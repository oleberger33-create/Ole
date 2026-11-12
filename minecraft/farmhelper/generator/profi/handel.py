"""Handelshalle (Profi): 16 Dorfbewohner in 1 × 1-Zellen, zwei Reihen an einem überdachten, beleuchteten Gang.

Gang z 0 (x 0 … 14, 2 hoch, Dach y 2), Eingang im Osten (15, 0, 0) mit Zauntor. Zellen bei geraden x (0, 2, … 14) in
z -2 (Nordreihe) und z 2 (Südreihe); dazwischen Trennwände (ungerade x) 2 hoch. Vor jeder Zelle (z ±1): unten der
Arbeitsblock (Theke), darüber eine Stufe in der OBEREN Blockhälfte – es bleibt ein Schlitz von einem halben Block zum
Handeln, und auch ohne Arbeitsblock ist die Öffnung nur 1,5 hoch (Dorfbewohner: 1,95). Hinter jeder Zelle (z ±3) Glas:
Daran bleibt eine Lore stehen (an undurchsichtigen Blöcken prallt sie zurück). Auf dem Zellenboden eine Schiene: Auf
Schienen spawnt nichts, und sie ist das Ende der Ladespur. Dach y 2 über allem (x -1 … 15, z -3 … 3), zwei Leuchtblöcke im
Gangdach (3, 2, 0) und (11, 2, 0). Blitzableiter auf einer Säule mitten auf dem Dach (7, 3 … 5, 0): Ein Blitz dort trifft
Wesen nur bis 3 Blöcke unter der Einschlagstelle (6) – die Dorfbewohner (bis 1,95 hoch) bleiben verschont.
"""
from profi_basis import *

# Zauntor mit Richtung: Ein Zauntor zeigt in deine Blickrichtung; quer zum Gang (Osten) sperrt es die ganze Breite.
GERICHTET_NEU = {"zauntor": ("oak_fence_gate", "#minecraft:fence_gates", "#minecraft:fence_gates", "Zauntor")}

BLOECKE = {
    "arbeitsblock": ("fletching_table",
                     "minecraft:fletching_table|minecraft:lectern|minecraft:composter|minecraft:smoker|"
                     "minecraft:blast_furnace|minecraft:cartography_table|minecraft:brewing_stand|minecraft:barrel|"
                     "#minecraft:cauldrons|minecraft:loom|minecraft:stonecutter|minecraft:smithing_table|"
                     "minecraft:grindstone",
                     "minecraft:fletching_table", "Arbeitsblock (Bognertisch, Lesepult, Komposter …)"),
    "licht": ("glowstone",
              "minecraft:glowstone|minecraft:sea_lantern|minecraft:shroomlight|minecraft:jack_o_lantern|"
              "minecraft:ochre_froglight|minecraft:verdant_froglight|minecraft:pearlescent_froglight",
              "minecraft:glowstone", "Leuchtblock (Leuchtstein, Seelaterne, Kürbislaterne …)"),
    "lightning_rod": ("lightning_rod", "minecraft:lightning_rod", "minecraft:lightning_rod", "Blitzableiter"),
}

GERADE = list(range(0, 15, 2))               # Zellen x 0 … 14
X0, X1 = -1, 15                              # Endwände


def reihe(zellen, trenn, rand="#", tor="#"):
    """Eine Reihe x -1 … 15: Zeichen für Zellen-x (gerade), Trenn-x (ungerade), Endwand West / Ost."""
    return rand + "".join(zellen if x % 2 == 0 else trenn for x in range(0, 15)) + tor


