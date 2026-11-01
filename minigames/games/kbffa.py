# Knockback-FFA: endless drop-in mode on the floating island "Amethystkrone".
# Join any time from the hub (NPC / compass / trigger 63), leave with /trigger mg_aktion set 99 or the barrier item.
# Knockback stick, sandstone that ages (sandstone -> yellow -> orange -> red terracotta -> gone, ~8 s), ender pearl with refill
# cooldown, leather armour. Falling into the void gives the kill to the last player who hit you within 10 s
# (damage_dealt/damage_taken stats + nearest attacker). Kill streak rewards, protected spawn platform above the centre.
_K = 'kbffa'
KX, KY, KZ = 76000, Y, 0
_T, _W, _SAFE = 'mg_kbffa', 'mg_kbffa_wait', 'mg_kbffa_safe'
_TRIG = 63
_FALL_Y = KY - 12                                 # feet below this -> fallen
_BOUND = 34                                       # |dx| or |dz| beyond this -> left the arena
_BX1, _BX2, _BZ1, _BZ2, _BY1, _BY2 = KX - 40, KX + 39, KZ - 39, KZ + 39, KY - 17, KY + 23   # decay / clear box
_FL = f'{_BX1} {_BZ1} {_BX2} {_BZ2}'
_SPY = KY + 13                                    # spawn platform surface block
_BOX = f'x={_BX1},dx={_BX2 - _BX1},y={_BY1 - 50},dy={_BY2 - _BY1 + 60},z={_BZ1},dz={_BZ2 - _BZ1}'
_ZONE = f'x={KX - 7},dx=14,y={KY + 9},dy=12,z={KZ - 7},dz=14'   # protected spawn airspace (platform r=5; pads at r=9 stay outside)
_AGE = ['sandstone', 'yellow_terracotta', 'orange_terracotta', 'red_terracotta']
_COIN_CAP = 30                                    # kbffa coins per visit
_PEARL_CD = 200                                   # ticks until a thrown pearl is refilled


def _txt(text, color, **kw):
    return dict(text=text, color=color, italic=False, **kw)


def _F(x1, y1, z1, x2, y2, z2, b):
    return f'{OW} fill {KX + x1} {KY + y1} {KZ + z1} {KX + x2} {KY + y2} {KZ + z2} minecraft:{b}'


def _S(x, y, z, b):
    return f'{OW} setblock {KX + x} {KY + y} {KZ + z} minecraft:{b}'


def _disk_cols(x0, z0, r):
    s = set()
    for dz in range(-r, r + 1):
        w = int(math.floor(math.sqrt(r * r + r - dz * dz)))
        for dx in range(-w, w + 1):
            s.add((x0 + dx, z0 + dz))
    return s


def _rows(cols, y1, y2, block):
    """relative (x,z) columns -> minimal row fills from y1..y2 (relative)."""
    out, byz = [], {}
    for x, z in cols:
        byz.setdefault(z, []).append(x)
    for z in sorted(byz):
        xs = sorted(byz[z])
        start = prev = xs[0]
        for x in xs[1:]:
            if x != prev + 1:
                out.append(_F(start, y1, z, prev, y2, z, block))
                start = x
            prev = x
        out.append(_F(start, y1, z, prev, y2, z, block))
    return out


def _polar(r, a):
    return round(r * math.cos(math.radians(a))), round(r * math.sin(math.radians(a)))


# ------------------------------------------------------------------ items
_HIDE = 'minecraft:tooltip_display={hidden_components:["minecraft:enchantments","minecraft:unbreakable","minecraft:dyed_color","minecraft:can_place_on"]}'
_PLACE_ON = ['grass_block', 'moss_block', 'coarse_dirt', 'rooted_dirt', 'dirt', 'stone', 'andesite', 'tuff', 'deepslate',
             'stone_bricks', 'mossy_stone_bricks', 'polished_andesite'] + _AGE
_PLACE_C = '{blocks:[' + ','.join(f'"minecraft:{b}"' for b in _PLACE_ON) + ']}'


def _stick(level, name, color, lore, glint=False):
    return ('minecraft:stick[minecraft:enchantments={"minecraft:knockback":' + str(level) + '},minecraft:custom_name=' + tc(_txt(name, color, bold=True)) +
            ',minecraft:lore=[' + tc(_txt(lore, 'gray')) + '],minecraft:custom_data={mg_kbffa_stick:1b},' +
            ('minecraft:enchantment_glint_override=true,' if glint else '') + _HIDE + ']')


STICK = _stick(2, 'Rückstoß-Stock', 'gold', 'Rückstoß II – schubs sie ins Nichts!')
STICK2 = _stick(3, 'Donner-Stock', 'yellow', 'Rückstoß III – Belohnung für 10 Kills in Folge', glint=True)
SAND = ('minecraft:sandstone[minecraft:can_place_on=' + _PLACE_C + ',minecraft:custom_name=' + tc(_txt('Sandstein', 'yellow', bold=True)) +
        ',minecraft:lore=[' + tc(_txt('Zerfällt nach etwa 8 Sekunden', 'gray')) + '],' + _HIDE + ']')
PEARL = 'minecraft:ender_pearl[minecraft:lore=[' + tc(_txt(f'Wird {_PEARL_CD // 20} s nach dem Werfen aufgefüllt', 'gray')) + ']]'
LEAVE = ('minecraft:carrot_on_a_stick[minecraft:item_model="minecraft:barrier",minecraft:custom_name=' + tc(_txt('Spiel verlassen', 'red', bold=True)) +
         ',minecraft:lore=[' + tc(_txt('Rechtsklick: zurück in die Lobby', 'gray')) + '],minecraft:custom_data={mg_kbffa_leave:1b},minecraft:unbreakable={},' + _HIDE + ']')
_COLORS = [16711680, 3949738, 6192150, 16701501, 16351261, 13061821, 1481884, 16777215]   # red blue green yellow orange magenta cyan white
_ARMOR = []
for _i, _c in enumerate(_COLORS):
    _comp = f'[minecraft:dyed_color={_c},minecraft:unbreakable={{}},minecraft:enchantments={{"minecraft:binding_curse":1}},minecraft:enchantment_glint_override=false,{_HIDE}]'
    fn(f'{_K}/armor{_i}', [f'item replace entity @s armor.{slot} with minecraft:leather_{piece}{_comp}'
                          for slot, piece in (('head', 'helmet'), ('chest', 'chestplate'), ('legs', 'leggings'), ('feet', 'boots'))])
    _ARMOR.append(f'execute if score @s mg_kbffa_col matches {_i} run function {NS}:{_K}/armor{_i}')

