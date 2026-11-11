"""Gibt den Farmhelper mehreren Spielern frei (Schritt 3 der Server-Version, siehe README).

Aufruf: python3 mehrere_spieler.py <nur_fuer.zip> <ausgabe.zip> <Name1> [<Name2> ...]

Eingabe ist die Ausgabe von farmhelper_nur_fuer.py (Branch speedrun-plan, smp/tools/) für <Name1>.
- tick: Wer den Farmhelper benutzen darf, steht in einer Namensliste (Tag ofh.darf), statt fest @a[name=<Name1>].
- Geisterblöcke und Hinweise: gehen an den Besitzer des jeweiligen Plans (Tag ofh.sieht, gesetzt in plan/daten),
  statt fest an <Name1>. Jeder sieht nur seine eigenen Pläne; alle anderen sehen nichts.
"""
import json, re, sys, zipfile

ein, aus, namen = sys.argv[1], sys.argv[2], sys.argv[3:]
erster = namen[0]
with zipfile.ZipFile(ein) as zf:
    dateien = {n: zf.read(n) for n in zf.namelist() if not n.endswith('/')}

TICK = 'data/ofh/function/tick.mcfunction'
DATEN = 'data/ofh/function/plan/daten.mcfunction'
zaehler = {'tick': 0, 'partikel': 0, 'tellraw': 0}
for rel, inhalt in list(dateien.items()):
    if not rel.endswith('.mcfunction') or f'name={erster}' not in inhalt.decode('utf-8'):
        continue
    t = inhalt.decode('utf-8')
    if rel == TICK:
        zaehler['tick'] += t.count(f'@a[name={erster}')
        t = t.replace(f'@a[name={erster},', '@a[tag=ofh.darf,').replace(f'@a[name={erster}]', '@a[tag=ofh.darf]')
        kopf = ['# Wer den Farmhelper benutzen darf (Namen genau wie im Spiel)', 'tag @a[tag=ofh.darf] remove ofh.darf']
        t = '\n'.join(kopf + [f'tag @a[name={n}] add ofh.darf' for n in namen]) + '\n' + t
    else:
        zaehler['partikel'] += t.count(f'force @a[name={erster}]')
        zaehler['tellraw'] += t.count(f'tellraw @a[name={erster}]')
        t = t.replace(f'force @a[name={erster}]', 'force @a[tag=ofh.sieht]')
        t = t.replace(f'tellraw @a[name={erster}]', 'tellraw @a[tag=ofh.sieht]')
    rest = re.findall(rf'@a\[name={re.escape(erster)}\b', t)
    assert rel == TICK or not rest, f'unerwartete Stelle mit {erster} in {rel}'
    dateien[rel] = t.encode('utf-8')

d = dateien[DATEN].decode('utf-8')
dateien[DATEN] = ('# Besitzer dieses Plans markieren: nur er sieht Geisterblöcke und Hinweise\n'
                  'scoreboard players operation #cur ofh.id = @s ofh.id\n'
                  'tag @a[tag=ofh.sieht] remove ofh.sieht\n'
                  'execute as @a if score @s ofh.id = #cur ofh.id run tag @s add ofh.sieht\n' + d).encode('utf-8')
meta = json.loads(dateien['pack.mcmeta'])
meta['pack']['description'] = "Ole's Farmhelper (nur " + ' und '.join(namen) + ', unsichtbar für andere)'
dateien['pack.mcmeta'] = json.dumps(meta, indent=2, ensure_ascii=False).encode('utf-8')

with zipfile.ZipFile(aus, 'w', zipfile.ZIP_DEFLATED) as zf:
    for rel in sorted(dateien):
        info = zipfile.ZipInfo(rel, date_time=(2026, 11, 11, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        zf.writestr(info, dateien[rel])
print(zaehler, '->', aus)
