# Jev-compatible API — specification 0.1 (draft)

This document specifies what a server must do to be a drop-in replacement for TypeSafe's
System One API (`POST /v1/systemone`, the API behind the Jev model), and what a client may rely
on. It is **unofficial**: it is written from TypeSafe's public documentation, OpenAPI file and
SDK source, and it is not endorsed by TypeSafe. Where those sources are silent or disagree, this
document makes a choice and says why (Appendix A).

Every requirement has an id (`choice.argmax`) that [`jevcompat test`](README.md) reports against.

## 0. Conventions

**MUST**, **SHOULD** and **MAY** are used as in RFC 2119. Levels are assigned by one rule:

- **MUST** — a client written against TypeSafe's documentation or official SDKs breaks if the
  server violates it: an exception, a crash, or a wrong answer returned as if it were right.
- **SHOULD** — violating it does not break documented clients, but it makes the server behave
  differently from the official one in a way a client can observe (an error shape, a rejected
  edge case, a field that may collide with a future official one).

Disagreements between official sources are settled by the **robustness rule**: a server accepts
every request that any official source describes as valid, and produces only responses that
every official client parses.

"Official sources" are, as retrieved on 2026-09-24:

| tag | source |
|---|---|
| `[api]` | API reference, https://docs.typesafe.ai/api |
| `[docs]` | other pages under https://docs.typesafe.ai (named where cited) |
| `[oas]` | OpenAPI 3.1 file served by the API, https://api.typesafe.ai/openapi.json (`info.version` 0.2.0) |
| `[sdk-py]` | `typesafe-sdk` 0.7.1, https://github.com/typesafe-ai/typesafe-sdk-python |
| `[sdk-js]` | `@typesafe-ai/sdk` 0.6.0, https://github.com/typesafe-ai/typesafe-sdk-js |
| `[live]` | behaviour observed from `api.typesafe.ai` with unauthenticated requests |

`[oas]` is generated from the server's own request models, so it is the best evidence of what the
official server *accepts*; the SDKs are the best evidence of what clients *require*.

A server is **conformant** to this version when every MUST that applies to it was tested and
passed. Two MUSTs are conditional (`auth.ignored-when-off` applies only without authentication,
`auth.bearer` only with it). A run in which an applicable MUST could not be tested — the server
timed out, the connection dropped — is **incomplete**, not conformant.

## 1. Transport

**http.endpoint** — MUST. The server accepts `POST /v1/systemone` with a JSON request body
(`Content-Type: application/json`) and answers valid requests with status `200`. `[api]` `[oas]`

**http.json** — MUST. The body of every `200` response is JSON. `[api]` `[oas]`

**http.content-type** — SHOULD. Every response, success or error, declares a JSON media type
(`application/json`, or a `+json` type). The official server does `[live]`; the Python SDK does
not depend on it `[sdk-py]`.

**http.models** — SHOULD. `GET /v1/models` returns `200` and
`{"models": [{"name": str, "description": str, "release_date": "YYYY-MM-DD"}, …]}` with at least one
entry. `[oas]` `[docs]` (models)

A server MAY return an `x-typesafe-request-id` header. `[live]`

## 2. Authentication

A server MAY run without authentication.

**auth.ignored-when-off** — MUST. A server that runs without authentication accepts requests that
carry an `Authorization` header. The official SDKs always send `Authorization: Bearer <key>`.
`[sdk-py]` `[sdk-js]`

When authentication is enabled:

**auth.bearer** — MUST. The key is read from `Authorization: Bearer <key>`. `[api]` `[oas]`

**auth.missing** — SHOULD. A request without a key gets `401` or `403` with body
`{"detail": {"error_type": "authentication_error", "message": str}}`. (The docs say `401`; the
official server returns `403`. Both are allowed: A.1.) `[api]` `[live]`

**auth.invalid** — SHOULD. A request with a wrong key gets `401` with the same body shape. `[live]`

## 3. Request

```json
{
  "model": "jev-latest",
  "state": "…",
  "questions": {
    "urgent":  {"type": "noul",   "instructions": "…", "criteria": {"true": "…", "false": "…"}},
    "team":    {"type": "choice", "instructions": "…", "criteria": {"billing": "…", "sales": null}},
    "anger":   {"type": "score",  "instructions": "…", "criteria": ["Calm", "Frustrated", "Very angry"]}
  }
}
```

In this section, *accepts* means: answers with `200` and a response that meets §4.

### 3.1 Top level

**request.state** — MUST. `state` may be a string, a JSON object or a JSON array; the server
accepts all three. `[oas]` `[api]`

