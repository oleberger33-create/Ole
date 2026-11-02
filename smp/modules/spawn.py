# modules/spawn.py – Spawn-Platz (einmal gebaut, Versions-Score #spawn_v) + /trigger spawn + Hologramme/Leaderboards.
#
# Storage smp:spawn
#   pos     {x,y,z (double, Stehposition = Mitte des Goldblocks), dim}  -> direkt fuer `function smp:core/tp with storage smp:spawn pos`
#   blk     {x,y,z (int Blockkoordinaten der Stehposition), px,py,pz (double wie pos)}  -> fuer loaded-Checks/setworldspawn
#   players [{name:"..."}]  alle bekannten Spielernamen (fuer Leaderboards auch offline)
#   join    {x,y,z int}  Join-Position des ersten neuen Spielers (= Weltspawn): dort wird der Platz 3 s spaeter gebaut
# Scores (Objective smp): #spawn_v (gebaute Version), #spawn_x/y/z, #spawn_holo (1 = Hologramme aktuell), #spawn_t (Sekunden-Zaehler)
# Objectives: smp_sp_pick (Scratch fuers Ranking); smp_tode (Todes-Zaehler) und smp_mkills kommen aus dem Kern
# Tags: smp_holo (+ smp_holo_top fuer die Leaderboards), smp_sp_pend (wartet auf den automatischen Bau), smp_sp_reg (Name registriert)
# Automatischer Bau: nur ein WIRKLICH neuer Spieler (kein Bett-Spawn, 0 XP -> er steht am Weltspawn) loest ihn aus; gebaut wird an seiner
# Join-Position (nicht dort, wo er 3 s spaeter steht). Wird das Pack in eine bestehende Welt eingebaut: /function smp:spawn/build_here.
# Funktionen fuer Admins: /function smp:spawn/build_here (als Spieler: baut den Platz an der eigenen Position und setzt den Weltspawn dorthin),
#                         /execute positioned <x> <y> <z> run function smp:spawn/build_at (nur die Bloecke+Hologramme, beliebige Position)
import math as _math

SPAWN_VERSION = 1
SP_R, SP_RIN, SP_RDAIS, SP_CLEAR, SP_DEEP = 12, 9, 4, 24, 15


def _rows(r):
    """(dz, halbe Breite) je Zeile einer Kreisscheibe (gleiche Formel wie der minigames-Helper disk())"""
    return [(dz, int(_math.floor(_math.sqrt(r * r + r - dz * dz)))) for dz in range(-r, r + 1)]


def _f(x1, y1, z1, x2, y2, z2, block, extra=''):
    return f'fill ~{x1} ~{y1} ~{z1} ~{x2} ~{y2} ~{z2} minecraft:{block}{extra}'


def _s(x, y, z, block):
    return f'setblock ~{x} ~{y} ~{z} minecraft:{block}'


def _holo(tags, dx, dy, dz, text, scale=1.0, billboard='vertical', align='left', width=200, bg=None):
    tagstr = ','.join(f'"{t}"' for t in ['smp_holo'] + list(tags))
    extra = f',background:{bg}' if bg is not None else ''
    return (f'summon minecraft:text_display ~{dx} ~{dy} ~{dz} {{Tags:[{tagstr}],billboard:"{billboard}",alignment:"{align}",'
            f'line_width:{width},shadow:1b{extra},text:{tc(text)},transformation:{{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],'
            f'translation:[0f,0f,0f],scale:[{scale}f,{scale}f,{scale}f]}}}}')


