# TNT-Run: three wool floors; every block you step on turns orange, then red, then vanishes. Last one standing wins.
# Solo run (1 starter, #tntrun_np 1): survive as long as possible, the time survived (ticks) is a personal record
# (mg_tntrun_pb, higher is better). No wins in solo; +2 coins from 30 s survived, +2 bonus when a new record reaches a
# new 30-s step (so creeping up a record by fractions of a second cannot be farmed).
TR = (70000, Y, 0)
_cx, _cy, _cz = TR
_LAYERS = [(0, 'white_wool'), (-8, 'light_blue_wool'), (-16, 'lime_wool')]
_b = clear_box(_cx - 18, _cy - 22, _cz - 18, _cx + 18, _cy + 4, _cz + 18, 6)
for dy, blk in _LAYERS:
    _b += [f'{OW} {c}' for c in disk(_cx, _cy + dy, _cz, 14, blk)]
_b += [f'{OW} {c}' for c in ring(_cx, _cy + 1, _cz, 15, 'barrier', 3)]
_game = [void_kill('mg_al_tntrun', _cy - 24),
         f'execute if score #tntrun_t mg matches 60.. as @a[tag=mg_al_tntrun] at @s run fill ~-0.3 ~-1 ~-0.3 ~0.3 ~-1 ~0.3 minecraft:orange_concrete replace #minecraft:wool',
         f'execute if score #tntrun_t mg matches 60.. as @a[tag=mg_al_tntrun] at @s run fill ~-0.3 ~-1.6 ~-0.3 ~0.3 ~-1.6 ~0.3 minecraft:orange_concrete replace #minecraft:wool',
         'scoreboard players operation #m mg = #tntrun_t mg', 'scoreboard players operation #m mg %= #4 mg',
         f'execute if score #m mg matches 0 run function {NS}:tntrun/decay',
         'execute if score #tntrun_t mg matches 60 run title @a[tag=mg_tntrun] actionbar {"text":"Der Boden zerfällt jetzt!","color":"red","bold":true}',
         f'execute as @a[tag=mg_al_tntrun] at @s if block ~ ~-1 ~ minecraft:barrier run kill @s',
         *[f'execute if score #tntrun_t mg matches {3600 + 200 * i} run {OW} fill {_cx - 14} {_cy + dy} {_cz - 14} {_cx + 14} {_cy + dy} {_cz + 14} minecraft:orange_concrete replace #minecraft:wool' for i, (dy, blk) in enumerate(_LAYERS)],
         'execute if score #tntrun_t mg matches 3600 run title @a[tag=mg_tntrun] actionbar {"text":"Zeit um – der Boden löst sich auf!","color":"red","bold":true}',
         'execute if score #tntrun_t mg matches 20 run title @a[tag=mg_tntrun] actionbar {"text":"3 Sekunden Schonzeit ...","color":"gray"}',
         # solo: handle the fall here (before the framework's out: no "ist raus", no out-coins), show a survival clock
         f'execute if score #tntrun_np mg matches ..1 as @a[tag=mg_al_tntrun,scores={{mg_deaths=1..}}] run function {NS}:tntrun/solo_out',
         'scoreboard players operation #m mg = #tntrun_t mg', 'scoreboard players operation #m mg %= #20 mg',
         f'execute if score #tntrun_np mg matches ..1 if score #m mg matches 0 if score #tntrun_t mg matches 100.. unless score #tntrun_t mg matches 3600..3680 run function {NS}:tntrun/solo_hud']
_decay = []
for dy, blk in _LAYERS:
    _decay += [f'{OW} fill {_cx - 14} {_cy + dy} {_cz - 14} {_cx + 14} {_cy + dy} {_cz + 14} minecraft:air replace minecraft:red_concrete',
               f'{OW} fill {_cx - 14} {_cy + dy} {_cz - 14} {_cx + 14} {_cy + dy} {_cz + 14} minecraft:red_concrete replace minecraft:orange_concrete']
fn('tntrun/decay', _decay)

# ---- solo run
pb_register('tntrun', 'TNT-Run', 'red', label='Überlebenszeit', lower=False)
_SPC = (_cx, _cy + 10, _cz)
fn('tntrun/solo_hud', [*pb_fmt('#tntrun_t mg', 'tntrun_h'),
                       'title @a[tag=mg_al_tntrun] actionbar ' + tc([{'text': 'Überlebt: ', 'color': 'red'}] + pb_txt('tntrun_h', 'white'))])
