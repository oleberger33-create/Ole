/* Flausenfabrik – Renderer für Charge 001.
   Zeichnet jedes Bild deterministisch aus timeline.json: render(frame).
   Echte 60 Bilder pro Sekunde: alles hängt stetig von t = frame / fps ab,
   nichts zählt Bilder. Leben kommt aus Atmung, Blick und Lidschlag nach
   festen Zeitplänen, Betonungen der Sprache und Feder-Kanälen, die init()
   einmal für die ganze Folge vorab integriert (precompute). */
'use strict';
const NS = 'http://www.w3.org/2000/svg';
const C = {
  senf: '#F4B41A', senfD: '#E2A20F', senfDD: '#C4880A', him: '#E33D6E', himD: '#B82A55', pet: '#135D66',
  petD: '#0F4C54', petDD: '#0B3A40', ink: '#1D1A2B', ink2: '#3A3550', taube: '#A7A3C2', taubeD: '#8C87AB',
  garn: '#FFF8EC', garnD: '#E6DCC8', screen: '#0E2326', wood: '#C98F3E', woodD: '#A9732B', brezel: '#B9772A'
};
const FONT = { bagel: "'Bagel Fat One'", body: "'Rethink Sans'", mono: "'DM Mono'" };
let TL = null;

function E(tag, attrs, parent) {
  const e = document.createElementNS(NS, tag);
  if (attrs) for (const k in attrs) e.setAttribute(k, attrs[k]);
  if (parent) parent.appendChild(e);
  return e;
}
function T(e, txt) { e.textContent = txt; return e; }
function setT(e, s) { if (e._t !== s) { e.setAttribute('transform', s); e._t = s; } }
function setA(e, k, v) { const key = '_' + k; if (e[key] !== v) { e.setAttribute(k, v); e[key] = v; } }
function show(e, on) { const v = on ? 'inline' : 'none'; if (e._d !== v) { e.style.display = v; e._d = v; } }
function clamp(x, a, b) { return Math.max(a, Math.min(b, x)); }
function lerp(a, b, u) { return a + (b - a) * u; }
function smooth(u) { u = clamp(u, 0, 1); return u * u * (3 - 2 * u); }
function smootherstep(u) { u = clamp(u, 0, 1); return u * u * u * (u * (6 * u - 15) + 10); }
function easeOut(u) { u = clamp(u, 0, 1); return 1 - (1 - u) * (1 - u); }
function frac(x) { return x - Math.floor(x); }
function hash(a, b) { let x = Math.sin(a * 127.1 + b * 311.7) * 43758.5453; return x - Math.floor(x); }
function rnd(a, b) { return hash(a, b) * 2 - 1; }
const f1 = v => v.toFixed(1), f2 = v => v.toFixed(2), f3 = v => v.toFixed(3);
// Glattes, langsames Rauschen in [-1,1] (0.2–0.65 Hz): Atmen, Blickdrift, Schwanzwippen.
function wob(t, seed) { return 0.5 * Math.sin(t * 1.13 + seed * 12.9) + 0.3 * Math.sin(t * 2.31 + seed * 7.7) + 0.2 * Math.sin(t * 4.07 + seed * 3.1); }
// Stetiges Rattern in [-1,1] (ca. 9–20 Hz) für Maschinen-Wackeln; seed wählt Achse/Phase.
function rattle(t, seed) { return 0.6 * Math.sin(t * (71 - seed * 4) + seed * 1.9) + 0.4 * Math.sin(t * (113 + seed * 7) + seed * 4.3); }
// Letzter Index k mit key(a[k]) <= t in einer aufsteigend sortierten Liste, sonst -1.
function lastLE(a, t, key) {
  let lo = 0, hi = a.length - 1, k = -1;
  while (lo <= hi) { const m = (lo + hi) >> 1; if ((key ? key(a[m]) : a[m]) <= t) { k = m; lo = m + 1; } else hi = m - 1; }
  return k;
}

// ---------------------------------------------------------------------------
// Zeitplan lesen
// ---------------------------------------------------------------------------
const DEF = {
  cam: { x: 960, y: 540, z: 1, r: 0 }, fussel: { x: -500, y: 900, s: 0.8, r: 0, flip: 1, lx: 0, ly: 0, thread: 1 },
  kurt: { x: 860, y: 900, s: 1.6, shake: 0 }, broesel: { x: 2200, y: 900, s: 1.25, r: 0, flip: -1, lid: 0.55, wing: 0, brow: 0 },
  gurrmann: { x: 2200, y: 900, s: 1.3, r: 0, flip: -1, lid: 0.2, wing: 0, brow: 0 }, train: { x: 3000, y: 740, s: 1, r: 0, doors: 0 },
  ball: { x: 0, y: 0, s: 1 }, iris: { r: 1200 }, fade: { a: 0 }, logo: { p: 0 }, outside: { v: 1 }
};
function ease(e, u) {
  u = clamp(u, 0, 1);
  if (e === 'lin') return u;
  if (e === 'in') return u * u;
  if (e === 'out') return 1 - (1 - u) * (1 - u);
  return u * u * (3 - 2 * u);
}
function num(actor, prop, t) {
  const segs = TL.tracks[actor] && TL.tracks[actor][prop];
  let v = (DEF[actor] && DEF[actor][prop] !== undefined) ? DEF[actor][prop] : 0;
  if (!segs) return v;
  for (let i = 0; i < segs.length; i++) {
    const s = segs[i];
    if (s[0] > t) break;
    if (t < s[1]) v = lerp(s[2], s[3], ease(s[4], (t - s[0]) / (s[1] - s[0])));
    else v = s[3];
  }
  return v;
}
function st(actor, prop, t, dflt) {
  const L = TL.states[actor] && TL.states[actor][prop];
  let v = dflt;
  if (!L) return v;
  for (let i = 0; i < L.length; i++) { if (L[i][0] > t + 1e-6) break; v = L[i][1]; }
  return v;
}
function stT(actor, prop, t) {
  const L = TL.states[actor] && TL.states[actor][prop];
  let v = 0;
  if (!L) return v;
  for (let i = 0; i < L.length; i++) { if (L[i][0] > t + 1e-6) break; v = L[i][0]; }
  return v;
}
// Zustand als weicher Wert 0..1 (wahr = 1): blendet nach jedem Wechsel über dur Sekunden,
// auch bei schnellen Wechseln stetig. Für alles, was sonst beim Umschalten springen würde.
function stSmooth(actor, prop, t, dur) {
  const L = TL.states[actor] && TL.states[actor][prop];
  if (!L) return 0;
  let from = 0, to = 0, t0 = -1e9;
  for (let i = 0; i < L.length && L[i][0] <= t + 1e-6; i++) {
    from = lerp(from, to, smooth((L[i][0] - t0) / dur)); to = L[i][1] ? 1 : 0; t0 = L[i][0];
  }
  return lerp(from, to, smooth((t - t0) / dur));
}
// Diskreter Zustand mit Vorgänger: { prev, cur, tau = Zeit seit dem letzten echten Wechsel }.
// Wiederholtes Setzen desselben Werts zählt nicht als Wechsel.
function stBlend(actor, prop, t, dflt) {
  const L = TL.states[actor] && TL.states[actor][prop];
  let prev = dflt, cur = dflt, t0 = -1e9;
  if (L) for (let i = 0; i < L.length && L[i][0] <= t + 1e-6; i++) if (L[i][1] !== cur) { prev = cur; cur = L[i][1]; t0 = L[i][0]; }
  return { prev, cur, tau: t - t0 };
}
function sceneAt(t) {
  let s = TL.scenes[0][1], s0 = 0;
  for (const [t0, n] of TL.scenes) { if (t0 > t + 1e-6) break; s = n; s0 = t0; }
  return [s, s0];
}
// Ableitungen der Spuren, analytisch aus der Easing-Kurve des aktiven Segments.
// Außerhalb von Segmenten (auch bei Sprüngen mit Dauer 0 an Schnitten) ist v = 0.
function easeD(e, u) { if (e === 'lin') return 1; if (e === 'in') return 2 * u; if (e === 'out') return 2 * (1 - u); return 6 * u * (1 - u); }
function easeDD(e, u) { if (e === 'lin') return 0; if (e === 'in') return 2; if (e === 'out') return -2; return 6 - 12 * u; }
function activeSeg(actor, prop, t) {
  const segs = TL.tracks[actor] && TL.tracks[actor][prop];
  if (!segs) return null;
  let s = null;
  for (let i = 0; i < segs.length; i++) { if (segs[i][0] > t) break; s = segs[i]; }
  return s && t < s[1] ? s : null;
}
function segV(s, t) { if (!s) return 0; const d = s[1] - s[0]; return (s[3] - s[2]) / d * easeD(s[4], (t - s[0]) / d); }
function segA(s, t) { if (!s) return 0; const d = s[1] - s[0]; return (s[3] - s[2]) / (d * d) * easeDD(s[4], (t - s[0]) / d); }
function numV(actor, prop, t) { return segV(activeSeg(actor, prop, t), t); }
function numA(actor, prop, t) { return segA(activeSeg(actor, prop, t), t); }

// ---------------------------------------------------------------------------
// Sprache: Mundkanäle, Betonungen, Geräusch-Zeiten (Indizes baut precompute)
// ---------------------------------------------------------------------------
const LBY = {};    // Sprecher -> Zeilen (nach t0 sortiert)
const ACC = {};    // Sprecher -> Betonungen {t, w, side, top} über alle Zeilen
const SFXT = {};   // Geräuschname -> sortierte Startzeiten
const BLINK = {};  // Figur -> sortierte Lidschlag-Startzeiten
// Aktive Zeile eines Sprechers; pre/post erweitern das Fenster nach vorn/hinten.
function lineAt(who, t, pre, post) {
  const L = LBY[who];
  if (!L) return null;
  const k = lastLE(L, t + (pre || 0), l => l.t0);
  if (k < 0) return null;
  const l = L[k];
  return t < l.t1 + (post || 0) ? l : null;
}
// Mund zur Zeit t: o = Öffnung, w = Breite (0 rund .. 1 breit), s = Zischlaut; linear zwischen 60-Hz-Stützstellen.
const M0 = { o: 0, w: 0.5, s: 0, l: null };
function mouth(who, t, fx) {
  const l = lineAt(who, t);
  if (!l || (fx !== undefined && l.fx !== fx)) return M0;
  const p = (t - l.t0) * TL.envRate, i = Math.floor(p), u = p - i;
  const at = a => a ? lerp(a[i] || 0, a[i + 1] || 0, u) : 0;
  return { o: at(l.env), w: l.wide ? at(l.wide) : 0.5, s: at(l.ss), l };
}
// Betonungen einer Zeile: Einsatz, wenn env über 0.55 steigt und in den 0.12 s davor unter 0.3 war.
function lineAccents(l) {
  const e = l.env, R = TL.envRate, out = [];
  let low = -1e9, last = -1e9;
  for (let i = 1; i < e.length; i++) {
    if (e[i - 1] < 0.3) low = i - 1;
    if (e[i] >= 0.55 && e[i - 1] < 0.55 && (i - low) / R <= 0.12 && (i - last) / R >= 0.28) {
      let w = e[i];
      for (let j = i; j < Math.min(e.length, i + 12); j++) w = Math.max(w, e[j]);
      out.push({ t: l.t0 + i / R, w: w * (l.ex ? 1.5 : 1), side: out.length % 2 ? -1 : 1, top: 0 });
      last = i;
    }
  }
  out.slice().sort((a, b) => b.w - a.w).slice(0, 3).forEach(a => { a.top = 1; });
  return out;
}
// Stoß einer Betonung: schnell rauf (0.09 s), dann abklingen (0.2 s)
function bump(x) { return x < 0 ? 0 : Math.sin(Math.min(x / 0.09, 1) * Math.PI / 2) * Math.exp(-x / 0.2); }
// Summe der Betonungsstöße: p (Betrag) und sp (mit wechselnder Seite); topOnly = nur die 3 stärksten je Zeile.
const P0 = { p: 0, sp: 0 };
function pulse(who, t, topOnly) {
  const A = ACC[who];
  if (!A || !A.length) return P0;
  let p = 0, sp = 0;
  for (let k = lastLE(A, t, a => a.t); k >= 0 && t - A[k].t < 1.2; k--) {
    if (topOnly && !A[k].top) continue;
    const b = A[k].w * bump(t - A[k].t);
    p += b; sp += b * A[k].side;
  }
  return p || sp ? { p, sp } : P0;
}
// Geste halten: auf den 3 stärksten Betonungen 0.35 s halten, 0.15 s ein-/ausblenden
function accHold(who, t) {
  const A = ACC[who];
  if (!A) return 0;
  let h = 0;
  for (let k = lastLE(A, t + 0.1, a => a.t); k >= 0 && t - A[k].t < 0.7; k--) {
    if (!A[k].top) continue;
    const x = t - A[k].t;
    h = Math.max(h, smooth((x + 0.1) / 0.15) * (1 - smooth((x - 0.35) / 0.15)));
  }
  return h;
}
// Sekunden seit dem letzten Geräusch dieses Namens (1e9, wenn keins war)
function since(name, t) {
  const a = SFXT[name];
  if (!a) return 1e9;
  const k = lastLE(a, t);
  return k < 0 ? 1e9 : t - a[k];
}
// Lidschlag 0..1 aus der Zeitplan-Liste: 3 Bilder zu, 2 zu, 7 auf (slow > 1 dehnt, z. B. Brösel).
function blinkShape(x) {
  if (x < 0) return 0;
  if (x < 0.05) return (x / 0.05) * (x / 0.05);
  if (x < 0.085) return 1;
  if (x < 0.2) { const u = (x - 0.085) / 0.115; return (1 - u) * (1 - u); }
  return 0;
}
function blinkClosure(key, t, slow) {
  const a = BLINK[key];
  if (!a) return 0;
  const k = lastLE(a, t), sl = slow || 1;
  if (k < 0) return 0;
  return Math.max(blinkShape((t - a[k]) / sl), k > 0 ? blinkShape((t - a[k - 1]) / sl) : 0);
}
// Ereignis-Zeitplan aus hash: Abstände gapMin..gapMax, mit Wahrscheinlichkeit pDbl ein zweites nach dbl s.
function eventList(seed, t0, gapMin, gapMax, pDbl, dbl) {
  const out = [];
  for (let t = t0, n = 0; t < TL.total + 6; n++) {
    out.push(t);
    if (hash(seed, n + 0.3) < pDbl) out.push(t + dbl);
    t += gapMin + (gapMax - gapMin) * hash(seed, n + 0.7);
  }
  return out;
}
function blinkList(seed, forced) {
  const f = forced.slice().sort((a, b) => a - b), out = [];
  for (const c of eventList(seed, 0.5 + 2 * hash(seed, 0.5), 2.2, 5.5, 0.18, 0.24)) {
    const k = lastLE(f, c + 0.35);
    if (!(k >= 0 && f[k] > c - 0.35)) out.push(c);   // geplante Lidschläge weichen erzwungenen
  }
  const all = out.concat(f).sort((a, b) => a - b);
  return all.filter((c, k) => k === 0 || c - all[k - 1] > 0.2);
}
// Schreck (Alarm/Knall): kurz ducken, 18 px hoch, nachfedern. sq > 0 staucht, up in px.
const S0 = { sq: 0, up: 0 };
function startle(x) {
  if (x < 0 || x > 0.9) return S0;
  const a = smooth(x / 0.06) * (1 - smooth((x - 0.06) / 0.05));
  const j = x > 0.06 && x < 0.36 ? Math.sin(Math.PI * (x - 0.06) / 0.3) : 0;
  const l = x > 0.36 ? Math.exp(-10 * (x - 0.36)) * Math.sin(25 * (x - 0.36)) : 0;
  return { sq: 0.08 * a - 0.05 * j + 0.06 * l, up: 18 * j };
}
// Hüllkurve einer Reaktion: ein über ain, halten bis hold, aus über aout
function env3(x, ain, hold, aout) { return x < 0 ? 0 : smooth(x / ain) * (1 - smooth((x - hold) / aout)); }

// ---------------------------------------------------------------------------
// Vorberechnung (init): alles ab t = 0 integriert, daher liefern alle parallelen
// Worker exakt dieselben Werte. Kanäle mit 240 Hz, beim Lesen linear interpoliert:
//   crank, crankRate  Kurbelwinkel [°] und -drehzahl [°/s] (läuft weich an, trudelt aus)
//   belt, beltRate    Förderband-Weg [px] und -tempo [px/s]
//   land              Fensterlandschaft im Zug [px]
//   dist_<figur>      zurückgelegter Weg / Größe
//   lean_<figur>      Neigung [°] als gedämpfte Feder, Ziel ~ Tempo in x
//   squash_<figur>    Strecken (+) / Stauchen (−), Feder, Ziel ~ |Tempo in y|
//   ph_<figur>        Gangphase (Tauben: Doppelschritte, Fussel: Hüpfer), vL_<figur> Tempo [lokale px/s]
//   thrX, thrY, jig   Fussels Faden-Nachlauf [lokale px] und Fell-Wackeln (Stauchung)
//   en_<F|K|B|G|A>    Sprech-Energie (env mit 0.4 s Ausklingen)
//   needle            KURTs VU-Zeiger (Feder auf seine Mundöffnung)
//   gx_/gy_<figur>    Blickrichtung Augen (schnelle Feder), lx_/ly_<figur> Kopf/Körper (langsame Feder)
// ---------------------------------------------------------------------------
const INT = {};
const WALKERS = { fussel: { lean: 0.018, leanMax: 10 }, broesel: { lean: 0.010, leanMax: 6 }, gurrmann: { lean: 0.012, leanMax: 7 } };
const GAZERS = ['fussel', 'kurt', 'broesel', 'gurrmann'];
const W2A = { F: 'fussel', K: 'kurt', B: 'broesel', G: 'gurrmann' };
const JUMP = { up: [], down: [], air: [] };   // Fussels Absprünge, Landungen, Flugphasen (aus der y-Spur)
let KSW = [];      // KURT: Grenzen der Sprechfenster [an, aus, an, aus, ...]
let PECK = [], PECKF = [], DROOP = [];

