# Speedrun-Datapack (Minecraft 26.3)

Läuft komplett auf dem Server. Spieler brauchen keine Mods.

## Was es macht
- **Lobby-Insel** bei 0 / 200 / 0 (Weltspawn). In der Lobby bekommt man keinen Schaden und ist im Abenteuermodus.
- **Rollen:** drei Knöpfe vorne auf der Insel (Ole · Kämpfer, Mats · Portal & Perlen, Sammy · Versorger), alternativ per Klick im Chat oder im Menü.
- **Neuer Run:** Hebel hinten auf der Insel ziehen. Alle mit Rolle werden geleert (Inventar, Endertruhe, XP, Fortschritte) und an einen frischen Ort teleportiert. Es gibt 60 Startorte, die mindestens 3200 Blöcke auseinanderliegen.
- **Aufgaben:** rechte Seitenleiste, je nach Rolle. Sie haken sich automatisch ab (Items im Inventar, Nether/End betreten, Festung/Bastion/Stronghold gefunden, Drache besiegt).
- **Timer:** Bossbar oben, mit Run-Nummer, Zeit und erledigten Aufgaben. Bestzeit und letzter Run stehen in der Lobby-Seitenleiste.
- **Menü:** Esc → „Speedrun-Menü“ (Rolle, Run starten, Run beitreten, zurück zur Lobby).
- **Drache schon tot?** Wer in einem späteren Run das End betritt, bekommt 4 Endkristalle, um ihn am Ausgangsportal neu zu beschwören.

## Befehle für alle Spieler
- `/trigger sr_rolle set 1|2|3`: Rolle Ole/Mats/Sammy
- `/trigger sr_aktion set 1`: neuer Run
- `/trigger sr_aktion set 2`: zurück zur Lobby
- `/trigger sr_aktion set 3`: Menü öffnen
- `/trigger sr_aktion set 4`: laufendem Run beitreten

## Bauen
`python3 build.py <ausgabeordner>` erzeugt `speedrun.zip`. Die Datei kommt nach `<welt>/datapacks/`.

## Server zurück auf die Himmelsinsel stellen
In `server.properties` `level-name=himmelsinsel` (und bei Bedarf `difficulty=hard`) setzen und den Server neu starten. Sonst bleibt in der Datei alles gleich.
