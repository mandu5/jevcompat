# open-jev: run record

| field | value |
|---|---|
| repo | https://github.com/Zefan-Cai/Open-Jev |
| commit | `3308a15ccd7eea1df7a37d6ddc39b023b801ba16` (2026-09-23 02:27:00 -0700, "Add the v1.1 game arcade and verified demo page post") |
| license | code MIT (LICENSE file; `pyproject.toml` license = "MIT"); weights Apache-2.0 (HF card) |
| weights | package `ZefanCai/Open-Jev-2B` @ `0c7aa498b1627be8da4acf34c863ff0ee0a92785` (LoRA adapter, decision head and temperature; checkpoint sha256 `3076462e6356412082e79af909227b39b2863b90def79155ca0821aa506b7ded` as reported by the server), downloaded to `bench/open-jev/models/Open-Jev-2B`; base `Qwen/Qwen3.5-2B` @ `15852e8c16360a2fea060d615a32b45270f8a8fc` (the revision the package's `model.json` pins) |
| port | 8791 |
| env vars | `(none)` |
| device | MPS, bfloat16 |
| date/time of run | 2026-09-24 08:21:14 KST (2026-09-23T23:21:14Z) |
| machine | Apple M1 Pro, 16 GB RAM (17179869184 bytes), macOS 26.6.1 (25G76) |
| jevcompat | jevcompat 0.1.0 (spec 0.1), commit `6a8a543dcece158896c4ad652480143c2266f37f` (clean tree); source hash `be5d4703795e75eb61bfaa7f63037ba25bbe4f7b1ef63b4bc89e03985474cb60` (`find src/jevcompat -name '*.py' \| sort \| xargs cat \| shasum -a 256`), unchanged after the run: True; typesafe-sdk 0.7.1 (the drop-in check ran) |
| wall time | 115 s for the jevcompat run (exit code 1); the report records 62 exchanges in 114.5 s. The server was ready 15.1 s after start. |
| verdict (as printed) | `not conformant to spec 0.1: MUST 31/32, SHOULD 9/12` |
| summary | MUST 31/32 passed (1 failed, 1 not tested); SHOULD 9/12 passed (3 failed, 3 not tested) |

## Install

```bash
cd ./bench/open-jev
git clone https://github.com/Zefan-Cai/Open-Jev.git src      # checked out at HEAD 3308a15
uv venv -p 3.12 .venv                                         # Python 3.12.4
uv pip install -p .venv/bin/python -e './src[train]'
# resolved: open-jev 0.1.0.dev0, torch 2.14.0, transformers 5.10.2, peft 0.19.1, accelerate 1.13.0
python -c 'from huggingface_hub import snapshot_download as s; s("ZefanCai/Open-Jev-2B", revision="0c7aa498b1627be8da4acf34c863ff0ee0a92785", local_dir="models/Open-Jev-2B"); s("Qwen/Qwen3.5-2B", revision="15852e8c16360a2fea060d615a32b45270f8a8fc")'
```

`.[train]` is the README's install extra. The model package is used as the README describes: `--checkpoint <package>/checkpoint`.

## Serve

```bash
cd src && ../.venv/bin/python -m jev.server --checkpoint ../models/Open-Jev-2B/package/checkpoint --device mps --max-length 4096
```

No env vars were set. `--device mps` replaces the default `cuda:0`, which does not exist on this Mac. The model loads in bfloat16 (`jev/model.py:90`), and transformers logs that the flash-linear-attention fast path is missing, so it falls back to the torch implementation. `--max-length 4096` is the README value. The server binds 127.0.0.1:8791 by default. There is no auth, and `--prefix-cache` is off (the default).

## Test

```bash
~/Documents/GitHub/jevcompat/.venv/bin/jevcompat test http://127.0.0.1:8791 --timeout 300 --json ~/Documents/GitHub/jevcompat/results/open-jev/report.json --markdown ~/Documents/GitHub/jevcompat/results/open-jev/report.md --title "Zefan-Cai/Open-Jev @ 3308a15"
```

`model sent 'jev-latest', server reports 'Qwen/Qwen3.5-2B' · 62 requests · 114.5s · typesafe-sdk 0.7.1`

The server was started in its own process group (76720) and stopped after the run with SIGTERM to the group. Afterwards the group had exited: True; port 8791 was free: True. Console output is in `console.txt`, the full report in `report.json` and `report.md`.
