"""Eisenfarm (Profi): zwei getrennte Gruppen aus je 3 Dorfbewohnern, ein gemeinsamer Zombie, eine große
Spawnfläche mit Wasser zur Mitte und ein Fallschacht, der die Golems sofort aus dem 16-Block-Bereich der Dorfbewohner
holt.

Koordinaten (x Ost, z Süd, y 0 = Füße beim Planstart, y -1 = Boden):
- Schacht 2 × 2 bei x 0..1, z 0..1. Unten (y -12) 4 Trichter → Truhe (2, -12, 1), Schilder y -10, Lava y -9.
  Glas (2, -11/-10, 1) über der Truhe = Fenster. Gang mit Treppe nach Osten (z 1) bis an die Oberfläche (x 14).
- Über dem Boden Schachtwände y 0..4, Plattform y 5 (10 × 10, x -4..5, z -4..5, Loch mit 4 Schildern in der Mitte),
  Rand y 6 (Stein) und y 7 (Glas), innen 8 × 8 (x -3..4, z -3..4) Wasser aus 4 Eckquellen (fließt zur Mitte).
- Raum A (Westen) x -7..-4, Raum B (Osten) x 6..9, je z -2..2: Boden y 7, Betten y 8 (Dorfbewohner x -5 bzw. 7,
  z -1..1), Wände y 8..10 mit 3 Fensterlöchern (y 10) zur Mitte, Glasdach y 11. Abstand der Gruppen ≥ 11,6 Blöcke
  (> 10: kein „near a summoning“), jeder Dorfbewohner ≤ 7,5 Blöcke vom Zombie (< 8).
- Zombie-Zelle über dem Loch: Zombie (1, 10, 0) auf Boden (1, 9, 0), Falltür-Fenster (0, 11, 0) und (2, 11, 0) mit
  Tageslichtsensoren (Nacht-Modus) darüber, Einstiegs-Falltür (1, 12, 0), Stufe (1, 13, 0). Steg aus Glas auf y 11
  von Norden (x 1, z -4..-1), Glaspfeiler (1, 8..10, -4) auf dem Nordrand.
"""
from profi_basis import *


def stufe(text, lagen):
    """Bauschritt aus {y: {(x, z): Zeichen}} (ein gemeinsamer Ausschnitt für alle Ebenen)."""
    xs = [x for zellen in lagen.values() for x, _ in zellen]
    zs = [z for zellen in lagen.values() for _, z in zellen]
    x0, z0, x1, z1 = min(xs), min(zs), max(xs), max(zs)
    f.schritt(text, {y: raster_aus(zellen, x0, z0, x1, z1) for y, zellen in lagen.items()}, x0=x0, z0=z0)


def rechteck(x0, z0, x1, z1, c, ohne=()):
    return {(x, z): c for x in range(x0, x1 + 1) for z in range(z0, z1 + 1) if (x, z) not in ohne}


def rand(x0, z0, x1, z1, c):
    return {(x, z): c for (x, z) in rechteck(x0, z0, x1, z1, c) if x in (x0, x1) or z in (z0, z1)}


LOCH = {(0, 0), (1, 0), (0, 1), (1, 1)}                                 # Fallschacht 2 × 2
RING = {(0, -1), (1, -1), (-1, 0), (2, 0), (-1, 1), (2, 1), (0, 2), (1, 2)}   # Schachtwand um das Loch
TREPPE = [(3 + i, -12 + i) for i in range(12)]                          # (x, Fußhöhe) der Treppenstufen, z 1

