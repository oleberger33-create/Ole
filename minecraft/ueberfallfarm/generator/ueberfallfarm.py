"""Gibt die Befehle für die Überfall-Farm über dem Meer aus (läuft rein vanilla, wird einmal per Konsole gesetzt).

Aufruf:  python3 ueberfallfarm.py <ort.json> [umbau]
         umbau: nur Version 5 → 6 (Hebel weg, Klappen immer offen), alles andere bleibt

ort.json:  {"chunk": [x, z]}   Nordwest-Ecke des Chunks; alles liegt in diesem einen Chunk (16 × 16)

Wie ein Überfall hier läuft (Spielcode):
- Wer mit „Böses Omen“ (Unheilvolle Flasche) in ein Dorf kommt, startet nach 30 Sekunden einen Überfall. Dorf heißt:
  ein Bett und ein Arbeitsblock, die ein Dorfbewohner belegt hat, höchstens einen Abschnitt (16er-Würfel) entfernt.
- Mitte des Überfalls = Mittel der belegten Dorfpunkte (hier Bettkopf und Komposter). Jede Welle sucht erst 64, dann
  32 Blöcke entfernt einen Platz auf der Oberfläche; ringsum ist nur Wasser, also spawnt sie direkt an der Mitte:
  auf der obersten Fläche im 5 × 5-Feld x+0..4, z+0..4. Bett oder Komposter allein: Mitte ein Block anders, deshalb
  ist das Feld 5 × 6 groß.
- Auf einer Schneeschicht darf ein Überfall immer spawnen. Eine einzelne Schicht hat keine Hitbox: Die Räuber fallen
  hindurch. Die Schichten schweben (mit „strict“ gesetzt, ohne Blockupdates). Baut man direkt daneben, fallen sie ab.
  Kein Licht in der Nähe, ab Lichtstufe 12 schmelzen sie.

Von oben nach unten:
  TOP       Schneefeld
  F1        Stufe 1, 8 × 8 Wasser: Quellen an der Nordwand, 7 Blöcke Fluss nach Süden. In der letzten Reihe ist das
            Wasser zu Ende, es läuft nicht über die Kante, die Räuber fallen 3 Blöcke tiefer in
  F2        Stufe 2, Rinne 2 breit: Quellen im Westen, 7 Blöcke Fluss nach Osten, dahinter das 2 × 2-Loch.
            Das letzte Feld vor dem Loch hat eine Stufe als Boden: Die Räuber fallen ab F2 - ½.
  F2-1..K   trockener Schacht (2 × 2, Verwüster passen). Die Räuber fallen ab etwa F2 - 1 (so lange stecken sie
            noch im Wasser der letzten Rinne).
  K-1       Boden der Tötungszelle: 4 eiserne Falltüren, immer offen (ein Redstoneblock in der Wand speist sie).
            Plünderer, Diener, Magier und Hexen fallen durch in die Grube auf die Trichter bei K-5, 29 Blöcke,
            26 und mehr Schaden: Sie sterben alle. Verwüster (fast 2 breit) passen nicht zwischen die offenen Klappen,
            sie bleiben oben mit etwa 39 Herzen und werden durch den Spalt erledigt; trifft man sie, greifen nur
            Verwüster an, und die sehen den Spieler nicht. Wer auf dem Rücken eines Verwüsters landet (Hexe: 3 Herzen
            übrig) oder als Reiter mitkommt, fällt bei seinem Tod 9 Blöcke tief in die Grube und stirbt. Die Grube
            reicht deshalb bis knapp übers Wasser (Version 5: Trichter 4 Blöcke höher, eine Hexe überlebte dort und
            warf durch den Spalt nach oben Schadenstränke). Sie leert sich in die Truhe auf der Plattform am Wasser.
            Warum kein Spielerschlag für die anderen (Version 4/5): Smaragde und XP gibt es nur, wenn ein Spieler
            trifft. Eine Hexe heilt die anderen mit Tränken; ein geheilter Magier überlebt den Schlag und ruft
            Plagegeister. Version 5 hatte dafür einen Hebel (Klappen zu für die Wellen 1 bis 4), zu umständlich.
  Spalt     Vorn eine untere Stufe (K - ½), darüber frei bis zu einer oberen Stufe (K + ½). Die Augen der Räuber in
            der Zelle liegen darüber (Verwüster auf den Klappen), die des stehenden Spielers auch (K + 0,62): Eine
            Sichtlinie müsste unter K + ½ durch, also sieht kein Räuber den Spieler. Aus der Grube steigen Sichtlinien
            steil an und treffen die untere Stufe oder den Boden. Nicht ducken (Augen K + 0,27).
  K-1       Spielerraum (Füße), Truhe aus Version 1 bis 4, Ofen, Werkbank. Hier die Flasche trinken.
  64        Dorfbewohner mit Bett und Komposter, 8 Blöcke unter der Zelle. Räuber suchen Dorfbewohner nur 4 Blöcke
            über und unter sich; so wird er nie angegriffen.
  63        Plattform auf dem Wasser, Leiter hoch in den Spielerraum
"""
import json
import sys

