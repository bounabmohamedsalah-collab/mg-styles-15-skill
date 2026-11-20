# Wein Qrit — promo 10 s (flat vector)

Première promo de l'appli **وين قريت** (slogan « رجّع صحاب القراية »), faite le 2026-11-20 avec le skill
`mg-styles-15` (style 01 flat vector). Image et son entièrement en code ; 1920×1080, 30 i/s, 10,00 s, −14 LUFS.

- `source/index.html` — l'animation (Canvas, `window.renderAt(t)`), 4 scènes : épingle + école → téléphone et
  recherche « ثانوية الأمل » → réseau d'avatars et lancer de toques → logo, nom et slogan.
- `source/cues.json` — la feuille de repères (temps de chaque événement), lue par l'image et par le son.
- `source/audio.py` — la musique (pop 120 BPM) et les bruitages, calés sur `cues.json`.
- `planche.png` — une image toutes les 0,5 s du film.
- `voix/` — test des deux voix ElevenLabs en darija (même texte), avec leurs sous-titres SRT.
  Voix « Wein Qrit féminine » `X5SHq2UrmBNK6xkG57U6`, « Ayyoub » `JvNKdNXWUbl2cNBNljB9`, modèle `eleven_v4`.

## Refaire le rendu

Les pages sont servies depuis la bibliothèque mg-styles-15 (installée par `install.sh` dans `~/mg-styles-15`) :

```bash
mkdir -p ~/mg-styles-15/demos/user-wine-krite && cp source/* ~/mg-styles-15/demos/user-wine-krite/
cd ~/mg-styles-15 && .venv/bin/python demos/user-wine-krite/audio.py
export MG_CHROME=$(ls /opt/pw-browsers/chromium-*/chrome-linux64/chrome | head -1) MG_GPU_ARGS="--no-sandbox --enable-unsafe-swiftshader"
node harness/render.mjs demos/user-wine-krite --mb 4          # -> demos/user-wine-krite/out/video.mp4
```

Pour modifier un texte, une couleur ou un timing : `index.html` (textes et dessin) et `cues.json` (temps), puis
relancer `audio.py` si les temps ont changé. Versions verticales : skill `video-formats` (ou nouveau rendu en
1080×1920 en adaptant la mise en page) ; sous-titres : skill `arabic-captions`.