f = profi("eisen", dict(
    name="Eisenfarm (Profi)", diff=4, out="Eisenbarren, Mohnblumen",
    where="Flaches Gelände ohne Höhlen darunter (13 Blöcke tief graben), mindestens 50 Blöcke weg von Dörfern; "
          "bis 8 Blöcke um die beiden Räume darf nichts höher sein als 1 Block über dem Boden am Startpunkt",
    afk="Ja – irgendwo in Simulationsdistanz, am besten unten an der Truhe",
    why="Zwei Gruppen mit je 3 Dorfbewohnern statt einer – jede ruft ihren eigenen Golem. Eine Gruppe ruft höchstens "
        "alle 30 Sekunden einen Golem und nur, wenn 30 Sekunden lang kein Golem in 16 Blöcken war; jeder "
        "Dorfbewohner in 10 Blöcken um den Rufer wartet danach ebenfalls 30 Sekunden. Darum stehen die Betten der "
        "beiden Gruppen links und rechts 12 Blöcke auseinander (mehr als 10), der Zombie in der Mitte ist für "
        "alle 6 nah genug (unter 8 Blöcken) und durch die Falltür-Fenster seiner Zelle sichtbar. Die Golems "
        "spawnen auf der großen Wasserfläche (8 × 8 statt 4 Blöcke wie bei der einfachen): Fast jeder Versuch "
        "klappt sofort. Das Wasser "
        "aus 4 Eckquellen fließt zur Mitte, dort fällt der Golem durchs Loch 17 Blöcke tief unter die Erde – damit "
        "ist er sofort weiter als 16 Blöcke von den Dorfbewohnern weg, und sie rufen nach 30 Sekunden schon den "
        "nächsten. Unten steckt er mit dem Kopf in der Lava (über Schildern), die Beute fällt in die Trichter und "
        "die Truhe. Nachts klappen die Falltüren an der Zombie-Zelle hoch (Tageslichtsensoren im Nacht-Modus), die "
        "Dorfbewohner sehen den Zombie nicht und schlafen – das brauchen sie alle 20 Minuten.",
    help=[["Keine Golems", "Alle 6 Dorfbewohner müssen in einem Bett geschlafen haben (erst nach der ersten Nacht) "
                           "und den Zombie tagsüber durch die Fensterlöcher und die Falltüren sehen – nicht durch "
                           "Glas. Die Fenster-Falltüren müssen tagsüber zu (flach) sein; die Sensoren einmal "
                           "anklicken (Nacht-Modus). Kein Baby-Zombie: er ist zu klein für das Fenster."],
          ["Zombie hinaufbringen", "Nachts einen Zombie über eine Behelfstreppe (Erde) auf den Steg locken. Die "
                                   "Einstiegs-Falltür über der Zelle ist nachts offen (die Sensoren schalten sie) – "
                                   "spring über die Lücke, der Zombie hält die offene Falltür für Boden, läuft darauf "
                                   "und fällt hinein. Namensschild geben! Dann die Stufe darüber (nie Glas): sonst "
                                   "verbrennt er am Tag."],
          ["Dorfbewohner hinaufbringen", "Mit einer Lore über Schienen (Antriebsschienen) oder einem Wasseraufzug "
                                         "(Seelensand unter Wasserquellen) bis aufs Dach, ein Dachglas über dem Bett "
                                         "kurz abbauen, Dorfbewohner hineinfallen lassen, Glas wieder setzen."],
          ["Golem bleibt stehen oder spawnt woanders", "Lebt in 16 Blöcken ein Golem (auf einem Hügel, Baum oder Dach "
                                                       "in der Nähe), rufen die Dorfbewohner keinen neuen. Rund um "
                                                       "die Farm alles einebnen; bei Regen ruht die Farm (die "
                                                       "Sensoren schließen die Fenster)."]],
    meta=m("Rate: Schätzung etwa 100–300 Eisenbarren pro Stunde (2 Gruppen, je Gruppe tagsüber höchstens alle "
           "35–45 Sekunden ein Golem mit 3–5 Barren; nachts schlafen sie und es kommen keine). Das Wiki nennt für "
           "gute Farmen 240–400 pro Stunde. Die einfache Farm brachte im Test 14 Barren in 30 Minuten.",
           [("Weit weg von Dörfern und deren Golems (16 Blöcke), flach, damit Golems nur auf der Plattform spawnen.",
             W + "Tutorial:Iron_golem_farming")],
           [("Panik-Methode: 3 Dorfbewohner in 10 Blöcken, alle in den letzten 20 Minuten geschlafen, 30 Sekunden "
             "kein Golem in 16 Blöcken, 30 Sekunden kein Ruf in 10 Blöcken; Zombie höchstens 8 Blöcke entfernt.",
             W + "Iron_Golem#Villages"),
            ("Spawnversuch: 10 zufällige Spalten im Bereich 17 × 13 × 17 um den Dorfbewohner, oberster fester Block "
             "mit Luft oder Wasser darüber, nicht Glas; Golem darf in 1 Block Wasser spawnen.",
             W + "Iron_Golem#Villages"),
            ("Ein Fallschacht, in dem die Golems weit genug weg fallen, hebt die Golem-Sperre auf; Wasser zum "
             "Transport, Lava über Schildern zum Töten.", W + "Tutorial:Iron_golem_farming"),
            ("Mobs halten offene Falltüren für Boden; Glas versperrt Dorfbewohnern die Sicht; eine Stufe über dem "
             "Zombie schützt ihn vor der Sonne (auf dem Testserver 26.3 geprüft).", None)])))

