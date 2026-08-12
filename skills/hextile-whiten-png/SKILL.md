---
name: hextile-whiten-png
description: "Force PNG opaque pixels to pure white; preserve alpha. Use for tinted silhouettes that must be white."
user-invocable: true
---

# hextile-whiten-png

Sets RGB to pure white for every pixel with alpha > 0. Fully transparent pixels stay transparent.

## Run

```bash
ROOT="${HEXTILE_PIPE_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT:-${GROK_PLUGIN_ROOT:-${PLUGIN_ROOT:-}}}}"
bash "$ROOT/scripts/fp-run.sh" whiten_png <path> --new [flags…]
```

**Agent default:** always pass `--new` unless user insists on overwrite.

## Flags

`bash "$ROOT/scripts/fp-run.sh" whiten_png -h`

| Flag | Meaning |
|------|---------|
| `--new` | Sidecar `file.white.png` |
| `--recursive` | Directory tree |

## Path rules

- PNG only. WSL-normalize paths. Fence CLI output.
