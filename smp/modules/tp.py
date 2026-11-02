# ---- Modul tp: Homes (3 pro Spieler), TPA / TPA-hier, Zufalls-Teleport (RTP), Zurueck ------------------------------
# Storage: smp:homes p<id>.h<n> {n,x,y,z,dim,xi,yi,zi,dn}   (xi/yi/zi = Blockkoordinaten, dn = Dimensionsname)
#          smp:tp center {x,z}  RTP-Mitte (automatisch: Join-Position des ersten neuen Spielers, sonst der Spawn-Platz; Admin: function smp:tp/rtp_center)
#          smp:tp dest          Scratch fuer /trigger back
# Trigger delhome: set n (1..3) fragt nach, set 1n (11..13) loescht wirklich (Knopf [Ja] der Rueckfrage).
# Scores:  smp_tp_n (gewaehltes Home), smp_tpa_to (Ziel-Id der offenen Anfrage), smp_tpa_t (Restzeit s), smp_tpa_mode (0 tpa / 1 tpahier),
#          smp_tpa_dest (Id des Spielers, zu dem der Teleport geht), smp_tpa_m (0 = ich bin Anfrager, 1 = ich bin Annehmer)
#          smp_rtp_try (RTP-Versuche, Tag smp_rtp_run waehrend der Suche)
# Cooldowns (Sekunden): smp_cd_home, smp_cd_tpa, smp_cd_rtp, smp_cd_back; smp_tpa_t = Restzeit der offenen Anfrage
_C = 'Teleport'
_HOME_CD, _TPA_CD, _RTP_CD, _BACK_CD, _TPA_TTL = 10, 30, 600, 30, 60
_RTP_MIN, _RTP_MAX, _RTP_TRIES = 1000, 4000, 8

for _o in ('smp_tp_n', 'smp_tpa_to', 'smp_tpa_mode', 'smp_tpa_dest', 'smp_tpa_m'):
    EXTRA_LOAD.append(f'scoreboard objectives add {_o} dummy')
for _o in ('smp_cd_home', 'smp_cd_tpa', 'smp_cd_rtp', 'smp_cd_back', 'smp_tpa_t'):
    cooldown(_o)


def _red(t):
    return 'tellraw @s ' + msg({'text': t, 'color': 'red'})


def _wait(obj):
    return 'tellraw @s ' + msg({'text': 'Warte noch ', 'color': 'red'}, {'score': {'name': '@s', 'objective': obj}, 'color': 'yellow'}, {'text': ' s.', 'color': 'red'})


def _sel(sel, color='yellow'):
    return {'selector': sel, 'color': color}


def _sc(name, obj='smp', color='white'):
    return {'score': {'name': name, 'objective': obj}, 'color': color}


# Blockposition von @s -> Scores #px #py #pz und storage smp:tmp xi yi zi  (`data get ... 1` rundet ab, auch bei negativen Werten: -37.5 -> -38)
fn('tp/pos', [
    *[f'execute store result score #p{a} smp run data get entity @s Pos[{i}] 1' for i, a in enumerate('xyz')],
    *[f'execute store result storage smp:tmp {a}i int 1 run scoreboard players get #p{a} smp' for a in 'xyz'],
])

