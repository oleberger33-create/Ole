"""Allgemeine Monster-Farm (Profi): zwei Räume 18 × 18 im kompakten Kanal-Design übereinander, ein gemeinsamer
Schacht, der Warteplatz so berechnet, dass beide Räume 24–32 Blöcke entfernt sind.

Höhen (y 0 = Füße im oberen Raum): oberer Raum y 0/1, seine Kanäle y -1 (Falltüren) und -2 (Wasser), Boden der Kanäle
y -3 = Decke des unteren Raums. Unterer Raum y -5/-4, Kanäle y -6/-7. Schacht x 8 … 9, z 8 … 9 bis y -38 (hier landen
die Mobs), Trichter y -39 → Truhe (9, -39, 10) mit Glas darüber (9, -38, 10).
Warteplatz P (10, -29, 10) schräg neben dem Schacht: 24 Blöcke unter dem unteren, 29 unter dem oberen Raum.
Kleiner Leiterschacht (10, -39 … -28, 11) zur Truhe, Gang y -29 von x 11 bis 18 (z 10) zum großen Leiterschacht
(19, -29 … 1, 10) mit Tür-Öffnungen (18, 0/1, 10) und (18, -5/-4, 10), die am Ende wieder zugemacht werden.
"""
from profi_basis import *

N = 18                      # Raum 18 × 18: Kanal = Quelle + 7 fließende Felder bis genau an das Loch
MITTE = N // 2 - 1          # Loch bei x/z 8 und 9
OBEN, UNTEN = 0, -5         # Füße der Monster im oberen / unteren Raum
LANDUNG = -38               # Füße der Mobs unten im Schacht; Trichter eine Ebene tiefer

KREUZ = {(x, z) for x in range(N) for z in range(N) if x in (MITTE, MITTE + 1) or z in (MITTE, MITTE + 1)}
LOCH = {(x, z) for x in (MITTE, MITTE + 1) for z in (MITTE, MITTE + 1)}
KANAL = KREUZ - LOCH
QUELLEN = {(x, z) for (x, z) in KANAL if x in (0, N - 1) or z in (0, N - 1)}


def deckel(x, z):
    """Über der Quelle ein Block, sonst offene Falltür, deren Klappe an der Außenwand ihrer Kanal-Spur steht."""
    if (x, z) in QUELLEN:
        return "#"
    if x == MITTE:
        return "E"                                  # Spur West im Nord-/Südkanal: Klappe an der Westwand
    if x == MITTE + 1:
        return "V"                                  # Spur Ost: Klappe an der Ostwand
    return "S" if z == MITTE else "N"               # West-/Ostkanal: Klappe an der Nord- bzw. Südwand


GRABEN_RAUM = flaeche("-", N, N)
# unterer Raum mit Tür-Öffnung (18, 10) zum Leiterschacht
GRABEN_UNTEN = raster_aus({(x, z): "-" for x in range(N) for z in range(N)} | {(N, 10): "-"}, 0, 0, N, N - 1)
GRABEN_KREUZ = raster_aus({p: "-" for p in KREUZ}, 0, 0, N - 1, N - 1)
WASSER = raster_aus({p: ("W" if p in QUELLEN else "F") for p in KANAL}, 0, 0, N - 1, N - 1)
DECKEL = raster_aus({p: deckel(*p) for p in KANAL}, 0, 0, N - 1, N - 1)

