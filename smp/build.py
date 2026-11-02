#!/usr/bin/env python3
"""OLE SMP – Server-Datapack (Minecraft 26.3, pack format 121; 26.1-Testserver: min_format 101).

Rein vanilla, laeuft komplett auf dem Server (keine Client-Mods noetig). Spieler bedienen alles ueber
/trigger-Befehle, klickbare Chat-Menues und das Pause-Menue (Esc -> "SMP-Menue", Dialog-Registry).

Run:  python3 build.py <out_dir> [min_format]   -> <out_dir>/smp/ und <out_dir>/smp.zip
Module: jede Datei in modules/*.py wird am Ende ausgefuehrt (alle Globals von hier sind verfuegbar).
        SMP_MODULES=info,spawn,tp baut nur diese Module (zum Entwickeln).
"""
import json, os, sys, zipfile

OUT = sys.argv[1] if len(sys.argv) > 1 else 'out'
MIN_FORMAT = int(sys.argv[2]) if len(sys.argv) > 2 else 121
ROOT = os.path.join(OUT, 'smp')
NS = 'smp'
SERVER_NAME = 'OLE SMP'
PACK_VERSION = 2
files = {}


def fn(path, lines):
    files[f'data/{NS}/function/{path}.mcfunction'] = '\n'.join(lines) + '\n'


def js(path, obj):
    files[path] = json.dumps(obj, ensure_ascii=False, indent=2) + '\n'


def tc(obj):
    return json.dumps(obj, ensure_ascii=False)


PREFIX = {'text': '» ', 'color': 'green', 'bold': True}
def msg(*parts):
    """chat message with the green » prefix (parts = text components; they do not inherit the prefix style)"""
    return tc([{'text': ''}, PREFIX] + list(parts))


def clk(label, cmd, color='yellow', hover=None, action='run_command'):
    """clickable text component running (or with action='suggest_command': suggesting) a command"""
    c = {'text': label, 'color': color, 'click_event': {'action': action, 'command': cmd}}
    if hover:
        c['hover_event'] = {'action': 'show_text', 'value': hover}
    return c


OW = 'execute in minecraft:overworld run'
PRED = 'type' if MIN_FORMAT >= 121 else 'condition'      # inline predicates: 26.3 uses "type", 26.1 "condition"
DIMS = [('minecraft:overworld', 'Oberwelt', 0), ('minecraft:the_nether', 'Nether', 1), ('minecraft:the_end', 'End', 2)]

# ------------------------------------------------------------------ registries (modules append to these)
EXTRA_LOAD = []      # commands run on load (after the core objectives exist)
EXTRA_TICK = []      # commands run every tick (as the server)
EXTRA_SECOND = []    # commands run every 20 ticks (as the server)
ON_JOIN = []         # run as a player on their FIRST join (after the id is assigned)
ON_REJOIN = []       # run as a player on every later join
ON_DEATH = []        # run as the dead player at their death position (before respawn)
ON_RESPAWN = []      # run as the player right after respawn
TRIGGERS = []        # (objective, handler, usage, text, category)
HELP = {}            # category -> [(usage, text)]
MENU = []            # (label text component, tooltip, command, width) buttons of the Esc dialog "SMP-Menue"
COOLDOWNS = []       # objectives decremented by 1 every second while > 0
WARMUPS = []         # (key, target function) teleport warm-ups (see warmup())
HUD_PRE = []         # commands run as+at the player inside info/hud before the actionbar line (other modules add segments)
HUD_PARTS = []       # text components appended to the info HUD actionbar line
EXTRA_FINISH = []    # callables run at the start of finish(): generate functions that depend on registries of later modules
RULES = [
    'Nicht griefen, nichts klauen – auch nicht aus fremden Kisten.',
    'Fremde Bauten und Claims respektieren (Claim-Anker schuetzen dein Gebiet).',
    'Keine Cheats, kein X-Ray, keine Dupes.',
    'Freundlich bleiben – wir spielen zusammen.',
    'Keine Lag-Maschinen (riesige Mob-Farmen, Redstone-Clocks ohne Aus-Schalter).',
]


def trigger(obj, handler, usage, text, category='Allgemein', menu=None):
    """Registers /trigger <obj>: every tick players with <obj> >= 1 run <handler> (as the player, at the player);
    the value is still in the score during the handler and is reset afterwards.
    usage/text appear in /trigger hilfe. menu=(label, tooltip) adds a button to the Esc dialog."""
    TRIGGERS.append((obj, handler, usage, text, category))
    HELP.setdefault(category, []).append((usage, text))
    if menu:
        MENU.append((menu[0], menu[1], f'trigger {obj}', 150))


