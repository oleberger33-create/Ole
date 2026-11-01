# Dropper: falling-parkour race through vertical shafts (~67 blocks deep each).
# There is a pool of N levels (_LEVELS). Every round picks 4 different random levels, sorted easy -> hard by 'diff';
# all players of the round get the same 4. Every player falls in a private copy of the course (8 slots, 30 blocks apart
# along z); the N levels sit side by side along x (30 apart). Land on anything that is not water -> back onto the
# ledge of the current level. Splash into the pool of your own current shaft -> next level. First through all 4 wins;
# after 5 minutes the furthest player (fewest fails) wins.
# Records are per level (mg_dropper_r_<id>, ticks from arriving on that level's ledge - for the first level from "LOS!" -
# until the splash, fails included). Solo and multiplayer both set them. Solo: +3 coins for finishing, +1 per new level
# record (max +2 per run). mg_dropper_rc counts the levels with a record (stats menu).
# The N x 8 shafts are static: built once, one shaft per step in the background (dropper/bstep, marker #dropper_v).
_K = 'dropper'
DX, DY, DZ = 84000, Y, 0
_T, _AL = 'mg_dropper', 'mg_al_dropper'
_RACE = f'@a[tag={_AL}]'
_GO = 120                              # tick of "LOS!" (after the 3-2-1 countdown)
_LIMIT = _GO + 6000                    # 5 minutes
_SLOTS = 8
_PICK = 4                              # levels per round
_B = DY - 6                            # shaft floor (y94); pool water y95..97
_L = DY + 64                           # start ledge block (y164), feet at y165
_R = _L + 5                            # glass roof (y169)
_BUILD_V = 3
_PRED = 'type' if MIN_FORMAT >= 121 else 'condition'
_GRAV = 0.04                           # half gravity inside the shafts: ~3.6 s per drop, enough time to steer around the obstacles


