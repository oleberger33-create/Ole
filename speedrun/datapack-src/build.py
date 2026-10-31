#!/usr/bin/env python3
"""Generates the Speedrun datapack (Minecraft 26.3, data pack format 121).
Run: python3 build.py <out_dir>   -> writes <out_dir>/speedrun/ and speedrun.zip
"""
import json, math, os, shutil, sys, zipfile

OUT = sys.argv[1] if len(sys.argv) > 1 else 'out'
ROOT = os.path.join(OUT, 'speedrun')
NS = 'sr'
files = {}

def fn(path, lines):
    files[f'data/{NS}/function/{path}.mcfunction'] = '\n'.join(lines) + '\n'

def js(path, obj):
    files[path] = json.dumps(obj, ensure_ascii=False, indent=2) + '\n'

def tc(obj):
    """text component -> SNBT-compatible JSON string for commands"""
    return json.dumps(obj, ensure_ascii=False)

# ---------------------------------------------------------------- config
LOBBY_Y = 199            # grass layer, players stand on 200
ROLES = [
    # id, team, color, sidebar title, name, role, button x, block
    (1, 'sr_ole',   'gold',         'Ole · Kämpfer',          'Ole',   'Kämpfer',        -4, 'orange_concrete'),
    (2, 'sr_mats',  'light_purple', 'Mats · Portal & Perlen', 'Mats',  'Portal & Perlen', 0, 'purple_concrete'),
    (3, 'sr_sammy', 'green',        'Sammy · Versorger',      'Sammy', 'Versorger',        4, 'green_concrete'),
]
# task key -> label (shown in chat when done)
TASKS = {
    'gear':       'Schild + Eisenschwert',
    'tools':      'Eimer + Feuerzeug',
    'beds':       '7 Betten',
    'food':       '30 Essen',
    'nether':     'Nether betreten',
    'fortress':   'Festung gefunden',
    'bastion':    'Bastion gefunden',
    'boots':      'Goldene Stiefel an',
    'blaze':      '7+ Blaze-Ruten',
    'pearls':     '12+ Enderperlen',
    'eyes':       '12 Enderaugen',
    'bow':        'Bogen + 16 Pfeile',
    'stronghold': 'Stronghold gefunden',
    'end':        'End betreten',
    'dragon':     'Drache besiegt',
}
# sidebar lists per role (top -> bottom)
LISTS = {
    'sr_ole':   ['gear', 'nether', 'fortress', 'blaze', 'stronghold', 'end', 'dragon'],
    'sr_mats':  ['tools', 'nether', 'boots', 'bastion', 'pearls', 'bow', 'dragon'],
    'sr_sammy': ['beds', 'food', 'nether', 'eyes', 'stronghold', 'end', 'dragon'],
}
FOOD = ['cooked_beef', 'cooked_porkchop', 'cooked_mutton', 'cooked_chicken', 'cooked_rabbit',
        'cooked_cod', 'cooked_salmon', 'bread', 'baked_potato', 'golden_carrot']

# run locations: well-separated, inside the stronghold rings (<~20k)
def positions(n=60, rmin=2500, rmax=20000, sep=3200, seed=7):
    import random
    rnd, pts = random.Random(seed), []
    for _ in range(200000):
        if len(pts) >= n: break
        r = math.sqrt(rnd.uniform(rmin * rmin, rmax * rmax)); a = rnd.uniform(0, 2 * math.pi)
        x, z = int(r * math.cos(a)) // 16 * 16 + 8, int(r * math.sin(a)) // 16 * 16 + 8
        if all((x - px) ** 2 + (z - pz) ** 2 >= sep * sep for px, pz in pts):
            pts.append((x, z))
    return pts
POS = positions()

# ---------------------------------------------------------------- tags / meta
js('pack.mcmeta', {'pack': {'description': 'Speedrun-Lobby, Rollen, Aufgaben & Timer (Ole, Mats, Sammy)',
                            'min_format': 121, 'max_format': [121, 999]}})
js('data/minecraft/tags/function/load.json', {'values': [f'{NS}:load']})
js('data/minecraft/tags/function/tick.json', {'values': [f'{NS}:tick']})
js('data/minecraft/tags/dialog/pause_screen_additions.json', {'values': [f'{NS}:menu']})
js('data/minecraft/tags/dialog/quick_actions.json', {'values': [f'{NS}:menu']})

def btn(label, tooltip, cmd, width=300):
    return {'label': label, 'tooltip': tooltip, 'width': width,
            'action': {'type': 'run_command', 'command': cmd}}