**request.model-alias** — MUST. The server accepts `"model": "jev-latest"`. It is the official
SDKs' default model, and documentation examples send it. `[sdk-py]` (`DEFAULT_MODEL`) `[api]`
`[docs]` (models) A server MAY accept
other model names and MAY report its own name in the response's `model`.

**request.multi** — MUST. The server accepts several questions of different types in one request
and answers each one. `[api]` `[docs]` (primitives)

**request.question-ids** — MUST. A question id is any non-empty string; the server accepts ids
containing `-`, `.`, spaces and non-ASCII characters and returns them unchanged. `[oas]`

**request.unicode** — MUST. The server accepts non-ASCII text (e.g. Hangul, emoji) in `state`,
`instructions`, criteria descriptions and choice option names, and returns option names
byte-for-byte as sent. Clients look answers up by these strings.

**request.unknown-fields** — SHOULD. Unknown top-level fields are ignored. The Python SDK forwards
caller-supplied extra fields (`extra_body`); the official server's schema does not forbid them.
`[sdk-py]` `[oas]`

**request.structured-text** — MUST. `instructions` and every criteria description may be a string,
an object or an array. `[api]` `[oas]`

### 3.2 Noul

**noul.criteria** — MUST. `criteria` may be omitted, `null`, `{"true": …, "false": …}`, or one-sided
(`{"true": …}` or `{"false": …}`). `[oas]` `[sdk-js]` (live integration test)

