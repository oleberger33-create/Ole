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

Eigene Punkte: Unter den Farmen öffnet „Meine Punkte“ ein zweites Fenster mit 5 Plätzen je Spieler (Haus, Basis …).
„Hier speichern“ merkt sich die jetzige Stelle mit Blickrichtung und Dimension (auch Nether und End); Namen und Bild
kommen aus einer festen Liste, denn Spieler ohne Operator-Rechte können dem Server nur Zahlen schicken (/trigger).
Der Speichern-Knopf setzt den Trigger auf 1PNN (P = Platz, NN = Name), Löschen auf 2P00, Hinreisen auf 10P.
Jeder Spieler bekommt eine feste Nummer (Scoreboard reise.id); seine Punkte liegen im Storage reise:punkte unter p<id>.
Die Fenster mit den eigenen Punkten baut das Pack für jeden Spieler neu (Makro-Funktionen mit seinen Daten).
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
MEINE, FARMEN, SPEICHERN = 98, 97, 96                                  # Trigger, die ein Fenster öffnen
PLAETZE = 5
NAMEN = [("Haus", "oak_door"), ("Basis", "iron_door"), ("Farm", "wheat"), ("Mine", "iron_pickaxe"),
         ("Lager", "bundle"), ("Portal", "ender_pearl"), ("Dorf", "emerald"), ("Turm", "spyglass"),
         ("Hafen", "oak_boat"), ("Punkt", "map")]
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
    "actions": [knopf(nr, z) for nr, z in enumerate(ZIELE, 1)] + [
        {"label": [symbol("compass_16"), {"text": "  Meine Punkte", "color": "yellow"}],
         "tooltip": {"text": "Eigene Punkte: Haus, Basis … speichern und hinreisen"}, "width": 150,
         "action": {"type": "run_command", "command": f"/trigger {NS} set {MEINE}"}}],
    "exit_action": {"label": {"translate": "gui.done"}, "width": 150},
}


def befehl(nr):
    return {"type": "run_command", "command": f"/trigger {NS} set {nr}"}


meine = {   # Platzhalter $(n1) … kommen beim Öffnen aus den Daten des Spielers (Makro)
    "type": "minecraft:multi_action",
    "title": {"text": "Meine Punkte", "bold": True},
    "external_title": {"text": "Meine Punkte"},
    "body": [{"type": "minecraft:plain_message", "width": 300,
              "contents": {"text": "Klick auf einen Punkt, um hinzureisen. Neue Punkte speicherst du dort, "
                                   "wo du gerade stehst.", "color": "gray"}}],
    "can_close_with_escape": True, "pause": False, "after_action": "close", "columns": 1,
    "actions": [{"label": [{"type": "object", "object": "atlas", "atlas": "minecraft:items", "sprite": f"$(i{k})"},
                           {"text": f"  $(n{k})", "color": f"$(c{k})"}],
                 "tooltip": {"text": f"Platz {k}"}, "width": 200, "action": befehl(100 + k)}
                for k in range(1, PLAETZE + 1)] + [
        {"label": {"text": "+ Hier speichern", "color": "green"}, "width": 200, "action": befehl(SPEICHERN)},
        {"label": {"text": "Zurück zu den Farmen"}, "width": 200, "action": befehl(FARMEN)}],
    "exit_action": {"label": {"translate": "gui.done"}, "width": 200},
}
speichern = {
    "type": "minecraft:multi_action",
    "title": {"text": "Punkt speichern", "bold": True},
    "body": [{"type": "minecraft:plain_message", "width": 300,
              "contents": {"text": "Speichert die Stelle, an der du gerade stehst, mit Blickrichtung.", "color": "gray"}}],
    "inputs": [
        {"type": "minecraft:single_option", "key": "platz", "label": {"text": "Platz"}, "width": 200,
         "options": [{"id": str(k), "display": {"text": f"{k}: $(n{k})"}, **({"initial": True} if k == 1 else {})}
                     for k in range(1, PLAETZE + 1)]},
        {"type": "minecraft:single_option", "key": "name", "label": {"text": "Name"}, "width": 200,
         "options": [{"id": f"{m:02d}", "display": {"text": n}} for m, (n, _) in enumerate(NAMEN, 1)]}],
    "can_close_with_escape": True, "pause": False, "after_action": "close", "columns": 1,
    "actions": [
        {"label": {"text": "Speichern", "color": "green"}, "width": 200,
         "action": {"type": "dynamic/run_command", "template": f"/trigger {NS} set 1$(platz)$(name)"}},
        {"label": {"text": "Platz leeren", "color": "red"}, "width": 200,
         "action": {"type": "dynamic/run_command", "template": f"/trigger {NS} set 2$(platz)00"}},
        {"label": {"text": "Zurück"}, "width": 200, "action": befehl(MEINE)}],
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
tick += [f"execute as @a[{OK}] unless score @s {NS}.id matches 1.. run function {NS}:neue_id",
         f"execute as @a[{OK},scores={{{NS}={MEINE}}}] run function {NS}:meine",
         f"execute as @a[{OK},scores={{{NS}={FARMEN}}}] run function {NS}:fenster",
         f"execute as @a[{OK},scores={{{NS}={SPEICHERN}}}] run function {NS}:speichern_fenster"]
for k in range(1, PLAETZE + 1):
    tick += [f"execute as @a[{OK},scores={{{NS}={100 + k}}}] run function {NS}:hin {{platz:{k}}}",
             f"execute as @a[{OK},scores={{{NS}={2000 + k * 100}}}] run function {NS}:leeren {{platz:{k}}}"]
    for m, (n, item) in enumerate(NAMEN, 1):
        tick.append(f"execute as @a[{OK},scores={{{NS}={1000 + k * 100 + m}}}] run function {NS}:merken "
                    f"{{platz:{k},name:\"{n}\",icon:\"item/{item}\"}}")
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
                  f"scoreboard objectives add {NS}.id dummy",
                  f"scoreboard objectives add {NS}.klick minecraft.used:minecraft.carrot_on_a_stick"])
