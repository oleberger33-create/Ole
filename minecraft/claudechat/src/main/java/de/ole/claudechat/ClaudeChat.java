package de.ole.claudechat;

import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.brigadier.context.CommandContext;
import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.command.v2.CommandRegistrationCallback;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents;
import net.fabricmc.fabric.api.message.v1.ServerMessageEvents;
import net.fabricmc.loader.api.FabricLoader;
import net.minecraft.ChatFormatting;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.BiConsumer;

/**
 * Claude im Minecraft-Chat: „@claude Frage“ im Chat (Antwort sehen alle) oder „/claude Frage“ (Antwort nur für
 * dich). „/claude vergessen“ startet ein neues Gespräch, „/claude status“ zeigt den Verbrauch,
 * „/claude laden“ liest die Einstellungen neu.
 */
public final class ClaudeChat implements ModInitializer {
    public static final Logger LOG = LoggerFactory.getLogger("claudechat");
    private static final boolean TEST = Boolean.getBoolean("claudechat.test");

    private static final ExecutorService ARBEITER = Executors.newFixedThreadPool(2, r -> {
        Thread t = new Thread(r, "Claude-Chat");
        t.setDaemon(true);
        return t;
    });

    private static final UUID KONSOLE = new UUID(0L, 0L);

    private volatile Einstellungen einstellungen;
    private volatile ClaudeFragen claude;
    private volatile MinecraftServer server;

    private final Map<UUID, List<ClaudeFragen.Runde>> verlauf = new ConcurrentHashMap<>();
    private final Map<UUID, Long> zuletzt = new ConcurrentHashMap<>();
    private final Map<UUID, Deque<Long>> fragenZeiten = new ConcurrentHashMap<>();
    private final Map<UUID, Boolean> beschaeftigt = new ConcurrentHashMap<>();
    private final AtomicLong fragen = new AtomicLong(), eingabe = new AtomicLong(), ausgabe = new AtomicLong(),
            cache = new AtomicLong(), suchen = new AtomicLong();

    @Override
    public void onInitialize() {
        laden();
        ServerLifecycleEvents.SERVER_STARTED.register(s -> server = s);
        ServerLifecycleEvents.SERVER_STOPPING.register(s -> {
            ARBEITER.shutdownNow();
            ClaudeFragen c = claude;
            if (c != null) {
                c.schliessen();
            }
        });
        ServerMessageEvents.CHAT_MESSAGE.register((nachricht, spieler, art) -> imChat(spieler, nachricht.signedContent()));
        CommandRegistrationCallback.EVENT.register((dispatcher, registries, umgebung) -> dispatcher.register(
                Commands.literal("claude")
                        .then(Commands.literal("vergessen").executes(this::vergessen))
                        .then(Commands.literal("status").executes(this::status))
                        .then(Commands.literal("laden").executes(this::neuLaden))
                        .then(Commands.argument("frage", StringArgumentType.greedyString()).executes(this::befehl))
                        .executes(this::hilfe)));
        if (TEST) {
            // Nur für den Testserver (Fake-Spieler können nicht chatten): „/claudetest <Chatzeile>“ wie eine Chatnachricht.
            CommandRegistrationCallback.EVENT.register((dispatcher, registries, umgebung) -> dispatcher.register(
                    Commands.literal("claudetest").then(Commands.argument("zeile", StringArgumentType.greedyString())
                            .executes(ctx -> {
                                ServerPlayer p = ctx.getSource().getPlayer();
                                if (p != null) {
                                    imChat(p, StringArgumentType.getString(ctx, "zeile"));
                                }
                                return 1;
                            }))));
        }
    }

