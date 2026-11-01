# Verstecken (hide and seek): one random seeker, everyone else hides in "Moosgrund", an overgrown village with a
# half-timbered house (cellar, two floors, attic), a barn with hay loft, a chapel ruin with tower and crypt, a market
# with greenhouse and pond, a well with a secret tunnel and lots of bushes, trees and wood piles.
# Hiders get 40 s head start (seeker blinded in a cage on the village square), names are hidden.
# A hit hider becomes a seeker (nobody dies: everyone has resistance; detection via damage_taken + damage_dealt).
# Seekers win when everyone is found within 4 minutes, otherwise the remaining hiders win.
# Hiders can taunt (carrot on a stick: plays a sound at them, +1 coin). Last 60 s: hiders glow briefly every 15 s.
VX, VY, VZ = 82000, Y, 0
_K = 'verstecken'
_T, _AL = 'mg_verstecken', 'mg_al_verstecken'
_HID, _SEE, _ORIG, _FD, _NEW = 'mg_verstecken_hid', 'mg_verstecken_see', 'mg_verstecken_orig', 'mg_verstecken_fd', 'mg_verstecken_new'
_HEAD = 800                  # 40 s head start
_SEEK = 4800                 # 4 min seeking
_END = _HEAD + _SEEK
_AREA = f'x={VX - 30},y={VY - 8},z={VZ - 30},dx=60,dy=36,dz=60'
_SPECT = (VX, VY + 1, VZ + 5)


def _F(x1, y1, z1, x2, y2, z2, b):
    return f'{OW} fill {VX + x1} {VY + y1} {VZ + z1} {VX + x2} {VY + y2} {VZ + z2} minecraft:{b}'


def _S(x, y, z, b):
    return f'{OW} setblock {VX + x} {VY + y} {VZ + z} minecraft:{b}'


def _txt(text, color, **kw):
    return dict(text=text, color=color, italic=False, **kw)


_rng = random.Random(66)
_res = []          # reserved rectangles (x1, z1, x2, z2): no random decoration there


def _reserve(x1, z1, x2, z2):
    _res.append((min(x1, x2), min(z1, z2), max(x1, x2), max(z1, z2)))


def _free(x, z):
    return all(not (a <= x <= c and b <= z <= d) for a, b, c, d in _res)


PX, PZ = '[east=true,west=true]', '[north=true,south=true]'    # pane / bar connections along x / along z
LEAF = 'oak_leaves[persistent=true]'
AZL = 'azalea_leaves[persistent=true]'
FAZL = 'flowering_azalea_leaves[persistent=true]'

# ------------------------------------------------------------------ base, ground, border wall
_b = [f'kill @e[type=minecraft:text_display,tag=mg_versteckenh]', f'kill @e[type=minecraft:marker,tag=mg_verstecken_sp]',
      f'{OW} kill @e[type=minecraft:item,{_AREA}]']
_b += clear_box(VX - 30, VY - 7, VZ - 30, VX + 30, VY + 24, VZ + 30, 6)
_b += [_F(-28, -7, -28, 28, -7, 28, 'stone'), _F(-28, -6, -28, 28, -1, 28, 'dirt'), _F(-28, 0, -28, 28, 0, 28, 'grass_block')]
# border: mossy stone wall with spruce posts, hedge on top, invisible barrier above
for a in (-27, 27):
    _b += [_F(a, 1, -27, a, 3, 27, 'mossy_cobblestone'), _F(-27, 1, a, 27, 3, a, 'mossy_cobblestone'),
           _F(a, 4, -27, a, 5, 27, LEAF), _F(-27, 4, a, 27, 5, a, LEAF),
           _F(a, 6, -27, a, 24, 27, 'barrier'), _F(-27, 6, a, 27, 24, a, 'barrier')]
for p in range(-27, 28, 6):
    for a in (-27, 27):
        _b += [_F(a, 1, p, a, 4, p, 'spruce_log'), _F(p, 1, a, p, 4, a, 'spruce_log'),
               _S(a, 5, p, 'lantern'), _S(p, 5, a, 'lantern')]
# wall texture
for _ in range(90):
    a = _rng.choice((-27, 27))
    p = _rng.randint(-26, 26)
    y = _rng.randint(1, 3)
    blk = _rng.choice(['cobblestone', 'mossy_stone_bricks', 'stone', 'moss_block', 'cobblestone'])
    _b.append(_S(a, y, p, blk) if _rng.random() < 0.5 else _S(p, y, a, blk))
# paths: cross through the village, village square in the middle
_b += [_F(-26, 0, -1, 26, 0, 1, 'dirt_path'), _F(-1, 0, -26, 1, 0, 26, 'dirt_path'), _F(-7, 0, -7, 7, 0, 7, 'cobblestone')]
_reserve(-26, -1, 26, 1)
_reserve(-1, -26, 1, 26)
_reserve(-8, -8, 8, 8)
for x in range(-7, 8):
    for z in range(-7, 8):
        r = _rng.random()
        if r < 0.25:
            _b.append(_S(x, 0, z, 'mossy_cobblestone'))
        elif r < 0.35:
            _b.append(_S(x, 0, z, 'andesite'))
        elif r < 0.42 and (abs(x) == 7 or abs(z) == 7):
            _b.append(_S(x, 0, z, 'moss_block'))
_gnd = {}     # ground overrides (cover plants must not be placed on gravel)
for _ in range(70):     # worn path edges
    x, z = _rng.randint(-26, 26), _rng.choice((-2, 2, -1, 1))
    if abs(x) > 8:
        for gx, gz in ((x, z), (z, x)):
            g = _rng.choice(['coarse_dirt', 'gravel', 'rooted_dirt', 'grass_block', 'moss_block'])
            _gnd[(gx, gz)] = g
            _b.append(_S(gx, 0, gz, g))
# square: seeker cage (spruce posts, iron bars, roof), benches and lamp posts
_b += [_F(-2, 0, -2, 2, 0, 2, 'polished_andesite'), _S(0, 0, 0, 'chiseled_stone_bricks')]
for x, z in ((-2, -2), (2, -2), (-2, 2), (2, 2)):
    _b.append(_F(x, 1, z, x, 3, z, 'stripped_spruce_log'))
_CAGE = [_F(-1, 1, -2, 1, 3, -2, 'iron_bars' + PX), _F(-1, 1, 2, 1, 3, 2, 'iron_bars' + PX),
         _F(-2, 1, -1, -2, 3, 1, 'iron_bars' + PZ), _F(2, 1, -1, 2, 3, 1, 'iron_bars' + PZ)]
_b += _CAGE
_b += [_F(-3, 4, -3, 3, 4, 3, 'dark_oak_slab[type=bottom]'), _F(-2, 4, -2, 2, 4, 2, 'dark_oak_planks'), _S(0, 5, 0, 'dark_oak_slab[type=bottom]'),
       _S(0, 3, 0, 'lantern[hanging=true]'), _S(0, 5, 0, 'bell[attachment=floor,facing=north]')]
for x, z in ((-6, -6), (6, -6), (-6, 6), (6, 6)):
    _b += [_F(x, 1, z, x, 2, z, 'dark_oak_fence'), _S(x, 3, z, 'lantern')]
_b += [_F(-6, 1, -3, -6, 1, -2, 'spruce_stairs[facing=west]'), _F(6, 1, 2, 6, 1, 3, 'spruce_stairs[facing=east]'),
       _F(2, 1, -6, 3, 1, -6, 'spruce_stairs[facing=north]'), _F(-3, 1, 6, -2, 1, 6, 'spruce_stairs[facing=south]'),
       _S(-6, 1, 3, 'potted_red_tulip'), _S(6, 1, -3, 'potted_azure_bluet'), _S(-3, 1, -6, 'potted_fern'), _S(3, 1, 6, 'potted_cornflower')]

# ------------------------------------------------------------------ helpers for buildings
def _gable_x(x0, x1, z0, z1, y0, stairs, fill):
    """Roof with ridge along x over walls x0..x1 / z0..z1, first stair row at y0 one block outside."""
    out = []
    i = 0
    while z0 - 1 + i <= z1 + 1 - i:
        y = y0 + i
        za, zb = z0 - 1 + i, z1 + 1 - i
        out.append(_F(x0 - 1, y, za, x1 + 1, y, za, f'{stairs}[facing=south]'))
        if zb != za:
            out.append(_F(x0 - 1, y, zb, x1 + 1, y, zb, f'{stairs}[facing=north]'))
        if za + 1 <= zb - 1:
            out += [_F(x0, y, za + 1, x0, y, zb - 1, fill), _F(x1, y, za + 1, x1, y, zb - 1, fill)]
        i += 1
    return out


def _gable_z(x0, x1, z0, z1, y0, stairs, fill):
    """Roof with ridge along z."""
    out = []
    i = 0
    while x0 - 1 + i <= x1 + 1 - i:
        y = y0 + i
        xa, xb = x0 - 1 + i, x1 + 1 - i
        out.append(_F(xa, y, z0 - 1, xa, y, z1 + 1, f'{stairs}[facing=east]'))
        if xb != xa:
            out.append(_F(xb, y, z0 - 1, xb, y, z1 + 1, f'{stairs}[facing=west]'))
        if xa + 1 <= xb - 1:
            out += [_F(xa + 1, y, z0, xb - 1, y, z0, fill), _F(xa + 1, y, z1, xb - 1, y, z1, fill)]
        i += 1
    return out


def _door(x, z, facing, wood='spruce', hinge='left'):
    return [_S(x, 2, z, f'{wood}_door[facing={facing},half=upper,hinge={hinge},open=false]'),
            _S(x, 1, z, f'{wood}_door[facing={facing},half=lower,hinge={hinge},open=false]')]


def _door_at(x, y, z, facing, wood='spruce', hinge='left'):
    return [_S(x, y + 1, z, f'{wood}_door[facing={facing},half=upper,hinge={hinge},open=false]'),
            _S(x, y, z, f'{wood}_door[facing={facing},half=lower,hinge={hinge},open=false]')]


