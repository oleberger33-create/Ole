"""Baut das Datapack „XP-Farm“: einen Mob-Turm ohne Spawner, einmalig per Datapack errichtet.

Aufruf:  python3 xpfarm.py <ort.json> [zip-datei] [entpackt-ordner]

ort.json:  {"loch": [x, y, z]}   x/z: Nordwest-Ecke des 2×2-Lochs, y: Höhe der Spawn-Plattformen
           (die Füße des Spielers stehen 23 Blöcke tiefer, dort liegt der Boden)

Aufbau (relativ zur Plattformhöhe 0):
  3        Decke aus unteren Stufen (darauf spawnt nichts, innen bleibt es dunkel)
  1 … 2    Spawnraum 2 hoch (zu niedrig für Endermen), offene Falltüren über den Kanälen
  0        vier Plattformen, dazwischen Wasserkanäle (Quellen an den Enden), 2 × 2-Loch in der Mitte
  -1 … -21 Fallschacht: 22 Blöcke freier Fall → Zombies, Skelette, Creeper landen mit 1 Herz
  -22      Tötungszelle, davor zwei untere Stufen als Schlitz zum Zuschlagen
  -23      Trichter → Doppeltruhe im Spielerraum; hier stehen die Füße des Spielers
Vor dem Bau setzt das Pack unsichtbare Lichter auf den Boden unter der Plattform, damit dort im
Schatten keine Monster spawnen und der Farm Platz im Mob-Limit wegnehmen.
Danach testet es sich selbst (Scoreboard xp.test).
"""
import collections
import json
import os
import shutil
import sys
import zipfile

NS = "xpfarm"
FORMAT_MIN, FORMAT_MAX = 71, 121
ORT = json.load(open(sys.argv[1]))
HIER = os.path.dirname(os.path.abspath(__file__))
ZIP = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HIER, "..", "XP-Farm.zip")
ORDNER = sys.argv[3] if len(sys.argv) > 3 else None
X0, P, Z0 = ORT["loch"]
dateien = {}


def datei(pfad, zeilen):
    text = "\n".join(zeilen) if isinstance(zeilen, list) else zeilen
    dateien[pfad] = text.rstrip("\n") + "\n"


def funktion(name, zeilen):
    datei(f"data/{NS}/function/{name}.mcfunction", zeilen)


