"""Wolle-Farm (Profi): 8 Schaf-Zellen wie die einfache Farm nebeneinander (Zellen bei x 0, 2, … 14 auf z 0), dazwischen
Wände aus Erde (wird Gras) mit Glas darüber – so wächst das abgefressene Gras von 12 statt 4 Grasblöcken nach.

Je Zelle: Grasblock (x, 0, 0) über einer Trichterlore auf Schiene (x, -1, 0), Trichterreihe y -2 nach Osten in die Truhe
(15, -2, 0). Beobachter (x, 0, -1) schaut nach Süden aufs Gras, dahinter Block (x, 0, -2) mit Redstone-Staub, Werfer
(x, 1, -1) nach Süden zum Schaf (x, 1, 0). Trennwände bei ungeradem x: Fackel (y 0), Erde (y 1), Glas (y 2); Südwand
z 1: Glas (y 0), Erde (y 1), Glas (y 2).
"""
from profi_basis import *

N = 8                                         # Schafe
XS = [2 * i for i in range(N)]               # Zellen x 0 … 14
OST = 2 * N - 1                              # 15: Ostende (Truhe, letzte Trennwand)


def reihe(zeichen_gerade, zeichen_ungerade, x_von=-1, x_bis=OST):
    """Eine Reihe x_von … x_bis: gerade x (Zellen) bzw. ungerade x (Trennwände)."""
    return "".join(zeichen_gerade if x % 2 == 0 else zeichen_ungerade for x in range(x_von, x_bis + 1))


f = profi("wolle", dict(
    name="Wolle-Farm (Profi)", diff=3, out="Wolle (8 Farben gleichzeitig)",
    where="Auf einer Wiese mit freiem Himmel (Gras rund um die Farm, Platz 19 × 4)",
    afk="Ja (in der Nähe bleiben, Simulationsdistanz)",
    why="Acht Schafe statt einem, jedes in einer eigenen Zelle wie in der einfachen Farm: Grasblock unter dem Schaf, "
        "darunter eine Trichterlore, nördlich ein Beobachter, der aufs Gras schaut, darauf ein Werfer mit Schere. "
        "Frisst das Schaf, wird sein Gras zu Erde, die Wolle wächst nach, der Beobachter meldet den Wechsel und der "
        "Werfer schert. Der Engpass ist das Nachwachsen des Grases: Ein Grasblock begrünt Erde, die höchstens 1 Block "
        "seitlich und bis zu 3 Blöcke tiefer oder 1 Block höher liegt. Darum sind die Wände zwischen und hinter den "
        "Schafen aus Erde, die von selbst zu Gras wird, mit Glas darüber; darunter bleibt der Wiesenboden unter Glas "
        "und Fackeln Gras. So kommen für jedes Schaf 12 Grasblöcke in Frage statt 4 – das Gras ist etwa dreimal so "
        "schnell wieder da, und die Fackeln lassen es auch nachts (fast überall) wachsen. Alle Loren geben über eine Trichterreihe in "
        "eine Truhe ab. Färbst du die Schafe, bekommst du 8 Farben auf einmal.",
    help=[["Werfer schert nicht", "Jeder Beobachter schaut nach Süden aufs Gras (roter Punkt nach Norden), dahinter "
                                  "ein Block mit Redstone-Staub; der Werfer steht auf dem Beobachter und zeigt nach "
                                  "Süden zum Schaf. In jeden Werfer eine Schere – Fehlversuche nutzen sie nicht ab."],
          ["Gras wächst langsam nach", "Die Erde in den Wänden wird erst nach und nach grün. Über jeder Erde muss Glas "
                                       "liegen, nie ein fester Block – darunter würde Gras wieder zu Erde. Gras "
                                       "breitet sich nur bei Licht 9 oder heller aus."],
          ["Wolle bleibt liegen", "Unter jedem Grasblock muss eine Trichterlore auf der Schiene stehen, darunter die "
                                  "Trichterreihe bis zur Truhe."],
          ["Andere Farben", "Schafe mit Farbstoff färben (Rechtsklick) – die nachwachsende Wolle hat dann diese Farbe. "
                            "Für alle 16 Farben die Reihe einfach verlängern (je Schaf 2 Blöcke)."]],
    meta=m("Rate: etwa 400 Wolle pro Stunde mit 8 Schafen (Schätzung: ein Schaf auf Gras frisst im Schnitt alle 50 "
           "Sekunden (Chance 1/1000 je Tick); mit 12 Grasblöcken rundum ist das Gras nach gut einer Minute zurück; "
           "je Scheren 1–3 Wolle, also etwa 50 pro Schaf und Stunde). Die einfache Farm mit einem Schaf und 4 "
           "Grasblöcken schafft etwa 20 pro Stunde.",
           [("Auf einer Wiese: Erde unter den Schafen wird nur von Gras in der Nähe wieder grün.",
             W + "Tutorial:Wool_farming")],
           [("Werfer mit Schere, Beobachter schaut aufs Gras, Trichterlore unter dem Gras; Schafe fressen mit 1/1000 "
             "je Tick.", W + "Tutorial:Wool_farming"),
            ("Gras breitet sich auf Erde im Bereich 3 × 5 × 3 aus (bis 3 Blöcke tiefer, 1 höher), wenn über dem "
             "Grasblock Licht 9 oder mehr ist; unter Glas und Fackeln bleibt Gras.", W + "Grass_Block#Post-generation"),
            ("Fehlversuche (Schaf ohne Wolle) nutzen die Schere nicht ab.", W + "Shears"),
            ("Eine Zelle (Beobachter, Staub, Werfer, Trichterlore unter dem Gras): in der einfachen Farm auf dem "
             "Testserver (26.3) geprüft.", None)])))

