"""XP-Farm am Spawner (Profi): Raum eine Ebene höher als bei der einfachen Farm (alle 3 Spawn-Ebenen nutzbar), ein Block
auf dem Spawner, Wasser schiebt alles in eine Rinne mit Loch in der Mitte; die Mobs fallen 11 Blöcke in eine Zelle
außerhalb des Prüfbereichs (9 × 9 × 9) des Spawners und kommen mit 12 von 20 Leben an. Du triffst sie durch einen Spalt,
die Beute läuft über einen Trichter in die Truhe.

Spawner (0, 0, 0). Raum x -4 … 4, z -4 … 4, Höhe -2 … 2 (Wasser auf -2). Rinne Höhe -3, z 4, x -8 … 8 (Quellen an den
Enden, Loch bei x 0). Schacht (0, -4 … -12, 4), Zelle (0, -14 … -13, 4), Trichter (0, -15, 4) nach unten in die Truhe
(0, -16, 4). Spalt (0, -14, 3) mit geschlossener Falltür unten, darunter eine Mulde (0, -15 … -16, 3) als Blick auf die
Truhe. Dein Platz (0, -15, 2): 15,6 Blöcke vom Spawner.
"""
from profi_basis import *

f = profi("xpspawner", dict(
    name="XP-Farm am Spawner (Profi)", diff=3, out="XP, Knochen, Pfeile, Fleisch (Beute in die Truhe)",
    where="Zombie- oder Skelett-Spawner im Verlies; unter dem Spawner 17 Ebenen Stein zum Graben",
    afk="Halb – an deinem Platz warten (genau dort, sonst ist der Spawner aus) und alle paar Minuten zuschlagen",
    why="Drei Verbesserungen gegenüber der einfachen Farm. 1. Mehr Mobs: Ein Spawner setzt Mobs eine Ebene unter, "
        "auf und über seine Höhe. Bei der einfachen Farm passt in die oberste Ebene kein 2 Blöcke hoher Mob – hier "
        "ist der Raum eine Ebene höher (5 statt 4), und ein Block auf dem Spawner sorgt dafür, dass niemand oben auf "
        "ihm liegen bleibt. Das gibt rechnerisch etwa 45 % mehr Mobs. Gespawnt wird wie gehabt nur in der Luft; das "
        "Wasser liegt zwei Ebenen unter dem Spawner. 2. Kein Stau: Das Wasser schiebt alle Mobs in die Rinne, und "
        "deren Wasser endet von beiden Seiten genau an einem Loch in der Mitte. Die Mobs fallen 11 Blöcke tief in "
        "eine Zelle – heraus aus dem Bereich um den Spawner (9 × 9 × 9), in dem er ab 6 Mobs aussetzt. Er spawnt "
        "also weiter, auch wenn sich unten viele sammeln. 3. Halb tot: Der Fall nimmt jedem Mob 8 Leben, es bleiben "
        "12 von 20 – ein Schlag weniger pro Mob, und mit Schwungkraft triffst du alle in der Zelle zugleich. Du "
        "stehst eine Ebene tiefer und triffst sie durch einen Spalt; sie sehen dich nicht. Eine geschlossene Falltür "
        "unten im Spalt hält Babyzombies drinnen, XP-Kugeln fliegen darüber zu dir. Die Beute fällt durch den "
        "Trichter in die Truhe.",
    help=[["Spawner spawnt nicht", "Genau auf deinem Platz stehen: 15 Ebenen unter dem Spawner, 2 Blöcke nördlich "
                                   "der Zelle – das sind 15,6 Blöcke, höchstens 16 gehen. Schon eine Ebene tiefer "
                                   "ist er aus. Keine Fackeln im Raum."],
          ["Wasser läuft in den Schacht", "Die beiden Quellen der Rinne gehören genau 8 Blöcke links und rechts vom "
                                          "Loch in den Stein. Dann endet das Wasser von beiden Seiten direkt am Loch "
                                          "und läuft nicht hinein – schiebt die Mobs aber hinein."],
          ["Mobs liegen oben auf dem Spawner", "Block auf den Spawner setzen. Wer dort liegen bleibt, zählt zu den 6 "
                                               "Mobs, ab denen der Spawner aussetzt."],
          ["Mobs sterben ohne XP", "Ab 24 Mobs auf einem Fleck erdrücken sie sich gegenseitig – dann gibt es nur die "
                                   "Beute (sie landet trotzdem in der Truhe). Alle paar Minuten zuschlagen."]],
    meta=m("Rate (Schätzung): rund 500 Mobs pro Stunde, also etwa 2500 XP (Stufe 30 in gut einer halben Stunde), "
           "gegen etwa 350 bei der einfachen Farm. Gerechnet: alle 10–40 s (im Mittel 25 s) 4 Versuche; hier "
           "gelingen fast 9 von 10, bei der einfachen gut die Hälfte (die oberste Ebene ist dort zu niedrig). Ein "
           "Zombie gibt 5 XP.",
           [("An einem Zombie- oder Skelett-Spawner im Verlies (Monsterraum).", W + "Tutorial:Monster_spawner_traps")],
           [("Spawner: Mobs in 9 × 3 × 9 um ihn (eine Ebene unter bis eine über ihm), auch in der Luft; 2 hohe Mobs "
             "in der obersten Ebene brauchen die Ebene darüber frei. 4 Versuche, dann 10–40 s Pause; ab 6 Mobs im "
             "Bereich 9 × 9 × 9 setzt er aus; ein Spieler muss höchstens 16 Blöcke entfernt sein.",
             W + "Monster_Spawner"),
            ("XP nur, wenn ein Spieler tötet; XP-Farmen machen die Mobs vorher per Fallhöhe schwach.",
             W + "Tutorial:Mob_farm"),
            ("Fallschaden = Fallhöhe − 3 (abgerundet): 11,3 Blöcke Fall auf den Trichter geben 8 Schaden.",
             W + "Damage#Fall_damage"),
            ("Ab mehr als 24 Mobs auf einem Fleck gibt es Gedränge-Schaden.", W + "Damage#Entity_cramming"),
            ("Babyzombies sind 0,98 Blöcke hoch – unter einer geschlossenen Falltür bleiben nur 0,81 frei. Ein "
             "Zombie gibt 5 XP.", W + "Zombie"),
            ("Auf dem Testserver (26.3) geprüft (einfache Farm): Im Wasser spawnt nichts; das Wasser zwei Ebenen "
             "unter dem Spawner schiebt die Mobs in die eine Ebene tiefere Rinne.", None)])))

