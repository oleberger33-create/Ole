"""Liest die Kartenfarben aus dem Server-Jar (mit javap), damit die Karte dieselben Farben hat wie im Spiel.

Aufruf:  python3 farben.py <klassen-ordner> > farben.json

<klassen-ordner>: entpacktes server-<version>.jar (net/minecraft/...). Ergebnis:
  "mc":     MapColor-Name → [id, rgb]
  "farben": Block-ID → MapColor-Name (erste Farbe in der Registrierung; Blöcke, die die Eigenschaften eines anderen
            Blocks kopieren, bekommen dessen Farbe; Blätter, Wolle usw. ergänzt pixel.py)
"""
import json
import re
import subprocess
import sys

ORDNER = sys.argv[1]


def javap(klasse):
    out = subprocess.run(["javap", "-c", "-p", f"{ORDNER}/net/minecraft/{klasse}.class"],
                         capture_output=True, text=True).stdout
    return out.split("static {};")[1].splitlines()


mc, werte = {"NONE": (0, 0)}, []
for z in javap("world/level/material/MapColor"):
    m = re.search(r"(iconst_(\d)|bipush\s+(-?\d+)|sipush\s+(-?\d+)|ldc(?:_w)?\s+#\d+\s+// int (-?\d+))", z)
    if m:
        werte.append(int(next(g for g in m.groups()[1:] if g is not None)))
    m = re.search(r"putstatic.*Field (\w+):Lnet/minecraft/world/level/material/MapColor;", z)
    if m:
        if len(werte) >= 2:
            mc[m.group(1)] = (werte[-2], werte[-1] & 0xFFFFFF)
        werte = []

farbstoff, offen = {}, []
for z in javap("world/item/DyeColor"):
    m = re.search(r"MapColor\.(\w+)", z)
    if m:
        offen.append(m.group(1))
    m = re.search(r"putstatic.*Field (\w+):Lnet/minecraft/world/item/DyeColor;", z)
    if m:
        farbstoff[m.group(1)] = offen[0] if offen else "NONE"
        offen = []

bloecke, offen = {}, []
for z in javap("world/level/block/Blocks"):
    m = re.search(r"putstatic.*Field (\w+):Lnet/minecraft/world/level/block/Block;", z)
    if m:
        farbe = "NONE"
        for art, name in offen:
            if art == "M":
                farbe = name
            elif art == "D":
                farbe = farbstoff.get(name, "NONE")
            elif name in bloecke:
                farbe = bloecke[name]
            else:
                continue
            break
        bloecke[m.group(1)] = farbe
        offen = []
        continue
    for art, muster in (("M", r"getstatic.*MapColor\.(\w+):"), ("D", r"getstatic.*DyeColor\.(\w+):"),
                        ("B", r"getstatic.*Field (\w+):Lnet/minecraft/world/level/block/Block;")):
        m = re.search(muster, z)
        if m:
            offen.append((art, m.group(1)))
            break

json.dump({"mc": mc, "farben": {k.lower(): v for k, v in bloecke.items()}}, sys.stdout)
