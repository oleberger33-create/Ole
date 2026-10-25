"""Baut das Datapack „Himmelsinsel-Spawn“ aus dem Bauplan.

Aufruf:  python3 datapack.py [zip-datei] [entpackt-ordner]
Ohne Angaben entsteht ../Himmelsinsel-Spawn.zip. Mit einem zweiten Pfad wird das Pack zusätzlich
entpackt dort abgelegt (praktisch zum Lesen und für pruefen.py).
"""
import json
import math
import os
import shutil
import sys
import zipfile

import bauplan
from bauplan import F, SPAWN, BIB, FLUCH, LANDUNG, BEREICH, AMBOSSE, BLUMEN
from haendler import HAENDLER, NUR_NEU, ROEMISCH, preis

NS = "himmelsinsel"
LEGACY = "legacy_1_21_5"       # Overlay für 1.21.5 bis 1.21.10
FORMAT_MIN, FORMAT_MAX = 71, 121   # 1.21.5 … 26.3
LEGACY_MAX = 93                # letztes Format vor 1.21.11

HIER = os.path.dirname(os.path.abspath(__file__))
ZIP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HIER, "..", "Himmelsinsel-Spawn.zip")
ORDNER = sys.argv[2] if len(sys.argv) > 2 else None

dateien = {}  # relativer Pfad -> Inhalt


def datei(pfad, zeilen):
    text = "\n".join(zeilen) if isinstance(zeilen, list) else zeilen
    dateien[pfad] = text.rstrip("\n") + "\n"


def funktion(name, zeilen, overlay=None):
    basis = f"{overlay}/" if overlay else ""
    datei(f"{basis}data/{NS}/function/{name}.mcfunction", zeilen)


def txt(obj):
    """Textkomponente als SNBT (JSON ist gültiges SNBT, Umlaute bleiben lesbar)."""
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def zahl(v):
    return str(int(v)) if float(v).is_integer() else f"{v:g}"


# ---------------------------------------------------------------- Blöcke → Befehle

PHASE2_NAMEN = {"short_grass", "tall_grass", "fern", "pink_petals", "wildflowers", "vine",
                "glow_lichen", "hanging_roots", "pointed_dripstone", "amethyst_cluster",
                "cave_vines", "cave_vines_plant", "lightning_rod", "anvil", *BLUMEN}


def phase(blk):
    name = blk.split("[")[0]
    if name in ("water", "light"):
        return 3
    if name in PHASE2_NAMEN or name.endswith("_carpet") or name.endswith("candle") \
            or name.endswith("lantern"):
        return 2
    return 1


def quader(zellen):
    """Fasst gleiche Blöcke gierig zu möglichst großen Quadern zusammen."""
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


def koord(v, relativ):
    if not relativ:
        return str(v)
    return "~" if v == 0 else f"~{v}"


def befehle(modell, relativ=False):
    """Liefert (befehl, volumen)-Paare in sicherer Reihenfolge: tragende Blöcke zuerst,
    dann Angehängtes von oben nach unten, zuletzt Wasser und Licht."""
    gruppen = {}
    for p, blk in modell.b.items():
        gruppen.setdefault((phase(blk), blk), []).append(p)
    liste = []
    for (ph, blk), zellen in gruppen.items():
        for q in quader(zellen):
            liste.append((ph, blk, q))
    liste.sort(key=lambda e: (e[0], e[2][1] if e[0] != 2 else -e[2][4], e[2][2], e[2][0]))
    out = []
    for ph, blk, (x1, y1, z1, x2, y2, z2) in liste:
        k = lambda v: koord(v, relativ)
        vol = (x2 - x1 + 1) * (y2 - y1 + 1) * (z2 - z1 + 1)
        if vol == 1:
            out.append((f"setblock {k(x1)} {k(y1)} {k(z1)} minecraft:{blk}", 1))
        else:
            out.append((f"fill {k(x1)} {k(y1)} {k(z1)} {k(x2)} {k(y2)} {k(z2)} minecraft:{blk}", vol))
    return out


def in_teile(liste, max_befehle=220, max_volumen=9000):
    teile, aktuell, n, vol = [], [], 0, 0
    for befehl, v in liste:
        if aktuell and (n + 1 > max_befehle or vol + v > max_volumen):
            teile.append(aktuell)
            aktuell, n, vol = [], 0, 0
        aktuell.append(befehl)
        n += 1
        vol += v
    if aktuell:
        teile.append(aktuell)
    return teile


def raeumen(modell):
    """Leert vor dem Bau den Luftraum der Insel (auch bei einem Neubau)."""
    ys = [p[1] for p in modell.b]
    y1, y2 = min(ys) - 2, max(ys) + 2
    x1, z1, x2, z2 = BEREICH
    out = []
    for cx in range(x1, x2 + 1, 16):
        for cz in range(z1, z2 + 1, 16):
            out.append(f"fill {cx} {y1} {cz} {cx + 15} {y2} {cz + 15} minecraft:air")
    return out, (y1, y2)


