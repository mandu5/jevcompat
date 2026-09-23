"""The conformance cases. Each one sends real requests and records which requirements it
exercised and which it found violated, with the exchange that shows it.

A requirement passes when at least one case exercised it and no case found a violation. A request
that timed out proves nothing either way: the requirements it would have tested are reported as
not tested, and the run as incomplete.
"""
from __future__ import annotations

import json
import math
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from importlib.metadata import PackageNotFoundError, version
from typing import Any

from . import spec
from .client import Busy, Client, Response, Timeout, TransportError
from .validate import (
    Violation,
    answer_vector,
    check_json,
    validate_error_shape,
    validate_success,
    validate_validation_error,
)

TICKET = ("Hi, I was charged twice for my March invoice (order #4471) and the refund I was promised "
          "last week still hasn't arrived. I've emailed three times. Please fix this today or I will "
          "dispute the charge with my bank.")
NOUL = {"type": "noul", "instructions": "Is the customer asking for money back?"}
CHOICE = {"type": "choice", "instructions": "Which team should handle this ticket?",
          "criteria": {"Billing": "Payments, invoices, refunds", "Technical": "Bugs, outages, integrations",
                       "Sales": "Pricing questions, upgrades, new contracts"}}
SCORE = {"type": "score", "instructions": "How frustrated is the customer?",
         "criteria": ["Calm", "Frustrated", "Very angry"]}

RESPONSE_REQS = ("http.endpoint", "http.json", "http.content-type", "response.envelope", "response.usage",
                 "response.answer-ids", "response.answer-type", "response.finite", "response.extensions")
TYPE_REQS = {
    "noul": ("noul.answer",),
    "choice": ("choice.answer", "choice.probability-keys", "choice.distribution", "choice.argmax",
               "confidence.range", "confidence.formula"),
    "score": ("score.answer", "score.legend", "score.probability-keys", "score.distribution", "score.expectation",
              "confidence.range", "confidence.formula"),
}
ERROR_JSON_REQS = ("http.content-type", "errors.json")


class Abort(Exception):
    """Nothing further can be tested (no endpoint, a key is needed, the server is not ready)."""


@dataclass
class Exchange:
    case: str
    method: str
    path: str
    request: Any
    status: int | None
    response: str
    ms: float | None
    via: str = "http"  # "http", or "typesafe-sdk" when the official SDK made the call


@dataclass
class Finding:
    req: str
    message: str
    where: str
    case: str
    exchange: int | None  # index into Ctx.exchanges
    tag: str = ""