f.zeichen(O=("observer", "s"), D=("dispenser", "s"), A="grass_block", E="grass_block", Y=("rail", {"axis": "x"}),
          Q="hopper_minecart", I="torch", X="sheep")

f.schritt("Ausheben: ein Graben 2 tief und 17 lang von West nach Ost (für Trichter und Loren), das östlichste Loch "
          "bleibt offen – von dort kommst du an die Truhe.", {
    -1: "-" * (OST + 2),
    -2: "-" * (OST + 2)})
f.schritt(f"Unten in den Graben: die Truhe an die vorletzte Stelle im Osten, dann {OST} Trichter nach Osten – "
          "schleichend den ersten an die Truhe klicken, jeden weiteren an den vorigen. Glas auf die Truhe.", {
    -1: "." * OST + "G",
    -2: ">" * OST + "C"})
f.schritt("Auf die Trichter abwechselnd eine Schiene und einen Erdblock (schleichend setzen): Schienen unter die "
          "späteren Schafe, Erde dazwischen – sie wird von selbst zu Gras.", {
    -1: reihe("Y", "E", 0, OST - 1)})
f.schritt("Auf jede Schiene eine Trichterlore.", {
    -1: reihe("Q", ".", 0, OST - 1)})
f.schritt("Über jede Lore einen Grasblock (oder Erde, die zu Gras wird). Dazwischen und an beiden Enden je eine "
          "Fackel auf den Boden. Nördlich jedes Grasblocks ein Beobachter, der aufs Gras schaut: aus 2 Blöcken "
          "Abstand von Norden her an die Nordseite des Grasblocks klicken und dabei nach Süden schauen (roter Punkt "
          "zeigt nach Norden). Hinter jeden Beobachter einen Block.", {
    0: "\n".join([reihe("#", "."), reihe("O", "."), reihe("A", "I")])}, x0=-1, z0=-2)
f.schritt("Südwand unten: eine Reihe Glas auf den Boden, direkt südlich von Grasblöcken und Fackeln (17 lang).", {
    0: reihe("G", "G")}, x0=-1, z0=1)
f.schritt("Auf jeden Beobachter einen Werfer, der nach Süden zum Schaf zeigt (ein Werfer zeigt beim Setzen zu dir: "
          "südlich vor der Glasreihe stehen und nach Norden schauen). Redstone-Staub auf jeden Block hinter einem "
          "Beobachter – er schaltet den Werfer davor. In jeden Werfer eine Schere.", {
    1: "\n".join([reihe("R", "."), reihe("D", ".")])}, x0=-1, z0=-2)
f.schritt("Wände aus Erde (sie wird von selbst zu Gras): je eine Trennwand über jede Fackel und auf die Glasreihe "
          "im Süden je einen Erdblock südlich jeder Trennwand. Südlich der Grasblöcke bleibt die Südwand noch offen – "
          "dort kommen die Schafe hinein.", {
    1: "\n".join([reihe(".", "E"), reihe(".", "E")])}, x0=-1, z0=0)
f.schritt("Glas oben drauf: auf jeden Werfer, jede Trennwand und jeden Erdblock der Südwand – unter Glas bleibt Gras "
          "grün, und die Schafe kommen nicht über die Wand.", {
    2: "\n".join([reihe("G", "."), reihe(".", "G"), reihe(".", "G")])}, x0=-1, z0=-1)
f.schritt("Schafe hinein: je ein Schaf mit Weizen von Süden über die Glasreihe auf einen Grasblock locken (nach Wunsch "
          "vorher färben) und die Lücke gleich schließen – Erde auf das Glas, Glas darauf. Frisst ein Schaf Gras, "
          "merkt es der Beobachter und der Werfer schert es.", {
    1: "\n".join([reihe("X", "."), reihe("E", ".")]),
    2: "\n".join([reihe(".", "."), reihe("G", ".")])}, x0=-1, z0=0)
f.schritt("Dein Platz am Ostende neben dem Truhenloch – Gras wächst und Schafe fressen nur, wenn du in der Nähe "
          "bist.", {0: "P"}, x0=OST + 2)

f.pruefe(boden=GRAS,
         nachher=[f"item replace block {{x+{x}}} {{y+1}} {{z-1}} container.0 with minecraft:shears" for x in XS] +
         ["kill @e[type=minecraft:sheep,x={x},y={y},z={z},distance=..20]"] +
         mobs("sheep", [(x, 1, 0) for x in XS], "PersistenceRequired:1b,Sheared:1b"),
         erwartet={"items": {"minecraft:white_wool": 100}})
