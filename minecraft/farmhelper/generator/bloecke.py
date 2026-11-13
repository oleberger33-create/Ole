"""Übersetzt die Blöcke aus den Bauplänen des Farm-Handbuchs in echte Minecraft-Blöcke.

Jeder Eintrag sagt, wie der Geisterblock aussieht (anzeige), woran das Pack einen richtig gesetzten Block erkennt
(pruefen, Block oder Block-Tag mit Eigenschaften), welches Item der Spieler dafür braucht (item, für die Zählung im
Inventar) und wie der Block auf Deutsch heißt. Richtungen kommen aus dem Plan als n/e/s/w/u/d (f = wohin der Block
zeigt, so wie es die Bauanleitung erklärt) und werden mit dem Plan gedreht.
"""

RICHTUNG = {"n": "north", "e": "east", "s": "south", "w": "west", "u": "up", "d": "down"}
GEGEN = {"n": "s", "s": "n", "e": "w", "w": "e", "u": "d", "d": "u"}
DREHUNG = {"n": "e", "e": "s", "s": "w", "w": "n", "u": "u", "d": "d"}    # 90° im Uhrzeigersinn

# Blöcke, die von selbst entstehen oder Ertrag sind: kein Geist, keine Prüfung
VON_SELBST = {"flowing_water", "melon", "pumpkin", "snow", "spawner"}

# Lebewesen und Loren: werden hingebracht, nicht gesetzt
LEBEWESEN = {
    "villager": ("minecraft:villager", "Dorfbewohner"), "zombie": ("minecraft:zombie", "Zombie"),
    "iron_golem": ("minecraft:iron_golem", "Eisengolem"), "sheep": ("minecraft:sheep", "Schaf"),
    "cow": ("minecraft:cow", "Kuh"), "chicken": ("minecraft:chicken", "Huhn"), "bee": ("minecraft:bee", "Biene"),
    "snow_golem": ("minecraft:snow_golem", "Schneegolem"), "endermite": ("minecraft:endermite", "Endermilbe"),
    "enderman": ("minecraft:enderman", "Enderman"), "cat": ("minecraft:cat", "Katze"),
    "hopper_minecart": ("minecraft:hopper_minecart", "Trichterlore"), "minecart": ("minecraft:minecart", "Lore"),
    "oak_boat": ("minecraft:oak_boat", "Boot"),
}
AFK = "player"                                   # „Hier stehen“: nur ein Schild, keine Prüfung