# ---------------------------------------------------------------- Händler & Schilder

def anzeige(x, y, z, text, breite=200, extra=""):
    return (f"summon minecraft:text_display {zahl(x)} {zahl(y)} {zahl(z)} "
            f"{{Tags:[\"hs.wesen\"],billboard:\"vertical\",shadow:1b,line_width:{breite},"
            f"text:{txt(text)}{extra}}}")


def angebot(ench, stufe):
    return ("{buy:{id:\"minecraft:emerald\",count:%d},buyB:{id:\"minecraft:book\",count:1},"
            "sell:{id:\"minecraft:enchanted_book\",count:1,components:{\"minecraft:stored_enchantments\":"
            "{\"minecraft:%s\":%d}}},maxUses:2147483647,uses:0,rewardExp:1b,xp:0,"
            "priceMultiplier:0.0f,specialPrice:0,demand:0}") % (preis(ench, stufe), ench, stufe)


def haendler_ort(h):
    if h["platz"] == "mitte":
        return BIB[0] + 0.5, F + 2, BIB[1] + 0.5, 0.0, (BIB[0] + 0.5, F + 4.4, BIB[1] + 0.5)
    if h["platz"] == "fluch":
        return FLUCH[0] - 0.5, F + 1, FLUCH[1] + 0.5, -90.0, (FLUCH[0] + 3.4, F + 3.5, FLUCH[1] + 0.5)
    phi = h["platz"]
    bx, bz = bauplan.stand_position(phi)
    yaw = (180 - phi + 180) % 360 - 180
    sx = BIB[0] + 0.5 + 5.9 * math.sin(math.radians(phi))
    sz = BIB[1] + 0.5 + 5.9 * math.cos(math.radians(phi))
    return bx + 0.5, F + 1, bz + 0.5, float(yaw), (round(sx, 2), F + 3.35, round(sz, 2))


def haendler_befehle(h, neu):
    buecher = [(e, s) for e, s in h["buecher"] if neu or e not in NUR_NEU]
    x, y, z, yaw, schild = haendler_ort(h)
    name = txt({"text": h["name"], "color": h["farbe"], "bold": True})
    angebote = ",".join(angebot(e, s) for e, s in buecher)
    villager = (f"summon minecraft:villager {zahl(x)} {zahl(y)} {zahl(z)} "
                f"{{NoAI:1b,Invulnerable:1b,PersistenceRequired:1b,CanPickUpLoot:0b,"
                f"Rotation:[{yaw}f,0.0f],Tags:[\"hs.wesen\",\"hs.haendler\"],CustomName:{name},"
                f"VillagerData:{{profession:\"minecraft:{h['beruf']}\",level:5,type:\"minecraft:{h['typ']}\"}},"
                f"VillagerDataFinalized:1b,Xp:250,Offers:{{Recipes:[{angebote}]}}}}")
    zeilen = ["", {"text": h["name"], "color": h["farbe"], "bold": True},
              {"text": "\n" + h["untertitel"], "color": "gray", "italic": True}]
    if h["platz"] != "mitte":
        for e, s in buecher:
            zeilen.append({"text": "\n"})
            zeilen.append({"translate": f"enchantment.minecraft.{e}", "color": "white"})
            if s > 1:
                zeilen.append({"text": " " + ROEMISCH[s], "color": "white"})
            zeilen.append({"text": f"  {preis(e, s)}", "color": "green"})
    else:
        zeilen.append({"text": "\nReparatur, Haltbarkeit, Effizienz,\nSchärfe, Schutz und mehr",
                       "color": "white"})
    zeilen.append({"text": "\nSmaragde + 1 Buch", "color": "dark_green"})
    return [f"# {h['name']}", villager, anzeige(*schild, zeilen, 170)]


def schilder():
    return [
        "# Schwebende Schilder auf der Insel",
        anzeige(0.5, F + 2.1, 3.9, ["", {"text": "✦ Himmelsinsel ✦", "color": "light_purple", "bold": True},
                                    {"text": "\nWillkommen!", "color": "white"},
                                    {"text": "\n\nNorden: Zauberbibliothek – alle Bücher", "color": "gray"},
                                    {"text": "\nOsten: Werkstatt – Zaubertisch & Ambosse", "color": "gray"},
                                    {"text": "\nSüden: Absprung in die Welt", "color": "gray"},
                                    {"text": "\n\nZurück zur Insel: ", "color": "gray"},
                                    {"text": "/trigger spawn", "color": "aqua"}], 230),
        anzeige(BIB[0] + 0.5, F + 5.6, BIB[1] + 9.3,
                ["", {"text": "Zauberbibliothek", "color": "light_purple", "bold": True},
                 {"text": "\nAlle Verzauberungsbücher", "color": "white"}]),
        anzeige(11.2, F + 3.3, 0.5,
                ["", {"text": "Werkstatt", "color": "gold", "bold": True},
                 {"text": "\nZaubertisch · Ambosse · Schleifstein", "color": "white"},
                 {"text": "\nDie Ambosse reparieren sich selbst", "color": "gray", "italic": True}]),
        anzeige(0.5, F + 5.5, 31.5,
                ["", {"text": "↓ Absprung ↓", "color": "aqua", "bold": True},
                 {"text": "\nFallschirm inklusive", "color": "white"},
                 {"text": "\nZurück: /trigger spawn oder Himmelstor", "color": "gray"}]),
    ]


