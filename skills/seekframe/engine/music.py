"""Score one video from its cue sheet: python music.py <cues.json> <out.wav>.

The cue sheet comes from the page (window.CUES): scene cuts, transition types, planned chapters
and every on-screen event (sfx). Styles: drive, tech, calm. Loudness ends at -16 LUFS, measured.
"""
import json
import os
import sys
import wave
from pathlib import Path

import numpy as np

RUNTIME = Path(os.environ.get('SEEKFRAME_RUNTIME') or Path(os.environ.get('XDG_CACHE_HOME') or Path.home() / '.cache') / 'seekframe')

cues = json.load(open(sys.argv[1]))
OUT = sys.argv[2]
SR = 48000
DUR = float(cues['dur']) + 0.3
N = int(SR * DUR)
rng = np.random.default_rng(abs(hash(cues.get('id', 'x'))) % (2 ** 32))
L = np.zeros(N)
R = np.zeros(N)
SEND = np.zeros((2, N))
exec(open(Path(__file__).with_name('audio_lib.py')).read())

STYLE = cues.get('style', 'tech')
P = {
    'drive': dict(bpm=124, kick=0.46, hats='16', clap=0.17, bass=0.14, arp=0.032, pad=0.075, cut=2100, prog=['Dm9', 'Bbmaj7', 'Fadd9', 'Cadd9']),
    'tech': dict(bpm=112, kick=0.4, hats='8', clap=0.13, bass=0.12, arp=0.03, pad=0.08, cut=1500, prog=['Dm9', 'Bbmaj7', 'Gm9', 'A7sus4']),
    'calm': dict(bpm=88, kick=0.0, hats=None, clap=0.0, bass=0.07, arp=0.045, pad=0.1, cut=1250, prog=['Fmaj9', 'Dm9', 'Bbmaj9', 'Cadd9']),
}[STYLE]
BPM = cues.get('bpm') or P['bpm']
BEAT = 60 / BPM
BAR = 4 * BEAT
CH = {
    'Dm9': [50, 57, 60, 64, 65], 'Bbmaj7': [46, 53, 57, 62, 65], 'Fadd9': [41, 53, 57, 60, 67], 'Cadd9': [48, 55, 62, 64, 67],
    'Gm9': [43, 50, 57, 58, 62], 'A7sus4': [45, 52, 57, 62, 67], 'Bbmaj9': [46, 53, 57, 60, 62], 'Fmaj9': [41, 48, 57, 60, 64, 67],
}
ROOT = {'Dm9': 38, 'Bbmaj7': 34, 'Fadd9': 41, 'Cadd9': 36, 'Gm9': 43, 'A7sus4': 33, 'Bbmaj9': 34, 'Fmaj9': 41}
scenes = cues['scenes']
endcard = next((s for s in scenes if s['type'] == 'endcard'), scenes[-1])
END_T0 = endcard['t0']
END_HIT = END_T0 + 1.4
first_cut = scenes[1]['t0'] if len(scenes) > 1 else 2.0
grid = lambda t: np.ceil(t / BEAT) * BEAT


def chord_at(t):
    if t >= END_HIT - 0.01:
        return 'Fmaj9'
    return P['prog'][int(t / (2 * BAR) + 1e-6) % len(P['prog'])]


def scene_at(t):
    cur = scenes[0]
    for s in scenes:
        if t >= s['t0']:
            cur = s
    return cur


def drums_on(t):
    if P['kick'] == 0:
        return False
    if t < grid(first_cut) - 1e-6 or t >= END_T0 - 1.2:
        return False
    sc = scene_at(t)
    return not sc.get('planned') and sc.get('energy') != 'drop'


for kk in range(int(np.ceil(END_HIT / (2 * BAR)))):
    t = kk * 2 * BAR
    end = min(END_HIT, (kk + 1) * 2 * BAR)
    if end - t < 0.05:
        continue
    name = chord_at(t + 0.01)
    nxt = scene_at(t + 0.01).get('planned')
    place(saw_pad(CH[name], end - t, 0.5 if kk == 0 else 0.08, 0.3, P['cut'] * (1.4 if nxt else 1.0)), t, P['pad'] * (1.15 if nxt else 1.0), send=0.35)
place(saw_pad(CH['Fmaj9'], DUR - END_HIT, 0.04, 1.6, 2000), END_HIT, 0.14, send=0.45)
for k, m in enumerate((65, 72, 76, 79)):
    place(pluck(mtof(m), 2.8, 0.9 + k * 0.1), END_HIT, 0.07 + 0.02 * (k == 0), send=0.7)

