#!/usr/bin/env python3
"""The MongoDB leaf, with the gradient scrolling through it.

    python3 mongodb_leaf.py
    python3 mongodb_leaf.py --style pulse --fill ramp
    python3 mongodb_leaf.py --color rainbow --speed slow

The mark is three curved segments around a vein, but at sixteen rows two gaps
read as stripes rather than as a leaf, so only the vein is drawn. The centre
line drifts as it rises, which is the tilt the mark has. Ctrl-C to stop.
"""

import argparse
import math
import os
import sys

# The shared gradient lives a directory up, and this script is run directly
# rather than imported, so its own directory is all that is on the path.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gradient  # noqa: E402  (needs the path above)

FILLED = "#"  # what a cell inside the leaf holds before a fill is applied

# Sixteen rows against twenty-one columns: character cells are about twice as
# tall as they are wide, so this reads as the tall, narrow leaf the mark is
# rather than as a circle.
ROWS = 16
HALF = 9.5  # half the leaf at its widest, in columns
BULGE = 1.6  # above 1 moves the widest part down the leaf, toward the base
POINT = 1.0  # raising the sine sharpens the tip and the base
LEAN = 2.5  # columns the centre line drifts right between base and tip
VEIN_MIN_HALF = 3.0  # the vein is only cut where there is leaf either side
SPAN = int(HALF) + 1


def half_at(y):
    """Half the leaf's width at a row, tapering to a point at either end."""
    # sin is pointed at both ends and widest in between, which is the outline
    # wanted; t ** BULGE skews where the widest part falls.
    across = (y + 0.5) / ROWS
    return HALF * math.sin(math.pi * across ** BULGE) ** POINT


def shift_at(y):
    """How far right of centre the leaf's midline sits at a row."""
    return LEAN * (1 - (y + 0.5) / ROWS)


def veined(cells, centre, half, y):
    """The row with its vein cut out, where the leaf is wide enough to have one."""
    if half < VEIN_MIN_HALF or y >= ROWS - 2:
        return cells
    return cells[:centre] + [" "] + cells[centre + 1 :]


def row_at(y):
    half, shift = half_at(y), shift_at(y)
    centre = SPAN + round(shift)
    cells = [
        FILLED if abs(x - shift) <= half else " " for x in range(-SPAN, SPAN + 2)
    ]
    # The tip is a single cell, which rounding the drifted midline could
    # otherwise land between and lose.
    cells[centre] = FILLED
    return "".join(veined(cells, centre, half, y)).rstrip()


def leaf():
    """The mark's rows, drawn from its outline rather than typed out."""
    return [row_at(y) for y in range(ROWS)]


def arguments():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    gradient.add_wave_arguments(parser, color="mongodb")
    return parser.parse_args()


def main():
    options = arguments()
    gradient.animate(
        gradient.frames_for(leaf(), options), gradient.SPEEDS[options.speed]
    )


if __name__ == "__main__":
    main()
