#!/usr/bin/env python3
"""Profi-Variante selbst prüfen: python3 profi_pruefen.py <farm> [--ebenen]

Lädt generator/profi/<farm>.py allein, übersetzt jeden Block in allen 4 Drehungen (wie das Datapack), zeigt
Schritte, Material, Größe, AFK-Platz und Test. Mit --ebenen auch den fertigen Bau Ebene für Ebene
(Zeilen = Norden → Süden, Spalten = Westen → Osten; Legende darunter).
"""
import importlib
import json
import sys
from collections import Counter

import bloecke
import entwurf

fid = sys.argv[1]
mod = importlib.import_module("profi." + fid)
farmen = [f for f in entwurf.Farm.alle if f.id == fid + "_profi"]
assert farmen, f"profi/{fid}.py legt keine Farm {fid}_profi an (profi(\"{fid}\", …))"
f = farmen[0]
plan = f.plan()                                   # prüft Textfelder und übersetzt jeden Block einmal
for b in plan["fertig"]:
    if b["id"] not in bloecke.VON_SELBST:
        for r in range(4):
            bloecke.block(b, r)
fertig = plan["fertig"]
fest = [b for b in fertig if not b["ent"] and b["id"] not in ("player",)]
wesen = [b for b in fertig if b["ent"]]
afk = [b for b in fertig if b["id"] == "player"]
print(f"== {f.id}: {plan['name']} ({len(plan['steps'])} Schritte)")
for n, st in enumerate(plan["steps"], 1):
    print(f"  {n:2}. {st['text'][:150]}{'…' if len(st['text']) > 150 else ''}  "
          f"[+{len(st['added'])} Blöcke/Wesen, {len(st['luft'])} ausgraben]")
xs = [b["x"] for b in fertig]; ys = [b["y"] for b in fertig]; zs = [b["z"] for b in fertig]
print(f"Größe: x {min(xs)}..{max(xs)}, y {min(ys)}..{max(ys)}, z {min(zs)}..{max(zs)}")
mat = f.material()
print("Material:", json.dumps(mat, ensure_ascii=False), "| Summe", sum(mat.values()))
print("Wesen:", dict(Counter(b["id"] for b in wesen)), "| AFK-Platz:", [(b["x"], b["y"], b["z"]) for b in afk])
if not afk:
    print("!! Kein AFK-Platz (P) – ist das Absicht (Farm ohne Warteplatz)?")
tests = {k: v for k, v in entwurf.Farm.weitere_tests.items() if v.get("plan") == f.id}
if f.test:
    tests = {f.id: f.test} | tests
print("Tests:", json.dumps(tests, ensure_ascii=False) if tests else "!! keiner")
if "--ebenen" in sys.argv:
    zeichen = {}
    frei = iter("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789")
    pos = {}
    for b in fertig:
        schl = b["id"] + (":" + b["p"].get("f", "") if b.get("p", {}).get("f") else "")
        if schl not in zeichen:
            zeichen[schl] = next(frei)
        pos[(b["x"], b["y"], b["z"])] = zeichen[schl]
    luft = {(q["x"], q["y"], q["z"]) for st in plan["steps"] for q in st["luft"]}
    for y in range(max(ys), min(ys) - 1, -1):
        zeilen = []
        for z in range(min(zs), max(zs) + 1):
            zeilen.append("".join(pos.get((x, y, z), "-" if (x, y, z) in luft else ".") for x in range(min(xs), max(xs) + 1)))
        if any(c != "." for zl in zeilen for c in zl):
            print(f"y {y}:")
            print("\n".join("   " + zl for zl in zeilen))
    print("Legende: " + ", ".join(f"{c}={k}" for k, c in zeichen.items()) + ", -=ausgraben, .=nichts")
