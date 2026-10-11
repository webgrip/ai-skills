"""Voice-over tools.

python vo.py prep <take> <n_lines> <lines_dir> <timing.js>
    Split one ElevenLabs take into its lines (at the longest pauses), clean each line and write
    window.TIMING with each line's spoken length, so the video re-times its scenes to the voice.
    Separate files named <id>-01.*, <id>-02.* … in the voice folder replace single lines.
python vo.py mix <cues.json> <lines_dir> <music.wav> <out.wav>
    Place every line at its scene time, duck the music under it and master the result.
"""
import json
import os
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

RUNTIME = Path(os.environ.get('SEEKFRAME_RUNTIME') or Path(os.environ.get('XDG_CACHE_HOME') or Path.home() / '.cache') / 'seekframe')

SR = 48000
FFMPEG = str(RUNTIME / 'ffmpeg')


def decode(path):
    raw = subprocess.run([FFMPEG, '-loglevel', 'error', '-i', str(path), '-f', 's16le', '-ac', '1', '-ar', str(SR), '-'], check=True, capture_output=True).stdout
    return np.frombuffer(raw, '<i2').astype(np.float64) / 32768


def write_wav(path, x, ch=1):
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(ch); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(x.T if ch > 1 else x, -1, 1) * 32767).astype('<i2').tobytes())


def read_wav(path):
    with wave.open(str(path)) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(np.float64) / 32768
        return x.reshape(-1, w.getnchannels()).T


def envelope(x, win=480):
    return np.convolve(np.abs(x), np.ones(win) / win, 'same')


def trim(x, thresh_db=-45, pad=0.04, with_lead=False):
    on = np.where(envelope(x) > 10 ** (thresh_db / 20))[0]
    if len(on) == 0:
        return (x, 0.0) if with_lead else x
    a = max(0, on[0] - int(pad * SR))
    y = x[a: min(len(x), on[-1] + int(pad * SR))]
    return (y, a / SR) if with_lead else y


def split_take(x, count, words=None, min_gap=0.16, thresh_db=-42):
    """Cut one take into `count` lines. Among all pauses, choose the cuts whose segment lengths best
    match each line's share of the words, preferring longer pauses (dynamic programming)."""
    loud = envelope(x) > 10 ** (thresh_db / 20)
    gaps, j = [], 0
    while j < len(loud):
        if not loud[j]:
            k = j
            while k < len(loud) and not loud[k]:
                k += 1
            if (k - j) / SR >= min_gap and j > 0 and k < len(loud):
                gaps.append(((j + k) // 2, (k - j) / SR))
            j = k
        else:
            j += 1
    if len(gaps) < count - 1:
        raise SystemExit(f'found {len(gaps) + 1} lines in the take; the script has {count}. Regenerate with clearer pauses, or send single lines.')
    on = np.where(loud)[0]
    start, end = (on[0], on[-1]) if len(on) else (0, len(x))
    w = np.array(words if words else [1] * count, dtype=float)
    pos = np.array([g[0] for g in gaps], dtype=float); length = np.array([g[1] for g in gaps])
    gbar = float(np.mean(sorted(length, reverse=True)[:count - 1]))
    rate = max(1e-3, ((end - start) / SR - (count - 1) * gbar) / w.sum())
    exp = w * rate + gbar
    M, INF = len(gaps), 1e18
    seg = lambda a_, b_, i: abs((b_ - a_) / SR - exp[i]) / exp[i] * 6.0
    bonus = lambda c: min(length[c], 1.2) * 2.5
    best = np.full((count - 1, M), INF); back = np.full((count - 1, M), -1)
    for c in range(M):
        best[0, c] = seg(start, pos[c], 0) - bonus(c)
    for i in range(1, count - 1):
        for c in range(i, M):
            prev = best[i - 1, :c] + np.array([seg(pos[q], pos[c], i) for q in range(c)])
            q = int(np.argmin(prev)); best[i, c] = prev[q] - bonus(c); back[i, c] = q
    last = best[count - 2] + np.array([seg(pos[c], end, count - 1) for c in range(M)])
    c = int(np.argmin(last))
    cuts = [c]
    for i in range(count - 2, 0, -1):
        c = int(back[i, c]); cuts.append(c)
    cuts = sorted(int(pos[c]) for c in cuts)
    bounds = [0, *cuts, len(x)]
    return [x[a:b] for a, b in zip(bounds, bounds[1:])]


def highpass(x, fc=85):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / np.sqrt(1 + (fc / np.maximum(f, 1e-3)) ** 4)
    return np.fft.irfft(X, n=len(x))


def compress(x, thresh_db=-20, ratio=3.0):
    env = np.sqrt(np.convolve(x ** 2, np.ones(960) / 960, 'same') + 1e-12)
    lvl = 20 * np.log10(env)
    return x * 10 ** (np.where(lvl > thresh_db, (thresh_db - lvl) * (1 - 1 / ratio), 0.0) / 20)


def prep(take, n, lines_dir, timing_js, words=None):
    lines_dir = Path(lines_dir); lines_dir.mkdir(parents=True, exist_ok=True)
    take = Path(take)
    parts = split_take(decode(take), n, words) if take.exists() else [None] * n
    out = []
    for i in range(n):
        single = sorted(f for f in take.parent.glob(f'{take.stem}-{i + 1:02d}.*') if f.suffix.lower() in ('.mp3', '.wav', '.m4a', '.flac', '.ogg', '.aac'))
        x = decode(single[0]) if single else parts[i]
        if x is None:
            raise SystemExit(f'line {i + 1} is missing')
        x, lead = trim(x, with_lead=True)
        x = compress(highpass(x))
        x *= 10 ** (-18 / 20) / (np.sqrt(np.mean(x ** 2)) + 1e-9)
        write_wav(lines_dir / f'{i + 1:02d}.wav', x)
        out.append({'dur': round(len(x) / SR, 3), 'lead': round(lead, 3)})
        print(f'line {i + 1:02d}: {len(x) / SR:.2f} s' + ('  (single take)' if single else ''))
    Path(timing_js).write_text('window.TIMING = ' + json.dumps(out) + ';\n')


def mix(cues_json, lines_dir, music_wav, out_wav):
    cues = json.load(open(cues_json))
    music = read_wav(music_wav)
    n = music.shape[1]
    voice = np.zeros(n)
    for i, l in enumerate(cues['lines']):
        f = Path(lines_dir) / f'{i + 1:02d}.wav'
        if not f.exists():
            continue
        x = read_wav(f)[0]
        a = int((l['t0'] + 0.12) * SR); m = min(len(x), n - a)
        if m > 0:
            voice[a:a + m] += x[:m]
    env = np.convolve(np.abs(voice), np.ones(2400) / 2400, 'same')
    target = np.clip(env / 0.02, 0, 1)
    k = np.exp(-1 / (0.3 * SR)); sm = np.empty(n); acc = 0.0
    for j in range(0, n, 48):
        acc = max(target[j], acc * k ** 48); sm[j:j + 48] = acc
    mixd = music * (1 - 0.62 * sm) + np.stack([voice, voice]) * 1.0
    peak = np.max(np.abs(mixd))
    if peak > 0.89:
        mixd *= 0.89 / peak
    write_wav(out_wav, mixd, 2)
    print('wrote', out_wav)


if __name__ == '__main__':
    if sys.argv[1] == 'prep':
        prep(sys.argv[2], int(sys.argv[3]), sys.argv[4], sys.argv[5], json.loads(sys.argv[6]) if len(sys.argv) > 6 else None)
    else:
        mix(*sys.argv[2:6])