f = profi("mobfarm", dict(
    name="Monster-Farm mit zwei Etagen (Profi)", diff=4,
    out="Knochen, Pfeile, Fäden, Schwarzpulver, Verrottetes Fleisch; dazu Hexen-Beute (Redstone, Glowstonestaub, "
        "Zucker, Glasflaschen, Stöcke)",
    where="Tief unter der Erde, weit weg von Höhlen (oder alle Höhlen in 128 Blöcken ausleuchten). Platz: zwei Räume "
          "18 × 18 übereinander, daneben ein Leiterschacht, vom oberen Raum aus 40 Blöcke in die Tiefe.",
    afk="Ja – auf deinem Platz unten schräg neben dem Schacht: 24 Blöcke unter dem unteren und 29 unter dem "
        "oberen Raum",
    why="Die einfache Farm hat einen Raum 10 × 10 mit 72 Feldern, auf denen Monster spawnen können. Hier liegen zwei "
        "Räume 18 × 18 übereinander über einem gemeinsamen Schacht – mit je 264 Spawnfeldern über 7-mal so viel "
        "Fläche. Sonst gilt, was sich in der einfachen Farm bewährt hat: Monster spawnen nur im Dunkeln und nie im "
        "Wasser; die offenen Falltüren über den Kanälen hält ihre Wegfindung für Boden, sie fallen ins Wasser, und das "
        "schiebt sie zum Loch in der Mitte. Jeder Kanal ist genau 8 Blöcke lang – so weit fließt Wasser von der "
        "Quelle. Darum endet es von selbst am Rand des Lochs, das Loch bleibt trocken, und Falltüren im Loch braucht "
        "es nicht (kompaktes Kanal-Design aus dem Wiki). Der Schacht führt durch die Mitte des unteren Raums bis 38 "
        "Blöcke unter den oberen: Aus dem unteren Raum fallen die Monster 31 Blöcke, aus dem oberen 36. Das tötet "
        "Zombies, Skelette, Creeper, Spinnen und auch Hexen (26 Leben), die den Fall in der einfachen Farm überleben. "
        "Trichter sammeln die Beute in eine Truhe. Dein Platz ist genau berechnet: Näher als 24 Blöcke am Spieler "
        "spawnt nichts, weiter als 32 Blöcke weg laufen Monster nicht mehr herum. 24 Blöcke unter dem unteren und 29 "
        "unter dem oberen Raum liegen beide Räume in diesem Bereich (nur die äußerste Nordwest-Ecke oben ist eine "
        "Spur weiter). Ein Leiterschacht neben den Räumen führt beim Bauen in beide Räume und danach zu deinem Platz "
        "und zur Truhe.",
    help=[["Wenig Mobs", "Alle Höhlen und dunklen Stellen in 128 Blöcken um deinen Platz ausleuchten – dort spawnen "
                         "sonst die Monster. In den beiden Räumen darf keine Fackel übrig sein."],
          ["Monster stehen herum", "Genau auf deinem Platz warten: Weiter als 32 Blöcke von dir weg laufen Monster "
                                   "nicht mehr herum, näher als 24 spawnen keine. Die Falltüren müssen offen sein "
                                   "(senkrecht an der Kanalwand)."],
          ["Wasser fließt in den Schacht", "Ein Kanal ist zu lang oder eine Quelle sitzt nicht ganz außen: Jeder "
                                           "Kanal hat genau 8 Felder (Quelle an der Wand und 7 weitere), dann endet "
                                           "das Wasser am Rand des Lochs."],
          ["Ein Mob überlebt unten", "Selten (Anführer-Zombie mit mehr Leben, Hühnerjockey): Glas über der Truhe "
                                     "abbauen, den Mob durch die Lücke erschlagen, Glas wieder setzen."]],
    meta=m("Rate: Schätzung – rund 7-mal so viel Spawnfläche wie die einfache Farm (528 statt 72 Felder), und auch "
           "Hexen sterben. Auf dem Testserver brachte die einfache Farm 17 Items in 30 Minuten; die Profi-Farm "
           "sollte ein Vielfaches davon schaffen. In einer echten Welt hängt die Rate stark von dunklen Höhlen in der "
           "Nähe ab (grob einige hundert Items pro Stunde).",
           [("Java: Monster spawnen bis 128 Blöcke um den Spieler, aber nicht näher als 24 (kugelförmig). Tief unter "
             "der Erde konkurrieren nur dunkle Höhlen.", W + "Mob_spawning")],
           [("Kompaktes Kanal-Design: Kanäle genau 8 lang, das Wasser endet von selbst am Rand des Lochs; das "
             "Design lässt sich stapeln.", W + "Tutorial:Mob_farm#Compact_canal_design"),
            ("Wasser fließt von der Quelle 7 Blöcke weit.", W + "Water"),
            ("Monster ohne Spieler in 32 Blöcken laufen nicht mehr herum und verschwinden nach 30 s mit der Zeit.",
             W + "Mob_spawning#Despawning"),
            ("Fallschaden: 1 je Block über 3 Blöcke, Rüstung schützt nicht. Zombie, Skelett und Creeper haben 20 "
             "Leben, Spinnen 16, Hexen 26.", W + "Fall_damage"),
            ("Auf dem Testserver (26.3) mit der einfachen Farm geprüft: Im Wasser spawnt nichts, Mobs halten offene "
             "Falltüren für Boden und fallen in die Kanäle; durch Glas sehen Mobs nichts.", None)])))

f.zeichen(E=("oak_trapdoor", {"half": "bottom", "f": "e", "open": True}),
          V=("oak_trapdoor", {"half": "bottom", "f": "w", "open": True}),
          S=("oak_trapdoor", {"half": "bottom", "f": "s", "open": True}),
          N=("oak_trapdoor", {"half": "bottom", "f": "n", "open": True}),
          L=("ladder", "w"), J=("ladder", "n"))