ORT = json.load(open(sys.argv[1]))
X0, Z0 = ORT["chunk"]
MEER = 63                                     # Wasseroberfläche: Wasser bis 62
V = 64                                        # Füße des Dorfbewohners
K = 72                                        # Tötungszelle (Trichter darunter)
F2 = K + 26                                   # Wasser Stufe 2
F1 = F2 + 3                                   # Wasser Stufe 1
TOP = F1 + 5                                  # Schneefeld
MAUER = TOP + 4                               # Mauern bis über die Spawnhöhe (TOP + 2): Eine Welle spawnt auf einem
                                              # Punkt, die Räuber schubsen sich im Fallen auseinander. In Version 2
                                              # (Mauern 3 bzw. 6 Blöcke niedriger) flogen einige über die Südwand.
W = "stone_bricks"
DECKEL = "smooth_stone_slab[type=bottom]"     # auf Stufen spawnt nichts, und Räuber laufen nicht dorthin


def pos(x, y, z):
    return f"{X0 + x} {y} {Z0 + z}"


def fill(x1, y1, z1, x2, y2, z2, blk, extra=""):
    return f"fill {pos(x1, y1, z1)} {pos(x2, y2, z2)} minecraft:{blk}{extra}"


def setb(x, y, z, blk):
    return f"setblock {pos(x, y, z)} minecraft:{blk}"