# ---------------------------------------------------------------- Block-Tag: "weiche" Bloecke (Luft, Wasser, Pflanzen, Baeume) fuer Bodensuche + Auffuellen
js(f'data/{NS}/tags/block/spawn_soft.json', {'replace': False, 'values': [
    '#minecraft:replaceable', '#minecraft:leaves', '#minecraft:logs', '#minecraft:flowers', '#minecraft:saplings',
    *[{'id': f'minecraft:{b}', 'required': False} for b in [
        'brown_mushroom', 'red_mushroom', 'brown_mushroom_block', 'red_mushroom_block', 'mushroom_stem', 'bamboo', 'bamboo_sapling',
        'sugar_cane', 'cactus', 'cactus_flower', 'pumpkin', 'melon', 'sweet_berry_bush', 'cobweb', 'moss_carpet', 'pale_moss_carpet',
        'pale_hanging_moss', 'pink_petals', 'wildflowers', 'leaf_litter', 'bush', 'firefly_bush', 'short_dry_grass', 'tall_dry_grass',
        'lily_pad', 'big_dripleaf', 'big_dripleaf_stem', 'small_dripleaf', 'spore_blossom', 'cave_vines', 'cave_vines_plant',
        'weeping_vines', 'weeping_vines_plant', 'twisting_vines', 'twisting_vines_plant', 'mangrove_roots', 'mangrove_propagule',
        'azalea', 'flowering_azalea', 'sea_pickle', 'kelp', 'kelp_plant', 'snow', 'powder_snow', 'chorus_plant', 'chorus_flower']]]})

# ---------------------------------------------------------------- Objectives, Konstanten, Registries
EXTRA_LOAD += [
    'scoreboard objectives add smp_sp_pick dummy',
    'scoreboard players set #7200 smp 7200', 'scoreboard players set #10 smp 10',
    'execute unless score #spawn_v smp matches 0.. run scoreboard players set #spawn_v smp 0',
    'scoreboard players set #spawn_holo smp 0',        # nach jedem /reload: Hologramme neu setzen (kill + summon, keine Duplikate)
    'scoreboard players set #spawn_t smp 55',          # erster Minuten-Job 5 s nach dem Laden
]
EXTRA_SECOND += [
    'scoreboard players add #spawn_t smp 1',
    f'execute if score #spawn_t smp matches 60.. run function {NS}:spawn/minute',
    f'execute unless data storage smp:spawn pos as @a[tag=smp_sp_pend,limit=1] at @s run function {NS}:spawn/pend',
]
ON_JOIN += [
    # noch kein Platz: der erste neue Spieler steht am Weltspawn -> dort bauen (mit kurzer Verzoegerung, bis die Chunks geladen sind)
    'execute unless data storage smp:spawn pos run scoreboard players set #spawn_wait smp 0',
    'execute unless data storage smp:spawn pos at @s if dimension minecraft:overworld unless data entity @s respawn if data entity @s {XpTotal:0} run function ' + f'{NS}:spawn/pend_mark',
    f'function {NS}:spawn/reg',
]
ON_REJOIN.append(f'execute if entity @s[tag=!smp_sp_reg] run function {NS}:spawn/reg')

# ---------------------------------------------------------------- /trigger spawn
trigger('spawn', f'{NS}:spawn/go', '/trigger spawn', 'Zum Spawn teleportieren', 'Teleport', ('⌂ Spawn', 'Zum Spawn teleportieren'))
warmup('spawn', f'{NS}:spawn/tp')
fn('spawn/go', [
    'execute unless data storage smp:spawn pos run return run tellraw @s ' + msg({'text': 'Der Spawn-Platz ist noch nicht gebaut.', 'color': 'red'}),
    f'function {NS}:core/warm_spawn',
])
fn('spawn/tp', [
    'execute unless data storage smp:spawn pos run return run tellraw @s ' + msg({'text': 'Der Spawn-Platz ist noch nicht gebaut.', 'color': 'red'}),
    f'function {NS}:core/back_save',
    f'function {NS}:core/tp with storage smp:spawn pos',
    'execute at @s run playsound minecraft:entity.enderman.teleport player @s ~ ~ ~ 0.6 1.3',
    'tellraw @s ' + msg({'text': 'Willkommen am Spawn! ', 'color': 'green'}, {'text': 'Zurueck: ', 'color': 'gray'}, clk('[/trigger back]', '/trigger back', 'yellow', 'Zur letzten Position')),
])

