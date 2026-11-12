"""Stöcke-Fabrik (Profi): Bambusfarm (2 × 16 auf Schlamm, Kolben von beiden Seiten, Beobachter je Stängel) liefert
über die Trichter direkt in einen Werker (Crafter) mit 7 gesperrten Feldern; Stöcke → Doppeltruhe.

Koordinaten (x West → Ost, z Nord → Süd):
  x 1..16 Bambus; z 0 Staub A (y 2) auf Blöcken (y 1), z 1 Kolben A (y 1, nach Süden) + Beobachter A (y 2),
  z 2 Bambus A, z 3 Bambus B (y 0, auf Schlamm y -1, darunter Trichter y -2 nach Westen),
  z 4 Kolben B (nach Norden) + Beobachter B, z 5 Staub B.
  Westende: Trichter (0, -2, 2) nach Süden in den Werker (0, -2, 3) (Gesicht Westen) ← Trichterreihe B;
  Werker → Doppeltruhe (-1, -2, 2/3). Takt: Beobachter (0, 0, 4) nach Süden und (0, 0, 5) nach Norden, der erste gibt
  seinen Impuls nach hinten in Redstone auf dem Block (0, -1, 3) über dem Werker.
"""
from profi_basis import *

N = 16                                                   # Stängel pro Reihe

f = profi("stockcrafter", dict(
    name="Stöcke-Fabrik (Profi)", diff=3, out="Stöcke (für Pfeilmacher-Smaragde), ganz ohne Nachfüllen",
    where="Überall mit freiem Himmel über dem Bambus (Licht ≥ 9 an der Spitze)",
    afk="Ja – in der Nähe bleiben (AFK-Platz am Westende), der Chunk muss laufen",
    why="Die einfache Fassung ist nur der Werker (Crafter), den du mit Bambus füttern musst. Die Profi-Fassung macht "
        "Stöcke ganz von selbst: Sie hat eine eigene Bambusfarm mit 32 Stängeln in zwei Reihen auf Schlamm. Von "
        "beiden Seiten zeigen Kolben hinein, und jeder Stängel hat einen Beobachter auf Höhe des 3. Blocks. Wird "
        "ein Stängel 3 hoch, gibt sein Beobachter einen Impuls nach hinten in den Redstone-Staub, und die Kolben "
        "seiner Reihe schlagen den 2. Block ab. Die Stücke fallen auf den Schlamm, und die Trichter darunter saugen "
        "sie hindurch. Alle 33 Trichter führen in EINEN Werker. Bei ihm sind 7 Felder gesperrt, frei sind nur links "
        "oben und links Mitte – genau das Stock-Rezept aus 2 Bambus übereinander. Ein Trichter füllt immer zuerst "
        "ein leeres freies Feld, darum liegt bald in beiden ein Bambus. Zwei Beobachter, die sich anschauen, geben "
        "einen dauernden Takt in den Staub auf dem Block über dem Werker, und bei jedem Impuls entsteht ein Stock. "
        "Der Stock landet in der Doppeltruhe vor dem Gesicht des Werkers. Ein Werker schafft mehrere Stöcke pro "
        "Sekunde – viel mehr, als der Bambus nachwächst. Darum reicht einer.",
    help=[["Keine Stöcke, aber Bambus im Werker",
           "Im Werker müssen genau 7 Felder gesperrt sein (leeres Feld anklicken), frei bleiben nur links oben und "
           "links Mitte. Sein Gesicht muss nach Westen zur Truhe zeigen. Und der Takt muss laufen: Die beiden "
           "Beobachter schauen sich an, Redstone liegt auf dem Block über dem Werker."],
          ["Der Werker zeigt nach oben oder unten",
           "Er schaut beim Setzen zu dir. Setz einen Hilfsblock östlich daneben, steh westlich davon im Graben, "
           "schau flach nach Osten und klick an die Westseite des Hilfsblocks. Danach den Hilfsblock abbauen."],
          ["Bambus wächst nicht oder ein Kolben feuert nicht",
           "Über der Spitze muss Licht ≥ 9 sein, also kein Dach. Jeder Beobachter auf einem Kolben schaut mit dem "
           "Gesicht zum Bambus, der rote Punkt zeigt nach hinten zum Staub. Beim Setzen flach zielen, nicht steil "
           "nach unten."],
          ["Truhe voll",
           "Eine Doppeltruhe fasst 3456 Stöcke, das reicht für etwa 12 Stunden. Beim Pfeilmacher gibt es für 32 "
           "Stöcke einen Smaragd."]],
    meta=m("Rate: etwa 280 Stöcke pro Stunde, also etwa 8–9 Smaragde beim Pfeilmacher (Schätzung: 32 Stängel, jeder "
           "wächst im Schnitt alle 4096 Ticks einen Block, das sind etwa 560 Bambus pro Stunde; aus 2 Bambus wird 1 "
           "Stock). Die einfache Fassung macht nur so viele Stöcke, wie du Bambus hineinlegst.",
           [("Überall. Nur über der Spitze muss Licht ≥ 9 sein, Wasser braucht es nicht.", W + "Tutorial:Bamboo_farming")],
           [("Doppelreihe Bambus auf Schlamm, Kolben von beiden Seiten nach innen, Trichter darunter.",
             W + "Tutorial:Bamboo_farming"),
            ("Bambus wächst bei jedem Zufallstick mit 1/3 Chance, im Schnitt alle 4096 Ticks (204,8 s) einen "
             "Block. Wird er von einem Kolben getroffen, fällt er als Item ab.", W + "Bamboo"),
            ("Werker: Gesperrte Felder nehmen nichts an. Trichter füllen zuerst leere Felder in Lesereihenfolge. "
             "4 Ticks nach einem Redstone-Signal entsteht ein Gegenstand, der in den Behälter vor dem Gesicht "
             "wandert.", W + "Crafter"),
            ("2 Bambus übereinander ergeben 1 Stock.", W + "Stick"),
            ("Pfeilmacher (Anfänger): 32 Stöcke gegen 1 Smaragd.", W + "Trading"),
            (TEST + "die einfache Fassung (7 Felder gesperrt, Beobachter-Takt) machte aus 128 Bambus 64 Stöcke, die "
                    "einfache Bambusfarm (8 Stängel, je ein Beobachter) brachte 245 Bambus in 30 min Zeitraffer. Die "
                    "Profi-Fassung verbindet beides mit viermal so viel Bambus.", None)])))

