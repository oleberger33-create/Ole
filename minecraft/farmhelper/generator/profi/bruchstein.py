"""Bruchstein-Generator (Profi): 4 Abbauplätze in einer Reihe genau vor dem Kopf des Spielers (AFK: linke Maustaste
halten), Trichter unter jedem Platz, alles in eine Doppeltruhe unter den Füßen.

Koordinaten: Spieler (AFK-Platz) bei (0, 0, 0), schaut nach Süden. Abbauplätze S1–S4 bei (0, 1, 1..4) auf Augenhöhe.
x -1: Lavarinne (eine Quelle bei z 2, fließt bis z 1 und z 4), x 1: fließendes Wasser über einer Lücke (x 1, y 0),
x 2: 4 Wasserquellen. Unter jedem Platz ein Trichter nach unten (0, 0, k), darunter Trichterreihe nach Norden
(0, -1, 1..4) in die Doppeltruhe (0, -1, -1..0). Deckel auf y 2.
"""
from profi_basis import *

f = profi("bruchstein", dict(
    name="Bruchstein-Generator (Profi)", diff=2, out="Bruchstein",
    where="Überall außer im Nether (dort verdampft Wasser); Platz 6 × 7",
    afk="Ja – auf der Truhe stehen, geradeaus schauen und die linke Maustaste mit der Spitzhacke gedrückt halten",
    why="Vier Abbauplätze in einer Reihe genau vor deinem Kopf statt einem im Graben. Westlich davon liegt eine "
        "Lavarinne (ein Eimer reicht, die Lava fließt durch alle 4 Plätze), östlich eine Wasserrinne: Ihr Wasser "
        "fällt in eine Lücke darunter und fließt darum nie auf die Abbauplätze. Baust du einen Platz ab, fließt "
        "nach 1,5 Sekunden Lava hinein und wird am Wasser sofort zu Bruchstein. Du schaust geradeaus nach Süden "
        "und hältst die Maustaste: Ist der erste Platz weg, triffst du den zweiten dahinter, dann den dritten – "
        "bis dahin ist der erste schon wieder da. Unter jedem Platz sitzt ein Trichter, der den Bruchstein im "
        "nächsten Tick einsaugt, bevor er in die Lava rutschen kann; alles landet in der Doppeltruhe unter deinen "
        "Füßen. So bekommst du ohne Verlust bis zu 4-mal so viel wie mit der einfachen, ohne Laufen und "
        "Aufsammeln.",
    help=[["Obsidian statt Bruchstein",
           "Wasser hat die Lava-QUELLE berührt. Das Wasser muss vor der Lava hinein, und die Lücke unter der "
           "Wasserrinne muss frei sein, damit das Wasser dort hinunterfällt. Obsidian abbauen, Lava neu einfüllen."],
          ["Hinterster Platz kommt nicht wieder",
           "Die Lava-Quelle gehört in den 2. Platz der Lavarinne von Norden. Lava fließt nur 3 Blöcke weit – von "
           "dort erreicht sie alle 4 Abbauplätze, vom 1. Platz aus nicht."],
          ["Bruchstein landet nicht in der Truhe",
           "Unter jedem Abbauplatz ein Trichter, der nach unten zeigt, darunter die Trichterreihe nach Norden in die "
           "Truhe. Ist die Truhe voll, staut es sich – rechtzeitig leeren (eine Doppeltruhe fasst 3456 Stück)."],
          ["Spitzhacke schnell kaputt",
           "Effizienz und Haltbarkeit verlängern die Zeit; Reparatur hilft hier nicht, weil Bruchstein keine "
           "Erfahrung gibt. Mit Effizienz V und Eile II (Leuchtfeuer) baust du alle 4 Plätze sofort ab."]],
    meta=m("Rate: bis etwa 9000 Bruchstein pro Stunde (Schätzung: jeder Platz ist 1,5 s nach dem Abbau wieder da, "
           "4 Plätze → bis 9600/h; die Trichter schaffen 9000/h). Mit einer Diamant-Spitzhacke ohne Verzauberung "
           "etwa 5500/h. Die einfache: ein Platz, höchstens 1 Stück alle 1,5 s von Hand (≈ 2400/h), dazu Verlust "
           "in der Lava.",
           [("Überall, nur nicht im Nether – dort verdampft Wasser.", W + "Tutorial:Cobblestone_farming")],
           [("Fließende Lava, die Wasser berührt, wird zu Bruchstein; Wasser auf der Lava-Quelle macht Obsidian.",
             W + "Tutorial:Cobblestone_farming"),
            ("Wiki: Verluste in der Lava vermeidet man, indem der Bruchstein in einen Trichter fällt; Trichter "
             "sammeln Items, bevor Lava sie zerstört.", W + "Tutorial:Cobblestone_farming"),
            ("Lava fließt in der Oberwelt 3 Blöcke weit, einen Block alle 30 Ticks (1,5 s).", W + "Lava"),
            ("Trichter sammeln jeden Tick Items im Block über sich ein und geben 2,5 Items pro Sekunde weiter.",
             W + "Hopper"),
            ("Die Reihe ist 4 Plätze lang, weil du Blöcke bis 4,5 Blöcke vor deinen Augen abbauen kannst.",
             W + "Interaction_range")])))

