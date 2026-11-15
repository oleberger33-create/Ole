package de.ole.lager;

import net.minecraft.core.Holder;
import net.minecraft.core.NonNullList;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.Prediction;
import net.minecraft.world.Container;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.ItemStackTemplate;
import net.minecraft.world.item.crafting.*;

import java.lang.reflect.Field;
import java.util.*;

/**
 * /lager herstellen <Item> [Anzahl]: stellt ein Item mit einem Werkbank-Rezept aus Zutaten im Lager her (wie das
 * automatische Herstellen in AE2, ohne Muster). Fehlt eine Zutat, wird sie – wenn möglich – zuerst selbst hergestellt
 * (bis 4 Stufen tief, z. B. Truhe ← Bretter ← Stamm). Zwischenprodukte gehen ins Lager, das Ergebnis ins Inventar.
 */
final class Herstellen {
	static final int TIEFE = 4;

	record Ergebnis(int gemacht, String fehlt) {}

	private Herstellen() {}

	/** Alle Werkbank-Rezepte (geformt/formlos), deren Ergebnis dieses Item ist. */
	static List<RecipeHolder<?>> rezepteFuer(Item ziel) {
		List<RecipeHolder<?>> l = new ArrayList<>();
		for (RecipeHolder<?> h : Lager.server.getRecipeManager().getRecipes()) {
			Recipe<?> r = h.value();
			if (!(r instanceof ShapedRecipe) && !(r instanceof ShapelessRecipe)) continue;
			ItemStackTemplate t = ergebnisVorlage(r);
			if (t != null && t.item().value() == ziel) l.add(h);
		}
		return l;
	}

	@SuppressWarnings("unchecked")
	static List<Ingredient> formlos(Recipe<?> r) {
		try {
			Field f = ShapelessRecipe.class.getDeclaredField("ingredients");
			f.setAccessible(true);
			return (List<Ingredient>) f.get(r);
		} catch (ReflectiveOperationException | ClassCastException e) {
			return r.placementInfo().ingredients();
		}
	}

	static ItemStackTemplate ergebnisVorlage(Recipe<?> r) {
		try {
			Field f = (r instanceof ShapedRecipe ? ShapedRecipe.class : ShapelessRecipe.class).getDeclaredField("result");
			f.setAccessible(true);
			return (ItemStackTemplate) f.get(r);
		} catch (ReflectiveOperationException | ClassCastException e) {
			return null;
		}
	}

	/** Zutaten in Raster-Reihenfolge (3 × 3, leer = keine Zutat). */
	static List<Optional<Ingredient>> zutaten(Recipe<?> r) {
		List<Optional<Ingredient>> raster = new ArrayList<>(Collections.nCopies(9, Optional.empty()));
		if (r instanceof ShapedRecipe s) {
			List<Optional<Ingredient>> ing = s.getIngredients();
			for (int y = 0; y < s.getHeight(); y++)
				for (int x = 0; x < s.getWidth(); x++) raster.set(y * 3 + x, ing.get(y * s.getWidth() + x));
		} else {
			List<Ingredient> ing = formlos(r);
			for (int i = 0; i < ing.size() && i < 9; i++) raster.set(i, Optional.of(ing.get(i)));
		}
		return raster;
	}

	/** Bestand im Lager: Muster (1 Stück) → Anzahl. */
	static List<LagerMenu.Sorte> bestand(List<Container> bs) {
		List<LagerMenu.Sorte> l = new ArrayList<>();
		for (Container c : bs)
			for (int i = 0; i < c.getContainerSize(); i++) {
				ItemStack s = c.getItem(i);
				if (s.isEmpty()) continue;
				LagerMenu.Sorte g = null;
				for (LagerMenu.Sorte x : l) if (ItemStack.isSameItemSameComponents(x.muster, s)) { g = x; break; }
				if (g == null) { g = new LagerMenu.Sorte(s.copyWithCount(1), 0); l.add(g); }
				g.anzahl += s.getCount();
			}
		return l;
	}

	/** Wählt für jede Zutat ein passendes Item aus dem Lager. null-Einträge in fehlend = Zutat, die es nicht gibt. */
	static List<ItemStack> planen(List<Optional<Ingredient>> zut, List<LagerMenu.Sorte> bestand, List<Ingredient> fehlend) {
		Map<LagerMenu.Sorte, Long> genutzt = new HashMap<>();
		List<ItemStack> raster = new ArrayList<>(9);
		for (Optional<Ingredient> o : zut) {
			if (o.isEmpty()) { raster.add(ItemStack.EMPTY); continue; }
			LagerMenu.Sorte wahl = null;
			for (LagerMenu.Sorte s : bestand)
				if (s.anzahl - genutzt.getOrDefault(s, 0L) > 0 && o.get().test(s.muster)) { wahl = s; break; }
			if (wahl == null) { fehlend.add(o.get()); raster.add(ItemStack.EMPTY); continue; }
			genutzt.merge(wahl, 1L, Long::sum);
			raster.add(wahl.muster.copyWithCount(1));
		}
		return fehlend.isEmpty() ? raster : null;
	}

