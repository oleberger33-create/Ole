# Dropper: falling-parkour race through 4 vertical shafts (~67 blocks deep each).
# Every player falls in a private copy of the course (8 slots, 30 blocks apart along z); the 4 levels sit side by side
# along x. Land on anything that is not water -> back onto the start ledge of the current level. Splash into the pool
# at the bottom -> next level. First through all 4 levels wins; after 5 minutes the furthest player (fewest fails) wins.
_K = 'dropper'
DX, DY, DZ = 84000, Y, 0
_T, _AL = 'mg_dropper', 'mg_al_dropper'
_RACE = f'@a[tag={_AL}]'
_GO = 120                              # tick of "LOS!" (after the 3-2-1 countdown)
_LIMIT = _GO + 6000                    # 5 minutes
_SLOTS = 8
_B = DY - 6                            # shaft floor (y94); pool water y95..97
_L = DY + 64                           # start ledge block (y164), feet at y165
_R = _L + 5                            # glass roof (y169)
_BUILD_V = 2
_PRED = 'type' if MIN_FORMAT >= 121 else 'condition'
_GRAV = 0.04                           # half gravity inside the shafts: ~3.6 s per drop, enough time to steer around the obstacles


def _lx(l):
    return DX - 45 + 30 * l


def _sz(s):
    return DZ - 105 + 30 * s


# ---- level data. Cells (i, j) in 0..12 map to x = cx-6+i, z = cz-6+j; the ledge covers i 0..2 at depth 0.
# layer: (depth below the ledge block, block, base 'full'|'empty', open rects, solid rects, thickness)
_LEVELS = [
    dict(name='Farbschacht', col='yellow', wall='white_concrete', band=None, corner='quartz_pillar', light='sea_lantern',
         ledge='smooth_quartz', floor='white_concrete', poolfloor='sea_lantern', rim='yellow_concrete',
         bands=['red_concrete', 'orange_concrete', 'yellow_concrete', 'lime_concrete', 'light_blue_concrete', 'purple_concrete'],
         pool=(3, 3, 9, 9),
         layers=[(8, 'red_concrete', 'full', [(3, 4, 7, 8)], [], 1),
                 (16, 'orange_concrete', 'full', [(4, 5, 8, 9)], [], 1),
                 (24, 'yellow_concrete', 'full', [(4, 3, 9, 10)], [(6, 6, 7, 7)], 1),
                 (33, 'lime_concrete', 'full', [(5, 4, 9, 8)], [], 1),
                 (42, 'light_blue_concrete', 'full', [(4, 3, 8, 7)], [], 1),
                 (51, 'purple_concrete', 'empty', [], [(0, 2, 12, 3), (0, 8, 12, 9)], 2)]),
    dict(name='Tiefsee', col='aqua', wall='prismarine_bricks', band='dark_prismarine', corner='dark_prismarine', light='sea_lantern',
         ledge='dark_prismarine', floor='prismarine', poolfloor='sea_lantern', rim='light_blue_concrete',
         pool=(7, 3, 10, 6),
         layers=[(7, 'cyan_stained_glass', 'full', [(4, 8, 7, 11)], [], 1),
                 (15, 'prismarine', 'full', [(5, 7, 8, 10)], [], 1),
                 (23, 'light_blue_stained_glass', 'full', [(4, 4, 10, 11)], [(6, 8, 8, 10)], 1),
                 (31, 'dark_prismarine', 'full', [(6, 4, 9, 8)], [], 1),
                 (40, 'cyan_stained_glass', 'full', [(7, 3, 9, 6)], [], 1),
                 (49, 'prismarine_bricks', 'full', [(6, 2, 11, 7)], [(8, 4, 9, 5)], 1)]),
    dict(name='Netherschlund', col='red', wall='polished_blackstone_bricks', band='gilded_blackstone', corner='obsidian', light='shroomlight',
         ledge='polished_blackstone', floor='blackstone', poolfloor='glowstone', rim='red_nether_bricks',
         pool=(8, 6, 11, 9),
         layers=[(6, 'nether_bricks', 'empty', [], [(0, 0, 4, 12), (7, 0, 8, 12), (11, 0, 12, 12)], 2),
                 (13, 'red_nether_bricks', 'full', [(5, 1, 8, 4)], [], 1),
                 (20, 'red_stained_glass', 'full', [(7, 2, 10, 5)], [], 1),
                 (28, 'nether_wart_block', 'full', [(6, 1, 11, 6)], [(8, 3, 9, 4)], 1),
                 (36, 'warped_wart_block', 'full', [(9, 4, 12, 7)], [], 1),
                 (45, 'red_stained_glass', 'full', [(8, 6, 11, 9)], [], 1),
                 (54, 'nether_bricks', 'full', [(7, 6, 12, 8)], [], 2)]),
    dict(name='Endkern', col='light_purple', wall='end_stone_bricks', band='purpur_block', corner='obsidian', light='pearlescent_froglight',
         ledge='purpur_block', floor='end_stone', poolfloor='pearlescent_froglight', rim='purpur_pillar',
         pool=(8, 6, 10, 8),
         layers=[(6, 'purpur_block', 'full', [(3, 9, 6, 12)], [], 1),
                 (12, 'magenta_stained_glass', 'full', [(4, 8, 7, 11)], [], 1),
                 (19, 'obsidian', 'full', [(6, 7, 8, 9)], [], 1),
                 (26, 'end_stone_bricks', 'full', [(4, 4, 10, 10)], [(6, 6, 8, 8)], 1),
                 (34, 'purple_stained_glass', 'full', [(8, 8, 10, 10)], [], 1),
                 (42, 'crying_obsidian', 'full', [(9, 7, 11, 9)], [], 1),
                 (50, 'magenta_stained_glass', 'full', [(8, 6, 10, 8)], [], 1),
                 (58, 'amethyst_block', 'empty', [], [(10, 7, 10, 7)], 1)]),
]
_NL = len(_LEVELS)


