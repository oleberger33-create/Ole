"""Alle Farmen des Farmhelpers in der einfachsten Bauweise, die auf dem Testserver funktioniert hat.

Aufruf:  python3 farmen.py            → schreibt plaene.json (für farmhelper.py) und ../test/tests.json
         python3 farmen.py --material → zeigt je Farm die Materialliste

Raster: Zeilen = Norden → Süden (z), Spalten = Westen → Osten (x). y 0 = Höhe der Füße des Spielers, y -1 = der
Boden, auf dem er steht. Erklärung des Formats in entwurf.py.
"""
import sys

from entwurf import Farm, schreiben

from farmtexte import TEXTE

REIHENFOLGE = ["zuckerrohr", "bambus", "kaktus", "kuerbis", "seetang", "weizen", "baum", "knochenmehl", "blumen",
               "huehner", "kuh", "wolle", "honig", "eisen", "xpspawner", "mobfarm", "creeper", "schleim", "hexe",
               "waechter", "lohe", "gold", "witherskelett", "enderman", "ertrunkene", "aussenposten", "ueberfall",
               "handel", "bruchstein", "lava", "schnee", "angeln", "stockcrafter"]


def farm(fid, **info):
    daten = dict(TEXTE[fid])
    daten.update(info)
    return Farm(fid, **daten)


GRAS = "minecraft:grass_block"


# ===================================================================== Pflanzen
def rohr_farm(fid, pflanze, einzeln, **info):
    """Zuckerrohr / Bambus: 8 Pflanzen auf Schlamm über Trichtern, Kolben schlagen den 2. Block ab.
    Ein Beobachter an einer Pflanze schaltet über eine Redstone-Leitung alle Kolben. Was daneben ins Wasser fällt,
    schwimmt zum letzten Trichter."""
    f = farm(fid, **info)
    f.zeichen(M="mud", Z=pflanze, K=("piston", "s"), B=("observer", "s"))
    f.schritt("Graben ausheben: eine Reihe 2 tief (für Truhe und Trichter), daneben eine Rinne 1 tief.", {
        -2: """
            ..........
            ..........
            ----------
            ..-.......
        """,
        -1: """
            ..........
            ..........
            ----------
            ..--------
        """}, x0=-1)
    f.schritt("Unten die Truhe (Westen) und 9 Trichter, die alle nach Westen zeigen. Unter das Westende der Rinne "
              "ein Trichter, der nach Norden in die Trichterreihe zeigt.", {
        -2: """
            C<<<<<<<<<
            ..^.......
        """}, x0=-1, z0=2)
    f.schritt("Schlamm auf 8 Trichter (Wasserflasche auf Erde) – der Trichter am Westende und die Truhe bleiben "
              "offen. In die Rinne ganz im Osten eine Wasserquelle: sie fließt bis zum Trichter am Westende. "
              "Hinter der Rinne eine niedrige Mauer, damit nichts darüber fliegt.", {
        -1: """
            .MMMMMMMM
            .FFFFFFFW
        """,
        0: """
            .........
            .........
            .########
        """}, z0=2)
    f.schritt("Nördlich vom Schlamm eine Reihe Blöcke, darauf Kolben, die nach Süden zeigen (auf Höhe des 2. Blocks).", {
        0: """
            .########
        """,
        1: """
            .KKKKKKKK
        """}, z0=1)
    if einzeln:
        f.schritt("Hinter die Kolben eine Reihe Blöcke mit Redstone-Staub obendrauf. Auf jeden Kolben ein Beobachter, "
                  "dessen Gesicht nach Süden auf den 3. Block schaut – Bambus wird sonst zu hoch und fliegt weit.", {
            1: """
                .########
            """,
            2: """
                .RRRRRRRR
                .BBBBBBBB
            """})
    else:
        f.schritt("Hinter die Kolben eine Reihe Blöcke mit Redstone-Staub obendrauf. Auf die Kolben eine Reihe Blöcke, "
                  "in der Mitte statt eines Blocks ein Beobachter, dessen Gesicht nach Süden auf den 3. Block schaut. "
                  "Zuckerrohr wird nie höher als 3 – die anderen warten, bis der beobachtete so weit ist.", {
            1: """
                .########
            """,
            2: """
                .RRRRRRRR
                .###B####
            """})
    f.schritt(("Zuckerrohr" if pflanze == "sugar_cane" else "Bambus") + " auf den Schlamm setzen – fertig. Wird "
              "die beobachtete Pflanze 3 hoch, schlagen alle Kolben den 2. Block ab.", {
        0: """
            .........
            .........
            .ZZZZZZZZ
        """})
    return f


rohr_farm("zuckerrohr", "sugar_cane", False).pruefe(
    boden=GRAS, erwartet={"items": {"minecraft:sugar_cane": 6}})
rohr_farm("bambus", "bamboo", True).pruefe(
    boden=GRAS, erwartet={"items": {"minecraft:bamboo": 6}})

f = farm("kaktus")
f.zeichen(S="sand", K="cactus")
f.schritt("Zwei Rinnen ausheben (1 tief, 8 lang) mit einer Reihe Sand dazwischen. Am Westende 2 tief für Truhe und "
          "Trichter.", {
    -2: """
        .-
        .-
        .-
    """,
    -1: """
        .--------
        .-SSSSS
        .--------
    """}, x0=-2, z0=-1)
f.schritt("Truhe in die Mitte, links und rechts davon Trichter, die in die Truhe zeigen.", {
    -2: """
        .v......
        .C......
        .^......
    """}, x0=-2, z0=-1)
f.schritt("Wasserquellen ans Ostende beider Rinnen – das Wasser fließt bis über die Trichter.", {
    -1: """
        ..FFFFFFW
        ........
        ..FFFFFFW
    """}, x0=-2, z0=-1)
f.schritt("Glasstange auf Höhe 1 über der südlichen Rinne (an den Enden je ein Glas als Stütze). Wächst ein Kaktus "
          "auf 2 Blöcke, berührt er das Glas und bricht ab.", {
    0: """
        .G.....G
    """,
    1: """
        .GGGGGGG
    """}, x0=-2, z0=1)
f.schritt("Kakteen auf jeden zweiten Sand pflanzen (Westende, Mitte, Ostende) – fertig.", {
    0: """
        K.K.K
    """}, x0=0, z0=0)
f.pruefe(boden=GRAS, erwartet={"items": {"minecraft:cactus": 3}})

f = farm("kuerbis")
f.zeichen(A="farmland", M="mud", T="melon_stem", K=("piston", "d"), B=("observer", "d"))
f.schritt("Ausheben: eine Wasserrinne (4 lang) und zwei Reihen weiter eine Reihe 2 tief für Trichter und Truhe.", {
    -2: """
        .....
        .....
        -----
    """,
    -1: """
        ----.
        .....
        -----
    """})
