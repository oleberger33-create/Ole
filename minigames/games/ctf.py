# Capture the Flag: Team Rot vs Team Blau on "Burg Zwiestein" - two fortresses facing each other across a river valley.
# Step onto the enemy flag pedestal to steal the banner, bring it to your own flag (while yours is at home) to score.
# The carrier glows; if he dies (or leaves) the flag flies home. 3 captures win, otherwise the score after 8 minutes
# (tie -> 2 minutes sudden death, then a draw where nobody wins). Respawn after 3 s at the own base.
CX, CY, CZ = 78000, Y, 0
_K = 'ctf'
_T, _AL = 'mg_ctf', 'mg_al_ctf'
_SPECT = (CX, CY + 22, CZ + 30)
_LEN = 9600                      # 8 minutes
_SD = 2400                       # + 2 minutes sudden death
_AREA = f'x={CX - 44},y={CY - 6},z={CZ - 20},dx=88,dy=34,dz=40'
_FX = 35                         # flag pedestal |x|
_SPX = 40                        # spawn |x|

# team key -> data. s = side (-1 west / +1 east), IN = facing towards the middle
TM = {
    'r': dict(s=-1, name='Rot', up='ROT', col='red', rgb=11546150, dust='[0.85,0.12,0.12]', o='b', adj='rote', team='mg_ctf_rot',
              IN='east', OUT='west', rot=12, yaw=-90),
    'b': dict(s=1, name='Blau', up='BLAU', col='blue', rgb=3949738, dust='[0.2,0.3,0.95]', o='r', adj='blaue', team='mg_ctf_blau',
              IN='west', OUT='east', rot=4, yaw=90),
}


def _F(x1, y1, z1, x2, y2, z2, b, mode=''):
    return f'{OW} fill {CX + x1} {CY + y1} {CZ + z1} {CX + x2} {CY + y2} {CZ + z2} minecraft:{b}' + (f' {mode}' if mode else '')


def _S(x, y, z, b, mode=''):
    return f'{OW} setblock {CX + x} {CY + y} {CZ + z} minecraft:{b}' + (f' {mode}' if mode else '')


def _txt(text, color, **kw):
    return dict(text=text, color=color, italic=False, **kw)


def _flagpos(t):
    return CX + TM[t]['s'] * _FX, CY + 2, CZ


def _banner_block(t):
    return (f'minecraft:{TM[t]["col"]}_banner[rotation={TM[t]["rot"]}]'
            '{patterns:[{pattern:"minecraft:rhombus",color:"white"},{pattern:"minecraft:border",color:"black"}]}')


def _set_banner(t):
    x, y, z = _flagpos(t)
    return f'{OW} setblock {x} {y} {z} {_banner_block(t)}'


def _head_item(t):
    d = TM[t]
    return (f'minecraft:{d["col"]}_banner[minecraft:banner_patterns=[{{pattern:"minecraft:rhombus",color:"white"}},{{pattern:"minecraft:border",color:"black"}}],'
            f'minecraft:enchantments={{"minecraft:binding_curse":1}},minecraft:custom_name={tc(_txt("Flagge " + d["name"], d["col"], bold=True))}]')


def _armor(t, piece):
    return (f'minecraft:leather_{piece}[minecraft:dyed_color={TM[t]["rgb"]},minecraft:unbreakable={{}},'
            'minecraft:tooltip_display={hidden_components:["minecraft:dyed_color","minecraft:unbreakable"]}]')


# ------------------------------------------------------------------ map "Burg Zwiestein"
_b = [f'kill @e[type=minecraft:text_display,tag=mg_ctfh]', f'{OW} kill @e[type=minecraft:item,{_AREA}]', f'{OW} kill @e[type=minecraft:arrow,{_AREA}]']
_b += clear_box(CX - 44, CY - 3, CZ - 20, CX + 44, CY + 16, CZ + 20, 6)
# ground
_b += [_F(-42, -3, -18, 42, -2, 18, 'stone'), _F(-42, -1, -18, 42, -1, 18, 'dirt'), _F(-42, 0, -18, 42, 0, 18, 'grass_block')]
# border: stone brick wall with mossy patches, invisible barrier above
for a in (-18, 18):
    _b += [_F(-42, 1, a, 42, 2, a, 'stone_bricks'), _F(-42, 3, a, 42, 14, a, 'barrier')]
for a in (-42, 42):
    _b += [_F(a, 1, -18, a, 2, 18, 'stone_bricks'), _F(a, 3, -18, a, 14, 18, 'barrier')]
_rng = random.Random(6464)
for _ in range(40):
    x, z = _rng.randint(-41, 41), _rng.choice((-18, 18))
    _b.append(_S(x, _rng.randint(1, 2), z, _rng.choice(('mossy_stone_bricks', 'cracked_stone_bricks'))))

# river valley in the middle: water channel along z, sand bed
_b += [_F(-1, -2, -17, 1, -2, 17, 'sand'), _F(-1, -1, -17, 1, 0, 17, 'water'),
       _F(-2, 0, -17, -2, 0, 17, 'mud_bricks'), _F(2, 0, -17, 2, 0, 17, 'mud_bricks')]
for z in range(-16, 17, 5):
    _b.append(_S(_rng.choice((-1, 0, 1)), -1, z, 'seagrass'))
# bridges
for zc in (-11, 11):
    _b += [_F(-2, 0, zc - 2, 2, 0, zc + 2, 'spruce_planks'), _F(-2, 1, zc - 2, 2, 1, zc - 2, 'spruce_fence'),
           _F(-2, 1, zc + 2, 2, 1, zc + 2, 'spruce_fence'), _S(-2, 2, zc - 2, 'lantern'), _S(2, 2, zc + 2, 'lantern'),
           _S(2, 2, zc - 2, 'lantern'), _S(-2, 2, zc + 2, 'lantern')]
