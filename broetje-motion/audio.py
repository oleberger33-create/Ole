"""Sound design + score for the 30 s Brötje Handel Breuer KG spot.

Everything is synthesised (no samples, no licences) and every hit is placed on
the same cue times the animation uses in index.html.
Usage: python3 audio.py out.wav
"""
import sys, wave
import numpy as np

SR = 48000
DUR = 30.0
N = int(SR * DUR)
rng = np.random.default_rng(7)
L = np.zeros(N); R = np.zeros(N)


def t_arr(d):
    return np.arange(int(SR * d)) / SR


def place(sig, at, gain=1.0, pan=0.0):
    """Mix mono `sig` at time `at` (s) with constant-power pan (-1..1)."""
    i = int(at * SR)
    if i >= N:
        return
    s = sig[: N - i] * gain
    a = (pan + 1) * np.pi / 4
    L[i:i + len(s)] += s * np.cos(a)
    R[i:i + len(s)] += s * np.sin(a)


def place_st(sl, sr, at, gain=1.0):
    i = int(at * SR)
    n = min(len(sl), N - i)
    L[i:i + n] += sl[:n] * gain
    R[i:i + n] += sr[:n] * gain


def env(n, a, d, curve=4.0):
    """attack seconds, exponential-ish decay over the rest."""
    x = np.arange(n) / SR
    at = np.clip(x / max(a, 1e-4), 0, 1)
    dc = np.exp(-curve * np.clip(x - a, 0, None) / max(d, 1e-4))
    return at * dc


def lp(x, cutoff):
    """one-pole low-pass (cutoff may be an array)"""
    c = np.broadcast_to(np.asarray(cutoff, float), x.shape)
    k = 1 - np.exp(-2 * np.pi * c / SR)
    y = np.empty_like(x); acc = 0.0
    for i in range(len(x)):
        acc += k[i] * (x[i] - acc); y[i] = acc
    return y


def hp(x, cutoff):
    return x - lp(x, cutoff)


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)

# ------------------------------------------------------------------ sounds

def whoosh(d, f0=300, f1=6000, rise=True):
    n = int(SR * d)
    noise = rng.standard_normal(n)
    x = np.linspace(0, 1, n)
    shape = x ** 2.2 if rise else (1 - x) ** 2.2
    cut = f0 + (f1 - f0) * (x ** 2 if rise else (1 - x) ** 2)
    s = lp(noise, cut) - lp(noise, cut * 0.25)
    return s * shape / (np.abs(s).max() + 1e-9)


def impact(d=2.2, f=46):
    t = t_arr(d)
    freq = f + 70 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(freq) / SR
    body = np.sin(ph) * np.exp(-t * 2.6)
    click = rng.standard_normal(len(t)) * np.exp(-t * 90) * 0.35
    air = hp(rng.standard_normal(len(t)), 3000) * np.exp(-t * 7) * 0.12
    return np.tanh(1.6 * (body + click + air))


def kick(f=50):
    t = t_arr(0.45)
    freq = f + 110 * np.exp(-t * 35)
    s = np.sin(2 * np.pi * np.cumsum(freq) / SR) * np.exp(-t * 8)
    return np.tanh(2 * s)


def hat(open_=False):
    t = t_arr(0.25 if open_ else 0.06)
    return hp(rng.standard_normal(len(t)), 7000) * np.exp(-t * (18 if open_ else 70))


def blip(f, d=0.35, bright=1.0):
    t = t_arr(d)
    s = np.sin(2 * np.pi * f * t) + 0.25 * bright * np.sin(2 * np.pi * 2 * f * t) + 0.1 * np.sin(2 * np.pi * 3.01 * f * t)
    return s * env(len(t), 0.003, d)


def tick(f=2600):
    t = t_arr(0.03)
    return np.sin(2 * np.pi * f * t) * np.exp(-t * 220)


def pad_chord(notes, d, cutoff=1400, detune=0.07):
    """warm detuned saw pad, stereo"""
    t = t_arr(d)
    sl = np.zeros(len(t)); sr = np.zeros(len(t))
    for m in notes:
        for k, dt in enumerate((-detune, 0.0, detune)):
            f = midi(m + dt)
            ph = rng.random()
            saw = 2 * ((f * t + ph) % 1) - 1
            if k == 0: sl += saw
            elif k == 2: sr += saw
            else: sl += saw * .7; sr += saw * .7
    a = np.clip(t / 0.5, 0, 1) * np.clip((d - t) / 0.6, 0, 1)
    sl = lp(sl, cutoff) * a; sr = lp(sr, cutoff) * a
    g = 1 / (len(notes) * 2.4)
    return sl * g, sr * g


def bass(m, d):
    t = t_arr(d)
    f = midi(m)
    s = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t)
    return s * np.clip(t / 0.01, 0, 1) * np.exp(-t * 1.6) * np.clip((d - t) / 0.05, 0, 1)


def reverb(x, secs=2.4, mix=0.25):
    n = int(SR * secs)
    t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-t * 6.9 / secs)
    ir = lp(ir, 5000); ir /= np.sqrt((ir ** 2).sum())
    m = len(x) + n
    nfft = 1 << (m - 1).bit_length()
    y = np.fft.irfft(np.fft.rfft(x, nfft) * np.fft.rfft(ir, nfft), nfft)[: len(x)]
    return x * (1 - mix) + y * mix * 3

