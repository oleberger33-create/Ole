"""Gibt die Befehle für die Patrouillen-Farm über dem Meer aus (läuft rein vanilla, wird einmal per Konsole gesetzt).
Jede Plünderer-Patrouille hat einen Anführer mit Banner, und der lässt beim Tod immer eine Unheilvolle Flasche fallen.

Aufruf:  python3 patrouillenfarm.py <ort.json>

ort.json:  {"afk": [x, y, z]}   Block, auf dem der Spieler AFK steht (y: Füße)

Wann eine Patrouille kommt (PatrolSpawner, Spielcode 26.3):
- Etwa alle 10 Minuten ein Versuch, nur tagsüber, ab Tag 5, mit 20 % Chance; dann ein zufälliger Spieler dieser
  Dimension. Steht er in einem Dorf (bis 2 Abschnitte von belegten Betten/Arbeitsblöcken), fällt sie aus.
- Ort: Spieler ± 24..47 Blöcke in x UND z, also eine von vier 24 × 24-Ecken um ihn, auf der obersten Fläche
  (MOTION_BLOCKING_NO_LEAVES). Der Anführer braucht festen Boden und Blocklicht ≤ 8, sonst fällt die Patrouille aus.
  Über dem Meer ist die oberste Fläche Wasser: Es zählen nur die vier Plattformen.
- Die Plattformen müssen über 105 Blöcke von der Überfall-Farm weg sein: Ein Überfall sucht seinen Spawnplatz bis
  98 Blöcke (plus Versatz) um seine Mitte und würde sonst auf diesen Plattformen landen.

Aufbau (relativ zum AFK-Block, jede Ecke gespiegelt, a/b = Abstand in x/z):
  ANFLUG      Plattform a, b = 24..47 auf Höhe P (Füße P + 1)
  P + 1       ringsum (a oder b = 23 bzw. 48) offene Holzfalltüren, Klappe außen: Für Mobs sind sie begehbarer
              Boden. Der Anführer läuft Richtung Ziel (zufällig, 500 Blöcke weit), die anderen folgen ihm, und alle
              treten auf die Klappen und fallen.
  Boden + 1   30 Blöcke tiefer ein Trichterring unter den Klappen, links und rechts Glas: Plünderer (24 Leben)
              sterben beim Aufprall (28 Schaden). Der Ring läuft zur inneren Ecke, eine Trichterkette bringt alles
              in eine Truhe im Boden des AFK-Raums.
  Boden       AFK-Raum 5 × 5 aus Glas, Seelaterne im Boden, vier Truhen (je Ecke eine)
"""
import json
import sys

ORT = json.load(open(sys.argv[1]))
X0, Y0, Z0 = ORT["afk"]
BODEN = Y0 - 1                                  # Boden des AFK-Raums, Trichter auf gleicher Höhe
P = BODEN + 30                                  # Plattformen: Füße P + 1, Fall bis in die Trichtermulde gut 30
W = "stone_bricks"
INNEN, AUSSEN = 24, 47                          # Spawnbereich je Achse
RING_I, RING_A = INNEN - 1, AUSSEN + 1          # Falltüren und Trichterring


def richtung(achse, vorzeichen, sx, sz):
    """Richtung im lokalen Eckkoordinatensystem (a = x, b = z, beide nach außen positiv) → Himmelsrichtung."""
    s = vorzeichen * (sx if achse == "a" else sz)
    if achse == "a":
        return "east" if s > 0 else "west"
    return "south" if s > 0 else "north"


befehle = []


def ecke(sx, sz):
    def p(a, y, b):
        return f"{X0 + sx * a} {y} {Z0 + sz * b}"

    def fill(a1, y1, b1, a2, y2, b2, blk):
        befehle.append(f"fill {p(a1, y1, b1)} {p(a2, y2, b2)} minecraft:{blk}")

    def setb(a, y, b, blk):
        befehle.append(f"setblock {p(a, y, b)} minecraft:{blk}")

    def r(achse, v):
        return richtung(achse, v, sx, sz)

    # Plattform
    fill(INNEN, P, INNEN, AUSSEN, P, AUSSEN, W)
    # Falltüren ringsum, offen, Klappe außen (facing zeigt zur Plattform)
    tuer = "spruce_trapdoor[half=bottom,open=true,facing={}]"
    fill(RING_I, P + 1, RING_I, RING_A, P + 1, RING_I, tuer.format(r("b", +1)))
    fill(RING_I, P + 1, RING_A, RING_A, P + 1, RING_A, tuer.format(r("b", -1)))
    fill(RING_I, P + 1, INNEN, RING_I, P + 1, AUSSEN, tuer.format(r("a", +1)))
    fill(RING_A, P + 1, INNEN, RING_A, P + 1, AUSSEN, tuer.format(r("a", -1)))
    # Glasrinne um den Trichterring
    fill(RING_I - 1, BODEN + 1, RING_I - 1, RING_A + 1, BODEN + 2, RING_A + 1, "glass")
    fill(RING_I, BODEN + 1, RING_I, RING_A, BODEN + 2, RING_A, "air")
    fill(INNEN, BODEN + 1, INNEN, AUSSEN, BODEN + 2, AUSSEN, "glass")
    fill(INNEN + 1, BODEN + 1, INNEN + 1, AUSSEN - 1, BODEN + 2, AUSSEN - 1, "air")
    # Trichterring zur inneren Ecke, von dort Kette zum AFK-Raum
    hopper = "hopper[facing={}]"
    fill(RING_I, BODEN, INNEN, RING_I, BODEN, RING_A, hopper.format(r("b", -1)))
    fill(RING_A, BODEN, INNEN, RING_A, BODEN, AUSSEN, hopper.format(r("b", -1)))
    fill(INNEN, BODEN, RING_I, RING_A, BODEN, RING_I, hopper.format(r("a", -1)))
    fill(INNEN, BODEN, RING_A, RING_A, BODEN, RING_A, hopper.format(r("a", -1)))
    fill(3, BODEN, RING_I, RING_I, BODEN, RING_I, hopper.format(r("a", -1)))
    fill(2, BODEN, 3, 2, BODEN, RING_I, hopper.format(r("b", -1)))
    setb(2, BODEN, 2, "chest")


# AFK-Raum: Boden zuerst, die Ketten ersetzen dann einzelne Bodenblöcke
befehle.append(f"fill {X0 - 3} {BODEN} {Z0 - 3} {X0 + 3} {BODEN} {Z0 + 3} minecraft:{W}")
befehle.append(f"fill {X0 - 3} {BODEN + 1} {Z0 - 3} {X0 + 3} {BODEN + 3} {Z0 + 3} minecraft:glass")
befehle.append(f"fill {X0 - 2} {BODEN + 1} {Z0 - 2} {X0 + 2} {BODEN + 3} {Z0 + 2} minecraft:air")
befehle.append(f"fill {X0 - 3} {BODEN + 4} {Z0 - 3} {X0 + 3} {BODEN + 4} {Z0 + 3} minecraft:smooth_stone_slab[type=bottom]")
befehle.append(f"setblock {X0} {BODEN} {Z0} minecraft:sea_lantern")
for sx in (1, -1):
    for sz in (1, -1):
        ecke(sx, sz)

if __name__ == "__main__":
    for b in befehle:
        print(b)
