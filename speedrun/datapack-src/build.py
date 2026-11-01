#!/usr/bin/env python3
"""Speedrun-Datapack v3 (Minecraft 26.3, data pack format 121).

Modi: Solo, Duo, Trio, Squad, Koop. Bei mehreren Teams ist es ein Rennen:
jedes Team startet an einem eigenen Ort, wer zuerst den Drachen tötet, gewinnt.

Run:  python3 build.py <out_dir>   -> <out_dir>/speedrun/ und <out_dir>/speedrun.zip
"""
import json, math, os, random, shutil, sys, zipfile

OUT = sys.argv[1] if len(sys.argv) > 1 else 'out'
MIN_FORMAT = int(sys.argv[2]) if len(sys.argv) > 2 else 121
ROOT = os.path.join(OUT, 'speedrun')
NS = 'sr'
BUILD_VERSION = 3
files = {}


def fn(path, lines):
    files[f'data/{NS}/function/{path}.mcfunction'] = '\n'.join(lines) + '\n'


def js(path, obj):
    files[path] = json.dumps(obj, ensure_ascii=False, indent=2) + '\n'


def tc(obj):
    return json.dumps(obj, ensure_ascii=False)


PREFIX = {'text': '» ', 'color': 'gold', 'bold': True}
def msg(*parts):
    return tc([PREFIX] + list(parts))

# ------------------------------------------------------------------ config
OW = 'execute in minecraft:overworld run'
LOBBY_Y = 199
MODES = {1: ('Solo', 1), 2: ('Duo', 2), 3: ('Trio', 3), 4: ('Squad', 4), 5: ('Koop', 99)}
MODE_INFO = {1: 'Jeder gegen jeden', 2: 'Teams aus 2', 3: 'Teams aus 3', 4: 'Teams aus 4', 5: 'Alle in einem Team'}
TEAMS = {1: ('red', 'Rot'), 2: ('blue', 'Blau'), 3: ('green', 'Grün'), 4: ('yellow', 'Gelb'),
         5: ('aqua', 'Türkis'), 6: ('light_purple', 'Lila'), 7: ('gold', 'Orange'), 8: ('white', 'Weiß')}
ROLES = {
    0: ('Solo', 'Alles selbst: Portal, Blaze-Ruten, Perlen, Stronghold, Drache'),
    1: ('Kämpfer', 'Festung, 7 Blaze-Ruten, Käfig-Kristalle, Drache mit Betten sprengen'),
    2: ('Portal & Perlen', 'Portal (Wasser + Lava), Bastion, Gold gegen 12 Perlen tauschen'),
    3: ('Versorger', 'Eimer, Feuerzeug, 7 Betten und Essen für das Team'),
    4: ('Späher', 'Enderaugen craften, Stronghold orten, Endportal öffnen'),
    5: ('Nether-Läufer', 'Festung + Bastion: 7 Blaze-Ruten und 12 Perlen'),
    6: ('Versorger & Wegfinder', 'Portal, Betten, Essen, Enderaugen, Stronghold'),
}
PREFS = {1: ('Kämpfer', 'orange_concrete', 'gold', -6), 2: ('Portal & Perlen', 'purple_concrete', 'light_purple', -2),
         3: ('Versorger', 'green_concrete', 'green', 2), 4: ('Späher', 'light_blue_concrete', 'aqua', 6)}
TASKS = [
    ('gear', 'Schild + Eisenschwert'), ('tools', 'Eimer + Feuerzeug'), ('nether', 'Nether betreten'),
    ('fortress', 'Festung gefunden'), ('bastion', 'Bastion gefunden'), ('blaze', 'Blaze-Ruten'),
    ('pearls', 'Enderperlen'), ('beds', 'Betten'), ('food', 'Essen'), ('eyes', 'Enderaugen'),
    ('stronghold', 'Stronghold gefunden'), ('end', 'End betreten'), ('dragon', 'Drache besiegt'),
]
NT = len(TASKS)
# counted tasks: key -> (needed amount, divisor for display)
NEED = {'blaze': (7, 2), 'pearls': (12, 1), 'beds': (7, 1), 'food': (20, 1), 'eyes': (12, 1)}
FOOD = ['cooked_beef', 'cooked_porkchop', 'cooked_mutton', 'cooked_chicken', 'cooked_rabbit',
        'cooked_cod', 'cooked_salmon', 'bread', 'baked_potato', 'golden_carrot']
STEPS = {
    0: [('tools', 'Eimer + Feuerzeug bauen'), ('nether', 'Portal gießen, ab in den Nether'), ('fortress', 'Festung finden'),
        ('blaze', 'Blaze-Ruten farmen'), ('pearls', 'Bastion: Gold gegen Perlen tauschen'), ('beds', 'Wolle sammeln, Betten craften'),
        ('eyes', 'Enderaugen craften'), ('stronghold', 'Augen werfen, Stronghold finden'), ('end', 'Endportal öffnen und rein'),
        ('dragon', 'Drachen töten')],
    1: [('gear', 'Schild + Eisenschwert bauen'), ('nether', 'Durchs Portal in den Nether'), ('fortress', 'Festung finden'),
        ('blaze', 'Blaze-Ruten farmen'), ('stronghold', 'Zum Stronghold'), ('end', 'Ins End'),
        ('dragon', 'Käfig-Kristalle zerstören, Drachen mit Betten sprengen')],
    2: [('tools', 'Eimer + Feuerzeug bauen'), ('nether', 'Portal mit Wasser + Lava gießen'), ('bastion', 'Bastion finden, Piglins einmauern'),
        ('pearls', 'Gold gegen Perlen tauschen'), ('stronghold', 'Zum Stronghold'), ('end', 'Ins End'), ('dragon', 'Kristalle abschießen')],
    3: [('beds', 'Wolle sammeln, Betten craften'), ('food', 'Essen braten für alle'), ('nether', 'In den Nether, beim Tauschen helfen'),
        ('eyes', 'Enderaugen craften'), ('stronghold', 'Augen werfen, Stronghold finden'), ('end', 'Ins End'),
        ('dragon', 'Betten bereithalten, Endermen nicht anschauen')],
    4: [('gear', 'Schild + Eisenschwert bauen'), ('nether', 'In den Nether'), ('eyes', 'Enderaugen craften'),
        ('stronghold', 'Augen werfen, Stronghold finden'), ('end', 'Endportal öffnen und rein'), ('dragon', 'Kristalle abschießen, Drachen töten')],
    5: [('nether', 'In den Nether'), ('fortress', 'Festung finden'), ('blaze', 'Blaze-Ruten farmen'), ('bastion', 'Bastion finden'),
        ('pearls', 'Gold gegen Perlen tauschen'), ('stronghold', 'Zum Stronghold'), ('end', 'Ins End'), ('dragon', 'Drachen töten')],
    6: [('tools', 'Eimer + Feuerzeug, Portal gießen'), ('beds', 'Betten craften'), ('food', 'Essen braten'), ('nether', 'In den Nether'),
        ('eyes', 'Enderaugen craften'), ('stronghold', 'Stronghold finden'), ('end', 'Ins End'), ('dragon', 'Drachen mit Betten sprengen')],
}
SLOTS = {1: 'gold', 2: 'light_purple', 3: 'green', 4: 'aqua', 5: 'red', 6: 'blue', 7: 'yellow', 8: 'white',
         9: 'dark_green', 10: 'dark_aqua', 11: 'dark_red', 12: 'dark_purple', 13: 'gray', 14: 'dark_blue', 15: 'dark_gray', 16: 'black'}
STEP_KEYS = sorted({k for steps in STEPS.values() for k, _ in steps})
TEAM_LINES = [('blaze', 'Blaze-Ruten'), ('pearls', 'Enderperlen'), ('eyes', 'Enderaugen'), ('stronghold', 'Stronghold'), ('dragon', 'Drache')]
# run time in the actionbar (sr:run tstr is formatted once per second by time/fmt)
TIME_BAR = [{'text': '⏱ ', 'color': 'white', 'bold': False}, {'nbt': 'tstr', 'storage': 'sr:run', 'interpret': True, 'color': 'white', 'bold': True},
            {'text': '  ·  ', 'color': 'dark_gray', 'bold': False}]
BAR_COLOR = {'red': 'red', 'blue': 'blue', 'green': 'green', 'yellow': 'yellow', 'aqua': 'blue',
             'light_purple': 'pink', 'gold': 'yellow', 'white': 'white'}


def positions(n=60, rmin=2500, rmax=20000, sep=3200, seed=7):
    rnd, pts = random.Random(seed), []
    for _ in range(200000):
        if len(pts) >= n:
            break
        r = math.sqrt(rnd.uniform(rmin * rmin, rmax * rmax)); a = rnd.uniform(0, 2 * math.pi)
        x, z = int(r * math.cos(a)) // 16 * 16 + 8, int(r * math.sin(a)) // 16 * 16 + 8
        if all((x - px) ** 2 + (z - pz) ** 2 >= sep * sep for px, pz in pts):
            pts.append((x, z))
    return pts
POS = positions()

# ------------------------------------------------------------------ meta, tags, dialog
js('pack.mcmeta', {'pack': {'description': 'Speedrun 2.0: Solo, Duo, Trio, Squad, Koop',
                            'min_format': MIN_FORMAT, 'max_format': [121, 999]}})
js('data/minecraft/tags/function/load.json', {'values': [f'{NS}:load']})
js('data/minecraft/tags/function/tick.json', {'values': [f'{NS}:tick']})
js('data/minecraft/tags/dialog/pause_screen_additions.json', {'values': [f'{NS}:menu']})
js('data/minecraft/tags/dialog/quick_actions.json', {'values': [f'{NS}:menu']})


def btn(label, tooltip, cmd, width=150):
    return {'label': label, 'tooltip': {'text': tooltip}, 'width': width,
            'action': {'type': 'run_command', 'command': cmd}}

actions = []
for m, (name, size) in MODES.items():
    actions.append(btn({'text': f'Modus: {name}', 'color': 'yellow'}, MODE_INFO[m], f'trigger sr_aktion set {10 + m}'))
actions.append(btn({'text': '▶ Run starten', 'color': 'green', 'bold': True}, 'Countdown startet für alle, die nicht zuschauen', 'trigger sr_aktion set 1'))
for p, (name, _, color, _) in PREFS.items():
    actions.append(btn({'text': f'Wunschrolle: {name}', 'color': color}, ROLES[p][1], f'trigger sr_rolle set {p}'))
actions += [
    btn({'text': '✎ Speedrun-Zettel', 'color': 'gold'}, 'Items, Team-Stand, Aufgaben und Zeit', 'trigger sr_aktion set 9'),
    btn({'text': '☰ Mein Plan', 'color': 'gold'}, 'Alle Schritte deiner Rolle', 'trigger sr_aktion set 7'),
    btn({'text': '➤ Position ans Team'}, 'Schickt deinem Team deine Koordinaten', 'trigger sr_aktion set 8'),
    btn({'text': '◎ Zuschauen an/aus'}, 'Beim nächsten Run zuschauen oder jetzt live zuschauen', 'trigger sr_aktion set 4'),
    btn({'text': '⌂ Zurück zur Lobby'}, 'Verlässt den Run und leert dein Inventar', 'trigger sr_aktion set 2'),
    btn({'text': '✖ Run abbrechen', 'color': 'red'}, 'Beendet den laufenden Run für alle', 'trigger sr_aktion set 6'),
]
js(f'data/{NS}/dialog/menu.json', {
    'type': 'minecraft:multi_action',
    'title': {'text': 'SPEEDRUN', 'color': 'gold', 'bold': True},
    'external_title': {'text': 'Speedrun-Menü'},
    'body': {'type': 'minecraft:plain_message', 'width': 310,
             'contents': [{'text': 'Modus wählen, Run starten. Bei mehreren Teams ist es ein Rennen: '},
                          {'text': 'wer zuerst den Drachen tötet, gewinnt.', 'color': 'gold'}]},
    'columns': 2,
    'actions': actions,
    'exit_action': {'label': {'text': 'Schließen'}, 'width': 200},
})

# ------------------------------------------------------------------ load
load = [
    f'{OW} forceload add -16 -16 15 15',
    # v1 cleanup
    'scoreboard objectives remove sr_ole', 'scoreboard objectives remove sr_mats', 'scoreboard objectives remove sr_sammy',
    'team remove sr_ole', 'team remove sr_mats', 'team remove sr_sammy',
    'scoreboard objectives add sr dummy',
    'scoreboard objectives add sr_tmp dummy',
    'scoreboard objectives add sr_done dummy',
    'scoreboard objectives add sr_rolle trigger',
    'scoreboard objectives add sr_aktion trigger',
    'scoreboard objectives add sr_leave minecraft.custom:minecraft.leave_game',
    'scoreboard objectives add sr_endt dummy',
    'scoreboard objectives add sr_pref dummy',
    'scoreboard objectives add sr_role dummy',
    'scoreboard objectives add sr_team dummy',
    'scoreboard objectives add sr_click minecraft.used:minecraft.carrot_on_a_stick',
    'scoreboard objectives add sr_slot dummy',
    'scoreboard objectives add sr_zcd dummy',
    'scoreboard objectives add sr_sx dummy', 'scoreboard objectives add sr_sy dummy', 'scoreboard objectives add sr_sz dummy',
    'scoreboard objectives add sr_pu_blaze minecraft.picked_up:minecraft.blaze_rod',
    'scoreboard objectives add sr_pu_pearl minecraft.picked_up:minecraft.ender_pearl',
    'scoreboard objectives add sr_cr_eye minecraft.crafted:minecraft.ender_eye',
    *[f'scoreboard objectives add sr_cr_f{i} minecraft.crafted:minecraft.{f}' for i, f in enumerate(FOOD)],
    *[f'scoreboard objectives add sr_d_{k} dummy' for k in STEP_KEYS],
    *[f'scoreboard objectives add sr_v_{k} dummy' for k in NEED],
    f'scoreboard objectives add sr_wins dummy {tc({"text": "Siege", "color": "gold"})}',
    'scoreboard objectives setdisplay list sr_wins',
    f'scoreboard objectives add sr_lobby dummy {tc({"text": "SPEEDRUN", "color": "gold", "bold": True})}',
    'scoreboard objectives modify sr_lobby numberformat blank',
    'scoreboard objectives setdisplay sidebar sr_lobby',
]
for n, (color, cname) in TEAMS.items():
    load += [
        f'team remove sr_t{n}',
        f'scoreboard objectives add sr_s{n} dummy {tc({"text": "Team " + cname, "color": color, "bold": True})}',
        f'scoreboard objectives modify sr_s{n} numberformat blank',
        f'bossbar add {NS}:t{n} {tc({"text": "Team " + cname})}',
        f'bossbar set {NS}:t{n} color {BAR_COLOR[color]}',
        f'bossbar set {NS}:t{n} style notched_12',
        f'bossbar set {NS}:t{n} max {NT}',
    ]
