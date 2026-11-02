#!/usr/bin/env python3
"""Ole's Farmhelper (Datapack OlesFarmhelper.zip, Namespace ofh) auf EINEN Spieler beschraenken.

Nur dieser Spieler bekommt das Farmhelper-Item, nur er kann es benutzen (Rechtsklick-Menue, /trigger ofh.t);
das Craft-Rezept wird entfernt, damit niemand sonst eines bauen kann. Alle anderen 6000+ Dateien bleiben unveraendert.

Run: python3 farmhelper_nur_fuer.py <original.zip> <spielername> <ausgabe.zip>
Item nochmal bekommen (als Op):  /function ofh:item
"""
import sys, zipfile

src, name, dst = sys.argv[1], sys.argv[2], sys.argv[3]
P = f'@a[name={name}]'
TICK = f"""scoreboard players enable {P} ofh.t
execute as @a[name={name},scores={{ofh.klick=1..}}] if items entity @s weapon.mainhand *[minecraft:custom_data~{{ofh:1b}}] run function ofh:klick
scoreboard players reset @a[scores={{ofh.klick=1..}}] ofh.klick
execute as {P} unless score @s ofh.id matches 1.. run function ofh:neue_id
execute as @a[name={name},tag=!ofh.v1] run function ofh:item
tag {P} add ofh.v1
execute as @a[name={name},scores={{ofh.t=1..}}] at @s run function ofh:trigger
scoreboard players reset @a[scores={{ofh.t=1..}}] ofh.t
"""
n_in = n_out = 0
with zipfile.ZipFile(src) as zin, zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zout:
    for info in zin.infolist():
        n_in += 1
        if info.filename.endswith('/'):
            continue
        if info.filename == 'data/ofh/recipe/farmhelper.json':
            continue                                  # kein Rezept mehr
        data = zin.read(info.filename)
        if info.filename == 'data/ofh/function/tick.mcfunction':
            data = TICK.encode('utf-8')
        if info.filename == 'pack.mcmeta':
            data = data.replace(b"Ole's Farmhelper", f"Ole's Farmhelper (nur {name})".encode('utf-8'))
        zout.writestr(info.filename, data)
        n_out += 1
print(f'{n_in} Eintraege gelesen, {n_out} geschrieben -> {dst} (nur fuer {name})')
