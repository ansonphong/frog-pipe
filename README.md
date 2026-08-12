# phong-art-pipe

Loose bag of **studio utility scripts** for art assets — not a product pipeline.

- **Python** (`matte/`) — whiten, cutout, color knockout  
- **Illustrator** (`illustrator/`) — batch-export selected groups  
- **Photoshop** (`photoshop/`) — design for layer export (jsx TBD)  

Use whatever you need; nothing requires anything else.

GitHub: `github.com/ansonphong/phong-art-pipe`

## Layout

```
phong-art-pipe/
  matte/                 Python CLIs (Pillow)
  illustrator/           ExtendScript (.jsx)
  photoshop/             Photoshop script design (WIP)
  fixtures/              Optional sample assets (LFS)
  README.md
```

**Conventions:** lowercase folders · Python `snake_case` · JSX/docs `kebab-case`.

---

## Matte (Python)

Requires: `pip install pillow` (numpy optional).

```bash
python3 matte/whiten_svg.py icon.svg
python3 matte/whiten_png.py sprite.png --in-place
python3 matte/cutout.py file.png                 # → file.cutout.png
python3 matte/knockout.py file.png               # → file.knockout.png
```

| Script | What it does |
|--------|----------------|
| `whiten_svg.py` | SVG fills/strokes → pure white |
| `whiten_png.py` | Opaque PNG pixels → pure white (keep alpha) |
| `cutout.py` | White-on-black → pure white + transparent black |
| `knockout.py` | Color-on-black → keep color + transparent black |

Flags (`--in-place`, `--recursive`, `--gamma`, …): **`matte/README.md`**.

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
git clone https://github.com/ansonphong/phong-art-pipe.git
cd phong-art-pipe && git lfs pull
```

| File | Role |
|------|------|
| `.gitignore` | Python, OS, Adobe junk, secrets, generated `*.cutout.png` / `*.knockout.png` |
| `.gitattributes` | LF text + LFS globs |
| `.editorconfig` | indent / charset / newlines |
| `.env.example` | template only — never commit `.env` |

Don’t commit export dumps or machine prefs (`prefs.txt`, `export-report.txt`).

## License

Private / studio tooling unless you add a LICENSE.
