"""Sound kit made from maths (no samples), voice processing, mixing and phone-level checks.

Every important low sound also carries a mid-range layer, because phone speakers
play almost nothing below ~300 Hz.
"""
import math
import wave

import numpy as np
from scipy import signal

SR = 48000


def silence(sec):
    return np.zeros(int(sec * SR), np.float32)


def rng(seed):
    return np.random.default_rng(seed)


def env(n, a=0.005, d=0.3, s=0.0, r=0.05):
    """Attack / exponential decay envelope over n samples."""
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4)) * (s + (1 - s) * np.exp(-t / max(d, 1e-4)))
    rel = int(r * SR)
    if rel and n > rel:
        e[-rel:] *= np.linspace(1, 0, rel)
    return e.astype(np.float32)


def hz(note):
    """MIDI note -> Hz."""
    return 440.0 * 2 ** ((note - 69) / 12)


def bp(x, lo, hi, order=2):
    sos = signal.butter(order, [lo, hi], btype="band", fs=SR, output="sos")
    return signal.sosfilt(sos, x).astype(np.float32)


def lp(x, f, order=2):
    sos = signal.butter(order, f, btype="low", fs=SR, output="sos")
    return signal.sosfilt(sos, x).astype(np.float32)


def hp(x, f, order=2):
    sos = signal.butter(order, f, btype="high", fs=SR, output="sos")
    return signal.sosfilt(sos, x).astype(np.float32)


# ---- instruments --------------------------------------------------------------
def piano(note, dur=1.6, vel=0.6):
    f = hz(note)
    n = int((dur + 0.4) * SR)
    t = np.arange(n) / SR
    x = np.zeros(n, np.float32)
    for k, amp in enumerate([1.0, 0.45, 0.25, 0.12, 0.07, 0.04], start=1):
        x += amp * np.sin(2 * np.pi * f * k * (1 + 0.0004 * k * k) * t) * np.exp(-t * (1.2 + 0.9 * k))
    x *= np.minimum(1, t / 0.004)
    x[int(dur * SR):] *= np.linspace(1, 0, n - int(dur * SR))
    return (x * vel * 0.32).astype(np.float32)


def music_box(note, dur=1.2, vel=0.5):
    f = hz(note)
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 3.98 * t) * np.exp(-t * 9)
    x *= np.exp(-t * 3.2) * np.minimum(1, t / 0.002)
    return (x * vel * 0.28).astype(np.float32)


def pluck(note, dur=1.0, vel=0.5, bright=1.0, seed=0):
    """Plucked string (pizzicato-like): harmonics that die faster the higher they are, plus a pick noise."""
    f = hz(note)
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.zeros(n, np.float32)
    for k in range(1, 11):
        if f * k > 16000:
            break
        x += (1.0 / k) ** (1.4 / bright) * np.sin(2 * np.pi * f * k * t + k) * np.exp(-t * (2.5 + 1.6 * k / bright))
    pick = bp(rng(200 + seed).normal(0, 1, n).astype(np.float32), 1500, 6000) * np.exp(-t * 300) * 0.25
    x = (x + pick) * np.minimum(1, t / 0.002)
    x[-int(0.02 * SR):] *= np.linspace(1, 0, int(0.02 * SR))
    return (x * vel * 0.3).astype(np.float32)


def clink(vel=0.5, seed=0, bounces=3):
    """A glass marble landing: bright inharmonic pings with a few smaller bounces."""
    n = int(0.9 * SR)
    out = np.zeros(n, np.float32)
    r = rng(500 + seed)
    base = 2600 + r.uniform(-300, 300)
    for b in range(bounces):
        k = int((0.0 + 0.11 * b + 0.03 * b * b) * SR)
        tt = np.arange(n - k) / SR
        a = 0.55 ** b
        x = np.zeros(n - k, np.float32)
        for m, amp in ((1.0, 1.0), (1.59, 0.5), (2.43, 0.3), (3.7, 0.15)):
            x += amp * np.sin(2 * np.pi * base * m * tt) * np.exp(-tt * (40 + 25 * m))
        x += bp(r.normal(0, 1, n - k).astype(np.float32), 2000, 8000) * np.exp(-tt * 300) * 0.3
        out[k:] += x * a
    return (out * vel * 0.45).astype(np.float32)


def ringtone(dur=2.0, vel=0.4):
    """A phone ringing: a two-note marimba-like ring in pairs, mid-range so phone speakers play it."""
    n = int(dur * SR)
    out = np.zeros(n, np.float32)
    t = 0.0
    while t < dur - 0.2:
        for i, note in enumerate((76, 83)):
            f = hz(note)
            k = int((t + i * 0.13) * SR)
            m = min(int(0.3 * SR), n - k)
            if m <= 0:
                continue
            tt = np.arange(m) / SR
            x = (np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(2 * np.pi * f * 4 * tt) * np.exp(-tt * 30)) * np.exp(-tt * 12)
            out[k:k + m] += x.astype(np.float32)
        t += 0.9
    return (out * vel * 0.4).astype(np.float32)


