#!/usr/bin/env python3
"""A divider with a horizontal gradient travelling along it.

    python3 divider_gradient.py divider_green.txt

The gradient is built from the divider's OWN color: a wave sweeps left to
right, lightening the glyphs toward white at its crest and darkening them in
its trough, so the divider shimmers in lighter and darker hues of itself
rather than changing color. A few glyphs are swapped for near-identical
shapes at the crest to make the light look like it's catching on them.

Color is read per character, so this works for the multi-colored divider.txt
as well as the single-color ones. Ctrl-C to stop.
"""

import math
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RESET = "\033[0m"
TOKEN = re.compile(r"(\033\[[0-9;]*m)|(.)", re.S)
RGB = re.compile(r"\033\[38;2;(\d+);(\d+);(\d+)m")

FRAMES = 48  # one full loop
SPEED = 0.08
WAVE = 18  # columns per gradient cycle; the whole wave is this wide
LIGHTEN = 0.55  # how far the crest mixes toward white
DARKEN = 0.45  # how far the trough mixes toward black

# Swapped in only at the crest of the wave. Each pair is the same shape at a
# different height or angle, so the divider's silhouette barely moves — the
# point is a glint, not a change of pattern.
SWAPS = {"°": "˚", "˚": "°", "¸": ",", ",": "¸", "`": "´"}
# Level above which a glyph is swapped. Tuned so only 4-9 of the ~77 glyphs
# differ at any moment; lower thresholds swapped enough of them at once to
# read as the pattern changing rather than as light moving along it.
CREST = 0.95


def load(name):
    """Cells of (rgb, char) for the divider's single line."""
    path = os.path.join(HERE, name)
    line = next(l for l in open(path).read().split("\n") if l.strip())
    cells, rgb = [], None
    for escape, char in TOKEN.findall(line):
        if escape:
            match = RGB.match(escape)
            # a reset ends the run; a color escape starts a new one
            rgb = tuple(int(v) for v in match.groups()) if match else None
        else:
            cells.append((rgb, char))
    return cells


def shade(rgb, level):
    """The base color lightened or darkened according to level in [0, 1]."""
    if rgb is None:
        return None
    if level >= 0.5:
        t = (level - 0.5) * 2 * LIGHTEN
        return tuple(round(c + (255 - c) * t) for c in rgb)
    t = (0.5 - level) * 2 * DARKEN
    return tuple(round(c * (1 - t)) for c in rgb)


def build_frames(cells):
    frames = []
    for f in range(FRAMES):
        out = ["\033[H"]
        line = []
        for x, (rgb, char) in enumerate(cells):
            # subtracting the step sweeps the crest rightwards over time
            phase = x / WAVE - f / FRAMES
            level = (1 + math.sin(2 * math.pi * phase)) / 2
            glyph = SWAPS.get(char, char) if level > CREST else char
            lit = shade(rgb, level)
            line.append(
                f"\033[38;2;{lit[0]};{lit[1]};{lit[2]}m{glyph}{RESET}" if lit else glyph
            )
        out.append(f"{''.join(line)}\n")
        frames.append("".join(out))
    return frames


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "divider.txt"
    frames = build_frames(load(name))

    sys.stdout.write("\033[?25l\033[2J")  # hide cursor, clear once
    try:
        while True:
            for frame in frames:
                sys.stdout.write(frame)
                sys.stdout.flush()
                time.sleep(SPEED)
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write(f"\033[?25h{RESET}\n")


if __name__ == "__main__":
    main()