@dataclass
class Ctx:
    client: Client
    key_given: bool
    sdk: bool = True
    exchanges: list[Exchange] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)
    exercised: dict[str, set[str]] = field(default_factory=dict)
    skipped: dict[str, str] = field(default_factory=dict)
    inconclusive: list[str] = field(default_factory=list)  # cases that timed out or could not finish
    info: dict[str, Any] = field(default_factory=dict)
    auth_mode: str = "bearer"  # "bearer" | "none" | "x-api-key"
    cache: dict[str, Any] = field(default_factory=dict)

    # -- plumbing
    def _record(self, case: str, method: str, path: str, request: Any, resp: Response | None, err: str = "",
                via: str = "http", status: int | None = None) -> int:
        self.exchanges.append(Exchange(case, method, path, request,
                                       resp.status if resp else status,
                                       resp.excerpt(4000) if resp else err,
                                       round(resp.ms, 1) if resp else None, via))
        return len(self.exchanges) - 1

    def _auth(self, auth: Any) -> tuple[Any, dict[str, str]]:
        if isinstance(auth, str) and self.auth_mode == "x-api-key":
            return False, {"x-api-key": auth}
        if auth is not True:
            return auth, {}
        if self.auth_mode == "none":
            return False, {}
        if self.auth_mode == "x-api-key":
            return False, {"x-api-key": self.client.key or ""}
        return True, {}

    def post(self, case: str, payload: Any, *, auth: Any = True, path: str = "/v1/systemone") -> tuple[Response, int]:
        shown = payload.decode("utf-8", "replace") if isinstance(payload, bytes) else payload
        body = payload if isinstance(payload, bytes) else json.dumps(payload, ensure_ascii=False).encode("utf-8")
        return self._call(case, "POST", path, body, shown, auth)

    def get(self, case: str, path: str) -> tuple[Response, int]:
        return self._call(case, "GET", path, None, None, True)

    def _call(self, case: str, method: str, path: str, body: bytes | None, shown: Any, auth: Any) -> tuple[Response, int]:
        """One request, retrying 429/503/529 as the official SDKs do. Still busy after that: raise
        Busy, which callers treat like a timeout — the server's load is not a conformance finding."""
        a, headers = self._auth(auth)
        waited = 0.0
        for attempt in range(spec.BUSY_ATTEMPTS):
            try:
                resp = self.client.request(method, path, body, auth=a, headers=headers)
            except TransportError as e:
                self._record(case, method, path, shown, None, str(e))
                raise
            if resp.status not in (429, 503, 529):
                return resp, self._record(case, method, path, shown, resp)
            delay = _retry_after(resp, attempt)
            if attempt == spec.BUSY_ATTEMPTS - 1 or waited + delay > spec.BUSY_BUDGET_S:
                break
            time.sleep(delay)
            waited += delay
        self._record(case, method, path, shown, resp)
        raise Busy(f"{method} {path}: still {resp.status} after {attempt + 1} attempts over {waited:.0f}s")

    def payload(self, questions: dict, state: Any = TICKET, **extra: Any) -> dict:
        return {"model": self.client.model, "state": state, "questions": questions, **extra}

    def exercise(self, case: str, *reqs: str) -> None:
        for r in reqs:
            self.exercised.setdefault(r, set()).add(case)

    def violate(self, case: str, xi: int | None, violations: list[Violation]) -> None:
        for v in violations:
            self.exercise(case, v.req)
            self.findings.append(Finding(v.req, v.message, v.where, case, xi, v.tag))

    def supports(self, case: str, types: tuple[str, ...], *reqs: str) -> bool:
        """Gate a case on question types the server answered on their own, so one unsupported
        type fails the requirement about that type, not every case that happens to use it."""
        missing = [t for t in types if t not in self.info.get("types_ok", set())]
        if missing:
            self.skip(f"needs {'/'.join(missing)} questions, which the server did not answer on their own", *reqs)
            return False
        return True

    def skip(self, reason: str, *reqs: str) -> None:
        for r in reqs:
            self.skipped.setdefault(r, reason)

    def timed_out(self, case: str, err: Timeout, reqs: tuple[str, ...]) -> None:
        self.inconclusive.append(f"{case}: {err}")
        self.skip(f"timed out ({err}); rerun with a longer --timeout", *reqs)

    def _send(self, case: str, payload: Any, reqs: tuple[str, ...]) -> tuple[Response, int] | None:
        """POST. A timeout is inconclusive; a request that gets no complete response at all is a
        finding against `reqs` (the server dropped the connection)."""
        try:
            return self.post(case, payload)
        except Timeout as e:
            self.timed_out(case, e, reqs)
        except TransportError as e:
            self.violate(case, len(self.exchanges) - 1, [Violation(r, f"no complete HTTP response: {e}") for r in reqs])
        return None

    # -- the three shapes of case
    def expect_answer(self, case: str, payload: dict, *accept_reqs: str,
                      remap: dict[tuple[str, str], str] | None = None,
                      transform: Callable[[list[Violation], Response], list[Violation]] | None = None) -> Response | None:
        """A valid request: must be answered with 200 and a response meeting §4.

        `remap` re-attributes violations by (requirement, tag): a case that exists to test one thing
        claims exactly the violations that show that thing failing, and nothing else."""
        got = self._send(case, payload, accept_reqs or ("http.endpoint",))
        if got is None:
            return None
        resp, xi = got
        self.exercise(case, *accept_reqs)
        if resp.status != 200:
            why = f"valid request got {resp.status}: {resp.excerpt(200)}"
            self.violate(case, xi, [Violation(r, why) for r in accept_reqs])
            return None
        types = {q.get("type") for q in payload["questions"].values() if isinstance(q, dict)}
        self.exercise(case, *RESPONSE_REQS, *(r for t in types if t in TYPE_REQS for r in TYPE_REQS[t]))
        violations = validate_success(payload, resp)
        if remap:
            violations = [Violation(remap.get((v.req, v.tag), v.req), v.message, v.where, v.tag) for v in violations]
        if transform:
            violations = transform(violations, resp)
        self.violate(case, xi, violations)
        return resp

    def expect_reject(self, case: str, payload: Any, *reqs: str) -> None:
        """An invalid request: must get a 4xx (SHOULD) and never a 5xx (MUST)."""
        got = self._send(case, payload, ("errors.no-5xx",))
        if got is None:
            return
        resp, xi = got
        self.exercise(case, "errors.no-5xx", "errors.reject-invalid", *reqs)
        if resp.status >= 500:
            self.violate(case, xi, [Violation("errors.no-5xx", f"invalid request got {resp.status}: {resp.excerpt(160)}")])
        elif resp.status < 400:
            why = f"invalid request was answered with {resp.status}"
            self.violate(case, xi, [Violation(r, why) for r in ("errors.reject-invalid", *reqs)])
        else:
            self.exercise(case, *ERROR_JSON_REQS, "errors.validation-shape")
            self.violate(case, xi, validate_validation_error(resp))

    def expect_answer_or_4xx(self, case: str, payload: dict) -> None:
        """Outside the documented ranges: answering and rejecting are both fine; 5xx is not."""
        got = self._send(case, payload, ("errors.no-5xx",))
        if got is None:
            return
        resp, xi = got
        self.exercise(case, "errors.no-5xx")
        if resp.status >= 500:
            self.violate(case, xi, [Violation("errors.no-5xx", f"got {resp.status}: {resp.excerpt(160)}")])
        elif resp.status == 200:
            types = {q.get("type") for q in payload["questions"].values() if isinstance(q, dict)}
            self.exercise(case, *RESPONSE_REQS, *(r for t in types if t in TYPE_REQS for r in TYPE_REQS[t]))
            self.violate(case, xi, validate_success(payload, resp))
        elif resp.status == 413:  # SPEC §3.5 allows 413 for an over-budget request
            self.exercise(case, *ERROR_JSON_REQS)
            self.violate(case, xi, check_json(resp, error=True))
        elif resp.status >= 400:
            self.exercise(case, *ERROR_JSON_REQS, "errors.validation-shape")
            self.violate(case, xi, validate_validation_error(resp))