def _F(x1, y1, z1, x2, y2, z2, b, mode=''):
    return f'{OW} fill {x1} {y1} {z1} {x2} {y2} {z2} minecraft:{b}' + (f' {mode}' if mode else '')


def _mask(base, holes, solids):
    cells = {(i, j) for i in range(13) for j in range(13)} if base == 'full' else set()
    for i1, j1, i2, j2 in holes:
        cells -= {(i, j) for i in range(i1, i2 + 1) for j in range(j1, j2 + 1)}
    for i1, j1, i2, j2 in solids:
        cells |= {(i, j) for i in range(i1, i2 + 1) for j in range(j1, j2 + 1)}
    return cells


def _rects(cells):
    """Cover the mask with rectangles: runs along i per row j, merged over consecutive rows."""
    runs = {}
    for j in range(13):
        i = 0
        while i < 13:
            if (i, j) in cells:
                e = i
                while (e + 1, j) in cells:
                    e += 1
                runs.setdefault((i, e), []).append(j)
                i = e + 1
            else:
                i += 1
    out = []
    for (i1, i2), js in runs.items():
        s = p = js[0]
        for j in js[1:] + [None]:
            if j is not None and j == p + 1:
                p = j
                continue
            out.append((i1, s, i2, p))
            if j is not None:
                s = p = j
    return out