kicks = []
n_beats = int(DUR / BEAT) + 1
for b in range(n_beats):
    t0 = b * BEAT
    if t0 >= END_T0 - 1.2:
        break
    on = drums_on(t0)
    bar_pos = b % 4
    if on:
        place(kick(), t0, P['kick'])
        kicks.append(t0)
        if P['clap'] and bar_pos in (1, 3):
            place(clap(), t0, P['clap'], send=0.25)
        if P['hats'] == '16':
            for q in range(4):
                place(hat(q == 2), t0 + q * BEAT / 4, 0.06 if q != 2 else 0.08, pan=0.3 if q % 2 else -0.2)
        elif P['hats'] == '8':
            place(hat(True), t0 + BEAT / 2, 0.07, pan=0.25)
            if bar_pos == 3:
                place(hat(False), t0 + 3 * BEAT / 4, 0.05, pan=-0.2)
    elif STYLE == 'calm' and t0 >= first_cut and bar_pos == 0:
        place(kick(0.6, 0.2) * 0.6, t0, 0.2)
    root = ROOT[chord_at(t0 + 0.01)]
    if on:
        for e, off in enumerate((0, 0, 12, 0)[:2]):
            place(bass_note(root + (0, 12)[e % 2] * (bar_pos % 2), BEAT / 2 * 0.95), t0 + e * BEAT / 2, P['bass'])
    elif STYLE == 'calm' and t0 >= first_cut * 0.5 and t0 < END_T0 - 0.5 and bar_pos in (0, 2):
        place(bass_note(root, BEAT * 1.6), t0, P['bass'])
    if P['arp'] and t0 < END_T0 - 0.6:
        notes = CH[chord_at(t0 + 0.01)]
        steps = 2 if STYLE != 'calm' else 1
        for q in range(steps):
            i = b * steps + q
            gain = P['arp'] * (0.6 if t0 < first_cut else 1.0)
            place(pluck(mtof(notes[(i * 3) % len(notes)] + 12 + (12 if STYLE == 'drive' and i % 4 == 3 else 0)), 0.7, 1.1), t0 + q * BEAT / steps, gain, pan=((i % 4) / 3 - 0.5) * 0.6, send=0.4)

place(riser(END_HIT - (END_T0 - 1.2), 260, 9000), END_T0 - 1.2, 0.17, send=0.25)
place(impact(1.25), END_HIT, 0.34, send=0.5)

for s in scenes[1:]:
    t0, tr = s['t0'], s['tr']
    if tr == 'wipe':
        place(whoosh(0.42, 600, 8000, -0.9, 0.9), t0 - 0.04, 0.2)
    elif tr == 'rise':
        place(whoosh(0.5, 200, 2500, 0.0, 0.0), t0 - 0.02, 0.17)
    elif tr in ('page', 'flap'):
        place(paper(0.32, 34), t0, 0.15, pan=-0.3)
        place(whoosh(0.5, 400, 4000, 0.5, -0.5), t0, 0.12)
    elif tr == 'zoom':
        place(noise_sweep(0.45, 400, 7000, 0.5, 'rise'), t0 - 0.05, 0.14)
    if s['type'] != 'endcard':
        place(impact(0.4), t0 + 0.02, 0.1, send=0.3)

