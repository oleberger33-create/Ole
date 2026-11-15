# TPA (Fabric, nur Server)

Teleport-Anfragen zwischen Spielern, ohne Client-Mod.

- `/tpa <Spieler>`: Anfrage, dich zu ihm zu teleportieren
- `/tpahere <Spieler>`: Anfrage, dass er zu dir kommt
- `/tpaccept [Spieler]`, `/tpdeny [Spieler]`: annehmen/ablehnen (oder die Knöpfe im Chat anklicken)
- `/tpacancel`: eigene Anfrage zurückziehen

Anfragen gelten 60 Sekunden, zwischen zwei Anfragen 10 Sekunden Pause. Nach dem Annehmen 3 Sekunden stillstehen,
dann Teleport, auch in Nether und End.
