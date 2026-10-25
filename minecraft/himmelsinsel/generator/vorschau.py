"""Zeichnet eine isometrische Vorschau der Himmelsinsel (Blick von Südosten).

Aufruf:  python3 vorschau.py [datei.png] [richtung]
richtung: so (Südosten, Standard), sw, nw, no
"""
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

import bauplan

FARBEN = {
    "grass_block": (98, 160, 58), "dirt": (134, 96, 67), "rooted_dirt": (144, 106, 76),
    "dirt_path": (160, 132, 76), "stone": (125, 125, 125), "andesite": (136, 136, 137),
    "tuff": (108, 109, 102), "cobblestone": (112, 112, 112), "mossy_cobblestone": (96, 116, 82),
    "deepslate": (80, 80, 84), "dripstone_block": (134, 107, 92), "amethyst_block": (133, 97, 191),
    "polished_deepslate": (72, 72, 76), "deepslate_bricks": (70, 70, 74),
    "cracked_deepslate_bricks": (66, 66, 70), "chiseled_deepslate": (60, 60, 64),
    "deepslate_tiles": (52, 52, 58), "deepslate_tile_stairs": (52, 52, 58),
    "polished_deepslate_slab": (72, 72, 76), "polished_deepslate_stairs": (72, 72, 76),
    "stone_bricks": (122, 121, 122), "mossy_stone_bricks": (104, 118, 90),
    "cracked_stone_bricks": (116, 114, 114), "chiseled_stone_bricks": (130, 128, 130),
    "polished_andesite": (140, 144, 142), "dark_oak_planks": (70, 45, 22),
    "dark_oak_log": (60, 46, 26), "stripped_dark_oak_log": (96, 74, 50),
    "spruce_planks": (115, 85, 49), "spruce_slab": (115, 85, 49), "spruce_stairs": (115, 85, 49),
    "stripped_spruce_log": (138, 106, 62), "spruce_log": (70, 50, 28), "spruce_fence": (115, 85, 49),
    "dark_oak_fence": (70, 45, 22), "dark_oak_stairs": (70, 45, 22), "dark_oak_slab": (70, 45, 22),
    "cherry_log": (60, 34, 48), "cherry_leaves": (236, 176, 200),
    "azalea_leaves": (92, 126, 44), "flowering_azalea_leaves": (120, 128, 70),
    "water": (60, 110, 220), "emerald_block": (42, 203, 88), "dark_prismarine": (51, 91, 75),
    "beacon": (130, 230, 225), "purple_stained_glass": (150, 80, 210), "bookshelf": (117, 94, 59),
    "lantern": (250, 200, 100), "soul_lantern": (120, 220, 230), "lightning_rod": (200, 120, 80),
    "anvil": (68, 68, 68), "grindstone": (140, 140, 140), "smithing_table": (60, 50, 50),
    "crafting_table": (140, 100, 60), "ender_chest": (40, 60, 60), "stonecutter": (120, 120, 120),
    "enchanting_table": (160, 40, 50), "water_cauldron": (70, 70, 80), "brewing_stand": (130, 120, 90),
    "crying_obsidian": (40, 20, 70), "glow_lichen": (130, 160, 130), "hanging_roots": (160, 110, 90),
    "pointed_dripstone": (134, 107, 92), "amethyst_cluster": (180, 140, 230),
    "cave_vines": (80, 110, 40), "cave_vines_plant": (80, 110, 40), "vine": (60, 100, 30),
    "short_grass": (90, 150, 50), "tall_grass": (90, 150, 50), "fern": (80, 130, 50),
    "pink_petals": (240, 170, 200), "wildflowers": (240, 220, 90), "poppy": (220, 40, 40),
    "dandelion": (250, 230, 60), "cornflower": (80, 110, 230), "allium": (190, 120, 230),
    "azure_bluet": (230, 230, 240), "oxeye_daisy": (240, 240, 220), "lily_of_the_valley": (250, 250, 250),
    "barrel": (130, 95, 55), "hay_block": (200, 170, 40), "composter": (110, 80, 45), "bell": (240, 200, 60),
    "blast_furnace": (90, 90, 95), "target": (220, 200, 180), "fletching_table": (190, 170, 120),
    "oak_log": (110, 85, 50),
}
WOLLE = {"lime": (120, 200, 40), "white": (235, 235, 235), "orange": (230, 120, 30), "red": (170, 40, 40),
         "black": (30, 30, 35), "brown": (115, 75, 45)}
