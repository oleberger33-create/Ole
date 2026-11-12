"""Testet Farm-Pläne auf einem lokalen Minecraft-Server (26.3, Fabric + Carpet, RCON).

Aufruf:  python3 mctest.py <plaene.json> <tests.json> [farm-id ...] [--ticks=N] [--zufall=N] [--behalten]
         (ohne --behalten werden vorher alle dauerhaft geladenen Chunks entladen und alle Wesen entfernt –
          Mobs alter Testorte füllen sonst das Monster-Limit und nichts spawnt mehr)

Für jede Farm:
- Ort vorbereiten (Dimension, Biom, Bauwerk, eigene Befehle aus tests.json),
- Plan aufbauen wie ein Spieler: Schritt für Schritt, je Schritt feste Blöcke von unten nach oben, Flüssigkeiten zuletzt,
  dann Lebewesen und Behälter-Inhalte,
- Testspieler (Carpet) auf den AFK-Platz stellen,
- Zeit laufen lassen (/tick sprint), dann messen: Items in Behältern, Items am Boden, Blöcke, Wesen, Spieler-Inventar.
  Erwartung "*" zählt alle Sorten zusammen (z. B. {"items": {"*": 1}}: irgendeine Beute), "a|b" zählt a und b.

tests.json: {"<farm>": {"dimension": "overworld|the_nether|the_end", "biom": "minecraft:…", "zeit": "day|night|cycle",
             "bauwerk": {"id": "minecraft:swamp_hut", "anker": [x, y, z]},
             "boden": "minecraft:grass_block",   (Erdboden unter y 0 nachbilden; ohne Angabe: alles Luft)
             "vorher": ["<Befehl mit {x} {y} {z} = Plan-Ursprung, auch {x+2} {z-1} …>", …], "nachher": […],
             "hoechstens": {"boden": {"minecraft:glass_bottle": 0}},   (items = in Behältern/Loren, boden = Items am Boden)
             "erwartet": {"items": {"minecraft:iron_ingot": 1}, "bloecke": {"minecraft:lava_cauldron": 1},
                          "wesen": {"minecraft:iron_golem": 1}, "inventar": {"minecraft:cod": 1}},
             "spieler": {"hand": "minecraft:fishing_rod", "aktion": "use continuous"},
             "behaelter": [[dx, dy, dz], …]}}   (weitere Behälter zählen, z. B. einen nur im Test gesetzten Werfer)
"""
import json, os, re, socket, struct, sys, time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'generator'))
import bloecke  # noqa: E402

LOG = os.environ.get('MC_LOG', '')
DIM = {'overworld': 'minecraft:overworld', 'the_nether': 'minecraft:the_nether', 'the_end': 'minecraft:the_end'}
BEHAELTER = {'chest', 'barrel', 'hopper', 'dispenser', 'dropper', 'trapped_chest'}


class Rcon:
    def __init__(self, host='127.0.0.1', port=int(os.environ.get('MC_RCON_PORT', 25575)), pw='test'):
        self.s = socket.create_connection((host, port), timeout=120)
        self.s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.n = 0
        self._send(3, pw)
        self._recv()

    def _send(self, typ, text):
        self.n += 1
        data = struct.pack('<ii', self.n, typ) + text.encode('utf-8') + b'\x00\x00'
        self.s.sendall(struct.pack('<i', len(data)) + data)
        return self.n

    def _recv(self):
        kopf = b''
        while len(kopf) < 4:
            teil = self.s.recv(4 - len(kopf))
            if not teil:
                raise ConnectionError('RCON-Verbindung vom Server geschlossen')
            kopf += teil
        laenge = struct.unpack('<i', kopf)[0]
        daten = b''
        while len(daten) < laenge:
            teil = self.s.recv(laenge - len(daten))
            if not teil:
                raise ConnectionError('RCON-Verbindung vom Server geschlossen')
            daten += teil
        rid, typ = struct.unpack('<ii', daten[:8])
        return rid, daten[8:-2]

    def __call__(self, befehl):
        """Befehl senden und Antwort lesen. Der Server liest pro Paket genau einmal vom Socket – kommen zwei Pakete
        zusammen an, trennt er die Verbindung. Darum nur ein Paket auf einmal; lange Antworten kommen in Stücken zu
        4096 Bytes, ein kürzeres Stück ist das letzte."""
        rid = self._send(2, befehl)
        teile = []
        while True:
            r, roh = self._recv()
            if r != rid:
                continue
            teile.append(roh.decode('utf-8', 'replace'))
            if len(teile[-1]) < 4096:           # der Server teilt nach Zeichen, nicht nach Bytes
                break
        return ''.join(teile)


