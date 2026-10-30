"""Baut Ole's Farmhelper: ein Datapack (Bauhelfer mit Geisterblöcken) und ein kleines Ressourcenpaket (Item-Bild).

Aufruf:  python3 farmhelper.py <plaene.json> <ausgabe-ordner>

plaene.json kommt aus dem Farm-Handbuch (export.js): je Farm Name, Infos, belegte Orts- und Meta-Angaben mit Quellen
und die Bauschritte mit allen Blöcken (x, y, z relativ, Block-id aus bloecke.py).

So funktioniert es im Spiel
- Das Item ist ein Karottenstock mit eigenem Bild (item_model ole:farmhelper, kommt über das Ressourcenpaket).
  Rechtsklick öffnet ein Fenster (Dialog): alle Farmen → Infos mit Quellen → „Hier bauen“.
- „Hier bauen“ setzt einen unsichtbaren Marker vor den Spieler (in Blickrichtung, eine von 4 Drehungen) und zeigt den
  ersten Teilschritt als leuchtende Geisterblöcke (block_display, 80 % groß). Teilschritt = ein Bauschritt des Handbuchs,
  Ebene für Ebene von unten nach oben.
- Jede Sekunde prüft das Pack jeden Geisterblock: richtig gesetzt → Geist weg; falscher Block → Geist leuchtet rot.
  Sind alle richtig, kommt der nächste Teilschritt. Lebewesen (Dorfbewohner …) zählen, sobald sie dort stehen.
- Die Aktionsleiste zeigt Schritt, fehlende Blöcke und je Material „im Inventar / fehlt noch“.
- Spieler ohne Operator-Rechte schicken Knopfdrücke per /trigger ofh (Zahlencodes, siehe CODES).
"""
import json
import os
import shutil
import sys
import zipfile

import bloecke
import textur

NS = "ofh"
FORMAT_MIN, FORMAT_MAX = 71, 121
RES_FORMAT = 97
PLAENE = json.load(open(sys.argv[1], encoding="utf-8"))
# Blöcke, die in einer Farm von selbst entstehen (Ertrag oder fließende Flüssigkeit): kein Geist, keine Prüfung
VON_SELBST_IN = {"bruchstein": lambda b: b["id"] == "cobblestone" or (b["id"] == "lava" and (b["x"], b["y"], b["z"]) == (3, 1, 0))}
for _f in PLAENE:
    weg = VON_SELBST_IN.get(_f["id"])
    if weg:
        _f["fertig"] = [b for b in _f["fertig"] if not weg(b)]
        for _s in _f["steps"]:
            _s["added"] = [b for b in _s["added"] if not weg(b)]
AUS = sys.argv[2]
VERSION = 1                      # erhöhen, wenn alle ein neues Item bekommen sollen
GRUEN, ROT, GELB = 0x55FF55, 0xFF4040, 0xFFD040

# Trigger-Codes
INFO, BAUEN, ORT = 0, 1000, 2000          # + Farm-Nummer (1 … 33)
MENU, PLANMENU, PLANORT, ZURUECK, WEITER, ABBRUCH, NEU_ITEM = 9000, 9001, 9002, 9020, 9021, 9022, 9099
SCHIEBEN = {9010: ("~ ~ ~-1", "Norden"), 9011: ("~ ~ ~1", "Süden"), 9012: ("~1 ~ ~", "Osten"),
            9013: ("~-1 ~ ~", "Westen"), 9014: ("~ ~1 ~", "hoch"), 9015: ("~ ~-1 ~", "runter")}
DREHEN = 9016
MATERIAL = 9003

dateien = {}


def datei(pfad, inhalt):
    dateien[pfad] = (inhalt if isinstance(inhalt, str) else "\n".join(inhalt)).rstrip("\n") + "\n"


def funktion(name, zeilen):
    datei(f"data/{NS}/function/{name}.mcfunction", zeilen)


def j(obj):
    return json.dumps(obj, ensure_ascii=False)


def trig(code):
    return {"type": "run_command", "command": f"/trigger {NS}.t set {code}"}


def zahl(v):
    s = f"{v:.3f}".rstrip("0").rstrip(".")
    return s if s not in ("-0", "") else "0"


# ---------- Bauplan vorbereiten: Teilschritte, Drehungen, Lage vor dem Spieler ----------
def drehe_xz(x, z, r):
    for _ in range(r):                     # 90° im Uhrzeigersinn: Norden → Osten
        x, z = -z, x
    return x, z


BLICK = {0: (0, -1), 1: (1, 0), 2: (0, 1), 3: (-1, 0)}       # 0 Nord, 1 Ost, 2 Süd, 3 West


def teilschritte(farm):
    """[(Schritt-Nr, Text, Ebene k von n, [Blöcke])], je Bauschritt die neuen Blöcke Ebene für Ebene."""
    out = []
    for k, s in enumerate(farm["steps"]):
        bl = [b for b in s["added"] if b["id"] not in bloecke.VON_SELBST]
        ebenen = sorted({b["y"] for b in bl})
        if not ebenen:
            out.append((k, s["text"], 1, 1, []))
            continue
        for e, y in enumerate(ebenen, 1):
            ebene = [b for b in bl if b["y"] == y]
            if any(b["id"] == "water" for b in ebene) and any(b["id"] == "lava" for b in ebene):
                # Gleichzeitig gesetzt fließt Wasser auf die Lavaquelle und macht Obsidian: erst Lava, dann Wasser
                out.append((k, s["text"] + " – Zuerst die Lava setzen.", e, len(ebenen),
                            [b for b in ebene if b["id"] != "water"]))
                out.append((k, s["text"] + " – Jetzt das Wasser.", e, len(ebenen), [b for b in ebene if b["id"] == "water"]))
            else:
                out.append((k, s["text"], e, len(ebenen), ebene))
    return out


def lage(farm, r):
    """Verschiebung (ox, oz), damit der gedrehte Plan 2 Blöcke vor dem Spieler steht, mittig in Blickrichtung."""
    pts = [drehe_xz(b["x"], b["z"], r) for b in farm["fertig"]]
    xs, zs = [p[0] for p in pts], [p[1] for p in pts]
    fx, fz = BLICK[r]
    mx, mz = -round((min(xs) + max(xs)) / 2), -round((min(zs) + max(zs)) / 2)
    if fz == -1:
        return mx, -2 - max(zs)
    if fz == 1:
        return mx, 2 - min(zs)
    if fx == 1:
        return 2 - min(xs), mz
    return -2 - max(xs), mz


def spawner_lage(farm):
    for b in farm["fertig"]:
        if b["id"] == "spawner":
            return b
    return None


# ---------- Geister und Prüfungen ----------
def anzeige_nbt(d, rot=False):
    props = ",".join(f'{k}:"{v}"' for k, v in d["props"].items())
    zustand = f'{{id:"minecraft:{d["anzeige"]}"' + (f",properties:{{{props}}}" if props else "") + "}"   # Format 26.3
    return (f'{{block_state:{zustand},transformation:[0.8f,0f,0f,0f,0f,0.8f,0f,0f,0f,0f,0.8f,0f,0f,0f,0f,1f],'
            f'Glowing:1b,glow_color_override:{ROT if rot else GRUEN},brightness:{{sky:15,block:15}},'
            f'Tags:["{NS}_g","{NS}_neu"]}}')


