#!/usr/bin/env python3
"""Arabic-first captions: transcribe (faster-whisper, local), fix with a script, cut into readable lines,
write SRT + ASS (word-by-word highlight, RTL-safe) and burn into a video.

  captions.py transcribe in.mp4 --out caps/            [--lang ar|fr|en|auto] [--script text.txt] [--model large-v3-turbo]
  captions.py build caps/words.json --out caps/        [--aspect 16:9|9:16|1:1] [--font Cairo] [--style box|outline|pop]
                                                       [--max-words 6] [--max-chars 38] [--highlight '#FFC62B']
  captions.py burn in.mp4 caps/captions.ass out.mp4
  captions.py all in.mp4 out.mp4 --out caps/ [same options as above]   # transcribe + build + burn

words.json = [{"w": "مرحبا", "s": 0.42, "e": 0.88}, ...]   (editable by hand; rerun `build` after editing)
Needs: ~/video-tools/.venv (faster-whisper), model cache ~/video-tools/models, ffmpeg with libass, fonts in
~/.local/share/fonts/arabic (Cairo, Tajawal, ...).
"""
import argparse, difflib, json, os, pathlib, re, subprocess, sys

HOME = pathlib.Path(os.environ.get('HOME', '/root'))
MODELS = HOME / 'video-tools' / 'models'
FONTS = HOME / '.local' / 'share' / 'fonts' / 'arabic'
ARABIC = re.compile(r'[؀-ۿݐ-ݿࢠ-ࣿ]')
PUNCT_END = re.compile(r'[.!?؟…،,:;]$')


# ---------------------------------------------------------------- transcribe
def transcribe(media, lang='ar', model='large-v3-turbo', prompt=None):
    from faster_whisper import WhisperModel
    m = WhisperModel(model, device='cpu', compute_type='int8', download_root=str(MODELS))
    segs, info = m.transcribe(str(media), language=None if lang == 'auto' else lang, word_timestamps=True,
                              vad_filter=True, beam_size=5, initial_prompt=prompt)
    words = []
    for seg in segs:
        for w in seg.words or []:
            t = w.word.strip()
            if t:
                words.append({'w': t, 's': round(w.start, 3), 'e': round(w.end, 3)})
    print(f'language: {info.language} ({info.language_probability:.2f}), {len(words)} words, {info.duration:.1f}s',
          file=sys.stderr)
    return words


def norm(t):
    t = re.sub(r'[ً-ْـ]', '', t)            # harakat + tatweel
    t = re.sub('[إأآا]', 'ا', t).replace('ى', 'ي').replace('ة', 'ه')
    return re.sub(r'[^\w]', '', t).lower()


def apply_script(words, script):
    """Keep whisper's timings, take the spelling from the script (word-level alignment)."""
    target = script.split()
    a, b = [norm(w['w']) for w in words], [norm(w) for w in target]
    out, fixes = [], []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op == 'equal':
            for i, j in zip(range(i1, i2), range(j1, j2)):
                out.append({**words[i], 'w': target[j]})
        elif op in ('replace', 'insert'):
            s = words[i1]['s'] if i1 < len(words) else (out[-1]['e'] if out else 0.0)
            e = words[i2 - 1]['e'] if i2 > i1 else (words[i1]['s'] if i1 < len(words) else s + 0.3)
            n = j2 - j1
            for k, j in enumerate(range(j1, j2)):          # spread the script words over the span
                out.append({'w': target[j], 's': round(s + (e - s) * k / n, 3), 'e': round(s + (e - s) * (k + 1) / n, 3)})
            fixes.append(f"{s:6.2f}s  {' '.join(w['w'] for w in words[i1:i2]) or '(rien)'}  ->  {' '.join(target[j1:j2])}")
        # 'delete': whisper heard words not in the script -> dropped
        elif op == 'delete':
            fixes.append(f"{words[i1]['s']:6.2f}s  {' '.join(w['w'] for w in words[i1:i2])}  ->  (supprimé)")
    return out, fixes


