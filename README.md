# ⬡ hextile-pipe

Studio matte utilities for **360 Hextile** — whiten, cutout, knockout, despeckle — as a multi-host agent plugin (Claude Code · Codex · Grok) and as plain Python CLIs.

**Install id:** `hextile-pipe@360-hextile`

GitHub: [`github.com/ansonphong/hextile-pipe`](https://github.com/ansonphong/hextile-pipe)

## Install (agent)

```bash
# Claude Code
/plugin marketplace add ansonphong/360-hextile-plugins
/plugin install hextile-pipe@360-hextile

# Grok
grok plugin marketplace add ansonphong/360-hextile-plugins
grok plugin install hextile-pipe --trust
# or path install:
grok plugin install /path/to/hextile-pipe --trust

# Codex
codex plugin marketplace add <path-to-360-hextile-plugins>
codex plugin add hextile-pipe@360-hextile
```

**Invoke:** `/hextile-pipe` · `/hextile-knockout …` · Codex `$hextile-pipe:hextile-knockout`

**Doctor:**

```bash
# from plugin root (or after install, host injects plugin root)
bash scripts/fp-doctor.sh
```

## Layout

```
hextile-pipe/
  .claude-plugin/plugin.json
  .codex-plugin/plugin.json
  skills/                  # agent SSOT (hub + per-tool)
  scripts/
    fp-run.sh              # dispatch matte/<tool>.py
    fp-doctor.sh
    test-plugin.sh
    lib/plugin-root.sh
  matte/                   # real Python CLIs
  illustrator/             # manual ExtendScript
  photoshop/               # design notes (WIP)
  references/adobe-manual.md
  fixtures/                # optional LFS samples
  requirements.txt
```

## Human CLI (standalone)

Requires: `pip install -r requirements.txt` (Pillow; numpy optional).

```bash
python3 matte/whiten_svg.py icon.svg             # overwrites (default)
python3 matte/whiten_png.py sprite.png
python3 matte/cutout.py file.png
python3 matte/knockout.py file.png
python3 matte/despeckle.py file.png
python3 matte/knockout.py file.png --new         # → sidecar
```

| Script | What it does |
|--------|----------------|
| `whiten_svg.py` | SVG fills/strokes → pure white |
| `whiten_png.py` | Opaque PNG pixels → pure white (keep alpha) |
| `cutout.py` | White-on-black → pure white + transparent black |
| `knockout.py` | Greyscale→alpha (levels) + solid fill (default white) |
| `despeckle.py` | Min-area dust removal |

Default **overwrites**. Agents using skills always inject **`--new`**. Flags: `matte/README.md` or `python3 matte/<tool>.py -h`.

### Via plugin helpers

```bash
bash scripts/fp-run.sh knockout file.png --new
bash scripts/fp-doctor.sh
bash scripts/test-plugin.sh
```

`fp-run` resolves the package root from env (`HEXTILE_PIPE_PLUGIN_ROOT` / host plugin roots) or from the script path — never from the art project's cwd.

## Skills

| Skill | Tool |
|-------|------|
| `hextile-pipe` | Hub + doctor routing |
| `hextile-whiten-svg` | `whiten_svg` |
| `hextile-whiten-png` | `whiten_png` |
| `hextile-cutout` | `cutout` |
| `hextile-knockout` | `knockout` |
| `hextile-despeckle` | `despeckle` |

## Adobe

Illustrator JSX and Photoshop design notes are **manual only** — see `references/adobe-manual.md`.

## Marketplace refresh

Catalog lives in **`ansonphong/360-hextile-plugins`**, not this repo.

1. Bump version in **both** `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json` (lockstep).
2. Push this repo.
3. In the marketplace: update `plugins/hextile-pipe` submodule pin.
4. Host: marketplace update / reinstall `hextile-pipe@360-hextile`.

## Version

Current plugin version: **0.1.0** (Claude + Codex manifests must match).

## License

Private / studio tooling unless you add a LICENSE.