# central plaza with obelisk (slab rim = walkable step)
_b += [f'{OW} {c}' for c in disk(CX, CY, CZ, 7, 'stone_bricks')]
_b += [f'{OW} {c}' for c in disk(CX, CY + 1, CZ, 6, 'andesite_slab[type=bottom]')]
_b += [f'{OW} {c}' for c in disk(CX, CY + 1, CZ, 5, 'polished_andesite')]
_b += [f'{OW} {c}' for c in disk(CX, CY + 1, CZ, 2, 'chiseled_stone_bricks')]
_b += [_F(0, 2, 0, 0, 5, 0, 'quartz_pillar'), _S(0, 6, 0, 'sea_lantern'), _S(0, 7, 0, 'end_rod'),
       _S(-1, 2, 0, 'quartz_stairs[facing=east]'), _S(1, 2, 0, 'quartz_stairs[facing=west]'),
       _S(0, 2, -1, 'quartz_stairs[facing=south]'), _S(0, 2, 1, 'quartz_stairs[facing=north]')]
for ox in (-4, 4):
    for oz in (-4, 4):
        _b += [_F(ox, 2, oz, ox, 3, oz, 'andesite_wall'), _S(ox, 4, oz, 'lantern')]
_b.append(holo('mg_ctfh', f'{CX}.5', CY + 9.5, f'{CZ}.5', [{'text': 'Burg Zwiestein', 'color': 'gold', 'bold': True}], 2.0))


def _tree(x, z):
    L = 'oak_leaves[persistent=true]'
    return [_F(x - 2, 3, z - 2, x + 2, 4, z + 2, L, 'keep'), _F(x - 1, 5, z - 1, x + 1, 5, z + 1, L, 'keep'), _S(x, 6, z, L, 'keep'),
            _F(x, 1, z, x, 5, z, 'oak_log')]


