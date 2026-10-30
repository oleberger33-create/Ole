"""Zeichnet das Item-Bild von Ole's Farmhelper (16 × 16 Pixel): eine blaue Bauplan-Rolle mit Gitter,
darauf eine goldene Hacke und ein Weizenhalm. Aufruf: python3 textur.py <ziel.png> [vorschau.png]"""
import sys
from PIL import Image

FARBEN = {
    ".": None,
    "B": (38, 92, 160), "b": (60, 124, 196), "g": (150, 196, 236),   # Bauplan: dunkel, hell, Gitter
    "R": (24, 58, 110),                                               # Rand / Rolle
    "W": (236, 242, 250),                                             # Papierkante
    "H": (122, 82, 44), "h": (88, 56, 28),                            # Stiel
    "G": (250, 214, 60), "O": (196, 150, 24), "Y": (255, 246, 160),   # Gold
    "L": (96, 176, 64), "l": (60, 128, 40), "K": (226, 190, 90), "k": (180, 140, 50),  # Halm, Korn
}
BILD = [
    "................",
    ".RRRRRRRRRRR....",
    ".RWbgbbgbbgR..K.",
    ".RbBgBBgBBgR.KkK",
    ".RggggggggggR.Kk",
    ".RbBgBBgOGGGY.l.",
    ".RbBgBBgBBOGG.l.",
    ".RggggggggHgR.L.",
    ".RbBgBBgBhBgRL..",
    ".RbBgBBgHBBgRL..",
    ".RgggggHgggglL..",
    ".RbBgBhBBgBgRL..",
    ".RbBgHBBBgBgR...",
    ".RRRhRRRRRRRR...",
    "...h............",
    "................",
]


def zeichnen():
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    for y, zeile in enumerate(BILD):
        for x, c in enumerate(zeile):
            if FARBEN.get(c):
                img.putpixel((x, y), FARBEN[c] + (255,))
    return img


if __name__ == "__main__":
    bild = zeichnen()
    bild.save(sys.argv[1])
    if len(sys.argv) > 2:
        bild.resize((256, 256), Image.NEAREST).save(sys.argv[2])
