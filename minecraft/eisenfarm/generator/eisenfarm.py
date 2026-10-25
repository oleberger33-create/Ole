"""Baut das Datapack „Eisenfarm“: eine kompakte Iron-Golem-Farm, einmalig per Datapack errichtet.

Aufruf:  python3 eisenfarm.py <ort.json> [zip-datei] [entpackt-ordner]

ort.json:  {"ecke": [x, y, z]}   x/z: Nordwest-Ecke des 2×2-Lochs, y: Bodenhöhe (Truhe steht hier)

Aufbau (von unten nach oben, G = Bodenhöhe, H = Höhe des oberen Teils über dem Turm):
  G       Doppeltruhe, davor eine Nische zum Rankommen
  G+1     4 Trichter
  G+2     Tötungszelle: Golems stehen hier, ihr Kopf steckt in der Lava
  G+3     Schilder halten die Lava
  G+4     Lava
  G+5     Schilder (halten Wasser von der Lava fern), darüber der Fallschacht
  G+H+5   Schilder direkt unter dem Loch: das Plattformwasser bleibt oben
  G+H+6   Plattform 6 × 6 mit 2 × 2-Loch, Glaswände; Wasser vom Rand schiebt die Golems ins Loch
  G+H+10  Glasdecke mit Leuchtstein (hier spawnen keine Golems)
  G+H+11  drei Dorfbewohner auf Betten; zur Zombie-Seite hin nur Zäune, damit sie ihn sehen
          (über Zäune hinweg), aber niemand hinüberkommt
Der obere Teil liegt so hoch, dass Golems des Dorfs am Boden mehr als 16 Blöcke unter den
Dorfbewohnern bleiben – sonst „sehen“ sie einen Golem und rufen keinen eigenen.

Der Zombie steht auf einem Block, den ein Klebriger Kolben (gesteuert von einem Tageslichtsensor) bewegt:
Tagsüber steht er einen Block höher und schaut über die Glaskante – die Dorfbewohner sehen ihn, geraten in
Panik und rufen Golems. Nachts sackt er ab und ist rundum von Glas umgeben: keine Panik, alle schlafen.
Ohne Schlaf in den letzten 20 Minuten rufen Dorfbewohner keine Golems.

Versionen (#gebaut): 1 = ohne Wasser, 2 = Wasser, 3 = hochgesetzt mit Zäunen, 4 = Nachtsperre (aktuell).
Ältere Stände werden nachgerüstet; danach testet das Pack sich selbst (Scoreboard ef.test).
"""
import json
import os
import shutil
import sys
import zipfile

NS = "eisenfarm"
FORMAT_MIN, FORMAT_MAX = 71, 121
H = 11            # Anhebung des oberen Teils (Version 3)

ORT = json.load(open(sys.argv[1]))
HIER = os.path.dirname(os.path.abspath(__file__))
ZIP = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HIER, "..", "Eisenfarm.zip")
ORDNER = sys.argv[3] if len(sys.argv) > 3 else None
X0, G, Z0 = ORT["ecke"]

dateien = {}
WAND = "stone_bricks"
LOCH = [(0, 0), (1, 0), (0, 1), (1, 1)]
BETTEN = (-2, 0, 2)


def datei(pfad, zeilen):
    text = "\n".join(zeilen) if isinstance(zeilen, list) else zeilen
    dateien[pfad] = text.rstrip("\n") + "\n"


def funktion(name, zeilen):
    datei(f"data/{NS}/function/{name}.mcfunction", zeilen)


def schild(x):
    return f"oak_wall_sign[facing={'east' if x == 0 else 'west'}]"


