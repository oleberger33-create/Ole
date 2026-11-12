"""Hexen-Farm (Profi): drei Spawn-Ebenen in der Box der Hexenhütte, rundum zu und mit Dach (Tag und Nacht), ein
gemeinsamer Schlitz mit offenen Falltüren über allen Ebenen, Wasserkanal zum Schacht, 31 Blöcke Fall auf einen
Trichter über einer Truhe, AFK-Platz in einem Gang 25 Blöcke unter der untersten Ebene, Zugang über einen Leiterschacht.

Box der Hütte (Spawnbereich, 7 × 7 × 9): x 0 … 6, y 0 … 6, z 0 … 8 (y 0 = eine Ebene unter dem alten Hüttenboden).
Böden (Bruchstein) auf y -1, 2, 5 → Hexenfüße auf y 0, 3, 6, je 2 Blöcke Luft (Hexe 1,95 hoch). Schlitz x 3, z 0 … 8 in
jedem Boden mit offenen Falltüren (Klappe an der Westseite). Wände ringsum (x -1/7, z -1/9) auf y 0 … 7, Dach y 8.
Kanal y -2 unter dem Schlitz wie in der einfachen Farm: Quelle bei z 0, fließt 7 Blöcke nach Süden, am Ende (3, -2, 8)
eine offene Falltür (Klappe an der Südseite) über dem Schacht (3, -3 … -33, 8); Trichter (3, -34, 8) nach unten in die
Truhe (3, -35, 8). Leiterschacht (8, -35 … -1, 4) außen vor der Mitte der Ostwand, Leitern am Ostrand (x 9). Gang unten
(4 … 7, -35/-34, 4), dann (4, -35/-34, 5 … 8) bis neben die Truhe; Gang in Tiefe 25 (3 … 7, -25/-24, 4) mit dem
AFK-Platz (3, -25, 4) genau unter der Mitte der Box: 25 bis 31,5 Blöcke von jeder Hexe.
"""
from profi_basis import *