def text_nbt(text, farbe="yellow"):
    return (f'{{text:{{text:"{text}",color:"{farbe}"}},billboard:"center",see_through:1b,'
            f'background:1073741824,Tags:["{NS}_g","{NS}_neu"]}}')


# Gemeinsame Mini-Funktionen: je Prüfung (und Material-Zähler k) eine Datei, die an „~ ~ ~“ arbeitet.
# Jeder Block im Plan braucht dann nur noch eine kurze Zeile „execute positioned ~x ~y ~z run function …“.
KLEIN = {}


def klein(art, schluessel, zeilen):
    if (art, schluessel) not in KLEIN:
        KLEIN[(art, schluessel)] = f"{NS}:{art}/{len([1 for a, _ in KLEIN if a == art])}"
        funktion(KLEIN[(art, schluessel)].split(":")[1], zeilen)
    return KLEIN[(art, schluessel)]


GEIST = f"positioned ~0.1 ~0.1 ~0.1 run kill @e[type=minecraft:block_display,tag={NS}_g,distance=..0.05]"


def nicht(pr):
    """„unless block …“ für jede erlaubte Variante (pruefen kann mehrere mit | getrennt haben)."""
    return " ".join(f"unless block ~ ~ ~ {v}" for v in pr.split("|"))


def zeilen_block(x, y, z, d, k):
    pr = d["pruefen"]
    fn = klein("c", (pr, k), [
        f"execute {nicht(pr)} run scoreboard players add #m{k} {NS} 1",
        *[f"execute if block ~ ~ ~ {v} {GEIST}" for v in pr.split("|")],
        f"execute unless block ~ ~ ~ #minecraft:replaceable {nicht(pr)} positioned ~0.1 ~0.1 ~0.1 run "
        f"data merge entity @e[type=minecraft:block_display,tag={NS}_g,distance=..0.05,limit=1] "
        f"{{glow_color_override:{ROT}}}"])
    return [f"execute positioned ~{x} ~{y} ~{z} run function {fn}"]


def zeilen_wesen(x, y, z, d, k):
    sel = f"@e[type={d['typ']},distance=..1.5]"
    fn = klein("w", (d["typ"], k), [
        f"execute positioned ~0.5 ~ ~0.5 unless entity {sel} run scoreboard players add #m{k} {NS} 1",
        f"execute positioned ~0.5 ~ ~0.5 if entity {sel} positioned ~ ~1.4 ~ run kill "
        f"@e[type=minecraft:text_display,tag={NS}_g,distance=..0.05]"])
    return [f"execute positioned ~{x} ~{y} ~{z} run function {fn}"]


def geist(x, y, z, d):
    if d["art"] == "block":
        fn = klein("z", (d["pruefen"], d["anzeige"], j(d["props"])), [
            f"execute {nicht(d['pruefen'])} run summon minecraft:block_display ~0.1 ~0.1 ~0.1 {anzeige_nbt(d)}"])
    elif d["art"] == "wesen":
        fn = klein("z", ("wesen", d["typ"]), [
            f"execute positioned ~0.5 ~ ~0.5 unless entity @e[type={d['typ']},distance=..1.5] run summon "
            f"minecraft:text_display ~ ~1.4 ~ {text_nbt(d['name'] + ' hierher bringen')}"])
    else:
        fn = klein("z", ("afk",), [f"summon minecraft:text_display ~0.5 ~1.4 ~0.5 {text_nbt('AFK-Platz: hier stehen', 'aqua')}"])
    return f"execute positioned ~{x} ~{y} ~{z} run function {fn}"


def hindernis(x, y, z, d):
    fn = klein("h", (d["pruefen"],), [f"execute unless block ~ ~ ~ #minecraft:replaceable {nicht(d['pruefen'])} "
                                      f"run scoreboard players add #hind {NS} 1"])
    return f"execute positioned ~{x} ~{y} ~{z} run function {fn}"


# ---------- Material ----------
def material(liste, r=0):
    """{Name: [Name, Item, Anzahl, Art, Bild-Schlüssel]} in Reihenfolge des ersten Auftretens."""
    m = {}
    for b in liste:
        d = bloecke.block(b, r)
        if not d or d["art"] == "afk":
            continue
        key = d["name"]                       # gleiche Namen (z. B. Trichter in alle Richtungen) zusammenfassen
        if key not in m:
            bild = (d["typ"].split(":")[1] if d["art"] == "wesen" else (d.get("item") or ""))
            m[key] = [d["name"], d.get("item"), 0, d["art"], bild]
        m[key][2] += 1
    return m


# ---------- Bilder (Sprites) ----------
# sprites.json: alle Texturen aus 26.3, die es wirklich gibt (geprüft gegen die Spieldateien). Blöcke ohne eigenes
# Item-Bild bekommen eine Block-Textur aus dem Block-Atlas, sonst wären es lila-schwarze Kästchen.
VORHANDEN = set(json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "sprites.json"))))
ERSATZ = {
    "#minecraft:dirt": "dirt", "#minecraft:sand": "sand", "#minecraft:planks": "oak_planks", "#minecraft:wool": "white_wool",
    "#minecraft:wooden_fences": "oak_planks", "#minecraft:walls": "cobblestone", "#minecraft:signs": "oak_sign",
    "#minecraft:buttons": "stone", "#minecraft:beds": "red_wool", "#minecraft:wool_carpets": "white_wool",
    "#minecraft:saplings": "dark_oak_sapling", "#minecraft:small_flowers": "poppy", "#minecraft:slabs": "smooth_stone_slab_side",
    "#minecraft:wooden_trapdoors": "oak_trapdoor",
    "cactus": "cactus_side", "magma_block": "magma", "composter": "composter_side", "daylight_detector": "daylight_detector_top",
    "fletching_table": "fletching_table_front", "chest": "chest_minecart", "bee_nest": "bee_nest_front", "crafter": "crafter_north",
    "observer": "observer_front", "piston": "piston_side", "sticky_piston": "piston_top_sticky", "dispenser": "dispenser_front",
    "hay_block": "hay_block_side", "grass_block": "grass_block_side", "scaffolding": "scaffolding_side",
    "wither_skeleton_skull": "wither_rose", "redstone_wire": "redstone", "compass": "compass_16", "clock": "clock_00",
    "melon_stem": "melon_seeds", "hopper_minecart": "hopper_minecart", "minecart": "minecart",
}


def bild(name):
    """Text-Baustein mit dem Bild zu einem Item- oder Blocknamen (oder Tag)."""
    n = name.split(":")[-1] if not name.startswith("#") else name
    n = ERSATZ.get(n, ERSATZ.get(name, n))
    if not n.startswith("#") and f"item/{n}" not in VORHANDEN and f"item/{n}_spawn_egg" in VORHANDEN:
        n = n + "_spawn_egg"
    for atlas, pfad in (("items", f"item/{n}"), ("blocks", f"block/{n}")):
        if pfad in VORHANDEN:
            return {"type": "object", "object": "atlas", "atlas": f"minecraft:{atlas}", "sprite": pfad}
    return {"type": "object", "object": "atlas", "atlas": "minecraft:items", "sprite": "item/barrier"}


