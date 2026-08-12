---
name: hextile-whiten-svg
description: "Force SVG shape fills/strokes to pure white. Use for icon silhouettes that must be white."
user-invocable: true
---

# hextile-whiten-svg

Forces SVG shape paints to `#ffffff`. Leaves `fill="none"` and `url(...)` paints alone.

## Run

```bash
ROOT="${HEXTILE_PIPE_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT:-${GROK_PLUGIN_ROOT:-${PLUGIN_ROOT:-}}}}"
bash "$ROOT/scripts/fp-run.sh" whiten_svg <path> --new [flags…]
```

**Agent default:** always pass `--new` unless user insists on overwrite.

## Flags

`bash "$ROOT/scripts/fp-run.sh" whiten_svg -h`

| Flag | Meaning |
|------|---------|
| `--new` | Sidecar `file.white.svg` |
| `--recursive` | Directory tree |

## Path rules

- SVG only. WSL-normalize paths. Fence CLI output.