def cooldown(obj):
    """objective (seconds) that counts down by itself; set it to N to start a cooldown"""
    COOLDOWNS.append(obj)
    EXTRA_LOAD.append(f'scoreboard objectives add {obj} dummy')


def warmup(key, target):
    """Teleport warm-up: run `function smp:core/warm_<key>` as the player; after #warm_s seconds without
    moving to another block, <target> runs as the player (at the player). Moving cancels it."""
    WARMUPS.append((key, target))
    fn(f'core/warm_{key}', [
        f'function {NS}:core/warm_clear',          # only ONE warm-up at a time (generated in finish() with all keys)
        f'tag @s add smp_wu_{key}',
        'scoreboard players operation @s smp_wu = #warm_t smp',
        'execute store result score @s smp_wx run data get entity @s Pos[0]',
        'execute store result score @s smp_wy run data get entity @s Pos[1]',
        'execute store result score @s smp_wz run data get entity @s Pos[2]',
        f'tellraw @s {msg({"text": "Teleport in ", "color": "gray"}, {"score": {"name": "#warm_s", "objective": "smp"}, "color": "yellow"}, {"text": " Sekunden – nicht bewegen!", "color": "gray"})}',
    ])


def player_menu(obj, title, exclude_self=True):
    """Function smp:core/list_<obj>: shows the viewer (@s) a clickable list of online players;
    a click runs /trigger <obj> set <id of that player>."""
    fn(f'core/list_{obj}', [
        'tag @s add smp_viewer',
        f'tellraw @s {msg({"text": title, "color": "white"})}',
        f'execute as @a[{"tag=!smp_viewer" if exclude_self else ""}] run function {NS}:core/listline_{obj}',
        f'execute unless entity @a[{"tag=!smp_viewer" if exclude_self else ""}] run tellraw @s {tc({"text": "   Niemand sonst ist online.", "color": "gray"})}',
        'tag @s remove smp_viewer',
    ])
    fn(f'core/listline_{obj}', ['execute store result storage smp:tmp id int 1 run scoreboard players get @s smp_id',
                                 f'function {NS}:core/listbtn_{obj} with storage smp:tmp'])
    fn(f'core/listbtn_{obj}', ['$tellraw @a[tag=smp_viewer] ' + tc([{'text': '   '}, {'text': '[', 'color': 'dark_gray'},
                                {'selector': '@s', 'color': 'yellow', 'click_event': {'action': 'run_command', 'command': f'/trigger {obj} set $(id)'},
                                 'hover_event': {'action': 'show_text', 'value': 'Anklicken'}}, {'text': ']', 'color': 'dark_gray'}])])


def dim_lines(prefix=''):
    """commands that store the dimension of @s: score @s smp_dim (0/1/2) and storage smp:tmp dim (id string)"""
    return [f'{prefix}execute if dimension {d} run scoreboard players set @s smp_dim {n}' for d, _, n in DIMS] + \
           [f'{prefix}execute if dimension {d} run data modify storage smp:tmp dim set value "{d}"' for d, _, n in DIMS]


# ------------------------------------------------------------------ meta
js('pack.mcmeta', {'pack': {'description': f'{SERVER_NAME}: Spawn, Homes, TPA, RTP, Stats, Menue', 'min_format': MIN_FORMAT, 'max_format': [121, 999]}})
js('data/minecraft/tags/function/load.json', {'values': [f'{NS}:load']})
js('data/minecraft/tags/function/tick.json', {'values': [f'{NS}:tick']})

# ------------------------------------------------------------------ core functions (generated at the end, after the modules)
fn('core/tp', ['$execute in $(dim) run tp @s $(x) $(y) $(z)'])       # with storage {x,y,z,dim}
fn('core/dim', dim_lines())
# "back" position: modules call `function smp:core/back_save` as the player BEFORE every teleport (home/spawn/tpa/rtp);
# `function smp:core/back_go` teleports the player to the saved position (storage smp:back p<id>).
fn('core/back_save', [
    'execute store result storage smp:tmp id int 1 run scoreboard players get @s smp_id',
    'data modify storage smp:tmp x set from entity @s Pos[0]',      # exact doubles (store result would floor)
    'data modify storage smp:tmp y set from entity @s Pos[1]',
    'data modify storage smp:tmp z set from entity @s Pos[2]',
    f'function {NS}:core/dim',
    f'function {NS}:core/back_put with storage smp:tmp',
])
fn('core/back_put', ['$data modify storage smp:back p$(id) set value {x:$(x),y:$(y),z:$(z),dim:"$(dim)"}', '$data modify storage smp:back p$(id).has set value 1b'])
fn('core/back_go', ['execute store result storage smp:tmp id int 1 run scoreboard players get @s smp_id',
                    f'function {NS}:core/back_go2 with storage smp:tmp'])
