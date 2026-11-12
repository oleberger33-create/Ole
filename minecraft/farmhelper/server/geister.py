#!/usr/bin/env python3
"""Server-Fassung des Farmhelpers: Blöcke im Weg deutlich zeigen.

Block-Fassung (nur_spieler.py, Geister sind leuchtende Blöcke): Ein Geist in einem Block leuchtet rot, die
Umrandung sieht man auch durch den Block – das bleibt. Ausgraben bleibt orange (wie in der Legende), und die
Aktionsleiste zeigt „im Weg N“.

Partikel-Fassung (farmhelper_nur_fuer.py):
In der Server-Fassung sind die Geisterblöcke Partikel (nur der Planbesitzer sieht sie). Steht an einer Stelle schon
ein Block – Gras, Erde, Stein –, steckt der Geist darin und ist unsichtbar; bisher kamen nur drei rote Punkte über
die Blockmitte, die man unter der Grasoberfläche oder an Höhlenwänden kaum sieht. Dieses Werkzeug ändert das:

* Block im Weg: kleine Punkte an allen fünf Seiten (oben, Nord, Süd, West, Ost), ganz knapp außerhalb des Blocks –
  so sieht man jede freie Seite. Orange = ausgraben (Schritt „frei machen“), rot = falscher Block (abbauen, dann
  erscheint dort der Geist). Das passt zur Legende im Plan-Menü (rot: falscher Block, gold: ausgraben).
* Aktionsleiste: zusätzlich „im Weg N“ mit der Erklärung, solange etwas im Weg ist.

Aufruf (Schritt 5 nach baustein.py): python3 geister.py <ein.zip> <aus.zip>
"""
import re
import sys
import zipfile

ein, aus = sys.argv[1], sys.argv[2]
NS = 'ofh'
ROT_GLUEHEN = re.compile(r'^(?P<cond>execute .*?) positioned ~0\.1 ~0\.1 ~0\.1 run data merge entity '
                         r'@e\[type=minecraft:block_display,tag=ofh_g,distance=\.\.0\.05,limit=1\] '
                         r'\{glow_color_override:\d+\}$')
ROT = re.compile(r'^(?P<cond>.*?) run particle minecraft:dust\{color:\[1\.0,0\.25,0\.25\],scale:1\.6\} '
                 r'~0\.5 ~1\.25 ~0\.5 0\.12 0\.1 0\.12 0 3 force (?P<wer>\S+)$')
FARBE = {'weg': '[1.0,0.15,0.15]', 'graben': '[1.0,0.65,0.0]'}
SEITEN = [('~0.5 ~1.04 ~0.5', '0.2 0 0.2'),                      # oben
          ('~0.5 ~0.5 ~-0.04', '0.2 0.2 0'), ('~0.5 ~0.5 ~1.04', '0.2 0.2 0'),   # Nord, Süd
          ('~-0.04 ~0.5 ~0.5', '0 0.2 0.2'), ('~1.04 ~0.5 ~0.5', '0 0.2 0.2')]   # West, Ost
ZUSATZ = (', {"text": "  im Weg ", "color": "gray"}, {"score": {"name": "#weg", "objective": "ofh"}, '
          '"color": "red"}, {"text": " (orange: ausgraben, rot: abbauen)", "color": "gray"}]')


def markierung(cond, wer, art):
    zeilen = [f'{cond} run particle minecraft:dust{{color:{FARBE[art]},scale:1.0}} {pos} {d} 0 1 force {wer}'
              for pos, d in SEITEN]
    return zeilen + [f'{cond} run scoreboard players add #weg {NS} 1']


def aktionsleiste(zeile):
    """Zweite Fassung einer actionbar-Zeile mit „im Weg“, nur wenn #weg > 0 (gewinnt, weil sie danach kommt)."""
    if ' actionbar [' not in zeile or not zeile.rstrip().endswith(']'):
        return None
    neu = zeile.rstrip()[:-1] + ZUSATZ
    bedingung = f'if score #weg {NS} matches 1.. '
    if neu.startswith('$execute '):
        return '$execute ' + bedingung + neu[len('$execute '):]
    if neu.startswith('execute '):
        return 'execute ' + bedingung + neu[len('execute '):]
    if neu.startswith('title '):
        return f'execute {bedingung}run ' + neu
    if neu.startswith('$title '):
        return f'$execute {bedingung}run ' + neu[1:]
    return None


zin = zipfile.ZipFile(ein)
zahl = {'c': 0, 'hud': 0, 'reset': 0}
with zipfile.ZipFile(aus, 'w', zipfile.ZIP_DEFLATED) as zout:
    for info in zin.infolist():
        n, daten = info.filename, zin.read(info.filename)
        if re.fullmatch(rf'data/{NS}/function/c/\d+\.mcfunction', n):
            zeilen = daten.decode('utf-8').splitlines()
            graben = zeilen[0].startswith('execute unless block ~ ~ ~ #minecraft:replaceable run scoreboard')
            neu = []
            for z in zeilen:
                m, g = ROT.match(z), ROT_GLUEHEN.match(z)
                if m:                                    # Partikel-Fassung: Seiten markieren
                    neu += markierung(m.group('cond'), m.group('wer'), 'graben' if graben else 'weg')
                    zahl['c'] += 1
                elif g:                                  # Block-Fassung: Geist leuchtet rot (sieht man durch Blöcke)
                    if not graben:                       # Ausgraben bleibt orange, wie in der Legende
                        neu.append(z)
                    neu.append(f"{g.group('cond')} run scoreboard players add #weg {NS} 1")
                    zahl['c'] += 1
                else:
                    neu.append(z)
            daten = ('\n'.join(neu) + '\n').encode('utf-8')
        elif n == f'data/{NS}/function/plan/sekunde.mcfunction':
            t = daten.decode('utf-8')
            alt = f'function {NS}:plan/pruefen_m'
            assert alt in t, 'plan/sekunde: Prüfaufruf nicht gefunden'
            t = t.replace(alt, f'scoreboard players set #weg {NS} 0\n' + alt, 1)
            daten = t.encode('utf-8')
            zahl['reset'] += 1
        elif n.endswith('/hud.mcfunction') and n.startswith(f'data/{NS}/function/'):
            neu = []
            for z in daten.decode('utf-8').splitlines():
                neu.append(z)
                v = aktionsleiste(z)
                if v:
                    neu.append(v)
                    zahl['hud'] += 1
            daten = ('\n'.join(neu) + '\n').encode('utf-8')
        zout.writestr(info, daten)
assert zahl['reset'] == 1 and zahl['c'] > 0 and zahl['hud'] > 0, zahl
print(f"Blöcke im Weg: {zahl['c']} Prüfungen markieren alle Seiten, {zahl['hud']} Aktionsleisten mit „im Weg“ -> {aus}")
