# matte

Python utilities for artwork mattes: recolor silhouettes, cut
black→transparent (glyph + fill color), knock out black with a fill color, or despeckle dust.

Requires: `pip install pillow` (numpy optional, speeds large images).

**Default: overwrite the source file.** Pass `--new` to write a sidecar instead.

**`--color`** (recolor / cutout / knockout / despeckle): name, `#rgb` / `#rrggbb`, or `r,g,b`.
**Default is white.** Shared parser: `colorutil.py`.

Discover live flags anytime: `python3 matte/<tool>.py -h` or `bash scripts/fp-run.sh <tool> -h`.

---

## Quick map

| Need | Script |
|------|--------|
| Force fills/pixels to a color (default white) | `recolor_svg.py` / `recolor_png.py` |
| Glyph cutout (luma→alpha + solid fill color) | `cutout.py` |
| Grey art on black → alpha + any fill color | `knockout.py` |
| Remove dust / freckles (black or transparent) | `despeckle.py` |

---

## Levels language (shared)

| Unit | Flags | Range | Native on |
|------|-------|--------|-----------|
| Percent | `--cutoff` / `--white` | 0–100 | knockout, despeckle |
| Raw luma | `--black-point` / `--white-point` | 0–255 | cutout |

All three tools accept **both** systems as aliases. **Do not mix** for the same end
(e.g. `--cutoff` and `--black-point` together → error).

Conversion: `u8 = pct/100*255`, `pct = u8/255*100`.

---

## SVG recolor — `recolor_svg.py`

Sets shape fills and strokes to a solid color (default `#ffffff`).
Leaves `fill="none"` and `url(...)` paints alone.

```bash
python3 matte/recolor_svg.py icon.svg              # white, overwrites
python3 matte/recolor_svg.py icon.svg --new        # → icon.recolor.svg
python3 matte/recolor_svg.py icon.svg --color "#e13e13"
```

| Flag | Default | Meaning |
|------|---------|---------|
| `--new` | off | Sidecar `file.recolor.svg` |
| `--recursive` | off | Recurse subfolders |
| `--color` | `white` | Fill/stroke color |

---

## PNG recolor — `recolor_png.py`

Sets RGB for pixels with alpha ≥ `--min-alpha` (default pure white).
Fully transparent / sub-floor pixels keep their original RGB.

```bash
python3 matte/recolor_png.py sprite.png            # white, overwrites
python3 matte/recolor_png.py sprite.png --new      # → sprite.recolor.png
python3 matte/recolor_png.py sprite.png --color red
python3 matte/recolor_png.py sprite.png --color "#e13e13" --min-alpha 16
```

| Flag | Default | Meaning |
|------|---------|---------|
| `--new` | off | Sidecar `file.recolor.png` |
| `--recursive` | off | Recurse subfolders |
| `--color` | `white` | RGB fill |
| `--min-alpha` | `1` | Only recolor when alpha ≥ N (1 = all nonzero; 8–16 skips AA fringe) |

---

## Cutout — `cutout.py` (black → transparent + solid fill)

White-on-black PNG/JPG → RGBA: **solid fill RGB** (default white), **black transparent**,
anti-alias via luminance→alpha.

```bash
python3 matte/cutout.py file.png                  # white fill, overwrites
python3 matte/cutout.py file.png --new            # → file.cutout.png
python3 matte/cutout.py file.png --color "#e13e13"
python3 matte/cutout.py file.png --black-point 12 --gamma 1.3
python3 matte/cutout.py file.png --cutoff 5 --white 97   # percent aliases
python3 matte/cutout.py file.png --invert
```

| Flag | Default | Meaning |
|------|---------|---------|
| `--new` | off | Sidecar `file.cutout.png` |
| `--recursive` | off | Recurse subfolders |
| `--black-point` | `8` | Luma ≤ N → alpha 0 (**0–255**) |
| `--white-point` | `247` | Luma ≥ N → alpha 255 (**0–255**) |
| `--cutoff` / `--white` | — | Percent **0–100** aliases |
| `--gamma` | `1.0` | Midtone gamma |
| `--color` | `white` | Solid RGB where visible |
| `--invert` | off | Dark glyph on light BG |

