# modules/waypoints.py – Wegpunkte pro Spieler, komplett serverseitig: speichern, benennen (Dialog), verfolgen
# (Kompass in der Actionbar: Richtung relativ zum Blick, Entfernung, hoeher/tiefer + Lichtsaeule aus Partikeln, die nur
# der Verfolger sieht), Chat-Liste, Esc-Menue-Dialog, teilen (Knopf zum Uebernehmen), loeschen mit Rueckfrage, Todesort.
#
# Storage smp:wp   p<id>.s<1..10> {n,name,x,y,z,xc,zc,yb,dim,dn}   p<id>.tod {n:99,...}   shared.c<code> {... , von}
# Scores: smp_wp_sel (verfolgt: 0 keiner, 1..10 Platz, 99 Todesort), smp_wp_last (zuletzt gespeicherter Platz, fuer den
#         Namens-Dialog), smp_wp_dist (letzte Entfernung, fuer die Lichtsaeule), Konstanten/Scratch #wp_* in `smp`
# Trigger-Werte: wpset 1 = naechster freier Platz, 11..20 = Platz 1..10 ueberschreiben; wpname 1 = Dialog, 2.. = Name;
#                wpgo/wpshare n = Platz, 99 = Todesort; wpdel n = Rueckfrage, 10+n = loeschen; wpget code = geteilter Wegpunkt
_C = 'Wegpunkte'
_MAX = 10
_NAMES = ['Basis', 'Haus', 'Farm', 'Mine', 'Dorf', 'Portal', 'Festung', 'Höhle', 'Schatz', 'Treffpunkt', 'Lager', 'Monument',
          'Wald', 'Berg', 'Insel', 'Spawner', 'Händler', 'Bastion', 'Endportal', 'Dschungel', 'Pilzinsel', 'Wüste', 'Sumpf',
          'Schlucht', 'Tempel', 'Nether-Hub', 'Sonstiges']
_ARROWS = ['↑', '↗', '→', '↘', '↓', '↙', '←', '↖']        # relativ zur Blickrichtung
_BEACON_RANGE = 500                                         # Lichtsaeule nur bis zu dieser Entfernung (force-Partikel reichen 512)

EXTRA_LOAD += [
    'scoreboard objectives add smp_wp_sel dummy', 'scoreboard objectives add smp_wp_last dummy', 'scoreboard objectives add smp_wp_dist dummy',
    *[f'scoreboard players set #{n} smp {n}' for n in (2, 8, 450, 1000, 2414, 3600)],
    'scoreboard players set #-1 smp -1',
    'execute unless score #wp_code smp matches 0.. run scoreboard players set #wp_code smp 0',
    'scoreboard players set #wp_t smp 0',
]
cooldown('smp_cd_wps')


def _r(t):
    return 'tellraw @s ' + msg({'text': t, 'color': 'red'})


def _dn_lines():
    """storage smp:tmp dim/dn (Dimensions-Id und deutscher Name) fuer @s"""
    return [f'function {NS}:core/dim', *[f'execute if dimension {d} run data modify storage smp:tmp dn set value "{name}"' for d, name, _ in DIMS]]


def _center_lines(src_x, src_y, src_z):
    """aus den Scores src_* (Blockkoordinaten) die Partikel-Position xc/zc (Blockmitte, double) und yb (y+14) nach smp:tmp"""
    out = []
    for a, src in (('x', src_x), ('z', src_z)):
        out += [f'scoreboard players operation #wp_c smp = {src}', 'scoreboard players operation #wp_c smp *= #2 smp', 'scoreboard players add #wp_c smp 1',
                f'execute store result storage smp:tmp {a}c double 0.5 run scoreboard players get #wp_c smp']
    out += [f'scoreboard players operation #wp_c smp = {src_y}', 'scoreboard players add #wp_c smp 14',
            'execute store result storage smp:tmp yb int 1 run scoreboard players get #wp_c smp']
    return out


fn('wp/id', ['execute store result storage smp:tmp id int 1 run scoreboard players get @s smp_id'])