def _shaft(l):
    """Commands that build level l in slot 0 (fresh: the hollow shell clears the inside)."""
    lv = _LEVELS[l]
    cx, cz = _lx(l), _sz(0)
    x1, x2, z1, z2 = cx - 7, cx + 7, cz - 7, cz + 7
    out = [_F(x1, _B - 1, z1, x2, _B - 1, z2, 'air'), _F(x1, _R + 1, z1, x2, _R + 1, z2, 'air'),
           _F(x1, _B, z1, x2, _R, z2, lv['wall'], 'hollow')]
    # bands every 10 blocks (outer + inner face, the walls are 1 thick)
    for n, y in enumerate(range(_B + 6, _R - 3, 10)):
        blk = lv['bands'][n % len(lv['bands'])] if lv.get('bands') else lv['band']
        out.append(_F(x1, y, z1, x2, y, z2, blk, f'replace minecraft:{lv["wall"]}'))
    # corner pillars + light strips in the middle of every wall
    for x, z in ((x1, z1), (x1, z2), (x2, z1), (x2, z2)):
        out.append(_F(x, _B, z, x, _R, z, lv['corner']))
    for x, z in ((cx, z1), (cx, z2), (x1, cz), (x2, cz)):
        out.append(_F(x, _B + 1, z, x, _R - 1, z, lv['light']))
    for x, z in ((cx - 4, z1), (cx + 4, z1), (cx - 4, z2), (cx + 4, z2), (x1, cz - 4), (x1, cz + 4), (x2, cz - 4), (x2, cz + 4)):
        out.append(_F(x, _B + 3, z, x, _L - 4, z, lv['light']))
    # base: stepped plinth below the floor, crown on the roof
    out += [_F(x1 + 1, _B - 1, z1 + 1, x2 - 1, _B - 1, z2 - 1, lv['corner']),
            _F(x1 + 1, _R, z1 + 1, x2 - 1, _R, z2 - 1, 'glass'),
            _F(x1, _R + 1, z1, x2, _R + 1, z2, lv['corner'], 'outline'),
            _F(x1 + 1, _R + 1, z1 + 1, x2 - 1, _R + 1, z2 - 1, 'air')]
    for x, z in ((x1, z1), (x1, z2), (x2, z1), (x2, z2)):
        out.append(f'{OW} setblock {x} {_R + 2} {z} minecraft:end_rod')
    # pool: solid floor with a glowing water basin and a coloured rim
    pi1, pj1, pi2, pj2 = lv['pool']
    X = lambda i: cx - 6 + i
    Z = lambda j: cz - 6 + j
    out += [_F(cx - 6, _B + 1, cz - 6, cx + 6, _B + 3, cz + 6, lv['floor']),
            _F(X(pi1) - 1, _B + 3, Z(pj1) - 1, X(pi2) + 1, _B + 3, Z(pj2) + 1, lv['rim']),
            _F(X(pi1), _B, Z(pj1), X(pi2), _B, Z(pj2), lv['poolfloor']),
            _F(X(pi1), _B + 1, Z(pj1), X(pi2), _B + 3, Z(pj2), 'water')]
    # obstacles
    for d, blk, base, holes, solids, th in lv['layers']:
        y = _L - d
        for i1, j1, i2, j2 in _rects(_mask(base, holes, solids)):
            out.append(_F(X(i1), y - th + 1, Z(j1), X(i2), y, Z(j2), blk))
    # start ledge (3 deep along the west wall) with a warning edge
    out.append(_F(cx - 6, _L, cz - 6, cx - 4, _L, cz + 6, lv['ledge']))
    for j in range(13):
        out.append(f'{OW} setblock {cx - 4} {_L} {Z(j)} minecraft:{"yellow_concrete" if j % 2 == 0 else "black_concrete"}')
    return out


def _gate(blk):
    return [_F(_lx(0) - 3, _L + 1, _sz(s) - 6, _lx(0) - 3, _L + 4, _sz(s) + 6, blk) for s in range(_SLOTS)]


_shafts = []
for _l in range(_NL):
    _shafts += _shaft(_l)
for _l in range(_NL):
    _cx = _lx(_l)
    for _s in range(1, _SLOTS):
        _shafts.append(f'{OW} clone {_cx - 7} {_B - 1} {_sz(0) - 7} {_cx + 7} {_R + 2} {_sz(0) + 7} {_cx - 7} {_B - 1} {_sz(_s) - 7}')
_shafts.append(f'scoreboard players set #dropper_v mg {_BUILD_V}')
fn('dropper/shafts', _shafts)

_build = [f'kill @e[type=minecraft:text_display,tag=mg_dropperh]',
          # the 32 shafts are static (adventure mode, nothing can change them): rebuild only after a layout change or if a marker is missing
          f'execute unless score #dropper_v mg matches {_BUILD_V} run function {NS}:dropper/shafts',
          *[f'execute in minecraft:overworld unless block {_lx(_l) - 4} {_L} {_sz(_SLOTS - 1) - 6} minecraft:yellow_concrete run function {NS}:dropper/shafts' for _l in range(_NL)],
          f'execute in minecraft:overworld unless block {_lx(_NL - 1) - 6 + _LEVELS[-1]["pool"][0]} {_B + 3} {_sz(_SLOTS - 1) - 6 + _LEVELS[-1]["pool"][1]} minecraft:water run function {NS}:dropper/shafts',
          *_gate('light_blue_stained_glass')]