# ---------------------------------------------------------------- Modell (relativ)
def modell(FALL):
    """Alle Blöcke und die frei zu räumende Luft; FALL = Höhe von der Wasserebene bis zum Trichter."""
    b = {}
    def setze(x, y, z, blk): b[(x, y, z)] = blk
    def box(x1, y1, z1, x2, y2, z2, blk):
        for x in range(x1, x2 + 1):
            for y in range(y1, y2 + 1):
                for z in range(z1, z2 + 1):
                    b[(x, y, z)] = blk
    W = "cobblestone"
    LOCH = {(0, 0), (1, 0), (0, 1), (1, 1)}
    def kanal(x, z):
        return (z in (0, 1) and -8 <= x <= 9) or (x in (0, 1) and -8 <= z <= 9)
    # Spawn-Ebene: Innenraum x/z -8..9, Wände bei -9 und 10
    for x in range(-9, 11):
        for z in range(-9, 11):
            rand = x in (-9, 10) or z in (-9, 10)
            if rand:
                box(x, -1, z, x, 2, z, W)
                setze(x, 3, z, "cobblestone_slab[type=bottom]")
                continue
            setze(x, 3, z, "cobblestone_slab[type=bottom]")            # Decke: auf Stufen spawnt nichts
            if (x, z) in LOCH:
                continue
            if kanal(x, z):
                setze(x, -1, z, W)                                    # Kanalboden
                ende = x in (-8, 9) or z in (-8, 9)
                if ende:
                    setze(x, 0, z, "water")                           # Quelle am Kanalende
            else:
                setze(x, 0, z, W)                                     # Plattform
    # Falltüren (offen) über den Kanälen, die Klappe zur Kanalmitte: Mobs halten das Feld für Boden und fallen ins Wasser.
    # Hängt die Klappe an der Plattformkante, ist sie eine Wand (Version 2 hatte das, per Konsole umgedreht).
    for x in range(-8, 10):
        for z in range(-8, 10):
            if not kanal(x, z) or (x, z) in LOCH:
                continue
            if z in (0, 1) and not (x in (0, 1)):
                setze(x, 1, z, f"oak_trapdoor[facing={'north' if z == 0 else 'south'},half=bottom,open=true]")
            elif x in (0, 1) and not (z in (0, 1)):
                setze(x, 1, z, f"oak_trapdoor[facing={'west' if x == 0 else 'east'},half=bottom,open=true]")
    # Fallschacht 2 × 2, Wände ringsum
    for y in range(-FALL + 1, -1):
        for x in range(-1, 3):
            for z in range(-1, 3):
                if (x, z) not in LOCH:
                    setze(x, y, z, W)
    for x in range(-1, 3):
        for z in range(-1, 3):
            if (x, z) not in LOCH:
                setze(x, -1, z, W)
    # Tötungszelle: Mobs stehen auf y=-22 (auf Trichtern bei -23)
    K = -FALL
    for x in range(-1, 3):
        for z in range(-1, 3):
            if (x, z) not in LOCH:
                setze(x, K, z, W)
                setze(x, K + 1, z, W)
    for x in range(-1, 3):                                       # Ring auf Trichterhöhe
        for z in range(-1, 3):
            if (x, z) not in LOCH:
                setze(x, K - 1, z, W)
    setze(0, K - 1, 0, "hopper[facing=east]")
    setze(1, K - 1, 0, "hopper[facing=south]")
    setze(0, K - 1, 1, "hopper[facing=east]")
    setze(1, K - 1, 1, "hopper[facing=east]")
    setze(2, K - 1, 1, "hopper[facing=south]")
    setze(2, K - 1, 2, "hopper[facing=south]")
    # Sichtschlitz: geschlossene Falltür vor den Mobs, darüber Stein. Der Spalt ist 13/16 hoch: Groß genug für
    # Schläge und XP-Kugeln (eine untere Stufe ließ nur einen halben Block), zu klein für Babyzombies (0,98).
    for x in (0, 1):
        setze(x, K, 2, "oak_trapdoor[facing=south,half=bottom,open=false]")
        setze(x, K + 1, 2, W)
        setze(x, K - 1, 2, W)
    # Spielerraum südlich: x -1..3, z 3..4, y K-1..K (2 hoch), Boden K-2
    box(-2, K - 2, -1, 4, K - 2, 5, W)                          # Fundament
    for x in range(-2, 5):
        for z in range(-1, 6):
            innen = -1 <= x <= 3 and 3 <= z <= 4
            if innen:
                continue
            if (x, z) in LOCH or (-1 <= x <= 2 and -1 <= z <= 2):
                continue
            box(x, K - 1, z, x, K + 1, z, W)
    for x in (-1, 0, 1, 3):
        for z in (3, 4):
            setze(x, K - 1, z, "air"); setze(x, K, z, "air")
    setze(2, K - 1, 3, "chest[facing=north,type=left]")
    setze(3, K - 1, 3, "chest[facing=north,type=right]")
    setze(2, K, 3, "air"); setze(2, K, 4, "air"); setze(2, K - 1, 4, "air")
    box(-1, K + 1, 3, 3, K + 1, 4, W)                           # Decke Spielerraum
    setze(-1, K - 1, 5, "air"); setze(-1, K, 5, "air")           # Eingang (Süden)
    setze(3, K, 4, "wall_torch[facing=north]")
    # AFK-Mulde einen Block tiefer: Dort sind die Füße 24 unter der Spawn-Ebene, also spawnt überall etwas
    # (im Spielerraum fehlt sonst ein Kreis von etwa 7 Blöcken direkt darüber)
    for z in (3, 4):
        setze(-1, K - 2, z, "air"); setze(-1, K - 3, z, W)
    for x in range(-2, 5):
        for z in range(-1, 6):
            if (x, K - 1, z) in b and b[(x, K - 1, z)] == "air" and (x, K - 2, z) not in b:
                setze(x, K - 2, z, W)

    # Luft, die vor dem Bau frei sein muss (Gelände, Gras, Pflanzen)
    luft = set()
    for x in range(-8, 10):
        for z in range(-8, 10):
            for y in (1, 2):
                luft.add((x, y, z))
            if kanal(x, z) and (x, z) not in LOCH:
                luft.add((x, 0, z))
    for x, z in LOCH:
        for y in range(K, 1):
            luft.add((x, y, z))
    for x in range(-1, 4):
        for z in (3, 4):
            luft.add((x, K - 1, z)); luft.add((x, K, z))
    luft |= {(-1, K - 1, 5), (-1, K, 5), (-1, K - 2, 3), (-1, K - 2, 4)}
    luft = {p for p in luft if b.get(p, "air") == "air"}
    return b, luft, K


