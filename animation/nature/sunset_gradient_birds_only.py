#!/usr/bin/env python3
"""sunset.txt with flapping birds.

Everything except the birds is reproduced exactly as it appears in the art.
sunset.txt is colored per character rather than per row, so the art is parsed
into individual colored cells and only the birds' glyphs are substituted —
that way every cell keeps its own color. Ctrl-C to stop.
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


def build_frames(rows):
    rng = random.Random(SEED)
    # Phases are baked once so each bird flaps steadily and out of step with
    # the others, rather than being re-rolled into a twitch every frame.
    flaps = {
        bird: (rng.choice(PERIODS), rng.randrange(FRAMES))
        for bird in find_birds(rows)
    }

    frames = []
    for f in range(FRAMES):
        out = ["\033[H"]
        for y, cells in enumerate(rows):
            glyphs = [char for _, char in cells]
            for (by, bx), (period, phase) in flaps.items():
                if by != y:
                    continue
                wings = WINGS[((f + phase) % period) * len(WINGS) // period]
                glyphs[bx : bx + BIRD_WIDTH] = wings
            line = "".join(
                f"{color}{glyph}{RESET}" if color else glyph
                for (color, _), glyph in zip(cells, glyphs)
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
