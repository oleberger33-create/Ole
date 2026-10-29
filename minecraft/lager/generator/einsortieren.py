"""Sortiert den Inhalt von Truhen in die Fächer des Lagers (lager.py) und beschriftet die Schilder.

Als Modul: plan(inhalt) nimmt {(x, y, z): "<SNBT-Liste der Items>"} (so wie „data get block … Items“ sie ausgibt)
und liefert (befehle, texte): Befehle, die die Lagertruhen füllen, und die Schildtexte je Fach.
rest(vorher, jetzt) berechnet, was in einer Quelltruhe bleiben muss, wenn zwischen Lesen und Leeren etwas
dazugekommen ist (Trichter der Farmen laufen weiter): nur der Zuwachs bleibt liegen.

Kategorien nach der Item-ID (Reihenfolge = Reihenfolge der Fächer). Jede Kategorie bekommt doppelt so viel Platz,
wie sie braucht (mindestens ein Fach), übrige Fächer stehen als „Frei“ bereit. Gleiche Items ohne Zusatzdaten werden
zu vollen Stapeln zusammengelegt; alles mit Zusatzdaten (Haltbarkeit, Verzauberung, Text …) bleibt, wie es ist.
"""
import math
import re

import nbtlib
from nbtlib import tag

import lager

HOLZARTEN = ("oak", "spruce", "birch", "jungle", "acacia", "dark_oak", "mangrove", "cherry", "pale_oak", "bamboo",
             "crimson", "warped")
BLUMEN = {"poppy", "dandelion", "azure_bluet", "oxeye_daisy", "cornflower", "allium", "lily_of_the_valley",
          "blue_orchid", "sunflower", "lilac", "rose_bush", "peony", "wildflowers", "pink_petals", "torchflower",
          "wither_rose", "cactus_flower", "open_eyeblossom", "closed_eyeblossom", "spore_blossom"}


def holz(i):
    return any(i.startswith(h + "_") for h in HOLZARTEN)


