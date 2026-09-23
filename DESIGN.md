# jevcompat — design

## Problem

TypeSafe released Jev (System One) on 2026-09-15: one HTTP endpoint, `POST /v1/systemone`, that
answers typed questions (`noul`, `choice`, `score`) with probabilities. The model is closed and
the API was waitlisted, so within nine days about 100 open-source servers claimed to be
"Jev-compatible". Reading the code of the 26 most-starred showed:

- only 14 serve `/v1/systemone` at all;
- `confidence` means five different things (top-1 probability, top-1 − top-2 margin,
  1 − normalised entropy, `max(p, 1−p)` on noul, undisclosed);
- the choice cap is 26, 50, 64, 128, 255 or unenforced; score levels 1–10, 2–10 or unenforced;
- `"model": "jev-latest"` is ignored, echoed, rejected with 404, or rejected with 422;
- invalid requests get 400, 404, 413, 422, 500, 502 or 503;
- one server returns a `score` that is not the expectation of its own `probabilities`.

There is nothing to check a server against. TypeSafe publishes docs, an OpenAPI file and two
SDKs, and they disagree with each other in eight places (401 vs 403 for a missing key, whether
`instructions` is required, the score level range, whether the 255-option cap exists, …).
"Compatible" therefore means "worked for the author's demo".

## What jevcompat is

1. **SPEC.md** — a numbered, testable specification of the wire contract, written from TypeSafe's
   public docs, OpenAPI file, SDK source and observed behaviour. Every requirement has an id,
   a level (MUST / SHOULD) and its sources. Where official sources disagree the spec says which
   wins and why (Appendix A). It is unofficial and says so.
2. **`jevcompat test URL`** — one check per requirement, run against any server. Prints what
   failed with the request and the offending bytes, writes a JSON report, and a badge.
3. **`jevcompat mock`** — a reference server that implements the spec exactly with a
   deterministic fake model. It is the suite's own test fixture and doubles as an offline
   stand-in for Jev in application CI.
4. **`jevcompat proxy`** — sits in front of a non-conforming server and fixes what can be fixed
   (derived fields, error shapes, limits, model aliases), reporting what it changed.
5. **Measured results** for the most-starred open servers, reproducible from `results/`.

## Non-goals

- Ranking models by accuracy or calibration. JevBench, sys1bench and the Decision Index do that.
  jevcompat asks "will my client code work against this server?", not "is it smart?".
- Testing TypeSafe's hosted API. Its customer terms prohibit security testing, and the checks
  send malformed requests on purpose. The tool will run against any URL; the published results
  cover open servers only.
- Redistributing TypeSafe material. The spec is original prose that cites URLs; the OpenAPI
  file is referenced by URL and hash, not copied.

## Principles

- **Robustness rule for disagreements.** A server must *accept* anything any official source
  says is valid (union), and must *produce* only what every official client can parse
  (intersection). This turns eight arguments into one rule.
- **Every check is proven.** For each check there is a fault the mock server can inject, and a
  test asserting that the check fails under that fault and passes without it. A check that
  cannot fail is deleted.
- **Evidence over verdicts.** Every failure carries the request that caused it and the
  response bytes that violated the requirement, so a server author can reproduce it with curl.
- **Tolerances are stated, not tuned.** Float comparisons allow for two-decimal rounding
  (the precision TypeSafe's own examples use); the allowances are in SPEC.md §5.
- **No runtime dependencies.** `uvx jevcompat test URL` should start instantly; stdlib HTTP only.
  The official SDK is an optional extra used for the "drop-in" check.

## Architecture

```
spec.py      requirement registry: id, level, section, title, sources  (mirrors SPEC.md)
client.py    minimal HTTP client: Response(status, headers, body, json, ms)
validate.py  pure functions: (request, response) -> [Violation]  — the heart, no I/O
checks.py    the catalog: each Check builds request(s), calls the server, runs validators
runner.py    runs checks, catches crashes as errors, computes the summary
report.py    terminal, JSON, Markdown, shields endpoint JSON, SVG badge
mock.py      reference server + fault injection (stdlib ThreadingHTTPServer)
proxy.py     normaliser in front of an upstream server
cli.py       test | mock | proxy | spec
```

`validate.py` is shared by `checks.py` (to judge responses) and `proxy.py` (to know what to fix),
so the proxy can never "fix" something the checks would not have flagged.

### Checks

A check has an id, the requirement ids it covers, and a `run(ctx)` that returns a result:
`pass`, `fail` (with violations), `skip` (with reason: e.g. auth not enabled) or `error`
(transport failure, timeout). Categories:

| category | examples | needs model calls |
|---|---|---|
| transport | JSON content type, endpoint exists, `GET /v1/models` shape | no |
| request acceptance | each type; string/object/array state; null/object/array descriptions; unicode; 2 and 255 options; 2 and 10 levels; `jev-latest` | yes |
| response shape | answers keyed by question id; per-type fields and types; `legend` equals criteria; probability keys equal options | yes |
| derived values | Σp ≈ 1; `choice` is the argmax; `score` = Σ i·p; confidence per the documented formula | yes |
| validation | missing fields, `{}` questions, unknown type (`"boolean"`), map-form score criteria, 256 options, 11 levels, `null` state, non-JSON body → 4xx (never 2xx/5xx), 422 body shape | no |
| semantics | question-id rename does not change answers; batching does not change answers; question order does not matter | yes (repeat calls, noise-aware) |
| auth | with `--key`: missing key → 401/403 with `authentication_error` | no |
| drop-in | the official `typesafe-sdk` parses every response type | yes (optional extra) |

Semantic checks compare against measured noise: the request is sent twice first, and a
difference only fails if it exceeds `max(0.05, 3 × observed repeat difference)`.

### Scoring

The summary is two numbers: MUSTs passed / MUSTs run, SHOULDs passed / SHOULDs run. A server is
**conformant** at a spec version when every MUST passes. Skips are listed, never counted as
passes. The badge shows `spec 0.1 | 38/40 MUST`.

## Release plan

- v0.1: SPEC.md 0.1, test, mock, JSON/Markdown/badge reports, measured results for 8 servers,
  GitHub Action for server authors.
- v0.2: proxy; JS port of the validators if server authors ask for it.
