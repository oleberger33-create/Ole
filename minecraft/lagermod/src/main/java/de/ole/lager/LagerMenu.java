package de.ole.lager;

import net.minecraft.ChatFormatting;
import net.minecraft.core.component.DataComponents;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.Container;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.SimpleMenuProvider;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.ChestMenu;
import net.minecraft.world.inventory.ContainerInput;
import net.minecraft.world.inventory.MenuType;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.component.ItemLore;

import java.text.NumberFormat;
import java.util.*;

/**
 * Das Lager-Menü: eine große Kiste (6 Reihen). Oben 45 Felder mit allen Item-Sorten aus den verbundenen Behältern,
 * unten die Knöpfe. Die angezeigten Items sind nur Bilder – jeder Klick wird hier ausgewertet und holt echte Items
 * aus den Kisten bzw. legt sie hinein.
 */
public class LagerMenu extends ChestMenu {
	static final int FELDER = 45;
	static final int ZURUECK = 45, SORTIEREN = 48, INFO = 49, FILTER = 50, VOR = 53;

	static class Sorte {
		final ItemStack muster; long anzahl;
		Sorte(ItemStack m, long a) { muster = m; anzahl = a; }
	}

	final ServerPlayer spieler;
	final Container anzeige;
	int seite;
	boolean nachName;
	String filter;
	List<Sorte> sichtbar = List.of();

	static void oeffnen(ServerPlayer p, String filter) {
		String titel = filter.isEmpty() ? "Lager" : "Lager – Suche: " + filter;
		p.openMenu(new SimpleMenuProvider((id, inv, pl) -> new LagerMenu(id, inv, p, filter), Component.literal(titel)));
	}

	LagerMenu(int id, Inventory inv, ServerPlayer p, String filter) {
		this(id, inv, p, filter, new SimpleContainer(54));
	}

	private LagerMenu(int id, Inventory inv, ServerPlayer p, String filter, SimpleContainer c) {
		super(MenuType.GENERIC_9x6, id, inv, c, 6);
		this.spieler = p;
		this.anzeige = c;
		this.filter = filter == null ? "" : filter.toLowerCase(Locale.ROOT).trim();
		anzeigen();
	}

	@Override public boolean stillValid(Player p) { return true; }
	@Override public ItemStack quickMoveStack(Player p, int slot) { return ItemStack.EMPTY; }

	// ------------------------------------------------------------------ Anzeige

	void anzeigen() {
		List<Container> bs = Lager.behaelter(spieler);
		Map<Item, List<Sorte>> nachItem = new HashMap<>();
		List<Sorte> alle = new ArrayList<>();
		int frei = 0, plaetze = 0;
		for (Container c : bs) {
			for (int i = 0; i < c.getContainerSize(); i++) {
				plaetze++;
				ItemStack s = c.getItem(i);
				if (s.isEmpty()) { frei++; continue; }
				List<Sorte> l = nachItem.computeIfAbsent(s.getItem(), k -> new ArrayList<>());
				Sorte gefunden = null;
				for (Sorte x : l) if (ItemStack.isSameItemSameComponents(x.muster, s)) { gefunden = x; break; }
				if (gefunden == null) { gefunden = new Sorte(s.copyWithCount(1), 0); l.add(gefunden); alle.add(gefunden); }
				gefunden.anzahl += s.getCount();
			}
		}
		List<Sorte> liste = new ArrayList<>();
		for (Sorte s : alle) if (passt(s.muster)) liste.add(s);
		Comparator<Sorte> nachNamen = Comparator.comparing(s -> s.muster.getHoverName().getString().toLowerCase(Locale.ROOT));
		liste.sort(nachName ? nachNamen : Comparator.<Sorte>comparingLong(s -> -s.anzahl).thenComparing(nachNamen));
		sichtbar = liste;
		int seiten = Math.max(1, (liste.size() + FELDER - 1) / FELDER);
		seite = Math.max(0, Math.min(seite, seiten - 1));

		for (int i = 0; i < FELDER; i++) {
			int idx = seite * FELDER + i;
			anzeige.setItem(i, idx < liste.size() ? bild(liste.get(idx)) : ItemStack.EMPTY);
		}
		ItemStack rand = knopf(Items.STAINED_GLASS_PANE.gray(), " ");
		for (int i = FELDER; i < 54; i++) anzeige.setItem(i, rand);
		if (seite > 0) anzeige.setItem(ZURUECK, knopf(Items.ARROW, "◀ Seite zurück"));
		if (seite < seiten - 1) anzeige.setItem(VOR, knopf(Items.ARROW, "Seite vor ▶"));
		anzeige.setItem(SORTIEREN, knopf(Items.HOPPER, "Sortiert nach: " + (nachName ? "Name" : "Menge"), "Klick: umschalten"));
		anzeige.setItem(INFO, knopf(Items.CHEST, "Lager – Seite " + (seite + 1) + "/" + seiten,
			bs.size() + " Behälter verbunden",
			alle.size() + " Sorten, " + zahl(frei) + " von " + zahl(plaetze) + " Plätzen frei",
			"",
			"Items aus deinem Inventar:",
			"Shift-Klick legt sie ins Lager"));
		if (filter.isEmpty()) anzeige.setItem(FILTER, knopf(Items.NAME_TAG, "Suche", "Im Chat: /lager suche <Text>"));
		else anzeige.setItem(FILTER, knopf(Items.NAME_TAG, "Suche: " + filter, "Klick: Suche aufheben"));
	}

