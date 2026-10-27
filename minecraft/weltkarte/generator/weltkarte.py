"""Baut die Weltkarte: eine fertig gezeichnete, gesperrte Karte der ganzen erkundeten Welt, und das Datapack, das sie
jedem Spieler einmal gibt (auch wer neu auf den Server kommt).

Aufruf:  python3 weltkarte.py <ort.json> <pixel-ordner> <farben.json> <ausgabe-ordner>

ort.json:  {"mitte": [x, z], "bloecke_pro_pixel": B, "karten_id": N,
            "marken": [{"name": "Basis", "pos": [x, z], "farbe": "red"}, …]}
pixel-ordner: Ausgaben von pixel.py (eine JSON-Datei je Region), farben.json: Ausgabe von farben.py

Eine Spielkarte deckt höchstens 2048 Blöcke ab. Die Welt ist größer, deshalb wird sie vorab aus den Weltdateien
gezeichnet (B Blöcke je Pixel) und die Karte gesperrt: Gesperrte Karten zeichnet das Spiel nie nach. Schattierung wie
im Spiel: Land heller, wenn es nach Süden ansteigt, Wasser dunkler, je tiefer es ist. Die Marken sind Banner-Marken der
Karte (mit Namen); ihre Lage wird auf den Maßstab der Karte umgerechnet. Der Spielerpfeil ist aus, er stünde falsch.

Ausgabe: <N>.dat (nach world/data/minecraft/maps/) und Weltkarte.zip (nach world/datapacks/). Die ID liegt weit über
den Karten der Spieler, damit eine neu gebastelte Karte sie nie überschreibt.
"""
import glob
import gzip
import json
import os
import sys
import zipfile

import nbtlib
from nbtlib import tag

ORT = json.load(open(sys.argv[1]))
PIXEL, FARBEN, AUS = sys.argv[2], json.load(open(sys.argv[3])), sys.argv[4]
MX, MZ = ORT["mitte"]
B = ORT["bloecke_pro_pixel"]
ID = ORT["karten_id"]
X0, Z0 = MX - 64 * B, MZ - 64 * B
SPIEL_B = 16                    # Maßstab 4: so rechnet das Spiel Marken in Pixel um
DATENVERSION = 5023
NS = "weltkarte"
FORMAT_MIN, FORMAT_MAX = 71, 121
mc = FARBEN["mc"]

pix = {}
for f in glob.glob(os.path.join(PIXEL, "*.json")):
    for k, v in json.load(open(f)).items():
        pix[tuple(map(int, k.split(",")))] = v

farben = bytearray(128 * 128)
for (px, pz), (f, h, tiefe) in pix.items():
    if mc[f][0] == 0:
        continue
    schach = (px + pz) & 1
    if f == "WATER":
        d = tiefe * 0.1 + schach * 0.2
        hell = 2 if d < 0.5 else (0 if d > 0.9 else 1)
    else:
        nord = pix.get((px, pz - 1))
        d = (h - (nord[1] if nord else h)) / 3 + (schach - 0.5) * 0.4
        hell = 2 if d > 0.6 else (0 if d < -0.6 else 1)
    farben[pz * 128 + px] = mc[f][0] * 4 + hell


def karte_pos(x, z):            # Weltposition → Position, die das Spiel bei Maßstab 4 an dieselbe Pixelstelle setzt
    return MX + round(((x - X0) / B - 64) * SPIEL_B), MZ + round(((z - Z0) / B - 64) * SPIEL_B)


def marke(m):
    x, z = karte_pos(*m["pos"])
    return tag.Compound({"pos": tag.IntArray([x, 64, z]), "color": tag.String(m["farbe"]),
                         "name": tag.String(m["name"])})


banner = tag.List[tag.Compound]([marke(m) for m in ORT["marken"]])
daten = nbtlib.File({
    "DataVersion": tag.Int(DATENVERSION),
    "data": tag.Compound({
        "dimension": tag.String("minecraft:overworld"),
        "xCenter": tag.Int(MX), "zCenter": tag.Int(MZ), "scale": tag.Byte(4),
        "locked": tag.Byte(1), "trackingPosition": tag.Byte(0), "unlimitedTracking": tag.Byte(0),
        "colors": tag.ByteArray([b - 256 if b > 127 else b for b in farben]),
        "banners": banner, "frames": tag.List[tag.Compound]([]),
    })})
os.makedirs(AUS, exist_ok=True)
daten.save(os.path.join(AUS, f"{ID}.dat"), gzipped=True)

karte = f'minecraft:filled_map[minecraft:map_id={ID},minecraft:item_name="Weltkarte"]'
dateien = {
    f"data/{NS}/function/tick.mcfunction":
        f"give @a[tag=!{NS}.hat] {karte}\ntag @a[tag=!{NS}.hat] add {NS}.hat\n",
    "data/minecraft/tags/function/tick.json": json.dumps({"values": [f"{NS}:tick"]}, indent=2) + "\n",
    "pack.mcmeta": json.dumps({"pack": {
        "description": "Weltkarte", "pack_format": FORMAT_MIN, "supported_formats": [FORMAT_MIN, FORMAT_MAX],
        "min_format": FORMAT_MIN, "max_format": FORMAT_MAX}}, indent=2) + "\n",
}
with zipfile.ZipFile(os.path.join(AUS, "Weltkarte.zip"), "w", zipfile.ZIP_DEFLATED) as zf:
    for pfad in sorted(dateien):
        zf.writestr(zipfile.ZipInfo(pfad, date_time=(2026, 1, 1, 0, 0, 0)), dateien[pfad].encode("utf-8"))
print(f"{len(pix)} Pixel, {len(ORT['marken'])} Marken")