f.schritt("4 Trichter nach Osten in die Truhe.", {
    -2: """
        .....
        .....
        >>>>C
    """})
f.schritt("Wasser ins Westende der Rinne, Gras dazwischen zu Ackerboden hacken, Schlamm auf die Trichter. "
          "An die Enden der Ackerreihe je ein Block, damit dort keine Frucht wächst.", {
    -1: """
        .WFFF.
        .AAAA.
        .MMMM.
    """,
    0: """
        ......
        #....#
        #.....
    """}, x0=-1)
f.schritt("Melonen- oder Kürbiskerne auf den Ackerboden.", {
    0: """
        ....
        TTTT
    """})
f.schritt("Über dem Schlamm 4 Kolben, die nach UNTEN zeigen (Stütze am Westende).", {
    1: """
        .....
        .....
        #KKKK
    """}, x0=-1)
f.schritt("Über den zweiten Stängel ein Beobachter, der nach UNTEN schaut, darauf ein Block. Redstone-Staub auf die "
          "Kolben – wächst eine Frucht, fahren alle Kolben aus.", {
    1: """
        ....
        .B..
    """,
    2: """
        ....
        .#..
        RRRR
    """})
f.pruefe(boden=GRAS, nachher=["fill {x} {y} {z+1} {x+3} {y} {z+1} minecraft:melon_stem[age=7]"],
         erwartet={"items": {"minecraft:melon_slice": 3}})

f = farm("seetang")
f.zeichen(Z="kelp", K=("piston", "s"), B=("observer", "s"))
f.schritt("Becken 6 lang, 1 breit, 3 hoch: Nordwand unten aus Blöcken, darüber Kolben nach Süden. An der Südseite "
          "unten Blöcke, darauf 6 Trichter nach Osten in eine Truhe. Die Enden zu.", {
    0: """
        ########
        #......#
        ########
    """,
    1: """
        #KKKKKK#
        #......#
        #>>>>>>C
    """}, x0=-1)
f.schritt("Hinter die Kolben Blöcke mit Redstone-Staub darauf. Obere Reihe der Nordwand aus Blöcken, in der Mitte ein "
          "Beobachter, der nach Süden auf den obersten Seetang schaut. Über den Trichtern ein Rand.", {
    1: """
        .######.
    """,
    2: """
        .RRRRRR.
        ###B####
        #......#
        #......G
        .######.
    """}, x0=-1, z0=-1)
f.schritt("Wasserquellen in die oberste Reihe des Beckens (Höhe 2): Das Wasser fällt nach unten und läuft über die "
          "Trichter. Unten im Becken entsteht fallendes Wasser – das reicht für den Seetang.", {
    1: """
        FFFFFF
    """,
    2: """
        WWWWWW
        FFFFFF
    """}, z0=1)
f.schritt("Seetang auf den Boden setzen – fertig. Wächst der Seetang bis oben, schlagen die Kolben ihn ab; er "
          "schwimmt hoch und treibt über den Trichter daneben.", {
    0: """
        ZZZZZZ
    """}, z0=1)
f.pruefe(boden=GRAS, erwartet={"items": {"minecraft:kelp": 4}})

f = farm("weizen")
f.zeichen(A="farmland", O="composter", Z="oak_fence", V="villager", Q="wheat")
f.schritt("Feld 4 × 2 ausheben, 2 tief, links davon Platz für Trichter und Truhe, rechts ein Loch fürs Wasser.", {
    -2: """
        ------
        ..----
    """,
    -1: """
        -------
        ..----
    """}, x0=-2)
f.schritt("8 Trichter unter das Feld: hintere Reihe nach Norden, vordere Reihe nach Westen, dann über einen "
          "Trichter in die Truhe.", {
    -2: """
        C<<<<<
        ..^^^^
    """}, x0=-2)
f.schritt("Erde auf die Trichter, dann zu Ackerboden hacken. Rechts daneben eine Wasserquelle.", {
    -1: """
        AAAAW
        AAAA.
    """})
f.schritt("Zaun rundherum, links ein Komposter mit Block darüber (Arbeitsplatz des Bauern).", {
    0: """
        ZZZZZZ
        Z....Z
        O....Z
        ZZZZZZ
    """,
    1: """
        ......
        ......
        #.....
    """}, x0=-1, z0=-1)
f.schritt("Weizen säen und einen Dorfbewohner hineinbringen. Wirf ihm einen Stapel Samen (oder Karotten/Kartoffeln) "
          "zu – er wird Bauer, erntet und pflanzt mit seinen Samen nach. Die Ernte fällt in die Trichter.", {
    0: """
        QQQQ
        QQQQ
    """})
f.schritt("Dorfbewohner aufs Feld.", {0: "V"}, x0=1)
f.pruefe(boden=GRAS, zeit="day",
         nachher=["kill @e[type=minecraft:villager,x={x},y={y},z={z},distance=..8]",
                  'summon minecraft:villager {x+1} {y} {z} {PersistenceRequired:1b,VillagerData:{profession:'
                  '"minecraft:farmer",level:1,type:"minecraft:plains"},Inventory:[{id:"minecraft:wheat_seeds",'
                  'count:64}]}',
                  "fill {x} {y} {z} {x+3} {y} {z+1} minecraft:wheat[age=7]"],
         erwartet={"items": {"minecraft:wheat": 4}})

f = farm("baum")
f.zeichen(S="oak_sapling")
f.schritt("Freier Platz mit Gras oder Erde, nach oben mindestens 15 Blöcke frei. 4 Setzlinge der Dunklen Eiche im "
          "2 × 2-Quadrat pflanzen, dann Knochenmehl drauf. Fällen, Setzlinge aufsammeln, von vorn.", {
    0: """
        SS
        SS
    """})
f.pruefe(boden=GRAS, erwartet={"bloecke": {"minecraft:dark_oak_log": 4}})

f = farm("knochenmehl")
f.zeichen(O="composter", H=("hopper", "d"))
f.schritt("Truhe auf den Boden, westlich daneben ein Trichter, der nach Osten in die Truhe zeigt.", {
    0: ">C"})
f.schritt("Komposter auf den Trichter, oben drauf ein Trichter, der nach UNTEN in den Komposter zeigt – fertig. "
          "Pflanzen (Samen, Seetang, Kaktus …) in den oberen Trichter, das Knochenmehl kommt in der Truhe an.", {
    1: "O",
    2: "H"})
