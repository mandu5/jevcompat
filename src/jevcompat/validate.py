"""Pure checks of responses against SPEC.md. No I/O.

`checks.py` uses these to judge a server; `mock.py` and `proxy.py` use the reference formulas to
behave correctly. Every function returns Violations tagged with the requirement id they break.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from . import spec
from .client import Response

TOP_LEVEL = {"model", "answers", "usage"}
ANSWER_FIELDS = {
    "noul": {"type", "noul"},
    "choice": {"type", "choice", "probabilities", "confidence"},
    "score": {"type", "score", "legend", "probabilities", "confidence"},
}


@dataclass
class Violation:
    req: str
    message: str
    where: str = ""
    tag: str = ""  # finer kind, so a case can re-attribute precisely (e.g. "missing-answer")

    def __str__(self) -> str:
        return f"{self.where}: {self.message}" if self.where else self.message


def is_num(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def is_int(v: Any) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


def fmt(v: Any) -> str:
    return repr(v)


def _le(x: float, bound: float) -> bool:
    return x <= bound + spec.SLACK


# ---------------------------------------------------------------- reference formulas (SPEC §4.5)

def choice_confidence(probs: list[float]) -> float:
    n = len(probs)
    if n <= 1:
        return 1.0
    return (max(probs) - 1 / n) / (1 - 1 / n)


def _uniform_spread(n: int) -> float:
    return sum(abs(i - (n - 1) / 2) for i in range(n)) / n


def score_confidence(probs: list[float], mode: int | None = None) -> float:
    n = len(probs)
    if n <= 1:
        return 1.0
    if mode is None:
        mode = max(range(n), key=lambda i: probs[i])
    spread = sum(p * abs(i - mode) for i, p in enumerate(probs))
    return max(0.0, 1 - spread / _uniform_spread(n))


# ---------------------------------------------------------------- transport

def is_json_media_type(content_type: str) -> bool:
    media = content_type.split(";")[0].strip().lower()
    return media == "application/json" or media.endswith("+json")


def check_json(resp: Response, where: str = "", error: bool = False) -> list[Violation]:
    """JSON-ness of a response: MUST for 200 bodies, SHOULD for error bodies and for Content-Type."""
    out = []
    if not is_json_media_type(resp.content_type):
        shown = f"{resp.content_type!r}" if resp.content_type else "absent"
        out.append(Violation("http.content-type", f"Content-Type is {shown}, not a JSON media type", where))
    if not resp.is_json:
        req = "errors.json" if error else "http.json"
        out.append(Violation(req, f"{resp.json_error}; body starts {resp.excerpt(120)!r}", where))
    if resp.nonfinite:
        out.append(Violation("response.finite", f"body contains {', '.join(sorted(set(resp.nonfinite)))}", where))
    return out


# ---------------------------------------------------------------- success responses

def validate_success(request: dict, resp: Response) -> list[Violation]:
    """A 200 response to `request` against §4. Assumes the caller already required status 200."""
    out = check_json(resp)
    if not resp.is_json:
        return out
    body = resp.data
    if not isinstance(body, dict):
        return out + [Violation("response.envelope", f"body is {type(body).__name__}, not an object")]
    for key, kind in (("model", str), ("answers", dict), ("usage", dict)):
        if key not in body:
            out.append(Violation("response.envelope", f"missing {key!r}"))
        elif not isinstance(body[key], kind):
            out.append(Violation("response.envelope", f"{key!r} is {type(body[key]).__name__}, not {kind.__name__}"))
    extra = sorted(k for k in body if k not in TOP_LEVEL and not str(k).startswith("x_"))
    if extra:
        out.append(Violation("response.extensions", f"unprefixed top-level field(s) {', '.join(extra)}"))
    usage = body.get("usage")
    if isinstance(usage, dict):
        for key in ("input_tokens", "output_tokens"):
            v = usage.get(key)
            if not (is_int(v) and v >= 0):
                out.append(Violation("response.usage", f"{key} is {fmt(v)}, not a non-negative integer", "usage"))
    answers = body.get("answers")
    if not isinstance(answers, dict):
        return out
    questions = request.get("questions") or {}
    missing = [q for q in questions if q not in answers]
    added = [a for a in answers if a not in questions]
    if missing:
        out.append(Violation("response.answer-ids", f"no answer for {', '.join(map(repr, missing))}", "answers", "missing-answer"))
    if added:
        out.append(Violation("response.answer-ids", f"answer(s) for unknown id(s) {', '.join(map(repr, added))}", "answers", "added-answer"))
    for qid, question in questions.items():
        if qid in answers:
            out += validate_answer(question, answers[qid], f"answers[{qid!r}]")
    return out


def validate_answer(question: dict, answer: Any, where: str) -> list[Violation]:
    qtype = question.get("type")
    if not isinstance(answer, dict):
        return [Violation("response.answer-type", f"answer is {type(answer).__name__}, not an object", where)]
    if answer.get("type") != qtype:
        return [Violation("response.answer-type", f"type is {fmt(answer.get('type'))}, question type is {qtype!r}", where)]
    out: list[Violation] = []
    extra = sorted(k for k in answer if k not in ANSWER_FIELDS[qtype] and not str(k).startswith("x_"))
    if extra:
        out.append(Violation("response.extensions", f"unprefixed field(s) {', '.join(extra)}", where))
    if qtype == "noul":
        p = answer.get("noul")
        if not (is_num(p) and 0 <= p <= 1):
            out.append(Violation("noul.answer", f"noul is {fmt(p)}, not a probability", where))
        return out
    if qtype == "choice":
        return out + _validate_choice(question, answer, where)
    return out + _validate_score(question, answer, where)


def _distribution(req: str, probs: dict, keys: list[str], where: str) -> tuple[list[Violation], list[float] | None, float]:
    """(violations, values in `keys` order or None if unusable, rounding r)."""
    bad = {k: v for k, v in probs.items() if not (is_num(v) and 0 <= v <= 1)}
    if bad:
        k, v = next(iter(bad.items()))
        more = f" (+{len(bad) - 1} more)" if len(bad) > 1 else ""
        return [Violation(req, f"probability of {k!r} is {fmt(v)}, not in [0, 1]{more}", where)], None, 0.0
    if set(probs) != set(keys):
        return [], None, 0.0  # a key mismatch is reported by the *.probability-keys requirement
    values = [float(probs[k]) for k in keys]
    r = spec.rounding(values)
    total = sum(values)
    over, under = spec.eps_sum(values, r)
    if not (_le(total - 1, over) and _le(1 - total, under)):
        bound = over if total > 1 else under
        return [Violation(req, f"probabilities sum to {total:.4f}, not 1 ± {bound:g}", where)], values, r
    return [], values, r


def key_diff(expected: list[str], got: dict) -> tuple[list[str], list[str]]:
    return [o for o in expected if o not in got], [k for k in got if k not in expected]


def _describe_keys(missing: list[str], extra: list[str]) -> str:
    parts = []
    if missing:
        parts.append(f"missing {', '.join(map(repr, missing[:3]))}" + (f" (+{len(missing) - 3})" if len(missing) > 3 else ""))
    if extra:
        parts.append(f"unexpected {', '.join(map(repr, extra[:3]))}" + (f" (+{len(extra) - 3})" if len(extra) > 3 else ""))
    return "; ".join(parts)


def _validate_choice(question: dict, answer: dict, where: str) -> list[Violation]:
    options = list((question.get("criteria") or {}).keys())
    out = [Violation("choice.answer", f"missing {k!r}", where) for k in ("choice", "probabilities", "confidence") if k not in answer]
    probs = answer.get("probabilities")
    values, dv, r = None, [], 0.0
    if "probabilities" in answer and not isinstance(probs, dict):
        out.append(Violation("choice.answer", f"probabilities is {type(probs).__name__}, not an object", where))
    elif isinstance(probs, dict):
        if set(probs) != set(options):
            out.append(Violation("choice.probability-keys", _describe_keys(*key_diff(options, probs)), where, "option-keys"))
        dv, values, r = _distribution("choice.distribution", probs, options, where)
        out += dv
    choice = answer.get("choice")
    if "choice" in answer and not isinstance(choice, str):
        out.append(Violation("choice.answer", f"choice is {type(choice).__name__}, not a string", where))
    elif isinstance(choice, str) and values is not None:
        top = max(values)
        if choice not in options:
            out.append(Violation("choice.argmax", f"choice {choice!r} is not one of the options", where, "not-an-option"))
        elif not _le(top - probs[choice], spec.EPS_ROUND):
            best = options[values.index(top)]
            out.append(Violation("choice.argmax", f"choice is {choice!r} (p={probs[choice]!r}) but {best!r} has p={top!r}", where))
    if "confidence" in answer:
        c = answer.get("confidence")
        if not (is_num(c) and 0 <= c <= 1):
            out.append(Violation("confidence.range", f"confidence is {fmt(c)}, not in [0, 1]", where))
        elif values is not None and not dv:
            n = len(values)
            ref = choice_confidence(values)
            bound = spec.EPS_CONF + (r / (1 - 1 / n) if n > 1 else 0)
            if not _le(abs(c - ref), bound):
                out.append(Violation("confidence.formula", f"confidence is {c:.3f}; the reference formula gives {ref:.3f}", where))
    return out


def _validate_score(question: dict, answer: dict, where: str) -> list[Violation]:
    levels = question.get("criteria") or []
    n = len(levels)
    keys = [str(i) for i in range(n)]
    out = [Violation("score.answer", f"missing {k!r}", where) for k in ("score", "legend", "probabilities", "confidence") if k not in answer]
    legend = answer.get("legend")
    if "legend" in answer:
        if not isinstance(legend, dict):
            out.append(Violation("score.legend", f"legend is {type(legend).__name__}, not an object", where))
        elif sorted(legend, key=_intish) != keys:
            out.append(Violation("score.legend", f"legend keys are {sorted(legend, key=_intish)}, expected {keys}", where))
        else:
            wrong = [k for k in keys if legend[k] != levels[int(k)]]
            if wrong:
                k = wrong[0]
                out.append(Violation("score.legend", f"legend[{k!r}] is {fmt(legend[k])}, the request's level {k} is {fmt(levels[int(k)])}", where))
    probs = answer.get("probabilities")
    values, dv, r = None, [], 0.0
    if "probabilities" in answer and not isinstance(probs, dict):
        out.append(Violation("score.answer", f"probabilities is {type(probs).__name__}, not an object", where))
    elif isinstance(probs, dict):
        if set(probs) != set(keys):
            out.append(Violation("score.probability-keys", f"keys are {sorted(probs, key=_intish)}, expected {keys}", where))
        dv, values, r = _distribution("score.distribution", probs, keys, where)
        out += dv
    score = answer.get("score")
    if "score" in answer and not is_num(score):
        out.append(Violation("score.answer", f"score is {fmt(score)}, not a number", where))
    elif is_num(score) and values is not None and not dv:
        expected = sum(i * p for i, p in enumerate(values))
        if not _le(abs(score - expected), spec.eps_score(n, r)):
            out.append(Violation("score.expectation", f"score is {score!r}; the probabilities give Σ i·p = {expected:.4f}", where))
    if "confidence" in answer:
        c = answer.get("confidence")
        if not (is_num(c) and 0 <= c <= 1):
            out.append(Violation("confidence.range", f"confidence is {fmt(c)}, not in [0, 1]", where))
        elif values is not None and not dv and n > 1:
            top = max(values)
            modes = [i for i, p in enumerate(values) if _le(top - p, spec.EPS_ROUND)]
            refs = [score_confidence(values, k) for k in modes]
            bounds = [spec.EPS_CONF + r * sum(abs(i - k) for i in range(n)) / _uniform_spread(n) for k in modes]
            if not any(_le(abs(c - ref), b) for ref, b in zip(refs, bounds, strict=True)):
                out.append(Violation("confidence.formula", f"confidence is {c:.3f}; the reference formula gives {refs[0]:.3f}", where))
    return out


def _intish(k: Any) -> tuple[int, str]:
    s = str(k)
    return (int(s), s) if s.isdigit() else (1 << 30, s)


# ---------------------------------------------------------------- error responses

def validate_validation_error(resp: Response, where: str = "") -> list[Violation]:
    """A rejection of an invalid body, against errors.validation-shape (and the JSON SHOULDs)."""
    out = check_json(resp, where, error=True)
    if resp.status != 422:
        out.append(Violation("errors.validation-shape", f"status {resp.status}; validation failures use 422", where))
    if not resp.is_json:
        return out
    detail = resp.data.get("detail") if isinstance(resp.data, dict) else None
    ok = isinstance(detail, list) and detail and all(
        isinstance(d, dict) and isinstance(d.get("loc"), list) and d["loc"][:1] == ["body"]
        and isinstance(d.get("msg"), str) and isinstance(d.get("type"), str) for d in detail)
    if not ok:
        out.append(Violation("errors.validation-shape", f"body is not {{\"detail\": [{{\"loc\": [\"body\", …], \"msg\", \"type\"}}]}}: {resp.excerpt(160)}", where))
    return out


def validate_error_shape(resp: Response, req: str = "errors.shape", error_type: str | None = None, where: str = "") -> list[Violation]:
    """A non-validation error body: {"detail": {"error_type": str, "message": str}}."""
    out = check_json(resp, where, error=True)
    if not resp.is_json:
        return out + [Violation(req, f"error body is not JSON: {resp.excerpt(120)!r}", where)]
    detail = resp.data.get("detail") if isinstance(resp.data, dict) else None
    if not (isinstance(detail, dict) and isinstance(detail.get("error_type"), str) and isinstance(detail.get("message"), str)):
        return out + [Violation(req, f"body is not {{\"detail\": {{\"error_type\", \"message\"}}}}: {resp.excerpt(160)}", where)]
    if error_type and detail["error_type"] != error_type:
        out.append(Violation(req, f"error_type is {detail['error_type']!r}, expected {error_type!r}", where))
    return out


# ---------------------------------------------------------------- semantics

def answer_vector(answer: Any) -> dict[str, float]:
    """The numbers an answer commits to, for comparing answers to the same question."""
    if not isinstance(answer, dict):
        return {}
    if answer.get("type") == "noul" and is_num(answer.get("noul")):
        return {"noul": float(answer["noul"])}
    probs = answer.get("probabilities")
    if isinstance(probs, dict):
        return {str(k): float(v) for k, v in probs.items() if is_num(v)}
    return {}


def max_difference(a: Any, b: Any) -> float | None:
    va, vb = answer_vector(a), answer_vector(b)
    if not va or set(va) != set(vb):
        return None
    return max(abs(va[k] - vb[k]) for k in va)
