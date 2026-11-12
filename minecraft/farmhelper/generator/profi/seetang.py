"""Seetang-Farm (Profi): der Querschnitt der einfachen Farm gespiegelt und auf 12 verlängert – 24 Pflanzen, die sich eine
Redstone-Mittelreihe teilen.

Querschnitt (Norden → Süden, z -4 … 4):
  Rand | Trichter (Wasser drüber) | Seetang-Rinne | Kolben/Beobachter | Mittelreihe mit Staub | Kolben/Beobachter |
  Seetang-Rinne | Trichter | Rand
"""
from profi_basis import *

f = profi("seetang", dict(
    name="Seetang-Farm (Profi)", diff=3, out="Seetang → Getrockneter Seetang (Brennstoff)",
    where="Überall – das Becken baust du selbst, auch an Land",
    afk="In der Nähe bleiben (Simulationsdistanz)",
    why="Viermal so viel Seetang wie die einfache Farm: 24 statt 6 Pflanzen. Jede Pflanze wächst nur oben weiter, im "
        "Schnitt etwa 7 Blöcke pro Stunde – mehr Ertrag gibt es nur durch mehr Pflanzen. Darum ist der bewährte "
        "Querschnitt der einfachen Farm gespiegelt (zwei Rinnen, die sich in der Mitte eine Redstone-Reihe teilen) und "
        "auf 12 Blöcke verlängert. Wächst irgendein Seetang bis oben (Höhe 2), sieht ihn sein Beobachter und gibt "
        "einen Impuls nach hinten in den Staub; alle 24 Kolben schlagen den 2. Block ab. Der untere Block bekommt "
        "dabei ein neues Alter und wächst weiter, Pflanzen, die zu früh aufgehört haben, werden beim nächsten Mal "
        "mit abgeschlagen. Die Stücke schwimmen hoch und treiben mit dem Wasser über die Trichter. Getrockneter "
        "Seetang als Block brennt im Ofen für 20 Gegenstände.",
    help=[["Stücke treiben nicht in die Trichter", "In der ganzen obersten Reihe der Rinnen (Höhe 2) müssen "
                                                   "Quellen sein, über den Trichtern fließt das Wasser, außen hält "
                                                   "es der Rand auf Höhe 2."],
          ["Kolben fahren nie aus", "Die Beobachter müssen mit dem Gesicht zur Rinne schauen (roter Punkt zur Mitte) "
                                    "und hinter sich den Staub haben. Unter dem Staub liegen normale Blöcke direkt "
                                    "neben den Kolben."],
          ["Seetang lässt sich nicht setzen", "Nur in Wasser: erst die Quellen oben, dann den Seetang unten auf den "
                                              "Boden der Rinne (Erde, Sand oder Stein – nicht Magma)."]],
    meta=m("Rate: etwa 180 Seetang pro Stunde (Schätzung nach dem Wiki: eine Pflanze wächst im Schnitt alle 488 "
           "Sekunden um 1 Block, 24 Pflanzen; die einfache Farm mit 6 Pflanzen kommt so auf etwa 45)",
           [("Überall – das Becken baust du selbst.", W + "Tutorial:Kelp_farming")],
           [("Seetang wächst mit 14 % je Zufallstick, auch in fallendes Wasser; wird ein Block abgebrochen, bekommt "
             "der darunter ein neues Zufallsalter und wächst weiter.", W + "Kelp#Growth_mechanics"),
            ("Kolben am 2. Block, Beobachter an der Pflanze, oben Wasser, daneben ein Trichter.",
             W + "Tutorial:Kelp_farming#Automatic_farming"),
            ("Querschnitt wie die einfache Farm, die auf dem Testserver (26.3) lief (72 Seetang in 30 Minuten mit 6 "
             "Pflanzen bei 10 Zufallsticks) – hier gespiegelt und verlängert.", None)])))

f.zeichen(Z="kelp", N=("piston", "n"), S=("piston", "s"), n=("observer", "n"), s=("observer", "s"))