# ---------------------------------------------------------------- Namen-Registry (fuer Leaderboards auch offline): Name per text_display-Selector aufloesen
fn('spawn/reg', [
    'kill @e[type=minecraft:text_display,tag=smp_sp_nm]',
    'tag @s add smp_sp_nmq',
    'execute at @s run summon minecraft:text_display ~ ~ ~ {Tags:["smp_sp_nm"],text:{selector:"@a[tag=smp_sp_nmq,limit=1]"}}',
    'tag @s remove smp_sp_nmq',
    'data remove storage smp:tmp nm',
    'data modify storage smp:tmp nm.name set from entity @e[type=minecraft:text_display,tag=smp_sp_nm,limit=1] text.insertion',
    'execute unless data storage smp:tmp nm.name run data modify storage smp:tmp nm.name set from entity @e[type=minecraft:text_display,tag=smp_sp_nm,limit=1] text.text',
    'kill @e[type=minecraft:text_display,tag=smp_sp_nm]',
    f'execute if data storage smp:tmp nm.name run function {NS}:spawn/reg2 with storage smp:tmp nm',
])
fn('spawn/reg2', [
    '$execute unless data storage smp:spawn players[{name:"$(name)"}] run data modify storage smp:spawn players append value {name:"$(name)"}',
    'tag @s add smp_sp_reg',
])

