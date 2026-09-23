# laya: run record

| field | value |
|---|---|
| repo | https://github.com/NandhaKishorM/laya |
| commit | `1e28ac20c0896b1c37a744cd11f740eb98f8b178` (2026-09-23 23:34:56 +0530, "release: 0.3.11") |
| license | Apache-2.0 (LICENSE file; `pyproject.toml` license = Apache-2.0) |
| weights | `convaiinnovations/laya` @ `aa8c91ca088ec597df95a0d1c76b3063cb2ae5e8` (bundle repo; the router preloads the root checkpoint `english` and the subfolders `multilingual/` and `typed-decisions/`) |
| port | 8000 |
| env vars | `LAYA_HOST=127.0.0.1 LAYA_PORT=8000` |
| device | MPS (auto) |
| date/time of run | 2026-09-24 08:05:46 KST (2026-09-23T23:05:46Z) |
| machine | Apple M1 Pro, 16 GB RAM (17179869184 bytes), macOS 26.6.1 (25G76) |
| jevcompat | jevcompat 0.1.0 (spec 0.1), commit `6a8a543dcece158896c4ad652480143c2266f37f` (clean tree); source hash `be5d4703795e75eb61bfaa7f63037ba25bbe4f7b1ef63b4bc89e03985474cb60` (`find src/jevcompat -name '*.py' \| sort \| xargs cat \| shasum -a 256`), unchanged after the run: True; typesafe-sdk 0.7.1 (the drop-in check ran) |
| wall time | 5 s for the jevcompat run (exit code 1); the report records 61 exchanges in 4.8 s. The server was ready 13.1 s after start. |
| verdict (as printed) | `not conformant to spec 0.1: MUST 30/32, SHOULD 6/12` |
| summary | MUST 30/32 passed (2 failed, 1 not tested); SHOULD 6/12 passed (6 failed, 3 not tested) |

## Install

```bash
cd ./bench/laya
git clone https://github.com/NandhaKishorM/laya.git src     # checked out at HEAD 1e28ac2
uv venv -p 3.12 .venv                                        # Python 3.12.4
uv pip install -p .venv/bin/python "./src[serve]"
# resolved: laya 0.3.11, torch 2.14.0, transformers 5.17.0, fastapi 0.141.1, uvicorn 0.53.0, huggingface_hub 1.32.0
```

The first lazy download of the third checkpoint stalled at 134 MB for 5+ minutes, so the bundle was fetched once with `huggingface_hub.snapshot_download("convaiinnovations/laya", revision="aa8c91ca088ec597df95a0d1c76b3063cb2ae5e8")`. The server then loads all three checkpoints from the HF cache. No HF token was used.

## Serve

```bash
LAYA_HOST=127.0.0.1 LAYA_PORT=8000 .venv/bin/laya-serve
```

`LAYA_HOST=127.0.0.1` binds loopback instead of the default 0.0.0.0. `LAYA_PORT=8000` is the default. Everything else is left at its default: `LAYA_PRELOAD=1` (all three checkpoints), `LAYA_API_KEY` unset (auth off), `LAYA_DEVICE` unset (auto, which picks `mps` on this machine; see `laya/agent.py:295-296`).

## Test

```bash
~/Documents/GitHub/jevcompat/.venv/bin/jevcompat test http://127.0.0.1:8000 --timeout 300 --json ~/Documents/GitHub/jevcompat/results/laya/report.json --markdown ~/Documents/GitHub/jevcompat/results/laya/report.md --title "NandhaKishorM/laya @ 1e28ac2"
```

`model sent 'jev-latest', server reports 'laya-rl-agent' · 61 requests · 4.8s · typesafe-sdk 0.7.1`

The server was started in its own process group (36862) and stopped after the run with SIGTERM to the group. Afterwards the group had exited: True; port 8000 was free: True. Console output is in `console.txt`, the full report in `report.json` and `report.md`.