	static Ergebnis herstellen(ServerPlayer p, Item ziel, int anzahl) {
		List<RecipeHolder<?>> rezepte = rezepteFuer(ziel);
		if (rezepte.isEmpty()) return new Ergebnis(0, "Für " + new ItemStack(ziel).getHoverName().getString() + " gibt es kein Werkbank-Rezept.");
		int gemacht = 0;
		String fehlt = null;
		while (gemacht < anzahl) {
			ItemStack erg = einmal(p, rezepte, 0, new HashSet<>());
			if (erg == null || erg.isEmpty()) { fehlt = letzterFehler; break; }
			gemacht += erg.getCount();
			p.getInventory().add(erg);
			if (!erg.isEmpty()) {
				ItemStack rest = LagerMenu.einlagern(Lager.behaelter(p), erg);
				if (!rest.isEmpty()) p.getInventory().placeItemBackInInventory(rest, Prediction.SERVER_ONLY);
			}
		}
		return new Ergebnis(gemacht, fehlt);
	}

	static String letzterFehler;

	/** Einmal eines der Rezepte ausführen, Zutaten aus dem Lager; fehlende Zutaten ggf. erst herstellen. */
	static ItemStack einmal(ServerPlayer p, List<RecipeHolder<?>> rezepte, int tiefe, Set<Item> unterwegs) {
		for (int versuch = 0; versuch < 6; versuch++) {
			List<Container> bs = Lager.behaelter(p);
			List<LagerMenu.Sorte> bestand = bestand(bs);
			List<Ingredient> ersteFehlende = null;
			for (RecipeHolder<?> h : rezepte) {
				List<Ingredient> fehlend = new ArrayList<>();
				List<ItemStack> plan = planen(zutaten(h.value()), bestand, fehlend);
				if (plan == null) { if (ersteFehlende == null) ersteFehlende = fehlend; continue; }
				ItemStack erg = ausfuehren(p, bs, (CraftingRecipe) h.value(), plan);
				if (erg != null) return erg;
			}
			if (ersteFehlende == null) { letzterFehler = "Das Rezept passt nicht."; return ItemStack.EMPTY; }
			// Fehlende Zutat selbst herstellen (Ergebnis ins Lager), dann neu versuchen
			if (tiefe >= TIEFE || !unterZutatHerstellen(p, ersteFehlende.get(0), tiefe, unterwegs)) {
				letzterFehler = "Es fehlt: " + name(ersteFehlende.get(0));
				return ItemStack.EMPTY;
			}
		}
		letzterFehler = "Zu viele Zwischenschritte.";
		return ItemStack.EMPTY;
	}

	static boolean unterZutatHerstellen(ServerPlayer p, Ingredient ing, int tiefe, Set<Item> unterwegs) {
		for (Holder<Item> it : (Iterable<Holder<Item>>) ing.items()::iterator) {
			Item item = it.value();
			if (unterwegs.contains(item)) continue;
			List<RecipeHolder<?>> rz = rezepteFuer(item);
			if (rz.isEmpty()) continue;
			unterwegs.add(item);
			ItemStack erg = einmal(p, rz, tiefe + 1, unterwegs);
			unterwegs.remove(item);
			if (erg != null && !erg.isEmpty()) {
				ItemStack rest = LagerMenu.einlagern(Lager.behaelter(p), erg);
				if (!rest.isEmpty()) p.getInventory().placeItemBackInInventory(rest, Prediction.SERVER_ONLY);
				return true;
			}
		}
		return false;
	}

	/** Zutaten aus dem Lager nehmen, herstellen, Reste ins Lager. null, wenn etwas nicht geklappt hat (alles zurück). */
	static ItemStack ausfuehren(ServerPlayer p, List<Container> bs, CraftingRecipe r, List<ItemStack> plan) {
		List<ItemStack> genommen = new ArrayList<>(9);
		boolean ok = true;
		for (ItemStack m : plan) {
			if (m.isEmpty()) { genommen.add(ItemStack.EMPTY); continue; }
			ItemStack s = LagerMenu.entnehmen(bs, m, 1);
			if (s.isEmpty()) { ok = false; genommen.add(ItemStack.EMPTY); continue; }
			genommen.add(s);
		}
		CraftingInput in = CraftingInput.ofPositioned(3, 3, genommen).input();
		if (!ok || !r.matches(in, p.level())) {
			for (ItemStack s : genommen) if (!s.isEmpty()) LagerMenu.einlagern(bs, s);
			return null;
		}
		ItemStack erg = r.assemble(in);
		NonNullList<ItemStack> reste = r.getRemainingItems(in);
		for (ItemStack rest : reste)
			if (!rest.isEmpty()) {
				ItemStack x = LagerMenu.einlagern(bs, rest);
				if (!x.isEmpty()) p.getInventory().placeItemBackInInventory(x, Prediction.SERVER_ONLY);
			}
		erg.onCraftedBy(p, erg.getCount());
		return erg;
	}

	static String name(Ingredient ing) {
		Optional<Holder<Item>> erstes = ing.items().findFirst();
		return erstes.map(h -> new ItemStack(h.value()).getHoverName().getString()).orElse("?");
	}
}
