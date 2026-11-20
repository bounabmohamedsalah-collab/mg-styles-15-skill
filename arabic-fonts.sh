#!/bin/sh
# Installs OFL Arabic fonts from google/fonts into ~/.local/share/fonts/arabic (seen by Chromium via fontconfig).
D=${HOME:-/root}/.local/share/fonts/arabic
[ -f "$D/.done" ] && exit 0
FAMS="cairo tajawal almarai ibmplexsansarabic readexpro notosansarabic amiri notonaskharabic scheherazadenew reemkufi lalezar notokufiarabic changa lemonada"
G=$(mktemp -d)
if git clone -q --depth 1 --filter=blob:none --sparse https://github.com/google/fonts "$G/gf"; then
  git -C "$G/gf" sparse-checkout set --no-cone $(for f in $FAMS; do echo "/ofl/$f/*.ttf /ofl/$f/OFL.txt"; done)
  mkdir -p "$D"
  for f in $FAMS; do [ -d "$G/gf/ofl/$f" ] && mkdir -p "$D/$f" && cp "$G/gf/ofl/$f/"*.ttf "$G/gf/ofl/$f/OFL.txt" "$D/$f/" 2>/dev/null; done
  command -v fc-cache >/dev/null && fc-cache -f "$D" >/dev/null 2>&1
  touch "$D/.done"
fi
rm -rf "$G"
