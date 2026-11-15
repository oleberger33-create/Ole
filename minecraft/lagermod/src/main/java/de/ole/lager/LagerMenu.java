package de.ole.lager;

import net.minecraft.ChatFormatting;
import net.minecraft.core.NonNullList;
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
import net.minecraft.world.item.crafting.CraftingInput;
import net.minecraft.world.item.crafting.CraftingRecipe;
import net.minecraft.world.item.crafting.RecipeHolder;
import net.minecraft.world.item.crafting.RecipeType;
import net.minecraft.util.Prediction;

import java.text.NumberFormat;
import java.util.*;

/**
 * Das Lager-Terminal (wie das Crafting-Terminal aus Applied Energistics 2), als große Kiste mit 6 Reihen:
 * links 6 × 5 Felder mit allen Item-Sorten aus den verbundenen Behältern, rechts ein 3 × 3-Werkbank-Raster mit
 * Ergebnisfeld, unten die Knöpfe. Die angezeigten Items sind nur Bilder – jeder Klick wird hier ausgewertet und holt
 * echte Items aus den Kisten bzw. legt sie hinein. Nach dem Herstellen füllt sich das Raster aus dem Lager nach.
 */
public class LagerMenu extends ChestMenu {
	/** Felder für Lager-Items: Reihen 0–4, Spalten 0–5. */
	static final int[] FELD = new int[30];
	static {
		for (int r = 0, i = 0; r < 5; r++) for (int s = 0; s < 6; s++) FELD[i++] = r * 9 + s;
	}
	static final int[] RASTER = {6, 7, 8, 15, 16, 17, 24, 25, 26};
	static final int ERGEBNIS = 34, LEEREN = 43;
	static final int ZURUECK = 45, SORTIEREN = 48, INFO = 49, FILTER = 50, VOR = 53;

	static class Sorte {
		final ItemStack muster; long anzahl;
		Sorte(ItemStack m, long a) { muster = m; anzahl = a; }
	}

	final ServerPlayer spieler;
	final Container anzeige;
	final SimpleContainer raster = new SimpleContainer(9);
	int seite;
	boolean nachName;
	String filter;
	List<Sorte> sichtbar = List.of();

	static void oeffnen(ServerPlayer p, String filter) {
		String titel = filter.isEmpty() ? "Lager-Terminal" : "Lager – Suche: " + filter;
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

	/** Beim Schließen: was noch im Raster liegt, zurück ins Lager (Rest ins Inventar). */
	@Override
	public void removed(Player p) {
		super.removed(p);
		for (int i = 0; i < 9; i++) {
			ItemStack s = raster.removeItemNoUpdate(i);
			if (s.isEmpty()) continue;
			ItemStack rest = einlagern(s);
			if (!rest.isEmpty()) spieler.getInventory().placeItemBackInInventory(rest, Prediction.SERVER_ONLY);
		}
	}

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
		int seiten = seiten();
		seite = Math.max(0, Math.min(seite, seiten - 1));

		ItemStack rand = knopf(Items.STAINED_GLASS_PANE.gray(), " ");
		for (int i = 0; i < 54; i++) anzeige.setItem(i, rand);
		for (int i = 0; i < FELD.length; i++) {
			int idx = seite * FELD.length + i;
			anzeige.setItem(FELD[i], idx < liste.size() ? bild(liste.get(idx)) : ItemStack.EMPTY);
		}
		// Werkbank
		for (int i = 0; i < 9; i++) anzeige.setItem(RASTER[i], raster.getItem(i).copy());
		ItemStack erg = vorschau();
		if (erg.isEmpty()) anzeige.setItem(ERGEBNIS, knopf(Items.STAINED_GLASS_PANE.white(), "Ergebnis",
			"Leg ein Rezept ins Raster darüber.", "Items nimmst du links aus dem Lager."));
		else {
			List<Component> z = new ArrayList<>();
			ItemLore alt = erg.get(DataComponents.LORE);
			if (alt != null) z.addAll(alt.lines());
			z.add(Component.literal("Klick: 1× herstellen").withStyle(st -> st.withColor(ChatFormatting.YELLOW).withItalic(false)));
			z.add(Lager.grau("Shift-Klick: einen Stapel herstellen"));
			z.add(Lager.grau("Zutaten kommen automatisch aus dem Lager"));
			erg.set(DataComponents.LORE, new ItemLore(z));
			anzeige.setItem(ERGEBNIS, erg);
		}
		anzeige.setItem(LEEREN, knopf(Items.BARRIER, "Raster leeren", "Legt alles aus dem Raster ins Lager"));
		// Leiste unten
		if (seite > 0) anzeige.setItem(ZURUECK, knopf(Items.ARROW, "◀ Seite zurück"));
		if (seite < seiten - 1) anzeige.setItem(VOR, knopf(Items.ARROW, "Seite vor ▶"));
		anzeige.setItem(SORTIEREN, knopf(Items.HOPPER, "Sortiert nach: " + (nachName ? "Name" : "Menge"), "Klick: umschalten"));
		anzeige.setItem(INFO, knopf(Items.CHEST, "Lager – Seite " + (seite + 1) + "/" + seiten,
			bs.size() + " Behälter verbunden",
			alle.size() + " Sorten, " + zahl(frei) + " von " + zahl(plaetze) + " Plätzen frei",
			"",
			"Links: Stapel · Rechts: 1 Stück · Shift: ins Inventar",
			"Item in der Hand auf ein Feld: ins Lager",
			"Shift-Klick im eigenen Inventar: ins Lager"));
		if (filter.isEmpty()) anzeige.setItem(FILTER, knopf(Items.NAME_TAG, "Suche", "Im Chat: /lager suche <Text>"));
		else anzeige.setItem(FILTER, knopf(Items.NAME_TAG, "Suche: " + filter, "Klick: Suche aufheben"));
	}

