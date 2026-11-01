# Murder Mystery: one secret murderer (one-hit sword after 10 s), one detective (bow, an arrow every 5 s), the rest innocent.
# Map: "Villa Nachtschatten" - a Tudor-style mansion with nine rooms, doors and a garden with fountain, gazebo and hedges.
# Innocents win when the murderer dies, leaves, or after 4 minutes; the murderer wins when everyone else is dead.
MX, MY, MZ = 74000, Y, 0
_K = 'murder'
_T, _AL = 'mg_murder', 'mg_al_murder'
_SPECT = (MX, MY + 20, MZ + 23)       # above the fountain: whoever respawns in adventure mode lands in water, not in the void
_LEN = 4800                       # round length in ticks (4 min)
_AREA = f'x={MX - 30},y={MY - 5},z={MZ - 30},dx=60,dy=30,dz=60'


def _F(x1, y1, z1, x2, y2, z2, b):
    return f'{OW} fill {MX + x1} {MY + y1} {MZ + z1} {MX + x2} {MY + y2} {MZ + z2} minecraft:{b}'


def _S(x, y, z, b):
    return f'{OW} setblock {MX + x} {MY + y} {MZ + z} minecraft:{b}'


def _txt(text, color, **kw):
    return dict(text=text, color=color, italic=False, **kw)


_HIDE = 'minecraft:tooltip_display={hidden_components:["minecraft:enchantments","minecraft:unbreakable","minecraft:attribute_modifiers"]}'
SWORD = ('minecraft:iron_sword[minecraft:custom_name=' + tc(_txt('Mordwaffe', 'dark_red', bold=True)) +
         ',minecraft:lore=[' + tc(_txt('Ein Treffer genügt.', 'gray')) + ']'
         ',minecraft:attribute_modifiers=[{type:"minecraft:attack_damage",amount:1000,id:"mg:murder_sword",operation:"add_value",slot:"mainhand"}]'
         ',minecraft:unbreakable={},minecraft:custom_data={mg_murder:"sword"},' + _HIDE + ']')
_BOWC = {'dbow': ('Detektiv-Bogen', 'aqua', 'Ein Treffer genügt. Neuer Pfeil nach 5 s.'),
         'ibow': ('Bogen', 'green', 'Ein Treffer genügt. Triff bloß keinen Unschuldigen!')}


def _bow(kind):
    n, c, l = _BOWC[kind]
    return ('minecraft:bow[minecraft:custom_name=' + tc(_txt(n, c, bold=True)) + ',minecraft:lore=[' + tc(_txt(l, 'gray')) + ']'
            ',minecraft:enchantments={"minecraft:power":255},minecraft:unbreakable={},minecraft:custom_data={mg_murder:"' + kind + '"},' + _HIDE + ']')


def _has(slotkind):
    """execute-condition fragments: player holds an item with this custom_data anywhere (inventory, offhand, cursor)."""
    p = f'*[minecraft:custom_data~{{mg_murder:"{slotkind}"}}]'
    return [f'if items entity @s container.* {p}', f'if items entity @s weapon.offhand {p}', f'if items entity @s player.cursor {p}']


# ------------------------------------------------------------------ map
_b = [f'kill @e[type=minecraft:text_display,tag=mg_murderh]', f'kill @e[type=minecraft:marker,tag=mg_murder_sp]',
      f'{OW} kill @e[type=minecraft:item,{_AREA}]', f'{OW} kill @e[type=minecraft:arrow,{_AREA}]']
_b += clear_box(MX - 30, MY - 1, MZ - 30, MX + 30, MY + 17, MZ + 30, 4)
# ground, hedge border (with invisible cap)
_b += [_F(-29, -1, -29, 29, -1, 29, 'dirt'), _F(-29, 0, -29, 29, 0, 29, 'grass_block')]
_HEDGE = 'oak_leaves[persistent=true]'
for a, b2 in ((-29, -29), (29, 29)):
    _b += [_F(a, 1, -29, b2, 3, 29, _HEDGE), _F(-29, 1, a, 29, 3, b2, _HEDGE),
           _F(a, 4, -29, b2, 6, 29, 'barrier'), _F(-29, 4, a, 29, 6, b2, 'barrier')]
# garden paths
_b += [_F(-18, 0, -18, 18, 0, 18, 'dirt_path'), _F(-1, 0, 17, 1, 0, 28, 'dirt_path'), _F(0, 0, -28, 0, 0, -17, 'dirt_path'),
       _F(-28, 0, 0, -17, 0, 0, 'dirt_path'), _F(17, 0, 0, 28, 0, 0, 'dirt_path')]
# flowers (fixed seed, keep paths and item spots free)
_rng = random.Random(62)
_FLOWERS = ['poppy', 'dandelion', 'cornflower', 'allium', 'azure_bluet', 'oxeye_daisy', 'short_grass', 'short_grass', 'short_grass', 'lily_of_the_valley']
_GOLD = [(-13, -13), (-2, -8), (13, -12), (-13, 0), (3, -3), (13, 3), (-13, 13), (3, 13), (9, 13),
         (-21, -21), (21, -21), (-21, 21), (21, 21), (0, -23), (-23, 6), (23, -6), (8, 23)]
_SPAWNS = [(-12, -9), (0, -14), (12, -8), (-10, 2), (0, 3), (10, -2), (-10, 12), (0, 12), (11, 12),
           (-22, -12), (22, 12), (-12, 22), (12, -22), (-22, 18), (22, -18), (6, 26)]
_busy = set(_GOLD) | set(_SPAWNS)
for _ in range(400):
    fx, fz = _rng.randint(-27, 27), _rng.randint(-27, 27)
    if max(abs(fx), abs(fz)) <= 18 or abs(fx) <= 2 or abs(fz) <= 1 or (fx, fz) in _busy:
        continue
    if abs(fx) <= 4 and 19 <= fz <= 27 or abs(fx) <= 3 and -26 <= fz <= -20 or abs(abs(fx) - 23) <= 1 and abs(abs(fz) - 23) <= 1:
        continue
    _b.append(_S(fx, 1, fz, _rng.choice(_FLOWERS)))

