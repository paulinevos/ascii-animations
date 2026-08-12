#!/usr/bin/env python3
"""A beating ASCII heart. Ctrl-C to stop."""

import math
import sys
import time

COLORS = [
    "\033[38;2;255;109;126m",  # red
    "\033[38;2;255;178;112m",  # orange
    "\033[38;2;255;237;114m",  # yellow
    "\033[38;2;162;229;123m",  # green
    "\033[38;2;124;213;241m",  # cyan
    "\033[38;2;234;178;249m",  # lavender
]
RESET = "\033[0m"

WIDTH, HEIGHT = 60, 30  # grid cells; y is halved on print via step of 2


def heart_frame(scale):
    """Render the heart at a given scale using the implicit heart equation."""
    rows = []
    for y in range(HEIGHT // 2, -(HEIGHT // 2), -1):
        row = []
        for x in range(-WIDTH // 2, WIDTH // 2):
            # y is doubled to correct the 2:1 character aspect ratio
            nx, ny = x * 0.05 / scale, y * 0.2 / scale
            inside = (nx**2 + ny**2 - 1) ** 3 - nx**2 * ny**3 <= 0
            row.append("#" if inside else " ")
        line = "".join(row).rstrip()
        if line:
            rows.append(line)
    return rows


def draw(rows, beat):
    out = ["\033[H"]  # cursor home — no full clear, avoids flicker
    pad = (HEIGHT // 2 - len(rows)) // 2
    for _ in range(max(pad, 0)):
        out.append("\033[K\n")
    for i, row in enumerate(rows):
        color = COLORS[(i + beat) % len(COLORS)]
        out.append(f"{color}{row}{RESET}\033[K\n")
    out.append("\033[J")  # erase anything left from a bigger previous frame
    sys.stdout.write("".join(out))
    sys.stdout.flush()


def main():
    # Two thumps per cycle, like a real heartbeat: lub-DUB, rest.
    keyframes = [1.0, 1.12, 1.0, 1.18, 1.05, 1.0, 1.0, 1.0]
    frames = []
    for i in range(len(keyframes) * 4):
        a, b = keyframes[i // 4], keyframes[(i // 4 + 1) % len(keyframes)]
        t = (i % 4) / 4
        # ease between keyframes so the pulse doesn't look mechanical
        eased = a + (b - a) * (1 - math.cos(t * math.pi)) / 2
        frames.append(heart_frame(eased))

    sys.stdout.write("\033[?25l\033[2J")  # hide cursor, clear once
    try:
        beat = 0
        while True:
            for frame in frames:
                draw(frame, beat)
                time.sleep(0.05)
            beat += 1
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write(f"\033[?25h{RESET}\n")


if __name__ == "__main__":
    main()