def _retry_after(resp: Response, attempt: int) -> float:
    for header, scale in (("retry-after-ms", 0.001), ("retry-after", 1.0)):
        v = resp.headers.get(header)
        if v is None:
            continue
        try:
            return min(30.0, max(0.0, float(v) * scale))
        except ValueError:  # an HTTP-date; fall back to backoff
            continue
    return _backoff(attempt)


def _backoff(attempt: int) -> float:
    return min(8.0, 0.5 * 2**attempt)


@dataclass
class Case:
    name: str
    fn: Callable[[Ctx, str], None]
    doc: str


CASES: list[Case] = []


def case(name: str) -> Callable[[Callable[[Ctx, str], None]], Callable[[Ctx, str], None]]:
    def register(fn: Callable[[Ctx, str], None]) -> Callable[[Ctx, str], None]:
        CASES.append(Case(name, fn, (fn.__doc__ or "").strip()))
        return fn
    return register


# ---------------------------------------------------------------- preflight

def preflight(ctx: Ctx) -> None:
    """One plain noul question. Settles the route, auth and model before anything else, and blames
    a requirement only when a second request proves which one."""
    name = "preflight"
    payload = ctx.payload({"q": dict(NOUL)})
    resp, xi = ctx.post(name, payload)  # Busy (still 429/503/529 after retries) aborts the run

    if 300 <= resp.status < 400:
        raise Abort(f"the server redirects ({resp.status} → {resp.headers.get('location', '?')}); test that URL instead")

    if resp.status in (401, 403):
        bare, xb = ctx.post(name, payload, auth=False)
        if bare.status == 200:
            # No key needed, yet the header SDKs always send is refused.
            ctx.violate(name, xb, [Violation("auth.ignored-when-off",
                                             f"a request with `Authorization: Bearer …` got {resp.status}; "
                                             "the same request without the header got 200")])
            ctx.auth_mode = "none"
            resp, xi = bare, xb
        elif ctx.key_given:
            ctx.auth_mode = "x-api-key"
            alt, xk = ctx.post(name, payload)
            if alt.status != 200:
                ctx.auth_mode = "bearer"
                raise Abort(f"the server refused the key ({resp.status}: {resp.excerpt(120)}); check --key")
            ctx.violate(name, xk, [Violation("auth.bearer", "the key was refused as `Authorization: Bearer <key>` "
                                                           "but accepted as `x-api-key: <key>`")])
            resp, xi = alt, xk
        else:
            raise Abort(f"the server requires an API key ({resp.status}); pass --key")
    if ctx.auth_mode == "none" or not ctx.key_given:
        ctx.exercise(name, "auth.ignored-when-off")
    else:
        ctx.exercise(name, "auth.bearer")

    if resp.status >= 500:  # one transient failure (a backend still starting) is not evidence yet
        resp, xi = ctx.post(name, payload)
    if resp.status != 200 and ctx.client.model == "jev-latest":
        # Is it the model name? Retry with a model the server lists, then jev-latest once more:
        # blame the alias only if the listed model works and jev-latest still does not.
        other = _served_model(ctx)
        if other:
            retry, xr = ctx.post(name, {**payload, "model": other})
            if retry.status == 200:
                again, xa = ctx.post(name, payload)
                if again.status == 200:
                    resp, xi = again, xa
                else:
                    ctx.exercise(name, "request.model-alias")
                    ctx.violate(name, xa, [Violation("request.model-alias", f"model \"jev-latest\" got {again.status}: "
                                                     f"{again.excerpt(200)}; model {other!r} is accepted")])
                    ctx.info["model_fallback"] = other
                    ctx.client.model = other
                    resp, xi = retry, xr
    if resp.status != 200:
        if resp.status >= 500:
            raise Abort(f"the server fails a minimal valid request ({resp.status}: {resp.excerpt(200)})")
        if resp.status in (404, 405):
            # Does the route exist? A GET to an existing POST route is usually 405; a missing route
            # answers exactly like a route that certainly does not exist.
            as_get, _ = ctx.get(name, "/v1/systemone")
            probe, _ = ctx.post(name, payload, path="/v1/jevcompat-no-such-route")
            if as_get.status != 405 and probe.status == resp.status and _same_body(probe, resp):
                ctx.exercise(name, "http.endpoint")
                ctx.violate(name, xi, [Violation("http.endpoint", f"POST /v1/systemone answers exactly like a route "
                                                                  f"that does not exist ({resp.status})")])
                raise Abort(f"no POST /v1/systemone at {ctx.client.base_url} ({resp.status})")
        raise Abort(f"the server rejects a minimal valid request ({resp.status}: {resp.excerpt(200)}); "
                    "if it needs a particular model name, pass --model NAME")
    ctx.info["model_reported"] = resp.data.get("model") if isinstance(resp.data, dict) else None
    ctx.info["types_ok"] = {"noul"}
    try:
        ctx.info["typesafe_sdk"] = version("typesafe-sdk")
    except PackageNotFoundError:
        ctx.info["typesafe_sdk"] = None


