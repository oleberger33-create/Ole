#!/usr/bin/env python3
"""Minigames-Datapack (Minecraft 26.3, data pack format 121).

Lobby mit Hotbar-Items, Parkour-Rush (Jump'n'Run + Loot + Arena-Kampf),
1v1: Sumo, Spleef, Duell (Best of 3, Warteschlange per Rechtsklick).

Run:  python3 build.py <out_dir> [min_format]  -> <out_dir>/minigames/ und <out_dir>/minigames.zip
"""
import json, math, os, random, shutil, sys, zipfile

OUT = sys.argv[1] if len(sys.argv) > 1 else 'out'
MIN_FORMAT = int(sys.argv[2]) if len(sys.argv) > 2 else 121
ROOT = os.path.join(OUT, 'minigames')
NS = 'mg'
BUILD_VERSION = 4
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

OW = 'execute in minecraft:overworld run'
Y = 100                       # floor level of every build
HUB = (0, Y, 0)
RUSH = (1000, Y, 0)           # parkour start
ARENA = (2000, Y, 0)          # rush final fight
DUELS = {                     # 1v1 games: key -> (name, centre, colour)
    'sumo':   ('Sumo', (3000, Y, 0), 'yellow'),
    'spleef': ('Spleef', (4000, Y, 0), 'aqua'),
    'duell':  ('Duell', (5000, Y, 0), 'red'),
}
RUSH_TIME = 900               # seconds of parkour before the arena
FINISH_GRACE = 30             # seconds after the first finisher

# ------------------------------------------------------------------ meta / tags
js('pack.mcmeta', {'pack': {'description': 'Minigames: Parkour-Rush, Sumo, Spleef, Duell',
                            'min_format': MIN_FORMAT, 'max_format': [121, 999]}})
js('data/minecraft/tags/function/load.json', {'values': [f'{NS}:load']})
js('data/minecraft/tags/function/tick.json', {'values': [f'{NS}:tick']})

# ------------------------------------------------------------------ loot tables
def item(name, weight, count=None, extra=None):
    """Loot entry in the 26.3 format: modifiers live under "modifier" and use "type"."""
    e = {'type': 'minecraft:item', 'name': f'minecraft:{name}', 'weight': weight}
    mods = []
    if count:
        mods.append({'type': 'minecraft:set_count', 'count': {'type': 'minecraft:uniform', 'min': count[0], 'max': count[1]}})
    if extra:
        mods += extra
    if mods:
        e['modifier'] = mods if len(mods) > 1 else mods[0]
    return e

def ench(**lv):
    return [{'type': 'minecraft:set_enchantments', 'enchantments': {f'minecraft:{k}': v for k, v in lv.items()}}]
def potion(pid):
    return [{'type': 'minecraft:set_potion', 'id': f'minecraft:{pid}'}]
LOOT = {
    'chest_easy': ((2, 3), [item('iron_sword', 3), item('stone_axe', 2), item('iron_helmet', 3), item('iron_boots', 3),
                            item('chainmail_chestplate', 3), item('chainmail_leggings', 2), item('bow', 2), item('arrow', 3, (8, 16)),
                            item('cooked_beef', 3, (4, 8)), item('shield', 2), item('golden_apple', 1)]),
    'chest_mid': ((3, 4), [item('iron_chestplate', 3), item('iron_leggings', 3), item('diamond_helmet', 2), item('diamond_boots', 2),
                           item('iron_sword', 3, None, ench(sharpness=2)), item('bow', 2, None, ench(power=2)), item('arrow', 3, (12, 20)),
                           item('golden_apple', 3, (1, 2)), item('splash_potion', 2, None, potion('healing')), item('ender_pearl', 1, (1, 2)),
                           item('shield', 2)]),
    'chest_hard': ((3, 4), [item('diamond_chestplate', 2), item('diamond_leggings', 2), item('diamond_sword', 3), item('diamond_axe', 1),
                            item('crossbow', 2, None, ench(quick_charge=2)), item('golden_apple', 3, (2, 3)),
                            item('splash_potion', 2, None, potion('strong_healing')), item('potion', 2, None, potion('strength')),
                            item('ender_pearl', 2, (1, 2)), item('arrow', 2, (16, 24)), item('iron_chestplate', 2, None, ench(protection=2))]),
    'chest_elite': ((4, 4), [item('diamond_sword', 3, None, ench(sharpness=2)), item('diamond_chestplate', 3, None, ench(protection=1)),
                             item('diamond_leggings', 3), item('diamond_boots', 2, None, ench(protection=2)), item('bow', 2, None, ench(power=3)),
                             item('golden_apple', 3, (2, 4)), item('splash_potion', 2, None, potion('strong_healing')),
                             item('potion', 2, None, potion('strength')), item('ender_pearl', 2, (2, 3)), item('arrow', 2, (20, 32))]),
    'chest_finish': ((4, 5), [item('diamond_sword', 3, None, ench(sharpness=3)), item('diamond_chestplate', 3, None, ench(protection=2)),
                              item('diamond_leggings', 2, None, ench(protection=2)), item('diamond_helmet', 2, None, ench(protection=2)),
                              item('bow', 2, None, ench(power=3, flame=1)), item('enchanted_golden_apple', 1), item('golden_apple', 3, (3, 4)),
                              item('splash_potion', 2, None, potion('strong_healing')), item('potion', 2, None, potion('strong_strength')),
                              item('totem_of_undying', 1)]),
}
for key, (rolls, entries) in LOOT.items():
    js(f'data/{NS}/loot_table/{key}.json', {'type': 'minecraft:chest',
        'pools': [{'rolls': {'type': 'minecraft:uniform', 'min': rolls[0], 'max': rolls[1]}, 'entries': entries}]})

# ------------------------------------------------------------------ geometry helpers
def disk(cx, y, cz, r, block):
    out = []
    for dz in range(-r, r + 1):
        w = int(math.floor(math.sqrt(r * r + r - dz * dz)))
        out.append(f'fill {cx - w} {y} {cz + dz} {cx + w} {y} {cz + dz} minecraft:{block}')
    return out


def ring(cx, y, cz, r, block, h=1):
    out = []
    pts = set()
    for a in range(0, 360, 2):
        x = cx + round((r + 0.5) * math.cos(math.radians(a)))
        z = cz + round((r + 0.5) * math.sin(math.radians(a)))
        pts.add((x, z))
    for x, z in sorted(pts):
        out.append(f'fill {x} {y} {z} {x} {y + h - 1} {z} minecraft:{block}')
    return out


def holo(tag, x, y, z, text, scale=1.0):
    return (f'{OW} summon minecraft:text_display {x} {y} {z} {{Tags:["mg_holo","{tag}"],billboard:"center",'
            f'background:0,shadow:true,text:{tc(text)},transformation:{{left_rotation:[0f,0f,0f,1f],'
            f'right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[{scale}f,{scale}f,{scale}f]}}}}')


def forceload(cx, cz, r):
    return f'{OW} forceload add {cx - r} {cz - r} {cx + r} {cz + r}'

# ------------------------------------------------------------------ parkour: 24 modules on floating islands, one private lane per player
LANES = 6
MODULES = 24
NCP = MODULES                     # checkpoint n = island after module n (24 = finish)
def map_x(mi):
    return 10000 + mi * 1000
def lane_z(L):
    return 1000 * L

THEMES = [
    dict(name='Himmel', color='aqua', seed=26, top='grass_block', under='dirt', core='stone', jump=['white_concrete', 'light_blue_concrete', 'yellow_concrete', 'orange_concrete'],
         fence='oak_fence', pillar='quartz_pillar', accent='sea_lantern', flower=['dandelion', 'poppy', 'cornflower', 'azure_bluet'], deco='cloud', ice=False),
    dict(name='Nether', color='red', seed=7, top='crimson_nylium', under='netherrack', core='blackstone', jump=['nether_bricks', 'red_nether_bricks', 'blackstone', 'magma_block'],
         fence='nether_brick_fence', pillar='polished_basalt', accent='shroomlight', flower=['crimson_fungus', 'crimson_roots', 'warped_fungus'], deco='nether', ice=False),
    dict(name='Eis', color='aqua', seed=99, top='snow_block', under='packed_ice', core='blue_ice', jump=['snow_block', 'packed_ice', 'packed_ice', 'blue_ice'],
         fence='spruce_fence', pillar='packed_ice', accent='sea_lantern', flower=['fern', 'short_grass'], deco='spike', ice=True),
    dict(name='Dschungel', color='green', seed=42, top='moss_block', under='rooted_dirt', core='mossy_cobblestone', jump=['moss_block', 'jungle_log', 'mossy_stone_bricks', 'jungle_planks'],
         fence='jungle_fence', pillar='jungle_log', accent='glowstone', flower=['fern', 'azalea', 'flowering_azalea', 'large_fern'], deco='tree', ice=False),
    dict(name='End', color='light_purple', seed=13, top='end_stone', under='end_stone', core='obsidian', jump=['end_stone_bricks', 'purpur_block', 'obsidian', 'crying_obsidian'],
         fence='end_rod', pillar='purpur_pillar', accent='end_rod', flower=['chorus_flower'], deco='endisle', ice=False),
]
TIER = lambda n: ('chest_finish' if n >= MODULES else 'chest_elite' if n > 18 else 'chest_hard' if n > 12 else 'chest_mid' if n > 6 else 'chest_easy')

