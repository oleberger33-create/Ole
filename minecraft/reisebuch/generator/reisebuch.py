"""Baut das Datapack „Reisebuch“: ein Enderauge, Rechtsklick öffnet ein Fenster mit allen Farmen, ein Klick teleportiert.

Aufruf:  python3 reisebuch.py <ziele.json> [zip-datei] [entpackt-ordner]

ziele.json:  {"spieler": ["Name", …] oder "alle",
              "ziele": [{"name": "XP-Farm", "pos": [x, y, z], "blick": [gier, neigung], "info": "Text",
                         "symbol": "experience_bottle"}, …]}
"symbol" ist ein Item, dessen Bild vor dem Namen steht (Sprite aus dem Item-Atlas, item/<symbol>).

Das Auge ist ein Karottenstock, der wie ein Enderauge aussieht (item_model): Ein echtes Enderauge würde beim Rechtsklick
weggeworfen. Den Rechtsklick zählt die Statistik „Karottenstock benutzt“; hält der Spieler dabei das Auge, zeigt das
Pack den Dialog (das eingebaute Fenster von Minecraft, Knöpfe in zwei Spalten, beim Draufzeigen die Beschreibung).
Ein Knopf führt „/trigger reise set <Nummer>“ aus; das darf jeder Spieler ohne Operator-Rechte. Das Pack teleportiert,
wer den Trigger gesetzt hat (immer in die Oberwelt, auch aus dem Nether). „/trigger reise set 99“ gibt ein neues Auge.
Nur die Spieler aus „spieler“ dürfen das Auge haben und benutzen; alle anderen verlieren es sofort. Mit "alle" bekommt
jeder Spieler eins, auch wer neu auf den Server kommt. Das Auge (wie früher das Buch) trägt custom_data {reise:1b}:
Stirbt ein Spieler, verschwindet es aus dem Fallengelassenen und er bekommt beim Wiederbeleben ein neues. Wer noch das
alte Buch hat, bekommt es gegen das Auge getauscht.
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
NEUES_AUGE = 99
VERSION = 3                     # erhöhen, wenn alle ein neues Auge bekommen sollen
dateien = {}


def datei(pfad, zeilen):
    text = "\n".join(zeilen) if isinstance(zeilen, list) else zeilen
    dateien[pfad] = text.rstrip("\n") + "\n"


def funktion(name, zeilen):
    datei(f"data/{NS}/function/{name}.mcfunction", zeilen)


def symbol(item):
    return {"type": "object", "object": "atlas", "atlas": "minecraft:items", "sprite": f"item/{item}"}


def knopf(nr, ziel):
    return {"label": [symbol(ziel.get("symbol", "ender_eye")), {"text": "  " + ziel["name"]}],
            "tooltip": {"text": ziel["info"]}, "width": 150,
            "action": {"type": "run_command", "command": f"/trigger {NS} set {nr}"}}


dialog = {
    "type": "minecraft:multi_action",
    "title": {"text": "Farmen", "bold": True},
    "external_title": {"text": "Reiseauge"},
    "body": [{"type": "minecraft:plain_message", "width": 300,
              "contents": {"text": "Klick auf ein Ziel, um dorthin zu reisen.", "color": "gray"}}],
    "can_close_with_escape": True,
    "pause": False,
    "after_action": "close",
    "columns": 2,
    "actions": [knopf(nr, z) for nr, z in enumerate(ZIELE, 1)],
    "exit_action": {"label": {"translate": "gui.done"}, "width": 150},
}
MARKE = f"minecraft:custom_data={{{NS}:1b}}"
UNSER = f"*[{MARKE.replace('=', '~', 1)}]"                             # Item-Prädikat: jedes Item mit diesen Daten
auge = (f'minecraft:carrot_on_a_stick[{MARKE},minecraft:item_model="minecraft:ender_eye",'
        f'minecraft:item_name="Reiseauge",minecraft:enchantment_glint_override=true,'
        f'minecraft:lore=[{{text:"Rechtsklick: alle Farmen",color:"gray",italic:false}}]]')
OK = f"tag={NS}.ok"
NEU = f"{NS}.v{VERSION}"

if SPIELER == "alle":
    tick = [f"tag @a add {NS}.ok"]
else:
    tick = [f"tag @a[name={n}] add {NS}.ok" for n in SPIELER] + [f"clear @a[tag=!{NS}.ok] {UNSER}"]
tick += [f"scoreboard players enable @a[{OK}] {NS}",
         "# Rechtsklick mit dem Auge: Fenster auf",
         f"execute as @a[{OK},scores={{{NS}.klick=1..}}] if items entity @s weapon.* {UNSER} run function {NS}:fenster",
         f"scoreboard players reset @a[scores={{{NS}.klick=1..}}] {NS}.klick"]
for nr, z in enumerate(ZIELE, 1):
    x, y, zz = z["pos"]
    gier, neigung = z.get("blick", [0, 0])
    tick.append(f"execute as @a[{OK},scores={{{NS}={nr}}}] in minecraft:overworld run tp @s {x} {y} {zz} {gier} {neigung}")
tick += [f"execute as @a[{OK},scores={{{NS}={NEUES_AUGE}}}] run function {NS}:auge",
         f"scoreboard players reset @a[scores={{{NS}=1..}}] {NS}",
         "# Gestorben: das fallengelassene Auge weg, nach dem Wiederbeleben ein neues (@e findet nur Lebende)",
         f"execute if entity @a[scores={{{NS}.tod=1..}}] run kill @e[type=minecraft:item,nbt={{Item:{{components:{{\"minecraft:custom_data\":{{{NS}:1b}}}}}}}}]",
         f"execute as @e[type=minecraft:player,{OK},scores={{{NS}.tod=1..}}] run function {NS}:auge",
         f"scoreboard players reset @e[type=minecraft:player,scores={{{NS}.tod=1..}}] {NS}.tod",
         f"execute as @a[{OK},tag=!{NEU}] run function {NS}:auge",
         f"tag @a[{OK}] add {NEU}"]

funktion("load", [f"scoreboard objectives add {NS} trigger \"Reisebuch\"",
                  f"scoreboard objectives add {NS}.tod deathCount",
                  f"scoreboard objectives add {NS}.klick minecraft.used:minecraft.carrot_on_a_stick"])
funktion("tick", tick)
funktion("auge", [f"clear @s {UNSER}", f"give @s {auge}"])
# Der Dialog steht direkt im Befehl: Dialoge aus Datapacks lädt der Server nur beim Start, nicht bei /reload
funktion("fenster", [f"dialog show @s {json.dumps(dialog, ensure_ascii=False)}"])
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
