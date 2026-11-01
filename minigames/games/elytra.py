# Elytra-Rennen: start on a launch tower in a red-rock canyon, glide with an elytra through 15 rings in order.
# Rings snake through three canyon lanes, dropping from y150 to y106 between banded terracotta mesas.
# Rockets: 3 at the start, +2 at rings 5 and 10, 1 on a respawn when you have none left.
# Falling below the course, touching rock/ground (0.4 s) or leaving the canyon -> back onto the pad on top of the last ring.
# First through the golden finish ring wins; everybody else gets a placement; the race ends when all finished
# or 3 minutes after the winner (6 minutes without any finisher -> whoever got furthest wins).
# Solo run (one starter, #elytra_np = 1): against the clock, personal best time (mg_elytra_pb), no win, 2 coins for
# finishing + 3 for a new record; time-out after 6 minutes ends with the reached ring.
_K = 'elytra'
EX, EY, EZ = 80000, Y, 0
_T, _AL = 'mg_elytra', 'mg_al_elytra'
_RACE = f'@a[tag={_AL},tag=!mg_elytra_fin]'
_GO = 120                          # tick of "LOS!" (after the 3-2-1 countdown)
_AFTER = 3600                      # 3 minutes after the winner
_LIMIT = _GO + 7200                # 6 minutes without a finisher
_FLOOR = EY - 4                    # canyon floor (top surface y96)
_LOW = EY - 2                      # below y98 = crashed
_SAFE = 'smooth_quartz'            # tower floor + respawn pads (standing there is allowed)
_BUILD_V = 4
_SPECT = (EX, EY + 75, EZ)
_ELY = ('minecraft:elytra[minecraft:unbreakable={},minecraft:enchantments={"minecraft:binding_curse":1},'
        'minecraft:tooltip_display={hidden_components:["minecraft:unbreakable"]},'
        'minecraft:custom_name={"text":"Renn-Elytra","color":"aqua","italic":false}]')
_FW = 'minecraft:firework_rocket'

# ---- the course: (dx, dy, dz, flight axis, inner radius, kind)   kind: n normal, r rocket refill, f finish
_RINGS = [
    (-30, 50, -40, 'x', 5, 'n'),
    (-12, 47, -36, 'x', 4, 'n'),
    (6, 43, -42, 'x', 4, 'n'),        # slot between two mesas
    (24, 39, -40, 'x', 4, 'n'),
    (52, 35, -20, 'z', 5, 'r'),       # apex of the first bend
    (24, 31, 0, 'x', 4, 'n'),
    (6, 24, 2, 'x', 4, 'n'),          # dive under the stone bridge
    (-12, 27, -2, 'x', 4, 'n'),       # climb
    (-30, 22, 0, 'x', 4, 'n'),
    (-52, 18, 20, 'z', 5, 'r'),       # apex of the second bend
    (-26, 15, 40, 'x', 4, 'n'),
    (-8, 11, 37, 'x', 3, 'n'),        # narrow canyon slot
    (10, 14, 43, 'x', 4, 'n'),
    (28, 9, 40, 'x', 4, 'n'),
    (48, 6, 40, 'x', 6, 'f'),         # finish
]
_N = len(_RINGS)
_RAIN = ['red', 'orange', 'yellow', 'lime', 'green', 'cyan', 'light_blue', 'blue', 'purple', 'magenta', 'pink', 'red']
_TXT = {'red': 'red', 'orange': 'gold', 'yellow': 'yellow', 'lime': 'green', 'green': 'dark_green', 'cyan': 'dark_aqua',
        'light_blue': 'aqua', 'blue': 'blue', 'purple': 'dark_purple', 'magenta': 'light_purple', 'pink': 'light_purple', 'white': 'white'}
_RD = []                           # per ring: dict with absolute coords + colours
_ci = 0
for _i, (_dx, _dy, _dz, _ax, _r, _kind) in enumerate(_RINGS):
    if _kind == 'n':
        _col = _RAIN[_ci % len(_RAIN)]; _ci += 1
        _hoop, _glass, _tcol = f'{_col}_concrete', f'{_col}_stained_glass', _TXT[_col]
    elif _kind == 'r':
        _hoop, _glass, _tcol = 'white_concrete', 'orange_stained_glass', 'gold'
    else:
        _hoop, _glass, _tcol = 'gold_block', 'yellow_stained_glass', 'gold'
    _RD.append(dict(k=_i + 1, x=EX + _dx, y=EY + _dy, z=EZ + _dz, ax=_ax, r=_r, kind=_kind, hoop=_hoop, glass=_glass, tcol=_tcol))
for _d in _RD:
    _d['c'] = (_d['x'] + 0.5, _d['y'] + 0.5, _d['z'] + 0.5)                  # hole centre
    _d['pad'] = (_d['x'], _d['y'] + _d['r'] + 3, _d['z'])                     # 3x3 respawn pad on top of the hoop
_TOWER_TOP = EY + 62                                                         # platform surface y162
_START = (EX - 47.5, _TOWER_TOP + 1, EZ - 39.5)                              # respawn spot before ring 1


def _c3(p):
    return f'{p[0]} {p[1]} {p[2]}'


def _F(x1, y1, z1, x2, y2, z2, b):
    return f'{OW} fill {x1} {y1} {z1} {x2} {y2} {z2} minecraft:{b}'