fn('tntrun/solo_info', [    # as the player at the start of a solo run
    *pb_fmt('@s mg_tntrun_pb', 'tntrun_b'),
    'execute if score @s mg_tntrun_pb matches 1.. run tellraw @s ' + msg({'text': 'Solo-Runde! ', 'color': 'aqua', 'bold': True},
                                                                         {'text': 'Dein Rekord: ', 'color': 'gray'}, *pb_txt('tntrun_b', 'gold'),
                                                                         {'text': ' – hältst du länger durch?', 'color': 'gray'}),
    'execute unless score @s mg_tntrun_pb matches 1.. run tellraw @s ' + msg({'text': 'Solo-Runde! ', 'color': 'aqua', 'bold': True},
                                                                             {'text': 'Bleib so lange wie möglich oben – deine Zeit wird dein Rekord.', 'color': 'gray'})])
fn('tntrun/solo_out', [     # as the solo player in the tick they fell / died
    'tag @s remove mg_al_tntrun', 'scoreboard players set @s mg_deaths 0', 'gamemode spectator @s', 'clear @s',
    f'{OW} tp @s {_SPC[0]} {_SPC[1]} {_SPC[2]}',
    'scoreboard players operation #pbv mg = #tntrun_t mg',
    'scoreboard players set #tntrun_ob mg 0',
    'execute if score @s mg_tntrun_pb matches 1.. run scoreboard players operation #tntrun_ob mg = @s mg_tntrun_pb',
    *pb_fmt('#pbv mg', 'tntrun_p'),
    'title @s times 5 60 15',
    'title @s subtitle ' + tc([{'text': 'Überlebt: ', 'color': 'white'}] + pb_txt('tntrun_p', 'yellow')),
    'tellraw @s ' + msg({'text': 'Runtergefallen! ', 'color': 'red', 'bold': True}, {'text': 'Du hast ', 'color': 'gray'}, *pb_txt('tntrun_p', 'yellow'),
                        {'text': ' überlebt.', 'color': 'gray'}),
    f'function {NS}:tntrun/pb',
    'execute if score #pbn mg matches 1 run title @s subtitle ' + tc([{'text': '★ Neuer Rekord: ', 'color': 'gold', 'bold': True}] + pb_txt('tntrun_p', 'yellow')),
    # coins: 2 from 30 s survived; record bonus only when the record reaches a new 30-s step
    'scoreboard players set #tntrun_k mg 600',
    'scoreboard players operation #tntrun_ob mg /= #tntrun_k mg',
    'scoreboard players operation #tntrun_nb mg = #pbv mg', 'scoreboard players operation #tntrun_nb mg /= #tntrun_k mg',
    'execute if score #pbv mg matches 600.. run scoreboard players add @s mg_coins 2',
    'execute if score #pbv mg matches 600.. run tellraw @s ' + msg({'text': '+2 Münzen', 'color': 'yellow'}),
    'execute unless score #pbv mg matches 600.. run tellraw @s ' + msg({'text': 'Ab 30 Sekunden gibt es Münzen.', 'color': 'gray'}),
    'execute if score #pbn mg matches 1 if score #tntrun_nb mg > #tntrun_ob mg run scoreboard players add @s mg_coins 2',
    'execute if score #pbn mg matches 1 if score #tntrun_nb mg > #tntrun_ob mg run tellraw @s ' + msg({'text': 'Rekord-Bonus: ', 'color': 'gold'}, {'text': '+2 Münzen', 'color': 'yellow'}),
    'execute at @s run playsound minecraft:block.note_block.didgeridoo master @s ~ ~ ~ 1 0.7'])
party('tntrun', 'TNT-Run', 'red', TR, trig=60, prof='mason', sub='Boden zerfällt · Letzter gewinnt · auch solo', menu='Lauf, bevor der Boden weg ist – auch solo',
      info='Jeder Block, auf den du trittst, zerfällt nach einem Moment. Drei Ebenen übereinander – wer zuletzt noch steht, gewinnt. '
           'Alleine spielst du auf Zeit und jagst deinen Überlebens-Rekord.',
      title_sub='Bleib in Bewegung!', size=24, build=_b,
      setup=[f'{OW} spreadplayers {_cx} {_cz} 3 9 under {_cy + 1} false @a[tag=mg_tntrun]',
             'effect give @a[tag=mg_tntrun] minecraft:saturation infinite 0 true',
             'effect give @a[tag=mg_tntrun] minecraft:resistance infinite 4 true',
             'effect give @a[tag=mg_tntrun] minecraft:weakness infinite 255 true',
             f'execute if score #tntrun_np mg matches ..1 as @a[tag=mg_tntrun] run function {NS}:tntrun/solo_info'],
      game=_game, spect=_SPC, solo=True)
