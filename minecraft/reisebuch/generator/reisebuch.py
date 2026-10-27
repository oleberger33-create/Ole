"""Baut das Datapack „Reisebuch“: ein Buch mit anklickbaren Zielen, ein Klick teleportiert zur Farm.

Aufruf:  python3 reisebuch.py <ziele.json> [zip-datei] [entpackt-ordner]

ziele.json:  {"spieler": ["Name", …] oder "alle",
              "ziele": [{"name": "XP-Farm", "pos": [x, y, z], "blick": [gier, neigung], "info": "Text"}, …]}

Ein Klick im Buch führt „/trigger reise set <Nummer>“ aus; das darf jeder Spieler ohne Operator-Rechte.
Das Pack schaltet den Trigger jeden Tick frei und teleportiert, wer ihn gesetzt hat (immer in die Oberwelt,
auch aus dem Nether). „/trigger reise set 99“ gibt ein neues Buch, falls eins verloren geht.
Nur die Spieler aus „spieler“ dürfen das Buch haben und benutzen; alle anderen verlieren es sofort. Mit "alle" bekommt
jeder Spieler das Buch, auch wer neu auf den Server kommt. Das Buch trägt
custom_data {reise:1b}: Stirbt ein Spieler, verschwindet es aus dem Fallengelassenen und er bekommt beim Wiederbeleben
ein neues. Der Rest des Inventars fällt wie immer.
"""
import json
import os
import shutil
import sys
import zipfile

NS = "reise"
FORMAT_MIN, FORMAT_MAX = 71, 121
KONFIG = json.load(open(sys.argv[1]))
ZIELE, SPIELER = KONFIG["ziele"], KONFIG["spieler"]
HIER = os.path.dirname(os.path.abspath(__file__))
ZIP = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HIER, "..", "Reisebuch.zip")
ORDNER = sys.argv[3] if len(sys.argv) > 3 else None
NEUES_BUCH = 99
dateien = {}


def datei(pfad, zeilen):
    text = "\n".join(zeilen) if isinstance(zeilen, list) else zeilen
    dateien[pfad] = text.rstrip("\n") + "\n"


def funktion(name, zeilen):
    datei(f"data/{NS}/function/{name}.mcfunction", zeilen)


def snbt(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace(chr(10), "\\n") + '"'


def zeile(nr, ziel):
    return (f'{{text:{snbt("▸ " + ziel["name"] + chr(10))},color:"dark_aqua",'
            f'click_event:{{action:"run_command",command:"/trigger {NS} set {nr}"}},'
            f'hover_event:{{action:"show_text",value:{snbt(ziel["info"])}}}}}')


seite = ([f'{{text:{snbt("Reisebuch" + chr(10) + chr(10))},bold:true}}']
         + [zeile(nr, z) for nr, z in enumerate(ZIELE, 1)]
         + [f'{{text:{snbt(chr(10) + "Klick = Teleport" + chr(10) + "Neues Buch: /trigger reise set 99")},color:"gray"}}'])
MARKE = f"minecraft:custom_data={{{NS}:1b}}"
UNSER = f"minecraft:written_book[{MARKE.replace('=', '~', 1)}]"     # Item-Prädikat: „hat diese Daten“
buch = (f'minecraft:written_book[{MARKE},minecraft:written_book_content={{title:"Reisebuch",author:"Server",'
        f'pages:[[{",".join(seite)}]]}}]')
OK = f"tag={NS}.ok"

if SPIELER == "alle":
    tick = [f"tag @a add {NS}.ok"]
else:
    tick = [f"tag @a[name={n}] add {NS}.ok" for n in SPIELER] + [f"clear @a[tag=!{NS}.ok] {UNSER}"]
tick += [
         f"scoreboard players enable @a[{OK}] {NS}"]
for nr, z in enumerate(ZIELE, 1):
    x, y, zz = z["pos"]
    gier, neigung = z.get("blick", [0, 0])
    tick.append(f"execute as @a[{OK},scores={{{NS}={nr}}}] in minecraft:overworld run tp @s {x} {y} {zz} {gier} {neigung}")
tick += [f"execute as @a[{OK},scores={{{NS}={NEUES_BUCH}}}] run function {NS}:buch",
         f"scoreboard players reset @a[scores={{{NS}=1..}}] {NS}",
         "# Gestorben: das fallengelassene Buch weg, nach dem Wiederbeleben ein neues (@e findet nur Lebende)",
         f"execute if entity @a[scores={{{NS}.tod=1..}}] run kill @e[type=minecraft:item,nbt={{Item:{{components:{{\"minecraft:custom_data\":{{{NS}:1b}}}}}}}}]",
         f"execute as @e[type=minecraft:player,{OK},scores={{{NS}.tod=1..}}] run function {NS}:buch",
         f"scoreboard players reset @e[type=minecraft:player,scores={{{NS}.tod=1..}}] {NS}.tod",
         f"execute as @a[{OK},tag=!{NS}.v2] run function {NS}:buch",
         f"tag @a[{OK}] add {NS}.v2"]

funktion("load", [f"scoreboard objectives add {NS} trigger \"Reisebuch\"",
                  f"scoreboard objectives add {NS}.tod deathCount"])
funktion("tick", tick)
funktion("buch", [f"clear @s {UNSER}", f"give @s {buch}"])

datei("data/minecraft/tags/function/load.json", json.dumps({"values": [f"{NS}:load"]}, indent=2))
datei("data/minecraft/tags/function/tick.json", json.dumps({"values": [f"{NS}:tick"]}, indent=2))
datei("pack.mcmeta", json.dumps({"pack": {
    "description": "Reisebuch", "pack_format": FORMAT_MIN, "supported_formats": [FORMAT_MIN, FORMAT_MAX],
    "min_format": FORMAT_MIN, "max_format": FORMAT_MAX}}, indent=2))

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
        zf.writestr(zipfile.ZipInfo(pfad, date_time=(2026, 1, 1, 0, 0, 0)), dateien[pfad].encode("utf-8"))
print(f"{len(ZIELE)} Ziele")
