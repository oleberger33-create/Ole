package de.ole.wegpunkte;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.reflect.TypeToken;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.brigadier.context.CommandContext;
import com.mojang.brigadier.suggestion.SuggestionProvider;
import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.command.v2.CommandRegistrationCallback;
import net.fabricmc.fabric.api.entity.event.v1.ServerEntityLevelChangeEvents;
import net.fabricmc.fabric.api.entity.event.v1.ServerPlayerEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerEntityEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.fabricmc.fabric.api.networking.v1.ServerPlayConnectionEvents;
import net.minecraft.ChatFormatting;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Vec3i;
import net.minecraft.network.chat.ClickEvent;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.network.protocol.game.ClientboundTrackedWaypointPacket;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.storage.LevelResource;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.waypoints.Waypoint;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.*;
import java.util.regex.Pattern;

/**
 * Gemeinsame Wegpunkte, nur serverseitig.
 * Jeder Spieler kann mit /wp add <Name> einen Wegpunkt setzen. Alle Spieler in derselben
 * Dimension sehen ihn in der Ortungsleiste (Locator Bar), am Ort schwebt ein Namensschild,
 * und wer einen Kompass hält und in Richtung eines Wegpunkts schaut, sieht Name und Entfernung.
 */
public class Wegpunkte implements ModInitializer {
	static final Logger LOG = LoggerFactory.getLogger("wegpunkte");
	static final int LIMIT = 15;
	static final Pattern NAME = Pattern.compile("[\\p{L}\\p{N} _\\-!?.#&+']{1,24}");
	static final String TAG = "wegpunkt";
	static final String TAG_ID = "wp_";

	/** Farben: Name → RGB und Chatfarbe. */
	enum Farbe {
		rot(0xFF5555, ChatFormatting.RED), orange(0xFFAA00, ChatFormatting.GOLD), gelb(0xFFFF55, ChatFormatting.YELLOW),
		gruen(0x55FF55, ChatFormatting.GREEN), tuerkis(0x55FFFF, ChatFormatting.AQUA), blau(0x5577FF, ChatFormatting.BLUE),
		lila(0xAA55FF, ChatFormatting.DARK_PURPLE), rosa(0xFF77CC, ChatFormatting.LIGHT_PURPLE), weiss(0xFFFFFF, ChatFormatting.WHITE);
		final int rgb; final ChatFormatting chat;
		Farbe(int rgb, ChatFormatting chat) { this.rgb = rgb; this.chat = chat; }
		static Farbe von(String s) {
			if (s == null) return null;
			String n = s.toLowerCase(Locale.ROOT).replace("ü", "ue").replace("ß", "ss").replace("grün", "gruen").replace("türkis", "tuerkis");
			for (Farbe f : values()) if (f.name().equals(n)) return f;
			return null;
		}
	}

	static class Punkt {
		String id, name, besitzer, besitzerUuid, dim, farbe;
		int x, y, z;
		long erstellt;
		UUID uuid() { return UUID.fromString(id); }
		Farbe farbeEnum() { Farbe f = Farbe.von(farbe); return f == null ? Farbe.gelb : f; }
		Vec3 mitte() { return new Vec3(x + 0.5, y + 0.5, z + 0.5); }
	}

	static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();
	static MinecraftServer server;
	static final Map<String, Punkt> punkte = new LinkedHashMap<>(); // id → Punkt
	/** Pro Spieler: welche Wegpunkt-IDs der Client gerade kennt. */
	static final Map<UUID, Set<String>> gesendet = new HashMap<>();
	/** Pro Spieler: beim nächsten Abgleich alles neu schicken (Join, Dimensionswechsel, Respawn). */
	static final Set<UUID> neuSenden = new HashSet<>();
	static final Map<UUID, String> letzteAnzeige = new HashMap<>();
	static int tick;

