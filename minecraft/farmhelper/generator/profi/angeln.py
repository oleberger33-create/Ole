"""AFK-Angelfarm (Profi): Wägeplatte auf geflutetem Zaun, Eisenfalltür vor einem stummen Notenblock, Trichter → Truhe.

Bauweise nach Tutorial:Fish_farming („Simple method“), so angeordnet, dass man GERADEAUS schaut (wie der Testspieler):
Der Spieler steht auf einer Stufe (Augenhöhe 1,12 statt 1,62) und schaut nach Süden.

Plan (x West → Ost, z Nord → Süden, Blickrichtung Süden):
  P (0, 0, 0) auf Stufe (0, -1, 0)      Stufe (0, 0, 1)      Zaun mit Wasser (0, 0, 2) auf Trichter (0, -1, 2) → Truhe
  Grobwägeplatte (0, 1, 2) auf dem Zaun Eisenfalltür (0, 1, 3) nach Osten (Scharnier Westen)   Notenblock (0, 1, 4)

Ablauf (nachgerechnet mit dem 26.3-Code, siehe meta):
- Kein Schwimmer → Platte aus → Falltür zu (liegt unten, Platte y 1,0–1,19): der Blick (y 1,12) trifft die Falltür.
  Eisenfalltüren lassen sich nicht anklicken → der Rechtsklick geht an die Angel → Wurf.
- Der Schwimmer fliegt flach, prallt im 2. Tick an den Zaunpfosten (bis y 1,5 hoch) und hängt dabei schon im
  Bereich der Wägeplatte (y 1,0–1,25 über dem Zaun) → Platte an → Falltür klappt sofort an die Westwand.
  Der nächste Rechtsklick (4 Ticks später) geht durch die offene Falltür auf den Notenblock → nichts passiert.
- Der Schwimmer fällt ins Wasser im Zaun; seine Oberkante (y ≈ 1,14) bleibt in der Platte. Beißt ein Fisch, zieht
  er ihn ≈ 0,25 tiefer → spätestens 10 Ticks danach geht die Platte aus → Falltür zu → Rechtsklick → Fang.
  Der Fang erscheint im Zaun-Block; der Trichter darunter saugt ihn ein (Zaun ist kein ganzer Block).
"""
from profi_basis import *

# Neue Blöcke (reine Literale, siehe bloecke.py)
BLOECKE = {
    "angel_zaun_nass": ("oak_fence", "#minecraft:wooden_fences[waterlogged=true]", "#minecraft:wooden_fences",
                        "Holzzaun mit Wasser (Wassereimer auf den Zaun)"),
    "angel_grobwaegeplatte": ("heavy_weighted_pressure_plate", "minecraft:heavy_weighted_pressure_plate",
                              "minecraft:heavy_weighted_pressure_plate", "Grobwägeplatte"),
    "angel_notenblock": ("note_block", "minecraft:note_block", "minecraft:note_block", "Notenblock"),
}
GERICHTET_NEU = {
    "angel_eisenfalltuer": ("iron_trapdoor", "minecraft:iron_trapdoor", "minecraft:iron_trapdoor", "Eisenfalltür"),
}

