"""SPEC.md and spec.py must describe the same requirements."""
from __future__ import annotations

import re
from pathlib import Path

from jevcompat import spec

SPEC = Path(__file__).resolve().parents[1] / "SPEC.md"


def parsed() -> list[tuple[str, str, str]]:
    text = SPEC.read_text(encoding="utf-8")
    out, section = [], None
    for line in text.splitlines():
        m = re.match(r"^#{2,3} (\d+(?:\.\d+)?)\.? ", line)
        if m:
            section = m.group(1)
        m = re.match(r"^\*\*([a-z0-9.-]+)\*\* — (MUST|SHOULD)\.", line)
        if m:
            out.append((m.group(1), m.group(2), section))
    return out


def test_ids_and_levels_match():
    doc = {rid: lvl for rid, lvl, _ in parsed()}
    code = {r.id: r.level for r in spec.REQUIREMENTS.values()}
    assert doc == code


def test_sections_match():
    for rid, _, section in parsed():
        assert spec.REQUIREMENTS[rid].section == section, rid


def test_ids_are_unique_in_the_document():
    ids = [rid for rid, _, _ in parsed()]
    assert len(ids) == len(set(ids))


def test_version_matches_title():
    assert f"specification {spec.SPEC_VERSION}" in SPEC.read_text(encoding="utf-8").splitlines()[0]


def test_tolerances_match_the_table():
    text = SPEC.read_text(encoding="utf-8")
    assert "| `ε_sum` | max(0.05, n·r) |" in text and spec.EPS_SUM == 0.05
    assert f"| `ε_round` | {spec.EPS_ROUND} |" in text
    assert "| `ε_score` | 0.02 + r·(1 + n(n−1)/2) |" in text
    assert abs(spec.eps_sum(255, 0.005) - 1.275) < 1e-12 and spec.eps_sum(3, 0.0) == 0.05
    assert abs(spec.eps_score(10, 0.005) - (0.02 + 0.005 * 46)) < 1e-12


def test_rounding_detection():
    assert spec.rounding([0.88, 0.12]) == 0.005
    assert spec.rounding([0.5, 0.5]) == 0.05
    assert spec.rounding([1.0, 0.0]) == 0.5
    assert spec.rounding([0.123456789, 0.876543211]) == 0.0