# ---------------------------------------------------------------- Platz setzen: Boden suchen, Storage/Scores schreiben, bauen, Weltspawn
fn('spawn/build_here', ['execute unless entity @s[type=minecraft:player] run return 0', f'execute at @s run function {NS}:spawn/place_here'])
fn('spawn/pend_mark', [       # als neuer Spieler (ON_JOIN): Bau vormerken + Join-Position (Blockkoordinaten) merken
    'tag @s add smp_sp_pend',
    'execute store result storage smp:spawn join.x int 1 run data get entity @s Pos[0]',
    'execute store result storage smp:spawn join.y int 1 run data get entity @s Pos[1]',
    'execute store result storage smp:spawn join.z int 1 run data get entity @s Pos[2]',
])
fn('spawn/pend', [            # jede Sekunde als + an dem vorgemerkten Spieler, solange kein Platz existiert
    'scoreboard players add #spawn_wait smp 1',
    'execute if score #spawn_wait smp matches 20.. run tag @a remove smp_sp_pend',
    'execute if score #spawn_wait smp matches 20.. run return run tellraw @s ' + msg({'text': 'Der Spawn-Platz konnte nicht gebaut werden (Chunks nicht geladen). Ein Admin kann ihn mit /function smp:spawn/build_here bauen.', 'color': 'red'}),
    'execute if score #spawn_wait smp matches ..2 run return 0',
    f'execute unless data storage smp:spawn join at @s run return run function {NS}:spawn/pend3',
    f'function {NS}:spawn/pend2 with storage smp:spawn join',
])
fn('spawn/pend2', [f'$execute in minecraft:overworld positioned $(x) $(y) $(z) run function {NS}:spawn/pend3'])
fn('spawn/pend3', [           # an der Bauposition: erst bauen, wenn die Chunks (+-16) geladen sind
    'execute unless dimension minecraft:overworld run return 0',
    'execute unless loaded ~-16 ~ ~-16 run return 0', 'execute unless loaded ~16 ~ ~-16 run return 0',
    'execute unless loaded ~-16 ~ ~16 run return 0', 'execute unless loaded ~16 ~ ~16 run return 0',
    f'function {NS}:spawn/place_here',
])
_M = '@e[type=minecraft:marker,tag=smp_sp_m,limit=1]'
fn('spawn/place_here', [      # als + an dem Spieler
    'execute unless entity @s[type=minecraft:player] run return 0',
    'execute unless dimension minecraft:overworld run return run tellraw @s ' + msg({'text': 'Der Spawn-Platz geht nur in der Oberwelt.', 'color': 'red'}),
    'kill @e[type=minecraft:marker,tag=smp_sp_m]',
    'scoreboard players set #spawn_sc smp 0',
    f'execute align xyz run function {NS}:spawn/scan',
    'execute unless entity @e[type=minecraft:marker,tag=smp_sp_m] run tag @a remove smp_sp_pend',
    'execute unless entity @e[type=minecraft:marker,tag=smp_sp_m] run return run tellraw @s ' + msg({'text': 'Kein Boden gefunden – stell dich auf festen Boden.', 'color': 'red'}),
    # Stehposition im Wasser (Spieler schwimmt / steht im See): nicht bauen, der Platz wuerde ueberflutet
    f'execute at {_M} if block ~ ~1 ~ minecraft:water run kill @e[type=minecraft:marker,tag=smp_sp_m]',
    'execute unless entity @e[type=minecraft:marker,tag=smp_sp_m] run tag @a remove smp_sp_pend',
    'execute unless entity @e[type=minecraft:marker,tag=smp_sp_m] run return run tellraw @s ' + msg({'text': 'Hier ist Wasser – der Spawn-Platz braucht festen Boden.', 'color': 'red'}),
    f'execute store result score #spawn_x smp run data get entity {_M} Pos[0]',
    f'execute store result score #spawn_y smp run data get entity {_M} Pos[1]',
    f'execute store result score #spawn_z smp run data get entity {_M} Pos[2]',
    'kill @e[type=minecraft:marker,tag=smp_sp_m]',
    'scoreboard players add #spawn_y smp 1',                        # Stehposition = Bodenblock + 1
    'data modify storage smp:spawn pos set value {dim:"minecraft:overworld"}',
    'data modify storage smp:spawn blk set value {}',
    'execute store result storage smp:spawn blk.x int 1 run scoreboard players get #spawn_x smp',
    'execute store result storage smp:spawn blk.y int 1 run scoreboard players get #spawn_y smp',
    'execute store result storage smp:spawn blk.z int 1 run scoreboard players get #spawn_z smp',
    # Blockmitte: (2*x+1)*0.5 (richtig auch fuer negative Koordinaten)
    'scoreboard players operation #spawn_t2 smp = #spawn_x smp', 'scoreboard players operation #spawn_t2 smp += #spawn_x smp', 'scoreboard players add #spawn_t2 smp 1',
    'execute store result storage smp:spawn pos.x double 0.5 run scoreboard players get #spawn_t2 smp',
    'execute store result storage smp:spawn pos.y double 1 run scoreboard players get #spawn_y smp',
    'scoreboard players operation #spawn_t2 smp = #spawn_z smp', 'scoreboard players operation #spawn_t2 smp += #spawn_z smp', 'scoreboard players add #spawn_t2 smp 1',
    'execute store result storage smp:spawn pos.z double 0.5 run scoreboard players get #spawn_t2 smp',
    'data modify storage smp:spawn blk.px set from storage smp:spawn pos.x',
    'data modify storage smp:spawn blk.py set from storage smp:spawn pos.y',
    'data modify storage smp:spawn blk.pz set from storage smp:spawn pos.z',
    f'function {NS}:spawn/place2 with storage smp:spawn blk',
    'tag @a remove smp_sp_pend',
    f'function {NS}:core/tp with storage smp:spawn pos',
    'tellraw @a ' + msg({'text': 'Der Spawn-Platz wurde gebaut – ', 'color': 'green'}, clk('[/trigger spawn]', '/trigger spawn', 'yellow', 'Zum Spawn'), {'text': ' bringt dich hin.', 'color': 'green'}),
])
fn('spawn/scan', [            # von der Position abwaerts durch weiche Bloecke bis zum Boden; Marker auf dem Bodenblock
    'scoreboard players add #spawn_sc smp 1',
    'execute if score #spawn_sc smp matches 400.. run return 0',
    f'execute if block ~ ~ ~ #{NS}:spawn_soft positioned ~ ~-1 ~ run return run function {NS}:spawn/scan',
    'summon minecraft:marker ~ ~ ~ {Tags:["smp_sp_m"]}',
])
fn('spawn/place2', [          # with storage smp:spawn blk  (auch fuer den Neubau nach einer Versionsaenderung)
    f'$execute in minecraft:overworld positioned $(px) $(py) $(pz) run function {NS}:spawn/build_at',
    # Spieler im Bauvolumen (Zylinder r=12, y-15..y+23) auf die Mitte holen: sonst fallen sie in den freigeraeumten Platz oder stecken in Bloecken
    f'$execute in minecraft:overworld positioned $(px) $(py) $(pz) positioned ~-13 ~-16 ~-13 as @a[dx=26,dy=42,dz=26] run function {NS}:core/tp with storage smp:spawn pos',
    '$execute in minecraft:overworld run setworldspawn $(x) $(y) $(z)',
    'gamerule respawn_radius 2',
    f'scoreboard players set #spawn_v smp {SPAWN_VERSION}',
    'scoreboard players set #spawn_holo smp 1',
])

