#!/usr/bin/env python3
"""Art-on-black PNG/JPG → solid fill + greyscale alpha (levels cutoff).

Process (simple):
  1. RGB → greyscale luminance
  2. Levels: anything under --cutoff (0–100%) → black; rest stretched to 0–255
  3. That greyscale becomes the alpha channel
  4. RGB filled with --color (default pure white)

On a pure black background the look matches the original greys (alpha * white).

Usage:
  python knockout.py path/to/file.png              # overwrite (default)
  python knockout.py path/to/folder/
  python knockout.py path/to/folder/ --recursive
  python knockout.py path/to/file.png --new        # → file.knockout.png
  python knockout.py path/to/file.jpg --new        # JPEG needs --new
  python knockout.py path/to/file.png --cutoff 5   # crush dark greys
  python knockout.py path/to/file.png --color "#e13e13"
  python knockout.py path/to/file.png --invert     # dark art on light BG
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from PIL import Image

try:
    import numpy as np

    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

IMAGE_EXTS = {".png", ".jpg", ".jpeg"}

# Common named fills
_NAMED = {
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "cyan": (0, 255, 255),
    "magenta": (255, 0, 255),
    "yellow": (255, 255, 0),
}


def parse_color(s: str) -> tuple[int, int, int]:
    """Parse fill color: name | #rgb | #rrggbb | r,g,b."""
    raw = s.strip()
    key = raw.lower()
    if key in _NAMED:
        return _NAMED[key]
    if raw.startswith("#"):
        h = raw[1:]
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        if len(h) != 6 or any(c not in "0123456789abcdefABCDEF" for c in h):
            raise ValueError(f"bad hex color: {s!r}")
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
    m = re.fullmatch(r"\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*", raw)
    if m:
        rgb = tuple(int(x) for x in m.groups())
        if any(v > 255 for v in rgb):
            raise ValueError(f"RGB components must be 0–255: {s!r}")
        return rgb  # type: ignore[return-value]
    raise ValueError(
        f"bad color {s!r} — use name, #rrggbb, or r,g,b (e.g. white / #fff / 255,0,0)"
    )


def _levels_u8(L: float, black: float, white: float, gamma: float) -> int:
    """Map luminance through levels → alpha 0–255."""
    if L <= black:
        return 0
    if L >= white:
        return 255
    t = (L - black) / (white - black)
    if gamma != 1.0:
        t = t**gamma
    return int(round(min(1.0, max(0.0, t)) * 255))


def knockout_image(
    im: Image.Image,
    *,
    cutoff: float = 0.0,
    white: float = 100.0,
    gamma: float = 1.0,
    color: tuple[int, int, int] = (255, 255, 255),
    invert: bool = False,
) -> Image.Image:
    """Greyscale→alpha after levels; RGB = solid fill color."""
    if not 0.0 <= cutoff < white <= 100.0:
        raise ValueError("need 0 <= cutoff < white <= 100")
    if gamma <= 0:
        raise ValueError("gamma must be > 0")
    fr, fg, fb = color
    if not all(0 <= c <= 255 for c in (fr, fg, fb)):
        raise ValueError("fill color components must be 0–255")

    black_pt = cutoff / 100.0 * 255.0
    white_pt = white / 100.0 * 255.0

    rgba = im.convert("RGBA")
    if HAS_NUMPY:
        arr = np.array(rgba, dtype=np.uint8)
        r = arr[:, :, 0].astype(np.float32)
        g = arr[:, :, 1].astype(np.float32)
        b = arr[:, :, 2].astype(np.float32)
        # 1) greyscale luminance of the image
        L = 0.2126 * r + 0.7152 * g + 0.0722 * b
        if invert:
            L = 255.0 - L

        # 2) levels → alpha
        a = np.zeros(L.shape, dtype=np.uint8)
        solid = L >= white_pt
        dead = L <= black_pt
        mid = ~(solid | dead)
        a[solid] = 255
        a[dead] = 0
        if mid.any():
            t = (L[mid] - black_pt) / (white_pt - black_pt)
            if gamma != 1.0:
                t = np.power(t, gamma)
            a[mid] = np.clip(np.rint(t * 255.0), 0, 255).astype(np.uint8)

        # 3) solid fill RGB where visible
        out = np.zeros_like(arr)
        vis = a > 0
        out[vis, 0] = fr
        out[vis, 1] = fg
        out[vis, 2] = fb
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
            a = _levels_u8(L, black_pt, white_pt, gamma)
            if a > 0:
                op[x, y] = (fr, fg, fb, a)
    return out


def knockout_file(
    src: Path,
    dest: Path,
    *,
    cutoff: float = 0.0,
    white: float = 100.0,
    gamma: float = 1.0,
    color: tuple[int, int, int] = (255, 255, 255),
    invert: bool = False,
) -> None:
    with Image.open(src) as im:
        out = knockout_image(
            im,
            cutoff=cutoff,
            white=white,
            gamma=gamma,
            color=color,
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


def dest_for(src: Path, new: bool) -> Path:
    if new:
        return src.with_name(f"{src.stem}.knockout.png")
    if src.suffix.lower() in {".jpg", ".jpeg"}:
        raise SystemExit(
            f"ERR default overwrites PNG only (JPEG has no alpha); use --new: {src}"
        )
    return src


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Art-on-black → solid fill + greyscale alpha. "
            "Levels cutoff on luminance, then fill RGB. Default: overwrite source PNG."
        )
    )
    ap.add_argument("path", type=Path, help="PNG/JPG file or directory")
    ap.add_argument(
        "--new",
        action="store_true",
        help="Write sidecar file.knockout.png instead of overwriting",
    )
    ap.add_argument("--recursive", action="store_true", help="Recurse into subfolders")
    ap.add_argument(
        "--cutoff",
        type=float,
        default=0.0,
        metavar="PCT",
        help="Levels black point 0–100: brightness under this → alpha 0 (default 0)",
    )
    ap.add_argument(
        "--white",
        type=float,
        default=100.0,
        metavar="PCT",
        help="Levels white point 0–100: brightness at/above this → alpha 255 (default 100)",
    )
    ap.add_argument(
        "--gamma",
        type=float,
        default=1.0,
        help="Midtone gamma on alpha after levels; >1 = crisper (default 1.0)",
    )
    ap.add_argument(
        "--color",
        type=str,
        default="white",
        help='Fill RGB: name, #rrggbb, or r,g,b (default white)',
    )
    ap.add_argument(
        "--invert",
        action="store_true",
        help="Dark art on light background (invert greyscale before levels)",
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

    if not 0.0 <= args.cutoff < args.white <= 100.0:
        print(
            "ERR need 0 <= --cutoff < --white <= 100",
            file=sys.stderr,
        )
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
            knockout_file(
                src,
                dest,
                cutoff=args.cutoff,
                white=args.white,
                gamma=args.gamma,
                color=fill,
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