PFLANZEN = {"short_grass", "tall_grass", "fern", "pink_petals", "wildflowers", "poppy", "dandelion",
            "cornflower", "allium", "azure_bluet", "oxeye_daisy", "lily_of_the_valley", "vine",
            "glow_lichen", "hanging_roots", "cave_vines", "cave_vines_plant", "lantern", "soul_lantern",
            "candle", "purple_candle", "white_candle", "amethyst_cluster", "pointed_dripstone",
            "lightning_rod", "spruce_fence", "dark_oak_fence"}


def farbe(blk):
    name = blk.split("[")[0]
    if name.endswith("_carpet"):
        return {"purple": (120, 50, 170), "yellow": (240, 200, 50), "red": (170, 40, 40),
                "light_blue": (90, 160, 220), "orange": (230, 120, 30), "lime": (120, 200, 40),
                "cyan": (30, 140, 150), "green": (80, 110, 30)}.get(name[:-7], (200, 200, 200))
    if name.endswith("_wool"):
        return WOLLE.get(name[:-5], (200, 200, 200))
    if name.endswith("candle"):
        return (255, 220, 140)
    return FARBEN.get(name, (200, 0, 200))


def drehen(p, richtung):
    x, y, z = p
    return {"so": (x, y, z), "sw": (-z, y, x), "nw": (-x, y, -z), "no": (z, y, -x)}[richtung]