# ---------------------------------------------------------------- Minuten-Job: Platz sicherstellen (Version), Hologramme nach /reload, Leaderboards
fn('spawn/minute', ['scoreboard players set #spawn_t smp 0', f'function {NS}:spawn/ensure'])
fn('spawn/ensure', ['execute unless data storage smp:spawn blk run return 0', f'function {NS}:spawn/ensure2 with storage smp:spawn blk'])
fn('spawn/ensure2', [
    '$execute in minecraft:overworld unless loaded $(x) $(y) $(z) run return 0',
    f'execute unless score #spawn_v smp matches {SPAWN_VERSION} run return run function {NS}:spawn/place2 with storage smp:spawn blk',
    f'$execute if score #spawn_holo smp matches 0 in minecraft:overworld positioned $(px) $(py) $(pz) run return run function {NS}:spawn/holo',
    '$execute in minecraft:overworld positioned $(px) $(py) $(pz) run kill @e[type=minecraft:text_display,tag=smp_holo,distance=64..]',   # Reste eines alten Platzes
    f'$execute in minecraft:overworld positioned $(px) $(py) $(pz) run function {NS}:spawn/top_all',
])

# ---------------------------------------------------------------- der Platz (relativ zur Stehposition in der Mitte; Boden = ~-1)
build = []
for dz, w in _rows(SP_R):                                          # Untergrund: Steinziegel-Sockel bis y-15 (nur Luft/Wasser/Pflanzen ersetzen -> am Hang/Ufer eine Stuetzmauer, im Flachland unsichtbar)
    build.append(_f(-w, -SP_DEEP, dz, w, -2, dz, 'stone_bricks', f' replace #{NS}:spawn_soft'))
for dz, w in _rows(SP_R):                                          # darueber freiraeumen (Baeume, Huegel)
    build.append(_f(-w, 0, dz, w, 11, dz, 'air'))
    build.append(_f(-w, 12, dz, w, SP_CLEAR - 1, dz, 'air'))
for dz, w in _rows(SP_R):                                          # Ringstrasse
    build.append(_f(-w, -1, dz, w, -1, dz, 'stone_bricks'))
for dz, w in _rows(SP_RIN):                                        # Rasen innen
    build.append(_f(-w, -1, dz, w, -1, dz, 'grass_block'))
for x, z in ((11, 2), (-11, -2), (2, -11), (-2, 11), (9, 7), (-9, -7)):
    build.append(_s(x, -1, z, 'mossy_stone_bricks'))
for x, z in ((10, -5), (-10, 5), (5, 10), (-5, -10)):
    build.append(_s(x, -1, z, 'cracked_stone_bricks'))
build += [_f(-1, -1, -10, 1, -1, 10, 'stone_bricks'), _f(-10, -1, -1, 10, -1, 1, 'stone_bricks')]   # Wege
for dz, w in _rows(SP_RDAIS):                                      # Podest in der Mitte
    build.append(_f(-w, -1, dz, w, -1, dz, 'polished_andesite'))