for _l, _lv in enumerate(_LEVELS):
    _build.append(holo('mg_dropperh', c5(_lx(_l)), _R + 4, c5(_sz(0) - 14),
                       [{'text': f'Level {_l + 1}\n', 'color': _lv['col'], 'bold': True}, {'text': _lv['name'], 'color': 'white', 'bold': False}], 3.0))
    for _s in range(_SLOTS):
        _build.append(holo('mg_dropperh', c5(_lx(_l)), _L + 3.5, c5(_sz(_s)),
                           [{'text': f'Level {_l + 1}/{_NL}\n', 'color': _lv['col'], 'bold': True}, {'text': _lv['name'], 'color': 'white', 'bold': False}], 0.9))
_build.append(holo('mg_dropperh', c5(DX), _R + 9, c5(_sz(0) - 14),
                   [{'text': 'DROPPER', 'color': 'gold', 'bold': True}], 5.0))

# ---- teleports onto the ledge of the player's current level (mg_dropper_l) in the player's slot (mg_dropper_s)
for _l in range(_NL):
    fn(f'dropper/tp{_l + 1}', [f'execute if score @s mg_dropper_s matches {_s} run {OW} tp @s {c5(_lx(_l) - 5)} {_L + 1} {c5(_sz(_s))} -90 25'
                               for _s in range(_SLOTS)])
fn('dropper/tp', [f'execute if score @s mg_dropper_l matches {_l + 1} run function {NS}:dropper/tp{_l + 1}' for _l in range(_NL)])

fn('dropper/assign', ['scoreboard players operation @s mg_dropper_s = #dropper_n mg', 'scoreboard players add #dropper_n mg 1'])

# ---- per player, every tick (only living racers)
fn('dropper/pl', [
    f'execute unless score #{_K} mg matches 2 run return 0',
    f'execute if score @s mg_deaths matches 1.. run return run function {NS}:dropper/died',
    f'execute if entity @s[y={_B - 2},dy=8] if block ~ ~ ~ minecraft:water run return run function {NS}:dropper/done',
    f'execute if entity @s[y={_B - 2},dy=8] if block ~ ~0.6 ~ minecraft:water run return run function {NS}:dropper/done',
    f'execute unless entity @s[x={DX - 60},y={_B - 4},z={DZ - 120},dx=120,dy={_R - _B + 6},dz=240] run return run function {NS}:dropper/fail',
    f'execute if entity @s[y={_L + 0.5},dy=8] run return 0',          # on the start ledge: safe
    f'execute if predicate {{{_PRED}:"minecraft:entity_properties",entity:"this",predicate:{{flags:{{is_on_ground:true}}}}}} run function {NS}:dropper/fail',
])
fn('dropper/fail', [
    'scoreboard players add @s mg_dropper_f 1',
    'particle minecraft:poof ~ ~0.5 ~ 0.4 0.4 0.4 0.05 20',
    'playsound minecraft:entity.player.big_fall master @s ~ ~ ~ 1 0.7',
    'playsound minecraft:block.note_block.bass master @s ~ ~ ~ 1 0.6',
    'title @s times 0 25 8', f'title @s title {tc({"text": "✖", "color": "red", "bold": True})}',
    f'title @s subtitle {tc([{"text": "Berührt! ", "color": "red", "bold": True}, {"text": "Nochmal von oben", "color": "gray"}])}',
    f'function {NS}:dropper/tp',
    'execute at @s run playsound minecraft:entity.enderman.teleport master @s ~ ~ ~ 0.6 1.3'])
fn('dropper/died', ['scoreboard players set @s mg_deaths 0', f'attribute @s minecraft:gravity base set {_GRAV}',
                    'effect give @s minecraft:saturation infinite 0 true', 'effect give @s minecraft:resistance infinite 4 true',
                    f'function {NS}:dropper/tp'])