# ---- geometry
def _ring_cmds(d):
    """Hoop (concrete) + translucent rim (glass) + 4 sea lanterns, merged into horizontal fill runs."""
    R = d['r']
    cells = {}
    for a in range(-(R + 3), R + 4):
        for b in range(-(R + 3), R + 4):
            dist = math.hypot(a, b)
            if R + 0.5 <= dist < R + 1.5:
                blk = 'sea_lantern' if (a == 0 or b == 0) else d['hoop']
            elif R + 1.5 <= dist < R + 2.2:
                blk = d['glass']
            else:
                continue
            cells[(a, b)] = blk
    out = []
    for a in range(-(R + 3), R + 4):
        b = -(R + 3)
        while b < R + 4:
            blk = cells.get((a, b))
            if not blk:
                b += 1
                continue
            e = b
            while cells.get((a, e + 1)) == blk:
                e += 1
            y = d['y'] + a
            if d['ax'] == 'x':
                out.append(_F(d['x'], y, d['z'] + b, d['x'], y, d['z'] + e, blk))
            else:
                out.append(_F(d['x'] + b, y, d['z'], d['x'] + e, y, d['z'], blk))
            b = e + 1
    px, py, pz = d['pad']
    out.append(_F(px - 1, py, pz - 1, px + 1, py, pz + 1, _SAFE))
    return out


_BANDS = ['terracotta', 'orange_terracotta', 'red_terracotta', 'white_terracotta', 'orange_terracotta', 'yellow_terracotta',
          'red_terracotta', 'brown_terracotta', 'light_gray_terracotta', 'orange_terracotta']


def _mesa(dx, dz, r, h, seed=0):
    """Banded terracotta column from the floor up to y96+h, slightly eroded, coarse-dirt top."""
    cx, cz = EX + dx, EZ + dz
    out = []
    top = _FLOOR + h
    nb = (h + 4) // 4
    for i in range(nb):
        y1 = _FLOOR - 1 + i * 4
        y2 = min(y1 + 3, top)
        if y1 > top:
            break
        rr = r
        if (i + seed) % 5 == 3:
            rr = r - 1                              # erosion notch
        if i >= nb - 2:
            rr = max(1, r - (i - (nb - 3)))         # tapered crown
        blk = _BANDS[(i + seed) % len(_BANDS)]
        for z in range(-rr, rr + 1):
            w = int(math.floor(math.sqrt(rr * rr + rr - z * z)))
            out.append(_F(cx - w, y1, cz + z, cx + w, y2, cz + z, blk))
    cr = max(1, rr - 1)
    for z in range(-cr, cr + 1):
        w = int(math.floor(math.sqrt(cr * cr + cr - z * z)))
        out.append(_F(cx - w, top, cz + z, cx + w, top, cz + z, 'coarse_dirt'))
    return out


_MESAS = [
    # wall between lane 1 and lane 2
    (-40, -20, 5, 56), (-22, -21, 5, 50), (-4, -19, 5, 46), (14, -21, 5, 52),
    # wall between lane 2 and lane 3
    (-14, 20, 5, 40), (4, 22, 5, 36), (22, 19, 5, 44), (40, 21, 5, 38),
    # bend cores
    (36, -20, 6, 52), (-36, 20, 6, 38),
    # ring 3 slot / ring 12 slot
    (6, -53, 4, 54), (6, -31, 3, 50), (-8, 29, 3, 36), (-8, 46, 3, 34),
    # bridge piers (ring 7)
    (6, -9, 3, 43), (6, 13, 3, 43),
    # canyon rims
    (-30, -55, 4, 58), (24, -55, 4, 48), (44, -50, 4, 44), (-56, -2, 3, 40), (56, 0, 3, 44),
    (-44, 52, 4, 30), (-24, 55, 4, 34), (10, 56, 4, 30), (30, 55, 4, 26), (54, 54, 3, 22),
]

_rnd = random.Random(65)
_clear = clear_box(EX - 60, _FLOOR - 1, EZ - 60, EX + 60, EY + 76, EZ + 60, 3)
_build = [f'execute unless score #elytra_v mg matches {_BUILD_V} run function {NS}:elytra/clear',
          f'scoreboard players set #elytra_v mg {_BUILD_V}',
          f'kill @e[type=minecraft:text_display,tag=mg_elytrah]']
# canyon floor: sandstone bed, red sand, patches, a winding creek
_build += [_F(EX - 60, _FLOOR - 1, EZ - 60, EX + 60, _FLOOR - 1, EZ + 60, 'smooth_red_sandstone'),
           _F(EX - 60, _FLOOR, EZ - 60, EX + 60, _FLOOR, EZ + 60, 'red_sand')]
for _ in range(28):
    _px, _pz, _pr = _rnd.randint(-55, 55), _rnd.randint(-55, 55), _rnd.randint(2, 5)
    _blk = _rnd.choice(['terracotta', 'coarse_dirt', 'red_sandstone', 'orange_terracotta', 'packed_mud'])
    _build += [f'{OW} {c}' for c in disk(EX + _px, _FLOOR, EZ + _pz, _pr, _blk)]
for _x in range(-56, 57):
    _zc = round(6 * math.sin(_x / 10.0) - 2)
    _build.append(_F(EX + _x, _FLOOR, EZ + _zc - 1, EX + _x, _FLOOR, EZ + _zc + 1, 'water'))
    _build.append(_F(EX + _x, _FLOOR, EZ + _zc - 2, EX + _x, _FLOOR, EZ + _zc - 2, 'mud'))
    _build.append(_F(EX + _x, _FLOOR, EZ + _zc + 2, EX + _x, _FLOOR, EZ + _zc + 2, 'mud'))
for _i, (_dx, _dz, _r, _h) in enumerate(_MESAS):
    _build += _mesa(_dx, _dz, _r, _h, _i)
    if _r >= 5:                                     # a lower side lobe so the big mesas look less like columns
        _a = math.radians(_rnd.choice([0, 180]) + _rnd.randint(-25, 25))
        _build += _mesa(_dx + round((_r - 1) * math.cos(_a)), _dz + round((_r - 1) * math.sin(_a)), _r - 2, int(_h * 0.6), _i + 3)
