"""Wither-Skelett-Farm (Profi): Zwei Spawnflächen übereinander in der Netherfestung (Kreuze aus Netherziegeln, Arme
2 breit, Ränder offen), in der Mitte ein Loch 2 × 2 mit offenen Falltüren – Monster halten sie für Boden und fallen.
Spinnennetze direkt unter dem Loch fangen jeden Fall ab; danach fallen die Wither-Skelette noch knapp 20 Blöcke durch
einen Schacht 2 × 2 und kommen mit 1½–2 Herzen in der Tötungskammer an. Du stehst auf den Truhen daneben und triffst
sie durch einen Spalt (½ Block hoch: unten Netherrack, oben eine obere Stufe); sehen und treffen können sie dich nicht.

Loch x 0 … 1, z 0 … 1. Untere Fläche: Boden y -1 (Füße y 0), Arme 15 lang; obere Fläche: Boden y 3 (Füße y 4), Arme 9
lang. Spinnennetze (0 … 1, -2, 0 … 1). Schachtwände (8 je Ebene, ohne Ecken) y -2 … -22. Kammer: Schlamm
(0 … 1, -25, 0 … 1) über Trichtern (0 … 1, -26, 0 … 2, alle nach Süden) → Truhen (0 … 1, -26, 3). Zwischenreihe z 2:
Netherrack y -25, obere Stufe y -24, Netherrack y -23. Platz (0, -25, 3), Decke y -23, Tür (0, -25 … -24, 4).
"""
from profi_basis import *

BLOECKE = {"cobweb": ("cobweb", "minecraft:cobweb", "minecraft:cobweb", "Spinnennetz (mit der Schere abbauen)")}

L1, L2 = 15, 9                      # Armlänge unten / oben (oben weiter weg vom Platz: höchstens 32 Blöcke)