f.pruefe(nachher=[f"item replace block {{x}} {{y+2}} {{z}} container.{i} with minecraft:wheat_seeds 64"
                  for i in range(5)],
         erwartet={"items": {"minecraft:bone_meal": 2}})

f = farm("blumen")
f.zeichen(D=("dispenser", "w"), U="stone_button")
f.schritt("Im Blumenwald (oder einem anderen Blumen-Biom) neben einem Grasblock ein Loch graben und einen Spender "
          "hineinsetzen, der zur Seite auf das Gras zeigt (oben auf dem Gras darf nichts stehen, sonst wird es zu "
          "Erde). Knochenmehl hinein, Knopf oben auf den Spender. Jeder Druck lässt rundherum Blumen wachsen – mit "
          "der Hand abernten.", {
    -1: ".D",
    0: ".U"})
f.pruefe(boden=GRAS, biom="minecraft:flower_forest",
         nachher=["item replace block {x+1} {y-1} {z} container.0 with minecraft:bone_meal 64",
                  "setblock {x+1} {y-1} {z-1} minecraft:observer[facing=north]",
                  "setblock {x+1} {y-1} {z-2} minecraft:observer[facing=south]"],
         erwartet={"bloecke": {"#minecraft:small_flowers": 3}})

# ===================================================================== Tiere
f = farm("wolle")
f.zeichen(O=("observer", "e"), D=("dispenser", "e"), A="grass_block", Y="rail", Q="hopper_minecart",
          X="sheep")
f.schritt("Ausheben: 2 tief für Trichter und Truhe, daneben ein Loch, um an die Truhe zu kommen.", {
    -2: "---",
    -1: "---"})
f.schritt("Trichter nach Osten in die Truhe, auf die Truhe ein Glas. Auf den Trichter eine Schiene mit Trichterlore.", {
    -2: ">C",
    -1: "YG",
})
f.schritt("Lore auf die Schiene.", {-1: "Q"})
f.schritt("Grasblock (oder Erde, die zu Gras wird) über die Lore. Westlich davon ein Beobachter, der auf das Gras "
          "schaut, dahinter ein Block. Rundherum Blöcke auf gleicher Höhe.", {
    0: """
        ..#.
        #OA#
        ..#.
    """}, x0=-2, z0=-1)
f.schritt("Redstone-Staub auf den Block hinter dem Beobachter, auf den Beobachter ein Spender, der nach Osten zeigt. "
          "Scheren in den Spender. Glaswände 2 hoch um das Gras.", {
    1: """
        ..G.
        RD.G
        ..G.
    """,
    2: """
        ..G.
        .G.G
        ..G.
    """}, x0=-2, z0=-1)
f.schritt("Schaf hinein – frisst es Gras, merkt es der Beobachter und der Spender schert es.", {1: "X"})
f.pruefe(boden=GRAS,
         nachher=["item replace block {x-1} {y+1} {z} container.0 with minecraft:shears",
                  "kill @e[type=minecraft:sheep,x={x},y={y},z={z},distance=..4]",
                  "summon minecraft:sheep {x}.5 {y+1} {z}.5 {PersistenceRequired:1b,Sheared:1b}"],
         erwartet={"items": {"minecraft:white_wool": 2}})

f = farm("honig")
f.zeichen(N="bee_nest", D=("dispenser", "d"), O=("observer", "e"), Q=("observer", "w"), Y="poppy", X="bee")
f.schritt("Ausheben: vor dem Nest ein Loch für einen Trichter, daneben eins für die Truhe.", {-1: "--"}, z0=-1)
f.schritt("Trichter nach Osten in die Truhe.", {-1: ">C"}, z0=-1)
f.schritt("Bienennest (Öffnung nach Norden, über den Trichter) hinter den Trichter. Links, rechts und hinten Blöcke – "
          "nur vorne bleibt es frei: dort fallen die Waben heraus in den Trichter.", {
    0: """
        ...
        #N#
        .#.
    """}, x0=-1, z0=-1)
f.schritt("Spender auf das Nest, der nach UNTEN zeigt, Schere hinein. Daneben zwei Beobachter, die sich anschauen "
          "(Takt): der Spender versucht dauernd zu scheren – bei vollem Nest fallen 3 Waben heraus. Fehlversuche "
          "kosten die Schere nichts.", {
    1: "DOQ"})
f.schritt("Blumen vor das Nest, Bienen ins Nest (Nest mit Behutsamkeit abbauen, dann sind sie drin).", {
    0: """
        Y.Y
        .X.
    """}, x0=-1, z0=-3)
f.pruefe(boden=GRAS, zeit="day",
         nachher=["kill @e[type=minecraft:bee,x={x},y={y},z={z},distance=..5]",
                  "setblock {x} {y} {z} minecraft:bee_nest[facing=north,honey_level=3]",
                  "item replace block {x} {y+1} {z} container.0 with minecraft:shears",
                  "summon minecraft:bee {x}.5 {y+1} {z-2}.5 {PersistenceRequired:1b,hive_pos:[I;{x},{y},{z}]}",
                  "summon minecraft:bee {x}.5 {y+1} {z-2}.5 {PersistenceRequired:1b,hive_pos:[I;{x},{y},{z}]}",
                  "summon minecraft:bee {x}.5 {y+1} {z-2}.5 {PersistenceRequired:1b,hive_pos:[I;{x},{y},{z}]}"],
         erwartet={"items": {"minecraft:honeycomb": 3}})

f = farm("huehner")
f.zeichen(D=("dispenser", "e"), T="stonecutter", O=("observer", "n"), Q=("observer", "s"),
          L="lava_cauldron", X="chicken")
f.schritt("Unten: zwei Stützblöcke, daneben ein Trichter nach Osten in eine Truhe.", {
    0: "##>C"})
f.schritt("Auf die Stützen einen Trichter nach Osten und einen Spender, der nach Osten zeigt. Auf den unteren Trichter "
          "einen Steinschneider, Glas drumherum (über der Truhe auch). Blöcke um den oberen Trichter. Hinter den "
          "Spender (Norden) zwei Beobachter, die sich gegenseitig anschauen (Takt).", {
    1: """
        ..Q..
        .#OG.
        #>DTG
        .#.G.
    """}, x0=-1, z0=-2)
f.schritt("Kessel auf den Steinschneider und mit Lava füllen. Glaswände 2 hoch um den oberen Trichter.", {
    2: """
        .G...
        G.GL.
        .G...
    """,
    3: """
        .G.
        G.G
        .G.
    """}, x0=-1, z0=-1)
f.schritt("Hühner auf den oberen Trichter: Ihre Eier fallen hinein, der Spender wirft sie auf den Steinschneider. "
          "Küken wachsen dort auf; erwachsene Hühner berühren mit dem Kopf die Lava im Kessel und werden gegart – "
          "das Hühnchen fällt durch den Steinschneider in den Trichter.", {2: "XX"})