# ---------------------------------------------------------------- oberer Raum und Zugang
f.schritt("Oberer Raum: unter der Erde einen Raum 18 × 18 Blöcke und 2 hoch ausgraben. Solange du baust, Fackeln "
          "aufstellen, damit nichts spawnt – ganz zum Schluss baust du sie alle wieder ab.", {
    OBEN: GRABEN_RAUM, OBEN + 1: GRABEN_RAUM})
f.schritt("Im oberen Raum Kanäle in Kreuzform 2 breit und 2 tief ausheben, von jeder Wand bis zur Mitte; in der "
          "Mitte bleibt ein Loch 2 × 2 (auch 2 tief). Jeder Kanal ist genau 8 Blöcke lang – so weit fließt das "
          "Wasser später, es endet von selbst am Rand des Lochs.", {
    OBEN - 1: GRABEN_KREUZ, OBEN - 2: GRABEN_KREUZ})
f.schritt("Zugang: Östlich vom Raum, mit 1 Block Wand dazwischen, einen Leiterschacht 1 × 1 graben – von Höhe 1 "
          "hinunter, bis du auf Höhe -29 stehst. Oben eine Tür-Öffnung 2 hoch durch die Wand in den Raum, direkt "
          "südlich neben dem Ende des Ostkanals (sie wird am Ende wieder zugemacht). Den Schacht nach oben "
          "verlängerst du zu deinem eigenen Eingang.", {
    y: ".-" for y in range(-29, 2)} | {OBEN: "--", OBEN + 1: "--"}, x0=18, z0=10)
f.schritt("Leitern an die Ostwand des Leiterschachts, von ganz unten (Höhe -29) bis Höhe 0. Eine Leiter klebt an "
          "dem Block, den du anklickst.", {
    y: "L" for y in range(-29, 1)}, x0=19, z0=10)

# ---------------------------------------------------------------- unterer Raum
f.schritt("Unterer Raum: Vom Leiterschacht auf Höhe -5 eine Tür-Öffnung 2 hoch nach Westen und von dort einen "
          "zweiten Raum 18 × 18, 2 hoch, genau unter dem oberen ausgraben (Höhe -5 und -4). Die Schicht -3 bleibt "
          "als Decke stehen – darin liegen die Böden der oberen Kanäle.", {
    UNTEN: GRABEN_UNTEN, UNTEN + 1: GRABEN_UNTEN})
f.schritt("Im unteren Raum genauso Kanäle in Kreuzform und das Loch in der Mitte ausheben, 2 breit und 2 tief "
          "(Höhe -6 und -7), jeder Kanal genau 8 lang.", {
    UNTEN - 1: GRABEN_KREUZ, UNTEN - 2: GRABEN_KREUZ})
f.schritt("Die beiden Löcher verbinden: In der Mitte die Decke des unteren Raums 2 × 2 durchbrechen (Höhe -3, "
          "unter dem Loch des oberen Raums).", {
    -3: "--\n--"}, x0=MITTE, z0=MITTE)

# ---------------------------------------------------------------- unten: Gang, Platz, Truhe
f.schritt("Unten auf Höhe -29: vom Fuß des Leiterschachts einen Gang 2 hoch 8 Blöcke nach Westen graben, und noch "
          "1 Feld weiter – dort ist dein Platz, schräg neben dem Schacht, der später in der Mitte hinunterführt. "
          "Direkt südlich neben deinem Platz einen kleinen Leiterschacht hinunter, bis du auf Höhe -39 stehst, und "
          "unten 1 Feld nach Norden, 2 hoch: Dort stehst du später an der Truhe.", {
    -28: "---------\n-", -29: "---------\n-"} | {y: ".\n-" for y in range(-39, -29)} | {-39: "-\n-", -38: "-\n-"},
    x0=10, z0=10)
f.schritt("Schacht: unter dem Loch des unteren Raums 2 × 2 weiter hinunter graben, bis Höhe -39 (zusammen 32 Blöcke "
          "ab dem Loch). Vorsicht – nicht hineinfallen. Unten vom südöstlichen Schachtfeld aus 1 Feld nach Süden "
          "durchbrechen, 2 hoch, bis zu deinem Platz an der Truhe: Dort kommen Truhe und Glas hin.", {
    y: "--\n--" for y in range(-39, -7)} | {-39: "--\n--\n.-", -38: "--\n--\n.-"}, x0=MITTE, z0=MITTE)
f.schritt("Unten: In das eben durchgebrochene Feld südlich vom Schacht (untere Ebene) eine Truhe. Dann die 4 "
          "Trichter unter den Schacht (ein Trichter zeigt in den Block, an den du klickst – an Truhe und Trichter "
          "schleichend klicken): zuerst den direkt nördlich der Truhe, der in die Truhe zeigt, dann nördlich davon "
          "einen, der nach Süden in diesen zeigt, dann die beiden westlichen, die nach Osten zeigen. Den letzten "
          "setzt du von einem schon gesetzten Trichter aus.", {
    -39: ">v\n>v\n.C"}, x0=MITTE, z0=MITTE)