# ------------------------------------------------------------------ score
BEAT = 0.5          # 120 bpm, one bar = 2 s
# D minor-ish uplift: Dm – Bb – F – C  (i–VI–III–VII), resolves to F major on the end card
PROG = [([62, 65, 69, 74], 38), ([58, 62, 65, 70], 34), ([57, 60, 65, 69], 41), ([55, 60, 64, 67], 36)]

# S1: intro — cold, sparse
place(whoosh(1.25, 200, 2500), 0.2, .22, -0.6)          # blue line
place(whoosh(1.15, 200, 2500), 0.3, .22, 0.6)           # red line
place(impact(2.4, 52), 1.4, .55)                         # lines meet
place(blip(midi(86), 1.4, .4), 1.4, .10)
for at, m, pn in ((1.45, 74, -.3), (2.05, 77, .3), (2.65, 81, 0)):   # Wasser / Wärme / Luft
    place(whoosh(.35, 800, 5000, rise=False), at, .07, pn)
    place(blip(midi(m), .9, .6), at + .05, .11, pn)
pl, pr = pad_chord([50, 57, 62, 65], 4.2, 900)
place_st(pl, pr, 0.0, .55)
place(whoosh(1.0, 300, 9000), 2.45, .32)                # riser into reveal
place(impact(2.6, 44), 3.45, .75)                       # circle reveal → S2

# S2 – S5: groove from 4.0 to 25.0
for bar in range(4, 25, 2):
    chord, root = PROG[(bar // 2 - 2) % 4]
    cl, cr = pad_chord(chord, 2.05, 1600 if bar >= 9 else 1100)
    place_st(cl, cr, bar, .5)
    for b in range(4):
        at = bar + b * BEAT
        if at >= 25.0: break
        place(kick(), at, .55 if b % 2 == 0 else .35)
        place(bass(root - 12, .45), at, .30)
        if at >= 9.0:
            place(hat(), at + BEAT / 2, .10, .35)
        if at >= 15.0 and b == 3:
            place(hat(True), at + BEAT / 2, .06, -.35)

# S2 type
for i in range(3):
    place(tick(2200 + i * 300), 4.15 + i * .085, .12, -.2 + i * .2)
place(whoosh(.6, 500, 4000), 5.15, .08)                 # red underline
# S3 wipe + tiles
place(whoosh(.7, 400, 7000), 7.95, .28)
place(impact(1.4, 60), 8.6, .35)
for i in range(4):
    place(tick(1800 + i * 250), 9.35 + i * .08, .16, -.6 + i * .4)
place(whoosh(1.1, 300, 3000), 10.25, .10)               # pipe draws
SPOT = [74, 77, 81, 86]
for i, m in enumerate(SPOT):
    place(blip(midi(m), .8, .8), 11.5 + i * .6, .14, -.6 + i * .4)
place(whoosh(.8, 600, 8000), 13.9, .22)
# S4 map
for at, m in ((15.25, 69), (16.05, 74), (16.55, 77)):
    place(blip(midi(m), 1.0, .5), at, .15)
    place(kick(70), at, .12)
place(whoosh(1.2, 200, 1800), 15.55, .12, .3)           # pipes flowing
for i in range(3):
    place(tick(2400), 16.9 + i * .12, .09)
place(whoosh(.9, 300, 9000), 19.15, .3)
place(impact(2.0, 48), 19.95, .6)                       # circle → light
# S5 odometer: decelerating ticks
tt = 20.55
while tt < 22.15:
    k = (tt - 20.55) / 1.6
    place(tick(3200 - 1200 * k), tt, .07 * (1 - .5 * k), rng.uniform(-.3, .3))
    tt += 0.025 + 0.11 * k ** 2
place(blip(midi(81), .7), 22.15, .12)
for i, s in enumerate((21.75, 22.35, 22.95, 23.55, 24.15)):
    place(tick(1500), s + .2, .16, .4)
    place(whoosh(.3, 900, 4000, rise=False), s, .04, .4)
# S6 end card
place(whoosh(1.3, 200, 9000), 24.4, .35)
place(whoosh(.9, 200, 2500), 25.5, .2, -.6)
place(whoosh(.85, 200, 2500), 25.58, .2, .6)
for i in range(22):
    place(tick(3000 + (i % 5) * 180), 25.75 + i * .028 + (.12 if i >= 13 else 0), .035, rng.uniform(-.5, .5))
place(impact(3.5, 41), 26.35, .85)
fl, fr = pad_chord([41, 53, 57, 60, 65, 69], 3.65, 2000, 0.09)   # F major, open voicing
place_st(fl, fr, 26.35, .9)
place(bass(29, 3.6), 26.35, .45)
for i, m in enumerate((77, 81, 84, 89)):
    place(blip(midi(m), 2.2, .3), 26.45 + i * .11, .07, -.45 + i * .3)

# ------------------------------------------------------------------ master
L[:] = reverb(L, 2.6, .28); R[:] = reverb(R, 2.9, .28)
fade = np.ones(N); fo = int(SR * 1.1); fade[-fo:] = np.linspace(1, 0, fo) ** 2
fi = int(SR * 0.05); fade[:fi] = np.linspace(0, 1, fi)
L *= fade; R *= fade
peak = max(np.abs(L).max(), np.abs(R).max())
L = np.tanh(1.2 * L / peak) * 0.89; R = np.tanh(1.2 * R / peak) * 0.89
out = (np.stack([L, R], 1) * 32767).astype('<i2')
with wave.open(sys.argv[1] if len(sys.argv) > 1 else 'score.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(out.tobytes())
print('ok', out.shape)