function actorVis(a, t, scene) {
  if (!st(a, 'vis', t, 0)) return false;
  const stage = scene !== 'logo' && scene !== 'titel' && scene !== 'filmtitel';
  if (a === 'fussel' || a === 'gurrmann') return stage && scene !== 'endcard';
  if (a === 'kurt') return scene === 'halle';
  if (a === 'broesel') return scene === 'halle' || scene === 'endcard';
  return false;
}
// Augenpunkt einer Figur in Weltkoordinaten
function headPt(a, t) {
  const x = num(a, 'x', t), y = num(a, 'y', t), s = num(a, 's', t);
  if (a === 'fussel') return [x, y - 97 * s];
  if (a === 'kurt') return [x, y - 134 * s];
  const face = num(a, 'flip', t) < 0 ? 1 : -1;
  return [x - 42 * s * face, y - 144 * s];
}
// Woher kommt die Durchsage?
function annPt(l, t, scene) {
  if (l && l.fx === 'kurt') return headPt('kurt', t);
  if (scene === 'bahnhof') return [1770, 200];
  if (scene === 'zug') return [1450, 60];
  if (scene === 'himmel') return [960, -300];
  return null;
}
// Wer spricht gerade? Jüngste Zeile mit t0 − 0.25 ≤ t < t1 + 0.5 (Zuhörer drehen sich vorher hin).
function speakerLine(t) {
  const L = TL.lines;
  for (let k = lastLE(L, t + 0.25, l => l.t0), n = 0; k >= 0 && n < 3; k--, n++) if (t < L[k].t1 + 0.5) return L[k];
  return null;
}
// Blickziel als Richtung [lx, ly] in Weltrichtung (je ±1); null = altes Ziel halten, undefined = keine Zeile aktiv.
function gazeTarget(a, t, scene) {
  const me = headPt(a, t);
  const toward = q => q ? [clamp((q[0] - me[0]) / 350, -1, 1), clamp((q[1] - me[1]) / 300, -1, 1)] : null;
  if (since('gong', t) < 1.3 && (scene === 'bahnhof' || scene === 'zug')) return toward(annPt(null, t, scene));
  const l = speakerLine(t);
  if (!l) return undefined;
  if (l.who === 'A') return toward(annPt(l, t, scene));
  const sa = W2A[l.who];
  if (sa !== a) return toward(headPt(sa, t));
  // Ich spreche: zum Angesprochenen (letzter anderer Sprecher der letzten 8 s), sonst zur nächsten Figur
  for (let j = l.i - 1; j >= 0 && TL.lines[j].t1 > l.t0 - 8; j--) {
    const o = W2A[TL.lines[j].who];
    if (o && o !== a && actorVis(o, t, scene)) return toward(headPt(o, t));
  }
  let best = null, bd = 1e9;
  for (const o of GAZERS) {
    if (o === a || !actorVis(o, t, scene)) continue;
    const q = headPt(o, t), d = Math.hypot(q[0] - me[0], q[1] - me[1]);
    if (d < bd) { bd = d; best = q; }
  }
  return toward(best);
}

function precompute() {
  // ---- Indizes: Zeilen je Sprecher, Betonungen, Geräusche ----
  TL.lines.forEach((l, i) => { l.i = i; (LBY[l.who] = LBY[l.who] || []).push(l); });
  for (const who in LBY) { ACC[who] = []; for (const l of LBY[who]) { l.acc = lineAccents(l); ACC[who].push(...l.acc); } }
  for (const e of TL.sfx) (SFXT[e.name] = SFXT[e.name] || []).push(e.t);
  for (const k in SFXT) SFXT[k].sort((a, b) => a - b);
  // ---- KURT: Sprechfenster [t0 − 0.12, t1 + 0.3], überlappende zusammengelegt ----
  KSW = [];
  for (const l of LBY.K || []) {
    const a = l.t0 - 0.12, b = l.t1 + 0.3;
    if (KSW.length && a <= KSW[KSW.length - 1]) KSW[KSW.length - 1] = Math.max(KSW[KSW.length - 1], b);
    else KSW.push(a, b);
  }
  // ---- Fussels Sprünge: 'out' nach oben = Absprung, 'in' nach unten = Landung ----
  const ys = (TL.tracks.fussel && TL.tracks.fussel.y) || [];
  for (const s of ys) {
    const d = s[3] - s[2], dur = s[1] - s[0];
    if (dur <= 0) continue;
    if (s[4] === 'out' && d < -25) JUMP.up.push({ t: s[0], v: Math.abs(2 * d / dur) });
    if (s[4] === 'in' && d > 25) {
      JUMP.down.push({ t: s[1], v: 2 * d / dur });
      const up = ys.find(u => u[4] === 'out' && u[3] - u[2] < -25 && Math.abs(u[1] - s[0]) < 0.02);
      JUMP.air.push([up ? up[0] : s[0], s[1]]);
    }
  }
  JUMP.up.sort((a, b) => a.t - b.t); JUMP.down.sort((a, b) => a.t - b.t); JUMP.air.sort((a, b) => a[0] - b[0]);
  // ---- Federn und Kanäle ----
  const forced = { fussel: [], kurt: [], broesel: [], gurrmann: [] };
  integrate(forced);
  // ---- Lidschläge: Zufallsplan + erzwungene (Schnitt, Augen-Wechsel, Blicksprung, Reaktionen) ----
  const cutB = TL.scenes.map(s => s[0] + 0.06);
  const eyeT = ((TL.states.fussel && TL.states.fussel.eyes) || []).map(e => e[0]);
  BLINK.fussel = blinkList(1, cutB.concat(eyeT, forced.fussel, SFXT.fehler || []));
  BLINK.kurt = blinkList(2, cutB.concat(forced.kurt, (SFXT.plopp || []).map(x => x + 0.02)));
  BLINK.broesel = blinkList(3, cutB.concat(forced.broesel));
  BLINK.gurrmann = blinkList(4, cutB.concat(forced.gurrmann));
  BLINK.endFussel = blinkList(5, cutB);
  BLINK.sitter = blinkList(6, cutB);
  for (let i = 0; i < 14; i++) BLINK['crowd' + i] = blinkList(10 + i, cutB);
  // ---- Picken der Bahnsteig-Tauben (30 % Doppelpicker), schnelles Picken an der Stempeluhr, Brösels Kopfhänger ----
  PECK = []; PECKF = [];
  for (let i = 0; i < 14; i++) { PECK.push(eventList(30 + i, 0.4 + 2 * hash(i, 4), 1.2, 4.0, 0.3, 0.32)); PECKF.push(eventList(60 + i, 0.3 * hash(i, 5), 0.35, 0.8, 0, 0)); }
  DROOP = eventList(77, 4 + 3 * hash(77, 1), 6, 9, 0, 0);
}

function integrate(forced) {
  const dt = 1 / 240, n = Math.ceil(TL.total / dt) + 2;
  // Cursor für monoton wachsendes t: aktives Segment / aktueller Zustand ohne Neu-Suche
  const segCur = (actor, prop) => {
    const segs = (TL.tracks[actor] && TL.tracks[actor][prop]) || [];
    const d0 = (DEF[actor] && DEF[actor][prop] !== undefined) ? DEF[actor][prop] : 0;
    let k = 0;
    return t => {
      while (k < segs.length && segs[k][0] <= t) k++;
      const s = segs[k - 1];
      if (!s) return { v: d0, s: null };
      if (t < s[1]) return { v: lerp(s[2], s[3], ease(s[4], (t - s[0]) / (s[1] - s[0]))), s };
      return { v: s[3], s: null };
    };
  };
  const stCur = (actor, prop, dflt) => {
    const L = (TL.states[actor] && TL.states[actor][prop]) || [];
    let k = 0;
    return t => { while (k < L.length && L[k][0] <= t + 1e-6) k++; return k ? L[k - 1][1] : dflt; };
  };
  const arr = () => new Float64Array(n), f32 = () => new Float32Array(n);
  const crank = arr(), crankRate = arr(), belt = arr(), beltRate = arr(), land = arr();
  const kurtCrank = stCur('kurt', 'crank', 0), crankFast = stCur('broesel', 'crankfast', 0), beltRun = stCur('belt', 'run', 0);
  const outV = segCur('outside', 'v');
  const kUp = 1 - Math.exp(-dt / 0.25), kDown = 1 - Math.exp(-dt / 0.5), kBelt = 1 - Math.exp(-dt / 0.35);
  // Federn: semi-implizites Euler, v += (−w²(y−Ziel) − 2zw·v)·dt; y += v·dt
  const W = Object.keys(WALKERS).map(name => ({
    name, cfg: WALKERS[name], cx: segCur(name, 'x'), cy: segCur(name, 'y'), cs: segCur(name, 's'), cf: segCur(name, 'flip'),
    vis: stCur(name, 'vis', 0), dist: arr(), lean: arr(), squash: arr(), ph: arr(), vL: f32(),
    l: 0, lv: 0, q: 0, qv: 0, px: null, py: null, phase: 0, wasVis: 0
  }));
  const springStep = (y, v, target, w, z) => { v += (-w * w * (y - target) - 2 * z * w * v) * dt; return [y + v * dt, v]; };
  const wL = 2 * Math.PI * 1.7, zL = 0.45, wQ = 2 * Math.PI * 2.6, zQ = 0.3;
  // Fussel: Faden (2.4 Hz, schwach gedämpft) und Fell (6 Hz) werden von Tempo-Änderungen angestoßen
  const thrX = f32(), thrY = f32(), jig = f32();
  const wT = 2 * Math.PI * 2.4, zT = 0.22, wJ = 2 * Math.PI * 6, zJ = 0.3;
  let Lx = 0, Ly = 0, Lvx = 0, Lvy = 0, jg = 0, jv = 0, pvx = 0, pvy = 0;
  // Sprech-Energie je Sprecher, KURTs Zeiger
  const WHOS = ['F', 'K', 'B', 'G', 'A'], EN = {}, ecur = {}, ek = {};
  for (const w of WHOS) { EN[w] = f32(); ecur[w] = 0; ek[w] = 0; }
  const eDecay = Math.exp(-dt / 0.4), needle = f32(), wN = 2 * Math.PI * 3, zN = 0.35;
  let nd = 0, ndv = 0;
  // Blick: Ziel mit 60 Hz bestimmen, Augen (5 Hz, kritisch gedämpft) und Kopf/Körper (1.4 Hz) folgen
  const wE = 2 * Math.PI * 5, zE = 1, wS = 2 * Math.PI * 1.4, zS = 0.8;
  const G = GAZERS.map((a, gi) => ({
    a, gi, gx: f32(), gy: f32(), lx: f32(), ly: f32(), tx: 0, ty: 0.1, has: false, vis: false,
    ex: 0, ey: 0, evx: 0, evy: 0, sx: 0, sy: 0, svx: 0, svy: 0, ox: 0, oy: 0, sacT: 0.4 + hash(gi, 9), sacN: 0
  }));
  let lastLine = -1e9;
  const cuts = TL.scenes.map(s => s[0]);
  let cr = 0, br = 0, cut = 0, scene = TL.scenes[0][1];
  for (let i = 1; i < n; i++) {
    const t = i * dt;
    const cT = kurtCrank(t) ? (crankFast(t) ? 900 : 380) : 0;
    cr += (cT - cr) * (cT > cr ? kUp : kDown);
    crank[i] = crank[i - 1] + cr * dt; crankRate[i] = cr;
    const bT = beltRun(t) ? 190 : 0;
    br += (bT - br) * kBelt;
    belt[i] = belt[i - 1] + br * dt; beltRate[i] = br;
    land[i] = land[i - 1] + outV(t).v * 520 * dt;
    let atCut = false;
    while (cut < cuts.length && cuts[cut] <= t) { scene = TL.scenes[cut][1]; cut++; atCut = true; }
    for (const a of W) {
      const X = a.cx(t), Y = a.cy(t), S = Math.max(0.1, a.cs(t).v);
      const vx = segV(X.s, t), vy = segV(Y.s, t);
      a.dist[i] = a.dist[i - 1] + Math.abs(vx) / S * dt;
      const lT = clamp(vx * a.cfg.lean, -a.cfg.leanMax, a.cfg.leanMax);
      const qT = clamp(Math.abs(vy) / 3500, 0, 0.18);
      // Schnitt, Teleport oder Auftritt: Federn auf Ziel setzen, damit nichts über den Schnitt nachschwingt
      const vis = a.vis(t);
      const jump = a.px !== null && (Math.abs(X.v - a.px) > 40 || Math.abs(Y.v - a.py) > 40);
      const reset = atCut || jump || (vis && !a.wasVis);
      if (reset) { a.l = lT; a.lv = 0; a.q = qT; a.qv = 0; }
      [a.l, a.lv] = springStep(a.l, a.lv, lT, wL, zL);
      [a.q, a.qv] = springStep(a.q, a.qv, qT, wQ, zQ);
      a.lean[i] = a.l; a.squash[i] = a.q; a.px = X.v; a.py = Y.v; a.wasVis = vis;
      // Gangphase. Tauben: Schrittlänge 36..60 px wächst mit dem Tempo, höchstens 3 Doppelschritte/s
      // (bis 180 px/s stehen die Füße fest). Fussel: Hüpfer von 30..60 px.
      const vL = Math.hypot(vx, vy) / S;
      if (a.name === 'fussel') a.phase += vL / clamp(vL / 4, 30, 60) * dt;
      else a.phase += Math.min(vL / clamp(vL / 3, 36, 60), 3) * dt;
      a.ph[i] = a.phase; a.vL[i] = vL;
      if (a.name === 'fussel') {
        const fl = a.cf(t).v >= 0 ? 1 : -1, vxl = vx * fl / S, vyl = vy / S;
        if (reset) { Lx = Ly = Lvx = Lvy = jg = jv = 0; pvx = vxl; pvy = vyl; }
        // Tempo-Sprung des Körpers stößt Faden und Fell in Gegenrichtung an (Trägheit)
        Lvx -= 0.3 * (vxl - pvx); Lvy -= 0.3 * (vyl - pvy); jv -= 0.0008 * (vyl - pvy);
        pvx = vxl; pvy = vyl;
        [Lx, Lvx] = springStep(Lx, Lvx, 0, wT, zT); [Ly, Lvy] = springStep(Ly, Lvy, 0, wT, zT);
        [jg, jv] = springStep(jg, jv, 0, wJ, zJ);
        thrX[i] = 25 * Math.tanh(Lx / 25); thrY[i] = 25 * Math.tanh(Ly / 25); jig[i] = clamp(jg, -0.15, 0.15);
      }
    }
    // Sprech-Energie
    let kOpen = 0;
    for (const w of WHOS) {
      const L = LBY[w] || [];
      let k = ek[w];
      while (k < L.length && L[k].t1 <= t) k++;
      ek[w] = k;
      let o = 0;
      if (k < L.length && L[k].t0 <= t) { const p = (t - L[k].t0) * TL.envRate, j = Math.floor(p); o = lerp(L[k].env[j] || 0, L[k].env[j + 1] || 0, p - j); }
      ecur[w] = Math.max(o, ecur[w] * eDecay); EN[w][i] = ecur[w];
      if (w === 'K') kOpen = o;
    }
    [nd, ndv] = springStep(nd, ndv, kOpen, wN, zN); needle[i] = nd;
    // Blickziele mit 60 Hz
    if (i % 4 === 0 || atCut) {
      if (speakerLine(t)) lastLine = t;
      for (const g of G) {
        if (!actorVis(g.a, t, scene)) { g.vis = false; continue; }
        let tg = gazeTarget(g.a, t, scene);
        if (tg === undefined) tg = g.a === 'fussel' && t - lastLine > 1.5 ? [0, 0.1] : null;   // Pause: Fussel schaut ins Publikum
        if (tg) {
          if (g.has && g.vis && !atCut && Math.hypot(tg[0] - g.tx, tg[1] - g.ty) > 0.6) forced[g.a].push(t);   // Kopfdrehung mit Lidschlag
          g.tx = tg[0]; g.ty = tg[1]; g.has = true;
        }
        if (!g.vis || atCut) { g.ex = g.sx = g.tx; g.ey = g.sy = g.ty; g.evx = g.evy = g.svx = g.svy = 0; }
        g.vis = true;
        while (t >= g.sacT) {   // Sakkaden: kleine Blicksprünge alle 0.6–1.8 s
          g.sacN++;
          g.ox = rnd(g.gi * 7 + 1, g.sacN) * 0.12; g.oy = rnd(g.gi * 7 + 2, g.sacN) * 0.08;
          g.sacT += 0.6 + 1.2 * hash(g.gi * 7 + 3, g.sacN);
        }
      }
    }
    for (const g of G) {
      if (!g.vis) continue;
      [g.ex, g.evx] = springStep(g.ex, g.evx, g.tx + g.ox, wE, zE); [g.ey, g.evy] = springStep(g.ey, g.evy, g.ty + g.oy, wE, zE);
      [g.sx, g.svx] = springStep(g.sx, g.svx, g.tx, wS, zS); [g.sy, g.svy] = springStep(g.sy, g.svy, g.ty, wS, zS);
      g.gx[i] = g.ex; g.gy[i] = g.ey; g.lx[i] = g.sx; g.ly[i] = g.sy;
    }
  }
  Object.assign(INT, { dt, crank, crankRate, belt, beltRate, land, thrX, thrY, jig, needle });
  for (const a of W) Object.assign(INT, { ['dist_' + a.name]: a.dist, ['lean_' + a.name]: a.lean, ['squash_' + a.name]: a.squash, ['ph_' + a.name]: a.ph, ['vL_' + a.name]: a.vL });
  for (const w of WHOS) INT['en_' + w] = EN[w];
  for (const g of G) Object.assign(INT, { ['gx_' + g.a]: g.gx, ['gy_' + g.a]: g.gy, ['lx_' + g.a]: g.lx, ['ly_' + g.a]: g.ly });
}
// Kanalwert zur Zeit t, linear zwischen den 240-Hz-Stützstellen
function integ(name, t) {
  const a = INT[name], x = clamp(t / INT.dt, 0, a.length - 1.001), i = Math.floor(x);
  return a[i] + (a[i + 1] - a[i]) * (x - i);
}
function kurtSpeaking(t) { const k = lastLE(KSW, t); return k >= 0 && k % 2 === 0; }
function kurtSwitch(t) { const k = lastLE(KSW, t); return k >= 0 ? KSW[k] : -1e9; }

// ---------------------------------------------------------------------------
// Grundgerüst
// ---------------------------------------------------------------------------
const svg = document.getElementById('stage');
const defs = E('defs', null, svg);
function pattern(id, w, h, draw) {
  const p = E('pattern', { id, width: w, height: h, patternUnits: 'userSpaceOnUse' }, defs);
  draw(p);
  return p;
}
pattern('dots', 32, 32, p => E('circle', { cx: 16, cy: 16, r: 2.6, fill: 'rgba(29,26,43,0.10)' }, p));
pattern('dotsL', 32, 32, p => E('circle', { cx: 16, cy: 16, r: 2.6, fill: 'rgba(255,248,236,0.08)' }, p));
pattern('scan', 8, 8, p => E('rect', { x: 0, y: 0, width: 8, height: 3, fill: 'rgba(0,0,0,0.28)' }, p));
pattern('felt', 6, 6, p => { E('circle', { cx: 1, cy: 2, r: 0.7, fill: 'rgba(255,255,255,0.07)' }, p); E('circle', { cx: 4, cy: 5, r: 0.6, fill: 'rgba(0,0,0,0.06)' }, p); });

E('rect', { x: 0, y: 0, width: 1920, height: 1080, fill: C.ink }, svg);
const world = E('g', { id: 'world' }, svg);
const bgBack = E('g', null, world);
const trainLayer = E('g', null, world);
const bgFront = E('g', null, world);
const actorsBack = E('g', null, world);
const actors = E('g', null, world);
const actorsFront = E('g', null, world);
const fxLayer = E('g', null, world);
const overlay = E('g', null, svg);

const SC = {};
function sceneGroup(name, parent) { const g = E('g', { id: 'sc-' + name }, parent || bgBack); SC[name] = SC[name] || []; SC[name].push(g); return g; }

// ---------------------------------------------------------------------------
// Figuren
// ---------------------------------------------------------------------------
const FUR = window.FUR;
let PID = 0;   // laufende Nummer für eindeutige clipPath-IDs und Rauschphasen