# stone bridge over ring 7
_build += [_F(EX + 4, EY + 37, EZ - 9, EX + 8, EY + 39, EZ + 13, 'red_sandstone'),
           _F(EX + 4, EY + 37, EZ - 9, EX + 8, EY + 37, EZ + 13, 'cut_red_sandstone'),
           _F(EX + 5, EY + 40, EZ - 9, EX + 7, EY + 40, EZ + 13, 'coarse_dirt'),
           _F(EX + 6, EY + 36, EZ - 6, EX + 6, EY + 36, EZ - 6, 'ochre_froglight'),
           _F(EX + 6, EY + 36, EZ + 10, EX + 6, EY + 36, EZ + 10, 'ochre_froglight')]
# launch tower: deepslate shaft with copper bands and froglight strips, quartz platform in a glass cage
_tx1, _tx2, _tz1, _tz2 = EX - 53, EX - 47, EZ - 43, EZ - 37
_build.append(_F(_tx1, _FLOOR - 1, _tz1, _tx2, _TOWER_TOP - 1, _tz2, 'deepslate_tiles'))
for _y in range(_FLOOR + 8, _TOWER_TOP - 2, 10):
    _build.append(_F(_tx1, _y, _tz1, _tx2, _y + 1, _tz2, 'waxed_cut_copper'))
for _sx, _sz in ((EX - 50, _tz1), (EX - 50, _tz2), (_tx1, EZ - 40), (_tx2, EZ - 40)):
    _build.append(_F(_sx, _FLOOR + 2, _sz, _sx, _TOWER_TOP - 3, _sz, 'ochre_froglight'))
_build += [_F(EX - 55, _TOWER_TOP - 1, EZ - 45, EX - 45, _TOWER_TOP - 1, EZ - 35, 'waxed_cut_copper'),
           _F(EX - 54, _TOWER_TOP, EZ - 44, EX - 46, _TOWER_TOP, EZ - 36, _SAFE),
           _F(EX - 55, _TOWER_TOP, EZ - 45, EX - 45, _TOWER_TOP, EZ - 45, 'waxed_cut_copper'),
           _F(EX - 55, _TOWER_TOP, EZ - 35, EX - 45, _TOWER_TOP, EZ - 35, 'waxed_cut_copper'),
           _F(EX - 55, _TOWER_TOP, EZ - 45, EX - 55, _TOWER_TOP, EZ - 35, 'waxed_cut_copper'),
           _F(EX - 45, _TOWER_TOP, EZ - 45, EX - 45, _TOWER_TOP, EZ - 35, 'waxed_cut_copper'),
           _F(EX - 45, _TOWER_TOP, EZ - 44, EX - 45, _TOWER_TOP, EZ - 36, _SAFE),      # floor under the gate: standing allowed
           _F(EX - 55, _TOWER_TOP + 1, EZ - 45, EX - 45, _TOWER_TOP + 4, EZ - 45, 'light_blue_stained_glass'),
           _F(EX - 55, _TOWER_TOP + 1, EZ - 35, EX - 45, _TOWER_TOP + 4, EZ - 35, 'light_blue_stained_glass'),
           _F(EX - 55, _TOWER_TOP + 1, EZ - 45, EX - 55, _TOWER_TOP + 4, EZ - 35, 'light_blue_stained_glass')]
for _sx, _sz in ((EX - 55, EZ - 45), (EX - 55, EZ - 35), (EX - 45, EZ - 45), (EX - 45, EZ - 35)):
    _build += [_F(_sx, _TOWER_TOP + 1, _sz, _sx, _TOWER_TOP + 4, _sz, 'waxed_copper_block'),
               _F(_sx, _TOWER_TOP + 5, _sz, _sx, _TOWER_TOP + 5, _sz, 'end_rod')]
_GATE = (EX - 45, _TOWER_TOP + 1, EZ - 44, EX - 45, _TOWER_TOP + 4, EZ - 36)


def _gate(blk):
    return _F(*_GATE, blk)


_build.append(_gate('red_stained_glass'))
# finish: checkered landing field under the golden ring
_f = _RD[-1]
for _i in range(8):
    for _j in range(8):
        _build.append(_F(_f['x'] - 8 + 2 * _i, _FLOOR, _f['z'] - 8 + 2 * _j, _f['x'] - 7 + 2 * _i, _FLOOR, _f['z'] - 7 + 2 * _j,
                         'white_concrete' if (_i + _j) % 2 else 'black_concrete'))
# rings + labels
for _d in _RD:
    _build += _ring_cmds(_d)
    _lab = [{'text': 'ZIEL' if _d['kind'] == 'f' else f'Ring {_d["k"]}', 'color': _d['tcol'], 'bold': True}]
    if _d['kind'] == 'r':
        _lab.append({'text': '\n+2 Raketen', 'color': 'yellow', 'bold': False})
    _build.append(holo('mg_elytrah', _d['c'][0], _d['y'] + _d['r'] + 6.5, _d['c'][2], _lab, 1.6 if _d['kind'] == 'f' else 1.2))
_build += [holo('mg_elytrah', EX - 49.5, _TOWER_TOP + 7.5, EZ - 39.5,
                [{'text': 'ELYTRA-RENNEN\n', 'color': 'dark_aqua', 'bold': True}, {'text': '15 Ringe · Start →', 'color': 'white', 'bold': False}], 2.0)]
fn('elytra/clear', _clear)

