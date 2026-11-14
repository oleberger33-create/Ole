package de.ole.wegpunkte;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.game.ClientboundAddEntityPacket;
import net.minecraft.network.protocol.game.ClientboundRemoveEntitiesPacket;
import net.minecraft.network.protocol.game.ClientboundSetEntityDataPacket;
import net.minecraft.network.protocol.game.ClientboundTeleportEntityPacket;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Display;
import net.minecraft.world.entity.EntityTypes;
import net.minecraft.world.entity.PositionMoveRotation;
import net.minecraft.world.phys.Vec3;
import org.joml.Vector3f;

import java.lang.reflect.Field;
import java.util.*;

/**
 * Namensschilder, die jeder Spieler immer sieht – durch Wände und egal wie weit weg.
 * Für jeden Spieler und jeden Wegpunkt seiner Dimension schickt der Server ein Text-Display nur an diesen Spieler
 * (es existiert nicht in der Welt). Es steht in Richtung des Wegpunkts höchstens WEIT Blöcke vor dem Spieler, ist
 * „durchsichtig“ (see_through: durch Blöcke sichtbar) und zeigt Name und Entfernung. Ist der Wegpunkt näher, steht
 * das Schild am echten Ort.
 */
final class Schilder {
	static final double WEIT = 24;           // so weit vor dem Spieler stehen Schilder ferner Wegpunkte
	static final double NAH_HOEHE = 2.5;     // am echten Ort: so hoch über dem Wegpunkt

	static final class Schild {
		final Display.TextDisplay ent;
		final int id;
		Vec3 pos;
		String text = "";
		float groesse = -1;
		Schild(Display.TextDisplay ent) { this.ent = ent; this.id = ent.getId(); }
	}

	/** Spieler → (Wegpunkt-ID → Schild) */
	static final Map<UUID, Map<String, Schild>> schilder = new HashMap<>();
	/** Spieler, die die Schilder ausgeschaltet haben (/wp schilder aus) */
	static final Set<UUID> aus = new HashSet<>();

	static EntityDataAccessor<Object> TEXT, HINTERGRUND, FLAGS, SKALA, BILLBOARD, HELL, SICHT, INTERPOL;

	@SuppressWarnings("unchecked")
	static EntityDataAccessor<Object> feld(Class<?> k, String name) throws ReflectiveOperationException {
		Field f = k.getDeclaredField(name);
		f.setAccessible(true);
		return (EntityDataAccessor<Object>) f.get(null);
	}

	static boolean bereit() {
		if (TEXT != null) return true;
		try {
			TEXT = feld(Display.TextDisplay.class, "DATA_TEXT_ID");
			HINTERGRUND = feld(Display.TextDisplay.class, "DATA_BACKGROUND_COLOR_ID");
			FLAGS = feld(Display.TextDisplay.class, "DATA_STYLE_FLAGS_ID");
			SKALA = feld(Display.class, "DATA_SCALE_ID");
			BILLBOARD = feld(Display.class, "DATA_BILLBOARD_RENDER_CONSTRAINTS_ID");
			HELL = feld(Display.class, "DATA_BRIGHTNESS_OVERRIDE_ID");
			SICHT = feld(Display.class, "DATA_VIEW_RANGE_ID");
			INTERPOL = feld(Display.class, "DATA_POS_ROT_INTERPOLATION_DURATION_ID");
			return true;
		} catch (ReflectiveOperationException e) {
			Wegpunkte.LOG.error("Schilder: Felder nicht gefunden – Schilder aus", e);
			TEXT = null;
			return false;
		}
	}

	static boolean geprueft = false, ok = false;