# ---------------------------------------------------------------- speichern: /trigger wpset (1 = freier Platz, 1n = Platz n)
fn('wp/free', ['scoreboard players set #wp_n smp 0', f'function {NS}:wp/id', f'function {NS}:wp/free2 with storage smp:tmp'])
fn('wp/free2', [f'$execute unless data storage smp:wp p$(id).s{n} run scoreboard players set #wp_n smp {n}' for n in range(_MAX, 0, -1)])
fn('wp/set', [
    'scoreboard players set #wp_n smp 0',
    f'execute if score @s wpset matches 11..{10 + _MAX} run scoreboard players operation #wp_n smp = @s wpset',
    f'execute if score @s wpset matches 11..{10 + _MAX} run scoreboard players remove #wp_n smp 10',
    f'execute if score @s wpset matches 1 run function {NS}:wp/free',
    'execute if score @s wpset matches 1 if score #wp_n smp matches 0 run return run ' + _r(f'Alle {_MAX} Plaetze belegt. Loeschen: /trigger wpliste – oder ueberschreiben: /trigger wpset set 1<Platz> (z. B. 13 = Platz 3)'),
    f'execute unless score #wp_n smp matches 1..{_MAX} run return run ' + _r(f'/trigger wpset (freier Platz) oder /trigger wpset set 1<Platz> fuer Platz 1 bis {_MAX}'),
    f'function {NS}:wp/id',
    'execute store result storage smp:tmp n int 1 run scoreboard players get #wp_n smp',
    *[f'execute store result score #wp_{a} smp run data get entity @s Pos[{i}]' for i, a in enumerate('xyz')],
    *[f'execute store result storage smp:tmp {a} int 1 run scoreboard players get #wp_{a} smp' for a in 'xyz'],
    *_center_lines('#wp_x smp', '#wp_y smp', '#wp_z smp'),
    *_dn_lines(),
    f'function {NS}:wp/set2 with storage smp:tmp',
])
fn('wp/set2', [
    '$data modify storage smp:wp p$(id).s$(n) set value {n:$(n),name:"Wegpunkt $(n)",x:$(x),y:$(y),z:$(z),xc:$(xc),zc:$(zc),yb:$(yb),dim:"$(dim)",dn:"$(dn)"}',
    '$scoreboard players set @s smp_wp_last $(n)',
    '$tellraw @s ' + msg({'text': 'Wegpunkt $(n) gespeichert: ', 'color': 'green'}, {'text': '$(x) $(y) $(z)', 'color': 'white'}, {'text': ' ($(dn))  ', 'color': 'gray'},
                         clk('[Verfolgen]', '/trigger wpgo set $(n)', 'green', 'Kompass + Lichtsaeule'), {'text': ' '}, clk('[Name]', '/trigger wpname', 'yellow', 'Namen waehlen')),
    f'function {NS}:wp/name_dialog',
])

# ---------------------------------------------------------------- benennen: Dialog mit Auswahlliste -> /trigger wpname set <k>
fn('wp/name_dialog', ['dialog show @s ' + tc({
    'type': 'minecraft:multi_action', 'title': {'text': 'Wegpunkt benennen', 'color': 'aqua', 'bold': True}, 'external_title': {'text': 'Wegpunkt benennen'},
    'body': {'type': 'minecraft:plain_message', 'width': 250, 'contents': {'text': 'Name fuer den gerade gespeicherten Wegpunkt:', 'color': 'gray'}},
    'inputs': [{'type': 'minecraft:single_option', 'key': 'k', 'label': {'text': 'Name'}, 'width': 220,
                'options': [{'id': str(i + 2), 'display': {'text': nm}, **({'initial': True} if i == 0 else {})} for i, nm in enumerate(_NAMES)]}],
    'actions': [{'label': {'text': 'Speichern'}, 'width': 150, 'action': {'type': 'minecraft:dynamic/run_command', 'template': 'trigger wpname set $(k)'}}],
    'exit_action': {'label': {'text': 'Ohne Namen'}, 'width': 150},
})])
fn('wp/name', [
    f'execute unless score @s smp_wp_last matches 1..{_MAX} run return run ' + _r('Erst einen Wegpunkt speichern: /trigger wpset'),
    f'execute unless score @s wpname matches 2..{len(_NAMES) + 1} run return run function {NS}:wp/name_dialog',
    f'function {NS}:wp/id',
    'execute store result storage smp:tmp n int 1 run scoreboard players get @s smp_wp_last',
    'execute store result storage smp:tmp k int 1 run scoreboard players get @s wpname',
    f'function {NS}:wp/name2 with storage smp:tmp',
])
fn('wp/name2', ['$execute unless data storage smp:wp p$(id).s$(n) run return run ' + _r('Wegpunkt $(n) gibt es nicht mehr.'),
                f'$function {NS}:wp/nm_$(k) with storage smp:tmp'])
for _i, _nm in enumerate(_NAMES):
    fn(f'wp/nm_{_i + 2}', [f'$data modify storage smp:wp p$(id).s$(n).name set value "{_nm}"',
                           '$tellraw @s ' + msg({'text': 'Wegpunkt $(n) heisst jetzt ', 'color': 'green'}, {'text': _nm, 'color': 'aqua'}, {'text': '. ', 'color': 'green'},
                                                clk('[Verfolgen]', '/trigger wpgo set $(n)', 'green', 'Kompass + Lichtsaeule'))])

