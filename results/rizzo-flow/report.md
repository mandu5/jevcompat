# Rizzo-AI-Academy/rizzo-flow @ d34665b

[![jevcompat 0.1: 31/32 MUST](https://img.shields.io/badge/jevcompat%200.1-31%2F32%20MUST-orange)](https://github.com/mandu5/jevcompat/blob/main/SPEC.md)

**not conformant to spec 0.1: MUST 31/32, SHOULD 9/12** — jevcompat 0.1.0, 2026-09-23T23:20:46+00:00, 60 requests in 11.3s, model `jev-latest` (server reports `rizzo-spark-x2.5-1.7b-q8_0`), typesafe-sdk 0.7.1.

Observed limits: choice options accepted up to 26, choice options rejected at 64, score levels accepted up to 10

**Failed MUSTs:** [`choice.options`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#choice.options) — 2 to 255 options are accepted

| | level | requirement | result |
|---|---|---|---|
| ✓ | MUST | [`http.endpoint`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#http.endpoint) POST /v1/systemone answers valid requests with 200 |  |
| ✓ | MUST | [`http.json`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#http.json) 200 bodies are JSON |  |
| ✓ | SHOULD | [`http.content-type`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#http.content-type) responses declare a JSON media type |  |
| ✓ | SHOULD | [`http.models`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#http.models) GET /v1/models lists models |  |
| ✓ | MUST | [`auth.ignored-when-off`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#auth.ignored-when-off) without auth, an Authorization header is accepted |  |
| – | MUST | [`auth.bearer`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#auth.bearer) the key is read from Authorization: Bearer | no --key given (auth is off, or untested) |
| – | SHOULD | [`auth.missing`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#auth.missing) a missing key gets 401/403 with authentication_error | no --key given (auth is off, or untested) |
| – | SHOULD | [`auth.invalid`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#auth.invalid) a wrong key gets 401 with authentication_error | no --key given (auth is off, or untested) |
| ✓ | MUST | [`request.state`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#request.state) state may be a string, object or array |  |
| ✓ | MUST | [`request.model-alias`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#request.model-alias) model "jev-latest" is accepted |  |
| ✓ | MUST | [`request.multi`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#request.multi) several questions of mixed types in one request |  |
| ✓ | MUST | [`request.question-ids`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#request.question-ids) any non-empty string is a question id |  |
| ✓ | MUST | [`request.unicode`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#request.unicode) non-ASCII text is accepted and option names round-trip |  |
| ✗ | SHOULD | [`request.unknown-fields`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#request.unknown-fields) unknown top-level fields are ignored | valid request got 422: {"detail":[{"type":"extra_forbidden","loc":["body","x_trace_id"],"msg":"Extra inputs are not permitted","input":"jevcompat"},{"type":"ext… |
| ✓ | MUST | [`request.structured-text`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#request.structured-text) instructions and descriptions may be objects or arrays |  |
| ✓ | MUST | [`noul.criteria`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#noul.criteria) noul criteria may be absent, null, two- or one-sided |  |
| ✗ | SHOULD | [`noul.no-instructions`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#noul.no-instructions) a noul without instructions is accepted | valid request got 422: {"detail":[{"type":"missing","loc":["body","questions","threat","noul","instructions"],"msg":"Field required","input":{"type":"noul","cri… |
| ✓ | MUST | [`choice.null-description`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#choice.null-description) an option description may be null |  |
| ✗ | MUST | [`choice.options`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#choice.options) 2 to 255 options are accepted | valid request got 422: {"detail":[{"type":"too_long","loc":["body","questions","queue","choice","criteria"],"msg":"Dictionary should have at most 26 items after… |
| ✓ | MUST | [`score.levels`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#score.levels) 2 to 10 levels are accepted |  |
| ✓ | SHOULD | [`score.map-rejected`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#score.map-rejected) map-form score criteria are rejected with 4xx |  |
| ✓ | MUST | [`response.envelope`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#response.envelope) model, answers and usage are present |  |
| ✓ | MUST | [`response.usage`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#response.usage) token counts are non-negative integers |  |
| ✓ | MUST | [`response.answer-ids`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#response.answer-ids) one answer per question id, none extra |  |
| ✓ | MUST | [`response.answer-type`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#response.answer-type) each answer's type matches its question |  |
| ✓ | MUST | [`response.finite`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#response.finite) no NaN or Infinity |  |
| ✓ | SHOULD | [`response.extensions`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#response.extensions) extra fields are prefixed x_ |  |
| ✓ | MUST | [`noul.answer`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#noul.answer) noul is a probability in [0, 1] |  |
| ✓ | MUST | [`choice.answer`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#choice.answer) choice, probabilities and confidence are present |  |
| ✓ | MUST | [`choice.probability-keys`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#choice.probability-keys) probability keys are exactly the option names |  |
| ✓ | MUST | [`choice.distribution`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#choice.distribution) probabilities are in [0, 1] and sum to 1 |  |
| ✓ | MUST | [`choice.argmax`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#choice.argmax) choice is the most probable option |  |
| ✓ | MUST | [`score.answer`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#score.answer) score, legend, probabilities and confidence are present |  |
| ✓ | MUST | [`score.legend`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#score.legend) legend maps "0".."n-1" to the level descriptions |  |
| ✓ | MUST | [`score.probability-keys`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#score.probability-keys) probability keys are "0".."n-1" |  |
| ✓ | MUST | [`score.distribution`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#score.distribution) probabilities are in [0, 1] and sum to 1 |  |
| ✓ | MUST | [`score.expectation`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#score.expectation) score is the expectation of the probabilities |  |
| ✓ | MUST | [`confidence.range`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#confidence.range) confidence is in [0, 1] |  |
| ✓ | SHOULD | [`confidence.formula`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#confidence.formula) confidence follows the reference formula |  |
| ✓ | SHOULD | [`errors.json`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#errors.json) error bodies are JSON |  |
| ✓ | MUST | [`errors.no-5xx`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#errors.no-5xx) bad requests never get a 5xx |  |
| ✓ | SHOULD | [`errors.reject-invalid`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#errors.reject-invalid) invalid requests get a 4xx, not an answer |  |
| ✗ | SHOULD | [`errors.validation-shape`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#errors.validation-shape) validation errors are 422 with detail[] | body is not {"detail": [{"loc": ["body", …], "msg", "type"}]}: {"detail":"Unknown model 'jevcompat-no-such-model'. Use 'rizzo-latest', 'rizzo-spark-x2.5-1.7b-q8… |
| – | SHOULD | [`errors.shape`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#errors.shape) other errors carry detail.error_type and detail.message | not exercised: the server never produced the situation it covers |
| ✓ | MUST | [`semantics.question-id`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#semantics.question-id) renaming a question id does not change its answer |  |
| ✓ | SHOULD | [`semantics.batching`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#semantics.batching) other questions in the request do not change an answer |  |
| ✓ | SHOULD | [`semantics.question-order`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#semantics.question-order) question order does not change answers |  |
| ✓ | MUST | [`dropin.sdk-python`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#dropin.sdk-python) the official Python SDK parses every answer type |  |

## Failures

### [`request.unknown-fields`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#request.unknown-fields) (SHOULD) — unknown top-level fields are ignored

- **unknown-fields**: valid request got 422: {"detail":[{"type":"extra_forbidden","loc":["body","x_trace_id"],"msg":"Extra inputs are not permitted","input":"jevcompat"},{"type":"extra_forbidden","loc":["body","seed"],"msg":"Extra inputs are not… (224 bytes)

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"refund": {"type": "noul", "instructions": "Is the customer asking for money back?"}}, "model": "jev-latest", "x_trace_id": "jevcompat", "seed": 7, "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 422
  {"detail":[{"type":"extra_forbidden","loc":["body","x_trace_id"],"msg":"Extra inputs are not permitted","input":"jevcompat"},{"type":"extra_forbidden","loc":["body","seed"],"msg":"Extra inputs are not permitted","input":7}]}
  ```
  </details>


### [`noul.no-instructions`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#noul.no-instructions) (SHOULD) — a noul without instructions is accepted

- **noul-no-instructions**: valid request got 422: {"detail":[{"type":"missing","loc":["body","questions","threat","noul","instructions"],"msg":"Field required","input":{"type":"noul","criteria":{"true":"The customer threatens a chargeback","false":"N… (214 bytes)

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"threat": {"type": "noul", "criteria": {"true": "The customer threatens a chargeback", "false": "No threat"}}}, "model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 422
  {"detail":[{"type":"missing","loc":["body","questions","threat","noul","instructions"],"msg":"Field required","input":{"type":"noul","criteria":{"true":"The customer threatens a chargeback","false":"No threat"}}}]}
  ```
  </details>


### [`choice.options`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#choice.options) (MUST) — 2 to 255 options are accepted

- **choice-options:64**: valid request got 422: {"detail":[{"type":"too_long","loc":["body","questions","queue","choice","criteria"],"msg":"Dictionary should have at most 26 items after validation, not 64","input":{"Billing":"Payments, invoices, re… (2853 bytes)

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"queue": {"type": "choice", "instructions": "Which queue should this ticket go to?", "criteria": {"Billing": "Payments, invoices, refunds", "Queue 001": "Tickets routed to queue 1", "Queue 002": "Tickets routed to queue 2", "Queue 003": "Tickets routed to queue 3", "Queue 004": "Tickets routed to queue 4", "Queue 005": "Tickets routed to queue 5", "Queue 006": "Tickets routed to queue 6", "Queue 007": "Tickets routed to queue 7", "Queue 008": "Tickets routed to queue 8", "Queue 009": "Tickets routed to queue 9", "Queue 010": "Tickets routed to queue 10", "Queue 011": "Tickets routed to queue 11", "Queue 012": "Tickets routed to queue 12", "Queue 013": "Tickets routed to queue 13", "Queue 014": "Tickets routed to queue 14", "Queue 015": "Tickets routed to queue 15", "Queue 016": "Tickets routed to queue 16", "Queue 017": "Tickets routed to queue 17", "Queue 018": "Tickets routed to queue 18", "Queue 019": "Tickets routed to queue 19", "Queue 020": "Tickets routed to queue 20", "Queue 021": "Tickets routed to queue 21", "Queue 022": "Tickets routed to queue 22", "Queue 023": "Tickets routed to queue 23", "Queue 024": "Tickets routed to queue 24", "Queue 025": "Tickets routed to queue 25", "Queue 026": "Tickets routed to queue 26", "Queue 027": "Tickets routed to queue 27", "Queue 028": "Tickets routed to queue 28", "Queue 029": "Tickets routed to queue 29", "Queue 030": "Tickets routed to queue 30", "Queue 031": "Tickets routed to queue 31", "Queue 032": "Tickets… (2954 chars)
  → 422
  {"detail":[{"type":"too_long","loc":["body","questions","queue","choice","criteria"],"msg":"Dictionary should have at most 26 items after validation, not 64","input":{"Billing":"Payments, invoices, refunds","Queue 001":"Tickets routed to queue 1","Queue 002":"Tickets routed to queue 2","Queue 003":"Tickets routed to queue 3","Queue 004":"Tickets routed to queue 4","Queue 005":"Tickets routed to queue 5","Queue 006":"Tickets routed to queue 6","Queue 007":"Tickets routed to queue 7","Queue 008":"Tickets routed to queue 8","Queue 009":"Tickets routed to queue 9","Queue 010":"Tickets routed to queue 10","Queue 011":"Tickets routed to queue 11","Queue 012":"Tickets routed to queue 12","Queue 013":"Tickets routed to queue 13","Queue 014":"Tickets routed to queue 14","Queue 015":"Tickets routed to queue 15","Queue 016":"Tickets routed to queue 16","Queue 017":"Tickets routed to queue 17","Queue 018":"Tickets routed to queue 18","Queue 019":"Tickets routed to queue 19","Queue 020":"Tickets routed to queue 20","Queue 021":"Tickets routed to queue 21","Queue 022":"Tickets routed to queue 22","Queue 023":"Tickets routed to queue 23","Queue 024":"Tickets routed to queue 24","Queue 025":"Tickets routed to queue 25","Queue 026":"Tickets routed to queue 26","Queue 027":"Tickets routed to queue 27","Queue 028":"Tickets routed to queue 28","Queue 029":"Tickets routed to queue 29","Queue 030":"Tickets routed to queue 30","Queue 031":"Tickets routed to queue 31","Queue 032":"Tickets routed to … (2853 chars)
  ```
  </details>


### [`errors.validation-shape`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#errors.validation-shape) (SHOULD) — validation errors are 422 with detail[]

- **unknown-model**: body is not {"detail": [{"loc": ["body", …], "msg", "type"}]}: {"detail":"Unknown model 'jevcompat-no-such-model'. Use 'rizzo-latest', 'rizzo-spark-x2.5-1.7b-q8_0' or a jev-* alias."}

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"refund": {"type": "noul", "instructions": "Is the customer asking for money back?"}}, "model": "jevcompat-no-such-model", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 422
  {"detail":"Unknown model 'jevcompat-no-such-model'. Use 'rizzo-latest', 'rizzo-spark-x2.5-1.7b-q8_0' or a jev-* alias."}
  ```
  </details>



MUST 31/32 · SHOULD 9/12

