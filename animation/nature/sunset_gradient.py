#!/usr/bin/env python3
"""sunset.txt with flapping birds, moving waves, and twinkles on the water.

sunset.txt is colored per character rather than per row, so the art is parsed
into individual colored cells and only the animated cells' glyphs are
substituted — that way every cell keeps its own color. The sun, the horizon
band, and the sunset-tinted water under the sun are left exactly as drawn;
only the blue water either side moves. Ctrl-C to stop.

assets/sunset_gradient_birds_only.py is the birds-only fallback version.
"""

import os
import random
import re
import sys
import time

ART = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sunset.txt")
RESET = "\033[0m"
TOKEN = re.compile(r"(\033\[[0-9;]*m)|(.)", re.S)

FRAMES = 48  # one full loop
SPEED = 0.14  # a calm flap, not a flutter
SEED = 23  # fixed so the birds' phases are the same every run

BIRD = "^"  # the glyph the art draws birds with
BIRD_WIDTH = 2  # a bird is a pair of glyphs, animated as one unit
# Wing positions, cycled in order. Down-up-down rather than a hard reset, so
# the wings sweep back through the middle instead of snapping.
WINGS = ("^^", "--", "vv", "--")
# Periods must divide FRAMES, otherwise the loop seams visibly.
PERIODS = (8, 12)

WATER = "~"  # the glyph the art draws water with
# Only the two blue tones move. The lavender, pink and orange "~" are the
# sun's reflection tinting the water, and holding those still keeps the
# reflection reading as a reflection rather than as more churn.
BLUE = ("\033[38;2;124;213;241m", "\033[38;2;80;170;220m")
WAVE_SHARE = 0.35  # fraction of blue water that moves; the rest stays put
WAVE_GLYPHS = ("~", "-", "~", "~")  # mostly at rest, dipping through flat
WAVE_PERIODS = (12, 16, 24)

# White twinkles: a handful of water cells catching the light, each one lit
# for only a few frames of a long period so they read as occasional glints
# rather than a second layer of animation.
TWINKLES = 7
TWINKLE_GLYPHS = (".", "*", "+", ".")  # the lit frames, in order
TWINKLE_PERIODS = (24, 48)
WHITE = "\033[38;2;242;255;252m"


def load():
    """Rows of cells, each cell a (color, char) pair.

    The art carries a color escape before nearly every character, so color is
    tracked per cell; keeping only one color per row would flatten the sunset.
    """
    rows = []
    for line in open(ART).read().split("\n"):
        if not line:
            continue
        cells, color = [], ""
        for escape, char in TOKEN.findall(line):
            if escape:
                # a reset ends the current run; any other escape starts one
                color = "" if escape == RESET else escape
            else:
                cells.append((color, char))
        rows.append(cells)
    return rows


def find_birds(rows):
    """Left-hand column of every bird, found by scanning for runs of BIRD.

    Runs are chopped into BIRD_WIDTH-wide marks so each bird animates as one
    unit and its glyphs stay in step. Positions come from the art itself, so
    editing sunset.txt moves the birds without touching this script.
    """
    birds = []
    for y, cells in enumerate(rows):
        x = 0
        while x < len(cells):
            if cells[x][1] != BIRD:
                x += 1
                continue
            run = x
            while run < len(cells) and cells[run][1] == BIRD:
                run += 1
            # a trailing odd glyph is left alone rather than half-animated
            for start in range(x, run - BIRD_WIDTH + 1, BIRD_WIDTH):
                birds.append((y, start))
            x = run
    return birds


def find_blue_water(rows):
    """Every water cell drawn in one of the blue tones."""
    return [
        (y, x)
        for y, cells in enumerate(rows)
        for x, (color, char) in enumerate(cells)
        if char == WATER and color in BLUE
    ]


def build_frames(rows):
    rng = random.Random(SEED)
    # Everything random is baked once here. Re-rolling per frame turns steady
    # motion into flickering static — the same trap as the heart's grain.
    flaps = {
        bird: (rng.choice(PERIODS), rng.randrange(FRAMES))
        for bird in find_birds(rows)
    }

    blue = find_blue_water(rows)
    waves = {
        cell: (rng.choice(WAVE_PERIODS), rng.randrange(FRAMES))
        for cell in rng.sample(blue, round(len(blue) * WAVE_SHARE))
    }
    twinkles = {
        cell: (rng.choice(TWINKLE_PERIODS), rng.randrange(FRAMES))
        for cell in rng.sample(blue, TWINKLES)
    }

    frames = []
    for f in range(FRAMES):
        out = ["\033[H"]
        for y, cells in enumerate(rows):
            glyphs = [char for _, char in cells]
            colors = [color for color, _ in cells]

            for (by, bx), (period, phase) in flaps.items():
                if by != y:
                    continue
                wings = WINGS[((f + phase) % period) * len(WINGS) // period]
                glyphs[bx : bx + BIRD_WIDTH] = wings

            for x in range(len(cells)):
                wave = waves.get((y, x))
                if wave:
                    period, phase = wave
                    step = ((f + phase) % period) * len(WAVE_GLYPHS) // period
                    glyphs[x] = WAVE_GLYPHS[step]
                # a twinkle overrides the wave beneath it, and is the one
                # place the art's own color is replaced
                twinkle = twinkles.get((y, x))
                if twinkle:
                    period, phase = twinkle
                    step = (f + phase) % period
                    if step < len(TWINKLE_GLYPHS):
                        glyphs[x] = TWINKLE_GLYPHS[step]
                        colors[x] = WHITE

            line = "".join(
                f"{color}{glyph}{RESET}" if color else glyph
                for color, glyph in zip(colors, glyphs)
            )
            out.append(f"{line.rstrip()}\n")
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
