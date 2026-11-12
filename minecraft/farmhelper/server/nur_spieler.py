#!/usr/bin/env python3
"""Ole's Farmhelper auf einen Spieler beschränken – die Geisterblöcke bleiben echte Blöcke (Schritt 2 der Server-Version).

Gegenstück zu farmhelper_nur_fuer.py (Branch speedrun-plan), aber ohne die Partikel-Umwandlung: Die Geister bleiben
leuchtende, leicht verkleinerte Blöcke (block_display) wie im Original – die sieht in Vanilla jeder Spieler in der
Nähe. Beschränkt wird nur, wer den Farmhelper bekommt und benutzen darf:

* Nur dieser Spieler bekommt das Farmhelper-Item, nur er kann es benutzen (Rechtsklick-Menü, /trigger ofh.t).
* Das Craft-Rezept wird entfernt.

Aufruf: python3 nur_spieler.py <original.zip> <spielername> <ausgabe.zip>
Danach mehrere_spieler.py für weitere Spieler (ersetzt @a[name=<spielername>] im tick durch eine Namensliste).
"""
import sys
import zipfile

ein, name, aus = sys.argv[1], sys.argv[2], sys.argv[3]
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
zin = zipfile.ZipFile(ein)
alt_tick = zin.read('data/ofh/function/tick.mcfunction').decode('utf-8')
assert 'function ofh:klick' in alt_tick and 'function ofh:trigger' in alt_tick, 'unbekannter tick'
n = 0
with zipfile.ZipFile(aus, 'w', zipfile.ZIP_DEFLATED) as zout:
    for info in zin.infolist():
        if info.filename.endswith('/') or info.filename == 'data/ofh/recipe/farmhelper.json':
            continue
        daten = zin.read(info.filename)
        if info.filename == 'data/ofh/function/tick.mcfunction':
            daten = TICK.encode('utf-8')
        elif info.filename == 'pack.mcmeta':
            daten = daten.replace(b"Ole's Farmhelper", f"Ole's Farmhelper (nur {name})".encode('utf-8'))
        zout.writestr(info.filename, daten)
        n += 1
print(f'{n} Dateien, Geisterblöcke bleiben Blöcke, nur {name} -> {aus}')
