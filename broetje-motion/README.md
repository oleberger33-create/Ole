# Brötje Handel Breuer KG – Motion-Spot (30 s)

Ein 30-Sekunden-Spot in 1920×1080 mit 60 fps. Bild und Ton sind komplett im Code gebaut: Es gibt kein Stockmaterial und keine Samples.

| Datei | Wofür |
| --- | --- |
| `index.html` | Die Animation. Im Browser öffnen, dann läuft sie mit Scrubber (Leertaste = Pause). |
| `render.js` | Exportiert die einzelnen Bilder ohne Zeitabweichung: `node render.js <ordner> 60 <worker> <anzahl>` |
| `audio.py` | Sounddesign und Musik (numpy), auf dieselben Zeitpunkte gelegt wie die Animation |
| `stills.js` | Einzelbilder zum Prüfen: `node stills.js <ordner> 3.5 12 26.8` |
| `broetje-handel-breuer-30s.mp4` | Das fertige Video |

## Dramaturgie

| Zeit | Szene | Idee |
| --- | --- | --- |
| 0–4 s | **Wasser. Wärme. Luft.** | Eine blaue und eine rote Leitung treffen sich in der Bildmitte. Aus dem Treffpunkt öffnet sich die nächste Szene. |
| 4–9 s | **Gebäudetechnik, die verbindet.** | Markenblau, Leitungsnetz, Kinetic Type |
| 9–15 s | **Sortiment** | Vier Kacheln mit Icons, die sich selbst zeichnen. Ein Spotlight geht im Takt der Musik von Kachel zu Kachel. |
| 15–20 s | **Standorte** | Minden, Löhne und Lübbecke, ungefähr an ihrer echten geografischen Lage. Sie sind mit Vorlauf- und Rücklaufleitungen verbunden. |
| 20–25 s | **600 m² ELEMENTS-Ausstellung + Service** | Zählwerk mit Bewegungsunschärfe aus der Geschwindigkeit, dazu ein 3D-Rad mit den Serviceleistungen |
| 25–30 s | **Endcard** | Dasselbe Leitungsmotiv wie am Anfang, Wortmarke Buchstabe für Buchstabe, Claim „Einfach nah dran.“ |

## Motion-Prinzipien (Skill emil-design-eng)

- Eigene Kurven statt CSS-Standard: `ease-out (0.23, 1, 0.32, 1)` für Auftritte, `ease-in-out (0.77, 0, 0.175, 1)` für Bewegungen und Übergänge.
- Nichts startet bei `scale(0)`: Auftritte beginnen bei 0.96 und kommen mit Opacity und Blur.
- Federn nach Apple-Art (Dauer + bounce 0.18–0.35) für Kacheln, Pins und Knotenpunkte.
- Stagger zwischen 28 und 85 ms, Abgänge laufen schneller als Auftritte.
- Blur überbrückt die Überblendungen. Beim Zählwerk richtet sich die Unschärfe nach der Geschwindigkeit, wie echte Bewegungsunschärfe.
- Animiert werden nur `transform`, `opacity`, `clip-path` und `filter`.

## Neu rendern

```bash
F=/tmp/frames; mkdir -p $F
for w in 0 1 2 3; do node render.js $F 60 $w 4 & done; wait
python3 audio.py /tmp/score.wav
ffmpeg -framerate 60 -i $F/f%05d.png -i /tmp/score.wav \
  -af loudnorm=I=-14:TP=-1.5 -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p \
  -c:a aac -b:a 256k -movflags +faststart broetje-handel-breuer-30s.mp4
```

Quellen für die Inhalte sind die Firmenseite in der G.U.T.-Gruppe und das Instagram-Profil. Die Wortmarke ist nur gesetzt, das Originallogo ist es nicht. Für eine offizielle Nutzung bitte das echte Logo und die CI-Vorgaben einsetzen.
