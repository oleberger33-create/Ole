"""Bauplan der Himmelsinsel.

Erzeugt Voxelmodelle {(x, y, z): blockzustand} für die schwebende Spawn-Insel und für die
Bodenstation darunter. Alle Zufallswerte sind fest geseedet, jeder Build sieht gleich aus.
"""
import math
import random

from haendler import HAENDLER

F = 224                       # Oberkante der Insel (Grasblöcke), man läuft auf F + 1
SPAWN = (0, F + 1, 6)         # Weltspawn auf dem Platz
BIB = (0, -18)                # Mitte der Zauberbibliothek
WERK = (13, -6, 25, 6)        # Werkstatt: x1, z1, x2, z2
FLUCH = (-17, 17)             # Mitte der Fluchhütte
BRETT = (32, 38)              # Sprungbrett bei x = 0 von z bis z
LANDUNG = (0, 41)             # Mitte der Bodenstation (x, z)
BEREICH = (-48, -48, 47, 47)  # Chunks, die zum Bauen geladen werden (x1, z1, x2, z2)
AMBOSSE = [(15, F + 1, -5), (17, F + 1, -5), (19, F + 1, -5)]


# ---------------------------------------------------------------- Modell & Rauschen

class Modell:
    def __init__(self):
        self.b = {}
        self.frei = set()  # (x, z)-Spalten, auf denen keine Pflanzen wachsen sollen

    def set(self, x, y, z, blk):
        if blk == "air":
            self.b.pop((x, y, z), None)
        else:
            self.b[(x, y, z)] = blk

    def get(self, x, y, z):
        return self.b.get((x, y, z))

    def box(self, x1, y1, z1, x2, y2, z2, blk):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                for z in range(min(z1, z2), max(z1, z2) + 1):
                    self.set(x, y, z, blk)


def _h(*werte):
    n = 2166136261
    for v in werte:
        n = ((n ^ (v & 0xFFFFFFFF)) * 16777619) & 0xFFFFFFFF
    n ^= n >> 15
    n = (n * 2246822519) & 0xFFFFFFFF
    n ^= n >> 13
    return n / 0xFFFFFFFF


def rauschen(x, z, s, seed=0):
    fx, fz = x / s, z / s
    ix, iz = math.floor(fx), math.floor(fz)
    tx, tz = fx - ix, fz - iz
    tx, tz = tx * tx * (3 - 2 * tx), tz * tz * (3 - 2 * tz)
    a, b = _h(ix, iz, seed), _h(ix + 1, iz, seed)
    c, d = _h(ix, iz + 1, seed), _h(ix + 1, iz + 1, seed)
    return (a + (b - a) * tx) * (1 - tz) + (c + (d - c) * tx) * tz


def rauschen3(x, y, z, s, seed=0):
    return (rauschen(x + y * 0.71, z, s, seed) + rauschen(x, z - y * 0.67, s, seed + 1)) / 2


def winkelabstand(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)


def treppe_zur_mitte(dx, dz):
    """Blickrichtung einer Dachtreppe, deren hohe Seite zur Mitte zeigt."""
    if abs(dx) >= abs(dz):
        return "west" if dx > 0 else "east"
    return "north" if dz > 0 else "south"


# ---------------------------------------------------------------- Gelände

def gestein(x, y, z, k, seed):
    n = rauschen3(x, y, z, 4.0, seed + 7)
    m = rauschen3(x, y, z, 3.0, seed + 11)
    if k <= 4 and m > 0.70:
        return "mossy_cobblestone"
    if n < 0.30:
        return "andesite"
    if n > 0.72:
        return "tuff"
    if m > 0.76:
        return "cobblestone"
    if k > 13 and m < 0.25:
        return "deepslate"
    return "stone"