for k, color in SLOTS.items():
    load += [
        f'team add sr_p{k}',
        f'team modify sr_p{k} color {color}',
        f'team modify sr_p{k} friendlyFire false',
        f'team modify sr_p{k} nametagVisibility always',
        f'scoreboard objectives add sr_o{k} dummy',
        f'scoreboard objectives modify sr_o{k} numberformat blank',
        f'scoreboard objectives setdisplay sidebar.team.{color} sr_o{k}',
    ]
load += [
    'scoreboard players set #20 sr 20', 'scoreboard players set #60 sr 60', 'scoreboard players set #2 sr 2', 'scoreboard players set #5 sr 5',
    'scoreboard players set #3600 sr 3600',
    'execute unless data storage sr:run tstr run data modify storage sr:run tstr set value "0:00"',
    f'scoreboard players set #npos sr {len(POS)}',
    'execute unless score #run sr matches 0.. run scoreboard players set #run sr 0',
    'execute unless score #active sr matches 0.. run scoreboard players set #active sr 0',
    'execute unless score #mode sr matches 1..5 run scoreboard players set #mode sr 3',
    'execute unless score #nextslot sr matches 0.. run scoreboard players set #nextslot sr 0',
    'scoreboard players set #cd sr 0',
    f'function {NS}:mode/apply_silent',
    'gamerule respawn_radius 0',
    'gamerule pvp false',
    'gamerule spawn_phantoms false',
    'gamerule locator_bar true',
    'gamerule show_advancement_messages false',
    'setworldspawn 0 200 0',
    f'{OW} forceload add -16 -16 15 15',
    f'function {NS}:sidebar/lobby',
    f'execute unless score #built sr matches {BUILD_VERSION} run schedule function {NS}:lobby/try_build 40t',
]
fn('load', load)

# ------------------------------------------------------------------ tick
# one-shot item gifts on request of the server owner: (id, player, {item: count}); each is given once (flag #gift_<id>)
GIFTS = [('g1', 'FNGreg', {'minecraft:obsidian': 10, 'minecraft:flint_and_steel': 1}, '10 Obsidian und 1 Feuerzeug')]
for _gid, _who, _items, _label in GIFTS:
    fn(f'gift/{_gid}', [f'scoreboard players set #gift_{_gid} sr 1', *[f'give {_who} {it} {n}' for it, n in _items.items()],
                        f'tellraw {_who} ' + msg({'text': 'Geschenk erhalten: ' + _label, 'color': 'green'})])
fn('tick', [
    'scoreboard players enable @a sr_rolle',
    'scoreboard players enable @a sr_aktion',
    f'execute as @a[tag=!sr_seen2] run function {NS}:player/first_join',
    f'execute as @a[scores={{sr_leave=1..}}] run function {NS}:player/rejoin',
    f'execute as @a[scores={{sr_rolle=1..}}] run function {NS}:role/pref',
    f'execute as @a[scores={{sr_aktion=1..}}] run function {NS}:player/action',
    f'execute as @a[scores={{sr_click=1..}}] run function {NS}:item/click',
    'scoreboard players add #itick sr 1',
    'scoreboard players add #ztick sr 1',
    f'execute if score #ztick sr matches 4.. run function {NS}:zettel/tick',
    'execute if score #itick sr matches 10.. run function sr:item/sweep',
    f'execute as @a[tag=sr_lobby] run function {NS}:lobby/keep',
    f'execute if score #cd sr matches 1.. run function {NS}:start/cd_tick',
    f'execute if score #active sr matches 1 run function {NS}:run/tick',
    *[f'execute unless score #gift_{gid} sr matches 1 if entity @e[type=minecraft:player,name={who}] run function {NS}:gift/{gid}' for gid, who, *_ in GIFTS],
])

# ------------------------------------------------------------------ lobby island
def disk(y, r, block):
    out = []
    for z in range(-r, r + 1):
        w = int(math.floor(math.sqrt(r * r + r - z * z)))
        out.append(f'fill {-w} {y} {z} {w} {y} {z} minecraft:{block}')
    return out


def sign(x, y, z, rot, lines, color, wood='dark_oak'):
    msgs = [{'text': lines[0], 'color': color, 'bold': True}] + [{'text': l} for l in lines[1:]]
    while len(msgs) < 4:
        msgs.append({'text': ''})
    nbt = '{front_text:{has_glowing_text:true,messages:[' + ','.join(tc(m) for m in msgs) + ']}}'
    return f'{OW} setblock {x} {y} {z} minecraft:{wood}_sign[rotation={rot}]{nbt}'


def holo(tag, x, y, z, text, scale=1.0, extra=''):
    return (f'{OW} summon minecraft:text_display {x} {y} {z} {{Tags:["sr_holo","{tag}"],billboard:"center",'
            f'background:0,shadow:true,{extra}text:{tc(text)},transformation:{{left_rotation:[0f,0f,0f,1f],'
            f'right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[{scale}f,{scale}f,{scale}f]}}}}')

build = ['kill @e[type=minecraft:text_display,tag=sr_holo]']
build += [f'{OW} {c}' for c in (
    ['fill -14 190 -14 14 212 14 minecraft:air']
    + disk(LOBBY_Y, 10, 'grass_block') + disk(LOBBY_Y - 1, 9, 'dirt') + disk(LOBBY_Y - 2, 8, 'dirt')
    + disk(LOBBY_Y - 3, 7, 'stone') + disk(LOBBY_Y - 4, 5, 'stone') + disk(LOBBY_Y - 5, 3, 'cobblestone')
    + disk(LOBBY_Y - 6, 1, 'cobblestone')
    # path ring + centre plate
    + ['fill -1 199 -1 1 199 1 minecraft:polished_andesite', 'setblock 0 199 0 minecraft:gold_block']
)]
for x, z in [(-8, -6), (8, -6), (-8, 6), (8, 6), (0, -9), (0, 9)]:
    build += [f'{OW} setblock {x} 200 {z} minecraft:oak_fence', f'{OW} setblock {x} 201 {z} minecraft:lantern']
for x, z in [(-6, 2), (6, 2), (-3, 8), (3, -8), (-8, 0), (8, 0)]:
    build += [f'{OW} setblock {x} 200 {z} minecraft:potted_poppy']
build += [
    holo('sr_holo_title', 0, 205.0, -7, {'text': 'SPEEDRUN', 'color': 'gold', 'bold': True}, 4.0),
    holo('sr_holo_sub', 0, 204.2, -7, {'text': 'Wer killt den Drachen zuerst?', 'color': 'gray'}, 1.4),
    holo('sr_holo_hint', 0, 201.6, -3, [{'text': 'Rechtsklick auf die Items in deiner Hotbar', 'color': 'white'}], 1.0),
    f'function {NS}:mode/apply_silent',
    f'function {NS}:holo/leaderboard',
    f'scoreboard players set #built sr {BUILD_VERSION}',
]
fn('lobby/build', build)
fn('lobby/try_build', [
    f'execute in minecraft:overworld if loaded 0 {LOBBY_Y} 0 if loaded 10 {LOBBY_Y} 10 if loaded -10 {LOBBY_Y} -10 run return run function {NS}:lobby/build',
    f'schedule function {NS}:lobby/try_build 20t',
])

fn('lobby/keep', [
    'effect give @s minecraft:resistance infinite 4 true',
    'effect give @s minecraft:saturation infinite 0 true',
    'execute unless entity @s[gamemode=adventure] unless entity @s[gamemode=creative] run gamemode adventure @s',
    f'execute at @s unless dimension minecraft:overworld run function {NS}:player/tp_lobby',
    f'execute at @s if dimension minecraft:overworld unless entity @s[y=185,dy=200] run function {NS}:player/tp_lobby',
    f'execute at @s if dimension minecraft:overworld unless entity @s[x=-40,dx=80,z=-40,dz=80] run function {NS}:player/tp_lobby',
    f'execute if entity @s[tag=sr_refresh] run return run function {NS}:item/hotbar',
    *[f'execute unless items entity @s hotbar.{slot} *[minecraft:custom_data~{{sr:"{key}"}}] run return run function {NS}:item/hotbar' for slot, key in ((0, 'start'), (1, 'mode'), (2, 'role'), (4, 'watch'), (8, 'menu'))],
])

# holograms: mode line + leaderboard
mode_apply = ['kill @e[type=minecraft:text_display,tag=sr_holo_mode]']
for m, (name, size) in MODES.items():
    mode_apply += [
        f'execute if score #mode sr matches {m} run data modify storage sr:run mode set value "{name}"',
        f'execute if score #mode sr matches {m} run ' + holo('sr_holo_mode', 0, 203.5, -7,
            [{'text': 'Modus: ', 'color': 'white'}, {'text': name, 'color': 'yellow', 'bold': True},
             {'text': '  ·  ' + MODE_INFO[m], 'color': 'gray'}], 1.4),
    ]
fn('mode/apply_silent', mode_apply)
fn('mode/apply', [
    f'function {NS}:mode/apply_silent',
    'tag @a[tag=sr_lobby] add sr_refresh',
    f'tellraw @a {msg({"text": "Modus: ", "color": "gray"}, {"nbt": "mode", "storage": "sr:run", "interpret": True, "color": "yellow", "bold": True})}',
    'execute as @a at @s run playsound minecraft:block.note_block.bell master @s ~ ~ ~ 0.8 1.2',
])
fn('mode/cycle', ['scoreboard players add #mode sr 1', 'execute if score #mode sr matches 6.. run scoreboard players set #mode sr 1',
                  f'function {NS}:mode/apply'])

lb = ['kill @e[type=minecraft:text_display,tag=sr_holo_lb]',
      holo('sr_holo_lb', 0, 204.6, 9, {'text': 'BESTZEITEN', 'color': 'gold', 'bold': True}, 1.6)]
for i, (m, (name, _)) in enumerate(MODES.items()):
    y = round(204.0 - i * 0.38, 2)
    lb += [
        f'scoreboard players operation #lbs sr = #best{m} sr',
        'scoreboard players operation #lbs sr /= #20 sr',
        'scoreboard players operation #lbm sr = #lbs sr',
        'scoreboard players operation #lbm sr /= #60 sr',
        'scoreboard players operation #lbs sr %= #60 sr',
        f'execute unless score #best{m} sr matches 1.. run ' + holo('sr_holo_lb', 0, y, 9, [{'text': f'{name}  ', 'color': 'yellow'}, {'text': '–:––', 'color': 'dark_gray'}], 1.1),
        f'execute if score #best{m} sr matches 1.. if score #lbs sr matches 10.. run ' + holo('sr_holo_lb', 0, y, 9, [{'text': f'{name}  ', 'color': 'yellow'}, {'score': {'name': '#lbm', 'objective': 'sr'}, 'color': 'white'}, {'text': ':', 'color': 'white'}, {'score': {'name': '#lbs', 'objective': 'sr'}, 'color': 'white'}], 1.1),
        f'execute if score #best{m} sr matches 1.. if score #lbs sr matches ..9 run ' + holo('sr_holo_lb', 0, y, 9, [{'text': f'{name}  ', 'color': 'yellow'}, {'score': {'name': '#lbm', 'objective': 'sr'}, 'color': 'white'}, {'text': ':0', 'color': 'white'}, {'score': {'name': '#lbs', 'objective': 'sr'}, 'color': 'white'}], 1.1),
    ]
fn('holo/leaderboard', lb)

# ------------------------------------------------------------------ player
fn('player/tp_lobby', [f'{OW} tp @s 0 200 0 180 0'])
fn('player/to_lobby', [
    'team leave @s',
    'tag @s remove sr_run', 'tag @s remove sr_spec', 'tag @s add sr_lobby',
    'scoreboard players set @s sr_role -1', 'scoreboard players set @s sr_team 0', 'scoreboard players set @s sr_slot 0',
    f'function {NS}:player/reset_state',
    'gamemode adventure @s',
    f'function {NS}:player/tp_lobby',
    f'{OW} spawnpoint @s 0 200 0',
    'waypoint modify @s color reset',
    f'function {NS}:item/hotbar',
])
fn('player/reset_state', [
    'clear @s',
    *[f'item replace entity @s enderchest.{i} with minecraft:air' for i in range(27)],
    'effect clear @s',
    'experience set @s 0 levels', 'experience set @s 0 points',
    'effect give @s minecraft:instant_health 1 10 true',
    'effect give @s minecraft:saturation 1 20 true',
    'advancement revoke @s everything',
    'scoreboard players set @s sr_endt 0',
    f'function {NS}:zettel/keep',
])
clk = lambda t, cmd, color='aqua', hover=None: dict({'text': t, 'color': color, 'bold': False,
                                                    'click_event': {'action': 'run_command', 'command': cmd}},
                                                   **({'hover_event': {'action': 'show_text', 'value': hover}} if hover else {}))