f = profi("hexe", dict(
    name="Hexen-Farm mit 3 Ebenen (Profi)", diff=4,
    out="Redstone-Staub, Glowstonestaub, Zucker, Schwarzpulver, Glasflaschen, Spinnenaugen, Stöcke",
    where="Hexenhütte im Sumpf (die ganze Hütte im Sumpf-Biom)",
    afk="Ja – im Gang 25 Blöcke unter der untersten Ebene (alle drei Ebenen 25 bis 31,5 Blöcke weg)",
    why="Die einfache Farm hat eine Ebene ohne Dach: Hexen spawnen dort nur nachts, und auch dann klappt nur etwa "
        "jeder vierte Versuch, weil der Himmel die Plattform aufhellt. Die Profi-Farm füllt die ganze Box der Hütte "
        "(7 hoch) mit drei Ebenen – mehr passen nicht hinein: Hexenfüße auf Höhe 0, 3 und 6, darüber je 2 Blöcke "
        "Luft. Das sind 162 statt 55 Spawnplätze. Wände rundherum und ein Dach machen es drinnen stockdunkel, so "
        "spawnen Hexen Tag und Nacht. Jede Ebene hat in der Mitte der Länge nach einen Schlitz mit offenen Falltüren: "
        "Hexen halten sie für Boden, laufen darauf und fallen durch den Spalt daneben. Die Schlitze liegen genau "
        "übereinander, so fallen auch die Hexen von oben bis in den Kanal unter der untersten Ebene. Von dort an wie "
        "in der einfachen Farm: Das Wasser schiebt sie zum Ende des Kanals, eine offene Falltür hält das Wasser, die "
        "Hexe fällt durch den Spalt 31 Blöcke tief auf einen Trichter – sie hat nur 26 Leben. Die Beute läuft in die "
        "Truhe darunter. Du wartest in einem Gang 25 Blöcke unter der untersten Ebene: Näher als 24 spawnt nichts, "
        "weiter als 32 Blöcke laufen die Hexen nicht herum – von deinem Platz sind alle drei Ebenen 25 bis 31,5 "
        "Blöcke weg.",
    help=[["Keine Hexen", "Die Böden müssen genau in der Box liegen: deine Füße beim Planstart eine Ebene unter dem "
                          "alten Hüttenboden, der Plan genau unter Dach und Veranda der Hütte. Drinnen muss es "
                          "stockdunkel sein – keine Fackel, kein Loch in Wand oder Dach, die Tür in der Ostwand zu."],
          ["Hexen stehen nur herum", "Du musst am AFK-Platz am Westende des oberen Gangs stehen (genau unter der "
                                     "Mitte der Box): Die Ecken der obersten Ebene sind von dort 31,5 Blöcke weg – "
                                     "über 32 laufen Mobs nicht herum (im Test nachgeprüft)."],
          ["Hexen bleiben im Kanal oder leben unten noch", "Alle Falltüren müssen offen sein (senkrecht an der "
                                                           "Westseite des Schlitzes). Die Falltür am Kanalende über "
                                                           "dem Schacht steht senkrecht an seiner Südseite und hält "
                                                           "das Wasser – im Schacht darf kein Wasser stehen, sonst "
                                                           "landen die Hexen weich."],
          ["Sumpfwasser läuft herein", "Kanal, Fallschacht und Leiterschacht müssen dicht sein: Wo Wasser oder Luft "
                                       "daneben ist, Blöcke setzen. Hinter jeder Leiter muss ein fester Block sein."]],
    meta=m("Rate (Schätzung): grob 20–60 Hexen pro Stunde, also etwa 100–400 Redstone-Staub (jede Hexe gibt sicher "
           "4–8) plus Glowstonestaub, Zucker, Schwarzpulver, Flaschen, Spinnenaugen und Stöcke. Grund: 162 statt 55 "
           "Spawnplätze und durch das Dach Tag und Nacht statt nur nachts. Höhlen in der Nähe senken die Rate "
           "(Monster-Limit). Zum Vergleich die einfache Farm im Test: 8 Redstone in 30 Minuten Nacht.",
           [("Hexenhütte im Sumpf; die Box ist 7 × 7 × 9 und reicht von 1 unter dem Hüttenboden bis 2 über das Dach.",
             W + "Swamp_Hut"),
            ("Eine Hexenhütte trägt höchstens 3 Spawn-Ebenen; nötig ist ein Himmelslicht von 7 oder weniger.",
             W + "Tutorial:Witch_farming")],
           [("In der Box einer Hexenhütte spawnen nur Hexen – an jedem Block der Box.", W + "Swamp_Hut"),
            ("Hexe: 26 Leben, 1,95 hoch, 0,6 breit; Beute 4–8 Redstone-Staub sicher, dazu Glowstonestaub, Zucker, "
             "Schwarzpulver, Glasflaschen, Spinnenaugen, Stöcke.", W + "Witch"),
            ("Monster brauchen Blocklicht 0 und wenig Himmelslicht: unter Dach auch tagsüber, unter freiem Himmel nur "
             "nachts. Kein Spawn näher als 24 Blöcke am Spieler; ohne Spieler im Umkreis von 32 Blöcken verschwinden "
             "Hexen nach und nach.", W + "Mob_spawning"),
            ("Mobs halten offene Falltüren für geschlossen und fallen hindurch.", W + "Trapdoor"),
            ("Auf dem Testserver (26.3) geprüft (einfache Farm): Kanal mit offenen Falltüren, Wasser zur offenen "
             "Falltür über dem Schacht, die Hexen fallen und sterben, die Beute liegt in der Truhe; Mobs über 32 "
             "Blöcke vom Spieler laufen nicht herum.", None)])))

f.zeichen(B="cobblestone", O=("oak_trapdoor", {"half": "bottom", "f": "e", "open": True}),
          U=("oak_trapdoor", {"half": "bottom", "f": "n", "open": True}), L=("ladder", "w"))

RING = "\n".join(["B" * 9] + ["B" + "." * 7 + "B"] * 9 + ["B" * 9])          # Wand rund um die Box (x -1 … 7)
BODEN = "\n".join(["BBBOBBB"] * 9)                                             # Boden mit Schlitz (Falltüren)

