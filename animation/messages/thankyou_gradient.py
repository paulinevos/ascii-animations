#!/usr/bin/env python3
"""thank you / <name>, rendered with figlet's own letterforms.

    thankyou_gradient [name]

The name defaults to "Laracon" and must be 1-16 alphanumeric characters. Its
block gets a horizontal color gradient scrolling top to bottom on a loop; the
"thank you" above it stays plain white. The heart suffixed to the name is
filled from a density ramp riding that same wave, so its texture scrolls with
the color. A long name in the roman font can be wider than the terminal, in
which case the script refuses to run rather than wrapping every row into
nonsense. Requires figlet on PATH. Ctrl-C to stop.
"""

import random
import shutil
import subprocess
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
WHITE = "\033[38;2;242;255;252m"
RESET = "\033[0m"

BANDS = 48  # gradient resolution; also the number of animation steps
SPEED = 0.06
LINE_GAP = 1  # blank rows between the two blocks
HEART_GAP = 2  # blank columns between the last letter and the heart

# Density ramp for the heart, lightest to densest. Starts at ":" rather than
# "." so the heart doesn't thin out to near-nothing in the light bands while
# the letters beside it stay solid.
CHARS = ":;+*=%#@"
NOISE = 2.2  # per-cell jitter in ramp steps; 0 = clean bands, higher = grainier
SEED = 7  # fixed so the grain is stable across frames and runs

DEFAULT_NAME = "Laracon"
MAXIMUM_NAME_LENGTH = 16

# Hand-drawn rather than derived from the heart equation: at seven rows the
# equation loses the top cleft, and without that a small heart reads as a
# blob. Seven rows to match the height of the roman figlet font.
HEART_MASK = [
    "  ####   ####  ",
    " ############# ",
    "###############",
    " ############# ",
    "  ###########  ",
    "    #######    ",
    "      ###      ",
]


# Grain is baked per cell, not per frame — otherwise the heart flickers
# instead of holding still while the wave passes through it.
_rng = random.Random(SEED)
HEART_GRAIN = [[_rng.uniform(-NOISE, NOISE) for _ in row] for row in HEART_MASK]


def heart(phase):
    """The mask filled from the density ramp at a given wave phase.

    Each row samples the ramp at the same phase used for its color, so the
    texture and the gradient travel down the heart together.
    """
    rows = []
    for y, row in enumerate(HEART_MASK):
        # a full palette cycle spans two passes of the density ramp
        level = (phase(y) % 1.0) * 2 % 1.0 * len(CHARS)
        rows.append(
            "".join(
                CHARS[int(level + HEART_GRAIN[y][x]) % len(CHARS)] if cell == "#" else " "
                for x, cell in enumerate(row)
            )
        )
    return rows


def suffix(block, mark, gap):
    """Append mark to the right of block, top-aligned."""
    width = max(len(line) for line in block) + gap
    return [
        line.ljust(width) + (mark[y] if y < len(mark) else "")
        for y, line in enumerate(block)
    ]


def figlet(text, font):
    out = subprocess.run(
        ["figlet", "-f", font, "-w", "300", text],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return [line for line in out.split("\n") if line.strip()]


def ramp(t):
    """Sample the palette as a continuous loop at position t in [0, 1)."""
    pos = (t % 1.0) * len(PALETTE)
    i = int(pos)
    frac = pos - i
    a, b = PALETTE[i % len(PALETTE)], PALETTE[(i + 1) % len(PALETTE)]
    return tuple(round(ca + (cb - ca) * frac) for ca, cb in zip(a, b))


def build_frames(head, letters, width):
    """Precompute one full loop: head is static white, letters + heart scroll."""
    def center(line):
        return " " * ((width - len(line)) // 2) + line.rstrip()

    static = [f"{WHITE}{center(line)}{RESET}\n" for line in head]
    static += ["\n"] * LINE_GAP

    frames = []
    for step in range(BANDS):
        # subtracting step moves the wave downward over time
        phase = lambda y: (y / len(letters)) - step / BANDS
        body = suffix(letters, heart(phase), HEART_GAP)
        out = ["\033[H", *static]
        for y, line in enumerate(body):
            r, g, b = ramp(phase(y))
            out.append(f"\033[38;2;{r};{g};{b}m{center(line)}{RESET}\n")
        frames.append("".join(out))
    return frames


def name_from(arguments):
    """The name to thank: the sole optional positional argument."""
    if not arguments:
        return DEFAULT_NAME
    if len(arguments) > 1:
        sys.exit(f"Expected at most one name, got {len(arguments)}: {' '.join(arguments)}")
    name = arguments[0]
    if not name.isalnum() or len(name) > MAXIMUM_NAME_LENGTH:
        sys.exit(
            f"The name must be 1-{MAXIMUM_NAME_LENGTH} alphanumeric characters "
            f"(letters and digits, no spaces or punctuation), got {name!r}."
        )
    return name


def main():
    if not shutil.which("figlet"):
        sys.exit("figlet not found on PATH (brew install figlet)")

    name = name_from(sys.argv[1:])
    head = figlet("thank you", "small")
    letters = figlet(name, "roman")
    # width from the widest possible body, so the centering never shifts as
    # the heart's texture changes between frames
    width = max(len(line) for line in head + suffix(letters, HEART_MASK, HEART_GAP))

    # Every row is padded to this width, so a terminal narrower than it wraps
    # each row in two and the block stops reading as letters at all. Refusing
    # is more useful than rendering that. Only when attached to a terminal:
    # otherwise get_terminal_size reports its 80-column fallback, which would
    # reject even the default name when the output is piped or captured.
    columns = shutil.get_terminal_size().columns
    if sys.stdout.isatty() and width > columns:
        sys.exit(
            f"{name!r} needs {width} columns in the roman font, but the terminal "
            f"is {columns} wide. Use a shorter name or a wider terminal."
        )

    frames = build_frames(head, letters, width)

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
