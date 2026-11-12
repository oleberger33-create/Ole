"""Honigwaben-Farm (Profi): 8 Bienenstöcke in einer Reihe (x 0 … 7, z 0), Öffnung nach Norden, je 3 Bienen.

Je Stock (Spalte x): Trichter (x, -1, 0) direkt UNTER dem Stock, alle nach Osten in die Truhe (8, -1, 0); Stock
(x, 0, 0); Werfer mit Schere dahinter (x, 0, 1), zeigt nach Norden auf den Stock; Beobachter auf dem Stock (x, 1, 0),
schaut nach unten auf den Stock (Ausgang oben); darauf ein Block S (x, 2, 0), den der Beobachter stark mit Strom
versorgt. Auf jedem Werfer ein Block T (x, 1, 1), darauf Redstone-Staub (x, 2, 1): eine Leitung über alle Werfer,
direkt neben den Blöcken S. Blume vor jedem Stock (x, 0, -1). Seitlich zu: Steinziegel (-1, 0, 0) im Westen, Glas (8, 0, 0)
auf der Truhe im Osten.

Warum nicht Staub direkt auf Beobachter und Werfer: Beobachter leiten keinen Strom, Staub auf einem Beobachter gibt
sein Signal nicht eine Stufe nach unten weiter (Wiki: Observer). Darum liegt die Leitung auf gleicher Höhe wie die Blöcke S.

Ablauf: Jede Änderung der Honigstufe eines Stocks → sein Beobachter gibt einen Puls in S → die Staubleitung daneben
schaltet alle Blöcke T → alle 8 Werfer darunter versuchen zu scheren.
Nur bei vollem Stock (Stufe 5) klappt es; die 3 Waben entstehen IM Stock, der Trichter darunter saugt sie an (Java:
Bienenstöcke blockieren Trichter nicht). Fehlversuche kosten die Schere nichts.
"""
from profi_basis import *

N = 8                                         # Bienenstöcke
OST = N                                       # x der Truhe


