"""Geräusche und Musik der Flausenfabrik, komplett synthetisch erzeugt.

Alles hier ist selbst gebaut (Sinus, Rauschen, Filter), damit es keine
Lizenzfragen gibt. Abtastrate 48 kHz, Mono, float32.
"""
import numpy as np
from scipy.signal import butter, sosfilt

SR = 48000
RNG = np.random.default_rng(7)


def T(d):
    return np.arange(int(d * SR)) / SR


def noise(d, seed=None):
    r = np.random.default_rng(seed) if seed is not None else RNG
    return r.uniform(-1, 1, int(d * SR))


def filt(x, kind, f, order=2):
    if kind == "bp":
        sos = butter(order, [f[0] / (SR / 2), f[1] / (SR / 2)], btype="band", output="sos")
    else:
        sos = butter(order, f / (SR / 2), btype={"lp": "low", "hp": "high"}[kind], output="sos")
    return sosfilt(sos, x)


def adsr(n, a=0.005, d=0.1, s=0.6, r=0.1, hold=None):
    a, d, r = int(a * SR), int(d * SR), int(r * SR)
    hold = n - a - d - r if hold is None else int(hold * SR)
    hold = max(hold, 0)
    e = np.concatenate([np.linspace(0, 1, a, endpoint=False), np.linspace(1, s, d, endpoint=False),
                        np.full(hold, s), np.linspace(s, 0, r)])
    return np.pad(e, (0, max(0, n - len(e))))[:n]


def expdec(d, tau, a=0.002):
    t = T(d)
    e = np.exp(-t / tau)
    na = max(1, int(a * SR))
    e[:na] *= np.linspace(0, 1, na)
    return e


def place(buf, x, t, vol=1.0):
    i = int(t * SR)
    if i < 0:
        x, i = x[-i:], 0
    if i >= len(buf) or len(x) == 0:
        return
    j = min(len(buf), i + len(x))
    buf[i:j] += x[: j - i] * vol


def add(*xs):
    n = max(len(x) for x in xs)
    return sum(np.pad(x, (0, n - len(x))) for x in xs)


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def norm(x, peak=0.9):
    m = np.max(np.abs(x)) if len(x) else 0
    return x * (peak / m) if m > 0 else x


# ---------------------------------------------------------------------------
# Instrumente
# ---------------------------------------------------------------------------
def marimba(f, d=0.6):
    t = T(d)
    x = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.35) + 0.25 * np.sin(2 * np.pi * f * 3.93 * t) * np.exp(-t / 0.08)
    x[:120] *= np.linspace(0, 1, 120)
    return x


def pluck(f, d=0.5, tau=0.22):
    t = T(d)
    x = sum(a * np.sin(2 * np.pi * f * k * t) for k, a in [(1, 1), (2, .5), (3, .25), (4, .12)])
    return x * expdec(d, tau, 0.003)


def tuba(f, d=0.4):
    t = T(d)
    x = np.sin(2 * np.pi * f * t) + 0.45 * np.sin(2 * np.pi * 2 * f * t) + 0.2 * np.sin(2 * np.pi * 3 * f * t)
    return x * adsr(len(t), 0.012, 0.12, 0.55, 0.12)


def clarinet(f, d=0.4):
    t = T(d)
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.2 * t)
    ph = 2 * np.pi * f * np.cumsum(vib) / SR
    x = np.sin(ph) + 0.45 * np.sin(3 * ph) + 0.25 * np.sin(5 * ph) + 0.12 * np.sin(7 * ph)
    return x * adsr(len(t), 0.03, 0.08, 0.8, 0.08)


def glock(f, d=1.2):
    t = T(d)
    x = (np.sin(2 * np.pi * f * t) * np.exp(-t / 0.6) + 0.4 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / 0.25)
         + 0.2 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t / 0.1))
    x[:60] *= np.linspace(0, 1, 60)
    return x


def pad(fs, d):
    t = T(d)
    x = np.zeros_like(t)
    for f in fs:
        for det in (-0.6, 0.6):
            x += np.sin(2 * np.pi * (f + det) * t) + 0.3 * np.sin(2 * np.pi * 2 * (f + det) * t)
    return x / (2 * len(fs)) * adsr(len(t), 0.25, 0.2, 0.8, 0.3)


