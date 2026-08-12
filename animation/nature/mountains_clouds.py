#!/usr/bin/env python3
"""mountains.txt with clouds rolling past.

The mountains are reproduced exactly as drawn. Clouds drift across the sky
behind them, at different heights and speeds, and are clipped wherever a
mountain glyph already occupies a cell — so they pass behind the peaks rather
than over them. Ctrl-C to stop.
"""

import os
import re
import sys
import time

ART = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mountains.txt")
RESET = "\033[0m"
ANSI = re.compile(r"\033\[[0-9;]*m")
CLOUD_COLOR = "\033[38;2;242;255;252m"  # white, so clouds read as sky not rock

SPEED = 0.12  # a slow drift; clouds shouldn't race

# Frames a cloud of speed 1 takes to advance a single column. Speeds are
# expressed in these sub-steps rather than whole columns per frame, which is
# what lets the clouds drift slowly and still travel at different rates —
# whole columns per frame is already too fast at the slowest possible value.
SUBSTEPS = 4

# (sprite, row, sub-steps per frame, head start in columns). Distinct speeds
# and offsets matter: at a shared speed the clouds hold formation and read as
# one blob drifting rather than as separate clouds at separate distances.
CLOUDS = (
    ("(~~~)", 1, 1, 0),
    ("(~~~~~)", 3, 2, 30),
    ("(~~)", 0, 3, 55),
    ("(~~~~)", 2, 1, 41),
)


def load():
    """Rows of (color, text) from the art, with escape codes stripped."""
    rows = []
    for line in open(ART).read().split("\n"):
        if not line:
            continue
        color = ANSI.match(line)
        rows.append((color.group(0) if color else "", ANSI.sub("", line)))
    return rows


def skyline(rows, width):
    """The topmost occupied row per column — the mountains' silhouette.

    The peaks are drawn as outlines, so their interiors are blank cells. Those
    have to count as rock, not sky: painting into them let clouds show through
    the middle of a mountain, which read as a broken sprite rather than as
    something passing behind. Anything at or below this line is hidden.
    """
    line = []
    for x in range(width):
        tops = [y for y, (_, text) in enumerate(rows) if x < len(text) and text[x] != " "]
        line.append(min(tops) if tops else len(rows))
    return line


def build_frames(rows):
    width = max(len(text) for _, text in rows)
    rock = skyline(rows, width)
    # A cloud travels from fully off the right edge to fully off the left, so
    # the loop length is the widest such journey. Every cloud's speed divides
    # it, which is what makes the wrap seamless.
    span = width + max(len(sprite) for sprite, *_ in CLOUDS)
    # Every cloud advances a whole number of columns over this many frames, so
    # all of them wrap seamlessly regardless of speed.
    frames = span * SUBSTEPS

    out_frames = []
    for f in range(frames):
        grid = [list(text.ljust(width)) for _, text in rows]
        # True where a cloud glyph was placed, so it can be colored separately
        painted = [[False] * width for _ in rows]

        for sprite, y, speed, offset in CLOUDS:
            if y >= len(rows):
                continue
            # right to left, wrapping; the span overshoots the art's width so a
            # cloud slides in from off-screen instead of appearing mid-sky
            x0 = width - ((f * speed // SUBSTEPS + offset) % span)
            visible = [
                0 <= x0 + i < width
                and y < rock[x0 + i]
                and grid[y][x0 + i] == " "
                for i in range(len(sprite))
            ]
            # A glyph with no visible neighbour is a one-character remnant of a
            # cloud that is otherwise behind a peak, and reads as debris rather
            # than as weather. Drop those.
            visible = [
                v
                and (
                    (i > 0 and visible[i - 1])
                    or (i + 1 < len(visible) and visible[i + 1])
                )
                for i, v in enumerate(visible)
            ]
            for i, glyph in enumerate(sprite):
                if not visible[i]:
                    continue
                grid[y][x0 + i] = glyph
                painted[y][x0 + i] = True

        buf = ["\033[H"]
        for y, (color, _) in enumerate(rows):
            line, run, run_cloud = [], [], None
            # emit the row as runs, switching color only when crossing between
            # cloud and mountain, to keep the escape count down
            for x, ch in enumerate(grid[y]):
                is_cloud = painted[y][x]
                if run and is_cloud != run_cloud:
                    line.append(
                        f"{CLOUD_COLOR if run_cloud else color}{''.join(run)}{RESET}"
                    )
                    run = []
                run.append(ch)
                run_cloud = is_cloud
            if run:
                line.append(
                    f"{CLOUD_COLOR if run_cloud else color}{''.join(run)}{RESET}"
                )
            buf.append(f"{''.join(line).rstrip()}\n")
        out_frames.append("".join(buf))
    return out_frames


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