# id im Plan: (Anzeige-Block, Prüfung, Item für die Inventar-Zählung, deutscher Name)
EINFACH = {
    "stone_bricks": ("stone_bricks", "minecraft:stone_bricks", "minecraft:stone_bricks", "Steinziegel"),
    "stone": ("stone", "minecraft:stone", "minecraft:stone", "Stein"),
    "cobblestone": ("cobblestone", "minecraft:cobblestone", "minecraft:cobblestone", "Bruchstein"),
    # Stütze: steht sonst als Erde/Stein im Boden; jeder feste Block zählt (Stein, Erde, Sand, Erz, Netherrack …)
    "fest": ("cobblestone", "#ofh:fest", "minecraft:cobblestone", "Fester Block (Stein, Erde, Bruchstein …)"),
    "smooth_stone": ("smooth_stone", "minecraft:smooth_stone", "minecraft:smooth_stone", "Glatter Stein"),
    "dirt": ("dirt", "#ofh:boden", "#minecraft:dirt", "Erde"),
    "grass_block": ("grass_block", "#ofh:boden", "#minecraft:dirt", "Grasblock (oder Erde)"),
    "farmland": ("farmland", "minecraft:farmland", "#minecraft:dirt", "Ackerboden (Erde + Hacke)"),
    "mud": ("mud", "minecraft:mud", "minecraft:mud", "Schlamm (Wasserflasche auf Erde)"),
    "sand": ("sand", "#minecraft:sand", "#minecraft:sand", "Sand"),
    "soul_sand": ("soul_sand", "minecraft:soul_sand", "minecraft:soul_sand", "Seelensand"),
    "netherrack": ("netherrack", "minecraft:netherrack", "minecraft:netherrack", "Netherrack"),
    "nether_bricks": ("nether_bricks", "minecraft:nether_bricks", "minecraft:nether_bricks", "Netherziegel"),
    "end_stone": ("end_stone", "minecraft:end_stone", "minecraft:end_stone", "Endstein"),
    "obsidian": ("obsidian", "minecraft:obsidian", "minecraft:obsidian", "Obsidian"),
    "magma": ("magma_block", "minecraft:magma_block", "minecraft:magma_block", "Magmablock"),
    "glowstone": ("glowstone", "minecraft:glowstone", "minecraft:glowstone", "Leuchtstein"),
    "sea_lantern": ("sea_lantern", "minecraft:sea_lantern", "minecraft:sea_lantern", "Seelaterne"),
    "oak_planks": ("oak_planks", "#minecraft:planks", "#minecraft:planks", "Bretter"),
    "hay_block": ("hay_block", "minecraft:hay_block", "minecraft:hay_block", "Strohballen"),
    "white_wool": ("white_wool", "#minecraft:wool", "#minecraft:wool", "Wolle"),
    "glass": ("glass", "#minecraft:impermeable", "minecraft:glass", "Glas"),
    "composter": ("composter", "minecraft:composter", "minecraft:composter", "Komposter"),
    "cauldron": ("cauldron", "#minecraft:cauldrons", "minecraft:cauldron", "Kessel"),
    "lava_cauldron": ("lava_cauldron", "minecraft:lava_cauldron", "minecraft:cauldron", "Kessel mit Lava (Kessel + Lavaeimer)"),
    "stonecutter": ("stonecutter", "minecraft:stonecutter", "minecraft:stonecutter", "Steinschneider"),
    "daylight_detector": ("daylight_detector", "minecraft:daylight_detector", "minecraft:daylight_detector",
                          "Tageslichtsensor"),
    "daylight_detector_inv": ("daylight_detector", "minecraft:daylight_detector[inverted=true]",
                              "minecraft:daylight_detector", "Tageslichtsensor (einmal anklicken: Nacht-Modus)"),
    "fletching_table": ("fletching_table", "minecraft:fletching_table", "minecraft:fletching_table", "Bognertisch"),
    "chest": ("chest", "#ofh:truhe", "minecraft:chest", "Truhe"),
    "cactus": ("cactus", "minecraft:cactus", "minecraft:cactus", "Kaktus"),
    "bamboo": ("bamboo", "#ofh:bambus", "minecraft:bamboo", "Bambus"),
    "scaffolding": ("scaffolding", "minecraft:scaffolding", "minecraft:scaffolding", "Gerüst"),
    "oak_fence": ("oak_fence", "#minecraft:wooden_fences", "#minecraft:wooden_fences", "Holzzaun"),
    "fence_gate": ("oak_fence_gate", "#minecraft:fence_gates", "#minecraft:fence_gates", "Zauntor"),
    "cobblestone_wall": ("cobblestone_wall", "#minecraft:walls", "#minecraft:walls", "Mauer"),
    "sign": ("oak_sign", "#minecraft:standing_signs", "#minecraft:signs", "Schild"),
    "redstone": ("redstone_wire", "minecraft:redstone_wire", "minecraft:redstone", "Redstone-Staub"),
    "lever": ("lever", "minecraft:lever", "minecraft:lever", "Hebel"),
    "stone_button": ("stone_button", "#minecraft:buttons", "#minecraft:buttons", "Knopf"),
    "campfire": ("campfire", "#minecraft:campfires", "minecraft:campfire", "Lagerfeuer"),
    "white_bed": ("white_bed", "#minecraft:beds", "#minecraft:beds", "Bett"),
    "red_bed": ("red_bed", "#minecraft:beds", "#minecraft:beds", "Bett"),
    "carpet": ("white_carpet", "#minecraft:wool_carpets", "#minecraft:wool_carpets", "Teppich"),
    "turtle_egg": ("turtle_egg", "minecraft:turtle_egg", "minecraft:turtle_egg", "Schildkrötenei"),
    "sugar_cane": ("sugar_cane", "minecraft:sugar_cane", "minecraft:sugar_cane", "Zuckerrohr"),
    "kelp": ("kelp", "#ofh:seetang", "minecraft:kelp", "Seetang"),
    "wheat": ("wheat", "minecraft:wheat", "minecraft:wheat_seeds", "Weizen (Samen)"),
    "feldfrucht": ("carrots", "minecraft:carrots|minecraft:potatoes|minecraft:wheat|minecraft:beetroots",
                   "minecraft:carrot", "Karotten oder Kartoffeln"),
    "melon_stem": ("melon_stem", "#ofh:staengel", "minecraft:melon_seeds", "Melonen-/Kürbiskerne"),
    "dark_oak_sapling": ("dark_oak_sapling", "minecraft:dark_oak_sapling", "minecraft:dark_oak_sapling",
                         "Schwarzeichensetzling"),
    "torch": ("torch", "minecraft:torch", "minecraft:torch", "Fackel"),
    "poppy": ("poppy", "#minecraft:small_flowers", "#minecraft:small_flowers", "Blume"),
    "tall_flower": ("sunflower", "minecraft:sunflower[half=lower]|minecraft:lilac[half=lower]|"
                                 "minecraft:rose_bush[half=lower]|minecraft:peony[half=lower]",
                    "minecraft:sunflower", "Hohe Blume (Sonnenblume, Flieder, Rosenstrauch, Pfingstrose)"),
    "pointed_dripstone": ("pointed_dripstone", "minecraft:pointed_dripstone[vertical_direction=down]", "minecraft:pointed_dripstone",
                          "Spitzer Tropfstein"),
    "dripstone_block": ("dripstone_block", "minecraft:dripstone_block", "minecraft:dripstone_block", "Tropfsteinblock"),
    "crafter": ("crafter", "minecraft:crafter[orientation=down_north]|minecraft:crafter[orientation=down_east]|"
                           "minecraft:crafter[orientation=down_south]|minecraft:crafter[orientation=down_west]",
                "minecraft:crafter", "Crafter (Vorderseite unten)"),
    "bee_nest": ("bee_nest", "#ofh:bienen", "minecraft:bee_nest", "Bienennest"),
    "bookshelf": ("bookshelf", "minecraft:bookshelf", "minecraft:bookshelf", "Bücherregal"),
}
# Blöcke mit Richtung: (Anzeige-Block, Prüf-Block, Item, Name, Eigenschaft, prüfen?)
GERICHTET = {
    "hopper": ("hopper", "minecraft:hopper", "minecraft:hopper", "Trichter"),
    "observer": ("observer", "minecraft:observer", "minecraft:observer", "Beobachter"),
    "piston": ("piston", "minecraft:piston", "minecraft:piston", "Kolben"),
    "sticky_piston": ("sticky_piston", "minecraft:sticky_piston", "minecraft:sticky_piston", "Klebriger Kolben"),
    "dispenser": ("dispenser", "minecraft:dispenser", "minecraft:dispenser", "Werfer"),
    "comparator": ("comparator", "minecraft:comparator", "minecraft:comparator", "Komparator"),
    "repeater": ("repeater", "minecraft:repeater", "minecraft:repeater", "Verstärker"),
    "wall_sign": ("oak_wall_sign", "#minecraft:wall_signs", "#minecraft:signs", "Schild (Wand)"),
    "ladder": ("ladder", "minecraft:ladder", "minecraft:ladder", "Leiter"),
}
FLUESSIG = {"water": ("light_blue_stained_glass", "minecraft:water[level=0]|minecraft:bubble_column", "minecraft:water_bucket", "Wasser (Eimer)"),
            "lava": ("orange_stained_glass", "minecraft:lava[level=0]", "minecraft:lava_bucket", "Lava (Eimer)")}


