#!/usr/bin/env python3
"""The PHP logo: its slanted wordmark inside its ellipse.

    python3 php_logo.py
    python3 php_logo.py --style wave-h --color rainbow
    python3 php_logo.py --font smslant --speed slow

The letters come from figlet's `slant`, which is the closest thing on hand to
the logo's own slanted lowercase. The ellipse is drawn around whatever the font
gives, so a different font still lands inside it. Requires figlet on PATH.
Ctrl-C to stop.
"""

import argparse
import math
import os
import shutil
import subprocess
import sys

# The shared gradient lives a directory up, and this script is run directly
# rather than imported, so its own directory is all that is on the path.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gradient  # noqa: E402  (needs the path above)

WORD = "php"
RING = "#"
ASPECT = 2.0  # character cells are about twice as tall as they are wide
# Columns and rows of clearance between the wordmark and the ellipse. Wider
# than tall, because the logo's oval is flat rather than round.
PAD_X, PAD_Y = 7, 2
# How thick the ellipse's edge is, in fractions of its own radius. Measured in
# that normalised space rather than in cells so the ring keeps an even width
# all the way round instead of thinning at the top and bottom.
THICKNESS = 0.14


def figlet(text, font):
    """The text as figlet draws it, blank rows dropped."""
    try:
        drawn = subprocess.run(
            ["figlet", "-f", font, "-w", "200", text],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    except subprocess.CalledProcessError as refused:
        sys.exit(refused.stderr.strip() or f"figlet could not draw with font {font!r}")
    return [line.rstrip() for line in drawn.split("\n") if line.strip()]


def on_ring(x, y, width, rows):
    """Whether a cell falls on the ellipse's edge."""
    centre_x, centre_y = (width - 1) / 2, (rows - 1) / 2
    radius_x, radius_y = width / 2, rows * ASPECT / 2
    distance = math.sqrt(
        ((x - centre_x) / radius_x) ** 2
        + (((y - centre_y) * ASPECT) / radius_y) ** 2
    )
    return 1 - THICKNESS <= distance <= 1


def logo(font):
    """The wordmark centred inside its ellipse."""
    letters = figlet(WORD, font)
    text_width, text_height = max(len(line) for line in letters), len(letters)
    width, rows = text_width + PAD_X * 2, text_height + PAD_Y * 2
    grid = [
        [RING if on_ring(x, y, width, rows) else " " for x in range(width)]
        for y in range(rows)
    ]
    return ["".join(row).rstrip() for row in lettered(grid, letters, width, rows)]


def lettered(grid, letters, width, rows):
    """The grid with the wordmark written into the middle of it."""
    top = (rows - len(letters)) // 2
    left = (width - max(len(line) for line in letters)) // 2
    for y, line in enumerate(letters):
        for x, char in enumerate(line):
            if char != " ":
                grid[top + y][left + x] = char
    return grid


def arguments():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--font", default="slant", help="any figlet font name")
    gradient.add_wave_arguments(parser, color="php")
    return parser.parse_args()


def main():
    if not shutil.which("figlet"):
        sys.exit("figlet not found on PATH (brew install figlet)")

    options = arguments()
    gradient.animate(
        gradient.frames_for(logo(options.font), options),
        gradient.SPEEDS[options.speed],
    )


if __name__ == "__main__":
    main()
