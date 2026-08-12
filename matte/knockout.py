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
  python knockout.py path/to/file.png --new        # → file.png.knockout.png
  python knockout.py path/to/file.jpg --new        # JPEG needs --new
  python knockout.py path/to/file.png --cutoff 5   # crush dark greys
  python knockout.py path/to/file.png --color "#e13e13"
  python knockout.py path/to/file.png --invert     # dark art on light BG
  python knockout.py path/to/file.png --force      # reprocess hextile-pipe outputs
"""
from __future__ import annotations

import argparse
import math
import os
import re
import sys
import tempfile
from pathlib import Path

from PIL import Image
from PIL.PngImagePlugin import PngInfo

try:
    import numpy as np

    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

IMAGE_EXTS = {".png", ".jpg", ".jpeg"}
META_TOOL_KEY = "hextile-pipe-tool"
# Accept legacy frog-pipe tags so old knockouts still detect as products
META_TOOL_KEYS_READ = (META_TOOL_KEY, "frog-pipe-tool")
META_TOOL_VALUE = "knockout"
SIDECAR_MARKER = ".knockout.png"

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


def _validate_levels(cutoff: float, white: float, gamma: float) -> None:
    if not (math.isfinite(cutoff) and math.isfinite(white)):
        raise ValueError("cutoff/white must be finite numbers")
    if not 0.0 <= cutoff < white <= 100.0:
        raise ValueError("need 0 <= cutoff < white <= 100")
    if not (math.isfinite(gamma) and gamma > 0):
        raise ValueError("gamma must be a finite number > 0")


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


def is_knockout_product(path: Path, im: Image.Image | None = None) -> bool:
    """True if this file was produced by knockout (sidecar name or PNG metadata)."""
    if path.name.lower().endswith(SIDECAR_MARKER):
        return True
    if path.suffix.lower() != ".png":
        return False
    try:
        img = im if im is not None else Image.open(path)
        close = im is None
        try:
            meta = getattr(img, "text", None) or {}
            if any(meta.get(k) == META_TOOL_VALUE for k in META_TOOL_KEYS_READ):
                return True
            # Pillow sometimes keeps info dict
            info = getattr(img, "info", None) or {}
            if any(info.get(k) == META_TOOL_VALUE for k in META_TOOL_KEYS_READ):
                return True
        finally:
            if close:
                img.close()
    except Exception:
        return False
    return False


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
    _validate_levels(cutoff, white, gamma)
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


def _pnginfo() -> PngInfo:
    info = PngInfo()
    info.add_text(META_TOOL_KEY, META_TOOL_VALUE)
    return info


def _atomic_save_png(img: Image.Image, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(suffix=".png", dir=str(dest.parent))
    os.close(fd)
    tmp_path = Path(tmp_name)
    try:
        img.save(tmp_path, format="PNG", pnginfo=_pnginfo())
        os.replace(tmp_path, dest)
    except Exception:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
        raise


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
        _atomic_save_png(out, dest)


def collect_images(path: Path, recursive: bool, *, force: bool) -> list[Path]:
    if path.is_file():
        if path.suffix.lower() not in IMAGE_EXTS:
            raise SystemExit(f"ERR not a PNG/JPG file: {path}")
        files = [path]
    elif path.is_dir():
        if recursive:
            candidates = path.rglob("*")
        else:
            candidates = path.iterdir()
        files = sorted(
            {
                p
                for p in candidates
                if p.is_file() and p.suffix.lower() in IMAGE_EXTS
            }
        )
    else:
        raise SystemExit(f"ERR path not found: {path}")

    out: list[Path] = []
    for p in files:
        # Always skip knockout sidecars unless --force (and even then only if explicit file?)
        if p.name.lower().endswith(SIDECAR_MARKER) and not force:
            continue
        if not force and is_knockout_product(p):
            continue
        out.append(p)
    return out


def dest_for(src: Path, new: bool) -> Path:
    """Sidecar includes source extension so asset.png / asset.jpg never collide."""
    if new:
        # e.g. photo.png → photo.png.knockout.png ; photo.jpg → photo.jpg.knockout.png
        ext = src.suffix.lower().lstrip(".") or "img"
        return src.with_name(f"{src.stem}.{ext}{SIDECAR_MARKER}")
    if src.suffix.lower() in {".jpg", ".jpeg"}:
        raise SystemExit(
            f"ERR default overwrites PNG only (JPEG has no alpha); use --new: {src}"
        )
    return src


def preflight_jobs(
    files: list[Path], *, new: bool, force: bool
) -> list[tuple[Path, Path]]:
    """Resolve all destinations and validate *before* any write."""
    jobs: list[tuple[Path, Path]] = []
    errors: list[str] = []

    for src in files:
        try:
            if not force and is_knockout_product(src):
                errors.append(
                    f"ERR already a knockout product (use --force to reprocess): {src}"
                )
                continue
            dest = dest_for(src, new)
            jobs.append((src, dest))
        except SystemExit as e:
            errors.append(str(e))

    # Unique destinations
    seen: dict[Path, Path] = {}
    for src, dest in jobs:
        key = dest.resolve()
        if key in seen:
            errors.append(
                f"ERR destination collision: {seen[key]} and {src} both → {dest}"
            )
        else:
            seen[key] = src

    # Dest must not clobber a different queued source (e.g. --force --new on
    # asset.png + asset.png.knockout.png would overwrite the latter mid-batch)
    source_keys = {src.resolve() for src, _ in jobs}
    for src, dest in jobs:
        dkey = dest.resolve()
        skey = src.resolve()
        if dkey in source_keys and dkey != skey:
            errors.append(
                f"ERR destination is another queued source (would clobber mid-batch): "
                f"{src} -> {dest}"
            )

    if errors:
        raise SystemExit("\n".join(errors))
    return jobs


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
        help="Write sidecar stem.ext.knockout.png instead of overwriting",
    )
    ap.add_argument("--recursive", action="store_true", help="Recurse into subfolders")
    ap.add_argument(
        "--force",
        action="store_true",
        help="Allow reprocessing files already tagged/named as knockout outputs",
    )
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
        help="Fill RGB: name, #rrggbb, or r,g,b (default white)",
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

    try:
        _validate_levels(args.cutoff, args.white, args.gamma)
    except ValueError as e:
        print(f"ERR {e}", file=sys.stderr)
        return 1

    try:
        files = collect_images(path, args.recursive, force=args.force)
    except SystemExit as e:
        print(str(e), file=sys.stderr)
        return 1

    if not files:
        print(f"ERR no PNG/JPG files found under: {path}", file=sys.stderr)
        return 1

    try:
        jobs = preflight_jobs(files, new=args.new, force=args.force)
    except SystemExit as e:
        print(str(e), file=sys.stderr)
        return 1

    if not jobs:
        print(f"ERR nothing to process under: {path}", file=sys.stderr)
        return 1

    errors = 0
    for src, dest in jobs:
        try:
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
        except Exception as e:
            print(f"ERR {src}: {e}", file=sys.stderr)
            errors += 1
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