# ---- level data. Cells (i, j) in 0..12 map to x = cx-6+i, z = cz-6+j; the ledge covers i 0..2 at depth 0 (feet at depth -1).
# layer: (depth below the ledge block, block, base 'full'|'empty', open rects, solid rects, thickness)
# diff: difficulty 1 (easy) .. 10 (hard) - the 4 levels of a round are played in ascending diff (ties: random order).
#       Shown as stars on the ledge sign: 1-3 = 1 star, 4-6 = 2 stars, 7-10 = 3 stars.
# id (optional): stable record key (scoreboard mg_dropper_r_<id>); default = the name in lower case ascii.
#       Never rename a level without setting id to the old key, otherwise its records are lost.
_LEVELS = [
    dict(name='Farbschacht', diff=2, col='yellow', wall='white_concrete', band=None, corner='quartz_pillar', light='sea_lantern',
         ledge='smooth_quartz', floor='white_concrete', poolfloor='sea_lantern', rim='yellow_concrete',
         bands=['red_concrete', 'orange_concrete', 'yellow_concrete', 'lime_concrete', 'light_blue_concrete', 'purple_concrete'],
         pool=(3, 3, 9, 9),
         layers=[(8, 'red_concrete', 'full', [(3, 4, 7, 8)], [], 1),
                 (16, 'orange_concrete', 'full', [(4, 5, 8, 9)], [], 1),
                 (24, 'yellow_concrete', 'full', [(4, 3, 9, 10)], [(6, 6, 7, 7)], 1),
                 (33, 'lime_concrete', 'full', [(5, 4, 9, 8)], [], 1),
                 (42, 'light_blue_concrete', 'full', [(4, 3, 8, 7)], [], 1),
                 (51, 'purple_concrete', 'empty', [], [(0, 2, 12, 3), (0, 8, 12, 9)], 2)]),
    dict(name='Tiefsee', diff=4, col='aqua', wall='prismarine_bricks', band='dark_prismarine', corner='dark_prismarine', light='sea_lantern',
         ledge='dark_prismarine', floor='prismarine', poolfloor='sea_lantern', rim='light_blue_concrete',
         pool=(7, 3, 10, 6),
         layers=[(7, 'cyan_stained_glass', 'full', [(4, 8, 7, 11)], [], 1),
                 (15, 'prismarine', 'full', [(5, 7, 8, 10)], [], 1),
                 (23, 'light_blue_stained_glass', 'full', [(4, 4, 10, 11)], [(6, 8, 8, 10)], 1),
                 (31, 'dark_prismarine', 'full', [(6, 4, 9, 8)], [], 1),
                 (40, 'cyan_stained_glass', 'full', [(7, 3, 9, 6)], [], 1),
                 (49, 'prismarine_bricks', 'full', [(6, 2, 11, 7)], [(8, 4, 9, 5)], 1)]),
    dict(name='Netherschlund', diff=6, col='red', wall='polished_blackstone_bricks', band='gilded_blackstone', corner='obsidian', light='shroomlight',
         ledge='polished_blackstone', floor='blackstone', poolfloor='glowstone', rim='red_nether_bricks',
         pool=(8, 6, 11, 9),
         layers=[(6, 'nether_bricks', 'empty', [], [(0, 0, 4, 12), (7, 0, 8, 12), (11, 0, 12, 12)], 2),
                 (13, 'red_nether_bricks', 'full', [(5, 1, 8, 4)], [], 1),
                 (20, 'red_stained_glass', 'full', [(7, 2, 10, 5)], [], 1),
                 (28, 'nether_wart_block', 'full', [(6, 1, 11, 6)], [(8, 3, 9, 4)], 1),
                 (36, 'warped_wart_block', 'full', [(9, 4, 12, 7)], [], 1),
                 (45, 'red_stained_glass', 'full', [(8, 6, 11, 9)], [], 1),
                 (54, 'nether_bricks', 'full', [(7, 6, 12, 8)], [], 2)]),
    dict(name='Endkern', diff=8, col='light_purple', wall='end_stone_bricks', band='purpur_block', corner='obsidian', light='pearlescent_froglight',
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

# ===== NEW LEVELS: paste the designer's 8 level dicts into this list (replacing the placeholders) =====
def _ph(src, name, diff):          # TEMPORARY placeholder: a copy of an existing level under another name
    return dict(_LEVELS[src], name=name, diff=diff)
_NEW_LEVELS = [
    _ph(0, 'Platzhalter A', 1), _ph(1, 'Platzhalter B', 3), _ph(2, 'Platzhalter C', 5), _ph(3, 'Platzhalter D', 7),
    _ph(0, 'Platzhalter E', 9), _ph(1, 'Platzhalter F', 3), _ph(2, 'Platzhalter G', 6), _ph(3, 'Platzhalter H', 10),
]
# ===== END NEW LEVELS =====
_LEVELS += _NEW_LEVELS
_NL = len(_LEVELS)
assert _NL >= _PICK


def _slug(n):
    for a, b in (('ä', 'ae'), ('ö', 'oe'), ('ü', 'ue'), ('ß', 'ss'), ('Ä', 'ae'), ('Ö', 'oe'), ('Ü', 'ue')):
        n = n.replace(a, b)
    return ''.join(ch for ch in n.lower() if ch.isascii() and ch.isalnum())


for _lv in _LEVELS:
    _lv.setdefault('id', _slug(_lv['name']))
    assert 'diff' in _lv, _lv['name']
assert len({_lv['id'] for _lv in _LEVELS}) == _NL, 'level ids must be unique'


def _obj(l):
    return f'mg_dropper_r_{_LEVELS[l]["id"]}'


def _stars(l):
    d = _LEVELS[l]['diff']
    n = 1 if d <= 3 else 2 if d <= 6 else 3
    return '★' * n + '☆' * (3 - n)


_X0 = DX - 15 * (_NL - 1)              # centre x of level 0


def _lx(l):
    return _X0 + 30 * l


def _sz(s):
    return DZ - 105 + 30 * s


def _r(x, y, z):
    return f'~{x} ~{y - DY} ~{z}'


def _F(x1, y1, z1, x2, y2, z2, b, mode=''):
    """fill relative to the shaft centre (x/z offsets, absolute y): the build functions run positioned at (cx, DY, cz)."""
    return f'fill {_r(x1, y1, z1)} {_r(x2, y2, z2)} minecraft:{b}' + (f' {mode}' if mode else '')


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
    """Commands (relative to the shaft centre) that build level l from scratch (the hollow shell clears the inside)."""
    lv = _LEVELS[l]
    cx, cz = 0, 0
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
        out.append(f'setblock {_r(x, _R + 2, z)} minecraft:end_rod')
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
        out.append(f'setblock {_r(cx - 4, _L, Z(j))} minecraft:{"yellow_concrete" if j % 2 == 0 else "black_concrete"}')
    return out


for _l in range(_NL):
    fn(f'dropper/lv{_l}', _shaft(_l))


def _holo(x, y, z, text, scale):      # like holo(), but without mg_holo: the hub rebuild must not kill these static labels
    return holo('mg_dropperh', x, y, z, text, scale).replace('Tags:["mg_holo","mg_dropperh"]', 'Tags:["mg_dropperh"]')


# ---- static background build: one shaft per step, only its 30x30 cell is forceloaded meanwhile.
# Everything is driven by the single scheduled function dropper/bstep (schedule replaces -> never two chains, also after /reload).
_JOBS = [(l, s) for l in range(_NL) for s in range(_SLOTS)]
_NJ = len(_JOBS)
_bj = []
for _j, (_l, _s) in enumerate(_JOBS):
    _cx, _cz = _lx(_l), _sz(_s)
    _box = f'{_cx - 15} {_cz - 15} {_cx + 14} {_cz + 14}'
    _ld = ' '.join(f'if loaded {x} {DY} {z}' for x in (_cx - 15, _cx + 14) for z in (_cz - 15, _cz + 14))
    _bj.append(f'execute if score #dropper_bq mg matches {_j} run return run function {NS}:dropper/b/j{_j}')
    fn(f'dropper/b/j{_j}', [
        f'{OW} forceload add {_box}',
        f'execute in minecraft:overworld {_ld} run scoreboard players add #dropper_bw mg 1',
        f'execute if score #dropper_bw mg matches 3.. run return run function {NS}:dropper/b/d{_j}',   # loaded for ~10 ticks: entities too
        f'schedule function {NS}:dropper/bstep 5t'])
    _lv = _LEVELS[_l]
    _d = [f'execute in minecraft:overworld positioned {_cx} {DY} {_cz} run function {NS}:dropper/lv{_l}',
          f'{OW} kill @e[type=minecraft:text_display,tag=mg_dropperh,x={_cx - 15},y={DY - 30},z={_cz - 15},dx=29,dy=120,dz=29]',
          _holo(c5(_cx - 5), _L + 3.5, c5(_cz), [{'text': _lv['name'] + '\n', 'color': _lv['col'], 'bold': True},
                                                {'text': _stars(_l), 'color': 'gold', 'bold': False}], 0.9)]
    if _s == 0:
        _d.append(_holo(c5(_cx), _R + 4, c5(_cz - 14), [{'text': _lv['name'] + '\n', 'color': _lv['col'], 'bold': True},
                                                         {'text': _stars(_l), 'color': 'gold', 'bold': False}], 2.5))
        if _l == _NL // 2:
            _d.append(_holo(c5(DX), _R + 9, c5(_cz - 14), [{'text': 'DROPPER', 'color': 'gold', 'bold': True}], 5.0))
    _d += [f'{OW} forceload remove {_box}', 'scoreboard players set #dropper_bw mg 0',
           f'scoreboard players set #dropper_bq mg {_j + 1}', f'schedule function {NS}:dropper/bstep 2t']
    fn(f'dropper/b/d{_j}', _d)
fn('dropper/bstep', [
    f'execute if score #dropper_v mg matches {_BUILD_V} run return 0',
    f'execute unless score #dropper_bq mg matches 0..{_NJ - 1} run return run function {NS}:dropper/bfin',
    *_bj])
fn('dropper/bfin', [f'scoreboard players set #dropper_v mg {_BUILD_V}', f'scoreboard players set #dropper_bq mg {_NJ}',
                    f'tellraw @a[tag=mg_hub] ' + msg({'text': 'Dropper ist fertig gebaut – ', 'color': 'gray'}, {'text': f'{_NL} Level', 'color': 'gold'},
                                                     {'text': ' warten auf dich!', 'color': 'gray'})])
_READY = (f'score #dropper_v mg matches {_BUILD_V}',
          msg({'text': 'Dropper wird noch gebaut (', 'color': 'red'}, {'score': {'name': '#dropper_bq', 'objective': 'mg'}, 'color': 'white'},
              {'text': f'/{_NJ}). Gleich fertig!', 'color': 'red'}))

# ---- round setup: pick _PICK different random levels (#dropper_p1..), sort them by diff (#dropper_d1..)
for _k in range(1, _PICK + 1):
    fn(f'dropper/pick{_k}', [f'execute store result score #dropper_p{_k} mg run random value 0..{_NL - 1}',
                             *[f'execute if score #dropper_p{_k} mg = #dropper_p{_i} mg run return run function {NS}:dropper/pick{_k}' for _i in range(1, _k)],
                             *[f'execute if score #dropper_p{_k} mg matches {_l} run scoreboard players set #dropper_d{_k} mg {_LEVELS[_l]["diff"]}' for _l in range(_NL)]])
_NET = {4: [(1, 2), (3, 4), (1, 3), (2, 4), (2, 3)]}.get(_PICK) or [(a, b) for i in range(_PICK) for a, b in ((x, x + 1) for x in range(1, _PICK))]
for _a, _b in set(_NET):
    fn(f'dropper/sw{_a}{_b}', [f'scoreboard players operation #dropper_p{_a} mg >< #dropper_p{_b} mg',
                               f'scoreboard players operation #dropper_d{_a} mg >< #dropper_d{_b} mg'])
_names = []
for _k in range(1, _PICK + 1):
    for _l, _lv in enumerate(_LEVELS):
        _names.append(f'execute if score #dropper_p{_k} mg matches {_l} run data modify storage {NS}:dropper n{_k} set value '
                      f'{{text:"{_lv["name"]}",color:"{_lv["col"]}"}}')
        _names.append(f'execute if score #dropper_p{_k} mg matches {_l} run data modify storage {NS}:dropper s{_k} set value "{_stars(_l)}"')
fn('dropper/pick', [*[f'function {NS}:dropper/pick{_k}' for _k in range(1, _PICK + 1)],
                    *[f'execute if score #dropper_d{_a} mg > #dropper_d{_b} mg run function {NS}:dropper/sw{_a}{_b}' for _a, _b in _NET],
                    *_names])


def _N(k, bold=False):
    return {'nbt': f'n{k}', 'storage': f'{NS}:dropper', 'interpret': True, 'bold': bold}


_overview = [{'text': 'Diese Runde: ', 'color': 'gray'}]
for _k in range(1, _PICK + 1):
    _overview += [{'text': f'{_k}. ', 'color': 'dark_gray'}, _N(_k), {'text': ' '},
                  {'nbt': f's{_k}', 'storage': f'{NS}:dropper', 'color': 'gold'}]
    if _k < _PICK:
        _overview.append({'text': '  →  ', 'color': 'dark_gray'})

# ---- the player's current level index mg_dropper_c from the step mg_dropper_l (1.._PICK)
fn('dropper/cur', [f'execute if score @s mg_dropper_l matches {_k} run scoreboard players operation @s mg_dropper_c = #dropper_p{_k} mg' for _k in range(1, _PICK + 1)])

# ---- teleports onto the ledge of the player's current level (mg_dropper_c) in the player's slot (mg_dropper_s)
for _l in range(_NL):
    fn(f'dropper/tp/l{_l}', [f'execute if score @s mg_dropper_s matches {_s} run {OW} tp @s {c5(_lx(_l) - 5)} {_L + 1} {c5(_sz(_s))} -90 25'
                             for _s in range(_SLOTS)])
fn('dropper/tp', [f'execute if score @s mg_dropper_c matches {_l} run return run function {NS}:dropper/tp/l{_l}' for _l in range(_NL)])

fn('dropper/assign', ['scoreboard players operation @s mg_dropper_s = #dropper_n mg', 'scoreboard players add #dropper_n mg 1'])

# ---- per-level records: arrival message + check after the splash (#dropper_lv mg = level time in ticks)
for _l, _lv in enumerate(_LEVELS):
    O = _obj(_l)
    NM = {'text': _lv['name'], 'color': _lv['col'], 'bold': True}
    fn(f'dropper/rec/a{_l}', [
        *[f'execute if score @s {O} matches 1.. run {x}' for x in pb_fmt(f'@s {O}', 'dropper_o')],
        f'execute if score @s {O} matches 1.. run tellraw @s ' + msg(NM, {'text': '  ·  Dein Rekord hier: ', 'color': 'gray', 'bold': False}, *pb_txt('dropper_o', 'aqua')),
        f'execute unless score @s {O} matches 1.. run tellraw @s ' + msg(NM, {'text': '  ·  Noch kein Rekord hier – jetzt setzen!', 'color': 'gray', 'bold': False})])
    fn(f'dropper/rec/r{_l}', [
        'scoreboard players set #dropper_new mg 0',
        f'execute unless score @s {O} matches 1.. run scoreboard players set #dropper_new mg 1',
        f'execute if score @s {O} matches 1.. if score #dropper_lv mg < @s {O} run scoreboard players set #dropper_new mg 2',
        'execute if score #dropper_lv mg matches ..0 run scoreboard players set #dropper_new mg 3',     # never a record (should not happen)
        *pb_fmt('#dropper_lv mg', 'dropper_a'),
        *[f'execute if score @s {O} matches 1.. run {x}' for x in pb_fmt(f'@s {O}', 'dropper_o')],
        f'execute if score #dropper_new mg matches 0 run tellraw @s ' + msg({'text': 'Zeit: ', 'color': 'gray'}, *pb_txt('dropper_a', 'white'),
                                                                             {'text': '   ·   Rekord: ', 'color': 'gray', 'bold': False}, *pb_txt('dropper_o', 'aqua')),
        f'execute if score #dropper_new mg matches 1 run tellraw @s ' + msg({'text': '★ Erster Rekord auf ', 'color': 'gold'}, NM,
                                                                             {'text': ': ', 'color': 'gold', 'bold': False}, *pb_txt('dropper_a', 'yellow')),
        f'execute if score #dropper_new mg matches 2 run tellraw @s ' + msg({'text': '★ Neuer Rekord auf ', 'color': 'gold'}, NM,
                                                                             {'text': ': ', 'color': 'gold', 'bold': False}, *pb_txt('dropper_a', 'yellow'),
                                                                             {'text': '  (vorher ', 'color': 'gray', 'bold': False}, *pb_txt('dropper_o', 'gray'),
                                                                             {'text': ')', 'color': 'gray', 'bold': False}),
        f'execute if score #dropper_new mg matches 2 run tellraw @a[tag={_T},distance=0.01..] ' + msg(
            {'selector': '@s', 'color': 'white'}, {'text': ' – neuer Rekord auf ', 'color': 'gray'}, NM, {'text': ': ', 'color': 'gray', 'bold': False},
            *pb_txt('dropper_a', 'yellow')),
        f'execute if score #dropper_new mg matches 1 run scoreboard players add @s mg_dropper_rc 1',
        f'execute if score #dropper_new mg matches 1..2 run scoreboard players operation @s {O} = #dropper_lv mg',
        'execute if score #dropper_new mg matches 1..2 at @s run playsound minecraft:entity.experience_orb.pickup master @s ~ ~ ~ 0.8 1.6',
        f'execute if score #dropper_new mg matches 1..2 if score #dropper_np mg matches ..1 if score @s mg_dropper_nr matches ..{1} run function {NS}:dropper/rec_coin'])
fn('dropper/rec_coin', ['scoreboard players add @s mg_dropper_nr 1', 'scoreboard players add @s mg_coins 1',
                        f'tellraw @s ' + msg({'text': '+1 Münze ', 'color': 'yellow'}, {'text': '(Level-Rekord)', 'color': 'gold'})])
fn('dropper/arr', [f'execute if score @s mg_dropper_c matches {_l} run return run function {NS}:dropper/rec/a{_l}' for _l in range(_NL)])
fn('dropper/rec', [f'execute if score @s mg_dropper_c matches {_l} run return run function {NS}:dropper/rec/r{_l}' for _l in range(_NL)])

# ---- per player, every tick (only living racers)
fn('dropper/pl', [
    f'execute unless score #{_K} mg matches 2 run return 0',
    f'execute if score @s mg_deaths matches 1.. run return run function {NS}:dropper/died',
    f'execute if score #dropper_t mg matches ..{_GO - 1} unless entity @s[y={_L + 0.5},dy=8] run return run function {NS}:dropper/tp',  # countdown: stay on the ledge
    f'execute if score #dropper_t mg matches ..{_GO - 1} run return 0',
    f'execute if entity @s[y={_B - 2},dy=8] if block ~ ~ ~ minecraft:water run return run function {NS}:dropper/splash',
    f'execute if entity @s[y={_B - 2},dy=8] if block ~ ~0.6 ~ minecraft:water run return run function {NS}:dropper/splash',
    f'execute unless entity @s[x={_X0 - 15},y={_B - 4},z={DZ - 120},dx={30 * _NL},dy={_R - _B + 6},dz=240] run return run function {NS}:dropper/fail',
    f'execute if entity @s[y={_L + 0.5},dy=8] run return 0',          # on the start ledge: safe
    f'execute if predicate {{{_PRED}:"minecraft:entity_properties",entity:"this",predicate:{{flags:{{is_on_ground:true}}}}}} run function {NS}:dropper/fail',
])
def _addc(sc, v):      # scoreboard add does not take negative numbers
    return f'scoreboard players {"add" if v >= 0 else "remove"} {sc} {abs(v)}'


# water only counts in the player's own current shaft (centre x = _X0 + 30*c, z = _sz(slot))
fn('dropper/splash', [
    'execute store result score #dropper_px mg run data get entity @s Pos[0]',
    'execute store result score #dropper_pz mg run data get entity @s Pos[2]',
    'scoreboard players operation #dropper_ex mg = @s mg_dropper_c', 'scoreboard players operation #dropper_ex mg *= #dropper_30 mg',
    _addc('#dropper_ex mg', _X0), 'scoreboard players operation #dropper_px mg -= #dropper_ex mg',
    'scoreboard players operation #dropper_ex mg = @s mg_dropper_s', 'scoreboard players operation #dropper_ex mg *= #dropper_30 mg',
    _addc('#dropper_ex mg', _sz(0)), 'scoreboard players operation #dropper_pz mg -= #dropper_ex mg',
    f'execute unless score #dropper_px mg matches -7..7 run return run function {NS}:dropper/fail',
    f'execute unless score #dropper_pz mg matches -7..7 run return run function {NS}:dropper/fail',
    f'function {NS}:dropper/done'])
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


_done = ['scoreboard players operation #dropper_lv mg = #dropper_t mg', 'scoreboard players operation #dropper_lv mg -= @s mg_dropper_lt',
         f'function {NS}:dropper/rec',
         'scoreboard players add @s mg_dropper_l 1', 'execute if score #dropper_np mg matches 2.. run scoreboard players add @s mg_coins 1',
         'particle minecraft:splash ~ ~1 ~ 0.6 0.4 0.6 0.2 40',
         f'execute if score @s mg_dropper_l matches {_PICK + 1}.. run return run function {NS}:dropper/win',
         'playsound minecraft:entity.player.levelup master @s ~ ~ ~ 1 1.2',
         'playsound minecraft:entity.generic.splash master @s ~ ~ ~ 0.6 1',
         f'function {NS}:dropper/cur', 'scoreboard players operation @s mg_dropper_lt = #dropper_t mg',
         f'function {NS}:dropper/tp', 'title @s times 3 35 10']
for _k in range(2, _PICK + 1):
    _done += [f'execute if score @s mg_dropper_l matches {_k} run title @s title {tc({"text": f"Level {_k}/{_PICK}", "color": "gold", "bold": True})}',
              f'execute if score @s mg_dropper_l matches {_k} run title @s subtitle {tc([{"text": "✔ Geschafft!  ", "color": "green", "bold": True}, {"text": "Weiter: ", "color": "white"}, _N(_k)])}',
              f'execute if score @s mg_dropper_l matches {_k} run tellraw @a[tag={_T}] ' + msg(
                  {'selector': '@s', 'color': 'white'}, {'text': ' hat ', 'color': 'gray'}, _N(_k - 1), {'text': ' geschafft ', 'color': 'gray'},
                  {'text': f'({_k - 1}/{_PICK})', 'color': 'gold'})]
_done.append(f'function {NS}:dropper/arr')
_done.append(f'execute if score @s mg_dropper_l matches {_PICK} as @a[tag={_T}] unless entity @s[scores={{mg_dropper_l={_PICK}..}}] at @s run '
             'playsound minecraft:block.note_block.didgeridoo master @s ~ ~ ~ 0.8 0.8')
fn('dropper/done', _done)

fn('dropper/win', [
    'tag @s add mg_dropper_win',
    f'execute if score #dropper_np mg matches ..1 run return run function {NS}:{_K}/end',     # solo -> solo_end
    'scoreboard players operation #dropper_c mg = #dropper_t mg', f'scoreboard players remove #dropper_c mg {_GO}',
    'scoreboard players operation #dropper_c mg /= #20 mg', *_clock('#dropper_c mg'),
    f'tellraw @a[tag={_T}] ' + msg({'selector': '@s', 'color': 'gold', 'bold': True}, {'text': f' hat alle {_PICK} Level geschafft! ', 'color': 'yellow'},
                                    {'text': '⏱ ', 'color': 'dark_gray'}, *_TIME),
    'playsound minecraft:ui.toast.challenge_complete master @s ~ ~ ~ 1 1',
    f'title @a[tag={_T}] times 5 60 15',
    f'title @s title {tc({"text": "SIEG!", "color": "gold", "bold": True})}',
    'title @s subtitle ' + tc([{'text': f'Alle {_PICK} Level in ', 'color': 'white'}] + _TIME),
    f'title @a[tag={_T},tag=!mg_dropper_win] title {tc({"text": "Vorbei!", "color": "red", "bold": True})}',
    f'title @a[tag={_T},tag=!mg_dropper_win] subtitle ' + tc([{'selector': '@s', 'color': 'gold'}, {'text': ' war schneller', 'color': 'white'}]),
    f'function {NS}:dropper/end_go'])

# ---- end of the round (own end: wins/coins are booked here, nobody has to keep mg_al_dropper)
_W = f'@a[tag={_T},tag=mg_dropper_win]'
_rank = []
for _l in range(_PICK + 1, 0, -1):
    _st = ([{'text': '✔ Ziel', 'color': 'green', 'bold': True}] if _l > _PICK else
           [{'text': f'Level {_l}/{_PICK} ', 'color': 'gold'}, _N(_l)])
    _rank.append(f'execute as @a[tag={_T},scores={{mg_dropper_l={_l}}}] run tellraw @a[tag={_T}] ' + tc(
        [{'text': '   ▸ ', 'color': 'dark_gray'}, {'selector': '@s', 'color': 'white'}, {'text': '  '}, *_st,
         {'text': '  ·  Fehlversuche: ', 'color': 'dark_gray'}, {'score': {'name': '@s', 'objective': 'mg_dropper_f'}, 'color': 'gray'}]))
fn('dropper/end_go', [
    f'execute if score #dropper_np mg matches ..1 run return run function {NS}:{_K}/end',     # solo (also: the player left)
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
    f'execute if score #dropper_np mg matches ..1 run return run function {NS}:{_K}/end',
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

# ---- countdown: everybody stands frozen on the ledge of the first picked level (no walking, no jumping) until "LOS!"
_FREEZE = ['attribute @s minecraft:movement_speed base set 0', 'attribute @s minecraft:jump_strength base set 0']
_THAW = ['attribute @s minecraft:movement_speed base reset', 'attribute @s minecraft:jump_strength base reset']


def _cd(num, col, pitch):
    return [f'title @a[tag={_T}] times 0 22 4', f'title @a[tag={_T}] title {tc({"text": num, "color": col, "bold": True})}',
            f'title @a[tag={_T}] subtitle {tc([{"text": "Gleich geht es los: ", "color": "gray"}, _N(1)])}',
            f'execute as @a[tag={_T}] at @s run playsound minecraft:block.note_block.pling master @s ~ ~ ~ 1 {pitch}']


fn('dropper/cd3', _cd('3', 'red', 0.7))
fn('dropper/cd2', _cd('2', 'gold', 0.85))
fn('dropper/cd1', _cd('1', 'yellow', 1.0))
fn('dropper/go', [
    *[f'execute as @a[tag={_T}] run {x}' for x in _THAW],
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
for _k in range(1, _PICK + 1):
    _hud.append(f'execute as @a[tag={_AL},scores={{mg_dropper_l={_k}}}] run title @s actionbar ' + tc(
        [{'text': f'Level {_k}/{_PICK} ', 'color': 'gold', 'bold': True}, _N(_k),
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
    f'function {NS}:dropper/pick',
    'scoreboard players set #dropper_n mg 0',
    f'execute as @a[tag={_T}] run function {NS}:dropper/assign',
    f'scoreboard players set @a[tag={_T}] mg_dropper_l 1', f'scoreboard players set @a[tag={_T}] mg_dropper_f 0',
    f'scoreboard players set @a[tag={_T}] mg_dropper_nr 0', f'scoreboard players set @a[tag={_T}] mg_dropper_lt {_GO}',
    f'execute as @a[tag={_T}] run function {NS}:dropper/cur',
    f'execute as @a[tag={_T}] run function {NS}:dropper/tp',
    *[f'execute as @a[tag={_T}] run {x}' for x in _FREEZE],
    f'effect give @a[tag={_T}] minecraft:saturation infinite 0 true',
    f'effect give @a[tag={_T}] minecraft:resistance infinite 4 true',
    f'execute as @a[tag={_T}] run attribute @s minecraft:gravity base set {_GRAV}',
    f'bossbar set {NS}:dropper max {(_LIMIT - _GO) // 20}', f'bossbar set {NS}:dropper value {(_LIMIT - _GO) // 20}',
    f'bossbar set {NS}:dropper color yellow', f'bossbar set {NS}:dropper players @a[tag={_T}]', f'bossbar set {NS}:dropper visible true',
    f'tellraw @a[tag={_T}] ' + msg(*_overview),
    f'execute as @a[tag={_T}] run function {NS}:dropper/arr',
]

# ---- solo run: result (solo_end runs as the server, before the framework's "Solo-Runde vorbei" title)
_SOLO_COINS = 3
fn('dropper/solo_done', [   # as the player who cleared all levels of the round
    'scoreboard players operation #dropper_c mg = #dropper_t mg', f'scoreboard players remove #dropper_c mg {_GO}',
    *pb_fmt('#dropper_c mg', 'dropper_p'),
    f'title @s subtitle ' + tc([{'text': f'Alle {_PICK} Level in ', 'color': 'white'}] + pb_txt('dropper_p', 'yellow')),
    f'tellraw @s ' + msg({'text': 'Ziel! ', 'color': 'green', 'bold': True}, {'text': f'Alle {_PICK} Level in ', 'color': 'white'}, *pb_txt('dropper_p', 'yellow'),
                         {'text': '  ·  Fehlversuche: ', 'color': 'gray'}, {'score': {'name': '@s', 'objective': 'mg_dropper_f'}, 'color': 'white'}),
    f'scoreboard players add @s mg_coins {_SOLO_COINS}',
    f'tellraw @s ' + msg({'text': f'+{_SOLO_COINS} Münzen', 'color': 'yellow'}),
    f'tellraw @s ' + msg({'text': 'Rekorde zählen pro Level – du hast auf ', 'color': 'gray'}, {'score': {'name': '@s', 'objective': 'mg_dropper_rc'}, 'color': 'gold'},
                         {'text': f'/{_NL} Level einen Rekord.', 'color': 'gray'}),
    'execute at @s run summon minecraft:firework_rocket ~ ~1 ~ {LifeTime:20,FireworksItem:{id:"minecraft:firework_rocket",count:1,components:{"minecraft:fireworks":{flight_duration:1,explosions:[{shape:"large_ball",colors:[I;16766720],has_twinkle:true}]}}}}',
    'playsound minecraft:ui.toast.challenge_complete master @s ~ ~ ~ 1 1'])
fn('dropper/solo_fail', [   # as the player when the time ran out
    'scoreboard players operation #dropper_c mg = @s mg_dropper_l', 'scoreboard players remove #dropper_c mg 1',
    f'title @s subtitle ' + tc([{'score': {'name': '#dropper_c', 'objective': 'mg'}, 'color': 'yellow', 'bold': True},
                                {'text': f'/{_PICK} Level geschafft', 'color': 'white'}]),
    f'tellraw @s ' + msg({'text': 'Zeit um! ', 'color': 'red', 'bold': True}, {'text': 'Du hast ', 'color': 'gray'},
                         {'score': {'name': '#dropper_c', 'objective': 'mg'}, 'color': 'yellow', 'bold': True},
                         {'text': f'/{_PICK} Level geschafft', 'color': 'gray'}, {'text': '  ·  Fehlversuche: ', 'color': 'gray'},
                         {'score': {'name': '@s', 'objective': 'mg_dropper_f'}, 'color': 'white'}),
    'playsound minecraft:block.note_block.didgeridoo master @s ~ ~ ~ 1 0.8'])
_solo_end = [f'bossbar set {NS}:dropper visible false', f'title @a[tag={_T}] times 5 60 15',
             f'execute as @a[tag={_T},tag=mg_dropper_win] at @s run function {NS}:dropper/solo_done',
             f'execute as @a[tag={_T},tag=!mg_dropper_win] at @s run function {NS}:dropper/solo_fail',
             f'tag @a[tag={_T}] remove {_AL}']

# ---- stats menu: number of levels with a personal record (one line, not one per level)
PB_MENU.append(f'execute if score @s mg_dropper_rc matches 1.. run tellraw @s ' + tc(
    [{'text': '   Dropper: ', 'color': 'gray'}, {'score': {'name': '@s', 'objective': 'mg_dropper_rc'}, 'color': 'gold', 'bold': True},
     {'text': f'/{_NL} Level mit Rekord', 'color': 'gold'}]))

EXTRA_LOAD.extend(['scoreboard objectives add mg_dropper_s dummy', 'scoreboard objectives add mg_dropper_l dummy',
                   'scoreboard objectives add mg_dropper_f dummy', 'scoreboard objectives add mg_dropper_c dummy',
                   'scoreboard objectives add mg_dropper_lt dummy', 'scoreboard objectives add mg_dropper_nr dummy',
                   'scoreboard objectives add mg_dropper_rc dummy',
                   *[f'scoreboard objectives add {_obj(_l)} dummy' for _l in range(_NL)],
                   'scoreboard players set #10 mg 10', 'scoreboard players set #dropper_30 mg 30',
                   f'bossbar add {NS}:dropper {tc({"text": "Dropper"})}',
                   f'execute unless score #{_K} mg matches 2 run bossbar set {NS}:dropper visible false',
                   # static shafts: (re)start / resume the background build (a new layout version starts from job 0)
                   f'execute unless score #dropper_bv mg matches {_BUILD_V} run scoreboard players set #dropper_bq mg 0',
                   f'execute unless score #dropper_bv mg matches {_BUILD_V} run scoreboard players set #dropper_bw mg 0',
                   f'scoreboard players set #dropper_bv mg {_BUILD_V}',
                   f'execute unless score #dropper_v mg matches {_BUILD_V} run schedule function {NS}:dropper/bstep 40t'])
ENTER_LINES.extend(['tag @s remove mg_dropper_win', 'attribute @s minecraft:gravity base reset', *_THAW])

party(_K, 'Dropper', 'gold', (DX, DY, DZ), trig=67, prof='fisherman', sub=f'{_NL} Schächte · Erster gewinnt · auch solo',
      menu=f'{_PICK} von {_NL} Schächten – auch solo',
      info=f'Jede Runde: {_PICK} zufällige von {_NL} Schächten, vom leichtesten zum schwersten. Spring rein und weich im Fallen allen '
           'Hindernissen aus. Landest du auf einem Block, geht es zurück nach oben. Triffst du das Wasser unten, kommt das nächste Level. '
           f'Wer zuerst alle {_PICK} schafft, gewinnt – Zeitlimit 5 Minuten! Für jedes Level gibt es einen eigenen Rekord.',
      title_sub='Triff das Wasser!', size=16, maxp=_SLOTS, build=[], setup=_setup, game=_game, custom_end=True,
      spect=(DX, _R + 8, DZ), coins_win=0, solo=True, solo_end=_solo_end, ready=_READY,
      cleanup=[f'bossbar set {NS}:dropper visible false', f'bossbar set {NS}:dropper players', 'tag @a remove mg_dropper_win'])
