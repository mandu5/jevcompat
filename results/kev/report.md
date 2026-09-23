# jaredpalmer/kev @ 2874258

[![jevcompat 0.1: 32/32 MUST](https://img.shields.io/badge/jevcompat%200.1-32%2F32%20MUST-brightgreen)](https://github.com/mandu5/jevcompat/blob/main/SPEC.md)

**conformant to spec 0.1: MUST 32/32, SHOULD 10/12** — jevcompat 0.1.0, 2026-09-23T23:06:01+00:00, 62 requests in 6.2s, model `jev-latest` (server reports `jev-latest`), typesafe-sdk 0.7.1.

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
| ✓ | SHOULD | [`noul.no-instructions`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#noul.no-instructions) a noul without instructions is accepted |  |
| ✓ | MUST | [`choice.null-description`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#choice.null-description) an option description may be null |  |
| ✓ | MUST | [`choice.options`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#choice.options) 2 to 255 options are accepted |  |
| ✓ | MUST | [`score.levels`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#score.levels) 2 to 10 levels are accepted |  |
| ✓ | SHOULD | [`score.map-rejected`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#score.map-rejected) map-form score criteria are rejected with 4xx |  |
| ✓ | MUST | [`response.envelope`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#response.envelope) model, answers and usage are present |  |
| ✓ | MUST | [`response.usage`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#response.usage) token counts are non-negative integers |  |
| ✓ | MUST | [`response.answer-ids`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#response.answer-ids) one answer per question id, none extra |  |
| ✓ | MUST | [`response.answer-type`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#response.answer-type) each answer's type matches its question |  |
| ✓ | MUST | [`response.finite`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#response.finite) no NaN or Infinity |  |
| ✗ | SHOULD | [`response.extensions`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#response.extensions) extra fields are prefixed x_ | unprefixed top-level field(s) latency_ms |
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
| ✗ | SHOULD | [`confidence.formula`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#confidence.formula) confidence follows the reference formula | confidence is 0.932; the reference formulas give 0.864 (distance) or 0.864 (top probability) |
| ✓ | SHOULD | [`errors.json`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#errors.json) error bodies are JSON |  |
| ✓ | MUST | [`errors.no-5xx`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#errors.no-5xx) bad requests never get a 5xx |  |
| ✓ | SHOULD | [`errors.reject-invalid`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#errors.reject-invalid) invalid requests get a 4xx, not an answer |  |
| ✓ | SHOULD | [`errors.validation-shape`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#errors.validation-shape) validation errors are 422 with detail[] |  |
| – | SHOULD | [`errors.shape`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#errors.shape) other errors carry detail.error_type and detail.message | not exercised: the server never produced the situation it covers |
| ✓ | MUST | [`semantics.question-id`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#semantics.question-id) renaming a question id does not change its answer |  |
| ✓ | SHOULD | [`semantics.batching`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#semantics.batching) other questions in the request do not change an answer |  |
| ✓ | SHOULD | [`semantics.question-order`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#semantics.question-order) question order does not change answers |  |
| ✓ | MUST | [`dropin.sdk-python`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#dropin.sdk-python) the official Python SDK parses every answer type |  |

## Failures

### [`response.extensions`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#response.extensions) (SHOULD) — extra fields are prefixed x_

- **noul-basic**: unprefixed top-level field(s) latency_ms

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"refund": {"type": "noul", "instructions": "Is the customer asking for money back?"}}, "model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 200
  {"model":"jev-latest","answers":{"refund":{"type":"noul","noul":0.9523}},"usage":{"input_tokens":68,"output_tokens":22},"latency_ms":26.3}
  ```
  </details>

- **noul-criteria:both**: unprefixed top-level field(s) latency_ms

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"refund": {"type": "noul", "instructions": "Is the customer asking for money back?", "criteria": {"true": "They want a refund or chargeback", "false": "They want anything else"}}}, "model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 200
  {"model":"jev-latest","answers":{"refund":{"type":"noul","noul":0.8687}},"usage":{"input_tokens":81,"output_tokens":22},"latency_ms":29.8}
  ```
  </details>

- **noul-criteria:true-only**: unprefixed top-level field(s) latency_ms

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"refund": {"type": "noul", "instructions": "Is the customer asking for money back?", "criteria": {"true": "They want a refund or chargeback"}}}, "model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 200
  {"model":"jev-latest","answers":{"refund":{"type":"noul","noul":0.9357}},"usage":{"input_tokens":76,"output_tokens":22},"latency_ms":28.7}
  ```
  </details>

- … and 34 more

### [`confidence.formula`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#confidence.formula) (SHOULD) — confidence follows the reference formula

- **score-levels:2** `answers['anger']`: confidence is 0.932; the reference formulas give 0.864 (distance) or 0.864 (top probability)

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"anger": {"type": "score", "instructions": "How frustrated is the customer?", "criteria": ["Calm", "Very angry"]}}, "model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 200
  {"model":"jev-latest","answers":{"anger":{"type":"score","score":0.932,"legend":{"0":"Calm","1":"Very angry"},"probabilities":{"0":0.068,"1":0.932},"confidence":0.932}},"usage":{"input_tokens":68,"output_tokens":70},"latency_ms":216.5}
  ```
  </details>

- **score-levels:3** `answers['anger']`: confidence is 0.753; the reference formulas give 0.260 (distance) or 0.260 (top probability)

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"anger": {"type": "score", "instructions": "How frustrated is the customer?", "criteria": ["Calm", "Frustrated", "Very angry"]}}, "model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 200
  {"model":"jev-latest","answers":{"anger":{"type":"score","score":1.4394,"legend":{"0":"Calm","1":"Frustrated","2":"Very angry"},"probabilities":{"0":0.0269,"1":0.5069,"2":0.4662},"confidence":0.7535}},"usage":{"input_tokens":74,"output_tokens":94},"latency_ms":29.8}
  ```
  </details>

- **score-levels:5** `answers['anger']`: confidence is 0.615; the reference formulas give 0.000 (distance) or 0.084 (top probability)

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"anger": {"type": "score", "instructions": "How frustrated is the customer?", "criteria": ["Level 0: calm", "Level 1: angrier", "Level 2: angrier", "Level 3: angrier", "Level 4: angrier"]}}, "model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 200
  {"model":"jev-latest","answers":{"anger":{"type":"score","score":2.4611,"legend":{"0":"Level 0: calm","1":"Level 1: angrier","2":"Level 2: angrier","3":"Level 3: angrier","4":"Level 4: angrier"},"probabilities":{"0":0.0308,"1":0.2572,"2":0.1995,"3":0.2451,"4":0.2674},"confidence":0.6153}},"usage":{"input_tokens":99,"output_tokens":147},"latency_ms":36.6}
  ```
  </details>

- … and 6 more


MUST 32/32 · SHOULD 10/12

