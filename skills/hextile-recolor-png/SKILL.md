---
name: hextile-recolor-png
description: "Force PNG opaque pixels to a solid color (default white); preserve alpha. Use for silhouettes that need a flat fill."
user-invocable: true
---

# hextile-recolor-png

Sets RGB for every pixel with alpha > 0. Fully transparent pixels stay transparent.
Default color is pure white; pass `--color` for any fill.

## Run

```bash
ROOT="${HEXTILE_PIPE_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT:-${GROK_PLUGIN_ROOT:-${PLUGIN_ROOT:-}}}}"
bash "$ROOT/scripts/fp-run.sh" recolor_png <path> --new [flags…]
```

**Agent default:** always pass `--new` unless user insists on overwrite.

## Flags

`bash "$ROOT/scripts/fp-run.sh" recolor_png -h`

| Flag | Meaning |
|------|---------|
| `--new` | Sidecar `file.recolor.png` |
| `--recursive` | Directory tree |
| `--color` | Fill RGB: name, `#rrggbb`, or `r,g,b` (default white) |

## Path rules

- PNG only. WSL-normalize paths. Fence CLI output.
