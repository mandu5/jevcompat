"""A reference server for SPEC.md, with a deterministic fake model and injectable faults.

Clean, it passes every check: that is how the suite knows its checks accept correct behaviour.
With a fault, it breaks one requirement on purpose: that is how the suite knows each check can
fail. Application developers can also run it as an offline stand-in for Jev in CI.

The fake model hashes (state, instructions, option) into logits. It never sees the question id,
the other questions or their order, which is what the spec promises about the real one.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import math
import random
import threading
import unicodedata
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .validate import choice_confidence, score_confidence

MODELS = [{"name": "jev-latest", "description": "jevcompat reference mock (not a real model)", "release_date": "2026-09-24"},
          {"name": "mock", "description": "the same mock under its own name", "release_date": "2026-09-24"}]
ACCEPTED_MODELS = {"jev-latest", "jev-preview", "jev-1.13.0", "mock"}
TEXT = (str, dict, list)

# fault -> (requirement it breaks, what it does)
FAULTS: dict[str, tuple[str, str]] = {
    "wrong-route": ("http.endpoint", "serve /v1/evaluate instead of /v1/systemone"),
    "xssi-200": ("http.json", "prefix 200 bodies with )]}' so they are not JSON"),
    "plain-content-type": ("http.content-type", "declare Content-Type text/plain on JSON bodies"),
    "text-errors": ("errors.json", "error bodies are plain text"),
    "models-404": ("http.models", "no GET /v1/models"),
    "auth-rejects-header": ("auth.ignored-when-off", "with auth off, reject requests that carry Authorization"),
    "auth-x-api-key": ("auth.bearer", "read the key from x-api-key, not Authorization"),
    "auth-plain": ("auth.missing", "a missing key gets a plain-text 401"),
    "auth-invalid-403-text": ("auth.invalid", "a wrong key gets {'error': ...}"),
    "reject-array-state": ("request.state", "422 when state is an array"),
    "reject-jev-latest": ("request.model-alias", "404 for model jev-latest"),
    "first-question-only": ("request.multi", "answer only the first question"),
    "strict-ids": ("request.question-ids", "422 for ids outside [A-Za-z0-9_]"),
    "nfd-keys": ("request.unicode", "return option names NFD-normalised"),
    "forbid-extra": ("request.unknown-fields", "422 on unknown top-level fields"),
    "string-only-text": ("request.structured-text", "422 unless instructions and descriptions are strings"),
    "noul-two-sided": ("noul.criteria", "422 on one-sided noul criteria"),
    "noul-needs-instructions": ("noul.no-instructions", "422 on a noul without instructions"),
    "no-null-description": ("choice.null-description", "422 on a null option description"),
    "cap-64": ("choice.options", "422 above 64 options"),
    "cap-5-levels": ("score.levels", "422 above 5 score levels"),
    "accept-map-score": ("score.map-rejected", "accept map-form score criteria"),
    "no-usage": ("response.envelope", "omit usage"),
    "float-usage": ("response.usage", "token counts as floats"),
    "extra-answer": ("response.answer-ids", "add an answer nobody asked for"),
    "boolean-type": ("response.answer-type", "noul answers say type 'boolean'"),
    "nan": ("response.finite", "emit NaN in an x_ field"),
    "unprefixed-extra": ("response.extensions", "add a top-level latency_ms"),
    "noul-range": ("noul.answer", "noul above 1"),
    "choice-no-confidence": ("choice.answer", "omit confidence from choice answers"),
    "choice-key-case": ("choice.probability-keys", "lowercase option names in probabilities"),
    "choice-sum": ("choice.distribution", "choice probabilities sum to about 1.2"),
    "choice-second": ("choice.argmax", "choice is the second most likely option"),
    "score-no-legend": ("score.answer", "omit legend"),
    "legend-1-based": ("score.legend", "legend keys start at 1"),
    "score-keys-1-based": ("score.probability-keys", "score probability keys start at 1"),
    "score-sum": ("score.distribution", "score probabilities sum to 0.8"),
    "score-argmax": ("score.expectation", "score is the most likely level, not the expectation"),
    "confidence-over": ("confidence.range", "confidence above 1"),
    "confidence-margin": ("confidence.formula", "confidence is the top-1 minus top-2 margin"),
    "500-on-unknown-type": ("errors.no-5xx", "500 on an unknown question type"),
    "accept-boolean": ("errors.reject-invalid", "answer type 'boolean' as if it were noul"),
    "validation-400": ("errors.validation-shape", "validation failures are 400 {'error': ...}"),
    "error-flat": ("errors.shape", "unknown model gets {'error': ...}"),
    "id-leaks": ("semantics.question-id", "the question id feeds the model"),
    "batch-leaks": ("semantics.batching", "the number of questions feeds the model"),
    "order-leaks": ("semantics.question-order", "a question's position feeds the model"),
}


@dataclass
class MockConfig:
    key: str | None = None
    faults: frozenset[str] = frozenset()
    noise: float = 0.0
    sampled: bool = False     # score answers are one sampled level (one-hot), like a sampling server
    busy_every: int = 0       # every Nth request gets 429 with Retry-After: 0
    rng: random.Random = field(default_factory=lambda: random.Random(0))
    lock: threading.Lock = field(default_factory=threading.Lock)
    requests: int = 0

    def __post_init__(self) -> None:
        unknown = set(self.faults) - set(FAULTS)
        if unknown:
            raise ValueError(f"unknown fault(s): {', '.join(sorted(unknown))}")

    def has(self, fault: str) -> bool:
        return fault in self.faults


# ---------------------------------------------------------------- request validation (FastAPI-shaped)

def _err(loc: list, msg: str, typ: str) -> dict:
    return {"loc": ["body", *loc], "msg": msg, "type": typ}


def _is_text(v: Any, nullable: bool) -> bool:
    return isinstance(v, TEXT) or (nullable and v is None)


def validate_request(body: Any, cfg: MockConfig) -> list[dict]:
    if not isinstance(body, dict):
        return [_err([], "Input should be a valid dictionary", "dict_type")]
    errs = [_err([k], "Field required", "missing") for k in ("state", "model", "questions") if k not in body]
    if "state" in body and not isinstance(body["state"], TEXT):
        errs.append(_err(["state"], "Input should be a valid string, object or array", "union_type"))
    if cfg.has("reject-array-state") and isinstance(body.get("state"), list):
        errs.append(_err(["state"], "Input should be a valid string", "string_type"))
    if "model" in body and not isinstance(body["model"], str):
        errs.append(_err(["model"], "Input should be a valid string", "string_type"))
    if cfg.has("forbid-extra"):
        errs += [_err([k], "Extra inputs are not permitted", "extra_forbidden") for k in body if k not in ("state", "model", "questions")]
    qs = body.get("questions")
    if "questions" in body:
        if not isinstance(qs, dict):
            errs.append(_err(["questions"], "Input should be a valid dictionary", "dict_type"))
        elif not qs:
            errs.append(_err(["questions"], "Dictionary should have at least 1 item after validation, not 0", "too_short"))
        else:
            for qid, q in qs.items():
                errs += _validate_question(qid, q, cfg)
    return errs


def _validate_question(qid: str, q: Any, cfg: MockConfig) -> list[dict]:
    loc = ["questions", qid]
    if cfg.has("strict-ids") and not all(c.isascii() and (c.isalnum() or c == "_") for c in qid):
        return [_err(loc, "Question id must match [A-Za-z0-9_]+", "string_pattern_mismatch")]
    if not isinstance(q, dict):
        return [_err(loc, "Input should be a valid dictionary", "model_attributes_type")]
    qtype = q.get("type")
    if cfg.has("accept-boolean") and qtype == "boolean":
        qtype = "noul"
    if "type" not in q:
        return [_err(loc, "Unable to extract tag using discriminator 'type'", "union_tag_not_found")]
    if qtype not in ("noul", "choice", "score"):
        return [_err(loc, f"Input tag '{qtype}' found using 'type' does not match any of the expected tags: 'noul', 'choice', 'score'", "union_tag_invalid")]
    loc = [*loc, qtype]
    errs = []
    strict_text = cfg.has("string-only-text")
    ins = q.get("instructions")
    if not _is_text(ins, nullable=True) or (strict_text and ins is not None and not isinstance(ins, str)):
        errs.append(_err([*loc, "instructions"], "Input should be a valid string", "string_type"))
    crit = q.get("criteria")
    if qtype == "noul":
        if cfg.has("noul-needs-instructions") and ins is None:
            errs.append(_err([*loc, "instructions"], "Field required", "missing"))
        if crit is not None:
            if not isinstance(crit, dict) or set(crit) - {"true", "false"}:
                errs.append(_err([*loc, "criteria"], "Input should be an object with 'true' and/or 'false'", "model_type"))
            elif cfg.has("noul-two-sided") and set(crit) != {"true", "false"}:
                errs.append(_err([*loc, "criteria"], "Both 'true' and 'false' are required", "missing"))
    elif qtype == "choice":
        if not isinstance(crit, dict):
            errs.append(_err([*loc, "criteria"], "Input should be a valid dictionary", "dict_type" if crit is not None else "missing"))
        else:
            cap = 64 if cfg.has("cap-64") else 255
            if not crit:
                errs.append(_err([*loc, "criteria"], "Dictionary should have at least 1 item after validation, not 0", "too_short"))
            elif len(crit) > cap:
                errs.append(_err([*loc, "criteria"], f"Dictionary should have at most {cap} items after validation, not {len(crit)}", "too_long"))
            for name, desc in crit.items():
                bad = not _is_text(desc, nullable=True) or (strict_text and desc is not None and not isinstance(desc, str))
                if bad or (cfg.has("no-null-description") and desc is None):
                    errs.append(_err([*loc, "criteria", name], "Input should be a valid string", "string_type"))
    else:
        if isinstance(crit, dict) and cfg.has("accept-map-score"):
            crit = [crit[k] for k in sorted(crit, key=str)]
            q["criteria"] = crit
        if not isinstance(crit, list):
            errs.append(_err([*loc, "criteria"], "Input should be a valid list", "list_type" if crit is not None else "missing"))
        else:
            cap = 5 if cfg.has("cap-5-levels") else 10
            if not crit:
                errs.append(_err([*loc, "criteria"], "List should have at least 1 item after validation, not 0", "too_short"))
            elif len(crit) > cap:
                errs.append(_err([*loc, "criteria"], f"List should have at most {cap} items after validation, not {len(crit)}", "too_long"))
            for i, level in enumerate(crit):
                if not _is_text(level, nullable=False) or (strict_text and not isinstance(level, str)):
                    errs.append(_err([*loc, "criteria", i], "Input should be a valid string", "string_type"))
    return errs


# ---------------------------------------------------------------- fake model

def _canon(v: Any) -> str:
    return json.dumps(v, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _logit(cfg: MockConfig, *parts: Any) -> float:
    h = hashlib.sha256(_canon(parts).encode("utf-8")).digest()
    x = (int.from_bytes(h[:8], "big") / 2**64 * 2 - 1) * 3
    if cfg.noise:
        with cfg.lock:
            x += cfg.rng.gauss(0, cfg.noise)
    return x


def _softmax(xs: list[float]) -> list[float]:
    m = max(xs)
    es = [math.exp(x - m) for x in xs]
    s = sum(es)
    return [e / s for e in es]


def answer(cfg: MockConfig, state: Any, qid: str, q: dict, position: int, count: int) -> dict:
    salt: list[Any] = []
    if cfg.has("id-leaks"):
        salt.append(qid)
    if cfg.has("batch-leaks"):
        salt.append(count)
    if cfg.has("order-leaks"):
        salt.append(position)
    qtype = "noul" if q["type"] == "boolean" else q["type"]
    ins = q.get("instructions")
    if qtype == "noul":
        p = 1 / (1 + math.exp(-_logit(cfg, state, ins, q.get("criteria"), *salt)))
        if cfg.has("noul-range"):
            p += 1
        return {"type": "boolean" if cfg.has("boolean-type") else "noul", "noul": p}
    if qtype == "choice":
        names = list(q["criteria"])
        probs = _softmax([_logit(cfg, state, ins, n, q["criteria"][n], *salt) for n in names])
        order = sorted(range(len(names)), key=lambda i: -probs[i])
        conf = choice_confidence(probs)
        if cfg.has("choice-sum"):  # like independent per-option sigmoids: each in [0, 1], sum ≠ 1
            probs = [min(1.0, p + 0.2 / len(probs)) for p in probs]
        keys = names
        if cfg.has("nfd-keys"):
            keys = [unicodedata.normalize("NFD", n) for n in names]
        if cfg.has("choice-key-case"):
            keys = [n.lower() for n in keys]
        pick = order[1] if cfg.has("choice-second") and len(order) > 1 else order[0]
        out = {"type": "choice", "choice": keys[pick], "probabilities": dict(zip(keys, probs, strict=True)), "confidence": conf}
        if cfg.has("confidence-margin") and len(order) > 1:
            out["confidence"] = probs[order[0]] - probs[order[1]]
        if cfg.has("confidence-over"):
            out["confidence"] = 1.5
        if cfg.has("choice-no-confidence"):
            del out["confidence"]
        return out
    levels = q["criteria"]
    probs = _softmax([_logit(cfg, state, ins, i, lv, *salt) for i, lv in enumerate(levels)])
    if cfg.sampled:
        with cfg.lock:
            pick = cfg.rng.choices(range(len(probs)), weights=probs)[0]
        probs = [1.0 if i == pick else 0.0 for i in range(len(probs))]
    score = sum(i * p for i, p in enumerate(probs))
    if cfg.has("score-argmax"):
        score = float(max(range(len(probs)), key=lambda i: probs[i]))
    conf = score_confidence(probs)
    if cfg.has("score-sum"):
        probs = [p * 0.8 for p in probs]
    base = 1 if cfg.has("legend-1-based") else 0
    pbase = 1 if cfg.has("score-keys-1-based") else 0
    out = {"type": "score", "score": score,
           "legend": {str(i + base): lv for i, lv in enumerate(levels)},
           "probabilities": {str(i + pbase): p for i, p in enumerate(probs)},
           "confidence": 1.5 if cfg.has("confidence-over") else conf}
    if cfg.has("score-no-legend"):
        del out["legend"]
    return out


def respond(cfg: MockConfig, body: dict) -> dict:
    qs = body["questions"]
    items = list(qs.items())
    if cfg.has("first-question-only"):
        items = items[:1]
    answers = {qid: answer(cfg, body["state"], qid, q, i, len(qs)) for i, (qid, q) in enumerate(items)}
    if cfg.has("extra-answer"):
        answers["__extra__"] = {"type": "noul", "noul": 0.5}
    tokens_in = len(_canon(body["state"])) // 4 + sum(len(_canon(q)) // 4 for q in qs.values())
    usage: dict[str, Any] = {"input_tokens": tokens_in, "output_tokens": 2 * len(answers)}
    if cfg.has("float-usage"):
        usage = {k: float(v) for k, v in usage.items()}
    out: dict[str, Any] = {"model": "jevcompat-mock-0.1", "answers": answers, "usage": usage}
    if cfg.has("no-usage"):
        del out["usage"]
    if cfg.has("nan"):
        out["x_debug"] = float("nan")
    if cfg.has("unprefixed-extra"):
        out["latency_ms"] = 1
    return out


# ---------------------------------------------------------------- HTTP

class Handler(BaseHTTPRequestHandler):
    server_version = "jevcompat-mock"
    cfg: MockConfig

    def log_message(self, fmt: str, *args: Any) -> None:  # quiet by default
        if getattr(self.server, "verbose", False):
            super().log_message(fmt, *args)

    def _send(self, status: int, payload: Any, text: bool = False) -> None:
        if text or (status >= 400 and self.cfg.has("text-errors")):
            message = payload if isinstance(payload, str) else _plain(payload)
            raw = message.encode()
            ctype = "text/plain; charset=utf-8"
        else:
            raw = json.dumps(payload, ensure_ascii=False, allow_nan=True).encode("utf-8")
            ctype = "text/plain" if self.cfg.has("plain-content-type") else "application/json"
            if status == 200 and self.cfg.has("xssi-200"):
                raw = b")]}'\n" + raw
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("x-typesafe-request-id", "req_mock")
        self.end_headers()
        self.wfile.write(raw)

    def _auth_error(self) -> bool:
        cfg = self.cfg
        header = self.headers.get("Authorization")
        if cfg.key is None:
            if cfg.has("auth-rejects-header") and header:
                self._send(401, {"detail": {"error_type": "authentication_error", "message": "This server takes no key."}})
                return True
            return False
        given = self.headers.get("x-api-key") if cfg.has("auth-x-api-key") else (
            header[7:] if header and header.startswith("Bearer ") else None)
        if not given:
            if cfg.has("auth-plain"):
                self._send(401, "Unauthorized", text=True)
            else:
                self._send(403, {"detail": {"error_type": "authentication_error", "message": "Must supply an API key!"}})
            return True
        if not hmac.compare_digest(given.encode(), cfg.key.encode()):
            if cfg.has("auth-invalid-403-text"):
                self._send(401, {"error": "bad key"})
            else:
                self._send(401, {"detail": {"error_type": "authentication_error", "message": "Cannot authenticate with the server."}})
            return True
        return False

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/v1/models" and not self.cfg.has("models-404"):
            if not self._auth_error():
                self._send(200, {"models": MODELS})
            return
        self._send(404, {"detail": {"error_type": "not_found", "message": f"No route {self.path}"}})

    def do_POST(self) -> None:  # noqa: N802
        route = "/v1/evaluate" if self.cfg.has("wrong-route") else "/v1/systemone"
        if self.path != route:
            self._send(404, {"detail": {"error_type": "not_found", "message": f"No route {self.path}"}})
            return
        if self._auth_error():
            return
        with self.cfg.lock:
            self.cfg.requests += 1
            busy = self.cfg.busy_every and self.cfg.requests % self.cfg.busy_every == 0
        if busy:
            self.rfile.read(int(self.headers.get("Content-Length") or 0))
            self.send_response(429)
            raw = b'{"detail": {"error_type": "rate_limit_error", "message": "slow down"}}'
            self.send_header("Content-Type", "application/json")
            self.send_header("Retry-After", "0")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
            return
        raw = read_body(self)
        try:
            body = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            self._validation([_err([getattr(e, "pos", 0)], "JSON decode error", "json_invalid")])
            return
        if self.cfg.has("500-on-unknown-type") and isinstance(body, dict) and isinstance(body.get("questions"), dict):
            if any(isinstance(q, dict) and q.get("type") not in ("noul", "choice", "score") for q in body["questions"].values()):
                self._send(500, {"detail": {"error_type": "internal_error", "message": "KeyError: 'type'"}})
                return
        errs = validate_request(body, self.cfg)
        if errs:
            self._validation(errs)
            return
        model = body["model"]
        if model not in ACCEPTED_MODELS or (model == "jev-latest" and self.cfg.has("reject-jev-latest")):
            if self.cfg.has("error-flat"):
                self._send(400, {"error": f"Unknown model: {model}"})
            elif model == "jev-latest":
                self._send(404, {"detail": {"error_type": "not_found", "message": "Model not served: jev-latest"}})
            else:
                self._send(400, {"detail": {"error_type": "api_usage_error", "message": f"Unknown model: {model}"}})
            return
        self._send(200, respond(self.cfg, body))

    def _validation(self, errs: list[dict]) -> None:
        if self.cfg.has("validation-400"):
            self._send(400, {"error": errs[0]["msg"]})
        else:
            self._send(422, {"detail": errs})


def _plain(payload: Any) -> str:
    detail = payload.get("detail") if isinstance(payload, dict) else None
    if isinstance(detail, dict):
        return str(detail.get("message", detail))
    if isinstance(detail, list) and detail:
        return "; ".join(str(d.get("msg")) for d in detail if isinstance(d, dict))
    return str(payload)


def read_body(handler: BaseHTTPRequestHandler, limit: int = 32 * 1024 * 1024) -> bytes:
    """The request body, with Content-Length or chunked transfer encoding."""
    if "chunked" in (handler.headers.get("Transfer-Encoding") or "").lower():
        parts, total = [], 0
        while True:
            size = int(handler.rfile.readline().split(b";")[0].strip() or b"0", 16)
            if size == 0:
                handler.rfile.readline()
                break
            total += size
            if total > limit:
                raise ValueError("request body too large")
            parts.append(handler.rfile.read(size))
            handler.rfile.readline()
        return b"".join(parts)
    return handler.rfile.read(min(int(handler.headers.get("Content-Length") or 0), limit))


def make_server(cfg: MockConfig, host: str = "127.0.0.1", port: int = 0, verbose: bool = False) -> ThreadingHTTPServer:
    handler = type("BoundHandler", (Handler,), {"cfg": cfg})
    srv = ThreadingHTTPServer((host, port), handler)
    srv.daemon_threads = True
    srv.verbose = verbose  # type: ignore[attr-defined]
    return srv


class Running:
    """Context manager: a mock server on a free port in a background thread."""

    def __init__(self, cfg: MockConfig | None = None):
        self.server = make_server(cfg or MockConfig())
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