    /** Einstellungen (neu) laden; gibt eine Meldung für den Aufrufer zurück. */
    private String laden() {
        try {
            Einstellungen neu = Einstellungen.laden(FabricLoader.getInstance().getConfigDir());
            ClaudeFragen alt = claude;
            claude = new ClaudeFragen(neu);
            einstellungen = neu;
            if (alt != null) {
                alt.schliessen();
            }
            String wer = neu.spieler.isEmpty() ? "alle Spieler" : neu.spielerText;
            if (!neu.eingerichtet()) {
                LOG.warn("Claude-Chat: kein API-Schlüssel – bitte in config/{} eintragen und /claude laden", Einstellungen.DATEI);
                return "Einstellungen geladen, aber der API-Schlüssel fehlt noch (config/" + Einstellungen.DATEI + ").";
            }
            LOG.info("Claude-Chat bereit: Modell {}, Aufwand {}, für {}", neu.modell, neu.aufwand, wer);
            return "Einstellungen geladen: Modell " + neu.modell + ", für " + wer + ".";
        } catch (Exception ex) {
            LOG.error("Claude-Chat: Einstellungen konnten nicht geladen werden", ex);
            return "Einstellungen konnten nicht geladen werden: " + ex.getMessage();
        }
    }

    // ---------------------------------------------------------------- Chat und Befehle

    private void imChat(ServerPlayer spieler, String text) {
        Einstellungen e = einstellungen;
        if (e == null) {
            return;
        }
        String klein = text.toLowerCase(Locale.ROOT);
        for (String praefix : e.praefixe) {
            if (klein.startsWith(praefix)) {
                String frage = text.substring(praefix.length()).replaceFirst("^[\\s,:]+", "").strip();
                if (!frage.isEmpty()) {
                    fragen(spieler, frage, true);
                }
                return;
            }
        }
    }

    private int befehl(CommandContext<CommandSourceStack> ctx) {
        ServerPlayer spieler = ctx.getSource().getPlayer();
        String frage = StringArgumentType.getString(ctx, "frage");
        if (spieler == null) {
            return konsole(ctx.getSource(), frage);
        }
        fragen(spieler, frage, false);
        return 1;
    }

    private int hilfe(CommandContext<CommandSourceStack> ctx) {
        Einstellungen e = einstellungen;
        String praefix = e == null ? "@claude" : e.praefixe.get(0);
        ctx.getSource().sendSuccess(() -> marke().append(Component.literal(
                "Schreib „" + praefix + " deine Frage“ in den Chat (alle sehen die Antwort) oder „/claude deine Frage“ "
                        + "(nur du siehst sie). /claude vergessen = neues Gespräch, /claude status = Verbrauch.")
                .withStyle(ChatFormatting.GRAY)), false);
        return 1;
    }

    private int vergessen(CommandContext<CommandSourceStack> ctx) {
        ServerPlayer spieler = ctx.getSource().getPlayer();
        if (spieler != null) {
            verlauf.remove(spieler.getUUID());
        }
        ctx.getSource().sendSuccess(() -> marke().append(Component.literal("Okay, neues Gespräch.")
                .withStyle(ChatFormatting.GRAY)), false);
        return 1;
    }

    private int status(CommandContext<CommandSourceStack> ctx) {
        Einstellungen e = einstellungen;
        String text = String.format(Locale.GERMANY,
                "%s · %s · seit Serverstart %d Fragen, %,d Eingabe-Token (%,d aus dem Cache), %,d Ausgabe-Token, %d Websuchen",
                e == null ? "?" : e.modell, e != null && e.eingerichtet() ? "Schlüssel ist eingetragen" : "API-Schlüssel fehlt",
                fragen.get(), eingabe.get() + cache.get(), cache.get(), ausgabe.get(), suchen.get());
        ctx.getSource().sendSuccess(() -> marke().append(Component.literal(text).withStyle(ChatFormatting.GRAY)), false);
        return 1;
    }

    private int neuLaden(CommandContext<CommandSourceStack> ctx) {
        ServerPlayer spieler = ctx.getSource().getPlayer();
        Einstellungen e = einstellungen;
        if (spieler != null && e != null && !e.darf(spieler.getName().getString())) {
            ctx.getSource().sendFailure(Component.literal("Das dürfen nur die freigeschalteten Spieler."));
            return 0;
        }
        String meldung = laden();
        ctx.getSource().sendSuccess(() -> marke().append(Component.literal(meldung).withStyle(ChatFormatting.GRAY)), true);
        return 1;
    }