f.zeichen(M="mud", Z="bamboo", K=("piston", "s"), k=("piston", "n"), B=("observer", "s"), b=("observer", "n"),
          T=("chest", "w"), X=("crafter", "w"))

f.schritt("Ausheben: ein Graben 2 breit, 2 tief und 19 lang von West nach Ost.", {
    -1: "\n".join(["-" * (N + 3)] * 2),
    -2: "\n".join(["-" * (N + 3)] * 2)}, x0=-2, z0=2)
f.schritt("Der Werker (Crafter) kommt auf den Grabenboden, 3. Platz von Westen in der südlichen Reihe, und sein "
          "Gesicht muss nach Westen zeigen (er schaut beim Setzen zu dir). Setz dafür einen Hilfsblock (z. B. Erde) "
          "östlich daneben. Stell dich westlich davon in den Graben, schau flach nach Osten und klick an die "
          "Westseite des Hilfsblocks. Danach den Hilfsblock abbauen.", {
    -2: "X"}, x0=0, z0=3)
f.schritt("Trichter unten im Graben. Südliche Reihe: 16 Trichter nach Westen, den ersten schleichend an die Ostseite "
          "des Werkers klicken, jeden weiteren an die Ostseite des vorigen. Nördlich neben den Werker einen "
          "Trichter, schleichend an die Nordseite des Werkers geklickt – er zeigt nach Süden in den Werker. An "
          "seine Ostseite die nördliche Reihe mit 16 Trichtern nach Westen. Zuletzt westlich davon 2 Truhen (eine "
          "Doppeltruhe): von Westen her setzen, also nach Osten schauen. In die südliche legt der Werker die Stöcke.", {
    -2: """
        Tv<<<<<<<<<<<<<<<<
        T.<<<<<<<<<<<<<<<<
    """}, x0=-1, z0=2)