fn('core/back_go2', ['$execute unless data storage smp:back p$(id).has run return run tellraw @s ' + msg({'text': 'Keine letzte Position gespeichert.', 'color': 'red'}),
                     '$function smp:core/tp with storage smp:back p$(id)'])
fn('core/death', [
    'tag @s add smp_dead', 'scoreboard players set @s smp_deaths 0',
    'scoreboard players add @s smp_tode 1',          # persistent death counter (stats, leaderboards)
    'execute store result score #x smp run data get entity @s Pos[0]',
    'execute store result score #y smp run data get entity @s Pos[1]',
    'execute store result score #z smp run data get entity @s Pos[2]',
    *[f'execute if dimension {d} run tellraw @s ' + msg({'text': 'Du bist gestorben bei ', 'color': 'red'},
        {'score': {'name': '#x', 'objective': 'smp'}, 'color': 'white'}, {'text': ' / ', 'color': 'gray'},
        {'score': {'name': '#y', 'objective': 'smp'}, 'color': 'white'}, {'text': ' / ', 'color': 'gray'},
        {'score': {'name': '#z', 'objective': 'smp'}, 'color': 'white'}, {'text': f' ({name})', 'color': 'gray'}) for d, name, _ in DIMS],
])   # ON_DEATH lines are appended in finish()
fn('core/help', [])      # filled at the end
fn('core/rules', [f'tellraw @s {tc({"text": "Regeln auf " + SERVER_NAME, "color": "gold", "bold": True})}',
                  *[f'tellraw @s {tc([{"text": f" {i + 1}. ", "color": "gold"}, {"text": r, "color": "white"}])}' for i, r in enumerate(RULES)]])
trigger('hilfe', f'{NS}:core/help', '/trigger hilfe', 'Alle Befehle anzeigen', 'Allgemein', ('? Hilfe', 'Alle Befehle'))
trigger('regeln', f'{NS}:core/rules', '/trigger regeln', 'Die Server-Regeln', 'Allgemein', ('§ Regeln', 'Die Server-Regeln'))
trigger('menu', f'{NS}:core/menu', '/trigger menu', 'Das SMP-Menue oeffnen (auch: Esc -> SMP-Menue)', 'Allgemein')
fn('core/menu', [f'dialog show @s {NS}:menu'])

STARTER = ['minecraft:bread 8', 'minecraft:stone_pickaxe', 'minecraft:stone_axe', 'minecraft:torch 16']
fn('core/first_join', [
    'tag @s add smp_seen',
    'scoreboard players add #next_id smp 1', 'scoreboard players operation @s smp_id = #next_id smp',
    'scoreboard players set @s smp_leave 0', 'scoreboard players set @s smp_deaths 0',
    'title @s times 10 60 20',
    f'title @s title {tc({"text": SERVER_NAME, "color": "green", "bold": True})}',
    f'title @s subtitle {tc({"text": "Willkommen! Chat: /trigger hilfe", "color": "gray"})}',
    f'tellraw @a {msg({"selector": "@s", "color": "yellow"}, {"text": " ist zum ersten Mal auf dem Server – willkommen!", "color": "green"})}',
    f'function {NS}:core/welcome',
    *[f'give @s {it}' for it in STARTER],
    f'tellraw @s {msg({"text": "Starter-Kit: 8 Brot, Steinspitzhacke, Steinaxt, 16 Fackeln.", "color": "gray"})}',
])
fn('core/welcome', [
    f'tellraw @s {tc([{"text": "Willkommen auf ", "color": "gray"}, {"text": SERVER_NAME, "color": "green", "bold": True}, {"text": " – Survival mit Freunden.", "color": "gray"}])}',
    f'tellraw @s {tc([{"text": "Alle Befehle: ", "color": "gray"}, clk("[/trigger hilfe]", "/trigger hilfe", "yellow"), {"text": "   Regeln: ", "color": "gray"}, clk("[/trigger regeln]", "/trigger regeln", "yellow"), {"text": "   Menue: ", "color": "gray"}, {"text": "Esc -> SMP-Menue", "color": "yellow"}])}',
])
fn('core/rejoin', ['scoreboard players set @s smp_leave 0', f'execute if score @s smp_id matches 1 run function {NS}:core/reid', f'function {NS}:core/welcome'])
# player number 1 is reserved: a bare "/trigger <obj>" sets the value 1, so "set <nr>" arguments must never collide with it.
# Players from pack version 1 may still have number 1 -> they get a new number (and their storage moves along).
fn('core/reid', [
    'scoreboard players add #next_id smp 1', 'scoreboard players operation @s smp_id = #next_id smp',
    'execute store result storage smp:tmp id int 1 run scoreboard players get @s smp_id',
    f'function {NS}:core/reid2 with storage smp:tmp',
])
fn('core/reid2', [
    '$execute if data storage smp:back p1 run data modify storage smp:back p$(id) set from storage smp:back p1',
    'data remove storage smp:back p1',
    '$execute if data storage smp:homes p1 run data modify storage smp:homes p$(id) set from storage smp:homes p1',
    'data remove storage smp:homes p1',
])


