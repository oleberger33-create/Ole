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
- am Ort schwebt ein Namensschild (text_display)
- mit Kompass in der Hand: Name und Entfernung des Wegpunkts, auf den man schaut

Daten: `<welt>/wegpunkte.json`

Bauen: `JAVA_HOME=/usr/lib/jvm/java-25-openjdk-amd64 ./gradlew build` → `build/libs/wegpunkte-1.0.0.jar` in den `mods`-Ordner.