def gui(pfad):
    return {"type": "object", "object": "atlas", "atlas": "minecraft:gui", "sprite": pfad}


ICON = {"zuckerrohr": "sugar_cane", "bambus": "bamboo", "kaktus": "cactus", "kuerbis": "melon_slice", "seetang": "kelp",
        "weizen": "wheat", "baum": "oak_log", "knochenmehl": "bone_meal", "blumen": "poppy", "huehner": "cooked_chicken",
        "kuh": "leather", "wolle": "white_wool", "honig": "honey_bottle", "eisen": "iron_ingot",
        "xpspawner": "experience_bottle", "mobfarm": "bone", "creeper": "gunpowder", "schleim": "slime_ball",
        "hexe": "redstone", "waechter": "prismarine_shard", "lohe": "blaze_rod", "gold": "gold_nugget",
        "witherskelett": "wither_skeleton_skull", "enderman": "ender_pearl", "ertrunkene": "trident",
        "aussenposten": "ominous_bottle", "ueberfall": "totem_of_undying", "handel": "emerald",
        "bruchstein": "cobblestone", "lava": "lava_bucket", "schnee": "snowball", "angeln": "fishing_rod",
        "stockcrafter": "stick"}
KATEGORIEN = []                          # [(Name, Bild, Farbe, [Farm-Nummern])]
for _nr, _f in enumerate(PLAENE, 1):
    if not KATEGORIEN or KATEGORIEN[-1][0] != _f["cat"]:
        KATEGORIEN.append((_f["cat"], {"Pflanzen": "wheat", "Tiere": "leather", "Mobs": "bone", "Nether": "blaze_rod",
                                        "End": "ender_pearl", "Handel": "emerald", "Blöcke": "cobblestone",
                                        "Sonstiges": "fishing_rod"}.get(_f["cat"], "wheat"),
                           {"Pflanzen": "green", "Tiere": "gold", "Mobs": "red", "Nether": "dark_red", "End": "light_purple",
                            "Handel": "dark_green", "Blöcke": "gray", "Sonstiges": "aqua"}.get(_f["cat"], "white"), []))
    KATEGORIEN[-1][3].append(_nr)
KAT = 9100                               # + Index der Kategorie


# ---------- Ort-Prüfungen (aus den belegten Angaben im Handbuch) ----------
FLUSS = ["minecraft:river", "minecraft:frozen_river", "minecraft:dripstone_caves"]
OZEAN = ["minecraft:ocean", "minecraft:deep_ocean", "minecraft:cold_ocean", "minecraft:deep_cold_ocean",
         "minecraft:lukewarm_ocean", "minecraft:deep_lukewarm_ocean", "minecraft:warm_ocean", "minecraft:frozen_ocean",
         "minecraft:deep_frozen_ocean"]
SUMPF = ["minecraft:swamp", "minecraft:mangrove_swamp"]
HEISS = ["minecraft:desert", "minecraft:badlands", "minecraft:eroded_badlands", "minecraft:wooded_badlands",
         "minecraft:savanna", "minecraft:savanna_plateau", "minecraft:windswept_savanna"]
OBERWELT = ("dimension", "minecraft:overworld")


def struktur(s):
    return f'predicate {{type:"minecraft:location_check",predicate:{{structures:"{s}"}}}}'


# Je Farm: Liste von Prüfungen (Art, Werte, Text wenn gut, Text wenn schlecht)
PRUEF = {
    "ertrunkene": [("biom", FLUSS, "Biom: Fluss/Tropfsteinhöhle – dort spawnen Ertrunkene am meisten (Gewicht 100/95)",
                    "Kein Fluss-Biom: im Ozean spawnen Ertrunkene nur mit Gewicht 5 – besser in einen Fluss")],
    "mobfarm": [("biom", OZEAN, "Über dem Ozean: kaum andere Spawnflächen in 128 Blöcken",
                 "Nicht über dem Ozean: alle Höhlen in 128 Blöcken ausleuchten, sonst spawnen Mobs dort"),
                ("nicht_biom", ["minecraft:mushroom_fields", "minecraft:deep_dark"], "Biom erlaubt Monster-Spawns",
                 "In Pilzfeldern/Tiefer Dunkelheit spawnen keine Monster!")],
    "creeper": [("biom", OZEAN, "Über dem Ozean (empfohlen; am besten kalter Ozean)",
                 "Nicht über dem Ozean – das Wiki empfiehlt den Ozean")],
    "schleim": [("biom", SUMPF, "Sumpf: Schleime spawnen hier zwischen Y 51 und 69 bei Licht ≤ 7",
                 "Kein Sumpf: Du brauchst einen Schleim-Chunk (Chunkbase) und baust unter Y 40"),
                ("y_max", 40, "Unter Y 40 – passt für einen Schleim-Chunk", "Über Y 40: im Schleim-Chunk erst unter Y 40")],
    "hexe": [("struktur", "minecraft:swamp_hut", "Du stehst in einer Hexenhütten-Box", "Keine Hexenhütte hier – such eine im Sumpf")],
    "waechter": [("struktur", "minecraft:monument", "Du stehst in einer Ozeanmonument-Box", "Kein Ozeanmonument hier")],
    "lohe": [("dimension", "minecraft:the_nether", "Im Nether", "Nicht im Nether"),
             ("struktur", "minecraft:fortress", "In einer Netherfestung", "Keine Netherfestung hier – such den Lohen-Spawner")],
    "witherskelett": [("dimension", "minecraft:the_nether", "Im Nether", "Nicht im Nether"),
                      ("struktur", "minecraft:fortress", "In einer Netherfestung – nur dort spawnen Wither-Skelette",
                       "Keine Netherfestung hier")],
    "gold": [("dimension", "minecraft:the_nether", "Im Nether", "Nicht im Nether"),
             ("biom", ["minecraft:nether_wastes"], "Nether-Ödland: Zombifizierte Piglins mit Gewicht 100",
              "Nicht im Nether-Ödland (Karmesinwald nur Gewicht 1, sonst gar nicht)")],
    "enderman": [("dimension", "minecraft:the_end", "Im End", "Nicht im End"),
                 ("weg_von_mitte", 230, "Weit genug weg von der Hauptinsel (über 128 Blöcke Abstand)",
                  "Zu nah an der Hauptinsel – mindestens 128 Blöcke Abstand zu anderen Spawnflächen")],
    "aussenposten": [("struktur", "minecraft:pillager_outpost", "Du stehst in einer Plünderer-Außenposten-Box",
                      "Kein Außenposten hier – die Farm geht nur dort")],
    "ueberfall": [("biom", OZEAN, "Über dem Ozean – ideal", "Nicht über dem Ozean (das Wiki empfiehlt ihn)"),
                  ("keine_wesen", ("minecraft:villager", 96), "Keine fremden Dorfbewohner in 96 Blöcken",
                   "Dorfbewohner in der Nähe – der Überfall kann am falschen Dorf landen")],
    "eisen": [("keine_wesen", ("minecraft:iron_golem", 16), "Kein Eisengolem in 16 Blöcken",
               "Ein Eisengolem ist in 16 Blöcken – dann rufen die Dorfbewohner keinen neuen")],
    "schnee": [("nicht_biom", HEISS, "Kein heißes Biom: der Schneegolem schmilzt hier nicht",
                "Heißes Biom: der Schneegolem schmilzt hier!"),
               ("nicht_dimension", "minecraft:the_nether", "", "Im Nether schmilzt der Schneegolem")],
    "blumen": [("biom", ["minecraft:flower_forest"], "Blumenwald: hier wachsen fast alle Blumen",
                "Kein Blumenwald: hier wachsen nur die Blumen dieses Bioms")],
    "xpspawner": [("block_unter", "minecraft:spawner", "Du stehst auf einem Spawner", "Stell dich direkt auf den Spawner")],
}
NUR_OBERWELT = {"zuckerrohr", "bambus", "kaktus", "kuerbis", "seetang", "weizen", "baum", "knochenmehl", "huehner",
                "kuh", "wolle", "honig", "eisen", "mobfarm", "creeper", "schleim", "hexe", "waechter", "ertrunkene",
                "aussenposten", "ueberfall", "handel", "schnee", "angeln", "blumen"}


