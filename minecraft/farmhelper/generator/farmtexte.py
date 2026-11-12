"""Texte zu jeder Farm (Infos-Fenster im Farmhelper): passend zur einfachen Bauweise aus farmen.py.

je Farm: name, cat, diff (1–5), out, where, afk, why, help [(Problem, Lösung)], meta {rate, ort [(Text, Quelle)],
meta [(Text, Quelle)]}. Quelle None = selbst geprüft (Testserver 26.3 oder Spielcode), sonst die Wiki-Seite.
"""
W = "https://minecraft.wiki/w/"
TEST = "Auf dem Testserver (26.3) nachgebaut und laufen lassen: "


def m(rate, ort, meta):
    return {"rate": rate, "ort": [list(x) for x in ort], "meta": [list(x) for x in meta]}


TEXTE = {
    "zuckerrohr": dict(
        name="Zuckerrohr-Farm", cat="Pflanzen", diff=2, out="Zuckerrohr → Papier, Zucker",
        where="Überall; Wasser direkt neben dem Schlamm", afk="In der Nähe bleiben (Chunk muss laufen)",
        why="Zuckerrohr wächst bis 3 hoch. Ein einziger Beobachter schaut auf den 3. Block eines Rohrs; wird es 3 "
            "hoch, gibt er einen Impuls in die Redstone-Leitung, und alle 8 Kolben schlagen den 2. Block ab. Die "
            "anderen Rohre warten so lange (sie werden nie höher als 3). Das Rohr steht auf Schlamm: Weil Schlamm "
            "etwas niedriger als ein ganzer Block ist, saugt der Trichter darunter die Items an. Was ins Wasser "
            "daneben fällt, schwimmt zum letzten Trichter.",
        help=[("Kolben feuern nie", "Der Beobachter muss mit dem Gesicht zum Rohr zeigen (roter Punkt nach hinten "
                                    "zum Redstone). Der Staub muss direkt hinter dem Beobachter liegen."),
              ("Rohr lässt sich nicht pflanzen", "Erst das Wasser einfüllen und bis zum Ende fließen lassen – ohne "
                                                 "Wasser daneben hält kein Zuckerrohr."),
              ("Items bleiben liegen", "Trichter unter Schlamm (nicht unter Erde!) – durch volle Blöcke saugt ein "
                                       "Trichter nicht.")],
        meta=m("Keine belegte Zahl – hängt von der Zahl der Rohre ab",
               [("Überall, wo Erde/Sand/Schlamm direkt neben Wasser liegt. Kein Biom nötig.",
                 W + "Tutorial:Sugar_cane_farming")],
               [("Wiki-Standard: Grundblock, Kolben, Beobachter übereinander; bei Pflanzung auf Schlamm reichen "
                 "normale Trichter statt Trichterloren.", W + "Tutorial:Sugar_cane_farming"),
                (TEST + "8 Rohre, ein Beobachter, alles landet in der Truhe.", None)])),
    "bambus": dict(
        name="Bambus-Farm", cat="Pflanzen", diff=2, out="Bambus → Stöcke, Gerüste, Brennstoff",
        where="Überall mit Licht ≥ 9 über der Spitze", afk="In der Nähe bleiben",
        why="Gleiche Bauweise wie die Zuckerrohr-Farm, aber mit einem Beobachter pro Stängel: Bambus wächst bis 16 "
            "hoch, und hohe Stängel würden die Items weit verstreuen. So wird jeder Stängel geerntet, sobald er "
            "3 hoch ist. Bambus wird von Kolben zerstört und fällt auf den Schlamm; die Trichter darunter saugen ihn "
            "durch den Schlamm an. Das Wasser daneben braucht der Bambus nicht – es sammelt nur, was zur Seite fällt.",
        help=[("Bambus wächst nicht", "Über der Spitze muss Licht ≥ 9 sein – nicht unter ein Dach bauen."),
              ("Viele Items daneben", "Mauer hinter der Wasserrinne prüfen; jeder Stängel braucht seinen "
                                      "Beobachter.")],
        meta=m("≈ 18 Bambus pro Pflanze und Stunde (aus dem Wachstums-Code berechnet, Spieler in der Nähe)",
               [("Überall, solange über der Spitze Licht ≥ 9 ist – das prüft der Wachstums-Code.", None)],
               [("Wiki-Empfehlung: Bambus auf Schlammblöcken, darunter Trichter.", W + "Tutorial:Bamboo_farming"),
                (TEST + "mit nur einem Beobachter flogen 40 % der Items daneben, mit einem pro Stängel fast nichts.",
                 None)])),
    "kaktus": dict(
        name="Kaktus-Farm", cat="Pflanzen", diff=1, out="Kaktus → grüner Farbstoff, XP im Ofen", where="Überall",
        afk="In der Nähe",
        why="Ein Kaktus bricht ab, wenn neben ihm ein fester Block steht. Die Glasstange hängt auf Höhe des 2. "
            "Kaktusblocks: Wächst er hoch, bricht das neue Stück sofort ab und fällt herunter. Neben den Kakteen "
            "fließt in zwei Rinnen Wasser zu zwei Trichtern und einer Truhe. Kein Redstone nötig.",
        help=[("Kakteen gehen beim Pflanzen kaputt", "Neben einem Kaktus darf auf seiner Höhe nichts Festes "
                                                     "stehen – nur die Glasstange eine Ebene höher."),
              ("Weniger als erwartet", "Ein Teil der Stücke fällt auf den Kaktus und wird zerstört, einige bleiben "
                                       "auf dem Sand zwischen den Kakteen liegen – ab und zu einsammeln.")],
        meta=m("Große Farmen: „tausende Kakteen pro Stunde“ (Wiki, ohne genaue Zahl)",
               [("Überall auf Sand.", W + "Tutorial:Cactus_farming")],
               [("Kaktus bricht ab, sobald er neben einem Block wächst. Standard laut Wiki: Wasserströme unten "
                 "spülen die Stücke zu Trichtern.", W + "Tutorial:Cactus_farming"),
                (TEST + "3 Kakteen, die Stücke kommen in der Truhe an.", None)])),
    "kuerbis": dict(
        name="Kürbis- & Melonen-Farm", cat="Pflanzen", diff=2, out="Kürbisse, Melonen", where="Überall",
        afk="In der Nähe",
        why="Jeder Stängel lässt seine Frucht nur auf das Schlammfeld daneben wachsen (die anderen Seiten sind "
            "Wasser, Nachbarstängel oder Blöcke). Ein Beobachter schaut von oben auf einen Stängel: Ändert er sich "
            "(er wächst oder bekommt eine Frucht), drücken alle Kolben von oben auf die Fruchtfelder – Früchte "
            "zerbrechen, leere Felder macht das nichts. Die anderen Früchte warten bis dahin. Die Trichter unter dem "
            "Schlamm sammeln ein.",
        help=[("Frucht wächst nicht", "Fruchtfeld muss frei sein; der Stängel braucht Licht ≥ 9 (von der Seite "
                                      "reicht)."),
              ("Frucht wächst an der falschen Stelle", "An die Enden der Ackerreihe gehört je ein Block.")],
        meta=m("Keine belegte Zahl",
               [("Überall; der Stängel braucht Licht ≥ 9, das Fruchtfeld muss frei sein und auf Erde/Gras/"
                 "Ackerboden/Schlamm liegen.", None)],
               [("Kolben, die in Kürbis oder Melone drücken, zerbrechen sie und lassen das Item fallen.",
                 W + "Tutorial:Pumpkin_and_melon_farming"),
                (TEST + "4 Melonenstängel, ein Beobachter, die Scheiben landen in der Truhe.", None)])),
    "seetang": dict(
        name="Seetang-Farm", cat="Pflanzen", diff=2, out="Seetang → Getrockneter Seetang (Brennstoff)",
        where="Überall", afk="In der Nähe",
        why="Seetang wächst in Wasser nach oben. Das Becken ist 3 hoch: oben Wasserquellen, darunter fallendes "
            "Wasser – das reicht dem Seetang. Ist er oben angekommen, merkt es sein Beobachter, und die Kolben "
            "schlagen den 2. Block ab. Die Stücke schwimmen nach oben und treiben über den Trichter neben dem "
            "obersten Block (Bauweise nach dem Wiki-Bauplan).",
        help=[("Items treiben nicht in den Trichter", "Über den Trichtern muss das Wasser aus dem Becken fließen – "
                                                       "die oberste Reihe im Becken müssen Quellen sein."),
              ("Seetang wächst nicht", "Seetang lässt sich nur in vollem Wasser setzen: erst Wasser, dann Seetang.")],
        meta=m("Keine belegte Zahl",
               [("Überall – das Becken baust du selbst.", W + "Tutorial:Kelp_farming")],
               [("Wiki-Bauplan: Kolben am 2. Block, oben Wasser, daneben auf Höhe des obersten Seetangs ein "
                 "Trichter.", W + "Tutorial:Kelp_farming"),
                (TEST + "6 Seetang, fast alles landet in der Truhe.", None)])),
    "weizen": dict(
        name="Weizen/Karotten mit Bauern", cat="Pflanzen", diff=2, out="Weizen, Karotten, Kartoffeln, Rote Bete",
        where="Überall, weit weg von Dörfern", afk="In der Nähe",
        why="Ein Bauer (Dorfbewohner mit Komposter als Arbeitsplatz) erntet reife Feldfrüchte und pflanzt mit seinem "
            "eigenen Vorrat nach. Der Ackerboden liegt auf Trichtern – weil Ackerboden etwas niedriger ist, saugen sie "
            "die Ernte an, bevor der Bauer sie aufhebt. Darum gibst du ihm vorher einen Vorrat: am besten Karotten "
            "oder Kartoffeln (Samen über 10 Stück kompostiert er).",
        help=[("Bauer erntet nicht", "Er braucht den Komposter als Arbeitsplatz (kein Baby), arbeitet tagsüber; "
                                     "die Spielregel mobGriefing muss an sein."),
              ("Felder bleiben leer", "Sein Vorrat ist aufgebraucht – Tor auf, ihn kurz herausholen, ihm auf "
                                      "normalem Boden wieder einen Stapel zuwerfen (auf dem Feld schlucken die "
                                      "Trichter alles)."),
              ("Er kommt nicht hinein", "Mit Leine, Boot oder Lore durchs Zauntor bringen.")],
        meta=m("Keine belegte Zahl",
               [("Die Farm muss weit genug weg von Dörfern liegen, sonst läuft der Bauer zum Dorf.",
                 W + "Tutorial:Crop_farming"),
                ("Dach drauf, wenn Gewitter häufig sind: Blitze verwandeln Dorfbewohner in Hexen.",
                 W + "Tutorial:Crop_farming")],
               [(TEST + "Bauer mit Samen erntet und pflanzt nach, Weizen landet in der Truhe.", None)])),
    "baum": dict(
        name="Baum-/Holz-Farm", cat="Pflanzen", diff=1, out="Holz, Setzlinge, Äpfel", where="Überall",
        afk="Nein – halbautomatisch",
        why="Echtes Holz lässt sich in Vanilla nicht einfach vollautomatisch ernten. Am meisten Holz pro Baum gibt "
            "die Dunkle Eiche (2 × 2 Setzlinge). Knochenmehl drauf, mit Effizienz-Axt fällen, Setzlinge wieder "
            "pflanzen.",
        help=[("Baum wächst nicht", "Nach oben mindestens 10 Blöcke frei (oben auch zur Seite), Licht ≥ 9, "
                                    "4 Setzlinge der Dunklen Eiche genau im Quadrat.")],
        meta=m("Dunkle Eiche: im Schnitt ca. 42 Holz und 6 Setzlinge pro Baum (Wiki)",
               [("Dunkle Eiche wächst nur aus 4 Setzlingen im Quadrat und braucht nach oben Platz.",
                 W + "Tutorial:Tree_farming")],
               [("Glück (Fortune) auf dem Werkzeug erhöht die Setzlings-Chance.", W + "Tutorial:Tree_farming")])),
    "knochenmehl": dict(
        name="Knochenmehl-Farm (Komposter)", cat="Pflanzen", diff=1, out="Knochenmehl", where="Überall",
        afk="In der Nähe",
        why="Ein Komposter macht aus Pflanzen Knochenmehl. Der obere Trichter füllt ihn, der untere holt das "
            "fertige Knochenmehl heraus und gibt es in die Truhe. Gut an jede Pflanzenfarm anzuschließen.",
        help=[("Kein Knochenmehl", "Manche Pflanzen haben nur eine kleine Chance pro Item (Samen 30 %, Kaktus und "
                                   "Melonenscheiben 50 %, Kürbis 65 %) – es braucht viele.")],
        meta=m("Je nach Pflanzen-Nachschub",
               [("Überall.", W + "Tutorial:Crop_farming")],
               [("Einfachster Kompost-Automat: Trichter, Komposter, Trichter, Truhe.", W + "Composter"),
                (TEST + "320 Samen ergaben 16 Knochenmehl.", None)])),
    "blumen": dict(
        name="Blumen-Farm", cat="Pflanzen", diff=1, out="Blumen → Farbstoffe",
        where="In einem Biom mit passenden Blumen (z. B. Blumenwald)", afk="Nein – Knopf drücken",
        why="Knochenmehl auf eine hohe Blume (Sonnenblume, Flieder, Rosenstrauch, Pfingstrose) lässt eine Kopie "
            "fallen, die Blume bleibt stehen. Ein Spender daneben macht das auf Knopfdruck – beliebig oft. Gelb, "
            "Magenta, Rot und Rosa als Farbstoff; andere Blumen wachsen mit Knochenmehl auf Gras je nach Biom.",
        help=[("Nichts passiert", "Der Spender muss auf die untere Hälfte der Blume zeigen; Knochenmehl hinein."),
              ("Andere Farben", "Kleine Blumen wachsen mit Knochenmehl auf Gras – welche, bestimmt das Biom "
                                "(Blumenwald hat fast alle).")],
        meta=m("Keine belegte Zahl",
               [("Welche Blumen wachsen, bestimmt das Biom. Im Blumenwald gibt es fast alle.",
                 W + "Tutorial:Flower_farming")],
               [("Hohe Blumen lassen mit Knochenmehl eine Kopie fallen.", W + "Bone_Meal"),
                (TEST + "Knochenmehl auf Gras wirkt nur einmal (danach wächst etwas darauf) – darum die hohe "
                        "Blume.", None)])),
    "huehner": dict(
        name="Hühner-Farm (automatisch)", cat="Tiere", diff=2, out="Gebratenes Hühnchen, Federn", where="Überall",
        afk="In der Nähe",
        why="Hühner legen Eier in den Trichter unter sich, der füllt den Spender. Zwei Beobachter, die sich "
            "anschauen, geben einen dauernden Takt – der Spender wirft jedes Ei auf den Steinschneider. Küken "
            "wachsen dort heran. Erwachsene Hühner sind größer und berühren mit dem Kopf die Lava im Kessel darüber – "
            "sie werden gegart, das Hühnchen fällt durch den Steinschneider in den Trichter.",
        help=[("Kein gebratenes Hühnchen", "Kessel genau über dem Steinschneider, mit Lava gefüllt; rundherum Glas, "
                                           "sonst entkommen Küken."),
              ("Eier bleiben im Spender", "Die zwei Beobachter müssen sich gegenseitig anschauen (Takt)."),
              ("Beobachter zeigt falsch", "Ein Beobachter schaut in die Richtung, in die du beim Setzen schaust – "
                                          "notfalls einen Hilfsblock setzen und danach wieder abbauen."),
              ("Wie kommen die Hühner hinein?", "Eier in den Schacht über dem Trichter werfen oder ein Huhn mit "
                                                "Samen hineinlocken.")],
        meta=m("Keine belegte Zahl",
               [("Überall.", W + "Tutorial:Egg_farming")],
               [("Lava zerstört gebratenes Hühnchen sofort – darum der Kessel mit Lava über einem Steinschneider: nur "
                 "der Kopf ragt hinein.", W + "Tutorial:Egg_farming"),
                (TEST + "erwachsenes Huhn auf dem Steinschneider → gebratenes Hühnchen in der Truhe.", None)])),
    "kuh": dict(
        name="Kuh-Gehege (Leder & Steak)", cat="Tiere", diff=1, out="Leder, Steak", where="Überall",
        afk="Nein – halbautomatisch",
        why="Kühe vermehren sich, wenn du zwei mit Weizen fütterst; das Kalb ist nach 20 Minuten groß. Ein "
            "Zaun-Gehege reicht: zwei Kühe behalten, die übrigen schlachten (am besten mit Plünderung, Flammen-"
            "Schwert = gebratenes Steak).",
        help=[("Zu eng", "In ein 3 × 3-Gehege passen gut 8 Kühe – vorher schlachten oder das Gehege vergrößern."),
              ("Kühe vermehren sich nicht", "Nach dem Füttern 5 Minuten warten, bis es wieder geht.")],
        meta=m("Keine belegte Zahl",
               [("Überall.", W + "Tutorial:Animal_farming")],
               [(TEST + "zwei gefütterte Kühe bekamen ein Kalb, alle blieben im Gehege.", None)])),
    "wolle": dict(
        name="Wolle-Farm", cat="Tiere", diff=2, out="Wolle (jede Farbe)", where="Überall", afk="Ja",
        why="Das Schaf steht auf einem Grasblock. Frisst es, wird das Gras zu Erde und seine Wolle wächst nach – "
            "der Beobachter merkt den Wechsel, und der Spender mit der Schere schert es. Die Wolle fällt auf das "
            "Gras; die Trichterlore darunter saugt sie durch den vollen Block an.",
        help=[("Schaf frisst nicht", "Echter Grasblock nötig; Gras daneben (Boden) lässt die Erde wieder grün "
                                     "werden."),
              ("Spender schert nicht", "Redstone auf dem Block hinter dem Beobachter, Spender direkt daneben.")],
        meta=m("Ein Schaf hat nach 50 s zu 63 % und nach 2 min zu über 90 % neue Wolle (Wiki)",
               [("Überall; das Schaf steht auf einem echten Grasblock.", W + "Tutorial:Wool_farming")],
               [("Wiki-Design: Spender mit Schere, Beobachter schaut aufs Gras, Trichterlore unter dem Gras.",
                 W + "Tutorial:Wool_farming"),
                ("Fehlversuche (Schaf ohne Wolle) nutzen die Schere nicht ab.", W + "Shears"),
                (TEST + "ein Schaf, die Wolle landet in der Truhe.", None)])),
    "honig": dict(
        name="Honigwaben-Farm", cat="Tiere", diff=2, out="Honigwaben (Kerzen, Bienenstöcke)", where="Bei Blumen",
        afk="Ja",
        why="Ein Spender mit Schere zeigt auf das Bienennest. Zwei Beobachter geben einen dauernden Takt: der "
            "Spender versucht immer wieder zu scheren. Erst bei vollem Nest (Stufe 5) klappt es – 3 Waben fallen "
            "vorne heraus in den Trichter. Fehlversuche kosten die Schere nichts. Ernten per Spender macht die Bienen "
            "nicht wütend. Honigflaschen erntest du von Hand (Lagerfeuer unter das Nest).",
        help=[("Keine Waben", "Bienen brauchen Blumen in der Nähe. Vorne vor dem Nest muss frei sein."),
              ("Waben liegen daneben", "Links, rechts und hinter dem Nest Blöcke – nur vorne frei, dort der "
                                       "Trichter.")],
        meta=m("Keine belegte Zahl",
               [("Bei Blumen; Bienen kommen aus Bienennestern (mit Behutsamkeit umziehen).",
                 W + "Tutorial:Honey_farming")],
               [("Ernten per Spender macht die Bienen nicht wütend.", W + "Tutorial:Honey_farming"),
                (TEST + "Glasflaschen werden bei nicht vollem Nest herausgeworfen – Scheren nicht. Darum Schere + "
                        "Takt.", None)])),
    "eisen": dict(
        name="Eisenfarm (Golem)", cat="Mobs", diff=3, out="Eisenbarren, Mohnblumen", where="Weit weg von Dörfern",
        afk="In der Nähe (Simulationsdistanz)",
        why="Dorfbewohner rufen einen Eisengolem, wenn mindestens 3 von ihnen in Panik sind (sie sehen einen Zombie) "
            "und alle in den letzten 20 Minuten geschlafen haben. Der Golem spawnt auf der Plattform (Glas, Leuchten "
            "und Betten sind tabu), Wasser schiebt ihn ins Loch, er fällt in den Schacht und steckt mit dem Kopf in "
            "der Lava. Nachts schließt eine Falltür (Tageslichtsensor im Nacht-Modus) das Fenster zum Zombie, damit "
            "die Dorfbewohner schlafen können.",
        help=[("Keine Golems", "Haben die Dorfbewohner geschlafen? Sehen sie den Zombie (nicht durch Glas!)? Lebt in "
                               "16 Blöcken ein anderer Golem?"),
              ("Zombie stirbt", "Stufe über ihm (Schatten) und Namensschild geben."),
              ("Golem spawnt woanders", "Alle Flächen 8 Blöcke um die Dorfbewohner und bis 6 darunter aus Glas, "
                                        "oder die Farm hoch genug bauen.")],
        meta=m("Im Wiki keine belegte Zahl.",
               [("Weit weg von echten Dörfern und deren Golems.", W + "Tutorial:Iron_golem_farming")],
               [("Panik-Methode: 3 Dorfbewohner, ein Zombie in 8 Blöcken mit Sicht (Glas versperrt die Sicht), alle "
                 "müssen in den letzten 20 Minuten geschlafen haben.", W + "Iron_Golem"),
                ("Golems spawnen nie auf Glas, Leuchtstein, Seelaterne, Eis, Laub.", W + "Iron_Golem")])),
    "xpspawner": dict(
        name="XP-Farm am Spawner", cat="Mobs", diff=2, out="XP, Knochen, Pfeile, Fleisch",
        where="Zombie- oder Skelett-Spawner im Verlies", afk="Innerhalb 16 Blöcken vom Spawner",
        why="Spawner erzeugen Mobs, solange ein Spieler höchstens 16 Blöcke entfernt ist. Wasser schiebt alle Mobs "
            "durch eine Tür in eine kleine Zelle (ein Schild hält das Wasser auf). Du stehst eine Ebene tiefer und "
            "triffst ihre Beine durch einen Spalt – sie sehen dich nicht und kommen nicht heraus. Kein Aufzug nötig.",
        help=[("Spawner spawnt nicht", "Höchstens 16 Blöcke entfernt bleiben; keine Fackeln im Raum."),
              ("Mobs kommen nicht in die Zelle", "Wasser an der Nordwand muss bis kurz vor die Südwand fließen, die "
                                                 "beiden Eck-Quellen schieben zur Tür.")],
        meta=m("Keine belegte Zahl",
               [("An einem Zombie- oder Skelett-Spawner (Verlies).", W + "Tutorial:Monster_spawner_traps")],
               [("XP gibt es nur, wenn ein Spieler tötet.", W + "Tutorial:Monster_spawner_traps"),
                ("Spawner: 4 Versuche alle 10–40 s im Bereich ±4 Blöcke.", W + "Monster_Spawner")])),
    "mobfarm": dict(
        name="Allgemeine Monster-Farm", cat="Mobs", diff=3, out="Knochen, Pfeile, Fäden, Schwarzpulver, Fleisch",
        where="Unter der Erde (oder als dunkler Kasten in der Luft)", afk="24–32 Blöcke unter dem Raum",
        why="Monster spawnen bei Licht 0, wenn kein Spieler näher als 24 Blöcke ist. Ein dunkler Raum 10 × 10, "
            "2 hoch: Wasser in Kreuzform schiebt alles zum Loch in der Mitte; Schilder halten das Wasser oben. "
            "24 Blöcke Fall töten Zombies, Skelette, Creeper und Spinnen; unten sammeln Trichter. Weiter als 32 "
            "Blöcke weg laufen Monster nicht mehr herum – darum wartest du direkt unten.",
        help=[("Wenig Mobs", "Höhlen in 128 Blöcken ausleuchten – sie konkurrieren. Weit weg von Höhlen bauen."),
              ("Mobs bleiben am Rand stehen", "Sie laufen zufällig ins Wasser; das dauert etwas.")],
        meta=m("Keine belegte Zahl",
               [("Java: Spawn-Radius 128 Blöcke, nicht näher als 24 am Spieler.", W + "Mob_spawning")],
               [("Kanal-Design: dunkler Raum 2 hoch, Wasserkanäle zur Mitte, ca. 24 Blöcke Fall.",
                 W + "Tutorial:Mob_farm"),
                ("Monster weiter als 32 Blöcke vom Spieler laufen nach 5 s nicht mehr zufällig herum.",
                 W + "Mob_spawning")])),
    "creeper": dict(
        name="Creeper-Farm (Schwarzpulver)", cat="Mobs", diff=3, out="Schwarzpulver",
        where="Unter der Erde (oder als dunkler Kasten in der Luft)", afk="24–32 Blöcke unter dem Raum",
        why="Wie die Monster-Farm, nur kleiner und mit Falltüren in der oberen Hälfte der zweiten Ebene: Es bleiben "
            "1,8 Blöcke Platz. Creeper (1,7 hoch) passen hinein, Zombies, Skelette und Hexen (fast 2 hoch) nicht. "
            "Spinnen passen auch (Fäden als Beifang).",
        help=[("Zombies spawnen trotzdem", "Falltüren müssen in der OBEREN Hälfte sitzen (an die Unterseite der "
                                           "Decke klicken)."),
              ("Wenig Creeper", "Höhlen in 128 Blöcken ausleuchten.")],
        meta=m("Keine belegte Zahl",
               [("Java: 2 Blöcke hoher Raum mit geschlossenen Falltüren oben → 1 13/16 Blöcke frei: nur Creeper und "
                 "Spinnen passen.", W + "Tutorial:Creeper_farming")],
               [("Creeper haben 20 Leben; 24 Blöcke Fall töten sie.", W + "Creeper")])),
    "schleim": dict(
        name="Schleim-Farm", cat="Mobs", diff=2, out="Schleimbälle", where="Schleim-Chunk unter Höhe 40",
        afk="24–32 Blöcke weg warten, dann erschlagen",
        why="Schleime spawnen in bestimmten Chunks (Schleim-Chunks, 10 % aller Chunks) unter Y 40 – egal wie hell. "
            "Grabe den ganzen Chunk 3 hoch aus (sie brauchen über 2 Blöcke Platz), warte 24–32 Blöcke weg (näher "
            "spawnt nichts) und erschlage sie dann. Ganz ohne Material.",
        help=[("Keine Schleime", "Bist du im richtigen Chunk? Grenzen mit F3+G anzeigen; Chunkbase hilft."),
              ("Nur kleine Schleime", "Normal – große zerfallen beim Tod in kleinere.")],
        meta=m("Keine belegte Zahl",
               [("Schleim-Chunk, unter Y = 40 – finden z. B. mit dem Chunkbase Slime Chunk Finder.",
                 W + "Tutorial:Slime_farming"),
                ("Unter Y 40 im Schleim-Chunk: jedes Licht, jedes Wetter; braucht 3 × 3 Platz und über 2 Blöcke "
                 "Höhe.", W + "Slime")],
               [("Automatisch: Eisengolem als Köder, Magmablöcke töten, Trichter daneben sammeln.",
                 W + "Tutorial:Slime_farming")])),
    "hexe": dict(
        name="Hexen-Farm", cat="Mobs", diff=3, out="Redstone, Glowstone-Staub, Zucker, Flaschen",
        where="Hexenhütte im Sumpf", afk="Unten am Schacht (nachts)",
        why="In der Box einer Hexenhütte (7 × 9 Grundfläche) spawnen nur Hexen. Eine Plattform genau unter der Box, "
            "Wasser schiebt jede Hexe zum Loch hinten in der Mitte (Schild hält das Wasser), 29 Blöcke Fall töten "
            "sie (26 Leben). Ohne Dach läuft die Farm nachts; ein dunkles Dach drüber macht sie auch tagsüber.",
        help=[("Keine Hexen", "Die Plattform muss genau in der Box liegen: Hexenfüße auf Höhe des Box-Bodens."),
              ("Hexen überleben", "Schacht mindestens 29 Blöcke tief.")],
        meta=m("Keine belegte Zahl",
               [("Hexenhütte im Sumpf; die Box ist 7 × 7 × 9 und reicht von 1 unter dem Hüttenboden bis 2 über das "
                 "Dach – bis zu 3 Plattformen passen hinein.", W + "Swamp_Hut")],
               [("Hexen haben 26 Leben – sie brauchen mindestens 29 Blöcke Fall.", W + "Witch")])),
    "waechter": dict(
        name="Wächter-Jagd (Monument)", cat="Mobs", diff=3, out="Prismarin, Fisch, XP",
        where="Ozeanmonument", afk="Nein – du kämpfst",
        why="Wächter spawnen nur im Wasser in der Box eines Ozeanmonuments. Eine echte Farm ist ein Großprojekt "
            "(trockenlegen oder Blasensäulen-Aufzüge). Am einfachsten: eine kleine Plattform an der Wasseroberfläche "
            "über dem Monument – die Wächter kommen hoch, du triffst sie mit Dreizack oder Schwert.",
        help=[("Abbaulähmung", "Erst die 3 Großen Wächter besiegen (sonst kannst du kaum abbauen)."),
              ("Laser treffen dich", "Hinter einem Block in Deckung gehen, dann zuschlagen.")],
        meta=m("Keine belegte Zahl",
               [("Ozeanmonument; Wächter spawnen nur in seiner Box, in Wasser.", W + "Tutorial:Guardian_farming")],
               [("Automatische Varianten: Seelensand-Aufzug zur Tötungskammer ohne Trockenlegen; laut Wiki heute "
                 "üblich.", W + "Tutorial:Guardian_farming")])),
    "lohe": dict(
        name="Lohen-Spawner (Kampfraum)", cat="Nether", diff=2, out="Lohenruten, XP",
        where="Lohen-Spawner in einer Netherfestung", afk="Nein – du kämpfst",
        why="Lohen kommen aus dem Spawner, solange du höchstens 16 Blöcke entfernt bist. Mauere den Raum um den "
            "Spawner ein (9 × 9), damit sie nicht wegfliegen, trink Feuerresistenz und schlag sie mit dem Schwert – "
            "Lohenruten gibt es nur, wenn du triffst. Wasser geht im Nether nicht.",
        help=[("Zu viele Feuerbälle", "Feuerresistenz-Trank; Rücken an eine Wand."),
              ("Spawner spawnt nicht", "Nicht zu hell (Licht ≤ 11); höchstens 6 Lohen auf einmal.")],
        meta=m("Lohen geben doppelt so viel XP wie normale Mobs (Wiki)",
               [("Am Lohen-Spawner in einer Netherfestung.", W + "Tutorial:Blaze_farming")],
               [("Spawner: Bereich ±4 Blöcke, hört bei 6 Lohen im Umkreis auf.", W + "Monster_Spawner"),
                ("Untätige Lohen sinken langsam – große Farmen nutzen das für einen Trichter zur Tötungszelle.",
                 W + "Blaze")])),
    "gold": dict(
        name="Gold-Farm (Zombifizierte Piglins)", cat="Nether", diff=3, out="Goldnuggets, verrottetes Fleisch",
        where="Nether-Ödland, am besten auf dem Netherdach", afk="24 Blöcke unter der Plattform",
        why="Zombifizierte Piglins spawnen auf Netherrack. Sie wollen das Schildkrötenei zertrampeln – erreichbar ist "
            "es nur über ein Loch mit einer offenen Falltür, die sie für Boden halten. Sie fallen 24 Blöcke und "
            "sterben. Seit 1.21.5 gibt es XP und Goldbarren nur, wenn du selbst tötest.",
        help=[("Piglins greifen alle an", "Nie einen schlagen – sonst wird die ganze Gruppe wütend."),
              ("Ghasts", "Ein Dach aus Stufen 3 Blöcke über der Plattform hält sie fern.")],
        meta=m("Keine belegte Zahl",
               [("Nether-Ödland; über dem Netherdach muss man nichts absichern.",
                 W + "Tutorial:Zombified_piglin_farming")],
               [("Schildkrötenei als Köder über einem Loch mit offenen Falltüren; 23 Blöcke Fall töten, 22 lassen "
                 "1 Leben.", W + "Tutorial:Zombified_piglin_farming"),
                ("Seit 1.21.5: XP und Spieler-Beute nur, wenn ein Spieler tötet.", W + "Zombified_Piglin")])),
    "witherskelett": dict(
        name="Wither-Skelett-Platz", cat="Nether", diff=3, out="Wither-Schädel, Kohle, Knochen",
        where="Netherfestung", afk="24–32 Blöcke weg warten, dann kämpfen",
        why="In der Box einer Netherfestung spawnen Wither-Skelette auf Netherziegeln, im Dunkeln (Licht ≤ 7). Eine "
            "freie Fläche 9 × 9 mit 3 Blöcken Platz (sie sind 2,4 hoch) reicht. Näher als 24 Blöcke spawnt nichts – "
            "warte etwas weg und kämpfe dann mit Plünderung III.",
        help=[("Zu viele andere Mobs", "Andere Flächen der Festung mit Stufen/Teppichen belegen."),
              ("Keine Schädel", "Nur bei Tod durch dich; 2,5 % Chance, +1 % je Plünderungsstufe.")],
        meta=m("Schädel: 2,5 % Grundchance, 5,5 % mit Plünderung III – nur bei Tod durch Spieler (Wiki)",
               [("Netherfestung; außerhalb der einzelnen Festungsteile nur auf Netherziegeln.",
                 W + "Wither_Skeleton")],
               [("Wither-Skelette rennen auf Piglins und Eisengolems in 16 Blöcken los – damit lassen sie sich in "
                 "eine Grube locken.", W + "Tutorial:Wither_skeleton_farming")])),
    "enderman": dict(
        name="Enderman-Farm (End)", cat="End", diff=3, out="Enderperlen, XP",
        where="Im End, ~128 Blöcke von anderen Inseln", afk="Unten an der Landestelle",
        why="Endermen hassen Endermilben. Eine Endermilbe mit Namensschild sitzt in einer Lore in der Mitte; "
            "erreichbar nur über ein Loch mit offener Falltür. Die Endermen fallen 42 Blöcke und kommen mit ½ Herz an "
            "– ein Schlag, XP und Perlen. Du stehst 3 Blöcke über ihnen, so erreichen sie dich nicht.",
        help=[("Endermilbe verschwindet", "Ohne Namensschild verschwindet sie nach 2 Minuten."),
              ("Wenig Endermen", "Mindestens 128 Blöcke von anderen Inseln bauen.")],
        meta=m("Keine belegte Zahl",
               [("Im End, mindestens 128 Blöcke von anderen Spawnflächen.", W + "Tutorial:Enderman_farming")],
               [("Endermilben-Köder: laut Wiki eine der billigsten und effizientesten Farmen.",
                 W + "Tutorial:Enderman_farming"),
                ("Seit 1.20.2 musst du mindestens 3 Blöcke über ihnen stehen.", W + "Tutorial:Enderman_farming")])),
    "ertrunkene": dict(
        name="Ertrunkenen-Farm (Fluss)", cat="Mobs", diff=3, out="Kupfer, Dreizacke, Nautilusschalen",
        where="Flussbiom", afk="Unten an der Landestelle",
        why="In Flussbiomen spawnen Ertrunkene in dunklem Wasser (2 tief, Licht 0) in jeder Höhe. Das geschlossene "
            "Becken ist stockdunkel; durch die Schilder im Boden fallen sie 22 Blöcke und kommen mit 1 Leben an. "
            "Du triffst ihre Beine durch einen Spalt – Dreizacke gibt es nur, wenn du tötest.",
        help=[("Keine Ertrunkenen", "Becken komplett im Flussbiom (F3), innen kein Licht, 2 Ebenen Wasser."),
              ("Keine Dreizacke", "Nur Ertrunkene, die mit Dreizack spawnen, lassen einen fallen (selten).")],
        meta=m("Keine belegte Zahl",
               [("Flussbiom: dort spawnen Ertrunkene in jeder Höhe (im Ozean nur unter Y 58).", W + "Drowned")],
               [("22 Blöcke Fall lassen ihnen 1 Leben.", W + "Damage"),
                ("Dreizack: 6,25 % spawnen mit einem; 8,5 % Drop-Chance, nur bei Tod durch Spieler.",
                 W + "Drowned")])),
    "aussenposten": dict(
        name="Außenposten-Gruben", cat="Mobs", diff=2, out="Unheilvolle Flaschen, Armbrüste, Pfeile",
        where="Am Plünderer-Außenposten", afk="28 Blöcke über dem Boden",
        why="Am Außenposten spawnen Plünderer immer wieder (auch wenn er abgebaut ist). Sie laufen herum und fallen "
            "in Gruben mit offener Falltür (sieht aus wie Boden) auf ein Lagerfeuer. Jeder Hauptmann lässt beim Tod "
            "eine Unheilvolle Flasche fallen – auch durchs Lagerfeuer. Trichter darunter sammeln.",
        help=[("Keine Flaschen", "Nur Hauptmänner (Banner auf dem Kopf) – etwa jeder 17. Plünderer."),
              ("Plünderer bleiben weg", "Du musst mehr als 24 und höchstens 32 Blöcke entfernt sein.")],
        meta=m("6 % der Plünderer werden Hauptmann; jeder lässt 1 Unheilvolle Flasche fallen (Wiki)",
               [("Spawn-Box laut Wiki: 72 × 54 × 72, mittig auf dem obersten Stockwerk.", W + "Pillager_Outpost")],
               [("Ein Hauptmann außerhalb eines Überfalls lässt immer eine Unheilvolle Flasche fallen.",
                 W + "Pillager")])),
    "ueberfall": dict(
        name="Überfall-Arena", cat="Mobs", diff=3, out="Totems, Smaragde, Sattel, Armbrüste",
        where="Weit weg von Dörfern", afk="Nein – du kämpfst",
        why="Ein Bett mit einem Dorfbewohner ist schon ein „Dorf“. Trinkst du eine Unheilvolle Flasche und kommst "
            "her, beginnt nach 30 Sekunden ein Überfall. Von deinem Turm aus erledigst du die Wellen mit Bogen oder "
            "Armbrust; Nahkämpfer kommen nicht hinauf. Eine vollautomatische Raid-Farm ist ein Großprojekt über dem "
            "Ozean.",
        help=[("Überfall startet nicht", "Der Dorfbewohner muss das Bett beansprucht haben (grüne Partikel)."),
              ("Plagegeister (Vexe)", "Magier zuerst erledigen – ihre Plagegeister fliegen durch Wände.")],
        meta=m("Keine belegte Zahl",
               [("Ein Dorf ist schon ein beanspruchtes Bett, ein Arbeitsplatz oder eine Glocke.", W + "Raid")],
               [("Seit 1.21: Unheilvolle Flasche → Überfall-Omen; der Überfall startet 30 s nach Betreten des Dorfs.",
                 W + "Raid_Omen"),
                ("Automatische Farmen stehen über dem Ozean, mind. 7 Chunks vom Land.",
                 W + "Tutorial:Raid_farming")])),
    "handel": dict(
        name="Handelshalle (Smaragde)", cat="Handel", diff=2, out="Smaragde, verzauberte Bücher, Werkzeuge",
        where="Überall", afk="Nein",
        why="Jeder Dorfbewohner steht in einer 1 × 1-Zelle direkt vor seinem Arbeitsblock (dort füllt er bis zu "
            "2-mal am Tag seine Angebote auf). Oben ist zu, unten bleibt eine 1 Block hohe Lücke: Du kannst handeln, "
            "er kommt nicht heraus. Ein Pfeilmacher kauft z. B. 32 Stöcke für 1 Smaragd.",
        help=[("Handel ausverkauft", "Der Dorfbewohner muss seinen Arbeitsblock erreichen (direkt hinter ihm)."),
              ("Falscher Handel", "Vor dem ersten Handel den Arbeitsblock abbauen und neu setzen.")],
        meta=m("Pfeilmacher kauft 32 Stöcke → 1 Smaragd, 16-mal, bis zu 2× Auffüllen pro Tag",
               [("Überall.", W + "Tutorial:Villager_trading_hall")],
               [("Rabatte durch Heilen eines Zombie-Dorfbewohners.", W + "Tutorial:Villager_trading_hall"),
                (TEST + "4 Dorfbewohner bleiben in ihren Zellen.", None)])),
    "bruchstein": dict(
        name="Bruchstein-Generator", cat="Blöcke", diff=1, out="Bruchstein", where="Überall",
        afk="Nein – abbauen",
        why="Fließende Lava trifft auf Wasser → Bruchstein. Der Graben liegt im Boden (kein Material außer zwei "
            "Eimern): Wasser fließt ins Loch und bleibt dort, Lava fließt bis daneben.",
        help=[("Obsidian entsteht", "Wasser darf nie auf die Lava-QUELLE fließen – deshalb das Loch."),
              ("Kein Bruchstein", "Erst das Wasser, dann die Lava.")],
        meta=m("So schnell du abbaust",
               [("Überall.", W + "Tutorial:Cobblestone_farming")],
               [(TEST + "Bruchstein bildet sich neu.", None)])),
    "lava": dict(
        name="Lava-Farm (Tropfstein)", cat="Blöcke", diff=1, out="Lava-Eimer (Brennstoff)", where="Überall",
        afk="In der Nähe",
        why="Spitzer Tropfstein unter einem Block mit Lava darüber füllt einen Kessel darunter langsam mit Lava – "
            "ganz ohne Nachschub. Ein Eimer Lava brennt 100 Items im Ofen.",
        help=[("Füllt sich nicht", "Erst den Block, dann den Tropfstein darunter hängen; Kessel genau unter der "
                                   "Spitze; Spieler in der Nähe.")],
        meta=m("Pro Kessel im Schnitt etwa ein Minecraft-Tag pro Füllung (Wiki)",
               [("Überall. Im Nether braucht der Tropfstein keine Lavaquelle darüber.", W + "Pointed_Dripstone")],
               [("Lavaquelle über einem Block, darunter spitzer Tropfstein; ein leerer Kessel darunter füllt sich.",
                 W + "Pointed_Dripstone"),
                (TEST + "4 Kessel füllten sich.", None)])),
    "schnee": dict(
        name="Schnee-Farm", cat="Blöcke", diff=1, out="Schneebälle, Schneeblöcke",
        where="Kaltes Biom (in warmen schmilzt der Golem)", afk="Nein – halbautomatisch",
        why="Ein Schneegolem hinterlässt überall, wo er steht, eine Schneedecke – sofort wieder, wenn du sie "
            "abbaust. Er steht in einer Glaskammer mit Dach (Regen schadet ihm); vorne unten bleibt ein Spalt, durch "
            "den du mit der Schaufel die Schneedecke abbaust.",
        help=[("Golem schmilzt", "Nur in kalten Biomen."),
              ("Kein Schnee", "Spielregel mobGriefing muss an sein.")],
        meta=m("Keine belegte Zahl (Schneebälle stapeln nur bis 16)",
               [("In Wüste, Tafelbergen, Savannen und im Nether schmilzt der Golem.", W + "Snow_Golem")],
               [("Golem in einer 1 × 1-Zelle, Dach gegen Regen, Schneedecke mit Schaufel abbauen.",
                 W + "Tutorial:Snow_farming")])),
    "angeln": dict(
        name="Angel-Teich", cat="Sonstiges", diff=1, out="Fisch, Schätze (Bücher, Bögen)",
        where="Überall", afk="Von Hand",
        why="Schätze gibt es nur in „offenem Wasser“: rund um den Schwimmer 5 × 5 Wasser, 2 tief, darüber 2 Blöcke "
            "Luft. Ein ausgehobenes Becken 5 × 5 × 2 reicht genau. Mit Glück III und Köder III wird es richtig gut.",
        help=[("Nur Fisch, keine Schätze", "Das Wasser ist nicht „offen“ – nichts im Becken, darüber frei.")],
        meta=m("Keine belegte Zahl",
               [("Offenes Wasser: um den Schwimmer 5 × 5, die Ebene darunter und die des Schwimmers Wasser, die "
                 "zwei darüber Luft.", W + "Fishing")],
               [("Beste Angel: Köder III, Glück des Meeres III, Haltbarkeit III, Reparatur.",
                 W + "Tutorial:Fish_farming")])),
    "stockcrafter": dict(
        name="Stöcke-Autocrafter", cat="Handel", diff=1, out="Stöcke (für Pfeilmacher-Smaragde)",
        where="An einer Bambusfarm", afk="Ja",
        why="Im Crafter sind 7 Felder gesperrt, nur links oben und links Mitte sind frei – genau das Stock-Rezept "
            "(2 Bambus übereinander). Zwei Beobachter, die sich anschauen, geben einen dauernden Takt: Sind beide "
            "Felder voll, entsteht ein Stock und fällt nach unten in die Truhe; sonst passiert nichts.",
        help=[("Keine Stöcke", "Crafter-Vorderseite muss nach unten zur Truhe zeigen; genau 7 Felder sperren.")],
        meta=m("So schnell, wie Bambus nachkommt (2 Bambus → 1 Stock)",
               [("Direkt an einer Bambusfarm.", None)],
               [(TEST + "128 Bambus → 64 Stöcke.", None)])),
}

