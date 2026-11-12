"""Bambus-Farm (Profi): 2 × 16 Bambus direkt nebeneinander auf Schlamm über Trichtern, Kolben von beiden Seiten
nach innen, ein Beobachter pro Stängel, zwei Doppeltruhen. Kein Wasser nötig.

Koordinaten: x 1..16 = Bambus (Westen → Osten), Truhen bei x -1/0.
z 0 Staubreihe A, 1 Kolben/Beobachter A (zeigen nach Süden), 2 Bambus A, 3 Bambus B,
z 4 Kolben/Beobachter B (zeigen nach Norden), 5 Staubreihe B.
"""
from profi_basis import *

N = 16                                                   # Stängel pro Reihe

f = profi("bambus", dict(
    name="Bambus-Farm (Profi)", diff=3, out="Bambus → Stöcke, Gerüste, Brennstoff",
    where="Überall mit freiem Himmel über den Stängeln (Licht ≥ 9 an der Spitze)",
    afk="Ja – in der Nähe bleiben (AFK-Platz an den Truhen), der Chunk muss laufen",
    why="Viermal so groß wie die einfache Farm und ohne Wasser: 32 Bambus stehen in zwei Reihen direkt nebeneinander "
        "auf Schlamm, von beiden Seiten zeigen Kolben hinein. Jeder Stängel hat seinen eigenen Beobachter auf Höhe "
        "des 3. Blocks; wächst er so hoch, gibt der Beobachter einen Impuls nach hinten in den Redstone-Staub und "
        "die Kolben seiner Reihe schlagen den 2. Block ab. Bambus wächst gut fünfmal so schnell wie Zuckerrohr – "
        "darum lohnt die Größe. Die Kolben drücken die Stücke zur Mitte, alles fällt auf den Schlamm, die Trichter "
        "darunter saugen hindurch und füllen zwei Doppeltruhen (genug für eine Nacht AFK). Die Wasserrinne der "
        "einfachen Farm braucht es hier nicht: Bambus wächst ohne Wasser.",
    help=[["Bambus wächst nicht",
           "Über der Spitze muss Licht ≥ 9 sein – kein Dach und keine Blätter darüber."],
          ["Ein Kolben feuert nicht",
           "Der Beobachter darauf muss mit dem Gesicht zum Bambus zeigen, der rote Punkt nach hinten zum Staub. "
           "Zeigt das Gesicht nach unten, hast du beim Setzen zu steil geschaut: abbauen und flacher zielen."],
          ["Items liegen auf dem Schlamm",
           "Unter jedem Stängel muss Schlamm liegen (nicht Erde) – nur durch Schlamm saugen die Trichter. Sind die "
           "Truhen voll, stauen sich die Trichter."],
          ["Truhen voll",
           "Zwei Doppeltruhen fassen fast 7000 Bambus – bei ≈ 560 pro Stunde reicht das etwa 12 Stunden. "
           "Rechtzeitig leeren (Bambus ist auch Brennstoff für den Ofen)."]],
    meta=m("≈ 560 Bambus pro Stunde (Schätzung: 32 Stängel, jeder wächst im Schnitt alle 4096 Ticks ≈ 3,4 min "
           "einen Block)",
           [("Überall – nur Licht ≥ 9 über der Spitze nötig, kein Wasser.", W + "Tutorial:Bamboo_farming")],
           [("Wiki: Doppelreihe Bambus auf Schlamm, Kolben von beiden Seiten nach innen, Trichter darunter.",
             W + "Tutorial:Bamboo_farming"),
            ("Bambus wächst bei jedem Zufallstick mit Chance 1/3 – im Schnitt alle 4096 Ticks (204,8 s) einen "
             "Block, Zuckerrohr nur alle 16 Zufallsticks.", W + "Bamboo"),
            ("Beobachter: Das Gesicht zeigt in die Richtung, in die du beim Setzen schaust, der rote Punkt "
             "(Ausgang) zu dir.", W + "Observer"),
            (TEST + "die einfache Farm (8 Stängel, ein Beobachter pro Stängel) brachte 250 Bambus in 30 min "
                    "Zeitraffer, fast nichts daneben – die Profi-Farm nutzt dasselbe Prinzip viermal.", None)])))

f.zeichen(M="mud", Z="bamboo", K=("piston", "s"), k=("piston", "n"), B=("observer", "s"),
          b=("observer", "n"), T=("chest", "n"))

f.schritt("Ausheben: ein Graben 2 breit, 2 tief und 18 lang. Die beiden westlichsten Plätze sind für die Truhen.", {
    -1: "\n".join(["-" * (N + 2)] * 2),
    -2: "\n".join(["-" * (N + 2)] * 2)}, x0=-1, z0=2)
f.schritt("Vier Truhen ins Westende, je zwei nebeneinander zu einer Doppeltruhe: alle vom Norden her setzen (vom "
          "Rand auf den Grabenboden klicken, erst die beiden südlichen, dann die nördlichen) – dann zeigen alle nach "
          "Norden, und vordere und hintere verbinden sich nicht. Dann unter beide Reihen je 16 Trichter nach Westen: schleichend an die Ostseite der Truhe klicken, "
          "jeden weiteren an die Ostseite des vorigen.", {
    -2: "\n".join(["TT" + "<" * N] * 2)}, x0=-1, z0=2)
f.schritt("Schlamm auf alle 32 Trichter (Erde setzen, mit der Wasserflasche zu Schlamm machen).", {
    -1: "\n".join(["M" * N] * 2)}, x0=1, z0=2)
f.schritt("Nördlich und südlich des Grabens je 16 Blöcke auf den Boden, darauf Kolben, die zum Bambus zeigen: "
          "Stell dich auf den Schlamm davor, schau zum Block und klick oben drauf – der Kolben zeigt zu dir "
          "(nördliche Reihe nach Süden, südliche nach Norden).", {
    0: "\n".join(["#" * N, "." * N, "." * N, "#" * N]),
    1: "\n".join(["K" * N, "." * N, "." * N, "k" * N])}, x0=1, z0=1)
f.schritt("Hinter jeden Kolben ein Block (an die Rückseite des Kolbens klicken). Dann auf jeden Kolben ein "
          "Beobachter, dessen Gesicht zum Bambus schaut: Stell dich schleichend an die Außenkante der Blockreihe "
          "und ziel flach über den Kolben Richtung Graben (nicht steil nach unten) – der rote Punkt zeigt dann zu "
          "dir.", {
    1: "\n".join(["#" * N] + ["." * N] * 4 + ["#" * N]),
    2: "\n".join(["." * N, "B" * N, "." * N, "." * N, "b" * N])}, x0=1, z0=0)
f.schritt("Redstone-Staub auf beide Blockreihen hinter den Beobachtern: rückwärts über die Reihe gehen und den Staub "
          "vor dir legen. Jeder Beobachter gibt seinen Impuls nach hinten in den Staub, der alle Kolben der Reihe "
          "schaltet.", {
    2: "\n".join(["R" * N] + ["." * N] * 4 + ["R" * N])}, x0=1, z0=0)
f.schritt("Bambus auf die 32 Schlammblöcke – fertig. Wird ein Stängel 3 hoch, schlagen die Kolben seiner Reihe den "
          "2. Block ab. Zum Warten: AFK-Platz neben den Truhen.", {
    0: "\n".join(["Z" * N] * 2)}, x0=1, z0=2)
f.schritt("Hier warten.", {0: "P"}, x0=-1, z0=5)

f.pruefe(boden=GRAS, erwartet={"items": {"minecraft:bamboo": 500}})
