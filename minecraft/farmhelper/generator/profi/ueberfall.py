"""Überfall-Arena mit Fallschacht (Profi): Der Dorfbewohner schwebt in einer Glaszelle 13 Blöcke über einem
Wasserbecken 12 × 12. Räuber laufen zum Dorfbewohner, landen im Becken, das Wasser schiebt sie in ein Loch 2 × 2, sie
fallen 25 Blöcke und kommen mit 2 Leben bei dir an (wie der Schacht der Ertrunkenen-Farm, nur 3 tiefer).

Höhen im Plan (Füße beim Start = 0, Boden = -1):
  16      Glasdach der Zelle; 13 … 15 Glaswände, Bett auf 13 (Kopf Norden); 12 Glasboden – mittig über dem Loch
  -1      Becken: Wasser, 40 Quellen am Rand (x -6 … 5, z -6 … 5 ohne Ecken), strömt zur Mitte
  -2      Beckenboden (Erdreich); Loch x -1 … 0, z -1 … 0 mit 4 Schildern
  -3…-28  Schacht (Luft); -29 Trichter (Landestelle) + Spalt, -30 Trichter + Doppeltruhe; Spieler (2, -29, -1)

Warum 13 Blöcke Höhe: Magier greifen Dorfbewohner nur bis 12 Blöcke an (dann keine Plagegeister gegen ihn), Plünderer
bis 32 Blöcke, auch ohne Sicht. Ein Weg zum Dorfbewohner endet am nächsten erreichbaren Punkt – das ist das Loch
(14 Blöcke unter dem Bett), nicht der Beckenrand (mindestens 14,3 Blöcke, deshalb das Becken 12 × 12).
"""
from profi_basis import *

f = profi("ueberfall", dict(
    name="Überfall-Arena mit Fallschacht (Profi)", diff=4, out="Totems, Smaragde, Sattel, Armbrüste, Hexen-Beute",
    where="Weit weg von Dörfern auf ebenem, festem Boden – im Umkreis von 64 Blöcken kein anderes Bett mit "
          "Dorfbewohner",
    afk="Fast – unten im Tötungsraum stehen und zuschlagen; jeder Räuber kommt mit 2 Leben an",
    why="In der einfachen Arena schießt du vom Turm auf alles, was kommt – die Räuber verteilen sich, Hexen werfen "
        "Tränke, Magier rufen Plagegeister. Hier kommen sie zu dir: Die Mitte des Überfalls ist das Bett des "
        "Dorfbewohners, und seine Glaszelle schwebt 13 Blöcke genau über einem Wasserbecken 12 × 12. Räuber laufen "
        "zum Dorfbewohner (Plünderer wittern ihn bis 32 Blöcke, auch durch Glas) und landen am nächsten "
        "erreichbaren Punkt darunter – im Becken. Das Wasser strömt von allen Rändern zur Mitte und schiebt sie in "
        "das Loch 2 × 2 (auch Verwüster passen hindurch); 4 Schilder halten das Wasser. Nach 25 Blöcken Fall haben "
        "Plünderer, Diener und Magier noch 2 Leben, Hexen 4: Ein Schlag durch den Spalt genügt, und sie sehen dich "
        "nicht – keine Pfeile, keine Tränke. Magier greifen Dorfbewohner nur bis 12 Blöcke an; die Zelle ist 13 "
        "hoch, also rufen sie keine Plagegeister gegen ihn. Die Beute fällt in Trichter und eine Doppeltruhe.",
    help=[["Überfall startet nicht", "Der Dorfbewohner muss das Bett in der Zelle beansprucht haben (grüne "
                                     "Partikel). Unheilvolle Flasche trinken und zur Farm gehen: Erst dort wird "
                                     "aus Böses Omen das Überfall-Omen, nach 30 Sekunden geht es los – in der Zeit "
                                     "über die Treppe nach unten."],
          ["Räuber bleiben am Beckenrand stehen", "Die Zelle muss genau über dem Loch hängen (Bett auf Höhe 13, "
                                                  "14 Blöcke über dem Wasser) und das Becken 12 × 12 groß sein – sonst liegt "
                                                  "ein Punkt am Rand näher am Dorfbewohner als das Loch."],
          ["Die nächste Welle kommt nicht", "Eine Welle beginnt erst, wenn alle Räuber der vorigen tot sind "
                                            "(Bossleiste). Hängt einer irgendwo fest, hingehen und erledigen."],
          ["Verwüster unten", "Er kommt mit etwa 78 Leben an – öfter zuschlagen. Durch den Spalt sieht er dich "
                              "nicht und greift nicht an."]],
    meta=m("Rate: ein Überfall auf Normal mit Unheilvoller Flasche I = 5 Wellen mit 31–43 Räubern, darunter 1 Magier "
           "(1 Totem, fällt immer); Smaragde und Armbrüste nur bei deinem Schlag. In der Farm dauert ein Überfall "
           "etwa 5–8 Minuten statt 15–20 vom Turm (Schätzung) – begrenzt durch deine Unheilvollen Flaschen.",
           [("Ein von einem Dorfbewohner beanspruchtes Bett ist schon ein Dorf; die Überfall-Mitte liegt bei den "
             "beanspruchten Betten.", W + "Raid")],
           [("Grundbauweise: Dorfbewohner mit Bett über einem Wassertrichter, Räuber werden in den Tötungsraum "
             "geschoben und sind nach einem Schlag tot.", W + "Tutorial:Raid_farming#Basic_raid_farm"),
            ("Magier greifen Dorfbewohner bis 12 Blöcke an und rufen Plagegeister.", W + "Evoker"),
            ("Plünderer sehen Gegner bis 32 Blöcke; Dorfbewohner suchen sie auch ohne Sicht (Spielcode 26.3).",
             W + "Pillager"),
            ("Verwüster 1,95 breit – passt durch ein Loch 2 × 2.", W + "Ravager"),
            ("Ein Überfall startet 30 Sekunden, nachdem du mit Böses Omen ins Dorf kommst (Überfall-Omen).",
             W + "Raid_Omen"),
            ("Auf dem Testserver (26.3) geprüft (andere Farmen): Glas versperrt Mobs die Sicht; Schacht mit "
             "Schildern, Trichtern und Spalt wie bei der Ertrunkenen-Farm.", None)])))

