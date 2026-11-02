# modules/info.py – Infos: HUD (Actionbar), Stats, Top-Liste, Online-Liste, Position teilen, AFK-Erkennung, Schlaf-Hinweis.
#
# Trigger (Kategorie "Infos"): hud (an/aus, Esc-Menue), stats (Esc-Menue), top, online, pos
# Objectives: smp_tode (Todes-Zaehler) und smp_mkills (mob_kills) kommen aus dem Kern (core/death zaehlt +1),
#             Stats: smp_pkills (player_kills), smp_walk (walk_one_cm), smp_sprint (sprint_one_cm), smp_jump (jump),
#                    smp_sleep (sleep_in_bed; wird nach dem Auswerten auf 0 gesetzt)
#             AFK:   smp_afk_x/y/z (letzte Blockposition), smp_afk_r (Blickrichtung: yaw*1000+pitch), smp_afk_t (Sekunden ohne Bewegung)
#             Anzeige: smp_inf_hh / smp_inf_hd (Spielzeit in Stunden / Zehntel), Cooldown smp_cd_pos
# Tags: smp_hud (HUD an), smp_afk (ist AFK), smp_top + smp_top_1..5 (Ranking-Scratch), smp_inf_v (Betrachter-Scratch)
# Team: smp_afk (Suffix " [AFK]", grau). Spieler sind nur waehrend AFK drin; angefasst werden nur Spieler ohne Team bzw. im Team smp_afk.
# Scores (Objective smp): #afk_s = AFK-Schwelle in Sekunden (Standard 300, bleibt bei /reload erhalten: zum Testen z.B. auf 10 setzen),
#          #inf_t (Tick-Zaehler 0..9), #inf_afk (10-s-Zaehler), #sleep_cd (globaler Cooldown des Schlaf-Hinweises), #inf_* Scratch
# Storage: smp:tmp hud {dim:{text}, dir:{text}} (Scratch fuer die Textbausteine, als Text-Compounds) – keine persistenten Daten.
_C = 'Infos'
_AFK_DEFAULT, _SLEEP_CD, _POS_CD = 300, 20, 5
_DIRS = ['N', 'NO', 'O', 'SO', 'S', 'SW', 'W', 'NW']       # Index = ((yaw*10 + 1800 + 225) mod 3600) / 450  (yaw 180 = Norden, -90 = Osten)


def _sc(name, obj='smp', color='white'):
    return {'score': {'name': name, 'objective': obj}, 'color': color}


def _t(text, color='gray'):
    return {'text': text, 'color': color}


_SEL = {'selector': '@s', 'color': 'yellow'}


def _NBT(path, color):
    """Textbaustein aus storage smp:tmp <path> (dort liegt ein Text-Compound {text:"..."}; interpret zeigt ihn ohne Anfuehrungszeichen)"""
    return {'nbt': path, 'storage': 'smp:tmp', 'interpret': True, 'color': color}

# ---------------------------------------------------------------- Objectives, Team, Konstanten
EXTRA_LOAD += [
    'scoreboard objectives add smp_pkills minecraft.custom:minecraft.player_kills',
    'scoreboard objectives add smp_walk minecraft.custom:minecraft.walk_one_cm',
    'scoreboard objectives add smp_sprint minecraft.custom:minecraft.sprint_one_cm',
    'scoreboard objectives add smp_jump minecraft.custom:minecraft.jump',
    'scoreboard objectives add smp_sleep minecraft.custom:minecraft.sleep_in_bed',
    *[f'scoreboard objectives add {o} dummy' for o in ('smp_afk_x', 'smp_afk_y', 'smp_afk_z', 'smp_afk_r', 'smp_afk_t', 'smp_inf_hh', 'smp_inf_hd')],
    'team add smp_afk',
    f'team modify smp_afk suffix {tc({"text": " [AFK]", "color": "gray"})}',
    'team modify smp_afk color gray',
    *[f'scoreboard players set #{n} smp {n}' for n in (10, 24, 360, 450, 1000, 3600, 7200, 10000)],
    f'execute unless score #afk_s smp matches 1.. run scoreboard players set #afk_s smp {_AFK_DEFAULT}',
    'scoreboard players set #inf_t smp 0', 'scoreboard players set #inf_afk smp 0', 'scoreboard players set #sleep_cd smp 0',
    'data modify storage smp:tmp hud set value {dim:{text:"?"},dir:{text:"?"}}',
]
cooldown('smp_cd_pos')

