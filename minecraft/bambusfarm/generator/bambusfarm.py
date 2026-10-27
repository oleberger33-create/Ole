"""Gibt die Befehle für die Bambusfarm aus (rein vanilla, einmal per Konsole gesetzt).

Aufruf:  python3 bambusfarm.py <ort.json>

ort.json:  {"ecke": [x, y, z]}   Nordwest-Ecke, y: Bodenhöhe (dort liegen die Trichter)

Zwei gleiche Blöcke nebeneinander, jeder mit zwei Bambusreihen von 14 Stück. Querschnitt von Nord nach Süd (z relativ
zur Mitte m eines Blocks), Höhe relativ zum Erdblock:
  m-3, m+3  Glaswand
  m-2, m+2  Erde, darauf der Bambus (bis 5 hoch); unter der Erde eine Trichterlore auf einer Schiene, darunter Trichter
  m-1, m+1  Kolben auf Höhe 2 zum Bambus hin, auf Höhe 5 ein Beobachter, der Höhe 5 vom Bambus beobachtet
  m         Redstone auf Höhe 5 (sammelt die Beobachter) und auf Höhe 3 (der Block darunter schaltet alle Kolben);
            am Ostende ein Beobachter nach oben, der die obere Leitung auf die untere überträgt
Wächst ein Bambus auf 5 Blöcke, schlagen alle Kolben des Blocks Höhe 2 ab. Alles darüber fällt mit ab, unten bleibt ein
Block stehen und wächst neu. Wie früh geschnitten wird, ändert die Menge nicht (jeder gewachsene Block wird geerntet),
höher geschnitten feuert die Farm nur seltener. Bambus wächst nur unter freiem Himmel, deshalb ein Glasdach.
Die Trichterloren saugen den Bambus durch die Erde, die Trichterreihen bringen ihn nach Westen in eine Sammelleitung
und die zur Doppeltruhe am Westende (auf Bodenhöhe, von oben zu öffnen).
"""
import json
import sys

ORT = json.load(open(sys.argv[1]))
X0, Y0, Z0 = ORT["ecke"]
LAENGE = 14                     # Bambus je Reihe, x 1..LAENGE; x 0 und LAENGE+1 Glas, LAENGE+2 Endwand
H = 5                           # Schnitthöhe (Beobachter)
MITTEN = (3, 9)                 # z der beiden Blöcke
E = LAENGE + 1                  # Ostende: Glas der Reihen, Beobachter der Mitte
W = "stone_bricks"
D = 2                           # Höhe des Erdblocks über der Ecke (darunter Schiene und Trichter)


def pos(x, y, z):
    return "%d %d %d" % (X0 + x, Y0 + y, Z0 + z)


def fill(x1, y1, z1, x2, y2, z2, blk):
    return f"fill {pos(x1, y1, z1)} {pos(x2, y2, z2)} minecraft:{blk}"


def h(n):                       # Höhe n über der Erde (1 = unterster Bambus)
    return D + n


reihen = [m + s * 2 for m in MITTEN for s in (-1, 1)]
z_end = MITTEN[-1] + 3
befehle = [
    fill(-2, 1, 0, E + 1, h(H) + 3, z_end, "air"),                   # Gras und Blumen weg
    fill(0, 0, 0, E + 1, D, z_end, W),                                # Unterbau
    fill(0, h(1), 0, E, h(H) + 1, z_end, "glass"),                    # Glaskörper mit Dach, Technik kommt hinein
    fill(E + 1, h(1), 0, E + 1, h(H), z_end, W),                      # Endwand im Osten
]
for z in reihen:
    befehle += [
        fill(0, 0, z, LAENGE, 0, z, "hopper[facing=west]"),
        fill(1, 1, z, LAENGE, 1, z, "powered_rail[shape=north_south,powered=false]"),  # quer: Loren bleiben stehen
        fill(1, D, z, LAENGE, D, z, "dirt"),
        fill(1, h(1), z, LAENGE, h(H), z, "air"),
    ]
for m in MITTEN:
    for s, blick in ((-1, "north"), (1, "south")):
        z = m + s
        befehle += [
            fill(0, h(1), z, E, h(H), z, W),
            fill(1, h(2), z, LAENGE, h(2), z, f"piston[facing={blick}]"),
            fill(1, h(H), z, LAENGE, h(H), z, f"observer[facing={blick}]"),
        ]
    befehle += [
        fill(0, h(1), m, E, h(H), m, W),
        fill(1, h(3), m, E, h(3), m, "redstone_wire[east=side,west=side]"),
        fill(1, h(H), m, E, h(H), m, "redstone_wire[east=side,west=side]"),
        f"setblock {pos(E, h(4), m)} minecraft:observer[facing=up]",
        fill(0, h(H) + 1, m - 1, E + 1, h(H) + 1, m + 1, "stone_brick_slab[type=bottom]"),  # Deckel über der Technik
    ]
# Sammelleitung im Westen, Doppeltruhe auf Bodenhöhe zwischen den Blöcken
TZ = MITTEN[0] + 3
befehle += [
    fill(-1, 0, reihen[0], -1, 0, TZ - 1, "hopper[facing=south]"),
    fill(-1, 0, TZ + 1, -1, 0, reihen[-1], "hopper[facing=north]"),
    f"setblock {pos(-1, 0, TZ)} minecraft:chest[facing=south,type=left]",
    f"setblock {pos(-2, 0, TZ)} minecraft:chest[facing=south,type=right]",
    fill(-1, 1, reihen[0], -1, 1, TZ - 1, "stone_brick_slab[type=bottom]"),
    fill(-1, 1, TZ + 1, -1, 1, reihen[-1], "stone_brick_slab[type=bottom]"),
]
for z in reihen:
    for x in range(1, LAENGE + 1):
        befehle.append(f"summon minecraft:hopper_minecart {X0 + x + 0.5} {Y0 + 1 + 0.0625} {Z0 + z + 0.5}")
for z in reihen:
    befehle.append(fill(1, h(1), z, LAENGE, h(1), z, "bamboo"))
for b in befehle:
    print(b)
