#!/usr/bin/env python3
"""Whiten all opaque (and semi-transparent) PNG pixels; keep alpha.

Usage:
  python whiten_png.py path/to/file.png          # overwrites (default)
  python whiten_png.py path/to/folder/
  python whiten_png.py path/to/folder/ --recursive
  python whiten_png.py path/to/file.png --new    # → file.white.png
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image

try:
    import numpy as np

    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


def whiten_png_file(src: Path, dest: Path) -> None:
    with Image.open(src) as im:
        rgba = im.convert("RGBA")
        if HAS_NUMPY:
            arr = np.array(rgba)
            alpha = arr[:, :, 3]
            mask = alpha > 0
            arr[mask, 0] = 255
            arr[mask, 1] = 255
            arr[mask, 2] = 255
            out = Image.fromarray(arr, mode="RGBA")
        else:
            pixels = rgba.load()
            w, h = rgba.size
            for y in range(h):
                for x in range(w):
                    r, g, b, a = pixels[x, y]
                    if a > 0:
                        pixels[x, y] = (255, 255, 255, a)
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
    return [p for p in files if not p.name.lower().endswith(".white.png")]


def dest_for(src: Path, new: bool) -> Path:
    if new:
        return src.with_name(f"{src.stem}.white{src.suffix}")
    return src


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Force PNG opaque pixels to pure white; preserve alpha. "
            "Default: overwrite source."
        )
    )
    ap.add_argument("path", type=Path, help="PNG file or directory")
    ap.add_argument(
        "--new",
        action="store_true",
        help="Write sidecar file.white.png instead of overwriting",
    )
    ap.add_argument("--recursive", action="store_true", help="Recurse into subfolders")
    args = ap.parse_args(argv)

    path = args.path.expanduser().resolve()
    if not path.exists():
        print(f"ERR path not found: {path}", file=sys.stderr)
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
            whiten_png_file(src, dest)
            print(f"OK  {src} -> {dest}")
        except Exception as e:
            errors += 1
            print(f"ERR {src}: {e}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
