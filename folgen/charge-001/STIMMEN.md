# Neue Stimmen für Charge 001 (ElevenLabs über IMG.LY)

Stand: Animation fertig (60 fps, geprüft). Es fehlen nur noch hochwertige Stimmen.
Die lokalen Piper-Stimmen sind Platzhalter.

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

Kosten laut IMG.LY-Doku: etwa 20 Credits pro Satz (1 Credit = 0,001 $), also rund 2–3 $ für die Folge.