# fountain (south)
_b += [f'{OW} {c}' for c in disk(MX, MY, MZ + 23, 3, 'stone_bricks')]
_b += [f'{OW} {c}' for c in ring(MX, MY + 1, MZ + 23, 3, 'stone_brick_wall')]
_b += [f'{OW} {c}' for c in disk(MX, MY, MZ + 23, 2, 'water')]
_b += [_F(0, 0, 23, 0, 2, 23, 'chiseled_stone_bricks'), _S(0, 3, 23, 'water')]
# gazebo (north)
for gx in (-2, 2):
    for gz in (-25, -21):
        _b.append(_F(gx, 1, gz, gx, 3, gz, 'dark_oak_fence'))
_b += [_F(-3, 4, -26, 3, 4, -20, 'dark_oak_slab[type=bottom]'), _F(-2, 4, -25, 2, 4, -21, 'dark_oak_planks'),
       _S(0, 5, -23, 'dark_oak_slab[type=bottom]'), _S(0, 3, -23, 'lantern[hanging=true]'),
       _F(-1, 1, -25, 1, 1, -25, 'spruce_stairs[facing=north]'), _F(-2, 0, -25, 2, 0, -21, 'spruce_planks')]
# trees in the four corners
for tx, tz in ((-23, -23), (23, -23), (-23, 23), (23, 23)):
    _b += [_F(tx - 2, 4, tz - 2, tx + 2, 5, tz + 2, _HEDGE), _F(tx - 1, 6, tz - 1, tx + 1, 6, tz + 1, _HEDGE),
           _S(tx, 7, tz, _HEDGE), _F(tx, 1, tz, tx, 6, tz, 'dark_oak_log')]
# lamp posts
for lx, lz in ((-8, 20), (8, 20), (-20, -8), (20, 8), (-20, 8), (20, -8), (-8, -20), (8, -20)):
    _b += [_F(lx, 1, lz, lx, 2, lz, 'dark_oak_fence'), _S(lx, 3, lz, 'lantern')]
# benches in the garden
_b += [_F(-24, 1, -4, -24, 1, -2, 'spruce_stairs[facing=west]'), _F(24, 1, 2, 24, 1, 4, 'spruce_stairs[facing=east]'),
       _F(-14, 1, 24, -12, 1, 24, 'spruce_stairs[facing=south]'), _F(12, 1, -24, 14, 1, -24, 'spruce_stairs[facing=north]')]
# bushes along the facade
_b += [_F(-12, 1, 17, -4, 1, 17, _HEDGE), _F(4, 1, 17, 12, 1, 17, _HEDGE),
       _F(-17, 1, -12, -17, 1, -4, _HEDGE), _F(17, 1, 4, 17, 1, 12, _HEDGE)]
# ---- the mansion: 33x33, nine rooms (3x3 grid), walls y1..5, ceiling y6, hip roof
_b += [_F(-16, 0, -16, 16, 0, 16, 'stone_bricks'), _F(-15, 0, -15, 15, 0, 15, 'dark_oak_planks')]
# room floors
_b += [_F(-15, 0, -15, -7, 0, -7, 'spruce_planks'),                    # library
       _F(-5, 0, 7, 5, 0, 15, 'polished_andesite'), _F(-1, 0, 7, 1, 0, 16, 'stone_bricks'),   # entrance
       _F(7, 0, 7, 15, 0, 15, 'moss_block'), _F(11, 0, 7, 11, 0, 15, 'mossy_cobblestone')]    # greenhouse
for kx in range(7, 16):                                                 # kitchen checkerboard
    for kz in range(-15, -6):
        if (kx + kz) % 2:
            _b.append(_S(kx, 0, kz, 'polished_blackstone'))
_b.append(f'{OW} fill {MX + 7} {MY} {MZ - 15} {MX + 15} {MY} {MZ - 7} minecraft:smooth_quartz replace minecraft:dark_oak_planks')
# outer walls: stone base, plaster infill, dark oak frame
_PIL = (-16, -11, -6, -2, 2, 6, 11, 16)
for s in (-16, 16):
    _b += [_F(-16, 1, s, 16, 5, s, 'white_terracotta'), _F(s, 1, -16, s, 5, 16, 'white_terracotta'),
           _F(-16, 1, s, 16, 1, s, 'stone_bricks'), _F(s, 1, -16, s, 1, 16, 'stone_bricks'),
           _F(-16, 5, s, 16, 5, s, 'stripped_dark_oak_wood'), _F(s, 5, -16, s, 5, 16, 'stripped_dark_oak_wood')]
    for p in _PIL:
        _b += [_F(p, 1, s, p, 4, s, 'dark_oak_log'), _F(s, 1, p, s, 4, p, 'dark_oak_log')]
    for w1, w2 in ((-14, -13), (-9, -8), (-4, -4), (4, 4), (8, 9), (13, 14)):
        _b += [_F(w1, 2, s, w2, 3, s, 'glass_pane[east=true,west=true]'), _F(s, 2, w1, s, 3, w2, 'glass_pane[north=true,south=true]')]
# interior walls
for s in (-6, 6):
    _b += [_F(s, 1, -15, s, 5, 15, 'spruce_planks'), _F(-15, 1, s, 15, 5, s, 'spruce_planks'),
           _F(s, 1, s, s, 5, s, 'stripped_spruce_log')]
# greenhouse glass walls
_b += [_F(16, 2, 7, 16, 4, 15, 'glass'), _F(7, 2, 16, 15, 4, 16, 'glass')]
# doorways: wide arches into the great hall, wooden doors elsewhere
_b += [_F(-6, 1, -1, -6, 3, 1, 'air'), _F(6, 1, -1, 6, 3, 1, 'air'), _F(-1, 1, -6, 1, 3, -6, 'air'), _F(-1, 1, 6, 1, 3, 6, 'air'),
       _F(-1, 1, 16, 1, 3, 16, 'air')]


def _door(x, z, facing):
    return [_S(x, 2, z, f'dark_oak_door[facing={facing},half=upper,hinge=left,open=false]'),
            _S(x, 1, z, f'dark_oak_door[facing={facing},half=lower,hinge=left,open=false]')]


