"""Wächter-Farm (Profi): ohne Trockenlegen. Seelensand-Feld 7 × 7 (x 0 … 6, z 0 … 6) auf Höhe 57 innerhalb der
Monument-Box; das Meerwasser darüber wird zu Blasensäulen bis zur Oberfläche (62). Wächter, die dort spawnen (die Box
reicht bis Höhe 61) oder hineinschwimmen, schießen nach oben durch eine Gerüst-Lage (63) in einen Wasserstrom (64) unter
einer Decke (65). Der Strom fließt 7 Blöcke nach Süden (die letzte Reihe z 7 liegt auf festen Blöcken) und endet über
einer Reihe Lagerfeuer (z 8) auf Trichtern, die in eine Truhe (8, -1, 8) führen.

Plan-Höhen: y 0 = Höhe 63 (erste Luftschicht über dem Meer), y -1 = Wasseroberfläche (62), Box-Oberkante 61 = y -2,
Box-Unterkante 39 = y -24. Boden y -7 (56), Seelensand y -6 (57), Blasensäulen y -5 … -1, Gerüst y 0, Strom y 1,
Decke y 2 (9 × 11, liegt auf den Wänden). Rand unter dem Gerüst (trägt es): y -1 bei x -1 und x 7. Warteplatz 26 Blöcke
über dem Gerüst.
"""
from profi_basis import *

FELD = [(x, z) for x in range(7) for z in range(7)]
RAND_UNTEN = [(x, z) for x in (-1, 7) for z in range(-1, 8)]          # y -1, trägt das Gerüst
GERUEST = [(x, z) for x in range(-1, 8) for z in range(7)]             # y 0 (Reihe z 7: feste Blöcke)
WAND = ([(x, z) for x in (-1, 7) for z in range(-1, 10)] +             # y 1 (y 0 nur hinten und an der Kammer)
        [(x, z) for x in range(7) for z in (-1, 9)])

f = profi("waechter", dict(
    name="Wächter-Farm mit Blasensäulen (Profi)", diff=4, out="Prismarinscherben, Prismarinkristalle, Kabeljau",
    where="Ozeanmonument: innerhalb seiner Grundfläche (58 × 58), wo das Dach nicht höher als Höhe 56 reicht "
          "(z. B. am Rand). Kein Trockenlegen nötig.",
    afk="Ja – oben auf der Säule, 26 Blöcke über der Plattform (ohne Erfahrung)",
    why="Statt mit dem Dreizack zu kämpfen, sammelt die Farm von selbst. Wächter spawnen nur im Wasser der Monument-Box "
        "(bis Höhe 61), unter einem Dach 20-mal so oft wie unter freiem Himmel. Auf einem Boden 7 × 7 auf Höhe 56 "
        "liegt Seelensand: Darüber wird das Meerwasser zu Blasensäulen, die alles schnell nach oben tragen – Wächter, "
        "die darin spawnen oder hineinschwimmen. Die Säulen enden an der Wasseroberfläche unter einer Lage Gerüst. "
        "Gerüst lässt Mobs von unten durch, trägt sie von oben und hält Wasser. Darauf fließt ein flacher Wasserstrom "
        "unter einer festen Decke – die macht das ganze Feld dunkel (volle Spawnrate) und hält die Wächter im Strom. "
        "Stillstehende Wächter treibt fließendes Wasser besonders schnell: Nach 7 Blöcken endet der Strom, die "
        "Wächter fallen auf eine Reihe Lagerfeuer, zappeln dort (an Land ersticken sie nicht) und verbrennen in "
        "etwa 15 Sekunden. Die Trichter darunter saugen die Beute durch die niedrigen Lagerfeuer an und füllen die "
        "Truhe. Die Plattform liegt über dem Meer, gebaut wird also fast nur an der Luft.",
    help=[["Keine Wächter oben", "Der Seelensand muss in der Monument-Grundfläche liegen und die Blasensäulen müssen "
                                 "bis zur Oberfläche frei sein (kein Block, kein Seetang darin). Spawns gibt es nur "
                                 "unter Höhe 62, also im Wasser zwischen Seelensand und Oberfläche."],
          ["Wasser läuft nach unten weg", "Gerüst wird nicht nass: Es hält das Wasser des Stroms. Fehlt ein Gerüst oder "
                                          "ist eins heruntergefallen, nachsetzen – jedes muss höchstens 6 Gerüste weit "
                                          "von einem Gerüst auf einem Randblock entfernt sein."],
          ["Wächter bleiben im Strom", "Der Strom ist genau 8 lang (Quellen an der Rückwand): Das Wasser endet direkt "
                                       "vor den Lagerfeuern. Steht Wasser auf den Feuern, sind sie aus."],
          ["Wenig Wächter", "Das übrige Monument füllt das Monster-Limit mit. Im Monument Wächter töten oder Räume "
                            "zumauern hilft. Erfahrung gibt es nur, wenn du sie selbst tötest."]],
    meta=m("Rate: etwa 50–150 Wächter pro Stunde (Schätzung, nicht gemessen: 49 Blasensäulen mit je 3 Spawn-Ebenen unter "
           "Dach; das restliche Monument teilt sich das Monster-Limit). Je Wächter im Schnitt etwa 1 Prismarinscherbe, "
           "dazu Kabeljau und Prismarinkristalle. Die einfache Variante liefert nur, was du selbst erlegst.",
           [("Ozeanmonument: Wächter spawnen nur in Wasser in der Box 58 × 58, von Höhe 39 bis 61.",
             W + "Tutorial:Guardian_farming#Spawning"),
            ("Unter einem Dach spawnen Wächter öfter; im offenen Ozean scheitern 95 % der Versuche.",
             W + "Guardian#Spawning")],
           [("Ohne Trockenlegen: Seelensand-Blasensäulen tragen die Wächter in eine Kammer an der Oberfläche, von dort zur "
             "Tötungskammer.", W + "Tutorial:Guardian_farming#Automatic_farms"),
            ("Brennende Lagerfeuer töten Wächter, Trichter darunter sammeln die Beute.",
             W + "Tutorial:Guardian_farming#Transport_and_killing"),
            ("Aufwärts-Blasensäulen tragen Wesen schnell nach oben; sie entstehen nur in Wasserquellen über Seelensand.",
             W + "Bubble_Column"),
            ("Stillstehende Wächter treibt fließendes Wasser viel schneller als andere Mobs; an Land ersticken sie nicht, "
             "sie springen herum.", W + "Guardian#Behavior"),
            ("Gerüst kann geflutet werden – nur mit dem Eimer, fließendes Wasser dringt nicht ein; Mobs kommen von unten "
             "hindurch, oben stehen sie darauf; es hält höchstens 6 Blöcke von einer Stütze.",
             W + "Scaffolding"),
            ("Auf einem Lagerfeuer nimmt man alle halbe Sekunde 1 Schaden; Wächter haben 30 Leben.", W + "Damage#Campfire"),
            ("Auf dem Testserver (26.3) geprüft (andere Farmen): Trichter saugen durch nicht ganz hohe Blöcke; "
             "Wasserstrom endet nach 7 Blöcken.", None)])))

