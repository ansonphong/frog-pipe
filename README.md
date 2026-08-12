# ⬡ hextile-pipe

Loose bag of **studio utility scripts** for art assets — not a product pipeline.

- **Python** (`matte/`) — recolor, cutout, knockout, despeckle  
- **Illustrator** (`illustrator/`) — batch-export selected groups  
- **Photoshop** (`photoshop/`) — design for layer export (jsx TBD)  

Use whatever you need; nothing requires anything else.

GitHub: [`github.com/ansonphong/hextile-pipe`](https://github.com/ansonphong/hextile-pipe)

## Layout

```
hextile-pipe/
  matte/                 Python CLIs (Pillow) + colorutil
  illustrator/           ExtendScript (.jsx)
  photoshop/             Photoshop script design (WIP)
  fixtures/              Optional sample assets (LFS)
  scripts/               fp-run, doctor, plugin test
  skills/                Claude/Codex plugin skills
  README.md
```

**Conventions:** lowercase folders · Python `snake_case` · JSX/docs `kebab-case`.

---

## Matte (Python)

Requires: `pip install pillow` (numpy optional).

**Default: overwrite the source.** Pass `--new` for a sidecar.  
**`--color`** (where present): name · `#rgb` / `#rrggbb` · `r,g,b` — **default white**.

```bash
python3 matte/recolor_svg.py icon.svg
python3 matte/recolor_png.py sprite.png --color "#e13e13"
python3 matte/cutout.py file.png
python3 matte/knockout.py file.png --cutoff 5 --color white
python3 matte/despeckle.py file.png --min-area 64
python3 matte/knockout.py file.png --new          # sidecar
```

| Script | What it does |
|--------|----------------|
| `recolor_svg.py` | SVG fills/strokes → solid color (default white) |
| `recolor_png.py` | Opaque PNG pixels → solid color, keep alpha (default white) |
| `cutout.py` | White-on-black → pure white + transparent black (AA via luma) |
| `knockout.py` | Greyscale→alpha (levels) + solid fill (default white) |
| `despeckle.py` | Min-area dust removal on black or transparent coverage |
| `colorutil.py` | Shared color parser (not a CLI) |

Detail + recipes: **`matte/README.md`**. Dispatch: `bash scripts/fp-run.sh <tool> …`.

### Params (current)

#### Shared (most tools)

| Flag | Meaning |
|------|---------|
| `path` | File or directory |
| `--new` | Write sidecar instead of overwrite |
| `--recursive` | Recurse into subfolders |
| `--color COLOR` | Fill RGB: name, `#rrggbb`, or `r,g,b` (default **white**) — *recolor, knockout, despeckle* |
| `--invert` | Flip coverage / greyscale (dark art on light) — *cutout, knockout, despeckle* |
| `--gamma G` | Midtone gamma; `>1` = crisper (default `1.0`) — *cutout, knockout, despeckle* |

#### `recolor_png.py` / `recolor_svg.py`

| Flag | Default | Meaning |
|------|---------|---------|
| `--new` | off | Sidecar `*.recolor.png` / `*.recolor.svg` |
| `--recursive` | off | Directory tree |
| `--color` | `white` | Solid fill on paints / opaque pixels |

#### `cutout.py`

| Flag | Default | Meaning |
|------|---------|---------|
| `--new` | off | Sidecar `*.cutout.png` |
| `--recursive` | off | Directory tree |
| `--black-point` | `8` | Luma ≤ N → alpha 0 (**0–255**) |
| `--white-point` | `247` | Luma ≥ N → alpha 255 (**0–255**) |
| `--gamma` | `1.0` | Midtone gamma on alpha |
| `--invert` | off | Dark glyph on light background |

RGB always pure white where visible. JPEG needs `--new` (no alpha).

#### `knockout.py`

| Flag | Default | Meaning |
|------|---------|---------|
| `--new` | off | Sidecar `stem.ext.knockout.png` |
| `--recursive` | off | Directory tree |
| `--force` | off | Reprocess tagged/named knockout products |
| `--cutoff` | `0` | Levels black point **0–100** → alpha 0 |
| `--white` | `100` | Levels white point **0–100** → alpha 255 |
| `--gamma` | `1.0` | Midtone gamma on alpha |
| `--color` | `white` | Solid RGB fill |
| `--invert` | off | Invert greyscale before levels |

#### `despeckle.py`

| Flag | Default | Meaning |
|------|---------|---------|
| `--new` | off | Sidecar `*.despeckle.png` |
| `--recursive` | off | Directory tree |
| `--mode` | `auto` | `auto` \| `alpha` \| `black` coverage |
| `--min-area` | `4` | Drop 8-conn components &lt; N px (`0` = off) |
| `--cutoff` | `1` | Levels black point **0–100** |
| `--white` | `100` | Levels white point **0–100** |
| `--gamma` | `1.0` | Midtone gamma |
| `--to-alpha` | off | BLACK mode: emit RGBA (fill + cleaned alpha) |
| `--color` | (see help) | Fill when emitting alpha / with `--to-alpha` |
| `--invert` | off | Invert coverage before cleanup |

#### Levels units (don’t mix them)

| Tool | Black / white flags | Range |
|------|---------------------|--------|
| `cutout` | `--black-point` / `--white-point` | **0–255** (raw luma) |
| `knockout`, `despeckle` | `--cutoff` / `--white` | **0–100** (percent) |

#### Sidecars (`--new`)

| Tool | Output name |
|------|-------------|
| recolor | `file.recolor.png` / `file.recolor.svg` |
| cutout | `file.cutout.png` |
| knockout | `file.ext.knockout.png` (e.g. `a.png.knockout.png`) |
| despeckle | `file.despeckle.png` |

Legacy: `fp-run.sh` still accepts `whiten_png` / `whiten_svg` → recolor tools.

---

## Illustrator

`illustrator/export-grouped-assets.jsx` — select groups → dialog → export AI / SVG / PNG.

| File | Role |
|------|------|
| `export-grouped-assets.jsx` | Runnable ExtendScript |
| `export-grouped-assets-design.md` | Design notes |
| `artboard-export-all-groups.md` | Earlier brief |
| `test-pure-helpers.js` | Pure-helper tests (no Illustrator) |

Run: **File → Scripts → Other Script…**

---

## Photoshop

`photoshop/export-selected-layers-design.md` — selected-layer PNG export design.  
**Not implemented yet** (no `.jsx`).

---

## Git / LFS

Large binaries (PNG/JPG/PSD/AI/PDF/…) use **Git LFS**.

```bash
git lfs install
git clone https://github.com/ansonphong/hextile-pipe.git
cd hextile-pipe && git lfs pull
```

| File | Role |
|------|------|
| `.gitignore` | Python, OS, Adobe junk, secrets, generated sidecars |
| `.gitattributes` | LF text + LFS globs |
| `.editorconfig` | indent / charset / newlines |
| `.env.example` | template only — never commit `.env` |

Don’t commit export dumps or machine prefs (`prefs.txt`, `export-report.txt`).

## License

Private / studio tooling unless you add a LICENSE.