# ---------------------------------------------------------------- lines
def make_lines(words, max_words=6, max_chars=38, max_dur=3.2, gap=0.45):
    lines, cur = [], []
    for i, w in enumerate(words):
        if cur:
            text = ' '.join(x['w'] for x in cur + [w])
            pause = w['s'] - cur[-1]['e']
            if (len(cur) >= max_words or len(text) > max_chars or w['e'] - cur[0]['s'] > max_dur or pause > gap
                    or PUNCT_END.search(cur[-1]['w'])):
                lines.append(cur); cur = []
        cur.append(w)
    if cur:
        lines.append(cur)
    # avoid a lonely last word: pull one word from the previous line
    for k in range(1, len(lines)):
        if len(lines[k]) == 1 and len(lines[k - 1]) > 2 and not PUNCT_END.search(lines[k - 1][-1]['w']):
            lines[k].insert(0, lines[k - 1].pop())
    return lines


def ts_srt(t):
    h, r = divmod(max(0, t), 3600); m, s = divmod(r, 60)
    return f'{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s % 1) * 1000)):03d}'.replace(',1000', ',999')


def ts_ass(t):
    h, r = divmod(max(0, t), 3600); m, s = divmod(r, 60)
    return f'{int(h)}:{int(m):02d}:{s:05.2f}'


def ass_color(hexcol, alpha=0):
    h = hexcol.lstrip('#'); r, g, b = h[0:2], h[2:4], h[4:6]
    return f'&H{alpha:02X}{b}{g}{r}'.upper()


def write_srt(lines, path):
    with open(path, 'w', encoding='utf-8') as f:
        for k, ln in enumerate(lines, 1):
            text = ' '.join(w['w'] for w in ln)
            if ARABIC.search(text):
                text = '‫' + text + '‬'          # RLE ... PDF: players keep punctuation on the right side
            f.write(f"{k}\n{ts_srt(ln[0]['s'])} --> {ts_srt(ln[-1]['e'] + 0.15)}\n{text}\n\n")


ASPECT = {'16:9': (1920, 1080), '9:16': (1080, 1920), '1:1': (1080, 1080), '4:5': (1080, 1350)}


def write_ass(lines, path, aspect='16:9', font='Cairo', style='box', highlight='#FFC62B', color='#FFFFFF',
              box='#151433'):
    W, H = ASPECT[aspect]
    size = round(H * (0.06 if aspect == '16:9' else 0.044 if aspect == '9:16' else 0.055))
    # vertical position: 9:16 keeps clear of the TikTok/Reels caption + buttons zone (bottom ~22 %)
    margin_v = round(H * (0.08 if aspect == '16:9' else 0.26 if aspect == '9:16' else 0.12))
    if style == 'box':
        border, outline, shadow, back = 3, round(size * 0.28), 0, ass_color(box)   # opaque box (no seams between runs)
        out_col = ass_color(box)
    else:
        border, outline, shadow, back = 1, round(size * 0.09), round(size * 0.04), ass_color('#000000', 0x80)
        out_col = ass_color(box)
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes
; Encoding -1 on the style = libass auto base direction: without it Arabic words come out in reverse order

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{font},{size},{ass_color(color)},{ass_color(highlight)},{out_col},{back},-1,0,0,0,100,100,0,0,{border},{outline},{shadow},2,{round(W*0.06)},{round(W*0.06)},{margin_v},-1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    hl = ass_color(highlight)
    ev = []
    for ln in lines:
        end_line = ln[-1]['e'] + 0.15
        for i, w in enumerate(ln):
            s = ln[0]['s'] if i == 0 else w['s']
            e = ln[i + 1]['s'] if i + 1 < len(ln) else end_line
            parts = []
            for j, x in enumerate(ln):
                t = x['w'].replace('{', '(').replace('}', ')')
                if j == i:
                    pop = r'\t(0,80,\fscx112\fscy112)\t(80,180,\fscx100\fscy100)' if style == 'pop' else ''
                    parts.append(f'{{\\c{hl}{pop}}}{t}{{\\r}}')
                else:
                    parts.append(t)
            fade = r'{\fad(90,0)}' if i == 0 else ''
            ev.append(f"Dialogue: 0,{ts_ass(s)},{ts_ass(e)},Cap,,0,0,0,,{fade}{' '.join(parts)}")
    pathlib.Path(path).write_text(head + '\n'.join(ev) + '\n', encoding='utf-8')
    return W, H


