# phong-art-pipe — pipeline map

Two stages. Folder = host runtime. Extension = language.

```
  ┌─────────────────────────────┐
  │  STAGE 1 · EXPORT           │
  │  illustrator/  (.jsx)       │
  │  photoshop/    (.jsx)       │
  └─────────────┬───────────────┘
                │  AI / SVG / PNG on disk
                ▼
  ┌─────────────────────────────┐
  │  STAGE 2 · MATTE PREP       │
  │  matte/        (.py)        │
  └─────────────┬───────────────┘
                │  alpha-ready assets
                ▼
         library / product use
```

## Stage 1 — Export (Adobe)

| Folder | Runtime | Job |
|--------|---------|-----|
| `illustrator/` | Illustrator ExtendScript | Batch-export selected **groups** → AI / SVG / PNG |
| `photoshop/` | Photoshop ExtendScript | Batch-export selected **layers** → transparent PNG (design; jsx TBD) |

Naming: `export-*.jsx` + matching `export-*-design.md`.

## Stage 2 — Matte prep (Python)

| Script | Job |
|--------|-----|
| `matte/whiten_svg.py` | Shape paints → pure white |
| `matte/whiten_png.py` | Opaque pixels → pure white (keep alpha) |
| `matte/cutout.py` | White-on-black → pure white + transparent black |
| `matte/knockout.py` | Color-on-black → keep color + transparent black |

Naming: `snake_case.py`, **verb first**. Format suffix only when engines differ (`whiten_svg` / `whiten_png`).

## Shared

| Path | Role |
|------|------|
| `fixtures/` | Intentional samples (Git LFS for binaries) |
| `docs/` | Meta docs (this file) |
| Root hygiene | `.gitignore`, `.gitattributes` (LFS), `.editorconfig` |

## Rules (frozen)

1. Top-level folder = **where it runs** (`matte` · `illustrator` · `photoshop`).
2. No nesting Adobe under `adobe/`.
3. Python = `snake_case`; JSX/docs = `kebab-case`.
4. Do not mix runtimes in one folder.
5. Generated `*.cutout.png` / `*.knockout.png` / `*.white.*` stay gitignored.
