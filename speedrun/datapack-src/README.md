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

## Lobby-Insel (0 / 200 / 0)
- Vorne: 4 Knöpfe für die Wunschrolle
- Hinten links: **Modus wechseln**
- Hinten Mitte: **Hebel = Run starten** (Countdown 5 s)
- Hinten rechts: **Zuschauen an/aus**
- Schwebeschrift: Titel, aktueller Modus, Bestzeiten pro Modus

## Während des Runs
- Seitenleiste: Team-Checkliste mit 12 Aufgaben, die sich selbst abhaken
- Bossbar: Team, Modus, Zeit, erledigte Aufgaben
- Actionbar: deine Rolle und was du tun sollst
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
- `/trigger sr_aktion set 11` bis `15`: Modus Solo, Duo, Trio, Squad, Koop
- `/trigger sr_rolle set 1` bis `4`: Wunschrolle Kämpfer, Portal & Perlen, Versorger, Späher

## Bauen
`python3 build.py <ausgabeordner>` erzeugt `speedrun.zip`. Die Datei kommt nach `<welt>/datapacks/`.

## Server zurück auf die Himmelsinsel
In `server.properties` `level-name=himmelsinsel` setzen (und bei Bedarf `difficulty=hard`, `white-list=false`), dann neu starten.
