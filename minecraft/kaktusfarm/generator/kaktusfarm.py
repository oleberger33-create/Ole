"""Baut das Datapack „Kaktusfarm“: einen Glasturm mit 12 Etagen Kakteen, einmalig per Datapack errichtet.

Aufruf:  python3 kaktusfarm.py <ort.json> [zip-datei] [entpackt-ordner]

ort.json:  {"ecke": [x, y, z]}   Nordwest-Ecke des Innenraums (7 × 7), y: Höhe direkt über dem Boden

Aufbau (relativ zur Ecke): Jede Etage ist 3 Blöcke hoch: Sand, darauf ein Kaktus, darüber wächst er. Neben
dieser Wuchshöhe steht ein Zaunpfosten; ein Kaktus neben einem festen Block zerbricht sofort und fällt als
Gegenstand herunter. Die Etagen wechseln ab:
  A (gerade)    Kakteen auf x 0/2/4/6 × z 0/2/4/6 (16), Zäune auf x 1/3/5 × z 0/2/4/6
  B (ungerade)  Kakteen auf x 1/3/5 × z 0/2/4/6 (12), der Sand liegt auf den Zäunen von A,
                Zäune auf x 0/2/4/6 × z 0/2/4/6 – darauf liegt der Sand der nächsten A-Etage
Ringsum ein Block Luft (ein Kaktus zerbricht auch an Glas), dann Glaswände. Der Boden ist aus Glas, darauf
spawnen keine Monster. Herunterfallende Kakteen landen sonst oft auf den Kakteen darunter und verbrennen; das
Pack bringt sie deshalb sofort zum Trichter vor der Doppeltruhe an der Westseite.
"""
import json
import os
import shutil
import sys
import zipfile

NS = "kaktus"
FORMAT_MIN, FORMAT_MAX = 71, 121
ORT = json.load(open(sys.argv[1]))
HIER = os.path.dirname(os.path.abspath(__file__))
ZIP = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HIER, "..", "Kaktusfarm.zip")
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


ETAGEN = 12
HOCH = 3 * ETAGEN                                               # oberster Zaun bei HOCH - 1
GERADE, UNGERADE = (0, 2, 4, 6), (1, 3, 5)
KISTE = [((-4, 0, 2), "left"), ((-4, 0, 3), "right")]          # Blick nach Osten: links = Norden
TRICHTER = (-3, 0, 3)

# ---------------------------------------------------------------- Modell
b = {}
for x in range(-2, 9):
    for z in range(-2, 9):
        b[(x, -1, z)] = "glass"                                 # Boden
        if x in (-2, 8) or z in (-2, 8):
            for y in range(0, HOCH + 1):
                b[(x, y, z)] = "glass"                          # Wände
kakteen = 0
for k in range(ETAGEN):
    y = 3 * k
    kx, zx = (GERADE, UNGERADE) if k % 2 == 0 else (UNGERADE, GERADE)
    for x in kx:
        for z in GERADE:
            b[(x, y, z)] = "sand"
            b[(x, y + 1, z)] = "cactus"
            kakteen += 1
    for x in zx:
        for z in GERADE:
            b[(x, y + 2, z)] = "oak_fence"
for (x, y, z), typ in KISTE:
    b[(x, y, z)] = f"chest[facing=east,type={typ}]"
b[TRICHTER] = "hopper[facing=west]"
luft = {(x, y, z) for x in range(-1, 8) for z in range(-1, 8) for y in range(0, HOCH + 1)} - set(b)


def rang(blk):
    n = blk.split("[")[0]
    return {"glass": 0, "sand": 1, "oak_fence": 2, "cactus": 3}.get(n, 2)


befehle = ["setblock %d %d %d minecraft:air" % welt(*p) for p in sorted(luft, key=lambda p: (p[1], p[0], p[2]))]
# von unten nach oben, Sand vor dem Kaktus darauf
for (x, y, z), blk in sorted(b.items(), key=lambda e: (e[0][1], rang(e[1]), e[0][0], e[0][2])):
    befehle.append(f"setblock {pos(x, y, z)} minecraft:{blk}")

ex, ey, ez = welt(*TRICHTER)
EINWURF = f"{ex + 0.5} {ey + 1} {ez + 0.5}"
tx, ty, tz = welt(-2, 0, -2)
TURM = f"x={tx},y={ty},z={tz},dx=10,dy={HOCH},dz=10"
xs = [X0 - 4, X0 + 8]
zs = [Z0 - 2, Z0 + 8]
FL = f"{xs[0]} {zs[0]} {xs[1]} {zs[1]}"
LADEN = " ".join(f"if loaded {x} {Y0} {z}" for x in xs for z in zs)

funktion("load", [
    "scoreboard objectives add kaktus.zustand dummy",
    "# #gebaut: 1 = Turm steht",
    f"execute unless score #gebaut kaktus.zustand matches 1.. unless score #stufe kaktus.zustand matches 1.. run function {NS}:start",
])
funktion("start", [f"forceload add {FL}", "scoreboard players set #stufe kaktus.zustand 1"])
funktion("tick", [
    f"execute if score #stufe kaktus.zustand matches 1 {LADEN} run function {NS}:bauen",
    "# Zerbrochene Kakteen sofort zum Trichter, bevor sie auf einen Kaktus darunter fallen",
    f"execute if score #gebaut kaktus.zustand matches 1.. run tp @e[type=minecraft:item,{TURM},nbt={{Item:{{id:\"minecraft:cactus\"}}}}] {EINWURF}",
])
funktion("bauen", befehle + ["scoreboard players set #stufe kaktus.zustand 0", "scoreboard players set #gebaut kaktus.zustand 1",
                             f"forceload remove {FL}"])

datei("data/minecraft/tags/function/load.json", json.dumps({"values": [f"{NS}:load"]}, indent=2))
datei("data/minecraft/tags/function/tick.json", json.dumps({"values": [f"{NS}:tick"]}, indent=2))
datei("pack.mcmeta", json.dumps({"pack": {
    "description": "Kaktusfarm", "pack_format": FORMAT_MIN, "supported_formats": [FORMAT_MIN, FORMAT_MAX],
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
print(f"{len(befehle)} Befehle, {kakteen} Kakteen, Forceload {FL}")
