"""Gold-Farm an der Bauhöhengrenze (Profi): Plattform 21 × 21 aus Netherrack ganz oben über dem Netherdach, dein
Platz noch 25 Blöcke darüber. Von dort sind alle Höhlen unter dem Netherdach über 128 Blöcke weit weg – das ganze
Monster-Limit gehört der Plattform. Ein Schildkrötenei in der Mitte lockt die Zombifizierten Piglins in zwei Gänge mit
je 2 offenen Falltüren (Lücke 2 breit); sie fallen 26 Blöcke auf eine Reihe aus 5 Trichtern. Untere Stufen auf jedem
4. Feld halten Ghasts fern (sie brauchen 5 × 5 × 4 Blöcke freien Platz).

Höhen (y 0 = Füße beim Start = Höhe 205): Truhe und Trichter y -1 (204), Glasrand y 0, Plattform y 25 (230), Ei,
Stufen und Glaswände y 26/27, Glas 3 × 3 oben y 50 (255 = Bauhöhengrenze), dein Platz P (10, 51, 9) auf Höhe 256.
Mitte (Ei) x 10, z 10. Gerüst-Säule x 10, z 9 (1 Feld nördlich der Mitte) von y -1 bis 50 – das ist die Fortsetzung
deines Gerüst-Turms vom Netherdach. Gänge: Löcher x 8/9 (West) und 11/12 (Ost) in der Reihe z 10.
Trichter (8 … 12, -1, 10): West-Trichter zeigen nach Osten, (11, -1, 10) nach Norden in die Truhe (11, -1, 9),
(12, -1, 10) nach Westen.
"""
from profi_basis import *

N = 21                                   # Plattform 21 × 21 (x/z 0 … 20)
M = 10                                   # Mitte: Ei auf (10, 26, 10)
EBENE = 25                               # Plattform (Füße der Piglins auf 26)
OBEN = 50                                # oberstes Gerüst und Glas 3 × 3 = Höhe 255
SAEULE = (M, M - 1)                      # Gerüst-Säule
LOCH = {(M - 2, M), (M - 1, M), (M + 1, M), (M + 2, M)}
WAND = {(M - 2, M - 1), (M - 1, M - 1), (M + 1, M - 1), (M + 2, M - 1),       # Gänge Nordseite
        (M - 2, M + 1), (M - 1, M + 1), (M + 1, M + 1), (M + 2, M + 1),       # Gänge Südseite
        (M, M - 2), (M, M + 1)}                                                # nördlich der Säule, südlich vom Ei
STUFEN = {(x, z) for x in range(2, N, 4) for z in range(2, N, 4)} - {(M, M)}  # 24 Stück, Reihen/Felder 3, 7, 11 …

PLATTFORM = raster_aus({(x, z): "N" for x in range(N) for z in range(N) if (x, z) not in LOCH | {SAEULE}},
                       0, 0, N - 1, N - 1)
STUFEN_R = raster_aus({p: "U" for p in STUFEN}, 0, 0, N - 1, N - 1)
WAND_R = raster_aus({p: "G" for p in WAND}, M - 2, M - 2, M + 2, M + 1)