def entwurf(h, version):
    """Relative Blöcke der Farm. h hebt alles ab der Plattform an."""
    b = {}

    def box(x1, y1, z1, x2, y2, z2, blk):
        for x in range(x1, x2 + 1):
            for y in range(y1, y2 + 1):
                for z in range(z1, z2 + 1):
                    b[(x, y, z)] = blk

    box(-1, -1, -1, 2, 6 + h, 2, WAND)                 # Turm
    box(0, 2, 0, 1, 6 + h, 1, "air")                   # Tötungszelle und Schacht
    b[(0, 1, 0)] = "hopper[facing=east]"
    b[(0, 1, 1)] = "hopper[facing=east]"
    b[(1, 1, 0)] = "hopper[facing=south]"
    b[(1, 1, 1)] = "hopper[facing=down]"
    b[(1, 0, 0)] = "chest[facing=east,type=left]"
    b[(1, 0, 1)] = "chest[facing=east,type=right]"
    b[(2, 0, 1)] = "air"                               # Nische vor der Truhe
    b[(2, 1, 1)] = "air"
    for x, z in LOCH:
        b[(x, 3, z)] = schild(x)
        b[(x, 4, z)] = "lava"
        if version >= 2:
            b[(x, 5, z)] = schild(x)
        if version >= 3:
            b[(x, 5 + h, z)] = schild(x)
    p = 6 + h                                          # Plattformboden
    box(-2, p, -2, 3, p, 3, "smooth_stone")
    for x, z in LOCH:
        b[(x, p, z)] = "air"
    box(-3, p + 1, -3, 4, p + 3, 4, "glass")
    box(-2, p + 1, -2, 3, p + 3, 3, "air")
    if version >= 2:
        for x in range(-2, 4):
            for z in range(-2, 4):
                if x in (-2, 3) or z in (-2, 3):
                    b[(x, p + 1, z)] = "water"
    d = p + 4                                          # Glasdecke
    box(-3, d, -3, 4, d, 4, "glass")
    for x, z in [(-2, -2), (3, -2), (-2, 3), (3, 3), (0, -2), (1, 3), (-2, 1), (3, 0)]:
        b[(x, d, z)] = "glowstone"
    v = d + 1                                          # Betten / Füße der Dorfbewohner
    box(-1, v, -3, 2, v + 2, 3, "glass")
    box(-1, v + 3, -3, 2, v + 3, 3, "glass")
    for z in BETTEN:
        b[(0, v, z)] = "white_bed[facing=east,part=foot]"
        b[(1, v, z)] = "white_bed[facing=east,part=head]"
        b[(0, v + 1, z)] = b[(1, v + 1, z)] = b[(0, v + 2, z)] = b[(1, v + 2, z)] = "air"
    if version >= 3:
        # Zur Zombie-Seite (x = 2) nur Zäune, darüber Luft; Zombie zwei Spalten weiter bei x = 4
        for z in range(-3, 4):
            b[(2, v, z)] = "oak_fence"
            b[(2, v + 1, z)] = b[(2, v + 2, z)] = "air"
        for x, z in [(3, 0), (5, 0), (4, -1), (4, 1)]:
            b[(x, v, z)] = "oak_fence"
        b[(4, v, 0)] = b[(4, v + 1, 0)] = "air"
        box(4, v + 2, -1, 5, v + 2, 1, "glowstone")    # Dach: gegen die Sonne und gegen Golems auf den Zäunen
        box(3, d, -1, 5, d, 1, "glass")                # Boden unter der Zombie-Ecke
    if version >= 4:
        # Zombie-Aufzug: zwei Glasringe (Füße/Kopf in der Nacht), darüber offen, Leuchtstein nur über dem Zombie
        for x, z in [(3, 0), (5, 0), (4, -1), (4, 1)]:
            b[(x, v, z)] = b[(x, v + 1, z)] = "glass"
            b[(x, v + 2, z)] = "air"
            b[(x, v + 3, z)] = "glass"
        b[(5, v + 2, -1)] = b[(5, v + 2, 1)] = "air"
        b[(4, v, 0)] = b[(4, v + 1, 0)] = b[(4, v + 2, 0)] = "air"
        b[(4, v + 3, 0)] = "glowstone"
        b[(4, v - 1, 0)] = "stone"                     # Stand des Zombies (nachts hier, tagsüber eins höher)
        b[(4, v - 2, 0)] = "sticky_piston[facing=up,extended=false]"
        b[(5, v - 2, 0)] = "daylight_detector[inverted=false]"
    if version < 3:
        box(3, v, -1, 4, v + 1, 1, "glass")
        b[(3, v, 0)] = b[(3, v + 1, 0)] = "air"
        b[(3, v + 2, 0)] = "glowstone"
    return b, v


def welt(x, y, z):
    return X0 + x, G + y, Z0 + z


def rang(blk):
    if blk in ("lava", "water"):
        return 3
    if blk.startswith(("hopper", "chest", "white_bed", "oak_wall_sign", "oak_fence", "sticky_piston",
                       "daylight_detector")):
        return 2
    return 0 if blk != "air" else 1


