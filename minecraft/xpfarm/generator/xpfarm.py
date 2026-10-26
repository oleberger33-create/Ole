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
def modell(FALL, oben=True, tief=True, etagen=4):
    """Alle Blöcke und die frei zu räumende Luft; FALL = Höhe von der Wasserebene bis zum Trichter,
    oben = mit zweiter Spawn-Ebene (ab Version 3), tief = Wasser 2 unter den Plattformen (ab Version 4).
    Bei 1 Block Abstand sprangen die Mobs aus dem Wasser zurück auf die Plattformen.
    etagen > 2 (ab Version 5): darüber reine Spawn-Etagen ohne Wasser, das Datapack holt die Mobs dort ab."""
    T = 1 if tief else 0                                          # so viel tiefer liegt das Wasser
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
    def kanalende(x, z):
        return x in (-8, 9) or z in (-8, 9)
    def falltueren(y):
        # Falltüren (offen) über den Kanälen, die Klappe zur Kanalmitte: Mobs halten das Feld für Boden und fallen ins
        # Wasser. Hängt die Klappe an der Plattformkante, ist sie eine Wand (Version 2 hatte das, per Konsole umgedreht).
        for x in range(-8, 10):
            for z in range(-8, 10):
                if not kanal(x, z) or (x, z) in LOCH:
                    continue
                if z in (0, 1) and not (x in (0, 1)):
                    setze(x, y, z, f"oak_trapdoor[facing={'north' if z == 0 else 'south'},half=bottom,open=true]")
                elif x in (0, 1) and not (z in (0, 1)):
                    setze(x, y, z, f"oak_trapdoor[facing={'west' if x == 0 else 'east'},half=bottom,open=true]")
    # Spawn-Ebene: Innenraum x/z -8..9, Wände bei -9 und 10
    for x in range(-9, 11):
        for z in range(-9, 11):
            rand = x in (-9, 10) or z in (-9, 10)
            if rand:
                box(x, -1 - T, z, x, 2, z, W)
                setze(x, 3, z, "cobblestone_slab[type=bottom]")
                continue
            setze(x, 3, z, "cobblestone_slab[type=bottom]")            # Decke: auf Stufen spawnt nichts
            if (x, z) in LOCH:
                continue
            if kanal(x, z):
                setze(x, -1 - T, z, W)                                # Kanalboden
                ende = kanalende(x, z)
                if ende:
                    setze(x, -T, z, "water")                          # Quelle am Kanalende
            else:
                box(x, -T, z, x, 0, z, W)                             # Plattform
    falltueren(1)
    # Zweite Spawn-Ebene ab 3, gleich aufgebaut, aber das Wasser (auf 4) fließt von 2 × 2 Quellen in der Mitte nach
    # außen. An den vier Kanalenden ist der Boden offen: Die Mobs fallen in die Quellen der unteren Kanäle
    # (Landung im Wasser, kein Schaden) und schwimmen mit den unteren Mobs zum Fallschacht.
    abwurf = set()
    if oben:
        for x in range(-9, 11):
            for z in range(-9, 11):
                setze(x, 7 + T, z, "cobblestone_slab[type=bottom]")
                if x in (-9, 10) or z in (-9, 10):
                    box(x, 3, z, x, 6 + T, z, W)
                    continue
                if kanal(x, z) and kanalende(x, z):
                    abwurf.add((x, 3, z))                             # offen: hier fallen sie runter
                    b.pop((x, 3, z), None)
                    continue
                setze(x, 3, z, W)                                     # Boden oben = Decke unten
                if (x, z) in LOCH:
                    setze(x, 4, z, "water")                           # Quellen in der Mitte
                elif not kanal(x, z):
                    box(x, 4, z, x, 4 + T, z, W)                      # Plattform
        falltueren(5 + T)
    # Etagen 3 und 4: Boden, 2 Luft, darüber die nächste Etage, ganz oben Stufen. Sie liegen mehr als 32 Blöcke über
    # dem Spielerraum, dort laufen Mobs nicht herum (sie fänden die Falltüren nie), deshalb ohne Wasser.
    dach = 7 + T
    if oben and etagen > 2:
        for i in range(etagen - 2):
            y = 8 + 3 * i
            for x in range(-9, 11):
                for z in range(-9, 11):
                    setze(x, y, z, W)
                    if x in (-9, 10) or z in (-9, 10):
                        box(x, y + 1, z, x, y + 2, z, W)
        dach = 8 + 3 * (etagen - 2)
        for x in range(-9, 11):
            for z in range(-9, 11):
                setze(x, dach, z, "cobblestone_slab[type=bottom]")
    # Fallschacht 2 × 2, Wände ringsum (bis unter die Wasserebene)
    K = -T - FALL                                                # Tötungszelle: Mobs stehen in den Trichtern bei K - 1
    for y in range(K + 1, -T):
        for x in range(-1, 3):
            for z in range(-1, 3):
                if (x, z) not in LOCH:
                    setze(x, y, z, W)
    if not tief:
        for x in range(-1, 3):
            for z in range(-1, 3):
                if (x, z) not in LOCH:
                    setze(x, -1, z, W)
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
    # Sichtschlitz: geschlossene Falltür (obere Hälfte) vor den Mobs. Der Spalt darunter ist 13/16 hoch: groß genug
    # für Schläge und XP-Kugeln, zu klein für Babyzombies (0,98). Er liegt unter den Augen der Creeper; mit der
    # Falltür unten (Spalt bis K + 1) sahen sie einen geduckten Spieler und sprengten.
    for x in (0, 1):
        setze(x, K, 2, "oak_trapdoor[facing=south,half=top,open=false]")
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
    # Version 3: AFK-Mulde einen Block tiefer, damit die Füße 24 unter der Spawn-Ebene sind (sonst fehlt ein Kreis
    # von etwa 7 Blöcken direkt darüber). Ab Version 4 liegt der ganze Spielerraum so tief.
    if not tief:
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
                luft |= {(x, y, z) for y in range(-T, 1)}
    for x, z in LOCH:
        for y in range(K, 1):
            luft.add((x, y, z))
    for x in range(-1, 4):
        for z in (3, 4):
            luft.add((x, K - 1, z)); luft.add((x, K, z))
    luft |= {(-1, K - 1, 5), (-1, K, 5)}
    if not tief:
        luft |= {(-1, K - 2, 3), (-1, K - 2, 4)}
    if oben:
        for x in range(-8, 10):
            for z in range(-8, 10):
                luft |= {(x, 5 + T, z), (x, 6 + T, z)}
                if kanal(x, z):
                    luft |= {(x, y, z) for y in range(4, 5 + T)}           # Quellen in der Mitte bleiben (b)
        luft |= abwurf
        for y in range(8, dach):
            if y % 3 != 2:
                luft |= {(x, y, z) for x in range(-8, 10) for z in range(-8, 10)}
    luft = {p for p in luft if b.get(p, "air") == "air"}
    return b, luft, K, dach