# ---- per-tick logic
_ring_checks = []
_hud_fx = []
for _d in _RD:
    k, R, (cx, cy, cz) = _d['k'], _d['r'], _d['c']
    if _d['ax'] == 'x':
        slab = f'positioned {cx - 2} {cy - R - 1} {cz - R - 1} if entity @s[dx=3,dy={2 * R + 2},dz={2 * R + 2}]'
        delta = f'0.15 {R * 0.35:.2f} {R * 0.35:.2f}'
    else:
        slab = f'positioned {cx - R - 1} {cy - R - 1} {cz - 2} if entity @s[dx={2 * R + 2},dy={2 * R + 2},dz=3]'
        delta = f'{R * 0.35:.2f} {R * 0.35:.2f} 0.15'
    sel = f'@a[tag={_AL},tag=!mg_elytra_fin,scores={{mg_elytra_p={k - 1}}}]'
    _ring_checks.append(f'execute as {sel} positioned {cx} {cy - 0.3:.1f} {cz} if entity @s[distance=..{R + 1}] {slab} at @s run function {NS}:elytra/r{k}')
    _hud_fx += [f'execute as {sel} run particle minecraft:end_rod {cx} {cy} {cz} {delta} 0 10 force @s',
                f'execute as {sel} at @s anchored eyes facing {cx} {cy} {cz} run particle minecraft:electric_spark ^ ^ ^5 0 0 0 0 1 force @s',
                f'execute as {sel} at @s anchored eyes facing {cx} {cy} {cz} run particle minecraft:electric_spark ^ ^ ^6.5 0 0 0 0 1 force @s']
    extra = []
    if _d['kind'] == 'r':
        extra = [f'give @s {_FW} 2', 'playsound minecraft:entity.item.pickup master @s ~ ~ ~ 1 0.8',
                 'title @s times 0 25 8', 'title @s title {"text":""}',
                 f'title @s subtitle [{{"text":"✔ Ring {k}/{_N}  ","color":"green","bold":true}},{{"text":"+2 Raketen!","color":"gold","bold":true}}]']
    elif _d['kind'] == 'f':
        extra = [f'function {NS}:elytra/goal']
    else:
        extra = ['title @s times 0 15 5', 'title @s title {"text":""}',
                 f'title @s subtitle {{"text":"✔ Ring {k}/{_N}","color":"green","bold":true}}']
    fn(f'elytra/r{k}', [f'function {NS}:elytra/pass',
                        f'playsound minecraft:block.note_block.bell master @s ~ ~ ~ 1 {0.6 + 0.09 * k:.2f}',
                        'playsound minecraft:entity.experience_orb.pickup master @s ~ ~ ~ 0.5 1.4',
                        f'{OW} particle minecraft:firework {cx} {cy} {cz} {delta} 0.05 25 force',
                        *extra])

fn('elytra/pass', [
    'scoreboard players add @s mg_elytra_p 1', 'scoreboard players set @s mg_elytra_g 0',
    f'execute if score #elytra_np mg matches 2.. if score @s mg_elytra_p matches ..{_N - 1} if score @s mg_elytra_p > #elytra_best mg unless entity @s[tag=mg_elytra_lead] run function {NS}:elytra/newlead',
    'execute if score @s mg_elytra_p > #elytra_best mg run scoreboard players operation #elytra_best mg = @s mg_elytra_p'])
fn('elytra/newlead', [
    'effect clear @a[tag=mg_elytra_lead] minecraft:glowing', 'tag @a[tag=mg_elytra_lead] remove mg_elytra_lead',
    'tag @s add mg_elytra_lead', 'effect give @s minecraft:glowing infinite 0 true',
    f'execute if score #elytra_best mg matches 1.. run tellraw @a[tag={_T}] ' + msg(
        {'selector': '@s', 'color': 'white'}, {'text': ' übernimmt die Führung! ', 'color': 'aqua'},
        {'text': '(Ring ', 'color': 'gray'}, {'score': {'name': '@s', 'objective': 'mg_elytra_p'}, 'color': 'gray'}, {'text': ')', 'color': 'gray'})])

_TIME = [{'score': {'name': '#elytra_sec', 'objective': 'mg'}, 'color': 'white'}, {'text': ',', 'color': 'white'},
         {'score': {'name': '#elytra_ten', 'objective': 'mg'}, 'color': 'white'}, {'text': ' s', 'color': 'white'}]
fn('elytra/goal', [
    'tag @s add mg_elytra_fin', 'scoreboard players add #elytra_place mg 1',
    'scoreboard players operation @s mg_elytra_pl = #elytra_place mg',
    'scoreboard players operation #elytra_sec mg = #elytra_t mg', f'scoreboard players remove #elytra_sec mg {_GO}',
    'scoreboard players operation #elytra_ten mg = #elytra_sec mg', 'scoreboard players operation #elytra_ten mg %= #20 mg',
    'scoreboard players operation #elytra_ten mg /= #2 mg', 'scoreboard players operation #elytra_sec mg /= #20 mg',
    'effect clear @s minecraft:glowing', 'tag @s remove mg_elytra_lead',
    'title @s times 5 50 15',
    f'execute if score #elytra_np mg matches ..1 run return run function {NS}:elytra/solo_fin',
    f'execute if score #elytra_place mg matches 1 run function {NS}:elytra/first',
    f'execute if score #elytra_place mg matches 2.. run title @s title {tc({"text": "IM ZIEL!", "color": "aqua", "bold": True})}',
    f'execute if score #elytra_place mg matches 2.. run title @s subtitle ' + tc([{'text': 'Platz ', 'color': 'white'}, {'score': {'name': '@s', 'objective': 'mg_elytra_pl'}, 'color': 'gold', 'bold': True}, {'text': '  ·  ', 'color': 'dark_gray'}] + _TIME),
    f'execute if score #elytra_place mg matches 2.. run tellraw @a[tag={_T}] ' + msg(
        {'selector': '@s', 'color': 'white'}, {'text': ' ist im Ziel – ', 'color': 'gray'},
        {'text': 'Platz ', 'color': 'aqua'}, {'score': {'name': '@s', 'objective': 'mg_elytra_pl'}, 'color': 'aqua', 'bold': True},
        {'text': '  ·  ', 'color': 'dark_gray'}, *_TIME),
    'scoreboard players add @s mg_coins 3',
    'playsound minecraft:ui.toast.challenge_complete master @s ~ ~ ~ 1 1',
    'summon minecraft:firework_rocket ~ ~1 ~ {LifeTime:15,FireworksItem:{id:"minecraft:firework_rocket",count:1,components:{"minecraft:fireworks":{flight_duration:1,explosions:[{shape:"star",colors:[I;16766720,65535],has_trail:true}]}}}}',
    'clear @s', 'gamemode spectator @s',
    f'tellraw @s {msg({"text": "Du bist jetzt Zuschauer – schau den anderen beim Fliegen zu.", "color": "gray"})}'])
