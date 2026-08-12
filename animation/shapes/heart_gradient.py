#!/usr/bin/env python3
"""A static ASCII heart with a horizontal color gradient scrolling top to
bottom on a loop. The fill characters ride the same wave, so the texture
scrolls with the color. Ctrl-C to stop."""

import random
import sys
import time

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
RESET = "\033[0m"

# Density ramp, lightest to densest. The scrolling wave indexes into this.
CHARS = ".,:;+*=%#@"
NOISE = 2.2  # per-cell jitter in ramp steps; 0 = clean bands, higher = grainier
WIDTH = 60
Y_TOP, Y_BOTTOM = 22, -22  # taller range than wide => elongated heart
BANDS = 48  # gradient resolution; also the number of animation steps
SPEED = 0.06
SEED = 7  # fixed so the grain is stable across frames and runs


def heart_mask():
    """Boolean rows of the heart via the implicit heart equation.

    y is scaled more gently than x, which stretches the shape vertically.
    """
    rows = []
    for y in range(Y_TOP, Y_BOTTOM, -1):
        row = [
            ((x * 0.05) ** 2 + (y * 0.085) ** 2 - 1) ** 3
            - (x * 0.05) ** 2 * (y * 0.085) ** 3
            <= 0
            for x in range(-WIDTH // 2, WIDTH // 2)
        ]
        if any(row):
            rows.append(row)
    return rows


def ramp(t):
    """Sample the palette as a continuous loop at position t in [0, 1)."""
    pos = (t % 1.0) * len(PALETTE)
    i = int(pos)
    frac = pos - i
    a, b = PALETTE[i % len(PALETTE)], PALETTE[(i + 1) % len(PALETTE)]
    return tuple(round(ca + (cb - ca) * frac) for ca, cb in zip(a, b))


def main():
    mask = heart_mask()
    rng = random.Random(SEED)
    # Grain is baked per cell, not per frame — otherwise the whole heart
    # flickers instead of holding still while the wave passes through it.
    grain = [[rng.uniform(-NOISE, NOISE) for _ in row] for row in mask]

    frames = []
    for step in range(BANDS):
        out = ["\033[H"]
        for y, row in enumerate(mask):
            # subtracting step moves the wave downward over time
            phase = (y / len(mask)) - step / BANDS
            r, g, b = ramp(phase)
            # a full palette cycle spans two passes of the density ramp
            level = (phase % 1.0) * 2 % 1.0 * len(CHARS)
            line = []
            for x, inside in enumerate(row):
                if not inside:
                    line.append(" ")
                    continue
                i = int(level + grain[y][x]) % len(CHARS)
                line.append(CHARS[i])
            out.append(f"\033[38;2;{r};{g};{b}m{''.join(line).rstrip()}{RESET}\n")
        frames.append("".join(out))

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
