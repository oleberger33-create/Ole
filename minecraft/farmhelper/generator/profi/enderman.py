"""Enderman-Farm im End (Profi): Endermilben-Köder (Boot in der Mitte, Dach 3 × 3 zwei Blöcke über der Plattform) auf
einer Plattform 19 × 19 statt 9 × 9, die Endermilbe auf einem ganzen Block (Sichtlinie über die große Plattform), unten
ein Trichterboden mit Doppeltruhe: voll AFK, keine Perle verschwindet.

Servertest 1 (Loch 5 × 5, 2 breit, um einen einzelnen Mittelblock): Endermilbe nach ~14 Endermen tot. Ursache: Ein
Enderman, der ins Loch tritt, steuert im Fallen weiter zur Endermilbe. Sobald sein Kopf unter dem Dach ist (Füße 0,9
unter der Plattform), kann er darunter treiben, während sein Körper noch auf Höhe der Endermilbe ist – dann reicht sein
Schlag (Mitte ≤ 1,33) oder das Boot nimmt ihn als zweiten Fahrgast auf (≤ 1,19). Darum sind jetzt alle 3 × 3 Blöcke
unter dem Dach massiv (Plattformhöhe): Über ihnen sind nur 2 Blöcke bis zum Dach, unter ihnen ist der Körper schon
unter der Endermilbe. Kein Enderman kommt näher als Mitte 1,8 (nachgerechnet für jede Höhe: Angriffsbox bleibt
0,67 von der Endermilbe weg, Boot-Aufnahmebox 0,61) – weder zu Fuß, beim Fallen noch beim Teleportieren. Das Loch ist
damit ein Ring 1 breit (16 Felder): Übersteigen geht nicht, weil hinter dem Ring nur 2 Blöcke Platz sind.

Gebaut wird von unten nach oben. Ursprung (0, 0, 0) = Warteplatz unten (Füße), Stufe darunter.
Unten (y 0): Trichterboden 5 × 5 bei x -7 … -3, z -2 … 2, Ausgang (-2, 0, 0) → Doppeltruhe (-1, 0 … 1, 0),
Ring aus Endstein auf y 0, Glasrand auf y 1. Gerüst-Säule (0, 0 … 44, 1).
Oben: Plattform 19 × 19 auf y 44 (x -14 … 4, z -9 … 9), massiver Innenbereich 3 × 3 um den Mittelblock (-5, 44, 0),
Lochring 1 breit darum (x -7 … -3, z -2 … 2), Boot + Endermilbe auf (-5, 45, 0), Dach aus unteren Stufen auf y 47.
Fall: Oberseite 45 → Trichter-Oberkante 1 = 44 Blöcke = 41 Schaden (Enderman 40 Leben).
"""
from profi_basis import *

