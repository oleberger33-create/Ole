# OLE SMP – Server-Datapack

Rein vanilla Datapack fuer den Survival-Server **OLE SMP** (Minecraft 26.3, pack format 121). Laeuft komplett
serverseitig, Spieler brauchen keine Mods. Bedienung ueber `/trigger`-Befehle, klickbare Chat-Menues und das
Pause-Menue (Esc -> **SMP-Menue**).

## Bauen

```
cd smp
python3 build.py <out_dir>        # 26.3 (min_format 121)  -> <out_dir>/smp/ und <out_dir>/smp.zip
python3 build.py <out_dir> 101    # 26.1-Testserver (mineflayer-Bots)
SMP_MODULES=info,tp python3 build.py <out_dir>   # nur einzelne Module (zum Entwickeln)
```

`build.py` ist der Kern (Objectives, Trigger-Dispatch, Hilfe, Esc-Menue, Warm-ups, Cooldowns, Zurueck-Position,
Erst-Join, Tod/Respawn). Jede Datei in `modules/*.py` wird am Ende ausgefuehrt und haengt sich ueber die
Registries ein (`trigger()`, `warmup()`, `cooldown()`, `player_menu()`, `EXTRA_LOAD/TICK/SECOND`, `ON_JOIN/REJOIN/DEATH/RESPAWN`).

## Deploy (Nitrado)

`smp.zip` nach `<welt>/datapacks/` hochladen. Neue oder geaenderte **Funktionen** reichen mit `/reload`; neue
Knoepfe im Esc-Menue (Dialog-Registry `data/smp/dialog/menu.json`) brauchen einen **Server-Neustart**.
Wird das Pack in eine bestehende Welt eingebaut, den Spawn-Platz einmal von Hand setzen:
`/function smp:spawn/build_here` (als Spieler, an der gewuenschten Stelle; setzt auch den Weltspawn).

## Befehle fuer Spieler

| Befehl | Wirkung |
|---|---|
| `/trigger hilfe` | alle Befehle (klickbar) |
| `/trigger regeln` | Server-Regeln |
| `/trigger menu` | SMP-Menue (auch Esc -> SMP-Menue) |
| `/trigger spawn` | zum Spawn-Platz (3 s nicht bewegen) |
| `/trigger sethome` / `set 2` / `set 3` | Home 1–3 an der eigenen Position setzen |
| `/trigger home` / `set 2` / `set 3` | zu Home 1–3 (3 s Warm-up, 10 s Cooldown) |
| `/trigger homes` | Homes mit Knoepfen [Hin] [X] |
| `/trigger delhome set <n>` | Home loeschen (fragt erst nach) |
| `/trigger tpa` | Spielerliste zum Anklicken -> Teleport-Anfrage (30 s Cooldown) |
| `/trigger tpahier` | jemanden zu sich holen (Anfrage) |
| `/trigger tpaok set <nr>` / `tpanein set <nr>` | Anfrage annehmen/ablehnen (oder Knopf im Chat) |
| `/trigger rtp` | Zufalls-Teleport 1000–4000 Bloecke in die Wildnis (Oberwelt, alle 10 min) |
| `/trigger back` | zurueck zur Position vor dem letzten Teleport (30 s Cooldown) |
| `/trigger hud` | Koordinaten, Dimension, Himmelsrichtung, Uhrzeit in der Actionbar an/aus |
| `/trigger stats` | Spielzeit, Tode, Kills, Strecke, Spruenge |
| `/trigger top` | Top 5 der Online-Spieler |
| `/trigger online` | wer ist online (mit AFK) |
| `/trigger pos` | eigene Position fuer alle posten |
| `/trigger wp` | Wegpunkt-Menue (Dialog): verfolgen, speichern |
| `/trigger wpset` | Wegpunkt an der eigenen Position speichern (bis 10; `set 1<n>` ueberschreibt Platz n), danach Namens-Dialog |
| `/trigger wpgo set <n>` | Wegpunkt verfolgen: Richtungspfeil + Entfernung in der Actionbar, Lichtsaeule am Ziel (nur fuer dich sichtbar); 99 = Todesort |
| `/trigger wpoff` / `wpliste` / `wpdel set <n>` / `wpshare set <n>` | Verfolgung aus / Chat-Liste mit Knoepfen / loeschen (Rueckfrage) / mit allen teilen (Knopf zum Uebernehmen) |

Spieler-Nummern (`smp_id`) beginnen bei 2: der Wert 1 ist das, was ein nacktes `/trigger <x>` setzt.

## Automatik

- Erst-Join: Begruessung, Starter-Kit (8 Brot, Steinspitzhacke, Steinaxt, 16 Fackeln), Spieler-Nummer.
- Der **Spawn-Platz** (Ringstrasse, Podest, Laternen, Baenke, 3 Info-Waende mit Hologrammen: Befehle, Regeln,
  Willkommen, Leaderboards Spielzeit/Tode/Mob-Kills) wird automatisch an der Join-Position des ersten wirklich
  neuen Spielers (= Weltspawn) gebaut und setzt den Weltspawn dorthin. Admin: `/function smp:spawn/build_here`.
- Tod: Koordinaten im Chat, persistenter Todeszaehler (`smp_tode`), Todesort als Wegpunkt (wird verfolgt, wenn gerade kein anderer aktiv ist).
- AFK nach 5 min ohne Bewegung (grauer `[AFK]`-Suffix), Schlaf-Hinweis (1 Spieler reicht, `players_sleeping_percentage 1`),
  keine Phantome, Spielstunden in der Tab-Liste.

## Daten

- Scoreboard: `smp` (Konstanten/Scratch, `#next_id`, `#smp_v`), `smp_id`, `smp_tode`, `smp_mkills`, Trigger-Objectives, Cooldowns `smp_cd_*`.
- Storage: `smp:back p<id>` (Zurueck-Position), `smp:homes p<id>.h<n>`, `smp:tp center` (RTP-Mitte), `smp:spawn` (Platz, Spielernamen),
  `smp:wp p<id>.s<n>` / `p<id>.tod` / `shared.c<code>` (Wegpunkte), `smp:tmp` (Scratch).
- Modul-Hooks fuer das Info-HUD: `HUD_PRE` (Befehle vor der Actionbar-Zeile) und `HUD_PARTS` (angehaengte Textbausteine), `EXTRA_FINISH`
  (Generatoren, die erst in `finish()` laufen, damit spaetere Module ihre Teile eintragen koennen).

## Testen

26.3: Testserver mit dem 121-Build, `/reload`, Log auf Fehler pruefen. 26.1 + mineflayer-Bots (101-Build) fuer
Spielerpfade (Join, Warm-ups, TPA, RTP, Tod). Siehe `/tmp/mc/AGENT_GUIDE.md` in der Session.

## Ole's Farmhelper (nur fuer einen Spieler)

Das bestehende Datapack `OlesFarmhelper.zip` (Namespace `ofh`, Farm-Baupläne mit Geisterblöcken) läuft auf dem SMP nur
für einen Spieler: `tools/farmhelper_nur_fuer.py <original.zip> <Spielername> <ausgabe.zip>` beschränkt Item-Vergabe,
Rechtsklick-Menü und `/trigger ofh.t` auf diesen Namen und entfernt das Craft-Rezept. Item erneut holen:
`/trigger ofh.t set 9099` (oder als Op `/function ofh:item`). Das Item-Modell braucht client-seitig das Resourcepack
`ole_farmhelper_ressourcen.zip` (liegt im Server-Root).