def _same_body(a: Response, b: Response) -> bool:
    def norm(r: Response) -> bytes:
        return r.body.replace(b"/v1/jevcompat-no-such-route", b"/ROUTE").replace(b"/v1/systemone", b"/ROUTE")
    return norm(a) == norm(b)


def _served_model(ctx: Ctx) -> str | None:
    try:
        resp, _ = ctx.get("preflight", "/v1/models")
    except TransportError:
        return None
    models = resp.data.get("models") if resp.status == 200 and isinstance(resp.data, dict) else None
    if not isinstance(models, list):
        return None
    for m in models:
        if isinstance(m, dict) and isinstance(m.get("name"), str) and m["name"] not in ("", "jev-latest"):
            return m["name"]
    return None


# ---------------------------------------------------------------- transport

@case("models-endpoint")
def _(ctx: Ctx, name: str) -> None:
    """GET /v1/models lists at least one model with name, description and release_date."""
    try:
        resp, xi = ctx.get(name, "/v1/models")
    except Timeout as e:
        ctx.timed_out(name, e, ("http.models",))
        return
    except TransportError as e:
        ctx.violate(name, len(ctx.exchanges) - 1, [Violation("http.models", f"no complete HTTP response: {e}")])
        return
    ctx.exercise(name, "http.models")
    if resp.status != 200:
        ctx.violate(name, xi, [Violation("http.models", f"GET /v1/models got {resp.status}")])
        return
    models = resp.data.get("models") if resp.is_json and isinstance(resp.data, dict) else None
    ok = isinstance(models, list) and models and all(
        isinstance(m, dict) and all(isinstance(m.get(k), str) for k in ("name", "description", "release_date")) for m in models)
    if not ok:
        ctx.violate(name, xi, [Violation("http.models", f"body is not {{\"models\": [{{name, description, release_date}}]}}: {resp.excerpt(160)}")])


# ---------------------------------------------------------------- request acceptance

@case("model-alias")
def _(ctx: Ctx, name: str) -> None:
    """model "jev-latest" is accepted (the SDKs' default)."""
    if "model_fallback" in ctx.info or ctx.client.model == "jev-latest":
        ctx.exercise(name, "request.model-alias")  # the preflight sent it; a failure was recorded there
        return
    payload = {"model": "jev-latest", "state": TICKET, "questions": {"q": dict(NOUL)}}
    ctx.expect_answer(name, payload, "request.model-alias")


@case("noul-basic")
def _(ctx: Ctx, name: str) -> None:
    """A noul question with instructions only."""
    ctx.expect_answer(name, ctx.payload({"refund": dict(NOUL)}), "http.endpoint")


@case("noul-criteria")
def _(ctx: Ctx, name: str) -> None:
    """Noul criteria: two-sided, true-only, false-only, null."""
    variants = {
        "both": {"true": "They want a refund or chargeback", "false": "They want anything else"},
        "true-only": {"true": "They want a refund or chargeback"},
        "false-only": {"false": "They are only asking a question"},
        "null": None,
    }
    for label, crit in variants.items():
        ctx.expect_answer(f"{name}:{label}", ctx.payload({"refund": {**NOUL, "criteria": crit}}), "noul.criteria")


@case("noul-no-instructions")
def _(ctx: Ctx, name: str) -> None:
    """A noul with criteria but no instructions."""
    q = {"type": "noul", "criteria": {"true": "The customer threatens a chargeback", "false": "No threat"}}
    ctx.expect_answer(name, ctx.payload({"threat": q}), "noul.no-instructions")


@case("choice-basic")
def _(ctx: Ctx, name: str) -> None:
    """A three-option choice."""
    if ctx.expect_answer(name, ctx.payload({"team": dict(CHOICE)}), "choice.options") is not None:
        ctx.info["types_ok"].add("choice")


@case("choice-null-description")
def _(ctx: Ctx, name: str) -> None:
    """Options with null descriptions."""
    if not ctx.supports(name, ("choice",), "choice.null-description"):
        return
    q = {"type": "choice", "instructions": "Which team should handle this ticket?",
         "criteria": {"Billing": None, "Technical": None, "Sales": None}}
    ctx.expect_answer(name, ctx.payload({"team": q}), "choice.null-description")


@case("choice-options")
def _(ctx: Ctx, name: str) -> None:
    """2 options, 26, 64, 128 and 255 — the caps servers actually use, and the documented maximum."""
    limits = ctx.info.setdefault("limits", {})
    for n in (2, 26, 64, 128, 255):
        options = {"Billing": "Payments, invoices, refunds", "Technical": "Bugs and outages"} if n == 2 else \
            {"Billing": "Payments, invoices, refunds", **{f"Queue {i:03d}": f"Tickets routed to queue {i}" for i in range(1, n)}}
        q = {"type": "choice", "instructions": "Which queue should this ticket go to?", "criteria": options}
        before = len(ctx.inconclusive)
        if ctx.expect_answer(f"{name}:{n}", ctx.payload({"queue": q}), "choice.options") is None:
            if len(ctx.inconclusive) == before:
                limits["choice options rejected at"] = n
            break
        limits["choice options accepted up to"] = n