def insel(m, cx, cz, oben, R, tiefe, seed, amp=2.0):
    """Schwebende Insel: Graskappe, Erde, darunter ein zerklüfteter Gesteinskegel."""
    rng = random.Random(seed)
    p = [rng.uniform(0, 2 * math.pi) for _ in range(3)]

    def rand(theta):
        return R + amp * (0.55 * math.sin(3 * theta + p[0]) + 0.3 * math.sin(5 * theta + p[1])
                          + 0.15 * math.sin(8 * theta + p[2]))

    # Felszapfen, die unter der Insel herabhängen: (x, z, Radius, Länge)
    zapfen = []
    for _ in range(int(R / 3.5)):
        w, s = rng.uniform(0, 2 * math.pi), rng.uniform(0.1, 0.65) * R
        zapfen.append((cx + s * math.cos(w), cz + s * math.sin(w), rng.uniform(1.8, 3.2),
                       rng.uniform(0.25, 0.5) * tiefe))
    unten = {}
    ext = int(R + amp + 2)
    for x in range(cx - ext, cx + ext + 1):
        for z in range(cz - ext, cz + ext + 1):
            dx, dz = x - cx, z - cz
            r = math.hypot(dx, dz)
            rt = rand(math.atan2(dz, dx))
            if r > rt:
                continue
            t = r / rt
            n = rauschen(x, z, 4, seed)
            # bauchige Kuppel plus spitzer Kern, mit zerklüftetem Rand
            d = 2 + 0.28 * tiefe * math.sqrt(max(0.0, 1 - t * t)) + 0.62 * tiefe * (1 - t) ** 2.6
            d *= 0.8 + 0.4 * n
            for zx, zz, zr, zl in zapfen:
                a = math.hypot(x - zx, z - zz)
                if a < zr:
                    d += zl * (1 - a / zr) ** 1.5
            d = max(1, int(round(d)))
            erde = 2 + (1 if n > 0.5 else 0)
            for k in range(d + 1):
                if k == 0:
                    blk = "grass_block"
                elif k < erde:
                    blk = "dirt"
                elif k == erde:
                    blk = "rooted_dirt" if rng.random() < 0.25 else "dirt"
                else:
                    blk = gestein(x, oben - k, z, k, seed)
                m.set(x, oben - k, z, blk)
            unten[(x, z)] = oben - d
    unterseite(m, unten, rng)
    ranken(m, unten, oben, rng)
    return unten


def unterseite(m, unten, rng):
    """Hängende Wurzeln, Leuchtflechten, Tropfsteine, Amethyst und Leuchtbeeren."""
    for (x, z), yb in sorted(unten.items()):
        if m.get(x, yb - 1, z):
            continue
        r = rng.random()
        if m.get(x, yb, z) in ("dirt", "rooted_dirt", "grass_block"):
            if r < 0.35:
                m.set(x, yb - 1, z, "hanging_roots")
            continue
        if r < 0.12:
            m.set(x, yb - 1, z, "glow_lichen[up=true]")
        elif r < 0.19:
            laenge = rng.randint(1, 4)
            formen = {1: ["tip"], 2: ["frustum", "tip"], 3: ["base", "frustum", "tip"],
                      4: ["base", "middle", "frustum", "tip"]}[laenge]
            m.set(x, yb, z, "dripstone_block")
            for i, form in enumerate(formen):
                m.set(x, yb - 1 - i, z, f"pointed_dripstone[thickness={form},vertical_direction=down]")
        elif r < 0.23:
            m.set(x, yb, z, "amethyst_block")
            m.set(x, yb - 1, z, "amethyst_cluster[facing=down]")
        elif r < 0.26:
            laenge = rng.randint(2, 5)
            beeren = rng.random() < 0.6
            for i in range(laenge - 1):
                m.set(x, yb - 1 - i, z, f"cave_vines_plant[berries={str(beeren and i % 2 == 1).lower()}]")
            m.set(x, yb - laenge, z, f"cave_vines[age=25,berries={str(beeren).lower()}]")


def ranken(m, unten, oben, rng):
    """Ranken, die am Inselrand herunterhängen."""
    richtungen = [(1, 0, "west"), (-1, 0, "east"), (0, 1, "north"), (0, -1, "south")]
    for (x, z) in sorted(unten):
        for dx, dz, seite in richtungen:
            nx, nz = x + dx, z + dz
            if (nx, nz) in unten or rng.random() > 0.10:
                continue
            for i in range(rng.randint(2, 6)):
                y = oben - 1 - i
                if m.get(nx, y, nz):
                    break
                m.set(nx, y, nz, f"vine[{seite}=true]")


# ---------------------------------------------------------------- Bauwerke

def laternenpfahl(m, x, y0, z, hoehe=2, holz="spruce_fence"):
    """Zaunpfahl mit Laterne obendrauf; y0 ist der Boden, auf dem der Pfahl steht."""
    for i in range(1, hoehe + 1):
        m.set(x, y0 + i, z, holz)
    m.set(x, y0 + hoehe + 1, z, "lantern[hanging=false]")
    m.frei.add((x, z))