js(f'data/{NS}/dialog/menu.json', {
    'type': 'minecraft:multi_action',
    'title': {'text': 'Speedrun', 'bold': True},
    'external_title': {'text': 'Speedrun-Menü'},
    'body': {'type': 'minecraft:plain_message', 'width': 300,
             'contents': {'text': 'Wähle deine Rolle und starte einen neuen Run. Deine Aufgaben stehen rechts in der Seitenleiste.'}},
    'columns': 1,
    'actions': [
        btn({'text': 'Rolle: Ole · Kämpfer', 'color': 'gold'}, 'Blaze-Ruten, Kristalle, Drache sprengen', 'trigger sr_rolle set 1'),
        btn({'text': 'Rolle: Mats · Portal & Perlen', 'color': 'light_purple'}, 'Portal, Piglin-Tausch, Kristalle abschießen', 'trigger sr_rolle set 2'),
        btn({'text': 'Rolle: Sammy · Versorger', 'color': 'green'}, 'Betten, Essen, Enderaugen, Stronghold', 'trigger sr_rolle set 3'),
        btn({'text': 'Neuen Run starten'}, 'Alle mit Rolle starten an einem frischen Ort', 'trigger sr_aktion set 1'),
        btn({'text': 'Laufendem Run beitreten'}, 'Zu deinem Team teleportieren', 'trigger sr_aktion set 4'),
        btn({'text': 'Zurück zur Lobby'}, 'Verlässt den Run, leert dein Inventar', 'trigger sr_aktion set 2'),
    ],
    'exit_action': {'label': {'text': 'Schließen'}, 'width': 200},
})

# ---------------------------------------------------------------- load
load = [
    'scoreboard objectives add sr dummy',
    'scoreboard objectives add sr_tmp dummy',
    'scoreboard objectives add sr_done dummy',
    'scoreboard objectives add sr_rolle trigger',
    'scoreboard objectives add sr_aktion trigger',
    'scoreboard objectives add sr_leave minecraft.custom:minecraft.leave_game',
    'scoreboard objectives add sr_endt dummy',
    f'scoreboard objectives add sr_lobby dummy {tc({"text": "Speedrun-Lobby", "bold": True})}',
]
for _, team, color, title, *_ in ROLES:
    load += [
        f'scoreboard objectives add {team} dummy {tc({"text": title, "color": color, "bold": True})}',
        f'scoreboard objectives modify {team} numberformat blank',
        f'team add {team}',
        f'team modify {team} color {color}',
        f'team modify {team} friendlyFire false',
        f'scoreboard objectives setdisplay sidebar.team.{color} {team}',
    ]
load += [
    'scoreboard objectives setdisplay sidebar sr_lobby',
    'scoreboard players set #20 sr 20',
    'scoreboard players set #60 sr 60',
    f'scoreboard players set #npos sr {len(POS)}',
    'execute unless score #run sr matches 0.. run scoreboard players set #run sr 0',
    'execute unless score #active sr matches 0.. run scoreboard players set #active sr 0',
    'execute unless score #best sr matches 0.. run scoreboard players set #best sr 0',
    f'bossbar add {NS}:timer {tc({"text": "Speedrun"})}',
    f'bossbar set {NS}:timer color yellow',
    f'bossbar set {NS}:timer style notched_10',
    f'bossbar set {NS}:timer max {len(TASKS)}',
    'gamerule respawn_radius 0',
    'gamerule pvp false',
    'gamerule spawn_phantoms false',
    'setworldspawn 0 200 0',
    'execute in minecraft:overworld run forceload add -16 -16 15 15',
    f'function {NS}:sidebar/lobby',
    f'execute unless score #sidebar sr matches 1 run function {NS}:tasks/reset',
    f'execute unless score #built sr matches 1 run schedule function {NS}:lobby/try_build 40t',
]
fn('load', load)

# ---------------------------------------------------------------- tick
fn('tick', [
    'scoreboard players enable @a sr_rolle',
    'scoreboard players enable @a sr_aktion',
    f'execute as @a[tag=!sr_seen] run function {NS}:player/first_join',
    f'execute as @a[scores={{sr_leave=1..}}] run function {NS}:player/rejoin',
    f'execute as @a[scores={{sr_rolle=1..}}] run function {NS}:role/pick',
    f'execute as @a[scores={{sr_aktion=1..}}] run function {NS}:player/action',
    f'execute if score #built sr matches 1 run function {NS}:lobby/inputs',
    f'execute as @a[tag=sr_lobby] run function {NS}:lobby/keep',
    f'execute if score #active sr matches 1 run function {NS}:run/tick',
])

# ---------------------------------------------------------------- lobby build
def disk(y, r, block):
    out = []
    for z in range(-r, r + 1):
        w = int(math.floor(math.sqrt(r * r + r - z * z)))
        out.append(f'fill {-w} {y} {z} {w} {y} {z} minecraft:{block}')
    return out

