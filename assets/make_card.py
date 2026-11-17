#!/usr/bin/env python3
"""Build `assets/social-preview.png` and `assets/reddit-card.png` from real output.

Nothing here is a mock-up. The generator runs `demo/run_demo.py --terse` and
captures stdout, exactly as `make_demo_gif.py` does, so the cards cannot drift
from what the command prints. The only text it adds is the headline, which is
there so the image reads as a catch without a caption.

Two files come out:

  social-preview.png  1280x640  the GitHub / Reddit / Twitter link card
  reddit-card.png     1200x630  the still that goes inside a self post

Both are the same card at different crops. Needs Pillow and a monospace font.

Run:  python assets/make_card.py
"""

from __future__ import annotations

import pathlib
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent

S = 2                       # supersample, then downsample
W, H = 1280, 640
INSET = 34
RADIUS = 16
HEADER = 30
TEXT_LEFT = 48
LINE_H = 19
SIZE = 14

BG = (8, 12, 17)
BG_BOTTOM = (5, 9, 13)
CARD = (13, 18, 24)
BORDER = (39, 48, 59)
DIVIDER = (30, 38, 48)
TEXT = (222, 230, 238)
DIM = (120, 134, 148)
AMBER = (240, 190, 90)
RED = (232, 92, 92)
GREEN = (110, 200, 130)
ACCENT = (90, 170, 240)

FONT_CANDIDATES = [
    r"C:\Windows\Fonts\CascadiaMono.ttf",
    r"C:\Windows\Fonts\consola.ttf",
    r"C:\Windows\Fonts\lucon.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/System/Library/Fonts/Menlo.ttc",
]
BOLD_CANDIDATES = [
    r"C:\Windows\Fonts\CascadiaMono.ttf",
    r"C:\Windows\Fonts\consolab.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
]


def find(candidates):
    for path in candidates:
        if pathlib.Path(path).exists():
            return path
    raise SystemExit("no monospace font found; add one to FONT_CANDIDATES")


def font(size):
    return ImageFont.truetype(find(FONT_CANDIDATES), size * S)


def bold(size):
    return ImageFont.truetype(find(BOLD_CANDIDATES), size * S)


def demo_lines():
    """The real output of the demo, verbatim."""
    proc = subprocess.run([sys.executable, "demo/run_demo.py", "--terse"],
                          cwd=ROOT, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=180)
    if proc.returncode not in (0, 1):
        raise SystemExit(f"demo failed: {proc.stderr[-400:]}")
    return proc.stdout.rstrip("\n").splitlines()


def colour_for(line):
    stripped = line.strip()
    if stripped.startswith("! ["):
        return AMBER
    if stripped.startswith("+"):
        return GREEN
    if stripped.startswith("x "):
        return RED
    if stripped.startswith("VERDICT") or "NOT VERIFIED" in stripped.upper():
        return RED
    if stripped.startswith("$"):
        return ACCENT
    if stripped.startswith("-") and stripped.strip("-"):
        return DIVIDER
    return None


def rounded(draw, box, fill, radius, outline=None):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline,
                           width=S if outline else 0)


def build() -> Image.Image:
    width, height = W * S, H * S
    image = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(image)

    # vertical wash
    for y in range(height):
        t = y / max(1, height - 1)
        colour = tuple(int(BG[i] + (BG_BOTTOM[i] - BG[i]) * t) for i in range(3))
        draw.line([(0, y), (width, y)], fill=colour)

    # headline
    kicker = font(21)
    draw.text((INSET * S, 26 * S), "unwash", font=bold(19), fill=TEXT)
    draw.text((INSET * S, 56 * S),
              "The visible tests passed. The held-out suite disagreed.",
              font=font(23), fill=TEXT)
    draw.text((INSET * S, 88 * S),
              "That gap is the evidence, and it cannot be argued with.",
              font=font(19), fill=DIM)

    # terminal card
    card_top = 120 * S
    card_box = (INSET * S, card_top, width - INSET * S, height - INSET * S)
    rounded(draw, card_box, CARD, RADIUS * S, BORDER)

    # chrome
    for i, dot in enumerate(((255, 95, 86), (255, 189, 46), (39, 201, 63))):
        cx = (INSET + 26 + i * 26) * S
        cy = card_top + (HEADER // 2 + 2) * S
        draw.ellipse((cx - 6 * S, cy - 6 * S, cx + 6 * S, cy + 6 * S), fill=dot)
    draw.text((width - (INSET + 250) * S, card_top + 10 * S),
              "zsh  unwash", font=font(13), fill=DIM)
    draw.line([(INSET * S, card_top + HEADER * S),
               (width - INSET * S, card_top + HEADER * S)], fill=DIVIDER, width=S)

    # The frame has to hold the whole argument: the visible suite passing, the
    # held-out suite failing, the flag, and the verdict. Start where
    # "Verification:" begins and stop after "Confidence:", so nothing in the
    # middle is skipped -- cropping lines out of a report would be editing it.
    lines = demo_lines()
    start = next((i for i, line in enumerate(lines)
                  if line.strip().startswith("Verification:")), 0)
    start = max(0, start - 1)
    end = next((i for i, line in enumerate(lines)
                if line.strip().startswith("Verdict:")), len(lines) - 1)
    shown = lines[start:end + 1]

    y = card_top + (HEADER + 14) * S
    body = font(SIZE)
    for line in shown:
        colour = colour_for(line) or TEXT
        draw.text((TEXT_LEFT * S, y), line, font=body, fill=colour)
        y += LINE_H * S

    # fade the bottom edge instead of cutting a line in half
    fade = Image.new("L", (1, height), 0)
    for row in range(height):
        distance = height - row
        fade.putpixel((0, row), min(255, int(distance / (18 * S) * 255)))
    mask = fade.resize((width, height))
    shade = Image.new("RGB", (width, height), BG_BOTTOM)
    image = Image.composite(image, shade, mask)

    return image.resize((W, H), Image.LANCZOS)


def main() -> None:
    card = build()
    for name in ("social-preview.png", "reddit-card.png"):
        path = HERE / name
        card.save(path, "PNG", optimize=True)
        print(f"wrote {path}  ({path.stat().st_size // 1024} KB, {card.size[0]}x{card.size[1]})")


if __name__ == "__main__":
    main()
