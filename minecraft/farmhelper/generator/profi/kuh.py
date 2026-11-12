"""Kuh-Farm mit Lava-Grube (Profi): Zuchtgehege wie die einfache Farm, in der Mitte ein Loch mit offener Falltür –
Kälber fallen hindurch, erwachsene Kühe nicht. Darunter eine Grube 2 × 2, in der die Kälber groß werden; auf Knopfdruck
setzt ein Werfer Lava in die Schicht über ihren Köpfen, die nur erwachsene Kühe erreichen.

Höhen: Gehegeboden y -1 (Erdboden), Lavaschicht y -2, Grube (Kühe) y -3 mit Schildern, Schlamm y -4, Trichter y -5.
Grube x 0 … 1, z 0 … 1; Loch mit Falltür über (0, 0). Kanal (2, -2, 0) mit Werfer (3, -2, 0) nach Westen, Knopf in einem
Loch (4, -1, 0) an der Ostseite des Blocks über dem Werfer. Truhe (3, -5, 1), Leiterschacht x 4, z 1.
"""
from profi_basis import *

# Knopf an einer Wand: Richtung = wohin er zeigt (weg von dem Block, an dem er hängt)
GERICHTET_NEU = {"wandknopf": ("stone_button", "#minecraft:buttons", "#minecraft:buttons", "Knopf")}

f = profi("kuh", dict(
    name="Kuh-Farm mit Lava-Grube (Profi)", diff=3, out="Gebratenes Rindfleisch (Steak), Leder",
    where="Überall auf festem Boden: 5 Blöcke tief graben, keine Höhle und kein Kies darunter",
    afk="Nein – du fütterst die Kühe (in Java vermehren sich Kühe nicht von selbst)",
    why="Du fütterst nur noch, den Rest macht die Farm – und die Zuchtkühe sind nie in Gefahr. Sie stehen im Gehege, "
        "in dessen Mitte ein Loch mit einer offenen Falltür ist. Die senkrechte Klappe lässt einen Spalt von 13/16 "
        "Block: Kälber (0,45 breit) fallen hindurch, erwachsene Kühe (0,9 breit) nicht. Mobs halten die offene "
        "Falltür für Boden, die Kälber laufen also von selbst darauf. Unten in der Grube (2 × 2) wachsen die Kälber "
        "20 Minuten heran. Über der Grube liegt eine leere Schicht. Drückst du den Knopf, setzt ein Werfer mit "
        "Lavaeimer dort Lava hinein; die Schilder auf dem Grubenboden halten sie oben. Erwachsene Kühe (1,4 hoch) "
        "stecken mit dem Kopf in der Lava und verbrennen – Steak und Leder fallen auf den Schlamm, die Trichter "
        "darunter bringen alles in die Truhe. Kälber (0,7 hoch) bleiben 0,4 Block unter der Lava heil. Noch einmal "
        "drücken: Der Werfer holt die Lava zurück. In der einfachen Farm musst du jede Kuh selbst schlachten und "
        "dabei die Zuchtkühe verschonen; Steak gibt es dort nur mit einem Schwert mit Verbrennung.",
    help=[["Kälber fallen nicht durch", "Die Falltür muss offen sein (sie steht dann senkrecht an der Westseite des "
                                        "Lochs) und das Loch darunter frei. Erwachsene Kühe passen nicht durch den "
                                        "Spalt – das ist Absicht."],
          ["Lava läuft in die Grube", "Auf jedem der 4 Schlammblöcke muss ein Schild stehen: Lava fließt nicht in "
                                      "Schilder, Kühe laufen aber durch sie hindurch."],
          ["Nichts verbrennt", "Lavaeimer in den Werfer (beim Bauen). Knopf einmal drücken, etwa 20 Sekunden warten, "
                               "noch einmal drücken – dann ist die Lava wieder im Eimer. Währenddessen nicht füttern: "
                               "ein fallendes Kalb fiele durch die Lava."],
          ["Grube zu voll", "Spätestens alle 20 Minuten den Knopf drücken. Mehr als etwa 20 Kühe in der Grube "
                            "drücken sich gegenseitig tot – dann gibt es nur rohes Fleisch."]],
    meta=m("Rate: so viel du züchtest – mit 8 Zuchtkühen und Füttern alle 5 Minuten etwa 48 Kühe pro Stunde, also "
           "rund 100 Steaks und 50 Leder (Schätzung: eine Kuh gibt 1–3 Fleisch und 0–2 Leder, ein Kalb braucht 20 "
           "Minuten). Die einfache Farm liefert dieselbe Menge nur mit Schlachten von Hand.",
           [("Überall; die Grube liegt unter dem Gehege, Wände und Decke sind der natürliche Boden.",
             W + "Tutorial:Animal_farming#Automated_animal_farming")],
           [("Lava über den Köpfen, von Schildern gehalten: erwachsene Tiere verbrennen, das Fleisch fällt gebraten "
             "herunter (Steakatron, Lava-Klinge).", W + "Tutorial:Animal_farming#Steakatron_2000"),
            ("Kuh: erwachsen 0,9 breit und 1,4 hoch, Kalb 0,45 breit und 0,7 hoch; Kälber brauchen 20 Minuten, "
             "Zuchtkühe 5 Minuten Pause.", W + "Cow"),
            ("Mobs halten offene Falltüren für geschlossen und laufen darauf – so fallen sie hindurch.",
             W + "Trapdoor#Barrier"),
            ("Schilder werden von Lava nicht zerstört und halten sie auf.", W + "Sign#Usage"),
            ("Ein Werfer mit Lavaeimer setzt Lava vor sich, mit dem leeren Eimer holt er sie beim nächsten Signal "
             "zurück.", W + "Dispenser#Behavior"),
            ("Auf dem Testserver (26.3) geprüft (andere Farmen): Mobs halten offene Falltüren für Boden; Trichter "
             "saugen durch Schlamm.", None)])))