def platz(m, rng):
    """Runder Platz mit Brunnen; im Brunnen steht ein Leuchtfeuer auf Smaragd."""
    for x in range(-8, 9):
        for z in range(-8, 9):
            r = math.hypot(x, z)
            if r > 7.6:
                continue
            m.frei.add((x, z))
            if r <= 3.6:
                kern = max(abs(x), abs(z))
                m.set(x, F - 1, z, "emerald_block" if kern <= 2 else "dark_prismarine")
                m.set(x, F, z, "emerald_block" if kern <= 1 else "water")
            elif r <= 4.6:
                m.set(x, F, z, "polished_deepslate")
                m.set(x, F + 1, z, "polished_deepslate_slab[type=bottom]")
            elif r <= 5.5:
                m.set(x, F, z, "stone_bricks")
            elif r <= 6.5:
                m.set(x, F, z, "polished_andesite")
            else:
                w = rng.random()
                m.set(x, F, z, "mossy_stone_bricks" if w < 0.22 else
                      "cracked_stone_bricks" if w < 0.30 else "stone_bricks")
    for x, z in [(0, 7), (0, -7), (7, 0), (-7, 0)]:
        m.set(x, F, z, "chiseled_stone_bricks")
    m.set(0, F + 1, 0, "beacon")
    m.set(0, F + 2, 0, "purple_stained_glass")
    for x, z in [(5, 5), (-5, 5), (5, -5), (-5, -5)]:
        laternenpfahl(m, x, F, z)


def stand_position(phi, r=6.9):
    cx, cz = BIB
    return cx + round(r * math.sin(math.radians(phi))), cz + round(r * math.cos(math.radians(phi)))


def bibliothek(m, rng):
    """Runde Zauberbibliothek mit Kegeldach, Bücherwänden und sieben Händlerständen."""
    cx, cz = BIB
    stand_winkel = [h["platz"] for h in HAENDLER if isinstance(h["platz"], int)]
    saeulen = [22.5 + 45 * k for k in range(8)]
    for x in range(cx - 11, cx + 12):
        for z in range(cz - 11, cz + 12):
            dx, dz = x - cx, z - cz
            r = math.hypot(dx, dz)
            if r >= 9.4:
                continue
            phi = math.degrees(math.atan2(dx, dz)) % 360
            m.frei.add((x, z))
            m.set(x, F - 1, z, "stone")
            if r < 7.5:
                m.set(x, F, z, "polished_deepslate" if 2.6 <= r < 3.4 else "dark_oak_planks")
            else:
                m.set(x, F, z, "polished_deepslate")
            if 7.5 <= r < 8.7:
                tuer = dz > 0 and abs(dx) <= 1
                rahmen = dz > 0 and abs(dx) == 2
                saeule = min(winkelabstand(phi, s) for s in saeulen) < 5.0
                fenster = min(winkelabstand(phi, s) for s in stand_winkel) < 9.5
                for y in range(F + 1, F + 8):
                    if tuer and y <= F + 4:
                        continue
                    if tuer and y == F + 5:
                        blk = "chiseled_deepslate"
                    elif rahmen and y <= F + 5:
                        blk = "polished_deepslate"
                    elif saeule:
                        blk = "stripped_dark_oak_log[axis=y]"
                    elif y == F + 1:
                        blk = "polished_deepslate"
                    elif y == F + 7:
                        blk = "dark_oak_planks"
                    elif fenster and F + 3 <= y <= F + 5:
                        blk = "purple_stained_glass"
                    else:
                        blk = "cracked_deepslate_bricks" if rng.random() < 0.08 else "deepslate_bricks"
                    m.set(x, y, z, blk)
            # Bücherwand innen, mit Lücken für Eingang und Stände
            if 6.55 <= r < 7.5:
                frei_fuer_stand = min(winkelabstand(phi, s) for s in stand_winkel) < 13
                frei_fuer_tuer = winkelabstand(phi, 0) < 22
                if not (frei_fuer_stand or frei_fuer_tuer):
                    for y in range(F + 1, F + 4):
                        m.set(x, y, z, "bookshelf")
                    if rng.random() < 0.3:
                        farbe = rng.choice(["candle", "purple_candle", "white_candle"])
                        m.set(x, F + 4, z, f"{farbe}[candles={rng.randint(1, 4)},lit=true]")
    # Kegeldach aus Schiefer, außen mit Treppen belegt
    dach = []
    y = F + 8
    while True:
        rr = 9.9 - 0.82 * (y - (F + 8))
        if rr < 1.0:
            break
        for x in range(cx - 11, cx + 12):
            for z in range(cz - 11, cz + 12):
                r = math.hypot(x - cx, z - cz)
                if rr - 1.45 <= r < rr:
                    m.set(x, y, z, "deepslate_tiles")
                    dach.append((x, y, z))
        y += 1
    spitze = y
    for i, blk in enumerate(["amethyst_block", "amethyst_block", "purple_stained_glass",
                             "lightning_rod[facing=up]"]):
        m.set(cx, spitze - 1 + i, cz, blk)
    for x, y, z in dach:
        if m.get(x, y + 1, z) is None:
            m.set(x, y, z, f"deepslate_tile_stairs[facing={treppe_zur_mitte(x - cx, z - cz)},half=bottom]")
    # Kronleuchter
    for y in range(F + 9, spitze - 1):
        m.set(cx, y, cz, "dark_oak_fence")
    for d in (1, 2):
        for ax, az in [(d, 0), (-d, 0), (0, d), (0, -d)]:
            m.set(cx + ax, F + 9, cz + az, "dark_oak_fence")
    for ax, az in [(2, 0), (-2, 0), (0, 2), (0, -2), (0, 0)]:
        m.set(cx + ax, F + 8, cz + az, "lantern[hanging=true]")
    # Podest des Meister-Bibliothekars
    m.box(cx - 1, F + 1, cz - 1, cx + 1, F + 1, cz + 1, "polished_deepslate")
    for ax, az, blick in [(0, 2, "north"), (0, -2, "south"), (2, 0, "west"), (-2, 0, "east")]:
        m.set(cx + ax, F + 1, cz + az, f"polished_deepslate_stairs[facing={blick},half=bottom]")
    for ax, az in [(1, 1), (-1, 1), (1, -1), (-1, -1)]:
        m.set(cx + ax, F + 2, cz + az, "purple_candle[candles=4,lit=true]")
    # Teppich vor jedem Stand
    for h in HAENDLER:
        if isinstance(h["platz"], int):
            tx, tz = stand_position(h["platz"], 5.4)
            m.set(tx, F + 1, tz, f"{h['teppich']}_carpet")