f.zeichen(**{"#": "cobblestone"}, U="soul_sand", X="scaffolding", Q="campfire", K="cobblestone")

f.schritt("Stelle suchen: innerhalb der Grundfläche des Monuments, wo das Dach höchstens bis Höhe 56 reicht. Plan "
          "starten und mit den Pfeilen im Plan-Menü so verschieben, dass die Gerüst-Ebene auf Höhe 63 liegt (eine Ebene "
          "über dem Meer) – dann liegt alles auf der richtigen Höhe. Unter Wasser zuerst den Boden 7 × 7 auf Höhe 56 "
          "(mit einer Hilfssäule vom Dach aus; liegt das Dach genau auf Höhe 56, ist es schon der Boden) und an seiner "
          "Westseite eine Säule bis eine Ebene unter die Wasseroberfläche.", {
    -7: raster_aus({**{p: "#" for p in FELD}, (-1, 0): "#"}, -1, 0, 6, 6),
    **{y: "#" for y in range(-6, -1)}}, x0=-1, z0=0)
f.schritt("Seelensand auf den ganzen Boden (49 Stück). Nach einer Sekunde steigen darüber Blasen bis zur Oberfläche: "
          "Das Meerwasser ist jetzt eine Fläche aus Blasensäulen.", {
    -6: raster_aus({p: "U" for p in FELD}, 0, 0, 6, 6)})
f.schritt("Rand in der obersten Wasserschicht (Höhe 62): auf die Säule einen Block, von dort die Westreihe (9 Blöcke, "
          "von einem Block nördlich des Feldes bis einen Block südlich davon). Auf ihr nördliches Ende einen Block und "
          "von dort eine Reihe eine Ebene über dem Wasser nach Osten (9 Blöcke, die Rückreihe), unter ihr östliches Ende "
          "einen Block (an die Unterseite klicken) und von dort die Ostreihe nach Süden.", {
    -1: raster_aus({p: "#" for p in RAND_UNTEN}, -1, -1, 7, 7),
    0: raster_aus({(x, -1): "#" for x in range(-1, 8)}, -1, -1, 7, 7)}, x0=-1, z0=-1)
f.schritt("Gerüst-Lage über dem Seelensand, eine Ebene über dem Wasser: zuerst auf jeden Block der West- und der "
          "Ostreihe, auf dem noch nichts steht, ein Gerüst – nur nicht auf den südlichsten. Dann von beiden Seiten nach "
          "innen (an die Seite eines Gerüsts klicken). Kein Gerüst darf weiter als 6 von einem Gerüst auf dem Rand "
          "entfernt sein – hier sind es höchstens 4. Südlich daran eine Reihe aus 9 festen Blöcken: Dort endet der "
          "Strom, und Beute, "
          "die aus der Kammer zurückfliegt, bleibt nicht im Gerüst hängen.", {
    0: raster_aus({**{p: "X" for p in GERUEST}, **{(x, 7): "#" for x in range(-1, 8)}}, -1, 0, 7, 7)}, x0=-1, z0=0)
