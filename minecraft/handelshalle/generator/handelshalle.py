"""Gibt die Befehle für die Handelshalle aus (rein vanilla, einmal per Konsole gesetzt).

Aufruf:  python3 handelshalle.py <ort.json>

ort.json:  {"ecke": [x, y, z]}   erste Zelle der Nordreihe, y: Höhe über dem Boden

Querschnitt von Nord nach Süd (z):  0 Wand · 1 Zelle · 2 Arbeitsblock · 3 Gang · 4 Arbeitsblock · 5 Zelle · 6 Wand
Die Zellen liegen bei x 0/2/4/6/8, dazwischen Wände. Der Arbeitsblock steht vor dem Dorfbewohner auf Fußhöhe;
darüber bleibt ein Block Luft, durch den man handelt. Die Decke liegt 2 hoch, so kommt kein Dorfbewohner über
seinen Arbeitsblock. Hinten in jeder Zelle ein Fenster. Eingang im Westen (Tür, auf „leicht“ brechen Zombies
keine Türen auf), Licht aus Seelaternen in der Gangdecke.
"""
import json
import sys

ORT = json.load(open(sys.argv[1]))
X0, Y0, Z0 = ORT["ecke"]
BERUFE = {   # (x, z): (Arbeitsblock, Beruf)
    (0, 1): ("brewing_stand", "Kleriker"), (2, 1): ("composter", "Bauer"), (4, 1): ("fletching_table", "Pfeilmacher"),
    (6, 1): ("blast_furnace[facing=south]", "Rüstungsschmied"), (8, 1): ("smithing_table", "Werkzeugschmied"),
    (0, 5): ("lectern[facing=north]", "Bibliothekar"), (2, 5): ("lectern[facing=north]", "Bibliothekar"),
    (4, 5): ("lectern[facing=north]", "Bibliothekar"), (6, 5): ("grindstone[face=floor,facing=north]", "Waffenschmied"),
    (8, 5): ("stonecutter[facing=north]", "Steinmetz"),
}


def pos(x, y, z):
    return "%d %d %d" % (X0 + x, Y0 + y, Z0 + z)


def fill(x1, y1, z1, x2, y2, z2, blk, extra=""):
    return f"fill {pos(x1, y1, z1)} {pos(x2, y2, z2)} minecraft:{blk}{extra}"


befehle = [
    fill(-1, 0, 0, 9, 4, 6, "air"),                                   # Gras und Blumen weg
    fill(-1, -3, 0, 9, -2, 6, "dirt", " replace minecraft:air"),      # Mulden im Boden füllen
    fill(-1, -1, 0, 9, -1, 6, "stone_bricks"),                        # Boden
    fill(-1, 0, 0, 9, 1, 6, "spruce_planks"),                         # Block, aus dem alles ausgeschnitten wird
    fill(0, 0, 3, 8, 1, 3, "air"),                                    # Gang
]
for (x, z), (blk, _) in BERUFE.items():
    vorne = 2 if z == 1 else 4
    befehle += [fill(x, 0, z, x, 1, z, "air"),                        # Zelle
                f"setblock {pos(x, 0, vorne)} minecraft:{blk}",
                f"setblock {pos(x, 1, vorne)} minecraft:air",          # hier handelt man
                f"setblock {pos(x, 1, 0 if z == 1 else 6)} minecraft:glass"]
befehle += [
    fill(-1, 2, 0, 9, 2, 6, "spruce_planks"),                         # Decke
    fill(-1, 3, 0, 9, 3, 6, "spruce_slab[type=bottom]"),              # Dach
    f"setblock {pos(9, 1, 3)} minecraft:glass",                       # Fenster am Gangende
    f"setblock {pos(-1, 0, 3)} minecraft:spruce_door[facing=east,half=lower,hinge=left]",
    f"setblock {pos(-1, 1, 3)} minecraft:spruce_door[facing=east,half=upper,hinge=left]",
]
for x, z in ((-1, 0), (9, 0), (-1, 6), (9, 6)):
    befehle.append(fill(x, 0, z, x, 2, z, "stripped_spruce_log"))     # Eckpfosten
for x in (1, 4, 7):
    befehle.append(f"setblock {pos(x, 2, 3)} minecraft:sea_lantern")
for x, z in ((-1, 1), (-1, 5)):
    befehle.append(f"setblock {pos(x - 1, 1, z)} minecraft:wall_torch[facing=west]")  # Außenlicht neben der Tür
# Arbeitslose Dorfbewohner in die Zellen; jeder nimmt den Arbeitsblock vor sich
for (x, z) in BERUFE:
    befehle.append(f"summon minecraft:villager {X0 + x + 0.5} {Y0} {Z0 + z + 0.5} "
                   "{VillagerData:{profession:\"minecraft:none\",level:1,type:\"minecraft:plains\"},Tags:[\"hh.halle\"]}")
for b in befehle:
    print(b)
