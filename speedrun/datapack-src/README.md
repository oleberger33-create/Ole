# Speedrun 2.0: Datapack für Minecraft 26.3

Läuft komplett auf dem Server. Spieler brauchen keine Mods.

## Modi
| Modus | Teamgröße | Ablauf |
| --- | --- | --- |
| Solo | 1 | Jeder gegen jeden |
| Duo | 2 | Teams aus 2 |
| Trio | 3 | Teams aus 3 |
| Squad | 4 | Teams aus 4 |
| Koop | alle | Ein Team, alle zusammen |

Gibt es mehr als ein Team, wird es ein **Rennen**: Jedes Team startet an einem eigenen, frischen Ort. Wer zuerst den Drachen tötet, gewinnt. Die Teams werden zufällig ausgelost (bis zu 8 Teams: Rot, Blau, Grün, Gelb, Türkis, Lila, Orange, Weiß).

## Rollen
Die Rollen werden automatisch nach Teamgröße vergeben. Wunschrollen werden zuerst berücksichtigt.
- **1 Spieler:** Solo (alles selbst)
- **2 Spieler:** Nether-Läufer / Versorger & Wegfinder
- **3 Spieler:** Kämpfer / Portal & Perlen / Versorger
- **4+ Spieler:** Kämpfer / Portal & Perlen / Versorger / Späher

## Lobby (Insel bei 0 / 200 / 0)
Jeder in der Lobby hat diese Items in der Hotbar (Rechtsklick):

| Slot | Item | Funktion |
| --- | --- | --- |
| 1 | Netherstern | Run starten (Countdown 5 s) |
| 2 | Uhr | Modus wechseln |
| 3 | Kompass / Blaze-Rute / Perle / Bett / Enderauge | Wunschrolle wechseln |
| 5 | Fernrohr | Zuschauen an/aus |
| 8 | Papier | Speedrun-Zettel (siehe unten) |
| 9 | Buch | Speedrun-Menü |

Die Items lassen sich nicht verlieren. Im Run sind sie weg. Über der Insel schweben Titel, aktueller Modus und Bestzeiten pro Modus.

## Speedrun-Zettel
Jeder Spieler hat immer ein Papier „Speedrun-Zettel“ (Slot 8): in der Lobby, im Run und als Zuschauer.
Er geht nicht verloren: Wegwerfen, Tod, Inventar leeren oder Verbauen – er ist nach spätestens 4 Ticks wieder da (genau einer).
Rechtsklick (oder Esc → Speedrun-Menü → Speedrun-Zettel, `/trigger sr_aktion set 9`) öffnet ein Fenster mit
- Zeit, Team, deiner Rolle und deinem nächsten Schritt,
- allen wichtigen Items als Bild mit Ziel und dem aktuellen Stand deines Teams (✔ wenn erreicht):
  Spitzhacke, Eisenschwert, Schild, Eimer, Feuerzeug, Obsidian 10, Essen 20, Betten 7, Blaze-Ruten 7, Enderperlen 12, Gold 32, Enderaugen 12, Bogen, Pfeile 16, Blöcke 64,
- den 13 Team-Aufgaben (✔/✘) und einem Tipp für die aktuelle Phase.
Gezählt wird beim Öffnen (alle Online-Spieler des Teams). Technisch ist der Zettel ein Karottenrute-Item mit Papier-Aussehen (Rechtsklick wird über die Statistik erkannt).

## Während des Runs
- Seitenleiste: Team-Checkliste mit 12 Aufgaben, die sich selbst abhaken
- Bossbar: Team, Modus, Zeit, erledigte Aufgaben
- Actionbar (unten über der Hotbar): Zeit des Runs, deine Rolle und was du tun sollst, z. B. „⏱ 12:34 · [Kämpfer] Schritt 4/7 ▸ Blaze-Ruten farmen 3/7“ (Zuschauer und Lobby: Zeit). Ab einer Stunde h:mm:ss
- Chat: Fortschritt der anderen Teams („[Blau] Festung gefunden“)
- Ende: Siegertitel, Zeit, Feuerwerk, Sieg in der Tab-Liste, nach 20 s zurück zur Lobby
- Drache aus einem alten Run schon tot: Wer ins End kommt, bekommt 4 Endkristalle zum Neu-Beschwören

## Menü und Befehle
Esc → **Speedrun-Menü** (alle Funktionen per Knopf). Alternativ:
- `/trigger sr_aktion set 1`: Run starten
- `/trigger sr_aktion set 2`: zurück zur Lobby
- `/trigger sr_aktion set 3`: Menü öffnen
- `/trigger sr_aktion set 4`: Zuschauen an/aus
- `/trigger sr_aktion set 6`: Run abbrechen
- `/trigger sr_aktion set 9`: Speedrun-Zettel öffnen
- `/trigger sr_aktion set 11` bis `15`: Modus Solo, Duo, Trio, Squad, Koop
- `/trigger sr_rolle set 1` bis `4`: Wunschrolle Kämpfer, Portal & Perlen, Versorger, Späher

## Bauen
`python3 build.py <ausgabeordner>` erzeugt `speedrun.zip`. Die Datei kommt nach `<welt>/datapacks/`.

## Server zurück auf die Himmelsinsel
In `server.properties` `level-name=himmelsinsel` setzen (und bei Bedarf `difficulty=hard`, `white-list=false`), dann neu starten.
