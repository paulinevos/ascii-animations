# ascii-animations

ASCII art and terminal animations for [presenterm](https://github.com/mfontanini/presenterm)
slides. Static art lives in `.txt` files; the `.py` scripts animate it with ANSI
true-color escape codes.

Every script resolves its art file relative to its own location, so the scripts
run correctly from any working directory.

## Layout

Animations and their art are grouped by category under `animation/`:

```
animation/decoration/   dividers
animation/messages/     thank-yous and banners
animation/nature/       mountains, sunsets, plants
animation/objects/      books, notes
animation/shapes/       hearts, diamonds
animation/space/        moon, stars, earth, rockets
animation/tech/         computers
```

Each category holds its animation scripts next to the `.txt` art they draw.

## Use as a submodule

```sh
git submodule add https://github.com/<you>/ascii-animations.git assets
git submodule update --init --recursive
```

Then reference the assets from a slide's executable code block:

````markdown
```bash +exec_replace +no_background
assets/animate sunset_gradient
```
````

## Running animations

`animate` runs any animation by name, without the `.py` extension. The category
is optional, and only needed to disambiguate:

```sh
./animate sunset_gradient
./animate nature/sunset_gradient
```

It works from any working directory. Run it with no arguments to list what is
available, grouped by category.

| Animation | Category | What it does |
|---|---|---|
| `computer_typing` | tech | `computer.txt` with lines typed into its screen, cursor blinking. `--handle NAME` writes `@NAME` on the case (alphanumeric, at most 12 characters; left out, that part of the case stays blank); any further arguments are the lines to type, truncated to the screen's width, e.g. `./animate computer_typing --handle pauline "jj st" "jj log"` |
| `diamond_gradient` | shapes | `diamond.txt` with a color gradient scrolling top to bottom |
| `divider_gradient` | decoration | A divider shimmering in lighter and darker hues of its own color |
| `heart_gradient` | shapes | A heart whose color and fill texture scroll on the same wave |
| `heartbeat` | shapes | A beating heart |
| `moon_gradient` | space | `moon.txt` with stars twinkling out of step with each other |
| `mountains_clouds` | nature | `mountains.txt` with clouds rolling past behind the peaks |
| `sunset_gradient` | nature | `sunset.txt` with flapping birds, moving waves, and twinkling water |
| `sunset_gradient_birds_only` | nature | `sunset.txt` with the birds animated and nothing else |
| `thankyou_gradient` | messages | figlet "thank you / Laracon" with a gradient sweep (needs `figlet` on PATH) |

Every animation loops until Ctrl-C.

Further arguments are passed through to the animation. `divider_gradient` takes
the name of a divider art file:

```sh
./animate divider_gradient divider_green.txt
```

Divider colors: `cyan`, `green`, `lavender`, `orange`, `red`, `white`, `yellow`,
plus the uncolored `divider.txt`.

## Static art

Display any `.txt` with `cat`, for example `cat animation/space/rocket.txt`.

| Category | Art |
|---|---|
| decoration | `divider.txt` and `divider_{cyan,green,lavender,orange,red,white,yellow}.txt` |
| messages | `sharing.txt` |
| nature | `flower.txt`, `mountains.txt`, `sun.txt`, `sunny.txt`, `sunset.txt`, `tree.txt`, `wave.txt` |
| objects | `book.txt`, `note.txt`, `spiral.txt` |
| shapes | `diamond.txt` |
| space | `earth.txt`, `moon.txt`, `moon2.txt`, `rocket.txt`, `star.txt`, `stars.txt` |
| tech | `computer.txt` |

## Drawing new art

`CLAUDE.md` documents the process and the Dracula palette used throughout.
