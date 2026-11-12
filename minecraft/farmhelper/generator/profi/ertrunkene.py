"""Ertrunkenen-Farm (Profi): ein großer dunkler Wasserblock über einer Schilderdecke im Flussbiom, darunter
fließendes Wasser, das alle Ertrunkenen in den bewährten Schacht der einfachen Farm schiebt.

Querschnitt (Höhen im Plan, Füße beim Start = 0):
  10      Dach: Stufen (obere Hälfte) mit Wasser darin (Wassereimer) – Lichtschutz und Wasserquelle jeder Spalte
  0 … 9   fallendes Wasser, Wand aus Bruchstein (Ring 36 je Schicht)          → Spawnplätze
  -1      fallendes Wasser über den Schildern (gegraben, Wände = Erdreich)
  -2      Schilderdecke (70 Schilder); 26 Randfelder ohne Schild: dort fällt das Wasser bis auf den Boden
  -3      Grubenboden mit fließendem Wasser, strömt von den Randlücken zur Mitte
  -4      Boden; in der Mitte das Schachtloch 2 × 2 mit 4 Schildern
  -5…-25  Schacht (Luft); -26 Trichter (Landestelle), -27 Trichter + Truhe; Spieler (7, -26, 4)
Feld x 0 … 9, z 0 … 9 ohne die 4 Ecken (96 Spalten); Schacht x 4 … 5, z 4 … 5.

Schilderdecke: Wandschilder (Anker) an der Westwand in z 2, 4, 6 und an der Ostwand in z 3, 5, 7; von dort laufen die
Reihen quer durch (jedes Schild hängt am vorigen). Die Reihen z 1 und z 8 hängen an den Reihen z 2 bzw. z 7.
Die Bodenströmung ist durchgerechnet: Von jedem der 96 Bodenfelder führt sie ins Loch (keine Ecke, in der etwas
stehen bleibt – deshalb sind die Ecken des Felds aus festem Block und die Anker nicht neben den Ecken).
"""
from profi_basis import *

f = profi("ertrunkene", dict(
    name="Ertrunkenen-Farm mit Wasserturm (Profi)", diff=4, out="Kupfer, Dreizacke, Nautilusschalen",
    where="Flussbiom (F3: minecraft:river) – alle 12 × 12 Spalten; fester Boden, Füße beim Start auf Höhe 64 oder "
          "höher",
    afk="Ja – unten neben der Landestelle stehen und zuschlagen; sie kommen von selbst",
    why="Die einfache Farm hat ein Becken 6 × 6 mit nur einer Spawn-Schicht – im Test kam 1 Ertrunkener pro Stunde. "
        "Im Flussbiom spawnen Ertrunkene aber in jedem dunklen Wasser, das mindestens 2 Blöcke tief ist, auch in "
        "fallendem Wasser und in jeder Höhe. Darum steht hier über einer Schilderdecke ein Wasserblock 10 × 10 "
        "(ohne Ecken) und 11 Schichten hoch: Das Dach aus Stufen in der oberen Blockhälfte hält das Licht draußen, "
        "und weil jede Stufe Wasser enthält (Wassereimer), fällt in jeder Spalte Wasser bis auf die Schilder – "
        "zusammen über 900 Spawnplätze statt 36. Ein Ertrunkener sinkt durch die Schilder auf den Grubenboden. "
        "Am Rand hat die Schilderdecke 26 Lücken: Dort fällt das Wasser bis auf den Boden und strömt von allen Seiten "
        "zur Mitte. Es schiebt jeden Ertrunkenen ins Schachtloch; die Schilder im Loch halten das Wasser. Der Schacht "
        "ist derselbe wie bei der einfachen Farm: 22 Blöcke Fall, unten kommen sie mit wenig Leben an. Du stehst "
        "daneben und triffst ihre Beine durch den Spalt – sie dich nicht. Dreizacke und Kupfer gibt es nur, wenn du "
        "tötest.",
    help=[["Keine Ertrunkenen", "Alle Spalten müssen im Flussbiom liegen (F3 an den Ecken prüfen). Innen kein "
                                "Licht: Wand und Stufendach dicht, keine Fackel im Wasser."],
          ["Nachts kommt nichts herunter", "Unter Höhe 61 schwimmen Ertrunkene nachts nach oben. Der Grubenboden "
                                           "liegt 4 unter deinen Füßen beim Start – starte also auf Höhe 64 oder "
                                           "höher, dann liegt alles Wasser darüber."],
          ["Wasser läuft in den Schacht", "Die 4 Schilder im Schachtloch (Höhe -4) müssen sitzen, bevor Wasser "
                                          "kommt, und die Schilderdecke darf nur am Rand Lücken haben (26 Felder)."],
          ["Grubenboden bleibt trocken", "Über den 26 Randfeldern ohne Schild muss das Wasser bis auf den Boden "
                                         "fallen – dort kein Schild setzen. Jede der 96 Stufen braucht Wasser."]],
    meta=m("Rate: etwa 30 Ertrunkene pro Stunde (Schätzung nach den Spawnregeln: 916 statt 36 Spawnplätze, die "
           "einfache Farm brachte im Test 1 pro Stunde). 6,25 % tragen einen Dreizack, der nur bei "
           "deinem Schlag mit 8,5 % fällt (Plünderung +1 % je Stufe) – grob 1 Dreizack in 6 Stunden; Kupferbarren "
           "11 %.",
           [("Flussbiom: dort spawnen Ertrunkene in jeder Höhe in Wasser ab 2 Blöcken Tiefe, auch in fließendem "
             "Wasser (im Ozean nur unter Y 58).", W + "Drowned#Spawning")],
           [("Spawnraum aus vielen Wasserschichten über einer Schilderdecke; Ertrunkene sinken durch die Schilder auf "
             "fließendes Wasser, das sie in das Loch zum Fallschacht schiebt.", W + "Tutorial:Drowned_farming"),
            ("Schilder lassen Mobs durch und halten Wasser auf; Schilder lassen sich an andere Schilder hängen.",
             W + "Sign"),
            ("Stufen (nicht doppelt) lassen Licht nur in bestimmte Richtungen durch – eine obere Stufe hält das "
             "Tageslicht von oben ab.", W + "Opacity"),
            ("Eine Stufe mit Wasser darin (Wassereimer) wirkt wie eine Quelle; Wasser fließt aus der offenen "
             "unteren Hälfte nach unten.", W + "Waterlogging"),
            ("Spielcode 26.3: im Fluss besteht ein Spawnversuch mit 1 : 15, Wasser an der Stelle und darunter; "
             "nachts schwimmen Ertrunkene unter Höhe 61 nach oben.", None),
            ("Schacht, Trichter und Spalt wie bei der einfachen Farm, die auf dem Testserver (26.3) lief.", None)])))

