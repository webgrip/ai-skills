def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def S(*xs):
    n = max(len(x) for x in xs)
    out = np.zeros(n)
    for x in xs:
        out[:len(x)] += x
    return out


def tt(n):
    return np.arange(n) / SR


def place(sig, t0, gain=1.0, pan=0.0, send=0.0):
    """Mix a mono or stereo signal into the master at t0 seconds."""
    i = int(round(t0 * SR))
    if sig.ndim == 1:
        l = sig * gain * np.sqrt(0.5 * (1 - pan))
        r = sig * gain * np.sqrt(0.5 * (1 + pan))
    else:
        l, r = sig[0] * gain, sig[1] * gain
    if i < 0:
        l, r = l[-i:], r[-i:]
        i = 0
    n = min(len(l), N - i)
    if n <= 0:
        return
    L[i:i + n] += l[:n]
    R[i:i + n] += r[:n]
    if send:
        SEND[0, i:i + n] += l[:n] * send
        SEND[1, i:i + n] += r[:n] * send


def stft_filter(x, gain_fn, n_fft=2048, hop=512):
    """Time-varying spectral filter: gain_fn(times[F], freqs[K]) -> gains[F, K]."""
    win = np.hanning(n_fft)
    pad = np.concatenate([np.zeros(n_fft), x, np.zeros(n_fft)])
    frames = 1 + (len(pad) - n_fft) // hop
    idx = np.arange(n_fft)[None, :] + hop * np.arange(frames)[:, None]
    spec = np.fft.rfft(pad[idx] * win, axis=1)
    times = (np.arange(frames) * hop + n_fft / 2 - n_fft) / SR
    freqs = np.fft.rfftfreq(n_fft, 1 / SR)
    spec *= gain_fn(times, freqs)
    out_frames = np.fft.irfft(spec, n=n_fft, axis=1) * win
    out = np.zeros(len(pad))
    norm = np.zeros(len(pad))
    for f in range(frames):
        s = f * hop
        out[s:s + n_fft] += out_frames[f]
        norm[s:s + n_fft] += win ** 2
    out /= np.maximum(norm, 1e-6)
    return out[n_fft:n_fft + len(x)]


def band(times, freqs, fc, width_oct):
    lf = np.log2(np.maximum(freqs[None, :], 1.0))
    c = np.log2(np.maximum(fc(times), 20.0))[:, None]
    return np.exp(-0.5 * ((lf - c) / width_oct) ** 2)


def lowpass_static(x, fc, order=2):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / np.sqrt(1 + (f / fc) ** (2 * order))
    return np.fft.irfft(X, n=len(x))


def highpass_static(x, fc, order=2):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / np.sqrt(1 + (fc / np.maximum(f, 1e-3)) ** (2 * order))
    return np.fft.irfft(X, n=len(x))


def kick(dur=0.5, punch=1.0):
    t = tt(int(dur * SR))
    f = 44 + 120 * np.exp(-t * 30)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t * 6.5)
    click = highpass_static(rng.standard_normal(len(t)), 2500) * np.exp(-t * 400) * 0.35
    return np.tanh((body + click * punch) * 1.6)


def clap(dur=0.32):
    t = tt(int(dur * SR))
    n = highpass_static(lowpass_static(rng.standard_normal(len(t)), 5000), 900)
    env = np.zeros(len(t))
    for d in (0.0, 0.011, 0.022):
        env += np.where(t >= d, np.exp(-(t - d) * 90), 0) * 0.6
    env += np.where(t >= 0.03, np.exp(-(t - 0.03) * 16), 0)
    tone = np.sin(2 * np.pi * 185 * t) * np.exp(-t * 30) * 0.5
    return n * env * 0.6 + tone


def hat(open_=False):
    dur = 0.28 if open_ else 0.06
    t = tt(int(dur * SR))
    n = highpass_static(rng.standard_normal(len(t)), 7000, 3)
    return n * np.exp(-t * (11 if open_ else 70)) * 0.5


def blip(freq, dur=0.18, kind='sine', drop=0.0, decay=18):
    t = tt(int(dur * SR))
    f = freq * (1 - drop * (1 - np.exp(-t * 30)))
    ph = 2 * np.pi * np.cumsum(f) / SR
    if kind == 'sine':
        w = np.sin(ph)
    elif kind == 'tri':
        w = 2 / np.pi * np.arcsin(np.sin(ph))
    else:
        w = np.sign(np.sin(ph)) * 0.5
        w = lowpass_static(w, 2500)
    env = np.minimum(1, t / 0.003) * np.exp(-t * decay)
    return w * env


def pluck(freq, dur=0.9, bright=1.0):
    t = tt(int(dur * SR))
    out = np.zeros(len(t))
    for k in range(1, 12):
        fk = freq * k * (1 + 0.0007 * k * k)
        if fk > 12000:
            break
        out += np.sin(2 * np.pi * fk * t + k) * (1 / k ** 1.1) * np.exp(-t * (2.5 + k * 1.6 / bright))
    return out * np.minimum(1, t / 0.002) * 0.5