    // ---------------------------------------------------------------- Frage stellen

    private void fragen(ServerPlayer spieler, String frage, boolean oeffentlich) {
        Einstellungen e = einstellungen;
        ClaudeFragen c = claude;
        MinecraftServer s = spieler.level().getServer();
        String name = spieler.getName().getString();
        UUID id = spieler.getUUID();
        if (e == null || c == null) {
            return;
        }
        if (!e.darf(name)) {
            privat(spieler, "Claude ist auf diesem Server nur für " + e.spielerText + " freigeschaltet.");
            return;
        }
        if (!e.eingerichtet()) {
            privat(spieler, "Claude ist noch nicht eingerichtet: Der API-Schlüssel fehlt (config/" + Einstellungen.DATEI + ").");
            return;
        }
        if (beschaeftigt.putIfAbsent(id, Boolean.TRUE) != null) {
            privat(spieler, "Moment, ich denke noch über deine letzte Frage nach …");
            return;
        }
        long jetzt = System.currentTimeMillis();
        Deque<Long> zeiten = fragenZeiten.computeIfAbsent(id, k -> new ArrayDeque<>());
        synchronized (zeiten) {
            while (!zeiten.isEmpty() && jetzt - zeiten.peekFirst() > 3_600_000L) {
                zeiten.pollFirst();
            }
            if (zeiten.size() >= e.maxProStunde) {
                beschaeftigt.remove(id);
                privat(spieler, "Du hast diese Stunde schon " + e.maxProStunde + " Fragen gestellt – bitte später weiter.");
                return;
            }
            zeiten.addLast(jetzt);
        }
        String mitInfo = spielInfo(spieler) + "\n" + frage;
        spieler.sendSystemMessage(Component.literal("Claude denkt nach …").withStyle(ChatFormatting.DARK_GRAY, ChatFormatting.ITALIC), true);
        LOG.info("Claude-Frage von {} ({} Zeichen, {})", name, frage.length(), oeffentlich ? "Chat" : "privat");
        stellen(s, name, id, mitInfo, e, c, (zeilen, ok) -> {
            ServerPlayer jetztDa = s.getPlayerList().getPlayer(id);
            if (oeffentlich && ok) {
                for (Component z : zeilen) {
                    s.getPlayerList().broadcastSystemMessage(z, false);
                }
            } else if (jetztDa != null) {
                for (Component z : zeilen) {
                    an(jetztDa, z);
                }
            }
        });
    }

    /** Frage von der Server-Konsole (z. B. Nitrado-Webkonsole): Antwort steht im Server-Log. */
    private int konsole(CommandSourceStack quelle, String frage) {
        Einstellungen e = einstellungen;
        ClaudeFragen c = claude;
        MinecraftServer s = quelle.getServer();
        if (e == null || c == null || !e.eingerichtet()) {
            quelle.sendFailure(Component.literal("Claude ist noch nicht eingerichtet: Der API-Schlüssel fehlt (config/" + Einstellungen.DATEI + ")."));
            return 0;
        }
        if (beschaeftigt.putIfAbsent(KONSOLE, Boolean.TRUE) != null) {
            quelle.sendFailure(Component.literal("Claude beantwortet gerade noch die letzte Konsolen-Frage."));
            return 0;
        }
        LOG.info("Claude-Frage von der Konsole ({} Zeichen)", frage.length());
        stellen(s, "Konsole", KONSOLE, "[Spiel-Info: Frage von der Server-Konsole]\n" + frage, e, c,
                (zeilen, ok) -> zeilen.forEach(s::sendSystemMessage));
        return 1;
    }