# ---------------------------------------------------------------------------------------------------------------
# Nachgeschärft nach der Gegenprüfung und den Mechanik-Tests (Mobs in die Farm gesetzt)
TEXTE["hexe"].update(
    afk="Auf der Treppe, 26 Blöcke unter den Hexenfüßen (24–32 Blöcke weg)",
    why="In der Box einer Hexenhütte (7 × 9 Grundfläche) spawnen nur Hexen – aber nicht im Wasser. Darum ist die "
        "Plattform trocken; mittendurch läuft ein 2 tiefer Kanal mit offenen Falltüren darüber. Hexen halten sie für "
        "Boden, fallen hinein, das Wasser schiebt sie zum Schacht, 32 Blöcke Fall töten sie (26 Leben). Ohne Dach "
        "läuft die Farm nachts; ein dunkles Dach macht sie auch tagsüber.",
    help=[["Keine Hexen", "Der Boden muss genau unter der Box liegen: deine Füße eine Ebene unter dem alten "
                          "Hüttenboden, dann den Plan mit den Pfeilen im Plan-Menü verschieben."],
          ["Hexen bleiben im Kanal", "Falltüren über dem Kanal offen, im Loch am Ende eine offene Falltür auf "
                                     "Wasserhöhe."],
          ["Hexen stehen nur herum", "Höchstens 32 Blöcke weg warten – weiter weg laufen Mobs nicht herum (im Test "
                                     "nachgeprüft)."]])
