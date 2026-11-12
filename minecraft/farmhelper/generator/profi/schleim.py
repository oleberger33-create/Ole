"""Schleim-Farm (Profi): automatisch statt Erschlagen. Raum wie die einfache Farm (ganzer Schleim-Chunk, 3 hoch), nur
das Eck x 0 … 4, z 0 … 4 bleibt stehen und wird zur Golemzelle: Eisengolem in einer Grube 3 × 3 (x 1 … 3, z 1 … 3) auf
unteren Stufen (Füße auf Höhe -1,5, Augen auf 0,8). Ost- und Südseite haben auf Raumhöhe Schlitze aus unteren Stufen
(offen 0,5 … 1,0): Durch sie sehen die Schleime den Golem, hindurch passt keiner (der kleinste ist 0,52 hoch).

Davor ein Ring Lagerfeuer (x 5, z 0 … 5 und z 5, x 0 … 4) auf Trichtern, außen ein zweiter Ring Trichter bündig im
Boden (x 6, z 0 … 6 und z 6, x 0 … 5). Alle Trichter laufen nach Norden bzw. Osten zur Truhe (7, -1, 0).
Fackel (11, 0, 11), Warteplatz 25 Blöcke über der Raummitte.
"""
from profi_basis import *

RAUM = {(x, z): "-" for x in range(16) for z in range(16) if not (x <= 4 and z <= 4)}
FENSTER = [(1, 4), (2, 4), (3, 4), (4, 1), (4, 2), (4, 3), (4, 4)]
INNEN = [(x, z) for x in range(1, 4) for z in range(1, 4)]
FEUER = [(5, z) for z in range(6)] + [(x, 5) for x in range(5)]          # Lagerfeuer auf Trichtern
AUSSEN = [(6, z) for z in range(7)] + [(x, 6) for x in range(6)]          # Trichter bündig im Boden

f = profi("schleim", dict(
    name="Schleim-Farm mit Eisengolem (Profi)", diff=3, out="Schleimbälle",
    where="Schleim-Chunk unter Höhe 40 (wie die einfache Farm); Höhlen in der Nähe ausleuchten",
    afk="Ja – 25 Blöcke über dem Raum warten (24–32 Blöcke weg)",
    why="Die einfache Farm lässt Schleime nur spawnen – erschlagen musst du sie selbst, und sind 70 Monster da, spawnt "
        "nichts mehr. Hier tötet und sammelt die Farm alles von selbst, also spawnen ständig neue. Der Köder ist ein "
        "Eisengolem: Schleime suchen im Umkreis von 16 Blöcken einen Eisengolem, den sie sehen, und springen geradeaus "
        "auf ihn zu. Der Golem steht im Eck des Chunks in einer Grube 3 × 3 auf Stufen – seine Augen sind so knapp über "
        "dem Raumboden. Ost- und Südseite seiner Zelle haben auf Bodenhöhe Schlitze: unten eine Stufe, darüber der "
        "stehen gebliebene Fels, offen bleibt ein halber Block. Durch den Schlitz sehen ihn die Schleime im ganzen Raum "
        "(Glas ginge nicht – durch Glas sehen Mobs nichts), aber kein Schleim passt hindurch, auch der kleinste "
        "(0,52 hoch) nicht. So kann ihn keiner berühren und verletzen. Vor der Zelle liegt ein Ring Lagerfeuer: Wer "
        "zum Golem will, steht darauf und brennt (1 Schaden pro halbe Sekunde) – große und mittlere zerfallen in "
        "kleinere, kleine sterben sofort und lassen Schleimbälle fallen. Die Trichter unter den Lagerfeuern saugen "
        "sie durch das niedrige Lagerfeuer an; ein zweiter Trichterring außen fängt Bälle, die beim Tod nach außen "
        "springen. Alles läuft in die Truhe. Die Lagerfeuer und eine Fackel machen den Raum hell: Andere Monster "
        "spawnen nicht, Schleime im Schleim-Chunk schon.",
    help=[["Golem nimmt Schaden", "In allen 7 Schlitzen muss eine UNTERE Stufe liegen, der Block über dem Eingang "
                                  "muss wieder gesetzt sein. Durch einen ganzen offenen Block passen kleine Schleime."],
          ["Schleime kommen nicht zum Golem", "Sie müssen seinen Kopf durch die Schlitze sehen: Er steht auf Stufen "
                                              "(nicht auf vollen Blöcken), die Schlitze sind frei, kein Glas. Weiter als "
                                              "16 Blöcke sieht ein Schleim den Golem nicht – sie hüpfen dann zufällig, "
                                              "bis er in Reichweite ist."],
          ["Andere Monster im Raum", "Fackel setzen (Licht überall mindestens 1) und Höhlen im Umkreis von 128 Blöcken "
                                     "ausleuchten – sie füllen sonst das Monster-Limit."],
          ["Bälle liegen neben den Feuern", "Der äußere Trichterring muss bündig im Boden liegen, die Lagerfeuer "
                                            "müssen brennen (gelöscht schadet ein Lagerfeuer nicht)."]],
    meta=m("Rate: etwa 150–250 Schleimbälle pro Stunde (Schätzung: Im Test der einfachen Farm kamen 58 Schleime in 60 "
           "Minuten, die einfach stehen blieben; hier sterben sie laufend, also stoppt das Monster-Limit das Spawnen "
           "nicht. Ein Schleim gibt über seine Teilstücke im Schnitt etwa 4 Bälle: groß 9, mittel 3, klein 1).",
           [("Schleim-Chunk unter Höhe 40, ganzer Chunk 3 hoch ausgehoben; der Chunk-Finder hilft beim Suchen.",
             W + "Tutorial:Slime_farming"),
            ("Im Schleim-Chunk unter Höhe 40 spawnen Schleime bei jedem Licht; sie brauchen über 2 Blöcke Platz.",
             W + "Slime#Slime_chunks")],
           [("Eisengolem als Köder, Lagerfeuer zum Töten, Trichter direkt darunter zum Sammeln.",
             W + "Tutorial:Slime_farming#Killing_trap"),
            ("Schleime suchen einen Spieler oder Eisengolem im Umkreis von 16 Blöcken und springen geradeaus auf ihn zu; "
             "sie verletzen Golems durch Berührung.", W + "Slime#Behavior"),
            ("Schleim-Größen: klein 0,52, mittel 1,04, groß 2,08 Blöcke; Gesundheit 1, 4, 16; große und mittlere "
             "zerfallen in 2–4 kleinere.", W + "Slime"),
            ("Auf einem Lagerfeuer nimmt man alle halbe Sekunde 1 Schaden.", W + "Damage#Campfire"),
            ("Eisengolem: 1,4 breit, 2,7 hoch, steigt 1 Block hoch, nimmt keinen Fallschaden.", W + "Iron_Golem"),
            ("Auf dem Testserver (26.3) geprüft (andere Farmen): Durch Glas sehen Mobs nichts; Trichter saugen durch "
             "nicht ganz hohe Blöcke.", None)])))

