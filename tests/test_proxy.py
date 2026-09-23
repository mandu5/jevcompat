"""The proxy fixes every fault that can be fixed without inventing an answer, and no others."""
from __future__ import annotations

import pytest

from jevcompat import proxy, runner
from jevcompat.mock import FAULTS, MockConfig
from jevcompat.mock import Running as Mock

UNFIXABLE = {
    "reject-array-state", "string-only-text", "noul-two-sided", "noul-needs-instructions",
    "no-null-description", "cap-64", "cap-5-levels", "noul-range",
}
# How an operator would configure the proxy for an upstream with this fault.
CONFIG = {
    "reject-jev-latest": {"upstream_model": "mock"},
    "wrong-route": {"upstream_path": "/v1/evaluate"},
    "auth-x-api-key": {"upstream_key": "up", "upstream_key_header": "x-api-key"},
    "first-question-only": {"split": True},
    "batch-leaks": {"split": True},
}
UPSTREAM_KEY = {"auth-x-api-key", "auth-plain", "auth-invalid-403-text"}


def through_proxy(fault: str | None, **extra):
    faults = frozenset({fault}) if fault else frozenset()
    mock_key = "up" if fault in UPSTREAM_KEY else None
    cfg = {"upstream_key": mock_key, **CONFIG.get(fault or "", {}), **extra}
    client_key = "client" if fault in UPSTREAM_KEY else None
    with Mock(MockConfig(key=mock_key, faults=faults)) as m, \
            proxy.Running(proxy.ProxyConfig(upstream=m.url, key=client_key, timeout=10, **cfg)) as p:
        return runner.run(p.url, key=client_key, sdk=False, timeout=10)


def test_proxy_over_clean_mock_is_conformant():
    rep = through_proxy(None)
    assert rep.conformant and rep.count("SHOULD", "fail") == 0


@pytest.mark.parametrize("fault", sorted(set(FAULTS) - UNFIXABLE))
def test_proxy_fixes(fault):
    rep = through_proxy(fault)
    bad = [(r.id, r.findings[0].message) for r in rep.results if r.status == "fail"]
    assert rep.conformant and not bad, bad


@pytest.mark.parametrize("fault", sorted(UNFIXABLE))
def test_proxy_does_not_hide(fault):
    rep = through_proxy(fault)
    target = next(r for r in rep.results if r.id == FAULTS[fault][0])
    assert rep.aborted or target.status == "fail"


def test_canonical_ids_ignore_names_and_order():
    q1 = {"a": {"type": "noul", "instructions": "x"}, "b": {"type": "noul", "instructions": "y"}}
    q2 = {"zz": {"type": "noul", "instructions": "y"}, "yy": {"type": "noul", "instructions": "x"}}
    m1 = {proxy.canonical_ids(q1)[i][1]: q1[proxy.canonical_ids(q1)[i][0]] for i in range(2)}
    m2 = {proxy.canonical_ids(q2)[i][1]: q2[proxy.canonical_ids(q2)[i][0]] for i in range(2)}
    assert m1 == m2


def test_fixes_header_reports_changes():
    import json

    from jevcompat.client import Client
    with Mock(MockConfig(faults=frozenset({"legend-1-based", "confidence-margin"}))) as m, \
            proxy.Running(proxy.ProxyConfig(upstream=m.url)) as p:
        r = Client(p.url).ask({"s": {"type": "score", "instructions": "?", "criteria": ["a", "b", "c"]},
                              "c": {"type": "choice", "instructions": "?", "criteria": {"A": None, "B": None, "C": None}}})
    assert r.status == 200
    assert set(r.headers["x-jevcompat-fixes"].split(",")) >= {"legend", "confidence"}
    assert json.loads(r.body)["answers"]["s"]["legend"] == {"0": "a", "1": "b", "2": "c"}
