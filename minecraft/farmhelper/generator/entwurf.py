"""Kleines Plan-Format für Farmhelper-Farmen: Bauschritte als Text-Raster, Ebene für Ebene.

So sieht ein Plan aus (Zeilen = Norden → Süden, Spalten = Westen → Osten, erste Spalte x 0, erste Zeile z 0):

    f = Farm("zuckerrohr", name="Zuckerrohr-Farm", …)
    f.zeichen(K=("piston", "s"), B=("observer", "s"))
    f.schritt("Trichter und Truhe legen.", {
        -1: '''
            C<<<<<<<
        '''})

Jeder Schritt ist {y: Raster}; „.“ und Leerzeichen = nichts. Ein Zeichen steht für einen Block aus bloecke.py,
mit Richtung als zweitem Wert (n/e/s/w/u/d) oder einem dict mit weiteren Eigenschaften. Lebewesen (villager …)
werden automatisch als Wesen eingetragen. „-“ heißt: hier muss frei sein (ausgraben).

Am Ende schreibt schreiben() plaene.json (für farmhelper.py) und tests.json (für ../test/mctest.py).
"""
import json
import os
import textwrap

import bloecke

HIER = os.path.dirname(os.path.abspath(__file__))

# Zeichen, die in jedem Plan gelten (ein Plan kann sie überschreiben)
GRUND = {
    "#": "stone_bricks", "G": "glass", "W": "water", "L": "lava", "D": "dirt", "S": "sand", "C": "chest",
    "-": "luft", "P": "player", "R": "redstone", "F": "flowing_water",
    "<": ("hopper", "w"), ">": ("hopper", "e"), "^": ("hopper", "n"), "v": ("hopper", "s"), "H": ("hopper", "d"),
}
LEER = {".", " "}


def _eintrag(wert):
    """Zeichen-Wert → (id, p)."""
    if isinstance(wert, str):
        return wert, {}
    i, rest = wert[0], wert[1] if len(wert) > 1 else {}
    if isinstance(rest, str):
        return i, {"f": rest}
    return i, dict(rest)


def raster(text):
    zeilen = textwrap.dedent(text).split("\n")
    while zeilen and not zeilen[0].strip():
        zeilen.pop(0)
    while zeilen and not zeilen[-1].strip():
        zeilen.pop()
    return zeilen


