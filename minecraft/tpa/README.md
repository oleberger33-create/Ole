# TPA (Fabric, nur Server)

Teleport-Anfragen zwischen Spielern, ohne Client-Mod.

- `/tpa <Spieler>`: Anfrage, dich zu ihm zu teleportieren
- `/tpahere <Spieler>`: Anfrage, dass er zu dir kommt
- `/tpaccept [Spieler]`, `/tpdeny [Spieler]`: annehmen/ablehnen (oder die Knöpfe im Chat anklicken)
- `/tpacancel`: eigene Anfrage zurückziehen
- `/tpmenu`: Teleport-Menü als Kiste. Bedrock-Spieler (Name beginnt mit `.`) bekommen es automatisch, wenn sie das
  Teleport-Buch benutzen, weil Bedrock keine Links in Büchern kann. Ziele stehen in `tpmenu.json` im Weltordner.

Anfragen gelten 60 Sekunden, zwischen zwei Anfragen 10 Sekunden Pause. Nach dem Annehmen 3 Sekunden stillstehen,
dann Teleport, auch in Nether und End.

## Bedrock

Mit Floodgate bekommen Bedrock-Spieler Fenster statt Chat-Links: `/menu` (Teleport-Ziele, TPA mit Spielerliste, Lager,
Tresor), Teleport-Anfragen als Fenster mit Annehmen/Ablehnen. `libs/` enthält nur die Floodgate-/Cumulus-API zum
Kompilieren (MIT-Lizenz, GeyserMC).
- Anklickbare Chat-Nachrichten (auch /tellraw aus Datapacks, z. B. Farmhelper) erscheinen für Bedrock-Spieler zusätzlich
  als Fenster mit Knöpfen; Farmhelper-Geisterblöcke (block_display) als schwebende fallende Blöcke nur für sie, weil Geyser block_display nicht anzeigt.