def setzbefehle(bloecke):
    out = []
    for (x, y, z), blk in sorted(bloecke.items(), key=lambda e: (rang(e[1]), e[0][1], e[0][0], e[0][2])):
        wx, wy, wz = welt(x, y, z)
        out.append(f"setblock {wx} {wy} {wz} minecraft:{blk}")
    return out


neu, V = entwurf(H, 4)
alt, V_ALT = entwurf(0, 2)


def dorfbewohner_zielorte():
    return [welt(1, V, z) for z in BETTEN]


# Vollbau (neue Welt): alles auf einmal, dann Dorfbewohner und Zombie
bauen = setzbefehle(neu)
for vx, vy, vz in dorfbewohner_zielorte():
    bauen.append(f"summon minecraft:villager {vx + 0.5} {vy + 0.6} {vz + 0.5} "
                 f"{{PersistenceRequired:1b,Tags:[\"ef.dorf\"],"
                 f"VillagerData:{{profession:\"minecraft:none\",level:1,type:\"minecraft:plains\"}}}}")
zx, zy, zz = welt(4, V, 0)
bauen.append(f"summon minecraft:zombie {zx + 0.5} {zy} {zz + 0.5} "
             f"{{PersistenceRequired:1b,CanPickUpLoot:0b,IsBaby:0b,Tags:[\"ef.zombie\"]}}")

# Nachrüsten von Version 2: altes Wasser weg, neuen oberen Teil bauen, Bewohner umziehen, Rest abräumen
umbau = ["# Version 2 → 3: oberen Teil um %d Blöcke anheben, Zäune statt Glas zum Zombie" % H]
for (x, y, z), blk in alt.items():
    if blk == "water":
        umbau.append("setblock %d %d %d minecraft:air" % welt(x, y, z))
umbau += setzbefehle({p: blk for p, blk in neu.items() if p[1] >= 6})
for i, (vx, vy, vz) in enumerate(dorfbewohner_zielorte()):
    umbau.append(f"tp @e[type=minecraft:villager,tag=ef.dorf,tag=!ef.umgezogen,limit=1,sort=nearest] "
                 f"{vx + 0.5} {vy + 0.6} {vz + 0.5}")
    umbau.append(f"tag @e[type=minecraft:villager,tag=ef.dorf,x={vx},y={vy},z={vz},dx=0,dy=1,dz=0] add ef.umgezogen")
umbau.append(f"tp @e[type=minecraft:zombie,tag=ef.zombie,limit=1] {zx + 0.5} {zy} {zz + 0.5}")
umbau.append("tag @e[type=minecraft:villager,tag=ef.umgezogen] remove ef.umgezogen")
umbau += setzbefehle({p: "air" for p in alt if p not in neu and p[1] >= 6})

alle = list(neu) + list(alt) + [(5, V, 0)]
xs = [welt(*p)[0] for p in alle]
zs = [welt(*p)[2] for p in alle]
FL = f"{min(xs)} {min(zs)} {max(xs)} {max(zs)}"
LADEN = " ".join(f"if loaded {x} 0 {z}" for x in (min(xs), max(xs)) for z in (min(zs), max(zs)))

funktion("load", [
    "scoreboard objectives add ef.zustand dummy",
    "scoreboard objectives add ef.test dummy",
    "# #gebaut: 1 = ohne Wasser, 2 = mit Wasser, 3 = hochgesetzt, 4 = mit Nachtsperre (aktuell)",
    f"execute unless score #gebaut ef.zustand matches 1.. unless score #stufe ef.zustand matches 1.. run function {NS}:start",
    f"execute if score #gebaut ef.zustand matches 1..2 unless score #stufe ef.zustand matches 1.. run function {NS}:start_umbau",
    f"execute if score #gebaut ef.zustand matches 3 unless score #stufe ef.zustand matches 1.. run function {NS}:start_sperre",
])
funktion("tick", [f"execute if score #stufe ef.zustand matches 1 {LADEN} run function {NS}:bauen",
                  f"execute if score #stufe ef.zustand matches 3 {LADEN} run function {NS}:umbau",
                  f"execute if score #stufe ef.zustand matches 4 {LADEN} run function {NS}:sperre"])
