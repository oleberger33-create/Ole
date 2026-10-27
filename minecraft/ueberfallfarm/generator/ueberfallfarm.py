"""Gibt die Befehle für die Überfall-Farm über dem Meer aus (läuft rein vanilla, wird einmal per Konsole gesetzt).

Aufruf:  python3 ueberfallfarm.py <ort.json> [umbau]
         umbau: nur Version 1 → 2 (oberer Teil 5 Blöcke höher), Zelle, Truhe und Spielerraum bleiben

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
  F2        Stufe 2, Rinne 2 breit: Quellen im Westen, 7 Blöcke Fluss nach Osten, dahinter das 2 × 2-Loch
  F2-1..K   trockener Schacht, 30 Blöcke: Plünderer, Diener, Magier und Hexen sterben beim Aufprall, Verwüster
            kommen mit etwa 36 Herzen an (2 × 2 passt für sie). Version 1 hatte 25 Blöcke, alle kamen mit ½ bis
            1 Herz an. Ein Magier, der einen Schlag überlebt, ruft Plagegeister, und die fliegen durch Wände.
            Ohne Spielerschlag fehlen nur Smaragde und XP; Totems, Flaschen der Anführer und Banner fallen immer.
  K         Tötungszelle über Trichtern; davor unten eine Stufe, darüber eine eiserne Falltür (obere Hälfte):
            Durch den Spalt schlägt man die Verwüster, und die XP-Kugeln kommen heraus. Die Augen der Räuber liegen
            über dem Spalt, sie sehen den Spieler nicht. Trifft man einen Verwüster, greifen nur Verwüster an.
  K-1       Spielerraum (Füße), Truhe hinter den Trichtern, Ofen, Werkbank. Hier die Flasche trinken.
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
F2 = K + 30                                   # Wasser Stufe 2
F2_ALT = K + 25                               # Version 1
F1 = F2 + 3                                   # Wasser Stufe 1
TOP = F1 + 5                                  # Schneefeld
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
    fill(1, F1 - 1, 1, 10, TOP + 1, 1, W),                         # Nordwand
    fill(1, F1 - 1, 1, 1, TOP + 1, 9, W),                          # Westwand
    fill(10, F1 - 1, 1, 10, TOP + 1, 9, W),                        # Ostwand
    fill(1, TOP + 2, 1, 10, TOP + 2, 1, DECKEL),
    fill(1, TOP + 2, 1, 1, TOP + 2, 9, DECKEL),
    fill(10, TOP + 2, 1, 10, TOP + 2, 9, DECKEL),
    fill(2, F2 - 1, 9, 9, F1 - 2, 9, W),                           # unter der Kante: Nordwand von Stufe 2
    # Stufe 2: x 2..9, z 10..11, Loch x 10..11
    fill(2, F2 - 1, 10, 9, F2 - 1, 11, W),
    fill(1, F2 - 1, 12, 12, F1 + 2, 12, W),                        # Südwand
    fill(1, F2 - 1, 10, 1, F1 + 2, 11, W),                         # Westwand
    fill(12, F2 - 1, 9, 12, F1 + 2, 11, W),                        # Ostwand am Loch
    fill(10, F2 - 1, 9, 10, F1 - 2, 9, W),                         # Nordwand am Loch, darüber die Ostwand von Stufe 1
    fill(11, F2 - 1, 9, 11, F1 + 2, 9, W),
    fill(1, F1 + 3, 12, 12, F1 + 3, 12, DECKEL),
    fill(1, F1 + 3, 10, 1, F1 + 3, 11, DECKEL),
    fill(11, F1 + 3, 9, 12, F1 + 3, 9, DECKEL),
    fill(12, F1 + 3, 10, 12, F1 + 3, 11, DECKEL),
]
schacht = [                                                         # 2 × 2 (x 10..11, z 10..11) von K bis F2
    fill(9, K - 2, 9, 12, F2 - 2, 12, W),
    fill(10, K, 10, 11, F2, 11, "air"),
]
unten = [
    # Spielerraum: innen x 9..13, z 13..14, Füße K-1
    fill(8, K - 2, 12, 14, K + 1, 15, W),
    fill(9, K - 1, 13, 13, K, 14, "air"),
    setb(11, K + 1, 14, "sea_lantern"),
    fill(8, K + 2, 12, 14, K + 2, 15, DECKEL, " replace minecraft:air"),  # auf dem Dach spawnt nichts
    # Tötungszelle und Spalt
    setb(10, K - 1, 10, "hopper[facing=east]"),
    setb(11, K - 1, 10, "hopper[facing=south]"),
    setb(10, K - 1, 11, "hopper[facing=east]"),
    setb(11, K - 1, 11, "hopper[facing=east]"),
    setb(12, K - 1, 11, "hopper[facing=south]"),
    setb(12, K - 1, 12, "hopper[facing=south]"),
    setb(12, K - 1, 13, "chest[facing=south,type=right]"),
    setb(13, K - 1, 13, "chest[facing=south,type=left]"),
    fill(10, K - 1, 12, 11, K - 1, 12, "stone_brick_slab[type=bottom]"),
    fill(10, K, 12, 11, K, 12, "iron_trapdoor[facing=south,half=top,open=false]"),
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
umbau = [fill(1, F2_ALT - 1, 1, 12, TOP + 2, 12, "air"),           # alte Stufen samt Schnee weg
         fill(9, F2_ALT - 1, 9, 12, F2 - 2, 12, W),                # Schacht nach oben verlängern
         fill(10, F2_ALT - 1, 10, 11, F2, 11, "air")]

if __name__ == "__main__":
    teile = umbau + oben if sys.argv[2:] == ["umbau"] else oben + schacht + unten
    for b in teile + wasser + schnee:
        print(b)
