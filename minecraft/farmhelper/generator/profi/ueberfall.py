"""Vollautomatische Totem-Farm (Überfall-Farm, Profi): Der Dorfbewohner schwebt in einer Glaszelle 13 Blöcke über
einem Wasserbecken 12 × 12. Räuber laufen zum Dorfbewohner, landen im Becken, das Wasser schiebt sie in ein Loch
2 × 2, sie fallen 32 Blöcke und sterben beim Aufprall; Verwüster (100 Leben) überleben den Fall und sterben unten
auf 4 Lagerfeuern. Trichter unter den Lagerfeuern sammeln alles in eine Doppeltruhe.

Der Spieler steht in einer Kammer unter der Erde neben dem Becken, höchstens 16 Blöcke unter dem Bett: Dort zählt er
als „im Dorf“ (Abstand ≤ 1 Abschnitt zu einem beanspruchten Bett), Böses Omen wird also sofort zum Überfall-Omen und
der Überfall startet nach 30 Sekunden – ohne dass er zur Farm hinaufgehen muss. Je Überfall: eine Unheilvolle Flasche.

Höhen im Plan (Füße beim Start = 0, Boden = -1):
  16      Glasdach der Zelle; 13 … 15 Glaswände, Bett auf 13 (Kopf Norden); 12 Glasboden – mittig über dem Loch
  -1      Becken: Wasser, 40 Quellen am Rand (x -6 … 5, z -6 … 5 ohne Ecken), strömt zur Mitte
  -2      Beckenboden (Erdreich); Loch x -1 … 0, z -1 … 0 mit 4 Schildern
  -3…-33  Schacht (Luft); -34 vier Lagerfeuer; -35 Trichter; -36 Doppeltruhe (x 0)
  Gang x 1 … 7, z 0, Höhe -36/-35 zur Leiter; Leiterschacht x 8, z 0 von -36 bis -2, oben eine Falltür im Boden
  AFK-Kammer x 8, z 1, Höhe -3/-2 (neben der Leiter, unter der Erde)

Spielcode 26.3 (geprüft): Räuber erscheinen auf festem Boden 30–98 Blöcke um die Überfall-Mitte (das beanspruchte
Bett), nur in Chunks, in denen Wesen laufen; Räuber suchen Dorfbewohner nur ±4 Blöcke in der Höhe (also nie den in
der Zelle), Magier haben 12 Blöcke Reichweite; ein im Überfall getöteter Hauptmann lässt keine Flasche fallen.
Fallschaden = Fallhöhe − 3: 32,5 Blöcke → 29 Schaden (Plünderer, Diener, Magier 24 Leben, Hexe 26).
"""
from profi_basis import *