f.pruefe(nachher=["kill @e[type=minecraft:chicken,x={x},y={y},z={z},distance=..6]"] +
         ["summon minecraft:chicken {x}.5 {y+2} {z}.5 {PersistenceRequired:1b,EggLayTime:200}"] * 4 +
         ["summon minecraft:chicken {x+2}.5 {y+1}.6 {z}.5 {PersistenceRequired:1b}"],
         erwartet={"items": {"minecraft:cooked_chicken": 1}, "wesen": {"minecraft:chicken": 4}})

f = farm("kuh")
f.zeichen(Z="oak_fence", T="fence_gate", X="cow")
f.schritt("Gehege 3 × 3 mit Zaun rundherum, an einer Seite ein Zauntor.", {
    0: """
        ZZZZZ
        Z...Z
        Z...Z
        Z...Z
        ZZTZZ
    """}, x0=-1, z0=-1)
f.schritt("Zwei Kühe hinein (mit Weizen locken). Füttere beide mit Weizen → Kalb. Erwachsene Kühe bis auf zwei "
          "schlachten.", {0: "X.X"})
f.pruefe(boden=GRAS,
         nachher=["kill @e[type=minecraft:cow,x={x},y={y},z={z},distance=..5]",
                  "summon minecraft:cow {x}.5 {y} {z}.5 {PersistenceRequired:1b,InLove:600}",
                  "summon minecraft:cow {x+2}.5 {y} {z}.5 {PersistenceRequired:1b,InLove:600}"],
         erwartet={"wesen": {"minecraft:cow": 3}})

f = farm("eisen")
f.zeichen(a=("wall_sign", "e"), b=("wall_sign", "w"), k=("white_bed", {"part": "head", "f": "n"}),
          q=("white_bed", {"part": "foot", "f": "n"}), t=("oak_trapdoor", {"half": "bottom", "f": "e"}),
          D="daylight_detector_inv", s=("slab", {"half": "bottom"}), V="villager", Z="zombie")
f.schritt("Unten 4 Trichter (2 × 2), die in eine Truhe im Osten führen.", {
    0: """
        >v.
        >>C
    """})
f.schritt("Wände um die Trichter 4 hoch (über der Truhe Glas). Auf Höhe 2 innen 4 Schilder an die Wände, auf "
          "Höhe 3 eine Lavaquelle – die Schilder halten sie. Ein Golem unten steckt mit dem Kopf in der Lava.", {
    1: """
        .##.
        #..#
        #..G
        .##.
    """,
    2: """
        .##.
        #ab#
        #ab#
        .##.
    """,
    3: """
        .##.
        #L.#
        #..#
        .##.
    """,
    4: """
        .##.
        #..#
        #..#
        .##.
    """}, x0=-1, z0=-1)
f.schritt("Plattform auf Höhe 5: nördlich des Lochs 2 Reihen Blöcke (hier spawnen die Golems), dahinter eine Reihe "
          "Glas (dort spawnen keine). Im Loch 4 Schilder an die Wände.", {
    5: """
        ####
        #GG#
        ####
        ####
        #ab#
        #ab#
        ####
    """}, x0=-1, z0=-4)
f.schritt("Wände 2 hoch um die Plattform (oben Glas). Wasser auf das Glas: es fließt über das Loch und schiebt "
          "jeden Golem hinein – die Schilder halten das Wasser.", {
    6: """
        ####
        #WW#
        #FF#
        #FF#
        #FF#
        #FF#
        ####
    """,
    7: """
        GGGG
        G..G
        G..G
        G..G
        G..G
        G..G
        GGGG
    """}, x0=-1, z0=-4)
f.schritt("Daneben (Osten) der Raum der Dorfbewohner: Boden auf Höhe 7, drei Betten, Wände 2 hoch (oben Glas).", {
    7: """
        #####
        #####
        #####
        #####
    """,
    8: """
        .###.#
        #kkk#.#
        #qqq##
        .###..
    """,
    9: """
        .GGG.G
        G...t.G
        G...tG
        .GGG..
    """}, x0=3, z0=-4)
f.schritt("Zombie-Zelle an der Ostseite: unten und oben eine Stufe (Schatten, sonst verbrennt er). Das Fenster zu "
          "den Dorfbewohnern sind zwei Falltüren nebeneinander (durch Glas sehen sie nichts!); auf jede ein "
          "Tageslichtsensor im Nacht-Modus (einmal anklicken): nachts klappen die Falltüren hoch, die Dorfbewohner "
          "sehen den Zombie nicht und können schlafen.", {
    7: """
        .#
        .s#
        .#
    """,
    10: """
        ..
        Ds
        D.
    """}, x0=7, z0=-4)
f.schritt("Drei Dorfbewohner auf die Betten, einen Zombie (mit Namensschild!) in die Zelle.", {
    8: """
        .....
        .....Z
        .VVV.
    """}, x0=3, z0=-4)
f.pruefe(boden=GRAS, zeit=12500,
         erwartet={"items": {"minecraft:iron_ingot": 1}},
         hoechstens={"wesen": {"minecraft:iron_golem": 1}})

f = farm("xpspawner")
f.zeichen(n="sign", Q="spawner")
frei = ["-" * 9] * 9
f.schritt("Den Raum um den Spawner freilegen: 9 × 9, von einer Ebene UNTER dem Spawner bis 1 darüber. Boden, Wände "
          "und Decke bleiben aus Stein (unter der Erde sind sie schon da). Fackeln nur zum Bauen – später weg.", {
    -1: "\n".join(frei),
    0: "\n".join(frei[:4] + ["----.----"] + frei[5:]),
    1: "\n".join(frei)}, x0=-4, z0=-4)
f.schritt("Vorne (Süden) eine Rinne eine Ebene tiefer über die ganze Breite, in der Mitte dahinter eine Tür "
          "(2 hoch), eine Zelle und ein Spalt.", {
    -2: "---------", }, x0=-4, z0=4)
f.schritt("Tür, Zelle und Spalt ausgraben.", {-2: "-\n-\n-", -1: "-\n-"}, z0=5)
f.schritt("Rand der Wasserebenen: rundherum Stein, damit das Wasser bleibt (unter der Erde meist schon da).", {
    -1: "\n".join(["#" * 11] + ["#.........#"] * 9 + ["#####.#####"]),
    }, x0=-5, z0=-5)
