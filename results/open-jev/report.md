# Zefan-Cai/Open-Jev @ 3308a15

[![jevcompat 0.1: 31/32 MUST](https://img.shields.io/badge/jevcompat%200.1-31%2F32%20MUST-orange)](https://github.com/mandu5/jevcompat/blob/main/SPEC.md)

**not conformant to spec 0.1: MUST 31/32, SHOULD 9/12** — jevcompat 0.1.0, 2026-09-23T23:21:14+00:00, 62 requests in 114.5s, model `jev-latest` (server reports `Qwen/Qwen3.5-2B`), typesafe-sdk 0.7.1.

Observed limits: choice options accepted up to 255, score levels accepted up to 10

**Failed MUSTs:** [`noul.criteria`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#noul.criteria) — noul criteria may be absent, null, two- or one-sided

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
| ✗ | MUST | [`noul.criteria`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#noul.criteria) noul criteria may be absent, null, two- or one-sided | valid request got 422: {"error": "Noul criteria must contain true and false descriptions"} |
| ✗ | SHOULD | [`noul.no-instructions`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#noul.no-instructions) a noul without instructions is accepted | valid request got 422: {"error": "instructions and descriptions must be text, an object, or an array"} |
| ✓ | MUST | [`choice.null-description`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#choice.null-description) an option description may be null |  |
| ✓ | MUST | [`choice.options`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#choice.options) 2 to 255 options are accepted |  |
| ✓ | MUST | [`score.levels`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#score.levels) 2 to 10 levels are accepted |  |
| ✓ | SHOULD | [`score.map-rejected`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#score.map-rejected) map-form score criteria are rejected with 4xx |  |
| ✓ | MUST | [`response.envelope`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#response.envelope) model, answers and usage are present |  |
| ✓ | MUST | [`response.usage`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#response.usage) token counts are non-negative integers |  |
| ✓ | MUST | [`response.answer-ids`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#response.answer-ids) one answer per question id, none extra |  |
| ✓ | MUST | [`response.answer-type`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#response.answer-type) each answer's type matches its question |  |
| ✓ | MUST | [`response.finite`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#response.finite) no NaN or Infinity |  |
| ✗ | SHOULD | [`response.extensions`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#response.extensions) extra fields are prefixed x_ | unprefixed top-level field(s) metadata |
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
| ✗ | SHOULD | [`errors.validation-shape`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#errors.validation-shape) validation errors are 422 with detail[] | body is not {"detail": [{"loc": ["body", …], "msg", "type"}]}: {"error": "Expecting property name enclosed in double quotes: line 1 column 53 (char 52)"} |
| – | SHOULD | [`errors.shape`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#errors.shape) other errors carry detail.error_type and detail.message | not exercised: the server never produced the situation it covers |
| ✓ | MUST | [`semantics.question-id`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#semantics.question-id) renaming a question id does not change its answer |  |
| ✓ | SHOULD | [`semantics.batching`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#semantics.batching) other questions in the request do not change an answer |  |
| ✓ | SHOULD | [`semantics.question-order`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#semantics.question-order) question order does not change answers |  |
| ✓ | MUST | [`dropin.sdk-python`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#dropin.sdk-python) the official Python SDK parses every answer type |  |

## Failures

### [`noul.criteria`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#noul.criteria) (MUST) — noul criteria may be absent, null, two- or one-sided

- **noul-criteria:true-only**: valid request got 422: {"error": "Noul criteria must contain true and false descriptions"}

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"refund": {"type": "noul", "instructions": "Is the customer asking for money back?", "criteria": {"true": "They want a refund or chargeback"}}}, "model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 422
  {"error": "Noul criteria must contain true and false descriptions"}
  ```
  </details>

- **noul-criteria:false-only**: valid request got 422: {"error": "Noul criteria must contain true and false descriptions"}

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"refund": {"type": "noul", "instructions": "Is the customer asking for money back?", "criteria": {"false": "They are only asking a question"}}}, "model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 422
  {"error": "Noul criteria must contain true and false descriptions"}
  ```
  </details>


### [`noul.no-instructions`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#noul.no-instructions) (SHOULD) — a noul without instructions is accepted

- **noul-no-instructions**: valid request got 422: {"error": "instructions and descriptions must be text, an object, or an array"}

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"threat": {"type": "noul", "criteria": {"true": "The customer threatens a chargeback", "false": "No threat"}}}, "model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 422
  {"error": "instructions and descriptions must be text, an object, or an array"}
  ```
  </details>


### [`response.extensions`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#response.extensions) (SHOULD) — extra fields are prefixed x_

- **noul-basic**: unprefixed top-level field(s) metadata

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"refund": {"type": "noul", "instructions": "Is the customer asking for money back?"}}, "model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 200
  {"answers": {"refund": {"type": "noul", "noul": 0.4257804870866414}}, "model": "Qwen/Qwen3.5-2B", "usage": {"input_tokens": 91, "output_tokens": 0}, "metadata": {"method": "lora_decision_head", "temperature": 1.518796342858676, "candidate_sequences": 1, "inference_seconds": 0.22318775003077462, "prefix_cache": {"enabled": false, "mode": "independent_candidates"}, "checkpoint_sha256": "3076462e6356412082e79af909227b39b2863b90def79155ca0821aa506b7ded", "base_revision": "15852e8c16360a2fea060d615a32b45270f8a8fc", "max_length": 4096, "code_commit": "3308a15ccd7eea1df7a37d6ddc39b023b801ba16"}}
  ```
  </details>

- **noul-criteria:both**: unprefixed top-level field(s) metadata

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"refund": {"type": "noul", "instructions": "Is the customer asking for money back?", "criteria": {"true": "They want a refund or chargeback", "false": "They want anything else"}}}, "model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 200
  {"answers": {"refund": {"type": "noul", "noul": 0.8176431273941468}}, "model": "Qwen/Qwen3.5-2B", "usage": {"input_tokens": 110, "output_tokens": 0}, "metadata": {"method": "lora_decision_head", "temperature": 1.518796342858676, "candidate_sequences": 1, "inference_seconds": 0.26864312501857057, "prefix_cache": {"enabled": false, "mode": "independent_candidates"}, "checkpoint_sha256": "3076462e6356412082e79af909227b39b2863b90def79155ca0821aa506b7ded", "base_revision": "15852e8c16360a2fea060d615a32b45270f8a8fc", "max_length": 4096, "code_commit": "3308a15ccd7eea1df7a37d6ddc39b023b801ba16"}}
  ```
  </details>

- **noul-criteria:null**: unprefixed top-level field(s) metadata

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"refund": {"type": "noul", "instructions": "Is the customer asking for money back?", "criteria": null}}, "model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 200
  {"answers": {"refund": {"type": "noul", "noul": 0.4257804870866414}}, "model": "Qwen/Qwen3.5-2B", "usage": {"input_tokens": 91, "output_tokens": 0}, "metadata": {"method": "lora_decision_head", "temperature": 1.518796342858676, "candidate_sequences": 1, "inference_seconds": 0.22511300002224743, "prefix_cache": {"enabled": false, "mode": "independent_candidates"}, "checkpoint_sha256": "3076462e6356412082e79af909227b39b2863b90def79155ca0821aa506b7ded", "base_revision": "15852e8c16360a2fea060d615a32b45270f8a8fc", "max_length": 4096, "code_commit": "3308a15ccd7eea1df7a37d6ddc39b023b801ba16"}}
  ```
  </details>

- … and 27 more

### [`errors.validation-shape`](https://github.com/mandu5/jevcompat/blob/main/SPEC.md#errors.validation-shape) (SHOULD) — validation errors are 422 with detail[]

- **invalid:not-json**: body is not {"detail": [{"loc": ["body", …], "msg", "type"}]}: {"error": "Expecting property name enclosed in double quotes: line 1 column 53 (char 52)"}

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"model": "jev-latest", "state": "x", "questions": {
  → 422
  {"error": "Expecting property name enclosed in double quotes: line 1 column 53 (char 52)"}
  ```
  </details>

- **invalid:missing-state**: body is not {"detail": [{"loc": ["body", …], "msg", "type"}]}: {"error": "request requires state and questions"}

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"questions": {"refund": {"type": "noul", "instructions": "Is the customer asking for money back?"}}, "model": "jev-latest"}
  → 422
  {"error": "request requires state and questions"}
  ```
  </details>

- **invalid:missing-questions**: body is not {"detail": [{"loc": ["body", …], "msg", "type"}]}: {"error": "request requires state and questions"}

  <details><summary>exchange</summary>

  ```
  POST /v1/systemone
  {"model": "jev-latest", "state": "Hi, I was charged twice for my March invoice (order #4471) a…"}
  → 422
  {"error": "request requires state and questions"}
  ```
  </details>

- … and 11 more


MUST 31/32 · SHOULD 9/12

