"""Baut das Datapack „Eisenfarm“: eine kompakte Iron-Golem-Farm, einmalig per Datapack errichtet.

Aufruf:  python3 eisenfarm.py <ort.json> [zip-datei] [entpackt-ordner]

ort.json:  {"ecke": [x, y, z]}   x/z: Nordwest-Ecke des 2×2-Lochs, y: Bodenhöhe (Truhe steht hier)

Aufbau (von unten nach oben, G = Bodenhöhe):
  G       Doppeltruhe, davor eine Nische zum Rankommen
  G+1     4 Trichter
  G+2     Tötungszelle: Golems stehen hier, ihr Kopf steckt in der Lava
  G+3     Schilder halten die Lava
  G+4     Lava
  G+5     zweite Schildlage: hält das Wasser von der Lava fern
  G+6     Plattform 6 × 6 mit 2 × 2-Loch in der Mitte, Wände aus Glas;
          Wasserquellen am Rand schieben die Golems ins Loch
  G+10    Glasdecke mit Leuchtstein (hier spawnen keine Golems)
  G+11    drei Dorfbewohner auf Betten in Glaskabinen, daneben ein Zombie unter Leuchtstein
Nach dem Bau testet das Pack sich selbst und schreibt das Ergebnis ins Scoreboard ef.test.
"""
import json
import os
import shutil
import sys
import zipfile

NS = "eisenfarm"
FORMAT_MIN, FORMAT_MAX = 71, 121

ORT = json.load(open(sys.argv[1]))
HIER = os.path.dirname(os.path.abspath(__file__))
ZIP = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HIER, "..", "Eisenfarm.zip")
ORDNER = sys.argv[3] if len(sys.argv) > 3 else None
X0, G, Z0 = ORT["ecke"]

dateien = {}
bloecke = {}     # relative Position -> Block; später in fester Reihenfolge gesetzt


def datei(pfad, zeilen):
    text = "\n".join(zeilen) if isinstance(zeilen, list) else zeilen
    dateien[pfad] = text.rstrip("\n") + "\n"


def funktion(name, zeilen):
    datei(f"data/{NS}/function/{name}.mcfunction", zeilen)


def setze(x, y, z, blk):
    bloecke[(x, y, z)] = blk


def box(x1, y1, z1, x2, y2, z2, blk):
    for x in range(x1, x2 + 1):
        for y in range(y1, y2 + 1):
            for z in range(z1, z2 + 1):
                setze(x, y, z, blk)


WAND = "stone_bricks"
LOCH = [(0, 0), (1, 0), (0, 1), (1, 1)]

# Turm mit Tötungszelle (Wände x/z = -1 und 2)
box(-1, -1, -1, 2, 6, 2, WAND)
box(0, 2, 0, 1, 6, 1, "air")
setze(0, 1, 0, "hopper[facing=east]")
setze(0, 1, 1, "hopper[facing=east]")
setze(1, 1, 0, "hopper[facing=south]")
setze(1, 1, 1, "hopper[facing=down]")
setze(1, 0, 0, "chest[facing=east,type=left]")
setze(1, 0, 1, "chest[facing=east,type=right]")
setze(0, 0, 0, WAND)
setze(0, 0, 1, WAND)
setze(2, 0, 1, "air")                             # Nische vor der Truhe
setze(2, 1, 1, "air")
setze(2, -1, 1, WAND)
for x, z in LOCH:                                 # Schilder an der Außenwand, Lava darüber
    setze(x, 3, z, f"oak_wall_sign[facing={'east' if x == 0 else 'west'}]")
    setze(x, 4, z, "lava")
    setze(x, 5, z, f"oak_wall_sign[facing={'east' if x == 0 else 'west'}]")

# Plattform 6 × 6 (x/z -2..3) mit Loch, Glaswände, Decke mit Leuchtstein
box(-2, 6, -2, 3, 6, 3, "smooth_stone")
for x, z in LOCH:
    setze(x, 6, z, "air")
box(-3, 7, -3, 4, 9, 4, "glass")
box(-2, 7, -2, 3, 9, 3, "air")
RAND = [(x, z) for x in range(-2, 4) for z in range(-2, 4) if x in (-2, 3) or z in (-2, 3)]
for x, z in RAND:
    setze(x, 7, z, "water")
box(-3, 10, -3, 4, 10, 4, "glass")
for x, z in [(-2, -2), (3, -2), (-2, 3), (3, 3), (0, -2), (1, 3), (-2, 1), (3, 0)]:
    setze(x, 10, z, "glowstone")

# Kabinen für drei Dorfbewohner (x -1..2, z -3..3), Betten Fuß bei x 0, Kopf bei x 1
box(-1, 11, -3, 2, 13, 3, "glass")
box(-1, 14, -3, 2, 14, 3, "glass")
BETTEN = (-2, 0, 2)
for z in BETTEN:
    setze(0, 11, z, "white_bed[facing=east,part=foot]")
    setze(1, 11, z, "white_bed[facing=east,part=head]")
    box(0, 12, z, 1, 13, z, "air")
# Zombie-Zelle direkt daneben, Leuchtstein als Dach gegen die Sonne
box(3, 11, -1, 4, 12, 1, "glass")
box(3, 11, 0, 3, 12, 0, "air")
setze(3, 13, 0, "glowstone")


def welt(x, y, z):
    return X0 + x, G + y, Z0 + z


# Reihenfolge: feste Blöcke, Luft, Anbauteile (Truhen, Trichter, Betten, Schilder), zuletzt Lava
def rang(blk):
    if blk in ("lava", "water"):
        return 3
    if blk.startswith(("hopper", "chest", "white_bed", "oak_wall_sign")):
        return 2
    return 0 if blk != "air" else 1


