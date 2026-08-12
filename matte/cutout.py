#!/usr/bin/env python3
"""White-on-black PNG/JPG → pure white RGB + transparent black (crisp AA).

Uses luminance as alpha, forces RGB to white so edges never show a dark halo.

Usage:
  python cutout.py path/to/file.png          # overwrites (default)
  python cutout.py path/to/folder/
  python cutout.py path/to/folder/ --recursive
  python cutout.py path/to/file.png --new    # → file.cutout.png
  python cutout.py path/to/file.jpg --new    # JPEG needs --new (no alpha)
  python cutout.py path/to/file.png --black-point 12 --gamma 1.3
  python cutout.py path/to/file.png --invert   # dark glyph on light BG
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

IMAGE_EXTS = {".png", ".jpg", ".jpeg"}


def _alpha_from_l(L: float, black_point: int, white_point: int, gamma: float) -> int:
    """Map luminance 0..255 → alpha 0..255 with crush + optional gamma."""
    if L <= black_point:
        return 0
    if L >= white_point:
        return 255
    t = (L - black_point) / (white_point - black_point)
    if gamma != 1.0:
        t = t**gamma
    return int(round(min(1.0, max(0.0, t)) * 255))


def cutout_image(
    im: Image.Image,
    *,
    black_point: int = 8,
    white_point: int = 247,
    gamma: float = 1.0,
    invert: bool = False,
) -> Image.Image:
    """Return RGBA: pure white where visible, black field transparent, AA preserved."""
    if black_point >= white_point:
        raise ValueError("black_point must be < white_point")
    if gamma <= 0:
        raise ValueError("gamma must be > 0")

    rgba = im.convert("RGBA")
    if HAS_NUMPY:
        arr = np.array(rgba, dtype=np.uint8)
        r = arr[:, :, 0].astype(np.float32)
        g = arr[:, :, 1].astype(np.float32)
        b = arr[:, :, 2].astype(np.float32)
        L = 0.2126 * r + 0.7152 * g + 0.0722 * b
        if invert:
            L = 255.0 - L
        a = np.zeros(L.shape, dtype=np.uint8)
        solid = L >= white_point
        dead = L <= black_point
        mid = ~(solid | dead)
        a[solid] = 255
        a[dead] = 0
        if mid.any():
            t = (L[mid] - black_point) / (white_point - black_point)
            if gamma != 1.0:
                t = np.power(t, gamma)
            a[mid] = np.clip(np.rint(t * 255.0), 0, 255).astype(np.uint8)
        # pure white RGB; transparent pixels RGB=0 for smaller PNGs
        out = np.zeros_like(arr)
        vis = a > 0
        out[vis, 0] = 255
        out[vis, 1] = 255
        out[vis, 2] = 255
        out[:, :, 3] = a
        return Image.fromarray(out, mode="RGBA")

    # Pillow-only fallback
    pixels = rgba.load()
    w, h = rgba.size
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    op = out.load()
    for y in range(h):
        for x in range(w):
            r, g, b, _ = pixels[x, y]
            L = 0.2126 * r + 0.7152 * g + 0.0722 * b
            if invert:
                L = 255.0 - L
            a = _alpha_from_l(L, black_point, white_point, gamma)
            if a > 0:
                op[x, y] = (255, 255, 255, a)
    return out


def cutout_file(
    src: Path,
    dest: Path,
    *,
    black_point: int = 8,
    white_point: int = 247,
    gamma: float = 1.0,
    invert: bool = False,
) -> None:
    with Image.open(src) as im:
        out = cutout_image(
            im,
            black_point=black_point,
            white_point=white_point,
            gamma=gamma,
            invert=invert,
        )
        dest.parent.mkdir(parents=True, exist_ok=True)
        out.save(dest, format="PNG")


def collect_images(path: Path, recursive: bool) -> list[Path]:
    if path.is_file():
        if path.suffix.lower() not in IMAGE_EXTS:
            raise SystemExit(f"ERR not a PNG/JPG file: {path}")
        return [path]
    if not path.is_dir():
        raise SystemExit(f"ERR path not found: {path}")
    files: list[Path] = []
    patterns = ("*.png", "*.PNG", "*.jpg", "*.JPG", "*.jpeg", "*.JPEG")
    if recursive:
        for pat in patterns:
            files.extend(path.glob(f"**/{pat}"))
    else:
        for pat in patterns:
            files.extend(path.glob(pat))
    files = sorted({p for p in files if p.is_file()})
    return [p for p in files if not p.name.lower().endswith(".cutout.png")]


def dest_for(src: Path, new: bool) -> Path:
    if new:
        return src.with_name(f"{src.stem}.cutout.png")
    if src.suffix.lower() in {".jpg", ".jpeg"}:
        raise SystemExit(
            f"ERR default overwrites PNG only (JPEG has no alpha); use --new: {src}"
        )
    return src


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=(
            "White-on-black image → pure white + transparent black (crisp AA). "
            "Luminance becomes alpha; RGB forced to white. "
            "Default: overwrite source PNG."
        )
    )
    ap.add_argument("path", type=Path, help="PNG/JPG file or directory")
    ap.add_argument(
        "--new",
        action="store_true",
        help="Write sidecar file.cutout.png instead of overwriting",
    )
    ap.add_argument("--recursive", action="store_true", help="Recurse into subfolders")
    ap.add_argument(
        "--black-point",
        type=int,
        default=8,
        help="L <= N → alpha 0 (default 8)",
    )
    ap.add_argument(
        "--white-point",
        type=int,
        default=247,
        help="L >= N → alpha 255 (default 247)",
    )
    ap.add_argument(
        "--gamma",
        type=float,
        default=1.0,
        help="Midtone gamma >1 = crisper (default 1.0)",
    )
    ap.add_argument(
        "--invert",
        action="store_true",
        help="Dark glyph on light background",
    )
    args = ap.parse_args(argv)

    path = args.path.expanduser().resolve()
    if not path.exists():
        print(f"ERR path not found: {path}", file=sys.stderr)
        return 1

    try:
        files = collect_images(path, args.recursive)
    except SystemExit as e:
        print(str(e), file=sys.stderr)
        return 1

    if not files:
        print(f"ERR no PNG/JPG files found under: {path}", file=sys.stderr)
        return 1

    errors = 0
    for src in files:
        try:
            dest = dest_for(src, args.new)
            cutout_file(
                src,
                dest,
                black_point=args.black_point,
                white_point=args.white_point,
                gamma=args.gamma,
                invert=args.invert,
            )
            print(f"OK  {src} -> {dest}")
        except SystemExit as e:
            print(str(e), file=sys.stderr)
            errors += 1
        except Exception as e:
            print(f"ERR {src}: {e}", file=sys.stderr)
            errors += 1
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
