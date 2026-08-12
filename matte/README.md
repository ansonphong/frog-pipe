# matte

Python utilities for artwork mattes: recolor silhouettes, cut
black→transparent (white glyph), knock out black with a fill color, or despeckle dust.

Requires: `pip install pillow` (numpy optional, speeds large images).

**Default: overwrite the source file.** Pass `--new` to write a sidecar instead.

**`--color`** (recolor / knockout / despeckle): name, `#rgb` / `#rrggbb`, or `r,g,b`.
**Default is white.** Shared parser: `colorutil.py`.

Discover live flags anytime: `python3 matte/<tool>.py -h` or `bash scripts/fp-run.sh <tool> -h`.

---

## Quick map

| Need | Script |
|------|--------|
| Force fills/pixels to a color (default white) | `recolor_svg.py` / `recolor_png.py` |
| White silhouette cutout (luma→alpha, always white RGB) | `cutout.py` |
| Grey art on black → alpha + any fill color | `knockout.py` |
| Remove dust / freckles (black or transparent) | `despeckle.py` |

---

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

| Flag | Default | Meaning |
|------|---------|---------|
| `path` | required | `.svg` file or directory |
| `--new` | off | Sidecar `file.recolor.svg` |
| `--recursive` | off | Recurse subfolders |
| `--color` | `white` | Fill/stroke color |

---

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

| Flag | Default | Meaning |
|------|---------|---------|
| `path` | required | `.png` file or directory |
| `--new` | off | Sidecar `file.recolor.png` |
| `--recursive` | off | Recurse subfolders |
| `--color` | `white` | RGB for all `alpha > 0` pixels |

---

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

| Flag | Default | Meaning |
|------|---------|---------|
| `path` | required | PNG/JPG file or directory |
| `--new` | off | Sidecar `file.cutout.png` |
| `--recursive` | off | Recurse subfolders |
| `--black-point` | `8` | Luma ≤ N → alpha 0 (**0–255**) |
| `--white-point` | `247` | Luma ≥ N → alpha 255 (**0–255**) |
| `--gamma` | `1.0` | Midtone gamma; `>1` = crisper |
| `--invert` | off | Dark glyph on light background |

Algorithm: `alpha = curve(luminance)`; `RGB = white` where visible.
JPEG cannot store alpha — use `--new`.

---

## Knockout — `knockout.py` (greyscale → alpha, solid fill)

Art-on-black PNG/JPG → RGBA PNG:

1. RGB → greyscale luminance  
2. **Levels** on that grey (`--cutoff` / `--white`, **0–100%**) → **alpha**  
3. **RGB** filled with `--color` (default pure white)

```bash
python3 matte/knockout.py file.png                # overwrites, white fill
python3 matte/knockout.py folder/
python3 matte/knockout.py file.png --new          # → file.png.knockout.png
python3 matte/knockout.py file.jpg --new          # → file.jpg.knockout.png
python3 matte/knockout.py file.png --cutoff 5     # crush dark greys (0–100)
python3 matte/knockout.py file.png --white 95     # levels white point
python3 matte/knockout.py file.png --gamma 1.2
python3 matte/knockout.py file.png --color "#e13e13"
python3 matte/knockout.py file.png --color 0,200,255
python3 matte/knockout.py file.png --invert       # dark on light
python3 matte/knockout.py file.png --force        # reprocess tagged outputs
```

| Flag | Default | Meaning |
|------|---------|---------|
| `path` | required | PNG/JPG file or directory |
| `--new` | off | Sidecar `stem.ext.knockout.png` |
| `--recursive` | off | Recurse subfolders |
| `--force` | off | Allow reprocessing knockout products |
| `--cutoff` | `0` | Levels black point **0–100** → alpha 0 |
| `--white` | `100` | Levels white point **0–100** → alpha 255 |
| `--gamma` | `1.0` | Midtone gamma on alpha |
| `--color` | `white` | Solid RGB fill |
| `--invert` | off | Invert greyscale before levels |

Batch safety: preflight destinations; unique sidecars per source extension;
PNG metadata `hextile-pipe-tool=knockout`; refuse reprocess unless `--force`.

---

## Despeckle — `despeckle.py` (dust / freckles)

Cleans small islands on **black-bg** or **transparent** art. Coverage channel
only (alpha or luminance) — not RGB blur.

1. Mode `auto`: any `A < 255` → alpha; else luminance  
2. Drop 8-connected components smaller than `--min-area` (default 4)  
3. Levels once (`--cutoff` / `--white` / `--gamma`, **0–100**)  
4. Pack: alpha keeps RGB (or `--color`); black → grey-on-black (`--to-alpha` → matte)

```bash
python3 matte/despeckle.py file.png                 # overwrite
python3 matte/despeckle.py folder/
python3 matte/despeckle.py file.png --new           # → file.despeckle.png
python3 matte/despeckle.py file.png --min-area 8 --cutoff 2
python3 matte/despeckle.py file.png --min-area 64   # freckles on mid/high-res
python3 matte/despeckle.py file.png --mode black --to-alpha
python3 matte/despeckle.py file.png --color white   # force fill when alpha out
python3 matte/despeckle.py file.png --invert
```

| Flag | Default | Meaning |
|------|---------|---------|
| `path` | required | PNG/JPG file or directory |
| `--new` | off | Sidecar `file.despeckle.png` |
| `--recursive` | off | Recurse subfolders |
| `--mode` | `auto` | `auto` \| `alpha` \| `black` |
| `--min-area` | `4` | Drop components with area &lt; N px (`0` = off) |
| `--cutoff` | `1` | Levels black point **0–100** |
| `--white` | `100` | Levels white point **0–100** |
| `--gamma` | `1.0` | Midtone gamma after levels |
| `--to-alpha` | off | BLACK mode → RGBA (fill + cleaned alpha) |
| `--color` | (see below) | Fill when emitting alpha |
| `--invert` | off | Invert coverage before cleanup |

`--color` default: preserve RGB in alpha mode; **white** when using `--to-alpha`.

Min-area is primary; morph open / blur are **not** defaults (too destructive).
High-res freckles often need `--min-area` 32–64+ (or multiple passes by hand).

---

## Levels units (don’t mix)

| Tool | Flags | Range |
|------|-------|--------|
| `cutout` | `--black-point` / `--white-point` | **0–255** raw luma |
| `knockout`, `despeckle` | `--cutoff` / `--white` | **0–100** percent |

---

## Naming

- `snake_case.py`, verb first  
- Format suffix only when engines differ (`recolor_svg` / `recolor_png`)  
- Shared color parse: `colorutil.py`  
- Sidecars (`--new`): `*.recolor.*`, `*.cutout.png`, `*.knockout.png`, `*.despeckle.png`

## Notes

- Folder mode is non-recursive unless `--recursive`.
- Sidecar-named files (`*.recolor.*`, `*.cutout.png`, `*.knockout.png`, `*.despeckle.png`) are skipped on re-run so `--new` is safe. Recolor also skips legacy `*.white.*`.
- Default **overwrites** the source. Use `--new` for a sidecar.
- `despeckle` is not fully idempotent if you raise cutoff/min-area between runs — prefer one clean pass from backup.
- Old names `whiten_svg` / `whiten_png` still work via `scripts/fp-run.sh` aliases.