_TIME = [{'score': {'name': '#dropper_mm', 'objective': 'mg'}, 'color': 'white'}, {'text': ':', 'color': 'white'},
         {'score': {'name': '#dropper_s10', 'objective': 'mg'}, 'color': 'white'}, {'score': {'name': '#dropper_s1', 'objective': 'mg'}, 'color': 'white'}]


def _clock(src):
    """#dropper_mm:#dropper_s10#dropper_s1 from a number of seconds in #dropper_c."""
    return [f'scoreboard players operation #dropper_c mg = {src}',
            'scoreboard players operation #dropper_mm mg = #dropper_c mg', 'scoreboard players operation #dropper_mm mg /= #60 mg',
            'scoreboard players operation #dropper_s1 mg = #dropper_c mg', 'scoreboard players operation #dropper_s1 mg %= #60 mg',
            'scoreboard players operation #dropper_s10 mg = #dropper_s1 mg', 'scoreboard players operation #dropper_s10 mg /= #10 mg',
            'scoreboard players operation #dropper_s1 mg %= #10 mg']


_done = ['scoreboard players add @s mg_dropper_l 1', 'scoreboard players add @s mg_coins 1',
         'particle minecraft:splash ~ ~1 ~ 0.6 0.4 0.6 0.2 40',
         f'execute if score @s mg_dropper_l matches {_NL + 1}.. run return run function {NS}:dropper/win',
         'playsound minecraft:entity.player.levelup master @s ~ ~ ~ 1 1.2',
         'playsound minecraft:entity.generic.splash master @s ~ ~ ~ 0.6 1',
         f'function {NS}:dropper/tp', 'title @s times 3 35 10']
for _l, _lv in enumerate(_LEVELS[1:], 2):
    _done += [f'execute if score @s mg_dropper_l matches {_l} run title @s title {tc({"text": f"Level {_l}", "color": _lv["col"], "bold": True})}',
              f'execute if score @s mg_dropper_l matches {_l} run title @s subtitle {tc([{"text": "✔ Geschafft!  ", "color": "green", "bold": True}, {"text": "Weiter: " + _lv["name"], "color": "white"}])}',
              f'execute if score @s mg_dropper_l matches {_l} run tellraw @a[tag={_T}] ' + msg(
                  {'selector': '@s', 'color': 'white'}, {'text': f' hat Level {_l - 1} geschafft ', 'color': 'gray'},
                  {'text': f'({_l - 1}/{_NL})', 'color': _lv['col']})]
_done.append(f'execute if score @s mg_dropper_l matches {_NL} as @a[tag={_T}] unless entity @s[scores={{mg_dropper_l={_NL}..}}] at @s run '
             'playsound minecraft:block.note_block.didgeridoo master @s ~ ~ ~ 0.8 0.8')
fn('dropper/done', _done)

fn('dropper/win', [
    'tag @s add mg_dropper_win',
    'scoreboard players operation #dropper_c mg = #dropper_t mg', f'scoreboard players remove #dropper_c mg {_GO}',
    'scoreboard players operation #dropper_c mg /= #20 mg', *_clock('#dropper_c mg'),
    f'tellraw @a[tag={_T}] ' + msg({'selector': '@s', 'color': 'gold', 'bold': True}, {'text': ' hat alle 4 Level geschafft! ', 'color': 'yellow'},
                                    {'text': '⏱ ', 'color': 'dark_gray'}, *_TIME),
    'playsound minecraft:ui.toast.challenge_complete master @s ~ ~ ~ 1 1',
    f'title @a[tag={_T}] times 5 60 15',
    f'title @s title {tc({"text": "SIEG!", "color": "gold", "bold": True})}',
    'title @s subtitle ' + tc([{'text': 'Alle 4 Level in ', 'color': 'white'}] + _TIME),
    f'title @a[tag={_T},tag=!mg_dropper_win] title {tc({"text": "Vorbei!", "color": "red", "bold": True})}',
    f'title @a[tag={_T},tag=!mg_dropper_win] subtitle ' + tc([{'selector': '@s', 'color': 'gold'}, {'text': ' war schneller', 'color': 'white'}]),
    f'function {NS}:dropper/end_go'])