def _tree(x, z, h=5, r=2, log='oak_log', leaf=LEAF, top=1):
    out = [_F(x, 1, z, x, h, z, log)]
    for dy in range(h - 2, h + top + 1):
        rr = r if dy <= h else max(1, r - 1)
        for dz in range(-rr, rr + 1):
            w = int(math.floor(math.sqrt(rr * rr + rr - dz * dz)))
            out.append(_F(x - w, dy, z + dz, x + w, dy, z + dz, leaf + ' replace air'))
    _reserve(x - r, z - r, x + r, z + r)
    return out


def _bush(x, z, w=2, d=2, h=2, leaf=AZL):
    _reserve(x, z, x + w - 1, z + d - 1)
    out = [_F(x, 1, z, x + w - 1, h, z + d - 1, leaf)]
    if _rng.random() < 0.5:
        out.append(_S(x, h, z, 'air'))
    if _rng.random() < 0.6:
        out.append(_S(x + w - 1, h + 1, z + d - 1, FAZL))
    return out


# ------------------------------------------------------------------ NW: half-timbered house "Krummbalken" (cellar, 2 floors, attic)
x0, x1, z0, z1 = -22, -11, -22, -13
_reserve(x0 - 1, z0 - 1, x1 + 1, z1 + 2)
_b += [_F(x0, 0, z0, x1, 0, z1, 'cobblestone'), _F(x0 + 1, 0, z0 + 1, x1 - 1, 0, z1 - 1, 'spruce_planks'),
       _F(x0, 1, z0, x1, 8, z1, 'calcite'), _F(x0 + 1, 1, z0 + 1, x1 - 1, 8, z1 - 1, 'air')]
for x in (x0, -18, -15, x1):
    for z in (z0, z1):
        _b.append(_F(x, 1, z, x, 8, z, 'dark_oak_log'))
for z in (z0, -18, z1):
    for x in (x0, x1):
        _b.append(_F(x, 1, z, x, 8, z, 'dark_oak_log'))
for y in (5, 9):
    _b += [_F(x0, y, z0, x1, y, z0, 'dark_oak_log[axis=x]'), _F(x0, y, z1, x1, y, z1, 'dark_oak_log[axis=x]'),
           _F(x0, y, z0 + 1, x0, y, z1 - 1, 'dark_oak_log[axis=z]'), _F(x1, y, z0 + 1, x1, y, z1 - 1, 'dark_oak_log[axis=z]')]
# diagonal-ish braces on the upper floor
_b += [_S(-20, 7, z1, 'dark_oak_planks'), _S(-21, 6, z1, 'dark_oak_planks'), _S(-13, 7, z1, 'dark_oak_planks'), _S(-12, 6, z1, 'dark_oak_planks'),
       _S(-20, 7, z0, 'dark_oak_planks'), _S(-13, 7, z0, 'dark_oak_planks')]
_b += [_F(x0 + 1, 5, z0 + 1, x1 - 1, 5, z1 - 1, 'spruce_planks'), _F(x0 + 1, 9, z0 + 1, x1 - 1, 9, z1 - 1, 'spruce_planks')]
_b += _gable_x(x0, x1, z0, z1, 9, 'dark_oak_stairs', 'dark_oak_planks')
_b += [_F(x0, 11, -18, x0, 11, -17, 'glass_pane' + PZ), _F(x1, 11, -18, x1, 11, -17, 'glass_pane' + PZ)]
# windows (ground + upper floor)
for y in (2, 6):
    _b += [_F(-20, y, z1, -19, y + 1, z1, 'glass_pane' + PX), _F(-17, y, z0, -16, y + 1, z0, 'glass_pane' + PX),
           _F(-13, y, z0, -12, y + 1, z0, 'glass_pane' + PX), _F(x0, y, -16, x0, y + 1, -15, 'glass_pane' + PZ),
           _F(x1, y, -20, x1, y + 1, -20, 'glass_pane' + PZ), _F(x0, y, -21, x0, y + 1, -20, 'glass_pane' + PZ)]
_b += [_F(-17, 6, z1, -16, 7, z1, 'glass_pane' + PX), _F(x1, 6, -16, x1, 7, -15, 'glass_pane' + PZ)]
# front door (south) with porch, back door (east)
_b += _door(-14, z1, 'south') + [_S(-14, 0, z1 + 1, 'cobblestone'), _S(-14, 1, z1 + 1, 'air'),
                                  _F(-15, 3, z1 + 1, -13, 3, z1 + 1, 'dark_oak_slab[type=top]'), _S(-13, 1, z1 + 1, 'potted_red_tulip'),
                                  _S(-15, 1, z1 + 1, 'potted_dandelion')]
_b += _door(x1, -17, 'east', 'spruce', 'right')
# ground floor: wall between kitchen (west) and parlour (east)
_b += [_F(-17, 1, z0 + 1, -17, 4, z1 - 1, 'spruce_planks'), _F(-17, 1, -17, -17, 2, -16, 'air'), _S(-17, 3, -17, 'spruce_slab[type=top]'),
       _S(-17, 3, -16, 'spruce_slab[type=top]')]
# kitchen
_b += [_S(-21, 1, -21, 'water_cauldron[level=3]'), _S(-20, 1, -21, 'stonecutter[facing=south]'), _F(-19, 1, -21, -18, 1, -21, 'smooth_stone_slab[type=top]'),
       _S(-19, 2, -21, 'potted_white_tulip'), _F(-21, 1, -20, -21, 1, -19, 'smooth_stone_slab[type=top]'), _S(-21, 2, -19, 'cake'),
       _S(-19, 1, -17, 'dark_oak_fence'), _S(-19, 2, -17, 'white_carpet'), _S(-20, 1, -17, 'spruce_stairs[facing=west]'),
       _S(-18, 1, -17, 'spruce_stairs[facing=east]'), _S(-19, 4, -18, 'lantern[hanging=true]'),
       _F(-21, 1, -14, -20, 1, -14, 'hay_block'), _S(-21, 2, -14, 'hay_block'), _S(-18, 1, -14, 'cauldron')]
# parlour with bookshelves, sofa, fireplace, ladder up
_b += [_F(-16, 1, -21, -14, 2, -21, 'bookshelf'), _F(-16, 3, -21, -14, 3, -21, 'spruce_slab[type=bottom]'),
       _F(-16, 1, -14, -14, 1, -14, 'spruce_stairs[facing=north]'), _F(-15, 1, -19, -13, 1, -16, 'red_carpet'),
       _F(-12, 1, -19, -12, 4, -18, 'bricks'), _S(-12, 1, -19, 'iron_bars' + PZ), _S(-12, 2, -18, 'lantern'),
       _S(-14, 4, -17, 'lantern[hanging=true]'), _S(-13, 1, -14, 'potted_bamboo'), _S(-16, 1, -17, 'potted_oak_sapling')]
_b += [_F(-12, 1, -21, -12, 5, -21, 'ladder[facing=west]')]
# upper floor: bedroom (west) and study with a secret closet (east)
_b += [_F(-16, 6, z0 + 1, -16, 8, z1 - 1, 'spruce_planks'), _F(-16, 6, -18, -16, 7, -18, 'air')]
_b += [_S(-21, 6, -20, 'red_bed[facing=west,part=head]'), _S(-20, 6, -20, 'red_bed[facing=west,part=foot]'),
       _S(-21, 6, -16, 'blue_bed[facing=west,part=head]'), _S(-20, 6, -16, 'blue_bed[facing=west,part=foot]'),
       _F(-19, 6, -21, -17, 8, -21, 'dark_oak_planks'), _F(-19, 6, -20, -17, 7, -20, 'air'),   # walk-in wardrobe
       _S(-18, 6, -19, 'spruce_trapdoor[facing=south,half=bottom,open=true]'),
       _F(-20, 6, -14, -17, 6, -14, 'white_carpet'), _S(-21, 6, -14, 'potted_allium'), _S(-19, 8, -17, 'lantern[hanging=true]')]
_b += [_F(-21, 6, -18, -21, 9, -18, 'ladder[facing=east]')]
_b += [_F(-15, 6, -21, -13, 8, -21, 'bookshelf'), _S(-15, 6, -19, 'dark_oak_fence'), _S(-15, 7, -19, 'brown_carpet'),
       _S(-14, 6, -19, 'spruce_stairs[facing=west]'), _S(-13, 8, -18, 'lantern[hanging=true]'),
       _F(-13, 6, -16, -13, 8, -14, 'spruce_planks')]
_b += _door_at(-13, 6, -15, 'east', 'dark_oak')
_b += [_S(-12, 8, -16, 'cobweb')]
# attic: hay, crates, cobwebs
_b += [_F(-20, 10, -19, -19, 10, -16, 'hay_block'), _S(-19, 11, -18, 'hay_block'), _F(-14, 10, -19, -13, 11, -19, 'stripped_spruce_wood'),
       _S(-13, 10, -16, 'stripped_spruce_wood'), _S(-15, 12, -17, 'lantern[hanging=true]'), _S(-12, 10, -15, 'cobweb'),
       _S(-17, 10, -15, 'white_wool'), _S(-17, 10, -20, 'potted_dead_bush')]
# cellar under the kitchen (trapdoor + ladder), secret tunnel to the well
_b += [_F(-22, -5, -22, -17, -1, -14, 'stone_bricks'), _F(-21, -4, -21, -18, -1, -15, 'air'), _F(-21, -5, -21, -18, -5, -15, 'spruce_planks'),
       _F(-21, -4, -15, -21, -1, -15, 'ladder[facing=east]'), _S(-21, 0, -15, 'spruce_trapdoor[facing=north,half=top,open=false]'),
       _F(-18, -4, -21, -18, -3, -20, 'hay_block'), _S(-21, -4, -21, 'cobweb'), _S(-19, -1, -18, 'lantern[hanging=true]'),
       _S(-20, -4, -21, 'mossy_cobblestone_wall'), _S(-20, -3, -21, 'candle[lit=true,candles=3]')]
for _ in range(10):
    _b.append(_S(_rng.choice((-22, -17)), _rng.randint(-4, -1), _rng.randint(-21, -15), _rng.choice(['mossy_stone_bricks', 'cracked_stone_bricks'])))