def blockzustand(b):
    """Echter Block (mit Eigenschaften) für einen Plan-Block, oder None für Lebewesen/Inhalt/AFK."""
    i = b['id']
    if i == 'water':
        return 'minecraft:water'
    if i == 'lava':
        return 'minecraft:lava'
    if i == 'flowing_water':
        return None
    if i in ('luft',):
        return 'minecraft:air'
    if i in ('snow', 'melon', 'pumpkin'):
        return None
    if i == 'spawner':
        return None              # Spawner setzt die Vorbereitung (Mob-Typ kommt aus tests.json)
    d = bloecke.block(b, 0)
    if d is None or d.get('art') != 'block':
        return None
    props = ','.join(f'{k}={v}' for k, v in d.get('props', {}).items())
    return f"minecraft:{d['anzeige']}" + (f'[{props}]' if props else '')


LEITER = {'stone_bricks', 'stone', 'cobblestone', 'smooth_stone', 'dirt', 'grass_block', 'sand', 'netherrack',
          'nether_bricks', 'end_stone', 'obsidian', 'oak_planks', 'hay_block', 'white_wool', 'dispenser', 'mud',
          'farmland', 'magma', 'soul_sand', 'bookshelf', 'composter', 'dripstone_block', 'fletching_table'}
QUELLE = {'lever', 'stone_button', 'daylight_detector', 'daylight_detector_inv', 'comparator'}
TRAEGT = LEITER | {'glass', 'observer', 'piston', 'sticky_piston', 'sea_lantern', 'glowstone', 'chest'}


def staub_form(plan, pos):
    """redstone_wire-Zustand wie nach dem Setzen durch einen Spieler (Java-Regeln für Verbindungen)."""
    x, y, z = pos
    def bid(q):
        b = plan.get(q)
        return b['id'] if b else None
    def leiter(q):
        return bid(q) in LEITER
    oben_frei = not leiter((x, y + 1, z))
    seiten = {}
    for name, (dx, dz) in {'north': (0, -1), 'south': (0, 1), 'east': (1, 0), 'west': (-1, 0)}.items():
        n = (x + dx, y, z + dz)
        nb = plan.get(n)
        art = 'none'
        if oben_frei and bid(n) in TRAEGT and bid((n[0], y + 1, n[2])) == 'redstone':
            art = 'up'
        elif nb and (nb['id'] == 'redstone' or nb['id'] in QUELLE or
                     (nb['id'] == 'observer' and nb.get('p', {}).get('f') == {'north': 'n', 'south': 's',
                                                                             'east': 'e', 'west': 'w'}[name]) or
                     (nb['id'] == 'repeater' and nb.get('p', {}).get('f') in ({'north': 'n', 'south': 's'}
                      if name in ('north', 'south') else {'east': 'e', 'west': 'w'}).values())):
            art = 'side'
        elif not leiter(n) and bid((n[0], y - 1, n[2])) == 'redstone':
            art = 'side'
        seiten[name] = art
    n_, s_, e_, w_ = (seiten[k] != 'none' for k in ('north', 'south', 'east', 'west'))
    if not n_ and not s_:
        if not w_: seiten['west'] = 'side'
        if not e_: seiten['east'] = 'side'
    if not e_ and not w_:
        if not n_: seiten['north'] = 'side'
        if not s_: seiten['south'] = 'side'
    return 'minecraft:redstone_wire[' + ','.join(f'{k}={v}' for k, v in seiten.items()) + ']'


