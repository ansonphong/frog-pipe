# matte

Python utilities for artwork mattes: force white silhouettes, cut
black→transparent (white glyph), or knock out black while keeping color.

Requires: `pip install pillow` (numpy optional, speeds large images).

**Default: overwrite the source file.** Pass `--new` to write a sidecar instead.

## SVG white — `whiten_svg.py`

Makes shape fills and strokes `#ffffff`. Leaves `fill="none"` and `url(...)` paints alone.

```bash
python3 matte/whiten_svg.py icon.svg              # overwrites
python3 matte/whiten_svg.py ./icons/
python3 matte/whiten_svg.py ./icons/ --recursive
python3 matte/whiten_svg.py icon.svg --new        # → icon.white.svg
```

## PNG white — `whiten_png.py`

Sets RGB to white for every pixel with alpha > 0. Fully transparent pixels stay transparent.

```bash
python3 matte/whiten_png.py sprite.png            # overwrites
python3 matte/whiten_png.py ./sprites/
python3 matte/whiten_png.py ./sprites/ --recursive
python3 matte/whiten_png.py sprite.png --new      # → sprite.white.png
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
python3 matte/knockout.py file.png --new          # → file.knockout.png
python3 matte/knockout.py file.jpg --new          # JPEG needs --new (no alpha)
python3 matte/knockout.py file.png --cutoff 5     # crush dark greys (0–100)
python3 matte/knockout.py file.png --white 95     # levels white point
python3 matte/knockout.py file.png --color "#e13e13"
python3 matte/knockout.py file.png --color 0,200,255
python3 matte/knockout.py file.png --invert       # dark on light
```

| Need | Script |
|------|--------|
| Force fills/pixels white | `whiten_svg.py` / `whiten_png.py` |
| White silhouette cutout (luminance→alpha, always white) | `cutout.py` |
| Same idea + levels cutoff + any fill color | `knockout.py` |

## Naming

- `snake_case.py`, verb first
- Format suffix only when engines differ (`whiten_svg` / `whiten_png`)
- Sidecar outputs (`--new`): `*.white.*`, `*.cutout.png`, `*.knockout.png`

## Notes

- Folder mode is non-recursive unless `--recursive`.
- Files already named `*.white.svg` / `*.white.png` / `*.cutout.png` / `*.knockout.png` are skipped so re-runs of `--new` are safe.
- Default **overwrites** the source. Use `--new` when you want a sidecar copy.
