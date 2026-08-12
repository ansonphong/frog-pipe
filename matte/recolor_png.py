#!/usr/bin/env python3
"""Recolor all opaque (and semi-transparent) PNG pixels; keep alpha.

Default fill is pure white. Use --color for any RGB.

Usage:
  python recolor_png.py path/to/file.png              # white (default), overwrites
  python recolor_png.py path/to/folder/
  python recolor_png.py path/to/folder/ --recursive
  python recolor_png.py path/to/file.png --new        # → file.recolor.png
  python recolor_png.py path/to/file.png --color "#e13e13"
  python recolor_png.py path/to/file.png --color 0,200,255
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image

from colorutil import COLOR_HELP, parse_color

try:
    import numpy as np

    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

SIDECAR_MARKER = ".recolor.png"
# Legacy sidecars from the old whiten_png tool name
_LEGACY_SIDECAR = ".white.png"


def recolor_png_file(
    src: Path, dest: Path, color: tuple[int, int, int] = (255, 255, 255)
) -> None:
    fr, fg, fb = color
    if not all(0 <= c <= 255 for c in color):
        raise ValueError("fill color components must be 0–255")
    with Image.open(src) as im:
        rgba = im.convert("RGBA")
        if HAS_NUMPY:
            arr = np.array(rgba)
            alpha = arr[:, :, 3]
            mask = alpha > 0
            arr[mask, 0] = fr
            arr[mask, 1] = fg
            arr[mask, 2] = fb
            out = Image.fromarray(arr, mode="RGBA")
        else:
            pixels = rgba.load()
            w, h = rgba.size
            for y in range(h):
                for x in range(w):
                    r, g, b, a = pixels[x, y]
                    if a > 0:
                        pixels[x, y] = (fr, fg, fb, a)
            out = rgba
        dest.parent.mkdir(parents=True, exist_ok=True)
        out.save(dest, format="PNG")


def collect_pngs(path: Path, recursive: bool) -> list[Path]:
    if path.is_file():
        if path.suffix.lower() != ".png":
            raise SystemExit(f"ERR not a .png file: {path}")
        return [path]
    if not path.is_dir():
        raise SystemExit(f"ERR path not found: {path}")
    if recursive:
        files = list(path.glob("**/*.png")) + list(path.glob("**/*.PNG"))
    else:
        files = list(path.glob("*.png")) + list(path.glob("*.PNG"))
    files = sorted({p for p in files if p.is_file()})
    skip = (SIDECAR_MARKER, _LEGACY_SIDECAR)
    return [p for p in files if not any(p.name.lower().endswith(s) for s in skip)]


def dest_for(src: Path, new: bool) -> Path:
    if new:
        return src.with_name(f"{src.stem}.recolor{src.suffix}")
    return src


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Force PNG opaque pixels to a solid color (default white); "
            "preserve alpha. Default: overwrite source."
        )
    )
    ap.add_argument("path", type=Path, help="PNG file or directory")
    ap.add_argument(
        "--new",
        action="store_true",
        help="Write sidecar file.recolor.png instead of overwriting",
    )
    ap.add_argument("--recursive", action="store_true", help="Recurse into subfolders")
    ap.add_argument(
        "--color",
        type=str,
        default="white",
        help=COLOR_HELP,
    )
    args = ap.parse_args(argv)

    path = args.path.expanduser().resolve()
    if not path.exists():
        print(f"ERR path not found: {path}", file=sys.stderr)
        return 1

    try:
        fill = parse_color(args.color)
    except ValueError as e:
        print(f"ERR {e}", file=sys.stderr)
        return 1

    try:
        files = collect_pngs(path, args.recursive)
    except SystemExit as e:
        print(str(e), file=sys.stderr)
        return 1

    if not files:
        print(f"ERR no .png files found under: {path}", file=sys.stderr)
        return 1

    errors = 0
    for src in files:
        dest = dest_for(src, args.new)
        try:
            recolor_png_file(src, dest, color=fill)
            print(f"OK  {src} -> {dest}")
        except Exception as e:
            errors += 1
            print(f"ERR {src}: {e}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
