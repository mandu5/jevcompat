"""jevcompat command line."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from . import __version__, spec


def _eprint(*a: object) -> None:
    print(*a, file=sys.stderr)


def cmd_test(args: argparse.Namespace) -> int:
    from . import report, runner

    color = sys.stdout.isatty() and not os.environ.get("NO_COLOR")
    seen = []

    def progress(name: str) -> None:
        if sys.stderr.isatty():
            seen.append(name)
            sys.stderr.write(f"\r\033[K  testing {name} ({len(seen)})")
            sys.stderr.flush()

    key = args.key or os.environ.get(args.key_env or "", "") or None
    rep = runner.run(args.url, key=key, model=args.model, timeout=args.timeout, sdk=not args.no_sdk, progress=progress)
    if sys.stderr.isatty():
        sys.stderr.write("\r\033[K")
    print(report.terminal(rep, color=color, evidence=args.evidence))
    if args.json:
        Path(args.json).write_text(report.to_json(rep) + "\n", encoding="utf-8")
        _eprint(f"  wrote {args.json}")
    if args.markdown:
        Path(args.markdown).write_text(report.markdown(rep, title=args.title) + "\n", encoding="utf-8")
        _eprint(f"  wrote {args.markdown}")
    if args.badge:
        print("\nREADME badge:\n" + report.badge_markdown(rep))
    return {"conformant": 0, "not conformant": 1, "incomplete": 3, "not tested": 2}[rep.verdict]


def cmd_mock(args: argparse.Namespace) -> int:
    from .mock import FAULTS, MockConfig, make_server

    if args.list_faults:
        for name, (req, what) in FAULTS.items():
            print(f"{name:<26} breaks {req:<26} {what}")
        return 0
    cfg = MockConfig(key=args.key, faults=frozenset(args.fault or ()), noise=args.noise)
    srv = make_server(cfg, host=args.host, port=args.port, verbose=args.verbose)
    host, port = srv.server_address[:2]
    _eprint(f"  jevcompat mock on http://{host}:{port}/v1/systemone"
            + (f"  faults: {', '.join(sorted(cfg.faults))}" if cfg.faults else "")
            + ("  (key required)" if cfg.key else ""))
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()
    return 0


def cmd_proxy(args: argparse.Namespace) -> int:
    from .proxy import ProxyConfig, make_server

    upstream_key = args.upstream_key or (os.environ.get(args.upstream_key_env) if args.upstream_key_env else None)
    cfg = ProxyConfig(upstream=args.upstream, upstream_key=upstream_key, upstream_model=args.upstream_model,
                      upstream_path=args.upstream_path, upstream_key_header=args.upstream_key_header,
                      key=args.key, split=args.split, renormalize=args.renormalize, timeout=args.timeout)
    srv = make_server(cfg, host=args.host, port=args.port, verbose=args.verbose)
    host, port = srv.server_address[:2]
    _eprint(f"  jevcompat proxy http://{host}:{port}/v1/systemone → {cfg.upstream}{cfg.upstream_path}"
            + (f" (model → {cfg.upstream_model})" if cfg.upstream_model else "") + ("  [split]" if cfg.split else ""))
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()
    return 0


def cmd_spec(args: argparse.Namespace) -> int:
    section = None
    for r in spec.REQUIREMENTS.values():
        if r.section != section:
            section = r.section
            print(f"\n§{section} {spec.SECTIONS[section]}")
        print(f"  {r.level:<6} {r.id:<26} {r.title}")
    print(f"\n{sum(r.level == 'MUST' for r in spec.REQUIREMENTS.values())} MUST, "
          f"{sum(r.level == 'SHOULD' for r in spec.REQUIREMENTS.values())} SHOULD — spec {spec.SPEC_VERSION}: "
          "https://github.com/mandu5/jevcompat/blob/main/SPEC.md")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="jevcompat",
                                description="Check a Jev-compatible (TypeSafe System One) server against a written spec.")
    p.add_argument("--version", action="version", version=f"jevcompat {__version__} (spec {spec.SPEC_VERSION})")
    sub = p.add_subparsers(dest="cmd", required=True)

    t = sub.add_parser("test", help="run the conformance suite against a server")
    t.add_argument("url", help="server root, e.g. http://localhost:8000 (the suite calls /v1/systemone and /v1/models)")
    t.add_argument("--key", help="API key, sent as Authorization: Bearer (also enables the auth checks)")
    t.add_argument("--key-env", metavar="VAR", help="read the API key from this environment variable")
    t.add_argument("--model", default="jev-latest", help="model name to send (default: jev-latest, the SDKs' default)")
    t.add_argument("--timeout", type=float, default=120.0, help="seconds per request (default 120); a timeout marks the run incomplete, never failed")
    t.add_argument("--json", metavar="PATH", help="write the full report as JSON")
    t.add_argument("--markdown", metavar="PATH", help="write the report as Markdown")
    t.add_argument("--title", help="title for the Markdown report")
    t.add_argument("--badge", action="store_true", help="print a README badge")
    t.add_argument("--evidence", type=int, default=2, metavar="N", help="failures shown per requirement (default 2)")
    t.add_argument("--no-sdk", action="store_true", help="skip the official-SDK drop-in check (the run is then incomplete)")
    t.set_defaults(fn=cmd_test)

    m = sub.add_parser("mock", help="run the reference server (a spec-exact stand-in for Jev)")
    m.add_argument("--host", default="127.0.0.1")
    m.add_argument("--port", type=int, default=8787)
    m.add_argument("--key", help="require this API key")
    m.add_argument("--fault", action="append", metavar="NAME", help="break one requirement on purpose (repeatable)")
    m.add_argument("--list-faults", action="store_true", help="list the faults and exit")
    m.add_argument("--noise", type=float, default=0.0, help="random logit noise, to imitate a non-deterministic model")
    m.add_argument("-v", "--verbose", action="store_true", help="log requests")
    m.set_defaults(fn=cmd_mock)

    x = sub.add_parser("proxy", help="serve a spec-conforming API in front of a non-conforming server")
    x.add_argument("upstream", help="the server to put behind the proxy, e.g. http://localhost:8000")
    x.add_argument("--host", default="127.0.0.1")
    x.add_argument("--port", type=int, default=8788)
    x.add_argument("--key", help="require this API key from clients")
    x.add_argument("--upstream-key", help="key to send upstream")
    x.add_argument("--upstream-key-env", metavar="VAR", help="read the upstream key from this environment variable")
    x.add_argument("--upstream-key-header", metavar="NAME", help="send the upstream key in this header instead of Authorization: Bearer")
    x.add_argument("--upstream-model", metavar="NAME", help="model name to send upstream (e.g. when it rejects jev-latest)")
    x.add_argument("--upstream-path", default="/v1/systemone", help="upstream route (default /v1/systemone)")
    x.add_argument("--split", action="store_true", help="send each question upstream on its own, so answers cannot affect each other")
    x.add_argument("--renormalize", action="store_true", help="renormalise probabilities whatever they sum to (default: only within 0.1 of 1)")
    x.add_argument("--timeout", type=float, default=120.0)
    x.add_argument("-v", "--verbose", action="store_true")
    x.set_defaults(fn=cmd_proxy)

    s = sub.add_parser("spec", help="list the requirements")
    s.set_defaults(fn=cmd_spec)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.fn(args)
    except (ValueError, OSError) as e:
        _eprint(f"jevcompat: {e}")
        return 2
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
