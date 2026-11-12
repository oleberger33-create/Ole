"""Baut Ersatzblöcke und die Bausteinauswahl in Ole's Farmhelper ein (Schritt 4 der Server-Version, siehe README).

Aufruf: python3 baustein.py <zip-oder-ordner> <zip-neu> baustein.json

konfig.json:
  {"tags": {"stein": [Block-IDs], "stein_nether": [...], ...},   – akzeptierte Blöcke je Gruppe
   "betroffen": {"minecraft:stone_bricks": "stein", ...},        – welche Positionen welche Gruppe akzeptieren
   "nur_flexibel": ["minecraft:glowstone", ...],                  – akzeptieren ihre Gruppe, folgen aber NICHT der Auswahl
   "auswahl": [{"id": "minecraft:cobblestone", "name": "Bruchstein"}, ...]}  – wählbar, muss in jeder Gruppe sein

Was passiert:
- Block-Tags #ofh:<gruppe>; Item-Tags nur für Gruppen, die ein Material-Zähler braucht.
- Prüfungen in c/, z/, h/: "block ~ ~ ~ minecraft:<betroffen>" -> "#ofh:stein".
- Geisterblock-Partikel: bei Plan-Vorgabe (#wahl 0) wie bisher, sonst der gewählte Block (Makro ofh:wahl/geist).
- HUD: zählt bei Vorgabe die ganze Gruppe, sonst den gewählten Block; Symbol zeigt den gewählten Block.
- Menü jedes Schritts: neuer Knopf "Baustein" (Trigger 9500), Auswahl-Dialog mit Trigger 9501 ff.
- plan/daten: Standardwerte am Plan-Marker und #wahl für den aktuellen Plan.
"""
import json, os, re, sys, zipfile

alt, ziel, konfig_pfad = sys.argv[1:4]
konfig = json.load(open(konfig_pfad, encoding='utf-8'))
TAGS, BETROFFEN, AUSWAHL = konfig['tags'], konfig['betroffen'], konfig['auswahl']
NUR_FLEXIBEL = set(konfig.get('nur_flexibel', []))
WAEHLBAR = {b: t for b, t in BETROFFEN.items() if b not in NUR_FLEXIBEL}
assert all(b in TAGS[t] for b, t in BETROFFEN.items()), 'jeder betroffene Block muss in seiner eigenen Gruppe sein'
assert not ({BETROFFEN[b] for b in NUR_FLEXIBEL} & set(WAEHLBAR.values())), 'nur flexible Blöcke brauchen eigene Gruppen'
assert all(a['id'] in TAGS[t] for a in AUSWAHL for t in set(WAEHLBAR.values())), 'wählbare Blöcke müssen überall erlaubt sein'

dateien = {}
if alt.endswith('.zip'):
    with zipfile.ZipFile(alt) as zf:
        dateien = {n: zf.read(n) for n in zf.namelist() if not n.endswith('/')}
else:
    for d, _, fs in os.walk(alt):
        for f in fs:
            p = os.path.join(d, f)
            dateien[os.path.relpath(p, alt).replace(os.sep, '/')] = open(p, 'rb').read()
FN = 'data/ofh/function/'
txt = lambda rel: dateien[rel].decode('utf-8')
def setze(rel, t): dateien[rel] = t.encode('utf-8')

bet = '|'.join(re.escape(b) for b in sorted(BETROFFEN, key=len, reverse=True))
wbet = '|'.join(re.escape(b) for b in sorted(WAEHLBAR, key=len, reverse=True))
PRAED = re.compile(r'(block ~ ~ ~ )(' + bet + r')(?![a-z_\[{])')
GEIST = re.compile(r'^(execute .*?)run (particle minecraft:block_marker\{block_state:\{id:"(' + wbet + r')"\}\} '
                   r'~0\.5 ~0\.5 ~0\.5 0 0 0 0 1 force @a\[tag=ofh\.sieht\])$')
# Geister als Blöcke (nur_spieler.py): summon block_display mit dem Plan-Stein -> bei Auswahl der gewählte Stein
GEIST_B = re.compile(r'^(execute .*?)run summon minecraft:block_display (\S+ \S+ \S+) \{block_state:\{id:"(' + wbet
                     + r')"\},(.*)$')