# ---- end of the round (own end: wins/coins are booked here, nobody has to keep mg_al_dropper)
_W = f'@a[tag={_T},tag=mg_dropper_win]'
_rank = []
for _l in range(_NL + 1, 0, -1):
    _st = ({'text': '✔ Ziel', 'color': 'green', 'bold': True} if _l > _NL else
           {'text': f'Level {_l}/{_NL}', 'color': _LEVELS[_l - 1]['col']})
    _rank.append(f'execute as @a[tag={_T},scores={{mg_dropper_l={_l}}}] run tellraw @a[tag={_T}] ' + tc(
        [{'text': '   ▸ ', 'color': 'dark_gray'}, {'selector': '@s', 'color': 'white'}, {'text': '  '}, _st,
         {'text': '  ·  Fehlversuche: ', 'color': 'dark_gray'}, {'score': {'name': '@s', 'objective': 'mg_dropper_f'}, 'color': 'gray'}]))
fn('dropper/end_go', [
    f'tag @a[tag={_T}] remove {_AL}',
    f'scoreboard players add {_W} mg_wins 1', f'scoreboard players add {_W} mg_coins 15',
    f'execute as {_W} run tellraw @a ' + msg({'selector': '@s', 'color': 'gold', 'bold': True}, {'text': ' gewinnt Dropper!', 'color': 'white'}),
    f'execute unless entity {_W} run tellraw @a[tag={_T}] ' + msg({'text': 'Unentschieden – niemand hat ein Level geschafft.', 'color': 'gray'}),
    f'tellraw @a[tag={_T}] ' + tc({'text': ' Ergebnis:', 'color': 'gold', 'bold': True}),
    *_rank,
    f'execute as {_W} at @s run summon minecraft:firework_rocket ~ ~1 ~ {{LifeTime:20,FireworksItem:{{id:"minecraft:firework_rocket",count:1,components:{{"minecraft:fireworks":{{flight_duration:1,explosions:[{{shape:"large_ball",colors:[I;16766720],has_twinkle:true}}]}}}}}}}}',
    f'execute as @a[tag={_T}] at @s run playsound minecraft:block.note_block.chime master @s ~ ~ ~ 1 1',
    f'bossbar set {NS}:dropper visible false',
    f'scoreboard players set #{_K} mg 3', f'schedule function {NS}:{_K}/finish 100t'])
fn('dropper/end_time', [
    f'tellraw @a[tag={_T}] ' + msg({'text': 'Zeit abgelaufen! Wer am weitesten gekommen ist, gewinnt (bei Gleichstand: weniger Fehlversuche).', 'color': 'red'}),
    'scoreboard players set #dropper_best mg 0', 'scoreboard players set #dropper_minf mg 999999',
    f'execute as {_RACE} run scoreboard players operation #dropper_best mg > @s mg_dropper_l',
    f'execute as {_RACE} if score @s mg_dropper_l = #dropper_best mg run scoreboard players operation #dropper_minf mg < @s mg_dropper_f',
    f'execute if score #dropper_best mg matches 2.. as {_RACE} if score @s mg_dropper_l = #dropper_best mg if score @s mg_dropper_f = #dropper_minf mg run tag @s add mg_dropper_win',
    f'title @a[tag={_T}] times 5 60 15', f'title @a[tag={_T}] title {tc({"text": "Zeit um!", "color": "red", "bold": True})}',
    f'title @a[tag={_T}] subtitle {tc({"text": "", "color": "white"})}',
    f'function {NS}:dropper/end_go'])
fn('dropper/end_alone', [   # anti farming: a win by forfeit only counts if the last player already cleared a level
    f'execute as {_RACE} if score @s mg_dropper_l matches 2.. run tag @s add mg_dropper_win',
    f'execute unless entity {_W} run tellraw @a[tag={_T}] ' + msg({'text': 'Alle anderen haben das Spiel verlassen – ohne geschafftes Level gibt es keine Wertung.', 'color': 'gray'}),
    f'execute if entity {_W} run tellraw @a[tag={_T}] ' + msg({'text': 'Alle anderen haben das Spiel verlassen – du gewinnst!', 'color': 'yellow'}),
    f'title @a[tag={_T}] times 5 60 15', f'title @a[tag={_T}] title {tc({"text": "SIEG!", "color": "gold", "bold": True})}',
    f'title @a[tag={_T}] subtitle {tc({"text": "Alle anderen sind weg", "color": "white"})}',
    f'function {NS}:dropper/end_go'])