f.schritt("Schlamm auf alle Trichter (Erde setzen, mit der Wasserflasche zu Schlamm machen), auch auf den Trichter "
          "nördlich vom Werker. Auf den Werker kommt ein normaler Block (schleichend klicken) – kein Schlamm, auf "
          "ihn kommt später Redstone.", {
    -1: "\n".join(["M" * (N + 1), "#" + "M" * N])}, x0=0, z0=2)
f.schritt("Nördlich und südlich des Grabens je 16 Blöcke auf den Boden, darauf Kolben, die zum Bambus zeigen: Stell "
          "dich auf den Schlamm davor, schau zum Block und klick oben drauf – der Kolben zeigt zu dir (nördliche "
          "Reihe nach Süden, südliche nach Norden).", {
    0: "\n".join(["#" * N, "." * N, "." * N, "#" * N]),
    1: "\n".join(["K" * N, "." * N, "." * N, "k" * N])}, x0=1, z0=1)
f.schritt("Hinter jeden Kolben ein Block (an die Rückseite des Kolbens klicken). Dann auf jeden Kolben ein "
          "Beobachter, dessen Gesicht zum Bambus schaut: Stell dich schleichend an die Außenkante der Blockreihe "
          "und ziel flach über den Kolben Richtung Graben (nicht steil nach unten) – der rote Punkt zeigt dann zu "
          "dir.", {
    1: "\n".join(["#" * N] + ["." * N] * 4 + ["#" * N]),
    2: "\n".join(["." * N, "B" * N, "." * N, "." * N, "b" * N])}, x0=1, z0=0)
f.schritt("Redstone-Staub auf beide Blockreihen hinter den Beobachtern: rückwärts über die Reihe gehen und den Staub "
          "vor dir legen. Jeder Beobachter gibt seinen Impuls nach hinten in den Staub, der alle Kolben der Reihe "
          "schaltet.", {
    2: "\n".join(["R" * N] + ["." * N] * 4 + ["R" * N])}, x0=1, z0=0)
f.schritt("Takt für den Werker, auf dem Boden südlich vom Block über dem Werker. Erst den hinteren Beobachter: Stell "
          "dich ein paar Blöcke weiter südlich hin, schau nach Norden und klick oben auf den Boden 2 Blöcke südlich "
          "vom Graben. Dann den vorderen: Stell dich auf den Schlamm nördlich vom Block über dem Werker, schau nach "
          "Süden und klick an die Nordseite des ersten Beobachters. Die beiden schauen sich jetzt an und takten. Zum "
          "Schluss Redstone-Staub auf den Block über dem Werker – der vordere Beobachter gibt seinen Takt hinein.", {
    0: """
        R
        B
        b
    """}, x0=0, z0=3)
f.schritt("Bambus auf die 32 Schlammblöcke – fertig. Wird ein Stängel 3 hoch, schlagen die Kolben seiner Reihe den "
          "2. Block ab, alles läuft in den Werker, und die Stöcke landen in der Truhe. Im Werker müssen dafür 7 "
          "Felder gesperrt sein, frei bleiben nur links oben und links Mitte.", {
    0: "\n".join(["Z" * N] * 2)}, x0=1, z0=2)
f.schritt("Hier warten (in der Nähe bleiben, sonst wächst nichts).", {0: "P"}, x0=-3, z0=3)

# Test wie bei der einfachen Fassung: Felder per Befehl sperren (im Spiel: anklicken). Gemessen: Stöcke in den Truhen –
# hier ohne vorgefüllten Bambus, alles kommt aus der eigenen Farm (Zufallsticks 10, 36000 Ticks).
f.pruefe(boden=GRAS, nachher=["data merge block {x} {y-2} {z+3} {disabled_slots:[I;1,2,4,5,6,7,8]}"],
         erwartet={"items": {"minecraft:stick": 150}})