f.zeichen(K="cobblestone", U=("slab", {"half": "bottom"}), Y="iron_golem", Q="campfire", T="torch",
          c=("chest", "s"))

f.schritt("Einen Schleim-Chunk finden (Chunkbase oder Schleime unter Höhe 40), Chunk-Grenzen mit F3+G anzeigen und "
          "den Plan mit den Pfeilen im Plan-Menü genau auf den Chunk schieben. Den Chunk 3 Blöcke hoch ausgraben – nur "
          "ein Eck 5 × 5 im Nordwesten bleibt stehen, daraus wird die Golemzelle.", {
    y: raster_aus(RAUM, 0, 0, 15, 15) for y in range(0, 3)})
f.schritt("Am stehen gebliebenen Eck die unterste Lage der Ost- und der Südseite ausgraben (7 Schlitze, siehe Plan), "
          "in der Mitte der Ostseite auch den Block darüber: Das ist der Eingang, 2 hoch.", {
    0: raster_aus({p: "-" for p in FENSTER}, 0, 0, 4, 4),
    1: raster_aus({(4, 2): "-"}, 0, 0, 4, 4)})
f.schritt("Durch den Eingang die Zelle 3 × 3 ausgraben: 4 Lagen, von der Höhe über dem Raumboden bis 2 Blöcke unter "
          "den Raumboden. Die Decke darüber bleibt stehen (sie ist das Dach der Zelle).", {
    y: raster_aus({p: "-" for p in INNEN}, 0, 0, 4, 4) for y in (1, 0, -1, -2)})
f.schritt("In die Grube springen und 9 untere Stufen auf ihren Boden setzen. Zum Herausklettern einen Hilfsblock auf "
          "die Stufe direkt vor dem Eingang setzen, hinauf und durch den Eingang hinaus, den Hilfsblock wieder abbauen.", {
    -2: raster_aus({p: "U" for p in INNEN}, 0, 0, 4, 4)})
f.schritt("Vom Eingang aus den Eisengolem in die Mitte bauen: einen Eisenblock auf die mittlere Stufe; einen an die "
          "Innenseite der Westwand auf Raumbodenhöhe (der westliche Arm); einen Eisenblock auf den ersten; einen an "
          "dessen Ostseite (der östliche Arm); oben drauf einen geschnitzten Kürbis. Der Golem steht dann auf den "
          "Stufen, seine Augen knapp über dem Raumboden. Herauskommen kann er nicht (2 Blöcke hoch).", {
    -1: "Y"}, x0=2, z0=2)
