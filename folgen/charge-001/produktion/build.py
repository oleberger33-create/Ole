"""Baut Ton, Zeitplan, Untertitel und Drehbuch für Charge 001.

Aufruf:  python3 build.py <ausgabeordner> <tts-modellordner>
"""
import hashlib
import json
import os
import subprocess
import sys
import wave

import numpy as np

import episode
import klang
from klang import SR

OUT = sys.argv[1] if len(sys.argv) > 1 else "out"
MODELS = sys.argv[2] if len(sys.argv) > 2 else "tts"
FPS = 12
os.makedirs(os.path.join(OUT, "stimmen"), exist_ok=True)

VOICES = {  # Figur: Modell, Sprecher-ID, Tempo, Tonhöhe, Formanten, Zusatzfilter
    "F": dict(model="de_DE-kerstin-low", sid=0, speed=1.0, pitch=1.30, formant="shifted",
              chain="highpass=f=160,acompressor=threshold=-20dB:ratio=3:attack=5:release=80"),
    "K": dict(model="de_DE-thorsten-medium", sid=0, speed=0.86, pitch=0.86, formant="shifted",
              chain="highpass=f=90", robot=True),
    "B": dict(model="de_DE-karlsson-low", sid=0, speed=0.84, pitch=0.90, formant="preserved",
              chain="lowpass=f=6500,acompressor=threshold=-20dB:ratio=2.5"),
    "G": dict(model="de_DE-thorsten_emotional-medium", sid=0, speed=1.15, pitch=1.13, formant="preserved",
              chain="vibrato=f=6.5:d=0.10"),
    "A": dict(model="de_DE-ramona-low", sid=0, speed=0.95, pitch=1.03, formant="preserved",
              chain="highpass=f=380,lowpass=f=3600,aecho=0.8:0.55:90|170:0.32|0.18"),
}
NAMES = {"F": "Fussel", "K": "KURT", "B": "Brösel", "G": "Gurrmann", "A": "Durchsage"}

_tts = {}


def tts_engine(model):
    if model not in _tts:
        import sherpa_onnx
        d = os.path.join(MODELS, f"vits-piper-{model}")
        cfg = sherpa_onnx.OfflineTtsConfig(
            model=sherpa_onnx.OfflineTtsModelConfig(
                vits=sherpa_onnx.OfflineTtsVitsModelConfig(
                    model=os.path.join(d, f"{model}.onnx"), tokens=os.path.join(d, "tokens.txt"),
                    data_dir=os.path.join(d, "espeak-ng-data")),
                num_threads=4),
            max_num_sentences=1)
        _tts[model] = sherpa_onnx.OfflineTts(cfg)
    return _tts[model]