funktion("tick", tick)
funktion("auge", [f"clear @s {UNSER}", f"give @s {auge}"])
# Der Dialog steht direkt im Befehl: Dialoge aus Datapacks lädt der Server nur beim Start, nicht bei /reload
funktion("fenster", [f"dialog show @s {json.dumps(dialog, ensure_ascii=False)}"])

# Eigene Punkte. reise:tmp ist Arbeitsplatz: id = Nummer des Spielers, p = seine Daten
LEER = {f"{a}{k}": v for k in range(1, PLAETZE + 1) for a, v in (("n", "leer"), ("i", "item/barrier"), ("c", "gray"))}
funktion("neue_id", [f"scoreboard players add #naechste {NS}.id 1",
                     f"scoreboard players operation @s {NS}.id = #naechste {NS}.id",
                     f"function {NS}:laden",
                     f"execute unless data storage {NS}:tmp p.n1 run function {NS}:anlegen with storage {NS}:tmp"])
funktion("anlegen", [f"$data modify storage {NS}:punkte p$(id) set value {json.dumps(LEER)}"])
funktion("laden", [f"execute store result storage {NS}:tmp id int 1 run scoreboard players get @s {NS}.id",
                   f"data remove storage {NS}:tmp p",
                   f"function {NS}:laden_m with storage {NS}:tmp"])
funktion("laden_m", [f"$data modify storage {NS}:tmp p set from storage {NS}:punkte p$(id)"])
funktion("meine", [f"function {NS}:laden", f"function {NS}:meine_m with storage {NS}:tmp p"])
funktion("meine_m", [f"$dialog show @s {json.dumps(meine, ensure_ascii=False)}"])
# Die Vorlage des Speichern-Knopfs enthält selbst $(platz) und $(name) (füllt der Dialog aus); damit das Makro sie
# stehen lässt, bekommt es sie als Werte mit, die genau so lauten
funktion("speichern_fenster", [f"function {NS}:laden",
                               f"data modify storage {NS}:tmp p.platz set value \"$(platz)\"",
                               f"data modify storage {NS}:tmp p.name set value \"$(name)\"",
                               f"function {NS}:speichern_m with storage {NS}:tmp p"])
funktion("speichern_m", [f"$dialog show @s {json.dumps(speichern, ensure_ascii=False)}"])
funktion("merken", [
    f"$data modify storage {NS}:tmp a set value {{platz:$(platz),name:\"$(name)\",icon:\"$(icon)\"}}",
    f"execute store result storage {NS}:tmp a.id int 1 run scoreboard players get @s {NS}.id",
    f"data modify storage {NS}:tmp neu set value {{}}",
    f"execute store result storage {NS}:tmp neu.x double 0.01 run data get entity @s Pos[0] 100",
    f"execute store result storage {NS}:tmp neu.y double 0.01 run data get entity @s Pos[1] 100",
    f"execute store result storage {NS}:tmp neu.z double 0.01 run data get entity @s Pos[2] 100",
    f"execute store result storage {NS}:tmp neu.gier double 0.01 run data get entity @s Rotation[0] 100",
    f"execute store result storage {NS}:tmp neu.neigung double 0.01 run data get entity @s Rotation[1] 100",
    f"data modify storage {NS}:tmp neu.dim set from entity @s Dimension",
    f"function {NS}:merken_m with storage {NS}:tmp a",
    f"function {NS}:meine"])
funktion("merken_m", [f"$data modify storage {NS}:punkte p$(id).s$(platz) set from storage {NS}:tmp neu",
                      f"$data modify storage {NS}:punkte p$(id).n$(platz) set value \"$(name)\"",
                      f"$data modify storage {NS}:punkte p$(id).i$(platz) set value \"$(icon)\"",
                      f"$data modify storage {NS}:punkte p$(id).c$(platz) set value \"white\"",
                      "$title @s actionbar {text:\"Gespeichert: $(name)\",color:\"green\"}"])
funktion("leeren", [f"$data modify storage {NS}:tmp a set value {{platz:$(platz)}}",
                    f"execute store result storage {NS}:tmp a.id int 1 run scoreboard players get @s {NS}.id",
                    f"function {NS}:leeren_m with storage {NS}:tmp a",
                    f"function {NS}:meine"])
funktion("leeren_m", [f"$data remove storage {NS}:punkte p$(id).s$(platz)",
                      f"$data modify storage {NS}:punkte p$(id).n$(platz) set value \"leer\"",
                      f"$data modify storage {NS}:punkte p$(id).i$(platz) set value \"item/barrier\"",
                      f"$data modify storage {NS}:punkte p$(id).c$(platz) set value \"gray\""])
funktion("hin", [f"function {NS}:laden",
                 f"$execute if data storage {NS}:tmp p.s$(platz) run return run function {NS}:hin_m with storage {NS}:tmp p.s$(platz)",
                 "title @s actionbar {text:\"Dieser Platz ist leer\",color:\"gray\"}"])
funktion("hin_m", ["$execute in $(dim) run tp @s $(x) $(y) $(z) $(gier) $(neigung)"])
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