def drehe(f, r):
    for _ in range(r):
        f = DREHUNG[f]
    return f


def block(b, r):
    """Liefert dict(art, anzeige, anzeige_props, pruefen, item, name, schluessel) oder None (von selbst)."""
    i, p = b["id"], b.get("p", {})
    f = drehe(p["f"], r) if "f" in p else None
    if i in VON_SELBST:
        return None
    if i == AFK:
        return {"art": "afk", "name": "AFK-Platz", "schluessel": "afk"}
    if i == "luft":                                       # muss frei sein (Loch, Schacht, Raum): ausgraben
        return {"art": "block", "anzeige": "red_stained_glass", "props": {}, "pruefen": "#minecraft:replaceable",
                "item": None, "name": "Ausgraben / frei machen", "schluessel": "luft", "farbe": 0xFF9900,
                "bild": "structure_void"}
    if i == "inhalt":                                     # Behälter befüllen / einstellen: nur eine Prüfung, kein Block
        return {"art": "inhalt", "pruefen": p["pruefen"], "item": p.get("item"), "name": p["name"],
                "text": p["text"], "schluessel": "inhalt:" + p["name"]}
    if i in LEBEWESEN:
        typ, name = LEBEWESEN[i]
        return {"art": "wesen", "typ": typ, "name": name, "item": None, "schluessel": i}
    if i in FLUESSIG:
        anz, pr, item, name = FLUESSIG[i]
        return {"art": "block", "anzeige": anz, "props": {}, "pruefen": pr, "item": item, "name": name, "schluessel": i}
    if i in EINFACH:
        anz, pr, item, name = EINFACH[i]
        props = {}
        if i in ("chest", "bee_nest") and f in ("n", "e", "s", "w"):
            props = {"facing": RICHTUNG[f]}
            if i == "bee_nest":                          # Öffnung muss frei sein: Richtung mitprüfen
                pr = f"{pr}[facing={RICHTUNG[f]}]"
        if i in ("white_bed", "red_bed"):                 # Bett = 2 Blöcke; Richtung zeigt vom Fußende zum Kopf
            props = {"part": p.get("part", "foot")} | ({"facing": RICHTUNG[f]} if f else {})
        if i == "crafter":
            if f in ("n", "e", "s", "w"):                  # liegend: Gesicht zeigt nach f (zur Truhe), oben ist oben
                props = {"orientation": f"{RICHTUNG[f]}_up"}
                pr = f"minecraft:crafter[orientation={RICHTUNG[f]}_up]"
                name = "Crafter (Gesicht zur Truhe)"
                return {"art": "block", "anzeige": anz, "props": props, "pruefen": pr, "item": item, "name": name,
                        "schluessel": f"crafter:{RICHTUNG[f]}"}
            props = {"orientation": "down_north"}          # Vorderseite nach unten
        if i == "pointed_dripstone":
            props = {"vertical_direction": "down", "thickness": "tip"}
        if i == "tall_flower":
            props = {"half": "lower"}
        if i == "daylight_detector_inv":
            props = {"inverted": "true"}
        return {"art": "block", "anzeige": anz, "props": props, "pruefen": pr, "item": item, "name": name,
                "schluessel": i}
    if i in GERICHTET:
        anz, pr, item, name = GERICHTET[i]
        f = f or "d"
        if i in ("comparator", "repeater"):          # Plan: Signal geht nach f; Minecraft: facing zeigt zum Eingang
            facing = RICHTUNG[GEGEN[f]]
        elif i == "hopper" and f == "u":
            facing = "down"
        else:
            facing = RICHTUNG[f]
        props = {"facing": facing}
        return {"art": "block", "anzeige": anz, "props": props, "pruefen": f"{pr}[facing={facing}]", "item": item,
                "name": name, "schluessel": f"{i}:{facing}"}
    if i in ("slab", "stone_slab"):
        typ = p.get("half", "bottom")
        anz = "smooth_stone_slab" if i == "slab" else "stone_brick_slab"
        name = ("Stufe" if i == "slab" else "Steinziegelstufe") + (" (oben)" if typ == "top" else " (unten)")
        return {"art": "block", "anzeige": anz, "props": {"type": typ}, "pruefen": f"#minecraft:slabs[type={typ}]",
                "item": "#minecraft:slabs", "name": name, "schluessel": f"{i}:{typ}"}
    if i == "oak_trapdoor":
        half = p.get("half", "bottom")
        props, pr = {"half": half}, f"half={half}"
        if p.get("open"):                                # offen: steht senkrecht, Mobs halten sie für Boden;
            props["open"] = "true"                       # oben/unten ist dann egal (gleiche Form)
            pr = "open=true"
        if f in ("n", "e", "s", "w"):                    # Richtung zählt (offen steht die Klappe auf der Gegenseite)
            props["facing"] = RICHTUNG[f]
            pr += f",facing={RICHTUNG[f]}"
        return {"art": "block", "anzeige": "oak_trapdoor", "props": props,
                "pruefen": f"#minecraft:wooden_trapdoors[{pr}]", "item": "#minecraft:wooden_trapdoors",
                "name": "Falltür" + (" (offen)" if p.get("open") else " (oben)" if half == "top" else " (unten)"),
                "schluessel": f"trapdoor:{half}:{props.get('facing', '')}:{props.get('open', '')}"}
    if i == "rail":
        achse = p.get("axis", "z")
        if r % 2:
            achse = "x" if achse == "z" else "z"
        form = "north_south" if achse == "z" else "east_west"
        return {"art": "block", "anzeige": "rail", "props": {"shape": form},
                "pruefen": "minecraft:rail", "item": "minecraft:rail", "name": "Schiene", "schluessel": "rail"}
    if i == "powered_rail":
        achse = p.get("axis", "z")
        if r % 2:
            achse = "x" if achse == "z" else "z"
        form = "north_south" if achse == "z" else "east_west"
        return {"art": "block", "anzeige": "powered_rail", "props": {"shape": form},
                "pruefen": f"minecraft:powered_rail[shape={form}]", "item": "minecraft:powered_rail",
                "name": "Antriebsschiene", "schluessel": f"rail:{form}"}
    raise KeyError(f"Block ohne Übersetzung: {i}")


# ---- Zusätzliche Blöcke aus den Profi-Varianten (generator/profi/*.py): BLOECKE = {...} im EINFACH-Format,
# GERICHTET_NEU = {...} im GERICHTET-Format, jeweils als reines Literal (wird hier gelesen, nicht ausgeführt)
def _profi_bloecke():
    import ast
    import glob
    import os
    for pfad in sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "profi", "*.py"))):
        for knoten in ast.parse(open(pfad, encoding="utf-8").read()).body:
            if isinstance(knoten, ast.Assign) and len(knoten.targets) == 1 and \
                    getattr(knoten.targets[0], "id", None) in ("BLOECKE", "GERICHTET_NEU"):
                ziel = EINFACH if knoten.targets[0].id == "BLOECKE" else GERICHTET
                for k, v in ast.literal_eval(knoten.value).items():
                    ziel.setdefault(k, tuple(v))


_profi_bloecke()
