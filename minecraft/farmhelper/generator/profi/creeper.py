"""Creeper-Farm (Profi): gleiche Bauweise wie die einfache Farm (dunkler Raum 2 hoch, Falltüren oben → 1,8 Blöcke frei,
2 breite Kanäle in Kreuzform zum Loch in der Mitte, gut 24 Blöcke Fall), aber 18 × 18 statt 8 × 8 – so groß, wie es
geht: Die Kanäle sind genau 8 lang (Quelle + 7 Blöcke Fließwasser), das Wasser endet am Loch, das Loch bleibt ohne
Falltüren trocken; jede Ecke ist höchstens 32 Blöcke vom AFK-Platz entfernt. Teppiche auf jedem dritten Feld verhindern
Spinnen.

Raum x 0 … 17, z 0 … 17, Füße auf Höhe 0, Boden -1. Kanäle x 8/9 bzw. z 8/9 (Wasser auf -2, offene Falltüren auf -1),
Loch (8 … 9, 8 … 9). Schacht bis -26, Trichter auf -27 (nach unten), Truhen auf -28. Plätze unten: Ost x 10 (AFK
(10, -28, 8)), West x 7, Gang Süd z 10, alle auf Höhe -28 … -27.
"""
from profi_basis import *

N = 18                     # Raumgröße
M = N // 2 - 1             # Loch bei M, M+1 (8, 9)

f = profi("creeper", dict(
    name="Creeper-Farm (Profi)", diff=4, out="Schwarzpulver (viel)",
    where="Unter der Erde, weit weg von Höhlen (Raum 18 × 18)",
    afk="Ja – unten am Schacht, 28 Blöcke unter dem Raum",
    why="Gleiches Prinzip wie die einfache Farm, aber 18 × 18 statt 8 × 8: 228 statt 44 Felder, auf denen Creeper "
        "spawnen können – rund 5-mal so viel. Größer geht es nicht: Jeder Kanal ist genau 8 lang, eine Quelle an der "
        "Wand plus 7 Blöcke Fließwasser, das genau am Loch endet. Darum bleibt das Loch auch ohne Falltüren trocken. "
        "Und jede Ecke ist von deinem Platz noch höchstens 32 Blöcke weit weg – weiter weg laufen Monster nicht herum. "
        "Falltüren oben an der Decke lassen 1,8 Blöcke Platz: Creeper (1,7 hoch) passen, Zombies, Skelette und Hexen "
        "(fast 2 hoch) nicht. Teppiche auf jedem dritten Feld verhindern Spinnen (sie brauchen 3 × 3 freie Felder) – "
        "die würden sonst Plätze im Mob-Limit belegen und könnten sich im Schacht festklammern. Die Creeper laufen "
        "auf die offenen Falltüren über den 2 breiten Kanälen (ihre Wegfindung hält sie für Boden), fallen ins "
        "Wasser, werden zum Loch geschoben und fallen gut 24 Blöcke tief: 21 Schaden bei 20 Leben. Vier Trichter "
        "bringen das Schwarzpulver in zwei große Truhen.",
    help=[["Zombies oder Skelette spawnen", "Die Falltüren an der Decke müssen in der OBEREN Hälfte sitzen (an die "
                                            "Unterseite der Decke klicken) – über jedem Feld außer Kanälen und Loch."],
          ["Spinnen im Raum", "Ein Teppich fehlt: Auf jedem dritten Feld in beiden Richtungen liegt einer (siehe "
                              "Plan). Dann gibt es nirgends 3 × 3 freie Felder."],
          ["Wasser läuft in den Schacht", "Die Quellen gehören ganz an die Wand-Enden der Kanäle, genau 8 Blöcke vom "
                                          "Loch. Ist ein Kanal kürzer, fließt das Wasser ins Loch."],
          ["Wenig Creeper", "Höhlen in 128 Blöcken ausleuchten und keine Fackel im Raum lassen. Genau auf deinem "
                            "Platz warten: Von dort sind die Ecken gut 31 Blöcke weit – noch weiter weg stehen die "
                            "Creeper nur herum."]],
    meta=m("Rate (Schätzung): etwa 5-mal so viel wie die einfache Farm – gleiche Bauweise, 228 statt 44 Spawnfelder. "
           "Wie viel absolut, hängt vor allem davon ab, wie viele dunkle Höhlen in 128 Blöcken mitspawnen.",
           [("Unter der Erde, weit weg von Höhlen; alles mindestens 24 Blöcke vom Spieler.",
             W + "Tutorial:Creeper_farming")],
           [("Falltüren oben an einer 2 hohen Decke lassen 1 13/16 Blöcke frei: Creeper ja, Zombies und Skelette "
             "nein. Gegen Spinnen Teppiche mit 2 Feldern Abstand.", W + "Tutorial:Creeper_farming"),
            ("Spinnen brauchen 3 × 1 × 3 freien Platz.", W + "Spider"),
            ("Auf und in Teppich spawnt nichts (Höhe 1/16).", W + "Carpet"),
            ("Monster spawnen 24–128 Blöcke vom Spieler; weiter als 32 Blöcke laufen sie nicht herum.",
             W + "Mob_spawning"),
            ("Creeper: 1,7 hoch, 20 Leben, 0–2 Schwarzpulver. Fallschaden = Fallhöhe − 3: rund 24 Blöcke Fall auf "
             "die Trichter geben 21 Schaden.", W + "Creeper"),
            ("Kanal-Bauweise: dunkler Raum, Kanäle zum Loch in der Mitte, Fallschacht.", W + "Tutorial:Mob_farm"),
            ("Auf dem Testserver (26.3) geprüft (einfache Farm, gleiche Bauweise): Creeper laufen auf die offenen "
             "Falltüren, fallen ins Wasser, werden zum Loch geschoben und sterben im Schacht.", None)])))