f.schritt("Zum Start des Plans stehst du mit den Füßen eine Ebene UNTER dem Boden der Hexenhütte (y 0 hier). "
          "Verschiebe und drehe den Plan im Plan-Menü (Pfeile, Drehen), bis die roten Felder (7 × 9) genau unter "
          "Dach und Veranda der Hütte liegen – die lange Seite (9) wie die lange Seite der Hütte. Das ist die "
          "Spawn-Box. Dann die ganze Hütte abbauen, auch Pfähle, Kessel und Dach: Im roten Bereich (8 Ebenen hoch) "
          "muss alles frei sein.", {y: flaeche("-", 7, 9) for y in range(0, 8)})
f.schritt("Unterster Boden eine Ebene unter deinen Füßen (genau unter der Box), aus Bruchstein. Der Länge nach in der "
          "Mitte bleibt ein Schlitz frei, darunter der Kanal: zusammen 2 tief. Vor die beiden Enden des Schlitzes "
          "(vor der Nord- und der Südkante der Box) kommt je ein Block. Steht die Hütte über Wasser oder Luft: Der "
          "Kanal muss trotzdem dicht sein – wo neben oder unter ihm Wasser oder Luft ist, Blöcke setzen.", {
    -1: "...B...\n" + "\n".join(["BBB-BBB"] * 9) + "\n...B...",
    -2: ".......\n" + "\n".join(["...-..."] * 9)}, z0=-1)
f.schritt("Wände rundherum, direkt außen an der Box, 3 Lagen hoch (Höhe 0 bis 2). Fang auf einem der beiden Blöcke "
          "vor dem Schlitz an und baue seitlich weiter. Die dritte Lage hat schon die Höhe des nächsten Bodens.", {
    0: RING, 1: RING, 2: RING}, x0=-1, z0=-1)
f.schritt("Zweiter Boden auf Höhe 2 (Hexenfüße hier auf Höhe 3), an die Wände angebaut. Im Schlitz genau über dem "
          "unteren kommen offene Falltüren: schleichend an die Ostseite des Bodenblocks westlich davon klicken und "
          "aufklappen – sie stehen dann senkrecht an der Westseite des Schlitzes. Hexen halten sie für Boden und fallen "
          "durch den Spalt daneben. Vorsicht: Du fällst da auch durch (unten ist der Kanal noch trocken).", {
    2: BODEN})
f.schritt("Wände 3 Lagen höher (Höhe 3 bis 5).", {3: RING, 4: RING, 5: RING}, x0=-1, z0=-1)
f.schritt("Dritter Boden auf Höhe 5 (Hexenfüße auf Höhe 6, die oberste Ebene der Box), wieder mit offenen Falltüren "
          "im Schlitz, genau über den unteren.", {5: BODEN})
f.schritt("Wände noch 2 Lagen höher (Höhe 6 und 7) – über den obersten Hexen sind dann 2 Blöcke Luft.", {
    6: RING, 7: RING}, x0=-1, z0=-1)
f.schritt("Dach auf Höhe 8, von oben gebaut (du stehst auf den Wänden): erst eine Reihe oben auf die Westwand, dann "
          "das Dach Reihe für Reihe daran anbauen, bis die ganze Box zu ist. Jetzt ist es drinnen stockdunkel – "
          "Hexen spawnen Tag und Nacht. Hilfsblöcke drinnen wieder abbauen.", {
    8: "\n".join(["B" * 8] * 9)}, x0=-1)
f.schritt("Zugang: Direkt außen an der Ostwand, genau vor ihrer Mitte, einen Schacht 1 × 1 senkrecht 35 Blöcke tief "
          "graben – setz die Leitern (nächster Schritt) gleich beim Graben, sonst kommst du nicht mehr hoch. In Tiefe "
          "25 (Füße) einen Gang 2 hoch und 5 lang nach Westen: An seinem Ende, genau unter der Mitte der Box, ist dein "
          "AFK-Platz. Ganz unten einen Gang (auch 2 hoch) 4 lang nach Westen und dann 4 nach Süden – er endet neben der Stelle, an "
          "die die Truhe kommt (unter dem Südende des Schlitzes). Gänge mit Fackeln beleuchten.", {
    **{y: ".....-" for y in range(-33, 0) if y not in (-24, -25)},
    -24: "------", -25: "------",
    -34: ".-----\n.-....\n.-....\n.-....\n.-....",
    -35: ".-----\n.-....\n.-....\n.-....\n.-...."}, x0=3, z0=4)