f.zeichen(Q="spawner", T=("oak_trapdoor", {"half": "bottom"}))

frei = ["-" * 9] * 9
f.schritt("Den Raum um den Spawner freilegen: 9 × 9, von zwei Ebenen UNTER dem Spawner bis zwei Ebenen ÜBER ihm "
          "(5 hoch – eine Ebene höher als bei der einfachen Farm). Boden, Wände und Decke bleiben Stein (unter der "
          "Erde sind sie schon da). Fackeln nur zum Bauen – am Ende alle weg.", {
    -2: "\n".join(frei), -1: "\n".join(frei),
    0: "\n".join(frei[:4] + ["----.----"] + frei[5:]),
    1: "\n".join(frei), 2: "\n".join(frei)}, x0=-4, z0=-4)
f.schritt("Einen Block oben auf den Spawner setzen (auf seine Oberseite klicken). Sonst bleiben Mobs, die in der "
          "obersten Ebene genau über ihm erscheinen, auf ihm liegen.", {1: "#"})
f.schritt("Vorne (Süden) eine Rinne eine Ebene tiefer als der Raum, 17 lang: über die ganze Raumbreite und auf "
          "beiden Seiten 4 Blöcke weiter in den Stein hinein (dort kommen später die Quellen hin).", {
    -3: "-" * 17}, x0=-8, z0=4)
f.schritt("Rand der Wasserebenen: rundherum Stein, damit das Wasser bleibt (unter der Erde meist schon da). Auch der "
          "Boden unter der Rinne muss dicht sein.", {
    -2: "\n".join(["#" * 11] + ["#.........#"] * 9 + ["#" * 11])}, x0=-5, z0=-5)