f.zeichen(N=("oak_trapdoor", {"half": "bottom", "f": "n", "open": True}),
          S=("oak_trapdoor", {"half": "bottom", "f": "s", "open": True}),
          E=("oak_trapdoor", {"half": "bottom", "f": "e", "open": True}),
          V=("oak_trapdoor", {"half": "bottom", "f": "w", "open": True}),
          T=("oak_trapdoor", {"half": "top"}), K="carpet",
          o=("chest", "e"), w=("chest", "w"))

alle = [(x, z) for x in range(N) for z in range(N)]
kanal = {(x, z) for (x, z) in alle if (x in (M, M + 1) or z in (M, M + 1))
         and not (M <= x <= M + 1 and M <= z <= M + 1)}
quelle = {(x, z) for (x, z) in kanal if x in (0, N - 1) or z in (0, N - 1)}
teppich = {(x, z) for (x, z) in alle if x % 3 == 1 and z % 3 == 1}
assert not teppich & kanal

f.schritt("Unter der Erde einen Raum 18 × 18 und 2 hoch ausgraben – ganz dunkel. Fackeln nur zum Bauen, am Ende "
          "alle weg.", {0: flaeche("-", N, N), 1: flaeche("-", N, N)})
f.schritt("In der Mitte ein Loch 2 × 2, und durch das Loch senkrecht weiter graben: Schacht 2 × 2, zusammen 26 tief "
          "(bis 26 Ebenen unter deine Füße beim Planstart).", {
    y: "--\n--" for y in range(-26, 0)}, x0=M, z0=M)
f.schritt("Unten im Schacht noch 2 tiefer graben (dort kommen Trichter und Truhen hin) und von dort aus, auf "
          "dieser tiefsten Ebene, 2 hoch: östlich und westlich je einen Platz 1 × 2 neben dem Schacht und einen Gang "
          "südlich darum herum. Die Ebene darüber (direkt neben dem Schachtboden) bleibt zu – sonst sehen dich die "
          "Creeper. Vom Ost-Platz eine Treppe zu deinem Zugang graben (Weg frei wählbar, nicht durch den Raum).", {
    -27: "----\n----\n----", -28: "----\n----\n----"}, x0=M - 1, z0=M)
f.schritt("Truhen und Trichter, vom Ost-Platz aus: zwei Truhen unter die östliche Schachthälfte (unten auf den "
          "Boden klicken) – sie werden eine große Truhe. Dann schleichend je einen Trichter oben auf die Truhen (zeigt "
          "nach unten). Vom West-Platz genauso für die westliche Hälfte.", {
    -28: "wo\nwo", -27: "HH\nHH"}, x0=M, z0=M)