f = profi("enderman", dict(
    name="Enderman-Farm im End (Profi)", diff=4, out="Enderperlen",
    where="Im End, mindestens 128 Blöcke von jeder anderen Insel; unten möglichst tief bauen (über Höhe 0), die "
          "Plattform liegt 44 Blöcke höher",
    afk="Ja – unten neben der Truhe, 45 Blöcke unter der Plattform",
    why="Endermen hassen Endermilben. Eine Endermilbe mit Namensschild sitzt in einem Boot auf dem Mittelblock, über "
        "ihm und seinen 8 Nachbarn ein Dach 3 × 3, zwei Blöcke über der Plattform. Rund um diese 3 × 3 Blöcke liegt ein "
        "Lochring mit offenen Falltüren (sie halten sie für Boden). Endermen wollen zur Endermilbe, treten auf die "
        "Falltüren und fallen 44 Blöcke tief: 41 Schaden, sie haben 40 Leben. Die 3 × 3 Blöcke unter dem Dach sind "
        "massiv – das ist der Kern: Darüber sind nur 2 Blöcke Platz (ein Enderman ist 2,9 hoch), und wer in den Ring "
        "fällt, kann erst unter das Dach treiben, wenn er schon unter der Endermilbe ist. So kommt keiner in "
        "Schlagweite oder ins Boot – weder zu Fuß noch beim Fallen oder Teleportieren. (Mit einem offenen Loch bis an "
        "den Mittelblock trieb im Test ein fallender Enderman unter das Dach und erschlug sie.) Der Ring darf hier 1 "
        "breit sein: Hinüber steigen geht nicht, dahinter ist kein Platz. Besser als die einfache Farm: Die Plattform "
        "ist 19 × 19 statt 9 × 9. Weit und breit ist sie der einzige Boden, also spawnen alle Endermen dort – auf etwa "
        "5-mal so viel Fläche (335 statt 65 Felder). Die Endermilbe sitzt auf einem ganzen Block statt auf einer "
        "Stufe, also einen halben Block höher: So sehen sie auch Endermen am Rand der großen Plattform (auf der Stufe "
        "läge ihr Kopf unter der Plattform-Oberkante). Unten landen die Endermen auf 25 Trichtern; die bringen jede "
        "Perle in eine Doppeltruhe neben deinem Warteplatz – nichts einsammeln, nichts verschwindet nach 5 Minuten. "
        "Das Dach ist aus unteren Stufen, unten liegen nur Trichter, Glas, Truhen und eine Stufe: Darauf spawnt "
        "nichts. Gebaut wird von unten nach oben; die Gerüst-Säule ist danach dein Weg zwischen Warteplatz und "
        "Plattform.",
    help=[["Endermilbe ist tot", "Die 3 × 3 Blöcke unter dem Dach müssen alle stehen (nur der Ring darum ist Loch), "
                                 "und das Dach (untere Stufen) liegt genau 2 Blöcke darüber – dann ist neben der "
                                 "Endermilbe nirgends Platz für einen Enderman. Ohne Namensschild verschwindet sie "
                                 "nach 2 Minuten."],
          ["Wenig Endermen", "Mindestens 128 Blöcke von anderen Inseln bauen und kein Licht (Fackeln) in die Nähe. "
                             "Unten möglichst tief anfangen: Beim Spawnen wählt das Spiel eine zufällige Höhe "
                             "zwischen 0 und dem obersten Block – je tiefer die Plattform, desto öfter trifft es sie."],
          ["Endermen greifen dich an", "Beim Bauen und Warten nicht in ihre Augen schauen (oder einen geschnitzten "
                                       "Kürbis aufsetzen)."],
          ["Truhe voll", "Die Doppeltruhe fasst 864 Perlen (grob 1½–2 Stunden). Danach bleiben die Perlen in den "
                         "Trichtern – rechtzeitig leeren."]],
    meta=m("Rate: Schätzung – die Plattform hat etwa 5-mal so viele Spawnfelder wie die einfache Farm (335 statt 65); "
           "die einfache brachte im Test 38–47 Perlen in 20 Minuten. Grob 400–700 Enderperlen pro Stunde, alle in "
           "der Truhe (Enderman: 0–1 Perle).",
           [("Im End, mindestens 128 Blöcke von anderen Spawnflächen – dann spawnen Endermen nur auf der Plattform.",
             W + "Tutorial:Enderman_farming")],
           [("Endermilben-Köder: benannte Endermilbe in einem Fahrzeug, Endermen in Sichtweite laufen zu ihr und "
             "fallen; 43 Blöcke Fall.", W + "Tutorial:Enderman_farming"),
            ("Endermen sehen eine Endermilbe bis 64 Blöcke weit und greifen sie an.", W + "Enderman"),
            ("Ohne Namensschild verschwindet eine Endermilbe nach 120 Sekunden – auch in Boot oder Lore.",
             W + "Endermite"),
            ("Fallschaden: 1 je Block ab dem vierten – 44 Blöcke sind 41 Schaden.", W + "Fall_damage"),
            ("Trichter sammeln Gegenstände aus dem Raum über sich ein.", W + "Hopper"),
            ("Auf Gerüst spawnen keine Mobs; darin klettert man hoch (Springen) und runter (Schleichen).",
             W + "Scaffolding"),
            ("Auf dem Testserver (26.3) geprüft: Endermen teleportieren sich und landen dabei auch auf Falltüren, ein "
             "Boot nimmt einen zweiten Fahrgast auf – darum das Dach. Mit offenem Loch bis an den Mittelblock trieb ein "
             "fallender Enderman unter das Dach – darum ist der Bereich unter dem Dach massiv.", None)])))

