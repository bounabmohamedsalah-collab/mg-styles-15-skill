---
name: arabic-captions
description: >-
  Transcribe speech (Arabic first: MSA and Maghrebi darija; also French/English) locally with faster-whisper, fix the
  text from a script, cut it into readable caption lines and produce SRT + ASS subtitles with word-by-word highlight
  that render right-to-left correctly, then burn them into a video (16:9, 9:16 with social safe zones, 1:1).
  Use for: subtitles / captions / sous-titres / ترجمة / تفريغ on any video or voice-over, transcribing Arabic audio,
  word-timed captions for TikTok/Reels/Shorts, or adding captions to a video made by another video skill.
---

# arabic-captions

Script: `scripts/captions.py` (run with `~/video-tools/.venv/bin/python`). Model: whisper `large-v3-turbo`
(int8, CPU, cached in `~/video-tools/models`; ~1.2× real time on this machine). Fonts: Arabic families in
`~/.local/share/fonts/arabic` (Cairo default; Tajawal, Almarai, Readex Pro, Lalezar… also work via `--font`).

## Workflow

1. **Transcribe** (one call does everything; or run the steps separately to review in between):
   ```bash
   P=~/video-tools/.venv/bin/python; C=<skill>/scripts/captions.py
   $P $C transcribe in.mp4 --out caps/ [--lang ar|fr|en|auto] [--script script.txt]
   ```
   - Always ask for the script / text if the user has one: with `--script` whisper's timings are kept and the
     spelling is taken from the script (darija spelling, brand names). The corrections are printed: show them.
   - Without a script, whisper writes darija in an MSA-leaning spelling: show the lines to the user and fix
     `caps/words.json` by hand (same structure, keep the times) before building.
2. **Build** the caption files: `$P $C build caps/words.json --out caps/ --aspect 9:16 --style box|outline|pop`
   (`--highlight`, `--color`, `--box` take hex colours: use the brand kit colours when one exists; `--max-words 6`,
   `--max-chars 38` control line length — shorter for 9:16). Prints every line with times: check them.
3. **Burn**: `$P $C burn in.mp4 caps/captions.ass out.mp4` — or `all in.mp4 out.mp4 --out caps/ …` for 1–3 in one go.
4. **Check**: extract 3–4 frames (`ffmpeg -i out.mp4 -vf "select='eq(n,90)+eq(n,300)',scale=960:-1,tile=2x1" -frames:v 1 -fps_mode vfr qa.png`)
   and look: word order right-to-left, punctuation at the left end, highlight on the spoken word, nothing under the
   platform UI (9:16 captions sit at ~74 % height on purpose).
5. Deliver the burned MP4 **and** `captions.srt` (for YouTube / CapCut / platforms that take a subtitle file).

## Rules that matter

- The ASS style must keep `Encoding = -1` (libass auto base direction). With any other value libass lays Arabic
  words out left-to-right (reversed sentence). The script already does it; keep it if you edit the ASS by hand.
- One line at a time, ≤ 6 words, ≤ ~3 s; break at punctuation and pauses; never leave a single word alone.
- Text must match the audio. Never "improve" what was said; fix only spelling.
- Captions on a video made with a code-video skill: render the video first (without baked text where captions
  go), then burn captions as the last step so they can be redone without re-rendering.
- Long media (> 10 min): transcription takes about as long as the media; tell the user before starting.