for dx_, dz_, f in ((-6, -11, 'east'), (6, -11, 'west'), (-6, 9, 'east'), (6, 9, 'west'),
                    (-9, -6, 'south'), (-11, 6, 'north'), (11, -6, 'south'), (11, 6, 'north'),
                    (0, -16, 'south'), (-16, 0, 'east'), (16, 0, 'west')):
    _b += _door(dx_, dz_, f)
# ceiling + lights
_b.append(_F(-16, 6, -16, 16, 6, 16, 'dark_oak_planks'))
for rx in (-11, 0, 11):
    for rz in (-11, 0, 11):
        for ox, oz in ((-2, -2), (2, -2), (-2, 2), (2, 2)):
            _b.append(_S(rx + ox, 6, rz + oz, 'shroomlight'))
# hip roof with slab steps, chimney, spire
for i in range(9):
    a = 17 - 2 * i
    _b.append(_F(-a, 7 + i, -a, a, 7 + i, a, 'deepslate_tile_slab[type=bottom]'))
    if a > 1:
        _b.append(_F(-(a - 1), 7 + i, -(a - 1), a - 1, 7 + i, a - 1, 'deepslate_tiles'))
_b += [_S(0, 16, 0, 'lightning_rod'), _F(-14, 7, -5, -13, 11, -4, 'bricks'), _S(-14, 12, -5, 'campfire[lit=true]'),
       _S(-13, 12, -4, 'campfire[lit=true]')]
# porch
_b += [_F(-3, 6, 17, 3, 6, 18, 'dark_oak_slab[type=bottom]'), _F(-3, 1, 18, -3, 5, 18, 'dark_oak_fence'), _F(3, 1, 18, 3, 5, 18, 'dark_oak_fence'),
       _S(-2, 5, 17, 'lantern[hanging=true]'), _S(2, 5, 17, 'lantern[hanging=true]')]
# --- NW library
_b += [_F(-15, 1, -15, -15, 4, -7, 'bookshelf'), _F(-15, 1, -15, -7, 4, -15, 'bookshelf'), _F(-13, 1, -12, -10, 3, -12, 'bookshelf'),
       _F(-13, 1, -10, -9, 1, -8, 'red_carpet'), _S(-9, 1, -9, 'lectern[facing=south]'), _S(-11, 5, -11, 'lantern[hanging=true]'),
       _S(-14, 1, -9, 'spruce_stairs[facing=west]'), _S(-14, 1, -14, 'potted_fern')]
# --- N dining room
_b += [_F(-3, 1, -12, 3, 1, -10, 'dark_oak_slab[type=top]'), _F(-4, 1, -15, -2, 1, -15, 'stripped_spruce_log[axis=y]'), _F(2, 1, -15, 4, 1, -15, 'stripped_spruce_log[axis=y]'),
       _S(-4, 2, -15, 'potted_red_tulip'), _S(4, 2, -15, 'potted_white_tulip'), _S(-3, 2, -15, 'lantern'), _S(3, 2, -15, 'lantern')]
for cx_ in (-3, -1, 1, 3):
    _b += [_S(cx_, 1, -13, 'spruce_stairs[facing=north]'), _S(cx_, 1, -9, 'spruce_stairs[facing=south]')]
for cx_ in (-2, 0, 2):
    _b.append(_S(cx_, 2, -11, 'candle[candles=3,lit=true]'))
_b += [_S(-2, 5, -11, 'lantern[hanging=true]'), _S(2, 5, -11, 'lantern[hanging=true]')]
# --- NE kitchen
_b += [_F(8, 1, -15, 14, 1, -15, 'polished_andesite'), _S(9, 1, -15, 'polished_deepslate'), _S(11, 1, -15, 'polished_deepslate'),
       _S(13, 1, -15, 'water_cauldron[level=3]'), _F(15, 1, -14, 15, 2, -13, 'stripped_spruce_log[axis=x]'), _S(15, 1, -10, 'fletching_table'),
       _F(10, 1, -11, 12, 1, -10, 'smooth_stone_slab[type=top]'), _S(11, 2, -11, 'cake'), _S(11, 5, -12, 'lantern[hanging=true]'),
       _S(8, 2, -15, 'potted_cactus')]
# --- W lounge with fireplace
_b += [_F(-15, 1, -5, -11, 4, -5, 'bricks'), _S(-13, 1, -5, 'campfire[lit=true,facing=south]'), _S(-13, 2, -5, 'air'),
       _F(-15, 3, -4, -11, 3, -4, 'spruce_slab[type=top]'), _F(-14, 1, 0, -9, 1, 3, 'brown_carpet'),
       _S(-14, 1, -2, 'spruce_stairs[facing=south]'), _S(-12, 1, -2, 'spruce_stairs[facing=south]'),
       _S(-10, 1, -1, 'dark_oak_fence'), _S(-10, 2, -1, 'oak_pressure_plate'), _S(-11, 5, 1, 'lantern[hanging=true]'),
       _S(-15, 1, 4, 'bookshelf'), _S(-15, 2, 4, 'potted_allium')]
# --- great hall
_b += [_F(-5, 1, -1, 5, 1, 1, 'red_carpet'), _F(-1, 1, -5, 1, 1, 5, 'red_carpet'), _S(0, 5, 0, 'iron_chain[axis=y]'), _S(0, 4, 0, 'lantern[hanging=true]'),
       _S(2, 5, 0, 'lantern[hanging=true]'), _S(-2, 5, 0, 'lantern[hanging=true]'), _S(0, 5, 2, 'lantern[hanging=true]'), _S(0, 5, -2, 'lantern[hanging=true]')]
for c1 in (-5, 5):
    for c2 in (-5, 5):
        _b.append(_S(c1, 1, c2, 'flowering_azalea'))
# --- E music room
_b += [_F(9, 1, -3, 13, 1, 3, 'cyan_carpet'), _F(13, 1, -5, 15, 1, -5, 'polished_blackstone'), _F(13, 2, -5, 15, 2, -5, 'quartz_slab[type=bottom]'),
       _S(14, 1, -4, 'spruce_stairs[facing=south]'), _S(15, 1, 3, 'jukebox'), _S(15, 1, 2, 'note_block'), _S(15, 1, -2, 'note_block'),
       _S(11, 5, 0, 'lantern[hanging=true]'), _S(15, 1, 5, 'potted_bamboo')]