f.schritt("Über die Truhe aus dem Schacht nach Süden steigen und weiter nach Osten auf deinen Platz an der Truhe, "
          "dann Glas auf die Truhe setzen (schleichend oben auf die Truhe klicken). Es schließt den Schacht ab, die "
          "Truhe geht trotzdem auf, und Monster sehen durch Glas nicht hindurch.", {
    -38: "G"}, x0=MITTE + 1, z0=MITTE + 2)
f.schritt("Leitern im kleinen Leiterschacht an die Südwand, von Höhe -39 bis -30. Oben steigst du nach Norden auf "
          "deinen Platz.", {
    y: "J" for y in range(-39, -29)}, x0=10, z0=11)

# ---------------------------------------------------------------- Wasser und Falltüren
f.schritt("Wasser im unteren Raum: in die 8 Kanal-Enden an den Wänden je eine Quelle (auf den Kanalboden, Höhe -7). "
          "Das Wasser fließt genau bis zum Rand des Lochs.", {
    UNTEN - 2: WASSER})
f.schritt("Unterer Raum: Über die 8 Quellen je einen Block, in jedes andere Kanalfeld auf Bodenhöhe (-6) eine "
          "Falltür: an die Seite der Kanalwand neben ihr klicken und aufklappen – die Klappe steht dann senkrecht an "
          "dieser Wand. Monster halten das für Boden, laufen darauf und fallen ins Wasser.", {
    UNTEN - 1: DECKEL})
f.schritt("Wasser im oberen Raum genauso: 8 Quellen in die Kanal-Enden an den Wänden (Höhe -2).", {
    OBEN - 2: WASSER})
f.schritt("Oberer Raum: über die Quellen je einen Block, in alle anderen Kanalfelder (Höhe -1) offene Falltüren mit "
          "der Klappe an der Kanalwand – wie unten.", {
    OBEN - 1: DECKEL})
f.schritt("Zum Schluss: alle Fackeln aus beiden Räumen abbauen – dort muss es ganz dunkel sein. Dann vom Leiterschacht "
          "aus die beiden Tür-Öffnungen mit je 2 Blöcken zumachen, ebenso Gänge, durch die du anfangs in den oberen "
          "Raum gekommen bist. Leiterschacht und Gang dagegen gut ausleuchten.", {
    OBEN: "#", OBEN + 1: "#", UNTEN: "#", UNTEN + 1: "#"}, x0=18, z0=10)
f.schritt("Dein Platz: unten im Gang auf Höhe -29, schräg neben dem Schacht – 24 Blöcke unter dem unteren und 29 unter "
          "dem oberen Raum. Hier warten. Zur Truhe geht es die kleine Leiter 10 Blöcke hinunter.", {
    -29: "P"}, x0=10, z0=10)

# Haupttest wie bei der einfachen Farm (unter der Erde in Stein), gleiche Messgröße: Beute in Truhe und Trichtern.
# Die einfache Farm brachte hier 17 Stück (1 Fleisch, 3 Pfeile, 5 Knochen, 8 Schwarzpulver).
BEUTE = "minecraft:rotten_flesh|minecraft:bone|minecraft:arrow|minecraft:gunpowder|minecraft:string"
f.pruefe(boden="minecraft:stone", fuellung="minecraft:stone", erde_bis=3, zeit="day",
         erwartet={"items": {BEUTE: 30}})
# Hexen sind selten: zwei Zombies und drei Hexen in den UNTEREN Raum (kürzester Fall, 31 Blöcke). Sie müssen in die
# Kanäle laufen und unten sterben – keine Hexe darf unten im Schacht überleben.
HEXENBEUTE = ("minecraft:redstone|minecraft:glowstone_dust|minecraft:sugar|minecraft:glass_bottle|minecraft:stick|"
              "minecraft:spider_eye")
f.pruefe_auch("mobfarm_profi_mech", boden="minecraft:stone", fuellung="minecraft:stone", erde_bis=3, zeit="day",
              nachher=mobs("zombie", [(1, UNTEN, 1), (16, UNTEN, 16)]) +
              mobs("witch", [(16, UNTEN, 1), (1, UNTEN, 16), (4, UNTEN, 12)]),
              bereich=[MITTE, LANDUNG, MITTE, MITTE + 1, LANDUNG, MITTE + 1],
              erwartet={"items": {"minecraft:rotten_flesh": 1, HEXENBEUTE: 1}},
              hoechstens={"wesen": {"minecraft:witch": 0}})
