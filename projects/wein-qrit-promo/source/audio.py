# وين قريت — Wine Krite promo soundtrack: mgaudio pop recipe (120 BPM, F major) + SFX locked to cues.json
import sys, json, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib', 'audio'))
import mgaudio as mg
from mgaudio import recipes, sfx, synth, samples, fm, drums, seq

HERE = os.path.dirname(os.path.abspath(__file__))
cues = json.load(open(os.path.join(HERE, 'cues.json')))
C = cues['t']; F = lambda n: n / 30.0

m = recipes.pop(bpm=cues['bpm'], key=cues['key'], build=cues['build'], drop=cues['drop'], outro=cues['outro'])
f = m.form
note = lambda t, i=-1, sh=12: f.chord_at(t, sh)[i]
try:
    MAR = samples.inst('marimba'); mar = lambda n, d=0.6, v=0.9: MAR.play(n, dur=d, vel=v)
except Exception:
    mar = lambda n, d=0.6, v=0.9: fm.mallet(n, d, v, 'marimba')

mot = m.track('motif', level=-18, sends={'plate': -12, 'delay': -18}, group='music')
gl = m.track('gliss', level=-23, sends={'room': -12}, group='music')
sub = m.track('sub808', level=-19, group='music')

# act 1: the pin drops, the school builds (one marimba gliss up the facade)
m.sfx(sfx.whoosh(0.5, 'swish', direction=1, peak=0.6), at=0.05, gain=-12)
m.sfx(sfx.pop('mouth', pitch=0.8), at=C['pinLand'] - F(1), gain=0)
m.sfx(sfx.impact('soft'), at=C['pinLand'], gain=-9)
m.sfx(sfx.pop('bubble', pitch=1.1), at=C['pinLand'] + 0.22, gain=-9)
m.sfx(sfx.pop('soft', pitch=0.9), at=C['school'], gain=-6)
m.sfx(sfx.pop('cork', pitch=1.0), at=C['roof'], gain=-6)
for k, n in enumerate(['F4', 'A4', 'C5', 'F5', 'A5', 'C6']):
    gl.add(mar(n, 0.3, 0.55 + 0.07 * k), C['win'] + k * F(2))
m.sfx(sfx.ding('C7'), at=C['clock'], gain=-16)
m.sfx(sfx.swish(0.25), at=C['flag'], gain=-12)
m.sfx(sfx.pop('bubble', pitch=0.9), at=C['tree1'], gain=-10, pan=-0.4)
m.sfx(sfx.pop('bubble', pitch=1.0), at=C['tree2'], gain=-10, pan=0.4)
m.sfx(sfx.blip('A6'), at=C['blink1'], gain=-18)
# the question: 3-note "wine qrit?" motif, rising
for k, n in enumerate(['F5', 'A5', 'D6']): mot.add(mar(n, 0.45, 0.9), C['bubble'] + k * F(3))
m.sfx(sfx.pop('mouth', pitch=1.3), at=C['bubble'], gain=-4, pan=0.3)
# wipe into the phone
m.sfx(sfx.whoosh(0.5, 'swoosh', direction=1, peak=0.7), at=C['wipe1'] - 0.15, gain=-8)
m.sfx(sfx.pop('bubble', pitch=0.75), at=C['wipe1'] + 0.1, gain=-3)
m.sfx(sfx.whoosh(0.4, 'air', direction=1, peak=0.8), at=C['phone'], gain=-10)
m.sfx(sfx.impact('thud'), at=C['phone'] + 0.42, gain=-10)
m.sfx(sfx.ui('confirm'), at=C['field'], gain=-12)
m.sfx(sfx.typing(12, rate=1 / C['typeStep'], kind='keyboard'), at=C['type'], gain=-11)
for i in range(4):
    m.sfx(sfx.pop('soft', pitch=1.0 + 0.08 * i), at=C['row'] + i * C['rowStep'], gain=-9, pan=0.15)
for i, n in enumerate(['F5', 'A5', 'C6', 'F6']):
    m.sfx(sfx.toggle(True), at=C['check'] + i * C['checkStep'], gain=-9)
    mot.add(mar(n, 0.4, 0.85), C['check'] + i * C['checkStep'])
# build: riser + snare roll into the drop
m.track('riser2', level=-24, group='music').add(sfx.riser(1.3, 'noise', intensity=1.0), C['drop'] - 1.3)
rl = m.track('roll', level=-24, sends={'plate': -16}, group='music')
rl.hits(lambda v: drums.snare('tight', v), seq.roll(5.0, C['drop'] - F(2), 8, 32, m.grid, 0.3, 1.0))
# drop: avatars burst out, network draws, caps fly
m.sfx(sfx.impact('punch'), at=C['drop'], gain=-3)
m.sfx(sfx.whoosh(0.4, 'swish', direction=1, peak=0.5), at=C['drop'], gain=-8)
sub.add(synth.b808('F1', 0.9, 1.0), C['drop'])
for i in range(9): m.sfx(sfx.tick('clock'), at=C['lines'] + i * 0.045, gain=-16, pan=(i % 3 - 1) * 0.4)
m.sfx(sfx.pop('mouth', pitch=0.85), at=C['capAntic'], gain=-8)
m.sfx(sfx.impact('punch'), at=C['caps'], gain=-4)
m.sfx(sfx.sparkle(0.9, key=cues['key']), at=C['caps'], gain=-9, verb=-10)
sub.add(synth.b808('A1', 0.6, 0.95), C['caps'])
for k, n in enumerate(['C6', 'F6', 'A6']): mot.add(mar(n, 0.5, 0.9), C['caps'] + k * F(2))
# converge + lockup
m.sfx(sfx.whoosh(0.5, 'swish', direction=-1, peak=0.8), at=C['converge'], gain=-8)
m.sfx(sfx.pop('bubble', pitch=0.72), at=C['logoPin'], gain=-2)
m.sfx(sfx.impact('punch'), at=C['capLand'], gain=-4)
sub.add(synth.b808('F1', 1.4, 1.0), C['capLand'])
mot.add(mar('F6', 1.4, 1.0), C['capLand'])
m.sfx(sfx.shimmer_hit(note(C['capLand'], -1, 12)), at=C['capLand'], gain=-7, verb=-10)
m.sfx(sfx.swish(0.3), at=C['word'], gain=-10)
m.sfx(sfx.pop('soft', pitch=1.2), at=C['slogan'], gain=-10)
m.sfx(sfx.sparkle(0.5, key=cues['key']), at=C['latin'], gain=-15, verb=-10)
m.sfx(sfx.blip('E7'), at=C['blink2'], gain=-20)
if 'kick' in m.tracks:
    for k in ('pad', 'arp', 'chords', 'lead'):
        if k in m.tracks: m[k].duck(by='kick', depth=6, release=0.18)
# pre-hit suck on the big hits
HITS = [C['wipe1'] + 0.1, C['drop'], C['caps'], C['capLand']]
pts = [(0.0, 0.0)]
for h in HITS: pts += [(h - 0.095, 0.0), (h - 0.055, -9.0), (h - 0.006, -9.0), (h, 0.0)]
m.group('music').automate('gain', pts + [(10.0, 0.0)])
os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
res = m.export(os.path.join(HERE, 'out/audio.wav'), lufs=-14, tp=-1.5, spectrogram=os.path.join(HERE, 'out/audio_spec.png'))
print({k: res[k] for k in ('duration', 'lufs', 'true_peak', 'warnings') if k in res})