# --- SW bedroom
_b += [_S(-15, 1, 9, 'red_bed[facing=west,part=head]'), _S(-14, 1, 9, 'red_bed[facing=west,part=foot]'),
       _S(-15, 1, 12, 'blue_bed[facing=west,part=head]'), _S(-14, 1, 12, 'blue_bed[facing=west,part=foot]'),
       _S(-15, 1, 10, 'stripped_spruce_log[axis=y]'), _S(-15, 2, 10, 'candle[candles=2,lit=true]'),
       _F(-13, 1, 15, -11, 3, 15, 'stripped_spruce_wood'), _F(-13, 1, 9, -10, 1, 13, 'white_carpet'), _S(-11, 5, 11, 'lantern[hanging=true]')]
# --- S entrance hall
_b += [_F(-1, 1, 7, 1, 1, 15, 'red_carpet'), _S(-3, 1, 15, 'potted_azalea_bush'), _S(3, 1, 15, 'potted_azalea_bush'),
       _F(-5, 1, 11, -5, 1, 13, 'spruce_stairs[facing=west]'), _F(5, 1, 11, 5, 1, 13, 'spruce_stairs[facing=east]'),
       _F(-5, 1, 15, -5, 2, 15, 'dark_oak_fence'), _S(0, 5, 11, 'lantern[hanging=true]')]
# --- SE greenhouse
_b += [_F(13, 0, 13, 14, 0, 14, 'water'), _S(13, 1, 13, 'lily_pad'), _S(15, 1, 7, 'flowering_azalea'), _S(7, 1, 15, 'flowering_azalea'),
       _S(15, 1, 15, 'azalea'), _S(8, 1, 8, 'potted_orange_tulip'), _S(15, 1, 10, 'potted_oxeye_daisy'),
       _F(8, 1, 11, 8, 1, 12, 'spruce_stairs[facing=west]'), _S(11, 5, 11, 'lantern[hanging=true]')]
# sign above the door, spawn markers
_b.append(holo('mg_murderh', f'{MX}.5', MY + 4.6, f'{MZ + 17}.6', [{'text': 'Villa Nachtschatten', 'color': 'dark_red', 'bold': True}], 1.2))
for sx, sz in _SPAWNS:
    _b.append(f'{OW} summon minecraft:marker {MX + sx}.5 {MY + 1} {MZ + sz}.5 {{Tags:["mg_murder_sp"]}}')
_b.append(f'{OW} kill @e[type=minecraft:item,{_AREA}]')     # blocks popped while clearing the old map

# ------------------------------------------------------------------ functions
_ROLE_TAGS = ('mg_murder_m', 'mg_murder_d', 'mg_murder_i', 'mg_murder_bad', 'mg_murder_hero')
ENTER_LINES.extend([f'tag @s remove {t}' for t in _ROLE_TAGS])
EXTRA_LOAD.extend([
    'scoreboard objectives add mg_murder_k playerKillCount', 'scoreboard objectives add mg_murder_g dummy', 'scoreboard objectives add mg_murder_cd dummy',
    'team add mg_murder_t', 'team modify mg_murder_t nametagVisibility never', 'team modify mg_murder_t deathMessageVisibility never',
    'team modify mg_murder_t friendlyFire true', 'team modify mg_murder_t seeFriendlyInvisibles false',
    f'bossbar add {NS}:murder {tc({"text": "Murder Mystery"})}', f'bossbar set {NS}:murder max {_LEN}', f'bossbar set {NS}:murder style notched_10',
    f'scoreboard players set #murder_len mg {_LEN}', 'scoreboard players set #murder_200 mg 200',
    f'execute unless entity @a[tag={_T}] run bossbar set {NS}:murder visible false',
    f'execute unless entity @a[tag={_T}] run bossbar set {NS}:murder players',
])

fn('murder/spawn_one', ['tp @s @e[type=minecraft:marker,tag=mg_murder_sp,tag=!mg_murder_used,sort=random,limit=1]',
                        'execute at @s run tag @e[type=minecraft:marker,tag=mg_murder_sp,distance=..0.6] add mg_murder_used',
                        'execute at @s run playsound minecraft:block.wooden_door.open master @s ~ ~ ~ 0.6 0.8'])
_setup = [*[f'tag @a[tag={_T}] remove {t}' for t in _ROLE_TAGS],
          f'execute as @a[tag={_T}] run function {NS}:murder/spawn_one',
          f'kill @e[type=minecraft:marker,tag=mg_murder_sp]',
          f'team join mg_murder_t @a[tag={_T}]',
          f'tag @a[tag={_T},sort=random,limit=1] add mg_murder_m',
          f'tag @a[tag={_T},tag=!mg_murder_m,sort=random,limit=1] add mg_murder_d',
          f'tag @a[tag={_T},tag=!mg_murder_m,tag=!mg_murder_d] add mg_murder_i',
          f'scoreboard players set @a[tag={_T}] mg_murder_k 0', f'scoreboard players set @a[tag={_T}] mg_murder_g 0',
          f'scoreboard players set @a[tag={_T}] mg_murder_cd 0',
          f'effect give @a[tag={_T}] minecraft:weakness infinite 0 true',      # fists do no damage: only sword + bows can kill
          f'effect give @a[tag={_T}] minecraft:saturation infinite 0 true',
          f'effect give @a[tag={_T}] minecraft:instant_health 1 10 true',
          'scoreboard players set #murder_win mg 0',
          f'bossbar set {NS}:murder color yellow', f'bossbar set {NS}:murder value {_LEN}', f'bossbar set {NS}:murder players @a[tag={_T}]',
          f'bossbar set {NS}:murder visible true']


def _title(sel, t, tcol, sub):
    return [f'title {sel} times 5 70 20', f'title {sel} subtitle {tc({"text": sub, "color": "gray"})}',
            f'title {sel} title {tc({"text": t, "color": tcol, "bold": True})}']