# ------------------------------------------------------------------ Homes
fn('tp/sethome', [
    f'execute unless score @s sethome matches 1..3 run return run {_red("Es gibt Home 1, 2 und 3: /trigger sethome set 2")}',
    'execute store result storage smp:tmp id int 1 run scoreboard players get @s smp_id',
    'execute store result storage smp:tmp n int 1 run scoreboard players get @s sethome',
    *[f'data modify storage smp:tmp {a} set from entity @s Pos[{i}]' for i, a in enumerate('xyz')],       # exakte Position (store result wuerde abrunden)
    f'function {NS}:tp/pos',
    f'function {NS}:core/dim',
    *[f'execute if dimension {d} run data modify storage smp:tmp dn set value "{name}"' for d, name, _ in DIMS],
    f'function {NS}:tp/home_put with storage smp:tmp',
])
fn('tp/home_put', [
    '$data modify storage smp:homes p$(id).h$(n) set value {n:$(n),x:$(x),y:$(y),z:$(z),dim:"$(dim)",xi:$(xi),yi:$(yi),zi:$(zi),dn:"$(dn)"}',
    '$tellraw @s ' + msg({'text': 'Home $(n) gesetzt: ', 'color': 'green'}, {'text': '$(xi) / $(yi) / $(zi)', 'color': 'white'},
                         {'text': ' ($(dn)). ', 'color': 'gray'}, clk('[Hin]', '/trigger home set $(n)', 'yellow', 'Zu Home $(n) teleportieren')),
])
fn('tp/home', [
    f'execute unless score @s home matches 1..3 run return run {_red("Es gibt Home 1, 2 und 3: /trigger home set 2")}',
    f'execute if score @s smp_cd_home matches 1.. run return run {_wait("smp_cd_home")}',
    'execute store result storage smp:tmp id int 1 run scoreboard players get @s smp_id',
    'execute store result storage smp:tmp n int 1 run scoreboard players get @s home',
    f'function {NS}:tp/home_start with storage smp:tmp',
])
fn('tp/home_start', [
    '$execute unless data storage smp:homes p$(id).h$(n) run return run tellraw @s ' + msg({'text': 'Home $(n) ist nicht gesetzt. ', 'color': 'red'}, clk('[Hier setzen]', '/trigger sethome set $(n)', 'yellow', 'Home $(n) an deiner Position setzen')),
    '$scoreboard players set @s smp_tp_n $(n)',
    f'function {NS}:core/warm_home',
])
fn('tp/home_go', [          # Warmup-Ziel (als Spieler, am Spieler)
    'execute store result storage smp:tmp id int 1 run scoreboard players get @s smp_id',
    'execute store result storage smp:tmp n int 1 run scoreboard players get @s smp_tp_n',
    f'function {NS}:tp/home_go2 with storage smp:tmp',
])
fn('tp/home_go2', [
    '$execute unless data storage smp:homes p$(id).h$(n) run return run ' + _red('Home $(n) gibt es nicht mehr.'),
    'tag @s remove smp_rtp_run',
    f'function {NS}:core/back_save',
    f'$function {NS}:core/tp with storage smp:homes p$(id).h$(n)',
    f'scoreboard players set @s smp_cd_home {_HOME_CD}',
    '$tellraw @s ' + msg({'text': 'Du bist bei Home $(n).', 'color': 'green'}),
])
fn('tp/delhome', [        # set 1..3 = Rueckfrage, set 11..13 = wirklich loeschen (Knopf [Ja] der Rueckfrage)
    'scoreboard players set #del smp 0',
    'execute if score @s delhome matches 11..13 run scoreboard players set #del smp 1',
    'execute if score @s delhome matches 11..13 run scoreboard players remove @s delhome 10',
    f'execute unless score @s delhome matches 1..3 run return run {_red("Welches Home? /trigger delhome set 1 (oder 2, 3)")}',
    'execute store result storage smp:tmp id int 1 run scoreboard players get @s smp_id',
    'execute store result storage smp:tmp n int 1 run scoreboard players get @s delhome',
    f'function {NS}:tp/home_del0 with storage smp:tmp',
])
fn('tp/home_del0', [      # Home-Daten (xi yi zi dn) fuer die Rueckfrage in smp:tmp kopieren, dann home_del
    '$execute unless data storage smp:homes p$(id).h$(n) run return run ' + _red('Home $(n) ist nicht gesetzt.'),
    '$data modify storage smp:tmp xi set from storage smp:homes p$(id).h$(n).xi',
    '$data modify storage smp:tmp yi set from storage smp:homes p$(id).h$(n).yi',
    '$data modify storage smp:tmp zi set from storage smp:homes p$(id).h$(n).zi',
    '$data modify storage smp:tmp dn set from storage smp:homes p$(id).h$(n).dn',
    f'function {NS}:tp/home_del with storage smp:tmp',
])
fn('tp/home_del', [       # #del smp = 1, wenn der Trigger-Wert 11..13 war (bestaetigt)
    '$execute unless data storage smp:homes p$(id).h$(n) run return run ' + _red('Home $(n) ist nicht gesetzt.'),
    '$execute if score #del smp matches 0 run return run tellraw @s ' + msg({'text': 'Home $(n) ($(xi) / $(yi) / $(zi), $(dn)) wirklich loeschen? ', 'color': 'yellow'},
                                                                              clk('[Ja, loeschen]', '/trigger delhome set 1$(n)', 'red', 'Home $(n) endgueltig loeschen')),
    '$data remove storage smp:homes p$(id).h$(n)',
    '$tellraw @s ' + msg({'text': 'Home $(n) geloescht.', 'color': 'green'}),
])
fn('tp/homes', [
    'execute store result storage smp:tmp id int 1 run scoreboard players get @s smp_id',
    f'function {NS}:tp/homes_list with storage smp:tmp',
])
fn('tp/homes_list', [
    '$execute store result score #hn smp run data get storage smp:homes p$(id)',
    'execute if score #hn smp matches ..0 run return run tellraw @s ' + msg({'text': 'Du hast noch kein Home. ', 'color': 'gray'}, clk('[Home 1 hier setzen]', '/trigger sethome', 'yellow', 'Home 1 an deiner Position setzen')),
    'tellraw @s ' + msg({'text': 'Deine Homes:', 'color': 'white'}),
    *[f'$execute if data storage smp:homes p$(id).h{n} run function {NS}:tp/homes_line with storage smp:homes p$(id).h{n}' for n in (1, 2, 3)],
    'execute if score #hn smp matches ..2 run tellraw @s ' + tc({'text': '   Weitere setzen: /trigger sethome set 2 (oder 3)', 'color': 'dark_gray'}),
])
fn('tp/homes_line', [
    '$tellraw @s ' + tc([{'text': '   Home $(n): ', 'color': 'yellow'}, {'text': '$(xi) / $(yi) / $(zi)', 'color': 'white'}, {'text': ' ($(dn))  ', 'color': 'gray'},
                        clk('[Hin]', '/trigger home set $(n)', 'green', 'Zu Home $(n) teleportieren'), {'text': ' '},
                        clk('[X]', '/trigger delhome set $(n)', 'red', 'Home $(n) loeschen')]),
])

