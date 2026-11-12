"""Außenposten-Farm mit Seelenlagerfeuern (Profi): Gerüstturm und 2 breites Grubenfeld wie die einfache Farm, aber die
Gruben sind 3 tief und unten brennen Seelenlagerfeuer – Plünderer sterben von selbst, Trichter darunter bringen
Unheilvolle Flaschen und Banner in eine Truhe. Turm 24 statt 28 hoch: größerer Einzugskreis.

Ursprung (0, 0, 0) = Füße auf dem Mittelblock (0, -1, 0) am Fuß des Turms. Feld x -2 … 2, z -2 … 2 ohne Mitte:
Falltüren y -1, Seelenlagerfeuer y -2 (Oberkante -1,5625: bis zum Boden 1,56 Block, Mobs springen 1,25),
Trichter y -3. Ausgang (3, -3, 0) → Truhe (4, -3, 0), darüber frei (4, -2, 0) und Deckel-Falltür (4, -1, 0).
Gerüst (0, 0 … 23, 0), Warteplatz (0, 24, 0): Boden ringsum ≥ 24 entfernt, bis 21 Blöcke Umkreis ≤ 32.
"""
from profi_basis import *

BLOECKE = {"soul_campfire": ("soul_campfire", "minecraft:soul_campfire[lit=true]", "minecraft:soul_campfire",
                             "Seelenlagerfeuer (brennend)")}

f = profi("aussenposten", dict(
    name="Außenposten-Farm mit Seelenlagerfeuern (Profi)", diff=3, out="Unheilvolle Flaschen, Unheilvolle Banner",
    where="Am Plünderer-Außenposten: an Stelle des Turms oder 10–15 Blöcke daneben",
    afk="Ja – oben auf dem Gerüstturm, 24 Blöcke hoch",
    why="Wie bei der einfachen Farm wartest du oben auf einem Turm aus Gerüst: Plünderer sehen durch Gerüst hindurch, "
        "rennen zum Fuß des Turms, treten auf die offenen Falltüren im Grubenfeld (sie halten sie für Boden) und fallen "
        "hinein. Das Feld ist 2 breit, weil sie über eine schmale Grube hinübersteigen. Besser als die einfache Farm: "
        "Die Gruben sind 3 tief, und unten stehen Seelenlagerfeuer. Wer darauf steht, bekommt jede halbe Sekunde 2 "
        "Schaden – ein Plünderer (24 Leben) stirbt nach etwa 6 Sekunden, ganz ohne dich. Herausspringen kann er nicht: "
        "Vom Lagerfeuer bis zum Boden sind es gut 1,5 Blöcke, Mobs springen 1,25. Hauptmänner lassen dabei ihre "
        "Unheilvolle Flasche und ihr Banner fallen; Lagerfeuer verbrennen keine Gegenstände, und die Trichter darunter "
        "saugen sie durch das niedrige Lagerfeuer ein und bringen sie in eine Truhe neben dem Feld. Du musst nie zum "
        "Kämpfen hinunter, und die Gruben laufen nie voll – in der einfachen Farm stehen die Plünderer darin, bis du "
        "kommst. Der Turm ist 24 statt 28 Blöcke hoch: Näher als 24 Blöcke spawnt nichts, weiter als 32 laufen sie "
        "nicht herum – so kommen sie aus bis 21 statt 15 Blöcken Umkreis, fast doppelt so viel Fläche. Seelenlagerfeuer "
        "leuchten nur mit Stärke 10, neben dem Feld bleibt es dunkel genug (Plünderer spawnen bei Blocklicht bis 8); "
        "normale Lagerfeuer (15) hielten sie rund 6 Blöcke vom Feld fern.",
    help=[["Keine Flaschen", "Nur Hauptmänner (Banner auf dem Kopf) lassen eine fallen – etwa jeder 17. Plünderer. "
                             "Flaschen und Banner liegen in der Truhe: Klappe neben dem Feld öffnen, hinunterschauen."],
          ["Plünderer bleiben weg", "Oben auf dem Turm warten: Du musst mehr als 24 und höchstens 32 Blöcke von ihnen "
                                    "weg sein. Fackeln in der Nähe entfernen – bei Blocklicht über 8 spawnen keine "
                                    "Plünderer."],
          ["Plünderer überleben in der Grube", "Alle 24 Seelenlagerfeuer müssen brennen (gelöschte mit dem Feuerzeug "
                                               "anzünden), und in den Gruben darf kein Wasser sein."],
          ["Plünderer in der Truhengrube", "Die Klappe über der Truhe immer schließen – offen halten Plünderer sie für "
                                           "Boden und fallen hinein."]],
    meta=m("Rate: Schätzung – die einfache Farm fing an echten Außenposten 1–14 Plünderer in 30 Minuten. Hier ist die "
           "Fangfläche fast doppelt so groß und die Gruben laufen nie voll: grob 10–40 Plünderer pro Stunde, davon 6 % "
           "Hauptmänner – etwa 1–2 Unheilvolle Flaschen pro Stunde, voll AFK.",
           [("Plünderer spawnen in einem Bereich 72 × 58 × 72 um das oberste Stockwerk des Turms – auch wenn er "
             "abgebaut ist –, auf undurchsichtigen Blöcken bei Blocklicht bis 8; 6 % werden Hauptmann.",
             W + "Pillager_Outpost")],
           [("Ein Hauptmann außerhalb eines Überfalls lässt beim Tod immer eine Unheilvolle Flasche fallen.",
             W + "Ominous_Bottle"),
            ("Flaschenfarm: Plünderer laufen in Fallen, werden automatisch getötet, Trichter bringen die Beute in "
             "Truhen.", W + "Tutorial:Ominous_bottle_farming"),
            ("Seelenlagerfeuer: 2 Schaden jede halbe Sekunde für Mobs darauf, zerstören keine Gegenstände, Licht 10.",
             W + "Soul_Campfire"),
            ("Trichter sammeln auch Gegenstände, die auf niedrigen Blöcken über ihnen liegen.", W + "Hopper"),
            ("Mobs halten offene Falltüren für Boden und laufen darauf.", W + "Trapdoor"),
            ("Auf dem Testserver (26.3) mit der einfachen Farm geprüft: Plünderer sehen durchs Gerüst und rennen zum "
             "Turm, steigen über 1 breite Gruben, laufen weiter als 32 Blöcke vom Spieler nicht herum.", None)])))

