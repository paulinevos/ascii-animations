# ascii-animations

ASCII art and terminal animations for [presenterm](https://github.com/mfontanini/presenterm)
slides. Static art lives in `.txt` files; the `.py` scripts animate it with ANSI
true-color escape codes.

Every script resolves its art file relative to its own location, so the scripts
run correctly from any working directory.

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

`animate` runs any animation by name, without the `.py` extension:

```sh
./animate sunset_gradient
```

It works from any working directory. Run it with no arguments to list what is
available.

| Animation | What it does |
|---|---|
| `computer_typing` | `computer.txt` with commands typed into its screen, cursor blinking |
| `diamond_gradient` | `diamond.txt` with a color gradient scrolling top to bottom |
| `divider_gradient` | A divider shimmering in lighter and darker hues of its own color |
| `heart_gradient` | A heart whose color and fill texture scroll on the same wave |
| `heartbeat` | A beating heart |
| `moon_gradient` | `moon.txt` with stars twinkling out of step with each other |
| `mountains_clouds` | `mountains.txt` with clouds rolling past behind the peaks |
| `sunset_gradient` | `sunset.txt` with flapping birds, moving waves, and twinkling water |
| `sunset_gradient_birds_only` | `sunset.txt` with the birds animated and nothing else |
| `thankyou_gradient` | figlet "thank you / Laracon" with a gradient sweep (needs `figlet` on PATH) |

Every animation loops until Ctrl-C.

Further arguments are passed through to the animation. `divider_gradient` takes
the name of a divider art file:

```sh
./animate divider_gradient divider_green.txt
```

Divider colors: `cyan`, `green`, `lavender`, `orange`, `red`, `white`, `yellow`,
plus the uncolored `divider.txt`.

## Static art

`book.txt`, `computer.txt`, `diamond.txt`, `earth.txt`, `flower.txt`, `moon.txt`,
`moon2.txt`, `mountains.txt`, `note.txt`, `rocket.txt`, `sharing.txt`,
`spiral.txt`, `star.txt`, `stars.txt`, `sun.txt`, `sunny.txt`, `sunset.txt`,
`tree.txt`, `wave.txt` — display with `cat`.

## Drawing new art

`CLAUDE.md` documents the process and the Dracula palette used throughout.