fn('elytra/first', [
    'tag @s add mg_elytra_win', f'function {NS}:elytra/award',
    'scoreboard players operation #elytra_dl mg = #elytra_t mg', f'scoreboard players add #elytra_dl mg {_AFTER}',
    f'title @s title {tc({"text": "SIEG!", "color": "gold", "bold": True})}',
    'title @s subtitle ' + tc([{'text': 'Platz 1  ·  ', 'color': 'white'}] + _TIME),
    f'tellraw @a[tag={_T}] ' + msg({'selector': '@s', 'color': 'gold', 'bold': True}, {'text': ' fliegt als Erster durchs Ziel! ', 'color': 'yellow'}, *_TIME),
    f'tellraw @a[tag=!{_T}] ' + msg({'selector': '@s', 'color': 'gold', 'bold': True}, {'text': ' gewinnt Elytra-Rennen!', 'color': 'white'}),
    f'tellraw {_RACE} ' + msg({'text': 'Ihr habt noch 3 Minuten, um ins Ziel zu kommen!', 'color': 'red'}),
    f'execute as {_RACE} at @s run playsound minecraft:entity.wither.spawn master @s ~ ~ ~ 0.4 1.6'])

# the win is booked the moment it is decided, so leaving the round afterwards cannot cost it
fn('elytra/award', ['scoreboard players add @s mg_wins 1', 'scoreboard players add @s mg_coins 15'])

# ---- solo run: against the clock, personal best, never a win; coins capped at 2 per finish (+3 for a new record)
pb_register(_K, 'Elytra-Rennen', 'dark_aqua')
fn('elytra/solo_fin', [          # as the player who flew through the finish ring
    'scoreboard players operation #pbv mg = #elytra_t mg', f'scoreboard players remove #pbv mg {_GO}',
    *pb_fmt('#pbv mg', 'elys'),
    f'tellraw @s ' + msg({'text': 'Ziel! ', 'color': 'aqua', 'bold': True}, {'text': 'Alle 15 Ringe in ', 'color': 'gray'}, *pb_txt('elys', 'yellow'),
                         {'text': '  +2 Münzen', 'color': 'yellow'}),
    'scoreboard players add @s mg_coins 2',
    f'function {NS}:elytra/pb',
    'execute if score #pbn mg matches 1 run scoreboard players add @s mg_coins 3',
    f'execute if score #pbn mg matches 1 run tellraw @s ' + msg({'text': 'Rekord-Bonus: ', 'color': 'gold'}, {'text': '+3 Münzen', 'color': 'yellow'}),
    'title @s subtitle ' + tc([{'text': 'Zeit: ', 'color': 'white'}] + pb_txt('elys', 'yellow')),
    'execute if score #pbn mg matches 1 run title @s subtitle ' + tc([{'text': '★ Neuer Rekord: ', 'color': 'gold', 'bold': True}] + pb_txt('elys', 'yellow')),
    'playsound minecraft:ui.toast.challenge_complete master @s ~ ~ ~ 1 1',
    'summon minecraft:firework_rocket ~ ~1 ~ {LifeTime:15,FireworksItem:{id:"minecraft:firework_rocket",count:1,components:{"minecraft:fireworks":{flight_duration:1,explosions:[{shape:"star",colors:[I;16766720,65535],has_trail:true}]}}}}',
    'clear @s', 'gamemode spectator @s',
    f'function {NS}:{_K}/end'])          # solo -> elytra/solo_end (title, state 3, back to the hub in 5 s)
fn('elytra/solo_time', [         # 6 minutes over without reaching the finish
    f'execute as {_RACE} run tellraw @s ' + msg({'text': 'Zeit abgelaufen! ', 'color': 'red', 'bold': True}, {'text': 'Du hast ', 'color': 'gray'},
                                               {'score': {'name': '@s', 'objective': 'mg_elytra_p'}, 'color': 'gold', 'bold': True},
                                               {'text': f' von {_N} Ringen geschafft – keine Wertung.', 'color': 'gray'}),
    f'execute as {_RACE} run title @s subtitle ' + tc([{'text': 'Zeit abgelaufen · Ring ', 'color': 'red'},
                                                      {'score': {'name': '@s', 'objective': 'mg_elytra_p'}, 'color': 'gold', 'bold': True},
                                                      {'text': f'/{_N}', 'color': 'gold'}]),
    f'function {NS}:{_K}/end'])
fn('elytra/solo_info', [         # as the player at "LOS!": show the record to beat
    *pb_fmt('@s mg_elytra_pb', 'elyb'),
    'execute if score @s mg_elytra_pb matches 1.. run tellraw @s ' + msg({'text': 'Solo-Lauf gegen die Uhr! ', 'color': 'aqua', 'bold': True},
                                                                        {'text': 'Deine Bestzeit: ', 'color': 'gray'}, *pb_txt('elyb', 'gold'),
                                                                        {'text': ' – schaffst du sie?', 'color': 'gray'}),
    'execute unless score @s mg_elytra_pb matches 1.. run tellraw @s ' + msg({'text': 'Solo-Lauf gegen die Uhr! ', 'color': 'aqua', 'bold': True},
                                                                            {'text': 'Flieg durch alle 15 Ringe und stell deine erste Bestzeit auf. Du hast 6 Minuten.', 'color': 'gray'})])