welcome = [
    {'text': '\n'}, {'text': ' SPEEDRUN ', 'color': 'black', 'bold': True},
    {'text': '  Willkommen!\n', 'color': 'gold', 'bold': True},
    {'text': ' Modus: ', 'color': 'gray', 'bold': False},
    clk('[Solo]', '/trigger sr_aktion set 11', 'yellow'), {'text': ' '},
    clk('[Duo]', '/trigger sr_aktion set 12', 'yellow'), {'text': ' '},
    clk('[Trio]', '/trigger sr_aktion set 13', 'yellow'), {'text': ' '},
    clk('[Squad]', '/trigger sr_aktion set 14', 'yellow'), {'text': ' '},
    clk('[Koop]', '/trigger sr_aktion set 15', 'yellow'),
    {'text': '\n Wunschrolle: ', 'color': 'gray', 'bold': False},
    clk('[Kämpfer]', '/trigger sr_rolle set 1', 'gold', ROLES[1][1]), {'text': ' '},
    clk('[Portal & Perlen]', '/trigger sr_rolle set 2', 'light_purple', ROLES[2][1]), {'text': ' '},
    clk('[Versorger]', '/trigger sr_rolle set 3', 'green', ROLES[3][1]), {'text': ' '},
    clk('[Späher]', '/trigger sr_rolle set 4', 'aqua', ROLES[4][1]),
    {'text': '\n ', 'bold': False}, clk('[▶ RUN STARTEN]', '/trigger sr_aktion set 1', 'green'),
    {'text': '   ', 'bold': False}, clk('[Menü]', '/trigger sr_aktion set 3', 'aqua'),
    {'text': '   Esc → Speedrun-Menü\n', 'color': 'dark_gray', 'bold': False},
    {'text': ' Dein ', 'color': 'gray', 'bold': False}, {'text': 'Speedrun-Zettel', 'color': 'gold', 'bold': False},
    {'text': ' (Slot 8, immer dabei): Rechtsklick zeigt alle Items, den Team-Stand und die Zeit.\n', 'color': 'gray', 'bold': False},
]
fn('player/welcome', [f'tellraw @s {tc(welcome)}'])
fn('player/first_join', [
    'tag @s add sr_seen2', 'scoreboard players set @s sr_leave 0',
    f'function {NS}:player/to_lobby', f'function {NS}:player/welcome',
    'title @s times 10 50 15',
    f'title @s title {tc({"text": "SPEEDRUN", "color": "gold", "bold": True})}',
    f'title @s subtitle {tc({"text": "Rechtsklick auf die Items in deiner Hotbar", "color": "gray"})}',
])
fn('player/rejoin', [
    'scoreboard players set @s sr_leave 0',
    f'execute unless entity @s[tag=sr_run] unless entity @s[tag=sr_spec] run function {NS}:player/to_lobby',
    f'execute if entity @s[tag=sr_spec] if score #active sr matches 0 run function {NS}:player/to_lobby',
    f'execute if entity @s[tag=sr_run] if score #active sr matches 0 run function {NS}:player/to_lobby',
    f'execute if entity @s[tag=sr_lobby] run function {NS}:player/welcome',
])
fn('player/action', [
    f'execute if score @s sr_aktion matches 1 run function {NS}:start/by_player',
    f'execute if score @s sr_aktion matches 2 run function {NS}:player/to_lobby',
    f'execute if score @s sr_aktion matches 3 run dialog show @s {NS}:menu',
    f'execute if score @s sr_aktion matches 4 run function {NS}:player/watch',
    f'execute if score @s sr_aktion matches 5 run function {NS}:mode/cycle',
    f'execute if score @s sr_aktion matches 6 run function {NS}:run/abort',
    f'execute if score @s sr_aktion matches 7 run function {NS}:role/plan',
    f'execute if score @s sr_aktion matches 8 run function {NS}:fx/share_me',
    f'execute if score @s sr_aktion matches 9 run function {NS}:zettel/open',
    *[f'execute if score @s sr_aktion matches {10 + m} run function {NS}:mode/set {{m:{m}}}' for m in MODES],
    'scoreboard players set @s sr_aktion 0',
])
fn('mode/set', ['$scoreboard players set #mode sr $(m)', f'function {NS}:mode/apply'])
fn('player/watch', [
    f'execute if score #active sr matches 1 unless entity @s[tag=sr_run] run return run function {NS}:player/spectate',
    f'execute if entity @s[tag=sr_watch] run return run function {NS}:player/watch_off',
    'tag @s add sr_watch',
    'tag @s add sr_refresh',
    f'tellraw @s {msg({"text": "Du schaust beim nächsten Run zu. ", "color": "aqua"}, clk("[Doch mitspielen]", "/trigger sr_aktion set 4", "green"))}',
])
fn('player/watch_off', ['tag @s remove sr_watch', 'tag @s add sr_refresh', f'tellraw @s {msg({"text": "Du spielst beim nächsten Run mit.", "color": "green"})}'])
fn('player/spectate', [
    'tag @s remove sr_lobby', 'tag @s add sr_spec', 'effect clear @s',
    'gamemode spectator @s',
    'tp @s @r[tag=sr_run]',
    f'tellraw @s {msg({"text": "Du schaust live zu. ", "color": "aqua"}, clk("[Zurück zur Lobby]", "/trigger sr_aktion set 2"))}',
])

# ------------------------------------------------------------------ roles
fn('role/pref', [
    *[f'execute if score @s sr_rolle matches {p} run tellraw @s {msg({"text": "Wunschrolle: ", "color": "gray"}, {"text": name, "color": color, "bold": True}, {"text": " (zählt ab 3 Spielern pro Team)", "color": "dark_gray"})}'
      for p, (name, _, color, _) in PREFS.items()],
    'scoreboard players operation @s sr_pref = @s sr_rolle',
    'tag @s add sr_refresh',
    'playsound minecraft:block.note_block.pling master @s ~ ~ ~ 1 1.4',
    'scoreboard players set @s sr_rolle 0',
])
fn('role/give', ['$scoreboard players set @s sr_role $(r)', 'tag @s add sr_hasrole', 'scoreboard players set #got sr 1'])
for n in TEAMS:
    S = f'@a[tag=sr_cur,tag=!sr_hasrole'
    def assign(spec, extra=False):
        # pass 1: everyone whose wish matches gets the role; pass 2: free roles go to anyone left
        out = []
        for r, lo, hi in spec:
            out += [f'scoreboard players set #g{r} sr 0',
                    f'execute as {S},scores={{sr_pref={lo}..{hi}}},limit=1,sort=random] run function {NS}:role/give {{r:{r}}}',
                    f'execute if score #got sr matches 1 run scoreboard players set #g{r} sr 1',
                    'scoreboard players set #got sr 0']
        for r, lo, hi in spec:
            out.append(f'execute if score #g{r} sr matches 0 as {S},limit=1,sort=random] run function {NS}:role/give {{r:{r}}}')
        if extra:
            out.append(f'execute as {S}] run function {NS}:role/extra')
        return ['scoreboard players set #got sr 0'] + out
    lines = ['tag @a remove sr_cur', f'tag @a[scores={{sr_team={n}}}] add sr_cur',
             'scoreboard players set #size sr 0', f'execute as @a[scores={{sr_team={n}}}] run scoreboard players add #size sr 1',
             'execute if score #size sr matches 0 run return 0',
             f'execute if score #size sr matches 1 as @a[scores={{sr_team={n}}}] run function {NS}:role/give {{r:0}}']
    lines += [f'execute if score #size sr matches 2 run function {NS}:role/duo_t{n}',
              f'execute if score #size sr matches 3 run function {NS}:role/trio_t{n}',
              f'execute if score #size sr matches 4.. run function {NS}:role/squad_t{n}']
    fn(f'role/assign_t{n}', lines)
    fn(f'role/duo_t{n}', assign([(5, 1, 2), (6, 3, 4)]))
    fn(f'role/trio_t{n}', assign([(1, 1, 1), (2, 2, 2), (3, 3, 4)]))
    fn(f'role/squad_t{n}', assign([(1, 1, 1), (2, 2, 2), (3, 3, 3), (4, 4, 4)], extra=True))
fn('role/extra', ['scoreboard players set @s sr_role 3',
                  'execute if score @s sr_pref matches 1..4 run scoreboard players operation @s sr_role = @s sr_pref',
                  'tag @s add sr_hasrole'])
brief = []
for r, (name, hint) in ROLES.items():
    brief += [f'execute if score @s sr_role matches {r} run title @s subtitle {tc([{"text": "Deine Rolle: ", "color": "gray"}, {"text": name, "color": "yellow", "bold": True}])}',
              f'execute if score @s sr_role matches {r} run tellraw @s {msg({"text": "Deine Rolle: ", "color": "gray"}, {"text": name, "color": "yellow", "bold": True}, {"text": " – " + hint, "color": "white"})}']
fn('role/brief', [
    'title @s times 5 60 15',
    *[f'execute if entity @s[scores={{sr_team={n}}}] run title @s title {tc({"text": "Team " + cname, "color": color, "bold": True})}' for n, (color, cname) in TEAMS.items()],
    *brief,
    f'function {NS}:role/plan_chat',
    f'tellraw @s {msg({"text": "Rechtsklick auf den Speedrun-Zettel: alle Items mit Ziel, Team-Stand und Aufgaben. Die Zeit steht unten über der Hotbar.", "color": "gold"})}',
    f'tellraw @s {msg({"text": "Rechts siehst du DEINE Schritte (▶ = jetzt dran) und unten den Team-Stand. Mitspieler leuchten, die Leiste über der Hotbar zeigt, wo sie sind. Wichtige Orte kommen automatisch mit Koordinaten. Plan & Position teilen: Esc → Speedrun-Menü", "color": "gray"})}',
    'execute if score #teams sr matches 2.. run tellraw @s ' + msg({'text': 'RENNEN! ', 'color': 'red', 'bold': True}, {'text': 'Jedes Team startet woanders. Wer zuerst den Drachen tötet, gewinnt.', 'color': 'white'}),
])
hint_lines = []
for r, (name, hint) in ROLES.items():
    hint_lines.append(f'execute if score @s sr_role matches {r} run return run title @s actionbar {tc(TIME_BAR + [{"text": "[" + name + "] ", "color": "yellow", "bold": True}, {"text": hint, "color": "gray", "bold": False}])}')
hint_lines.append(f'title @s actionbar {tc(TIME_BAR[:-1])}')
fn('role/actionbar', hint_lines)
plan_lines = []
for r, steps in STEPS.items():
    parts = [{'text': 'Dein Plan als ', 'color': 'gray'}, {'text': ROLES[r][0], 'color': 'yellow', 'bold': True}]
    for i, (key, text) in enumerate(steps):
        parts.append({'text': f'\n  {i + 1}. ', 'color': 'gold', 'bold': False})
        parts.append({'text': text + (f' ({NEED[key][0]})' if key in NEED else ''), 'color': 'white', 'bold': False})
    plan_lines.append(f'execute if score @s sr_role matches {r} run tellraw @s {msg(*parts)}')
    js(f'data/{NS}/dialog/plan_r{r}.json', {
        'type': 'minecraft:notice',
        'title': {'text': 'Dein Plan: ' + ROLES[r][0], 'color': 'gold', 'bold': True},
        'body': {'type': 'minecraft:plain_message', 'width': 300, 'contents':
                 [{'text': ROLES[r][1] + '\n\n', 'color': 'gray'}] +
                 [{'text': f'{i + 1}.  {text}' + (f' ({NEED[key][0]})' if key in NEED else '') + '\n', 'color': 'white'} for i, (key, text) in enumerate(steps)]},
        'action': {'label': {'text': 'Los geht’s'}, 'width': 150},
    })
fn('role/plan_chat', plan_lines)
fn('role/plan', [
    f'execute unless entity @s[tag=sr_run] run return run tellraw @s {msg({"text": "Dein Plan erscheint, sobald ein Run läuft.", "color": "gray"})}',
    *[f'execute if score @s sr_role matches {r} run return run dialog show @s {NS}:plan_r{r}' for r in STEPS],
])
for n, (color, cname) in TEAMS.items():
    disp = []
    for r, steps in STEPS.items():
        disp.append(f'execute if score @s sr_role matches {r} run return run function {NS}:role/step_t{n}_r{r}')
        lines = []
        for i, (key, text) in enumerate(steps):
            comp = [{'text': '[' + ROLES[r][0] + '] ', 'color': 'yellow', 'bold': True},
                    {'text': f'Schritt {i + 1}/{len(steps)} ▸ ', 'color': 'gray', 'bold': False},
                    {'text': text, 'color': 'white', 'bold': False}]
            if key in NEED:
                comp += [{'text': '   ', 'bold': False}, {'score': {'name': f'#t{n}_v_{key}', 'objective': 'sr'}, 'color': 'yellow', 'bold': True},
                         {'text': f'/{NEED[key][0]}', 'color': 'gray', 'bold': False}]
            lines.append(f'execute if score #t{n}_{key} sr_done matches 0 run return run title @s actionbar {tc(comp)}')
        lines.append(f'title @s actionbar {tc([{"text": "[" + ROLES[r][0] + "] ", "color": "yellow", "bold": True}, {"text": "Alles erledigt – hilf deinem Team!", "color": "green", "bold": False}])}')
        fn(f'role/step_t{n}_r{r}', lines)
    fn(f'role/step_t{n}', disp)

