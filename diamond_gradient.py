#!/usr/bin/env python3
"""diamond.txt with a color gradient scrolling top to bottom on a loop.

The art itself is untouched — every glyph stays exactly where it is and as it
is. Only the color changes, sweeping down through the diamonds and wrapping
seamlessly. Ctrl-C to stop.
"""

import os
import re
import sys
import time

ART = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diamond.txt")
RESET = "\033[0m"
ANSI = re.compile(r"\033\[[0-9;]*m")

# Dracula palette, ordered as a gradient ramp. The list wraps around to the
# first entry so the scroll loops without a visible seam.
PALETTE = [
    (255, 109, 126),  # red
    (255, 178, 112),  # orange
    (255, 237, 114),  # yellow
    (162, 229, 123),  # green
    (124, 213, 241),  # cyan
    (234, 178, 249),  # lavender
]

BANDS = 48  # gradient resolution; also the number of animation steps
SPEED = 0.06


def load():
    """Rows of the art with its own color escapes stripped.

    The gradient supplies the color here, so the file's per-row colors are
    dropped rather than preserved.
    """
    return [ANSI.sub("", line) for line in open(ART).read().split("\n") if line]


def ramp(t):
    """Sample the palette as a continuous loop at position t in [0, 1)."""
    pos = (t % 1.0) * len(PALETTE)
    i = int(pos)
    frac = pos - i
    a, b = PALETTE[i % len(PALETTE)], PALETTE[(i + 1) % len(PALETTE)]
    return tuple(round(ca + (cb - ca) * frac) for ca, cb in zip(a, b))


def build_frames(rows):
    frames = []
    for step in range(BANDS):
        out = ["\033[H"]
        for y, line in enumerate(rows):
            # subtracting step moves the gradient downward over time
            r, g, b = ramp((y / len(rows)) - step / BANDS)
            out.append(f"\033[38;2;{r};{g};{b}m{line.rstrip()}{RESET}\n")
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
