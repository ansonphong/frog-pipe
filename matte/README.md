# matte

Python utilities for artwork mattes: recolor silhouettes, cut
black→transparent (white glyph), or knock out black while keeping color.

Requires: `pip install pillow` (numpy optional, speeds large images).

**Default: overwrite the source file.** Pass `--new` to write a sidecar instead.

`--color` (where present): name, `#rrggbb`, or `r,g,b`. **Default is white.**

## SVG recolor — `recolor_svg.py`

Sets shape fills and strokes to a solid color (default `#ffffff`).
Leaves `fill="none"` and `url(...)` paints alone.

```bash
python3 matte/recolor_svg.py icon.svg              # white, overwrites
python3 matte/recolor_svg.py ./icons/
python3 matte/recolor_svg.py ./icons/ --recursive
python3 matte/recolor_svg.py icon.svg --new        # → icon.recolor.svg
python3 matte/recolor_svg.py icon.svg --color "#e13e13"
python3 matte/recolor_svg.py icon.svg --color 0,200,255
```

## PNG recolor — `recolor_png.py`

Sets RGB for every pixel with alpha > 0 (default pure white).
Fully transparent pixels stay transparent.

```bash
python3 matte/recolor_png.py sprite.png            # white, overwrites
python3 matte/recolor_png.py ./sprites/
python3 matte/recolor_png.py ./sprites/ --recursive
python3 matte/recolor_png.py sprite.png --new      # → sprite.recolor.png
python3 matte/recolor_png.py sprite.png --color red
python3 matte/recolor_png.py sprite.png --color "#e13e13"
```

## Cutout — `cutout.py` (black → transparent, white glyph)

White-on-black PNG/JPG → RGBA PNG: **pure white RGB**, **black transparent**,
anti-alias kept via luminance→alpha (no dark halo).

```bash
python3 matte/cutout.py file.png                  # overwrites
python3 matte/cutout.py folder/
python3 matte/cutout.py file.png --new            # → file.cutout.png
python3 matte/cutout.py file.jpg --new            # JPEG needs --new (no alpha)
python3 matte/cutout.py file.png --black-point 12 --gamma 1.3
python3 matte/cutout.py file.png --invert         # dark ink on white paper
```

Algorithm: `alpha = curve(luminance)`; `RGB = white` where visible.
JPEG cannot store alpha — use `--new` for `name.cutout.png`.

## Knockout — `knockout.py` (greyscale → alpha, solid fill)

Art-on-black PNG/JPG → RGBA PNG. Simple 3-step process:

1. RGB → greyscale luminance  
2. **Levels** on that grey (`--cutoff` / `--white`, 0–100%) → becomes **alpha**  
3. **RGB** filled with `--color` (default pure white)

On a pure black background the greys match the original.

```bash
python3 matte/knockout.py file.png                # overwrites, white fill
python3 matte/knockout.py folder/
python3 matte/knockout.py file.png --new          # → file.png.knockout.png
python3 matte/knockout.py file.jpg --new          # → file.jpg.knockout.png
python3 matte/knockout.py file.png --cutoff 5     # crush dark greys (0–100)
python3 matte/knockout.py file.png --white 95     # levels white point
python3 matte/knockout.py file.png --color "#e13e13"
python3 matte/knockout.py file.png --color 0,200,255
python3 matte/knockout.py file.png --invert       # dark on light
python3 matte/knockout.py file.png --force        # reprocess tagged outputs
```

Batch safety: preflight destinations before any write; unique sidecars per source
extension; PNG metadata tags outputs; refuse reprocess unless `--force`.

## Despeckle — `despeckle.py` (dust / freckles)

Cleans small islands on **black-bg** or **transparent** art. Works on a
**coverage** channel only (alpha or luminance) — not RGB blur.

1. Mode `auto`: any `A < 255` → use alpha; else luminance  
2. Drop 8-connected components smaller than `--min-area` (default 4)  
3. Levels once (`--cutoff` / `--white` / `--gamma`)  
4. Pack: alpha keeps RGB (or `--color`); black → grey-on-black (`--to-alpha` → matte)

```bash
python3 matte/despeckle.py file.png                 # overwrite
python3 matte/despeckle.py folder/
python3 matte/despeckle.py file.png --new           # → file.despeckle.png
python3 matte/despeckle.py file.png --min-area 8 --cutoff 2
python3 matte/despeckle.py file.png --mode black --to-alpha
python3 matte/despeckle.py file.png --color white   # force fill when alpha out
```

Codex Sol review: min-area primary; morph open / blur **not** default (too destructive).

| Need | Script |
|------|--------|
| Force fills/pixels to a color (default white) | `recolor_svg.py` / `recolor_png.py` |
| White silhouette cutout (luminance→alpha, always white) | `cutout.py` |
| Same idea + levels cutoff + any fill color | `knockout.py` |
| Remove dust / freckles (black or transparent) | `despeckle.py` |

## Naming

- `snake_case.py`, verb first
- Format suffix only when engines differ (`recolor_svg` / `recolor_png`)
- Shared color parse: `colorutil.py`
- Sidecar outputs (`--new`): `*.recolor.*`, `*.cutout.png`, `*.knockout.png`, `*.despeckle.png`

## Notes

- Folder mode is non-recursive unless `--recursive`.
- Files already named `*.recolor.svg` / `*.recolor.png` / `*.cutout.png` / `*.knockout.png` / `*.despeckle.png` are skipped so re-runs of `--new` are safe (legacy `*.white.*` also skipped by recolor tools).
- Default **overwrites** the source. Use `--new` when you want a sidecar copy.
- `despeckle` is not fully idempotent if you raise cutoff/min-area between runs — prefer one clean pass from backup.
- Old names `whiten_svg` / `whiten_png` still work via `scripts/fp-run.sh` aliases.