f.schritt("Rand der Rinne.", {-2: "#.........#\n#####.#####"}, x0=-5, z0=4)
f.schritt("Zelle: Wände, Decke, unten ein Schild (hält das Wasser auf), vorne oben ein Block – unten bleibt ein "
          "Spalt.", {
    -3: "###\n###",
    -2: "#n#\n...",
    -1: "#.#\n.#.",
    0: "###"}, x0=-1, z0=6)
f.schritt("Davor ein Loch, 1 tiefer als die Rinne: Hier stehst du und triffst durch den Spalt die Beine der Mobs. "
          "Sie sehen dich nicht und kommen nicht heraus.", {
    -4: ".#.",
    -3: "#-#",
    -2: "#-#"}, x0=-1, z0=8)
f.schritt("Wasser: an der Nordwand eine Reihe Quellen – es fließt genau 7 Blöcke bis zur Kante der Rinne und schiebt "
          "alles hinein. In die beiden Enden der Rinne je eine Quelle, sie schieben zur Tür. Die Mobs spawnen über "
          "dem Wasser (im Wasser selbst spawnt in 26.3 nichts) und fallen hinein.", {
    -1: "\n".join(["WWWWWWWWW"] + ["FFFFFFFFF"] * 7)}, x0=-4, z0=-4)
f.schritt("Quellen an beide Enden der Rinne.", {-2: "WFFFFFFFW"}, x0=-4, z0=4)
f.schritt("Hier stehen (höchstens 16 Blöcke vom Spawner, sonst spawnt nichts).", {-3: "P"}, z0=8)
f.schritt("Spawner (ist schon da).", {0: "Q"})
f.pruefe(boden="minecraft:stone", fuellung="minecraft:stone", erde_bis=4,
         nachher=['setblock {x} {y} {z} minecraft:spawner{SpawnData:{entity:{id:"minecraft:zombie"}}}'],
         bereich=[-1, -2, 6, 1, 0, 6],
         erwartet={"wesen": {"minecraft:zombie": 2}})

# ===================================================================== Mobs
def raster_aus(zellen, x0, z0, x1, z1):
    """Raster-Text aus {(x, z): Zeichen} für x0..x1, z0..z1."""
    return "\n".join("".join(zellen.get((x, z), ".") for x in range(x0, x1 + 1)) for z in range(z0, z1 + 1))


f = farm("mobfarm")
f.zeichen(a=("wall_sign", "e"), b=("wall_sign", "w"))


def kanal_raum(f, n, text_raum):
    """Dunkler Raum n × n (2 hoch) mit 2 breiten Wasserkanälen eine Ebene tiefer in Kreuzform zum Loch in der Mitte.
    Im Wasser spawnt nichts – darum liegen die Kanäle tiefer als der Spawnboden."""
    m = n // 2 - 1                                   # Loch bei m, m+1
    f.schritt(text_raum, {0: "\n".join(["-" * n] * n), 1: "\n".join(["-" * n] * n)})
    kreuz = {(x, z): "-" for x in range(n) for z in range(n) if x in (m, m + 1) or z in (m, m + 1)}
    f.schritt("Kanäle in Kreuzform eine Ebene tiefer ausheben (2 breit, von jeder Wand bis zur Mitte).", {
        -1: raster_aus(kreuz, 0, 0, n - 1, n - 1)})
    f.schritt("In der Mitte ein Loch 2 × 2, 24 Blöcke unter den Kanälen.", {
        y: "--\n--" for y in range(-25, -1)}, x0=m, z0=m)
    f.schritt("Unten 4 Trichter unter den Schacht, sie führen in eine Truhe. Daneben Platz für dich.", {
        -26: ".>v..\n.>>>C",
        -25: "....-\n....-",
        -24: "....-"}, x0=m - 1, z0=m)
    f.schritt("Unter das Loch 4 Schilder an die Schachtwände: Sie halten das Wasser, Monster fallen durch.", {
        -2: "ab\nab"}, x0=m, z0=m)
    wasser = {}
    for x in range(n):
        for z in range(n):
            if (x, z) in kreuz:
                rand = x in (0, n - 1) or z in (0, n - 1)
                wasser[(x, z)] = "W" if rand else "F"
    f.schritt("Wasserquellen an die vier Kanal-Enden an den Wänden: Das Wasser fließt bis über das Loch.", {
        -1: raster_aus(wasser, 0, 0, n - 1, n - 1)})
    f.schritt("Hier unten warten (mindestens 24 Blöcke vom Raumboden, höchstens 32).", {-25: "P"}, x0=m + 3, z0=m)
    return m


kanal_raum(f, 10, "Unter der Erde (oder in einem dunklen Kasten) einen Raum 10 × 10 und 2 hoch ausgraben. Keine "
                  "Fackeln – es muss ganz dunkel sein. Ideal: weit weg von Höhlen, sonst spawnen die Monster dort.")
f.pruefe(boden="minecraft:stone", fuellung="minecraft:stone", erde_bis=3, zeit="day",
         erwartet={"items": {"minecraft:rotten_flesh": 1}})


f = farm("creeper")
f.zeichen(a=("wall_sign", "e"), b=("wall_sign", "w"), T=("oak_trapdoor", {"half": "top"}))
m = kanal_raum(f, 8, "Unter der Erde einen Raum 8 × 8 und 2 hoch ausgraben – ganz dunkel, keine Fackeln.")
ecken = {(x, z): "T" for x in range(8) for z in range(8) if x not in (m, m + 1) and z not in (m, m + 1)}
f.schritt("Über den Spawnboden (überall außer über den Kanälen) Falltüren in die OBERE Hälfte der zweiten Ebene. "
          "Dann bleiben nur 1,8 Blöcke Platz: Creeper (1,7) passen hinein, Zombies und Skelette (fast 2) nicht.", {
    1: raster_aus(ecken, 0, 0, 7, 7)})
f.pruefe(boden="minecraft:stone", fuellung="minecraft:stone", erde_bis=3, zeit="day",
         erwartet={"items": {"minecraft:gunpowder": 1}})


f = farm("gold")
f.zeichen(N="netherrack", E="turtle_egg", O=("oak_trapdoor", {"half": "bottom", "f": "w", "open": True}))
f.schritt("Plattform 9 × 9 aus Netherrack (am besten auf dem Netherdach in einem Nether-Ödland). Beim Feld links "
          "von der Mitte bleibt ein Loch.", {
    -1: "\n".join(["N" * 9] * 4 + ["NNN.NNNNN"] + ["N" * 9] * 4)})
f.schritt("In die Mitte ein Schildkrötenei, an drei Seiten Glas 2 hoch – nur von Westen über das Loch kommt man hin. "
          "Ins Loch eine offene Falltür: Zombifizierte Piglins halten sie für Boden, laufen zum Ei und fallen.", {
    -1: "...\nO..", 0: ".G\n.EG\n.G", 1: ".G\n..G\n.G"}, x0=3, z0=3)