def knock(vel=0.6, times=(0, 0.18)):
    """Knuckles on a wooden door: knocks with a woody mid-range body."""
    n = int(0.6 * SR)
    out = np.zeros(n, np.float32)
    for i, off in enumerate(times):
        k = int(off * SR)
        tt = np.arange(n - k) / SR
        body = np.sin(2 * np.pi * 180 * tt) * np.exp(-tt * 40) + np.sin(2 * np.pi * 420 * tt) * np.exp(-tt * 60) * 0.6
        click = bp(rng(300 + i).normal(0, 1, n - k).astype(np.float32), 800, 3500) * np.exp(-tt * 120) * 0.6
        out[k:] += (body + click).astype(np.float32)
    return (out * vel * 0.6).astype(np.float32)


def scribble(dur=0.6, vel=0.4, seed=0):
    """Pen on paper: scratchy noise in short strokes."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = bp(rng(400 + seed).normal(0, 1, n).astype(np.float32), 2500, 7000)
    strokes = 0.5 + 0.5 * np.sin(2 * np.pi * 9 * t) ** 2
    return (x * strokes * np.sin(np.pi * t / dur) * vel * 0.5).astype(np.float32)


def pad(notes, dur, vel=0.4, bright=1800, seed=0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.zeros(n, np.float32)
    r = rng(seed)
    for note in notes:
        for det in (-0.07, 0.0, 0.06):
            f = hz(note) * 2 ** (det / 12)
            ph = r.random() * 2 * np.pi
            x += signal.sawtooth(2 * np.pi * f * t + ph).astype(np.float32) * 0.3
    x = lp(x, bright)
    a = min(1.2, dur / 3)
    e = np.minimum(1, t / a) * np.minimum(1, (dur - t) / a)
    return (x * e * vel * 0.10 / max(1, len(notes) ** 0.5)).astype(np.float32)


def soft_kick(vel=0.6):
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    f = 52 + 70 * np.exp(-t * 30)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)
    knock = bp(rng(5).normal(0, 1, n).astype(np.float32), 900, 2600) * np.exp(-t * 60) * 0.6
    return ((x + knock) * vel * 0.6).astype(np.float32)


# ---- effects --------------------------------------------------------------------
def tick(vel=0.5):
    n = int(0.06 * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 120) + bp(rng(1).normal(0, 1, n).astype(np.float32), 2000, 6000) * np.exp(-t * 200) * 0.4
    return (x * vel * 0.5).astype(np.float32)


def buzz(dur=0.9, vel=0.6):
    """Phone vibration: low rumble plus a mid-range rattle so a phone speaker plays it."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    gate = ((t % 0.42) < 0.3).astype(np.float32)
    x = signal.square(2 * np.pi * 165 * t).astype(np.float32) * 0.5 + np.sin(2 * np.pi * 330 * t) * 0.3
    x = bp(x, 150, 1800) + bp(rng(2).normal(0, 1, n).astype(np.float32), 900, 2400) * 0.25
    return (x * gate * vel * 0.5).astype(np.float32)


def heartbeat(vel=0.6):
    n = int(0.7 * SR)
    t = np.arange(n) / SR
    out = np.zeros(n, np.float32)
    for off, a in ((0, 1.0), (0.22, 0.7)):
        k = int(off * SR)
        tt = t[: n - k]
        thump = np.sin(2 * np.pi * 55 * tt) * np.exp(-tt * 18)
        knock = bp(rng(3 + k).normal(0, 1, n - k).astype(np.float32), 500, 1400) * np.exp(-tt * 45) * 0.5
        out[k:] += (thump + knock) * a
    return (out * vel * 0.7).astype(np.float32)


def whoosh(dur=0.6, vel=0.5, up=True, seed=4):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = rng(seed).normal(0, 1, n).astype(np.float32)
    out = np.zeros(n, np.float32)
    seg = 8
    for i in range(seg):
        a, b = i * n // seg, (i + 1) * n // seg
        f = 400 + 3000 * ((i / seg) if up else (1 - i / seg))
        out[a:b] = bp(x, f * 0.6, f * 1.4)[a:b]
    e = np.sin(np.pi * t / dur) ** 2
    return (out * e * vel * 0.8).astype(np.float32)