# coordinates to the team
for n, (color, cname) in TEAMS.items():
    base = [{'text': '➤ ', 'color': color}, {'text': '$(label)', 'color': color, 'bold': True}, {'text': ': ', 'color': 'gray'},
            {'score': {'name': '#px', 'objective': 'sr'}, 'color': 'white'}, {'text': ' ', 'color': 'white'},
            {'score': {'name': '#py', 'objective': 'sr'}, 'color': 'white'}, {'text': ' ', 'color': 'white'},
            {'score': {'name': '#pz', 'objective': 'sr'}, 'color': 'white'}]
    who = [{'text': '  (', 'color': 'dark_gray'}, {'selector': '@s', 'color': 'gray'}, {'text': ')', 'color': 'dark_gray'}]
    fn(f'fx/share_t{n}', [
        'execute store result score #px sr run data get entity @s Pos[0]',
        'execute store result score #py sr run data get entity @s Pos[1]',
        'execute store result score #pz sr run data get entity @s Pos[2]',
        f'$execute if dimension minecraft:overworld run tellraw @a[tag=sr_run,scores={{sr_team={n}}}] {tc(base + [{"text": "  Oberwelt", "color": "green"}] + who)}',
        f'$execute if dimension minecraft:the_nether run tellraw @a[tag=sr_run,scores={{sr_team={n}}}] {tc(base + [{"text": "  Nether", "color": "red"}] + who)}',
        f'$execute if dimension minecraft:the_end run tellraw @a[tag=sr_run,scores={{sr_team={n}}}] {tc(base + [{"text": "  End", "color": "light_purple"}] + who)}',
        f'execute as @a[tag=sr_run,scores={{sr_team={n}}}] at @s run playsound minecraft:block.note_block.chime master @s ~ ~ ~ 0.8 1.5',
    ])
fn('fx/share_me', [
    f'execute unless entity @s[tag=sr_run] run return run tellraw @s {msg({"text": "Das geht nur im Run.", "color": "gray"})}',
    'data modify storage sr:run share.label set value "Position"',
    *[f'execute if entity @s[scores={{sr_team={n}}}] at @s run function {NS}:fx/share_t{n} with storage sr:run share' for n in TEAMS],
])

# ------------------------------------------------------------------ start (request -> countdown -> launch)
fn('start/by_player', ['tag @s add sr_starter', f'function {NS}:start/request', 'tag @a remove sr_starter'])
fn('start/request', [
    'execute if score #cd sr matches 1.. run return 0',
    f'execute if score #active sr matches 1 run return run tellraw @a[tag=sr_starter] {msg({"text": "Ein Run läuft gerade. ", "color": "red"}, clk("[Run abbrechen]", "/trigger sr_aktion set 6", "red"))}',
    f'execute unless entity @a[tag=!sr_watch] run return run tellraw @a[tag=sr_starter] {msg({"text": "Niemand spielt mit – alle schauen zu.", "color": "red"})}',
    'scoreboard players set #cd sr 5', 'scoreboard players set #cdt sr 0',
    f'tellraw @a {msg({"selector": "@a[tag=sr_starter]", "color": "white"}, {"text": " startet einen Run: ", "color": "gray"}, {"nbt": "mode", "storage": "sr:run", "interpret": True, "color": "yellow", "bold": True})}',
    f'function {NS}:start/cd_show',
])
fn('start/cd_tick', ['scoreboard players add #cdt sr 1', 'execute if score #cdt sr matches 20.. run function ' + f'{NS}:start/cd_step'])
fn('start/cd_step', ['scoreboard players set #cdt sr 0', 'scoreboard players remove #cd sr 1',
                     f'execute if score #cd sr matches 0 run return run function {NS}:start/launch',
                     f'function {NS}:start/cd_show'])
fn('start/cd_show', [
    'title @a times 0 25 5',
    f'title @a title {tc({"score": {"name": "#cd", "objective": "sr"}, "color": "gold", "bold": True})}',
    f'title @a subtitle {tc([{"text": "Modus ", "color": "gray"}, {"nbt": "mode", "storage": "sr:run", "interpret": True, "color": "yellow"}])}',
    'execute as @a at @s run playsound minecraft:block.note_block.hat master @s ~ ~ ~ 1 1',
])
launch = [
    'scoreboard players add #run sr 1',
    'scoreboard players operation #runmode sr = #mode sr',
    # reset everybody's team / role state
    'team leave @a', 'scoreboard players set @a sr_slot 0', 'tag @a remove sr_run', 'tag @a remove sr_spec', 'tag @a remove sr_hasrole', 'tag @a remove sr_pending',
    'scoreboard players set @a sr_role -1', 'scoreboard players set @a sr_team 0',
    'tag @a[tag=!sr_watch] add sr_pending',
    # team size
    'scoreboard players set #k sr 99',
    *[f'execute if score #mode sr matches {m} run scoreboard players set #k sr {size}' for m, (_, size) in MODES.items()],
    'scoreboard players set #n sr 1', 'scoreboard players set #c sr 0',
    f'function {NS}:start/assign_next',
    'scoreboard players set #teams sr 0',
    *[f'execute if entity @a[scores={{sr_team={n}}}] run scoreboard players add #teams sr 1' for n in TEAMS],
    'tag @a[scores={sr_team=1..}] add sr_run', 'tag @a[tag=sr_run] remove sr_lobby',
    f'execute as @a[tag=sr_run] run function {NS}:player/reset_state',
    'gamemode survival @a[tag=sr_run]',
    'effect give @a[tag=sr_run] minecraft:glowing infinite 0 true',
    'time set 0', 'weather clear', 'difficulty normal',
    'scoreboard players set #crystals sr 0', 'scoreboard players set #dseen sr 0', 'scoreboard players set #finished sr 0',
    f'{OW} tp @a[tag=sr_run] 0 200 0',
]
for n in TEAMS:
    launch += [f'execute if entity @a[scores={{sr_team={n}}}] run function {NS}:team/setup_t{n}',
               f'execute unless entity @a[scores={{sr_team={n}}}] run bossbar set {NS}:t{n} visible false']
launch += [
    'execute as @a[tag=sr_run] at @s run spawnpoint @s ~ ~ ~',
    'execute as @a[tag=sr_run] store result score @s sr_sx run data get entity @s Pos[0]',
    'execute as @a[tag=sr_run] store result score @s sr_sy run data get entity @s Pos[1]',
    'execute as @a[tag=sr_run] store result score @s sr_sz run data get entity @s Pos[2]',
    'scoreboard players set #k sr 0',
    f'execute as @a[tag=sr_run] run function {NS}:start/slot',
    'scoreboard players set @a[tag=sr_run] sr_pu_blaze 0', 'scoreboard players set @a[tag=sr_run] sr_pu_pearl 0',
    'scoreboard players set @a[tag=sr_run] sr_cr_eye 0',
    *[f'scoreboard players set @a[tag=sr_run] sr_cr_f{i} 0' for i in range(len(FOOD))],
    *[f'scoreboard players set @a[tag=sr_run] sr_d_{k} 0' for k in STEP_KEYS],
    *[f'scoreboard players set @a[tag=sr_run] sr_v_{k} 0' for k in NEED],
    f'execute as @a[tag=sr_run,scores={{sr_slot=1..16}}] run function {NS}:p/init',
    'scoreboard players set #ticks sr 0', 'scoreboard players set #st sr 0', 'scoreboard players set #empty sr 0', 'scoreboard players set #active sr 1',
    'data modify storage sr:run tstr set value "0:00"',
    f'execute as @a[tag=sr_run] run function {NS}:role/brief',
    'execute as @a[tag=sr_run] at @s run playsound minecraft:entity.ender_dragon.growl master @s ~ ~ ~ 0.6 1.2',
    f'execute as @a[tag=sr_watch] run function {NS}:player/spectate',
    f'tellraw @a {msg({"text": "Run #", "color": "white"}, {"score": {"name": "#run", "objective": "sr"}, "color": "white"}, {"text": " gestartet · ", "color": "gray"}, {"nbt": "mode", "storage": "sr:run", "interpret": True, "color": "yellow"}, {"text": " · ", "color": "gray"}, {"score": {"name": "#teams", "objective": "sr"}, "color": "white"}, {"text": " Team(s)", "color": "gray"})}',
]
fn('start/launch', launch)
fn('start/assign_next', [
    'execute unless entity @a[tag=sr_pending] run return 0',
    *[f'execute if score #n sr matches {n} as @r[tag=sr_pending] run function {NS}:start/join_t{n}' for n in TEAMS],
    'scoreboard players add #c sr 1',
    'execute if score #c sr >= #k sr run scoreboard players add #n sr 1',
    'execute if score #c sr >= #k sr run scoreboard players set #c sr 0',
    'execute if score #n sr matches 9.. run scoreboard players set #n sr 1',
    f'function {NS}:start/assign_next',
])
for n in TEAMS:
    fn(f'start/join_t{n}', ['tag @s remove sr_pending', f'scoreboard players set @s sr_team {n}'])

# per-team setup: roles, start position, sidebar, bossbar, task flags
for n, (color, cname) in TEAMS.items():
    sel = f'@a[tag=sr_run,scores={{sr_team={n}}}]'
    setup = [
        f'function {NS}:role/assign_t{n}',
        'scoreboard players operation #slot sr = #nextslot sr',
        'scoreboard players add #nextslot sr 1',
        'scoreboard players operation #slot sr %= #npos sr',
        f'function {NS}:pos/pick',
        f'data modify storage sr:run place set value {{n:{n}}}',
        'execute store result storage sr:run place.x int 1 run scoreboard players get #cx sr',
        'execute store result storage sr:run place.z int 1 run scoreboard players get #cz sr',
        'scoreboard players set #try sr 0',
        f'function {NS}:pos/place with storage sr:run place',
        f'scoreboard players set #t{n}_cnt sr 0',
        f'scoreboard players reset * sr_s{n}',
    ]
    for i, (key, label) in enumerate(TASKS):
        setup += [f'scoreboard players set #t{n}_{key} sr_done 0',
                  f'scoreboard players set {key} sr_s{n} {NT - i}',
                  f'scoreboard players display name {key} sr_s{n} {tc({"text": "☐ " + label, "color": "gray"})}']
        if key in NEED:
            setup.append(f'scoreboard players display numberformat {key} sr_s{n} fixed {tc({"text": "0/" + str(NEED[key][0]), "color": "gray"})}')
            setup.append(f'scoreboard players set #t{n}_v_{key} sr 0')
    setup += [f'scoreboard objectives modify sr_s{n} displayname {tc({"text": "Team " + cname, "color": color, "bold": True})}',
              ]
    setup += [f'bossbar set {NS}:t{n} value 0', f'bossbar set {NS}:t{n} visible true', f'bossbar set {NS}:t{n} players {sel}']
    fn(f'team/setup_t{n}', setup)

fn('pos/pick', [f'execute if score #slot sr matches {i} run return run function {NS}:pos/set {{x:{x},z:{z}}}' for i, (x, z) in enumerate(POS)])
fn('pos/set', ['$scoreboard players set #cx sr $(x)', '$scoreboard players set #cz sr $(z)'])
fn('pos/place', [
    '$execute in minecraft:overworld store success score #ok sr run spreadplayers $(x) $(z) 2 24 false @a[tag=sr_run,scores={sr_team=$(n)}]',
    '$execute if score #ok sr matches 0 in minecraft:overworld store success score #ok sr run spreadplayers $(x) $(z) 2 96 false @a[tag=sr_run,scores={sr_team=$(n)}]',
    '$execute if score #ok sr matches 0 in minecraft:overworld store success score #ok sr run spreadplayers $(x) $(z) 2 320 false @a[tag=sr_run,scores={sr_team=$(n)}]',
    f'execute if score #ok sr matches 0 run function {NS}:pos/retry',
])
fn('pos/retry', [
    'scoreboard players add #try sr 1',
    f'execute if score #try sr matches 6.. run return run tellraw @a {msg({"text": "Konnte keinen Startplatz finden.", "color": "red"})}',
    'scoreboard players add #slot sr 1', 'scoreboard players add #nextslot sr 1',
    'scoreboard players operation #slot sr %= #npos sr',
    f'function {NS}:pos/pick',
    'execute store result storage sr:run place.x int 1 run scoreboard players get #cx sr',
    'execute store result storage sr:run place.z int 1 run scoreboard players get #cz sr',
    f'function {NS}:pos/place with storage sr:run place',
])

# ------------------------------------------------------------------ run loop
fn('run/tick', [
    'scoreboard players add #st sr 1',
    'execute if entity @a[tag=sr_run] run scoreboard players add #ticks sr 1',
    f'execute if score #st sr matches 20.. run function {NS}:run/second',
])
second = [
    'scoreboard players set #st sr 0',
    'execute if entity @a[tag=sr_run] run scoreboard players set #empty sr 0',
    'execute unless entity @a[tag=sr_run] run scoreboard players add #empty sr 1',
    f'execute if score #empty sr matches 600.. run return run function {NS}:run/empty',
    'execute unless entity @a[tag=sr_run] run return 0',
    'scoreboard players operation #s sr = #ticks sr', 'scoreboard players operation #s sr /= #20 sr',
    'scoreboard players operation #min sr = #s sr', 'scoreboard players operation #min sr /= #60 sr',
    'scoreboard players operation #sec sr = #s sr', 'scoreboard players operation #sec sr %= #60 sr',
    f'function {NS}:time/fmt',
]
for n in TEAMS:
    second.append(f'execute if entity @a[tag=sr_run,scores={{sr_team={n}}}] run function {NS}:team/second_t{n}')
second += [
    f'execute as @a[tag=sr_run,scores={{sr_slot=1..16}}] at @s run function {NS}:p/second',
    f'execute as @a[tag=sr_run] unless score @s sr_slot matches 1..16 run function {NS}:role/actionbar',
    f'title @a[tag=sr_spec] actionbar {tc(TIME_BAR + [{"text": "Zuschauer", "color": "aqua", "bold": False}])}',
    f'title @a[tag=sr_lobby] actionbar {tc(TIME_BAR + [{"text": "Run läuft", "color": "yellow", "bold": False}, {"text": " · Zuschauen: Fernrohr (Slot 5)", "color": "gray", "bold": False}])}',
    f'execute as @a[tag=sr_run,gamemode=survival] at @s if dimension minecraft:overworld if entity @s[x=-40,dx=80,y=185,dy=120,z=-40,dz=80] run function {NS}:p/rescue',
    'scoreboard players operation #five sr = #s sr', 'scoreboard players operation #five sr %= #5 sr',
    'execute if score #five sr matches 0 run effect give @a[tag=sr_run] minecraft:glowing infinite 0 true',
    f'function {NS}:run/end_watch',
]
fn('run/second', second)
fn('run/empty', ['scoreboard players set #active sr 0',
                 *[f'bossbar set {NS}:t{n} visible false' for n in TEAMS],
                 f'tellraw @a {msg({"text": "Run beendet – 10 Minuten lang war niemand mehr im Run.", "color": "gray"})}'])

