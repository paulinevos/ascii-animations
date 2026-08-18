#!/usr/bin/env python3
"""Any text rendered with figlet, animated.

    python3 figlet_text.py "Hello there"
    python3 figlet_text.py "Hello" --font small --color rainbow --style wave
    python3 figlet_text.py "Hello" --color cyan --style wave-h --speed slow

Three animation styles: `wave` sweeps the color down the letters, `wave-h`
sweeps it left to right along them, and `pulse` cycles the whole block in
unison. `rainbow` travels through the Dracula palette; a single color instead
shimmers in lighter and darker hues of itself, the way the dividers do.

Requires figlet on PATH. Ctrl-C to stop.
"""

import argparse
import math
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
COLORS = {
    "cyan": (124, 213, 241),
    "lavender": (234, 178, 249),
    "green": (162, 229, 123),
    "yellow": (255, 237, 114),
    "orange": (255, 178, 112),
    "red": (255, 109, 126),
    "white": (242, 255, 252),
}
RESET = "\033[0m"

FRAMES = 48  # gradient resolution; also the number of steps in one full loop
SPEEDS = {"slow": 0.12, "medium": 0.07, "fast": 0.035}
WAVE = 18  # columns per gradient cycle, for the horizontal sweep
LIGHTEN = 0.55  # how far a single color mixes toward white at the crest
DARKEN = 0.45  # how far it mixes toward black in the trough


def figlet(text, font):
    """The text as figlet draws it, blank rows dropped."""
    try:
        drawn = subprocess.run(
            ["figlet", "-f", font, "-w", "300", text],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    except subprocess.CalledProcessError as refused:
        sys.exit(refused.stderr.strip() or f"figlet could not draw with font {font!r}")
    return [line for line in drawn.split("\n") if line.strip()]


def ramp(phase):
    """Sample the palette as a continuous loop at position phase in [0, 1)."""
    position = (phase % 1.0) * len(PALETTE)
    index = int(position)
    fraction = position - index
    start, end = PALETTE[index % len(PALETTE)], PALETTE[(index + 1) % len(PALETTE)]
    return tuple(round(a + (b - a) * fraction) for a, b in zip(start, end))


def shade(rgb, level):
    """The base color lightened or darkened according to level in [0, 1]."""
    if level >= 0.5:
        toward_white = (level - 0.5) * 2 * LIGHTEN
        return tuple(round(c + (255 - c) * toward_white) for c in rgb)
    toward_black = (0.5 - level) * 2 * DARKEN
    return tuple(round(c * (1 - toward_black)) for c in rgb)


def shimmer(rgb):
    """A single color as a wave: brightest at the crest, darkest in the trough."""
    return lambda phase: shade(rgb, (1 + math.sin(2 * math.pi * phase)) / 2)


def color_of(name):
    """The phase-to-rgb function a colorway names."""
    if name == "rainbow":
        return ramp
    return shimmer(COLORS[name])


def painted(rgb, text):
    return f"\033[38;2;{rgb[0]};{rgb[1]};{rgb[2]}m{text}{RESET}"


def wave(color, block, step):
    """One color per row, travelling downward as the step advances."""
    return [
        painted(color(y / len(block) - step / FRAMES), line)
        for y, line in enumerate(block)
    ]


def pulse(color, block, step):
    """The whole block in one color, cycling in unison."""
    return [painted(color(step / FRAMES), line) for line in block]


def wave_horizontal(color, block, step):
    """The color varying across each row, travelling rightward."""
    return [
        "".join(cell(color, x, char, step) for x, char in enumerate(line))
        for line in block
    ]


def cell(color, x, char, step):
    if char == " ":
        return char  # a space shows no foreground color, so spare it the escape
    return painted(color(x / WAVE - step / FRAMES), char)


STYLES = {"wave": wave, "wave-h": wave_horizontal, "pulse": pulse}


def trimmed(block):
    """The block with its trailing blanks dropped, alignment left alone.

    Centring each row on its own would shift the short ones — the tops of the
    letters, which figlet draws with nothing to their right — rightwards out of
    line with the stems below them.
    """
    return [line.rstrip() for line in block]


def build_frames(block, style, color):
    """One full loop, precomputed: cheap enough to redraw on a slide."""
    return [
        "".join(["\033[H", *(f"{line}\n" for line in style(color, block, step))])
        for step in range(FRAMES)
    ]


def animate(frames, speed):
    sys.stdout.write("\033[?25l\033[2J")  # hide cursor, clear once
    try:
        while True:
            for frame in frames:
                sys.stdout.write(frame)
                sys.stdout.flush()
                time.sleep(speed)
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write(f"\033[?25h{RESET}\n")


def arguments():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("text", nargs="?", default="hello")
    parser.add_argument("--font", default="roman", help="any figlet font name")
    parser.add_argument(
        "--color", default="rainbow", choices=["rainbow", *COLORS]
    )
    parser.add_argument("--style", default="wave", choices=list(STYLES))
    parser.add_argument("--speed", default="medium", choices=list(SPEEDS))
    return parser.parse_args()


def main():
    if not shutil.which("figlet"):
        sys.exit("figlet not found on PATH (brew install figlet)")

    options = arguments()
    block = trimmed(figlet(options.text, options.font))
    frames = build_frames(block, STYLES[options.style], color_of(options.color))
    animate(frames, SPEEDS[options.speed])


if __name__ == "__main__":
    main()
