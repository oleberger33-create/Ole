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

- `generator/farmen.py` enthält alle 33 Baupläne in der einfachsten Bauweise, die auf dem Testserver funktioniert
  hat (Text-Raster je Ebene, Format in `entwurf.py`), die Texte stehen in `farmtexte.py`. `python3 farmen.py`
  schreibt `plaene.json` und `../test/tests.json`; `python3 farmen.py --material` zeigt die Materialliste je Farm.
- `generator/farmhelper.py plaene.json <ordner>` baut das Datapack `OlesFarmhelper.zip` und das Ressourcenpaket
  `OlesFarmhelper-Ressourcen.zip`; `bloecke.py` übersetzt die Plan-Blöcke in echte Blöcke, Prüfungen und Items,
  `textur.py` zeichnet das Item-Bild.
- Je Farm, Drehung (4) und Teilschritt gibt es eine `zeigen`- und eine `pruefen`-Funktion; die eigentliche Arbeit
  machen kleine gemeinsame Funktionen (`c/`, `z/`, `h/`, `w/`), die an `~ ~ ~` arbeiten.
- Knöpfe schicken `/trigger ofh.t set <Code>` (geht ohne Operator-Rechte). Ein unsichtbarer Marker merkt sich
  Farm, Drehung und Teilschritt; jede Sekunde prüft das Pack alle offenen Pläne.
- `test/mctest.py plaene.json tests.json [farm …] --ticks=N --zufall=N` baut die Farmen auf einem lokalen
  26.3-Server (Fabric + Carpet, RCON) so auf, wie ein Spieler sie baut, stellt einen Testspieler an den
  Warteplatz, lässt die Zeit im Zeitraffer laufen und misst den Ertrag in Truhen, am Boden, Blöcke und Wesen.
  Bauwerk-Farmen (Hexenhütte, Außenposten, Festung) brauchen eine normale Welt mit Bauwerken – per Befehl gesetzte
  Bauwerke haben keine Spawn-Regeln. Das Programm misst die Spawn-Box der Hexenhütte blockgenau und nimmt nur eine
  Hütte in Plan-Ausrichtung. Vor jedem Lauf entlädt es alte Testorte und entfernt alle Wesen (`--behalten` lässt
  das): Mobs alter Testorte füllen sonst das Monster-Limit, und nichts spawnt mehr.
  Erwartungen: `items` (Behälter), `boden` (Items am Boden), `inventar` (Testspieler), `beute` (alles zusammen),
  `bloecke`, `wesen` (mit `bereich` nur in einem Teil); Schlüssel `*` = alle Sorten, `a|b` = a und b zusammen.

### Was beim Vereinfachen gelernt wurde (Testserver 26.3)

- Im Wasser spawnt nichts – auch nicht am Spawner. Wasserkanäle liegen darum eine Ebene unter dem Spawnboden.
- Fließendes Wasser über Wasser breitet sich nicht aus: Sammelrinnen über einem Becken gehen nicht.
- Durch Glas sehen Mobs nichts (Dorfbewohner/Zombie, Endermen/Endermilbe).
- Werfer mit Glasflaschen werfen sie bei nicht vollem Bienennest heraus, Scheren nicht.
- Trichter saugen durch Schlamm und Ackerboden (nicht ganz hohe Blöcke), nicht durch Erde oder Magma.
- Ein Dispenser direkt auf Gras macht das Gras zu Erde.
- Mobs, die weiter als 32 Blöcke von jedem Spieler sind, laufen nicht herum (Hexen standen bei 33 Blöcken still).
  Der AFK-Platz liegt darum 24–32 Blöcke von der Spawnfläche entfernt.
- Durch Gerüst sehen Mobs hindurch (Plünderer zielen auf den Spieler oben auf dem Gerüstturm), durch Erde/Glas nicht.
- Mobs können auf der Oberkante einer offenen Falltür stehen und darauf laufen. Über einen 1 breiten Lochring
  kommen sie trotzdem: Der Spalt neben der Kante ist schmaler als ein Schritt, und sie steigen auf den nächsten
  Block (Endermen sogar einen ganzen Block hoch). Darum sind Lochfelder um ein Ziel 2 breit, Klappen außen.
- Endermen teleportieren sich ab und zu von selbst und landen dabei auch auf Falltüren. Ein Boot nimmt einen
  zweiten Fahrgast auf – so kam ein Enderman neben die Endermilbe. Ein Dach 3 × 3 über der Mitte (2 Blöcke Platz)
  verhindert das.
- Endermen spawnen auch auf einem 3 × 3-Feld neben der Endermilbe; auf unteren Stufen nicht.
- Echte Dorfbewohner heben auf (per `/summon` gesetzte nicht, außer mit `CanPickUpLoot:1b`): Der Bauer schnappt
  sich die Ernte vor den Trichtern unter dem Acker. Er wirft aber ab mehr als 24 Stück einer Sorte den Rest einem
  anderen Dorfbewohner zu – dort fangen Trichter ihn auf. Weizen backt er vorher zu Brot.
