# Wegpunkte

Server-Mod (Fabric 26.3): Gemeinsame Wegpunkte für alle Spieler, ohne dass jemand etwas installieren muss.

- `/wp add <Name> [Farbe]`: Wegpunkt an der eigenen Position setzen (max. 15 pro Spieler)
- `/wp liste`: alle Wegpunkte mit Entfernung
- `/wp entfernen <Name>`: eigenen Wegpunkt löschen (Ops dürfen alle löschen)
- `/wp farbe <Farbe> <Name>`: Farbe ändern
- `/wp info <Name>`

Farben: rot orange gelb gruen tuerkis blau lila rosa weiss

Anzeige:
- in der Ortungsleiste über der Hotbar, für alle Spieler in derselben Dimension (direkte Waypoint-Pakete, ohne Entities, auch wenn der Ort weit weg ist)
- Namensschilder für jeden Spieler, immer sichtbar – durch Wände und egal wie weit weg (`Schilder.java`): Der
  Server schickt jedem Spieler eigene Text-Displays (nur Pakete, nicht in der Welt), see_through, höchstens 24 Blöcke
  vor ihm in Richtung des Wegpunkts, mit Name und Entfernung; nah dran steht das Schild am echten Ort. Beim Start
  prüft ein Selbsttest die Pakete (verschlüsseln und lesen); schlägt er fehl, bleiben die Schilder aus.
  `/wp schilder aus|an` blendet sie für einen selbst aus und ein.
- ESP (`Esp.java`): andere Spieler leuchten durch Wände – nur für den Zuschauer (die Status-Bits mit „leuchtet“
  gehen nur an ihn, alle 2 Ticks erneuert). Weiter als 40 Blöcke entfernte Spieler bekommen zusätzlich ein Schild mit
  Name und Entfernung, egal wie weit. `/esp off` / `/esp on` (auch aus/an) für sich selbst.
- mit Kompass in der Hand: Name und Entfernung des Wegpunkts, auf den man schaut

Daten: `<welt>/wegpunkte.json`

Bauen: `JAVA_HOME=/usr/lib/jvm/java-25-openjdk-amd64 ./gradlew build` → `build/libs/wegpunkte-<version>.jar` in den `mods`-Ordner.