f.schritt("24 Blöcke unter dem Loch ein Trichter (der Fall tötet sie), daneben eine Truhe mit Glas darüber, "
          "Blöcke um den Trichter. Dein Warteplatz daneben.", {
    -25: ".>C#"}, x0=2, z0=4)
f.schritt("Ring um die Landestelle.", {-24: ".#.\n#.G\n.#."}, x0=2, z0=3)
f.schritt("Hier warten (24 Blöcke unter der Plattform – näher spawnt nichts, weiter weg laufen sie nicht herum).",
          {-24: "P"}, x0=5, z0=4)
f.pruefe(dimension="the_nether", hoehe=160, biom="minecraft:nether_wastes", zeit="day",
         erwartet={"items": {"minecraft:gold_nugget": 1}})

f = farm("enderman")
f.zeichen(N="end_stone", Y="rail", M="minecart", X="endermite",
          O=("oak_trapdoor", {"half": "bottom", "f": "n", "open": True}))
f.schritt("Im End, mindestens 128 Blöcke von jeder anderen Insel: Plattform 9 × 9 aus Endstein. In der Mitte bleibt "
          "ein Block stehen, rundherum ein Ring aus 8 Löchern.", {
    -1: "\n".join(["N" * 9] * 3 + ["NNN...NNN", "NNN.N.NNN", "NNN...NNN"] + ["N" * 9] * 3)})
f.schritt("In jedes Loch eine offene Falltür – Endermen halten sie für Boden. Auf den Mittelblock eine Schiene.", {
    -1: "OOO\nO.O\nOOO", 0: "...\n.Y."}, x0=3, z0=3)
f.schritt("Lore auf die Schiene, eine Endermilbe mit Namensschild hinein. Endermen wollen zu ihr und fallen.", {
    0: "M"}, x0=4, z0=4)
f.schritt("Endermilbe in die Lore.", {0: "X"}, x0=4, z0=4)
f.schritt("44 Blöcke unter der Plattform ein Boden 3 × 3: Der Fall tötet die Endermen. Du stehst in der Mitte (dort "
          "fällt keiner hin) und sammelst die Perlen automatisch ein. Für XP: 42 Blöcke tief und selbst zuschlagen.", {
    -45: "###\n###\n###"}, x0=3, z0=3)
f.schritt("Hier stehen.", {-44: "P"}, x0=4, z0=4)
f.pruefe(dimension="the_end", zeit="day",
         nachher=["kill @e[type=minecraft:endermite,x={x},y={y},z={z},distance=..8]",
                  "kill @e[type=minecraft:minecart,x={x},y={y},z={z},distance=..8]",
                  'summon minecraft:minecart {x+4}.5 {y} {z+4}.5 {Passengers:[{id:"minecraft:endermite",'
                  'PersistenceRequired:1b}]}'],
         erwartet={"inventar": {"minecraft:ender_pearl": 1}})

f = farm("hexe")
f.zeichen(a=("wall_sign", "e"))
f.schritt("Hexenhütte abbauen. Ihre Grundfläche ist die Spawn-Box (7 × 9). Stell dich zum Bauen in die Mitte der "
          "früheren Hütte – der Plan legt sich an die Box.", {
    0: "\n".join(["-" * 7] * 9), 1: "\n".join(["-" * 7] * 9)})
f.schritt("Boden 7 × 9 (eine Ebene unter dem früheren Hüttenboden, genau unter der Box) und ein Rand außen herum. "
          "Hinten in der Mitte ein Loch mit einem Schild darin.", {
    -1: "\n".join(["#" * 7] * 8 + ["###.###"])})
f.schritt("Rand.", {0: "\n".join(["#########"] + ["#.......#"] * 9 + ["#########"])}, x0=-1, z0=-1)
f.schritt("Schild ins Loch (hält das Wasser).", {-1: "a"}, x0=3, z0=8)
f.schritt("Wasser: an der Vorderseite eine Reihe Quellen, hinten in den Ecken je eine – alles fließt zum Loch.", {
    0: "\n".join(["WWWWWWW"] + ["FFFFFFF"] * 7 + ["WFFFFFW"])})
f.schritt("Schacht 29 Blöcke tief (Hexen haben 26 Leben), unten Trichter in eine Truhe. Dein Warteplatz daneben.", {
    **{y: "-" for y in range(-29, -1)}}, x0=3, z0=8)
f.schritt("Unten Trichter und Truhe.", {-30: ">C", -29: ".--", -28: "..-"}, x0=3, z0=8)
f.schritt("Hier warten.", {-29: "P"}, x0=5, z0=8)
f.pruefe(zeit="night", welt="struktur",
         bauwerk={"id": "minecraft:swamp_hut", "anker": [3, 3, 4], "suchen": True, "hoehe": 64},
         erwartet={})

f = farm("ertrunkene")
f.zeichen(a=("wall_sign", "e"), b=("wall_sign", "w"), H=("hopper", "d"))
f.schritt("Im Flussbiom ein Becken 6 × 6 bauen: Boden und Wände 2 hoch. In der Mitte des Bodens ein Loch 2 × 2.", {
    -1: "\n".join(["########"] * 3 + ["###..###"] * 2 + ["########"] * 3),
    0: "\n".join(["########"] + ["#......#"] * 6 + ["########"]),
    1: "\n".join(["########"] + ["#......#"] * 6 + ["########"])}, x0=-1, z0=-1)
f.schritt("Vier Schilder ins Loch (halten das Wasser, Ertrunkene fallen durch).", {-1: "ab\nab"}, x0=2, z0=2)
f.schritt("Becken mit Wasser füllen (2 hoch).", {
    0: "\n".join(["WWWWWW"] * 6), 1: "\n".join(["WWWWWW"] * 6)})
f.schritt("Deckel drauf – innen muss es stockdunkel sein, sonst spawnt nichts.", {
    2: "\n".join(["########"] * 8)}, x0=-1, z0=-1)
f.schritt("Schacht 22 Blöcke tief: Ertrunkene kommen mit 1 Leben unten an.", {
    y: "--\n--" for y in range(-22, -1)}, x0=2, z0=2)
f.schritt("Unten 4 Trichter, die über einen Trichter unter dem Spalt in eine Truhe führen. Auf der Truhe stehst du "
          "(eine Ebene tiefer als die Landestelle); der Block über dem Spalt schützt dich – du triffst ihre Beine, "
          "sie dich nicht.", {
    -24: "...>C",
    -23: ".>>H-\n.^^..",
    -22: "...--"}, x0=1, z0=2)
