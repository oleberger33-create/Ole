"""Kürbis- & Melonen-Farm (Profi): 16 Stängel in zwei Reihen teilen sich 8 Fruchtfelder aus Schlamm über Trichtern.

Querschnitt (Norden → Süden, z -2 … 2):  Karotten | Stängel | Schlamm-Fruchtfeld | Stängel | Karotten
Über jedem Stängel ein Beobachter (schaut nach unten), über jedem Fruchtfeld ein Kolben (zeigt nach unten), oben drauf
Blöcke bzw. Redstone-Staub. Eine Wasserquelle in der Karottenreihe hält alle Felder feucht (±4 Blöcke).
"""
from profi_basis import *

f = profi("kuerbis", dict(
    name="Kürbis- & Melonen-Farm (Profi)", diff=3,
    out="Melonen oder Kürbisse (nebenbei Karotten/Kartoffeln)",
    where="Überall auf ebenem Boden mit freiem Himmel über den Karotten (sonst Fackeln an die Außenseite)",
    afk="In der Nähe bleiben (Simulationsdistanz)",
    why="Viermal so viele Stängel wie die einfache Farm, doppelt so viele Stängel pro Fruchtfeld und alles "
        "automatisch: 16 Melonen- oder Kürbisstängel stehen in zwei Reihen links und rechts von 8 Fruchtfeldern aus "
        "Schlamm. Jede andere Seite eines Stängels ist belegt (Nachbarstängel, Karotten bzw. das Wasserloch, "
        "Stützwand, Endblock) – die Frucht kann nur auf den Schlamm. Die Karotten außen blockieren die Außenseite, "
        "und ihr feuchter Acker lässt die Stängel schneller wachsen (mehr feuchter Acker rundum: Chance 1/4 statt 1/5 "
        "je Zufallstick). "
        "Über jedem Stängel schaut ein Beobachter nach unten: Setzt irgendein Stängel eine Frucht an, gibt er einen "
        "Impuls in den Block über sich, der Staub daneben schaltet alle 8 Kolben, sie zerbrechen die Früchte, und die "
        "Trichter unter dem Schlamm saugen die Stücke in die Truhe. Ergebnis: etwa 5-mal so viel wie die einfache "
        "Farm.",
    help=[["Frucht wächst neben der Farm", "Früchte dürfen nur auf den Schlamm: Jede andere Seite eines Stängels muss "
                                           "belegt sein – Karotten (nach der Ernte sofort nachpflanzen), Stützwand im "
                                           "Westen, Endblöcke im Osten."],
          ["Stängel wachsen nicht", "Sie brauchen Licht ≥ 9; es kommt von der Seite über den Karotten. Unter einem "
                                    "Dach oder unter der Erde Fackeln an die Außenseite. Der Acker muss feucht sein "
                                    "(die Wasserquelle in der Nordreihe reicht für alle Felder)."],
          ["Kolben fahren nicht aus", "Beobachter müssen nach unten schauen (roter Punkt oben) und einen normalen "
                                      "Block tragen – kein Glas, das leitet kein Redstone. Der Staub liegt direkt "
                                      "auf den Kolben."],
          ["Stücke bleiben liegen", "Unter jedem Schlammfeld muss ein Trichter sein (durch Erde saugt er nicht). Was "
                                    "auf den Acker springt, sammelst du ab und zu ein."]],
    meta=m("Rate: etwa 50 Früchte pro Stunde, also rund 250 Melonenscheiben oder 50 Kürbisse (Schätzung nach den "
           "Wachstumsregeln im Wiki: 16 Stängel, Chance 1/4 je Zufallstick, eine Fruchtseite; die einfache Farm "
           "kommt so auf etwa 10 Früchte pro Stunde)",
           [("Überall auf ebenem Boden. Die Stängel brauchen Licht ≥ 9, das Fruchtfeld Luft über Erde, Gras, Acker "
             "oder Schlamm.", W + "Tutorial:Pumpkin_and_melon_farming")],
           [("Ein reifer Stängel wählt bei jedem Wachstum eine zufällige Seite; nur wenn dort Luft über passendem Boden "
             "ist, wächst die Frucht. Belegte Seiten kosten Versuche, aber nur so landet jede Frucht über einem "
             "Trichter.",
             W + "Tutorial:Pumpkin_and_melon_farming#Growth_mechanics"),
            ("Wachstumschance: feuchter Acker unter und neben der Pflanze erhöht sie; gleiche Pflanzen nur in Reihen, "
             "nicht schräg daneben.", W + "Tutorial:Crop_farming#Growth_rate"),
            ("Kolben, die in Kürbis oder Melone drücken, zerbrechen sie; Beobachter melden den Stängel, der eine "
             "Frucht ansetzt.", W + "Tutorial:Pumpkin_and_melon_farming#Fully_automatic_farms"),
            ("Beobachter direkt über dem Stängel und Trichter unter Schlamm: in der einfachen Farm auf dem Testserver "
             "(26.3) geprüft – das Licht kommt von der Seite.", None)])))