# ---- countdown on the ledge of level 1
def _cd(num, col, glass, pitch):
    return ([*_gate(glass), f'title @a[tag={_T}] times 0 22 4', f'title @a[tag={_T}] title {tc({"text": num, "color": col, "bold": True})}',
             f'title @a[tag={_T}] subtitle {tc({"text": "Gleich öffnet sich die Glaswand ...", "color": "gray"})}',
             f'execute as @a[tag={_T}] at @s run playsound minecraft:block.note_block.pling master @s ~ ~ ~ 1 {pitch}'])
fn('dropper/cd3', _cd('3', 'red', 'red_stained_glass', 0.7))
fn('dropper/cd2', _cd('2', 'gold', 'orange_stained_glass', 0.85))
fn('dropper/cd1', _cd('1', 'yellow', 'yellow_stained_glass', 1.0))
fn('dropper/go', [
    *_gate('air'),
    f'title @a[tag={_T}] times 0 30 10', f'title @a[tag={_T}] title {tc({"text": "LOS!", "color": "green", "bold": True})}',
    f'title @a[tag={_T}] subtitle {tc({"text": "Spring in den Schacht und triff das Wasser!", "color": "white"})}',
    f'execute as @a[tag={_T}] at @s run playsound minecraft:block.note_block.pling master @s ~ ~ ~ 1 2',
    f'tellraw @a[tag={_T}] ' + msg({'text': 'Tipp: ', 'color': 'yellow'}, {'text': 'Im Schacht fällst du langsamer – steuer schon früh, '
                                    'je tiefer du kommst, desto schneller wirst du. Durch Glas siehst du die nächste Lücke.', 'color': 'gray'})])

# ---- HUD: bossbar timer + per-player actionbar
_hud = ['scoreboard players set #dropper_rem mg ' + str(_LIMIT), 'scoreboard players operation #dropper_rem mg -= #dropper_t mg',
        'scoreboard players operation #dropper_rem mg /= #20 mg',
        f'execute if score #dropper_rem mg matches {(_LIMIT - _GO) // 20 + 1}.. run scoreboard players set #dropper_rem mg {(_LIMIT - _GO) // 20}',
        *_clock('#dropper_rem mg'),
        f'execute store result bossbar {NS}:dropper value run scoreboard players get #dropper_rem mg',
        f'bossbar set {NS}:dropper players @a[tag={_T}]', f'bossbar set {NS}:dropper visible true',
        f'execute if score #dropper_rem mg matches 31.. run bossbar set {NS}:dropper name ' + tc([{'text': 'Dropper  ', 'color': 'gold', 'bold': True}, {'text': '⏱ ', 'color': 'gray'}] + _TIME),
        f'execute if score #dropper_rem mg matches ..30 run bossbar set {NS}:dropper name ' + tc([{'text': 'Dropper  ', 'color': 'red', 'bold': True}, {'text': '⏱ ', 'color': 'red'}] + _TIME),
        f'execute if score #dropper_rem mg matches ..30 run bossbar set {NS}:dropper color red']
for _l, _lv in enumerate(_LEVELS, 1):
    _hud.append(f'execute as @a[tag={_AL},scores={{mg_dropper_l={_l}}}] run title @s actionbar ' + tc(
        [{'text': f'Level {_l}/{_NL} ', 'color': _lv['col'], 'bold': True}, {'text': _lv['name'], 'color': 'white'},
         {'text': '   ✖ ', 'color': 'dark_gray'}, {'score': {'name': '@s', 'objective': 'mg_dropper_f'}, 'color': 'gray'}]))
fn('dropper/hud', _hud)

_warn = []
for _ticks, _txt in ((1200, 'Noch 60 Sekunden!'), (600, 'Noch 30 Sekunden!'), (200, 'Noch 10 Sekunden!')):
    _warn += [f'execute if score #dropper_t mg matches {_LIMIT - _ticks} run tellraw @a[tag={_T}] {msg({"text": _txt, "color": "red", "bold": True})}',
              f'execute if score #dropper_t mg matches {_LIMIT - _ticks} as @a[tag={_T}] at @s run playsound minecraft:block.note_block.basedrum master @s ~ ~ ~ 1 0.6']