SHARE = {
    'nether': ('Nether-Portal', 'in minecraft:the_nether as @a[tag=sr_run,scores={{sr_team={n}}},distance=0..,limit=1]'),
    'fortress': ('Festung', 'as @a[tag=sr_run,scores={{sr_team={n}}},advancements={{minecraft:nether/find_fortress=true}},limit=1]'),
    'bastion': ('Bastion', 'as @a[tag=sr_run,scores={{sr_team={n}}},advancements={{minecraft:nether/find_bastion=true}},limit=1]'),
    'stronghold': ('Stronghold', 'as @a[tag=sr_run,scores={{sr_team={n}}},advancements={{minecraft:story/follow_ender_eye=true}},limit=1]'),
}
for n, (color, cname) in TEAMS.items():
    sel = f'@a[tag=sr_run,scores={{sr_team={n}}}]'
    def bar(zero):
        return tc([{'text': 'Team ' + cname, 'color': color, 'bold': True},
                   {'text': '  ·  ', 'color': 'gray'}, {'nbt': 'mode', 'storage': 'sr:run', 'interpret': True, 'color': 'white'},
                   {'text': '   ⏱ ', 'color': 'white'}, {'score': {'name': '#min', 'objective': 'sr'}, 'color': 'white'},
                   {'text': ':0' if zero else ':', 'color': 'white'}, {'score': {'name': '#sec', 'objective': 'sr'}, 'color': 'white'},
                   {'text': '   ✔ ', 'color': 'green'}, {'score': {'name': f'#t{n}_cnt', 'objective': 'sr'}, 'color': 'green'},
                   {'text': f'/{NT}', 'color': 'green'}])
    def title(zero):
        return tc([{'text': 'Team ' + cname, 'color': color, 'bold': True}, {'text': '  ⏱ ', 'color': 'white', 'bold': False},
                   {'score': {'name': '#min', 'objective': 'sr'}, 'color': 'white', 'bold': False},
                   {'text': ':0' if zero else ':', 'color': 'white', 'bold': False},
                   {'score': {'name': '#sec', 'objective': 'sr'}, 'color': 'white', 'bold': False}])
    lines = [
        f'execute if score #sec sr matches 10.. run bossbar set {NS}:t{n} name {bar(False)}',
        f'execute if score #sec sr matches ..9 run bossbar set {NS}:t{n} name {bar(True)}',
        f'bossbar set {NS}:t{n} players {sel}',
        f'execute if score #sec sr matches 10.. run scoreboard objectives modify sr_s{n} displayname {title(False)}',
        f'execute if score #sec sr matches ..9 run scoreboard objectives modify sr_s{n} displayname {title(True)}',
    ]
    for key, label in TASKS:
        lines.append(f'execute if score #t{n}_{key} sr_done matches 0 if function {NS}:cond/t{n}_{key} run function {NS}:done/t{n}_{key}')
    fn(f'team/second_t{n}', lines)

    # conditions
    def count(item):
        return ['scoreboard players set #c sr 0',
                f'execute as {sel} store result score @s sr_tmp run clear @s {item} 0',
                f'execute as {sel} run scoreboard players operation #c sr += @s sr_tmp']
    def sumc(terms, need, key=None):
        out = ['scoreboard players set #sum sr 0']
        for item, mult in terms:
            out += count(item) + ['scoreboard players operation #sum sr += #c sr'] * mult
        if key:
            amount, div = NEED[key]
            v = f'#t{n}_v_{key}'
            out += [f'scoreboard players operation {v} sr = #sum sr']
            if div != 1:
                out += [f'scoreboard players operation {v} sr /= #{div} sr']
            out += [f'scoreboard players display numberformat {key} sr_s{n} fixed '
                    + tc([{'score': {'name': v, 'objective': 'sr'}, 'color': 'yellow'}, {'text': f'/{amount}', 'color': 'gray'}])]
        return out + [f'execute if score #sum sr matches {need}.. run return 1', 'return 0']
    def adv(a):
        return [f'execute if entity @a[tag=sr_run,scores={{sr_team={n}}},advancements={{{a}=true}}] run return 1', 'return 0']
    def dim(d, a):
        return [f'execute as {sel} at @s if dimension {d} run return 1'] + adv(a)
    C = {
        'gear': count('minecraft:shield') + ['execute if score #c sr matches 0 run return 0']
                + sumc([('minecraft:iron_sword', 1), ('minecraft:diamond_sword', 1), ('minecraft:netherite_sword', 1)], 1),
        'tools': count('minecraft:flint_and_steel') + ['execute if score #c sr matches 0 run return 0']
                 + sumc([('minecraft:bucket', 1), ('minecraft:water_bucket', 1), ('minecraft:lava_bucket', 1)], 1),
        'nether': dim('minecraft:the_nether', 'minecraft:story/enter_the_nether'),
        'fortress': adv('minecraft:nether/find_fortress'),
        'bastion': adv('minecraft:nether/find_bastion'),
        'blaze': sumc([('minecraft:blaze_rod', 2), ('minecraft:blaze_powder', 1), ('minecraft:ender_eye', 1)], 14, 'blaze'),
        'pearls': sumc([('minecraft:ender_pearl', 1), ('minecraft:ender_eye', 1)], 12, 'pearls'),
        'beds': sumc([('#minecraft:beds', 1)], 7, 'beds'),
        'food': sumc([(f'minecraft:{f}', 1) for f in FOOD], 20, 'food'),
        'eyes': sumc([('minecraft:ender_eye', 1)], 12, 'eyes'),
        'stronghold': adv('minecraft:story/follow_ender_eye'),
        'end': dim('minecraft:the_end', 'minecraft:story/enter_the_end'),
        'dragon': adv('minecraft:end/kill_dragon'),
    }
    for key, label in TASKS:
        fn(f'cond/t{n}_{key}', C[key])
        d = [f'scoreboard players set #t{n}_{key} sr_done 1', f'scoreboard players add #t{n}_cnt sr 1',
             f'execute store result bossbar {NS}:t{n} value run scoreboard players get #t{n}_cnt sr',
             f'scoreboard players display name {key} sr_s{n} {tc({"text": "✔ " + label, "color": "green"})}',
             f'scoreboard players display numberformat {key} sr_s{n} fixed {tc({"text": "✔", "color": "green", "bold": True})}',
             f'tellraw {sel} {tc([{"text": "✔ Team: ", "color": "dark_green", "bold": True}, {"text": label, "color": "gray"}])}',
             f'execute as {sel} at @s run playsound minecraft:entity.player.levelup master @s ~ ~ ~ 0.5 1.6',
             f'tag @a remove sr_cur2', f'tag {sel} add sr_cur2',
             f'execute if score #teams sr matches 2.. run tellraw @a[tag=!sr_cur2] {tc([{"text": "[" + cname + "] ", "color": color, "bold": True}, {"text": label, "color": "gray"}])}']
        if key in SHARE:
            lbl, sel_share = SHARE[key]
            d += [f'data modify storage sr:run share.label set value "{lbl}"',
                  f'execute {sel_share.format(n=n)} at @s run function {NS}:fx/share_t{n} with storage sr:run share']
        if key == 'dragon':
            d.append(f'execute if score #finished sr matches 0 run function {NS}:run/finish {{n:{n}}}')
        fn(f'done/t{n}_{key}', d)

# End: dragon watch (also catches bed kills without kill credit) + crystals for respawn
fn('run/end_watch', [
    'execute as @a[tag=sr_run] at @s if dimension minecraft:the_end run scoreboard players add @s sr_endt 1',
    'execute unless entity @a[tag=sr_run,scores={sr_endt=6..}] run return 0',
    'execute in minecraft:the_end positioned 0 64 0 if entity @e[type=minecraft:ender_dragon,distance=..400] run return run scoreboard players set #dseen sr 1',
    f'execute if score #dseen sr matches 1 if score #finished sr matches 0 run return run function {NS}:run/dragon_gone',
    'execute if score #crystals sr matches 1 run return 0',
    'scoreboard players set #crystals sr 1',
    'give @r[tag=sr_run,scores={sr_endt=6..}] minecraft:end_crystal 4',
    f'tellraw @a[tag=sr_run] {msg({"text": "Der Drache ist aus einem alten Run schon tot. Setzt die 4 Endkristalle auf die 4 Seiten des Ausgangsportals in der Mitte – dann kommt er zurück.", "color": "light_purple"})}',
])
gone = ['scoreboard players set #wn sr 0']
for n in TEAMS:
    gone.append(f'execute if score #wn sr matches 0 if entity @a[tag=sr_run,scores={{sr_team={n}}},advancements={{minecraft:end/kill_dragon=true}}] run scoreboard players set #wn sr {n}')
gone += ['execute if score #wn sr matches 0 in minecraft:the_end positioned 0 64 0 as @p[tag=sr_run,distance=..200] run scoreboard players operation #wn sr = @s sr_team',
         'execute if score #wn sr matches 0 run scoreboard players set #wn sr 1',
         'execute store result storage sr:run win.n int 1 run scoreboard players get #wn sr',
         f'function {NS}:run/finish with storage sr:run win']
fn('run/dragon_gone', gone)

fin = [
    'scoreboard players set #finished sr 1', 'scoreboard players set #active sr 0',
    '$scoreboard players set #winner sr $(n)',
    'scoreboard players operation #s sr = #ticks sr', 'scoreboard players operation #s sr /= #20 sr',
    'scoreboard players operation #min sr = #s sr', 'scoreboard players operation #min sr /= #60 sr',
    'scoreboard players operation #sec sr = #s sr', 'scoreboard players operation #sec sr %= #60 sr',
]
for m in MODES:
    fin += [f'execute if score #runmode sr matches {m} unless score #best{m} sr matches 1.. run scoreboard players operation #best{m} sr = #ticks sr',
            f'execute if score #runmode sr matches {m} if score #ticks sr < #best{m} sr run scoreboard players operation #best{m} sr = #ticks sr']
fin += ['scoreboard players operation #last sr = #ticks sr', f'function {NS}:holo/leaderboard', f'function {NS}:sidebar/lobby',
        'title @a times 10 80 20']
tstr = lambda zero: [{'text': 'Zeit ', 'color': 'gray'}, {'score': {'name': '#min', 'objective': 'sr'}, 'color': 'white'},
                     {'text': ':0' if zero else ':', 'color': 'white'}, {'score': {'name': '#sec', 'objective': 'sr'}, 'color': 'white'}]
for n, (color, cname) in TEAMS.items():
    sel = f'@a[tag=sr_run,scores={{sr_team={n}}}]'
    fin += [
        f'execute if score #winner sr matches {n} if score #teams sr matches 2.. run title @a title {tc({"text": "Team " + cname + " gewinnt!", "color": color, "bold": True})}',
        f'execute if score #winner sr matches {n} if score #teams sr matches 1 run title @a title {tc({"text": "Drache besiegt!", "color": "gold", "bold": True})}',
        f'execute if score #winner sr matches {n} run scoreboard players add {sel} sr_wins 1',
        f'execute if score #winner sr matches {n} as {sel} at @s run function {NS}:fx/fireworks',
        f'execute if score #winner sr matches {n} run tellraw @a {msg({"text": "Run #", "color": "white"}, {"score": {"name": "#run", "objective": "sr"}, "color": "white"}, {"text": " · Sieger: ", "color": "gray"}, {"text": "Team " + cname, "color": color, "bold": True}, {"text": " ", "color": "gray"}, {"selector": sel, "color": "white"})}',
    ]
fin += [
    f'execute if score #sec sr matches 10.. run title @a subtitle {tc(tstr(False))}',
    f'execute if score #sec sr matches ..9 run title @a subtitle {tc(tstr(True))}',
    f'execute if score #sec sr matches 10.. run tellraw @a {msg(*tstr(False))}',
    f'execute if score #sec sr matches ..9 run tellraw @a {msg(*tstr(True))}',
    'execute as @a at @s run playsound minecraft:ui.toast.challenge_complete master @s ~ ~ ~ 1 1',
    *[f'bossbar set {NS}:t{n} visible false' for n in TEAMS],
    'scoreboard players operation #finrun sr = #run sr',
    f'schedule function {NS}:run/auto_lobby 400t',
    f'tellraw @a {msg({"text": "In 20 Sekunden geht es zurück zur Lobby. ", "color": "gray"}, clk("[Jetzt zur Lobby]", "/trigger sr_aktion set 2"))}',
]
fn('run/finish', fin)
fn('fx/fireworks', [
    'summon minecraft:firework_rocket ~ ~1 ~ {LifeTime:20,FireworksItem:{id:"minecraft:firework_rocket",count:1,components:{"minecraft:fireworks":{flight_duration:1,explosions:[{shape:"large_ball",colors:[I;16766720,16733525],has_twinkle:true}]}}}}',
    'summon minecraft:firework_rocket ~2 ~1 ~ {LifeTime:30,FireworksItem:{id:"minecraft:firework_rocket",count:1,components:{"minecraft:fireworks":{flight_duration:2,explosions:[{shape:"star",colors:[I;5635925,16777215],has_trail:true}]}}}}',
    'summon minecraft:firework_rocket ~-2 ~1 ~ {LifeTime:25,FireworksItem:{id:"minecraft:firework_rocket",count:1,components:{"minecraft:fireworks":{flight_duration:1,explosions:[{shape:"burst",colors:[I;5592575,16777045],has_twinkle:true}]}}}}',
])
fn('run/auto_lobby', [
    'execute if score #active sr matches 1 run return 0',
    'execute unless score #run sr = #finrun sr run return 0',
    f'execute as @a[tag=sr_run] run function {NS}:player/to_lobby',
    f'execute as @a[tag=sr_spec] run function {NS}:player/to_lobby',
])
fn('run/abort', [
    f'execute if score #cd sr matches 1.. run return run function {NS}:run/abort_cd',
    f'execute if score #active sr matches 0 run return run tellraw @s {msg({"text": "Gerade läuft kein Run.", "color": "gray"})}',
    'scoreboard players set #active sr 0',
    *[f'bossbar set {NS}:t{n} visible false' for n in TEAMS],
    f'tellraw @a {msg({"selector": "@s", "color": "white"}, {"text": " hat den Run abgebrochen.", "color": "red"})}',
    f'execute as @a[tag=sr_run] run function {NS}:player/to_lobby',
    f'execute as @a[tag=sr_spec] run function {NS}:player/to_lobby',
])
fn('run/abort_cd', ['scoreboard players set #cd sr 0', 'title @a clear',
                    f'tellraw @a {msg({"selector": "@s", "color": "white"}, {"text": " hat den Countdown abgebrochen.", "color": "red"})}'])


