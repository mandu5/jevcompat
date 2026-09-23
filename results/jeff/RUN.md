# jeff: run record

| field | value |
|---|---|
| repo | https://github.com/logan-markewich/jeff |
| commit | `34b32f99a727c47b679adde33f4702a001e02979` (2026-09-19 18:59:42 -0600, "update jevbench results") |
| license | MIT (LICENSE file; `pyproject.toml` license = "MIT"); weights Apache-2.0 (HF card) |
| weights | `knowledgator/gliformer-large-v1` @ `d0a4e53d09cebe6bc963dd9be319d4279084bb2d` (`pytorch_model.bin`, 2,302,735,855 bytes), downloaded to `bench/jeff/models/gliformer-large-v1` |
| port | 8000 |
| env vars | `JEFF_MODEL=./bench/jeff/models/gliformer-large-v1 JEFF_API_KEYS=devkey JEFF_HOST=127.0.0.1 JEFF_PORT=8000` |
| device | MPS (auto), float32 |
| date/time of run | 2026-09-24 08:07:10 KST (2026-09-23T23:07:10Z) |
| machine | Apple M1 Pro, 16 GB RAM (17179869184 bytes), macOS 26.6.1 (25G76) |
| jevcompat | jevcompat 0.1.0 (spec 0.1), commit `6a8a543dcece158896c4ad652480143c2266f37f` (clean tree); source hash `be5d4703795e75eb61bfaa7f63037ba25bbe4f7b1ef63b4bc89e03985474cb60` (`find src/jevcompat -name '*.py' \| sort \| xargs cat \| shasum -a 256`), unchanged after the run: True; typesafe-sdk 0.7.1 (the drop-in check ran) |
| wall time | 12 s for the jevcompat run (exit code 1); the report records 69 exchanges in 11.3 s. The server was ready 15.2 s after start. |
| verdict (as printed) | `not conformant to spec 0.1: MUST 30/32, SHOULD 11/14` |
| summary | MUST 30/32 passed (2 failed, 1 not tested); SHOULD 11/14 passed (3 failed, 1 not tested) |

## Install

```bash
cd ./bench/jeff
git clone https://github.com/logan-markewich/jeff.git src    # checked out at HEAD 34b32f9
cd src
UV_PROJECT_ENVIRONMENT=./bench/jeff/.venv uv sync --locked --extra dev
# Python 3.12.4; resolved from uv.lock: gliformer 0.1.2, gliner 0.2.29, torch 2.14.0, transformers 5.16.1, fastapi 0.141.1, uvicorn 0.53.0
# weights (README step 2, into a directory outside the clone):
python -c 'from huggingface_hub import snapshot_download; snapshot_download("knowledgator/gliformer-large-v1", revision="d0a4e53d09cebe6bc963dd9be319d4279084bb2d", local_dir="./bench/jeff/models/gliformer-large-v1")'
```

The README uses `uv run hf download knowledgator/gliformer-large-v1 --local-dir models/gliformer-large-v1` inside the clone. Here the weights were put outside the clone and `JEFF_MODEL` points at them.

## Serve

```bash
cd src && JEFF_MODEL=./bench/jeff/models/gliformer-large-v1 JEFF_API_KEYS=devkey JEFF_HOST=127.0.0.1 JEFF_PORT=8000 ../.venv/bin/jeff
```

`JEFF_API_KEYS=devkey` turns auth on, as in the README quickstart (`JEFF_API_KEYS=devkey uv run jeff`), so jevcompat was run with `--key devkey` and the auth requirements were exercised. `JEFF_MODEL` gives the weights path. `JEFF_HOST=127.0.0.1` binds loopback instead of the default 0.0.0.0. `JEFF_PORT=8000` is the default. The other `JEFF_*` settings are at their defaults: `JEFF_ISOLATE=nouls`, `JEFF_TEMPERATURE=3.2`, `JEFF_MAX_LABELS=64`, and device auto, which the startup log shows as `device=mps dtype=float32`.

## Test

```bash
~/Documents/GitHub/jevcompat/.venv/bin/jevcompat test http://127.0.0.1:8000 --key devkey --timeout 300 --json ~/Documents/GitHub/jevcompat/results/jeff/report.json --markdown ~/Documents/GitHub/jevcompat/results/jeff/report.md --title "logan-markewich/jeff @ 34b32f9"
```

`model sent 'jev-latest', server reports 'gliformer-large-v1' · 69 requests · 11.3s · typesafe-sdk 0.7.1`

The server was started in its own process group (41947) and stopped after the run with SIGTERM to the group. Afterwards the group had exited: True; port 8000 was free: True. Console output is in `console.txt`, the full report in `report.json` and `report.md`.
