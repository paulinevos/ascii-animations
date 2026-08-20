#!/usr/bin/env python3
"""Any text rendered with figlet, animated.

    python3 figlet_text.py "Hello there"
    python3 figlet_text.py "Hello" --font small --color rainbow --style wave
    python3 figlet_text.py "Hello" --color cyan --style wave-h --speed slow
    python3 figlet_text.py "Hello" --fill ramp

Three animation styles: `wave` sweeps the color down the letters, `wave-h`
sweeps it left to right along them, and `pulse` cycles the whole block in
unison. `rainbow` travels through the Dracula palette; a single color instead
shimmers in lighter and darker hues of itself, the way the dividers do.

`--fill ramp` swaps the letterforms for characters off a density ramp, each
cell read at the phase its own color is read at, so the texture scrolls with
the gradient. That is the effect the heart in thankyou_gradient has, and it
works with any of the three styles.

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


def trimmed(block):
    """The block with its trailing blanks dropped, alignment left alone.

    Centring each row on its own would shift the short ones — the tops of the
    letters, which figlet draws with nothing to their right — rightwards out of
    line with the stems below them.
    """
    return [line.rstrip() for line in block]


def arguments():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("text", nargs="?", default="hello")
    parser.add_argument("--font", default="roman", help="any figlet font name")
    gradient.add_wave_arguments(parser)
    return parser.parse_args()


def main():
    if not shutil.which("figlet"):
        sys.exit("figlet not found on PATH (brew install figlet)")

    options = arguments()
    block = trimmed(figlet(options.text, options.font))
    gradient.animate(
        gradient.frames_for(block, options), gradient.SPEEDS[options.speed]
    )


if __name__ == "__main__":
    main()