f.zeichen(a=("wall_sign", "e"), b=("wall_sign", "w"), j=("wall_sign", "s"), k=("wall_sign", "n"),
          q=("white_bed", {"part": "head", "f": "w"}), r=("white_bed", {"part": "foot", "f": "w"}),
          t=("white_bed", {"part": "head", "f": "e"}), u=("white_bed", {"part": "foot", "f": "e"}),
          T=("oak_trapdoor", {"half": "bottom", "f": "e"}), U=("oak_trapdoor", {"half": "bottom", "f": "w"}),
          E=("oak_trapdoor", {"half": "bottom", "f": "e"}), D="daylight_detector_inv",
          s=("slab", {"half": "bottom"}), V="villager", Z="zombie")

# ------------------------------------------------------------------ unter der Erde
gang = {-12: {(2, 1): "-"}, -11: {(2, 1): "-"}, -10: {(2, 1): "-"}}
for x, y in TREPPE:                                     # Treppe: je Stufe 3 Blöcke hoch frei
    for dy in range(3):
        if y + dy <= -1:
            gang.setdefault(y + dy, {})[(x, 1)] = "-"
stufe("Zuerst der Weg nach unten: 13 Blöcke östlich vom späteren Schacht (rote Felder) eine Treppe nach Westen "
      "graben, 12 Stufen tief (je Stufe 3 hoch frei). Unten 1 Block weiter nach Westen: die Nische für die Truhe "
      "(Höhe -12) und darüber 2 Fensterlöcher (Höhe -11 und -10) – dahinter kommt der Schacht.", gang)
stufe("Den Schacht 2 × 2 von oben 12 tief ausheben (bis Höhe -12), Löcher in den Schachtwänden zumauern. Unten "
      "kommst du durch die Truhennische in den Gang.", {y: {p: "-" for p in LOCH} for y in range(-12, 0)})
stufe("Unten: die Truhe in die Nische, dann 4 Trichter auf den Schachtboden – schleichend den ersten (Südosten) an "
      "die Truhe klicken, den im Nordosten an den Südost-Trichter (zeigt nach Süden), die beiden westlichen an ihren "
      "östlichen Nachbarn. Über die Truhe und die Fensterlöcher kommst du zurück in den Gang.", {
    -12: {(0, 0): ">", (1, 0): "v", (0, 1): ">", (1, 1): ">", (2, 1): "C"}})