build = [f'execute in minecraft:overworld run {c}' for c in (
    ['fill -14 192 -14 14 210 14 minecraft:air']
    + disk(LOBBY_Y, 10, 'grass_block')
    + disk(LOBBY_Y - 1, 9, 'dirt')
    + disk(LOBBY_Y - 2, 8, 'dirt')
    + disk(LOBBY_Y - 3, 6, 'stone')
    + disk(LOBBY_Y - 4, 4, 'stone')
    + disk(LOBBY_Y - 5, 2, 'cobblestone')
    + ['setblock 0 194 0 minecraft:cobblestone']
)]
def sign(x, y, z, rot, lines, color):
    msgs = [{'text': lines[0], 'color': color, 'bold': True}] + [{'text': l} for l in lines[1:]]
    while len(msgs) < 4: msgs.append({'text': ''})
    nbt = '{front_text:{has_glowing_text:true,messages:[' + ','.join(json.dumps(m, ensure_ascii=False) for m in msgs) + ']}}'
    return f'execute in minecraft:overworld run setblock {x} {y} {z} minecraft:dark_oak_sign[rotation={rot}]{nbt}'
for rid, team, color, title, name, role, bx, block in ROLES:
    build += [
        f'execute in minecraft:overworld run setblock {bx} 200 -4 minecraft:{block}',
        f'execute in minecraft:overworld run setblock {bx} 200 -3 minecraft:stone_button[face=wall,facing=south]',
        sign(bx, 201, -4, 0, [name, role, 'Knopf drücken'], color),
    ]
build += [
    'execute in minecraft:overworld run setblock 0 200 5 minecraft:gold_block',
    'execute in minecraft:overworld run setblock 0 200 4 minecraft:lever[face=wall,facing=north,powered=false]',
    sign(0, 201, 5, 8, ['Neuer Run', 'Hebel ziehen', 'Alle mit Rolle', 'starten'], 'yellow'),
]
for x, z in [(-7, -7), (7, -7), (-7, 7), (7, 7)]:
    build += [f'execute in minecraft:overworld run setblock {x} 200 {z} minecraft:oak_fence',
              f'execute in minecraft:overworld run setblock {x} 201 {z} minecraft:lantern']
for x, z in [(-6, 2), (6, 2), (-2, 7), (3, -7)]:
    build += [f'execute in minecraft:overworld run setblock {x} 200 {z} minecraft:potted_poppy']
build += [
    'scoreboard players set #built sr 1',
    'scoreboard players set #lever sr 0',
    'scoreboard players set #b1 sr 0', 'scoreboard players set #b2 sr 0', 'scoreboard players set #b3 sr 0',
    f'tellraw @a {tc({"text": "[Speedrun] Lobby-Insel gebaut.", "color": "gray"})}',
]
fn('lobby/build', build)
fn('lobby/try_build', [
    f'execute in minecraft:overworld if loaded 0 {LOBBY_Y} 0 if loaded 10 {LOBBY_Y} 10 if loaded -10 {LOBBY_Y} -10 run return run function {NS}:lobby/build',
    f'schedule function {NS}:lobby/try_build 20t',
])

# button / lever edge detection
inputs = []
for rid, team, color, title, name, role, bx, block in ROLES:
    b = f'#b{rid}'
    inputs += [
        f'execute in minecraft:overworld if block {bx} 200 -3 minecraft:stone_button[powered=true] if score {b} sr matches 0 positioned {bx} 200 -2 as @p[distance=..6] run scoreboard players set @s sr_rolle {rid}',
        f'execute in minecraft:overworld if block {bx} 200 -3 minecraft:stone_button[powered=true] run scoreboard players set {b} sr 1',
        f'execute in minecraft:overworld if block {bx} 200 -3 minecraft:stone_button[powered=false] run scoreboard players set {b} sr 0',
    ]
inputs += [
    f'execute in minecraft:overworld if block 0 200 4 minecraft:lever[powered=true] run function {NS}:lobby/lever',
]
fn('lobby/inputs', inputs)
fn('lobby/lever', [
    'execute in minecraft:overworld run setblock 0 200 4 minecraft:lever[face=wall,facing=north,powered=false]',
    'execute in minecraft:overworld positioned 0 200 3 as @p[distance=..8] run tag @s add sr_starter',
    f'function {NS}:run/start',
    'tag @a remove sr_starter',
])
fn('lobby/keep', [
    'effect give @s minecraft:resistance infinite 4 true',
    'effect give @s minecraft:saturation infinite 0 true',
    'execute unless entity @s[gamemode=adventure] unless entity @s[gamemode=creative] unless entity @s[gamemode=spectator] run gamemode adventure @s',
    f'execute at @s unless dimension minecraft:overworld run function {NS}:player/tp_lobby',
    f'execute at @s if dimension minecraft:overworld unless entity @s[y=185,dy=200] run function {NS}:player/tp_lobby',
    f'execute at @s if dimension minecraft:overworld unless entity @s[x=-40,dx=80,z=-40,dz=80] run function {NS}:player/tp_lobby',
])

