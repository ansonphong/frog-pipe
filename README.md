# phong-art-pipe

Phong’s art-asset pipeline scripts:

1. **Adobe export** — batch export from Illustrator / Photoshop  
2. **Matte prep** — whiten · white cutout · color knockout (Python)

GitHub: `github.com/ansonphong/phong-art-pipe` (remote when you push)

## Layout

```
phong-art-pipe/
  matte/                 Python CLIs (Pillow)
  Adobe-Illustrator/     ExtendScript export grouped assets
  Adobe-Photoshop/       Design: export selected layers (WIP)
  README.md
  .gitignore
```

## Matte (Python)

Requires: `pip install pillow` (numpy optional).

```bash
# Force SVG / PNG paints white
python3 matte/whiten_svg.py icon.svg
python3 matte/whiten_png.py sprite.png --in-place

# White glyph on black → pure white + transparent BG
python3 matte/cutout_png.py file.png              # → file.cutout.png

# Color/glow on black → keep color, black transparent
python3 matte/knockout_black.py file.png          # → file.knockout.png
```

See `matte/README.md` for flags (`--in-place`, `--recursive`, `--gamma`, …).

## Adobe Illustrator

`Adobe-Illustrator/export-grouped-assets.jsx` — select groups → dialog → export AI / SVG / PNG.  
Design docs in the same folder. Run via **File → Scripts → Other Script…**

## Adobe Photoshop

`Adobe-Photoshop/export-selected-layers-design.md` — design for selected-layer PNG export (not implemented yet).

## License

Private / studio tooling unless you add a LICENSE.
