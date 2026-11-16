package de.ole.tpa;

import net.minecraft.network.chat.ClickEvent;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Display;
import net.minecraft.world.phys.AABB;

import java.util.*;

/**
 * Was Bedrock nicht kann, für Bedrock-Spieler nachgebaut:
 * - Chat-Nachrichten mit anklickbaren Befehlen (Farmhelper-Menüs, TPA-Knöpfe, Wegpunkt-Liste, …) erscheinen zusätzlich
 *   als Fenster mit Knöpfen. Nachrichten aus demselben Tick werden zu einem Fenster zusammengefasst.
 * - Geisterblöcke des Farmhelpers (block_display, zeigt Geyser nicht an) erscheinen als schwebende Blöcke (nur für sie).
 */
public final class BedrockChat {
	private BedrockChat() {}

	record Knopf(String text, String befehl) {}

	static final class Offen {
		final StringBuilder text = new StringBuilder();
		final List<Knopf> knoepfe = new ArrayList<>();
	}

	static final Map<UUID, Offen> offen = new HashMap<>();
	static final Map<UUID, Integer> zuletzt = new HashMap<>();
	static boolean beimSenden;

	/** Aus dem Mixin: jede System-Nachricht an einen Spieler. */
	public static void nachricht(ServerPlayer p, Component c) {
		if (beimSenden || Tpa.server == null || !Bedrock.formulare(p)) return;
		List<Knopf> k = new ArrayList<>();
		sammeln(c, k);
		Offen o = offen.get(p.getUUID());
		if (k.isEmpty() && o == null) return;
		if (o == null) { o = new Offen(); offen.put(p.getUUID(), o); }
		String zeile = c.getString().strip();
		if (!zeile.isEmpty()) { if (o.text.length() > 0) o.text.append('\n'); o.text.append(zeile); }
		for (Knopf x : k) if (o.knoepfe.stream().noneMatch(y -> y.befehl().equals(x.befehl()))) o.knoepfe.add(x);
	}

	static void sammeln(Component c, List<Knopf> k) {
		ClickEvent e = c.getStyle().getClickEvent();
		if (e instanceof ClickEvent.RunCommand rc) {
			String t = c.getString().strip().replaceAll("^[\\[➜\\s]+|[\\]\\s]+$", "");
			if (t.isEmpty()) t = rc.command();
			if (t.length() > 40) t = t.substring(0, 40) + "…";
			k.add(new Knopf(t, rc.command()));
			return;                                     // Kinder gehören zum selben Knopf
		}
		for (Component s : c.getSiblings()) sammeln(s, k);
	}

	/** Am Ende jedes Ticks: gesammelte Nachrichten als ein Fenster schicken. */
	static void tick(MinecraftServer s, int tick) {
		if (!offen.isEmpty()) {
			for (Map.Entry<UUID, Offen> en : new ArrayList<>(offen.entrySet())) {
				Offen o = en.getValue();
				ServerPlayer p = s.getPlayerList().getPlayer(en.getKey());
				if (p == null || o.knoepfe.isEmpty()) continue;
				Integer z = zuletzt.get(en.getKey());
				if (z != null && tick - z < 10) continue;    // höchstens zwei Fenster pro Sekunde
				zuletzt.put(en.getKey(), tick);
				Formulare.knopfFenster(p, o.text.toString(), o.knoepfe);
			}
			offen.clear();
		}
		for (ServerPlayer p : s.getPlayerList().getPlayers()) {
			if (!Bedrock.istBedrock(p)) continue;
			schleichen(p, tick);
			if (tick % 10 == 0) geister(p);
		}
	}

	// ------------------------------------------------------------------ Menü ohne Tippen (Controller/Handy)

	static final Map<UUID, Boolean> schlichVorher = new HashMap<>();
	static final Map<UUID, Integer> letztesSchleichen = new HashMap<>();

	/** Zweimal kurz hintereinander schleichen (innerhalb 0,4 s) öffnet das Menü. */
	static void schleichen(ServerPlayer p, int tick) {
		UUID u = p.getUUID();
		boolean jetzt = p.isShiftKeyDown();
		boolean vorher = schlichVorher.getOrDefault(u, false);
		schlichVorher.put(u, jetzt);
		if (!jetzt || vorher) return;                       // nur der Moment des Drückens zählt
		Integer z = letztesSchleichen.get(u);
		if (z != null && tick - z <= 8 && !p.isSpectator()) {
			letztesSchleichen.remove(u);
			Formulare.hauptmenue(p);
		} else letztesSchleichen.put(u, tick);
	}