_b += [_F(-17, -4, -19, -8, -3, -19, 'air'), _F(-8, -4, -19, -8, -3, -12, 'air'), _F(-8, -4, -12, -5, -3, -12, 'air'),
       _F(-17, -5, -19, -8, -5, -19, 'gravel'), _F(-8, -5, -19, -8, -5, -12, 'gravel'), _F(-8, -5, -12, -4, -5, -12, 'gravel'),
       _F(-16, -2, -19, -9, -2, -19, 'spruce_planks'), _F(-8, -2, -19, -8, -2, -13, 'spruce_planks'),
       _S(-12, -3, -20, 'glow_lichen[south=true]'), _S(-7, -3, -15, 'glow_lichen[west=true]')]
# well (shaft with ladder down to the tunnel)
_reserve(-6, -14, -2, -10)
_b += [_F(-5, 0, -13, -3, 1, -11, 'cobblestone'), _F(-4, -4, -12, -4, 1, -12, 'air'), _F(-4, -4, -12, -4, 1, -12, 'ladder[facing=south]'),
       _S(-5, 1, -13, 'mossy_cobblestone'), _S(-3, 1, -11, 'mossy_cobblestone')]
for x, z in ((-5, -13), (-3, -13), (-5, -11), (-3, -11)):
    _b.append(_F(x, 2, z, x, 3, z, 'spruce_fence'))
_b += [_F(-5, 4, -13, -3, 4, -11, 'spruce_slab[type=bottom]'), _F(-4, 2, -12, -4, 3, -12, 'air')]

# ------------------------------------------------------------------ NE: barn with hay loft
x0, x1, z0, z1 = 10, 23, -23, -12
_reserve(x0 - 1, z0 - 1, x1 + 1, z1 + 3)
_b += [_F(x0, 0, z0, x1, 0, z1, 'stripped_spruce_wood'), _F(x0 + 1, 0, z0 + 1, x1 - 1, 0, z1 - 1, 'coarse_dirt'),
       _F(x0, 1, z0, x1, 6, z1, 'spruce_planks'), _F(x0 + 1, 1, z0 + 1, x1 - 1, 6, z1 - 1, 'air')]
for x in (x0, 14, 19, x1):
    for z in (z0, z1):
        _b.append(_F(x, 1, z, x, 6, z, 'stripped_dark_oak_log'))
for z in (z0, -17, z1):
    for x in (x0, x1):
        _b.append(_F(x, 1, z, x, 6, z, 'stripped_dark_oak_log'))
_b += [_F(x0, 6, z0, x1, 6, z0, 'stripped_dark_oak_log[axis=x]'), _F(x0, 6, z1, x1, 6, z1, 'stripped_dark_oak_log[axis=x]'),
       _F(x0, 6, z0, x0, 6, z1, 'stripped_dark_oak_log[axis=z]'), _F(x1, 6, z0, x1, 6, z1, 'stripped_dark_oak_log[axis=z]')]
_b += _gable_z(x0, x1, z0, z1, 7, 'spruce_stairs', 'dark_oak_planks')
for z in range(z0 + 2, z1 - 1, 3):     # roof beams inside
    _b.append(_F(x0 + 1, 7, z, x1 - 1, 7, z, 'stripped_spruce_log[axis=x]'))
_b += [_F(16, 9, z0, 17, 10, z0, 'glass_pane' + PX), _S(16, 12, z1, 'glass_pane' + PX), _S(17, 12, z1, 'glass_pane' + PX)]
# big barn door (south), side door (west), small windows
_b += [_F(15, 1, z1, 18, 4, z1, 'air'), _F(15, 5, z1, 18, 5, z1, 'stripped_dark_oak_log[axis=x]'),
       _F(14, 0, z1 + 1, 19, 0, z1 + 2, 'coarse_dirt'), _F(x0, 1, -15, x0, 2, -15, 'air'),
       _F(x1, 3, -21, x1, 4, -20, 'glass_pane' + PZ), _F(x1, 3, -15, x1, 4, -14, 'glass_pane' + PZ), _F(x0, 3, -21, x0, 4, -20, 'glass_pane' + PZ),
       _S(14, 1, z1 + 1, 'hay_block'), _S(13, 1, z1 + 1, 'hay_block'), _S(13, 2, z1 + 1, 'hay_block[axis=x]'), _S(20, 1, z1 + 1, 'potted_dead_bush')]
# loft over the north half, ladder at the east wall
_b += [_F(x0 + 1, 5, z0 + 1, x1 - 1, 5, -18, 'spruce_planks'), _F(x0 + 1, 5, -17, x1 - 1, 5, -17, 'spruce_slab[type=top]'),
       _F(x1 - 1, 1, -16, x1 - 1, 6, -16, 'ladder[facing=west]'),
       _F(12, 4, -17, 12, 4, -17, 'lantern[hanging=true]'), _S(20, 4, -17, 'lantern[hanging=true]'), _S(16, 11, -17, 'lantern[hanging=true]')]
# hay stacks and stalls on the ground floor
_b += [_F(11, 1, -22, 13, 3, -20, 'hay_block'), _F(11, 1, -19, 12, 1, -18, 'hay_block'), _S(11, 2, -19, 'hay_block'),
       _F(18, 1, -22, 22, 2, -21, 'hay_block'), _F(16, 1, -22, 16, 1, -21, 'hay_block'), _S(13, 1, -16, 'hay_block'),
       _F(20, 1, -16, 20, 1, -13, 'spruce_fence'), _S(20, 1, -15, 'spruce_fence_gate[facing=east]'),
       _F(21, 1, -14, 22, 1, -13, 'hay_block'), _S(22, 1, -15, 'water_cauldron[level=2]'), _S(11, 1, -13, 'grindstone[face=floor,facing=north]'),
       _S(11, 1, -14, 'anvil[facing=east]'), _S(12, 1, -13, 'stripped_spruce_wood')]
# loft: hay maze
_b += [_F(11, 6, -22, 13, 7, -21, 'hay_block'), _F(15, 6, -22, 16, 6, -19, 'hay_block'), _S(15, 7, -22, 'hay_block'),
       _F(18, 6, -20, 20, 7, -20, 'hay_block'), _F(21, 6, -22, 22, 6, -22, 'hay_block'), _S(11, 6, -19, 'stripped_spruce_wood'),
       _S(13, 6, -18, 'white_wool'), _S(19, 6, -22, 'cobweb')]

# ------------------------------------------------------------------ SW: chapel ruin with tower and crypt
x0, x1, z0, z1 = -21, -11, 11, 24
_reserve(-26, 8, x1 + 1, 25)
_b += [_F(x0, 0, z0, x1, 0, z1, 'stone_bricks'), _F(x0, 1, z0, x1, 6, z1, 'stone_bricks'), _F(x0 + 1, 1, z0 + 1, x1 - 1, 6, z1 - 1, 'air')]
for _ in range(110):    # weathering
    side = _rng.randint(0, 3)
    t = _rng.randint(0, 13)
    y = _rng.randint(0, 6)
    x, z = [(x0 + min(t, 10), z0), (x0 + min(t, 10), z1), (x0, z0 + t), (x1, z0 + t)][side]
    _b.append(_S(x, y, z, _rng.choice(['mossy_stone_bricks', 'mossy_stone_bricks', 'cracked_stone_bricks', 'cobblestone', 'mossy_cobblestone'])))
for _ in range(45):
    _b.append(_S(_rng.randint(x0 + 1, x1 - 1), 0, _rng.randint(z0 + 1, z1 - 1), _rng.choice(['mossy_stone_bricks', 'cracked_stone_bricks', 'moss_block', 'grass_block', 'cobblestone'])))
# broken wall tops
for (ax, az, bx, bz, h) in ((-21, 15, -21, 19, 4), (-19, 24, -15, 24, 3), (-11, 13, -11, 16, 5), (-11, 20, -11, 22, 3), (-16, 11, -13, 11, 5),
                            (-21, 22, -21, 24, 5), (-12, 24, -11, 24, 2)):
    _b.append(_F(ax, h, az, bx, 6, bz, 'air'))
# gothic windows and the entrance arch (north), side opening (east)
for z in (14, 18, 22):
    _b += [_F(x0, 2, z, x0, 4, z, 'air'), _F(x1, 2, z, x1, 4, z, 'air')]
_b += [_F(-18, 1, z0, -16, 3, z0, 'air'), _S(-17, 4, z0, 'air'), _S(-18, 4, z0, 'stone_brick_stairs[facing=east,half=top]'),
       _S(-16, 4, z0, 'stone_brick_stairs[facing=west,half=top]'), _F(x1, 1, 18, x1, 2, 18, 'air')]
# pews, aisle, altar
_b += [_F(-17, 0, 12, -17, 0, 21, 'mossy_cobblestone')]
for z in (14, 16, 18):
    _b += [_F(-20, 1, z, -18, 1, z, 'spruce_stairs[facing=north]'), _F(-16, 1, z, -13, 1, z, 'spruce_stairs[facing=north]')]
_b += [_S(-15, 1, 16, 'air'), _S(-19, 1, 18, 'mossy_cobblestone_wall'),
       _F(-19, 1, 22, -13, 1, 23, 'stone_brick_slab[type=bottom]'), _F(-18, 2, 23, -16, 2, 23, 'chiseled_stone_bricks'),
       _S(-17, 3, 23, 'candle[lit=true,candles=4]'), _S(-18, 3, 23, 'candle[lit=true,candles=2]'), _S(-16, 3, 23, 'potted_wither_rose'),
       _F(-14, 2, 22, -14, 4, 22, 'stone_brick_wall'), _S(-14, 5, 22, 'lantern')]
# overgrowth: leaves on the walls, a birch growing in the nave, moss
_b += [_F(-21, 4, 12, -21, 4, 14, LEAF), _F(-14, 5, 11, -12, 5, 11, AZL), _F(-11, 3, 20, -11, 3, 23, LEAF), _F(-20, 3, 24, -19, 3, 24, FAZL),
       _F(-12, 6, 17, -11, 6, 19, LEAF)]
_b += _tree(-13, 13, 6, 2, 'birch_log', 'birch_leaves[persistent=true]')
for _ in range(25):
    x, z = _rng.randint(x0 + 1, x1 - 1), _rng.randint(z0 + 1, z1 - 2)
    blk = _rng.choice(['moss_carpet', 'moss_carpet', 'short_grass', 'fern'])
    if (x, z) == (-17, 17):      # crypt trapdoor
        continue
    if blk != 'moss_carpet':     # grass and ferns need soil
        _b.append(_S(x, 0, z, 'moss_block'))
    _b.append(_F(x, 1, z, x, 1, z, blk + ' replace air'))