	@Override
	public void onInitialize() {
		ServerLifecycleEvents.SERVER_STARTED.register(s -> { server = s; laden(); einstellungenLaden(); Schilder.selbsttest(s); });
		ServerLifecycleEvents.SERVER_STOPPING.register(s -> speichern());

		ServerPlayConnectionEvents.JOIN.register((handler, sender, s) -> {
			UUID u = handler.getPlayer().getUUID();
			gesendet.put(u, new HashSet<>());
			neuSenden.add(u);
			Schilder.vergessen(u); Esp.vergessen(u);
		});
		ServerPlayConnectionEvents.DISCONNECT.register((handler, s) -> {
			UUID u = handler.getPlayer().getUUID();
			gesendet.remove(u); neuSenden.remove(u); letzteAnzeige.remove(u); Schilder.vergessen(u); Esp.vergessen(u);
		});
		ServerEntityLevelChangeEvents.AFTER_PLAYER_CHANGE_LEVEL.register((p, von, nach) -> { neuSenden.add(p.getUUID()); Schilder.vergessen(p.getUUID()); Esp.vergessen(p.getUUID()); });
		ServerPlayerEvents.AFTER_RESPAWN.register((alt, neu, ende) -> { neuSenden.add(neu.getUUID()); Schilder.vergessen(neu.getUUID()); Esp.vergessen(neu.getUUID()); });

		// Verwaiste Namensschilder (Wegpunkt wurde gelöscht, während der Chunk nicht geladen war) entfernen
		ServerEntityEvents.ENTITY_LOAD.register((e, welt) -> {
			if (!(e instanceof net.minecraft.world.entity.Display.TextDisplay) || !e.entityTags().contains(TAG)) return;
			for (String t : e.entityTags())
				if (t.startsWith(TAG_ID) && !punkte.containsKey(t.substring(TAG_ID.length()))) { e.discard(); return; }
		});

		ServerTickEvents.END_SERVER_TICK.register(s -> {
			tick++;
			if (tick % 20 == 0) for (ServerPlayer p : s.getPlayerList().getPlayers()) abgleichen(p);
			if (tick % 5 == 0) for (ServerPlayer p : s.getPlayerList().getPlayers()) kompass(p);
			if (tick % 2 == 0) {
				try { Esp.tick(s, tick); } catch (RuntimeException e) { LOG.error("ESP", e); }
			}
			if (tick % 2 == 0) for (ServerPlayer p : s.getPlayerList().getPlayers()) {
				try { Schilder.aktualisieren(p); } catch (RuntimeException e) { LOG.error("Schilder", e); }
			}
		});

		CommandRegistrationCallback.EVENT.register((d, reg, env) -> {
			SuggestionProvider<CommandSourceStack> farben = (c, b) -> { for (Farbe f : Farbe.values()) b.suggest(f.name()); return b.buildFuture(); };
			SuggestionProvider<CommandSourceStack> eigene = (c, b) -> {
				ServerPlayer p = c.getSource().getPlayer();
				boolean op = p != null && istOp(p);
				for (Punkt w : punkte.values())
					if (p != null && (op || w.besitzerUuid.equals(p.getUUID().toString()))) b.suggest(w.name);
				return b.buildFuture();
			};
			// Nach dem Namen eine Farbe vorschlagen: "/wp add Meine Farm " → rot, gelb, ...
			SuggestionProvider<CommandSourceStack> farbeAmEnde = (c, b) -> {
				String rest = b.getRemaining();
				int leer = rest.lastIndexOf(' ');
				if (leer < 0) return b.buildFuture();
				String anfang = rest.substring(0, leer + 1), wort = rest.substring(leer + 1).toLowerCase(Locale.ROOT);
				for (Farbe f : Farbe.values()) if (f.name().startsWith(wort)) b.suggest(anfang + f.name());
				return b.buildFuture();
			};
			SuggestionProvider<CommandSourceStack> alle = (c, b) -> { for (Punkt w : punkte.values()) b.suggest(w.name); return b.buildFuture(); };

			d.register(Commands.literal("esp")
				.executes(c -> espSchalten(c, null))
				.then(Commands.literal("on").executes(c -> espSchalten(c, true)))
				.then(Commands.literal("off").executes(c -> espSchalten(c, false)))
				.then(Commands.literal("an").executes(c -> espSchalten(c, true)))
				.then(Commands.literal("aus").executes(c -> espSchalten(c, false))));

			for (String wurzel : new String[]{"wp", "wegpunkt"}) {
				d.register(Commands.literal(wurzel)
					.executes(Wegpunkte::hilfe)
					.then(Commands.literal("add")
						.then(Commands.argument("name", StringArgumentType.greedyString()).suggests(farbeAmEnde).executes(Wegpunkte::hinzufuegen)))
					.then(Commands.literal("liste").executes(Wegpunkte::liste))
					.then(Commands.literal("list").executes(Wegpunkte::liste))
					.then(Commands.literal("entfernen")
						.then(Commands.argument("name", StringArgumentType.greedyString()).suggests(eigene).executes(Wegpunkte::entfernen)))
					.then(Commands.literal("remove")
						.then(Commands.argument("name", StringArgumentType.greedyString()).suggests(eigene).executes(Wegpunkte::entfernen)))
					.then(Commands.literal("farbe")
						.then(Commands.argument("farbe", StringArgumentType.word()).suggests(farben)
							.then(Commands.argument("name", StringArgumentType.greedyString()).suggests(eigene).executes(Wegpunkte::farbeAendern))))
					.then(Commands.literal("schilder")
						.then(Commands.literal("an").executes(c -> schilderSchalten(c, true)))
						.then(Commands.literal("aus").executes(c -> schilderSchalten(c, false))))
					.then(Commands.literal("groesse")
						.executes(c -> { c.getSource().sendSuccess(() -> Component.literal("◆ Schildgröße: " + Schilder.faktor
							+ " (Standard 0.022, kleiner = kleiner)").withStyle(ChatFormatting.GRAY), false); return 1; })
						.then(Commands.argument("wert", com.mojang.brigadier.arguments.DoubleArgumentType.doubleArg(0.005, 0.2))
							.executes(Wegpunkte::groesseSetzen)))
					.then(Commands.literal("info")
						.then(Commands.argument("name", StringArgumentType.greedyString()).suggests(alle).executes(Wegpunkte::info)))
				);
			}
		});
	}

