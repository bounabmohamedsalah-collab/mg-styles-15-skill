# mg-styles-15 skill (Claude Code)

Wrapper skill + installer for [Vincentwei1021/mg-styles-15](https://github.com/Vincentwei1021/mg-styles-15) (MIT),
whose repository ships prompts, demos and a renderer but no `SKILL.md`.

```bash
git clone https://github.com/bounabmohamedsalah-collab/mg-styles-15-skill && sh mg-styles-15-skill/install.sh
```

Installs the library into `~/mg-styles-15` (without the gallery videos), its Node and Python audio packages, the OFL
fonts it uses (from google/fonts), and the skill into `~/.claude/skills/mg-styles-15/`. Proprietary CJK fonts used by
some demos are not installed; see `skill/SKILL.md`.

`arabic-fonts.sh` (run by `install.sh`) also installs 14 OFL Arabic font families from google/fonts into
`~/.local/share/fonts/arabic`, usable by any page rendered in Chromium.

## Also in this repo

- `skills/video-studio/` — entry-point skill for any video request: routing between the video skills and connectors,
  defaults, delivery checklist, and the brand kit (`brand/brand.json`, logo files).
- `skills/arabic-captions/` — local Arabic/darija/FR/EN transcription (faster-whisper large-v3-turbo) and RTL-correct
  word-highlight captions (SRT + ASS), burned with ffmpeg/libass.
- `skills/video-formats/` — 9:16 / 1:1 / 4:5 / 16:9 versions (crop, fit, blurred background) and TikTok/Reels/Shorts
  safe-zone check.

`install.sh` installs all of them into `~/.claude/skills/` and sets up `~/video-tools` (venv + whisper model).
