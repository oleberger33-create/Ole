"""Karotten/Kartoffeln mit Bauern (Profi): Feld 9 × 9 (80 Felder) um einen Komposter über der Wasserquelle in der Mitte,
Sammelzelle wie in der einfachen Farm am Westrand der mittleren Reihe.

Feld: x 0 … 8, z 0 … 8 (Ackerboden auf Höhe -1), Mitte (4, 4) = Wasser mit Komposter darüber. Mauer 2 hoch auf dem Ring
x -1/9, z -1/9. Zelle: Trichter (-1, -1, 4) unter der Lücke in der Mauer, Nichtsnutz auf dem Trichter (-2, -1, 4),
Truhe (-3, -1, 4), Einstiegsloch (-4, -1, 4).
"""
from profi_basis import *

f = profi("weizen", dict(
    name="Karotten/Kartoffeln mit Bauern (Profi)", diff=3, out="Karotten, Kartoffeln (auch Rote Bete)",
    where="Überall auf ebenem Boden, mehr als 32 Blöcke weg von Dörfern",
    afk="In der Nähe bleiben (Simulationsdistanz)",
    why="Zehnmal so viel Feld wie die einfache Farm: 80 Felder (9 × 9) statt 8. Der Komposter steht mitten im Feld "
        "über der Wasserquelle – das Wasser hält alle 80 Felder feucht (4 Blöcke in jede Richtung), und der Bauer "
        "bleibt in der Mitte, von wo er jedes Feld erreicht. Er erntet reife Karotten oder Kartoffeln, hebt sie auf, "
        "pflanzt nach und wirft alles über 24 Stück dem Nichtsnutz in der Zelle am Westrand zu; die Trichter unter "
        "ihm und vor ihm fangen es auf (wie in der einfachen Farm). Ein Bauer schafft so ein Feld locker – er braucht "
        "pro Pflanze ein, zwei Sekunden, die Pflanzen zum Reifen fast eine Stunde. Mauer 2 hoch (durch Zäune schlagen "
        "Zombies), Fackeln auf den Ecken, damit oben auf der Mauer nachts nichts spawnt.",
    help=[["Bauer erntet nicht", "Er braucht den Komposter als Arbeitsplatz (kein Baby) und arbeitet nur tagsüber; "
                                 "die Spielregel mob_griefing („Zerstörung durch Kreaturen“) muss an sein."],
          ["Nichts in der Truhe", "Er gibt erst ab mehr als 24 Stück einer Sorte ab – und nur in seiner freien Zeit "
                                  "(nachmittags bis abends, früh morgens), wenn er zur Zelle kommt. Der Nichtsnutz darf kein Bauer sein; Weizen backt "
                                  "der Bauer zu Brot und gibt erst ab 25 Broten etwas ab."],
          ["Felder bleiben leer", "Sein Vorrat ist aufgebraucht. In der Südmauer unten einen Block abbauen (der obere "
                                  "bleibt, so kommt er nicht hinaus), einen Stapel Karotten in die Lücke werfen – dort "
                                  "liegt kein Trichter, er holt sie sich. Danach wieder zumachen."],
          ["Dorfbewohner wird zur Hexe", "Ein Blitz hat neben ihm eingeschlagen. Ein Blitzableiter lenkt Blitze im "
                                         "Umkreis von 128 Blöcken auf sich – er muss der höchste Block seiner Säule "
                                         "sein und mindestens 4 Blöcke von den Dorfbewohnern weg stehen."]],
    meta=m("Rate: etwa 150 Karotten oder Kartoffeln pro Stunde (Schätzung nach den Wachstumsregeln im Wiki: auf einem "
           "vollen Feld wird eine Pflanze im Schnitt in gut 45 Minuten reif, 80 Felder, je Ernte bleiben nach dem "
           "Nachpflanzen etwa 1,7 übrig; die einfache Farm mit 8 Feldern kommt so auf etwa 15)",
           [("Mehr als 32 Blöcke weg von jedem Dorf, sonst läuft der Bauer dorthin.",
             W + "Tutorial:Crop_farming#Fully_automatic_farming_using_villagers"),
            ("Eine Wasserquelle hält Acker bis 4 Blöcke weit feucht – genau ein Feld 9 × 9 mit Wasser in der Mitte.",
             W + "Tutorial:Crop_farming#Classic_farm")],
           [("Bauer mit Komposter erntet und pflanzt nach; den Überschuss wirft er einem anderen Dorfbewohner zu, den "
             "die Farm einsperrt und auffängt.", W + "Tutorial:Crop_farming#Fully_automatic_farming_using_villagers"),
            ("Wachstum: Chance je Zufallstick 1/(25 / Wachstumswert + 1); gleiche Pflanzen ringsum halbieren den Wert.",
             W + "Tutorial:Crop_farming#Growth_rate"),
            ("Zelle mit Trichtern und Falltür: in der einfachen Farm auf dem Testserver (26.3) geprüft – der Bauer warf "
             "den Überschuss zu, die Trichter fingen ihn auf.", None)])))

f.zeichen(A="farmland", O="composter", V="villager", K="villager", Q="feldfrucht", I="torch",
          T=("oak_trapdoor", {"half": "top", "f": "s"}), w=("hopper", "w"))

f.schritt("Platz 11 × 11 ebnen (das Feld 9 × 9 plus Mauer). In die Mitte des Feldes ein Loch 1 tief. Am Westrand in der "
          "mittleren Reihe 4 Löcher nebeneinander nach Westen: unter der Mauer und dahinter für 2 Trichter, eins für "
          "die Truhe, eins zum Hineinsteigen (darin stehst du zum Öffnen der Truhe).", {
    -1: "----....-"}, x0=-4, z0=4)
