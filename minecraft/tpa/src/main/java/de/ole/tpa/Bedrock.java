package de.ole.tpa;

import net.fabricmc.loader.api.FabricLoader;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;

/**
 * Bedrock-Unterstützung. Bedrock-Spieler (über Geyser/Floodgate) können keine Chat-Links und keine Links in Büchern
 * anklicken; für sie gibt es Fenster (Floodgate-Formulare). Ohne Floodgate fällt alles auf Kisten-Menüs/Chat zurück.
 * Die Floodgate-Klassen werden nur in {@link Formulare} benutzt, damit der Mod auch ohne Floodgate lädt.
 */
final class Bedrock {
	private Bedrock() {}

	static final boolean FLOODGATE = FabricLoader.getInstance().isModLoaded("floodgate");

	static boolean istBedrock(ServerPlayer p) {
		if (FLOODGATE) {
			try { return Formulare.istFloodgate(p.getUUID()); } catch (Throwable ignored) {}
		}
		return p.getPlainTextName().startsWith(".");
	}

	/** Können für diesen Spieler Fenster gezeigt werden? */
	static boolean formulare(ServerPlayer p) { return FLOODGATE && istBedrock(p); }

	static void hauptmenue(ServerPlayer p) {
		if (formulare(p)) { Formulare.hauptmenue(p); return; }
		p.sendSystemMessage(Component.literal("Menü: /tpmenu (Teleport-Ziele), /tpa <Spieler>, /lager oeffnen, /tresor").withStyle(ChatFormatting.GOLD));
	}

	static void zieleFenster(ServerPlayer p) { Formulare.ziele(p); }

	static void anfrageFenster(ServerPlayer ziel, ServerPlayer fragender, boolean hier) {
		if (formulare(ziel)) Formulare.anfrage(ziel, fragender, hier);
	}
}