# ------------------------------------------------------------------ map: "Amethystkrone"
_rng = random.Random(6376)
_b = [f'kill @e[type=minecraft:text_display,tag=mg_kbffah]', f'{OW} kill @e[type=minecraft:item,{_BOX}]',
      f'{OW} kill @e[type=minecraft:ender_pearl,{_BOX}]']
_b += clear_box(_BX1, _BY1, _BZ1, _BX2, _BY2, _BZ2, 5)
_b.append(_F(-35, 21, -35, 35, 21, 35, 'barrier'))                     # invisible ceiling (build limit)
# main island: grass top, inverted rocky cone with amethyst tip
_MAIN = _disk_cols(0, 0, 21)
_b += _rows(_MAIN, 0, 0, 'grass_block')
for dy, r, blk in ((-1, 21, 'dirt'), (-2, 20, 'dirt'), (-3, 19, 'stone'), (-4, 17, 'stone'), (-5, 15, 'andesite'), (-6, 13, 'stone'),
                   (-7, 11, 'tuff'), (-8, 9, 'tuff'), (-9, 7, 'deepslate'), (-10, 5, 'deepslate'), (-11, 3, 'deepslate'), (-12, 1, 'amethyst_block')):
    _b += _rows(_disk_cols(0, 0, r), dy, dy, blk)
for a in range(0, 360, 17):
    x, z = _polar(20, a)
    _b.append(_S(x, -3, z, 'hanging_roots'))
for a in range(8, 360, 29):
    x, z = _polar(13, a)
    _b.append(_S(x, -7, z, 'amethyst_cluster[facing=down]'))
_b.append(_S(0, -13, 0, 'amethyst_cluster[facing=down]'))
# floor details: moss / coarse dirt patches
_busy = set()
for _ in range(90):
    x, z = _rng.randint(-20, 20), _rng.randint(-20, 20)
    if (x, z) in _MAIN and x * x + z * z > 49:
        _b.append(_S(x, 0, z, _rng.choice(['moss_block', 'moss_block', 'coarse_dirt', 'rooted_dirt'])))
# central plaza + four diagonal stone paths
_plaza = {(x, z) for x in range(-7, 8) for z in range(-7, 8) if 2.5 <= math.hypot(x, z) <= 6.6}
_b += [_S(x, 0, z, 'mossy_stone_bricks' if _rng.random() < 0.3 else 'stone_bricks') for x, z in sorted(_plaza)]
_path = set()
for a in (45, 135, 225, 315):
    r = 6.0
    while r <= 21:
        x, z = _polar(r, a)
        for ox, oz in ((0, 0), (1, 0), (0, 1)):
            if (x + ox, z + oz) in _MAIN:
                _path.add((x + ox, z + oz))
        r += 0.5
_b += [_S(x, 0, z, 'mossy_stone_bricks' if _rng.random() < 0.3 else 'stone_bricks') for x, z in sorted(_path)]
for a in (30, 60, 120, 150, 210, 240, 300, 330):
    x, z = _polar(9, a)
    _b.append(_S(x, 0, z, 'sea_lantern'))
_busy |= _plaza | _path
# spawn pillar (calcite + amethyst) and protected spawn platform on top
_b += [_F(-1, 1, -1, 1, 12, 1, 'calcite')]
_b += [_F(c1, 1, c2, c1, 12, c2, 'amethyst_block') for c1 in (-1, 1) for c2 in (-1, 1)]
_b += [_S(x, 6, z, 'sea_lantern') for x, z in ((0, -1), (0, 1), (-1, 0), (1, 0))]
_b += _rows(_disk_cols(0, 0, 3), 12, 12, 'amethyst_block')
_b += _rows(_disk_cols(0, 0, 5), 13, 13, 'calcite')
_b += [_S(x, 13, z, 'amethyst_block') for x, z in sorted({_polar(5.2, a) for a in range(0, 360, 6)}) if (x, z) in _disk_cols(0, 0, 5)]
_b += [_S(0, 13, 0, 'sea_lantern')] + [_S(x, 13, z, 'smooth_quartz') for x, z in sorted({_polar(2, a) for a in range(0, 360, 10)})]
# terraces (level 2) east and west: stone-brick mesas with grass top, steps up from the plaza side
for ca in (0, 180):
    cols = set()
    for x in range(-19, 20):
        for z in range(-19, 20):
            d = math.hypot(x, z)
            ang = (math.degrees(math.atan2(z, x)) - ca + 540) % 360 - 180
            if 11.5 <= d <= 18.5 and abs(ang) <= 35:
                cols.add((x, z))
    _b += _rows(cols, 1, 3, 'stone_bricks') + _rows(cols, 4, 4, 'grass_block')
    _b += [_S(x, 2, z, 'mossy_stone_bricks') for x, z in sorted(cols) if _rng.random() < 0.25 and math.hypot(x, z) > 17.5]
    _rim = sorted(c for c in cols if any((c[0] + i, c[1] + j) not in cols for i, j in ((1, 0), (-1, 0), (0, 1), (0, -1))))
    _b += [_S(x, 4, z, 'mossy_stone_bricks' if _rng.random() < 0.35 else 'stone_bricks') for x, z in _rim]
    sgn = 1 if ca == 0 else -1
    for h, r in ((1, 9), (2, 10), (3, 11)):
        _b.append(_F(sgn * r, 1, -1, sgn * r, h, 1, 'polished_andesite'))
    lx, lz = _polar(15, ca + 20)
    _b += [_F(lx, 5, lz, lx, 6, lz, 'stone_brick_wall'), _S(lx, 7, lz, 'lantern')]
    bx, bz = _polar(16, ca - 18)
    _b += [_S(bx, 5, bz, 'flowering_azalea_leaves[persistent=true]'), _S(bx + 1, 5, bz, 'azalea_leaves[persistent=true]')]
    _busy |= cols
