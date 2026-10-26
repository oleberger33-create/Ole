"""Baut das Datapack „Holzfarm“: ein Feld mit 9 Setzlingen, die von selbst zu echten Bäumen wachsen.

Aufruf:  python3 holzfarm.py <ort.json> [zip-datei] [entpackt-ordner]

ort.json:  {"ecke": [x, y, z]}   Nordwest-Ecke des Feldes, y: Höhe direkt über dem Gras

Aufbau (relativ zur Ecke, Feld 17 × 17):
  Bäume    3 Reihen à 3 Setzlinge im Abstand 5: Eiche (z 3), Birke (z 8), Fichte (z 13), x 3 / 8 / 13
  Laternen auf Zaunpfosten zwischen den Bäumen: Die Setzlinge wachsen auch nachts, Monster spawnen nicht
  Lager    Doppeltruhe am Westrand (x 0, z 8 … 9), davor ein Trichter
Alle 2 Sekunden schaut das Pack, ob ein Setzling zum Stamm geworden ist. Dann nimmt es Stamm und Laub weg,
wirft das Holz Stück für Stück in den Trichter und pflanzt einen neuen Setzling. Blumen auf dem Feld kommen
beim Bau weg, sonst bauen Bienen Nester in die Bäume.
"""
import json
import os
import shutil
import sys
import zipfile

NS = "holz"
FORMAT_MIN, FORMAT_MAX = 71, 121
ORT = json.load(open(sys.argv[1]))
HIER = os.path.dirname(os.path.abspath(__file__))
ZIP = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HIER, "..", "Holzfarm.zip")
ORDNER = sys.argv[3] if len(sys.argv) > 3 else None
X0, Y0, Z0 = ORT["ecke"]
dateien = {}


def datei(pfad, zeilen):
    text = "\n".join(zeilen) if isinstance(zeilen, list) else zeilen
    dateien[pfad] = text.rstrip("\n") + "\n"


def funktion(name, zeilen):
    datei(f"data/{NS}/function/{name}.mcfunction", zeilen)


def welt(x, y, z):
    return X0 + x, Y0 + y, Z0 + z


def pos(x, y, z):
    return "%d %d %d" % welt(x, y, z)


GROESSE = 17
BAEUME = [(x, z, art) for z, art in ((3, "oak"), (8, "birch"), (13, "spruce")) for x in (3, 8, 13)]
PFOSTEN = [(5, 5), (10, 5), (5, 10), (10, 10), (0, 1), (15, 1), (15, 8), (0, 16), (15, 16)]
KISTE = [((0, 0, 8), "left"), ((0, 0, 9), "right")]             # Blick nach Osten: links = Norden
TRICHTER = (1, 0, 9)
REICHWEITE, HOEHE = 4, 15                                       # Kasten um jeden Stamm, groß genug für große Eichen
PFLANZEN = ["short_grass", "tall_grass", "fern", "large_fern", "dandelion", "poppy", "oxeye_daisy", "azure_bluet",
            "cornflower", "allium", "lily_of_the_valley", "pink_petals", "wildflowers", "leaf_litter", "bush",
            "firefly_bush", "sunflower", "lilac", "rose_bush", "peony"]

# ---------------------------------------------------------------- Bau
bauen = []
for p in PFLANZEN:
    bauen.append(f"fill {pos(0, 0, 0)} {pos(GROESSE - 1, 1, GROESSE - 1)} minecraft:air replace minecraft:{p}")
for x, z, art in BAEUME:
    bauen.append(f"execute unless block {pos(x, -1, z)} minecraft:grass_block unless block {pos(x, -1, z)} minecraft:dirt "
                 f"run setblock {pos(x, -1, z)} minecraft:grass_block")
    bauen.append(f"setblock {pos(x, 0, z)} minecraft:{art}_sapling")
for x, z in PFOSTEN:
    bauen.append(f"setblock {pos(x, 0, z)} minecraft:oak_fence")
    bauen.append(f"setblock {pos(x, 1, z)} minecraft:lantern")