f.zeichen(a=("wall_sign", "e"), b=("wall_sign", "w"), H=("hopper", "d"), V="villager",
          k=("white_bed", {"part": "head", "f": "n"}), q=("white_bed", {"part": "foot", "f": "n"}))

BECKEN = "\n".join([".XXXXXXXXXX."] + ["XXXXXXXXXXXX"] * 10 + [".XXXXXXXXXX."])   # 12 × 12 ohne Ecken
RAND = "\n".join([".WWWWWWWWWW."] + ["WFFFFFFFFFFW"] * 10 + [".WWWWWWWWWW."])


def treppe(zeichen):
    """Stufe k (0 … 12): x -1, Höhe 12 - k, z 2 + k; darunter je ein Stützblock (Höhe 11 - k), an dessen Seite die
    nächste Stufe hängt. Je Höhe y (0 … 11): Stütze z 13 - y, Stufe z 14 - y; oben (12) nur die Stufe z 2.
    Zeilen mit „.“ davor, damit z stimmt."""
    return {y: ".\n" * (13 - y) + zeichen + "\n" + zeichen if y < 12 else ".\n.\n" + zeichen for y in range(13)}


f.schritt("Weit weg von Dörfern auf ebenem Boden. Zuerst eine Treppe aus Hilfsblöcken für den Dorfbewohner: 13 "
          "Stufen von Süden nach Norden, jede einen Block höher und einen weiter nördlich – die unterste steht auf "
          "dem Boden 14 Blöcke südlich der Mitte, die oberste auf Höhe 12. Unter jeder Stufe außer der untersten ein "
          "Stützblock: Von einer Stufe aus klickst du die Stütze an ihre Nordseite und die nächste Stufe oben darauf.",
          treppe("D"), x0=-1)
f.schritt("Von der obersten Stufe aus die Zelle: Glasboden auf Höhe 12 (an die Stufe klicken), darauf das Bett – mit "
          "Blick nach Norden setzen, Kopfende im Norden, Fußende an der Treppe –, Glaswände 3 hoch (auf dem Bett braucht "
          "ein Dorfbewohner 2,5 Blöcke) und das Glasdach. Im Süden, zur Treppe hin, bleibt eine Lücke 1 breit.", {
    12: ".G.\nGGG\nGGG\n.G.",
    13: ".G.\nGkG\nGqG",
    14: ".G.\nG.G\nG.G",
    15: ".G.\nG.G\nG.G",
    16: ".G.\nGGG\nGGG\n.G."}, x0=-2, z0=-2)
f.schritt("Dorfbewohner in die Nähe bringen (Boot oder Lore). Nachts sucht er ein freies Bett, läuft die Treppe hinauf "
          "und beansprucht es (grüne Partikel).", {13: "V"}, x0=-1)
f.schritt("Wenn er auf dem Bett ist: die Lücke mit 3 Glas schließen (von der obersten Stufe aus).", {
    y: ".\n.\n.\nG" for y in (13, 14, 15)}, x0=-1, z0=-2)
f.schritt("Die Treppe samt Stützblöcken von oben nach unten wieder abbauen – sonst führt sie die Räuber zum "
          "Dorfbewohner.",
          treppe("-"), x0=-1)