LOCH = {(0, 0), (1, 0), (0, 1), (1, 1)}
# Fallhöhe 21: Die Mobs landen in der Trichtermulde (11/16 Block tief), also fallen sie 21,3 Blöcke
# → 19 Schaden, 1 Herz bleibt. Version 1 hatte 22 (= 20 Schaden, die Mobs starben ohne XP).
# #gebaut zählt die Version in der Welt: 2 = Fall 21, 3 = zweite Spawn-Ebene, 4 = Wasser 2 Blöcke tief.
b, luft, K, DACH = modell(21)
b_v4, _, _, _ = modell(21, etagen=2)


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

def umbau_von(b_alt):
    """Nur die Unterschiede zur alten Version; was es nicht mehr gibt, wird Luft (nicht unter dem Fundament)."""
    neu = {p: blk for p, blk in b.items() if b_alt.get(p) != blk}
    for p in b_alt:
        if p not in b and p[1] >= K - 2:
            neu[p] = "air"
    for p in luft:
        neu.setdefault(p, "air")
    zeilen = []
    for (x, y, z), blk in sorted(neu.items(), key=lambda e: (e[1] != "air", rang(e[1]), e[0][1], e[0][0], e[0][2])):
        wx, wy, wz = welt(x, y, z)
        zeilen.append(f"setblock {wx} {wy} {wz} minecraft:{blk}")
    return zeilen