KATEGORIEN = [
    ("Erze & Barren", ["Eisen, Gold, Kupfer", "Diamant, Lapis", "Quarz, Kohle"], lambda i: (
        i.endswith(("_ore", "_ingot", "_nugget")) or i.startswith("raw_") or i in {
            "diamond", "emerald", "lapis_lazuli", "coal", "charcoal", "quartz", "amethyst_shard", "netherite_scrap",
            "ancient_debris", "flint"} or i in {f"{m}_block" for m in (
                "iron", "gold", "copper", "diamond", "emerald", "lapis", "coal", "netherite", "amethyst")})),
    ("Werkzeuge", ["Spitzhacken, Äxte", "Schaufeln, Hacken", "Eimer, Angeln"], lambda i: (
        i.endswith(("_pickaxe", "_axe", "_shovel", "_hoe", "bucket")) or i in {
            "shears", "fishing_rod", "flint_and_steel", "spyglass", "brush", "compass", "recovery_compass", "clock",
            "lead", "name_tag", "saddle", "bundle", "carrot_on_a_stick"})),
    ("Kampf & Rüstung", ["Bögen, Pfeile", "Schwerter, Rüstung", "Armbrüste"], lambda i: (
        i.endswith(("_sword", "_spear", "_helmet", "_chestplate", "_leggings", "_boots", "_horse_armor", "arrow"))
        or i in {"bow", "crossbow", "trident", "shield", "totem_of_undying", "mace", "fire_charge", "elytra"})),
    ("Redstone & Schienen", ["Redstone, Fackeln", "Schienen, Loren", "Kolben, Trichter"], lambda i: (
        "redstone" in i or i.endswith(("rail", "minecart", "_bulb")) or i in {
            "repeater", "comparator", "piston", "sticky_piston", "observer", "hopper", "dropper", "dispenser",
            "lever", "stone_button", "stone_pressure_plate", "tnt", "daylight_detector", "target", "note_block",
            "tripwire_hook", "crafter", "lightning_rod", "slime_block", "honey_block"})),
    ("Essen", ["Äpfel, Fleisch", "Karotten, Kartoffeln", "Zucker, Weizen"], lambda i: (
        i.startswith("cooked_") or i in {
            "apple", "golden_apple", "enchanted_golden_apple", "golden_carrot", "beef", "porkchop", "chicken",
            "mutton", "rabbit", "cod", "salmon", "bread", "carrot", "potato", "baked_potato", "poisonous_potato",
            "beetroot", "melon_slice", "sweet_berries", "glow_berries", "cookie", "cake", "pumpkin_pie", "sugar",
            "wheat", "egg", "brown_egg", "blue_egg", "honey_bottle"})),
    ("Mob-Drops", ["Knochen, Fleisch", "Spinnenaugen, Fäden", "Schwarzpulver, Leder"], lambda i: i in {
        "bone", "bone_meal", "bone_block", "rotten_flesh", "spider_eye", "string", "gunpowder", "leather",
        "feather", "slime_ball", "ender_pearl", "blaze_rod", "breeze_rod", "ghast_tear", "phantom_membrane",
        "ink_sac", "glow_ink_sac", "rabbit_hide", "nautilus_shell", "dried_ghast", "shulker_shell", "armadillo_scute",
        "turtle_scute", "fermented_spider_eye", "blaze_powder", "magma_cream"}),
    ("Pflanzen & Samen", ["Kaktus, Mohn", "Samen, Setzlinge", "Blumen, Zuckerrohr"], lambda i: (
        i in BLUMEN or i.endswith(("_sapling", "_seeds", "_propagule", "_leaves", "_tulip", "_mushroom")) or i in {
            "cactus", "sugar_cane", "bamboo", "kelp", "cocoa_beans", "leaf_litter", "vine", "lily_pad",
            "short_grass", "tall_grass", "fern", "moss_block", "pumpkin", "melon", "dead_bush", "bush"})),
    ("Stein", ["Bruchstein, Stufen", "Glatter Stein", "Schiefer, Tuff"], lambda i: (
        any(s in i for s in ("cobble", "stone", "deepslate", "andesite", "diorite", "granite", "tuff", "brick",
                             "dripstone", "obsidian", "copper", "calcite", "prismarine"))
        and not i.startswith(("redstone", "glowstone")) and "blackstone" not in i and "nether_brick" not in i
        and i not in {"grindstone", "stonecutter", "lodestone"})),
    ("Erde & Sand", ["Erde, Kies, Sand", "Lehm, Gras"], lambda i: i in {
        "dirt", "grass_block", "coarse_dirt", "rooted_dirt", "podzol", "mycelium", "mud", "gravel", "sand",
        "red_sand", "clay", "clay_ball", "dirt_path", "snow_block", "snowball", "soul_soil_x"}),
    ("Holz", ["Bretter, Stämme", "Stufen, Treppen", "Türen, Leitern"], lambda i: (
        (holz(i) and not i.endswith(("_boat", "_raft", "_roots", "_fungus", "_nylium", "_sapling", "_propagule",
                                     "_leaves")))
        or i.endswith(("_log", "_wood", "_planks")) or i.startswith("stripped_") or i in {
            "stick", "ladder", "crafting_table", "barrel", "chest", "scaffolding", "bamboo_block"})),
    ("Nether", ["Netherrack", "Seelensand, Magma", "Schwarzstein, Basalt"], lambda i: (
        "nether" in i or "blackstone" in i or "basalt" in i or "soul_" in i or i.startswith(("crimson_", "warped_"))
        or i in {"magma_block", "glowstone", "glowstone_dust", "shroomlight", "quartz_block"})),
    ("Farben & Deko", ["Farbstoffe, Wolle", "Banner, Teppiche", "Glas, Laternen"], lambda i: (
        i.endswith(("_dye", "_wool", "_carpet", "_banner", "_bed", "candle", "glass", "glass_pane", "terracotta",
                    "_concrete", "_concrete_powder", "lantern"))
        or i in {"torch", "painting", "item_frame", "glow_item_frame", "flower_pot", "armor_stand"})),
    ("Sonstiges", ["Bücher, Karten", "Schallplatten", "Vorlagen, Boote"], lambda i: True),
]

EINZELN = ("_sword", "_spear", "_pickaxe", "_axe", "_shovel", "_hoe", "_helmet", "_chestplate", "_leggings",
           "_boots", "_horse_armor", "_boat", "_raft", "_bucket", "_minecart")
EINZELN_IDS = {"bow", "crossbow", "trident", "shield", "elytra", "fishing_rod", "shears", "flint_and_steel",
               "spyglass", "goat_horn", "bundle", "enchanted_book", "writable_book", "totem_of_undying", "saddle",
               "minecart", "potion", "splash_potion", "lingering_potion", "cake", "mace", "brush",
               "carrot_on_a_stick", "mushroom_stew", "rabbit_stew", "beetroot_soup", "suspicious_stew"}
