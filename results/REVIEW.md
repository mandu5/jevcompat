# Review of the failed requirements: 8 replicas × jevcompat 6a8a543

The final reports in `results/<name>/report.json` all come from jevcompat commit `6a8a543dcece158896c4ad652480143c2266f37f`, clean tree. The source hash (`find src/jevcompat -name '*.py' | sort | xargs cat | shasum -a 256`) was `be5d4703795e75eb61bfaa7f63037ba25bbe4f7b1ef63b4bc89e03985474cb60` before and after every run. All runs used `--timeout 300` and were made on 2026-09-24 between 08:05 and 08:23 KST, on an Apple M1 Pro with 16 GB RAM. 6a8a543 changes only report presentation over 3c23db3 (SPEC anchors, titles, JSON-rendered values, the null-legend message); every replica's MUST/SHOULD counts, per-requirement statuses and per-requirement finding counts are identical to the 3c23db3 run (kept in `bench/_superseded-runs/jevcompat-3c23db3/`).

For every requirement a report marks as failed, the tables below judge it. **real** means the server deviates from SPEC 0.1 and the evidence shows it. **suspect jevcompat** means the check is wrong, too strict, or blames the wrong requirement. Each judgment rests on the request and response recorded in the report, the official sources in SPEC.md (OAS 0.2.0, typesafe-sdk 0.7.1, the API reference, and the JS SDK source), and, where it helped, the replica's own code.

## Result

- In the final reports, **42 failed requirements across 8 replicas: 42 real, 0 suspect jevcompat.**
- During the measurement, **5 jevcompat issues** were found on the intermediate commits 38ade40 and 8659b29. Each was reported to the maintainer and fixed in 3c23db3 or earlier; they are listed under "Resolved before the final run" at the end.
- Two cross-cutting caveats. Neither changes a judgment, but a reader should know them:
  - `response.extensions` (the `x_` prefix) and `confidence.formula` are jevcompat's own SHOULD-level policies. The x_ rule is SPEC's forward-compatibility convention, and no TypeSafe source requires it. The confidence reference formulas come from TypeSafe's docs and adapter library, and TypeSafe says clients are "never locked into our definition". The failures are genuine against SPEC 0.1 as written, not against anything TypeSafe mandates.
  - For an unknown `model`, jevcompat accepts any 4xx and checks 422 bodies against the validation shape. The live API answers `400 {"detail":{"error_type":"api_usage_error","message":"Unknown model: x"}}` (per the research notes: the JS SDK live integration test). The three unknown-model findings filed under `errors.validation-shape` (simple-jev, rizzo-flow, open-jev) are genuine, because their bodies match neither shape, but the check itself is looser than the live behaviour.

## laya — NandhaKishorM/laya @ 1e28ac2 (MUST 30/32, SHOULD 6/12)

| requirement | level | judgment | reason |
|---|---|---|---|
| choice.options | MUST | real | 64 options are accepted, 128 get `422 {"detail":"question 'queue' options exceed head_max_len=192"}`. The head's token budget cannot hold 128 option names. |
| score.legend | MUST | real | For `criteria: ["Calm", null]`, an out-of-range request laya chose to accept, it returns `"legend":{"0":"Calm","1":null}`. typesafe-sdk's `SystemOneResponse.model_validate_json` raises `ValidationError` on that body (checked directly) but parses the same body with `"1":""`. The Python SDK passes a raw-dict question with a `null` level through unvalidated, so an SDK user can hit this. |
| http.models | SHOULD | real | `GET /v1/models` → `404 {"detail":"Not Found"}`. laya has no such route. |
| noul.no-instructions | SHOULD | real | A noul with criteria and no `instructions` gets `422 {"detail":"question 'threat': no 'instructions'; …"}`. OAS `NoulQuestion` requires only `type`. |
| response.extensions | SHOULD | real | Unprefixed top-level `routing`, `action` on every answer, and `confidence` on noul answers, which TypeSafe's Confidence page says noul answers do not carry. |
| confidence.formula | SHOULD | real | laya's confidence is 1 − normalised entropy (H/ln n), which matches all 15 findings to within 0.0003. Example: choice-basic `{"Billing":0.9856,"Technical":0.0066,"Sales":0.0078}` → 0.9224, where the reference gives 0.978. It matches neither accepted formula. |
| errors.reject-invalid | SHOULD | real | A body with no `state` gets 200 (the OAS lists `state` as required), and `"questions":{}` gets 200 (OAS `minProperties: 1`). |
| errors.validation-shape | SHOULD | real | Non-JSON bodies and a missing `questions` get 400, not 422. Every rejection body is `{"detail":"<string>"}`, not the FastAPI list form. |

## kev — jaredpalmer/kev @ 2874258, Kev-0.8B (MUST 32/32, SHOULD 10/12)