f.zeichen(a=("oak_trapdoor", {"half": "bottom", "f": "s", "open": True}),
          b=("oak_trapdoor", {"half": "bottom", "f": "n", "open": True}),
          c=("oak_trapdoor", {"half": "bottom", "f": "e", "open": True}),
          d=("oak_trapdoor", {"half": "bottom", "f": "w", "open": True}),
          T=("oak_trapdoor", {"half": "top"}), X="scaffolding", S="soul_campfire")
feld = "-----\n-----\n--.--\n-----\n-----"
f.schritt("Am Außenposten (an Stelle des abgebauten Turms oder 10–15 Blöcke daneben) um einen Block herum ein "
          "Grubenfeld 5 × 5 ausheben, 3 tief – der Block in der Mitte bleibt bis unten stehen. 2 breit, weil Plünderer "
          "über eine schmale Grube hinübersteigen. Wo Wasser oder eine Höhle angrenzt, zumauern. Hinein und hinaus: "
          "einen Block als Stufe setzen und danach wieder abbauen.", {-1: feld, -2: feld, -3: feld}, x0=-2, z0=-2)
f.schritt("Für die Truhe: östlich des Feldes auf der untersten Ebene einen Gang 2 Blöcke lang, über seinem hinteren Ende "
          "ein Loch bis nach oben. Der Block über dem vorderen Gangstück bleibt stehen – sonst kämen Plünderer von den "
          "Lagerfeuern herunter.", {
    -3: "--", -2: ".-", -1: ".-"}, x0=3)
f.schritt("Truhe ans hintere Gangende (von oben durch das Loch auf den Boden klicken). Dann die Trichter von der Truhe "
          "aus rückwärts. Ein Trichter zeigt in den Block, an den du klickst; immer schleichend klicken, sonst öffnet "
          "sich Truhe oder Trichter. Erst den Trichter im Gang an die Westseite der Truhe, dann den östlichen der "
          "mittleren Reihe an dessen Westseite. In der östlichen Spalte zeigen die zwei nördlichen Trichter nach Süden, "
          "die zwei südlichen nach Norden (an den mittleren bzw. den nächsten klicken). In der mittleren Reihe zeigen "
          "die zwei westlichen nach Norden (an die Südseite des Trichters nördlich davon klicken), alle anderen nach "
          "Osten (an die Westseite des östlichen Nachbarn). An Trichter an der Wand kommst du auch von oben: vom "
          "Grubenrand hineinschauen.", {
    -3: """
        >>>>v
        >>>>v
        ^^.>>>C
        >>>>^
        >>>>^
    """}, x0=-2, z0=-2)
f.schritt("Auf jeden der 24 Trichter im Feld ein Seelenlagerfeuer (schleichend auf die Oberseite klicken) – es brennt "
          "sofort. Seelenlagerfeuer: 3 Stöcke, 3 Stämme und Seelensand oder Seelenerde aus dem Nether. Nimm keine "
          "normalen Lagerfeuer: Ihr Licht (15) verhindert das Spawnen rund um das Feld.", {
    -2: "SSSSS\nSSSSS\nSS.SS\nSSSSS\nSSSSS"}, x0=-2, z0=-2)
