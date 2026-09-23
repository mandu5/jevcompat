# rizzo-flow: run record

| field | value |
|---|---|
| repo | https://github.com/Rizzo-AI-Academy/rizzo-flow |
| commit | `d34665b7a28c62b79f37939f2fd83f5fe659fbf9` (2026-09-22 01:31:41 +0200, "README: Contributors section, with BiG86 and what their pull request changed") |
| license | Apache-2.0 (LICENSE and NOTICE files; weights Apache-2.0 per the README) |
| weights | `XHToken/Spark-X2.5-1.7B-GGUF` @ `1f7fa33b1245c14730da39e125714ad3a327901b`, file `Spark-X2.5-1.7B-Q8_0.gguf` (sha256 `cd77c03185a834bb1162a4b7713520be5838058bfc54873645beff470bb24442`), converted from `XHToken/Spark-X2.5-1.7B` @ `14d6e83c13c7add2b62a7c39b2131f4ed1cddcf8`; runtime llama.cpp release `b11081` (commit `161755f29e415e2c33efe906e91843c068efd664`), darwin-arm64-metal build |
| port | 8017 |
| env vars | `(none)` |
| device | Metal (llama.cpp), Q8_0 |
| date/time of run | 2026-09-24 08:20:46 KST (2026-09-23T23:20:46Z) |
| machine | Apple M1 Pro, 16 GB RAM (17179869184 bytes), macOS 26.6.1 (25G76) |
| jevcompat | jevcompat 0.1.0 (spec 0.1), commit `6a8a543dcece158896c4ad652480143c2266f37f` (clean tree); source hash `be5d4703795e75eb61bfaa7f63037ba25bbe4f7b1ef63b4bc89e03985474cb60` (`find src/jevcompat -name '*.py' \| sort \| xargs cat \| shasum -a 256`), unchanged after the run: True; typesafe-sdk 0.7.1 (the drop-in check ran) |
| wall time | 11 s for the jevcompat run (exit code 1); the report records 60 exchanges in 11.3 s. The server was ready 2.1 s after start. |
| verdict (as printed) | `not conformant to spec 0.1: MUST 31/32, SHOULD 9/12` |
| summary | MUST 31/32 passed (1 failed, 1 not tested); SHOULD 9/12 passed (3 failed, 3 not tested) |

## Install

```bash
cd ./bench/rizzo-flow
git clone https://github.com/Rizzo-AI-Academy/rizzo-flow.git src   # checked out at HEAD d34665b
cd src
export UV_PROJECT_ENVIRONMENT=./bench/rizzo-flow/.venv
uv sync --locked                                                    # Python 3.12.4, rizzo-flow 0.1.0
../.venv/bin/rizzo download --size 1.7b                             # llama.cpp b11081 metal + Spark-X2.5-1.7B Q8_0 (1.8 GB) into src/runtimes, src/models (git-ignored)
```

The README offers `--size 1.7b` as the smaller GGUF (Q8_0, 1.8 GB), and it was used as instructed. The README's default is the 4B Q8_0, 4.4 GB, and it calls the 1.7B "much less accurate".

## Serve

```bash
cd src && ../.venv/bin/rizzo serve --size 1.7b
```

No env vars were set. `RIZZO_API_KEY` is unset, so auth is off. The defaults are host 127.0.0.1, port 8017 and `--device auto`; `/health` reports `"device":"gpu","backend":"mtl","device_name":"Apple M1 Pro"`.

## Test

```bash
~/Documents/GitHub/jevcompat/.venv/bin/jevcompat test http://127.0.0.1:8017 --timeout 300 --json ~/Documents/GitHub/jevcompat/results/rizzo-flow/report.json --markdown ~/Documents/GitHub/jevcompat/results/rizzo-flow/report.md --title "Rizzo-AI-Academy/rizzo-flow @ d34665b"
```

`model sent 'jev-latest', server reports 'rizzo-spark-x2.5-1.7b-q8_0' · 60 requests · 11.3s · typesafe-sdk 0.7.1`

The server was started in its own process group (76067) and stopped after the run with SIGTERM to the group. Afterwards the group had exited: True; port 8017 was free: True. Console output is in `console.txt`, the full report in `report.json` and `report.md`.
