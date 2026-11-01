# Bot-Duelle: play the 1v1 modes alone against a mob "bot" with 4 difficulty levels.
# Pure vanilla: a bot is a mob (zombie / vindicator / skeleton / stray) with tuned attributes, cosmetic equipment and a
# coloured name ("Bot · Mittel"). Best of 3 rounds, 3 s freeze per round (player slowness+weakness, mob NoAI).
# Up to _NS matches at the same time, each in its own arena slot far away (x = 90000 + 300*slot); a slot is
# forceloaded only while it is in use. Menu: NPC "Bot-Duelle" / compass (trigger 69) or the line in the 1v1 menu;
# a difficulty button runs /trigger mg_aktion set 200 + mode*10 + difficulty (211..254, see AKTION_EXTRA).
# Rewards: coins only (1/2/3/5 by difficulty, at most _CAP per refill window, -1 every 3 min), no mg_wins.
# Beaten difficulties are kept as tags mg_botw_<mode><diff> (shown as ✔ in the menu and in the stats menu).
_K = 'bot'
_NS = 6                                   # arena slots = parallel matches
_SX = lambda i: 90000 + 300 * i           # slot origin x (z = 0, floor y = Y)
_TRIG = 69
_CAP = 20                                 # bot coins per window
_DEC = 3600                               # ticks per refill step (1 coin)
_FALL = Y - 5                             # feet below Y-4 -> fallen (sumo / kb); the other arenas are walled
_FALL_DY = _FALL + 64
_ROUND_MAX = 2400                         # 2 min per round, then the round is replayed
_T = 'mg_bot'                             # player tag while in a bot match
_M = 'mg_botm'                            # mob tag

DIFFS = [(1, 'Leicht', 'green', 5635925, 1), (2, 'Mittel', 'yellow', 16777045, 2), (3, 'Schwer', 'red', 16733525, 3),
         (4, 'Extrem', 'dark_purple', 11141290, 5)]   # (id, name, colour, leather rgb, coins)
DN = {d: n for d, n, *_ in DIFFS}
DC = {d: c for d, _, c, *_ in DIFFS}
BOX_PLAYER = 10                                        # Boxen: hits the player needs
BOX_BOT = {1: 15, 2: 10, 3: 8, 4: 6}                   # Boxen: hits the bot needs

# (id, key, name, colour, short description, player spawn, mob spawn)
BMODES = [(1, 'schwert', 'Schwert-Duell', 'red', 'Eisenschwert und Eisenrüstung gegen einen Kämpfer', (-7, -90), (7, 90)),
          (2, 'boxen', 'Boxen', 'gray', f'Nur Fäuste – du brauchst {BOX_PLAYER} Treffer, der Bot je nach Stufe {BOX_BOT[4]}–{BOX_BOT[1]}', (-3, -90), (3, 90)),
          (3, 'sumo', 'Sumo', 'yellow', 'Ohne Schaden – schubs den Bot von der Plattform', (-3, -90), (3, 90)),
          (4, 'kb', 'Knockback', 'gold', 'Rückstoß-Stock auf einer kleinen Insel – runter mit ihm', (-3, -90), (3, 90)),
          (5, 'bogen', 'Bogen', 'dark_aqua', 'Bogenduell zwischen Deckungsmauern', (-14, -90), (14, 90))]
MN = {m: n for m, _, n, *_ in BMODES}
MCOL = {m: c for m, _, _, c, *_ in BMODES}


def _bt(text, color, **kw):
    return dict(text=text, color=color, italic=False, **kw)


def _rd(r, y, block):
    """disk relative to the execution position (same shape as disk())"""
    out = []
    for dz in range(-r, r + 1):
        w = int(math.floor(math.sqrt(r * r + r - dz * dz)))
        out.append(f'fill ~{-w} ~{y} ~{dz} ~{w} ~{y} ~{dz} minecraft:{block}')
    return out


def _rring(r, y, block, h=1):
    pts = set()
    for a in range(0, 360, 2):
        pts.add((round((r + 0.5) * math.cos(math.radians(a))), round((r + 0.5) * math.sin(math.radians(a)))))
    return [f'fill ~{x} ~{y} ~{z} ~{x} ~{y + h - 1} ~{z} minecraft:{block}' for x, z in sorted(pts)]


