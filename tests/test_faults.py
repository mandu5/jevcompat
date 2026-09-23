"""Every check can fail, and none fails on correct behaviour.

For each fault the mock can inject, the suite must mark the requirement that fault breaks as
failed. A check that never fails would pass here only by accident, so this is the suite's own
mutation test.
"""
from __future__ import annotations

import pytest
from conftest import run_against

from jevcompat import spec
from jevcompat.mock import FAULTS, MockConfig

AUTH_FAULTS = {"auth-x-api-key", "auth-plain", "auth-invalid-403-text"}


def test_clean_mock_is_conformant():
    rep = run_against()
    assert rep.conformant, [(r.id, r.findings[:1]) for r in rep.results if r.status == "fail"]
    assert rep.count("SHOULD", "fail") == 0


def test_clean_mock_with_key_passes_auth(status):
    rep = run_against(MockConfig(key="secret"), key="secret")
    assert rep.conformant
    for req in ("auth.bearer", "auth.missing", "auth.invalid"):
        assert status(rep, req) == "pass"
    assert status(rep, "auth.ignored-when-off") == "skip"


@pytest.mark.parametrize("noise", [0.05, 0.2])
def test_noisy_mock_is_still_conformant(noise):
    rep = run_against(MockConfig(noise=noise))
    assert rep.conformant, [(r.id, r.findings[:1]) for r in rep.results if r.status == "fail"]
    assert rep.count("SHOULD", "fail") == 0


def test_every_testable_requirement_has_a_fault():
    targeted = {req for req, _ in FAULTS.values()}
    untestable_by_fault = {"dropin.sdk-python"}  # end-to-end: covered by the SDK itself
    assert set(spec.REQUIREMENTS) - targeted == untestable_by_fault


@pytest.mark.parametrize("fault", sorted(FAULTS))
def test_fault_is_detected(fault, status):
    target = FAULTS[fault][0]
    key = "secret" if fault in AUTH_FAULTS else None
    rep = run_against(MockConfig(key=key, faults=frozenset({fault})), key=key)
    assert status(rep, target) == "fail", f"{fault} should break {target}"
    failed = next(r for r in rep.results if r.id == target)
    assert failed.findings and all(f.message for f in failed.findings)


def test_rejected_alias_falls_back_to_a_listed_model(status):
    rep = run_against(MockConfig(faults=frozenset({"reject-jev-latest"})))
    assert status(rep, "request.model-alias") == "fail"
    assert rep.info["model_fallback"] == "mock"
    assert status(rep, "choice.argmax") == "pass"  # the rest of the suite still ran


def test_header_rejection_without_auth_is_worked_around(status):
    rep = run_against(MockConfig(faults=frozenset({"auth-rejects-header"})))
    assert status(rep, "auth.ignored-when-off") == "fail"
    assert status(rep, "choice.argmax") == "pass"


def test_unreachable_server_aborts():
    from jevcompat import runner
    rep = runner.run("http://127.0.0.1:9", sdk=False, timeout=2)
    assert rep.aborted and "cannot reach" in rep.aborted
    assert all(r.status == "skip" for r in rep.results)


def test_sdk_drop_in_detects_what_breaks_the_official_client(status):
    pytest.importorskip("typesafe_sdk")
    clean = run_against(MockConfig(), sdk=True)
    assert status(clean, "dropin.sdk-python") == "pass"
    broken = run_against(MockConfig(faults=frozenset({"float-usage"})), sdk=True)
    assert status(broken, "dropin.sdk-python") == "fail"