# ------------------------------------------------------------------ TPA
_BTN = [clk('[Annehmen]', '/trigger tpaok set $(rid)', 'green', 'Anfrage annehmen'), {'text': ' '}, clk('[Ablehnen]', '/trigger tpanein set $(rid)', 'red', 'Anfrage ablehnen')]
player_menu('tpazu', 'Zu wem willst du dich teleportieren? (anklicken)')
player_menu('tpahol', 'Wen willst du zu dir holen? (anklicken)')
_MYNR = 'tellraw @s ' + tc([{'text': '   Deine Spieler-Nr.: ', 'color': 'dark_gray'}, _sc('@s', 'smp_id', 'gray')])
fn('tp/tpa', [
    f'execute if score @s tpa matches 1 run return run function {NS}:tp/tpa_list',
    'scoreboard players set #tpm smp 0',
    'execute store result storage smp:tmp tid int 1 run scoreboard players get @s tpa',
    f'function {NS}:tp/send',
])
fn('tp/tpa_list', [f'function {NS}:core/list_tpazu', _MYNR])
fn('tp/tpazu', ['scoreboard players set #tpm smp 0', 'execute store result storage smp:tmp tid int 1 run scoreboard players get @s tpazu', f'function {NS}:tp/send'])
fn('tp/tpahier', [
    f'execute if score @s tpahier matches 1 run return run function {NS}:tp/tpahier_list',
    'scoreboard players set #tpm smp 1',
    'execute store result storage smp:tmp tid int 1 run scoreboard players get @s tpahier',
    f'function {NS}:tp/send',
])
fn('tp/tpahier_list', [f'function {NS}:core/list_tpahol', _MYNR])
fn('tp/tpahol', ['scoreboard players set #tpm smp 1', 'execute store result storage smp:tmp tid int 1 run scoreboard players get @s tpahol', f'function {NS}:tp/send'])
fn('tp/send', [         # als Anfrager; storage smp:tmp tid = Ziel-Id, #tpm smp = Modus
    f'execute if score @s smp_cd_tpa matches 1.. run return run {_wait("smp_cd_tpa")}',
    'execute store result score #tid smp run data get storage smp:tmp tid',
    f'execute if score @s smp_id = #tid smp run return run {_red("Du kannst dich nicht zu dir selbst teleportieren.")}',
    'execute store result storage smp:tmp rid int 1 run scoreboard players get @s smp_id',
    'execute store result storage smp:tmp mode int 1 run scoreboard players get #tpm smp',
    f'function {NS}:tp/send2 with storage smp:tmp',
])
fn('tp/send2', [
    '$execute unless entity @a[scores={smp_id=$(tid)}] run return run ' + _red('Spieler Nr. $(tid) ist nicht online.'),
    'execute if score @s smp_tpa_to matches 1.. run tellraw @s ' + msg({'text': 'Deine vorherige Anfrage wurde ersetzt.', 'color': 'gray'}),
    '$scoreboard players set @s smp_tpa_to $(tid)',
    f'scoreboard players set @s smp_tpa_t {_TPA_TTL}',
    '$scoreboard players set @s smp_tpa_mode $(mode)',
    '$execute if score @s smp_tpa_mode matches 0 run tellraw @a[scores={smp_id=$(tid)}] ' + msg(_sel('@s'), {'text': ' moechte sich zu dir teleportieren. ', 'color': 'white'}, *_BTN),
    '$execute if score @s smp_tpa_mode matches 1 run tellraw @a[scores={smp_id=$(tid)}] ' + msg(_sel('@s'), {'text': ' moechte dich zu sich holen. ', 'color': 'white'}, *_BTN),
    '$tellraw @s ' + msg({'text': 'Anfrage an ', 'color': 'green'}, _sel('@a[scores={smp_id=$(tid)},limit=1]'), {'text': f' gesendet – gilt {_TPA_TTL} s.', 'color': 'green'}),
])
fn('tp/tpaok', ['execute store result storage smp:tmp rid int 1 run scoreboard players get @s tpaok', f'function {NS}:tp/accept with storage smp:tmp'])
fn('tp/accept', [        # als Annehmer
    '$execute unless entity @a[scores={smp_id=$(rid),smp_tpa_t=1..}] run return run ' + _red('Keine offene Anfrage (abgelaufen oder Spieler offline).'),
    '$execute unless score @a[scores={smp_id=$(rid)},limit=1] smp_tpa_to = @s smp_id run return run ' + _red('Keine offene Anfrage von diesem Spieler.'),
    'tag @s add smp_tpa_acc',
    f'$execute as @a[scores={{smp_id=$(rid)}},limit=1] run function {NS}:tp/accept2',
    'tag @s remove smp_tpa_acc',
])
fn('tp/accept2', [       # als Anfrager; Annehmer = @a[tag=smp_tpa_acc]
    f'execute if score @s smp_tpa_mode matches 0 run function {NS}:tp/accept_m0',
    f'execute if score @s smp_tpa_mode matches 1 run function {NS}:tp/accept_m1',
    'scoreboard players set @s smp_tpa_to 0',
    'scoreboard players set @s smp_tpa_t 0',
])
fn('tp/accept_m0', [     # tpa: der Anfrager (@s) kommt zum Annehmer
    'scoreboard players operation @s smp_tpa_dest = @a[tag=smp_tpa_acc,limit=1] smp_id',
    'scoreboard players set @s smp_tpa_m 0',
    'tellraw @s ' + msg(_sel('@a[tag=smp_tpa_acc]'), {'text': ' hat deine Anfrage angenommen.', 'color': 'green'}),
    'tellraw @a[tag=smp_tpa_acc] ' + msg({'text': 'Angenommen – ', 'color': 'green'}, _sel('@s'), {'text': ' kommt gleich zu dir.', 'color': 'green'}),
    f'execute at @s run function {NS}:core/warm_tpa',
])
fn('tp/accept_m1', [     # tpahier: der Annehmer kommt zum Anfrager (@s)
    'scoreboard players operation @a[tag=smp_tpa_acc] smp_tpa_dest = @s smp_id',
    'scoreboard players set @a[tag=smp_tpa_acc] smp_tpa_m 1',
    'tellraw @s ' + msg(_sel('@a[tag=smp_tpa_acc]'), {'text': ' hat angenommen und kommt gleich zu dir.', 'color': 'green'}),
    'tellraw @a[tag=smp_tpa_acc] ' + msg({'text': 'Angenommen – du wirst zu ', 'color': 'green'}, _sel('@s'), {'text': ' teleportiert.', 'color': 'green'}),
    f'execute as @a[tag=smp_tpa_acc] at @s run function {NS}:core/warm_tpa',
])
fn('tp/tpa_go', [        # Warmup-Ziel (als der Spieler, der sich bewegt)
    'execute store result storage smp:tmp d int 1 run scoreboard players get @s smp_tpa_dest',
    f'function {NS}:tp/tpa_go2 with storage smp:tmp',
])
fn('tp/tpa_go2', [
    '$execute unless entity @a[scores={smp_id=$(d)}] run return run ' + _red('Der andere Spieler ist nicht mehr online.'),
    'tag @s remove smp_rtp_run',
    f'function {NS}:core/back_save',
    '$execute at @a[scores={smp_id=$(d)},limit=1] run tp @s ~ ~ ~',
    '$tellraw @s ' + msg({'text': 'Du bist jetzt bei ', 'color': 'green'}, _sel('@a[scores={smp_id=$(d)},limit=1]'), {'text': '.', 'color': 'green'}),
    '$tellraw @a[scores={smp_id=$(d)}] ' + msg(_sel('@s'), {'text': ' ist jetzt bei dir.', 'color': 'green'}),
    f'execute if score @s smp_tpa_m matches 0 run scoreboard players set @s smp_cd_tpa {_TPA_CD}',
    f'$execute if score @s smp_tpa_m matches 1 run scoreboard players set @a[scores={{smp_id=$(d)}}] smp_cd_tpa {_TPA_CD}',
])
fn('tp/tpanein', ['execute store result storage smp:tmp rid int 1 run scoreboard players get @s tpanein', f'function {NS}:tp/deny with storage smp:tmp'])
fn('tp/deny', [
    '$execute unless entity @a[scores={smp_id=$(rid),smp_tpa_t=1..}] run return run ' + _red('Keine offene Anfrage (abgelaufen oder Spieler offline).'),
    '$execute unless score @a[scores={smp_id=$(rid)},limit=1] smp_tpa_to = @s smp_id run return run ' + _red('Keine offene Anfrage von diesem Spieler.'),
    'tag @s add smp_tpa_acc',
    f'$execute as @a[scores={{smp_id=$(rid)}},limit=1] run function {NS}:tp/deny2',
    'tag @s remove smp_tpa_acc',
])
fn('tp/deny2', [         # als Anfrager
    'scoreboard players set @s smp_tpa_to 0',
    'scoreboard players set @s smp_tpa_t 0',
    'tellraw @s ' + msg(_sel('@a[tag=smp_tpa_acc]'), {'text': ' hat deine Anfrage abgelehnt.', 'color': 'red'}),
    'tellraw @a[tag=smp_tpa_acc] ' + msg({'text': 'Du hast die Anfrage von ', 'color': 'gray'}, _sel('@s'), {'text': ' abgelehnt.', 'color': 'gray'}),
])
fn('tp/expire', [        # als Anfrager, wenn smp_tpa_t abgelaufen ist (jede Sekunde geprueft)
    'execute store result storage smp:tmp tid int 1 run scoreboard players get @s smp_tpa_to',
    'scoreboard players set @s smp_tpa_to 0',
    f'function {NS}:tp/expire2 with storage smp:tmp',
])
fn('tp/expire2', [
    '$tellraw @a[scores={smp_id=$(tid)}] ' + msg({'text': 'Die Anfrage von ', 'color': 'gray'}, _sel('@s'), {'text': ' ist abgelaufen.', 'color': 'gray'}),
    '$execute if entity @a[scores={smp_id=$(tid)}] run tellraw @s ' + msg({'text': 'Deine Anfrage an ', 'color': 'gray'}, _sel('@a[scores={smp_id=$(tid)},limit=1]'), {'text': ' ist abgelaufen.', 'color': 'gray'}),
    '$execute unless entity @a[scores={smp_id=$(tid)}] run tellraw @s ' + msg({'text': 'Deine Teleport-Anfrage ist abgelaufen.', 'color': 'gray'}),
])
EXTRA_SECOND.append(f'execute as @a[scores={{smp_tpa_to=1..,smp_tpa_t=..0}}] run function {NS}:tp/expire')

