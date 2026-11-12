package de.ole.claudechat;

import com.anthropic.client.AnthropicClient;
import com.anthropic.client.okhttp.AnthropicOkHttpClient;
import com.anthropic.errors.AnthropicIoException;
import com.anthropic.errors.AnthropicServiceException;
import com.anthropic.errors.UnauthorizedException;
import com.anthropic.errors.PermissionDeniedException;
import com.anthropic.errors.RateLimitException;
import com.anthropic.models.beta.messages.BetaCacheControlEphemeral;
import com.anthropic.models.beta.messages.BetaContentBlock;
import com.anthropic.models.beta.messages.BetaMessage;
import com.anthropic.models.beta.messages.BetaOutputConfig;
import com.anthropic.models.beta.messages.BetaStopReason;
import com.anthropic.models.beta.messages.BetaWebSearchTool20260209;
import com.anthropic.models.beta.messages.MessageCreateParams;

import java.time.Duration;
import java.util.ArrayList;
import java.util.List;

/**
 * Stellt Claude eine Frage über die Claude API (Anthropic Java SDK) – ohne Minecraft-Abhängigkeiten.
 *
 * Verlauf: pro Spieler nur Text (Frage + Antwort). Denk-Blöcke und Websuch-Ergebnisse früherer Runden werden
 * nicht wieder mitgeschickt – das hält Anfragen klein (Websuch-Ergebnisse sind groß) und ist für die API erlaubt
 * (alle Denk-Blöcke wegzulassen verändert keinen geprüften Verlauf). Innerhalb einer Runde (pause_turn bei
 * der Websuche) geht die Antwort unverändert zurück.
 */
public final class ClaudeFragen {
    /** Ergebnis einer Frage: Antworttext (oder Fehlermeldung für den Spieler) und Verbrauch. */
    public record Antwort(String text, boolean ok, long eingabe, long ausgabe, long cacheGelesen, int suchen) {}

    /** Ein Eintrag im Gesprächsverlauf. */
    public record Runde(String frage, String antwort) {}

    private final Einstellungen e;
    private final AnthropicClient client;

    public ClaudeFragen(Einstellungen e) {
        this.e = e;
        AnthropicOkHttpClient.Builder b = AnthropicOkHttpClient.builder()
                .apiKey(e.eingerichtet() ? e.apiSchluessel : "fehlt")
                .timeout(Duration.ofSeconds(120))
                .maxRetries(2);
        if (!e.basisUrl.isEmpty()) {
            b.baseUrl(e.basisUrl);
        }
        this.client = b.build();
    }

    public void schliessen() {
        client.close();
    }

    public Antwort frage(List<Runde> verlauf, String frage) {
        MessageCreateParams.Builder p = MessageCreateParams.builder()
                .model(e.modell)
                .maxTokens(e.maxTokens)
                .system(e.anweisungen)
                // Bei einer Ablehnung durch die Sicherheitsfilter beantwortet ein Ersatzmodell die Frage.
                .addBeta("server-side-fallback-2026-07-01")
                .fallbacksDefault()
                // Verlauf zwischenspeichern: Folgefragen lesen den gleichen Anfang günstig aus dem Cache.
                .cacheControl(BetaCacheControlEphemeral.builder().build())
                .outputConfig(BetaOutputConfig.builder().effort(BetaOutputConfig.Effort.of(e.aufwand)).build());
        if (e.webSuche) {
            BetaWebSearchTool20260209.Builder w = BetaWebSearchTool20260209.builder().maxUses(3L);
            if (!e.webSeiten.isEmpty()) {
                w.allowedDomains(e.webSeiten);
            }
            p.addTool(w.build());
        }
        for (Runde r : verlauf) {
            p.addUserMessage(r.frage());
            p.addAssistantMessage(r.antwort());
        }
        p.addUserMessage(frage);

        StringBuilder text = new StringBuilder();
        long ein = 0, aus = 0, cache = 0;
        int suchen = 0;
        try {
            for (int runde = 0; runde < 4; runde++) {
                BetaMessage m = client.beta().messages().create(p.build());
                ein += m.usage().inputTokens();
                aus += m.usage().outputTokens();
                cache += m.usage().cacheReadInputTokens().orElse(0L);
                for (BetaContentBlock b : m.content()) {
                    b.text().ifPresent(t -> text.append(t.text()));
                    if (b.isServerToolUse()) {
                        suchen++;
                    }
                }
                BetaStopReason grund = m.stopReason().orElse(BetaStopReason.END_TURN);
                if (grund.equals(BetaStopReason.REFUSAL)) {
                    return new Antwort("Dazu kann ich hier leider nichts sagen.", false, ein, aus, cache, suchen);
                }
                if (grund.equals(BetaStopReason.PAUSE_TURN)) {
                    p.addMessage(m.toParam());      // Websuche läuft noch: unverändert zurückgeben und weitermachen
                    continue;
                }
                if (grund.equals(BetaStopReason.MAX_TOKENS)) {
                    text.append(" …");
                }
                break;
            }
        } catch (UnauthorizedException | PermissionDeniedException ex) {
            return fehler("Der API-Schlüssel stimmt nicht (config/" + Einstellungen.DATEI + ").", ein, aus, cache, suchen);
        } catch (RateLimitException ex) {
            return fehler("Gerade zu viele Anfragen – bitte kurz warten.", ein, aus, cache, suchen);
        } catch (AnthropicServiceException ex) {
            ClaudeChat.LOG.warn("Claude API: {} {}", ex.statusCode(), ex.getMessage());
            return fehler("Claude ist gerade nicht erreichbar (Fehler " + ex.statusCode() + ").", ein, aus, cache, suchen);
        } catch (AnthropicIoException ex) {
            ClaudeChat.LOG.warn("Claude API: Verbindung fehlgeschlagen: {}", ex.getMessage());
            return fehler("Keine Verbindung zu Claude – bitte später nochmal.", ein, aus, cache, suchen);
        }
        String t = text.toString().strip();
        if (t.isEmpty()) {
            return fehler("Claude hat nichts geantwortet – frag bitte nochmal anders.", ein, aus, cache, suchen);
        }
        return new Antwort(t, true, ein, aus, cache, suchen);
    }

    private static Antwort fehler(String text, long ein, long aus, long cache, int suchen) {
        return new Antwort(text, false, ein, aus, cache, suchen);
    }

    /** Verlauf kürzen: nur die letzten n Runden behalten (vorne weglassen – es gibt keine Denk-Blöcke darin). */
    public static List<Runde> kuerzen(List<Runde> verlauf, int n) {
        if (verlauf.size() <= n) {
            return verlauf;
        }
        return new ArrayList<>(verlauf.subList(verlauf.size() - n, verlauf.size()));
    }
}
