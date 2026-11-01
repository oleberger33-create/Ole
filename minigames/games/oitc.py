# One in the Chamber: free-for-all in the ruined sun temple "Tempel von Solaris".
# Everyone gets a wooden sword and a bow with ONE arrow that kills in one hit (Power 255 + raised arrow damage).
# Every kill gives +1 arrow. You respawn instantly at a random spawn point (away from enemies) with 2 s spawn protection.
# First to 15 kills wins; otherwise the most kills after 5 minutes (tie -> 1 min overtime, next kill decides).
# Kills come from a playerKillCount objective; live ranking in each player's actionbar. No fall damage
# (fall_damage_multiplier 0), shot arrows can't be picked up, death drops are removed.
_K = 'oitc'
_OX, _OY, _OZ = 86000, Y, 0
_T, _AL = 'mg_oitc', 'mg_al_oitc'
_WIN = 15                      # kills to win
_LEN = 6000                    # 5 min
_SD = 1200                     # overtime (1 min)
_R = 23                        # inner half size of the arena (walls at +-23)
_SPECT = (_OX, _OY + 8, _OZ)      # respawn point = shrine on top of the ziggurat (always air), players are moved on at once
_AREA = f'x={_OX - 26},y={_OY - 12},z={_OZ - 26},dx=52,dy=32,dz=52'
_TAGS = ('mg_oitc_dead', 'mg_oitc_me', 'mg_oitc_kl', 'mg_oitc_lead', 'mg_oitc_w')


def _txt(text, color, **kw):
    return dict(text=text, color=color, italic=False, **kw)


# ------------------------------------------------------------------ map: block model -> merged fills
_B = {}


def _oput(x, y, z, b):
    _B[(x, y, z)] = b


def _obox(x1, y1, z1, x2, y2, z2, b):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            for z in range(min(z1, z2), max(z1, z2) + 1):
                _B[(x, y, z)] = b


def _osolid(x, y, z):
    b = _B.get((x, y, z), 'air')
    return b != 'air' and not any(k in b for k in ('ladder', 'vine', 'lantern', 'short_grass', 'fern', 'carpet', 'water', 'torch', 'wall'))


_rng = random.Random(6886)
# base: sandstone body, floor pattern
_obox(-_R, -6, -_R, _R, -1, _R, 'sandstone')
_obox(-_R, -6, -_R, _R, -6, _R, 'smooth_sandstone')
for x in range(-_R, _R + 1):
    for z in range(-_R, _R + 1):
        b = 'smooth_sandstone'
        if x % 4 == 0 or z % 4 == 0:
            b = 'cut_sandstone'
        if x % 4 == 0 and z % 4 == 0:
            b = 'chiseled_sandstone'
        if _rng.random() < 0.07:
            b = _rng.choice(['sandstone', 'sandstone', 'smooth_red_sandstone'])
        _oput(x, 0, z, b)
# red sandstone avenues on the axes, terracotta ring around the ziggurat
for i in range(-_R, _R + 1):
    for j in (-1, 0, 1):
        _oput(i, 0, j, 'cut_red_sandstone')
        _oput(j, 0, i, 'cut_red_sandstone')
    _oput(i, 0, 0, 'smooth_red_sandstone')
    _oput(0, 0, i, 'smooth_red_sandstone')
for x in range(-11, 12):
    for z in range(-11, 12):
        d = math.hypot(x, z)
        if 9.6 <= d <= 10.5:
            _oput(x, 0, z, 'orange_terracotta' if (x + z) % 3 else 'blue_terracotta')
# overgrowth patches (moss + grass)
for cx_, cz_ in ((-8, -15), (9, 15), (-15, 14), (14, -15), (5, -13), (-6, 12)):
    for x in range(cx_ - 3, cx_ + 4):
        for z in range(cz_ - 3, cz_ + 4):
            if math.hypot(x - cx_, z - cz_) <= 2.6 + _rng.random() and abs(x) < _R and abs(z) < _R:
                _oput(x, 0, z, _rng.choice(['moss_block', 'moss_block', 'rooted_dirt', 'grass_block']))
                if _rng.random() < 0.35:
                    _oput(x, 1, z, _rng.choice(['short_grass', 'fern', 'moss_carpet']))

# perimeter wall (ruined height) with crenellations; vines on the inside
for i in range(-_R, _R + 1):
    for (x, z) in ((i, -_R), (i, _R), (-_R, i), (_R, i)):
        h = 6 if _rng.random() > 0.18 else _rng.choice([4, 5])
        _obox(x, 1, z, x, h - 1, z, 'sandstone')
        _oput(x, 3, z, 'cut_sandstone')
        _oput(x, 1, z, 'chiseled_sandstone' if i % 6 == 0 else 'sandstone')
        if h == 6:
            _oput(x, 5, z, 'smooth_sandstone')
            if i % 2 == 0:
                _oput(x, 6, z, 'sandstone_wall')
        else:
            _oput(x, h, z, 'sandstone_slab')
for _ in range(26):
    side = _rng.randint(0, 3)
    i = _rng.randint(-_R + 3, _R - 3)
    ln = _rng.randint(2, 4)
    x, z, face = {0: (i, -_R + 1, 'north'), 1: (i, _R - 1, 'south'), 2: (-_R + 1, i, 'west'), 3: (_R - 1, i, 'east')}[side]
    for k in range(ln):
        _oput(x, 5 - k, z, f'vine[{face}=true]')

# ---- central ziggurat (3 tiers) with E-W tunnel and a shrine on top
_obox(-6, 1, -6, 6, 3, 6, 'sandstone')
_obox(-6, 3, -6, 6, 3, 6, 'cut_sandstone')
for x in range(-6, 7):
    for z in (-6, 6):
        _oput(x, 2, z, 'orange_terracotta')
        _oput(z, 2, x, 'orange_terracotta')
_obox(-4, 4, -4, 4, 5, 4, 'smooth_sandstone')
for x in range(-4, 5):
    for z in (-4, 4):
        _oput(x, 4, z, 'cut_sandstone')
        _oput(z, 4, x, 'cut_sandstone')
for cx_ in (-4, 4):
    for cz_ in (-4, 4):
        _oput(cx_, 5, cz_, 'chiseled_sandstone')
