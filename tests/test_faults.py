"""Every check can fail, and none fails on correct behaviour.

For each fault the mock can inject, the suite must mark the requirement that fault breaks as
failed. A check that never fails would pass here only by accident, so this is the suite's own
mutation test.
"""
from __future__ import annotations

import pytest
from conftest import run_against, status_of

from jevcompat import spec
from jevcompat.mock import FAULTS, MockConfig

AUTH_FAULTS = {"auth-x-api-key", "auth-plain", "auth-invalid-403-text"}


def failures(rep):
    return [(r.id, r.findings[0].message) for r in rep.results if r.status == "fail"]


def test_clean_mock_is_conformant():
    rep = run_against(sdk=True)
    assert rep.verdict == "conformant", failures(rep)
    assert rep.count("SHOULD", "fail") == 0 and rep.count("SHOULD", "skip") == 2  # auth.missing/invalid need --key


def test_clean_mock_with_key_passes_auth():
    rep = run_against(MockConfig(key="secret"), key="secret", sdk=True)
    assert rep.verdict == "conformant", failures(rep)
    for req in ("auth.bearer", "auth.missing", "auth.invalid"):
        assert status_of(rep, req) == "pass"
    assert status_of(rep, "auth.ignored-when-off") == "skip"


def test_without_sdk_the_run_is_incomplete_not_conformant():
    rep = run_against()
    assert rep.verdict == "incomplete" and rep.untested_musts == ["dropin.sdk-python"]


def test_every_testable_requirement_has_a_fault():
    assert set(spec.REQUIREMENTS) - {req for req, _ in FAULTS.values()} == {"dropin.sdk-python"}


@pytest.mark.parametrize("fault", sorted(FAULTS))
def test_fault_is_detected(fault):
    target = FAULTS[fault][0]
    key = "secret" if fault in AUTH_FAULTS else None
    rep = run_against(MockConfig(key=key, faults=frozenset({fault})), key=key)
    assert status_of(rep, target) == "fail", f"{fault} should break {target}"
    failed = next(r for r in rep.results if r.id == target)
    assert failed.findings and all(f.message for f in failed.findings)


# Faults whose one defect legitimately shows under more than one requirement.
KNOWN_SPILLOVER = {
    "wrong-route": None,          # nothing else can be tested
    "xssi-200": None,             # no response parses
    "first-question-only": {"response.answer-ids", "semantics.batching", "semantics.question-id", "semantics.question-order"},
    "no-usage": set(), "float-usage": set(),
}


@pytest.mark.parametrize("fault", sorted(FAULTS))
def test_one_defect_fails_few_musts(fault):
    """A single fault must not smear MUST failures across unrelated requirements."""
    if fault in KNOWN_SPILLOVER and KNOWN_SPILLOVER[fault] is None:
        pytest.skip("the fault makes the rest untestable")
    key = "secret" if fault in AUTH_FAULTS else None
    rep = run_against(MockConfig(key=key, faults=frozenset({fault})), key=key)
    target = FAULTS[fault][0]
    allowed = {target} | (KNOWN_SPILLOVER.get(fault) or set())
    extra = [(r.id, r.findings[0].message) for r in rep.results
             if r.status == "fail" and r.level == "MUST" and r.id not in allowed]
    assert not extra, extra


def test_rejected_alias_falls_back_to_a_listed_model():
    rep = run_against(MockConfig(faults=frozenset({"reject-jev-latest"})))
    assert status_of(rep, "request.model-alias") == "fail"
    assert rep.info["model_fallback"] == "mock"
    assert status_of(rep, "choice.argmax") == "pass"


def test_header_rejection_without_auth_is_worked_around():
    rep = run_against(MockConfig(faults=frozenset({"auth-rejects-header"})))
    assert status_of(rep, "auth.ignored-when-off") == "fail"
    assert status_of(rep, "choice.argmax") == "pass"


def test_key_given_to_a_server_without_auth_skips_the_auth_shoulds():
    rep = run_against(MockConfig(), key="whatever", sdk=True)
    assert status_of(rep, "auth.missing") == "skip" and status_of(rep, "auth.invalid") == "skip"
    assert rep.verdict == "conformant"


def test_unreachable_server_is_not_tested():
    from jevcompat import runner
    rep = runner.run("http://127.0.0.1:9", sdk=False, timeout=2)
    assert rep.verdict == "not tested" and "cannot reach" in rep.aborted
    assert all(r.status == "skip" for r in rep.results)


def test_sdk_drop_in_detects_what_breaks_the_official_client():
    assert status_of(run_against(MockConfig(faults=frozenset({"float-usage"})), sdk=True), "dropin.sdk-python") == "fail"


def test_rate_limiting_is_not_a_finding():
    rep = run_against(MockConfig(busy_every=3), sdk=True)
    assert rep.verdict == "conformant", failures(rep)


def test_every_case_runs_against_a_conformant_server():
    """No case may be skipped by its own gating on a server that supports everything: a case that
    never runs is a check that can never fail."""
    from jevcompat.checks import CASES
    rep = run_against(MockConfig(key="k"), key="k", sdk=True)
    ran = {x.case.split(":")[0].rstrip("+") for x in rep.exchanges}
    ran = {c.replace("-confirm", "").replace("semantics-baseline", "") for c in ran}
    missing = [c.name for c in CASES if c.name not in ran and c.name != "model-alias"]  # model-alias rides on the preflight
    assert not missing, missing
    assert not [r.id for r in rep.results if r.status == "skip" and r.id != "auth.ignored-when-off"]