def zeichnen(modell, pfad, richtung="so", a=7, b=3.5, c=8.2, schilder=(), strahl=None, titel=None, rand=40):
    bloecke = {}
    for p, blk in modell.b.items():
        name = blk.split("[")[0]
        if name == "light":
            continue
        bloecke[drehen(p, richtung)] = blk
    xs = [p[0] - p[2] for p in bloecke]
    ys = [(p[0] + p[2]) * b - p[1] * c for p in bloecke]
    ox, oy = -min(xs) * a + rand, -min(ys) + 80
    w = int((max(xs) - min(xs)) * a + 2 * rand)
    h = int(max(ys) - min(ys) + 160)
    bild = Image.new("RGB", (w, h), (150, 190, 240))
    hg = ImageDraw.Draw(bild)
    for i in range(h):  # Himmelsverlauf
        t = i / h
        hg.line([(0, i), (w, i)], fill=(int(120 + 80 * t), int(170 + 60 * t), int(235 + 15 * t)))
    d = ImageDraw.Draw(bild, "RGBA")

    def P(x, y, z):
        return (ox + (x - z) * a, oy + (x + z) * b - y * c)

    def undurchsichtig(q):
        blk = bloecke.get(q)
        return blk is not None and blk.split("[")[0] not in PFLANZEN and blk.split("[")[0] != "water"

    for (x, y, z) in sorted(bloecke, key=lambda q: (q[0] + q[1] + q[2], q[1])):
        blk = bloecke[(x, y, z)]
        name = blk.split("[")[0]
        r, g, bl = farbe(blk)
        if name in PFLANZEN:
            cx, cy = P(x + 0.5, y + 0.4, z + 0.5)
            s = 2.2 if "lantern" not in name else 2.8
            d.ellipse([cx - s, cy - s, cx + s, cy + s], fill=(r, g, bl, 255))
            continue
        alpha = 170 if name in ("water", "purple_stained_glass", "beacon") else 255
        if not undurchsichtig((x, y + 1, z)):
            d.polygon([P(x, y + 1, z), P(x + 1, y + 1, z), P(x + 1, y + 1, z + 1), P(x, y + 1, z + 1)],
                      fill=(r, g, bl, alpha))
        if name == "water":
            continue
        if not undurchsichtig((x + 1, y, z)):
            k = 0.78
            d.polygon([P(x + 1, y + 1, z), P(x + 1, y + 1, z + 1), P(x + 1, y, z + 1), P(x + 1, y, z)],
                      fill=(int(r * k), int(g * k), int(bl * k), alpha))
        if not undurchsichtig((x, y, z + 1)):
            k = 0.62
            d.polygon([P(x, y + 1, z + 1), P(x + 1, y + 1, z + 1), P(x + 1, y, z + 1), P(x, y, z + 1)],
                      fill=(int(r * k), int(g * k), int(bl * k), alpha))
    bild = bild.filter(ImageFilter.SMOOTH_MORE)
    d = ImageDraw.Draw(bild, "RGBA")
    if strahl:  # Leuchtfeuer-Strahl
        x, y, z = drehen(strahl, richtung)
        fx, fy = P(x + 0.5, y + 1, z + 0.5)
        for breite, alpha in [(a * 0.9, 50), (a * 0.45, 110), (a * 0.18, 200)]:
            d.rectangle([fx - breite, 0, fx + breite, fy], fill=(205, 170, 255, alpha))
    schrift = ImageFont.truetype("DejaVuSans-Bold.ttf", int(a * 1.9))
    for text, pos, (vx, vy) in schilder:
        x, y, z = drehen(pos, richtung)
        px, py = P(x + 0.5, y, z + 0.5)
        tx, ty = px + vx * a, py + vy * a
        d.line([(px, py), (tx, ty)], fill=(30, 20, 50, 230), width=max(2, a // 4))
        d.ellipse([px - 4, py - 4, px + 4, py + 4], fill=(30, 20, 50, 240))
        l, t, r_, bo = d.textbbox((0, 0), text, font=schrift)
        w_, h_ = r_ - l, bo - t
        kx, ky = tx - w_ / 2, ty - h_ / 2
        d.rounded_rectangle([kx - 10, ky - 7, kx + w_ + 10, ky + h_ + 9], radius=8, fill=(30, 20, 50, 225))
        d.text((kx - l, ky - t), text, font=schrift, fill=(255, 240, 255))
    if titel:
        gross = ImageFont.truetype("DejaVuSans-Bold.ttf", int(a * 3.6))
        klein = ImageFont.truetype("DejaVuSans.ttf", int(a * 1.8))
        d.text((a * 4, a * 3), titel[0], font=gross, fill=(40, 25, 70))
        d.text((a * 4, a * 3 + a * 4.6), titel[1], font=klein, fill=(55, 45, 90))
    bild.save(pfad)
    return bild.size


if __name__ == "__main__":
    ziel = sys.argv[1] if len(sys.argv) > 1 else "vorschau.png"
    richtung = sys.argv[2] if len(sys.argv) > 2 else "so"
    m, _ = bauplan.himmelsinsel()
    F = bauplan.F
    schilder = [
        ("Zauberbibliothek – alle Bücher", (0, F + 12, -18), (12, -10)),
        ("Spawn & Leuchtfeuer-Brunnen", (0, F + 1, 4), (-21, -15)),
        ("Werkstatt", (19, F + 6, 0), (14, -3)),
        ("Absprung ins Tal", (0, F + 1, 37), (-6, 11)),
        ("Fluchhändler", (-17, F + 6, 17), (-12, 5)),
        ("Aussichtspunkt", (-31, F + 2, 0), (-7, -9)),
        ("Marktinsel – Waren gegen Smaragde", (37, F + 5, -29), (6, -12)),
    ]
    print(zeichnen(m, ziel, richtung, a=10, b=5, c=11.7, schilder=schilder, strahl=(0, F + 1, 0),
                   titel=("Himmelsinsel-Spawn", "Schwebende Spawn-Insel mit allen Verzauberungsbüchern"),
                   rand=130))
