"""Lava-Farm (Profi): 16 Kessel in zwei Reihen an einem Gang – ein Durchgang mit einem Stapel Eimer leert alle.

Koordinaten: Gang x 0, z -1..8 (Eingang im Norden bei z -1 = AFK-Platz). Kessel bei x -1 und x 1, z 0..7 (y 0),
direkt darüber spitzer Tropfstein (y 1), Decke y 2 (x -1..1, z -1..8), auf y 3 über jedem Tropfstein eine
Lavaquelle, ringsum und in der Mitte Blöcke (x -2..2), Deckel y 4 (x -1..1). Stützen bei x ±1, z -1 und z 8.
"""
from profi_basis import *

N = 8                                                   # Kessel pro Reihe

f = profi("lava", dict(
    name="Lava-Farm (Profi)", diff=2, out="Lava-Eimer (Brennstoff, 100 Items pro Eimer)",
    where="Überall, auch im Nether; Platz 5 × 10, 5 Blöcke hoch",
    afk="In der Nähe bleiben (Simulationsdistanz) – leeren von Hand: einmal durch den Gang gehen",
    why="Viermal so viele Kessel wie die einfache Farm: 16 Kessel in zwei Reihen links und rechts eines Gangs. "
        "Über jedem Kessel hängt ein spitzer Tropfstein, darüber ein Deckenblock und darauf eine Lavaquelle – die "
        "Tropfsteine tropfen die Lava in die Kessel. Der Tropfstein hängt direkt über dem Kessel (ein Abstand ist "
        "nicht nötig), darum ist die Decke nur 2 hoch und du läufst bequem darunter. Die Lava liegt sicher "
        "zwischen Wänden unter einem Deckel. Weil Eimer sich bis 16 stapeln, gehst du mit einem Stapel Eimer "
        "einmal durch den Gang und leerst alle Kessel. Eine Fackel am Ende hält Monster aus dem Gang.",
    help=[["Ein Kessel füllt sich nicht",
           "Über dem Tropfstein genau ein Block und darauf eine Lava-QUELLE. Der Tropfstein muss mit der Spitze nach "
           "unten unter der Decke hängen, zwischen Spitze und Kessel darf nichts sein. Du musst in der Nähe sein."],
          ["Woher 16 Eimer Lava?",
           "Aus einem Lavasee – oder klein anfangen: erst ein paar Quellen setzen, volle Kessel leeren und mit "
           "dieser Lava die nächsten Plätze füllen."],
          ["Lava läuft aus",
           "Erst die Wand auf Höhe 3 ringsum und die Mittelreihe fertig bauen, dann die Lava einfüllen. Den Deckel "
           "von der Mittelreihe aus nach außen über die Lava legen."],
          ["Monster im Gang", "Die Fackel ganz hinten im Gang stehen lassen – sie macht den ganzen Gang hell."]],
    meta=m("Rate: ≈ 50 Eimer Lava pro Stunde (Schätzung aus der Wiki-Zahl: jeder Kessel füllt sich im Schnitt alle "
           "19 Minuten, 16 × 60/19), wenn du etwa alle 20 Minuten leerst – volle Kessel warten. Die einfache Farm "
           "mit 4 Kesseln: ≈ 13 pro Stunde.",
           [("Überall, auch im Nether – über jedem Tropfstein muss eine Lava-Quelle liegen.",
             W + "Tutorial:Lava_farming")],
           [("Lava-Quelle zwei Blöcke über dem obersten Tropfstein, Kessel darunter: je Zufallstick 15/256 Chance, "
             "dass sich der leere Kessel ganz füllt, im Schnitt nach 19 Minuten.", W + "Tutorial:Lava_farming"),
            ("Zwischen Tropfsteinspitze und Kessel darf kein Block sein, ein Abstand ist aber nicht nötig.",
             W + "Tutorial:Lava_farming"),
            ("Ein Tropfstein füllt nur einen Kessel – mehr Lava gibt es nur mit mehr Tropfsteinen.",
             W + "Pointed_Dripstone"),
            ("Eimer stapeln sich bis 16.", W + "Bucket"),
            (TEST + "einfache Farm (Tropfstein mit Abstand über dem Kessel): 4 Kessel füllten sich.", None)])))

f.zeichen(O="cauldron", T="pointed_dripstone", I="torch")

f.schritt("Vier Stützen, je 2 Blöcke hoch: an den beiden Enden des späteren Gangs links und rechts (der Gang selbst "
          "bleibt frei, er ist 1 breit).", {
    0: "#.#" + "\n..." * N + "\n#.#",
    1: "#.#" + "\n..." * N + "\n#.#"}, x0=-1, z0=-1)
f.schritt("Decke auf Höhe 2: 3 breit und 10 lang – von einer Stütze aus Block an Block legen.", {
    2: "\n".join(["###"] * (N + 2))}, x0=-1, z0=-1)
f.schritt("Unter die Decke links und rechts je 8 spitze Tropfsteine (an die Unterseite der Deckenblöcke klicken, "
          "die Spitze zeigt nach unten). Die Mitte bleibt frei – das ist der Gang.", {
    1: "\n".join(["T.T"] * N)}, x0=-1, z0=0)
f.schritt("Unter jeden Tropfstein einen Kessel auf den Boden – die Spitze berührt den Kessel fast.", {
    0: "\n".join(["O.O"] * N)}, x0=-1, z0=0)
f.schritt("Auf Höhe 3 (auf der Decke) einen Rand 5 breit und 10 lang legen – die beiden Längsseiten ragen einen "
          "Block über die Decke hinaus: an den Enden anfangen und Block an Block setzen. Dazu die Mittelreihe über "
          "dem Gang. Frei bleiben nur die 16 Plätze genau über den Tropfsteinen.", {
    3: "#####\n" + "#.#.#\n" * N + "#####"}, x0=-2, z0=-1)
f.schritt("In jeden der 16 freien Plätze einen Eimer Lava (Quellen). Jede Quelle liegt jetzt zwei Blöcke über ihrem "
          "Tropfstein.", {
    3: "\n".join(["L.L"] * N)}, x0=-1, z0=0)
f.schritt("Deckel auf Höhe 4: zuerst die Mittelreihe auf die Blöcke über dem Gang, dann links und rechts daran je "
          "eine Reihe über die Lava (3 breit, 10 lang). So entsteht kein Feuer und niemand fällt hinein.", {
    4: "\n".join(["###"] * (N + 2))}, x0=-1, z0=-1)
f.schritt("Eine Fackel ganz hinten in den Gang auf den Boden. Leeren: mit einem Stapel Eimer vom Eingang aus durch "
          "den Gang gehen und links und rechts jeden vollen Kessel anklicken.", {
    0: "P" + "\n." * N + "\nI"}, z0=-1)

f.pruefe(boden=GRAS, erwartet={"bloecke": {"minecraft:lava_cauldron": 12}})
