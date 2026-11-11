"""Baut das Datapack „Geheimbasis“: eine versteckte unterirdische Basis hinter einer Felswand.

Aufruf:  python3 basis.py <ort.json> [zip-datei] [entpackt-ordner]

ort.json enthält nur den Ursprung, damit die echten Koordinaten nicht im Repo landen:
    {"tuer": [x, y, z]}   untere Mitte der dreiteiligen Tür in der Felswand (Tür zeigt nach Westen)

Alles andere liegt relativ dazu fest. Das Pack baut die Basis einmal, testet danach Türen,
Aufzüge und XP-Farm selbst und schreibt das Ergebnis ins Scoreboard gb.test.
"""
import json
import math
import os
import shutil
import sys
import zipfile

NS = "geheim"
FORMAT_MIN, FORMAT_MAX = 71, 121   # 1.21.5 … 26.3

ORT = json.load(open(sys.argv[1]))
HIER = os.path.dirname(os.path.abspath(__file__))
ZIP = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HIER, "..", "Geheimbasis.zip")
ORDNER = sys.argv[3] if len(sys.argv) > 3 else None

X, Y, Z = ORT["tuer"]          # Felswand-Ebene, Türunterkante, mittlere Türspalte
ZD, ZE = Z - 1, Z + 1          # Fallschacht (Norden) und Aufzug (Süden)
L = Y - 29                     # Boden-Ebene der Basis (man steht auf L)

WAND, BODEN, DECKE = "deepslate_bricks", "polished_deepslate", "deepslate_tiles"
FELS = "stone"

dateien = {}


def datei(pfad, zeilen):
    text = "\n".join(zeilen) if isinstance(zeilen, list) else zeilen
    dateien[pfad] = text.rstrip("\n") + "\n"


def funktion(name, zeilen):
    datei(f"data/{NS}/function/{name}.mcfunction", zeilen)


