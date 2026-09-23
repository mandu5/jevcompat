"""The conformance cases. Each one sends real requests and records which requirements it
exercised and which it found violated, with the exchange that shows it.

A requirement passes when at least one case exercised it and no case found a violation.
"""
from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from . import spec
from .client import Client, Response, TransportError
from .validate import (
    Violation,
    check_json,
    max_difference,
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

RESPONSE_REQS = ("http.endpoint", "http.json", "response.envelope", "response.usage", "response.answer-ids",
                 "response.answer-type", "response.finite", "response.extensions")
TYPE_REQS = {
    "noul": ("noul.answer",),
    "choice": ("choice.answer", "choice.probability-keys", "choice.distribution", "choice.argmax",
               "confidence.range", "confidence.formula"),
    "score": ("score.answer", "score.legend", "score.probability-keys", "score.distribution", "score.expectation",
              "confidence.range", "confidence.formula"),
}


class Abort(Exception):
    """Nothing further can be tested (no endpoint, auth needed, no usable model)."""


@dataclass
class Exchange:
    case: str
    method: str
    path: str
    request: Any
    status: int | None
    response: str
    ms: float | None


@dataclass
class Finding:
    req: str
    message: str
    where: str
    case: str
    exchange: int | None  # index into Ctx.exchanges


@dataclass
class Ctx:
    client: Client
    key_given: bool
    sdk: bool = True
    progress: Callable[[str], None] | None = None
    exchanges: list[Exchange] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)
    exercised: dict[str, set[str]] = field(default_factory=dict)
    skipped: dict[str, str] = field(default_factory=dict)
    info: dict[str, Any] = field(default_factory=dict)
    send_auth: bool = True
    cache: dict[str, Any] = field(default_factory=dict)

    # -- plumbing
    def _record(self, case: str, method: str, path: str, request: Any, resp: Response | None, err: str = "") -> int:
        self.exchanges.append(Exchange(case, method, path, request, resp.status if resp else None,
                                       resp.excerpt(600) if resp else err, round(resp.ms, 1) if resp else None))
        return len(self.exchanges) - 1

    def post(self, case: str, payload: Any, *, auth: Any = True, path: str = "/v1/systemone") -> tuple[Response, int]:
        if auth is True and not self.send_auth:
            auth = False
        shown = payload.decode("utf-8", "replace") if isinstance(payload, bytes) else payload
        try:
            resp = self.client.post_json(path, payload, auth=auth)
        except TransportError as e:
            self._record(case, "POST", path, shown, None, str(e))
            raise
        return resp, self._record(case, "POST", path, shown, resp)

    def get(self, case: str, path: str) -> tuple[Response, int]:
        try:
            resp = self.client.request("GET", path, auth=False if not self.send_auth else True)
        except TransportError as e:
            self._record(case, "GET", path, None, None, str(e))
            raise
        return resp, self._record(case, "GET", path, None, resp)

    def payload(self, questions: dict, state: Any = TICKET, **extra: Any) -> dict:
        return {"model": self.client.model, "state": state, "questions": questions, **extra}

    def exercise(self, case: str, *reqs: str) -> None:
        for r in reqs:
            self.exercised.setdefault(r, set()).add(case)

    def violate(self, case: str, xi: int | None, violations: list[Violation], remap: dict[str, str] | None = None) -> None:
        for v in violations:
            req = (remap or {}).get(v.req, v.req)
            self.exercise(case, req)
            self.findings.append(Finding(req, v.message, v.where, case, xi))

    def skip(self, reason: str, *reqs: str) -> None:
        for r in reqs:
            self.skipped.setdefault(r, reason)

    def _post_or_record(self, case: str, payload: Any, reqs: tuple[str, ...]) -> tuple[Response, int] | None:
        """POST; a request that gets no HTTP response at all is a finding against `reqs`."""
        try:
            return self.post(case, payload)
        except TransportError as e:
            self.violate(case, len(self.exchanges) - 1, [Violation(r, f"no HTTP response: {e}") for r in reqs])
            return None

    # -- the three shapes of case
    def expect_answer(self, case: str, payload: dict, *accept_reqs: str, remap: dict[str, str] | None = None) -> Response | None:
        """A valid request: must be answered with 200 and a response meeting §4."""
        self.exercise(case, *accept_reqs)
        got = self._post_or_record(case, payload, accept_reqs or ("http.endpoint",))
        if got is None:
            return None
        resp, xi = got
        if resp.status != 200:
            why = f"valid request got {resp.status}: {resp.excerpt(200)}"
            self.violate(case, xi, [Violation(r, why) for r in accept_reqs])
            if resp.status >= 500:
                self.violate(case, xi, [Violation("errors.no-5xx", why)])
            return None
        types = {q.get("type") for q in payload["questions"].values() if isinstance(q, dict)}
        self.exercise(case, *RESPONSE_REQS, *(r for t in types if t in TYPE_REQS for r in TYPE_REQS[t]))
        self.violate(case, xi, validate_success(payload, resp), remap)
        return resp

    def expect_reject(self, case: str, payload: Any, *reqs: str) -> None:
        """An invalid request: must get a 4xx (SHOULD) and never a 5xx (MUST)."""
        self.exercise(case, "errors.no-5xx", "errors.reject-invalid", *reqs)
        got = self._post_or_record(case, payload, ("errors.no-5xx",))
        if got is None:
            return
        resp, xi = got
        if resp.status >= 500:
            self.violate(case, xi, [Violation("errors.no-5xx", f"invalid request got {resp.status}: {resp.excerpt(160)}")])
        elif resp.status < 400:
            why = f"invalid request was answered with {resp.status}"
            self.violate(case, xi, [Violation(r, why) for r in ("errors.reject-invalid", *reqs)])
        else:
            self.exercise(case, "http.json", "errors.validation-shape")
            self.violate(case, xi, validate_validation_error(resp))

    def expect_answer_or_4xx(self, case: str, payload: dict) -> None:
        """Outside the documented ranges: answering and rejecting are both fine; 5xx is not."""
        self.exercise(case, "errors.no-5xx")
        got = self._post_or_record(case, payload, ("errors.no-5xx",))
        if got is None:
            return
        resp, xi = got
        if resp.status >= 500:
            self.violate(case, xi, [Violation("errors.no-5xx", f"got {resp.status}: {resp.excerpt(160)}")])
        elif resp.status == 200:
            types = {q.get("type") for q in payload["questions"].values() if isinstance(q, dict)}
            self.exercise(case, *RESPONSE_REQS, *(r for t in types if t in TYPE_REQS for r in TYPE_REQS[t]))
            self.violate(case, xi, validate_success(payload, resp))
        elif resp.status >= 400:
            self.exercise(case, "http.json", "errors.validation-shape")
            self.violate(case, xi, validate_validation_error(resp))


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
    """One plain noul question. Settles the endpoint, auth and model before anything else."""
    name = "preflight"
    payload = ctx.payload({"q": dict(NOUL)})
    resp, xi = ctx.post(name, payload)
    if resp.status in (401, 403):
        if ctx.key_given:
            ctx.violate(name, xi, [Violation("auth.bearer", f"the key sent as Authorization: Bearer was refused: {resp.status} {resp.excerpt(160)}")])
            raise Abort("the server refused the key sent as `Authorization: Bearer <key>`")
        bare, xj = ctx.post(name, payload, auth=False)
        if bare.status == 200:
            ctx.violate(name, xj, [Violation("auth.ignored-when-off",
                                             f"a request with `Authorization: Bearer …` got {resp.status}; the same request without the header got 200")])
            ctx.send_auth = False
            resp, xi = bare, xj
        else:
            raise Abort(f"the server requires an API key ({resp.status}); pass --key")
    elif not ctx.key_given:
        ctx.exercise(name, "auth.ignored-when-off")
    if ctx.key_given:
        ctx.exercise(name, "auth.bearer")
    if resp.status in (404, 405) and not _mentions_model(resp):
        ctx.violate(name, xi, [Violation("http.endpoint", f"POST /v1/systemone got {resp.status}: {resp.excerpt(160)}")])
        raise Abort(f"no POST /v1/systemone at {ctx.client.base_url} ({resp.status})")
    if resp.status != 200 and ctx.client.model == "jev-latest":
        ctx.exercise(name, "request.model-alias")
        ctx.violate(name, xi, [Violation("request.model-alias", f"model \"jev-latest\" got {resp.status}: {resp.excerpt(200)}")])
        other = _served_model(ctx)
        if not other:
            raise Abort("the server rejects model \"jev-latest\" and lists no other model; pass --model NAME")
        ctx.info["model_fallback"] = other
        ctx.client.model = other
        payload = ctx.payload({"q": dict(NOUL)})
        resp, xi = ctx.post(name, payload)
    if resp.status != 200:
        ctx.exercise(name, "http.endpoint")
        ctx.violate(name, xi, [Violation("http.endpoint", f"a minimal valid request got {resp.status}: {resp.excerpt(200)}")])
        raise Abort(f"a minimal valid request got {resp.status}; nothing else can be tested")
    ctx.info["model_reported"] = resp.data.get("model") if isinstance(resp.data, dict) else None


