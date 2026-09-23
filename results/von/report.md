# wfzyx/von @ 657f42f

[![jevcompat 0.1: 31/32 MUST](https://img.shields.io/badge/jevcompat%200.1-31%2F32%20MUST-orange)](https://github.com/mandu5/jevcompat/blob/main/SPEC.md)

**not conformant to spec 0.1: MUST 31/32, SHOULD 8/12** — jevcompat 0.1.0, 2026-09-23T23:06:44+00:00, 62 requests in 9.8s, model `jev-latest` (server reports `von-1.1.0`), typesafe-sdk 0.7.1.

Observed limits: choice options accepted up to 255, score levels accepted up to 10

**Failed MUSTs:** [`request.structured-text`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#request.structured-text) — instructions and descriptions may be objects or arrays

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
| ✗ | MUST | [`request.structured-text`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#request.structured-text) instructions and descriptions may be objects or arrays | valid request got 422: {"detail":"3 validation errors for Noul\ninstructions\n  Input should be a valid string [type=string_type, input_value={'task': 'Decide w… |
| ✓ | MUST | [`noul.criteria`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#noul.criteria) noul criteria may be absent, null, two- or one-sided |  |
| ✗ | SHOULD | [`noul.no-instructions`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#noul.no-instructions) a noul without instructions is accepted | valid request got 422: {"detail":"1 validation error for Noul\ninstructions\n  Field required [type=missing, input_value={'type': 'noul', 'criteri..., 'false': … |
| ✓ | MUST | [`choice.null-description`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#choice.null-description) an option description may be null |  |
| ✓ | MUST | [`choice.options`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#choice.options) 2 to 255 options are accepted |  |
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
| ✗ | SHOULD | [`confidence.formula`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#confidence.formula) confidence follows the reference formula | confidence is 0.012; the reference formula gives 0.044 |
| ✓ | SHOULD | [`errors.json`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#errors.json) error bodies are JSON |  |
| ✓ | MUST | [`errors.no-5xx`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#errors.no-5xx) bad requests never get a 5xx |  |
| ✗ | SHOULD | [`errors.reject-invalid`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#errors.reject-invalid) invalid requests get a 4xx, not an answer | invalid request was answered with 200 |
| ✗ | SHOULD | [`errors.validation-shape`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#errors.validation-shape) validation errors are 422 with detail[] | body is not {"detail": [{"loc": ["body", …], "msg", "type"}]}: {"detail":"1 validation error for Choice\ncriteria\n  Field required [type=missing, input_value={… |
| – | SHOULD | [`errors.shape`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#errors.shape) other errors carry detail.error_type and detail.message | not exercised: the server never produced the situation it covers |
| ✓ | MUST | [`semantics.question-id`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#semantics.question-id) renaming a question id does not change its answer |  |
| ✓ | SHOULD | [`semantics.batching`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#semantics.batching) other questions in the request do not change an answer |  |
| ✓ | SHOULD | [`semantics.question-order`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#semantics.question-order) question order does not change answers |  |
| ✓ | MUST | [`dropin.sdk-python`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#dropin.sdk-python) the official Python SDK parses every answer type |  |

## Failures

### [`request.structured-text`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#request.structured-text) (MUST) — instructions and descriptions may be objects or arrays

- **structured-text:noul**: valid request got 422: {"detail":"3 validation errors for Noul\ninstructions\n  Input should be a valid string [type=string_type, input_value={'task': 'Decide whether ...efunds', 'chargebacks']}, input_type=dict]\n    For f… (731 bytes)

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"q": {"type": "noul", "instructions": {"task": "Decide whether the customer wants money back", "include": ["refunds", "chargebacks"]}, "criteria": {"true": {"examples": ["refund me", "I'll dispute this"]}, "false": ["questions", "complaints without a request"]}}}, "model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 422
  {"detail":"3 validation errors for Noul\ninstructions\n  Input should be a valid string [type=string_type, input_value={'task': 'Decide whether ...efunds', 'chargebacks']}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.13/v/string_type\ncriteria.true\n  Input should be a valid string [type=string_type, input_value={'examples': ['refund me', \"I'll dispute this\"]}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.13/v/string_type\ncriteria.false\n  Input should be a valid string [type=string_type, input_value=['questions', 'complaints without a request'], input_type=list]\n    For further information visit https://errors.pydantic.dev/2.13/v/string_type"}
  ```
  </details>

- **structured-text:choice**: valid request got 422: {"detail":"3 validation errors for Choice\ninstructions\n  Input should be a valid string [type=string_type, input_value=['Route the ticket.', 'Pick exactly one team.'], input_type=list]\n    For furt… (692 bytes)

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"q": {"type": "choice", "instructions": ["Route the ticket.", "Pick exactly one team."], "criteria": {"Billing": {"owns": ["invoices", "refunds"]}, "Technical": ["bugs", "outages"], "Sales": "Pricing"}}}, "model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 422
  {"detail":"3 validation errors for Choice\ninstructions\n  Input should be a valid string [type=string_type, input_value=['Route the ticket.', 'Pick exactly one team.'], input_type=list]\n    For further information visit https://errors.pydantic.dev/2.13/v/string_type\ncriteria.Billing\n  Input should be a valid string [type=string_type, input_value={'owns': ['invoices', 'refunds']}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.13/v/string_type\ncriteria.Technical\n  Input should be a valid string [type=string_type, input_value=['bugs', 'outages'], input_type=list]\n    For further information visit https://errors.pydantic.dev/2.13/v/string_type"}
  ```
  </details>

- **structured-text:score**: valid request got 422: {"detail":"1 validation error for Score\ninstructions\n  Input should be a valid string [type=string_type, input_value={'scale': 'frustration'}, input_type=dict]\n    For further information visit htt… (245 bytes)

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"q": {"type": "score", "instructions": {"scale": "frustration"}, "criteria": [{"label": "Calm"}, {"label": "Frustrated"}, {"label": "Very angry", "signals": ["threats"]}]}}, "model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 422
  {"detail":"1 validation error for Score\ninstructions\n  Input should be a valid string [type=string_type, input_value={'scale': 'frustration'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.13/v/string_type"}
  ```
  </details>


### [`noul.no-instructions`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#noul.no-instructions) (SHOULD) — a noul without instructions is accepted

- **noul-no-instructions**: valid request got 422: {"detail":"1 validation error for Noul\ninstructions\n  Field required [type=missing, input_value={'type': 'noul', 'criteri..., 'false': 'No threat'}}, input_type=dict]\n    For further information vi… (248 bytes)

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"threat": {"type": "noul", "criteria": {"true": "The customer threatens a chargeback", "false": "No threat"}}}, "model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 422
  {"detail":"1 validation error for Noul\ninstructions\n  Field required [type=missing, input_value={'type': 'noul', 'criteri..., 'false': 'No threat'}}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.13/v/missing"}
  ```
  </details>


### [`confidence.formula`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#confidence.formula) (SHOULD) — confidence follows the reference formula

- **choice-null-description** `answers['team']`: confidence is 0.012; the reference formula gives 0.044

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"team": {"type": "choice", "instructions": "Which team should handle this ticket?", "criteria": {"Billing": null, "Technical": null, "Sales": null}}}, "model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 200
  {"model":"von-1.1.0","answers":{"team":{"type":"choice","choice":"Technical","probabilities":{"Billing":0.2861,"Technical":0.3629,"Sales":0.351},"confidence":0.012}},"usage":{"input_tokens":61,"output_tokens":1}}
  ```
  </details>

- **score-levels:3** `answers['anger']`: confidence is 0.394; the reference formulas give 0.430 (distance) or 0.431 (top probability)

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"anger": {"type": "score", "instructions": "How frustrated is the customer?", "criteria": ["Calm", "Frustrated", "Very angry"]}}, "model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 200
  {"model":"von-1.1.0","answers":{"anger":{"type":"score","score":1.07,"confidence":0.394,"legend":{"0":"Calm","1":"Frustrated","2":"Very angry"},"probabilities":{"0":0.1534,"1":0.6204,"2":0.2263}}},"usage":{"input_tokens":59,"output_tokens":1}}
  ```
  </details>

- **score-levels:10** `answers['anger']`: confidence is 0.042; the reference formulas give 0.000 (distance) or 0.253 (top probability)

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"anger": {"type": "score", "instructions": "How frustrated is the customer?", "criteria": ["Level 0: calm", "Level 1: angrier", "Level 2: angrier", "Level 3: angrier", "Level 4: angrier", "Level 5: angrier", "Level 6: angrier", "Level 7: angrier", "Level 8: angrier", "Level 9: angrier"]}}, "model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 200
  {"model":"von-1.1.0","answers":{"anger":{"type":"score","score":4.27,"confidence":0.042,"legend":{"0":"Level 0: calm","1":"Level 1: angrier","2":"Level 2: angrier","3":"Level 3: angrier","4":"Level 4: angrier","5":"Level 5: angrier","6":"Level 6: angrier","7":"Level 7: angrier","8":"Level 8: angrier","9":"Level 9: angrier"},"probabilities":{"0":0.0,"1":0.3281,"2":0.0011,"3":0.001,"4":0.0123,"5":0.2858,"6":0.1441,"7":0.2225,"8":0.0052,"9":0.0}}},"usage":{"input_tokens":59,"output_tokens":1}}
  ```
  </details>

- … and 4 more

### [`errors.reject-invalid`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#errors.reject-invalid) (SHOULD) — invalid requests get a 4xx, not an answer

- **invalid:empty-questions**: invalid request was answered with 200

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {}, "model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 200
  {"model":"von-1.1.0","answers":{},"usage":{"input_tokens":53,"output_tokens":0}}
  ```
  </details>

- **invalid:choice-no-options**: invalid request was answered with 200

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"team": {"type": "choice", "instructions": "Team?", "criteria": {}}}, "model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 200
  {"model":"von-1.1.0","answers":{"team":{"type":"choice","choice":"","probabilities":{},"confidence":0.0}},"usage":{"input_tokens":53,"output_tokens":1}}
  ```
  </details>


### [`errors.validation-shape`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#errors.validation-shape) (SHOULD) — validation errors are 422 with detail[]

- **invalid:missing-type**: body is not {"detail": [{"loc": ["body", …], "msg", "type"}]}: {"detail":"1 validation error for Choice\ncriteria\n  Field required [type=missing, input_value={'instructions': 'Refund?'}, input_type=dict]\n    For further i… (221 bytes)

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"refund": {"instructions": "Refund?"}}, "model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 422
  {"detail":"1 validation error for Choice\ncriteria\n  Field required [type=missing, input_value={'instructions': 'Refund?'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.13/v/missing"}
  ```
  </details>

- **invalid:type-boolean**: body is not {"detail": [{"loc": ["body", …], "msg", "type"}]}: {"detail":"Unknown question type 'boolean'"}

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"refund": {"type": "boolean", "instructions": "Refund?"}}, "model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 422
  {"detail":"Unknown question type 'boolean'"}
  ```
  </details>

- **invalid:score-map**: body is not {"detail": [{"loc": ["body", …], "msg", "type"}]}: {"detail":"1 validation error for Score\ncriteria\n  Input should be a valid list [type=list_type, input_value={'0': 'Calm', '1': 'Frust...ted', '2': 'Very angr… (263 bytes)

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"anger": {"type": "score", "instructions": "How frustrated?", "criteria": {"0": "Calm", "1": "Frustrated", "2": "Very angry"}}}, "model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 422
  {"detail":"1 validation error for Score\ncriteria\n  Input should be a valid list [type=list_type, input_value={'0': 'Calm', '1': 'Frust...ted', '2': 'Very angry'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.13/v/list_type"}
  ```
  </details>

- … and 1 more


MUST 31/32 · SHOULD 8/12