	// ---------- Befehle ----------

	static int hilfe(CommandContext<CommandSourceStack> c) {
		c.getSource().sendSuccess(() -> Component.literal("")
			.append(Component.literal("◆ Wegpunkte\n").withStyle(ChatFormatting.GOLD, ChatFormatting.BOLD))
			.append(befehl("/wp add <Name> [Farbe]", "/wp add ", " – Wegpunkt hier setzen\n"))
			.append(befehl("/wp liste", "/wp liste", " – alle Wegpunkte\n"))
			.append(befehl("/wp entfernen <Name>", "/wp entfernen ", " – eigenen Wegpunkt löschen\n"))
			.append(befehl("/wp farbe <Farbe> <Name>", "/wp farbe ", " – Farbe ändern\n"))
			.append(befehl("/wp schilder an|aus", "/wp schilder ", " – Namensschilder ein-/ausblenden\n"))
			.append(Component.literal("Beispiel: /wp add Meine Farm blau. Farben: rot orange gelb gruen tuerkis blau lila rosa weiss.\n").withStyle(ChatFormatting.GRAY))
			.append(Component.literal("Tipp: Mit einem Kompass in der Hand siehst du den Namen des Wegpunkts, auf den du schaust.").withStyle(ChatFormatting.GRAY)), false);
		return 1;
	}

	static MutableComponent befehl(String text, String vorschlag, String erklaerung) {
		return Component.literal(text).withStyle(s -> s.withColor(ChatFormatting.YELLOW).withClickEvent(new ClickEvent.SuggestCommand(vorschlag)))
			.append(Component.literal(erklaerung).withStyle(ChatFormatting.GRAY));
	}

