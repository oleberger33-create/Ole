package de.ole.tpa;

import com.mojang.brigadier.context.CommandContext;
import com.mojang.brigadier.exceptions.CommandSyntaxException;
import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.command.v2.CommandRegistrationCallback;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.fabricmc.fabric.api.networking.v1.ServerPlayConnectionEvents;
import net.minecraft.ChatFormatting;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.EntityArgument;
import net.minecraft.network.chat.ClickEvent;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.HoverEvent;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;

import java.util.*;

/**
 * Teleport-Anfragen: /tpa <Spieler> (zu ihm), /tpahere <Spieler> (er zu dir), /tpaccept, /tpdeny, /tpacancel.
 * Anfragen verfallen nach 60 Sekunden; im Chat gibt es Knöpfe zum Annehmen/Ablehnen. Nach dem Annehmen 3 Sekunden
 * stillstehen, dann Teleport (auch in andere Dimensionen).
 */
public class Tpa implements ModInitializer {
	static final int GUELTIG = 60 * 20, WARTEN = 3 * 20, ABKLINGEN = 10 * 20;

	/** Eine Anfrage: wer fragt, wen, und wer zu wem reist. */
	record Anfrage(UUID von, UUID an, boolean hier, int ablauf) {}
	/** Ein angenommener Teleport, der nach WARTEN Ticks ausgeführt wird, wenn der Reisende stillsteht. */
	record Wartend(UUID reisender, UUID ziel, double x, double y, double z, int zeit) {}

	static MinecraftServer server;
	static int tick;
	static final List<Anfrage> anfragen = new ArrayList<>();
	static final Map<UUID, Wartend> wartend = new HashMap<>();
	static final Map<UUID, Integer> zuletzt = new HashMap<>();

	@Override
	public void onInitialize() {
		ServerTickEvents.END_SERVER_TICK.register(s -> {
			server = s; tick++; ticken();
			if (Bedrock.FLOODGATE) try { BedrockChat.tick(s, tick); } catch (RuntimeException e) { org.slf4j.LoggerFactory.getLogger("tpa").error("Bedrock", e); }
		});
		net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents.SERVER_STARTED.register(s -> server = s);
		// Bedrock-Spieler können im Teleport-Buch nichts anklicken: dort öffnet das Buch stattdessen ein Kisten-Menü
		net.fabricmc.fabric.api.event.player.UseItemCallback.EVENT.register((spieler, welt, hand) -> {
			if (welt.isClientSide() || !(spieler instanceof ServerPlayer p)) return net.minecraft.world.InteractionResult.PASS;
			if (!TpMenu.istTpBuch(spieler.getItemInHand(hand)) || !TpMenu.istBedrock(p)) return net.minecraft.world.InteractionResult.PASS;
			TpMenu.oeffnen(p);
			return net.minecraft.world.InteractionResult.SUCCESS;
		});
		ServerPlayConnectionEvents.JOIN.register((h, sender, s) -> s.execute(() -> {
			ServerPlayer p = h.getPlayer();
			if (Bedrock.istBedrock(p)) p.sendSystemMessage(text("✦ Bedrock: Tippe /menu für Teleport, Lager, Tresor und TPA", ChatFormatting.GOLD));
		}));
		ServerPlayConnectionEvents.DISCONNECT.register((h, s) -> {
			UUID u = h.getPlayer().getUUID();
			anfragen.removeIf(a -> a.von().equals(u) || a.an().equals(u));
			wartend.values().removeIf(w -> w.reisender().equals(u) || w.ziel().equals(u));
		});
		CommandRegistrationCallback.EVENT.register((d, reg, env) -> {
			d.register(Commands.literal("tpa").then(Commands.argument("spieler", EntityArgument.player()).executes(c -> fragen(c, false))));
			d.register(Commands.literal("tpahere").then(Commands.argument("spieler", EntityArgument.player()).executes(c -> fragen(c, true))));
			d.register(Commands.literal("tpaccept").executes(c -> antworten(c, null, true))
				.then(Commands.argument("spieler", EntityArgument.player()).executes(c -> antworten(c, EntityArgument.getPlayer(c, "spieler"), true))));
			d.register(Commands.literal("tpdeny").executes(c -> antworten(c, null, false))
				.then(Commands.argument("spieler", EntityArgument.player()).executes(c -> antworten(c, EntityArgument.getPlayer(c, "spieler"), false))));
			d.register(Commands.literal("tpacancel").executes(Tpa::abbrechen));
			d.register(Commands.literal("tpmenu").executes(c -> { TpMenu.oeffnen(c.getSource().getPlayerOrException()); return 1; }));
			d.register(Commands.literal("menu").executes(c -> { Bedrock.hauptmenue(c.getSource().getPlayerOrException()); return 1; }));
		});
	}