f.zeichen(N="end_stone", s=("slab", {"half": "bottom"}), U=("slab", {"half": "bottom"}), K=("chest", "e"),
          X="scaffolding", B="oak_boat", M="endermite",
          a=("oak_trapdoor", {"half": "bottom", "f": "s", "open": True}),
          b=("oak_trapdoor", {"half": "bottom", "f": "n", "open": True}),
          c=("oak_trapdoor", {"half": "bottom", "f": "e", "open": True}),
          d=("oak_trapdoor", {"half": "bottom", "f": "w", "open": True}))

f.schritt("Im End, mindestens 128 Blöcke von jeder anderen Insel (z. B. am Ende einer Brücke aus Blöcken, auf denen "
          "nichts spawnt). Du stehst am späteren Warteplatz – so tief wie möglich, aber über Höhe 0. Eine Ebene unter "
          "deinen Füßen: westlich ein Boden 7 × 7 aus Endstein, dazwischen 3 Blöcke Endstein und unter deinem Platz "
          "eine untere Stufe (darauf spawnen keine Endermen; erst setzen, wenn du schon auf dem Endstein stehst).", {
    -1: """
        NNNNNNN..
        NNNNNNN..
        NNNNNNN..
        NNNNNNNNs
        NNNNNNNNN
        NNNNNNN..
        NNNNNNN..
    """}, x0=-8, z0=-3)
f.schritt("Doppeltruhe direkt westlich neben deinem Platz: zwei Truhen nebeneinander, beim Setzen nach Westen schauen – "
          "dann zeigt ihre Vorderseite zu dir.", {
    0: "K\nK"}, x0=-1)
f.schritt("Westlich davon der Trichterboden 5 × 5 – hier landen später die Endermen – und ein Trichter zur Truhe. Ein "
          "Trichter zeigt in den Block, an den du klickst; immer schleichend klicken, sonst öffnet sich Truhe oder "
          "Trichter. Du stehst dabei auf dem Boden hinter dem neuen Trichter und rückst nach jedem einen Block zurück. "
          "Erst den Trichter an die Westseite der Truhe, dann den nächsten an dessen Westseite. In der östlichen Spalte "
          "des Bodens zeigen die zwei nördlichen Trichter nach Süden (an die Nordseite des mittleren klicken), die "
          "zwei südlichen nach Norden. Alle anderen zeigen nach Osten: Reihe für Reihe von Osten nach Westen, jeweils "
          "an die Westseite des Nachbarn klicken.", {
    0: """
        >>>>v
        >>>>v
        >>>>>>
        >>>>^
        >>>>^
    """}, x0=-7, z0=-2)
f.schritt("Rand um den Trichterboden: ein Ring aus Endstein auf Höhe der Trichter (der Trichter zur Truhe ist ein Teil "
          "davon) und darauf ein Ring aus Glas (auf den Trichter schleichend klicken). Er hält Perlen fest, die beim "
          "Tod eines Enderman etwas wegspringen; auf Glas spawnt nichts.", {
    0: """
        NNNNNNN
        N.....N
        N.....N
        N......
        N.....N
        N.....N
        NNNNNNN
    """,
    1: """
        GGGGGGG
        G.....G
        G.....G
        G.....G
        G.....G
        G.....G
        GGGGGGG
    """}, x0=-8, z0=-3)
f.schritt("Südlich neben deinem Platz eine Gerüst-Säule, 45 hoch: Gerüst an Gerüst klicken setzt es oben auf die "
          "Säule. Darin kletterst du hinauf (Springen) und hinunter (Schleichen).", {
    y: "X" for y in range(0, 45)}, z0=1)
f.schritt("Oben auf der Säule die Plattform 19 × 19 aus Endstein, auf gleicher Höhe wie das oberste Gerüst (die "
          "Säule ist ein Feld davon): vom Gerüst aus nach allen Seiten bauen. Über dem Trichterboden alles zubauen – "
          "der Ring kommt später. Der Block genau über der Mitte des Trichterbodens wird der Mittelblock.", {
    44: "\n".join(["N" * 19] * 10 + ["N" * 14 + "." + "N" * 4] + ["N" * 19] * 8)}, x0=-14, z0=-9)