f.zeichen(M="mud", S="sign", D=("dispenser", "w"), k=("wandknopf", "e"), L=("ladder", "w"),
          F=("oak_trapdoor", {"f": "e", "open": True}), Z="oak_fence", T="fence_gate", X="cow",
          s=("hopper", "s"))

f.schritt("Ausheben: die Grube 2 × 2 Blöcke und 5 tief (die oberste Schicht ist der Boden des späteren Geheges). "
          "Östlich davon auf dem Grund 2 Löcher für Trichter und Truhe, über dem Truhenloch eins für Glas, daneben einen "
          "Schacht 5 tief zum Einsteigen und nördlich neben dem Schacht oben ein Loch 1 tief für den Knopf.", {
    -1: "--..-\n--..-",
    -2: "--\n--..-",
    -3: "--\n--..-",
    -4: "--\n--.--",
    -5: "--\n-----"})
f.schritt("Unten: erst die Truhe ganz im Osten, dann die Trichter – alle führen zur Truhe: schleichend an die Truhe bzw. "
          "an den nächsten Trichter klicken (ein Trichter zeigt in den Block, an den du klickst). Den Trichter unter "
          "deinen Füßen setzt du zuletzt, auf einem anderen Trichter stehend.", {
    -5: """
        >s
        >>>C
    """})
f.schritt("Schlamm auf die 4 Trichter der Grube (Wasserflasche auf Erde) – Trichter saugen durch Schlamm, nicht durch "
          "Erde. Glas auf die Truhe, sonst geht sie nicht auf.", {
    -4: """
        MM
        MM.G
    """})
f.schritt("Auf jeden Schlammblock ein Schild stellen. Die Schilder halten später die Lava eine Schicht höher; die "
          "Kühe laufen durch sie hindurch.", {
    -3: "SS\nSS"})