fn('murder/reveal', [
    *_title('@a[tag=mg_murder_m]', 'Du bist der MÖRDER', 'dark_red', 'Erledige alle – aber bleib unerkannt!'),
    *_title('@a[tag=mg_murder_d]', 'Du bist der DETEKTIV', 'aqua', 'Finde den Mörder und erschieße ihn!'),
    *_title('@a[tag=mg_murder_i]', 'Du bist UNSCHULDIG', 'green', 'Überlebe! 10 Gold = Bogen + Pfeil'),
    f'tellraw @a[tag=mg_murder_m] {msg(_txt("Du bist der Mörder. In 7 Sekunden bekommst du dein Schwert – ein Treffer tötet. Tu so, als wärst du unschuldig!", "red"))}',
    f'tellraw @a[tag=mg_murder_d] {msg(_txt("Du bist der Detektiv. In 7 Sekunden bekommst du einen Bogen. Nach jedem Schuss gibt es nach 5 s einen neuen Pfeil. Triffst du einen Unschuldigen, stirbst du selbst!", "aqua"))}',
    f'tellraw @a[tag=mg_murder_i] {msg(_txt("Du bist unschuldig. Versteck dich, sammle Gold (10 Gold = Bogen + Pfeil) und überlebe 4 Minuten!", "green"))}',
    'execute as @a[tag=mg_murder_m] at @s run playsound minecraft:entity.elder_guardian.curse master @s ~ ~ ~ 0.7 1',
    'execute as @a[tag=mg_murder_d] at @s run playsound minecraft:block.note_block.chime master @s ~ ~ ~ 1 1.2',
    'execute as @a[tag=mg_murder_i] at @s run playsound minecraft:block.note_block.bell master @s ~ ~ ~ 1 1',
])
fn('murder/arm', [
    f'give @a[tag={_AL},tag=mg_murder_m] {SWORD}',
    f'give @a[tag={_AL},tag=mg_murder_d] {_bow("dbow")}', f'give @a[tag={_AL},tag=mg_murder_d] minecraft:arrow 1',
    f'tellraw @a[tag=mg_murder_m] {msg(_txt("Dein Schwert ist bereit. Viel Spaß beim Jagen ...", "dark_red"))}',
    f'title @a[tag={_T}] actionbar {tc({"text": "Der Mörder hat jetzt seine Waffe!", "color": "red", "bold": True})}',
    f'execute as @a[tag={_T}] at @s run playsound minecraft:entity.wither.spawn master @s ~ ~ ~ 0.35 1.4',
])

