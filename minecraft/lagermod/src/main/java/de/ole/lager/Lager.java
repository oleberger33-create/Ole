package de.ole.lager;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.reflect.TypeToken;
import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.brigadier.context.CommandContext;
import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.command.v2.CommandRegistrationCallback;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.fabricmc.fabric.api.event.player.PlayerBlockBreakEvents;
import net.fabricmc.fabric.api.event.player.UseBlockCallback;
import net.fabricmc.fabric.api.event.player.UseItemCallback;
import net.minecraft.ChatFormatting;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.core.BlockPos;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.Container;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.CreativeModeTabs;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.world.item.component.ItemLore;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.ChestBlock;
import net.minecraft.world.level.block.entity.BarrelBlockEntity;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.ChestBlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.ChestType;
import net.minecraft.world.level.storage.LevelResource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.*;

/**
 * Gemeinsames Kisten-Lager, nur serverseitig.
 * Mit dem Lager-Terminal (Item) verbindet man Kisten und Fässer (Schleichen + Rechtsklick auf die Kiste) und öffnet
 * mit Rechtsklick ein Menü, das den Inhalt aller verbundenen Kisten zusammen zeigt: herausnehmen und hineinlegen von
 * überall. Kisten sind entweder geteilt (alle sehen sie) oder privat (nur der Besitzer sieht und öffnet sie).
 */
public class Lager implements ModInitializer {
	static final Logger LOG = LoggerFactory.getLogger("lager");
	static final String TERMINAL_TAG = "lager_terminal";
	static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();

	static class Kiste {
		String dim, besitzer, besitzerName;
		int x, y, z;
		boolean privat;
		BlockPos pos() { return new BlockPos(x, y, z); }
		String schluessel() { return Lager.schluessel(dim, x, y, z); }
		boolean gehoert(ServerPlayer p) { return besitzer.equals(p.getUUID().toString()); }
		/** Darf p diese Kiste im Terminal sehen und öffnen? */
		boolean sichtbar(ServerPlayer p) { return !privat || gehoert(p); }
	}

	static MinecraftServer server;
	static final Map<String, Kiste> kisten = new LinkedHashMap<>();
	static int tick;

	static String schluessel(String dim, int x, int y, int z) { return dim + "|" + x + "|" + y + "|" + z; }
	static String dimName(Level l) { return l.dimension().identifier().toString(); }