f = profi("angeln", dict(
    name="AFK-Angelfarm (Profi)", diff=3,
    out="Fisch (Kabeljau, Lachs, Kugelfisch, Tropenfisch), Trödel (Seerosenblätter, Leder, Schnüre, Knochen …) "
        "und viel Erfahrung – aber keine Schätze",
    where="Überall auf festem, ebenem Boden – du brauchst nur einen Eimer Wasser",
    afk="Ja – auf der Stufe stehen, genau geradeaus schauen und die rechte Maustaste dauerhaft drücken",
    why="Beim einfachen Angel-Teich musst du jeden Biss selbst sehen und die Angel einholen. Hier holt sie die Farm "
        "von selbst ein, du kannst stundenlang AFK angeln, und jeder Fang landet über einen Trichter in einer "
        "Doppeltruhe. Du stehst auf einer Stufe, schaust geradeaus nach Süden und hältst die rechte Maustaste "
        "gedrückt. Vor dir liegt ein Zaun mit Wasser darin und darauf eine Grobwägeplatte. Dahinter kommen eine "
        "Eisenfalltür und ein stummer Notenblock. "
        "Ist die Angel nicht ausgeworfen, ist die Platte aus und die Eisenfalltür liegt zu. Dein Blick trifft dann "
        "ihre Kante. Eine Eisenfalltür lässt sich nicht von Hand öffnen, darum geht der Rechtsklick an die Angel, "
        "und du wirfst aus. Der Schwimmer prallt an den Zaunpfosten, fällt ins Wasser im Zaun und drückt dabei die "
        "Wägeplatte. Wägeplatten spüren jedes Wesen, auch den Schwimmer. Die Platte öffnet die Falltür, und die "
        "klappt an die Wand. Jetzt trifft dein Blick den Notenblock, der jeden weiteren Klick abfängt. "
        "Beißt ein Fisch, zieht er den Schwimmer unter die Platte. Die Platte geht aus, die Falltür klappt zu, und "
        "dein nächster Klick holt den Fang ein. Gleich danach wirfst du wieder aus. Der Fang erscheint im Zaun, der "
        "Trichter darunter saugt ihn sofort ein, und die Erfahrung fliegt zu dir. Mit Reparatur auf der Angel geht "
        "sie darum nie kaputt. "
        "Ehrlich gesagt: Schätze (Bücher, Sättel, Namensschilder) gibt es nur in „offenem Wasser“, also wenn um den "
        "Schwimmer 5 × 5 Wasser und darüber Luft ist. Dort kann ihn aber nichts erkennen. Für Schätze bleibt "
        "deshalb der einfache Angel-Teich, für Fisch und Erfahrung AFK diese Farm.",
    help=[["Die Angel wirft dauernd aus und holt sofort wieder ein (oder wirft gar nicht)",
           "Du musst genau auf der Stufe stehen und genau geradeaus schauen: F3 zeigt hinter „Facing“ die Neigung, "
           "sie soll 0 sein oder ganz leicht nach unten gehen (bis etwa 2°). Dann trifft dein Blick bei geschlossener "
           "Falltür ihre dünne Kante und bei offener den Notenblock. Bei mehr als etwa 1,5° nach oben geht der Blick "
           "über die Falltür hinweg, und die Angel wirft nie aus."],
          ["Der Notenblock „klickt“, aber es wird nie eingeholt",
           "Prüf, ob Wasser im Zaun ist (Wassereimer auf den Zaun) und ob es eine GROBwägeplatte aus Eisen ist. Eine "
           "Steindruckplatte spürt den Schwimmer nicht. Die Falltür muss aus Eisen sein, unten liegen und sich an "
           "die Westwand öffnen."],
          ["Die Angel geht kaputt",
           "Nimm eine Angel mit Reparatur und Haltbarkeit III. Jeder Fang bringt 1–6 Erfahrungspunkte, und die "
           "reparieren sie wieder. Mit Köder III beißt es etwa doppelt so oft."],
          ["Nach ein paar Minuten hört es auf",
           "Das Spiel darf nicht pausieren: Mit F3+P schaltest du die Pause beim Fensterwechsel aus. Die Taste "
           "muss gedrückt bleiben, z. B. mit einem Gewicht auf der Maus. Ist die Doppeltruhe voll (gut 3000 Fische), "
           "fliegt der Fang zu dir ins Inventar und danach auf den Boden. Also rechtzeitig leeren."]],
    meta=m("Rate: etwa 170 Fänge pro Stunde mit einer normalen Angel und etwa 320 mit Köder III, jeder mit "
           "1–6 Erfahrungspunkten (Schätzung aus den Wiki-Wartezeiten: 5–30 s, mit Köder III 0–15 s, dazu 1–4 s, bis "
           "der Fisch anbeißt, und höchstens 1 s, bis die Farm einholt). Etwa 89 % Fisch, 11 % Trödel, keine Schätze. "
           "Beim einfachen Teich angelst du gleich schnell, aber nur, solange du selbst klickst.",
           [("Überall. Die Farm braucht nur den einen Wasserblock im Zaun und freien Himmel über der Wägeplatte "
             "(Glas geht). Unter Dach dauert jeder Biss doppelt so lang.", W + "Fishing")],
           [("AFK-Fischfarm aus Eisenfalltür, Notenblock (mit Block darüber stumm), Grobwägeplatte auf geflutetem "
             "Zaun, Trichter und Truhe: Den Notenblock anklicken und gedrückt halten, beim Biss zieht der Fisch den "
             "Schwimmer unter die Platte, die Falltür schließt sich vor dem Notenblock, die Angel holt ein. Keine "
             "Schätze.", W + "Tutorial:Fish_farming"),
            ("Wartezeit 5–30 s, jede Stufe Köder −5 s. Ohne freien Himmel über dem Schwimmer etwa doppelt so lang. "
             "Schätze nur in offenem Wasser (5 × 4 × 5 um den Schwimmer).", W + "Fishing"),
            ("Wägeplatten spüren alle Wesen und prüfen alle 10 Ticks neu. Auf einem Zaun kann man durch die Platte "
             "hindurchfallen und sie trotzdem drücken.", W + "Pressure_Plate"),
            ("Eisenfalltüren öffnen sich nur durch Redstone, ein Rechtsklick auf sie geht an das Item in der Hand.",
             W + "Trapdoor"),
            ("Ein Notenblock fängt jeden Rechtsklick ab. Ist über ihm kein Luftblock, bleibt er stumm.",
             W + "Note_Block"),
            ("Geometrie für den Blick geradeaus nachgerechnet (Java-Code 26.3, nicht auf dem Testserver): "
             "Augenhöhe auf der Stufe 1,12. Die geschlossene Falltür liegt auf 1,0–1,19, die Platte über dem Zaun "
             "spürt auf 1,0–1,25. Der Schwimmer prallt im 2. Tick an den Zaunpfosten, die Platte öffnet die "
             "Falltür sofort, also vor dem nächsten Klick 4 Ticks später. Einfache Simulation des Schwimmers: Ohne "
             "Biss bleibt seine Oberkante über 1,0, bei einem Biss wird er fast immer rechtzeitig erkannt.", None)])))