def gen_map(t):
    rnd = random.Random(t['seed'])
    B = {}
    chests, cps, holos, path = [], [], [], []
    def put(x, y, z, b):
        B[(x, y, z)] = b
    def island(cx, cy, cz, r, chest=None, label=None, big=False):
        for px in range(-r, r + 1):
            for pz in range(-r, r + 1):
                d = px * px + pz * pz
                if d <= r * r + r:
                    put(cx + px, cy, cz + pz, t['top'])
                    put(cx + px, cy - 1, cz + pz, t['under'])
                    if d <= (r - 1) * (r - 1) + r - 1:
                        put(cx + px, cy - 2, cz + pz, t['under'])
                    if d <= (r - 2) * (r - 2):
                        put(cx + px, cy - 3, cz + pz, t['core'])
        put(cx, cy - 4, cz, t['core'])
        # decoration on the island rim, away from the walking line (z == cz)
        for _ in range(3 if not big else 6):
            px, pz = rnd.randint(-r + 1, r - 1), rnd.choice([-r + 1, r - 1])
            if t['flower'] and (px, pz) != (0, 0):
                put(cx + px, cy + 1, cz + pz, rnd.choice(t['flower']))
        put(cx - r + 1, cy + 1, cz - r + 1, 'lantern') if t['accent'] != 'end_rod' else put(cx - r + 1, cy + 1, cz - r + 1, 'end_rod')
        if chest:
            chests.append(chest)
        if label:
            holos.append(label)
    x, y, z = 0, 0, 0
    island(0, 0, 0, 3, label=(0, 3.2, 0, [{'text': 'START\n', 'color': 'green', 'bold': True}, {'text': 'Map: ' + t['name'], 'color': t['color'], 'bold': False}], 1.4))
    put(0, 0, 0, 'emerald_block')
    x = 3
    path.append((x, y, z))
    POOLS = [['hop', 'pillars', 'stairs', 'hop'],
             ['hop', 'pillars', 'ladder', 'head', 'fence', 'drop', 'stairs'],
             ['pillars', 'ladder', 'head', 'fence', 'drop', 'neo', 'hop', 'ice'],
             ['pillars', 'head', 'fence', 'neo', 'neo', 'drop', 'ladder', 'ice', 'hop']]
    for n in range(1, MODULES + 1):
        diff = 0 if n <= 6 else 1 if n <= 12 else 2 if n <= 18 else 3
        blk = t['jump'][diff]
        kind = rnd.choice(POOLS[diff])
        if kind == 'ice' and not t['ice']:
            kind = 'pillars'
        if kind == 'ladder' and y > 18:
            kind = 'drop'
        if kind == 'stairs' and y > 20:
            kind = 'hop'
        if kind == 'drop' and y < -6:
            kind = 'stairs'
        def jump(dxr, dyr):
            nonlocal x, y, z
            dx = rnd.randint(*dxr); dy = rnd.randint(*dyr)
            if dx >= 4 and dy == 1:
                dy = 0
            dz = rnd.randint(-1, 1) if dx >= 4 else rnd.randint(-2, 2)
            if dx == 3 and dy == 1 and abs(dz) == 2:
                dz = dz // 2
            x, y, z = x + dx, y + dy, max(-20, min(20, z + dz))
        if kind == 'hop':                                   # tiny 2x2 islands
            for _ in range(rnd.randint(3, 5)):
                jump((3, 4), (0, 0) if diff == 0 else (-1, 1))
                for ox in (0, 1):
                    for oz in (0, 1):
                        put(x + ox, y, z + oz, t['top']); put(x + ox, y - 1, z + oz, t['under'])
                if rnd.random() < 0.4 and t['flower']:
                    put(x + 1, y + 1, z + 1, rnd.choice(t['flower']))
                x += 1
        elif kind == 'pillars':
            for _ in range(rnd.randint(4, 6)):
                jump((2, 3) if diff == 0 else (3, 4), (0, 0) if diff == 0 else (-1, 1))
                put(x, y, z, blk)
                for py in range(1, rnd.randint(3, 6)):
                    put(x, y - py, z, t['pillar'] if t['pillar'] != 'end_rod' else t['core'])
        elif kind == 'stairs':
            for _ in range(4):
                x, y = x + 2, y + 1
                z = max(-20, min(20, z + rnd.choice((-1, 0, 1))))
                put(x, y, z, blk)
        elif kind == 'ladder':
            x += 3
            put(x, y, z, blk)
            h = rnd.randint(4, 6)
            for ly in range(1, h + 1):
                put(x + 1, y + ly, z, t['core'])
                put(x, y + ly, z, 'ladder[facing=west]')
            x, y = x + 1, y + h
            put(x, y, z, t['accent'] if t['accent'] != 'end_rod' else blk)
            jump((3, 4), (-1, 0)); put(x, y, z, blk)
        elif kind == 'head':                               # jumps under a ceiling
            for _ in range(3):
                x += 3
                put(x, y, z, blk)
                put(x, y + 3, z, t['core'])
            x += 3; put(x, y, z, blk)
        elif kind == 'fence':                              # thin fence posts
            x += 3; put(x, y, z, blk)
            fb = t['fence'] if t['fence'] != 'end_rod' else 'end_stone_brick_wall'
            for _ in range(rnd.randint(3, 4)):
                x += 2 if diff < 3 else 3
                put(x, y, z, fb)
                put(x, y - 1, z, t['core'])
            x += 2; put(x, y + 1 if False else y, z, blk)
        elif kind == 'drop':
            for _ in range(2):
                x, y = x + 4, y - 2
                z = max(-20, min(20, z + rnd.choice((-1, 0, 1))))
                put(x, y, z, blk)
            jump((3, 3), (0, 1)); put(x, y, z, blk)
        elif kind == 'neo':                                # jump around the end of a wall
            x += 3; put(x, y, z, blk)
            side = 1 if z <= 0 else -1
            for wz in range(0, 4):
                for wy in range(1, 4):
                    put(x + 1, y + wy, z - side * wz, t['core'])
            put(x + 1, y, z - side * 1, t['core'])
            x += 2; put(x, y, z, blk)
            jump((3, 3), (0, 0)); put(x, y, z, blk)
        elif kind == 'ice':
            x += 3; put(x, y, z, blk)
            for i in range(1, 5):
                put(x + i, y, z, 'packed_ice')
            x += 4 + 4
            put(x, y, z, 'blue_ice')
            jump((3, 3), (0, 0)); put(x, y, z, 'packed_ice')
        path.append((x, y, z))
        # checkpoint island n
        r = 4 if n == MODULES else 3
        x += r + 3
        island(x, y, z, r, big=(n == MODULES))
        put(x, y, z, 'gold_block' if n < MODULES else 'diamond_block')
        if n < MODULES:
            cps.append((x, y, z, [(1, 1, 2)]))            # chest offsets relative to the island centre
            holos.append((x, y + 3.0, z, [{'text': f'Checkpoint {n}', 'color': 'yellow', 'bold': True}], 1.1))
        else:
            cps.append((x, y, z, [(1, 1, 3), (-1, 1, 3)]))
            for gz in (-5, 5):
                for gy in range(1, 6):
                    put(x + 4, y + gy, z + gz, t['core'])
            for gz in range(-5, 6):
                put(x + 4, y + 6, z + gz, t['accent'] if t['accent'] != 'end_rod' else t['core'])
            holos.append((x, y + 3.4, z, [{'text': 'ZIEL\n', 'color': 'aqua', 'bold': True}, {'text': '2 Truhen mit dem besten Loot', 'color': 'gold', 'bold': False}], 1.5))
        x += r + 1
        path.append((x, y, z))
    length = x + 6
    # scenery far from the path
    drnd = random.Random(t['seed'] * 7 + 1)
    def near_path(dx, dz):
        return any(abs(dx - px) < 10 and abs(dz - pz) < 10 for (px, py, pz) in path)
    for k in range(70):
        cx = drnd.randint(0, length)
        cz = drnd.choice((-1, 1)) * drnd.randint(14, 34)
        if near_path(cx, cz):
            continue
        cy = drnd.randint(-10, 22)
        d = t['deco']
        if d == 'cloud':
            for ox in range(-3, 4):
                for oz in range(-2, 3):
                    if ox * ox / 9 + oz * oz / 4 <= 1.05 and drnd.random() < 0.9:
                        put(cx + ox, cy, cz + oz, 'white_wool')
                        if abs(ox) < 2 and abs(oz) < 2:
                            put(cx + ox, cy + 1, cz + oz, 'white_wool')
        elif d == 'nether':
            for ox in range(-2, 3):
                for oz in range(-2, 3):
                    if ox * ox + oz * oz <= 5:
                        put(cx + ox, cy, cz + oz, 'netherrack')
            put(cx, cy + 1, cz, 'glowstone'); put(cx + 1, cy, cz, 'magma_block'); put(cx - 1, cy - 1, cz, 'crying_obsidian')
        elif d == 'spike':
            h = drnd.randint(5, 12)
            for oy in range(h):
                put(cx, cy + oy, cz, 'packed_ice')
                if oy < h // 2:
                    for ox, oz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        put(cx + ox, cy + oy, cz + oz, 'packed_ice')
        elif d == 'tree':
            for ox in range(-2, 3):
                for oz in range(-2, 3):
                    if ox * ox + oz * oz <= 5:
                        put(cx + ox, cy, cz + oz, 'grass_block')
            for oy in range(1, 5):
                put(cx, cy + oy, cz, 'jungle_log')
            for ox in range(-2, 3):
                for oz in range(-2, 3):
                    if ox * ox + oz * oz <= 5 and (ox, oz) != (0, 0):
                        put(cx + ox, cy + 4, cz + oz, 'jungle_leaves[persistent=true]')
            put(cx, cy + 5, cz, 'jungle_leaves[persistent=true]')
        elif d == 'endisle':
            for ox in range(-2, 3):
                for oz in range(-2, 3):
                    if ox * ox + oz * oz <= 5:
                        put(cx + ox, cy, cz + oz, 'end_stone')
            for oy in range(1, drnd.randint(3, 6)):
                put(cx, cy + oy, cz, 'purpur_pillar')
            put(cx + 1, cy + 1, cz, 'end_rod')
    ys = [p[1] for p in path]
    return dict(blocks=B, cps=cps, holos=holos, length=length, miny=min(ys), maxy=max(ys))

