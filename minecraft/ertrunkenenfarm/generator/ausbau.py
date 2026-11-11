"""Gibt die Befehle für den Ausbau der Ertrunkenen-Farm aus (läuft rein vanilla, wird einmal per Konsole gesetzt).

Aufruf:  python3 ausbau.py <ort.json>

ort.json:  {"tank": [x, z]}   Nordwest-Ecke des Innenraums des bestehenden Tanks (18 × 18)

Bestand (Tank A, von den Spielern gebaut): Wasser von 226 bis 294 über einer Schildlage (225), darunter eine Wasserlage
(223), die zu einer Rinne in der Mitte fließt, und der 2 × 2-Schacht hinunter zur Plattform bei 200.

Ertrunkene spawnen in Flüssen in jeder Höhe, im Wasser und im Dunkeln. Das Spiel würfelt pro Chunk und Tick eine Spalte
und eine Höhe zwischen -64 und der obersten Fläche: Je mehr Spalten und Höhe der Tank hat, desto mehr Treffer.
  1. Tank A bis zur Bauhöhe: Wasser bis 318, Dach 319 (69 → 93 Lagen)
  2. Tank B, 18 × 18 westlich daneben (gemeinsame Wand), ebenfalls bis 318. Sein Boden fällt in drei Stufen zu Tank A
     hin ab: Schildlage, Luft, Wasserlage, Boden; jede Wasserlage fließt 7 Blöcke nach Osten (Quelle an der Westkante,
     Stufe 7 an der Kante, also läuft nichts über). Unter den Schildern sinken die Ertrunkenen in die Strömung, die
     schiebt sie zur nächsten Stufe und zuletzt durch die gemeinsame Wand (unten Strömung, darüber ein Schild) auf
     Höhe der Schildlage von Tank A. Dort fallen sie in dessen Wasserlage und weiter wie bisher.
Beide Tanks liegen ganz im Flussbiom und bis 121 Blöcke von der Plattform: Ab 128 Blöcken würden sie sofort verschwinden.
"""
import json
import sys

ORT = json.load(open(sys.argv[1]))
AX, AZ = ORT["tank"]                    # Innenraum A: AX..AX+17, AZ..AZ+17
SCHILD_A = 225
TOP, DACH = 318, 319
W = "cobblestone"
ZN, ZS = AZ - 1, AZ + 18                # Wände Nord/Süd
OST = AX - 1                            # gemeinsame Wand
WEST = AX - 20                          # Westwand von B, Innenraum B: WEST+1 .. OST-1
befehle = []


def fill(x1, y1, z1, x2, y2, z2, blk):
    befehle.append(f"fill {x1} {y1} {z1} {x2} {y2} {z2} minecraft:{blk}")


# 1. Tank A erhöhen
fill(OST, 295, ZN, AX + 18, DACH - 1, ZS, W)
fill(AX, 295, AZ, AX + 17, TOP, AZ + 17, "water")
fill(OST, DACH, ZN, AX + 18, DACH, ZS, "smooth_stone_slab[type=bottom]")

# 2. Tank B: Hülle, dann Stufen von West nach Ost (x-Bereich, Boden = Höhe des Bodens)
STUFEN = [(WEST + 1, WEST + 8, SCHILD_A + 1), (WEST + 9, WEST + 16, SCHILD_A), (WEST + 17, OST - 1, SCHILD_A - 1)]
for y1, y2 in ((SCHILD_A - 1, 271), (272, DACH - 1)):
    fill(WEST, y1, ZN, OST - 1, y2, ZS, W)
for x1, x2, boden in STUFEN:
    fill(x1, boden + 1, AZ, x2, boden + 1, AZ + 17, "air")             # Strömung (Wasser kommt zum Schluss)
    fill(x1, boden + 2, AZ, x2, boden + 2, AZ + 17, "air")
    fill(x1, boden + 3, AZ, x2, boden + 3, AZ + 17, "oak_sign")
    fill(x1, boden + 4, AZ, x2, TOP, AZ + 17, "air")
fill(WEST, DACH, ZN, OST, DACH, ZS, "smooth_stone_slab[type=bottom]")
# Durchgang in der gemeinsamen Wand auf Höhe der Schildlage von A: unten fließt die letzte Strömung noch hinein
# (sonst blieben die Ertrunkenen auf der Wandkante stehen), darüber ein Schild, das das Wasser von A hält
# Vorher die Schilder der ersten Reihe von A umhängen: Sie hingen an der Wand. Fiel ihr Halt weg, fiel das Schild ab und
# riss alle östlich daran hängenden mit (beim ersten Ausbau 153 Stück, Tank A lief in den Schacht aus).
befehle.append(f"fill {AX} {SCHILD_A} {AZ} {AX} {SCHILD_A} {AZ + 17} minecraft:oak_wall_sign[facing=west] strict")
befehle.append(f"fill {OST} {SCHILD_A} {AZ} {OST} {SCHILD_A} {AZ + 17} minecraft:air strict")
befehle.append(f"fill {OST} {SCHILD_A + 1} {AZ} {OST} {SCHILD_A + 1} {AZ + 17} minecraft:oak_sign strict")
# Wasser: Tank B, dann die Quellen der Strömungen
for x1, x2, boden in STUFEN:
    fill(x1, boden + 4, AZ, x2, 271, AZ + 17, "water")
    fill(x1, 272, AZ, x2, TOP, AZ + 17, "water")
    fill(x1, boden + 1, AZ, x1, boden + 1, AZ + 17, "water")

if __name__ == "__main__":
    for b in befehle:
        print(b)
