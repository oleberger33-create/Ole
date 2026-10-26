"""Gibt die Befehle für die Lava-Farm aus (rein vanilla, wird einmal per Konsole gesetzt).

Aufruf:  python3 lavafarm.py <ort.json>

ort.json:  {"ecke": [x, y, z]}   Kessel ganz im Norden, y: Höhe der Kessel

Aufbau (relativ zur Ecke, Kessel in einer Reihe nach Süden):
  0      Kessel
  1      Luft (hier tropft es)
  2      spitzer Tropfstein, Spitze nach unten
  3      Tropfsteinblock, daneben Steinziegel als Dach
  4      Lavaquelle über jedem Tropfsteinblock, ringsum Glas
  5      Glasdach über der Lava, 3 breit: Lava zündet sonst Brennbares in der Nähe an
Ein Tropfstein unter Lava füllt den Kessel im Schnitt alle 20 Minuten mit einem Eimer Lava (nur, wenn ein Spieler in
der Nähe ist). Ein Eimer Lava brennt 100 Gegenstände im Ofen.
"""
import json
import sys

ORT = json.load(open(sys.argv[1]))
X0, Y0, Z0 = ORT["ecke"]
ANZAHL = 4


def pos(x, y, z):
    return "%d %d %d" % (X0 + x, Y0 + y, Z0 + z)


b = {}
for z in range(-1, ANZAHL + 1):
    for x in (-1, 0, 1):
        if (x, z) != (1, -1):                                   # dort sitzt der Trichter der Schmelzanlage
            b[(x, 3, z)] = "stone_bricks"                       # Dach über den Kesseln
        b[(x, 4, z)] = "glass"                                  # Rand der Lava
        b[(x, 5, z)] = "glass"                                  # Glasdach
for z in range(ANZAHL):
    b[(0, 0, z)] = "cauldron"
    b[(0, 1, z)] = "air"
    b[(0, 2, z)] = "pointed_dripstone[vertical_direction=down,thickness=tip]"
    b[(0, 3, z)] = "dripstone_block"
    b[(0, 4, z)] = "lava"
for x, z in ((-1, ANZAHL), (1, ANZAHL), (1, 0)):                # Pfeiler, der Weg vor den Kesseln bleibt frei
    for y in range(0, 3):
        b[(x, y, z)] = "stone_bricks"

reihenfolge = {"lava": 2, "pointed_dripstone": 1}
for (x, y, z), blk in sorted(b.items(), key=lambda e: (reihenfolge.get(e[1].split("[")[0], 0), e[0][1], e[0][0], e[0][2])):
    print(f"setblock {pos(x, y, z)} minecraft:{blk}")
