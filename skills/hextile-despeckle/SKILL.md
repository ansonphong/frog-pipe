---
name: hextile-despeckle
description: "Despeckle dust/freckles on black-bg or transparent art via min-area components + levels."
user-invocable: true
---

# hextile-despeckle

Removes small islands on black-bg or transparent coverage (not RGB blur).

## Run

```bash
ROOT="${HEXTILE_PIPE_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT:-${GROK_PLUGIN_ROOT:-${PLUGIN_ROOT:-}}}}"
bash "$ROOT/scripts/fp-run.sh" despeckle <path> --new [flags…]
```

**Agent default:** always pass `--new` unless user insists on overwrite.

## Common flags

`bash "$ROOT/scripts/fp-run.sh" despeckle -h`

| Flag | Meaning |
|------|---------|
| `--new` | Sidecar `file.despeckle.png` |
| `--recursive` | Directory tree |
| `--mode auto\|alpha\|black` | Coverage source |
| `--min-area N` | Drop components under N pixels |
| `--cutoff` / `--white` / `--gamma` | Levels on coverage |
| `--to-alpha` | BLACK mode: emit RGBA |
| `--color` / `--invert` | Fill / invert |

## Path rules

- WSL-normalize paths. Fence CLI output.
