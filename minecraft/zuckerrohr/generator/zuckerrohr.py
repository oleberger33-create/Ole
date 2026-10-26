"""Gibt die Befehle für die Zuckerrohr-Farm aus (rein vanilla, einmal per Konsole gesetzt).

Aufruf:  python3 zuckerrohr.py <ort.json>

ort.json:  {"ecke": [x, y, z]}   Westende der Rohrreihe, y: Höhe des Erdblocks

Querschnitt von Süd nach Nord (z relativ):
   1  Wasser auf Erdhöhe, darüber Glas
   0  Erde, darauf das Zuckerrohr (3 hoch), darüber ein Glasdach; unter der Erde eine Trichterlore auf einer
      Schiene, darunter ein Trichter
  -1  Kolben auf Höhe 2 (Blick nach Süden), darüber ein Beobachter, der Höhe 3 beobachtet
  -2  Block mit Redstone darauf: Der Beobachter gibt nach hinten ein Signal, der Block schaltet den Kolben
Wächst ein Rohr auf 3 Blöcke, schlägt der Kolben Höhe 2 und 3 ab. Der Beobachter sieht danach nur noch einmal
eine Änderung, also läuft nichts im Kreis. Das Rohr fällt auf die Erde; die Trichterlore darunter saugt es durch
den Block, der Trichter unter der Schiene holt es aus der Lore, die Trichterreihe bringt es zur Truhe im Westen.
"""
import json
import sys

ORT = json.load(open(sys.argv[1]))
X0, Y0, Z0 = ORT["ecke"]
LAENGE = 12


def pos(x, y, z):
    return "%d %d %d" % (X0 + x, Y0 + y, Z0 + z)


def fill(x1, y1, z1, x2, y2, z2, blk):
    return f"fill {pos(x1, y1, z1)} {pos(x2, y2, z2)} minecraft:{blk}"


E = LAENGE - 1
befehle = [
    fill(-1, -2, -2, LAENGE, 5, 1, "air"),                            # Gras und Blumen weg
    fill(-1, -3, -2, LAENGE, -3, 1, "stone_bricks") + " replace minecraft:air",  # nur Löcher und Hang füllen
    fill(-1, -2, -2, LAENGE, 0, 1, "stone_bricks"),                   # Unterbau
    fill(0, -2, 0, E, -2, 0, "hopper[facing=west]"),                  # Trichterreihe zur Truhe
    fill(0, -1, 0, E, -1, 0, "powered_rail[shape=north_south,powered=false]"),  # quer: jede Lore auf eigenem Stück, ohne Strom gebremst
    fill(0, 0, 0, E, 0, 0, "dirt"),
    fill(0, 0, 1, E, 0, 1, "water"),
    fill(-1, 1, 0, LAENGE, 4, 1, "glass"),                            # Glaswand vorn, Enden, Dach
    fill(0, 1, 0, E, 3, 0, "air"),                                    # Platz für das Rohr
    fill(0, 1, 0, E, 1, 0, "sugar_cane"),
    fill(-1, 1, -1, LAENGE, 1, -1, "stone_bricks"),                   # unter den Kolben
    fill(0, 2, -1, E, 2, -1, "piston[facing=south]"),
    fill(0, 3, -1, E, 3, -1, "observer[facing=south]"),
    fill(-1, 1, -2, LAENGE, 2, -2, "stone_bricks"),
    fill(0, 3, -2, E, 3, -2, "redstone_wire"),
    fill(-1, 4, -2, LAENGE, 4, -1, "stone_brick_slab[type=bottom]"),  # Deckel, darauf spawnt nichts
    fill(-1, 2, -1, -1, 3, -1, "stone_bricks"),                       # Enden der Kolbenreihe
    fill(LAENGE, 2, -1, LAENGE, 3, -1, "stone_bricks"),
    f"setblock {pos(-1, -2, 0)} minecraft:chest[facing=west,type=right]",
    f"setblock {pos(-1, -2, 1)} minecraft:chest[facing=west,type=left]",
    f"setblock {pos(-1, -1, 0)} minecraft:glass",                     # Schienenende; Glas lässt die Truhe offen
    f"setblock {pos(-1, -1, 1)} minecraft:glass",
]
for x in range(LAENGE):
    befehle.append(f"summon minecraft:hopper_minecart {X0 + x + 0.5} {Y0 - 1 + 0.0625} {Z0 + 0.5}")
for b in befehle:
    print(b)