// Fussel: Fellball mit Lidern, Brauen, Viseme-Mund und nachschwingendem Faden.
// Der Faden (Mittelpunkte der Bézier-Kurve) folgt dem Nachlauf L mit wachsendem Gewicht zur Spitze.
const THREAD = [[97, 36], [106, 22], [121, 24], [135, 26], [136, 42], [124, 44], [114, 46], [112, 32], [124, 22], [134, 14], [152, 14], [162, 24]];
const THREAD_W = [0.12, 0.2, 0.28, 0.36, 0.44, 0.5, 0.56, 0.62, 0.7, 0.8, 0.9, 1];
function makeFussel(parent) {
  const id = ++PID;
  const g = E('g', null, parent), inner = E('g', null, g);
  const legs = E('path', { fill: 'none', stroke: C.ink, 'stroke-width': 6, 'stroke-linecap': 'round' }, inner);
  const f1e = E('ellipse', { rx: 11, ry: 6, fill: C.ink }, inner), f2e = E('ellipse', { rx: 11, ry: 6, fill: C.ink }, inner);
  const body = E('g', null, inner);
  const thread = E('path', { fill: 'none', stroke: C.himD, 'stroke-width': 5, 'stroke-linecap': 'round' }, body);
  E('path', { d: FUR, fill: C.him }, body);
  E('path', { d: FUR, fill: 'url(#felt)' }, body);
  E('path', { d: 'M62 132q6 8 4 16M140 134q-5 8-3 15M70 80q5-6 13-7M128 76q8 2 12 9M96 158q6 3 12 0', fill: 'none', stroke: C.himD, 'stroke-width': 3, 'stroke-linecap': 'round' }, body);
  const eyes = E('g', null, body);
  // Auge: Weiß, Pupille + Glanzpunkt (auf das Weiß beschnitten), Lider (auf r + 1.5 beschnitten, damit kein heller Rand bleibt), Wimpernlinie
  const EYE = [[79, 106, 19, 9, 1], [122, 104, 15, 7.5, 0.8]];
  const eye = EYE.map(([cx, cy, r, pr, k], j) => {
    const ce = `fu${id}e${j}`, cl = `fu${id}l${j}`;
    E('circle', { cx, cy, r }, E('clipPath', { id: ce }, defs));
    E('circle', { cx, cy, r: r + 1.5 }, E('clipPath', { id: cl }, defs));
    E('circle', { cx, cy, r, fill: '#fff' }, eyes);
    const cg = E('g', { 'clip-path': `url(#${ce})` }, eyes);
    const pupil = E('circle', { r: pr, fill: C.ink }, cg), hl = E('circle', { r: pr / 3, fill: '#fff' }, cg);
    const lg = E('g', { 'clip-path': `url(#${cl})` }, eyes);
    const lidT = E('path', { fill: C.him }, lg), lidB = E('path', { fill: C.him }, lg);
    const lash = E('path', { fill: 'none', stroke: C.ink, 'stroke-width': 4, 'stroke-linecap': 'round' }, eyes);
    return { cx, cy, r, pr, k, pupil, hl, lidT, lidB, lash };
  });
  const brows = [0, 1].map(() => E('path', { fill: 'none', stroke: C.ink, 'stroke-width': 5, 'stroke-linecap': 'round' }, body));
  const mid = `fu${id}m`, mclip = E('path', null, E('clipPath', { id: mid }, defs));
  const mouthP = E('path', { fill: C.ink, stroke: C.ink, 'stroke-width': 3, 'stroke-linejoin': 'round' }, body);
  const mg = E('g', { 'clip-path': `url(#${mid})` }, body);
  const tongue = E('ellipse', { fill: C.himD }, mg), teeth = E('rect', { fill: C.garn }, mg);
  let tlen = 0;
  return {
    g, update(o) {
      // Ganzer Körper: Squash/Stretch um den Fußpunkt (100,202); face −1..1 dreht stetig (Spiegelung)
      const face = Math.abs(o.face) < 0.12 ? (o.face < 0 ? -0.12 : 0.12) : o.face;
      setT(g, `translate(${f1(o.x)},${f1(o.y)}) rotate(${f2(o.r)}) scale(${(o.s * face * o.fsx).toFixed(4)},${(o.s * o.fsy).toFixed(4)}) translate(-100,-202)`);
      // In der Luft: Strecken entlang der Flugrichtung
      setT(inner, o.m > 0.003 ? `translate(100,110) rotate(${f1(o.ang)}) scale(${f3(1 + o.m)},${f3(1 / (1 + o.m))}) rotate(${f1(-o.ang)}) translate(-100,-110)` : '');
      // Rumpf: Atmen/Sprechen (Volumen bleibt), Anheben auf Betonungen; Füße bleiben stehen
      const bsy = o.bsy, bsx = 1 - 0.6 * (bsy - 1), lift = o.lift || 0;
      setT(body, `translate(100,${f2(172 - lift)}) scale(${(bsx).toFixed(4)},${(bsy).toFixed(4)}) translate(-100,-172)`);
      // Faden: Nachlauf + leichtes Schweben; Locke zieht sich bei großen Augen zusammen
      const sx = 2.5 * Math.sin(1.7 * o.t) + (o.Lx || 0), sy = 1.5 * Math.sin(2.3 * o.t + 1) + (o.Ly || 0), cu = 1 - 0.15 * (o.curl || 0);
      const P = THREAD.map(([px, py], j) => {
        if (j >= 2 && j <= 8) { px = 126 + (px - 126) * cu; py = 34 + (py - 34) * cu; }
        const w = THREAD_W[j];
        return `${f1(px + w * sx)} ${f1(py + w * sy - (j >= 9 ? (o.tip || 0) * (j - 8) / 3 : 0))}`;
      });
      setA(thread, 'd', `M101 52C${P[0]} ${P[1]} ${P[2]}C${P[3]} ${P[4]} ${P[5]}C${P[6]} ${P[7]} ${P[8]}C${P[9]} ${P[10]} ${P[11]}`);
      if (!tlen) tlen = thread.getTotalLength();
      setA(thread, 'stroke-dasharray', `${f1(tlen * o.thread)} 400`);
      // Beine: Ansatz folgt der Rumpfunterkante; Füße stehen, spreizen (Landung), ziehen an (Luft), sitzen
      const hy = 172 - 6 * bsy - lift, h0 = 100 - 14 * bsx, h1 = 100 + 14 * bsx, hyS = lerp(hy, 160, o.sit);
      let ax = 82 - 6 * o.splay, bx = 118 + 6 * o.splay, ay = 194, by = 194;
      ax = lerp(ax, h0 + 5, o.tuck); bx = lerp(bx, h1 - 5, o.tuck); ay = lerp(ay, hy + 21, o.tuck); by = ay;
      ax = lerp(ax, 74, o.sit); bx = lerp(bx, 126, o.sit); ay = lerp(ay, 182, o.sit); by = lerp(by, 182, o.sit);
      setA(legs, 'd', `M${f1(h0)} ${f1(hyS)}L${f1(ax)} ${f1(ay)}M${f1(h1)} ${f1(hyS)}L${f1(bx)} ${f1(by)}`);
      setA(f1e, 'cx', f1(ax - 4)); setA(f1e, 'cy', f1(ay + 2)); setA(f2e, 'cx', f1(bx + 4)); setA(f2e, 'cy', f1(by + 2));
      // Augen
      const sc = o.eyeScale;
      setT(eyes, `translate(100,105) scale(${f3(sc)}) translate(-100,-105)`);
      const c = clamp(Math.max(o.lid, o.blink), 0, 1);
      for (const e of eye) {
        const { cx, cy, r, pr, k } = e;
        const px = cx + 1 + 7 * k * o.lx, py = cy + 2 + 6 * k * o.ly;
        setA(e.pupil, 'cx', f1(px)); setA(e.pupil, 'cy', f1(py)); setA(e.pupil, 'r', f2(pr * (1 + 0.12 * o.wide)));
        setA(e.hl, 'cx', f1(px + 3 * k - 2.5 * k * o.lx)); setA(e.hl, 'cy', f1(py - 3.5 * k - 2 * k * o.ly));
        const yE = cy - r + 2 * r * c, bow = 3 + 4 * c;
        show(e.lidT, c > 0.01);
        if (c > 0.01) setA(e.lidT, 'd', `M${cx - r - 2} ${cy - r - 2}H${cx + r + 2}V${f1(yE)}Q${cx} ${f1(yE + bow)} ${cx - r - 2} ${f1(yE)}Z`);
        const q = clamp(o.squint, 0, 1) * (1 - c);
        show(e.lidB, q > 0.01);
        if (q > 0.01) { const yB = cy + r - 1.2 * r * q; setA(e.lidB, 'd', `M${cx - r - 2} ${cy + r + 2}H${cx + r + 2}V${f1(yB)}Q${cx} ${f1(yB - 9 * q)} ${cx - r - 2} ${f1(yB)}Z`); }
        show(e.lash, c > 0.06);
        if (c > 0.06) {
          const half = Math.sqrt(Math.max(0, r * r - (yE - cy) * (yE - cy))), hw = Math.max(half, 0.8 * r * smooth((c - 0.75) / 0.2));
          setA(e.lash, 'd', `M${f1(cx - hw)} ${f1(yE)}Q${cx} ${f1(yE + bow * 1.6)} ${f1(cx + hw)} ${f1(yE)}`);
        }
      }
      // Brauen: raise hebt, tilt + = traurig (innen hoch), − = böse (innen runter)
      const b = 7 * o.raise + 6 * o.wide, ti = 6 * o.tilt;
      setA(brows[0], 'd', `M64 ${f1(86 - b + 0.3 * ti)}Q78 ${f1(76 - b)} 92 ${f1(82 - b - ti)}`);
      setA(brows[1], 'd', `M112 ${f1(81 - b - ti)}Q123 ${f1(74 - b)} 135 ${f1(83 - b + 0.3 * ti)}`);
      // Mund: o = auf, w = breit (0 rund), s = Zischlaut (Zähne), smile hebt die Mundwinkel
      const mo = o.mo, w = o.mw, s = o.ms, mx = 103, my = 139;
      let hw = 6 + 3 * mo + 10 * w * (0.35 + 0.65 * mo), h = 1.5 + mo * (19 - 6 * w);
      if (s > 0.3) { const k = smooth((s - 0.3) / 0.15); hw = lerp(hw, Math.max(hw, 10 + 2 * s), k); h = lerp(h, Math.max(h, 5 + 2 * s), k); }
      const ht = h * (0.42 - 0.3 * w), hb = h - ht, cyC = my - 3 * o.smile;
      const d = `M${f1(mx - hw)} ${f1(cyC)}C${f1(mx - 0.6 * hw)} ${f1(my - 1.3 * ht)} ${f1(mx + 0.6 * hw)} ${f1(my - 1.3 * ht)} ${f1(mx + hw)} ${f1(cyC)}C${f1(mx + 0.9 * hw)} ${f1(my + 1.33 * hb)} ${f1(mx - 0.9 * hw)} ${f1(my + 1.33 * hb)} ${f1(mx - hw)} ${f1(cyC)}Z`;
      setA(mouthP, 'd', d); setA(mclip, 'd', d);
      show(tongue, h > 9);
      if (h > 9) { setA(tongue, 'cx', mx); setA(tongue, 'cy', f1(my + hb)); setA(tongue, 'rx', f1(0.6 * hw)); setA(tongue, 'ry', f1(0.5 * hb)); }
      const th = s > 0.3 ? (h + 2) * smooth((s - 0.3) / 0.1) : (w > 0.6 && mo > 0.4 ? 4 * smooth((mo - 0.4) / 0.1) : 0);
      show(teeth, th > 0.3);
      if (th > 0.3) { setA(teeth, 'x', f1(mx - hw)); setA(teeth, 'y', f1(my - 1.3 * ht - 2)); setA(teeth, 'width', f1(2 * hw)); setA(teeth, 'height', f1(th)); }
    }
  };
}

function makeKurt(parent) {
  const g = E('g', null, parent), inner = E('g', null, g);
  const steam = E('g', null, inner);
  const puffs = [];
  for (let i = 0; i < 7; i++) puffs.push(E('circle', { fill: C.garn, opacity: 0.8 }, steam));
  const funnel = E('g', null, inner);   // Trichter wippt mit Betonungen und federt beim "Plopp"
  E('rect', { x: 101, y: 40, width: 18, height: 24, fill: C.petDD }, funnel);
  E('path', { d: 'M70 10H150L124 46H96Z', fill: C.garn }, funnel);
  E('path', { d: 'M118 10H150L124 46H112Z', fill: C.garnD }, funnel);
  E('ellipse', { cx: 110, cy: 10, rx: 40, ry: 7, fill: C.ink }, funnel);
  E('rect', { x: 58, y: 226, width: 26, height: 30, rx: 4, fill: C.ink }, inner);
  E('rect', { x: 146, y: 226, width: 26, height: 30, rx: 4, fill: C.ink }, inner);
  E('rect', { x: 50, y: 250, width: 42, height: 12, rx: 6, fill: C.ink }, inner);
  E('rect', { x: 138, y: 250, width: 42, height: 12, rx: 6, fill: C.ink }, inner);
  const crank = E('g', null, inner);
  E('path', { d: 'M200 128L222 104', stroke: C.ink, 'stroke-width': 9, 'stroke-linecap': 'round' }, crank);
  E('rect', { x: 215, y: 82, width: 16, height: 26, rx: 8, fill: C.him }, crank);
  E('rect', { x: 30, y: 60, width: 170, height: 172, rx: 28, fill: C.pet }, inner);
  E('rect', { x: 30, y: 60, width: 170, height: 172, rx: 28, fill: 'url(#felt)' }, inner);
  E('path', { d: 'M30 200H200V204A28 28 0 0 1 172 232H58A28 28 0 0 1 30 204Z', fill: C.petD }, inner);
  E('circle', { cx: 200, cy: 128, r: 9, fill: C.ink }, inner);
  E('circle', { cx: 115, cy: 128, r: 54, fill: C.petDD }, inner);
  const scr = E('circle', { cx: 115, cy: 128, r: 44, fill: C.screen }, inner);
  const cid = 'kclip' + (++PID);
  const cp = E('clipPath', { id: cid }, defs); E('circle', { cx: 115, cy: 128, r: 43 }, cp);
  const content = E('g', { 'clip-path': `url(#${cid})` }, inner);
  const disp = E('g', null, content);   // Bildinhalt; klappt beim Umschalten wie eine Röhre auf
  const face = E('g', null, disp);
  const e1 = E('rect', { x: 91, y: 110, width: 15, height: 20, rx: 2, fill: C.senf }, face);
  const e2 = E('rect', { x: 124, y: 110, width: 15, height: 20, rx: 2, fill: C.senf }, face);
  const mouthR = E('rect', { x: 99, y: 146, width: 32, height: 5, rx: 2, fill: C.senf }, face);
  const teeth = [0, 1, 2].map(() => E('rect', { height: 2.6, rx: 1.3, fill: C.senf }, face));
  const load = E('g', null, disp); const dots = [];
  for (let i = 0; i < 8; i++) dots.push(E('rect', { width: 7, height: 7, rx: 1, fill: C.senf }, load));
  const err = E('g', null, disp);
  E('path', { d: 'M90 108l16 18M106 108l-16 18M124 108l16 18M140 108l-16 18', stroke: C.senf, 'stroke-width': 5, 'stroke-linecap': 'round' }, err);
  const errMouth = E('path', { d: 'M96 150l6-6 6 6 6-6 6 6 6-6', fill: 'none', stroke: C.senf, 'stroke-width': 4, 'stroke-linejoin': 'round' }, err);
  const boot = E('rect', { x: 71, y: 126, width: 88, height: 4, fill: C.garn }, disp);
  const film = E('g', null, disp);
  E('rect', { x: 70, y: 84, width: 90, height: 90, fill: '#163A3E' }, film);
  E('rect', { x: 70, y: 150, width: 90, height: 30, fill: '#0B2427' }, film);
  const ftrain = E('g', null, film);
  E('rect', { x: 0, y: 0, width: 44, height: 14, rx: 5, fill: C.senf }, ftrain);
  E('rect', { x: 5, y: 3, width: 6, height: 5, fill: C.screen }, ftrain); E('rect', { x: 16, y: 3, width: 6, height: 5, fill: C.screen }, ftrain); E('rect', { x: 27, y: 3, width: 6, height: 5, fill: C.screen }, ftrain);
  const fcloud = E('g', null, film);
  E('rect', { x: 0, y: 0, width: 18, height: 6, rx: 3, fill: C.garn, opacity: 0.6 }, fcloud);
  const ans = E('g', null, disp); const bars = [];
  for (let i = 0; i < 7; i++) bars.push(E('rect', { x: 84 + i * 9, width: 6, rx: 2, fill: C.senf }, ans));
  const scan = E('rect', { x: 70, y: 84, width: 90, height: 90, fill: 'url(#scan)', opacity: 0.5 }, inner);
  E('circle', { cx: 132, cy: 104, r: 4, fill: '#fff', opacity: 0.18 }, inner);
  E('rect', { x: 80, y: 205, width: 70, height: 20, rx: 3, fill: C.senf }, inner);
  T(E('text', { x: 115, y: 219.5, 'text-anchor': 'middle', 'font-family': FONT.mono, 'font-size': 11, 'font-weight': 500, fill: C.ink, 'letter-spacing': 1 }, inner), 'K.U.R.T.');
  E('circle', { cx: 56, cy: 215, r: 9, fill: C.garn }, inner);
  const n1 = E('path', { stroke: C.ink, 'stroke-width': 2.5, 'stroke-linecap': 'round' }, inner);
  E('circle', { cx: 174, cy: 215, r: 9, fill: C.garn }, inner);
  const n2 = E('path', { stroke: C.ink, 'stroke-width': 2.5, 'stroke-linecap': 'round' }, inner);
  return {
    g, update(o) {
      const sh = o.shake, t = o.t;   // stetiges Rattern statt Zufallssprüngen pro Bild
      const jx = sh * 7 * rattle(t, 1), jy = sh * 4 * rattle(t, 2), jr = sh * 1.5 * rattle(t, 3);
      // Betonung: Gehäuse staucht minimal um die Füße
      setT(g, `translate(${f1(o.x + jx)},${f1(o.y + jy)}) rotate(${f2(o.r + jr)}) scale(${o.s},${(o.s * (1 - 0.012 * o.pulse)).toFixed(4)}) translate(-115,-262)`);
      setT(funnel, `rotate(${f2(o.funnelR)},110,46) translate(110,46) scale(${f3(1 + 0.6 * (1 - o.funnelSq))},${f3(o.funnelSq)}) translate(-110,-46)`);
      setT(crank, `rotate(${(o.crank % 360).toFixed(1)},200,128)`);
      // Zeiger: links VU-Meter seiner Stimme, rechts "hört zu"; mit Kurbeldrehzahl zittern beide
      const cw = clamp(o.crankRate / 380, 0, 1);
      const na = lerp(o.n1, Math.sin(t * 9) * 0.9, cw), nb = lerp(o.n2, Math.cos(t * 7) * 0.9, cw);
      setA(n1, 'd', `M56 215L${f1(56 + Math.sin(na) * 7)} ${f1(215 - Math.cos(na) * 7)}`);
      setA(n2, 'd', `M174 215L${f1(174 + Math.sin(nb) * 7)} ${f1(215 - Math.cos(nb) * 7)}`);
      setA(scan, 'opacity', f3(0.5 + 0.05 * Math.sin(t * 1.3)));
      const mode = o.mode;
      setA(scr, 'fill', mode === 'red' ? '#4A1027' : (mode === 'off' ? '#0A1719' : C.screen));
      show(face, mode === 'on' || mode === 'glitch');
      show(load, mode === 'load'); show(err, mode === 'red'); show(boot, mode === 'boot');
      show(film, mode === 'film'); show(ans, mode === 'ansage');
      // Röhren-Umschalten: neuer Inhalt klappt in 0.12 s aus einer Linie auf
      setT(disp, o.flip < 0.999 ? `translate(0,128) scale(1,${f3(o.flip)}) translate(0,-128)` : '');
      if (mode === 'on' || mode === 'glitch') {
        const gk = Math.floor(t * 15);   // Glitch: bewusst gestuft, aber 15 Hz und an t gebunden
        const gx = mode === 'glitch' ? rnd(gk, 9) * 8 : 0;
        setT(face, `translate(0,${f2(-2.5 * o.pulse)})`);
        const eh = Math.max(1.5, lerp(lerp(20, 12, o.squint), 2, o.blink) + 4 * o.pulse), ex = o.lx * 6, ey = 120 + o.ly * 4;
        setA(e1, 'height', f1(eh)); setA(e2, 'height', f1(eh));
        setA(e1, 'y', f1(ey - eh / 2)); setA(e2, 'y', f1(ey - eh / 2));
        setA(e1, 'x', f1(91 + gx + ex)); setA(e2, 'x', f1(124 - gx + ex));
        setA(e1, 'fill', mode === 'glitch' && gk % 2 ? C.him : C.senf);
        // Mund: breiter bei breiten Lauten, höher beim Öffnen; Zischlaute als drei Zahnreihen
        const mw = 28 + 12 * o.mw, mh = 4 + 18 * o.mo, k = smooth((o.ms - 0.35) / 0.15);
        setA(mouthR, 'width', f1(mw)); setA(mouthR, 'x', f1(115 - mw / 2 + ex * 0.5));
        setA(mouthR, 'height', f1(mh)); setA(mouthR, 'y', f1(148.5 - mh / 2)); setA(mouthR, 'rx', f1(2 + 5 * (1 - o.mw) * o.mo));
        setA(mouthR, 'opacity', f2(1 - k));
        teeth.forEach((b, i) => { show(b, k > 0.01); if (k > 0.01) { setA(b, 'x', f1(115 - mw / 2 + ex * 0.5)); setA(b, 'width', f1(mw)); setA(b, 'y', f1(143 + i * 4.4)); setA(b, 'opacity', f2(k)); } });
      }
      if (mode === 'load') {
        const k = Math.floor(t * 12);   // LED-Spinner: 12 Schritte/s = 1.5 Umdrehungen/s
        for (let i = 0; i < 8; i++) {
          const a = i / 8 * Math.PI * 2;
          setA(dots[i], 'x', f1(115 + Math.cos(a) * 20 - 3.5)); setA(dots[i], 'y', f1(128 + Math.sin(a) * 20 - 3.5));
          setA(dots[i], 'opacity', f2(((i - k) % 8 + 8) % 8 / 8 * 0.85 + 0.15));
        }
      }
      if (mode === 'red') setT(errMouth, `translate(0,${(Math.floor(t * 8) % 2) * 2})`);
      if (mode === 'boot') { const u = clamp(o.sinceScreen / 1.2, 0, 1); setA(boot, 'width', f1(88 * u)); setA(boot, 'x', f1(115 - 44 * u)); setA(boot, 'height', f1(2 + 30 * u * u)); setA(boot, 'y', f1(128 - (1 + 15 * u * u))); }
      if (mode === 'film') {
        const u = (t * 0.35) % 1;
        setT(ftrain, `translate(${f1(170 - u * 140)},${f1(140 + Math.sin(t * 3) * 2)})`);
        setT(fcloud, `translate(${f1(60 + ((t * 12) % 110))},100)`);
      }
      if (mode === 'ansage') for (let i = 0; i < 7; i++) { const h = 6 + o.ansAmp * 40 * (0.5 + 0.5 * Math.abs(Math.sin(i * 1.7 + t * 14))); setA(bars[i], 'height', f1(h)); setA(bars[i], 'y', f1(128 - h / 2)); }
      show(steam, o.steam);
      if (o.steam) for (let i = 0; i < puffs.length; i++) {
        const u = ((t * 0.9 + i / puffs.length) % 1);
        setA(puffs[i], 'cx', f1(110 + Math.sin(i * 2.3 + t) * 18 * u)); setA(puffs[i], 'cy', f1(0 - u * 120));
        setA(puffs[i], 'r', f1(8 + u * 26)); setA(puffs[i], 'opacity', f2(0.85 * (1 - u)));
      }
    }
  };
}