	@Override
	public void onInitialize() {
		ServerLifecycleEvents.SERVER_STARTED.register(s -> { server = s; laden(); });
		ServerLifecycleEvents.SERVER_STOPPING.register(s -> { speichern(); Tresor.allesSpeichern(); });
		// Jeder bekommt beim Betreten einen Tresor, falls er keinen hat (neue und alte Spieler)
		net.fabricmc.fabric.api.networking.v1.ServerPlayConnectionEvents.JOIN.register((h, sender, s) -> s.execute(() -> Tresor.geben(h.getPlayer())));
		net.fabricmc.fabric.api.networking.v1.ServerPlayConnectionEvents.DISCONNECT.register((h, s) -> {
			Tresor.speichern(h.getPlayer().getUUID());
			cache.remove(h.getPlayer().getUUID());
			cacheTick.remove(h.getPlayer().getUUID());
		});

		ServerTickEvents.END_SERVER_TICK.register(s -> {
			if (++tick % 1200 == 0) Tresor.allesSpeichern();
			if (tick % 40 != 0) return;
			for (ServerPlayer p : s.getPlayerList().getPlayers())
				if (p.containerMenu instanceof LagerMenu m) {
					try { m.anzeigen(); m.broadcastChanges(); } catch (RuntimeException e) { LOG.error("Lager-Anzeige", e); }
				}
		});

		// Tresor-Item: Rechtsklick öffnet den eigenen Tresor, schleichend die nächste Seite
		UseItemCallback.EVENT.register((spieler, welt, hand) -> {
			if (!Tresor.istTresor(spieler.getItemInHand(hand))) return InteractionResult.PASS;
			if (welt.isClientSide() || !(spieler instanceof ServerPlayer p)) return InteractionResult.SUCCESS;
			int s = Tresor.letzteSeite.getOrDefault(p.getUUID(), 1);
			if (p.isShiftKeyDown()) s = s % Tresor.SEITEN + 1;
			Tresor.letzteSeite.put(p.getUUID(), s);
			Tresor.oeffnen(p, s);
			return InteractionResult.SUCCESS;
		});

		// Rechtsklick in die Luft mit dem Terminal: Lager öffnen
		UseItemCallback.EVENT.register((spieler, welt, hand) -> {
			if (!istTerminal(spieler.getItemInHand(hand))) return InteractionResult.PASS;
			if (welt.isClientSide() || !(spieler instanceof ServerPlayer p)) return InteractionResult.SUCCESS;
			LagerMenu.oeffnen(p, "");
			return InteractionResult.SUCCESS;
		});

		UseBlockCallback.EVENT.register((spieler, welt, hand, treffer) -> {
			if (welt.isClientSide() || !(spieler instanceof ServerPlayer p)) return InteractionResult.PASS;
			if (Tresor.istTresor(spieler.getItemInHand(hand))) {
				if (hand == InteractionHand.MAIN_HAND) Tresor.oeffnen(p, Tresor.letzteSeite.getOrDefault(p.getUUID(), 1));
				return InteractionResult.SUCCESS;
			}
			BlockPos pos = treffer.getBlockPos();
			boolean terminal = istTerminal(spieler.getItemInHand(hand));
			if (terminal) {
				if (hand != InteractionHand.MAIN_HAND) return InteractionResult.SUCCESS;
				if (p.isShiftKeyDown() && lagerfaehig(welt.getBlockEntity(pos))) umschalten(p, (ServerLevel) welt, pos);
				else LagerMenu.oeffnen(p, "");
				return InteractionResult.SUCCESS;
			}
			// Private Kisten (auch die andere Hälfte einer Doppelkiste) öffnet nur der Besitzer
			for (BlockPos q : haelften(welt, pos)) {
				Kiste k = kisten.get(schluessel(dimName(welt), q.getX(), q.getY(), q.getZ()));
				if (k != null && k.privat && !k.gehoert(p) && !istOp(p)) {
					p.sendSystemMessage(Component.literal("🔒 Private Kiste von " + k.besitzerName).withStyle(ChatFormatting.RED), true);
					return InteractionResult.FAIL;
				}
			}
			return InteractionResult.PASS;
		});

		PlayerBlockBreakEvents.BEFORE.register((welt, spieler, pos, zustand, be) -> {
			if (welt.isClientSide() || !(spieler instanceof ServerPlayer p)) return true;
			Kiste k = kisten.get(schluessel(dimName(welt), pos.getX(), pos.getY(), pos.getZ()));
			if (k == null) return true;
			if (k.privat && !k.gehoert(p) && !istOp(p)) {
				p.sendSystemMessage(Component.literal("🔒 Private Kiste von " + k.besitzerName + " – nur der Besitzer kann sie abbauen").withStyle(ChatFormatting.RED), true);
				return false;
			}
			return true;
		});
		PlayerBlockBreakEvents.AFTER.register((welt, spieler, pos, zustand, be) -> {
			if (kisten.remove(schluessel(dimName(welt), pos.getX(), pos.getY(), pos.getZ())) != null) { cacheLeeren(); speichern(); }
		});

		CommandRegistrationCallback.EVENT.register((d, reg, env) -> d.register(Commands.literal("tresor")
			.executes(c -> { Tresor.oeffnen(c.getSource().getPlayerOrException(), 1); return 1; })
			.then(Commands.literal("item").executes(c -> {
				ServerPlayer p = c.getSource().getPlayerOrException();
				if (Tresor.hat(p)) { c.getSource().sendFailure(Component.literal("Du hast schon einen Tresor.")); return 0; }
				Tresor.geben(p); return 1; }))
			.then(Commands.argument("seite", IntegerArgumentType.integer(1, Tresor.SEITEN))
				.executes(c -> { Tresor.oeffnen(c.getSource().getPlayerOrException(), IntegerArgumentType.getInteger(c, "seite")); return 1; }))));
		CommandRegistrationCallback.EVENT.register((d, reg, env) -> d.register(Commands.literal("lager")
			.executes(Lager::hilfe)
			.then(Commands.literal("item").executes(Lager::itemGeben))
			.then(Commands.literal("oeffnen").executes(c -> { LagerMenu.oeffnen(c.getSource().getPlayerOrException(), ""); return 1; }))
			.then(Commands.literal("suche").then(Commands.argument("text", StringArgumentType.greedyString())
				.executes(c -> { LagerMenu.oeffnen(c.getSource().getPlayerOrException(), StringArgumentType.getString(c, "text")); return 1; })))
			.then(Commands.literal("liste").executes(Lager::liste))
			.then(Commands.literal("herstellen").then(Commands.argument("item", net.minecraft.commands.arguments.item.ItemArgument.item(reg))
				.executes(c -> herstellen(c, 1))
				.then(Commands.argument("anzahl", IntegerArgumentType.integer(1, 2304)).executes(c -> herstellen(c, IntegerArgumentType.getInteger(c, "anzahl"))))))
			.then(Commands.literal("scan").then(Commands.argument("radius", IntegerArgumentType.integer(1, 64)).executes(Lager::scan)))
			// Nur für Tests (Ops): einen Klick im offenen Lager-Menü auslösen
			.then(Commands.literal("testklick").then(Commands.argument("slot", IntegerArgumentType.integer(-999, 200))
				.then(Commands.argument("knopf", IntegerArgumentType.integer(0, 40)).then(Commands.argument("art", StringArgumentType.word())
					.executes(Lager::testKlick)))))
		));
	}