# ---------------------------------------------------------------- verfolgen: /trigger wpgo set <n>  (99 = Todesort), /trigger wpoff
fn('wp/go', [
    f'execute if score @s wpgo matches 99 run return run function {NS}:wp/go_tod',
    f'execute unless score @s wpgo matches 1..{_MAX} run return run ' + _r(f'/trigger wpgo set <Platz 1 bis {_MAX}> (99 = Todesort). Liste: /trigger wpliste'),
    f'function {NS}:wp/id', 'execute store result storage smp:tmp n int 1 run scoreboard players get @s wpgo',
    f'function {NS}:wp/go2 with storage smp:tmp',
])
fn('wp/go2', ['$execute unless data storage smp:wp p$(id).s$(n) run return run ' + _r('Wegpunkt $(n) ist leer. Speichern: /trigger wpset'),
              '$scoreboard players set @s smp_wp_sel $(n)', 'scoreboard players set @s smp_wp_dist 0',
              '$data modify storage smp:tmp wp set from storage smp:wp p$(id).s$(n)', f'function {NS}:wp/go_msg with storage smp:tmp wp'])
fn('wp/go_tod', [f'function {NS}:wp/id', f'function {NS}:wp/go_tod2 with storage smp:tmp'])
fn('wp/go_tod2', ['$execute unless data storage smp:wp p$(id).tod run return run ' + _r('Kein Todesort gespeichert.'),
                  'scoreboard players set @s smp_wp_sel 99', 'scoreboard players set @s smp_wp_dist 0',
                  '$data modify storage smp:tmp wp set from storage smp:wp p$(id).tod', f'function {NS}:wp/go_msg with storage smp:tmp wp'])
fn('wp/go_msg', ['$tellraw @s ' + msg({'text': 'Verfolge ', 'color': 'green'}, {'text': '$(name)', 'color': 'aqua'}, {'text': ' ($(x) $(y) $(z), $(dn)). Kompass unten, Lichtsaeule am Ziel. ', 'color': 'gray'},
                                      clk('[Aus]', '/trigger wpoff', 'yellow', 'Verfolgung beenden'))])
fn('wp/off', ['scoreboard players set @s smp_wp_sel 0', 'title @s actionbar ""', 'tellraw @s ' + msg({'text': 'Verfolgung aus.', 'color': 'gray'})])
fn('wp/lost', ['scoreboard players set @s smp_wp_sel 0', 'tellraw @s ' + msg({'text': 'Der verfolgte Wegpunkt wurde geloescht.', 'color': 'gray'})])

# Kompass: alle 5 Ticks (ohne Info-HUD) bzw. innerhalb des Info-HUDs (alle 10 Ticks, als Segment)
EXTRA_TICK += ['scoreboard players add #wp_t smp 1', f'execute if score #wp_t smp matches 5.. run function {NS}:wp/t5']
fn('wp/t5', ['scoreboard players set #wp_t smp 0', f'execute as @a[scores={{smp_wp_sel=1..}},tag=!smp_hud] at @s run function {NS}:wp/track'])
HUD_PRE += ['data modify storage smp:tmp hud.wp set value {text:""}', f'execute if score @s smp_wp_sel matches 1.. run function {NS}:wp/track']
HUD_PARTS.append({'nbt': 'hud.wp', 'storage': 'smp:tmp', 'interpret': True})
fn('wp/track', [
    f'function {NS}:wp/id',
    'execute store result storage smp:tmp k int 1 run scoreboard players get @s smp_wp_sel',
    f'execute if score @s smp_wp_sel matches 99 run return run function {NS}:wp/track_tod with storage smp:tmp',
    f'function {NS}:wp/track2 with storage smp:tmp',
])
fn('wp/track2', [f'$execute unless data storage smp:wp p$(id).s$(k) run return run function {NS}:wp/lost',
                 '$data modify storage smp:tmp wp set from storage smp:wp p$(id).s$(k)', f'function {NS}:wp/track3 with storage smp:tmp wp'])
fn('wp/track_tod', [f'$execute unless data storage smp:wp p$(id).tod run return run function {NS}:wp/lost',
                    '$data modify storage smp:tmp wp set from storage smp:wp p$(id).tod', f'function {NS}:wp/track3 with storage smp:tmp wp'])