MAPGEN = [gen_map(t) for t in THEMES]
MAXLEN = max(m['length'] for m in MAPGEN) + 10
for t, m in zip(THEMES, MAPGEN):
    print(f"map {t['name']}: {len(m['blocks'])} blocks, length {m['length']}, y {m['miny']}..{m['maxy']}, checkpoints {len(m['cps'])}")

# ------------------------------------------------------------------ load
load = [
    forceload(HUB[0], HUB[2], 32),
    f'{OW} forceload remove 984 -96 1176 96',   # v1 left the old single parkour permanently loaded
    forceload(ARENA[0], ARENA[2], 32),
    *[forceload(c[0], c[2], 24) for _, c, _ in DUELS.values()],
    'scoreboard objectives add mg dummy',
    'scoreboard objectives add mg_click minecraft.used:minecraft.carrot_on_a_stick',
    'scoreboard objectives add mg_deaths deathCount',
    'scoreboard objectives add mg_leave minecraft.custom:minecraft.leave_game',
    'scoreboard objectives add mg_cp dummy',
    'scoreboard objectives add mg_lane dummy',
    f'scoreboard objectives add mg_prog dummy {tc({"text": "Fortschritt (Inseln /24)", "color": "green", "bold": True})}', 'scoreboard objectives add mg_cx dummy', 'scoreboard objectives add mg_cy dummy', 'scoreboard objectives add mg_cz dummy',
    'scoreboard objectives add mg_loot dummy',
    'scoreboard objectives add mg_round dummy',
    'scoreboard objectives add mg_aktion trigger',
    f'scoreboard objectives add mg_wins dummy {tc({"text": "Siege", "color": "gold"})}',
    'scoreboard objectives setdisplay list mg_wins',
    f'scoreboard objectives add mg_side dummy {tc({"text": "MINIGAMES", "color": "gold", "bold": True})}',
    'scoreboard objectives modify mg_side numberformat blank',
    'scoreboard objectives setdisplay sidebar mg_side',
    'scoreboard players set #20 mg 20', 'scoreboard players set #60 mg 60', f'scoreboard players set #{LANES} mg {LANES}', 'scoreboard players set #6 mg 6',
    'execute unless score #rush mg matches 0.. run scoreboard players set #rush mg 0',
    *[f'execute unless score #{k} mg matches 0.. run scoreboard players set #{k} mg 0' for k in DUELS],
    'gamerule pvp true',
    'gamerule keep_inventory false',
    'gamerule immediate_respawn true',
    'gamerule spawn_monsters false',
    'gamerule spawn_mobs false',
    'gamerule advance_time false',
    'gamerule advance_weather false',
    'gamerule fall_damage true',
    'gamerule show_death_messages false',
    'gamerule respawn_radius 0',
    'gamerule natural_health_regeneration true',
    'time set 6000', 'weather clear',
    f'setworldspawn {HUB[0]} {HUB[1] + 1} {HUB[2]}',
    'difficulty normal',
    f'bossbar add {NS}:rush {tc({"text": "Parkour-Rush"})}',
    f'bossbar set {NS}:rush color green',
    f'function {NS}:hub/sidebar',
    f'execute unless score #built mg matches {BUILD_VERSION} run schedule function {NS}:build/try 40t',
    f'execute if score #built mg matches {BUILD_VERSION} unless score #lanes mg matches {BUILD_VERSION} run schedule function {NS}:build/lane_resume 40t',
]
fn('load', load)

# ------------------------------------------------------------------ build
fn('build/try', [
    f'execute in minecraft:overworld if loaded {HUB[0]} {Y} {HUB[2]} '
    f'if loaded {ARENA[0]} {Y} {ARENA[2]} if loaded {DUELS["duell"][1][0]} {Y} 0 run return run function {NS}:build/all',
    f'schedule function {NS}:build/try 20t',
])
fn('build/all', [
    'kill @e[type=minecraft:text_display,tag=mg_holo]',
    f'function {NS}:build/hub', f'function {NS}:build/arena',
    *[f'function {NS}:build/{k}' for k in DUELS],
    f'function {NS}:build/done',
    'scoreboard players set #bq mg 0', 'scoreboard players set #lanes_done mg 0', f'function {NS}:build/lane_next',
])
fn('build/done', [f'scoreboard players set #built mg {BUILD_VERSION}', f'tellraw @a {msg({"text": "Minigame-Welt gebaut.", "color": "gray"})}'])

hx, hy, hz = HUB
hub = [f'{OW} {c}' for c in (
    [f'fill {hx - 16} {hy - 4} {hz - 16} {hx + 16} {hy + 12} {hz + 16} minecraft:air']
    + disk(hx, hy, hz, 13, 'smooth_quartz') + disk(hx, hy, hz, 4, 'polished_andesite')
    + [f'setblock {hx} {hy} {hz} minecraft:gold_block']
    + disk(hx, hy - 1, hz, 12, 'quartz_bricks') + disk(hx, hy - 2, hz, 9, 'quartz_bricks') + disk(hx, hy - 3, hz, 5, 'quartz_bricks')
    + ring(hx, hy + 1, hz, 13, 'glass', 2)
)]
for i, a in enumerate(range(0, 360, 45)):
    lx, lz = hx + round(10 * math.cos(math.radians(a))), hz + round(10 * math.sin(math.radians(a)))
    hub += [f'{OW} setblock {lx} {hy + 1} {lz} minecraft:quartz_pillar', f'{OW} setblock {lx} {hy + 2} {lz} minecraft:lantern']
hub += [
    holo('mg_title', hx, hy + 6.2, hz - 6, {'text': 'MINIGAMES', 'color': 'gold', 'bold': True}, 4.0),
    holo('mg_sub', hx, hy + 5.4, hz - 6, {'text': 'Ole · Mats · Sammy · Qelloxx', 'color': 'gray'}, 1.4),
    holo('mg_help', hx, hy + 2.2, hz - 4, [{'text': 'Rechtsklick auf die Items in deiner Hotbar', 'color': 'white'}], 1.0),
    holo('mg_g1', hx - 7, hy + 3.2, hz + 6, [{'text': 'PARKOUR-RUSH\n', 'color': 'green', 'bold': True}, {'text': 'Springen, Loot sammeln,\nam Ende kämpfen', 'color': 'gray', 'bold': False}], 1.0),
    holo('mg_g2', hx, hy + 3.2, hz + 8, [{'text': '1 GEGEN 1\n', 'color': 'red', 'bold': True}, {'text': 'Sumo · Spleef · Duell\nBest of 3', 'color': 'gray', 'bold': False}], 1.0),
    holo('mg_g3', hx + 7, hy + 3.2, hz + 6, [{'text': 'SIEGE\n', 'color': 'gold', 'bold': True}, {'text': 'stehen in der Tab-Liste', 'color': 'gray', 'bold': False}], 1.0),
]
fn('build/hub', hub)