f.schritt("Kanal: Von der Grube aus nach Osten in der Schicht direkt unter dem Erdboden (Höhe -2) zwei Blöcke "
          "ausgraben. Der Block unter dem Kanal und der Erdboden darüber bleiben stehen.", {
    -2: "..--"})
f.schritt("In das hintere Kanalloch einen Werfer, der nach Westen in den Kanal zeigt (ein Werfer zeigt beim Setzen zu "
          "dir: aus der Grube heraus nach Osten schauen). Einen Lavaeimer hineinlegen. Dann mit ein paar Hilfsblöcken "
          "aus der Grube steigen und sie wieder abbauen.", {
    -2: "...D"})
f.schritt("Grube oben wieder zumachen (Steinziegel, Stein oder Erde) bis auf das Loch im Nordwesten – darunter bleibt "
          "die Lavaschicht leer. Ins Loch eine Falltür: an die Ostseite des Blocks westlich vom Loch klicken und "
          "aufklappen; sie steht dann senkrecht an der Westwand des Lochs.", {
    -1: "F#\n##"})
f.schritt("Leitern an die Ostwand des Schachts, von unten bis eine Stufe unter den Rand. Im Knopfloch nördlich daneben "
          "einen Knopf an die Westwand – das ist der Block direkt über dem Werfer: Drückst du ihn, wirft der Werfer.", {
    -1: "k\n.",
    -2: ".\nL",
    -3: ".\nL",
    -4: ".\nL",
    -5: ".\nL"}, x0=4)
f.schritt("Gehege 3 × 3 aus Zaun rund um das Loch, im Süden ein Zauntor.", {
    0: """
        ZZZZZ
        Z...Z
        Z...Z
        Z...Z
        ZZTZZ
    """}, x0=-2, z0=-2)
f.schritt("Zuchtkühe hinein (mit Weizen locken), 2 bis 8 Stück. Füttere je zwei mit Weizen: Das Kalb läuft bald über "
          "die Falltür und fällt in die Grube, die Großen bleiben oben. Nach 5 Minuten wieder füttern.", {
    0: """
        X.X
        ...
        X.X
    """}, x0=-1, z0=-1)
f.schritt("Dein Platz am Gehege, nahe beim Knopf. Ernten: Knopf drücken – Lava kommt, die großen Kühe in der Grube "
          "verbrennen. Nach etwa 20 Sekunden noch einmal drücken – die Lava ist wieder im Eimer. Steak und Leder holst "
          "du über die Leiter aus der Truhe.", {0: "P"}, x0=3, z0=-1)

# Haupttest: Lava liegt (wie nach dem ersten Knopfdruck); 3 Jungkühe werden in der Grube gleich groß und verbrennen,
# ein ganz junges Kalb bleibt unter der Lava heil. Die Zuchtkühe oben werden verliebt gemacht.
GRUBE = [0, -3, 0, 1, -3, 1]
f.pruefe(boden=GRAS,
         nachher=["execute as @e[type=minecraft:cow,x={x},y={y},z={z},distance=..4] run data merge entity @s "
                  "{InLove:600}"] +
         mobs("cow", [(1, -3, 0), (0, -3, 1), (1, -3, 1)], "PersistenceRequired:1b,Age:-200") +
         mobs("cow", [(0, -3, 0)], "PersistenceRequired:1b,Age:-40000") +
         ["setblock {x+2} {y-2} {z} minecraft:lava"],
         bereich=GRUBE, erwartet={"items": {"minecraft:cooked_beef": 3}, "wesen": {"minecraft:cow": 1}})
# Trennung: ohne Lava – die Kälber der verliebten Zuchtkühe müssen durch die Falltür in die Grube fallen
f.pruefe_auch("kuh_profi_mech", boden=GRAS,
              nachher=["execute as @e[type=minecraft:cow,x={x},y={y},z={z},distance=..4] run data merge entity @s "
                       "{InLove:600}"],
              bereich=GRUBE, erwartet={"wesen": {"minecraft:cow": 1}})