def ort_zeilen(fid):
    """Prüfzeilen: laufen als Spieler an der zu prüfenden Stelle; Ergebnis per tellraw nur an ihn."""
    z = [f'tellraw @s {{text:"— Ort-Check —",color:"gold"}}']
    pr = list(PRUEF.get(fid, []))
    if fid in NUR_OBERWELT:
        pr.insert(0, ("dimension", "minecraft:overworld", "In der Oberwelt", "Nicht in der Oberwelt"))

    def aus(gut, schlecht, bedingung_gut):
        z.append(f"scoreboard players set #ok {NS} 0")
        z.extend(f"execute {b} run scoreboard players set #ok {NS} 1" for b in bedingung_gut)
        if gut:
            z.append(f'execute if score #ok {NS} matches 1 run tellraw @s {{text:"✔ {gut}",color:"green"}}')
        z.append(f'execute if score #ok {NS} matches 0 run tellraw @s {{text:"✘ {schlecht}",color:"red"}}')

    for art, wert, gut, schlecht in pr:
        if art == "biom":
            aus(gut, schlecht, [f"if biome ~ ~ ~ {b}" for b in wert])
        elif art == "nicht_biom":
            z.append(f"scoreboard players set #ok {NS} 1")
            z.extend(f"execute if biome ~ ~ ~ {b} run scoreboard players set #ok {NS} 0" for b in wert)
            z.append(f'execute if score #ok {NS} matches 1 run tellraw @s {{text:"✔ {gut}",color:"green"}}')
            z.append(f'execute if score #ok {NS} matches 0 run tellraw @s {{text:"✘ {schlecht}",color:"red"}}')
        elif art == "dimension":
            aus(gut, schlecht, [f"if dimension {wert}"])
        elif art == "nicht_dimension":
            z.append(f'execute if dimension {wert} run tellraw @s {{text:"✘ {schlecht}",color:"red"}}')
        elif art == "struktur":
            aus(gut, schlecht, [f"if {struktur(wert)}"])
        elif art == "y_max":
            aus(gut, schlecht, [f"if predicate {{type:\"minecraft:location_check\",predicate:{{position:{{y:{{max:{wert}}}}}}}}}"])
        elif art == "weg_von_mitte":
            aus(gut, schlecht, [f"positioned 0 ~ 0 unless entity @s[distance=..{wert}]"])
        elif art == "keine_wesen":
            typ, weit = wert
            aus(gut, schlecht, [f"unless entity @e[type={typ},distance=..{weit}]"])
        elif art == "block_unter":
            aus(gut, schlecht, [f"if block ~ ~-1 ~ {wert}"])
    if len(pr) == 0:
        z.append('tellraw @s {text:"✔ Diese Farm geht überall – kein bestimmtes Biom nötig",color:"green"}')
    return z


# ---------- Dialoge ----------
LINIE = {"text": "━" * 34, "color": "dark_gray"}


def kopf(icon, text, farbe="gold"):
    return [bild(icon), {"text": "  " + text, "color": farbe, "bold": True}]


def sterne(n):
    return [{"text": "★" * n, "color": "gold"}, {"text": "★" * (5 - n), "color": "dark_gray"}]


def balken(teil, gesamt, breite=20):
    voll = round(breite * teil / max(gesamt, 1))
    return [{"text": "▌" * voll, "color": "green"}, {"text": "▌" * (breite - voll), "color": "dark_gray"},
            {"text": f"  {round(100 * teil / max(gesamt, 1))} %", "color": "white"}]


def titel(f):
    return [bild(ICON.get(f["id"], "wheat")), {"text": "  " + f["name"], "bold": True, "color": "gold"}]


def text_mit_quelle(text, url):
    if url and url.startswith("http"):
        return [{"text": " ▸ ", "color": "gold"}, {"text": text + " "},
                {"text": "[Quelle ↗]", "color": "aqua", "underlined": True,
                 "click_event": {"action": "open_url", "url": url}, "hover_event": {"action": "show_text", "value": url}}]
    marke = " ✔ Spieldaten 26.3" if url is None else " ✎ Hinweis zum Modell"
    return [{"text": " ▸ ", "color": "gold"}, {"text": text}, {"text": marke, "color": "dark_green" if url is None else "gray"}]


def body(texte, breite=400):
    return [{"type": "minecraft:plain_message", "width": breite, "contents": t} for t in texte]


def material_text(m, je_zeile=3):
    """Material als Raster: Bild, Anzahl, Name; mehrere Einträge je Zeile."""
    zeilen, zeile = [], []
    for name, item, n, art, bildname in m.values():
        zeile += [bild(bildname or "barrier"), {"text": f" {n}×", "color": "yellow", "bold": True},
                  {"text": f" {name}" + (" (herbringen)" if art == "wesen" else "") + "     ", "color": "white"}]
        if len(zeile) >= 3 * je_zeile:
            zeilen.append(zeile); zeile = []
    if zeile:
        zeilen.append(zeile)
    return zeilen or [[{"text": "nichts", "color": "gray"}]]


def knopf(text, code, farbe=None, icon=None, tip=None, breite=130, fett=False):
    label = ([bild(icon), {"text": " "}] if icon else []) + [{"text": text, **({"color": farbe} if farbe else {}),
                                                              **({"bold": True} if fett else {})}]
    k = {"label": label, "width": breite, "action": trig(code)}
    if tip:
        k["tooltip"] = {"text": tip}
    return k