def thud(vel=0.6):
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * 80 * t) * np.exp(-t * 22) + bp(rng(6).normal(0, 1, n).astype(np.float32), 400, 1600) * np.exp(-t * 35) * 0.7
    return (x * vel * 0.7).astype(np.float32)


def tap(vel=0.35, seed=0):
    """Screen tap / key press."""
    n = int(0.04 * SR)
    t = np.arange(n) / SR
    x = bp(rng(100 + seed).normal(0, 1, n).astype(np.float32), 1500, 5000) * np.exp(-t * 180)
    return (x * vel).astype(np.float32)


def blow(dur=0.8, vel=0.5):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = bp(rng(7).normal(0, 1, n).astype(np.float32), 300, 3000) * np.sin(np.pi * t / dur) ** 1.5
    return (x * vel).astype(np.float32)


def shimmer(dur=2.4, vel=0.4, base=84):
    out = np.zeros(int(dur * SR), np.float32)
    for i, nn in enumerate([0, 4, 7, 12, 16, 19]):
        s = music_box(base + nn, dur=dur - i * 0.12, vel=vel)
        k = int(i * 0.09 * SR)
        out[k:k + len(s)] += s[: len(out) - k]
    return out


def hit(vel=0.9):
    """The big impact: boom + crack + noise burst."""
    n = int(1.6 * SR)
    t = np.arange(n) / SR
    boom = np.sin(2 * np.pi * np.cumsum(45 + 60 * np.exp(-t * 12)) / SR) * np.exp(-t * 3)
    crack = bp(rng(8).normal(0, 1, n).astype(np.float32), 1200, 7000) * np.exp(-t * 14)
    return ((boom * 0.8 + crack * 0.6) * vel).astype(np.float32)


def room_tone(dur, vel=0.05, seed=9):
    x = rng(seed).normal(0, 1, int(dur * SR)).astype(np.float32)
    return (lp(hp(x, 120), 1400) * vel).astype(np.float32)


def rain(dur, vel=0.12, seed=10):
    n = int(dur * SR)
    x = rng(seed).normal(0, 1, n).astype(np.float32)
    x = bp(x, 800, 7000)
    drops = (rng(seed + 1).random(n) > 0.9993).astype(np.float32)
    drops = signal.lfilter([1], [1, -0.97], drops).astype(np.float32)
    return ((x * 0.6 + bp(drops * rng(seed + 2).normal(0, 1, n).astype(np.float32), 1500, 5000) * 2) * vel).astype(np.float32)


def street(dur, vel=0.06, seed=11):
    n = int(dur * SR)
    x = lp(rng(seed).normal(0, 1, n).astype(np.float32), 600)
    t = np.arange(n) / SR
    swell = 0.6 + 0.4 * np.sin(2 * np.pi * t / 7.0)
    return (hp(x, 150) * swell * vel * 3).astype(np.float32)


def footsteps(times, vel=0.3):
    out = []
    for i, tm in enumerate(times):
        n = int(0.12 * SR)
        t = np.arange(n) / SR
        x = bp(rng(200 + i).normal(0, 1, n).astype(np.float32), 300, 2500) * np.exp(-t * 50)
        out.append((tm, (x * vel).astype(np.float32)))
    return out


