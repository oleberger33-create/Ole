# TNT-Run: three wool floors; every block you step on turns orange, then red, then vanishes. Last one standing wins.
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
         'execute if score #tntrun_t mg matches 20 run title @a[tag=mg_tntrun] actionbar {"text":"3 Sekunden Schonzeit ...","color":"gray"}']
_decay = []
for dy, blk in _LAYERS:
    _decay += [f'{OW} fill {_cx - 14} {_cy + dy} {_cz - 14} {_cx + 14} {_cy + dy} {_cz + 14} minecraft:air replace minecraft:red_concrete',
               f'{OW} fill {_cx - 14} {_cy + dy} {_cz - 14} {_cx + 14} {_cy + dy} {_cz + 14} minecraft:red_concrete replace minecraft:orange_concrete']
fn('tntrun/decay', _decay)
party('tntrun', 'TNT-Run', 'red', TR, trig=60, prof='mason', sub='Boden zerfällt · Letzter gewinnt', menu='Lauf, bevor der Boden weg ist',
      info='Jeder Block, auf den du trittst, zerfällt nach einem Moment. Drei Ebenen übereinander – wer zuletzt noch steht, gewinnt.',
      title_sub='Bleib in Bewegung!', size=24, build=_b,
      setup=[f'{OW} spreadplayers {_cx} {_cz} 3 11 false @a[tag=mg_tntrun]',
             'effect give @a[tag=mg_tntrun] minecraft:saturation infinite 0 true',
             'effect give @a[tag=mg_tntrun] minecraft:resistance infinite 4 true'],
      game=_game, spect=(_cx, _cy + 10, _cz))