# ------------------------------------------------------------------ RTP (nur Oberwelt, 1000-4000 Bloecke von der Mitte)
# spreadplayers sucht die Oberflaeche (kein Wasser/Lava) und laedt/generiert den Ziel-Chunk dabei synchron (wie ein /tp in
# unerforschtes Gebiet: ca. 0.2-0.9 s Server-Haenger pro Versuch). Deshalb nur EIN Versuch pro Sekunde (Tag smp_rtp_run,
# Zaehler smp_rtp_try am Spieler), damit sich die Haenger nicht zu einem langen addieren. Getestet und verworfen: forceload-Vorladen
# im Warmup ist in 26.x ebenfalls synchron (3 Chunks = 3x so lang), `execute if biome` geht nicht in ungeladenen Chunks.
EXTRA_LOAD.append('scoreboard objectives add smp_rtp_try dummy')
# Landeflaechen, auf denen nochmal gewuerfelt wird (spreadplayers meidet nur Wasser/Lava/Feuer): Baumkronen, Pulverschnee, Kakteen, Magma, ...
js(f'data/{NS}/tags/block/rtp_bad.json', {'replace': False, 'values': [
    '#minecraft:leaves', '#minecraft:campfires', '#minecraft:fire',
    *[{'id': f'minecraft:{b}', 'required': False} for b in ['powder_snow', 'cactus', 'magma_block', 'sweet_berry_bush', 'pointed_dripstone', 'cobweb']]]})
