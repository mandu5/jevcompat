"""Render docs/cover.png (1200x630) from results/*/report.json. Run from the repo root."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONTS = Path.home() / "Documents/GitHub/sessionreel/src/sessionreel/fonts"
ORDER = ["kev", "decider", "von", "rizzo-flow", "open-jev", "laya", "jeff", "simple-jev"]
NAMES = {"kev": "jaredpalmer/kev", "decider": "Mapika/decider", "von": "wfzyx/von", "rizzo-flow": "Rizzo-AI-Academy/rizzo-flow",
         "open-jev": "Zefan-Cai/Open-Jev", "laya": "NandhaKishorM/laya", "jeff": "logan-markewich/jeff",
         "simple-jev": "featherless-ai/simple-jev"}
BG, FG, DIM, GREEN, RED, LINE = (13, 17, 23), (230, 237, 243), (125, 133, 144), (63, 185, 80), (248, 81, 73), (48, 54, 61)


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / name), size)


def main() -> None:
    img = Image.new("RGB", (1200, 630), BG)
    d = ImageDraw.Draw(img)
    d.text((60, 48), "jevcompat", font=font("JetBrainsMono-Bold.ttf", 56), fill=FG)
    d.text((60, 122), "A spec and conformance suite for Jev-compatible servers", font=font("Inter-Regular.ttf", 28), fill=DIM)
    d.text((60, 168), "48 requirements · every check proven to fail · 8 servers measured", font=font("Inter-Regular.ttf", 22), fill=DIM)
    y = 226
    mono, mono_b = font("JetBrainsMono-Regular.ttf", 24), font("JetBrainsMono-Bold.ttf", 24)
    d.line((60, y - 12, 1140, y - 12), fill=LINE, width=2)
    for name in ORDER:
        s = json.loads(Path(f"results/{name}/report.json").read_text())["summary"]
        ok = s["verdict"] == "conformant"
        must = f"{s['MUST']['passed']}/{s['MUST']['tested']} MUST"
        d.text((60, y), "✓" if ok else "✗", font=mono_b, fill=GREEN if ok else RED)
        d.text((100, y), NAMES[name], font=mono, fill=FG)
        d.text((720, y), must, font=mono_b if ok else mono, fill=GREEN if ok else FG)
        d.text((920, y), "conformant" if ok else "not conformant", font=mono, fill=GREEN if ok else DIM)
        y += 42
    d.line((60, y + 4, 1140, y + 4), fill=LINE, width=2)
    d.text((60, y + 18), "github.com/mandu5/jevcompat", font=font("Inter-SemiBold.ttf", 22), fill=DIM)
    img.save("docs/cover.png", optimize=True)
    print("wrote docs/cover.png")


if __name__ == "__main__":
    main()
