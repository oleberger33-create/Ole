"""Holt hochwertige Stimmen von einem externen Dienst und legt sie so ab,
dass build.py sie statt der lokalen Piper-Stimmen verwendet.

  python3 stimmen_extern.py liste  <ordner>            # Zeilenliste als JSON (für jeden Dienst)
  python3 stimmen_extern.py google <ordner>            # Google Cloud TTS, Schlüssel in GOOGLE_TTS_KEY

Jede Datei heißt <Figur>_<Schlüssel>.wav; der Schlüssel hängt nur am gesprochenen
Text, nicht an der lokalen Stimme. build.py findet sie über STIMMEN_EXTERN=<ordner>.
"""
import base64
import hashlib
import json
import os
import sys
import urllib.request

import episode

# Google Chirp 3 HD, deutsche Stimmen je Figur
GOOGLE = {
    "F": dict(name="de-DE-Chirp3-HD-Leda", rate=1.08),     # Fussel: jung, hell, schnell
    "K": dict(name="de-DE-Chirp3-HD-Charon", rate=0.92),   # KURT: ruhig, tief, amtlich
    "B": dict(name="de-DE-Chirp3-HD-Algenib", rate=0.92),  # Brösel: rau, müde
    "G": dict(name="de-DE-Chirp3-HD-Puck", rate=1.05),     # Gurrmann: munter
    "A": dict(name="de-DE-Chirp3-HD-Kore", rate=1.0),      # Durchsage: klar, sachlich
}


def key_for(who, say):
    return hashlib.sha1(f"{who}|{say}".encode()).hexdigest()[:16]


def collect():
    lines = []

    class Dry:
        t = 0.0
        def __getattr__(self, _):
            return lambda *a, **k: None
        def line(self, who, text, say=None, gap=0.45, pre=0.0, fx=None):
            s = (say or text).replace("…", "...").replace("„", "").replace("“", "")
            lines.append(dict(who=who, text=text, say=s, fx=fx, key=key_for(who, s)))
    episode.write(Dry())
    return lines


def google(lines, out):
    api_key = os.environ.get("GOOGLE_TTS_KEY")
    if not api_key:
        sys.exit("GOOGLE_TTS_KEY fehlt")
    url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={api_key}"
    for i, l in enumerate(lines, 1):
        path = os.path.join(out, f"{l['who']}_{l['key']}.wav")
        if os.path.exists(path):
            continue
        v = GOOGLE[l["who"]]
        body = {"input": {"text": l["say"]},
                "voice": {"languageCode": "de-DE", "name": v["name"]},
                "audioConfig": {"audioEncoding": "LINEAR16", "sampleRateHertz": 48000, "speakingRate": v["rate"]}}
        req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as r:
            audio = base64.b64decode(json.loads(r.read())["audioContent"])
        with open(path, "wb") as f:
            f.write(audio)
        print(f"{i}/{len(lines)} {l['who']}: {l['text'][:50]}", flush=True)


if __name__ == "__main__":
    mode, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    lines = collect()
    if mode == "liste":
        json.dump(lines, open(os.path.join(out, "zeilen.json"), "w"), ensure_ascii=False, indent=1)
        print(len(lines), "Zeilen,", sum(len(l["say"]) for l in lines), "Zeichen")
    elif mode == "google":
        google(lines, out)
