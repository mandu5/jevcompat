# Mapika/decider @ b44b4c9

[![jevcompat 0.1: 32/32 MUST](https://img.shields.io/badge/jevcompat%200.1-32%2F32%20MUST-brightgreen)](https://github.com/mandu5/jevcompat/blob/main/SPEC.md)

**conformant to spec 0.1: MUST 32/32, SHOULD 6/12** — jevcompat 0.1.0, 2026-09-23T23:06:17+00:00, 62 requests in 22.0s, model `jev-latest` (server reports `decider-0.8b-v1`), typesafe-sdk 0.7.1.

Observed limits: choice options accepted up to 255, score levels accepted up to 10

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
| ✓ | SHOULD | [`request.unknown-fields`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#request.unknown-fields) unknown top-level fields are ignored |  |
| ✓ | MUST | [`request.structured-text`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#request.structured-text) instructions and descriptions may be objects or arrays |  |
| ✓ | MUST | [`noul.criteria`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#noul.criteria) noul criteria may be absent, null, two- or one-sided |  |
| ✗ | SHOULD | [`noul.no-instructions`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#noul.no-instructions) a noul without instructions is accepted | valid request got 422: {"detail":"question without instructions"} |
| ✓ | MUST | [`choice.null-description`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#choice.null-description) an option description may be null |  |
| ✓ | MUST | [`choice.options`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#choice.options) 2 to 255 options are accepted |  |
| ✓ | MUST | [`score.levels`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#score.levels) 2 to 10 levels are accepted |  |
| ✗ | SHOULD | [`score.map-rejected`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#score.map-rejected) map-form score criteria are rejected with 4xx | invalid request was answered with 200 |
| ✓ | MUST | [`response.envelope`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#response.envelope) model, answers and usage are present |  |
| ✓ | MUST | [`response.usage`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#response.usage) token counts are non-negative integers |  |
| ✓ | MUST | [`response.answer-ids`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#response.answer-ids) one answer per question id, none extra |  |
| ✓ | MUST | [`response.answer-type`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#response.answer-type) each answer's type matches its question |  |
| ✓ | MUST | [`response.finite`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#response.finite) no NaN or Infinity |  |
| ✗ | SHOULD | [`response.extensions`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#response.extensions) extra fields are prefixed x_ | unprefixed field(s) certainty |
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
| ✗ | SHOULD | [`confidence.formula`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#confidence.formula) confidence follows the reference formula | confidence is 0.576; the reference formulas give 0.364 (distance) or 0.364 (top probability) |
| ✓ | SHOULD | [`errors.json`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#errors.json) error bodies are JSON |  |
| ✓ | MUST | [`errors.no-5xx`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#errors.no-5xx) bad requests never get a 5xx |  |
| ✗ | SHOULD | [`errors.reject-invalid`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#errors.reject-invalid) invalid requests get a 4xx, not an answer | invalid request was answered with 200 |
| ✗ | SHOULD | [`errors.validation-shape`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#errors.validation-shape) validation errors are 422 with detail[] | body is not {"detail": [{"loc": ["body", …], "msg", "type"}]}: {"detail":"choice criteria: a map of 2..255 options"} |
| – | SHOULD | [`errors.shape`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#errors.shape) other errors carry detail.error_type and detail.message | not exercised: the server never produced the situation it covers |
| ✓ | MUST | [`semantics.question-id`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#semantics.question-id) renaming a question id does not change its answer |  |
| ✓ | SHOULD | [`semantics.batching`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#semantics.batching) other questions in the request do not change an answer |  |
| ✓ | SHOULD | [`semantics.question-order`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#semantics.question-order) question order does not change answers |  |
| ✓ | MUST | [`dropin.sdk-python`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#dropin.sdk-python) the official Python SDK parses every answer type |  |

## Failures

### [`noul.no-instructions`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#noul.no-instructions) (SHOULD) — a noul without instructions is accepted

- **noul-no-instructions**: valid request got 422: {"detail":"question without instructions"}

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"threat": {"type": "noul", "criteria": {"true": "The customer threatens a chargeback", "false": "No threat"}}}, "model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 422
  {"detail":"question without instructions"}
  ```
  </details>


### [`score.map-rejected`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#score.map-rejected) (SHOULD) — map-form score criteria are rejected with 4xx

- **invalid:score-map**: invalid request was answered with 200

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"anger": {"type": "score", "instructions": "How frustrated?", "criteria": {"0": "Calm", "1": "Frustrated", "2": "Very angry"}}}, "model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 200
  {"model":"decider-0.8b-v1","answers":{"anger":{"type":"score","score":1.4,"confidence":0.602,"certainty":0.3809,"legend":{"0":"Calm","1":"Frustrated","2":"Very angry"},"probabilities":{"0":0.0012,"1":0.602,"2":0.3969},"level_fit":{"0":0.0011,"1":0.5697,"2":0.3756},"fit_mass":0.9464}},"usage":{"input_tokens":138,"output_tokens":0}}
  ```
  </details>


### [`response.extensions`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#response.extensions) (SHOULD) — extra fields are prefixed x_

- **choice-basic** `answers['team']`: unprefixed field(s) certainty

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"team": {"type": "choice", "instructions": "Which team should handle this ticket?", "criteria": {"Billing": "Payments, invoices, refunds", "Technical": "Bugs, outages, integrations", "Sales": "Pricing questions, upgrades, new contracts"}}}, "model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 200
  {"model":"decider-0.8b-v1","answers":{"team":{"type":"choice","choice":"Billing","confidence":0.9998,"certainty":0.9979,"probabilities":{"Billing":0.9998,"Technical":0.0001,"Sales":0.0001}}},"usage":{"input_tokens":105,"output_tokens":0}}
  ```
  </details>

- **choice-null-description** `answers['team']`: unprefixed field(s) certainty

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"team": {"type": "choice", "instructions": "Which team should handle this ticket?", "criteria": {"Billing": null, "Technical": null, "Sales": null}}}, "model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 200
  {"model":"decider-0.8b-v1","answers":{"team":{"type":"choice","choice":"Billing","confidence":0.9996,"certainty":0.9963,"probabilities":{"Billing":0.9996,"Technical":0.0003,"Sales":0.0001}}},"usage":{"input_tokens":83,"output_tokens":0}}
  ```
  </details>

- **choice-options:2** `answers['queue']`: unprefixed field(s) certainty

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"queue": {"type": "choice", "instructions": "Which queue should this ticket go to?", "criteria": {"Billing": "Payments, invoices, refunds", "Technical": "Bugs and outages"}}}, "model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 200
  {"model":"decider-0.8b-v1","answers":{"queue":{"type":"choice","choice":"Billing","confidence":0.9998,"certainty":0.9971,"probabilities":{"Billing":0.9998,"Technical":0.0002}}},"usage":{"input_tokens":91,"output_tokens":0}}
  ```
  </details>

- … and 16 more

### [`confidence.formula`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#confidence.formula) (SHOULD) — confidence follows the reference formula

- **score-levels:3** `answers['anger']`: confidence is 0.576; the reference formulas give 0.364 (distance) or 0.364 (top probability)

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"anger": {"type": "score", "instructions": "How frustrated is the customer?", "criteria": ["Calm", "Frustrated", "Very angry"]}}, "model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 200
  {"model":"decider-0.8b-v1","answers":{"anger":{"type":"score","score":1.42,"confidence":0.5758,"certainty":0.3732,"legend":{"0":"Calm","1":"Frustrated","2":"Very angry"},"probabilities":{"0":0.001,"1":0.5758,"2":0.4232},"level_fit":{"0":0.001,"1":0.5604,"2":0.4118},"fit_mass":0.9732}},"usage":{"input_tokens":141,"output_tokens":0}}
  ```
  </details>

- **score-levels:5** `answers['anger']`: confidence is 0.273; the reference formulas give 0.216 (distance) or 0.092 (top probability)

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"anger": {"type": "score", "instructions": "How frustrated is the customer?", "criteria": ["Level 0: calm", "Level 1: angrier", "Level 2: angrier", "Level 3: angrier", "Level 4: angrier"]}}, "model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 200
  {"model":"decider-0.8b-v1","answers":{"anger":{"type":"score","score":2.45,"confidence":0.2734,"certainty":0.1399,"legend":{"0":"Level 0: calm","1":"Level 1: angrier","2":"Level 2: angrier","3":"Level 3: angrier","4":"Level 4: angrier"},"probabilities":{"0":0.0004,"1":0.2422,"2":0.2734,"3":0.2705,"4":0.2135},"level_fit":{"0":0.0004,"1":0.2584,"2":0.2916,"3":0.2885,"4":0.2277},"fit_mass":1.0667}},"usage":{"input_tokens":199,"output_tokens":0}}
  ```
  </details>

- **score-levels:10** `answers['anger']`: confidence is 0.185; the reference formulas give 0.125 (distance) or 0.095 (top probability)

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"anger": {"type": "score", "instructions": "How frustrated is the customer?", "criteria": ["Level 0: calm", "Level 1: angrier", "Level 2: angrier", "Level 3: angrier", "Level 4: angrier", "Level 5: angrier", "Level 6: angrier", "Level 7: angrier", "Level 8: angrier", "Level 9: angrier"]}}, "model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 200
  {"model":"decider-0.8b-v1","answers":{"anger":{"type":"score","score":3.86,"confidence":0.1854,"certainty":0.096,"legend":{"0":"Level 0: calm","1":"Level 1: angrier","2":"Level 2: angrier","3":"Level 3: angrier","4":"Level 4: angrier","5":"Level 5: angrier","6":"Level 6: angrier","7":"Level 7: angrier","8":"Level 8: angrier","9":"Level 9: angrier"},"probabilities":{"0":0.0003,"1":0.1643,"2":0.1854,"3":0.1835,"4":0.1448,"5":0.0761,"6":0.067,"7":0.0656,"8":0.0652,"9":0.0478},"level_fit":{"0":0.0004,"1":0.2584,"2":0.2916,"3":0.2885,"4":0.2277,"5":0.1197,"6":0.1054,"7":0.1032,"8":0.1025,"9":0.0751},"fit_mass":1.5727}},"usage":{"input_tokens":329,"output_tokens":0}}
  ```
  </details>

- … and 5 more

### [`errors.reject-invalid`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#errors.reject-invalid) (SHOULD) — invalid requests get a 4xx, not an answer

- **invalid:empty-questions**: invalid request was answered with 200

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {}, "model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 200
  {"model":"decider-0.8b-v1","answers":{},"usage":{"input_tokens":0,"output_tokens":0}}
  ```
  </details>

- **invalid:score-map**: invalid request was answered with 200

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"anger": {"type": "score", "instructions": "How frustrated?", "criteria": {"0": "Calm", "1": "Frustrated", "2": "Very angry"}}}, "model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 200
  {"model":"decider-0.8b-v1","answers":{"anger":{"type":"score","score":1.4,"confidence":0.602,"certainty":0.3809,"legend":{"0":"Calm","1":"Frustrated","2":"Very angry"},"probabilities":{"0":0.0012,"1":0.602,"2":0.3969},"level_fit":{"0":0.0011,"1":0.5697,"2":0.3756},"fit_mass":0.9464}},"usage":{"input_tokens":138,"output_tokens":0}}
  ```
  </details>


### [`errors.validation-shape`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#errors.validation-shape) (SHOULD) — validation errors are 422 with detail[]

- **invalid:missing-type**: body is not {"detail": [{"loc": ["body", …], "msg", "type"}]}: {"detail":"choice criteria: a map of 2..255 options"}

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"refund": {"instructions": "Refund?"}}, "model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 422
  {"detail":"choice criteria: a map of 2..255 options"}
  ```
  </details>

- **invalid:type-boolean**: body is not {"detail": [{"loc": ["body", …], "msg", "type"}]}: {"detail":"unknown question type 'boolean'"}

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"refund": {"type": "boolean", "instructions": "Refund?"}}, "model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 422
  {"detail":"unknown question type 'boolean'"}
  ```
  </details>

- **invalid:choice-no-options**: body is not {"detail": [{"loc": ["body", …], "msg", "type"}]}: {"detail":"choice criteria: a map of 2..255 options"}

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"team": {"type": "choice", "instructions": "Team?", "criteria": {}}}, "model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 422
  {"detail":"choice criteria: a map of 2..255 options"}
  ```
  </details>

- … and 4 more


MUST 32/32 · SHOULD 6/12