# crystal platforms (level 3) north and south, reached with the jump pads below them
_PADS = []
for ca in (90, 270):
    px, pz = _polar(14, ca)
    _b += _rows(_disk_cols(px, pz, 3), 8, 8, 'amethyst_block') + _rows(_disk_cols(px, pz, 2), 7, 7, 'calcite') + [_S(px, 6, pz, 'amethyst_block'),
                                                                                                                   _S(px, 5, pz, 'amethyst_cluster[facing=down]'),
                                                                                                                   _S(px, 8, pz, 'sea_lantern')]
    ox, oz = _polar(3, ca)
    _b += [_S(px + oz, 9, pz + ox, 'amethyst_cluster[facing=up]'), _S(px - oz, 9, pz - ox, 'small_amethyst_bud[facing=up]')]
    jx, jz = _polar(9, ca)                        # pad just inside the platform edge (platform spans r=11..17)
    _PADS.append((jx, jz))
    _b += [_F(jx - 1, 0, jz - 1, jx + 1, 0, jz + 1, 'polished_andesite'), _S(jx, 0, jz, 'purple_glazed_terracotta')]
    _busy |= {(jx + i, jz + j) for i in (-1, 0, 1) for j in (-1, 0, 1)}
# satellite islands (level -1) on the diagonals
for a in (45, 135, 225, 315):
    sx, sz = _polar(28, a)
    _b += _rows(_disk_cols(sx, sz, 4), -3, -3, 'grass_block') + _rows(_disk_cols(sx, sz, 4), -4, -4, 'dirt')
    _b += _rows(_disk_cols(sx, sz, 3), -5, -5, 'stone') + _rows(_disk_cols(sx, sz, 2), -6, -6, 'tuff') + [_S(sx, -7, sz, 'deepslate'), _S(sx, -8, sz, 'amethyst_cluster[facing=down]')]
    _b += [_F(sx, -2, sz, sx, -1, sz, 'mossy_stone_brick_wall'), _S(sx, 0, sz, 'lantern')]
    _b += [_S(sx + 2, -2, sz - 1, 'short_grass'), _S(sx - 2, -2, sz + 1, 'allium'), _S(sx - 1, -2, sz - 2, 'short_grass')]
# flowers, grass and a few bushes on the main floor (keep paths, pads, steps and the plaza free)
_busy |= {(x, z) for x in range(-12, 13) for z in (-1, 0, 1)} | {(x, z) for x in (-1, 0, 1) for z in range(-12, 13)}
_FLOWERS = ['short_grass', 'short_grass', 'short_grass', 'poppy', 'allium', 'azure_bluet', 'cornflower', 'oxeye_daisy', 'lily_of_the_valley']
for _ in range(220):
    x, z = _rng.randint(-20, 20), _rng.randint(-20, 20)
    if (x, z) in _MAIN and (x, z) not in _busy and math.hypot(x, z) > 7.5:
        _busy.add((x, z))
        _b.append(_S(x, 1, z, _rng.choice(_FLOWERS)))
for a in (20, 160, 200, 340):
    x, z = _polar(19, a + 45 if a in (20, 200) else a - 45)
    if (x, z) not in _path:
        _b += [_S(x, 1, z, 'flowering_azalea_leaves[persistent=true]'), _S(x, 1, z + 1, 'azalea_leaves[persistent=true]')]
# holograms
_b += [holo('mg_kbffah', f'{KX}.5', KY + 18.6, f'{KZ}.5', _txt('KNOCKBACK-FFA', 'light_purple', bold=True), 2.4),
       holo('mg_kbffah', f'{KX}.5', KY + 17.8, f'{KZ}.5', [_txt('Stoß alle ins Nichts!  ', 'white'), _txt('Kein PvP am Spawn', 'gray')], 1.0)]
_b += [holo('mg_kbffah', f'{KX + jx}.5', KY + 2.2, f'{KZ + jz}.5', _txt('⇧ Sprungfeld', 'light_purple'), 0.8) for jx, jz in _PADS]
fn(f'{_K}/build', _b)

# ------------------------------------------------------------------ spawn points (ring on the platform, facing outwards)
_SP = []
for i, a in enumerate(range(0, 360, 60)):
    x, z = _polar(3, a)
    _SP.append(f'execute if score #kbffa_r mg matches {i} in minecraft:overworld run tp @s {KX + x}.5 {_SPY + 1} {KZ + z}.5 {a - 90} 10')
fn(f'{_K}/tp_spawn', [f'execute store result score #kbffa_r mg run random value 1..{len(_SP) - 1}',      # never the same point twice in a row
                       'scoreboard players operation #kbffa_r mg += #kbffa_last mg', f'scoreboard players set #kbffa_6 mg {len(_SP)}',
                       'scoreboard players operation #kbffa_r mg %= #kbffa_6 mg', 'scoreboard players operation #kbffa_last mg = #kbffa_r mg'] + _SP)
_DROP = []
for i, a in enumerate((45, 135, 225, 315)):
    x, z = _polar(5, a)
    _DROP.append(f'execute if score #kbffa_r mg matches {i} in minecraft:overworld run tp @s {KX + x}.5 {KY + 1} {KZ + z}.5 {a - 90} 0')
fn(f'{_K}/drop', ['execute store result score #kbffa_r mg run random value 0..3'] + _DROP + [
    'scoreboard players set @s mg_kbffa_hold 40',
    'execute at @s run playsound minecraft:entity.breeze.wind_burst master @s ~ ~ ~ 0.8 1'])
fn(f'{_K}/kick_spawn', [f'title @s actionbar {tc(_txt("Zu lange am Spawn – ab in den Kampf!", "red", bold=True))}', f'function {NS}:{_K}/drop'])
fn(f'{_K}/no_return', [f'title @s actionbar {tc(_txt("Spawn-Schutz gibt es nur direkt nach dem Respawn!", "red", bold=True))}', f'function {NS}:{_K}/drop'])

# ------------------------------------------------------------------ kit / respawn
fn(f'{_K}/kit', ['clear @s',
                 f'item replace entity @s hotbar.0 with {STICK}',
                 f'item replace entity @s hotbar.1 with {SAND} 64',
                 f'item replace entity @s hotbar.2 with {PEARL} 1',
                 f'item replace entity @s hotbar.8 with {LEAVE}', *_ARMOR])