# death of a player in the round
fn('murder/died', [
    'scoreboard players set @s mg_deaths 0', f'tag @s remove {_AL}', 'gamemode spectator @s', 'clear @s',
    f'execute in minecraft:overworld run tp @s {_SPECT[0]} {_SPECT[1]} {_SPECT[2]}',
    f'execute if entity @s[tag=mg_murder_m] run return run function {NS}:murder/m_dead',
    f'execute store result score #murder_alive mg if entity @a[tag={_AL},tag=!mg_murder_m]',
    f'execute if entity @s[tag=mg_murder_d] run tellraw @a[tag={_T}] {msg(_txt("Der Detektiv ist tot! ", "aqua", bold=True), _txt("Sein Bogen liegt jetzt irgendwo am Boden ...", "gray"))}',
    f'execute unless entity @s[tag=mg_murder_bad] run tellraw @a[tag={_T}] {msg(_txt("☠ ", "dark_red"), {"selector": "@s", "color": "white"}, _txt(" ist tot! ", "red"), _txt("Unschuldige am Leben: ", "gray"), {"score": {"name": "#murder_alive", "objective": "mg"}, "color": "white"})}',
    f'execute if entity @s[tag=mg_murder_bad] run tellraw @a[tag={_T}] {msg(_txt("☠ ", "dark_red"), _txt("Unschuldige am Leben: ", "gray"), {"score": {"name": "#murder_alive", "objective": "mg"}, "color": "white"})}',
    *_title('@s', 'Du bist tot!', 'dark_red', 'Du schaust jetzt zu – nichts verraten!'),
    f'execute as @a[tag={_T}] at @s run playsound minecraft:entity.player.hurt_sweet_berry_bush master @s ~ ~ ~ 0.4 0.5',
    f'execute as @a[tag={_T}] at @s run playsound minecraft:block.bell.resonate master @s ~ ~ ~ 0.5 0.6',
    'scoreboard players add @s mg_coins 2',
])
fn('murder/m_dead', [
    'scoreboard players set #murder_win mg 1',
    f'tag @a[tag={_T},tag=!mg_murder_m,scores={{mg_murder_k=1..}}] add mg_murder_hero',
    f'execute if entity @a[tag=mg_murder_hero] run tellraw @a[tag={_T}] {msg({"selector": "@a[tag=mg_murder_hero]", "color": "aqua", "bold": True}, _txt(" hat den Mörder ", "white"), {"selector": "@s", "color": "dark_red", "bold": True}, _txt(" zur Strecke gebracht!", "white"))}',
    f'execute unless entity @a[tag=mg_murder_hero] run tellraw @a[tag={_T}] {msg(_txt("Der Mörder ", "white"), {"selector": "@s", "color": "dark_red", "bold": True}, _txt(" ist tot!", "white"))}',
    'scoreboard players add @a[tag=mg_murder_hero] mg_coins 10',
])
fn('murder/punish', [
    'scoreboard players set @s mg_murder_k 0', 'tag @s add mg_murder_bad',
    f'tellraw @a[tag={_T}] {msg({"selector": "@s", "color": "white"}, _txt(" hat einen Unschuldigen getötet – und stirbt dafür selbst!", "red"))}',
    'kill @s',
])
# bows / arrows / gold, every 5 ticks
_BOWITEM = 'minecraft:bow'
_slow = [
    # the detective bow on the ground: no normal pickup, glows, only innocents can take it
    f'execute as @e[type=minecraft:item,{_AREA},tag=!mg_murder_bi] unless data entity @s {{PickupDelay:32767s}} if items entity @s contents *[minecraft:custom_data~{{mg_murder:"dbow"}}] run function {NS}:murder/bow_drop',
    f'execute as @e[type=minecraft:item,tag=mg_murder_bi] at @s if entity @a[tag={_AL},tag=!mg_murder_m,gamemode=adventure,distance=..1.8] run function {NS}:murder/bow_take',
    f'execute at @e[type=minecraft:item,tag=mg_murder_bi] run particle minecraft:end_rod ~ ~0.6 ~ 0.15 0.3 0.15 0.01 2',
    # other dropped weapons/arrows vanish
    f'execute as @e[type=minecraft:item,{_AREA}] if items entity @s contents minecraft:arrow run kill @s',
    f'execute as @e[type=minecraft:item,{_AREA}] if items entity @s contents *[minecraft:custom_data~{{mg_murder:"ibow"}}] run kill @s',
    f'execute as @e[type=minecraft:item,{_AREA}] if items entity @s contents *[minecraft:custom_data~{{mg_murder:"sword"}}] run kill @s',
    f'kill @e[type=minecraft:arrow,{_AREA},nbt={{inGround:1b}}]',
    # murderer never keeps a bow, always has his sword after 10 s
    'clear @a[tag=mg_murder_m] minecraft:bow', 'clear @a[tag=mg_murder_m] minecraft:arrow',
    f'execute if score #murder_t mg matches 205.. as @a[tag={_AL},tag=mg_murder_m] ' + ' '.join('unless' + c[2:] for c in _has('sword')) + f' run give @s {SWORD}',
    # gold -> bow + arrow
    f'execute as @a[tag={_AL}] store result score @s mg_murder_g run clear @s minecraft:gold_ingot 0',
    f'execute as @a[tag={_AL},scores={{mg_murder_g=10..}}] run function {NS}:murder/buy',
    # lost detective bow (disconnect / despawn): lay a new one in the great hall
    f'execute if score #murder_t mg matches 210.. run function {NS}:murder/bow_check',
]
fn('murder/slow', _slow)
fn('murder/bow_drop', [
    'tag @s add mg_murder_bi', 'data merge entity @s {PickupDelay:32767,Glowing:1b,Age:-32768}',
    f'tellraw @a[tag={_T}] {msg(_txt("Der Detektiv-Bogen liegt am Boden! ", "aqua", bold=True), _txt("Unschuldige können ihn aufheben.", "gray"))}',
    f'execute as @a[tag={_T}] at @s run playsound minecraft:block.amethyst_block.chime master @s ~ ~ ~ 1 0.8',
])
fn('murder/bow_take', [f'execute as @p[tag={_AL},tag=!mg_murder_m,gamemode=adventure,distance=..1.8] run function {NS}:murder/bow_get', 'kill @s'])
fn('murder/bow_get', [
    'clear @s minecraft:bow', f'give @s {_bow("dbow")}', 'execute unless items entity @s container.* minecraft:arrow run give @s minecraft:arrow 1',
    'scoreboard players set @s mg_murder_cd 0', 'tag @s remove mg_murder_i', 'tag @s add mg_murder_d',
    f'tellraw @a[tag={_T}] {msg(_txt("Jemand hat den Detektiv-Bogen aufgehoben!", "aqua"))}',
    f'tellraw @s {msg(_txt("Du hast jetzt den Detektiv-Bogen – finde den Mörder!", "aqua", bold=True))}',
    'playsound minecraft:item.armor.equip_chain master @s ~ ~ ~ 1 1.2',
])
fn('murder/bow_check', [
    f'execute store result score #n mg run clear @a[tag={_AL}] *[minecraft:custom_data~{{mg_murder:"dbow"}}] 0',
    'execute if entity @e[type=minecraft:item,tag=mg_murder_bi] run scoreboard players add #n mg 1',
    f'execute if score #n mg matches 0 run function {NS}:murder/bow_respawn',
])
fn('murder/bow_respawn', [   # already locked (no vanilla pickup), then turned into the real detective bow
    f'{OW} summon minecraft:item {MX}.5 {MY + 1.2} {MZ}.5 {{Item:{{id:"minecraft:bow",count:1}},PickupDelay:32767,Age:-32768,Glowing:1b,Tags:["mg_murder_bi","mg_murder_bnew"],Motion:[0.0,0.0,0.0]}}',
    f'item replace entity @e[type=minecraft:item,tag=mg_murder_bnew] contents with {_bow("dbow")}',
    'tag @e[type=minecraft:item,tag=mg_murder_bnew] remove mg_murder_bnew',
    f'tellraw @a[tag={_T}] {msg(_txt("Der Detektiv-Bogen liegt in der großen Halle! ", "aqua", bold=True), _txt("Unschuldige können ihn aufheben.", "gray"))}',
    f'execute as @a[tag={_T}] at @s run playsound minecraft:block.amethyst_block.chime master @s ~ ~ ~ 1 0.8',
])
# detective needs a new arrow: holds the bow anywhere (also offhand / cursor / crafting grid) and has no arrow left
fn('murder/need_arrow', [
    'execute store result score #n mg run clear @s minecraft:arrow 0', 'execute if score #n mg matches 1.. run return 0',
    'execute store result score #n mg run clear @s *[minecraft:custom_data~{mg_murder:"dbow"}] 0', 'execute if score #n mg matches 1.. run return 1',
    'return 0',
])
fn('murder/buy', [
    'clear @s minecraft:gold_ingot 10', 'scoreboard players remove @s mg_murder_g 10',
    f'execute if entity @s[tag=mg_murder_m] run return run function {NS}:murder/buy_m',
    f'execute unless items entity @s container.* {_BOWITEM} run tellraw @s {msg(_txt("10 Gold eingetauscht: ", "gold"), _txt("Bogen + Pfeil!", "green", bold=True))}',
    f'execute if items entity @s container.* {_BOWITEM} run tellraw @s {msg(_txt("10 Gold eingetauscht: ", "gold"), _txt("+1 Pfeil!", "green", bold=True))}',
    f'execute unless items entity @s container.* {_BOWITEM} run give @s {_bow("ibow")}',
    'give @s minecraft:arrow 1',
    'playsound minecraft:entity.player.levelup master @s ~ ~ ~ 1 1.3',
])
fn('murder/buy_m', ['effect give @s minecraft:speed 10 1 true',
                    f'tellraw @s {msg(_txt("10 Gold eingetauscht: ", "gold"), _txt("10 s Tempo!", "dark_red", bold=True))}',
                    'playsound minecraft:entity.player.levelup master @s ~ ~ ~ 1 0.8'])