# ---------------------------------------------------------------- Tick-Jobs
EXTRA_TICK += [
    'scoreboard players add #inf_t smp 1',
    f'execute if score #inf_t smp matches 10.. run function {NS}:info/t10',
]
EXTRA_SECOND += [
    f'execute as @a[scores={{smp_sleep=1..}}] run function {NS}:info/sleep',
    'execute if score #sleep_cd smp matches 1.. run scoreboard players remove #sleep_cd smp 1',
    'scoreboard players add #inf_afk smp 1',
    f'execute if score #inf_afk smp matches 10.. run function {NS}:info/afk10',
]
ON_JOIN.append(f'function {NS}:info/join')
ON_REJOIN.append(f'function {NS}:info/join')
fn('info/join', [           # nach einem Relog nie als AFK starten (Tag + Team sind persistent)
    'scoreboard players set @s smp_afk_t 0',
    'tag @s remove smp_afk',
    'execute if entity @s[team=smp_afk] run team leave @s',
    *[f'scoreboard players add @s {o} 0' for o in ('smp_tode', 'smp_mkills', 'smp_pkills', 'smp_walk', 'smp_sprint', 'smp_jump')],
])

# ---------------------------------------------------------------- HUD: /trigger hud (Actionbar alle 10 Ticks)
trigger('hud', f'{NS}:info/hud_toggle', '/trigger hud', 'Koordinaten, Richtung und Uhrzeit als HUD an/aus', _C,
        ('HUD an/aus', 'Koordinaten, Himmelsrichtung und Uhrzeit in der Actionbar'))
fn('info/hud_toggle', [
    f'execute if entity @s[tag=smp_hud] run return run function {NS}:info/hud_off',
    'tag @s add smp_hud',
    f'function {NS}:info/clock',
    f'execute at @s run function {NS}:info/hud',
    'tellraw @s ' + msg(_t('HUD an. ', 'green'), _t('Nochmal '), clk('/trigger hud', '/trigger hud', 'yellow', 'HUD ausschalten'), _t(' schaltet es aus.')),
])
fn('info/hud_off', ['tag @s remove smp_hud', 'title @s actionbar ""', 'tellraw @s ' + msg(_t('HUD aus.', 'green'))])
fn('info/t10', [
    'scoreboard players set #inf_t smp 0',
    f'execute if entity @a[tag=smp_hud] run function {NS}:info/clock',
    f'execute as @a[tag=smp_hud] at @s unless score @s smp_wu matches 1.. run function {NS}:info/hud',     # nicht waehrend eines Teleport-Warmups (dessen Actionbar hat Vorrang)
])
fn('info/clock', [          # Uhrzeit hh:mm aus der Tageszeit: h = (dt/1000 + 6) mod 24, m = (dt mod 1000) * 60 / 1000  -> Ziffern #inf_h10 #inf_h1 #inf_m10 #inf_m1
    'execute store result score #inf_dt smp run time query minecraft:day',       # 26.x: Tageszeit = Position der Timeline minecraft:day (0..23999)
    'scoreboard players operation #inf_h smp = #inf_dt smp', 'scoreboard players operation #inf_h smp /= #1000 smp',
    'scoreboard players add #inf_h smp 6', 'scoreboard players operation #inf_h smp %= #24 smp',
    'scoreboard players operation #inf_m smp = #inf_dt smp', 'scoreboard players operation #inf_m smp %= #1000 smp',
    'scoreboard players operation #inf_m smp *= #60 smp', 'scoreboard players operation #inf_m smp /= #1000 smp',
    'scoreboard players operation #inf_h10 smp = #inf_h smp', 'scoreboard players operation #inf_h10 smp /= #10 smp',
    'scoreboard players operation #inf_h1 smp = #inf_h smp', 'scoreboard players operation #inf_h1 smp %= #10 smp',
    'scoreboard players operation #inf_m10 smp = #inf_m smp', 'scoreboard players operation #inf_m10 smp /= #10 smp',
    'scoreboard players operation #inf_m1 smp = #inf_m smp', 'scoreboard players operation #inf_m1 smp %= #10 smp',
])
fn('info/dimname', ['data modify storage smp:tmp hud.dim set value {text:"?"}',      # unbekannte (Mod-)Dimension -> "?" statt dem Wert des vorigen Spielers
                    *[f'execute if dimension {d} run data modify storage smp:tmp hud.dim set value {{text:"{name}"}}' for d, name, _ in DIMS]])
