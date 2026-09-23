from __future__ import annotations

import json

import pytest

from jevcompat import cli
from jevcompat.mock import MockConfig, Running


def test_conformant_server_exits_0(tmp_path, capsys):
    out = tmp_path / "r.json"
    md = tmp_path / "r.md"
    with Running() as m:
        code = cli.main(["test", m.url, "--no-sdk", "--json", str(out), "--markdown", str(md), "--badge"])
    assert code == 0
    data = json.loads(out.read_text())
    assert data["summary"]["conformant"] is True
    assert "img.shields.io/badge/jevcompat" in capsys.readouterr().out
    assert "| ✓ | MUST |" in md.read_text()


def test_nonconformant_server_exits_1(tmp_path):
    md = tmp_path / "r.md"
    with Running(MockConfig(faults=frozenset({"choice-second"}))) as m:
        code = cli.main(["test", m.url, "--no-sdk", "--markdown", str(md)])
    assert code == 1
    text = md.read_text()
    assert "### `choice.argmax` (MUST)" in text and "<details>" in text


def test_unreachable_exits_2():
    assert cli.main(["test", "http://127.0.0.1:9", "--no-sdk", "--timeout", "2"]) == 2


def test_key_from_environment(monkeypatch):
    monkeypatch.setenv("MY_KEY", "s3")
    with Running(MockConfig(key="s3")) as m:
        assert cli.main(["test", m.url, "--no-sdk", "--key-env", "MY_KEY"]) == 0


def test_spec_and_faults_listing(capsys):
    assert cli.main(["spec"]) == 0
    assert "choice.argmax" in capsys.readouterr().out
    assert cli.main(["mock", "--list-faults"]) == 0
    assert "choice-second" in capsys.readouterr().out


def test_unknown_fault_is_a_usage_error():
    with pytest.raises(ValueError):
        MockConfig(faults=frozenset({"nope"}))
