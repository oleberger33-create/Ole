"""Schnee-Farm (Profi): 3 Schneegolems in Zellen nebeneinander, unter jedem Golem-Boden eine Trichterlore, die die
Schneebälle durch den Block hindurch einsammelt; Trichterreihe → Crafter (Schneebälle → Schneeblöcke) → Doppeltruhe.

Koordinaten: Zellen bei x -2, 0, 2 auf z 1 (Golem steht auf dem Boden (x, 1, 1), die Schneedecke liegt auf y 2).
Stufe für den Spieler y 0, z 0 (x -3..3), AFK-Platz (0, 1, 0). Schienen mit Trichterloren (x, 0, 1), Trichterreihe
y -1 nach Osten (x -2..3) in den Crafter (4, -1, 1, Gesicht nach Osten) → Truhe (5, -1, 0..1). Takt: Beobachter
(4, 0, 2) schaut nach Süden, (4, 0, 3) nach Norden; der erste gibt sein Signal in den Block (4, 0, 1) über dem
Crafter.
"""
from profi_basis import *

f = profi("schnee", dict(
    name="Schnee-Farm (Profi)", diff=3, out="Schneeblöcke (und Schneebälle)",
    where="Überall außer Wüste, Savanne, Tafelberg (Badlands) und Nether; Platz 9 × 4",
    afk="Halb – auf der Stufe stehen und die linke Maustaste mit der Schaufel halten; alles landet in der Truhe",
    why="Drei Schneegolems statt einem, jeder in seiner eigenen Zelle mit Dach (Regen schadet ihnen), vorne ein "
        "Spalt, durch den du die Schneedecke abbaust. Jeder Golem legt sofort eine neue Schneedecke unter sich. "
        "Der große Unterschied: Die Schneebälle fallen auf den Boden der Zelle, und eine Trichterlore direkt "
        "darunter sammelt sie durch den Block hindurch ein – du musst nichts aufheben (bis 2,5 pro Sekunde; was "
        "du schneller abbaust, hebst du wie bisher selbst auf). Trichter ziehen die Schneebälle aus den Loren in "
        "eine Trichterreihe und weiter in einen Crafter, in dem nur die 4 Felder oben links offen sind: Ein Beobachter-Takt lässt ihn immer wieder craften, aus je "
        "4 Schneebällen wird ein Schneeblock, der in die Truhe davor fällt. Schneeblöcke stapeln sich bis 64 statt "
        "16 – in eine Doppeltruhe passen so 13 824 Schneebälle statt 864.",
    help=[["Kein Schnee",
           "Spielregel mob_griefing („Zerstörung durch Kreaturen“) muss an sein. In Wüste, Savanne, Tafelberg und "
           "im Nether schmilzt der Golem; ohne Dach schadet ihm Regen."],
          ["Schneebälle bleiben liegen",
           "Unter jedem Golem-Boden muss eine Trichterlore auf der Schiene stehen, darunter ein Trichter. Eine Lore "
           "fasst 80 Schneebälle, die Trichter schaffen 2,5 pro Sekunde – baust du schneller ab, bleibt der Rest "
           "liegen und du sammelst ihn selbst ein, wenn du direkt davor stehst."],
          ["Keine Schneeblöcke",
           "Im Crafter 5 Felder sperren (anklicken, solange sie leer sind): die rechte Spalte und die untere Reihe – "
           "frei bleiben nur die 4 Felder oben links. Die beiden Beobachter müssen sich anschauen; der nördliche gibt "
           "sein Signal (roter Punkt) in den Block über dem Crafter."],
          ["Golem stirbt",
           "Monster greifen ihn durch den Spalt an, wenn er sie mit Schneebällen bewirft – die Gegend hell "
           "machen (Fackeln)."]],
    meta=m("Rate: bis etwa 9000 Schneebälle (2250 Schneeblöcke) pro Stunde in der Truhe (Schätzung: die "
           "Trichterreihe schafft 2,5 Items pro Sekunde, eine Schaufel baut Schnee sofort ab). Die einfache: nur so "
           "viel, wie in dein Inventar passt (576 Schneebälle), danach von Hand craften.",
           [("Nicht in Wüste, Savanne, Tafelberg (Badlands) und Nether: dort schmilzt der Golem.",
             W + "Tutorial:Snow_farming")],
           [("Wiki-Vorschläge für eine bessere Schneefarm: Trichterlore unter dem Golem-Boden, Trichter zur Truhe, "
             "Crafter für Schneeblöcke, mehr Golems.", W + "Tutorial:Snow_farming"),
            ("Eine Trichterlore sammelt Items, die auf dem Block direkt über der Schiene liegen; ein Trichter unter "
             "der Schiene leert sie.", W + "Minecart_with_Hopper"),
            ("Schnee gibt beim Abbau mit einer Schaufel 1 Schneeball pro Schicht; der Golem legt Schnee auf jeden "
             "Block mit voller Oberseite, auf dem er steht.", W + "Snow"),
            ("Crafter: gesperrte Felder bleiben leer, bei jedem Redstone-Impuls entsteht ein Gegenstand und kommt in "
             "den Behälter vor dem Gesicht.", W + "Crafter"),
            (TEST + "Trichterlore unter einem Block (Wolle-Farm) und Crafter mit Beobachter-Takt (Stöcke-Crafter) "
                    "funktionieren.", None)])))

