package de.ole.claudechat;

import java.io.IOException;
import java.io.InputStream;
import java.io.Reader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Properties;

/**
 * Einstellungen aus config/claudechat.properties (wird beim ersten Start mit Erklärungen angelegt) und die
 * Anweisungen an Claude aus config/claudechat_anweisungen.txt (ebenfalls beim ersten Start angelegt).
 */
public final class Einstellungen {
    public static final String DATEI = "claudechat.properties";
    public static final String ANWEISUNGEN = "claudechat_anweisungen.txt";

    public final String apiSchluessel;
    public final List<String> spieler;          // klein geschrieben; leer = alle
    public final String spielerText;            // wie eingetragen, für Meldungen
    public final List<String> praefixe;         // klein geschrieben
    public final String modell;
    public final String aufwand;                // low, medium, high, xhigh, max
    public final long maxTokens;
    public final boolean webSuche;
    public final List<String> webSeiten;
    public final int maxProStunde;
    public final int verlaufRunden;
    public final int vergessenNachMinuten;
    public final String basisUrl;               // nur für Tests, sonst leer
    public final String anweisungen;

    private Einstellungen(Properties p, String anweisungen) {
        String schluessel = p.getProperty("api_schluessel", "").trim();
        if (schluessel.isEmpty()) {
            String env = System.getenv("ANTHROPIC_API_KEY");
            schluessel = env == null ? "" : env.trim();
        }
        this.apiSchluessel = schluessel;
        this.spieler = liste(p.getProperty("spieler", ""));
        this.spielerText = String.join(", ", p.getProperty("spieler", "").trim().split("\\s*,\\s*"));
        List<String> pr = liste(p.getProperty("praefix", "@claude,!claude"));
        this.praefixe = pr.isEmpty() ? List.of("@claude") : pr;
        this.modell = p.getProperty("modell", "claude-opus-5-5").trim();
        this.aufwand = p.getProperty("aufwand", "low").trim().toLowerCase(Locale.ROOT);
        this.maxTokens = zahl(p, "max_tokens", 4000);
        this.webSuche = Boolean.parseBoolean(p.getProperty("web_suche", "true").trim());
        this.webSeiten = liste(p.getProperty("web_seiten", "minecraft.wiki,modrinth.com"));
        this.maxProStunde = (int) zahl(p, "max_fragen_pro_stunde", 40);
        this.verlaufRunden = (int) zahl(p, "verlauf_runden", 8);
        this.vergessenNachMinuten = (int) zahl(p, "vergessen_nach_minuten", 30);
        this.basisUrl = p.getProperty("basis_url", "").trim();
        this.anweisungen = anweisungen;
    }

    public boolean darf(String name) {
        return spieler.isEmpty() || spieler.contains(name.toLowerCase(Locale.ROOT));
    }

    public boolean eingerichtet() {
        return !apiSchluessel.isEmpty() && !apiSchluessel.startsWith("HIER");
    }

    /** Lädt die Einstellungen; legt fehlende Dateien mit Vorlagen an. */
    public static Einstellungen laden(Path ordner) throws IOException {
        Files.createDirectories(ordner);
        Path datei = ordner.resolve(DATEI);
        if (!Files.exists(datei)) {
            vorlage("/claudechat/claudechat.properties", datei);
        }
        Path anw = ordner.resolve(ANWEISUNGEN);
        if (!Files.exists(anw)) {
            vorlage("/claudechat/anweisungen.txt", anw);
        }
        Properties p = new Properties();
        try (Reader r = Files.newBufferedReader(datei, StandardCharsets.UTF_8)) {
            p.load(r);
        }
        return new Einstellungen(p, Files.readString(anw, StandardCharsets.UTF_8).strip());
    }

    private static void vorlage(String quelle, Path ziel) throws IOException {
        try (InputStream in = Einstellungen.class.getResourceAsStream(quelle)) {
            if (in == null) {
                throw new IOException("Vorlage fehlt in der Mod: " + quelle);
            }
            Files.copy(in, ziel);
        }
    }

    private static List<String> liste(String wert) {
        List<String> aus = new ArrayList<>();
        for (String s : wert.split(",")) {
            String t = s.trim().toLowerCase(Locale.ROOT);
            if (!t.isEmpty()) {
                aus.add(t);
            }
        }
        return aus;
    }

    private static long zahl(Properties p, String schluessel, long standard) {
        try {
            return Long.parseLong(p.getProperty(schluessel, String.valueOf(standard)).trim());
        } catch (NumberFormatException e) {
            return standard;
        }
    }
}