f = profi("witherskelett", dict(
    name="Wither-Skelett-Farm (Profi)", diff=4,
    out="Wither-Skelett-Schädel, Kohle, Knochen (nebenbei Lohenruten, Goldklumpen, Pfeile)",
    where="Netherfestung: neben einer Brücke oder einem Gang auf Höhe des Netherziegelbodens, darunter 26 Blöcke "
          "Platz (meist Luft über dem Lavasee)",
    afk="Ja – an der Tötungskammer warten (dort spawnt nichts) und ab und zu zuschlagen",
    why="Auf der Fläche der einfachen Farm spawnte im Test in 30 Minuten kein einziges Wither-Skelett, und wer kam, "
        "musste von dir im Kampf erwischt werden. Hier gibt es zwei Spawnflächen übereinander: Ein Monster-Trupp "
        "spawnt auf einer zufälligen Höhe, darum zählt jede Ebene extra. Beide sind Kreuze aus Netherziegeln mit 4 "
        "Armen, 2 breit (unten 15 lang, oben 9), dazwischen 3 Blöcke Luft (Wither-Skelette sind 2,4 hoch). Die "
        "Ränder bleiben offen: Monster laufen nicht freiwillig über eine Kante, und große Magmawürfel (passen nicht "
        "durchs Loch) hüpfen so von selbst hinunter. In der Mitte liegt ein Loch 2 × 2 mit 4 offenen Falltüren – "
        "Monster halten sie für Boden. Wer von einem Arm zu einem anderen will, tritt darauf und fällt. Direkt "
        "unter dem Loch hängen 4 Spinnennetze: Sie bremsen jeden Fall auf null, auch den von der oberen Fläche. "
        "Danach fällt ein Wither-Skelett noch knapp 20 Blöcke durch den Schacht und kommt mit 1½–2 Herzen unten an "
        "– ein Schlag genügt, mit Schwungkraft für alle. Unten stehen sie auf Schlamm; die Trichter darunter bringen "
        "Schädel, Kohle und Knochen in die Truhen, auf denen du stehst. Zwischen dir und ihnen liegt ein Spalt, "
        "½ Block hoch: Du triffst ihre Beine, sie sehen dich nicht und erreichen dich nicht, auch kleine "
        "Magmawürfel passen nicht hindurch. Abstände: Dein Platz ist 25 Blöcke unter der unteren Fläche – näher "
        "als 24 spawnt nichts – und jedes Armende höchstens 32 Blöcke von dir entfernt, sonst stehen die Monster "
        "still. Schädel gibt es nur, wenn du triffst. XP-Kugeln kommen durch den niedrigen Spalt kaum zu dir – dafür "
        "ist er dicht.",
    help=[["Es spawnt wenig",
           "Die Flächen müssen in der Festung liegen (außerhalb ihrer Gänge zählt nur Netherziegel-Boden), dunkel "
           "sein (Licht ≤ 7) und 3 Blöcke Luft haben. Freie Netherziegel-Flächen der Festung in der Nähe mit Stufen "
           "oder Teppichen belegen – dann spawnen mehr Monster hier."],
          ["Monster bleiben oben",
           "Du musst auf deinem Platz sein: Weiter als 32 Blöcke weg laufen sie nicht herum. Die 4 Falltüren müssen "
           "offen sein (Klappen am Rand des Lochs)."],
          ["Sie kommen tot unten an",
           "Die 4 Spinnennetze müssen direkt unter den Falltüren hängen, alle 4 Felder. Ohne Netz ist der Fall von "
           "oben tödlich – dann gibt es keine Schädel."],
          ["Keine Schädel",
           "Nur wenn du triffst: 2,5 %, mit Plünderung III 5,5 %. Im Spinnennetz hängen sie etwa 45 Sekunden, bevor "
           "sie unten ankommen."]],
    meta=m("Rate: Schätzung – je nach Festung und anderen freien Flächen 30–100 Wither-Skelette pro Stunde, mit "
           "Plünderung III also etwa 2–5 Schädel, dazu Kohle und Knochen (ein Trupp sind bis zu 5). Im Test der "
           "einfachen Farm spawnte auf der Fläche in 30 Minuten keins.",
           [("Netherfestung: Wither-Skelette spawnen in den einzelnen Festungsteilen auf jedem Block, im ganzen "
             "Festungsbereich außerhalb davon nur auf Netherziegeln; Licht ≤ 7.", W + "Wither_Skeleton"),
            ("Spawnflächen in der Festung bauen, andere Flächen belegen, die Monster zu einem Punkt bringen und dort "
             "töten.", W + "Tutorial:Wither_skeleton_farming")],
           [("Ein Trupp spawnt auf einer zufälligen Höhe zwischen Boden und oberstem Block (alle auf derselben Höhe), "
             "nur weiter als 24 Blöcke vom Spieler; Monster ohne Spieler in 32 Blöcken bleiben stehen und "
             "verschwinden.", W + "Mob_spawning"),
            ("Mobs halten offene Falltüren für geschlossen und fallen hindurch.", W + "Trapdoor"),
            ("Spinnennetze heben den Fallschaden auf (Fallhöhe wird null); Mobs sinken darin etwa 13 Sekunden pro "
             "Block.", W + "Cobweb"),
            ("Fallschaden = Fallhöhe − 3 (abgerundet); Wither-Skelette haben 20 Lebenspunkte, sind 2,4 hoch und "
             "passen nicht durch 2 hohe Öffnungen.", W + "Damage#Fall_damage"),
            (TEST + "Mobs laufen auf offene Falltüren und fallen; weiter als 32 Blöcke vom Spieler laufen sie nicht "
             "herum; Trichter saugen Items durch Schlamm hindurch auf.", None)])))

f.zeichen(N="nether_bricks", R="netherrack", M="mud", X="cobweb", O=("slab", {"half": "top"}),
          a=("oak_trapdoor", {"f": "e", "open": True}), b=("oak_trapdoor", {"f": "s", "open": True}),
          c=("oak_trapdoor", {"f": "w", "open": True}), d=("oak_trapdoor", {"f": "n", "open": True}))

