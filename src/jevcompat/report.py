"""Render a Report: terminal, JSON, Markdown and a README badge."""
from __future__ import annotations

import json
import urllib.parse
from dataclasses import asdict
from typing import Any

from . import spec
from .runner import Report, RequirementResult

SPEC_URL = "https://github.com/mandu5/jevcompat/blob/main/SPEC.md"
MARK = {"pass": "✓", "fail": "✗", "skip": "–"}


def _c(text: str, code: str, color: bool) -> str:
    return f"\033[{code}m{text}\033[0m" if color else text


def _clip(v: Any, n: int = 300) -> str:
    s = v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)
    return s if len(s) <= n else s[:n] + f"… ({len(s)} chars)"


def verdict(report: Report) -> str:
    s = report.summary()
    must, should = s["MUST"], s["SHOULD"]
    head = "conformant" if report.conformant else "not conformant"
    return (f"{head} to spec {report.spec_version}: MUST {must['passed']}/{must['tested']}, "
            f"SHOULD {should['passed']}/{should['tested']}"
            + (f", {must['skipped'] + should['skipped']} not tested" if must["skipped"] + should["skipped"] else ""))


def terminal(report: Report, color: bool = False, evidence: int = 2) -> str:
    lines = [f"jevcompat {report.tool_version} · spec {report.spec_version} · {report.url}"]
    reported = report.info.get("model_reported")
    lines.append(f"model sent {report.model!r}" + (f", server reports {reported!r}" if reported else "")
                 + f" · {len(report.exchanges)} requests · {report.seconds}s")
    if report.aborted:
        lines += ["", _c(f"stopped: {report.aborted}", "31", color)]
    section = None
    for r in report.results:
        if r.section != section:
            section = r.section
            lines += ["", _c(f"§{section} {spec.SECTIONS[section]}", "1", color)]
        mark = _c(MARK[r.status], {"pass": "32", "fail": "31", "skip": "90"}[r.status], color)
        lvl = "MUST  " if r.level == "MUST" else "SHOULD"
        tail = f"  ({r.reason})" if r.status == "skip" else ""
        lines.append(f"  {mark} {lvl} {r.id:<26} {r.title}{_c(tail, '90', color)}")
        if r.status == "fail":
            lines += _evidence(report, r, evidence, color)
    for case, err in report.case_errors:
        lines.append(_c(f"  ! case {case} could not finish: {err}", "33", color))
    lines += ["", _c(verdict(report), "1;32" if report.conformant else "1;31", color)]
    return "\n".join(lines)


def _evidence(report: Report, r: RequirementResult, limit: int, color: bool) -> list[str]:
    out = []
    for f in r.findings[:limit]:
        where = f" {f.where}" if f.where else ""
        out.append(f"      {f.case}{where}: {f.message}")
        if f.exchange is not None:
            x = report.exchanges[f.exchange]
            if x.request is not None:
                out.append(_c(f"        → {x.method} {x.path} {_clip(x.request, 220)}", "90", color))
            out.append(_c(f"        ← {x.status if x.status is not None else 'no response'} {_clip(x.response, 220)}", "90", color))
    if len(r.findings) > limit:
        out.append(_c(f"      … {len(r.findings) - limit} more", "90", color))
    return out


def to_json(report: Report) -> str:
    data = asdict(report)
    data["summary"] = report.summary()
    return json.dumps(data, ensure_ascii=False, indent=2)


def badge(report: Report) -> dict[str, Any]:
    s = report.summary()["MUST"]
    if report.aborted:
        message, color = "unreachable", "lightgrey"
    else:
        message = f"{s['passed']}/{s['tested']} MUST"
        color = "brightgreen" if report.conformant else "yellow" if s["failed"] <= 3 else "orange"
    return {"schemaVersion": 1, "label": f"jevcompat {report.spec_version}", "message": message, "color": color}


def badge_markdown(report: Report, link: str = SPEC_URL) -> str:
    b = badge(report)
    q = lambda s: urllib.parse.quote(s.replace("-", "--").replace("_", "__"), safe="")  # noqa: E731
    return f"[![{b['label']}: {b['message']}](https://img.shields.io/badge/{q(b['label'])}-{q(b['message'])}-{b['color']})]({link})"


def markdown(report: Report, title: str | None = None) -> str:
    s = report.summary()
    out = [f"# {title or report.url}", "",
           f"{badge_markdown(report)}", "",
           f"**{verdict(report)}** — jevcompat {report.tool_version}, {report.started}, "
           f"{len(report.exchanges)} requests in {report.seconds}s, model `{report.model}`"
           + (f" (server reports `{report.info['model_reported']}`)" if report.info.get("model_reported") else "") + ".", ""]
    if report.aborted:
        out += [f"> Stopped: {report.aborted}", ""]
    limits = report.info.get("limits") or {}
    if limits:
        out += ["Observed limits: " + ", ".join(f"{k.replace('_', ' ')} {v}" for k, v in limits.items()), ""]
    out += ["| | level | requirement | |", "|---|---|---|---|"]
    for r in report.results:
        note = r.reason if r.status == "skip" else (r.findings[0].message if r.findings else "")
        out.append(f"| {MARK[r.status]} | {r.level} | [`{r.id}`]({SPEC_URL}) | {_md(note, 140)} |")
    fails = [r for r in report.results if r.status == "fail"]
    if fails:
        out += ["", "## Failures", ""]
        for r in fails:
            out += [f"### `{r.id}` ({r.level}) — {r.title}", ""]
            for f in r.findings[:3]:
                out.append(f"- **{f.case}**{' `' + f.where + '`' if f.where else ''}: {_md(f.message, 400)}")
                if f.exchange is not None:
                    x = report.exchanges[f.exchange]
                    out += ["", "  <details><summary>exchange</summary>", "", "  ```",
                            f"  {x.method} {x.path}", f"  {_clip(x.request, 1200)}" if x.request is not None else "",
                            f"  → {x.status}", f"  {_clip(x.response, 1200)}", "  ```", "  </details>", ""]
            if len(r.findings) > 3:
                out.append(f"- … and {len(r.findings) - 3} more")
            out.append("")
    out += ["", f"MUST {s['MUST']['passed']}/{s['MUST']['tested']} · SHOULD {s['SHOULD']['passed']}/{s['SHOULD']['tested']}", ""]
    return "\n".join(out)


def _md(text: str, n: int) -> str:
    text = text.replace("|", "\\|").replace("\n", " ")
    return text if len(text) <= n else text[:n] + "…"
