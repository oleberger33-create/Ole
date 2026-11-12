"""Hühner-Farm (Profi): Hühnerschacht aus 3 Trichtern (bis zu 30 Hühner) über einen Werfer-Takt in den Lavakessel-Kocher
wie in der einfachen Farm; Kocher rundum in Glas, Hebel am Werfer zum Eiersammeln.

Reihe auf z 0 (West → Ost): Hühnertrichter x -2 … 0 (Höhe 1, alle nach Osten), Werfer x 1 (nach Osten), Steinschneider
x 2 auf dem unteren Trichter (2, 0, 0) → Truhe (3, 0, 0). Kessel mit Lava (2, 2, 0) über dem Steinschneider. Takt: zwei
Beobachter nördlich vom Werfer (1, 1, -1) und (1, 1, -2). Hebel (1, 1, 1) an der Südseite des Werfers.
"""
from profi_basis import *

# Hebel an einer Wand: Richtung = wohin er zeigt (weg von dem Block, an dem er hängt)
GERICHTET_NEU = {"wandhebel": ("lever", "minecraft:lever", "minecraft:lever", "Hebel")}

f = profi("huehner", dict(
    name="Hühner-Farm (Profi)", diff=2, out="Gebratenes Hühnchen, Federn (auf Wunsch Eier)", where="Überall",
    afk="In der Nähe bleiben (Simulationsdistanz)",
    why="Gleiches Prinzip wie die einfache Farm, aber für viele Hühner: Drei Trichter in einer Reihe bieten Platz für "
        "bis zu 30 Hühner statt einer Handvoll – und die Menge an Hühnchen wächst mit der Zahl der Hühner. Ihre Eier "
        "fallen in die Trichter und laufen in den Werfer; zwei Beobachter, die sich anschauen, geben einen dauernden "
        "Takt, und der Werfer wirft jedes Ei auf den Steinschneider. Etwa jedes 8. Ei schlüpft. Küken sind klein und "
        "passen unter den Lavakessel; ein erwachsenes Huhn ist größer, berührt mit dem Kopf den Kessel und wird "
        "gegart – Hühnchen und Federn fallen durch den Steinschneider in den Trichter zur Truhe. Neu gegenüber der "
        "einfachen Farm: Der Kessel ist auch auf seiner Höhe rundum in Glas (seit 26.1 entwischen Küken sonst durch "
        "den Spalt unter dem Kessel), und ein Hebel am Werfer schaltet auf „Eier sammeln“: Ein dauernd eingeschalteter Werfer "
        "wirft nicht – er feuert nur, wenn sein Signal neu angeht. Die Eier bleiben dann im Werfer, und du füllst damit "
        "den Hühnerschacht schnell auf.",
    help=[["Kein gebratenes Hühnchen", "Der Hebel muss AUS sein, sonst wirft der Werfer keine Eier. Kessel genau über "
                                       "dem Steinschneider und mit Lava gefüllt."],
          ["Küken laufen weg", "Rund um den Steinschneider und rund um den Kessel (auch auf seiner Höhe) muss überall "
                               "Glas sein – seit 26.1 passen Küken sonst durch den Spalt unter dem Kessel."],
          ["Wie kommen 30 Hühner hinein?", "Hebel AN: Die Eier sammeln sich im Werfer (Rechtsklick auf seine "
                                           "Südseite neben dem Hebel). Wirf sie von oben in den offenen Hühnerschacht – "
                                           "etwa jedes 8. schlüpft – oder füttere zwei Hühner darin mit Samen. Danach "
                                           "Hebel wieder AUS. Mehr als 30 Hühner drängeln sich zu sehr."],
          ["Beobachter zeigt falsch", "Ein Beobachter schaut in die Richtung, in die du beim Setzen schaust (das "
                                      "Gesicht zeigt von dir weg). Notfalls einen Hilfsblock setzen und wieder "
                                      "abbauen."]],
    meta=m("Rate: mit 30 Hühnern etwa 30 gebratene Hühnchen und 30 Federn pro Stunde (Schätzung nach dem Wiki: ein "
           "Huhn legt alle 5–10 Minuten ein Ei, also etwa 8 pro Stunde; jedes 8. Ei schlüpft; das Küken ist nach "
           "20 Minuten groß). Die einfache Farm mit 4 Hühnern kommt so auf etwa 4 pro Stunde.",
           [("Überall. Der Kocher mit Steinschneider und Lavakessel funktioniert nur in der Java Edition.",
             W + "Tutorial:Egg_farming#Chicken_farming_and_cooking")],
           [("Steinschneider unter einem Kessel mit Lava: Küken passen darunter, erwachsene Hühner berühren den Kessel "
             "mit dem Kopf und werden gegart; seit 26.1 muss der Kessel rundum eingefasst sein.",
             W + "Tutorial:Egg_farming#Chicken_farming_and_cooking"),
            ("Ein Huhn legt alle 5–10 Minuten ein Ei; ein geworfenes Ei schlüpft mit 1/8, dazu selten 3 weitere "
             "Küken.", W + "Chicken#Eggs"),
            ("Ein Werfer feuert nur beim Einschalten (steigende Flanke), nicht solange er an ist – darum hält ihn "
             "der Hebel an.", W + "Dispenser#Behavior"),
            ("Kocher aus Trichter, Werfer-Takt, Steinschneider und Lavakessel: in der einfachen Farm auf dem "
             "Testserver (26.3) geprüft.", None)])))