fn('tp/rtp', [
    f'execute unless dimension minecraft:overworld run return run {_red("RTP geht nur in der Oberwelt.")}',
    f'execute if score @s smp_cd_rtp matches 1.. run return run function {NS}:tp/rtp_wait',
    f'execute if entity @s[tag=smp_rtp_run] run return run {_red("Suche laeuft schon – einen Moment.")}',
    f'function {NS}:core/warm_rtp',
])
fn('tp/rtp_wait', [
    'scoreboard players operation #m smp = @s smp_cd_rtp', 'scoreboard players operation #m smp /= #60 smp',
    'scoreboard players operation #s smp = @s smp_cd_rtp', 'scoreboard players operation #s smp %= #60 smp',
    'tellraw @s ' + msg({'text': 'RTP geht erst wieder in ', 'color': 'red'}, _sc('#m', 'smp', 'yellow'), {'text': ' min ', 'color': 'red'}, _sc('#s', 'smp', 'yellow'), {'text': ' s.', 'color': 'red'}),
])
fn('tp/rtp_go', [        # Warmup-Ziel: Suche starten, erster Versuch sofort, weitere jede Sekunde (EXTRA_SECOND)
    f'execute unless dimension minecraft:overworld run return run {_red("RTP geht nur in der Oberwelt.")}',
    f'execute unless data storage smp:tp center if data storage smp:spawn blk run function {NS}:tp/center_spawn',   # noch keine Mitte: Spawn-Platz
    f'function {NS}:core/back_save',
    'scoreboard players set @s smp_rtp_try 0',
    'tag @s add smp_rtp_run',
    f'function {NS}:tp/rtp_step',
])
EXTRA_SECOND.append(f'execute as @a[tag=smp_rtp_run] at @s run function {NS}:tp/rtp_step')
fn('tp/rtp_step', [      # ein Versuch: Zufallspunkt -> spreadplayers (Oberflaeche, kein Wasser/Lava); auf #smp:rtp_bad (Baumkronen, Pulverschnee, ...) neu wuerfeln
    f'execute unless dimension minecraft:overworld run return run function {NS}:tp/rtp_abort',
    'scoreboard players add @s smp_rtp_try 1',
    f'execute if score @s smp_rtp_try matches {_RTP_TRIES + 1}.. run return run function {NS}:tp/rtp_fail',
    f'function {NS}:tp/rtp_rand',
    'execute store result storage smp:tmp x int 1 run scoreboard players get #rx smp',
    'execute store result storage smp:tmp z int 1 run scoreboard players get #rz smp',
    f'function {NS}:tp/rtp_spread with storage smp:tmp',
    f'execute if score #ok smp matches 0 run return run function {NS}:tp/rtp_retry',
    f'execute if score @s smp_rtp_try matches ..{_RTP_TRIES - 2} at @s if block ~ ~-1 ~ #{NS}:rtp_bad run return run function {NS}:tp/rtp_retry',
    f'function {NS}:tp/rtp_done',
])
fn('tp/rtp_retry', ['execute if score @s smp_rtp_try matches 1 run tellraw @s ' + msg({'text': 'Dort ist nur Wasser – ich suche weiter ...', 'color': 'gray'})])
fn('tp/rtp_rand', [      # Zufallsversatz mit Abstand _RTP_MIN.._RTP_MAX (Kreisring) um die Mitte -> #rx #rz
    f'execute store result score #dx smp run random value -{_RTP_MAX}..{_RTP_MAX}',
    f'execute store result score #dz smp run random value -{_RTP_MAX}..{_RTP_MAX}',
    'scoreboard players operation #d2 smp = #dx smp', 'scoreboard players operation #d2 smp *= #dx smp',
    'scoreboard players operation #dz2 smp = #dz smp', 'scoreboard players operation #dz2 smp *= #dz smp',
    'scoreboard players operation #d2 smp += #dz2 smp',
    f'execute unless score #d2 smp matches {_RTP_MIN * _RTP_MIN}..{_RTP_MAX * _RTP_MAX} run return run function {NS}:tp/rtp_rand',
    'execute store result score #rx smp run data get storage smp:tp center.x',
    'execute store result score #rz smp run data get storage smp:tp center.z',
    'scoreboard players operation #rx smp += #dx smp',
    'scoreboard players operation #rz smp += #dz smp',
])
fn('tp/rtp_spread', ['$execute in minecraft:overworld store success score #ok smp run spreadplayers $(x) $(z) 0 1 false @s'])
fn('tp/rtp_done', [
    'tag @s remove smp_rtp_run',
    'effect give @s minecraft:resistance 5 4 true',
    'effect give @s minecraft:slow_falling 5 0 true',
    f'scoreboard players set @s smp_cd_rtp {_RTP_CD}',
    f'function {NS}:tp/pos',
    'tellraw @s ' + msg({'text': 'Zufalls-Teleport! Du bist jetzt bei ', 'color': 'green'}, _sc('#px'), {'text': ' / ', 'color': 'gray'}, _sc('#py'),
                        {'text': ' / ', 'color': 'gray'}, _sc('#pz'), {'text': '. Viel Glueck!', 'color': 'green'}),
])
fn('tp/rtp_abort', ['tag @s remove smp_rtp_run', _red('RTP abgebrochen – du bist nicht mehr in der Oberwelt.')])
fn('tp/rtp_fail', ['tag @s remove smp_rtp_run', _red('Kein sicherer Platz gefunden (nur Wasser?) – versuch es gleich nochmal.')])
# RTP-Mitte = Weltspawn: beim allerersten Join (Spieler steht am Spawn) automatisch gesetzt; Admin: als Spieler `function smp:tp/rtp_center`
fn('tp/center_set', [
    f'function {NS}:tp/pos',
    'execute store result storage smp:tp center.x int 1 run scoreboard players get #px smp',
    'execute store result storage smp:tp center.z int 1 run scoreboard players get #pz smp',
])
fn('tp/center_spawn', ['data modify storage smp:tp center.x set from storage smp:spawn blk.x', 'data modify storage smp:tp center.z set from storage smp:spawn blk.z'])
fn('tp/rtp_center', [
    f'function {NS}:tp/center_set',
    'tellraw @s ' + msg({'text': 'RTP-Mitte gesetzt: ', 'color': 'green'}, _sc('#px'), {'text': ' / ', 'color': 'gray'}, _sc('#pz')),
])
ON_JOIN.append(f'execute at @s if dimension minecraft:overworld unless data storage smp:tp center run function {NS}:tp/center_set')
ON_REJOIN.append('tag @s remove smp_rtp_run')

