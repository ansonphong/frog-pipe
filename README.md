# phong-art-pipe

Phong’s art-asset pipeline scripts:

1. **Adobe export** — batch export from Illustrator / Photoshop  
2. **Matte prep** — whiten · white cutout · color knockout (Python)

GitHub: `github.com/ansonphong/phong-art-pipe` (remote when you push)

## Layout

```
phong-art-pipe/
  matte/                          Python CLIs (Pillow)
  adobe/
    illustrator/                  ExtendScript export grouped assets
    photoshop/                    Design: export selected layers (WIP)
  README.md
  .gitignore
```

All paths: **lowercase**, **kebab-case** files, nested `adobe/<app>/`.

## Matte (Python)

Requires: `pip install pillow` (numpy optional).

```bash
# From repo root:
python3 matte/whiten_svg.py icon.svg
python3 matte/whiten_png.py sprite.png --in-place
python3 matte/cutout_png.py file.png              # → file.cutout.png
python3 matte/knockout_black.py file.png          # → file.knockout.png
```

See `matte/README.md` for flags (`--in-place`, `--recursive`, `--gamma`, …).

## Adobe Illustrator

`adobe/illustrator/export-grouped-assets.jsx` — select groups → dialog → export AI / SVG / PNG.

| File | Role |
|------|------|
| `export-grouped-assets.jsx` | Runnable ExtendScript |
| `export-grouped-assets-design.md` | Design SSOT |
| `artboard-export-all-groups.md` | Original production brief |
| `test-pure-helpers.js` | Pure-helper unit tests (no Illustrator) |

Run via **File → Scripts → Other Script…**

## Adobe Photoshop

`adobe/photoshop/export-selected-layers-design.md` — design for selected-layer PNG export (not implemented yet).

## Naming conventions

- Folders: `lowercase` / `kebab-case` (`adobe/illustrator`, not `Adobe-Illustrator`)
- Docs & scripts: `kebab-case` (`export-grouped-assets.jsx`)
- Python package folder: short noun (`matte/`)

## License

Private / studio tooling unless you add a LICENSE.