fn('wp/track3', [
    f'$execute unless dimension $(dim) run return run function {NS}:wp/far with storage smp:tmp wp',
    *[f'$scoreboard players set #wp_t{a} smp $({a})' for a in 'xyz'],
    f'function {NS}:wp/calc',
    f'function {NS}:wp/show with storage smp:tmp wp',
])
_calc = [*[f'execute store result score #wp_p{a} smp run data get entity @s Pos[{i}]' for i, a in enumerate('xyz')]]
for _a in 'xyz':
    _calc += [f'scoreboard players operation #wp_d{_a} smp = #wp_t{_a} smp', f'scoreboard players operation #wp_d{_a} smp -= #wp_p{_a} smp']
for _a in 'xz':                                                       # auf +-30000 begrenzen (Quadrate muessen in int passen)
    _calc += [f'execute if score #wp_d{_a} smp matches 30001.. run scoreboard players set #wp_d{_a} smp 30000',
              f'execute if score #wp_d{_a} smp matches ..-30001 run scoreboard players set #wp_d{_a} smp -30000',
              f'scoreboard players operation #wp_a{_a} smp = #wp_d{_a} smp',
              f'execute if score #wp_a{_a} smp matches ..-1 run scoreboard players operation #wp_a{_a} smp *= #-1 smp']
_calc += ['scoreboard players operation #wp_d2 smp = #wp_ax smp', 'scoreboard players operation #wp_d2 smp *= #wp_ax smp',
          'scoreboard players operation #wp_q smp = #wp_az smp', 'scoreboard players operation #wp_q smp *= #wp_az smp', 'scoreboard players operation #wp_d2 smp += #wp_q smp',
          'scoreboard players set #wp_dist smp 0', f'execute if score #wp_d2 smp matches 1.. run function {NS}:wp/isqrt',
          'scoreboard players operation @s smp_wp_dist = #wp_dist smp',
          # Blick-Sektor 0..7 (N, NO, O, SO, S, SW, W, NW) wie im Info-HUD
          'execute store result score #wp_r smp run data get entity @s Rotation[0] 10', 'scoreboard players add #wp_r smp 2025',
          'scoreboard players operation #wp_r smp %= #3600 smp', 'scoreboard players operation #wp_r smp /= #450 smp',
          # Ziel-Sektor: |dz|*1000 >= |dx|*2414 -> N/S, |dx|*1000 >= |dz|*2414 -> O/W, sonst diagonal
          'scoreboard players set #wp_ts smp -1',
          'scoreboard players operation #wp_a smp = #wp_az smp', 'scoreboard players operation #wp_a smp *= #1000 smp',
          'scoreboard players operation #wp_b smp = #wp_ax smp', 'scoreboard players operation #wp_b smp *= #2414 smp',
          'execute if score #wp_a smp >= #wp_b smp if score #wp_dz smp matches ..-1 run scoreboard players set #wp_ts smp 0',
          'execute if score #wp_a smp >= #wp_b smp if score #wp_dz smp matches 0.. run scoreboard players set #wp_ts smp 4',
          'scoreboard players operation #wp_a smp = #wp_ax smp', 'scoreboard players operation #wp_a smp *= #1000 smp',
          'scoreboard players operation #wp_b smp = #wp_az smp', 'scoreboard players operation #wp_b smp *= #2414 smp',
          'execute if score #wp_ts smp matches -1 if score #wp_a smp >= #wp_b smp if score #wp_dx smp matches 1.. run scoreboard players set #wp_ts smp 2',
          'execute if score #wp_ts smp matches -1 if score #wp_a smp >= #wp_b smp if score #wp_dx smp matches ..-1 run scoreboard players set #wp_ts smp 6',
          'execute if score #wp_ts smp matches -1 if score #wp_dx smp matches 1.. if score #wp_dz smp matches ..-1 run scoreboard players set #wp_ts smp 1',
          'execute if score #wp_ts smp matches -1 if score #wp_dx smp matches 1.. if score #wp_dz smp matches 0.. run scoreboard players set #wp_ts smp 3',
          'execute if score #wp_ts smp matches -1 if score #wp_dx smp matches ..-1 if score #wp_dz smp matches 0.. run scoreboard players set #wp_ts smp 5',
          'execute if score #wp_ts smp matches -1 run scoreboard players set #wp_ts smp 7',
          'scoreboard players operation #wp_ts smp -= #wp_r smp', 'scoreboard players add #wp_ts smp 8', 'scoreboard players operation #wp_ts smp %= #8 smp',
          *[f'execute if score #wp_ts smp matches {i} run data modify storage smp:tmp wp.arrow set value "{g}"' for i, g in enumerate(_ARROWS)],
          'execute if score #wp_d2 smp matches 0 run data modify storage smp:tmp wp.arrow set value "●"',
          'data modify storage smp:tmp wp.vert set value ""',
          'execute if score #wp_dy smp matches 4.. run data modify storage smp:tmp wp.vert set value "▲ hoeher"',
          'execute if score #wp_dy smp matches ..-4 run data modify storage smp:tmp wp.vert set value "▼ tiefer"',
          'execute store result storage smp:tmp wp.dist int 1 run scoreboard players get #wp_dist smp']