TEXTE["aussenposten"].update(
    afk="Oben auf dem Gerüstturm, 28 Blöcke hoch",
    why="Am Außenposten spawnen Plünderer immer wieder (auch wenn er abgebaut ist). Du wartest oben auf einem Turm aus "
        "Gerüst – durch Gerüst sehen sie hindurch. Sie rennen zu dir, treten auf die offenen Falltüren rund um den "
        "Turm (sieht aus wie Boden) und sitzen in 2 tiefen Gruben fest. Ab und zu runter und sie erledigen: Jeder "
        "Hauptmann (Banner auf dem Kopf) lässt eine Unheilvolle Flasche fallen.")
TEXTE["gold"]["help"] = TEXTE["gold"]["help"] + [
    ["Wenig Gold", "Spawns verteilen sich auf alle dunklen Flächen bis 128 Blöcke um dich – auch auf Höhlen unter dem "
                   "Dach. Mehr Plattform = mehr Piglins: Netherrack ist billig, die Plattform darf viel größer sein "
                   "(alle Wege führen zum Loch am Ei)."]]
TEXTE["ertrunkene"].update(
    why="In Flussbiomen spawnen Ertrunkene in dunklem Wasser (die Stelle und der Block darunter Wasser, darüber Platz) "
        "in jeder Höhe. Das geschlossene Becken ist stockdunkel; durch die Schilder im Boden sinken sie in den Schacht "
        "und kommen mit wenig Leben unten an. Du triffst ihre Beine durch einen Spalt – Dreizacke gibt es nur, wenn du "
        "tötest.")