for x, z in ((2, 2), (-2, 2), (2, -2), (-2, -2)):
    build.append(_s(x, -1, z, 'chiseled_stone_bricks'))
build.append(_s(0, -1, 0, 'gold_block'))                           # Mitte = Spawnpunkt
for sx in (-3, 3):                                                 # 4 Laternen-Saeulen am Podest
    for sz in (-3, 3):
        build += [_s(sx, 0, sz, 'chiseled_stone_bricks'), _f(sx, 1, sz, sx, 2, sz, 'stone_brick_wall'), _s(sx, 3, sz, 'lantern')]
for sx in (-8, 8):                                                 # 4 Laternenpfosten auf der Ringstrasse
    for sz in (-8, 8):
        build += [_f(sx, 0, sz, sx, 2, sz, 'spruce_fence'), _s(sx, 3, sz, 'lantern')]
for a, b in ((-4, -2), (2, 4)):                                    # Baenke (Treppen, Blick zur Mitte)
    build += [_f(a, 0, -6, b, 0, -6, 'spruce_stairs[facing=south]'), _f(a, 0, 6, b, 0, 6, 'spruce_stairs[facing=north]'),
              _f(-6, 0, a, -6, 0, b, 'spruce_stairs[facing=east]'), _f(6, 0, a, 6, 0, b, 'spruce_stairs[facing=west]')]
for (sx, sz), pot in zip(((6, 6), (-6, 6), (6, -6), (-6, -6)), ('red_tulip', 'blue_orchid', 'oxeye_daisy', 'allium')):
    build += [_s(sx, 0, sz, 'stone_brick_wall'), _s(sx, 1, sz, f'potted_{pot}')]
for (sx, sz), fl in zip(((5, 2), (-5, -2), (5, -2), (-5, 2), (2, 5), (-2, -5), (2, -5), (-2, 5)),
                        ('poppy', 'dandelion', 'cornflower', 'oxeye_daisy', 'azure_bluet', 'poppy', 'dandelion', 'cornflower')):
    build.append(_s(sx, 0, sz, fl))
# 3 ueberdachte Info-Waende (Nord: Befehle/Regeln, Sued: Spielzeit/Tode, Ost: Mob-Kills/Willkommen); Westen bleibt offen
for side in 'nse':
    for a, b in ((-7, -2), (2, 7)):
        if side == 'n':
            build += [_f(a, 0, -10, b, 3, -10, 'spruce_planks'), _f(a, 0, -10, a, 3, -10, 'stripped_spruce_log'), _f(b, 0, -10, b, 3, -10, 'stripped_spruce_log'),
                      _f(a, 4, -10, b, 4, -9, 'spruce_slab')]
        elif side == 's':
            build += [_f(a, 0, 10, b, 3, 10, 'spruce_planks'), _f(a, 0, 10, a, 3, 10, 'stripped_spruce_log'), _f(b, 0, 10, b, 3, 10, 'stripped_spruce_log'),
                      _f(a, 4, 9, b, 4, 10, 'spruce_slab')]
        else:
            build += [_f(10, 0, a, 10, 3, b, 'spruce_planks'), _f(10, 0, a, 10, 3, a, 'stripped_spruce_log'), _f(10, 0, b, 10, 3, b, 'stripped_spruce_log'),
                      _f(9, 4, a, 10, 4, b, 'spruce_slab')]
    for x, z in (((-2, -9), (2, -9)) if side == 'n' else ((-2, 9), (2, 9)) if side == 's' else ((9, -2), (9, 2))):
        build.append(_s(x, 3, z, 'lantern[hanging=true]'))
build.append(f'function {NS}:spawn/holo')
fn('spawn/build_at', build)