fn(f'{_K}/respawn', [
    'tag @s add mg_kbffa_rsp',
    f'{OW} execute as @e[type=minecraft:ender_pearl,{_BOX}] at @s on origin if entity @s[tag=mg_kbffa_rsp] run kill @e[type=minecraft:ender_pearl,distance=..0.5,limit=1,sort=nearest]',
    'tag @s remove mg_kbffa_rsp', 'tag @s remove mg_kbffa_rech', 'tag @s add mg_kbffa_fresh',
    *[f'scoreboard players set @s mg_kbffa_{o} 0' for o in ('s', 'lt', 'lh', 'pc', 'sp', 'dd', 'dt')],
    'scoreboard players set @s mg_deaths 0', 'scoreboard players set @s mg_kbffa_pv 40',
    'effect clear @s', 'effect give @s minecraft:instant_health 1 5 true', 'effect give @s minecraft:saturation infinite 0 true',
    'effect give @s minecraft:resistance 2 4 true', 'effect give @s minecraft:weakness 2 100 true',
    f'function {NS}:{_K}/kit', f'function {NS}:{_K}/tp_spawn',
    'execute at @s run playsound minecraft:entity.enderman.teleport master @s ~ ~ ~ 0.6 1.4',
    'execute at @s run particle minecraft:reverse_portal ~ ~1 ~ 0.3 0.6 0.3 0.05 30'])
fn(f'{_K}/refill', ['clear @s minecraft:sandstone',
                    f'execute unless items entity @s hotbar.1 * run item replace entity @s hotbar.1 with {SAND} 64',
                    f'execute unless items entity @s hotbar.1 minecraft:sandstone run give @s {SAND} 64'])

# ------------------------------------------------------------------ join / enter / leave
fn(f'{_K}/join', [
    'execute unless entity @s[tag=mg_hub] run return 0',
    f'function {NS}:q/leave_all', 'tag @s remove mg_hub', f'tag @s add {_T}', f'tag @s add {_W}',
    *[f'scoreboard players set @s mg_kbffa_{o} 0' for o in ('k', 'd', 'best', 'use', 'pad', 'hold')],
    'execute unless score @s mg_kbffa_cn matches 0.. run scoreboard players set @s mg_kbffa_cn 0',
    'execute unless score @s mg_kbffa_pid matches 1.. run scoreboard players add #kbffa_pid mg 1',      # persistent id (survives rejoin)
    'execute unless score @s mg_kbffa_pid matches 1.. run scoreboard players operation @s mg_kbffa_pid = #kbffa_pid mg',
    'scoreboard players add #kbffa_id mg 1', 'scoreboard players operation @s mg_kbffa_id = #kbffa_id mg',
    f'execute store result score @s mg_kbffa_col run random value 0..{len(_COLORS) - 1}',
    'ride @s dismount', 'clear @s', 'effect clear @s', 'gamemode adventure @s',
    'attribute @s minecraft:fall_damage_multiplier base set 0',
    f'{OW} spawnpoint @s {KX} {_SPY + 1} {KZ}',
    f'execute if score #kbffa mg matches 0 run function {NS}:{_K}/activate',
    f'execute if score #kbffa mg matches 2 run return run function {NS}:{_K}/enter',
    f'{OW} tp @s {KX}.5 {_SPY + 1} {KZ}.5',
    'effect give @s minecraft:blindness 2 0 true', 'effect give @s minecraft:resistance 5 4 true',
])
fn(f'{_K}/activate', [f'{OW} forceload add {_FL}', 'scoreboard players set #kbffa mg 1', 'scoreboard players set #kbffa_lw mg 0'])
fn(f'{_K}/loading', [
    'scoreboard players add #kbffa_lw mg 1',
    f'{OW} tp @a[tag={_W}] {KX}.5 {_SPY + 1} {KZ}.5',
    f'title @a[tag={_W}] actionbar {tc(_txt("Arena wird geladen …", "light_purple"))}',
    f'execute in minecraft:overworld if loaded {_BX1} {KY} {_BZ1} if loaded {_BX2} {KY} {_BZ2} if loaded {_BX1} {KY} {_BZ2} if loaded {_BX2} {KY} {_BZ1} run function {NS}:{_K}/ready',
    f'execute if score #kbffa_lw mg matches 200.. run {OW} forceload add {_FL}'])
fn(f'{_K}/ready', [f'function {NS}:{_K}/build', 'scoreboard players set #kbffa mg 2', 'scoreboard players set #kbffa_t mg 0',
                   f'execute as @a[tag={_W}] at @s run function {NS}:{_K}/enter'])
fn(f'{_K}/enter', [
    f'tag @s remove {_W}', f'function {NS}:{_K}/respawn',
    'title @s times 5 50 10',
    f'title @s title {tc(_txt("KNOCKBACK-FFA", "light_purple", bold=True))}',
    f'title @s subtitle {tc(_txt("Stoß alle ins Nichts!", "white"))}',
    f'tellraw @s {msg(_txt("Knockback-FFA", "light_purple", bold=True), _txt(" – Schubs die anderen mit dem Rückstoß-Stock von der Insel. Wer dich zuletzt (10 s) getroffen hat, bekommt den Kill. Sandstein zerfällt nach ~8 s, die Enderperle kommt 10 s nach dem Wurf zurück. Am Spawn gibt es kein PvP.", "gray"))}',
    f'tellraw @s {tc([_txt("  Serien: ", "gold", bold=True), _txt("3 = Tempo · 5 = Extra-Perle · 10 = Donner-Stock", "white")])}',
    f'tellraw @s {tc([{"text": "  "}, {"text": "[Spiel verlassen]", "color": "red", "click_event": {"action": "run_command", "command": "/trigger mg_aktion set 99"}}])}',
    f'execute store result score #kbffa_n mg if entity @a[tag={_T},tag=!{_W}]',
    f'tellraw @a[tag={_T}] {msg({"selector": "@s", "color": "white"}, _txt(" ist in der Arena! ", "light_purple"), _txt("(", "dark_gray"), {"score": {"name": "#kbffa_n", "objective": "mg"}, "color": "white"}, _txt(" Spieler)", "dark_gray"))}',
    f'tellraw @a[tag=mg_hub] {msg({"selector": "@s", "color": "white"}, _txt(" spielt jetzt ", "gray"), _txt("Knockback-FFA", "light_purple", bold=True), _txt(" – ", "gray"), {"text": "[Mitspielen]", "color": "green", "click_event": {"action": "run_command", "command": f"/trigger mg_aktion set {_TRIG}"}})}',
    'execute at @s run playsound minecraft:block.amethyst_block.chime master @s ~ ~ ~ 1 1'])