f = profi("gold", dict(
    name="Gold-Farm an der Bauhöhengrenze (Profi)", diff=4, out="Goldnuggets, verrottetes Fleisch",
    where="Nether-Ödland über dem Netherdach, ganz oben: Truhe auf Höhe 204, Plattform 21 × 21 auf Höhe 230, dein "
          "Platz auf Höhe 256 direkt an der Bauhöhengrenze (oberster Block 255)",
    afk="Ja – oben auf deiner Gerüst-Säule (Glas 3 × 3 auf Höhe 255), 25 Blöcke über der Plattform",
    why="Die einfache Farm hat eine Plattform 9 × 9 mit einem Loch und brachte im Test 9 Goldnuggets in 30 Minuten. "
        "Drei Dinge machen die Profi-Farm um ein Vielfaches schneller. Erstens steht sie ganz oben an der "
        "Bauhöhengrenze und du wartest über ihr: Monster spawnen nur 24 bis 128 Blöcke um den Spieler. Von deinem "
        "Platz auf Höhe 256 sind alle Höhlen unter dem Netherdach über 128 Blöcke weit weg – dort spawnt nichts mehr, "
        "und das ganze Monster-Limit gehört der Plattform. Bei der einfachen Farm füllen die Höhlen das Limit fast "
        "allein. Zweitens ist die Plattform 21 × 21 groß: rund 400 Spawnfelder statt 80, alle 25 bis 29 Blöcke von "
        "dir entfernt. Drittens können keine Ghasts spawnen: Sie brauchen 5 × 5 Felder und 4 Blöcke Höhe frei, und auf "
        "jedem 4. Feld liegt eine untere Stufe, über die die Piglins einfach steigen. Ohne Stufen spawnten dort auch "
        "Ghasts, die das Limit belegen und auf dich schießen. "
        "So funktioniert es: Zombifizierte Piglins wollen das Schildkrötenei in der Mitte zertrampeln und finden es "
        "bis 23 Blöcke weit – also von der ganzen Plattform aus. Glaswände lassen nur zwei Wege frei, von Westen und "
        "von Osten, je 2 Felder mit offenen Falltüren. Die Wegfindung hält sie für Boden, doch zwischen den beiden "
        "Klappen ist 1⅝ Block Luft – zu breit zum Hinübersteigen (über ein 1 breites Loch wie bei der einfachen Farm "
        "können Mobs hinübersteigen). Die Piglins fallen 26 Blöcke auf eine Reihe aus 5 Trichtern und sterben; die "
        "Trichter bringen Nuggets und Fleisch in die Truhe. Die Reihe ist so lang, weil fallende Piglins noch ein "
        "Stück zur Mitte treiben.",
    help=[["Wenig Piglins", "Dein Platz muss ganz oben sein (Füße auf Höhe 256), sonst spawnen sie wieder in den "
                            "Höhlen unter dem Netherdach. Auf der Plattform muss Nether-Ödland sein (F3 zeigt das "
                            "Biom), und dort darf nichts leuchten: über Lichtstufe 11 spawnen keine Piglins."],
          ["Das Ei ist zertrampelt", "Eine Falltür ist zu oder hängt falsch. Alle 4 müssen offen sein: in den äußeren "
                                     "Löchern mit der Klappe am Plattformrand, in den inneren an der Mitte. Die "
                                     "Glaswände müssen 2 hoch sein. Neues Ei aus dem Gerüst heraus auf die Mitte "
                                     "setzen."],
          ["Andere Mobs stehen herum", "Normale Piglins (etwa jede siebte Gruppe) wollen nicht zum Ei und bleiben auf "
                                       "der Plattform. Sinkt die Rate nach ein, zwei Stunden, stell die Schwierigkeit "
                                       "kurz auf Friedlich – dann verschwinden alle Monster. Selten überlebt ein "
                                       "Anführer-Piglin (40–100 Leben) den Fall und steht bei den Trichtern; er "
                                       "verschwindet von selbst. Mit Goldhelm greifen dich Piglins beim Klettern "
                                       "nicht an."],
          ["Truhe voll", "Bei einigen hundert Piglins pro Stunde ist die Truhe nach etwa 2–4 Stunden voll. Zum Leeren im "
                         "Gerüst so weit hinunter, bis die Truhe östlich vor deinem Gesicht ist."]],
    meta=m("Rate: Schätzung – einige hundert Zombifizierte Piglins pro Stunde, also grob 200–500 Goldnuggets "
           "(20–50 Barren) und ebenso viel verrottetes Fleisch pro Stunde. Die einfache Farm brachte im Test 9 "
           "Nuggets in 30 Minuten. XP und Goldbarren gibt es seit 1.21.5 nur, wenn du selbst tötest.",
           [("Nether-Ödland ganz oben an der Bauhöhengrenze: Dort muss man nichts absichern, weil nur die Plattform "
             "nah genug am Spieler ist (wie die Farm von Nico is LOST / LonelyKat).",
             W + "Tutorial:Zombified_piglin_farming")],
           [("Schildkrötenei als Köder: Zombifizierte Piglins suchen Eier bis 23 Blöcke waagerecht und 3 senkrecht "
             "und laufen hin, auch über offene Falltüren.", W + "Zombified_Piglin#Behavior"),
            ("Mobs spawnen nur 24–128 Blöcke um den Spieler (Kugel); die Spawnhöhe wird zufällig zwischen dem "
             "Weltboden und dem höchsten Block gewählt; im Nether bis Lichtstufe 11.", W + "Mob_spawning"),
            ("Ghasts brauchen zum Spawnen 5 × 5 Felder und 4 Blöcke Höhe freien Platz.", W + "Ghast#Spawning"),
            ("Mobs halten offene Falltüren für geschlossen und laufen darauf.", W + "Trapdoor"),
            ("Fallschaden 1 je Block über 3; Zombifizierte Piglins haben 20 Leben (Anführer mehr).",
             W + "Fall_damage"),
            ("Auf dem Testserver (26.3) mit der einfachen Farm geprüft: Piglins laufen zum Ei, fallen durch die "
             "offene Falltür und sterben; über 1 breite Lochringe steigen Mobs hinüber – darum hier 2 Felder.",
             None)])))