# ------------------------------------------------------------------ hotbar items (right click)
def citem(key, model, name, lore, glint=False):
    comps = [f'minecraft:item_model="minecraft:{model}"',
             f'minecraft:custom_name={tc(dict(name, italic=False))}',
             'minecraft:lore=[' + ','.join(tc({'text': l, 'color': 'gray', 'italic': False}) for l in lore) + ']',
             f'minecraft:custom_data={{sr_item:1b,sr:"{key}"}}',
             'minecraft:unbreakable={}',
             'minecraft:tooltip_display={hidden_components:["minecraft:unbreakable"]}',
             'minecraft:use_cooldown={seconds:0.6f}']
    if glint:
        comps.append('minecraft:enchantment_glint_override=true')
    return 'minecraft:carrot_on_a_stick[' + ','.join(comps) + ']'

ROLE_ITEMS = {0: ('compass', 'egal', 'white', 'Rolle wird automatisch verteilt'),
              1: ('blaze_rod', 'Kämpfer', 'gold', ROLES[1][1]),
              2: ('ender_pearl', 'Portal & Perlen', 'light_purple', ROLES[2][1]),
              3: ('red_bed', 'Versorger', 'green', ROLES[3][1]),
              4: ('ender_eye', 'Späher', 'aqua', ROLES[4][1])}
hb = ['tag @s remove sr_refresh',
      'clear @s *[minecraft:custom_data~{sr_item:1b}]',
      'item replace entity @s hotbar.0 with ' + citem('start', 'nether_star', {'text': '▶ RUN STARTEN', 'color': 'green', 'bold': True},
                                                    ['Rechtsklick: Countdown für alle', 'die nicht zuschauen'], glint=True)]
for m, (name, size) in MODES.items():
    hb.append(f'execute if score #mode sr matches {m} run item replace entity @s hotbar.1 with ' +
              citem('mode', 'clock', {'text': f'Modus: {name}', 'color': 'yellow', 'bold': True},
                    [MODE_INFO[m], 'Rechtsklick: nächster Modus', 'Solo → Duo → Trio → Squad → Koop']))
hb.append('execute unless score @s sr_pref matches 1..4 run scoreboard players set @s sr_pref 0')
for p, (model, name, color, desc) in ROLE_ITEMS.items():
    hb.append(f'execute if score @s sr_pref matches {p} run item replace entity @s hotbar.2 with ' +
              citem('role', model, {'text': f'Wunschrolle: {name}', 'color': color, 'bold': True},
                    [desc, 'Rechtsklick: nächste Rolle', 'Gilt ab 3 Spielern pro Team']))
hb += [
    'execute if entity @s[tag=sr_watch] run item replace entity @s hotbar.4 with ' +
    citem('watch', 'spyglass', {'text': 'Zuschauen: AN', 'color': 'aqua', 'bold': True}, ['Du schaust beim nächsten Run zu', 'Rechtsklick: doch mitspielen']),
    'execute unless entity @s[tag=sr_watch] run item replace entity @s hotbar.4 with ' +
    citem('watch', 'spyglass', {'text': 'Zuschauen: AUS', 'color': 'gray', 'bold': True}, ['Du spielst beim nächsten Run mit', 'Rechtsklick: zuschauen', 'Läuft ein Run: sofort live zuschauen']),
    'item replace entity @s hotbar.8 with ' + citem('menu', 'book', {'text': 'Speedrun-Menü', 'color': 'white', 'bold': True}, ['Rechtsklick: alle Optionen', 'auch über Esc → Speedrun-Menü']),
]
fn('item/hotbar', hb)
fn('item/click', [
    'scoreboard players set @s sr_click 0',
    f'execute if items entity @s weapon.mainhand *[minecraft:custom_data~{{sr_zettel:1b}}] run return run function {NS}:zettel/click',
    f'execute unless items entity @s weapon.mainhand minecraft:carrot_on_a_stick if items entity @s weapon.offhand *[minecraft:custom_data~{{sr_zettel:1b}}] run return run function {NS}:zettel/click',
    'execute unless entity @s[tag=sr_lobby] run return 0',
    f'execute if items entity @s weapon.mainhand *[minecraft:custom_data~{{sr:"start"}}] run return run function {NS}:start/by_player',
    f'execute if items entity @s weapon.mainhand *[minecraft:custom_data~{{sr:"mode"}}] run return run function {NS}:mode/cycle',
    f'execute if items entity @s weapon.mainhand *[minecraft:custom_data~{{sr:"role"}}] run return run function {NS}:role/cycle',
    f'execute if items entity @s weapon.mainhand *[minecraft:custom_data~{{sr:"watch"}}] run return run function {NS}:player/watch',
    f'execute if items entity @s weapon.mainhand *[minecraft:custom_data~{{sr:"menu"}}] run return run dialog show @s {NS}:menu',
])
fn('role/cycle', ['scoreboard players add @s sr_pref 1',
                  'execute if score @s sr_pref matches 5.. run scoreboard players set @s sr_pref 0',
                  'scoreboard players operation @s sr_rolle = @s sr_pref',
                  f'execute if score @s sr_rolle matches 1.. run return run function {NS}:role/pref',
                  'scoreboard players set @s sr_rolle 0', 'tag @s add sr_refresh',
                  f'tellraw @s {msg({"text": "Wunschrolle: egal (wird automatisch verteilt)", "color": "gray"})}'])
fn('item/sweep', ['scoreboard players set #itick sr 0',
                  'execute as @e[type=minecraft:item] if items entity @s contents *[minecraft:custom_data~{sr_item:1b}] run kill @s',
                  'clear @a[tag=!sr_lobby] *[minecraft:custom_data~{sr_item:1b}]'])


# ------------------------------------------------------------------ personal sidebars (one per player)
slot = ['scoreboard players add #k sr 1', 'scoreboard players operation @s sr_slot = #k sr',
        'execute store result storage sr:tmp s.k int 1 run scoreboard players get #k sr',
        f'execute if score #k sr matches ..16 run function {NS}:start/slot_join with storage sr:tmp s']
fn('start/slot', slot)
sj = ['$team join sr_p$(k) @s']
for n, (color, cname) in TEAMS.items():
    sj.append(f'$execute if score @s sr_team matches {n} run team modify sr_p$(k) prefix {tc({"text": "[" + cname + "] ", "color": color})}')
for k, color in SLOTS.items():
    sj.append(f'execute if score @s sr_slot matches {k} run waypoint modify @s color {color}')
fn('start/slot_join', sj)

def p_store():
    return ['execute store result storage sr:tmp p.k int 1 run scoreboard players get @s sr_slot',
            'execute store result storage sr:tmp p.n int 1 run scoreboard players get @s sr_team']
fn('p/init', p_store() + [f'execute if score @s sr_role matches {r} run return run function {NS}:p/init_r{r} with storage sr:tmp p' for r in STEPS])
fn('p/second', p_store() + [f'execute if score @s sr_role matches {r} run return run function {NS}:p/r{r} with storage sr:tmp p' for r in STEPS])

LBL = dict(TASKS)
def cnt(key, who='@s', obj=None):
    return [{'score': {'name': who, 'objective': obj or f'sr_v_{key}'}, 'color': 'yellow'}, {'text': f'/{NEED[key][0]}', 'color': 'gray'}]
for r, steps in STEPS.items():
    team_part = r != 0
    init = ['$scoreboard players reset * sr_o$(k)',
            f'$scoreboard objectives modify sr_o$(k) displayname {tc({"text": ROLES[r][0], "color": "yellow", "bold": True})}']
    for i, (key, text) in enumerate(steps):
        init += [f'$scoreboard players set s{i} sr_o$(k) {100 - i}',
                 f'$scoreboard players display name s{i} sr_o$(k) {tc({"text": "☐ " + text, "color": "gray"})}']
        if key in NEED:
            init.append(f'$scoreboard players display numberformat s{i} sr_o$(k) fixed {tc({"text": "0/" + str(NEED[key][0]), "color": "gray"})}')
    if team_part:
        init += [f'$scoreboard players set g0 sr_o$(k) 50',
                 f'$scoreboard players display name g0 sr_o$(k) {tc({"text": "── Team ──", "color": "dark_gray"})}']
        for j, (key, label) in enumerate(TEAM_LINES):
            init += [f'$scoreboard players set g{j + 1} sr_o$(k) {49 - j}',
                     f'$scoreboard players display name g{j + 1} sr_o$(k) {tc({"text": label, "color": "gray"})}']
    fn(f'p/init_r{r}', init)

    up = ['scoreboard players set #found sr 0']
    for i, (key, text) in enumerate(steps):
        up.append(f'execute if score @s sr_d_{key} matches 0 if function {NS}:pc/{key} run function {NS}:pd/{key}')
        bar = TIME_BAR + [{'text': '[' + ROLES[r][0] + '] ', 'color': 'yellow', 'bold': True},
               {'text': f'Schritt {i + 1}/{len(steps)} ▸ ', 'color': 'gray', 'bold': False},
               {'text': text, 'color': 'white', 'bold': False}]
        if key in NEED:
            bar += [{'text': '   ', 'bold': False}] + [dict(c, bold=False) for c in cnt(key)]
        up += [
            f'$execute if score @s sr_d_{key} matches 1 run scoreboard players display name s{i} sr_o$(k) {tc({"text": "✔ " + text, "color": "green"})}',
            f'$execute if score @s sr_d_{key} matches 1 run scoreboard players display numberformat s{i} sr_o$(k) fixed {tc({"text": "✔", "color": "green", "bold": True})}',
            f'$execute if score @s sr_d_{key} matches 0 if score #found sr matches 0 run scoreboard players display name s{i} sr_o$(k) {tc({"text": "▶ " + text, "color": "yellow", "bold": True})}',
            f'execute if score @s sr_d_{key} matches 0 if score #found sr matches 0 run title @s actionbar {tc(bar)}',
            f'$execute if score @s sr_d_{key} matches 0 if score #found sr matches 1 run scoreboard players display name s{i} sr_o$(k) {tc({"text": "☐ " + text, "color": "gray"})}',
        ]
        if key in NEED:
            up.append(f'$execute if score @s sr_d_{key} matches 0 run scoreboard players display numberformat s{i} sr_o$(k) fixed {tc(cnt(key))}')
        up.append(f'execute if score @s sr_d_{key} matches 0 run scoreboard players set #found sr 1')
    up.append(f'execute if score #found sr matches 0 run title @s actionbar {tc(TIME_BAR + [{"text": "[" + ROLES[r][0] + "] ", "color": "yellow", "bold": True}, {"text": "Alles erledigt – hilf deinem Team!", "color": "green", "bold": False}])}')
    if team_part:
        for j, (key, label) in enumerate(TEAM_LINES):
            e = f'g{j + 1}'
            up.append(f'$execute if score #t$(n)_{key} sr_done matches 1 run scoreboard players display numberformat {e} sr_o$(k) fixed {tc({"text": "✔", "color": "green", "bold": True})}')
            if key in NEED:
                up.append(f'$execute if score #t$(n)_{key} sr_done matches 0 run scoreboard players display numberformat {e} sr_o$(k) fixed ' +
                          tc([{'score': {'name': '#t$(n)_v_' + key, 'objective': 'sr'}, 'color': 'yellow'}, {'text': f'/{NEED[key][0]}', 'color': 'gray'}]))
            else:
                up.append(f'$execute if score #t$(n)_{key} sr_done matches 0 run scoreboard players display numberformat {e} sr_o$(k) fixed {tc({"text": "–", "color": "dark_gray"})}')
    for zero in (False, True):
        t = [{'text': ROLES[r][0], 'color': 'yellow', 'bold': True}, {'text': '  ⏱ ', 'color': 'white', 'bold': False},
             {'score': {'name': '#min', 'objective': 'sr'}, 'color': 'white', 'bold': False},
             {'text': ':0' if zero else ':', 'color': 'white', 'bold': False},
             {'score': {'name': '#sec', 'objective': 'sr'}, 'color': 'white', 'bold': False}]
        up.append(f'$execute if score #sec sr matches {"..9" if zero else "10.."} run scoreboard objectives modify sr_o$(k) displayname {tc(t)}')
    fn(f'p/r{r}', up)

# personal conditions (run as the player, at the player)
def inv(item, target='#a'):
    return f'execute store result score {target} sr run clear @s {item} 0'