PENTA = [74, 77, 79, 81, 84, 86, 89, 91, 93, 96]
for e in cues['sfx']:
    t0, k, i, d = e['t'], e['k'], e.get('i', 0), e.get('d', 0.4)
    if t0 >= DUR:
        continue
    if k == 'word':
        place(pluck(mtof(PENTA[(i * 2) % 7]), 0.6, 1.3), t0, 0.09, send=0.4); place(tick(4000, 0.012), t0, 0.04)
    elif k == 'card':
        place(paper(0.05, 7, 1.3), t0, 0.1, pan=0.5); place(tick(1900 + (int(t0 * 10) % 5) * 200, 0.012), t0, 0.035, pan=0.5)
    elif k == 'stamp':
        place(impact(0.75), t0, 0.32, send=0.3); place(clap(), t0, 0.22, send=0.4)
    elif k == 'flap':
        place(flap_flip(), t0, 0.14, pan=((int(t0 * 7) % 5) / 4 - 0.5) * 0.6)
    elif k == 'blip':
        place(blip(mtof(PENTA[i % len(PENTA)]), 0.22, 'sine', 0.0, 14), t0, 0.06, send=0.4)
    elif k == 'check':
        place(blip(mtof(PENTA[min(i, 6) + 1]), 0.25, 'sine', 0.0, 12), t0, 0.08, send=0.35)
    elif k == 'sign':
        place(noise_sweep(d, 1800, 4200, 0.35, 'bell') * 0.6, t0, 0.06, pan=0.2)
    elif k == 'whoosh':
        place(whoosh(max(0.4, d), 300, 6000, -0.8, 0.8), t0, 0.16)
    elif k in ('chime', 'yes'):
        place(S(pluck(mtof(77), 1.4, 1.1), pluck(mtof(81), 1.4, 1.1) * 0.8, pluck(mtof(84), 1.4, 1.2) * 0.7), t0, 0.11, send=0.6)
    elif k == 'tick':
        place(tick(2400, 0.012), t0, 0.05)
    elif k == 'click':
        place(tick(1300, 0.025), t0, 0.14)
    elif k == 'thunk':
        place(S(kick(0.25, 1.6) * 0.5, tick(900, 0.03)), t0, 0.2)
    elif k == 'sweep':
        tt_ = tt(int(max(0.3, d) * SR))
        place(np.sin(2 * np.pi * np.cumsum(220 * 4 ** (tt_ / tt_[-1]) ** 2) / SR) * (tt_ / tt_[-1]) * 0.5, t0, 0.09)
    elif k == 'swell':
        place(noise_sweep(max(0.3, d), 400, 5000, 0.5, 'rise'), t0, 0.1)
    elif k == 'low':
        place(blip(mtof(50), 0.6, 'tri', 0.0, 5), t0, 0.08, send=0.4)
    elif k == 'typing':
        typing(t0, t0 + d, 28, 0.07)
    elif k == 'fan':
        n = int(max(0.5, d) * SR)
        x = highpass_static(lowpass_static(rng.standard_normal(n), 1400), 120) * np.linspace(0.05, 1, n) ** 1.5
        x += np.sin(2 * np.pi * np.cumsum(np.linspace(90, 210, n)) / SR) * np.linspace(0.02, 0.4, n)
        place(x / (np.max(np.abs(x)) + 1e-9), t0, 0.12)
    elif k == 'error':
        place(blip(mtof(57), 0.18, 'square', 0.2, 14), t0, 0.12); place(blip(mtof(52), 0.22, 'square', 0.2, 12), t0 + 0.14, 0.11)
    elif k == 'fail':
        place(blip(mtof(53), 0.2, 'square', 0.25, 12), t0, 0.11)
    elif k == 'msg':
        place(blip(mtof(PENTA[3 + int(t0 * 3) % 5]), 0.22, 'sine', 0.0, 14), t0, 0.065, send=0.45); place(noise_sweep(0.3, 1500, 5000, 0.5, 'bell') * 0.5, t0, 0.025)
    elif k == 'shimmer':
        place(noise_sweep(0.7, 3000, 9000, 0.4, 'bell'), t0, 0.05, send=0.6); place(blip(mtof(93), 0.6, 'sine', 0.0, 6), t0, 0.05, send=0.7)
    elif k == 'chord':
        place(S(pluck(mtof(65), 1.2, 1.0), pluck(mtof(72), 1.2, 1.0) * 0.7, pluck(mtof(77), 1.2, 1.2) * 0.6), t0, 0.11, send=0.5)
    elif k == 'stuck':
        place(impact(0.5), t0, 0.2, send=0.4); place(blip(mtof(50), 0.35, 'square', 0.2, 8), t0, 0.09, send=0.3)
    elif k == 'revoke':
        place(noise_sweep(0.3, 6000, 1500, 0.4, 'fall'), t0, 0.07); place(tick(1200, 0.03), t0 + 0.15, 0.12)
    elif k == 'block':
        place(pluck(mtof((62, 65, 67, 69, 72, 74, 77)[i % 7]), 0.8, 0.8), t0, 0.12, send=0.35); place(S(kick(0.12, 0.4) * 0.3), t0, 0.12)
    elif k == 'wobble':
        tt_ = tt(int(0.6 * SR))
        place(np.sin(2 * np.pi * np.cumsum(220 + 30 * np.sin(2 * np.pi * 7 * tt_)) / SR) * np.exp(-tt_ * 4), t0, 0.08)
    elif k == 'step':
        for q in range(4):
            place(S(kick(0.1, 0.3) * 0.4, paper(0.04, 5)), t0 + q * d / 4, 0.08)
    elif k == 'impact':
        pass
    elif k == 'slam':
        place(impact(0.7), t0, 0.3, send=0.3); place(clap(), t0, 0.24, send=0.35); place(kick(0.4, 1.4), t0, 0.3)
    elif k == 'approve':
        place(tick(1500, 0.02), t0, 0.12); place(blip(mtof(84 + (i % 3) * 3), 0.12, 'sine', 0.0, 24), t0 + 0.04, 0.05)
    elif k == 'drop':
        place(impact(1.1), t0, 0.5, send=0.6)
    elif k == 'letters':
        for q in range(6):
            place(pluck(mtof((77, 79, 81, 84, 86, 89)[q]), 0.7, 1.2), t0 + q * 0.055, 0.04, pan=(q / 5 - 0.5) * 0.8, send=0.5)
    elif k == 'tagline':
        for q, m in enumerate((72, 76, 79, 84)):
            place(pluck(mtof(m), 1.2, 1.1), t0 + q * 0.12, 0.06, send=0.6)