# ---------------------------------------------------------------- player
fn('player/tp_lobby', ['execute in minecraft:overworld run tp @s 0 200 0 180 0'])
fn('player/to_lobby', [
    'tag @s remove sr_run',
    'tag @s add sr_lobby',
    f'function {NS}:player/reset_state',
    'gamemode adventure @s',
    f'function {NS}:player/tp_lobby',
    'execute in minecraft:overworld run spawnpoint @s 0 200 0',
    f'bossbar set {NS}:timer players @a[tag=sr_run]',
])
enderchest = [f'item replace entity @s enderchest.{i} with minecraft:air' for i in range(27)]
fn('player/reset_state', [
    'clear @s',
    *enderchest,
    'effect clear @s',
    'experience set @s 0 levels',
    'experience set @s 0 points',
    'effect give @s minecraft:instant_health 1 10 true',
    'effect give @s minecraft:saturation 1 20 true',
    'advancement revoke @s everything',
])
welcome = [
    {'text': '\n[Speedrun] ', 'color': 'yellow', 'bold': True},
    {'text': 'Willkommen auf der Lobby-Insel!\n', 'color': 'white', 'bold': False},
    {'text': 'Rolle wählen: ', 'color': 'gray', 'bold': False},
    {'text': '[Ole · Kämpfer]', 'color': 'gold', 'bold': False, 'click_event': {'action': 'run_command', 'command': '/trigger sr_rolle set 1'}, 'hover_event': {'action': 'show_text', 'value': 'Blaze-Ruten, Kristalle, Drache sprengen'}},
    {'text': ' ', 'bold': False},
    {'text': '[Mats · Portal & Perlen]', 'color': 'light_purple', 'bold': False, 'click_event': {'action': 'run_command', 'command': '/trigger sr_rolle set 2'}, 'hover_event': {'action': 'show_text', 'value': 'Portal, Piglin-Tausch, Kristalle abschießen'}},
    {'text': ' ', 'bold': False},
    {'text': '[Sammy · Versorger]', 'color': 'green', 'bold': False, 'click_event': {'action': 'run_command', 'command': '/trigger sr_rolle set 3'}, 'hover_event': {'action': 'show_text', 'value': 'Betten, Essen, Enderaugen, Stronghold'}},
    {'text': '\nNeuer Run: Hebel hinter dir ziehen oder ', 'color': 'gray', 'bold': False},
    {'text': '[Run starten]', 'color': 'yellow', 'bold': False, 'click_event': {'action': 'run_command', 'command': '/trigger sr_aktion set 1'}},
    {'text': '\nMenü jederzeit: Esc → „Speedrun-Menü“ oder ', 'color': 'gray', 'bold': False},
    {'text': '[Menü öffnen]', 'color': 'aqua', 'bold': False, 'click_event': {'action': 'run_command', 'command': '/trigger sr_aktion set 3'}},
]
fn('player/first_join', [
    'tag @s add sr_seen',
    'scoreboard players set @s sr_leave 0',
    f'function {NS}:player/to_lobby',
    f'tellraw @s {tc(welcome)}',
])
fn('player/rejoin', [
    'scoreboard players set @s sr_leave 0',
    f'execute unless entity @s[tag=sr_run] run function {NS}:player/to_lobby',
    f'execute if entity @s[tag=sr_run] if score #active sr matches 0 run tellraw @s {tc([{"text": "[Speedrun] ", "color": "yellow"}, {"text": "Kein Run aktiv. ", "color": "gray"}, {"text": "[Zurück zur Lobby]", "color": "aqua", "click_event": {"action": "run_command", "command": "/trigger sr_aktion set 2"}}])}',
    f'execute unless entity @s[tag=sr_run] run tellraw @s {tc(welcome)}',
])
fn('player/action', [
    f'execute if score @s sr_aktion matches 1 run function {NS}:run/start_by_player',
    f'execute if score @s sr_aktion matches 2 run function {NS}:player/to_lobby',
    f'execute if score @s sr_aktion matches 3 run dialog show @s {NS}:menu',
    f'execute if score @s sr_aktion matches 4 run function {NS}:run/join',
    'scoreboard players set @s sr_aktion 0',
])

# ---------------------------------------------------------------- roles
pick = []
for rid, team, color, title, name, role, *_ in ROLES:
    pick += [
        f'execute if score @s sr_rolle matches {rid} run team join {team} @s',
        f'execute if score @s sr_rolle matches {rid} run tellraw @a {tc([{"text": "[Speedrun] ", "color": "yellow"}, {"selector": "@s"}, {"text": " spielt jetzt ", "color": "gray"}, {"text": f"{name} · {role}", "color": color}])}',
        f'execute if score @s sr_rolle matches {rid} run title @s actionbar {tc({"text": f"Rolle: {name} · {role}", "color": color})}',
    ]
