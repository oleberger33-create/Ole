package de.ole.tpa;

import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;
import net.minecraft.ChatFormatting;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.SimpleMenuProvider;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.ChestMenu;
import net.minecraft.world.inventory.ContainerInput;
import net.minecraft.world.inventory.MenuType;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.world.item.component.ItemLore;
import net.minecraft.world.level.storage.LevelResource;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

/**
 * Teleport-Menü als Kiste – für Bedrock-Spieler (dort lassen sich Links im Buch nicht anklicken) und per /tpmenu für alle.
 * Die Ziele stehen in tpmenu.json im Weltordner: [{"name": "Base", "item": "minecraft:red_bed", "befehl": "function …"}].
 * Ein Klick führt den Befehl als der Spieler aus (mit Server-Rechten, damit Datapack-Funktionen laufen).
 */
public class TpMenu extends ChestMenu {
	record Ziel(String name, String item, String befehl, String farbe) {}

	static List<Ziel> ziele = List.of();

	static void laden() {
		try {
			Path f = Tpa.server.getWorldPath(LevelResource.ROOT).resolve("tpmenu.json");
			if (!Files.exists(f)) { ziele = List.of(); return; }
			List<Ziel> l = new Gson().fromJson(Files.readString(f, StandardCharsets.UTF_8), new TypeToken<List<Ziel>>() {}.getType());
			ziele = l == null ? List.of() : l;
		} catch (Exception e) { ziele = List.of(); }
	}

	static boolean istBedrock(ServerPlayer p) { return p.getPlainTextName().startsWith("."); }

	static boolean istTpBuch(ItemStack s) {
		CustomData d = s.get(DataComponents.CUSTOM_DATA);
		return d != null && d.copyTag().contains("tpbuch");
	}

	static void oeffnen(ServerPlayer p) {
		laden();
		if (ziele.isEmpty()) { p.sendSystemMessage(Component.literal("Keine Teleport-Ziele eingerichtet.").withStyle(ChatFormatting.RED)); return; }
		int reihen = Math.min(6, Math.max(1, (ziele.size() + 8) / 9));
		MenuType<ChestMenu> typ = switch (reihen) {
			case 1 -> MenuType.GENERIC_9x1; case 2 -> MenuType.GENERIC_9x2; case 3 -> MenuType.GENERIC_9x3;
			case 4 -> MenuType.GENERIC_9x4; case 5 -> MenuType.GENERIC_9x5; default -> MenuType.GENERIC_9x6;
		};
		p.openMenu(new SimpleMenuProvider((id, inv, pl) -> new TpMenu(typ, id, inv, reihen, p), Component.literal("Teleport")));
	}

	final ServerPlayer spieler;
	final int groesse;

	TpMenu(MenuType<ChestMenu> typ, int id, Inventory inv, int reihen, ServerPlayer p) {
		this(typ, id, inv, reihen, p, new SimpleContainer(reihen * 9));
	}

	private TpMenu(MenuType<ChestMenu> typ, int id, Inventory inv, int reihen, ServerPlayer p, SimpleContainer c) {
		super(typ, id, inv, c, reihen);
		spieler = p;
		groesse = reihen * 9;
		for (int i = 0; i < ziele.size() && i < groesse; i++) {
			Ziel z = ziele.get(i);
			Item item = Items.ENDER_PEARL;
			try {
				Item x = BuiltInRegistries.ITEM.getValue(Identifier.parse(z.item()));
				if (x != null && x != Items.AIR) item = x;
			} catch (RuntimeException ignored) {}
			ItemStack s = new ItemStack(item);
			ChatFormatting f = null;
			if (z.farbe() != null) for (ChatFormatting cf : ChatFormatting.values()) if (cf.name().equalsIgnoreCase(z.farbe())) f = cf;
			ChatFormatting farbe = f == null ? ChatFormatting.GOLD : f;
			s.set(DataComponents.CUSTOM_NAME, Component.literal("➜ " + z.name()).withStyle(st -> st.withColor(farbe).withItalic(false)));
			s.set(DataComponents.LORE, new ItemLore(List.of(Component.literal("Antippen: hin teleportieren").withStyle(st -> st.withColor(ChatFormatting.GRAY).withItalic(false)))));
			c.setItem(i, s);
		}
	}

	@Override public boolean stillValid(Player p) { return true; }
	@Override public ItemStack quickMoveStack(Player p, int slot) { return ItemStack.EMPTY; }

	@Override
	public void clicked(int slot, int button, ContainerInput art, Player p) {
		if (slot >= 0 && slot < groesse && slot < ziele.size() && (art == ContainerInput.PICKUP || art == ContainerInput.QUICK_MOVE)) {
			Ziel z = ziele.get(slot);
			spieler.closeContainer();
			String uuid = spieler.getUUID().toString();
			Tpa.server.getCommands().performPrefixedCommand(Tpa.server.createCommandSourceStack().withSuppressedOutput(),
				"execute as " + uuid + " at @s run " + z.befehl());
			return;
		}
		// alles andere (Ziehen, Doppelklick, Shift) sperren, damit niemand die Symbole herausnimmt
		sendAllDataToRemote();
	}
}
