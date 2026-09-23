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
    assert "| `ε_sum` | above 1: max(0.05, k·r); below 1: max(0.05, n·r) |" in text and spec.EPS_SUM == 0.05
    assert f"| `ε_round` | {spec.EPS_ROUND} |" in text
    assert "| `ε_score` | 0.02 + r·(1 + n(n−1)/2) |" in text
    assert spec.eps_sum([0.2, 0.3, 0.5], 0.0) == (0.05, 0.05)
    assert abs(spec.eps_score(10, 0.005) - (0.02 + 0.005 * 46)) < 1e-12


def test_rounding_detection():
    assert spec.rounding([0.88, 0.12]) == 0.005
    assert spec.rounding([0.5, 0.5]) == 0.005  # never coarser than two decimals
    assert spec.rounding([1.0, 0.0]) == 0.005
    assert spec.rounding([0.1234, 0.8766]) == 0.00005
    assert spec.rounding([0.123456789, 0.876543211]) == 0.0
    assert spec.rounding([1 - 4e-7, 4e-7, 1e-12]) == 0.0  # saturated, not rounded


def test_sum_bound_is_asymmetric():
    over, under = spec.eps_sum([1.0, 1.0] + [0.0] * 253, 0.005)
    assert over == 0.05 and abs(under - 1.275) < 1e-12


def test_float32_rounding_counts_as_rounding():
    import struct
    f32 = [struct.unpack("f", struct.pack("f", v))[0] for v in (0.9, 0.07, 0.03)]
    assert f32[0] != 0.9 and spec.rounding(f32) == 0.005