def info_dialog(nr, f):
    meta = f.get("meta") or {}
    t = [[bild("emerald"), {"text": "  Ertrag: ", "color": "gold"}, {"text": f["out"]}],
         [bild("clock"), {"text": "  Menge: ", "color": "gold"}, {"text": meta.get("rate") or "keine belegte Zahl"}],
         [bild("compass"), {"text": "  Wo bauen: ", "color": "gold"}, {"text": f["where"]}],
         [bild("name_tag"), {"text": "  Spieler nötig: ", "color": "gold"}, {"text": f["afk"]}],
         [bild("golden_hoe"), {"text": "  Schwierigkeit: ", "color": "gold"}, *sterne(f["diff"])],
         LINIE, {"text": f["why"], "color": "gray", "italic": True}]
    if meta.get("ort"):
        t += [LINIE, kopf("map", "Der richtige Ort", "yellow")] + [text_mit_quelle(a, b) for a, b in meta["ort"]]
    if meta.get("meta"):
        t += [LINIE, kopf("writable_book", "Beste Bauweise & Erweitern", "yellow")] + \
             [text_mit_quelle(a, b) for a, b in meta["meta"]]
    if f.get("help"):
        t += [LINIE, kopf("knowledge_book", "Hilfe", "yellow")] + \
             [[{"text": " ? ", "color": "aqua", "bold": True}, {"text": q + ": ", "color": "white"}, {"text": a, "color": "gray"}]
              for q, a in f["help"]]
    t += [LINIE, kopf("chest", "Material für die ganze Farm", "yellow")] + material_text(material(f["fertig"]))
    t.append({"text": "Das ist das Lern-Modell aus Oles Farm-Handbuch. Für mehr Ertrag verlängern oder stapeln – wie, steht "
                      "unter „Beste Bauweise“.", "color": "dark_gray", "italic": True})
    return {"type": "minecraft:multi_action", "title": titel(f), "external_title": {"text": "Farm-Infos"},
            "body": body(t), "can_close_with_escape": True, "pause": False, "after_action": "close", "columns": 3,
            "actions": [knopf("Hier bauen", BAUEN + nr, "green", "golden_hoe", "Der Plan erscheint als leuchtende "
                              "Geisterblöcke 2 Blöcke vor dir, in Blickrichtung.", fett=True),
                        knopf("Ort prüfen", ORT + nr, "aqua", "compass", "Prüft Biom, Bauwerk, Dimension und Abstände "
                              "an der Stelle, an der du stehst."),
                        knopf("Zurück", KAT + [i for i, k in enumerate(KATEGORIEN) if nr in k[3]][0], "gray", "arrow")]}


def haupt_dialog():
    knoepfe = [knopf(f"{name}  ({len(nrn)})", KAT + i, farbe, icon, ", ".join(PLAENE[n - 1]["name"] for n in nrn), 150)
               for i, (name, icon, farbe, nrn) in enumerate(KATEGORIEN)]
    return {"type": "minecraft:multi_action",
            "title": [bild("golden_hoe"), {"text": "  Ole's ", "color": "yellow", "bold": True},
                      {"text": "Farmhelper", "color": "gold", "bold": True}],
            "external_title": {"text": "Ole's Farmhelper"},
            "body": body([{"text": "Was willst du farmen?", "color": "white", "bold": True},
                          {"text": "Infos mit Quellen, Ort-Check – und dann Schritt für Schritt bauen mit leuchtenden "
                                   "Geisterblöcken.", "color": "gray"}, LINIE], 300),
            "can_close_with_escape": True, "pause": False, "after_action": "close", "columns": 2,
            "actions": knoepfe, "exit_action": {"label": {"translate": "gui.done"}, "width": 150}}


def kategorie_dialog(i):
    name, icon, farbe, nrn = KATEGORIEN[i]
    knoepfe = []
    for nr in nrn:
        f = PLAENE[nr - 1]
        knoepfe.append({"label": [bild(ICON.get(f["id"], "wheat")), {"text": "  " + f["name"]}],
                        "tooltip": [*sterne(f["diff"]), {"text": "\n" + f["out"], "color": "white"},
                                    {"text": "\n" + f["where"], "color": "gray"}],
                        "width": 170, "action": trig(INFO + nr)})
    knoepfe.append(knopf("Alle Kategorien", MENU, "gray", "arrow", breite=170))
    return {"type": "minecraft:multi_action", "title": [bild(icon), {"text": "  " + name, "color": farbe, "bold": True}],
            "external_title": {"text": name}, "body": body([{"text": "Wähle eine Farm.", "color": "gray"}, LINIE], 360),
            "can_close_with_escape": True, "pause": False, "after_action": "close", "columns": 2, "actions": knoepfe}


def plan_dialog(nr, f, i, ts, gesamt):
    k, text, e, n, liste = ts
    t = [balken(i, gesamt),
         [{"text": f"Schritt {k + 1} von {len(f['steps'])}", "color": "gold", "bold": True},
          {"text": f"   Ebene {e}/{n} · Teil {i + 1}/{gesamt}", "color": "gray"}],
         LINIE, {"text": text, "color": "white"}, LINIE,
         kopf("chest", "Für diesen Teil brauchst du", "yellow")] + material_text(material(liste)) + [
         LINIE, [{"text": "■ ", "color": "green"}, {"text": "hier hinsetzen   ", "color": "gray"},
                 {"text": "■ ", "color": "red"}, {"text": "falscher Block   ", "color": "gray"},
                 {"text": "■ ", "color": "yellow"}, {"text": "Tier herbringen", "color": "gray"}]]
    a = [knopf("◀ Zurück", ZURUECK, "white", tip="Einen Teil zurück"),
         knopf("Weiter ▶", WEITER, "white", tip="Diesen Teil überspringen"),
         knopf("↻ Drehen", DREHEN, "aqua", tip="Plan um 90° drehen (um den Startpunkt)"),
         knopf("↑ Norden", 9010, "yellow"), knopf("↓ Süden", 9011, "yellow"), knopf("▲ Hoch", 9014, "yellow"),
         knopf("← Westen", 9013, "yellow"), knopf("→ Osten", 9012, "yellow"), knopf("▼ Runter", 9015, "yellow"),
         knopf("Ort prüfen", PLANORT, "aqua", "compass", "Biom, Bauwerk, Abstände – und wie viele Blöcke im Weg sind"),
         knopf("Material", MATERIAL, "gold", "chest", "Material für die ganze Farm"),
         knopf("Farm-Infos", INFO + nr, "white", "writable_book"),
         knopf("Andere Farm", MENU, "gray", "map"), knopf("Abbrechen", ABBRUCH, "red", "barrier",
                                                          "Plan und Geisterblöcke entfernen")]
    return {"type": "minecraft:multi_action", "title": titel(f), "external_title": {"text": "Bauplan"},
            "body": body(t), "can_close_with_escape": True, "pause": False, "after_action": "close", "columns": 3,
            "actions": a}


def material_dialog(f):
    return {"type": "minecraft:notice", "title": [bild("chest"), {"text": "  Material: " + f["name"], "bold": True,
                                                                   "color": "gold"}],
            "body": body([LINIE, *material_text(material(f["fertig"])), LINIE,
                          {"text": "Mehr Ertrag = Module verlängern oder stapeln (siehe Farm-Infos).", "color": "gray"}]),
            "action": {"label": {"text": "◀ Zurück"}, "width": 150, "action": trig(PLANMENU)}}