	boolean passt(ItemStack s) {
		if (filter.isEmpty()) return true;
		return s.getHoverName().getString().toLowerCase(Locale.ROOT).contains(filter)
			|| s.getItem().toString().toLowerCase(Locale.ROOT).contains(filter);
	}

	static String zahl(long n) { return NumberFormat.getIntegerInstance(Locale.GERMANY).format(n); }

	static ItemStack bild(Sorte s) {
		ItemStack b = s.muster.copyWithCount((int) Math.max(1, Math.min(s.anzahl, s.muster.getMaxStackSize())));
		List<Component> zeilen = new ArrayList<>();
		ItemLore alt = s.muster.get(DataComponents.LORE);
		if (alt != null) zeilen.addAll(alt.lines());
		zeilen.add(Component.literal("Im Lager: " + zahl(s.anzahl)).withStyle(st -> st.withColor(ChatFormatting.YELLOW).withItalic(false)));
		zeilen.add(Lager.grau("Links: Stapel · Rechts: 1 Stück"));
		zeilen.add(Lager.grau("Shift-Klick: Stapel ins Inventar"));
		b.set(DataComponents.LORE, new ItemLore(zeilen));
		return b;
	}

	static ItemStack knopf(Item item, String name, String... zeilen) {
		ItemStack s = new ItemStack(item);
		s.set(DataComponents.CUSTOM_NAME, Component.literal(name).withStyle(st -> st.withColor(ChatFormatting.GOLD).withItalic(false)));
		List<Component> l = new ArrayList<>();
		for (String z : zeilen) l.add(Lager.grau(z));
		s.set(DataComponents.LORE, new ItemLore(l));
		return s;
	}

	// ------------------------------------------------------------------ Klicks

	@Override
	public void clicked(int slot, int button, ContainerInput art, Player p) {
		if (slot >= 0 && slot < 54) {
			obenGeklickt(slot, button, art);
			anzeigen();
			broadcastChanges();
			return;
		}
		// Eigenes Inventar: Shift-Klick legt ins Lager; Doppelklick und Ziehen sind gesperrt (würden die Bilder oben erfassen)
		if (art == ContainerInput.QUICK_MOVE && slot >= 54 && slot < slots.size()) {
			Slot s = slots.get(slot);
			if (s.hasItem()) {
				ItemStack rest = einlagern(s.getItem().copy());
				s.set(rest);
				s.setChanged();
			}
			anzeigen();
			broadcastChanges();
			return;
		}
		if (art == ContainerInput.PICKUP_ALL || art == ContainerInput.QUICK_CRAFT) { broadcastFullState(); return; }
		super.clicked(slot, button, art, p);
	}

