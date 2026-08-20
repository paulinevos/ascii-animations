#!/usr/bin/env python3
"""An ASCII heart with the gradient scrolling through it.

    python3 heart_gradient.py
    python3 heart_gradient.py --size small --color red --style pulse
    python3 heart_gradient.py --fill glyphs --style wave-h

Two hearts: `large` is drawn from the heart equation, `small` is the seven-row
one from thankyou_gradient. `--fill ramp`, the default here, fills the shape
from a density ramp riding the same wave as the color, so the texture scrolls
with it. Ctrl-C to stop.
"""

import argparse
import os
import sys

# The shared gradient lives a directory up, and this script is run directly
# rather than imported, so its own directory is all that is on the path.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gradient  # noqa: E402  (needs the path above)

FILLED = "#"  # what a cell inside the heart holds before a fill is applied

WIDTH = 60
Y_TOP, Y_BOTTOM = 22, -22  # taller range than wide => elongated heart

# Hand-drawn rather than taken from the equation: at seven rows the equation
# loses the top cleft, and without that a small heart reads as a blob. Seven
# rows to match the height of the roman figlet font it sits beside in
# thankyou_gradient.
SMALL = [
    "  ####   ####  ",
    " ############# ",
    "###############",
    " ############# ",
    "  ###########  ",
    "    #######    ",
    "      ###      ",
]


def large():
    """The heart equation, evaluated per cell into rows of the block.

    y is scaled more gently than x, which stretches the shape vertically to
    make up for character cells being about twice as tall as they are wide.
    """
    rows = []
    for y in range(Y_TOP, Y_BOTTOM, -1):
        row = "".join(
            FILLED if inside(x, y) else " "
            for x in range(-WIDTH // 2, WIDTH // 2)
        )
        if row.strip():
            rows.append(row.rstrip())
    return rows


def inside(x, y):
    return (
        ((x * 0.05) ** 2 + (y * 0.085) ** 2 - 1) ** 3
        - (x * 0.05) ** 2 * (y * 0.085) ** 3
        <= 0
    )


def small():
    return list(SMALL)


SIZES = {"large": large, "small": small}


def arguments():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--size", default="large", choices=list(SIZES))
    # The ramp is the look this animation has always had, so it stays the
    # default here even though figlet_text defaults to its own letterforms.
    gradient.add_wave_arguments(parser, fill="ramp")
    return parser.parse_args()


def main():
    options = arguments()
    block = SIZES[options.size]()
    gradient.animate(
        gradient.frames_for(block, options), gradient.SPEEDS[options.speed]
    )


if __name__ == "__main__":
    main()
