"""Kaktus-Farm (Profi): 42 Kakteen auf Sand, der auf frei hängenden Steinziegeln sitzt; darunter eine flache
Wasserfläche, die von beiden Rändern zur Mitte fließt und alles in eine Trichterreihe treibt. Holzzäune (dünn,
aber „fest“) brechen das neue Kaktusstück ab. Kein Redstone.

Koordinaten: Grube x 1..15 (Westen → Osten), z 0..12 (Norden → Süden), 2 tief (y -1 und y -2).
Kakteen bei x 2, 4, …, 14 und z 1, 3, …, 11 (Sand y 0 auf Steinziegel y -1, Kaktus y 1).
Wasser y -2: Quellen in den Spalten x 1 und x 15, Treffpunkt x 8 über den Trichtern (y -3) → Truhe (8, -3, 13), Schacht darüber.
Zaunreihen y 2 über z 2, 6, 10 (x 2..16), am Ostrand auf 2 Zäunen bei x 16.
"""
from profi_basis import *

X, Z = 15, 13                                            # Grube: Breite (x 1..15), Tiefe (z 0..12)
MITTE = 8                                                # Trichter-Spalte (dort treffen sich beide Strömungen)
ZAUN = (2, 6, 10)                                        # z der Zaunreihen


def gitter(c):
    """Kaktus-Gitter: Zeichen c bei geradem x (2..14) in ungeraden Reihen (z 1..11), Raster ab x 1, z 0."""
    return "\n".join((".".join([""] + [c] * 7 + [""]) if z % 2 else "." * X) for z in range(Z))


def spalte(c, bis):
    """Zeichen c nur in der Mitte (x 8), Reihen z 0..bis."""
    return "\n".join("." * (MITTE - 1) + c + "." * (X - MITTE) for _ in range(bis + 1))


def zaunreihen(zeile):
    """Raster ab x 1, z 0 bis z 10: Zeile an den Zaun-Reihen, sonst leer."""
    return "\n".join(zeile if z in ZAUN else "." * len(zeile) for z in range(max(ZAUN) + 1))


f = profi("kaktus", dict(
    name="Kaktus-Farm (Profi)", diff=2, out="Kaktus → grüner Farbstoff, viel XP im Ofen",
    where="Überall (keine Wüste nötig – Sand mitbringen)",
    afk="Ja – in der Nähe bleiben (AFK-Platz an der Truhe), der Chunk muss laufen",
    why="42 Kakteen statt 3 und viel weniger Verlust. Jeder Kaktus steht auf einem Sandblock, der auf einem frei "
        "hängenden Steinziegel sitzt; darunter fließt eine flache Wasserfläche. Wächst ein Kaktus, berührt das neue "
        "Stück einen Holzzaun und bricht ab. Zäune sind dünn: Die Stücke prallen kaum ab, gut die Hälfte fällt neben "
        "den Kaktus statt darauf (dort würden sie zerstört). Sie fallen zwei Ebenen tief ins Wasser – weit weg von "
        "allen Kakteen, und es gibt keinen Sand, auf dem etwas liegen bleibt (bei der einfachen Farm blieben Stücke "
        "zwischen den Kakteen liegen, und die Glasstange warf mehr zurück auf den Kaktus). Das Wasser fließt von "
        "beiden Rändern 7 Blöcke weit zur Mitte und treibt alles zu einer Trichterreihe, die in eine Truhe führt. "
        "Kein Redstone.",
    help=[["Kakteen gehen beim Setzen kaputt",
           "Neben dem Kaktus darf auf seiner Höhe nichts stehen – die Zäune hängen eine Ebene höher, genau über den "
           "Lücken zwischen zwei Kaktusreihen."],
          ["Ein Kaktus wächst nicht mehr",
           "Oben sitzt eine Kaktusblüte (sie wächst nur, solange noch kein Zaun daneben ist) – abbauen."],
          ["Items bleiben im Wasser stehen",
           "Die ganze West- und die ganze Ostspalte der Grube müssen Quellen sein, sonst nirgends: Dann trifft sich "
           "das Wasser genau in der Mitte über den Trichtern. Kein Block darf unten im Wasser stehen."],
          ["Weniger als erwartet",
           "Etwa 4 von 10 Stücken fallen zurück auf den Kaktus und werden zerstört – das lässt sich nicht vermeiden. "
           "Die Truhe fasst etwa 1700 Kakteen (rund 20 Stunden): rechtzeitig leeren."]],
    meta=m("≈ 80 Kakteen pro Stunde (Schätzung: 42 Kakteen, je ein Stück im Schnitt alle 18 Minuten, etwa 40 % "
           "fallen zurück auf den Kaktus)",
           [("Überall – Kakteen brauchen nur Sand, weder Licht noch Wasser.", W + "Cactus")],
           [("Kaktus bricht ab, sobald neben dem neuen Stück ein Block steht. Dünne Blöcke wie Zaunpfosten sind am "
             "besten: Die Stücke fallen eher neben den Kaktus als darauf.", W + "Tutorial:Cactus_farming"),
            ("Ein Kaktus zerstört Items, die ihn berühren; er wächst alle 16 Zufallsticks (≈ 18 min) und setzt "
             "keine Blüte an, wenn neben dem Platz darüber ein Block steht.", W + "Cactus"),
            ("Zäune zählen immer als „fester“ Block (alte Solid-Eigenschaft) – genau das bricht Kakteen.",
             W + "Block_properties/Solid_(legacy)"),
            ("Wasser fließt 7 Blöcke weit: Quellen an beiden Rändern einer 15 breiten Fläche treffen sich genau in "
             "der Mitte.", W + "Water")])))