fn('wp/calc', _calc)
fn('wp/isqrt', [    # ganzzahlige Wurzel aus #wp_d2 (>= 1): Newton von oben, Start |dx|+|dz| >= Wurzel
    'scoreboard players operation #wp_x smp = #wp_ax smp', 'scoreboard players operation #wp_x smp += #wp_az smp',
    *(['scoreboard players operation #wp_q smp = #wp_d2 smp', 'scoreboard players operation #wp_q smp /= #wp_x smp',
       'scoreboard players operation #wp_x smp += #wp_q smp', 'scoreboard players operation #wp_x smp /= #2 smp'] * 6),
    'scoreboard players operation #wp_dist smp = #wp_x smp',
])
fn('wp/show', [
    '$data modify storage smp:tmp hud.wp set value {text:" · ◆ $(name) $(arrow) $(dist) m $(vert)",color:"aqua"}',
    '$execute if entity @s[tag=!smp_hud] unless score @s smp_wu matches 1.. run title @s actionbar [{text:"◆ $(name)  ",color:"aqua",bold:true},{text:"$(arrow) ",color:"yellow",bold:true},{text:"$(dist) m",color:"white"},{text:"  $(vert)",color:"gray"}]',
])
fn('wp/far', [
    '$data modify storage smp:tmp hud.wp set value {text:" · ◆ $(name) – in $(dn)",color:"aqua"}',
    '$execute if entity @s[tag=!smp_hud] unless score @s smp_wu matches 1.. run title @s actionbar [{text:"◆ $(name)",color:"aqua",bold:true},{text:" – liegt in $(dn)",color:"gray"}]',
])
# Lichtsaeule am Ziel: jede Sekunde, nur fuer den Verfolger (particle ... force @s), nur in der Naehe
EXTRA_SECOND.append(f'execute as @a[scores={{smp_wp_sel=1..,smp_wp_dist=..{_BEACON_RANGE}}}] at @s run function {NS}:wp/beacon')
fn('wp/beacon', [f'function {NS}:wp/id', 'execute store result storage smp:tmp k int 1 run scoreboard players get @s smp_wp_sel',
                 f'execute if score @s smp_wp_sel matches 99 run return run function {NS}:wp/beacon_tod with storage smp:tmp',
                 f'function {NS}:wp/beacon2 with storage smp:tmp'])
fn('wp/beacon2', [f'$execute if data storage smp:wp p$(id).s$(k) run function {NS}:wp/beacon3 with storage smp:wp p$(id).s$(k)'])
fn('wp/beacon_tod', [f'$execute if data storage smp:wp p$(id).tod run function {NS}:wp/beacon3 with storage smp:wp p$(id).tod'])
fn('wp/beacon3', ['$execute if dimension $(dim) run particle minecraft:end_rod $(xc) $(yb) $(zc) 0.12 10 0.12 0 40 force @s',
                  '$execute if dimension $(dim) run particle minecraft:dust{color:[0.3,0.9,1.0],scale:2.0} $(xc) $(yb) $(zc) 0.6 10 0.6 0 12 force @s'])

# ---------------------------------------------------------------- Chat-Liste: /trigger wpliste
fn('wp/list', [f'function {NS}:wp/id', f'function {NS}:wp/list2 with storage smp:tmp'])
fn('wp/list2', [
    'tellraw @s ' + msg({'text': 'Deine Wegpunkte', 'color': 'aqua', 'bold': True}, {'text': f'  (max. {_MAX})', 'color': 'gray'}),
    *[f'$execute if data storage smp:wp p$(id).s{n} run function {NS}:wp/line with storage smp:wp p$(id).s{n}' for n in range(1, _MAX + 1)],
    f'$execute if data storage smp:wp p$(id).tod run function {NS}:wp/line_tod with storage smp:wp p$(id).tod',
    '$execute unless data storage smp:wp p$(id) run tellraw @s ' + tc({'text': '   Noch keine Wegpunkte.', 'color': 'gray'}),
    'tellraw @s ' + tc([{'text': '   '}, clk('[+ Hier speichern]', '/trigger wpset', 'green', 'Wegpunkt an deiner Position'), {'text': '  '},
                        clk('[Verfolgung aus]', '/trigger wpoff', 'yellow', 'Kompass ausschalten'), {'text': '  '}, clk('[Menue]', '/trigger wp', 'aqua', 'Als Dialog')]),
])
fn('wp/line', ['$tellraw @s ' + tc([{'text': '  $(n). ', 'color': 'gray'}, {'text': '$(name)', 'color': 'aqua'}, {'text': '  $(x) $(y) $(z)', 'color': 'white'}, {'text': ' ($(dn))  ', 'color': 'gray'},
                                     clk('[Verfolgen]', '/trigger wpgo set $(n)', 'green', 'Kompass + Lichtsaeule'), {'text': ' '},
                                     clk('[Teilen]', '/trigger wpshare set $(n)', 'yellow', 'Allen im Chat zeigen'), {'text': ' '},
                                     clk('[X]', '/trigger wpdel set $(n)', 'red', 'Loeschen (mit Rueckfrage)')])])
