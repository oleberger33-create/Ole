#!/usr/bin/env python3
"""Speedrun-Datapack v2 (Minecraft 26.3, data pack format 121).

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
    ('fortress', 'Festung gefunden'), ('bastion', 'Bastion gefunden'), ('blaze', '7+ Blaze-Ruten'),
    ('pearls', '12+ Enderperlen'), ('beds', '7 Betten'), ('eyes', '12 Enderaugen'),
    ('stronghold', 'Stronghold gefunden'), ('end', 'End betreten'), ('dragon', 'Drache besiegt'),
]
NT = len(TASKS)
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
    btn({'text': '👁 Zuschauen an/aus'}, 'Beim nächsten Run zuschauen oder jetzt live zuschauen', 'trigger sr_aktion set 4'),
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
    f'scoreboard objectives add sr_wins dummy {tc({"text": "Siege", "color": "gold"})}',
    'scoreboard objectives setdisplay list sr_wins',
    f'scoreboard objectives add sr_lobby dummy {tc({"text": "SPEEDRUN", "color": "gold", "bold": True})}',
    'scoreboard objectives modify sr_lobby numberformat blank',
    'scoreboard objectives setdisplay sidebar sr_lobby',
]
for n, (color, cname) in TEAMS.items():
    load += [
        f'team add sr_t{n}',
        f'team modify sr_t{n} color {color}',
        f'team modify sr_t{n} displayName {tc({"text": "Team " + cname, "color": color})}',
        f'team modify sr_t{n} prefix {tc({"text": "[" + cname + "] ", "color": color})}',
        f'team modify sr_t{n} friendlyFire false',
        f'scoreboard objectives add sr_s{n} dummy {tc({"text": "Team " + cname, "color": color, "bold": True})}',
        f'scoreboard objectives modify sr_s{n} numberformat blank',
        f'scoreboard objectives setdisplay sidebar.team.{color} sr_s{n}',
        f'bossbar add {NS}:t{n} {tc({"text": "Team " + cname})}',
        f'bossbar set {NS}:t{n} color {BAR_COLOR[color]}',
        f'bossbar set {NS}:t{n} style notched_12',
        f'bossbar set {NS}:t{n} max {NT}',
    ]
load += [
    'scoreboard players set #20 sr 20', 'scoreboard players set #60 sr 60', 'scoreboard players set #2 sr 2',
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
    'gamerule show_advancement_messages false',
    'setworldspawn 0 200 0',
    f'{OW} forceload add -16 -16 15 15',
    f'function {NS}:sidebar/lobby',
    f'execute unless score #built sr matches {BUILD_VERSION} run schedule function {NS}:lobby/try_build 40t',
]
fn('load', load)

# ------------------------------------------------------------------ tick
fn('tick', [
    'scoreboard players enable @a sr_rolle',
    'scoreboard players enable @a sr_aktion',
    f'execute as @a[tag=!sr_seen2] run function {NS}:player/first_join',
    f'execute as @a[scores={{sr_leave=1..}}] run function {NS}:player/rejoin',
    f'execute as @a[scores={{sr_rolle=1..}}] run function {NS}:role/pref',
    f'execute as @a[scores={{sr_aktion=1..}}] run function {NS}:player/action',
    f'execute as @a[scores={{sr_click=1..}}] run function {NS}:item/click',
    'scoreboard players add #itick sr 1',
    'execute if score #itick sr matches 10.. run function sr:item/sweep',
    f'execute as @a[tag=sr_lobby] run function {NS}:lobby/keep',
    f'execute if score #cd sr matches 1.. run function {NS}:start/cd_tick',
    f'execute if score #active sr matches 1 run function {NS}:run/tick',
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
    'scoreboard players set @s sr_role -1', 'scoreboard players set @s sr_team 0',
    f'function {NS}:player/reset_state',
    'gamemode adventure @s',
    f'function {NS}:player/tp_lobby',
    f'{OW} spawnpoint @s 0 200 0',
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
    S = f'@a[team=sr_t{n},tag=!sr_hasrole'
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
    lines = ['scoreboard players set #size sr 0', f'execute as @a[team=sr_t{n}] run scoreboard players add #size sr 1',
             'execute if score #size sr matches 0 run return 0',
             f'execute if score #size sr matches 1 as @a[team=sr_t{n}] run function {NS}:role/give {{r:0}}']
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
    *[f'execute if entity @s[team=sr_t{n}] run title @s title {tc({"text": "Team " + cname, "color": color, "bold": True})}' for n, (color, cname) in TEAMS.items()],
    *brief,
    'execute if score #teams sr matches 2.. run tellraw @s ' + msg({'text': 'RENNEN! ', 'color': 'red', 'bold': True}, {'text': 'Jedes Team startet woanders. Wer zuerst den Drachen tötet, gewinnt.', 'color': 'white'}),
])
hint_lines = []
for r, (name, hint) in ROLES.items():
    hint_lines.append(f'execute if score @s sr_role matches {r} run title @s actionbar {tc([{"text": name, "color": "yellow", "bold": True}, {"text": "  ·  " + hint, "color": "gray"}])}')
fn('role/actionbar', hint_lines)

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
    'team leave @a', 'tag @a remove sr_run', 'tag @a remove sr_spec', 'tag @a remove sr_hasrole', 'tag @a remove sr_pending',
    'scoreboard players set @a sr_role -1', 'scoreboard players set @a sr_team 0',
    'tag @a[tag=!sr_watch] add sr_pending',
    # team size
    'scoreboard players set #k sr 99',
    *[f'execute if score #mode sr matches {m} run scoreboard players set #k sr {size}' for m, (_, size) in MODES.items()],
    'scoreboard players set #n sr 1', 'scoreboard players set #c sr 0',
    f'function {NS}:start/assign_next',
    'scoreboard players set #teams sr 0',
    *[f'execute if entity @a[team=sr_t{n}] run scoreboard players add #teams sr 1' for n in TEAMS],
    'tag @a[team=!] add sr_run', 'tag @a[tag=sr_run] remove sr_lobby',
    f'execute as @a[tag=sr_run] run function {NS}:player/reset_state',
    'gamemode survival @a[tag=sr_run]',
    'time set 0', 'weather clear', 'difficulty normal',
    'scoreboard players set #crystals sr 0', 'scoreboard players set #dseen sr 0', 'scoreboard players set #finished sr 0',
    f'{OW} tp @a[tag=sr_run] 0 200 0',
]
for n in TEAMS:
    launch += [f'execute if entity @a[team=sr_t{n}] run function {NS}:team/setup_t{n}',
               f'execute unless entity @a[team=sr_t{n}] run bossbar set {NS}:t{n} visible false']
launch += [
    'execute as @a[tag=sr_run] at @s run spawnpoint @s ~ ~ ~',
    'scoreboard players set #ticks sr 0', 'scoreboard players set #active sr 1',
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
    fn(f'start/join_t{n}', [f'team join sr_t{n} @s', 'tag @s remove sr_pending', f'scoreboard players set @s sr_team {n}'])

# per-team setup: roles, start position, sidebar, bossbar, task flags
for n, (color, cname) in TEAMS.items():
    sel = f'@a[tag=sr_run,team=sr_t{n}]'
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
    setup += [f'bossbar set {NS}:t{n} value 0', f'bossbar set {NS}:t{n} visible true', f'bossbar set {NS}:t{n} players {sel}']
    fn(f'team/setup_t{n}', setup)

fn('pos/pick', [f'execute if score #slot sr matches {i} run return run function {NS}:pos/set {{x:{x},z:{z}}}' for i, (x, z) in enumerate(POS)])
fn('pos/set', ['$scoreboard players set #cx sr $(x)', '$scoreboard players set #cz sr $(z)'])
fn('pos/place', [
    '$execute in minecraft:overworld store success score #ok sr run spreadplayers $(x) $(z) 2 24 false @a[tag=sr_run,team=sr_t$(n)]',
    '$execute if score #ok sr matches 0 in minecraft:overworld store success score #ok sr run spreadplayers $(x) $(z) 2 96 false @a[tag=sr_run,team=sr_t$(n)]',
    '$execute if score #ok sr matches 0 in minecraft:overworld store success score #ok sr run spreadplayers $(x) $(z) 2 320 false @a[tag=sr_run,team=sr_t$(n)]',
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
    'scoreboard players add #ticks sr 1',
    'scoreboard players operation #t sr = #ticks sr', 'scoreboard players operation #t sr %= #20 sr',
    f'execute if score #t sr matches 0 run function {NS}:run/second',
])
second = [
    f'execute unless entity @a[tag=sr_run] run return run function {NS}:run/empty',
    'scoreboard players operation #s sr = #ticks sr', 'scoreboard players operation #s sr /= #20 sr',
    'scoreboard players operation #min sr = #s sr', 'scoreboard players operation #min sr /= #60 sr',
    'scoreboard players operation #sec sr = #s sr', 'scoreboard players operation #sec sr %= #60 sr',
]
for n in TEAMS:
    second.append(f'execute if entity @a[tag=sr_run,team=sr_t{n}] run function {NS}:team/second_t{n}')
second += [
    'scoreboard players operation #half sr = #s sr', 'scoreboard players operation #half sr %= #2 sr',
    f'execute if score #half sr matches 0 as @a[tag=sr_run] run function {NS}:role/actionbar',
    f'function {NS}:run/end_watch',
]
fn('run/second', second)
fn('run/empty', ['scoreboard players set #active sr 0',
                 *[f'bossbar set {NS}:t{n} visible false' for n in TEAMS],
                 f'tellraw @a {msg({"text": "Run beendet – niemand mehr im Run.", "color": "gray"})}'])

for n, (color, cname) in TEAMS.items():
    sel = f'@a[tag=sr_run,team=sr_t{n}]'
    def bar(zero):
        return tc([{'text': 'Team ' + cname, 'color': color, 'bold': True},
                   {'text': '  ·  ', 'color': 'gray'}, {'nbt': 'mode', 'storage': 'sr:run', 'interpret': True, 'color': 'white'},
                   {'text': '   ⏱ ', 'color': 'white'}, {'score': {'name': '#min', 'objective': 'sr'}, 'color': 'white'},
                   {'text': ':0' if zero else ':', 'color': 'white'}, {'score': {'name': '#sec', 'objective': 'sr'}, 'color': 'white'},
                   {'text': '   ✔ ', 'color': 'green'}, {'score': {'name': f'#t{n}_cnt', 'objective': 'sr'}, 'color': 'green'},
                   {'text': f'/{NT}', 'color': 'green'}])
    lines = [
        f'execute if score #sec sr matches 10.. run bossbar set {NS}:t{n} name {bar(False)}',
        f'execute if score #sec sr matches ..9 run bossbar set {NS}:t{n} name {bar(True)}',
        f'bossbar set {NS}:t{n} players {sel}',
    ]
    for key, label in TASKS:
        lines.append(f'execute if score #t{n}_{key} sr_done matches 0 if function {NS}:cond/t{n}_{key} run function {NS}:done/t{n}_{key}')
    fn(f'team/second_t{n}', lines)

    # conditions
    def count(item):
        return ['scoreboard players set #c sr 0',
                f'execute as {sel} store result score @s sr_tmp run clear @s {item} 0',
                f'execute as {sel} run scoreboard players operation #c sr += @s sr_tmp']
    def sumc(terms, need):
        out = ['scoreboard players set #sum sr 0']
        for item, mult in terms:
            out += count(item) + ['scoreboard players operation #sum sr += #c sr'] * mult
        return out + [f'execute if score #sum sr matches {need}.. run return 1', 'return 0']
    def adv(a):
        return [f'execute if entity @a[tag=sr_run,team=sr_t{n},advancements={{{a}=true}}] run return 1', 'return 0']
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
        'blaze': sumc([('minecraft:blaze_rod', 2), ('minecraft:blaze_powder', 1), ('minecraft:ender_eye', 1)], 14),
        'pearls': sumc([('minecraft:ender_pearl', 1), ('minecraft:ender_eye', 1)], 12),
        'beds': sumc([('#minecraft:beds', 1)], 7),
        'eyes': sumc([('minecraft:ender_eye', 1)], 12),
        'stronghold': adv('minecraft:story/follow_ender_eye'),
        'end': dim('minecraft:the_end', 'minecraft:story/enter_the_end'),
        'dragon': adv('minecraft:end/kill_dragon'),
    }
    for key, label in TASKS:
        fn(f'cond/t{n}_{key}', C[key])
        d = [f'scoreboard players set #t{n}_{key} sr_done 1', f'scoreboard players add #t{n}_cnt sr 1',
             f'execute store result bossbar {NS}:t{n} value run scoreboard players get #t{n}_cnt sr',
             f'scoreboard players display name {key} sr_s{n} {tc({"text": "✔ " + label, "color": "green"})}',
             f'tellraw {sel} {tc([{"text": "✔ ", "color": "green", "bold": True}, {"text": label, "color": "white"}])}',
             f'execute as {sel} at @s run playsound minecraft:entity.player.levelup master @s ~ ~ ~ 0.5 1.6',
             f'execute if score #teams sr matches 2.. run tellraw @a[team=!sr_t{n}] {tc([{"text": "[" + cname + "] ", "color": color, "bold": True}, {"text": label, "color": "gray"}])}']
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
    gone.append(f'execute if score #wn sr matches 0 if entity @a[tag=sr_run,team=sr_t{n},advancements={{minecraft:end/kill_dragon=true}}] run scoreboard players set #wn sr {n}')
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
    sel = f'@a[tag=sr_run,team=sr_t{n}]'
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

# ------------------------------------------------------------------ lobby sidebar
lob = ['scoreboard players reset * sr_lobby']
rows = [
    ('a1', {'text': ' '}),
    ('a2', [{'text': 'Hotbar-Items: ', 'color': 'gray'}, {'text': 'Rechtsklick', 'color': 'yellow'}]),
    ('a3', [{'text': '1 ', 'color': 'dark_gray'}, {'text': 'Run starten', 'color': 'green'}]),
    ('a4', [{'text': '2 ', 'color': 'dark_gray'}, {'text': 'Modus wechseln', 'color': 'yellow'}]),
    ('a5', [{'text': '3 ', 'color': 'dark_gray'}, {'text': 'Wunschrolle', 'color': 'gold'}]),
    ('a6', [{'text': '5 ', 'color': 'dark_gray'}, {'text': 'Zuschauen', 'color': 'aqua'}]),
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