# ------------------------------------------------------------------ arenas (relative to the slot origin, floor at ~0)
ARENA_B = {
    'schwert': (_rd(12, -1, 'stone') + _rd(12, 0, 'stone_bricks') + _rd(9, 0, 'polished_andesite') + _rd(3, 0, 'chiseled_stone_bricks')
                + _rring(12, 1, 'barrier', 5) + _rring(12, 1, 'stone_brick_wall', 1)
                + [f'fill ~{x} ~1 ~{z} ~{x} ~2 ~{z} minecraft:mossy_stone_bricks' for x, z in ((-4, -7), (4, 7), (-4, 7), (4, -7))]
                + [f'setblock ~{x} ~3 ~{z} minecraft:lantern' for x, z in ((-4, -7), (4, 7), (-4, 7), (4, -7))]),
    'boxen': ['fill ~-7 ~-1 ~-7 ~7 ~-1 ~7 minecraft:stone', 'fill ~-7 ~ ~-7 ~7 ~ ~7 minecraft:white_concrete',
              'fill ~-6 ~ ~-6 ~6 ~ ~6 minecraft:light_gray_concrete', 'fill ~-1 ~ ~-1 ~1 ~ ~1 minecraft:gray_concrete',
              'fill ~-7 ~1 ~-7 ~7 ~4 ~-7 minecraft:barrier', 'fill ~-7 ~1 ~7 ~7 ~4 ~7 minecraft:barrier',
              'fill ~-7 ~1 ~-7 ~-7 ~4 ~7 minecraft:barrier', 'fill ~7 ~1 ~-7 ~7 ~4 ~7 minecraft:barrier',
              'fill ~-7 ~1 ~-7 ~-7 ~2 ~-7 minecraft:red_concrete', 'fill ~-7 ~1 ~7 ~-7 ~2 ~7 minecraft:red_concrete',
              'fill ~7 ~1 ~-7 ~7 ~2 ~-7 minecraft:blue_concrete', 'fill ~7 ~1 ~7 ~7 ~2 ~7 minecraft:blue_concrete',
              'fill ~-6 ~1 ~-7 ~6 ~1 ~-7 minecraft:white_carpet', 'fill ~-6 ~1 ~7 ~6 ~1 ~7 minecraft:white_carpet',
              'fill ~-7 ~1 ~-6 ~-7 ~1 ~6 minecraft:white_carpet', 'fill ~7 ~1 ~-6 ~7 ~1 ~6 minecraft:white_carpet'],
    'sumo': _rd(6, 0, 'white_concrete') + _rd(5, 0, 'yellow_concrete') + _rd(5, -1, 'smooth_stone') + _rd(2, -2, 'smooth_stone'),
    'kb': (_rd(6, 0, 'grass_block') + _rd(5, -1, 'dirt') + _rd(3, -2, 'dirt') + _rd(2, -3, 'stone') + _rd(1, -4, 'stone')
           + ['setblock ~ ~ ~ minecraft:moss_block']),
    'bogen': ['fill ~-17 ~-1 ~-8 ~17 ~-1 ~8 minecraft:stone', 'fill ~-17 ~ ~-8 ~17 ~ ~8 minecraft:stone_bricks',
              'fill ~-16 ~ ~-7 ~16 ~ ~7 minecraft:polished_andesite', 'fill ~-1 ~ ~-7 ~1 ~ ~7 minecraft:stone_bricks',
              'fill ~-17 ~1 ~-8 ~17 ~6 ~-8 minecraft:barrier', 'fill ~-17 ~1 ~8 ~17 ~6 ~8 minecraft:barrier',
              'fill ~-17 ~1 ~-8 ~-17 ~6 ~8 minecraft:barrier', 'fill ~17 ~1 ~-8 ~17 ~6 ~8 minecraft:barrier',
              'fill ~-17 ~1 ~-8 ~17 ~1 ~-8 minecraft:stone_brick_wall', 'fill ~-17 ~1 ~8 ~17 ~1 ~8 minecraft:stone_brick_wall',
              'fill ~-17 ~1 ~-8 ~-17 ~1 ~8 minecraft:stone_brick_wall', 'fill ~17 ~1 ~-8 ~17 ~1 ~8 minecraft:stone_brick_wall',
              # cover: 2-high walls beside the centre line (the line between the spawns stays free, so the bot sees you at the start)
              *[f'fill ~{s * 8} ~1 ~{z1} ~{s * 8} ~2 ~{z2} minecraft:mossy_stone_bricks' for s in (-1, 1) for z1, z2 in ((-6, -3), (3, 6))],
              *[f'fill ~{s * 4} ~1 ~{z1} ~{s * 4} ~1 ~{z2} minecraft:cobblestone_wall' for s in (-1, 1) for z1, z2 in ((-3, -2), (2, 3))],
              'fill ~ ~1 ~-5 ~ ~2 ~-3 minecraft:mossy_stone_bricks', 'fill ~ ~1 ~3 ~ ~2 ~5 minecraft:mossy_stone_bricks'],
}

# ------------------------------------------------------------------ bots: (entity, attributes, equipment, extra nbt, effects)
def _eq(item, comps=None):
    c = {'"minecraft:unbreakable"': '{}', '"minecraft:attribute_modifiers"': '[]'}   # cosmetic: stats come from the mob attributes
    c.update(comps or {})
    return f'{{id:"minecraft:{item}",count:1,components:{{' + ','.join(f'{k}:{v}' for k, v in c.items()) + '}}'


def _leather(rgb):
    return {s: _eq(f'leather_{p}', {'"minecraft:dyed_color"': str(rgb)}) for s, p in (('head', 'helmet'), ('chest', 'chestplate'), ('legs', 'leggings'), ('feet', 'boots'))}


def _set(mat):
    return {s: _eq(f'{mat}_{p}') for s, p in (('head', 'helmet'), ('chest', 'chestplate'), ('legs', 'leggings'), ('feet', 'boots'))}


def _ench(**lv):
    return {'"minecraft:enchantments"': '{' + ','.join(f'"minecraft:{k}":{v}' for k, v in lv.items()) + '}', '"minecraft:enchantment_glint_override"': 'true'}


# Balance (measured on a test server against scripted players, see the playtest notes): melee mobs get a longer reach via
# attack_range on the held item (default mob reach is ~0.8 blocks, a player's 3 -> a player who just clicks keeps any mob
# away). The kit gives saturation, so a mob must deal more than ~2 HP/s to make progress early in a round.
SPEC = {}
for d, dn, dc, rgb, _c in DIFFS:
    # Schwert-Duell: zombie (Leicht..Schwer), vindicator (Extrem). Player: iron sword (6) + iron armour (15).
    sw = {1: dict(e='zombie', spd=0.23, dmg=2.5, hp=20, arm=4, tou=0, kbr=0.0, rch=2.0, eq=dict(_leather(rgb), mainhand=_eq('wooden_sword'))),
          2: dict(e='zombie', spd=0.26, dmg=4.5, hp=30, arm=8, tou=0, kbr=0.5, rch=2.8, eq=dict(_set('chainmail'), mainhand=_eq('stone_sword'))),
          3: dict(e='zombie', spd=0.29, dmg=6.5, hp=36, arm=12, tou=0, kbr=0.65, rch=2.9, eq=dict(_set('iron'), mainhand=_eq('iron_sword'))),
          4: dict(e='vindicator', spd=0.33, dmg=7, hp=34, arm=14, tou=2, kbr=0.7, rch=3.0, eq=dict(head=_eq('diamond_helmet'), mainhand=_eq('diamond_axe', _ench(sharpness=1))))}[d]
    SPEC[(1, d)] = sw
    # Boxen: fists only, 1 damage; difficulty = speed, knockback resistance, hits the bot needs
    SPEC[(2, d)] = dict(e='zombie', spd=[0.2, 0.26, 0.29, 0.32][d - 1], dmg=1, hp=60, arm=0, tou=0, kbr=[0.0, 0.3, 0.5, 0.65][d - 1], akb=[0, 0, 0.3, 0.6][d - 1],
                        rch=[1.4, 2.0, 2.5, 2.8][d - 1], eq=_leather(rgb))
    # Sumo: no damage (resistance), the bot hits with extra attack knockback
    SPEC[(3, d)] = dict(e='zombie', spd=[0.19, 0.26, 0.29, 0.32][d - 1], dmg=1, hp=20, arm=0, tou=0, kbr=[0.0, 0.15, 0.25, 0.4][d - 1],
                        akb=[0.0, 0.3, 0.5, 0.8][d - 1], rch=[1.2, 1.8, 2.3, 2.6][d - 1], res=True, eq=_leather(rgb))
    # Knockback: stick without / with knockback 2/2/3, no damage
    kbl = [0, 2, 2, 3][d - 1]
    SPEC[(4, d)] = dict(e='zombie', spd=[0.19, 0.26, 0.29, 0.32][d - 1], dmg=1, hp=20, arm=0, tou=0, kbr=[0.0, 0.3, 0.5, 0.65][d - 1],
                        akb=[0.0, 0.0, 0.5, 0.5][d - 1], rch=[1.4, 2.2, 2.8, 3.0][d - 1], res=True,
                        eq=dict(_leather(rgb), mainhand=_eq('stick', _ench(knockback=kbl) if kbl else None)))
    # Bogen: skeleton (Leicht/Mittel), stray with slowness arrows (Schwer/Extrem)
    bw = {1: dict(e='skeleton', spd=0.22, dmg=2, hp=16, arm=0, tou=0, kbr=0.0, eq=dict(head=_eq('leather_helmet', {'"minecraft:dyed_color"': str(rgb)}), mainhand=_eq('bow'))),
          2: dict(e='skeleton', spd=0.25, dmg=2, hp=22, arm=4, tou=0, kbr=0.0, eq=dict(_leather(rgb), mainhand=_eq('bow', _ench(power=2)))),
          3: dict(e='stray', spd=0.27, dmg=2, hp=28, arm=8, tou=0, kbr=0.1, eq=dict(_set('chainmail'), mainhand=_eq('bow', _ench(power=5)))),
          4: dict(e='stray', spd=0.30, dmg=2, hp=34, arm=12, tou=0, kbr=0.2, eq=dict(_set('iron'), mainhand=_eq('bow', _ench(power=5, punch=1, flame=1))))}[d]
    SPEC[(5, d)] = bw