# ------------------------------------------------------------------ Zurueck (Position vor dem letzten Teleport, core/back_save)
fn('tp/back', [
    f'execute if score @s smp_cd_back matches 1.. run return run {_wait("smp_cd_back")}',
    'execute store result storage smp:tmp id int 1 run scoreboard players get @s smp_id',
    f'function {NS}:tp/back_start with storage smp:tmp',
])
fn('tp/back_start', [
    '$execute unless data storage smp:back p$(id).has run return run ' + _red('Keine letzte Position gespeichert.'),
    f'function {NS}:core/warm_back',
])
fn('tp/back_go', [       # Warmup-Ziel
    'execute store result storage smp:tmp id int 1 run scoreboard players get @s smp_id',
    f'function {NS}:tp/back_go2 with storage smp:tmp',
])
fn('tp/back_go2', [
    '$execute unless data storage smp:back p$(id).has run return run ' + _red('Keine letzte Position gespeichert.'),
    '$data modify storage smp:tp dest set from storage smp:back p$(id)',
    'tag @s remove smp_rtp_run',
    f'function {NS}:core/back_save',        # damit /trigger back erneut hierher zurueckfuehrt
    f'function {NS}:core/tp with storage smp:tp dest',
    f'scoreboard players set @s smp_cd_back {_BACK_CD}',
    'tellraw @s ' + msg({'text': 'Zurueck an deiner letzten Position.', 'color': 'green'}),
])