class Farm:
    alle = []
    weitere_tests = {}                                   # Name → Test (mit "plan": Farm-id), z. B. Mechanik-Tests

    def __init__(self, fid, **info):
        self.id = fid
        self.info = dict(info)
        self.legende = dict(GRUND)
        self.steps = []
        self.test = None
        Farm.alle.append(self)

    def zeichen(self, **neu):
        self.legende.update(neu)
        return self

    def schritt(self, text, ebenen=None, x0=0, z0=0):
        added, luft = [], []
        for y, txt in (ebenen or {}).items():
            for dz, zeile in enumerate(raster(txt)):
                for dx, c in enumerate(zeile):
                    if c in LEER:
                        continue
                    if c not in self.legende:
                        raise KeyError(f"{self.id}: Zeichen {c!r} unbekannt (Schritt „{text[:40]}…“)")
                    i, p = _eintrag(self.legende[c])
                    pos = {"x": x0 + dx, "y": y, "z": z0 + dz}
                    if i == "luft":
                        luft.append(pos)
                        continue
                    ent = i in bloecke.LEBEWESEN
                    added.append(pos | {"id": i, "p": p, "ent": ent})
        self.steps.append({"text": text, "luft": luft, "added": added})
        return self

    def pruefe(self, **test):
        self.test = test
        return self

    def pruefe_auch(self, name, **test):
        """Zusätzlicher Test derselben Farm (z. B. Mobs hineinsetzen statt auf seltene Spawns zu warten)."""
        Farm.weitere_tests[name] = dict(test, plan=self.id)
        return self

    # ------------------------------------------------------------------ Ausgabe
    def fertig(self, schritte=None):
        stand = {}
        for st in (schritte if schritte is not None else self.schritte_mit_stuetzen()):
            for q in st["luft"]:
                stand.pop((q["x"], q["y"], q["z"], False), None)
            for b in st["added"]:
                stand[(b["x"], b["y"], b["z"], b["ent"])] = b
        return [dict(b) for b in stand.values()]

    # ------------------------------------------------------------------ Stützen
    def stuetzen(self):
        """Blöcke, die der Plan sonst stillschweigend aus dem Boden erwartet: Unter der Starthöhe (y < 0) brauchen
        Gruben, Schächte, Wasser und Blöcke feste Wände und einen Boden, auf Starthöhe (y = 0) alles einen Boden.
        Wer in die Erde baut, hat sie schon (jeder feste Block zählt); wer in der Luft baut, sieht sie als Geister.
        Liefert {Schritt-Nr: [Stütz-Blöcke]} – jede Stütze kommt in den Schritt, in dem sie zuerst gebraucht wird."""
        if self.info.get("ohne_stuetzen"):
            return {}
        erst = {}                                        # Position → erster Schritt, der dort etwas plant
        afk = set()
        for k, st in enumerate(self.steps):
            for q in st["luft"]:
                erst.setdefault((q["x"], q["y"], q["z"]), k)
            for b in st["added"]:
                erst.setdefault((b["x"], b["y"], b["z"]), k)
                if b["id"] == bloecke.AFK:
                    afk |= {(b["x"], b["y"], b["z"]), (b["x"], b["y"] + 1, b["z"])}
        frei = set(self.info.get("frei_lassen", []))     # Stellen, die offen bleiben müssen (Zugang, Quelle …)
        stuetze = {}
        for (x, y, z), k in sorted(erst.items(), key=lambda kv: kv[1]):
            if y > 0:
                continue
            nachbarn = [(x, y - 1, z)]
            if y < 0 and (x, y, z) not in afk:
                nachbarn += [(x + 1, y, z), (x - 1, y, z), (x, y, z + 1), (x, y, z - 1)]
            for n in nachbarn:
                if n in erst or n in afk or n in frei or n in stuetze:
                    continue
                stuetze[n] = k
        out = {}
        for (x, y, z), k in stuetze.items():
            out.setdefault(k, []).append({"x": x, "y": y, "z": z, "id": "fest", "p": {}, "ent": False})
        return out

    def schritte_mit_stuetzen(self):
        st = self.stuetzen()
        neu = []
        for k, s in enumerate(self.steps):
            s = dict(s)
            if st.get(k):
                s["added"] = sorted(st[k], key=lambda b: (b["y"], b["z"], b["x"])) + list(s["added"])
            neu.append(s)
        return neu

    def plan(self):
        f = {"id": self.id}
        f.update({k: self.info[k] for k in ("name", "cat", "diff", "out", "where", "afk", "why", "help")})
        f["verified"] = self.info.get("verified", True)
        f["meta"] = self.info.get("meta", {"rate": "", "ort": [], "meta": []})
        f["steps"] = [dict(s) for s in self.schritte_mit_stuetzen()]
        f["fertig"] = self.fertig(f["steps"])
        for b in f["fertig"]:                         # jeder Block muss übersetzbar sein
            if b["id"] not in bloecke.VON_SELBST:
                bloecke.block(b, 0)
        return f

    def material(self):
        """Grobe Materialliste (Block-id → Anzahl) aus dem fertigen Bau, ohne Lebewesen und Luft."""
        m = {}
        for b in self.fertig():
            if b["ent"] or b["id"] in bloecke.VON_SELBST or b["id"] in ("player",):
                continue
            m[b["id"]] = m.get(b["id"], 0) + 1
        return dict(sorted(m.items(), key=lambda kv: -kv[1]))


def schreiben(plaene_pfad=None, tests_pfad=None, reihenfolge=None):
    farmen = Farm.alle
    if reihenfolge:
        nach = {f.id: f for f in farmen}
        farmen = [nach[i] for i in reihenfolge if i in nach] + [f for f in farmen if f.id not in reihenfolge]
    plaene = [f.plan() for f in farmen]
    tests = {f.id: f.test for f in farmen if f.test}
    tests.update(Farm.weitere_tests)
    plaene_pfad = plaene_pfad or os.path.join(HIER, "plaene.json")
    tests_pfad = tests_pfad or os.path.join(HIER, "..", "test", "tests.json")
    with open(plaene_pfad, "w", encoding="utf-8") as d:
        json.dump(plaene, d, ensure_ascii=False, indent=1)
    with open(tests_pfad, "w", encoding="utf-8") as d:
        json.dump(tests, d, ensure_ascii=False, indent=1)
    return plaene, tests
