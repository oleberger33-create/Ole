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

## Server-Version (OLE SMP, Welt „welt“)

Auf dem Server läuft nicht das Original, sondern eine nachbearbeitete Fassung. Sie entsteht in vier Schritten:

```bash
# 1. Original bauen
python3 generator/farmhelper.py generator/plaene.json aus/
# 2. Auf einen Spieler beschränken, Geister als Partikel nur für ihn (Werkzeug liegt im Branch speedrun-plan)
python3 smp/tools/farmhelper_nur_fuer.py aus/OlesFarmhelper.zip FNGreg nur.zip
# 3. Für mehrere Spieler freigeben; jeder sieht nur die Geister seiner eigenen Pläne
python3 server/mehrere_spieler.py nur.zip mehrere.zip FNGreg korokchris
# 4. Ersatzblöcke und Bausteinauswahl
python3 server/baustein.py mehrere.zip OlesFarmhelper.zip server/baustein.json
```

Das Ergebnis kommt nach `welt/datapacks/OlesFarmhelper.zip`, danach `/reload`.

**Ersatzblöcke (`server/baustein.json`):** Wo ein Plan Steinziegel, Bruchstein, Stein, Glatten Stein oder Endstein
verlangt, akzeptiert die Prüfung jeden Block der Gruppe `stein` (41 Steinsorten: voll, undurchsichtig, nicht brennbar,
leitet Redstone, Mobs spawnen darauf, Explosionswiderstand ≥ 6). Netherrack in der Gold-Farm nimmt zusätzlich die
Steingruppe ohne Netherziegel, Obsidian in der Enderman-Farm die Steingruppe, Leuchtstein auch Seelaterne, Strohballen
auch Stein und das Weizenfeld auch Karotten, Kartoffeln und Rote Bete. Fest bleiben Netherziegel (Festungs-Spawns),
Magma, Seelensand, Wasser, Lava und alle Funktionsblöcke. Grundlage ist eine Prüfung aller 33 Farmen gegen 26.3
(Spawnregeln, Redstone, Kolben, Feuer, Wasser, Explosionen) mit anschließender Gegenprüfung.

**Bausteinauswahl:** Im Plan-Menü öffnet „Baustein“ eine Auswahl von 14 Steinsorten. Die Wahl gilt für den eigenen Plan:
Geisterblöcke und der Zähler in der Aktionsleiste zeigen dann diesen Stein. „Vorgabe des Plans“ stellt zurück.