f.schritt("Kanäle in Kreuzform 2 tief ausheben: 2 breit, von jeder Wand bis zum Loch – jeder genau 8 lang.", {
    -1: raster_aus({p: "-" for p in kanal}, 0, 0, N - 1, N - 1),
    -2: raster_aus({p: "-" for p in kanal}, 0, 0, N - 1, N - 1)})
f.schritt("Wasserquellen unten in die 8 Kanal-Enden an den Wänden. Das Wasser fließt 7 Blöcke und endet genau am "
          "Loch – es läuft nicht hinein.", {
    -2: raster_aus({p: ("W" if p in quelle else "F") for p in kanal}, 0, 0, N - 1, N - 1)})
deckel = {}
for (x, z) in kanal:
    if (x, z) in quelle:
        deckel[(x, z)] = "#"                 # über den Quellen: dort hinge ein Mob im stehenden Wasser
    elif x == M:
        deckel[(x, z)] = "E"
    elif x == M + 1:
        deckel[(x, z)] = "V"
    elif z == M:
        deckel[(x, z)] = "S"
    else:
        deckel[(x, z)] = "N"
f.schritt("Über die Quellen an den Wänden einen Block, in jedes andere Kanalfeld auf Bodenhöhe eine offene Falltür "
          "mit der Klappe an der Kanalwand: an die Seite des Bodenblocks daneben klicken (nicht an die Kanalmitte) "
          "und aufklappen. Monster halten sie für Boden, laufen drauf und fallen ins Wasser. Das Loch bleibt offen.", {
    -1: raster_aus(deckel, 0, 0, N - 1, N - 1)})
f.schritt("Teppiche auf jedes dritte Feld (in beiden Richtungen, siehe Plan): Dann ist nirgends ein Feld 3 × 3 frei "
          "– Spinnen können nicht spawnen. Creeper laufen einfach darüber.", {
    0: raster_aus({p: "K" for p in teppich}, 0, 0, N - 1, N - 1)})
decke = {p: "T" for p in alle if p not in kanal or p in quelle}
decke = {p: v for p, v in decke.items() if not (M <= p[0] <= M + 1 and M <= p[1] <= M + 1)}
f.schritt("Über den ganzen Spawnboden – auch über die 8 Blöcke an den Kanal-Enden, nur nicht über die offenen "
          "Falltüren und das Loch – Falltüren in die OBERE Hälfte der zweiten Ebene (an die Unterseite der Decke "
          "klicken). Dann bleiben 1,8 Blöcke Platz: Creeper (1,7) passen hinein, Zombies und Skelette (fast 2) "
          "nicht.", {1: raster_aus(decke, 0, 0, N - 1, N - 1)})
f.schritt("Hier unten warten: 28 Blöcke unter dem Raum (mindestens 24, sonst spawnt nichts), die fernste Ecke gut "
          "31 Blöcke weit (höchstens 32). Die Creeper fallen gut 24 Blöcke und sterben auf den Trichtern.", {
    -28: "P"}, x0=M + 2, z0=M)

# Wie die einfache Farm (gleiche Messgröße: Schwarzpulver), aber hoch über der flachen Testwelt: deren Oberfläche liegt
# unter Y 40, dort spawnen in Schleim-Chunks Schleime und füllen das Monster-Limit (mechanik). 100 hoch ist sie mehr als
# 128 Blöcke vom Spieler entfernt – dann spawnt nur in der Farm etwas.
f.pruefe(boden="minecraft:stone", fuellung="minecraft:stone", erde_bis=3, hoehe=100, zeit="day",
         erwartet={"items": {"minecraft:gunpowder": 5}})
# Mechanik: 8 Creeper in Ecken und Mitten der Viertel – sie müssen bis zu 8 Felder zum nächsten Kanal laufen
f.pruefe_auch("creeper_profi_mech", boden="minecraft:stone", fuellung="minecraft:stone", erde_bis=3, hoehe=100,
              zeit="day",
              nachher=mobs("creeper", [(0, 0, 0), (16, 0, 0), (0, 0, 16), (15, 0, 16), (5, 0, 5), (11, 0, 5),
                                       (5, 0, 11), (11, 0, 11)]),
              erwartet={"items": {"minecraft:gunpowder": 3}})