def _mentions_model(resp: Response) -> bool:
    return b"model" in resp.body.lower()


def _served_model(ctx: Ctx) -> str | None:
    try:
        resp, _ = ctx.get("preflight", "/v1/models")
    except TransportError:
        return None
    models = resp.data.get("models") if resp.status == 200 and isinstance(resp.data, dict) else None
    for m in models or []:
        if isinstance(m, dict) and isinstance(m.get("name"), str) and m["name"] != "jev-latest":
            return m["name"]
    return None


# ---------------------------------------------------------------- transport

@case("models-endpoint")
def _(ctx: Ctx, name: str) -> None:
    """GET /v1/models lists at least one model with name, description and release_date."""
    resp, xi = ctx.get(name, "/v1/models")
    ctx.exercise(name, "http.models")
    if resp.status != 200:
        ctx.violate(name, xi, [Violation("http.models", f"GET /v1/models got {resp.status}")])
        return
    ctx.violate(name, xi, [v for v in check_json(resp) if v.req != "http.json"] +
                ([] if resp.is_json else [Violation("http.models", resp.json_error or "")]))
    models = resp.data.get("models") if isinstance(resp.data, dict) else None
    ok = isinstance(models, list) and models and all(
        isinstance(m, dict) and all(isinstance(m.get(k), str) for k in ("name", "description", "release_date")) for m in models)
    if not ok:
        ctx.violate(name, xi, [Violation("http.models", f"body is not {{\"models\": [{{name, description, release_date}}]}}: {resp.excerpt(160)}")])