# ---- voices ---------------------------------------------------------------------
def resample(x, sr_in, sr_out=SR):
    sr_out = int(round(sr_out / 50.0)) * 50
    if sr_in == sr_out:
        return x.astype(np.float32)
    g = math.gcd(int(sr_in), sr_out)
    return signal.resample_poly(x, sr_out // g, sr_in // g).astype(np.float32)


def trim(x, thresh=0.01):
    idx = np.where(np.abs(x) > thresh)[0]
    if len(idx) == 0:
        return x
    return x[max(0, idx[0] - 240): idx[-1] + 2400]


def normalize_rms(x, target_db=-20.0):
    r = np.sqrt(np.mean(x ** 2) + 1e-12)
    return (x * (10 ** (target_db / 20) / r)).astype(np.float32)


def simple_reverb(x, mix=0.18, decay=0.45):
    out = x.copy()
    for d, a in ((0.031, 0.6), (0.047, 0.5), (0.071, 0.4), (0.113, 0.3), (0.157, 0.22)):
        k = int(d * SR)
        y = np.zeros_like(x)
        y[k:] = x[:-k] * a * decay
        out += y * (mix / 0.18)
    return out.astype(np.float32)


def whisperize(x, sr, pitch=0.82):
    """Villain voice: pitched down, breathy, doubled lower, a little wet. Sounds like a thought."""
    # resample to a higher rate, play back at SR: lower and slightly slower
    y = resample(x, sr, int(SR / pitch))
    breath_env = np.abs(signal.hilbert(y)).astype(np.float32)
    breath_env = lp(breath_env, 30)
    noise = bp(rng(12).normal(0, 1, len(y)).astype(np.float32), 1200, 6500) * breath_env * 1.6
    dbl = resample(y, SR, int(SR / 0.85))[: len(y)]
    dbl = np.pad(dbl, (0, len(y) - len(dbl)))
    v = hp(y, 140) * 0.55 + noise * 0.8 + lp(dbl, 1800) * 0.35
    v = simple_reverb(v, 0.25)
    return normalize_rms(v, -24)


def phone_line(x):
    """Voice heard through a phone receiver."""
    return normalize_rms(bp(x, 350, 3200, 3), -26)


# ---- mixing ---------------------------------------------------------------------
class Mix:
    def __init__(self, duration):
        self.n = int(duration * SR)
        self.buses = {}

    def add(self, bus, t, x, gain=1.0):
        b = self.buses.setdefault(bus, np.zeros(self.n, np.float32))
        k = int(round(t * SR))
        if k >= self.n or len(x) == 0:
            return
        if k < 0:
            x = x[-k:]
            k = 0
        m = min(len(x), self.n - k)
        b[k:k + m] += x[:m] * gain

    def duck(self, bus, regions, depth_db=-8, ramp=0.25):
        """Lower `bus` under speech regions [(t0, t1), ...]."""
        if bus not in self.buses:
            return
        g = np.ones(self.n, np.float32)
        d = 10 ** (depth_db / 20)
        for t0, t1 in regions:
            a, b = int((t0 - ramp) * SR), int((t1 + ramp) * SR)
            a, b = max(0, a), min(self.n, b)
            seg = np.full(b - a, d, np.float32)
            r = int(ramp * SR)
            seg[:r] = np.linspace(1, d, min(r, len(seg)))[: len(seg[:r])]
            if r and len(seg) > r:
                seg[-r:] = np.linspace(d, 1, r)
            g[a:b] = np.minimum(g[a:b], seg)
        self.buses[bus] *= g

    def silence_window(self, t0, t1, keep=("voice",), ramp=0.15):
        """Near-silence before the biggest hit: everything except `keep` fades out."""
        for name, b in self.buses.items():
            if name in keep:
                continue
            a, z = int(t0 * SR), int(t1 * SR)
            r = int(ramp * SR)
            b[a - r:a] *= np.linspace(1, 0.03, r)
            b[a:z] *= 0.03

    def render(self, peak_db=-1.5, gain_db=0.0):
        x = sum(self.buses.values()) * (10 ** (gain_db / 20))
        x = limit(x, peak_db + 0.5)
        pk = np.max(np.abs(x)) + 1e-9
        target = 10 ** (peak_db / 20)
        if pk > target:
            x *= target / pk
        return x.astype(np.float32)


def limit(x, ceiling_db=-1.0, release=0.12):
    """Gentle peak limiter: instant attack (with 3 ms look-ahead), smooth release. No hard clipping."""
    c = 10 ** (ceiling_db / 20)
    need = np.maximum(1.0, np.abs(x) / c)
    look = int(0.003 * SR)
    need = np.maximum.accumulate(np.lib.stride_tricks.sliding_window_view(np.pad(need, (0, look)), look + 1).max(axis=1)[None])[0] if False else \
        np.max(np.lib.stride_tricks.sliding_window_view(np.pad(need, (0, look), constant_values=1.0), look + 1), axis=1)
    a = math.exp(-1.0 / (release * SR))
    g = signal.lfilter([1 - a], [1, -a], need).astype(np.float32)
    g = np.maximum(g, need)
    return (x / g).astype(np.float32)


def write_wav(path, x, stereo=True):
    y = np.clip(x, -1, 1)
    pcm = (y * 32767).astype(np.int16)
    if stereo:
        pcm = np.repeat(pcm[:, None], 2, axis=1)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2 if stereo else 1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def phone_levels(x, scenes):
    """Loudness per scene as a phone hears it: 300 Hz high-pass, RMS dBFS of the active parts."""
    y = hp(x, 300, 4)
    rows = []
    for name, t0, t1 in scenes:
        seg = y[int(t0 * SR):int(t1 * SR)]
        if len(seg) == 0:
            continue
        frames = seg[: len(seg) // 2400 * 2400].reshape(-1, 2400)
        r = np.sqrt(np.mean(frames ** 2, axis=1) + 1e-12)
        act = r[r > 10 ** (-55 / 20)]
        db = 20 * np.log10(np.sqrt(np.mean(act ** 2))) if len(act) else -99
        rows.append((name, t0, t1, round(float(db), 1)))
    return rows
