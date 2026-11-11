# Ole's Farmhelper

Ein Bauhelfer für den Himmelsinsel-Server (Minecraft Java 26.3). Er läuft komplett auf dem Server: Die Spieler
installieren nichts, nur das Item-Bild kommt beim Beitreten als kleines Ressourcenpaket (über Polymer).

## Im Spiel

- **Item:** „Ole's Farmhelper“ (Bauplan-Rolle mit goldener Hacke). Jeder bekommt eins beim nächsten Beitreten.
  Nachbauen geht formlos aus Papier + Weizenkörnern + Stock.
- **Rechtsklick ohne Plan:** Liste aller 33 Farmen. Ein Klick zeigt Ertrag, Menge, den richtigen Ort und die
  beste Bauweise mit Quellen (Minecraft Wiki oder Spieldaten 26.3), Hilfe und das Material für die ganze Farm.
- **Ort hier prüfen:** prüft, wo du stehst: Dimension, Biom (z. B. Fluss für Ertrunkene), Bauwerk (Außenposten,
  Hexenhütte, Monument, Festung), Abstände (kein Golem in 16 Blöcken, keine Dorfbewohner in 96 Blöcken für die
  Überfall-Farm, 128+ Blöcke von der End-Hauptinsel) und für den Schleim-Chunk die Höhe.
- **Hier bauen:** Der Plan erscheint 2 Blöcke vor dir in Blickrichtung als leuchtende Geisterblöcke (grün). Gebaut
  wird Bauschritt für Bauschritt, jeweils Ebene für Ebene von unten nach oben.
  - Richtig gesetzt → der Geist verschwindet. Falscher Block → der Geist leuchtet rot.
  - Sind alle Blöcke eines Teils richtig, kommt automatisch der nächste.
  - Tiere und Dorfbewohner zeigt ein gelbes Schild („Dorfbewohner hierher bringen“); sie zählen, sobald sie dort sind.
  - Die Aktionsleiste zeigt laufend: Schritt, fehlende Blöcke und je Material „im Inventar / fehlt noch“.
- **Rechtsklick mit Plan:** Plan-Menü: Schritt zurück/überspringen, Plan verschieben (Norden/Süden/Osten/Westen/
  hoch/runter) und drehen, Ort prüfen (inkl. „Blöcke im Weg“), Material der ganzen Farm, Farm-Infos, abbrechen.

## Technik

- `generator/export.js` holt die Baupläne und die belegten Orts-/Meta-Angaben aus dem Farm-Handbuch
  (`plaene.json`).
- `generator/farmhelper.py plaene.json <ordner>` baut das Datapack `OlesFarmhelper.zip` und das Ressourcenpaket
  `OlesFarmhelper-Ressourcen.zip`; `bloecke.py` übersetzt die Plan-Blöcke in echte Blöcke, Prüfungen und Items,
  `textur.py` zeichnet das Item-Bild.
- Je Farm, Drehung (4) und Teilschritt gibt es eine `zeigen`- und eine `pruefen`-Funktion; die eigentliche Arbeit
  machen kleine gemeinsame Funktionen (`c/`, `z/`, `h/`, `w/`), die an `~ ~ ~` arbeiten.
- Knöpfe schicken `/trigger ofh.t set <Code>` (geht ohne Operator-Rechte). Ein unsichtbarer Marker merkt sich
  Farm, Drehung und Teilschritt; jede Sekunde prüft das Pack alle offenen Pläne.
- Getestet auf einem lokalen 26.3-Server (Fabric + Carpet-Testspieler): alle 33 Farmen Teil für Teil nachgebaut,
  jeder Teil schaltet automatisch weiter; alle Fenster, Ort-Checks und Knöpfe laufen ohne Fehler.

Die Pläne sind die Lern-Modelle aus dem Farm-Handbuch (Eisen- und Bambusfarm genau wie auf dem Server). Wo die
besten Designs größer oder anders sind, steht das mit Quelle in den Farm-Infos.