def burn(video, ass, out):
    fd = str(FONTS) if FONTS.exists() else ''
    esc = lambda p: str(p).replace('\\', '\\\\').replace(':', '\\:').replace("'", "\\'")
    vf = f"ass='{esc(pathlib.Path(ass).resolve())}'" + (f":fontsdir='{esc(fd)}'" if fd else '')
    cmd = ['ffmpeg', '-v', 'error', '-y', '-i', str(video), '-vf', vf, '-c:v', 'libx264', '-crf', '17', '-preset', 'medium',
           '-c:a', 'copy', str(out)]
    subprocess.run(cmd, check=True)
    print(f'burned -> {out}', file=sys.stderr)


# ---------------------------------------------------------------- cli
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest='cmd', required=True)

    def build_opts(p):
        p.add_argument('--aspect', default=None, choices=list(ASPECT)); p.add_argument('--font', default='Cairo')
        p.add_argument('--style', default='box', choices=['box', 'outline', 'pop'])
        p.add_argument('--max-words', type=int, default=6); p.add_argument('--max-chars', type=int, default=38)
        p.add_argument('--highlight', default='#FFC62B'); p.add_argument('--color', default='#FFFFFF')
        p.add_argument('--box', default='#151433')

    p = sp.add_parser('transcribe'); p.add_argument('media'); p.add_argument('--out', required=True)
    p.add_argument('--lang', default='ar'); p.add_argument('--script'); p.add_argument('--model', default='large-v3-turbo')
    p = sp.add_parser('build'); p.add_argument('words'); p.add_argument('--out', required=True); build_opts(p)
    p = sp.add_parser('burn'); p.add_argument('video'); p.add_argument('ass'); p.add_argument('out')
    p = sp.add_parser('all'); p.add_argument('media'); p.add_argument('outvideo'); p.add_argument('--out', required=True)
    p.add_argument('--lang', default='ar'); p.add_argument('--script'); p.add_argument('--model', default='large-v3-turbo')
    build_opts(p)
    a = ap.parse_args()

    def do_transcribe(media, out):
        out.mkdir(parents=True, exist_ok=True)
        script = pathlib.Path(a.script).read_text(encoding='utf-8') if a.script else None
        words = transcribe(media, a.lang, a.model, prompt=script[:200] if script else None)
        (out / 'whisper_raw.json').write_text(json.dumps(words, ensure_ascii=False, indent=0), encoding='utf-8')
        if script:
            words, fixes = apply_script(words, script)
            if fixes:
                print('corrections (whisper -> script):', *fixes, sep='\n  ', file=sys.stderr)
        (out / 'words.json').write_text(json.dumps(words, ensure_ascii=False, indent=0), encoding='utf-8')
        return words

    def guess_aspect(media):
        try:
            r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height',
                                '-of', 'csv=p=0', str(media)], capture_output=True, text=True).stdout.strip()
            w, h = map(int, r.split(','))
            return min(ASPECT, key=lambda k: abs(ASPECT[k][0] / ASPECT[k][1] - w / h))
        except Exception:
            return '16:9'

    def do_build(words, out, aspect):
        lines = make_lines(words, a.max_words, a.max_chars)
        write_srt(lines, out / 'captions.srt')
        write_ass(lines, out / 'captions.ass', aspect, a.font, a.style, a.highlight, a.color, a.box)
        print(f'{len(lines)} lines -> {out}/captions.srt, captions.ass ({aspect})', file=sys.stderr)
        for ln in lines:
            print(f"  {ln[0]['s']:6.2f}–{ln[-1]['e']:6.2f}  {' '.join(w['w'] for w in ln)}", file=sys.stderr)

    if a.cmd == 'transcribe':
        do_transcribe(a.media, pathlib.Path(a.out))
    elif a.cmd == 'build':
        out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
        do_build(json.loads(pathlib.Path(a.words).read_text(encoding='utf-8')), out, a.aspect or '16:9')
    elif a.cmd == 'burn':
        burn(a.video, a.ass, a.out)
    else:
        out = pathlib.Path(a.out)
        words = do_transcribe(a.media, out)
        do_build(words, out, a.aspect or guess_aspect(a.media))
        burn(a.media, out / 'captions.ass', a.outvideo)


if __name__ == '__main__':
    main()
