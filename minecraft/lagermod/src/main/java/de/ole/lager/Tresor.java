package de.ole.lager;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.mojang.serialization.JsonOps;
import net.minecraft.ChatFormatting;
import net.minecraft.core.component.DataComponents;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.RegistryOps;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.SimpleMenuProvider;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.ChestMenu;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.world.item.component.ItemLore;
import net.minecraft.world.level.storage.LevelResource;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.*;

/**
 * Persönlicher Tresor: jeder Spieler hat 3 Seiten mit je 54 Plätzen, gespeichert direkt auf dem Server
 * (welt/tresor/&lt;uuid&gt;.json) – unabhängig von Kisten, Chunks oder Mods. Geöffnet wird er mit dem Tresor-Item
 * (Rechtsklick, schleichend = nächste Seite) oder /tresor [1-3]. Es ist eine ganz normale Kisten-Oberfläche.
 * Gespeichert wird beim Schließen, alle 60 Sekunden und beim Herunterfahren; die vorige Datei bleibt als .bak erhalten.
 */
final class Tresor {
	static final int SEITEN = 3, PLAETZE = 54;
	static final String TAG = "lager_tresor";
	static final Map<UUID, SimpleContainer[]> offen = new HashMap<>();
	static final Set<UUID> geaendert = new HashSet<>();

	private Tresor() {}

	static Path ordner() { return Lager.server.getWorldPath(LevelResource.ROOT).resolve("tresor"); }
	static Path datei(UUID u) { return ordner().resolve(u + ".json"); }

	static SimpleContainer[] seiten(UUID u) {
		return offen.computeIfAbsent(u, k -> {
			SimpleContainer[] s = new SimpleContainer[SEITEN];
			for (int i = 0; i < SEITEN; i++) {
				s[i] = new SimpleContainer(PLAETZE) {
					@Override public void setChanged() { super.setChanged(); geaendert.add(k); }
				};
			}
			laden(k, s);
			return s;
		});
	}

	static void laden(UUID u, SimpleContainer[] s) {
		Path f = datei(u);
		if (!Files.exists(f)) f = f.resolveSibling(u + ".json.bak");
		if (!Files.exists(f)) return;
		try {
			RegistryOps<JsonElement> ops = Lager.server.registryAccess().createSerializationContext(JsonOps.INSTANCE);
			JsonObject o = JsonParser.parseString(Files.readString(f, StandardCharsets.UTF_8)).getAsJsonObject();
			JsonArray seiten = o.getAsJsonArray("seiten");
			for (int p = 0; p < SEITEN && p < seiten.size(); p++) {
				JsonArray a = seiten.get(p).getAsJsonArray();
				for (int i = 0; i < PLAETZE && i < a.size(); i++) {
					if (a.get(i).isJsonNull()) continue;
					ItemStack st = ItemStack.OPTIONAL_CODEC.parse(ops, a.get(i)).result().orElse(ItemStack.EMPTY);
					s[p].setItem(i, st);
				}
			}
			geaendert.remove(u);
		} catch (Exception e) { Lager.LOG.error("Tresor laden " + u, e); }
	}

	static void speichern(UUID u) {
		SimpleContainer[] s = offen.get(u);
		if (s == null) return;
		try {
			RegistryOps<JsonElement> ops = Lager.server.registryAccess().createSerializationContext(JsonOps.INSTANCE);
			JsonObject o = new JsonObject();
			JsonArray seiten = new JsonArray();
			for (SimpleContainer c : s) {
				JsonArray a = new JsonArray();
				for (int i = 0; i < PLAETZE; i++) {
					ItemStack st = c.getItem(i);
					a.add(st.isEmpty() ? com.google.gson.JsonNull.INSTANCE : ItemStack.CODEC.encodeStart(ops, st).getOrThrow());
				}
				seiten.add(a);
			}
			o.add("seiten", seiten);
			Files.createDirectories(ordner());
			Path f = datei(u), tmp = f.resolveSibling(u + ".json.tmp");
			Files.writeString(tmp, o.toString(), StandardCharsets.UTF_8);
			if (Files.exists(f)) Files.copy(f, f.resolveSibling(u + ".json.bak"), StandardCopyOption.REPLACE_EXISTING);
			Files.move(tmp, f, StandardCopyOption.REPLACE_EXISTING, StandardCopyOption.ATOMIC_MOVE);
			geaendert.remove(u);
		} catch (Exception e) { Lager.LOG.error("Tresor speichern " + u, e); }
	}

	static void allesSpeichern() { for (UUID u : new ArrayList<>(geaendert)) speichern(u); }

	static void oeffnen(ServerPlayer p, int seite) {
		int nr = Math.max(1, Math.min(SEITEN, seite));
		SimpleContainer c = seiten(p.getUUID())[nr - 1];
		p.openMenu(new SimpleMenuProvider((id, inv, pl) -> new ChestMenu(net.minecraft.world.inventory.MenuType.GENERIC_9x6, id, inv, c, 6) {
			@Override public void removed(Player pl2) { super.removed(pl2); speichern(p.getUUID()); }
		}, Component.literal("Tresor – Seite " + nr + "/" + SEITEN)));
		p.sendSystemMessage(Component.literal("Tresor Seite " + nr + "/" + SEITEN + " · schleichen + Rechtsklick: nächste Seite · /tresor " + (nr % SEITEN + 1)).withStyle(ChatFormatting.GRAY), true);
	}

	// ------------------------------------------------------------------ Item

	static ItemStack item() {
		ItemStack s = new ItemStack(Items.SHULKER_SHELL);
		CompoundTag t = new CompoundTag();
		t.putBoolean(TAG, true);
		s.set(DataComponents.CUSTOM_DATA, CustomData.of(t));
		s.set(DataComponents.CUSTOM_NAME, Component.literal("Tresor").withStyle(st -> st.withColor(ChatFormatting.LIGHT_PURPLE).withBold(true).withItalic(false)));
		s.set(DataComponents.ENCHANTMENT_GLINT_OVERRIDE, true);
		s.set(DataComponents.MAX_STACK_SIZE, 1);
		s.set(DataComponents.LORE, new ItemLore(List.of(
			Lager.grau("Dein persönlicher Speicher (3 × 54 Plätze)"),
			Lager.grau("Rechtsklick: öffnen · schleichend: nächste Seite"),
			Lager.grau("Nur du kommst ran, sicher auf dem Server gespeichert"))));
		return s;
	}

	static boolean istTresor(ItemStack s) {
		if (s.isEmpty()) return false;
		CustomData d = s.get(DataComponents.CUSTOM_DATA);
		return d != null && d.copyTag().getBooleanOr(TAG, false);
	}

	static boolean hat(ServerPlayer p) {
		for (ItemStack s : p.getInventory().getNonEquipmentItems()) if (istTresor(s)) return true;
		return false;
	}

	static void geben(ServerPlayer p) {
		if (hat(p)) return;
		if (!p.getInventory().add(item())) p.drop(item(), false, net.minecraft.util.Prediction.SERVER_ONLY);
	}

	/** Welche Seite als nächstes (schleichender Rechtsklick blättert weiter). */
	static final Map<UUID, Integer> letzteSeite = new HashMap<>();
}
