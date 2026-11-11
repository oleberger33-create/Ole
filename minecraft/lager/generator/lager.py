"""Gibt die Befehle für das Lager unter dem Haus aus: eine Halle aus Steinziegeln mit Truhen-Fächern und Schildern.

Aufruf:  python3 lager.py <ort.json> [faecher.json]

ort.json:  {"ecke": [x, y, z], "einstieg": [x, y, z]}
           ecke: Nordwest-Ecke der Außenwand auf Bodenhöhe; einstieg: Stelle im Hausboden für die Falltür
faecher.json (optional, von einsortieren.py): {"<fach-nr>": ["Titel", "Zeile 2", "Zeile 3", "Zeile 4"], …}
           ohne die Datei bekommen die Schilder nur „Fach <nr>“

Halle innen 15 × 13 Blöcke, 5 hoch (Boden y+0, Decke y+6), Leuchtstein in der Decke, damit nichts spawnt.
Ein Fach sind zwei Doppeltruhen übereinander (108 Stapel); über jeder Spalte eines Fachs hängt ein Schild an der
Wand (oder am Mittelrücken der Insel), so bleibt über jeder Truhe Luft und alle lassen sich öffnen.
  Nordwand   2 + 4 Fächer, dazwischen frei für die Leiter
  Südwand    7 Fächer
  West/Ost   je 5 Fächer
  Insel      je 4 Fächer nach Norden und Süden, Rücken aus Steinziegeln
Einstieg: Leiter an der Nordwand vom Hausboden bis in die Halle, oben eine Falltür im Boden.
"""
import json
import sys

ORT = json.load(open(sys.argv[1])) if __name__ == "__main__" else None
FAECHER = json.load(open(sys.argv[2])) if __name__ == "__main__" and len(sys.argv) > 2 else {}
X0 = Y0 = Z0 = EX = EY = EZ = 0


def setze_ort(ort):
    global X0, Y0, Z0, EX, EY, EZ
    X0, Y0, Z0 = ort["ecke"]
    EX, EY, EZ = ort["einstieg"]
B, T = 17, 15                         # Außenmaße x, z
W = "stone_bricks"


def p(x, y, z):
    return f"{X0 + x} {Y0 + y} {Z0 + z}"


def fill(x1, y1, z1, x2, y2, z2, blk, extra=""):
    return f"fill {p(x1, y1, z1)} {p(x2, y2, z2)} minecraft:{blk}{extra}"


# Fächer: (Spalte 1, Spalte 2, Blickrichtung der Truhen, Schild hängt an Block in Richtung „hinten“)
def faecher():
    f = []
    for xa in (1, 3, 8, 10, 12, 14):                          # Nordwand z = 1, Truhen schauen nach Süden
        f.append(((xa, 1), (xa + 1, 1), "south"))
    for xa in range(1, 15, 2):                                # Südwand z = 13
        f.append(((xa, 13), (xa + 1, 13), "north"))
    for za in range(2, 12, 2):                                # Westwand x = 1
        f.append(((1, za), (1, za + 1), "east"))
    for za in range(2, 12, 2):                                # Ostwand x = 15
        f.append(((15, za), (15, za + 1), "west"))
    for xa in range(4, 12, 2):                                # Insel: Nordreihe z = 6, Südreihe z = 8, Rücken z = 7
        f.append(((xa, 6), (xa + 1, 6), "north"))
    for xa in range(4, 12, 2):
        f.append(((xa, 8), (xa + 1, 8), "south"))
    return f


HINTEN = {"south": (0, -1), "north": (0, 1), "east": (-1, 0), "west": (1, 0)}


def fach_truhen(nummer):
    """Weltpositionen eines Fachs: [(unten links, unten rechts), (oben links, oben rechts)] mit Doppeltruhen."""
    a, b_, _ = faecher()[nummer - 1]
    return [((X0 + a[0], Y0 + y, Z0 + a[1]), (X0 + b_[0], Y0 + y, Z0 + b_[1])) for y in (1, 2)]


def schild(x, z, richtung, text):
    msgs = ",".join(json.dumps(t, ensure_ascii=False) for t in (list(text) + ["", "", "", ""])[:4])
    return (f"setblock {p(x, 3, z)} minecraft:spruce_wall_sign[facing={richtung}]"
            f"{{front_text:{{has_glowing_text:1b,color:\"white\",messages:[{msgs}]}},is_waxed:1b}}")


def schilder(texte):
    """Befehle für alle Schilder; texte: {"<nr>": [4 Zeilen], "<nr>b": [4 Zeilen] für die rechte Spalte}."""
    out = []
    for nummer, (a, b_, richtung) in enumerate(faecher(), 1):
        links = texte.get(str(nummer), [f"Fach {nummer}"])
        rechts = texte.get(f"{nummer}b", links)
        out += [schild(a[0], a[1], richtung, links), schild(b_[0], b_[1], richtung, rechts)]
    return out


def truhen_typ(richtung, erste):
    # Doppeltruhe: „left“ verbindet im Uhrzeigersinn der Blickrichtung. Spalte 1 liegt bei Süd/West-Blick links
    # vom Partner im Uhrzeigersinn, sonst rechts.
    uhrzeiger = {"south": (-1, 0), "west": (0, -1), "north": (1, 0), "east": (0, 1)}[richtung]
    return uhrzeiger




def bau():
    befehle = [
        fill(0, 0, 0, B - 1, 6, T - 1, W),                                  # Block aus Steinziegeln
        fill(1, 1, 1, B - 2, 5, T - 2, "air"),                              # Halle
        fill(1, 0, 1, B - 2, 0, T - 2, "polished_andesite"),                # Boden
    ]
    for x in range(2, B - 2, 4):                                            # Licht in der Decke
        for z in range(2, T - 2, 4):
            befehle.append(f"setblock {p(x, 6, z)} minecraft:glowstone")
    befehle.append(fill(4, 1, 7, 12, 3, 7, W))                              # Inselrücken
    nummer = 0
    for (a, b_, richtung) in faecher():
        nummer += 1
        hx, hz = HINTEN[richtung]
        # Typen: left verbindet zum Nachbarn im Uhrzeigersinn der Blickrichtung
        cw = truhen_typ(richtung, True)
        typ_a = "left" if (b_[0] - a[0], b_[1] - a[1]) == cw else "right"
        typ_b = "right" if typ_a == "left" else "left"
        for y in (1, 2):
            befehle.append(f"setblock {p(a[0], y, a[1])} minecraft:chest[facing={richtung},type={typ_a}]")
            befehle.append(f"setblock {p(b_[0], y, b_[1])} minecraft:chest[facing={richtung},type={typ_b}]")
    befehle += schilder(FAECHER)
    # Einstieg: Leiter an der Nordwand, Falltür im Hausboden
    lx, lz = EX - X0, EZ - Z0
    befehle += [fill(lx, 1, lz, lx, EY - Y0 - 1, lz, "ladder[facing=south]"),
                f"setblock {EX} {EY} {EZ} minecraft:oak_trapdoor[facing=south,half=top,open=false]"]
    return befehle


if __name__ == "__main__":
    setze_ort(ORT)
    for b in bau():
        print(b)