FOLLOW = {1: 24, 2: 16, 3: 16, 4: 16, 5: 40}


def summon_cmd(m, d):
    s = SPEC[(m, d)]
    attrs = {'movement_speed': s['spd'], 'attack_damage': s['dmg'], 'max_health': s['hp'], 'armor': s['arm'], 'armor_toughness': s['tou'],
             'knockback_resistance': s['kbr'], 'follow_range': FOLLOW[m], 'attack_knockback': s.get('akb', 0)}
    if s['e'] == 'zombie':
        attrs['spawn_reinforcements'] = 0
    at = ','.join(f'{{id:"minecraft:{k}",base:{v}d}}' for k, v in attrs.items())
    eqd = dict(s['eq'])
    if s.get('rch'):   # melee reach (attack_range on the held item; mobs use it too). Fists: an invisible item (model air)
        hand = eqd.get('mainhand') or _eq('stick', {'"minecraft:item_model"': '"minecraft:air"'})
        eqd['mainhand'] = hand[:-2] + f',"minecraft:attack_range":{{max_reach:{s["rch"]}f,mob_factor:1.0f}}}}}}'
    eq = ','.join(f'{k}:{v}' for k, v in eqd.items())
    name = tc({'text': 'Bot · ' + DN[d], 'color': DC[d], 'bold': d == 4})
    # the custom name is an SNBT text component (26.x): JSON object syntax is valid SNBT here
    extra = {'zombie': 'IsBaby:0b,CanBreakDoors:0b,', 'vindicator': 'PatrolLeader:0b,CanJoinRaid:0b,Johnny:0b,'}.get(s['e'], '')
    _, _, _, _, _, _, (mx, myaw) = BMODES[m - 1]
    # NoAI + Invulnerable during the freeze (a bow shot at the frozen bot would otherwise win the round before it moves)
    return (f'summon minecraft:{s["e"]} ~{mx} ~1 ~ {{Tags:["{_M}","{_M}_new"],NoAI:1b,Invulnerable:1b,PersistenceRequired:1b,CanPickUpLoot:0b,'
            f'DeathLootTable:"minecraft:empty",{extra}Health:{s["hp"]}f,Rotation:[{myaw}f,0f],CustomName:{name},CustomNameVisible:1b,'
            'drop_chances:{mainhand:0f,offhand:0f,head:0f,chest:0f,legs:0f,feet:0f},'
            f'equipment:{{{eq}}},attributes:[{at}]}}')


# ------------------------------------------------------------------ player kits
UNB = 'minecraft:unbreakable={}'
KIT_B = {
    'schwert': ['item replace entity @s armor.head with minecraft:iron_helmet[' + UNB + ']', 'item replace entity @s armor.chest with minecraft:iron_chestplate[' + UNB + ']',
                'item replace entity @s armor.legs with minecraft:iron_leggings[' + UNB + ']', 'item replace entity @s armor.feet with minecraft:iron_boots[' + UNB + ']',
                'item replace entity @s hotbar.0 with minecraft:iron_sword[' + UNB + ']', 'item replace entity @s hotbar.1 with minecraft:cooked_beef 4'],
    'boxen': [],
    'sumo': ['effect give @s minecraft:resistance infinite 4 true'],
    'kb': ['effect give @s minecraft:resistance infinite 4 true',
           'item replace entity @s hotbar.0 with minecraft:stick[minecraft:enchantments={"minecraft:knockback":3},minecraft:enchantment_glint_override=true]'],
    'bogen': ['item replace entity @s armor.head with minecraft:chainmail_helmet[' + UNB + ']', 'item replace entity @s armor.chest with minecraft:chainmail_chestplate[' + UNB + ']',
              'item replace entity @s armor.legs with minecraft:chainmail_leggings[' + UNB + ']', 'item replace entity @s armor.feet with minecraft:chainmail_boots[' + UNB + ']',
              'item replace entity @s hotbar.0 with minecraft:bow[minecraft:enchantments={"minecraft:infinity":1},' + UNB + ']',
              'item replace entity @s hotbar.1 with minecraft:stone_sword[' + UNB + ']', 'item replace entity @s hotbar.2 with minecraft:cooked_beef 4',
              'item replace entity @s inventory.0 with minecraft:arrow 1'],
}
for m, k, *_ in BMODES:
    fn(f'{_K}/kit_{k}', ['clear @s', 'effect clear @s', 'attribute @s minecraft:max_health base set 20',
                         'effect give @s minecraft:instant_health 1 10 true', 'effect give @s minecraft:saturation 1 20 true', 'gamemode adventure @s',
                         'effect give @s minecraft:slowness 3 255 true', 'effect give @s minecraft:weakness 3 255 true', 'effect give @s minecraft:resistance 3 4 true',
                         *KIT_B[k]])
    fn(f'{_K}/build_{k}', ['fill ~-20 ~-6 ~-20 ~20 ~12 ~20 minecraft:air', *ARENA_B[k]])
    for d, *_ in DIFFS:
        fn(f'{_K}/mob_{m}{d}', [summon_cmd(m, d), *(['effect give @e[tag=mg_botm_new,distance=..40] minecraft:resistance infinite 4 true'] if SPEC[(m, d)].get('res') else [])])

