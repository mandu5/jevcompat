"""The proxy fixes every fault that can be fixed without inventing an answer, and no others."""
from __future__ import annotations

import pytest

from jevcompat import proxy, runner
from jevcompat.mock import FAULTS, MockConfig
from jevcompat.mock import Running as Mock

UNFIXABLE = {
    "reject-array-state", "string-only-text", "noul-two-sided", "noul-needs-instructions",
    "no-null-description", "cap-64", "cap-5-levels", "noul-range", "xssi-200",
}
# How an operator would configure the proxy for an upstream with this fault.
CONFIG = {
    "reject-jev-latest": {"upstream_model": "mock"},
    "wrong-route": {"upstream_path": "/v1/evaluate"},
    "auth-x-api-key": {"upstream_key": "up", "upstream_key_header": "x-api-key"},
    "first-question-only": {"split": True},
    "batch-leaks": {"split": True},
    "choice-sum": {"renormalize": True},
    "score-sum": {"renormalize": True},
}
UPSTREAM_KEY = {"auth-x-api-key", "auth-plain", "auth-invalid-403-text"}


def through_proxy(fault: str | None, **extra):
    faults = frozenset({fault}) if fault else frozenset()
    mock_key = "up" if fault in UPSTREAM_KEY else None
    cfg = {"upstream_key": mock_key, **CONFIG.get(fault or "", {}), **extra}
    client_key = "client" if fault in UPSTREAM_KEY else None
    with Mock(MockConfig(key=mock_key, faults=faults)) as m, \
            proxy.Running(proxy.ProxyConfig(upstream=m.url, key=client_key, timeout=10, **cfg)) as p:
        return runner.run(p.url, key=client_key, sdk=True, timeout=10)


def test_proxy_over_clean_mock_is_conformant():
    rep = through_proxy(None)
    assert rep.verdict == "conformant" and rep.count("SHOULD", "fail") == 0


@pytest.mark.parametrize("fault", sorted(set(FAULTS) - UNFIXABLE))
def test_proxy_fixes(fault):
    rep = through_proxy(fault)
    bad = [(r.id, r.findings[0].message) for r in rep.results if r.status == "fail"]
    assert rep.verdict == "conformant" and not bad, bad


@pytest.mark.parametrize("fault", sorted(UNFIXABLE))
def test_proxy_does_not_hide(fault):
    rep = through_proxy(fault)
    target = next(r for r in rep.results if r.id == FAULTS[fault][0])
    assert rep.aborted or target.status == "fail"


def test_canonical_ids_do_not_depend_on_other_questions():
    a = {"a": {"type": "noul", "instructions": "x"}}
    b = {**a, "zzz": {"type": "noul", "instructions": "added"}}
    assert dict(proxy.canonical_ids(a))["a"] == dict(proxy.canonical_ids(b))["a"]


def _answer(question, upstream):
    return proxy.normalise_answer(question, upstream, set())


def test_option_matching_is_one_to_one():
    q = {"type": "choice", "criteria": {"Apple": None, "apple": None}}
    with pytest.raises(proxy.UpstreamError):
        _answer(q, {"type": "choice", "probabilities": {"Apple": 0.9}})
    with pytest.raises(proxy.UpstreamError):  # two names that normalise alike, one fuzzy key
        _answer({"type": "choice", "criteria": {"Yes": None, "Yes ": None}}, {"type": "choice", "probabilities": {"yes": 1.0}})
    ok = _answer({"type": "choice", "criteria": {"Café": None, "Tea": None}},
                 {"type": "choice", "probabilities": {"cafe\u0301": 0.7, "tea": 0.3}})
    assert ok["choice"] == "Café" and set(ok["probabilities"]) == {"Café", "Tea"}


def test_mass_on_unasked_options_is_refused():
    with pytest.raises(proxy.UpstreamError, match="not asked"):
        _answer({"type": "choice", "criteria": {"A": None, "B": None}}, {"type": "choice", "probabilities": {"A": 0.3, "B": 0.1, "Other": 0.6}})


def test_renormalisation_is_bounded_unless_asked():
    q = {"type": "choice", "criteria": {"A": None, "B": None, "C": None}}
    sigmoids = {"type": "choice", "probabilities": {"A": 0.95, "B": 0.9, "C": 0.1}}
    with pytest.raises(proxy.UpstreamError, match="renormalize"):
        _answer(q, sigmoids)
    assert abs(sum(proxy.normalise_answer(q, sigmoids, set(), any_sum=True)["probabilities"].values()) - 1) < 1e-9


def test_nested_nan_is_refused():
    from jevcompat.client import Client
    from jevcompat.mock import Running as M
    class NanMock(MockConfig):
        pass
    with M(MockConfig()) as m, proxy.Running(proxy.ProxyConfig(upstream=m.url)) as p:
        # patch the upstream call to add a nested NaN in an extra field
        orig = proxy.Proxy._upstream
        def with_nan(self, payload):
            data = orig(self, payload)
            data["debug"] = {"logit": float("nan")}
            return data
        proxy.Proxy._upstream = with_nan
        try:
            r = Client(p.url).ask({"q": {"type": "noul", "instructions": "?"}})
        finally:
            proxy.Proxy._upstream = orig
    assert r.status == 502 and "NaN" in r.body.decode()


def test_canonical_ids_ignore_names_and_order():
    q1 = {"a": {"type": "noul", "instructions": "x"}, "b": {"type": "noul", "instructions": "y"}}
    q2 = {"zz": {"type": "noul", "instructions": "y"}, "yy": {"type": "noul", "instructions": "x"}}
    m1 = {up: q1[cid] for cid, up in proxy.canonical_ids(q1)}
    m2 = {up: q2[cid] for cid, up in proxy.canonical_ids(q2)}
    assert m1 == m2 and [up for _, up in proxy.canonical_ids(q1)] == [up for _, up in proxy.canonical_ids(q2)]


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