    /** Frage im Hintergrund stellen; die Antwortzeilen kommen auf dem Server-Thread bei „zustellen“ an. */
    private void stellen(MinecraftServer s, String name, UUID id, String mitInfo, Einstellungen e, ClaudeFragen c,
                         BiConsumer<List<Component>, Boolean> zustellen) {
        long jetzt = System.currentTimeMillis();
        Long vorher = zuletzt.put(id, jetzt);
        if (vorher != null && jetzt - vorher > e.vergessenNachMinuten * 60_000L) {
            verlauf.remove(id);
        }
        List<ClaudeFragen.Runde> bisher = new ArrayList<>(verlauf.getOrDefault(id, List.of()));
        ARBEITER.execute(() -> {
            ClaudeFragen.Antwort a;
            try {
                a = c.frage(bisher, mitInfo);
            } catch (Exception ex) {
                LOG.error("Claude-Chat: unerwarteter Fehler", ex);
                a = new ClaudeFragen.Antwort("Da ist etwas schiefgegangen – bitte nochmal versuchen.", false, 0, 0, 0, 0);
            }
            ClaudeFragen.Antwort antwort = a;
            fragen.incrementAndGet();
            eingabe.addAndGet(antwort.eingabe());
            ausgabe.addAndGet(antwort.ausgabe());
            cache.addAndGet(antwort.cacheGelesen());
            suchen.addAndGet(antwort.suchen());
            LOG.info("Claude-Antwort an {}: {} Zeichen, Token ein {} (+{} Cache) / aus {}, {} Websuchen",
                    name, antwort.text().length(), antwort.eingabe(), antwort.cacheGelesen(), antwort.ausgabe(), antwort.suchen());
            s.execute(() -> {
                beschaeftigt.remove(id);
                if (antwort.ok()) {
                    bisher.add(new ClaudeFragen.Runde(mitInfo, antwort.text()));
                    verlauf.put(id, ClaudeFragen.kuerzen(bisher, e.verlaufRunden));
                }
                zustellen.accept(zeilen(antwort.text(), antwort.ok()), antwort.ok());
            });
        });
    }

    /** Kurze Spiel-Info vor jeder Frage, damit Claude weiß, wo der Spieler gerade ist. */
    private static String spielInfo(ServerPlayer spieler) {
        ServerLevel welt = spieler.level();
        BlockPos pos = spieler.blockPosition();
        String biom = welt.getBiome(pos).unwrapKey().map(k -> k.identifier().toString()).orElse("?");
        return "[Spiel-Info: Spieler " + spieler.getName().getString()
                + ", Dimension " + welt.dimension().identifier()
                + ", Position " + pos.getX() + " " + pos.getY() + " " + pos.getZ()
                + ", Biom " + biom
                + ", " + (welt.isBrightOutside() ? "Tag" : "Nacht")
                + (welt.isThundering() ? ", Gewitter" : welt.isRaining() ? ", Regen" : "") + "]";
    }

    // ---------------------------------------------------------------- Ausgabe

    private static MutableComponent marke() {
        return Component.literal("[Claude] ").withStyle(ChatFormatting.GOLD);
    }

    private static void privat(ServerPlayer spieler, String text) {
        an(spieler, marke().append(Component.literal(text).withStyle(ChatFormatting.GRAY)));
    }

    private static void an(ServerPlayer spieler, Component z) {
        spieler.sendSystemMessage(z);
        if (TEST) {
            LOG.info("an {}: {}", spieler.getName().getString(), z.getString());
        }
    }

    /** Antwort in Chatzeilen: Markdown entfernen (der Chat zeigt es nicht), eine Zeile pro Absatz. */
    static List<Component> zeilen(String text, boolean ok) {
        List<Component> aus = new ArrayList<>();
        boolean erste = true;
        for (String roh : text.split("\n")) {
            String z = roh.strip()
                    .replaceAll("\\*\\*|__|`", "")
                    .replaceFirst("^#{1,6}\\s*", "")
                    .replaceFirst("^[-*]\\s+", "• ");
            if (z.isEmpty() || z.matches("^-{3,}$")) {
                continue;
            }
            MutableComponent zeile = erste ? marke() : Component.literal("  ");
            zeile.append(Component.literal(z).withStyle(ok ? ChatFormatting.WHITE : ChatFormatting.GRAY));
            aus.add(zeile);
            erste = false;
            if (aus.size() >= 20) {
                break;
            }
        }
        return aus;
    }
}