# ------------------------------------------------------------------ menu
def _btn(m, d):
    dn, dc = DN[d], DC[d]
    coins = DIFFS[d - 1][4]
    return [{'text': ' '}, {'text': f'[{dn}]', 'color': dc, 'bold': d == 4,
             'click_event': {'action': 'run_command', 'command': f'/trigger mg_aktion set {200 + m * 10 + d}'},
             'hover_event': {'action': 'show_text', 'value': [{'text': f'{MN[m]} · {dn}\n', 'color': dc, 'bold': True},
                                                                {'text': f'Best of 3 · Sieg: {coins} ' + ('Münze' if coins == 1 else 'Münzen'), 'color': 'gray', 'bold': False}]}},
            {'nbt': f'c.a{m}{d}', 'storage': f'{NS}:bot', 'interpret': True, 'color': 'green', 'bold': False}]


menu = ['data remove storage mg:bot c',
        *[f'execute if entity @s[tag=mg_botw_{m}{d}] run data modify storage {NS}:bot c.a{m}{d} set value "✔"' for m, *_ in BMODES for d, *_ in DIFFS],
        'scoreboard players set #bot_free mg 0',
        *[f'execute if score #bot_s{i} mg matches 0 run scoreboard players add #bot_free mg 1' for i in range(1, _NS + 1)],
        f'scoreboard players set #bot_room mg {_CAP}', 'scoreboard players operation #bot_room mg -= @s mg_bot_cc',
        'execute if score #bot_room mg matches ..-1 run scoreboard players set #bot_room mg 0',
        f'tellraw @s {msg(_bt("Bot-Duelle", "dark_green", bold=True), _bt(" – 1v1 gegen einen Bot. Modus + Stufe anklicken:", "gray"))}']
for m, k, name, color, desc, *_ in BMODES:
    row = [{'text': '  '}, {'text': name, 'color': color, 'bold': True, 'hover_event': {'action': 'show_text', 'value': desc}},
           {'text': ' ', 'bold': False}]
    for d, *_ in DIFFS:
        row += _btn(m, d)
    menu.append(f'tellraw @s {tc(row)}')
menu += [f'tellraw @s {tc([{"text": "  Sieg: ", "color": "gray"}, {"text": "1", "color": "green"}, {"text": " / ", "color": "gray"}, {"text": "2", "color": "yellow"}, {"text": " / ", "color": "gray"}, {"text": "3", "color": "red"}, {"text": " / ", "color": "gray"}, {"text": "5", "color": "dark_purple"}, {"text": " Münzen · noch ", "color": "gray"}, {"score": {"name": "#bot_room", "objective": "mg"}, "color": "yellow"}, {"text": f" bis zum Limit ({_CAP}/h) · ", "color": "gray"}, {"text": "✔", "color": "green"}, {"text": " = geschafft", "color": "gray"}])}',
         f'tellraw @s {tc([{"text": "  Freie Arenen: ", "color": "gray"}, {"score": {"name": "#bot_free", "objective": "mg"}, "color": "white"}, {"text": f"/{_NS}", "color": "gray"}])}']
fn(f'{_K}/menu', menu)

# ------------------------------------------------------------------ start: pick -> claim slot -> loading -> begin -> round
fn(f'{_K}/pick', [   # as a hub player, mg_aktion = 200 + mode*10 + diff
    'scoreboard players operation #bot_m mg = @s mg_aktion', 'scoreboard players remove #bot_m mg 200',
    'scoreboard players operation #bot_d mg = #bot_m mg', 'scoreboard players operation #bot_d mg %= #10 mg', 'scoreboard players operation #bot_m mg /= #10 mg',
    f'execute unless score #bot_m mg matches 1..{len(BMODES)} run return 0', 'execute unless score #bot_d mg matches 1..4 run return 0',
    'execute store result score #bot_dif mg run difficulty',
    f'execute if score #bot_dif mg matches 0 run return run tellraw @s {msg(_bt("Bot-Duelle gehen nicht, solange der Server auf Friedlich steht.", "red"))}',
    *[f'execute if score #bot_s{i} mg matches 0 run return run function {NS}:{_K}/claim{i}' for i in range(1, _NS + 1)],
    f'tellraw @s {msg(_bt("Alle Bot-Arenen sind gerade belegt – versuch es gleich nochmal.", "red"))}',
])
for i in range(1, _NS + 1):
    x = _SX(i)
    fn(f'{_K}/claim{i}', [
        f'function {NS}:q/leave_all',
        'scoreboard players add #bot_id mg 1', 'scoreboard players operation @s mg_bot_id = #bot_id mg',
        f'scoreboard players set #bot_s{i} mg 1', f'scoreboard players operation #bot_o{i} mg = #bot_id mg',
        f'scoreboard players set @s mg_bot_sl {i}',
        'scoreboard players operation @s mg_bot_md = #bot_m mg', 'scoreboard players operation @s mg_bot_df = #bot_d mg',
        'scoreboard players set @s mg_bot_p 0', 'scoreboard players set @s mg_bot_b 0', 'scoreboard players set @s mg_bot_st 4', 'scoreboard players set @s mg_bot_t 0',
        f'{OW} forceload add {x - 24} -24 {x + 24} 24',
        f'tag @s remove mg_hub', f'tag @s add {_T}', 'clear @s', 'effect clear @s',
        'effect give @s minecraft:resistance 10 4 true',
        f'title @s actionbar {tc(_bt("Arena wird vorbereitet …", "gray"))}',
    ])
    fn(f'{_K}/free{i}', [   # as anyone: removes the slot's mob/items, frees the slot
        f'execute in minecraft:overworld positioned {x}.5 {Y} 0.5 run kill @e[tag={_M},distance=..90]',
        f'execute in minecraft:overworld positioned {x}.5 {Y} 0.5 run kill @e[type=minecraft:item,distance=..90]',
        f'execute in minecraft:overworld positioned {x}.5 {Y} 0.5 run kill @e[type=#minecraft:arrows,distance=..90]',
        f'execute in minecraft:overworld positioned {x}.5 {Y} 0.5 run kill @e[type=minecraft:experience_orb,distance=..90]',
        f'{OW} forceload remove {x - 24} -24 {x + 24} 24',
        f'scoreboard players set #bot_s{i} mg 0', f'scoreboard players set #bot_o{i} mg 0',
    ])