# bell tower (west of the nave), ladder to a lookout
tx0, tx1, tz0, tz1 = -25, -21, 9, 13
_b += [_F(tx0, 0, tz0, tx1, 12, tz1, 'stone_bricks'), _F(tx0 + 1, 1, tz0 + 1, tx1 - 1, 12, tz1 - 1, 'air'),
       _F(tx0 + 1, 0, tz0 + 1, tx1 - 1, 0, tz1 - 1, 'cobblestone'),
       _F(tx0 + 1, 1, tz0 + 2, tx0 + 1, 11, tz0 + 2, 'ladder[facing=east]'), _F(tx0 + 1, 11, tz0 + 1, tx1 - 1, 11, tz1 - 1, 'spruce_planks'),
       _S(tx0 + 1, 11, tz0 + 2, 'ladder[facing=east]'), _F(tx1, 1, 12, tx1, 2, 12, 'air'), _F(tx0 + 2, 6, tz0, tx0 + 2, 7, tz0, 'air'),
       _F(tx0 + 2, 6, tz1, tx0 + 2, 7, tz1, 'air'), _F(tx0, 6, tz0 + 3, tx0, 7, tz0 + 3, 'air'),
       _S(tx0 + 2, 10, tz0 + 2, 'lantern[hanging=true]'), _S(tx0 + 3, 1, tz0 + 3, 'cobweb')]
for x in range(tx0, tx1 + 1, 2):
    _b += [_S(x, 13, tz0, 'stone_brick_wall'), _S(x, 13, tz1, 'stone_brick_wall')]
for z in range(tz0, tz1 + 1, 2):
    _b += [_S(tx0, 13, z, 'stone_brick_wall'), _S(tx1, 13, z, 'stone_brick_wall')]
_b += [_F(tx0, 12, tz0 + 1, tx0, 12, tz1 - 1, 'mossy_stone_bricks'), _S(tx1, 11, tz0, 'mossy_stone_bricks'), _F(tx0, 9, tz1, tx0, 12, tz1, 'mossy_cobblestone')]
# crypt below the altar (trapdoor in front of the altar)
_b += [_F(-21, -5, 16, -12, -1, 24, 'stone_bricks'), _F(-20, -4, 17, -13, -2, 23, 'air'), _F(-17, -4, 17, -17, -1, 17, 'air'),
       _F(-17, -4, 17, -17, -1, 17, 'ladder[facing=south]'), _S(-17, 0, 17, 'spruce_trapdoor[facing=north,half=top,open=false]'),
       _F(-20, -4, 19, -19, -4, 20, 'smooth_stone_slab[type=bottom]'), _F(-20, -4, 22, -19, -4, 23, 'smooth_stone_slab[type=bottom]'),
       _F(-14, -4, 19, -13, -4, 20, 'smooth_stone_slab[type=bottom]'), _S(-17, -4, 23, 'skeleton_skull[rotation=8]'),
       _S(-16, -2, 20, 'soul_lantern[hanging=true]'), _S(-20, -3, 17, 'cobweb'), _S(-13, -4, 23, 'candle[lit=true,candles=2]'),
       _F(-15, -4, 17, -14, -3, 17, 'cobweb')]

# ------------------------------------------------------------------ SE: market stalls, greenhouse, pond, scarecrow
_reserve(8, 8, 26, 26)
for i, (sx, wool) in enumerate(((9, 'red'), (14, 'yellow'), (19, 'blue'))):
    _b += [_F(sx, 0, 9, sx + 3, 0, 12, 'spruce_planks')]
    for x, z in ((sx, 9), (sx + 3, 9), (sx, 12), (sx + 3, 12)):
        _b.append(_F(x, 1, z, x, 3, z, 'spruce_fence'))
    for x in range(sx, sx + 4):
        _b.append(_F(x, 4, 9, x, 4, 12, f'{wool if (x - sx) % 2 == 0 else "white"}_wool'))
    _b += [_F(sx - 1, 4, 8, sx + 4, 4, 8, f'{wool}_wool'), _F(sx + 1, 1, 9, sx + 2, 1, 9, 'spruce_slab[type=top]'),
           _F(sx + 1, 1, 12, sx + 2, 2, 12, ['stripped_oak_wood', 'bamboo_block', 'oak_planks'][i]), _S(sx + 1, 1, 11, 'hay_block')]
_b += [_S(10, 2, 9, 'melon'), _S(11, 2, 9, 'carved_pumpkin[facing=north]'), _S(15, 2, 9, 'cake'), _S(16, 2, 9, 'potted_red_mushroom'),
       _S(20, 2, 9, 'potted_cactus'), _S(21, 2, 9, 'pumpkin')]
# crate stacks between market and greenhouse
for (x, z, h, blk) in ((9, 14, 2, 'stripped_oak_wood'), (10, 14, 1, 'oak_planks'), (12, 15, 2, 'stripped_spruce_wood'), (13, 15, 1, 'hay_block'),
                       (23, 14, 2, 'stripped_oak_wood'), (24, 14, 1, 'oak_planks'), (24, 15, 2, 'hay_block'), (14, 25, 2, 'stripped_spruce_wood'),
                       (15, 25, 1, 'oak_planks'), (25, 20, 2, 'stripped_oak_wood')):
    _b.append(_F(x, 1, z, x, h, z, blk))
# greenhouse
gx0, gx1, gz0, gz1 = 17, 25, 16, 24
_b += [_F(gx0, 0, gz0, gx1, 0, gz1, 'mossy_cobblestone'), _F(gx0, 1, gz0, gx1, 4, gz1, 'glass'), _F(gx0 + 1, 1, gz0 + 1, gx1 - 1, 4, gz1 - 1, 'air'),
       _F(gx0, 5, gz0, gx1, 5, gz1, 'glass'), _F(gx0 + 2, 6, gz0 + 2, gx1 - 2, 6, gz1 - 2, 'glass')]
for x, z in ((gx0, gz0), (gx1, gz0), (gx0, gz1), (gx1, gz1)):
    _b.append(_F(x, 1, z, x, 5, z, 'birch_log'))
_b += [_F(gx0, 5, gz0, gx1, 5, gz0, 'birch_log[axis=x]'), _F(gx0, 5, gz1, gx1, 5, gz1, 'birch_log[axis=x]'),
       _F(gx0, 5, gz0, gx0, 5, gz1, 'birch_log[axis=z]'), _F(gx1, 5, gz0, gx1, 5, gz1, 'birch_log[axis=z]')]
_b += [_F(gx0, 1, 20, gx0, 2, 20, 'air'), _F(gx0 + 1, 0, gz0 + 1, gx1 - 1, 0, gz1 - 1, 'moss_block'), _F(gx0 + 1, 0, 20, gx1 - 1, 0, 20, 'gravel'),
       _F(gx0 + 1, 1, gz0 + 1, gx1 - 1, 2, gz0 + 1, AZL), _F(gx0 + 1, 1, gz1 - 1, gx1 - 1, 2, gz1 - 1, FAZL),
       _F(gx0 + 2, 1, 18, gx1 - 2, 1, 18, 'oak_leaves[persistent=true]'), _F(gx0 + 2, 1, 22, gx1 - 2, 1, 22, AZL),
       _S(19, 1, 18, 'moss_block'), _S(22, 1, 18, 'moss_block'), _S(20, 1, 22, 'moss_block'),
       _S(19, 2, 18, 'flowering_azalea'), _S(22, 2, 18, 'azalea'), _S(20, 2, 22, 'flowering_azalea'), _S(23, 2, 22, 'potted_fern'),
       _S(20, 1, 18, 'air'), _S(gx1 - 2, 1, 22, 'air'), _S(gx1 - 1, 1, 20, 'water_cauldron[level=3]'), _S(21, 4, 20, 'lantern[hanging=true]'),
       _F(22, 1, gz0 + 1, 23, 2, gz0 + 1, 'air')]
# pond with jetty
_b += [_F(9, -2, 17, 14, 0, 23, 'clay'), _F(10, -1, 18, 13, 0, 22, 'water'), _F(11, -2, 19, 12, -2, 21, 'water'),
       _F(9, 0, 17, 14, 0, 17, 'sand'), _S(9, 0, 23, 'sand'), _S(14, 0, 23, 'sand'), _F(9, 0, 18, 9, 0, 22, 'mud'),
       _F(14, 0, 18, 14, 0, 22, 'spruce_planks'), _F(15, 0, 19, 16, 0, 21, 'spruce_planks'),
       _S(14, 1, 18, 'spruce_fence'), _S(14, 1, 22, 'spruce_fence'), _S(14, 2, 18, 'lantern'),
       _S(11, 1, 19, 'lily_pad'), _S(12, 1, 22, 'lily_pad'), _S(10, 1, 21, 'lily_pad'), _S(12, -2, 20, 'seagrass'), _S(11, -2, 21, 'seagrass'),
       _S(9, 1, 20, 'sugar_cane'), _S(9, 2, 20, 'sugar_cane'), _S(9, 1, 22, 'sugar_cane')]
# scarecrow
_b += [_S(11, 1, 25, 'spruce_fence'), _S(11, 2, 25, 'hay_block'), _S(11, 3, 25, 'carved_pumpkin[facing=north]'),
       _S(10, 2, 25, 'spruce_fence'), _S(12, 2, 25, 'spruce_fence')]
_b += [_F(9, 0, 24, 13, 0, 25, 'farmland[moisture=7]'), _S(11, 0, 25, 'coarse_dirt'), _F(9, 1, 24, 13, 1, 24, 'wheat[age=7]' + ' replace air')]

# ------------------------------------------------------------------ east: woodshed and apple tree; west: garden, fallen log, haystacks
_reserve(17, -7, 25, -2)
_b += [_F(17, 0, -7, 25, 0, -3, 'coarse_dirt')]
for x, z in ((17, -7), (25, -7), (17, -3), (25, -3)):
    _b.append(_F(x, 1, z, x, 3, z, 'spruce_log'))
