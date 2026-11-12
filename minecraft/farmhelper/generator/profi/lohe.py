"""Lohenfarm am Spawner (Profi): Die Lohen spawnen in einem eingemauerten Schacht 7 × 7 um den Spawner, sinken
(ohne Ziel) 7 Blöcke tief auf einen Boden mit fließender Lava. Lava aus den 4 Ecken fließt zur Mitte und schiebt die
Lohen dorthin (Java: fließende Lava schiebt Mobs, im Nether 7 Blöcke weit); in der Mitte hält ein Wandschild die Lava,
die Lohen fallen hindurch in eine Rutsche 1 × 1 und landen in einer Zelle auf Schlamm. Du stehst 2 Blöcke daneben auf
der Truhe: Dazwischen liegt ein Spalt (Schlamm unten, obere Stufe oben, 5/8 hoch) – du triffst ihre Beine, sie sehen
dich nicht. Beute: Schlamm → Trichter → Truhe; XP rollt durch den Spalt zu dir.

Spawner (0, 0, 0). Schacht innen x/z -3 … 3, y -7 … 2; Rand/Wände x/z ±4, y -7 … 2; Boden y -8 (9 × 9, Mitte Schild);
Decke y 3 (9 × 9); Block auf dem Spawner (0, 1, 0). Lava-Quellen (±3, -7, ±3). Rutsche (0, -12 … -9, 0), Zelle
(0, -14, 0) Schlamm; Zwischenfeld (0, -14, 1) Schlamm, (0, -13, 1) obere Stufe, (0, -12, 1) Block; Platz (0, -14, 2) auf
der Truhe (0, -15, 2); Trichter (0, -15, 0) und (0, -15, 1) nach Süden. Tür: (0, -14, 3) und (0, -13, 3).
"""
from profi_basis import *

f = profi("lohe", dict(
    name="Lohenfarm am Spawner (Profi)", diff=4, out="Lohenruten, viel XP",
    where="Lohen-Spawner in einer Netherfestung; um ihn 9 × 9 und bis 15 Blöcke darunter muss Platz werden",
    afk="Halb – du stehst sicher an der Tötungskammer und schlägst ab und zu zu, die Lohen kommen von selbst",
    why="In der einfachen Farm kämpfst du im Raum gegen die Lohen, und sobald 6 Lohen um den Spawner schweben, macht er "
        "Pause. Hier bleibt keine Lohe in seiner Nähe, und du stehst geschützt: Der Spawner hängt frei in einem "
        "Schacht 7 × 7, der 7 Blöcke unter ihm auf einem Boden aus fließender Lava endet. Lohen ohne Ziel sinken "
        "langsam – sie landen in der Lava (Lava, Feuer und Fallen tun ihnen nichts). Die Lava kommt aus den 4 Ecken "
        "und fließt im Nether bis zur Mitte; fließende Lava schiebt Mobs, also landen alle Lohen in der Mitte. Dort "
        "hängt im Boden ein Wandschild: Lava fließt nicht hinein, die Lohen fallen aber hindurch – eine Rutsche "
        "1 × 1 hinunter in eine Zelle auf Schlamm. Du stehst 2 Blöcke daneben auf der Truhe, schräg unter dem "
        "Spawner und knapp 15 Blöcke von ihm entfernt (näher als 16 muss es sein, sonst ruht er). Zwischen dir und der Zelle ist nur ein Spalt "
        "5/8 Block hoch (unten Schlamm, oben eine obere Stufe): Du siehst und triffst die Beine der Lohen, sie "
        "sehen dich nicht – keine Feuerbälle, kein Nahkampf. Mit Schwungkraft triffst du alle in der Zelle auf "
        "einmal. Lohenruten fallen auf den Schlamm, die Trichter darunter bringen sie in die Truhe; die XP-Kugeln "
        "rollen durch den Spalt zu dir. Die Lava liegt 7 Blöcke unter dem Spawner, so bleibt es dort, wo Lohen "
        "spawnen, dunkel genug (Licht höchstens 9, erlaubt sind 11).",
    help=[["Es kommen keine Lohen",
           "Du musst auf der Truhe stehen (knapp 15 Blöcke vom Spawner, mehr als 16 geht nicht). Im Schacht kein "
           "Licht außer der Lava (keine Fackeln). Die Lava muss 7 Blöcke unter dem Spawner liegen – höher wird es "
           "zu hell."],
          ["Lohen bleiben auf der Lava liegen",
           "Lava nur in die 4 inneren Ecken, sie fließt bis zur Mitte (dort ganz flach). Das Loch in der Mitte "
           "braucht ein Wandschild (kein Block, keine Falltür) und darunter freie Rutsche. Ein Block muss auf dem "
           "Spawner liegen, sonst bleiben Lohen oben auf ihm stehen."],
          ["Feuerbälle treffen dich",
           "Zwischen dir und der Zelle: unten Schlamm, darüber eine OBERE Stufe und darüber ein Block. Ist der Spalt "
           "höher, sehen dich die Lohen. Zum Bauen Trank der Feuerresistenz trinken."],
          ["Lohen sterben ohne Ruten",
           "Mehr als 24 Lohen in einer Zelle erdrücken sich gegenseitig – dann gibt es weder Ruten noch XP. Alle "
           "paar Minuten zuschlagen; Ruten gibt es nur, wenn du triffst."]],
    meta=m("Rate: Schätzung – der Spawner versucht alle 10–40 Sekunden 4 Lohen zu setzen; weil keine Lohe bei ihm "
           "bleibt, macht er nie Pause: bis etwa 300–400 Lohen pro Stunde, wenn du oft genug zuschlägst. Eine Lohe "
           "gibt 0–1 Rute (mit Plünderung III 0–4) und 10 XP. Die einfache Farm stoppt bei 6 Lohen im Raum (im "
           "Test 6) – du musst jede einzeln im Kampf erwischen.",
           [("Am Lohen-Spawner einer Netherfestung. Ab 1.16 bauen Java-Farmen den Sammler aus fließender Lava, weil "
             "sie feuerfeste Mobs schiebt.", W + "Tutorial:Blaze_farming")],
           [("Spawner: setzt Lohen in einem Bereich 9 × 3 × 9 (eine Ebene unter bis eine über ihm), auch in der Luft; "
             "nur wenn ein Spieler höchstens 16 Blöcke entfernt ist; Pause, wenn 6 Lohen im Würfel 9 × 9 × 9 um ihn "
             "sind; Lohen brauchen Licht ≤ 11 (12 schaltet ihn ab).", W + "Monster_Spawner"),
            ("Lohen ohne Ziel sinken langsam; hoch fliegen sie nur, wenn ihr Ziel höher ist. Feuer, Lava und Fallen "
             "schaden ihnen nicht. Nah- und Fernangriff brauchen Sicht auf das Ziel. Ruten nur, wenn ein Spieler "
             "tötet.", W + "Blaze"),
            ("Fließende Lava schiebt Wesen, auch feuerfeste; im Nether fließt sie 7 Blöcke weit.", W + "Lava"),
            ("Schilder werden von Wasser und Lava nicht zerstört und halten sie auf; sie haben keine Kollision, "
             "Mobs und Items gehen hindurch. Schilder brennen nicht.", W + "Sign"),
            (TEST + "Trichter saugen Items durch Schlamm hindurch auf; ein Schild im Loch hält Wasser, Mobs sinken "
             "hindurch (Ertrunkenen-Farm).", None)])))