def finish():
    """Writes load/tick/help/menu from the registries and the zip. Called once at the very end."""
    for _cb in EXTRA_FINISH:
        _cb()
    load = [
        'scoreboard objectives add smp dummy',
        'scoreboard objectives add smp_id dummy',
        'scoreboard objectives add smp_tmp dummy',
        'scoreboard objectives add smp_dim dummy',
        'scoreboard objectives add smp_wu dummy', 'scoreboard objectives add smp_wx dummy', 'scoreboard objectives add smp_wy dummy', 'scoreboard objectives add smp_wz dummy',
        'scoreboard objectives add smp_deaths deathCount',
        'scoreboard objectives add smp_tode dummy',
        'scoreboard objectives add smp_mkills minecraft.custom:minecraft.mob_kills',
        'scoreboard objectives add smp_leave minecraft.custom:minecraft.leave_game',
        'scoreboard objectives add smp_pt minecraft.custom:minecraft.play_time',
        f'scoreboard objectives add smp_hours dummy {tc({"text": "Stunden", "color": "gray"})}',
        'scoreboard objectives setdisplay list smp_hours',
        *[f'scoreboard objectives add {o} trigger' for o, *_ in TRIGGERS],
        'scoreboard players set #warm_s smp 3', 'scoreboard players set #warm_t smp 60',
        'scoreboard players set #72000 smp 72000', 'scoreboard players set #20 smp 20', 'scoreboard players set #60 smp 60',
        'execute unless score #next_id smp matches 1.. run scoreboard players set #next_id smp 1',     # first player gets number 2 (1 is reserved)
        f'execute as @a[scores={{smp_id=1}}] run function {NS}:core/reid',
        'gamerule players_sleeping_percentage 1',
        'gamerule spawn_phantoms false',
        *EXTRA_LOAD,
        f'scoreboard players set #smp_v smp {PACK_VERSION}',
        f'tellraw @a {msg({"text": SERVER_NAME + " Datapack geladen.", "color": "gray"})}',
    ]
    fn('load', load)
    fn('tick', [
        *[f'scoreboard players enable @a {o}' for o, *_ in TRIGGERS],
        f'execute as @a[tag=!smp_seen] run function {NS}:core/first_join',
        f'execute as @a[scores={{smp_leave=1..}}] run function {NS}:core/rejoin',
        *[f'execute as @a[scores={{{o}=1..}}] at @s run function {NS}:core/trig_{o}' for o, *_ in TRIGGERS],
        f'execute as @a[scores={{smp_deaths=1..}}] at @s run function {NS}:core/death',
        f'execute as @e[type=minecraft:player,tag=smp_dead] at @s run function {NS}:core/respawn',
        f'execute as @a[scores={{smp_wu=1..}}] at @s run function {NS}:core/warm_tick',
        *EXTRA_TICK,
        'scoreboard players add #t20 smp 1',
        f'execute if score #t20 smp matches 20.. run function {NS}:core/second',
    ])
    for o, handler, *_ in TRIGGERS:
        fn(f'core/trig_{o}', [f'function {handler}', f'scoreboard players set @s {o} 0'])
    fn('core/respawn', ['tag @s remove smp_dead', *ON_RESPAWN])
    files[f'data/{NS}/function/core/death.mcfunction'] += ''.join(l + '\n' for l in ON_DEATH)
    files[f'data/{NS}/function/core/first_join.mcfunction'] += ''.join(l + '\n' for l in ON_JOIN)
    files[f'data/{NS}/function/core/rejoin.mcfunction'] += ''.join(l + '\n' for l in ON_REJOIN)
    fn('core/second', [
        'scoreboard players set #t20 smp 0',
        *[f'scoreboard players remove @a[scores={{{o}=1..}}] {o} 1' for o in COOLDOWNS],
        'execute as @a run scoreboard players operation @s smp_hours = @s smp_pt',
        'scoreboard players operation @a smp_hours /= #72000 smp',
        *EXTRA_SECOND,
    ])
    fn('core/warm_tick', [
        'execute store result score #wx smp run data get entity @s Pos[0]',
        'execute store result score #wy smp run data get entity @s Pos[1]',
        'execute store result score #wz smp run data get entity @s Pos[2]',
        f'execute unless score @s smp_wx = #wx smp run return run function {NS}:core/warm_cancel',
        f'execute unless score @s smp_wy = #wy smp run return run function {NS}:core/warm_cancel',
        f'execute unless score @s smp_wz = #wz smp run return run function {NS}:core/warm_cancel',
        'scoreboard players remove @s smp_wu 1',
        'scoreboard players operation #ws smp = @s smp_wu', 'scoreboard players operation #ws smp /= #20 smp', 'scoreboard players add #ws smp 1',
        f'execute if score @s smp_wu matches 1.. run title @s actionbar {tc([{"text": "Teleport in ", "color": "gray"}, {"score": {"name": "#ws", "objective": "smp"}, "color": "yellow", "bold": True}, {"text": " ... nicht bewegen", "color": "gray"}])}',
        f'execute if score @s smp_wu matches 0 run function {NS}:core/warm_fire',
    ])
    fn('core/warm_clear', [f'tag @s remove smp_wu_{k}' for k, _ in WARMUPS])
    fn('core/warm_fire', [*[f'execute if entity @s[tag=smp_wu_{k}] run function {t}' for k, t in WARMUPS],
                          f'function {NS}:core/warm_clear'])
    fn('core/warm_cancel', ['scoreboard players set @s smp_wu 0', f'function {NS}:core/warm_clear',
                            f'tellraw @s {msg({"text": "Teleport abgebrochen – du hast dich bewegt.", "color": "red"})}'])
    help_lines = [f'tellraw @s {tc({"text": SERVER_NAME + " – Befehle", "color": "green", "bold": True})}',
                  f'tellraw @s {tc({"text": "Tipp: Esc -> SMP-Menue hat alles als Knoepfe.", "color": "gray"})}']
    for cat, entries in HELP.items():
        help_lines.append(f'tellraw @s {tc({"text": " " + cat, "color": "gold", "bold": True})}')
        for usage, text in entries:
            cmd = usage.split(' <')[0]
            btn = clk(usage, cmd + ' ', 'yellow', 'Anklicken, dann den Wert eintippen', 'suggest_command') if '<' in usage else clk(usage, cmd, 'yellow', 'Anklicken')
            help_lines.append(f'tellraw @s {tc([{"text": "  "}, btn, {"text": "  " + text, "color": "gray"}])}')
    fn('core/help', help_lines)
    # Esc menu (dialog registry: needs a server restart to change, functions only need /reload)
    js('data/minecraft/tags/dialog/pause_screen_additions.json', {'values': [f'{NS}:menu']})
    js(f'data/{NS}/dialog/menu.json', {
        'type': 'minecraft:multi_action',
        'title': {'text': SERVER_NAME, 'color': 'green', 'bold': True},
        'external_title': {'text': 'SMP-Menü'},
        'body': {'type': 'minecraft:plain_message', 'width': 310, 'contents': {'text': 'Survival mit Freunden. Alle Funktionen auch per /trigger (siehe Hilfe).', 'color': 'gray'}},
        'columns': 2,
        'actions': [{'label': {'text': lab}, 'tooltip': {'text': tip}, 'width': w, 'action': {'type': 'run_command', 'command': cmd}} for lab, tip, cmd, w in MENU],
        'exit_action': {'label': {'text': 'Schließen'}, 'width': 200},
    })
    # write
    if os.path.exists(ROOT):
        import shutil
        shutil.rmtree(ROOT)
    for p, c in files.items():
        full = os.path.join(ROOT, p)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, 'w', encoding='utf-8') as f:
            f.write(c)
    with zipfile.ZipFile(os.path.join(OUT, 'smp.zip'), 'w', zipfile.ZIP_DEFLATED) as z:
        for p, c in files.items():
            z.writestr(p, c)
    print(f'{len(files)} files -> {os.path.join(OUT, "smp.zip")}')


# ------------------------------------------------------------------ modules
_only = [m for m in os.environ.get('SMP_MODULES', '').split(',') if m]
_mdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'modules')
for _f in sorted(os.listdir(_mdir)) if os.path.isdir(_mdir) else []:
    if _f.endswith('.py') and (not _only or _f[:-3] in _only):
        exec(compile(open(os.path.join(_mdir, _f), encoding='utf-8').read(), _f, 'exec'))

finish()
