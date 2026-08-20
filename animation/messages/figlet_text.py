#!/usr/bin/env python3
"""Any text rendered with figlet, animated.

    python3 figlet_text.py "Hello there"
    python3 figlet_text.py "Hello" --font small --color rainbow --style wave
    python3 figlet_text.py "Hello" --color cyan --style wave-h --speed slow
    python3 figlet_text.py "Hello" --fill ramp
    python3 figlet_text.py "$(printf 'thank you\nLaracon')" --align center

Three animation styles: `wave` sweeps the color down the letters, `wave-h`
sweeps it left to right along them, and `pulse` cycles the whole block in
unison. `rainbow` travels through the Dracula palette; a single color instead
shimmers in lighter and darker hues of itself, the way the dividers do.

`--fill ramp` swaps the letterforms for characters off a density ramp, each
cell read at the phase its own color is read at, so the texture scrolls with
the gradient. That is the effect the heart in thankyou_gradient has, and it
works with any of the three styles.

A newline in the text has figlet stack a second block below the first, and
--align shifts each block within the width of the widest. The blank rows figlet
puts between the blocks are kept, so the words do not run together.

Requires figlet on PATH. Ctrl-C to stop.
"""

import argparse
import os
import shutil
import subprocess
import sys

# The shared gradient lives a directory up, and this script is run directly
# rather than imported, so its own directory is all that is on the path.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gradient  # noqa: E402  (needs the path above)


def figlet(text, font):
    """The text as figlet draws it, with the blank rows around it dropped.

    Only around it: a newline in the text has figlet stack another block below
    the first, and a blank line between them is a gap the caller asked for.
    Dropping every blank row would run the two words together.

    Trailing spaces are left on, because the alignments measure by them.
    """
    try:
        drawn = subprocess.run(
            ["figlet", "-f", font, "-w", "300", text],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    except subprocess.CalledProcessError as refused:
        sys.exit(refused.stderr.strip() or f"figlet could not draw with font {font!r}")
    return without_blank_ends(drawn.split("\n"))


def without_blank_ends(lines):
    first = next((y for y, line in enumerate(lines) if line.strip()), len(lines))
    last = next((y for y, line in reversed(list(enumerate(lines))) if line.strip()), 0)
    return lines[first : last + 1]


def left(line, width):
    return line


def center(line, width):
    return " " * ((width - len(line)) // 2) + line


def right(line, width):
    return " " * (width - len(line)) + line


ALIGNMENTS = {"left": left, "center": center, "right": right}


def aligned(block, how):
    """The block shifted as a whole, never row by row.

    figlet pads every row of a word to the same length, so measuring the rows
    before their trailing spaces come off gives each row of that word the same
    shift. Measuring after would shift the short rows — the tops of the
    letters, which figlet draws with nothing to their right — out of line with
    the stems below them.
    """
    shift = ALIGNMENTS[how]
    width = max(len(line) for line in block)
    return [shift(line, width).rstrip() for line in block]


def arguments():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("text", nargs="?", default="hello")
    parser.add_argument("--font", default="roman", help="any figlet font name")
    parser.add_argument("--align", default="left", choices=list(ALIGNMENTS))
    gradient.add_wave_arguments(parser)
    return parser.parse_args()


def main():
    if not shutil.which("figlet"):
        sys.exit("figlet not found on PATH (brew install figlet)")

    options = arguments()
    block = aligned(figlet(options.text, options.font), options.align)
    gradient.animate(
        gradient.frames_for(block, options), gradient.SPEEDS[options.speed]
    )


if __name__ == "__main__":
    main()