	/**
	 * Selbsttest beim Serverstart: alle Pakete einmal so verschlüsseln und wieder lesen, wie sie an echte Spieler
	 * gehen. Schlägt das fehl, bleiben die Schilder aus – sonst würden Spieler mit einem Netzwerkfehler rausfliegen.
	 */
	static void selbsttest(net.minecraft.server.MinecraftServer server) {
		geprueft = true;
		if (!bereit()) return;
		try {
			Display.TextDisplay ent = new Display.TextDisplay(EntityTypes.TEXT_DISPLAY, server.overworld());
			SynchedEntityData sd = ent.getEntityData();
			sd.set(BILLBOARD, (byte) 3);
			sd.set(FLAGS, (byte) (Display.TextDisplay.FLAG_SEE_THROUGH | Display.TextDisplay.FLAG_SHADOW));
			sd.set(HINTERGRUND, 0x60000000);
			sd.set(HELL, 15 << 4 | 15 << 20);
			sd.set(SICHT, 2.0f);
			sd.set(INTERPOL, 3);
			sd.set(SKALA, new Vector3f(1.5f, 1.5f, 1.5f));
			sd.set(TEXT, Component.literal("◆ ").withStyle(ChatFormatting.GOLD).append(Component.literal("Test\n12 m")));
			var buf = new net.minecraft.network.RegistryFriendlyByteBuf(io.netty.buffer.Unpooled.buffer(), server.registryAccess());
			var add = new ClientboundAddEntityPacket(ent.getId(), UUID.randomUUID(), 1, 2, 3, 0f, 0f, EntityTypes.TEXT_DISPLAY, 0, Vec3.ZERO, 0d);
			ClientboundAddEntityPacket.STREAM_CODEC.encode(buf, add);
			var add2 = ClientboundAddEntityPacket.STREAM_CODEC.decode(buf);
			var daten = new ClientboundSetEntityDataPacket(ent.getId(), sd.getNonDefaultValues());
			ClientboundSetEntityDataPacket.STREAM_CODEC.encode(buf, daten);
			var daten2 = ClientboundSetEntityDataPacket.STREAM_CODEC.decode(buf);
			var tp = ClientboundTeleportEntityPacket.teleport(ent.getId(), new PositionMoveRotation(new Vec3(4, 5, 6), Vec3.ZERO, 0f, 0f), Set.of(), false);
			ClientboundTeleportEntityPacket.STREAM_CODEC.encode(buf, tp);
			var tp2 = ClientboundTeleportEntityPacket.STREAM_CODEC.decode(buf);
			if (add2.getType() != EntityTypes.TEXT_DISPLAY || daten2.packedItems().size() != daten.packedItems().size()
				|| tp2.id() != ent.getId() || buf.readableBytes() != 0)
				throw new IllegalStateException("Pakete stimmen nach dem Lesen nicht");
			ok = true;
			Wegpunkte.LOG.info("Schilder-Selbsttest OK ({} Datenwerte)", daten2.packedItems().size());
		} catch (Exception e) {
			Wegpunkte.LOG.error("Schilder-Selbsttest fehlgeschlagen – Namensschilder bleiben aus", e);
		}
	}

	/** Alle Schilder des Spielers vergessen und beim Client entfernen (Join, Dimensionswechsel, Respawn). */
	static void zuruecksetzen(ServerPlayer p) {
		Map<String, Schild> m = schilder.remove(p.getUUID());
		if (m != null && !m.isEmpty() && p.connection != null)
			p.connection.send(new ClientboundRemoveEntitiesPacket(m.values().stream().mapToInt(s -> s.id).toArray()));
	}

	static void vergessen(UUID u) { schilder.remove(u); }