def tick(freq=3200, dur=0.012):
    t = tt(int(dur * SR))
    return np.sin(2 * np.pi * freq * t) * np.exp(-t * 600) + highpass_static(rng.standard_normal(len(t)), 4000) * np.exp(-t * 900) * 0.4


def noise_sweep(dur, f0, f1, width=0.6, shape='rise', curve=2.0):
    n = int(dur * SR)
    x = rng.standard_normal(n)
    fc = lambda ts: f0 * (f1 / f0) ** np.clip(ts / dur, 0, 1) ** curve
    y = stft_filter(x, lambda ts, fs: band(ts, fs, fc, width), 1024, 256)
    t = tt(n) / dur
    if shape == 'rise':
        env = t ** 2.2
    elif shape == 'fall':
        env = (1 - t) ** 1.6 * np.minimum(1, t / 0.02)
    else:
        env = np.sin(np.pi * np.clip(t, 0, 1)) ** 1.5
    y = y * env
    return y / (np.max(np.abs(y)) + 1e-9)


def whoosh(dur, f0=300, f1=4000, pan0=-0.6, pan1=0.6):
    m = noise_sweep(dur, f0, f1, 0.7, 'bell', 1.0)
    p = np.linspace(pan0, pan1, len(m))
    return np.stack([m * np.sqrt(0.5 * (1 - p)), m * np.sqrt(0.5 * (1 + p))])


def riser(dur, f0=200, f1=9000):
    n = noise_sweep(dur, f0, f1, 0.5, 'rise', 1.6)
    t = tt(len(n))
    f = 180 * (8 ** (t / dur) ** 1.5)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * (t / dur) ** 3 * 0.35
    return n * 0.8 + tone


def impact(size=1.0):
    dur = 2.5
    t = tt(int(dur * SR))
    f = 38 + 70 * np.exp(-t * 9)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2)
    burst = lowpass_static(rng.standard_normal(len(t)), 1800) * np.exp(-t * 9) * 0.7
    crack = highpass_static(rng.standard_normal(len(t)), 3000) * np.exp(-t * 40) * 0.5
    return np.tanh((sub * 1.2 + burst + crack) * size)


def paper(dur=0.16, density=26, bright=1.0):
    n = int(dur * SR)
    out = np.zeros(n)
    for _ in range(density):
        i = rng.integers(0, max(1, n - 400))
        ln = rng.integers(40, 260)
        g = rng.uniform(0.2, 1.0)
        out[i:i + ln] += rng.standard_normal(ln) * np.exp(-np.arange(ln) / (ln / 4)) * g
    out = highpass_static(lowpass_static(out, 7000 * bright), 900)
    env = np.sin(np.pi * np.linspace(0, 1, n)) ** 0.5
    return out * env / (np.max(np.abs(out)) + 1e-9)


def flap_flip():
    return S(paper(0.07, 10, 1.2) * 0.7, blip(1400, 0.04, 'tri', 0.3, 80) * 0.25)


def typing(t0, t1, rate=26, gain=0.12):
    k = 0
    t = t0
    while t < t1:
        f = 2200 + (hash_(k) % 1400)
        place(S(tick(f, 0.012) * 0.8, paper(0.012, 2, 1.4) * 0.4), t, gain, pan=((hash_(k * 3) % 100) / 100 - 0.5) * 0.4)
        k += 1
        t += 1 / rate * (0.75 + (hash_(k * 7) % 50) / 100)


def hash_(n):
    n = (n ^ 61) ^ (n >> 16)
    n = (n + (n << 3)) & 0xffffffff
    n ^= n >> 4
    n = (n * 0x27d4eb2d) & 0xffffffff
    return n ^ (n >> 15)


def saw_pad(notes, dur, attack=0.6, release=1.2, cutoff=1800, detune=0.08):
    n = int((dur + release) * SR)
    t = tt(n)
    out = np.zeros((2, n))
    for m in notes:
        f = mtof(m)
        for j, d in enumerate((-detune, 0.0, detune)):
            fj = f * 2 ** (d / 12)
            ph = (fj * t + rng.random()) % 1.0
            w = 2 * ph - 1
            pan = (-0.5, 0.0, 0.5)[j]
            out[0] += w * np.sqrt(0.5 * (1 - pan))
            out[1] += w * np.sqrt(0.5 * (1 + pan))
    env = np.minimum(1, t / attack) * np.where(t < dur, 1.0, np.exp(-(t - dur) * 4 / release))
    out = np.stack([lowpass_static(out[0], cutoff, 2), lowpass_static(out[1], cutoff, 2)]) * env
    return out / (len(notes) * 3) * 1.6


def bass_note(m, dur=0.24, glide=0.0):
    f = mtof(m)
    t = tt(int(dur * SR))
    out = np.sin(2 * np.pi * f * t) * 1.0
    for k in range(2, 14):
        out += np.sin(2 * np.pi * f * k * t) * (1 / k) * np.exp(-t * (6 + k * 3.5)) * 0.9
    env = np.minimum(1, t / 0.004) * np.exp(-t * 3.2) * np.minimum(1, (dur - t) / 0.02)
    return out * env