def dachstufen(m, x1, z1, x2, z2, y, stufen, treppe, voll, deckel):
    """Walmdach: jede Stufe ein Ring aus Treppen, oben ein Deckel aus Stufen."""
    for i in range(stufen):
        a1, b1, a2, b2 = x1 + i, z1 + i, x2 - i, z2 - i
        for x in range(a1, a2 + 1):
            for z in range(b1, b2 + 1):
                if x in (a1, a2):
                    blick = "east" if x == a1 else "west"
                elif z in (b1, b2):
                    blick = "south" if z == b1 else "north"
                else:
                    m.set(x, y + i, z, voll)
                    continue
                m.set(x, y + i, z, f"{treppe}[facing={blick},half=bottom]")
    i = stufen
    for x in range(x1 + i, x2 - i + 1):
        for z in range(z1 + i, z2 - i + 1):
            m.set(x, y + i, z, deckel)


def werkstatt(m, rng):
    """Offene Werkstatt: Zaubertisch mit 28 Bücherregalen, Ambosse, Schleifstein, Endertruhen."""
    x1, z1, x2, z2 = WERK
    for x in range(x1, x2 + 1):
        for z in range(z1, z2 + 1):
            m.frei.add((x, z))
            rand = x in (x1, x2) or z in (z1, z2)
            m.set(x, F, z, "stone_bricks" if rand else "spruce_planks")
            m.set(x, F - 1, z, "stone")
    pfosten = [(x1, z1), (x2, z1), (x1, z2), (x2, z2), (19, z1), (19, z2), (x2, 0)]
    for x, z in pfosten:
        m.box(x, F + 1, z, x, F + 4, z, "stripped_spruce_log[axis=y]")
    for x in range(x1 + 1, x2):
        for z in (z1, z2):
            if (x, z) not in pfosten:
                m.set(x, F + 1, z, "spruce_fence")
    for z in range(z1 + 1, z2):
        if (x2, z) not in pfosten:
            m.set(x2, F + 1, z, "spruce_fence")
    dachstufen(m, x1 - 1, z1 - 1, x2 + 1, z2 + 1, F + 5, 4, "spruce_stairs", "spruce_planks",
               "spruce_slab[type=bottom]")
    # Zaubertisch mit Regalring (5 × 5, zwei hoch, offen nach Westen und Osten)
    ex, ez = 19, 0
    m.set(ex, F + 1, ez, "enchanting_table")
    for x in range(ex - 2, ex + 3):
        for z in range(ez - 2, ez + 3):
            if max(abs(x - ex), abs(z - ez)) == 2 and z != ez:
                m.set(x, F + 1, z, "bookshelf")
                m.set(x, F + 2, z, "bookshelf")
                if rng.random() < 0.35:
                    m.set(x, F + 3, z, f"candle[candles={rng.randint(1, 3)},lit=true]")
    for x, y, z in AMBOSSE:
        m.set(x, y, z, "anvil[facing=east]")
    m.set(21, F + 1, -5, "grindstone[face=floor,facing=north]")
    m.set(23, F + 1, -5, "smithing_table")
    m.set(15, F + 1, 5, "crafting_table")
    m.set(17, F + 1, 5, "crafting_table")
    m.set(19, F + 1, 5, "ender_chest[facing=north]")
    m.set(21, F + 1, 5, "ender_chest[facing=north]")
    m.set(23, F + 1, 5, "stonecutter[facing=north]")
    for x, z in [(16, -3), (22, -3), (16, 3), (22, 3)]:
        m.set(x, F + 4, z, "lantern[hanging=true]")


