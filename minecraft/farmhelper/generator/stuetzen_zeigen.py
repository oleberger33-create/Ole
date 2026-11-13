#!/usr/bin/env python3
"""Plan mit automatischen Stützen Ebene für Ebene zeigen: python3 stuetzen_zeigen.py <farm-id>

Zeichen: + = automatische Stütze (fester Block), - = ausgraben/frei, P = AFK-Platz, ~ = Wasser, sonst Buchstaben je
Block (Legende unten). Zeilen = Norden → Süden, Spalten = Westen → Osten; Höhe 0 = Füße beim Start.
"""
import sys
import entwurf
import farmen  # noqa: F401  (lädt alle Farmen inkl. Profi)

fid = sys.argv[1]
f = [f for f in entwurf.Farm.alle if f.id == fid][0]
plan = f.plan()
pos, zeichen = {}, {}
frei = iter("ABCDEFGHIJKLMNOQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789")
for st in plan["steps"]:
    for q in st["luft"]:
        pos[(q["x"], q["y"], q["z"])] = "-"
for b in plan["fertig"]:
    i = b["id"]
    c = {"fest": "+", "player": "P", "water": "~", "flowing_water": "~", "luft": "-"}.get(i)
    if c is None:
        k = i + (":" + b["p"].get("f", "") if b.get("p", {}).get("f") else "")
        if k not in zeichen:
            zeichen[k] = next(frei)
        c = zeichen[k]
    pos[(b["x"], b["y"], b["z"])] = c
xs = [p[0] for p in pos]; ys = [p[1] for p in pos]; zs = [p[2] for p in pos]
print(f"== {fid}: {plan['name']}\nOrt: {plan['where']}\nAFK: {plan['afk']}\n")
for n, st in enumerate(plan["steps"], 1):
    print(f"{n}. {st['text']}")
print()
for y in range(max(ys), min(ys) - 1, -1):
    print(f"y {y}:")
    for z in range(min(zs), max(zs) + 1):
        print("   " + "".join(pos.get((x, y, z), ".") for x in range(min(xs), max(xs) + 1)))
print("Legende: + Stütze, - frei/ausgraben, P AFK, ~ Wasser, " + ", ".join(f"{c}={k}" for k, c in zeichen.items()))