# ---------------------------------------------------------------- request acceptance

@case("model-alias")
def _(ctx: Ctx, name: str) -> None:
    """model "jev-latest" is accepted (the SDKs' default)."""
    if "model_fallback" in ctx.info or ctx.client.model == "jev-latest":
        ctx.exercise(name, "request.model-alias")  # preflight already sent it; a failure was recorded there
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
        "true_only": {"true": "They want a refund or chargeback"},
        "false_only": {"false": "They are only asking a question"},
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
    ctx.expect_answer(name, ctx.payload({"team": dict(CHOICE)}))


@case("choice-null-description")
def _(ctx: Ctx, name: str) -> None:
    """Options with null descriptions."""
    q = {"type": "choice", "instructions": "Which team should handle this ticket?",
         "criteria": {"Billing": None, "Technical": None, "Sales": None}}
    ctx.expect_answer(name, ctx.payload({"team": q}), "choice.null-description")


@case("choice-options")
def _(ctx: Ctx, name: str) -> None:
    """2 options, 26, 64, 128 and 255 — the caps servers actually use, and the documented maximum."""
    for n in (2, 26, 64, 128, 255):
        options = {"Billing": "Payments, invoices, refunds", "Technical": "Bugs and outages"} if n == 2 else \
            {"Billing": "Payments, invoices, refunds", **{f"Queue {i:03d}": None for i in range(1, n)}}
        q = {"type": "choice", "instructions": "Which queue should this ticket go to?", "criteria": options}
        if ctx.expect_answer(f"{name}:{n}", ctx.payload({"queue": q}), "choice.options") is None:
            ctx.info.setdefault("limits", {})["choice_options_failed_at"] = n
            break
        ctx.info.setdefault("limits", {})["choice_options_ok"] = n