alle = list(b) + list(luft) + list(b_v4)
xs = [welt(*p)[0] for p in alle] + [X0 - 8, X0 + 10]
zs = [welt(*p)[2] for p in alle] + [Z0 - 8, Z0 + 10]
FL = f"{min(xs)} {min(zs)} {max(xs)} {max(zs)}"
LADEN = " ".join(f"if loaded {x} 0 {z}" for x in (min(xs), max(xs)) for z in (min(zs), max(zs)))

# Mob-Limit: Pro Spieler zählen alle Monster im Umkreis von 128 Blöcken, also auch die in den Höhlen darunter.
# Ist das Limit (70) voll, spawnt in der Farm nichts. Solange jemand im Spielerraum steht, verschwinden deshalb
# alle 2 Sekunden Höhlenmonster, die mehr als 34 Blöcke von ihm weg sind (die obere
# Ebene reicht bis 32); bei anderen Spielern (48) bleiben sie.
MONSTER = ["zombie", "husk", "drowned", "zombie_villager", "skeleton", "stray", "bogged", "creeper", "spider",
           "cave_spider", "witch", "enderman", "slime"]
rx, ry, rz = welt(-1, K - 2, 3)
RAUM = f"x={rx},y={ry},z={rz},dx=4,dy=2,dz=1"
zx, zy, zz = welt(0, K - 1, 0)
ZELLBOX = f"x={zx},y={zy},z={zz},dx=1,dy=2,dz=2"                 # Tötungszelle samt Schlitz
fx, fy, fz = welt(-9, K - 2, -9)
FARM = f"x={fx},y={fy},z={fz},dx=19,dy={DACH - (K - 2)},dz=19"  # das ganze Bauwerk
ex, ey, ez = welt(-8, 9, -8)
ETAGEN = f"x={ex},y={ey},z={ez},dx=17,dy={DACH - 1 - 9},dz=17"  # Etagen 3 und 4
KANAL = f"{X0 - 6 + 0.5} {P - 1} {Z0 + 0.5}"                    # unterer Westkanal, fließt zum Loch
sx, sy, sz = welt(-8, -1, -8)
SPAWN = f"x={sx},y={sy},z={sz},dx=17,dy={DACH - 1 - (-1)},dz=17"  # alle Etagen samt unteren Kanälen
ZELLE = " ".join(f"{v}.0" for v in welt(1, K, 1))
funktion("load", [
    "scoreboard objectives add xp.zustand dummy",
    "scoreboard objectives add xp.test dummy",
    "# #gebaut: 1 = Fall 22 (Mobs starben beim Aufprall), 2 = Fall 21, 3 = zweite Spawn-Ebene, 4 = Wasser tiefer,",
    "# 5 = vier Etagen (aktuell)",
    f"execute unless score #gebaut xp.zustand matches 1.. unless score #stufe xp.zustand matches 1.. run function {NS}:start",
    f"execute if score #gebaut xp.zustand matches 4 unless score #stufe xp.zustand matches 1.. run function {NS}:start_umbau",
    f"schedule function {NS}:platz 40t",
])
funktion("tick", [f"execute if score #stufe xp.zustand matches 1 {LADEN} run function {NS}:licht",
                  f"execute if score #stufe xp.zustand matches 2 {LADEN} run function {NS}:bauen",
                  f"execute if score #stufe xp.zustand matches 3 {LADEN} run function {NS}:umbau",
                  "# Spinnen passen nicht in die Kanäle und blieben für immer oben (sie belegen Mob-Plätze). Im Schacht klettern",
                  "# sie an den Wänden hoch, deshalb kommen sie direkt in die Tötungszelle, mit 1 Herz wie die anderen.",
                  f"execute if score #gebaut xp.zustand matches 2.. as @e[type=minecraft:spider,{SPAWN}] run function {NS}:spinne",
                  "# Creeper in der Farm explodieren ohne Wirkung: Zwei Sprengungen hatten die Tötungszelle aufgerissen,",
                  "# danach liefen Mobs in den Spielerraum.",
                  f"execute if score #gebaut xp.zustand matches 2.. as @e[type=minecraft:creeper,{FARM},tag=!xp.zahm] run function {NS}:zahm",
                  "# XP-Kugeln blieben zur Hälfte in den Trichtermulden hängen (sie zielen auf Hüfthöhe des Spielers, die Mulde",
                  "# liegt tiefer als der Schlitz): Sie kommen direkt zum Spieler im Raum.",
                  f"execute if score #gebaut xp.zustand matches 2.. as @e[type=minecraft:experience_orb,{ZELLBOX}] at @p[{RAUM}] run tp @s ~ ~ ~",
                  "# Was trotzdem in den Spielerraum kommt, stirbt sofort"]
                 + [f"execute if score #gebaut xp.zustand matches 2.. run kill @e[type=minecraft:{m},{RAUM}]" for m in MONSTER])
