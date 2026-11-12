"""Zuckerrohr-Farm (Profi): 2 × 15 Rohre auf Schlamm über Trichtern, ein Beobachter + Kolben pro Rohr,
gemeinsame Wasserrinne in der Mitte (Quelle in der Mitte, Abfluss-Trichter an beiden Enden).

Koordinaten: x 1..15 = Rohre (Westen → Osten), Doppeltruhe bei x -1/0.
z 0 Staubreihe A, 1 Kolben/Beobachter A (zeigen nach Süden), 2 Rohre A, 3 Wasserrinne,
z 4 Rohre B, 5 Kolben/Beobachter B (zeigen nach Norden), 6 Staubreihe B.
"""
from profi_basis import *

N = 15                                                   # Rohre pro Reihe

f = profi("zuckerrohr", dict(
    name="Zuckerrohr-Farm (Profi)", diff=3, out="Zuckerrohr → Papier, Zucker, Raketen",
    where="Überall; die Wasserrinne zwischen den beiden Schlammreihen versorgt alle Rohre",
    afk="Ja – in der Nähe bleiben (AFK-Platz an der Truhe), der Chunk muss laufen",
    why="Doppelt so viele Reihen und ein Beobachter für JEDES Rohr. Bei der einfachen Farm schaut nur ein "
        "Beobachter auf ein Rohr: Die anderen bleiben bei 3 Blöcken stehen und wachsen nicht weiter, bis gerade "
        "dieses eine Rohr so weit ist. Hier wird jedes Rohr geerntet, sobald es 3 hoch ist – keines wartet. "
        "30 Rohre stehen in zwei Reihen auf Schlamm über Trichtern, dazwischen eine Wasserrinne, die beide Reihen "
        "versorgt. Wird ein Rohr 3 hoch, gibt sein Beobachter einen Impuls nach hinten in den Redstone-Staub, und "
        "die Kolben dieser Reihe schlagen den 2. Block ab. Alles fällt auf den Schlamm (die Trichter saugen "
        "hindurch) oder ins Wasser, das von der Mitte zu den Abfluss-Trichtern an beiden Enden fließt (auch unter "
        "der Quelle sitzt einer). Alles "
        "landet in einer Doppeltruhe – etwa 5-mal so viel wie bei der einfachen Farm.",
    help=[["Ein Kolben feuert nicht",
           "Der Beobachter darauf muss mit dem Gesicht zum Rohr zeigen, der rote Punkt nach hinten zum Staub. "
           "Zeigt das Gesicht nach unten, hast du beim Setzen zu steil geschaut: abbauen und flacher zielen."],
          ["Rohr lässt sich nicht pflanzen",
           "Erst das Wasser in die Mitte der Rinne gießen und warten, bis es an beiden Enden angekommen ist – ohne "
           "Wasser direkt neben dem Schlamm hält kein Zuckerrohr."],
          ["Items bleiben liegen",
           "Unter jedem Rohr muss Schlamm liegen, nicht Erde: Nur durch Schlamm saugen die Trichter. Was ins Wasser "
           "fällt, treibt zu den Trichtern unter den Enden der Rinne – die Quelle muss genau in der Mitte über dem "
           "mittleren Abfluss-Trichter sitzen."],
          ["Truhe voll",
           "Die Doppeltruhe fasst etwa 3400 Zuckerrohr (rund 30 Stunden). Rechtzeitig leeren, sonst stauen sich "
           "die Trichter."]],
    meta=m("≈ 100 Zuckerrohr pro Stunde (Schätzung: 30 Rohre, jedes wächst im Schnitt alle 18 Minuten einen "
           "Block und wird sofort geerntet)",
           [("Überall, wo Schlamm direkt neben Wasser liegt – kein Biom nötig.", W + "Tutorial:Sugar_cane_farming")],
           [("Wiki „Stationary design“: Grundblock, Kolben, Beobachter übereinander; auf Schlamm reichen normale "
             "Trichter statt Trichterloren.", W + "Tutorial:Sugar_cane_farming"),
            ("Zuckerrohr wächst alle 16 Zufallsticks einen Block (im Schnitt alle 18 Minuten), höchstens 3 hoch – "
             "darum ein Beobachter pro Rohr, damit keines oben wartet.", W + "Tutorial:Sugar_cane_farming"),
            ("Beobachter: Das Gesicht zeigt in die Richtung, in die du beim Setzen schaust, der rote Punkt "
             "(Ausgang) zu dir.", W + "Observer"),
            ("Wasser fließt 7 Blöcke weit: Eine Quelle in der Mitte reicht genau für die 15 Blöcke lange Rinne.",
             W + "Water"),
            (TEST + "die einfache Farm (8 Rohre, ein Beobachter) brachte 25 Rohr in 30 min Zeitraffer – mit einem "
                    "Beobachter pro Rohr wartet keines mehr.", None)])))