f.zeichen(K="cobblestone")

f.schritt("Ausheben: eine Rinne 1 tief und 6 lang von Norden nach Süden – hier kommen die Truhe und 4 Trichter "
          "hinein.", {
    -1: "-\n-\n-\n-\n-\n-"}, z0=-1)
f.schritt("Zwei Truhen in das Nordende der Rinne (zusammen eine Doppeltruhe). Dann 4 Trichter nach Norden: "
          "schleichend an die Südseite der Truhe klicken, jeden weiteren an die Südseite des vorigen.", {
    -1: "C\nC\n^\n^\n^\n^"}, z0=-1)
f.schritt("Auf jeden der 4 Trichter schleichend einen zweiten Trichter setzen – er zeigt nach unten. Daneben die "
          "Grundreihe auf den Boden: westlich 6 Blöcke (Boden der Lavarinne) und dahinter noch 4; südlich der "
          "Trichter 1 Block; östlich bleibt eine Rinne frei (die Lücke für das Wasser), nur an ihren beiden Enden "
          "je 1 Block; dann 6 Blöcke (Boden der Wasserquellen) und noch 4. Der Platz ganz im Norden über der "
          "Truhe bleibt frei – dort stehst du später.", {
    0: """
        .#.##.
        ##H.##
        ##H.##
        ##H.##
        ##H.##
        .####.
    """}, x0=-2, z0=0)
f.schritt("Die 4 Abbauplätze: schleichend auf jeden senkrechten Trichter einen Bruchstein (Platzhalter – später "
          "kommt er von selbst). Dann die Wände auf Höhe 1: ganz im Westen 4 Blöcke, an beiden Enden der Lava-, "
          "der Wasser- und der Quellenrinne je 1 Block, südlich der Bruchsteine 1 Block, ganz im Osten 4 Blöcke. "
          "Die Rinnen dazwischen bleiben leer.", {
    1: """
        .#.##.
        #.K..#
        #.K..#
        #.K..#
        #.K..#
        .####.
    """}, x0=-2, z0=0)
f.schritt("ZUERST das Wasser: 4 Eimer in die äußere Rinne im Osten – je einer auf die 4 Bodenblöcke zwischen der "
          "Ostwand und der Lücke. Das Wasser fließt einen Block nach Westen bis neben die Bruchsteine und fällt "
          "dort in die Lücke darunter – so fließt es nie auf die Abbauplätze.", {
    1: "FW\nFW\nFW\nFW",
    0: "F\nF\nF\nF"}, x0=1, z0=1)
f.schritt("DANACH die Lava: EIN Eimer in die westliche Rinne, in den 2. Platz von Norden. Sie fließt nach Norden "
          "und Süden durch die ganze Rinne (4 Plätze neben den 4 Bruchsteinen) und bleibt dort.", {
    1: "L"}, x0=-1, z0=2)
f.schritt("Deckel: auf jeden Bruchstein einen Block, daran nach Westen über die Lava je einen Block und nach Osten "
          "über das Wasser je zwei (4 Reihen zu 4 Blöcken). So fällt nichts in die Lava und kein Feuer entsteht.", {
    2: "####\n####\n####\n####"}, x0=-1, z0=1)
f.schritt("Hier stehen: auf der Truhe zwischen den beiden Wandblöcken, Blick geradeaus nach Süden auf den ersten "
          "Bruchstein. Spitzhacke in die Hand, linke Maustaste gedrückt halten: Ist der vordere Platz abgebaut, "
          "triffst du den nächsten dahinter; nach 1,5 s ist der vordere wieder da. Der Bruchstein fällt in die "
          "Trichter und landet in der Truhe unter dir (Truhe öffnen: nach unten schauen).", {
    0: "P"})

f.pruefe(boden=GRAS, spieler={"hand": "minecraft:diamond_pickaxe", "aktion": "attack continuous"},
         erwartet={"items": {"minecraft:cobblestone": 400}})
# Ohne Spieler: Platzhalter weg – alle 4 Plätze müssen sich von selbst wieder füllen (einfache Farm: 1 Platz)
f.pruefe_auch("bruchstein_profi_mech", boden=GRAS,
              nachher=[f"setblock {{x}} {{y+1}} {{z+{k}}} minecraft:air" for k in range(1, 5)],
              erwartet={"bloecke": {"minecraft:cobblestone": 4}})