f.schritt("4 Falltüren an die Seiten des Mittelblocks klicken (Klappe am Mittelblock), alle öffnen.", {
    -1: ".b.\nd.c\n.a."}, x0=-1, z0=-1)
f.schritt("16 Falltüren an den Rand des Feldes klicken (Klappe am Rand) – schräg von der Seite an die Grubenwand "
          "klicken. Dann alle öffnen. Die 4 inneren Ecken bleiben offen. Plünderer halten die Falltüren für Boden.", {
    -1: "aaaaa\nc...d\nc...d\nc...d\nbbbbb"}, x0=-2, z0=-2)
f.schritt("Deckel über das Loch zur Truhe: eine Falltür an die obere Hälfte einer Lochwand klicken, geschlossen lassen. "
          "Dann liegt sie bündig mit dem Boden. Zum Leeren öffnen, hinunterschauen, Truhe öffnen – danach wieder "
          "schließen.", {
    -1: "T"}, x0=4)
f.schritt("Auf den Mittelblock einen Turm aus Gerüst, 24 hoch – oben wartest du. Durch Gerüst sehen die Plünderer "
          "hindurch (durch Erde oder Glas nicht) und rennen zum Turm.", {
    y: "X" for y in range(0, 24)})
f.schritt("Hier oben warten: 24 Blöcke hoch – näher spawnt nichts, und bis 21 Blöcke um den Turm sind sie höchstens 32 "
          "Blöcke von dir weg und laufen los.", {24: "P"})

# Natürliche Plünderer lassen beim Tod nichts zurück (nur Hauptmänner: Flasche und Banner, 6 %). Darum zusätzlich
# markierte Plünderer: Armbrust (sonst greifen sie nicht an) und ein weißes Banner auf dem Kopf mit Drop-Chance 2 –
# das fällt bei jedem Tod heraus, auch ohne Spieler. Messung: Banner/Flaschen in Trichtern und Truhe; in den Gruben
# darf am Ende fast keiner mehr leben (in der einfachen Farm standen dort 6–14).
MARKE = ('PersistenceRequired:1b,equipment:{mainhand:{id:"minecraft:crossbow",count:1},'
         'head:{id:"minecraft:white_banner",count:1}},drop_chances:{head:2.0f}')
GRUBEN = [-2, -2, -2, 2, -1, 2]
# Echter Außenposten wie bei der einfachen Farm; eigener Suchort, damit nicht derselbe Außenposten wie im Test der
# einfachen Farm gefunden wird. Die markierten Plünderer stehen auf dem eingeebneten Boden um die Farm (±7).
f.pruefe(boden=GRAS, zeit="day", welt="struktur", ursprung=[-8192, 8192],
         bauwerk={"id": "minecraft:pillager_outpost", "anker": [12, 10, 0], "suchen": True, "hoehe": 72,
                  "oberflaeche": True},
         nachher=mobs("pillager", [(-7, 0, -7), (-7, 0, 7), (7, 0, -7), (7, 0, 7)], MARKE),
         bereich=GRUBEN, erwartet={"items": {"minecraft:white_banner|minecraft:ominous_bottle": 3}},
         hoechstens={"wesen": {"minecraft:pillager": 2}})
# Wie aussenposten_mech: großer Boden mit Mauer, 6 Plünderer in 12 Blöcken Abstand
WEIT = ["forceload add {x-18} {z-18} {x+18} {z+18}",
        "fill {x-16} {y-2} {z-16} {x+16} {y-2} {z+16} minecraft:dirt",
        "fill {x-16} {y-1} {z-16} {x+16} {y-1} {z+16} minecraft:grass_block",
        "fill {x-17} {y-1} {z-17} {x+17} {y+1} {z-17} minecraft:stone_bricks",
        "fill {x-17} {y-1} {z+17} {x+17} {y+1} {z+17} minecraft:stone_bricks",
        "fill {x-17} {y-1} {z-17} {x-17} {y+1} {z+17} minecraft:stone_bricks",
        "fill {x+17} {y-1} {z-17} {x+17} {y+1} {z+17} minecraft:stone_bricks"]
f.pruefe_auch("aussenposten_profi_mech", boden=GRAS, zeit="day", vorher=WEIT,
              nachher=mobs("pillager", [(0, 0, -12), (0, 0, 12), (-12, 0, 0), (12, 0, 0), (9, 0, 9), (-9, 0, -9)],
                           MARKE),
              bereich=GRUBEN, erwartet={"items": {"minecraft:white_banner": 4}},
              hoechstens={"wesen": {"minecraft:pillager": 2}})