fn('murder/arrow_give', ['give @s minecraft:arrow 1', 'playsound minecraft:item.crossbow.loading_end master @s ~ ~ ~ 1 1.2'])
# gold spawning
_g1 = ['execute store result score #r mg run random value 0..%d' % (len(_GOLD) - 1)]
for i, (gx, gz) in enumerate(_GOLD):
    _g1.append(f'execute if score #r mg matches {i} in minecraft:overworld positioned {MX + gx}.5 {MY + 1} {MZ + gz}.5 unless entity @e[type=minecraft:item,distance=..1.5] '
               f'run summon minecraft:item ~ ~0.3 ~ {{Item:{{id:"minecraft:gold_ingot",count:1}},Tags:["mg_murder_gi"],Motion:[0.0,0.2,0.0]}}')
fn('murder/gold_one', _g1)
fn('murder/gold', [f'execute store result score #n mg if entity @e[type=minecraft:item,{_AREA},tag=mg_murder_gi]',
                   'execute if score #n mg matches 14.. run return 0',
                   *[f'function {NS}:murder/gold_one'] * 3])
# HUD: bossbar timer + role in the actionbar
_ab_gold = [_txt('   Gold ', 'gold'), {'score': {'name': '@s', 'objective': 'mg_murder_g'}, 'color': 'yellow'}, _txt('/10', 'gold')]
fn('murder/hud', [
    'scoreboard players operation #murder_rem mg = #murder_len mg', 'scoreboard players operation #murder_rem mg -= #murder_t mg',
    'scoreboard players operation #murder_s mg = #murder_rem mg', 'scoreboard players add #murder_s mg 19', 'scoreboard players operation #murder_s mg /= #20 mg',
    'scoreboard players operation #murder_mm mg = #murder_s mg', 'scoreboard players operation #murder_mm mg /= #60 mg',
    'scoreboard players operation #murder_ss mg = #murder_s mg', 'scoreboard players operation #murder_ss mg %= #60 mg',
    'scoreboard players operation #murder_s10 mg = #murder_ss mg', 'scoreboard players operation #murder_s10 mg /= #10 mg',
    'scoreboard players operation #murder_s1 mg = #murder_ss mg', 'scoreboard players operation #murder_s1 mg %= #10 mg',
    f'execute store result score #murder_alive mg if entity @a[tag={_AL},tag=!mg_murder_m]',
    f'execute store result bossbar {NS}:murder value run scoreboard players get #murder_rem mg',
    f'bossbar set {NS}:murder name ' + tc([_txt('Villa Nachtschatten  ', 'dark_red', bold=True), _txt('⌛ ', 'gray'),
                                           {'score': {'name': '#murder_mm', 'objective': 'mg'}, 'color': 'white'}, _txt(':', 'white'),
                                           {'score': {'name': '#murder_s10', 'objective': 'mg'}, 'color': 'white'},
                                           {'score': {'name': '#murder_s1', 'objective': 'mg'}, 'color': 'white'},
                                           _txt('   ☺ ', 'green'), {'score': {'name': '#murder_alive', 'objective': 'mg'}, 'color': 'white'},
                                           _txt(' Unschuldige', 'gray')]),
    f'bossbar set {NS}:murder players @a[tag={_T}]',
    f'execute as @a[tag={_AL},tag=mg_murder_m] run title @s actionbar ' + tc([_txt('⚔ MÖRDER', 'dark_red', bold=True)] + _ab_gold),
    f'execute as @a[tag={_AL},tag=mg_murder_d,scores={{mg_murder_cd=0}}] run title @s actionbar ' + tc([_txt('✪ DETEKTIV', 'aqua', bold=True)] + _ab_gold),
    f'execute as @a[tag={_AL},tag=mg_murder_d,scores={{mg_murder_cd=1..}}] run title @s actionbar ' + tc([_txt('✪ DETEKTIV', 'aqua', bold=True), _txt('   Pfeil lädt ...', 'gray')] + _ab_gold),
    f'execute as @a[tag={_AL},tag=mg_murder_i] run title @s actionbar ' + tc([_txt('☺ UNSCHULDIG', 'green', bold=True)] + _ab_gold),
    f'title @a[tag={_T},tag=!{_AL}] actionbar ' + tc([_txt('☠ Du bist tot', 'gray', bold=True), _txt(' – du schaust zu', 'dark_gray')]),
])
fn('murder/last_minute', [
    f'bossbar set {NS}:murder color red',
    f'effect give @a[tag={_AL}] minecraft:glowing infinite 0 true',      # everyone, murderer included - otherwise he is the only one not glowing
    f'tellraw @a[tag={_T}] {msg(_txt("Noch 60 Sekunden! ", "red", bold=True), _txt("Alle Lebenden leuchten jetzt – niemand kann sich mehr verstecken!", "gray"))}',
    f'execute as @a[tag={_T}] at @s run playsound minecraft:block.bell.use master @s ~ ~ ~ 1 0.7',
])
_disarm = [f'clear @a[tag={_T}] minecraft:iron_sword', f'clear @a[tag={_T}] minecraft:bow', f'clear @a[tag={_T}] minecraft:arrow',
           f'effect give @a[tag={_T}] minecraft:resistance 10 4 true', f'{OW} kill @e[type=minecraft:arrow,{_AREA}]',
           f'kill @e[type=minecraft:item,tag=mg_murder_bi]']
