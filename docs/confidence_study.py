"""Same answers, same threshold, different `confidence` definitions.

Reads every choice answer recorded in results/*/report.json, applies each definition of
`confidence` the measured servers use, and reports how many answers clear a threshold under
each. Writes docs/confidence.png. Run from the repo root: python docs/confidence_study.py
"""
from __future__ import annotations

import glob
import json
import math
from pathlib import Path

DEFINITIONS = {
    # label: (who uses it, function of the sorted probabilities)
    "TypeSafe's formula": ("kev, jeff, rizzo-flow, Open-Jev", lambda p: (len(p) * p[0] - 1) / (len(p) - 1)),
    "top probability": ("decider, simple-jev", lambda p: p[0]),
    "top-two margin": ("von", lambda p: p[0] - p[1]),
    "1 − normalised entropy": ("laya", lambda p: 1 + sum(q * math.log(q) for q in p if q > 0) / math.log(len(p))),
}


def answers() -> list[list[float]]:
    out = []
    for f in sorted(glob.glob("results/*/report.json")):
        for x in json.loads(Path(f).read_text())["exchanges"]:
            if x["status"] != 200 or x.get("via") != "http":
                continue
            try:
                body = json.loads(x["response"])
            except (json.JSONDecodeError, TypeError):
                continue  # a response too long to have been stored whole
            for a in (body.get("answers") or {}).values():
                if isinstance(a, dict) and a.get("type") == "choice" and isinstance(a.get("probabilities"), dict):
                    p = sorted((v for v in a["probabilities"].values() if isinstance(v, (int, float))), reverse=True)
                    if len(p) >= 2 and abs(sum(p) - 1) <= 0.05:
                        out.append(p)
    return out


def main() -> None:
    rows = answers()
    print(f"{len(rows)} choice answers")
    table = {}
    for t in (0.5, 0.8, 0.9):
        table[t] = {name: sum(f(p) >= t for p in rows) for name, (_, f) in DEFINITIONS.items()}
        print(t, {k: f"{v}/{len(rows)} ({v / len(rows):.0%})" for k, v in table[t].items()})
    doc = DEFINITIONS["TypeSafe's formula"][1]
    for name, (_, f) in DEFINITIONS.items():
        more = sum(f(p) >= 0.9 > doc(p) for p in rows)
        fewer = sum(doc(p) >= 0.9 > f(p) for p in rows)
        print(f"at 0.9, {name}: accepts {more} the documented formula rejects, rejects {fewer} it accepts")
    chart(table[0.9], len(rows))


def chart(counts: dict[str, int], total: int) -> None:
    from PIL import Image, ImageDraw, ImageFont
    fonts = Path.home() / "Documents/GitHub/sessionreel/src/sessionreel/fonts"
    f = lambda name, size: ImageFont.truetype(str(fonts / name), size)  # noqa: E731
    bg, ink, muted, grid, blue = (26, 26, 25), (236, 236, 233), (154, 154, 148), (58, 58, 55), (57, 135, 229)
    img = Image.new("RGB", (1200, 630), bg)
    d = ImageDraw.Draw(img)
    d.text((60, 44), "Same answers, same 0.9 threshold", font=f("InterDisplay-Bold.ttf", 44), fill=ink)
    d.text((60, 104), f"Share of {total} recorded answers auto-accepted, by each server's definition of confidence",
           font=f("Inter-Regular.ttf", 22), fill=muted)
    x0, x1, y = 60, 1080, 182
    scale = (x1 - 460) / 100
    for name, (who, _) in DEFINITIONS.items():
        pct = 100 * counts[name] / total
        d.text((x0, y + 2), name, font=f("Inter-SemiBold.ttf", 24), fill=ink)
        d.text((x0, y + 34), who, font=f("Inter-Regular.ttf", 19), fill=muted)
        bx = 460
        d.line((bx, y - 6, bx, y + 70), fill=grid, width=1)
        w = max(4, round(pct * scale))
        d.rounded_rectangle((bx, y + 8, bx + w, y + 52), radius=4, fill=blue)
        d.text((bx + w + 12, y + 12), f"{pct:.0f}%", font=f("InterDisplay-Bold.ttf", 30), fill=ink)
        y += 96
    d.text((60, 586), "Data and script: github.com/mandu5/jevcompat (docs/confidence_study.py)", font=f("Inter-Regular.ttf", 19), fill=muted)
    img.save("docs/confidence.png", optimize=True)
    print("wrote docs/confidence.png")


if __name__ == "__main__":
    main()