f.schritt("Hier stehen und zuschlagen (Dreizacke gibt es nur, wenn du triffst).", {-23: "P"}, x0=5, z0=2)
f.pruefe(biom="minecraft:river", boden=GRAS, zeit="day", bereich=[2, -22, 2, 3, -20, 3],
         erwartet={"wesen": {"minecraft:drowned": 1}})

f = farm("aussenposten")
f.zeichen(K="campfire", O=("oak_trapdoor", {"half": "bottom", "f": "n", "open": True}),
          S=("oak_trapdoor", {"half": "bottom", "f": "n"}))
gruben = {}
for gx, gz in ((0, -9), (0, 9), (-9, 0), (9, 0)):
    gruben[(gx, gz)] = True
f.schritt("Um den Turm herum 4 Gruben (je 9 Blöcke von der Mitte): 3 tief ausheben, daneben Platz für eine Truhe.", {
    -3: raster_aus({(x + d, z): "-" for x, z in gruben for d in (0, 1)}, -9, -9, 10, 9),
    -2: raster_aus({(x + d, z): "-" for x, z in gruben for d in (0, 1)}, -9, -9, 10, 9),
    -1: raster_aus({(x + d, z): "-" for x, z in gruben for d in (0, 1)}, -9, -9, 10, 9)}, x0=-9, z0=-9)
f.schritt("Unten in jede Grube einen Trichter nach Osten in eine Truhe, auf den Trichter ein Lagerfeuer, oben "
          "eine offene Falltür. Plünderer halten sie für Boden, fallen hinein und verbrennen.", {
    -3: raster_aus({**{(x, z): ">" for x, z in gruben}, **{(x + 1, z): "C" for x, z in gruben}}, -9, -9, 10, 9),
    -2: raster_aus({(x, z): "K" for x, z in gruben}, -9, -9, 10, 9),
    -1: raster_aus({**{(x, z): "O" for x, z in gruben}, **{(x + 1, z): "S" for x, z in gruben}}, -9, -9, 10, 9)},
    x0=-9, z0=-9)
f.schritt("Vom Turm aus eine Säule hoch bauen und oben warten: 28 Blöcke über dem Boden (näher spawnt nichts, "
          "weiter weg laufen sie nicht herum).", {27: "G", 28: "P"})
f.pruefe(boden=GRAS, zeit="day", welt="struktur",
         bauwerk={"id": "minecraft:pillager_outpost", "anker": [0, 10, 0], "suchen": True, "hoehe": 72},
         erwartet={"items": {"minecraft:arrow": 1}})

f = farm("lohe")
f.zeichen(Q="spawner")
f.schritt("Den Raum um den Lohen-Spawner freilegen: 9 × 9, vom Boden unter dem Spawner bis 2 darüber. Wände, Boden "
          "und Decke bleiben (oder aus Netherziegeln ergänzen) – so fliegen die Lohen nicht weg.", {
    **{y: "\n".join(["---------"] * 4 + ["----.----"] + ["---------"] * 4) if y == 0 else
       "\n".join(["---------"] * 9) for y in range(-1, 3)}}, x0=-4, z0=-4)
f.schritt("Rand rundherum.", {y: "\n".join(["###########"] + ["#.........#"] * 9 + ["###########"])
                            for y in range(-1, 3)}, x0=-5, z0=-5)
f.schritt("Spawner (ist schon da). Stell dich in eine Ecke, Trank der Feuerresistenz trinken, mit Schwert "
          "(Plünderung) zuschlagen – Lohenruten gibt es nur, wenn du triffst.", {0: "Q"})
f.schritt("Hier stehen.", {-1: "P"}, x0=-4, z0=-4)
f.pruefe(boden="minecraft:nether_bricks", fuellung="minecraft:nether_bricks", erde_bis=4,
         nachher=['setblock {x} {y} {z} minecraft:spawner{SpawnData:{entity:{id:"minecraft:blaze"}}}'],
         erwartet={"wesen": {"minecraft:blaze": 2}})

f = farm("witherskelett")
f.zeichen(N="nether_bricks")
f.schritt("In der Netherfestung eine Fläche 9 × 9 aus Netherziegeln (Boden), darüber 3 Blöcke frei – "
          "Wither-Skelette sind 2,4 hoch. Kein Licht.", {
    -1: "\n".join(["N" * 9] * 9), 0: "\n".join(["-" * 9] * 9), 1: "\n".join(["-" * 9] * 9),
    2: "\n".join(["-" * 9] * 9)})
f.schritt("24–32 Blöcke weg warten (näher spawnt nichts), ab und zu hingehen und mit Plünderung III kämpfen.", {
    0: "P"}, x0=4, z0=-22)
f.pruefe(dimension="the_nether", zeit="day", welt="struktur",
         bauwerk={"id": "minecraft:fortress", "anker": [4, 1, 4], "suchen": True, "hoehe": 64},
         erwartet={"wesen": {"minecraft:wither_skeleton": 1}})

f = farm("schleim")
f.schritt("Einen Schleim-Chunk finden (Chunkbase oder Schleime unter Y 40). Den ganzen Chunk (16 × 16) unter Höhe 40 "
          "3 Blöcke hoch ausgraben – Licht ist egal.", {y: "\n".join(["-" * 16] * 16) for y in range(0, 3)})
f.schritt("24–32 Blöcke weg warten (z. B. darüber), dann runter und die Schleime erschlagen.", {25: "P"}, x0=8, z0=8)
f.pruefe(boden="minecraft:stone", fuellung="minecraft:stone", erde_bis=4, ursprung=[6400, 4016],
         erwartet={"wesen": {"minecraft:slime": 1}})

f = farm("ueberfall")
f.zeichen(k=("white_bed", {"part": "head", "f": "n"}), q=("white_bed", {"part": "foot", "f": "n"}), V="villager")
f.schritt("Weit weg von Dörfern: ein Bett in eine kleine Glaszelle – mit einem Dorfbewohner darin ist hier ein "
          "„Dorf“. Wände 2 hoch, Deckel drauf.", {
    0: ".G.\nGkG\nGqG\n.G.", 1: ".G.\nG.G\nG.G\n.G.", 2: "...\n.G.\n.G."}, x0=-1, z0=-2)
f.schritt("Turm daneben: 5 Blöcke hoch, oben eine Plattform 3 × 3 mit Rand – von hier schießt du mit Armbrust "
          "oder Bogen, die Plünderer kommen nicht hinauf.", {
    **{y: "#" for y in range(0, 5)},
    5: "###\n###\n###", 6: "#.#\n...\n#.#"}, x0=3, z0=0)