for (x, y, z), typ in KISTE:
    bauen.append(f"setblock {pos(x, y, z)} minecraft:chest[facing=east,type={typ}]")
bauen.append(f"setblock {pos(*TRICHTER)} minecraft:hopper[facing=west]")

# ---------------------------------------------------------------- Ernte
ex, ey, ez = welt(*TRICHTER)
EINWURF = f"{ex + 0.5} {ey + 1} {ez + 0.5}"
pruefen = [f"schedule function {NS}:pruefen 40t"]
for i, (x, z, art) in enumerate(BAEUME):
    pruefen.append(f"execute if block {pos(x, 0, z)} minecraft:{art}_log run function {NS}:baum/{i}")
    von = pos(x - REICHWEITE, 0, z - REICHWEITE)
    bis = pos(x + REICHWEITE, HOEHE, z + REICHWEITE)
    funktion(f"baum/{i}", [
        f"execute store result score #holz holz.zustand run fill {von} {bis} minecraft:air replace minecraft:{art}_log",
        f"fill {von} {bis} minecraft:air replace minecraft:{art}_leaves",
        f"fill {von} {bis} minecraft:air replace minecraft:bee_nest",
        f"setblock {pos(x, 0, z)} minecraft:{art}_sapling",
        f"execute if score #holz holz.zustand matches 1.. run function {NS}:gib/{art}",
        f"scoreboard players add #baeume holz.zustand 1",
    ])
for art in sorted({a for _, _, a in BAEUME}):
    funktion(f"gib/{art}", [
        f"summon minecraft:item {EINWURF} {{Item:{{id:\"minecraft:{art}_log\",count:1}}}}",
        "scoreboard players remove #holz holz.zustand 1",
        f"execute if score #holz holz.zustand matches 1.. run function {NS}:gib/{art}",
    ])

xs = [X0, X0 + GROESSE - 1]
zs = [Z0, Z0 + GROESSE - 1]
FL = f"{xs[0]} {zs[0]} {xs[1]} {zs[1]}"
LADEN = " ".join(f"if loaded {x} {Y0} {z}" for x in xs for z in zs)

funktion("load", [
    "scoreboard objectives add holz.zustand dummy",
    "# #gebaut: 1 = Feld steht; #baeume zählt die geernteten Bäume",
    f"execute unless score #gebaut holz.zustand matches 1.. unless score #stufe holz.zustand matches 1.. run function {NS}:start",
    f"schedule function {NS}:pruefen 40t",
])
funktion("start", [f"forceload add {FL}", "scoreboard players set #stufe holz.zustand 1"])
funktion("tick", [f"execute if score #stufe holz.zustand matches 1 {LADEN} run function {NS}:bauen"])
funktion("bauen", bauen + ["scoreboard players set #stufe holz.zustand 0", "scoreboard players set #gebaut holz.zustand 1",
                           f"forceload remove {FL}"])
funktion("pruefen", pruefen)

datei("data/minecraft/tags/function/load.json", json.dumps({"values": [f"{NS}:load"]}, indent=2))
datei("data/minecraft/tags/function/tick.json", json.dumps({"values": [f"{NS}:tick"]}, indent=2))
datei("pack.mcmeta", json.dumps({"pack": {
    "description": "Holzfarm", "pack_format": FORMAT_MIN, "supported_formats": [FORMAT_MIN, FORMAT_MAX],
    "min_format": FORMAT_MIN, "max_format": FORMAT_MAX}}, indent=2))

if ORDNER:
    if os.path.isdir(ORDNER):
        shutil.rmtree(ORDNER)
    for pfad, inhalt in dateien.items():
        voll = os.path.join(ORDNER, pfad)
        os.makedirs(os.path.dirname(voll), exist_ok=True)
        with open(voll, "w", encoding="utf-8", newline="\n") as f:
            f.write(inhalt)
with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
    for pfad in sorted(dateien):
        zf.writestr(zipfile.ZipInfo(pfad, date_time=(2026, 1, 1, 0, 0, 0)), dateien[pfad].encode("utf-8"))
print(f"{len(bauen)} Baubefehle, {len(BAEUME)} Bäume, Forceload {FL}")