pick += ['playsound minecraft:block.note_block.pling master @s ~ ~ ~ 1 1.4', 'scoreboard players set @s sr_rolle 0']
fn('role/pick', pick)

# ---------------------------------------------------------------- run
fn('run/start_by_player', [
    'tag @s add sr_starter',
    f'function {NS}:run/start',
    'tag @a remove sr_starter',
])
role_sel = '@a[team=!]'
fn('run/start', [
    f'execute unless entity {role_sel} run return run tellraw @a[tag=sr_starter] {tc([{"text": "[Speedrun] ", "color": "yellow"}, {"text": "Erst eine Rolle wählen (Knöpfe auf der Insel oder Esc → Speedrun-Menü).", "color": "red"}])}',
    'scoreboard players add #run sr 1',
    'scoreboard players operation #slot sr = #run sr',
    'scoreboard players remove #slot sr 1',
    'scoreboard players operation #slot sr %= #npos sr',
    f'function {NS}:run/pick_pos',
    'execute store result storage sr:run x int 1 run scoreboard players get #cx sr',
    'execute store result storage sr:run z int 1 run scoreboard players get #cz sr',
    f'tag {role_sel} add sr_run',
    f'tag {role_sel} remove sr_lobby',
    f'execute as @a[tag=sr_run] run function {NS}:player/reset_state',
    'gamemode survival @a[tag=sr_run]',
    'time set 0',
    'weather clear',
    'difficulty normal',
    f'function {NS}:tasks/reset',
    'scoreboard players set #crystals sr 0',
    'scoreboard players set @a sr_endt 0',
    'execute in minecraft:overworld run tp @a[tag=sr_run] 0 200 0',
    'scoreboard players set #try sr 0',
    f'function {NS}:run/place with storage sr:run',
    'execute as @a[tag=sr_run] at @s run spawnpoint @s ~ ~ ~',
    'scoreboard players set #ticks sr 0',
    'scoreboard players set #active sr 1',
    f'bossbar set {NS}:timer value 0',
    f'bossbar set {NS}:timer players @a[tag=sr_run]',
    f'bossbar set {NS}:timer visible true',
    f'title @a[tag=sr_run] title {tc([{"text": "Run #", "color": "yellow"}, {"score": {"name": "#run", "objective": "sr"}, "color": "yellow"}])}',
    f'title @a[tag=sr_run] subtitle {tc({"text": "Los geht’s! Aufgaben stehen rechts.", "color": "white"})}',
    'execute as @a[tag=sr_run] at @s run playsound minecraft:entity.ender_dragon.growl master @s ~ ~ ~ 0.6 1.2',
    f'tellraw @a {tc([{"text": "[Speedrun] ", "color": "yellow"}, {"text": "Run #", "color": "white"}, {"score": {"name": "#run", "objective": "sr"}, "color": "white"}, {"text": " gestartet bei ", "color": "gray"}, {"nbt": "x", "storage": "sr:run", "color": "white"}, {"text": " / ", "color": "gray"}, {"nbt": "z", "storage": "sr:run", "color": "white"}])}',
])
pp = []
for i, (x, z) in enumerate(POS):
    pp.append(f'execute if score #slot sr matches {i} run return run function {NS}:run/set_pos {{x:{x},z:{z}}}')