# ---------- Funktionen erzeugen ----------
CODES_DISPATCH = []
anzahl_zeilen = 0

for nr, f in enumerate(PLAENE, 1):
    fid = f["id"]
    ts = teilschritte(f)
    sp = spawner_lage(f)
    funktion(f"f/{fid}/info", [f"dialog show @s {j(info_dialog(nr, f))}"])
    funktion(f"f/{fid}/ort", ort_zeilen(fid))
    funktion(f"f/{fid}/material", [f"dialog show @s {j(material_dialog(f))}"])
    # Start: Marker setzen (Blickrichtung → Drehung r)
    start = [f"function {NS}:abbrechen_still", f"scoreboard players set #r {NS} 0",
             f"execute if entity @s[y_rotation=-135..-45] run scoreboard players set #r {NS} 1",
             f"execute if entity @s[y_rotation=-45..45] run scoreboard players set #r {NS} 2",
             f"execute if entity @s[y_rotation=45..135] run scoreboard players set #r {NS} 3"]
    for r in range(4):
        if sp:
            sx, sz = drehe_xz(sp["x"], sp["z"], r)
            ziel = f"~{-sx} ~{-1 - sp['y']} ~{-sz}"
            start.append(f"execute if score #r {NS} matches {r} if block ~ ~-1 ~ minecraft:spawner align xyz "
                         f"positioned {ziel} run function {NS}:marker {{farm:\"{fid}\",r:{r},n:{len(ts)}}}")
        else:
            ox, oz = lage(f, r)
            start.append(f"execute if score #r {NS} matches {r} align xyz positioned ~{ox} ~ ~{oz} run function "
                         f"{NS}:marker {{farm:\"{fid}\",r:{r},n:{len(ts)}}}")
    if sp:
        start.append(f'execute unless block ~ ~-1 ~ minecraft:spawner run tellraw @s {{text:"Stell dich direkt auf '
                     f'den Spawner und starte dann – der Plan wird um ihn herum gebaut.",color:"yellow"}}')
    funktion(f"f/{fid}/start", start)
    CODES_DISPATCH += [(INFO + nr, f"{NS}:f/{fid}/info"), (BAUEN + nr, f"{NS}:f/{fid}/start"),
                       (ORT + nr, f"{NS}:f/{fid}/ort")]

    for i, t in enumerate(ts):
        liste = t[4]
        mat = material(liste)
        keys = list(mat)
        # Plan-Menü und Anzeige-Leiste hängen nicht von der Drehung ab
        funktion(f"f/{fid}/s{i}/menu", [f"dialog show @s {j(plan_dialog(nr, f, i, t, len(ts)))}"])
        hud = []
        voll = round(10 * i / max(len(ts), 1))
        teile = [bild(ICON.get(fid, "wheat")), {"text": f" Schritt {t[0] + 1}/{len(f['steps'])} ", "color": "gold"},
                 {"text": "▌" * voll, "color": "green"}, {"text": "▌" * (10 - voll), "color": "dark_gray"},
                 {"text": "  fehlt ", "color": "gray"}, {"score": {"name": "#fehlt", "objective": NS}, "color": "yellow"}]
        for k, key in enumerate(keys):
            name, item, _, art, bildname = mat[key]
            teile += [{"text": "   "}, bild(bildname or "barrier"), {"text": " "}]
            if item:
                hud.append(f"execute store result score #h{k} {NS} run clear @s {item} 0")
                teile += [{"score": {"name": f"#h{k}", "objective": NS}, "color": "white"}, {"text": "/", "color": "dark_gray"}]
            teile.append({"score": {"name": f"#m{k}", "objective": NS}, "color": "yellow"})
        hud.append(f"title @s actionbar {j(teile)}")
        funktion(f"f/{fid}/s{i}/hud", hud)
        for r in range(4):
            zeigen, pruefen = [], [f"scoreboard players set #m{k} {NS} 0" for k in range(len(keys))]
            for b in liste:
                d = bloecke.block(b, r)
                if not d:
                    continue
                x, z = drehe_xz(b["x"], b["z"], r)
                y = b["y"]
                zeigen.append(geist(x, y, z, d))
                if d["art"] == "afk":
                    continue
                k = keys.index(d["name"])
                pruefen += zeilen_block(x, y, z, d, k) if d["art"] == "block" else zeilen_wesen(x, y, z, d, k)
            pruefen.append(f"scoreboard players set #fehlt {NS} 0")
            pruefen += [f"scoreboard players operation #fehlt {NS} += #m{k} {NS}" for k in range(len(keys))]
            zeigen.append(f"scoreboard players operation @e[tag={NS}_neu] {NS}.id = #cur {NS}.id")
            zeigen.append(f"tag @e[tag={NS}_neu] remove {NS}_neu")
            funktion(f"f/{fid}/r{r}/s{i}/zeigen", zeigen)
            funktion(f"f/{fid}/r{r}/s{i}/pruefen", pruefen)
            anzahl_zeilen += len(zeigen) + len(pruefen)
    # Hindernisse im ganzen Plan (für „Ort prüfen“ am Plan)
    for r in range(4):
        h = [f"scoreboard players set #hind {NS} 0"]
        for b in f["fertig"]:
            d = bloecke.block(b, r)
            if not d or d["art"] != "block":
                continue
            x, z = drehe_xz(b["x"], b["z"], r)
            h.append(hindernis(x, b["y"], z, d))
        funktion(f"f/{fid}/r{r}/hindernisse", h)
        anzahl_zeilen += len(h)

# ---------- Allgemeine Funktionen ----------
MARKE = f"minecraft:custom_data={{{NS}:1b}}"
UNSER = f"*[{MARKE.replace('=', '~', 1)}]"
ITEM = (f"minecraft:carrot_on_a_stick[{MARKE},minecraft:item_model=\"ole:farmhelper\","
        f"minecraft:item_name={{text:\"Ole's Farmhelper\",color:\"gold\"}},minecraft:unbreakable={{}},"
        f"minecraft:lore=[{{text:\"Rechtsklick: Farm wählen und Schritt für Schritt bauen\",color:\"gray\",italic:false}},"
        f"{{text:\"Geisterblöcke zeigen, wo was hinkommt\",color:\"gray\",italic:false}}]]")
NEU = f"{NS}.v{VERSION}"

funktion("load", [f"scoreboard objectives add {NS} dummy",
                  f"scoreboard objectives add {NS}.t trigger \"Farmhelper\"",
                  f"scoreboard objectives add {NS}.id dummy",
                  f"scoreboard objectives add {NS}.s dummy",
                  f"scoreboard objectives add {NS}.r dummy",
                  f"scoreboard objectives add {NS}.n dummy",
                  f"scoreboard objectives add {NS}.klick minecraft.used:minecraft.carrot_on_a_stick",
                  f"schedule function {NS}:sekunde 20t replace"])