	static int hinzufuegen(CommandContext<CommandSourceStack> c) {
		ServerPlayer p = c.getSource().getPlayer();
		if (p == null) { fehler(c, "Nur Spieler können Wegpunkte setzen."); return 0; }
		String name = StringArgumentType.getString(c, "name").trim().replaceAll("\\s+", " ");
		// Letztes Wort eine Farbe? "/wp add Meine Farm blau"
		String farbeText = null;
		int leer = name.lastIndexOf(' ');
		if (leer > 0 && Farbe.von(name.substring(leer + 1)) != null) { farbeText = name.substring(leer + 1); name = name.substring(0, leer); }
		if (!NAME.matcher(name).matches()) { fehler(c, "Name: 1–24 Zeichen, nur Buchstaben, Zahlen, Leerzeichen und - _ ! ? . # & + '"); return 0; }
		if (finde(name) != null) { fehler(c, "Es gibt schon einen Wegpunkt namens \"" + name + "\"."); return 0; }
		Farbe f = Farbe.gelb;
		if (farbeText != null) f = Farbe.von(farbeText);
		String uid = p.getUUID().toString();
		long anzahl = punkte.values().stream().filter(w -> w.besitzerUuid.equals(uid)).count();
		if (anzahl >= LIMIT && !istOp(p)) { fehler(c, "Du hast schon " + LIMIT + " Wegpunkte. Lösche erst einen mit /wp entfernen."); return 0; }

		Punkt w = new Punkt();
		w.id = UUID.randomUUID().toString();
		w.name = name;
		w.besitzer = p.getGameProfile().name();
		w.besitzerUuid = uid;
		w.dim = p.level().dimension().identifier().toString();
		BlockPos b = p.blockPosition();
		w.x = b.getX(); w.y = b.getY(); w.z = b.getZ();
		w.farbe = f.name();
		w.erstellt = System.currentTimeMillis();
		punkte.put(w.id, w);
		speichern();
		for (ServerPlayer q : server.getPlayerList().getPlayers()) abgleichen(q);
		Farbe ff = f;
		c.getSource().sendSuccess(() -> Component.literal("◆ Wegpunkt ").withStyle(ChatFormatting.GRAY)
			.append(Component.literal(w.name).withStyle(ff.chat, ChatFormatting.BOLD))
			.append(Component.literal(" gesetzt bei " + w.x + " " + w.y + " " + w.z + ". Alle sehen ihn jetzt in der Ortungsleiste.").withStyle(ChatFormatting.GRAY)), false);
		LOG.info("{} hat Wegpunkt '{}' bei {} {} {} ({}) gesetzt", w.besitzer, name, w.x, w.y, w.z, w.dim);
		return 1;
	}

	static int liste(CommandContext<CommandSourceStack> c) {
		ServerPlayer p = c.getSource().getPlayer();
		if (punkte.isEmpty()) {
			c.getSource().sendSuccess(() -> Component.literal("Noch keine Wegpunkte. Setze einen mit /wp add <Name>").withStyle(ChatFormatting.GRAY), false);
			return 1;
		}
		List<Punkt> l = new ArrayList<>(punkte.values());
		String dim = p == null ? null : p.level().dimension().identifier().toString();
		Vec3 pos = p == null ? Vec3.ZERO : p.position();
		l.sort(Comparator.comparing((Punkt w) -> !w.dim.equals(dim)).thenComparingDouble(w -> w.mitte().distanceTo(pos)));
		MutableComponent m = Component.literal("◆ Wegpunkte (" + l.size() + ")").withStyle(ChatFormatting.GOLD, ChatFormatting.BOLD);
		boolean op = p != null && istOp(p);
		for (Punkt w : l) {
			m.append(Component.literal("\n "));
			m.append(Component.literal("● ").withStyle(w.farbeEnum().chat));
			m.append(Component.literal(w.name).withStyle(ChatFormatting.WHITE));
			m.append(Component.literal(" (" + w.besitzer + ") ").withStyle(ChatFormatting.DARK_GRAY));
			if (w.dim.equals(dim)) m.append(Component.literal((int) Math.round(w.mitte().distanceTo(pos)) + " m").withStyle(ChatFormatting.AQUA));
			else m.append(Component.literal(dimName(w.dim)).withStyle(ChatFormatting.DARK_AQUA));
			m.append(Component.literal("  " + w.x + " " + w.y + " " + w.z).withStyle(ChatFormatting.GRAY));
			if (p != null && (op || w.besitzerUuid.equals(p.getUUID().toString())))
				m.append(Component.literal(" [x]").withStyle(s -> s.withColor(ChatFormatting.RED).withClickEvent(new ClickEvent.SuggestCommand("/wp entfernen " + w.name))));
		}
		c.getSource().sendSuccess(() -> m, false);
		return l.size();
	}