fn('run/pick_pos', pp)
fn('run/set_pos', ['$scoreboard players set #cx sr $(x)', '$scoreboard players set #cz sr $(z)'])
# spreadplayers with fallback: bigger radius, then next slot
fn('run/place', [
    '$execute in minecraft:overworld store success score #ok sr run spreadplayers $(x) $(z) 2 24 false @a[tag=sr_run]',
    '$execute if score #ok sr matches 0 in minecraft:overworld store success score #ok sr run spreadplayers $(x) $(z) 2 96 false @a[tag=sr_run]',
    '$execute if score #ok sr matches 0 in minecraft:overworld store success score #ok sr run spreadplayers $(x) $(z) 2 320 false @a[tag=sr_run]',
    f'execute if score #ok sr matches 0 run function {NS}:run/next_slot',
])
fn('run/next_slot', [
    'scoreboard players add #try sr 1',
    'execute if score #try sr matches 6.. run return run tellraw @a {"text":"[Speedrun] Konnte keinen Startplatz finden.","color":"red"}',
    'scoreboard players add #slot sr 1',
    'scoreboard players operation #slot sr %= #npos sr',
    f'function {NS}:run/pick_pos',
    'execute store result storage sr:run x int 1 run scoreboard players get #cx sr',
    'execute store result storage sr:run z int 1 run scoreboard players get #cz sr',
    f'function {NS}:run/place with storage sr:run',
])
fn('run/join', [
    f'execute if score #active sr matches 0 run return run tellraw @s {tc([{"text": "[Speedrun] ", "color": "yellow"}, {"text": "Gerade läuft kein Run.", "color": "red"}])}',
    f'execute unless entity @s[team=!] run return run tellraw @s {tc([{"text": "[Speedrun] ", "color": "yellow"}, {"text": "Erst eine Rolle wählen.", "color": "red"}])}',
    f'execute if entity @s[tag=sr_run] run return run tellraw @s {tc([{"text": "[Speedrun] ", "color": "yellow"}, {"text": "Du bist schon im Run.", "color": "gray"}])}',
    f'execute unless entity @a[tag=sr_run] run return run tellraw @s {tc([{"text": "[Speedrun] ", "color": "yellow"}, {"text": "Niemand ist gerade im Run.", "color": "red"}])}',
    f'function {NS}:player/reset_state',
    'tag @s remove sr_lobby',
    'tag @s add sr_run',
    'gamemode survival @s',
    'tp @s @r[tag=sr_run,distance=0..,limit=1,tag=!sr_lobby]',
    'execute at @s run spawnpoint @s ~ ~ ~',
    f'bossbar set {NS}:timer players @a[tag=sr_run]',
])
fn('run/tick', [
    'scoreboard players add #ticks sr 1',
    'scoreboard players operation #t sr = #ticks sr',
    'scoreboard players operation #t sr %= #20 sr',
    f'execute if score #t sr matches 0 run function {NS}:run/second',
])
timer_name = lambda zero: [
    {'text': 'Run #', 'color': 'yellow'}, {'score': {'name': '#run', 'objective': 'sr'}, 'color': 'yellow'},
    {'text': '   ⏱ ', 'color': 'white'}, {'score': {'name': '#min', 'objective': 'sr'}, 'color': 'white'},
    {'text': ':0' if zero else ':', 'color': 'white'}, {'score': {'name': '#sec', 'objective': 'sr'}, 'color': 'white'},
    {'text': '   ✔ ', 'color': 'green'}, {'score': {'name': '#donecount', 'objective': 'sr'}, 'color': 'green'},
    {'text': f'/{len(TASKS)}', 'color': 'green'}]
fn('run/second', [
    'scoreboard players operation #s sr = #ticks sr',
    'scoreboard players operation #s sr /= #20 sr',
    'scoreboard players operation #min sr = #s sr',
    'scoreboard players operation #min sr /= #60 sr',
    'scoreboard players operation #sec sr = #s sr',
    'scoreboard players operation #sec sr %= #60 sr',
    f'execute if score #sec sr matches 10.. run bossbar set {NS}:timer name {tc(timer_name(False))}',
    f'execute if score #sec sr matches ..9 run bossbar set {NS}:timer name {tc(timer_name(True))}',
    f'bossbar set {NS}:timer players @a[tag=sr_run]',
    f'function {NS}:tasks/check',
    f'function {NS}:run/end_crystals',
])
# dragon already dead from an earlier run -> hand out 4 end crystals once
fn('run/end_crystals', [
    'execute as @a[tag=sr_run] at @s if dimension minecraft:the_end run scoreboard players add @s sr_endt 1',
    'execute if score #crystals sr matches 1 run return 0',
    'execute unless entity @a[tag=sr_run,scores={sr_endt=6..}] run return 0',
    'execute in minecraft:the_end if entity @e[type=minecraft:ender_dragon] run return run scoreboard players set #crystals sr 1',
    'scoreboard players set #crystals sr 1',
    'give @r[tag=sr_run,scores={sr_endt=6..}] minecraft:end_crystal 4',
    f'tellraw @a[tag=sr_run] {tc([{"text": "[Speedrun] ", "color": "yellow"}, {"text": "Der Drache ist aus einem alten Run schon tot. Setzt die 4 Endkristalle auf die 4 Seiten des Ausgangsportals in der Mitte, dann kommt er zurück.", "color": "light_purple"}])}',
])
fn('run/finish', [
    'scoreboard players set #active sr 0',
    'scoreboard players operation #fmin sr = #min sr',
    'scoreboard players operation #fsec sr = #sec sr',
    'execute if score #best sr matches 0 run scoreboard players operation #best sr = #ticks sr',
    'execute if score #ticks sr < #best sr run scoreboard players operation #best sr = #ticks sr',
    'scoreboard players operation #last sr = #ticks sr',
    f'function {NS}:sidebar/lobby',
    f'title @a[tag=sr_run] title {tc({"text": "Drache besiegt!", "color": "gold"})}',
    f'execute if score #sec sr matches 10.. run title @a[tag=sr_run] subtitle {tc([{"text": "Zeit ", "color": "white"}, {"score": {"name": "#min", "objective": "sr"}}, {"text": ":"}, {"score": {"name": "#sec", "objective": "sr"}}])}',
    f'execute if score #sec sr matches ..9 run title @a[tag=sr_run] subtitle {tc([{"text": "Zeit ", "color": "white"}, {"score": {"name": "#min", "objective": "sr"}}, {"text": ":0"}, {"score": {"name": "#sec", "objective": "sr"}}])}',
    'execute as @a[tag=sr_run] at @s run playsound minecraft:ui.toast.challenge_complete master @s ~ ~ ~ 1 1',
    f'tellraw @a {tc([{"text": "[Speedrun] ", "color": "yellow"}, {"text": "Run #", "color": "gold"}, {"score": {"name": "#run", "objective": "sr"}, "color": "gold"}, {"text": " geschafft! ", "color": "gold"}, {"text": "[Zurück zur Lobby]", "color": "aqua", "click_event": {"action": "run_command", "command": "/trigger sr_aktion set 2"}}])}',
])