// Taube (Brösel, Gurrmann, Statisten): Schnabel mit Mundinnerem, gebogenes Lid mit Brauen-Neigung,
// Kehle pumpt beim Sprechen, Füße setzen beim Gehen nach Weg auf, Kopf ruckt vor und hält.
function makePigeon(parent, opt) {
  opt = Object.assign({ body: C.taube, wingC: C.taubeD, hat: 'none', neck: true, board: false }, opt || {});
  const id = ++PID;
  const g = E('g', null, parent);
  const legStyle = { fill: 'none', stroke: C.him, 'stroke-width': 6, 'stroke-linecap': 'round' };
  const ghost = E('path', Object.assign({ opacity: 0 }, legStyle), g);   // Bein-Wischer bei schnellem Gehen
  const legs = E('path', legStyle, g);
  const inner = E('g', null, g);
  const farWing = E('path', { d: 'M120 130C140 80 190 60 214 70C200 100 170 130 126 146Z', fill: opt.wingC, opacity: 0.85 }, inner);
  const tail = E('g', null, inner);
  E('path', { d: 'M168 134L226 112L214 170Z', fill: opt.wingC }, tail);
  E('ellipse', { cx: 118, cy: 150, rx: 74, ry: 58, fill: opt.body }, inner);
  E('ellipse', { cx: 118, cy: 150, rx: 74, ry: 58, fill: 'url(#felt)' }, inner);
  const neck = E('g', null, inner);
  if (opt.neck) {
    E('path', { d: 'M60 124C72 100 104 98 116 112C104 132 74 140 60 124Z', fill: C.pet }, neck);
    E('path', { d: 'M70 136C84 128 102 128 112 134C100 144 82 146 70 136Z', fill: C.him, opacity: 0.6 }, neck);
  }
  const wing = E('g', null, inner);
  E('path', { d: 'M118 132C150 118 186 128 190 156C176 180 136 182 120 166C112 156 112 140 118 132Z', fill: opt.wingC }, wing);
  const board = E('g', null, wing);
  E('rect', { x: 146, y: 150, width: 44, height: 54, rx: 4, fill: C.garn, transform: 'rotate(8 168 177)' }, board);
  E('rect', { x: 158, y: 146, width: 20, height: 9, rx: 3, fill: C.ink, transform: 'rotate(8 168 177)' }, board);
  E('path', { d: 'M156 168H182M155 178H180M154 188H172', stroke: C.taube, 'stroke-width': 3, 'stroke-linecap': 'round', transform: 'rotate(8 168 177)' }, board);
  const broom = E('g', null, wing);
  E('path', { d: 'M150 150L60 250', stroke: C.wood, 'stroke-width': 7, 'stroke-linecap': 'round' }, broom);
  E('path', { d: 'M40 236L82 262L70 282L28 258Z', fill: C.senfDD }, broom);
  E('path', { d: 'M34 252L28 274M44 258L38 280M54 264L48 286M64 270L58 290', stroke: C.senfDD, 'stroke-width': 4, 'stroke-linecap': 'round' }, broom);
  const head = E('g', null, inner);
  E('circle', { cx: 78, cy: 84, r: 36, fill: opt.body }, head);
  const inside = E('path', { fill: C.himD }, head);
  const lower = E('path', { d: 'M47 98L22 102.5L46 107Z', fill: C.ink }, head);
  E('path', { d: 'M45 89L19 100.5L47 99.5Z', fill: C.ink }, head);
  E('ellipse', { cx: 47, cy: 91, rx: 5, ry: 4, fill: C.garn }, head);
  const cid = 'eye' + id;
  const cp = E('clipPath', { id: cid }, defs); E('circle', { cx: 68, cy: 82, r: 12.5 }, cp);
  E('circle', { cx: 68, cy: 82, r: 11, fill: '#fff' }, head);
  const pupil = E('circle', { cx: 66, cy: 85, r: 5, fill: C.ink }, head);
  const lidG = E('g', { 'clip-path': `url(#${cid})` }, head);
  const lid = E('path', { fill: opt.wingC }, lidG);
  const lidLine = E('path', { fill: 'none', stroke: C.ink, 'stroke-width': 2.8, 'stroke-linecap': 'round' }, head);
  if (opt.hat === 'helmet') {
    E('path', { d: 'M42 64A37 37 0 0 1 114 64Z', fill: C.garn }, head);
    E('path', { d: 'M72 29A37 37 0 0 1 86 29V64H72Z', fill: C.garnD }, head);
    E('rect', { x: 36, y: 60, width: 86, height: 10, rx: 5, fill: C.garnD }, head);
  } else if (opt.hat === 'cap') {
    E('path', { d: 'M48 62C48 36 108 36 108 58Z', fill: C.pet }, head);
    E('rect', { x: 49, y: 54, width: 59, height: 9, fill: C.senf }, head);
    E('path', { d: 'M52 62L24 66C26 58 40 56 52 58Z', fill: C.ink }, head);
    E('circle', { cx: 78, cy: 46, r: 4, fill: C.senf }, head);
  }
  show(board, opt.board);
  const T0 = 1.6 + 0.5 * hash(id, 1);   // Takt der Kopfrucke im Stehen
  // Beine (lokal, Blickrichtung = −x). Gehen: Stand- (Fuß gleitet mit Körpertempo nach hinten) und Schwungphase.
  function legD(wp, wa, S, hipDy, fl, si) {
    const hip = [[96, 200 + hipDy], [126, 202 + hipDy]], foot = [[90, 222], [130, 224]];
    let out = '';
    const toe = (1 - si) * (1 - fl);
    for (let i = 0; i < 2; i++) {
      let [fx, fy] = foot[i];
      if (wa > 0.001) {
        const p = frac(wp + i / 2);
        const f = p < 0.5 ? S / 4 - S * p : -S / 4 + S / 2 * smootherstep((p - 0.5) / 0.5);
        fx -= f * wa; fy -= (p < 0.5 ? 0 : 9 * Math.sin(Math.PI * (p - 0.5) / 0.5)) * wa;
      }
      let [hx, hy] = hip[i];
      fx = lerp(fx, i ? 118 : 86, si); fy = lerp(fy, i ? 212 : 210, si);
      hx = lerp(hx, i ? 124 : 100, fl); hy = lerp(hy, i ? 198 : 196, fl); fx = lerp(fx, i ? 134 : 112, fl); fy = lerp(fy, 206, fl);
      out += `M${f1(hx)} ${f1(hy)}L${f1(fx)} ${f1(fy)}`;
      if (toe > 0.05) out += `M${f1(fx - 12 * toe)} ${f1(fy + 2)}H${f1(fx + 10 * toe)}`;
    }
    return out;
  }
  return {
    g, opt, update(o) {
      const t = o.t, ph = o.ph || 0;
      let face = o.face;
      if (Math.abs(face) < 0.12) face = face < 0 ? -0.12 : 0.12;
      setT(g, `translate(${f1(o.x)},${f1(o.y)}) rotate(${f2(o.r || 0)}) scale(${(o.s * face * (o.sx || 1)).toFixed(4)},${(o.s * (o.sy || 1)).toFixed(4)}) translate(-110,-226)`);
      const wa = o.walkAmt || 0, wp = o.wp || 0, S = o.stride || 40, fl = o.fly || 0, si = o.sit || 0;
      // Rumpf: atmen (Fußpunkt fest), beim Gehen zwei Senken pro Doppelschritt und Watscheln
      const b = o.breath || 0;
      const bob = -4 * Math.abs(Math.sin(2 * Math.PI * wp)) * wa - (o.bodyUp || 0);
      const wad = 2.5 * Math.sin(2 * Math.PI * wp) * wa;
      setT(inner, `translate(0,${f2(bob)}) rotate(${f2(wad)},118,220) translate(110,226) scale(${(1 - 0.5 * b).toFixed(4)},${(1 + b).toFixed(4)}) translate(-110,-226)`);
      // Schwanz wippt dem Rumpf hinterher
      const tr = 2 * Math.sin(2 * Math.PI * (t - 0.15) / (o.period || 3.1) + ph) + 2 * wob(t * 1.6, id * 0.37) - 3 * Math.sin(2 * Math.PI * (wp - 0.15)) * wa;
      setT(tail, `rotate(${f2(tr)},172,138)`);
      const hipDy = bob - 26 * b;
      setA(legs, 'd', legD(wp, wa, S, hipDy, fl, si));
      show(ghost, (o.smear || 0) > 0.01);
      if ((o.smear || 0) > 0.01) { setA(ghost, 'd', legD(wp - 0.08, wa, S, hipDy, fl, si)); setA(ghost, 'opacity', f2(o.smear)); }
      // Flügel: Pose (wing), Kurbeln, Fegen, Flattern – jeweils weich überblendet
      let wr = -(o.wing || 0) * 55;
      if (o.crankAmt) wr = lerp(wr, -25 + Math.sin(o.crankA * Math.PI / 180) * 18, o.crankAmt);
      if (o.sweepAmt) wr = lerp(wr, Math.sin(t * 6) * 14, o.sweepAmt);
      if (fl > 0) wr = lerp(wr, -20 - 45 * (0.5 + 0.5 * Math.sin(t * 26 + ph)), fl);
      setT(wing, `rotate(${f1(wr)},125,138)`);
      show(farWing, fl > 0.02);
      if (fl > 0.02) { setT(farWing, `rotate(${f1(lerp(-10, -30 + 50 * Math.sin(t * 26 + ph + 0.6), fl))},126,140)`); setA(farWing, 'opacity', f2(0.85 * fl)); }
      show(broom, !!o.broom);
      if (o.broom) setT(broom, 'rotate(25,150,150)');
      // Kopf: kurzer Ruck (0.1 s), dann stillhalten; dazu Picken, Nicken, Blick. Beim Gehen: Kopf stößt vor und bleibt in der Welt stehen.
      const q = (t + ph) / T0, k = Math.floor(q), su = (q - k) * T0;
      let hr = (o.head || 0) + (o.snap === undefined ? 7 : o.snap) * (1 - wa) * lerp(rnd(k - 1, id), rnd(k, id), smootherstep(su / 0.1));
      hr += (o.peck || 0) + (o.hr || 0);
      if (o.crankAmt) hr += Math.sin(o.crankA * Math.PI / 180) * 9 * o.crankAmt;
      let hx = 0, hy = 0;
      if (wa > 0.001) {
        const qq = frac(2 * wp), A = 0.35 * S / 2;
        if (qq < 0.3) { hx = lerp(A, -A, easeOut(qq / 0.3)); hy = 2.5 * Math.sin(Math.PI * qq / 0.3); } else hx = lerp(-A, A, (qq - 0.3) / 0.7);
        hx *= wa; hy *= wa;
      }
      setT(head, `translate(${f2(hx)},${f2(hy)}) rotate(${f1(hr)},92,118)`);
      // Schnabel: Unterschnabel klappt auf, das Mundinnere folgt der Spitze
      const op = clamp(o.open || 0, 0, 1.2), ba = -(op * 24 + 6 * (o.ex || 0) * op);
      setT(lower, `rotate(${f1(ba)},47,101)`);
      const th = ba * Math.PI / 180, cs = Math.cos(th), sn = Math.sin(th);
      setA(inside, 'd', `M47 97L21 100.5L${f1(47 - 25 * cs - 1.5 * sn)} ${f1(101 - 25 * sn + 1.5 * cs)}L47 104Z`);
      setT(neck, `translate(88,130) scale(1,${f3(1 + 0.08 * (o.puff || 0))}) translate(-88,-130)`);
      // Lid: gebogen, brow −1 = böse, +1 = besorgt
      const lv = clamp(Math.max(o.lid || 0, o.blink || 0), 0, 1), y = 70 + 24 * lv, ta = 4 * (o.brow || 0);
      setA(lid, 'd', `M54 66H84V${f1(y - ta)}Q68 ${f1(y + 3)} 54 ${f1(y + ta)}Z`);
      setA(lidLine, 'd', `M55.5 ${f1(y + 1.2 * ta)}Q68 ${f1(y + 3.5)} 80.5 ${f1(y - 1.2 * ta)}`);
      setA(lidLine, 'opacity', f2(smooth((lv - 0.02) / 0.08)));
      setA(pupil, 'cx', f1(66 + (o.px || 0))); setA(pupil, 'cy', f1(85 + (o.py || 0)));
    }
  };
}

function makeBall(parent) {
  const g = E('g', null, parent);
  E('circle', { r: 16, fill: C.him }, g);
  E('path', { d: 'M-12 -4Q0 -14 13 2M-13 5Q0 -4 10 10', fill: 'none', stroke: C.himD, 'stroke-width': 3, 'stroke-linecap': 'round' }, g);
  return g;
}

