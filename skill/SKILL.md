---
name: mg-styles-15
description: >-
  Make a 10-second (or custom) motion-design film in code in one of 15 proven styles from the mg-styles-15 library
  (Vincentwei1021/mg-styles-15): flat vector, line art, isometric 2.5D, 3D render, frame-by-frame line boil, collage,
  liquid motion, shape morph, Bauhaus, 80s synthwave/VHS, aurora glassmorphism, variety captions (9:16), sticker
  explainer, pixel art, cyberpunk HUD. Picture is code (SVG/Canvas/WebGL/Three.js), sound is synthesized with Python,
  rendered by headless Chrome + ffmpeg. Use when the user asks for an MG / motion-graphics film in one of these styles,
  names mg-styles-15, or wants to reuse its prompts, renderer or audio toolkit.
---

# mg-styles-15

Wrapper skill (written locally; the upstream repo ships no SKILL.md) around the library installed at
`~/mg-styles-15` (`LIB` below). Upstream README: `$LIB/README.md` (English), `$LIB/README.zh-CN.md`.

## Library layout

- `$LIB/prompts/<NN-style>.md` — one complete prompt per style. The English block under 「提示词」 is the brief.
  Only `Creative seed` is story-specific; keep `Signature features` (what makes the style recognisable).
- `$LIB/demos/<NN-style>/` — full source of the original film: `index.html` (+ JS), `audio.py`, `cues.json`, tools.
  Read the matching demo for techniques before building; don't copy its story or branding.
- `$LIB/harness/render.mjs` — renderer. Pages expose `window.renderAt(t)` (may be async), set `window.__ready = true`
  when loaded, and optionally `window.DEMO = {width, height, fps, duration, motionBlur:{samples, shutter}}`.
- `$LIB/lib/audio/mgaudio` — music/SFX synthesis toolkit + 103 CC0 instrument samples (used by every `audio.py`).
- `$LIB/rubric.md` — review rubric (self-review after the first render, then revise). `$LIB/template.md` — new style.

## Workflow

1. Ask (one round, only what changes the film): topic/brand/copy, style (offer the 15 if unsure), aspect ratio
   (default 1920×1080, 30 fps, 10 s), colours.
2. Read `$LIB/prompts/<style>.md`, adapt `Creative seed` (and `Output` if size/length change) to the user's content.
   Then read the demo's `index.html`, `audio.py`, `cues.json` for technique.
3. Build the film as a new folder **inside the library**: `$LIB/demos/user-<slug>/` (pages are served from `$LIB`, so
   `/assets/...`, `/node_modules/...`, `/lib/...` resolve). Write `index.html`, `cues.json`, `audio.py`
   (import mgaudio the same way the demos do; output `out/audio.wav`).
4. Check stills, fix, repeat:
   `cd $LIB && node harness/render.mjs demos/user-<slug> --stills 1,4,8` → `out/stills/*.png` (look at them).
5. Sound: `cd $LIB && .venv/bin/python demos/user-<slug>/audio.py`
6. Render: `cd $LIB && node harness/render.mjs demos/user-<slug>` → `out/video.mp4` (add `--mb 4` for motion blur;
   ~4× slower). Other options are listed at the top of `harness/render.mjs`.
7. Review against `$LIB/rubric.md`, fix the worst issues, re-render. Copy the final MP4 and the source folder to the
   user's working directory and report paths.

## Environment notes (this machine)

- Always export before rendering (render.mjs defaults to a macOS Chrome path and NVIDIA GPU flags):
  `export MG_CHROME=$(ls /opt/pw-browsers/chromium-*/chrome-linux64/chrome | head -1) MG_GPU_ARGS="--no-sandbox --enable-unsafe-swiftshader"`
  WebGL runs on SwiftShader (CPU): shader/Three.js styles render slower.
- Python: use `$LIB/.venv/bin/python` (numpy, scipy, soundfile, numba, pedalboard, pyloudnorm, librosa, pillow,
  fonttools). Asset-prep extras (opencv, scikit-image, rembg) are not installed; add them to the venv only if needed.
- Fonts: OFL fonts from google/fonts are installed under `$LIB/assets/fonts/`. NOT installed (proprietary/unreachable):
  Alibaba PuHuiTi, Alimama ShuHeiTi, Douyin Sans, HarmonyOS Sans SC, Resource Han Rounded, Fusion Pixel 12. A page that
  loads a missing font fails before `__ready` (NetworkError), so demos 01, 02, 03, 06, 07, 08, 09, 10, 12, 18, 19, 20, 22
  don't render as-is. In new films, use only installed fonts (`ls -R $LIB/assets/fonts`), e.g. Noto Sans SC /
  Noto Serif SC / ZCOOL KuaiLe / LXGW Marker Gothic / Long Cang for Chinese.
- Arabic: 14 OFL families are installed system-wide in `~/.local/share/fonts/arabic` (use by family name, no
  @font-face needed): Cairo, Tajawal, Almarai, IBM Plex Sans Arabic, Readex Pro, Noto Sans Arabic (modern/UI);
  Amiri, Noto Naskh Arabic, Scheherazade New (classic); Reem Kufi, Lalezar, Noto Kufi Arabic, Changa, Lemonada
  (display). Set `dir="rtl"` on Arabic text.
- The 3D style (04) needs Blender, which is not installed.
- ffmpeg 7 is on PATH.