- Die flache Testwelt ist für Schleime und Ertrunkene ungeeignet: Auf der Oberfläche (y -61, unter 40) spawnen in
  Schleim-Chunks Schleime und füllen das Monster-Limit. Tests darum hoch über der Oberfläche oder mit gefülltem
  Untergrund in einem allein liegenden Schleim-Chunk.

### Teststand (26.3)

Letzter Gesamtlauf: 31 von 32 Flachwelt-Tests bestanden (30 Spielminuten, alle Farmen gleichzeitig), dazu die
Bauwerk-Farmen in einer normalen Welt.

- Mit echten Spawns bzw. echtem Wachstum bestanden: Zuckerrohr, Bambus, Kaktus, Melone/Kürbis, Seetang,
  Karotten-Bauer, Baum, Knochenmehl, Blumen, Hühner, Kühe, Wolle, Honig, Eisen, Spawner, Monster, Creeper, Lohen,
  Gold, Endermen (weit weg von Inseln: 38–47 Perlen in 20 Minuten), Handel, Bruchstein, Lava, Schnee,
  Stock-Crafter; Hexen an echten Hexenhütten (3 von 3 Läufen).
- Schleim: allein in einem allein liegenden Schleim-Chunk 58 Schleime in 60 Minuten; im Gesamtlauf mit 32 Farmen
  keiner (alle teilen sich das Monster-Limit).
- Plünderer an echten Außenposten: 6 bzw. 14 in den Gruben nach 30 Minuten, an einem dritten Außenposten erst nach
  35 Minuten einer – die Spawnrate schwankt je Außenposten.
- Ertrunkene: funktioniert, aber wenig (1 in 60 Minuten).
- Zusätzlich mit hineingesetzten Mobs bestanden: Monster, Creeper, Hexen, Ertrunkene, Plünderer, Gold.
- Nicht nachgewiesen: Wither-Skelette spawnten in der Festung, auf der Fläche in 30 Minuten aber keins; Wächter,
  Überfall und Angeln haben keinen automatischen Test (Kampf- bzw. Handarbeit).

## Server-Version (OLE SMP, Welt „welt“)

Auf dem Server läuft nicht das Original, sondern eine nachbearbeitete Fassung. Sie entsteht in fünf Schritten:

```bash
# 1. Original bauen
python3 generator/farmhelper.py generator/plaene.json aus/
# 2. Auf einen Spieler beschränken, Geister als Partikel nur für ihn (Werkzeug liegt im Branch speedrun-plan)
python3 smp/tools/farmhelper_nur_fuer.py aus/OlesFarmhelper.zip FNGreg nur.zip
# 3. Für mehrere Spieler freigeben; jeder sieht nur die Geister seiner eigenen Pläne
python3 server/mehrere_spieler.py nur.zip mehrere.zip FNGreg korokchris
# 4. Ersatzblöcke und Bausteinauswahl
python3 server/baustein.py mehrere.zip baustein.zip server/baustein.json
# 5. Blöcke im Weg an allen Seiten markieren (orange ausgraben, rot abbauen), „im Weg N“ in der Aktionsleiste
python3 server/geister.py baustein.zip OlesFarmhelper.zip
```

Das Ergebnis kommt nach `welt/datapacks/OlesFarmhelper.zip`, danach `/reload`.

**Ersatzblöcke (`server/baustein.json`):** Wo ein Plan Steinziegel, Bruchstein, Stein, Glatten Stein oder Endstein
verlangt, akzeptiert die Prüfung jeden Block der Gruppe `stein` (41 Steinsorten: voll, undurchsichtig, nicht brennbar,
leitet Redstone, Mobs spawnen darauf, Explosionswiderstand ≥ 6). Netherrack in der Gold-Farm nimmt zusätzlich die
Steingruppe ohne Netherziegel, Obsidian in der Enderman-Farm die Steingruppe, Leuchtstein auch Seelaterne, Strohballen
auch Stein und das Weizenfeld auch Karotten, Kartoffeln und Rote Bete. Fest bleiben Netherziegel (Festungs-Spawns),
Magma, Seelensand, Wasser, Lava und alle Funktionsblöcke. Grundlage ist eine Prüfung aller 33 Farmen gegen 26.3
(Spawnregeln, Redstone, Kolben, Feuer, Wasser, Explosionen) mit anschließender Gegenprüfung.

**Geister in der Server-Fassung:** Die Geisterblöcke sind Partikel (nur der Planbesitzer sieht sie). Steht an der
Stelle schon ein Block, steckt der Geist darin – darum markiert `geister.py` solche Blöcke an allen freien Seiten
(orange: ausgraben, rot: falscher Block, abbauen) und die Aktionsleiste zeigt „im Weg N“. Ist der Block weg,
erscheint der Geist.

**Bausteinauswahl:** Im Plan-Menü öffnet „Baustein“ eine Auswahl von 14 Steinsorten. Die Wahl gilt für den eigenen Plan:
Geisterblöcke und der Zähler in der Aktionsleiste zeigen dann diesen Stein. „Vorgabe des Plans“ stellt zurück.
