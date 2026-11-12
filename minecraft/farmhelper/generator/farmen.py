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
f.schritt("Glasstange auf Höhe 1 über der südlichen Rinne: links neben der Rinne ein Glas auf den Boden, darauf die "
          "Stange nach Osten. Wächst ein Kaktus auf 2 Blöcke, berührt er das Glas und bricht ab.", {
    0: """
        G
    """,
    1: """
        GGGGGGG
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
f.schritt("Zuerst die Kolben, die nach UNTEN zeigen: An das Westende einen Stützblock 2 hoch, dann stellst du dich in "
          "den Graben, schaust nach oben und setzt die 4 Kolben in einer Reihe (Kolben zeigen zu dir).", {
    0: "#",
    1: "#KKKK"}, x0=-1, z0=2)
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
    """}, x0=-1)
f.schritt("Melonen- oder Kürbiskerne auf den Ackerboden.", {
    0: """
        ....
        TTTT
    """})
f.schritt("Über den zweiten Stängel ein Beobachter, der nach UNTEN schaut, darauf ein Block. Redstone-Staub auf die "
          "Kolben – ändert sich der beobachtete Stängel (er wächst oder bekommt eine Frucht), fahren alle Kolben aus "
          "und zerbrechen die Früchte, die gerade da sind.", {
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
f.schritt("Hinter die Kolben Blöcke mit Redstone-Staub darauf. Obere Reihe der Nordwand aus Beobachtern, die nach "
          "Süden auf den obersten Seetang schauen (einer pro Pflanze – sonst kann ein Seetang, der zu früh "
          "ausgewachsen ist, die Farm anhalten). Über den Trichtern ein Rand, vom Glas am Ostende aus gebaut.", {
    1: """
        .######.
    """,
    2: """
        .RRRRRR.
        #BBBBBB#
        #......#
        #......G
        .#######
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
f.zeichen(A="farmland", O="composter", Z="oak_fence", T="fence_gate", V="villager", Q="wheat")
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
        ZZTZZZ
    """,
    1: """
        ......
        ......
        #.....
    """}, x0=-1, z0=-1)
f.schritt("Weizen säen. Dann einen Dorfbewohner durchs Zauntor bringen – vorher (auf normalem Boden, nicht auf dem "
          "Feld!) wirfst du ihm einen Stapel Karotten oder Kartoffeln zu: Auf dem Feld würden die Trichter sie "
          "schneller schlucken. Mit dem Komposter wird er Bauer, erntet und pflanzt mit seinem Vorrat nach.", {
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
f.schritt("Freier Platz mit Gras oder Erde, nach oben mindestens 10 Blöcke frei. 4 Setzlinge der Dunklen Eiche im "
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
f.zeichen(D=("dispenser", "w"), U="stone_button", Y="tall_flower")
f.schritt("Eine hohe Blume (Sonnenblume, Flieder, Rosenstrauch oder Pfingstrose) auf Gras pflanzen.", {0: "Y"})
f.schritt("Daneben einen Spender, der zur Blume zeigt, Knochenmehl hinein, Knopf oben drauf. Jeder Druck lässt die "
          "Blume eine Kopie fallen – sie selbst bleibt stehen. Aufsammeln von Hand (Farbstoffe!).", {
    0: ".D", 1: ".U"})
f.pruefe(boden=GRAS,
         nachher=["setblock {x} {y} {z} minecraft:sunflower[half=lower]",
                  "setblock {x} {y+1} {z} minecraft:sunflower[half=upper]",
                  "item replace block {x+1} {y} {z} container.0 with minecraft:bone_meal 64",
                  "setblock {x+1} {y} {z-1} minecraft:observer[facing=north]",
                  "setblock {x+1} {y} {z-2} minecraft:observer[facing=south]"],
         erwartet={"bloecke": {"minecraft:sunflower": 1}},          # Blume steht noch
         hoechstens={"items": {"minecraft:bone_meal": 0}})          # jedes Knochenmehl hat eine Blume abgeworfen

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
f.zeichen(N=("bee_nest", "n"), D=("dispenser", "w"), O=("observer", "e"), Q=("observer", "w"), Y="poppy",
          X="bee")
f.schritt("Ausheben: vor dem Nest ein Loch für einen Trichter, daneben eins für die Truhe.", {-1: "--"}, z0=-1)
f.schritt("Trichter nach Osten in die Truhe.", {-1: ">C"}, z0=-1)
f.schritt("Bienennest hinter den Trichter, die Öffnung zeigt zum Trichter (Norden). Links ein Block, hinten ein Block, "
          "oben ein Block – rechts (Osten) ein Spender, der aufs Nest zeigt, Schere hinein.", {
    0: """
        ...
        #ND
        .#.
    """,
    1: """
        ...
        .#.
    """}, x0=-1, z0=-1)
f.schritt("Hinter den Spender zwei Beobachter, die sich anschauen (Takt): der Spender versucht dauernd zu scheren – "
          "bei vollem Nest fallen 3 Waben vorne heraus in den Trichter. Fehlversuche kosten die Schere nichts.", {
    0: "OQ"}, x0=2)
f.schritt("Blumen vor das Nest, Bienen ins Nest (Nest mit Behutsamkeit abbauen, dann sind sie drin).", {
    0: """
        Y.Y
        .X.
    """}, x0=-1, z0=-3)
f.pruefe(boden=GRAS, zeit="day",
         nachher=["kill @e[type=minecraft:bee,x={x},y={y},z={z},distance=..5]",
                  "setblock {x} {y} {z} minecraft:bee_nest[facing=north,honey_level=3]",
                  "item replace block {x+1} {y} {z} container.0 with minecraft:shears",
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
          "das Hühnchen fällt durch den Steinschneider in den Trichter. Tipp: Eier in den Schacht werfen.", {2: "X"})
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
f.schritt("Daneben (Osten) der Raum der Dorfbewohner: Boden auf Höhe 7, drei Betten, Wände 3 hoch (unten Stein, "
          "darüber Glas) und ein Glasdach – sonst stellt das Spiel einen Dorfbewohner beim Aufwachen auch mal "
          "neben das Bett auf die Wand.", {
    7: "\n".join(["#####"] * 4),
    8: """
        ######
        #kkk#.#
        #qqq##G
        #####
    """,
    9: """
        GGGGGG
        G...t.G
        G...tG
        GGGGG
    """,
    10: """
        GGGGG
        G...D
        G...D
        GGGGG
    """,
    11: "\n".join(["GGGGG"] * 4)}, x0=3, z0=-4)
f.schritt("Zombie-Zelle an der Ostseite: unten und oben eine Stufe (Schatten, sonst verbrennt er). Das Fenster zu "
          "den Dorfbewohnern sind zwei Falltüren nebeneinander (durch Glas sehen sie nichts!), darüber je ein "
          "Tageslichtsensor im Nacht-Modus (einmal anklicken): nachts klappen die Falltüren hoch, die Dorfbewohner "
          "sehen den Zombie nicht und können schlafen.", {
    7: """
        .#
        .s#
        .#
    """,
    10: """
        ..
        .s
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
f.zeichen(n="sign", Q="spawner", H=("hopper", "s"))
frei = ["-" * 9] * 9
f.schritt("Den Raum um den Spawner freilegen: 9 × 9, von zwei Ebenen UNTER dem Spawner bis 1 darüber. Boden, Wände "
          "und Decke bleiben aus Stein (unter der Erde sind sie schon da). Fackeln nur zum Bauen – später weg.", {
    -2: "\n".join(frei), -1: "\n".join(frei),
    0: "\n".join(frei[:4] + ["----.----"] + frei[5:]),
    1: "\n".join(frei)}, x0=-4, z0=-4)
f.schritt("Vorne (Süden) eine Rinne eine Ebene tiefer über die ganze Breite.", {-3: "---------"}, x0=-4, z0=4)
f.schritt("Mitten dahinter Tür (2 hoch), Zelle, Spalt und dein Platz ausgraben, dazu eine Treppe für dich.", {
    -4: ".\n.\n-\n-", -3: "-\n-\n-\n-", -2: "-\n-\n.\n-"}, z0=5)
f.schritt("Rand der Wasserebenen: rundherum Stein, damit das Wasser bleibt (unter der Erde meist schon da).", {
    -2: "\n".join(["#" * 11] + ["#.........#"] * 9 + ["#####.#####"])}, x0=-5, z0=-5)
f.schritt("Rand der Rinne.", {-3: "#.........#\n#####.#####"}, x0=-5, z0=4)
f.schritt("Zelle: unter dem Boden ein Trichter, der nach Süden in eine Truhe unter dem Spalt zeigt. Auf den Trichter "
          "ein Schild (hält das Wasser auf), Wände und Decke, vorne über dem Spalt ein Block.", {
    -4: ".H.\n.C.",
    -3: "#n#\n#.#",
    -2: "#.#\n.#.",
    -1: "###"}, x0=-1, z0=6)
f.schritt("Wasser: an der Nordwand eine Reihe Quellen – es fließt genau 7 Blöcke bis zur Kante der Rinne und schiebt "
          "alles hinein. Die Mobs spawnen über dem Wasser (im Wasser selbst spawnt in 26.3 nichts), fallen hinein und "
          "schwimmen unter dem Spawner durch.", {
    -2: "\n".join(["WWWWWWWWW"] + ["FFFFFFFFF"] * 7)}, x0=-4, z0=-4)
f.schritt("Quellen an beide Enden der Rinne – sie schieben zur Tür.", {-3: "WFFFFFFFW"}, x0=-4, z0=4)
f.schritt("Hier stehst du (eine Ebene tiefer als die Mobs) und triffst durch den Spalt ihre Beine; die Beute fällt in "
          "die Truhe neben dir. Höchstens 16 Blöcke vom Spawner, sonst spawnt nichts.", {-4: "P"}, z0=8)
f.schritt("Spawner (ist schon da).", {0: "Q"})
f.pruefe(boden="minecraft:stone", fuellung="minecraft:stone", erde_bis=4,
         nachher=['setblock {x} {y} {z} minecraft:spawner{SpawnData:{entity:{id:"minecraft:zombie"}}}'],
         bereich=[-1, -3, 6, 1, -1, 6],
         erwartet={"wesen": {"minecraft:zombie": 2}})

# ===================================================================== Mobs
def raster_aus(zellen, x0, z0, x1, z1):
    """Raster-Text aus {(x, z): Zeichen} für x0..x1, z0..z1."""
    return "\n".join("".join(zellen.get((x, z), ".") for x in range(x0, x1 + 1)) for z in range(z0, z1 + 1))


f = farm("mobfarm")
f.zeichen(a=("wall_sign", "e"), b=("wall_sign", "w"))


def kanal_raum(f, n, text_raum):
    """Dunkler Raum n × n (2 hoch) mit 2 breiten Kanälen in Kreuzform zum Loch in der Mitte. Im Wasser spawnt nichts,
    und von selbst laufen Monster nicht ins Wasser: Die Kanäle sind 2 tief, unten fließt Wasser, oben liegen offene
    Falltüren – die hält die Wegfindung für Boden, die Monster laufen drauf und fallen hinein. Das Loch ist trocken
    (Falltüren auf Wasserhöhe halten das Wasser), so fallen auch Mobs hinein, die oben schwimmen."""
    m = n // 2 - 1                                   # Loch bei m, m+1
    f.zeichen(N=("oak_trapdoor", {"half": "bottom", "f": "n", "open": True}),
              S=("oak_trapdoor", {"half": "bottom", "f": "s", "open": True}),
              E=("oak_trapdoor", {"half": "bottom", "f": "e", "open": True}),
              V=("oak_trapdoor", {"half": "bottom", "f": "w", "open": True}))
    f.schritt(text_raum, {0: "\n".join(["-" * n] * n), 1: "\n".join(["-" * n] * n)})
    f.schritt("In der Mitte ein Loch 2 × 2 ausheben: 2 tief für die Mitte, darunter der Schacht – zusammen 28 tief.", {
        y: "--\n--" for y in range(-28, 0)}, x0=m, z0=m)
    f.schritt("Gleich jetzt (solange die Kanäle noch nicht gegraben sind, kannst du sie an die Wände klicken): Ins Loch "
              "auf der zweiten Ebene 4 offene Falltüren, Klappe jeweils zur Mitte. Sie halten später das Wasser auf, "
              "aber alles, was das Wasser hineinschiebt, fällt trocken in den Schacht – auch Mobs, die oben "
              "schwimmen.", {-2: "NN\nSS"}, x0=m, z0=m)
    kreuz = {(x, z): "-" for x in range(n) for z in range(n) if (x in (m, m + 1) or z in (m, m + 1))
             and not (m <= x <= m + 1 and m <= z <= m + 1)}
    f.schritt("Kanäle in Kreuzform 2 tief ausheben (2 breit, von jeder Wand bis zum Loch).", {
        -1: raster_aus(kreuz, 0, 0, n - 1, n - 1), -2: raster_aus(kreuz, 0, 0, n - 1, n - 1)})
    f.schritt("Unten 4 Trichter unter den Schacht, sie führen in eine Truhe. Daneben dein Platz – grab dir eine Treppe "
              "hinunter.", {
        -29: ".>v..\n.>>>C",
        -28: "....-\n....-",
        -27: "....-"}, x0=m - 1, z0=m)
    wasser = {(x, z): ("W" if x in (0, n - 1) or z in (0, n - 1) else "F") for (x, z) in kreuz}
    f.schritt("Wasserquellen unten in die vier Kanal-Enden an den Wänden: Das Wasser fließt bis zu den Falltüren im "
              "Loch.", {-2: raster_aus(wasser, 0, 0, n - 1, n - 1)})
    deckel = {}
    for (x, z) in kreuz:
        if wasser[(x, z)] == "W":
            deckel[(x, z)] = "#"                     # über den Quellen: dort hinge ein Mob im stehenden Wasser
        elif x == m:
            deckel[(x, z)] = "E"
        elif x == m + 1:
            deckel[(x, z)] = "V"
        elif z == m:
            deckel[(x, z)] = "S"
        else:
            deckel[(x, z)] = "N"
    f.schritt("Über die Quellen an den Wänden einen Block, in jedes andere Kanalfeld auf Bodenhöhe eine offene Falltür "
              "mit der Klappe an der Kanalwand. Monster halten sie für Boden, laufen drauf und fallen ins Wasser.", {
        -1: raster_aus(deckel, 0, 0, n - 1, n - 1)})
    f.schritt("Hier unten warten (mindestens 24 Blöcke vom Raumboden, höchstens 32).", {-28: "P"}, x0=m + 3, z0=m)
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
f.zeichen(N="netherrack", E="turtle_egg", O=("oak_trapdoor", {"half": "bottom", "f": "e", "open": True}))
f.schritt("Unten (z. B. auf dem Netherdach im Nether-Ödland) ein Trichter in eine Truhe mit Glas darüber, ein Ring "
          "aus Blöcken um den Trichter, daneben dein Platz.", {
    0: ".>C#", 1: "...", }, x0=2, z0=4)
f.schritt("Ring um die Landestelle.", {1: ".#.\n#.G\n.#."}, x0=2, z0=3)
f.schritt("25 Blöcke höher eine Plattform 9 × 9 aus Netherrack (mit einer Gerüst-Säule hochbauen). Genau über dem "
          "Trichter bleibt ein Loch.", {
    25: "\n".join(["N" * 9] * 4 + ["NNN.NNNNN"] + ["N" * 9] * 4)})
f.schritt("In die Mitte ein Schildkrötenei, an drei Seiten Glas 2 hoch – nur von Westen über das Loch kommt man hin. "
          "Ins Loch eine offene Falltür (Klappe nach Westen): Zombifizierte Piglins halten sie für Boden, laufen zum Ei "
          "und fallen 25 Blöcke – tot.", {
    25: "...\nO..", 26: ".G\n.EG\n.G", 27: ".G\n..G\n.G"}, x0=3, z0=3)
f.schritt("Hier warten (25 Blöcke unter der Plattform: näher spawnt nichts, weiter weg laufen sie nicht herum).",
          {1: "P"}, x0=5, z0=4)
f.pruefe(dimension="the_nether", hoehe=135, biom="minecraft:nether_wastes", zeit="day",
         erwartet={"items": {"minecraft:rotten_flesh": 1}})

f = farm("enderman")
f.zeichen(N="end_stone", Y="rail", M="minecart", X="endermite",
          a=("oak_trapdoor", {"half": "bottom", "f": "s", "open": True}),
          b=("oak_trapdoor", {"half": "bottom", "f": "n", "open": True}),
          c=("oak_trapdoor", {"half": "bottom", "f": "e", "open": True}),
          d=("oak_trapdoor", {"half": "bottom", "f": "w", "open": True}))
f.schritt("Im End, mindestens 128 Blöcke von jeder anderen Insel: Plattform 9 × 9 aus Endstein. In der Mitte bleibt "
          "ein Block stehen, rundherum ein Ring aus 8 Löchern.", {
    -1: "\n".join(["N" * 9] * 3 + ["NNN...NNN", "NNN.N.NNN", "NNN...NNN"] + ["N" * 9] * 3)})
f.schritt("In jedes Loch eine offene Falltür, die Klappe an der Außenkante (nicht am Mittelblock) – Endermen halten "
          "sie für Boden. Auf den Mittelblock eine Schiene.", {
    -1: "aaa\nc.d\nbbb", 0: "...\n.Y."}, x0=3, z0=3)
f.schritt("Lore auf die Schiene, eine Endermilbe mit Namensschild hinein. Endermen wollen zu ihr und fallen.", {
    0: "M"}, x0=4, z0=4)
f.schritt("Endermilbe in die Lore.", {0: "X"}, x0=4, z0=4)
f.schritt("44 Blöcke unter der Plattform ein Boden 3 × 3 mit einem Rand: Der Fall tötet die Endermen. Du stehst "
          "in der Mitte (dort fällt keiner hin) und sammelst die Perlen automatisch ein. Bau dir eine Treppe oder "
          "Leiter hinunter.", {
    -45: "###\n###\n###"}, x0=3, z0=3)
f.schritt("Rand um den Boden (die Perlen rollen sonst herunter).", {
    -44: ".###.\n#...#\n#...#\n#...#\n.###."}, x0=2, z0=2)
f.schritt("Hier stehen.", {-44: "P"}, x0=4, z0=4)
f.pruefe(dimension="the_end", zeit="day",
         nachher=["kill @e[type=minecraft:endermite,x={x},y={y},z={z},distance=..8]",
                  "kill @e[type=minecraft:minecart,x={x},y={y},z={z},distance=..8]",
                  'summon minecraft:minecart {x+4}.5 {y} {z+4}.5 {Passengers:[{id:"minecraft:endermite",'
                  'PersistenceRequired:1b}]}'],
         erwartet={"inventar": {"minecraft:ender_pearl": 1}})

f = farm("hexe")
f.zeichen(O=("oak_trapdoor", {"half": "bottom", "f": "e", "open": True}),
          U=("oak_trapdoor", {"half": "bottom", "f": "n", "open": True}))
f.schritt("Hexenhütte abbauen; ihre Grundfläche ist die Spawn-Box (7 × 9). Zum Start des Plans stehst du mit den "
          "Füßen eine Ebene UNTER dem alten Hüttenboden (y 0 hier). Verschiebe den Plan mit den Pfeilen im Plan-Menü, "
          "bis er genau unter der früheren Hütte liegt.", {
    0: "\n".join(["-" * 7] * 9), 1: "\n".join(["-" * 7] * 9)})
f.schritt("Schacht zuerst: In der Mitte der hinteren Kante 33 Blöcke tief graben, unten Trichter in eine Truhe und "
          "dein Platz (Treppe hinunter graben).", {
    **{y: "-" for y in range(-33, 0)}}, x0=3, z0=8)
f.schritt("Unten Trichter und Truhe.", {-34: ">C", -33: ".--", -32: "..-"}, x0=3, z0=8)
f.schritt("Boden 7 × 9 eine Ebene unter deinen Füßen (genau unter der Box) – trocken, hier spawnen die Hexen. In "
          "der Mitte läuft von vorne bis zum Schacht ein Kanal, 2 tief.", {
    -1: "\n".join(["###-###"] * 8 + ["###.###"]),
    -2: "\n".join(["...-..."] * 8)})
f.schritt("Ins Schachtloch auf Kanalhöhe eine offene Falltür (Klappe nach hinten): Sie hält das Wasser, die Hexen "
          "fallen trocken in den Schacht.", {-2: "U"}, x0=3, z0=8)
f.schritt("Wasserquelle vorne in den Kanal – sie fließt genau 7 Blöcke bis zur Falltür.", {
    -2: "\n".join(["W"] + ["F"] * 7)}, x0=3)
f.schritt("Über die Quelle einen Block, über den Kanal offene Falltüren (Klappe an der Kanalwand): Hexen halten sie "
          "für Boden, laufen drauf und fallen hinein.", {-1: "\n".join(["#"] + ["O"] * 7 + ["O"])}, x0=3)
rand = "\n".join(["#########"] + ["#.......#"] * 9 + ["#########"])
f.schritt("Rand rundherum, 2 hoch – über einen Block springen Hexen drüber. Ein Dach (dunkel, sonst spawnen sie nur "
          "nachts) ist optional.", {0: rand, 1: rand}, x0=-1, z0=-1)
f.schritt("Auf deiner Treppe hinunter zur Truhe warten, 26 Blöcke unter den Hexenfüßen: näher als 24 spawnt nichts, "
          "weiter als 32 weg laufen die Hexen nicht herum.", {-26: "P", -25: "-"}, x0=5, z0=8)
f.pruefe(zeit="night", welt="struktur",
         bauwerk={"id": "minecraft:swamp_hut", "anker": [3, 3, 4], "suchen": True, "hoehe": 64},
         erwartet={"items": {"*": 1}})

f = farm("ertrunkene")
f.zeichen(a=("wall_sign", "e"), b=("wall_sign", "w"), H=("hopper", "d"))
f.schritt("Im Flussbiom zuerst den Schacht: 2 × 2, 22 Blöcke tief, unten 4 Trichter, die über einen Trichter unter "
          "einem Spalt in eine Truhe führen. Auf der Truhe stehst du (eine Ebene tiefer als die Landestelle); der Block "
          "über dem Spalt schützt dich – du triffst ihre Beine, sie dich nicht. Treppe hinunter graben.", {
    **{y: "--\n--" for y in range(-22, 0)}}, x0=2, z0=2)
f.schritt("Unten Trichter, Truhe und dein Platz.", {
    -24: "...>C",
    -23: ".>>H-\n.^^..",
    -22: "...--"}, x0=1, z0=2)
f.schritt("Becken 6 × 6: Boden mit dem Loch in der Mitte, Wände 3 hoch.", {
    -1: "\n".join(["########"] * 3 + ["###..###"] * 2 + ["########"] * 3),
    0: "\n".join(["########"] + ["#......#"] * 6 + ["########"]),
    1: "\n".join(["########"] + ["#......#"] * 6 + ["########"]),
    2: "\n".join(["########"] + ["#......#"] * 6 + ["########"])}, x0=-1, z0=-1)
f.schritt("Vier Schilder ins Loch (halten das Wasser, Ertrunkene sinken durch).", {-1: "ab\nab"}, x0=2, z0=2)
f.schritt("Becken 2 hoch mit Wasser füllen – darüber bleibt eine Ebene Luft (sie brauchen Platz zum Spawnen).", {
    0: "\n".join(["WWWWWW"] * 6), 1: "\n".join(["WWWWWW"] * 6)})
f.schritt("Deckel drauf – innen muss es stockdunkel sein, sonst spawnt nichts.", {
    3: "\n".join(["########"] * 8)}, x0=-1, z0=-1)
f.schritt("Hier stehen und zuschlagen (Dreizacke gibt es nur, wenn du triffst).", {-23: "P"}, x0=5, z0=2)
f.pruefe(biom="minecraft:river", boden=GRAS, zeit="day", bereich=[2, -22, 2, 3, -20, 3],
         erwartet={"wesen": {"minecraft:drowned": 1}})

f = farm("aussenposten")
f.zeichen(a=("oak_trapdoor", {"half": "bottom", "f": "s", "open": True}),
          b=("oak_trapdoor", {"half": "bottom", "f": "n", "open": True}),
          c=("oak_trapdoor", {"half": "bottom", "f": "e", "open": True}),
          d=("oak_trapdoor", {"half": "bottom", "f": "w", "open": True}), X="scaffolding")
ring = "---\n-.-\n---"
f.schritt("Neben dem Außenposten (oder an Stelle des abgebauten Turms) um einen Block herum 8 Gruben ausheben, "
          "2 tief – der Block in der Mitte bleibt.", {-1: ring, -2: ring}, x0=-1, z0=-1)
f.schritt("In jede Grube oben eine offene Falltür, die Klappe an der Außenkante (nicht am Mittelblock – sonst laufen "
          "sie auf den Klappen-Kanten bis zur Mitte). Plünderer halten sie für Boden.", {
    -1: "aaa\nc.d\nbbb"}, x0=-1, z0=-1)
f.schritt("Auf den mittleren Block einen Sockel 2 hoch (auf 1 Block springen Plünderer hinauf), darauf einen Turm "
          "aus Gerüst bis 28 hoch – oben wartest du. Durch Gerüst sehen die Plünderer hindurch (durch Erde oder Glas "
          "nicht): Sie sehen dich, rennen zu dir, treten auf die Falltüren und sitzen in der Grube fest. Ab und zu "
          "auf den Sockel hinunter (Gerüst: Schleichen), sie von oben erledigen und wieder hochklettern: Jeder "
          "Hauptmann (Banner) lässt eine Unheilvolle Flasche fallen. Zum Wiederkommen von außen einen Block neben die "
          "Gruben stellen, auf den Sockel springen, Block wieder abbauen.", {
    0: "#", 1: "#", **{y: "X" for y in range(2, 28)}})
f.schritt("Hier oben warten (28 Blöcke hoch: näher spawnt nichts, weiter weg laufen sie nicht herum).", {28: "P"})
f.pruefe(boden=GRAS, zeit="day", welt="struktur",
         bauwerk={"id": "minecraft:pillager_outpost", "anker": [12, 10, 0], "suchen": True, "hoehe": 72},
         bereich=[-1, -2, -1, 1, -1, 1], erwartet={"wesen": {"minecraft:pillager": 1}})

f = farm("lohe")
f.zeichen(Q="spawner", N="nether_bricks")
f.schritt("Den Raum um den Lohen-Spawner freilegen: 9 × 9, vom Boden unter dem Spawner bis 2 darüber.", {
    **{y: "\n".join(["---------"] * 4 + ["----.----"] + ["---------"] * 4) if y == 0 else
       "\n".join(["---------"] * 9) for y in range(-1, 3)}}, x0=-4, z0=-4)
f.schritt("Rundherum Wände aus Netherziegeln, 4 hoch (vieles steht in der Festung schon). Wo kein Boden oder keine "
          "Decke ist, dort auch zumachen – sonst fliegen die Lohen weg.", {
    **{y: "\n".join(["NNNNNNNNNNN"] + ["N.........N"] * 9 + ["NNNNNNNNNNN"]) for y in range(-1, 3)}}, x0=-5, z0=-5)
f.schritt("Spawner (ist schon da). Ein Block der Wand bleibt als Tür; Trank der Feuerresistenz trinken, hinein, mit "
          "dem Schwert (Plünderung) zuschlagen – Lohenruten gibt es nur, wenn du triffst.", {0: "Q"})
f.schritt("Hier stehen.", {-1: "P"}, x0=-4, z0=-4)
f.pruefe(boden="minecraft:nether_bricks", fuellung="minecraft:nether_bricks", erde_bis=5,
         nachher=['setblock {x} {y} {z} minecraft:spawner{SpawnData:{entity:{id:"minecraft:blaze"}}}'],
         erwartet={"wesen": {"minecraft:blaze": 2}})

f = farm("witherskelett")
f.zeichen(N="nether_bricks")
f.schritt("In der Netherfestung eine Fläche 9 × 9 aus Netherziegeln (Boden), darüber 3 Blöcke frei – "
          "Wither-Skelette sind 2,4 hoch. Kein Licht.", {
    -1: "\n".join(["N" * 9] * 9), 0: "\n".join(["-" * 9] * 9), 1: "\n".join(["-" * 9] * 9),
    2: "\n".join(["-" * 9] * 9)})
f.schritt("24–32 Blöcke weg warten (näher spawnt nichts), ab und zu hingehen und mit Plünderung III kämpfen.", {
    0: "P"}, x0=4, z0=-24)
f.pruefe(dimension="the_nether", zeit="day", welt="struktur",
         bauwerk={"id": "minecraft:fortress", "anker": [4, 1, 4], "suchen": True, "hoehe": 64},
         erwartet={"wesen": {"minecraft:wither_skeleton": 1}})

f = farm("schleim")
f.schritt("Einen Schleim-Chunk finden (Chunkbase oder Schleime unter Y 40). Chunk-Grenzen mit F3+G anzeigen und den "
          "Plan mit den Pfeilen im Plan-Menü genau auf den Chunk schieben. Den ganzen Chunk (16 × 16) unter Höhe 40 "
          "3 Blöcke hoch ausgraben und mit Fackeln hell machen: Schleime stört das Licht nicht, andere Monster schon.",
          {y: "\n".join(["-" * 16] * 16) for y in range(0, 3)})
f.schritt("24–32 Blöcke weg warten (z. B. 25 Blöcke darüber in einer kleinen Höhle), dann runter und die Schleime "
          "erschlagen.", {25: "P"}, x0=8, z0=8)
f.pruefe(boden="minecraft:stone", fuellung="minecraft:stone", erde_bis=4, ursprung=[6400, 4016],
         erwartet={"wesen": {"minecraft:slime": 1}})

f = farm("ueberfall")
f.zeichen(k=("white_bed", {"part": "head", "f": "n"}), q=("white_bed", {"part": "foot", "f": "n"}), V="villager")
f.schritt("Weit weg von Dörfern: ein Bett in eine kleine Glaszelle, Wände 3 hoch (auf dem Bett braucht ein "
          "Dorfbewohner 2,5 Blöcke). Mit einem Dorfbewohner darin ist hier ein „Dorf“.", {
    0: ".G.\nGkG\nGqG\n.G.", 1: ".G.\nG.G\nG.G\n.G.", 2: ".G.\nG.G\nG.G\n.G."}, x0=-1, z0=-2)
f.schritt("Dorfbewohner ins Bett bringen, dann das Dach drauf.", {0: "V"}, z0=0)
f.schritt("Dach.", {3: ".G.\nGGG\nGGG\n.G."}, x0=-1, z0=-2)
f.schritt("Turm daneben: 5 Blöcke hoch, oben eine Plattform 3 × 3 mit Rand – von hier schießt du mit Armbrust "
          "oder Bogen, die Plünderer kommen nicht hinauf. Unheilvolle Flasche trinken, herkommen – nach 30 s beginnt "
          "der Überfall.", {
    **{y: "#" for y in range(0, 5)},
    5: "###\n###\n###", 6: "#.#\n...\n#.#"}, x0=3, z0=0)
f.schritt("Hier stehen.", {6: "P"}, x0=4, z0=1)

f = farm("waechter")
f.schritt("Über dem Ozeanmonument an der Wasseroberfläche eine kleine Plattform 3 × 3 bauen (auf Säulen vom "
          "Monument-Dach oder schwimmend). Wächter kommen zu dir hoch – mit Dreizack (Durchbohren) oder Bogen "
          "treffen; hinter einem Block vor ihren Lasern in Deckung gehen.", {
    -1: "###\n#.#\n###"}, x0=-1, z0=-1)
f.schritt("Hier stehen.", {0: "P"}, x0=1)

# ===================================================================== Handel
f = farm("handel")
f.zeichen(T="fletching_table", V="villager")
f.schritt("Hinten 4 Arbeitsblöcke (z. B. Bognertische) mit Lücken dazwischen, Trennblöcke 3 hoch.", {
    0: """
        .T.T.T.T.
        #.#.#.#.#
    """,
    1: """
        .........
        #.#.#.#.#
    """,
    2: """
        .........
        #.#.#.#.#
    """}, x0=-1, z0=-1)
f.schritt("Auf die Arbeitsblöcke je einen Block. Vorne unten und auf Höhe 2 eine Reihe Blöcke – dazwischen bleibt "
          "das Fenster zum Handeln (der Dorfbewohner passt nicht durch).", {
    0: """
        .........
        .........
        #########
    """,
    1: """
        .#.#.#.#.
    """,
    2: """
        .........
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
f.schritt("Kammer aus Glas um einen Platz: hinten und seitlich 2 hoch, vorne bleibt unten eine Lücke.", {
    0: """
        .G.
        G.G
    """,
    1: """
        .G.
        G.G
    """}, x0=-1, z0=-1)
f.schritt("Schneegolem hinein bauen (2 Schneeblöcke + geschnitzter Kürbis).", {0: "X"})
f.schritt("Dach aus Glas (Regen schadet dem Golem), vorne oben ein Glas unters Dach – unten bleibt die Lücke, durch "
          "die du mit der Schaufel die Schneedecke abbaust; sie bildet sich sofort neu.", {
    2: ".\n.\nG\nG", 1: ".\n.\n.\nG"}, z0=-2)
f.schritt("Dach hinten.", {2: "G"}, z0=-1)
f.pruefe(boden=GRAS, biom="minecraft:snowy_plains", erwartet={"bloecke": {"minecraft:snow": 1}})

f = farm("angeln")
f.schritt("Becken 5 × 5 und 2 tief ausheben.", {
    -2: "\n".join(["-----"] * 5),
    -1: "\n".join(["-----"] * 5)})
f.schritt("Mit Wasserquellen füllen (Tipp: im Schachbrettmuster füllen, die Lücken werden von selbst zu Quellen – "
          "fließendes Wasser zählt nicht). Darüber 2 Blöcke frei lassen – so ist es „offenes Wasser“ und du angelst "
          "auch Schätze.", {
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

# ===================================================================== Mechanik-Tests
# Seltene Spawns lassen sich im Zeitraffer schlecht abwarten: Mobs hineinsetzen und prüfen, ob Transport und Tötung
# funktionieren. Die Spawnregeln selbst stehen mit Quelle in den Texten.
def mobs(typ, punkte, extra="PersistenceRequired:1b"):
    return [f"summon minecraft:{typ} {{x{x:+d}}}.5 {{y{y:+d}}} {{z{z:+d}}}.5 {{{extra}}}" for x, y, z in punkte]


[f for f in Farm.alle if f.id == "mobfarm"][0].pruefe_auch(
    "mobfarm_mech", boden="minecraft:stone", fuellung="minecraft:stone", erde_bis=3, zeit="day",
    nachher=mobs("zombie", [(1, 0, 1), (8, 0, 1), (1, 0, 8), (8, 0, 8)]),
    erwartet={"items": {"minecraft:rotten_flesh": 1}})
[f for f in Farm.alle if f.id == "creeper"][0].pruefe_auch(
    "creeper_mech", boden="minecraft:stone", fuellung="minecraft:stone", erde_bis=3, zeit="day",
    nachher=mobs("creeper", [(1, 0, 1), (6, 0, 1), (1, 0, 6), (6, 0, 6)]),
    erwartet={"items": {"minecraft:gunpowder": 1}})
[f for f in Farm.alle if f.id == "hexe"][0].pruefe_auch(
    "hexe_mech", boden=GRAS, zeit="day",
    nachher=mobs("witch", [(1, 0, 1), (5, 0, 2), (3, 0, 5), (1, 0, 6)]),
    hoechstens={"wesen": {"minecraft:witch": 0}})
[f for f in Farm.alle if f.id == "ertrunkene"][0].pruefe_auch(
    "ertrunkene_mech", boden=GRAS, zeit="day", bereich=[2, -22, 2, 3, -20, 3],
    nachher=mobs("drowned", [(0, 0, 0), (5, 0, 0), (0, 0, 5), (5, 0, 5)]),
    erwartet={"wesen": {"minecraft:drowned": 1}})
# Großer Boden mit Mauer drumherum, damit die Plünderer nicht vom Testboden fallen
WEIT = ["forceload add {x-18} {z-18} {x+18} {z+18}",
        "fill {x-16} {y-2} {z-16} {x+16} {y-2} {z+16} minecraft:dirt",
        "fill {x-16} {y-1} {z-16} {x+16} {y-1} {z+16} minecraft:grass_block",
        "fill {x-17} {y-1} {z-17} {x+17} {y+1} {z-17} minecraft:stone_bricks",
        "fill {x-17} {y-1} {z+17} {x+17} {y+1} {z+17} minecraft:stone_bricks",
        "fill {x-17} {y-1} {z-17} {x-17} {y+1} {z+17} minecraft:stone_bricks",
        "fill {x+17} {y-1} {z-17} {x+17} {y+1} {z+17} minecraft:stone_bricks"]
[f for f in Farm.alle if f.id == "aussenposten"][0].pruefe_auch(
    "aussenposten_mech", boden=GRAS, zeit="day", vorher=WEIT,
    nachher=mobs("pillager", [(0, 0, -12), (0, 0, 12), (-12, 0, 0), (12, 0, 0), (9, 0, 9), (-9, 0, -9)],
                 'PersistenceRequired:1b,equipment:{mainhand:{id:"minecraft:crossbow",count:1}}'),
    bereich=[-1, -2, -1, 1, -1, 1], erwartet={"wesen": {"minecraft:pillager": 4}})
[f for f in Farm.alle if f.id == "gold"][0].pruefe_auch(
    "gold_mech", dimension="the_nether", hoehe=135, biom="minecraft:nether_wastes", zeit="day",
    nachher=mobs("zombified_piglin", [(0, 26, 0), (8, 26, 8), (0, 26, 8), (8, 26, 0), (1, 26, 6), (7, 26, 2)]),
    erwartet={"items": {"minecraft:gold_nugget": 1}})


if __name__ == "__main__":
    if "--material" in sys.argv:
        for f in Farm.alle:
            print(f.id, f.material())
    else:
        p, t = schreiben(reihenfolge=REIHENFOLGE)
        print(len(p), "Farmen,", len(t), "Tests")