befehle = []
for (x, y, z), blk in sorted(bloecke.items(), key=lambda e: (rang(e[1]), e[0][1], e[0][0], e[0][2])):
    wx, wy, wz = welt(x, y, z)
    befehle.append(f"setblock {wx} {wy} {wz} minecraft:{blk}")
bx, by, bz = welt(0, 11, 0)
for z in BETTEN:
    vx, vy, vz = welt(1, 11, z)
    befehle.append(f"summon minecraft:villager {vx + 0.5} {vy + 0.6} {vz + 0.5} "
                   f"{{PersistenceRequired:1b,Tags:[\"ef.dorf\"],"
                   f"VillagerData:{{profession:\"minecraft:none\",level:1,type:\"minecraft:plains\"}}}}")
zx, zy, zz = welt(3, 11, 0)
befehle.append(f"summon minecraft:zombie {zx + 0.5} {zy} {zz + 0.5} "
               f"{{PersistenceRequired:1b,CanPickUpLoot:0b,IsBaby:0b,Tags:[\"ef.zombie\"]}}")

xs = [welt(*p)[0] for p in bloecke]
zs = [welt(*p)[2] for p in bloecke]
FL = f"{min(xs)} {min(zs)} {max(xs)} {max(zs)}"
LADEN = " ".join(f"if loaded {x} 0 {z}" for x in (min(xs), max(xs)) for z in (min(zs), max(zs)))

funktion("load", [
    "scoreboard objectives add ef.zustand dummy",
    "scoreboard objectives add ef.test dummy",
    "# #gebaut: 1 = erste Version ohne Wasser, 2 = aktuell",
    f"execute unless score #gebaut ef.zustand matches 1.. unless score #stufe ef.zustand matches 1.. run function {NS}:start",
    f"execute if score #gebaut ef.zustand matches 1 unless score #stufe ef.zustand matches 1.. run function {NS}:start_update",
])
funktion("tick", [f"execute if score #stufe ef.zustand matches 1 {LADEN} run function {NS}:bauen",
                  f"execute if score #stufe ef.zustand matches 2 {LADEN} run function {NS}:update"])
funktion("start", [f"forceload add {FL}", "scoreboard players set #stufe ef.zustand 1"])
funktion("start_update", [f"forceload add {FL}", "scoreboard players set #stufe ef.zustand 2"])
funktion("bauen", befehle + [
    "scoreboard players set #stufe ef.zustand 0",
    "scoreboard players set #gebaut ef.zustand 2",
    f"schedule function {NS}:test/t1 100t",
])
update = []
for x, z in LOCH:
    wx, wy, wz = welt(x, 5, z)
    update.append(f"setblock {wx} {wy} {wz} minecraft:oak_wall_sign[facing={'east' if x == 0 else 'west'}]")
for x, z in RAND:
    wx, wy, wz = welt(x, 7, z)
    update.append(f"setblock {wx} {wy} {wz} minecraft:water")
funktion("update", ["# Nachrüsten: Schildsperre über der Lava und Wasser auf der Plattform"] + update + [
    "scoreboard players set #stufe ef.zustand 0",
    "scoreboard players set #gebaut ef.zustand 2",
    f"schedule function {NS}:test/t1 100t",
])

kx, ky, kz = welt(1, 8, 1)
cx, cy, cz = welt(1, 0, 1)
lava = " ".join(f"if block {' '.join(map(str, welt(x, 4, z)))} minecraft:lava" for x, z in LOCH)
funktion("test/t1", [
    "# Testgolem direkt über das Loch: fällt er in die Lava, und landet Eisen in der Truhe?",
    f"summon minecraft:iron_golem {kx}.0 {ky} {kz}.0 {{Tags:[\"ef.test\"]}}",   # .0: genau über der Lochmitte
    f"schedule function {NS}:test/t2 2400t",
])
funktion("test/t2", [
    f"execute store result score #golem_lebt ef.test if entity @e[type=minecraft:iron_golem,tag=ef.test]",
    f"execute store success score #eisen ef.test if items block {cx} {cy} {cz} container.* minecraft:iron_ingot",
    f"execute store success score #lava ef.test {lava}",
    f"execute store result score #dorfbewohner ef.test if entity @e[type=minecraft:villager,tag=ef.dorf]",
    f"execute store result score #zombie ef.test if entity @e[type=minecraft:zombie,tag=ef.zombie]",
    f"execute store result score #betten ef.test if entity "
    f"@e[type=minecraft:villager,tag=ef.dorf,nbt={{Brain:{{memories:{{\"minecraft:home\":{{}}}}}}}}]",
    f"forceload remove {FL}",
    "scoreboard players set #fertig ef.test 1",
])

datei("data/minecraft/tags/function/load.json", json.dumps({"values": [f"{NS}:load"]}, indent=2))
datei("data/minecraft/tags/function/tick.json", json.dumps({"values": [f"{NS}:tick"]}, indent=2))
datei("pack.mcmeta", json.dumps({"pack": {
    "description": "Eisenfarm", "pack_format": FORMAT_MIN, "supported_formats": [FORMAT_MIN, FORMAT_MAX],
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
        info = zipfile.ZipInfo(pfad, date_time=(2026, 1, 1, 0, 0, 0))
        zf.writestr(info, dateien[pfad].encode("utf-8"))
print(f"{len(bloecke)} Blöcke, {len(befehle)} Befehle, Forceload {FL}")