# ---------------------------------------------------------------- tasks
def count(item, sel='@a[tag=sr_run]'):
    return [f'scoreboard players set #c sr 0',
            f'execute as {sel} store result score @s sr_tmp run clear @s {item} 0',
            f'execute as {sel} run scoreboard players operation #c sr += @s sr_tmp']
def cond_count(key, terms, need, sel='@a[tag=sr_run]'):
    lines = ['scoreboard players set #sum sr 0']
    for item, mult in terms:
        lines += count(item, sel)
        for _ in range(mult):
            lines.append('scoreboard players operation #sum sr += #c sr')
    lines += [f'execute if score #sum sr matches {need}.. run return 1', 'return 0']
    fn(f'cond/{key}', lines)
def cond_adv(key, adv):
    fn(f'cond/{key}', [f'execute if entity @a[tag=sr_run,advancements={{{adv}=true}}] run return 1', 'return 0'])

# gear: Ole has shield + iron/diamond/netherite sword
fn('cond/gear', [
    *count('minecraft:shield', '@a[tag=sr_run,team=sr_ole]'),
    'execute if score #c sr matches 0 run return 0',
    'scoreboard players set #sum sr 0',
    *count('minecraft:iron_sword', '@a[tag=sr_run,team=sr_ole]'), 'scoreboard players operation #sum sr += #c sr',
    *count('minecraft:diamond_sword', '@a[tag=sr_run,team=sr_ole]'), 'scoreboard players operation #sum sr += #c sr',
    *count('minecraft:netherite_sword', '@a[tag=sr_run,team=sr_ole]'), 'scoreboard players operation #sum sr += #c sr',
    'execute if score #sum sr matches 1.. run return 1', 'return 0'])
fn('cond/tools', [
    *count('minecraft:flint_and_steel', '@a[tag=sr_run,team=sr_mats]'),
    'execute if score #c sr matches 0 run return 0',
    'scoreboard players set #sum sr 0',
    *count('minecraft:bucket', '@a[tag=sr_run,team=sr_mats]'), 'scoreboard players operation #sum sr += #c sr',
    *count('minecraft:water_bucket', '@a[tag=sr_run,team=sr_mats]'), 'scoreboard players operation #sum sr += #c sr',
    *count('minecraft:lava_bucket', '@a[tag=sr_run,team=sr_mats]'), 'scoreboard players operation #sum sr += #c sr',
    'execute if score #sum sr matches 1.. run return 1', 'return 0'])
cond_count('beds', [('#minecraft:beds', 1)], 7)
cond_count('food', [(f'minecraft:{f}', 1) for f in FOOD], 30)
fn('cond/nether', ['execute as @a[tag=sr_run] at @s if dimension minecraft:the_nether run return 1',
                   'execute if entity @a[tag=sr_run,advancements={minecraft:story/enter_the_nether=true}] run return 1', 'return 0'])
cond_adv('fortress', 'minecraft:nether/find_fortress')
cond_adv('bastion', 'minecraft:nether/find_bastion')
fn('cond/boots', ['execute as @a[tag=sr_run,team=sr_mats] if items entity @s armor.feet minecraft:golden_boots run return 1', 'return 0'])
cond_count('blaze', [('minecraft:blaze_rod', 2), ('minecraft:blaze_powder', 1), ('minecraft:ender_eye', 1)], 14)
cond_count('pearls', [('minecraft:ender_pearl', 1), ('minecraft:ender_eye', 1)], 12)
cond_count('eyes', [('minecraft:ender_eye', 1)], 12)
fn('cond/bow', [
    *count('minecraft:bow', '@a[tag=sr_run,team=sr_mats]'),
    'execute if score #c sr matches 0 run return 0',
    *count('minecraft:arrow', '@a[tag=sr_run,team=sr_mats]'),
    'execute if score #c sr matches 16.. run return 1', 'return 0'])