	static int entfernen(CommandContext<CommandSourceStack> c) {
		ServerPlayer p = c.getSource().getPlayer();
		String name = StringArgumentType.getString(c, "name");
		Punkt w = finde(name);
		if (w == null) { fehler(c, "Kein Wegpunkt namens \"" + name + "\"."); return 0; }
		if (p != null && !w.besitzerUuid.equals(p.getUUID().toString()) && !istOp(p)) {
			fehler(c, "Diesen Wegpunkt hat " + w.besitzer + " gesetzt – nur " + w.besitzer + " kann ihn löschen."); return 0;
		}
		punkte.remove(w.id);
		schildEntfernen(w);
		speichern();
		for (ServerPlayer q : server.getPlayerList().getPlayers()) abgleichen(q);
		c.getSource().sendSuccess(() -> Component.literal("◆ Wegpunkt \"" + w.name + "\" gelöscht.").withStyle(ChatFormatting.GRAY), false);
		LOG.info("Wegpunkt '{}' von {} gelöscht ({})", w.name, w.besitzer, p == null ? "Konsole" : p.getGameProfile().name());
		return 1;
	}

	static int farbeAendern(CommandContext<CommandSourceStack> c) {
		ServerPlayer p = c.getSource().getPlayer();
		String name = StringArgumentType.getString(c, "name");
		Punkt w = finde(name);
		if (w == null) { fehler(c, "Kein Wegpunkt namens \"" + name + "\"."); return 0; }
		if (p != null && !w.besitzerUuid.equals(p.getUUID().toString()) && !istOp(p)) { fehler(c, "Das ist nicht dein Wegpunkt."); return 0; }
		Farbe f = Farbe.von(StringArgumentType.getString(c, "farbe"));
		if (f == null) { fehler(c, "Unbekannte Farbe. Möglich: rot orange gelb gruen tuerkis blau lila rosa weiss"); return 0; }
		w.farbe = f.name();
		for (ServerPlayer q : server.getPlayerList().getPlayers()) Schilder.zuruecksetzen(q);
		speichern();
		// Client kennt die alte Farbe: bei allen neu schicken
		for (ServerPlayer q : server.getPlayerList().getPlayers()) {
			Set<String> s = gesendet.get(q.getUUID());
			if (s != null && s.remove(w.id)) q.connection.send(ClientboundTrackedWaypointPacket.removeWaypoint(w.uuid()));
			abgleichen(q);
		}
		c.getSource().sendSuccess(() -> Component.literal("◆ \"" + w.name + "\" ist jetzt ").withStyle(ChatFormatting.GRAY)
			.append(Component.literal(f.name()).withStyle(f.chat)), false);
		return 1;
	}

	static int schilderSchalten(CommandContext<CommandSourceStack> c, boolean an) {
		ServerPlayer p = c.getSource().getPlayer();
		if (p == null) return 0;
		if (an) Schilder.aus.remove(p.getUUID()); else Schilder.aus.add(p.getUUID());
		c.getSource().sendSuccess(() -> Component.literal(an ? "◆ Namensschilder an." : "◆ Namensschilder aus. Wieder an: /wp schilder an")
			.withStyle(ChatFormatting.GRAY), false);
		return 1;
	}

	static int espSchalten(CommandContext<CommandSourceStack> c, Boolean an) {
		ServerPlayer p = c.getSource().getPlayer();
		if (p == null) return 0;
		boolean neu = an == null ? !Esp.an(p) : an;
		if (neu) Esp.einschalten(p); else Esp.ausschalten(server, p);
		c.getSource().sendSuccess(() -> Component.literal(neu
			? "◆ ESP an: Du siehst andere Spieler durch Wände. Aus mit /esp off"
			: "◆ ESP aus. Wieder an mit /esp on").withStyle(ChatFormatting.GRAY), false);
		return 1;
	}

	static int groesseSetzen(CommandContext<CommandSourceStack> c) {
		ServerPlayer p = c.getSource().getPlayer();
		if (p != null && !istOp(p)) { fehler(c, "Nur Ops können die Schildgröße ändern."); return 0; }
		Schilder.faktor = com.mojang.brigadier.arguments.DoubleArgumentType.getDouble(c, "wert");
		einstellungenSpeichern();
		c.getSource().sendSuccess(() -> Component.literal("◆ Schildgröße jetzt " + Schilder.faktor + " – gilt sofort für alle.")
			.withStyle(ChatFormatting.GRAY), false);
		return 1;
	}

	static Path einstellungenDatei() { return server.getWorldPath(LevelResource.ROOT).resolve("wegpunkte_einstellungen.json"); }