f.zeichen(M="mud", Z="sugar_cane", K=("piston", "s"), k=("piston", "n"), B=("observer", "s"),
          b=("observer", "n"), T=("chest", "n"))

f.schritt("Ausheben: zwei Gräben 2 tief und 15 lang für Trichter und Schlamm, dazwischen eine Rinne nur 1 tief für "
          "das Wasser – unter ihren beiden Enden und unter ihrer Mitte je ein Loch für einen Abfluss-Trichter. Am Westende des nördlichen "
          "Grabens 2 Plätze mehr für die Doppeltruhe.", {
    -1: """
        -----------------
        ..---------------
        ..---------------
    """,
    -2: """
        -----------------
        ..-......-......-
        ..---------------
    """}, x0=-1, z0=2)
f.schritt("Doppeltruhe ins Westende des nördlichen Grabens (vom Norden her setzen). Unter Reihe A (Norden) "
          "15 Trichter nach Westen: schleichend an die Ostseite der Truhe klicken, jeden weiteren an die Ostseite "
          "des vorigen. Unter die Enden und die Mitte der Rinne je ein Abfluss-Trichter nach Norden (schleichend an die "
          "Südseite des Trichters nördlich davon klicken). Unter Reihe B (Süden) zeigt der westlichste Trichter "
          "nach Norden in den Abfluss-Trichter (an dessen Südseite klicken), die 14 weiteren nach Westen.", {
    -2: """
        TT<<<<<<<<<<<<<<<
        ..^......^......^
        ..^<<<<<<<<<<<<<<
    """}, x0=-1, z0=2)
f.schritt("Schlamm auf die 30 Trichter unter den beiden Reihen (Erde setzen, mit der Wasserflasche zu Schlamm "
          "machen). Die drei Abfluss-Trichter unter der Rinne bleiben offen.", {
    -1: "\n".join(["M" * N, "." * N, "M" * N])}, x0=1, z0=2)
f.schritt("Nördlich von Reihe A und südlich von Reihe B je 15 Blöcke auf den Boden, darauf Kolben, die zum Rohr "
          "zeigen: Stell dich auf den Schlamm davor, schau zum Block und klick oben drauf – der Kolben zeigt zu dir "
          "(nördliche Reihe nach Süden, südliche nach Norden).", {
    0: "\n".join(["#" * N, "." * N, "." * N, "." * N, "#" * N]),
    1: "\n".join(["K" * N, "." * N, "." * N, "." * N, "k" * N])}, x0=1, z0=1)
f.schritt("Hinter jeden Kolben ein Block (an die Rückseite des Kolbens klicken). Dann auf jeden Kolben ein "
          "Beobachter, dessen Gesicht zum Rohr schaut: Stell dich schleichend an die Außenkante der Blockreihe und "
          "ziel flach über den Kolben Richtung Rohr (nicht steil nach unten) – der rote Punkt zeigt dann zu dir.", {
    1: "\n".join(["#" * N] + ["." * N] * 5 + ["#" * N]),
    2: "\n".join(["." * N, "B" * N, "." * N, "." * N, "." * N, "b" * N])}, x0=1, z0=0)
f.schritt("Redstone-Staub auf beide Blockreihen hinter den Beobachtern: rückwärts über die Reihe gehen und den Staub "
          "vor dir legen. Jeder Beobachter gibt seinen Impuls nach hinten in den Staub, der alle Kolben der Reihe "
          "schaltet.", {
    2: "\n".join(["R" * N] + ["." * N] * 5 + ["R" * N])}, x0=1, z0=0)
f.schritt("Wasser: ein Eimer genau in die Mitte der Rinne (8. Platz von Westen). Es fließt 7 Blöcke nach beiden "
          "Seiten, genau bis über die Abfluss-Trichter an den Enden. Der Trichter unter der Quelle holt, was direkt in "
          "sie fällt (dort steht das Wasser still).", {
    -1: "FFFFFFFWFFFFFFF"}, x0=1, z0=3)
f.schritt("Zuckerrohr auf die 30 Schlammblöcke – fertig. Wird ein Rohr 3 hoch, schlagen die Kolben seiner Reihe den "
          "2. Block ab. Zum Warten: AFK-Platz neben der Truhe.", {
    0: "\n".join(["Z" * N, "." * N, "Z" * N])}, x0=1, z0=2)
f.schritt("Hier warten.", {0: "P"}, x0=-1, z0=4)

f.pruefe(boden=GRAS, erwartet={"items": {"minecraft:sugar_cane": 60}})