tick = [f"scoreboard players enable @a {NS}.t",
        f"execute as @a[scores={{{NS}.klick=1..}}] if items entity @s weapon.mainhand {UNSER} run function {NS}:klick",
        f"scoreboard players reset @a[scores={{{NS}.klick=1..}}] {NS}.klick",
        f"execute as @a unless score @s {NS}.id matches 1.. run function {NS}:neue_id",
        f"execute as @a[tag=!{NEU}] run function {NS}:item",
        f"tag @a add {NEU}",
        f"execute as @a[scores={{{NS}.t=1..}}] at @s run function {NS}:trigger",
        f"scoreboard players reset @a[scores={{{NS}.t=1..}}] {NS}.t"]
funktion("tick", tick)
funktion("neue_id", [f"scoreboard players add #naechste {NS}.id 1", f"scoreboard players operation @s {NS}.id = #naechste {NS}.id"])
funktion("item", [f"clear @s {UNSER}", f"give @s {ITEM}"])

# Trigger verteilen
for _i in range(len(KATEGORIEN)):
    funktion(f"kat/{_i}", [f"dialog show @s {j(kategorie_dialog(_i))}"])
    CODES_DISPATCH.append((KAT + _i, f"{NS}:kat/{_i}"))
tr = [f"scoreboard players operation #cur {NS}.id = @s {NS}.id"]
for code, fn in CODES_DISPATCH:
    tr.append(f"execute if score @s {NS}.t matches {code} run return run function {fn}")
tr += [f"execute if score @s {NS}.t matches {MENU} run return run function {NS}:menu",
       f"execute if score @s {NS}.t matches {PLANMENU} run return run function {NS}:klick",
       f"execute if score @s {NS}.t matches {NEU_ITEM} run return run function {NS}:item",
       f"execute if score @s {NS}.t matches {ABBRUCH} run return run function {NS}:abbrechen"]
for code, fn in ((PLANORT, "ort_plan"), (ZURUECK, "zurueck"), (WEITER, "weiter"), (DREHEN, "drehen"),
                 (MATERIAL, "material")):
    tr.append(f"execute if score @s {NS}.t matches {code} run return run execute as @e[type=minecraft:marker,"
              f"tag={NS}_plan] if score @s {NS}.id = #cur {NS}.id at @s run function {NS}:plan/{fn}")
for code, (ziel, _) in SCHIEBEN.items():
    tr.append(f"execute if score @s {NS}.t matches {code} run return run execute as @e[type=minecraft:marker,"
              f"tag={NS}_plan] if score @s {NS}.id = #cur {NS}.id at @s run function {NS}:plan/schieben "
              f"{{ziel:\"{ziel}\"}}")
funktion("trigger", tr)

funktion("menu", [f"dialog show @s {j(haupt_dialog())}"])
# Rechtsklick: mit aktivem Plan das Plan-Menü, sonst die Farmliste
funktion("klick", [f"scoreboard players operation #cur {NS}.id = @s {NS}.id",
                   f"execute as @e[type=minecraft:marker,tag={NS}_plan] if score @s {NS}.id = #cur {NS}.id run "
                   f"return run function {NS}:plan/menu_von",
                   f"function {NS}:menu"])

# Marker anlegen (Makro: farm, r, n); läuft als Spieler, positioniert am Plan-Nullpunkt
funktion("marker", ["$summon minecraft:marker ~ ~ ~ {Tags:[\"" + NS + "_plan\",\"" + NS + "_neum\"],data:{farm:\"$(farm)\",r:$(r),s:0}}",
                    f"scoreboard players operation @e[type=minecraft:marker,tag={NS}_neum] {NS}.id = #cur {NS}.id",
                    f"scoreboard players set @e[type=minecraft:marker,tag={NS}_neum] {NS}.s 0",
                    f"$scoreboard players set @e[type=minecraft:marker,tag={NS}_neum] {NS}.r $(r)",
                    f"$scoreboard players set @e[type=minecraft:marker,tag={NS}_neum] {NS}.n $(n)",
                    f"execute as @e[type=minecraft:marker,tag={NS}_neum] at @s run function {NS}:plan/zeigen",
                    f"tag @e[type=minecraft:marker,tag={NS}_neum] remove {NS}_neum",
                    'tellraw @s [{text:"Plan gesetzt! ",color:"green"},{text:"Bau die grünen Geisterblöcke nach – '
                    'Rechtsklick mit dem Farmhelper öffnet das Plan-Menü (verschieben, drehen, überspringen).",color:"gray"}]',
                    "playsound minecraft:block.note_block.chime master @s ~ ~ ~ 1 1.4"])

# Plan-Funktionen: laufen als Marker, an seiner Stelle; #cur = Besitzer-Nummer
P = f"{NS}:plan"
funktion("plan/daten", [f"execute store result entity @s data.s int 1 run scoreboard players get @s {NS}.s",
                        f"execute store result entity @s data.r int 1 run scoreboard players get @s {NS}.r",
                        f"data modify storage {NS}:tmp d set from entity @s data"])
funktion("plan/geister_weg", [f"scoreboard players operation #cur {NS}.id = @s {NS}.id",
                              f"execute as @e[tag={NS}_g] if score @s {NS}.id = #cur {NS}.id run kill @s"])
funktion("plan/zeigen", [f"function {P}/geister_weg", f"function {P}/daten",
                         f"function {P}/zeigen_m with storage {NS}:tmp d"])
funktion("plan/zeigen_m", ["$function " + NS + ":f/$(farm)/r$(r)/s$(s)/zeigen"])
funktion("plan/pruefen_m", ["$function " + NS + ":f/$(farm)/r$(r)/s$(s)/pruefen"])
funktion("plan/hud_m", ["$function " + NS + ":f/$(farm)/s$(s)/hud"])
funktion("plan/menu_m", ["$function " + NS + ":f/$(farm)/s$(s)/menu"])
funktion("plan/ort_m", ["$function " + NS + ":f/$(farm)/ort", "$function " + NS + ":f/$(farm)/r$(r)/hindernisse"])
funktion("plan/material_m", ["$function " + NS + ":f/$(farm)/material"])
# Alles hier läuft als Marker an seiner Stelle; „execute as <Besitzer>“ behält die Stelle des Markers
BESITZER = f"execute as @a if score @s {NS}.id = #cur {NS}.id run"
funktion("plan/sekunde", [f"scoreboard players operation #cur {NS}.id = @s {NS}.id",
                          f"function {P}/daten",
                          f"function {P}/pruefen_m with storage {NS}:tmp d",
                          f"{BESITZER} function {P}/hud_m with storage {NS}:tmp d",
                          f"execute if score #fehlt {NS} matches 0 run function {P}/naechster"])
funktion("plan/naechster", [f"scoreboard players add @s {NS}.s 1",
                            f"execute if score @s {NS}.s >= @s {NS}.n run return run function {P}/fertig",
                            f"function {P}/zeigen",
                            f"execute as @a if score @s {NS}.id = #cur {NS}.id at @s run playsound "
                            "minecraft:entity.experience_orb.pickup master @s ~ ~ ~ 1 1.2",
                            f"{BESITZER} title @s actionbar " + '{text:"✔ Teil fertig – weiter geht\'s!",color:"green"}'])