f.zeichen(a=("wall_sign", "e"), b=("wall_sign", "w"), n=("wall_sign", "n"), s=("wall_sign", "s"),
          H=("hopper", "d"), Z="cobblestone", U=("stone_slab", {"half": "top"}))

FELD = "\n".join([".XXXXXXXX."] + ["XXXXXXXXXX"] * 8 + [".XXXXXXXX."])      # 10 × 10 ohne Ecken

f.schritt("Im Flussbiom (Füße auf Höhe 64 oder höher) zuerst den Schacht: 2 × 2, 25 Blöcke tief – er liegt später in "
          "der Mitte der Grube. Daneben eine Treppe hinunter graben, sie bleibt dein Weg nach unten.", {
    **{y: "--\n--" for y in range(-25, 0)}}, x0=4, z0=4)
f.schritt("Unten wie bei der einfachen Farm, nur tiefer: 4 Trichter unter dem Schacht führen über einen Trichter unter "
          "einem Spalt in die Truhe (schleichend an Truhe bzw. nächsten Trichter klicken). Auf der Truhe stehst du, "
          "eine Ebene tiefer als die Landestelle; der Block über dem Spalt schützt dich.", {
    -27: "...>C",
    -26: ".>>H-\n.^^..",
    -25: "...--"}, x0=3, z0=4)
f.schritt("Grube ausheben: 10 × 10 ohne die 4 Ecken, 3 tief (Höhe -1 bis -3), mit dem Schacht in der Mitte. Der Boden "
          "darunter (Höhe -4) bleibt, nur das Schachtloch ist offen. Ränder und Boden müssen dicht sein (kein "
          "Flusswasser, keine Höhle).", {
    y: FELD.replace("X", "-") for y in (-1, -2, -3)})
f.schritt("Vier Schilder ins Schachtloch (Höhe -4): die zwei westlichen an die Westseite des Lochs, die zwei östlichen an "
          "die Ostseite. Sie halten später das Wasser, Ertrunkene fallen hindurch. Vorsicht: Darunter geht es 22 "
          "Blöcke tief – nicht auf das Loch treten.", {
    -4: "ab\nab"}, x0=4, z0=4)
f.schritt("Schilderdecke auf Brusthöhe (Höhe -2), erst 6 Reihen: An die Westwand der Grube in der 3., 5. und 7. Reihe "
          "(von Norden gezählt) je ein Schild, an die Ostwand in der 4., 6. und 8. Reihe. Von jedem Wandschild aus die "
          "Reihe quer hinüber: rückwärts gehen, zum letzten Schild schauen und an seine Vorderseite klicken – das neue "
          "hängt am vorigen (Schilder halten an Schildern). Jede Reihe hat 9 Schilder, das Feld am anderen Ende bleibt "
          "frei.", {
    -2: """
        aaaaaaaaa.
        .bbbbbbbbb
        aaaaaaaaa.
        .bbbbbbbbb
        aaaaaaaaa.
        .bbbbbbbbb
    """}, z0=2)