f.schritt("Dorfbewohner ins Bett bringen. Unheilvolle Flasche trinken, herkommen – nach 30 s beginnt der Überfall.", {
    0: "V"}, z0=0)
f.schritt("Hier stehen.", {6: "P"}, x0=4, z0=1)

f = farm("waechter")
f.schritt("Über dem Ozeanmonument an der Wasseroberfläche eine kleine Plattform 3 × 3 bauen (auf Säulen vom "
          "Monument-Dach oder schwimmend). Wächter kommen zu dir hoch – mit Dreizack oder Schwert zuschlagen.", {
    -1: "###\n#.#\n###"}, x0=-1, z0=-1)
f.schritt("Hier stehen – in der Mitte ist ein Loch ins Wasser, durch das du nach unten schlägst.", {0: "P"}, x0=1)

# ===================================================================== Handel
f = farm("handel")
f.zeichen(T="fletching_table", V="villager")
f.schritt("Hinten 4 Arbeitsblöcke (z. B. Bognertische) mit Lücken dazwischen, Trennblöcke 2 hoch.", {
    0: """
        .T.T.T.T.
        #.#.#.#.#
    """,
    1: """
        .........
        #.#.#.#.#
    """}, x0=-1, z0=-1)
f.schritt("Auf die Arbeitsblöcke je einen Block, vorne eine Reihe Blöcke auf Kopfhöhe – unten bleibt eine Lücke zum "
          "Handeln (der Dorfbewohner passt nicht durch).", {
    1: """
        .#.#.#.#.
        .........
        #########
    """}, x0=-1, z0=-1)
f.schritt("Je einen Dorfbewohner hinein. Passt der Handel nicht: Arbeitsblock abbauen und neu setzen (vor dem "
          "ersten Handel).", {
    0: "V.V.V.V"})
f.pruefe(boden=GRAS, erwartet={"wesen": {"minecraft:villager": 4}})

# ===================================================================== Blöcke
f = farm("bruchstein")
f.zeichen(K="cobblestone")
f.schritt("Graben 4 lang und 1 tief ausheben, beim dritten Block ein Loch, einen Block tiefer.", {
    -2: "..-.",
    -1: "----"})
f.schritt("ZUERST das Wasser ans Ostende: Es fließt ins Loch und bleibt dort – so kommt es nie an die Lavaquelle "
          "(Wasser auf Lavaquelle = Obsidian).", {
    -2: "..F.",
    -1: "..FW"})
f.schritt("DANACH die Lava ans Westende. Wo die fließende Lava das Wasser trifft, entsteht Bruchstein – abbauen, er "
          "kommt sofort neu.", {
    -1: "LK"})
f.pruefe(boden=GRAS, erwartet={"bloecke": {"minecraft:cobblestone": 1}})

f = farm("lava")
f.zeichen(O="cauldron", T="pointed_dripstone")
f.schritt("4 Kessel in eine Reihe, an beiden Enden ein Pfeiler aus 5 Blöcken.", {
    0: "#OOOO#",
    1: "#....#",
    2: "#....#",
    3: "#....#",
    4: "#....#"}, x0=-1)
f.schritt("Auf Höhe 3 eine Reihe Blöcke zwischen den Pfeilern.", {3: "####"})
f.schritt("Unter jeden dieser Blöcke einen Spitzen Tropfstein (Spitze nach unten) – über jedem Kessel einer.", {
    2: "TTTT"})
f.schritt("Auf Höhe 4 links und rechts der Reihe Blöcke als Rand, dann eine Lavaquelle über jeden Tropfstein.", {
    4: """
        ####
        LLLL
        ####
    """}, z0=-1)
f.pruefe(boden=GRAS, erwartet={"bloecke": {"minecraft:lava_cauldron": 1}})

f = farm("schnee")
f.zeichen(X="snow_golem")
f.schritt("Kammer aus Glas um einen Platz: hinten und seitlich 2 hoch, vorne nur oben (unten bleibt die Lücke zum "
          "Abbauen), Glasdach (Regen schadet dem Golem).", {
    0: """
        .G.
        G.G
        ...
    """,
    1: """
        .G.
        G.G
    """,
    2: """
        ...
        .G.
        .G.
    """}, x0=-1, z0=-1)
f.schritt("Vorne ein Glas oben unter das Dach hängen – unten bleibt die Lücke.", {1: "G"}, z0=1)
f.schritt("Schneegolem hinein bauen (2 Schneeblöcke + geschnitzter Kürbis). Unter ihm bildet sich Schnee – durch die "
          "Lücke mit der Schaufel abbauen, er kommt sofort neu.", {0: "X"})
f.pruefe(boden=GRAS, biom="minecraft:snowy_plains", erwartet={"bloecke": {"minecraft:snow": 1}})

f = farm("angeln")
f.schritt("Becken 5 × 5 und 2 tief ausheben.", {
    -2: "\n".join(["-----"] * 5),
    -1: "\n".join(["-----"] * 5)})
f.schritt("Mit Wasser füllen (Tipp: Ecken und Mitte füllen, der Rest wird von selbst zu Quellen). Darüber 2 Blöcke "
          "frei lassen – so zählt es als „offenes Wasser“ und du angelst auch Schätze.", {
    -2: "\n".join(["WWWWW"] * 5),
    -1: "\n".join(["WWWWW"] * 5)})
f.schritt("Davor stehen und in die Mitte angeln.", {0: "P"}, x0=2, z0=5)

f = farm("stockcrafter")
f.zeichen(X="crafter", H=("hopper", "d"), O=("observer", "e"), Q=("observer", "w"))
f.schritt("Truhe auf den Boden, darauf ein Crafter mit der Vorderseite nach UNTEN (beim Setzen nach oben schauen).", {
    0: "C",
    1: "X"})
f.schritt("Trichter auf den Crafter, der nach unten zeigt – hier kommt der Bambus hinein.", {2: "H"})
f.schritt("Zwei Beobachter neben den Crafter, die sich gegenseitig anschauen (Takt): der erste schaut vom Crafter "
          "weg nach Osten, der zweite zurück nach Westen.", {1: ".OQ"})
f.pruefe(nachher=["data merge block {x} {y+1} {z} {disabled_slots:[I;1,2,4,5,6,7,8]}",
                  "item replace block {x} {y+2} {z} container.0 with minecraft:bamboo 64",
                  "item replace block {x} {y+2} {z} container.1 with minecraft:bamboo 64"],
         erwartet={"items": {"minecraft:stick": 8}})

if __name__ == "__main__":
    if "--material" in sys.argv:
        for f in Farm.alle:
            print(f.id, f.material())
    else:
        p, t = schreiben(reihenfolge=REIHENFOLGE)
        print(len(p), "Farmen,", len(t), "Tests")
