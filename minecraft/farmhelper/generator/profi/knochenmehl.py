"""Knochenmehl-Farm (Profi): eine Melonenfarm füttert den Komposter selbst.

24 Melonenstängel in zwei Reihen links und rechts von 12 Fruchtfeldern aus Schlamm (Bauweise wie die Kürbis-Farm
(Profi), aber eine Lage höher gebaut, damit Komposter und Truhe darunter passen). Die Trichter unter dem Schlamm laufen
nach Osten in einen Trichter über dem Komposter; unter dem Komposter holt ein Trichter das Knochenmehl in die Truhe.

Querschnitt (Norden → Süden, z -2 … 2): Karotten | Stängel | Schlamm-Fruchtfeld | Stängel | Karotten
Höhen: Trichter -1 (Graben), Ackerboden/Schlamm 0, Pflanzen 1, Kolben/Beobachter 2, Staub/Blöcke 3.
Komposter (12, -2, 0), Trichter darunter (12, -3, 0) nach Osten, Truhe (13, -3, 0) im Schacht.
"""
from profi_basis import *

N = 12                                                    # Fruchtfelder (= Stängel pro Reihe)

f = profi("knochenmehl", dict(
    name="Knochenmehl-Farm mit Melonen (Profi)", diff=3, out="Knochenmehl (nebenbei Karotten oder Kartoffeln)",
    where="Überall auf ebenem Boden mit freiem Himmel über den Karottenreihen",
    afk="Ja – in der Nähe bleiben (AFK-Platz an der Truhe), die Stängel wachsen nur, wenn du in der Nähe bist",
    why="Die einfache Farm macht nur Knochenmehl aus dem, was du von Hand hineinwirfst. Die Profi-Farm baut "
        "ihr Futter selbst an – mit Melonen, denn die geben am meisten Kompost: Jede Melone zerfällt in 3–7 "
        "Scheiben, und jede Scheibe füllt den Komposter mit 50 % Chance (Samen nur mit 30 %). 24 Melonenstängel "
        "stehen in zwei Reihen links und rechts von 12 Fruchtfeldern aus Schlamm; alle anderen Seiten der Stängel "
        "sind belegt (Nachbarstängel, Karotten, Wand, Endblöcke), die Frucht kann nur auf den Schlamm. Über jedem "
        "Stängel schaut ein Beobachter nach unten: Setzt ein Stängel eine Melone an, schalten alle 12 Kolben und "
        "zerbrechen die Früchte. Die Scheiben fallen auf den Schlamm, die Trichter darunter bringen sie nach Osten "
        "in den Komposter, und der Trichter unter dem Komposter holt das fertige Knochenmehl in die Truhe – ganz "
        "ohne dein Zutun, Tag und Nacht.",
    help=[["Scheiben kommen an, aber kein Knochenmehl",
           "Der Trichter über dem Komposter muss nach unten zeigen, der unter dem Komposter nach Osten in die Truhe. "
           "Von der Seite nimmt ein Komposter nichts an und gibt nichts ab."],
          ["Keine Melonen",
           "Die Stängel brauchen Licht ≥ 9 (es kommt von der Seite – über den Karotten freier Himmel), feuchten "
           "Ackerboden (die zwei Wasserlöcher in der Nordreihe) und dich in der Nähe. Die Frucht wächst nur auf "
           "den Schlamm: Am Ostende müssen die Blöcke neben den letzten Stängeln stehen."],
          ["Kolben fahren nicht aus",
           "Die Beobachter müssen nach unten schauen (roter Punkt oben) und einen normalen Block tragen – kein Glas. "
           "Der Redstone-Staub liegt direkt auf den Kolben."],
          ["Ackerboden wird zu Erde",
           "Ein Mob ist auf die Felder gesprungen. Die zwei Fackeln oben verhindern, dass auf der Farm etwas "
           "spawnt; steht die Farm im Dunkeln, ringsum Fackeln stellen. Ein Stängel auf Erde fällt ab – Erde "
           "wieder hacken, neu pflanzen."]],
    meta=m("Rate: etwa 25–30 Knochenmehl pro Stunde, ohne dass du etwas tust (Schätzung nach den Wachstumsregeln im "
           "Wiki: 24 Stängel, Chance 1/4 je Zufallstick, eine freie Seite → je Stängel gut 3 Melonen pro Stunde, "
           "5 Scheiben je Melone, 13 Scheiben je Knochenmehl)",
           [("Überall auf ebenem Boden. Die Stängel brauchen Licht ≥ 9, die Fruchtfelder Luft über Schlamm.",
             W + "Tutorial:Pumpkin_and_melon_farming")],
           [("Am meisten Knochenmehl pro Stunde bringen Melonen- oder Kaktusfarmen, die einen Komposter füttern.",
             W + "Tutorial:Bone_meal_farming"),
            ("Kompost-Chance: Melonenscheibe 50 %, Samen 30 %; im Schnitt braucht ein Knochenmehl 1 + 6 / Chance "
             "Gegenstände – 13 Scheiben.", W + "Composter"),
            ("Ein Trichter direkt darüber (nach unten) füllt den Komposter, einer direkt darunter holt das "
             "Knochenmehl; von der Seite geht nichts.", W + "Composter#Hoppers"),
            ("Kolben zerbrechen Melonen: 3–7 Scheiben.", W + "Melon"),
            ("Ein reifer Stängel wählt bei jedem Wachstum eine zufällige Seite; nur wenn dort Luft über passendem "
             "Boden ist, wächst die Frucht.", W + "Tutorial:Pumpkin_and_melon_farming#Growth_mechanics"),
            (TEST + "einfache Kürbis-Farm (Beobachter über dem Stängel, Trichter unter Schlamm): 90 Melonenscheiben "
                    "in 30 min Zeitraffer; einfache Knochenmehl-Farm: 320 Samen ergaben 14 Knochenmehl.", None)])))

