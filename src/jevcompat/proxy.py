"""A normalising proxy: put it in front of a non-conforming server and clients see SPEC.md.

What it fixes is whatever can be recomputed or re-labelled without inventing an answer:
derived fields (`choice`, `score`, `legend`, `confidence`), probability keys that differ only by
Unicode normalisation, case or a 1-based index (when the match is unambiguous), distributions
that sum to within 0.1 of 1, integer token counts, unprefixed extra fields, error shapes, the
model alias, and answers that depend on the question id: the upstream only ever sees ids derived
from each question's content. Questions also go upstream in a content-derived order, so
reordering a request changes nothing; adding questions can still shift positions, which only
`split` (one upstream request per question) rules out, together with any other cross-question
effect.

What it cannot fix it refuses loudly (502 with `error_type: upstream_error`) rather than
passing a wrong answer through: a missing or ambiguous option, probability mass on options that
were not asked, a probability outside [0, 1], a NaN. Every response says what was changed in
the `x-jevcompat-fixes` header.
"""
from __future__ import annotations

import hashlib
import json
import math
import threading
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .client import Client, TransportError
from .mock import MockConfig, read_body, validate_request
from .validate import choice_confidence, is_num, score_confidence

TEXT_FIELDS = ("state", "model", "questions")


class UpstreamError(Exception):
    """The upstream answered something that cannot be turned into a correct answer."""

    def __init__(self, message: str, error_type: str = "upstream_error"):
        super().__init__(message)
        self.error_type = error_type


class UpstreamRejected(Exception):
    """The upstream refused the request with a 4xx: the client's problem, passed on in spec shape."""

    def __init__(self, status: int, data: Any, text: str):
        super().__init__(text)
        self.status, self.data, self.text = status, data, text

    def with_ids(self, upstream_to_client: dict[str, str]) -> UpstreamRejected:
        """Replace the proxy's question ids with the client's in validation-error locations."""
        detail = self.data.get("detail") if isinstance(self.data, dict) else None
        if isinstance(detail, list):
            for d in detail:
                if isinstance(d, dict) and isinstance(d.get("loc"), list):
                    d["loc"] = [upstream_to_client.get(x, x) if isinstance(x, str) else x for x in d["loc"]]
        return self


class RateLimited(Exception):
    def __init__(self, status: int, retry_after: str | None):
        super().__init__(status)
        self.status, self.retry_after = status, retry_after


@dataclass
class ProxyConfig:
    upstream: str
    upstream_key: str | None = None
    upstream_model: str | None = None     # send this model name upstream instead of the client's
    upstream_path: str = "/v1/systemone"
    upstream_key_header: str | None = None  # e.g. "x-api-key"; default Authorization: Bearer
    key: str | None = None                 # require this key from clients
    split: bool = False                    # one upstream request per question
    renormalize: bool = False              # renormalise any positive sum, not only sums within 0.1 of 1
    timeout: float = 120.0


