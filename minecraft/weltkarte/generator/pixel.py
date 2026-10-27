"""Wertet eine Regionsdatei für die Weltkarte aus: je Kartenpixel ein Chunk, darin vier Spalten.

Aufruf:  python3 pixel.py <r.X.Z.mca> <X> <Z> <x0> <z0> <blöcke_pro_pixel> <farben.json>  > pixel.json

Pixel (px, pz) liegt bei x0 + px·B … x0 + (px+1)·B; ausgewertet wird der Chunk in der Mitte. In jeder Spalte zählt
wie im Spiel der oberste Block mit Kartenfarbe (Glas, Fackeln usw. haben keine). Ergebnis je Pixel: häufigste Farbe der
vier Spalten, mittlere Höhe, bei Wasser die mittlere Tiefe. Nicht erzeugte Chunks fehlen (bleiben auf der Karte leer).
"""
import sys, json, math, zlib, struct, io, nbtlib
pfad, rx, rz, X0, Z0, B = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])
F = json.load(open(sys.argv[7]))['farben']
d = open(pfad, 'rb').read()
def chunk(cx, cz):
    i = 4 * ((cx & 31) + (cz & 31) * 32)
    off = int.from_bytes(d[i:i+3], 'big') * 4096
    if not off: return None
    ln, comp = struct.unpack('>IB', d[off:off+5])
    return nbtlib.File.parse(io.BytesIO(zlib.decompress(d[off+5:off+4+ln])))
def nm(p):
    p = p if isinstance(p, str) else str(p.get('Name', p.get('id', p.get('', '?'))))
    return p.replace('minecraft:', '')
FARB = 'white orange magenta light_blue yellow lime pink gray light_gray cyan purple blue brown green red black'.split()
DYE = {'white':'SNOW','lime':'COLOR_LIGHT_GREEN'}
def farbe(n):
    n = n.split('[')[0]
    if n in F and F[n] != 'NONE': return F[n]
    if n.endswith('leaves'): return 'COLOR_PINK' if n.startswith('cherry') else 'PLANT'
    if n in ('piston', 'sticky_piston'): return 'STONE'
    if n == 'wheat': return 'PLANT'
    for c in FARB:
        if n.startswith(c + '_'):
            rest = n[len(c)+1:]
            if rest == 'terracotta': return 'TERRACOTTA_' + c.upper()
            return DYE.get(c, 'COLOR_' + c.upper())
    if n in F: return 'NONE'
    sys.stderr.write('UNBEKANNT '+n+'\n'); return 'STONE'
out = {}
for pz in range(128):
    cz_b = Z0 + pz * B + B // 2
    if (cz_b >> 9) != rz: continue
    for px in range(128):
        cx_b = X0 + px * B + B // 2
        if (cx_b >> 9) != rx: continue
        c = chunk(cx_b >> 4, cz_b >> 4)
        if c is None or str(c.get('Status', '')).replace('minecraft:', '') not in ('full', ''):
            continue
        secs = {}
        for s in c['sections']:
            bs = s.get('block_states')
            if not bs: continue
            pal = [nm(p) for p in bs['palette']]
            data = [int(v) & ((1 << 64) - 1) for v in bs['data']] if 'data' in bs else None
            secs[int(s['Y'])] = (pal, data)
        def blk(x, y, z):
            s = secs.get(y >> 4)
            if not s: return 'air'
            pal, data = s
            if data is None: return pal[0]
            bits = max(4, math.ceil(math.log2(len(pal)))); per = 64 // bits
            idx = ((y & 15) << 8) | ((z & 15) << 4) | (x & 15)
            return pal[(data[idx // per] >> ((idx % per) * bits)) & ((1 << bits) - 1)]
        hm = c['Heightmaps'].get('WORLD_SURFACE')
        proben = []
        for ox in (3, 11):
            for oz in (3, 11):
                x = (cx_b & ~15) + ox; z = (cz_b & ~15) + oz
                i = (oz) * 16 + ox
                if hm is not None:
                    per = 64 // 9; v = (int(hm[i // per]) & ((1 << 64) - 1)) >> ((i % per) * 9) & 511
                    y = v - 64 - 1
                else:
                    y = 319
                f = 'NONE'; tiefe = 0
                while y > -64:
                    b = blk(x, y, z); f = farbe(b)
                    if f != 'NONE': break
                    y -= 1
                if f == 'WATER':
                    yy = y
                    while yy > -64 and farbe(blk(x, yy, z)) == 'WATER' and tiefe < 20: tiefe += 1; yy -= 1
                proben.append((f, y, tiefe))
        from collections import Counter
        f = Counter(p[0] for p in proben).most_common(1)[0][0]
        h = sum(p[1] for p in proben) / 4
        t = sum(p[2] for p in proben) / 4
        out[f'{px},{pz}'] = (f, h, t)
print(json.dumps(out))