	static MutableComponent text(String t, ChatFormatting f) { return Component.literal(t).withStyle(f); }

	static MutableComponent knopf(String t, ChatFormatting f, String befehl, String hover) {
		return Component.literal(t).withStyle(s -> s.withColor(f).withBold(true)
			.withClickEvent(new ClickEvent.RunCommand(befehl))
			.withHoverEvent(new HoverEvent.ShowText(Component.literal(hover))));
	}

	static int fragen(CommandContext<CommandSourceStack> c, boolean hier) throws CommandSyntaxException {
		return fragen(c.getSource().getPlayerOrException(), EntityArgument.getPlayer(c, "spieler"), hier);
	}

	static void fehler(ServerPlayer p, String t) { p.sendSystemMessage(text(t, ChatFormatting.RED)); }

	static int fragen(ServerPlayer p, ServerPlayer ziel, boolean hier) {
		if (ziel == p) { fehler(p, "Du kannst dir nicht selbst eine Anfrage schicken."); return 0; }
		Integer z = zuletzt.get(p.getUUID());
		if (z != null && tick - z < ABKLINGEN) {
			fehler(p, "Warte noch " + ((ABKLINGEN - (tick - z)) / 20 + 1) + " s bis zur nächsten Anfrage.");
			return 0;
		}
		zuletzt.put(p.getUUID(), tick);
		anfragen.removeIf(a -> a.von().equals(p.getUUID()) && a.an().equals(ziel.getUUID()));
		anfragen.add(new Anfrage(p.getUUID(), ziel.getUUID(), hier, tick + GUELTIG));
		String name = p.getPlainTextName();
		ziel.sendSystemMessage(Component.empty()
			.append(text("✉ " + name, ChatFormatting.GOLD))
			.append(text(hier ? " möchte, dass du zu " + (name) + " kommst. " : " möchte sich zu dir teleportieren. ", ChatFormatting.YELLOW))
			.append(knopf("[Annehmen]", ChatFormatting.GREEN, "/tpaccept " + name, "Klick: annehmen"))
			.append(Component.literal(" "))
			.append(knopf("[Ablehnen]", ChatFormatting.RED, "/tpdeny " + name, "Klick: ablehnen"))
			.append(text("  (60 s)", ChatFormatting.DARK_GRAY)));
		ziel.level().playSound(null, ziel.getX(), ziel.getY(), ziel.getZ(), SoundEvents.NOTE_BLOCK_PLING, SoundSource.PLAYERS, 0.7f, 1.4f);
		p.sendSystemMessage(Component.empty()
			.append(text("✉ Anfrage an " + ziel.getPlainTextName() + " geschickt. ", ChatFormatting.GRAY))
			.append(knopf("[Zurückziehen]", ChatFormatting.DARK_RED, "/tpacancel", "Klick: Anfrage zurückziehen")));
		// Bedrock: die Chat-Knöpfe werden automatisch zu einem Fenster (BedrockChat)
		return 1;
	}

	static int antworten(CommandContext<CommandSourceStack> c, ServerPlayer von, boolean ja) throws CommandSyntaxException {
		return antworten(c.getSource().getPlayerOrException(), von, ja);
	}

