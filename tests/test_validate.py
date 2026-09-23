from __future__ import annotations

import pytest

from jevcompat.client import Response, parse_json
from jevcompat.validate import (
    choice_confidence,
    max_difference,
    score_confidence,
    validate_error_shape,
    validate_success,
    validate_validation_error,
)


def resp(data, status=200, raw: bytes | None = None, ctype="application/json"):
    import json
    body = raw if raw is not None else json.dumps(data).encode()
    value, err, nonfinite = parse_json(body)
    return Response(status, {"content-type": ctype}, body, 1.0, value, err, nonfinite)


# The documentation's worked examples (docs.typesafe.ai/confidence, /introduction/quickstart, /api).
@pytest.mark.parametrize("probs, shown", [([0.85, 0.0, 0.15], 0.78), ([0.88, 0.12, 0.0], 0.81)])
def test_choice_formula_reproduces_documented_examples(probs, shown):
    assert abs(choice_confidence(probs) - shown) <= 0.02


@pytest.mark.parametrize("probs, shown", [([0, 0.57, 0.43], 0.35), ([0, 0.89, 0.11], 0.84), ([0, 0.95, 0.05], 0.92)])
def test_score_formula_reproduces_documented_examples(probs, shown):
    assert abs(score_confidence(probs) - shown) <= 0.02


def test_confidence_extremes():
    assert choice_confidence([1, 0, 0]) == 1 and abs(choice_confidence([1 / 3] * 3)) < 1e-12
    assert score_confidence([0, 1, 0]) == 1 and score_confidence([0.5, 0, 0.5]) == 0
    assert choice_confidence([1.0]) == 1 and score_confidence([1.0]) == 1


REQ = {"questions": {
    "n": {"type": "noul", "instructions": "?"},
    "c": {"type": "choice", "criteria": {"A": None, "B": None}},
    "s": {"type": "score", "criteria": ["lo", "mid", "hi"]},
}}
GOOD = {"model": "m", "usage": {"input_tokens": 3, "output_tokens": 0}, "answers": {
    "n": {"type": "noul", "noul": 0.9},
    "c": {"type": "choice", "choice": "A", "probabilities": {"A": 0.88, "B": 0.12}, "confidence": 0.76},
    "s": {"type": "score", "score": 1.05, "legend": {"0": "lo", "1": "mid", "2": "hi"},
          "probabilities": {"0": 0.0, "1": 0.95, "2": 0.05}, "confidence": 0.925},
}}


def reqs(violations):
    return sorted({v.req for v in violations})


def test_documented_shape_passes():
    assert validate_success(REQ, resp(GOOD)) == []


def mutate(path, value):
    import copy
    data = copy.deepcopy(GOOD)
    node = data
    for k in path[:-1]:
        node = node[k]
    if value is KeyError:
        del node[path[-1]]
    else:
        node[path[-1]] = value
    return data


@pytest.mark.parametrize("path, value, expected", [
    (["usage", "input_tokens"], 3.0, "response.usage"),
    (["usage", "output_tokens"], -1, "response.usage"),
    (["usage"], KeyError, "response.envelope"),
    (["x_latency"], 3, None),
    (["latency_ms"], 3, "response.extensions"),
    (["answers", "n", "confidence"], 0.8, "response.extensions"),
    (["answers", "n", "noul"], 1.01, "noul.answer"),
    (["answers", "n", "noul"], True, "noul.answer"),
    (["answers", "n", "type"], "boolean", "response.answer-type"),
    (["answers", "c", "choice"], "B", "choice.argmax"),
    (["answers", "c", "choice"], "Z", "choice.argmax"),
    (["answers", "c", "probabilities"], {"a": 0.88, "B": 0.12}, "choice.probability-keys"),
    (["answers", "c", "probabilities"], {"A": 0.93, "B": 0.21}, "choice.distribution"),
    (["answers", "c", "probabilities"], {"A": 0.9, "B": 0.2}, "choice.distribution"),  # two-decimal r: 1.1 is too far
    (["answers", "c", "probabilities"], {"A": 1, "B": 1}, "choice.distribution"),  # independent sigmoids
    (["answers", "c", "probabilities"], {"A": 0.88, "B": 0.1}, None),  # sum 0.98: within ε_sum
    (["answers", "c", "probabilities"], {"A": 0.885, "B": 0.125}, None),  # within ε_sum
    (["answers", "c", "confidence"], 0.88, "confidence.formula"),
    (["answers", "c", "confidence"], 1.2, "confidence.range"),
    (["answers", "c", "confidence"], KeyError, "choice.answer"),
    (["answers", "s", "score"], 1.0, "score.expectation"),
    (["answers", "s", "score"], 1.085, None),  # within ε_score for 3 two-decimal levels (0.04)
    (["answers", "s", "legend"], {"1": "lo", "2": "mid", "3": "hi"}, "score.legend"),
    (["answers", "s", "legend"], {"0": "lo", "1": "MID", "2": "hi"}, "score.legend"),
    (["answers", "s", "probabilities"], {"1": 0.0, "2": 0.95, "3": 0.05}, "score.probability-keys"),
    (["answers", "extra"], {"type": "noul", "noul": 0.5}, "response.answer-ids"),
])
def test_each_violation_is_attributed(path, value, expected):
    got = reqs(validate_success(REQ, resp(mutate(path, value))))
    assert got == ([expected] if expected else [])


