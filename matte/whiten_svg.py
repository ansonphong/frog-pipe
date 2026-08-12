#!/usr/bin/env python3
"""Whiten all SVG shape paints (fill/stroke → #ffffff). Keeps structure.

Usage:
  python whiten_svg.py path/to/file.svg
  python whiten_svg.py path/to/folder/
  python whiten_svg.py path/to/folder/ --recursive
  python whiten_svg.py path/to/file.svg --in-place
"""
from __future__ import annotations

import argparse
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SHAPE_TAGS = {
    "path",
    "rect",
    "circle",
    "ellipse",
    "polygon",
    "polyline",
    "line",
    "text",
    "tspan",
}
SKIP_PAINT = {"none", "None", ""}
URL_RE = re.compile(r"^\s*url\s*\(", re.I)
STYLE_FILL_RE = re.compile(r"(fill)\s*:\s*([^;]+)", re.I)
STYLE_STROKE_RE = re.compile(r"(stroke)\s*:\s*([^;]+)", re.I)
NS_SVG = "http://www.w3.org/2000/svg"


def local_tag(tag: str) -> str:
    if tag.startswith("{"):
        return tag.rsplit("}", 1)[-1]
    return tag


def should_whiten_paint(value: str | None) -> bool:
    if value is None:
        return False
    v = value.strip()
    if v in SKIP_PAINT or URL_RE.match(v):
        return False
    return True


def whiten_style(style: str) -> str:
    def repl(m: re.Match[str]) -> str:
        prop, val = m.group(1), m.group(2)
        if should_whiten_paint(val):
            return f"{prop}:#ffffff"
        return m.group(0)

    style = STYLE_FILL_RE.sub(repl, style)
    style = STYLE_STROKE_RE.sub(repl, style)
    return style


def whiten_element(el: ET.Element) -> None:
    tag = local_tag(el.tag)
    if "fill" in el.attrib and should_whiten_paint(el.attrib["fill"]):
        el.set("fill", "#ffffff")
    if "stroke" in el.attrib and should_whiten_paint(el.attrib["stroke"]):
        el.set("stroke", "#ffffff")
    if "style" in el.attrib:
        el.set("style", whiten_style(el.attrib["style"]))
    # Unfilled drawing shapes default to black in SVG — force white fill
    if tag in SHAPE_TAGS and "fill" not in el.attrib:
        style = el.attrib.get("style", "")
        if not re.search(r"fill\s*:", style, re.I):
            if tag != "line":  # lines are stroke-only by convention
                el.set("fill", "#ffffff")


def whiten_svg_file(src: Path, dest: Path) -> None:
    ET.register_namespace("", NS_SVG)
    tree = ET.parse(src)
    root = tree.getroot()
    for el in root.iter():
        whiten_element(el)
    dest.parent.mkdir(parents=True, exist_ok=True)
    tree.write(dest, encoding="utf-8", xml_declaration=True)


def collect_svgs(path: Path, recursive: bool) -> list[Path]:
    if path.is_file():
        if path.suffix.lower() != ".svg":
            raise SystemExit(f"ERR not an .svg file: {path}")
        return [path]
    if not path.is_dir():
        raise SystemExit(f"ERR path not found: {path}")
    if recursive:
        files = list(path.glob("**/*.svg")) + list(path.glob("**/*.SVG"))
    else:
        files = list(path.glob("*.svg")) + list(path.glob("*.SVG"))
    files = sorted({p for p in files if p.is_file()})
    return [p for p in files if not p.name.lower().endswith(".white.svg")]


def dest_for(src: Path, in_place: bool) -> Path:
    if in_place:
        return src
    return src.with_name(f"{src.stem}.white{src.suffix}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Force SVG shape paints to pure white.")
    ap.add_argument("path", type=Path, help="SVG file or directory")
    ap.add_argument("--in-place", action="store_true", help="Overwrite source files")
    ap.add_argument("--recursive", action="store_true", help="Recurse into subfolders")
    args = ap.parse_args(argv)

    path = args.path.expanduser().resolve()
    if not path.exists():
        print(f"ERR path not found: {path}", file=sys.stderr)
        return 1

    try:
        files = collect_svgs(path, args.recursive)
    except SystemExit as e:
        print(str(e), file=sys.stderr)
        return 1

    if not files:
        print(f"ERR no .svg files found under: {path}", file=sys.stderr)
        return 1

    errors = 0
    for src in files:
        dest = dest_for(src, args.in_place)
        try:
            whiten_svg_file(src, dest)
            print(f"OK  {src} -> {dest}")
        except Exception as e:
            errors += 1
            print(f"ERR {src}: {e}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
