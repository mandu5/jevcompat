"""The requirements of SPEC.md, as data.

Ids, levels and sections must match SPEC.md exactly; tests/test_spec.py parses the document and
fails on any drift, so the report can never cite a requirement the spec does not contain.
"""
from __future__ import annotations

from dataclasses import dataclass

SPEC_VERSION = "0.1"

# Numeric tolerances, SPEC.md §5. r is the rounding the response shows (0 for unrounded values).
EPS_SUM = 0.05
EPS_ROUND = 0.005
EPS_CONF = 0.02
SLACK = 1e-9


def rounding(values: list[float]) -> float:
    """½·10⁻ᵈ for the smallest d in 2..6 at which every value is exact; 0 if none is.

    Never coarser than two decimals (the documented examples' precision): otherwise one-hot or
    saturated answers would look "rounded to 0 decimals" and switch the checks off."""
    for d in range(2, 7):
        if all(abs(v - round(v, d)) < 1e-12 for v in values):
            return 0.5 / 10**d
    return 0.0


def eps_sum(values: list[float], r: float) -> tuple[float, float]:
    """(allowed overshoot, allowed undershoot) of Σp above/below 1. Rounding moves a sum up by at
    most r per value reported as non-zero (a reported 0 was rounded down), and down by at most r
    per value."""
    nonzero = sum(1 for v in values if v > 0)
    return max(EPS_SUM, nonzero * r), max(EPS_SUM, len(values) * r)


def eps_score(n: int, r: float) -> float:
    return 0.02 + r * (1 + n * (n - 1) / 2)


# Semantic comparisons, SPEC.md §7.
SEM_REPEATS = 3           # sends per request per round
SEM_MAX_REPEATS = 9       # more sends before calling a server too noisy
SEM_FLOOR = 0.05
SEM_Z = 4.0               # limit = max(SEM_FLOOR, SEM_Z · pooled sd · √(2/k))
SEM_TOO_NOISY = 0.5

# Busy servers (429/503/529): retry with Retry-After, then call the request inconclusive.
BUSY_ATTEMPTS = 4
BUSY_BUDGET_S = 60.0

MAX_CHOICE_OPTIONS = 255
MAX_SCORE_LEVELS = 10


@dataclass(frozen=True)
class Requirement:
    id: str
    level: str  # "MUST" | "SHOULD"
    section: str
    title: str


_R = [
    ("http.endpoint", "MUST", "1", "POST /v1/systemone answers valid requests with 200"),
    ("http.json", "MUST", "1", "200 bodies are JSON"),
    ("http.content-type", "SHOULD", "1", "responses declare a JSON media type"),
    ("http.models", "SHOULD", "1", "GET /v1/models lists models"),
    ("auth.ignored-when-off", "MUST", "2", "without auth, an Authorization header is accepted"),
    ("auth.bearer", "MUST", "2", "the key is read from Authorization: Bearer"),
    ("auth.missing", "SHOULD", "2", "a missing key gets 401/403 with authentication_error"),
    ("auth.invalid", "SHOULD", "2", "a wrong key gets 401 with authentication_error"),
    ("request.state", "MUST", "3.1", "state may be a string, object or array"),
    ("request.model-alias", "MUST", "3.1", "model \"jev-latest\" is accepted"),
    ("request.multi", "MUST", "3.1", "several questions of mixed types in one request"),
    ("request.question-ids", "MUST", "3.1", "any non-empty string is a question id"),
    ("request.unicode", "MUST", "3.1", "non-ASCII text is accepted and option names round-trip"),
    ("request.unknown-fields", "SHOULD", "3.1", "unknown top-level fields are ignored"),
    ("request.structured-text", "MUST", "3.1", "instructions and descriptions may be objects or arrays"),
    ("noul.criteria", "MUST", "3.2", "noul criteria may be absent, null, two- or one-sided"),
    ("noul.no-instructions", "SHOULD", "3.2", "a noul without instructions is accepted"),
    ("choice.null-description", "MUST", "3.3", "an option description may be null"),
    ("choice.options", "MUST", "3.3", "2 to 255 options are accepted"),
    ("score.levels", "MUST", "3.4", "2 to 10 levels are accepted"),
    ("score.map-rejected", "SHOULD", "3.4", "map-form score criteria are rejected with 4xx"),
    ("response.envelope", "MUST", "4.1", "model, answers and usage are present"),
    ("response.usage", "MUST", "4.1", "token counts are non-negative integers"),
    ("response.answer-ids", "MUST", "4.1", "one answer per question id, none extra"),
    ("response.answer-type", "MUST", "4.1", "each answer's type matches its question"),
    ("response.finite", "MUST", "4.1", "no NaN or Infinity"),
    ("response.extensions", "SHOULD", "4.1", "extra fields are prefixed x_"),
    ("noul.answer", "MUST", "4.2", "noul is a probability in [0, 1]"),
    ("choice.answer", "MUST", "4.3", "choice, probabilities and confidence are present"),
    ("choice.probability-keys", "MUST", "4.3", "probability keys are exactly the option names"),
    ("choice.distribution", "MUST", "4.3", "probabilities are in [0, 1] and sum to 1"),
    ("choice.argmax", "MUST", "4.3", "choice is the most probable option"),
    ("score.answer", "MUST", "4.4", "score, legend, probabilities and confidence are present"),
    ("score.legend", "MUST", "4.4", "legend maps \"0\"..\"n-1\" to the level descriptions"),
    ("score.probability-keys", "MUST", "4.4", "probability keys are \"0\"..\"n-1\""),
    ("score.distribution", "MUST", "4.4", "probabilities are in [0, 1] and sum to 1"),
    ("score.expectation", "MUST", "4.4", "score is the expectation of the probabilities"),
    ("confidence.range", "MUST", "4.5", "confidence is in [0, 1]"),
    ("confidence.formula", "SHOULD", "4.5", "confidence follows the reference formula"),
    ("errors.json", "SHOULD", "6", "error bodies are JSON"),
    ("errors.no-5xx", "MUST", "6", "bad requests never get a 5xx"),
    ("errors.reject-invalid", "SHOULD", "6", "invalid requests get a 4xx, not an answer"),
    ("errors.validation-shape", "SHOULD", "6", "validation errors are 422 with detail[]"),
    ("errors.shape", "SHOULD", "6", "other errors carry detail.error_type and detail.message"),
    ("semantics.question-id", "MUST", "7", "renaming a question id does not change its answer"),
    ("semantics.batching", "SHOULD", "7", "other questions in the request do not change an answer"),
    ("semantics.question-order", "SHOULD", "7", "question order does not change answers"),
    ("dropin.sdk-python", "MUST", "8", "the official Python SDK parses every answer type"),
]

REQUIREMENTS: dict[str, Requirement] = {rid: Requirement(rid, lvl, sec, title) for rid, lvl, sec, title in _R}

SECTIONS = {
    "1": "Transport",
    "2": "Authentication",
    "3.1": "Request",
    "3.2": "Noul",
    "3.3": "Choice",
    "3.4": "Score",
    "4.1": "Response envelope",
    "4.2": "Noul answer",
    "4.3": "Choice answer",
    "4.4": "Score answer",
    "4.5": "Confidence",
    "6": "Errors",
    "7": "Semantics",
    "8": "Drop-in",
}