# ---------------------------------------------------------------- Feste Funktionen

LADE_PRUEFUNG = " ".join(f"if loaded {x} 0 {z}" for x in range(-40, 41, 16) for z in range(-40, 41, 16))
ZONE = "x=-48,y=184,z=-48,dx=96,dy=90,dz=96"        # Schutzbereich (Abenteuermodus)
FALLBAND = "x=-48,y=184,z=-48,dx=96,dy=36,dz=96"    # Luft unter der Insel
UNTER_INSEL = "x=-36,y=-64,z=-36,dx=72,dy=247,dz=72"  # Boden unterhalb der Insel
TOR_BEREICH = "x=-3,y=-64,z=33,dx=6,dy=247,dz=8"     # rund um das Himmelstor der Bodenstation
SX, SY, SZ = SPAWN
ROT = {"color": "red"}
WARTET = ["", {"text": "[Himmelsinsel] ", "color": "light_purple"},
          {"text": "Bestehende Welt erkannt – es wurde noch nichts gebaut. Ein Admin startet den Bau mit ",
           "color": "white"},
          {"text": "/function himmelsinsel:admin/bauen", "color": "aqua"},
          {"text": " (Einstellungen vorher mit /function himmelsinsel:admin/info prüfen).", "color": "gray"}]

MONSTER = ["zombie", "husk", "drowned", "zombie_villager", "skeleton", "stray", "bogged",
           "wither_skeleton", "spider", "cave_spider", "creeper", "enderman", "endermite", "witch",
           "slime", "magma_cube", "phantom", "pillager", "vindicator", "evoker", "illusioner",
           "ravager", "vex", "silverfish", "breeze", "creaking", "blaze", "ghast", "hoglin", "zoglin",
           "piglin_brute", "guardian", "parched", "camel_husk", "zombie_nautilus"]