# ---------------------------------------------------------------- statische Hologramme
CMDS = [('/trigger spawn', 'zum Spawn'), ('/trigger sethome', 'Zuhause setzen'), ('/trigger home', 'nach Hause'), ('/trigger tpa', 'zu Freunden'),
        ('/trigger rtp', 'zufaelliger Ort'), ('/trigger back', 'zurueck'), ('/trigger hud', 'Anzeige an/aus'), ('/trigger stats', 'deine Statistik'),
        ('/trigger hilfe', 'alle Befehle'), ('/trigger menu', 'SMP-Menue (Esc)')]
befehle = [{'text': ''}, {'text': 'Befehle\n', 'color': 'gold', 'bold': True}]
for i, (u, t) in enumerate(CMDS):
    befehle += [{'text': u, 'color': 'yellow'}, {'text': f' – {t}' + ('\n' if i < len(CMDS) - 1 else ''), 'color': 'gray'}]
regeln = [{'text': ''}, {'text': 'Regeln\n', 'color': 'gold', 'bold': True}]
for i, r in enumerate(RULES):
    regeln += [{'text': f'{i + 1}. ', 'color': 'gold'}, {'text': r + ('\n' if i < len(RULES) - 1 else ''), 'color': 'white'}]
willkommen = [{'text': ''}, {'text': 'Willkommen!\n', 'color': 'aqua', 'bold': True}, {'text': 'Survival mit Freunden.\n', 'color': 'white'},
              {'text': '• Esc → SMP-Menü: alles per Knopf\n• /trigger hilfe: alle Befehle\n• Claim-Anker schützen dein Gebiet\n• Schlafen: 1 Spieler reicht\n• Viel Spaß!', 'color': 'gray'}]
fn('spawn/holo', [
    'kill @e[type=minecraft:text_display,tag=smp_holo]',       # global (geladene Chunks): auch alte Hologramme eines frueheren Platzes
    _holo(['smp_holo_title'], 0, 8.5, 0, {'text': SERVER_NAME, 'color': 'green', 'bold': True}, 4.0, 'center', 'center', 200, 0),
    _holo(['smp_holo_sub'], 0, 7.7, 0, {'text': 'Survival mit Freunden', 'color': 'white'}, 1.4, 'center', 'center', 200, 0),
    _holo(['smp_holo_cmd'], -4.5, 0.9, -9, befehle, 1.0, width=200),          # 11 Zeilen * 0.25 = 2.75 -> Oberkante 3.65 (Dach bei 4.0)
    _holo(['smp_holo_rules'], 4.5, 0.8, -9, regeln, 0.9, width=200),          # ~13 Zeilen * 0.225 = 2.9 -> 3.7
    _holo(['smp_holo_welcome'], 9, 1.2, 4.5, willkommen, 1.1, width=180),     # ~8 Zeilen * 0.275 = 2.2 -> 3.4
    f'function {NS}:spawn/top_all',
    'scoreboard players set #spawn_holo smp 1',
])

