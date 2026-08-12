#!/usr/bin/env python3
"""computer.txt with commands being typed into its screen.

The art is reproduced exactly as drawn; commands are typed into the blank rows
inside the monitor, character by character, with a blinking cursor. Each row
keeps its own color from the file, and the typed text gets its own.

    computer_typing [--handle HANDLE] [line ...]

--handle  the handle written on the case, without its "@": alphanumeric, at
          most 12 characters. Left out, that part of the case stays blank.
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


def with_handle(rows, handle):
    """The art rows with the handle it was drawn with replaced by this one."""
    return [(color, substituted(text, handle)) for color, text in rows]


def substituted(text, handle):
    """Text with its handle swapped, padded to the drawn handle's width.

    The padding is what keeps the case edge to the right of the handle in its
    own column whatever length the new handle is, blank included.
    """
    drawn = HANDLE_IN_ART.search(text)
    if not drawn:
        return text
    padded = handle.ljust(len(drawn.group(0)))
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
    handle = validated_handle(arguments.handle)
    frames = build_frames(with_handle(load(), handle), arguments.lines or COMMANDS)

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