PC = {
    'gear': [inv('minecraft:shield'), 'execute if score #a sr matches 0 run return 0',
             inv('minecraft:iron_sword', '#b'), inv('minecraft:diamond_sword', '#c'), inv('minecraft:netherite_sword', '#d'),
             'scoreboard players operation #b sr += #c sr', 'scoreboard players operation #b sr += #d sr',
             'execute if score #b sr matches 1.. run return 1', 'return 0'],
    'tools': [inv('minecraft:flint_and_steel'), 'execute if score #a sr matches 0 run return 0',
              inv('minecraft:bucket', '#b'), inv('minecraft:water_bucket', '#c'), inv('minecraft:lava_bucket', '#d'),
              'scoreboard players operation #b sr += #c sr', 'scoreboard players operation #b sr += #d sr',
              'execute if score #b sr matches 1.. run return 1', 'return 0'],
    'nether': ['execute if dimension minecraft:the_nether run return 1',
               'execute if entity @s[advancements={minecraft:story/enter_the_nether=true}] run return 1', 'return 0'],
    'fortress': ['execute if entity @s[advancements={minecraft:nether/find_fortress=true}] run return 1', 'return 0'],
    'bastion': ['execute if entity @s[advancements={minecraft:nether/find_bastion=true}] run return 1', 'return 0'],
    'stronghold': ['execute if entity @s[advancements={minecraft:story/follow_ender_eye=true}] run return 1', 'return 0'],
    'end': ['execute if dimension minecraft:the_end run return 1',
            'execute if entity @s[advancements={minecraft:story/enter_the_end=true}] run return 1', 'return 0'],
    'blaze': ['scoreboard players operation @s sr_v_blaze = @s sr_pu_blaze', 'execute if score @s sr_v_blaze matches 7.. run return 1', 'return 0'],
    'pearls': ['scoreboard players operation @s sr_v_pearls = @s sr_pu_pearl', 'execute if score @s sr_v_pearls matches 12.. run return 1', 'return 0'],
    'beds': ['execute store result score @s sr_v_beds run clear @s #minecraft:beds 0', 'execute if score @s sr_v_beds matches 7.. run return 1', 'return 0'],
    'food': ['scoreboard players set @s sr_v_food 0', *[f'scoreboard players operation @s sr_v_food += @s sr_cr_f{i}' for i in range(len(FOOD))],
             'execute if score @s sr_v_food matches 20.. run return 1', 'return 0'],
    'eyes': ['scoreboard players operation @s sr_v_eyes = @s sr_cr_eye', 'execute if score @s sr_v_eyes matches 12.. run return 1', 'return 0'],
    'dragon': ['execute if score #finished sr matches 1 run return 1', 'return 0'],
}
for key in STEP_KEYS:
    fn(f'pc/{key}', PC[key])
    fn(f'pd/{key}', [f'scoreboard players set @s sr_d_{key} 1',
                     f'tellraw @s {tc([{"text": "✔ ", "color": "green", "bold": True}, {"text": "Dein Schritt erledigt: ", "color": "gray"}, {"text": LBL[key], "color": "white"}])}',
                     'playsound minecraft:entity.experience_orb.pickup master @s ~ ~ ~ 0.8 1.2'])


# ------------------------------------------------------------------ rescue: run player respawned on the lobby island
fn('p/rescue', [
    f'execute unless data entity @s LastDeathLocation run return run function {NS}:p/to_start',
    'data modify storage sr:tmp d.dim set from entity @s LastDeathLocation.dimension',
    'execute store result storage sr:tmp d.x int 1 run data get entity @s LastDeathLocation.pos[0]',
    'execute store result storage sr:tmp d.z int 1 run data get entity @s LastDeathLocation.pos[2]',
    'execute store result score #dy sr run data get entity @s LastDeathLocation.pos[1]',
    'scoreboard players add #dy sr 3',
    'execute store result storage sr:tmp d.y int 1 run scoreboard players get #dy sr',
    'scoreboard players set #ok sr 0',
    f'execute if score #dy sr matches 4.. run function {NS}:p/to_death with storage sr:tmp d',
    f'execute if score #ok sr matches 0 run return run function {NS}:p/to_start',
    f'function {NS}:p/fix_spawn',
    f'tellraw @s {msg({"text": "Du warst in der Lobby gelandet – zurück zu deinem Todespunkt.", "color": "aqua"})}',
])
fn('p/to_death', [
    '$execute in $(dim) store success score #ok sr run spreadplayers $(x) $(z) 0 6 under $(y) false @s',
    '$execute if score #ok sr matches 0 in $(dim) store success score #ok sr run spreadplayers $(x) $(z) 0 24 under $(y) false @s',
])
fn('p/to_start', [
    'execute store result storage sr:tmp s.x int 1 run scoreboard players get @s sr_sx',
    'execute store result storage sr:tmp s.y int 1 run scoreboard players get @s sr_sy',
    'execute store result storage sr:tmp s.z int 1 run scoreboard players get @s sr_sz',
    f'function {NS}:p/tp_start with storage sr:tmp s',
    f'function {NS}:p/fix_spawn',
    f'tellraw @s {msg({"text": "Du warst in der Lobby gelandet – zurück zu deinem Startpunkt.", "color": "aqua"})}',
])
fn('p/tp_start', ['$execute in minecraft:overworld run tp @s $(x) $(y) $(z)'])
fn('p/fix_spawn', [
    'execute store result storage sr:tmp s.x int 1 run scoreboard players get @s sr_sx',
    'execute store result storage sr:tmp s.y int 1 run scoreboard players get @s sr_sy',
    'execute store result storage sr:tmp s.z int 1 run scoreboard players get @s sr_sz',
    f'function {NS}:p/spawn_start with storage sr:tmp s',
])
fn('p/spawn_start', ['$execute in minecraft:overworld run spawnpoint @s $(x) $(y) $(z)'])


# ------------------------------------------------------------------ Speedrun-Zettel (everyone always has it, right click -> dialog)
class Raw(str):
    """SNBT fragment inserted verbatim (macro placeholder holding an SNBT text component)."""


def snbt(o):
    if isinstance(o, Raw):
        return str(o)
    if isinstance(o, bool):
        return 'true' if o else 'false'
    if isinstance(o, int):
        return str(o)
    if isinstance(o, str):
        return json.dumps(o, ensure_ascii=False)
    if isinstance(o, list):
        return '[' + ','.join(snbt(v) for v in o) + ']'
    if isinstance(o, dict):
        return '{' + ','.join(f'{k}:{snbt(v)}' for k, v in o.items()) + '}'
    raise TypeError(o)


def sval(o):
    """SNBT text component stored as a string in storage (for macro insertion)."""
    t = snbt(o).replace('\\', '\\\\').replace("'", "\\'")
    return f"'{t}'"


ZSLOT = 'hotbar.7'          # slot 8 (lobby: 1 start, 2 mode, 3 role, 5 watch, 8 zettel, 9 menu book)
ZTEST = '*[minecraft:custom_data~{sr_zettel:1b}]'
ZETTEL = 'minecraft:carrot_on_a_stick[' + ','.join([
    'minecraft:item_model="minecraft:paper"',
    f'minecraft:custom_name={tc({"text": "Speedrun-Zettel", "color": "gold", "bold": True, "italic": False})}',
    'minecraft:lore=[' + ','.join(tc({'text': l, 'color': c, 'italic': False}) for l, c in (
        ('Rechtsklick: alles für den Run', 'yellow'), ('Items mit Ziel, Team-Stand, Aufgaben, Zeit', 'gray'),
        ('Geht nicht verloren', 'dark_gray'))) + ']',
    'minecraft:custom_data={sr_zettel:1b}',
    'minecraft:unbreakable={}',
    'minecraft:tooltip_display={hidden_components:["minecraft:unbreakable"]}',
    'minecraft:use_cooldown={seconds:0.5f}',
    'minecraft:enchantment_glint_override=true',
]) + ']'
ZSLOTS = [ZSLOT] + [f'hotbar.{i}' for i in range(9) if f'hotbar.{i}' != ZSLOT] + [f'inventory.{i}' for i in range(27)]

fn('zettel/tick', [
    'scoreboard players set #ztick sr 0',
    f'execute as @e[type=minecraft:item] if items entity @s contents {ZTEST} run kill @s',
    # @e[type=player] skips players on the death screen; they get it back after respawning
    f'execute as @e[type=minecraft:player] run function {NS}:zettel/keep',
])
fn('zettel/keep', [
    # count also sees the cursor and the crafting grid
    f'execute store result score #zn sr run clear @s {ZTEST} 0',
    'execute if score #zn sr matches 1 run return 0',
    f'execute if score #zn sr matches 2.. run clear @s {ZTEST}',
    f'function {NS}:zettel/give',
])
# right click: use_cooldown does not apply to carrot_on_a_stick (its use() returns PASS), and a held
# right click repeats every 4 ticks -> debounce: open only if the previous click was >= 10 ticks ago
fn('zettel/click', [
    'execute store result score #znow sr run time query gametime',
    'execute unless score @s sr_zcd matches -2147483648..2147483647 run scoreboard players set @s sr_zcd -1000',
    'scoreboard players operation #zgap sr = #znow sr',
    'scoreboard players operation #zgap sr -= @s sr_zcd',
    'scoreboard players operation @s sr_zcd = #znow sr',
    'execute if score #zgap sr matches 0..9 run return 0',
    f'function {NS}:zettel/open',
])
fn('zettel/give', [f'execute unless items entity @s {sl} * run return run item replace entity @s {sl} with {ZETTEL}' for sl in ZSLOTS])

# time string "m:ss" / "h:mm:ss" in storage sr:run tstr (from #s = seconds)
fn('time/fmt', [
    'scoreboard players operation #th sr = #s sr', 'scoreboard players operation #th sr /= #3600 sr',
    'scoreboard players operation #tm sr = #s sr', 'scoreboard players operation #tm sr /= #60 sr',
    'execute if score #th sr matches 1.. run scoreboard players operation #tm sr %= #60 sr',
    'scoreboard players operation #ts sr = #s sr', 'scoreboard players operation #ts sr %= #60 sr',
    'execute store result storage sr:tmp t.h int 1 run scoreboard players get #th sr',
    'execute store result storage sr:tmp t.m int 1 run scoreboard players get #tm sr',
    'execute store result storage sr:tmp t.s int 1 run scoreboard players get #ts sr',
    'data modify storage sr:tmp t.mp set value ""', 'data modify storage sr:tmp t.sp set value ""',
    'execute if score #tm sr matches ..9 run data modify storage sr:tmp t.mp set value "0"',
    'execute if score #ts sr matches ..9 run data modify storage sr:tmp t.sp set value "0"',
    f'execute if score #th sr matches 1.. run return run function {NS}:time/hms with storage sr:tmp t',
    f'function {NS}:time/ms with storage sr:tmp t',
])
fn('time/hms', ['$data modify storage sr:run tstr set value "$(h):$(mp)$(m):$(sp)$(s)"'])
fn('time/ms', ['$data modify storage sr:run tstr set value "$(m):$(sp)$(s)"'])

PICKS = [f'minecraft:{m}_pickaxe' for m in ('wooden', 'stone', 'copper', 'iron', 'golden', 'diamond', 'netherite')]
# (key, icon, icon count, label, [(item, factor)], divisor, target, team task that also ticks it off)
ZSECTIONS = [
    ('Oberwelt', [
        ('pick', 'minecraft:stone_pickaxe', 1, 'Spitzhacke', [(p, 1) for p in PICKS], 1, 1, None),
        ('sword', 'minecraft:iron_sword', 1, 'Eisenschwert', [('minecraft:iron_sword', 1), ('minecraft:diamond_sword', 1), ('minecraft:netherite_sword', 1)], 1, 1, 'gear'),
        ('shield', 'minecraft:shield', 1, 'Schild', [('minecraft:shield', 1)], 1, 1, 'gear'),
        ('bucket', 'minecraft:water_bucket', 1, 'Eimer (Wasser + Lava)', [('minecraft:bucket', 1), ('minecraft:water_bucket', 1), ('minecraft:lava_bucket', 1)], 1, 1, 'tools'),
        ('flint', 'minecraft:flint_and_steel', 1, 'Feuerzeug', [('minecraft:flint_and_steel', 1)], 1, 1, 'tools'),
        ('obsi', 'minecraft:obsidian', 10, 'Obsidian (oder Portal gießen)', [('minecraft:obsidian', 1)], 1, 10, 'nether'),
        ('food', 'minecraft:cooked_beef', 20, 'Essen (gebraten)', [(f'minecraft:{f}', 1) for f in FOOD], 1, NEED['food'][0], 'food'),
        ('beds', 'minecraft:red_bed', 1, 'Betten (Drache)', [('#minecraft:beds', 1)], 1, NEED['beds'][0], 'beds'),
    ]),
    ('Nether', [
        ('blaze', 'minecraft:blaze_rod', NEED['blaze'][0], 'Blaze-Ruten', [('minecraft:blaze_rod', 2), ('minecraft:blaze_powder', 1), ('minecraft:ender_eye', 1)], 2, NEED['blaze'][0], 'blaze'),
        ('pearls', 'minecraft:ender_pearl', NEED['pearls'][0], 'Enderperlen', [('minecraft:ender_pearl', 1), ('minecraft:ender_eye', 1)], 1, NEED['pearls'][0], 'pearls'),
        ('gold', 'minecraft:gold_ingot', 32, 'Gold zum Tauschen', [('minecraft:gold_ingot', 1), ('minecraft:gold_block', 9)], 1, 32, 'pearls'),
    ]),
    ('End', [
        ('eyes', 'minecraft:ender_eye', NEED['eyes'][0], 'Enderaugen', [('minecraft:ender_eye', 1)], 1, NEED['eyes'][0], 'eyes'),
        ('bow', 'minecraft:bow', 1, 'Bogen (für Kristalle)', [('minecraft:bow', 1), ('minecraft:crossbow', 1)], 1, 1, None),
        ('arrows', 'minecraft:arrow', 16, 'Pfeile', [('minecraft:arrow', 1), ('minecraft:spectral_arrow', 1), ('minecraft:tipped_arrow', 1)], 1, 16, None),
        ('blocks', 'minecraft:cobblestone', 64, 'Blöcke zum Bauen', [('minecraft:cobblestone', 1), ('minecraft:cobbled_deepslate', 1), ('minecraft:netherrack', 1), ('minecraft:dirt', 1), ('minecraft:end_stone', 1)], 1, 64, None),
    ]),
]
OK = lambda: {'text': ' ✔', 'color': 'green', 'bold': True}
NO = lambda: {'text': '', 'color': 'gray'}

