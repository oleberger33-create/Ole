package de.ole.tpa;

import net.minecraft.core.particles.DustParticleOptions;
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
 * - Geisterblöcke des Farmhelpers (block_display, zeigt Geyser nicht an) erscheinen als leuchtende Partikel.
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
		if (tick % 10 == 0) for (ServerPlayer p : s.getPlayerList().getPlayers()) if (Bedrock.istBedrock(p)) geister(p);
	}

	/** Farmhelper-Geisterblöcke in 24 Blöcken als Partikel zeigen (nur für diesen Spieler). */
	static void geister(ServerPlayer p) {
		AABB box = p.getBoundingBox().inflate(24);
		List<Display.BlockDisplay> l = p.level().getEntitiesOfClass(Display.BlockDisplay.class, box, d -> d.entityTags().contains("ofh_g"));
		int n = 0;
		for (Display.BlockDisplay d : l) {
			if (n++ > 300) break;
			double x = d.getX() + 0.4, y = d.getY() + 0.4, z = d.getZ() + 0.4;
			p.level().sendParticles(p, new DustParticleOptions(0x55FFFF, 1.2f), true, false, x, y, z, 2, 0.25, 0.25, 0.25, 0);
		}
	}
}