def _side(t):
    """Everything on one half (mirrored in x). Coordinates are written for Blau (east, +x) and mirrored with s."""
    d = TM[t]
    s, c, IN, OUT = d['s'], d['col'], d['IN'], d['OUT']
    X = lambda x: s * x
    F = lambda x1, y1, z1, x2, y2, z2, b, m='': _F(X(x1), y1, z1, X(x2), y2, z2, b, m)
    S = lambda x, y, z, b, m='': _S(X(x), y, z, b, m)
    o = []
    # ---- middle field: paths, cover, trees
    o += [F(3, 0, -1, 26, 0, 1, 'dirt_path'), F(8, 0, -1, 9, 0, 1, 'coarse_dirt'), F(19, 0, -1, 20, 0, 1, 'coarse_dirt')]
    for sz in (-1, 1):
        Z = lambda z: sz * z
        # low walls (2 high) left and right of the path
        o += [F(9, 1, Z(3), 9, 2, Z(7), 'mossy_stone_bricks'), S(9, 3, Z(4), 'mossy_stone_brick_slab[type=bottom]'),
              S(9, 3, Z(5), 'mossy_stone_brick_slab[type=bottom]'), F(9, 1, Z(7), 11, 1, Z(7), 'mossy_stone_bricks')]
        # ruined arch
        o += [F(20, 1, Z(6), 20, 4, Z(6), 'stone_bricks'), F(20, 1, Z(10), 20, 4, Z(10), 'stone_bricks'),
              F(20, 5, Z(6), 20, 5, Z(10), 'stone_brick_slab[type=bottom]'), S(20, 4, Z(8), 'stone_bricks'),
              S(20, 4, Z(7), 'stone_bricks'), S(20, 4, Z(9), 'cracked_stone_bricks'), S(20, 2, Z(10), 'cracked_stone_bricks'),
              S(20, 3, Z(6), 'mossy_stone_bricks')]
        # hay and crates near the flanks
        o += [F(11, 1, Z(13), 12, 1, Z(13), 'hay_block[axis=x]'), S(11, 2, Z(13), 'hay_block[axis=x]'), S(12, 1, Z(14), 'hay_block[axis=z]')]
        o += [F(16, 1, Z(15), 17, 2, Z(16), 'barrel[facing=up]'), S(17, 1, Z(14), 'barrel[facing=up]')]
        # lamp posts along the path
        o += [S(5, 1, Z(3), 'spruce_fence'), S(5, 2, Z(3), 'spruce_fence'), S(5, 3, Z(3), 'lantern'),
              S(24, 1, Z(3), 'spruce_fence'), S(24, 2, Z(3), 'spruce_fence'), S(24, 3, Z(3), 'lantern')]
    # crate cluster on the centre line (cover in front of the gate)
    o += [F(15, 1, -1, 16, 2, 0, 'barrel[facing=up]'), S(15, 1, 1, 'spruce_planks'), S(16, 1, 1, 'barrel[facing=up]'),
          S(15, 3, -1, 'spruce_slab[type=bottom]')]
    # trees
    for tx, tz in ((7, 14), (7, -14), (22, 15), (22, -15), (13, -9), (13, 9)):
        o += _tree(X(tx), tz)
    # ---- the fortress: courtyard x28..41, z-11..11
    o += [F(28, 0, -11, 41, 0, 11, 'stone_bricks'), F(28, 0, -1, 41, 0, 1, f'{c}_concrete'),
          F(28, -1, -11, 41, -1, 11, 'stone')]
    for x in (30, 33, 37, 40):
        o += [S(x, 0, -7, 'sea_lantern'), S(x, 0, 7, 'sea_lantern')]
    # front wall x=27 with three gates and windows
    o += [F(27, 1, -11, 27, 3, 11, 'deepslate_bricks'), F(27, 4, -11, 27, 4, 11, f'{c}_concrete')]
    o += [S(27, 5, z, 'deepslate_brick_wall') for z in range(-11, 12, 2)]
    o += [F(27, 1, -1, 27, 3, 1, 'air'), F(27, 1, 6, 27, 3, 7, 'air'), F(27, 1, -7, 27, 3, -6, 'air')]
    for z in (-9, -3, 3, 9):
        o.append(F(27, 2, z, 27, 3, z, f'{c}_stained_glass'))
    for z in (-4, 4):
        o.append(S(26, 3, z, f'{c}_wall_banner[facing={IN}]'))
    # side walls z=+-12 with a gate to the flank
    for sz in (-1, 1):
        z = 12 * sz
        o += [F(28, 1, z, 41, 3, z, 'deepslate_bricks'), F(28, 4, z, 41, 4, z, f'{c}_concrete'),
              F(33, 1, z, 35, 3, z, 'air'), F(30, 2, z, 30, 3, z, f'{c}_stained_glass'), F(38, 2, z, 38, 3, z, f'{c}_stained_glass')]
        o += [S(x, 5, z, 'deepslate_brick_wall') for x in range(29, 42, 2)]
    # watch towers at the front corners: x25..27, z +-12..+-14, ladder inside, entrance from the flank
    for sz in (-1, 1):
        Z = lambda z: sz * z
        o += [F(25, 1, Z(12), 27, 7, Z(14), 'deepslate_tiles'), F(26, 1, Z(13), 26, 7, Z(13), 'air'),
              F(27, 1, Z(13), 27, 2, Z(13), 'air'), F(25, 4, Z(13), 25, 4, Z(13), f'{c}_stained_glass'),
              F(24, 8, Z(11), 28, 8, Z(15), 'polished_deepslate'), F(25, 7, Z(12), 27, 7, Z(14), f'{c}_concrete'),
              F(26, 7, Z(13), 26, 8, Z(13), 'air')]
        per = [(x, Z(11)) for x in range(24, 29)] + [(x, Z(15)) for x in range(24, 29)] + [(24, Z(z)) for z in (12, 13, 14)] + [(28, Z(z)) for z in (12, 13, 14)]
        for px, pz in sorted(set(per)):
            if (px + pz) % 2 == 0:
                o.append(S(px, 9, pz, 'deepslate_tile_wall'))
        o.append(F(26, 1, Z(13), 26, 8, Z(13), f'ladder[facing={"north" if sz > 0 else "south"}]'))
        o += [S(27, 10, Z(11), f'{c}_banner[rotation={d["rot"]}]')]
    # flag pedestal: beacon (team-coloured beam) under a glass pedestal, banner on top
    o += [f'{OW} {cmd}' for cmd in disk(CX + X(_FX), CY, CZ, 2, 'polished_blackstone_bricks')]
    o += [F(_FX - 1, -1, -1, _FX + 1, -1, 1, 'iron_block'), S(_FX, 0, 0, 'beacon'), S(_FX, 1, 0, f'{c}_stained_glass')]
    for ox in (-2, 2):
        for oz in (-2, 2):
            o += [S(_FX + ox, 1, oz, 'polished_blackstone_wall'), S(_FX + ox, 2, oz, 'soul_lantern')]
    # spawn pad + back-wall banners
    o += [F(_SPX - 1, 0, -1, _SPX + 1, 0, 1, f'{c}_glazed_terracotta'), S(_SPX, 0, 0, 'sea_lantern')]
    for z in (-8, -5, 5, 8):
        o.append(S(41, 2, z, f'{c}_wall_banner[facing={IN}]'))
    # flank: bushes
    o += [F(31, 1, 15, 32, 1, 16, 'azalea_leaves[persistent=true]'), F(31, 1, -16, 32, 1, -15, 'azalea_leaves[persistent=true]'),
          S(38, 1, 16, 'flowering_azalea'), S(38, 1, -16, 'flowering_azalea')]
    # flowers (seeded, same layout on both sides)
    fr = random.Random(77)
    for _ in range(90):
        fx, fz = fr.randint(4, 25), fr.randint(-17, 17)
        if abs(fz) <= 2 or (fx <= 8 and abs(fz) <= 8):
            continue
        o.append(S(fx, 1, fz, fr.choice(('short_grass', 'short_grass', 'short_grass', 'poppy', 'dandelion', 'cornflower', 'oxeye_daisy', 'azure_bluet')), 'keep'))
    # flag holo
    o.append(f'{OW} summon minecraft:text_display {CX + X(_FX)}.5 {CY + 4.3} {CZ}.5 {{Tags:["mg_holo","mg_ctfh","mg_ctfh_{t}"],billboard:"center",'
             f'background:0,shadow:true,text:{tc(_txt("⚑ Flagge " + d["name"], c, bold=True))},transformation:{{left_rotation:[0f,0f,0f,1f],'
             f'right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[1.3f,1.3f,1.3f]}}}}')
    o.append(_set_banner(t))
    return o


for t in TM:
    _b += _side(t)
_b.append(f'{OW} kill @e[type=minecraft:item,{_AREA}]')