funktion("plan/fertig", [f"function {P}/geister_weg",
                         f"execute as @a if score @s {NS}.id = #cur {NS}.id at @s run playsound "
                         "minecraft:ui.toast.challenge_complete master @s ~ ~ ~ 1 1",
                         f"{BESITZER} title @s title " + '{text:"Farm fertig!",color:"gold"}',
                         f"{BESITZER} title @s subtitle " + '{text:"Ole\'s Farmhelper",color:"yellow"}',
                         "kill @s"])
funktion("plan/zurueck", [f"execute if score @s {NS}.s matches 1.. run scoreboard players remove @s {NS}.s 1",
                          f"function {P}/zeigen"])
funktion("plan/weiter", [f"scoreboard players add @s {NS}.s 1",
                         f"execute if score @s {NS}.s >= @s {NS}.n run return run function {P}/fertig",
                         f"function {P}/zeigen"])
funktion("plan/drehen", [f"scoreboard players add @s {NS}.r 1",
                         f"execute if score @s {NS}.r matches 4.. run scoreboard players set @s {NS}.r 0",
                         f"function {P}/zeigen"])
funktion("plan/schieben", ["$tp @s $(ziel)", f"execute at @s run function {P}/zeigen"])
funktion("plan/menu_von", [f"scoreboard players operation #cur {NS}.id = @s {NS}.id", f"function {P}/daten",
                           f"{BESITZER} function {P}/menu_m with storage {NS}:tmp d"])
funktion("plan/ort_plan", [f"scoreboard players operation #cur {NS}.id = @s {NS}.id", f"function {P}/daten",
                           f"{BESITZER} function {P}/ort_m with storage {NS}:tmp d",
                           f"{BESITZER} tellraw @s [{{text:\"Blöcke im Weg: \",color:\"gold\"}},{{score:{{name:\"#hind\","
                           f"objective:\"{NS}\"}}}},{{text:\" (andere Blöcke dort, wo der Plan hinkommt – abbauen oder Plan "
                           f"verschieben)\",color:\"gray\"}}]"])
funktion("plan/material", [f"scoreboard players operation #cur {NS}.id = @s {NS}.id", f"function {P}/daten",
                           f"{BESITZER} function {P}/material_m with storage {NS}:tmp d"])
funktion("abbrechen", [f"function {NS}:abbrechen_still",
                       'tellraw @s {text:"Plan abgebrochen.",color:"gray"}'])
funktion("abbrechen_still", [f"scoreboard players operation #cur {NS}.id = @s {NS}.id",
                             f"execute as @e[tag={NS}_g] if score @s {NS}.id = #cur {NS}.id run kill @s",
                             f"execute as @e[type=minecraft:marker,tag={NS}_plan] if score @s {NS}.id = #cur {NS}.id run kill @s"])
funktion("sekunde", [f"execute as @e[type=minecraft:marker,tag={NS}_plan] at @s run function {P}/sekunde",
                     f"schedule function {NS}:sekunde 20t replace"])

# Tags, Rezept, Pack-Datei
for name, werte in {"truhe": ["minecraft:chest", "minecraft:trapped_chest"],
                    "boden": ["#minecraft:dirt", "minecraft:grass_block"],
                    "bambus": ["minecraft:bamboo", "minecraft:bamboo_sapling"],
                    "seetang": ["minecraft:kelp", "minecraft:kelp_plant"],
                    "staengel": ["minecraft:melon_stem", "minecraft:attached_melon_stem", "minecraft:pumpkin_stem",
                                 "minecraft:attached_pumpkin_stem"],
                    "bienen": ["minecraft:bee_nest", "minecraft:beehive"]}.items():
    datei(f"data/{NS}/tags/block/{name}.json", json.dumps({"values": werte}, indent=2))
datei(f"data/{NS}/recipe/farmhelper.json", json.dumps({
    "type": "minecraft:crafting_shapeless", "category": "misc",
    "ingredients": ["minecraft:paper", "minecraft:wheat_seeds", "minecraft:stick"],
    "result": {"id": "minecraft:carrot_on_a_stick", "count": 1, "components": {
        "minecraft:custom_data": {NS: True}, "minecraft:item_model": "ole:farmhelper",
        "minecraft:item_name": {"text": "Ole's Farmhelper", "color": "gold"}, "minecraft:unbreakable": {},
        "minecraft:lore": [{"text": "Rechtsklick: Farm wählen und Schritt für Schritt bauen", "color": "gray",
                            "italic": False}]}}}, indent=2))
datei("data/minecraft/tags/function/load.json", json.dumps({"values": [f"{NS}:load"]}, indent=2))
datei("data/minecraft/tags/function/tick.json", json.dumps({"values": [f"{NS}:tick"]}, indent=2))
datei("pack.mcmeta", json.dumps({"pack": {"description": "Ole's Farmhelper", "pack_format": FORMAT_MIN,
                                          "supported_formats": [FORMAT_MIN, FORMAT_MAX], "min_format": FORMAT_MIN,
                                          "max_format": FORMAT_MAX}}, indent=2))

# ---------- Ausgabe ----------
os.makedirs(AUS, exist_ok=True)
with zipfile.ZipFile(os.path.join(AUS, "OlesFarmhelper.zip"), "w", zipfile.ZIP_DEFLATED) as zf:
    for pfad in sorted(dateien):
        zf.writestr(zipfile.ZipInfo(pfad, date_time=(2026, 1, 1, 0, 0, 0)), dateien[pfad].encode("utf-8"))
ordner = os.path.join(AUS, "OlesFarmhelper")
if os.path.isdir(ordner):
    shutil.rmtree(ordner)
for pfad, inhalt in dateien.items():
    voll = os.path.join(ordner, pfad)
    os.makedirs(os.path.dirname(voll), exist_ok=True)
    with open(voll, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(inhalt)

# Ressourcenpaket: nur das Item-Bild (Polymer liefert es beim Beitreten aus)
bild = os.path.join(AUS, "farmhelper.png")
textur.zeichnen().save(bild)
with zipfile.ZipFile(os.path.join(AUS, "OlesFarmhelper-Ressourcen.zip"), "w", zipfile.ZIP_DEFLATED) as zf:
    def rein(pfad, daten):
        zf.writestr(zipfile.ZipInfo(pfad, date_time=(2026, 1, 1, 0, 0, 0)), daten)
    rein("pack.mcmeta", json.dumps({"pack": {"description": "Ole's Farmhelper", "pack_format": RES_FORMAT,
                                             "min_format": RES_FORMAT, "max_format": RES_FORMAT}}, indent=2))
    rein("assets/ole/items/farmhelper.json",
         json.dumps({"model": {"type": "minecraft:model", "model": "ole:item/farmhelper"}}, indent=2))
    rein("assets/ole/models/item/farmhelper.json",
         json.dumps({"parent": "minecraft:item/handheld", "textures": {"layer0": "ole:item/farmhelper"}}, indent=2))
    rein("assets/ole/textures/item/farmhelper.png", open(bild, "rb").read())
print(f"{len(PLAENE)} Farmen, {len(dateien)} Dateien, {anzahl_zeilen} Bau-Befehlszeilen")