function makeTrain(parent) {
  const g = E('g', null, parent);
  const farW = E('g', null, g), body = E('g', null, g), nearW = E('g', null, g);
  function wingShape(p, fill, shade) {
    E('path', { d: 'M0 0C-60 -140 -260 -250 -430 -230C-420 -200 -380 -190 -360 -180C-390 -170 -400 -150 -390 -130C-360 -130 -330 -125 -310 -115C-330 -100 -335 -80 -320 -65C-260 -70 -150 -40 -60 20Z', fill }, p);
    E('path', { d: 'M-60 -60C-150 -120 -260 -170 -350 -190M-60 -30C-160 -80 -250 -110 -320 -120M-60 0C-150 -40 -230 -60 -300 -70', fill: 'none', stroke: shade, 'stroke-width': 8, 'stroke-linecap': 'round' }, p);
  }
  const fw = E('g', null, farW); wingShape(fw, C.garnD, C.taube);
  const nw = E('g', null, nearW); wingShape(nw, C.garn, C.garnD);
  E('path', { d: 'M-700 -330H800Q850 -330 850 -280V-60H-850V-180Q-850 -330 -700 -330Z', fill: C.pet }, body);
  E('path', { d: 'M-700 -330H800Q850 -330 850 -280V-60H-850V-180Q-850 -330 -700 -330Z', fill: 'url(#felt)' }, body);
  E('rect', { x: -850, y: -160, width: 1700, height: 26, fill: C.senf }, body);
  E('rect', { x: -850, y: -90, width: 1700, height: 30, fill: C.petD }, body);
  E('path', { d: 'M-830 -250Q-800 -300 -720 -300H-640V-200H-835Z', fill: C.screen }, body);
  const heads = [];
  const wins = [-560, -420, -140, 0, 140, 420, 560, 700];
  for (const x of wins) {
    E('rect', { x: x - 50, y: -300, width: 100, height: 90, rx: 14, fill: C.garn }, body);
    if (Math.abs(x) % 280 !== 0) { const h = E('g', null, body); E('circle', { cx: x, cy: -232, r: 24, fill: C.taube }, h); E('path', { d: `M${x - 22} -228l-14 5 15 3z`, fill: C.ink }, h); E('circle', { cx: x - 9, cy: -238, r: 4, fill: C.ink }, h); heads.push(h); }
  }
  const doors = [];
  for (const x of [-280, 280]) {
    E('rect', { x: x - 60, y: -310, width: 120, height: 250, fill: C.ink2 }, body);
    const l = E('rect', { x: x - 58, y: -306, width: 58, height: 244, fill: C.petD }, body);
    const r = E('rect', { x: x, y: -306, width: 58, height: 244, fill: C.petD }, body);
    E('rect', { x: x - 48, y: -290, width: 38, height: 60, rx: 6, fill: C.garnD }, body);
    doors.push([l, r, x]);
  }
  T(E('text', { x: 160, y: -100, 'font-family': FONT.bagel, 'font-size': 44, fill: C.garn }, body), 'Taubenbahn');
  const wheels = [];
  for (const x of [-640, -540, 540, 640]) {
    const w = E('g', null, body);
    E('circle', { r: 38, fill: C.ink }, w); E('path', { d: 'M-30 0H30M0 -30V30', stroke: C.ink2, 'stroke-width': 7 }, w); E('circle', { r: 9, fill: C.taube }, w);
    wheels.push([w, x]);
  }
  E('rect', { x: -700, y: -70, width: 220, height: 26, rx: 8, fill: C.ink }, body); E('rect', { x: 480, y: -70, width: 220, height: 26, rx: 8, fill: C.ink }, body);
  return {
    g, update(o) {
      setT(g, `translate(${o.x.toFixed(1)},${o.y.toFixed(1)}) rotate(${o.r.toFixed(2)}) scale(${o.s})`);
      for (const [w, x] of wheels) setT(w, `translate(${x},-38) rotate(${(-o.x * 1.5 % 360).toFixed(1)})`);
      for (const [l, r, x] of doors) { setA(l, 'x', (x - 58 - o.doors * 52).toFixed(1)); setA(r, 'x', (x + o.doors * 52).toFixed(1)); }
      show(farW, o.wings); show(nearW, o.wings);
      if (o.wings) {
        const fl = o.flap ? Math.sin(o.t * 7) * 28 : 0;
        setT(fw, `translate(120,-320) rotate(${(20 + fl * 0.8).toFixed(1)})`);
        setT(nw, `translate(-60,-300) rotate(${(-6 + fl).toFixed(1)})`);
      }
      heads.forEach((h, i) => setT(h, `translate(0,${(Math.sin(o.t * 5 + i) * 3).toFixed(1)})`));
    }
  };
}
function makeMiniTrain(parent) {
  const g = E('g', null, parent);
  E('path', { d: 'M0 0C-20 -50 -90 -80 -140 -70C-110 -55 -100 -40 -90 -20Z', fill: C.garnD }, g);
  E('rect', { x: -110, y: -40, width: 220, height: 50, rx: 18, fill: C.pet }, g);
  E('rect', { x: -110, y: -10, width: 220, height: 7, fill: C.senf }, g);
  for (const x of [-80, -40, 0, 40, 80]) E('rect', { x: x - 12, y: -32, width: 24, height: 16, rx: 4, fill: C.garn }, g);
  const w = E('path', { d: 'M0 -30C-20 -80 -90 -110 -140 -100C-110 -85 -100 -70 -90 -50Z', fill: C.garn }, g);
  return { g, w };
}

// ---------------------------------------------------------------------------
// Szenen
// ---------------------------------------------------------------------------
const H = {}; // dynamische Teile der Kulissen

(function buildHalle() {
  const g = sceneGroup('halle');
  E('rect', { x: 0, y: 0, width: 1920, height: 700, fill: C.senf }, g);
  E('rect', { x: 0, y: 0, width: 1920, height: 700, fill: 'url(#dots)' }, g);
  E('rect', { x: 0, y: 560, width: 1920, height: 140, fill: C.senfD }, g);
  for (let x = 30; x < 1920; x += 64) E('rect', { x, y: 560, width: 3, height: 140, fill: C.senfDD, opacity: 0.5 }, g);
  E('rect', { x: 0, y: 0, width: 1920, height: 44, fill: C.petD }, g);
  E('rect', { x: 0, y: 700, width: 1920, height: 380, fill: C.pet }, g);
  E('rect', { x: 0, y: 700, width: 1920, height: 380, fill: 'url(#dotsL)' }, g);
  for (const y of [760, 850, 970]) E('rect', { x: 0, y, width: 1920, height: 4, fill: C.petD }, g);
  T(E('text', { x: 760, y: 420, 'text-anchor': 'middle', 'font-family': FONT.bagel, 'font-size': 120, fill: C.senfDD, opacity: 0.32 }, g), 'Flausenfabrik');
  T(E('text', { x: 760, y: 470, 'text-anchor': 'middle', 'font-family': FONT.mono, 'font-weight': 500, 'font-size': 26, fill: C.senfDD, opacity: 0.8, 'letter-spacing': 8 }, g), 'UNSINN AM FLIESSBAND · SEIT 2026');
  // Regal mit Garnrollen
  E('rect', { x: 60, y: 252, width: 340, height: 14, rx: 4, fill: C.petD }, g);
  [C.him, C.pet, C.garn, C.taube, C.him].forEach((c, i) => {
    const x = 80 + i * 64; E('rect', { x, y: 186, width: 46, height: 66, rx: 6, fill: c }, g);
    E('rect', { x: x - 5, y: 180, width: 56, height: 10, rx: 4, fill: C.woodD }, g); E('rect', { x: x - 5, y: 246, width: 56, height: 10, rx: 4, fill: C.woodD }, g);
  });
  // Unfall-Schild
  E('rect', { x: 1170, y: 120, width: 300, height: 140, rx: 10, fill: C.garn }, g);
  E('rect', { x: 1170, y: 120, width: 300, height: 140, rx: 10, fill: 'none', stroke: C.ink, 'stroke-width': 4 }, g);
  T(E('text', { x: 1320, y: 162, 'text-anchor': 'middle', 'font-family': FONT.mono, 'font-weight': 500, 'font-size': 22, fill: C.ink, 'letter-spacing': 2 }, g), 'UNFALLFREI SEIT');
  E('rect', { x: 1190, y: 176, width: 84, height: 66, rx: 6, fill: C.ink }, g);
  H.signN = T(E('text', { x: 1232, y: 230, 'text-anchor': 'middle', 'font-family': FONT.bagel, 'font-size': 56, fill: C.senf }, g), '3');
  T(E('text', { x: 1290, y: 222, 'font-family': FONT.mono, 'font-weight': 500, 'font-size': 30, fill: C.ink, 'letter-spacing': 2 }, g), 'TAGEN');
  // Stempeluhr
  E('rect', { x: 1540, y: 240, width: 150, height: 210, rx: 12, fill: C.taube }, g);
  E('circle', { cx: 1615, cy: 310, r: 48, fill: C.garn }, g);
  E('circle', { cx: 1615, cy: 310, r: 48, fill: 'none', stroke: C.ink, 'stroke-width': 5 }, g);
  H.hourHand = E('path', { d: 'M1615 310V284', stroke: C.ink, 'stroke-width': 6, 'stroke-linecap': 'round' }, g);
  H.minHand = E('path', { d: 'M1615 310V272', stroke: C.ink, 'stroke-width': 4, 'stroke-linecap': 'round' }, g);
  E('rect', { x: 1572, y: 386, width: 86, height: 12, rx: 3, fill: C.ink }, g);
  T(E('text', { x: 1615, y: 430, 'text-anchor': 'middle', 'font-family': FONT.mono, 'font-weight': 500, 'font-size': 18, fill: C.ink, 'letter-spacing': 2 }, g), 'STEMPELN');
  E('rect', { x: 1708, y: 250, width: 76, height: 180, rx: 6, fill: C.petD }, g);
  H.cards = [];
  for (let i = 0; i < 4; i++) {
    const c = E('g', null, g);
    E('rect', { x: 1718, y: 232 + i * 42, width: 56, height: 44, rx: 3, fill: C.garn }, c);
    E('rect', { x: 1718, y: 240 + i * 42, width: 56, height: 6, fill: C.him }, c);
    H.cards.push(c);
  }
  // Lampen
  for (const x of [300, 960, 1620]) {
    E('path', { d: `M${x - 70} 210L${x + 70} 210L${x + 300} 700L${x - 300} 700Z`, fill: C.garn, opacity: 0.09 }, g);
    E('path', { d: `M${x} 44V150`, stroke: C.ink, 'stroke-width': 4 }, g);
    E('path', { d: `M${x - 66} 206L${x - 32} 150H${x + 32}L${x + 66} 206Z`, fill: C.pet }, g);
    E('circle', { cx: x, cy: 208, r: 16, fill: C.garn }, g);
  }
  // Warnleuchte
  E('rect', { x: 1478, y: 44, width: 44, height: 12, fill: C.ink }, g);
  H.warnDome = E('path', { d: 'M1482 56A18 18 0 0 1 1518 56V76H1482Z', fill: '#7A3046' }, g);
  H.warnRays = E('g', null, g);
  for (let i = 0; i < 2; i++) E('path', { d: 'M1500 66L1900 -40L1900 200Z', fill: C.him, opacity: 0.18 }, H.warnRays);
  // Förderband
  E('rect', { x: -20, y: 612, width: 1790, height: 36, fill: C.ink }, g);
  H.beltTop = E('path', { d: 'M-20 608H1770', stroke: C.ink2, 'stroke-width': 10, 'stroke-dasharray': '40 24' }, g);
  H.rollers = [];
  for (let x = 30; x < 1760; x += 90) { E('circle', { cx: x, cy: 630, r: 13, fill: C.ink2 }, g); H.rollers.push(E('path', { stroke: C.taube, 'stroke-width': 3 }, g)); H.rollers[H.rollers.length - 1]._x = x; }
  for (let x = 60; x < 1760; x += 340) E('rect', { x, y: 648, width: 22, height: 54, fill: C.ink }, g);
  // Versand-Luke
  E('rect', { x: 1745, y: 420, width: 180, height: 282, fill: C.petD }, g);
  E('rect', { x: 1765, y: 470, width: 155, height: 180, fill: C.ink }, g);
  T(E('text', { x: 1840, y: 455, 'text-anchor': 'middle', 'font-family': FONT.mono, 'font-weight': 500, 'font-size': 24, fill: C.garn, 'letter-spacing': 3 }, g), 'VERSAND');
  H.flaps = [];
  for (let i = 0; i < 5; i++) H.flaps.push(E('rect', { x: 1768 + i * 31, y: 470, width: 27, height: 178, fill: C.taubeD, opacity: 0.9 }, g));
  // Kiste für Brösel
  E('rect', { x: 1062, y: 752, width: 176, height: 150, rx: 6, fill: C.wood }, g);
  for (const y of [800, 850]) E('rect', { x: 1062, y, width: 176, height: 4, fill: C.woodD }, g);
  T(E('text', { x: 1150, y: 834, 'text-anchor': 'middle', 'font-family': FONT.mono, 'font-weight': 500, 'font-size': 17, fill: C.woodD, 'letter-spacing': 2 }, g), 'NICHT STAPELN');
  H.flash = E('rect', { x: -400, y: -400, width: 2720, height: 1880, fill: C.him, opacity: 0 }, sceneGroup('halle', fxLayer));
})();

(function buildLogo() {
  const g = sceneGroup('logo');
  E('rect', { x: 0, y: 0, width: 1920, height: 1080, fill: C.senf }, g);
  E('rect', { x: 0, y: 0, width: 1920, height: 1080, fill: 'url(#dots)' }, g);
  const L = window.LOGO;
  const lg = E('g', { transform: `translate(${(1920 - L.w * 1.25) / 2},${360}) scale(1.25)` }, g);
  const fus = E('g', { transform: 'translate(0 42)' }, lg); fus.innerHTML = L.fussel;
  H.logoThread = E('path', { d: L.thread, fill: 'none', stroke: C.him, 'stroke-width': 7, 'stroke-linecap': 'round' }, lg);
  const cp = E('clipPath', { id: 'wordclip' }, defs);
  H.wordClip = E('rect', { x: 0, y: 0, width: 0, height: 400 }, cp);
  const wg = E('g', { 'clip-path': 'url(#wordclip)' }, lg);
  E('path', { d: L.word, fill: C.ink }, wg);
  H.logoBall = E('g', null, lg); H.logoBall.innerHTML = L.ball;
  H.logoBallXY = [L.bx, L.by];
  H.logoW = L.w;
  H.claim = T(E('text', { x: 960, y: 780, 'text-anchor': 'middle', 'font-family': FONT.body, 'font-weight': 800, 'font-size': 52, fill: C.ink }, g), 'Unsinn am Fließband.');
})();

(function buildTitel() {
  const g = sceneGroup('titel');
  E('rect', { x: 0, y: 0, width: 1920, height: 1080, fill: C.senf }, g);
  E('rect', { x: 0, y: 0, width: 1920, height: 1080, fill: 'url(#dots)' }, g);
  E('rect', { x: 40, y: 40, width: 1840, height: 1000, rx: 40, fill: 'none', stroke: C.garn, 'stroke-width': 8, 'stroke-dasharray': '26 18', opacity: 0.7 }, g);
  H.stamp = E('g', null, g);
  E('rect', { x: -210, y: -50, width: 420, height: 100, rx: 14, fill: 'none', stroke: C.him, 'stroke-width': 8 }, H.stamp);
  T(E('text', { x: 0, y: 20, 'text-anchor': 'middle', 'font-family': FONT.mono, 'font-weight': 500, 'font-size': 56, fill: C.him, 'letter-spacing': 6 }, H.stamp), 'CHARGE 001');
  H.t1 = T(E('text', { x: 960, y: 560, 'text-anchor': 'middle', 'font-family': FONT.bagel, 'font-size': 116, fill: C.ink }, g), 'Und was, wenn Tauben');
  H.t2 = T(E('text', { x: 960, y: 690, 'text-anchor': 'middle', 'font-family': FONT.bagel, 'font-size': 116, fill: C.ink }, g), 'die Bahn übernehmen?');
  T(E('text', { x: 960, y: 820, 'text-anchor': 'middle', 'font-family': FONT.mono, 'font-weight': 500, 'font-size': 28, fill: C.ink, 'letter-spacing': 4 }, g), 'FORMAT: UND WAS, WENN …?');
})();

(function buildFilmtitel() {
  const g = sceneGroup('filmtitel');
  E('rect', { x: 0, y: 0, width: 1920, height: 1080, fill: C.screen }, g);
  H.ftGlow = E('circle', { cx: 960, cy: 540, r: 700, fill: '#163A3E' }, g);
  H.ft1 = T(E('text', { x: 960, y: 470, 'text-anchor': 'middle', 'font-family': FONT.mono, 'font-weight': 500, 'font-size': 64, fill: C.senf, 'letter-spacing': 16 }, g), 'FILM 1');
  H.ft2 = T(E('text', { x: 960, y: 640, 'text-anchor': 'middle', 'font-family': FONT.bagel, 'font-size': 150, fill: C.senf }, g), 'Die Übernahme');
  E('rect', { x: 0, y: 0, width: 1920, height: 1080, fill: 'url(#scan)', opacity: 0.6 }, g);
  E('path', { d: 'M0 0H1920V1080H0Z M960 -260A1060 860 0 1 0 960.1 -260Z', fill: C.petDD, 'fill-rule': 'evenodd', opacity: 0.9 }, g);
})();

(function buildBahnhof() {
  const g = sceneGroup('bahnhof');
  E('rect', { x: 0, y: 0, width: 1920, height: 760, fill: '#EFE6D2' }, g);
  for (const x of [80, 560, 1040, 1520]) {
    E('path', { d: `M${x} 560V250A160 160 0 0 1 ${x + 320} 250V560Z`, fill: C.garn }, g);
    E('path', { d: `M${x} 560V250A160 160 0 0 1 ${x + 320} 250V560Z`, fill: 'none', stroke: C.pet, 'stroke-width': 14 }, g);
    E('path', { d: `M${x + 160} 92V560M${x} 400H${x + 320}`, stroke: C.pet, 'stroke-width': 8 }, g);
  }
  E('rect', { x: 0, y: 0, width: 1920, height: 60, fill: C.pet }, g);
  for (let x = -100; x < 2000; x += 480) E('path', { d: `M${x} 60Q${x + 240} -40 ${x + 480} 60`, fill: 'none', stroke: C.petD, 'stroke-width': 12 }, g);
  E('rect', { x: 0, y: 560, width: 1920, height: 200, fill: '#4A4560' }, g);
  E('rect', { x: 0, y: 736, width: 1920, height: 10, fill: C.taubeD }, g);
  // Anzeigetafel
  E('path', { d: 'M260 60V90M640 60V90', stroke: C.ink, 'stroke-width': 5 }, g);
  E('rect', { x: 110, y: 88, width: 700, height: 250, rx: 12, fill: C.ink }, g);
  T(E('text', { x: 140, y: 134, 'font-family': FONT.mono, 'font-weight': 500, 'font-size': 26, fill: C.garn, 'letter-spacing': 4 }, g), 'ABFAHRT · GLEIS 1');
  E('rect', { x: 130, y: 150, width: 660, height: 3, fill: C.ink2 }, g);
  H.b1 = T(E('text', { x: 140, y: 205, 'font-family': FONT.mono, 'font-weight': 500, 'font-size': 38, fill: C.senf }, g), '');
  H.b2 = T(E('text', { x: 140, y: 265, 'font-family': FONT.mono, 'font-weight': 500, 'font-size': 30, fill: C.garn }, g), '');
  H.b3 = T(E('text', { x: 140, y: 312, 'font-family': FONT.mono, 'font-weight': 500, 'font-size': 30, fill: C.him }, g), '');
  // Bahnhofsuhr
  E('path', { d: 'M1020 60V96', stroke: C.ink, 'stroke-width': 5 }, g);
  E('circle', { cx: 1020, cy: 150, r: 56, fill: '#fff' }, g);
  E('circle', { cx: 1020, cy: 150, r: 56, fill: 'none', stroke: C.ink, 'stroke-width': 7 }, g);
  E('path', { d: 'M1020 150L1040 136M1020 150L1020 104', stroke: C.ink, 'stroke-width': 6, 'stroke-linecap': 'round' }, g);
  H.secHand = E('path', { d: 'M1020 150V104', stroke: C.him, 'stroke-width': 3 }, g);
  // Bahnhofsschild
  E('path', { d: 'M1230 60V120M1560 60V120', stroke: C.ink, 'stroke-width': 4 }, g);
  E('rect', { x: 1150, y: 118, width: 490, height: 84, rx: 8, fill: C.garn }, g);
  E('rect', { x: 1150, y: 118, width: 490, height: 84, rx: 8, fill: 'none', stroke: C.pet, 'stroke-width': 6 }, g);
  T(E('text', { x: 1395, y: 174, 'text-anchor': 'middle', 'font-family': FONT.body, 'font-weight': 800, 'font-size': 42, fill: C.pet }, g), 'Brötchenhausen Hbf');
  // Bahnsteig vorne
  const f = sceneGroup('bahnhof', bgFront);
  E('rect', { x: 0, y: 742, width: 1920, height: 338, fill: C.taube }, f);
  E('rect', { x: 0, y: 742, width: 1920, height: 30, fill: C.garnD }, f);
  E('path', { d: 'M0 800H1920', stroke: C.senf, 'stroke-width': 9, 'stroke-dasharray': '46 22' }, f);
  for (const y of [880, 990]) E('rect', { x: 0, y, width: 1920, height: 3, fill: C.taubeD }, f);
  for (let x = 120; x < 1920; x += 240) E('path', { d: `M${x} 803L${x - 60} 1080`, stroke: C.taubeD, 'stroke-width': 3 }, f);
  E('rect', { x: 1812, y: 160, width: 18, height: 650, fill: C.ink }, f);
  H.horn = E('g', null, f);
  E('path', { d: 'M1812 200L1730 160V250Z', fill: C.taubeD }, H.horn);
  E('rect', { x: 1806, y: 188, width: 22, height: 24, rx: 4, fill: C.ink }, H.horn);
  H.hornWaves = E('path', { d: 'M1715 175q-14 30 0 60M1695 160q-24 45 0 90', fill: 'none', stroke: C.him, 'stroke-width': 5, 'stroke-linecap': 'round' }, H.horn);
})();