def txt(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


# ---------------------------------------------------------------- Rohbau: Räume und Wände

class Bau:
    def __init__(self):
        self.innen = set()        # begehbare Luft
        self.fest = {}            # Pflichtblöcke (Wände, Fundamente, Möbel)
        self.dunkel = set()       # Innenräume, die dunkel bleiben (Farm)
        self.aussen = set()       # Luft im Freien: bekommt keine Wände drumherum

    def raum(self, x1, y1, z1, x2, y2, z2, dunkel=False):
        for x in range(x1, x2 + 1):
            for y in range(y1, y2 + 1):
                for z in range(z1, z2 + 1):
                    self.innen.add((x, y, z))
                    if dunkel:
                        self.dunkel.add((x, y, z))

    def block(self, x, y, z, blk):
        self.innen.discard((x, y, z))
        self.fest[(x, y, z)] = blk

    def box(self, x1, y1, z1, x2, y2, z2, blk):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                for z in range(min(z1, z2), max(z1, z2) + 1):
                    self.block(x, y, z, blk)

    def huelle(self):
        """Jede Luftzelle bekommt feste Nachbarn: Boden, Decke oder Wand."""
        for (x, y, z) in list(self.innen):
            for dx, dy, dz in [(1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1), (0, 1, 0), (0, -1, 0)]:
                q = (x + dx, y + dy, z + dz)
                if q in self.innen or q in self.fest or q in self.aussen:
                    continue
                self.fest[q] = BODEN if dy == -1 else DECKE if dy == 1 else WAND


b = Bau()

# Ankunftshalle, Gang, Räume
b.raum(X + 2, L, Z - 4, X + 7, L + 3, Z + 3)              # Ankunft
b.raum(X + 8, L, ZD, X + 37, L + 3, ZE)                   # Hauptgang
b.raum(X + 10, L, Z - 11, X + 22, L + 3, Z - 3)           # Lager & Werkstatt
b.raum(X + 25, L, Z - 11, X + 35, L + 3, Z - 3)           # Verzauberung
b.raum(X + 1, L, Z + 5, X + 11, L + 3, Z + 9)             # Schlafraum
b.raum(X + 38, L, Z - 4, X + 42, L + 2, Z + 5)            # Vorraum Tresor
b.raum(X + 44, L, Z - 4, X + 52, L + 2, Z + 5)            # Tresor
b.raum(X + 26, L, Z + 3, X + 30, L + 2, Z + 4)            # XP-Nische
# Durchgänge
b.raum(X + 1, L, ZD, X + 1, L + 1, ZD)                    # aus dem Landebecken
b.raum(X + 15, L, Z - 2, X + 17, L + 2, Z - 2)            # Gang → Lager
b.raum(X + 29, L, Z - 2, X + 31, L + 2, Z - 2)            # Gang → Verzauberung
b.raum(X + 3, L, Z + 4, X + 5, L + 2, Z + 4)              # Ankunft → Schlafraum
b.raum(X + 27, L, Z + 2, X + 29, L + 2, Z + 2)            # Gang → XP-Nische
b.raum(X + 43, L, Z - 1, X + 43, L + 1, Z)                # Tresortür (Kolbenebene)

# ---------------------------------------------------------------- Eingang in der Felswand

# Vorplatz: kleiner Absatz vor der Tür, damit man eben hineingehen kann
for z in range(ZD - 1, ZE + 1):
    b.block(X - 1, Y - 1, z, "grass_block")
    for y in range(Y, Y + 3):
        b.aussen.add((X - 1, y, z))
# Türöffnung (wird von den Kolben mit Stein gefüllt)
for z in (ZD, Z, ZE):
    for y in (Y, Y + 1):
        b.aussen.add((X, y, z))
# Fallschacht mit Landebecken
for y in range(L, Y):
    b.innen.add((X, y, ZD))
b.block(X, L - 1, ZD, "water")
b.block(X, L - 2, ZD, FELS)
# Trennsäule zwischen Schacht und Aufzug
b.box(X, L - 1, Z, X, Y - 1, Z, FELS)
# Aufzug (Seelensand → Blasensäule), oben eine Luftblase mit Knopf
b.block(X, L - 1, ZE, "soul_sand")
for y in range(L, Y - 1):
    b.block(X, y, ZE, "bubble_column[drag=false]")
b.innen.add((X, Y - 1, ZE))
# Schachtwände außen herum
for y in range(L - 1, Y):
    for z in (ZD - 1, ZE + 1):
        b.fest.setdefault((X, y, z), FELS)
    for z in (ZD, Z, ZE):
        b.fest.setdefault((X - 1, y, z), FELS)
        if (X + 1, y, z) not in b.innen:
            b.fest.setdefault((X + 1, y, z), FELS)
# Westwand der Ankunft: nur Becken-Ausgang und Aufzugstür offen
for y in range(L, L + 4):
    for z in range(Z - 4, Z + 4):
        if (X + 1, y, z) not in b.innen:
            b.block(X + 1, y, z, WAND)

# Technikraum hinter der Tür: alles massiv (auch Kies wird ersetzt), Bauteile kommen später
FEST_FELS = "stone!"     # Stein, der vorhandenes Material ersetzt (FELS füllt nur Löcher)
TECHNIK = [(x, y, z) for x in range(X + 1, X + 6) for y in range(Y - 2, Y + 3) for z in range(ZD - 2, ZE + 2)]
TECHNIK += [(x, Y + 3, z) for x in range(X + 2, X + 6) for z in range(ZD - 2, ZE + 2)]   # Deckel
for p in TECHNIK:
    if p not in b.innen:
        b.fest[p] = FEST_FELS
b.fest[(X + 1, L - 1, ZE)] = BODEN                       # unter der Aufzugstür

# ---------------------------------------------------------------- Fluchtweg (Wasseraufzug in den Teich)

FX, FZ = X + 4, Z + 11                      # Säule unter dem Teich
FLUCHT_OBEN = ORT.get("teich_y", Y + 15)    # Wasseroberfläche des Teichs
b.block(FX, L - 1, FZ, "soul_sand")
for y in range(L, FLUCHT_OBEN + 1):
    b.block(FX, y, FZ, "bubble_column[drag=false]")
for y in range(L - 1, FLUCHT_OBEN - 1):
    for dx, dz in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        if (FX + dx, y, FZ + dz) not in b.innen:
            b.fest.setdefault((FX + dx, y, FZ + dz), FELS)

# ---------------------------------------------------------------- XP-Farm (Zombie-Spawner)

FX0, FZ0 = X + 24, Z + 6         # Spawnerraum 9 × 9 (Front = Norden)
R = L + 11                       # Wasserebene im Spawnerraum
KX = FX0 + 4                     # Mittelachse (Schacht, Tötungszelle)
b.raum(FX0, R, FZ0 + 1, FX0 + 8, R + 3, FZ0 + 8, dunkel=True)       # Raum über dem Wasser
b.raum(FX0, R - 1, FZ0, FX0 + 8, R + 3, FZ0, dunkel=True)           # Rinne vorne (eine Stufe tiefer)
for y in range(L + 3, R - 1):                                       # Fallschacht
    b.raum(KX, y, FZ0, KX, y, FZ0, dunkel=True)
b.raum(KX, L + 1, FZ0, KX, L + 2, FZ0, dunkel=True)                # Tötungszelle
SPAWNER = (KX, R + 2, FZ0 + 4)
b.block(*SPAWNER, "spawner")

# ---------------------------------------------------------------- Feste Einbauten (Möbel, Licht)

moebel = []   # (x, y, z, block) – nach dem Rohbau gesetzt


def m(x, y, z, blk):
    b.innen.discard((x, y, z))
    moebel.append((x, y, z, blk))


def schild(x, y, z, facing, zeilen):
    text = ",".join(txt(t) for t in (zeilen + ["", "", "", ""])[:4])
    m(x, y, z, f"dark_oak_wall_sign[facing={facing}]{{front_text:{{has_glowing_text:1b,color:\"light_blue\","
               f"messages:[{text}]}}}}")


# Lager & Werkstatt
lx1, lx2, lz1, lz2 = X + 10, X + 22, Z - 11, Z - 3
for x in range(lx1 + 1, lx2 - 1, 2):
    for y in (L, L + 1):
        m(x, y, lz1, "chest[facing=south,type=right]")
        m(x + 1, y, lz1, "chest[facing=south,type=left]")
for i, blk in enumerate(["crafting_table", "furnace[facing=east]", "blast_furnace[facing=east]",
                         "smoker[facing=east]", "furnace[facing=east]", "crafting_table"]):
    m(lx1, L, lz1 + 2 + i, blk)
for i, blk in enumerate(["anvil[facing=north]", "smithing_table", "grindstone[face=floor,facing=north]",
                         "stonecutter[facing=west]", "loom[facing=west]", "cartography_table"]):
    m(lx2, L, lz1 + 2 + i, blk)
m(lx1 + 6, L, lz1 + 4, "ender_chest[facing=south]")
schild(X + 16, L + 3, Z - 1, "south", ["Lager &", "Werkstatt"])

# Verzauberung, Tisch mittig
vx, vz = X + 30, Z - 7
m(vx, L, vz, "enchanting_table")
regale = [(vx + d, L, vz - 2) for d in range(-2, 3)] + [(vx - 2, L, vz + d) for d in (-1, 0, 1)] \
         + [(vx + 2, L, vz + d) for d in (-1, 0, 1)] + [(vx + d, L + 1, vz - 2) for d in (-2, -1, 1, 2)]
for p in regale:
    m(*p, "bookshelf")
for x in range(X + 26, X + 35):
    m(x, L, Z - 11, "bookshelf")
    m(x, L + 1, Z - 11, "bookshelf")
m(X + 26, L, Z - 9, "brewing_stand")
m(X + 26, L, Z - 8, "water_cauldron[level=3]")
m(X + 26, L, Z - 7, "brewing_stand")
m(X + 34, L, Z - 8, "lectern[facing=west]")
schild(X + 30, L + 3, Z - 1, "south", ["Verzauberung"])

# Schlafraum, Fluchtweg-Tür in der Südwand
for bx in (X + 6, X + 9):
    m(bx, L, Z + 6, "red_bed[facing=north,part=head]")
    m(bx, L, Z + 7, "red_bed[facing=north,part=foot]")
m(X + 11, L, Z + 5, "chest[facing=west,type=single]")
m(X + 1, L, Z + 5, "cartography_table")
m(X + 1, L, Z + 9, "barrel[facing=up]")
m(X + 11, L, Z + 9, "barrel[facing=up]")
b.fest[(FX, L - 1, FZ - 1)] = WAND
m(FX, L, FZ - 1, "spruce_door[facing=north,half=lower,hinge=left,open=false]")
m(FX, L + 1, FZ - 1, "spruce_door[facing=north,half=upper,hinge=left,open=false]")
schild(FX + 1, L + 1, FZ - 2, "north", ["Fluchtweg", "↑ Teich ↑"])
schild(X + 4, L + 3, Z + 3, "north", ["Schlafraum"])

# XP-Nische: Hopper unter der Tötungszelle, Sichtschlitz, Truhe
m(KX, L, FZ0, "hopper[facing=north]")
m(KX, L, FZ0 - 1, "hopper[facing=west]")
m(KX - 1, L, FZ0 - 1, "hopper[facing=north]")
m(KX - 1, L, FZ0 - 2, "chest[facing=south,type=single]")
m(KX, L + 1, FZ0 - 1, "deepslate_tile_slab[type=bottom]")
m(KX, L + 2, FZ0 - 1, DECKE)
m(KX, R - 1, FZ0, "oak_wall_sign[facing=south]")     # hält das Wasser vom Schacht fern
schild(KX, L + 3, Z + 1, "north", ["XP-Farm", "Hier warten,", "Zombies fallen", "von oben"])

# Tresor-Vorraum und Tresor
schild(X + 42, L + 2, Z + 1, "west", ["Tresor"])
for z in range(Z - 4, Z + 6):
    if z in (Z - 1, Z):
        continue
    m(X + 52, L, z, "chest[facing=west,type=single]")
m(X + 52, L + 1, Z - 1, "barrel[facing=west]")
m(X + 52, L + 1, Z, "barrel[facing=west]")

# Lavafenster im Gang (Südwand)
for lx in (X + 13, X + 19):
    for y in (L + 1, L + 2):
        m(lx, y, Z + 2, "glass")
        b.block(lx, y, Z + 3, "lava")
        for dx, dz in [(1, 0), (-1, 0), (0, 1)]:
            b.fest.setdefault((lx + dx, y, Z + 3 + dz), WAND)
    b.fest.setdefault((lx, L, Z + 3), WAND)
    b.fest.setdefault((lx, L + 3, Z + 3), WAND)

# Laternen
laternen = [(x, L + 3, Z) for x in range(X + 10, X + 38, 6)] + [
    (X + 4, L + 3, Z - 2), (X + 4, L + 3, Z + 2), (X + 16, L + 3, Z - 7), (X + 30, L + 3, Z - 5),
    (X + 30, L + 3, Z - 9), (X + 6, L + 3, Z + 7), (X + 40, L + 2, Z), (X + 48, L + 2, Z - 2),
    (X + 48, L + 2, Z + 3), (X + 28, L + 2, Z + 3)]
for p in laternen:
    m(*p, "lantern[hanging=true]")

# ---------------------------------------------------------------- Redstone

# Haupttür: 6 Klebrige Kolben ziehen die Steine zurück (Strom = zu)
redstone = []   # Reihenfolge zählt: Träger, Komparator, Birne, Staub, Verstärker, Türsteine, Kolben


def r(x, y, z, blk):
    b.innen.discard((x, y, z))
    redstone.append((x, y, z, blk))


def staub(x, y, z, **seiten):
    s = ",".join(f"{k}={seiten.get(k, 'none')}" for k in ("east", "north", "south", "west"))
    r(x, y, z, f"redstone_wire[{s},power=0]")


TUERSTEIN = ORT.get("tuerstein", FELS)
# Luft, die der Schaltung Platz lässt
for p in [(X + 1, Y, ZD - 1), (X + 5, Y + 1, ZD - 1), (X + 4, Y + 2, ZD - 1), (X + 3, Y + 2, ZE + 1),
          (X + 4, Y, ZE + 1)]:
    r(*p, "air")
# Komparator liest die Kupferbirne und speist das Netz
r(X + 2, Y - 1, ZE, "comparator[facing=west,mode=compare,powered=false]")
r(X + 1, Y - 1, ZE, "waxed_copper_bulb[lit=true,powered=false]")
r(X, Y - 1, ZE, "stone_button[face=wall,facing=west,powered=false]")       # Knopf in der Luftblase
staub(X + 3, Y - 1, ZE + 1, north="side", east="side")
staub(X + 4, Y - 1, ZE + 1, west="side", east="up")
for z in range(ZD - 1, ZE + 2):                                            # untere Leitung
    nord = "side" if z > ZD - 1 else "none"
    sued = "side" if z < ZE + 1 else "none"
    west = "side" if z in (ZD, Z, ZE) else ("up" if z == ZD - 1 else "side")
    staub(X + 5, Y, z, north=nord, south=sued, west=west)
for z in (ZD, Z, ZE):
    r(X + 4, Y, z, "repeater[facing=east,delay=1,locked=false,powered=false]")
staub(X + 4, Y + 1, ZD - 1, east="side", west="up")                        # Treppe nach oben
for z in range(ZD - 1, ZE + 1):                                            # obere Leitung
    staub(X + 3, Y + 2, z, north="side" if z > ZD - 1 else "none", south="side",
          east="side" if z == ZD - 1 else "none")
# Außenknopf und Leitung zur Birne
r(X - 1, Y, ZD - 2, "stone_button[face=wall,facing=west,powered=false]")
staub(X + 1, Y, ZD - 2, south="side", north="side")
for z in (ZD - 1, ZD, Z):
    staub(X + 1, Y - 1, z, north="up" if z == ZD - 1 else "side", south="side")
# Fackelturm von der Ankunftshalle hoch zur Leitung (gerade Anzahl Umkehrungen)
for y in range(L, Y):
    k = (y - L) // 2
    if (y - L) % 2 == 0:
        r(X + 2, y, ZD - 1, BODEN)
    else:
        r(X + 2, y, ZD - 1, f"redstone_torch[lit={'true' if k % 2 == 0 else 'false'}]")
r(X + 3, L, ZD - 1, "stone_button[face=wall,facing=east,powered=false]")
r(X + 3, L + 2, ZD - 1, "dark_oak_wall_sign[facing=east]{front_text:{has_glowing_text:1b,color:\"light_blue\","
                        "messages:[\"Tür oben\",\"Knopf unten\",\"auf / zu\",\"\"]}}")
# Tür am Aufzug (hält das Wasser zurück)
m(X + 1, L, ZE, "oak_door[facing=east,half=lower,hinge=left,open=false]")
m(X + 1, L + 1, ZE, "oak_door[facing=east,half=upper,hinge=left,open=false]")
# Türsteine (eingefahren) und Kolben zuletzt
for z in (ZD, Z, ZE):
    for y in (Y, Y + 1):
        r(X + 1, y, z, TUERSTEIN)
for z in (ZD, Z, ZE):
    for y in (Y, Y + 1):
        r(X + 2, y, z, "sticky_piston[facing=west,extended=false]")

# Tresortür (2 × 2) in der Ebene TX, Kolben von Norden und Süden
TX = X + 43
r(TX, L + 2, Z + 3, "comparator[facing=south,mode=compare,powered=false]")
r(TX, L + 2, Z + 4, "waxed_copper_bulb[lit=true,powered=false]")
r(TX - 1, L + 2, Z + 4, "stone_button[face=wall,facing=west,powered=false]")
r(TX + 1, L + 2, Z + 4, "stone_button[face=wall,facing=east,powered=false]")
for z in range(Z - 3, Z + 3):
    staub(TX, L + 3, z, north="side", south="side")
for z, y in [(Z - 2, L), (Z - 2, L + 1), (Z + 1, L), (Z + 1, L + 1)]:
    r(TX, y, z, "iron_block")
for y in (L, L + 1):
    r(TX, y, Z - 3, "sticky_piston[facing=south,extended=false]")
    r(TX, y, Z + 2, "sticky_piston[facing=north,extended=false]")

# Ebene der Tresortür und Technik ringsum massiv
for z in range(Z - 4, Z + 6):
    for y in range(L - 1, L + 5):
        if (TX, y, z) not in b.innen:
            b.fest.setdefault((TX, y, z), WAND)
for z in range(Z - 3, Z + 3):
    b.fest[(TX, L + 2, z)] = WAND           # Träger der Leitung (über der Tür)
b.fest[(TX, L + 3, Z - 4)] = WAND
b.fest[(TX, L + 3, Z + 3)] = WAND
for (x, y, z, blk) in redstone:
    b.fest.pop((x, y, z), None)
# Träger unter Staub und Verstärkern
for (x, y, z, blk) in redstone:
    if blk.startswith(("redstone_wire", "repeater", "comparator")):
        if (x, y - 1, z) not in {(a, c, d) for a, c, d, _ in redstone}:
            b.fest[(x, y - 1, z)] = FELS if x < X + 10 else WAND
for p in [(X + 3, Y, z) for z in (ZD, Z, ZE)] + [(X + 3, Y + 1, z) for z in (ZD - 1, ZD, Z, ZE)] \
         + [(X + 3, Y - 1, ZE), (X + 4, Y, ZD - 1)]:
    b.fest[p] = FELS

b.huelle()
for (x, y, z, blk) in redstone + moebel:
    b.fest.pop((x, y, z), None)

# ---------------------------------------------------------------- Licht

LICHT = {"lantern": 15, "lava": 15, "redstone_torch[lit=true]": 7}


def licht_setzen():
    """Unsichtbare Lichtblöcke überall, wo in der Basis sonst Monster spawnen könnten."""
    quellen = [((x, y, z), 15) for (x, y, z, blk) in moebel if blk.startswith("lantern")]
    quellen += [((x, y, z), 15) for (x, y, z), blk in b.fest.items() if blk == "lava"]
    hell = {}

    def ausbreiten(start):
        offen = list(start)
        while offen:
            neu = []
            for p, lv in offen:
                if hell.get(p, 0) >= lv:
                    continue
                hell[p] = lv
                for d in [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]:
                    q = (p[0] + d[0], p[1] + d[1], p[2] + d[2])
                    if q in b.innen and q not in b.dunkel and lv > 1:
                        neu.append((q, lv - 1))
            offen = neu
    ausbreiten(quellen)
    neu = []
    for p in sorted(b.innen, key=lambda q: (q[1], q[0], q[2])):
        x, y, z = p
        unten = b.fest.get((x, y - 1, z))
        if p in b.dunkel or unten is None or unten in ("water", "lava") or unten.startswith("bubble"):
            continue
        if (x, y + 1, z) not in b.innen or hell.get(p, 0) > 0 or x < X + 1:
            continue
        neu.append(p)
        ausbreiten([(p, 13)])
    return neu


lichter = licht_setzen()

# ---------------------------------------------------------------- Befehle


def quader(zellen):
    rest = set(zellen)
    out = []
    for p in sorted(zellen, key=lambda q: (q[1], q[2], q[0])):
        if p not in rest:
            continue
        x, y, z = p
        x2 = x
        while (x2 + 1, y, z) in rest:
            x2 += 1
        z2 = z
        while all((xx, y, z2 + 1) in rest for xx in range(x, x2 + 1)):
            z2 += 1
        y2 = y
        while all((xx, y2 + 1, zz) in rest for xx in range(x, x2 + 1) for zz in range(z, z2 + 1)):
            y2 += 1
        for xx in range(x, x2 + 1):
            for yy in range(y, y2 + 1):
                for zz in range(z, z2 + 1):
                    rest.discard((xx, yy, zz))
        out.append((x, y, z, x2, y2, z2))
    return out


def fuellen(zellen, blk, zusatz=""):
    out = []
    for x1, y1, z1, x2, y2, z2 in quader(zellen):
        if (x1, y1, z1) == (x2, y2, z2) and not zusatz:
            out.append(f"setblock {x1} {y1} {z1} minecraft:{blk}")
        else:
            out.append(f"fill {x1} {y1} {z1} {x2} {y2} {z2} minecraft:{blk}{zusatz}")
    return out


befehle = []
gruppen = {}
spaet = []
for p, blk in b.fest.items():
    if blk in ("water", "lava", "spawner") or blk.startswith("bubble_column") or blk == "soul_sand":
        spaet.append((p, blk))
        continue
    gruppen.setdefault(blk, set()).add(p)
for blk, zellen in sorted(gruppen.items()):
    zusatz = " replace #minecraft:replaceable" if blk == FELS else ""   # vorhandenes Gestein bleibt
    befehle += fuellen(zellen, blk.rstrip("!"), zusatz)
befehle += fuellen(b.innen | b.aussen, "air")
for (x, y, z, blk) in moebel:
    befehle.append(f"setblock {x} {y} {z} minecraft:{blk}")
for (x, y, z, blk) in redstone:
    befehle.append(f"setblock {x} {y} {z} minecraft:{blk}")
for p in lichter:
    befehle.append(f"setblock {p[0]} {p[1]} {p[2]} minecraft:light[level=13]")
for (x, y, z), blk in sorted(spaet, key=lambda e: (e[1] != "soul_sand", e[0][1])):
    if blk == "spawner":
        befehle.append(f"setblock {x} {y} {z} minecraft:spawner{{SpawnData:{{entity:{{id:\"minecraft:zombie\"}}}},"
                       f"MinSpawnDelay:200s,MaxSpawnDelay:600s,SpawnCount:4s,MaxNearbyEntities:8s,"
                       f"RequiredPlayerRange:16s,SpawnRange:4s}}")
    else:
        befehle.append(f"setblock {x} {y} {z} minecraft:{blk}")
# Wasser der Farm: Quellen hinten und an den Enden der Rinne
for x in range(FX0, FX0 + 9):
    befehle.append(f"setblock {x} {R} {FZ0 + 8} minecraft:water")
befehle.append(f"setblock {FX0} {R - 1} {FZ0} minecraft:water")
befehle.append(f"setblock {FX0 + 8} {R - 1} {FZ0} minecraft:water")

teile = [befehle[i:i + 200] for i in range(0, len(befehle), 200)]

# ---------------------------------------------------------------- Funktionen

alle = list(b.innen) + list(b.aussen) + list(b.fest) + [(x, y, z) for x, y, z, _ in redstone + moebel]
bx1, bx2 = min(p[0] for p in alle), max(p[0] for p in alle)
bz1, bz2 = min(p[2] for p in alle), max(p[2] for p in alle)
cx1, cx2, cz1, cz2 = bx1 >> 4, bx2 >> 4, bz1 >> 4, bz2 >> 4
LADEN = " ".join(f"if loaded {cx * 16 + 8} 0 {cz * 16 + 8}"
                 for cx in range(cx1, cx2 + 1) for cz in range(cz1, cz2 + 1))
FL = f"{cx1 * 16} {cz1 * 16} {cx2 * 16 + 15} {cz2 * 16 + 15}"

funktion("load", [
    "scoreboard objectives add gb.zustand dummy",
    "scoreboard objectives add gb.test dummy",
    f"execute unless score #gebaut gb.zustand matches 1 unless score #stufe gb.zustand matches 1.. run function {NS}:bau/start",
])
funktion("tick", [f"execute if score #stufe gb.zustand matches 1.. run function {NS}:bau/tick"])
funktion("bau/start", [
    f"forceload add {FL}",
    "scoreboard players set #stufe gb.zustand 1",
])
funktion("bau/tick", [f"execute {LADEN} run function {NS}:bau/schritt"])
schritt = []
for i in range(1, len(teile) + 1):
    schritt.append(f"execute if score #stufe gb.zustand matches {i} run function {NS}:bau/teil_{i:02d}")
schritt += ["scoreboard players add #stufe gb.zustand 1",
            f"execute if score #stufe gb.zustand matches {len(teile) + 1}.. run function {NS}:bau/fertig"]
funktion("bau/schritt", schritt)
for i, t in enumerate(teile, 1):
    funktion(f"bau/teil_{i:02d}", t)
funktion("bau/fertig", [
    "scoreboard players set #stufe gb.zustand 0",
    "scoreboard players set #gebaut gb.zustand 1",
    f"schedule function {NS}:test/t1 60t",
])


def zu_haupt(name):
    pruef = [f"if block {X + 2} {y} {z} minecraft:sticky_piston[extended=true]" for z in (ZD, Z, ZE) for y in (Y, Y + 1)]
    pruef += [f"if block {X} {y} {z} minecraft:{TUERSTEIN}" for z in (ZD, Z, ZE) for y in (Y, Y + 1)]
    return f"execute store success score #{name} gb.test " + " ".join(pruef)


def auf_haupt(name):
    pruef = [f"if block {X + 2} {y} {z} minecraft:sticky_piston[extended=false]" for z in (ZD, Z, ZE) for y in (Y, Y + 1)]
    pruef += [f"if block {X} {y} {z} minecraft:air" for z in (ZD, Z, ZE) for y in (Y, Y + 1)]
    return f"execute store success score #{name} gb.test " + " ".join(pruef)


def tresor(name, offen):
    pruef = [f"if block {TX} {y} {z} minecraft:sticky_piston[extended={'false' if offen else 'true'}]"
             for z in (Z - 3, Z + 2) for y in (L, L + 1)]
    ziel = "air" if offen else "iron_block"
    pruef += [f"if block {TX} {y} {z} minecraft:{ziel}" for z in (Z - 1, Z) for y in (L, L + 1)]
    return f"execute store success score #{name} gb.test " + " ".join(pruef)


AUSSEN = (X, Y, ZD - 2)
B0 = (X + 2, L, ZD - 1)
funktion("test/t1", [
    "# Selbsttest: Tür zu? Dann Außenknopf drücken (Redstone-Block statt des Felsblocks)",
    zu_haupt("haupt_zu_start"),
    f"setblock {AUSSEN[0]} {AUSSEN[1]} {AUSSEN[2]} minecraft:redstone_block",
    f"schedule function {NS}:test/t1b 6t",
])
funktion("test/t1b", [f"setblock {AUSSEN[0]} {AUSSEN[1]} {AUSSEN[2]} minecraft:{ORT.get('knopfstein', 'andesite')}",
                      f"schedule function {NS}:test/t2 30t"])
funktion("test/t2", [
    auf_haupt("haupt_auf_aussen"),
    f"setblock {X} {Y - 1} {ZE} minecraft:redstone_block",
    f"schedule function {NS}:test/t2b 6t",
])
funktion("test/t2b", [f"setblock {X} {Y - 1} {ZE} minecraft:stone_button[face=wall,facing=west]",
                      f"schedule function {NS}:test/t3 30t"])
funktion("test/t3", [
    zu_haupt("haupt_zu_blase"),
    f"setblock {B0[0]} {B0[1]} {B0[2]} minecraft:redstone_block",
    f"schedule function {NS}:test/t3b 10t",
])
funktion("test/t3b", [f"setblock {B0[0]} {B0[1]} {B0[2]} minecraft:{BODEN}", f"schedule function {NS}:test/t4 100t"])
funktion("test/t4", [
    auf_haupt("haupt_auf_saeule"),
    f"setblock {B0[0]} {B0[1]} {B0[2]} minecraft:redstone_block",
    f"schedule function {NS}:test/t4b 10t",
])
funktion("test/t4b", [f"setblock {B0[0]} {B0[1]} {B0[2]} minecraft:{BODEN}", f"schedule function {NS}:test/t5 100t"])
funktion("test/t5", [
    zu_haupt("haupt_zu_saeule"),
    tresor("tresor_zu_start", False),
    f"setblock {TX - 1} {L + 2} {Z + 4} minecraft:redstone_block",
    f"schedule function {NS}:test/t5b 6t",
])
funktion("test/t5b", [f"setblock {TX - 1} {L + 2} {Z + 4} minecraft:stone_button[face=wall,facing=west]",
                      f"schedule function {NS}:test/t6 30t"])
funktion("test/t6", [
    tresor("tresor_auf", True),
    f"setblock {TX + 1} {L + 2} {Z + 4} minecraft:redstone_block",
    f"schedule function {NS}:test/t6b 6t",
])
funktion("test/t6b", [f"setblock {TX + 1} {L + 2} {Z + 4} minecraft:stone_button[face=wall,facing=east]",
                      f"schedule function {NS}:test/t7 30t"])
funktion("test/t7", [
    tresor("tresor_zu", False),
    f"execute store success score #aufzug gb.test if block {X} {L - 1} {ZE} minecraft:soul_sand "
    f"if block {X} {L} {ZE} minecraft:bubble_column if block {X} {Y - 2} {ZE} minecraft:bubble_column",
    f"execute store success score #becken gb.test if block {X} {L - 1} {ZD} minecraft:water",
    f"execute store success score #flucht gb.test if block {FX} {L - 1} {FZ} minecraft:soul_sand "
    f"if block {FX} {L} {FZ} minecraft:bubble_column if block {FX} {FLUCHT_OBEN} {FZ} minecraft:bubble_column",
    f"execute store success score #spawner gb.test if block {SPAWNER[0]} {SPAWNER[1]} {SPAWNER[2]} minecraft:spawner",
    "# Testzombie hinten im Spawnerraum",
    f"summon minecraft:zombie {FX0 + 1.5} {R} {FZ0 + 7.5} {{Tags:[\"gb.test\"],IsBaby:0b,PersistenceRequired:1b}}",
    f"schedule function {NS}:test/t8 400t",
])
funktion("test/t8", [
    f"execute store success score #farm_ankunft gb.test if entity "
    f"@e[type=minecraft:zombie,tag=gb.test,x={KX},y={L + 1},z={FZ0},dx=0,dy=1,dz=0]",
    f"execute store result score #farm_hp gb.test run data get entity @e[type=minecraft:zombie,tag=gb.test,limit=1] Health",
    f"execute store result score #farm_y gb.test run data get entity @e[type=minecraft:zombie,tag=gb.test,limit=1] Pos[1]",
    f"execute store result score #farm_z gb.test run data get entity @e[type=minecraft:zombie,tag=gb.test,limit=1] Pos[2]",
    "tp @e[type=minecraft:zombie,tag=gb.test] ~ -200 ~",
    f"forceload remove {FL}",
    "scoreboard players set #fertig gb.test 1",
])

datei("data/minecraft/tags/function/load.json", json.dumps({"values": [f"{NS}:load"]}, indent=2))
datei("data/minecraft/tags/function/tick.json", json.dumps({"values": [f"{NS}:tick"]}, indent=2))
datei("pack.mcmeta", json.dumps({
    "pack": {
        "description": [{"text": "Geheimbasis", "color": "dark_gray"}],
        "pack_format": FORMAT_MIN,
        "supported_formats": [FORMAT_MIN, FORMAT_MAX],
        "min_format": FORMAT_MIN,
        "max_format": FORMAT_MAX,
    }
}, indent=2, ensure_ascii=False))

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
        info.compress_type = zipfile.ZIP_DEFLATED
        zf.writestr(info, dateien[pfad].encode("utf-8"))
print(f"Luft {len(b.innen)}, feste Blöcke {len(b.fest)}, Möbel {len(moebel)}, Redstone {len(redstone)}, "
      f"Lichter {len(lichter)}")
print(f"{len(befehle)} Befehle in {len(teile)} Teilen, Chunks x {cx1}..{cx2} z {cz1}..{cz2}")
print(f"Zip → {ZIP} ({os.path.getsize(ZIP) // 1024} KB)")
