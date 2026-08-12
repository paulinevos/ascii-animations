#!/usr/bin/env python3
"""moon.txt with twinkling stars.

The moon itself is left alone; the scattered stars cycle through a brightness
ramp of glyphs, each on its own period and phase so they twinkle out of step
with each other. Row colors are taken straight from moon.txt. Ctrl-C to stop.
"""

import os
import random
import re
import sys
import time

ART = os.path.join(os.path.dirname(os.path.abspath(__file__)), "moon.txt")
RESET = "\033[0m"
ANSI = re.compile(r"\033\[[0-9;]*m")

FRAMES = 48  # one full loop
SPEED = 0.12  # slower than the gradient pieces; twinkling shouldn't strobe
SEED = 11  # fixed so the twinkle pattern is the same every run
# Periods must divide FRAMES, otherwise the loop seams visibly.
PERIODS = (8, 12, 16, 24)
MOON_RUN = 3  # horizontal run of "*" this long or longer is moon, not a star

# Brightness ramps, dimmest to brightest, keyed by the glyph in the source art.
# Each star walks its ramp forwards and back, so it fades up and down rather
# than snapping from brightest to dimmest.
RAMPS = {
    "*": (".", "+", "*", "*"),
    ".": ("`", ".", ",", "."),
    "+": ("+", "x", "*", "x"),
    "-": ("-",),  # the arms of a -+- star stay put; only its center twinkles
}


def load():
    """Rows of (color, text) from the art, with escape codes stripped."""
    rows = []
    for line in open(ART).read().split("\n"):
        if not line:
            continue
        color = ANSI.match(line)
        rows.append((color.group(0) if color else "", ANSI.sub("", line)))
    return rows


def is_moon(text, x):
    """True if this cell sits in a horizontal run of "*" of at least MOON_RUN.

    The moon is a solid block of asterisks and the stars are isolated marks,
    so run length separates them without hardcoding the moon's position.
    """
    if text[x] != "*":
        return False
    left = x
    while left > 0 and text[left - 1] == "*":
        left -= 1
    right = x
    while right + 1 < len(text) and text[right + 1] == "*":
        right += 1
    return right - left + 1 >= MOON_RUN


def build_frames(rows):
    rng = random.Random(SEED)
    # Per-star period and phase, assigned once. Baked here rather than rolled
    # per frame so a given star pulses steadily instead of flickering.
    stars = {}
    for y, (_, text) in enumerate(rows):
        for x, ch in enumerate(text):
            if ch == " " or is_moon(text, x) or ch not in RAMPS:
                continue
            stars[(y, x)] = (rng.choice(PERIODS), rng.randrange(FRAMES))

    frames = []
    for f in range(FRAMES):
        out = ["\033[H"]
        for y, (color, text) in enumerate(rows):
            line = list(text)
            for x, ch in enumerate(line):
                star = stars.get((y, x))
                if star is None:
                    continue
                period, phase = star
                ramp = RAMPS[ch]
                line[x] = ramp[((f + phase) % period) * len(ramp) // period]
            out.append(f"{color}{''.join(line).rstrip()}{RESET}\n")
        frames.append("".join(out))
    return frames


def main():
    frames = build_frames(load())

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