_obox(-2, 6, -2, 2, 7, 2, 'cut_sandstone')
_obox(-2, 7, -2, 2, 7, 2, 'smooth_sandstone')
_oput(0, 7, 0, 'chiseled_sandstone')
for s in (-1, 1):
    # stairs on the north and south faces (3 wide)
    f = 'south' if s < 0 else 'north'
    for j in (-1, 0, 1):
        for k, (zz, lvl) in enumerate(((9, 1), (8, 2), (7, 3), (6, 4), (5, 5), (4, 6), (3, 7))):
            z = zz * s
            _obox(j, 1, z, j, lvl - 1, z, 'sandstone')
            _oput(j, lvl, z, f'sandstone_stairs[facing={f}]')
# tunnel E-W through the bottom tier, glowing floor
_obox(-6, 1, -1, 6, 2, 1, 'air')
for x in range(-6, 7):
    _oput(x, 0, 0, 'ochre_froglight' if x % 3 == 0 else 'cut_red_sandstone')
_oput(-6, 3, 0, 'chiseled_sandstone')
_oput(6, 3, 0, 'chiseled_sandstone')
# shrine
for cx_ in (-2, 2):
    for cz_ in (-2, 2):
        _obox(cx_, 8, cz_, cx_, 10, cz_, 'cut_sandstone')
        _oput(cx_, 11, cz_, 'chiseled_sandstone')
_obox(-2, 12, -2, 2, 12, 2, 'smooth_sandstone_slab')
for x in range(-2, 3):
    _oput(x, 12, -2, 'cut_sandstone')
    _oput(x, 12, 2, 'cut_sandstone')
    _oput(-2, 12, x, 'cut_sandstone')
    _oput(2, 12, x, 'cut_sandstone')
_oput(0, 12, 0, 'gold_block')
_oput(0, 11, 0, 'lantern[hanging=true]')

# ---- corner towers (5x5, ladder inside, battlements on top) at (+-20, +-20)
for sx in (-1, 1):
    for sz in (-1, 1):
        tx, tz = 20 * sx, 20 * sz
        _obox(tx - 2, 1, tz - 2, tx + 2, 6, tz + 2, 'sandstone')
        _obox(tx - 1, 1, tz - 1, tx + 1, 5, tz + 1, 'air')
        _obox(tx - 2, 3, tz - 2, tx + 2, 3, tz + 2, 'cut_sandstone')
        _obox(tx - 1, 3, tz - 1, tx + 1, 3, tz + 1, 'air')
        _obox(tx - 2, 6, tz - 2, tx + 2, 6, tz + 2, 'smooth_sandstone')
        for cx_ in (-2, 2):
            for cz_ in (-2, 2):
                _obox(tx + cx_, 1, tz + cz_, tx + cx_, 6, tz + cz_, 'chiseled_sandstone' if False else 'cut_sandstone')
        # doors towards the plaza and towards the gallery side
        _obox(tx - 2 * sx, 1, tz, tx - 2 * sx, 2, tz, 'air')
        _obox(tx, 1, tz - 2 * sz, tx, 2, tz - 2 * sz, 'air')
        # windows
        _oput(tx + 2 * sx, 4, tz, 'air')
        _oput(tx, 4, tz + 2 * sz, 'air')
        _oput(tx, 0, tz, 'ochre_froglight')
        # ladder against the outer wall (z side)
        lz = tz + sz
        for y in range(1, 7):
            _oput(tx, y, lz, f'ladder[facing={"north" if sz > 0 else "south"}]')
        # battlements (gap towards the gallery = x side towards the centre)
        for x in range(tx - 2, tx + 3):
            for z in range(tz - 2, tz + 3):
                if abs(x - tx) == 2 or abs(z - tz) == 2:
                    gallery_side = (x == tx - 2 * sx and abs(z - tz) <= 2 and abs(z) >= 19)
                    if not gallery_side and (x + z) % 2 == 0:
                        _oput(x, 7, z, 'sandstone_wall')
        _oput(tx + 2 * sx, 7, tz + 2 * sz, 'chiseled_sandstone')
        _oput(tx + 2 * sx, 8, tz + 2 * sz, 'lantern')

# ---- galleries along the north and south walls (z = +-19..+-22, floor level 6) on columns, stairs up in the middle
for s in (-1, 1):
    z1, z2 = 19 * s, 22 * s
    _obox(-17, 6, z1, 17, 6, z2, 'cut_sandstone')
    for x in range(-17, 18):
        _oput(x, 6, 19 * s, 'smooth_sandstone')
    for x in range(-16, 17, 4):
        _obox(x, 1, 19 * s, x, 5, 19 * s, 'cut_sandstone')
        _oput(x, 1, 19 * s, 'chiseled_sandstone')
        _oput(x, 5, 19 * s, 'chiseled_sandstone')
    # arches between the columns
    for x in range(-17, 18):
        if x % 4 != 0:
            _oput(x, 5, 19 * s, 'sandstone_stairs[facing=%s,half=top]' % ('west' if x % 4 == 1 else 'east')
                if x % 4 != 2 else 'cut_sandstone_slab[type=top]')
    # railing with gaps
    for x in range(-17, 18):
        if abs(x) > 1 and x % 5 not in (0,):
            _oput(x, 7, 19 * s, 'sandstone_wall')
    for x in range(-16, 17, 8):
        _oput(x, 8, 19 * s, 'lantern') if _osolid(x, 7, 19 * s) or _B.get((x, 7, 19 * s), '').endswith('wall') else None
    # staircase up from the plaza (x = -1..1, z = 13..18)
    f = 'north' if s < 0 else 'south'
    for j in (-1, 0, 1):
        for k, zz in enumerate(range(13, 19)):
            lvl = k + 1
            _obox(j, 1, zz * s, j, lvl - 1, zz * s, 'sandstone')
            _oput(j, lvl, zz * s, f'sandstone_stairs[facing={f}]')
    for k, zz in enumerate(range(13, 19)):
        for j in (-2, 2):
            _obox(j, 1, zz * s, j, k + 1, zz * s, 'cut_sandstone')
    # banners of light under the gallery
    for x in range(-14, 15, 8):
        _oput(x, 0, 21 * s, 'ochre_froglight')

# ---- east: sunken garden (floor level -3) with water channel, bushes, obelisk and a bridge
_GX1, _GX2, _GZ1, _GZ2 = 11, 21, -9, 9
_obox(_GX1, -3, _GZ1, _GX2, 0, _GZ2, 'air')
for x in range(_GX1, _GX2 + 1):
    for z in range(_GZ1, _GZ2 + 1):
        _oput(x, -3, z, _rng.choice(['moss_block', 'moss_block', 'grass_block', 'rooted_dirt']))
        _oput(x, -4, z, 'dirt')
# water channel along x (z = 0)
for x in range(14, _GX2 + 1):
    _oput(x, -3, 0, 'water')
    _oput(x, -4, 0, 'sandstone')
