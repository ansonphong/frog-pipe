# phong-art-pipe

Phong’s **art-asset pipeline**: export from Adobe, then matte-prep in Python.

```
illustrator/ · photoshop/   →  files on disk  →  matte/  →  library-ready
     STAGE 1 · EXPORT              PNG/SVG/AI      STAGE 2 · PREP
```

GitHub: `github.com/ansonphong/phong-art-pipe` (remote when you push)

Full map: **[`docs/PIPELINE.md`](docs/PIPELINE.md)**

## Layout

```
phong-art-pipe/
│
├── matte/                      # STAGE 2 · prep · runtime: Python
│   ├── README.md
│   ├── whiten_svg.py
│   ├── whiten_png.py
│   ├── cutout.py
│   └── knockout.py
│
├── illustrator/                # STAGE 1 · export · runtime: Illustrator JSX
│   ├── export-grouped-assets.jsx
│   ├── export-grouped-assets-design.md
│   ├── artboard-export-all-groups.md
│   └── test-pure-helpers.js
│
├── photoshop/                  # STAGE 1 · export · runtime: Photoshop JSX
│   └── export-selected-layers-design.md
│       # export-selected-layers.jsx when built
│
├── fixtures/                   # samples (Git LFS for binaries)
├── docs/
│   └── PIPELINE.md             # meta overview
└── README.md
```

**Conventions:** lowercase folders · Python `snake_case` · JSX/docs `kebab-case` · top-level app folders (no `adobe/` nest).

## Matte (Python)

Requires: `pip install pillow` (numpy optional).

```bash
# From repo root:
python3 matte/whiten_svg.py icon.svg
python3 matte/whiten_png.py sprite.png --in-place
python3 matte/cutout.py file.png                 # → file.cutout.png
python3 matte/knockout.py file.png               # → file.knockout.png
```

| Need | Script |
|------|--------|
| Force white (SVG / PNG) | `whiten_svg.py` / `whiten_png.py` |
| White glyph, black → transparent | `cutout.py` |
| Keep color/glow, black → transparent | `knockout.py` |

Flags and details: **`matte/README.md`**.

## Illustrator

`illustrator/export-grouped-assets.jsx` — select groups → dialog → export AI / SVG / PNG.

| File | Role |
|------|------|
| `export-grouped-assets.jsx` | Runnable ExtendScript |
| `export-grouped-assets-design.md` | Design SSOT |
| `artboard-export-all-groups.md` | Original production brief |
| `test-pure-helpers.js` | Pure-helper unit tests (no Illustrator) |

Run via **File → Scripts → Other Script…**

## Photoshop

`photoshop/export-selected-layers-design.md` — design for selected-layer PNG export (**jsx not implemented yet**).

## Git / LFS

```bash
git lfs install
git clone https://github.com/ansonphong/phong-art-pipe.git
cd phong-art-pipe && git lfs pull
```

| File | Role |
|------|------|
| `.gitignore` | Python, OS, Adobe junk, secrets, generated mattes |
| `.gitattributes` | LF text + LFS (raster / PSD / AI / PDF / …) |
| `.editorconfig` | indent / charset / newlines |
| `.env.example` | template only — never commit `.env` |

**Do not commit** export dumps or script prefs (`prefs.txt`, `export-report.txt`).

## License

Private / studio tooling unless you add a LICENSE.