fn(f'{_K}/bye', [f'tellraw @s {msg(_txt("Knockback-FFA verlassen – ", "gray"), {"score": {"name": "@s", "objective": "mg_kbffa_k"}, "color": "gold", "bold": True}, _txt(" Kills, beste Serie: ", "gray"), {"score": {"name": "@s", "objective": "mg_kbffa_best"}, "color": "red", "bold": True})}'])
fn(f'{_K}/deactivate', [f'{OW} kill @e[type=minecraft:item,{_BOX}]', f'{OW} kill @e[type=minecraft:ender_pearl,{_BOX}]',
                        f'{OW} forceload remove {_FL}', 'scoreboard players set #kbffa mg 0'])
fn(f'{_K}/use', ['scoreboard players set @s mg_kbffa_use 0',
                 f'execute if items entity @s weapon.mainhand *[minecraft:custom_data~{{mg_kbffa_leave:1b}}] run function {NS}:hub/quit'])

# ------------------------------------------------------------------ hits, falls, kills, streaks
fn(f'{_K}/hurt', ['scoreboard players set @s mg_kbffa_dt 0', 'scoreboard players set #kbffa_lh mg 0',
                  'scoreboard players operation #kbffa_lh mg = @p[tag=mg_kbffa_atk,distance=0.01..8] mg_kbffa_id',
                  'execute if score #kbffa_lh mg matches 1.. run scoreboard players operation @s mg_kbffa_lh = #kbffa_lh mg',
                  'execute if score #kbffa_lh mg matches 1.. run scoreboard players set @s mg_kbffa_lt 200'])
_VIC = '@a[tag=mg_kbffa_vic,limit=1]'
fn(f'{_K}/fall', [
    'scoreboard players add @s mg_kbffa_d 1',
    'scoreboard players set #kbffa_lh mg 0',
    'execute if score @s mg_kbffa_lt matches 1.. run scoreboard players operation #kbffa_lh mg = @s mg_kbffa_lh',
    'scoreboard players operation #kbffa_vs mg = @s mg_kbffa_s',
    'scoreboard players set #kbffa_kf mg 0', 'tag @s add mg_kbffa_vic', 'scoreboard players operation #kbffa_vid mg = @s mg_kbffa_pid',
    f'execute if score #kbffa_lh mg matches 1.. as @a[tag={_T},tag=!mg_kbffa_vic,tag=!{_W}] if score @s mg_kbffa_id = #kbffa_lh mg at @s run function {NS}:{_K}/kill',
    f'execute if score #kbffa_kf mg matches 0 run tellraw @a[tag={_T}] {msg({"selector": "@s", "color": "white"}, _txt(" ist ins Nichts gestürzt.", "gray"))}',
    f'execute if score #kbffa_kf mg matches 0 if score #kbffa_vs mg matches 3.. run tellraw @a[tag={_T}] {msg(_txt("Die ", "gray"), {"score": {"name": "#kbffa_vs", "objective": "mg"}, "color": "red", "bold": True}, _txt("er-Serie von ", "gray"), {"selector": "@s", "color": "white"}, _txt(" ist vorbei.", "gray"))}',
    'execute if score #kbffa_kf mg matches 0 run title @s times 0 25 8',
    f'execute if score #kbffa_kf mg matches 0 run title @s title {tc(_txt("Abgestürzt!", "red", bold=True))}',
    f'execute if score #kbffa_kf mg matches 0 run title @s subtitle {tc(_txt("Pass auf die Kante auf", "gray"))}',
    'execute at @s run playsound minecraft:entity.player.hurt_on_fire master @s ~ ~ ~ 0.5 0.6',
    'tag @s remove mg_kbffa_vic',
    f'function {NS}:{_K}/respawn'])
fn(f'{_K}/kill', [
    'scoreboard players set #kbffa_kf mg 1', 'tag @s add mg_kbffa_klr',
    # anti coin farming: no coins for killing the same player twice in a row, max ~30 coins, refilling by 1 per minute
    'scoreboard players set #kbffa_pay mg 1',
    'execute if score @s mg_kbffa_lv = #kbffa_vid mg run scoreboard players set #kbffa_pay mg 0',
    f'execute if score @s mg_kbffa_cn matches {_COIN_CAP}.. run scoreboard players set #kbffa_pay mg 0',
    'scoreboard players operation @s mg_kbffa_lv = #kbffa_vid mg',
    'scoreboard players add @s mg_kbffa_k 1', 'scoreboard players add @s mg_kbffa_s 1', f'function {NS}:{_K}/coin {{n:1}}',
    f'tellraw @a[tag={_T}] {msg(_txt("☠ ", "red"), {"selector": _VIC, "color": "white"}, _txt(" wurde von ", "gray"), {"selector": "@s", "color": "gold"}, _txt(" ins Nichts gestoßen ", "gray"), _txt("(Serie ", "dark_gray"), {"score": {"name": "@s", "objective": "mg_kbffa_s"}, "color": "red"}, _txt(")", "dark_gray"))}',
    'title @s times 0 25 8', f'title @s title {tc(_txt("", "white"))}',
    f'title @s subtitle {tc([_txt("☠ ", "red"), {"selector": _VIC, "color": "white"}, _txt("  +1 Kill", "gold", bold=True)])}',
    'playsound minecraft:entity.experience_orb.pickup master @s ~ ~ ~ 1 1.2',
    'playsound minecraft:entity.arrow.hit_player master @s ~ ~ ~ 0.8 1',
    f'execute as {_VIC} run title @s times 0 25 8',
    f'execute as {_VIC} run title @s title {tc(_txt("Runtergestoßen!", "red", bold=True))}',
    f'execute as {_VIC} run title @s subtitle {tc([_txt("von ", "gray"), {"selector": "@a[tag=mg_kbffa_klr,limit=1]", "color": "gold"}])}',
    'effect give @s minecraft:instant_health 1 1 true',
    f'function {NS}:{_K}/refill',
    f'execute if score #kbffa_vs mg matches 5.. run tellraw @a[tag={_T}] {msg({"selector": "@s", "color": "gold", "bold": True}, _txt(" beendet die ", "yellow"), {"score": {"name": "#kbffa_vs", "objective": "mg"}, "color": "red", "bold": True}, _txt("er-Serie von ", "yellow"), {"selector": _VIC, "color": "white"}, _txt("!", "yellow"))}',
    f'execute if score #kbffa_vs mg matches 5.. run function {NS}:{_K}/coin {{n:3}}',
    f'function {NS}:{_K}/streak',
    'execute if score @s mg_kbffa_s > @s mg_kbffa_best run scoreboard players operation @s mg_kbffa_best = @s mg_kbffa_s',
    f'execute if score @s mg_kbffa_s matches 5.. if score @s mg_kbffa_s > #kbffa_rec mg unless entity @s[tag=mg_kbffa_rech] run tellraw @a[tag={_T}] {msg(_txt("★ Neuer Arena-Rekord: ", "light_purple", bold=True), {"score": {"name": "@s", "objective": "mg_kbffa_s"}, "color": "white", "bold": True}, _txt(" Kills in Folge von ", "light_purple"), {"selector": "@s", "color": "white"})}',
    'execute if score @s mg_kbffa_s matches 5.. if score @s mg_kbffa_s > #kbffa_rec mg run tag @s add mg_kbffa_rech',
    'execute if score @s mg_kbffa_s > #kbffa_rec mg run scoreboard players operation #kbffa_rec mg = @s mg_kbffa_s',
    'tag @s remove mg_kbffa_klr'])
