# NandhaKishorM/laya @ 1e28ac2

[![jevcompat 0.1: 30/32 MUST](https://img.shields.io/badge/jevcompat%200.1-30%2F32%20MUST-orange)](https://github.com/mandu5/jevcompat/blob/main/SPEC.md)

**not conformant to spec 0.1: MUST 30/32, SHOULD 6/12** — jevcompat 0.1.0, 2026-09-23T23:05:46+00:00, 61 requests in 4.8s, model `jev-latest` (server reports `laya-rl-agent`), typesafe-sdk 0.7.1.

Observed limits: choice options accepted up to 64, choice options rejected at 128, score levels accepted up to 10

**Failed MUSTs:** [`choice.options`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#choice.options) — 2 to 255 options are accepted, [`score.legend`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#score.legend) — legend maps "0".."n-1" to the level descriptions

| | level | requirement | result |
|---|---|---|---|
| ✓ | MUST | [`http.endpoint`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#http.endpoint) POST /v1/systemone answers valid requests with 200 |  |
| ✓ | MUST | [`http.json`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#http.json) 200 bodies are JSON |  |
| ✓ | SHOULD | [`http.content-type`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#http.content-type) responses declare a JSON media type |  |
| ✗ | SHOULD | [`http.models`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#http.models) GET /v1/models lists models | GET /v1/models got 404 |
| ✓ | MUST | [`auth.ignored-when-off`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#auth.ignored-when-off) without auth, an Authorization header is accepted |  |
| – | MUST | [`auth.bearer`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#auth.bearer) the key is read from Authorization: Bearer | no --key given (auth is off, or untested) |
| – | SHOULD | [`auth.missing`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#auth.missing) a missing key gets 401/403 with authentication_error | no --key given (auth is off, or untested) |
| – | SHOULD | [`auth.invalid`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#auth.invalid) a wrong key gets 401 with authentication_error | no --key given (auth is off, or untested) |
| ✓ | MUST | [`request.state`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#request.state) state may be a string, object or array |  |
| ✓ | MUST | [`request.model-alias`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#request.model-alias) model "jev-latest" is accepted |  |
| ✓ | MUST | [`request.multi`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#request.multi) several questions of mixed types in one request |  |
| ✓ | MUST | [`request.question-ids`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#request.question-ids) any non-empty string is a question id |  |
| ✓ | MUST | [`request.unicode`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#request.unicode) non-ASCII text is accepted and option names round-trip |  |
| ✓ | SHOULD | [`request.unknown-fields`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#request.unknown-fields) unknown top-level fields are ignored |  |
| ✓ | MUST | [`request.structured-text`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#request.structured-text) instructions and descriptions may be objects or arrays |  |
| ✓ | MUST | [`noul.criteria`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#noul.criteria) noul criteria may be absent, null, two- or one-sided |  |
| ✗ | SHOULD | [`noul.no-instructions`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#noul.no-instructions) a noul without instructions is accepted | valid request got 422: {"detail":"question 'threat': no 'instructions'; add the text the model should answer"} |
| ✓ | MUST | [`choice.null-description`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#choice.null-description) an option description may be null |  |
| ✗ | MUST | [`choice.options`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#choice.options) 2 to 255 options are accepted | valid request got 422: {"detail":"question 'queue' options exceed head_max_len=192"} |
| ✓ | MUST | [`score.levels`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#score.levels) 2 to 10 levels are accepted |  |
| ✓ | SHOULD | [`score.map-rejected`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#score.map-rejected) map-form score criteria are rejected with 4xx |  |
| ✓ | MUST | [`response.envelope`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#response.envelope) model, answers and usage are present |  |
| ✓ | MUST | [`response.usage`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#response.usage) token counts are non-negative integers |  |
| ✓ | MUST | [`response.answer-ids`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#response.answer-ids) one answer per question id, none extra |  |
| ✓ | MUST | [`response.answer-type`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#response.answer-type) each answer's type matches its question |  |
| ✓ | MUST | [`response.finite`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#response.finite) no NaN or Infinity |  |
| ✗ | SHOULD | [`response.extensions`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#response.extensions) extra fields are prefixed x_ | unprefixed top-level field(s) routing |
| ✓ | MUST | [`noul.answer`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#noul.answer) noul is a probability in [0, 1] |  |
| ✓ | MUST | [`choice.answer`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#choice.answer) choice, probabilities and confidence are present |  |
| ✓ | MUST | [`choice.probability-keys`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#choice.probability-keys) probability keys are exactly the option names |  |
| ✓ | MUST | [`choice.distribution`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#choice.distribution) probabilities are in [0, 1] and sum to 1 |  |
| ✓ | MUST | [`choice.argmax`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#choice.argmax) choice is the most probable option |  |
| ✓ | MUST | [`score.answer`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#score.answer) score, legend, probabilities and confidence are present |  |
| ✗ | MUST | [`score.legend`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#score.legend) legend maps "0".."n-1" to the level descriptions | legend['1'] is a null legend value, which the official SDK rejects |
| ✓ | MUST | [`score.probability-keys`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#score.probability-keys) probability keys are "0".."n-1" |  |
| ✓ | MUST | [`score.distribution`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#score.distribution) probabilities are in [0, 1] and sum to 1 |  |
| ✓ | MUST | [`score.expectation`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#score.expectation) score is the expectation of the probabilities |  |
| ✓ | MUST | [`confidence.range`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#confidence.range) confidence is in [0, 1] |  |
| ✗ | SHOULD | [`confidence.formula`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#confidence.formula) confidence follows the reference formula | confidence is 0.922; the reference formula gives 0.978 |
| ✓ | SHOULD | [`errors.json`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#errors.json) error bodies are JSON |  |
| ✓ | MUST | [`errors.no-5xx`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#errors.no-5xx) bad requests never get a 5xx |  |
| ✗ | SHOULD | [`errors.reject-invalid`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#errors.reject-invalid) invalid requests get a 4xx, not an answer | invalid request was answered with 200 |
| ✗ | SHOULD | [`errors.validation-shape`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#errors.validation-shape) validation errors are 422 with detail[] | status 400; validation failures use 422 |
| – | SHOULD | [`errors.shape`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#errors.shape) other errors carry detail.error_type and detail.message | not exercised: the server never produced the situation it covers |
| ✓ | MUST | [`semantics.question-id`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#semantics.question-id) renaming a question id does not change its answer |  |
| ✓ | SHOULD | [`semantics.batching`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#semantics.batching) other questions in the request do not change an answer |  |
| ✓ | SHOULD | [`semantics.question-order`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#semantics.question-order) question order does not change answers |  |
| ✓ | MUST | [`dropin.sdk-python`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#dropin.sdk-python) the official Python SDK parses every answer type |  |

## Failures

### [`http.models`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#http.models) (SHOULD) — GET /v1/models lists models

- **models-endpoint**: GET /v1/models got 404

  <details><summary>exchange</summary>

  ```
  GET /v1/models
  
  → 404
  {"detail":"Not Found"}
  ```
  </details>


### [`noul.no-instructions`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#noul.no-instructions) (SHOULD) — a noul without instructions is accepted

- **noul-no-instructions**: valid request got 422: {"detail":"question 'threat': no 'instructions'; add the text the model should answer"}

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"threat": {"type": "noul", "criteria": {"true": "The customer threatens a chargeback", "false": "No threat"}}}, "model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 422
  {"detail":"question 'threat': no 'instructions'; add the text the model should answer"}
  ```
  </details>


### [`choice.options`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#choice.options) (MUST) — 2 to 255 options are accepted

- **choice-options:128**: valid request got 422: {"detail":"question 'queue' options exceed head_max_len=192"}

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"queue": {"type": "choice", "instructions": "Which queue should this ticket go to?", "criteria": {"Billing": "Payments, invoices, refunds", "Queue 001": "Tickets routed to queue 1", "Queue 002": "Tickets routed to queue 2", "Queue 003": "Tickets routed to queue 3", "Queue 004": "Tickets routed to queue 4", "Queue 005": "Tickets routed to queue 5", "Queue 006": "Tickets routed to queue 6", "Queue 007": "Tickets routed to queue 7", "Queue 008": "Tickets routed to queue 8", "Queue 009": "Tickets routed to queue 9", "Queue 010": "Tickets routed to queue 10", "Queue 011": "Tickets routed to queue 11", "Queue 012": "Tickets routed to queue 12", "Queue 013": "Tickets routed to queue 13", "Queue 014": "Tickets routed to queue 14", "Queue 015": "Tickets routed to queue 15", "Queue 016": "Tickets routed to queue 16", "Queue 017": "Tickets routed to queue 17", "Queue 018": "Tickets routed to queue 18", "Queue 019": "Tickets routed to queue 19", "Queue 020": "Tickets routed to queue 20", "Queue 021": "Tickets routed to queue 21", "Queue 022": "Tickets routed to queue 22", "Queue 023": "Tickets routed to queue 23", "Queue 024": "Tickets routed to queue 24", "Queue 025": "Tickets routed to queue 25", "Queue 026": "Tickets routed to queue 26", "Queue 027": "Tickets routed to queue 27", "Queue 028": "Tickets routed to queue 28", "Queue 029": "Tickets routed to queue 29", "Queue 030": "Tickets routed to queue 30", "Queue 031": "Tickets routed to queue 31", "Queue 032": "Tickets… (5734 chars)
  → 422
  {"detail":"question 'queue' options exceed head_max_len=192"}
  ```
  </details>


### [`response.extensions`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#response.extensions) (SHOULD) — extra fields are prefixed x_

- **noul-basic**: unprefixed top-level field(s) routing

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"refund": {"type": "noul", "instructions": "Is the customer asking for money back?"}}, "model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 200
  {"model":"laya-rl-agent","answers":{"refund":{"type":"noul","noul":0.8593,"confidence":0.8593,"action":{"act_probability":1.0}}},"usage":{"input_tokens":83,"output_tokens":0},"routing":{"model":"english","repo":"convaiinnovations/laya","reason":"English Latin text","detection":{"script":"latin","script_profile":{"latin":1.0},"language":"en","is_english":true,"language_undecided":false,"diacritic_rate":0.0,"non_latin_fraction":0.0},"workflow":null}}
  ```
  </details>

- **noul-basic** `answers['refund']`: unprefixed field(s) action, confidence

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"refund": {"type": "noul", "instructions": "Is the customer asking for money back?"}}, "model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 200
  {"model":"laya-rl-agent","answers":{"refund":{"type":"noul","noul":0.8593,"confidence":0.8593,"action":{"act_probability":1.0}}},"usage":{"input_tokens":83,"output_tokens":0},"routing":{"model":"english","repo":"convaiinnovations/laya","reason":"English Latin text","detection":{"script":"latin","script_profile":{"latin":1.0},"language":"en","is_english":true,"language_undecided":false,"diacritic_rate":0.0,"non_latin_fraction":0.0},"workflow":null}}
  ```
  </details>

- **noul-criteria:both**: unprefixed top-level field(s) routing

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"refund": {"type": "noul", "instructions": "Is the customer asking for money back?", "criteria": {"true": "They want a refund or chargeback", "false": "They want anything else"}}}, "model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 200
  {"model":"laya-rl-agent","answers":{"refund":{"type":"noul","noul":0.8259,"confidence":0.8259,"action":{"act_probability":1.0}}},"usage":{"input_tokens":82,"output_tokens":0},"routing":{"model":"english","repo":"convaiinnovations/laya","reason":"English Latin text","detection":{"script":"latin","script_profile":{"latin":1.0},"language":"en","is_english":true,"language_undecided":false,"diacritic_rate":0.0,"non_latin_fraction":0.0},"workflow":null}}
  ```
  </details>

- … and 68 more

### [`score.legend`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#score.legend) (MUST) — legend maps "0".."n-1" to the level descriptions

- **out-of-range:score-null-level** `answers['anger']`: legend['1'] is a null legend value, which the official SDK rejects

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"anger": {"type": "score", "instructions": "Frustration?", "criteria": ["Calm", null]}}, "model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 200
  {"model":"laya-rl-agent","answers":{"anger":{"type":"score","score":0.853,"legend":{"0":"Calm","1":null},"probabilities":{"0":0.147,"1":0.853},"confidence":0.3977,"action":{"act_probability":1.0}}},"usage":{"input_tokens":70,"output_tokens":0},"routing":{"model":"english","repo":"convaiinnovations/laya","reason":"English Latin text","detection":{"script":"latin","script_profile":{"latin":1.0},"language":"en","is_english":true,"language_undecided":false,"diacritic_rate":0.0,"non_latin_fraction":0.0},"workflow":null}}
  ```
  </details>


### [`confidence.formula`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#confidence.formula) (SHOULD) — confidence follows the reference formula

- **choice-basic** `answers['team']`: confidence is 0.922; the reference formula gives 0.978

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"team": {"type": "choice", "instructions": "Which team should handle this ticket?", "criteria": {"Billing": "Payments, invoices, refunds", "Technical": "Bugs, outages, integrations", "Sales": "Pricing questions, upgrades, new contracts"}}}, "model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 200
  {"model":"laya-rl-agent","answers":{"team":{"type":"choice","choice":"Billing","probabilities":{"Billing":0.9856,"Technical":0.0066,"Sales":0.0078},"confidence":0.9224,"action":{"act_probability":1.0}}},"usage":{"input_tokens":98,"output_tokens":0},"routing":{"model":"english","repo":"convaiinnovations/laya","reason":"English Latin text","detection":{"script":"latin","script_profile":{"latin":1.0},"language":"en","is_english":true,"language_undecided":false,"diacritic_rate":0.0,"non_latin_fraction":0.0},"workflow":null}}
  ```
  </details>

- **choice-null-description** `answers['team']`: confidence is 0.701; the reference formula gives 0.883

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"team": {"type": "choice", "instructions": "Which team should handle this ticket?", "criteria": {"Billing": null, "Technical": null, "Sales": null}}}, "model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 200
  {"model":"laya-rl-agent","answers":{"team":{"type":"choice","choice":"Billing","probabilities":{"Billing":0.9218,"Technical":0.0364,"Sales":0.0418},"confidence":0.7012,"action":{"act_probability":1.0}}},"usage":{"input_tokens":70,"output_tokens":0},"routing":{"model":"english","repo":"convaiinnovations/laya","reason":"English Latin text","detection":{"script":"latin","script_profile":{"latin":1.0},"language":"en","is_english":true,"language_undecided":false,"diacritic_rate":0.0,"non_latin_fraction":0.0},"workflow":null}}
  ```
  </details>

- **choice-options:2** `answers['queue']`: confidence is 0.754; the reference formula gives 0.918

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"queue": {"type": "choice", "instructions": "Which queue should this ticket go to?", "criteria": {"Billing": "Payments, invoices, refunds", "Technical": "Bugs and outages"}}}, "model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 200
  {"model":"laya-rl-agent","answers":{"queue":{"type":"choice","choice":"Billing","probabilities":{"Billing":0.9592,"Technical":0.0408},"confidence":0.7539,"action":{"act_probability":1.0}}},"usage":{"input_tokens":84,"output_tokens":0},"routing":{"model":"english","repo":"convaiinnovations/laya","reason":"English Latin text","detection":{"script":"latin","script_profile":{"latin":1.0},"language":"en","is_english":true,"language_undecided":false,"diacritic_rate":0.0,"non_latin_fraction":0.0},"workflow":null}}
  ```
  </details>

- … and 13 more

### [`errors.reject-invalid`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#errors.reject-invalid) (SHOULD) — invalid requests get a 4xx, not an answer

- **invalid:missing-state**: invalid request was answered with 200

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"refund": {"type": "noul", "instructions": "Is the customer asking for money back?"}}, "model": "jev-latest"}
  → 200
  {"model":"laya-rl-agent","answers":{"refund":{"type":"noul","noul":0.1109,"confidence":0.8891,"action":{"act_probability":1.0}}},"usage":{"input_tokens":35,"output_tokens":0},"routing":{"model":"english","repo":"convaiinnovations/laya","reason":"no letters detected in state; using default (english)","detection":{"script":"unknown","script_profile":{},"language":null,"is_english":true,"language_undecided":true,"diacritic_rate":0.0,"non_latin_fraction":0.0},"workflow":null}}
  ```
  </details>

- **invalid:empty-questions**: invalid request was answered with 200

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {}, "model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 200
  {"model":"laya-rl-agent","answers":{},"usage":{"input_tokens":0,"output_tokens":0},"routing":{"model":"english","repo":"convaiinnovations/laya","reason":"English Latin text","detection":{"script":"latin","script_profile":{"latin":1.0},"language":"en","is_english":true,"language_undecided":false,"diacritic_rate":0.0,"non_latin_fraction":0.0},"workflow":null}}
  ```
  </details>


### [`errors.validation-shape`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#errors.validation-shape) (SHOULD) — validation errors are 422 with detail[]

- **invalid:not-json**: status 400; validation failures use 422

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"model": "jev-latest", "state": "x", "questions": {
  → 400
  {"detail":"request body must be valid JSON"}
  ```
  </details>

- **invalid:not-json**: body is not {"detail": [{"loc": ["body", …], "msg", "type"}]}: {"detail":"request body must be valid JSON"}

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"model": "jev-latest", "state": "x", "questions": {
  → 400
  {"detail":"request body must be valid JSON"}
  ```
  </details>

- **invalid:missing-questions**: status 400; validation failures use 422

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 400
  {"detail":"request body must be an object with a 'questions' field"}
  ```
  </details>

- … and 6 more


MUST 30/32 · SHOULD 6/12