fn('info/blockpos', [       # Blockkoordinaten von @s -> #inf_x #inf_y #inf_z (data get rundet ab, auch bei negativen Werten)
    *[f'execute store result score #inf_{a} smp run data get entity @s Pos[{i}]' for i, a in enumerate('xyz')],
])
fn('info/direction', [      # Himmelsrichtung aus der Blickrichtung (Rotation[0] = yaw) -> storage smp:tmp hud.dir
    'execute store result score #inf_r smp run data get entity @s Rotation[0] 10',
    'scoreboard players add #inf_r smp 2025',
    'scoreboard players operation #inf_r smp %= #3600 smp',
    'scoreboard players operation #inf_r smp /= #450 smp',
    *[f'execute if score #inf_r smp matches {i} run data modify storage smp:tmp hud.dir set value {{text:"{d}"}}' for i, d in enumerate(_DIRS)],
])
def _gen_hud():             # erst in finish(): spaetere Module haengen Segmente an (HUD_PRE / HUD_PARTS, z.B. Wegpunkt-Kompass)
    fn('info/hud', [        # als + an dem Spieler (Uhrzeit-Scores kommen aus info/clock)
        f'function {NS}:info/blockpos',
        f'function {NS}:info/dimname',
        f'function {NS}:info/direction',
        *HUD_PRE,
        'title @s actionbar ' + tc([
            _t('X '), _sc('#inf_x'), _t(' Y '), _sc('#inf_y'), _t(' Z '), _sc('#inf_z'),
            _t(' · ', 'dark_gray'), _NBT('hud.dim', 'yellow'),
            _t(' · ', 'dark_gray'), _t('↑ '), _NBT('hud.dir', 'white'),
            _t(' · ', 'dark_gray'), _sc('#inf_h10'), _sc('#inf_h1'), _t(':', 'white'), _sc('#inf_m10'), _sc('#inf_m1'), *HUD_PARTS]),
    ])


EXTRA_FINISH.append(_gen_hud)

# ---------------------------------------------------------------- Stats: /trigger stats
trigger('stats', f'{NS}:info/stats', '/trigger stats', 'Deine Statistiken (Spielzeit, Tode, Kills, Strecke, Spruenge)', _C,
        ('Meine Stats', 'Spielzeit, Tode, Kills, Strecke, Spruenge'))
fn('info/calc_h', [         # Spielzeit von @s: smp_inf_hh Stunden, smp_inf_hd Zehntel
    'scoreboard players operation @s smp_inf_hh = @s smp_pt',
    'scoreboard players operation @s smp_inf_hh /= #7200 smp',
    'scoreboard players operation @s smp_inf_hd = @s smp_inf_hh',
    'scoreboard players operation @s smp_inf_hd %= #10 smp',
    'scoreboard players operation @s smp_inf_hh /= #10 smp',
])
fn('info/stats', [
    *[f'scoreboard players add @s {o} 0' for o in ('smp_pt', 'smp_tode', 'smp_mkills', 'smp_pkills', 'smp_walk', 'smp_sprint', 'smp_jump')],
    f'function {NS}:info/calc_h',
    'scoreboard players operation #inf_k smp = @s smp_walk', 'scoreboard players operation #inf_k smp += @s smp_sprint',
    'scoreboard players operation #inf_k smp /= #10000 smp',                     # Zehntel-km
    'scoreboard players operation #inf_k1 smp = #inf_k smp', 'scoreboard players operation #inf_k1 smp /= #10 smp',
    'scoreboard players operation #inf_k2 smp = #inf_k smp', 'scoreboard players operation #inf_k2 smp %= #10 smp',
    'tellraw @s ' + msg({'text': 'Deine Stats', 'color': 'gold', 'bold': True}),
    'tellraw @s ' + tc([_t('  Spielzeit: '), _sc('@s', 'smp_inf_hh'), _t(',', 'white'), _sc('@s', 'smp_inf_hd'), _t(' h', 'white')]),
    'tellraw @s ' + tc([_t('  Tode: '), _sc('@s', 'smp_tode')]),
    'tellraw @s ' + tc([_t('  Mob-Kills: '), _sc('@s', 'smp_mkills')]),
    'tellraw @s ' + tc([_t('  Spieler-Kills: '), _sc('@s', 'smp_pkills')]),
    'tellraw @s ' + tc([_t('  Gelaufen: '), _sc('#inf_k1'), _t(',', 'white'), _sc('#inf_k2'), _t(' km', 'white')]),
    'tellraw @s ' + tc([_t('  Spruenge: '), _sc('@s', 'smp_jump')]),
])