oben = [
    # Stufe 1: x 2..9, z 2..9
    fill(2, F1 - 1, 2, 9, F1 - 1, 9, W),
    fill(1, F1 - 1, 1, 10, MAUER, 1, W),                           # Nordwand
    fill(1, F1 - 1, 1, 1, MAUER, 9, W),                            # Westwand
    fill(10, F1 - 1, 1, 10, MAUER, 9, W),                          # Ostwand
    fill(1, MAUER + 1, 1, 10, MAUER + 1, 1, DECKEL),
    fill(1, MAUER + 1, 1, 1, MAUER + 1, 9, DECKEL),
    fill(10, MAUER + 1, 1, 10, MAUER + 1, 9, DECKEL),
    fill(2, F2 - 1, 9, 9, F1 - 2, 9, W),                           # unter der Kante: Nordwand von Stufe 2
    # Stufe 2: x 2..9, z 10..11, Loch x 10..11
    fill(2, F2 - 1, 10, 9, F2 - 1, 11, W),
    fill(9, F2 - 1, 10, 9, F2 - 1, 11, "stone_brick_slab[type=bottom]"),   # Absprung ½ Block tiefer
    fill(1, F2 - 1, 12, 12, MAUER, 12, W),                         # Südwand
    fill(1, F2 - 1, 10, 1, MAUER, 11, W),                          # Westwand
    fill(12, F2 - 1, 9, 12, MAUER, 11, W),                         # Ostwand am Loch
    fill(10, F2 - 1, 9, 10, F1 - 2, 9, W),                         # Nordwand am Loch, darüber die Ostwand von Stufe 1
    fill(11, F2 - 1, 9, 11, MAUER, 9, W),
    fill(1, MAUER + 1, 12, 12, MAUER + 1, 12, DECKEL),
    fill(1, MAUER + 1, 10, 1, MAUER + 1, 11, DECKEL),
    fill(11, MAUER + 1, 9, 12, MAUER + 1, 9, DECKEL),
    fill(12, MAUER + 1, 10, 12, MAUER + 1, 11, DECKEL),
]
schacht = [                                                         # 2 × 2 (x 10..11, z 10..11) von K bis F2
    fill(9, K - 2, 9, 12, F2 - 2, 12, W),
    fill(10, K, 10, 11, F2, 11, "air"),
]
zelle = [
    # Grube: Trichter knapp über dem Wasser, darüber frei bis zum Klappboden, Truhe darunter (Zugang von Süden)
    fill(9, MEER, 9, 12, K - 3, 12, W, " keep"),
    fill(10, MEER + 2, 10, 11, K - 2, 11, "air"),
    setb(10, MEER + 1, 10, "hopper[facing=east]"),
    setb(11, MEER + 1, 10, "hopper[facing=south]"),
    setb(10, MEER + 1, 11, "hopper[facing=east]"),
    setb(11, MEER + 1, 11, "hopper[facing=down]"),
    setb(11, MEER, 11, "chest[facing=south]"),
    fill(11, MEER, 12, 11, MEER + 1, 12, "air"),
    # Klappboden: offen liegen die Klappen an der West- und Ostwand
    fill(10, K - 1, 10, 10, K - 1, 11, "iron_trapdoor[facing=east,half=bottom,open=false]"),
    fill(11, K - 1, 10, 11, K - 1, 11, "iron_trapdoor[facing=west,half=bottom,open=false]"),
    # Spalt
    fill(10, K - 1, 12, 11, K - 1, 12, "stone_brick_slab[type=bottom]"),
    fill(10, K, 12, 11, K, 12, "stone_brick_slab[type=top]"),
    # Leitung: Redstoneblock in der Raumwand → Staub um die Zelle → Verstärker in der Zellwand → Falltüren
    fill(8, K - 2, 8, 8, K - 2, 11, W),
    fill(9, K - 2, 8, 13, K - 2, 8, W),
    fill(13, K - 2, 9, 13, K - 2, 11, W),
    fill(9, K - 1, 10, 9, K - 1, 11, "repeater[facing=west]"),
    fill(12, K - 1, 10, 12, K - 1, 11, "repeater[facing=east]"),
    fill(8, K - 1, 8, 8, K - 1, 11, "redstone_wire"),
    fill(9, K - 1, 8, 13, K - 1, 8, "redstone_wire"),
    fill(13, K - 1, 9, 13, K - 1, 12, "redstone_wire"),
    setb(12, K - 1, 12, W),
    setb(13, K, 12, "redstone_block"),
]
unten = [
    # Spielerraum: innen x 9..13, z 13..14, Füße K-1
    fill(8, K - 2, 12, 14, K + 1, 15, W),
    fill(9, K - 1, 13, 13, K, 14, "air"),
    setb(11, K + 1, 14, "sea_lantern"),
    fill(8, K + 2, 12, 14, K + 2, 15, DECKEL, " replace minecraft:air"),  # auf dem Dach spawnt nichts
    setb(12, K - 1, 13, "chest[facing=south,type=right]"),
    setb(13, K - 1, 13, "chest[facing=south,type=left]"),
    # Leiter vom Wasser in den Spielerraum (x 9, z 14)
    fill(7, MEER - 1, 11, 11, MEER - 1, 13, W),
    setb(9, MEER - 1, 14, W),
    fill(8, MEER, 14, 8, K - 3, 14, W),
    fill(10, MEER, 14, 10, K - 3, 14, W),
    fill(9, MEER, 15, 9, K - 3, 15, W),
    fill(9, MEER + 2, 13, 9, K - 3, 13, W),
    fill(9, MEER, 14, 9, K - 2, 14, "ladder[facing=north]"),
    setb(7, MEER, 11, "lantern"),
    # Dorfbewohner: innen x 3..4, z 2..4, Bett (Kopf bei z 3), Komposter, Glas
    fill(2, MEER, 1, 5, MEER, 5, W),
    fill(2, V, 1, 5, V + 2, 5, "glass"),
    fill(3, V, 2, 4, V + 1, 4, "air"),
    setb(4, MEER, 2, "sea_lantern"),                              # hell genug, dass in der Zelle nichts spawnt
    setb(3, V, 2, "green_bed[facing=south,part=foot]"),
    setb(3, V, 3, "green_bed[facing=south,part=head]"),
    setb(3, V, 4, "composter"),
]
wasser = [
    fill(2, F1, 2, 9, F1, 2, "water"),                             # Quellen Stufe 1
    fill(2, F2, 10, 2, F2, 11, "water"),                           # Quellen Stufe 2
]
schnee = [fill(3, TOP, 3, 7, TOP, 8, "snow[layers=1]", " strict")]

if __name__ == "__main__":
    modus = sys.argv[2] if len(sys.argv) > 2 else "neu"
    teile = {"neu": oben + schacht + unten + zelle + wasser + schnee,
             "umbau": [setb(12, K, 13, "air")] + zelle}[modus]
    for b in teile:
        print(b)