@case("score-levels")
def _(ctx: Ctx, name: str) -> None:
    """2, 3, 5 and 10 levels."""
    limits = ctx.info.setdefault("limits", {})
    for n in (2, 3, 5, 10):
        levels = ["Calm", "Very angry"] if n == 2 else SCORE["criteria"] if n == 3 else \
            [f"Level {i}: {'calm' if i == 0 else 'angrier'}" for i in range(n)]
        q = {"type": "score", "instructions": "How frustrated is the customer?", "criteria": levels}
        before = len(ctx.inconclusive)
        if ctx.expect_answer(f"{name}:{n}", ctx.payload({"anger": q}), "score.levels") is None:
            if len(ctx.inconclusive) == before:
                limits["score levels rejected at"] = n
            break
        limits["score levels accepted up to"] = n
        ctx.info["types_ok"].add("score")


@case("choice-ambiguous")
def _(ctx: Ctx, name: str) -> None:
    """A question the state cannot settle, so the probabilities spread and the confidence formula
    is actually tested (on a clear-cut question most formulas agree near 1)."""
    if not ctx.supports(name, ("choice", "score"), "confidence.formula"):
        return
    state = "Hello."
    qs = {"team": {"type": "choice", "instructions": "Which of these colours is the writer's favourite?",
                   "criteria": {"Red": None, "Green": None, "Blue": None, "Yellow": None, "Purple": None}},
          "mood": {"type": "score", "instructions": "How much does the writer enjoy jazz?",
                   "criteria": ["Not at all", "A little", "Somewhat", "A lot", "More than anything"]}}
    ctx.expect_answer(name, ctx.payload(qs, state=state))


@case("state-types")
def _(ctx: Ctx, name: str) -> None:
    """state as a string, an object and an array (with the noul question the preflight proved works)."""
    states = {
        "string": TICKET,
        "object": {"subject": "Charged twice", "body": TICKET, "customer": {"plan": "pro", "tickets": 3}},
        "array": ["Charged twice for March.", "Refund promised last week, not received.", "Will dispute the charge."],
    }
    for label, state in states.items():
        ctx.expect_answer(f"{name}:{label}", ctx.payload({"refund": dict(NOUL)}, state=state), "request.state")


@case("structured-text")
def _(ctx: Ctx, name: str) -> None:
    """instructions and descriptions as objects and arrays, one question type at a time."""
    qs = {
        "noul": {"type": "noul", "instructions": {"task": "Decide whether the customer wants money back", "include": ["refunds", "chargebacks"]},
                 "criteria": {"true": {"examples": ["refund me", "I'll dispute this"]}, "false": ["questions", "complaints without a request"]}},
        "choice": {"type": "choice", "instructions": ["Route the ticket.", "Pick exactly one team."],
                   "criteria": {"Billing": {"owns": ["invoices", "refunds"]}, "Technical": ["bugs", "outages"], "Sales": "Pricing"}},
        "score": {"type": "score", "instructions": {"scale": "frustration"},
                  "criteria": [{"label": "Calm"}, {"label": "Frustrated"}, {"label": "Very angry", "signals": ["threats"]}]},
    }
    for label, q in qs.items():
        if ctx.supports(f"{name}:{label}", (label,), "request.structured-text"):
            ctx.expect_answer(f"{name}:{label}", ctx.payload({"q": q}), "request.structured-text")


@case("multi-question")
def _(ctx: Ctx, name: str) -> None:
    """noul, choice and score in one request."""
    if not ctx.supports(name, ("choice", "score"), "request.multi"):
        return
    ctx.expect_answer(name, ctx.payload({"refund": dict(NOUL), "team": dict(CHOICE), "anger": dict(SCORE)}), "request.multi",
                      remap={("response.answer-ids", "missing-answer"): "request.multi"})


@case("question-ids")
def _(ctx: Ctx, name: str) -> None:
    """Question ids with -, ., spaces, Hangul and emoji, each in its own request."""
    for qid in ["ticket-1", "q.2", "with space", "질문", "🎯"]:
        ctx.expect_answer(f"{name}:{qid}", ctx.payload({qid: dict(NOUL)}), "request.question-ids",
                          remap={("response.answer-ids", "missing-answer"): "request.question-ids"})


def _unicode_keys(ctx: Ctx) -> Callable[[list[Violation], Response], list[Violation]]:
    """In the unicode case every option name is non-ASCII. A key mismatch or a `choice` that is not
    an option is a round-trip failure (request.unicode) — unless the ASCII choice case already showed
    a key problem, in which case it is that problem again and keeps its own id."""
    def transform(violations: list[Violation], resp: Response) -> list[Violation]:
        ascii_key_problem = any(f.req == "choice.probability-keys" or (f.req, f.tag) == ("choice.argmax", "not-an-option")
                                for f in ctx.findings)
        out = []
        for v in violations:
            if not ascii_key_problem and (v.tag == "option-keys" or (v.req, v.tag) == ("choice.argmax", "not-an-option")):
                v = Violation("request.unicode", v.message + " (non-ASCII option names did not round-trip)", v.where, v.tag)
            out.append(v)
        return out
    return transform


UNICODE_OPTIONS = {"환불 요청": "고객이 돈을 돌려받기를 원함", "배송 문의": "배송 상태를 물음", "🙂 기타": "그 외"}  # no ASCII letters