f.zeichen(N="netherrack", Y="scaffolding", E="turtle_egg", U=("slab", {"half": "bottom"}),
          a=("oak_trapdoor", {"half": "bottom", "f": "e", "open": True}),     # Klappe an der Westseite des Lochs
          b=("oak_trapdoor", {"half": "bottom", "f": "w", "open": True}))     # Klappe an der Ostseite des Lochs

# ---------------------------------------------------------------- unten: Truhe, Trichter, Glasrand
f.schritt("Im Nether-Ödland aufs Netherdach und von dort einen Gerüst-Turm hochbauen, bis deine Füße auf Höhe 205 "
          "sind (F3). Dann liegt dein Platz am Ende genau an der Bauhöhengrenze. Das oberste Gerüst unter dir ist "
          "der Fuß der Farm; der Turm bleibt dein Weg hinauf und hinunter.", {
    -1: "Y"}, x0=M, z0=M - 1)
f.schritt("Auf Höhe des obersten Gerüsts (eine Ebene unter deinen Füßen): östlich daneben eine Truhe, westlich zwei "
          "Glasblöcke als Standplatz. Dazu schleichend an den Rand gehen und an die Seite des Gerüsts klicken, wie "
          "beim Brückenbauen.", {
    -1: "GG.C"}, x0=M - 2, z0=M - 1)
f.schritt("Südlich davon eine Reihe aus 5 Trichtern, alle schleichend setzen – ein Trichter zeigt in den Block, an den "
          "du klickst: zuerst den südlich der Truhe (an die Südseite der Truhe klicken, er zeigt nach Norden in die "
          "Truhe), dann westlich davon drei, die nach Osten zeigen (jeweils an die Westseite des vorigen Trichters "
          "klicken), und östlich einen, der nach Westen zeigt (an die Ostseite des ersten). Du kannst dabei auf den "
          "Trichtern stehen.", {
    -1: ">>>^<"}, x0=M - 2, z0=M)
f.schritt("Glas an beide Enden der Trichterreihe und an die Südseite aller 5 Trichter (gleiche Höhe) – "
          "schleichend klicken, sonst öffnet sich der Trichter.", {
    -1: "G.....G\n.GGGGG"}, x0=M - 3, z0=M)
f.schritt("Eine Ebene höher (Höhe deiner Füße) Glas rund um die Trichterreihe: auf die Glasblöcke und auf die Truhe "
          "(schleichend oben auf die Truhe klicken – mit Glas darüber geht sie noch auf), das Feld östlich davon an "
          "die Seite dieses Glases. Über dem Turm bleibt es frei. "
          "So rollt nichts von den Trichtern herunter.", {
    0: ".GG.GG\nG.....G\n.GGGGG"}, x0=M - 3, z0=M - 1)

# ---------------------------------------------------------------- Säule und Plattform
f.schritt("Das Gerüst 26 Blöcke weiter hochbauen (Gerüst auf das Gerüst klicken, dann hochklettern), bis das oberste "
          "Gerüst auf Höhe 230 steht – das ist die Höhe der Plattform.", {
    y: "Y" for y in range(0, EBENE + 1)}, x0=M, z0=M - 1)
f.schritt("Auf Höhe 230 eine Plattform 21 × 21 aus Netherrack (436 Blöcke). Dein Gerüst steht darin 1 Feld nördlich "
          "der Mitte (Feld 11 von Westen, 10 von Norden). In der Mittelreihe bleiben 4 Felder frei: die 2 westlich "
          "und die 2 östlich der Mitte. Die Mitte selbst bekommt Netherrack – darauf kommt das Ei. Vorsicht an den "
          "Löchern (25 Blöcke tief)!", {
    EBENE: PLATTFORM})
f.schritt("Gegen Ghasts: 24 untere Stufen (z. B. Bruchstein) auf die Plattform – in den Reihen 3, 7, 11, 15 und 19 "
          "(von Norden gezählt) jeweils auf die Felder 3, 7, 11, 15 und 19 (von Westen), nur nicht auf die Mitte. "
          "Ghasts brauchen 5 × 5 Felder und 4 Blöcke Höhe frei, die Piglins steigen einfach über die Stufen.", {
    EBENE + 1: STUFEN_R})