f = profi("honig", dict(
    name="Honigwaben-Farm (Profi)", diff=3, out="Honigwaben (Kerzen, Bienenstöcke, Wachs für Kupfer)",
    where="Auf Gras oder Erde, Grundfläche 10 × 3 (mit Platz davor und dahinter etwa 12 × 6); Bienen aus "
          "Bienennestern (mit Behutsamkeit abgebaut) oder mit Blumen vermehrt",
    afk="Ja (in der Nähe bleiben, Simulationsdistanz)",
    why="Acht Bienenstöcke statt einem Nest, mit je 3 Bienen – achtmal so viel Honig. Jeder Stock steht direkt auf "
        "einem Trichter: In Java entstehen die Waben beim Scheren mitten im Stock, und ein Trichter darunter saugt "
        "sie durch den Stock hindurch an (Bienenstöcke und -nester blockieren Trichter nicht) – nichts fliegt mehr "
        "herum. Alle Trichter führen nach Osten in eine Truhe. Hinter jedem Stock zeigt ein Werfer mit Schere auf "
        "ihn. Statt eines Dauertakts schaut auf jedem Stock ein Beobachter nach unten: Bei jeder neuen Honigstufe "
        "gibt er einen Puls in den Block über sich, die Redstone-Leitung daneben (auf Blöcken über den Werfern) "
        "schaltet alle 8 Werfer, und sie versuchen zu scheren. Nur ein voller Stock (Stufe 5) gibt 3 Waben her; "
        "bei den anderen passiert nichts, die Schere "
        "nutzt sich dabei nicht ab und die Bienen werden nicht wütend. Vor jedem Stock steht eine Blume: Die Bienen "
        "kommen vorne heraus und sammeln sofort, statt Blumen zu suchen.",
    help=[["Ein voller Stock wird nicht geleert", "Liegt in seinem Werfer eine Schere? Der Werfer muss nach Norden "
                                                 "auf den Stock zeigen, der Beobachter auf dem Stock nach unten "
                                                 "(roter Punkt oben), auf ihm ein fester Block, direkt daneben "
                                                 "die Staubleitung auf den Blöcken über den Werfern. Sobald "
                                                 "irgendein Stock eine Stufe weiter ist, versuchen es alle Werfer "
                                                 "erneut."],
          ["Waben liegen vor den Stöcken", "Jeder Stock muss direkt auf einem Trichter stehen, links und rechts "
                                           "müssen Stöcke bzw. die Endblöcke sein, oben der Beobachter, hinten der "
                                           "Werfer – nur vorne frei. Zeigt ein Trichter in einen Block statt zum "
                                           "nächsten Trichter, staut sich alles."],
          ["Bienen kommen nicht in die Stöcke", "Ein Stock fasst 3 Bienen; Bienen ohne Zuhause suchen sich in der "
                                                "Nähe einen Stock mit Platz. Vorne vor der Öffnung darf nur die "
                                                "Blume stehen. Nachts und bei Regen bleiben alle drin – das ist "
                                                "normal."],
          ["Mehr Bienen", "Zwei Bienen mit einer Blume füttern: Sie bekommen ein Junges (alle 5 Minuten). Stöcke "
                          "baust du aus 6 Brettern und 3 Waben aus der einfachen Farm."]],
    meta=m("Rate: etwa 70 Waben pro Stunde im Tag-Nacht-Wechsel, bei Dauer-Tag rund 140 (Schätzung: die einfache "
           "Farm gab auf dem Testserver mit einem Nest und 3 Bienen 9 Waben in 30 Minuten Tag; hier arbeiten 8 "
           "Stöcke mit je 3 Bienen, die Blumen stehen direkt vor der Öffnung). Bienen sammeln nur tagsüber und "
           "ohne Regen.",
           [("Überall auf Gras oder Erde; Bienen und das erste Nest gibt es in Blumenwald, Ebene, Sonnenblumenebene, "
             "Wiese, Birken- und Kirschwald. Mit Behutsamkeit abgebaute Nester behalten ihre Bienen.",
             W + "Tutorial:Honey_farming")],
           [("Automatisch ernten: Werfer mit Schere zeigt auf den Stock; ein Beobachter am Stock löst bei jeder "
             "neuen Honigstufe aus – bei nicht vollem Stock nutzt sich die Schere nicht ab. Ernten per Werfer macht "
             "die Bienen nicht wütend.", W + "Tutorial:Honey_farming#Automatic_harvesting"),
            ("Java: Die Waben entstehen im Stock und werden von einem Trichter darunter eingesammelt.",
             W + "Tutorial:Honey_farming#Automatic_harvesting"),
            ("Trichter sammeln auch Items in Bienennestern und -stöcken über ihnen (Tag does_not_block_hoppers).",
             W + "Hopper#Bee_nests_and_beehives"),
            ("Ein Stock fasst 3 Bienen; sie verlassen ihn nur durch die Öffnung vorne. Jede Biene mit Pollen hebt "
             "die Honigstufe um 1, bei Stufe 5 gibt Scheren 3 Waben.", W + "Beehive"),
            ("Ein Stock zeigt mit der Öffnung zu dem, der ihn setzt; Werfer zeigen zum Spieler, Beobachter "
             "schauen in die Blickrichtung.", W + "Beehive#Block_states"),
            ("Beobachter geben einen starken Puls (Stärke 15) in den Block hinter sich; sie leiten selbst keinen "
             "Strom, Staub auf ihnen gibt kein Signal nach unten weiter.", W + "Observer"),
            ("Redstone-Staub schaltet den Block, auf dem er liegt; ein so geschalteter Block schaltet Werfer daneben.",
             W + "Redstone_Dust"),
            (TEST + "einfache Variante: Werfer mit Schere erntet ein volles Nest, Glasflaschen würden bei nicht "
                    "vollem Nest herausfliegen.", None)])))

f.zeichen(N=("bee_nest", "n"), D=("dispenser", "n"), O=("observer", "d"), Y="poppy", X="bee")

f.schritt(f"Ausheben: ein Graben 1 tief und {N + 1} lang von West nach Ost (für {N} Trichter und die Truhe).", {
    -1: "-" * (N + 1)})