(function buildZug() {
  const g = sceneGroup('zug');
  E('rect', { x: 0, y: 0, width: 1920, height: 1080, fill: C.garn }, g);
  E('rect', { x: 0, y: 0, width: 1920, height: 70, fill: C.garnD }, g);
  E('rect', { x: 60, y: 34, width: 1800, height: 16, rx: 8, fill: '#fff', opacity: 0.8 }, g);
  E('path', { d: 'M40 150H1880', stroke: C.ink2, 'stroke-width': 6 }, g);
  for (let x = 60; x < 1880; x += 60) E('path', { d: `M${x} 150V120`, stroke: C.ink2, 'stroke-width': 3 }, g);
  const cp = E('clipPath', { id: 'winclip' }, defs);
  const W = [[170, 190, 480, 300], [720, 190, 480, 300], [1270, 190, 480, 300]];
  for (const [x, y, w, h] of W) E('rect', { x, y, width: w, height: h, rx: 34 }, cp);
  const out = E('g', { 'clip-path': 'url(#winclip)' }, g);
  H.outLand = E('g', null, out); H.outBakery = E('g', null, out); H.outClouds = E('g', null, out);
  // Landschaft (wiederholt sich alle 1200 px)
  E('rect', { x: 0, y: 150, width: 1920, height: 400, fill: '#FFF1CF' }, H.outLand);
  H.landFar = E('g', null, H.outLand); H.landNear = E('g', null, H.outLand); H.poles = E('g', null, H.outLand);
  for (let k = 0; k < 4; k++) {
    E('path', { d: `M${k * 1200} 420Q${k * 1200 + 300} 300 ${k * 1200 + 600} 410T${k * 1200 + 1200} 420V520H${k * 1200}Z`, fill: '#4F8E92' }, H.landFar);
    E('path', { d: `M${k * 1200} 460Q${k * 1200 + 200} 400 ${k * 1200 + 450} 455T${k * 1200 + 1200} 450V520H${k * 1200}Z`, fill: C.senfD }, H.landNear);
    for (const dx of [150, 520, 900]) { E('rect', { x: k * 1200 + dx, y: 395, width: 10, height: 50, fill: C.woodD }, H.landNear); E('circle', { cx: k * 1200 + dx + 5, cy: 385, r: 30, fill: C.pet }, H.landNear); }
    for (const dx of [0, 600]) E('rect', { x: k * 1200 + dx, y: 180, width: 14, height: 320, fill: C.ink2 }, H.poles);
  }
  E('rect', { x: 0, y: 480, width: 1920, height: 40, fill: '#7C7894' }, H.outLand);
  // Bäckerei
  E('rect', { x: 0, y: 150, width: 1920, height: 400, fill: '#FFF1CF' }, H.outBakery);
  E('rect', { x: 560, y: 200, width: 800, height: 320, fill: C.garnD }, H.outBakery);
  for (let i = 0; i < 10; i++) E('path', { d: `M${560 + i * 80} 230h80l-10 50h-60z`, fill: i % 2 ? C.garn : C.him }, H.outBakery);
  E('rect', { x: 600, y: 300, width: 300, height: 200, rx: 10, fill: C.ink2 }, H.outBakery);
  for (let i = 0; i < 4; i++) E('ellipse', { cx: 650 + i * 66, cy: 440, rx: 28, ry: 18, fill: C.brezel }, H.outBakery);
  E('path', { d: 'M1040 340c-60-60 40-110 70-40c30-70 130-20 70 40c-30 30-110 30-140 0z', fill: 'none', stroke: C.brezel, 'stroke-width': 22 }, H.outBakery);
  T(E('text', { x: 1110, y: 470, 'text-anchor': 'middle', 'font-family': FONT.bagel, 'font-size': 52, fill: C.him }, H.outBakery), 'Bäckerei');
  E('rect', { x: 0, y: 480, width: 1920, height: 40, fill: '#7C7894' }, H.outBakery);
  // Wolken
  E('rect', { x: 0, y: 150, width: 1920, height: 400, fill: '#BFE0DC' }, H.outClouds);
  H.cloudRow = E('g', null, H.outClouds);
  for (let k = 0; k < 8; k++) { const cx = k * 300, cy = 250 + (k % 3) * 80; for (const [dx, dy, r] of [[0, 0, 40], [40, -10, 50], [85, 5, 38], [40, 20, 36]]) E('circle', { cx: cx + dx, cy: cy + dy, r, fill: '#fff' }, H.cloudRow); }
  H.cloudBrezel = E('path', { d: 'M0 0c-90-90 60-160 105-60c45-100 195-30 105 60c-45 45-165 45-210 0z', fill: 'none', stroke: C.brezel, 'stroke-width': 30 }, H.outClouds);
  for (const [x, y, w, h] of W) { E('rect', { x, y, width: w, height: h, rx: 34, fill: 'none', stroke: C.petD, 'stroke-width': 16 }, g); E('rect', { x: x + 20, y: y + h + 8, width: w - 40, height: 10, rx: 5, fill: C.taubeD }, g); }
  E('rect', { x: 0, y: 560, width: 1920, height: 520, fill: C.garnD }, g);
  for (const x of [60, 560, 1060, 1560]) {
    const w = x === 1560 ? 300 : 440;
    E('rect', { x, y: 560, width: w, height: 230, rx: 30, fill: C.pet }, g);
    E('rect', { x, y: 560, width: w, height: 230, rx: 30, fill: 'url(#felt)' }, g);
    E('rect', { x: x + 30, y: 572, width: w - 60, height: 38, rx: 12, fill: C.garn, opacity: 0.85 }, g);
    E('rect', { x: x - 6, y: 770, width: w + 12, height: 46, rx: 14, fill: C.petD }, g);
  }
  E('rect', { x: 0, y: 816, width: 1920, height: 264, fill: C.taubeD }, g);
  E('rect', { x: 0, y: 900, width: 1920, height: 70, fill: C.taube, opacity: 0.5 }, g);
  E('rect', { x: 1210, y: 82, width: 480, height: 34, rx: 6, fill: C.pet }, g);
  H.kleber = T(E('text', { x: 1450, y: 106, 'text-anchor': 'middle', 'font-family': FONT.mono, 'font-weight': 500, 'font-size': 20, fill: C.garn, 'letter-spacing': 3 }, g), 'RUHEWAGEN · BITTE LEISE GURREN');
})();

(function buildHimmel() {
  const g = sceneGroup('himmel');
  E('rect', { x: 0, y: 0, width: 1920, height: 1080, fill: '#BFE0DC' }, g);
  E('rect', { x: 0, y: 600, width: 1920, height: 480, fill: '#D8EDE6' }, g);
  E('circle', { cx: 1620, cy: 190, r: 90, fill: C.senf }, g);
  H.sunRays = E('g', null, g);
  for (let i = 0; i < 12; i++) E('rect', { x: 1612, y: 40, width: 16, height: 40, rx: 8, fill: C.senf, transform: `rotate(${i * 30},1620,190)` }, H.sunRays);
  H.landBelow = E('g', null, g);
  E('path', { d: 'M0 930Q300 870 640 920T1280 910T1920 920V1080H0Z', fill: '#4F8E92' }, H.landBelow);
  E('path', { d: 'M0 980Q400 940 800 975T1920 970V1080H0Z', fill: C.senfD }, H.landBelow);
  for (let i = 0; i < 9; i++) { const x = 700 + i * 34; E('rect', { x, y: 950 - (i % 3) * 8, width: 26, height: 22 + (i % 3) * 8, fill: [C.garn, C.him, C.garnD][i % 3] }, H.landBelow); E('path', { d: `M${x - 3} ${950 - (i % 3) * 8}l16-14 16 14z`, fill: C.ink2 }, H.landBelow); }
  T(E('text', { x: 834, y: 1030, 'text-anchor': 'middle', 'font-family': FONT.mono, 'font-weight': 500, 'font-size': 20, fill: C.ink, 'letter-spacing': 2 }, H.landBelow), 'BRÖTCHENHAUSEN');
  H.clouds = [];
  for (let k = 0; k < 9; k++) {
    const c = E('g', null, g);
    for (const [dx, dy, r] of [[0, 0, 60], [70, -25, 75], [140, 0, 58], [70, 25, 55], [-50, 15, 40]]) E('circle', { cx: dx, cy: dy, r, fill: '#fff' }, c);
    E('circle', { cx: 70, cy: 0, r: 1, fill: 'url(#felt)' }, c);
    c._k = k; H.clouds.push(c);
  }
  H.swarm = E('g', null, g);
  H.brezel = E('g', { transform: 'translate(860,560)' }, H.swarm);
  E('path', { d: 'M0 0c-180-180 120-320 210-120c90-200 390-60 210 120c-90 90-330 90-420 0z', fill: 'none', stroke: C.brezel, 'stroke-width': 64, transform: 'translate(-110,-40)' }, H.brezel);
  for (let i = 0; i < 18; i++) E('rect', { x: -60 + (i * 53) % 330 - 90, y: -150 + (i * 37) % 200, width: 9, height: 6, rx: 2, fill: C.garn, transform: 'translate(-20,0)' }, H.brezel);
  E('rect', { x: -40, y: 170, width: 300, height: 70, rx: 8, fill: C.garn }, H.brezel);
  T(E('text', { x: 110, y: 218, 'text-anchor': 'middle', 'font-family': FONT.body, 'font-weight': 800, 'font-size': 34, fill: C.pet }, H.brezel), 'Hauptbahnhof');
  H.minis = [];
  for (let i = 0; i < 6; i++) H.minis.push(makeMiniTrain(H.swarm));
})();

(function buildEndcard() {
  const g = sceneGroup('endcard');
  E('rect', { x: 0, y: 0, width: 1920, height: 1080, fill: C.pet }, g);
  E('rect', { x: 0, y: 0, width: 1920, height: 1080, fill: 'url(#dotsL)' }, g);
  E('rect', { x: 140, y: 220, width: 800, height: 450, rx: 18, fill: C.petD }, g);
  E('rect', { x: 140, y: 220, width: 800, height: 450, rx: 18, fill: 'none', stroke: C.garn, 'stroke-width': 6, 'stroke-dasharray': '24 16' }, g);
  T(E('text', { x: 540, y: 455, 'text-anchor': 'middle', 'font-family': FONT.mono, 'font-weight': 500, 'font-size': 34, fill: C.garn, 'letter-spacing': 6 }, g), 'NÄCHSTE CHARGE');
  E('circle', { cx: 1180, cy: 445, r: 165, fill: C.senf }, g);
  E('circle', { cx: 1180, cy: 445, r: 165, fill: 'none', stroke: C.garn, 'stroke-width': 8 }, g);
  H.endFussel = makeFussel(g);
  T(E('text', { x: 1180, y: 680, 'text-anchor': 'middle', 'font-family': FONT.mono, 'font-weight': 500, 'font-size': 30, fill: C.garn, 'letter-spacing': 6 }, g), 'ABONNIEREN');
  H.endTitle = T(E('text', { x: 140, y: 880, 'font-family': FONT.bagel, 'font-size': 120, fill: C.senf }, g), 'Feierabend!');
  T(E('text', { x: 146, y: 950, 'font-family': FONT.mono, 'font-weight': 500, 'font-size': 28, fill: C.garn, 'letter-spacing': 4 }, g), 'NEUE CHARGE JEDEN FREITAG · 16 UHR');
})();

// ---------------------------------------------------------------------------
// Darsteller
// ---------------------------------------------------------------------------
const train = makeTrain(trainLayer);
const crowd = [];
const CROWD_N = 14;
const bodies = [C.taube, '#9C98B8', '#B3AFCB', '#8F8AAE'];
for (let i = 0; i < CROWD_N; i++) crowd.push(makePigeon(i < 7 ? actorsBack : actorsFront, { body: bodies[i % 4], wingC: i % 2 ? '#7E79A0' : C.taubeD, neck: true }));
const kurt = makeKurt(actors);
const broesel = makePigeon(actors, { hat: 'helmet', board: true });
const gurrmann = makePigeon(actors, { hat: 'cap', body: '#9C98B8' });
const fussel = makeFussel(actors);
const sitter = makePigeon(actorsFront, { body: '#B3AFCB' });
const ball = makeBall(actorsFront);
const crumbG = E('g', null, fxLayer);
const crumbs = [];
for (let i = 0; i < 46; i++) crumbs.push(E('rect', { width: 9, height: 7, rx: 2, fill: i % 3 ? C.brezel : C.senfDD }, crumbG));
const featherG = E('g', null, fxLayer);
const feathers = [];
for (let i = 0; i < 10; i++) feathers.push(E('ellipse', { rx: 12, ry: 5, fill: C.garn }, featherG));

const irisPath = E('path', { fill: C.ink, 'fill-rule': 'evenodd' }, overlay);
const fadeRect = E('rect', { x: 0, y: 0, width: 1920, height: 1080, fill: '#000', opacity: 0 }, overlay);

// Positionen der Tauben je Modus
const PLAT_POS = [[180, 905, -1], [300, 960, 1], [420, 900, 1], [260, 1030, -1], [1380, 910, -1], [1520, 960, 1], [1650, 905, -1],
  [1760, 1010, -1], [1480, 1040, 1], [120, 1020, 1], [1320, 1010, -1], [1600, 1060, -1], [380, 1060, 1], [1720, 930, -1]];
const SEAT_POS = [[150, 770], [280, 770], [650, 770], [930, 770], [1150, 770], [1430, 770], [1700, 770]];
function chaosPos(i, t) {
  const a = t * (0.6 + (i % 5) * 0.12) + i * 1.7;
  return [960 + Math.sin(a) * (520 + (i % 3) * 180), 330 + Math.sin(a * 1.7 + i) * 170 + (i % 2) * 60];
}
function beltX(i) { return 160 + i * 115; }

// Pose einer Statisten-Taube in einem Modus (ohne Überblendung). face: +1 schaut nach links.
function crowdPose(mode, i, t, m0, prevMode, noVel) {
  const o = { x: 0, y: 0, s: 0.75, face: 1, r: 0, head: 0, lid: 0.25, open: 0, fly: 0, sit: 0, peck: 0, vis: true, flying: false };
  const u = t - m0;
  if (mode === 'platform' || mode === 'look' || mode === 'board') {
    const [x, y, fl] = PLAT_POS[i];
    o.x = x; o.y = y; o.face = -fl; o.s = 0.62 + (y - 900) / 900;
    const pk = PECK[i], k = lastLE(pk, t);   // Picken: 0.28 s rein und raus, nach Zufallsplan
    if (k >= 0 && t - pk[k] < 0.28) o.peck = -28 * Math.pow(Math.sin(Math.PI * (t - pk[k]) / 0.28), 2);
    if (mode === 'look') { o.face = x < 600 ? -1 : 1; o.head = -14; o.peck = 0; o.lid = 0; }
    if (mode === 'board') {
      const uu = clamp((u - 0.08 * i) / 1.4, 0, 1), tx = i % 2 ? 700 : 1260;
      o.x = lerp(x, tx, uu); o.y = lerp(y, 820, uu) - Math.sin(uu * Math.PI) * 120; o.face = tx > x ? -1 : 1;
      o.fly = smooth(uu / 0.05); o.s *= lerp(1, 0.7, uu); o.peck = 0; o.flying = uu > 0;
      if (uu >= 1) o.vis = false;
    }
  } else if (mode === 'seats' || mode === 'window' || mode === 'loud') {
    if (i >= SEAT_POS.length) o.vis = false;
    else {
      const [x, y] = SEAT_POS[i]; o.x = x; o.y = y; o.sit = 1; o.s = 0.72; o.face = i % 2 ? 1 : -1;
      if (mode === 'window') { o.head = 16; o.lid = 0; o.face = -1; o.r = -6; }
      if (mode === 'loud') { o.open = 0.5 + 0.5 * Math.abs(Math.sin(t * 9 + i)); o.head = Math.sin(t * 10 + i) * 10; o.y -= Math.abs(Math.sin(t * 8 + i)) * 10; }
    }
  } else if (mode === 'burst' || mode === 'chaos' || mode === 'clock' || mode === 'tobelt' || mode === 'belt') {
    o.s = 0.6; o.fly = 1; o.flying = true;
    let dflt = 0;   // Blickrichtung, wenn die Taube steht (0 = nur aus dem Tempo)
    if (mode === 'burst') {
      const uu = clamp(u / 1.4, 0, 1), [cx, cy] = chaosPos(i, t);
      o.x = lerp(853, cx, ease('out', uu)); o.y = lerp(678, cy, ease('out', uu)); o.s = lerp(0.15, 0.6, uu);
    } else if (mode === 'chaos' || (mode === 'clock' && i % 3)) {
      const [x, y] = chaosPos(i, t); o.x = x; o.y = y;
      if (mode === 'chaos' && prevMode === 'clock' && i % 3 === 0 && u < 1) {   // von der Uhr zurück in den Schwarm, ohne Sprung
        const w = ease('io', u); o.x = lerp(1660 + (i % 4) * 30, x, w); o.y = lerp(300 + (i % 3) * 50, y, w);
      }
    } else if (mode === 'clock') {
      const tx = 1660 + (i % 4) * 30, ty = 300 + (i % 3) * 50, [sx, sy] = chaosPos(i, m0), uu = clamp(u / 1.0, 0, 1);
      o.x = lerp(sx, tx, ease('io', uu)); o.y = lerp(sy, ty, ease('io', uu)); dflt = -1;
      o.fly = 1 - smooth((uu - 0.85) / 0.15);
      if (uu >= 1) {   // an der Stempeluhr: schnell picken
        const pk = PECKF[i], k = lastLE(pk, t);
        if (k >= 0 && t - pk[k] < 0.2) o.peck = -26 * Math.pow(Math.sin(Math.PI * (t - pk[k]) / 0.2), 2);
      }
    } else {
      const tx = beltX(i), ty = 608;
      const [sx, sy] = prevMode === 'clock' || prevMode === 'chaos' || mode === 'tobelt' ? chaosPos(i, mode === 'tobelt' ? m0 : stT('crowd', 'mode', m0 - 0.01)) : [tx, ty];
      dflt = -1;
      if (mode === 'tobelt') {
        const uu = clamp((u - i * 0.05) / 1.2, 0, 1);
        o.x = lerp(sx, tx, ease('io', uu)); o.y = lerp(sy, ty, ease('io', uu));
        o.fly = 1 - smooth((uu - 0.85) / 0.15);
      } else {
        o.fly = 0; o.x = tx + (integ('belt', t) - integ('belt', m0)); o.y = ty; o.s = 0.6;
        if (o.x > 1790) o.vis = false;
        o.head = Math.sin(t * 3 + i) * 5;
      }
    }
    if (!noVel) {   // Blickrichtung und Schräglage aus dem Tempo (stetiges Wenden, Neigen beim Sinken)
      const p2 = crowdPose(mode, i, t + 0.01, m0, prevMode, true), vx = (p2.x - o.x) / 0.01, vy = (p2.y - o.y) / 0.01;
      const fv = -Math.tanh(vx / 90);
      o.face = dflt ? lerp(dflt, fv, clamp(Math.abs(vx) / 120, 0, 1)) : fv;
      o.r = -clamp(vy * 0.015, -18, 18) * (o.face < 0 ? -1 : 1) * o.fly;
    }
  } else o.vis = false;
  return o;
}

