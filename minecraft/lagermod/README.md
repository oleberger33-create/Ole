# Lager (Fabric, nur Server)

Gemeinsames Kisten-Lager für den Server. Spieler brauchen keinen Mod: alles läuft über normale Kisten-Menüs.

- `/lager item`: Lager-Terminal holen (Bergungskompass mit Glanz)
- **Rechtsklick** mit dem Terminal: Lager öffnen. Zeigt alle Items aus allen verbundenen Kisten und Fässern zusammen.
  - Links-Klick: Stapel nehmen · Rechts-Klick: 1 Stück · Shift-Klick: Stapel ins Inventar · Zahl-Taste: in den Hotbar-Platz
  - Item in der Hand auf ein Feld klicken oder Shift-Klick im eigenen Inventar: ins Lager legen
  - Unten: Seiten blättern, nach Menge/Name sortieren, Suche aufheben
- **Schleichen + Rechtsklick** mit dem Terminal auf eine Kiste oder ein Fass: verbinden (für alle) → privat → trennen.
  Doppelkisten zählen als eine. Nur wer die Kiste verbunden hat (oder ein Op), kann sie umschalten.
- **Private Kisten** sieht im Lager nur der Besitzer. Andere können sie nicht öffnen und nicht abbauen
  (Ops schon). Trichter können trotzdem daraus ziehen.
- `/lager suche <Text>`: nur passende Items zeigen · `/lager liste`: Anzahl deiner Kisten
- `/lager scan <Radius>` (Op): alle Kisten und Fässer im Umkreis als geteilt verbinden

Daten: `lager.json` im Weltordner. Kisten in nicht geladenen Chunks werden beim Öffnen kurz geladen.

Bauen: `JAVA_HOME=<JDK 25> ./gradlew build` → `build/libs/lager-<version>.jar` in den `mods`-Ordner.
