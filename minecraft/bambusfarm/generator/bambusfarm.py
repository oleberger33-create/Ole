"""Gibt die Befehle für die Bambusfarm aus (rein vanilla, einmal per Konsole gesetzt).

Aufruf:  python3 bambusfarm.py <ort.json> [neu|umbau|lager|etage]
  neu    (Standard) die ganze Farm
  umbau  nur für die schon gebaute Farm: Schienen quer stellen, Loren mittig setzen, Truhe gegen den Stöcke-Crafter
         tauschen (der Bambus aus der alten Truhe kommt in den Zubringer-Trichter)
  lager  nur für die Farm mit Crafter und einer Truhe: Crafter nach oben in die Lagerleitung, die alte Truhe weg
         (ihre Stöcke kommen in die erste Lagertruhe)
  etage  nur für die Farm mit einer Etage: zweite Etage obendrauf, Seelaternen ins untere Dach

ort.json:  {"ecke": [x, y, z]}   Nordwest-Ecke, y: Bodenhöhe (dort liegen die Trichter)

Zwei Etagen übereinander, je zwei gleiche Blöcke nebeneinander, jeder mit zwei Bambusreihen von 14 Stück. Querschnitt von Nord nach Süd (z relativ
zur Mitte m eines Blocks), Höhe relativ zum Erdblock:
  m-3, m+3  Glaswand
  m-2, m+2  Erde, darauf der Bambus (bis 5 hoch); unter der Erde eine Trichterlore auf einer Schiene, darunter Trichter
  m-1, m+1  Kolben auf Höhe 2 zum Bambus hin, auf Höhe 5 ein Beobachter, der Höhe 5 vom Bambus beobachtet
  m         Redstone auf Höhe 5 (sammelt die Beobachter) und auf Höhe 3 (der Block darunter schaltet alle Kolben);
            am Ostende ein Beobachter nach oben, der die obere Leitung auf die untere überträgt
Wächst ein Bambus auf 5 Blöcke, schlagen alle Kolben des Blocks Höhe 2 ab. Alles darüber fällt mit ab, unten bleibt ein
Block stehen und wächst neu. Wie früh geschnitten wird, ändert die Menge nicht (jeder gewachsene Block wird geerntet),
höher geschnitten feuert die Farm nur seltener. Bambus braucht Licht 9 über der Spitze: oben ein Glasdach, in der
unteren Etage Seelaternen im Dach über den Reihen. Die obere Sammelleitung führt am Westende senkrecht hinunter in den
Zubringer der unteren.
Die Trichterloren saugen den Bambus durch die Erde, die Trichterreihen bringen ihn nach Westen in eine Sammelleitung
und die zum Crafter am Westende, der aus je 2 Bambus einen Stock macht und ihn nach oben ins Lager gibt.

Stöcke-Crafter (alles auf Bodenhöhe, Redstone unter Stufen): Nur die zwei Felder links oben und links Mitte sind frei,
die anderen sieben gesperrt; der Trichter füllt die freien gleichmäßig. Ein Komparator liest den Crafter: Er zählt
belegte und gesperrte Felder, also 9, wenn beide Bambus da sind, sonst 8 oder 7. Danach 9 Redstone-Stücke: Am letzten
kommt nur aus 9 noch Strom an (9 - 8 = 1). Es zeigt in einen Block neben dem Crafter, der Crafter fertigt einen Stock,
ein Feld wird frei, der Strom geht aus, und beim nächsten vollen Paar wieder an.
Lager: Über dem Boden läuft eine Trichterleitung vom Crafter nach Westen und dann vor dem Haus nach Norden. Unter jedem
Trichter der Leitung zieht ein zweiter Trichter Stöcke heraus und legt sie in die Truhe daneben (vier Doppeltruhen auf
Bodenhöhe, von oben zu öffnen). Ist eine Truhe voll, bleibt ihr Trichter voll und die Stöcke laufen zur nächsten.
Sind alle voll, wirft der Crafter die Stöcke aus: rechtzeitig leeren (Platz für 13824 Stöcke).
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
TZ = MITTEN[0] + 3                                                    # Zeile der Sammelleitung (zwischen den Blöcken)
ETAGEN = 2
HOCH = h(H) + 2                                                       # eine Etage: Trichter bis Dach


def etage(k):
    """Befehle für Etage k (0 = unten), ohne Loren und Bambus. Unter einer weiteren Etage bekommt das Dach über den
    Reihen Seelaternen statt Glas: Bambus wächst nur bei Licht 9 oder mehr über der Spitze."""
    oy = k * HOCH
    b = [
        fill(-2 if k == 0 else 0, oy + 1, 0, E + 1, oy + h(H) + 3, z_end, "air"),   # Gras und Blumen weg
        fill(0, oy, 0, E + 1, oy + D, z_end, W),                                     # Unterbau
        fill(0, oy + h(1), 0, E, oy + h(H) + 1, z_end, "glass"),                     # Glaskörper mit Dach
        fill(E + 1, oy + h(1), 0, E + 1, oy + h(H), z_end, W),                       # Endwand im Osten
    ]
    for z in reihen:
        b += [
            fill(0, oy, z, LAENGE, oy, z, "hopper[facing=west]"),
            fill(1, oy + D, z, LAENGE, oy + D, z, "dirt"),
            fill(1, oy + h(1), z, LAENGE, oy + h(H), z, "air"),
        ]
        if k < ETAGEN - 1:
            b.append(fill(1, oy + h(H) + 1, z, LAENGE, oy + h(H) + 1, z, "sea_lantern"))
    for m in MITTEN:
        for s, blick in ((-1, "north"), (1, "south")):
            z = m + s
            b += [
                fill(0, oy + h(1), z, E, oy + h(H), z, W),
                fill(1, oy + h(2), z, LAENGE, oy + h(2), z, f"piston[facing={blick}]"),
                fill(1, oy + h(H), z, LAENGE, oy + h(H), z, f"observer[facing={blick}]"),
            ]
        b += [
            fill(0, oy + h(1), m, E, oy + h(H), m, W),
            fill(1, oy + h(3), m, E, oy + h(3), m, "redstone_wire[east=side,west=side]"),
            fill(1, oy + h(H), m, E, oy + h(H), m, "redstone_wire[east=side,west=side]"),
            f"setblock {pos(E, oy + h(4), m)} minecraft:observer[facing=up]",
            fill(0, oy + h(H) + 1, m - 1, E + 1, oy + h(H) + 1, m + 1, "stone_brick_slab[type=bottom]"),  # Deckel
        ]
    # Sammelleitung westlich der Reihen zur Zeile TZ; oben geht sie dort senkrecht hinunter zum Zubringer
    b += [
        fill(-1, oy, reihen[0], -1, oy, TZ - 1, "hopper[facing=south]"),
        fill(-1, oy, TZ + 1, -1, oy, reihen[-1], "hopper[facing=north]"),
        fill(-1, oy + 1, reihen[0], -1, oy + 1, TZ - 1, "stone_brick_slab[type=bottom]"),
        fill(-1, oy + 1, TZ + 1, -1, oy + 1, reihen[-1], "stone_brick_slab[type=bottom]"),
    ]
    if k > 0:
        b += [fill(-1, 1, TZ, -1, oy, TZ, "hopper[facing=down]"),
              f"setblock {pos(-1, oy + 1, TZ)} minecraft:stone_brick_slab[type=bottom]"]
    b += [fill(1, oy + 1, z, LAENGE, oy + 1, z, "powered_rail[shape=north_south,powered=false]") + " strict"
          for z in reihen]
    return b


def bepflanzen(k):
    oy = k * HOCH
    b = [f"summon minecraft:hopper_minecart {X0 + x + 0.5} {Y0 + oy + 1 + 0.0625} {Z0 + z + 0.5}"
         for z in reihen for x in range(1, LAENGE + 1)]
    return b + [fill(1, oy + h(1), z, LAENGE, oy + h(1), z, "bamboo") for z in reihen]


schienen = [fill(1, 1, z, LAENGE, 1, z, "powered_rail[shape=north_south,powered=false]") + " strict" for z in reihen]
befehle = [c for k in range(ETAGEN) for c in etage(k)]
# Zubringer-Trichter am Ende der unteren Sammelleitung füllt den Crafter
CX = -2                                                               # Crafter; Truhe westlich davon, Redstone drumherum
DRAHT = [(CX, TZ - 2, "south", "west"), (CX - 1, TZ - 2, "east", "west"), (CX - 2, TZ - 2, "east", "west"),
         (CX - 3, TZ - 2, "east", "south"), (CX - 3, TZ - 1, "north", "south"), (CX - 3, TZ, "north", "south"),
         (CX - 3, TZ + 1, "north", "east"), (CX - 2, TZ + 1, "west", "east"), (CX - 1, TZ + 1, "west", "east")]
LX = CX - 5                                                           # Lagerleitung nach Norden, Truhen westlich davon
LZ = range(TZ, TZ - 8, -1)
lager = [fill(LX + 1, 1, TZ, CX, 1, TZ, "hopper[facing=west]"),
         fill(LX, 1, TZ, LX, 1, LZ[-2], "hopper[facing=north]"),
         f"setblock {pos(LX, 1, LZ[-1])} minecraft:hopper[facing=down]",
         fill(LX, 0, TZ, LX, 0, LZ[-1], "hopper[facing=west]")]
for z in LZ:                                                          # Doppeltruhe nach Westen: links ist die südliche
    lager.append(f"setblock {pos(LX - 1, 0, z)} minecraft:chest[facing=west,type={'left' if (TZ - z) % 2 == 0 else 'right'}]")
AUSGABE = "minecraft:crafter[orientation=up_west]{disabled_slots:[I;1,2,4,5,6,7,8]}"
crafter = [
    fill(CX - 2, 0, TZ, CX - 1, 0, TZ, W),                              # zwischen Crafter und Redstone
    f"setblock {pos(-1, 0, TZ)} minecraft:hopper[facing=west]",
] + lager + [
    f"setblock {pos(CX, 0, TZ)} {AUSGABE}",
    f"setblock {pos(CX, 0, TZ - 1)} minecraft:comparator[facing=south,mode=compare]",
    f"setblock {pos(CX, 0, TZ + 1)} minecraft:{W}",                    # vom letzten Redstone geschaltet, neben dem Crafter
] + [f"setblock {pos(x, 0, z)} minecraft:redstone_wire[{a}=side,{b}=side]" for x, z, a, b in DRAHT] + [
    f"setblock {pos(x, 1, z)} minecraft:stone_brick_slab[type=bottom]" for x, z, _, _ in DRAHT + [(CX, TZ - 1, "", "")]]

if MODUS == "etage":
    befehle = etage(1) + [fill(1, h(H) + 1, z, LAENGE, h(H) + 1, z, "sea_lantern") for z in reihen] + bepflanzen(1)
elif MODUS == "lager":
    alt = [pos(CX - 1, 0, TZ), pos(CX - 2, 0, TZ)]
    befehle = lager + [
        f"data modify storage bam:umbau C set from block {pos(CX, 0, TZ)} Items",
        f"setblock {pos(CX, 0, TZ)} {AUSGABE}",
        f"data modify block {pos(CX, 0, TZ)} Items set from storage bam:umbau C",
        f"data modify block {pos(LX - 1, 0, TZ)} Items set from block {alt[0]} Items",
        f"data modify block {pos(LX - 1, 0, TZ - 1)} Items set from block {alt[1]} Items",
        fill(CX - 2, 0, TZ, CX - 1, 0, TZ, W),
    ]
elif MODUS == "umbau":
    befehle = schienen + [
        f"execute as @e[type=minecraft:hopper_minecart,x={X0},y={Y0},z={Z0},dx={LAENGE + 1},dy=2,dz={reihen[-1] + 1}] "
        f"at @s align xz run tp @s ~0.5 {Y0 + 1 + 0.0625} ~0.5",
        f"data modify storage bam:umbau Items set from block {pos(CX, 0, TZ)} Items",
    ] + crafter + [f"data modify block {pos(-1, 0, TZ)} Items set from storage bam:umbau Items"]
else:
    befehle += crafter
    for k in range(ETAGEN):
        befehle += bepflanzen(k)
for b in befehle:
    print(b)