cond_adv('stronghold', 'minecraft:story/follow_ender_eye')
fn('cond/end', ['execute as @a[tag=sr_run] at @s if dimension minecraft:the_end run return 1',
                'execute if entity @a[tag=sr_run,advancements={minecraft:story/enter_the_end=true}] run return 1', 'return 0'])
cond_adv('dragon', 'minecraft:end/kill_dragon')

def entry(team, i):
    return f'{team[3:]}{i}'
def line(label, done):
    return tc({'text': ('✔ ' if done else '☐ ') + label, 'color': 'green' if done else 'gray', 'strikethrough': False})

check = []
for key, label in TASKS.items():
    check.append(f'execute if score #{key} sr_done matches 0 if function {NS}:cond/{key} run function {NS}:done/{key}')
    d = [f'scoreboard players set #{key} sr_done 1', 'scoreboard players add #donecount sr 1',
         f'execute store result bossbar {NS}:timer value run scoreboard players get #donecount sr']
    for team, keys in LISTS.items():
        for i, k in enumerate(keys):
            if k == key:
                d.append(f'scoreboard players display name {entry(team, i)} {team} {line(label, True)}')
    d += [f'tellraw @a[tag=sr_run] {tc([{"text": "✔ ", "color": "green"}, {"text": label, "color": "white"}])}',
          'execute as @a[tag=sr_run] at @s run playsound minecraft:entity.player.levelup master @s ~ ~ ~ 0.6 1.6']
    if key == 'dragon':
        d.append(f'function {NS}:run/finish')
    fn(f'done/{key}', d)
fn('tasks/check', check)

reset = ['scoreboard players set #donecount sr 0', 'scoreboard players set #sidebar sr 1']
for key in TASKS:
    reset.append(f'scoreboard players set #{key} sr_done 0')
for team, keys in LISTS.items():
    reset.append(f'scoreboard players reset * {team}')
    for i, k in enumerate(keys):
        e = entry(team, i)
        reset += [f'scoreboard players set {e} {team} {len(keys) - i}',
                  f'scoreboard players display name {e} {team} {line(TASKS[k], False)}']
fn('tasks/reset', reset)

# lobby sidebar (players without role)
fn('sidebar/lobby', [
    'scoreboard players reset * sr_lobby',
    'scoreboard players operation #bestsec sr = #best sr',
    'scoreboard players operation #bestsec sr /= #20 sr',
    'scoreboard players operation #lastsec sr = #last sr',
    'scoreboard players operation #lastsec sr /= #20 sr',
    'scoreboard players set l1 sr_lobby 6', f'scoreboard players display name l1 sr_lobby {tc({"text": "Rolle wählen:", "color": "white"})}',
    'scoreboard players display numberformat l1 sr_lobby blank',
    'scoreboard players set l2 sr_lobby 5', f'scoreboard players display name l2 sr_lobby {tc({"text": " Knöpfe vorne auf der Insel", "color": "gray"})}',
    'scoreboard players display numberformat l2 sr_lobby blank',
    'scoreboard players set l3 sr_lobby 4', f'scoreboard players display name l3 sr_lobby {tc({"text": "Neuer Run: Hebel hinten", "color": "white"})}',
    'scoreboard players display numberformat l3 sr_lobby blank',
    'scoreboard players set l4 sr_lobby 3', f'scoreboard players display name l4 sr_lobby {tc({"text": "Menü: Esc → Speedrun-Menü", "color": "white"})}',
    'scoreboard players display numberformat l4 sr_lobby blank',
    'scoreboard players set l5 sr_lobby 2', f'scoreboard players display name l5 sr_lobby {tc({"text": "Bestzeit (Sek.)", "color": "gold"})}',
    'execute store result score l5 sr_lobby run scoreboard players get #bestsec sr',
    'scoreboard players set l6 sr_lobby 1', f'scoreboard players display name l6 sr_lobby {tc({"text": "Letzter Run (Sek.)", "color": "yellow"})}',
    'execute store result score l6 sr_lobby run scoreboard players get #lastsec sr',
])

# ---------------------------------------------------------------- write
if os.path.exists(ROOT): shutil.rmtree(ROOT)
for path, content in files.items():
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f: f.write(content)
zpath = os.path.join(OUT, 'speedrun.zip')
with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
    for path, content in files.items(): z.writestr(path, content)
print(f'{len(files)} files, {len(POS)} run positions -> {zpath}')