f.schritt("Dach über dem Mittelblock und seinen 8 Nachbarn: Auf dem Mittelblock zwei Hilfsblöcke hochbauen (springen "
          "und unter dich setzen), als dritte Lage eine untere Stufe unter dich setzen. Auf ihr stehend an den Kanten "
          "schleichen und 8 weitere untere Stufen an die untere Hälfte ihrer Seiten klicken – Dach 3 × 3, zwei Blöcke "
          "über der Plattform. Hinunterspringen und die zwei Hilfsblöcke abbauen. Unter dem Dach sind nur 2 Blöcke "
          "Platz: Kein Enderman passt hinein, auch nicht beim Teleportieren. Auf unteren Stufen spawnen keine "
          "Endermen; sehen können sie die Endermilbe trotzdem.", {
    47: "UUU\nUUU\nUUU"}, x0=-6, z0=-1)
f.schritt("Auf den Mittelblock (unter das Dach) ein Boot. Eine Endermilbe hineinlocken – sie entsteht manchmal beim "
          "Werfen einer Enderperle und läuft dir nach – und ihr ein Namensschild geben, sonst verschwindet sie nach 2 "
          "Minuten. Vorher alle Endermen auf der Plattform erledigen – sonst schlagen sie die Endermilbe, solange der "
          "Ring noch fehlt. Neue kommen nicht, solange du in der Mitte bist: Die ganze Plattform ist näher als 24 "
          "Blöcke an dir.", {
    45: "B"}, x0=-5)
f.schritt("Endermilbe im Boot.", {45: "M"}, x0=-5)
f.schritt("Um die 3 × 3 Blöcke unter dem Dach einen Ring ausheben, 1 breit (16 Blöcke) – genau über dem Rand des "
          "Trichterbodens. Die 3 × 3 Blöcke unter dem Dach bleiben unbedingt stehen: Wer in den Ring fällt, kommt "
          "erst unter das Dach, wenn er schon tiefer ist als die Endermilbe – so erreicht sie keiner.", {
    44: "-----\n-...-\n-...-\n-...-\n-----"}, x0=-7, z0=-2)
f.schritt("16 Falltüren an den Außenrand des Rings klicken (Klappe außen, an der Plattform) – schräg von der Seite an "
          "die Innenwand klicken. Dann alle öffnen. Endermen halten die Falltüren für Boden, wollen zur Endermilbe und "
          "fallen. Hinüber steigen können sie nicht: Hinter dem Ring ist unter dem Dach kein Platz für sie.", {
    44: "aaaaa\nc...d\nc...d\nc...d\nbbbbb"}, x0=-7, z0=-2)
f.schritt("Im Gerüst hinunter (schleichen) und hier warten: 45 Blöcke unter der Plattform – näher als 24 Blöcke "
          "spawnt nichts, und bis 128 Blöcke bleiben die Endermen da. Die Perlen landen in der Truhe neben dir.", {
    0: "P"})

# Wie die einfache Farm im leeren Ring um die Hauptinsel, aber auf der anderen Seite (die einfache testet bei 400/400 –
# laufen beide Tests zugleich, dürfen sie sich nicht überbauen). hoehe 15: Plattform auf Höhe 59 wie bei der einfachen.
f.pruefe(dimension="the_end", zeit="day", hoehe=15, ursprung=[-400, 400],
         nachher=["kill @e[type=minecraft:endermite,x={x-5},y={y+45},z={z},distance=..8]",
                  "kill @e[type=minecraft:oak_boat,x={x-5},y={y+45},z={z},distance=..8]",
                  'execute positioned {x-5} {y+45} {z} run summon minecraft:oak_boat ~0.5 ~ ~0.5 '   # auch bei x < 0
                  '{Passengers:[{id:"minecraft:endermite",PersistenceRequired:1b}]}'],
         bereich=[-6, 45, -1, -4, 47, 1],
         erwartet={"beute": {"minecraft:ender_pearl": 100}, "wesen": {"minecraft:endermite": 1}})
