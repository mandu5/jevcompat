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


def shown_request(request: Any, state_chars: int = 60) -> Any:
    """The request as evidence: questions first (they are usually the point), long state elided."""
    if not isinstance(request, dict):
        return request
    out = {k: request[k] for k in ("questions", "model") if k in request}
    out.update({k: v for k, v in request.items() if k not in ("questions", "model", "state")})
    if "state" in request:
        st = request["state"]
        text = st if isinstance(st, str) else json.dumps(st, ensure_ascii=False)
        out["state"] = st if len(text) <= state_chars else text[:state_chars] + "…"
    return out


def verdict(report: Report) -> str:
    if report.aborted:
        return f"not tested: {report.aborted}"
    s = report.summary()
    must, should = s["MUST"], s["SHOULD"]
    counts = f"MUST {must['passed']}/{must['tested']}, SHOULD {should['passed']}/{should['tested']}"
    if report.verdict == "incomplete":
        why = []
        if report.untested_musts:
            why.append(f"not tested: {', '.join(report.untested_musts)}")
        if report.inconclusive or report.case_errors:
            why.append(f"{len(report.inconclusive) + len(report.case_errors)} request(s) timed out or failed")
        return f"incomplete against spec {report.spec_version}: {counts} ({'; '.join(why)})"
    return f"{report.verdict} to spec {report.spec_version}: {counts}"


def terminal(report: Report, color: bool = False, evidence: int = 2) -> str:
    lines = [f"jevcompat {report.tool_version} · spec {report.spec_version} · {report.url}"]
    reported = report.info.get("model_reported")
    sdk = report.info.get("typesafe_sdk")
    lines.append(f"model sent {report.model!r}" + (f", server reports {reported!r}" if reported else "")
                 + f" · {len(report.exchanges)} requests · {report.seconds}s" + (f" · typesafe-sdk {sdk}" if sdk else ""))
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
    for item in report.inconclusive:
        lines.append(_c(f"  ! {item}", "33", color))
    for case, err in report.case_errors:
        lines.append(_c(f"  ! case {case} could not finish: {err}", "33", color))
    tone = {"conformant": "1;32", "incomplete": "1;33"}.get(report.verdict, "1;31")
    lines += ["", _c(verdict(report), tone, color)]
    return "\n".join(lines)


def _evidence(report: Report, r: RequirementResult, limit: int, color: bool) -> list[str]:
    out = []
    for f in r.findings[:limit]:
        where = f" {f.where}" if f.where else ""
        out.append(f"      {f.case}{where}: {f.message}")
        if f.exchange is not None:
            x = report.exchanges[f.exchange]
            via = " (via typesafe-sdk)" if x.via != "http" else ""
            if x.request is not None:
                out.append(_c(f"        → {x.method} {x.path}{via} {_clip(shown_request(x.request), 260)}", "90", color))
            status = x.status if x.status is not None else ("raised" if x.via != "http" else "no response")
            out.append(_c(f"        ← {status} {_clip(x.response, 260)}", "90", color))
    if len(r.findings) > limit:
        out.append(_c(f"      … {len(r.findings) - limit} more", "90", color))
    return out


def to_json(report: Report) -> str:
    data = asdict(report)
    data["summary"] = report.summary()
    return json.dumps(data, ensure_ascii=False, indent=2, default=lambda o: sorted(o) if isinstance(o, set) else str(o))


def badge(report: Report) -> dict[str, Any]:
    s = report.summary()["MUST"]
    if report.aborted:
        message, color = "not tested", "lightgrey"
    elif report.verdict == "incomplete":
        message, color = f"{s['passed']}/{s['tested']} MUST, incomplete", "yellow"
    else:
        message = f"{s['passed']}/{s['tested']} MUST"
        color = "brightgreen" if report.conformant else "orange" if s["failed"] <= 3 else "red"
    return {"schemaVersion": 1, "label": f"jevcompat {report.spec_version}", "message": message, "color": color}


def badge_markdown(report: Report, link: str = SPEC_URL) -> str:
    b = badge(report)
    q = lambda s: urllib.parse.quote(s.replace("-", "--").replace("_", "__"), safe="")  # noqa: E731
    return f"[![{b['label']}: {b['message']}](https://img.shields.io/badge/{q(b['label'])}-{q(b['message'])}-{b['color']})]({link})"


def markdown(report: Report, title: str | None = None) -> str:
    s = report.summary()
    out = [f"# {title or report.url}", "",
           f"{badge_markdown(report)}", "",
           f"**{_md(verdict(report), 600)}** — jevcompat {report.tool_version}, {report.started}, "
           f"{len(report.exchanges)} requests in {report.seconds}s, model `{report.model}`"
           + (f" (server reports `{report.info['model_reported']}`)" if report.info.get("model_reported") else "")
           + (f", typesafe-sdk {report.info['typesafe_sdk']}" if report.info.get("typesafe_sdk") else "") + ".", ""]
    limits = report.info.get("limits") or {}
    if limits:
        out += ["Observed limits: " + ", ".join(f"{k} {v}" for k, v in limits.items()), ""]
    failed_musts = [r for r in report.results if r.status == "fail" and r.level == "MUST"]
    if failed_musts:
        out += ["**Failed MUSTs:** " + ", ".join(f"[`{r.id}`]({SPEC_URL}#{r.id}) — {r.title}" for r in failed_musts), ""]
    out += ["| | level | requirement | result |", "|---|---|---|---|"]
    for r in report.results:
        note = r.reason if r.status == "skip" else (r.findings[0].message if r.findings else "")
        out.append(f"| {MARK[r.status]} | {r.level} | [`{r.id}`]({SPEC_URL}#{r.id}) {r.title} | {_md(note, 160)} |")
    fails = [r for r in report.results if r.status == "fail"]
    if fails:
        out += ["", "## Failures", ""]
        for r in fails:
            out += [f"### [`{r.id}`]({SPEC_URL}#{r.id}) ({r.level}) — {r.title}", ""]
            for f in r.findings[:3]:
                out.append(f"- **{f.case}**{' `' + f.where + '`' if f.where else ''}: {_md(f.message, 400)}")
                if f.exchange is not None:
                    x = report.exchanges[f.exchange]
                    req = _clip(shown_request(x.request), 1500) if x.request is not None else ""
                    resp = _clip(x.response, 1500)
                    fence = "`" * max(3, _longest_backtick_run(req + resp) + 1)
                    via = " (via typesafe-sdk)" if x.via != "http" else ""
                    out += ["", "  <details><summary>exchange</summary>", "", f"  {fence}",
                            f"  {x.method} {x.path}{via}", f"  {req}",
                            f"  → {x.status if x.status is not None else 'raised'}", f"  {resp}", f"  {fence}", "  </details>", ""]
            if len(r.findings) > 3:
                out.append(f"- … and {len(r.findings) - 3} more")
            out.append("")
    out += ["", f"MUST {s['MUST']['passed']}/{s['MUST']['tested']} · SHOULD {s['SHOULD']['passed']}/{s['SHOULD']['tested']}", ""]
    return "\n".join(out)


def _md(text: str, n: int) -> str:
    text = text.replace("\n", " ")
    text = text if len(text) <= n else text[:n] + "…"
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("|", "\\|").replace("`", "'")


def _longest_backtick_run(text: str) -> int:
    best = run = 0
    for ch in text:
        run = run + 1 if ch == "`" else 0
        best = max(best, run)
    return best