_b += [_F(16, 4, -8, 26, 4, -2, 'spruce_slab[type=bottom]'), _F(18, 1, -7, 24, 2, -7, 'oak_log[axis=x]'), _F(19, 3, -7, 23, 3, -7, 'oak_log[axis=x]'),
       _F(18, 1, -5, 20, 2, -5, 'birch_log[axis=x]'), _F(22, 1, -5, 24, 1, -5, 'spruce_log[axis=x]'), _F(22, 2, -5, 23, 2, -5, 'spruce_log[axis=x]'),
       _S(25, 1, -5, 'spruce_log'), _S(21, 3, -3, 'lantern[hanging=true]'), _S(18, 1, -3, 'chipped_anvil[facing=east]')]
_b += _tree(12, 5, 5, 2, 'oak_log', LEAF)
# little cart
_reserve(20, 3, 24, 6)
_b += [_F(21, 1, 4, 23, 1, 5, 'spruce_slab[type=top]'), _S(20, 1, 4, 'spruce_fence'), _S(21, 2, 4, 'hay_block'), _S(22, 2, 5, 'pumpkin'),
       _S(23, 2, 4, 'hay_block')]
# west: vegetable garden with fence, fallen log, hay stacks
_reserve(-25, 3, -15, 7)
_b += [_F(-24, 0, 4, -16, 0, 6, 'farmland[moisture=7]'), _F(-24, 0, 5, -16, 0, 5, 'water'), _F(-24, 1, 4, -16, 1, 4, 'carrots[age=7]'),
       _F(-24, 1, 6, -16, 1, 6, 'potatoes[age=7]'), _F(-24, 1, 5, -16, 1, 5, 'lily_pad'),
       _F(-25, 1, 3, -15, 1, 3, 'oak_fence'), _F(-25, 1, 7, -15, 1, 7, 'oak_fence'), _F(-25, 1, 4, -25, 1, 6, 'oak_fence'),
       _F(-15, 1, 4, -15, 1, 6, 'oak_fence'), _S(-20, 1, 3, 'oak_fence_gate[facing=north]')]
_reserve(-24, -6, -14, -3)
_b += [_F(-23, 1, -5, -15, 1, -5, 'oak_log[axis=x]'), _F(-21, 1, -6, -19, 1, -6, 'moss_carpet'), _F(-18, 2, -5, -16, 2, -5, 'moss_carpet'),
       _S(-14, 1, -5, 'brown_mushroom'), _S(-23, 2, -5, 'red_mushroom')]
_b += [_F(-12, 1, -6, -10, 2, -5, 'hay_block'), _S(-11, 3, -6, 'hay_block'), _F(-12, 1, 4, -11, 1, 5, 'hay_block'), _S(-12, 2, 4, 'hay_block')]
_reserve(-13, -7, -9, -4)
_reserve(-13, 3, -10, 6)
# tree house in a huge dark oak (south), ladder up the trunk, hut on the platform
_reserve(-10, 13, -2, 22)
_DOL = 'dark_oak_leaves[persistent=true]'
_b += [_F(-6, 1, 17, -5, 10, 18, 'dark_oak_log'), _F(-9, 6, 14, -2, 6, 21, 'spruce_planks'), _F(-6, 6, 17, -5, 6, 18, 'dark_oak_log'),
       _F(-9, 7, 14, -2, 7, 14, 'spruce_fence'), _F(-9, 7, 21, -2, 7, 21, 'spruce_fence'), _F(-9, 7, 15, -9, 7, 20, 'spruce_fence'),
       _F(-2, 7, 15, -2, 7, 20, 'spruce_fence'), _S(-5, 7, 21, 'air'),
       _F(-5, 1, 19, -5, 7, 19, 'ladder[facing=south]'), _S(-5, 6, 19, 'ladder[facing=south]'),
       _F(-4, 7, 15, -2, 9, 17, 'stripped_spruce_wood'), _F(-3, 7, 16, -3, 8, 16, 'air'), _F(-4, 7, 16, -4, 8, 16, 'air'),
       _F(-5, 10, 14, -1, 10, 18, 'spruce_slab[type=bottom]'), _S(-3, 7, 17, 'air'), _S(-3, 8, 17, 'air'),
       _S(-9, 8, 21, 'lantern'), _S(-2, 8, 14, 'lantern'),
       _F(-7, 3, 16, -4, 3, 16, 'dark_oak_log[axis=x]'), _F(-7, 4, 15, -7, 5, 15, 'dark_oak_log')]
for dy, rr in ((9, 3), (10, 4), (11, 4), (12, 3), (13, 2)):
    for dz in range(-rr, rr + 1):
        w = int(math.floor(math.sqrt(rr * rr + rr - dz * dz)))
        _b.append(_F(-6 - w, dy, 17 + dz, -5 + w, dy, 17 + dz, _DOL + ' replace air'))
_b += [_F(-10, 7, 13, -8, 8, 15, _DOL + ' replace air'), _F(-3, 5, 20, -1, 5, 22, _DOL + ' replace air')]
# little shed east of the square (open to the path)
_reserve(8, -8, 14, -3)
_b += [_F(9, 0, -7, 13, 0, -4, 'spruce_planks'), _F(9, 1, -7, 13, 3, -7, 'oak_planks'), _F(9, 1, -6, 9, 3, -4, 'oak_planks'),
       _F(13, 1, -6, 13, 3, -4, 'oak_planks'), _F(8, 4, -8, 14, 4, -3, 'spruce_slab[type=bottom]'),
       _S(9, 1, -7, 'spruce_log'), _S(13, 1, -7, 'spruce_log'), _F(9, 1, -4, 9, 3, -4, 'spruce_log'), _F(13, 1, -4, 13, 3, -4, 'spruce_log'),
       _S(11, 2, -7, 'glass_pane' + PX), _F(10, 1, -6, 11, 2, -6, 'hay_block'), _S(12, 1, -6, 'stripped_oak_wood'), _S(12, 1, -5, 'loom[facing=west]'),
       _S(11, 3, -5, 'lantern[hanging=true]')]
# trees and bushes around the village
for (x, z, h, r, log, leaf) in ((6, -18, 6, 2, 'oak_log', LEAF),
                                 (-20, -2, 5, 2, 'spruce_log', 'spruce_leaves[persistent=true]'), (23, 1, 4, 1, 'birch_log', 'birch_leaves[persistent=true]'),
                                 (5, 24, 4, 2, 'oak_log', AZL), (-24, -25, 4, 1, 'oak_log', LEAF), (24, -25, 4, 1, 'oak_log', LEAF)):
    _b += _tree(x, z, h, r, log, leaf)
for (x, z) in ((-8, -22), (5, -10), (8, -25), (-4, 23), (4, 14), (-10, 10), (-7, 13), (15, -4), (14, 2),
               (-10, -10), (24, -10), (-25, -9), (3, -25), (-3, -24), (7, 4), (-8, 3), (16, 6)):
    if _free(x, z) and _free(x + 1, z + 1):
        _b += _bush(x, z, 2, 2, _rng.choice((1, 2, 2)), _rng.choice((AZL, LEAF, AZL)))
# random ground cover on free cells
_COVER = ['short_grass'] * 8 + ['fern'] * 3 + ['poppy', 'dandelion', 'cornflower', 'oxeye_daisy', 'azure_bluet', 'lily_of_the_valley', 'allium',
                                                'bush', 'firefly_bush', 'leaf_litter', 'wildflowers', 'wildflowers']
for _ in range(420):
    x, z = _rng.randint(-26, 26), _rng.randint(-26, 26)
    if _free(x, z) and _gnd.get((x, z)) != 'gravel':
        _b.append(_F(x, 1, z, x, 1, z, _rng.choice(_COVER) + ' replace air'))
for _ in range(60):
    x, z = _rng.randint(-26, 26), _rng.randint(-26, 26)
    if _free(x, z):
        _b.append(_S(x, 0, z, _rng.choice(['moss_block', 'coarse_dirt', 'podzol', 'rooted_dirt'])))
for x, z in ((-9, -2), (9, 2), (-2, -9), (2, 9), (-18, 2), (18, -2), (-2, -20), (2, 20)):   # lamp posts along the paths
    _b += [_F(x, 1, z, x, 2, z, 'spruce_fence'), _S(x, 3, z, 'lantern')]
# sign over the square and spawn markers for the hiders
_b.append(holo('mg_versteckenh', c5(VX), VY + 6.2, c5(VZ), [{'text': 'Moosgrund', 'color': 'dark_green', 'bold': True}], 1.4))
_SPAWNS = [(0, -5), (0, 5), (-5, 0), (5, 0), (-4, -4), (4, -4), (-4, 4), (4, 4), (-5, 3), (5, -3), (3, 5), (-3, -5), (-5, -2), (5, 2), (-2, 5), (2, -5)]
for sx, sz in _SPAWNS:
    _b.append(f'{OW} summon minecraft:marker {c5(VX + sx)} {VY + 1} {c5(VZ + sz)} {{Tags:["mg_verstecken_sp"]}}')
_b.append(f'{OW} kill @e[type=minecraft:item,{_AREA}]')

# ------------------------------------------------------------------ items
_HIDEC = 'minecraft:tooltip_display={hidden_components:["minecraft:enchantments","minecraft:unbreakable","minecraft:attribute_modifiers","minecraft:dyed_color"]}'
TAUNT = ('minecraft:carrot_on_a_stick[minecraft:item_model="minecraft:goat_horn",minecraft:custom_name=' + tc(_txt('Taunt – Spotten', 'light_purple', bold=True)) +
         ',minecraft:lore=[' + tc(_txt('Rechtsklick: Macht ein Geräusch bei dir.', 'gray')) + ',' + tc(_txt('Mutig? +1 Münze pro Taunt!', 'gold')) + ']'
         ',minecraft:enchantment_glint_override=true'
         ',minecraft:unbreakable={},minecraft:custom_data={mg_verstecken:"taunt"},' + _HIDEC + ']')
