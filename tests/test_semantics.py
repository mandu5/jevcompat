"""The semantic checks are statistics; test them as statistics, over many seeds."""
from __future__ import annotations

import random

import pytest
from conftest import run_against, status_of

from jevcompat.mock import MockConfig

SEM = {"semantics-question-id", "semantics-batching", "semantics-question-order"}
REQS = ("semantics.question-id", "semantics.batching", "semantics.question-order")


@pytest.mark.parametrize("noise", [0.1, 0.3, 0.6])
def test_no_false_positives_on_a_correct_noisy_server(noise):
    fails = 0
    for seed in range(25):
        rep = run_against(MockConfig(noise=noise, rng=random.Random(seed)), only=SEM)
        fails += sum(status_of(rep, r) == "fail" for r in REQS)
    assert fails == 0


@pytest.mark.parametrize("fault, req", [("id-leaks", "semantics.question-id"), ("batch-leaks", "semantics.batching"),
                                        ("order-leaks", "semantics.question-order")])
def test_leaks_are_found_through_moderate_noise(fault, req):
    found = judged = 0
    for seed in range(20):
        rep = run_against(MockConfig(noise=0.1, faults=frozenset({fault}), rng=random.Random(seed)), only=SEM)
        st = status_of(rep, req)
        judged += st != "skip"
        found += st == "fail"
    assert judged == 20 and found >= 19


def test_a_very_noisy_server_is_not_judged():
    rep = run_against(MockConfig(noise=4.0, rng=random.Random(1)), only=SEM)
    assert all(status_of(rep, r) == "skip" for r in REQS)
    assert "too noisy" in next(r for r in rep.results if r.id == "semantics.batching").reason


def test_a_cache_cannot_hide_noise():
    """With unknown fields accepted, every semantic request carries a distinct x_nonce."""
    rep = run_against(MockConfig(noise=0.2), only=SEM | {"unknown-fields"})
    bodies = [x.request for x in rep.exchanges if isinstance(x.request, dict) and x.case.startswith("semantics")]
    nonces = [b.get("x_nonce") for b in bodies]
    assert all(nonces) and len(set(nonces)) == len(nonces)