f.zeichen(A="farmland", M="mud", T="melon_stem", Q="feldfrucht", K=("piston", "d"), B=("observer", "d"))

f.schritt("Ausheben: in der Mitte eine Reihe 9 lang und 2 tief (für Trichter und Truhe), zwei Reihen weiter nördlich "
          "ein einzelnes Loch für das Wasser (vierte Stelle von Westen).", {
    -2: """
        .........
        .........
        ---------
    """,
    -1: """
        ...-.....
        .........
        ---------
    """}, z0=-2)
f.schritt("Stützwand am Westende des Grabens: 3 Blöcke breit, 2 hoch. Dann stellst du dich in den Graben, schaust nach "
          "oben und setzt 8 Kolben in die Reihe über dem Graben (Höhe 1) – den ersten an die Stützwand geklickt, "
          "jeden weiteren an den vorigen. Weil du nach oben schaust, zeigen alle Kolben nach unten (zu dir).", {
    0: """
        #
        #
        #
    """,
    1: """
        #
        #KKKKKKKK
        #
    """}, x0=-1, z0=-1)
f.schritt("Unten in den Graben: Truhe ans Ostende, dann 8 Trichter nach Osten (schleichend an die Truhe bzw. den "
          "vorigen Trichter klicken). Über der Truhe bleibt das Loch offen – von dort öffnest du sie.", {
    -2: ">>>>>>>>C"})
f.schritt("Schlamm auf die 8 Trichter (Wasserflasche auf Erde). Die zwei Reihen daneben und die zwei äußeren Reihen zu "
          "Ackerboden hacken (31 Felder), Wassereimer ins Loch – es hält alle Felder feucht. Am Ostende der beiden "
          "Stängelreihen je ein Block, damit dort keine Frucht wächst.", {
    -1: """
        AAAWAAAA
        AAAAAAAA
        MMMMMMMM
        AAAAAAAA
        AAAAAAAA
    """,
    0: """
        ........
        ........#
        .........
        ........#
    """}, z0=-2)
f.schritt("Melonen- oder Kürbiskerne in die beiden Reihen direkt neben dem Schlamm (16 Stängel). In die äußeren Reihen "
          "Karotten oder Kartoffeln: Dort kann dann keine Frucht wachsen, und der feuchte Acker rundum lässt die "
          "Stängel schneller wachsen. Abgeerntete Karotten sofort nachpflanzen.", {
    0: """
        QQQ.QQQQ
        TTTTTTTT
        ........
        TTTTTTTT
        QQQQQQQQ
    """}, z0=-2)
f.schritt("Beobachter über die Stängel (Höhe 1): Stell dich oben auf die Kolbenreihe und schau steil nach unten. Den "
          "ersten an die Seite der Stützwand klicken, jeden weiteren an die Seite des vorigen. Weil du nach unten "
          "schaust, schaut ihr Gesicht nach unten auf den Stängel, der rote Punkt nach oben. Beide Reihen, 16 Stück.", {
    1: """
        BBBBBBBB
        ........
        BBBBBBBB
    """}, z0=-1)
f.schritt("Auf jeden Beobachter einen normalen Block, auf die Kolben Redstone-Staub. Setzt ein Stängel eine Frucht an, "
          "gibt sein Beobachter einen Impuls nach oben, der Staub daneben schaltet alle 8 Kolben: Sie zerbrechen die "
          "Früchte, die Stücke fallen auf den Schlamm, die Trichter saugen sie ein.", {
    2: """
        ########
        RRRRRRRR
        ########
    """}, z0=-1)
f.schritt("Dein Platz neben dem Truhenloch – die Stängel wachsen nur, wenn du in der Nähe bist.", {0: "P"}, x0=10)

f.pruefe(boden=GRAS,
         nachher=["fill {x} {y} {z-1} {x+7} {y} {z-1} minecraft:melon_stem[age=7]",
                  "fill {x} {y} {z+1} {x+7} {y} {z+1} minecraft:melon_stem[age=7]"],
         erwartet={"items": {"minecraft:melon_slice": 200}})
