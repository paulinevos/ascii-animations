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