geist_b_nbt = None
zaehl = {'praedikate': 0, 'geister': 0, 'hud_zaehler': 0, 'hud_titel': 0, 'menues': 0}
item_tags = set()  # Gruppen, die ein Material-Zähler (clear @s #ofh:…) braucht

# ---- Prüf-, Zeige- und Hindernis-Funktionen
for rel in list(dateien):
    if not rel.startswith(FN) or not re.match(FN + r'(c|z|h)/', rel):
        continue
    neu = []
    for z in txt(rel).splitlines():
        z2, n = PRAED.subn(lambda m: m.group(1) + '#ofh:' + BETROFFEN[m.group(2)], z)
        zaehl['praedikate'] += n
        m = GEIST.match(z2)
        mb = GEIST_B.match(z2)
        if m and n:
            neu.append(f'{m.group(1)}if score #wahl ofh matches 0 run {m.group(2)}')
            neu.append(f'{m.group(1)}unless score #wahl ofh matches 0 run function ofh:wahl/geist with storage ofh:tmp d')
            zaehl['geister'] += 1
        elif mb and n:
            pos, rest = mb.group(2), mb.group(4)
            assert geist_b_nbt in (None, (pos, rest)), 'Geister-Blöcke mit unterschiedlichem NBT'
            geist_b_nbt = (pos, rest)
            neu.append(f'{mb.group(1)}if score #wahl ofh matches 0 run ' + z2[len(mb.group(1)) + len('run '):])
            neu.append(f'{mb.group(1)}unless score #wahl ofh matches 0 run function ofh:wahl/geist with storage ofh:tmp d')
            zaehl['geister'] += 1
        else:
            neu.append(z2)
    setze(rel, '\n'.join(neu) + '\n')

# ---- HUDs
def titel_mit_wahl(zeile, zaehler):
    """Tauscht im Aktionsleisten-Titel das Symbol direkt vor jedem genannten Zähler gegen $(bild).
    Gibt None zurück, wenn nichts zu tauschen ist (dann bleibt die Zeile, wie sie ist)."""
    kopf = 'title @s actionbar '
    teile = json.loads(zeile[len(kopf):])
    if not isinstance(teile, list):
        return None
    getauscht = False
    for i, el in enumerate(teile):
        if isinstance(el, dict) and el.get('score', {}).get('name') in zaehler:
            for k in range(i - 1, 0, -1):          # Stelle 0 ist das Farm-Logo und bleibt
                if isinstance(teile[k], dict) and 'sprite' in teile[k]:
                    if teile[k]['sprite'].startswith('block/'):
                        teile[k] = dict(teile[k], sprite='$(bild)')
                        getauscht = True
                    break
    return kopf + json.dumps(teile, ensure_ascii=False) if getauscht else None

farmen_mit_stein = set()
CLEAR = re.compile(r'^execute store result score (#h\d+) ofh run clear @s (' + bet + r') 0$')
def CLEAR_FIX(m):
    item_tags.add(BETROFFEN[m.group(2)])
    return f'execute store result score {m.group(1)} ofh run clear @s #ofh:{BETROFFEN[m.group(2)]} 0'
for rel in list(dateien):
    if not re.match(FN + r'f/[^/]+/s\d+/hud\.mcfunction$', rel):
        continue
    t, neu, geaendert, waehl = txt(rel), [], False, False
    # Zähler (#hN), deren clear-Ziel ein wählbarer Block ist: nur deren Symbol folgt der Wahl
    gewaehlte_zaehler = {m.group(1) for m in map(CLEAR.match, t.splitlines()) if m and m.group(2) in WAEHLBAR}
    for z in t.splitlines():
        m = CLEAR.match(z)
        if m and m.group(2) in NUR_FLEXIBEL:
            neu.append(CLEAR_FIX(m))
            geaendert = True
            continue
        if m:
            item_tags.add(BETROFFEN[m.group(2)])
            neu.append(f'execute if score #wahl ofh matches 0 store result score {m.group(1)} ofh run clear @s #ofh:{BETROFFEN[m.group(2)]} 0')
            neu.append(f'$execute unless score #wahl ofh matches 0 store result score {m.group(1)} ofh run clear @s $(stein) 0')
            zaehl['hud_zaehler'] += 1
            geaendert = waehl = True
            continue
        ersetzt = titel_mit_wahl(z, gewaehlte_zaehler) if z.startswith('title @s actionbar ') else None
        if ersetzt:
            assert '$(' not in z
            neu.append('execute if score #wahl ofh matches 0 run ' + z)
            neu.append('$execute unless score #wahl ofh matches 0 run ' + ersetzt)
            zaehl['hud_titel'] += 1
            geaendert = waehl = True
            continue
        neu.append(z)
    if waehl:
        farmen_mit_stein.add(rel.split('/')[4])
    if geaendert:
        setze(rel, '\n'.join(neu) + '\n')