f.schritt("Die Reihen am Nord- und Südrand (2. und 9. Reihe, je 8 Schilder): Erst darunter 8 Hilfsblöcke auf den Boden "
          "legen (Höhe -3). Stell dich in die Randreihe, schau fast waagerecht zur Schilderdecke und klick oben auf einen "
          "Hilfsblock – das Schild hängt sich an das Schild dahinter. Danach die Hilfsblöcke abbauen. Frei bleiben 26 "
          "Randfelder – die 1. und 10. Reihe und die Endfelder ohne Schild: Dort fällt später das Wasser bis auf den "
          "Boden.", {
    -2: """
        .nnnnnnnn.
        ..........
        ..........
        ..........
        ..........
        ..........
        ..........
        .ssssssss.
    """}, z0=1)
f.schritt("Hinaus: in einer Randlücke 3 Blöcke hochbauen (springen und "
          "unter dich setzen), oben aussteigen und den Turm von oben wieder abbauen. Rund um die Grube eine Wand aus "
          "Bruchstein, 11 Blöcke hoch (Höhe 0 bis 10): an jeder Seite 8 Blöcke, dazu die 4 Eckfelder des 10 × 10-Felds. "
          "Sie hält das Licht ab.", {
    y: """
        ..ZZZZZZZZ..
        .Z........Z.
        Z..........Z
        Z..........Z
        Z..........Z
        Z..........Z
        Z..........Z
        Z..........Z
        Z..........Z
        Z..........Z
        .Z........Z.
        ..ZZZZZZZZ..
    """ for y in range(0, 11)}, x0=-1, z0=-1)
f.schritt("Dach aus Stufen in der oberen Blockhälfte auf Höhe 10, innerhalb der obersten Wandreihe: die erste an die "
          "obere Hälfte der Wand-Innenseite klicken, jede weitere an die obere Hälfte der vorigen Stufe. Hinauf kommst du "
          "außen mit Gerüst oder Leiter, auf dem Dach kannst du laufen.", {
    10: FELD.replace("X", "U")})
f.schritt("Wasser: Daneben eine Wasserquelle 2 × 2 (unendlich), dann jede der 96 Stufen mit dem Wassereimer anklicken. "
          "Aus jeder Stufe fällt Wasser bis auf die Schilder, in den 26 Randlücken bis auf den Grubenboden; dort "
          "strömt es zur Mitte und hält über dem Schachtloch an. Innen bleibt es stockdunkel.", {
    -2: """
        .FFFFFFFF.
        F........F
        .........F
        F.........
        .........F
        F.........
        .........F
        F.........
        F........F
        .FFFFFFFF.
    """,
    -3: FELD.replace("X", "F")})
f.schritt("Dein Platz: unten auf der Truhe (über die Treppe). Ertrunkene sinken herab, das Wasser schiebt sie ins Loch, "
          "sie fallen auf die Trichter – durch den Spalt an den Beinen treffen. Nachts wie tags.", {-26: "P"}, x0=7, z0=4)

# Test hoch über der flachen Testwelt (dort füllen Schleime sonst das Monster-Limit). Die Stufen werden – wie mit dem
# Wassereimer – mit Wasser gefüllt; eine Lage darüber kurz gesetzt und wieder entfernt, damit jede Stufe ihr Wasser
# fließen lässt (ein per Befehl gesetztes Wasser in einer Stufe fließt erst nach einer Nachbaränderung).
WASSER = ["fill {x+0} {y+10} {z+0} {x+9} {y+10} {z+9} minecraft:stone_brick_slab[type=top,waterlogged=true] "
          "replace minecraft:stone_brick_slab[type=top]",
          "fill {x+0} {y+11} {z+0} {x+9} {y+11} {z+9} minecraft:stone_bricks replace minecraft:air",
          "fill {x+0} {y+11} {z+0} {x+9} {y+11} {z+9} minecraft:air replace minecraft:stone_bricks"]
LANDUNG = [4, -25, 4, 5, -23, 5]
f.pruefe(biom="minecraft:river", boden=GRAS, zeit="day", hoehe=100, nachher=WASSER, bereich=LANDUNG,
         erwartet={"wesen": {"minecraft:drowned": 5}})
# Weg prüfen ohne Spawn-Zufall: Wasserturm direkt füllen, 6 Ertrunkene oben, am Rand und unten hineinsetzen
f.pruefe_auch("ertrunkene_profi_mech", boden=GRAS, zeit="day", hoehe=100, bereich=LANDUNG,
              nachher=WASSER + ["fill {x+0} {y+0} {z+0} {x+9} {y+8} {z+9} minecraft:water replace minecraft:air"] +
              mobs("drowned", [(1, 8, 1), (8, 8, 8), (0, 5, 5), (5, 3, 0), (9, 2, 4), (2, 0, 7)]),
              erwartet={"wesen": {"minecraft:drowned": 5}})