def feste_funktionen(lichtpunkte, n_teile):
    x1, z1, x2, z2 = BEREICH
    funktion("load", [
        "# Wird bei jedem Serverstart und /reload ausgeführt",
        "scoreboard objectives add hs.state dummy",
        "scoreboard objectives add hs.config dummy",
        "scoreboard objectives add hs.cd dummy",
        "scoreboard objectives add spawn trigger \"Zum Spawn\"",
        "scoreboard objectives add hs.tod deathCount",
        "scoreboard objectives add hs.weg minecraft.custom:minecraft.leave_game",
        "execute unless score #stufe hs.state = #stufe hs.state run scoreboard players set #stufe hs.state 0",
        f"execute if score #stufe hs.state matches -1 run tellraw @a {txt(WARTET)}",
        "# Einstellungen – werden nur beim allerersten Laden gesetzt (siehe README)",
        "execute unless score #spawn_befehl hs.config = #spawn_befehl hs.config run scoreboard players set #spawn_befehl hs.config 1",
        "execute unless score #abklingzeit hs.config = #abklingzeit hs.config run scoreboard players set #abklingzeit hs.config 30",
        "execute unless score #schutz hs.config = #schutz hs.config run scoreboard players set #schutz hs.config 1",
        "execute unless score #fallschirm hs.config = #fallschirm hs.config run scoreboard players set #fallschirm hs.config 1",
        "execute unless score #bodenstation hs.config = #bodenstation hs.config run scoreboard players set #bodenstation hs.config 1",
        "execute unless score #login_spawn hs.config = #login_spawn hs.config run scoreboard players set #login_spawn hs.config 1",
        "execute unless score #starterpaket hs.config = #starterpaket hs.config run scoreboard players set #starterpaket hs.config 1",
        f"schedule function {NS}:spiel/sekunde 20t",
        f"schedule function {NS}:spiel/halbsekunde 10t",
    ])
    funktion("tick", [
        f"execute unless score #fertig hs.state matches 1 run function {NS}:bau/tick",
        f"execute if score #fertig hs.state matches 1 run function {NS}:spiel/tick",
    ])
    # ---- Bauablauf
    funktion("bau/tick", [
        "# -1 = wartet auf /function himmelsinsel:admin/bauen, 0 = neu, 1 = lädt, 2+ = baut",
        f"execute if score #stufe hs.state matches 0 run function {NS}:bau/welt_pruefen",
        f"execute if score #stufe hs.state matches 1.. run function {NS}:bau/warten",
    ])
    funktion("bau/welt_pruefen", [
        "# Ganz neue Welt (jünger als 5 Minuten): sofort bauen.",
        "# Bestehende Welt: nichts anfassen, bis ein Admin den Bau startet.",
        "execute store result score #zeit hs.state run time query gametime",
        "execute if score #zeit hs.state matches 6001.. run scoreboard players set #stufe hs.state -1",
        f"execute if score #zeit hs.state matches 6001.. run tellraw @a {txt(WARTET)}",
        "execute if score #zeit hs.state matches ..6000 run scoreboard players set #neue_welt hs.state 1",
        f"execute if score #zeit hs.state matches ..6000 run function {NS}:bau/vorbereiten",
    ])
    funktion("bau/vorbereiten", [
        "# Bauplatz laden (die Insel schwebt über x 0 / z 0)",
        f"forceload add {x1} {z1} {x2} {z2}",
        "scoreboard players set #stufe hs.state 1",
        f"tellraw @a {txt({'text': '[Himmelsinsel] Lade den Bauplatz …', 'color': 'light_purple'})}",
    ])
    funktion("bau/warten", [
        "# Erst weitermachen, wenn alle 36 Chunks samt Wesen geladen sind",
        f"execute {LADE_PRUEFUNG} run function {NS}:bau/weiter",
    ])
    funktion("bau/weiter", [
        f"execute if score #stufe hs.state matches 1 run function {NS}:bau/start",
        f"execute if score #stufe hs.state matches 2.. run function {NS}:bau/schritt",
    ])
    funktion("bau/start", [
        "scoreboard players set #stufe hs.state 2",
        f"execute unless score #boden hs.state matches 1 run function {NS}:bau/boden",
        f"tellraw @a {txt({'text': '[Himmelsinsel] Baue die Insel … (dauert ein paar Sekunden)', 'color': 'light_purple'})}",
    ])
    boden = ["# Läuft nur einmal, solange unter dem Bauplatz noch freier Himmel ist.",
             "# Unsichtbare Lichter im Schatten der Insel, damit dort tagsüber keine Monster spawnen."]
    for x, z in lichtpunkte:
        boden.append(f"execute positioned {x} 0 {z} positioned over motion_blocking_no_leaves "
                     f"run setblock ~ ~ ~ minecraft:light[level=13] keep")
    boden += [f"execute if score #bodenstation hs.config matches 1 positioned {LANDUNG[0]} 0 {LANDUNG[1]} "
              f"positioned over motion_blocking_no_leaves run function {NS}:bau/bodenstation",
              "scoreboard players set #boden hs.state 1"]
    funktion("bau/boden", boden)
    schritt = ["# Baut pro Tick einen Teil der Insel"]
    for i in range(1, n_teile + 1):
        schritt.append(f"execute if score #stufe hs.state matches {i + 1} run function {NS}:bau/teil_{i:02d}")
    schritt += ["scoreboard players add #stufe hs.state 1",
                f"execute if score #stufe hs.state matches {n_teile + 2}.. run function {NS}:bau/fertig"]
    funktion("bau/schritt", schritt)
    funktion("bau/fertig", [
        f"function {NS}:bau/wesen",
        f"function {NS}:version/spawnpunkt",
        f"forceload remove {x1} {z1} {x2} {z2}",
        "scoreboard players set #fertig hs.state 1",
        "scoreboard players set #stufe hs.state 0",
        "# Neue Welt: wer schon unten am alten Spawn steht, kommt mit nach oben",
        f"execute if score #neue_welt hs.state matches 1 in minecraft:overworld "
        f"as @a[x=-100,y=-64,z=-100,dx=200,dy=384,dz=200] run function {NS}:spiel/zum_spawn_still",
        "scoreboard players set #neue_welt hs.state 0",
        f"tellraw @a {txt(['', {'text': '[Himmelsinsel] ', 'color': 'light_purple'}, {'text': 'Fertig! Die Spawn-Insel schwebt jetzt über x 0 / z 0.', 'color': 'white'}, {'text': chr(10) + 'Admins: In server.properties spawn-protection=0 setzen, sonst können Spieler ohne OP Ambosse und Werkbänke am Spawn nicht benutzen. Die Insel schützt sich selbst.', 'color': 'gray', 'italic': True}])}",
    ])
    wesen = ["# Händler und Schilder (alte vorher entfernen)",
             "kill @e[tag=hs.wesen,type=!minecraft:player]"]
    wesen += [f"function {NS}:haendler/{h['id']}" for h in HAENDLER]
    wesen.append(f"function {NS}:schilder")
    funktion("bau/wesen", wesen)

    # ---- Spielbetrieb
    funktion("spiel/tick", [
        "# /trigger spawn",
        "scoreboard players enable @a spawn",
        f"execute as @a[scores={{spawn=1..}}] run function {NS}:spiel/spawn_befehl",
        "# Schutzzone: auf der Insel wird aus Überleben Abenteuer",
        f"execute if score #schutz hs.config matches 1 run function {NS}:spiel/schutz",
        f"execute unless score #schutz hs.config matches 1 as @a[tag=hs.adv] run function {NS}:spiel/schutz_raus",
        "# Fallschirm für alle, die von der Insel springen",
        f"execute if score #fallschirm hs.config matches 1 as @a[{FALLBAND},tag=!hs.fall] "
        f"run function {NS}:spiel/fallschirm_an",
        "# Himmelstor: wer im Portal steht, kommt hoch (auch falls das Endtransitportal selbst nicht teleportiert)",
        f"execute as @a[{TOR_BEREICH}] at @s if block ~ ~ ~ minecraft:end_gateway run function {NS}:spiel/zum_spawn_still",
        "# Nach dem Tod und beim Einloggen: wer unten unter der Insel steht, kommt hoch",
        f"execute as @e[type=minecraft:player,scores={{hs.tod=1..}}] run function {NS}:spiel/nach_tod",
        f"execute as @a[scores={{hs.weg=1..}}] run function {NS}:spiel/nach_login",
    ])
    funktion("spiel/nach_tod", [
        "# Wiederbelebt am Weltspawn, aber unten gelandet? Dann nach oben. Wer ein eigenes Bett hat, bleibt dort.",
        "scoreboard players set @s hs.tod 0",
        f"execute unless data entity @s respawn if entity @s[{UNTER_INSEL}] run function {NS}:spiel/zum_spawn_still",
    ])
    funktion("spiel/nach_login", [
        "# #login_spawn: 0 = nie, 1 = wer sich unter der Insel ausgeloggt hat, 2 = jeder bei jedem Login",
        "scoreboard players set @s hs.weg 0",
        f"execute if score #login_spawn hs.config matches 2 run function {NS}:spiel/zum_spawn_still",
        f"execute if score #login_spawn hs.config matches 1 if entity @s[{UNTER_INSEL}] run function {NS}:spiel/zum_spawn_still",
    ])
    funktion("spiel/schutz", [
        "tag @a remove hs.in",
        f"tag @a[{ZONE}] add hs.in",
        f"execute as @a[tag=hs.in,gamemode=survival] run function {NS}:spiel/schutz_rein",
        f"execute as @a[tag=hs.adv,tag=!hs.in] run function {NS}:spiel/schutz_raus",
    ])
    funktion("spiel/schutz_rein", [
        "gamemode adventure @s",
        "tag @s add hs.adv",
        f"title @s actionbar {txt({'text': 'Spawn-Insel: Hier kann nichts abgebaut werden', 'color': 'light_purple'})}",
    ])
    funktion("spiel/schutz_raus", [
        "gamemode survival @s[gamemode=adventure]",
        "tag @s remove hs.adv",
    ])
    funktion("spiel/fallschirm_an", [
        "tag @s add hs.fall",
        "effect give @s minecraft:slow_falling 5 0 true",
        f"title @s actionbar {txt({'text': '☂ Fallschirm geöffnet – gute Landung!', 'color': 'aqua'})}",
    ])
    funktion("spiel/halbsekunde", [
        "effect give @a[tag=hs.fall] minecraft:slow_falling 3 0 true",
        "execute as @a[tag=hs.fall] at @s if block ~ ~ ~ minecraft:water run tag @s remove hs.fall",
        "tag @a[tag=hs.fall,nbt={OnGround:1b}] remove hs.fall",
        f"schedule function {NS}:spiel/halbsekunde 10t",
    ])
    funktion("spiel/sekunde", [
        "scoreboard players remove @a[scores={hs.cd=1..}] hs.cd 1",
        f"execute if score #fertig hs.state matches 1 run function {NS}:spiel/pflege",
        f"execute if score #fertig hs.state matches 1 as @a[tag=!hs.gesehen] run function {NS}:spiel/willkommen",
        f"execute if score #starterpaket hs.config matches 1 as @e[type=minecraft:player,tag=!hs.starter] "
        f"run function {NS}:spiel/starterpaket",
        f"execute if score #starterpaket hs.config matches 1 as @e[type=minecraft:player,tag=hs.starter,tag=!hs.werkzeug] "
        f"run function {NS}:spiel/werkzeug_nachreichen",
        f"schedule function {NS}:spiel/sekunde 20t",
    ])
    ax, ay, az = AMBOSSE[0]
    pflege = ["# Abgenutzte Ambosse ersetzen, Monster von der Insel entfernen, Glitzern"]
    pflege.append(f"execute if loaded {ax} {ay} {az} run function {NS}:spiel/ambosse")
    pflege.append(f"kill @e[type=#{NS}:monster,{ZONE}]")
    pflege.append(f"particle minecraft:enchant {BIB[0] + 0.5} {F + 3} {BIB[1] + 0.5} 2.5 1.5 2.5 0.6 25")
    funktion("spiel/pflege", pflege)
    funktion("spiel/ambosse", [f"execute unless block {x} {y} {z} minecraft:anvil "
                               f"run setblock {x} {y} {z} minecraft:anvil[facing=east]" for x, y, z in AMBOSSE])
    funktion("spiel/spawn_befehl", [
        f"execute if score #spawn_befehl hs.config matches 0 run tellraw @s {txt(dict(text='Der Spawn-Befehl ist auf diesem Server ausgeschaltet.', **ROT))}",
        f"execute if score #spawn_befehl hs.config matches 1 if score @s hs.cd matches 1.. run tellraw @s "
        f"{txt(['', dict(text='Bitte warte noch ', **ROT), {'score': {'name': '@s', 'objective': 'hs.cd'}, 'color': 'yellow'}, dict(text=' Sekunden.', **ROT)])}",
        f"execute if score #spawn_befehl hs.config matches 1 unless score @s hs.cd matches 1.. run function {NS}:spiel/zum_spawn",
        "scoreboard players set @s spawn 0",
    ])
    funktion("spiel/zum_spawn", [
        f"function {NS}:spiel/zum_spawn_still",
        "scoreboard players operation @s hs.cd = #abklingzeit hs.config",
        f"tellraw @s {txt({'text': '✦ Zurück auf der Himmelsinsel!', 'color': 'light_purple'})}",
    ])
    funktion("spiel/zum_spawn_still", [
        f"execute in minecraft:overworld run tp @s {SX + 0.5} {SY} {SZ + 0.5} 180 0",
        "execute at @s run playsound minecraft:entity.enderman.teleport player @s ~ ~ ~ 0.7 1.3",
        "execute at @s run particle minecraft:portal ~ ~1 ~ 0.4 0.8 0.4 0.5 40",
    ])
    klick = {"text": "/trigger spawn", "color": "aqua", "underlined": True,
             "click_event": {"action": "run_command", "command": "/trigger spawn"},
             "hover_event": {"action": "show_text", "value": "Klicken, um zum Spawn zu reisen"}}
    funktion("spiel/willkommen", [
        "tag @s add hs.gesehen",
        f"execute if entity @s[{UNTER_INSEL}] run function {NS}:spiel/zum_spawn_still",
        f"tellraw @s {txt(['', {'text': '✦ Willkommen auf der Himmelsinsel! ✦', 'color': 'light_purple', 'bold': True}, {'text': chr(10) + 'In der Zauberbibliothek im Norden gibt es alle Verzauberungsbücher.', 'color': 'gray'}, {'text': chr(10) + 'Runter in die Welt geht es über das Sprungbrett im Süden – mit Fallschirm.', 'color': 'gray'}, {'text': chr(10) + 'Zurück zur Insel: ', 'color': 'gray'}, klick])}",
    ])
    ruestung = [("armor.head", "iron_helmet"), ("armor.chest", "iron_chestplate"),
                ("armor.legs", "iron_leggings"), ("armor.feet", "iron_boots"), ("weapon.offhand", "shield")]
    starter = ["# Einmal pro Spieler. Rüstung und Schild werden direkt angelegt, wenn der Platz frei ist,",
               "# sonst landen sie im Inventar (bei vollem Inventar fallen Sachen vor die Füße).",
               "tag @s add hs.starter"]
    for slot, item in ruestung:
        starter.append(f"execute unless items entity @s {slot} * run item replace entity @s {slot} with minecraft:{item}")
        starter.append(f"execute if items entity @s {slot} * unless items entity @s {slot} minecraft:{item} "
                       f"run give @s minecraft:{item}")
    starter += [f"function {NS}:spiel/werkzeug_geben",
                "give @s minecraft:emerald 64",
                "give @s minecraft:bow",
                "give @s minecraft:arrow 32",
                "give @s minecraft:cooked_beef 16",
                f"tellraw @s {txt(['', {'text': '✦ Starterpaket erhalten: ', 'color': 'gold', 'bold': True}, {'text': 'Eisenrüstung, Schild, Eisenwerkzeuge, Bogen mit 32 Pfeilen, 16 Steaks und 64 Smaragde für die Zauberbibliothek!', 'color': 'yellow'}])}",
                "execute at @s run playsound minecraft:entity.player.levelup player @s ~ ~ ~ 0.8 1.2"]
    funktion("spiel/starterpaket", starter)
    funktion("spiel/werkzeug_geben", [
        "tag @s add hs.werkzeug",
        "give @s minecraft:iron_sword",
        "give @s minecraft:iron_pickaxe",
        "give @s minecraft:iron_axe",
        "give @s minecraft:iron_shovel",
    ])
    funktion("spiel/werkzeug_nachreichen", [
        "# Für alle, die das Starterpaket schon vor den Werkzeugen bekommen haben",
        f"function {NS}:spiel/werkzeug_geben",
        f"tellraw @s {txt(['', {'text': '✦ Nachlieferung zum Starterpaket: ', 'color': 'gold', 'bold': True}, {'text': 'Eisenschwert, -spitzhacke, -axt und -schaufel!', 'color': 'yellow'}])}",
        "execute at @s run playsound minecraft:entity.player.levelup player @s ~ ~ ~ 0.8 1.2",
    ])
    # ---- Admin
    funktion("admin/bauen", [
        "# Startet den Bau in einer bestehenden Welt (in neuen Welten passiert das automatisch)",
        f"execute if score #fertig hs.state matches 1 run tellraw @s {txt({'text': 'Die Insel steht schon. Neu bauen: /function himmelsinsel:admin/neu_bauen', 'color': 'yellow'})}",
        f"execute unless score #fertig hs.state matches 1 if score #stufe hs.state matches ..0 run function {NS}:bau/vorbereiten",
    ])
    funktion("admin/neu_bauen", [
        "# Baut Insel, Händler und Schilder komplett neu (z. B. nach einem Update des Datapacks)",
        "scoreboard players set #fertig hs.state 0",
        f"function {NS}:bau/vorbereiten",
        f"tellraw @a {txt({'text': '[Himmelsinsel] Wird neu gebaut …', 'color': 'light_purple'})}",
    ])
    info = [{"text": "Himmelsinsel – Einstellungen", "color": "light_purple", "bold": True}]
    for key, erkl in [("spawn_befehl", "/trigger spawn erlaubt (1/0)"),
                      ("abklingzeit", "Sekunden zwischen zwei /trigger spawn"),
                      ("schutz", "Insel im Abenteuermodus schützen (1/0)"),
                      ("fallschirm", "Sanfter Fall beim Absprung (1/0)"),
                      ("bodenstation", "Bodenstation beim ersten Bau (1/0)"),
                      ("login_spawn", "Beim Login auf die Insel: 0 nie, 1 wer unten steht, 2 immer"),
                      ("starterpaket", "Starterpaket beim ersten Join (1/0)")]:
        info += [{"text": f"\n#{key} = ", "color": "gray"},
                 {"score": {"name": f"#{key}", "objective": "hs.config"}, "color": "yellow"},
                 {"text": f"  {erkl}", "color": "dark_gray"}]
    info.append({"text": "\nÄndern: /scoreboard players set #<name> hs.config <wert>", "color": "gray"})
    info += [{"text": "\n\nBau fertig: ", "color": "gray"},
             {"score": {"name": "#fertig", "objective": "hs.state"}, "color": "yellow"},
             {"text": "   Insel am Spawn gefunden: ", "color": "gray"},
             {"score": {"name": "#insel", "objective": "hs.state"}, "color": "yellow"},
             {"text": "  (1 = ja)", "color": "dark_gray"}]
    funktion("admin/info", [
        f"execute store success score #insel hs.state if block {SX} {SY - 1} {SZ} minecraft:polished_andesite",
        f"tellraw @s {txt([''] + info)}",
    ])
    funktion("admin/deinstallieren", [
        "# Schaltet alles ab. Insel, Händler und Schilder bleiben stehen.",
        f"schedule clear {NS}:spiel/sekunde",
        f"schedule clear {NS}:spiel/halbsekunde",
        "execute as @a[tag=hs.adv] run gamemode survival @s[gamemode=adventure]",
        "tag @a remove hs.adv",
        "tag @a remove hs.in",
        "tag @a remove hs.fall",
        "tag @a remove hs.gesehen",
        f"forceload remove {x1} {z1} {x2} {z2}",
        "scoreboard objectives remove hs.state",
        "scoreboard objectives remove hs.config",
        "scoreboard objectives remove hs.cd",
        "scoreboard objectives remove spawn",
        "scoreboard objectives remove hs.tod",
        "scoreboard objectives remove hs.weg",
        f"tellraw @s {txt({'text': 'Himmelsinsel deaktiviert. Jetzt noch das Datapack abschalten: /datapack list zeigt den Namen, dann /datapack disable <name>', 'color': 'yellow'})}",
    ])
    # ---- Versionsabhängiges
    funktion("version/spawnpunkt", [
        "# Ab Minecraft 1.21.11: Gamerules heißen jetzt snake_case, Spawn mit Blickrichtung",
        f"setworldspawn {SX} {SY} {SZ} 180 0",
        "gamerule respawn_radius 0",
    ])
    funktion("version/spawnpunkt", [
        "# Minecraft 1.21.5 bis 1.21.10",
        f"setworldspawn {SX} {SY} {SZ}",
        "gamerule spawnRadius 0",
    ], overlay=LEGACY)

    datei(f"data/{NS}/tags/entity_type/monster.json",
          json.dumps({"values": [{"id": f"minecraft:{m}", "required": False} for m in MONSTER]}, indent=2))
    datei("data/minecraft/tags/function/load.json", json.dumps({"values": [f"{NS}:load"]}, indent=2))
    datei("data/minecraft/tags/function/tick.json", json.dumps({"values": [f"{NS}:tick"]}, indent=2))
    datei("pack.mcmeta", json.dumps({
        "pack": {
            "description": [{"text": "Himmelsinsel-Spawn", "color": "light_purple"},
                            {"text": " – schwebender Spawn mit allen Verzauberungsbüchern", "color": "gray"}],
            "pack_format": FORMAT_MIN,
            "supported_formats": [FORMAT_MIN, FORMAT_MAX],
            "min_format": FORMAT_MIN,
            "max_format": FORMAT_MAX,
        },
        "overlays": {"entries": [{"directory": LEGACY, "formats": [FORMAT_MIN, LEGACY_MAX],
                                  "min_format": FORMAT_MIN, "max_format": LEGACY_MAX}]},
    }, indent=2, ensure_ascii=False))


