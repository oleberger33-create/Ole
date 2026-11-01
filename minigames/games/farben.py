# Farbenparty (block party): a 32x32 floor of coloured concrete tiles. Music plays, then a colour is announced -
# get onto a tile of that colour before the countdown ends, everything else vanishes. Last one standing wins.
FB = (72000, Y, 0)
_cx, _cy, _cz = FB
_X0, _Z0 = _cx - 16, _cz - 16          # floor: 32x32 blocks = 16x16 tiles of 2x2, x/z _X0.._X0+31
_X1, _Z1 = _X0 + 31, _Z0 + 31
_FL = f'{_X0} {_cy} {_Z0} {_X1} {_cy} {_Z1}'
_AL, _T = 'mg_al_farben', 'mg_farben'
_SPECT = (_cx, _cy + 14, _cz)
_STO = f'{NS}:farben'

# colour id -> (German name, upper case, text colour, bossbar colour)
_COL = {
    'white': ('Weiß', 'WEISS', '#FFFFFF', 'white'), 'orange': ('Orange', 'ORANGE', '#F9801D', 'yellow'),
    'magenta': ('Magenta', 'MAGENTA', '#D35BC9', 'purple'), 'light_blue': ('Hellblau', 'HELLBLAU', '#5CC8EE', 'blue'),
    'yellow': ('Gelb', 'GELB', '#FED83D', 'yellow'), 'lime': ('Hellgrün', 'HELLGRÜN', '#8BD42A', 'green'),
    'pink': ('Rosa', 'ROSA', '#F7A1BC', 'pink'), 'gray': ('Grau', 'GRAU', '#8A8A8A', 'white'),
    'light_gray': ('Hellgrau', 'HELLGRAU', '#C8C8C8', 'white'), 'cyan': ('Türkis', 'TÜRKIS', '#1FB5B5', 'blue'),
    'purple': ('Lila', 'LILA', '#A45ADB', 'purple'), 'blue': ('Blau', 'BLAU', '#5361E8', 'blue'),
    'brown': ('Braun', 'BRAUN', '#A0693F', 'red'), 'green': ('Grün', 'GRÜN', '#6E9420', 'green'),
    'red': ('Rot', 'ROT', '#F04438', 'red'), 'black': ('Schwarz', 'SCHWARZ', '#555555', 'white'),
}
# palettes of 8 clearly different colours; the last one (similar hues) only from round 6 on
_PAL = [['red', 'orange', 'yellow', 'lime', 'light_blue', 'blue', 'purple', 'white'],
        ['red', 'yellow', 'green', 'cyan', 'blue', 'magenta', 'white', 'black'],
        ['orange', 'lime', 'pink', 'light_blue', 'purple', 'yellow', 'brown', 'white'],
        ['red', 'blue', 'yellow', 'lime', 'white', 'black', 'purple', 'orange'],
        ['pink', 'magenta', 'cyan', 'lime', 'yellow', 'orange', 'light_gray', 'blue'],
        ['light_blue', 'cyan', 'blue', 'purple', 'magenta', 'pink', 'red', 'orange']]
for _k, _p in enumerate(_PAL):
    _d = {}
    for _s, _c in enumerate(_p):
        _n, _u, _h, _b = _COL[_c]
        _d.update({f'c{_s}': _c, f'n{_s}': _n, f'u{_s}': _u, f'h{_s}': _h, f'b{_s}': _b})
    fn(f'farben/pal/{_k}', [f'data modify storage {_STO} pal set value {tc(_d)}'])
fn('farben/pal', [f'execute if score #farben_pl mg matches {k} run return run function {NS}:farben/pal/{k}' for k in range(len(_PAL))])