f = profi("ueberfall", dict(
    name="Totem-Farm vollautomatisch (Profi)", diff=4, out="Totems, Armbrüste, Sättel, Hexen-Beute, Pfeile",
    where="Auf einer großen, offenen und ebenen Fläche weit weg von Dörfern: im Umkreis von 100 Blöcken kein anderes "
          "Bett mit Dorfbewohner, möglichst wenig Wasser, Wald und Schluchten (dort bleiben Räuber hängen)",
    afk="Ja – in der Kammer unter der Erde stehen; je Überfall eine Unheilvolle Flasche trinken",
    why="Du kämpfst nicht: Die Mitte des Überfalls ist das Bett des Dorfbewohners, und seine Glaszelle schwebt 13 "
        "Blöcke genau über einem Wasserbecken 12 × 12. Alle Räuber laufen zum Dorfbewohner und landen im Becken. Das "
        "Wasser strömt von allen Rändern zur Mitte und schiebt sie in das Loch 2 × 2 (auch Verwüster passen "
        "hindurch); 4 Schilder halten das Wasser. Nach 32 Blöcken Fall sterben Plünderer, Diener, Magier und Hexen "
        "beim Aufprall, Verwüster sterben kurz danach auf den Lagerfeuern. Trichter unter den Lagerfeuern bringen "
        "Totems und Beute in eine Doppeltruhe. Du wartest in einer Kammer unter der Erde direkt neben dem Becken: "
        "Dort zählst du schon als „im Dorf“ – Unheilvolle Flasche trinken, stehen bleiben, nach 30 Sekunden "
        "beginnt der Überfall und läuft bis zum Ende allein durch. Die Flaschen liefert die Außenposten-Farm (Profi).",
    help=[["Überfall startet nicht", "Der Dorfbewohner muss das Bett in der Zelle beansprucht haben (grüne "
                                     "Partikel), und du musst in der Kammer stehen (Leiter oben, Höhe -3). Steht "
                                     "irgendwo im Umkreis von 100 Blöcken noch ein Bett mit Dorfbewohner, liegt die "
                                     "Überfall-Mitte zwischen beiden."],
          ["Die nächste Welle kommt nicht", "Eine Welle beginnt erst, wenn alle Räuber der vorigen tot sind "
                                            "(Bossleiste). Einer hängt irgendwo fest – nach einer Weile leuchten "
                                            "die letzten Räuber; hingehen und erledigen. Hilft auf Dauer: die "
                                            "Umgebung ebnen, Wasser und Löcher zuschütten."],
          ["Räuber bleiben am Beckenrand stehen", "Die Zelle muss genau über dem Loch hängen (Bett auf Höhe 13) und "
                                                  "das Becken 12 × 12 groß sein."],
          ["Ein Räuber kommt unten lebend an", "Der Schacht muss bis Höhe -33 frei sein und die Lagerfeuer auf -34 "
                                               "brennen (mit Feuerzeug anzünden, falls aus). Wasser darf nicht in den "
                                               "Schacht laufen – alle 4 Schilder prüfen."],
          ["Leiter-Ausgang", "Die Falltür oben im Boden bleibt zu; Räuber laufen darüber, fallen aber nicht hinein."]],
    meta=m("Rate: ein Überfall auf Normal = 5 Wellen (mit Unheilvoller Flasche II–V eine Bonuswelle) mit 1–2 Magiern, "
           "jeder Magier lässt 1 Totem fallen; auf Schwer 7 Wellen mit bis zu 4 Magiern. Ein Überfall dauert etwa "
           "5–10 Minuten (Laufweg der Räuber). Smaragde gibt es nicht (nur wenn ein Spieler tötet).",
           [("Ein von einem Dorfbewohner beanspruchtes Bett ist schon ein Dorf; die Überfall-Mitte liegt bei den "
             "beanspruchten Betten.", W + "Raid")],
           [("Grundbauweise: Dorfbewohner mit Bett über einem Wassertrichter, Räuber fallen in den Tötungsraum.",
             W + "Tutorial:Raid_farming"),
            ("Magier lassen immer ein Totem der Unsterblichkeit fallen, auch ohne Spieler.", W + "Evoker"),
            ("Räuber erscheinen 30–98 Blöcke um die Mitte auf festem Boden; Räuber suchen Dorfbewohner nur ±4 Blöcke "
             "hoch (Spielcode 26.3).", W + "Raid"),
            ("Verwüster 1,95 breit – passt durch ein Loch 2 × 2.", W + "Ravager"),
            ("Lagerfeuer verletzen Wesen, die darauf stehen; Items verbrennen nicht, Trichter darunter sammeln sie.",
             W + "Campfire"),
            ("Böses Omen wird im Dorf zum Überfall-Omen, der Überfall startet 30 Sekunden später.",
             W + "Raid_Omen")])))

f.zeichen(V="villager", K="campfire", l=("ladder", "w"),
          n=("oak_trapdoor", {"half": "bottom", "f": "s", "open": True}),   # Klappe an der Nordseite
          s=("oak_trapdoor", {"half": "bottom", "f": "n", "open": True}),   # Südseite
          w=("oak_trapdoor", {"half": "bottom", "f": "e", "open": True}),   # Westseite
          o=("oak_trapdoor", {"half": "bottom", "f": "w", "open": True}),   # Ostseite
          T=("oak_trapdoor", {"half": "top", "f": "s"}),
          k=("white_bed", {"part": "head", "f": "n"}), q=("white_bed", {"part": "foot", "f": "n"}))