f.schritt("Truhe ins dritte Loch von innen, davor 2 Trichter nach Westen in die Truhe (schleichend an die Truhe bzw. "
          "den Trichter klicken). Wassereimer ins Loch in der Mitte – es hält das ganze Feld feucht.", {
    -1: ".Cww....W"}, x0=-4, z0=4)
f.schritt("Hilfsblock (noch nicht hacken!): einen Block direkt nördlich neben das Wasserloch auf den Boden stellen.", {
    0: "D"}, x0=4, z0=3)
f.schritt("Komposter an die Südseite des Hilfsblocks klicken – er sitzt jetzt genau über dem Wasser. Hilfsblock wieder "
          "abbauen. Der Komposter ist der Arbeitsplatz des Bauern, mitten im Feld.", {
    0: "-\nO"}, x0=4, z0=3)
f.schritt("Das Feld 9 × 9 rund um den Komposter zu Ackerboden hacken (80 Felder).", {
    -1: """
        AAAAAAAAA
        AAAAAAAAA
        AAAAAAAAA
        AAAAAAAAA
        AAAA.AAAA
        AAAAAAAAA
        AAAAAAAAA
        AAAAAAAAA
        AAAAAAAAA
    """})
f.schritt("Mauer 2 hoch rund ums Feld (durch einen Zaun schlagen Zombies zu). Über dem vorderen Trichter im Westen "
          "bleibt sie offen, in der Südmauer bleiben in der Mitte 2 Blöcke breit offen (Eingang für den Bauern).", {
    0: """
        ###########
        #.........#
        #.........#
        #.........#
        #.........#
        ..........#
        #.........#
        #.........#
        #.........#
        #.........#
        #####..####
    """,
    1: """
        ###########
        #.........#
        #.........#
        #.........#
        #.........#
        ..........#
        #.........#
        #.........#
        #.........#
        #.........#
        #####..####
    """}, x0=-1, z0=-1)
f.schritt("Über den vorderen Trichter eine Falltür in die OBERE Hälfte (an die Mauer im Norden klicken, obere Hälfte "
          "der Seite): Darunter passt kein Dorfbewohner durch, aber Geworfenes fliegt durch.", {1: "T"}, x0=-1, z0=4)
f.schritt("Zelle für den zweiten Dorfbewohner über dem hinteren Trichter: im Norden 3 Blöcke übereinander, Glas über "
          "der Truhe, darüber ein Block, oben als Dach ein Block (an den obersten Block im Norden klicken). Im Süden "
          "noch offen lassen.", {
    0: ".#\nG.", 1: ".#\n#.", 2: ".#\n.#"}, x0=-3, z0=3)
f.schritt("Karotten oder Kartoffeln auf alle 80 Felder – Weizen geht auch, aber den backt der Bauer zu Brot und gibt "
          "erst ab 25 Broten etwas ab.", {
    0: """
        QQQQQQQQQ
        QQQQQQQQQ
        QQQQQQQQQ
        QQQQQQQQQ
        QQQQ.QQQQ
        QQQQQQQQQ
        QQQQQQQQQ
        QQQQQQQQQ
        QQQQQQQQQ
    """})
f.schritt("Zwei Dorfbewohner: Der Bauer kommt durch die Lücke im Süden aufs Feld – ein Dorfbewohner ohne Beruf läuft "
          "von selbst zum Komposter, sonst im Boot hineinrudern. Vorher (auf normalem Boden) wirfst du ihm ein paar "
          "Karotten oder Kartoffeln zu. Der zweite darf kein Bauer werden (Nichtsnutz im grünen Kittel, oder einer, "
          "mit dem du schon gehandelt hast): mit einer Lore auf einer Schiene von Süden in seine Zelle schieben, Lore "
          "abbauen.", {
    0: """
        K...
        ....
        ....
        ...V
    """}, x0=-2, z0=4)
f.schritt("Zelle im Süden schließen.", {0: "#", 1: "#"}, x0=-2, z0=5)
f.schritt("Feld im Süden schließen.", {0: "##", 1: "##"}, x0=4, z0=9)
f.schritt("Fackeln oben auf die vier Ecken der Mauer: Sonst können nachts oben auf der Mauer Zombies erscheinen und "
          "ins Feld springen.", {
    2: """
        I.........I
        ...........
        ...........
        ...........
        ...........
        ...........
        ...........
        ...........
        ...........
        ...........
        I.........I
    """}, x0=-1, z0=-1)
f.schritt("Dein Platz neben dem Einstiegsloch vor der Truhe.", {0: "P"}, x0=-5, z0=4)

f.pruefe(boden=GRAS, zeit="cycle",
         nachher=["kill @e[type=minecraft:villager,x={x},y={y},z={z},distance=..12]",
                  'summon minecraft:villager {x+2}.5 {y} {z+4}.5 {PersistenceRequired:1b,CanPickUpLoot:1b,'
                  'VillagerData:{profession:"minecraft:farmer",level:1,type:"minecraft:plains"},Inventory:[{id:'
                  '"minecraft:carrot",count:8}]}',
                  'summon minecraft:villager {x-2}.5 {y} {z+4}.5 {PersistenceRequired:1b,CanPickUpLoot:1b,'
                  'VillagerData:{profession:"minecraft:nitwit",level:1,type:"minecraft:plains"}}',
                  "fill {x} {y} {z} {x+8} {y} {z+8} minecraft:carrots[age=7] replace minecraft:carrots"],
         erwartet={"items": {"minecraft:carrot": 60}})