| requirement | level | judgment | reason |
|---|---|---|---|
| response.extensions | SHOULD | real | Every response has an unprefixed top-level `latency_ms`. |
| confidence.formula | SHOULD | real | kev's score confidence is `1 − E\|level − mode\| / (L − 1)` (`kev/api.py:125`, which calls it an approximation). It normalises by L−1, not by the uniform distribution's spread. On TypeSafe's own documented example `{0, 0.57, 0.43}` it gives 0.785 where the docs show 0.35. Measured example: score-levels:3 `{"0":0.0269,"1":0.5069,"2":0.4662}` gives 0.7535; both references give 0.260. Choice confidence passes. |

## decider — Mapika/decider @ b44b4c9, decider-0.8b (MUST 32/32, SHOULD 6/12)

| requirement | level | judgment | reason |
|---|---|---|---|
| noul.no-instructions | SHOULD | real | `422 {"detail":"question without instructions"}`. |
| score.map-rejected | SHOULD | real | Score `criteria` sent as `{"0":"Calm","1":"Frustrated","2":"Very angry"}` gets 200 with a normal score answer. The OAS types it as an array. |
| response.extensions | SHOULD | real | Unprefixed `certainty` on choice and score answers, plus `level_fit` and `fit_mass` on score answers. |
| confidence.formula | SHOULD | real | Choice and score confidence are both p_max. Example: choice-ambiguous `{"Red":0.195,"Green":0.1994,"Blue":0.2252,"Yellow":0.2286,"Purple":0.1518}` gives confidence 0.2286, where the reference gives 0.036. Example: score-levels:5 top level 0.2734 gives 0.2734, where the references give 0.216 (distance) or 0.092 (top probability). |
| errors.reject-invalid | SHOULD | real | `"questions":{}` gets 200 with `"answers":{}`, and score-map gets 200 (see score.map-rejected). |
| errors.validation-shape | SHOULD | real | Rejections are 422 but the body is `{"detail":"<string>"}`, e.g. `{"detail":"unknown question type 'boolean'"}`. |

## von — wfzyx/von @ 657f42f (MUST 31/32, SHOULD 8/12)

| requirement | level | judgment | reason |
|---|---|---|---|
| request.structured-text | MUST | real | Object or array `instructions` and criteria descriptions get `422 {"detail":"3 validation errors for Noul\ninstructions\n  Input should be a valid string …"}`. von's pydantic types are `str`, while the OAS allows string, object or array. |
| noul.no-instructions | SHOULD | real | `422 … instructions Field required`. |
| confidence.formula | SHOULD | real | Confidence is the top-1 minus top-2 margin. Example: choice-null-description `{"Billing":0.2861,"Technical":0.3629,"Sales":0.351}` gives 0.012 = 0.3629 − 0.351, where the reference gives 0.044. |
| errors.reject-invalid | SHOULD | real | `"questions":{}` gets 200. `"criteria":{}` gets 200 with `{"choice":"","probabilities":{},"confidence":0.0}`, whose `choice` is not an option. Caveat: the OAS sets no `minProperties` on choice criteria, so the reason this is invalid is SPEC §3.3/§4 (no valid answer exists), not the OAS. |
| errors.validation-shape | SHOULD | real | Rejections are 422 with `{"detail":"<pydantic error text>"}` or `{"detail":"Unknown question type 'boolean'"}`, not the list form. |

## jeff — logan-markewich/jeff @ 34b32f9, run with `JEFF_API_KEYS=devkey` and `--key devkey` (MUST 30/32, SHOULD 11/14)

| requirement | level | judgment | reason |
|---|---|---|---|
| choice.options | MUST | real | 128 options get `422 {"detail":[{"loc":["body","questions","queue","criteria"],"msg":"At most 64 options/levels",…}]}` (`JEFF_MAX_LABELS` defaults to 64). |
| score.expectation | MUST | real | `score` is computed from the untempered distribution while `probabilities` are tempered at T=3.2, which jeff's README acknowledges. Example: score-levels:2 `{"0":0.136,"1":0.864}` with `"score":0.9973`, where Σ i·p = 0.864. |
| auth.missing | SHOULD | real | The status is correct (401), but the body is `{"error":{"type":"authentication_error","message":"Missing bearer token"}}`, not `{"detail":{"error_type","message"}}`. |
| auth.invalid | SHOULD | real | Same body shape: `{"error":{"type":"authentication_error","message":"Invalid API key"}}`. |
| semantics.question-order | SHOULD | real | Baseline (refund, team, anger) gives `team` = `{"Billing":0.768,"Technical":0.1423,"Sales":0.0896}`. Reversed order gives `{"Billing":0.3508,"Technical":0.4255,"Sales":0.2236}`, so the answer flips to Technical. All 3+3 sends were identical, so this is not noise. jeff shares one encoder pass across choice and score questions by default (README). |