@case("score-levels")
def _(ctx: Ctx, name: str) -> None:
    """2, 3, 5 and 10 levels."""
    for n in (2, 3, 5, 10):
        levels = ["Calm", "Very angry"] if n == 2 else SCORE["criteria"] if n == 3 else [f"Level {i}: {'calm' if i == 0 else 'angrier'}" for i in range(n)]
        q = {"type": "score", "instructions": "How frustrated is the customer?", "criteria": levels}
        if ctx.expect_answer(f"{name}:{n}", ctx.payload({"anger": q}), "score.levels") is None:
            ctx.info.setdefault("limits", {})["score_levels_failed_at"] = n
            break
        ctx.info.setdefault("limits", {})["score_levels_ok"] = n


@case("state-types")
def _(ctx: Ctx, name: str) -> None:
    """state as a string, an object and an array."""
    states = {
        "string": TICKET,
        "object": {"subject": "Charged twice", "body": TICKET, "customer": {"plan": "pro", "tickets": 3}},
        "array": ["Charged twice for March.", "Refund promised last week, not received.", "Will dispute the charge."],
    }
    for label, state in states.items():
        ctx.expect_answer(f"{name}:{label}", ctx.payload({"refund": dict(NOUL), "team": dict(CHOICE)}, state=state), "request.state")


@case("structured-text")
def _(ctx: Ctx, name: str) -> None:
    """instructions and descriptions as objects and arrays."""
    qs = {
        "refund": {"type": "noul", "instructions": {"task": "Decide whether the customer wants money back", "include": ["refunds", "chargebacks"]},
                   "criteria": {"true": {"examples": ["refund me", "I'll dispute this"]}, "false": ["questions", "complaints without a request"]}},
        "team": {"type": "choice", "instructions": ["Route the ticket.", "Pick exactly one team."],
                 "criteria": {"Billing": {"owns": ["invoices", "refunds"]}, "Technical": ["bugs", "outages"], "Sales": "Pricing"}},
        "anger": {"type": "score", "instructions": {"scale": "frustration"},
                  "criteria": [{"label": "Calm"}, {"label": "Frustrated"}, {"label": "Very angry", "signals": ["threats"]}]},
    }
    ctx.expect_answer(name, ctx.payload(qs), "request.structured-text")


@case("multi-question")
def _(ctx: Ctx, name: str) -> None:
    """noul, choice and score in one request."""
    ctx.expect_answer(name, ctx.payload({"refund": dict(NOUL), "team": dict(CHOICE), "anger": dict(SCORE)}), "request.multi",
                      remap={"response.answer-ids": "request.multi"})


@case("question-ids")
def _(ctx: Ctx, name: str) -> None:
    """Question ids with -, ., spaces, Hangul and emoji."""
    ids = ["ticket-1", "q.2", "with space", "질문", "🎯"]
    ctx.expect_answer(name, ctx.payload({i: dict(NOUL) for i in ids}), "request.question-ids",
                      remap={"response.answer-ids": "request.question-ids"})