def write_wav(path, x, sr):
    x = np.clip(x, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


def read_wav(path):
    with wave.open(path, "rb") as w:
        n, ch, sr = w.getnframes(), w.getnchannels(), w.getframerate()
        x = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32767
    if ch == 2:
        x = x.reshape(-1, 2).mean(axis=1)
    return x, sr


def trim(x, thr=0.012, pre=0.03, post=0.08):
    idx = np.where(np.abs(x) > thr * max(1e-6, np.abs(x).max()) * 3)[0]
    if len(idx) == 0:
        return x
    a = max(0, idx[0] - int(pre * SR))
    b = min(len(x), idx[-1] + int(post * SR))
    return x[a:b]


def voice(who, say, fx=None):
    v = VOICES[who]
    key = hashlib.sha1(json.dumps([v, say, fx, 3]).encode()).hexdigest()[:16]
    path = os.path.join(OUT, "stimmen", f"{who}_{key}.wav")
    if not os.path.exists(path):
        a = tts_engine(v["model"]).generate(say, sid=v["sid"], speed=v["speed"])
        raw = path + ".raw.wav"
        write_wav(raw, np.array(a.samples, dtype=np.float32), a.sample_rate)
        chain = f"rubberband=pitch={v['pitch']}:formant={v['formant']},aresample={SR}"
        if v.get("chain"):
            chain += "," + v["chain"]
        if fx == "kurt":    # Durchsage aus KURTs Lautsprecher
            chain = f"rubberband=pitch={v['pitch']}:formant=preserved,aresample={SR},highpass=f=500,lowpass=f=3000,aecho=0.8:0.4:40:0.3"
        if fx == "off":     # aus dem Off, hinter der Tür
            chain += ",lowpass=f=2200,aecho=0.8:0.35:60:0.25"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", raw, "-af", chain, "-ac", "1", path], check=True)
        os.remove(raw)
        x, _ = read_wav(path)
        x = trim(x)
        if v.get("robot"):
            t = np.arange(len(x)) / SR
            x = x * (0.72 + 0.28 * np.sin(2 * np.pi * 52 * t))
            d = int(0.007 * SR)
            y = x.copy()
            y[d:] += 0.45 * x[:-d]
            x = y
        if fx == "kurt":
            x = np.tanh(x * 3) / 3
        rms = np.sqrt(np.mean(x ** 2)) + 1e-9
        x = x * (0.1 / rms)
        if fx == "off":
            x *= 0.6
        peak = np.abs(x).max()
        if peak > 0.95:
            x *= 0.95 / peak
        write_wav(path, x, SR)
    x, _ = read_wav(path)
    return path, x


def envelope(x):
    hop = SR // FPS
    n = int(np.ceil(len(x) / hop))
    e = np.array([np.sqrt(np.mean(x[i * hop:(i + 1) * hop] ** 2)) if len(x[i * hop:(i + 1) * hop]) else 0 for i in range(n)])
    ref = np.percentile(e, 90) + 1e-9
    e = np.clip(e / ref, 0, 1)
    e[e < 0.18] = 0
    return [round(float(v) ** 0.7, 2) for v in e]


DEFAULTS = {
    "cam": dict(x=960, y=540, z=1, r=0),
    "fussel": dict(x=-500, y=900, s=0.8, r=0, flip=1, lx=0, ly=0, thread=1),
    "kurt": dict(x=860, y=900, s=1.6, shake=0),
    "broesel": dict(x=2200, y=900, s=1.25, r=0, flip=-1, lid=0.55, wing=0),
    "gurrmann": dict(x=2200, y=900, s=1.3, r=0, flip=-1, lid=0.2, wing=0),
    "train": dict(x=3000, y=740, s=1, r=0, doors=0),
    "ball": dict(x=0, y=0, s=1),
    "iris": dict(r=1200),
    "fade": dict(a=0),
    "logo": dict(p=0),
    "outside": dict(v=1),
}


def ease_ok(e):
    assert e in ("lin", "in", "out", "io"), e
    return e


class TL:
    def __init__(self):
        self.t = 0.0
        self.tracks, self.states = {}, {}
        self.lines, self.sfxs, self.musics, self.scenes, self.cues = [], [], [], [], {}
        self.chapters = []

    # -- Werkzeuge ---------------------------------------------------------
    def _value_at(self, actor, prop, t):
        segs = self.tracks.get(actor, {}).get(prop, [])
        val = DEFAULTS.get(actor, {}).get(prop, 0)
        for s in sorted(segs, key=lambda s: s[0]):
            if s[0] <= t:
                if t < s[1]:
                    u = (t - s[0]) / (s[1] - s[0])
                    val = s[2] + (s[3] - s[2]) * u
                else:
                    val = s[3]
        return val

    def key(self, actor, dur=0.0, off=0.0, ease="io", **props):
        t0 = round(self.t + off, 3)
        for p, v in props.items():
            frm = self._value_at(actor, p, t0)
            self.tracks.setdefault(actor, {}).setdefault(p, []).append([t0, round(t0 + dur, 3), frm, v, ease_ok(ease)])

    def shot(self, x, y, z, dur=0.0, ease="io", off=0.0):
        self.key("cam", dur=dur, off=off, ease=ease, x=x, y=y, z=z)

    def st(self, actor, off=0.0, **props):
        for p, v in props.items():
            self.states.setdefault(actor, {}).setdefault(p, []).append([round(self.t + off, 3), v])

    def scene(self, name):
        self.scenes.append([round(self.t, 3), name])

    def wait(self, sec):
        self.t += sec

    def chapter(self, name):
        self.chapters.append([round(self.t, 2), name])

    def cue(self, name):
        self.cues[name] = round(self.t, 3)

    def sfx(self, name, off=0.0, vol=1.0, dur=None):
        self.sfxs.append(dict(t=self.t + off, name=name, vol=vol, dur=dur))

    def music(self, name, vol, off=0.0):
        self.musics.append([self.t + off, name, vol])

    def line(self, who, text, say=None, gap=0.45, pre=0.0, fx=None):
        say = (say or text).replace("…", "...").replace("„", "").replace("“", "")
        path, x = voice(who, say, fx)
        self.t += pre
        d = len(x) / SR
        self.lines.append(dict(t0=round(self.t, 3), t1=round(self.t + d, 3), who=who, text=text,
                               file=path, env=envelope(x), fx=fx))
        self.t += d + gap


def main():
    tl = TL()
    episode.write(tl)
    end_start = [s for s in tl.scenes if s[1] == "endcard"][-1][0]
    total = max(tl.t, end_start + 20.0)
    total = round(total, 2)
    print(f"Laufzeit: {int(total // 60)}:{total % 60:05.2f}  (Endcard ab {end_start:.1f}s)")

    # ---- Ton mischen -----------------------------------------------------
    n = int((total + 1) * SR)
    voc = np.zeros(n)
    for l in tl.lines:
        x, _ = read_wav(l["file"])
        klang.place(voc, x, l["t0"])
    fx = np.zeros(n)
    for e in tl.sfxs:
        x = klang.sfx(e["name"], e["dur"])
        klang.place(fx, x, e["t"], e["vol"] * 0.55)
    mus = np.zeros(n)
    cues = sorted(tl.musics, key=lambda m: m[0]) + [[total + 1, "off", 0]]
    cache = {}
    for (t0, name, vol), (t1, _, _) in zip(cues, cues[1:]):
        if name == "off" or vol <= 0:
            continue
        if name not in cache:
            cache[name] = klang.theme(name)
        th = cache[name]
        ln = int((t1 - t0 + 0.8) * SR)
        reps = int(np.ceil(ln / len(th))) + 1
        seg = np.tile(th, reps)[:ln]
        e = np.ones(ln)
        fi, fo = int(0.3 * SR), int(0.8 * SR)
        e[:fi] = np.linspace(0, 1, fi)
        e[-fo:] = np.linspace(1, 0, fo)
        if name == "ende":   # Endcard: Musik läuft aus
            tail = int(3.0 * SR)
            e[-tail:] *= np.linspace(1, 0, tail)
        klang.place(mus, seg * e, t0, vol)
    # Musik unter Dialog absenken
    act = np.abs(voc)
    win = int(0.25 * SR)
    cs = np.concatenate([[0.0], np.cumsum(act)])
    lo = np.clip(np.arange(len(act)) - win // 2, 0, len(act))
    hi = np.clip(np.arange(len(act)) + win // 2, 0, len(act))
    act = (cs[hi] - cs[lo]) / win
    act = np.clip(act / 0.03, 0, 1)
    duck = 1 - 0.6 * act
    mix = voc * 1.0 + fx + mus * duck * 0.55
    mix = mix[: int(total * SR)]
    fade = int(0.8 * SR)
    mix[-fade:] *= np.linspace(1, 0, fade)
    stereo = np.stack([mix, mix], axis=1)
    peak = np.abs(stereo).max()
    stereo = stereo * (0.89 / peak)
    with wave.open(os.path.join(OUT, "mix.wav"), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((stereo * 32767).astype(np.int16).tobytes())

    # ---- Zeitplan für die Animation -------------------------------------
    for a in tl.tracks.values():
        for p in a:
            a[p].sort(key=lambda s: s[0])
    for a in tl.states.values():
        for p in a:
            a[p].sort(key=lambda s: s[0])
    tj = dict(fps=FPS, total=total, scenes=tl.scenes, tracks=tl.tracks, states=tl.states, cues=tl.cues,
              lines=[dict(t0=l["t0"], t1=l["t1"], who=l["who"], env=l["env"], fx=l["fx"]) for l in tl.lines],
              sfx=[dict(t=round(e["t"], 3), name=e["name"]) for e in tl.sfxs])
    with open(os.path.join(OUT, "timeline.json"), "w") as f:
        json.dump(tj, f)

    # ---- Untertitel ------------------------------------------------------
    def tc(t, sep=","):
        h, m, s = int(t // 3600), int(t % 3600 // 60), t % 60
        return f"{h:02d}:{m:02d}:{int(s):02d}{sep}{int(round((s % 1) * 1000)):03d}"
    srt = []
    for i, l in enumerate(tl.lines, 1):
        txt = l["text"]
        if l["who"] == "A":
            txt = "[Durchsage] " + txt
        srt.append(f"{i}\n{tc(l['t0'])} --> {tc(l['t1'] + 0.25)}\n{txt}\n")
    with open(os.path.join(OUT, "untertitel.srt"), "w") as f:
        f.write("\n".join(srt))

    # ---- Drehbuch --------------------------------------------------------
    labels = {"halle": "HALLE", "logo": "SOUND-LOGO", "titel": "TITEL", "filmtitel": "FILMTITEL (KURTs Bildschirm)",
              "bahnhof": "FILM · BAHNHOF BRÖTCHENHAUSEN", "zug": "FILM · IM ZUG", "himmel": "FILM · ÜBER DEN WOLKEN",
              "endcard": "ENDCARD"}
    ev = [(s[0], 0, f"\n### {tc(s[0], '.')[3:8]} · {labels.get(s[1], s[1])}\n") for s in tl.scenes]
    ev += [(l["t0"], 1, f"**{NAMES[l['who']]}{' (aus dem Off)' if l['fx'] == 'off' else ''}:** {l['text']}  ") for l in tl.lines]
    ev.sort(key=lambda e: (e[0], e[1]))
    md = [f"# Charge 001 · {episode.TITLE}\n",
          f"Laufzeit {int(total // 60)}:{int(total % 60):02d} · {len(tl.lines)} Dialogzeilen · "
          "Figuren: Fussel, KURT, Brösel, Zugbegleiter Gurrmann, Bahnhofsdurchsage\n",
          "Zeitangaben in Minuten:Sekunden, so wie sie im fertigen Video stehen."]
    last = None
    for t, kind, txt in ev:
        if kind == 0 and txt == last:
            continue
        md.append(txt)
        last = txt
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "drehbuch.md"), "w") as f:
        f.write("\n".join(md) + "\n")
    # ---- Upload-Text ----------------------------------------------------
    def mmss(t):
        return f"{int(t // 60)}:{int(t % 60):02d}"
    chap = "\n".join(f"{mmss(t) if i else '0:00'} {n}" for i, (t, n) in enumerate(tl.chapters))
    yt = f"""# YouTube-Upload · Charge 001

## Titel

{episode.TITLE}

## Beschreibung

```
Brösels Zug fällt mal wieder aus. Fussel hat sofort eine Idee: Was, wenn einfach die Tauben die Bahn übernehmen? KURT nimmt den Auftrag an. Wörtlich.

🧶 Charge 001 · Laufzeit {mmss(total)} · Ausschuss: geheim
Neue Charge jeden Freitag um 16 Uhr. Ein Abo ist wie eine Stempelkarte.

Dein Auftrag für KURT? Schreib ihn in die Kommentare. Vielleicht versteht er ihn diesmal richtig.

Kapitel
{chap}

Stimmen: KI-Sprachsynthese (Piper-Stimmen „Thorsten“ und „Kerstin“ von Thorsten-Voice, CC0; „Karlsson“ und „Ramona“ auf Basis des M-AILABS-Datensatzes)
Musik und Geräusche: selbst erzeugt in der Flausenfabrik
Ausgedacht in der Flausenfabrik.

#Animation #Comedy #Flausenfabrik
```

## Tags

Animation, Comedy, Zeichentrick, Kurzfilm, Was wäre wenn, Tauben, Bahn, Bahn-Humor, Flausenfabrik, Fussel, KURT, Brösel

## Einstellungen

- Zielgruppe: **Nein, nicht speziell für Kinder**
- Veränderte oder synthetische Inhalte: nicht erforderlich (klar erkennbare Animation, keine realen Personen)
- Kategorie: Comedy · Sprache: Deutsch
- Untertitel: `untertitel.srt` hochladen (Deutsch)
- Endcard ab {mmss(end_start)}: links Element „Video“ (nächstes Video), rechts Element „Abonnieren“ auf den Kreis mit Fussel
- Thumbnail: `assets/youtube/thumbnail-beispiel-und-was-wenn.png`
"""
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "youtube.md"), "w") as f:
        f.write(yt)
    print(f"{len(tl.lines)} Zeilen, {len(tl.sfxs)} Geräusche, {len(tl.scenes)} Szenenwechsel")


if __name__ == "__main__":
    main()
