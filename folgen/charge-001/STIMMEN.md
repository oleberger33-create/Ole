# Neue Stimmen für Charge 001 (ElevenLabs über IMG.LY)

**Stand: erledigt.** Alle 111 Zeilen liegen als ElevenLabs-Stimmen in `stimmen/`, die Folge ist damit gebaut
(1920×1080, 60 fps, 9:35, −14 LUFS). Die lokalen Piper-Stimmen bleiben nur als Rückfall, wenn `STIMMEN_EXTERN` fehlt.

## Neu bauen

```sh
STIMMEN_EXTERN=$PWD/folgen/charge-001/stimmen WORKERS=4 \
  folgen/charge-001/produktion/produce.sh <arbeitsordner> <tts-modelle> <schriften>
```

- Mit externen Stimmen werden keine Piper-Modelle geladen; `<tts-modelle>` darf ein leerer Ordner sein. Nötig ist `scipy`.
- `<schriften>` braucht `BagelFatOne-400.ttf`, `RethinkSans-600.ttf`, `RethinkSans-800.ttf`, `DMMono-400.ttf`, `DMMono-500.ttf`
  (Google Fonts; Rethink Sans gibt es nur variabel, statisch per `fonttools varLib.instancer RethinkSans[wght].ttf wght=800`).
- Rendern dauert mit 4 Workern rund 25 Minuten, das fertige MP4 (CRF 18) ist etwa 300 MB groß.
- `stimmen/elevenlabs.json` hält Stimme und Prompt (samt Audio-Tag) jeder Zeile. Eine Zeile neu erzeugen:
  Prompt dort ändern, mit `asset_generate` neu generieren, MP3 unter demselben Namen ablegen, neu bauen.
  Wird der Text einer Zeile in `episode.py` geändert, ändert sich ihr Schlüssel: `stimmen_extern.py liste` neu laufen lassen.

## Ergebnis des Laufs

- Laufzeit 8:07 → 9:35. Die neuen Stimmen sprechen langsamer und mit mehr Pausen; Kapitel, Endcard (ab 9:15),
  Untertitel und Drehbuch sind neu berechnet.
- Stichproben mit `elevenlabs/scribe-v2`: Deutsch erkannt, Audio-Tags werden nicht mitgesprochen.
  KURTs Abbrüche („Auftrag ausgef…“, „Auftrag verst…“) enden wirklich mitten im Wort.
- `build.py` schreibt die Stimmen-Angabe in `youtube.md` jetzt passend (ElevenLabs statt Piper, sobald `STIMMEN_EXTERN` gesetzt ist).
- Kosten: 111 Zeilen zu je vorläufig 26,8 Credits, also gut 3.000 Credits (≈ 3 $). Jede Zeile kostet gleich viel, egal wie lang.

---

# Ursprüngliche Anleitung

## Voraussetzungen in der Cloud-Umgebung

1. **Netzwerkzugriff → Erlaubte Domains:** `clerk.img.ly`, `gateway.img.ly`, `cdn.img.ly`, `mcp.img.ly` (erledigt)
2. **Umgebungsvariable:** `NODE_USE_ENV_PROXY=1`. Ohne sie nutzt der IMG.LY-Dienst (Node) den Proxy nicht, und die Anmeldung scheitert mit „token endpoint unreachable“. Wird erst in einer **neuen Sitzung** wirksam.

## Ablauf in der neuen Sitzung

1. IMG.LY anmelden: `login`-Werkzeug aufrufen, Link öffnen, anmelden. Die Adresse der Fehlerseite (`http://127.0.0.1:<port>/callback?code=…`) zurück in den Chat geben; sie wird in der Umgebung per `curl` aufgerufen.
2. Zeilenliste erzeugen:
   `python3 produktion/stimmen_extern.py liste <ordner>` → `<ordner>/zeilen.json` (111 Zeilen, 4.870 Zeichen)
3. Jede Zeile mit `asset_generate`, Modell `elevenlabs/eleven-v3-tts`, erzeugen (Stimme pro Figur, siehe unten). Die MP3 als `<ordner>/<who>_<key>.mp3` speichern (`who` und `key` stehen in `zeilen.json`).
4. Bauen und rendern:
   `STIMMEN_EXTERN=<ordner> WORKERS=4 produktion/produce.sh <arbeitsordner> <tts-modelle> <schriften>`
   `build.py` nimmt dann die externen Dateien statt Piper. Mund, Timing, Untertitel und Drehbuch passen sich automatisch an.

## Stimmen je Figur (Vorschlag, vor dem Lauf mit `schema: true` prüfen)

| Figur | Charakter | ElevenLabs-Stimme | Hinweise |
| --- | --- | --- | --- |
| Fussel (F) | jung, hell, aufgedreht | Jessica | Tags wie `[excited]`; leicht hochgepitcht |
| KURT (K) | ruhig, tief, Amtsdeutsch | Daniel | Roboterfilter kommt in `build.py` dazu |
| Brösel (B) | müde, brummig, berlinernd | Bill | Tags wie `[sighs]`, `[tired]` |
| Gurrmann (G) | munterer Zugbegleiter | Charlie | |
| Durchsage (A) | klar, sachlich | Matilda | Bahnhofshall kommt in `build.py` dazu |

Kosten laut IMG.LY-Doku: etwa 20 Credits pro Satz (1 Credit = 0,001 $), also rund 2–3 $ für die Folge. Tatsächlich: 26,8 Credits pro Zeile, siehe oben.