f.zeichen(Q="spawner", N="nether_bricks", M="mud", O=("slab", {"half": "top"}), s=("wall_sign", "e"))


def zellen(punkte, zeichen):
    return {p: zeichen for p in punkte}


INNEN = [(x, z) for x in range(-3, 4) for z in range(-3, 4)]                       # Schacht 7 × 7
RING = [(x, z) for x in range(-4, 5) for z in range(-4, 5) if max(abs(x), abs(z)) == 4]   # Rand 9 × 9
ALLE = [(x, z) for x in range(-4, 5) for z in range(-4, 5)]


def ebene(zellen_dict):
    return raster_aus(zellen_dict, -4, -4, 4, 4)


# 1 – Freimachen
frei = {y: ebene(zellen([p for p in INNEN if not (y == 0 and p == (0, 0))], "-")) for y in range(-7, 3)}
frei[0] = ebene(zellen([p for p in INNEN if p != (0, 0)], "-") | {(0, 0): "Q"})      # Spawner bleibt
frei[1] = ebene(zellen([p for p in INNEN if p != (0, 0)], "-") | {(0, 0): "N"})      # Block auf dem Spawner
frei[-8] = ebene({(0, 0): "-"})
for y in range(-13, -8):
    frei[y] = ebene({(0, 0): "-"})
frei[-14] = ebene({(0, 2): "-"})
frei[-13] = ebene({(0, 0): "-", (0, 2): "-"})
f.schritt("Als Erstes, noch vom Boden neben dem Spawner aus: einen Block oben auf den Spawner setzen – sonst bleiben "
          "später Lohen darauf stehen. Trank der Feuerresistenz trinken: Solange du baust, kommen Lohen. Dann den "
          "Schacht um den Spawner freimachen: innen 7 × 7, von 7 Blöcken unter dem Spawner bis 2 darüber; der Spawner "
          "bleibt in der Luft hängen. Darunter mittig eine Rutsche 1 × 1 bis 13 Blöcke unter dem Spawner ausgraben "
          "und ganz unten, 2 Blöcke südlich davon, deinen Platz (2 hoch).", frei, x0=-4, z0=-4)

# 2 – Kammer unten
f.schritt("Kammer ganz unten (15 Blöcke unter dem Spawner): zuerst die Truhe unter deinen späteren Platz, dann zwei "
          "Trichter nach Norden davor – schleichend an die Truhe bzw. an den Trichter klicken (ein Trichter zeigt in den "
          "Block, an den du klickst): Beide zeigen nach Süden zur Truhe. Ist rundherum nichts zum Anklicken, erst "
          "einen Hilfsblock setzen und später abbauen.", {
    -15: "v\nv\nC"}, z0=0)