def shaker(d=0.06, seed=None):
    return filt(noise(d, seed), "hp", 5000) * expdec(d, 0.02, 0.001)


def woodblock(f=1300):
    t = T(0.08)
    return (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 1.48 * t)) * np.exp(-t / 0.018)


def kick():
    t = T(0.25)
    f = 50 + 70 * np.exp(-t / 0.04)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.09)


def brush(d=0.12):
    return filt(noise(d), "bp", (1500, 7000)) * expdec(d, 0.05, 0.004)


# ---------------------------------------------------------------------------
# Musikstücke (Schleifen)
# ---------------------------------------------------------------------------
CH = {"C": [48, 52, 55], "G": [43, 47, 50], "Am": [45, 48, 52], "F": [41, 45, 48], "Dm": [50, 53, 57],
      "E": [40, 44, 47], "Bb": [46, 50, 53], "D": [50, 54, 57], "A": [45, 49, 52], "Bm": [47, 50, 54],
      "Em": [52, 55, 59]}

MOTIF = [  # (midi, beat, dauer) – Erkennungsmelodie der Flausenfabrik in C
    (76, 0, .5), (79, .5, .5), (84, 1, 1), (79, 2, .5), (76, 2.5, .5), (79, 3, 1),
    (74, 4, .5), (79, 4.5, .5), (83, 5, 1), (81, 6, .5), (79, 6.5, .5), (74, 7, 1),
    (72, 8, .5), (76, 8.5, .5), (81, 9, 1), (79, 10, .5), (76, 10.5, .5), (72, 11, 1),
    (81, 12, .5), (79, 12.5, .5), (77, 13, 1), (76, 14, .5), (74, 14.5, .5), (72, 15, 1),
    (76, 16, .5), (79, 16.5, .5), (84, 17, 1), (79, 18, .5), (76, 18.5, .5), (79, 19, 1),
    (71, 20, .5), (74, 20.5, .5), (79, 21, 1), (77, 22, .5), (74, 22.5, .5), (71, 23, 1),
    (81, 24, 1), (79, 25, .5), (77, 25.5, .5), (76, 26, 1), (74, 27, 1),
    (72, 28, 1), (67, 29, .5), (72, 29.5, .5), (76, 30, 1), (72, 31, 1),
]