f = profi("handel", dict(
    name="Handelshalle (Profi)", diff=3, out="Smaragde, verzauberte Bücher, Werkzeuge, Rüstung – 16 Dorfbewohner",
    where="Überall auf ebenem Boden, Platz 17 × 7; nahe einem Dorf oder einer Dorfbewohner-Zucht (Schienenweg bis "
          "zum Eingang)",
    afk="Nein",
    why="16 Dorfbewohner statt 4, jeder in einer 1 × 1-Zelle an einem überdachten, hellen Gang mit Zauntor. Der "
        "Arbeitsblock steht VOR dem Dorfbewohner als Theke, darüber eine Stufe in der oberen Blockhälfte: Durch den "
        "halben Block hohen Schlitz handelst du (schleichend schaust du genau hindurch). Gefällt dir ein Angebot "
        "nicht, baust du den Arbeitsblock vom Gang aus ab und setzt ihn neu – die Öffnung ist dann nur 1,5 Blöcke "
        "hoch, der Dorfbewohner (1,95) kommt trotzdem nicht heraus. In der einfachen Halle steht der Arbeitsblock "
        "unerreichbar hinter ihm. Eingeladen wird mit der Lore: Sie rollt durch den Gang, biegt in die Zelle ab und "
        "bleibt am Glas dahinter stehen. Sicher: Zombies (auch kleine) kommen durch kein Loch, auf den Schienen in "
        "den Zellen und im hellen Gang spawnt nichts, und ein Blitzableiter hoch über dem Dach fängt jeden Blitz im "
        "Umkreis von 128 Blöcken – ein Blitz in der Nähe macht Dorfbewohner sonst zu Hexen. Die Dorfbewohner "
        "füllen ihre Angebote bis zu 2-mal am Tag am Arbeitsblock vor sich auf.",
    help=[["Falsches Angebot", "Solange du noch nicht mit ihm gehandelt hast: Arbeitsblock vom Gang aus abbauen und "
                               "neu setzen, bis das Angebot passt (z. B. Lesepult für ein bestimmtes Buch). Danach "
                               "einmal handeln – dann bleibt es für immer."],
          ["Lore fährt an der Zelle vorbei", "Vor der Zelle (auf dem Platz des Arbeitsblocks) muss eine Schiene "
                                             "liegen, und westlich davon dürfen im Gang keine Schienen mehr liegen. "
                                             "Biegt die letzte Gang-Schiene trotzdem nicht ab: abbauen und neu "
                                             "setzen."],
          ["Angebote bleiben ausverkauft", "Der Arbeitsblock muss direkt vor ihm stehen und ihm gehören (beim Setzen "
                                           "grüne Funken). Aufgefüllt wird tagsüber, höchstens 2-mal am Tag."],
          ["Viel billiger handeln", "Einen Dorfbewohner von einem Zombie anstecken lassen (nur auf Normal oder "
                                    "Schwer) und heilen: Wurftrank der Schwäche, dann Goldener Apfel. Danach sind "
                                    "seine Preise dauerhaft stark gesenkt."]],
    meta=m("Rate: 16 Dorfbewohner mit eigenem Arbeitsblock statt 4 – viermal so viele Angebote, jedes bis zu 2-mal "
           "am Tag aufgefüllt; z. B. kaufen 4 Pfeilmacher zusammen bis zu 128-mal 32 Stöcke für je 1 Smaragd pro "
           "Tag (Schätzung, ohne Preisanstieg durch Nachfrage).",
           [("Überall; die Dorfbewohner kommen aus einem Dorf oder einer Zucht und werden mit der Lore gebracht.",
             W + "Tutorial:Villager_trading_hall")],
           [("Zellen mit Arbeitsblock; neu würfeln durch Abbauen und Setzen, solange nicht gehandelt wurde.",
             W + "Tutorial:Villager_trading_hall#Locking_in_trades"),
            ("Dorfbewohner arbeiten an einem Arbeitsblock direkt neben sich (auch schräg) und füllen bis zu 2-mal "
             "am Tag auf, auch ohne Bett. Ein erwachsener Dorfbewohner ist 1,95 hoch.", W + "Villager"),
            ("Eine Lore hält am Ende der Schiene vor durchsichtigen Blöcken an, vor undurchsichtigen prallt sie "
             "zurück. Mitfahrer ersticken nicht in durchsichtigen Blöcken (Stufe). Mobs steigen nur aus, wenn die "
             "Lore zerstört wird.", W + "Minecart"),
            ("Auf Schienen spawnen keine Monster (Tag prevent_mob_spawning_inside).", W + "Rail"),
            ("Blitz in 3–4 Blöcken Nähe macht Dorfbewohner zu Hexen; ein Blitzableiter als höchster Block fängt "
             "Blitze im Umkreis von 128 Blöcken ab.", W + "Lightning_Rod"),
            ("Heilen eines Zombie-Dorfbewohners senkt die Preise.", W + "Zombie_Villager"),
            (TEST + "einfache Variante: Dorfbewohner bleiben in 1 × 1-Zellen.", None)])))

f.zeichen(A="arbeitsblock", E="licht", B="lightning_rod", V="villager", Y="rail",
          s=("slab", {"half": "top"}), T=("zauntor", "e"))

