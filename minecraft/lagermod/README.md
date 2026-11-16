# Lager (Fabric, nur Server)

Gemeinsames Kisten-Lager für den Server. Spieler brauchen keinen Mod: alles läuft über normale Kisten-Menüs.

- `/lager item`: Lager-Terminal holen (Bergungskompass mit Glanz)
- **Ordner** oben (wie die Kreativ-Reiter): Alles, Baublöcke, Natur, Funktionsblöcke, Redstone, Werkzeuge, Kampf, Essen, Rohstoffe.
  Sortierung standardmäßig nach Name, damit nichts herumspringt; „Inventar einlagern“ räumt das Inventar (ohne Schnellleiste) ins Lager.
- **Rechtsklick** mit dem Terminal: Lager-Terminal öffnen (wie das Crafting-Terminal aus Applied Energistics 2).
  Links alle Items aus allen verbundenen Kisten und Fässern zusammen, über den Knopf „Werkbank öffnen“ ein 3×3-Werkbank-Raster.
  - Links-Klick: Stapel nehmen · Rechts-Klick: 1 Stück · Shift-Klick: Stapel ins Inventar · Zahl-Taste: in den Hotbar-Platz
  - Item in der Hand auf ein Feld klicken oder Shift-Klick im eigenen Inventar: ins Lager legen
  - Werkbank: Zutaten aus dem Lager ins Raster legen, Ergebnis anklicken (1×) oder Shift-Klick (ein Stapel).
    Verbrauchte Zutaten füllen sich automatisch aus dem Lager nach; Reste wie leere Eimer gehen ins Lager.
    Beim Schließen wandert alles aus dem Raster zurück ins Lager.
  - Unten: Seiten blättern, nach Menge/Name sortieren, Suche aufheben
- **Schleichen + Rechtsklick** mit dem Terminal auf eine Kiste oder ein Fass: verbinden (für alle) → privat → trennen.
  Doppelkisten zählen als eine. Nur wer die Kiste verbunden hat (oder ein Op), kann sie umschalten.
- **Private Kisten** sieht im Lager nur der Besitzer. Andere können sie nicht öffnen und nicht abbauen
  (Ops schon). Trichter können trotzdem daraus ziehen.
- `/lager herstellen <Item> [Anzahl]`: stellt mit Werkbank-Rezepten aus dem Lager her. Fehlende Zutaten werden
  selbst hergestellt, bis 4 Stufen tief (z. B. Truhe ← Bretter ← Stamm). Ergebnis ins Inventar, Zwischenprodukte ins Lager.
- `/lager suche <Text>`: nur passende Items zeigen · `/lager liste`: Anzahl deiner Kisten
- `/lager scan <Radius>` (Op): alle Kisten und Fässer im Umkreis als geteilt verbinden

**Tresor**: jeder Spieler bekommt beim Betreten ein Tresor-Item (Shulkerschale). Rechtsklick öffnet den persönlichen
Speicher (3 Seiten × 54 Plätze, schleichend = nächste Seite, oder `/tresor [1-3]`). Gespeichert direkt auf dem Server in
`welt/tresor/<uuid>.json` (mit `.bak`), unabhängig von Kisten und Chunks.

Protokoll: jedes Ein- und Auslagern im Lager steht in `welt/lager_protokoll.log`.

Daten: `lager.json` im Weltordner. Kisten in nicht geladenen Chunks werden beim Öffnen kurz geladen.

Bauen: `JAVA_HOME=<JDK 25> ./gradlew build` → `build/libs/lager-<version>.jar` in den `mods`-Ordner.