@case("unicode")
def _(ctx: Ctx, name: str) -> None:
    """Hangul and emoji in state, instructions and option names; names must round-trip exactly."""
    if not ctx.supports(name, ("choice",), "request.unicode"):
        return
    q = {"type": "choice", "instructions": "이 문의는 어떤 유형인가요?", "criteria": dict(UNICODE_OPTIONS)}
    ctx.expect_answer(name, ctx.payload({"kind": q}, state="배송이 3일째 안 와요. 그냥 환불해 주세요 😡"), "request.unicode",
                      transform=_unicode_keys(ctx))


@case("unknown-fields")
def _(ctx: Ctx, name: str) -> None:
    """Unknown top-level fields are ignored."""
    resp = ctx.expect_answer(name, ctx.payload({"refund": dict(NOUL)}, x_trace_id="jevcompat", seed=7), "request.unknown-fields")
    ctx.info["unknown_fields_ok"] = resp is not None


# ---------------------------------------------------------------- invalid and out-of-range requests

@case("invalid")
def _(ctx: Ctx, name: str) -> None:
    """Requests every official source rejects: 4xx expected, 5xx never."""
    base = ctx.payload({"refund": dict(NOUL)})
    cases: dict[str, Any] = {
        "not-json": b'{"model": "jev-latest", "state": "x", "questions": {',
        "missing-state": {k: v for k, v in base.items() if k != "state"},
        "missing-questions": {k: v for k, v in base.items() if k != "questions"},
        "empty-questions": {**base, "questions": {}},
        "missing-type": {**base, "questions": {"refund": {"instructions": "Refund?"}}},
        "type-boolean": {**base, "questions": {"refund": {"type": "boolean", "instructions": "Refund?"}}},
        "choice-no-options": {**base, "questions": {"team": {"type": "choice", "instructions": "Team?", "criteria": {}}}},
    }
    for label, payload in cases.items():
        ctx.expect_reject(f"{name}:{label}", payload)
    ctx.expect_reject(f"{name}:score-map", {**base, "questions": {"anger": {
        "type": "score", "instructions": "How frustrated?", "criteria": {"0": "Calm", "1": "Frustrated", "2": "Very angry"}}}},
        "score.map-rejected")


@case("out-of-range")
def _(ctx: Ctx, name: str) -> None:
    """Outside the documented ranges: answer or 4xx, never 5xx."""
    base = ctx.payload({})
    many = {"Billing": None, **{f"Queue {i:03d}": None for i in range(1, 256)}}
    cases = {
        "choice-1": {"team": {"type": "choice", "instructions": "Team?", "criteria": {"Billing": None}}},
        "choice-256": {"queue": {"type": "choice", "instructions": "Queue?", "criteria": many}},
        "score-1": {"anger": {"type": "score", "instructions": "Frustration?", "criteria": ["Calm"]}},
        "score-11": {"anger": {"type": "score", "instructions": "Frustration?", "criteria": [f"Level {i}" for i in range(11)]}},
        "score-null-level": {"anger": {"type": "score", "instructions": "Frustration?", "criteria": ["Calm", None]}},
    }
    for label, qs in cases.items():
        ctx.expect_answer_or_4xx(f"{name}:{label}", {**base, "questions": qs})
    ctx.expect_answer_or_4xx(f"{name}:state-null", {**base, "state": None, "questions": {"refund": dict(NOUL)}})


@case("unknown-model")
def _(ctx: Ctx, name: str) -> None:
    """An unknown model name: answer, or a 4xx with the error shape."""
    payload = {**ctx.payload({"refund": dict(NOUL)}), "model": "jevcompat-no-such-model"}
    got = ctx._send(name, payload, ("errors.no-5xx",))
    if got is None:
        return
    resp, xi = got
    ctx.exercise(name, "errors.no-5xx")
    if resp.status >= 500:
        ctx.violate(name, xi, [Violation("errors.no-5xx", f"got {resp.status}: {resp.excerpt(160)}")])
    elif resp.status == 422:
        ctx.exercise(name, *ERROR_JSON_REQS, "errors.validation-shape")
        ctx.violate(name, xi, validate_validation_error(resp))
    elif resp.status >= 400:
        ctx.exercise(name, *ERROR_JSON_REQS, "errors.shape")
        ctx.violate(name, xi, validate_error_shape(resp))


# ---------------------------------------------------------------- auth

@case("auth")
def _(ctx: Ctx, name: str) -> None:
    """With --key: a missing key and a wrong key are refused with authentication_error."""
    reqs = ("auth.missing", "auth.invalid")
    if not ctx.key_given:
        ctx.skip("no --key given (auth is off, or untested)", *reqs, "auth.bearer")
        return
    if ctx.auth_mode == "none":
        ctx.skip("auth is off (requests without a key are answered)", *reqs, "auth.bearer")
        return
    payload = ctx.payload({"refund": dict(NOUL)})
    try:
        missing, xm = ctx.post(f"{name}:missing", payload, auth=False)
        wrong, xw = ctx.post(f"{name}:wrong", payload, auth="jevcompat-wrong-key")
    except Timeout as e:
        ctx.timed_out(name, e, reqs)
        return
    if missing.status == 200 and wrong.status == 200:
        ctx.skip("auth appears to be off: requests without a key and with a wrong key were both answered", *reqs)
        return
    for req, resp, xi, allowed in (("auth.missing", missing, xm, (401, 403)), ("auth.invalid", wrong, xw, (401,))):
        ctx.exercise(name, req)
        if resp.status not in allowed:
            ctx.violate(name, xi, [Violation(req, f"got {resp.status}, expected {' or '.join(map(str, allowed))}")])
        if resp.status >= 400:
            ctx.violate(name, xi, validate_error_shape(resp, req, "authentication_error"))


