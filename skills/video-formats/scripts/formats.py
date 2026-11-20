#!/usr/bin/env python3
"""Platform versions of a video + safe-zone check.

  formats.py reframe in.mp4 out.mp4 --aspect 9:16 [--mode blur|crop|fit] [--x 0.5] [--y 0.5] [--bg '#151433']
  formats.py all in.mp4 --out versions/ [--mode blur] [--aspects 9:16,1:1,4:5,16:9]
  formats.py safezone in.mp4 qa.png [--platform tiktok|reels|shorts|all] [--t 2.0]

modes: blur = whole picture fitted on a blurred, zoomed copy of itself (safe default, nothing cut)
       crop = fill the frame, cut the sides (or top/bottom); --x/--y = focus point 0..1 (0.5 = centre)
       fit  = whole picture on a solid colour (--bg)
Output: H.264 yuv420p, CRF 18, audio copied, same fps as the source.
"""
import argparse, json, pathlib, subprocess, sys

SIZES = {'9:16': (1080, 1920), '1:1': (1080, 1080), '4:5': (1080, 1350), '16:9': (1920, 1080)}
# Approximate UI zones on a 1080x1920 frame (px): top, bottom, right column, left. Vary by app version / ad vs organic.
ZONES = {
    'tiktok': {'top': 140, 'bottom': 480, 'right': 140, 'left': 40},
    'reels':  {'top': 220, 'bottom': 440, 'right': 130, 'left': 40},
    'shorts': {'top': 160, 'bottom': 400, 'right': 140, 'left': 40},
}


def probe(p):
    r = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                                   'stream=width,height,r_frame_rate', '-of', 'json', str(p)],
                                  capture_output=True, text=True).stdout)['streams'][0]
    return r['width'], r['height'], r['r_frame_rate']


def has_audio(p):
    r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=index', '-of', 'csv=p=0',
                        str(p)], capture_output=True, text=True).stdout.strip()
    return bool(r)


def reframe(inp, out, aspect, mode='blur', fx=0.5, fy=0.5, bg='#151433'):
    W, H = SIZES[aspect]
    w, h, _ = probe(inp)
    if mode == 'crop':
        vf = (f"scale={W}:{H}:force_original_aspect_ratio=increase,"
              f"crop={W}:{H}:(iw-{W})*{fx}:(ih-{H})*{fy},setsar=1")
    elif mode == 'fit':
        vf = (f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
              f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color={bg.replace('#', '0x')},setsar=1")
    else:
        vf = (f"split[a][b];[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=28:2,"
              f"eq=brightness=-0.08:saturation=1.1[bg];[b]scale={W}:{H}:force_original_aspect_ratio=decrease[fg];"
              f"[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1")
    cmd = ['ffmpeg', '-v', 'error', '-y', '-i', str(inp), '-filter_complex' if mode == 'blur' else '-vf', vf,
           '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-pix_fmt', 'yuv420p']
    cmd += ['-c:a', 'copy'] if has_audio(inp) else ['-an']
    subprocess.run(cmd + [str(out)], check=True)
    print(f'{out}  {aspect} {W}x{H} ({mode}) from {w}x{h}', file=sys.stderr)


def safezone(inp, out, platform='all', t=2.0):
    w, h, _ = probe(inp)
    sx, sy = w / 1080, h / 1920
    plats = list(ZONES) if platform == 'all' else [platform]
    cols = {'tiktok': 'red', 'reels': 'magenta', 'shorts': 'yellow'}
    draws = []
    for p in plats:
        z = ZONES[p]; c = cols[p]
        draws += [f"drawbox=x=0:y=0:w=iw:h={int(z['top'] * sy)}:color={c}@0.28:t=fill",
                  f"drawbox=x=0:y=ih-{int(z['bottom'] * sy)}:w=iw:h={int(z['bottom'] * sy)}:color={c}@0.28:t=fill",
                  f"drawbox=x=iw-{int(z['right'] * sx)}:y=0:w={int(z['right'] * sx)}:h=ih:color={c}@0.28:t=fill",
                  f"drawbox=x=0:y=0:w={int(z['left'] * sx)}:h=ih:color={c}@0.20:t=fill"]
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(t), '-i', str(inp), '-vf', ','.join(draws), '-frames:v', '1',
                    str(out)], check=True)
    print(f'{out}: tinted = covered by the app UI ({", ".join(plats)}; approximate). Keep text, faces and logos out of it.',
          file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest='cmd', required=True)
    p = sp.add_parser('reframe'); p.add_argument('inp'); p.add_argument('out')
    p.add_argument('--aspect', required=True, choices=list(SIZES)); p.add_argument('--mode', default='blur', choices=['blur', 'crop', 'fit'])
    p.add_argument('--x', type=float, default=0.5); p.add_argument('--y', type=float, default=0.5); p.add_argument('--bg', default='#151433')
    p = sp.add_parser('all'); p.add_argument('inp'); p.add_argument('--out', required=True)
    p.add_argument('--mode', default='blur', choices=['blur', 'crop', 'fit']); p.add_argument('--aspects', default='9:16,1:1,4:5,16:9')
    p.add_argument('--x', type=float, default=0.5); p.add_argument('--y', type=float, default=0.5); p.add_argument('--bg', default='#151433')
    p = sp.add_parser('safezone'); p.add_argument('inp'); p.add_argument('out')
    p.add_argument('--platform', default='all', choices=list(ZONES) + ['all']); p.add_argument('--t', type=float, default=2.0)
    a = ap.parse_args()
    if a.cmd == 'reframe':
        reframe(a.inp, a.out, a.aspect, a.mode, a.x, a.y, a.bg)
    elif a.cmd == 'all':
        out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
        w, h, _ = probe(a.inp); stem = pathlib.Path(a.inp).stem
        for asp in a.aspects.split(','):
            W, H = SIZES[asp]
            if abs(W / H - w / h) < 0.01:
                print(f'skip {asp}: source is already {w}x{h}', file=sys.stderr); continue
            reframe(a.inp, out / f"{stem}_{asp.replace(':', 'x')}.mp4", asp, a.mode, a.x, a.y, a.bg)
    else:
        safezone(a.inp, a.out, a.platform, a.t)


if __name__ == '__main__':
    main()