f.schritt("Grundplatte auf ebenem Boden (Höhe 0), 12 lang – von Norden nach Süden: 1 Reihe Blöcke, 1 Reihe frei "
          "(Seetang-Rinne), 3 Reihen Blöcke, 1 Reihe frei (Rinne), 1 Reihe Blöcke. Der Boden der Rinnen bleibt (Erde, "
          "Sand oder Stein; kein Magma). An beide Enden der Rinnen und der äußeren Reihen je ein Block mehr.", {
    0: """
        ##############
        #............#
        .############.
        .############.
        .############.
        #............#
        ##############
    """}, x0=-1, z0=-3)
f.schritt("Kolben auf die Plattenreihen direkt neben den Rinnen (Innenseite): Stell dich in die nördliche Rinne und "
          "schau nach Süden auf die Platte – die Kolben zeigen zu dir in die Rinne. Dann aus der südlichen Rinne "
          "genauso (diese Kolben zeigen nach Süden). Die mittlere Reihe dazwischen bleibt frei – das ist dein Gang.", {
    1: """
        NNNNNNNNNNNN
        ............
        SSSSSSSSSSSS
    """}, z0=-1)
f.schritt("Stell dich in den Gang zwischen den Kolben und schau geradeaus nach Norden: Beobachter auf die nördlichen "
          "Kolben setzen – ihr Gesicht schaut nach Norden über die Rinne, der rote Punkt zu dir. Dann umdrehen und "
          "genauso nach Süden auf die südlichen Kolben.", {
    2: """
        nnnnnnnnnnnn
        ............
        ssssssssssss
    """}, z0=-1)
f.schritt("Den Gang rückwärts gehend mit Blöcken zuschließen (Höhe 1, zwischen den Kolben), dann Redstone-Staub "
          "obendrauf. Jeder Beobachter gibt seinen Impuls nach hinten in den Staub, der Staub schaltet über die Blöcke "
          "darunter alle 24 Kolben.", {
    1: "############",
    2: "RRRRRRRRRRRR"})
f.schritt("Truhen auf das Ostende der beiden äußeren Reihen, dann je 12 Trichter nach Osten in die Truhe (schleichend "
          "an die Truhe bzw. den vorigen Trichter klicken).", {
    1: """
        >>>>>>>>>>>>C
        .............
        .............
        .............
        .............
        .............
        >>>>>>>>>>>>C
    """}, z0=-3)
f.schritt("Enden hochziehen: an beiden Enden der Rinnen Blöcke bis Höhe 2, am Westende auch neben den Trichtern; am "
          "Ostende Glas auf die Truhen (darunter lassen sie sich öffnen). Dann außen über den Trichtern auf Höhe 2 je "
          "eine Randreihe, vom Westende aus Block an Block nach Osten gebaut – sie hält das Wasser über den "
          "Trichtern.", {
    1: """
        ..............
        #.............
        #............#
        ..............
        ..............
        ..............
        #............#
        #.............
    """,
    2: """
        ##############
        #............G
        #............#
        ..............
        ..............
        ..............
        #............#
        #............G
        ##############
    """}, x0=-1, z0=-4)
f.schritt("Wasserquellen in die oberste Ebene beider Rinnen (Höhe 2), 12 pro Seite: Das Wasser fällt bis zum Boden und "
          "läuft oben über die Trichter bis an den Rand.", {
    1: """
        ............
        FFFFFFFFFFFF
        ............
        ............
        ............
        FFFFFFFFFFFF
    """,
    2: """
        FFFFFFFFFFFF
        WWWWWWWWWWWW
        ............
        ............
        ............
        WWWWWWWWWWWW
        FFFFFFFFFFFF
    """}, z0=-3)
f.schritt("Seetang auf den Boden der Rinnen setzen, 12 pro Seite – fertig. Wächst ein Seetang bis Höhe 2, schlagen "
          "alle Kolben den 2. Block ab; die Stücke schwimmen hoch und treiben über die Trichter.", {
    0: """
        ZZZZZZZZZZZZ
        ............
        ............
        ............
        ZZZZZZZZZZZZ
    """}, z0=-2)
f.schritt("Dein Platz – der Seetang wächst nur, wenn du in der Nähe bist.", {0: "P"}, x0=14)

f.pruefe(boden=GRAS, erwartet={"items": {"minecraft:kelp": 150}})