def _canon(v: Any) -> str:
    return json.dumps(v, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def canonical_ids(questions: dict[str, Any]) -> list[tuple[str, str]]:
    """(client id, upstream id), both the ids and their order derived from each question's content,
    so neither depends on the client's ids, their order, or the other questions."""
    digests = {q: hashlib.sha256(_canon(questions[q]).encode()).hexdigest() for q in questions}
    seen: dict[str, int] = {}
    out = []
    for qid in sorted(questions, key=lambda q: (digests[q], q)):
        base = "q" + digests[qid][:12]
        n = seen.get(base, 0)
        seen[base] = n + 1
        out.append((qid, base if n == 0 else f"{base}_{n}"))
    return out


# ---------------------------------------------------------------- answer normalisation

def _prefix_extras(obj: dict, known: set[str], fixes: set[str]) -> dict:
    out = {}
    for k, v in obj.items():
        if k in known:
            continue
        if isinstance(v, float) and not math.isfinite(v):
            fixes.add("dropped-nonfinite")
            continue
        name = k if str(k).startswith("x_") else f"x_{k}"
        if name != k:
            fixes.add("prefixed-extras")
        out[name] = v
    return out


def _norm(s: str) -> str:
    return unicodedata.normalize("NFC", s).casefold().strip()


def _match_keys(wanted: list[str], got: dict[str, Any], fixes: set[str]) -> dict[str, float]:
    """Map the request's option names onto the upstream's probability keys, one to one.

    Exact matches first; then each still-unmatched name may claim an unclaimed key equal to it
    under NFC, case folding and trimming — only when exactly one unclaimed key and no other
    unmatched name normalise the same way."""
    claimed: dict[str, str] = {w: w for w in wanted if w in got}
    free = [k for k in got if k not in claimed.values()]
    for w in wanted:
        if w in claimed:
            continue
        rivals = [x for x in wanted if x not in claimed and _norm(x) == _norm(w)]
        candidates = [k for k in free if _norm(str(k)) == _norm(w)]
        if len(rivals) != 1 or len(candidates) != 1:
            raise UpstreamError(f"upstream gave no unambiguous probability for option {w!r}")
        claimed[w] = candidates[0]
        free.remove(candidates[0])
        fixes.add("option-names")
    leftover = sum(v for k, v in got.items() if k in free and is_num(v))
    if leftover > 0.01:
        raise UpstreamError(f"upstream put {leftover:.3f} probability on options that were not asked: "
                            f"{', '.join(map(repr, free[:3]))}")
    out = {}
    for w in wanted:
        v = got[claimed[w]]
        if not (is_num(v) and -1e-9 <= v <= 1 + 1e-9):
            raise UpstreamError(f"upstream probability for {w!r} is {v!r}")
        out[w] = min(1.0, max(0.0, float(v)))
    return out


def _renormalise(values: list[float], fixes: set[str], any_sum: bool) -> list[float]:
    total = sum(values)
    if total <= 0:
        raise UpstreamError("upstream probabilities sum to 0")
    if abs(total - 1) > 0.1 and not any_sum:
        raise UpstreamError(f"upstream probabilities sum to {total:.3f}; pass --renormalize to accept that")
    if abs(total - 1) > 1e-6:
        fixes.add("renormalised")
    return [v / total for v in values]


def normalise_answer(question: dict, ans: Any, fixes: set[str], any_sum: bool = False) -> dict:
    if not isinstance(ans, dict):
        raise UpstreamError(f"upstream answer is {type(ans).__name__}")
    qtype = question["type"]
    if ans.get("type") != qtype:
        fixes.add("answer-type")
    if qtype == "noul":
        p = ans.get("noul")
        if not (is_num(p) and -1e-9 <= p <= 1 + 1e-9):
            raise UpstreamError(f"upstream noul is {p!r}")
        return {"type": "noul", "noul": min(1.0, max(0.0, float(p))),
                **_prefix_extras(ans, {"type", "noul"}, fixes)}
    probs = ans.get("probabilities")
    if isinstance(probs, list):
        probs = {str(i): v for i, v in enumerate(probs)}
        fixes.add("probability-keys")
    if not isinstance(probs, dict):
        raise UpstreamError("upstream answer has no probabilities")
    known = {"type", "choice", "probabilities", "confidence", "score", "legend"}
    extras = _prefix_extras(ans, known, fixes)
    if qtype == "choice":
        names = list(question["criteria"])
        values = _renormalise(list(_match_keys(names, probs, fixes).values()), fixes, any_sum)
        best = max(range(len(names)), key=lambda i: values[i])
        conf = choice_confidence(values)
        _note(fixes, "choice", ans.get("choice") != names[best])
        _note(fixes, "confidence", not (is_num(ans.get("confidence")) and abs(ans["confidence"] - conf) <= 1e-3))
        return {"type": "choice", "choice": names[best], "probabilities": dict(zip(names, values, strict=True)),
                "confidence": conf, **extras}
    levels = question["criteria"]
    n = len(levels)
    keys = [str(i) for i in range(n)]
    got = {str(k): v for k, v in probs.items()}
    if set(got) == {str(i) for i in range(1, n + 1)}:
        got = {str(int(k) - 1): v for k, v in got.items()}
        fixes.add("probability-keys")
    values = _renormalise(list(_match_keys(keys, got, fixes).values()), fixes, any_sum)
    score = sum(i * p for i, p in enumerate(values))
    conf = score_confidence(values)
    legend = {str(i): lv for i, lv in enumerate(levels)}
    _note(fixes, "score", not (is_num(ans.get("score")) and abs(ans["score"] - score) <= 1e-3))
    _note(fixes, "legend", ans.get("legend") != legend)
    _note(fixes, "confidence", not (is_num(ans.get("confidence")) and abs(ans["confidence"] - conf) <= 1e-3))
    return {"type": "score", "score": score, "legend": legend, "probabilities": dict(zip(keys, values, strict=True)),
            "confidence": conf, **extras}


def _note(fixes: set[str], name: str, changed: bool) -> None:
    if changed:
        fixes.add(name)


def _usage(u: Any, fixes: set[str]) -> dict[str, int]:
    out = {}
    for k in ("input_tokens", "output_tokens"):
        v = u.get(k) if isinstance(u, dict) else None
        if isinstance(v, int) and not isinstance(v, bool) and v >= 0:
            out[k] = v
        else:
            out[k] = int(round(v)) if is_num(v) and v >= 0 else 0
            fixes.add("usage")
    return out


# ---------------------------------------------------------------- the proxy

class Proxy:
    def __init__(self, cfg: ProxyConfig):
        self.cfg = cfg
        self.client = Client(cfg.upstream, key=cfg.upstream_key, timeout=cfg.timeout)
        self.pool = ThreadPoolExecutor(max_workers=16)

    def _upstream(self, payload: dict) -> dict:
        headers = {}
        auth: Any = bool(self.cfg.upstream_key)  # no key: send no Authorization header at all
        if self.cfg.upstream_key_header and self.cfg.upstream_key:
            headers[self.cfg.upstream_key_header] = self.cfg.upstream_key
            auth = False
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        try:
            r = self.client.request("POST", self.cfg.upstream_path, body, auth=auth, headers=headers)
        except TransportError as e:
            raise UpstreamError(f"upstream unreachable: {e}") from None
        if r.status == 429 or r.status == 529:
            raise RateLimited(r.status, r.headers.get("retry-after"))
        if 400 <= r.status < 500 and r.status not in (401, 403):
            raise UpstreamRejected(r.status, r.data, r.excerpt(300))
        if r.status in (401, 403):
            raise UpstreamError(f"upstream refused the proxy's credentials ({r.status}); check --upstream-key",
                                "upstream_auth_error")
        if r.status != 200:
            raise UpstreamError(f"upstream answered {r.status}: {r.excerpt(300)}")
        if not r.is_json or not isinstance(r.data, dict) or not isinstance(r.data.get("answers"), dict):
            raise UpstreamError(f"upstream response is not a System One response: {r.excerpt(300)}")
        return r.data

    def answer(self, body: dict) -> tuple[dict, set[str]]:
        fixes: set[str] = set()
        questions = body["questions"]
        ids = canonical_ids(questions)
        model = self.cfg.upstream_model or body["model"]
        if model != body["model"]:
            fixes.add("model")
        if set(body) - set(TEXT_FIELDS):
            fixes.add("dropped-unknown-fields")
        if self.cfg.split:
            batches = [[pair] for pair in ids]
        else:
            batches = [ids]
        payloads = [{"model": model, "state": body["state"], "questions": {up: questions[cid] for cid, up in batch}}
                    for batch in batches]
        try:
            replies = list(self.pool.map(self._upstream, payloads)) if len(payloads) > 1 else [self._upstream(payloads[0])]
        except UpstreamRejected as e:
            raise e.with_ids({up: cid for cid, up in ids}) from None
        answers: dict[str, Any] = {}
        usage = {"input_tokens": 0, "output_tokens": 0}
        reported = None
        top_extras: dict[str, Any] = {}
        for batch, reply in zip(batches, replies, strict=True):
            got = reply["answers"]
            if set(got) - {up for _, up in batch}:
                fixes.add("dropped-extra-answers")
            for cid, up in batch:
                if up not in got:
                    raise UpstreamError(f"upstream returned no answer for question {cid!r}")
                answers[cid] = normalise_answer(questions[cid], got[up], fixes, self.cfg.renormalize)
            u = _usage(reply.get("usage"), fixes)
            usage = {k: usage[k] + u[k] for k in usage}
            reported = reported or reply.get("model")
            top_extras.update(_prefix_extras(reply, {"model", "answers", "usage"}, fixes))
        out = {"model": reported if isinstance(reported, str) else model, "answers": answers, "usage": usage, **top_extras}
        return out, fixes


class Handler(BaseHTTPRequestHandler):
    server_version = "jevcompat-proxy"
    proxy: Proxy

    def log_message(self, fmt: str, *args: Any) -> None:
        if getattr(self.server, "verbose", False):
            super().log_message(fmt, *args)

    def _send(self, status: int, payload: Any, headers: dict[str, str] | None = None) -> None:
        try:
            raw = json.dumps(payload, ensure_ascii=False, allow_nan=False).encode("utf-8")
        except ValueError:  # a NaN or Infinity somewhere in an upstream extra field
            status, headers = 502, None
            raw = json.dumps({"detail": {"error_type": "upstream_error",
                                         "message": "upstream response contains NaN or Infinity"}}).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(raw)

    def _error(self, status: int, error_type: str, message: str, headers: dict[str, str] | None = None) -> None:
        self._send(status, {"detail": {"error_type": error_type, "message": message}}, headers)

    def _authorised(self) -> bool:
        key = self.proxy.cfg.key
        if key is None:
            return True
        header = self.headers.get("Authorization") or ""
        if not header.startswith("Bearer ") or not header[7:]:
            self._error(403, "authentication_error", "Must supply an API key.")
            return False
        if header[7:] != key:
            self._error(401, "authentication_error", "Cannot authenticate with the server.")
            return False
        return True

    def do_GET(self) -> None:  # noqa: N802
        if self.path != "/v1/models":
            self._error(404, "not_found", f"No route {self.path}")
            return
        if not self._authorised():
            return
        name = "jev-latest"
        self._send(200, {"models": [{"name": name, "description": f"jevcompat proxy for {self.proxy.cfg.upstream}",
                                     "release_date": date.today().isoformat()}]})

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/v1/systemone":
            self._error(404, "not_found", f"No route {self.path}")
            return
        if not self._authorised():
            return
        raw = read_body(self)
        try:
            body = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            self._send(422, {"detail": [{"loc": ["body", getattr(e, "pos", 0)], "msg": "JSON decode error", "type": "json_invalid"}]})
            return
        errs = validate_request(body, MockConfig())
        if errs:
            self._send(422, {"detail": errs})
            return
        try:
            out, fixes = self.proxy.answer(body)
        except RateLimited as e:
            self._error(e.status, "rate_limit_error" if e.status == 429 else "overloaded_error", "upstream is busy",
                        {"retry-after": e.retry_after} if e.retry_after else None)
            return
        except UpstreamRejected as e:
            self._rejected(e)
            return
        except UpstreamError as e:
            self._error(502, e.error_type, str(e))
            return
        self._send(200, out, {"x-jevcompat-fixes": ",".join(sorted(fixes)) or "none"})


    def _rejected(self, e: UpstreamRejected) -> None:
        detail = e.data.get("detail") if isinstance(e.data, dict) else None
        if e.status == 422:
            ok = isinstance(detail, list) and detail and all(
                isinstance(d, dict) and isinstance(d.get("loc"), list) and d["loc"][:1] == ["body"]
                and isinstance(d.get("msg"), str) and isinstance(d.get("type"), str) for d in detail)
            self._send(422, {"detail": detail if ok else [{"loc": ["body"], "msg": e.text, "type": "upstream_validation"}]})
        elif isinstance(detail, dict) and isinstance(detail.get("error_type"), str) and isinstance(detail.get("message"), str):
            self._send(e.status, {"detail": detail})
        else:
            message = next((e.data[k] for k in ("message", "error", "detail") if isinstance(e.data, dict) and isinstance(e.data.get(k), str)), e.text)
            self._error(e.status, "api_usage_error" if e.status == 400 else "invalid_request_error", message)


def make_server(cfg: ProxyConfig, host: str = "127.0.0.1", port: int = 0, verbose: bool = False) -> ThreadingHTTPServer:
    handler = type("BoundProxyHandler", (Handler,), {"proxy": Proxy(cfg)})
    srv = ThreadingHTTPServer((host, port), handler)
    srv.daemon_threads = True
    srv.verbose = verbose  # type: ignore[attr-defined]
    return srv


class Running:
    def __init__(self, cfg: ProxyConfig):
        self.server = make_server(cfg)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    @property
    def url(self) -> str:
        host, port = self.server.server_address[:2]
        return f"http://{host}:{port}"

    def __enter__(self) -> Running:
        self.thread.start()
        return self

    def __exit__(self, *exc: Any) -> None:
        self.server.shutdown()
        self.server.server_close()
