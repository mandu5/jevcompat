# jevcompat

**About a hundred servers say they are "Jev-compatible". Nothing said what that means. Now something does.**

`jevcompat` is three things for the TypeSafe System One API (`POST /v1/systemone`, the API behind Jev):

1. **[SPEC.md](SPEC.md)** — a numbered, testable specification: 48 requirements, each with a
   level (MUST / SHOULD) and the official source it comes from. Where TypeSafe's docs, OpenAPI
   file and SDKs disagree (they do, in eight places), it says which wins and why.
2. **`jevcompat test URL`** — runs the spec against any server and shows, for every failure, the
   request that caused it and the bytes that broke the rule.
3. **`jevcompat proxy URL`** — puts a spec-conforming API in front of a server that isn't,
   fixing what can be fixed and refusing, loudly, what can't.

```
uvx jevcompat test http://localhost:8000
```

<!-- RESULTS -->

## Why

Jev's weights are closed and the API was waitlisted, so within nine days of the 2026-09-15 launch
there were ~100 open-source servers claiming compatibility. Reading the code of the 26 most-starred:

- only 14 serve `/v1/systemone` at all;
- **`confidence` means five different things**: the top probability, the top-two margin,
  1 − normalised entropy, `max(p, 1−p)` on yes/no answers, or undisclosed. A threshold of 0.8
  tuned on one server means something else on the next;
- the choice limit is 26, 50, 64, 128, 255 or unenforced — the docs promise 255;
- `"model": "jev-latest"`, the official SDKs' default, is ignored, echoed, rejected with 404, or
  rejected with 422;
- invalid requests get 400, 404, 413, 422, 500, 502 or 503. The SDKs *retry* 5xx.

None of that is visible until your code breaks. The spec makes it visible, and the suite checks it.

## What it checks

| § | area | what a server must get right |
|---|---|---|
| 1 | transport | the route, JSON everywhere, `GET /v1/models` |
| 2 | auth | Bearer keys; and, with auth off, not choking on the header the SDKs always send |
| 3 | requests | string/object/array `state`; `null`, object and array descriptions; 2–255 options; 2–10 score levels; any question id; Unicode that round-trips byte-for-byte |
| 4 | responses | the envelope; one answer per id; integer token counts; no `NaN`; probabilities keyed exactly by option, summing to 1; `choice` is the argmax; `score` is Σ i·p; `legend` echoes the levels; `confidence` per the documented formula |
| 6 | errors | never a 5xx for a bad request; 422 with `detail[]` for validation; `detail.error_type` otherwise |
| 7 | semantics | renaming a question id, adding questions, or reordering them does not change answers (noise-aware: a difference fails only above 3× the server's own repeat-to-repeat variation) |
| 8 | drop-in | the official `typesafe-sdk` parses every answer type |

`jevcompat spec` lists all 48. Checks judge the wire contract, not intelligence: a server can be
fully conformant and still give bad answers. For accuracy and calibration, see
[JevBench](https://github.com/fstandhartinger/jevbench) and
[sys1bench](https://github.com/rssr25/sys1bench).

## Every check is proven to fail

A conformance suite that never fails is worse than none. `jevcompat mock` is a reference server
that implements the spec exactly, and it can break any requirement on purpose:

```
jevcompat mock --list-faults        # 47 faults: every requirement but the SDK check has at least one
jevcompat mock --fault choice-second --fault legend-1-based
```

The test suite runs every check against the clean mock (must pass), against a noisy mock over
many seeds (must never fail — the semantic checks are statistics, and are tested as statistics),
and against each fault (the targeted requirement must fail, and a single fault must not smear
failures across unrelated MUSTs). If a check could not catch the thing it exists to catch, or
blames the wrong requirement, CI goes red.

## Use

```
jevcompat test http://localhost:8000                    # terminal report
jevcompat test URL --key-env MY_KEY                     # server with auth (also runs the auth checks)
jevcompat test URL --json r.json --markdown r.md --badge
```

The verdict is **conformant** (every applicable MUST tested and passed; exit 0), **not
conformant** (a MUST failed; exit 1), **not tested** (the server could not be reached or refused
a minimal request; exit 2) or **incomplete** (nothing failed, but a MUST could not be judged —
usually a timeout, which is never counted against the server; exit 3). The output names the
requirement, the case, and the exchange:

```
§4.4 Score answer
  ✗ MUST   score.expectation          score is the expectation of the probabilities
      score-levels:3 answers['anger']: score is 2.000; the probabilities give Σ i·p = 1.412
        → POST /v1/systemone {"model": "jev-latest", "state": "Hi, I was charged twice…
        ← 200 {"model":"…","answers":{"anger":{"type":"score","score":2.0,…
```

### Put a proxy in front of a server

```
jevcompat proxy http://localhost:8000 --port 8788            # then point clients at :8788
jevcompat proxy URL --upstream-model laya --split             # rename the model; one question per upstream call
```

The proxy recomputes `choice`, `score`, `legend` and `confidence` from the probabilities,
reconciles option names that differ only by Unicode normalisation or case, renormalises, fixes
token counts, prefixes extra fields with `x_`, answers `/v1/models`, validates requests itself so
bad ones get a proper 422, and hides question ids and order from the upstream so answers cannot
depend on them (`--split` also rules out any effect of one question on another). What it cannot
fix — a missing or ambiguous option, probability mass on options nobody asked about, a
probability of 1.3, a sum far from 1 (unless you pass `--renormalize`) — it refuses with
`502 upstream_error` rather than pass through. Each response lists what it changed in
`x-jevcompat-fixes`. Of the mock's 47 faults, the proxy fixes 38 and refuses 9.

### Test your server in CI

```yaml
- run: my-server --port 8000 &                 # start your server
- uses: mandu5/jevcompat@v0
  with:
    url: http://localhost:8000
```

The step fails unless the verdict is conformant, writes the report to the job summary, and
outputs the verdict and a badge:

[![jevcompat 0.1: 32/32 MUST](https://img.shields.io/badge/jevcompat%200.1-32%2F32%20MUST-brightgreen)](SPEC.md)

### Use the mock in your application's tests

`jevcompat mock --port 8787` is a spec-exact stand-in for Jev with deterministic answers. Point
`TYPESAFE_BASE_URL` at it and your CI no longer needs a key, a network, or a waitlist.

## FAQ

**Is this official?** No. It is written from TypeSafe's public docs, OpenAPI file and SDK source,
and cites them requirement by requirement. If TypeSafe publishes a conformance suite, this one
should defer to it.

**Why not test TypeSafe's own API?** The suite sends malformed requests on purpose, and
TypeSafe's customer terms prohibit security testing. The tool will run against any URL; the
published results cover open-source servers only.

**Why is `confidence.formula` only a SHOULD?** TypeSafe says clients are "never locked into our
definition" and ships the full probabilities. But a threshold means the same thing across servers
only if the number does, so the spec recommends the formula TypeSafe documents and uses.

**My server fails a requirement I think is wrong.** Open an issue quoting the requirement id.
The spec is a draft; disagreements with evidence are how it gets better.

## Development

```
uv run --extra dev pytest -q      # validators, every fault, statistical semantics, preflight, the proxy, the CLI
```

Design notes: [DESIGN.md](DESIGN.md).

## License

MIT