	int seiten() { return Math.max(1, (sichtbar.size() + FELD.length - 1) / FELD.length); }

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

	int feldNr(int slot) { for (int i = 0; i < FELD.length; i++) if (FELD[i] == slot) return i; return -1; }
	int rasterNr(int slot) { for (int i = 0; i < 9; i++) if (RASTER[i] == slot) return i; return -1; }

	void obenGeklickt(int slot, int button, ContainerInput art) {
		int r = rasterNr(slot);
		if (r >= 0) { rasterGeklickt(r, button, art); return; }
		if (slot == ERGEBNIS) { ergebnisGeklickt(art); return; }
		int f = feldNr(slot);
		if (f >= 0) { lagerGeklickt(f, button, art); return; }
		if (art != ContainerInput.PICKUP || !getCarried().isEmpty()) return;
		if (slot == ZURUECK && seite > 0) seite--;
		else if (slot == VOR && seite < seiten() - 1) seite++;
		else if (slot == SORTIEREN) nachName = !nachName;
		else if (slot == FILTER && !filter.isEmpty()) { filter = ""; seite = 0; }
		else if (slot == LEEREN) rasterLeeren();
	}

	void lagerGeklickt(int f, int button, ContainerInput art) {
		ItemStack hand = getCarried();
		Sorte s = sorte(f);
		// Mit einem Item in der Hand auf ein Feld klicken: hineinlegen (links alles, rechts eins)
		if (!hand.isEmpty() && art == ContainerInput.PICKUP) {
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

	/** Klicks ins Werkbank-Raster verhalten sich wie bei einem normalen Platz. */
	void rasterGeklickt(int r, int button, ContainerInput art) {
		ItemStack hand = getCarried(), da = raster.getItem(r);
		if (art == ContainerInput.QUICK_MOVE) {
			if (!da.isEmpty()) raster.setItem(r, einlagern(da));
			return;
		}
		if (art == ContainerInput.SWAP && button >= 0 && button < 9) {
			ItemStack hb = spieler.getInventory().getItem(button);
			spieler.getInventory().setItem(button, da);
			raster.setItem(r, hb);
			return;
		}
		if (art != ContainerInput.PICKUP) return;
		if (hand.isEmpty()) {
			if (da.isEmpty()) return;
			int n = button == 0 ? da.getCount() : (da.getCount() + 1) / 2;
			setCarried(da.split(n));
			raster.setItem(r, da.isEmpty() ? ItemStack.EMPTY : da);
		} else if (da.isEmpty() || ItemStack.isSameItemSameComponents(da, hand)) {
			int platz = hand.getMaxStackSize() - da.getCount();
			int n = Math.min(platz, button == 0 ? hand.getCount() : 1);
			if (n <= 0) return;
			if (da.isEmpty()) raster.setItem(r, hand.split(n));
			else { da.grow(n); hand.shrink(n); }
			setCarried(hand);
		} else {                                         // andere Sorte: tauschen
			raster.setItem(r, hand);
			setCarried(da);
		}
	}

	void rasterLeeren() {
		for (int i = 0; i < 9; i++) {
			ItemStack s = raster.getItem(i);
			if (s.isEmpty()) continue;
			ItemStack rest = einlagern(s);
			raster.setItem(i, ItemStack.EMPTY);
			if (!rest.isEmpty()) spieler.getInventory().placeItemBackInInventory(rest, Prediction.SERVER_ONLY);
		}
	}

	// ------------------------------------------------------------------ Herstellen

	List<ItemStack> rasterListe() {
		List<ItemStack> l = new ArrayList<>(9);
		for (int i = 0; i < 9; i++) l.add(raster.getItem(i));
		return l;
	}

	Optional<RecipeHolder<CraftingRecipe>> rezept(CraftingInput in) {
		if (in.isEmpty()) return Optional.empty();
		return Lager.server.getRecipeManager().getRecipeFor(RecipeType.CRAFTING, in, spieler.level());
	}

	ItemStack vorschau() {
		CraftingInput in = CraftingInput.ofPositioned(3, 3, rasterListe()).input();
		return rezept(in).map(h -> h.value().assemble(in)).orElse(ItemStack.EMPTY);
	}

	/** Einmal herstellen: Zutaten aus dem Raster verbrauchen, leere Felder aus dem Lager nachfüllen. */
	ItemStack einmalHerstellen() {
		CraftingInput.Positioned pos = CraftingInput.ofPositioned(3, 3, rasterListe());
		CraftingInput in = pos.input();
		Optional<RecipeHolder<CraftingRecipe>> rz = rezept(in);
		if (rz.isEmpty()) return ItemStack.EMPTY;
		ItemStack erg = rz.get().value().assemble(in);
		if (erg.isEmpty()) return ItemStack.EMPTY;
		NonNullList<ItemStack> reste = rz.get().value().getRemainingItems(in);
		ItemStack[] vorher = new ItemStack[9];
		for (int i = 0; i < 9; i++) vorher[i] = raster.getItem(i).copyWithCount(1);

		erg.onCraftedBy(spieler, erg.getCount());
		spieler.triggerRecipeCrafted(rz.get(), in.items());
		for (int y = 0; y < in.height(); y++)
			for (int x = 0; x < in.width(); x++) {
				int i = (y + pos.top()) * 3 + x + pos.left();
				ItemStack s = raster.getItem(i);
				if (!s.isEmpty()) { s.shrink(1); if (s.isEmpty()) raster.setItem(i, ItemStack.EMPTY); }
				ItemStack rest = reste.get(x + y * in.width());
				if (!rest.isEmpty()) {
					rest = einlagern(rest);
					if (!rest.isEmpty()) spieler.getInventory().placeItemBackInInventory(rest, Prediction.SERVER_ONLY);
				}
			}
		for (int i = 0; i < 9; i++)
			if (raster.getItem(i).isEmpty() && !vorher[i].isEmpty()) {
				ItemStack neu = entnehmen(vorher[i], 1);
				if (!neu.isEmpty()) raster.setItem(i, neu);
			}
		return erg;
	}

	void ergebnisGeklickt(ContainerInput art) {
		ItemStack hand = getCarried();
		if (art == ContainerInput.PICKUP) {
			ItemStack v = vorschau();
			if (v.isEmpty()) return;
			if (!hand.isEmpty() && (!ItemStack.isSameItemSameComponents(hand, v) || hand.getCount() + v.getCount() > hand.getMaxStackSize())) return;
			ItemStack erg = einmalHerstellen();
			if (erg.isEmpty()) return;
			if (hand.isEmpty()) setCarried(erg); else { hand.grow(erg.getCount()); setCarried(hand); }
		} else if (art == ContainerInput.QUICK_MOVE) {
			ItemStack erstes = vorschau();
			if (erstes.isEmpty()) return;
			int gemacht = 0;
			while (gemacht < erstes.getMaxStackSize()) {
				ItemStack v = vorschau();
				if (v.isEmpty() || !ItemStack.isSameItemSameComponents(v, erstes)) break;
				ItemStack erg = einmalHerstellen();
				if (erg.isEmpty()) break;
				gemacht += erg.getCount();
				spieler.getInventory().add(erg);
				if (!erg.isEmpty()) {                           // Inventar voll: Rest ins Lager, dann aufhören
					ItemStack rest = einlagern(erg);
					if (!rest.isEmpty()) spieler.getInventory().placeItemBackInInventory(rest, Prediction.SERVER_ONLY);
					break;
				}
			}
		}
	}

	// ------------------------------------------------------------------ Lager

	Sorte sorte(int f) {
		int idx = seite * FELD.length + f;
		return idx < sichtbar.size() ? sichtbar.get(idx) : null;
	}

	/** Legt den Stapel ins Lager (zuerst zu gleichen Items, dann in freie Plätze). Gibt den Rest zurück. */
	ItemStack einlagern(ItemStack st) { return einlagern(Lager.behaelter(spieler), st); }

	static ItemStack einlagern(List<Container> bs, ItemStack st) {
		if (st.isEmpty() || Lager.istTerminal(st)) return st;
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
	ItemStack entnehmen(ItemStack muster, int n) { return entnehmen(Lager.behaelter(spieler), muster, n); }

	static ItemStack entnehmen(List<Container> bs, ItemStack muster, int n) {
		n = Math.min(n, muster.getMaxStackSize());
		ItemStack ergebnis = ItemStack.EMPTY;
		for (Container c : bs) {
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