	void obenGeklickt(int slot, int button, ContainerInput art) {
		ItemStack hand = getCarried();
		if (slot >= FELDER) {
			if (art != ContainerInput.PICKUP) return;
			int seiten = Math.max(1, (sichtbar.size() + FELDER - 1) / FELDER);
			if (slot == ZURUECK && seite > 0) seite--;
			else if (slot == VOR && seite < seiten - 1) seite++;
			else if (slot == SORTIEREN) nachName = !nachName;
			else if (slot == FILTER && !filter.isEmpty()) { filter = ""; seite = 0; }
			return;
		}
		// Mit einem Item in der Hand auf ein Feld klicken: hineinlegen (links alles, rechts eins)
		if (!hand.isEmpty() && art == ContainerInput.PICKUP) {
			Sorte s = sorte(slot);
			if (button == 1 && s != null && ItemStack.isSameItemSameComponents(s.muster, hand)) {
				// Rechtsklick mit derselben Sorte in der Hand: noch eins dazunehmen
				if (hand.getCount() < hand.getMaxStackSize()) hand.grow(entnehmen(s.muster, 1).getCount());
				setCarried(hand);
				return;
			}
			if (button == 0) setCarried(einlagern(hand));
			else {
				ItemStack eins = hand.split(1);
				ItemStack rest = einlagern(eins);
				if (!rest.isEmpty()) hand.grow(rest.getCount());
				setCarried(hand);
			}
			return;
		}
		Sorte s = sorte(slot);
		if (s == null) return;
		int stapel = s.muster.getMaxStackSize();
		if (art == ContainerInput.PICKUP && hand.isEmpty()) {
			setCarried(entnehmen(s.muster, button == 0 ? stapel : 1));
		} else if (art == ContainerInput.QUICK_MOVE) {
			ItemStack geholt = entnehmen(s.muster, stapel);
			spieler.getInventory().add(geholt);
			if (!geholt.isEmpty()) einlagern(geholt);         // passte nicht mehr ins Inventar: zurück ins Lager
		} else if (art == ContainerInput.SWAP && button >= 0 && button < 9 && spieler.getInventory().getItem(button).isEmpty()) {
			spieler.getInventory().setItem(button, entnehmen(s.muster, stapel));
		}
	}

	Sorte sorte(int slot) {
		int idx = seite * FELDER + slot;
		return idx < sichtbar.size() ? sichtbar.get(idx) : null;
	}

	/** Legt den Stapel ins Lager (zuerst zu gleichen Items, dann in freie Plätze). Gibt den Rest zurück. */
	ItemStack einlagern(ItemStack st) {
		if (st.isEmpty() || Lager.istTerminal(st)) return st;
		List<Container> bs = Lager.behaelter(spieler);
		for (Container c : bs) {
			for (int i = 0; i < c.getContainerSize() && !st.isEmpty(); i++) {
				ItemStack da = c.getItem(i);
				if (da.isEmpty() || !ItemStack.isSameItemSameComponents(da, st)) continue;
				int platz = Math.min(c.getMaxStackSize(da), da.getMaxStackSize()) - da.getCount();
				if (platz <= 0) continue;
				int n = Math.min(platz, st.getCount());
				da.grow(n); st.shrink(n); c.setChanged();
			}
			if (st.isEmpty()) return ItemStack.EMPTY;
		}
		for (Container c : bs) {
			for (int i = 0; i < c.getContainerSize() && !st.isEmpty(); i++) {
				if (!c.getItem(i).isEmpty() || !c.canPlaceItem(i, st)) continue;
				c.setItem(i, st.split(Math.min(st.getCount(), c.getMaxStackSize(st))));
				c.setChanged();
			}
			if (st.isEmpty()) return ItemStack.EMPTY;
		}
		return st;
	}

	/** Holt bis zu n Stück der Sorte aus dem Lager. */
	ItemStack entnehmen(ItemStack muster, int n) {
		n = Math.min(n, muster.getMaxStackSize());
		ItemStack ergebnis = ItemStack.EMPTY;
		for (Container c : Lager.behaelter(spieler)) {
			for (int i = c.getContainerSize() - 1; i >= 0; i--) {
				int fehlt = n - ergebnis.getCount();
				if (fehlt <= 0) return ergebnis;
				ItemStack da = c.getItem(i);
				if (da.isEmpty() || !ItemStack.isSameItemSameComponents(da, muster)) continue;
				ItemStack teil = c.removeItem(i, Math.min(fehlt, da.getCount()));
				c.setChanged();
				if (ergebnis.isEmpty()) ergebnis = teil; else ergebnis.grow(teil.getCount());
			}
		}
		return ergebnis;
	}
}