function updateCrowd(t, scene) {
  const mode = st('crowd', 'mode', t, 'off');
  const m0 = stT('crowd', 'mode', t), u = t - m0;
  const prevMode = (() => { const L = TL.states.crowd && TL.states.crowd.mode; if (!L) return 'off'; let p = 'off'; for (let i = 0; i < L.length; i++) { if (L[i][0] >= m0 - 1e-6) break; p = L[i][1]; } return p; })();
  const fam = m => (m === 'platform' || m === 'look' || m === 'board') ? 1 : (m === 'seats' || m === 'window' || m === 'loud') ? 2 : 0;
  const blendIn = fam(mode) && fam(mode) === fam(prevMode) && mode !== prevMode;
  const hide = scene === 'logo' || scene === 'titel' || scene === 'filmtitel' || scene === 'endcard' || scene === 'himmel' ||
    (fam(mode) === 2 && scene !== 'zug') || (fam(mode) === 0 && scene !== 'halle');
  // Durchsage: Statisten gurren das "Gurr." am Anfang und Ende mit; Gong: alle schauen hoch
  const ann = scene === 'bahnhof' || scene === 'zug' ? lineAt('A', t) : null;
  const tGong = since('gong', t), tGurr = Math.min(since('gurren', t), since('gurren_laut', t) + 0.0);
  for (let i = 0; i < CROWD_N; i++) {
    const p = crowd[i];
    let o = crowdPose(mode, i, t, m0, prevMode);
    if (blendIn) {   // Moduswechsel gestaffelt: jede Taube 0.035 s später, 0.2 s weich
      const ui = smooth((u - i * 0.035) / 0.2);
      if (ui < 1) {
        const q = crowdPose(prevMode, i, t, m0, null);
        for (const k of ['face', 'head', 'r', 'lid', 'open', 'y', 'peck']) o[k] = lerp(q[k], o[k], ui);
      }
    }
    const vis = o.vis && !hide;
    show(p.g, vis);
    if (!vis) continue;
    const ph = i * 1.3;
    let open = o.open;
    if (ann && !ann.fx) {
      const w = 1 - smooth((t - ann.t0 - 0.45) / 0.15) + smooth((t - ann.t1 + 0.65) / 0.15);
      if (w > 0.01) open = Math.max(open, 0.5 * clamp(w, 0, 1) * mouth('A', t - 0.05 - (i % 4) * 0.03).o);
    }
    if (tGurr < 2.6) open = Math.max(open, 0.55 * Math.pow(Math.max(0, Math.sin(t * 13 + i * 2.1)), 2) * (1 - smooth((tGurr - 2.0) / 0.5)));
    const look = tGong < 2 ? smooth((tGong - i * 0.04) / 0.2) * (1 - smooth((tGong - 1.3 - i * 0.04) / 0.4)) : 0;
    const settled = (1 - o.fly) * (o.vis ? 1 : 0);
    p.update({
      x: o.x, y: o.y + 6 * Math.sin(t * 26 + ph + Math.PI / 2) * o.fly, s: o.s, face: o.face, r: o.r, t, ph,
      breath: 0.018 * Math.sin(2 * Math.PI * t / 3.1 + ph), period: 3.1,
      head: o.head + (4 * Math.sin(2 * Math.PI * (0.2 + 0.3 * hash(i, 7)) * t + 6.28 * hash(i, 8)) + 12 * look) * settled,
      snap: 5, peck: o.peck, open, puff: open, lid: o.lid, blink: blinkClosure('crowd' + i, t),
      px: -2, py: -2 * look, fly: o.fly, sit: o.sit, wing: 0
    });
  }
}

// ---------------------------------------------------------------------------
// Figuren posieren (pro Bild, reine Funktionen von t)
// ---------------------------------------------------------------------------
// Ausdruck je Augen-Zustand: Lider, Brauen, Ruhe-Mund (mo/mw/smile)
const FEXPR = {
  normal: { wide: 0, squint: 0, lid: 0, raise: 0, mo: 0, mw: 0.5, smile: 0.6 },
  wide: { wide: 1, squint: 0, lid: 0, raise: 0.2, mo: 0.35, mw: 0, smile: 0 },
  happy: { wide: 0, squint: 1, lid: 0.15, raise: 0.4, mo: 0.45, mw: 1, smile: 1 }
};
// Brauen-Zustand von Fussel: [heben, neigen (+ traurig, − böse), Lid, Mundwinkel]
const FBROW = { none: [0, 0, 0, 0], up: [1, 0, 0, 0], sad: [0.3, 1, 0, -0.6], angry: [0, -1, 0.15, -0.8], skeptic: [0.2, -0.4, 0.35, -0.4] };
function fusselExpr(t) {
  const b = stBlend('fussel', 'eyes', t, 'normal');
  const P = FEXPR[b.prev] || FEXPR.normal, Q = FEXPR[b.cur] || FEXPR.normal, u = smooth(b.tau / 0.12);
  const e = {};
  for (const k in Q) e[k] = lerp(P[k], Q[k], u);
  if (b.cur === 'wide') e.wide = lerp(P.wide, 1, 1 - Math.exp(-14 * b.tau) * Math.cos(20 * b.tau));   // Augen springen auf, mit Überschwinger
  const r = stBlend('fussel', 'brow', t, 'none'), A = FBROW[r.prev] || FBROW.none, B = FBROW[r.cur] || FBROW.none, w = smooth(r.tau / 0.2);
  e.raise += lerp(A[0], B[0], w); e.tilt = lerp(A[1], B[1], w); e.lid = Math.max(e.lid, lerp(A[2], B[2], w)); e.smile += lerp(A[3], B[3], w);
  return e;
}
// Kopfnicken der Zuhörer auf die 3 stärksten Betonungen des Sprechers
function listenNod(self, t) {
  let n = 0;
  for (const w of ['F', 'K', 'B', 'G']) if (w !== self) n += pulse(w, t - 0.15, true).p;
  return 0.4 * n;
}

function poseFussel(t) {
  const x = num('fussel', 'x', t), y = num('fussel', 'y', t), s = num('fussel', 's', t);
  const face = clamp(num('fussel', 'flip', t) * 8, -1, 1), fs = face < 0 ? -1 : 1;
  const vx = numV('fussel', 'x', t), vy = numV('fussel', 'y', t);
  const e = fusselExpr(t), P = pulse('F', t), en = integ('en_F', t), nod = listenNod('F', t);
  let fsx = 1, fsy = 1, tuck = 0, splay = 0, m = 0, ang = 0, r = num('fussel', 'r', t) + integ('lean_fussel', t), lift = 0;
  // Ausholen vor dem Absprung (0.14 s), Lösen in 0.06 s
  const ku = lastLE(JUMP.up, t + 0.14, j => j.t);
  if (ku >= 0) {
    const J = JUMP.up[ku], x0 = J.t - t, k = clamp(J.v / 2500, 0.1, 0.25);
    const a = x0 >= 0 ? k * Math.sin(Math.PI / 2 * (1 - x0 / 0.14)) : k * (1 - smooth(-x0 / 0.06));
    if (a > 0) { fsy *= 1 - a; fsx *= 1 + 0.7 * a; }
  }
  // Flug: Strecken entlang der Flugbahn, Neigen in Flugrichtung, Beine angezogen
  const ka = lastLE(JUMP.air, t, a => a[0]);
  if (ka >= 0 && t < JUMP.air[ka][1]) {
    const air = smooth((t - JUMP.air[ka][0]) / 0.06);
    m = clamp(Math.hypot(vx, vy) / 2600, 0, 0.22) * air;
    ang = Math.atan2(vy, vx * fs) * 180 / Math.PI;
    r += clamp(vx / 40, -15, 15) * air;
    tuck = air;
  }
  // Landung: Stauchen und nachfedern, Füße gespreizt
  const kd = lastLE(JUMP.down, t, j => j.t);
  if (kd >= 0 && t - JUMP.down[kd].t < 0.45) {
    const x1 = t - JUMP.down[kd].t, A = clamp(JUMP.down[kd].v / 3000, 0.1, 0.32), q = A * Math.exp(-9 * x1) * Math.cos(26 * x1);
    fsy *= 1 - q; fsx *= 1 + 0.8 * q; splay = clamp(q / 0.15, 0, 1);
  }
  // Hüpf-Gang: Bodenphase (Stauchen, Abdruck), dann Parabel; steht er still, nur leichtes Federn
  const wa = stSmooth('fussel', 'walk', t, 0.12), sit = stSmooth('fussel', 'sit', t, 0.2);
  if (wa > 0.001) {
    const mv = clamp(integ('vL_fussel', t) / 40, 0, 1) * wa, q = frac(integ('ph_fussel', t)), u = clamp((q - 0.2) / 0.8, 0, 1);
    lift += 14 * s * 4 * u * (1 - u) * mv;
    const c = q < 0.2 ? 0.14 * Math.sin(Math.PI * q / 0.2) * mv : 0;
    fsy *= 1 - c; fsx *= Math.pow(1 - c, -0.7);
    if (q > 0.2 && q < 0.45) fsy *= 1 + 0.08 * Math.sin(Math.PI * (q - 0.2) / 0.25) * mv;
    tuck = Math.max(tuck, Math.sin(Math.PI * u) * mv);
    splay = Math.max(splay, c / 0.14);
    r += 4 * fs * mv;
    fsy *= 1 - 0.025 * Math.abs(Math.sin(2 * Math.PI * 2.2 * t)) * (wa - mv);
  }
  // Reaktionen auf Geräusche
  const tsp = since('sparkle', t), tfe = since('fehler', t), tgr = since('grille', t);
  const spk = env3(tsp, 0.08, 1.3, 0.6);   // Idee: Brauen hoch, Faden zuckt hoch
  const pop = tsp < 1.5 ? 0.05 * Math.exp(-8 * tsp) * Math.sin(22 * tsp) : 0;
  const spStretch = tsp < 1.5 ? 0.1 * Math.exp(-8.8 * tsp) * Math.cos(23.5 * tsp) * smooth(tsp / 0.05) : 0;
  const flinch = env3(tfe, 0.05, 0.05, 0.4);   // WLAN-Fehler: zusammenzucken
  fsy *= 1 - 0.08 * flinch; fsx *= 1 + 0.05 * flinch;
  // Sprechen: Betonungen heben den Körper und kippen ihn abwechselnd; Fragen: Kopf schief, Brauen hoch
  const ql = lineAt('F', t, 0, 0.4);
  let qa = 0;
  if (ql && ql.q) qa = smooth(((t - ql.t0) / (ql.t1 - ql.t0) - 0.7) / 0.15) * (1 - smooth((t - ql.t1) / 0.4));
  // Gewicht verlagern im Stehen
  r += 1.5 * Math.sin(2 * Math.PI * t / 5.3) * (1 - sit) * (1 - wa) + 3.5 * P.sp + 5 * qa * fs + 3 * integ('lx_fussel', t);
  const shake = stSmooth('fussel', 'shake', t, 0.08);
  // Blick: automatisch (zum Sprecher), außer das Drehbuch setzt lx/ly
  const klx = num('fussel', 'lx', t), kly = num('fussel', 'ly', t), kw = clamp(Math.max(Math.abs(klx), Math.abs(kly)) / 0.25, 0, 1);
  let lx = lerp(integ('gx_fussel', t) * fs, klx, kw), ly = lerp(integ('gy_fussel', t), kly, kw);
  if (tgr < 3.2) {   // Grillen-Pause: verlegen nach links, dann nach rechts schauen
    const w = env3(tgr, 0.25, 2.3, 0.5), v = tgr < 0.75 ? -0.6 * smooth(tgr / 0.6) : lerp(-0.6, 0.8, smooth((tgr - 0.75) / 0.6));
    lx = lerp(lx, v * fs, w); ly = lerp(ly, 0.1, w);
  }
  const mt = mouth('F', t), k = clamp(mt.o / 0.3, 0, 1);
  return {
    x: x + shake * Math.sin(t * 60) * 8, y: y - lift, r: r + shake * Math.sin(t * 47) * 9, s, face, fsx, fsy, m, ang, t,
    bsy: 1 + 0.022 * Math.sin(2 * Math.PI * t / 2.8 + 0.4) + 0.05 * P.p - 0.03 * en - 0.03 * nod - integ('jig', t) + spStretch,
    lift: 7 * P.p + 3 * nod,
    thread: num('fussel', 'thread', t), Lx: integ('thrX', t), Ly: integ('thrY', t), tip: 10 * spk, curl: clamp(e.wide, 0, 1),
    sit, tuck, splay,
    wide: e.wide, squint: e.squint, lid: e.lid, blink: blinkClosure('fussel', t), lx, ly,
    eyeScale: 1 + 0.17 * e.wide + 0.04 * P.p + pop, raise: e.raise + 0.5 * P.p + 0.6 * qa + spk, tilt: e.tilt,
    mo: lerp(e.mo, mt.o, k), mw: lerp(e.mw, mt.w, k), ms: mt.s * k, smile: lerp(e.smile, 0.15, k)
  };
}

// Brösel und Gurrmann: Atmen, Blick, Sprech-Gesten, Gehen, Reaktionen
function posePigeon(name, who, t, scene) {
  const P = pulse(who, t), en = integ('en_' + who, t), mt = mouth(who, t), nod = listenNod(who, t);
  const face = -clamp(num(name, 'flip', t) * 8, -1, 1), fs = face < 0 ? -1 : 1;
  const wa = stSmooth(name, 'walk', t, 0.15), vL = integ('vL_' + name, t), sq = integ('squash_' + name, t);
  const ex = mt.l && mt.l.ex ? 1 : 0;
  const o = {
    x: num(name, 'x', t), y: num(name, 'y', t), s: num(name, 's', t), face, t,
    r: num(name, 'r', t) + integ('lean_' + name, t), sx: 1 - sq * 0.3, sy: 1 + sq * 0.6,
    walkAmt: wa, wp: integ('ph_' + name, t), stride: clamp(vL / 3, 36, 60), smear: 0.35 * clamp((vL - 180) / 60, 0, 1) * wa,
    open: mt.o, ex, puff: mt.o, lid: num(name, 'lid', t), brow: num(name, 'brow', t),
    px: 4 * integ('gx_' + name, t) * fs, py: 3 * integ('gy_' + name, t),
    hr: -7 * P.p - 10 * integ('ly_' + name, t) - 6 * nod, bodyUp: 3 * P.p, wing: num(name, 'wing', t), snap: 5
  };
  // Brösel: schwere Lider, tiefer Atem, ab und zu müde den Kopf hängen lassen
  if (name === 'broesel') {
    o.ph = 0.3; o.period = 3.6; o.breath = 0.025 * Math.sin(2 * Math.PI * t / 3.6 + 0.3);
    o.blink = blinkClosure('broesel', t, 1.6);
    o.wing += (ex ? 0.4 : 0.12) * smooth(en * 1.5);
    o.lid -= 0.15 * P.p;
    const kd = lastLE(DROOP, t), dr = kd >= 0 ? env3(t - DROOP[kd], 0.25, 0.4, 0.3) * (1 - clamp(en * 2, 0, 1)) : 0;
    o.hr -= 6 * dr;
    const sg = env3(since('seufzer', t), 0.5, 0.9, 0.8);   // Seufzer: sackt zusammen, Lider fast zu
    o.hr -= 8 * sg; o.sy -= 0.06 * sg; o.lid = lerp(o.lid, 0.8, sg);
    o.lid = lerp(o.lid, 0.9, env3(since('stempeluhr', t), 0.3, 1.5, 0.5));   // Feierabend gestempelt: zufrieden
    o.lid += 0.15 * env3(since('grille', t), 0.3, 2.0, 0.5);
    const ts = Math.min(since('alarm', t), since('explosion_weich', t)), stl = startle(ts);
    o.sy *= 1 - stl.sq; o.sx *= 1 + 0.6 * stl.sq; o.y -= stl.up;
    o.lid = lerp(o.lid, 0, env3(ts, 0.06, 1.2, 0.4));
  } else {
    o.ph = 1.1; o.period = 3.1; o.breath = 0.018 * Math.sin(2 * Math.PI * t / 3.1 + 1.1);
    o.blink = blinkClosure(name, t);
    o.wing += 0.35 * accHold(who, t);   // Zugbegleiter zeigt mit dem Flügel
    o.hr += 4 * en;                      // spricht mit erhobenem Kinn
  }
  return o;
}

function poseKurt(t) {
  const sb = stBlend('kurt', 'screen', t, 'off');
  let mode = sb.cur;
  const talking = kurtSpeaking(t);
  if (mode === 'film' && talking) mode = 'on';   // spricht KURT, zeigt der Schirm sein Gesicht statt des Films
  const sw = Math.max(t - sb.tau, sb.cur === 'film' ? kurtSwitch(t) : -1e9);
  const mt = mouth('K', t), P = pulse('K', t);
  let lx = integ('gx_kurt', t), ly = integ('gy_kurt', t);
  const tgr = since('grille', t);
  if (tgr < 3.2) { const w = env3(tgr, 0.25, 2.3, 0.5); lx = lerp(lx, tgr < 0.75 ? 0.5 : -0.6, w); }   // Augen gleiten gegen Fussels Blick
  const others = Math.max(integ('en_F', t), integ('en_B', t), integ('en_G', t), integ('en_A', t));
  const tpl = since('plopp', t);
  return {
    x: num('kurt', 'x', t), y: num('kurt', 'y', t), s: num('kurt', 's', t), r: 0, shake: num('kurt', 'shake', t), t,
    crank: integ('crank', t), crankRate: integ('crankRate', t), mode, sinceScreen: sb.tau,
    flip: 0.04 + 0.96 * easeOut((t - sw) / 0.12),
    mo: mt.o, mw: mt.w, ms: mt.s, ansAmp: mouth('A', t, 'kurt').o, pulse: P.p,
    blink: blinkClosure('kurt', t), lx, ly,
    squint: sb.cur === 'on' && sb.prev === 'boot' ? env3(sb.tau, 0.15, 0.9, 0.3) : 0,
    n1: -0.6 + 0.12 * Math.sin(0.7 * t) + 1.7 * integ('needle', t), n2: 2.3 + 0.1 * Math.sin(0.53 * t + 1) - 0.9 * others,
    funnelR: 1.5 * P.sp, funnelSq: tpl < 1 ? 1 - 0.15 * Math.exp(-7 * tpl) * Math.cos(20 * tpl) * smooth(tpl / 0.03) : 1,
    steam: !!st('kurt', 'steam', t, 0)
  };
}

