"""Blumen-Farm (Profi): vier hohe Blumen (Sonnenblume, Flieder, Rosenstrauch, Pfingstrose) auf Schlamm über Trichtern,
je ein Werfer mit Knochenmehl davor, ein Beobachter-Takt lässt alle vier dauernd feuern. Knochenmehl kommt aus einer
Eingangstruhe über eine Trichterleitung, die Blumen landen in der Ausgangstruhe.

Koordinaten: Blumen x 0..3, z 0 (Höhe 0/1) auf Schlamm (Höhe -1), Trichter darunter (Höhe -2) nach Osten in die Truhe
(4, -2, 0) mit Glas darüber, Zugangsloch (5, -2..-1, 0). Werfer x 0..3, z 1 (zeigen nach Norden), Staub darauf.
Hinter den Werfern (z 2): Zuführ-Trichter nach Norden, darüber die Verteil-Trichter nach Osten, Eingangstruhe (0, 2, 2).
Takt: Beobachter (-1, 1, 1) schaut nach Westen (Ausgang in den Staub), (-2, 1, 1) schaut nach Osten.
Glaswände 2 hoch: Norden z -1 (x -1..4), Westen (-1, 0), Osten (4, 0).
"""
from profi_basis import *

f = profi("blumen", dict(
    name="Blumen-Farm (Profi)", diff=2, out="Sonnenblumen, Flieder, Rosensträucher, Pfingstrosen → gelber, "
                                           "magenta, roter und rosa Farbstoff",
    where="Überall – je eine Sonnenblume (Sonnenblumenebene), Flieder, Rosenstrauch und Pfingstrose (Wald, "
          "Birkenwald, Dunkler Wald, Blumenwald) brauchst du zum Anfangen",
    afk="Ja – Knochenmehl in die Eingangstruhe, in der Nähe bleiben",
    why="Die einfache Farm ist Rechtsklick-Arbeit an einer Blume. Hier arbeiten vier Werfer für dich: Vor jeder der "
        "vier hohen Blumen steht ein Werfer mit Knochenmehl, ein Takt aus zwei Beobachtern lässt alle vier "
        "mehrmals pro Sekunde feuern. Jedes Knochenmehl wirft eine Kopie der Blume ab (die Blume bleibt stehen) – "
        "1 Knochenmehl = 1 Blume = 2 Farbstoff, in allen vier Farben gleichzeitig. Die Blumen stehen auf Schlamm, "
        "die Trichter darunter saugen die Kopien hindurch in die Ausgangstruhe; Glaswände halten alles auf dem "
        "Schlamm. Das Knochenmehl legst du oben in die Eingangstruhe, Trichter verteilen es auf die Werfer – etwa "
        "so schnell, wie die Trichter unten die Blumen wegbringen, damit nichts liegen bleibt. Gut mit der "
        "Knochenmehl-Farm zu kombinieren.",
    help=[["Werfer feuern nicht",
           "Der Takt braucht zwei Beobachter, die sich anschauen: der östliche mit dem roten Punkt zum Staub. Läuft "
           "er nicht an, den westlichen noch einmal abbauen und setzen. Der Staub muss auf allen vier Werfern liegen."],
          ["Knochenmehl kommt nicht an",
           "Der erste Verteil-Trichter muss direkt unter der Eingangstruhe sitzen, die Zuführ-Trichter zeigen nach "
           "Norden in die Werfer. Dass sie dabei im Takt kurz gesperrt werden, ist normal."],
          ["Blumen bleiben liegen",
           "Unter den Blumen muss Schlamm liegen (nicht Erde) – nur durch Schlamm saugen die Trichter. Was oben auf "
           "einem Werfer landet, sammelst du ab und zu ein."],
          ["Abschalten",
           "Ohne Knochenmehl klicken die Werfer nur. Zum Abschalten einen Beobachter abbauen, zum Anschalten wieder "
           "setzen."]],
    meta=m("Rate: so viel Knochenmehl, so viele Blumen – bis etwa 2 Blumen pro Sekunde (gut 7000 pro Stunde, so "
           "schnell bringt die Trichterleitung das Knochenmehl hin und die Blumen weg; Schätzung nach den "
           "Trichter-Werten im Wiki). Jeder Werfer allein schafft bis zu 5 pro Sekunde.",
           [("Überall; das Biom zählt nur, um die ersten vier hohen Blumen zu finden.",
             W + "Tutorial:Flower_farming")],
           [("Knochenmehl auf eine hohe Blume (Sonnenblume, Flieder, Rosenstrauch, Pfingstrose) lässt eine Kopie "
             "fallen, die Blume bleibt stehen.", W + "Bone_Meal"),
            ("Ein Werfer setzt Knochenmehl auf den Block vor ihm ein; Redstone-Staub auf dem Werfer schaltet ihn.",
             W + "Dispenser"),
            ("Zwei Beobachter, die sich anschauen, geben ununterbrochen Impulse; das Gesicht zeigt beim Setzen in "
             "deine Blickrichtung, der rote Punkt zu dir.", W + "Observer"),
            ("Ein Trichter bewegt 2,5 Gegenstände pro Sekunde und holt aus einem Behälter direkt über ihm.",
             W + "Hopper"),
            ("Hohe Blumen lassen sich auch auf Schlamm pflanzen.", W + "Sunflower"),
            ("Glas über einer Truhe stört nicht – sie lässt sich trotzdem öffnen.", W + "Chest"),
            (TEST + "ein Werfer mit Beobachter-Takt vor einer Sonnenblume verbrauchte 64 Knochenmehl, die Blume "
                    "blieb stehen; Trichter saugen durch Schlamm.", None)])))