@case("unicode")
def _(ctx: Ctx, name: str) -> None:
    """Hangul and emoji in state, instructions and option names; names must round-trip exactly."""
    q = {"type": "choice", "instructions": "이 문의는 어떤 유형인가요?",
         "criteria": {"환불 요청": "고객이 돈을 돌려받기를 원함", "배송 문의": None, "🙂 Other": "그 외"}}
    state = "배송이 3일째 안 와요. 그냥 환불해 주세요 😡"
    remap = {"choice.probability-keys": "request.unicode", "choice.argmax": "request.unicode"}
    ctx.expect_answer(name, ctx.payload({"유형": q}, state=state), "request.unicode", remap=remap)


@case("unknown-fields")
def _(ctx: Ctx, name: str) -> None:
    """Unknown top-level fields are ignored."""
    ctx.expect_answer(name, ctx.payload({"refund": dict(NOUL)}, x_trace_id="jevcompat", seed=7), "request.unknown-fields")


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
    resp, xi = ctx.post(name, payload)
    ctx.exercise(name, "errors.no-5xx")
    if resp.status >= 500:
        ctx.violate(name, xi, [Violation("errors.no-5xx", f"got {resp.status}: {resp.excerpt(160)}")])
    elif resp.status == 422:
        ctx.exercise(name, "errors.validation-shape")
        ctx.violate(name, xi, validate_validation_error(resp))
    elif resp.status >= 400:
        ctx.exercise(name, "errors.shape", "http.json")
        ctx.violate(name, xi, validate_error_shape(resp))


# ---------------------------------------------------------------- auth

@case("auth")
def _(ctx: Ctx, name: str) -> None:
    """With --key: a missing key and a wrong key are refused with authentication_error."""
    reqs = ("auth.missing", "auth.invalid")
    if not ctx.key_given:
        ctx.skip("auth is off or no --key was given", *reqs, "auth.bearer")
        return
    payload = ctx.payload({"refund": dict(NOUL)})
    for req, auth, allowed in (("auth.missing", False, (401, 403)), ("auth.invalid", "jevcompat-wrong-key", (401,))):
        resp, xi = ctx.post(f"{name}:{req.split('.')[1]}", payload, auth=auth)
        ctx.exercise(name, req)
        if resp.status not in allowed:
            ctx.violate(name, xi, [Violation(req, f"got {resp.status}, expected {' or '.join(map(str, allowed))}")])
        if resp.status >= 400:
            ctx.violate(name, xi, validate_error_shape(resp, req, "authentication_error"))


# ---------------------------------------------------------------- semantics

SEM_QUESTIONS = {"refund": NOUL, "team": CHOICE, "anger": SCORE}
EXTRA_QUESTIONS = {
    "urgent": {"type": "noul", "instructions": "Does the customer need an answer today?"},
    "lang": {"type": "choice", "instructions": "What language is the ticket in?", "criteria": {"English": None, "Other": None}},
    "polite": {"type": "score", "instructions": "How polite is the message?", "criteria": ["Rude", "Neutral", "Polite"]},
}


def _baseline(ctx: Ctx, name: str) -> tuple[dict, float] | None:
    """Send the same request twice; return the first answers and the noise between the two."""
    if "baseline" not in ctx.cache:
        payload = ctx.payload({k: dict(v) for k, v in SEM_QUESTIONS.items()})
        first, xi = ctx.post(f"{name}:baseline", payload)
        second, _ = ctx.post(f"{name}:baseline-repeat", payload)
        if first.status != 200 or second.status != 200 or not all(
                isinstance(r.data, dict) and isinstance(r.data.get("answers"), dict) for r in (first, second)):
            ctx.cache["baseline"] = None
        else:
            a, b = first.data["answers"], second.data["answers"]
            diffs = [max_difference(a.get(q), b.get(q)) for q in SEM_QUESTIONS]
            noise = max((d for d in diffs if d is not None), default=0.0)
            ctx.cache["baseline"] = (a, noise)
            ctx.info["repeat_noise"] = round(noise, 4)
    return ctx.cache["baseline"]