JPEG needs `--new`.

---

## Knockout — `knockout.py` (greyscale → alpha, solid fill)

Art-on-black PNG/JPG → RGBA:

1. RGB → greyscale luminance  
2. **Levels** (`--cutoff` / `--white`, **0–100%**) → **alpha**  
3. **RGB** filled with `--color` (default pure white)

```bash
python3 matte/knockout.py file.png                # white fill
python3 matte/knockout.py file.png --new          # → file.png.knockout.png
python3 matte/knockout.py file.png --cutoff 5 --white 95
python3 matte/knockout.py file.png --black-point 13 --white-point 242
python3 matte/knockout.py file.png --color "#e13e13"
python3 matte/knockout.py file.png --force
```

| Flag | Default | Meaning |
|------|---------|---------|
| `--new` | off | Sidecar `stem.ext.knockout.png` |
| `--recursive` | off | Recurse |
| `--force` | off | Reprocess knockout products |
| `--cutoff` | `0` | Black point **0–100** |
| `--white` | `100` | White point **0–100** |
| `--black-point` / `--white-point` | — | Raw **0–255** aliases |
| `--gamma` | `1.0` | Midtone gamma |
| `--color` | `white` | Solid fill |
| `--invert` | off | Invert greyscale first |

PNG metadata `hextile-pipe-tool=knockout`; refuse reprocess unless `--force`.

---

## Despeckle — `despeckle.py` (dust / freckles)

Coverage-channel cleanup (alpha or luminance) — not RGB blur.

1. Mode `auto`: any `A < 255` → alpha; else luminance  
2. Drop 8-connected components &lt; `--min-area` or scale-aware `--min-area-rel`  
3. Levels once  
4. Optional `--passes P` repeats steps 2–3  

```bash
python3 matte/despeckle.py file.png
python3 matte/despeckle.py file.png --new
python3 matte/despeckle.py file.png --min-area 64
python3 matte/despeckle.py file.png --min-area-rel 0.0001   # scales with long_edge²
python3 matte/despeckle.py file.png --passes 2
python3 matte/despeckle.py file.png --mode black --to-alpha --color white
python3 matte/despeckle.py file.png --black-point 3         # 0–255 alias
```

| Flag | Default | Meaning |
|------|---------|---------|
| `--new` | off | Sidecar `file.despeckle.png` |
| `--recursive` | off | Recurse |
| `--mode` | `auto` | `auto` \| `alpha` \| `black` |
| `--min-area` | `4` | Absolute pixel threshold (`0` = off) |
| `--min-area-rel` | — | Fraction of long_edge² (exclusive with `--min-area`) |
| `--passes` | `1` | Repeat cleanup P times |
| `--cutoff` | `1` | Levels black **0–100** |
| `--white` | `100` | Levels white **0–100** |
| `--black-point` / `--white-point` | — | Raw **0–255** aliases |
| `--gamma` | `1.0` | Midtone gamma |
| `--to-alpha` | off | BLACK → RGBA |
| `--color` | (see help) | Fill when emitting alpha |
| `--invert` | off | Invert coverage first |

`--min-area-rel F` → `effective = max(1, round(F * long_edge²))` (F=0 → off).

High-res freckles: prefer relative, or absolute 32–64+, and/or `--passes 2`.

---

## Naming

- `snake_case.py`, verb first  
- Format suffix only when engines differ (`recolor_svg` / `recolor_png`)  
- Shared helpers: `colorutil.py`  
- Sidecars (`--new`): `*.recolor.*`, `*.cutout.png`, `*.knockout.png`, `*.despeckle.png`

## Notes

- Folder mode is non-recursive unless `--recursive`.
- Sidecar-named files are skipped on re-run so `--new` is safe.
- Default **overwrites** the source. Use `--new` for a sidecar.
- Old names `whiten_svg` / `whiten_png` still work via `scripts/fp-run.sh` aliases.
