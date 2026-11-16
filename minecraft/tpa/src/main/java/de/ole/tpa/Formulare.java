package de.ole.tpa;

import net.minecraft.server.level.ServerPlayer;
import org.geysermc.cumulus.form.ModalForm;
import org.geysermc.cumulus.form.SimpleForm;
import org.geysermc.floodgate.api.FloodgateApi;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/** Fenster für Bedrock-Spieler (Floodgate/Cumulus). Antworten kommen aus dem Netzwerk-Thread → zurück auf den Server-Thread. */
final class Formulare {
	private Formulare() {}

	static boolean istFloodgate(UUID u) { return FloodgateApi.getInstance().isFloodgatePlayer(u); }

	static void senden(ServerPlayer p, Object form) {
		if (form instanceof SimpleForm f) FloodgateApi.getInstance().sendForm(p.getUUID(), f);
		else if (form instanceof ModalForm f) FloodgateApi.getInstance().sendForm(p.getUUID(), f);
	}

	static void aufServer(Runnable r) { Tpa.server.execute(r); }

	static ServerPlayer online(UUID u) { return Tpa.server.getPlayerList().getPlayer(u); }

	static void befehl(ServerPlayer p, String befehl) {
		Tpa.server.getCommands().performPrefixedCommand(p.createCommandSourceStack(), befehl);
	}

	/** Fenster aus anklickbaren Chat-Nachrichten: Knopf = Befehl, als der Spieler ausgeführt. */
	static void knopfFenster(ServerPlayer p, String text, List<BedrockChat.Knopf> knoepfe) {
		UUID u = p.getUUID();
		List<BedrockChat.Knopf> l = new ArrayList<>(knoepfe);
		String inhalt = text.length() > 900 ? text.substring(text.length() - 900) : text;
		SimpleForm.Builder b = SimpleForm.builder().title("OLE SMP").content(inhalt);
		for (BedrockChat.Knopf k : l) b.button(k.text());
		senden(p, b.validResultHandler(r -> aufServer(() -> {
			ServerPlayer q = online(u);
			int i = r.clickedButtonId();
			if (q == null || i < 0 || i >= l.size()) return;
			String befehl = l.get(i).befehl();
			befehl(q, befehl.startsWith("/") ? befehl.substring(1) : befehl);
		})).build());
	}

	static void hauptmenue(ServerPlayer p) {
		UUID u = p.getUUID();
		senden(p, SimpleForm.builder()
			.title("OLE SMP")
			.content("Was möchtest du tun?")
			.button("Teleport-Ziele")
			.button("Zu einem Spieler teleportieren")
			.button("Einen Spieler zu mir holen")
			.button("Lager öffnen")
			.button("Tresor öffnen")
			.validResultHandler(r -> aufServer(() -> {
				ServerPlayer q = online(u);
				if (q == null) return;
				switch (r.clickedButtonId()) {
					case 0 -> { TpMenu.laden(); ziele(q); }
					case 1 -> spielerWahl(q, false);
					case 2 -> spielerWahl(q, true);
					case 3 -> befehl(q, "lager oeffnen");
					case 4 -> befehl(q, "tresor");
					default -> {}
				}
			}))
			.build());
	}

	static void ziele(ServerPlayer p) {
		UUID u = p.getUUID();
		List<TpMenu.Ziel> liste = new ArrayList<>(TpMenu.ziele);
		SimpleForm.Builder b = SimpleForm.builder().title("Teleport").content("Wohin möchtest du?");
		for (TpMenu.Ziel z : liste) b.button(z.name());
		senden(p, b.validResultHandler(r -> aufServer(() -> {
			ServerPlayer q = online(u);
			int i = r.clickedButtonId();
			if (q != null && i >= 0 && i < liste.size()) TpMenu.hinreisen(q, liste.get(i));
		})).build());
	}

	static void spielerWahl(ServerPlayer p, boolean hier) {
		UUID u = p.getUUID();
		List<UUID> andere = new ArrayList<>();
		SimpleForm.Builder b = SimpleForm.builder().title(hier ? "Spieler zu mir holen" : "Zu Spieler teleportieren")
			.content(hier ? "Wen möchtest du zu dir holen?" : "Zu wem möchtest du?");
		for (ServerPlayer o : Tpa.server.getPlayerList().getPlayers()) {
			if (o == p) continue;
			andere.add(o.getUUID());
			b.button(o.getPlainTextName());
		}
		if (andere.isEmpty()) { Tpa.fehler(p, "Gerade ist niemand anderes online."); return; }
		senden(p, b.validResultHandler(r -> aufServer(() -> {
			ServerPlayer q = online(u);
			int i = r.clickedButtonId();
			if (q == null || i < 0 || i >= andere.size()) return;
			ServerPlayer ziel = online(andere.get(i));
			if (ziel == null) { Tpa.fehler(q, "Der Spieler ist nicht mehr online."); return; }
			Tpa.fragen(q, ziel, hier);
		})).build());
	}

	static void anfrage(ServerPlayer ziel, ServerPlayer fragender, boolean hier) {
		UUID z = ziel.getUUID(), f = fragender.getUUID();
		String name = fragender.getPlainTextName();
		senden(ziel, ModalForm.builder()
			.title("Teleport-Anfrage")
			.content(hier ? name + " möchte, dass du zu " + name + " kommst." : name + " möchte sich zu dir teleportieren.")
			.button1("Annehmen")
			.button2("Ablehnen")
			.validResultHandler(r -> aufServer(() -> {
				ServerPlayer q = online(z);
				if (q != null) Tpa.antworten(q, online(f), r.clickedFirst());
			}))
			.build());
	}
}