f.zeichen(S="sand", K="cactus", Y="oak_fence", T=("chest", "n"))

f.schritt("Grube 15 × 13 ausheben – zuerst nur 1 tief.", {-1: flaeche("-", X, Z)}, x0=1, z0=0)
f.schritt("Auf den Grubenboden 42 Steinziegel als Gitter: in jeder 2. Reihe (Reihe 2, 4, …, 12 von Norden) auf "
          "jeden 2. Platz (Spalte 2, 4, …, 14 von Westen), nie am Rand. Auf jeden Steinziegel einen Sandblock.", {
    -1: gitter("#"),
    0: gitter("S")}, x0=1, z0=0)
f.schritt("Jetzt die Schicht darunter ausheben – überall, auch unter den Steinziegeln: Sie bleiben in der Luft "
          "hängen, der Sand darauf hält. In der Mitte (Spalte 8) eine Rinne noch 1 tiefer für die Trichter, an ihrem "
          "Südende außerhalb der Grube ein Schacht 3 tief für die Truhe.", {
    -1: "\n".join(["." * X] * Z + [spalte("-", 0)]),
    -2: "\n".join([flaeche("-", X, Z), spalte("-", 0)]),
    -3: spalte("-", Z)}, x0=1, z0=0)
f.schritt("Truhe unten in den Schacht (aus der Grube auf den Schachtboden klicken). Dann 13 Trichter in die Rinne, "
          "alle nach Süden: schleichend an die Nordseite der Truhe klicken, jeden weiteren an die Nordseite des "
          "vorigen.", {
    -3: "\n".join([spalte("v", Z - 1), spalte("T", 0)])}, x0=1, z0=0)
f.schritt("Drei Zaunreihen auf Höhe der Kaktusspitzen, je zwischen zwei Kaktusreihen (über Reihe 3, 7 und 11 von "
          "Norden): Am Ostrand neben der Grube 3 Zäune übereinander, von dort die Reihe nach Westen bis über "
          "Spalte 2. Stell dich dazu auf die Sandblöcke daneben.", {
    0: zaunreihen("." * X + "Y"),
    1: zaunreihen("." * X + "Y"),
    2: zaunreihen("." + "Y" * X)}, x0=1, z0=0)
f.schritt("Wasser unten in die Grube: in die westlichste und die östlichste Spalte je 7 Eimer auf jeden 2. Platz "
          "(ab der Nordecke) – dazwischen entstehen von selbst Quellen. Das Wasser fließt von beiden Seiten 7 "
          "Blöcke weit und trifft sich genau über den Trichtern in der Mitte.", {
    -2: flaeche("W" + "F" * (X - 2) + "W", 1, Z)}, x0=1, z0=0)
f.schritt("Kakteen auf die 42 Sandblöcke – fertig. Die Reihen am Rand setzt du vom Boden aus, die inneren von einem "
          "Sandblock der Nachbarreihe, auf dem noch kein Kaktus steht (über die Zäune kommst du nicht). Nicht an "
          "die Kakteen stoßen – sie piksen.", {
    1: gitter("K")}, x0=1, z0=0)
f.schritt("Hier warten – die Truhe liegt im Schacht vor dir.", {0: "P"}, x0=MITTE, z0=Z + 1)

f.pruefe(boden=GRAS, erwartet={"items": {"minecraft:cactus": 40}})