LOCH = {(0, 0), (1, 0), (0, 1), (1, 1)}
# Fallhöhe 21: Die Mobs landen in der Trichtermulde (11/16 Block tief), also fallen sie 21,3 Blöcke
# → 19 Schaden, 1 Herz bleibt. Version 1 hatte 22 (= 20 Schaden, die Mobs starben ohne XP).
b, luft, K = modell(21)
b_alt, luft_alt, K_alt = modell(22)


def welt(x, y, z):
    return X0 + x, P + y, Z0 + z


def rang(blk):
    n = blk.split("[")[0]
    if n == "water":
        return 3
    if n in ("oak_trapdoor", "hopper", "chest", "wall_torch"):
        return 2
    return 1


befehle = []
for (x, y, z) in sorted(luft, key=lambda p: (p[1], p[0], p[2])):
    befehle.append("setblock %d %d %d minecraft:air" % welt(x, y, z))
for (x, y, z), blk in sorted(b.items(), key=lambda e: (rang(e[1]), e[0][1], e[0][0], e[0][2])):
    if blk == "air":
        continue
    wx, wy, wz = welt(x, y, z)
    befehle.append(f"setblock {wx} {wy} {wz} minecraft:{blk}")

# Lichter auf den Boden unter der Plattform – vor dem Bau, solange die Höhenkarte noch den Boden zeigt
lichter = []
for dx in (-8, -3, 2, 7, 10):
    for dz in (-8, -3, 2, 7, 10):
        if -2 <= dx <= 4 and -1 <= dz <= 5:
            continue
        lichter.append(f"execute positioned {X0 + dx} 0 {Z0 + dz} positioned over motion_blocking_no_leaves "
                       f"if block ~ ~ ~ minecraft:air run setblock ~ ~ ~ minecraft:light[level=15]")

# Umbau von Version 1 (Fall 22): Tötungszelle und Spielerraum einen Block höher
umbau_b = {p: blk for p, blk in b.items() if b_alt.get(p) != blk}
for p in b_alt:
    if p not in b and p[1] >= K - 2:
        umbau_b[p] = "air"
for p in luft:
    umbau_b.setdefault(p, "air")
umbau = []
for (x, y, z), blk in sorted(umbau_b.items(), key=lambda e: (e[1] != "air", rang(e[1]), e[0][1], e[0][0], e[0][2])):
    wx, wy, wz = welt(x, y, z)
    umbau.append(f"setblock {wx} {wy} {wz} minecraft:{blk}")

alle = list(b) + list(luft) + list(b_alt)
xs = [welt(*p)[0] for p in alle] + [X0 - 8, X0 + 10]
zs = [welt(*p)[2] for p in alle] + [Z0 - 8, Z0 + 10]
FL = f"{min(xs)} {min(zs)} {max(xs)} {max(zs)}"
LADEN = " ".join(f"if loaded {x} 0 {z}" for x in (min(xs), max(xs)) for z in (min(zs), max(zs)))

sx, sy, sz = welt(-8, 0, -8)
SPAWN = f"x={sx},y={sy},z={sz},dx=17,dy=2,dz=17"
ZELLE = " ".join(f"{v}.0" for v in welt(1, K, 1))
funktion("load", [
    "scoreboard objectives add xp.zustand dummy",
    "scoreboard objectives add xp.test dummy",
    "# #gebaut: 1 = Fall 22 (Mobs starben beim Aufprall), 2 = Fall 21 (aktuell)",
    f"execute unless score #gebaut xp.zustand matches 1.. unless score #stufe xp.zustand matches 1.. run function {NS}:start",
    f"execute if score #gebaut xp.zustand matches 1 unless score #stufe xp.zustand matches 1.. run function {NS}:start_umbau",
])
funktion("tick", [f"execute if score #stufe xp.zustand matches 1 {LADEN} run function {NS}:licht",
                  f"execute if score #stufe xp.zustand matches 2 {LADEN} run function {NS}:bauen",
                  f"execute if score #stufe xp.zustand matches 3 {LADEN} run function {NS}:umbau",
                  "# Spinnen passen nicht in die Kanäle und blieben für immer oben (sie belegen Mob-Plätze). Im Schacht klettern",
                  "# sie an den Wänden hoch, deshalb kommen sie direkt in die Tötungszelle, mit 1 Herz wie die anderen.",
                  f"execute if score #gebaut xp.zustand matches 2.. as @e[type=minecraft:spider,{SPAWN}] run function {NS}:spinne"])