f.zeichen(Y=("rail", {"axis": "x"}), Q="hopper_minecart", X="snow_golem", A=("crafter", "e"),
          O=("observer", "s"), U=("observer", "n"))

f.schritt("Ausheben: eine Rinne 1 tief und 8 lang von West nach Ost (für Trichter und Crafter), am Ostende 1 Block "
          "nach Norden mehr (für die Doppeltruhe).", {
    -1: ".......-\n--------"}, x0=-2, z0=0)
f.schritt("Der Crafter ans Ostende der Rinne, auf den vorletzten Platz: stell dich 3 Blöcke östlich davon auf den "
          "Boden, schau nach Westen und klick auf den Boden der Rinne – das Gesicht des Crafters zeigt dann nach "
          "Osten, zu dir (aus 1–2 Blöcken Abstand schaust du zu steil nach unten, dann zeigt es nach oben). Davor "
          "(Osten) zwei Truhen: eine vor das Gesicht, eine nördlich daneben (Doppeltruhe). Dann den Crafter öffnen "
          "und 5 Felder sperren (leere Felder anklicken): die ganze rechte Spalte und die ganze untere Reihe – frei "
          "bleiben nur die 4 Felder oben links, genau das Rezept für einen Schneeblock.", {
    -1: "..C\n.AC"}, x0=3, z0=0)
f.schritt("6 Trichter nach Osten in die Rinne: den ersten schleichend an die Westseite des Crafters klicken, jeden "
          "weiteren an die Westseite des vorigen.", {
    -1: ">>>>>>"}, x0=-2, z0=1)
f.schritt("Takt aus zwei Beobachtern, die sich anschauen, südlich vom Crafter auf dem Boden: Für den ersten stell "
          "dich nördlich davon auf den Boden (neben die Truhe), schau flach nach Süden und klick auf den Boden 2 "
          "Blöcke vor dir – Gesicht nach Süden, roter Punkt nach Norden zum Platz über dem Crafter. Den zweiten "
          "südlich daran: von Süden her an die Südseite des ersten klicken und dabei nach Norden schauen.", {
    0: "O\nU"}, x0=4, z0=2)
f.schritt("Auf Höhe 0: die Stufe für dich (7 Blöcke, nördlich der Rinne), auf die Trichter abwechselnd Block und "
          "Schiene (Schienen unter den späteren Golems; beim Setzen nach Osten oder Westen schauen), hinten eine "
          "Reihe Blöcke. Jetzt erst schleichend einen Block auf den Crafter – der nördliche Beobachter gibt sein "
          "Signal in diesen Block, und der schaltet den Crafter darunter.", {
    0: """
        #######.
        #Y#Y#Y##
        #######.
    """}, x0=-3, z0=0)
f.schritt("Auf jede Schiene eine Trichterlore.", {
    0: "Q.Q.Q"}, x0=-2, z0=1)
f.schritt("Auf Höhe 1 über den Loren und dazwischen eine Reihe Blöcke (7 lang, von einem Ende aus Block an Block "
          "setzen, nicht auf die Loren klicken) – die Böden der Golems liegen genau über den Loren. Dahinter die "
          "Rückwand weiter hoch.", {
    1: "#######\n#######"}, x0=-3, z0=1)
f.schritt("Zellen: auf Höhe 2 und 3 Trennwände zwischen und neben den Golem-Böden, hinten die Rückwand. Vorne auf "
          "Höhe 3 eine Reihe Glas (7 lang, an die Vorderseite der Wände klicken) – darunter bleibt auf Höhe 2 der "
          "Spalt, durch den du abbaust.", {
    2: ".......\n#.#.#.#\n#######",
    3: "GGGGGGG\n#.#.#.#\n#######"}, x0=-3, z0=0)
f.schritt("In jede Zelle einen Schneegolem bauen: 2 Schneeblöcke übereinander auf den Boden, oben drauf einen "
          "geschnitzten Kürbis (der steht dann auf Höhe 4).", {
    2: "X.X.X"}, x0=-2, z0=1)
f.schritt("Dach auf Höhe 4 über die Zellen (7 Blöcke, auf die Trennwände legen) – Regen schadet den Golems.", {
    4: "#######"}, x0=-3, z0=1)
f.schritt("Hier stehen: auf der Stufe vor dem mittleren Golem. Schaufel in die Hand, durch den Spalt auf die vordere "
          "Kante der Schneedecke zielen (nicht auf den Golem!) und die linke Maustaste halten. Die Schneebälle "
          "landen über Loren, Trichter und Crafter als Schneeblöcke in der Truhe.", {
    1: "P"})

f.pruefe(boden=GRAS, biom="minecraft:snowy_plains", erwartet={"bloecke": {"minecraft:snow": 3}})
# Sammelweg: Schneebälle auf die drei Golem-Böden legen – sie müssen als Schneeblöcke in der Truhe ankommen
f.pruefe_auch("schnee_profi_mech", boden=GRAS, biom="minecraft:snowy_plains",
              nachher=["data merge block {x+4} {y-1} {z+1} {disabled_slots:[I;2,5,6,7,8]}"] +
              [f'summon minecraft:item {{x{x:+d}}}.5 {{y+2}} {{z+1}}.5 {{Item:{{id:"minecraft:snowball",count:16}}}}'
               for x in (-2, 0, 2)],
              erwartet={"items": {"minecraft:snow_block": 6}})