## simple-jev — featherless-ai/simple-jev @ 8b7b7f9, Qwen3.5-0.8B on CPU, run with `--model Qwen/Qwen3.5-0.8B` (MUST 29/32, SHOULD 7/12)

The default run without `--model` stopped at preflight with "not tested" (exit 2), because the server rejects `jev-latest` and has no `/v1/models` to fall back to (`results/simple-jev/default/`). The judgments below are for the `--model` run. Leaving `request.model-alias` unblamed in the default run is jevcompat's documented rule: it blames a requirement only when a second request proves which one. The `--model` run then records the failure.

| requirement | level | judgment | reason |
|---|---|---|---|
| request.model-alias | MUST | real | `"model":"jev-latest"` gets `422 {"error":{"message":"Loaded model is 'Qwen/Qwen3.5-0.8B'","type":"invalid_request_error",…}}`. The server accepts only the exact `--model` string. |
| choice.options | MUST | real | 26 options are accepted, 64 get `422 … "questions.queue.choice.criteria: Dictionary should have at most 50 items after validation, not 64"`. The schema caps options at 50. |
| score.legend | MUST | real | `criteria: ["Calm", null]` (out of range, accepted) returns `"legend":{"0":"Calm","1":null}`, which typesafe-sdk cannot parse. This is the same mechanism as laya. |
| http.models | SHOULD | real | `GET /v1/models` → 404. |
| noul.no-instructions | SHOULD | real | `422 … "questions.threat.noul.instructions: Field required"`. |
| confidence.formula | SHOULD | real | Confidence is p_max for choice and score (`common/response_scoring.py:288`, `"confidence": float(p[winner])`). All 14 findings match p_max exactly. Example: choice-null-description `{"Billing":0.8983,"Technical":0.0420,"Sales":0.0597}` gives 0.8983, where the reference gives 0.847. |
| errors.validation-shape | SHOULD | real | All 13 rejections are 422 with an OpenAI-style envelope, `{"error":{"message","type":"invalid_request_error","code":422,"param","details"}}`, not `{"detail":[…]}`. |
| semantics.question-order | SHOULD | real, marginal | `anger` probability of level 1 is 0.8880 in all 3 baseline sends (refund, team, anger) and 0.9478 in all 6 reversed sends (anger, team, refund). The difference is 0.060 against a 0.05 floor, reproduced in a second round. Every send was identical, so this is not sampling noise; the answer does depend on question order. |

## rizzo-flow — Rizzo-AI-Academy/rizzo-flow @ d34665b, Spark-X2.5-1.7B Q8_0 on llama.cpp Metal (MUST 31/32, SHOULD 9/12)

| requirement | level | judgment | reason |
|---|---|---|---|
| choice.options | MUST | real | 26 options are accepted, 64 get `422 … "Dictionary should have at most 26 items after validation, not 64"`. `MAX_SLOTS=26` maps each option to one answer letter. |
| request.unknown-fields | SHOULD | real | A request with extra top-level `"x_trace_id":"jevcompat","seed":7` gets `422 {"detail":[{"type":"extra_forbidden","loc":["body","x_trace_id"],…},{"type":"extra_forbidden","loc":["body","seed"],…}]}`. The Python SDK forwards `extra_body` fields, and the OAS does not forbid extra fields. |
| noul.no-instructions | SHOULD | real | `422 … ["body","questions","threat","noul","instructions"] … "Field required"`. |
| errors.validation-shape | SHOULD | real | `"model":"jevcompat-no-such-model"` gets `422 {"detail":"Unknown model 'jevcompat-no-such-model'. Use 'rizzo-latest', …"}`, a string `detail` that matches neither the validation shape nor the live API's `400 {"detail":{"error_type":"api_usage_error",…}}`. |

## open-jev — Zefan-Cai/Open-Jev @ 3308a15, Open-Jev-2B on MPS (MUST 31/32, SHOULD 9/12)

| requirement | level | judgment | reason |
|---|---|---|---|
| noul.criteria | MUST | real | `"criteria":{"true":"They want a refund or chargeback"}` and the false-only variant get `422 {"error": "Noul criteria must contain true and false descriptions"}`. OAS `NoulCriteria` makes both `true` and `false` optional (each `anyOf` string, object, array or null, none required). |
| noul.no-instructions | SHOULD | real | `422 {"error": "instructions and descriptions must be text, an object, or an array"}` for a noul without `instructions`. |
| response.extensions | SHOULD | real | Unprefixed top-level `metadata` (method, temperature, candidate_sequences, inference_seconds, checkpoint_sha256, and so on) on every response. |
| errors.validation-shape | SHOULD | real | All 14 rejections are 422 with `{"error": "<string>"}`. Examples: `{"error": "request requires state and questions"}`, and `{"error": "requested model is not loaded; see /v1/models"}` for an unknown model. |

