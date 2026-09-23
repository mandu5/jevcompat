# von: run record

| field | value |
|---|---|
| repo | https://github.com/wfzyx/von |
| commit | `657f42f45fcfbf8cbfceaff7af5a2193dcec2b8b` (2026-09-23 03:30:20 -0400, "bench(hard): add --tier flag to reuse the fixed harness for standard/easy tiers") |
| license | Apache-2.0 (LICENSE.md) |
| weights | `wfzyx/von` @ `d8bb5e0745d8ee1fb65d536d6d4892d54d5a93fd` (`option_marker.pt`, `marker_calibration.json`, config and tokenizer; von 1.1.0) |
| port | 8000 |
| env vars | `(none)` |
| device | MPS (auto) |
| date/time of run | 2026-09-24 08:06:44 KST (2026-09-23T23:06:44Z) |
| machine | Apple M1 Pro, 16 GB RAM (17179869184 bytes), macOS 26.6.1 (25G76) |
| jevcompat | jevcompat 0.1.0 (spec 0.1), commit `6a8a543dcece158896c4ad652480143c2266f37f` (clean tree); source hash `be5d4703795e75eb61bfaa7f63037ba25bbe4f7b1ef63b4bc89e03985474cb60` (`find src/jevcompat -name '*.py' \| sort \| xargs cat \| shasum -a 256`), unchanged after the run: True; typesafe-sdk 0.7.1 (the drop-in check ran) |
| wall time | 10 s for the jevcompat run (exit code 1); the report records 62 exchanges in 9.8 s. The server was ready 4.1 s after start. |
| verdict (as printed) | `not conformant to spec 0.1: MUST 31/32, SHOULD 8/12` |
| summary | MUST 31/32 passed (1 failed, 1 not tested); SHOULD 8/12 passed (4 failed, 3 not tested) |

## Install

```bash
cd ./bench/von
git clone https://github.com/wfzyx/von.git src               # checked out at HEAD 657f42f
uv venv -p 3.12 .venv                                         # Python 3.12.4
uv pip install -p .venv/bin/python ./src
# resolved: von-sdk 1.1.1, torch 2.14.0, transformers 5.17.0, fastapi 0.141.1, uvicorn 0.53.0
```

von fetches `wfzyx/von` from the Hub without pinning a revision (`option_marker_backend.py:203`). The repo was pre-fetched once at the then-current `main`, `d8bb5e0`, and the server loaded that snapshot from the HF cache. No HF token was used.

## Serve

```bash
.venv/bin/von serve --host 127.0.0.1 --port 8000
```

No env vars were set. `VON_API_KEY` is unset, so auth is off. `--device` was left at its default, auto; the startup log reads `von-1.1 on Apple Silicon [MPS]`. `--host` defaults to 0.0.0.0 and was set to loopback.

## Test

```bash
~/Documents/GitHub/jevcompat/.venv/bin/jevcompat test http://127.0.0.1:8000 --timeout 300 --json ~/Documents/GitHub/jevcompat/results/von/report.json --markdown ~/Documents/GitHub/jevcompat/results/von/report.md --title "wfzyx/von @ 657f42f"
```

`model sent 'jev-latest', server reports 'von-1.1.0' · 62 requests · 9.8s · typesafe-sdk 0.7.1`

The server was started in its own process group (41126) and stopped after the run with SIGTERM to the group. Afterwards the group had exited: True; port 8000 was free: True. Console output is in `console.txt`, the full report in `report.json` and `report.md`.
