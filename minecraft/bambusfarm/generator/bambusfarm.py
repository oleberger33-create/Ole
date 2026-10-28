"""Gibt die Befehle für die Bambusfarm aus (rein vanilla, einmal per Konsole gesetzt).

Aufruf:  python3 bambusfarm.py <ort.json> [neu|umbau]
  neu    (Standard) die ganze Farm
  umbau  nur für die schon gebaute Farm: Schienen quer stellen, Loren mittig setzen, Truhe gegen den Stöcke-Crafter
         tauschen (der Bambus aus der alten Truhe kommt in den Zubringer-Trichter)

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
und die zum Crafter am Westende, der aus je 2 Bambus einen Stock macht und ihn in die Doppeltruhe dahinter legt.

Stöcke-Crafter (alles auf Bodenhöhe, Redstone unter Stufen): Nur die zwei Felder links oben und links Mitte sind frei,
die anderen sieben gesperrt; der Trichter füllt die freien gleichmäßig. Ein Komparator liest den Crafter: Er zählt
belegte und gesperrte Felder, also 9, wenn beide Bambus da sind, sonst 8 oder 7. Danach 9 Redstone-Stücke: Am letzten
kommt nur aus 9 noch Strom an (9 - 8 = 1). Es zeigt in einen Block neben dem Crafter, der Crafter fertigt einen Stock,
ein Feld wird frei, der Strom geht aus, und beim nächsten vollen Paar wieder an.
Ist die Truhe voll, wirft der Crafter die Stöcke aus: rechtzeitig leeren.
Die Schienen werden mit strict gesetzt, sonst drehen sie sich längs zur Reihe und die Loren schieben sich gegenseitig.
"""
import json
import sys

ORT = json.load(open(sys.argv[1]))
MODUS = sys.argv[2] if len(sys.argv) > 2 else "neu"
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
schienen = [fill(1, 1, z, LAENGE, 1, z, "powered_rail[shape=north_south,powered=false]") + " strict" for z in reihen]
for z in reihen:
    befehle += [
        fill(0, 0, z, LAENGE, 0, z, "hopper[facing=west]"),
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
befehle += schienen
# Sammelleitung im Westen in den Zubringer-Trichter, der füllt den Crafter
TZ = MITTEN[0] + 3
CX = -2                                                               # Crafter; Truhe westlich davon, Redstone drumherum
befehle += [
    fill(-1, 0, reihen[0], -1, 0, TZ - 1, "hopper[facing=south]"),
    fill(-1, 0, TZ + 1, -1, 0, reihen[-1], "hopper[facing=north]"),
    fill(-1, 1, reihen[0], -1, 1, TZ - 1, "stone_brick_slab[type=bottom]"),
    fill(-1, 1, TZ + 1, -1, 1, reihen[-1], "stone_brick_slab[type=bottom]"),
]
DRAHT = [(CX, TZ - 2, "south", "west"), (CX - 1, TZ - 2, "east", "west"), (CX - 2, TZ - 2, "east", "west"),
         (CX - 3, TZ - 2, "east", "south"), (CX - 3, TZ - 1, "north", "south"), (CX - 3, TZ, "north", "south"),
         (CX - 3, TZ + 1, "north", "east"), (CX - 2, TZ + 1, "west", "east"), (CX - 1, TZ + 1, "west", "east")]
crafter = [
    f"setblock {pos(CX - 1, 0, TZ)} minecraft:chest[facing=south,type=left]",
    f"setblock {pos(CX - 2, 0, TZ)} minecraft:chest[facing=south,type=right]",
    f"setblock {pos(-1, 0, TZ)} minecraft:hopper[facing=west]",
    f"setblock {pos(CX, 0, TZ)} minecraft:crafter[orientation=west_up]{{disabled_slots:[I;1,2,4,5,6,7,8]}}",
    f"setblock {pos(CX, 0, TZ - 1)} minecraft:comparator[facing=south,mode=compare]",
    f"setblock {pos(CX, 0, TZ + 1)} minecraft:{W}",                    # vom letzten Redstone geschaltet, neben dem Crafter
] + [f"setblock {pos(x, 0, z)} minecraft:redstone_wire[{a}=side,{b}=side]" for x, z, a, b in DRAHT] + [
    f"setblock {pos(x, 1, z)} minecraft:stone_brick_slab[type=bottom]" for x, z, _, _ in DRAHT + [(CX, TZ - 1, "", "")]]

if MODUS == "umbau":
    befehle = schienen + [
        f"execute as @e[type=minecraft:hopper_minecart,x={X0},y={Y0},z={Z0},dx={LAENGE + 1},dy=2,dz={reihen[-1] + 1}] "
        f"at @s align xz run tp @s ~0.5 {Y0 + 1 + 0.0625} ~0.5",
        f"data modify storage bam:umbau Items set from block {pos(CX, 0, TZ)} Items",
    ] + crafter + [f"data modify block {pos(-1, 0, TZ)} Items set from storage bam:umbau Items"]
else:
    befehle += crafter
    for z in reihen:
        for x in range(1, LAENGE + 1):
            befehle.append(f"summon minecraft:hopper_minecart {X0 + x + 0.5} {Y0 + 1 + 0.0625} {Z0 + z + 0.5}")
    for z in reihen:
        befehle.append(fill(1, h(1), z, LAENGE, h(1), z, "bamboo"))
for b in befehle:
    print(b)
