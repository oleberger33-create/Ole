# Claude-Chat

Ein kleiner Server-Mod für den OLE-SMP-Server (Minecraft Java 26.3, Fabric). Mit ihm kann man im Spielchat
Claude fragen. Die Spieler installieren nichts.

## Im Spiel

- **`@claude deine Frage`** im normalen Chat (oder `!claude …`): Alle sehen Frage und Antwort.
- **`/claude deine Frage`**: Nur du siehst die Antwort.
- **`/claude vergessen`**: neues Gespräch (Claude merkt sich sonst die letzten 8 Fragen pro Spieler; nach
  30 Minuten Pause beginnt automatisch ein neues).
- **`/claude status`**: Modell, ob der Schlüssel eingetragen ist, Fragen und Token seit dem Serverstart.
- **`/claude laden`**: Einstellungen neu lesen (nach einer Änderung an der Datei).
- **Server-Konsole** (z. B. Nitrado-Webkonsole): `claude deine Frage`; die Antwort steht im Server-Log.

Claude weiß bei jeder Frage, wer fragt, in welcher Dimension, wo (Koordinaten, Biom), ob Tag oder Nacht ist und
welches Wetter herrscht. Wenn es unsicher ist, schaut es im Minecraft Wiki oder auf Modrinth nach (Websuche).
Antworten kommen als reiner Text ohne Markdown, eine Chatzeile pro Absatz. Im Spiel tun kann Claude nichts: keine
Befehle, keine Blöcke, keine Gegenstände.

## Einrichten

1. Einen API-Schlüssel auf <https://platform.claude.com> anlegen (Settings → API Keys). Das Konto braucht
   Guthaben, denn jede Frage kostet ein paar Cent.
2. Auf dem Server die Datei `config/claudechat.properties` öffnen (bei Nitrado: Dateibrowser) und hinter
   `api_schluessel=` den Schlüssel eintragen. **Den Schlüssel nie in den Chat schreiben.**
3. Im Spiel `/claude laden` eingeben (oder `claude laden` in der Konsole). Danach antwortet Claude.

Weitere Einstellungen in derselben Datei:

| Einstellung | Bedeutung | Standard |
|---|---|---|
| `spieler` | wer fragen darf (leer = alle) | `FNGreg,korokchris` |
| `praefix` | so beginnt eine Frage im Chat | `@claude,!claude` |
| `modell`, `aufwand` | Modell und Denk-Aufwand (`low` antwortet am schnellsten) | `claude-opus-5-5`, `low` |
| `web_suche`, `web_seiten` | Websuche erlaubt und wo | `true`, `minecraft.wiki,modrinth.com` |
| `max_fragen_pro_stunde` | Kostenbremse pro Spieler | `40` |
| `verlauf_runden`, `vergessen_nach_minuten` | Gedächtnis | `8`, `30` |

Was Claude über den Server weiß und wie es antworten soll, steht in `config/claudechat_anweisungen.txt`. Du kannst
die Datei frei ändern und danach `/claude laden` eingeben.

## Technik

- `ClaudeFragen.java` stellt die Frage über das Anthropic Java SDK (Beta-Messages-Endpunkt). Das passiert mit
  adaptivem Denken, `effort` aus den Einstellungen und der Websuche `web_search_20260209` mit höchstens 3 Suchen.
  Weil `fallbacks: "default"` gesetzt ist, beantwortet ein Ersatzmodell die Frage, wenn die Sicherheitsfilter sie
  ablehnen. Bei `pause_turn` (Websuche läuft noch) geht die Antwort unverändert zurück und es wird weitergemacht.
  Bei `refusal` kommt ein freundlicher Hinweis.
- Gesprächsverlauf: Pro Spieler werden nur Frage und Antworttext aufbewahrt. Denk-Blöcke und Websuch-Ergebnisse
  früherer Runden werden nicht wieder mitgeschickt. So bleiben Folgefragen klein, und die API erlaubt es, alle
  Denk-Blöcke wegzulassen. Der Verlauf wird ganz am Ende zwischengespeichert (`cache_control`).
- `ClaudeChat.java` ist der Fabric-Teil. Er hört über Fabric API (`ServerMessageEvents.CHAT_MESSAGE`) auf den
  Chat, stellt den Befehl `/claude` bereit und fragt im Hintergrund. Antworten gehen über den Server-Thread in den
  Chat. Erlaubte Spieler, eine Frage gleichzeitig pro Spieler und die Kostenbremse werden hier geprüft.
- Abhängigkeiten: Fabric API und Fabric Language Kotlin. Beide sind auf dem Server installiert; Kotlin braucht das
  SDK. Das SDK mit OkHttp und Jackson ist als Jar-in-Jar eingebettet (`include`), darum ist die Jar groß (~43 MB).

Bauen (JDK 25): `./gradlew build` → `build/libs/claudechat-1.0.0.jar`, kommt in den `mods`-Ordner des Servers.

Getestet auf einem lokalen 26.3-Server mit genau den 38 Mods vom Nitrado-Server (Fabric Loader 0.19.5) und einer
nachgebauten Claude API. Geprüft wurden die Anfrage (Modell, Beta-Header, `fallbacks`, Websuche, Verlauf) und
diese Fälle:

- Chat- und Befehlsfrage, Folgefrage mit Verlauf
- Websuche mit `pause_turn`, Ablehnung, falscher Schlüssel, keine Verbindung
- zwei Fragen gleichzeitig, fremder Spieler, Kostenbremse
- Konsole und alle Unterbefehle

Fake-Spieler können nicht chatten. Darum gibt es mit `-Dclaudechat.test=true` den Testbefehl
`/claudetest <Chatzeile>`, der eine Chatzeile nachspielt.