# ------------------------------------------------------------------ state / helpers
_TAGS = ('mg_ctf_r', 'mg_ctf_b', 'mg_ctf_c', 'mg_ctf_kl', 'mg_ctf_cam')
ENTER_LINES.extend([f'tag @s remove {t}' for t in _TAGS] + ['scoreboard players set @s mg_ctf_rs 0'])
EXTRA_LOAD.extend([
    'scoreboard objectives add mg_ctf_k playerKillCount', 'scoreboard objectives add mg_ctf_rs dummy', 'scoreboard objectives add mg_ctf_a dummy',
    'scoreboard objectives add mg_ctf_cap dummy',
    f'bossbar add {NS}:ctf {tc({"text": "Capture the Flag"})}', f'bossbar set {NS}:ctf max {_LEN}', f'bossbar set {NS}:ctf style notched_10',
    f'scoreboard players set #ctf_len mg {_LEN}',
    # server restarted mid-round: nobody is in a round any more -> hide the stale bar
    f'execute unless entity @a[tag={_T}] run bossbar set {NS}:ctf visible false',
    f'execute unless entity @a[tag={_T}] run bossbar set {NS}:ctf players',
])
for t, d in TM.items():
    EXTRA_LOAD += [f'team add {d["team"]}', f'team modify {d["team"]} color {d["col"]}', f'team modify {d["team"]} friendlyFire false',
                   f'team modify {d["team"]} seeFriendlyInvisibles true', f'team modify {d["team"]} displayName {tc(_txt("Team " + d["name"], d["col"]))}',
                   f'team modify {d["team"]} prefix {tc({"text": "[" + d["name"] + "] ", "color": d["col"]})}']


def _title(sel, t, tcol, sub, subcol='gray'):
    return [f'title {sel} times 5 40 15', f'title {sel} subtitle {tc(_txt(sub, subcol))}', f'title {sel} title {tc(_txt(t, tcol, bold=True))}']


_SCORE = [_txt('Rot ', 'red', bold=True), {'score': {'name': '#ctf_sr', 'objective': 'mg'}, 'color': 'white', 'bold': True},
          _txt(' : ', 'gray'), {'score': {'name': '#ctf_sb', 'objective': 'mg'}, 'color': 'white', 'bold': True}, _txt(' Blau', 'blue', bold=True)]

fn('ctf/assign', [
    f'execute store result score #ctf_nr mg if entity @a[tag={_T},tag=mg_ctf_r]',
    f'execute store result score #ctf_nb mg if entity @a[tag={_T},tag=mg_ctf_b]',
    f'execute if score #ctf_nr mg <= #ctf_nb mg run return run function {NS}:ctf/join_r',
    f'function {NS}:ctf/join_b'])
