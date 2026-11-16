package de.ole.tpa.mixin;

import de.ole.tpa.BedrockChat;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Jede System-Nachricht an einen Spieler (auch /tellraw aus Datapacks) – für Bedrock-Fenster mit Knöpfen. */
@Mixin(ServerPlayer.class)
public class ServerPlayerMixin {
	@Inject(method = "sendSystemMessage(Lnet/minecraft/network/chat/Component;Z)V", at = @At("HEAD"))
	private void tpa$nachricht(Component nachricht, boolean actionbar, CallbackInfo ci) {
		if (!actionbar) BedrockChat.nachricht((ServerPlayer) (Object) this, nachricht);
	}
}