_reveal_end = [
    f'execute if entity @a[tag=mg_murder_m] run tellraw @a[tag={_T}] {msg(_txt("Der Mörder war: ", "gray"), {"selector": "@a[tag=mg_murder_m]", "color": "dark_red", "bold": True})}',
    f'execute if entity @a[tag=mg_murder_d] run tellraw @a[tag={_T}] {msg(_txt("Detektiv: ", "gray"), {"selector": "@a[tag=mg_murder_d]", "color": "aqua", "bold": True})}',
]
fn('murder/win_i', [
    f'tag @a[tag={_T},tag=!mg_murder_m,tag=!mg_murder_bad] add {_AL}', f'tag @a[tag=mg_murder_m] remove {_AL}', f'tag @a[tag=mg_murder_bad] remove {_AL}',
    f'title @a[tag={_T}] subtitle {tc(_txt("Die Unschuldigen gewinnen!", "green", bold=True))}',
    f'tellraw @a[tag={_T}] {msg(_txt("Die Unschuldigen gewinnen!", "green", bold=True))}',
    *_reveal_end,
    f'execute as @a[tag={_AL}] at @s run playsound minecraft:ui.toast.challenge_complete master @s ~ ~ ~ 1 1',
    f'execute as @a[tag=mg_murder_m] at @s run playsound minecraft:entity.wither.death master @s ~ ~ ~ 0.4 1.2',
    *_disarm,
    f'function {NS}:murder/end',
])
fn('murder/win_m', [
    f'tag @a[tag={_T}] remove {_AL}', f'tag @a[tag=mg_murder_m] add {_AL}',
    f'title @a[tag={_T}] subtitle {tc(_txt("Der Mörder gewinnt!", "dark_red", bold=True))}',
    f'tellraw @a[tag={_T}] {msg(_txt("Kein Unschuldiger ist mehr übrig – der Mörder gewinnt!", "dark_red", bold=True))}',
    *_reveal_end,
    f'execute as @a[tag={_T}] at @s run playsound minecraft:entity.wither.spawn master @s ~ ~ ~ 0.5 0.8',
    *_disarm,
    f'function {NS}:murder/end',
])

_game = [
    'scoreboard players operation #m mg = #murder_t mg', 'scoreboard players operation #m mg %= #20 mg',
    'scoreboard players operation #m5 mg = #murder_t mg', 'scoreboard players operation #m5 mg %= #5 mg',
    'scoreboard players operation #m200 mg = #murder_t mg', 'scoreboard players operation #m200 mg %= #murder_200 mg',
    f'execute if score #murder_t mg matches 60 run function {NS}:murder/reveal',
    f'execute if score #murder_t mg matches 200 run function {NS}:murder/arm',
    f'execute if score #murder_t mg matches {_LEN - 1200} run function {NS}:murder/last_minute',
    f'execute if score #murder_t mg matches {_LEN - 200}.. if score #m mg matches 0 as @a[tag={_T}] at @s run playsound minecraft:block.note_block.hat master @s ~ ~ ~ 1 1.5',
    # deaths, then "shot an innocent" punishment
    f'execute as @a[tag={_AL},scores={{mg_deaths=1..}}] run function {NS}:murder/died',
    f'execute if score #murder_win mg matches 0 as @a[tag={_AL},tag=!mg_murder_m,scores={{mg_murder_k=1..}}] run function {NS}:murder/punish',
    'scoreboard players set @a[tag=mg_murder_m] mg_murder_k 0',
    # detective arrow reload: 5 s after the last arrow is gone
    f'execute as @a[tag={_AL},scores={{mg_murder_cd=1}}] run function {NS}:murder/arrow_give',
    f'scoreboard players remove @a[tag={_AL},scores={{mg_murder_cd=1..}}] mg_murder_cd 1',
    f'execute as @a[tag={_AL},tag=!mg_murder_m,scores={{mg_murder_cd=0}}] if function {NS}:murder/need_arrow run scoreboard players set @s mg_murder_cd 100',
    f'execute if score #m5 mg matches 0 run function {NS}:murder/slow',
    f'execute if score #m200 mg matches 100 run function {NS}:murder/gold',
    f'execute if score #m mg matches 0 run function {NS}:murder/hud',
    f'execute if score #m mg matches 10 run function {NS}:murder/hud',
    # end conditions
    f'execute if score #murder_win mg matches 1 run return run function {NS}:murder/win_i',
    f'execute unless entity @a[tag={_AL},tag=mg_murder_m] run tellraw @a[tag={_T}] {msg(_txt("Der Mörder hat das Spiel verlassen!", "yellow", bold=True))}',
    f'execute unless entity @a[tag={_AL},tag=mg_murder_m] run return run function {NS}:murder/win_i',
    f'execute unless entity @a[tag={_AL},tag=!mg_murder_m] run return run function {NS}:murder/win_m',
    f'execute if score #murder_t mg matches {_LEN}.. run tellraw @a[tag={_T}] {msg(_txt("Die Zeit ist um – der Mörder hat versagt!", "yellow", bold=True))}',
    f'execute if score #murder_t mg matches {_LEN}.. run return run function {NS}:murder/win_i',
]
_cleanup = [f'bossbar set {NS}:murder players', f'bossbar set {NS}:murder visible false',
            *[f'tag @a remove {t}' for t in _ROLE_TAGS], 'team empty mg_murder_t',
            f'kill @e[type=minecraft:marker,tag=mg_murder_sp]', f'kill @e[type=minecraft:item,tag=mg_murder_bi]',
            f'{OW} kill @e[type=minecraft:arrow,{_AREA}]']

party(_K, 'Murder Mystery', 'dark_red', (MX, MY, MZ), trig=62, prof='cleric', sub='Mörder · Detektiv · Unschuldige', menu='Finde den Mörder – oder sei es',
      info='Einer ist der Mörder (Schwert, ein Treffer tötet), einer der Detektiv (Bogen, neuer Pfeil nach 5 s), alle anderen sind unschuldig. '
           'Sammle Gold: 10 Gold = Bogen + Pfeil. Wer einen Unschuldigen erschießt, stirbt selbst. Die Unschuldigen gewinnen, wenn der Mörder stirbt '
           'oder 4 Minuten um sind – der Mörder, wenn alle anderen tot sind. Namen sind versteckt!',
      minp=3, maxp=12, size=32, build=_b, setup=_setup, game=_game, cleanup=_cleanup, custom_end=True,
      title_sub='Wer ist der Mörder?', spect=_SPECT, coins_win=10)