stufe("Vom Gang aus durch die Fensterlöcher: 4 Schilder in Höhe -10 an die Nord- und Südwand des Schachts "
      "(schleichend), dann einen Lavaeimer in Höhe -9 in die Nordwest-Ecke gießen (an die Westwand zielen) – die "
      "Lava breitet sich über allen 4 Schildern aus. Ein Golem unten steckt mit dem Kopf darin.", {
    -10: {(0, 0): "j", (1, 0): "j", (0, 1): "k", (1, 1): "k"},
    -9: {(0, 0): "L"}})
stufe("Beide Fensterlöcher mit Glas schließen (über der Truhe muss Glas sein, sonst geht sie nicht auf).", {
    -11: {(2, 1): "G"}, -10: {(2, 1): "G"}})
# ------------------------------------------------------------------ über der Erde
stufe("Schachtwand über dem Boden: um das Loch 8 Blöcke je Ebene, 5 hoch (Höhe 0 bis 4).",
      {y: {p: "#" for p in RING} for y in range(0, 5)})
platte = rechteck(-4, -4, 5, 5, "#", ohne=LOCH)
platte.update({(0, 0): "a", (1, 0): "b", (0, 1): "a", (1, 1): "b"})
stufe("Die Plattform auf Höhe 5: 10 × 10 um das Loch. Ins Loch 4 Schilder an die Wände (schleichend) – sie halten "
      "das Wasser, der Golem fällt hindurch.", {5: platte})
oben = rand(-4, -4, 5, 5, "G")
oben.update({(-4, z): "#" for z in range(-2, 3)})
stufe("Rand 2 hoch: unten Steinziegel, darauf Glas (an der Westseite in der Mitte 5 Steinziegel – dort kommt der "
      "Boden von Raum A hin). Auf Glas spawnen keine Golems, und 2 hoch kommt kein Golem hinaus.", {
    6: rand(-4, -4, 5, 5, "#"), 7: oben})
stufe("Wasser in die 4 inneren Ecken: es fließt bis in die Mitte (dort über den Schildern am flachsten) und schiebt "
      "jeden Golem ins Loch. Die Golems spawnen im Wasser auf der Plattform.", {
    6: {(-3, -3): "W", (4, -3): "W", (-3, 4): "W", (4, 4): "W", **{p: "F" for p in rechteck(-3, -3, 4, 4, "F")
                                                                  if p not in {(-3, -3), (4, -3), (-3, 4), (4, 4)}}}})


def raum(x_wand_aussen, x_innen, x_fenster, kopf, fuss, text):
    """Dorfbewohner-Raum: Wände bei x_wand_aussen und x_fenster, Betten bei x_innen (Kopf, Fuß), z -2..2."""
    xa, xb = sorted((x_wand_aussen, x_fenster))
    boden = rechteck(xa, -2, xb, 2, "#")
    if xa == -7:                                   # Raum A: die Ostreihe (x -4) ist schon der Plattformrand
        boden = {p: c for p, c in boden.items() if p[0] != -4}
    w8 = rand(xa, -2, xb, 2, "#")
    w8.update({(x_innen[0], z): kopf for z in (-1, 0, 1)})
    w8.update({(x_innen[1], z): fuss for z in (-1, 0, 1)})
    w10 = {p: c for p, c in rand(xa, -2, xb, 2, "G").items() if not (p[0] == x_fenster and -1 <= p[1] <= 1)}
    stufe(text, {7: boden, 8: w8, 9: rand(xa, -2, xb, 2, "G"), 10: w10, 11: rechteck(xa, -2, xb, 2, "G")})


raum(-7, (-6, -5), -4, "q", "r",
     "Raum A im Westen auf Höhe 7: Boden 4 × 5, Wand ringsum (unten Steinziegel, darüber 2 Glas), 3 Betten nach "
     "Westen schauend auf den Boden klicken (Kopf im Westen). In die Ostwand oben (Höhe 10) 3 Löcher als Fenster – "
     "durch die Löcher sehen die Dorfbewohner den Zombie, hinaus passen sie nicht. Glasdach darüber.")