# ---- floor patterns: 16x16 tile grids with colour slots 0..7 (the palette decides the real colours at runtime)
_R = random.Random(4711)
_c = 7.5
def _latin():
    g = [[0] * 16 for _ in range(16)]
    for bi in range(4):
        for bj in range(4):
            v = list(range(8)) * 2; _R.shuffle(v)
            for k in range(16):
                g[bi * 4 + k // 4][bj * 4 + k % 4] = v[k]
    return lambda i, j, g=g: g[i][j]
def _kaleido():
    g = [[0] * 8 for _ in range(8)]
    for bi in range(2):
        for bj in range(2):
            v = list(range(8)) * 2; _R.shuffle(v)
            for k in range(16):
                g[bi * 4 + k // 4][bj * 4 + k % 4] = v[k]
    return lambda i, j, g=g: g[min(i, 15 - i)][min(j, 15 - j)]
_PATTERNS = [                     # each 4x4-tile block holds every colour where possible -> every colour is close to everyone
    _latin(), _latin(), _latin(), _latin(), _latin(), _latin(), _kaleido(), _kaleido(),
    lambda i, j: (i + j) % 8,                                                          # diagonal stripes
    lambda i, j: (i + abs(j % 8 - 4)) % 8,                                             # chevrons
    lambda i, j: int(abs(i - _c) + abs(j - _c)) % 8,                                   # diamonds
    lambda i, j: (i // 2 + 3 * (j // 2)) % 8,                                          # mosaic
    lambda i, j: (i + round(2.2 * math.sin(j * 0.7))) % 8,                             # waves
    lambda i, j: (i % 4) + 4 * ((j // 2) % 2),                                         # woven bands
    lambda i, j: (int(math.hypot(i - _c, j - _c)) % 4) * 2 + ((i // 2 + j // 2) % 2),  # checkered circles
    lambda i, j: (int(max(abs(i - _c), abs(j - _c))) % 4) * 2 + ((i // 2 + j // 2) % 2),  # checkered squares
]
def _fills(f):
    """merge equal tiles into rectangles (runs along x, then identical runs along z)"""
    rows = []
    for j in range(16):
        runs, i = [], 0
        while i < 16:
            s, k = f(i, j), i
            while k + 1 < 16 and f(k + 1, j) == s:
                k += 1
            runs.append((i, k, s))
            i = k + 1
        rows.append(runs)
    out, open_ = [], {}
    for j, runs in enumerate(rows + [[]]):
        nxt = {}
        for r in runs:
            nxt[r] = open_.pop(r, j)
        for (i0, i1, s), j0 in open_.items():
            out.append(f'$fill {_X0 + 2 * i0} {_cy} {_Z0 + 2 * j0} {_X0 + 2 * i1 + 1} {_cy} {_Z0 + 2 * j - 1} minecraft:$(c{s})_concrete')
        open_ = nxt
    return out
for _k, _f in enumerate(_PATTERNS):
    fn(f'farben/p/{_k}', _fills(_f))
fn('farben/pat', [f'execute if score #farben_p mg matches {k} run return run function {NS}:farben/p/{k} with storage {_STO} pal' for k in range(len(_PATTERNS))])

# ---- drop: remove every colour except the announced one
for _c1 in _COL:
    fn(f'farben/d/{_c1}', [f'{OW} fill {_FL} minecraft:air replace minecraft:{_c2}_concrete' for _c2 in _COL if _c2 != _c1])

# ---- map
_b = [f'{OW} kill @e[type=minecraft:text_display,tag=mg_farbenh]']
_b += clear_box(_cx - 24, _cy - 22, _cz - 24, _cx + 24, _cy + 14, _cz + 24, 6)
def _sq(d, y, blk, h=1):
    """square ring d blocks outside the floor"""
    x0, z0, x1, z1 = _X0 - d, _Z0 - d, _X1 + d, _Z1 + d
    y2 = y + h - 1
    return [f'{OW} fill {x0} {y} {z0} {x1} {y2} {z0} minecraft:{blk}', f'{OW} fill {x0} {y} {z1} {x1} {y2} {z1} minecraft:{blk}',
            f'{OW} fill {x0} {y} {z0} {x0} {y2} {z1} minecraft:{blk}', f'{OW} fill {x1} {y} {z0} {x1} {y2} {z1} minecraft:{blk}']
_b += _sq(1, _cy, 'sea_lantern') + _sq(2, _cy, 'smooth_quartz') + _sq(4, _cy, 'smooth_quartz')
_b += _sq(1, _cy - 1, 'smooth_quartz') + _sq(2, _cy - 1, 'smooth_quartz') + _sq(3, _cy - 1, 'smooth_quartz') + _sq(4, _cy - 1, 'quartz_bricks')
_b += _sq(3, _cy - 2, 'sea_lantern') + _sq(4, _cy - 2, 'smooth_quartz') + _sq(4, _cy - 3, 'smooth_quartz_slab')
_b += _sq(1, _cy + 1, 'barrier', 3) + _sq(2, _cy + 1, 'white_stained_glass')
# rainbow trim (ring 3): two-block segments cycling through the colours
_rain = ['red', 'orange', 'yellow', 'lime', 'green', 'cyan', 'light_blue', 'blue', 'purple', 'magenta', 'pink']
_per = []
_x0, _z0, _x1, _z1 = _X0 - 3, _Z0 - 3, _X1 + 3, _Z1 + 3
_per += [(x, _z0) for x in range(_x0, _x1)] + [(_x1, z) for z in range(_z0, _z1)] + [(x, _z1) for x in range(_x1, _x0, -1)] + [(_x0, z) for z in range(_z1, _z0, -1)]
for _i in range(0, len(_per), 2):
    _seg = _per[_i:_i + 2]
    _blk = _rain[(_i // 2) % len(_rain)]
    (_ax, _az), (_bx, _bz) = _seg[0], _seg[-1]
    _b.append(f'{OW} fill {_ax} {_cy} {_az} {_bx} {_cy} {_bz} minecraft:{_blk}_concrete')
# corner towers with speakers and light crowns
for _tx, _tz in ((_X0 - 4, _Z0 - 4), (_X1 + 4, _Z0 - 4), (_X0 - 4, _Z1 + 4), (_X1 + 4, _Z1 + 4)):
    _b += [f'{OW} fill {_tx} {_cy - 8} {_tz} {_tx} {_cy + 6} {_tz} minecraft:quartz_pillar',
           f'{OW} setblock {_tx} {_cy - 9} {_tz} minecraft:sea_lantern', f'{OW} setblock {_tx} {_cy - 10} {_tz} minecraft:end_rod[facing=down]',
           f'{OW} setblock {_tx} {_cy + 7} {_tz} minecraft:sea_lantern', f'{OW} setblock {_tx} {_cy + 8} {_tz} minecraft:end_rod',
           f'{OW} fill {_tx - 1} {_cy + 6} {_tz - 1} {_tx + 1} {_cy + 6} {_tz + 1} minecraft:magenta_stained_glass replace minecraft:air',
           f'{OW} fill {_tx - 1} {_cy + 1} {_tz - 1} {_tx + 1} {_cy + 2} {_tz + 1} minecraft:note_block replace minecraft:air',
           f'{OW} fill {_tx - 1} {_cy + 3} {_tz - 1} {_tx + 1} {_cy + 3} {_tz + 1} minecraft:jukebox replace minecraft:air']
# glowing light strips along the middle of each side
for _sx, _sz in ((_cx, _Z0 - 4), (_cx, _Z1 + 4)):
    _b += [f'{OW} fill {_sx - 6} {_cy + 1} {_sz} {_sx + 5} {_cy + 1} {_sz} minecraft:end_rod']
for _sx, _sz in ((_X0 - 4, _cz), (_X1 + 4, _cz)):
    _b += [f'{OW} fill {_sx} {_cy + 1} {_sz - 6} {_sx} {_cy + 1} {_sz + 5} minecraft:end_rod']
# disco pit far below (only spectators see it)
_b += [f'{OW} fill {_X0 - 4} {_cy - 20} {_Z0 - 4} {_X1 + 4} {_cy - 20} {_Z1 + 4} minecraft:black_concrete']
for _gx in range(_X0, _X1 + 1, 6):
    _b.append(f'{OW} fill {_gx} {_cy - 20} {_Z0 - 4} {_gx} {_cy - 20} {_Z1 + 4} minecraft:purple_stained_glass')
for _gz in range(_Z0, _Z1 + 1, 6):
    _b.append(f'{OW} fill {_X0 - 4} {_cy - 20} {_gz} {_X1 + 4} {_cy - 20} {_gz} minecraft:cyan_stained_glass')
_b.append(f'{OW} fill {_X0 - 4} {_cy - 21} {_Z0 - 4} {_X1 + 4} {_cy - 21} {_Z1 + 4} minecraft:sea_lantern')
# title holograms
_letters = [{'text': ch, 'color': _COL[_rain[i % len(_rain)]][2], 'bold': True} for i, ch in enumerate('FARBENPARTY')]
_b += [holo('mg_farbenh', f'{_cx}.5', _cy + 10, f'{_Z0 - 4}.5', [{'text': ''}] + _letters, 4.0),
       holo('mg_farbenh', f'{_cx}.5', _cy + 8.6, f'{_Z0 - 4}.5', {'text': 'Musik stoppt → Farbe merken → drauf stellen!', 'color': 'white'}, 1.4)]
# starting floor
_b += [f'function {NS}:farben/pal/0', f'scoreboard players set #farben_p mg 8', f'function {NS}:farben/p/8 with storage {_STO} pal']

# ---- music: a chiptune loop, one step every 3 ticks (32 steps)
_lead = [13, None, 17, None, 20, 17, 15, None, 13, None, 10, None, 13, 15, 17, None,
         12, None, 15, None, 20, 15, 13, None, 10, None, 8, 10, 13, None, 13, None]
_bass = {0: 1, 4: 1, 8: 10, 12: 10, 16: 6, 20: 6, 24: 8, 28: 8}
def _p(n):
    return round(2 ** ((n - 12) / 12), 3)
_mus = [f'scoreboard players add #farben_m mg 1', f'execute if score #farben_m mg matches 96.. run scoreboard players set #farben_m mg 0']
_ps = f'as @a[tag={_T}] at @s run playsound'
for _st in range(32):
    _t = _st * 3
    if _lead[_st] is not None:
        _mus.append(f'execute if score #farben_m mg matches {_t} {_ps} minecraft:block.note_block.bit record @s ~ ~ ~ 0.55 {_p(_lead[_st])}')
    if _st in _bass:
        _mus.append(f'execute if score #farben_m mg matches {_t} {_ps} minecraft:block.note_block.bass record @s ~ ~ ~ 0.9 {_p(_bass[_st])}')
    if _st % 4 == 0:
        _mus.append(f'execute if score #farben_m mg matches {_t} {_ps} minecraft:block.note_block.basedrum record @s ~ ~ ~ 0.7 1')
    if _st % 4 == 2:
        _mus.append(f'execute if score #farben_m mg matches {_t} {_ps} minecraft:block.note_block.hat record @s ~ ~ ~ 0.5 1.2')
fn('farben/music', _mus)

# ---- round flow.  #farben_ph: 3 intro, 0 music, 1 countdown, 2 drop/hold.  #farben_pt: ticks left in the phase
_BB = f'bossbar set {NS}:farben'
fn('farben/round', [
    'scoreboard players add #farben_r mg 1', 'scoreboard players set #farben_ph mg 0', 'scoreboard players set #farben_m mg -1',
    'execute store result score #farben_pt mg run random value 50..110',
    f'execute store result score #farben_np mg run random value 0..{len(_PATTERNS) - 1}',
    'execute if score #farben_np mg = #farben_p mg run scoreboard players add #farben_np mg 1',
    f'execute if score #farben_np mg matches {len(_PATTERNS)}.. run scoreboard players set #farben_np mg 0',
    'scoreboard players operation #farben_p mg = #farben_np mg',
    f'execute store result score #farben_pl mg run random value 0..{len(_PAL) - 2}',
    f'execute if score #farben_r mg matches 6.. store result score #farben_pl mg run random value 0..{len(_PAL) - 1}',
    f'function {NS}:farben/pal', f'function {NS}:farben/pat',
    f'clear @a[tag={_AL}]', 'experience set @a[tag=mg_farben] 0 levels',
    f'{OW} kill @e[type=minecraft:item,x={_X0 - 6},y={_cy - 30},z={_Z0 - 6},dx=44,dy=45,dz=44]',
    f'{_BB} name [{{"text":"Runde ","color":"light_purple","bold":true}},{{"score":{{"name":"#farben_r","objective":"mg"}},"color":"white","bold":true}},{{"text":"  ♪ Tanz! Gleich kommt die Farbe …","color":"gray","bold":false}}]',
    f'{_BB} color pink', f'{_BB} max 1', f'{_BB} value 1',
    f'title @a[tag={_T}] actionbar [{{"text":"♪ Runde ","color":"light_purple"}},{{"score":{{"name":"#farben_r","objective":"mg"}},"color":"white","bold":true}},{{"text":" ♪","color":"light_purple"}}]',
    f'execute as @a[tag={_T}] at @s run playsound minecraft:block.beacon.activate master @s ~ ~ ~ 0.6 1.6',
])
fn('farben/pick', [f'$execute if score #farben_s mg matches {s} run data modify storage {_STO} cur set value '
                   f'{{c:"$(c{s})",n:"$(n{s})",u:"$(u{s})",h:"$(h{s})",b:"$(b{s})"}}' for s in range(8)])
_name = '{"text":"$(u)","color":"$(h)","bold":true,"italic":false}'
fn('farben/announce', [
    f'title @a[tag={_T}] times 2 40 6',
    f'$title @a[tag={_T}] subtitle {{"text":"Stell dich auf $(n)!","color":"white"}}',
    f'$title @a[tag={_T}] title {{"text":"$(u)","color":"$(h)","bold":true}}',
    *[f'$item replace entity @a[tag={_AL}] hotbar.{i} with minecraft:$(c)_concrete[minecraft:custom_name={_name}]' for i in range(9)],
    f'${_BB} name [{{"text":"Runde ","color":"light_purple","bold":true}},{{"score":{{"name":"#farben_r","objective":"mg"}},"color":"white","bold":true}},{{"text":"  ▶ ","color":"gray","bold":false}},{{"text":"$(u)","color":"$(h)","bold":true}},{{"text":" ◀","color":"gray","bold":false}}]',
    f'${_BB} color $(b)',
])
fn('farben/ab', ['$title @a[tag=mg_farben] actionbar [{"text":"▶  ","color":"$(h)"},{"text":"$(u)","color":"$(h)","bold":true},{"text":"  ◀","color":"$(h)"}]'])
fn('farben/choose', [
    'execute store result score #farben_s mg run random value 0..7',
    f'function {NS}:farben/pick with storage {_STO} pal',
    # countdown: 5 s in round 1, 0.35 s shorter each round, at least 1.5 s
    'scoreboard players operation #farben_d mg = #farben_r mg', 'scoreboard players remove #farben_d mg 1',
    'scoreboard players operation #farben_d mg *= #farben_7 mg',
    'scoreboard players set #farben_pt mg 100', 'scoreboard players operation #farben_pt mg -= #farben_d mg',
    'execute if score #farben_pt mg matches ..30 run scoreboard players set #farben_pt mg 30',
    f'execute store result bossbar {NS}:farben max run scoreboard players get #farben_pt mg',
    f'execute store result bossbar {NS}:farben value run scoreboard players get #farben_pt mg',
    f'function {NS}:farben/announce with storage {_STO} cur',
    f'function {NS}:farben/ab with storage {_STO} cur',
    f'execute as @a[tag={_T}] at @s run playsound minecraft:block.note_block.pling master @s ~ ~ ~ 1 2',
    f'execute as @a[tag={_T}] at @s run playsound minecraft:entity.experience_orb.pickup master @s ~ ~ ~ 0.8 0.6',
    'scoreboard players set #farben_ph mg 1',
])
_cnt = ['scoreboard players remove #farben_pt mg 1',
        f'execute store result bossbar {NS}:farben value run scoreboard players get #farben_pt mg',
        f'execute if score #farben_pt mg matches ..0 run return run function {NS}:farben/drop']
for _s in range(1, 6):
    _cnt.append(f'execute if score #farben_pt mg matches {20 * _s - 19}..{20 * _s} run experience set @a[tag={_AL}] {_s} levels')
for _t in (20, 40, 60, 80):
    _cnt.append(f'execute if score #farben_pt mg matches {_t} {_ps} minecraft:block.note_block.hat master @s ~ ~ ~ 1 {1.0 + (100 - _t) / 160:.2f}')
for _t in (15, 10, 5):
    _cnt.append(f'execute if score #farben_pt mg matches {_t} {_ps} minecraft:block.note_block.pling master @s ~ ~ ~ 0.8 {2.0 - _t / 40:.2f}')
_cnt.append(f'execute if score #farben_pt mg matches 20 run function {NS}:farben/ab with storage {_STO} cur')
_cnt.append(f'execute if score #farben_pt mg matches 50 run function {NS}:farben/ab with storage {_STO} cur')
fn('farben/ph_count', _cnt)
fn('farben/dropc', [f'$function {NS}:farben/d/$(c)',
                    f'${_BB} name [{{"text":"$(u)","color":"$(h)","bold":true}},{{"text":" bleibt – alles andere ist weg!","color":"gray","bold":false}}]'])
fn('farben/drop', [
    f'function {NS}:farben/dropc with storage {_STO} cur',
    f'clear @a[tag={_AL}]', f'experience set @a[tag={_T}] 0 levels', f'{_BB} value 0',
    f'title @a[tag={_T}] clear',
    f'execute as @a[tag={_T}] at @s run playsound minecraft:block.glass.break master @s ~ ~ ~ 1 0.6',
    f'execute as @a[tag={_T}] at @s run playsound minecraft:entity.breeze.wind_burst master @s ~ ~ ~ 0.7 0.8',
    'scoreboard players set #farben_ph mg 2', 'scoreboard players set #farben_pt mg 50',
])
fn('farben/fall', [
    f'tag @s remove {_AL}', 'tag @s add mg_farben_fell', 'scoreboard players set @s mg_deaths 0',
    'gamemode spectator @s', 'clear @s', 'experience set @s 0 levels',
    f'{OW} tp @s {_SPECT[0]}.5 {_SPECT[1]} {_SPECT[2]}.5 0 60',
    f'title @s title {tc({"text": "Runtergefallen!", "color": "red", "bold": True})}',
    f'title @s subtitle {tc({"text": "Mal sehen, ob die anderen es schaffen …", "color": "gray"})}',
    'execute at @s run playsound minecraft:block.note_block.didgeridoo master @s ~ ~ ~ 1 0.6',
    f'tellraw @a[tag={_T}] {msg({"text": "✖ ", "color": "red"}, {"selector": "@s", "color": "white"}, {"text": " ist gefallen!", "color": "gray"})}',
])
fn('farben/revive', [
    f'tag @a[tag={_T},tag=mg_farben_fell] add mg_farben_rev', f'tag @a[tag=mg_farben_rev] add {_AL}', 'tag @a[tag=mg_farben_rev] remove mg_farben_fell',
    f'tellraw @a[tag={_T}] {msg({"text": "Alle sind gefallen – diese Runde zählt nicht! Weiter geht's.", "color": "yellow"})}',
])
fn('farben/revive2', [
    'gamemode adventure @a[tag=mg_farben_rev]',
    f'{OW} spreadplayers {_cx} {_cz} 2 12 false @a[tag=mg_farben_rev]',
    'effect give @a[tag=mg_farben_rev] minecraft:saturation infinite 0 true',
    'effect give @a[tag=mg_farben_rev] minecraft:resistance infinite 4 true',
    'title @a[tag=mg_farben_rev] title {"text":"Zurück im Spiel!","color":"green","bold":true}',
    'tag @a[tag=mg_farben_rev] remove mg_farben_rev',
])
fn('farben/elim', [
    'tag @s remove mg_farben_fell', 'scoreboard players add @s mg_coins 2',
    f'tellraw @a[tag={_T}] {msg({"selector": "@s", "color": "white"}, {"text": " ist raus! ", "color": "red"}, {"text": "Noch ", "color": "gray"}, {"score": {"name": "#farben_n", "objective": "mg"}, "color": "white"}, {"text": " übrig.", "color": "gray"})}',
])
fn('farben/eval', [
    f'execute store result score #farben_n mg if entity @a[tag={_AL}]',
    f'execute if score #farben_n mg matches 0 if entity @a[tag={_T},tag=mg_farben_fell] run function {NS}:farben/revive',
    f'execute store result score #farben_n mg if entity @a[tag={_AL}]',
    f'execute as @a[tag={_T},tag=mg_farben_fell] run function {NS}:farben/elim',
    f'execute if score #farben_n mg matches ..1 run return run function {NS}:farben/end',
    f'execute as @a[tag={_AL}] at @s run playsound minecraft:entity.player.levelup master @s ~ ~ ~ 0.6 1.4',
    f'function {NS}:farben/round',
    f'execute if entity @a[tag=mg_farben_rev] run function {NS}:farben/revive2',
])
_game = [
    # falling below the floor = out (no death screen); deaths of any other kind count too
    f'execute as @a[tag={_AL}] at @s if entity @s[y=-64,dy={_cy - 4 + 64}] run function {NS}:farben/fall',
    f'execute as @a[tag={_AL},scores={{mg_deaths=1..}}] run function {NS}:farben/fall',
    'scoreboard players remove #farben_pt mg 1',
    f'execute if score #farben_ph mg matches 3 if score #farben_pt mg matches ..0 run function {NS}:farben/round',
    f'execute if score #farben_ph mg matches 0 run function {NS}:farben/music',
    f'execute if score #farben_ph mg matches 0 if score #farben_pt mg matches ..0 run function {NS}:farben/choose',
    'execute if score #farben_ph mg matches 1 run scoreboard players add #farben_pt mg 1',
    f'execute if score #farben_ph mg matches 1 run function {NS}:farben/ph_count',
    f'execute if score #farben_ph mg matches 2 if score #farben_pt mg matches ..0 run function {NS}:farben/eval',
    # someone left (trigger 99) and at most one player is left -> end (unless a fall is still being decided)
    f'execute store result score #farben_n mg if entity @a[tag={_AL}]',
    f'execute if score #farben mg matches 2 if score #farben_n mg matches ..1 unless entity @a[tag={_T},tag=mg_farben_fell] run function {NS}:farben/end',
    'scoreboard players operation #m mg = #farben_t mg', 'scoreboard players operation #m mg %= #5 mg',
    f'execute if score #m mg matches 0 run {_BB} players @a[tag={_T}]',
]
_setup = [
    f'{OW} spreadplayers {_cx} {_cz} 3 12 false @a[tag={_T}]',
    f'effect give @a[tag={_T}] minecraft:saturation infinite 0 true',
    f'effect give @a[tag={_T}] minecraft:resistance infinite 4 true',
    'scoreboard players set #farben_r mg 0', 'scoreboard players set #farben_ph mg 3', 'scoreboard players set #farben_pt mg 70',
    'scoreboard players set #farben_7 mg 7',
    f'tag @a[tag={_T}] remove mg_farben_fell', f'tag @a[tag={_T}] remove mg_farben_rev',
    f'{_BB} name {tc({"text": "Farbenparty – gleich geht es los!", "color": "light_purple", "bold": True})}',
    f'{_BB} color pink', f'{_BB} max 1', f'{_BB} value 1', f'{_BB} players @a[tag={_T}]', f'{_BB} visible true',
]
EXTRA_LOAD.extend([f'bossbar add {NS}:farben {tc({"text": "Farbenparty"})}', f'bossbar set {NS}:farben visible false'])
ENTER_LINES.extend(['tag @s remove mg_farben_fell', 'tag @s remove mg_farben_rev'])
party('farben', 'Farbenparty', 'light_purple', FB, trig=61, prof='shepherd', sub='Musik · Farbe · Letzter gewinnt', menu='Stell dich auf die richtige Farbe',
      info='Wenn die Musik stoppt, wird eine Farbe angesagt. Stell dich schnell auf ein Feld dieser Farbe – alle anderen Felder verschwinden! Jede Runde wird die Zeit kürzer. Wer zuletzt noch steht, gewinnt.',
      title_sub='Merk dir die Farbe!', size=24, build=_b, setup=_setup, game=_game, custom_end=True,
      cleanup=[f'{_BB} players', f'{_BB} visible false', 'scoreboard players set #farben_ph mg 3'],
      spect=_SPECT)