fn('wp/line_tod', ['$tellraw @s ' + tc([{'text': '  ☠ ', 'color': 'red'}, {'text': 'Todesort', 'color': 'aqua'}, {'text': '  $(x) $(y) $(z)', 'color': 'white'}, {'text': ' ($(dn))  ', 'color': 'gray'},
                                         clk('[Verfolgen]', '/trigger wpgo set 99', 'green', 'Kompass + Lichtsaeule'), {'text': ' '},
                                         clk('[X]', '/trigger wpdel set 99', 'red', 'Todesort vergessen')])])

# ---------------------------------------------------------------- Dialog-Menue: /trigger wp (auch Esc -> SMP-Menue)
_ARGS = ','.join([f'l{i}:"",n{i}:0,d{i}:""' for i in range(1, _MAX + 2)])
fn('wp/menu', [f'function {NS}:wp/id', f'data modify storage smp:tmp wpargs set value {{{_ARGS}}}', 'scoreboard players set #wp_i smp 0',
               f'function {NS}:wp/menu_collect with storage smp:tmp',
               *[f'execute if score #wp_i smp matches {k} run function {NS}:wp/menu_{k} with storage smp:tmp wpargs' for k in range(_MAX + 2)]])
fn('wp/menu_collect', [*[f'$execute if data storage smp:wp p$(id).s{n} run function {NS}:wp/menu_add with storage smp:wp p$(id).s{n}' for n in range(1, _MAX + 1)],
                       f'$execute if data storage smp:wp p$(id).tod run function {NS}:wp/menu_add with storage smp:wp p$(id).tod'])
fn('wp/menu_add', ['scoreboard players add #wp_i smp 1', 'data modify storage smp:tmp fv set value {}',
                   'execute store result storage smp:tmp fv.i int 1 run scoreboard players get #wp_i smp',
                   '$data modify storage smp:tmp fv.l set value "◆ $(name)  $(x) $(y) $(z)"', '$data modify storage smp:tmp fv.d set value "$(dn)"',
                   '$data modify storage smp:tmp fv.n set value $(n)', f'function {NS}:wp/menu_put with storage smp:tmp fv'])
fn('wp/menu_put', ['$data modify storage smp:tmp wpargs.l$(i) set value "$(l)"', '$data modify storage smp:tmp wpargs.n$(i) set value $(n)', '$data modify storage smp:tmp wpargs.d$(i) set value "$(d)"'])
for _k in range(_MAX + 2):
    _acts = [{'label': {'text': f'$(l{i})'}, 'tooltip': {'text': f'$(d{i}) – anklicken: verfolgen'}, 'width': 200, 'action': {'type': 'run_command', 'command': f'trigger wpgo set $(n{i})'}} for i in range(1, _k + 1)]
    _acts += [{'label': {'text': '+ Hier speichern', 'color': 'green'}, 'tooltip': {'text': 'Wegpunkt an deiner Position'}, 'width': 200, 'action': {'type': 'run_command', 'command': 'trigger wpset'}},
              {'label': {'text': 'Verfolgung aus', 'color': 'yellow'}, 'tooltip': {'text': 'Kompass ausschalten'}, 'width': 200, 'action': {'type': 'run_command', 'command': 'trigger wpoff'}},
              {'label': {'text': 'Chat-Liste (teilen, loeschen)', 'color': 'gray'}, 'tooltip': {'text': 'Alle Wegpunkte mit Knoepfen im Chat'}, 'width': 200, 'action': {'type': 'run_command', 'command': 'trigger wpliste'}}]
    fn(f'wp/menu_{_k}', [('$' if _k else '') + 'dialog show @s ' + tc({
        'type': 'minecraft:multi_action', 'title': {'text': '◆ Wegpunkte', 'color': 'aqua', 'bold': True}, 'external_title': {'text': 'Wegpunkte'},
        'body': {'type': 'minecraft:plain_message', 'width': 300, 'contents': {'text': 'Anklicken = verfolgen (Kompass unten, Lichtsaeule am Ziel – nur fuer dich sichtbar).' if _k else 'Noch keine Wegpunkte. Speichern mit dem Knopf oder /trigger wpset.', 'color': 'gray'}},
        'columns': 2, 'actions': _acts, 'exit_action': {'label': {'text': 'Schliessen'}, 'width': 150}})])

