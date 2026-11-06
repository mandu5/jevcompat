"""Package the existing recorded reports for the static documentation page.

This copies committed evidence; it never starts a server or runs conformance checks.
Run with --check to verify that the checked-in site snapshot is current.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVERS = ["kev", "decider", "von", "rizzo-flow", "open-jev", "laya", "jeff", "simple-jev"]


def snapshot() -> str:
    sources = {}
    reports = []
    for server in SERVERS:
        name = f"results/{server}/report.json"
        raw = (ROOT / name).read_bytes()
        sources[name] = hashlib.sha256(raw).hexdigest()
        reports.append({"server": server, "report": json.loads(raw)})
    spec = (ROOT / "SPEC.md").read_bytes()
    sources["SPEC.md"] = hashlib.sha256(spec).hexdigest()
    requirements = {
        match[0]: match[1].strip()
        for match in re.findall(
            r'<a id="([^"]+)"></a>(.*?)(?=\n<a id=|\n#{1,6} |\Z)', spec.decode(), re.S
        )
    }
    return json.dumps(
        {"sources": sources, "requirements": requirements, "reports": reports},
        ensure_ascii=False,
        separators=(",", ":"),
    ) + "\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    target = ROOT / "docs/assets/recorded-runs.json"
    expected = snapshot()
    if args.check:
        if not target.exists() or target.read_text() != expected:
            raise SystemExit("Site evidence is stale. Run python3 docs/build_site.py")
        print("Site evidence matches all 8 recorded reports and SPEC.md.")
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(expected)
        print(f"Wrote {target.relative_to(ROOT)} from recorded artifacts.")