# ---------------------------------------------------------------- semantics (SPEC §7)

SEM_QUESTIONS = {"refund": NOUL, "team": CHOICE, "anger": SCORE}
EXTRA_QUESTIONS = {
    "urgent": {"type": "noul", "instructions": "Does the customer need an answer today?"},
    "lang": {"type": "choice", "instructions": "What language is the ticket in?", "criteria": {"English": None, "Other": None}},
    "polite": {"type": "score", "instructions": "How polite is the message?", "criteria": ["Rude", "Neutral", "Polite"]},
}


def _samples(ctx: Ctx, name: str, questions: dict, k: int) -> list[dict] | str:
    """k answer maps for the same request, or the reason there are none."""
    out = []
    for i in range(k):
        extra = {"x_nonce": uuid.uuid4().hex} if ctx.info.get("unknown_fields_ok") else {}
        try:
            resp, _ = ctx.post(f"{name}:{i + 1}", ctx.payload({q: dict(v) for q, v in questions.items()}, **extra))
        except Timeout as e:
            ctx.inconclusive.append(f"{name}: {e}")
            return f"timed out or busy ({e})"
        except TransportError as e:
            return f"no complete HTTP response ({e})"
        if resp.status != 200 or not isinstance(resp.data, dict) or not isinstance(resp.data.get("answers"), dict):
            return f"the request got {resp.status}"
        out.append(resp.data["answers"])
    return out


@dataclass
class _Judgement:
    too_noisy: bool
    differs: dict[tuple[str, str], tuple[int, float, float]]  # (question, number) -> (sign, |Δmean|, limit)
    worst_limit: float


def _judge(base: list[dict], variant: list[dict], mapping: dict[str, str]) -> _Judgement | None:
    """SPEC §7: per number, |m − m′| against max(floor, z · pooled sd · √(1/k₁ + 1/k₂))."""
    differs: dict[tuple[str, str], tuple[int, float, float]] = {}
    worst = 0.0
    compared = 0
    for q, q2 in mapping.items():
        va = [answer_vector(a.get(q)) for a in base]
        vb = [answer_vector(a.get(q2)) for a in variant]
        keys = set(va[0])
        if not keys or any(set(v) != keys for v in va + vb):
            continue  # shape problems are other requirements' business
        for key in keys:
            xs, ys = [v[key] for v in va], [v[key] for v in vb]
            ma, mb = sum(xs) / len(xs), sum(ys) / len(ys)
            ss = sum((x - ma) ** 2 for x in xs) + sum((y - mb) ** 2 for y in ys)
            sd = math.sqrt(ss / max(1, len(xs) + len(ys) - 2))
            limit = max(spec.SEM_FLOOR, spec.SEM_Z * sd * math.sqrt(1 / len(xs) + 1 / len(ys)))
            worst = max(worst, limit)
            compared += 1
            if abs(ma - mb) > limit:
                differs[(q, key)] = (1 if mb > ma else -1, abs(ma - mb), limit)
    if not compared:
        return None
    return _Judgement(worst >= spec.SEM_TOO_NOISY, differs, worst)


def _compare(ctx: Ctx, name: str, req: str, questions: dict, mapping: dict[str, str], what: str) -> None:
    if not ctx.supports(name, ("choice", "score"), req):
        return
    k = spec.SEM_REPEATS
    if "baseline" not in ctx.cache:
        ctx.cache["baseline"] = _samples(ctx, "semantics-baseline", SEM_QUESTIONS, k)
    base = ctx.cache["baseline"]
    if isinstance(base, str):
        ctx.skip(f"the baseline request could not be sampled: {base}", req)
        return
    variant = _samples(ctx, name, questions, k)
    if isinstance(variant, str):
        ctx.skip(f"the variant request could not be sampled: {variant}", req)
        return
    judged = _judge(base, variant, mapping)
    while judged is not None and judged.too_noisy and len(variant) < spec.SEM_MAX_REPEATS:
        more_base = _samples(ctx, "semantics-baseline+", SEM_QUESTIONS, spec.SEM_REPEATS) if len(base) <= len(variant) else []
        more_var = _samples(ctx, f"{name}+", questions, spec.SEM_REPEATS)
        if isinstance(more_base, str) or isinstance(more_var, str):
            break
        base = ctx.cache["baseline"] = base + more_base
        variant = variant + more_var
        judged = _judge(base, variant, mapping)
    if judged is None:
        ctx.skip("no comparable answers", req)
        return
    if judged.too_noisy:
        ctx.skip(f"too noisy to judge: after {len(variant)} sends the limit is still {judged.worst_limit:.2f}", req)
        return
    ctx.exercise(name, req)
    if not judged.differs:
        return
    # Confirm on fresh sends: fail only if the same number moves the same way again.
    fresh_base = _samples(ctx, "semantics-confirm-base", SEM_QUESTIONS, len(variant))
    fresh_var = _samples(ctx, f"{name}-confirm", questions, len(variant))
    if isinstance(fresh_base, str) or isinstance(fresh_var, str):
        ctx.skip("a difference was seen but could not be confirmed (the confirmation sends failed)", req)
        ctx.exercised.get(req, set()).discard(name)
        return
    again = _judge(fresh_base, fresh_var, mapping)
    confirmed = [key for key, (sign, _, _) in judged.differs.items()
                 if again is not None and again.differs.get(key, (0,))[0] == sign]
    if confirmed:
        q, key = max(confirmed, key=lambda kk: again.differs[kk][1])
        _, d, limit = again.differs[(q, key)]
        what_moved = f"{q!r}" + ("" if key == "noul" else f" option {key!r}")
        ctx.violate(name, len(ctx.exchanges) - 1, [Violation(
            req, f"{what} moved {what_moved} by {d:.3f} on average (limit {limit:.3f}); "
                 f"seen in two independent rounds of {len(variant)} sends each")])