def oompah(prog, bpm, bars_per_chord=1, beats=4, melody=None, mel_inst=marimba, transpose=0,
           mel_vol=0.5, swing=0.0, shake=True, perc=True):
    spb = 60 / bpm
    nbeats = len(prog) * bars_per_chord * beats
    out = np.zeros(int((nbeats * spb + 2) * SR))
    for i, ch in enumerate(prog):
        notes = [n + transpose for n in CH[ch]]
        for b in range(bars_per_chord * beats):
            t0 = (i * bars_per_chord * beats + b) * spb
            if b % 2 == 0:
                root = notes[0] - 12 if (b // 2) % 2 == 0 else notes[2] - 24
                place(out, tuba(mtof(root), spb * 0.9), t0, 0.55)
            else:
                for n in notes:
                    place(out, pluck(mtof(n + 12), spb * 0.6, 0.12), t0 + swing * spb, 0.16)
            if shake:
                place(out, shaker(0.06), t0, 0.12)
                place(out, shaker(0.05), t0 + spb * (0.5 + swing), 0.07)
            if perc and b % beats == beats - 1:
                place(out, woodblock(), t0, 0.12)
    if melody:
        for m, b, d in melody:
            bb = b + (swing if (b * 2) % 2 == 1 else 0)
            place(out, mel_inst(mtof(m + transpose), max(d * spb * 1.4, 0.3)), bb * spb, mel_vol)
    return out[: int(nbeats * spb * SR)]


def theme(name):
    if name == "halle":
        a = oompah(["C", "G", "Am", "F", "C", "G", "F", "C"], 112, melody=MOTIF)
        b = oompah(["C", "G", "Am", "F", "C", "G", "F", "C"], 112, melody=None)
        return norm(np.concatenate([a, b]), 0.8)
    if name == "ende":
        return norm(oompah(["C", "G", "Am", "F", "C", "G", "F", "C"], 112, melody=MOTIF, mel_vol=0.65), 0.85)
    if name == "bahnhof":
        mel = [(m - 7, b, d) for m, b, d in MOTIF]
        a = oompah(["F", "C", "Dm", "Bb", "F", "C", "Bb", "F"], 100, melody=mel, mel_inst=clarinet,
                   transpose=0, mel_vol=0.32, swing=0.16)
        b = oompah(["F", "C", "Dm", "Bb", "F", "C", "Bb", "F"], 100, swing=0.16)
        return norm(np.concatenate([a, b]), 0.8)
    if name == "zug":
        bpm = 126
        spb = 60 / bpm
        prog = ["D", "A", "Bm", "G"] * 2
        out = np.zeros(int((len(prog) * 4 * spb + 2) * SR))
        for i, ch in enumerate(prog):
            notes = CH.get(ch, CH["D"])
            for b in range(8):
                t0 = (i * 4 + b / 2) * spb
                place(out, shaker(0.05), t0, 0.14 if b % 2 == 0 else 0.07)
                n = notes[[0, 1, 2, 1][b % 4]] + 24
                place(out, marimba(mtof(n), 0.4), t0, 0.22)
            place(out, tuba(mtof(notes[0] - 12), spb * 1.8), i * 4 * spb, 0.5)
            place(out, tuba(mtof(notes[2] - 24), spb * 1.8), (i * 4 + 2) * spb, 0.45)
        return norm(out[: int(len(prog) * 4 * spb * SR)], 0.8)
    if name == "himmel":
        bpm = 138
        spb = 60 / bpm
        prog = ["G", "D", "Em", "C"] * 2
        out = np.zeros(int((len(prog) * 6 * spb + 3) * SR))
        mel = [79, 83, 86, 83, 81, 78, 79, 76, 74, 76, 79, 81, 83, 79, 76, 74]
        for i, ch in enumerate(prog):
            key = {"G": [55, 59, 62], "D": [50, 54, 57], "Em": [52, 55, 59], "C": [48, 52, 55]}[ch]
            for bar in range(2):
                t0 = (i * 6 + bar * 3) * spb
                place(out, tuba(mtof(key[0] - 12), spb * 0.9), t0, 0.45)
                for k in (1, 2):
                    for n in key:
                        place(out, pluck(mtof(n + 12), 0.3, 0.1), t0 + k * spb, 0.11)
            place(out, pad([mtof(n + 12) for n in key], spb * 6), i * 6 * spb, 0.18)
            m = mel[(i * 2) % len(mel)]
            place(out, glock(mtof(m), 1.4), i * 6 * spb, 0.35)
            place(out, glock(mtof(mel[(i * 2 + 1) % len(mel)]), 1.2), (i * 6 + 3) * spb, 0.3)
        return norm(out[: int(len(prog) * 6 * spb * SR)], 0.8)
    if name == "spannung":
        bpm = 104
        spb = 60 / bpm
        out = np.zeros(int((16 * 4 * spb + 2) * SR))
        seq = [45, 45, 52, 45, 48, 45, 52, 47]
        for b in range(16 * 4 * 2):
            t0 = b * spb / 2
            place(out, pluck(mtof(seq[b % 8] - 12), 0.25, 0.08), t0, 0.5)
            if b % 2 == 0:
                place(out, woodblock(1800 if b % 4 == 0 else 1500), t0, 0.08)
            if b % 8 == 0:
                place(out, kick(), t0, 0.5)
        return norm(out[: int(16 * 4 * spb * SR)], 0.8)
    if name == "chaos":
        mel = [(m - 3, b, d) for m, b, d in MOTIF]
        a = oompah(["Am", "E", "Am", "E", "Dm", "Am", "E", "Am"], 152, melody=mel, mel_inst=clarinet,
                   mel_vol=0.3)
        return norm(a, 0.85)
    raise ValueError(name)


# ---------------------------------------------------------------------------
# Geräusche
# ---------------------------------------------------------------------------
def click_burst(n, rate, d_click=0.012, f=(800, 3500), jitter=0.15, seed=1):
    r = np.random.default_rng(seed)
    out = np.zeros(int((n / rate + 0.1) * SR))
    for i in range(n):
        c = filt(noise(d_click, seed + i), "bp", f) * expdec(d_click, d_click / 3, 0.0005)
        place(out, c, i / rate + r.uniform(-jitter, jitter) / rate, r.uniform(0.6, 1))
    return out


def bell(f=1568, d=1.6):
    t = T(d)
    x = sum(a * np.sin(2 * np.pi * f * k * t) * np.exp(-t / tau)
            for k, a, tau in [(1, 1, .7), (2.0, .35, .4), (2.76, .3, .25), (5.4, .15, .1)])
    x[:30] *= np.linspace(0, 1, 30)
    return x


def coo(f0=420, d=0.55, seed=0):
    r = np.random.default_rng(seed)
    t = T(d)
    f = f0 * (1 + 0.12 * np.sin(np.pi * t / d)) * (1 + 0.02 * np.sin(2 * np.pi * 24 * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) + 0.4 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph)
    am = 0.55 + 0.45 * np.sin(2 * np.pi * r.uniform(14, 20) * t) ** 2
    e = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 0.7
    return filt(x * am * e, "lp", 2200)


def flap(seed=0):
    return filt(noise(0.09, seed), "bp", (300, 2500)) * expdec(0.09, 0.03, 0.004)


def sweep(f0, f1, d, kind="sine"):
    t = T(d)
    f = f0 * (f1 / f0) ** (t / d)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) if kind == "sine" else np.sign(np.sin(ph))