ax, ay, az = ARENA
arena = [f'{OW} {c}' for c in (
    [f'fill {ax - 24} {ay - 4} {az - 24} {ax + 24} {ay + 12} {az + 24} minecraft:air']
    + disk(ax, ay, az, 18, 'stone_bricks') + disk(ax, ay, az, 6, 'chiseled_stone_bricks')
    + disk(ax, ay - 1, az, 18, 'stone') + ring(ax, ay + 1, az, 18, 'barrier', 8) + ring(ax, ay + 1, az, 18, 'mossy_stone_brick_wall', 1)
)]
for a in range(0, 360, 60):
    px, pz = ax + round(11 * math.cos(math.radians(a))), az + round(11 * math.sin(math.radians(a)))
    arena += [f'{OW} fill {px} {ay + 1} {pz} {px + 1} {ay + 3} {pz + 1} minecraft:mossy_stone_bricks']
arena.append(holo('mg_arena', ax, ay + 9, az, {'text': 'ARENA', 'color': 'red', 'bold': True}, 3.0))
fn('build/arena', arena)

def duel_build(key):
    name, (cx, cy, cz), color = DUELS[key]
    out = [f'{OW} fill {cx - 16} {cy - 6} {cz - 16} {cx + 16} {cy + 10} {cz + 16} minecraft:air']
    if key == 'sumo':
        out += [f'{OW} {c}' for c in disk(cx, cy, cz, 6, 'white_concrete') + disk(cx, cy, cz, 5, 'yellow_concrete')
                + disk(cx, cy - 1, cz, 5, 'smooth_stone')]
    elif key == 'spleef':
        out += [f'{OW} fill {cx - 10} {cy} {cz - 10} {cx + 10} {cy} {cz + 10} minecraft:snow_block']
        out += [f'{OW} {c}' for c in ring(cx, cy + 1, cz, 14, 'barrier', 5)]
    else:
        out += [f'{OW} fill {cx - 12} {cy} {cz - 12} {cx + 12} {cy} {cz + 12} minecraft:red_sandstone',
                f'{OW} fill {cx - 12} {cy - 1} {cz - 12} {cx + 12} {cy - 1} {cz + 12} minecraft:stone',
                f'{OW} fill {cx - 13} {cy + 1} {cz - 13} {cx + 13} {cy + 6} {cz + 13} minecraft:barrier hollow',
                f'{OW} fill {cx - 12} {cy + 1} {cz - 12} {cx + 12} {cy + 5} {cz + 12} minecraft:air',
                f'{OW} fill {cx - 1} {cy + 1} {cz - 4} {cx + 1} {cy + 2} {cz - 4} minecraft:cut_red_sandstone',
                f'{OW} fill {cx - 1} {cy + 1} {cz + 4} {cx + 1} {cy + 2} {cz + 4} minecraft:cut_red_sandstone']
    out.append(holo('mg_d', cx, cy + 7, cz, {'text': name.upper(), 'color': color, 'bold': True}, 3.0))
    return out
for k in DUELS:
    fn(f'build/{k}', duel_build(k))
fn('spleef/reset_floor', [f'{OW} fill {DUELS["spleef"][1][0] - 10} {Y} {DUELS["spleef"][1][2] - 10} '
                          f'{DUELS["spleef"][1][0] + 10} {Y} {DUELS["spleef"][1][2] + 10} minecraft:snow_block'])

# ------------------------------------------------------------------ hotbar items
def citem(key, model, name, lore, glint=False):
    comps = [f'minecraft:item_model="minecraft:{model}"',
             f'minecraft:custom_name={tc(dict(name, italic=False))}',
             'minecraft:lore=[' + ','.join(tc({'text': l, 'color': 'gray', 'italic': False}) for l in lore) + ']',
             f'minecraft:custom_data={{mg_item:1b,mg:"{key}"}}',
             'minecraft:unbreakable={}',
             'minecraft:tooltip_display={hidden_components:["minecraft:unbreakable"]}',
             'minecraft:use_cooldown={seconds:0.6f}']
    if glint:
        comps.append('minecraft:enchantment_glint_override=true')
    return 'minecraft:carrot_on_a_stick[' + ','.join(comps) + ']'

HOTBAR = [
    (0, 'rush', 'feather', {'text': '▶ PARKOUR-RUSH', 'color': 'green', 'bold': True},
     ['Startet für alle in der Lobby', 'Springen, Loot sammeln, dann Arena-Kampf'], True),
    (2, 'sumo', 'slime_ball', {'text': 'Sumo 1v1', 'color': 'yellow', 'bold': True},
     ['Schubs den Gegner von der Plattform', 'Rechtsklick: Warteschlange an/aus'], False),
    (3, 'spleef', 'diamond_shovel', {'text': 'Spleef 1v1', 'color': 'aqua', 'bold': True},
     ['Grab den Schnee unter dem Gegner weg', 'Rechtsklick: Warteschlange an/aus'], False),
    (4, 'duell', 'iron_sword', {'text': 'Duell 1v1', 'color': 'red', 'bold': True},
     ['Schwert, Bogen, Rüstung', 'Rechtsklick: Warteschlange an/aus'], False),
    (8, 'info', 'book', {'text': 'Info', 'color': 'white', 'bold': True}, ['Rechtsklick: Spielregeln'], False),
]
fn('hub/hotbar', ['clear @s *[minecraft:custom_data~{mg_item:1b}]']
   + [f'item replace entity @s hotbar.{slot} with ' + citem(key, model, name, lore, glint) for slot, key, model, name, lore, glint in HOTBAR])
fn('hub/click', [
    'scoreboard players set @s mg_click 0',
    'execute unless entity @s[tag=mg_hub] run return 0',
    f'execute if items entity @s weapon.mainhand *[minecraft:custom_data~{{mg:"rush"}}] run return run function {NS}:rush/request',
    *[f'execute if items entity @s weapon.mainhand *[minecraft:custom_data~{{mg:"{k}"}}] run return run function {NS}:q/toggle_{k}' for k in DUELS],
    f'execute if items entity @s weapon.mainhand *[minecraft:custom_data~{{mg:"info"}}] run return run function {NS}:hub/info',
])
fn('hub/info', [f'tellraw @s {msg({"text": "Spielregeln", "color": "gold", "bold": True})}',
                f'tellraw @s {tc([{"text": " Parkour-Rush: ", "color": "green", "bold": True}, {"text": f"Jeder springt auf seiner eigenen Strecke: 24 schwebende Inseln mit Sprung-Modulen (Säulen, Leitern, Kopfstoß, Zäune, Neo, Eis …) auf einer von 5 Maps. Auf jeder Insel wartet eine Truhe – je weiter du kommst, desto besser der Loot. Rechts siehst du, wie weit die anderen sind. Nach 15 Minuten (oder {FINISH_GRACE} s nach dem Ersten im Ziel) geht es in die Arena – wer zuletzt steht, gewinnt. Runterfallen = zurück zum Checkpoint.", "color": "white"}])}',
                f'tellraw @s {tc([{"text": " Sumo: ", "color": "yellow", "bold": True}, {"text": "Ohne Waffen. Wer von der Plattform fällt, verliert die Runde.", "color": "white"}])}',
                f'tellraw @s {tc([{"text": " Spleef: ", "color": "aqua", "bold": True}, {"text": "Mit der Schaufel den Schnee unter dem Gegner wegmachen.", "color": "white"}])}',
                f'tellraw @s {tc([{"text": " Duell: ", "color": "red", "bold": True}, {"text": "Schwert, Bogen, Eisenrüstung. Wer stirbt, verliert die Runde.", "color": "white"}])}',
                f'tellraw @s {tc([{"text": " 1v1 ist Best of 3. Zwei Spieler in derselben Warteschlange starten automatisch.", "color": "gray"}])}'])