for x in range(14, _GX2 + 1):
    for z in (-1, 1):
        _oput(x, -3, z, 'mossy_stone_bricks' if _rng.random() < 0.5 else 'stone_bricks')
# stairs down: west (x=11,12, z -2..2), north (z -9,-8), south (z 9,8) at x 15..17
for z in range(-2, 3):
    _obox(11, -3, z, 11, -2, z, 'sandstone')
    _oput(11, -1, z, 'sandstone_stairs[facing=west]')
    _oput(12, -3, z, 'sandstone')
    _oput(12, -2, z, 'sandstone_stairs[facing=west]')
for s in (-1, 1):
    for x in range(15, 18):
        _obox(x, -3, 9 * s, x, -2, 9 * s, 'sandstone')
        _oput(x, -1, 9 * s, f'sandstone_stairs[facing={"north" if s < 0 else "south"}]')
        _oput(x, -3, 8 * s, 'sandstone')
        _oput(x, -2, 8 * s, f'sandstone_stairs[facing={"north" if s < 0 else "south"}]')
# bushes (cover)
for bx, bz in ((14, -5), (20, -6), (13, 7), (20, 7), (15, -3)):
    for x in range(bx - 1, bx + 1):
        for z in range(bz - 1, bz + 1):
            _obox(x, -2, z, x, -1, z, _rng.choice(['azalea_leaves[persistent=true]', 'flowering_azalea_leaves[persistent=true]', 'jungle_leaves[persistent=true]']))
    _oput(bx, 0, bz, 'azalea_leaves[persistent=true]') if _rng.random() < 0.5 else None
# obelisk in the garden
_obox(18, -2, -2, 18, 4, -2, 'cut_sandstone')
_oput(18, -2, -2, 'chiseled_sandstone')
_oput(18, 5, -2, 'gold_block')
# bridge across the pit (level 0, z = 3..6)
for x in range(_GX1, _GX2 + 1):
    for z in range(3, 7):
        _oput(x, 0, z, 'smooth_sandstone_slab[type=top]')
    _oput(x, 1, 3, 'sandstone_wall') if x % 2 else None
    _oput(x, 1, 6, 'sandstone_wall') if x % 2 else None
# fallen column in the garden
for x in range(12, 15):
    _oput(x, -2, -8, 'smooth_sandstone')