f.zeichen(u="slab", T=("chest", "w"), Z="angel_zaun_nass", p="angel_grobwaegeplatte", N="angel_notenblock",
          F=("angel_eisenfalltuer", "e"))

# Raster: Spalten x -1 … 2, Zeilen z -1 … 4
f.schritt("Ausheben (je 1 tief): den Block unter deinem späteren Platz, 2 Blöcke davor (Süden) einen für den "
          "Trichter, östlich neben dem Trichter-Loch einen und nördlich davon noch einen für die Truhe.", {
    -1: """
        ....
        .-..
        ..-.
        .--.
    """}, x0=-1, z0=-1)
f.schritt("Zwei Truhen ins Loch im Osten. Sie werden eine Doppeltruhe und zeigen beide nach Westen: von Westen her "
          "setzen, also nach Osten schauen. Dann den Trichter schleichend an die Westseite der südlichen Truhe "
          "klicken, er zeigt in die Truhe. Ins Loch an deinem Platz eine Stufe (untere Hälfte) – darauf stehst du "
          "später, und deine Augen sind dann genau auf der richtigen Höhe.", {
    -1: """
        ....
        .u..
        ..T.
        .>T.
    """}, x0=-1, z0=-1)
f.schritt("Auf Bodenhöhe: vor deinen Platz eine Stufe (untere Hälfte). Rund um den Trichter: im Westen einen "
          "Block, im Osten ein Glas (unter Glas geht die Truhe noch auf), im Süden zwei Blöcke hintereinander. Dann "
          "schleichend einen Holzzaun auf den Trichter und mit dem Wassereimer füllen. Das Wasser bleibt im Zaun, weil "
          "ringsum alles zu ist (im Norden hält es die Stufe).", {
    0: """
        ....
        ....
        .u..
        #ZG.
        .#..
        .#..
    """}, x0=-1, z0=-1)