for t, d in TM.items():
    o = TM[d['o']]
    sx = CX + d['s'] * _SPX
    fx, fy, fz = _flagpos(t)
    cam_x = CX + d['s'] * 22
    fn(f'ctf/join_{t}', [f'tag @s add mg_ctf_{t}', f'team join {d["team"]} @s', f'{OW} spawnpoint @s {sx} {CY + 1} {CZ}',
                         f'tellraw @s {msg(_txt("Du spielst für ", "gray"), _txt("Team " + d["name"], d["col"], bold=True), _txt("! Klau die " + o["adj"] + " Flagge.", "gray"))}'])
    fn(f'ctf/kit_{t}', [
        'clear @s',
        f'give @s minecraft:stone_sword[minecraft:unbreakable={{}},minecraft:tooltip_display={{hidden_components:["minecraft:unbreakable"]}}]',
        f'give @s minecraft:bow[minecraft:unbreakable={{}},minecraft:tooltip_display={{hidden_components:["minecraft:unbreakable"]}}]',
        'give @s minecraft:cooked_beef 8', 'give @s minecraft:arrow 16',
        f'item replace entity @s armor.head with {_armor(t, "helmet")}', f'item replace entity @s armor.chest with {_armor(t, "chestplate")}',
        f'item replace entity @s armor.legs with {_armor(t, "leggings")}', f'item replace entity @s armor.feet with {_armor(t, "boots")}'])
    # (re)spawn at the own base
    fn(f'ctf/spawn_{t}', [
        'gamemode adventure @s', f'{OW} tp @s {sx}.5 {CY + 1} {CZ}.5 {d["yaw"]} 0', f'function {NS}:ctf/kit_{t}',
        'effect clear @s', 'effect give @s minecraft:instant_health 1 10 true', 'effect give @s minecraft:saturation 1 4 true',
        'effect give @s minecraft:resistance 3 4 true',
        'scoreboard players set @s mg_ctf_rs 0',
        'playsound minecraft:item.armor.equip_iron master @s ~ ~ ~ 1 1'])
    # flag of team t is stolen by @s (a player of the other team)
    fn(f'ctf/take_{t}', [
        f'scoreboard players set #ctf_f{t} mg 1', f'{OW} setblock {fx} {fy} {fz} minecraft:air',
        'tag @s add mg_ctf_c', f'item replace entity @s armor.head with {_head_item(t)}', 'effect give @s minecraft:glowing infinite 0 true',
        f'data merge entity @e[type=minecraft:text_display,tag=mg_ctfh_{t},limit=1] {{text:{tc(_txt("⚑ Flagge gestohlen!", "gold", bold=True))}}}',
        f'tellraw @a[tag={_T}] {msg({"selector": "@s"}, _txt(" hat die Flagge von ", "white"), _txt("Team " + d["name"], d["col"], bold=True), _txt(" gestohlen!", "white"))}',
        *_title(f'@a[tag={_T},tag=mg_ctf_{t}]', 'FLAGGE GESTOHLEN!', 'red', 'Schnappt euch den leuchtenden Dieb!'),
        *_title('@s', 'DU HAST DIE FLAGGE!', 'gold', 'Bring sie zu deiner Basis!', 'yellow'),
        f'execute as @a[tag={_T},tag=mg_ctf_{t}] at @s run playsound minecraft:block.bell.use master @s ~ ~ ~ 1 0.6',
        f'execute as @a[tag={_T},tag=mg_ctf_{d["o"]}] at @s run playsound minecraft:block.note_block.pling master @s ~ ~ ~ 1 1.6',
        f'execute at @s run playsound minecraft:entity.player.levelup master @s ~ ~ ~ 1 1.4'])
    # flag of team t goes back home
    fn(f'ctf/home_{t}', [
        f'scoreboard players set #ctf_f{t} mg 0', _set_banner(t),
        f'data merge entity @e[type=minecraft:text_display,tag=mg_ctfh_{t},limit=1] {{text:{tc(_txt("⚑ Flagge " + d["name"], d["col"], bold=True))}}}'])
    fn(f'ctf/ret_{t}', [
        f'function {NS}:ctf/home_{t}',
        f'tellraw @a[tag={_T}] {msg(_txt("Die Flagge von ", "gray"), _txt("Team " + d["name"], d["col"], bold=True), _txt(" ist zurück in der Basis.", "gray"))}',
        f'title @a[tag={_T},tag=mg_ctf_{t}] actionbar {tc(_txt("Eure Flagge ist wieder zuhause!", "green", bold=True))}',
        f'execute as @a[tag={_T}] at @s run playsound minecraft:block.beacon.power_select master @s ~ ~ ~ 0.8 1.3'])
    # @s (team t) captures the enemy flag
    fn(f'ctf/cap_{t}', [
        f'execute unless score #ctf_f{t} mg matches 0 run return 0',
        f'scoreboard players add #ctf_s{t} mg 1', f'function {NS}:ctf/home_{d["o"]}',
        'tag @s remove mg_ctf_c', 'effect clear @s minecraft:glowing', f'item replace entity @s armor.head with {_armor(t, "helmet")}',
        'scoreboard players add @s mg_coins 3', 'scoreboard players add @s mg_ctf_cap 1',
        f'tellraw @a[tag={_T}] {msg({"selector": "@s"}, _txt(" hat die Flagge erobert! ", "gold", bold=True), *_SCORE)}',
        *_title(f'@a[tag={_T}]', f'TEAM {d["up"]} PUNKTET!', d['col'], ''),
        f'title @a[tag={_T}] subtitle {tc(_SCORE)}',
        f'execute as @a[tag={_T},tag=mg_ctf_{t}] at @s run playsound minecraft:ui.toast.challenge_complete master @s ~ ~ ~ 1 1.2',
        f'execute as @a[tag={_T},tag=mg_ctf_{d["o"]}] at @s run playsound minecraft:entity.wither.ambient master @s ~ ~ ~ 0.5 1.5',
        f'execute in minecraft:overworld run summon minecraft:firework_rocket {fx}.5 {fy + 1} {fz}.5 {{LifeTime:25,FireworksItem:{{id:"minecraft:firework_rocket",count:1,components:{{"minecraft:fireworks":{{flight_duration:1,explosions:[{{shape:"star",colors:[I;{d["rgb"]}],fade_colors:[I;16777215],has_twinkle:true}}]}}}}}}}}'])
    # death / respawn
    # the camera tp is done by ctf/cam_* from ctf/rs once the player has really respawned (a tp on the death screen is lost)
    fn(f'ctf/dead_{t}', [
        'gamemode spectator @s', 'tag @s remove mg_ctf_cam', 'scoreboard players set @s mg_ctf_rs 60',
        *_title('@s', 'Du bist gestorben!', 'red', 'Respawn in 3 Sekunden ...')])
    fn(f'ctf/cam_{t}', ['gamemode spectator @s', f'{OW} tp @s {cam_x}.5 {CY + 12} {CZ}.5 {-d["yaw"]} 30', 'tag @s add mg_ctf_cam'])
    # end: team t wins
    fn(f'ctf/win_{t}', [
        f'tag @a[tag={_T}] remove {_AL}', f'tag @a[tag={_T},tag=mg_ctf_{t}] add {_AL}',
        f'tellraw @a[tag={_T}] {msg(_txt("Team " + d["name"] + " gewinnt! ", d["col"], bold=True), *_SCORE)}',
        f'title @a[tag={_T}] subtitle {tc(_txt("Team " + d["name"] + " gewinnt!", d["col"], bold=True))}',
        f'execute as @a[tag={_T},tag=mg_ctf_{t}] at @s run playsound minecraft:ui.toast.challenge_complete master @s ~ ~ ~ 1 1',
        f'execute as @a[tag={_T},tag=!mg_ctf_{t}] at @s run playsound minecraft:entity.wither.death master @s ~ ~ ~ 0.4 1.2',
        f'function {NS}:ctf/end'])

fn('ctf/died', [
    'scoreboard players set @s mg_deaths 0',
    f'execute if entity @s[tag=mg_ctf_c] run tellraw @a[tag={_T}] {msg({"selector": "@s"}, _txt(" hat die Flagge verloren!", "yellow"))}',
    'tag @s remove mg_ctf_c',
    f'execute if entity @a[tag=mg_ctf_kl] run tellraw @a[tag={_T}] {msg(_txt("☠ ", "dark_red"), {"selector": "@s"}, _txt(" wurde von ", "gray"), {"selector": "@a[tag=mg_ctf_kl,limit=1]"}, _txt(" erledigt.", "gray"))}',
    f'execute unless entity @a[tag=mg_ctf_kl] run tellraw @a[tag={_T}] {msg(_txt("☠ ", "dark_red"), {"selector": "@s"}, _txt(" ist gestorben.", "gray"))}',
    f'execute if entity @s[tag=mg_ctf_r] run function {NS}:ctf/dead_r',
    f'execute if entity @s[tag=mg_ctf_b] run function {NS}:ctf/dead_b'])