# as the player, positioned at the slot origin (block centre)
fn(f'{_K}/loading', [
    f'execute if loaded ~-20 ~ ~-20 if loaded ~20 ~ ~20 if loaded ~-20 ~ ~20 if loaded ~20 ~ ~-20 run return run function {NS}:{_K}/begin',
    f'execute if score @s mg_bot_t matches 200.. run tellraw @s {msg(_bt("Die Arena konnte nicht geladen werden – versuch es nochmal.", "red"))}',
    f'execute if score @s mg_bot_t matches 200.. run function {NS}:hub/enter',
])
fn(f'{_K}/begin', [
    f'kill @e[tag={_M},distance=..90]', 'kill @e[type=minecraft:item,distance=..90]', 'kill @e[type=#minecraft:arrows,distance=..90]',
    *[f'execute if score @s mg_bot_md matches {m} run function {NS}:{_K}/build_{k}' for m, k, *_ in BMODES],
    *[f'execute if score @s mg_bot_md matches {m} if score @s mg_bot_df matches {d} run tellraw @s {msg(_bt(MN[m], MCOL[m], bold=True), _bt(" gegen ", "gray"), _bt("Bot · " + DN[d], DC[d], bold=True), _bt(" – Best of 3. ", "gray"), _bt("[Aufgeben]", "red", click_event={"action": "run_command", "command": "/trigger mg_aktion set 99"}))}'
      for m, *_ in BMODES for d, *_ in DIFFS],
    *[f'execute if score @s mg_bot_md matches 2 if score @s mg_bot_df matches {d} run scoreboard players set @s mg_bot_nd {BOX_BOT[d]}' for d, *_ in DIFFS],
    f'execute if score @s mg_bot_md matches 2 run tellraw @s {msg(_bt(f"Du brauchst {BOX_PLAYER} Treffer, der Bot ", "gray"), {"score": {"name": "@s", "objective": "mg_bot_nd"}, "color": "white"}, _bt(".", "gray"))}',
    f'function {NS}:{_K}/round',
])
fn(f'{_K}/round', [
    f'kill @e[tag={_M},distance=..90]', 'kill @e[type=minecraft:item,distance=..90]', 'kill @e[type=#minecraft:arrows,distance=..90]',
    'scoreboard players set @s mg_bot_st 1', 'scoreboard players set @s mg_bot_t 0',
    'scoreboard players set @s mg_deaths 0', 'scoreboard players set @s mg_bot_hp 0', 'scoreboard players set @s mg_bot_hb 0',
    'scoreboard players set @s mg_bot_dd 0', 'scoreboard players set @s mg_bot_dt 0',
    *[f'execute if score @s mg_bot_md matches {m} run function {NS}:{_K}/kit_{k}' for m, k, *_ in BMODES],
    *[f'execute if score @s mg_bot_md matches {m} run tp @s ~{px} ~1 ~ {pyaw} 0' for m, _, _, _, _, (px, pyaw), _ in BMODES],
    f'{OW} spawnpoint @s {SPAWN[0]} {SPAWN[1]} {SPAWN[2]}',
    *[f'execute if score @s mg_bot_md matches {m} if score @s mg_bot_df matches {d} run function {NS}:{_K}/mob_{m}{d}' for m, *_ in BMODES for d, *_ in DIFFS],
    f'scoreboard players operation @e[tag={_M}_new,distance=..40] mg_bot_id = @s mg_bot_id', f'tag @e[tag={_M}_new,distance=..40] remove {_M}_new',
    'scoreboard players operation #bot_rn mg = @s mg_bot_p', 'scoreboard players operation #bot_rn mg += @s mg_bot_b', 'scoreboard players add #bot_rn mg 1',
    'title @s times 0 30 10',
    f'title @s title [{tc(_bt("Runde ", "gold", bold=True))},{{"score":{{"name":"#bot_rn","objective":"mg"}},"color":"gold","bold":true}}]',
    f'title @s subtitle [{tc(_bt("Du ", "gray"))},{{"score":{{"name":"@s","objective":"mg_bot_p"}},"color":"white","bold":true}},{tc(_bt(" : ", "gray"))},{{"score":{{"name":"@s","objective":"mg_bot_b"}},"color":"white","bold":true}},{tc(_bt(" Bot", "gray"))}]',
])
fn(f'{_K}/go', [
    'scoreboard players set @s mg_bot_st 2', 'scoreboard players set @s mg_bot_t 0',
    f'execute as @e[tag={_M},distance=..90] run data merge entity @s {{NoAI:0b,Invulnerable:0b}}',
    'effect clear @s minecraft:slowness', 'effect clear @s minecraft:weakness',
    'scoreboard players set @s mg_bot_dd 0', 'scoreboard players set @s mg_bot_dt 0',
    f'title @s actionbar {tc(_bt("LOS!", "green", bold=True))}', 'playsound minecraft:block.note_block.pling master @s ~ ~ ~ 1 2',
])
_SCORE = [_bt("Du ", "gray"), {"score": {"name": "@s", "objective": "mg_bot_p"}, "color": "white", "bold": True}, _bt(" : ", "gray"),
          {"score": {"name": "@s", "objective": "mg_bot_b"}, "color": "white", "bold": True}, _bt(" Bot", "gray")]