BECKEN = "\n".join([".XXXXXXXXXXX."] + ["XXXXXXXXXXXXX"] * 11 + [".XXXXXXXXXXX."])   # 13 × 13 ohne Ecken
RAND = "\n".join([".WWWWWWWWWWW."] + ["WFFFFFFFFFFFW"] * 4 + ["WFFFF...FFFFW"] * 3 + ["WFFFFFFFFFFFW"] * 4 +
                 [".WWWWWWWWWWW."])                                  # Mitte 3 × 3: Falltüren, kein Wasser


def treppe(zeichen):
    """Stufe k (0 … 12): x -1, Höhe 12 - k, z 2 + k; darunter je ein Stützblock (Höhe 11 - k), an dessen Seite die
    nächste Stufe hängt. Je Höhe y (0 … 11): Stütze z 13 - y, Stufe z 14 - y; oben (12) nur die Stufe z 2.
    Zeilen mit „.“ davor, damit z stimmt."""
    return {y: ".\n" * (13 - y) + zeichen + "\n" + zeichen if y < 12 else ".\n.\n" + zeichen for y in range(13)}


f.schritt("Weit weg von Dörfern auf ebenem Boden. Zuerst eine Treppe aus Hilfsblöcken für den Dorfbewohner: 13 "
          "Stufen von Süden nach Norden, jede einen Block höher und einen weiter nördlich – die unterste steht auf "
          "dem Boden 14 Blöcke südlich der Mitte, die oberste auf Höhe 12. Unter jeder Stufe außer der untersten ein "
          "Stützblock: Von einer Stufe aus klickst du die Stütze an ihre Nordseite und die nächste Stufe oben darauf.",
          treppe("D"), x0=0)
f.schritt("Von der obersten Stufe aus die Zelle: Glasboden auf Höhe 12 (an die Stufe klicken), darauf das Bett – mit "
          "Blick nach Norden setzen, Kopfende im Norden, Fußende an der Treppe –, Glaswände 3 hoch (auf dem Bett braucht "
          "ein Dorfbewohner 2,5 Blöcke) und das Glasdach. Im Süden, zur Treppe hin, bleibt eine Lücke 1 breit.", {
    12: ".G.\nGGG\nGGG\n.G.",
    13: ".G.\nGkG\nGqG",
    14: ".G.\nG.G\nG.G",
    15: ".G.\nG.G\nG.G",
    16: ".G.\nGGG\nGGG\n.G."}, x0=-1, z0=-2)
f.schritt("Dorfbewohner in die Nähe bringen (Boot oder Lore). Nachts sucht er ein freies Bett, läuft die Treppe hinauf "
          "und beansprucht es (grüne Partikel).", {13: "V"}, x0=0)
f.schritt("Wenn er auf dem Bett ist: die Lücke mit 3 Glas schließen (von der obersten Stufe aus).", {
    y: ".\n.\n.\nG" for y in (13, 14, 15)}, x0=0, z0=-2)
f.schritt("Die Treppe samt Stützblöcken von oben nach unten wieder abbauen – sonst führt sie die Räuber zum "
          "Dorfbewohner.",
          treppe("-"), x0=0)
f.schritt("Neben dem Becken den Einstieg: 9 Blöcke östlich der Mitte einen Leiterschacht 1 × 1 graben, 35 Blöcke tief "
          "(bis Höhe -36). An die Ostwand von unten nach oben Leitern setzen, oben in die Bodenöffnung eine Falltür "
          "(obere Hälfte, geschlossen) – Räuber laufen darüber.", {
    **{y: "-" for y in range(-36, -1)}, -1: "T"}, x0=8, z0=0)
f.schritt("Leitern an die Ostwand des Schachts, von unten (Höhe -36) bis oben (Höhe -2).", {
    y: "l" for y in range(-36, -1)}, x0=8, z0=0)
f.schritt("Die AFK-Kammer: auf Höhe -3 neben der Leiter nach Süden 1 Block breit, 2 hoch ausgraben. Über ihr bleibt "
          "der Erdboden – dort stehst du später versteckt, höchstens 16 Blöcke unter dem Bett.", {
    -3: "-", -2: "-"}, x0=8, z0=1)
