---
name: video-studio
description: >-
  Entry point for ANY video request (promo, ad, explainer, motion design, social short, reel, animation, edit of
  existing footage, subtitles, vertical versions, voice-over, music): picks the right skill or connector, applies the
  owner's brand kit and defaults, and runs the delivery checklist. Use first whenever the user asks for a video,
  vidéo, فيديو, promo, pub, reel, TikTok, short, animation or montage, before choosing a style library.
---

# video-studio — routing, brand, delivery

## 1. Read the brand kit first

`<skill>/brand/brand.json` (+ logo files next to it). Use its colours, fonts, voice, music mood, end card and
languages unless the user says otherwise for this video. Fields still `TODO` are unknown: ask about them only if
this video needs them (one round of questions, max 3), never invent them. If the user gives new brand facts, offer
to save them into `brand.json` (it lives in the repo `bounabmohamedsalah-collab/mg-styles-15-skill`, folder
`skills/video-studio/brand/`; commit + push so it persists).

## 2. Route

| The user wants… | Use | Notes |
|---|---|---|
| Short promo / ad / logo animation, clear brief | **mg-styles-15** (15 MG styles; flat vector = safest) | 10–20 s, code-made, Arabic text OK |
| A film in a specific art look (watercolour, ukiyo-e, oil, papercut…) or 99-style choice | **lemo-opuscar** | needs ffmpeg 7 (installed) |
| Direction unclear → show 3 options with previews first | **xilo-opus-video** | writes a reusable brief.md |
| Explainer driven by a voice-over / narration, painterly styles (Van Gogh, Kurzgesagt-like…) | **huashu-art-motion** | voice: brand voice via ElevenLabs, or user recording |
| Realistic people, products, places (filmed look) | Creative Claw `generate_video` / Halai | **paid credits: quote and get approval first** |
| UGC-style ad with a creator | `creative-claw:creativeclaw-create-ugc-ad` | paid |
| Talking avatar / lip-sync | Creative Claw (`lip_sync_video`, avatars) | paid; consent for real people |
| Edit existing footage (cut, trim, reorder, clean audio) | `creative-claw:creativeclaw-edit-media` or Descript | |
| Long video → several shorts | `creative-claw:creativeclaw-create-reels` | |
| Subtitles / transcription (Arabic, darija, FR, EN) | **arabic-captions** | always last step |
| Vertical / square / 4:5 versions, safe zones | **video-formats** | prefer native re-render for code-made videos |
| Voice-over | ElevenLabs (brand `voice_id`) or the user's own recording | paid; Arabic dialect quality varies: use the validated voice |
| Music | the code-synth music inside the style skills (free), or Creative Claw music (paid) | |
| Publish / schedule | Upload-Post | needs the owner to authorise the connector first |

Combine when needed, in this order: picture → voice → music/SFX mix → captions → platform versions → QA.

## 3. Defaults (when neither the user nor the brand kit says otherwise)

16:9 1920×1080, 30 fps, 15 s for a promo / 30–60 s for an explainer; audio −14 LUFS, true peak ≤ −1 dBTP;
social versions 9:16 (+ 1:1) with burned captions; on-screen Arabic in the brand's language variant, `dir="rtl"`,
Arabic fonts from `~/.local/share/fonts/arabic`. Facts, prices, claims only from the user's material.

## 4. Money and consent

- Anything that spends credits (Creative Claw, Halai, ElevenLabs): estimate first, say the cost, wait for a yes.
  Never retry a paid generation automatically.
- Never clone or imitate a real person's voice or face without their explicit consent.

## 5. Delivery checklist

1. Output folder `/home/user/videos/<slug>/`: `final.mp4`, `final_9x16.mp4`… , `captions.srt` if any, `source/`.
2. `ffprobe`: duration, size, fps, audio present; loudness check (`ffmpeg -i f.mp4 -af ebur128=peak=true -f null -`).
3. Contact sheet of the final (one frame every 0.5–1 s) and look at it: no clipped text, no tofu/fallback fonts,
   Arabic reads right-to-left, nothing under the vertical-format UI.
4. Send the MP4 to the user (SendUserFile) + a short report: concept, beat sheet, checks, honest top-3 weaknesses.