fn(f'{_K}/streak', [
    'execute if score @s mg_kbffa_s matches 3 run effect give @s minecraft:speed 20 0 true',
    f'execute if score @s mg_kbffa_s matches 3 run title @s actionbar {tc(_txt("3er-Serie! Tempo für 20 Sekunden", "aqua", bold=True))}',
    'execute if score @s mg_kbffa_s matches 3 run scoreboard players set @s mg_kbffa_hold 40',
    f'execute if score @s mg_kbffa_s matches 5 run give @s {PEARL} 1',
    f'execute if score @s mg_kbffa_s matches 5 run function {NS}:{_K}/coin {{n:2}}',
    f'execute if score @s mg_kbffa_s matches 5 run tellraw @a[tag={_T}] {msg({"selector": "@s", "color": "gold", "bold": True}, _txt(" hat eine ", "yellow"), _txt("5er-Serie", "red", bold=True), _txt("! Extra-Enderperle.", "yellow"))}',
    'execute if score @s mg_kbffa_s matches 5 run playsound minecraft:entity.player.levelup master @s ~ ~ ~ 1 1.2',
    f'execute if score @s mg_kbffa_s matches 10 run function {NS}:{_K}/st10',
    'scoreboard players operation #kbffa_m5 mg = @s mg_kbffa_s', 'scoreboard players operation #kbffa_m5 mg %= #5 mg',
    f'execute if score @s mg_kbffa_s matches 15.. if score #kbffa_m5 mg matches 0 run function {NS}:{_K}/st15'])
fn(f'{_K}/st10', [
    'clear @s minecraft:stick[minecraft:custom_data~{mg_kbffa_stick:1b}]',
    f'execute unless items entity @s hotbar.0 * run item replace entity @s hotbar.0 with {STICK2}',
    f'execute unless items entity @s container.* minecraft:stick run give @s {STICK2}',
    f'function {NS}:{_K}/coin {{n:5}}',
    f'tellraw @a[tag={_T}] {msg({"selector": "@s", "color": "gold", "bold": True}, _txt(" ist nicht zu stoppen – ", "yellow"), _txt("10er-Serie", "red", bold=True), _txt("! Donner-Stock freigeschaltet.", "yellow"))}',
    f'title @s title {tc(_txt("10er-SERIE!", "gold", bold=True))}',
    f'title @s subtitle {tc(_txt("Donner-Stock: Rückstoß III", "yellow"))}',
    f'execute as @a[tag={_T}] at @s run playsound minecraft:entity.lightning_bolt.thunder master @s ~ ~ ~ 0.6 1.3',
    'particle minecraft:totem_of_undying ~ ~1 ~ 0.5 1 0.5 0.4 60'])
fn(f'{_K}/st15', [
    f'give @s {PEARL} 1', f'function {NS}:{_K}/coin {{n:2}}',
    f'tellraw @a[tag={_T}] {msg({"selector": "@s", "color": "gold", "bold": True}, _txt(" ist auf einer ", "yellow"), {"score": {"name": "@s", "objective": "mg_kbffa_s"}, "color": "red", "bold": True}, _txt("er-Serie! Stoppt ihn!", "yellow"))}',
    'playsound minecraft:ui.toast.challenge_complete master @s ~ ~ ~ 0.8 1.2'])
fn(f'{_K}/coin', ['execute if score #kbffa_pay mg matches 0 run return 0',
                  '$scoreboard players add @s mg_coins $(n)', '$scoreboard players add @s mg_kbffa_cn $(n)'])
fn(f'{_K}/died', ['scoreboard players set @s mg_deaths 0', f'function {NS}:{_K}/fall'])

# ------------------------------------------------------------------ per player tick
fn(f'{_K}/zone', [f'execute unless entity @s[tag=mg_kbffa_fresh] run return run function {NS}:{_K}/no_return',   # no pearling back to safety
                  f'execute unless entity @s[tag={_SAFE}] run attribute @s minecraft:knockback_resistance modifier add {NS}:kbffa_safe 1 add_value',
                  'effect give @s minecraft:resistance 1 4 true', 'effect give @s minecraft:weakness 1 100 true',
                  f'tag @s add {_SAFE}', 'scoreboard players add @s mg_kbffa_sp 1',
                  f'execute if score @s mg_kbffa_sp matches 300 run title @s actionbar {tc(_txt("Noch 5 Sekunden am Spawn – spring runter!", "yellow", bold=True))}',
                  'execute if score @s mg_kbffa_sp matches 300 run scoreboard players set @s mg_kbffa_hold 40',
                  f'execute if score @s mg_kbffa_sp matches 400.. run function {NS}:{_K}/kick_spawn'])