f.schritt("Den Eingang oben wieder zumachen (an die Unterseite des Blocks darüber klicken). Dann in alle 7 Schlitze eine "
          "UNTERE Stufe (oben auf den Block darunter klicken): Offen bleibt ein halber Block – genug zum Sehen, zu eng "
          "für jeden Schleim.", {
    1: raster_aus({(4, 2): "K"}, 0, 0, 4, 4),
    0: raster_aus({p: "U" for p in FENSTER}, 0, 0, 4, 4)})
f.schritt("Vor der Zelle einen Graben 1 tief ausheben: 2 Reihen entlang der Ostseite und 2 entlang der Südseite (siehe "
          "Plan), dazu ein Loch für die Truhe an der Nordwand.", {
    -1: raster_aus({p: "-" for p in FEUER + AUSSEN + [(7, 0)]}, 0, 0, 7, 6)})
TRICHTER = {(7, 0): "c", (6, 0): ">", (5, 0): ">"}
TRICHTER.update({(5, z): "^" for z in range(1, 6)})
TRICHTER.update({(6, z): "^" for z in range(1, 7)})
TRICHTER.update({(x, 5): ">" for x in range(5)})
TRICHTER.update({(x, 6): "^" for x in range(6)})
f.schritt("Truhe ins Loch an der Nordwand, dann die 24 Trichter, immer schleichend an den Block klicken, in den der "
          "Trichter zeigen soll – von der Truhe aus rückwärts: die zwei an der Nordwand an die Truhe bzw. an den "
          "Trichter östlich davon, in den beiden Reihen an der Ostseite jeweils an den Trichter nördlich davon, in der "
          "inneren Reihe an der Südseite an den Trichter östlich davon, in der äußeren Reihe an der Südseite an den "
          "Trichter nördlich davon. Alles fließt zur Truhe.", {
    -1: raster_aus(TRICHTER, 0, 0, 7, 6)})
f.schritt("Auf die 11 Trichter direkt an der Zelle je ein Lagerfeuer (oben auf den Trichter klicken; es brennt von "
          "selbst). Die äußeren Trichter bleiben frei und bündig mit dem Boden.", {
    0: raster_aus({p: "Q" for p in FEUER}, 0, 0, 5, 5)})
f.schritt("Eine Fackel in die Südostecke des Raums: Mit dem Licht der Lagerfeuer ist dann überall Licht 1 oder mehr – "
          "andere Monster spawnen nicht, Schleime schon.", {0: "T"}, x0=11, z0=11)
f.schritt("24–32 Blöcke weg warten, z. B. 25 Blöcke über der Raummitte in einer kleinen Höhle: Näher spawnt nichts, "
          "und der Golem soll das einzige Ziel sein. Die Schleimbälle holst du aus der Truhe.", {25: "P"}, x0=8, z0=8)

# Test wie bei der einfachen Farm: allein liegender Schleim-Chunk der flachen Testwelt (Seed 12345), Raum auf Höhe 37,
# Untergrund gefüllt – aber andere Chunks als der Test der einfachen Farm (43055/43015), damit sich die Läufe nicht
# stören: 43086/42999 und 43043/43031 (beide ohne weiteren Schleim-Chunk in 5 Chunks Umkreis). Gemessen: Schleimbälle in
# Trichtern und Truhe (die einfache Farm zählte lebende Schleime) – und der Golem muss den Lauf überleben.
TESTORT = dict(boden="minecraft:stone", fuellung="minecraft:stone", erde_bis=4, hoehe=37, zeit="day",
               vorher=["fill {x} -60 {z} {x+15} {y-7} {z+15} minecraft:stone"])
f.pruefe(**TESTORT, ursprung=[689376, 687984],
         erwartet={"items": {"minecraft:slime_ball": 4}, "wesen": {"minecraft:iron_golem": 1}})
# Mechanik: Schleime aller Größen (2 groß, 3 mittel, 4 klein) überall im Raum – Golem lockt, Feuer töten, Trichter
# sammeln. Aus diesen allein kämen rund 30 Bälle.
f.pruefe_auch("schleim_profi_mech", **TESTORT, ursprung=[688688, 688496],
              nachher=mobs("slime", [(12, 0, 12), (12, 0, 3)], "PersistenceRequired:1b,Size:3") +
              mobs("slime", [(3, 0, 12), (14, 0, 8), (8, 0, 14)], "PersistenceRequired:1b,Size:1") +
              mobs("slime", [(9, 0, 9), (10, 0, 2), (2, 0, 10), (15, 0, 15)], "PersistenceRequired:1b,Size:0"),
              erwartet={"items": {"minecraft:slime_ball": 10}, "wesen": {"minecraft:iron_golem": 1}})