f.schritt("Leitern an die Ostseite des Schachts, vom Grund bis ganz oben (beim Setzen schaust du nach Osten).", {
    y: "L" for y in range(-35, 0)}, x0=8, z0=4)
f.schritt("Fallschacht: Unten in der Mitte der Ostwand (direkt neben dem Leiterschacht) zwei Blöcke übereinander "
          "abbauen – das ist deine Tür. Drinnen nur auf der Osthälfte gehen. Am Südende des Kanals (letztes Stück vor "
          "der Südwand) senkrecht hinunter graben, bis deine Füße auf Höhe des unteren Gangs sind (35 Blöcke unter "
          "deinen Füßen beim Planstart), dann nach Osten in den Gang treten.", {
    y: "-" for y in range(-35, -2)}, x0=3, z0=8)
f.schritt("Vom unteren Gang aus: Truhe auf den Grund des Schachts (auf den Boden klicken), dann schleichend oben auf "
          "die Truhe klicken – der Trichter zeigt nach unten in die Truhe. Auf ihm landen die Hexen nach 31 Blöcken Fall. "
          "Truhe ab und zu leeren.", {
    -35: "C", -34: "H"}, x0=3, z0=8)
f.schritt("Leiter hoch, durch die Tür hinein (Osthälfte!). Ans Südende des Kanals, über das Schachtloch, eine "
          "Falltür: an die Südwand des Kanals klicken und aufklappen – sie steht dann senkrecht an der Südseite, hält "
          "das Wasser, und die Hexen fallen durch den Spalt davor in den Schacht. Dann einen Wassereimer ans Nordende "
          "des Kanals: Das Wasser fließt genau 7 Blöcke bis zur Falltür. Zuletzt die 9 Falltüren über dem Kanal wie "
          "oben (an die Ostseite der Bodenblöcke westlich vom Schlitz klicken, öffnen). Hinaus durch die Tür und sie von "
          "außen wieder zumauern.", {
    -2: "W\nF\nF\nF\nF\nF\nF\nF\nU",
    -1: "\n".join(["O"] * 9)}, x0=3)
f.schritt("Dein Platz: Leiter hinunter bis zum oberen Gang (Tiefe 25) und an sein Westende, genau unter die Mitte der "
          "Box. Hier bist du 25 Blöcke unter den untersten und 31 unter den obersten Hexenfüßen (die Ecken oben 31,5) – "
          "näher als 24 spawnt nichts, weiter als 32 laufen sie nicht herum. Die Beute holst du unten aus der Truhe.", {
    -25: "P"}, x0=3, z0=4)

# Echte Hexenhütte, mittags: Ohne Dach (einfache Farm) spawnt am Tag nichts; mit Dach und 3 Ebenen mehr als die 8
# Redstone, die die einfache Farm in 30 Minuten Nacht schaffte.
f.pruefe(zeit="day", welt="struktur", boden="minecraft:dirt",
         bauwerk={"id": "minecraft:swamp_hut", "suchen": True, "hoehe": 64, "groesse": [7, 9], "ecke": [0, 0, 0]},
         erwartet={"items": {"minecraft:redstone": 16}})
# Mechanik: je 2 Hexen auf jede Ebene (weit weg vom Schlitz). Pilzland-Biom: Dort spawnen keine Monster, im dunklen Bau
# entstehen also keine fremden Hexen. Alle 6 müssen unten sterben (mindestens 6 × 4 Redstone).
f.pruefe_auch("hexe_profi_mech", biom="minecraft:mushroom_fields", boden=GRAS, zeit="day",
              nachher=mobs("witch", [(1, 0, 1), (5, 0, 7), (0, 3, 8), (6, 3, 0), (0, 6, 0), (6, 6, 8)]),
              hoechstens={"wesen": {"minecraft:witch": 0}}, erwartet={"items": {"minecraft:redstone": 24}})
