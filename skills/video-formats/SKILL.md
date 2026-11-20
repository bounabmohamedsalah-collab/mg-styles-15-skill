---
name: video-formats
description: >-
  Make platform versions of a finished video (9:16 TikTok/Reels/Shorts, 1:1, 4:5 feed, 16:9 YouTube) by crop, fit or
  blurred-background reframe, and check the vertical version against the TikTok / Instagram Reels / YouTube Shorts UI
  safe zones. Use when the user wants a video "en vertical", "pour TikTok/Reels/Shorts/Instagram", "en carré", all
  formats, or asks whether text or a logo will be hidden by the app's buttons.
---

# video-formats

Script: `scripts/formats.py` (plain `python3` + ffmpeg).

```bash
F=<skill>/scripts/formats.py
python3 $F all in.mp4 --out versions/ [--mode blur|crop|fit] [--aspects 9:16,1:1,4:5,16:9]
python3 $F reframe in.mp4 out.mp4 --aspect 9:16 --mode crop --x 0.5 --y 0.5
python3 $F safezone out_9x16.mp4 qa.png [--platform tiktok|reels|shorts|all] --t <seconds>
```

## Choosing the mode

- **Best result = re-render natively.** If the video was made by a code-video skill (mg-styles-15, xilo-opus-video,
  lemo-opuscar, huashu-art-motion), re-render it at the target size with the layout recomposed for that aspect
  (bigger type, stacked layout, captions above the bottom UI zone). Use this script only for footage you can't re-render
  or when the user wants the quick version.
- `crop` — when the subject stays near one spot (a talking head, a centred logo). Set `--x/--y` to the subject
  (0..1). Check several frames: anything outside the crop is lost.
- `blur` (default) — nothing is cut; the picture gets smaller on a blurred copy of itself. Safe for wide shots,
  slides, screen recordings.
- `fit` — like blur but on a solid brand colour (`--bg '#hex'`, use the brand kit colour).

## Checks before delivering

1. `safezone` on each vertical version at 2–3 key moments (the hook, the main text, the end card). Text, faces,
   logo and captions must stay out of the tinted areas (approximate; apps change; ads have bigger bottom bars).
2. Captions: burn them **after** reframing, with `arabic-captions build --aspect 9:16` so they sit above the UI.
3. `ffprobe` each output: right size, same duration as the source, audio present.
4. Name outputs `<name>_9x16.mp4`, `<name>_1x1.mp4`… and list them for the user with what each is for.
