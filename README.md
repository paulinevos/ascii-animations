```
                _ _                   _                 _   _
  __ _ ___  ___(_|_)       __ _ _ __ (_)_ __ ___   __ _| |_(_) ___  _ __  ___
 / _` / __|/ __| | |_____ / _` | '_ \| | '_ ` _ \ / _` | __| |/ _ \| '_ \/ __|
| (_| \__ \ (__| | |_____| (_| | | | | | | | | | | (_| | |_| | (_) | | | \__ \
 \__,_|___/\___|_|_|      \__,_|_| |_|_|_| |_| |_|\__,_|\__|_|\___/|_| |_|___/
```

# ascii-animations

Looping ASCII art animations for your terminal. Static art lives in `.txt` files; 
the `.py` scripts animate it with ANSI true-color escape codes. 

Primarily made for use with presenterm, but perfectly usable standalone.

Art is partially sourced from www.asciiart.eu :)

See [DEMO.md](DEMO.md) for gifs of the animations running.

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

Run it with no arguments to list what is
available, grouped by category.

Set `LOOP_ASCII=false` to draw an animation once and stop, rather than looping:

```sh
LOOP_ASCII=false ./animate sunset_gradient
```

presenterm runs every snippet in a deck when it loads and does not close their
ptys, so looping animations exhaust the 511 macOS allows after a few reloads.

Further arguments are passed through to the animation. `divider_gradient` takes
the name of a divider art file:

```sh
./animate divider_gradient divider_green.txt
```

Divider colors: `cyan`, `green`, `lavender`, `orange`, `red`, `white`, `yellow`,
plus the uncolored `divider.txt`.

### Text animations

```sh
./animate figlet_text "Hello there"
./animate figlet_text "Hello" --font small --color rainbow --style wave --speed fast
./animate figlet_text "Hello" --color cyan --style wave-h --speed slow
./animate figlet_text "Hello" --fill ramp
```

| Flag | Values | Default |
|---|---|---|
| `text` | any string | `hello` |
| `--font` | any figlet font name (`figlet -I2` lists the font directory) | `roman` |
| `--color` | `rainbow`, `cyan`, `lavender`, `green`, `yellow`, `orange`, `red`, `white` | `rainbow` |
| `--style` | `wave` (sweeps down), `wave-h` (sweeps right), `pulse` (all in unison) | `wave` |
| `--fill` | `glyphs`, or `ramp` for letters filled from a density ramp that scrolls with the color | `glyphs` |
| `--align` | `left`, `center`, `right` — shifts each line of stacked text within the widest | `left` |
| `--speed` | `slow`, `medium`, `fast` | `medium` |

`rainbow` travels through the palette; a single color shimmers in lighter and
darker hues of itself.

A newline in the text stacks a second block below the first, which is what
`--align` is for:

```sh
./animate figlet_text "$(printf 'thank you\nLaracon')" --font small --align center
```

### Hearts

```sh
./animate heart_gradient
./animate heart_gradient --size small --color red --style pulse
./animate heart_gradient --fill glyphs --style wave-h
```

| Flag | Values | Default |
|---|---|---|
| `--size` | `large` (from the heart equation), `small` (the seven-row one from `thankyou_gradient`) | `large` |
| `--color` | as above | `rainbow` |
| `--style` | as above | `wave` |
| `--fill` | as above | `ramp` |
| `--speed` | `slow`, `medium`, `fast` | `medium` |

`--color`, `--style`, `--fill` and `--speed` are shared with `figlet_text`, and
come from `animation/gradient.py`.

### MongoDB leaf

```sh
./animate mongodb_leaf
./animate mongodb_leaf --style pulse --fill ramp
./animate mongodb_leaf --color rainbow
```

Takes the same flags, and defaults to `--color mongodb`: the brand greens,
which every animation can now use.

### PHP logo

```sh
./animate php_logo
./animate php_logo --style wave-h --color rainbow
./animate php_logo --font smslant
```

The slanted wordmark from figlet's `slant` inside the logo's ellipse, which is
drawn around whatever the font gives. Defaults to `--color php`.