# crashes / respawn
_rsp = ['scoreboard players set @s mg_elytra_g 0']
_nexts = [_RD[0]['c']] + [d['c'] for d in _RD[1:]]
_rsp.append(f'execute if score @s mg_elytra_p matches 0 run {OW} tp @s {_c3(_START)} facing {_c3(_RD[0]["c"])}')
for _i, _d in enumerate(_RD[:-1]):
    px, py, pz = _d['pad']
    _rsp.append(f'execute if score @s mg_elytra_p matches {_d["k"]} run {OW} tp @s {px + 0.5} {py + 1} {pz + 0.5} facing {_c3(_RD[_i + 1]["c"])}')
_rsp += [f'execute if score #elytra_t mg matches {_GO}.. store result score #elytra_fw mg run clear @s {_FW} 0',
         f'execute if score #elytra_t mg matches {_GO}.. if score #elytra_fw mg matches 0 run give @s {_FW} 1',
         'execute at @s run playsound minecraft:entity.enderman.teleport master @s ~ ~ ~ 0.8 1.2']
fn('elytra/respawn', _rsp)
for _n, _m in (('low', 'Abgestürzt!'), ('ground', 'Bodenkontakt!'), ('out', 'Außerhalb der Strecke!')):
    fn(f'elytra/crash_{_n}', [
        'execute at @s run particle minecraft:poof ~ ~0.5 ~ 0.4 0.4 0.4 0.05 20',
        'execute at @s run playsound minecraft:entity.player.big_fall master @s ~ ~ ~ 1 0.8',
        'title @s times 0 30 10', f'title @s title {tc({"text": "✖", "color": "red", "bold": True})}',
        f'title @s subtitle {tc([{"text": _m + " ", "color": "red", "bold": True}, {"text": "Zurück zum letzten Ring", "color": "gray"}])}',
        f'function {NS}:elytra/respawn'])
fn('elytra/died', [
    'scoreboard players set @s mg_deaths 0', f'item replace entity @s armor.chest with {_ELY}',
    'effect give @s minecraft:saturation infinite 0 true', 'effect give @s minecraft:resistance infinite 4 true', 'effect give @s minecraft:weakness infinite 255 true',
    'execute if entity @s[tag=mg_elytra_lead] run effect give @s minecraft:glowing infinite 0 true',
    f'execute if score #elytra_t mg matches {_GO}.. run give @s {_FW} 2',
    f'function {NS}:elytra/respawn'])
fn('elytra/pl', [
    f'execute if score @s mg_deaths matches 1.. run return run function {NS}:elytra/died',
    f'execute if entity @s[y=-64,dy={_LOW + 64}] run return run function {NS}:elytra/crash_low',
    f'execute unless entity @s[x={EX - 62},y=90,z={EZ - 62},dx=124,dy=115,dz=124] run return run function {NS}:elytra/crash_out',
    # 26.3 (pack format 121) renamed the predicate key "condition" to "type"; 26.1 test servers still need "condition"
    'execute store success score #elytra_og mg if predicate {' + ('type' if MIN_FORMAT >= 121 else 'condition') + ':"minecraft:entity_properties",entity:"this",predicate:{flags:{is_on_ground:true}}}',
    f'execute if score #elytra_og mg matches 1 at @s if block ~ ~-0.5 ~ minecraft:{_SAFE} run scoreboard players set #elytra_og mg 0',
    'execute if score #elytra_og mg matches 0 run scoreboard players set @s mg_elytra_g 0',
    'execute if score #elytra_og mg matches 1 run scoreboard players add @s mg_elytra_g 1',
    f'execute if score @s mg_elytra_g matches 8.. run function {NS}:elytra/crash_ground'])

# countdown on the tower
def _cd(num, col, gate, pitch):
    return ([_gate(gate), f'title @a[tag={_T}] times 0 22 4', f'title @a[tag={_T}] title {tc({"text": num, "color": col, "bold": True})}',
             f'title @a[tag={_T}] subtitle {tc({"text": "Gleich öffnet sich das Tor ...", "color": "gray"})}',
             f'execute as @a[tag={_T}] at @s run playsound minecraft:block.note_block.pling master @s ~ ~ ~ 1 {pitch}'])
fn('elytra/cd3', _cd('3', 'red', 'red_stained_glass', 0.7))
fn('elytra/cd2', _cd('2', 'gold', 'orange_stained_glass', 0.85))
fn('elytra/cd1', _cd('1', 'yellow', 'yellow_stained_glass', 1.0))
fn('elytra/go', [
    _gate('air'),
    f'title @a[tag={_T}] times 0 30 10', f'title @a[tag={_T}] title {tc({"text": "LOS!", "color": "green", "bold": True})}',
    f'title @a[tag={_T}] subtitle {tc({"text": "Spring vom Turm und gleite durch Ring 1!", "color": "white"})}',
    f'execute as @a[tag={_T}] at @s run playsound minecraft:block.note_block.pling master @s ~ ~ ~ 1 2',
    f'execute as @a[tag={_T}] at @s run playsound minecraft:entity.firework_rocket.launch master @s ~ ~ ~ 1 1',
    f'give {_RACE} {_FW} 3',
    f'execute if score #elytra_np mg matches ..1 as {_RACE} run function {NS}:elytra/solo_info',
    f'tellraw @a[tag={_T}] ' + msg({'text': 'Tipp: ', 'color': 'yellow'}, {'text': 'Lauf über die Kante und drück in der Luft ', 'color': 'gray'},
                                   {'text': 'Springen', 'color': 'white'}, {'text': ' zum Gleiten. ', 'color': 'gray'},
                                   {'text': 'Rechtsklick mit Rakete', 'color': 'white'}, {'text': ' = Schub. Die Funken zeigen zum nächsten Ring.', 'color': 'gray'}),
    f'{OW} particle minecraft:firework {EX - 44.5} {_TOWER_TOP + 3} {EZ - 39.5} 0.3 2 4 0.05 60 force'])