## Resolved before the final run (jevcompat issues found during this measurement)

These were found on intermediate commits and reported to the maintainer. Items 1–4 are fixed as of 8659b29 and item 5 in 3c23db3. None of them affects the final reports. The superseded reports are kept in `bench/_superseded-runs/` (gitignored).

1. **score.legend (MUST) on structured levels: false positive, fixed as SPEC A.9 (as of 8659b29).** Affected kev, decider and rizzo-flow at 38ade40. jevcompat required object levels to come back unchanged, but the API reference types `legend` as `map<string, string>`, the SDK accepts both, and SPEC cited only `[api]`. Evidence (kev, 38ade40):
   `→ {"questions":{"q":{"type":"score","instructions":{"scale":"frustration"},"criteria":[{"label":"Calm"},{"label":"Frustrated"},{"label":"Very angry","signals":["threats"]}]}}, …}`
   `← 200 {"answers":{"q":{"type":"score","score":1.1403,"legend":{"0":"label: Calm","1":"label: Frustrated","2":"label: Very angry\nsignals:\n  - threats"},…}}}`, which jevcompat reported as "legend['0'] is 'label: Calm', the request's level 0 is {'label': 'Calm'}".
2. **score.legend (MUST) on a null level: false positive, fixed as of 8659b29.** Affected kev and decider at 38ade40. jevcompat required `legend["1"] == null`, but typesafe-sdk's `ScoreAnswer` rejects a null legend value (checked: `ValidationError`). Evidence (kev):
   `→ {"questions":{"anger":{"type":"score","instructions":"Frustration?","criteria":["Calm",null]}}, …}`
   `← 200 {"answers":{"anger":{"type":"score","score":0.6852,"legend":{"0":"Calm","1":""},…}}}`, reported as "legend['1'] is '', the request's level 1 is None". (decider returned `"1":"null"`.) Since the fix, a `null` echo fails, as it does for laya and simple-jev above, and a string passes.
3. **confidence.formula on score answers: false positive, fixed as SPEC A.10 (as of 8659b29).** Affected jeff and rizzo-flow. Both use `(n·p_max − 1)/(n − 1)`, the statistic on TypeSafe's Confidence page. It reproduces every documented score example: all have 3 levels with the mode in the middle, where it equals the adapter's distance formula. Only the adapter-library formula disagrees at 5, 10 and 11 levels. Evidence (jeff, 38ade40):
   `→ {"questions":{"anger":{"type":"score","instructions":"How frustrated is the customer?","criteria":["Level 0: calm","Level 1: angrier","Level 2: angrier","Level 3: angrier","Level 4: angrier"]}}, …}`
   `← 200 {"answers":{"anger":{"type":"score","score":1.4504,"confidence":0.2062,…,"probabilities":{"0":0.0765,"1":0.365,"2":0.211,"3":0.1901,"4":0.1574}}}}`. (5·0.365 − 1)/4 = 0.2062, and it was reported as "the reference formula gives 0.050".
4. **errors.reject-invalid for `invalid:choice-no-options`: SPEC contradiction, fixed as of 8659b29.** At 38ade40, SPEC §3.5 listed "a choice with 0 … options" as MAY-accept, while §6 listed empty `criteria` as invalid (SHOULD 4xx). The OAS has no `minProperties` on choice `criteria`. The fix removed 0 from §3.5. von's 200 (`{"choice":"","probabilities":{},"confidence":0.0}`) is now judged a genuine SHOULD failure above, with the OAS caveat noted there.
5. **The `choice-ambiguous` case never ran: false negative, fixed in 3c23db3.** At 8659b29, `choice-ambiguous` (checks.py:446) called `ctx.supports(name, ("choice","score"), …)`, but `"score"` is only added to `types_ok` by `score-levels` (checks.py:500), which ran later. So the case was skipped silently on every server, and none of the laya, kev, decider, von or jeff reports at 8659b29 contains a `choice-ambiguous` exchange. As a result, decider's choice confidence (p_max) passed `confidence.formula`, because every other choice probe had a top probability near 0.999. From 3c23db3 on the case runs, and in the final run it catches decider: `{"Red":0.195,"Green":0.1994,"Blue":0.2252,"Yellow":0.2286,"Purple":0.1518}` gives confidence 0.2286, where the reference gives 0.036.

One more event, not a finding: while the maintainer was editing, a jevcompat run crashed mid-way with `AttributeError: module 'jevcompat.spec' has no attribute 'SEM_NOISE_K'`. That run was discarded, and every final run was guarded by a check of the commit and source hash.
