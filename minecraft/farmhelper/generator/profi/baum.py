"""Baum-/Holz-Farm (Profi): zwei Schwarzeichen in einem flachen Wasserbecken, das alle Setzlinge und Äpfel in eine
Truhe treibt; Knochenmehl kommt per Knopf aus einem Werfer.

Koordinaten (x Westen → Osten, z Norden → Süden):
  Becken x -3..12, z -3..4 auf Höhe -1 (1 tief). Pflanzfelder (Erde bleiben stehen) x 0..1 und x 8..9, z 0..1.
  Südlich jedes Pflanzfelds ein Stützblock (0, -1, 2) bzw. (8, -1, 2) mit Werfer darauf (zeigt nach Norden),
  Knopf an der Südseite des Werfers. Wasserquellen in der Nordreihe z -3, das Wasser fließt 7 Blöcke nach Süden bis
  über die Trichterreihe z 4 (Höhe -2). Die Trichter laufen von beiden Seiten zum mittleren Trichter x 4, der nach
  Süden in die Truhe (4, -2, 5) zeigt.
"""
from profi_basis import *

GERICHTET_NEU = {"button_wall": ("stone_button", "#minecraft:buttons", "#minecraft:buttons", "Knopf (an der Wand)")}

X0, X1, Z0, Z1 = -3, 12, -3, 4                           # Becken
FELDER = [(0, 0), (8, 0)]                                 # Nordwest-Ecke der beiden Pflanzfelder
PFLANZ = {(fx + dx, fz + dz) for fx, fz in FELDER for dx in (0, 1) for dz in (0, 1)}
STUETZE = {(fx, fz + 2) for fx, fz in FELDER}             # Stützblock unter dem Werfer
TROCKEN = {(fx + dx, Z1) for fx, fz in FELDER for dx in (0, 1)}   # hinter Stamm + Stütze kommt kein Wasser an