SECHZEHN = ("_sign", "_banner")
SECHZEHN_IDS = {"egg", "brown_egg", "blue_egg", "snowball", "ender_pearl", "bucket", "armor_stand", "honey_bottle",
                "written_book"}


def max_stapel(i):
    if i in EINZELN_IDS or i.endswith(EINZELN) or i.startswith("music_disc_"):
        return 1
    if i in SECHZEHN_IDS or i.endswith(SECHZEHN):
        return 16
    return 64


def lesen(snbt):
    """SNBT aus dem Log → Liste von Compounds. nbtlib kennt keine Escapes wie \\n: vorübergehend ersetzen."""
    return list(nbtlib.parse_nbt(re.sub(r'\\([^"\\\'])', lambda m: "\u0001" + m.group(1), snbt)))


def schreiben(item):
    return nbtlib.serialize_tag(item).replace("\u0001", "\\")


def kategorie(i):
    for nr, (_, _, passt) in enumerate(KATEGORIEN):
        if passt(i):
            return nr
    return len(KATEGORIEN) - 1


def stapel(items):
    """Zusammenlegen: Items ohne Zusatzdaten zu vollen Stapeln, alles andere einzeln. Sortiert nach ID."""
    summe, einzeln = {}, []
    for it in items:
        i = str(it["id"]).removeprefix("minecraft:")
        if "components" in it:
            einzeln.append(it)
        else:
            summe[i] = summe.get(i, 0) + int(it["count"])
    out = []
    for i, n in summe.items():
        m = max_stapel(i)
        while n > 0:
            k = min(n, m)
            out.append(tag.Compound({"id": tag.String("minecraft:" + i), "count": tag.Int(k)}))
            n -= k
    out += einzeln
    return sorted(out, key=lambda it: (str(it["id"]), "components" in it))


def plan(inhalt, faktor=2.0):
    alle = [it for s in inhalt.values() for it in lesen(s)]
    je = {}
    for it in alle:
        je.setdefault(kategorie(str(it["id"]).removeprefix("minecraft:")), []).append(it)
    je = {k: stapel(v) for k, v in je.items()}
    gesamt = len(lager.faecher())
    while True:
        bedarf = {k: max(1, math.ceil(len(v) * faktor / 108)) for k, v in je.items()}
        if sum(bedarf.values()) <= gesamt or faktor <= 1.0:
            break
        faktor -= 0.1
    befehle, texte, fach = [], {}, 1
    for k in sorted(je):
        titel, info, _ = KATEGORIEN[k]
        n = bedarf[k]
        haelften = [h for f in range(fach, fach + n) for paar in lager.fach_truhen(f) for h in paar]
        rest = je[k]
        for h in haelften:
            teil, rest = rest[:27], rest[27:]
            if teil:
                for slot, it in enumerate(teil):
                    it["Slot"] = tag.Byte(slot)
                befehle.append(f"data modify block {h[0]} {h[1]} {h[2]} Items set value "
                               f"[{','.join(schreiben(it) for it in teil)}]")
        assert not rest, titel
        for i in range(n):
            texte[str(fach + i)] = [titel] + info
            texte[f"{fach + i}b"] = [titel, f"Teil {i + 1} von {n}" if n > 1 else "", "", ""]
        fach += n
    for f in range(fach, gesamt + 1):
        texte[str(f)] = texte[f"{f}b"] = ["Frei", "Platz für", "neue Sachen", ""]
    return befehle, texte


def schluessel(it):
    return (str(it["id"]), schreiben(it.get("components", tag.Compound())))


def rest(vorher, jetzt):
    """Was in der Quelltruhe bleibt: Zuwachs seit dem Lesen (gleicher Slot, gleiches Item, mehr Stück) und neue Items.
    Zweiter Wert: Stück, die seither herausgenommen wurden (stehen dann doppelt im Lager)."""
    alt = {int(it["Slot"]): it for it in lesen(vorher)}
    bleibt, weg = [], 0
    for it in lesen(jetzt):
        a = alt.pop(int(it["Slot"]), None)
        if a is not None and schluessel(a) == schluessel(it):
            d = int(it["count"]) - int(a["count"])
            if d > 0:
                it["count"] = tag.Int(d)
                bleibt.append(it)
            weg += max(0, -d)
        else:
            bleibt.append(it)
            if a is not None:
                weg += int(a["count"])
    weg += sum(int(a["count"]) for a in alt.values())
    return "[" + ",".join(schreiben(it) for it in bleibt) + "]", weg