setze(FN + 'plan/hud_m.mcfunction', '$function ofh:f/$(farm)/s$(s)/hud with storage ofh:tmp d\n')

# Farmen, deren Pläne betroffene Blöcke enthalten (auch ohne HUD-Zähler)
for rel in dateien:
    m = re.match(FN + r'f/([^/]+)/r\d+/s\d+/pruefen\.mcfunction$', rel)
    if m:
        for cid in re.findall(r'function ofh:(c/\d+)', txt(rel)):
            if any(f'#ofh:{t}' in txt(FN + cid + '.mcfunction') for t in set(WAEHLBAR.values())):
                farmen_mit_stein.add(m.group(1))
                break

# ---- Menü-Knopf "Baustein" in jedem Schritt dieser Farmen
KNOPF = {"label": [{"type": "object", "object": "atlas", "atlas": "minecraft:blocks", "sprite": "block/stone_bricks"},
                   {"text": " "}, {"text": "Baustein", "color": "gold"}],
         "width": 130, "action": {"type": "run_command", "command": "/trigger ofh.t set 9500"},
         "tooltip": {"text": "Welchen Stein du für diesen Plan nehmen willst"}}
for rel in list(dateien):
    m = re.match(FN + r'f/([^/]+)/s\d+/menu\.mcfunction$', rel)
    if not m or m.group(1) not in farmen_mit_stein:
        continue
    kopf, js = txt(rel).strip().split(' ', 3)[:3], txt(rel).strip().split(' ', 3)[3]
    assert kopf == ['dialog', 'show', '@s'], rel
    d = json.loads(js)
    i = next(k for k, a in enumerate(d['actions']) if a['action'].get('command') == '/trigger ofh.t set 9003')
    d['actions'].insert(i + 1, KNOPF)
    setze(rel, 'dialog show @s ' + json.dumps(d, ensure_ascii=False) + '\n')
    zaehl['menues'] += 1

# ---- plan/daten: Standardwerte und #wahl
d = txt(FN + 'plan/daten.mcfunction').splitlines()
pos = next(k for k, z in enumerate(d) if z.startswith('execute store result entity @s data.s'))
d[pos:pos] = ['# Baustein dieses Plans (0 = Vorgabe des Plans)',
              'execute unless data entity @s data.name run data merge entity @s {data:{wahl:0,stein:"minecraft:stone_bricks",bild:"block/stone_bricks",name:"Vorgabe des Plans"}}',
              'execute store result score #wahl ofh run data get entity @s data.wahl']
setze(FN + 'plan/daten.mcfunction', '\n'.join(d) + '\n')

# ---- Trigger
t = txt(FN + 'trigger.mcfunction').splitlines()
t[1:1] = ['execute if score @s ofh.t matches 9500 run return run function ofh:wahl/menu',
          f'execute if score @s ofh.t matches 9501..{9501 + len(AUSWAHL)} run return run function ofh:wahl/gewaehlt']
setze(FN + 'trigger.mcfunction', '\n'.join(t) + '\n')

# ---- neue Funktionen
def knopf(text, sprite, wert, farbe='white'):
    lab = [{"type": "object", "object": "atlas", "atlas": "minecraft:blocks", "sprite": sprite}, {"text": " "},
           {"text": text, "color": farbe}]
    return {"label": lab, "width": 130, "action": {"type": "run_command", "command": f"/trigger ofh.t set {wert}"}}