_game = [
    f'execute if score #dropper_t mg matches {_GO - 60} run function {NS}:dropper/cd3',
    f'execute if score #dropper_t mg matches {_GO - 40} run function {NS}:dropper/cd2',
    f'execute if score #dropper_t mg matches {_GO - 20} run function {NS}:dropper/cd1',
    f'execute if score #dropper_t mg matches {_GO} run function {NS}:dropper/go',
    f'execute as @e[type=minecraft:player,tag={_AL}] at @s run function {NS}:dropper/pl',     # @e: only living players
    f'execute unless score #{_K} mg matches 2 run return 0',
    'scoreboard players operation #dropper_m mg = #dropper_t mg', 'scoreboard players operation #dropper_m mg %= #4 mg',
    f'execute if score #dropper_m mg matches 0 run function {NS}:dropper/hud',
    *_warn,
    f'execute store result score #dropper_n mg if entity {_RACE}',
    f'execute if score #dropper_n mg matches 0 run return run function {NS}:dropper/end_go',
    f'execute if score #dropper_n mg matches 1 if score #dropper_np mg matches 2.. run return run function {NS}:dropper/end_alone',
    f'execute if score #dropper_t mg matches {_LIMIT}.. run return run function {NS}:dropper/end_time',
]

_setup = [
    'tag @a remove mg_dropper_win',
    'scoreboard players set #dropper_n mg 0',
    f'execute as @a[tag={_T}] run function {NS}:dropper/assign',
    f'execute store result score #dropper_np mg if entity @a[tag={_T}]',
    f'scoreboard players set @a[tag={_T}] mg_dropper_l 1', f'scoreboard players set @a[tag={_T}] mg_dropper_f 0',
    f'execute as @a[tag={_T}] run function {NS}:dropper/tp',
    f'effect give @a[tag={_T}] minecraft:saturation infinite 0 true',
    f'effect give @a[tag={_T}] minecraft:resistance infinite 4 true',
    f'execute as @a[tag={_T}] run attribute @s minecraft:gravity base set {_GRAV}',
    f'bossbar set {NS}:dropper max {(_LIMIT - _GO) // 20}', f'bossbar set {NS}:dropper value {(_LIMIT - _GO) // 20}',
    f'bossbar set {NS}:dropper color yellow', f'bossbar set {NS}:dropper players @a[tag={_T}]', f'bossbar set {NS}:dropper visible true',
]

EXTRA_LOAD.extend(['scoreboard objectives add mg_dropper_s dummy', 'scoreboard objectives add mg_dropper_l dummy',
                   'scoreboard objectives add mg_dropper_f dummy', 'scoreboard players set #10 mg 10',
                   f'bossbar add {NS}:dropper {tc({"text": "Dropper"})}',
                   f'execute unless score #{_K} mg matches 2 run bossbar set {NS}:dropper visible false'])
ENTER_LINES.extend(['tag @s remove mg_dropper_win', 'attribute @s minecraft:gravity base reset'])

party(_K, 'Dropper', 'gold', (DX, DY, DZ), trig=67, prof='fisherman', sub='4 Schächte · Fallen · Erster gewinnt',
      menu='Fall durch 4 Schächte ins Wasser',
      info='Spring in den Schacht und weich im Fallen allen Hindernissen aus. Landest du auf einem Block, geht es zurück nach oben. '
           'Triffst du das Wasser unten, kommt das nächste Level. Wer zuerst alle 4 Level schafft, gewinnt – Zeitlimit 5 Minuten!',
      title_sub='Triff das Wasser!', size=114, maxp=_SLOTS, build=_build, setup=_setup, game=_game, custom_end=True,
      spect=(DX, _R + 8, DZ), coins_win=0, cleanup=[*_gate('light_blue_stained_glass'), f'bossbar set {NS}:dropper visible false',
                                                   f'bossbar set {NS}:dropper players', 'tag @a remove mg_dropper_win'])
