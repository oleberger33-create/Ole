"""Fehlende Geister nachziehen (Schritt 6 der Server-Version, siehe README).

Aufruf: python3 nachziehen.py <geister.zip> <ausgabe.zip>

Bisher erschienen die Geister nur einmal, wenn ein Teil beginnt. Wird ein Block erst danach entfernt (weggegraben,
von Wasser ersetzt), zählt die Prüfung ihn als fehlend, aber kein Geist zeigt ihn.
- z/: ein Geist entsteht nur, wenn an der Stelle noch keiner ist (sonst gäbe es beim Nachziehen doppelte).
- sekunde: ein Takt-Zähler #takt läuft 0, 1, 2.
- plan/sekunde: fehlt etwas, ruft jeder 3. Takt die zeigen-Funktion des Teils noch einmal auf (ohne die alten
  Geister zu löschen) – sie ergänzt nur die fehlenden.
"""
import re, sys, zipfile

NS = 'ofh'
ein, aus = sys.argv[1], sys.argv[2]
FREI = f'unless entity @e[type=minecraft:block_display,tag={NS}_g,distance=..0.05]'
GEIST = re.compile(r'^(execute .*?) run summon minecraft:block_display ~0\.1 ~0\.1 ~0\.1 (\{.*)$')
WAHL = re.compile(r'^(execute .*?) run (function ' + NS + r':wahl/geist with storage .*)$')
zahl = {'geist': 0, 'wahl': 0, 'takt': 0, 'nachziehen': 0}

with zipfile.ZipFile(ein) as zin, zipfile.ZipFile(aus, 'w', zipfile.ZIP_DEFLATED) as zout:
    for info in zin.infolist():
        daten = zin.read(info.filename)
        n = info.filename
        if re.match(rf'data/{NS}/function/z/\d+\.mcfunction$', n):
            neu = []
            for z in daten.decode('utf-8').splitlines():
                g, w = GEIST.match(z), WAHL.match(z)
                if g:
                    z = f'{g.group(1)} positioned ~0.1 ~0.1 ~0.1 {FREI} run summon minecraft:block_display ~ ~ ~ {g.group(2)}'
                    zahl['geist'] += 1
                elif w:
                    z = f'{w.group(1)} positioned ~0.1 ~0.1 ~0.1 {FREI} positioned ~-0.1 ~-0.1 ~-0.1 run {w.group(2)}'
                    zahl['wahl'] += 1
                neu.append(z)
            daten = ('\n'.join(neu) + '\n').encode('utf-8')
        elif n == f'data/{NS}/function/sekunde.mcfunction':
            t = daten.decode('utf-8')
            t = (f'scoreboard players add #takt {NS} 1\n'
                 f'execute if score #takt {NS} matches 3.. run scoreboard players set #takt {NS} 0\n') + t
            daten = t.encode('utf-8')
            zahl['takt'] += 1
        elif n == f'data/{NS}/function/plan/sekunde.mcfunction':
            t = daten.decode('utf-8')
            alt = f'function {NS}:plan/pruefen_m with storage {NS}:tmp d'
            assert alt in t, 'plan/sekunde: Prüfaufruf nicht gefunden'
            t = t.replace(alt, alt + f'\nexecute if score #fehlt {NS} matches 1.. if score #takt {NS} matches 0 run '
                                     f'function {NS}:plan/zeigen_m with storage {NS}:tmp d', 1)
            daten = t.encode('utf-8')
            zahl['nachziehen'] += 1
        zout.writestr(info, daten)

print(zahl)
assert zahl['geist'] > 100 and zahl['takt'] == 1 and zahl['nachziehen'] == 1, 'nicht alles umgebaut'