# ---- west: market ruins (two houses with walkable roofs, stalls, a well)
def _house(x1, z1, x2, z2, door, roof_hole):
    _obox(x1, 1, z1, x2, 4, z2, 'sandstone')
    _obox(x1 + 1, 1, z1 + 1, x2 - 1, 4, z2 - 1, 'air')
    _obox(x1, 4, z1, x2, 4, z2, 'cut_sandstone')
    _obox(x1, 5, z1, x2, 5, z2, 'smooth_sandstone')
    for x in range(x1, x2 + 1):
        for z in (z1, z2):
            if (x - x1) % 2 == 0:
                _oput(x, 6, z, 'sandstone_wall')
    for z in range(z1, z2 + 1):
        if (z - z1) % 2 == 0:
            _oput(x1, 6, z, 'sandstone_wall')
            _oput(x2, 6, z, 'sandstone_wall')
    dx, dz = door
    _obox(dx, 1, dz, dx, 2, dz, 'air')
    # windows
    for (wx, wz) in ((x1, (z1 + z2) // 2), (x2, z1 + 1), ((x1 + x2) // 2, z1), ((x1 + x2) // 2, z2)):
        _oput(wx, 2, wz, 'air')
        _oput(wx, 3, wz, 'air')
    hx, hz = roof_hole
    south = hz == z1 + 1                         # ladder against the north wall (z1) or the south wall (z2)
    _obox(hx, 4, hz, hx + 1, 5, hz + (1 if south else -1), 'air')     # collapsed corner (way up via ladder)
    for y in range(1, 6):
        _oput(hx, y, hz, f'ladder[facing={"south" if south else "north"}]')
    _oput((x1 + x2) // 2, 0, (z1 + z2) // 2, 'ochre_froglight')


_house(-21, -10, -14, -4, (-14, -7), (-20, -9))
_house(-21, 4, -14, 10, (-14, 7), (-20, 9))
# market stalls with striped canopies (cover from above)
for sz_, col in ((-2, 'orange_wool'), (2, 'cyan_wool')):
    for x in (-12, -9):
        _obox(x, 1, sz_ - 1, x, 2, sz_ - 1, 'spruce_fence')
        _obox(x, 1, sz_ + 1, x, 2, sz_ + 1, 'spruce_fence')
    for x in range(-12, -8):
        for z in range(sz_ - 1, sz_ + 2):
            _oput(x, 3, z, col if (x % 2) else 'white_wool')
    _oput(-11, 1, sz_, 'smooth_sandstone_slab')
    _oput(-10, 1, sz_, 'smooth_sandstone_slab')
# well in the market square
for x in range(-19, -16):
    for z in range(-1, 2):
        if (x, z) != (-18, 0):
            _oput(x, 1, z, 'mossy_stone_bricks')
_oput(-18, 0, 0, 'water')
_oput(-18, -1, 0, 'sandstone')
for x, z in ((-19, -1), (-17, -1), (-19, 1), (-17, 1)):
    _obox(x, 2, z, x, 3, z, 'spruce_fence')
_obox(-19, 4, -1, -17, 4, 1, 'spruce_slab')
# broken walls / cover in the market
for (x1, z1, x2, z2, h) in ((-12, -9, -10, -9, 2), (-12, 9, -11, 9, 3), (-22, -2, -22, 2, 2)):
    _obox(x1, 1, z1, x2, h, z2, 'sandstone')

# ---- broken columns around the plaza (cover), with lanterns
for (x, z, h) in ((-7, -12, 4), (7, -12, 2), (-12, -12, 3), (12, -12, 5), (-7, 12, 3), (7, 12, 5), (-12, 12, 2), (12, 12, 4),
                  (-5, -16, 2), (5, 16, 2), (-14, -16, 3), (14, 16, 3)):
    _obox(x, 1, z, x, h, z, 'cut_sandstone')
    _oput(x, 1, z, 'chiseled_sandstone')
    if h >= 4:
        _oput(x, h + 1, z, 'lantern')
    elif _rng.random() < 0.6:
        _oput(x + (1 if x > 0 else -1), 1, z, 'smooth_sandstone_slab')
# fallen column pieces
for x in range(-11, -7):
    _oput(x, 1, 16, 'smooth_sandstone')
for z in range(-17, -14):
    _oput(10, 1, z, 'smooth_sandstone')
# low half-walls for cover in the open lanes
for (x1, z1, x2, z2) in ((-16, 13, -16, 15), (16, -15, 16, -13), (3, -10, 5, -10), (-5, 10, -3, 10)):
    _obox(x1, 1, z1, x2, 1, z2, 'cut_sandstone')
    for x in range(min(x1, x2), max(x1, x2) + 1):
        for z in range(min(z1, z2), max(z1, z2) + 1):
            _oput(x, 2, z, 'sandstone_slab')

# ---- sanity pass: attached blocks need their support, plants need soil
_SOIL = ('moss_block', 'grass_block', 'rooted_dirt', 'dirt')
for (x, y, z), b in list(_B.items()):
    sup = None
    if 'ladder' in b:
        f = b.split('facing=')[1].rstrip(']')
        sup = {'north': (x, y, z + 1), 'south': (x, y, z - 1), 'east': (x - 1, y, z), 'west': (x + 1, y, z)}[f]
    elif 'vine' in b:
        f = b.split('[')[1].split('=')[0]
        sup = {'north': (x, y, z - 1), 'south': (x, y, z + 1), 'west': (x - 1, y, z), 'east': (x + 1, y, z)}[f]
    elif 'lantern' in b:
        sup = (x, y + 1, z) if 'hanging=true' in b else (x, y - 1, z)
    if sup is not None and _B.get(sup, 'air') == 'air' or (sup is not None and any(k in _B.get(sup) for k in ('ladder', 'vine', 'lantern'))):
        del _B[(x, y, z)]
    elif b in ('short_grass', 'fern') and _B.get((x, y - 1, z)) not in _SOIL:
        del _B[(x, y, z)]
    elif b == 'moss_carpet' and not _osolid(x, y - 1, z):
        del _B[(x, y, z)]

# ---- spawn points (feet position, relative) - validated below
_SPAWNS = [(0, 8, 0), (-20, 7, -20), (20, 7, -20), (-20, 7, 20), (20, 7, 20), (-8, 7, 21), (8, 7, -21),
           (-12, 1, -14), (12, 1, 14), (-14, 1, 17), (14, 1, -18), (-3, 1, 0), (3, 1, 0), (17, -2, -6), (15, -2, 7),
           (-17, 1, -2), (-18, 6, -7), (-17, 6, 7), (-10, 1, -6), (8, 1, 8), (-8, 1, -8)]
for (x, y, z) in _SPAWNS:
    for yy in (y, y + 1):
        if _B.get((x, yy, z)) in ('short_grass', 'fern', 'moss_carpet'):
            del _B[(x, yy, z)]
    assert not _osolid(x, y, z) and not _osolid(x, y + 1, z) and _B.get((x, y, z), 'air') == 'air' and _osolid(x, y - 1, z), ('bad spawn', x, y, z, _B.get((x, y - 1, z)))


def _yaw(x, z):
    return round(math.degrees(math.atan2(x, -z))) if (x, z) != (0, 0) else 0


# ---- emit: solids merged into boxes first, attached blocks afterwards
_ATT = ('ladder', 'vine', 'lantern', 'short_grass', 'fern', 'carpet', 'water', 'torch')


def _merge(cells):
    """cells: dict (x,y,z)->block (no air). Greedy merge to boxes: x-runs, then z, then y."""
    runs = {}
    by_yz = {}
    for (x, y, z), b in cells.items():
        by_yz.setdefault((y, z), []).append((x, b))
    r1 = []
    for (y, z), lst in by_yz.items():
        lst.sort()
        sx, pb, px = lst[0][0], lst[0][1], lst[0][0]
        for x, b in lst[1:]:
            if x == px + 1 and b == pb:
                px = x
                continue
            r1.append((sx, px, y, z, pb))
            sx, pb, px = x, b, x
        r1.append((sx, px, y, z, pb))
    # merge along z
    key = {}
    for (x1, x2, y, z, b) in r1:
        key.setdefault((x1, x2, y, b), []).append(z)
    r2 = []
    for (x1, x2, y, b), zs in key.items():
        zs.sort()
        s = p = zs[0]
        for z in zs[1:]:
            if z == p + 1:
                p = z
                continue
            r2.append((x1, x2, s, p, y, b))
            s = p = z
        r2.append((x1, x2, s, p, y, b))
    # merge along y
    key = {}
    for (x1, x2, z1, z2, y, b) in r2:
        key.setdefault((x1, x2, z1, z2, b), []).append(y)
    out = []
    for (x1, x2, z1, z2, b), ys in key.items():
        ys.sort()
        s = p = ys[0]
        for y in ys[1:]:
            if y == p + 1 and (x2 - x1 + 1) * (z2 - z1 + 1) * (y - s + 1) <= 32768:
                p = y
                continue
            out.append((x1, s, z1, x2, p, z2, b))
            s = p = y
        out.append((x1, s, z1, x2, p, z2, b))
    out.sort(key=lambda t: (t[1], t[0], t[2]))
    return out


def _emit(cells):
    o = []
    for (x1, y1, z1, x2, y2, z2, b) in _merge(cells):
        if (x1, y1, z1) == (x2, y2, z2):
            o.append(f'{OW} setblock {_OX + x1} {_OY + y1} {_OZ + z1} minecraft:{b}')
        else:
            o.append(f'{OW} fill {_OX + x1} {_OY + y1} {_OZ + z1} {_OX + x2} {_OY + y2} {_OZ + z2} minecraft:{b}')
    return o


_sol = {k: v for k, v in _B.items() if v != 'air' and not any(a in v for a in _ATT)}
_att = {k: v for k, v in _B.items() if v != 'air' and any(a in v for a in _ATT)}
_b = ['kill @e[type=minecraft:text_display,tag=mg_oitch]', f'{OW} kill @e[type=minecraft:arrow,{_AREA}]']
_b += clear_box(_OX - _R - 1, _OY - 7, _OZ - _R - 1, _OX + _R + 1, _OY + 16, _OZ + _R + 1, 8)
_b += _emit(_sol) + _emit(_att)
# invisible cage: barrier ring outside the walls and a ceiling
_b += [f'{OW} fill {_OX - _R - 1} {_OY - 6} {_OZ - _R - 1} {_OX + _R + 1} {_OY + 16} {_OZ - _R - 1} minecraft:barrier',
       f'{OW} fill {_OX - _R - 1} {_OY - 6} {_OZ + _R + 1} {_OX + _R + 1} {_OY + 16} {_OZ + _R + 1} minecraft:barrier',
       f'{OW} fill {_OX - _R - 1} {_OY - 6} {_OZ - _R - 1} {_OX - _R - 1} {_OY + 16} {_OZ + _R + 1} minecraft:barrier',
       f'{OW} fill {_OX + _R + 1} {_OY - 6} {_OZ - _R - 1} {_OX + _R + 1} {_OY + 16} {_OZ + _R + 1} minecraft:barrier',
       f'{OW} fill {_OX - _R} {_OY + 16} {_OZ - _R} {_OX + _R} {_OY + 16} {_OZ + _R} minecraft:barrier']
_b.append(holo('mg_oitch', c5(_OX), _OY + 14.2, c5(_OZ), [_txt('☠ ONE IN THE CHAMBER ☠\n', 'gold', bold=True), _txt('Tempel von Solaris', 'yellow')], 1.6))
_b += [f'{OW} kill @e[type=minecraft:item,{_AREA}]', f'{OW} kill @e[type=minecraft:experience_orb,{_AREA}]']

# ------------------------------------------------------------------ items / kit
_HIDE = 'minecraft:tooltip_display={hidden_components:["minecraft:enchantments","minecraft:unbreakable"]}'
_OBOW = ('minecraft:bow[minecraft:custom_name=' + tc(_txt('Ein-Schuss-Bogen', 'gold', bold=True)) +
       ',minecraft:lore=[' + tc(_txt('Jeder Treffer tötet sofort.', 'gray')) + ',' + tc(_txt('Pro Kill bekommst du 1 Pfeil.', 'gray')) + ']'
       ',minecraft:enchantments={"minecraft:power":255},minecraft:enchantment_glint_override=true,minecraft:unbreakable={},'
       'minecraft:custom_data={mg_oitc:1b},' + _HIDE + ']')
_OSWORD = ('minecraft:wooden_sword[minecraft:custom_name=' + tc(_txt('Holzschwert', 'yellow', bold=True)) +
         ',minecraft:lore=[' + tc(_txt('Kein Pfeil mehr? Dann eben so!', 'gray')) + '],minecraft:unbreakable={},'
         'minecraft:custom_data={mg_oitc:1b},' + _HIDE + ']')

ENTER_LINES.extend([f'tag @s remove {t}' for t in _TAGS] + ['attribute @s minecraft:fall_damage_multiplier base reset',
                                                           'scoreboard players set @s mg_oitc_st 0'])
EXTRA_LOAD.extend(['scoreboard objectives add mg_oitc_k playerKillCount', 'scoreboard objectives add mg_oitc_kills dummy',
                   'scoreboard objectives add mg_oitc_st dummy', 'scoreboard objectives add mg_oitc_rank dummy',
                   'scoreboard objectives add mg_oitc_ar dummy', 'scoreboard objectives add mg_oitc_fd dummy',
                   f'scoreboard players set #oitc_win mg {_WIN}'])

fn('oitc/kit', ['clear @s', f'item replace entity @s hotbar.0 with {_OSWORD}', f'item replace entity @s hotbar.1 with {_OBOW}',
                'item replace entity @s hotbar.8 with minecraft:arrow 1'])

# random spawn point, preferring points without a living enemy within 10 blocks
_N = len(_SPAWNS)
_try = ['scoreboard players add #oitc_try mg 1', f'execute store result score #oitc_r mg run random value 0..{_N - 1}']
_fb = []
for i, (x, y, z) in enumerate(_SPAWNS):
    pos = f'{c5(_OX + x)} {_OY + y} {c5(_OZ + z)}'
    tp = f'tp @s {pos} {_yaw(x, z)} 0'
    _try.append(f'execute if score #oitc_r mg matches {i} in minecraft:overworld positioned {pos} '
                f'unless entity @a[tag={_AL},tag=!mg_oitc_me,gamemode=adventure,distance=..10] run return run {OW} {tp}')
    _fb.append(f'execute if score #oitc_r mg matches {i} run return run {OW} {tp}')
_try.append(f'execute if score #oitc_try mg matches ..24 run return run function {NS}:oitc/try')
fn('oitc/try', _try + _fb)
fn('oitc/spawn', [
    'tag @s add mg_oitc_me', 'scoreboard players set #oitc_try mg 0', f'function {NS}:oitc/try', 'tag @s remove mg_oitc_me',
    'gamemode adventure @s', f'function {NS}:oitc/kit', 'effect clear @s',
    'effect give @s minecraft:resistance 2 4 true', 'effect give @s minecraft:instant_health 1 10 true',
    'attribute @s minecraft:fall_damage_multiplier base set 0',
    'scoreboard players set @s mg_oitc_st 0',
    'execute at @s run playsound minecraft:entity.enderman.teleport master @s ~ ~ ~ 0.6 1.4',
    'execute at @s run particle minecraft:cloud ~ ~1 ~ 0.3 0.6 0.3 0.02 12'])

# a kill (one per call; recursion for double kills in the same tick)
_who = {'selector': '@s', 'color': 'gold', 'bold': True}
fn('oitc/kill', [
    'scoreboard players remove @s mg_oitc_k 1', 'scoreboard players add @s mg_oitc_kills 1', 'scoreboard players add @s mg_oitc_st 1',
    'scoreboard players add @s mg_coins 1', 'tag @s add mg_oitc_kl',
    'give @s minecraft:arrow 1',
    'title @s times 0 25 8', 'title @s title {"text":""}',
    'title @s subtitle ' + tc([_txt('☠ Kill! ', 'red', bold=True), _txt('+1 Pfeil  ', 'gold'), {'score': {'name': '@s', 'objective': 'mg_oitc_kills'}, 'color': 'white', 'bold': True},
                              _txt(f'/{_WIN}', 'gray')]),
    'playsound minecraft:entity.arrow.hit_player master @s ~ ~ ~ 1 1',
    'playsound minecraft:entity.experience_orb.pickup master @s ~ ~ ~ 1 1.3',
    f'execute if score @s mg_oitc_st matches 3 run tellraw @a[tag={_T}] {msg(_who, _txt(" hat eine Serie von 3 Kills!", "yellow"))}',
    f'execute if score @s mg_oitc_st matches 5 run tellraw @a[tag={_T}] {msg(_who, _txt(" ist nicht zu stoppen! (5er-Serie)", "gold", bold=True))}',
    f'execute if score @s mg_oitc_st matches 5 as @a[tag={_T}] at @s run playsound minecraft:entity.blaze.shoot master @s ~ ~ ~ 0.6 0.8',
    f'execute if score @s mg_oitc_st matches 8 run tellraw @a[tag={_T}] {msg(_who, _txt(" ist eine LEGENDE! (8er-Serie)", "light_purple", bold=True))}',
    f'execute if score @s mg_oitc_st matches 8 as @a[tag={_T}] at @s run playsound minecraft:entity.ender_dragon.growl master @s ~ ~ ~ 0.4 1.4',
    f'execute if score @s mg_oitc_kills matches {_WIN - 1} run tellraw @a[tag={_T}] {msg(_who, _txt(" braucht nur noch 1 Kill zum Sieg!", "red", bold=True))}',
    f'execute if score @s mg_oitc_kills matches {_WIN - 1} as @a[tag={_T}] at @s run playsound minecraft:block.note_block.bell master @s ~ ~ ~ 1 0.7',
    f'execute if score @s mg_oitc_k matches 1.. run function {NS}:oitc/kill'])

fn('oitc/died', [
    'tag @s add mg_oitc_dead',
    f'execute if score @s mg_oitc_st matches 3.. if entity @a[tag=mg_oitc_kl] run tellraw @a[tag={_T}] {msg({"selector": "@a[tag=mg_oitc_kl]", "color": "white"}, _txt(" beendet die Serie von ", "yellow"), {"selector": "@s", "color": "white"}, _txt("!", "yellow"))}',
    'scoreboard players set @s mg_oitc_st 0',
    f'execute if entity @a[tag=mg_oitc_kl] run tellraw @a[tag={_T}] {tc([_txt("☠ ", "dark_red"), {"selector": "@s", "color": "gray"}, _txt(" ← ", "dark_gray"), {"selector": "@a[tag=mg_oitc_kl]", "color": "white"}])}',
    f'execute unless entity @a[tag=mg_oitc_kl] run tellraw @a[tag={_T}] {tc([_txt("☠ ", "dark_red"), {"selector": "@s", "color": "gray"}, _txt(" ist gestorben.", "dark_gray")])}',
    'title @s times 0 30 10',
    'title @s title ' + tc(_txt('Erledigt!', 'red', bold=True)),
    'execute if entity @a[tag=mg_oitc_kl] run title @s subtitle ' + tc([_txt('von ', 'gray'), {'selector': '@a[tag=mg_oitc_kl]', 'color': 'white'}]),
    'execute unless entity @a[tag=mg_oitc_kl] run title @s subtitle ' + tc(_txt('Weiter geht\'s!', 'gray'))])

fn('oitc/respawn', ['scoreboard players set @s mg_deaths 0', 'tag @s remove mg_oitc_dead', f'function {NS}:oitc/spawn'])

# leader: #oitc_max = best score, tag mg_oitc_lead, #oitc_nl = number of leaders
fn('oitc/lead', [
    'scoreboard players set #oitc_max mg 0', f'scoreboard players operation #oitc_max mg > @a[tag={_AL}] mg_oitc_kills',
    f'tag @a[tag={_T}] remove mg_oitc_lead',
    f'execute as @a[tag={_AL}] if score @s mg_oitc_kills = #oitc_max mg run tag @s add mg_oitc_lead',
    'execute store result score #oitc_nl mg if entity @a[tag=mg_oitc_lead]'])
fn('oitc/rank1', ['scoreboard players operation #oitc_me mg = @s mg_oitc_kills', 'scoreboard players set #oitc_rk mg 1',
                  f'execute as @a[tag={_AL}] if score @s mg_oitc_kills > #oitc_me mg run scoreboard players add #oitc_rk mg 1',
                  'scoreboard players operation @s mg_oitc_rank = #oitc_rk mg'])

# ---- HUD (every 10 ticks): actionbar "kills · place · arrows · leader · time"
_tm = ['scoreboard players set #oitc_rem mg %d' % _LEN, f'execute if score #oitc_sd mg matches 1 run scoreboard players set #oitc_rem mg {_LEN + _SD}',
       'scoreboard players operation #oitc_rem mg -= #oitc_t mg', 'execute if score #oitc_rem mg matches ..0 run scoreboard players set #oitc_rem mg 0',
       'scoreboard players operation #oitc_s mg = #oitc_rem mg', 'scoreboard players add #oitc_s mg 19', 'scoreboard players operation #oitc_s mg /= #20 mg',
       'scoreboard players operation #oitc_mm mg = #oitc_s mg', 'scoreboard players operation #oitc_mm mg /= #60 mg',
       'scoreboard players operation #oitc_ss mg = #oitc_s mg', 'scoreboard players operation #oitc_ss mg %= #60 mg',
       'scoreboard players operation #oitc_s10 mg = #oitc_ss mg', 'scoreboard players operation #oitc_s10 mg /= #10 mg',
       'scoreboard players operation #oitc_s1 mg = #oitc_ss mg', 'scoreboard players operation #oitc_s1 mg %= #10 mg',
       f'function {NS}:oitc/lead',
       f'execute as @a[tag={_AL}] run function {NS}:oitc/hud1']
fn('oitc/hud', _tm)
_SEP = _txt('  │  ', 'dark_gray')
_P_KILLS = [_txt('☠ ', 'red'), {'score': {'name': '@s', 'objective': 'mg_oitc_kills'}, 'color': 'white', 'bold': True}, _txt(f'/{_WIN}', 'gray'), _SEP,
            _txt('Platz ', 'gray'), {'score': {'name': '@s', 'objective': 'mg_oitc_rank'}, 'color': 'aqua', 'bold': True}, _SEP]
_P_AR = {'some': [_txt('➶ ', 'gold'), {'score': {'name': '@s', 'objective': 'mg_oitc_ar'}, 'color': 'white'}, _SEP],
         'none': [_txt('➶ 0 – nimm das Schwert!', 'red'), _SEP]}
_P_LEAD = {'none': [_txt('Noch keine Kills', 'gray')],
           'me': [_txt('★ Du führst!', 'green', bold=True)],
           'other': [_txt('Führung: ', 'gray'), {'selector': '@a[tag=mg_oitc_lead]', 'color': 'yellow'}, _txt(' (', 'gray'),
                     {'score': {'name': '#oitc_max', 'objective': 'mg'}, 'color': 'white'}, _txt(')', 'gray')]}
_P_TIME = {0: [_SEP, _txt('⌛ ', 'gray'), {'score': {'name': '#oitc_mm', 'objective': 'mg'}, 'color': 'white'}, _txt(':', 'white'),
               {'score': {'name': '#oitc_s10', 'objective': 'mg'}, 'color': 'white'}, {'score': {'name': '#oitc_s1', 'objective': 'mg'}, 'color': 'white'}],
           1: [_SEP, _txt('VERLÄNGERUNG ', 'light_purple', bold=True), {'score': {'name': '#oitc_mm', 'objective': 'mg'}, 'color': 'white'}, _txt(':', 'white'),
               {'score': {'name': '#oitc_s10', 'objective': 'mg'}, 'color': 'white'}, {'score': {'name': '#oitc_s1', 'objective': 'mg'}, 'color': 'white'}]}
_h = [f'function {NS}:oitc/rank1', 'execute store result score @s mg_oitc_ar run clear @s minecraft:arrow 0',
      'scoreboard players set #oitc_hl mg 2', 'execute if score #oitc_max mg matches 0 run scoreboard players set #oitc_hl mg 0',
      'execute if score #oitc_max mg matches 1.. if score #oitc_nl mg matches 1 if entity @s[tag=mg_oitc_lead] run scoreboard players set #oitc_hl mg 1',
      'scoreboard players set #oitc_ha mg 1', 'execute if score @s mg_oitc_ar matches 0 run scoreboard players set #oitc_ha mg 0']
for ai, ak in enumerate(('none', 'some')):
    for li, lk in enumerate(('none', 'me', 'other')):
        for sd in (0, 1):
            _h.append(f'execute if score #oitc_ha mg matches {ai} if score #oitc_hl mg matches {li} if score #oitc_sd mg matches {sd} run title @s actionbar '
                      + tc(_P_KILLS + _P_AR[ak] + _P_LEAD[lk] + _P_TIME[sd]))
fn('oitc/hud1', _h)

# ---- end of the round
fn('oitc/podium', [
    f'function {NS}:oitc/lead', 'execute if score #oitc_max mg matches 0 run return 0',
    f'execute as @a[tag={_T}] run function {NS}:oitc/rank1',
    f'tellraw @a[tag={_T}] {tc(_txt("━━━━━━━━ Endstand ━━━━━━━━", "gold", bold=True))}',
    *[f'execute as @a[tag={_AL},scores={{mg_oitc_rank={r}}}] run tellraw @a[tag={_T}] '
      + tc([_txt(f'  {m} {r}. ', c, bold=True), {'selector': '@s', 'color': 'white'}, _txt(' – ', 'dark_gray'),
            _txt('Kills: ', 'gray'), {'score': {'name': '@s', 'objective': 'mg_oitc_kills'}, 'color': c, 'bold': True}])
      for r, m, c in ((1, '①', 'gold'), (2, '②', 'white'), (3, '③', 'red'))],
    f'execute as @a[tag={_AL},scores={{mg_oitc_rank=4..}}] run tellraw @s '
    + tc([_txt('  Dein Platz: ', 'gray'), {'score': {'name': '@s', 'objective': 'mg_oitc_rank'}, 'color': 'aqua', 'bold': True},
          _txt(' (Kills: ', 'gray'), {'score': {'name': '@s', 'objective': 'mg_oitc_kills'}, 'color': 'white'}, _txt(')', 'gray')])])
fn('oitc/win', [   # winners carry mg_oitc_w
    f'function {NS}:oitc/podium',
    f'execute unless entity @a[tag={_T},tag=mg_oitc_w] run return run function {NS}:oitc/draw',
    f'tag @a[tag={_T}] remove {_AL}', f'tag @a[tag={_T},tag=mg_oitc_w] add {_AL}', f'tag @a[tag={_T}] remove mg_oitc_w',
    f'effect give @a[tag={_T}] minecraft:resistance 10 4 true',
    f'clear @a[tag={_T}] minecraft:arrow',
    f'execute as @a[tag={_AL}] at @s run playsound minecraft:ui.toast.challenge_complete master @s ~ ~ ~ 1 1',
    f'execute as @a[tag={_T},tag=!{_AL}] at @s run playsound minecraft:entity.villager.no master @s ~ ~ ~ 1 0.8',
    f'execute if entity @a[tag={_AL}] run title @a[tag={_T}] subtitle ' + tc([{'selector': f'@a[tag={_AL}]', 'color': 'gold', 'bold': True}, _txt(' gewinnt!', 'white')]),
    f'function {NS}:{_K}/end'])
fn('oitc/draw', [   # nobody won: own ending (framework end would say 'niemand hat überlebt', wrong in a respawn FFA)
    f'tag @a[tag={_T}] remove {_AL}',
    f'effect give @a[tag={_T}] minecraft:resistance 10 4 true',
    f'clear @a[tag={_T}] minecraft:arrow',
    f'execute as @a[tag={_T}] at @s run playsound minecraft:entity.villager.no master @s ~ ~ ~ 1 0.8',
    f'title @a[tag={_T}] subtitle ' + tc(_txt('Unentschieden', 'gray')),
    f'title @a[tag={_T}] title ' + tc(_txt('Spiel vorbei!', 'gold', bold=True)),
    f'scoreboard players set #{_K} mg 3', f'schedule function {NS}:{_K}/finish 100t'])
fn('oitc/win_kills', [
    f'tag @a[tag={_AL},scores={{mg_oitc_kills={_WIN}..}}] add mg_oitc_w',
    f'tellraw @a[tag={_T}] {msg({"selector": "@a[tag=mg_oitc_w]", "color": "gold", "bold": True}, _txt(f" hat {_WIN} Kills erreicht!", "yellow", bold=True))}',
    f'function {NS}:oitc/win'])
fn('oitc/alone', [
    f'tag @a[tag={_AL}] add mg_oitc_w',
    f'tellraw @a[tag={_T}] {msg(_txt("Alle anderen haben das Spiel verlassen.", "yellow"))}',
    f'function {NS}:oitc/win'])
fn('oitc/timeup', [
    f'function {NS}:oitc/lead',
    f'tellraw @a[tag={_T}] {msg(_txt("Die Zeit ist um!", "yellow", bold=True))}',
    f'execute if score #oitc_max mg matches 0 run tellraw @a[tag={_T}] {msg(_txt("Niemand hat einen Kill geschafft – Unentschieden.", "gray"))}',
    f'execute if score #oitc_max mg matches 0 run return run function {NS}:oitc/win',
    f'execute if score #oitc_nl mg matches 1 run tag @a[tag=mg_oitc_lead] add mg_oitc_w',
    f'execute if score #oitc_nl mg matches 1 run return run function {NS}:oitc/win',
    'scoreboard players set #oitc_sd mg 1',
    f'tellraw @a[tag={_T}] {msg(_txt("Gleichstand! ", "light_purple", bold=True), _txt("Verlängerung: Der nächste Kill eines Führenden entscheidet (1 Minute)!", "white"))}',
    f'title @a[tag={_T}] times 5 40 15', f'title @a[tag={_T}] subtitle {tc(_txt("Der nächste Kill entscheidet", "white"))}',
    f'title @a[tag={_T}] title {tc(_txt("VERLÄNGERUNG!", "light_purple", bold=True))}',
    f'execute as @a[tag={_T}] at @s run playsound minecraft:entity.ender_dragon.growl master @s ~ ~ ~ 0.5 1.2'])
fn('oitc/sdend', [   # overtime over: all leaders share the win
    f'function {NS}:oitc/lead',
    f'tellraw @a[tag={_T}] {msg(_txt("Die Verlängerung ist vorbei – Gleichstand!", "light_purple"))}',
    f'tag @a[tag=mg_oitc_lead] add mg_oitc_w', f'function {NS}:oitc/win'])
fn('oitc/sdchk', [f'function {NS}:oitc/lead', f'execute if score #oitc_nl mg matches 1 run tag @a[tag=mg_oitc_lead] add mg_oitc_w',
                  f'execute if score #oitc_nl mg matches 1 run function {NS}:oitc/win'])

# ---- periodic housekeeping
fn('oitc/slow', [
    f'{OW} kill @e[type=minecraft:arrow,{_AREA},nbt={{inGround:1b}}]',
    f'execute as @a[tag={_AL},gamemode=adventure] store result score @s mg_oitc_ar run clear @s minecraft:wooden_sword 0',
    f'execute as @a[tag={_AL},gamemode=adventure,scores={{mg_oitc_ar=0}}] run give @s {_OSWORD}',
    f'execute as @a[tag={_AL},gamemode=adventure] store result score @s mg_oitc_ar run clear @s minecraft:bow 0',
    f'execute as @a[tag={_AL},gamemode=adventure,scores={{mg_oitc_ar=0}}] run give @s {_OBOW}',
    f'execute as @a[tag={_AL},gamemode=adventure] store result score @s mg_oitc_fd run data get entity @s foodLevel',
    f'effect give @a[tag={_AL},scores={{mg_oitc_fd=..15}}] minecraft:saturation 1 0 true'])

_setup = [
    'scoreboard players set #oitc_sd mg 0', *[f'tag @a[tag={_T}] remove {t}' for t in _TAGS],
    *[f'scoreboard players set @a[tag={_T}] {o} 0' for o in ('mg_oitc_k', 'mg_oitc_kills', 'mg_oitc_st', 'mg_oitc_ar')],
    f'scoreboard players set @a[tag={_T}] mg_oitc_rank 1',
    f'execute as @a[tag={_T},sort=random] run function {NS}:oitc/spawn',
    f'function {NS}:oitc/hud',
    f'execute as @a[tag={_T}] at @s run playsound minecraft:item.crossbow.loading_end master @s ~ ~ ~ 1 1']

_game = [
    'scoreboard players operation #m mg = #oitc_t mg', 'scoreboard players operation #m mg %= #20 mg',
    # new arrows: no pickup, lethal base damage (on top of Power 255)
    f'execute as @e[type=minecraft:arrow,{_AREA},tag=!mg_oitc_ar] run data merge entity @s {{pickup:0b,damage:100.0d,Tags:["mg_oitc_ar"]}}',
    f'{OW} kill @e[type=minecraft:item,{_AREA}]', f'{OW} kill @e[type=minecraft:experience_orb,{_AREA}]',
    # kills first (tags the killer for the death message), then deaths, then respawns of players that are alive again
    f'execute as @a[tag={_AL},scores={{mg_oitc_k=1..}}] at @s run function {NS}:oitc/kill',
    f'execute as @a[tag={_AL},tag=!mg_oitc_dead,scores={{mg_deaths=1..}}] run function {NS}:oitc/died',
    'tag @a[tag=mg_oitc_kl] remove mg_oitc_kl',
    f'execute as @e[type=minecraft:player,tag={_AL},tag=mg_oitc_dead] run function {NS}:oitc/respawn',
    f'execute as @a[tag={_AL},gamemode=adventure] at @s if entity @s[y=-64,dy={_OY - 9 + 64}] run kill @s',
    f'execute if score #m mg matches 0 run function {NS}:oitc/hud', f'execute if score #m mg matches 10 run function {NS}:oitc/hud',
    f'execute if score #m mg matches 5 run function {NS}:oitc/slow',
    f'execute if score #oitc_t mg matches {_LEN - 1200} run tellraw @a[tag={_T}] {msg(_txt("Noch 1 Minute!", "yellow", bold=True))}',
    f'execute if score #oitc_t mg matches {_LEN - 200}.. if score #oitc_t mg matches ..{_LEN - 1} if score #m mg matches 0 as @a[tag={_T}] at @s run playsound minecraft:block.note_block.hat master @s ~ ~ ~ 1 1.5',
    # end conditions
    f'execute if entity @a[tag={_AL},scores={{mg_oitc_kills={_WIN}..}}] run return run function {NS}:oitc/win_kills',
    f'execute store result score #oitc_n mg if entity @a[tag={_AL}]',
    f'execute if score #oitc_n mg matches ..1 run return run function {NS}:oitc/alone',
    f'execute if score #oitc_sd mg matches 1 if score #oitc_t mg matches {_LEN + _SD}.. run return run function {NS}:oitc/sdend',
    f'execute if score #oitc_sd mg matches 1 run return run function {NS}:oitc/sdchk',
    f'execute if score #oitc_t mg matches {_LEN}.. run return run function {NS}:oitc/timeup',
]
_cleanup = [*[f'tag @a remove {t}' for t in _TAGS], f'{OW} kill @e[type=minecraft:arrow,{_AREA}]', 'scoreboard players set #oitc_sd mg 0']

party(_K, 'One in the Chamber', 'gold', (_OX, _OY, _OZ), trig=68, prof='librarian', sub='1 Pfeil · 1 Treffer · 15 Kills',
      menu='Ein Pfeil, ein Kill',
      info='Jeder gegen jeden! Du hast einen Bogen mit nur EINEM Pfeil – jeder Treffer tötet sofort. Für jeden Kill bekommst du einen neuen Pfeil. '
           'Daneben? Dann hilft nur das Holzschwert. Nach dem Tod respawnst du sofort an einem zufälligen Punkt. '
           'Wer zuerst 15 Kills hat, gewinnt – sonst die meisten Kills nach 5 Minuten.',
      minp=2, maxp=12, size=32, build=_b, setup=_setup, game=_game, cleanup=_cleanup, custom_end=True,
      title_sub='Ein Pfeil. Ein Kill.', spect=_SPECT, coins_win=10)