# ---------------------------------------------------------------- Zusammenbauen

def main():
    insel, lichter = bauplan.himmelsinsel()
    station = bauplan.bodenstation()
    print(f"Insel: {len(insel.b)} Blöcke, davon {lichter} unsichtbare Lichter")

    raeum, (y1, y2) = raeumen(insel)
    teile = [["# Luftraum leeren"] + raeum]
    teile += in_teile(befehle(insel))
    for i, t in enumerate(teile, 1):
        funktion(f"bau/teil_{i:02d}", t)
    print(f"Bau in {len(teile)} Teilen, {sum(len(t) for t in teile)} Befehle, Luftraum y {y1}–{y2}")

    st = ["# Wird am Boden unter dem Sprungbrett ausgeführt (~ ~ ~ = erste Luft über dem Gelände)",
          "fill ~-6 ~ ~-6 ~6 ~7 ~6 minecraft:air",
          "# Fundament: Löcher und Wasser unter der Plattform füllen"]
    for z in range(-5, 6):
        breite = int(math.floor(math.sqrt(max(0, 5.2 ** 2 - z * z))))
        st.append(f"fill {koord(-breite, True)} ~-6 {koord(z, True)} {koord(breite, True)} ~-2 {koord(z, True)} "
                  "minecraft:dirt replace #minecraft:replaceable")
    st += [b for b, _ in befehle(station, relativ=True)]
    tor = f"minecraft:end_gateway{{ExactTeleport:1b,exit_portal:[I;{SX},{SY},{SZ}]}}"
    for x, y, z in bauplan.TOR:
        st.append(f"setblock {koord(x, True)} {koord(y, True)} {koord(z, True)} {tor}")
    st += ["kill @e[type=minecraft:text_display,tag=hs.bodenschild,distance=..12]",
           "summon minecraft:text_display ~0.5 ~4.7 ~-3.5 {Tags:[\"hs.bodenschild\"],billboard:\"vertical\","
           f"shadow:1b,text:{txt(['', {'text': 'Himmelstor ↑', 'color': 'light_purple', 'bold': True}, {'text': chr(10) + 'Hinein und zurück zur Spawn-Insel', 'color': 'white'}])}}}"]
    funktion("bau/bodenstation", st)

    lichtpunkte = [(x, z) for x in range(-30, 31, 10) for z in range(-30, 31, 10) if math.hypot(x, z) <= 34]
    feste_funktionen(lichtpunkte, len(teile))

    for h in HAENDLER:
        funktion(f"haendler/{h['id']}", haendler_befehle(h, neu=True))
        if any(e in NUR_NEU for e, _ in h["buecher"]):
            funktion(f"haendler/{h['id']}", haendler_befehle(h, neu=False), overlay=LEGACY)
    funktion("schilder", schilder())

    if ORDNER:
        if os.path.isdir(ORDNER):
            shutil.rmtree(ORDNER)
        for pfad, inhalt in dateien.items():
            voll = os.path.join(ORDNER, pfad)
            os.makedirs(os.path.dirname(voll), exist_ok=True)
            with open(voll, "w", encoding="utf-8", newline="\n") as f:
                f.write(inhalt)
        print(f"{len(dateien)} Dateien → {ORDNER}")
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        for pfad in sorted(dateien):
            info = zipfile.ZipInfo(pfad, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(info, dateien[pfad].encode("utf-8"))
    print(f"Zip → {os.path.normpath(ZIP)} ({os.path.getsize(ZIP) // 1024} KB, {len(dateien)} Dateien)")


if __name__ == "__main__":
    main()