fn('ctf/rs', [
    'scoreboard players remove @s mg_ctf_rs 1',
    # still on the death screen? (Health 0) -> no camera yet, and never run the respawn before the player is back
    'execute store result score #ctf_hp mg run data get entity @s Health',
    'execute if score #ctf_hp mg matches ..0 if score @s mg_ctf_rs matches ..0 run scoreboard players set @s mg_ctf_rs 1',
    f'execute if score #ctf_hp mg matches 1.. if entity @s[tag=!mg_ctf_cam,tag=mg_ctf_r] run function {NS}:ctf/cam_r',
    f'execute if score #ctf_hp mg matches 1.. if entity @s[tag=!mg_ctf_cam,tag=mg_ctf_b] run function {NS}:ctf/cam_b',
    f'execute if score @s mg_ctf_rs matches 59 run title @s actionbar {tc(_txt("Respawn in 3 ...", "gray"))}',
    f'execute if score @s mg_ctf_rs matches 40 run title @s actionbar {tc(_txt("Respawn in 2 ...", "gray"))}',
    f'execute if score @s mg_ctf_rs matches 20 run title @s actionbar {tc(_txt("Respawn in 1 ...", "gray"))}',
    'execute if score @s mg_ctf_rs matches 20 run playsound minecraft:block.note_block.hat master @s ~ ~ ~ 1 1',
    'execute unless score @s mg_ctf_rs matches ..0 run return 0',
    f'execute if entity @s[tag=mg_ctf_r] run function {NS}:ctf/spawn_r',
    f'execute if entity @s[tag=mg_ctf_b] run function {NS}:ctf/spawn_b',
    'title @s clear'])

# ---- HUD (every 10 ticks): bossbar with score + time, status in the actionbar
_tm = ['scoreboard players operation #ctf_rem mg = #ctf_len mg',
       f'execute if score #ctf_sd mg matches 1 run scoreboard players set #ctf_rem mg {_LEN + _SD}',   # overtime: time until the draw
       'scoreboard players operation #ctf_rem mg -= #ctf_t mg',
       'execute if score #ctf_rem mg matches ..0 run scoreboard players set #ctf_rem mg 0',
       'scoreboard players operation #ctf_s mg = #ctf_rem mg', 'scoreboard players add #ctf_s mg 19', 'scoreboard players operation #ctf_s mg /= #20 mg',
       'scoreboard players operation #ctf_mm mg = #ctf_s mg', 'scoreboard players operation #ctf_mm mg /= #60 mg',
       'scoreboard players operation #ctf_ss mg = #ctf_s mg', 'scoreboard players operation #ctf_ss mg %= #60 mg',
       'scoreboard players operation #ctf_s10 mg = #ctf_ss mg', 'scoreboard players operation #ctf_s10 mg /= #10 mg',
       'scoreboard players operation #ctf_s1 mg = #ctf_ss mg', 'scoreboard players operation #ctf_s1 mg %= #10 mg',
       f'execute store result bossbar {NS}:ctf value run scoreboard players get #ctf_rem mg',
       f'execute if score #ctf_sd mg matches 0 run bossbar set {NS}:ctf name ' + tc(_SCORE + [_txt('     ⌛ ', 'gray'),
            {'score': {'name': '#ctf_mm', 'objective': 'mg'}, 'color': 'white'}, _txt(':', 'white'),
            {'score': {'name': '#ctf_s10', 'objective': 'mg'}, 'color': 'white'}, {'score': {'name': '#ctf_s1', 'objective': 'mg'}, 'color': 'white'}]),
       f'execute if score #ctf_sd mg matches 1 run bossbar set {NS}:ctf name ' + tc(_SCORE + [_txt('     VERLÄNGERUNG – nächste Eroberung gewinnt!  ⌛ ', 'light_purple', bold=True),
            {'score': {'name': '#ctf_mm', 'objective': 'mg'}, 'color': 'white'}, _txt(':', 'white'),
            {'score': {'name': '#ctf_s10', 'objective': 'mg'}, 'color': 'white'}, {'score': {'name': '#ctf_s1', 'objective': 'mg'}, 'color': 'white'}]),
       f'bossbar set {NS}:ctf players @a[tag={_T}]']
for t, d in TM.items():
    o = d['o']
    P = f'@a[tag={_AL},tag=mg_ctf_{t},gamemode=adventure'
    _tm += [
        f'execute if score #ctf_f{t} mg matches 0 run title {P},tag=mg_ctf_c] actionbar ' + tc(_txt('⚑ Du hast die Flagge! Lauf zu deiner Basis!', 'gold', bold=True)),
        f'execute if score #ctf_f{t} mg matches 1 run title {P},tag=mg_ctf_c] actionbar ' + tc(_txt('⚑ Eure Flagge ist weg – erst zurückholen, dann punkten!', 'red', bold=True)),
        f'execute if score #ctf_f{t} mg matches 1 run title {P},tag=!mg_ctf_c] actionbar ' + tc(_txt('Eure Flagge wurde gestohlen! Jagt den leuchtenden Dieb!', 'red', bold=True)),
        f'execute if score #ctf_f{t} mg matches 0 if score #ctf_f{o} mg matches 1 run title {P},tag=!mg_ctf_c] actionbar ' + tc(_txt('Ein Teamkollege hat die Flagge – gib ihm Deckung!', 'green')),
        f'execute if score #ctf_f{t} mg matches 0 if score #ctf_f{o} mg matches 0 run title {P},tag=!mg_ctf_c] actionbar ' + tc(_txt(f'Hol die Flagge von Team {TM[o]["name"]}!', TM[o]['col'])),
    ]
fn('ctf/hud', _tm)