STICK = ('minecraft:stick[minecraft:item_model="minecraft:blaze_rod",minecraft:custom_name=' + tc(_txt('Fangstab', 'red', bold=True)) +
         ',minecraft:lore=[' + tc(_txt('Schlag einen Versteckten – dann sucht er mit.', 'gray')) + ']'
         ',minecraft:attribute_modifiers=[{type:"minecraft:attack_damage",amount:3,id:"mg:verstecken_stick",operation:"add_value",slot:"mainhand"}]'
         ',minecraft:enchantment_glint_override=true,minecraft:custom_data={mg_verstecken:"stick"},' + _HIDEC + ']')


def _armor(piece):
    return (f'minecraft:leather_{piece}[minecraft:dyed_color=13382451,minecraft:unbreakable={{}},'
            'minecraft:enchantments={"minecraft:binding_curse":1},minecraft:custom_data={mg_verstecken:"armor"},' + _HIDEC + ']')


# ------------------------------------------------------------------ functions
_ROLE_TAGS = (_HID, _SEE, _ORIG, _FD, _NEW)
ENTER_LINES.extend([f'tag @s remove {t}' for t in _ROLE_TAGS])
EXTRA_LOAD.extend([
    'scoreboard objectives add mg_verstecken_dt minecraft.custom:minecraft.damage_taken',
    'scoreboard objectives add mg_verstecken_dd minecraft.custom:minecraft.damage_dealt',
    'scoreboard objectives add mg_verstecken_use minecraft.used:minecraft.carrot_on_a_stick',
    'scoreboard objectives add mg_verstecken_f dummy', 'scoreboard objectives add mg_verstecken_ab dummy', 'scoreboard objectives add mg_verstecken_cd dummy', 'scoreboard objectives add mg_verstecken_tn dummy',
    'team add mg_verstecken_hid', 'team modify mg_verstecken_hid nametagVisibility never', 'team modify mg_verstecken_hid friendlyFire false',
    'team modify mg_verstecken_hid color green', 'team modify mg_verstecken_hid deathMessageVisibility never', 'team modify mg_verstecken_hid collisionRule never',
    'team add mg_verstecken_see', 'team modify mg_verstecken_see nametagVisibility always', 'team modify mg_verstecken_see friendlyFire false',
    'team modify mg_verstecken_see color red', 'team modify mg_verstecken_see deathMessageVisibility never',
    f'team modify mg_verstecken_see prefix {tc({"text": "[Sucher] ", "color": "red"})}',
    f'bossbar add {NS}:verstecken {tc({"text": "Verstecken"})}', f'bossbar set {NS}:verstecken style notched_10',
    'scoreboard players set #verstecken_end mg %d' % _END, 'scoreboard players set #verstecken_head mg %d' % _HEAD,
    'scoreboard players set #verstecken_60 mg 60', 'scoreboard players set #verstecken_300 mg 300',
])


def _title(sel, t, tcol, sub, scol='gray'):
    return [f'title {sel} times 5 50 15', f'title {sel} subtitle {tc({"text": sub, "color": scol})}',
            f'title {sel} title {tc({"text": t, "color": tcol, "bold": True})}']


fn(f'{_K}/spawn_one', ['tp @s @e[type=minecraft:marker,tag=mg_verstecken_sp,tag=!mg_verstecken_used,sort=random,limit=1]',
                       'execute at @s run tag @e[type=minecraft:marker,tag=mg_verstecken_sp,distance=..0.6] add mg_verstecken_used',
                       f'execute at @s facing {c5(VX)} {VY + 1} {c5(VZ)} run tp @s ~ ~ ~ ~180 0'])
fn(f'{_K}/kit_hid', ['clear @s', f'item replace entity @s hotbar.0 with {TAUNT}',
                     'effect give @s minecraft:weakness infinite 255 true'])
fn(f'{_K}/kit_see', ['clear @s', f'item replace entity @s hotbar.0 with {STICK}',
                     f'item replace entity @s armor.head with {_armor("helmet")}', f'item replace entity @s armor.chest with {_armor("chestplate")}',
                     'effect clear @s minecraft:weakness', 'effect clear @s minecraft:glowing', 'effect clear @s minecraft:speed'])
fn(f'{_K}/cage', [f'{OW} tp @s {c5(VX)} {VY + 1} {c5(VZ)} 0 0', 'clear @s',
                  f'item replace entity @s armor.head with {_armor("helmet")}', f'item replace entity @s armor.chest with {_armor("chestplate")}',
                  'effect give @s minecraft:blindness infinite 0 true', 'effect give @s minecraft:slowness infinite 3 true',
                  'effect clear @s minecraft:weakness', 'effect clear @s minecraft:speed'])
_setup = [
    *[f'tag @a[tag={_T}] remove {t}' for t in _ROLE_TAGS],
    f'execute as @a[tag={_T}] run function {NS}:{_K}/spawn_one',
    f'kill @e[type=minecraft:marker,tag=mg_verstecken_sp]',
    f'tag @a[tag={_T},sort=random,limit=1] add {_SEE}',
    f'tag @a[tag={_SEE}] add {_ORIG}',
    f'tag @a[tag={_T},tag=!{_SEE}] add {_HID}',
    f'team join mg_verstecken_hid @a[tag={_HID}]', f'team join mg_verstecken_see @a[tag={_SEE}]',
    *[f'scoreboard players set @a[tag={_T}] {o} 0' for o in ('mg_verstecken_dt', 'mg_verstecken_dd', 'mg_verstecken_use', 'mg_verstecken_f', 'mg_verstecken_tn', 'mg_verstecken_ab', 'mg_verstecken_cd')],
    f'effect give @a[tag={_T}] minecraft:resistance infinite 3 true',
    f'effect give @a[tag={_T}] minecraft:saturation infinite 0 true',
    f'effect give @a[tag={_T}] minecraft:night_vision infinite 0 true',
    f'effect give @a[tag={_T}] minecraft:instant_health 1 10 true',
    f'execute as @a[tag={_HID}] run function {NS}:{_K}/kit_hid',
    f'effect give @a[tag={_HID}] minecraft:speed 40 0 true',
    f'execute as @a[tag={_SEE}] run function {NS}:{_K}/cage',
    *_CAGE, 'scoreboard players set #verstecken_rel mg 0',
    f'bossbar set {NS}:verstecken color green', f'bossbar set {NS}:verstecken max {_HEAD}', f'bossbar set {NS}:verstecken value {_HEAD}',
    f'bossbar set {NS}:verstecken players @a[tag={_T}]', f'bossbar set {NS}:verstecken visible true',
]

fn(f'{_K}/reveal', [
    *_title(f'@a[tag={_SEE}]', 'Du bist der SUCHER', 'red', 'Zähl bis 40 – dann finde sie alle!'),
    *_title(f'@a[tag={_HID}]', 'VERSTECK DICH!', 'green', '40 Sekunden – lauf!'),
    f'tellraw @a[tag={_T}] {msg({"selector": f"@a[tag={_SEE}]", "color": "red", "bold": True}, _txt(" sucht! ", "white"), _txt("Die anderen haben 40 Sekunden, um sich zu verstecken.", "gray"))}',
    f'tellraw @a[tag={_HID}] {msg(_txt("Dein Name ist unsichtbar. Wirst du geschlagen, suchst du mit. ", "gray"), _txt("Taunt", "light_purple", bold=True), _txt(" (Rechtsklick) = Geräusch + 1 Münze.", "gray"))}',
    f'tellraw @a[tag={_SEE}] {msg(_txt("Du sitzt im Käfig, bis die Zeit um ist. Dann schlag die Versteckten mit dem Fangstab!", "gray"))}',
    f'execute as @a[tag={_HID}] at @s run playsound minecraft:entity.player.levelup master @s ~ ~ ~ 0.8 1.4',
    f'execute as @a[tag={_SEE}] at @s run playsound minecraft:entity.elder_guardian.curse master @s ~ ~ ~ 0.5 1.2',
])
fn(f'{_K}/release', [
    'scoreboard players set #verstecken_rel mg 1',
    *[c.replace('iron_bars' + PX, 'air replace minecraft:iron_bars').replace('iron_bars' + PZ, 'air replace minecraft:iron_bars') for c in _CAGE],
    f'effect clear @a[tag={_SEE}] minecraft:blindness', f'effect clear @a[tag={_SEE}] minecraft:slowness',
    f'execute as @a[tag={_AL},tag={_SEE}] run function {NS}:{_K}/kit_see',
    f'bossbar set {NS}:verstecken color yellow', f'bossbar set {NS}:verstecken max {_SEEK}',
    *_title(f'@a[tag={_SEE}]', 'LOS!', 'red', 'Finde sie alle!'),
    *_title(f'@a[tag={_HID}]', 'Der Sucher kommt!', 'gold', 'Psst ... nicht bewegen.'),
    f'tellraw @a[tag={_T}] {msg(_txt("Bereit oder nicht – ich komme! ", "red", bold=True), _txt("4 Minuten Suchzeit.", "gray"))}',
    f'execute as @a[tag={_T}] at @s run playsound minecraft:event.raid.horn master @s ~ ~ ~ 0.6 1.1',
    f'execute as @a[tag={_T}] at @s run playsound minecraft:block.iron_door.open master @s ~ ~ ~ 1 0.8',
    f'scoreboard players set @a[tag={_T}] mg_verstecken_dd 0',
])
# a seeker hit something: the nearest hurt hider near him is found
fn(f'{_K}/hit', [
    'scoreboard players set @s mg_verstecken_dd 0', f'tag @s add {_FD}',
    f'execute at @s as @a[tag={_AL},tag={_HID},scores={{mg_verstecken_dt=1..}},distance=..7,sort=nearest,limit=1] run function {NS}:{_K}/found',
    f'tag @s remove {_FD}',
])
fn(f'{_K}/found', [
    'scoreboard players set @s mg_verstecken_dt 0', f'tag @s remove {_HID}',
    f'scoreboard players add @a[tag={_FD}] mg_verstecken_f 1', f'scoreboard players add @a[tag={_FD}] mg_coins 2',
    f'execute store result score #verstecken_h mg if entity @a[tag={_AL},tag={_HID}]',
    f'tellraw @a[tag={_T}] {msg(_txt("✦ ", "red"), {"selector": f"@a[tag={_FD}]", "color": "red"}, _txt(" hat ", "gray"), {"selector": "@s", "color": "green", "bold": True}, _txt(" gefunden! ", "gray"), _txt("Noch ", "gray"), {"score": {"name": "#verstecken_h", "objective": "mg"}, "color": "white", "bold": True}, _txt(" versteckt.", "gray"))}',
    f'tag @s add {_SEE}', 'team join mg_verstecken_see @s', f'function {NS}:{_K}/kit_see',
    *_title('@s', 'GEFUNDEN!', 'red', 'Jetzt suchst du mit!', 'white'),
    f'title @a[tag={_FD}] actionbar {tc([_txt("✦ Gefunden! ", "gold", bold=True), _txt("+2 Münzen", "yellow")])}', f'scoreboard players set @a[tag={_FD}] mg_verstecken_ab 40',
    'execute at @s run particle minecraft:totem_of_undying ~ ~1 ~ 0.4 0.7 0.4 0.25 40',
    'execute at @s run playsound minecraft:entity.firework_rocket.blast master @a ~ ~ ~ 1.5 1.2',
    f'execute as @a[tag={_FD}] at @s run playsound minecraft:entity.player.levelup master @s ~ ~ ~ 1 1.5',
    f'execute as @a[tag={_HID}] at @s run playsound minecraft:block.note_block.bass master @s ~ ~ ~ 1 0.6',
])
_TAUNTS = ['minecraft:entity.goat.screaming.ambient', 'minecraft:entity.chicken.ambient', 'minecraft:entity.cat.ambient',
           'minecraft:entity.villager.celebrate', 'minecraft:entity.parrot.imitate.creeper', 'minecraft:block.note_block.didgeridoo',
           'minecraft:entity.pig.ambient', 'minecraft:entity.donkey.ambient']