class Test:
    def __init__(self, rcon, farm, test, ursprung):
        self.r, self.f, self.t = rcon, farm, test
        self.x, self.y, self.z = ursprung
        self.dim = DIM[test.get('dimension', 'overworld')]
        self.meld = []

    def cmd(self, befehl):
        aus = self.r(f'execute in {self.dim} run {befehl}')
        if befehl.startswith('kill ') and 'No entity was found' in aus:
            return aus
        if any(w in aus for w in ('Unknown', 'Incorrect', 'Expected', 'Invalid', 'Could not', 'not loaded',
                                  'No entity', 'Failed')):
            self.meld.append(f'{befehl[:120]} -> {aus[:160]}')
        return aus

    def p(self, b):
        return self.x + b['x'], self.y + b['y'], self.z + b['z']

    def box(self, rand=2):
        bl = self.f['fertig'] + [q for st in self.f['steps'] for q in st.get('luft', [])]   # auch Aushub
        xs = [b['x'] for b in bl]; ys = [b['y'] for b in bl]; zs = [b['z'] for b in bl]
        return (self.x + min(xs) - rand, self.y + min(ys) - rand, self.z + min(zs) - rand,
                self.x + max(xs) + rand, self.y + max(ys) + rand, self.z + max(zs) + rand)

    def ersetze(self, befehl):
        basis = {'x': self.x, 'y': self.y, 'z': self.z}
        return re.sub(r'\{([xyz])([+-]\d+)?\}', lambda m: str(basis[m.group(1)] + int(m.group(2) or 0)), befehl)

    def finde(self, bw, x=None, z=None):
        x = self.x if x is None else x
        z = self.z if z is None else z
        a = self.r(f'execute in {self.dim} positioned {x} {self.y} {z} run locate structure {bw["id"]}')
        m = re.search(r'\[(-?\d+), (~|-?\d+), (-?\d+)\]', a)
        if not m:
            self.meld.append(f'locate {bw["id"]}: {a[:120]}')
            return False
        self.x, self.z = int(m.group(1)), int(m.group(3))
        self.y = bw.get('hoehe', self.y if m.group(2) == '~' else int(m.group(2)))
        self.cmd(f'forceload add {self.x - 48} {self.z - 48} {self.x + 48} {self.z + 48}')
        warte_geladen(self, self.x, self.z)
        time.sleep(3)
        return True

    def bauwerk_genau(self, bw):
        """Spawn-Box (Bauwerksteil) blockgenau ausmessen; nur ein Bauwerk nehmen, dessen Box in x/z so liegt wie im
        Plan ("groesse": [x, z]), dann den Plan-Ursprung so legen, dass "ecke" (Plan-Koordinate der Box-Ecke mit
        den kleinsten Werten) genau auf der Box-Ecke liegt."""
        pred = f'{{type:"minecraft:location_check",predicate:{{structures:"{bw["id"]}"}}}}'

        def drin(x, y, z):
            return 'passed' in self.r(f'execute in {self.dim} positioned {x} {y} {z} if predicate {pred}').lower()

        sx, sz = self.x, self.z
        for versuch in range(8):
            if not self.finde(bw, sx + versuch * 2500, sz):
                return
            start = next(((self.x + dx, self.y + dy, self.z + dz) for dy in range(-12, 13, 2)
                          for dx in range(0, 16, 2) for dz in range(0, 16, 2)
                          if drin(self.x + dx, self.y + dy, self.z + dz)), None)
            if not start:
                continue
            lo, hi = list(start), list(start)
            for ach in range(3):
                for richt, grenze in ((-1, lo), (1, hi)):
                    p = list(start)
                    while True:
                        p[ach] += richt
                        if not drin(*p):
                            break
                        grenze[ach] = p[ach]
            gx, gz = hi[0] - lo[0] + 1, hi[2] - lo[2] + 1
            self.meld.append(f'Box {bw["id"]}: {lo} .. {hi} ({gx} x {hi[1] - lo[1] + 1} x {gz})')
            if [gx, gz] == list(bw['groesse']):
                ex, ey, ez = bw.get('ecke', [0, 0, 0])
                self.x, self.y, self.z = lo[0] - ex, lo[1] - ey, lo[2] - ez
                return
        self.meld.append(f'kein passend gedrehtes {bw["id"]} gefunden')

    # ---------------------------------------------------------------- Aufbau
    def vorbereiten(self):
        if self.t.get('bauwerk', {}).get('suchen'):     # echtes Bauwerk: erst finden, dann dort aufbauen
            self.bauwerk(self.t['bauwerk'])
        x1, y1, z1, x2, y2, z2 = self.box(6)
        self.cmd(f'forceload add {x1} {z1} {x2} {z2}')
        warte_geladen(self, (x1 + x2) // 2, (z1 + z2) // 2)
        for yy in range(y1, y2 + 1, 8):                 # Platz frei machen (in Scheiben, wegen Blocklimit)
            self.cmd(f'fill {x1} {yy} {z1} {x2} {min(y2, yy + 7)} {z2} minecraft:air')
        self.cmd(f'kill @e[type=!minecraft:player,x={x1},y={y1},z={z1},dx={x2 - x1},dy={y2 - y1},dz={z2 - z1}]')
        if self.t.get('boden'):                          # Erdboden: unter y 0 Erde (bzw. Stein), oben drauf der Boden
            oben = self.y + self.t.get('erde_bis', -1)    # erde_bis > -1: die Farm liegt unter der Erde
            fuell = self.t.get('fuellung', 'minecraft:dirt')
            for yy in range(y1, oben, 8):
                self.cmd(f'fill {x1} {yy} {z1} {x2} {min(oben - 1, yy + 7)} {z2} {fuell}')
            self.cmd(f'fill {x1} {oben} {z1} {x2} {oben} {z2} {self.t["boden"]}')
        if self.t.get('biom'):                           # in Scheiben, sonst ist der Bereich zu groß
            for yy in range(y1 - 8, y2 + 9, 8):
                self.cmd(f'fillbiome {x1 - 8} {yy} {z1 - 8} {x2 + 8} {yy + 7} {z2 + 8} {self.t["biom"]}')
        if self.t.get('bauwerk') and not self.t['bauwerk'].get('suchen'):
            self.bauwerk(self.t['bauwerk'])
        for c in self.t.get('vorher', []):
            self.cmd(self.ersetze(c))

    def bauwerk(self, bw):
        """Bauwerk suchen (echte Welt: /locate, sonst setzen), seine Box finden, leeren und den Plan-Ursprung so
        legen, dass der Anker in der Box liegt. Per Befehl gesetzte Bauwerke haben keine Spawn-Regeln."""
        if bw.get('suchen') and bw.get('groesse'):      # genaue Box ausmessen, passend gedrehtes Bauwerk suchen
            return self.bauwerk_genau(bw)
        if bw.get('suchen'):
            if not self.finde(bw):
                return
        else:
            self.cmd(f'place structure {bw["id"]} {self.x} {self.y} {self.z}')
        treffer = []
        pred = f'{{type:"minecraft:location_check",predicate:{{structures:"{bw["id"]}"}}}}'
        schritt, hoch = (3, 40) if bw.get('suchen') else (2, 24)
        for dx in range(-48, 49, schritt):
            for dz in range(-48, 49, schritt):
                for dy in range(-hoch, hoch + 1, 4):
                    a = self.r(f'execute in {self.dim} positioned {self.x + dx} {self.y + dy} {self.z + dz} '
                               f'if predicate {pred}')
                    if 'passed' in a.lower() or 'Test passed' in a:
                        treffer.append((self.x + dx, self.y + dy, self.z + dz))
        if not treffer:
            self.meld.append(f'Bauwerk {bw["id"]} nicht gefunden')
            return
        mx = sum(p[0] for p in treffer) // len(treffer)
        my = sum(p[1] for p in treffer) // len(treffer)
        mz = sum(p[2] for p in treffer) // len(treffer)
        if bw.get('suchen'):     # große Bauwerke (Festung): Mittelpunkt liegt oft außerhalb – nächsten Treffer nehmen
            mx, my, mz = min(treffer, key=lambda p: (p[0] - mx) ** 2 + (p[1] - my) ** 2 + (p[2] - mz) ** 2)
        ax, ay, az = bw.get('anker', [0, 0, 0])
        self.x, self.y, self.z = mx - ax, my - ay, mz - az
        if bw.get('oberflaeche'):          # Plan auf den echten Boden an dieser Stelle setzen (nicht in einen Hügel)
            for yy in range(self.y + 40, self.y - 41, -1):
                if 'passed' not in self.r(f'execute in {self.dim} if block {self.x} {yy} {self.z} '
                                          f'#minecraft:replaceable').lower() and \
                        'passed' not in self.r(f'execute in {self.dim} if block {self.x} {yy} {self.z} '
                                               f'#minecraft:leaves').lower():
                    self.y = yy + 1
                    break
        if bw.get('suchen'):
            return
        x1, y1, z1, x2, y2, z2 = self.box(6)
        for yy in range(min(y1, my - 30), max(y2, my + 30) + 1, 8):   # Bauwerk-Blöcke weg, nur die Box bleibt
            self.cmd(f'fill {x1 - 10} {yy} {z1 - 10} {x2 + 10} {yy + 7} {z2 + 10} minecraft:air')

    def bauen(self):
        plan = {(b['x'], b['y'], b['z']): b for b in self.f['fertig'] if not b.get('ent')}
        for st in self.f['steps']:
            for q in st.get('luft', []):
                x, y, z = self.p(q)
                self.cmd(f'setblock {x} {y} {z} minecraft:air')
            fest = [b for b in st['added'] if not b.get('ent') and b['id'] not in ('water', 'lava')]
            fl = [b for b in st['added'] if not b.get('ent') and b['id'] in ('water', 'lava')]
            haengt = {'wall_sign', 'ladder', 'stone_button', 'lever', 'pointed_dripstone', 'oak_trapdoor'}
            for b in sorted(fest, key=lambda q: (q['y'], q['id'] in haengt)) + fl:
                zst = blockzustand(b)
                if b['id'] == 'redstone':
                    zst = staub_form(plan, (b['x'], b['y'], b['z']))
                if zst:
                    x, y, z = self.p(b)
                    self.cmd(f'setblock {x} {y} {z} {zst}')
            if fl:
                time.sleep(4)                  # Wasser/Lava erst fließen lassen (Spieler könnte sonst nichts pflanzen)
        # Lebewesen und AFK-Platz nach dem Bau
        for b in self.f['fertig']:
            if not b.get('ent') and b['id'] != bloecke.AFK:
                continue
            x, y, z = self.p(b)
            if b['id'] == bloecke.AFK:
                self.afk = (x, y, z)
                if 'passed' in self.r(f'execute in {self.dim} if block {x} {y - 1} {z} minecraft:air').lower():
                    self.cmd(f'setblock {x} {y - 1} {z} minecraft:glass')
            elif b['id'] in bloecke.LEBEWESEN:
                typ = bloecke.LEBEWESEN[b['id']][0]
                extra = '{PersistenceRequired:1b}' if typ not in ('minecraft:hopper_minecart', 'minecraft:minecart') else ''
                self.cmd(f'summon {typ} {x + 0.5} {y} {z + 0.5} {extra}'.strip())
        for c in self.t.get('nachher', []):
            self.cmd(self.ersetze(c))

    def spieler(self, name):
        if not hasattr(self, 'afk'):                     # neben der Farm stehen (nicht darüber: Bäume brauchen Platz)
            x1, y1, z1, x2, y2, z2 = self.box(0)
            self.afk = (x2 + 4, self.y, (z1 + z2) // 2)
            self.cmd(f'setblock {self.afk[0]} {self.afk[1] - 1} {self.afk[2]} minecraft:glass')
        x, y, z = self.afk
        self.r(f'player {name} spawn at {x + 0.5} {y} {z + 0.5} facing 0 0 in {self.dim} in survival')
        time.sleep(1.0)
        self.r(f'clear {name}')                          # Testspieler behalten sonst ihr Inventar aus alten Läufen
        self.r(f'effect give {name} minecraft:resistance infinite 255 true')
        self.r(f'effect give {name} minecraft:saturation infinite 255 true')
        sp = self.t.get('spieler', {})
        if sp.get('hand'):
            self.r(f'item replace entity {name} weapon.mainhand with {sp["hand"]}')
        if sp.get('aktion'):
            self.r(f'player {name} {sp["aktion"]}')
        self.name = name

    # ---------------------------------------------------------------- Messen
    def messen(self):
        erg = {'items': {}, 'boden': {}, 'bloecke': {}, 'wesen': {}, 'inventar': {}, 'beute': {}}
        x1, y1, z1, x2, y2, z2 = self.box(3)
        for b in self.f['fertig']:
            if b['id'] in BEHAELTER and not b.get('ent'):
                x, y, z = self.p(b)
                zaehle(self.cmd(f'data get block {x} {y} {z} Items'), erg['items'])
        sel = f'x={x1},y={y1},z={z1},dx={x2 - x1},dy={y2 - y1},dz={z2 - z1}'
        for dx, dy, dz in self.t.get('behaelter', []):     # Behälter, die nur der Test setzt
            zaehle(self.cmd(f'data get block {self.x + dx} {self.y + dy} {self.z + dz} Items'), erg['items'])
        for typ in ('minecraft:hopper_minecart', 'minecraft:chest_minecart'):
            zaehle(self.r(f'execute in {self.dim} as @e[type={typ},{sel}] run data get entity @s Items'), erg['items'])
        # Items am Boden: je erwartetem Item-Typ die Anzahl aufsummieren
        alle = set()
        for teil in ('erwartet', 'hoechstens'):
            for art in ('items', 'boden', 'beute'):
                alle |= {it for k in self.t.get(teil, {}).get(art, {}) for it in k.split('|') if it != '*'}
        for it in alle:
            filt = f'type=minecraft:item,{sel},nbt={{Item:{{id:"{it}"}}}}'
            self.r('scoreboard players set #s mctest 0')
            self.r(f'execute in {self.dim} as @e[{filt}] store result score @s mctest run data get entity @s Item.count')
            self.r(f'execute in {self.dim} as @e[{filt}] run scoreboard players operation #s mctest += @s mctest')
            m = re.search(r'has (\d+)', self.r('scoreboard players get #s mctest'))
            if m and int(m.group(1)):
                erg['boden'][it] = int(m.group(1))
        for bl in set(self.t.get('erwartet', {}).get('bloecke', {})) | set(self.t.get('hoechstens', {}).get('bloecke', {})):
            erg['bloecke'][bl] = zaehle_bloecke(self, bl, (x1, y1, z1, x2, y2, z2))
        wsel = sel
        if self.t.get('bereich'):                        # Wesen nur in einem Teil zählen (z. B. Tötungszelle)
            a1, b1, c1, a2, b2, c2 = self.t['bereich']
            wsel = (f'x={self.x + a1},y={self.y + b1},z={self.z + c1},dx={a2 - a1},dy={b2 - b1},dz={c2 - c1}')
        for w in set(self.t.get('erwartet', {}).get('wesen', {})) | set(self.t.get('hoechstens', {}).get('wesen', {})):
            erg['wesen'][w] = anzahl(self.r(f'execute in {self.dim} if entity @e[type={w},{wsel}]'))
        if hasattr(self, 'name') and (self.t.get('erwartet', {}).get('inventar') or self.t.get('erwartet', {}).get('beute')):
            zaehle(self.r(f'data get entity {self.name} Inventory'), erg['inventar'])
        erg['beute'] = {}                                 # alles zusammen: Behälter, Boden, Inventar des Testspielers
        for art in ('items', 'boden', 'inventar'):
            for k, v in erg[art].items():
                erg['beute'][k] = erg['beute'].get(k, 0) + v
        return erg


def zaehle(antwort, ziel):
    """Items aus einer data-get-Antwort zählen: jedes {…} mit id und count (Reihenfolge der Felder egal)."""
    for m in re.finditer(r'\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}', antwort):
        teil = m.group(1)
        i = re.search(r'(?<![a-z_])id: "([a-z0-9_:]+)"', teil)
        if not i or i.group(1).split(':')[-1] in BEHAELTER or 'Slot' not in teil and 'count' not in teil:
            continue
        n = re.search(r'(?<![a-z_])count: (\d+)', teil)
        ziel[i.group(1)] = ziel.get(i.group(1), 0) + (int(n.group(1)) if n else 1)


def anzahl(antwort):
    m = re.search(r'Test passed[.,] [Cc]ount: (\d+)', antwort)
    return int(m.group(1)) if m else (1 if 'Test passed' in antwort else 0)


def zaehle_bloecke(t, block, box):
    """Zählt Blöcke ohne die Farm zu verändern: gefiltert in einen leeren Bereich weit oben klonen, dann leeren."""
    x1, y1, z1, x2, y2, z2 = box
    ziel_y = 250 - (y2 - y1)
    n = 0
    for yy in range(y1, y2 + 1, 8):
        y_end = min(y2, yy + 7)
        a = t.r(f'execute in {t.dim} run clone {x1} {yy} {z1} {x2} {y_end} {z2} {x1} {ziel_y} {z1} filtered {block} force')
        m = re.search(r'cloned (\d+)', a)
        n += int(m.group(1)) if m else 0
        t.r(f'execute in {t.dim} run fill {x1} {ziel_y} {z1} {x2} {ziel_y + 7} {z2} minecraft:air')
    return n


def warte_geladen(t, x, z, versuche=60):
    for _ in range(versuche):
        if 'passed' in t.r(f'execute in {t.dim} if loaded {x} 0 {z}').lower():
            return
        time.sleep(0.5)
    t.meld.append(f'Chunk bei {x} {z} lädt nicht')


STOERER = ('slime', 'zombie', 'skeleton', 'spider', 'creeper', 'enderman', 'witch', 'drowned', 'zombie_villager',
           'husk', 'stray', 'phantom', 'cave_spider')


def aufraeumen(r):
    """Die flache Testwelt liegt unter Y 40: dort spawnen überall Schleime und füllen das Monster-Limit. Alles auf
    der Oberfläche der Testwelt (unter Y -50) weg – die Farmen liegen höher."""
    for typ in STOERER:
        r(f'execute in minecraft:overworld run kill @e[type=minecraft:{typ},y=-64,dy=13]')


def sprint(r, ticks):
    r('tick unfreeze')
    aufraeumen(r)
    aus = r(f'tick sprint {ticks}')
    start = time.time()
    while True:
        time.sleep(3)
        aufraeumen(r)
        q = r('tick query')
        if 'sprint' not in q.lower() or time.time() - start > 3600:
            break
    return aus, round(time.time() - start)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    ticks = int(next((a.split('=')[1] for a in sys.argv if a.startswith('--ticks=')), 12000))
    zufall = int(next((a.split('=')[1] for a in sys.argv if a.startswith('--zufall=')), 3))
    plaene = {f['id']: f for f in json.load(open(args[0], encoding='utf-8'))}
    tests = json.load(open(args[1], encoding='utf-8'))
    auswahl = args[2:] or list(tests)
    r = Rcon()
    r('scoreboard objectives add mctest dummy')
    if '--behalten' not in sys.argv:       # alte Testorte entladen: ihre Mobs zählen sonst zum Monster-Limit
        for d in DIM.values():
            r(f'execute in {d} run forceload remove all')
            r(f'execute in {d} run kill @e[type=!minecraft:player]')
    for c in ('gamerule spawn_mobs true', 'gamerule advance_weather false', 'weather clear',
              'gamerule max_entity_cramming 100', 'gamerule players_sleeping_percentage 101',
              f'gamerule random_tick_speed {zufall}'):
        r(c)
    laeufe = []
    nur_messen = '--nur-messen' in sys.argv
    for k, fid in enumerate(auswahl):
        tt = tests[fid]
        plan = plaene[tt.get('plan', fid)]
        hoehe = tt.get('hoehe', 0 if tt.get('dimension', 'overworld') != 'the_end' else 60)
        basis = int(os.environ.get('MCTEST_BASIS', 4096))  # neuer Ort: keine Reste alter Testläufe in der Nähe
        ux, uz = tt.get('ursprung', (k * 1024 + basis, basis))
        t = Test(r, plan, tt, (ux, hoehe, uz))
        if not nur_messen:
            t.vorbereiten()
            t.bauen()
            t.spieler(f'test{k}')
        laeufe.append((fid, t))
    zeit = {t.t.get('zeit', 'day') for _, t in laeufe}
    zahl = [z for z in zeit if isinstance(z, int)]
    if zahl:                                          # feste Startzeit, Tag/Nacht läuft weiter
        r(f'time set {zahl[0]}'); r('gamerule advance_time true')
    elif zeit == {'night'}:
        r('time set midnight'); r('gamerule advance_time false')
    elif 'cycle' in zeit or len(zeit) > 1:
        r('time set day'); r('gamerule advance_time true')
    else:
        r('time set noon'); r('gamerule advance_time false')
    aus, sek = sprint(r, ticks) if not nur_messen else ('', 0)
    bericht = {}
    for fid, t in laeufe:
        erg = t.messen()
        ok = True
        for art, ziel in t.t.get('erwartet', {}).items():
            for key, mindest in ziel.items():
                ist = sum(v for k2, v in erg[art].items() if key == '*' or k2.split(' ')[0] in key.split('|'))
                if ist < mindest:
                    ok = False
        for art, ziel in t.t.get('hoechstens', {}).items():
            for key, hoechst in ziel.items():
                ist = sum(v for k2, v in erg[art].items() if key == '*' or k2.split(' ')[0] in key.split('|'))
                if ist > hoechst:
                    ok = False
                    t.meld.append(f'zu viel {key}: {ist} > {hoechst}')
        bericht[fid] = {'ok': ok, 'gemessen': erg, 'meldungen': t.meld[:12]}
        print(f'== {fid}: {"OK" if ok else "FEHLT"} | {json.dumps(erg, ensure_ascii=False)}')
        for m in t.meld[:12]:
            print('   !', m)
    print(f'Sprint {ticks} Ticks in {sek} s')
    for _, t in laeufe:
        if hasattr(t, 'name'):
            r(f'player {t.name} kill')
    json.dump(bericht, open(os.environ.get('MCTEST_BERICHT', 'bericht.json'), 'w'), indent=1, ensure_ascii=False)


if __name__ == '__main__':
    main()