f.schritt(f"Truhe ans Ostende, dann {N} Trichter, die alle nach Osten zeigen: schleichend den ersten an die Truhe "
          "klicken, jeden weiteren an den vorigen (ein Trichter zeigt in den Block, an den du klickst).", {
    -1: ">" * N + "C"})
f.schritt(f"Südlich neben der Trichterreihe {N} Werfer auf den Boden, die nach Norden zeigen. Ein Werfer zeigt beim "
          "Setzen zu dir: Stell dich nördlich der Trichterreihe hin (2–3 Blöcke von den Werfern weg) und schau flach "
          "nach Süden – nicht steil nach unten, sonst zeigt er nach oben. In jeden Werfer eine Schere.", {
    0: "D" * N}, z0=1)
f.schritt(f"Auf jeden Trichter einen Bienenstock (oder ein Bienennest), die Öffnung nach Norden: Ein Stock zeigt mit "
          "der Öffnung zu dir – von Norden her nach Süden schauen und schleichend oben auf den Trichter klicken. "
          "Im Westen neben den ersten Stock einen Steinziegel, im Osten schleichend Glas auf die Truhe (dann geht sie "
          "noch auf): "
          "Die Waben dürfen nur nach vorne heraus.", {
    0: "#" + "N" * N + "G"}, x0=-1)
f.schritt("Auf jeden Stock einen Beobachter, der nach unten auf den Stock schaut: Stell dich auf die Werfer, schau "
          "steil nach unten auf die Oberseite des Stocks und setz ihn – der rote Punkt zeigt dann nach oben.", {
    1: "O" * N})
f.schritt("Auf jeden Beobachter einen Steinziegel (dafür auf den Werfern stehen, dann siehst du die Oberseite) – "
          "der Beobachter schaltet ihn bei jeder neuen Honigstufe. Dann von hinten (Süden) schleichend auf jeden Werfer "
          "einen Steinziegel.", {
    2: "#" * N,
    1: "." * N + "\n" + "#" * N})
f.schritt("Redstone-Staub auf die Steinziegel über den Werfern: Stell dich dafür hinter den Werfern auf einen "
          "Hilfsblock (danach abbauen), vom Boden aus siehst du die Oberseiten nicht. Die Leitung liegt direkt neben "
          "den Steinziegeln auf den Beobachtern: Ändert sich ein Stock, schaltet sie alle Steinziegel über den "
          "Werfern, und alle Werfer versuchen zu scheren.", {
    2: "R" * N}, z0=1)
f.schritt("Vor jeden Stock eine Blume (auf Gras oder Erde) – dort kommen die Bienen heraus.", {
    0: "Y" * N}, z0=-1)
f.schritt(f"Bienen holen: 3 je Stock, zusammen {3 * N}. Mit Behutsamkeit abgebaute Nester haben ihre Bienen schon drin "
          "(mit der Öffnung nach Norden setzen); sonst Bienen mit einer Blume in der Hand herlocken und vermehren – "
          "Bienen ohne Zuhause ziehen von selbst in einen Stock mit Platz.", {
    0: "X" * N}, z0=-2)
f.schritt("Dein Platz neben der Truhe – Bienen arbeiten nur, wenn du in der Nähe bist.", {0: "P"}, x0=OST + 2, z0=1)

# Test wie bei der einfachen Farm: alle Stöcke auf Honigstufe 3, je 3 Bienen mit diesem Stock als Zuhause.
nachher = ["kill @e[type=minecraft:bee,x={x},y={y},z={z},distance=..14]"]
for x in range(N):
    nachher += [f"setblock {{x{x:+d}}} {{y}} {{z}} minecraft:bee_nest[facing=north,honey_level=3]",
                f"item replace block {{x{x:+d}}} {{y}} {{z+1}} container.0 with minecraft:shears"]
    nachher += mobs("bee", [(x, 1, -1)] * 3, f"PersistenceRequired:1b,hive_pos:[I;{{x{x:+d}}},{{y}},{{z}}]")
f.pruefe(boden=GRAS, zeit="day", nachher=nachher, erwartet={"items": {"minecraft:honeycomb": 36}})