	// ------------------------------------------------------------------ Terminal-Item

	static ItemStack terminal() {
		ItemStack s = new ItemStack(Items.RECOVERY_COMPASS);
		CompoundTag t = new CompoundTag();
		t.putBoolean(TERMINAL_TAG, true);
		s.set(DataComponents.CUSTOM_DATA, CustomData.of(t));
		s.set(DataComponents.CUSTOM_NAME, Component.literal("Lager-Terminal").withStyle(s2 -> s2.withColor(ChatFormatting.GOLD).withItalic(false).withBold(true)));
		s.set(DataComponents.ENCHANTMENT_GLINT_OVERRIDE, true);
		s.set(DataComponents.MAX_STACK_SIZE, 1);
		s.set(DataComponents.LORE, new ItemLore(List.of(
			grau("Rechtsklick: Lager öffnen"),
			grau("Schleichen + Rechtsklick auf Kiste/Fass:"),
			grau("  verbinden → privat → trennen"))));
		return s;
	}

	static Component grau(String t) { return Component.literal(t).withStyle(s -> s.withColor(ChatFormatting.GRAY).withItalic(false)); }

	static boolean istTerminal(ItemStack s) {
		if (s.isEmpty()) return false;
		CustomData d = s.get(DataComponents.CUSTOM_DATA);
		return d != null && d.copyTag().getBooleanOr(TERMINAL_TAG, false);
	}

