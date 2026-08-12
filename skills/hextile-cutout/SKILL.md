---
name: hextile-cutout
description: "White-on-black cutout — pure white RGB + transparent black with AA. Use for glyphs/logos on black."
user-invocable: true
---

# hextile-cutout

White-on-black image → pure white + transparent black (crisp anti-alias via luminance→alpha).

## Run

```bash
ROOT="${HEXTILE_PIPE_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT:-${GROK_PLUGIN_ROOT:-${PLUGIN_ROOT:-}}}}"
bash "$ROOT/scripts/fp-run.sh" cutout <path> --new [flags…]
```

**Agent default:** always pass `--new` unless user insists on overwrite.

## Common flags

`bash "$ROOT/scripts/fp-run.sh" cutout -h`

| Flag | Meaning |
|------|---------|
| `--new` | Sidecar `file.cutout.png` |
| `--recursive` | Directory tree |
| `--black-point N` | L ≤ N → alpha 0 |
| `--white-point N` | L ≥ N → alpha 255 |
| `--gamma G` | Midtone gamma |
| `--invert` | Dark glyph on light background |

## Path rules

- WSL-normalize Windows paths.
- JPEG needs `--new`.
- Fence CLI output.