	static void aktualisieren(ServerPlayer p) {
		if (!ok || !bereit()) return;
		Map<String, Schild> m = schilder.computeIfAbsent(p.getUUID(), k -> new HashMap<>());
		String dim = p.level().dimension().identifier().toString();
		boolean an = !aus.contains(p.getUUID());

		// Weg mit Schildern gelöschter oder fremder Wegpunkte
		List<Integer> weg = new ArrayList<>();
		for (Iterator<Map.Entry<String, Schild>> it = m.entrySet().iterator(); it.hasNext(); ) {
			Map.Entry<String, Schild> e = it.next();
			Wegpunkte.Punkt w = Wegpunkte.punkte.get(e.getKey());
			if (!an || w == null || !w.dim.equals(dim)) { weg.add(e.getValue().id); it.remove(); }
		}
		if (!weg.isEmpty()) p.connection.send(new ClientboundRemoveEntitiesPacket(weg.stream().mapToInt(i -> i).toArray()));
		if (!an) return;

		Vec3 auge = p.getEyePosition();
		List<Wegpunkte.Punkt> l = new ArrayList<>();
		for (Wegpunkte.Punkt w : Wegpunkte.punkte.values()) if (w.dim.equals(dim)) l.add(w);
		l.sort(Comparator.comparingDouble(w -> ziel(w).distanceToSqr(auge)));
		List<Vec3> richtungen = new ArrayList<>();
		List<Integer> stufen = new ArrayList<>();

		for (Wegpunkte.Punkt w : l) {
			Vec3 z = ziel(w);
			Vec3 d = z.subtract(auge);
			double dist = d.length();
			Vec3 r = dist < 1e-3 ? new Vec3(0, 1, 0) : d.scale(1 / dist);
			double abstand = Math.min(dist, WEIT);
			float groesse = (float) Math.max(0.5, abstand * 0.07);
			// Schilder in fast gleicher Richtung übereinander stapeln
			int stufe = 0;
			for (int i = 0; i < richtungen.size(); i++)
				if (richtungen.get(i).dot(r) > 0.9985 && stufen.get(i) >= stufe) stufe = stufen.get(i) + 1;
			richtungen.add(r); stufen.add(stufe);
			Vec3 pos = auge.add(r.scale(abstand)).add(0, stufe * groesse * 0.55, 0);
			if (dist <= WEIT) pos = z.add(0, stufe * groesse * 0.55, 0);

			String text = w.name + "\n" + entfernung(w.mitte().distanceTo(p.position()));
			Schild s = m.get(w.id);
			if (s == null) {
				Display.TextDisplay ent = new Display.TextDisplay(EntityTypes.TEXT_DISPLAY, p.level());
				s = new Schild(ent);
				s.pos = pos;
				SynchedEntityData sd = ent.getEntityData();
				sd.set(BILLBOARD, (byte) 3);                                   // immer zum Spieler gedreht
				sd.set(FLAGS, (byte) (Display.TextDisplay.FLAG_SEE_THROUGH | Display.TextDisplay.FLAG_SHADOW));
				sd.set(HINTERGRUND, 0x60000000);
				sd.set(HELL, 15 << 4 | 15 << 20);                               // volle Helligkeit
				sd.set(SICHT, 2.0f);
				sd.set(INTERPOL, 3);                                            // weich nachziehen
				sd.set(SKALA, new Vector3f(groesse, groesse, groesse));
				sd.set(TEXT, anzeige(w, text));
				s.text = text; s.groesse = groesse;
				p.connection.send(new ClientboundAddEntityPacket(s.id, UUID.randomUUID(), pos.x, pos.y, pos.z, 0f, 0f,
					EntityTypes.TEXT_DISPLAY, 0, Vec3.ZERO, 0d));
				List<SynchedEntityData.DataValue<?>> werte = sd.getNonDefaultValues();
				if (werte != null) p.connection.send(new ClientboundSetEntityDataPacket(s.id, werte));
				sd.packDirty();
				m.put(w.id, s);
				continue;
			}
			SynchedEntityData sd = s.ent.getEntityData();
			if (!text.equals(s.text)) { sd.set(TEXT, anzeige(w, text)); s.text = text; }
			if (Math.abs(groesse - s.groesse) > 0.02f) { sd.set(SKALA, new Vector3f(groesse, groesse, groesse)); s.groesse = groesse; }
			List<SynchedEntityData.DataValue<?>> neu = sd.packDirty();
			if (neu != null && !neu.isEmpty()) p.connection.send(new ClientboundSetEntityDataPacket(s.id, neu));
			if (s.pos.distanceToSqr(pos) > 0.0025) {
				s.pos = pos;
				p.connection.send(ClientboundTeleportEntityPacket.teleport(s.id,
					new PositionMoveRotation(pos, Vec3.ZERO, 0f, 0f), Set.of(), false));
			}
		}
	}

	static Vec3 ziel(Wegpunkte.Punkt w) { return new Vec3(w.x + 0.5, w.y + NAH_HOEHE, w.z + 0.5); }

	static Component anzeige(Wegpunkte.Punkt w, String text) {
		String[] t = text.split("\n", 2);
		return Component.literal("◆ ").withStyle(w.farbeEnum().chat)
			.append(Component.literal(t[0]).withStyle(s -> s.withColor(w.farbeEnum().rgb).withBold(true)))
			.append(Component.literal("\n" + t[1]).withStyle(ChatFormatting.GRAY));
	}

	static String entfernung(double m) {
		if (m < 1000) return Math.round(m) + " m";
		return String.format(Locale.GERMANY, "%.1f km", m / 1000);
	}
}