raum(9, (8, 7), 6, "t", "u",
     "Raum B im Osten genauso, direkt östlich an den Plattformrand gebaut (Boden 4 × 5 auf Höhe 7): Betten nach "
     "Osten schauend (Kopf im Osten), die 3 Fensterlöcher in der Westwand (Höhe 10). Die inneren Bettenreihen der "
     "beiden Räume liegen 12 Blöcke auseinander – so stört ein Ruf der einen Gruppe die andere nicht.")
stufe("Zombie-Zelle und Steg: auf den Nordrand, in Linie mit der Osthälfte des Lochs, einen Glaspfeiler (Höhe "
      "8–10). Auf Höhe 9 vom Pfeiler aus nach Süden 3 Glas, dann den Zellenboden (Steinziegel, über dem Loch) und "
      "um ihn 3 Glas (Westen, Osten, Süden). Auf das 3. Glas 2 Glas nach oben, und auf Höhe 11 vom Pfeiler aus der "
      "Steg nach Süden. Unter dem Glas auf Höhe 9 passen die Golems im Wasser gerade hindurch.", {
    8: {(1, -4): "G"},
    9: {(1, -4): "G", (1, -3): "G", (1, -2): "G", (1, -1): "G", (1, 0): "#", (0, 0): "G", (2, 0): "G", (1, 1): "G"},
    10: {(1, -4): "G", (1, -1): "G"},
    11: {(1, -4): "G", (1, -3): "G", (1, -2): "G", (1, -1): "G"}})
stufe("Zellenwände auf Höhe 10: Glas im Westen, Osten und Süden, auf das südliche noch eines (Höhe 11). Dann in die "
      "Zelle steigen: nach Westen schauend oben auf das westliche Glas klicken (Falltür, bleibt flach), nach Osten "
      "schauend auf das östliche – das sind die Fenster. Mit einem Hilfsblock wieder hinaus, Hilfsblock abbauen.", {
    10: {(0, 0): "G", (2, 0): "G", (1, 1): "G"}, 11: {(0, 0): "T", (2, 0): "U", (1, 1): "G"}})
stufe("Auf jede Fenster-Falltür schleichend einen Tageslichtsensor und ihn einmal anklicken (Nacht-Modus): nachts "
      "klappen die Falltüren hoch und verdecken den Zombie, die Dorfbewohner schlafen. Zwischen die Sensoren die "
      "Einstiegs-Falltür: schleichend an die Ostseite des westlichen Sensors klicken.", {
    12: {(0, 0): "D", (1, 0): "E", (2, 0): "D"}})
stufe("Dorfbewohner: je 3 auf die Betten in Raum A und Raum B (siehe Hilfe, wie sie hinaufkommen).", {
    8: {(-5, -1): "V", (-5, 0): "V", (-5, 1): "V", (7, -1): "V", (7, 0): "V", (7, 1): "V"}})
stufe("Zombie (Namensschild!): nachts über eine Behelfstreppe auf den Steg locken. Die Einstiegs-Falltür ist nachts "
      "offen – spring über die Lücke nach Süden aufs Glas, der Zombie läuft auf die offene Falltür und fällt in die "
      "Zelle.", {10: {(1, 0): "Z"}})
stufe("Zurück über die Lücke, die Falltür zuklappen und schleichend eine Stufe oben drauf setzen – Schatten, sonst "
      "verbrennt der Zombie am Tag (kein Glas!). Behelfstreppe wieder abbauen.", {13: {(1, 0): "s"}})
stufe("Hier unten an der Truhe kannst du warten (oder irgendwo in Simulationsdistanz).", {-12: {(3, 1): "P"}})

f.pruefe(boden=GRAS, zeit=12500,
         erwartet={"items": {"minecraft:iron_ingot": 28}},
         hoechstens={"wesen": {"minecraft:iron_golem": 2}})