tg = np.arange(N) / SR
duck = np.ones(N)
for k_ in kicks:
    i = int(k_ * SR)
    seg = tg[i:i + int(0.4 * SR)] - k_
    duck[i:i + len(seg)] = np.minimum(duck[i:i + len(seg)], 1 - 0.5 * np.exp(-seg * 9))
L *= 0.4 + 0.6 * duck
R *= 0.4 + 0.6 * duck
ir_n = int(2.6 * SR)
it = tt(ir_n)
ir = rng.standard_normal((2, ir_n)) * np.exp(-it * 6.9 / 2.4)
ir = np.stack([lowpass_static(ir[0], 5000), lowpass_static(ir[1], 5000)])
ir[:, : int(0.012 * SR)] = 0
ir /= np.sqrt(np.sum(ir ** 2, axis=1, keepdims=True))
size = 1 << int(np.ceil(np.log2(N + ir_n)))
for c, buf in ((0, L), (1, R)):
    buf += np.fft.irfft(np.fft.rfft(SEND[c], size) * np.fft.rfft(ir[c], size), size)[:N] * 0.55
mix = np.stack([highpass_static(L, 28), highpass_static(R, 28)])
mix = np.tanh(mix * 1.15) / np.tanh(1.15)
fade = np.ones(N)
fade[-int(0.8 * SR):] = np.linspace(1, 0, int(0.8 * SR)) ** 2
fade[: int(0.02 * SR)] = np.linspace(0, 1, int(0.02 * SR))
mix *= fade
rms = np.sqrt(np.mean(mix[:, : int(max(1.0, END_T0) * SR)] ** 2))
mix *= 10 ** (-19.5 / 20) / max(rms, 1e-9)
def limit(mix, CEIL=0.8, BLK=96):
    nb = N // BLK + 1
    pad = np.zeros((2, nb * BLK)); pad[:, :N] = mix
    env = np.abs(pad).max(axis=0).reshape(nb, BLK).max(axis=1)
    g = np.minimum(1.0, CEIL / np.maximum(env, 1e-9))
    g = np.minimum(g, np.concatenate([g[1:], [1.0]]))
    rel = np.exp(-BLK / (0.12 * SR))
    sm = np.empty(nb); acc = 1.0
    for j in range(nb):
        acc = g[j] if g[j] < acc else 1 - (1 - acc) * rel
        sm[j] = acc
    return np.clip(mix * np.interp(np.arange(nb * BLK), np.arange(nb) * BLK, sm)[:N], -0.89, 0.89)


def write(path, x):
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x.T * 32767).astype('<i2').tobytes())


def lufs(path):
    import re, subprocess
    out = subprocess.run([str(RUNTIME / 'ffmpeg'), '-nostdin', '-hide_banner', '-i', path, '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', out)[-1])


mix = limit(mix)
for _ in range(2):
    write(OUT, mix)
    mix = limit(mix * 10 ** ((-16.0 - lufs(OUT)) / 20))
write(OUT, mix)
print('wrote', OUT, f'{DUR:.1f}s', STYLE, len(cues['sfx']), 'cues')