# ---------------------------------------------------------------- loeschen (Rueckfrage), teilen, uebernehmen
fn('wp/del', [
    'scoreboard players set #wp_c smp 0',
    f'execute if score @s wpdel matches 11..{10 + _MAX} run scoreboard players set #wp_c smp 1',
    f'execute if score @s wpdel matches 11..{10 + _MAX} run scoreboard players remove @s wpdel 10',
    f'execute if score @s wpdel matches 99 run return run function {NS}:wp/del_tod',
    f'execute unless score @s wpdel matches 1..{_MAX} run return run ' + _r('Welchen Wegpunkt? Liste: /trigger wpliste'),
    f'function {NS}:wp/id', 'execute store result storage smp:tmp n int 1 run scoreboard players get @s wpdel',
    'scoreboard players operation #wp_n smp = @s wpdel', 'scoreboard players add #wp_n smp 10',
    'execute store result storage smp:tmp n10 int 1 run scoreboard players get #wp_n smp',
    f'function {NS}:wp/del2 with storage smp:tmp',
])
fn('wp/del2', [
    '$execute unless data storage smp:wp p$(id).s$(n) run return run ' + _r('Wegpunkt $(n) ist leer.'),
    '$data modify storage smp:tmp wp set from storage smp:wp p$(id).s$(n)', '$data modify storage smp:tmp wp.n10 set value $(n10)',
    f'execute if score #wp_c smp matches 0 run return run function {NS}:wp/del_ask with storage smp:tmp wp',
    '$data remove storage smp:wp p$(id).s$(n)',
    '$execute if score @s smp_wp_sel matches $(n) run function ' + f'{NS}:wp/off',
    '$tellraw @s ' + msg({'text': 'Wegpunkt $(n) geloescht.', 'color': 'green'}),
])
fn('wp/del_ask', ['$tellraw @s ' + msg({'text': '$(name) ($(x) $(y) $(z), $(dn)) wirklich loeschen? ', 'color': 'yellow'}, clk('[Ja, loeschen]', '/trigger wpdel set $(n10)', 'red', 'Endgueltig loeschen'))])
fn('wp/del_tod', [f'function {NS}:wp/id', f'function {NS}:wp/del_tod2 with storage smp:tmp'])
fn('wp/del_tod2', ['$data remove storage smp:wp p$(id).tod', f'execute if score @s smp_wp_sel matches 99 run function {NS}:wp/off',
                   'tellraw @s ' + msg({'text': 'Todesort vergessen.', 'color': 'green'})])
fn('wp/share', [
    'execute if score @s smp_cd_wps matches 1.. run return run ' + 'tellraw @s ' + msg({'text': 'Warte noch ', 'color': 'red'}, {'score': {'name': '@s', 'objective': 'smp_cd_wps'}, 'color': 'yellow'}, {'text': ' s.', 'color': 'red'}),
    f'execute unless score @s wpshare matches 1..{_MAX} run return run ' + _r('Welchen Wegpunkt? Liste: /trigger wpliste'),
    f'function {NS}:wp/id', 'execute store result storage smp:tmp n int 1 run scoreboard players get @s wpshare',
    f'function {NS}:wp/share2 with storage smp:tmp',
])
fn('wp/share2', [
    '$execute unless data storage smp:wp p$(id).s$(n) run return run ' + _r('Wegpunkt $(n) ist leer.'),
    'scoreboard players add #wp_code smp 1', 'scoreboard players set @s smp_cd_wps 10',
    '$data modify storage smp:tmp wp set from storage smp:wp p$(id).s$(n)',
    'execute store result storage smp:tmp wp.code int 1 run scoreboard players get #wp_code smp',
    f'function {NS}:wp/share3 with storage smp:tmp wp',
])
fn('wp/share3', [
    '$data modify storage smp:wp shared.c$(code) set from storage smp:tmp wp',
    '$tellraw @a ' + msg({'selector': '@s', 'color': 'yellow'}, {'text': ' teilt den Wegpunkt ', 'color': 'white'}, {'text': '$(name)', 'color': 'aqua'}, {'text': ' ($(x) $(y) $(z), $(dn))  ', 'color': 'gray'},
                         clk('[Uebernehmen]', '/trigger wpget set $(code)', 'green', 'In deine Wegpunkte speichern')),
])
fn('wp/get', [
    'execute unless score @s wpget matches 1.. run return run ' + _r('Geteilte Wegpunkte uebernimmst du mit dem Knopf im Chat.'),
    'execute store result storage smp:tmp code int 1 run scoreboard players get @s wpget',
    f'function {NS}:wp/get2 with storage smp:tmp',
])
fn('wp/get2', [
    '$execute unless data storage smp:wp shared.c$(code) run return run ' + _r('Diesen geteilten Wegpunkt gibt es nicht (mehr).'),
    f'function {NS}:wp/free',
    'execute if score #wp_n smp matches 0 run return run ' + _r(f'Alle {_MAX} Plaetze belegt – erst einen loeschen (/trigger wpliste).'),
    'execute store result storage smp:tmp n int 1 run scoreboard players get #wp_n smp',
    f'function {NS}:wp/get3 with storage smp:tmp',
])
fn('wp/get3', [
    '$data modify storage smp:wp p$(id).s$(n) set from storage smp:wp shared.c$(code)',
    '$data modify storage smp:wp p$(id).s$(n).n set value $(n)', '$data remove storage smp:wp p$(id).s$(n).code',
    '$tellraw @s ' + msg({'text': 'Uebernommen als Wegpunkt $(n). ', 'color': 'green'}, clk('[Verfolgen]', '/trigger wpgo set $(n)', 'green', 'Kompass + Lichtsaeule')),
])