TEXTE["gold"].update(
    where="Nether-Ödland, am besten über dem Netherdach", afk="Unten am Trichter, 25 Blöcke unter der Plattform",
    why="Zombifizierte Piglins spawnen auf Netherrack. Sie wollen das Schildkrötenei zertrampeln – erreichbar ist es "
        "nur über ein Loch mit einer offenen Falltür, die sie für Boden halten. Sie fallen 25 Blöcke und sterben. Seit "
        "1.21.5 gibt es XP und Goldbarren nur, wenn du selbst tötest – dafür die Plattform nur 22 Blöcke hoch bauen "
        "und unten zuschlagen.")
TEXTE["enderman"].update(
    afk="Unten in der Mitte der Landestelle",
    why="Endermen hassen Endermilben. Eine Endermilbe mit Namensschild sitzt in einer Lore in der Mitte, rundherum ein "
        "Ring aus Löchern mit offenen Falltüren (sie halten sie für Boden). Sie fallen 44 Blöcke und sterben. Du "
        "stehst unten in der Mitte (dort fällt keiner hin) und sammelst die Perlen ein. Für XP: nur 42 Blöcke tief – "
        "dann kommen sie mit ½ Herz an; stell dich dann 3 Blöcke über sie.")
TEXTE["schleim"].update(
    why="Schleime spawnen in bestimmten Chunks (Schleim-Chunks, 10 % aller Chunks) unter Y 40 – egal wie hell. Grabe "
        "den ganzen Chunk 3 hoch aus (sie brauchen über 2 Blöcke Platz) und mach ihn mit Fackeln hell: Dann spawnen "
        "dort nur noch Schleime. Warte 24–32 Blöcke weg (näher spawnt nichts) und erschlage sie dann.")