fn(f'{_K}/unsafe', [f'tag @s remove {_SAFE}', 'tag @s remove mg_kbffa_fresh', 'effect clear @s minecraft:weakness',
                    f'attribute @s minecraft:knockback_resistance modifier remove {NS}:kbffa_safe',
                    'execute unless score @s mg_kbffa_pv matches 1.. run effect clear @s minecraft:resistance',
                    'playsound minecraft:item.armor.equip_leather master @s ~ ~ ~ 0.7 0.8'])
fn(f'{_K}/pad', ['scoreboard players set @s mg_kbffa_pad 50', 'effect give @s minecraft:levitation 2 5 true', 'effect give @s minecraft:slow_falling 7 0 true',
                 'playsound minecraft:entity.breeze.wind_burst master @a[distance=..16] ~ ~ ~ 0.8 1.3', 'particle minecraft:dragon_breath ~ ~0.2 ~ 0.4 0.1 0.4 0.02 20'])
fn(f'{_K}/pearl', ['scoreboard players add @s mg_kbffa_pc 1',
                   f'execute if score @s mg_kbffa_pc matches {_PEARL_CD}.. run function {NS}:{_K}/pearl_give'])
fn(f'{_K}/pearl_give', ['scoreboard players set @s mg_kbffa_pc 0', f'give @s {PEARL} 1',
                        'playsound minecraft:entity.enderman.teleport master @s ~ ~ ~ 0.4 1.8'])
_KS = [_txt('Kills ', 'gray'), {'score': {'name': '@s', 'objective': 'mg_kbffa_k'}, 'color': 'gold', 'bold': True},
       _txt('  ·  Serie ', 'gray'), {'score': {'name': '@s', 'objective': 'mg_kbffa_s'}, 'color': 'red', 'bold': True}]
fn(f'{_K}/hud', [
    'execute if score @s mg_kbffa_hold matches 1.. run return 0',
    f'execute if entity @s[tag={_SAFE}] run return run title @s actionbar {tc([_txt("⛨ Spawn-Schutz", "aqua", bold=True), _txt("  ·  ", "gray")] + _KS)}',
    'scoreboard players set @s mg_kbffa_ps 219', 'scoreboard players operation @s mg_kbffa_ps -= @s mg_kbffa_pc', 'scoreboard players operation @s mg_kbffa_ps /= #20 mg',
    f'execute if score @s mg_kbffa_pc matches 1.. run return run title @s actionbar {tc(_KS + [_txt("  ·  Perle ", "gray"), {"score": {"name": "@s", "objective": "mg_kbffa_ps"}, "color": "yellow"}, _txt(" s", "yellow")])}',
    f'title @s actionbar {tc(_KS + [_txt("  ·  Perle ", "gray"), _txt("bereit", "green")])}'])
fn(f'{_K}/ptick', [
    f'execute if entity @s[y=-64,dy={_FALL_Y + 64 - 1}] run return run function {NS}:{_K}/fall',
    f'execute unless entity @s[x={KX - _BOUND},dx={2 * _BOUND},z={KZ - _BOUND},dz={2 * _BOUND},y=-64,dy=500] run return run function {NS}:{_K}/fall',
    'execute if score @s mg_kbffa_lt matches 1.. run scoreboard players remove @s mg_kbffa_lt 1',
    'execute if score @s mg_kbffa_pv matches 1.. run scoreboard players remove @s mg_kbffa_pv 1',
    'execute if score @s mg_kbffa_pad matches 1.. run scoreboard players remove @s mg_kbffa_pad 1',
    f'execute if entity @s[{_ZONE}] run function {NS}:{_K}/zone',
    f'execute if entity @s[tag={_SAFE}] unless entity @s[{_ZONE}] run function {NS}:{_K}/unsafe',
    f'execute if block ~ ~-1 ~ minecraft:purple_glazed_terracotta unless score @s mg_kbffa_pad matches 1.. run function {NS}:{_K}/pad',
    'execute store result score @s mg_kbffa_n run clear @s minecraft:ender_pearl 0',      # counts inventory, cursor AND 2x2 crafting grid
    'execute if score @s mg_kbffa_n matches 1.. run scoreboard players set @s mg_kbffa_pc 0',
    f'execute if score @s mg_kbffa_n matches 0 run function {NS}:{_K}/pearl',
    'execute if score @s mg_kbffa_hold matches 1.. run scoreboard players remove @s mg_kbffa_hold 1',
    f'execute if score #kbffa_m10 mg matches 0 run function {NS}:{_K}/hud'])
# restock (every 45 ticks): lost stick / leave item, slow sandstone trickle
_STK = '*[minecraft:custom_data~{mg_kbffa_stick:1b}]'
_LVI = '*[minecraft:custom_data~{mg_kbffa_leave:1b}]'
fn(f'{_K}/restock', [
    f'execute store result score @s mg_kbffa_n run clear @s {_STK.replace("*", "minecraft:stick", 1)} 0',
    f'execute if score @s mg_kbffa_n matches 0 run give @s {STICK}',
    f'execute store result score @s mg_kbffa_n run clear @s {_LVI.replace("*", "minecraft:carrot_on_a_stick", 1)} 0',
    f'execute if score @s mg_kbffa_n matches 0 run give @s {LEAVE}',
    'execute store result score @s mg_kbffa_n run clear @s minecraft:sandstone 0',
    f'execute if score @s mg_kbffa_n matches ..31 run give @s {SAND} 4'])

# ------------------------------------------------------------------ block ageing (8 x-slabs of 10, one slab every 5 ticks)
for i in range(8):
    x1 = _BX1 + 10 * i
    x2 = min(_BX2, x1 + 9)
    box = f'{x1} {_BY1} {_BZ1} {x2} {_BY2} {_BZ2}'
    seq = [f'{OW} fill {box} minecraft:air replace minecraft:{_AGE[-1]}']
    for j in range(len(_AGE) - 1, 0, -1):
        seq.append(f'{OW} fill {box} minecraft:{_AGE[j]} replace minecraft:{_AGE[j - 1]}')
    fn(f'{_K}/decay{i}', seq)