# ------------------------------------------------------------------ hub / player state
fn('hub/tp', [f'{OW} tp @s {HUB[0]} {HUB[1] + 1} {HUB[2]} 180 0'])
fn('hub/enter', [
    'tag @s remove mg_rush', 'tag @s remove mg_fight', 'tag @s remove mg_duel', 'tag @s remove mg_p1', 'tag @s remove mg_p2',
    'tag @s add mg_hub',
    'clear @s', 'effect clear @s', 'experience set @s 0 levels', 'experience set @s 0 points',
    'effect give @s minecraft:instant_health 1 10 true', 'effect give @s minecraft:saturation 1 20 true',
    'gamemode adventure @s',
    f'function {NS}:hub/tp',
    f'{OW} spawnpoint @s {HUB[0]} {HUB[1] + 1} {HUB[2]}',
    f'function {NS}:hub/hotbar',
])
fn('hub/keep', [
    'effect give @s minecraft:resistance infinite 4 true',
    'effect give @s minecraft:saturation infinite 0 true',
    'execute unless entity @s[gamemode=adventure] unless entity @s[gamemode=creative] unless entity @s[gamemode=spectator] run gamemode adventure @s',
    f'execute at @s unless entity @s[x={HUB[0] - 30},dx=60,y={Y - 6},dy=40,z={HUB[2] - 30},dz=60] run function {NS}:hub/tp',
    *[f'execute unless items entity @s hotbar.{slot} *[minecraft:custom_data~{{mg:"{key}"}}] run return run function {NS}:hub/hotbar'
      for slot, key, *_ in HOTBAR],
])
fn('hub/first', ['tag @s add mg_seen', f'function {NS}:hub/enter', 'title @s times 10 50 15',
                 f'title @s title {tc({"text": "MINIGAMES", "color": "gold", "bold": True})}',
                 f'title @s subtitle {tc({"text": "Rechtsklick auf die Items in deiner Hotbar", "color": "gray"})}'])
fn('hub/rejoin', ['scoreboard players set @s mg_leave 0', f'function {NS}:q/leave_all', f'function {NS}:hub/enter'])
fn('hub/sweep', [
    'scoreboard players set #itick mg 0',
    'execute as @e[type=minecraft:item] if items entity @s contents *[minecraft:custom_data~{mg_item:1b}] run kill @s',
    'clear @a[tag=!mg_hub] *[minecraft:custom_data~{mg_item:1b}]',
])
side = ['scoreboard players reset * mg_side']
rows = [('a1', {'text': ' '}),
        ('a2', [{'text': 'Rechtsklick auf die Items', 'color': 'gray'}]),
        ('a3', [{'text': '1 ', 'color': 'dark_gray'}, {'text': 'Parkour-Rush', 'color': 'green'}]),
        ('a4', [{'text': '3 ', 'color': 'dark_gray'}, {'text': 'Sumo 1v1', 'color': 'yellow'}]),
        ('a5', [{'text': '4 ', 'color': 'dark_gray'}, {'text': 'Spleef 1v1', 'color': 'aqua'}]),
        ('a6', [{'text': '5 ', 'color': 'dark_gray'}, {'text': 'Duell 1v1', 'color': 'red'}]),
        ('a7', {'text': '  '}),
        ('a8', [{'text': 'Siege: ', 'color': 'dark_gray'}, {'text': 'Tab-Liste', 'color': 'gray'}])]
for i, (e, t) in enumerate(rows):
    side += [f'scoreboard players set {e} mg_side {len(rows) - i}', f'scoreboard players display name {e} mg_side {tc(t)}']
fn('hub/sidebar', side)

# ------------------------------------------------------------------ tick
fn('tick', [
    'scoreboard players enable @a mg_aktion',
    f'execute as @a[tag=!mg_seen] run function {NS}:hub/first',
    f'execute as @a[scores={{mg_leave=1..}}] run function {NS}:hub/rejoin',
    f'execute as @a[scores={{mg_click=1..}}] run function {NS}:hub/click',
    f'execute as @a[tag=mg_hub] run function {NS}:hub/keep',
    'scoreboard players add #itick mg 1',
    f'execute if score #itick mg matches 10.. run function {NS}:hub/sweep',
    f'execute if score #rush mg matches 1.. run function {NS}:rush/tick',
    *[f'execute if score #{k} mg matches 1.. run function {NS}:{k}/tick' for k in DUELS],
    *[f'execute if score #{k} mg matches 0 if entity @a[tag=mg_q_{k}] run function {NS}:q/try_{k}' for k in DUELS],
])

# ------------------------------------------------------------------ PARKOUR-RUSH (24 modules, private lanes, progress board)
YLO, YHI = -25, 40
def lane_box(mi, L):
    return (map_x(mi) - 12, lane_z(L) - 48, map_x(mi) + MAXLEN + 12, lane_z(L) + 48)
for mi, (t, m) in enumerate(zip(THEMES, MAPGEN)):
    b = []
    for sx in range(-10, MAXLEN + 1, 6):
        b.append(f'fill ~{sx} ~{YLO} ~-40 ~{sx + 5} ~{YHI} ~40 minecraft:air')
    for (bx, by, bz), st in sorted(m['blocks'].items()):
        b.append(f'setblock ~{bx} ~{by} ~{bz} minecraft:{st}')
    for (hx_, hy_, hz_, text, sc) in m['holos']:
        b.append(f'summon minecraft:text_display ~{hx_} ~{hy_} ~{hz_} {{Tags:["mg_holo","mg_lh"],billboard:"center",background:0,shadow:true,'
                 f'text:{tc(text)},transformation:{{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[{sc}f,{sc}f,{sc}f]}}}}')
    fn(f'build/lane_m{mi + 1}', b)
    checks = []
    for ci, (cx, cy, cz, chs) in enumerate(m['cps']):
        n = ci + 1
        r = 4 if n == MODULES else 3
        a = chs[0]
        args = f'n:{n},tier:"{TIER(n)}",ax:{r + a[0]},ay:{a[1]},az:{r + a[2]}'
        if len(chs) > 1:
            bb = chs[1]
            args += f',bx:{r + bb[0]},by:{bb[1]},bz:{r + bb[2]}'
            fnname = 'reach2'
        else:
            fnname = 'reach1'
        checks.append(f'execute if score @s mg_cp matches {ci} positioned ~{cx - r} ~{cy} ~{cz - r} if entity @s[dx={2 * r},dy=3,dz={2 * r}] run function {NS}:rush/{fnname} {{{args}}}')
    fn(f'rush/cp_m{mi + 1}', checks)

