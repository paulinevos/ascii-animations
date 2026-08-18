#!/usr/bin/env python3
"""computer.txt with commands being typed into its screen.

The art is reproduced exactly as drawn; commands are typed into the blank rows
inside the monitor, character by character, with a blinking cursor. Each row
keeps its own color from the file, and the typed text gets its own.

    computer_typing [--handle HANDLE] [--name NAME] [line ...]

--handle  the handle written on the case, without its "@": alphanumeric, at
          most 12 characters. Left out, that part of the case stays blank.
--name    the name written on the case above the handle: letters, spaces and
          the punctuation names carry, at most 19 characters. Left out, that
          part of the case stays blank.
line      a line to type, in order; longer than the screen is truncated. With
          none given, the default commands are typed.

Ctrl-C to stop.
"""

import argparse
import os
import re
import sys
import time

ART = os.path.join(os.path.dirname(os.path.abspath(__file__)), "computer.txt")
RESET = "\033[0m"
ANSI = re.compile(r"\033\[[0-9;]*m")
GREEN = "\033[38;2;162;229;123m"  # phosphor green for the typed text

SPEED = 0.09
FRAMES_PER_CHAR = 2  # keystroke pace
HOLD = 14  # frames a finished command stays on screen
BLINK = 4  # frames per cursor on/off phase
CURSOR = "_"
PROMPT = "-"  # the character the art already uses as the prompt

# Typed in order, then the cycle repeats, when no lines are given.
COMMANDS = ("jj st", "jj log", "jj new", "jj desc")

# The handle drawn on the case, e.g. "@vanamerongen". Found rather than
# positioned, so the art stays the one source of truth for where it sits.
HANDLE_IN_ART = re.compile(r"@[A-Za-z0-9]+")
HANDLE_ALLOWED = re.compile(r"\A[A-Za-z0-9]+\Z")
HANDLE_LIMIT = 12

# The name drawn on the case, above the handle. There is no "@" to recognise it
# by, so it is matched literally — together with the spaces that follow it,
# which are slack the name can grow into without shoving the cable's ")" out of
# its column.
DRAWN_NAME = "pauline vos"
NAME_SLACK = 8
NAME_IN_ART = re.compile(re.escape(DRAWN_NAME) + " " * NAME_SLACK)
# Letters, spaces and the punctuation names actually carry. Anchored on a
# letter so a name cannot start with a space and drift out of its column.
NAME_ALLOWED = re.compile(r"\A[A-Za-z][A-Za-z .'-]*\Z")
NAME_LIMIT = len(DRAWN_NAME) + NAME_SLACK


def parse_arguments(argv):
    parser = argparse.ArgumentParser(
        prog="computer_typing",
        description="Type lines into computer.txt.",
    )
    parser.add_argument(
        "--handle",
        default=None,
        help="handle on the case, without its @",
    )
    parser.add_argument(
        "--name",
        default=None,
        help="name on the case, above the handle",
    )
    parser.add_argument("lines", nargs="*", help="lines to type, in order")
    return parser.parse_args(argv)


def validated_handle(handle):
    """The handle as it should appear, or "" for no handle at all."""
    if handle is None:
        return ""
    if HANDLE_ALLOWED.match(handle) and len(handle) <= HANDLE_LIMIT:
        return f"@{handle}"
    sys.exit(
        f"--handle must be alphanumeric and at most {HANDLE_LIMIT} "
        f"characters (the @ is added for you); got {handle!r}"
    )


def validated_name(name):
    """The name as it should appear, or "" for no name at all."""
    if name is None:
        return ""
    if NAME_ALLOWED.match(name) and len(name) <= NAME_LIMIT:
        return name
    sys.exit(
        f"--name must start with a letter, hold only letters, spaces, "
        f"'.', '-' and \"'\", and be at most {NAME_LIMIT} characters; "
        f"got {name!r}"
    )


def relabelled(rows, drawn_label, replacement):
    """The art rows with a label it was drawn with replaced by this one."""
    return [
        (color, substituted(text, drawn_label, replacement)) for color, text in rows
    ]


def substituted(text, drawn_label, replacement):
    """Text with a drawn label swapped, padded to the width it was drawn at.

    The padding is what keeps the case edge to the right of the label in its
    own column whatever length the replacement is, blank included.
    """
    drawn = drawn_label.search(text)
    if not drawn:
        return text
    padded = replacement.ljust(len(drawn.group(0)))
    return text[: drawn.start()] + padded + text[drawn.end() :]


def load():
    """Rows of (color, text) from the art, with escape codes stripped."""
    rows = []
    for line in open(ART).read().split("\n"):
        if not line:
            continue
        color = ANSI.match(line)
        rows.append((color.group(0) if color else "", ANSI.sub("", line)))
    return rows


def find_screen(rows):
    """(row index, start, stop) for each blank line inside the monitor.

    A screen row is one with four pipes — the case wall and the screen bezel on
    each side — whose innermost span is blank apart from the prompt. That last
    condition is what excludes the keyboard rows below, which also have four
    pipes but are filled with underscores.
    """
    screen = []
    for y, (_, text) in enumerate(rows):
        pipes = [x for x, ch in enumerate(text) if ch == "|"]
        if len(pipes) != 4:
            continue
        start, stop = pipes[1] + 1, pipes[2]
        if set(text[start:stop]) <= {" ", PROMPT}:
            screen.append((y, start, stop))
    return screen


def build_frames(rows, lines):
    screen = find_screen(rows)
    if not screen:
        sys.exit("no screen rows found in the art")

    # Type across the full interior of the first screen row. The art's own "-"
    # sits inside that span and is the resting cursor, so it's overwritten
    # while a command is on screen rather than typed around — six cells to the
    # right of it isn't enough for these commands.
    y, left, stop = screen[0]
    room = stop - left
    # One cell short of the interior, so the cursor after the last character
    # still has somewhere to blink without pushing into the bezel.
    typed_lines = [line[: room - 1] for line in lines]

    # (text so far, cursor visible) for every frame of the loop.
    beats = []
    for command in typed_lines:
        for i in range(1, len(command) + 1):
            beats += [(command[:i], True)] * FRAMES_PER_CHAR
        for f in range(HOLD):
            beats.append((command, (f // BLINK) % 2 == 0))
        beats.append(("", True))  # cleared, ready for the next command

    frames = []
    for typed, cursor in beats:
        out = ["\033[H"]
        for ry, (color, text) in enumerate(rows):
            if ry != y:
                out.append(f"{color}{text.rstrip()}{RESET}\n")
                continue
            shown = typed + (CURSOR if cursor else "")
            line = (
                f"{color}{text[:left]}{RESET}"
                f"{GREEN}{shown}{RESET}"
                f"{color}{text[left + len(shown):]}{RESET}"
            )
            out.append(f"{line}\n")
        frames.append("".join(out))
    return frames


def main():
    arguments = parse_arguments(sys.argv[1:])
    labelled = relabelled(load(), HANDLE_IN_ART, validated_handle(arguments.handle))
    labelled = relabelled(labelled, NAME_IN_ART, validated_name(arguments.name))
    frames = build_frames(labelled, arguments.lines or COMMANDS)

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