f.schritt("Unten am Leiterschacht einen Gang 2 hoch nach Westen graben, 6 Blöcke lang (bis x 2).", {
    -36: "------", -35: "------"}, x0=2, z0=0)
f.schritt("Genau unter der Zelle den Schacht: 3 × 3, von Höhe -2 bis -33 ausheben (32 Blöcke tief). Am sichersten von "
          "unten aus dem Gang nach oben graben, oder von oben mit Wassereimer. 3 breit, damit auch Verwüster "
          "(fast 2 Blöcke breit) zwischen den Falltüren hindurchfallen.", {
    **{y: "---\n---\n---" for y in range(-33, -1)}}, x0=-1, z0=-1)
f.schritt("Unten der Tötungsraum: Doppeltruhe unter die östliche Schachtreihe (Höhe -36, mittig und nördlich). Darauf "
          "Trichter (Höhe -35): östliche Reihe – Norden zeigt nach Süden, Mitte nach unten in die Truhe, Süden nach "
          "Norden; die 6 Trichter westlich davon zeigen nach Osten (schleichend an den Nachbartrichter klicken). Auf die "
          "9 Trichter 9 Lagerfeuer (Höhe -34). Vom Gang aus öffnest du die Truhe.", {
    -36: "..C\n..C",
    -35: ">>v\n>>H\n>>^",
    -34: "KKK\nKKK\nKKK"}, x0=-1, z0=-1)
f.schritt("Becken ausheben: 13 × 13 ohne die 4 Ecken, 1 tief (Höhe -1), mit dem Schacht in der Mitte. Der Boden darunter "
          "(Höhe -2) bleibt, nur das Schachtloch ist offen.", {
    -1: BECKEN.replace("X", "-")}, x0=-6, z0=-6)
f.schritt("Acht offene Falltüren in den Ring des Schachtlochs (Höhe -1, das Mittelfeld bleibt frei): jede steht offen an "
          "der Außenkante ihres Felds, die Ecken im Uhrzeigersinn (Nordwest an Nord, Nordost an Ost, Südost an Süd, "
          "Südwest an West). Sie halten das Wasser – und Räuber halten offene Falltüren für Boden: Sie laufen darauf "
          "zu, weil das Loch direkt unter dem Dorfbewohner liegt, und fallen. Vorsicht, darunter geht es 33 Blöcke tief.", {
    -1: "nno\nw.o\nwss"}, x0=-1, z0=-1)
f.schritt("Wasserquellen in alle 44 Randfelder des Beckens (nicht in die 4 Ecken) – von außen auf den Beckenboden "
          "klicken. Das Wasser strömt von allen Seiten zur Mitte und hält über dem Loch an.", {
    -1: RAND}, x0=-6, z0=-6)
f.schritt("Dein Platz: in der Kammer neben der Leiter (Höhe -3). Hier zählst du schon als „im Dorf“: Unheilvolle "
          "Flasche trinken und stehen bleiben – nach 30 Sekunden beginnt der Überfall, alle Wellen laufen von "
          "allein. Danach die nächste Flasche. Die Beute holst du unten aus der Truhe.", {-3: "P"}, x0=8, z0=1)

# Echter Überfall im Test: Carpet-Testspieler (echter ServerPlayer) mit Bösem Omen in der AFK-Kammer. Testort hoch
# über der Flachwelt (Höhe 100), damit Räuber nur auf der großen Testfläche erscheinen (±96 Blöcke um die Mitte).
WEIT = ["forceload add {x-110} {z-110} {x+110} {z+110}"] + [
    f"fill {{x{a:+d}}} {{y-1}} {{z{b:+d}}} {{x{a + 109:+d}}} {{y-1}} {{z{b + 109:+d}}} minecraft:grass_block keep"
    for a in (-110, 0) for b in (-110, 0)]
f.pruefe(boden=GRAS, zeit="day", hoehe=100, vorher=WEIT, behaelter=[[0, -36, -1]],
         danach=["difficulty normal", "effect give {spieler} minecraft:bad_omen 6000 0"],
         erwartet={"items": {"minecraft:totem_of_undying": 1}, "wesen": {"minecraft:villager": 1}})