f = profi("baum", dict(
    name="Baum-/Holz-Farm (Profi)", diff=2, out="Schwarzeichenholz, Setzlinge, Äpfel",
    where="Überall auf ebenem Boden; über den beiden Pflanzfeldern mindestens 12 Blöcke Luft",
    afk="Nein – halbautomatisch: Knochenmehl per Knopf, Setzlinge und Äpfel sammeln sich von selbst",
    why="Holz lässt sich in Java nur mit TNT-Duplizierern vollautomatisch ernten – riesig und kompliziert. Die beste "
        "Bauweise mit normalem Aufwand ist darum halbautomatisch, aber ohne Laufarbeit: Zwei Schwarzeichen (je 4 "
        "Setzlinge im Quadrat, dicker 2 × 2-Stamm, im Schnitt 42 Holz) stehen in einem flachen Wasserbecken 16 × 8. "
        "Ein Werfer mit Knochenmehl zeigt auf jedes Pflanzfeld – Knopf drücken, bis der Baum steht. Während du den "
        "einen Baum fällst, zerfallen beim anderen schon die Blätter: Setzlinge und Äpfel fallen ins Becken, das "
        "Wasser treibt alles nach Süden über eine Reihe Trichter, und die bringen es in die Truhe. Bei der einfachen "
        "Farm suchst du die Setzlinge im Gras und verlierst viele – Schwarzeichen werfen aber nur knapp genug "
        "Setzlinge für den nächsten Baum ab. Hier gehen (fast) keine verloren, die Farm trägt sich selbst, und du "
        "arbeitest an zwei Bäumen im Wechsel ohne Wartezeit.",
    help=[["Baum wächst nicht",
           "4 Schwarzeichensetzlinge genau im Quadrat. Über dem nordwestlichen Setzling und einen Block ringsum muss "
           "bis 8 Blöcke hoch alles frei sein, oben 2 Blöcke ringsum (Werfer und Knopf daneben auf Bodenhöhe "
           "stören nicht). Knochenmehl muss im Werfer sein; jeder Druck hat eine Chance von 45 %."],
          ["Setzlinge bleiben liegen",
           "Die ganze Nordreihe des Beckens muss aus Wasserquellen bestehen, sonst reicht das Wasser nicht bis über "
           "die Trichter. Was direkt nördlich am Stamm, auf dem Pflanzfeld oder oben auf dem Werfer landet, treibt "
           "nicht weiter – das sammelst du beim Fällen und Nachpflanzen ein."],
          ["Stamm schnell fällen",
           "Unten die 2 × 2 Blöcke wegschlagen, in das Loch stellen und nach oben fällen; Äste zuletzt. Eine "
           "Effizienz-Axt hilft am meisten. Die Blätter musst du nicht abbauen – sie zerfallen von selbst."],
          ["Knopf drücken tut nichts",
           "Der Werfer muss mit der Öffnung zum Setzling zeigen (nach Norden). Zeigt sie nach oben, hast du beim "
           "Setzen zu steil geschaut: abbauen und flacher zielen."]],
    meta=m("Rate: etwa 30 Bäume ≈ 1200 Holz pro Stunde mit einer Effizienz-Axt, dazu 4–6 Setzlinge und ½ Apfel je "
           "Baum, alle in der Truhe (Schätzung: 42 Holz und rund 6 Setzlinge pro Schwarzeiche laut Wiki, zwei Bäume "
           "in etwa 4 Minuten fällen und nachpflanzen)",
           [("Überall; die Schwarzeiche braucht über dem nordwestlichen Setzling eine 3 × 3-Säule freie Luft "
             "(8 Blöcke), oben 5 × 5 – am Boden darf direkt daneben etwas stehen.", W + "Dark_Oak#Planting")],
           [("Schwarzeiche: 42 Holz und 6 Setzlinge im Schnitt, aber nur jeder fünfte Baum wirft viele Setzlinge ab "
             "– man muss alle einsammeln, damit die Farm sich trägt.", W + "Tutorial:Tree_farming#Tree_comparisons"),
            ("Vollautomatische Holzfarmen gehen in Java nur mit TNT-Duplizierern (sehr groß); halbautomatisch: "
             "Knochenmehl aus Werfern, ernten von Hand.", W + "Tutorial:Tree_farming#Automatic_tree_farms"),
            ("Zerfallende Blätter: 5 % Setzling, 0,5 % Apfel (Eiche, Schwarzeiche), 2 % Stöcke.",
             W + "Leaves"),
            ("Werfer mit Knochenmehl: verbraucht nur etwas, wenn der Block davor darauf reagiert – vor einem "
             "Stamm oder vor Luft bleibt das Knochenmehl im Werfer.", W + "Dispenser"),
            ("Wasser fließt 7 Blöcke weit und schiebt Gegenstände mit; Trichter sammeln, was im Block über ihnen "
             "liegt oder schwimmt.", W + "Hopper"),
            (TEST + "die einfache Farm (4 Setzlinge) wuchs im Zeitraffer zu einer Schwarzeiche.", None)])))

f.zeichen(S="dark_oak_sapling", Q=("dispenser", "n"), K=("button_wall", "s"))

# Schritt 1: Becken ausheben, Pflanzfelder und Stützen bleiben (Erde)
aushub = {}
for x in range(X0, X1 + 1):
    for z in range(Z0, Z1 + 1):
        aushub[(x, z)] = "D" if (x, z) in PFLANZ | STUETZE else "-"
aushub[(4, Z1 + 1)] = "-"                                 # Loch über der Truhe
aushub2 = {(x, Z1): "-" for x in range(X0, X1 + 1)} | {(4, Z1 + 1): "-"}   # Trichterreihe + Truhe
f.schritt("Platz suchen: eben, über den beiden Pflanzfeldern mindestens 12 Blöcke Luft. Ein Becken 16 × 8 und 1 tief "
          "ausheben. Stehen lassen (Erde oder Gras): zwei Pflanzfelder 2 × 2 – ringsum je 3 Reihen Becken, zwischen "
          "den beiden Feldern 6 – und direkt südlich der Südwest-Ecke jedes Felds einen Stützblock. Die Südreihe des "
          "Beckens 1 tiefer ausheben (für die Trichter), südlich ihrer 8. Stelle von Westen ein Loch 2 tief für die "
          "Truhe.", {
    -1: raster_aus(aushub, X0, Z0, X1, Z1 + 1),
    -2: raster_aus(aushub2, X0, Z0, X1, Z1 + 1)}, x0=X0, z0=Z0)