# ---------------------------------------------------------------- Leaderboards (Top 5 ueber alle bekannten Namen, auch offline), alle 60 s neu
BOARDS = [  # key, Objective fuers Ranking, Mindestwert, Titel, Position (dx, dy, dz)
    ('hours', 'smp_pt', 7200, 'Spielzeit', (-4.5, 1.6, 9)),     # 6 Zeilen * 0.3 = 1.8 -> Oberkante 3.4 (Dach bei 4.0)
    ('tode', 'smp_tode', 1, 'Tode', (4.5, 1.6, 9)),
    ('kills', 'smp_mkills', 1, 'Mob-Kills', (9, 1.6, -4.5)),
]
RANK_COLORS = ['gold', '#C0C0C0', '#CD7F32', 'white', 'white']
fn('spawn/take', ['$scoreboard players set $(cand) smp_sp_pick 1', '$data modify storage smp:tmp top append value {name:"$(cand)"}'])
fn('spawn/top_all', ['kill @e[type=minecraft:text_display,tag=smp_holo_top,distance=..64]', *[f'function {NS}:spawn/top_{k}' for k, *_ in BOARDS]])
for key, obj, minv, title, (dx, dy, dz) in BOARDS:
    rank = ['scoreboard players reset * smp_sp_pick', 'data remove storage smp:tmp top']
    for i in range(5):
        rank += [f'scoreboard players set #max smp {minv - 1}', 'data remove storage smp:tmp cand', 'data remove storage smp:tmp names',
                 'data modify storage smp:tmp names set from storage smp:spawn players',
                 f'execute if data storage smp:tmp names[0] run function {NS}:spawn/scan_{key}',
                 f'execute if data storage smp:tmp cand run function {NS}:spawn/take with storage smp:tmp']
    fn(f'spawn/scan_{key}', [f'function {NS}:spawn/cmp_{key} with storage smp:tmp names[0]', 'data remove storage smp:tmp names[0]',
                             f'execute if data storage smp:tmp names[0] run function {NS}:spawn/scan_{key}'])
    fn(f'spawn/cmp_{key}', [f'$execute unless score $(name) smp_sp_pick matches 1 if score $(name) {obj} > #max smp run function {NS}:spawn/cand_{key} {{name:"$(name)"}}'])
    fn(f'spawn/cand_{key}', [f'$scoreboard players operation #max smp = $(name) {obj}', '$data modify storage smp:tmp cand set value "$(name)"'])
    # Zeilen formatieren: args.l1..l5
    fmt = ['data modify storage smp:tmp args set value {l1:"",l2:"",l3:"",l4:"",l5:""}']
    for i in range(5):
        fmt += [f'data modify storage smp:tmp fv set value {{i:{i + 1}}}',
                f'data modify storage smp:tmp fv.name set from storage smp:tmp top[{i}].name',
                f'execute if data storage smp:tmp top[{i}] run function {NS}:spawn/fmt_{key} with storage smp:tmp fv']
    if key == 'hours':
        fn(f'spawn/fmt_{key}', [f'$execute store result score #v smp run scoreboard players get $(name) {obj}',
                                'scoreboard players operation #v smp /= #7200 smp',
                                'scoreboard players operation #h smp = #v smp', 'scoreboard players operation #h smp /= #10 smp',
                                'scoreboard players operation #d smp = #v smp', 'scoreboard players operation #d smp %= #10 smp',
                                'execute store result storage smp:tmp fv.h int 1 run scoreboard players get #h smp',
                                'execute store result storage smp:tmp fv.d int 1 run scoreboard players get #d smp',
                                f'function {NS}:spawn/fmt2_{key} with storage smp:tmp fv'])
        fn(f'spawn/fmt2_{key}', ['$data modify storage smp:tmp args.l$(i) set value "$(i). $(name) – $(h),$(d) h"'])
    else:
        fn(f'spawn/fmt_{key}', [f'$execute store result storage smp:tmp fv.v int 1 run scoreboard players get $(name) {obj}',
                                f'function {NS}:spawn/fmt2_{key} with storage smp:tmp fv'])
        fn(f'spawn/fmt2_{key}', ['$data modify storage smp:tmp args.l$(i) set value "$(i). $(name) – $(v)"'])
    show = [f'execute if data storage smp:tmp top[{n - 1}] run return run function {NS}:spawn/show_{key}_{n} with storage smp:tmp args' for n in range(5, 0, -1)]
    show.append(f'function {NS}:spawn/show_{key}_0')
    fn(f'spawn/top_{key}', rank + fmt + show)
    for n in range(6):
        text = [{'text': ''}, {'text': f'{title} (Top 5)' + ('\n' if n else ''), 'color': 'gold', 'bold': True}]
        if n == 0:
            text.append({'text': '\nNoch niemand', 'color': 'gray'})
        for i in range(n):
            text.append({'text': f'$(l{i + 1})' + ('\n' if i < n - 1 else ''), 'color': RANK_COLORS[i]})
        fn(f'spawn/show_{key}_{n}', [('$' if n else '') + _holo(['smp_holo_top'], dx, dy, dz, text, 1.2, width=170)])