def sfx(name, dur=None):
    d = dur
    if name == "tuer":
        x = filt(noise(0.35), "lp", 900) * expdec(0.35, 0.08)
        return np.concatenate([x * 0.4, np.zeros(int(0.25 * SR)), add(kick() * 0.9, filt(noise(0.25), "lp", 500) * expdec(0.25, 0.05) * 0.5)])
    if name == "sparkle":
        out = np.zeros(int(1.0 * SR))
        for i, m in enumerate([84, 88, 91, 96]):
            place(out, glock(mtof(m), 0.7), i * 0.07, 0.35)
        return out
    if name in ("ratter", "kurbel"):
        n = int((d or (0.9 if name == "ratter" else 2.0)) * (14 if name == "ratter" else 9))
        return click_burst(n, 14 if name == "ratter" else 9, seed=3 if name == "ratter" else 11) * (1 if name == "ratter" else 0.6)
    if name == "ratterpling":
        out = np.zeros(int(3.6 * SR))
        place(out, click_burst(7, 16, seed=5), 0.0, 0.9)
        place(out, click_burst(7, 16, seed=9), 0.6, 0.9)
        place(out, bell(1568, 2.2), 2.25, 0.8)
        place(out, bell(2349, 1.6), 2.25, 0.25)
        return out
    if name == "stamp":
        return add(kick() * 0.9, filt(noise(0.15), "lp", 1800) * expdec(0.15, 0.03) * 0.6)
    if name == "stempeluhr":
        out = np.zeros(int(1.4 * SR))
        place(out, sfx("stamp"), 0.0)
        place(out, click_burst(3, 30, seed=21), 0.08, 0.8)
        place(out, bell(2093, 1.2), 0.18, 0.5)
        return out
    if name == "boing":
        t = T(0.35)
        f = 220 * (1 + 2.2 * (t / 0.35)) * (1 + 0.06 * np.sin(2 * np.pi * 18 * t))
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * expdec(0.35, 0.14) * 0.6
    if name == "hop":
        return add(kick() * 0.6, filt(noise(0.06), "lp", 1200) * expdec(0.06, 0.015) * 0.4)
    if name == "boot":
        out = np.zeros(int(1.4 * SR))
        place(out, sweep(180, 900, 0.6) * adsr(int(0.6 * SR), 0.02, 0.1, 0.7, 0.1) * 0.35, 0)
        for i, f in enumerate([880, 1175, 1568]):
            t = T(0.09)
            place(out, np.sign(np.sin(2 * np.pi * f * t)) * 0.12, 0.7 + i * 0.13)
        return out
    if name == "aus":
        return sweep(700, 60, 0.7) * expdec(0.7, 0.3) * 0.4
    if name in ("swish", "whoosh", "iris", "abheben"):
        ln = {"swish": 0.35, "whoosh": 1.0, "iris": 0.8, "abheben": 2.5}[name]
        t = T(ln)
        e = np.sin(np.pi * t / ln) ** 2
        x = noise(ln)
        lo, hi = (1500, 6000) if name == "swish" else (300, 3000)
        return filt(x, "bp", (lo, hi)) * e * (0.5 if name != "abheben" else 0.6)
    if name == "plopp":
        return sweep(700, 140, 0.18) * expdec(0.18, 0.06) * 0.7
    if name == "blip":
        t = T(0.12)
        return np.sign(np.sin(2 * np.pi * 1320 * t)) * expdec(0.12, 0.04) * 0.15
    if name == "fall":
        return sweep(1400, 300, 0.6) * adsr(int(0.6 * SR), 0.01, 0.1, 0.8, 0.1) * 0.25
    if name == "gong":   # Drei-Ton-Gong vor jeder Durchsage
        out = np.zeros(int(2.4 * SR))
        for i, m in enumerate([76, 72, 67]):
            place(out, add(bell(mtof(m), 1.6) * 0.6, glock(mtof(m), 1.2) * 0.2), i * 0.34)
        return out
    if name == "klacker":
        return click_burst(18, 40, d_click=0.008, f=(1200, 6000), seed=13) * 0.7
    if name == "schuettel":
        return click_burst(14, 12, d_click=0.03, f=(200, 1500), seed=17) * 0.8
    if name in ("gurren", "gurren_laut"):
        n = 6 if name == "gurren" else 16
        ln = 2.0 if name == "gurren" else 2.4
        out = np.zeros(int((ln + 0.6) * SR))
        r = np.random.default_rng(31 if name == "gurren" else 33)
        for i in range(n):
            place(out, coo(r.uniform(330, 520), r.uniform(0.4, 0.7), seed=i), r.uniform(0, ln), r.uniform(0.3, 0.6))
        return out
    if name == "gurr1":
        return coo(400, 0.7, 3) * 0.7
    if name == "fluegel":
        ln = d or 1.5
        out = np.zeros(int((ln + 0.2) * SR))
        r = np.random.default_rng(41)
        tt = 0.0
        while tt < ln:
            place(out, flap(int(tt * 100)), tt, r.uniform(0.3, 0.7))
            tt += r.uniform(0.05, 0.12)
        return out * 0.8
    if name in ("zug_ein", "zug_aus", "zug_fahrt"):
        ln = {"zug_ein": 5.5, "zug_aus": 4.2}.get(name, d or 10)
        t = T(ln)
        rumble = filt(noise(ln), "lp", 220) * 1.6
        out = rumble.copy()
        # Schienenstöße: "ta-dam"
        if name == "zug_ein":
            speed = np.maximum(0.05, 1 - t / ln) ** 0.8
        elif name == "zug_aus":
            speed = np.minimum(1, 0.1 + t / ln)
        else:
            speed = np.ones_like(t) * 0.8
        pos = np.cumsum(speed) / SR * 4.0
        hits = np.where(np.diff(np.floor(pos)) > 0)[0]
        for h in hits:
            for k in (0, 0.11):
                place(out, add(kick() * 0.5, filt(noise(0.05), "bp", (400, 2500)) * expdec(0.05, 0.012) * 0.6), h / SR + k, 0.6)
        if name == "zug_ein":
            sq = sweep(3200, 2900, 1.6) * (1 + 0.2 * np.sin(2 * np.pi * 7 * T(1.6)))
            place(out, sq * adsr(len(sq), 0.2, 0.2, 0.6, 0.4) * 0.12, ln - 2.0)
        vol = np.ones_like(t)
        if name == "zug_ein":
            vol = np.minimum(1, t / 1.5) * np.clip((ln - t) / 0.6, 0, 1)
        if name == "zug_aus":
            vol = np.clip((ln - t) / 2.0, 0, 1)
        if name == "zug_fahrt":
            vol = np.minimum(1, t / 1.0) * np.clip((ln - t) / 1.0, 0, 1)
        return out * vol * 0.6
    if name == "tuer_auf" or name == "tuer_zu":
        x = filt(noise(0.7), "hp", 1500) * adsr(int(0.7 * SR), 0.02, 0.1, 0.5, 0.4) * 0.35
        if name == "tuer_zu":
            x = np.concatenate([x * 0.6, kick() * 0.6])
        return x
    if name == "bremse":
        sq = sweep(3000, 2600, 1.4) * (1 + 0.3 * np.sin(2 * np.pi * 9 * T(1.4)))
        return add(sq * adsr(len(sq), 0.15, 0.2, 0.6, 0.4) * 0.09, filt(noise(1.4), "lp", 250) * expdec(1.4, 0.6) * 0.8)
    if name == "fehler":
        t = T(0.4)
        return np.sign(np.sin(2 * np.pi * 140 * t)) * adsr(len(t), 0.005, 0.05, 0.8, 0.05) * 0.18
    if name == "grille":
        out = np.zeros(int(2.2 * SR))
        for k in range(4):
            t = T(0.25)
            chirp = np.sin(2 * np.pi * 4200 * t) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 45 * t))) * np.sin(np.pi * t / 0.25)
            place(out, chirp * 0.08, k * 0.55)
        return out
    if name == "seufzer":
        ln = 1.2
        t = T(ln)
        e = np.sin(np.pi * t / ln) ** 1.5
        return filt(noise(ln), "bp", (300, 1800)) * e * np.exp(-t / 0.8) * 0.5
    if name == "wind":
        ln = d or 10
        t = T(ln)
        mod = 0.6 + 0.4 * np.sin(2 * np.pi * 0.23 * t) * np.sin(2 * np.pi * 0.07 * t)
        e = np.minimum(1, t / 1.5) * np.clip((ln - t) / 1.5, 0, 1)
        return filt(noise(ln), "bp", (200, 1200)) * mod * e * 0.7
    if name == "glitch":
        out = np.zeros(int(0.9 * SR))
        r = np.random.default_rng(5)
        for i in range(10):
            f = r.uniform(200, 2000)
            seg = np.sign(np.sin(2 * np.pi * f * T(0.05))) * 0.15
            place(out, seg, i * 0.08)
        return out
    if name == "alarm":
        ln = d or 5
        t = T(ln)
        f = np.where((t % 0.8) < 0.4, 880, 660)
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.3 * np.sin(4 * np.pi * np.cumsum(f) / SR)
        return x * 0.12 * np.minimum(1, (ln - t) / 0.5)
    if name == "explosion_weich":
        ln = 1.2
        x = filt(noise(ln), "lp", 700) * expdec(ln, 0.3, 0.01)
        out = np.zeros(int(ln * SR))
        place(out, x, 0, 1.0)
        place(out, kick(), 0, 1.0)
        return out
    if name == "picken":
        return click_burst(int((d or 2) * 7), 7, d_click=0.015, f=(600, 3000), seed=55) * 0.6
    if name == "hebel":
        return np.concatenate([click_burst(3, 25, seed=61) * 0.7, kick() * 0.8])
    if name == "band":
        ln = d or 8
        t = T(ln)
        hum = np.sin(2 * np.pi * 55 * t) * 0.3 + np.sin(2 * np.pi * 110 * t) * 0.15
        rattle = click_burst(int(ln * 6), 6, d_click=0.02, f=(300, 1200), seed=71)[: len(t)]
        rattle = np.pad(rattle, (0, len(t) - len(rattle)))
        e = np.minimum(1, t / 0.6) * np.clip((ln - t) / 0.6, 0, 1)
        return (hum + rattle * 0.5) * e * 0.6
    if name == "fegen":
        ln = d or 8
        out = np.zeros(int((ln + 0.3) * SR))
        tt = 0.0
        while tt < ln:
            s = filt(noise(0.35), "bp", (1500, 6000)) * np.sin(np.pi * T(0.35) / 0.35) ** 2 * 0.3
            place(out, s, tt)
            tt += 0.6
        return out
    raise ValueError(name)