funktion("zahm", ["data merge entity @s {ExplosionRadius:0b}", "tag @s add xp.zahm"])
funktion("spinne", ["data modify entity @s Health set value 2.0f", f"tp @s {ZELLE}"])

funktion("platz", [f"schedule function {NS}:platz 40t",
                   f"execute if score #gebaut xp.zustand matches 2.. if entity @a[{RAUM}] run function {NS}:platz_frei"])
funktion("platz_frei",
         [f"execute as @a[gamemode=!spectator] unless entity @s[{RAUM}] at @s run tag @e[type=minecraft:{m},distance=..48] add xp.bleibt"
          for m in MONSTER]
         + [f"execute at @a[{RAUM},limit=1] as @e[type=minecraft:{m},distance=34..128,tag=!xp.bleibt] "
            f"unless data entity @s {{PersistenceRequired:1b}} unless entity @s[{FARM}] at @s run tp @s ~ -300 ~" for m in MONSTER]
         + ["tag @e[tag=xp.bleibt] remove xp.bleibt",
            "# Etagen 3 und 4: Mobs ab in den unteren Kanal (Spinnen holt der Tick schon in die Zelle)"]
         + [f"tp @e[type=minecraft:{m},{ETAGEN}] {KANAL}" for m in MONSTER if m != "spider"])
funktion("start_umbau", [f"forceload add {FL}", "scoreboard players set #stufe xp.zustand 3"])
funktion("start", [f"forceload add {FL}", "scoreboard players set #stufe xp.zustand 1"])
funktion("licht", lichter + ["scoreboard players set #stufe xp.zustand 2"])
fertig = ["scoreboard players set #stufe xp.zustand 0", "scoreboard players set #gebaut xp.zustand 5",
          f"schedule function {NS}:test/t1 100t"]
funktion("bauen", befehle + fertig)
funktion("umbau", ["# Version 4 → 5: Etagen 3 und 4"] + umbau_von(b_v4) + fertig)

# Selbsttest
kx, ky, kz = welt(0, K, 0)
def wpos(x, y, z):
    return " ".join(map(str, welt(x, y, z)))
funktion("test/t1", [
    "# Zombie direkt in einen Kanal (Wasser), zwei weitere auf Plattformen",
    f"summon minecraft:zombie {X0 - 6 + 0.5} {P} {Z0 + 0.5} {{Tags:[\"xp.test\",\"xp.kanal\"],PersistenceRequired:1b,IsBaby:0b}}",
    f"summon minecraft:zombie {X0 - 5}.5 {P + 1} {Z0 - 5}.5 {{Tags:[\"xp.test\"],PersistenceRequired:1b,IsBaby:0b}}",
    f"summon minecraft:zombie {X0 + 6}.5 {P + 1} {Z0 + 6}.5 {{Tags:[\"xp.test\"],PersistenceRequired:1b,IsBaby:0b}}",
    f"execute store success score #wasser xp.test if block {wpos(-8, -1, 0)} minecraft:water if block {wpos(9, -1, 1)} minecraft:water "
    f"if block {wpos(0, -1, -8)} minecraft:water if block {wpos(1, -1, 9)} minecraft:water",
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