aktionen = [knopf('Vorgabe des Plans', 'block/structure_block', 9501, 'gray')]
setzen = ['# Läuft als Plan-Marker; #w = gewählte Nummer (1 = Vorgabe)',
          'execute if score #w ofh matches 1 run data merge entity @s {data:{wahl:0,stein:"minecraft:stone_bricks",bild:"block/stone_bricks",name:"Vorgabe des Plans"}}']
for k, a in enumerate(AUSWAHL, 2):
    bild = 'block/' + a['id'].split(':')[1]
    aktionen.append(knopf(a['name'], bild, 9500 + k))
    setzen.append(f'execute if score #w ofh matches {k} run data merge entity @s '
                  f'{{data:{{wahl:{k},stein:"{a["id"]}",bild:"{bild}",name:"{a["name"]}"}}}}')
assert 9500 + len(AUSWAHL) + 1 <= 9599
setzen += ['scoreboard players set #gefunden ofh 1',
           'function ofh:plan/zeigen',
           'data modify storage ofh:tmp w set from entity @s data',
           'execute as @a if score @s ofh.id = #cur ofh.id at @s run function ofh:wahl/bestaetigt with storage ofh:tmp w']
menu = {"type": "minecraft:multi_action",
        "title": [{"type": "object", "object": "atlas", "atlas": "minecraft:blocks", "sprite": "block/stone_bricks"},
                  {"text": "  Baustein wählen", "bold": True, "color": "gold"}],
        "external_title": {"text": "Baustein"},
        "body": [{"type": "minecraft:plain_message", "width": 300, "contents": {"text": "Welchen Stein willst du für diesen Plan nehmen? Die Geisterblöcke und der Zähler zeigen dann diesen Stein. Andere passende Steine nimmt die Farm trotzdem an. Blöcke, die für die Farm wichtig sind, bleiben fest. Die Material-Liste und der Menütext nennen weiter die Vorgabe des Plans.", "color": "gray"}}],
        "can_close_with_escape": True, "pause": False, "after_action": "close", "columns": 3, "actions": aktionen}
neu = {
    'wahl/menu': ['dialog show @s ' + json.dumps(menu, ensure_ascii=False)],
    'wahl/gewaehlt': ['scoreboard players operation #w ofh = @s ofh.t',
                      'scoreboard players remove #w ofh 9500',
                      'scoreboard players set #gefunden ofh 0',
                      'execute as @e[type=minecraft:marker,tag=ofh_plan] if score @s ofh.id = #cur ofh.id at @s run function ofh:wahl/setzen',
                      'execute if score #gefunden ofh matches 0 run tellraw @s {text:"Kein Plan aktiv – erst eine Farm wählen.",color:"gray"}'],
    'wahl/setzen': setzen,
    'wahl/bestaetigt': ['$tellraw @s [{text:"Baustein: ",color:"gold"},{text:"$(name)",color:"yellow"},{text:" – die Geisterblöcke zeigen jetzt diesen Stein.",color:"gray"}]',
                        'playsound minecraft:block.stone.place master @s ~ ~ ~ 1 1.2'],
    'wahl/geist': (['$summon minecraft:block_display %s {block_state:{id:"$(stein)"},%s' % geist_b_nbt] if geist_b_nbt else
                   ['$particle minecraft:block_marker{block_state:{id:"$(stein)"}} ~0.5 ~0.5 ~0.5 0 0 0 0 1 force @a[tag=ofh.sieht]']),
}
for name, zeilen in neu.items():
    setze(FN + name + '.mcfunction', '\n'.join(zeilen) + '\n')

# ---- Tags
for t, ids in TAGS.items():
    setze(f'data/ofh/tags/block/{t}.json', json.dumps({"values": ids}, indent=2) + '\n')
    if t in item_tags:
        setze(f'data/ofh/tags/item/{t}.json', json.dumps({"values": ids}, indent=2) + '\n')

with zipfile.ZipFile(ziel, 'w', zipfile.ZIP_DEFLATED) as zf:
    for rel in sorted(dateien):
        info = zipfile.ZipInfo(rel, date_time=(2026, 11, 11, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        zf.writestr(info, dateien[rel])
print(zaehl, '| Item-Tags:', sorted(item_tags), '| Farmen mit Baustein-Knopf:', len(farmen_mit_stein), sorted(farmen_mit_stein))
print('->', ziel, os.path.getsize(ziel), 'Bytes')