f.schritt("In die 4 Löcher je eine Falltür und alle aufklappen. Eine Falltür hängt an dem Block, an den du klickst, "
          "und steht aufgeklappt senkrecht an ihm. In die beiden äußeren Löcher an den Plattformrand klicken "
          "(westliches Loch: Ostseite des Netherracks westlich davon; östliches Loch: Westseite des Netherracks östlich "
          "davon), in die beiden inneren Löcher an die Seiten der Mitte. Am besten von den Feldern nördlich der "
          "Löcher aus, auf die untere Hälfte klicken. Dazwischen bleibt 1⅝ Block Luft – zu breit zum Hinübersteigen.", {
    EBENE: "ab.ab"}, x0=M - 2, z0=M)
f.schritt("Glaswände 2 hoch: an beiden Seiten der Gänge (je 2 Felder nördlich und südlich der Löcher), nördlich vom "
          "Gerüst und südlich der Mitte. Dann führen nur noch die Falltüren zur Mitte. Die Wand südlich der Mitte "
          "zuletzt: Geh dafür vorsichtig auf die Mitte (links und rechts sind die Löcher), setz das Glas südlich davon "
          "(2 hoch) und steig nach Norden in dein Gerüst.", {
    EBENE + 1: WAND_R, EBENE + 2: WAND_R}, x0=M - 2, z0=M - 2)
f.schritt("Aus dem Gerüst heraus das Schildkrötenei (nur mit Behutsamkeit abbaubar) auf die Mitte setzen (oben auf "
          "den Netherrack südlich von dir klicken). Über dem Ei müssen 2 Blöcke frei bleiben, sonst suchen die "
          "Piglins es nicht.", {
    EBENE + 1: "E"}, x0=M, z0=M)

# ---------------------------------------------------------------- oben: dein Platz
f.schritt("Das Gerüst weiter hochbauen bis zur Bauhöhengrenze: Das oberste Gerüst steht auf Höhe 255 (es geht nicht "
          "höher). Oben drumherum 8 Glasblöcke (3 × 3, schleichend an die Seiten des Gerüsts klicken), damit du "
          "sicher stehst.", {
    **{y: "...\n.Y" for y in range(EBENE + 1, OBEN)}, OBEN: "GGG\nGYG\nGGG"}, x0=M - 1, z0=M - 2)
f.schritt("Dein Platz: oben auf dem Gerüst, Füße auf Höhe 256 – 25 Blöcke über der Plattform. Alle Spawnfelder sind "
          "25 bis 29 Blöcke weit weg: näher als 24 spawnt nichts, weiter als 32 laufen Mobs nicht mehr herum. Zum "
          "Leeren der Truhe im Gerüst hinuntersteigen (schleichen).", {
    OBEN + 1: "P"}, x0=M, z0=M - 1)

# Test an der echten Stelle: Ursprung auf Höhe 205, Platz auf 256 – die Höhlen unter dem Netherdach sind dann über
# 128 Blöcke vom Testspieler weg. Der Netherrack unter dem Turmfuß ersetzt den Rest des Gerüst-Turms (sonst fiele das
# Gerüst herunter). Gleiche Messgröße wie bei der einfachen Farm (dort 10 Fleisch und 9 Nuggets in 30 Minuten);
# das Ei muss heil bleiben, Ghasts darf es keine geben.
TURM = ["setblock {x+10} {y-2} {z+9} minecraft:netherrack"]
f.pruefe(dimension="the_nether", hoehe=205, biom="minecraft:nether_wastes", zeit="day", vorher=TURM,
         erwartet={"items": {"minecraft:rotten_flesh": 30, "minecraft:gold_nugget": 20},
                   "bloecke": {"minecraft:turtle_egg": 1}},
         hoechstens={"wesen": {"minecraft:ghast": 0}})
# Viele Piglins auf einmal, auch direkt vor den Gängen: Sie drängeln, fallen alle, keiner erreicht das Ei.
f.pruefe_auch("gold_profi_mech", dimension="the_nether", hoehe=205, biom="minecraft:nether_wastes", zeit="day",
              vorher=TURM,
              nachher=mobs("zombified_piglin", [(0, 26, 0), (20, 26, 0), (0, 26, 20), (20, 26, 20), (6, 26, 9),
                                                (6, 26, 11), (7, 26, 10), (14, 26, 9), (14, 26, 11), (13, 26, 10),
                                                (10, 26, 4), (10, 26, 16)]),
              erwartet={"items": {"minecraft:rotten_flesh|minecraft:gold_nugget": 6},
                        "bloecke": {"minecraft:turtle_egg": 1}})
