"""Run the cases against a server and fold the findings into one result per requirement."""
from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from . import __version__, spec
from .checks import CASES, Abort, Ctx, Exchange, Finding, preflight
from .client import Client, Timeout, TransportError


@dataclass
class RequirementResult:
    id: str
    level: str
    section: str
    title: str
    status: str  # pass | fail | skip
    findings: list[Finding] = field(default_factory=list)
    cases: list[str] = field(default_factory=list)
    reason: str = ""


@dataclass
class Report:
    url: str
    model: str
    spec_version: str
    tool_version: str
    started: str
    seconds: float
    results: list[RequirementResult]
    exchanges: list[Exchange]
    info: dict[str, Any]
    aborted: str | None = None
    case_errors: list[tuple[str, str]] = field(default_factory=list)
    inconclusive: list[str] = field(default_factory=list)

    def count(self, level: str, status: str) -> int:
        return sum(1 for r in self.results if r.level == level and r.status == status)

    @property
    def untested_musts(self) -> list[str]:
        """Applicable MUSTs that were not tested. Exactly one of the two auth MUSTs applies."""
        conditional = {"auth.bearer", "auth.ignored-when-off"}
        return [r.id for r in self.results if r.level == "MUST" and r.status == "skip" and r.id not in conditional]

    @property
    def verdict(self) -> str:
        if self.aborted:
            return "not tested"
        if self.count("MUST", "fail"):
            return "not conformant"
        if self.untested_musts or self.case_errors or self.inconclusive:
            return "incomplete"
        return "conformant"

    @property
    def conformant(self) -> bool:
        return self.verdict == "conformant"

    def summary(self) -> dict[str, Any]:
        out: dict[str, Any] = {"verdict": self.verdict, "conformant": self.conformant,
                               "untested_musts": self.untested_musts}
        for level in ("MUST", "SHOULD"):
            p, f, s = (self.count(level, x) for x in ("pass", "fail", "skip"))
            out[level] = {"passed": p, "failed": f, "skipped": s, "tested": p + f}
        return out


def run(url: str, *, key: str | None = None, model: str = "jev-latest", timeout: float = 120.0, sdk: bool = True,
        progress: Callable[[str], None] | None = None, only: set[str] | None = None) -> Report:
    """Run the suite. `only` limits it to the named cases (the preflight always runs)."""
    client = Client(url, key=key, model=model, timeout=timeout)
    ctx = Ctx(client, key_given=key is not None, sdk=sdk)
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    t0 = time.perf_counter()
    aborted = None
    errors: list[tuple[str, str]] = []
    try:
        if progress:
            progress("preflight")
        preflight(ctx)
    except Abort as e:
        aborted = str(e)
    except Timeout as e:
        aborted = f"no answer to a minimal request: {e}"
    except TransportError as e:
        aborted = f"cannot reach {url}: {e}"
    if not aborted:
        for c in CASES:
            if only is not None and c.name not in only:
                continue
            if progress:
                progress(c.name)
            try:
                c.fn(ctx, c.name)
            except TransportError as e:
                errors.append((c.name, str(e)))
    results = fold(ctx, aborted)
    return Report(url=url, model=client.model, spec_version=spec.SPEC_VERSION, tool_version=__version__,
                  started=started, seconds=round(time.perf_counter() - t0, 1), results=results,
                  exchanges=ctx.exchanges, info=ctx.info, aborted=aborted, case_errors=errors,
                  inconclusive=ctx.inconclusive)


def fold(ctx: Ctx, aborted: str | None) -> list[RequirementResult]:
    by_req: dict[str, list[Finding]] = {}
    for f in ctx.findings:
        by_req.setdefault(f.req, []).append(f)
    out = []
    for req in spec.REQUIREMENTS.values():
        findings = by_req.get(req.id, [])
        cases = sorted(ctx.exercised.get(req.id, set()))
        if findings:
            status, reason = "fail", ""
        elif cases:
            status, reason = "pass", ""
        else:
            status = "skip"
            reason = ctx.skipped.get(req.id) or (f"not reached: {aborted}" if aborted else "no case observed it")
        out.append(RequirementResult(req.id, req.level, req.section, req.title, status, findings, cases, reason))
    unknown = set(by_req) - set(spec.REQUIREMENTS)
    if unknown:  # a case tagged a finding with an id the spec does not have: a bug in jevcompat
        raise RuntimeError(f"findings for unknown requirement(s): {', '.join(sorted(unknown))}")
    return out