	static int itemGeben(CommandContext<CommandSourceStack> c) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
		ServerPlayer p = c.getSource().getPlayerOrException();
		for (ItemStack s : p.getInventory().getNonEquipmentItems())
			if (istTerminal(s)) { p.sendSystemMessage(Component.literal("Du hast schon ein Lager-Terminal.").withStyle(ChatFormatting.GRAY)); return 0; }
		if (!p.getInventory().add(terminal())) p.drop(terminal(), false, net.minecraft.util.Prediction.SERVER_ONLY);
		p.sendSystemMessage(Component.literal("◆ Lager-Terminal bekommen. Rechtsklick öffnet das Lager.").withStyle(ChatFormatting.GOLD));
		return 1;
	}

	// ------------------------------------------------------------------ Kisten verbinden

	static boolean lagerfaehig(BlockEntity be) { return be instanceof ChestBlockEntity || be instanceof BarrelBlockEntity; }

	/** Die Position und bei einer Doppelkiste auch die andere Hälfte. */
	static List<BlockPos> haelften(Level welt, BlockPos pos) {
		BlockState st = welt.getBlockState(pos);
		if (st.getBlock() instanceof ChestBlock && st.hasProperty(ChestBlock.TYPE) && st.getValue(ChestBlock.TYPE) != ChestType.SINGLE)
			return List.of(pos, pos.relative(ChestBlock.getConnectedDirection(st)));
		return List.of(pos);
	}

	/** Schleichen + Rechtsklick mit dem Terminal: nicht verbunden → geteilt → privat → getrennt. */
	static void umschalten(ServerPlayer p, ServerLevel welt, BlockPos pos) {
		List<BlockPos> teile = haelften(welt, pos);
		String dim = dimName(welt);
		Kiste k = kisten.get(schluessel(dim, pos.getX(), pos.getY(), pos.getZ()));
		String art = welt.getBlockEntity(pos) instanceof BarrelBlockEntity ? "Fass" : (teile.size() > 1 ? "Doppelkiste" : "Kiste");
		if (k != null && !k.gehoert(p) && !istOp(p)) {
			p.sendSystemMessage(Component.literal("Diese " + art + " hat " + k.besitzerName + " verbunden – nur " + k.besitzerName + " kann sie ändern.").withStyle(ChatFormatting.RED), true);
			return;
		}
		Component meldung;
		if (k == null) {
			for (BlockPos q : teile) {
				Kiste n = new Kiste();
				n.dim = dim; n.x = q.getX(); n.y = q.getY(); n.z = q.getZ();
				n.besitzer = p.getUUID().toString(); n.besitzerName = p.getPlainTextName(); n.privat = false;
				kisten.put(n.schluessel(), n);
			}
			meldung = Component.literal("✔ " + art + " mit dem Lager verbunden (für alle)").withStyle(ChatFormatting.GREEN);
		} else if (!k.privat) {
			for (BlockPos q : teile) {
				Kiste n = kisten.get(schluessel(dim, q.getX(), q.getY(), q.getZ()));
				if (n == null) { n = new Kiste(); n.dim = dim; n.x = q.getX(); n.y = q.getY(); n.z = q.getZ(); n.besitzer = k.besitzer; n.besitzerName = k.besitzerName; kisten.put(n.schluessel(), n); }
				n.privat = true;
			}
			meldung = Component.literal("🔒 " + art + " ist jetzt privat – nur " + k.besitzerName + " sieht und öffnet sie").withStyle(ChatFormatting.GOLD);
		} else {
			for (BlockPos q : teile) kisten.remove(schluessel(dim, q.getX(), q.getY(), q.getZ()));
			meldung = Component.literal("✖ " + art + " vom Lager getrennt").withStyle(ChatFormatting.GRAY);
		}
		p.sendSystemMessage(meldung, true);
		cacheLeeren();
		speichern();
	}

	/** Pro Spieler und Tick nur einmal suchen (ein Klick braucht die Liste mehrmals). */
	static final Map<UUID, List<Container>> cache = new HashMap<>();
	static final Map<UUID, Integer> cacheTick = new HashMap<>();

	static void cacheLeeren() { cache.clear(); cacheTick.clear(); }

	/** Alle Behälter, die p im Terminal sieht. Kisten, deren Block weg ist, werden entfernt. */
	static List<Container> behaelter(ServerPlayer p) {
		Integer t = cacheTick.get(p.getUUID());
		if (t != null && t == tick) return cache.get(p.getUUID());
		List<Container> l = behaelterSuchen(p);
		cache.put(p.getUUID(), l);
		cacheTick.put(p.getUUID(), tick);
		return l;
	}

	static List<Container> behaelterSuchen(ServerPlayer p) {
		List<Container> eigene = new ArrayList<>(), geteilte = new ArrayList<>();
		boolean geaendert = false;
		for (Iterator<Kiste> it = kisten.values().iterator(); it.hasNext(); ) {
			Kiste k = it.next();
			if (!k.sichtbar(p)) continue;
			ServerLevel welt = server.getLevel(ResourceKey.create(Registries.DIMENSION, Identifier.parse(k.dim)));
			if (welt == null) continue;
			// Chunk geladen halten, solange das Terminal benutzt wird (Ticket läuft nach ~15 s ab) – sonst würde er bei
			// jedem Klick neu von der Platte geladen
			net.minecraft.world.level.ChunkPos cp = new net.minecraft.world.level.ChunkPos(k.x >> 4, k.z >> 4);
			welt.getChunkSource().addTicketWithRadius(net.minecraft.server.level.TicketType.PORTAL, cp, 1);
			welt.getChunk(k.x >> 4, k.z >> 4);          // lädt den Chunk, falls nötig
			BlockEntity be = welt.getBlockEntity(k.pos());
			if (lagerfaehig(be) && be instanceof Container c) (k.privat ? eigene : geteilte).add(c);
			else { it.remove(); geaendert = true; }
		}
		if (geaendert) speichern();
		// Geteilte zuerst: neue Sachen landen bevorzugt dort
		geteilte.addAll(eigene);
		return geteilte;
	}

	// ------------------------------------------------------------------ Befehle

	static int hilfe(CommandContext<CommandSourceStack> c) {
		c.getSource().sendSuccess(() -> Component.literal("")
			.append(Component.literal("◆ Lager\n").withStyle(ChatFormatting.GOLD, ChatFormatting.BOLD))
			.append(Component.literal("/lager item").withStyle(ChatFormatting.YELLOW)).append(Component.literal(" – Lager-Terminal holen\n").withStyle(ChatFormatting.GRAY))
			.append(Component.literal("Rechtsklick mit Terminal").withStyle(ChatFormatting.YELLOW)).append(Component.literal(" – Lager öffnen (alle verbundenen Kisten)\n").withStyle(ChatFormatting.GRAY))
			.append(Component.literal("Schleichen + Rechtsklick auf Kiste").withStyle(ChatFormatting.YELLOW)).append(Component.literal(" – verbinden → privat → trennen\n").withStyle(ChatFormatting.GRAY))
			.append(Component.literal("/lager suche <Text>").withStyle(ChatFormatting.YELLOW)).append(Component.literal(" – nur passende Items zeigen\n").withStyle(ChatFormatting.GRAY))
			.append(Component.literal("/lager herstellen <Item> [Anzahl]").withStyle(ChatFormatting.YELLOW)).append(Component.literal(" – aus dem Lager herstellen, auch Zwischenschritte\n").withStyle(ChatFormatting.GRAY))
			.append(Component.literal("/lager liste").withStyle(ChatFormatting.YELLOW)).append(Component.literal(" – deine verbundenen Kisten").withStyle(ChatFormatting.GRAY)), false);
		return 1;
	}

	static int liste(CommandContext<CommandSourceStack> c) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
		ServerPlayer p = c.getSource().getPlayerOrException();
		int geteilt = 0, privat = 0, eigeneGeteilt = 0;
		for (Kiste k : kisten.values()) {
			if (!k.privat) { geteilt++; if (k.gehoert(p)) eigeneGeteilt++; }
			else if (k.gehoert(p)) privat++;
		}
		int g = geteilt, pr = privat, eg = eigeneGeteilt;
		MutableComponent m = Component.literal("◆ Lager: " + g + " geteilte Behälter (" + eg + " von dir), " + pr + " private von dir").withStyle(ChatFormatting.GOLD);
		c.getSource().sendSuccess(() -> m, false);
		return 1;
	}

	/** Op: alle Kisten und Fässer im Umkreis als geteilte Kisten verbinden. */
	static int scan(CommandContext<CommandSourceStack> c) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
		ServerPlayer p = c.getSource().getPlayerOrException();
		if (!istOp(p)) { c.getSource().sendFailure(Component.literal("Nur Ops.")); return 0; }
		int r = IntegerArgumentType.getInteger(c, "radius"), neu = 0;
		ServerLevel welt = p.level();
		String dim = dimName(welt);
		BlockPos m = p.blockPosition();
		for (BlockPos q : BlockPos.betweenClosed(m.offset(-r, -r, -r), m.offset(r, r, r))) {
			if (!lagerfaehig(welt.getBlockEntity(q))) continue;
			String s = schluessel(dim, q.getX(), q.getY(), q.getZ());
			if (kisten.containsKey(s)) continue;
			Kiste n = new Kiste();
			n.dim = dim; n.x = q.getX(); n.y = q.getY(); n.z = q.getZ();
			n.besitzer = p.getUUID().toString(); n.besitzerName = p.getPlainTextName();
			kisten.put(s, n); neu++;
		}
		cacheLeeren();
		speichern();
		int z = neu;
		c.getSource().sendSuccess(() -> Component.literal("◆ " + z + " Behälter im Umkreis " + r + " verbunden.").withStyle(ChatFormatting.GOLD), true);
		return neu;
	}

	static int herstellen(CommandContext<CommandSourceStack> c, int anzahl) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
		ServerPlayer p = c.getSource().getPlayerOrException();
		net.minecraft.world.item.Item item = net.minecraft.commands.arguments.item.ItemArgument.getItem(c, "item").item().value();
		Herstellen.Ergebnis e = Herstellen.herstellen(p, item, anzahl);
		String name = new ItemStack(item).getHoverName().getString();
		if (e.gemacht() > 0) {
			String t = "◆ " + e.gemacht() + "× " + name + " hergestellt" + (e.fehlt() != null && e.gemacht() < anzahl ? " – dann ging es nicht weiter: " + e.fehlt() : "");
			c.getSource().sendSuccess(() -> Component.literal(t).withStyle(ChatFormatting.GOLD), false);
		} else c.getSource().sendFailure(Component.literal(name + " nicht hergestellt. " + (e.fehlt() == null ? "" : e.fehlt())));
		if (p.containerMenu instanceof LagerMenu m) { m.anzeigen(); m.broadcastChanges(); }
		return e.gemacht();
	}

	static int testKlick(CommandContext<CommandSourceStack> c) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
		ServerPlayer p = c.getSource().getPlayerOrException();
		if (!istOp(p) || !(p.containerMenu instanceof LagerMenu m)) { c.getSource().sendFailure(Component.literal("Kein Lager offen / keine Rechte")); return 0; }
		m.clicked(IntegerArgumentType.getInteger(c, "slot"), IntegerArgumentType.getInteger(c, "knopf"),
			net.minecraft.world.inventory.ContainerInput.valueOf(StringArgumentType.getString(c, "art")), p);
		ItemStack hand = m.getCarried();
		c.getSource().sendSuccess(() -> Component.literal("Hand: " + hand.getCount() + " " + hand.getItem() + " | Sorten: " + m.sichtbar.size()), false);
		return 1;
	}

	// ------------------------------------------------------------------ Ordner (aus den Kreativ-Reitern)

	record Ordner(String name, Item symbol, List<ResourceKey<CreativeModeTab>> reiter) {}

	static final List<Ordner> ORDNER = List.of(
		new Ordner("Alles", Items.CHEST, List.of()),
		new Ordner("Baublöcke", Items.BRICKS, List.of(CreativeModeTabs.BUILDING_BLOCKS, CreativeModeTabs.COLORED_BLOCKS)),
		new Ordner("Natur", Items.GRASS_BLOCK, List.of(CreativeModeTabs.NATURAL_BLOCKS)),
		new Ordner("Funktionsblöcke", Items.FURNACE, List.of(CreativeModeTabs.FUNCTIONAL_BLOCKS)),
		new Ordner("Redstone", Items.REDSTONE, List.of(CreativeModeTabs.REDSTONE_BLOCKS)),
		new Ordner("Werkzeuge", Items.IRON_PICKAXE, List.of(CreativeModeTabs.TOOLS_AND_UTILITIES)),
		new Ordner("Kampf & Rüstung", Items.IRON_SWORD, List.of(CreativeModeTabs.COMBAT)),
		new Ordner("Essen", Items.BREAD, List.of(CreativeModeTabs.FOOD_AND_DRINKS)),
		new Ordner("Rohstoffe & Sonstiges", Items.IRON_INGOT, List.of(CreativeModeTabs.INGREDIENTS, CreativeModeTabs.SPAWN_EGGS)));

	static Map<Item, Integer> ordnerVonItem;

	/** Ordner-Nummer (1 … 8) für ein Item; Items ohne Kreativ-Reiter landen in „Rohstoffe & Sonstiges“. */
	static int ordner(Item item) {
		if (ordnerVonItem == null) {
			ordnerVonItem = new HashMap<>();
			try {
				CreativeModeTabs.tryRebuildTabContents(server.getWorldData().enabledFeatures(), true, server.registryAccess());
				for (int o = 1; o < ORDNER.size(); o++)
					for (ResourceKey<CreativeModeTab> k : ORDNER.get(o).reiter()) {
						CreativeModeTab tab = net.minecraft.core.registries.BuiltInRegistries.CREATIVE_MODE_TAB.getValue(k);
						if (tab == null) continue;
						for (ItemStack s : tab.getDisplayItems()) ordnerVonItem.putIfAbsent(s.getItem(), o);
					}
				LOG.info("Lager: {} Items in Ordner einsortiert", ordnerVonItem.size());
			} catch (RuntimeException e) { LOG.error("Lager: Ordner", e); }
		}
		return ordnerVonItem.getOrDefault(item, ORDNER.size() - 1);
	}

	/** Protokoll aller Ein- und Auslagerungen (welt/lager_protokoll.log), damit verlorene Sachen nachvollziehbar sind. */
	static void protokoll(ServerPlayer p, String art, ItemStack muster, int anzahl) {
		if (anzahl <= 0 || server == null) return;
		try {
			String z = java.time.LocalDateTime.now().withNano(0) + " " + p.getPlainTextName() + " " + art + " " + anzahl + " "
				+ net.minecraft.core.registries.BuiltInRegistries.ITEM.getKey(muster.getItem()) + "\n";
			Files.writeString(server.getWorldPath(LevelResource.ROOT).resolve("lager_protokoll.log"), z, StandardCharsets.UTF_8,
				java.nio.file.StandardOpenOption.CREATE, java.nio.file.StandardOpenOption.APPEND);
		} catch (Exception e) { LOG.error("Lager-Protokoll", e); }
	}

	static boolean istOp(ServerPlayer p) { return server.getPlayerList().isOp(p.nameAndId()); }

	// ------------------------------------------------------------------ Speichern

	static Path datei() { return server.getWorldPath(LevelResource.ROOT).resolve("lager.json"); }

	static void laden() {
		kisten.clear();
		try {
			Path f = datei();
			if (!Files.exists(f)) return;
			List<Kiste> l = GSON.fromJson(Files.readString(f, StandardCharsets.UTF_8), new TypeToken<List<Kiste>>() {}.getType());
			if (l != null) for (Kiste k : l) kisten.put(k.schluessel(), k);
			LOG.info("Lager: {} Behälter geladen", kisten.size());
		} catch (Exception e) { LOG.error("Lager laden", e); }
	}

	static void speichern() {
		if (server == null) return;
		try {
			Path f = datei(), tmp = f.resolveSibling("lager.json.tmp");
			Files.writeString(tmp, GSON.toJson(new ArrayList<>(kisten.values())), StandardCharsets.UTF_8);
			Files.move(tmp, f, java.nio.file.StandardCopyOption.REPLACE_EXISTING, java.nio.file.StandardCopyOption.ATOMIC_MOVE);
		} catch (Exception e) { LOG.error("Lager speichern", e); }
	}
}