@case("semantics-question-id")
def _(ctx: Ctx, name: str) -> None:
    """Renaming question ids does not change the answers."""
    mapping = {"refund": "zz-renamed.1", "team": "Q 🙂", "anger": "x_y_z"}
    _compare(ctx, name, "semantics.question-id", {mapping[k]: v for k, v in SEM_QUESTIONS.items()}, mapping,
             "renaming the question ids")


@case("semantics-batching")
def _(ctx: Ctx, name: str) -> None:
    """Adding other questions does not change the answers."""
    _compare(ctx, name, "semantics.batching", {**SEM_QUESTIONS, **EXTRA_QUESTIONS}, {k: k for k in SEM_QUESTIONS},
             "adding three other questions")


@case("semantics-question-order")
def _(ctx: Ctx, name: str) -> None:
    """Reversing the question order does not change the answers."""
    _compare(ctx, name, "semantics.question-order", {k: SEM_QUESTIONS[k] for k in reversed(list(SEM_QUESTIONS))},
             {k: k for k in SEM_QUESTIONS}, "reversing the question order")


# ---------------------------------------------------------------- drop-in

@case("sdk-python")
def _(ctx: Ctx, name: str) -> None:
    """The official Python SDK parses a noul, a choice and a score answer."""
    if not ctx.sdk:
        ctx.skip("disabled with --no-sdk", "dropin.sdk-python")
        return
    try:
        from typesafe_sdk import Choice, Noul, Score, TypeSafeClient
    except ImportError:
        ctx.skip("typesafe-sdk is not importable", "dropin.sdk-python")
        return
    if ctx.auth_mode == "x-api-key":
        ctx.skip("the server does not read Authorization: Bearer, which the SDK sends", "dropin.sdk-python")
        return
    if not ctx.supports(name, ("choice", "score"), "dropin.sdk-python"):
        return
    questions = {
        "refund": Noul(instructions=NOUL["instructions"]),
        "team": Choice(instructions=CHOICE["instructions"], criteria=CHOICE["criteria"]),
        "anger": Score(instructions=SCORE["instructions"], criteria=SCORE["criteria"]),
    }
    shown = {"model": ctx.client.model, "questions": {"refund": NOUL, "team": CHOICE, "anger": SCORE}, "state": TICKET}
    path = "/v1/systemone"
    try:
        with TypeSafeClient(api_key=ctx.client.key or "jevcompat-no-key", base_url=ctx.client.base_url,
                            timeout=ctx.client.timeout) as client:
            r = client.system_one(state=TICKET, questions=questions, model=ctx.client.model)
    except Exception as e:  # noqa: BLE001 — any exception from the SDK is the finding
        if "timeout" in type(e).__name__.lower():
            ctx.timed_out(name, Timeout(f"typesafe-sdk: {e}"), ("dropin.sdk-python",))
            return
        xi = ctx._record(name, "POST", path, shown, None, f"{type(e).__name__}: {e}", via="typesafe-sdk")
        ctx.exercise(name, "dropin.sdk-python")
        ctx.violate(name, xi, [Violation("dropin.sdk-python", f"typesafe-sdk raised {type(e).__name__}: {str(e)[:300]}")])
        return
    ctx.exercise(name, "dropin.sdk-python")
    got = {"refund": r.nouls.get("refund"), "team": r.choices.get("team"), "anger": r.scores.get("anger")}
    missing = [k for k, v in got.items() if v is None]
    summary = {k: (getattr(v, "noul", None) or getattr(v, "choice", None) or getattr(v, "score", None)) for k, v in got.items() if v}
    xi = ctx._record(name, "POST", path, shown, None, json.dumps(summary, ensure_ascii=False, default=str),
                     via="typesafe-sdk", status=200)
    if missing:
        ctx.violate(name, xi, [Violation("dropin.sdk-python", f"typesafe-sdk parsed the response but found no "
                                                              f"{'/'.join(missing)} answer of the expected type")])
