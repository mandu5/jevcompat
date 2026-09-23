# kev: run record

| field | value |
|---|---|
| repo | https://github.com/jaredpalmer/kev |
| commit | `287425898c4eb695b45bfdfe9f6e59c62ac05747` (2026-09-23 17:00:56 -0400, "benchmark --remote-concurrency: bounded parallel requests for RemotePredictor, rows unchanged (#86)") |
| license | Apache-2.0 (LICENSE file; `pyproject.toml` license = "Apache-2.0") |
| weights | adapter and pointer head `jaredpalmer/kev-0.8b` @ `54f4f8777356cd5bbbb6c6919c657f26e6f2f6d8`; base `Qwen/Qwen3.5-0.8B-Base` @ `dc7cdfe2ee4154fa7e30f5b51ca41bfa40174e68` (the revision pinned in the checkpoint's `training_config.json`) |
| port | 8009 |
| env vars | `(none)` |
| device | MLX on the Apple GPU, bfloat16 |
| date/time of run | 2026-09-24 08:06:01 KST (2026-09-23T23:06:01Z) |
| machine | Apple M1 Pro, 16 GB RAM (17179869184 bytes), macOS 26.6.1 (25G76) |
| jevcompat | jevcompat 0.1.0 (spec 0.1), commit `6a8a543dcece158896c4ad652480143c2266f37f` (clean tree); source hash `be5d4703795e75eb61bfaa7f63037ba25bbe4f7b1ef63b4bc89e03985474cb60` (`find src/jevcompat -name '*.py' \| sort \| xargs cat \| shasum -a 256`), unchanged after the run: True; typesafe-sdk 0.7.1 (the drop-in check ran) |
| wall time | 6 s for the jevcompat run (exit code 0); the report records 62 exchanges in 6.2 s. The server was ready 9.1 s after start. |
| verdict (as printed) | `conformant to spec 0.1: MUST 32/32, SHOULD 10/12` |
| summary | MUST 32/32 passed (0 failed, 1 not tested); SHOULD 10/12 passed (2 failed, 3 not tested) |

## Install

```bash
cd ./bench/kev
git clone https://github.com/jaredpalmer/kev.git src         # checked out at HEAD 2874258
cd src
UV_PROJECT_ENVIRONMENT=./bench/kev/.venv uv sync --locked --extra serve
# Python 3.13.3 (from the repo's .python-version). Resolved from uv.lock: torch 2.8.0, transformers 5.17.0,
# mlx 0.32.2, mlx-lm 0.31.3, peft 0.21.0, fastapi 0.141.1, uvicorn 0.53.0
```

`UV_PROJECT_ENVIRONMENT` only moves the venv outside the clone. The README command is `uv sync --extra serve`. On first start the server downloaded the adapter and the base model itself (no HF token).

## Serve

```bash
cd src && ../.venv/bin/python -m kev.serve --run jaredpalmer/kev-0.8b --port 8009
```

No env vars were set. `KEV_API_KEY` is unset, so auth is off. `KEV_BACKEND` and `KEV_DTYPE` are unset, which gives the Apple Silicon serving defaults: the MLX backend in bfloat16. The README form is `uv run --extra serve python -m kev.serve --run jaredpalmer/kev-4b --port 8009`; this run used the 0.8B checkpoint, as instructed. `kev.serve` binds 127.0.0.1.

## Test

```bash
~/Documents/GitHub/jevcompat/.venv/bin/jevcompat test http://127.0.0.1:8009 --timeout 300 --json ~/Documents/GitHub/jevcompat/results/kev/report.json --markdown ~/Documents/GitHub/jevcompat/results/kev/report.md --title "jaredpalmer/kev @ 2874258"
```

`model sent 'jev-latest', server reports 'jev-latest' · 62 requests · 6.2s · typesafe-sdk 0.7.1`

The server was started in its own process group (38531) and stopped after the run with SIGTERM to the group. Afterwards the group had exited: True; port 8009 was free: True. Console output is in `console.txt`, the full report in `report.json` and `report.md`.