function updateCrumbs(t, scene, fx, fy) {
  let k = 0;
  const put = (x, y, r) => { if (k >= crumbs.length) return; const c = crumbs[k++]; show(c, true); setT(c, `translate(${x.toFixed(1)},${y.toFixed(1)}) rotate(${r.toFixed(0)})`); };
  if (st('crumbs', 'fussel', t, 0) && (scene === 'bahnhof' || scene === 'zug')) {
    const u = t - stT('crumbs', 'fussel', t);
    const n = scene === 'zug' ? 1 : 12;
    const floor = scene === 'zug' ? 815 : fy + 10;
    for (let i = 0; i < n; i++) {
      const tt = clamp(u - 0.3 - i * 0.05, 0, 9);
      const vx = rnd(i, 3) * 160, y0 = fy - 80;
      const y = Math.min(floor - (i % 4) * 4, y0 + 260 * tt + 600 * tt * tt);
      put(fx + vx * Math.min(tt, 0.6), y, i * 40 + tt * 300);
    }
  }
  if (st('crumbs', 'funnel', t, 0) && scene === 'halle') {
    const u = t - stT('crumbs', 'funnel', t);
    for (let i = 0; i < 24; i++) {
      const tt = (u * 0.9 + i / 24) % 1.6;
      const ang = -Math.PI / 2 + rnd(i, 8) * 1.1;
      const v = 700 + hash(i, 2) * 300;
      put(852 + Math.cos(ang) * v * tt, 500 + Math.sin(ang) * v * tt + 900 * tt * tt, i * 30 + tt * 500);
    }
  }
  if (st('crumbs', 'floor', t, 0) && scene === 'halle') {
    const u = t - stT('crumbs', 'floor', t);
    const left = Math.max(0, 30 - Math.floor(u * 1.8));
    for (let i = 0; i < left; i++) put(700 + hash(i, 4) * 700, 905 + hash(i, 5) * 60, i * 37);
  }
  for (; k < crumbs.length; k++) show(crumbs[k], false);
}

// Fussel auf der Endcard: glücklich, atmet, blinzelt, schaut zu Brösel, wenn der spricht
function poseEndFussel(t) {
  const lb = 0.6 * clamp(integ('en_B', t) * 3, 0, 1);
  return {
    x: 1180, y: 540, s: 1.15, r: Math.sin(t * 2) * 3 + 1.5 * Math.sin(2 * Math.PI * t / 5.3), face: 1, fsx: 1, fsy: 1, m: 0, ang: 0, t,
    bsy: 1 + 0.022 * Math.sin(2 * Math.PI * t / 2.8 + 1.3), lift: 0, thread: 1, Lx: 0, Ly: 0, tip: 0, curl: 0, sit: 0, tuck: 0, splay: 0,
    wide: 0, squint: 1, lid: 0.15, blink: blinkClosure('endFussel', t), lx: lb + 0.1 * wob(t, 3), ly: 0.05 * wob(t, 4), eyeScale: 1,
    raise: 0.4, tilt: 0, mo: 0.45, mw: 1, ms: 0, smile: 1
  };
}

// ---------------------------------------------------------------------------
// Bild berechnen
// ---------------------------------------------------------------------------
function render(frame) {
  const t = frame / TL.fps;   // ab hier zählt nur noch die Zeit
  const [scene, s0] = sceneAt(t);
  for (const n in SC) for (const g of SC[n]) show(g, n === scene);

  // Kamera
  let cx = num('cam', 'x', t), cy = num('cam', 'y', t), cz = num('cam', 'z', t), cr = num('cam', 'r', t);
  const ar = Math.abs(cr) * Math.PI / 180;
  if (ar > 0.001) cz = Math.max(cz, Math.cos(ar) + Math.sin(ar) * 1920 / 1080 + 0.04);
  cz = Math.max(cz, 1);
  const hw = 960 / cz, hh = 540 / cz;
  cx = clamp(cx, hw, 1920 - hw); cy = clamp(cy, hh, 1080 - hh);
  setT(world, `translate(960,540) rotate(${cr.toFixed(2)}) scale(${cz.toFixed(4)}) translate(${(-cx).toFixed(1)},${(-cy).toFixed(1)})`);

  const stage = !['logo', 'titel', 'filmtitel'].includes(scene);
  show(actors, stage); show(actorsBack, stage); show(actorsFront, stage); show(trainLayer, stage); show(fxLayer, stage);

  // Fussel
  const fv = actorVis('fussel', t, scene);
  show(fussel.g, fv);
  const fx = num('fussel', 'x', t), fy = num('fussel', 'y', t);
  let fo = null;
  if (fv) { fo = poseFussel(t); fussel.update(fo); }
  // KURT
  const kv = actorVis('kurt', t, scene);
  show(kurt.g, kv);
  if (kv) kurt.update(poseKurt(t));
  // Brösel
  const bv = actorVis('broesel', t, scene);
  show(broesel.g, bv);
  if (bv) {
    const o = posePigeon('broesel', 'B', t, scene);
    const inHalle = scene === 'halle', cA = integ('crank', t), crankAmt = inHalle ? stSmooth('broesel', 'crank', t, 0.25) : 0;
    o.y -= crankAmt * Math.abs(Math.sin(cA * Math.PI / 180)) * 6;   // wippt beim Kurbeln mit
    Object.assign(o, { crankAmt, crankA: cA, broom: st('broesel', 'broom', t, 0), sweepAmt: stSmooth('broesel', 'sweep', t, 0.25) });
    broesel.update(o);
  }
  // Gurrmann
  const gv = actorVis('gurrmann', t, scene);
  show(gurrmann.g, gv);
  if (gv) {
    const o = posePigeon('gurrmann', 'G', t, scene);
    const fly = stSmooth('gurrmann', 'fly', t, 0.2);
    // Fliegen: abheben ohne Sprung, Körper wippt im Flügelschlag, Schräglage beim Sinken/Steigen
    o.y -= stSmooth('gurrmann', 'fly', t, 0.3) * 30 + fly * 6 * Math.sin(t * 26 + 1.1 + Math.PI / 2);
    o.r -= clamp(numV('gurrmann', 'y', t) * 0.015, -18, 18) * (o.face < 0 ? -1 : 1) * fly;
    o.fly = fly;
    gurrmann.update(o);
  }
  // Taube auf Fussels Kopf: fliegt im Bogen an, landet mit kleinem Stauchen, reitet auf seinem Atem mit
  const sOn = st('sitter', 'on', t, 0) && scene === 'zug' && fv;
  show(sitter.g, sOn);
  if (sOn) {
    const tau = t - stT('sitter', 'on', t), u = clamp(tau / 0.7, 0, 1), fs = num('fussel', 's', t);
    const hx = fx + 6, hy = fy - fo.lift * fs - (150 + 130 * (fo.bsy - 1)) * fs;
    const xl = tau - 0.7, q = xl > 0 ? 0.15 * Math.exp(-7 * xl) * Math.sin(25 * xl) : 0;
    const fl = 1 - smooth((u - 0.8) / 0.2);
    sitter.update({
      x: lerp(1300, hx, ease('out', u)), y: lerp(300, hy, ease('io', u)) - 90 * Math.sin(Math.PI * u) + fl * 6 * Math.sin(t * 26 + 2 + Math.PI / 2),
      s: 0.55, face: 1, t, ph: 2, fly: fl, sit: 1 - fl, sx: 1 + 0.6 * q, sy: 1 - q, r: -10 * fl * (1 - u),
      breath: 0.018 * Math.sin(2 * Math.PI * t / 3.1 + 2), lid: 0.6, blink: blinkClosure('sitter', t), wing: 0, open: 0, px: -1, snap: 5
    });
  }
  // Ball (Idee)
  const balv = st('ball', 'vis', t, 0) && scene === 'halle';
  show(ball, balv);
  if (balv) setT(ball, `translate(${num('ball', 'x', t).toFixed(1)},${num('ball', 'y', t).toFixed(1)}) rotate(${(t * 400 % 360).toFixed(1)})`);
  // Zug
  const tv = st('train', 'vis', t, 0) && (scene === 'bahnhof' || scene === 'himmel');
  show(train.g, tv);
  if (tv) train.update({ x: num('train', 'x', t), y: num('train', 'y', t) + (st('train', 'wings', t, 0) ? Math.sin(t * 7) * 10 : 0), s: num('train', 's', t), r: num('train', 'r', t), doors: num('train', 'doors', t), wings: st('train', 'wings', t, 0), flap: st('train', 'flap', t, 0), t });

  updateCrowd(t, scene);
  updateCrumbs(t, scene, fx, fy);

  // Kulissen-Details
  if (scene === 'halle') {
    H.signN.textContent = String(st('sign', 'n', t, 3));
    const hh = (8 + t / 600) * 30, mm = (12 + t / 10) * 6;
    setT(H.hourHand, `rotate(${hh.toFixed(1)},1615,310)`); setT(H.minHand, `rotate(${mm.toFixed(1)},1615,310)`);
    const warn = st('warn', 'on', t, 0);
    const wp = 0.5 + 0.5 * Math.sin(t * 2 * Math.PI * 2.2);   // Warnleuchte 2.2 Hz (unter 3 Hz, fotosensibel unkritisch)
    setA(H.warnDome, 'fill', warn ? (wp > 0.5 ? '#FF7A9A' : C.him) : '#7A3046');
    show(H.warnRays, warn);
    if (warn) setT(H.warnRays, `rotate(${(t * 400 % 360).toFixed(1)},1500,66)`);
    setA(H.flash, 'opacity', warn ? (0.03 + 0.07 * wp).toFixed(3) : 0);
    const bo = integ('belt', t);
    setA(H.beltTop, 'stroke-dashoffset', (-bo).toFixed(1));
    for (const r of H.rollers) { const a = bo / 13; setA(r, 'd', `M${(r._x - Math.cos(a) * 10).toFixed(1)} ${(630 - Math.sin(a) * 10).toFixed(1)}L${(r._x + Math.cos(a) * 10).toFixed(1)} ${(630 + Math.sin(a) * 10).toFixed(1)}`); }
    const bw = clamp(integ('beltRate', t) / 190, 0, 1);   // Klappen schwingen mit dem Bandtempo
    H.flaps.forEach((fl, i) => setT(fl, bw > 0.002 ? `rotate(${(Math.sin(t * 6 + i) * 6 * bw).toFixed(1)},${1781 + i * 31},470)` : ''));
    const cm = st('crowd', 'mode', t, 'off'), cu = t - stT('crowd', 'mode', t);
    H.cards.forEach((c, i) => {
      if ((cm === 'clock' && cu > 1.2 + i * 0.5) || cm === 'tobelt' || cm === 'belt' || (cm === 'off' && t > TL.cues.endcard_hold - 60 && st('sign', 'n', t, 3) === 0)) {
        const uu = cm === 'clock' ? cu - 1.2 - i * 0.5 : 3;
        setT(c, `translate(${(-uu * 80 - i * 20).toFixed(0)},${Math.min(640, uu * 300 + uu * uu * 200).toFixed(0)}) rotate(${(uu * 120 * (i % 2 ? 1 : -1)).toFixed(0)},1746,${254 + i * 42})`);
      } else setT(c, '');
    });
    const fe = ['burst', 'chaos', 'clock', 'tobelt'].includes(cm);
    show(featherG, fe);
    if (fe) feathers.forEach((e, i) => { const tt = (t * 0.3 + i / 10) % 1, ex = 300 + i * 150 + Math.sin(t * 2 + i) * 60, ey = 100 + tt * 800; setA(e, 'cx', ex.toFixed(1)); setA(e, 'cy', ey.toFixed(1)); setA(e, 'transform', `rotate(${(Math.sin(t * 3 + i) * 40).toFixed(1)},${300 + i * 150},${ey.toFixed(1)})`); });
  } else show(featherG, false);
  if (scene === 'logo') {
    const p = num('logo', 'p', t);
    const th = H.logoThread, L = th._len || (th._len = th.getTotalLength());
    const up = smooth((p - 0.05) / 0.62);
    setA(th, 'stroke-dasharray', `${(L * up).toFixed(1)} ${L + 10}`);
    setA(H.wordClip, 'width', (190 + (H.logoW - 160) * smooth((p - 0.12) / 0.6)).toFixed(1));
    const bu = clamp((p - 0.78) / 0.1, 0, 1), bs = bu <= 0 ? 0 : (bu < 1 ? 1.5 * Math.sin(bu * Math.PI / 2) : 1 + 0.15 * Math.sin((p - 0.88) * 40) * Math.exp(-(p - 0.88) * 20));
    const [bx, by] = H.logoBallXY;
    setT(H.logoBall, `translate(${bx},${by}) scale(${bs.toFixed(3)}) translate(${-bx},${-by})`);
    setA(H.claim, 'opacity', smooth((p - 0.86) / 0.12).toFixed(2));
  }
  if (scene === 'titel') {
    const u = t - s0;
    const sc = u < 0.25 ? 1.8 - u * 3.2 : 1;
    setT(H.stamp, `translate(960,320) rotate(-4) scale(${Math.max(1, sc).toFixed(3)})`);
    setA(H.stamp, 'opacity', u < 0.05 ? 0 : 1);
    setT(H.t1, `translate(${(-(1 - smooth((u - 0.4) / 0.5)) * 1400).toFixed(0)},0)`);
    setT(H.t2, `translate(${((1 - smooth((u - 0.6) / 0.5)) * 1400).toFixed(0)},0)`);
  }
  if (scene === 'filmtitel') {
    H.ft1.textContent = 'FILM ' + st('filmtitel', 'nr', t, 1);
    H.ft2.textContent = st('filmtitel', 'name', t, '');
    const fl = 0.92 + 0.05 * Math.sin(t * 11.3) + 0.03 * Math.sin(t * 27.1);   // Röhrenflimmern, stetig
    setA(H.ft1, 'opacity', fl.toFixed(3)); setA(H.ft2, 'opacity', fl.toFixed(3));
    setA(H.ftGlow, 'opacity', (0.6 + 0.15 * Math.sin(t * 3.1)).toFixed(3));
  }
  if (scene === 'bahnhof') {
    const bt = st('board', 'text', t, 'leer');
    const rows = {
      leer: ['--:--  ----------', '', ''],
      kruemel: ['08:15  Krümelstadt', 'über Brösel-Allee, Taubenmarkt', 'pünktlich'],
      kruemel2: ['08:15  Krümelstadt', 'über Brösel-Allee, Taubenmarkt', 'Abfahrt bei ausreichend Krümeln'],
      einfahrt: ['08:15  Krümelstadt', 'über Brösel-Allee, Taubenmarkt', 'fährt ein · Vorsicht!']
    }[bt];
    H.b1.textContent = rows[0]; H.b2.textContent = rows[1]; H.b3.textContent = rows[2];
    setA(H.b3, 'opacity', bt === 'kruemel2' || bt === 'einfahrt' ? (((t * 1.25) % 1) < 0.65 ? 1 : 0.3) : 1);
    setT(H.secHand, `rotate(${((t * 6) % 360).toFixed(1)},1020,150)`);
    const a = mouth('A', t).o;
    setT(H.horn, `translate(1812,200) scale(${(1 + a * 0.06).toFixed(3)}) translate(-1812,-200)`);
    show(H.hornWaves, a > 0.02);
  }
  if (scene === 'zug') {
    const view = st('outside', 'view', t, 'land');
    show(H.outLand, view === 'land'); show(H.outBakery, view === 'bakery'); show(H.outClouds, view === 'clouds' || view === 'circle');
    const off = integ('land', t);
    setT(H.landFar, `translate(${(-(off * 0.3) % 1200).toFixed(1)},0)`);
    setT(H.landNear, `translate(${(-(off * 0.8) % 1200).toFixed(1)},0)`);
    setT(H.poles, `translate(${(-(off * 2.2) % 600).toFixed(1)},0)`);
    if (view === 'clouds' || view === 'circle') {
      setT(H.cloudRow, `translate(${(-(t * 420) % 600).toFixed(1)},${view === 'circle' ? (Math.sin(t * 1.2) * 60).toFixed(1) : 0})`);
      const bx = view === 'circle' ? 2200 - ((t * 500) % 2600) : 4000;
      setT(H.cloudBrezel, `translate(${bx.toFixed(1)},300)`);
    }
  }
  if (scene === 'himmel') {
    setT(H.sunRays, `rotate(${(t * 10 % 360).toFixed(1)},1620,190)`);
    H.clouds.forEach((c) => { const k = c._k, sp = 60 + (k % 3) * 50, x = ((k * 330 - t * sp) % 2400 + 2400) % 2400 - 300; setT(c, `translate(${x.toFixed(1)},${(140 + (k * 97) % 560)}) scale(${(0.7 + (k % 3) * 0.25).toFixed(2)})`); });
    const sw = st('swarm', 'on', t, 0);
    show(H.swarm, sw);
    if (sw) H.minis.forEach((m, i) => {
      const a = t * 0.9 + i * Math.PI * 2 / H.minis.length;
      const x = 960 + Math.cos(a) * 640, y = 520 + Math.sin(a) * 300, dir = -Math.sin(a) >= 0 ? 1 : -1;
      setT(m.g, `translate(${x.toFixed(1)},${y.toFixed(1)}) scale(${(dir * (0.8 + 0.25 * Math.sin(a))).toFixed(3)},${(0.8 + 0.25 * Math.sin(a)).toFixed(3)})`);
      setT(m.w, `rotate(${(Math.sin(t * 9 + i) * 20).toFixed(1)},0,-30)`);
      m.g.parentNode.appendChild && (Math.sin(a) > 0 ? H.swarm.appendChild(m.g) : H.swarm.insertBefore(m.g, H.brezel));
    });
  }
  if (scene === 'endcard') {
    const u = t - s0;
    H.endFussel.update(poseEndFussel(t));
    setT(H.endTitle, `translate(0,${((1 - smooth(u / 0.6)) * 300).toFixed(0)})`);
  }

  // Iris und Abblende
  const ir = num('iris', 'r', t);
  if (ir < 1150) { setA(irisPath, 'd', `M0 0H1920V1080H0Z M${960 - ir} 540a${ir} ${ir} 0 1 0 ${2 * ir} 0a${ir} ${ir} 0 1 0 ${-2 * ir} 0Z`); show(irisPath, true); }
  else show(irisPath, false);
  setA(fadeRect, 'opacity', num('fade', 'a', t).toFixed(3));
}

window.init = function (tl) { TL = tl; precompute(); return Math.round(tl.total * tl.fps); };
window.render = render;
// Für Prüfskripte: Zugriff auf Figuren, Kulissen und Kanäle (wird beim Rendern nicht benutzt)
window.STAGE = { fussel, kurt, broesel, gurrmann, sitter, crowd, train, H, world, INT, integ, num, numV, numA, mouth, pulse, BLINK, ACC, JUMP, poseFussel, posePigeon, poseKurt };
