#!/bin/sh
# Installs the mg-styles-15 library (github.com/Vincentwei1021/mg-styles-15, MIT) into ~/mg-styles-15,
# its Node + Python audio packages, the OFL fonts it needs (from google/fonts), and the wrapper skill
# into ~/.claude/skills/mg-styles-15. Idempotent; each step is non-fatal.
H=${HOME:-/root}; LIB=$H/mg-styles-15; HERE=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$H/.claude/skills/mg-styles-15" && cp "$HERE/skill/SKILL.md" "$H/.claude/skills/mg-styles-15/"

if [ ! -d "$LIB/.git" ]; then
  git clone -q --depth 1 --filter=blob:none --sparse https://github.com/Vincentwei1021/mg-styles-15 "$LIB" || exit 0
  git -C "$LIB" sparse-checkout set --no-cone '/*' '!/videos/' '!/docs/' '!/site/'
fi
cd "$LIB" || exit 0
[ -d node_modules ] || npm install --no-audit --no-fund --loglevel=error || true
[ -x .venv/bin/python ] || python3 -m venv .venv
.venv/bin/pip install -q --disable-pip-version-check numpy==2.4.6 scipy==1.16.3 soundfile==0.14.0 numba==0.66.0 \
  pedalboard==0.9.25 pyloudnorm==0.2.0 matplotlib librosa==0.11.0 pillow==12.3.0 fonttools==4.53.1 || true

# Fonts: target path (relative to LIB) <- google/fonts path
MAP="assets/fonts/latin/anton/Anton-Regular.ttf ofl/anton/Anton-Regular.ttf
assets/fonts/latin/archivo/Archivo-Italic-VF.ttf ofl/archivo/Archivo-Italic[wdth,wght].ttf
assets/fonts/latin/bebasneue/BebasNeue-Regular.ttf ofl/bebasneue/BebasNeue-Regular.ttf
assets/fonts/latin/caveat/Caveat-VF.ttf ofl/caveat/Caveat[wght].ttf
assets/fonts/latin/chakrapetch/ChakraPetch-SemiBold.ttf ofl/chakrapetch/ChakraPetch-SemiBold.ttf
assets/fonts/latin/cormorantgaramond/CormorantGaramond-VF.ttf ofl/cormorantgaramond/CormorantGaramond[wght].ttf
assets/fonts/latin/dmsans/DMSans-VF.ttf ofl/dmsans/DMSans[opsz,wght].ttf
assets/fonts/latin/fredoka/Fredoka-VF.ttf ofl/fredoka/Fredoka[wdth,wght].ttf
assets/fonts/latin/ibmplexmono/IBMPlexMono-Medium.ttf ofl/ibmplexmono/IBMPlexMono-Medium.ttf
assets/fonts/latin/ibmplexmono/IBMPlexMono-SemiBold.ttf ofl/ibmplexmono/IBMPlexMono-SemiBold.ttf
assets/fonts/latin/instrumentserif/InstrumentSerif-Italic.ttf ofl/instrumentserif/InstrumentSerif-Italic.ttf
assets/fonts/latin/instrumentserif/InstrumentSerif-Regular.ttf ofl/instrumentserif/InstrumentSerif-Regular.ttf
assets/fonts/latin/inter/Inter-VF.ttf ofl/inter/Inter[opsz,wght].ttf
assets/fonts/latin/jetbrainsmono/JetBrainsMono-VF.ttf ofl/jetbrainsmono/JetBrainsMono[wght].ttf
assets/fonts/latin/luckiestguy/LuckiestGuy-Regular.ttf apache/luckiestguy/LuckiestGuy-Regular.ttf
assets/fonts/latin/michroma/Michroma-Regular.ttf ofl/michroma/Michroma-Regular.ttf
assets/fonts/latin/poppins/Poppins-Black.ttf ofl/poppins/Poppins-Black.ttf
assets/fonts/latin/poppins/Poppins-SemiBold.ttf ofl/poppins/Poppins-SemiBold.ttf
assets/fonts/latin/pressstart2p/PressStart2P-Regular.ttf ofl/pressstart2p/PressStart2P-Regular.ttf
assets/fonts/latin/rajdhani/Rajdhani-Bold.ttf ofl/rajdhani/Rajdhani-Bold.ttf
assets/fonts/latin/rajdhani/Rajdhani-SemiBold.ttf ofl/rajdhani/Rajdhani-SemiBold.ttf
assets/fonts/latin/sora/Sora-VF.ttf ofl/sora/Sora[wght].ttf
assets/fonts/latin/unbounded/Unbounded-VF.ttf ofl/unbounded/Unbounded[wght].ttf
assets/fonts/latin/vt323/VT323-Regular.ttf ofl/vt323/VT323-Regular.ttf
assets/fonts/cjk/longcang/LongCang-Regular.ttf ofl/longcang/LongCang-Regular.ttf
assets/fonts/cjk/zcoolkuaile/ZCOOLKuaiLe-Regular.ttf ofl/zcoolkuaile/ZCOOLKuaiLe-Regular.ttf
assets/fonts/cjk/notosanssc/NotoSansSC-VF.ttf ofl/notosanssc/NotoSansSC[wght].ttf
assets/fonts/cjk/notoserifsc/NotoSerifSC-VF.ttf ofl/notoserifsc/NotoSerifSC[wght].ttf
assets/fonts/cjk/lxgwmarkergothic/LXGWMarkerGothic-Regular.ttf ofl/lxgwmarkergothic/LXGWMarkerGothic-Regular.ttf
demos/10-synthwave/assets/fonts/MrDafoe-Regular.ttf ofl/mrdafoe/MrDafoe-Regular.ttf"
if [ ! -f demos/08-morph/assets/fonts/Outfit-SemiBold.ttf ]; then
  GF=$(mktemp -d)
  if git clone -q --depth 1 --filter=blob:none --sparse https://github.com/google/fonts "$GF/gf"; then
    git -C "$GF/gf" sparse-checkout set --no-cone $(echo "$MAP" | awk '{s=$2; gsub(/\[/,"[[]",s); print "/" s}') \
      '/ofl/fraunces/Fraunces[[]SOFT,WONK,opsz,wght].ttf' '/ofl/outfit/Outfit[[]wght].ttf'
    echo "$MAP" | while read dst src; do mkdir -p "$(dirname "$dst")"; cp "$GF/gf/$src" "$dst" || true; done
    I=".venv/bin/python -m fontTools.varLib.instancer -q"
    mkdir -p demos/03-isometric/assets/fonts demos/07-liquid/assets demos/08-morph/assets/fonts
    $I "$GF/gf/ofl/unbounded/Unbounded[wght].ttf" wght=800 -o demos/03-isometric/assets/fonts/Unbounded-800-static.ttf
    $I "$GF/gf/ofl/fraunces/Fraunces[SOFT,WONK,opsz,wght].ttf" opsz=72 wght=900 SOFT=100 WONK=0 \
      -o demos/07-liquid/assets/Fraunces-Liquid-72-900-Soft.ttf
    $I "$GF/gf/ofl/outfit/Outfit[wght].ttf" wght=600 -o demos/08-morph/assets/fonts/Outfit-SemiBold.ttf
  fi
  rm -rf "$GF"
fi
sh "$HERE/arabic-fonts.sh" || true   # OFL Arabic fonts for all skills
echo "mg-styles-15 ready: $LIB"