f.schritt("Eine Grobwägeplatte (aus Eisen) oben auf den Zaun. Auf den hinteren Block kommt der Notenblock und "
          "darauf ein Block, damit er stumm bleibt.", {
    1: """
        ....
        ....
        ....
        .p..
        ....
        .N..
    """,
    2: """
        ....
        ....
        ....
        ....
        ....
        .#..
    """}, x0=-1, z0=-1)
f.schritt("Wände, Teil 1: im Westen eine Wand 2 hoch von deinem Platz bis neben die Stelle vor dem Notenblock. Unten "
          "kommt je ein Block östlich neben deinen Platz, östlich neben das Loch über der Truhe und beidseits unter "
          "die Stelle vor dem Notenblock.", {
    0: """
        ....
        #.#.
        #..#
        ....
        #.#.
    """,
    1: """
        ....
        #...
        #...
        #...
        #...
    """}, x0=-1, z0=-1)
f.schritt("Eisenfalltür auf die Stelle direkt vor dem Notenblock: Stell dich 2 Blöcke östlich davon auf den Boden, "
          "schau nach Westen und klick oben auf den Block unter dieser Stelle. Die Falltür liegt dann unten und "
          "klappt beim Öffnen an die Westwand. Sie öffnet sich nur, wenn die Wägeplatte gedrückt ist.", {
    1: "F"}, z0=3)
f.schritt("Wände, Teil 2: im Osten auf Augenhöhe eine Reihe von deinem Platz bis neben die Falltür. Dann das Dach, "
          "von Süden her: an die Nordseite des Blocks auf dem Notenblock 3 Glas nach Norden, zuletzt über deinem "
          "Platz einen Block. Über dem Schwimmer muss freier Himmel sein, Glas zählt dazu.", {
    1: """
        ....
        ..#.
        ..#.
        ..#.
        ..#.
    """,
    2: """
        ....
        .#..
        .G..
        .G..
        .G..
    """}, x0=-1, z0=-1)
f.schritt("Hinter deinen Platz (Norden) 2 Blöcke als Rückwand. Zum Hinein- und Hinausgehen baust du sie ab und "
          "setzt sie wieder. Dann stellst du dich auf die Stufe, nimmst die Angel in die Hand (am besten mit "
          "Reparatur, Haltbarkeit III und Köder III) und schaust GENAU geradeaus nach Süden auf die dünne Kante der "
          "geschlossenen Eisenfalltür (F3: Neigung 0). Halt die rechte Maustaste gedrückt, mit F3+P pausiert das "
          "Spiel nicht, wenn du das Fenster wechselst. An die Truhe kommst du von hier: schräg nach links unten (Osten) "
          "schauen und auf ihren weiter entfernten Teil zielen.", {
    0: """
        .#..
        .P..
    """,
    1: """
        .#..
    """}, x0=-1, z0=-1)

# Test: Der Testspieler steht auf der Stufe (Augen 1,12) und schaut geradeaus nach Süden – genau wie gebaut.
# Den Zaun flutet ein Befehl (der Testaufbau setzt Blöcke ohne Wasser; im Spiel: Wassereimer auf den Zaun).
# Angel ohne Verzauberung: 64 Haltbarkeit → höchstens 64 Fänge; erwartet sind ≥ 15 Fische in 30 min.
f.pruefe(boden=GRAS, nachher=["setblock {x} {y} {z+2} minecraft:oak_fence[waterlogged=true]"],
         spieler={"hand": "minecraft:fishing_rod", "aktion": "use continuous"},
         erwartet={"beute": {"minecraft:cod|minecraft:salmon|minecraft:pufferfish|minecraft:tropical_fish": 15}})