def fluchhuette(m, rng):
    """Kleine, schiefe Hütte des Fluchhändlers mit Kessel und Braustand."""
    cx, cz = FLUCH
    x1, z1, x2, z2 = cx - 2, cz - 2, cx + 2, cz + 2
    for x in range(x1, x2 + 1):
        for z in range(z1, z2 + 1):
            m.frei.add((x, z))
            m.set(x, F, z, "spruce_planks")
            rand = x in (x1, x2) or z in (z1, z2)
            if not rand:
                continue
            ecke = x in (x1, x2) and z in (z1, z2)
            for y in range(F + 1, F + 4):
                if ecke:
                    blk = "dark_oak_log[axis=y]"
                elif y == F + 1:
                    blk = "mossy_cobblestone"
                elif y == F + 2 and (x == cx or z == cz):
                    blk = "purple_stained_glass"
                else:
                    blk = "dark_oak_planks"
                m.set(x, y, z, blk)
    m.set(x2, F + 1, cz, "air")
    m.set(x2, F + 2, cz, "air")
    dachstufen(m, x1 - 1, z1 - 1, x2 + 1, z2 + 1, F + 4, 3, "dark_oak_stairs", "dark_oak_planks",
               "dark_oak_slab[type=bottom]")
    m.set(cx - 1, F + 1, cz - 1, "water_cauldron[level=3]")
    m.set(cx - 1, F + 1, cz + 1, "brewing_stand")
    m.set(cx + 1, F + 1, cz - 1, "purple_candle[candles=3,lit=true]")
    m.set(cx, F + 3, cz, "soul_lantern[hanging=true]")


def weg(m, punkte, breite=1):
    """Trampelpfad aus Wegblöcken entlang einer Punktfolge."""
    for (ax, az), (bx, bz) in zip(punkte, punkte[1:]):
        n = int(max(abs(bx - ax), abs(bz - az))) * 2 + 1
        for i in range(n + 1):
            t = i / n
            px, pz = ax + (bx - ax) * t, az + (bz - az) * t
            for ox in range(-breite, breite + 1):
                for oz in range(-breite, breite + 1):
                    if math.hypot(ox, oz) > breite + 0.25:
                        continue
                    x, z = round(px + ox), round(pz + oz)
                    m.frei.add((x, z))
                    if m.get(x, F, z) == "grass_block":
                        m.set(x, F, z, "dirt_path")


def sprungbrett(m):
    """Plattform mit Torbogen und einem Sprungbrett weit über den Inselrand hinaus."""
    for x in range(-2, 3):
        for z in range(27, 32):
            m.frei.add((x, z))
            m.set(x, F, z, "spruce_planks")
            m.set(x, F - 1, z, "spruce_planks" if m.get(x, F - 1, z) is None else m.get(x, F - 1, z))
    for z in range(27, 31):
        for x in (-2, 2):
            m.set(x, F + 1, z, "spruce_fence")
    for x in (-2, 2):
        m.box(x, F + 1, 31, x, F + 3, 31, "stripped_spruce_log[axis=y]")
    m.box(-2, F + 4, 31, 2, F + 4, 31, "stripped_spruce_log[axis=x]")
    for x in (-1, 1):
        m.set(x, F + 3, 31, "lantern[hanging=true]")
    for z in range(BRETT[0], BRETT[1] + 1):
        m.frei.add((0, z))
        m.set(0, F, z, "spruce_slab[type=top]")


