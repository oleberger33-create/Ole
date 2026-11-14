package de.ole.wegpunkte;

import net.minecraft.network.protocol.game.ClientboundSetEntityDataPacket;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;

import java.lang.reflect.Field;
import java.util.*;

/**
 * Spieler durch Wände sehen (Leuchtrand wie beim Leuchten-Effekt), für jeden Zuschauer einzeln: Der Server schickt
 * jedem Spieler, der ESP an hat, die Status-Bits der anderen Spieler mit gesetztem „leuchtet“-Bit. Nur er sieht das
 * Leuchten. Ändert sich der echte Status (Schleichen, Sprinten …), schickt der Server ihn ohne Leuchten – das wird
 * spätestens nach 2 Ticks wieder überschrieben. /esp off schaltet es für einen selbst aus.
 */
final class Esp {
	static final byte LEUCHTEN = 1 << 6;
	static final Set<UUID> aus = new HashSet<>();
	/** Zuschauer → (Ziel-Entity-ID → zuletzt geschickter Status) */
	static final Map<UUID, Map<Integer, Byte>> gesendet = new HashMap<>();
	static EntityDataAccessor<Byte> FLAGS;

	@SuppressWarnings("unchecked")
	static boolean bereit() {
		if (FLAGS != null) return true;
		try {
			Field f = Entity.class.getDeclaredField("DATA_SHARED_FLAGS_ID");
			f.setAccessible(true);
			FLAGS = (EntityDataAccessor<Byte>) f.get(null);
			return true;
		} catch (ReflectiveOperationException e) {
			Wegpunkte.LOG.error("ESP: Feld nicht gefunden – ESP aus", e);
			return false;
		}
	}

	static boolean an(ServerPlayer p) { return !aus.contains(p.getUUID()); }

	static void vergessen(UUID u) { gesendet.remove(u); }

	/** Jeden 2. Tick: allen Zuschauern mit ESP die anderen Spieler leuchtend schicken (nur bei Änderung, sonst alle 10 Ticks). */
	static void tick(MinecraftServer server, int tick) {
		if (!bereit()) return;
		boolean auffrischen = tick % 10 == 0;
		List<ServerPlayer> alle = server.getPlayerList().getPlayers();
		for (ServerPlayer v : alle) {
			if (!an(v)) continue;
			Map<Integer, Byte> m = gesendet.computeIfAbsent(v.getUUID(), k -> new HashMap<>());
			for (ServerPlayer z : alle) {
				if (z == v || z.level() != v.level() || z.isSpectator()) continue;
				byte soll = (byte) (z.getEntityData().get(FLAGS) | LEUCHTEN);
				Byte alt = m.get(z.getId());
				if (!auffrischen && alt != null && alt == soll) continue;
				senden(v, z, soll);
				m.put(z.getId(), soll);
			}
		}
	}

	static void senden(ServerPlayer an, ServerPlayer ziel, byte wert) {
		an.connection.send(new ClientboundSetEntityDataPacket(ziel.getId(),
			List.of(SynchedEntityData.DataValue.create(FLAGS, wert))));
	}

	/** ESP aus: allen Spielern wieder den echten Status schicken. */
	static void ausschalten(MinecraftServer server, ServerPlayer v) {
		aus.add(v.getUUID());
		gesendet.remove(v.getUUID());
		if (!bereit()) return;
		for (ServerPlayer z : server.getPlayerList().getPlayers())
			if (z != v && z.level() == v.level()) senden(v, z, z.getEntityData().get(FLAGS));
	}

	static void einschalten(ServerPlayer v) {
		aus.remove(v.getUUID());
		gesendet.remove(v.getUUID());
	}
}