f.schritt("Genau unter der Zelle den Schacht: 2 × 2, 28 Blöcke tief (bis Höhe -28). Daneben eine Treppe hinunter "
          "graben – sie bleibt dein Weg zum Tötungsraum.", {
    **{y: "--\n--" for y in range(-28, 0)}}, x0=-1, z0=-1)
f.schritt("Unten: 4 Trichter unter dem Schacht führen über einen Trichter unter einem Spalt in eine Doppeltruhe "
          "(schleichend an Truhe bzw. nächsten Trichter klicken). Auf der nördlichen Truhe stehst du, eine Ebene tiefer "
          "als die Landestelle; der Block über dem Spalt schützt dich. Über der südlichen Truhe bleibt Luft, sonst geht "
          "die Doppeltruhe nicht auf.", {
    -30: "...>C\n....C",
    -29: ".>>H-\n.^^.-",
    -28: "...--"}, x0=-2, z0=-1)
f.schritt("Becken ausheben: 12 × 12 ohne die 4 Ecken, 1 tief (Höhe -1), mit dem Schacht in der Mitte. Der Boden darunter "
          "(Höhe -2) bleibt, nur das Schachtloch ist offen.", {
    -1: BECKEN.replace("X", "-")}, x0=-6, z0=-6)
f.schritt("Vier Schilder ins Schachtloch (Höhe -2): die zwei westlichen an die Westseite des Lochs, die zwei östlichen an "
          "die Ostseite. Sie halten das Wasser, Räuber fallen hindurch. Vorsicht, darunter geht es 26 Blöcke tief.", {
    -2: "ab\nab"}, x0=-1, z0=-1)
f.schritt("Wasserquellen in alle 40 Randfelder des Beckens (nicht in die 4 Ecken) – von außen auf den Beckenboden "
          "klicken. Das Wasser strömt von allen Seiten zur Mitte und hält über dem Loch an.", {
    -1: RAND}, x0=-6, z0=-6)
f.schritt("Dein Platz: unten auf der nördlichen Truhe. Unheilvolle Flasche trinken, oben zur Farm gehen (Überfall-Omen), "
          "dann innerhalb von 30 Sekunden hinunter. Die Räuber fallen auf die Trichter – durch den Spalt zuschlagen, am "
          "besten mit Schwungkraft (Sweeping Edge); Magier zuerst.", {-29: "P"}, x0=2, z0=-1)

# Kein echter Überfall im Test möglich (Böses Omen braucht einen echten Spieler im Dorf). Geprüft wird, was sich prüfen
# lässt: Plünderer wittern den Dorfbewohner in der Zelle und laufen ins Becken (Haupttest); Diener, Hexe, Magier und
# Verwüster werden vom Wasser ins Loch geschoben und landen unten (Mechanik-Test). Großer Boden mit Mauer drumherum,
# damit niemand vom Testboden fällt (wie beim Außenposten-Test).
WEIT = ["forceload add {x-18} {z-18} {x+18} {z+18}",
        "fill {x-16} {y-2} {z-16} {x+16} {y-2} {z+16} minecraft:dirt",
        "fill {x-16} {y-1} {z-16} {x+16} {y-1} {z+16} minecraft:grass_block",
        "fill {x-17} {y-1} {z-17} {x+17} {y+1} {z-17} minecraft:stone_bricks",
        "fill {x-17} {y-1} {z+17} {x+17} {y+1} {z+17} minecraft:stone_bricks",
        "fill {x-17} {y-1} {z-17} {x-17} {y+1} {z+17} minecraft:stone_bricks",
        "fill {x+17} {y-1} {z-17} {x+17} {y+1} {z+17} minecraft:stone_bricks"]
LANDUNG = [-1, -28, -1, 0, -26, 0]
f.pruefe(boden=GRAS, zeit="day", vorher=WEIT, bereich=LANDUNG,
         nachher=mobs("pillager", [(0, 0, -13), (0, 0, 12), (-13, 0, 0), (12, 0, 0)],
                      'PersistenceRequired:1b,equipment:{mainhand:{id:"minecraft:crossbow",count:1}}'),
         erwartet={"wesen": {"minecraft:pillager": 3}})
f.pruefe_auch("ueberfall_profi_mech", boden=GRAS, zeit="day", vorher=WEIT, bereich=LANDUNG,
              nachher=mobs("vindicator", [(-4, -1, -4), (3, -1, 2)]) + mobs("witch", [(-4, -1, 3)]) +
              mobs("evoker", [(3, -1, -4)]) + mobs("ravager", [(-3, -1, -1)]),
              erwartet={"wesen": {"minecraft:vindicator": 2, "minecraft:witch": 1, "minecraft:evoker": 1,
                                  "minecraft:ravager": 1}})