def aussichtspunkt(m):
    """Holzbalkon am Westrand, der über den Abgrund ragt."""
    for x in range(-34, -25):
        for z in range(-3, 4):
            m.frei.add((x, z))
            m.set(x, F, z, "spruce_planks")
    for x in range(-34, -25):
        for z in (-2, 2):
            if m.get(x, F - 1, z) is None:
                m.set(x, F - 1, z, "spruce_log[axis=x]")
    for z in range(-3, 4):
        m.set(-34, F + 1, z, "spruce_fence")
    for x in range(-33, -27):
        for z in (-3, 3):
            m.set(x, F + 1, z, "spruce_fence")
    for z in (-3, 3):
        m.set(-34, F + 1, z, "spruce_fence")
        m.set(-34, F + 2, z, "spruce_fence")
        m.set(-34, F + 3, z, "lantern[hanging=false]")


def kirschbaum(m, x0, y0, z0, rng, hoehe=5, krone=3.6):
    """Kirschbaum; y0 ist der Grasblock unter dem Stamm."""
    for i in range(1, hoehe + 1):
        m.set(x0, y0 + i, z0, "cherry_log[axis=y]")
    ast = rng.choice([(1, 0, "x"), (-1, 0, "x"), (0, 1, "z"), (0, -1, "z")])
    m.set(x0 + ast[0], y0 + hoehe - 1, z0 + ast[1], f"cherry_log[axis={ast[2]}]")
    m.set(x0 + 2 * ast[0], y0 + hoehe, z0 + 2 * ast[1], "cherry_log[axis=y]")
    ky = y0 + hoehe + 1
    kx, kz = x0 + ast[0], z0 + ast[1]
    ri = int(krone) + 2
    for dx in range(-ri, ri + 1):
        for dy in range(-3, 4):
            for dz in range(-ri, ri + 1):
                e = (dx / krone) ** 2 + (dy / 2.2) ** 2 + (dz / krone) ** 2
                e += (rng.random() - 0.5) * 0.35
                if e <= 1.0 and m.get(kx + dx, ky + dy, kz + dz) is None:
                    m.set(kx + dx, ky + dy, kz + dz, "cherry_leaves[persistent=true]")
    # Blütenvorhänge am Kronenrand
    for dx in range(-ri, ri + 1):
        for dz in range(-ri, ri + 1):
            if rng.random() > 0.18:
                continue
            for dy in range(-3, 1):
                y = ky + dy
                if m.get(kx + dx, y, kz + dz) == "cherry_leaves[persistent=true]" and \
                        m.get(kx + dx, y - 1, kz + dz) is None:
                    for i in range(1, rng.randint(1, 2) + 1):
                        if m.get(kx + dx, y - i, kz + dz) is None and y - i > y0 + 2:
                            m.set(kx + dx, y - i, kz + dz, "cherry_leaves[persistent=true]")
                    break
    for dx in range(-1, 2):
        for dz in range(-1, 2):
            m.frei.add((x0 + dx, z0 + dz))


def busch(m, x0, y0, z0, rng):
    for dx in range(-2, 3):
        for dy in range(0, 3):
            for dz in range(-2, 3):
                e = (dx / 1.6) ** 2 + (dy / 1.5) ** 2 + (dz / 1.6) ** 2 + (rng.random() - 0.5) * 0.4
                if e <= 1.0 and m.get(x0 + dx, y0 + 1 + dy, z0 + dz) is None \
                        and m.get(x0 + dx, y0 + dy, z0 + dz) is not None:
                    blatt = "flowering_azalea_leaves" if rng.random() < 0.55 else "azalea_leaves"
                    m.set(x0 + dx, y0 + 1 + dy, z0 + dz, f"{blatt}[persistent=true]")


BLUMEN = ["poppy", "dandelion", "cornflower", "allium", "azure_bluet", "oxeye_daisy",
          "lily_of_the_valley"]