LOCH = [(0, 0), (1, 0), (0, 1), (1, 1)]
FALLTUEREN = {(0, 0): "a", (1, 0): "b", (1, 1): "c", (0, 1): "d"}       # Klappen außen am Lochrand (Windrad)
RING = [(-1, 0), (-1, 1), (2, 0), (2, 1), (0, -1), (1, -1), (0, 2), (1, 2)]   # Schachtwände ohne Ecken
X0, Z0, X1, Z1 = -L1, -L1, L1 + 1, L1 + 1


def arme(n):
    return [(x, z) for x in (0, 1) for z in range(-n, 0)] + [(x, z) for x in (0, 1) for z in range(2, n + 2)] + \
           [(x, z) for z in (0, 1) for x in range(-n, 0)] + [(x, z) for z in (0, 1) for x in range(2, n + 2)]


def ebene(zellen):
    return raster_aus(zellen, X0, Z0, X1, Z1)


def mit(punkte, zeichen):
    return {p: zeichen for p in punkte}


# 1 – Freimachen
frei = {y: ebene(mit(arme(L1) + LOCH, "-")) for y in range(0, 3)}
frei.update({y: ebene(mit(arme(L2) + LOCH, "-")) for y in range(4, 7)})
frei.update({y: ebene(mit(LOCH, "-")) for y in range(-24, -1)})
frei.update({y: ebene(mit([(0, 3), (1, 3)], "-")) for y in (-25, -24)})
frei[-24] = ebene(mit(LOCH + [(0, 3), (1, 3)], "-"))
f.schritt("Ort: in der Netherfestung neben einer Brücke oder einem Gang, auf Höhe seines Netherziegelbodens – dort "
          "gilt noch die Festung –, wo darunter 26 Blöcke frei sind (meist über dem Lavasee). Du stehst auf dem "
          "Nordwest-Feld des späteren Lochs. Frei sein müssen: über beiden Flächen je 3 Blöcke Luft, der Schacht 2 × 2 "
          "nach unten und unten dein Platz. Kein Licht in der Nähe (keine Fackeln, keine Lava).", frei, x0=X0, z0=Z0)

# 2 – untere Fläche
f.schritt(f"Untere Spawnfläche: ein Kreuz aus Netherziegeln eine Ebene unter deinen Füßen, 4 Arme je 2 breit und "
          f"{L1} lang (an der Brücke ansetzen, dann Block an Block). In der Mitte bleibt das Loch 2 × 2. Die Ränder "
          f"bleiben offen.", {-1: ebene(mit(arme(L1), "N"))}, x0=X0, z0=Z0)
f.schritt("In jedes Lochfeld eine Falltür (Karmesin oder Wirr brennen nicht), jeweils an einen Armblock klicken und "
          "dann öffnen: Nordwest-Feld an den Block im Westen, Nordost an den im Norden, Südost an den im Osten, "
          "Südwest an den im Süden. Offen stehen die Klappen dann am Lochrand, in der Mitte ist 1 5/8 Block frei.", {
    -1: "ab\ndc"})

# 3 – Schacht
f.schritt("Schacht 2 × 2 nach unten: Wände aus Netherrack an allen 4 Seiten (die Ecken brauchst du nicht), vom "
          "Block unter den Armen 21 Ebenen tief. Am besten von einem Gerüst aus bauen.", {
    y: ebene(mit(RING, "R")) for y in range(-22, -1)}, x0=X0, z0=Z0)
f.schritt("4 Spinnennetze direkt unter die Falltüren, an die Schachtwand klicken (abbauen nur mit der Schere). Hier "
          "bleibt jeder Fall hängen – auch der von der oberen Fläche –, die Fallhöhe beginnt neu.", {
    -2: "XX\nXX"})