_ab_race = tc([{'text': 'Ring ', 'color': 'gray'}, {'score': {'name': '@s', 'objective': 'mg_elytra_p'}, 'color': 'gold', 'bold': True},
               {'text': f'/{_N}', 'color': 'gold'}, {'text': '   ⏱ ', 'color': 'dark_gray'},
               {'score': {'name': '#elytra_sec', 'objective': 'mg'}, 'color': 'white'}, {'text': ' s', 'color': 'gray'}])
_ab_late = tc([{'text': 'Ring ', 'color': 'gray'}, {'score': {'name': '@s', 'objective': 'mg_elytra_p'}, 'color': 'gold', 'bold': True},
               {'text': f'/{_N}', 'color': 'gold'}, {'text': '   noch ', 'color': 'red'},
               {'score': {'name': '#elytra_rem', 'objective': 'mg'}, 'color': 'red', 'bold': True}, {'text': ' s', 'color': 'red'}])
_ab_fin = tc([{'text': 'Im Ziel  ·  Platz ', 'color': 'aqua'}, {'score': {'name': '@s', 'objective': 'mg_elytra_pl'}, 'color': 'gold', 'bold': True}])
fn('elytra/hud', [
    'scoreboard players operation #elytra_sec mg = #elytra_t mg', f'scoreboard players remove #elytra_sec mg {_GO}',
    'scoreboard players operation #elytra_sec mg /= #20 mg',
    'execute if score #elytra_place mg matches 1.. run scoreboard players operation #elytra_rem mg = #elytra_dl mg',
    'execute if score #elytra_place mg matches 1.. run scoreboard players operation #elytra_rem mg -= #elytra_t mg',
    'execute if score #elytra_place mg matches 1.. run scoreboard players operation #elytra_rem mg /= #20 mg',
    *_hud_fx,
    f'execute if score #elytra_place mg matches 0 as {_RACE} run title @s actionbar {_ab_race}',
    f'execute if score #elytra_place mg matches 1.. as {_RACE} run title @s actionbar {_ab_late}',
    f'execute as @a[tag={_T},tag=mg_elytra_fin] run title @s actionbar {_ab_fin}'])

# end of the race
# own end instead of the framework's elytra/end: wins/coins were already booked in elytra/first / end_time,
# so nobody keeps mg_al_elytra and the framework's draw line never shows up
_W = f'@a[tag={_T},tag=mg_elytra_win]'
fn('elytra/end_go', [
    f'tag @a[tag={_T}] remove {_AL}', f'title @a[tag={_T}] times 10 60 20', f'effect clear @a[tag={_T}] minecraft:glowing',
    f'execute as {_W} run tellraw @a[tag={_T}] ' + msg({'selector': '@s', 'color': 'gold', 'bold': True}, {'text': ' gewinnt Elytra-Rennen!', 'color': 'white'}),
    f'execute unless entity {_W} if score #elytra_place mg matches 1.. run tellraw @a[tag={_T}] ' + msg({'text': 'Der Sieger hat das Rennen schon verlassen – sein Sieg zählt trotzdem.', 'color': 'gray'}),
    f'execute unless entity {_W} if score #elytra_place mg matches 0 run tellraw @a[tag={_T}] ' + msg({'text': 'Unentschieden – niemand hat einen Ring geschafft.', 'color': 'gray'}),
    f'title @a[tag={_T}] title {tc({"text": "Spiel vorbei!", "color": "dark_aqua", "bold": True})}',
    f'execute as {_W} at @s run summon minecraft:firework_rocket ~ ~1 ~ {{LifeTime:20,FireworksItem:{{id:"minecraft:firework_rocket",count:1,components:{{"minecraft:fireworks":{{flight_duration:1,explosions:[{{shape:"large_ball",colors:[I;16766720],has_twinkle:true}}]}}}}}}}}',
    f'scoreboard players set #{_K} mg 3', f'schedule function {NS}:{_K}/finish 100t'])
fn('elytra/end_late', [f'tellraw {_RACE} ' + msg({'text': 'Zeit abgelaufen – du hast es nicht mehr ins Ziel geschafft.', 'color': 'red'}),
                       f'function {NS}:elytra/end_go'])
fn('elytra/end_time', [
    f'execute if score #elytra_np mg matches ..1 run return run function {NS}:elytra/solo_time',
    f'tellraw @a[tag={_T}] ' + msg({'text': 'Zeit abgelaufen! Niemand hat das Ziel erreicht – wer am weitesten kam, gewinnt.', 'color': 'red'}),
    'scoreboard players set #elytra_best mg 0',
    f'execute as {_RACE} run scoreboard players operation #elytra_best mg > @s mg_elytra_p',
    f'execute if score #elytra_best mg matches 1.. as {_RACE} if score @s mg_elytra_p = #elytra_best mg run tag @s add mg_elytra_win',
    f'execute as @a[tag={_T},tag=mg_elytra_win] run function {NS}:elytra/award',
    f'execute as @a[tag={_T},tag=mg_elytra_win] run tellraw @a[tag=!{_T}] ' + msg({'selector': '@s', 'color': 'gold', 'bold': True}, {'text': ' gewinnt Elytra-Rennen!', 'color': 'white'}),
    f'function {NS}:elytra/end_go'])