def bepflanzen(m, rng):
    """Gras und Blumen auf allem freien Gras."""
    for (x, y, z), blk in sorted(m.b.items()):
        if blk != "grass_block" or (x, z) in m.frei or m.get(x, y + 1, z) is not None:
            continue
        r = rng.random()
        richtung = rng.choice(["north", "south", "east", "west"])
        if r < 0.30:
            m.set(x, y + 1, z, "short_grass")
        elif r < 0.34 and m.get(x, y + 2, z) is None:
            m.set(x, y + 1, z, "tall_grass[half=lower]")
            m.set(x, y + 2, z, "tall_grass[half=upper]")
        elif r < 0.37:
            m.set(x, y + 1, z, "fern")
        elif r < 0.43:
            m.set(x, y + 1, z, rng.choice(BLUMEN))
        elif r < 0.47:
            m.set(x, y + 1, z, f"pink_petals[facing={richtung},flower_amount={rng.randint(1, 4)}]")
        elif r < 0.49:
            m.set(x, y + 1, z, f"wildflowers[facing={richtung},flower_amount={rng.randint(1, 4)}]")


# ---------------------------------------------------------------- Zäune & Licht

ZAUN_FREI = ("_slab", "_stairs", "glass", "leaves", "lantern", "candle", "carpet", "water",
             "light", "beacon", "anvil", "grindstone", "enchanting_table", "ender_chest",
             "stonecutter", "cauldron", "brewing_stand", "dirt_path", "lightning_rod", "dripstone",
             "amethyst_cluster", "glow_lichen", "hanging_roots", "vine", "short_grass", "tall_grass",
             "fern", "petals", "wildflowers", "end_gateway", "_fence", "lectern") + tuple(BLUMEN)


def ist_voll(blk):
    """Voller, undurchsichtiger Block (darauf können Monster stehen, daran hängt ein Zaun)."""
    if blk is None:
        return False
    name = blk.split("[")[0]
    if name in ("pointed_dripstone", "cave_vines", "cave_vines_plant"):
        return False
    return not any(t in name for t in ZAUN_FREI)


def zaeune_verbinden(m):
    for (x, y, z), blk in list(m.b.items()):
        name = blk.split("[")[0]
        if not name.endswith("_fence"):
            continue
        an = []
        for dx, dz, seite in [(0, -1, "north"), (1, 0, "east"), (0, 1, "south"), (-1, 0, "west")]:
            n = m.get(x + dx, y, z + dz)
            if n is not None and (n.split("[")[0].endswith("_fence") or ist_voll(n)):
                an.append(f"{seite}=true")
        m.set(x, y, z, f"{name}[{','.join(an)}]" if an else name)


LEUCHTKRAFT = {"lantern": 15, "soul_lantern": 10, "beacon": 15, "end_gateway": 15,
               "crying_obsidian": 10, "glow_lichen": 7, "amethyst_cluster": 5,
               "enchanting_table": 7, "ender_chest": 7, "brewing_stand": 1, "sea_lantern": 15}


def leuchtkraft(blk):
    name = blk.split("[")[0]
    if name.endswith("candle") and "lit=true" in blk:
        n = int(blk.split("candles=")[1][0])
        return 3 * n
    if name in ("cave_vines", "cave_vines_plant") and "berries=true" in blk:
        return 14
    if name == "light":
        return int(blk.split("level=")[1].rstrip("]"))
    return LEUCHTKRAFT.get(name, 0)


def lichtdurchlaessig(blk):
    if blk is None:
        return True
    name = blk.split("[")[0]
    if "_slab" in name or "_stairs" in name or name == "dirt_path":
        return False
    return not ist_voll(blk)


def begehbar(blk):
    """Zelle, in der ein Monster stehen könnte."""
    if blk is None:
        return True
    name = blk.split("[")[0]
    return name in ("short_grass", "fern", "tall_grass", "pink_petals", "wildflowers") or \
        name.endswith("_carpet") or name in BLUMEN