**noul.no-instructions** — SHOULD. A noul question without `instructions` is accepted. (The docs
call `instructions` required; the official server's schema does not: A.2.) `[oas]` `[api]`

### 3.3 Choice

**choice.null-description** — MUST. An option's description may be `null`; the option is then
interpreted by its name. `[api]`

**choice.options** — MUST. The server accepts every option count from 2 to 255 inclusive. `[api]`
("You can have a maximum of 255 options per Choice.") A server that cannot serve 255 options is
not a drop-in replacement: a client with 100 options breaks.

### 3.4 Score

**score.levels** — MUST. `criteria` is an ordered array of level descriptions, low to high; the
server accepts every level count from 2 to 10 inclusive. `[api]` ("A Score should have at least
two levels; the API accepts up to 10.")

**score.map-rejected** — SHOULD. Score `criteria` given as an object (the pre-0.6 SDK form,
`{"0": …, "1": …}`) is rejected with a 4xx status. `[oas]` `[sdk-js]` (v0.6.0 changelog)

### 3.5 Limits

Beyond the ranges above — a choice with 0, 1 or 256+ options, a score with 1 or 11+ levels — the
official behaviour is not documented. A server MAY accept such requests; if it rejects them it
does so with a 4xx status (**errors.no-5xx**, §6).

The official context budget is 64k tokens per request and 32k for `state` plus the longest
question. `[docs]` (models) A server MAY have a smaller budget and SHOULD reject requests over it
with `413` or `422`, not truncate silently.

## 4. Response

```json
{
  "model": "jev-1.13.0",
  "answers": {
    "urgent": {"type": "noul", "noul": 0.95},
    "team":   {"type": "choice", "choice": "billing",
               "probabilities": {"billing": 0.88, "sales": 0.12}, "confidence": 0.76},
    "anger":  {"type": "score", "score": 1.05,
               "legend": {"0": "Calm", "1": "Frustrated", "2": "Very angry"},
               "probabilities": {"0": 0.0, "1": 0.95, "2": 0.05}, "confidence": 0.925}
  },
  "usage": {"input_tokens": 304, "output_tokens": 18}
}
```

### 4.1 Envelope

**response.envelope** — MUST. The body is an object with `model` (string), `answers` (object) and
`usage` (object). `[oas]` `[sdk-py]` (all three are required by the SDK's strict response model)

**response.usage** — MUST. `usage.input_tokens` and `usage.output_tokens` are non-negative JSON
integers. `[oas]` `[sdk-py]` (strict mode rejects `12.0` for an integer)

**response.answer-ids** — MUST. `answers` has exactly one entry per question id in the request —
none missing, none added. `[api]` `[oas]` (A client that looks up each answer's question by id,
as documented examples do, breaks on an added one.)

**response.answer-type** — MUST. Each answer's `type` equals its question's `type`. `[oas]`

**response.finite** — MUST. Every number in the response is a finite JSON number. `NaN` and
`Infinity` are not JSON; Python's `json.dumps` emits them by default and every strict parser
rejects them.

**response.extensions** — SHOULD. Fields not defined by this specification — at the top level or
inside an answer — have names beginning with `x_` (for example `x_latency_ms`). The SDKs ignore
unknown fields, so an extra field breaks nothing today; an unprefixed one (`confidence` on a noul
answer, `action`, `certainty`, `metadata`) collides the day TypeSafe adds a field with that name
and a different meaning.

### 4.2 Noul answer

**noul.answer** — MUST. `{"type": "noul", "noul": p}` where `p` is a number in [0, 1], the
probability that the answer is yes. `[api]` `[oas]`

### 4.3 Choice answer

**choice.answer** — MUST. The answer has `choice` (string), `probabilities` (object) and
`confidence` (number). `[api]` `[oas]`

**choice.probability-keys** — MUST. The keys of `probabilities` are exactly the option names of
the request, byte-for-byte. `[api]` ("covers every option")

**choice.distribution** — MUST. Every probability is in [0, 1] and they sum to 1 within
`ε_sum` (§5). `[api]` ("values sum to approximately 1")

**choice.argmax** — MUST. `choice` is an option name whose probability is the largest, within
`ε_round` (§5). `[api]` ("the highest-probability option")

### 4.4 Score answer

**score.answer** — MUST. The answer has `score` (number), `legend` (object), `probabilities`
(object) and `confidence` (number). `[api]` `[oas]`

**score.legend** — MUST. `legend` maps `"0"` … `"n-1"` (decimal strings) to the request's level
descriptions, in order, unchanged. `[api]`

**score.probability-keys** — MUST. The keys of `probabilities` are `"0"` … `"n-1"`. `[api]`

**score.distribution** — MUST. As **choice.distribution**.

**score.expectation** — MUST. `score` equals Σ i·pᵢ over the returned probabilities, within
`ε_score` (§5). `[api]` ("the probability-weighted answer across the levels") A client that reads
both `score` and `probabilities` must not see two different answers.

### 4.5 Confidence

**confidence.range** — MUST. `confidence` is a number in [0, 1]. `[api]` `[oas]`

**confidence.formula** — SHOULD. `confidence` equals the reference formula below within
`ε_conf` (§5). TypeSafe says confidence is "derived from the probabilities", that "all of it on
one option gives 1.0; the more evenly it spreads, the lower the confidence", and uses
`(3 × largest − 1) / 2` for three options `[docs]` (confidence). The reference formulas reproduce
the documentation's worked examples and are the ones in TypeSafe's own adapter library
(`system-one-adapter-python`, `confidence_metrics.py`):

- choice with n options and largest probability m: `(m − 1/n) / (1 − 1/n)`; 1 when n = 1.
- score with n levels, probabilities pᵢ and most likely level k:
  `max(0, 1 − Σ pᵢ·|i − k| / D)` where `D = (1/n)·Σ |i − (n−1)/2|` is the same quantity for a
  uniform distribution; 1 when n = 1.

This is SHOULD, not MUST, because TypeSafe says clients are "never locked into our definition".
It matters because clients pick thresholds on `confidence`: across open servers today the field
is variously the top probability, the top-two margin and an entropy measure, so a threshold
tuned on one server means something else on another.

A noul answer has no `confidence`. `[docs]` (confidence)

## 5. Numeric tolerances

Servers may round the numbers they report, and official examples give probabilities to two
decimals, so every comparison allows for the rounding the response actually shows. For an
answer's probabilities, let d be the smallest number of decimal places from 2 to 6 at which every
probability is exact, and r = ½·10⁻ᵈ the largest rounding error per value; values exact at none
of them have r = 0. Rounding coarser than two decimals is never assumed. For n options or levels,
k of them reported as non-zero:

| name | bound | used by |
|---|---|---|
| `ε_sum` | above 1: max(0.05, k·r); below 1: max(0.05, n·r) | how far Σp may be from 1. 0.05 is the bound the official JS SDK's live test uses (`toBeCloseTo(1, 1)`). Rounding raises a sum by at most r per value reported as non-zero (a reported 0 was rounded down) and lowers it by at most r per value. |
| `ε_round` | 0.005 | the chosen option may trail the largest probability by this much |
| `ε_score` | 0.02 + r·(1 + n(n−1)/2) | `\|score − Σ i·pᵢ\|`: the base allowance plus rounding of each pᵢ and of `score` |
| `ε_conf` | 0.02 + the change rounding by r can cause in the reference formula | `\|confidence − reference\|` |

Every bound is compared with a slack of 10⁻⁹ so that exact boundary values pass. Where several
options or levels tie for the largest probability within `ε_round`, the reference confidence may
use any of them.

## 6. Errors

**errors.json** — SHOULD. Error responses have JSON bodies. The SDKs read the message from them
and fall back to the raw text when they are not JSON, so a plain-text or HTML error page degrades
error messages but breaks nothing. `[sdk-py]` `[live]`

**errors.no-5xx** — MUST. A request that is malformed or outside the documented ranges never
produces a `5xx` status. The SDKs retry `5xx` (and `408`, `429`), so a server that answers a bad
request with `500` makes every client retry a request that can never succeed. `[sdk-py]` `[sdk-js]`

**errors.reject-invalid** — SHOULD. A request that is invalid under §3 gets a `4xx` status, not a
`200`. A server that answers requests the official server rejects lets bugs pass in development
that fail in production. Invalid includes: a body that is not JSON; missing `state` or `questions`;
`questions` equal to `{}`; a question without `type`; an unknown `type` (for example `"boolean"`,
which other decision APIs use); a choice with empty `criteria`; a score whose `criteria` is not an
array.

**errors.validation-shape** — SHOULD. Validation failures use status `422` and the body
`{"detail": [{"loc": [..], "msg": str, "type": str}, …]}`, where `loc` locates the offending field
starting with `"body"`. `[oas]` (`HTTPValidationError`) `[sdk-js]` (live integration test)

**errors.shape** — SHOULD. Other errors use `{"detail": {"error_type": str, "message": str}}`.
`[live]` `[sdk-js]`

Servers under load SHOULD answer `429` (over a rate limit) or `529` (overloaded); the SDKs back off
and retry both. `[api]`

## 7. Semantics

These are observable only by comparing responses, and servers are not required to be
deterministic, so each comparison is statistical. The base request and the variant are each sent
k = 3 times. When the server ignores unknown fields (`request.unknown-fields`), every request
carries a distinct `x_nonce`, so a response cache cannot make repeats look identical. For every
number an answer commits to (the `noul` value, each probability), let m and m′ be its means over
the base and variant sends and σ its pooled standard deviation over both groups. The number
differs when |m − m′| > max(0.05, 4·σ·√(2/k)).

- If any of these limits is 0.5 or more, both groups are sent 3 more times, up to k = 9. If a
  limit is still 0.5 or more, the server is too noisy to judge, and the requirement is reported
  as not tested.
- A difference fails the requirement only when a second, fresh round of sends shows a difference
  for the same number in the same direction. One unlucky round of a sampling server is not a
  finding.

**semantics.question-id** — MUST. Renaming a question id does not change its answer. `[api]`
("The key is not sent to the underlying model and is not used in inference.")

**semantics.batching** — SHOULD. A question's answer does not change when other questions are added
to the same request. `[docs]` (primitives: "System One models evaluate every question in a request
in parallel"; parallel questions cookbook: "no change in the answers")

**semantics.question-order** — SHOULD. The order of questions in the `questions` object does not
change any answer.

## 8. Drop-in

**dropin.sdk-python** — MUST. The official Python SDK, pointed at the server with `base_url`,
parses the server's responses to noul, choice and score questions without raising. This is the
end-to-end form of §4 and catches anything the field-level requirements miss.

## Appendix A. Disagreements between official sources

| # | topic | sources say | this spec |
|---|---|---|---|
| A.1 | missing API key | `[api]`: 401 · `[live]`: 403 | either (auth.missing) |
| A.2 | `instructions` | `[api]`: required · `[oas]`: optional | clients send it; servers SHOULD accept its absence (noul.no-instructions) |
| A.3 | score level count | `[api]`: 2–10 · `[oas]`: ≥1, no max · `[sdk-py]`: ≥1 · `[sdk-js]`: ≥2 | MUST accept 2–10; outside, accept or 4xx (score.levels, §3.5) |
| A.4 | choice option count | `[api]`: ≤255 · `[oas]`: no bounds | MUST accept 2–255; outside, accept or 4xx (choice.options, §3.5) |
| A.5 | `state: null` | `[sdk-js]` type allows it · `[oas]`: not allowed | not required; accept or 4xx |
| A.6 | `null` score level | `[sdk-js]` type allows it · `[oas]`: not allowed | not required; accept or 4xx |
| A.7 | choice confidence example | `[api]` example: 0.81 · reference formula on the same probabilities: 0.82 | within `ε_conf` either way |
| A.8 | error body | `[live]`: `{"detail": {"error_type", "message"}}` · Vercel's gateway: top-level `{"message", "error_type"}` | `detail` form (errors.shape) |

## Appendix B. Changes

- 0.1 (2026-09-24): first draft.