z_open = [
    # who counts: in a run the whole (online) team, otherwise only you
    'tag @a remove sr_zg',
    'scoreboard players set #zt sr 0',
    'execute if entity @s[tag=sr_run] run scoreboard players operation #zt sr = @s sr_team',
    # spectators see the team of the nearest runner (same dimension)
    'execute if entity @s[tag=sr_spec] at @s as @p[tag=sr_run] run scoreboard players operation #zt sr = @s sr_team',
    'execute if entity @s[tag=sr_spec] if score #zt sr matches 0 as @r[tag=sr_run] run scoreboard players operation #zt sr = @s sr_team',
    'execute if score #zt sr matches 1.. as @a[tag=sr_run] if score @s sr_team = #zt sr run tag @s add sr_zg',
    'execute if score #zt sr matches 0 run tag @s add sr_zg',
]
for _, rows in ZSECTIONS:
    for key, icon, icnt, label, terms, div, target, task in rows:
        z_open.append('scoreboard players set #zv sr 0')
        for item, mult in terms:
            z_open += [f'execute as @a[tag=sr_zg] store result score @s sr_tmp run clear @s {item} 0']
            z_open += ['execute as @a[tag=sr_zg] run scoreboard players operation #zv sr += @s sr_tmp'] * mult
        if div != 1:
            z_open.append(f'scoreboard players operation #zv sr /= #{div} sr')
        z_open += [f'execute store result storage sr:zettel d.v_{key} int 1 run scoreboard players get #zv sr',
                   f'data modify storage sr:zettel d.c_{key} set value {sval(NO())}',
                   f'execute if score #zv sr matches {target}.. run data modify storage sr:zettel d.c_{key} set value {sval(OK())}']
# header: team, time, role
z_open += [
    f'data modify storage sr:zettel d.team set value {sval({"text": "Lobby", "color": "gray"})}',
    'data modify storage sr:zettel d.time set value "–:––"',
    'execute if score #active sr matches 1 run data modify storage sr:zettel d.time set from storage sr:run tstr',
    'execute if entity @s[tag=sr_run] run data modify storage sr:zettel d.time set from storage sr:run tstr',
    f'data modify storage sr:zettel d.who set value {sval({"text": "Zählt nur deine Items (im Run: das ganze Team)", "color": "dark_gray"})}',
    f'execute if score #zt sr matches 1.. run data modify storage sr:zettel d.who set value {sval({"text": "Zahlen = alle Items deines Teams (online)", "color": "dark_gray"})}',
    f'execute if entity @s[tag=sr_spec] run data modify storage sr:zettel d.team set value {sval({"text": "Zuschauer", "color": "aqua"})}',
    f'data modify storage sr:zettel d.role set value {sval({"text": "noch keine – wird beim Start verteilt", "color": "gray"})}',
    f'data modify storage sr:zettel d.hint set value {sval({"text": "Wunschrolle: Slot 3 in der Lobby", "color": "gray"})}',
    f'data modify storage sr:zettel d.next set value {sval({"text": "Modus wählen, Netherstern: Run starten", "color": "white"})}',
    f'data modify storage sr:zettel d.tip set value {sval({"text": "Lobby: Modus mit der Uhr wählen, mit dem Netherstern starten. Im Run zählt dieser Zettel die Items deines ganzen Teams und hakt alles ab.", "color": "gray"})}',
    'data modify storage sr:zettel d.cnt set value 0',
]
for i, (key, label) in enumerate(TASKS):
    z_open.append(f'data modify storage sr:zettel d.t{i} set value {sval([{"text": "☐ ", "color": "dark_gray"}, {"text": label, "color": "gray"}])}')
for r, (name, hint) in ROLES.items():
    z_open += [f'execute if entity @s[tag=sr_run] if score @s sr_role matches {r} run data modify storage sr:zettel d.role set value {sval({"text": name, "color": "yellow", "bold": True})}',
               f'execute if entity @s[tag=sr_run] if score @s sr_role matches {r} run data modify storage sr:zettel d.hint set value {sval({"text": hint, "color": "gray"})}']
# next personal step: last matching line wins -> iterate the steps backwards
for r, steps in STEPS.items():
    z_open.append(f'execute if entity @s[tag=sr_run] if score @s sr_role matches {r} run data modify storage sr:zettel d.next set value {sval({"text": "Alles erledigt – hilf deinem Team!", "color": "green"})}')
    for i, (key, text) in reversed(list(enumerate(steps))):
        z_open.append(f'execute if entity @s[tag=sr_run] if score @s sr_role matches {r} if score @s sr_d_{key} matches 0 run data modify storage sr:zettel d.next set value '
                      + sval([{"text": f"Schritt {i + 1}/{len(steps)}: ", "color": "gold"}, {"text": text + (f' ({NEED[key][0]})' if key in NEED else ''), "color": "white"}]))
z_open += [f'execute if score #zt sr matches {n} run function {NS}:zettel/team_t{n}' for n in TEAMS]
z_open += [
    f'execute if entity @s[tag=sr_spec] run data modify storage sr:zettel d.role set value {sval({"text": "Zuschauer", "color": "aqua", "bold": True})}',
    f'execute if entity @s[tag=sr_spec] run data modify storage sr:zettel d.hint set value {sval({"text": "Du siehst den Stand des Teams, das dir am nächsten ist.", "color": "gray"})}',
    f'execute if entity @s[tag=sr_spec] run data modify storage sr:zettel d.next set value {sval({"text": "Zurück zur Lobby: Esc → Speedrun-Menü", "color": "white"})}',
    f'execute if entity @s[tag=sr_spec] if score #zt sr matches 1.. run data modify storage sr:zettel d.who set value {sval({"text": "Zahlen = alle Items dieses Teams (online)", "color": "dark_gray"})}',
]
z_open += [f'function {NS}:zettel/show with storage sr:zettel d',
           'tag @a remove sr_zg',
           'playsound minecraft:item.book.page_turn master @s ~ ~ ~ 0.8 1.1']
fn('zettel/open', z_open)

TIPS = [  # (unfinished team task, phase tip) - first unfinished one wins
    ('nether', 'Oberwelt: Holz, Steinwerkzeug, Eisen für Eimer, Feuerzeug, Schild. Essen braten, Wolle für Betten. Portal: Wasser auf Lava gießen (Form 4×5) oder 10 Obsidian.'),
    ('blaze', 'Nether: Festung suchen (Nether-Ziegel), 7 Blaze-Ruten farmen. Schild hoch, Feuerball zurückschlagen. Portal-Koordinaten merken!'),
    ('pearls', 'Nether: Bastion oder Piglins: Gold hinwerfen, Perlen tauschen (12+). Goldrüstung anziehen, sonst greifen Piglins an.'),
    ('eyes', 'Zurück in die Oberwelt: Blaze-Ruten zu Pulver, mit Perlen 12 Enderaugen craften.'),
    ('stronghold', 'Enderauge werfen und hinterherlaufen, nach ca. 500 Blöcken nochmal. Fliegt es nach unten: dort graben.'),
    ('end', 'Stronghold: Endportal-Raum suchen (Silberfisch-Spawner), fehlende Augen einsetzen, alle rein. Blöcke mitnehmen!'),
    ('dragon', 'End: Endermen nicht anschauen. Kristalle mit Bogen abschießen, Käfige hochbauen. Sitzt der Drache auf dem Portal: Bett hinstellen, Block davor, klicken.'),
]
for n, (color, cname) in TEAMS.items():
    t = [f'data modify storage sr:zettel d.team set value {sval({"text": "Team " + cname, "color": color, "bold": True})}',
         f'execute store result storage sr:zettel d.cnt int 1 run scoreboard players get #t{n}_cnt sr']
    for i, (key, label) in enumerate(TASKS):
        t += [f'execute if score #t{n}_{key} sr_done matches 0 run data modify storage sr:zettel d.t{i} set value {sval([{"text": "✘ ", "color": "red"}, {"text": label, "color": "gray"}])}',
              f'execute if score #t{n}_{key} sr_done matches 1 run data modify storage sr:zettel d.t{i} set value {sval([{"text": "✔ ", "color": "green", "bold": True}, {"text": label, "color": "green"}])}']
    for _, rows in ZSECTIONS:
        for key, icon, icnt, label, terms, div, target, task in rows:
            if task:
                t.append(f'execute if score #t{n}_{task} sr_done matches 1 run data modify storage sr:zettel d.c_{key} set value {sval(OK())}')
    t.append(f'data modify storage sr:zettel d.tip set value {sval({"text": "Drache besiegt – GG!", "color": "green"})}')
    for key, tip in reversed(TIPS):
        t.append(f'execute if score #t{n}_{key} sr_done matches 0 run data modify storage sr:zettel d.tip set value {sval({"text": tip, "color": "white"})}')
    fn(f'zettel/team_t{n}', t)

# the dialog (inline, built by macro from storage sr:zettel d)
H = lambda txt: {'type': 'minecraft:plain_message', 'width': 300, 'contents': {'text': f'— {txt} —', 'color': 'gold', 'bold': True}}
body = [
    {'type': 'minecraft:plain_message', 'width': 300, 'contents': [
        {'text': ''}, {'text': '⏱ $(time)', 'color': 'white', 'bold': True}, {'text': '   ·   ', 'color': 'dark_gray'}, Raw('$(team)'),
        {'text': '\n'}, {'text': 'Rolle: ', 'color': 'gray'}, Raw('$(role)'), {'text': '\n'}, Raw('$(hint)'),
        {'text': '\n'}, {'text': '▶ ', 'color': 'gold'}, Raw('$(next)')]},
]
for title, rows in ZSECTIONS:
    body.append(H(title))
    for key, icon, icnt, label, terms, div, target, task in rows:
        body.append({'type': 'minecraft:item', 'item': {'id': icon, 'count': icnt}, 'show_decorations': True, 'show_tooltip': True,
                     'description': {'width': 230, 'contents': [
                         {'text': ''}, {'text': label + '  ', 'color': 'white'}, {'text': '$(v_' + key + ')', 'color': 'yellow', 'bold': True},
                         {'text': f'/{target}', 'color': 'gray'}, Raw(f'$(c_{key})')]}})
body.append({'type': 'minecraft:plain_message', 'width': 300, 'contents': Raw('$(who)')})
body.append(H(f'Team-Aufgaben  $(cnt)/{NT}'))
tl = [{'text': ''}]
for i in range(NT):
    tl.append(Raw(f'$(t{i})'))
    tl.append({'text': '\n' if i % 2 else '     '})
body.append({'type': 'minecraft:plain_message', 'width': 320, 'contents': tl})
body.append(H('Tipp'))
body.append({'type': 'minecraft:plain_message', 'width': 300, 'contents': Raw('$(tip)')})
ZDIALOG = {
    'type': 'minecraft:multi_action',
    'title': {'text': 'SPEEDRUN-ZETTEL', 'color': 'gold', 'bold': True},
    'external_title': {'text': 'Speedrun-Zettel'},
    'body': body,
    'columns': 3,
    'actions': [
        {'label': {'text': '↻ Aktualisieren', 'color': 'green'}, 'tooltip': {'text': 'Zahlen neu zählen'}, 'width': 100,
         'action': {'type': 'minecraft:run_command', 'command': 'trigger sr_aktion set 9'}},
        {'label': {'text': '☰ Mein Plan', 'color': 'gold'}, 'tooltip': {'text': 'Alle Schritte deiner Rolle'}, 'width': 100,
         'action': {'type': 'minecraft:run_command', 'command': 'trigger sr_aktion set 7'}},
        {'label': {'text': 'Speedrun-Menü'}, 'tooltip': {'text': 'Modus, Start, Rollen, Zuschauen'}, 'width': 100,
         'action': {'type': 'minecraft:run_command', 'command': 'trigger sr_aktion set 3'}},
    ],
    'exit_action': {'label': {'text': 'Schließen'}, 'width': 200},
}
fn('zettel/show', ['$dialog show @s ' + snbt(ZDIALOG)])

# ------------------------------------------------------------------ lobby sidebar
lob = ['scoreboard players reset * sr_lobby']
rows = [
    ('a1', {'text': ' '}),
    ('a2', [{'text': 'Hotbar-Items: ', 'color': 'gray'}, {'text': 'Rechtsklick', 'color': 'yellow'}]),
    ('a3', [{'text': '1 ', 'color': 'dark_gray'}, {'text': 'Run starten', 'color': 'green'}]),
    ('a4', [{'text': '2 ', 'color': 'dark_gray'}, {'text': 'Modus wechseln', 'color': 'yellow'}]),
    ('a5', [{'text': '3 ', 'color': 'dark_gray'}, {'text': 'Wunschrolle', 'color': 'gold'}]),
    ('a6', [{'text': '5 ', 'color': 'dark_gray'}, {'text': 'Zuschauen', 'color': 'aqua'}]),
    ('a6z', [{'text': '8 ', 'color': 'dark_gray'}, {'text': 'Speedrun-Zettel', 'color': 'gold'}]),
    ('a7', [{'text': '9 ', 'color': 'dark_gray'}, {'text': 'Menü', 'color': 'white'}]),
    ('a8', {'text': '  '}),
    ('a9', [{'text': 'Siege: ', 'color': 'dark_gray'}, {'text': 'Tab-Liste', 'color': 'gray'}]),
]
for i, (e, t) in enumerate(rows):
    lob += [f'scoreboard players set {e} sr_lobby {len(rows) - i}', f'scoreboard players display name {e} sr_lobby {tc(t)}']
fn('sidebar/lobby', lob)

# ------------------------------------------------------------------ write
if os.path.exists(ROOT):
    shutil.rmtree(ROOT)
for path, content in files.items():
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(content)
zpath = os.path.join(OUT, 'speedrun.zip')
with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
    for path, content in files.items():
        z.writestr(path, content)
print(f'{len(files)} files, {len(POS)} start positions -> {zpath}')