# 4 – Tötungskammer
f.schritt("Kammer ganz unten (23 bis 26 Blöcke unter deinen Füßen auf der unteren Fläche): Die Schachtwände im "
          "Westen, Norden und Osten noch 3 Ebenen tiefer führen. Im Süden kommt eine Zwischenreihe: Netherrack direkt "
          "unter der Südwand und 2 Ebenen tiefer (mit je einem Block an den Seiten); dazwischen kommt später die "
          "Stufe. Südlich davon dein Platz, 2 breit und 2 hoch, mit Decke (eine Reihe länger), Seitenwänden und "
          "Rückwand (sie reicht eine Ebene tiefer). Die zwei Rückwandblöcke hinter dem westlichen Platz sind deine "
          "Tür: abbauen und hinter dir wieder setzen. Den Weg hierher (Leiter oder Treppe) baust du, wie es passt.", {
    -23: """
        .RR.
        R..R
        R..R
        .RR.
        .RR.
        .RR.
    """,
    -24: """
        .RR.
        R..R
        R..R
        R..R
        R..R
        .RR.
    """,
    -25: """
        .RR.
        R..R
        R..R
        RRRR
        R..R
        .RR.
    """,
    -26: """
        ....
        ....
        ....
        ....
        ....
        .RR.
    """}, x0=-1, z0=-1)
f.schritt("Ganz unten: 2 Truhen (an die Rückwand klicken), dann je 3 Trichter nach Norden davor – schleichend an die "
          "Truhe bzw. den Trichter klicken: Alle zeigen nach Süden zur Truhe.", {
    -26: "vv\nvv\nvv\nCC"})
f.schritt("Schlamm (Wasserflasche auf Erde) auf die 4 Trichter unter dem Schacht – Trichter saugen durch Schlamm. "
          "Zwei OBERE Stufen in die Lücke der Zwischenreihe (an die Unterseite des Netherracks darüber klicken). "
          "Zwischen Netherrack und Stufe bleibt ein Spalt ½ Block hoch: Du triffst die Beine der Monster, sie sehen "
          "dich nicht.", {
    -25: "MM\nMM",
    -24: "..\n..\nOO"})
mitte = arme(L2)
f.schritt(f"Obere Spawnfläche: dasselbe Kreuz 4 Blöcke höher (3 Blöcke Luft über der unteren), Arme nur {L2} lang – "
          f"weiter weg wären die Monster mehr als 32 Blöcke von deinem Platz entfernt und blieben stehen. Mit einem "
          f"Turm aus Hilfsblöcken hinauf und ihn danach abbauen. Ins Loch wieder 4 offene Falltüren wie unten.", {
    3: ebene(mit(mitte, "N") | {(x, z): FALLTUEREN[(x, z)] for (x, z) in LOCH})}, x0=X0, z0=Z0)
f.schritt("Dein Platz: auf der westlichen Truhe stehen, 25 Blöcke unter der unteren Fläche. Wenn sich unten Monster "
          "sammeln, durch den Spalt zuschlagen – am besten mit Schwungkraft und Plünderung III.", {-25: "P"}, z0=3)

# Test: am echten Festungsbauwerk wie die einfache Farm. Unter der Kammer füllt der Test Netherrack auf (oben bleibt
# Luft wie neben einer Brücke). Gemessen: Wither-Skelette in der Tötungskammer.
KAMMER = [0, -25, 0, 1, -22, 1]
UMGEBUNG = dict(dimension="the_nether", zeit="day", welt="struktur",
                bauwerk={"id": "minecraft:fortress", "anker": [0, 1, 0], "suchen": True, "hoehe": 64},
                boden="minecraft:netherrack", fuellung="minecraft:netherrack", erde_bis=-21)
f.pruefe(**UMGEBUNG, bereich=KAMMER, erwartet={"wesen": {"minecraft:wither_skeleton": 1}})
# Mechanik: Wither-Skelette auf beide Flächen setzen – sie müssen ins Loch laufen, im Netz hängen bleiben und lebend
# unten ankommen.
f.pruefe_auch("witherskelett_profi_mech", **UMGEBUNG,
              nachher=mobs("wither_skeleton", [(0, 0, -10), (-8, 0, 1), (10, 0, 0), (1, 0, 9), (1, 4, -6), (6, 4, 1)]),
              bereich=KAMMER, erwartet={"wesen": {"minecraft:wither_skeleton": 4}})
