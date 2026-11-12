"""Gemeinsame Werkzeuge für die Profi-Varianten (generator/profi/<farm>.py).

Jede Farm hat zwei Bauweisen: die einfache (farmen.py, id „<farm>“) und die beste im Survival machbare
(„<farm>_profi“, Name „… (Profi)“). Eine Profi-Datei sieht so aus:

    from profi_basis import *

    BLOECKE = {}            # nur falls nötig: neue Blöcke im EINFACH-Format von bloecke.py (reines Literal!)
    GERICHTET_NEU = {}      # dito im GERICHTET-Format

    f = profi("zuckerrohr", dict(
        name="Zuckerrohr-Farm (Profi)", diff=3, out="Zuckerrohr", where="Überall", afk="Ja",
        why="…", help=[["Problem", "Lösung"]],
        meta=m("Rate …", [("Ort …", W + "Tutorial:Sugar_cane_farming")], [("Mechanik …", W + "…")])))
    f.zeichen(K=("piston", "s"), …)
    f.schritt("Text …", {y: Raster, …}, x0=…, z0=…)
    …
    f.pruefe(boden=GRAS, erwartet={"items": {"minecraft:sugar_cane": 40}})

Plan-Format, Zeichen und Richtungen: siehe entwurf.py und bloecke.py; Tests: ../test/mctest.py.
Selbst prüfen: python3 profi_pruefen.py <farm>
"""
import os

from entwurf import Farm, raster  # noqa: F401  (für die Profi-Dateien)
from farmtexte import TEXTE, W, TEST, m  # noqa: F401

GRAS = "minecraft:grass_block"
HIER = os.path.dirname(os.path.abspath(__file__))


def profi(fid, text):
    """Profi-Variante der Farm <fid> anlegen. text: name, diff, out, where, afk, why, help, meta (cat wie die
    Grundfarm, wenn nicht angegeben)."""
    assert fid in TEXTE, f"unbekannte Grundfarm {fid}"
    daten = {"cat": TEXTE[fid]["cat"]}
    daten.update(text)
    for k in ("name", "diff", "out", "where", "afk", "why", "help", "meta"):
        assert k in daten, f"{fid}_profi: Text-Feld {k} fehlt"
    assert daten["name"].endswith("(Profi)"), "Name soll mit „(Profi)“ enden"
    return Farm(fid + "_profi", **daten)


def raster_aus(zellen, x0, z0, x1, z1):
    """Raster-Text aus {(x, z): Zeichen} für x0..x1, z0..z1."""
    return "\n".join("".join(zellen.get((x, z), ".") for x in range(x0, x1 + 1)) for z in range(z0, z1 + 1))


def flaeche(zeichen, breite, tiefe):
    """Rechteck aus einem Zeichen, z. B. flaeche("#", 9, 9)."""
    return "\n".join([zeichen * breite] * tiefe)


def mobs(typ, punkte, extra="PersistenceRequired:1b"):
    """Test-Befehle: Mobs an Plan-Koordinaten setzen (für _mech-Tests)."""
    return [f"summon minecraft:{typ} {{x{x:+d}}}.5 {{y{y:+d}}} {{z{z:+d}}}.5 {{{extra}}}" for x, y, z in punkte]


def lade_alle():
    """Alle Profi-Dateien laden (sortiert) – gibt die Liste der geladenen Grundfarm-ids zurück."""
    import importlib
    ids = []
    for n in sorted(os.listdir(os.path.join(HIER, "profi"))):
        if n.endswith(".py") and not n.startswith("_"):
            importlib.import_module("profi." + n[:-3])
            ids.append(n[:-3])
    return ids