def test_missing_answer():
    data = mutate(["answers", "s"], KeyError)
    assert reqs(validate_success(REQ, resp(data))) == ["response.answer-ids"]


def test_hard_labels_are_still_checked():
    one_hot = {"type": "score", "score": 2.0, "legend": {"0": "lo", "1": "mid", "2": "hi"},
               "probabilities": {"0": 0, "1": 1, "2": 0}, "confidence": 1.0}
    assert reqs(validate_success(REQ, resp(mutate(["answers", "s"], one_hot)))) == ["score.expectation"]


def test_nan_is_caught_although_python_json_accepts_it():
    raw = b'{"model": "m", "usage": {"input_tokens": 1, "output_tokens": 1}, "answers": {"n": {"type": "noul", "noul": NaN}}}'
    r = resp(None, raw=raw)
    got = reqs(validate_success({"questions": {"n": {"type": "noul"}}}, r))
    assert "response.finite" in got and "noul.answer" in got


def test_not_json():
    r = resp(None, raw=b"Internal Server Error", ctype="text/plain")
    assert reqs(validate_success(REQ, r)) == ["http.content-type", "http.json"]


def test_content_type_is_a_should_and_accepts_plus_json():
    assert reqs(validate_success(REQ, resp(GOOD, ctype="text/plain"))) == ["http.content-type"]
    assert validate_success(REQ, resp(GOOD, ctype="application/json; charset=utf-8")) == []
    assert validate_success(REQ, resp(GOOD, ctype="application/vnd.jev+json")) == []


def test_exact_boundaries_pass():
    import copy
    data = copy.deepcopy(GOOD)
    data["answers"]["c"] = {"type": "choice", "choice": "A", "probabilities": {"A": 0.55, "B": 0.5}, "confidence": 0.1}
    assert "choice.distribution" not in reqs(validate_success(REQ, resp(data)))


def _rounded(values, d=2):
    return [round(v, d) for v in values]


def test_two_decimal_rounding_is_allowed_for_many_options():
    import math
    import random
    rng = random.Random(3)
    for n in (64, 255):
        logits = [rng.gauss(0, 2) for _ in range(n)]
        m = max(logits)
        ex = [math.exp(x - m) for x in logits]
        p = _rounded([e / sum(ex) for e in ex])
        names = [f"o{i}" for i in range(n)]
        best = names[max(range(n), key=lambda i: p[i])]
        req = {"questions": {"c": {"type": "choice", "criteria": {k: None for k in names}}}}
        body = {"model": "m", "usage": {"input_tokens": 1, "output_tokens": 1}, "answers": {"c": {
            "type": "choice", "choice": best, "probabilities": dict(zip(names, p, strict=True)),
            "confidence": round((max(p) - 1 / n) / (1 - 1 / n), 2)}}}
        assert validate_success(req, resp(body)) == []


def test_two_decimal_rounding_is_allowed_for_ten_levels():
    import random
    rng = random.Random(5)
    for _ in range(200):
        raw = [rng.random() for _ in range(10)]
        exact = [x / sum(raw) for x in raw]
        p = _rounded(exact)
        score = round(sum(i * q for i, q in enumerate(exact)), 2)
        req = {"questions": {"s": {"type": "score", "criteria": [str(i) for i in range(10)]}}}
        from jevcompat.validate import score_confidence
        body = {"model": "m", "usage": {"input_tokens": 1, "output_tokens": 1}, "answers": {"s": {
            "type": "score", "score": score, "legend": {str(i): str(i) for i in range(10)},
            "probabilities": {str(i): q for i, q in enumerate(p)}, "confidence": round(score_confidence(exact), 2)}}}
        assert validate_success(req, resp(body)) == [], p


def test_validation_error_shapes():
    ok = resp({"detail": [{"loc": ["body", "state"], "msg": "Field required", "type": "missing"}]}, status=422)
    assert validate_validation_error(ok) == []
    assert reqs(validate_validation_error(resp({"error": "bad"}, status=400))) == ["errors.validation-shape"]
    assert reqs(validate_validation_error(resp({"detail": "bad"}, status=422))) == ["errors.validation-shape"]


def test_error_shape():
    ok = resp({"detail": {"error_type": "authentication_error", "message": "no"}}, status=401)
    assert validate_error_shape(ok, "auth.missing", "authentication_error") == []
    wrong_type = resp({"detail": {"error_type": "auth", "message": "no"}}, status=401)
    assert reqs(validate_error_shape(wrong_type, "auth.missing", "authentication_error")) == ["auth.missing"]
    text = resp(None, status=401, raw=b"Unauthorized", ctype="text/plain")
    assert reqs(validate_error_shape(text, "auth.missing")) == ["auth.missing", "errors.json", "http.content-type"]


def test_max_difference():
    a = {"type": "choice", "probabilities": {"A": 0.6, "B": 0.4}}
    b = {"type": "choice", "probabilities": {"A": 0.5, "B": 0.5}}
    assert abs(max_difference(a, b) - 0.1) < 1e-9
    assert max_difference({"type": "noul", "noul": 0.2}, {"type": "noul", "noul": 0.25}) == pytest.approx(0.05)
    assert max_difference(a, {"type": "choice", "probabilities": {"A": 1.0}}) is None