_warn = []
for _ticks, _txt in ((1200, 'Noch 60 Sekunden!'), (600, 'Noch 30 Sekunden!'), (200, 'Noch 10 Sekunden!')):
    _warn += [f'execute if score #elytra_place mg matches 1.. if score #elytra_r2 mg matches {_ticks} run tellraw {_RACE} {msg({"text": _txt, "color": "red", "bold": True})}',
              f'execute if score #elytra_place mg matches 1.. if score #elytra_r2 mg matches {_ticks} as {_RACE} at @s run playsound minecraft:block.note_block.basedrum master @s ~ ~ ~ 1 0.6',
              f'execute if score #elytra_place mg matches 0 if score #elytra_np mg matches 2.. if score #elytra_t mg matches {_LIMIT - _ticks} run tellraw {_RACE} {msg({"text": _txt + " Danach gewinnt, wer am weitesten ist.", "color": "red", "bold": True})}',
              f'execute if score #elytra_place mg matches 0 if score #elytra_np mg matches ..1 if score #elytra_t mg matches {_LIMIT - _ticks} run tellraw {_RACE} {msg({"text": _txt, "color": "red", "bold": True})}',
              f'execute if score #elytra_place mg matches 0 if score #elytra_np mg matches ..1 if score #elytra_t mg matches {_LIMIT - _ticks} as {_RACE} at @s run playsound minecraft:block.note_block.basedrum master @s ~ ~ ~ 1 0.6']

_game = [
    f'execute if score #elytra_t mg matches {_GO - 60} run function {NS}:elytra/cd3',
    f'execute if score #elytra_t mg matches {_GO - 40} run function {NS}:elytra/cd2',
    f'execute if score #elytra_t mg matches {_GO - 20} run function {NS}:elytra/cd1',
    f'execute if score #elytra_t mg matches {_GO} run function {NS}:elytra/go',
    f'execute as @e[type=minecraft:player,tag={_AL},tag=!mg_elytra_fin] run function {NS}:elytra/pl',   # @e: only living players
    *_ring_checks,
    'scoreboard players operation #elytra_m mg = #elytra_t mg', 'scoreboard players operation #elytra_m mg %= #4 mg',
    f'execute if score #elytra_m mg matches 0 if score #elytra_t mg matches {_GO}.. run function {NS}:elytra/hud',
    f'execute if score #elytra_m mg matches 2 run {OW} kill @e[type=minecraft:item,x={EX - 62},y=90,z={EZ - 62},dx=124,dy=115,dz=124]',
    'execute if score #elytra_place mg matches 1.. run scoreboard players operation #elytra_r2 mg = #elytra_dl mg',
    'execute if score #elytra_place mg matches 1.. run scoreboard players operation #elytra_r2 mg -= #elytra_t mg',
    *_warn,
    f'execute unless score #{_K} mg matches 2 run return 0',
    f'execute unless entity @a[tag={_T}] run return run function {NS}:elytra/end_go',
    f'execute if score #elytra_place mg matches 1.. unless entity {_RACE} run return run function {NS}:elytra/end_go',
    f'execute if score #elytra_place mg matches 1.. if score #elytra_r2 mg matches ..0 run return run function {NS}:elytra/end_late',
    f'execute if score #elytra_place mg matches 0 if score #elytra_t mg matches {_LIMIT}.. run return run function {NS}:elytra/end_time',
]

_setup = [
    'scoreboard players set #elytra_place mg 0', 'scoreboard players set #elytra_best mg 0', 'scoreboard players set #elytra_dl mg 0',
    'scoreboard players set #elytra_r2 mg 1', 'scoreboard players set #elytra_sec mg 0',
    'tag @a remove mg_elytra_fin', 'tag @a remove mg_elytra_win', 'tag @a remove mg_elytra_lead',
    f'scoreboard players set @a[tag={_T}] mg_elytra_p 0', f'scoreboard players set @a[tag={_T}] mg_elytra_g 0',
    f'scoreboard players set @a[tag={_T}] mg_elytra_pl 0',
    f'{OW} tp @a[tag={_T}] {EX - 49.5} {_TOWER_TOP + 1} {EZ - 39.5}',
    f'{OW} spreadplayers {EX - 49.5} {EZ - 39.5} 1 3 false @a[tag={_T}]',
    f'execute as @a[tag={_T}] at @s run tp @s ~ ~ ~ facing {_c3(_RD[0]["c"])}',
    f'item replace entity @a[tag={_T}] armor.chest with {_ELY}',
    f'effect give @a[tag={_T}] minecraft:saturation infinite 0 true',
    f'effect give @a[tag={_T}] minecraft:resistance infinite 4 true', f'effect give @a[tag={_T}] minecraft:weakness infinite 255 true',
]

EXTRA_LOAD.extend(['scoreboard objectives add mg_elytra_p dummy', 'scoreboard objectives add mg_elytra_g dummy',
                   'scoreboard objectives add mg_elytra_pl dummy'])
ENTER_LINES.extend(['tag @s remove mg_elytra_fin', 'tag @s remove mg_elytra_win', 'tag @s remove mg_elytra_lead'])

party(_K, 'Elytra-Rennen', 'dark_aqua', (EX, EY, EZ), trig=65, prof='toolsmith', sub='15 Ringe · Raketen · auch solo',
      menu='Flieg durch die Ringe – auch solo',
      info='Gleite mit der Elytra vom Startturm durch alle 15 Ringe – in der richtigen Reihenfolge. Raketen geben Schub '
           '(Nachschub an Ring 5 und 10). Absturz oder Bodenkontakt = zurück zum letzten Ring. Wer zuerst durchs goldene Ziel fliegt, gewinnt! '
           'Auch solo spielbar: Flieg gegen die Uhr und knack deine Bestzeit.',
      title_sub='Flieg durch alle 15 Ringe!', size=60, build=_build, setup=_setup, game=_game, custom_end=True,
      spect=_SPECT, coins_win=0, cleanup=[_gate('red_stained_glass')], solo=True,
      solo_end=[f'effect clear @a[tag={_T}] minecraft:glowing', f'tag @a[tag={_T}] remove {_AL}', f'title @a[tag={_T}] times 10 60 20'])