f.schritt("Truhe unten ins Loch südlich der Trichterreihe. Dann den Trichter direkt nördlich davor: schleichend an die "
          "Nordseite der Truhe klicken – er zeigt nach Süden in die Truhe. Westlich davon 7 Trichter nach Osten, "
          "östlich davon 8 nach Westen: schleichend jeweils an die Seite des vorigen Trichters klicken. So laufen "
          "beide Hälften zur Mitte und in die Truhe.", {
    -2: ">>>>>>>v<<<<<<<<\n.......C"}, x0=X0, z0=Z1)
f.schritt("Werfer auf die beiden Stützblöcke: Stell dich in das noch trockene Becken direkt nördlich vor das "
          "Pflanzfeld (3 Blöcke nördlich der Stütze), schau nach Süden über das Feld und klick oben auf die Stütze. "
          "Weil du fast waagerecht schaust, zeigt die Öffnung zu dir nach Norden auf das Pflanzfeld. An die Südseite "
          "jedes Werfers einen Knopf.", {
    0: "Q.......Q\nK.......K"}, x0=0, z0=2)
wasser = {}
for x in range(X0, X1 + 1):
    for z in range(Z0, Z1 + 1):
        if (x, z) in PFLANZ | STUETZE | TROCKEN:
            continue
        wasser[(x, z)] = "W" if z == Z0 else "F"
f.schritt("Wasser in die ganze Nordreihe des Beckens (16 Quellen): am schnellsten in jeden zweiten Platz und ans "
          "Ostende – die Lücken füllen sich von selbst. Das Wasser fließt 7 Blöcke nach Süden bis über die Trichter; "
          "hinter den Stützblöcken bleiben zwei Plätze über den Trichtern trocken, das ist richtig so.", {
    -1: raster_aus(wasser, X0, Z0, X1, Z1)}, x0=X0, z0=Z0)
f.schritt("Je 4 Schwarzeichensetzlinge auf die beiden Pflanzfelder, Knochenmehl in die Werfer. Knopf drücken, bis der "
          "Baum steht (meist 3–6 Mal). Fällen, während der andere Baum wächst: Die Blätter zerfallen von selbst, "
          "Setzlinge und Äpfel treiben über die Trichter in die Truhe. Neue Setzlinge aus der Truhe pflanzen, "
          "wieder drücken – von vorn.", {
    0: "SS......SS\nSS......SS"})

f.pruefe(boden=GRAS,
         nachher=["item replace block {x} {y} {z+2} container.0 with minecraft:bone_meal 64",
                  "item replace block {x+8} {y} {z+2} container.0 with minecraft:bone_meal 64",
                  # statt des Knopfs: Takt aus zwei Beobachtern östlich neben jedem Werfer
                  "setblock {x+1} {y} {z+2} minecraft:observer[facing=east]",
                  "setblock {x+2} {y} {z+2} minecraft:observer[facing=west]",
                  "setblock {x+9} {y} {z+2} minecraft:observer[facing=east]",
                  "setblock {x+10} {y} {z+2} minecraft:observer[facing=west]"],
         erwartet={"bloecke": {"minecraft:dark_oak_log": 30}})           # beide Bäume (je 16 Stamm bis Höhe 3)
# Sammelbecken: Blätter über dem Becken zerfallen lassen, die Setzlinge müssen in der Truhe ankommen
f.pruefe_auch("baum_profi_mech", boden=GRAS,
              nachher=["fill {x} {y} {z} {x+9} {y} {z+1} minecraft:air replace minecraft:dark_oak_sapling",
                       "fill {x-3} {y+6} {z-3} {x+12} {y+8} {z+4} "
                       "minecraft:dark_oak_leaves[persistent=false,distance=7]"],
              erwartet={"items": {"minecraft:dark_oak_sapling": 8}})
