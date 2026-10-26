"""Baut das Datapack „Kaktusfarm“: einen Glasturm mit 12 Etagen Kakteen. Das Pack baut nur; danach wird es
gelöscht, die Farm selbst läuft rein vanilla.

Aufruf:  python3 kaktusfarm.py <ort.json> [zip-datei] [entpackt-ordner]

ort.json:  {"ecke": [x, y, z]}   Nordwest-Ecke des Innenraums, y: Höhe direkt über dem Boden

Jede Etage ist 3 Blöcke hoch: unten Sand und Trichter, darauf die Kakteen, darüber wächst der Kaktus. Neben dieser
Wuchshöhe steht ein Glasblock; ein Kaktus neben einem festen Block zerbricht sofort (Zäune taugen nicht:
am dünnen Pfosten rutschen die Kakteen vorbei in Ecken, aus denen sie nicht mehr herauskommen). Die freien Seiten führen
nach unten in den Trichterboden derselben Etage, so fällt ein Kaktus höchstens 2 Blöcke (wer auf seinen eigenen
Kaktus fällt, verbrennt – das ist bei jeder Kaktusfarm so). Die Etagen wechseln ab, der Sand liegt auf dem Glas
der Etage darunter:
  A (gerade)    Kakteen auf x 0/2/4/6 × z 0/2/4/6 (16), Glas auf x 1/3/5, frei nach z ± 1
  B (ungerade)  Kakteen auf x 1/3/5 × z 0/2/4/6 (12), Glas auf x 0/2/4/6, frei nach z ± 1
Was ein Gegenstand nie erreicht, ist Glas. Die Trichterreihen in z -1/1/3/5/7 laufen nach Westen in fünf
senkrechte Trichterketten bei x -1, unten sammelt eine Reihe bei y 3 alles und gibt es durch die Wand an die
Schmelzanlage (x -4): oben ein Trichter, die Doppeltruhe auf Kopfhöhe, zwei Trichter, zwei Öfen. Der grüne
Farbstoff bleibt im Ofen; wer ihn herausnimmt, bekommt die XP (1 pro Kaktus).
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
SOCKEL = 4                                                      # Etage 0 beginnt bei y 4, darunter die Sammelreihe (y 3)
OBEN = SOCKEL + 3 * ETAGEN                                      # Oberkante der Wände
INNEN = range(-1, 8)
GERADE, UNGERADE = (0, 2, 4, 6), (1, 3, 5)
REIHEN = (-1, 1, 3, 5, 7)                                       # Trichterreihen
KISTE = [((-4, 2, 2), "right"), ((-4, 2, 3), "left")]          # Blick nach Westen: links = Süden
OEFEN = [(-4, 0, 2), (-4, 0, 3)]
EINGANG = (-4, 3, 3)                                            # Trichter über der Truhe
ALT_HOCH = 37                                                   # so hoch stand Version 1

# ---------------------------------------------------------------- Modell
b = {}
for x in range(-2, 9):
    for z in range(-2, 9):
        b[(x, -1, z)] = "glass"                                 # Boden
        if x in (-2, 8) or z in (-2, 8):
            for y in range(0, OBEN + 1):
                b[(x, y, z)] = "glass"                          # Wände
        else:
            for y in range(0, SOCKEL):
                b[(x, y, z)] = "glass"                          # Sockel
for z in INNEN:                                                 # Sammelreihe: zur Mitte, dann nach Westen
    b[(-1, 3, z)] = "hopper[facing=%s]" % ("south" if z < 3 else "north" if z > 3 else "west")
b[(-2, 3, 3)] = "hopper[facing=west]"
b[(-3, 3, 3)] = "hopper[facing=west]"
kakteen = 0
for k in range(ETAGEN):
    y = SOCKEL + 3 * k
    a = k % 2 == 0
    kx, zx = (GERADE, UNGERADE) if a else (UNGERADE, GERADE)
    for x in INNEN:
        for z in INNEN:
            for dy in range(3):
                b[(x, y + dy, z)] = "glass"
    for z in GERADE:
        for x in kx:
            b[(x, y, z)] = "sand"
            b[(x, y + 1, z)] = "cactus"
            b[(x, y + 2, z)] = "air"                            # hier wächst er
            for nx, nz in ((x - 1, z), (x + 1, z), (x, z - 1), (x, z + 1)):
                b[(nx, y + 1, nz)] = "air"                      # nichts Festes neben dem Kaktus
            kakteen += 1
        for x in zx:
            b[(x, y + 2, z)] = "glass"                          # voller Block: an einem Zaun rutschen Kakteen vorbei
    for z in REIHEN:
        for x in range(0, 7 if a else 6):
            b[(x, y, z)] = "hopper[facing=west]"
        for x in kx:
            b[(x, y + 1, z)] = "air"                            # freie Seite neben dem Wuchsplatz
            b[(x, y + 2, z)] = "air"
        for dy in range(3):
            b[(-1, y + dy, z)] = "hopper[facing=down]"          # Kette nach unten
for (x, y, z), typ in KISTE:
    b[(x, y, z)] = f"chest[facing=west,type={typ}]"
for x, y, z in OEFEN:
    b[(x, y, z)] = "furnace[facing=west]"
    b[(x, y + 1, z)] = "hopper[facing=down]"
b[EINGANG] = "hopper[facing=down]"


def rang(blk):
    return 1 if blk.startswith("cactus") else 0                 # Kakteen erst, wenn ihre Nachbarn frei sind


# Erst den alten Turm von oben nach unten leeren (sonst fällt Sand), dann von unten nach oben bauen
abriss = [f"fill {pos(-1, y, -1)} {pos(7, y, 7)} minecraft:air" for y in range(max(OBEN, ALT_HOCH), -1, -1)]
befehle = []
for (x, y, z), blk in sorted(b.items(), key=lambda e: (e[0][1], rang(e[1]), e[0][0], e[0][2])):
    if blk == "air" and y > -1 and x in INNEN and z in INNEN:
        continue                                                # schon durch den Abriss leer
    if x == -4:                                                 # Schmelzanlage: stehen lassen, sonst wäre der Inhalt weg
        befehle.append(f"execute unless block {pos(x, y, z)} minecraft:{blk.split('[')[0]} "
                       f"run setblock {pos(x, y, z)} minecraft:{blk}")
    else:
        befehle.append(f"setblock {pos(x, y, z)} minecraft:{blk}")

xs = [X0 - 4, X0 + 8]
zs = [Z0 - 2, Z0 + 8]
FL = f"{xs[0]} {zs[0]} {xs[1]} {zs[1]}"
LADEN = " ".join(f"if loaded {x} {Y0} {z}" for x in xs for z in zs)

funktion("load", [
    "scoreboard objectives add kaktus.zustand dummy",
    "# #gebaut: 1 = Turm mit Teleport (Version 1), 2 = Trichterböden, rein vanilla (aktuell)",
    f"execute unless score #gebaut kaktus.zustand matches 2.. unless score #stufe kaktus.zustand matches 1.. run function {NS}:start",
])
funktion("start", [f"forceload add {FL}", "scoreboard players set #stufe kaktus.zustand 1"])
funktion("tick", [f"execute if score #stufe kaktus.zustand matches 1 {LADEN} run function {NS}:bauen"])
funktion("bauen", abriss + befehle + ["scoreboard players set #stufe kaktus.zustand 0",
                                      "scoreboard players set #gebaut kaktus.zustand 2", f"forceload remove {FL}"])

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
trichter = sum(1 for v in b.values() if v.startswith("hopper"))
print(f"{len(befehle)} Befehle, {kakteen} Kakteen, {trichter} Trichter, Forceload {FL}")