f.zeichen(M="mud", Y="tall_flower", Q=("dispenser", "n"), N=("hopper", "n"), O=("observer", "w"),
          o=("observer", "e"))

f.schritt("Ausheben: eine Reihe 4 lang und 2 tief für Schlamm und Trichter, daneben (östlich) 2 tief für die Truhe "
          "und noch einen Platz weiter ein Loch 2 tief – von dort öffnest du später die Truhe.", {
    -1: "------",
    -2: "------"})
f.schritt("Truhe unten an die 5. Stelle, davor 4 Trichter nach Osten (schleichend an die Truhe bzw. den vorigen "
          "Trichter klicken). Auf die Truhe ein Glas – es hält die Blumen fern, und die Truhe lässt sich trotzdem "
          "öffnen (von der Seite aus dem Loch daneben). Schlamm auf die 4 Trichter (Erde setzen, mit der "
          "Wasserflasche zu Schlamm machen).", {
    -2: ">>>>C",
    -1: "MMMMG"})
f.schritt("Takt: westlich neben die Werferreihe zwei Stützblöcke auf den Boden. Auf den östlichen einen Beobachter, "
          "der nach Westen schaut: Stell dich 3 Blöcke östlich davon auf den Boden (wo gleich die Werfer hinkommen), "
          "schau nach Westen und klick oben auf die Stütze – das Gesicht zeigt nach Westen, der rote Punkt zu dir. "
          "Auf die westliche Stütze einen Beobachter, der nach Osten schaut: von Westen her setzen. Sobald der zweite "
          "steht, gibt das Paar ununterbrochen Impulse nach Osten – sie wirken, sobald dort Staub liegt.", {
    0: "##",
    1: "oO"}, x0=-2, z0=1)
f.schritt("4 Werfer südlich neben den Schlamm auf den Boden: Stell dich 3 Blöcke nördlich davon hin, schau nach Süden "
          "und klick oben auf den Boden – nicht steil nach unten schauen. Die Öffnung zeigt dann zu dir (nach "
          "Norden) auf den Schlamm.", {
    0: "QQQQ"}, z0=1)
f.schritt("Auf jeden Schlamm eine hohe Blume, jede Sorte einmal: Sonnenblume, Flieder, Rosenstrauch, Pfingstrose.", {
    0: "YYYY"})
f.schritt("Glaswände 2 hoch: an der Nordseite (6 lang), am West- und am Ostende des Schlamms (auf dem Glas über der "
          "Truhe). Sie halten die Kopien auf dem Schlamm.", {
    0: "GGGGGG\nG....G",
    1: "GGGGGG\nG....G"}, x0=-1, z0=-1)
f.schritt("Redstone-Staub auf die 4 Werfer – jetzt schaltet der Takt sie. Hinter jeden Werfer einen Zuführ-Trichter: "
          "schleichend an die Südseite des Werfers klicken – er zeigt nach Norden hinein. Darüber die Verteil-Trichter: "
          "zuerst schleichend oben auf den östlichsten Zuführ-Trichter einen (er zeigt dann nach unten), dann nach "
          "Westen je einen schleichend an die Westseite des vorigen – sie zeigen nach Osten. Auf den westlichsten "
          "schleichend die Eingangstruhe.", {
    0: "....\nNNNN",
    1: "RRRR\n>>>H",
    2: "....\nC..."}, z0=1)
f.schritt("Knochenmehl in die Eingangstruhe – fertig. Die Blumen holst du aus der Truhe unter dem Glas: von der "
          "Seite, aus dem Loch östlich davon. Hier ist dein Platz.", {0: "P"}, x0=6, z0=1)

f.pruefe(boden=GRAS,
         nachher=["setblock {x} {y} {z} minecraft:sunflower[half=lower]",
                  "setblock {x} {y+1} {z} minecraft:sunflower[half=upper]",
                  "setblock {x+1} {y} {z} minecraft:lilac[half=lower]",
                  "setblock {x+1} {y+1} {z} minecraft:lilac[half=upper]",
                  "setblock {x+2} {y} {z} minecraft:rose_bush[half=lower]",
                  "setblock {x+2} {y+1} {z} minecraft:rose_bush[half=upper]",
                  "setblock {x+3} {y} {z} minecraft:peony[half=lower]",
                  "setblock {x+3} {y+1} {z} minecraft:peony[half=upper]"] +
                 [f"item replace block {{x}} {{y+2}} {{z+2}} container.{i} with minecraft:bone_meal 64"
                  for i in range(4)],
         erwartet={"items": {"minecraft:sunflower|minecraft:lilac|minecraft:rose_bush|minecraft:peony": 200},
                   "bloecke": {"minecraft:sunflower": 2}},              # die Blumen stehen noch
         hoechstens={"items": {"minecraft:bone_meal": 0}})              # alles Knochenmehl verbraucht
