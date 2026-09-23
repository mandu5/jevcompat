# decider: run record

| field | value |
|---|---|
| repo | https://github.com/Mapika/decider |
| commit | `b44b4c9880a67291206499b86aac89004850134a` (2026-09-23 21:57:49 +0200, "cards: decider-2b JevBench public items and speed measured again on B300") |
| license | Apache-2.0 (LICENSE file; `pyproject.toml` license = "Apache-2.0") |
| weights | `Mapika/decider-0.8b` @ `a0a01d6f8135298f400a8c856b355793012ae971` (the server reports it as `decider-0.8b-v1`, temperature 1.03) |
| port | 8000 |
| env vars | `DECIDER_MODEL=Mapika/decider-0.8b` |
| device | MPS (auto), eager |
| date/time of run | 2026-09-24 08:06:17 KST (2026-09-23T23:06:17Z) |
| machine | Apple M1 Pro, 16 GB RAM (17179869184 bytes), macOS 26.6.1 (25G76) |
| jevcompat | jevcompat 0.1.0 (spec 0.1), commit `6a8a543dcece158896c4ad652480143c2266f37f` (clean tree); source hash `be5d4703795e75eb61bfaa7f63037ba25bbe4f7b1ef63b4bc89e03985474cb60` (`find src/jevcompat -name '*.py' \| sort \| xargs cat \| shasum -a 256`), unchanged after the run: True; typesafe-sdk 0.7.1 (the drop-in check ran) |
| wall time | 22 s for the jevcompat run (exit code 0); the report records 62 exchanges in 22.0 s. The server was ready 8.1 s after start. |
| verdict (as printed) | `conformant to spec 0.1: MUST 32/32, SHOULD 6/12` |
| summary | MUST 32/32 passed (0 failed, 1 not tested); SHOULD 6/12 passed (6 failed, 3 not tested) |

## Install

```bash
cd ./bench/decider
git clone https://github.com/Mapika/decider.git src          # checked out at HEAD b44b4c9
uv venv -p 3.12 .venv                                         # Python 3.12.4
uv pip install -p .venv/bin/python "./src[serve,metal]"
# resolved: decider-ai 1.2.1, torch 2.14.0, transformers 5.17.0, mlx 0.32.2, fastapi 0.141.1, uvicorn 0.53.0
```

`[metal]` is the README's optional Apple Silicon extra. On first start the server downloaded the weights itself (no HF token).

## Serve

```bash
cd src && DECIDER_MODEL=Mapika/decider-0.8b ../.venv/bin/uvicorn decider.serve:app --host 127.0.0.1 --port 8000
```

`DECIDER_MODEL=Mapika/decider-0.8b` selects the checkpoint; this is the README's `scripts/serve.sh` equivalent with a loopback host. All `DECIDER_*` tuning variables are left at their defaults. `DECIDER_DEVICE` is unset (auto, which picks `mps` here; the startup log shows `'device': 'mps'`). There is no auth.

## Test

```bash
~/Documents/GitHub/jevcompat/.venv/bin/jevcompat test http://127.0.0.1:8000 --timeout 300 --json ~/Documents/GitHub/jevcompat/results/decider/report.json --markdown ~/Documents/GitHub/jevcompat/results/decider/report.md --title "Mapika/decider @ b44b4c9"
```

`model sent 'jev-latest', server reports 'decider-0.8b-v1' · 62 requests · 22.0s · typesafe-sdk 0.7.1`

The server was started in its own process group (39787) and stopped after the run with SIGTERM to the group. Afterwards the group had exited: True; port 8000 was free: True. Console output is in `console.txt`, the full report in `report.json` and `report.md`.
