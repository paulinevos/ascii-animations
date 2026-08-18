```
                _ _                   _                 _   _
  __ _ ___  ___(_|_)       __ _ _ __ (_)_ __ ___   __ _| |_(_) ___  _ __  ___
 / _` / __|/ __| | |_____ / _` | '_ \| | '_ ` _ \ / _` | __| |/ _ \| '_ \/ __|
| (_| \__ \ (__| | |_____| (_| | | | | | | | | | | (_| | |_| | (_) | | | \__ \
 \__,_|___/\___|_|_|      \__,_|_| |_|_|_| |_| |_|\__,_|\__|_|\___/|_| |_|___/
```

# ascii-animations

ASCII art and terminal animations for [presenterm](https://github.com/mfontanini/presenterm)
slides. Static art lives in `.txt` files; the `.py` scripts animate it with ANSI
true-color escape codes.

Every script resolves its art file relative to its own location, so the scripts
run correctly from any working directory.

## Requirements

Python 3, with no third-party packages. The figlet-based animations also need
figlet:

```sh
brew install figlet
```

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
Some categories, such as `objects/`, are art only.

## Use as a submodule

```sh
git submodule add https://github.com/paulinevos/ascii-animations.git assets
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
| `computer_typing` | tech | `computer.txt` with commands typed into its screen, cursor blinking |
| `diamond_gradient` | shapes | `diamond.txt` with a color gradient scrolling top to bottom |
| `divider_gradient` | decoration | A divider shimmering in lighter and darker hues of its own color |
| `figlet_text` | messages | Any text rendered with figlet, animated; font, color, style and speed all selectable |
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

`figlet_text` takes the text to draw, then flags:

```sh
./animate figlet_text "Hello there"
./animate figlet_text "Hello" --font small --color rainbow --style wave --speed fast
./animate figlet_text "Hello" --color cyan --style wave-h --speed slow
```

| Flag | Values | Default |
|---|---|---|
| `text` | any string | `hello` |
| `--font` | any figlet font name (`figlet -I2` lists the font directory) | `roman` |
| `--color` | `rainbow`, `cyan`, `lavender`, `green`, `yellow`, `orange`, `red`, `white` | `rainbow` |
| `--style` | `wave` (sweeps down), `wave-h` (sweeps right), `pulse` (all in unison) | `wave` |
| `--speed` | `slow`, `medium`, `fast` | `medium` |

`rainbow` travels through the palette; a single color shimmers in lighter and
darker hues of itself.

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