# ---------------------------------------------------------------- Top 5 (online): /trigger top
trigger('top', f'{NS}:info/top', '/trigger top', 'Top 5 der Online-Spieler: Spielzeit, Mob-Kills, Tode', _C)
_RANK_COL = ['gold', 'gray', 'red', 'white', 'white']
_BOARDS = [('pt', 'smp_pt', 'Spielzeit', [_sc('@a[tag=smp_top_{i},limit=1]', 'smp_inf_hh', 'yellow'), _t(',', 'yellow'), _sc('@a[tag=smp_top_{i},limit=1]', 'smp_inf_hd', 'yellow'), _t(' h', 'yellow')]),
           ('mk', 'smp_mkills', 'Mob-Kills', [_sc('@a[tag=smp_top_{i},limit=1]', 'smp_mkills', 'yellow')]),
           ('td', 'smp_tode', 'Tode', [_sc('@a[tag=smp_top_{i},limit=1]', 'smp_tode', 'yellow')])]
fn('info/top', [
    *[f'scoreboard players add @a {o} 0' for o in ('smp_pt', 'smp_mkills', 'smp_tode')],
    f'execute as @a run function {NS}:info/calc_h',
    'tellraw @s ' + msg({'text': 'Top 5 (online)', 'color': 'gold', 'bold': True}),
    *[f'function {NS}:info/rank_{k}' for k, *_ in _BOARDS],
])
fn('info/top_pick', ['$execute if entity @a[tag=smp_top_$(i)] run return 0', '$tag @s add smp_top_$(i)', 'tag @s add smp_top'])
for _k, _obj, _title, _val in _BOARDS:
    _lines = ['tag @a remove smp_top', *[f'tag @a remove smp_top_{i}' for i in range(1, 6)],
              'tellraw @s ' + tc({'text': f' {_title}', 'color': 'gold'})]
    for _i in range(1, 6):
        _v = [dict(c, **({'score': {'name': c['score']['name'].format(i=_i), 'objective': c['score']['objective']}} if 'score' in c else {})) for c in _val]
        _lines += ['scoreboard players set #inf_max smp -1',
                   f'execute as @a[tag=!smp_top] run scoreboard players operation #inf_max smp > @s {_obj}',
                   f'execute if score #inf_max smp matches 0.. as @a[tag=!smp_top] if score @s {_obj} = #inf_max smp run function {NS}:info/top_pick {{i:{_i}}}',
                   f'execute if entity @a[tag=smp_top_{_i}] run tellraw @s ' + tc([{'text': f'  {_i}. ', 'color': _RANK_COL[_i - 1]},
                                                                                   {'selector': f'@a[tag=smp_top_{_i}]', 'color': 'white'}, {'text': '  '}, *_v])]
    _lines += ['tag @a remove smp_top', *[f'tag @a remove smp_top_{i}' for i in range(1, 6)]]
    fn(f'info/rank_{_k}', _lines)

