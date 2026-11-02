#!/usr/bin/env python3
"""Ole's Farmhelper (Datapack OlesFarmhelper.zip, Namespace ofh) auf EINEN Spieler beschraenken – unsichtbar fuer alle anderen.

* Nur dieser Spieler bekommt das Farmhelper-Item, nur er kann es benutzen (Rechtsklick-Menue, /trigger ofh.t);
  das Craft-Rezept wird entfernt.
* Die Geisterbloecke (block_display) und Hinweis-Schilder (text_display) sieht in Vanilla jeder. Sie werden durch
  Partikel ersetzt, die der Server nur diesem Spieler schickt (`particle ... force @a[name=...]`):
    - fehlender Block  -> block_marker-Partikel mit der Block-Textur in der Blockmitte (jede Sekunde neu, nur fuer ihn)
    - falscher Block   -> rote Punkte ueber dem Block
    - "X hierher bringen" / "Y in den Spender legen" -> gelbe Punkte ueber der Stelle + Chat-Zeile mit Koordinaten (nur er)
  Die Plan-Logik (Marker, Schritte, Pruefung jede Sekunde, HUD, Menues) bleibt unveraendert.

Run: python3 farmhelper_nur_fuer.py <original.zip> <spielername> <ausgabe.zip>
Item nochmal bekommen: /trigger ofh.t set 9099 (oder als Op /function ofh:item)
"""
import collections, re, sys, zipfile

src, name, dst = sys.argv[1], sys.argv[2], sys.argv[3]
P = f'@a[name={name}]'
FN = 'data/ofh/function/'
TICK = f"""scoreboard players enable {P} ofh.t
execute as @a[name={name},scores={{ofh.klick=1..}}] if items entity @s weapon.mainhand *[minecraft:custom_data~{{ofh:1b}}] run function ofh:klick
scoreboard players reset @a[scores={{ofh.klick=1..}}] ofh.klick
execute as {P} unless score @s ofh.id matches 1.. run function ofh:neue_id
execute as @a[name={name},tag=!ofh.v1] run function ofh:item
tag {P} add ofh.v1
execute as @a[name={name},scores={{ofh.t=1..}}] at @s run function ofh:trigger
scoreboard players reset @a[scores={{ofh.t=1..}}] ofh.t
"""
RED = f'particle minecraft:dust{{color:[1.0,0.25,0.25],scale:1.6}} ~0.5 ~1.25 ~0.5 0.12 0.1 0.12 0 3 force {P}'
YELLOW = 'particle minecraft:dust{color:[1.0,0.85,0.2],scale:1.3} %s 0.08 0.3 0.08 0 4 force ' + P
REP = {  # Ersatz-Block fuer Tag-Checks, falls kein Geisterblock zugeordnet werden kann
    '#ofh:truhe': 'minecraft:chest', '#ofh:boden': 'minecraft:dirt', '#ofh:staengel': 'minecraft:melon_stem', '#ofh:seetang': 'minecraft:kelp',
    '#ofh:bienen': 'minecraft:beehive', '#ofh:bambus': 'minecraft:bamboo', '#minecraft:beds': 'minecraft:red_bed', '#minecraft:buttons': 'minecraft:oak_button',
    '#minecraft:campfires': 'minecraft:campfire', '#minecraft:cauldrons': 'minecraft:cauldron', '#minecraft:impermeable': 'minecraft:glass',
    '#minecraft:planks': 'minecraft:oak_planks', '#minecraft:sand': 'minecraft:sand', '#minecraft:saplings': 'minecraft:oak_sapling',
    '#minecraft:slabs': 'minecraft:oak_slab', '#minecraft:small_flowers': 'minecraft:poppy', '#minecraft:standing_signs': 'minecraft:oak_sign',
    '#minecraft:wall_signs': 'minecraft:oak_wall_sign', '#minecraft:walls': 'minecraft:cobblestone_wall', '#minecraft:wooden_fences': 'minecraft:oak_fence',
    '#minecraft:wooden_trapdoors': 'minecraft:oak_trapdoor', '#minecraft:wool_carpets': 'minecraft:white_carpet',
}

zin = zipfile.ZipFile(src)
names = [i.filename for i in zin.infolist() if not i.filename.endswith('/')]
text = {n: zin.read(n).decode('utf-8') for n in names if n.endswith('.mcfunction')}

# ---- Zuordnung Pruef-Funktion (c/i/w) -> Geister-Funktion (z): gleiche Position in zeigen/pruefen eines Schritts
c2z = collections.defaultdict(collections.Counter)
for zn in [n for n in names if re.search(r'/f/[^/]+/r\d+/s\d+/zeigen\.mcfunction$', n)]:
    pn = zn.replace('zeigen', 'pruefen')
    if pn not in text:
        continue
    zl = [l for l in text[zn].splitlines() if 'ofh:z/' in l]
    pl = [l for l in text[pn].splitlines() if re.search(r'ofh:[ciw]/', l)]
    if len(zl) != len(pl):
        continue
    for a, b in zip(zl, pl):
        if re.search(r'positioned (\S+ \S+ \S+)', a).group(1) != re.search(r'positioned (\S+ \S+ \S+)', b).group(1):
            break
        c2z[re.search(r'ofh:([ciw]/\d+)', b).group(1)][re.search(r'ofh:(z/\d+)', a).group(1)] += 1