	static void einstellungenLaden() {
		try {
			Path f = einstellungenDatei();
			if (!Files.exists(f)) return;
			var o = com.google.gson.JsonParser.parseString(Files.readString(f, StandardCharsets.UTF_8)).getAsJsonObject();
			if (o.has("schildgroesse")) Schilder.faktor = o.get("schildgroesse").getAsDouble();
		} catch (Exception e) {
			LOG.error("wegpunkte_einstellungen.json konnte nicht gelesen werden", e);
		}
	}

	static void einstellungenSpeichern() {
		try {
			var o = new com.google.gson.JsonObject();
			o.addProperty("schildgroesse", Schilder.faktor);
			Files.writeString(einstellungenDatei(), GSON.toJson(o), StandardCharsets.UTF_8);
		} catch (Exception e) {
			LOG.error("wegpunkte_einstellungen.json konnte nicht gespeichert werden", e);
		}
	}

	static int info(CommandContext<CommandSourceStack> c) {
		Punkt w = finde(StringArgumentType.getString(c, "name"));
		if (w == null) { fehler(c, "Kein Wegpunkt mit diesem Namen."); return 0; }
		c.getSource().sendSuccess(() -> Component.literal("◆ ").withStyle(w.farbeEnum().chat)
			.append(Component.literal(w.name).withStyle(ChatFormatting.WHITE, ChatFormatting.BOLD))
			.append(Component.literal(" von " + w.besitzer + " – " + w.x + " " + w.y + " " + w.z + " (" + dimName(w.dim) + ")").withStyle(ChatFormatting.GRAY)), false);
		return 1;
	}

	// ---------- Ortungsleiste ----------

	/** Schickt dem Spieler genau die Wegpunkte seiner Dimension und entfernt alle anderen. */
	static void abgleichen(ServerPlayer p) {
		Set<String> s = gesendet.computeIfAbsent(p.getUUID(), k -> new HashSet<>());
		String dim = p.level().dimension().identifier().toString();
		boolean alles = neuSenden.remove(p.getUUID());
		if (alles) {
			// Client-Zustand unbekannt: alles Fremde entfernen, alles Passende neu schicken
			for (Punkt w : punkte.values())
				if (!w.dim.equals(dim)) p.connection.send(ClientboundTrackedWaypointPacket.removeWaypoint(w.uuid()));
			for (String id : s) if (!punkte.containsKey(id)) p.connection.send(ClientboundTrackedWaypointPacket.removeWaypoint(UUID.fromString(id)));
			s.clear();
		}
		for (Iterator<String> it = s.iterator(); it.hasNext(); ) {
			String id = it.next();
			Punkt w = punkte.get(id);
			if (w == null || !w.dim.equals(dim)) { p.connection.send(ClientboundTrackedWaypointPacket.removeWaypoint(UUID.fromString(id))); it.remove(); }
		}
		for (Punkt w : punkte.values()) {
			if (!w.dim.equals(dim) || s.contains(w.id)) continue;
			Waypoint.Icon icon = new Waypoint.Icon();
			icon.color = Optional.of(w.farbeEnum().rgb);
			p.connection.send(ClientboundTrackedWaypointPacket.addWaypointPosition(w.uuid(), icon, new Vec3i(w.x, w.y, w.z)));
			s.add(w.id);
		}
	}

