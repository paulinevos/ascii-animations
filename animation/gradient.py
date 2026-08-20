#!/usr/bin/env python3
"""The scrolling gradient shared by the animations built on it.

Colorways, animation styles, character fills and the frame loop live here so
that figlet_text and heart_gradient stay one effect rather than three copies
drifting apart. thankyou_gradient keeps its own copy on purpose: its heart and
stacked blocks are bespoke, and the Laracon slide should not move.

Not an animation itself — the dispatcher only looks inside animation/<category>/,
so a module at this level is never offered as one.

A "block" throughout is a list of equal-or-ragged strings, one per row, where a
space is a hole and anything else is a filled cell.
"""

import math
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

# MongoDB's brand greens, for its leaf. The ramp returns the way it came --
# bright, mid, dark, mid -- because a green palette that wrapped straight from
# its darkest entry back to its brightest would show a seam every loop, where
# the Dracula one gets away with it by wrapping round the hues.
MONGODB = [
    (0, 237, 100),  # spring green
    (19, 170, 82),  # base green
    (0, 104, 74),  # forest green
    (19, 170, 82),  # base green again, coming back up
]

# PHP's indigos, for its logo. Returns the way it came, for the same reason
# MONGODB does.
PHP = [
    (136, 146, 191),  # elephant blue
    (119, 123, 180),  # logo indigo
    (79, 91, 147),  # dark indigo
    (119, 123, 180),  # logo indigo again, coming back up
]

# The colorways that travel through several colors, as against the single
# colors below them that shimmer in hues of themselves.
RAMPS = {"rainbow": PALETTE, "mongodb": MONGODB, "php": PHP}

FRAMES = 48  # gradient resolution; also the number of steps in one full loop
SPEEDS = {"slow": 0.12, "medium": 0.07, "fast": 0.035}
WAVE = 18  # columns per gradient cycle, for the horizontal sweep
LIGHTEN = 0.55  # how far a single color mixes toward white at the crest
DARKEN = 0.45  # how far it mixes toward black in the trough

# Density ramp for the "ramp" fill, lightest to densest. Starts at ":" rather
# than "." so a filled cell never thins out to nearly nothing in the light
# bands while its neighbours stay solid.
DENSITY = ":;+*=%#@"
NOISE = 2.2  # per-cell jitter in ramp steps; 0 = clean bands, higher = grainier
SEED = 7  # fixed so the grain holds still rather than flickering per frame


def sampled(palette):
    """A sampler reading a palette as a continuous loop over phase [0, 1)."""

    def at(phase):
        position = (phase % 1.0) * len(palette)
        index = int(position)
        fraction = position - index
        start, end = palette[index % len(palette)], palette[(index + 1) % len(palette)]
        return tuple(round(a + (b - a) * fraction) for a, b in zip(start, end))

    return at


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
    if name in RAMPS:
        return sampled(RAMPS[name])
    return shimmer(COLORS[name])


def painted(rgb, text):
    return f"\033[38;2;{rgb[0]};{rgb[1]};{rgb[2]}m{text}{RESET}"


def glyphs(line, y, phase_at, grain):
    """The line exactly as it was drawn."""
    return line


def textured(line, y, phase_at, grain):
    """The line's filled cells swapped for characters off the density ramp.

    Every cell reads the ramp at the phase its own color is read at, so the
    texture scrolls along with the gradient instead of sitting still under it.
    This is what the heart in thankyou_gradient does.
    """
    return "".join(
        speckled(char, phase_at(x), grain[y][x]) for x, char in enumerate(line)
    )


def speckled(char, phase, jitter):
    if char == " ":
        return char  # holes stay holes
    return DENSITY[int(depth(phase) + jitter) % len(DENSITY)]


def depth(phase):
    """How far into the density ramp a phase falls."""
    # A full color cycle spans two passes of the ramp, as the heart's does, so
    # the texture peaks twice per trip round the palette.
    return (phase % 1.0) * 2 % 1.0 * len(DENSITY)


FILLS = {"glyphs": glyphs, "ramp": textured}


def wave(color, block, step, fill, grain):
    """One color per row, travelling downward as the step advances."""
    rows = len(block)
    return [
        painted(
            color(y / rows - step / FRAMES),
            fill(line, y, uniform(y, rows, step), grain),
        )
        for y, line in enumerate(block)
    ]


def pulse(color, block, step, fill, grain):
    """The whole block in one color, cycling in unison."""
    return [
        painted(color(step / FRAMES), fill(line, y, steady(step), grain))
        for y, line in enumerate(block)
    ]


def wave_horizontal(color, block, step, fill, grain):
    """The color varying across each row, travelling rightward."""
    return [
        "".join(
            cell(color, x, char, step)
            for x, char in enumerate(fill(line, y, sweeping(step), grain))
        )
        for y, line in enumerate(block)
    ]


def uniform(y, rows, step):
    """The phase of a row whose color does not vary along it."""
    return lambda x: y / rows - step / FRAMES


def steady(step):
    """The phase of a block whose color is the same everywhere at once."""
    return lambda x: step / FRAMES


def sweeping(step):
    """The phase of a cell in a row whose color travels rightward."""
    return lambda x: x / WAVE - step / FRAMES


def cell(color, x, char, step):
    if char == " ":
        return char  # a space shows no foreground color, so spare it the escape
    return painted(color(x / WAVE - step / FRAMES), char)


STYLES = {"wave": wave, "wave-h": wave_horizontal, "pulse": pulse}


def add_wave_arguments(parser, fill="glyphs", color="rainbow"):
    """The flags every animation built on this module takes.

    The fill and color defaults are the caller's: each animation keeps the look
    it already had, or the one its subject calls for, rather than all of them
    changing to one.
    """
    parser.add_argument("--color", default=color, choices=[*RAMPS, *COLORS])
    parser.add_argument("--style", default="wave", choices=list(STYLES))
    parser.add_argument("--fill", default=fill, choices=list(FILLS))
    parser.add_argument("--speed", default="medium", choices=list(SPEEDS))


def grain_of(block):
    """Per-cell jitter for the ramp fill, baked once for the whole run.

    Drawn per cell rather than per frame: recomputed each frame the filled
    cells would boil instead of holding still while the wave passes through.
    """
    jitter = random.Random(SEED)
    return [[jitter.uniform(-NOISE, NOISE) for _ in line] for line in block]


def build_frames(block, style, color, fill):
    """One full loop, precomputed: cheap enough to redraw on a slide."""
    grain = grain_of(block)
    return [
        "".join(["\033[H", *(f"{line}\n" for line in drawn)])
        for drawn in (
            style(color, block, step, fill, grain) for step in range(FRAMES)
        )
    ]


def frames_for(block, options):
    """The frames an animation's parsed flags ask for."""
    return build_frames(
        block, STYLES[options.style], color_of(options.color), FILLS[options.fill]
    )


def animate(frames, speed):
    """Loop the frames until interrupted, leaving the cursor as it was found."""
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
