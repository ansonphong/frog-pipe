"""Shared color parse helpers for matte CLIs.

Accepts: named color | #rgb | #rrggbb | r,g,b
Default fill across tools is white.
"""
from __future__ import annotations

import re

NAMED = {
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "cyan": (0, 255, 255),
    "magenta": (255, 0, 255),
    "yellow": (255, 255, 0),
}

COLOR_HELP = "Fill RGB: name, #rrggbb, or r,g,b (default white)"


def parse_color(s: str) -> tuple[int, int, int]:
    """Parse fill color: name | #rgb | #rrggbb | r,g,b."""
    raw = s.strip()
    key = raw.lower()
    if key in NAMED:
        return NAMED[key]
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


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    r, g, b = rgb
    return f"#{r:02x}{g:02x}{b:02x}"