	static int antworten(ServerPlayer p, ServerPlayer von, boolean ja) {
		Anfrage gefunden = null;
		for (int i = anfragen.size() - 1; i >= 0; i--) {
			Anfrage a = anfragen.get(i);
			if (a.an().equals(p.getUUID()) && (von == null || a.von().equals(von.getUUID()))) { gefunden = a; break; }
		}
		if (gefunden == null) { fehler(p, "Keine offene Teleport-Anfrage."); return 0; }
		anfragen.remove(gefunden);
		ServerPlayer fragender = server.getPlayerList().getPlayer(gefunden.von());
		if (fragender == null) { fehler(p, "Der Spieler ist nicht mehr online."); return 0; }
		if (!ja) {
			p.sendSystemMessage(text("Anfrage von " + fragender.getPlainTextName() + " abgelehnt.", ChatFormatting.GRAY));
			fragender.sendSystemMessage(text("✖ " + p.getPlainTextName() + " hat deine Teleport-Anfrage abgelehnt.", ChatFormatting.RED));
			return 1;
		}
		ServerPlayer reisender = gefunden.hier() ? p : fragender;
		ServerPlayer ziel = gefunden.hier() ? fragender : p;
		wartend.put(reisender.getUUID(), new Wartend(reisender.getUUID(), ziel.getUUID(), reisender.getX(), reisender.getY(), reisender.getZ(), tick + WARTEN));
		reisender.sendSystemMessage(text("✔ Angenommen – 3 Sekunden stillstehen, dann geht's zu " + ziel.getPlainTextName() + ".", ChatFormatting.GREEN));
		if (reisender != p) p.sendSystemMessage(text("✔ Angenommen – " + reisender.getPlainTextName() + " kommt gleich.", ChatFormatting.GREEN));
		else fragender.sendSystemMessage(text("✔ " + p.getPlainTextName() + " hat angenommen und kommt gleich.", ChatFormatting.GREEN));
		return 1;
	}

	static int abbrechen(CommandContext<CommandSourceStack> c) throws CommandSyntaxException {
		ServerPlayer p = c.getSource().getPlayerOrException();
		boolean weg = anfragen.removeIf(a -> a.von().equals(p.getUUID()));
		weg |= wartend.remove(p.getUUID()) != null;
		if (weg) p.sendSystemMessage(text("Teleport-Anfrage zurückgezogen.", ChatFormatting.GRAY));
		else c.getSource().sendFailure(Component.literal("Du hast keine offene Anfrage."));
		return weg ? 1 : 0;
	}

	static void ticken() {
		for (Iterator<Anfrage> it = anfragen.iterator(); it.hasNext(); ) {
			Anfrage a = it.next();
			if (tick < a.ablauf()) continue;
			it.remove();
			ServerPlayer v = server.getPlayerList().getPlayer(a.von());
			if (v != null) v.sendSystemMessage(text("Deine Teleport-Anfrage ist abgelaufen.", ChatFormatting.GRAY));
		}
		for (Iterator<Wartend> it = wartend.values().iterator(); it.hasNext(); ) {
			Wartend w = it.next();
			ServerPlayer r = server.getPlayerList().getPlayer(w.reisender()), z = server.getPlayerList().getPlayer(w.ziel());
			if (r == null || z == null) { it.remove(); continue; }
			if (r.distanceToSqr(w.x(), w.y(), w.z()) > 0.25) {
				it.remove();
				r.sendSystemMessage(text("✖ Teleport abgebrochen – du hast dich bewegt.", ChatFormatting.RED));
				continue;
			}
			if (tick < w.zeit()) continue;
			it.remove();
			r.teleportTo(z.level(), z.getX(), z.getY(), z.getZ(), Set.of(), z.getYRot(), z.getXRot(), true);
			r.level().playSound(null, r.getX(), r.getY(), r.getZ(), SoundEvents.ENDERMAN_TELEPORT, SoundSource.PLAYERS, 0.6f, 1.2f);
		}
	}
}