fn('ctf/timeup', [
    f'execute if score #ctf_sr mg > #ctf_sb mg run tellraw @a[tag={_T}] {msg(_txt("Die Zeit ist um!", "yellow", bold=True))}',
    f'execute if score #ctf_sr mg > #ctf_sb mg run return run function {NS}:ctf/win_r',
    f'execute if score #ctf_sb mg > #ctf_sr mg run tellraw @a[tag={_T}] {msg(_txt("Die Zeit ist um!", "yellow", bold=True))}',
    f'execute if score #ctf_sb mg > #ctf_sr mg run return run function {NS}:ctf/win_b',
    'scoreboard players set #ctf_sd mg 1',
    f'bossbar set {NS}:ctf color purple', f'bossbar set {NS}:ctf max {_SD}', f'bossbar set {NS}:ctf value {_SD}',
    f'tellraw @a[tag={_T}] {msg(_txt("Gleichstand! ", "light_purple", bold=True), _txt("Verlängerung: Die nächste Eroberung gewinnt – du hast 2 Minuten!", "white"))}',
    *_title(f'@a[tag={_T}]', 'VERLÄNGERUNG!', 'light_purple', 'Die nächste Eroberung gewinnt'),
    f'execute as @a[tag={_T}] at @s run playsound minecraft:entity.ender_dragon.growl master @s ~ ~ ~ 0.5 1.2'])
fn('ctf/draw', [
    f'tag @a[tag={_T}] remove {_AL}',
    f'tellraw @a[tag={_T}] {msg(_txt("Die Verlängerung ist vorbei – keine Eroberung. Beide Teams verlieren!", "gray"))}',
    f'title @a[tag={_T}] subtitle {tc(_txt("Unentschieden!", "gray", bold=True))}',
    f'function {NS}:ctf/end'])
fn('ctf/left', [  # one team has nobody left
    f'tellraw @a[tag={_T}] {msg(_txt("Das gegnerische Team hat das Spiel verlassen.", "yellow"))}',
    f'execute if entity @a[tag={_AL},tag=mg_ctf_r] run return run function {NS}:ctf/win_r',
    f'execute if entity @a[tag={_AL},tag=mg_ctf_b] run return run function {NS}:ctf/win_b',
    f'function {NS}:ctf/end'])
fn('ctf/arrows', [f'execute as @a[tag={_AL},gamemode=adventure] store result score @s mg_ctf_a run clear @s minecraft:arrow 0',
                  f'give @a[tag={_AL},gamemode=adventure,scores={{mg_ctf_a=..7}}] minecraft:arrow 1'])
_UNB = '[minecraft:unbreakable={},minecraft:tooltip_display={hidden_components:["minecraft:unbreakable"]}]'
fn('ctf/kitchk', [f'execute as @a[tag={_AL},gamemode=adventure] store result score @s mg_ctf_a run clear @s minecraft:stone_sword 0',
                  f'give @a[tag={_AL},gamemode=adventure,scores={{mg_ctf_a=0}}] minecraft:stone_sword{_UNB}',
                  f'execute as @a[tag={_AL},gamemode=adventure] store result score @s mg_ctf_a run clear @s minecraft:bow 0',
                  f'give @a[tag={_AL},gamemode=adventure,scores={{mg_ctf_a=0}}] minecraft:bow{_UNB}'])
fn('ctf/slow', [
    f'{OW} kill @e[type=minecraft:item,{_AREA}]',
    *[f'execute at @a[tag={_AL},tag=mg_ctf_{TM[t]["o"]},tag=mg_ctf_c] run particle minecraft:dust{{color:{d["dust"]},scale:1.5}} ~ ~2.4 ~ 0.25 0.25 0.25 0 4 force'
      for t, d in TM.items()],
])

# ------------------------------------------------------------------ setup + tick
_setup = [
    'scoreboard players set #ctf_fr mg 0', 'scoreboard players set #ctf_fb mg 0', 'scoreboard players set #ctf_sr mg 0',
    'scoreboard players set #ctf_sb mg 0', 'scoreboard players set #ctf_sd mg 0',
    *[f'tag @a[tag={_T}] remove {t}' for t in _TAGS],
    f'scoreboard players set @a[tag={_T}] mg_ctf_rs 0', f'scoreboard players set @a[tag={_T}] mg_ctf_k 0', f'scoreboard players set @a[tag={_T}] mg_ctf_cap 0',
    f'execute as @a[tag={_T},sort=random] run function {NS}:ctf/assign',
    f'execute as @a[tag={_T},tag=mg_ctf_r] run function {NS}:ctf/spawn_r',
    f'execute as @a[tag={_T},tag=mg_ctf_b] run function {NS}:ctf/spawn_b',
    f'bossbar set {NS}:ctf color yellow', f'bossbar set {NS}:ctf max {_LEN}', f'bossbar set {NS}:ctf value {_LEN}', f'bossbar set {NS}:ctf players @a[tag={_T}]',
    f'bossbar set {NS}:ctf visible true',
    f'function {NS}:ctf/hud',
]
_game = [
    'scoreboard players operation #m mg = #ctf_t mg', 'scoreboard players operation #m mg %= #20 mg',
    'scoreboard players operation #m5 mg = #ctf_t mg', 'scoreboard players operation #m5 mg %= #5 mg',
    # deaths (killer is tagged first for the kill message), respawn timers
    f'execute as @a[tag={_AL},scores={{mg_ctf_k=1..}}] run tag @s add mg_ctf_kl',
    f'execute as @a[tag={_AL},scores={{mg_ctf_k=1..}}] at @s run playsound minecraft:entity.experience_orb.pickup master @s ~ ~ ~ 1 0.8',
    f'scoreboard players add @a[tag={_AL},scores={{mg_ctf_k=1..}}] mg_coins 1',
    f'execute as @a[tag={_AL},scores={{mg_deaths=1..}}] run function {NS}:ctf/died',
    'tag @a[tag=mg_ctf_kl] remove mg_ctf_kl', f'scoreboard players set @a[tag={_T},scores={{mg_ctf_k=1..}}] mg_ctf_k 0',
    f'execute as @a[tag={_AL},scores={{mg_ctf_rs=1..}}] run function {NS}:ctf/rs',
    # only living players: a spectator waiting for the respawn may fly below the map
    f'execute as @a[tag={_AL},gamemode=adventure] at @s if entity @s[y=-64,dy={CY - 6 + 64}] run kill @s',
]
for t, d in TM.items():
    o = d['o']
    fx, fy, fz = _flagpos(t)
    # carrier gone (died / left / disconnected) -> flag back home
    _game.append(f'execute if score #ctf_f{t} mg matches 1 unless entity @a[tag={_AL},tag=mg_ctf_{o},tag=mg_ctf_c] run function {NS}:ctf/ret_{t}')
    # pickup: an enemy steps onto the pedestal
    _game.append(f'execute if score #ctf_f{t} mg matches 0 in minecraft:overworld positioned {fx}.5 {fy} {fz}.5 as @a[tag={_AL},tag=mg_ctf_{o},tag=!mg_ctf_c,gamemode=adventure,distance=..1.6,sort=nearest,limit=1] run function {NS}:ctf/take_{t}')
    # capture: own carrier reaches the own flag
    _game.append(f'execute in minecraft:overworld positioned {fx}.5 {fy} {fz}.5 as @a[tag={_AL},tag=mg_ctf_{t},tag=mg_ctf_c,gamemode=adventure,distance=..2.6,limit=1] run function {NS}:ctf/cap_{t}')
