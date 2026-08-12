#!/usr/bin/env python3
"""Color-on-black PNG/JPG → keep color, black → transparent (soft glow OK).

Assumes art is composited on black (premultiplied). Alpha from brightness
(max channel by default), then un-premultiply so edge pixels recover full
color at partial opacity — no dark fringe on light backgrounds.

Usage:
  python knockout_black.py path/to/file.png
  python knockout_black.py path/to/file.jpg          # → file.knockout.png
  python knockout_black.py path/to/folder/
  python knockout_black.py path/to/folder/ --recursive
  python knockout_black.py path/to/file.png --in-place
  python knockout_black.py path/to/file.png --black-point 8 --gamma 1.2
  python knockout_black.py path/to/file.png --alpha-from lum
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
ALPHA_FROM_CHOICES = ("max", "lum")


def _coverage(r: float, g: float, b: float, mode: str) -> float:
    if mode == "lum":
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    return max(r, g, b)


def _alpha_u8(cov: float, black_point: int, white_point: int, gamma: float) -> int:
    if cov <= black_point:
        return 0
    if cov >= white_point:
        return 255
    t = (cov - black_point) / (white_point - black_point)
    if gamma != 1.0:
        t = t**gamma
    return int(round(min(1.0, max(0.0, t)) * 255))


def knockout_image(
    im: Image.Image,
    *,
    black_point: int = 8,
    white_point: int = 247,
    gamma: float = 1.0,
    alpha_from: str = "max",
    invert: bool = False,
) -> Image.Image:
    """Return RGBA: original color recovered, black field transparent."""
    if alpha_from not in ALPHA_FROM_CHOICES:
        raise ValueError(f"alpha_from must be one of {ALPHA_FROM_CHOICES}")
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
        if alpha_from == "lum":
            cov = 0.2126 * r + 0.7152 * g + 0.0722 * b
        else:
            cov = np.maximum(np.maximum(r, g), b)
        if invert:
            cov = 255.0 - cov

        a = np.zeros(cov.shape, dtype=np.uint8)
        solid = cov >= white_point
        dead = cov <= black_point
        mid = ~(solid | dead)
        a[solid] = 255
        a[dead] = 0
        if mid.any():
            t = (cov[mid] - black_point) / (white_point - black_point)
            if gamma != 1.0:
                t = np.power(t, gamma)
            a[mid] = np.clip(np.rint(t * 255.0), 0, 255).astype(np.uint8)

        out = np.zeros_like(arr)
        vis = a > 0
        # Un-premultiply against black: C' = C / (a/255)
        af = a.astype(np.float32) / 255.0
        # avoid div0 on transparent; only write visible
        safe = np.where(vis, af, 1.0)
        out_r = np.clip(np.rint(r / safe), 0, 255).astype(np.uint8)
        out_g = np.clip(np.rint(g / safe), 0, 255).astype(np.uint8)
        out_b = np.clip(np.rint(b / safe), 0, 255).astype(np.uint8)
        out[vis, 0] = out_r[vis]
        out[vis, 1] = out_g[vis]
        out[vis, 2] = out_b[vis]
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
            cov = _coverage(float(r), float(g), float(b), alpha_from)
            if invert:
                cov = 255.0 - cov
            a = _alpha_u8(cov, black_point, white_point, gamma)
            if a <= 0:
                continue
            af = a / 255.0
            op[x, y] = (
                min(255, int(round(r / af))),
                min(255, int(round(g / af))),
                min(255, int(round(b / af))),
                a,
            )
    return out


def knockout_file(
    src: Path,
    dest: Path,
    *,
    black_point: int = 8,
    white_point: int = 247,
    gamma: float = 1.0,
    alpha_from: str = "max",
    invert: bool = False,
) -> None:
    with Image.open(src) as im:
        out = knockout_image(
            im,
            black_point=black_point,
            white_point=white_point,
            gamma=gamma,
            alpha_from=alpha_from,
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
    return [p for p in files if not p.name.lower().endswith(".knockout.png")]


def dest_for(src: Path, in_place: bool) -> Path:
    if in_place:
        if src.suffix.lower() in {".jpg", ".jpeg"}:
            raise SystemExit(
                f"ERR --in-place requires PNG source (JPEG cannot store alpha): {src}"
            )
        return src
    return src.with_name(f"{src.stem}.knockout.png")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Color-on-black image → keep color, black transparent. "
            "Alpha from brightness; un-premultiply so glow edges stay clean."
        )
    )
    ap.add_argument("path", type=Path, help="PNG/JPG file or directory")
    ap.add_argument("--in-place", action="store_true", help="Overwrite source PNG")
    ap.add_argument("--recursive", action="store_true", help="Recurse into subfolders")
    ap.add_argument(
        "--black-point",
        type=int,
        default=8,
        help="coverage <= N → alpha 0 (default 8)",
    )
    ap.add_argument(
        "--white-point",
        type=int,
        default=247,
        help="coverage >= N → alpha 255 (default 247)",
    )
    ap.add_argument(
        "--gamma",
        type=float,
        default=1.0,
        help="Midtone gamma on alpha >1 = crisper (default 1.0)",
    )
    ap.add_argument(
        "--alpha-from",
        choices=ALPHA_FROM_CHOICES,
        default="max",
        help="Coverage metric: max channel (glow default) or luminance",
    )
    ap.add_argument(
        "--invert",
        action="store_true",
        help="Dark art on light background (invert coverage)",
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
            dest = dest_for(src, args.in_place)
            knockout_file(
                src,
                dest,
                black_point=args.black_point,
                white_point=args.white_point,
                gamma=args.gamma,
                alpha_from=args.alpha_from,
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
