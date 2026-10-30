"""Prüft alle Pläne auf Fallen beim Bauen und gibt eine Liste aus (für die Durchsicht, nicht fürs Spiel).

- Flüssigkeit läuft im fertigen Bau aus (Nachbar seitlich/unten ist Luft und keine geplante Flüssigkeit)
- Flüssigkeit wird gesetzt, bevor ein Nachbarblock steht (läuft beim Bauen aus)
- Spawner und AFK-Platz weiter als 16 Blöcke auseinander
"""
import json, sys
import bloecke

FLUID = {"water", "lava", "flowing_water"}
SEITEN = [(1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1), (0, -1, 0)]
plaene = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "plaene.json"))
for f in plaene:
    fertig = {(b["x"], b["y"], b["z"]): b for b in f["fertig"] if not b.get("ent")}
    schritt = {}
    for k, s in enumerate(f["steps"]):
        for b in s["added"]:
            schritt.setdefault((b["x"], b["y"], b["z"]), k)
    meldungen = []
    belegt = set(fertig)
    xs = [p[0] for p in belegt]; ys = [p[1] for p in belegt]; zs = [p[2] for p in belegt]
    box = (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))
    drinnen = lambda p: box[0] <= p[0] <= box[1] and box[2] <= p[1] <= box[3] and box[4] <= p[2] <= box[5]
    for pos, b in fertig.items():
        if b["id"] not in ("water", "lava"):
            continue
        # Wohin kann die Flüssigkeit fließen? Seitlich höchstens 7 (Lava 3) Felder, nach unten immer
        weit = 7 if b["id"] == "water" else 3
        offen, gesehen, raus = [(pos, 0)], {pos}, None
        while offen and not raus:
            p, d = offen.pop()
            unten = (p[0], p[1] - 1, p[2])
            schritte = [unten] if unten not in belegt else [(p[0] + 1, p[1], p[2]), (p[0] - 1, p[1], p[2]),
                                                             (p[0], p[1], p[2] + 1), (p[0], p[1], p[2] - 1)]
            for n in schritte:
                if n in belegt or n in gesehen:
                    continue
                nd = d if n == unten else d + 1
                if nd > weit:
                    continue
                if not drinnen(n):
                    raus = n; break
                gesehen.add(n); offen.append((n, nd))
        if raus:
            meldungen.append(f"läuft aus dem Bau: {b['id']} {pos} → {raus}")
        for dx, dy, dz in SEITEN:
            n = (pos[0] + dx, pos[1] + dy, pos[2] + dz)
            nb = fertig.get(n)
            if nb is not None and nb["id"] not in FLUID and schritt.get(n, -1) > schritt[pos]:
                meldungen.append(f"zu früh: {b['id']} {pos} (Schritt {schritt[pos]}) vor Nachbar {nb['id']} {n} (Schritt {schritt[n]})")
    sp = [b for b in f["fertig"] if b["id"] == "spawner"]
    afk = [b for b in f["fertig"] if b["id"] == "player"]
    for s_ in sp:
        for a in afk:
            d = ((s_["x"] - a["x"]) ** 2 + (s_["y"] - a["y"]) ** 2 + (s_["z"] - a["z"]) ** 2) ** 0.5
            if d > 16:
                meldungen.append(f"AFK-Platz {d:.1f} Blöcke vom Spawner (max. 16)")
    if meldungen:
        print(f"== {f['id']}: {len(meldungen)}")
        for m in sorted(set(meldungen))[:6]:
            print("   ", m)