_game += [
    f'execute if score #m5 mg matches 0 run function {NS}:ctf/slow',
    f'execute if score #m mg matches 0 run {OW} kill @e[type=minecraft:arrow,{_AREA},nbt={{inGround:1b}}]',
    f'execute if score #m mg matches 0 run function {NS}:ctf/hud', f'execute if score #m mg matches 10 run function {NS}:ctf/hud',
    'scoreboard players operation #m100 mg = #ctf_t mg', 'scoreboard players operation #m100 mg %= #100 mg',
    f'execute if score #m100 mg matches 50 run function {NS}:ctf/arrows',
    f'execute if score #ctf_t mg matches {_LEN - 1200} run tellraw @a[tag={_T}] {msg(_txt("Noch 1 Minute!", "yellow", bold=True))}',
    f'execute if score #ctf_t mg matches {_LEN - 1200} run bossbar set {NS}:ctf color red',
    f'execute if score #ctf_t mg matches {_LEN - 200}.. if score #ctf_t mg matches ..{_LEN - 1} if score #m mg matches 0 as @a[tag={_T}] at @s run playsound minecraft:block.note_block.hat master @s ~ ~ ~ 1 1.5',
    f'execute if score #ctf_t mg matches {_LEN + _SD - 200}.. if score #ctf_t mg matches ..{_LEN + _SD - 1} if score #m mg matches 0 as @a[tag={_T}] at @s run playsound minecraft:block.note_block.hat master @s ~ ~ ~ 1 1.5',
    # dropped sword / bow (Q) is deleted with the other items -> hand it back
    f'execute if score #m mg matches 5 run function {NS}:ctf/kitchk',
    # end conditions
    f'execute if score #ctf_sr mg matches 3.. run return run function {NS}:ctf/win_r',
    f'execute if score #ctf_sb mg matches 3.. run return run function {NS}:ctf/win_b',
    f'execute if score #ctf_sd mg matches 1 if score #ctf_sr mg > #ctf_sb mg run return run function {NS}:ctf/win_r',
    f'execute if score #ctf_sd mg matches 1 if score #ctf_sb mg > #ctf_sr mg run return run function {NS}:ctf/win_b',
    f'execute unless entity @a[tag={_AL},tag=mg_ctf_r] run return run function {NS}:ctf/left',
    f'execute unless entity @a[tag={_AL},tag=mg_ctf_b] run return run function {NS}:ctf/left',
    f'execute if score #ctf_t mg matches {_LEN} run return run function {NS}:ctf/timeup',
    f'execute if score #ctf_t mg matches {_LEN + _SD}.. run return run function {NS}:ctf/draw',
]
_cleanup = [f'bossbar set {NS}:ctf players', f'bossbar set {NS}:ctf visible false',
            *[f'tag @a remove {t}' for t in _TAGS], *[f'team empty {d["team"]}' for d in TM.values()],
            f'{OW} kill @e[type=minecraft:arrow,{_AREA}]']

party(_K, 'Capture the Flag', 'blue', (CX, CY, CZ), trig=64, prof='leatherworker', sub='Rot gegen Blau · 3 Flaggen gewinnen',
      menu='Klau die Flagge der Gegner',
      info='Team Rot gegen Team Blau. Lauf zur gegnerischen Burg und tritt auf ihr Flaggen-Podest, um die Flagge zu klauen. '
           'Bring sie zu deiner eigenen Flagge – das zählt nur, wenn deine Flagge zuhause ist! Der Träger leuchtet; stirbt er, fliegt die Flagge zurück. '
           'Wer zuerst 3 Flaggen erobert, gewinnt – sonst zählt der Stand nach 8 Minuten. Du respawnst nach 3 Sekunden in deiner Basis.',
      minp=2, maxp=16, size=48, build=_b, setup=_setup, game=_game, cleanup=_cleanup, custom_end=True,
      title_sub='Klau die Flagge!', spect=_SPECT, coins_win=10)