funktion("spinne", ["data modify entity @s Health set value 2.0f", f"tp @s {ZELLE}"])
funktion("start_umbau", [f"forceload add {FL}", "scoreboard players set #stufe xp.zustand 3"])
funktion("start", [f"forceload add {FL}", "scoreboard players set #stufe xp.zustand 1"])
funktion("licht", lichter + ["scoreboard players set #stufe xp.zustand 2"])
fertig = ["scoreboard players set #stufe xp.zustand 0", "scoreboard players set #gebaut xp.zustand 2",
          f"schedule function {NS}:test/t1 100t"]
funktion("bauen", befehle + fertig)
funktion("umbau", ["# Version 1 → 2: Fall 22 → 21"] + umbau + fertig)

# Selbsttest
kx, ky, kz = welt(0, K, 0)
def wpos(x, y, z):
    return " ".join(map(str, welt(x, y, z)))
funktion("test/t1", [
    "# Zombie direkt in einen Kanal (Wasser), zwei weitere auf Plattformen",
    f"summon minecraft:zombie {X0 - 6}.5 {P} {Z0}.5 {{Tags:[\"xp.test\",\"xp.kanal\"],PersistenceRequired:1b,IsBaby:0b}}",
    f"summon minecraft:zombie {X0 - 5}.5 {P + 1} {Z0 - 5}.5 {{Tags:[\"xp.test\"],PersistenceRequired:1b,IsBaby:0b}}",
    f"summon minecraft:zombie {X0 + 6}.5 {P + 1} {Z0 + 6}.5 {{Tags:[\"xp.test\"],PersistenceRequired:1b,IsBaby:0b}}",
    f"execute store success score #wasser xp.test if block {wpos(-8, 0, 0)} minecraft:water if block {wpos(9, 0, 1)} minecraft:water "
    f"if block {wpos(0, 0, -8)} minecraft:water if block {wpos(1, 0, 9)} minecraft:water",
    f"schedule function {NS}:test/t2 600t",
])
zelle = f"x={kx},y={ky},z={kz},dx=1,dy=1,dz=1"
funktion("test/t2", [
    f"execute store success score #kanal_unten xp.test if entity @e[type=minecraft:zombie,tag=xp.kanal,{zelle}]",
    f"execute store result score #kanal_hp xp.test run data get entity @e[type=minecraft:zombie,tag=xp.kanal,limit=1] Health",
    f"schedule function {NS}:test/t3 3000t",
])
funktion("test/t3", [
    f"execute store result score #test_unten xp.test if entity @e[type=minecraft:zombie,tag=xp.test,{zelle}]",
    f"execute store result score #test_gesamt xp.test if entity @e[type=minecraft:zombie,tag=xp.test]",
    f"execute store result score #mobs_unten xp.test if entity @e[type=!minecraft:player,type=!minecraft:item,{zelle}]",
    "tp @e[type=minecraft:zombie,tag=xp.test] ~ -200 ~",
    f"forceload remove {FL}",
    "scoreboard players set #fertig xp.test 1",
])

datei("data/minecraft/tags/function/load.json", json.dumps({"values": [f"{NS}:load"]}, indent=2))
datei("data/minecraft/tags/function/tick.json", json.dumps({"values": [f"{NS}:tick"]}, indent=2))
datei("pack.mcmeta", json.dumps({"pack": {
    "description": "XP-Farm", "pack_format": FORMAT_MIN, "supported_formats": [FORMAT_MIN, FORMAT_MAX],
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
c = collections.Counter(v.split("[")[0] for v in b.values() if v != "air")
print(f"{len(befehle)} Befehle, {len(lichter)} Lichter, Forceload {FL}", dict(c))