f.zeichen(A="farmland", M="mud", T="melon_stem", Q="feldfrucht", O="composter", I="torch",
          K=("piston", "d"), B=("observer", "d"))

f.schritt("Ausheben: ein Graben 13 lang und 1 tief. An seinem Ostende geht es 2 Blöcke tiefer (für Komposter und "
          "Trichter), östlich daneben ein Schacht 3 tief für die Truhe.", {
    -1: "-" * (N + 2),
    -2: "." * N + "--",
    -3: "." * N + "--"})
f.schritt("Wand am Westende des Grabens: 3 breit (über dem Graben und eine Reihe zu jeder Seite), 3 hoch. Dann stell "
          "dich in den Graben, schau nach oben und setz 12 Kolben in die dritte Lage über dem Boden (Höhe 2) – den "
          "ersten an die Wand geklickt, jeden weiteren an den vorigen. Weil du nach oben schaust, zeigen alle Kolben "
          "nach unten (zu dir).", {
    0: "#\n#\n#",
    1: "#\n#\n#",
    2: "#\n#" + "K" * N + "\n#"}, x0=-1, z0=-1)
f.schritt("Unten im Schacht: Truhe ganz nach unten, westlich daneben ein Trichter nach Osten (schleichend an die Truhe "
          "klicken). Auf diesen Trichter den Komposter, auf den Komposter schleichend einen Trichter – oben "
          "draufgeklickt zeigt er nach unten in den Komposter. Dann 12 Trichter nach Osten durch den Graben: "
          "schleichend an die Westseite des vorigen Trichters klicken.", {
    -1: ">" * N + "H",
    -2: "." * N + "O",
    -3: "." * N + ">C"})
f.schritt("Schlamm auf die 12 Trichter (Erde setzen, mit der Wasserflasche zu Schlamm machen). Nördlich und südlich "
          "davon je zwei Reihen Erde (je 12 lang) auf den Boden setzen und zu Ackerboden hacken – in der äußersten "
          "Nordreihe an der 4. und 9. Stelle von Westen ein Loch lassen, nördlich davor je einen Block, und Wasser "
          "in die beiden Löcher: Es hält alle Felder feucht. Am Ostende der beiden Reihen direkt neben dem Schlamm "
          "je 2 Blöcke übereinander, damit dort keine Frucht wächst.", {
    0: """
        ...#....#....
        AAAWAAAAWAAA.
        AAAAAAAAAAAA#
        MMMMMMMMMMMM.
        AAAAAAAAAAAA#
        AAAAAAAAAAAA.
    """,
    1: """
        .............
        .............
        ............#
        .............
        ............#
    """}, z0=-3)
f.schritt("Melonenkerne in die beiden Reihen direkt neben dem Schlamm (24 Stängel). In die äußeren Reihen Karotten "
          "oder Kartoffeln: Dort kann dann keine Frucht wachsen, und der feuchte Acker rundum lässt die Stängel "
          "schneller wachsen. Abgeerntete Karotten sofort nachpflanzen.", {
    1: """
        QQQ.QQQQ.QQQ
        TTTTTTTTTTTT
        ............
        TTTTTTTTTTTT
        QQQQQQQQQQQQ
    """}, z0=-2)
f.schritt("Beobachter über die Stängel (Höhe 2): Stell dich oben auf die Kolbenreihe und schau steil nach unten. Den "
          "ersten an die Seite der Wand klicken, jeden weiteren an die Seite des vorigen. Weil du nach unten schaust, "
          "schaut ihr Gesicht nach unten auf den Stängel, der rote Punkt nach oben. Beide Reihen, 24 Stück.", {
    2: "B" * N + "\n" + "." * N + "\n" + "B" * N}, z0=-1)
f.schritt("Auf jeden Beobachter einen normalen Block, auf die Kolben Redstone-Staub. Setzt ein Stängel eine Melone an, "
          "gibt sein Beobachter einen Impuls nach oben, der Staub daneben schaltet alle 12 Kolben. Zwei Fackeln oben "
          "auf die Blockreihen, damit auf der Farm nichts spawnt.", {
    3: "#" * N + "\n" + "R" * N + "\n" + "#" * N,
    4: "..I.........\n............\n.........I.."}, z0=-1)
f.schritt("Dein Platz östlich neben dem Schacht – die Stängel wachsen nur, wenn du in der Nähe bist. Das Knochenmehl "
          "holst du von oben aus der Truhe im Schacht.", {0: "P"}, x0=N + 2)

f.pruefe(boden=GRAS,
         nachher=["fill {x} {y+1} {z-1} {x+11} {y+1} {z-1} minecraft:melon_stem[age=7]",
                  "fill {x} {y+1} {z+1} {x+11} {y+1} {z+1} minecraft:melon_stem[age=7]"],
         erwartet={"items": {"minecraft:bone_meal": 20}})