# ---------------------------------------------------------------- Todesort (core/death hat #x #y #z gesetzt)
ON_DEATH.append(f'function {NS}:wp/death')
fn('wp/death', [
    f'function {NS}:wp/id',
    *[f'execute store result storage smp:tmp {a} int 1 run scoreboard players get #{a} smp' for a in 'xyz'],
    *_center_lines('#x smp', '#y smp', '#z smp'),
    *_dn_lines(),
    f'function {NS}:wp/death2 with storage smp:tmp',
])
fn('wp/death2', [
    '$data modify storage smp:wp p$(id).tod set value {n:99,name:"Todesort",x:$(x),y:$(y),z:$(z),xc:$(xc),zc:$(zc),yb:$(yb),dim:"$(dim)",dn:"$(dn)"}',
    'execute unless score @s smp_wp_sel matches 1.. run scoreboard players set @s smp_wp_sel 99',
    'execute unless score @s smp_wp_sel matches 1.. run scoreboard players set @s smp_wp_dist 0',
    'tellraw @s ' + msg({'text': 'Todesort als Wegpunkt gespeichert. ', 'color': 'gray'}, clk('[Verfolgen]', '/trigger wpgo set 99', 'green', 'Kompass + Lichtsaeule zum Todesort'), {'text': ' '},
                        clk('[Nicht verfolgen]', '/trigger wpoff', 'yellow', 'Kompass aus')),
])

# ---------------------------------------------------------------- Trigger, Hilfe, Esc-Menue
trigger('wp', f'{NS}:wp/menu', '/trigger wp', 'Wegpunkt-Menue: speichern, verfolgen (Kompass + Lichtsaeule nur fuer dich)', _C, ('◆ Wegpunkte', 'Wegpunkte speichern, verfolgen, teilen'))
trigger('wpset', f'{NS}:wp/set', '/trigger wpset', f'Wegpunkt an deiner Position speichern (bis {_MAX}; set 1<n> ueberschreibt Platz n)', _C)
trigger('wpname', f'{NS}:wp/name', '/trigger wpname', 'Namen fuer den zuletzt gespeicherten Wegpunkt waehlen', _C)
trigger('wpgo', f'{NS}:wp/go', '/trigger wpgo set <n>', 'Wegpunkt n verfolgen: Richtung + Entfernung unten, Lichtsaeule am Ziel (99 = Todesort)', _C)
trigger('wpoff', f'{NS}:wp/off', '/trigger wpoff', 'Verfolgung ausschalten', _C)
trigger('wpliste', f'{NS}:wp/list', '/trigger wpliste', 'Deine Wegpunkte als Chat-Liste mit Knoepfen', _C)
trigger('wpdel', f'{NS}:wp/del', '/trigger wpdel set <n>', 'Wegpunkt n loeschen (mit Rueckfrage)', _C)
trigger('wpshare', f'{NS}:wp/share', '/trigger wpshare set <n>', 'Wegpunkt n allen im Chat zeigen (Knopf zum Uebernehmen)', _C)
trigger('wpget', f'{NS}:wp/get', '/trigger wpget set <code>', 'Geteilten Wegpunkt uebernehmen (Knopf im Chat)', _C)