KAMMER = {(8, 7): "#", (8, 8): "C", (7, 8): ">"}
KAMMER.update({(x, 8): ">" for x in range(7)})
f.schritt("Tötungskammer südlich davon: Östlich neben den südlichsten Randblock einen Block (dein Stand zum Leeren der "
          "Truhe), südlich davon die Truhe in die Wasseroberfläche. Dann 8 Trichter in einer Reihe nach Westen, "
          "schleichend jeweils an die Truhe bzw. an den Trichter östlich davon klicken – alle zeigen nach Osten zur "
          "Truhe.", {
    -1: raster_aus(KAMMER, 0, 7, 8, 8)}, x0=0, z0=7)
f.schritt("Auf die 7 westlichen Trichter je ein Lagerfeuer (oben auf den Trichter klicken), daneben und dahinter "
          "Wände: je ein Block an beide Enden der Feuerreihe (der östliche schleichend auf den 8. Trichter) und eine "
          "Reihe von 9 Blöcken südlich davon.", {
    0: raster_aus({**{(x, 8): "Q" for x in range(7)}, (-1, 8): "#", (7, 8): "#",
                   **{(x, 9): "#" for x in range(-1, 8)}}, -1, 8, 7, 9)}, x0=-1, z0=8)
f.schritt("Wände eine Ebene höher rund um Feld und Kammer (auf die äußeren Gerüste, die Rückreihe, die Enden der festen "
          "Reihe und die Kammerwände). Dann 7 Wasserquellen "
          "an die Innenseite der Rückwand klicken (nicht auf das Gerüst – Gerüst lässt sich per Eimer füllen und ließe "
          "dann Wasser durch): Der Strom fließt genau 7 Blöcke nach Süden und endet vor den Lagerfeuern.", {
    1: raster_aus({**{p: "#" for p in WAND}, **{(x, 0): "W" for x in range(7)},
                   **{(x, z): "F" for x in range(7) for z in range(1, 8)}}, -1, -1, 7, 9)}, x0=-1, z0=-1)
f.schritt("Decke 9 × 11 auf die Wände, über Strom und Kammer (vom Rand aus nach innen bauen): Sie macht das Feld darunter "
          "dunkel – unter Dach spawnen Wächter 20-mal so oft – und hält hochgeschossene Wächter im Strom.", {
    2: raster_aus({(x, z): "#" for x in range(-1, 8) for z in range(-1, 10)}, -1, -1, 7, 9)}, x0=-1, z0=-1)
f.schritt("Warteplatz: eine Säule auf die Decke, oben 26 Blöcke über dem Gerüst stehen. Näher als 24 Blöcke spawnt "
          "nichts, Laser reichen 15 Blöcke weit. Die Beute holst du aus der Truhe.", {
    **{y: "K" for y in range(3, 26)}, 26: "P"}, x0=3, z0=3)

# Echtes Monument (Welt mit Bauwerken): Box blockgenau ausmessen, das Feld 3 Blöcke von ihrer Nordwestecke entfernt
# (Box-Unterkante 39 = Plan-y -24, also Plan-y 0 = Höhe 63). Der Test räumt den Bauplatz frei; Wasser bis Höhe 62 füllt
# ihn wieder wie das Meer. Gemessen: Beute in Trichtern und Truhe (die einfache Variante hat keinen Test).
MEER = dict(boden="minecraft:water", fuellung="minecraft:water", zeit="day")
BEUTE = "minecraft:prismarine_shard|minecraft:prismarine_crystals|minecraft:cod"
f.pruefe(**MEER, welt="struktur",
         bauwerk={"id": "minecraft:monument", "suchen": True, "hoehe": 50, "groesse": [58, 58],
                  "ecke": [-3, -24, -3]},
         erwartet={"items": {BEUTE: 1}})
# Mechanik in der flachen Welt, hoch über dem Boden: ein Steinkasten mit Wasser darin ersetzt das Meer (läuft nicht aus),
# 6 Wächter in die Blasensäulen – hoch, Strom, Lagerfeuer, Truhe.
f.pruefe_auch("waechter_profi_mech", zeit="day", hoehe=100,
              vorher=["fill {x-2} {y-8} {z-2} {x+8} {y-1} {z+8} minecraft:stone",
                      "fill {x-1} {y-7} {z-1} {x+7} {y-1} {z+7} minecraft:water"],
              nachher=mobs("guardian", [(0, -4, 1), (3, -4, 3), (6, -4, 5), (1, -3, 6), (5, -3, 1), (3, -2, 6)]),
              erwartet={"items": {BEUTE: 4}})
