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

	// ------------------------------------------------------------------ Menü-Item für Bedrock

	static final String MENUE_TAG = "tpa_menue";

	static net.minecraft.world.item.ItemStack menueItem() {
		var s = new net.minecraft.world.item.ItemStack(net.minecraft.world.item.Items.NETHER_STAR);
		var t = new net.minecraft.nbt.CompoundTag();
		t.putBoolean(MENUE_TAG, true);
		s.set(net.minecraft.core.component.DataComponents.CUSTOM_DATA, net.minecraft.world.item.component.CustomData.of(t));
		s.set(net.minecraft.core.component.DataComponents.CUSTOM_NAME, Component.literal("Menü").withStyle(st -> st.withColor(ChatFormatting.GOLD).withBold(true).withItalic(false)));
		s.set(net.minecraft.core.component.DataComponents.MAX_STACK_SIZE, 1);
		s.set(net.minecraft.core.component.DataComponents.LORE, new net.minecraft.world.item.component.ItemLore(java.util.List.of(
			Component.literal("Benutzen: Teleport, TPA, Lager, Tresor").withStyle(st -> st.withColor(ChatFormatting.GRAY).withItalic(false)))));
		return s;
	}

	static boolean istMenueItem(net.minecraft.world.item.ItemStack s) {
		if (s.isEmpty()) return false;
		var d = s.get(net.minecraft.core.component.DataComponents.CUSTOM_DATA);
		return d != null && d.copyTag().getBooleanOr(MENUE_TAG, false);
	}

	static void menueItemGeben(ServerPlayer p) {
		for (var s : p.getInventory().getNonEquipmentItems()) if (istMenueItem(s)) return;
		if (!p.getInventory().add(menueItem())) p.drop(menueItem(), false, net.minecraft.util.Prediction.SERVER_ONLY);
	}

	static void anfrageFenster(ServerPlayer ziel, ServerPlayer fragender, boolean hier) {
		if (formulare(ziel)) Formulare.anfrage(ziel, fragender, hier);
	}
}