TEXTE["xpspawner"].update(
    why="Spawner erzeugen Mobs, solange ein Spieler höchstens 16 Blöcke entfernt ist – aber nicht im Wasser. Darum "
        "liegt das Wasser eine Ebene unter dem Spawner: Die Mobs spawnen darüber, fallen hinein und werden unter dem "
        "Spawner durch zur Rinne und durch die Tür in eine Zelle geschoben (ein Schild hält das Wasser). Du stehst "
        "eine Ebene tiefer und triffst ihre Beine durch einen Spalt; die Beute fällt in die Truhe neben dir.",
    help=[["Spawner spawnt nicht", "Höchstens 16 Blöcke entfernt bleiben; keine Fackeln im Raum."],
          ["Baby-Zombie kommt heraus", "Babys passen durch den Spalt – einfach erschlagen."]])
TEXTE["handel"].update(
    why="Jeder Dorfbewohner steht in einer 1 × 1-Zelle direkt vor seinem Arbeitsblock (dort füllt er bis zu 2-mal am "
        "Tag seine Angebote auf). Vorne ist unten ein Block und auf Höhe 2 ein Block, dazwischen ein Fenster: Du "
        "handelst ganz normal, er kommt nicht heraus. Ein Pfeilmacher kauft z. B. 32 Stöcke für 1 Smaragd.")