f.schritt("Schlamm (Wasserflasche auf Erde) auf beide Trichter – Trichter saugen durch Schlamm. Rundherum Wände, "
          "2 hoch. Die beiden Wandblöcke südlich von deinem Platz sind deine Tür: zum Hinein- und Hinausgehen "
          "abbauen und hinter dir wieder setzen (den Weg hierher baust du, wie es passt). Auf den nördlichen "
          "Schlamm kommen die Lohen.", {
    -14: """
        .N.
        NMN
        NMN
        N.N
        .N.
    """,
    -13: """
        .N.
        N.N
        N.N
        N.N
        .N.
    """}, x0=-1, z0=-1)
f.schritt("Eine OBERE Stufe über den südlichen Schlamm (an die obere Hälfte eines Wandblocks daneben klicken). "
          "Zwischen Schlamm und Stufe bleibt ein Spalt 5/8 Block hoch: Durch ihn triffst du die Beine der Lohen, "
          "sehen können sie dich nicht.", {-13: "O"}, z0=1)
f.schritt("Über die Stufe einen Block, über deinen Platz und die Tür die Decke, und die Wände der Rutsche 1 × 1 "
          "nach oben bis 9 Blöcke unter den Spawner – direkt darüber kommt der Boden.", {
    -12: """
        .N.
        N.N
        .N.
        .N.
        .N.
    """,
    **{y: """
        .N.
        N.N
        .N.
    """ for y in range(-11, -8)}}, x0=-1, z0=-1)

# 3 – Lavaboden
boden = zellen([p for p in ALLE if p != (0, 0)], "N")
boden[(0, 0)] = "s"
f.schritt("Boden 9 × 9 aus Netherziegeln, 8 Blöcke unter dem Spawner – von der Rutsche aus nach außen bauen. Über der "
          "Rutsche bleibt ein Loch. In dieses Loch ein Wandschild (am besten Karmesin oder Wirr – brennt nicht): an "
          "die Ostseite des Blocks westlich vom Loch klicken. Lava fließt nicht in Schilder, Lohen fallen hindurch.", {
    -8: ebene(boden)}, x0=-4, z0=-4)
rand = zellen(RING, "N")
rand.update({(-3, -3): "L", (3, -3): "L", (-3, 3): "L", (3, 3): "L"})
f.schritt("Rand 1 hoch rund um den Boden – das ist die Lavaschicht. Dann, auf dem Rand stehend, je einen Eimer Lava "
          "in die 4 inneren Ecken (auf den Boden klicken): Im Nether fließt sie 7 Blöcke weit, bedeckt den ganzen "
          "Boden und wird zur Mitte hin flacher. Dorthin schiebt sie die Lohen.", {
    -7: ebene(rand)}, x0=-4, z0=-4)

# 4 – Wände, Decke
f.schritt("Wände aus Netherziegeln auf den Rand, 9 Ringe übereinander bis 2 Blöcke über den Spawner (was von der Festung "
          "schon steht, bleibt). Lohen spawnen bis eine Ebene über dem Spawner und sind 1,8 hoch.", {
    y: ebene(zellen(RING, "N")) for y in range(-6, 3)}, x0=-4, z0=-4)
f.schritt("Decke 9 × 9 drei Blöcke über dem Spawner, auf die Wände gesetzt – von außen bauen. Im Schacht darf nichts "
          "leuchten außer der Lava, und die Lohen fliegen so nicht hinaus.", {
    3: ebene(zellen(ALLE, "N"))}, x0=-4, z0=-4)

# 5 – Platz
f.schritt("Dein Platz: auf der Truhe stehen (knapp 15 Blöcke vom Spawner). Durch den Spalt siehst du die Beine der "
          "Lohen in der Zelle – mit Schwungkraft und Plünderung zuschlagen, alle paar Minuten. Die Truhe unter dir "
          "kannst du öffnen.", {-14: "P"}, z0=2)

# Test: wie die einfache Farm im Netherziegel-Block, aber im Nether (fließende Lava schiebt dort stärker). Gemessen
# werden die Lohen in Zelle und Rutsche – die einfache kommt auf höchstens 6 im ganzen Raum.
ZELLE = [0, -14, 0, 0, -8, 0]
UMGEBUNG = dict(dimension="the_nether", hoehe=70, boden="minecraft:nether_bricks",
                fuellung="minecraft:nether_bricks", erde_bis=4, zeit="day")
f.pruefe(**UMGEBUNG,
         nachher=['setblock {x} {y} {z} minecraft:spawner{SpawnData:{entity:{id:"minecraft:blaze"}}}'],
         bereich=ZELLE, erwartet={"wesen": {"minecraft:blaze": 10}})
# Mechanik allein (ohne Spawner): Lohen auf den Lava-Ecken müssen zur Mitte geschoben werden und in die Zelle fallen.
f.pruefe_auch("lohe_profi_mech", **UMGEBUNG,
              nachher=mobs("blaze", [(-3, -7, -3), (3, -7, -3), (-3, -7, 3), (3, -7, 3)]),
              bereich=ZELLE, erwartet={"wesen": {"minecraft:blaze": 3}})