f.zeichen(D=("dispenser", "e"), T="stonecutter", O=("observer", "n"), Q=("observer", "s"), K="lava_cauldron",
          h=("wandhebel", "s"), X="chicken")

f.schritt("Unten auf dem Boden: 4 Stützblöcke in einer Reihe von West nach Ost und einen weiteren nördlich neben "
          "die östlichste Stütze. Östlich der Reihe ein Trichter nach Osten in eine Truhe (erst die Truhe, dann den "
          "Trichter schleichend an die Truhe klicken).", {
    0: """
        ...#..
        ####>C
    """}, x0=-2, z0=-1)
f.schritt("Takt: zwei Beobachter, die sich anschauen. Den ersten auf die nördliche Stütze: südlich neben der "
          "östlichsten Stütze auf dem Boden stehen, auf die Oberseite der nördlichen Stütze klicken und dabei nach "
          "Norden schauen – er schaut dann nach Norden, sein Rücken zeigt nach Süden (dorthin kommt der Werfer). Den "
          "zweiten an seine Nordseite: von Norden her klicken und dabei nach Süden schauen.", {
    1: "Q\nO"}, x0=1, z0=-2)
f.schritt("Auf die östlichste Stütze einen Werfer, der nach Osten zeigt (ein Werfer zeigt beim Setzen zu dir: von "
          "Südosten her flach nach Westen schauen). Auf die 3 anderen Stützen die Hühnertrichter, alle nach Osten: "
          "schleichend den ersten an den Werfer klicken, jeden weiteren an den vorigen Trichter. Auf den unteren "
          "Trichter schleichend einen Steinschneider.", {
    1: ">>>DT"}, x0=-2)
f.schritt("Steinziegel rund um die Hühnertrichter (Nordseite, Südseite, Westende) und Glas um den Steinschneider "
          "(Norden, Süden und über der Truhe). An die Südseite des Werfers einen Hebel – er bleibt AUS.", {
    1: """
        .###.G.
        #.....G
        .###hG.
    """}, x0=-3, z0=-1)
f.schritt("Kessel auf den Steinschneider und mit dem Lavaeimer füllen. Glaswände 2 hoch rund um die Hühnertrichter "
          "(auch über dem Werfer), oben bleibt der Schacht offen. Den Kessel auf seiner Höhe rundum mit Glas "
          "einfassen – seit 26.1 entwischen Küken sonst durch den Spalt unter dem Kessel.", {
    2: """
        .GGG.G.
        G...GKG
        .GGG.G.
    """,
    3: """
        .GGG
        G...G
        .GGG
    """}, x0=-3, z0=-1)
f.schritt("Hühner in den Schacht, bis zu 30 Stück (je Trichter etwa 10): Eier von oben hineinwerfen (etwa jedes 8. "
          "schlüpft) oder Hühner mit der Leine hineinheben; zwei Hühner darin kannst du mit Samen füttern. Zum "
          "schnellen Auffüllen den Hebel AN: Dann sammeln sich die Eier der Hühner im Werfer, du nimmst sie heraus "
          "und wirfst sie in den Schacht. Danach Hebel AUS – jetzt wirft der Werfer jedes Ei auf den Steinschneider, "
          "erwachsene Hühner werden gegart, alles landet in der Truhe.", {
    2: "XXX"}, x0=-2)
f.schritt("Dein Platz östlich der Truhe – die Hühner legen nur, wenn du in der Nähe bist.", {0: "P"}, x0=4)

f.pruefe(nachher=mobs("chicken", [(-2, 2, 0), (-1, 2, 0), (0, 2, 0)] * 8, "PersistenceRequired:1b,EggLayTime:200") +
         ["summon minecraft:chicken {x+2}.5 {y+1}.6 {z}.5 {PersistenceRequired:1b}"],
         erwartet={"items": {"minecraft:cooked_chicken": 3}, "wesen": {"minecraft:chicken": 24}})