# ------------------------------------------------------------------ Warmups, Trigger, Hilfe, Esc-Menue
warmup('home', f'{NS}:tp/home_go')
warmup('tpa', f'{NS}:tp/tpa_go')
warmup('rtp', f'{NS}:tp/rtp_go')
warmup('back', f'{NS}:tp/back_go')
trigger('home', f'{NS}:tp/home', '/trigger home', 'Zu Home 1 teleportieren (set 2 / set 3 fuer Home 2 und 3)', _C, ('Home', 'Zu deinem Home 1 teleportieren'))
trigger('sethome', f'{NS}:tp/sethome', '/trigger sethome', 'Home 1 hier setzen (set 2 / set 3 fuer Home 2 und 3)', _C, ('Home setzen', 'Home 1 an deiner Position setzen'))
trigger('homes', f'{NS}:tp/homes', '/trigger homes', 'Deine Homes anzeigen (mit Knoepfen)', _C, ('Homes', 'Deine Homes anzeigen'))
trigger('delhome', f'{NS}:tp/delhome', '/trigger delhome set <n>', 'Home n loeschen (mit Rueckfrage)', _C)
trigger('tpa', f'{NS}:tp/tpa', '/trigger tpa', 'Zu einem Spieler teleportieren (Anfrage; Liste zum Anklicken)', _C, ('TPA', 'Zu einem Spieler teleportieren (Anfrage)'))
trigger('tpazu', f'{NS}:tp/tpazu', '/trigger tpazu set <nr>', 'Teleport-Anfrage an Spieler-Nr. <nr>', _C)
trigger('tpahier', f'{NS}:tp/tpahier', '/trigger tpahier', 'Einen Spieler zu dir holen (Anfrage; Liste)', _C)
trigger('tpahol', f'{NS}:tp/tpahol', '/trigger tpahol set <nr>', 'Spieler-Nr. <nr> zu dir holen (Anfrage)', _C)
trigger('tpaok', f'{NS}:tp/tpaok', '/trigger tpaok set <nr>', 'Teleport-Anfrage von Spieler-Nr. <nr> annehmen (oder Knopf klicken)', _C)
trigger('tpanein', f'{NS}:tp/tpanein', '/trigger tpanein set <nr>', 'Teleport-Anfrage ablehnen (oder Knopf klicken)', _C)
trigger('rtp', f'{NS}:tp/rtp', '/trigger rtp', 'Zufalls-Teleport weit weg in die Wildnis (Oberwelt, alle 10 min)', _C, ('RTP', 'Zufalls-Teleport in die Wildnis'))
trigger('back', f'{NS}:tp/back', '/trigger back', 'Zurueck zur Position vor deinem letzten Teleport', _C, ('Zurueck', 'Zur Position vor dem letzten Teleport'))