f.schritt("Grundriss 17 × 7, alle Wände 2 hoch: hinten in beiden Reihen (Norden und Süden) Glas hinter jeder Zelle, "
          "Steinziegel dazwischen und an den Ecken; Endwände im Westen und Osten (im Osten in der Mitte bleibt der "
          "Eingang offen). Dazwischen je 7 Trennwände für die Zellen und vorne zum Gang je 7 Pfeiler – zwischen den "
          "Pfeilern bleiben die Zellen vorne offen.", {
    y: "\n".join([reihe("G", "#"),                  # z -3: Rückwand Nord
                  reihe(".", "#"),                  # z -2: Zellen / Trennwände
                  reihe(".", "#"),                  # z -1: Theke (später) / Pfeiler
                  reihe(".", ".", "#", "."),        # z  0: Gang, Eingang im Osten
                  reihe(".", "#"),                  # z  1
                  reihe(".", "#"),                  # z  2
                  reihe("G", "#")])                 # z  3: Rückwand Süd
    for y in (0, 1)}, x0=X0, z0=-3)
f.schritt("Vor jede Zelle auf Höhe 1 (Kopfhöhe, zwischen zwei Pfeilern) eine Stufe in die OBERE Blockhälfte: an "
          "die obere Hälfte der Seitenfläche eines Pfeilers daneben klicken. Darunter bleibt die Öffnung 1,5 Blöcke "
          "hoch – kein Dorfbewohner passt hindurch, eine Lore schon.", {
    1: reihe("s", ".", ".", ".") + "\n" * 2 + reihe("s", ".", ".", ".")}, x0=X0, z0=-1)
f.schritt("Eine Schiene auf den Boden jeder Zelle (vom Gang aus durch die Öffnung). Auf Schienen spawnen keine "
          "Monster, und hier endet später die Lore.", {
    0: reihe("Y", ".", ".", ".") + "\n" * 4 + reihe("Y", ".", ".", ".")}, x0=X0, z0=-2)
f.schritt("Dach auf Höhe 2 über die ganze Halle, 17 × 7. Über dem Gang an 2 Stellen einen Leuchtblock "
          "(Leuchtstein, Seelaterne, Kürbislaterne …) statt Steinziegel – dann ist der Gang hell genug.", {
    2: "\n".join(["#" * 17] * 3 + ["####E#######E####"] + ["#" * 17] * 3)}, x0=X0, z0=-3)
f.schritt("Blitzableiter: mitten auf dem Dach über dem Gang 2 Steinziegel übereinander, oben drauf der Blitzableiter "
          "(3 Kupferbarren). Er muss der höchste Block weit und breit sein. Ein Blitz trifft Wesen nur bis 3 Blöcke "
          "unter der Einschlagstelle – so hoch erreicht er keinen Dorfbewohner.", {
    3: "#", 4: "#", 5: "B"}, x0=7)
f.schritt("Einladen, Zelle für Zelle, im Westen anfangen: (1) Auf den Platz vor der Zelle (unter der Stufe) eine "
          "Schiene legen. (2) Im Gang Schienen vom Eingang bis vor diese Zelle, weiter westlich keine – die letzte "
          "biegt dann in die Zelle ab. (3) Den Dorfbewohner in einer Lore vom Eingang her schieben: Sie rollt in die "
          "Zelle und bleibt am Glas stehen. (4) Lore durch die Öffnung kaputt schlagen – er steht in der Zelle und "
          "kommt unter der Stufe nicht heraus. (5) Die Schiene vor ihm abbauen und seinen Arbeitsblock dort setzen "
          "(Bognertisch, Lesepult, Komposter …). Dann die Gang-Schienen bis vor die nächste Zelle abbauen. Passt "
          "das Angebot nicht: Arbeitsblock abbauen und neu setzen, bis es passt.", {
    0: "\n".join([reihe("V", ".", ".", "."), reihe("A", ".", ".", "."), "", reihe("A", ".", ".", "."),
                  reihe("V", ".", ".", ".")])}, x0=X0, z0=-2)
f.schritt("Gang-Schienen abbauen und in den Eingang im Osten ein Zauntor setzen: im Gang stehen und nach Osten "
          "schauen. Ein geschlossenes Zauntor ist 1,5 hoch, darüber bleibt bis zum Dach nur ein halber Block – nichts "
          "kommt herein, du machst es einfach auf.", {
    0: "T"}, x0=X1)

f.pruefe(boden=GRAS, erwartet={"wesen": {"minecraft:villager": 16}})
# Schutz: Zombies und kleine Zombies im Gang erreichen die Dorfbewohner nicht (Nacht, die Halle ist überdacht)
f.pruefe_auch("handel_profi_mech", boden=GRAS, zeit="night",
              nachher=mobs("zombie", [(1, 0, 0), (7, 0, 0), (13, 0, 0)]) +
              mobs("zombie", [(4, 0, 0), (10, 0, 0)], "PersistenceRequired:1b,IsBaby:1b"),
              erwartet={"wesen": {"minecraft:villager": 16}},
              hoechstens={"wesen": {"minecraft:zombie_villager": 0, "minecraft:witch": 0}})