fn(f'{_K}/boxhits', [
    'execute if score @s mg_bot_dd matches 1.. run scoreboard players add @s mg_bot_hp 1', 'scoreboard players set @s mg_bot_dd 0',
    'execute if score @s mg_bot_dt matches 1.. run scoreboard players add @s mg_bot_hb 1', 'scoreboard players set @s mg_bot_dt 0',
    f'title @s actionbar {tc([_bt("Treffer  Du ", "gray"), {"score": {"name": "@s", "objective": "mg_bot_hp"}, "color": "white", "bold": True}, _bt(f"/{BOX_PLAYER}", "gray"), _bt("   Bot ", "gray"), {"score": {"name": "@s", "objective": "mg_bot_hb"}, "color": "white", "bold": True}, _bt("/", "gray"), {"score": {"name": "@s", "objective": "mg_bot_nd"}, "color": "gray"}])}',
    f'execute if score @s mg_bot_hp matches {BOX_PLAYER}.. run return run function {NS}:{_K}/r_player',
    f'execute if score @s mg_bot_hb >= @s mg_bot_nd run return run function {NS}:{_K}/r_bot',
])
fn(f'{_K}/fight', [
    f'execute if score @s mg_deaths matches 1.. run return run function {NS}:{_K}/r_bot',
    f'execute at @s if entity @s[y=-64,dy={_FALL_DY}] run return run function {NS}:{_K}/r_bot',
    f'execute as @e[tag={_M},distance=..90] at @s if entity @s[y=-64,dy={_FALL_DY}] run kill @s',
    f'execute unless entity @e[tag={_M},distance=..90] run return run function {NS}:{_K}/nomob',
    f'execute if score @s mg_bot_t matches 600 run effect give @e[tag={_M},distance=..90] minecraft:glowing infinite 0 true',
    f'execute if score @s mg_bot_t matches {_ROUND_MAX}.. run return run function {NS}:{_K}/draw',
    f'execute if score @s mg_bot_md matches 2 run return run function {NS}:{_K}/boxhits',
    'scoreboard players operation #bot_m20 mg = @s mg_bot_t', 'scoreboard players operation #bot_m20 mg %= #20 mg',
    f'execute if score #bot_m20 mg matches 0 run title @s actionbar {tc(_SCORE)}',
])
fn(f'{_K}/nomob', [   # the bot is gone: killed / fallen = round won; despawned because the server was set to Friedlich = match aborted
    'execute store result score #bot_dif mg run difficulty',
    f'execute if score #bot_dif mg matches 0 run tellraw @s {msg(_bt("Der Server steht auf Friedlich – das Bot-Duell wurde abgebrochen.", "red"))}',
    f'execute if score #bot_dif mg matches 0 run return run function {NS}:hub/enter',
    f'function {NS}:{_K}/r_player',
])
fn(f'{_K}/draw', [f'tellraw @s {msg(_bt("Zeit um – die Runde wird wiederholt.", "gray"))}', f'function {NS}:{_K}/round'])
fn(f'{_K}/freeze', [
    'execute if score @s mg_bot_t matches 1 run title @s actionbar {"text":"3","color":"red","bold":true}',
    'execute if score @s mg_bot_t matches 20 run title @s actionbar {"text":"2","color":"gold","bold":true}',
    'execute if score @s mg_bot_t matches 40 run title @s actionbar {"text":"1","color":"yellow","bold":true}',
    *[f'execute if score @s mg_bot_t matches {t} run playsound minecraft:block.note_block.hat master @s ~ ~ ~ 1 1' for t in (1, 20, 40)],
    f'execute if score @s mg_bot_t matches 60.. run function {NS}:{_K}/go',
])
fn(f'{_K}/stick', [   # as the player at the slot origin, every tick
    'scoreboard players add @s mg_bot_t 1',
    'kill @e[type=minecraft:item,distance=..90]', 'kill @e[type=minecraft:experience_orb,distance=..90]',
    f'execute if score @s mg_bot_st matches 4 run return run function {NS}:{_K}/loading',
    f'execute if score @s mg_bot_st matches 1 run return run function {NS}:{_K}/freeze',
    f'execute if score @s mg_bot_st matches 2 run return run function {NS}:{_K}/fight',
    f'execute if score @s mg_bot_st matches 3 if score @s mg_bot_t matches 50.. run function {NS}:hub/enter',
])
fn(f'{_K}/ptick', [f'execute if score @s mg_bot_sl matches {i} in minecraft:overworld positioned {_SX(i)}.5 {Y} 0.5 run return run function {NS}:{_K}/stick'
                   for i in range(1, _NS + 1)])

# ------------------------------------------------------------------ round / match results
fn(f'{_K}/r_player', [
    'scoreboard players add @s mg_bot_p 1',
    f'tellraw @s {msg(_bt("Runde an dich! ", "green", bold=True), *_SCORE)}',
    'playsound minecraft:entity.experience_orb.pickup master @s ~ ~ ~ 1 1',
    f'execute if score @s mg_bot_p matches 2.. run return run function {NS}:{_K}/win',
    f'function {NS}:{_K}/round',
])
fn(f'{_K}/r_bot', [
    'scoreboard players add @s mg_bot_b 1',
    f'tellraw @s {msg(_bt("Runde an den Bot. ", "red", bold=True), *_SCORE)}',
    'playsound minecraft:entity.villager.no master @s ~ ~ ~ 1 1',
    f'execute if score @s mg_bot_b matches 2.. run return run function {NS}:{_K}/lose',
    f'function {NS}:{_K}/round',
])
fn(f'{_K}/ending', [
    'scoreboard players set @s mg_bot_st 3', 'scoreboard players set @s mg_bot_t 0',
    f'kill @e[tag={_M},distance=..90]', 'effect give @s minecraft:resistance 5 4 true', 'effect give @s minecraft:weakness 5 255 true',
    'scoreboard players set @s mg_deaths 0', 'title @s times 5 50 15',
])
def _again(won):   # chat buttons after a match: again, next harder (after a win) / easier (after a loss), bot menu
    out = []
    for m, *_ in BMODES:
        for d, *_ in DIFFS:
            nd = d + 1 if won else d - 1
            nxt = [{'text': f'[{DN[nd]} probieren]', 'color': DC[nd],
                    'click_event': {'action': 'run_command', 'command': f'/trigger mg_aktion set {200 + m * 10 + nd}'}}, {'text': '  '}] if 1 <= nd <= 4 else []
            out.append(f'execute if score @s mg_bot_md matches {m} if score @s mg_bot_df matches {d} run tellraw @s ' + tc([{'text': '  '},
                       {'text': '[Nochmal]', 'color': 'green', 'click_event': {'action': 'run_command', 'command': f'/trigger mg_aktion set {200 + m * 10 + d}'}},
                       {'text': '  '}, *nxt,
                       {'text': '[Bot-Menü]', 'color': 'dark_green', 'click_event': {'action': 'run_command', 'command': f'/trigger mg_aktion set {_TRIG}'}}]))
    return out


