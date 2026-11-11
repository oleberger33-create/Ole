"""Die Händler der Zauberbibliothek: Stand, Aussehen und Bücher mit Preisen.

Preise in Smaragden (immer plus ein normales Buch):
  normale Verzauberung   4 + 6 × Stufe   (Stufe I = 10 … Stufe V = 34)
  Schatz-Verzauberung    dasselbe + 6    (Eisläufer, Seelenläufer, Huschen, Windstoß)
  Reparatur              20
  Flüche                 1
"""

SCHATZ = {"frost_walker", "soul_speed", "swift_sneak", "wind_burst"}
FLUECHE = {"binding_curse", "vanishing_curse"}
NUR_NEU = {"lunge"}  # gibt es erst ab Minecraft 1.21.11


def preis(ench, stufe):
    if ench in FLUECHE:
        return 1
    if ench == "mending":
        return 20
    return min(64, 4 + 6 * stufe + (6 if ench in SCHATZ else 0))


# platz: Winkel des Standes in der Bibliothek (0 = Eingang im Süden, 90 = Osten,
# 180 = Norden), "mitte" = Podest in der Mitte, "fluch" = Hütte im Südwesten.
HAENDLER = [
    dict(id="meister", platz="mitte", name="Meister-Bibliothekar", farbe="light_purple",
         beruf="librarian", typ="plains", teppich="purple",
         untertitel="Die Bestseller",
         buecher=[("mending", 1), ("unbreaking", 3), ("efficiency", 5), ("fortune", 3),
                  ("silk_touch", 1), ("sharpness", 5), ("protection", 4),
                  ("feather_falling", 4), ("looting", 3), ("power", 5), ("infinity", 1)]),
    dict(id="werkzeuge", platz=180, name="Werkzeuge", farbe="yellow",
         beruf="toolsmith", typ="desert", teppich="yellow",
         untertitel="Spitzhacke, Axt, Schaufel, Hacke",
         buecher=[("efficiency", 5), ("fortune", 3), ("silk_touch", 1),
                  ("unbreaking", 3), ("mending", 1)]),
    dict(id="schwert", platz=135, name="Schwert", farbe="red",
         beruf="weaponsmith", typ="savanna", teppich="red",
         untertitel="Für den Nahkampf",
         buecher=[("sharpness", 5), ("smite", 5), ("bane_of_arthropods", 5),
                  ("fire_aspect", 2), ("looting", 3), ("knockback", 2), ("sweeping_edge", 3)]),
    dict(id="ruestung", platz=225, name="Rüstung", farbe="aqua",
         beruf="armorer", typ="taiga", teppich="light_blue",
         untertitel="Helm, Brust, Hose, Stiefel",
         buecher=[("protection", 4), ("fire_protection", 4), ("blast_protection", 4),
                  ("projectile_protection", 4), ("thorns", 3)]),
    dict(id="fernkampf", platz=90, name="Bogen & Armbrust", farbe="gold",
         beruf="fletcher", typ="jungle", teppich="orange",
         untertitel="Für Fernkämpfer",
         buecher=[("power", 5), ("punch", 2), ("flame", 1), ("infinity", 1),
                  ("multishot", 1), ("piercing", 4), ("quick_charge", 3)]),
    dict(id="kopf_fuss", platz=270, name="Helm & Stiefel", farbe="green",
         beruf="leatherworker", typ="snow", teppich="lime",
         untertitel="Tauchen, Fallen, Laufen",
         buecher=[("respiration", 3), ("aqua_affinity", 1), ("feather_falling", 4),
                  ("depth_strider", 3), ("frost_walker", 2), ("soul_speed", 3),
                  ("swift_sneak", 3)]),
    dict(id="wasser", platz=45, name="Dreizack & Angel", farbe="dark_aqua",
         beruf="fisherman", typ="swamp", teppich="cyan",
         untertitel="Für das Meer",
         buecher=[("impaling", 5), ("loyalty", 3), ("riptide", 3), ("channeling", 1),
                  ("luck_of_the_sea", 3), ("lure", 3)]),
    dict(id="streitkolben", platz=315, name="Streitkolben & Speer", farbe="dark_green",
         beruf="mason", typ="plains", teppich="green",
         untertitel="Die neuen Waffen",
         buecher=[("density", 5), ("breach", 4), ("wind_burst", 3), ("lunge", 3)]),
    dict(id="fluch", platz="fluch", name="Fluchhändler", farbe="dark_purple",
         beruf="cleric", typ="swamp", teppich=None,
         untertitel="Nur für Scherzkekse",
         buecher=[("binding_curse", 1), ("vanishing_curse", 1)]),
]

ROEMISCH = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V"}


# Händler auf der Marktinsel: Sie kaufen Waren und zahlen in Smaragden.
# x, z = Standplatz des Händlers, blick = Richtung zum Marktplatz,
# waren = (Gegenstand, Anzahl, Smaragde).
ANKAUF = [
    dict(id="bauer", name="Bauer & Fischer", farbe="green", beruf="farmer", typ="plains",
         x=34, z=-35, blick="south", wolle=("lime", "white"), theke="composter", deko="hay_block[axis=y]",
         waren=[("wheat", 20, 1), ("carrot", 22, 1), ("potato", 26, 1), ("beetroot", 15, 1),
                ("pumpkin", 6, 1), ("melon", 4, 1), ("sugar_cane", 24, 1), ("sweet_berries", 24, 1),
                ("cod", 12, 1), ("salmon", 8, 1)]),
    dict(id="bergmann", name="Bergmann", farbe="gold", beruf="toolsmith", typ="desert",
         x=40, z=-35, blick="south", wolle=("orange", "white"), theke="smithing_table",
         deko="blast_furnace[facing=south]",
         waren=[("coal", 15, 1), ("copper_ingot", 12, 1), ("iron_ingot", 4, 1), ("gold_ingot", 3, 1),
                ("redstone", 24, 1), ("lapis_lazuli", 12, 1), ("quartz", 12, 1),
                ("amethyst_shard", 12, 1), ("diamond", 1, 2)]),
    dict(id="jaeger", name="Monsterjäger", farbe="red", beruf="cleric", typ="swamp",
         x=31, z=-29, blick="east", wolle=("red", "black"), theke="barrel[facing=up]",
         deko="target",
         waren=[("rotten_flesh", 32, 1), ("bone", 16, 1), ("string", 16, 1), ("gunpowder", 8, 1),
                ("spider_eye", 10, 1), ("slime_ball", 8, 1), ("ender_pearl", 3, 1), ("blaze_rod", 4, 1),
                ("phantom_membrane", 4, 1), ("ghast_tear", 1, 1)]),
    dict(id="holz", name="Holzfäller", farbe="#C08040", beruf="fletcher", typ="taiga",
         x=43, z=-29, blick="west", wolle=("brown", "white"), theke="fletching_table",
         deko="oak_log[axis=y]",
         waren=[("oak_log", 32, 1), ("spruce_log", 32, 1), ("birch_log", 32, 1), ("jungle_log", 32, 1),
                ("acacia_log", 32, 1), ("dark_oak_log", 32, 1), ("mangrove_log", 32, 1),
                ("cherry_log", 32, 1), ("pale_oak_log", 32, 1), ("crimson_stem", 32, 1),
                ("warped_stem", 32, 1)]),
]
BLICK = {"south": (0, 1, 0), "north": (0, -1, 180), "east": (1, 0, -90), "west": (-1, 0, 90)}