fn(f'{_K}/taunt', [
    'scoreboard players set @s mg_verstecken_use 0',
    'scoreboard players set @s mg_verstecken_ab 40',
    f'execute if score #verstecken_t mg matches ..{_HEAD - 1} run return run title @s actionbar {tc(_txt("Taunts zählen erst, wenn der Sucher losläuft!", "gray"))}',
    f'execute if score @s mg_verstecken_cd matches 1.. run return run title @s actionbar {tc([_txt("Taunt lädt noch ... ", "gray"), {"score": {"name": "@s", "objective": "mg_verstecken_cd"}, "color": "white"}, _txt(" s", "gray")])}',
    'scoreboard players set @s mg_verstecken_cd 12',
    f'execute store result score #r mg run random value 0..{len(_TAUNTS) - 1}',
    *[f'execute if score #r mg matches {i} at @s run playsound {s} player @a ~ ~ ~ 2.5 1' for i, s in enumerate(_TAUNTS)],
    'execute at @s run particle minecraft:note ~ ~2.3 ~ 0.4 0.3 0.4 1 6',
    'execute unless score @s mg_verstecken_tn matches 10.. run scoreboard players add @s mg_coins 1', 'scoreboard players add @s mg_verstecken_tn 1',   # max 10 taunt coins per round
    f'title @s actionbar {tc([_txt("♪ Getauntet! ", "light_purple", bold=True), _txt("+1 Münze", "gold"), _txt("  (", "gray"), {"score": {"name": "@s", "objective": "mg_verstecken_tn"}, "color": "white"}, _txt(" insgesamt)", "gray")])}',
])
fn(f'{_K}/respawn', [   # someone died after all (e.g. /kill): back into the village with the right kit
    'scoreboard players set @s mg_deaths 0',
    f'{OW} tp @s {c5(_SPECT[0])} {_SPECT[1]} {c5(_SPECT[2])}', 'gamemode adventure @s',
    'effect give @s minecraft:resistance infinite 3 true', 'effect give @s minecraft:saturation infinite 0 true',
    'effect give @s minecraft:night_vision infinite 0 true',
    f'execute if entity @s[tag={_HID}] run function {NS}:{_K}/kit_hid',
    f'execute if entity @s[tag={_SEE}] if score #verstecken_t mg matches {_HEAD}.. run function {NS}:{_K}/kit_see',
    f'execute if entity @s[tag={_SEE}] if score #verstecken_t mg matches ..{_HEAD - 1} run function {NS}:{_K}/cage',
])
fn(f'{_K}/new_seeker', [   # the seeker left: a random hider takes over
    f'tag @s remove {_HID}', f'tag @s remove {_NEW}', f'tag @s add {_SEE}', f'tag @s add {_ORIG}', 'team join mg_verstecken_see @s',
    f'tellraw @a[tag={_T}] {msg(_txt("Kein Sucher mehr da – ", "yellow"), {"selector": "@s", "color": "red", "bold": True}, _txt(" sucht jetzt!", "yellow"))}',
    *_title('@s', 'Du bist jetzt SUCHER', 'red', 'Der alte Sucher ist weg.'),
    f'execute if score #verstecken_t mg matches ..{_HEAD - 1} run function {NS}:{_K}/cage',
    f'execute if score #verstecken_t mg matches {_HEAD}.. run function {NS}:{_K}/kit_see',
    'execute at @s run playsound minecraft:entity.elder_guardian.curse master @s ~ ~ ~ 0.5 1.2',
])
# item upkeep every second: dropped items vanish, lost kit items come back
fn(f'{_K}/slow', [
    f'{OW} kill @e[type=minecraft:item,{_AREA}]',
    f'execute as @a[tag={_AL},tag={_HID}] unless items entity @s container.* *[minecraft:custom_data~{{mg_verstecken:"taunt"}}] unless items entity @s weapon.offhand *[minecraft:custom_data~{{mg_verstecken:"taunt"}}] unless items entity @s player.cursor *[minecraft:custom_data~{{mg_verstecken:"taunt"}}] run give @s {TAUNT}',
    f'execute if score #verstecken_t mg matches {_HEAD}.. as @a[tag={_AL},tag={_SEE}] unless items entity @s container.* *[minecraft:custom_data~{{mg_verstecken:"stick"}}] unless items entity @s weapon.offhand *[minecraft:custom_data~{{mg_verstecken:"stick"}}] unless items entity @s player.cursor *[minecraft:custom_data~{{mg_verstecken:"stick"}}] run give @s {STICK}',
    f'clear @a[tag={_HID}] *[minecraft:custom_data~{{mg_verstecken:"stick"}}]',
])
# HUD: bossbar timer + role in the actionbar
_time = [{'score': {'name': '#verstecken_mm', 'objective': 'mg'}, 'color': 'white'}, _txt(':', 'white'),
         {'score': {'name': '#verstecken_s10', 'objective': 'mg'}, 'color': 'white'}, {'score': {'name': '#verstecken_s1', 'objective': 'mg'}, 'color': 'white'}]