	/** Mit Kompass in der Hand: Name + Entfernung des Wegpunkts, auf den man schaut. */
	static void kompass(ServerPlayer p) {
		boolean kompass = p.getMainHandItem().is(Items.COMPASS) || p.getOffhandItem().is(Items.COMPASS);
		if (!kompass) { letzteAnzeige.remove(p.getUUID()); return; }
		String dim = p.level().dimension().identifier().toString();
		Vec3 auge = p.getEyePosition();
		Vec3 blick = p.getLookAngle();
		double blickWinkel = Math.atan2(blick.z, blick.x);
		Punkt bester = null; double besterWinkel = Math.toRadians(7);
		for (Punkt w : punkte.values()) {
			if (!w.dim.equals(dim)) continue;
			Vec3 d = w.mitte().subtract(auge);
			if (d.x * d.x + d.z * d.z < 4) continue;
			double diff = Math.abs(Math.atan2(Math.sin(Math.atan2(d.z, d.x) - blickWinkel), Math.cos(Math.atan2(d.z, d.x) - blickWinkel)));
			if (diff < besterWinkel) { besterWinkel = diff; bester = w; }
		}
		if (bester == null) {
			if (letzteAnzeige.remove(p.getUUID()) != null) p.sendSystemMessage(Component.literal(""), true);
			return;
		}
		int m = (int) Math.round(bester.mitte().distanceTo(p.position()));
		int hoehe = bester.y - p.blockPosition().getY();
		String h = Math.abs(hoehe) < 3 ? "" : (hoehe > 0 ? "  ↑" + hoehe : "  ↓" + (-hoehe));
		p.sendSystemMessage(Component.literal("◆ ").withStyle(bester.farbeEnum().chat)
			.append(Component.literal(bester.name).withStyle(ChatFormatting.WHITE, ChatFormatting.BOLD))
			.append(Component.literal("  " + m + " m" + h).withStyle(ChatFormatting.AQUA))
			.append(Component.literal("  (" + bester.besitzer + ")").withStyle(ChatFormatting.DARK_GRAY)), true);
		letzteAnzeige.put(p.getUUID(), bester.id);
	}

	// ---------- Namensschild am Ort ----------

	static void schildSetzen(Punkt w) {
		String farbe = String.format("#%06X", w.farbeEnum().rgb);
		String text = w.name.replace("\\", "").replace("\"", "'");
		String cmd = String.format(Locale.ROOT,
			"execute in %s run summon text_display %.1f %.1f %.1f {billboard:\"center\",view_range:3.0f,shadow:1b,"
				+ "background:1073741824,Tags:[\"%s\",\"%s%s\"],"
				+ "text:[{text:\"◆ \",color:\"%s\"},{text:\"%s\",color:\"white\",bold:1b},{text:\"\\n%s\",color:\"gray\",bold:0b}]}",
			w.dim, w.x + 0.5, w.y + 2.3, w.z + 0.5, TAG, TAG_ID, w.id, farbe, text, w.besitzer);
		befehl(cmd);
	}

	static void schildEntfernen(Punkt w) {
		befehl("execute in " + w.dim + " run kill @e[type=text_display,tag=" + TAG_ID + w.id + "]");
	}

	static void befehl(String cmd) {
		server.getCommands().performPrefixedCommand(server.createCommandSourceStack().withSuppressedOutput(), cmd);
	}

	// ---------- Hilfen ----------

	static Punkt finde(String name) {
		for (Punkt w : punkte.values()) if (w.name.equalsIgnoreCase(name.trim())) return w;
		return null;
	}

	static boolean istOp(ServerPlayer p) { return server.getPlayerList().isOp(p.nameAndId()); }


	static String dimName(String dim) {
		return switch (dim) {
			case "minecraft:overworld" -> "Oberwelt";
			case "minecraft:the_nether" -> "Nether";
			case "minecraft:the_end" -> "End";
			default -> dim;
		};
	}

	static void fehler(CommandContext<CommandSourceStack> c, String text) {
		c.getSource().sendFailure(Component.literal(text));
	}

	static Path datei() { return server.getWorldPath(LevelResource.ROOT).resolve("wegpunkte.json"); }

	static void laden() {
		punkte.clear();
		try {
			Path f = datei();
			if (!Files.exists(f)) return;
			List<Punkt> l = GSON.fromJson(Files.readString(f, StandardCharsets.UTF_8), new TypeToken<List<Punkt>>() {}.getType());
			if (l != null) for (Punkt w : l) punkte.put(w.id, w);
			LOG.info("{} Wegpunkte geladen", punkte.size());
		} catch (Exception e) {
			LOG.error("wegpunkte.json konnte nicht gelesen werden", e);
		}
	}

	static void speichern() {
		if (server == null) return;
		try {
			Path f = datei();
			Path tmp = f.resolveSibling("wegpunkte.json.tmp");
			Files.writeString(tmp, GSON.toJson(new ArrayList<>(punkte.values())), StandardCharsets.UTF_8);
			Files.move(tmp, f, java.nio.file.StandardCopyOption.REPLACE_EXISTING, java.nio.file.StandardCopyOption.ATOMIC_MOVE);
		} catch (Exception e) {
			LOG.error("wegpunkte.json konnte nicht gespeichert werden", e);
		}
	}
}