def _compare(ctx: Ctx, name: str, req: str, questions: dict, mapping: dict[str, str], what: str) -> None:
    base = _baseline(ctx, name)
    if base is None:
        ctx.skip("the baseline request was not answered", req)
        return
    answers, noise = base
    resp, xi = ctx.post(name, ctx.payload(questions))
    if resp.status != 200 or not isinstance(resp.data, dict) or not isinstance(resp.data.get("answers"), dict):
        ctx.skip(f"the variant request got {resp.status}", req)
        return
    ctx.exercise(name, req)
    limit = max(spec.SEM_FLOOR, spec.SEM_NOISE_K * noise)
    for q, q2 in mapping.items():
        d = max_difference(answers.get(q), resp.data["answers"].get(q2))
        if d is not None and d > limit:
            ctx.violate(name, xi, [Violation(req, f"{what} moved {q!r} by {d:.3f} (repeat noise {noise:.3f}, limit {limit:.3f})")])


@case("semantics-question-id")
def _(ctx: Ctx, name: str) -> None:
    """Renaming question ids does not change the answers."""
    mapping = {"refund": "zz-renamed.1", "team": "Q 🙂", "anger": "x_y_z"}
    qs = {mapping[k]: dict(v) for k, v in SEM_QUESTIONS.items()}
    _compare(ctx, name, "semantics.question-id", qs, mapping, "renaming the question ids")


@case("semantics-batching")
def _(ctx: Ctx, name: str) -> None:
    """Adding other questions does not change the answers."""
    qs = {**{k: dict(v) for k, v in SEM_QUESTIONS.items()}, **{k: dict(v) for k, v in EXTRA_QUESTIONS.items()}}
    _compare(ctx, name, "semantics.batching", qs, {k: k for k in SEM_QUESTIONS}, "adding three other questions")


@case("semantics-question-order")
def _(ctx: Ctx, name: str) -> None:
    """Reversing the question order does not change the answers."""
    qs = {k: dict(SEM_QUESTIONS[k]) for k in reversed(list(SEM_QUESTIONS))}
    _compare(ctx, name, "semantics.question-order", qs, {k: k for k in SEM_QUESTIONS}, "reversing the question order")


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
        ctx.skip("typesafe-sdk is not installed (pip install 'jevcompat[sdk]')", "dropin.sdk-python")
        return
    ctx.exercise(name, "dropin.sdk-python")
    questions = {
        "refund": Noul(instructions=NOUL["instructions"]),
        "team": Choice(instructions=CHOICE["instructions"], criteria=CHOICE["criteria"]),
        "anger": Score(instructions=SCORE["instructions"], criteria=SCORE["criteria"]),
    }
    key = ctx.client.key or "jevcompat-no-key"
    shown = {"model": ctx.client.model, "state": TICKET, "questions": {k: "(typesafe_sdk question)" for k in questions}}
    try:
        with TypeSafeClient(api_key=key, base_url=ctx.client.base_url, timeout=ctx.client.timeout) as client:
            r = client.system_one(state=TICKET, questions=questions, model=ctx.client.model)
            got = (r.nouls["refund"].noul, r.choices["team"].choice, r.scores["anger"].score)
        xi = ctx._record(name, "POST", "/v1/systemone (typesafe-sdk)", shown, None, json.dumps(got, ensure_ascii=False, default=str))
    except Exception as e:  # noqa: BLE001 — any exception is the finding
        xi = ctx._record(name, "POST", "/v1/systemone (typesafe-sdk)", shown, None, f"{type(e).__name__}: {e}")
        ctx.violate(name, xi, [Violation("dropin.sdk-python", f"typesafe-sdk raised {type(e).__name__}: {str(e)[:300]}")])