# one-time background build of every lane (5 maps x LANES), one lane at a time
JOBS = [(mi, L) for mi in range(len(THEMES)) for L in range(1, LANES + 1)]
nxt = ['scoreboard players add #bq mg 1']
for j, (mi, L) in enumerate(JOBS):
    x1, z1, x2, z2 = lane_box(mi, L)
    nxt.append(f'execute if score #bq mg matches {j + 1} run return run function {NS}:build/q{j + 1}')
    fn(f'build/q{j + 1}', [f'{OW} forceload add {x1} {z1} {x2} {z2}', f'schedule function {NS}:build/q{j + 1}_try 20t'])
    tries = ' '.join(f'if loaded {px} {Y} {lane_z(L)}' for px in (map_x(mi), map_x(mi) + MAXLEN // 3, map_x(mi) + 2 * MAXLEN // 3, map_x(mi) + MAXLEN))
    fn(f'build/q{j + 1}_try', [
        f'execute in minecraft:overworld {tries} run return run function {NS}:build/q{j + 1}_do',
        f'schedule function {NS}:build/q{j + 1}_try 20t'])
    fn(f'build/q{j + 1}_do', [
        f'execute in minecraft:overworld positioned {map_x(mi)} {Y} {lane_z(L)} run function {NS}:build/lane_m{mi + 1}',
        f'{OW} forceload remove {x1} {z1} {x2} {z2}',
        f'scoreboard players set #lanes_done mg {j + 1}',
        f'schedule function {NS}:build/lane_next 2t'])
nxt.append(f'scoreboard players set #lanes mg {BUILD_VERSION}')
nxt.append(f'tellraw @a {msg({"text": "Alle Parkour-Strecken sind fertig gebaut.", "color": "green"})}')
fn('build/lane_next', nxt)
fn('build/lane_resume', ['scoreboard players remove #bq mg 1', 'execute if score #bq mg matches ..-1 run scoreboard players set #bq mg 0', f'function {NS}:build/lane_next'])

fn('rush/request', [
    f'execute unless score #lanes mg matches {BUILD_VERSION} run return run tellraw @s {msg({"text": "Die Strecken werden noch gebaut (", "color": "red"}, {"score": {"name": "#lanes_done", "objective": "mg"}, "color": "white"}, {"text": f"/{len(JOBS)}). Gleich fertig!", "color": "red"})}',
    f'execute if score #rush mg matches 1.. run return run tellraw @s {msg({"text": "Parkour-Rush läuft schon.", "color": "red"})}',
    f'tellraw @a {msg({"selector": "@s", "color": "white"}, {"text": " startet ", "color": "gray"}, {"text": "PARKOUR-RUSH", "color": "green", "bold": True}, {"text": " für alle in der Lobby!", "color": "gray"})}',
    'scoreboard players set #rush mg 1', 'scoreboard players set #cd mg 5', 'scoreboard players set #cdt mg 0',
    'scoreboard players set #L mg 0', 'scoreboard players set @a mg_lane 0',
    f'execute as @a[tag=mg_hub] run function {NS}:rush/lane_assign',
    f'function {NS}:rush/cd_show',
])
fn('rush/lane_assign', ['scoreboard players add #L mg 1', 'scoreboard players operation @s mg_lane = #L mg',
                        'scoreboard players remove @s mg_lane 1', f'scoreboard players operation @s mg_lane %= #{LANES} mg',
                        'scoreboard players add @s mg_lane 1'])
fn('rush/cd_show', ['title @a[tag=mg_hub] times 0 25 5',
                    f'title @a[tag=mg_hub] title {tc({"score": {"name": "#cd", "objective": "mg"}, "color": "green", "bold": True})}',
                    f'title @a[tag=mg_hub] subtitle {tc({"text": "Parkour-Rush · 24 Inseln · 15 Minuten", "color": "gray"})}',
                    'execute as @a[tag=mg_hub] at @s run playsound minecraft:block.note_block.hat master @s ~ ~ ~ 1 1'])
fn('rush/cd_tick', ['scoreboard players add #cdt mg 1',
                    'execute if score #cdt mg matches 20.. run scoreboard players remove #cd mg 1',
                    'execute if score #cdt mg matches 20.. run scoreboard players set #cdt mg 0',
                    f'execute if score #cd mg matches ..0 run return run function {NS}:rush/start',
                    f'execute if score #cdt mg matches 0 run function {NS}:rush/cd_show'])
start = [
    'tag @a[tag=mg_hub,scores={mg_lane=1..}] add mg_rush', 'tag @a[tag=mg_rush] remove mg_hub',
    f'execute as @a[tag=mg_rush] run function {NS}:q/leave_all',
    'clear @a[tag=mg_rush]', 'effect clear @a[tag=mg_rush]', 'gamemode adventure @a[tag=mg_rush]',
    'scoreboard players set @a[tag=mg_rush] mg_cp 0',
    f'execute store result score #map mg run random value 1..{len(THEMES)}',
    'scoreboard players reset * mg_prog', 'scoreboard players set @a[tag=mg_rush] mg_prog 0',
    'scoreboard objectives setdisplay sidebar mg_prog',
]
for mi in range(len(THEMES)):
    for L in range(1, LANES + 1):
        sel = f'@a[tag=mg_rush,scores={{mg_lane={L}}}]'
        c = f'execute if score #map mg matches {mi + 1} run'
        start += [f'{c} {OW} tp {sel} {map_x(mi)} {Y + 1} {lane_z(L)} -90 0',
                  f'{c} execute as {sel} run {OW} spawnpoint @s {map_x(mi)} {Y + 1} {lane_z(L)}',
                  f'{c} scoreboard players set {sel} mg_cx {map_x(mi)}',
                  f'{c} scoreboard players set {sel} mg_cz {lane_z(L)}']
start += [
    f'scoreboard players set @a[tag=mg_rush] mg_cy {Y + 1}',
    'effect give @a[tag=mg_rush] minecraft:saturation infinite 0 true',
    'effect give @a[tag=mg_rush] minecraft:resistance infinite 4 true',
    'scoreboard players set #rush mg 2', 'scoreboard players set #t mg 0', f'scoreboard players set #left mg {RUSH_TIME}',
    'scoreboard players set #finished mg 0',
    f'bossbar set {NS}:rush players @a[tag=mg_rush]', f'bossbar set {NS}:rush visible true', f'bossbar set {NS}:rush max {RUSH_TIME}',
    'title @a[tag=mg_rush] times 5 50 10',
    f'title @a[tag=mg_rush] title {tc({"text": "LOS!", "color": "green", "bold": True})}',
    *[f'execute if score #map mg matches {mi + 1} run title @a[tag=mg_rush] subtitle ' + tc([{'text': 'Map: ', 'color': 'gray'}, {'text': t['name'], 'color': t['color'], 'bold': True}, {'text': ' · 24 Inseln', 'color': 'white'}]) for mi, t in enumerate(THEMES)],
    *[f'execute if score #map mg matches {mi + 1} run tellraw @a[tag=mg_rush] ' + msg({'text': 'Map: ', 'color': 'gray'}, {'text': t['name'], 'color': t['color'], 'bold': True}, {'text': ' – jeder hat seine eigene Strecke. Auf jeder Insel wartet eine Truhe, je weiter du kommst, desto besser der Loot. Rechts siehst du, wie weit die anderen sind.', 'color': 'gray'}) for mi, t in enumerate(THEMES)],
    'execute as @a[tag=mg_rush] at @s run playsound minecraft:entity.player.levelup master @s ~ ~ ~ 1 1',
]
fn('rush/start', start)
fn('rush/tick', [
    f'execute if score #rush mg matches 1 run function {NS}:rush/cd_tick',
    'execute unless score #rush mg matches 2.. run return 0',
    f'execute if score #rush mg matches 2 run function {NS}:rush/parkour_tick',
    f'execute if score #rush mg matches 3 run function {NS}:rush/arena_tick',
])
fn('rush/parkour_tick', [
    *[f'execute if score #map mg matches {mi + 1} as @a[tag=mg_rush,scores={{mg_lane={L}}}] in minecraft:overworld positioned {map_x(mi)} {Y} {lane_z(L)} run function {NS}:rush/cp_m{mi + 1}'
      for mi in range(len(THEMES)) for L in range(1, LANES + 1)],
    *[f'execute if score #map mg matches {mi + 1} as @a[tag=mg_rush] at @s if entity @s[y=-64,dy={Y + m["miny"] - 10 + 64}] run function {NS}:rush/back'
      for mi, m in enumerate(MAPGEN)],
    'scoreboard players add #t mg 1',
    f'execute if score #t mg matches 20.. run function {NS}:rush/second',
])
reach_common = [
    '$scoreboard players set @s mg_cp $(n)',
    'scoreboard players operation @s mg_prog = @s mg_cp',
    'execute store result score @s mg_cx run data get entity @s Pos[0]',
    'execute store result score @s mg_cy run data get entity @s Pos[1]',
    'execute store result score @s mg_cz run data get entity @s Pos[2]',
    'execute at @s run spawnpoint @s ~ ~ ~',
    '$setblock ~$(ax) ~$(ay) ~$(az) minecraft:chest[facing=west]{LootTable:"mg:$(tier)"}',
]
reach_tail = [
    f'execute if score @s mg_cp matches {NCP} run return run function {NS}:rush/finish_player',
    f'$title @s actionbar [{{"text":"Insel $(n)/{NCP} ✔ ","color":"yellow","bold":true}},{{"text":"Truhe geöffnet für dich bereit","color":"gold","bold":false}}]',
    'playsound minecraft:entity.experience_orb.pickup master @s ~ ~ ~ 1 1',
    'scoreboard players operation #m6 mg = @s mg_cp', 'scoreboard players operation #m6 mg %= #6 mg',
    f'$execute if score #m6 mg matches 0 run tellraw @a[tag=mg_rush] {tc([PREFIX, {"selector": "@s", "color": "white"}, {"text": " ist auf Insel $(n)/" + str(NCP) + "!", "color": "yellow"}])}',
]
fn('rush/reach1', reach_common + reach_tail)
fn('rush/reach2', reach_common + ['$setblock ~$(bx) ~$(by) ~$(bz) minecraft:chest[facing=west]{LootTable:"mg:$(tier)"}'] + reach_tail)
fn('rush/back', [
    'execute store result storage mg:tmp p.x int 1 run scoreboard players get @s mg_cx',
    'execute store result storage mg:tmp p.y int 1 run scoreboard players get @s mg_cy',
    'execute store result storage mg:tmp p.z int 1 run scoreboard players get @s mg_cz',
    f'function {NS}:rush/back_tp with storage mg:tmp p',
    'playsound minecraft:entity.enderman.teleport master @s ~ ~ ~ 0.6 1',
])
fn('rush/back_tp', ['$execute in minecraft:overworld run tp @s $(x).5 $(y) $(z).5'])
fn('rush/finish_player', [
    'title @s times 5 40 10',
    f'title @s title {tc({"text": "ZIEL!", "color": "aqua", "bold": True})}',
    f'title @s subtitle {tc({"text": "Hol dir die 2 Truhen!", "color": "gold"})}',
    'playsound minecraft:ui.toast.challenge_complete master @s ~ ~ ~ 1 1.2',
    f'execute if score #finished mg matches 0 if score #left mg matches {FINISH_GRACE + 1}.. run scoreboard players set #left mg {FINISH_GRACE}',
    'scoreboard players set #finished mg 1',
    f'tellraw @a[tag=mg_rush] {msg({"selector": "@s", "color": "aqua", "bold": True}, {"text": " ist im Ziel! ", "color": "white"}, {"text": "Arena in ", "color": "gray"}, {"score": {"name": "#left", "objective": "mg"}, "color": "red"}, {"text": " Sekunden!", "color": "gray"})}',
])
def tbar(zero):
    return tc([{'text': 'Parkour-Rush', 'color': 'green', 'bold': True}, {'text': '   Arena in ', 'color': 'white'},
               {'score': {'name': '#lm', 'objective': 'mg'}, 'color': 'white'}, {'text': ':0' if zero else ':', 'color': 'white'},
               {'score': {'name': '#ls', 'objective': 'mg'}, 'color': 'white'}])
fn('rush/second', [
    'scoreboard players set #t mg 0', 'scoreboard players remove #left mg 1',
    'scoreboard players operation #lm mg = #left mg', 'scoreboard players operation #lm mg /= #60 mg',
    'scoreboard players operation #ls mg = #left mg', 'scoreboard players operation #ls mg %= #60 mg',
    f'execute if score #ls mg matches 10.. run bossbar set {NS}:rush name {tbar(False)}',
    f'execute if score #ls mg matches ..9 run bossbar set {NS}:rush name {tbar(True)}',
    f'execute store result bossbar {NS}:rush value run scoreboard players get #left mg',
    f'bossbar set {NS}:rush players @a[tag=mg_rush]',
    f'execute as @a[tag=mg_rush,scores={{mg_cp=..{NCP - 1}}}] run title @s actionbar [{{"text":"Insel ","color":"gray"}},{{"score":{{"name":"@s","objective":"mg_cp"}},"color":"yellow","bold":true}},{{"text":"/{NCP}","color":"gray"}}]',
    'execute if score #left mg matches 1..5 as @a[tag=mg_rush] at @s run playsound minecraft:block.note_block.pling master @s ~ ~ ~ 1 1.5',
    'execute if score #left mg matches 60 run tellraw @a[tag=mg_rush] ' + msg({'text': 'Noch 1 Minute bis zur Arena!', 'color': 'red', 'bold': True}),
    f'execute unless entity @a[tag=mg_rush] run return run function {NS}:rush/stop',
    f'execute if score #left mg matches ..0 run function {NS}:rush/to_arena',
])

fn('rush/to_arena', [
    'scoreboard players set #rush mg 3', 'scoreboard players set #grace mg 100',
    'effect clear @a[tag=mg_rush] minecraft:resistance', 'effect clear @a[tag=mg_rush] minecraft:saturation',
    'tag @a[tag=mg_rush] add mg_fight',
    f'{OW} tp @a[tag=mg_fight] {ARENA[0]} {Y + 1} {ARENA[2]}',
    f'execute in minecraft:overworld run spreadplayers {ARENA[0]} {ARENA[2]} 6 13 under {Y + 3} false @a[tag=mg_fight]',
    f'execute as @a[tag=mg_fight] run {OW} spawnpoint @s {HUB[0]} {HUB[1] + 1} {HUB[2]}',
    'scoreboard players operation @a[tag=mg_fight] mg_deaths = #zero mg',
    'effect give @a[tag=mg_fight] minecraft:resistance 5 4 true',
    'effect give @a[tag=mg_fight] minecraft:instant_health 1 10 true',
    f'bossbar set {NS}:rush name {tc({"text": "ARENA – wer zuletzt steht, gewinnt!", "color": "red", "bold": True})}',
    f'bossbar set {NS}:rush color red', f'bossbar set {NS}:rush value {RUSH_TIME}',
    'title @a[tag=mg_fight] times 5 40 10',
    f'title @a[tag=mg_fight] title {tc({"text": "ARENA!", "color": "red", "bold": True})}',
    f'title @a[tag=mg_fight] subtitle {tc({"text": "5 Sekunden Schutz, dann kämpfen", "color": "white"})}',
    'execute as @a[tag=mg_fight] at @s run playsound minecraft:entity.ender_dragon.growl master @s ~ ~ ~ 0.7 1.2',
])
fn('rush/arena_tick', [
    'scoreboard players remove #grace mg 1',
    f'execute as @a[tag=mg_fight,scores={{mg_deaths=1..}}] run function {NS}:rush/out',
    f'execute as @a[tag=mg_fight] at @s if entity @s[y=-64,dy={Y - 6 + 64}] run function {NS}:rush/out_fall',
    'scoreboard players set #alive mg 0',
    'execute as @a[tag=mg_fight] run scoreboard players add #alive mg 1',
    f'execute if score #alive mg matches ..1 run function {NS}:rush/end',
])
fn('rush/out', [
    'scoreboard players set @s mg_deaths 0',
    f'tellraw @a[tag=mg_rush] {msg({"selector": "@s", "color": "white"}, {"text": " ist raus!", "color": "red"})}',
    'tag @s remove mg_fight', f'function {NS}:hub/enter',
])
fn('rush/out_fall', ['clear @s', f'function {NS}:rush/out'])
fn('rush/end', [
    f'execute as @a[tag=mg_fight] run tellraw @a {msg({"selector": "@s", "color": "gold", "bold": True}, {"text": " gewinnt Parkour-Rush!", "color": "white"})}',
    'scoreboard players add @a[tag=mg_fight] mg_wins 1',
    'title @a[tag=mg_rush] times 10 60 20',
    f'execute as @a[tag=mg_fight] run title @a[tag=mg_rush] title [{{"selector":"@s","color":"gold","bold":true}}]',
    f'title @a[tag=mg_rush] subtitle {tc({"text": "gewinnt Parkour-Rush!", "color": "white"})}',
    'execute as @a[tag=mg_fight] at @s run summon minecraft:firework_rocket ~ ~1 ~ {LifeTime:20,FireworksItem:{id:"minecraft:firework_rocket",count:1,components:{"minecraft:fireworks":{flight_duration:1,explosions:[{shape:"large_ball",colors:[I;16766720,5635925],has_twinkle:true}]}}}}',
    'execute as @a at @s run playsound minecraft:ui.toast.challenge_complete master @s ~ ~ ~ 1 1',
    f'function {NS}:rush/stop',
])
fn('rush/stop', [
    'scoreboard players set #rush mg 0', f'bossbar set {NS}:rush visible false', f'bossbar set {NS}:rush color green',
    'scoreboard objectives setdisplay sidebar mg_side',
    f'execute as @a[tag=mg_rush] run function {NS}:hub/enter',
    f'{OW} kill @e[type=minecraft:item,x={ARENA[0] - 30},dx=60,y={Y - 10},dy=40,z={ARENA[2] - 30},dz=60]',
    f'{OW} kill @e[type=minecraft:item,x={map_x(0) - 20},dx={map_x(len(THEMES) - 1) - map_x(0) + MAXLEN + 40},y={Y - 40},dy=110,z={lane_z(1) - 60},dz={lane_z(LANES) - lane_z(1) + 120}]',
])

# ------------------------------------------------------------------ 1v1 (queue, rounds, best of 3)
KITS = {
    'sumo': [],
    'spleef': ['give @s minecraft:diamond_shovel[minecraft:can_break={blocks:"minecraft:snow_block"},minecraft:enchantments={"minecraft:efficiency":5},minecraft:unbreakable={}]'],
    'duell': ['item replace entity @s armor.head with minecraft:iron_helmet', 'item replace entity @s armor.chest with minecraft:iron_chestplate',
              'item replace entity @s armor.legs with minecraft:iron_leggings', 'item replace entity @s armor.feet with minecraft:iron_boots',
              'item replace entity @s hotbar.0 with minecraft:iron_sword', 'item replace entity @s hotbar.1 with minecraft:bow',
              'item replace entity @s hotbar.2 with minecraft:cooked_beef 8', 'item replace entity @s weapon.offhand with minecraft:shield',
              'item replace entity @s inventory.0 with minecraft:arrow 16'],
}
for k, (name, (cx, cy, cz), color) in DUELS.items():
    off = {'sumo': 3, 'spleef': 6, 'duell': 9}[k]
    fn(f'q/toggle_{k}', [
        f'execute if entity @s[tag=mg_q_{k}] run return run function {NS}:q/leave_{k}',
        f'function {NS}:q/leave_all', f'tag @s add mg_q_{k}',
        f'tellraw @s {msg({"text": "Warteschlange ", "color": "gray"}, {"text": name, "color": color, "bold": True}, {"text": " – sobald ein Gegner dabei ist, geht es los. Nochmal klicken = raus.", "color": "gray"})}',
        f'tellraw @a[tag=mg_hub,tag=!mg_q_{k}] {msg({"selector": "@s", "color": "white"}, {"text": " wartet auf einen Gegner für ", "color": "gray"}, {"text": name, "color": color, "bold": True}, {"text": " – ", "color": "gray"}, {"text": "[Annehmen]", "color": "green", "click_event": {"action": "run_command", "command": f"/trigger mg_aktion set {list(DUELS).index(k) + 1}"}})}',
    ])
    fn(f'q/leave_{k}', [f'tag @s remove mg_q_{k}', f'tellraw @s {msg({"text": "Warteschlange " + name + " verlassen.", "color": "gray"})}'])
    fn(f'q/try_{k}', [
        f'execute unless entity @a[tag=mg_q_{k},tag=mg_hub] run return 0',
        f'execute store result score #n mg if entity @a[tag=mg_q_{k},tag=mg_hub]',
        'execute if score #n mg matches ..1 run return 0',
        f'tag @r[tag=mg_q_{k},tag=mg_hub] add mg_p1',
        f'tag @r[tag=mg_q_{k},tag=mg_hub,tag=!mg_p1] add mg_p2',
        f'tag @a[tag=mg_p1] add mg_duel_{k}', f'tag @a[tag=mg_p2] add mg_duel_{k}',
        f'tag @a[tag=mg_duel_{k}] remove mg_q_{k}', f'tag @a[tag=mg_duel_{k}] remove mg_hub', f'tag @a[tag=mg_duel_{k}] add mg_duel',
        f'scoreboard players set @a[tag=mg_duel_{k}] mg_round 0',
        f'scoreboard players set #{k} mg 1',
        f'tellraw @a {msg({"selector": "@a[tag=mg_p1,tag=mg_duel_" + k + "]", "color": "white"}, {"text": " vs ", "color": "gray"}, {"selector": "@a[tag=mg_p2,tag=mg_duel_" + k + "]", "color": "white"}, {"text": "  –  " + name, "color": color, "bold": True})}',
        f'function {NS}:{k}/round',
    ])
    fn(f'{k}/round', [
        f'execute as @a[tag=mg_duel_{k}] run function {NS}:{k}/kit',
        f'{OW} tp @a[tag=mg_duel_{k},tag=mg_p1] {cx - off} {cy + 1} {cz} -90 0',
        f'{OW} tp @a[tag=mg_duel_{k},tag=mg_p2] {cx + off} {cy + 1} {cz} 90 0',
        *( [f'function {NS}:spleef/reset_floor'] if k == 'spleef' else [] ),
        f'scoreboard players set #{k}_cd mg 60',
        f'scoreboard players set #{k} mg 1',
        'title @a[tag=mg_duel_' + k + '] times 0 30 10',
        f'title @a[tag=mg_duel_{k}] title {tc({"text": "Runde", "color": color, "bold": True})}',
        f'title @a[tag=mg_duel_{k}] subtitle [{{"score":{{"name":"@a[tag=mg_p1,tag=mg_duel_{k}]","objective":"mg_round"}},"color":"white"}},{{"text":" : ","color":"gray"}},{{"score":{{"name":"@a[tag=mg_p2,tag=mg_duel_{k}]","objective":"mg_round"}},"color":"white"}}]',
    ])
    fn(f'{k}/kit', ['clear @s', 'effect clear @s', 'effect give @s minecraft:instant_health 1 10 true', 'effect give @s minecraft:saturation 1 20 true',
                    'gamemode adventure @s', 'scoreboard players set @s mg_deaths 0',
                    f'{OW} spawnpoint @s {HUB[0]} {HUB[1] + 1} {HUB[2]}', 'effect give @s minecraft:slowness 3 255 true',
                    'effect give @s minecraft:resistance 3 4 true'] + KITS[k])
    tick = [
        f'execute if score #{k}_cd mg matches 1.. run scoreboard players remove #{k}_cd mg 1',
        f'execute if score #{k}_cd mg matches 1.. run return 0',
        f'execute if score #{k} mg matches 1 run title @a[tag=mg_duel_{k}] actionbar {tc({"text": "LOS!", "color": color, "bold": True})}',
        f'scoreboard players set #{k} mg 2',
        # a player left the game or the hub took him -> forfeit
        f'execute store result score #n mg if entity @a[tag=mg_duel_{k}]',
        f'execute if score #n mg matches ..1 run return run function {NS}:{k}/forfeit',
        f'execute as @a[tag=mg_duel_{k},scores={{mg_deaths=1..}}] run function {NS}:{k}/lose',
        f'execute as @a[tag=mg_duel_{k}] at @s if entity @s[y=-64,dy={Y - 4 + 64}] run function {NS}:{k}/lose',
    ]
    fn(f'{k}/tick', tick)
    fn(f'{k}/lose', [
        f'execute if score #{k} mg matches ..1 run return 0',
        'scoreboard players set @s mg_deaths 0',
        f'tag @a[tag=mg_duel_{k}] remove mg_rw', f'tag @a[tag=mg_duel_{k}] add mg_rw', 'tag @s remove mg_rw',
        f'scoreboard players add @a[tag=mg_rw,tag=mg_duel_{k}] mg_round 1',
        f'tellraw @a[tag=mg_duel_{k}] {msg({"selector": "@a[tag=mg_rw,tag=mg_duel_" + k + "]", "color": "white"}, {"text": " gewinnt die Runde!", "color": color})}',
        f'execute as @a[tag=mg_duel_{k}] at @s run playsound minecraft:entity.experience_orb.pickup master @s ~ ~ ~ 1 1',
        f'execute if entity @a[tag=mg_rw,tag=mg_duel_{k},scores={{mg_round=2..}}] run return run function {NS}:{k}/win',
        f'scoreboard players set #{k} mg 1',
        f'function {NS}:{k}/round',
    ])
    fn(f'{k}/win', [
        f'scoreboard players add @a[tag=mg_rw,tag=mg_duel_{k}] mg_wins 1',
        f'tellraw @a {msg({"selector": "@a[tag=mg_rw,tag=mg_duel_" + k + "]", "color": "gold", "bold": True}, {"text": " gewinnt " + name + " (2:", "color": "white"}, {"score": {"name": "@a[tag=!mg_rw,tag=mg_duel_" + k + "]", "objective": "mg_round"}, "color": "white"}, {"text": ")", "color": "white"})}',
        f'title @a[tag=mg_duel_{k}] times 10 50 15',
        f'title @a[tag=mg_duel_{k},tag=mg_rw] title {tc({"text": "SIEG!", "color": "gold", "bold": True})}',
        f'title @a[tag=mg_duel_{k},tag=!mg_rw] title {tc({"text": "Verloren", "color": "red", "bold": True})}',
        'execute as @a[tag=mg_rw] at @s run summon minecraft:firework_rocket ~ ~1 ~ {LifeTime:20,FireworksItem:{id:"minecraft:firework_rocket",count:1,components:{"minecraft:fireworks":{flight_duration:1,explosions:[{shape:"star",colors:[I;16766720],has_twinkle:true}]}}}}',
        f'function {NS}:{k}/stop',
    ])
    fn(f'{k}/forfeit', [
        f'execute as @a[tag=mg_duel_{k}] run tellraw @a {msg({"selector": "@s", "color": "gold"}, {"text": " gewinnt " + name + " – Gegner ist weg.", "color": "white"})}',
        f'scoreboard players add @a[tag=mg_duel_{k}] mg_wins 1',
        f'function {NS}:{k}/stop',
    ])
    fn(f'{k}/stop', [
        f'scoreboard players set #{k} mg 0',
        f'execute as @a[tag=mg_duel_{k}] run function {NS}:hub/enter',
        f'tag @a remove mg_duel_{k}', 'tag @a[tag=mg_hub] remove mg_rw',
        f'{OW} kill @e[type=minecraft:item,x={cx - 20},dx=40,y={cy - 10},dy=30,z={cz - 20},dz=40]',
        f'{OW} kill @e[type=minecraft:arrow,x={cx - 20},dx=40,y={cy - 10},dy=30,z={cz - 20},dz=40]',
        *( [f'function {NS}:spleef/reset_floor'] if k == 'spleef' else [] ),
    ])
# hub/enter clears duel state of a player that left mid-match
fn('q/leave_all', [*[f'tag @s remove mg_q_{k}' for k in DUELS], *[f'tag @s remove mg_duel_{k}' for k in DUELS]])
# accept via chat click
fn('hub/aktion', [*[f'execute if score @s mg_aktion matches {i + 1} if entity @s[tag=mg_hub] unless entity @s[tag=mg_q_{k}] run function {NS}:q/toggle_{k}' for i, k in enumerate(DUELS)],
                  'scoreboard players set @s mg_aktion 0'])
files[f'data/{NS}/function/tick.mcfunction'] = files[f'data/{NS}/function/tick.mcfunction'].replace(
    'scoreboard players enable @a mg_aktion\n',
    f'scoreboard players enable @a mg_aktion\nexecute as @a[scores={{mg_aktion=1..}}] run function {NS}:hub/aktion\n')
fn('init_zero', ['scoreboard players set #zero mg 0'])
files[f'data/{NS}/function/load.mcfunction'] += 'scoreboard players set #zero mg 0\n'

# ------------------------------------------------------------------ write
if os.path.exists(ROOT):
    shutil.rmtree(ROOT)
for path, content in files.items():
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(content)
zpath = os.path.join(OUT, 'minigames.zip')
with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
    for path, content in files.items():
        z.writestr(path, content)
print(f'{len(files)} files -> {zpath}')