f.schritt("Rand der Rinne: hinten (Süden) auf ganzer Länge, an den Enden und neben den Teilen im Stein.", {
    -3: "#####.........#####\n#.................#\n###################"}, x0=-9, z0=3)
f.schritt("Schacht: genau in der Mitte der Rinne (vor dem Spawner) senkrecht 11 Blöcke tief graben – immer den Block "
          "unter dir. Unten stehst du in der Zelle.", {
    y: "-" for y in range(-14, -3)}, x0=0, z0=4)
f.schritt("Unten nach Norden: den Spalt erst 2 hoch durchbrechen (damit du durchkommst), dahinter eine Ebene tiefer "
          "dein Platz. Von dort die Mulde vor dir 2 tief, und aus der Mulde unter der Zelle zwei Blöcke für Trichter "
          "und Truhe. Von deinem Platz eine Treppe zu deinem Zugang graben (Weg frei wählbar, aber nicht durch Raum, "
          "Rinne oder Schacht).", {
    -13: ".\n-", -14: "-\n-", -15: "-\n-\n-", -16: ".\n-\n-"}, x0=0, z0=2)
f.schritt("Aus der Mulde: die Truhe unter die Zelle setzen (unten auf den Boden klicken), dann schleichend einen "
          "Trichter oben auf die Truhe – er zeigt nach unten in die Truhe. Auf dem Trichter landen die Mobs, ihre "
          "Beute fällt hinein.", {-16: "C", -15: "H"}, x0=0, z0=4)
f.schritt("Zurück auf deinen Platz. Den oberen Spaltblock wieder zumachen (von unten an den Stein darüber klicken). "
          "Dann eine Falltür in die UNTERE Hälfte des Spalts: unten an seine Seitenwand klicken und zu lassen. Mobs "
          "kommen nicht heraus (auch Babyzombies nicht, sie sind 0,98 hoch), XP-Kugeln fliegen über die Falltür zu "
          "dir.", {-13: "#", -14: "T"}, x0=0, z0=3)
f.schritt("Wasser: an der Nordwand eine Reihe Quellen (9) – es fließt genau 7 Blöcke bis zur Kante der Rinne und "
          "schiebt alles hinein. Im Wasser spawnt nichts, die Mobs spawnen darüber und fallen hinein.", {
    -2: "\n".join(["WWWWWWWWW"] + ["FFFFFFFFF"] * 7)}, x0=-4, z0=-4)
f.schritt("Je eine Quelle in die beiden Enden der Rinne, 8 Blöcke vom Loch: Das Wasser fließt 7 Blöcke und endet "
          "von beiden Seiten genau am Loch – es läuft nicht in den Schacht, schiebt aber alles hinein.", {
    -3: "WFFFFFFF.FFFFFFFW"}, x0=-8, z0=4)
f.schritt("Hier stehst du – eine Ebene tiefer als die Mobs in der Zelle, 15,6 Blöcke vom Spawner (höchstens 16, "
          "sonst spawnt nichts). Du triffst sie durch den Spalt über der Falltür; nach 11 Blöcken Fall haben sie nur "
          "noch 12 von 20 Leben. Die Truhe öffnest du durch die Lücke unter der Falltür (schräg nach unten schauen).",
          {-15: "P"}, x0=0, z0=2)
f.schritt("Spawner (ist schon da).", {0: "Q"})

# Wie die einfache Farm (gleiche Messgröße: Zombies in der Zelle). Die einfache kam auf 3 – dort staut es sich im
# Prüfbereich des Spawners. Hier fallen die Zombies aus dem Bereich heraus, der Spawner läuft weiter.
f.pruefe(boden="minecraft:stone", fuellung="minecraft:stone", erde_bis=4,
         nachher=['setblock {x} {y} {z} minecraft:spawner{SpawnData:{entity:{id:"minecraft:zombie"}}}'],
         bereich=[0, -15, 4, 0, -13, 4],
         erwartet={"wesen": {"minecraft:zombie": 10}})