TEXTE["honig"].update(
    why="Ein Spender mit Schere zeigt seitlich auf das Bienennest. Zwei Beobachter geben einen dauernden Takt: der "
        "Spender versucht immer wieder zu scheren. Erst bei vollem Nest (Stufe 5) klappt es – 3 Waben fallen vorne "
        "heraus in den Trichter. Fehlversuche kosten die Schere nichts, und Ernten per Spender macht die Bienen nicht "
        "wütend.")
TEXTE["mobfarm"].update(
    afk="Unten am Schacht (24–32 Blöcke unter dem Raum)",
    why="Monster spawnen bei Licht 0, wenn kein Spieler näher als 24 Blöcke ist – aber nicht im Wasser, und von selbst "
        "laufen sie auch nicht hinein. Darum: dunkler Raum 10 × 10, 2 hoch, Kanäle in Kreuzform 2 tief, oben offene "
        "Falltüren. Die Wegfindung hält sie für Boden, die Monster fallen ins Wasser, das schiebt sie zum trockenen "
        "Loch in der Mitte: 26 Blöcke Fall töten Zombies, Skelette, Creeper und Spinnen. Weiter als 32 Blöcke weg "
        "laufen Monster nicht mehr herum – darum wartest du direkt unten.",
    help=[["Wenig Mobs", "Höhlen in 128 Blöcken ausleuchten – sie konkurrieren. Weit weg von Höhlen bauen."],
          ["Hexen unten", "Hexen haben 26 Leben und überleben den Fall – unten erschlagen."]])
TEXTE["creeper"].update(
    afk="Unten am Schacht (24–32 Blöcke unter dem Raum)",
    why="Wie die Monster-Farm, nur 8 × 8 und mit Falltüren in der oberen Hälfte der zweiten Ebene über dem "
        "Spawnboden: Es bleiben 1,8 Blöcke Platz. Creeper (1,7 hoch) passen hinein, Zombies, Skelette und Hexen (fast "
        "2 hoch) nicht. Spinnen passen auch (Fäden als Beifang).")
TEXTE["eisen"]["help"] = TEXTE["eisen"]["help"] + [
    ["Bei Regen nichts", "Der Tageslichtsensor im Nacht-Modus hält bei Regen die Falltüren offen – nach dem Regen "
                         "geht es weiter."],
    ["Golem steht woanders", "In 16 Blöcken darf kein lebender Golem sein – auch keiner, der auf einem Dach "
                             "oder Hügel in der Nähe gespawnt ist. Flächen bis 8 Blöcke um die Dorfbewohner aus "
                             "Glas oder weit genug weg."]]