# ---- z/N: Geisterblock -> block_marker-Partikel (nur fuer den Spieler); Schild -> Funktion zt/N (Chat-Zeile + gelbe Punkte)
zblock = {}       # 'z/N' -> block_state-Compound
new = {}          # Dateiname -> neuer Inhalt
R_BLOCK = re.compile(r'^(?P<pre>.*?)summon minecraft:block_display \S+ \S+ \S+ \{block_state:(?P<rest>\{.*)$')


def balanced(t):
    """erstes geklammertes Compound am Anfang von t, z.B. {id:"minecraft:chest",properties:{facing:"south"}}"""
    depth = 0
    for i, ch in enumerate(t):
        depth += (ch == '{') - (ch == '}')
        if depth == 0:
            return t[:i + 1]
    raise ValueError(t[:80])
R_TEXT = re.compile(r'^(?P<pre>.*?)summon minecraft:text_display (?P<pos>\S+ \S+ \S+) \{text:\{text:"(?P<label>[^"]+)"')
for n in names:
    m = re.match(r'data/ofh/function/z/(\d+)\.mcfunction$', n)
    if not m:
        continue
    k, line = m.group(1), text[n].strip()
    mb, mt = R_BLOCK.match(line), R_TEXT.match(line)
    if mb:
        bs = balanced(mb.group('rest'))
        zblock['z/' + k] = bs
        new[n] = f"{mb.group('pre')}particle minecraft:block_marker{{block_state:{bs}}} ~0.5 ~0.5 ~0.5 0 0 0 0 1 force {P}\n"
    elif mt:
        new[n] = f"{mt.group('pre')}function ofh:zt/{k}\n"
        label = mt.group('label').replace('\\', '').replace('"', "'")
        new[f'{FN}zt/{k}.mcfunction'] = '\n'.join([
            'summon minecraft:marker ~ ~ ~ {Tags:["ofh_lbl"]}',
            *[f'execute store result score #l{a} ofh run data get entity @e[type=minecraft:marker,tag=ofh_lbl,limit=1] Pos[{i}]' for i, a in enumerate('xyz')],
            'kill @e[type=minecraft:marker,tag=ofh_lbl]',
            f'tellraw {P} [{{text:"➜ ",color:"gold"}},{{text:"{label}",color:"yellow"}},{{text:" bei ",color:"gray"}},'
            '{score:{name:"#lx",objective:"ofh"},color:"white"},{text:" / ",color:"gray"},{score:{name:"#ly",objective:"ofh"},color:"white"},'
            '{text:" / ",color:"gray"},{score:{name:"#lz",objective:"ofh"},color:"white"}]',
            YELLOW % mt.group('pos'),
        ]) + '\n'
    else:
        raise SystemExit(f'unbekanntes z-Muster in {n}: {line[:120]}')


def ghost_for(key, cond_block):
    """block_state-Compound fuer den Partikel: zugeordneter Geisterblock, sonst konkreter Block / Ersatz fuer den Tag"""
    zk = c2z[key].most_common(1)[0][0] if c2z.get(key) else None
    if zk in zblock:
        return zblock[zk]
    b = re.sub(r'\[.*$', '', cond_block)
    return '{id:"%s"}' % (REP.get(b, b) if b.startswith('#') else b)


# ---- c/N (Block-Check), i/N (Item im Behaelter), w/N (Tier/Lore da?): Entity-Zeilen -> Partikel nur fuer den Spieler
for n in names:
    m = re.match(r'data/ofh/function/([ciw])/(\d+)\.mcfunction$', n)
    if not m:
        continue
    kind, k = m.groups()
    lines = text[n].splitlines()
    first = lines[0]
    cond = first[:first.index(' run scoreboard')]
    if kind == 'c':
        blocks = re.findall(r'unless block ~ ~ ~ (\S+)', cond)
        out = [first]
        if blocks[0] != '#minecraft:replaceable':                      # fehlt -> Marker mit Block-Textur
            out.append(f'{cond} run particle minecraft:block_marker{{block_state:{ghost_for(f"c/{k}", blocks[0])}}} ~0.5 ~0.5 ~0.5 0 0 0 0 1 force {P}')
        out.append(f'{cond} unless block ~ ~ ~ #minecraft:replaceable run {RED}')   # falscher Block im Weg -> rot
    else:
        pos = '~ ~1.3 ~' if cond.startswith('execute positioned ~0.5 ~ ~0.5') else '~0.5 ~1.3 ~0.5'
        out = [first, f'{cond} run ' + (YELLOW % pos)]
    new[n] = '\n'.join(out) + '\n'

n_out = 0
with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zout:
    for n in names:
        if n == 'data/ofh/recipe/farmhelper.json':
            continue                                                   # kein Rezept mehr
        data = new.get(n, None)
        if data is None:
            data = zin.read(n)
            if n == FN + 'tick.mcfunction':
                data = TICK.encode('utf-8')
            if n == 'pack.mcmeta':
                data = data.replace(b"Ole's Farmhelper", f"Ole's Farmhelper (nur {name}, unsichtbar fuer andere)".encode('utf-8'))
        zout.writestr(n, data)
        n_out += 1
    for n, data in new.items():
        if n not in names:
            zout.writestr(n, data); n_out += 1
print(f'{len(names)} Eintraege gelesen, {n_out} geschrieben, {len(zblock)} Geisterbloecke, {len([n for n in new if "/zt/" in n])} Schilder -> {dst} (nur fuer {name})')
