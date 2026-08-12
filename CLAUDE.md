# Generating ASCII Visuals

Follow these steps whenever asked to draw something in ASCII art.

---

## Step 1: Research the Shape

Before drawing anything, look up what the shape actually looks like.

- Search for reference images or descriptions: what are its defining visual features?
- Identify the silhouette: what does the outline look like from a distance?
- Note any symmetry (left-right, top-bottom, rotational).
- Identify the most recognizable features — the parts that make it look like *that thing*
  and not something else. These are non-negotiable; get them right first.

Example questions to answer before drawing:
- Does it have curves or straight edges?
- Where is it widest? Narrowest?
- Does it have a distinctive top, bottom, or profile?
- Is there internal detail worth capturing at this scale?

---

## Step 2: Plan the Grid

ASCII art is a grid of equal-sized cells in a monospace font.

- Pick a width (e.g. 20–40 chars) that fits the complexity of the shape.
- Estimate the height: because characters are roughly **2× taller than wide**,
  a shape that is 20 units wide and 20 units tall should only be ~10 rows high.
  Always divide the visual height by ~2 to account for this aspect ratio.
- Sketch the bounding box: where does the shape start and end in the grid?
- Mark the center, axis of symmetry, and any key proportional landmarks.

---

## Step 3: Build the Shape Row by Row

Work from top to bottom. For each row, ask:
- How wide is the shape at this height?
- Is this an edge row (outline only) or a filled row?
- Count characters carefully — verify left and right sides are symmetric if applicable.

Use fill characters appropriate to the intent:
- `*` or `#` for solid/bold fills
- `@` `%` `+` `-` `.` for lighter fills or gradients (darkest → lightest)
- `/` `\` `|` `_` for edges and diagonals

---

## Step 4: Verify Before Committing

- Count characters per row to confirm symmetry holds.
- Read it at a distance — squint or zoom out. Does it look like the thing?
- Check that the defining features from Step 1 are visible.
- If a row looks wrong, fix the count rather than eyeballing it.

---

## Step 5: Common Pitfalls to Avoid

- **Forgetting aspect ratio**: not compressing height leads to tall, squished shapes.
- **Missing the defining feature**: e.g. a heart without the double-bump top
  looks like a raindrop. Identify and protect the key features.
- **Uneven sides**: always count, don't eyeball symmetry.
- **Too much detail**: at small scales, simplify. A 10-row shape can't have fine detail.
- **Starting without a reference**: drawing from vague memory produces vague results.

---

## Reference: Mathematical Shapes

For precise geometric shapes, use implicit equations evaluated per grid cell.
Always scale x and y to correct for the 2:1 aspect ratio.

**Circle** (radius r, center cx/cy):
```
(x - cx)^2 + ((y - cy) * 2)^2 <= r^2
```

**Heart**:
```
((x * 0.05)^2 + (y * 0.1)^2 - 1)^3 - (x * 0.05)^2 * (y * 0.1)^3 <= 0
```
Iterate x from -30 to 29, y from 15 down to -14.

**Diamond**: `|x - cx| + |y - cy| * 2 <= r`

---

## Reference: Colors (Dracula Theme)

Use ANSI true color escape codes to colorize output. The format is:
```
\033[38;2;R;G;Bm   ← set foreground color to RGB
\033[0m             ← reset (always add at end of each line)
```

**Always assign a different color to each row of the art.**
Cycle through the palette below from top to bottom of the shape.

### Dracula Palette (hex → RGB)

| Name     | Hex       | RGB                  | Escape code                   |
|----------|-----------|----------------------|-------------------------------|
| cyan     | `#7cd5f1` | rgb(124, 213, 241)   | `\033[38;2;124;213;241m`      |
| lavender | `#eab2f9` | rgb(234, 178, 249)   | `\033[38;2;234;178;249m`      |
| green    | `#a2e57b` | rgb(162, 229, 123)   | `\033[38;2;162;229;123m`      |
| yellow   | `#ffed72` | rgb(255, 237, 114)   | `\033[38;2;255;237;114m`      |
| orange   | `#ffb270` | rgb(255, 178, 112)   | `\033[38;2;255;178;112m`      |
| red      | `#ff6d7e` | rgb(255, 109, 126)   | `\033[38;2;255;109;126m`      |
| white    | `#f2fffc` | rgb(242, 255, 252)   | `\033[38;2;242;255;252m`      |

### Example (Python)

```python
COLORS = [
    "\033[38;2;124;213;241m",  # cyan
    "\033[38;2;234;178;249m",  # lavender
    "\033[38;2;162;229;123m",  # green
    "\033[38;2;255;237;114m",  # yellow
    "\033[38;2;255;178;112m",  # orange
    "\033[38;2;255;109;126m",  # red
]
RESET = "\033[0m"

rows = [
    " ****   **** ",
    "***** * *****",
    # ...
]

for i, row in enumerate(rows):
    color = COLORS[i % len(COLORS)]
    print(f"{color}{row}{RESET}")
```

---

## Reference: Useful Characters

| Use case   | Characters                      |
|------------|---------------------------------|
| Fill       | `█ ▓ ▒ ░` or `@ # * + - .`     |
| Horizontal | `─ ━ = ≡ -`                     |
| Vertical   | `│ ┃ \| ¦`                      |
| Diagonal   | `/ \ ╱ ╲`                       |
| Box        | `┌ ┐ └ ┘ ├ ┤ ┬ ┴ ┼`            |
| Curves     | `( ) { } ~ ° `                  |