fn(f'{_K}/hud', [
    f'scoreboard players remove @a[tag={_T},scores={{mg_verstecken_ab=1..}}] mg_verstecken_ab 10',
    'scoreboard players operation #verstecken_rem mg = #verstecken_end mg',
    f'execute if score #verstecken_t mg matches ..{_HEAD - 1} run scoreboard players operation #verstecken_rem mg = #verstecken_head mg',
    'scoreboard players operation #verstecken_rem mg -= #verstecken_t mg',
    'scoreboard players operation #verstecken_s mg = #verstecken_rem mg', 'scoreboard players add #verstecken_s mg 19', 'scoreboard players operation #verstecken_s mg /= #20 mg',
    'scoreboard players operation #verstecken_mm mg = #verstecken_s mg', 'scoreboard players operation #verstecken_mm mg /= #verstecken_60 mg',
    'scoreboard players operation #verstecken_ss mg = #verstecken_s mg', 'scoreboard players operation #verstecken_ss mg %= #verstecken_60 mg',
    'scoreboard players operation #verstecken_s10 mg = #verstecken_ss mg', 'scoreboard players operation #verstecken_s10 mg /= #10 mg',
    'scoreboard players operation #verstecken_s1 mg = #verstecken_ss mg', 'scoreboard players operation #verstecken_s1 mg %= #10 mg',
    f'execute store result score #verstecken_h mg if entity @a[tag={_AL},tag={_HID}]',
    f'execute store result score #verstecken_k mg if entity @a[tag={_AL},tag={_SEE}]',
    f'execute store result bossbar {NS}:verstecken value run scoreboard players get #verstecken_rem mg',
    f'execute if score #verstecken_t mg matches ..{_HEAD - 1} run bossbar set {NS}:verstecken name ' + tc(
        [_txt('Versteckt euch!  ', 'green', bold=True), _txt('⌛ ', 'gray')] + _time),
    f'execute if score #verstecken_t mg matches {_HEAD}.. run bossbar set {NS}:verstecken name ' + tc(
        [_txt('Moosgrund  ', 'dark_green', bold=True), _txt('⌛ ', 'gray')] + _time +
        [_txt('   ☺ ', 'green'), {'score': {'name': '#verstecken_h', 'objective': 'mg'}, 'color': 'white'}, _txt(' versteckt', 'gray'),
         _txt('   ⚔ ', 'red'), {'score': {'name': '#verstecken_k', 'objective': 'mg'}, 'color': 'white'}, _txt(' Sucher', 'gray')]),
    f'bossbar set {NS}:verstecken players @a[tag={_T}]',
    f'execute if score #verstecken_t mg matches ..{_HEAD - 1} as @a[tag={_AL},tag={_SEE},scores={{mg_verstecken_ab=..0}}] run title @s actionbar ' + tc(
        [_txt('⚔ SUCHER', 'red', bold=True), _txt('   Augen zu und zählen ... ', 'gray'), {'score': {'name': '#verstecken_s', 'objective': 'mg'}, 'color': 'white', 'bold': True}]),
    f'execute if score #verstecken_t mg matches {_HEAD}.. as @a[tag={_AL},tag={_SEE},scores={{mg_verstecken_ab=..0}}] run title @s actionbar ' + tc(
        [_txt('⚔ SUCHER', 'red', bold=True), _txt('   Schlag die Versteckten!  Funde: ', 'gray'), {'score': {'name': '@s', 'objective': 'mg_verstecken_f'}, 'color': 'gold'}]),
    f'execute if score #verstecken_t mg matches ..{_HEAD - 1} as @a[tag={_AL},tag={_HID},scores={{mg_verstecken_ab=..0}}] run title @s actionbar ' + tc(
        [_txt('☺ VERSTECKT', 'green', bold=True), _txt('   Taunt ab Suchbeginn', 'gray'), _txt('   Name unsichtbar', 'gray')]),
    f'execute if score #verstecken_t mg matches {_HEAD}.. as @a[tag={_AL},tag={_HID},scores={{mg_verstecken_ab=..0,mg_verstecken_cd=..0}}] run title @s actionbar ' + tc(
        [_txt('☺ VERSTECKT', 'green', bold=True), _txt('   Taunt bereit: +1 Münze', 'light_purple'), _txt('   Name unsichtbar', 'gray')]),
    f'execute as @a[tag={_AL},tag={_HID},scores={{mg_verstecken_ab=..0,mg_verstecken_cd=1..}}] run title @s actionbar ' + tc(
        [_txt('☺ VERSTECKT', 'green', bold=True), _txt('   Taunt in ', 'gray'), {'score': {'name': '@s', 'objective': 'mg_verstecken_cd'}, 'color': 'white'}, _txt(' s', 'gray'), _txt('   Name unsichtbar', 'gray')]),
])
fn(f'{_K}/glow', [
    f'effect give @a[tag={_AL},tag={_HID}] minecraft:glowing 3 0 true',
    f'title @a[tag={_T}] actionbar {tc(_txt("✧ Die Versteckten leuchten kurz auf! ✧", "yellow", bold=True))}', f'scoreboard players set @a[tag={_T}] mg_verstecken_ab 40',
    f'execute as @a[tag={_T}] at @s run playsound minecraft:block.amethyst_block.resonate master @s ~ ~ ~ 1 1.2',
    f'execute as @a[tag={_HID}] at @s run playsound minecraft:block.note_block.bit master @s ~ ~ ~ 1 0.5',
])
fn(f'{_K}/last_minute', [
    f'bossbar set {NS}:verstecken color red',
    f'tellraw @a[tag={_T}] {msg(_txt("Noch 60 Sekunden! ", "red", bold=True), _txt("Alle 15 Sekunden leuchten die Versteckten kurz auf.", "gray"))}',
    f'execute as @a[tag={_T}] at @s run playsound minecraft:block.bell.use master @s ~ ~ ~ 1 0.7',
])
_stats = [
    'scoreboard players set #verstecken_best mg 0',
    f'scoreboard players operation #verstecken_best mg > @a[tag={_T}] mg_verstecken_f',
    f'execute if score #verstecken_best mg matches 1.. as @a[tag={_T}] if score @s mg_verstecken_f = #verstecken_best mg run tellraw @a[tag={_T}] '
    + msg(_txt('Bester Sucher: ', 'gray'), {'selector': '@s', 'color': 'red', 'bold': True}, _txt('  (Funde: ', 'gray'),
          {'score': {'name': '@s', 'objective': 'mg_verstecken_f'}, 'color': 'white'}, _txt(')', 'gray')),
    f'execute as @a[tag={_T},scores={{mg_verstecken_tn=1..}}] run tellraw @s ' + msg(_txt('Deine Taunts: ', 'gray'), {'score': {'name': '@s', 'objective': 'mg_verstecken_tn'}, 'color': 'light_purple'}, _txt(' (je +1 Münze)', 'gray')),
    f'bossbar set {NS}:verstecken visible false', f'bossbar set {NS}:verstecken players',
    f'effect clear @a[tag={_T}] minecraft:blindness', f'effect clear @a[tag={_T}] minecraft:slowness', f'effect clear @a[tag={_T}] minecraft:glowing',
    f'effect give @a[tag={_T}] minecraft:glowing 5 0 true',
]
fn(f'{_K}/win_s', [
    f'tag @a[tag={_T}] remove {_AL}', f'tag @a[tag={_SEE},tag={_ORIG}] add {_AL}', f'tag @a[tag={_SEE},scores={{mg_verstecken_f=1..}}] add {_AL}',
    f'title @a[tag={_T}] subtitle {tc(_txt("Die Sucher haben alle gefunden!", "red", bold=True))}',
    f'tellraw @a[tag={_T}] {msg(_txt("Alle gefunden – die Sucher gewinnen!", "red", bold=True))}',
    f'execute as @a[tag={_T}] at @s run playsound minecraft:ui.toast.challenge_complete master @s ~ ~ ~ 1 0.9',
    *_stats, f'function {NS}:{_K}/end'])
fn(f'{_K}/win_h', [
    f'tag @a[tag={_T}] remove {_AL}', f'tag @a[tag={_HID}] add {_AL}',
    f'title @a[tag={_T}] subtitle {tc(_txt("Die Versteckten haben überlebt!", "green", bold=True))}',
    f'tellraw @a[tag={_T}] {msg(_txt("Die Zeit ist um – nicht gefunden: ", "green", bold=True), {"selector": f"@a[tag={_HID}]", "color": "white"})}',
    f'execute as @a[tag={_T}] at @s run playsound minecraft:ui.toast.challenge_complete master @s ~ ~ ~ 1 1.2',
    *_stats, f'function {NS}:{_K}/end'])
fn(f'{_K}/win_left', [   # fewer than 2 players left: whoever is still there wins
    f'tag @a[tag={_T}] remove {_AL}', f'tag @a[tag={_HID}] add {_AL}', f'tag @a[tag={_SEE}] add {_AL}',
    f'tellraw @a[tag={_T}] {msg(_txt("Zu wenige Spieler übrig – die Runde ist vorbei.", "yellow", bold=True))}',
    *_stats, f'function {NS}:{_K}/end'])

_game = [
    'scoreboard players operation #m mg = #verstecken_t mg', 'scoreboard players operation #m mg %= #20 mg',
    'scoreboard players operation #m300 mg = #verstecken_t mg', 'scoreboard players operation #m300 mg %= #verstecken_300 mg',
    f'execute if score #verstecken_t mg matches 50 run function {NS}:{_K}/reveal',
    f'execute if score #verstecken_t mg matches {_HEAD - 200}..{_HEAD - 1} if score #m mg matches 0 as @a[tag={_T}] at @s run playsound minecraft:block.note_block.hat master @s ~ ~ ~ 1 1.5',
    f'execute if score #verstecken_t mg matches ..{_HEAD - 1} if score #m mg matches 0 as @a[tag={_SEE}] at @s run playsound minecraft:block.note_block.basedrum master @s ~ ~ ~ 0.6 0.8',
    f'execute if score #verstecken_t mg matches {_HEAD}.. if score #verstecken_rel mg matches 0 run function {NS}:{_K}/release',
    f'execute if score #verstecken_t mg matches {_END - 1200} run function {NS}:{_K}/last_minute',
    f'execute if score #verstecken_t mg matches {_END - 1200}..{_END - 1} if score #m300 mg matches {(_END - 1200) % 300} run function {NS}:{_K}/glow',
    f'execute if score #verstecken_t mg matches {_END - 200}.. if score #m mg matches 0 as @a[tag={_T}] at @s run playsound minecraft:block.note_block.hat master @s ~ ~ ~ 1 1.8',
    # nobody dies, but just in case
    f'execute as @e[type=minecraft:player,tag={_AL},scores={{mg_deaths=1..}}] run function {NS}:{_K}/respawn',
    # hits: seeker dealt damage + hider took damage close to him
    f'execute if score #verstecken_t mg matches {_HEAD}.. as @a[tag={_AL},tag={_SEE},scores={{mg_verstecken_dd=1..}}] run function {NS}:{_K}/hit',
    f'scoreboard players set @a[tag={_T}] mg_verstecken_dt 0', f'scoreboard players set @a[tag={_T}] mg_verstecken_dd 0',
    # taunts
    f'execute as @a[tag={_AL},tag={_HID},scores={{mg_verstecken_use=1..}}] run function {NS}:{_K}/taunt',
    f'scoreboard players set @a[tag={_T}] mg_verstecken_use 0',
    f'execute if score #m mg matches 0 run function {NS}:{_K}/slow',
    f'execute if score #m mg matches 0 run scoreboard players remove @a[tag={_T},scores={{mg_verstecken_cd=1..}}] mg_verstecken_cd 1',
    f'execute if score #m mg matches 0 run function {NS}:{_K}/hud',
    f'execute if score #m mg matches 10 run function {NS}:{_K}/hud',
    # end conditions
    f'execute store result score #verstecken_n mg if entity @a[tag={_AL}]',
    f'execute if score #verstecken_n mg matches ..1 run return run function {NS}:{_K}/win_left',
    f'execute unless entity @a[tag={_AL},tag={_SEE}] run tag @a[tag={_AL},tag={_HID},sort=random,limit=1] add {_NEW}',
    f'execute as @a[tag={_NEW}] at @s run function {NS}:{_K}/new_seeker',
    f'execute unless entity @a[tag={_AL},tag={_HID}] run return run function {NS}:{_K}/win_s',
    f'execute if score #verstecken_t mg matches {_END}.. run return run function {NS}:{_K}/win_h',
]
_cleanup = [f'bossbar set {NS}:verstecken players', f'bossbar set {NS}:verstecken visible false',
            *[f'tag @a remove {t}' for t in _ROLE_TAGS], 'team empty mg_verstecken_hid', 'team empty mg_verstecken_see',
            f'kill @e[type=minecraft:marker,tag=mg_verstecken_sp]']

party(_K, 'Verstecken', 'green', (VX, VY, VZ), trig=66, prof='shepherd', sub='Verstecken · Suchen · Taunts', menu='Versteck dich – oder such alle',
      info='Einer sucht, alle anderen verstecken sich im verwilderten Dorf Moosgrund. Die Versteckten haben 40 Sekunden Vorsprung, '
           'ihre Namen sind unsichtbar. Wen der Sucher schlägt, der sucht mit. Taunt (Rechtsklick) macht ein Geräusch und gibt +1 Münze. '
           'Die Sucher gewinnen, wenn sie in 4 Minuten alle finden – sonst gewinnen die Versteckten. In der letzten Minute leuchten die Versteckten alle 15 Sekunden kurz auf.',
      minp=3, maxp=16, size=32, build=_b, setup=_setup, game=_game, cleanup=_cleanup, custom_end=True,
      title_sub='Versteck dich gut!', spect=_SPECT, coins_win=10)