# ---------------------------------------------------------------- Online-Liste: /trigger online
trigger('online', f'{NS}:info/online', '/trigger online', 'Wer ist online? (mit AFK und Spielzeit)', _C)
fn('info/online', [
    'scoreboard players add @a smp_pt 0',
    f'execute as @a run function {NS}:info/calc_h',
    'execute store result score #inf_n smp if entity @a',
    'tag @s add smp_inf_v',
    'tellraw @s ' + msg({'text': 'Online (', 'color': 'gold', 'bold': True}, _sc('#inf_n', 'smp', 'gold'), {'text': ')', 'color': 'gold', 'bold': True}),
    f'execute as @a run function {NS}:info/online_line',
    'tag @s remove smp_inf_v',
])
_ONL = [_t('  '), _SEL, _t('  '), _sc('@s', 'smp_inf_hh'), _t(',', 'white'), _sc('@s', 'smp_inf_hd'), _t(' h')]
fn('info/online_line', [    # Mitglieder des Teams smp_afk zeigen " [AFK]" schon ueber den Team-Suffix im Namen (selector) – sonst explizit anhaengen
    'execute if entity @s[tag=smp_afk,team=!smp_afk] run tellraw @a[tag=smp_inf_v] ' + tc(_ONL + [_t('  [AFK]', 'dark_gray')]),
    'execute unless entity @s[tag=smp_afk,team=!smp_afk] run tellraw @a[tag=smp_inf_v] ' + tc(_ONL),
])

# ---------------------------------------------------------------- Position teilen: /trigger pos
trigger('pos', f'{NS}:info/pos', '/trigger pos', 'Deine Position fuer alle in den Chat posten (zum Treffen)', _C)
fn('info/pos', [
    'execute if score @s smp_cd_pos matches 1.. run return run tellraw @s ' + msg(_t('Warte noch ', 'red'), _sc('@s', 'smp_cd_pos', 'yellow'), _t(' s.', 'red')),
    f'scoreboard players set @s smp_cd_pos {_POS_CD}',
    f'function {NS}:info/blockpos',
    f'function {NS}:info/dimname',
    'tellraw @a ' + msg(_SEL, _t(' ist bei '), _sc('#inf_x'), _t(' / '), _sc('#inf_y'), _t(' / '), _sc('#inf_z'),
                        _t(' ('), _NBT('hud.dim', 'yellow'), _t(')')),
])

# ---------------------------------------------------------------- AFK: alle 10 s Blockposition + Blickrichtung vergleichen
fn('info/afk10', ['scoreboard players set #inf_afk smp 0', f'execute as @a at @s run function {NS}:info/afk_chk'])
fn('info/afk_chk', [
    f'function {NS}:info/blockpos',
    'execute store result score #inf_r smp run data get entity @s Rotation[0]',
    'execute store result score #inf_p smp run data get entity @s Rotation[1]',
    'scoreboard players operation #inf_r smp %= #360 smp',
    'scoreboard players operation #inf_r smp *= #1000 smp',
    'scoreboard players operation #inf_r smp += #inf_p smp',
    *[f'execute unless score @s smp_afk_{a} = #inf_{a} smp run return run function {NS}:info/afk_move' for a in 'xyzr'],
    'scoreboard players add @s smp_afk_t 10',
    f'execute if entity @s[tag=!smp_afk] if score @s smp_afk_t >= #afk_s smp run function {NS}:info/afk_on',
])
fn('info/afk_move', [
    *[f'scoreboard players operation @s smp_afk_{a} = #inf_{a} smp' for a in 'xyzr'],
    'scoreboard players set @s smp_afk_t 0',
    f'execute if entity @s[tag=smp_afk] run function {NS}:info/afk_off',
])
fn('info/afk_on', [         # Meldung vor dem Team-Beitritt, sonst steht der Suffix schon im Namen
    'tellraw @a ' + msg(_SEL, _t(' ist jetzt AFK.')),
    'tag @s add smp_afk',
    'execute if entity @s[team=] run team join smp_afk @s',
])
fn('info/afk_off', [
    'tag @s remove smp_afk',
    'execute if entity @s[team=smp_afk] run team leave @s',
    'tellraw @a ' + msg(_SEL, _t(' ist zurueck.')),
])

# ---------------------------------------------------------------- Schlaf-Hinweis (Stat sleep_in_bed; 1 Spieler reicht wegen players_sleeping_percentage 1)
fn('info/sleep', [
    'scoreboard players set @s smp_sleep 0',
    'execute if score #sleep_cd smp matches 1.. run return 0',
    f'scoreboard players set #sleep_cd smp {_SLEEP_CD}',
    'tellraw @a ' + msg(_SEL, _t(' schlaeft – gute Nacht! ', 'green'), _t('(1 Spieler reicht)')),
])
