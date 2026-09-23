# simple-jev: run record

| field | value |
|---|---|
| repo | https://github.com/featherless-ai/simple-jev |
| commit | `8b7b7f994690a56cbde033e4179d920e288039d5` (2026-09-23 20:58:01 +0000, "Update classifier API pricing and model order") |
| license | Apache-2.0 (LICENSE file) |
| weights | `Qwen/Qwen3.5-0.8B` @ `2fc06364715b967f1860aea9cf38778875588b17` (the default Transformers backend; one of the two checkpoints the hf-server README reports running on CPU) |
| port | 8000 |
| env vars | `(none)` |
| device | CPU, float32 |
| date/time of run | 2026-09-24 08:07:29 KST (2026-09-23T23:07:29Z) |
| machine | Apple M1 Pro, 16 GB RAM (17179869184 bytes), macOS 26.6.1 (25G76) |
| jevcompat | jevcompat 0.1.0 (spec 0.1), commit `6a8a543dcece158896c4ad652480143c2266f37f` (clean tree); source hash `be5d4703795e75eb61bfaa7f63037ba25bbe4f7b1ef63b4bc89e03985474cb60` (`find src/jevcompat -name '*.py' \| sort \| xargs cat \| shasum -a 256`), unchanged after the run: True; typesafe-sdk 0.7.1 (the drop-in check ran) |
| wall time | 794 s for the jevcompat run (exit code 1); the report records 67 exchanges in 794.2 s. The server was ready 6.1 s after start. |
| verdict (as printed) | `not conformant to spec 0.1: MUST 29/32, SHOULD 7/12` |
| summary | MUST 29/32 passed (3 failed, 1 not tested); SHOULD 7/12 passed (5 failed, 3 not tested) |

## Install

```bash
cd ./bench/simple-jev
git clone https://github.com/featherless-ai/simple-jev.git src   # checked out at HEAD 8b7b7f9
uv venv -p 3.12 .venv                                             # Python 3.12.4
uv pip install -p .venv/bin/python -e './src/hf-server[test]'
# resolved: torch 2.14.0 (default macOS arm64 wheel), transformers 5.17.0, fastapi 0.141.1, uvicorn 0.53.0
```

The weights were pre-fetched with `snapshot_download("Qwen/Qwen3.5-0.8B", revision="2fc06364715b967f1860aea9cf38778875588b17")`. No HF token was used.

## Serve

```bash
cd src && ../.venv/bin/simple-jev --model Qwen/Qwen3.5-0.8B --revision 2fc06364715b967f1860aea9cf38778875588b17 --device cpu --dtype float32 --host 127.0.0.1 --port 8000
```

No env vars were set. `--device cpu --dtype float32` follows the hf-server README's CPU instructions; that README also reports that loading Qwen directly on MPS crashed on the authors' Mac. There is no auth. jevcompat's `/v1/systemone` requests go to the undocumented alias of `/v1/classifier`.

## Test

```bash
~/Documents/GitHub/jevcompat/.venv/bin/jevcompat test http://127.0.0.1:8000 --model Qwen/Qwen3.5-0.8B --timeout 300 --json ~/Documents/GitHub/jevcompat/results/simple-jev/report.json --markdown ~/Documents/GitHub/jevcompat/results/simple-jev/report.md --title "featherless-ai/simple-jev @ 8b7b7f9"
```

`model sent 'Qwen/Qwen3.5-0.8B', server reports 'Qwen/Qwen3.5-0.8B' · 67 requests · 794.2s · typesafe-sdk 0.7.1`

The server accepts only the model name given to `--model`. `"model": "jev-latest"` gets `422 {"error":{"message":"Loaded model is 'Qwen/Qwen3.5-0.8B'",...}}`, and there is no `GET /v1/models` (404), so jevcompat cannot fall back to another name by itself. The default run (`default/`) stopped at that point, and the reported run was made with `--model Qwen/Qwen3.5-0.8B`.

Default run, without `--model` (in `default/`):

```bash
~/Documents/GitHub/jevcompat/.venv/bin/jevcompat test http://127.0.0.1:8000 --timeout 300 --json ~/Documents/GitHub/jevcompat/results/simple-jev/default/report.json --markdown ~/Documents/GitHub/jevcompat/results/simple-jev/default/report.md --title "featherless-ai/simple-jev @ 8b7b7f9"
```

That run exited with code 2 and printed `not tested: the server rejects a minimal valid request (422: {"error":{"message":"Loaded model is 'Qwen/Qwen3.5-0.8B'","type":"invalid_request_error","code":422,"param":null,"details":[]}}); if it needs a particular model name, pass --model NAME`

The server was started in its own process group (43121) and stopped after the run with SIGTERM to the group. Afterwards the group had exited: True; port 8000 was free: True. Console output is in `console.txt`, the full report in `report.json` and `report.md`.