fn(f'{_K}/band', [f'{OW} fill {KX - 9} {KY + 9} {KZ - 9} {KX + 9} {KY + 20} {KZ + 9} minecraft:air replace minecraft:sandstone',
                  f'{OW} fill {KX - 9} {KY + 9} {KZ - 9} {KX + 9} {KY + 20} {KZ + 9} minecraft:air replace #minecraft:terracotta'])
fn(f'{_K}/slow', [f'{OW} kill @e[type=minecraft:item,{_BOX}]',
                  f'execute as @a[tag={_T},tag=!{_W}] run function {NS}:{_K}/restock',
                  f'{OW} particle minecraft:end_rod {KX}.5 {_SPY + 1.2} {KZ}.5 3.5 0.1 3.5 0 8',
                  *[f'{OW} particle minecraft:portal {KX + jx}.5 {KY + 1.3} {KZ + jz}.5 0.4 0.3 0.4 0.3 25' for jx, jz in _PADS]])

# ------------------------------------------------------------------ main tick (state: 0 idle, 1 loading, 2 running)
fn(f'{_K}/tick', [
    f'execute unless entity @a[tag={_T}] run return run function {NS}:{_K}/deactivate',
    f'execute as @a[tag={_T},scores={{mg_kbffa_use=1..}}] run function {NS}:{_K}/use',
    f'execute if score #kbffa mg matches 1 run return run function {NS}:{_K}/loading',
    'scoreboard players add #kbffa_t mg 1',
    'scoreboard players operation #kbffa_m mg = #kbffa_t mg', 'scoreboard players operation #kbffa_m mg %= #kbffa_45 mg',
    'scoreboard players operation #kbffa_m10 mg = #kbffa_t mg', 'scoreboard players operation #kbffa_m10 mg %= #10 mg',
    f'tag @a[tag={_T},scores={{mg_kbffa_dd=1..}}] add mg_kbffa_atk',
    f'execute as @a[tag={_T},scores={{mg_kbffa_dt=1..}}] at @s run function {NS}:{_K}/hurt',
    'scoreboard players set @a[tag=mg_kbffa_atk] mg_kbffa_dd 0', 'tag @a[tag=mg_kbffa_atk] remove mg_kbffa_atk',
    f'execute as @e[type=minecraft:player,tag={_T},tag=!{_W},scores={{mg_deaths=1..}}] at @s run function {NS}:{_K}/died',
    f'execute as @a[tag={_T},tag=!{_W}] at @s run function {NS}:{_K}/ptick',
    *[f'execute if score #kbffa_m mg matches {5 * i} run function {NS}:{_K}/decay{i}' for i in range(8)],
    'scoreboard players operation #kbffa_m2 mg = #kbffa_t mg',
    'scoreboard players operation #kbffa_m2 mg %= #2 mg',
    f'execute if score #kbffa_m2 mg matches 0 run function {NS}:{_K}/band',
    f'execute if score #kbffa_m mg matches 22 run function {NS}:{_K}/slow'])

# ------------------------------------------------------------------ registration / wiring
register_game(_K, 'Knockback-FFA', 'light_purple', 'butcher', _TRIG, f'function {NS}:{_K}/join',
              'Jederzeit rein · Schubs sie runter', 'Endlos, jederzeit einsteigen')
INFO.append(('Knockback-FFA', 'light_purple', 'Jederzeit einsteigen über NPC oder Kompass. Mit dem Rückstoß-Stock schubst du die anderen von der '
             'Insel – wer dich zuletzt (innerhalb von 10 s) getroffen hat, bekommt den Kill. Sandstein zerfällt nach ~8 s, die Enderperle kommt nach '
             '10 s zurück. Serien: 3 = Tempo, 5 = Extra-Perle, 10 = Donner-Stock. Kein PvP am Spawn. Raus mit dem Barriere-Item oder /trigger mg_aktion set 99.'))
ENTER_LINES.extend([f'execute if entity @s[tag={_T}] run function {NS}:{_K}/bye',
                    *[f'tag @s remove {t}' for t in (_T, _W, _SAFE, 'mg_kbffa_vic', 'mg_kbffa_klr', 'mg_kbffa_rsp', 'mg_kbffa_atk', 'mg_kbffa_rech', 'mg_kbffa_fresh')],
                    'attribute @s minecraft:fall_damage_multiplier base reset',
                    f'attribute @s minecraft:knockback_resistance modifier remove {NS}:kbffa_safe'])
EXTRA_TICK.append(f'execute if score #kbffa mg matches 1.. run function {NS}:{_K}/tick')
# coin cap refills by 1 per minute (not per visit, so leaving and rejoining does not reset it)
EXTRA_TICK.extend(['scoreboard players add #kbffa_cnt mg 1', 'execute if score #kbffa_cnt mg matches 1200.. run scoreboard players remove @a[scores={mg_kbffa_cn=1..}] mg_kbffa_cn 1',
                   'execute if score #kbffa_cnt mg matches 1200.. run scoreboard players set #kbffa_cnt mg 0'])
WATCHDOG.append(f'execute if score #kbffa mg matches 0 as @a[tag={_T}] run function {NS}:hub/enter')
EXTRA_LOAD.extend([
    *[f'scoreboard objectives add mg_kbffa_{o} dummy' for o in ('k', 's', 'd', 'best', 'id', 'lh', 'lt', 'pc', 'ps', 'sp', 'pv', 'pad', 'col', 'n', 'hold', 'pid', 'lv', 'cn')],
    'scoreboard objectives add mg_kbffa_dd minecraft.custom:minecraft.damage_dealt',
    'scoreboard objectives add mg_kbffa_dt minecraft.custom:minecraft.damage_taken',
    'scoreboard objectives add mg_kbffa_use minecraft.used:minecraft.carrot_on_a_stick',
    'scoreboard players set #kbffa_45 mg 45', 'scoreboard players set #10 mg 10',
    'execute unless score #kbffa mg matches 0.. run scoreboard players set #kbffa mg 0',
    'execute unless score #kbffa_rec mg matches 0.. run scoreboard players set #kbffa_rec mg 0',
    f'execute unless entity @a[tag={_T}] run scoreboard players set #kbffa mg 0',
    f'execute if score #kbffa mg matches 1.. run {OW} forceload add {_FL}'])