fn(f'{_K}/again_w', _again(True))
fn(f'{_K}/again_l', _again(False))
fn(f'{_K}/win', [
    f'function {NS}:{_K}/ending',
    # coins: 1/2/3/5 by difficulty, capped by the refilling allowance mg_bot_cc
    *[f'execute if score @s mg_bot_df matches {d} run scoreboard players set #bot_r mg {c}' for d, _, _, _, c in DIFFS],
    f'scoreboard players set #bot_room mg {_CAP}', 'scoreboard players operation #bot_room mg -= @s mg_bot_cc',
    'scoreboard players operation #bot_r mg < #bot_room mg', 'execute if score #bot_r mg matches ..-1 run scoreboard players set #bot_r mg 0',
    'scoreboard players operation @s mg_coins += #bot_r mg', 'scoreboard players operation @s mg_bot_cc += #bot_r mg',
    # first win on this mode/difficulty?
    'scoreboard players set #bot_new mg 0',
    *[f'execute if score @s mg_bot_md matches {m} if score @s mg_bot_df matches {d} unless entity @s[tag=mg_botw_{m}{d}] run scoreboard players set #bot_new mg 1' for m, *_ in BMODES for d, *_ in DIFFS],
    *[f'execute if score @s mg_bot_md matches {m} if score @s mg_bot_df matches {d} run tag @s add mg_botw_{m}{d}' for m, *_ in BMODES for d, *_ in DIFFS],
    f'title @s title {tc(_bt("SIEG!", "gold", bold=True))}',
    *[f'execute if score @s mg_bot_df matches {d} run title @s subtitle {tc([_bt("gegen ", "gray"), _bt("Bot · " + DN[d], DC[d], bold=True)])}' for d, *_ in DIFFS],
    *[f'execute if score @s mg_bot_md matches {m} if score @s mg_bot_df matches {d} run tellraw @s {msg(_bt("Gewonnen! ", "gold", bold=True), _bt(MN[m] + " gegen ", "gray"), _bt("Bot · " + DN[d], DC[d], bold=True), _bt(" – ", "gray"), {"score": {"name": "@s", "objective": "mg_bot_p"}, "color": "white"}, _bt(":", "gray"), {"score": {"name": "@s", "objective": "mg_bot_b"}, "color": "white"})}'
      for m, *_ in BMODES for d, *_ in DIFFS],
    f'execute if score #bot_r mg matches 1 run tellraw @s {msg(_bt("+1 Münze", "yellow"))}',
    f'execute if score #bot_r mg matches 2.. run tellraw @s {msg(_bt("+", "yellow"), {"score": {"name": "#bot_r", "objective": "mg"}, "color": "yellow"}, _bt(" Münzen", "yellow"))}',
    f'execute if score #bot_r mg matches 0 run tellraw @s {msg(_bt(f"Keine Münzen – dein Bot-Limit ({_CAP} pro Stunde) ist erreicht. Es füllt sich langsam wieder auf.", "gray"))}',
    f'execute if score #bot_new mg matches 1 run tellraw @s {msg(_bt("✔ Neue Stufe geschafft!", "green", bold=True))}',
    *[f'execute if score @s mg_bot_df matches 4 if score @s mg_bot_md matches {m} run tellraw @a[tag=mg_hub] {msg({"selector": "@s", "color": "white"}, _bt(" hat den ", "gray"), _bt("Extrem-Bot", "dark_purple", bold=True), _bt(" in " + MN[m] + " besiegt!", "gray"))}' for m, *_ in BMODES],
    'execute at @s run summon minecraft:firework_rocket ~ ~1 ~ {LifeTime:20,FireworksItem:{id:"minecraft:firework_rocket",count:1,components:{"minecraft:fireworks":{flight_duration:1,explosions:[{shape:"star",colors:[I;5635925,16766720],has_twinkle:true}]}}}}',
    'playsound minecraft:ui.toast.challenge_complete master @s ~ ~ ~ 1 1.2',
    f'function {NS}:{_K}/again_w',
])
fn(f'{_K}/lose', [
    f'function {NS}:{_K}/ending',
    f'title @s title {tc(_bt("Verloren", "red", bold=True))}',
    f'title @s subtitle {tc(_bt("Der Bot war diesmal besser", "gray"))}',
    *[f'execute if score @s mg_bot_md matches {m} if score @s mg_bot_df matches {d} run tellraw @s {msg(_bt("Verloren: ", "red", bold=True), _bt(MN[m] + " gegen ", "gray"), _bt("Bot · " + DN[d], DC[d], bold=True), _bt(" – ", "gray"), {"score": {"name": "@s", "objective": "mg_bot_p"}, "color": "white"}, _bt(":", "gray"), {"score": {"name": "@s", "objective": "mg_bot_b"}, "color": "white"})}'
      for m, *_ in BMODES for d, *_ in DIFFS],
    'playsound minecraft:entity.wither.ambient master @s ~ ~ ~ 0.4 1.5',
    f'function {NS}:{_K}/again_l',
])