funktion("start", [f"forceload add {FL}", "scoreboard players set #stufe ef.zustand 1"])
funktion("start_umbau", [f"forceload add {FL}", "scoreboard players set #stufe ef.zustand 3"])
funktion("start_sperre", [f"forceload add {FL}", "scoreboard players set #stufe ef.zustand 4"])
fertig = ["scoreboard players set #stufe ef.zustand 0", "scoreboard players set #gebaut ef.zustand 4",
          f"schedule function {NS}:test/s1 40t", f"schedule function {NS}:test/t1 100t"]
funktion("bauen", bauen + fertig)
funktion("umbau", umbau + fertig)
v3, _ = entwurf(H, 3)
aenderung = {p: blk for p, blk in neu.items() if v3.get(p) != blk}
aenderung.update({p: "air" for p in v3 if p not in neu})
funktion("sperre", ["# Version 3 → 4: Zombie-Aufzug mit Tageslichtsensor"] + setzbefehle(aenderung) + fertig)

# Test des Zombie-Aufzugs: Zustand jetzt, dann Kolben per Redstone-Block auf „Tag“ zwingen
sx, sy, sz = welt(4, V, 0)
zombie_oben = f"if entity @e[type=minecraft:zombie,tag=ef.zombie,x={sx},y={sy + 1},z={sz},dx=0,dy=0,dz=0]"
funktion("test/s1", [
    f"execute store success score #nacht ef.test if block {sx + 1} {sy - 2} {sz} minecraft:daylight_detector[power=0]",
    f"execute store success score #zombie_oben_jetzt ef.test {zombie_oben}",
    f"setblock {sx} {sy - 2} {sz + 1} minecraft:redstone_block",
    f"schedule function {NS}:test/s2 20t",
])
funktion("test/s2", [
    f"execute store success score #aufzug_tag ef.test if block {sx} {sy} {sz} minecraft:stone "
    f"if block {sx} {sy - 2} {sz} minecraft:sticky_piston[extended=true]",
    f"execute store success score #zombie_oben_tag ef.test {zombie_oben}",
    f"setblock {sx} {sy - 2} {sz + 1} minecraft:glass",
    f"schedule function {NS}:test/s3 20t",
])
funktion("test/s3", [
    f"execute store success score #zombie_oben_danach ef.test {zombie_oben}",
    "execute store result score #zombie_lebt ef.test if entity @e[type=minecraft:zombie,tag=ef.zombie]",
])

# Selbsttest: Testgolem durchs Loch, danach 25 Minuten beobachten, ob von selbst Eisen kommt
kx, ky, kz = welt(1, 6 + H + 2, 1)
cx, cy, cz = welt(1, 0, 1)
lava = " ".join(f"if block {' '.join(map(str, welt(x, 4, z)))} minecraft:lava" for x, z in LOCH)
eisen = f"if items block {cx} {cy} {cz} container.* minecraft:iron_ingot"
funktion("test/t1", [
    f"summon minecraft:iron_golem {kx}.0 {ky} {kz}.0 {{Tags:[\"ef.test\"]}}",
    f"schedule function {NS}:test/t2 600t",
])
funktion("test/t2", [
    "execute store result score #testgolem_lebt ef.test if entity @e[type=minecraft:iron_golem,tag=ef.test]",
    f"execute store result score #eisen_nach_test ef.test {eisen}",
    f"execute store success score #lava ef.test {lava}",
    "execute store result score #dorfbewohner ef.test if entity @e[type=minecraft:villager,tag=ef.dorf]",
    "execute store result score #zombie ef.test if entity @e[type=minecraft:zombie,tag=ef.zombie]",
    f"schedule function {NS}:test/t3 6000t",
])
funktion("test/t3", [
    f"execute store result score #eisen_5min ef.test {eisen}",
    "execute store result score #betten ef.test if entity "
    "@e[type=minecraft:villager,tag=ef.dorf,nbt={Brain:{memories:{\"minecraft:home\":{}}}}]",
    f"schedule function {NS}:test/t4 18000t",
])
funktion("test/t4", [
    f"execute store result score #eisen_20min ef.test {eisen}",
    f"schedule function {NS}:test/t5 24000t",
])
funktion("test/t5", [
    f"execute store result score #eisen_40min ef.test {eisen}",
    f"forceload remove {FL}",
    "scoreboard players set #fertig ef.test 3",
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
print(f"Vollbau {len(bauen)} Befehle, Umbau {len(umbau)} Befehle, Dorfbewohner auf y {G + V}, Forceload {FL}")