	// ------------------------------------------------------------------ Geisterblöcke für Bedrock

	/** Pro Spieler: Geist-Entity-ID → ID des falschen fallenden Blocks, den nur dieser Spieler sieht. */
	static final Map<UUID, Map<Integer, Integer>> geschickt = new HashMap<>();
	static final Map<UUID, Object> welt = new HashMap<>();
	static int naechsteId = 1_600_000_000;
	static net.minecraft.network.syncher.EntityDataAccessor<Boolean> OHNE_SCHWERKRAFT;

	@SuppressWarnings("unchecked")
	static net.minecraft.network.syncher.EntityDataAccessor<Boolean> ohneSchwerkraft() throws ReflectiveOperationException {
		if (OHNE_SCHWERKRAFT == null) {
			java.lang.reflect.Field f = net.minecraft.world.entity.Entity.class.getDeclaredField("DATA_NO_GRAVITY");
			f.setAccessible(true);
			OHNE_SCHWERKRAFT = (net.minecraft.network.syncher.EntityDataAccessor<Boolean>) f.get(null);
		}
		return OHNE_SCHWERKRAFT;
	}

	static void vergessen(UUID u) { geschickt.remove(u); welt.remove(u); schlichVorher.remove(u); letztesSchleichen.remove(u); }

	/**
	 * Farmhelper-Geisterblöcke (block_display, zeigt Geyser nicht an) in 32 Blöcken als schwebende fallende Blöcke
	 * schicken – nur an diesen Spieler. Bedrock zeigt sie als echten Block in voller Größe, man kann hindurchgehen.
	 */
	static void geister(ServerPlayer p) {
		UUID u = p.getUUID();
		Object w = p.level().dimension();
		if (!w.equals(welt.get(u))) { geschickt.remove(u); welt.put(u, w); }  // neue Dimension: Client hat alles vergessen
		Map<Integer, Integer> m = geschickt.computeIfAbsent(u, k -> new HashMap<>());
		AABB box = p.getBoundingBox().inflate(32);
		List<Display.BlockDisplay> l = p.level().getEntitiesOfClass(Display.BlockDisplay.class, box, d -> d.entityTags().contains("ofh_g"));
		Set<Integer> jetzt = new HashSet<>();
		int neu = 0;
		for (Display.BlockDisplay d : l) {
			jetzt.add(d.getId());
			if (m.containsKey(d.getId()) || neu >= 200) continue;
			neu++;
			int id = naechsteId++;
			m.put(d.getId(), id);
			double x = Math.floor(d.getX()) + 0.5, y = Math.floor(d.getY()), z = Math.floor(d.getZ()) + 0.5;
			int zustand = net.minecraft.world.level.block.Block.getId(d.getBlockState());
			p.connection.send(new net.minecraft.network.protocol.game.ClientboundAddEntityPacket(id, UUID.randomUUID(), x, y, z, 0f, 0f,
				net.minecraft.world.entity.EntityTypes.FALLING_BLOCK, zustand, net.minecraft.world.phys.Vec3.ZERO, 0d));
			try {
				p.connection.send(new net.minecraft.network.protocol.game.ClientboundSetEntityDataPacket(id,
					List.of(net.minecraft.network.syncher.SynchedEntityData.DataValue.create(ohneSchwerkraft(), true))));
			} catch (ReflectiveOperationException e) { /* ohne Schwerkraft-Flag geht es notfalls auch */ }
		}
		List<Integer> weg = new ArrayList<>();
		for (Iterator<Map.Entry<Integer, Integer>> it = m.entrySet().iterator(); it.hasNext(); ) {
			Map.Entry<Integer, Integer> en = it.next();
			if (!jetzt.contains(en.getKey())) { weg.add(en.getValue()); it.remove(); }
		}
		if (!weg.isEmpty())
			p.connection.send(new net.minecraft.network.protocol.game.ClientboundRemoveEntitiesPacket(weg.stream().mapToInt(i -> i).toArray()));
	}
}