# ------------------------------------------------------------------ leaving / cleanup / watchdog
fn(f'{_K}/cleanup', [   # as the player (from hub/enter via ENTER_LINES): frees the slot only if it still belongs to this match
    *[f'execute if score @s mg_bot_sl matches {i} if score #bot_o{i} mg = @s mg_bot_id run function {NS}:{_K}/free{i}' for i in range(1, _NS + 1)],
    f'tag @s remove {_T}', 'scoreboard players set @s mg_bot_sl 0', 'scoreboard players set @s mg_bot_st 0',
])
fn(f'{_K}/mobcheck', [   # as a bot mob: remove it unless its match is still running
    'scoreboard players set #bot_q mg -1', 'scoreboard players operation #bot_q mg = @s mg_bot_id',
    f'execute as @a[tag={_T}] if score @s mg_bot_id = #bot_q mg run return 0',
    'kill @s',
])
ENTER_LINES.extend([f'execute if entity @s[tag={_T}] run function {NS}:{_K}/cleanup', f'tag @s remove {_T}'])
WATCHDOG.extend([
    *[f'execute if score #bot_s{i} mg matches 1.. unless entity @a[tag={_T},scores={{mg_bot_sl={i}}}] run function {NS}:{_K}/free{i}' for i in range(1, _NS + 1)],
    *[f'execute as @a[tag={_T},scores={{mg_bot_sl={i}}}] unless score @s mg_bot_id = #bot_o{i} mg run function {NS}:hub/enter' for i in range(1, _NS + 1)],
    f'execute as @a[tag={_T}] unless score @s mg_bot_sl matches 1..{_NS} run function {NS}:hub/enter',
    f'execute as @e[tag={_M}] run function {NS}:{_K}/mobcheck',
])
EXTRA_TICK.extend([
    f'execute as @e[type=minecraft:player,tag={_T}] run function {NS}:{_K}/ptick',
    'scoreboard players add #bot_dec mg 1',
    f'execute if score #bot_dec mg matches {_DEC}.. run scoreboard players remove @a[scores={{mg_bot_cc=1..}}] mg_bot_cc 1',
    f'execute if score #bot_dec mg matches {_DEC}.. run scoreboard players set #bot_dec mg 0',
])
EXTRA_LOAD.extend([
    *[f'scoreboard objectives add mg_bot_{o} dummy' for o in ('sl', 'md', 'df', 'p', 'b', 'st', 't', 'id', 'cc', 'hp', 'hb', 'nd')],
    'scoreboard objectives add mg_bot_dd minecraft.custom:minecraft.damage_dealt',
    'scoreboard objectives add mg_bot_dt minecraft.custom:minecraft.damage_taken',
    'scoreboard players set #10 mg 10', 'scoreboard players set #20 mg 20',
    'execute unless score #bot_id mg matches 0.. run scoreboard players set #bot_id mg 0',
    *[f'execute unless score #bot_s{i} mg matches 0.. run scoreboard players set #bot_s{i} mg 0' for i in range(1, _NS + 1)],
    f'execute as @e[tag={_M}] run function {NS}:{_K}/mobcheck',
    # load.mcfunction starts with "forceload remove all": re-add the slots of running matches
    *[f'execute if score #bot_s{i} mg matches 1.. run {OW} forceload add {_SX(i) - 24} -24 {_SX(i) + 24} 24' for i in range(1, _NS + 1)],
])
AKTION_EXTRA.extend([   # the buttons after a match appear while the player is still in the arena (state 3): let them work right away
    f'execute if score @s mg_aktion matches 211..{200 + len(BMODES) * 10 + 4} if entity @s[tag={_T},scores={{mg_bot_st=3}}] run function {NS}:hub/enter',
    f'execute if score @s mg_aktion matches {_TRIG} if entity @s[tag={_T},scores={{mg_bot_st=3}}] run function {NS}:{_K}/menu',
    f'execute if score @s mg_aktion matches 211..{200 + len(BMODES) * 10 + 4} if entity @s[tag=mg_hub] run function {NS}:{_K}/pick'])
register_game(_K, 'Bot-Duelle', 'dark_green', 'nitwit', _TRIG, f'function {NS}:{_K}/menu', '1v1 gegen Bots · 4 Stufen', '1v1 gegen Bots, 4 Stufen, alleine spielbar')
INFO.append(('Bot-Duelle', 'dark_green', 'Spiel alleine 1v1 gegen einen Bot: Schwert-Duell, Boxen, Sumo, Knockback oder Bogen, jeweils in 4 Stufen '
             '(Leicht, Mittel, Schwer, Extrem). Best of 3 – wer zuerst 2 Runden holt. Du verlierst eine Runde, wenn du stirbst oder runterfällst, '
             f'und gewinnst sie, wenn der Bot stirbt oder runterfällt (Boxen: zuerst {BOX_PLAYER} Treffer). Siege geben 1/2/3/5 Münzen '
             f'(höchstens {_CAP} pro Stunde), zählen aber nicht in der Siege-Liste. Geschaffte Stufen bekommen ein ✔. Aufgeben: /trigger mg_aktion set 99.'))
# 1v1 menu: link to the bot menu
files[f'data/{NS}/function/q/menu.mcfunction'] += f'tellraw @s {tc([{"text": "  Keinen Gegner? ", "color": "gray"}, {"text": "[Gegen Bot spielen]", "color": "dark_green", "bold": True, "click_event": {"action": "run_command", "command": f"/trigger mg_aktion set {_TRIG}"}, "hover_event": {"action": "show_text", "value": "1v1 gegen einen Bot – 4 Stufen"}}])}\n'
# stats menu: best beaten difficulty per mode
_pb = ['scoreboard players set #bot_any mg 0', *[f'execute if entity @s[tag=mg_botw_{m}{d}] run scoreboard players set #bot_any mg 1' for m, *_ in BMODES for d, *_ in DIFFS]]
for m, *_ in BMODES:
    _pb.append(f'data modify storage {NS}:bot b.m{m} set value "–"')
    _pb += [f'execute if entity @s[tag=mg_botw_{m}{d}] run data modify storage {NS}:bot b.m{m} set value "{DN[d]}"' for d, *_ in DIFFS]
_row = [{'text': '   Bot-Duelle (beste Stufe): ', 'color': 'gray'}]
for j, (m, *_r) in enumerate(BMODES):
    _row += [{'text': MN[m] + ' ', 'color': MCOL[m]}, {'nbt': f'b.m{m}', 'storage': f'{NS}:bot', 'interpret': True, 'color': 'white'}]
    if j < len(BMODES) - 1:
        _row.append({'text': ' · ', 'color': 'dark_gray'})
_pb.append(f'execute if score #bot_any mg matches 1 run tellraw @s {tc(_row)}')
PB_MENU.extend(_pb)