def ausleuchten(m, stufe=12):
    """Setzt unsichtbare Lichtblöcke überall dorthin, wo nachts Monster spawnen könnten."""
    licht = {}

    def ausbreiten(start):
        offen = list(start)
        while offen:
            neu = []
            for (p, lv) in offen:
                if licht.get(p, 0) >= lv:
                    continue
                licht[p] = lv
                if lv <= 1:
                    continue
                x, y, z = p
                for d in [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]:
                    q = (x + d[0], y + d[1], z + d[2])
                    b = m.b.get(q)
                    if not lichtdurchlaessig(b):
                        continue
                    kosten = 1 + (1 if b is not None and ("leaves" in b or b == "water") else 0)
                    if lv - kosten > licht.get(q, 0):
                        neu.append((q, lv - kosten))
            offen = neu

    quellen = [(p, leuchtkraft(b)) for p, b in m.b.items() if leuchtkraft(b) > 0]
    ausbreiten(quellen)
    stellen = []
    for (x, y, z), blk in m.b.items():
        if not ist_voll(blk):
            continue
        p = (x, y + 1, z)
        if begehbar(m.b.get(p)) and licht.get(p, 0) == 0:
            stellen.append(p)
    gesetzt = 0
    for p in sorted(stellen, key=lambda q: (q[1], q[0], q[2])):
        if licht.get(p, 0) > 0:
            continue
        ziel = p if m.b.get(p) is None else (p[0], p[1] + 1, p[2])
        if m.b.get(ziel) is not None:
            continue
        m.set(*ziel, f"light[level={stufe}]")
        ausbreiten([(ziel, stufe)])
        gesetzt += 1
    return gesetzt


# ---------------------------------------------------------------- Gesamtmodelle

def himmelsinsel():
    rng = random.Random(1904)
    m = Modell()
    insel(m, 0, 0, F, 31, 34, seed=11, amp=2.2)
    insel(m, -40, -22, F + 6, 5.2, 13, seed=23, amp=0.8)
    insel(m, 40, 25, F + 2, 4.3, 11, seed=37, amp=0.6)
    platz(m, rng)
    bibliothek(m, rng)
    werkstatt(m, rng)
    fluchhuette(m, rng)
    sprungbrett(m)
    aussichtspunkt(m)
    weg(m, [(0, 7), (0, 27)], 1)
    weg(m, [(7, 0), (13, 0)], 1)
    weg(m, [(-7, 0), (-26, 0)], 1)
    weg(m, [(-5, 5), (-10, 11), (-14, 17)], 0)
    weg(m, [(0, -7), (0, -10)], 1)
    for x, z in [(-2, 13), (2, 20), (-2, 25), (10, 2), (-12, 2), (-19, -2), (-25, 2), (-10, 13)]:
        laternenpfahl(m, x, F, z)
    for x, z, h, k in [(-15, -9, 5, 3.6), (-22, 10, 5, 3.4), (15, -15, 6, 3.8), (13, 16, 5, 3.4)]:
        kirschbaum(m, x, F, z, rng, h, k)
    kirschbaum(m, -40, F + 6, -22, rng, 4, 2.6)
    for x, z in [(-11, -13), (-24, -12), (24, -14), (22, 12), (-6, 24), (8, 24), (26, -4), (-4, -28)]:
        busch(m, x, F, z, rng)
    busch(m, 40, F + 2, 25, rng)
    bepflanzen(m, rng)
    zaeune_verbinden(m)
    lichter = ausleuchten(m)
    return m, lichter


def bodenstation():
    """Landeplatz unter dem Sprungbrett. Koordinaten relativ: (0, 0, 0) = erste Luft über dem Boden."""
    rng = random.Random(77)
    m = Modell()
    for x in range(-5, 6):
        for z in range(-5, 6):
            r = math.hypot(x, z)
            if r > 5.2:
                continue
            if r <= 1.0:
                blk = "chiseled_stone_bricks"
            elif 1.5 <= r <= 2.5:
                blk = "polished_deepslate"
            elif r > 4.3:
                blk = "polished_andesite"
            else:
                blk = "mossy_stone_bricks" if rng.random() < 0.25 else "stone_bricks"
            m.set(x, -1, z, blk)
    # Himmelstor: Rahmen aus weinendem Obsidian, offen nach Süden (zur Landefläche)
    for y in range(0, 3):
        m.set(-1, y, -4, "crying_obsidian")
        m.set(1, y, -4, "crying_obsidian")
        m.set(0, y, -5, "crying_obsidian")
    m.set(0, 2, -4, "crying_obsidian")
    m.set(-1, 3, -4, "amethyst_block")
    m.set(0, 3, -4, "amethyst_block")
    m.set(1, 3, -4, "amethyst_block")
    for x, z in [(4, 1), (-4, 1), (3, -3), (-3, -3)]:
        laternenpfahl(m, x, -1, z)
    zaeune_verbinden(m)
    return m


TOR = [(0, 0, -4), (0, 1, -4)]   # relative Positionen der Endtransitportal-Blöcke
