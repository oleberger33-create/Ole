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
  ball: { x: 0, y: 0, s: 1 }, iris: { r: 1200, x: 960, y: 540 }, fade: { a: 0 }, logo: { p: 0 }, outside: { v: 1 }
};
// Easings (wie ease_fn in build.py): io = smoothstep, io5 = smootherstep, back/brake = easeOutBack mit
// ~7 % / ~3 % Überschwingen (c = 1.4 / 0.9)
const BACK_C = { back: 1.4, brake: 0.9 };
function ease(e, u) {
  u = clamp(u, 0, 1);
  if (e === 'lin') return u;
  if (e === 'in') return u * u;
  if (e === 'out') return 1 - (1 - u) * (1 - u);
  if (e === 'io5') return u * u * u * (u * (6 * u - 15) + 10);
  const c = BACK_C[e];
  if (c) { const v = u - 1; return 1 + (c + 1) * v * v * v + c * v * v; }
  return u * u * (3 - 2 * u);
}
// Wert eines Segments [t0, t1, von, nach, ease]; der Kamera-Zoom läuft logarithmisch (gleichmäßig empfundene Fahrt)
function segVal(s, t, logz) {
  const e = ease(s[4], (t - s[0]) / (s[1] - s[0]));
  return logz ? s[2] * Math.pow(s[3] / s[2], e) : lerp(s[2], s[3], e);
}
function num(actor, prop, t) {
  const segs = TL.tracks[actor] && TL.tracks[actor][prop];
  let v = (DEF[actor] && DEF[actor][prop] !== undefined) ? DEF[actor][prop] : 0;
  if (!segs) return v;
  const logz = actor === 'cam' && prop === 'z';
  for (let i = 0; i < segs.length; i++) {
    const s = segs[i];
    if (s[0] > t) break;
    if (t < s[1]) v = segVal(s, t, logz);
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
function easeD(e, u) {
  if (e === 'lin') return 1; if (e === 'in') return 2 * u; if (e === 'out') return 2 * (1 - u);
  if (e === 'io5') return 30 * u * u * (1 - u) * (1 - u);
  const c = BACK_C[e];
  if (c) { const v = u - 1; return 3 * (c + 1) * v * v + 2 * c * v; }
  return 6 * u * (1 - u);
}
function easeDD(e, u) {
  if (e === 'lin') return 0; if (e === 'in') return 2; if (e === 'out') return -2;
  if (e === 'io5') return 60 * u - 180 * u * u + 120 * u * u * u;
  const c = BACK_C[e];
  if (c) return 6 * (c + 1) * (u - 1) + 2 * c;
  return 6 - 12 * u;
}
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
// Weiche Hülle einer Sprechzeile: e = 0..1 ab t0 − 0.15 über ain herein, nach t1 über aout hinaus; l = die Zeile
// (für Haltungen beim Reden; l bleibt im Ausklingen gültig, damit z. B. l.ex nicht vorzeitig umspringt)
const TE0 = { e: 0, l: null };
function talkEnv(who, t, ain, aout) {
  const l = lineAt(who, t, 0.15, aout);
  return l ? { e: smooth((t - l.t0 + 0.15) / ain) * (1 - smooth((t - l.t1) / aout)), l } : TE0;
}
// Geglättete Sprech-Hülle einer Figur (Anstieg 0.1 s, Abklingen 0.25 s, läuft 1 s über das Zeilenende hinaus):
// für Lautsprecher, Horn-Wellen und Zuhörer-Reaktionen, die nicht im 60-Hz-Takt flackern sollen
function ampS(who, t, fx) {
  const l = lineAt(who, t, 0, 1.0);
  if (!l || (fx !== undefined && l.fx !== fx) || !l.envS) return 0;
  const p = (t - l.t0) * TL.envRate, i = Math.floor(p);
  return lerp(l.envS[i] || 0, l.envS[i + 1] || 0, p - i);
}
// Durchsage läuft (weich 0..1: 0.3 s herein, 0.5 s hinaus), ohne KURTs Lautsprecher in der Halle
function annW(t) {
  const l = lineAt('A', t, 0.3, 0.5);
  if (!l || l.fx) return 0;
  return smooth((t - l.t0 + 0.3) / 0.3) * (1 - smooth((t - l.t1) / 0.5));
}
// Fahrgäste im Zug: federn kurz nach dem Wagen nach (Welle von links nach rechts), kippen beim Bremsen
function ride(x, t, ky, kr) {
  const d = 0.12 * clamp(x / 1920, 0, 1);
  return { dy: ky * integ('rockY', t - 0.06 - d), dr: kr * integ('seatLean', t - d) };
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
  // Szenenanfang: jede Figur blinzelt einmal beim "Ankommen", aber nicht alle im selben Bild
  const f0 = forced.concat(TL.scenes.map((s, i) => s[0] + 0.3 + 0.9 * hash(seed, i + 0.5))).sort((a, b) => a - b), f = [], out = [];
  for (const c of f0) if (!f.length || c - f[f.length - 1] > 0.7) f.push(c);   // dicht folgende erzwungene zusammenfassen
  for (const c of eventList(seed, 0.5 + 2 * hash(seed, 0.5), 2.6, 6.0, 0.18, 0.24)) {
    const k = lastLE(f, c + 0.9);
    if (!(k >= 0 && f[k] > c - 0.9)) out.push(c);   // geplante Lidschläge weichen erzwungenen (±0.9 s)
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
const WALKERS = { fussel: { lean: 0.02, leanMax: 12 }, broesel: { lean: 0.012, leanMax: 9 }, gurrmann: { lean: 0.012, leanMax: 9 } };
const GAZERS = ['fussel', 'kurt', 'broesel', 'gurrmann'];
const W2A = { F: 'fussel', K: 'kurt', B: 'broesel', G: 'gurrmann' };
const JUMP = { up: [], down: [], air: [] };   // Fussels Absprünge, Landungen, Flugphasen (aus der y-Spur)
let KSW = [];      // KURT: Grenzen der Sprechfenster [an, aus, an, aus, ...]
let PECK = [], PECKF = [], DROOP = [];
let STOPS = [];    // Zeiten, zu denen der Zug an einer Bäckerei zum Stehen kommt
let BURST = [];    // Zeiten der Explosion (Schwarm bricht aus KURT aus)
let CLOCK_T = null; // erster Anflug der Tauben auf die Stempeluhr (dann fallen die Stempelkarten)
let FOUNT = [];    // Krümel-Fontäne aus dem Trichter: [an, aus]-Intervalle
let FLAPPASS = [[], [], [], [], []];   // je Klappe der Versand-Luke: Zeiten, zu denen jemand hindurchfährt

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
  if (scene === 'zug') return [1780, 100];
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
  const R = TL.envRate, ka = 1 - Math.exp(-1 / (R * 0.1)), kr = 1 - Math.exp(-1 / (R * 0.25));
  for (const l of TL.lines) {   // geglättete Hülle für ampS()
    const out = new Float32Array(l.env.length + R);
    let y = 0;
    for (let i = 0; i < out.length; i++) { const v = l.env[i] || 0; y += (v > y ? ka : kr) * (v - y); out[i] = y; }
    l.envS = out;
  }
  STOPS = ((TL.tracks.outside && TL.tracks.outside.v) || []).filter(s => s[3] === 0 && s[1] > s[0]).map(s => s[1]);
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
  buildIdle();
  buildCrowdModes();
  integrate(forced);
  prepareCamera();
  buildFlapPasses();
  // ---- Lidschläge: Zufallsplan + erzwungene (Schnitt, Augen-Wechsel, Blicksprung, Reaktionen) ----
  const eyeT = ((TL.states.fussel && TL.states.fussel.eyes) || []).map(e => e[0]);
  BLINK.fussel = blinkList(1, eyeT.concat(forced.fussel, SFXT.fehler || []));
  BLINK.kurt = blinkList(2, forced.kurt.concat((SFXT.plopp || []).map(x => x + 0.02)));
  BLINK.broesel = blinkList(3, forced.broesel);
  BLINK.gurrmann = blinkList(4, forced.gurrmann);
  BLINK.endFussel = blinkList(5, []);
  BLINK.sitter = blinkList(6, []);
  for (let i = 0; i < 14; i++) BLINK['crowd' + i] = blinkList(10 + i, []);
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
  // KURTs Kurbel dreht nur, solange Brösel kurbelt (Zustand broesel crank), und trudelt danach aus
  const broeselCrank = stCur('broesel', 'crank', 0), crankFast = stCur('broesel', 'crankfast', 0), beltRun = stCur('belt', 'run', 0);
  const outV = segCur('outside', 'v'), fWalk = stCur('fussel', 'walk', 0);
  const kUp = 1 - Math.exp(-dt / 0.25), kDown = 1 - Math.exp(-dt / 0.5), kBelt = 1 - Math.exp(-dt / 0.35);
  // Federn: semi-implizites Euler, v += (−w²(y−Ziel) − 2zw·v)·dt; y += v·dt
  const W = Object.keys(WALKERS).map(name => ({
    name, cfg: WALKERS[name], cx: segCur(name, 'x'), cy: segCur(name, 'y'), cs: segCur(name, 's'), cf: segCur(name, 'flip'),
    vis: stCur(name, 'vis', 0), dist: arr(), lean: arr(), squash: arr(), ph: arr(), vL: f32(),
    l: 0, lv: 0, q: 0, qv: 0, px: null, py: null, phase: 0, wasVis: 0
  }));
  const springStep = (y, v, target, w, z) => { v += (-w * w * (y - target) - 2 * z * w * v) * dt; return [y + v * dt, v]; };
  const wL = 13, zL = 0.35, wQ = 2 * Math.PI * 2.6, zQ = 0.3;   // Neigung: schwingt nach dem Anhalten 2–3-mal nach
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
  // Zugwagen (nur Szene zug): Federung auf den Schienenstößen, phasengleich mit den "ta-dam" in zug_fahrt
  // (Stoßabstand J Landschafts-px = 520 px/s ÷ 3.2 Hz), zweites Drehgestell 0.11 s später; Wanken mit
  // wechselnder Seite; Ruck bei 'outside lurch'. seatLean: Fahrgäste kippen beim Bremsen nach vorn (+).
  const rockY = f32(), rockR = f32(), seatLean = f32();
  // Himmel: Windweg der Wolken und Kreiswinkel des Schwarms; Richtung ('swarm' dir) dreht in 0.8 s weich um
  const cloud = arr(), swarmA = arr();
  // Zug am Bahnsteig: Wagenkasten nickt vor allem auf Änderungen der Beschleunigung (Ziel −0.003°/(px/s²) × (a − a
  // geglättet, τ 0.45 s) plus wenig Dauerneigung −0.001°/(px/s²) × a): beim Halt federt er zurück, beim Anfahren hockt
  // er hinten ein und richtet sich auf. Feder 1.3 Hz, ζ 0.32, danach weich auf ±0.8° begrenzt. Stöße an den
  // Schienenstößen alle 170 px (Feder 3 Hz), Stärke nach Tempo.
  const trainPitch = f32(), trainBump = f32(), trX = segCur('train', 'x'), trVis = stCur('train', 'vis', 0), trWings = stCur('train', 'wings', 0);
  let tp = 0, tpv = 0, tbmp = 0, tbv = 0, tJ = null, accLP = null;
  const kAcc = 1 - Math.exp(-dt / 0.45);
  const J = 162.5, wRy = 2 * Math.PI * 2.4, zRy = 0.3, wRr = 2 * Math.PI * 1.1, zRr = 0.4, wSl = 13, zSl = 0.35;
  const viewCur = stCur('outside', 'view', 'land');
  const ZF = SFXT.zug_fahrt || [], LURCH = ((TL.states.outside && TL.states.outside.lurch) || []).filter(e => e[1]).map(e => e[0]);
  let ry = 0, rvy = 0, rr = 0, rvr = 0, sl = 0, slv = 0, jRef = 0, jLast = 0, rSide = 1, zf = 0, lu = 0, bogie = [];
  const cuts = TL.scenes.map(s => s[0]);
  let cr = 0, br = 0, cut = 0, scene = TL.scenes[0][1];
  for (let i = 1; i < n; i++) {
    const t = i * dt;
    const cT = broeselCrank(t) ? (crankFast(t) ? 900 : 380) : 0;
    cr += (cT - cr) * (cT > cr ? kUp : kDown);
    crank[i] = crank[i - 1] + cr * dt; crankRate[i] = cr;
    const bT = beltRun(t) ? 240 : 0;
    br += (bT - br) * kBelt;
    belt[i] = belt[i - 1] + br * dt; beltRate[i] = br;
    land[i] = land[i - 1] + outV(t).v * 520 * dt;
    let atCut = false;
    while (cut < cuts.length && cuts[cut] <= t) { scene = TL.scenes[cut][1]; cut++; atCut = true; }
    const sb = stBlend('swarm', 'dir', t, 1), dS = lerp(sb.prev, sb.cur, smooth(sb.tau / 0.8));
    cloud[i] = cloud[i - 1] + dS * dt; swarmA[i] = swarmA[i - 1] + 0.9 * dS * dt;
    // ---- Zugwagen ----
    while (zf < ZF.length && ZF[zf] <= t) { jRef = land[i]; jLast = 0; zf++; }
    if (scene !== 'zug' || atCut) { ry = rvy = rr = rvr = sl = slv = 0; bogie = []; }
    if (scene === 'zug') {
      const ov = outV(t), v = ov.v, view = viewCur(t), rails = view === 'land' || view === 'bakery';
      const jn = Math.floor((land[i] - jRef) / J + 1e-6);
      if (rails && jn > jLast && v > 0.02) {
        rvy -= 55 * v; bogie.push([t + 0.11, 40 * v]);
        rvr += 0.9 * rSide * v; rSide = -rSide;
      }
      jLast = Math.max(jLast, jn);
      while (bogie.length && bogie[0][0] <= t) rvy -= bogie.shift()[1];
      while (lu < LURCH.length && LURCH[lu] <= t) { rvr -= 16; rvy += 80; lu++; }
      [ry, rvy] = springStep(ry, rvy, 0, wRy, zRy);
      [rr, rvr] = springStep(rr, rvr, 0, wRr, zRr);
      const sT = clamp(-segV(ov.s, t) * 3, -4, 4);   // Bremsen (dv/dt < 0): nach vorn, in Fahrtrichtung (+x)
      [sl, slv] = springStep(sl, slv, sT, wSl, zSl);
      const air = rails ? 0 : 1;   // fliegend: Luftschaukeln statt Schienenstöße
      rockY[i] = ry + air * (6 * Math.sin(1.1 * t) + 3 * Math.sin(2.3 * t + 0.7));
      rockR[i] = rr + air * 0.6 * Math.sin(0.7 * t + 0.3);
      seatLean[i] = sl;
    } else { rockY[i] = rockR[i] = seatLean[i] = 0; }
    while (lu < LURCH.length && LURCH[lu] <= t) lu++;
    if (scene === 'bahnhof' && trVis(t) && !trWings(t) && !atCut) {
      const X = trX(t), acc = segA(X.s, t), vx = segV(X.s, t), j = Math.floor(X.v / 170);
      if (accLP === null) accLP = acc;   // Auftritt (schon in Fahrt): kein Ruck aus dem Nichts
      accLP += (acc - accLP) * kAcc;
      [tp, tpv] = springStep(tp, tpv, clamp(-0.003 * (acc - accLP) - 0.001 * acc, -1.2, 1.2), 2 * Math.PI * 1.3, 0.32);
      if (tJ !== null && j !== tJ) tbv -= 0.07 * Math.abs(vx);
      tJ = j;
      [tbmp, tbv] = springStep(tbmp, tbv, 0, 2 * Math.PI * 3, 0.3);
    } else { tp = tpv = tbmp = tbv = 0; tJ = null; accLP = null; }
    trainPitch[i] = 0.8 * Math.tanh(tp / 0.8); trainBump[i] = tbmp;
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
      let vL = Math.hypot(vx, vy) / S;
      if (a.name === 'fussel' && fWalk(t) && Math.abs(Y.v - 610) < 40) vL += br / S;   // auf dem laufenden Band: läuft auf der Stelle dagegen an
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
  Object.assign(INT, { dt, crank, crankRate, belt, beltRate, land, thrX, thrY, jig, needle, rockY, rockR, seatLean, trainPitch, trainBump, cloud, swarmA });
  for (const a of W) Object.assign(INT, { ['dist_' + a.name]: a.dist, ['lean_' + a.name]: a.lean, ['squash_' + a.name]: a.squash, ['ph_' + a.name]: a.ph, ['vL_' + a.name]: a.vL });
  for (const w of WHOS) INT['en_' + w] = EN[w];
  for (const g of G) Object.assign(INT, { ['gx_' + g.a]: g.gx, ['gy_' + g.a]: g.gy, ['lx_' + g.a]: g.lx, ['ly_' + g.a]: g.ly });
}
// ---------------------------------------------------------------------------
// Kamera. Vorab (init): je Szenen-Intervall ein fester Mindestzoom, der Handkamera-Drift, Wagen-Schaukeln
// und Kamera-Rollen abdeckt (kein Zoom-Pumpen); alle Schlüssel x/y werden auf den gültigen Bereich ihres
// Endzooms begrenzt (Fahrten laufen nie mehr gegen den Bildrand); x, y, ln z laufen durch eine Feder
// (Nachschwingen ~1.5 %, ~70 ms Nachlauf), die an Schnitten (Dauer 0) und Szenenwechseln einrastet.
// Pro Bild: Handkamera-Drift im Bildraum und Stöße aus den Geräuschen (Explosion, Stempel, ...).
// ---------------------------------------------------------------------------
const DRIFT_W = { halle: 1, bahnhof: 1, zug: 0.4, himmel: 0.4 };
const SHAKE_W = { explosion_weich: 1, stamp: 0.6, aus: 0.35, bremse: 0.3, glitch: 0.3, hebel: 0.2, tuer_zu: 0.15, hop: 0.12, plopp: 0.1 };
let SCN = [];
function sceneIdx(t) { return Math.max(0, lastLE(TL.scenes, t + 1e-6, s => s[0])); }
// Halbe Ausdehnung des sichtbaren Weltausschnitts bei Zoom z und Rollwinkel a [rad], plus Ränder mx/my [Welt-px]
function camExt(z, a, mx, my) {
  const c = Math.cos(a), sn = Math.abs(Math.sin(a));
  return [Math.min(960, (960 * c + 540 * sn) / z + mx), Math.min(540, (960 * sn + 540 * c) / z + my)];
}
function prepareCamera() {
  const sc = TL.scenes, dt = INT.dt;
  SCN = sc.map(([t0, name], i) => {
    const t1 = i + 1 < sc.length ? sc[i + 1][0] : TL.total, w = DRIFT_W[name] || 0;
    let rMax = 0, ry = 0, rk = 0;
    for (let t = t0; t < t1; t += 1 / 30) rMax = Math.max(rMax, Math.abs(num('cam', 'r', t)));
    for (let k = Math.floor(t0 / dt); k < Math.min(INT.rockY.length, t1 / dt); k++) { ry = Math.max(ry, Math.abs(INT.rockY[k])); rk = Math.max(rk, Math.abs(INT.rockR[k])); }
    const safe = w > 0 || ry > 0 ? 2 : 0;
    const K = { name, t0, t1, w, aDeg: 0.15 * w + rk, sx: 5 * w + safe, sy: 3.5 * w + safe, rx: 1000 * Math.sin(rk * Math.PI / 180), ry };
    const a = (rMax + K.aDeg) * Math.PI / 180, c = Math.cos(a), sn = Math.sin(a);
    K.zMin = Math.max(1, (960 * sn + 540 * c + K.sy) / (540 - K.ry), (960 * c + 540 * sn + K.sx) / (960 - K.rx));
    return K;
  });
  // Zoom-Schlüssel nie unter den Mindestzoom der Szene (sonst liefe die Fahrt mit Tempo in die Begrenzung
  // und stünde ruckartig); Startwert = (angehobener) Wert davor
  const zs = (TL.tracks.cam && TL.tracks.cam.z) || [];
  zs.forEach((s, j) => {
    let v = DEF.cam.z;
    for (let q = 0; q < j; q++) { const o = zs[q]; if (o[0] > s[0]) break; v = s[0] < o[1] ? segVal(o, s[0], true) : o[3]; }
    const zMin = SCN[sceneIdx(s[0])].zMin;
    s[2] = Math.max(v, zMin); s[3] = Math.max(s[3], zMin);
  });
  // Schlüssel begrenzen: Endwert auf den gültigen Bereich beim Endzoom, Startwert = (begrenzter) Wert davor
  for (const p of ['x', 'y']) {
    const segs = (TL.tracks.cam && TL.tracks.cam[p]) || [];
    segs.forEach((s, j) => {
      let v = DEF.cam[p];
      for (let q = 0; q < j; q++) { const o = segs[q]; if (o[0] > s[0]) break; v = s[0] < o[1] ? segVal(o, s[0]) : o[3]; }
      s[2] = v;
      const K = SCN[sceneIdx(s[0])], zE = Math.max(num('cam', 'z', s[1]), K.zMin);
      const [ex, ey] = camExt(zE, (Math.abs(num('cam', 'r', s[1])) + K.aDeg) * Math.PI / 180, K.sx / zE + K.rx, K.sy / zE + K.ry);
      s[3] = p === 'x' ? clamp(s[3], ex, 1920 - ex) : clamp(s[3], ey, 1080 - ey);
    });
  }
  // Feder auf x, y, ln z (240 Hz). Einrasten an Schnitten; Zoom-Segmente mit 'in' (Fahrt in KURTs Schirm)
  // laufen ungefedert, damit der Anschluss an den Filmtitel bildgenau sitzt.
  const n = INT.rockY.length, camX = new Float32Array(n), camY = new Float32Array(n), camLZ = new Float32Array(n);
  const tr = TL.tracks.cam || {}, snaps = sc.map(s => s[0]);
  for (const p of ['x', 'y', 'z']) for (const s of tr[p] || []) if (s[1] - s[0] < 1e-6) snaps.push(s[0]);
  snaps.sort((a, b) => a - b);
  const cur = (p, logz) => {
    const segs = tr[p] || [];
    let k = 0;
    return t => {
      while (k < segs.length && segs[k][0] <= t) k++;
      const sg = segs[k - 1];
      if (!sg) return { v: DEF.cam[p], s: null };
      return t < sg[1] ? { v: segVal(sg, t, logz), s: sg } : { v: sg[3], s: null };
    };
  };
  const cX = cur('x'), cY = cur('y'), cZ = cur('z', true), w = 18, ze = 0.7;
  let x = 0, y = 0, lz = 0, vx = 0, vy = 0, vz = 0, sk = 0;
  for (let i = 0; i < n; i++) {
    const t = i * dt, X = cX(t).v, Y = cY(t).v, Z = cZ(t), LZ = Math.log(Z.v);
    let snap = i === 0;
    while (sk < snaps.length && snaps[sk] <= t + 1e-9) { snap = true; sk++; }
    if (snap) { x = X; y = Y; lz = LZ; vx = vy = vz = 0; } else {
      vx += (-w * w * (x - X) - 2 * ze * w * vx) * dt; x += vx * dt;
      vy += (-w * w * (y - Y) - 2 * ze * w * vy) * dt; y += vy * dt;
      vz += (-w * w * (lz - LZ) - 2 * ze * w * vz) * dt; lz += vz * dt;
    }
    if (Z.s && Z.s[4] === 'in') { lz = LZ; vz = Math.log(Z.s[3] / Z.s[2]) * segV([Z.s[0], Z.s[1], 0, 1, 'in'], t); }
    camX[i] = x; camY[i] = y; camLZ[i] = lz;
  }
  Object.assign(INT, { camX, camY, camLZ });
}
// Wer auf dem Band durch die Versand-Luke fährt, stößt die Klappen auf (Zeiten vorab)
function buildFlapPasses() {
  BURST = CREC.filter(r => r.mode === 'burst').map(r => r.t0);
  const ck = CREC.find(r => r.mode === 'clock');
  CLOCK_T = ck ? ck.t0 : null;
  FOUNT = [];
  for (const [t0, on] of (TL.states.crumbs && TL.states.crumbs.funnel) || []) {
    const last = FOUNT[FOUNT.length - 1];
    if (on && (!last || last[1] < t0)) FOUNT.push([t0, 1e9]); else if (!on && last && last[1] === 1e9) last[1] = t0;
  }
  FLAPPASS = [[], [], [], [], []];
  const riders = [];
  CREC.forEach((rec, k) => {
    if (rec.mode !== 'belt') return;
    const t1 = k + 1 < CREC.length ? CREC[k + 1].t0 : TL.total;
    for (let i = 0; i < CROWD_N; i++) riders.push([rec.t0, t1, t => beltX(i) + 55 + integ('belt', t) - integ('belt', rec.t0)]);
  });
  const gb = (TL.states.gurrmann && TL.states.gurrmann.belt) || [];
  gb.forEach(([t0, on], k) => { if (on) riders.push([t0, k + 1 < gb.length ? gb[k + 1][0] : TL.total, t => gurrX(t) + 80]); });
  for (const [t0, t1, X] of riders) for (let f = 0; f < 5; f++) {
    const xf = 1768 + 31 * f;
    for (let t = t0; t < t1; t += 1 / 120) if (X(t) >= xf) { FLAPPASS[f].push(t); break; }
  }
  for (const P of FLAPPASS) P.sort((a, b) => a - b);
}
// Gurrmann fährt auf dem Band mit (Zustand belt): x = Schlüsselwert + Bandweg seit dem Aufsteigen
function gurrX(t) {
  const x = num('gurrmann', 'x', t);
  return st('gurrmann', 'belt', t, 0) ? x + integ('belt', t) - integ('belt', stT('gurrmann', 'belt', t)) : x;
}
// Stoß-Stärke 0..1 aus den Geräuschen der letzten 1.5 s (springt beim Aufprall, klingt mit e^(−6 t) ab)
function shakeAmt(t) {
  let a = 0;
  for (const name in SHAKE_W) {
    const L = SFXT[name];
    if (!L) continue;
    for (let k = lastLE(L, t); k >= 0 && t - L[k] < 1.5; k--) a += SHAKE_W[name] * Math.exp(-6 * (t - L[k]));
  }
  return Math.min(1, a);
}
// Kamera eines Bildes: Mittelpunkt, Zoom, Rollen und Bildraum-Versatz (Drift + Stoß)
function camera(t) {
  const K = SCN[sceneIdx(t)];
  let cx = integ('camX', t), cy = integ('camY', t), cz = Math.exp(integ('camLZ', t));
  const cr = num('cam', 'r', t), tr = shakeAmt(t), t2 = tr * tr;
  // Mindestzoom weich (Softplus in ln z, Breite 1 %): das Nachschwingen der Feder läuft nie mit Tempo gegen eine Kante.
  // Stoß: kurz hineinstoßen, damit der Rand nie sichtbar wird
  const lzx = (Math.log(cz) - Math.log(K.zMin)) / 0.01;
  cz = K.zMin * Math.exp(0.01 * (lzx > 30 ? lzx : Math.log1p(Math.exp(lzx)))) * (1 + 0.045 * t2);
  const dw = K.w * clamp((4 - cz) / 2.5, 0, 1);   // Handkamera; ganz nah (Fahrt in den Schirm) ruhig
  const P2 = 2 * Math.PI;
  const dx = 5 * dw * wob(t, 11) + 16 * t2 * (0.6 * Math.sin(P2 * 13 * t) + 0.4 * Math.sin(P2 * 19 * t + 1.3));
  const dy = 3.5 * dw * wob(t, 12) + 16 * t2 * (0.6 * Math.sin(P2 * 17 * t + 0.7) + 0.4 * Math.sin(P2 * 27 * t + 2.1));
  const dr = 0.15 * dw * wob(t, 13) + 0.5 * t2 * Math.sin(P2 * 11 * t + 0.4);
  const [ex, ey] = camExt(cz, (Math.abs(cr) + K.aDeg + 0.5 * t2) * Math.PI / 180, (K.sx + 16 * t2) / cz + K.rx, (K.sy + 16 * t2) / cz + K.ry);
  cx = clamp(cx, ex, 1920 - ex); cy = clamp(cy, ey, 1080 - ey);
  return { cx, cy, cz, cr: cr + dr, dx, dy, K };
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
  let tlen = 0, thr = 1;
  return {
    g,
    // Spitze des sichtbaren Fadens in den Koordinaten von ref (z. B. der Welt); nur nach update() und wenn sichtbar
    tipIn(ref) {
      if (!tlen) return null;
      const m = ref.getCTM(), mt = thread.getCTM();
      if (!m || !mt) return null;
      const q = thread.getPointAtLength(tlen * thr);
      return new DOMPoint(q.x, q.y).matrixTransform(DOMMatrix.fromMatrix(m).invertSelf().multiplySelf(DOMMatrix.fromMatrix(mt)));
    },
    update(o) {
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
      thr = o.thread;
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
  E('rect', { x: 30, y: 60, width: 170, height: 172, rx: 28, fill: C.pet }, inner);
  E('rect', { x: 30, y: 60, width: 170, height: 172, rx: 28, fill: 'url(#felt)' }, inner);
  E('path', { d: 'M30 200H200V204A28 28 0 0 1 172 232H58A28 28 0 0 1 30 204Z', fill: C.petD }, inner);
  // Kurbel vorn auf der Seitenwand: Griff 30 px (lokal) vom Drehpunkt (200,128), kreist ganz sichtbar vor dem
  // Gehäuse; update() gibt seine Weltposition für Brösels Flügel heraus
  const crank = E('g', null, inner), CRANK_H = [200 + 30 * Math.cos(-0.87), 128 + 30 * Math.sin(-0.87)];
  E('path', { d: `M200 128L${f1(CRANK_H[0])} ${f1(CRANK_H[1])}`, stroke: C.ink, 'stroke-width': 9, 'stroke-linecap': 'round' }, crank);
  E('rect', { x: f1(CRANK_H[0] - 8), y: f1(CRANK_H[1] - 13), width: 16, height: 26, rx: 8, fill: C.him }, crank);
  E('circle', { cx: 200, cy: 128, r: 9, fill: C.ink }, crank);
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
  // Der zuletzt gezeigte Film läuft hier weiter: render() hängt Kulisse und Darsteller dieser Szene in filmMini
  const filmMini = E('g', null, film);
  // Filmtitel auf dem Schirm (vor dem Schnitt auf die Titelkarte): genau so groß und so hell, wie die Karte
  // im ersten Bild steht (Kamera-Zoom 9 × KURT 1.6 = 14.4, Karte zu Beginn 1.25-fach)
  const title = E('g', null, disp);
  E('rect', { x: 70, y: 84, width: 90, height: 90, fill: '#163A3E' }, title);
  const titleT = T(E('text', { x: 115, y: 121.92, 'text-anchor': 'middle', 'font-family': FONT.mono, 'font-weight': 500, 'font-size': 5.556, fill: C.senf, 'letter-spacing': 1.389 }, title), 'FILM 1');
  const ans = E('g', null, disp); const bars = [];
  for (let i = 0; i < 7; i++) bars.push(E('rect', { x: 84 + i * 9, width: 6, rx: 2, fill: C.senf }, ans));
  const tube = E('rect', { fill: C.garn, rx: 1.5 }, content);   // Röhre schaltet ab: Strich, dann Punkt
  const scan = E('rect', { x: 70, y: 84, width: 90, height: 90, fill: 'url(#scan)', opacity: 0.5 }, inner);
  E('circle', { cx: 132, cy: 104, r: 4, fill: '#fff', opacity: 0.18 }, inner);
  E('rect', { x: 80, y: 205, width: 70, height: 20, rx: 3, fill: C.senf }, inner);
  T(E('text', { x: 115, y: 219.5, 'text-anchor': 'middle', 'font-family': FONT.mono, 'font-size': 11, 'font-weight': 500, fill: C.ink, 'letter-spacing': 1 }, inner), 'K.U.R.T.');
  E('circle', { cx: 56, cy: 215, r: 9, fill: C.garn }, inner);
  const n1 = E('path', { stroke: C.ink, 'stroke-width': 2.5, 'stroke-linecap': 'round' }, inner);
  E('circle', { cx: 174, cy: 215, r: 9, fill: C.garn }, inner);
  const n2 = E('path', { stroke: C.ink, 'stroke-width': 2.5, 'stroke-linecap': 'round' }, inner);
  const rig = {
    g, filmMini, handleW: null, funnelM: null, update(o) {
      const sh = o.shake, t = o.t;   // stetiges Rattern statt Zufallssprüngen pro Bild
      const jx = sh * 7 * rattle(t, 1), jy = sh * 4 * rattle(t, 2), jr = sh * 1.5 * rattle(t, 3);
      // Betonung: Gehäuse staucht minimal um die Füße
      const gsy = o.s * (1 - 0.012 * o.pulse), fsx = 1 + 0.6 * (1 - o.funnelSq);
      setT(g, `translate(${f1(o.x + jx)},${f1(o.y + jy)}) rotate(${f2(o.r + jr)}) scale(${o.s},${gsy.toFixed(4)}) translate(-115,-262)`);
      setT(funnel, `rotate(${f2(o.funnelR)},110,46) translate(110,46) scale(${f3(fsx)},${f3(o.funnelSq)}) translate(-110,-46)`);
      setT(crank, `rotate(${(o.crank % 360).toFixed(1)},200,128)`);
      // Weltlage von Kurbelgriff und Trichter (für Brösels Flügel und den Ausschnitt an der Trichterkante)
      const M = new DOMMatrix().translateSelf(o.x + jx, o.y + jy).rotateSelf(o.r + jr).scaleSelf(o.s, gsy).translateSelf(-115, -262);
      const ca = o.crank * Math.PI / 180, hx = CRANK_H[0] - 200, hy = CRANK_H[1] - 128;
      rig.handleW = M.transformPoint(new DOMPoint(200 + hx * Math.cos(ca) - hy * Math.sin(ca), 128 + hx * Math.sin(ca) + hy * Math.cos(ca)));
      rig.funnelM = M.translate(110, 46).rotateSelf(o.funnelR).scaleSelf(fsx, o.funnelSq).translateSelf(-110, -46);
      // Zeiger: links VU-Meter seiner Stimme, rechts "hört zu"; mit Kurbeldrehzahl zittern beide
      const cw = clamp(o.crankRate / 380, 0, 1);
      const na = lerp(o.n1, Math.sin(t * 9) * 0.9, cw), nb = lerp(o.n2, Math.cos(t * 7) * 0.9, cw);
      setA(n1, 'd', `M56 215L${f1(56 + Math.sin(na) * 7)} ${f1(215 - Math.cos(na) * 7)}`);
      setA(n2, 'd', `M174 215L${f1(174 + Math.sin(nb) * 7)} ${f1(215 - Math.cos(nb) * 7)}`);
      // Zeilenraster: bei großer Kamera-Nähe (Fahrt in den Schirm) blendet es aus, sonst würden die Zeilen riesig
      setA(scan, 'opacity', f3((0.5 + 0.05 * Math.sin(t * 1.3)) * clamp((5 - (o.camZ || 1)) / 2, 0, 1)));
      // Abschalten wie eine alte Röhre: der letzte Inhalt staucht in 0.13 s zu einem Strich, der schrumpft zum Punkt
      // und verlischt (0.32 s); sonst zeigt der Schirm seinen Modus
      const offU = o.mode === 'off' && o.prevMode && o.prevMode !== 'off' ? o.sinceScreen / 0.32 : 1;
      const mode = offU < 1 ? o.prevMode : o.mode;
      setA(scr, 'fill', mode === 'red' ? '#4A1027' : (o.mode === 'off' ? '#0A1719' : C.screen));
      show(face, mode === 'on' || mode === 'glitch');
      show(load, mode === 'load'); show(err, mode === 'red'); show(boot, mode === 'boot');
      show(film, mode === 'film'); show(ans, mode === 'ansage'); show(title, mode === 'title');
      if (mode === 'title' && titleT.textContent !== o.title) titleT.textContent = o.title;
      // Röhren-Umschalten: neuer Inhalt klappt in 0.12 s aus einer Linie auf
      show(disp, offU >= 0.4);
      show(tube, offU < 1);
      if (offU < 0.4) {
        const e = ease('in', offU / 0.4);
        show(disp, true);
        setT(disp, `translate(115,128) scale(${f3(1 + 0.08 * e)},${f3(Math.max(0.02, 1 - e))}) translate(-115,-128)`);
        setA(tube, 'width', 92); setA(tube, 'x', 69); setA(tube, 'height', f2(1 + 4 * e)); setA(tube, 'y', f2(128 - (1 + 4 * e) / 2)); setA(tube, 'opacity', f2(e));
      } else if (offU < 1) {
        const w = 3 + 89 * (1 - ease('io', (offU - 0.4) / 0.4)), h = 3 + 2 * (1 - smooth((offU - 0.4) / 0.4));
        setA(tube, 'width', f2(w)); setA(tube, 'x', f2(115 - w / 2)); setA(tube, 'height', f2(h)); setA(tube, 'y', f2(128 - h / 2));
        setA(tube, 'opacity', f2(1 - smooth((offU - 0.8) / 0.2)));
      } else setT(disp, o.flip < 0.999 ? `translate(0,128) scale(1,${f3(o.flip)}) translate(0,-128)` : '');
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
        // spricht KURT dabei, pulsiert der Ring mit seiner Stimme (Punkte größer, Ring weiter)
        const ds = 7 * (1 + 0.7 * o.mo), rr = 20 + 5 * o.mo;
        for (let i = 0; i < 8; i++) {
          const a = i / 8 * Math.PI * 2;
          setA(dots[i], 'width', f2(ds)); setA(dots[i], 'height', f2(ds));
          setA(dots[i], 'x', f1(115 + Math.cos(a) * rr - ds / 2)); setA(dots[i], 'y', f1(128 + Math.sin(a) * rr - ds / 2));
          setA(dots[i], 'opacity', f2(Math.min(1, ((i - k) % 8 + 8) % 8 / 8 * 0.85 + 0.15 + 0.5 * o.mo)));
        }
      }
      // Fehler-Gesicht: Zickzack-Mund zittert; spricht eine Durchsage aus KURT, reißt er im Takt der Stimme auf
      if (mode === 'red') setT(errMouth, `translate(0,${(Math.floor(t * 8) % 2) * 2 * (1 - clamp(o.ansAmp * 3, 0, 1))}) translate(115,147) scale(${f3(1 + 0.15 * o.ansAmp)},${f3(1 + 2.4 * o.ansAmp)}) translate(-115,-147)`);
      if (mode === 'boot') { const u = clamp(o.sinceScreen / 1.2, 0, 1); setA(boot, 'width', f1(88 * u)); setA(boot, 'x', f1(115 - 44 * u)); setA(boot, 'height', f1(2 + 30 * u * u)); setA(boot, 'y', f1(128 - (1 + 15 * u * u))); }
      if (mode === 'film') {
        show(ftrain, !o.miniT); show(fcloud, !o.miniT);   // ohne Filmszene: Sinnbild (Zug, Wolke)
        if (o.miniT) setT(filmMini, o.miniT);
        else {
          const u = (t * 0.35) % 1;
          setT(ftrain, `translate(${f1(170 - u * 140)},${f1(140 + Math.sin(t * 3) * 2)})`);
          setT(fcloud, `translate(${f1(60 + ((t * 12) % 110))},100)`);
        }
      }
      if (mode === 'ansage') for (let i = 0; i < 7; i++) { const h = 6 + o.ansAmp * 40 * (0.5 + 0.5 * Math.abs(Math.sin(i * 1.7 + t * 14))); setA(bars[i], 'height', f1(h)); setA(bars[i], 'y', f1(128 - h / 2)); }
      // Dampf: jedes Wölkchen steigt zyklisch auf, aber nur, wenn beim Start seines Zyklus Dampf an war: beim
      // Einschalten kommen sie nacheinander aus dem Trichter, beim Ausschalten steigen die fliegenden zu Ende auf
      let puffOn = false;
      for (let i = 0; i < puffs.length; i++) {
        const p = t * 0.9 + i / puffs.length, n = Math.floor(p), u = p - n, on = o.steamAt((n - i / puffs.length) / 0.9);
        show(puffs[i], on); puffOn = puffOn || on;
        if (!on) continue;
        setA(puffs[i], 'cx', f1(110 + Math.sin(i * 2.3 + t) * 18 * u)); setA(puffs[i], 'cy', f1(0 - u * 120));
        setA(puffs[i], 'r', f1(8 + u * 26)); setA(puffs[i], 'opacity', f2(0.85 * (1 - u)));
      }
      show(steam, puffOn);
    }
  };
  return rig;
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
      const t = o.t, ph = o.ph || 0, wa = o.walkAmt || 0, wp = o.wp || 0, S = o.stride || 40, fl = o.fly || 0, si = o.sit || 0;
      // Wenden: Breite nie unter 40 % (dort klappt die Spiegelung um), dazu ein kleiner Hüpfer mit Strecken –
      // so liest sich das Umdrehen als Bewegung statt als Pappaufsteller (nicht im Flug und nicht im Sitzen)
      const turn = clamp(1 - Math.abs(o.face), 0, 1) * (1 - clamp(fl, 0, 1)) * (1 - si);
      let face = o.face;
      if (Math.abs(face) < 0.4) face = face < 0 ? -0.4 : 0.4;
      const hop = 16 * o.s * Math.sin(Math.PI / 2 * turn), tsy = 1 + 0.07 * turn, tsx = 1 - 0.04 * turn;
      const px0 = o.x, py0 = o.y - hop, gsx = o.s * face * (o.sx || 1) * tsx, gsy = o.s * (o.sy || 1) * tsy;
      // Wischen bei schnellem Flug: entlang der Flugrichtung strecken, um die Körpermitte, volumengleich
      const sm = o.smM > 0.01 ? `translate(0,${f1(-76 * o.s)}) rotate(${f1(o.smA)}) scale(${f3(1 + o.smM)},${f3(1 / (1 + o.smM))}) rotate(${f1(-o.smA)}) translate(0,${f1(76 * o.s)}) ` : '';
      setT(g, `translate(${f1(px0)},${f1(py0)}) ${sm}rotate(${f2(o.r || 0)}) scale(${gsx.toFixed(4)},${gsy.toFixed(4)}) translate(-110,-226)`);
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
      // Flügel: Pose (wing), Fegen, Flattern – jeweils weich überblendet
      let wr = -(o.wing || 0) * 55;
      if (o.sweepAmt) wr = lerp(wr, Math.sin(t * 6) * 14, o.sweepAmt);
      // Flattern: Schlagfrequenz je Taube; flapAmt < 1 = Gleiten mit erhobenen Flügeln (beim Sinken)
      const fHz = o.flapHz || 26, fA = o.flapAmt === undefined ? 1 : o.flapAmt;
      if (fl > 0) wr = lerp(wr, -20 - 45 * fA * (0.5 + 0.5 * Math.sin(t * fHz + ph)) - (1 - fA) * 28, fl);
      // Greifen (Kurbeln): Flügel dreht vom Schultergelenk (nach vorn verlegt) zum Ziel in Weltkoordinaten und
      // streckt sich bis dorthin, die Spitze liegt auf dem Griff. Achse des Flügels in Ruhe: 15.5°, Länge 67.
      let wing0 = `rotate(${f1(wr)},125,138)`;
      const ra = clamp(o.reachAmt || 0, 0, 1);
      if (ra > 0.001 && o.reach) {
        const M = new DOMMatrix().translateSelf(px0, py0);
        if (sm) M.translateSelf(0, -76 * o.s).rotateSelf(o.smA).scaleSelf(1 + o.smM, 1 / (1 + o.smM)).rotateSelf(-o.smA).translateSelf(0, 76 * o.s);
        M.rotateSelf(o.r || 0).scaleSelf(gsx, gsy).translateSelf(-110, -226)
          .translateSelf(0, bob).translateSelf(118, 220).rotateSelf(wad).translateSelf(-118, -220)
          .translateSelf(110, 226).scaleSelf(1 - 0.5 * b, 1 + b).translateSelf(-110, -226);
        const q = M.inverse().transformPoint(new DOMPoint(o.reach.x, o.reach.y));
        const sx0 = lerp(125, 104, ra), sy0 = lerp(138, 142, ra);   // Schulter rückt beim Greifen nach vorn
        let phi = Math.atan2(q.y - sy0, q.x - sx0) * 180 / Math.PI;
        while (phi < 60) phi += 360;   // stetig um "nach vorn" (180°), Anschwung über unten
        while (phi >= 420) phi -= 360;
        const k = clamp(Math.hypot(q.x - sx0, q.y - sy0) / 67, 0.6, 2.4), kk = lerp(1, k, ra);
        wing0 = `translate(${f2(sx0)},${f2(sy0)}) rotate(${f2(lerp(15.5 + wr, phi, ra))}) scale(${f3(kk)},${f3(clamp(1.1 - 0.2 * kk, 0.7, 1))}) rotate(-15.5) translate(-125,-138)`;
      }
      setT(wing, wing0);
      // Klemmbrett verschwindet beim Greifen unter dem Flügel (schrumpft weg), Besen wächst aus dem Flügel
      const bs = 1 - smooth(ra / 0.5);
      show(board, opt.board && bs > 0.01);
      if (opt.board) setT(board, bs < 0.999 ? `translate(168,177) scale(${f3(bs)}) translate(-168,-177)` : '');
      show(farWing, fl > 0.02);
      if (fl > 0.02) { setT(farWing, `rotate(${f1(lerp(-10, -30 + 50 * fA * Math.sin(t * fHz + ph + 0.6) - (1 - fA) * 20, fl))},126,140)`); setA(farWing, 'opacity', f2(0.85 * fl)); }
      const br = clamp(o.broom || 0, 0, 1);
      show(broom, br > 0.01);
      if (br > 0.01) setT(broom, `rotate(25,150,150) translate(150,150) scale(${f3(ease('back', br))}) translate(-150,-150)`);
      // Kopf: kurzer Ruck (0.1 s), dann stillhalten; dazu Picken, Nicken, Blick. Beim Gehen: Kopf stößt vor und bleibt in der Welt stehen.
      const q = (t + ph) / T0, k = Math.floor(q), su = (q - k) * T0;
      let hr = (o.head || 0) + (o.snap === undefined ? 7 : o.snap) * (1 - wa) * lerp(rnd(k - 1, id), rnd(k, id), smootherstep(su / 0.1));
      hr += (o.peck || 0) + (o.hr || 0);
      if (o.crankAmt) hr += Math.sin(o.crankA * Math.PI / 180) * 5 * o.crankAmt;
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

// Ideen-Knäuel; zwei Nachzieher (use) für schnellen Flug
function makeBall(parent) {
  const ghosts = [0.35, 0.18].map(() => E('use', { href: '#ballArt', opacity: 0 }, parent));
  const g = E('g', null, parent), art = E('g', { id: 'ballArt' }, g);
  E('circle', { r: 16, fill: C.him }, art);
  E('path', { d: 'M-12 -4Q0 -14 13 2M-13 5Q0 -4 10 10', fill: 'none', stroke: C.himD, 'stroke-width': 3, 'stroke-linecap': 'round' }, art);
  g._ghosts = ghosts;
  return g;
}
// Wischen ohne Filter: in Bewegungsrichtung strecken (volumengleich), Mittelpunkt (cx, cy)
function smearT(vx, vy, k, max, cx, cy) {
  const m = Math.min(max, Math.hypot(vx, vy) * k);
  if (m < 0.005) return '';
  const a = Math.atan2(vy, vx) * 57.3;
  return `translate(${f1(cx)},${f1(cy)}) rotate(${f1(a)}) scale(${f3(1 + m)},${f3(1 / (1 + m))}) rotate(${f1(-a)}) translate(${f1(-cx)},${f1(-cy)}) `;
}

// Zug (schaut nach links). Fahrwerk (Räder, Drehgestelle) und Wagenkasten getrennt: der Kasten nickt beim
// Bremsen vorn ein, federt nach dem Halt 2–3-mal nach, hockt beim Anfahren hinten ein; Schienenstöße.
function makeTrain(parent) {
  const g = E('g', null, parent);
  const speed = E('g', null, g), lines = [];
  for (let i = 0; i < 4; i++) lines.push(E('path', { stroke: C.garn, 'stroke-width': 10, 'stroke-linecap': 'round', fill: 'none' }, speed));
  const bodyG = E('g', null, g);
  const farW = E('g', null, bodyG), body = E('g', null, bodyG), nearW = E('g', null, bodyG), chassis = E('g', null, g);
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
  // Fussel schaut aus dem vordersten Fenster, sobald er eingestiegen ist (Abfahrt, Flug); Mund folgt seiner Stimme
  const fWin = E('g', null, body);
  E('circle', { cx: -560, cy: -236, r: 30, fill: C.him }, fWin);
  E('path', { d: 'M-560 -264c-4-14 10-22 20-14', fill: 'none', stroke: C.himD, 'stroke-width': 5, 'stroke-linecap': 'round' }, fWin);
  for (const [ex, er] of [[-571, 9], [-549, 7.5]]) { E('circle', { cx: ex, cy: -242, r: er, fill: '#fff' }, fWin); E('circle', { cx: ex - 2, cy: -241, r: er * 0.48, fill: C.ink }, fWin); }
  const fMouth = E('ellipse', { cx: -562, cy: -222, rx: 5, ry: 2, fill: C.ink }, fWin);
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
    const w = E('g', null, chassis);
    E('circle', { r: 38, fill: C.ink }, w);
    const sp = E('path', { d: 'M-30 0H30M0 -30V30', stroke: C.ink2, 'stroke-width': 7 }, w);
    const ring = E('circle', { r: 22, fill: 'none', stroke: C.ink2, 'stroke-width': 9, opacity: 0 }, w);   // Speichen verwischt
    E('circle', { r: 9, fill: C.taube }, w);
    wheels.push([w, x, sp, ring]);
  }
  E('rect', { x: -700, y: -70, width: 220, height: 26, rx: 8, fill: C.ink }, chassis); E('rect', { x: 480, y: -70, width: 220, height: 26, rx: 8, fill: C.ink }, chassis);
  return {
    g, body, update(o) {
      // Fahrt-Wischen: minimal in Fahrtrichtung gestreckt (um die Wagenmitte), Tempo-Striche hinter dem Heck
      const v = Math.abs(o.vx || 0), sx = 1 + v / 20000;
      setT(g, `translate(${o.x.toFixed(1)},${o.y.toFixed(1)}) rotate(${o.r.toFixed(2)}) scale(${f3(o.s * sx)},${f3(o.s)})`);
      setT(bodyG, `translate(0,${f2(o.sag || 0)}) rotate(${f3(o.pitch || 0)},0,-50)`);   // Drehpunkt auf der Drehgestell-Linie
      const dpf = v * 1.5 / 60, blur = smooth((dpf - 14) / 12);   // Grad pro Bild: ab ~20° flimmern die Speichen
      for (const [w, x, sp, ring] of wheels) {
        setT(w, `translate(${x},-38) rotate(${(-o.x * 1.5 % 360).toFixed(1)})`);
        setA(sp, 'opacity', f2(1 - blur)); setA(ring, 'opacity', f2(0.8 * blur));
      }
      const so = clamp((v - 300) / 900, 0, 0.55), tail = (o.vx || 0) < 0 ? 1 : -1;
      show(speed, so > 0.01);
      if (so > 0.01) lines.forEach((l, i) => {
        const y = [-280, -205, -125, -75][i], x0 = tail * (880 + 30 * (i % 2)), len = (0.22 + 0.08 * i) * v;
        setA(l, 'd', `M${f1(x0)} ${y}H${f1(x0 + tail * len)}`); setA(l, 'opacity', f2(so * (1 - 0.15 * i)));
      });
      for (const [l, r, x] of doors) { setA(l, 'x', (x - 58 - o.doors * 52).toFixed(1)); setA(r, 'x', (x + o.doors * 52).toFixed(1)); }
      show(farW, o.wings); show(nearW, o.wings);
      if (o.wings) {
        const fl = o.flap ? Math.sin(o.t * 7) * 28 : 0;
        setT(fw, `translate(120,-320) rotate(${(20 + fl * 0.8).toFixed(1)})`);
        setT(nw, `translate(-60,-300) rotate(${(-6 + fl).toFixed(1)})`);
      }
      // Fahrgäste: wippen; beim Bremsen rutschen die Köpfe nach vorn (links), beim Anfahren zurück
      heads.forEach((h, i) => setT(h, `translate(${f1(6 * (o.pitch || 0))},${(Math.sin(o.t * 5 + i) * 3).toFixed(1)})`));
      show(fWin, !!o.fussel);
      if (o.fussel) {
        setT(fWin, `translate(${f1(6 * (o.pitch || 0))},${(Math.sin(o.t * 5 + 7) * 3 - 6 * o.fussel.mo).toFixed(1)})`);
        setA(fMouth, 'rx', f1(5 + 4 * o.fussel.mo)); setA(fMouth, 'ry', f1(2 + 9 * o.fussel.mo));
      }
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
const BOARD = {
  leer: ['--:--  ----------', '', ''],
  kruemel: ['08:15  Krümelstadt', 'über Brösel-Allee, Taubenmarkt', 'pünktlich'],
  kruemel2: ['08:15  Krümelstadt', 'über Brösel-Allee, Taubenmarkt', 'Abfahrt bei ausreichend Krümeln'],
  einfahrt: ['08:15  Krümelstadt', 'über Brösel-Allee, Taubenmarkt', 'fährt ein · Vorsicht!'],
  abfahrt: ['08:15  Krümelstadt', 'über Brösel-Allee, Taubenmarkt', 'abgefahren · pünktlich!']
};
const FLAPS = 'ABCDEFGHIKLMNOPRSTUZ0123456789:·';

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
  H.secK = E('path', { d: 'M1615 318V270', stroke: C.him, 'stroke-width': 2.5, 'stroke-linecap': 'round' }, g);   // tickt
  E('circle', { cx: 1615, cy: 310, r: 4, fill: C.him }, g);
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
  // Lampen: pendeln an der Decke (um den Aufhängepunkt), Lichtkegel schwingt mit; Staub tanzt im Licht
  H.lamps = [300, 960, 1620].map(x => {
    const L = E('g', null, g);
    L._cone = E('path', { d: `M${x - 70} 210L${x + 70} 210L${x + 300} 700L${x - 300} 700Z`, fill: C.garn, opacity: 0.09 }, L);
    E('path', { d: `M${x} 44V150`, stroke: C.ink, 'stroke-width': 4 }, L);
    E('path', { d: `M${x - 66} 206L${x - 32} 150H${x + 32}L${x + 66} 206Z`, fill: C.pet }, L);
    E('circle', { cx: x, cy: 208, r: 16, fill: C.garn }, L);
    L._x = x; L._ang = 0;
    return L;
  });
  H.dust = E('g', null, g); H.motes = [];
  for (let k = 0; k < 3; k++) for (let j = 0; j < 6; j++) {
    const m = E('circle', { r: f1(2 + 2 * hash(k * 6 + j, 33)), fill: C.garn }, H.dust);
    m._k = k; m._j = j; m._h = [hash(k * 6 + j, 31), hash(k * 6 + j, 32), hash(k * 6 + j, 34)]; H.motes.push(m);
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
  // Logo-Fussel lebt: atmet (um die Fußlinie), blinzelt, schaut der Schrift nach und zum Knäuel, zuckt beim "Pling"
  const fus = E('g', { transform: 'translate(0 42)' }, lg);
  H.logoFus = E('g', null, fus); H.logoFus.innerHTML = L.fussel;
  const ec = H.logoFus.querySelectorAll('circle');   // Augenweiß ×2, Pupillen ×2, Glanzpunkte ×2
  H.logoEyes = [2, 3, 4, 5].map(k => { const c = ec[k]; c._x = +c.getAttribute('cx'); c._y = +c.getAttribute('cy'); return c; });
  H.logoLids = [0, 1].map(k => {
    const cx = +ec[k].getAttribute('cx'), cy = +ec[k].getAttribute('cy'), r = +ec[k].getAttribute('r'), id = 'logoLid' + k;
    E('circle', { cx, cy, r: r + 1.5 }, E('clipPath', { id }, defs));
    const lid = E('path', { fill: C.him }, E('g', { 'clip-path': `url(#${id})` }, H.logoFus));
    lid._e = [cx, cy, r];
    return lid;
  });
  // Faden beginnt ein Stück im Fell (gleiche Farbe), damit beim Atmen keine Lücke am Kopf entsteht
  H.logoThread = E('path', { d: L.thread.replace(/^M101 92/, 'M101 102L101 92'), fill: 'none', stroke: C.him, 'stroke-width': 7, 'stroke-linecap': 'round' }, lg);
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
  H.t1 = T(E('text', { id: 'ttl1', x: 960, y: 560, 'text-anchor': 'middle', 'font-family': FONT.bagel, 'font-size': 116, fill: C.ink }, g), 'Und was, wenn Tauben');
  H.t2 = T(E('text', { id: 'ttl2', x: 960, y: 690, 'text-anchor': 'middle', 'font-family': FONT.bagel, 'font-size': 116, fill: C.ink }, g), 'die Bahn übernehmen?');
  // Nachzieher beim schnellen Hereinfliegen (Kopien, nur Transform/Deckkraft ändern sich)
  H.tGhost = ['ttl1', 'ttl1', 'ttl2', 'ttl2'].map(id => { const u = E('use', { href: '#' + id, opacity: 0 }); g.insertBefore(u, H.t1); return u; });
  T(E('text', { x: 960, y: 820, 'text-anchor': 'middle', 'font-family': FONT.mono, 'font-weight': 500, 'font-size': 28, fill: C.ink, 'letter-spacing': 4 }, g), 'FORMAT: UND WAS, WENN …?');
})();

// Filmtitel = KURTs Bildschirm in Großaufnahme. Im ersten Bild deckt sich die Karte mit dem Schirm aus der
// Halle (Loch r = 43·1.6·9, Ring und Gehäuse drumherum), dann öffnet sich der Rand und die Karte zoomt nach.
(function buildFilmtitel() {
  const g = sceneGroup('filmtitel');
  E('rect', { x: 0, y: 0, width: 1920, height: 1080, fill: C.screen }, g);
  H.ftG = E('g', null, g);
  H.ftGlow = E('circle', { cx: 960, cy: 540, r: 700, fill: '#163A3E' }, H.ftG);
  H.ft1 = T(E('text', { x: 960, y: 470, 'text-anchor': 'middle', 'font-family': FONT.mono, 'font-weight': 500, 'font-size': 64, fill: C.senf, 'letter-spacing': 16 }, H.ftG), 'FILM 1');
  H.ft2 = T(E('text', { x: 960, y: 640, 'text-anchor': 'middle', 'font-family': FONT.bagel, 'font-size': 150, fill: C.senf }, H.ftG), 'Die Übernahme');
  H.ftScan = E('rect', { x: 0, y: 0, width: 1920, height: 1080, fill: 'url(#scan)', opacity: 0.6 }, g);
  E('path', { d: 'M0 0H1920V1080H0Z M960 -260A1060 860 0 1 0 960.1 -260Z', fill: C.petDD, 'fill-rule': 'evenodd', opacity: 0.9 }, g);
  H.ftHi = E('circle', { fill: '#fff' }, g);   // Glanzpunkt auf dem Glas
  H.ftRim = [C.screen, C.petDD, C.pet].map(fill => E('path', { fill, 'fill-rule': 'evenodd' }, g));
  H.ftRimFelt = E('path', { d: 'M-1000 -1000H1200V1200H-1000Z M61 128a54 54 0 1 0 108 0a54 54 0 1 0 -108 0Z', fill: 'url(#felt)', 'fill-rule': 'evenodd' }, g);
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
  for (const y of [192, 255, 302]) E('rect', { x: 130, y, width: 660, height: 2, fill: C.ink }, g);   // Fallblatt-Teilung
  // Bahnhofsuhr
  E('path', { d: 'M1020 60V96', stroke: C.ink, 'stroke-width': 5 }, g);
  E('circle', { cx: 1020, cy: 150, r: 56, fill: '#fff' }, g);
  E('circle', { cx: 1020, cy: 150, r: 56, fill: 'none', stroke: C.ink, 'stroke-width': 7 }, g);
  // Bahnhofsuhr 8:13–8:15: Sekundenzeiger läuft in 58.5 s herum, wartet oben, dann springt der Minutenzeiger
  E('path', { d: 'M1020 150V122', stroke: C.ink, 'stroke-width': 6, 'stroke-linecap': 'round', transform: 'rotate(247,1020,150)' }, g);
  H.clockMin = E('path', { d: 'M1020 150V104', stroke: C.ink, 'stroke-width': 6, 'stroke-linecap': 'round' }, g);
  H.secHand = E('g', null, g);   // roter Zeiger mit Kelle
  E('path', { d: 'M1020 162V104', stroke: C.him, 'stroke-width': 3 }, H.secHand);
  E('circle', { cx: 1020, cy: 114, r: 6, fill: C.him }, H.secHand);
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
  // Schallwellen: zwei Bögen wandern nach außen und verblassen (Stärke aus der geglätteten Durchsage)
  H.hornW = [0, 1].map(() => E('path', { d: 'M1715 175q-14 30 0 60', fill: 'none', stroke: C.him, 'stroke-width': 5, 'stroke-linecap': 'round' }, H.horn));
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
  // Aussicht: steht in der Welt still, während der Wagen schaukelt (H.outside hält dagegen)
  H.outside = E('g', null, out);
  H.outLand = E('g', null, H.outside); H.outClouds = E('g', null, H.outside);
  // Landschaft (wiederholt sich alle 1200 px)
  E('rect', { x: 0, y: 150, width: 1920, height: 400, fill: '#FFF1CF' }, H.outLand);
  H.landFar = E('g', null, H.outLand); H.landNear = E('g', null, H.outLand);
  H.outBakery = E('g', null, H.outLand);   // zwischen Hügeln und Masten: gleitet mit der Landschaft herein
  H.poles = E('g', null, H.outLand); H.poleRects = [];
  // Hügel und Feld: je ein durchgehender Pfad über alle 4 Kacheln (keine Stoßkanten); jede Kachel beginnt und endet
  // auf derselben Höhe mit waagerechter Tangente, die Wiederholung alle 1200 px ist daher nahtlos
  let far = 'M0 420', near = 'M0 448';
  for (let k = 0; k < 4; k++) {
    const x = dx => k * 1200 + dx;
    far += `C${x(120)} 420 ${x(200)} 350 ${x(330)} 352S${x(520)} 410 ${x(640)} 418S${x(880)} 470 ${x(1000)} 452S${x(1140)} 420 ${x(1200)} 420`;
    near += `C${x(90)} 448 ${x(150)} 406 ${x(260)} 408S${x(400)} 440 ${x(520)} 446S${x(760)} 476 ${x(930)} 466S${x(1110)} 448 ${x(1200)} 448`;
    // Bäume vor dem Feld gezeichnet: das Feld deckt die Stämme unten ab, sie wurzeln hinter der Kuppe
    for (const dx of [150, 520, 900]) { E('rect', { x: x(dx), y: 395, width: 10, height: 85, fill: C.woodD }, H.landNear); E('circle', { cx: x(dx) + 5, cy: 385, r: 30, fill: C.pet }, H.landNear); }
    for (const dx of [0, 600]) { const pr = E('rect', { x: x(dx), y: 180, width: 14, height: 320, fill: C.ink2 }, H.poles); pr._x = x(dx) + 7; H.poleRects.push(pr); }
  }
  E('path', { d: far + 'V520H0Z', fill: '#4F8E92' }, H.landFar);
  E('path', { d: near + 'V520H0Z', fill: C.senfD }, H.landNear);
  E('rect', { x: 0, y: 480, width: 1920, height: 40, fill: '#7C7894' }, H.outLand);
  H.outLand.appendChild(H.poles);   // Masten ganz vorn, auch vor der Bäckerei
  // Bäckerei (ein Gebäude an der Strecke, ohne eigenen Himmel; steht auf dem Boden der Landschaft)
  E('rect', { x: 560, y: 200, width: 800, height: 320, fill: C.garnD }, H.outBakery);
  for (let i = 0; i < 10; i++) E('path', { d: `M${560 + i * 80} 230h80l-10 50h-60z`, fill: i % 2 ? C.garn : C.him }, H.outBakery);
  E('rect', { x: 600, y: 300, width: 300, height: 200, rx: 10, fill: C.ink2 }, H.outBakery);
  for (let i = 0; i < 4; i++) E('ellipse', { cx: 650 + i * 66, cy: 440, rx: 28, ry: 18, fill: C.brezel }, H.outBakery);
  E('path', { d: 'M1040 340c-60-60 40-110 70-40c30-70 130-20 70 40c-30 30-110 30-140 0z', fill: 'none', stroke: C.brezel, 'stroke-width': 22 }, H.outBakery);
  T(E('text', { x: 1110, y: 470, 'text-anchor': 'middle', 'font-family': FONT.bagel, 'font-size': 52, fill: C.him }, H.outBakery), 'Bäckerei');
  E('rect', { x: 520, y: 500, width: 880, height: 22, rx: 6, fill: '#6A6684' }, H.outBakery);
  // Wolken
  E('rect', { x: 0, y: 150, width: 1920, height: 400, fill: '#BFE0DC' }, H.outClouds);
  // Wolkenreihe: Höhen wiederholen sich alle 3 Wolken (900 px), daher Umlauf modulo 900; 12 Wolken decken 1920 + 900 px
  H.cloudRow = E('g', null, H.outClouds);
  for (let k = 0; k < 12; k++) { const cx = k * 300, cy = 250 + (k % 3) * 80; for (const [dx, dy, r] of [[0, 0, 40], [40, -10, 50], [85, 5, 38], [40, 20, 36]]) E('circle', { cx: cx + dx, cy: cy + dy, r, fill: '#fff' }, H.cloudRow); }
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
  // Deckenlautsprecher für die Durchsagen
  H.speaker = E('g', null, g);
  E('circle', { cx: 1780, cy: 100, r: 22, fill: C.ink2 }, H.speaker);
  E('path', { d: 'M1768 92H1792M1765 100H1795M1768 108H1792', stroke: C.garnD, 'stroke-width': 3, 'stroke-linecap': 'round' }, H.speaker);
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
  // Wolken in drei Ebenen (fern: klein, langsam, leicht getönt; nah: groß, schnell); fern zuerst gezeichnet
  const puff = (c, fill) => { for (const [dx, dy, r] of [[0, 0, 60], [70, -25, 75], [140, 0, 58], [70, 25, 55], [-50, 15, 40]]) E('circle', { cx: dx, cy: dy, r, fill }, c); };
  H.clouds = [];
  for (const layer of [0, 1, 2]) for (let k = layer; k < 9; k += 3) {
    const c = E('g', null, g);
    puff(c, layer ? '#fff' : '#EAF5F2');
    c._k = k; c._sp = [35, 80, 160][layer]; c._sc = [0.55, 0.85, 1.2][layer]; H.clouds.push(c);
  }
  // zwei große Wolken ganz vorn, die kurz durchs Bild ziehen
  const fg = sceneGroup('himmel', fxLayer);
  H.fgClouds = [0, 1].map(k => { const c = E('g', null, fg); puff(c, '#fff'); c._k = k; return c; });
  H.swarm = E('g', null, g);
  H.brezel = E('g', { transform: 'translate(860,560)' }, H.swarm);
  E('path', { d: 'M0 0c-180-180 120-320 210-120c90-200 390-60 210 120c-90 90-330 90-420 0z', fill: 'none', stroke: C.brezel, 'stroke-width': 64, transform: 'translate(-110,-40)' }, H.brezel);
  for (let i = 0; i < 18; i++) E('rect', { x: -60 + (i * 53) % 330 - 90, y: -150 + (i * 37) % 200, width: 9, height: 6, rx: 2, fill: C.garn, transform: 'translate(-20,0)' }, H.brezel);
  H.minis = [];
  for (let i = 0; i < 6; i++) H.minis.push(makeMiniTrain(H.swarm));
  // Schild "Hauptbahnhof" ganz oben (bewegt sich mit der Brezel): vordere Züge fliegen dahinter vorbei, der Witz bleibt lesbar
  H.brezelLabel = E('g', { transform: 'translate(860,560)' }, H.swarm);
  E('rect', { x: -40, y: 170, width: 300, height: 70, rx: 8, fill: C.garn }, H.brezelLabel);
  T(E('text', { x: 110, y: 218, 'text-anchor': 'middle', 'font-family': FONT.body, 'font-weight': 800, 'font-size': 34, fill: C.pet }, H.brezelLabel), 'Hauptbahnhof');
})();

(function buildEndcard() {
  const g = sceneGroup('endcard');
  E('rect', { x: 0, y: 0, width: 1920, height: 1080, fill: C.pet }, g);
  H.endDots = E('rect', { x: -32, y: -32, width: 1984, height: 1144, fill: 'url(#dotsL)' }, g);   // driftet langsam
  E('rect', { x: 140, y: 220, width: 800, height: 450, rx: 18, fill: C.petD }, g);
  H.endFrame = E('rect', { x: 140, y: 220, width: 800, height: 450, rx: 18, fill: 'none', stroke: C.garn, 'stroke-width': 6, 'stroke-dasharray': '24 16' }, g);
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
// Jede Statistin, Gurrmann und Fussel stecken in einer Hülle ohne Transform: beim Einsteigen bekommt sie den
// Tür-Ausschnitt (#doorclip, Weltkoordinaten), damit sie hinter dem Wagenkasten in der Tür verschwinden.
for (let i = 0; i < CROWD_N; i++) {
  const wrap = E('g', null, i < 7 ? actorsBack : actorsFront);
  const p = makePigeon(wrap, { body: bodies[i % 4], wingC: i % 2 ? '#7E79A0' : C.taubeD, neck: true });
  p.wrap = wrap; crowd.push(p);
}
const kurt = makeKurt(actors);
const broesel = makePigeon(actors, { hat: 'helmet', board: true });
// Einsteigende Statisten der vorderen Ebene werden ab dem Abheben über eine Kopie (use) hinter Gurrmann und Fussel
// gezeichnet, die selbst in die Türen steigen: sie fliegen hinter ihnen in den Wagen statt über sie hinweg
const boardBack = E('g', null, actors);
crowd.forEach((p, i) => { p.g.id = 'crowdBird' + i; p.boardUse = i >= 7 ? E('use', null, boardBack) : null; });
const gurrWrap = E('g', null, actors), fusselWrap = E('g', null, actors);
const gurrmann = makePigeon(gurrWrap, { hat: 'cap', body: '#9C98B8' });
const fussel = makeFussel(fusselWrap);
// Tür-Ausschnitt: alles außerhalb des Wagenkastens plus die offenen Türspalte (pro Bild aus Zug-Lage und Türen)
const doorClip = E('clipPath', { id: 'doorclip' }, defs);
const doorClipOut = E('path', { 'clip-rule': 'evenodd' }, doorClip);
const doorClipGaps = [0, 1].map(() => E('rect', null, doorClip));
// Versand-Luke vorn: Kopie der Klappen über den Band-Fahrgästen (nur solange jemand auf dem Band fährt)
const flapsFront = E('g', null, sceneGroup('halle', actorsFront));
H.flapsF = [];
for (let i = 0; i < 5; i++) H.flapsF.push(E('rect', { x: 1768 + i * 31, y: 470, width: 27, height: 178, fill: C.taubeD, opacity: 0.9 }, flapsFront));
const sitter = makePigeon(actorsFront, { body: '#B3AFCB' });
const ballWrap = E('g', null, actorsFront), ball = makeBall(ballWrap);
// Trichter-Ausschnitt (Weltkoordinaten über die Lage des Trichters): alles oberhalb der vorderen Trichterkante.
// Wer in den Trichter fällt (Fussel, der Ideen-Knäuel), verschwindet hinter der Kante statt davor.
const funnelClipP = E('path', { d: 'M-2000 -3000H2000V10H150A40 7 0 0 1 70 10H-2000Z' }, E('clipPath', { id: 'funnelclip' }, defs));
const crumbG = E('g', null, fxLayer);
const crumbs = [];
for (let i = 0; i < 60; i++) crumbs.push(E('rect', { width: 9, height: 7, rx: 2, fill: i % 3 ? C.brezel : C.senfDD }, crumbG));
const dustG = E('g', null, fxLayer);   // Staubwölkchen bei Fussels harten Landungen
const dust = [-1, 1, 0].map(dir => { const e = E('ellipse', { fill: C.garn }, dustG); e._dir = dir; return e; });
const featherG = E('g', null, fxLayer);
const feathers = [];
for (let i = 0; i < 16; i++) feathers.push(E('ellipse', { rx: 12, ry: 5, fill: i % 3 ? C.garn : C.taube }, featherG));

// Film auf KURTs Schirm: zurück in der Halle läuft der zuletzt gezeigte Film (Bahnhof, Zug) auf seinem Schirm weiter.
// Dafür wandern die Knoten dieser Szene (Kulisse und Darsteller, keine Kopien) in filmMini, mit der letzten
// Kameraeinstellung des Films: beim Schnitt aus dem Film deckt sich die Großaufnahme des Schirms bildgenau mit dem
// letzten Filmbild, danach fährt die Kamera heraus. Jeder Knoten hat einen festen Platz daheim und im Schirm
// (Kommentar-Marken), die Lage hängt daher nur vom Bild ab, nie von der Reihenfolge des Renderns.
const MINI_NODES = [];
function miniNode(n, scene) {
  const home = document.createComment(''), slot = document.createComment('');
  n.parentNode.insertBefore(home, n.nextSibling); kurt.filmMini.appendChild(slot);
  MINI_NODES.push({ n, home, slot, scene });
}
miniNode(SC.bahnhof[0], 'bahnhof'); miniNode(SC.zug[0], 'zug'); miniNode(SC.bahnhof[1], 'bahnhof');
crowd.slice(0, 7).forEach(p => miniNode(p.wrap, null));
miniNode(gurrWrap, null); miniNode(fusselWrap, null);
crowd.slice(7).forEach(p => miniNode(p.wrap, null));
miniNode(sitter.g, null);
function placeMini(mini) {
  for (const m of MINI_NODES) {
    const want = mini && (!m.scene || m.scene === mini) ? m.slot : m.home;
    if (m.n.nextSibling !== want) want.parentNode.insertBefore(m.n, want);
  }
}
// Welche Filmszene läuft gerade auf KURTs Schirm? Nur in der Halle direkt nach Bahnhof/Zug, solange der Schirm den
// Film zeigt (spricht KURT, zeigt er sein Gesicht)
function filmMiniScene(t, scene) {
  if (scene !== 'halle' || !st('kurt', 'vis', t, 0) || st('kurt', 'screen', t, 'off') !== 'film' || kurtSpeaking(t)) return null;
  const k = sceneIdx(t), prev = k > 0 ? TL.scenes[k - 1][1] : null;
  return prev === 'bahnhof' || prev === 'zug' ? prev : null;
}

const irisPath = E('path', { fill: C.ink, 'fill-rule': 'evenodd' }, overlay);
const fadeRect = E('rect', { x: 0, y: 0, width: 1920, height: 1080, fill: '#000', opacity: 0 }, overlay);

// Positionen der Tauben je Modus. Bahnsteig [x, y, Blick (+1 = nach links)]: 0–6 stehen hinter Fussels
// Fußlinie (y < 925, Ebene actorsBack), 7–13 davor (actorsFront); links x 90–490, rechts 1350–1820, ≥ 100 px Abstand.
const PLAT_POS = [[130, 880, -1], [280, 860, 1], [430, 880, -1], [1360, 870, 1], [1510, 900, -1], [1660, 865, 1], [1820, 880, 1],
  [90, 1010, -1], [215, 965, 1], [370, 1045, -1], [490, 990, -1], [1350, 1000, 1], [1560, 1045, 1], [1760, 985, -1]];
const SEAT_POS = [[150, 770], [280, 770], [650, 770], [930, 770], [1150, 770], [1430, 770], [1700, 770]];
// Schwarm: hintere Ebene (0–6) kleiner und mit engeren Bahnen, damit sie weiter weg wirken
const CS = Array.from({ length: 14 }, (_, i) => (i < 7 ? 0.42 : 0.55) + 0.13 * hash(i, 6));
function chaosPos(i, t) {
  const a = t * (0.6 + (i % 5) * 0.12) + i * 1.7, k = CS[i] / 0.6;
  return [960 + Math.sin(a) * (520 + (i % 3) * 180) * k, 330 + (Math.sin(a * 1.7 + i) * 170 + (i % 2) * 60) * k];
}
function beltX(i) { return 560 + i * 86; }   // rechts von Fussel (x 420): die Band-Fahrgäste fahren nie durch ihn hindurch
// Fliegende Statisten weichen dem Gesicht dessen aus, der gerade spricht (weich ein-/ausgeblendet): Abstand zum
// Augenpunkt wird stetig auf mindestens ~R gedrückt, ab 1.6 R bleibt die Bahn unverändert
function avoidSpeakers(o, t) {
  for (const who of ['F', 'B', 'G']) {
    const w = talkEnv(who, t, 0.3, 0.4).e;
    if (w < 0.001) continue;
    const a = W2A[who], [hx, hy] = headPt(a, t), R = 150 * num(a, 's', t) / (a === 'fussel' ? 0.8 : 1.25), R2 = 1.6 * R;
    const dx = o.x - hx, dy = o.y - 60 * o.s - hy, r = Math.hypot(dx, dy);   // Körpermitte der Taube
    if (r >= R2 || r < 1e-6) continue;
    const g = r + (R2 - r) * (R2 - r) / (R2 * R2) * R, k = lerp(r, g, w) / r - 1;
    o.x += dx * k; o.y += dy * k;
  }
}
// sin²-Buckel zwischen a und b (0 außerhalb)
function hump(u, a, b) { const x = Math.sin(Math.PI * clamp((u - a) / (b - a), 0, 1)); return x * x; }

// Leerlauf der Bahnsteig-Tauben: je Taube Ereignisse im Abstand P (2.0–4.2 s): Doppelpicken, Umschauen,
// Gefieder schütteln, Umdrehen mit einem Schritt. Blickrichtung und Versatz nach jedem Ereignis vorab (init).
let IDLE = [];
function buildIdle() {
  IDLE = PLAT_POS.map(([, , f], i) => {
    const P = 2.0 + 2.2 * hash(i, 11), phi = P * hash(i, 12), n = Math.ceil((TL.total + phi) / P) + 2;
    const type = [], face = [], dx = [];
    let fc = f, d = 0;
    for (let k = 0; k < n; k++) {
      type.push(Math.floor(hash(i, k + 0.5) * 5)); face.push(fc); dx.push(d);
      if (type[k] === 4) { fc = -fc; d = clamp(d - 18 * fc, -40, 40); }
    }
    return { P, phi, type, face, dx };
  });
}
function platIdle(i, t) {
  const I = IDLE[i], q = (t + I.phi) / I.P, k = clamp(Math.floor(q), 0, I.type.length - 2), u = (q - k) * I.P;
  const ty = I.type[k], f0 = I.face[k], o = { face: f0, dx: I.dx[k], peck: 0, head: 0, wing: 0, sy: 1, walk: 0, wp: 0 };
  if (ty <= 1) o.peck = -30 * (hump(u, 0, 0.32) + hump(u, 0.38, 0.66));
  else if (ty === 2) o.head = (hash(i, k + 0.25) < 0.5 ? -1 : 1) * 14 * Math.sin(Math.PI * clamp(u / 1.2, 0, 1));
  else if (ty === 3) { const h = hump(u, 0, 0.45); o.wing = 0.35 * h; o.sy = 1 + 0.05 * h; }
  else {   // umdrehen: Blick läuft über die Stauchung auf die andere Seite, dann ein Doppelschritt
    o.face = f0 * Math.cos(Math.PI * smooth(u / 0.22));
    const w = clamp((u - 0.15) / 0.5, 0, 1);
    o.dx = lerp(I.dx[k], I.dx[k + 1], smooth(w)); o.walk = hump(u, 0.12, 0.72); o.wp = w;
  }
  return o;
}
// Moduswechsel der Statisten als Kette {mode, t0, prev}; nur echte Wechsel zählen
let CREC = [];
function buildCrowdModes() {
  const L = (TL.states.crowd && TL.states.crowd.mode) || [];
  let cur = { mode: 'off', t0: -1e9, prev: null };
  CREC = [cur];
  for (const [t0, m] of L) if (m !== cur.mode) { cur = { mode: m, t0, prev: cur }; CREC.push(cur); }
}
function crowdRec(t) { return CREC[Math.max(0, lastLE(CREC, t + 1e-6, r => r.t0))]; }
const FAM = m => (m === 'platform' || m === 'look' || m === 'board') ? 1 : (m === 'seats' || m === 'window' || m === 'loud') ? 2 : 0;

// Pose einer Statisten-Taube unter einem Modus (ohne Überblendung). face: +1 schaut nach links.
function crowdPose(i, t, rec, noVel) {
  const mode = rec.mode, m0 = rec.t0, u = t - m0, prevMode = rec.prev ? rec.prev.mode : 'off';
  const o = { x: 0, y: 0, s: 0.75, face: 1, r: 0, head: 0, lid: 0.25, open: 0, fly: 0, sit: 0, peck: 0, wing: 0, sy: 1,
    walkAmt: 0, wp: 0, vis: true, flapAmt: 1, smA: 0, smM: 0, board: false };
  if (FAM(mode) === 1) {
    const [x, y] = PLAT_POS[i], id = platIdle(i, t);
    Object.assign(o, { x: x + id.dx, y, s: 0.62 + (y - 900) / 900, face: id.face, peck: id.peck, head: id.head, wing: id.wing, sy: id.sy, walkAmt: id.walk, wp: id.wp });
    // Krümel entdeckt: gestaffelt hindrehen (über die Stauchung), Kopf runter, ein paar Schritte hin, picken
    const L = mode === 'look' ? rec : (mode === 'board' && prevMode === 'look' ? rec.prev : null);
    if (L) {
      const d = 0.04 * i + 0.12 * hash(i, 3), ul = t - L.t0 - d, v = smooth(ul / 0.25), fl = x < 650 ? -1 : 1;
      o.face = lerp(o.face, fl, v); o.head = lerp(o.head, -14, v); o.lid = lerp(0.25, 0.05, v);
      const go = clamp(1 - Math.abs(x - 650) / 1100, 0.15, 1), w = smooth((ul - 0.5) / 1.1);
      o.x = lerp(o.x, o.x + (650 - x) * 0.14 * go, w);
      o.walkAmt = lerp(o.walkAmt, hump(ul, 0.45, 1.7), v); o.wp = lerp(o.wp, clamp((ul - 0.5) / 1.1, 0, 1) * 1.5, v);
      const pk = -30 * hump(((ul - 1.8) * (1.1 + 0.4 * hash(i, 4))) % 1, 0, 0.3);
      o.peck = lerp(o.peck, ul > 1.8 ? pk : 0, v);
    }
    if (mode === 'board') {   // einsteigen: im Bogen bis vor die Mitte der nächsten Tür, dann darin kleiner werden
      const d = 0.07 * i + 0.2 * hash(i, 21), uu = clamp((u - d) / 1.4, 0, 1);
      if (uu > 0) {   // Start und Ankunft mit Tempo 0 (io), Kopf/Picken blenden weich aus
        const s0 = crowdPose(i, m0 + d, rec.prev, true), left = PLAT_POS[i][0] < 960, w = smooth(uu / 0.15);
        const ua = clamp(uu / 0.78, 0, 1), e = ease('io', ua), ui = clamp((uu - 0.78) / 0.22, 0, 1);
        const tx = num('train', 'x', t) + (left ? -280 : 280) * num('train', 's', t), ty = 640;
        o.x = lerp(s0.x, tx, e); o.y = lerp(s0.y, ty, e) - 160 * Math.sin(Math.PI * e) - 20 * ui;
        o.fly = smooth(uu / 0.08); o.s = s0.s * lerp(1, 0.8, e) * (1 - ease('in', ui));
        o.peck = lerp(s0.peck, 0, w); o.head = lerp(s0.head, 0, w); o.walkAmt = lerp(s0.walkAmt, 0, w); o.face = s0.face;
        o.dir = tx > s0.x ? 1 : -1; o.boarding = true;
        // Tür-Ausschnitt erst, wenn die Taube ganz in der Türöffnung schwebt (sie ist dort schmaler als der Spalt)
        o.board = uu >= 0.78;
        if (uu >= 1) o.vis = false;
      }
    }
  } else if (FAM(mode) === 2) {
    if (i >= SEAT_POS.length) o.vis = false;
    else {
      const [x, y] = SEAT_POS[i]; o.x = x; o.y = y; o.sit = 1; o.s = 0.72; o.face = i % 2 ? 1 : -1;
      if (mode === 'window') { o.head = 16; o.lid = 0; o.face = -1; o.r = -6; }
      if (mode === 'loud') { o.open = 0.5 + 0.5 * Math.abs(Math.sin(t * 9 + i)); o.head = Math.sin(t * 10 + i) * 10; o.y -= Math.abs(Math.sin(t * 8 + i)) * 10; }
    }
  } else if (mode === 'burst' || mode === 'chaos' || mode === 'clock' || mode === 'tobelt' || mode === 'belt') {
    o.s = CS[i]; o.fly = 1;
    let dflt = 0;   // Blickrichtung, wenn die Taube steht (0 = nur aus dem Tempo)
    if (mode === 'burst') {   // aus KURTs Schirm, gestaffelt
      const d = 0.045 * i, uu = clamp((u - d) / 1.2, 0, 1), [cx, cy] = chaosPos(i, t);
      if (u < d) o.vis = false;
      o.x = lerp(860, cx, ease('out', uu)); o.y = lerp(686, cy, ease('out', uu)); o.s = lerp(0.1, CS[i], ease('out', uu));
    } else if (mode === 'chaos' || (mode === 'clock' && i % 3)) {
      [o.x, o.y] = chaosPos(i, t);
      if (mode === 'chaos' && prevMode === 'clock' && i % 3 === 0 && u < 1) {   // von der Uhr zurück in den Schwarm, ohne Sprung
        const w = ease('io', u); o.x = lerp(1660 + (i % 4) * 30, o.x, w); o.y = lerp(300 + (i % 3) * 50, o.y, w);
      }
    } else if (mode === 'clock') {
      const tx = 1660 + (i % 4) * 30, ty = 300 + (i % 3) * 50, [sx, sy] = chaosPos(i, m0), uu = clamp(u / 1.0, 0, 1);
      o.x = lerp(sx, tx, ease('io', uu)); o.y = lerp(sy, ty, ease('io', uu)); dflt = -1;
      o.fly = 1 - smooth((uu - 0.85) / 0.15);
      if (uu >= 1) o.peck = -26 * hump((t * 2.2 + 0.37 * i) % 1, 0, 0.45);   // an der Stempeluhr: Karten fressen
    } else {
      const tx = beltX(i), ty = 608;
      dflt = -1;
      if (mode === 'tobelt') {   // fliegen weiter im Schwarm, bis sie (gestaffelt) zum Band abdrehen
        const d = 0.04 * i, uu = clamp((u - d) / 1.2, 0, 1), [sx, sy] = chaosPos(i, Math.min(t, m0 + d));
        o.x = lerp(sx, tx, ease('io', uu)); o.y = lerp(sy, ty, ease('io', uu)); o.s = lerp(CS[i], 0.6, uu);
        o.fly = 1 - smooth((uu - 0.85) / 0.15);
      } else {
        o.fly = 0; o.x = tx + (integ('belt', t) - integ('belt', m0)); o.y = ty; o.s = 0.6;
        if (o.x > 1930) o.vis = false;   // erst hinter den Klappen der Versand-Luke ausblenden
        o.head = Math.sin(t * 3 + i) * 5;
      }
    }
    if (mode !== 'belt' && st('fussel', 'vis', t, 0)) avoidSpeakers(o, t);
    if (!noVel) {   // Tempo: Blickrichtung (stetiges Wenden), Steigen/Sinken (Neigung), Flügelschlag, Wischen
      const h = 1 / 120, p1 = crowdPose(i, t - h, rec, true), p2 = crowdPose(i, t + h, rec, true);
      const vx = (p2.x - p1.x) / (2 * h), vy = (p2.y - p1.y) / (2 * h), fv = -Math.tanh(vx / 120);
      o.face = dflt ? lerp(dflt, fv, clamp(Math.abs(vx) / 120, 0, 1)) : fv;
      // Neigung mit dem stetigen Blickwert gewichtet: beim Wenden (face ≈ 0) waagerecht, kein Vorzeichensprung
      o.r = -clamp(Math.atan2(vy, Math.abs(vx) + 40) * 57.3 * 0.55, -24, 24) * clamp(o.face * 1.5, -1, 1) * o.fly;
      o.flapAmt = clamp(0.35 - vy / 260, 0.25, 1);
      const sp = Math.hypot(vx, vy);
      o.smM = Math.min(0.22, sp / 4000) * o.fly; o.smA = Math.atan2(vy, vx) * 57.3;
    }
  } else o.vis = false;
  if (mode === 'board' && !noVel && o.fly > 0) {   // Einsteiger: Blick in Flugrichtung (auch im Schweben vor der Tür), Neigung aus der Bahn
    const h = 1 / 120, p1 = crowdPose(i, t - h, rec, true), p2 = crowdPose(i, t + h, rec, true);
    const vx = (p2.x - p1.x) / (2 * h), vy = (p2.y - p1.y) / (2 * h);
    o.face = lerp(o.face, -(o.dir || 1) * Math.max(0.8, Math.abs(Math.tanh(vx / 120))), o.fly);
    o.r = -clamp(Math.atan2(vy, Math.abs(vx) + 40) * 57.3 * 0.55, -24, 24) * clamp(o.face * 1.5, -1, 1) * o.fly;
    o.flapAmt = clamp(0.35 - vy / 260, 0.25, 1);
  }
  return o;
}

function updateCrowd(t, scene, rec0) {
  const rec = rec0 || crowdRec(t), mode = rec.mode, u = t - rec.t0, prevMode = rec.prev ? rec.prev.mode : 'off';
  const blendIn = FAM(mode) === 2 && FAM(prevMode) === 2;
  const hide = scene === 'logo' || scene === 'titel' || scene === 'filmtitel' || scene === 'endcard' || scene === 'himmel' ||
    (FAM(mode) === 2 && scene !== 'zug') || (FAM(mode) === 0 && scene !== 'halle');
  // Durchsage: Statisten gurren das "Gurr." am Anfang und Ende mit; Gong: alle schauen hoch
  const ann = scene === 'bahnhof' || scene === 'zug' ? lineAt('A', t) : null;
  const tGong = since('gong', t), tGurr = Math.min(since('gurren', t), since('gurren_laut', t) + 0.0);
  const listen = scene === 'bahnhof' || scene === 'zug';
  for (let i = 0; i < CROWD_N; i++) {
    const p = crowd[i];
    const o = crowdPose(i, t, rec);
    if (blendIn) {   // im Zug: Moduswechsel gestaffelt, jede Taube 0.035 s später, 0.2 s weich
      const ui = smooth((u - i * 0.035) / 0.2);
      if (ui < 1) {
        const q = crowdPose(i, t, rec.prev);
        for (const k of ['face', 'head', 'r', 'lid', 'open', 'y', 'peck']) o[k] = lerp(q[k], o[k], ui);
      }
    }
    const vis = o.vis && !hide, viaUse = vis && o.boarding && p.boardUse;   // ab dem Abheben hinter den Figuren
    show(p.g, vis);
    show(p.wrap, !viaUse);
    setA(p.wrap, 'clip-path', vis && o.board && !viaUse ? 'url(#doorclip)' : 'none');
    if (p.boardUse) {
      setA(p.boardUse, 'href', viaUse ? '#crowdBird' + i : '');
      setA(p.boardUse, 'clip-path', viaUse && o.board ? 'url(#doorclip)' : 'none');
      show(p.boardUse, !!viaUse);
    }
    if (!vis) continue;
    if (scene === 'zug' && FAM(mode) === 2) { const rd = ride(o.x, t, 0.4, 1); o.y += rd.dy; o.r += rd.dr; o.head += 0.6 * rd.dy; }
    const ph = i * 1.3;
    let open = o.open;
    if (ann && !ann.fx) {
      const w = 1 - smooth((t - ann.t0 - 0.45) / 0.15) + smooth((t - ann.t1 + 0.65) / 0.15);
      if (w > 0.01) open = Math.max(open, 0.5 * clamp(w, 0, 1) * mouth('A', t - 0.05 - (i % 4) * 0.03).o);
    }
    if (tGurr < 2.6) open = Math.max(open, 0.55 * Math.pow(Math.max(0, Math.sin(t * 13 + i * 2.1)), 2) * (1 - smooth((tGurr - 2.0) / 0.5)));
    const look = tGong < 2 ? smooth((tGong - i * 0.04) / 0.2) * (1 - smooth((tGong - 1.3 - i * 0.04) / 0.4)) : 0;
    const hear = listen ? annW(t - 0.05 * i) : 0;   // Durchsage: Kopf hoch zum Lautsprecher
    const settled = 1 - o.fly;
    const flapHz = 20 + 9 * hash(i, 5);
    p.update({
      x: o.x, y: o.y - 5 * o.flapAmt * Math.sin(t * flapHz + ph + 1.2) * o.fly, s: o.s, face: o.face, r: o.r, t, ph,
      breath: 0.018 * Math.sin(2 * Math.PI * t / 3.1 + ph), period: 3.1, sy: o.sy * (1 + 0.015 * Math.sin(2.4 * t + i)),
      head: o.head + (4 * Math.sin(2 * Math.PI * (0.2 + 0.3 * hash(i, 7)) * t + 6.28 * hash(i, 8)) + 12 * look + 8 * hear) * settled,
      snap: 5, peck: o.peck, open, puff: open, lid: o.lid, blink: blinkClosure('crowd' + i, t),
      px: -2, py: -2 * Math.max(look, hear), fly: o.fly, flapHz, flapAmt: o.flapAmt, sit: o.sit, wing: o.wing,
      walkAmt: o.walkAmt, wp: o.wp, stride: 36, smA: o.smA, smM: o.smM
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
  const ql = lineAt('F', t, 0, 0.4), [scn] = sceneAt(t), hear = scn === 'bahnhof' || scn === 'zug' ? annW(t) : 0;   // lauscht der Durchsage
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
    eyeScale: 1 + 0.17 * e.wide + 0.04 * P.p + pop, raise: e.raise + 0.5 * P.p + 0.6 * qa + spk + 0.35 * hear, tilt: e.tilt,
    mo: lerp(e.mo, mt.o, k), mw: lerp(e.mw, mt.w, k), ms: mt.s * k, smile: lerp(e.smile, 0.15, k)
  };
}

// Brösel und Gurrmann: Atmen, Blick, Sprech-Gesten, Gehen, Reaktionen
function posePigeon(name, who, t, scene) {
  const P = pulse(who, t), en = integ('en_' + who, t), mt = mouth(who, t), nod = listenNod(who, t);
  const face = -clamp(num(name, 'flip', t) * 3, -1, 1), fs = face < 0 ? -1 : 1;   // Wenden über ~40 % der Drehung
  const wa = stSmooth(name, 'walk', t, 0.15), vL = integ('vL_' + name, t), sq = integ('squash_' + name, t);
  const ex = mt.l && mt.l.ex ? 1 : 0;
  const o = {
    x: name === 'gurrmann' ? gurrX(t) : num(name, 'x', t), y: num(name, 'y', t), s: num(name, 's', t), face, t,
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
    const te = talkEnv(who, t, 0.35, 0.5);   // Klemmbrett hebt sich beim Reden, bei Ausrufen mehr
    o.wing = Math.min(1.15, o.wing + (te.l && te.l.ex ? 0.4 : 0.12) * te.e);
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
    if (scene === 'bahnhof' || scene === 'zug') o.hr += 6 * Math.sin(2.2 * t) * annW(t);   // nickt zur Durchsage
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
    // beim Schnitt zurück in die Halle läuft der Film schon (kein Aufklappen im ersten Bild)
    flip: sb.cur === 'film' && Math.abs(sw - sceneAt(t)[1]) < 1e-3 ? 1 : 0.04 + 0.96 * easeOut((t - sw) / 0.12),
    mo: mt.o, mw: mt.w, ms: mt.s, ansAmp: mouth('A', t, 'kurt').o, pulse: P.p,
    blink: blinkClosure('kurt', t), lx, ly,
    squint: sb.cur === 'on' && sb.prev === 'boot' ? env3(sb.tau, 0.15, 0.9, 0.3) : 0,
    n1: -0.6 + 0.12 * Math.sin(0.7 * t) + 1.7 * integ('needle', t), n2: 2.3 + 0.1 * Math.sin(0.53 * t + 1) - 0.9 * others,
    funnelR: 1.5 * P.sp, funnelSq: tpl < 1 ? 1 - 0.15 * Math.exp(-7 * tpl) * Math.cos(20 * tpl) * smooth(tpl / 0.03) : 1,
    steamAt: tt => !!st('kurt', 'steam', tt, 0), prevMode: sb.prev, title: 'FILM ' + st('filmtitel', 'nr', t, 1), camZ: 1
  };
}

function updateCrumbs(t, scene, fx, fy) {
  let k = 0;
  const put = (x, y, r) => { if (k >= crumbs.length) return; const c = crumbs[k++]; show(c, true); setT(c, `translate(${x.toFixed(1)},${y.toFixed(1)}) rotate(${r.toFixed(0)})`); };
  if (st('crumbs', 'fussel', t, 0) && (scene === 'bahnhof' || scene === 'zug')) {
    const c0 = stT('crumbs', 'fussel', t), u = t - c0;
    fx = num('fussel', 'x', c0); fy = num('fussel', 'y', c0);   // Krümel bleiben liegen, wo sie herausgeschüttelt wurden
    const n = scene === 'zug' ? 1 : 12;
    const floor = scene === 'zug' ? 815 : fy + 10;
    for (let i = 0; i < n; i++) {
      const tt = clamp(u - 0.3 - i * 0.05, 0, 9);
      const vx = rnd(i, 3) * 160, y0 = fy - 80, fl = floor - (i % 4) * 4;
      // fällt, springt am Boden einmal kurz auf und bleibt liegen
      const tl = (-260 + Math.sqrt(260 * 260 + 2400 * Math.max(0, fl - y0))) / 1200, tau = tt - tl;
      const y = tau < 0 ? y0 + 260 * tt + 600 * tt * tt : fl - 18 * Math.abs(Math.sin(9 * tau)) * Math.exp(-8 * tau) * (tau < 0.7 ? 1 : 0);
      put(fx + vx * Math.min(tt, 0.6), y, i * 40 + Math.min(tt, tl + 0.35) * 300);
    }
  }
  // Fontäne aus dem Trichter: jeder Krümel fliegt zyklisch; ein Zyklus findet nur statt, wenn er beim Abschuss lief,
  // nach dem Abschalten fliegen die schon fliegenden also zu Ende (nichts verschwindet in der Luft)
  const fk = lastLE(FOUNT, t, f => f[0]);
  if (fk >= 0 && scene === 'halle' && t < FOUNT[fk][1] + 2) {
    const [f0, f1] = FOUNT[fk], u = t - f0;
    for (let i = 0; i < 24; i++) {
      const p = u * 0.9 + i / 24, n = Math.floor(p / 1.6), tt = p - n * 1.6, launch = f0 + (n * 1.6 - i / 24) / 0.9;
      if (launch < f0 || launch > f1) continue;
      const ang = -Math.PI / 2 + rnd(i, 8) * 1.1;
      const v = 700 + hash(i, 2) * 300;
      put(852 + Math.cos(ang) * v * tt, 500 + Math.sin(ang) * v * tt + 900 * tt * tt, i * 30 + tt * 500);
    }
  }
  // Krümel am Boden: sammeln sich nach der Explosion nach und nach an (jeder fällt mit kleinem Hüpfer auf), ab dem
  // Fegen (Zustand floor) schiebt der Besen sie der Nähe nach zusammen, bis keiner mehr liegt
  if (BURST.length && scene === 'halle' && t > BURST[0]) {
    const L = (TL.states.crumbs && TL.states.crumbs.floor) || [], on = L.find(e => e[1]), off = on && L.find(e => !e[1] && e[0] > on[0]);
    const tS = on ? on[0] : 1e9, tE = off ? off[0] : 1e9;
    for (let i = 0; i < 30; i++) {
      const x = 700 + hash(i, 4) * 700, y = 905 + hash(i, 5) * 60, ta = BURST[0] + 1.2 + i * 0.5 + 0.3 * hash(i, 6);
      const rank = Math.abs(x - 1000) / 700 * 29, tr = tS + 0.5 + rank * 0.38;   // fern zuletzt
      const ua = t - ta, ur = (t - Math.min(tr, tE)) / 0.35;
      if (ua < 0 || ur >= 1) continue;
      const drop = ua < 0.25 ? -40 * (1 - ua / 0.25) * (1 - ua / 0.25) : -8 * Math.exp(-10 * (ua - 0.25)) * Math.abs(Math.sin(12 * (ua - 0.25)));
      const sw = smooth(ur);   // weggefegt: rutscht zum Besen und wird kleiner
      if (k >= crumbs.length) break;
      const c = crumbs[k];
      put(lerp(x, 1000, 0.5 * sw), y + drop, i * 37);
      if (sw > 0) setT(c, `${c._t} scale(${f3(1 - sw)})`);
    }
  }
  for (; k < crumbs.length; k++) show(crumbs[k], false);
}

// Fussel auf der Endcard: glücklich, atmet, blinzelt, schaut zu Brösel, wenn der spricht
// u = Zeit seit Beginn der Endcard: alle 2.4 s ein Hüpfer im Kreis (Ausholen, Bogen, Landung mit Stauchen)
function poseEndFussel(t, u) {
  const lb = 0.6 * clamp(integ('en_B', t) * 3, 0, 1);
  const p = (u + 1.2) % 2.4, hop = Math.max(0, Math.sin(Math.PI * clamp(p / 0.6, 0, 1))), land = hump(p, 0.58, 0.78), crouch = hump(p, 2.22, 2.42);
  const sq = 0.12 * land + 0.08 * crouch;
  return {
    x: 1180, y: 540 - 40 * hop, s: 1.15, r: Math.sin(t * 2) * 3 + 1.5 * Math.sin(2 * Math.PI * t / 5.3), face: 1, fsx: 1 + sq, fsy: 1 - sq + 0.06 * hop, m: 0, ang: 0, t,
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
  // Film auf KURTs Schirm: Darsteller und Kulissen dieser Szene spielen dort weiter (ascene = Szene der Darsteller),
  // mit ihrem Sichtbarkeits- und Statistenstand vom Ende des Films
  const mini = filmMiniScene(t, scene), ascene = mini || scene, tcut = s0 - 1e-3;
  placeMini(mini);
  const visA = a => mini ? !!st(a, 'vis', tcut, 0) : actorVis(a, t, scene);
  for (const n in SC) for (const g of SC[n]) show(g, n === scene || n === mini);

  // Kamera (+ im Zug: der Wagen schaukelt in der Welt, die Aussicht hält dagegen)
  const cam = camera(t), rkY = scene === 'zug' ? integ('rockY', t) : 0, rkR = scene === 'zug' ? integ('rockR', t) : 0;
  setT(world, `translate(${f2(960 + cam.dx)},${f2(540 + cam.dy)}) rotate(${f3(cam.cr)}) scale(${cam.cz.toFixed(4)}) translate(${f2(-cam.cx)},${f2(-cam.cy)})` +
    (scene === 'zug' ? ` translate(0,${f2(rkY)}) rotate(${f3(rkR)},960,1000)` : ''));

  const stage = !['logo', 'titel', 'filmtitel'].includes(scene);
  show(actors, stage); show(actorsBack, stage); show(actorsFront, stage); show(trainLayer, stage); show(fxLayer, stage);

  // Fussel
  const fv = visA('fussel');
  show(fussel.g, fv);
  const fx = num('fussel', 'x', t), fy = num('fussel', 'y', t);
  let fo = null;
  if (fv) {
    fo = poseFussel(t);
    if (ascene === 'zug') { const rd = ride(fo.x, t, 0.4, 1); fo.y += rd.dy; fo.r += rd.dr; }
    fussel.update(fo);
  }
  // Staub: drei Wölkchen quellen an den Füßen auf und verblassen (0.35 s), Größe nach Aufprall-Tempo
  const kl = lastLE(JUMP.down, t, j => j.t), dl = kl >= 0 ? t - JUMP.down[kl].t : 1e9;
  const dOn = fv && dl < 0.35 && JUMP.down[kl].v > 700 && !st('fussel', 'funnel', t, 0);   // nicht im Trichter
  show(dustG, dOn);
  if (dOn) {
    const u = dl / 0.35, e = easeOut(u), k = num('fussel', 's', t) / 0.8 * clamp(JUMP.down[kl].v / 2000, 0.5, 1.1);
    for (const d of dust) {
      const r = (4 + 22 * e) * k * (d._dir ? 1 : 0.8);
      setA(d, 'cx', f1(fx + d._dir * (20 + 46 * e) * k)); setA(d, 'cy', f1(fy - (4 + (d._dir ? 8 : 14) * e) * k));
      setA(d, 'rx', f1(r)); setA(d, 'ry', f1(r * 0.62)); setA(d, 'opacity', f2(0.55 * (1 - u) * smooth(dl / 0.03)));
    }
  }
  // KURT
  const kv = actorVis('kurt', t, scene);
  show(kurt.g, kv);
  if (kv) {
    const ko = poseKurt(t); ko.camZ = cam.cz;
    if (mini) {   // letzte Kameraeinstellung des Films, verkleinert auf den Schirm (Großaufnahme beim Schnitt: 14.4-fach)
      const c = camera(tcut);
      ko.miniT = `translate(115,128) scale(${(1 / 14.4).toFixed(6)}) translate(${f2(c.dx)},${f2(c.dy)}) rotate(${f3(c.cr)}) scale(${c.cz.toFixed(4)}) translate(${f2(-c.cx)},${f2(-c.cy)})` +
        (mini === 'zug' ? ` translate(0,${f2(integ('rockY', tcut))}) rotate(${f3(integ('rockR', tcut))},960,1000)` : '');
    }
    kurt.update(ko);
  }
  // Brösel
  const bv = actorVis('broesel', t, scene);
  show(broesel.g, bv);
  if (bv) {
    const o = posePigeon('broesel', 'B', t, scene);
    const inHalle = scene === 'halle', cA = integ('crank', t), crankAmt = inHalle && kv ? stSmooth('broesel', 'crank', t, 0.3) : 0;
    // Kurbeln: der Flügel greift den Griff (Weltposition aus KURTs Rig), der Körper geht ein Stück mit
    const hw = kurt.handleW;
    if (crankAmt > 0 && hw) {
      const ks = num('kurt', 's', t);   // Kurbel-Drehpunkt (200,128) in KURTs Koordinaten
      o.x += crankAmt * 0.5 * (hw.x - (num('kurt', 'x', t) + 85 * ks)); o.y += crankAmt * 0.3 * (hw.y - (num('kurt', 'y', t) - 134 * ks));
    }
    o.y -= crankAmt * Math.abs(Math.sin(cA * Math.PI / 180)) * 4;   // wippt beim Kurbeln mit
    Object.assign(o, { crankAmt, crankA: cA, reach: hw, reachAmt: crankAmt, broom: stSmooth('broesel', 'broom', t, 0.3), sweepAmt: stSmooth('broesel', 'sweep', t, 0.25) });
    broesel.update(o);
  }
  // Gurrmann
  const gv = visA('gurrmann') && gurrX(t) < 1990;   // auf dem Band: erst hinter der Luke weg
  show(gurrmann.g, gv);
  if (gv) {
    const o = posePigeon('gurrmann', 'G', t, scene);
    const fly = stSmooth('gurrmann', 'fly', t, 0.2);
    // Fliegen: abheben ohne Sprung, Körper wippt im Flügelschlag, Schräglage beim Sinken/Steigen
    o.y -= stSmooth('gurrmann', 'fly', t, 0.3) * 30 + fly * 6 * Math.sin(t * 26 + 1.1 + Math.PI / 2);
    o.r -= clamp(numV('gurrmann', 'y', t) * 0.015, -18, 18) * (o.face < 0 ? -1 : 1) * fly;
    o.fly = fly;
    if (ascene === 'zug') { const rd = ride(o.x, t, 0.25, 1.4); o.y += rd.dy; o.r += rd.dr; }   // steht im Gang: schwankt mehr
    gurrmann.update(o);
  }
  // Taube auf Fussels Kopf: fliegt im Bogen an, landet mit kleinem Stauchen, reitet auf seinem Atem mit
  const sOn = st('sitter', 'on', t, 0) && ascene === 'zug' && fv;
  show(sitter.g, sOn);
  if (sOn) {
    // fliegt von rechts oben außerhalb des Bildes an (1 s), landet mit kleinem Stauchen
    const tau = t - stT('sitter', 'on', t), u = clamp(tau / 1.0, 0, 1), fs = num('fussel', 's', t);
    const hx = fo.x + 6, hy = fo.y - fo.lift * fs - (150 + 130 * (fo.bsy - 1)) * fs;
    const xl = tau - 1.0, q = xl > 0 ? 0.15 * Math.exp(-7 * xl) * Math.sin(25 * xl) : 0;
    const fl = 1 - smooth((u - 0.8) / 0.2);
    sitter.update({
      x: lerp(2100, hx, ease('out', u)), y: lerp(120, hy, ease('io', u)) - 70 * Math.sin(Math.PI * u) + fl * 6 * Math.sin(t * 26 + 2 + Math.PI / 2),
      s: 0.55, face: 1, t, ph: 2, fly: fl, sit: 1 - fl, sx: 1 + 0.6 * q, sy: 1 - q, r: -10 * fl * (1 - u),
      breath: 0.018 * Math.sin(2 * Math.PI * t / 3.1 + 2), lid: 0.6, blink: blinkClosure('sitter', t), wing: 0, open: 0, px: -1, snap: 5
    });
  }
  // Ball (Idee)
  // Knäuel wächst an der Fadenspitze (Zustand 'tip'): dort festgehalten, nach dem Abwurf blendet der Versatz
  // zwischen Spitze und Schlüsselbahn in 0.25 s aus; im Sinkflug in den Trichter hinter der Kante ausgeschnitten
  const balv = st('ball', 'vis', t, 0) && scene === 'halle';
  show(ball, balv);
  const tipOn = st('ball', 'tip', t, 0), ballFunnel = balv && kv && !tipOn && numV('ball', 'y', t) > 0;
  if (balv) {
    let bx = num('ball', 'x', t), by = num('ball', 'y', t);
    const vx = numV('ball', 'x', t), vy = numV('ball', 'y', t), sp = Math.hypot(vx, vy);
    const tw = tipOn ? 1 : 1 - smooth((t - stT('ball', 'tip', t)) / 0.25), tp = tw > 0 && fv ? fussel.tipIn(world) : null;
    if (tp) { const t0 = tipOn ? t : stT('ball', 'tip', t); bx += tw * (tp.x - num('ball', 'x', t0)); by += tw * (tp.y - num('ball', 'y', t0)); }
    setT(ball, `${smearT(vx, vy, 1 / 2500, 0.45, bx, by)}translate(${f1(bx)},${f1(by)}) rotate(${(t * 400 % 360).toFixed(1)}) scale(${f3(num('ball', 's', t))})`);
    ball._ghosts.forEach((gh, j) => {
      const on = sp > 600, d = (j + 1) / 120;
      show(gh, on);
      if (on) { setT(gh, `translate(${f1(num('ball', 'x', t - d))},${f1(num('ball', 'y', t - d))}) rotate(${((t - d) * 400 % 360).toFixed(1)})`); setA(gh, 'opacity', j ? 0.18 : 0.35); }
    });
  } else ball._ghosts.forEach(gh => show(gh, false));
  // Zug
  const tv = st('train', 'vis', t, 0) && (scene === 'bahnhof' || scene === 'himmel');
  show(train.g, tv);
  if (tv) {
    const wings = st('train', 'wings', t, 0), vx = numV('train', 'x', t), vy = numV('train', 'y', t);
    let r = num('train', 'r', t);
    if (wings) {   // fliegend: Nase folgt der Flugbahn (Zug schaut nach links), nur bei Tempo
      const dir = Math.atan2(vy, vx) * 57.3 - 180, wrap = ((dir + 540) % 360) - 180;
      r += clamp(wrap * 0.7, -18, 18) * clamp(Math.hypot(vx, vy) / 250, 0, 1);
    }
    const pitch = integ('trainPitch', t);
    // fliegend: Körper hebt sich im Abschlag der Flügel (an den Flügelschlag gekoppelt)
    // eingestiegen (Abfahrt) oder fliegend: Fussel sitzt vorn am Fenster
    const fIn = scene === 'himmel' || !st('fussel', 'vis', t, 0) ? { mo: mouth('F', t).o } : null;
    train.update({ x: num('train', 'x', t), y: num('train', 'y', t) + (wings ? Math.sin(t * 7) * 10 : 0), s: num('train', 's', t), r, vx, fussel: fIn,
      pitch, sag: 4 * Math.abs(pitch) + integ('trainBump', t), doors: num('train', 'doors', t), wings, flap: st('train', 'flap', t, 0), t });
  }
  // Tür-Ausschnitt für Einsteigende: Welt außerhalb des Wagenkastens + offene Türspalte
  if (tv && scene === 'bahnhof') {
    const tx = num('train', 'x', t), ty = num('train', 'y', t) + 4 * Math.abs(integ('trainPitch', t)) + integ('trainBump', t), ts = num('train', 's', t), dw = 52 * num('train', 'doors', t) * ts;
    setA(doorClipOut, 'd', `M-500 -500H2420V1580H-500Z M${f1(tx - 850 * ts)} ${f1(ty - 330 * ts)}H${f1(tx + 850 * ts)}V${f1(ty - 60 * ts)}H${f1(tx - 850 * ts)}Z`);
    doorClipGaps.forEach((g, k) => {
      const cx = tx + (k ? 280 : -280) * ts;
      setA(g, 'x', f1(cx - dw)); setA(g, 'y', f1(ty - 306 * ts)); setA(g, 'width', f1(Math.max(0, 2 * dw))); setA(g, 'height', f1(244 * ts));
    });
  }
  const inFunnel = fv && kv && st('fussel', 'funnel', t, 0);
  if ((inFunnel || ballFunnel) && kurt.funnelM) { const m = kurt.funnelM; setA(funnelClipP, 'transform', `matrix(${[m.a, m.b, m.c, m.d, m.e, m.f].map(f3).join(',')})`); }
  setA(fusselWrap, 'clip-path', fv && tv && st('fussel', 'board', t, 0) ? 'url(#doorclip)' : (inFunnel ? 'url(#funnelclip)' : 'none'));
  setA(ballWrap, 'clip-path', ballFunnel ? 'url(#funnelclip)' : 'none');
  setA(gurrWrap, 'clip-path', gv && tv && st('gurrmann', 'board', t, 0) ? 'url(#doorclip)' : 'none');

  updateCrowd(t, ascene, mini ? crowdRec(tcut) : null);
  updateCrumbs(t, scene, fx, fy);

  // Kulissen-Details
  if (scene === 'halle') {
    H.signN.textContent = String(st('sign', 'n', t, 3));
    const hh = (8 + t / 600) * 30, mm = (12 + t / 10) * 6;
    setT(H.hourHand, `rotate(${hh.toFixed(1)},1615,310)`); setT(H.minHand, `rotate(${mm.toFixed(1)},1615,310)`);
    const tu = t % 1;   // Sekundenzeiger: springt jede Sekunde mit kleinem Überschwinger
    setT(H.secK, `rotate(${f1(6 * (Math.floor(t) + (tu < 0.14 ? ease('back', tu / 0.14) : 1)))},1615,310)`);
    // Lampen pendeln; stärker, wenn KURT wackelt, beim Alarm und beim schnellen Kurbeln
    const warnS = stSmooth('warn', 'on', t, 0.4), amp = 0.9 + 5 * num('kurt', 'shake', t) + 2.5 * warnS + 1.5 * stSmooth('broesel', 'crankfast', t, 0.4);
    H.lamps.forEach((L, k) => {
      L._ang = amp * Math.sin(2 * Math.PI * t / (2.7 + 0.35 * k) + 1.9 * k);
      setT(L, `rotate(${f2(L._ang)},${L._x},44)`);
      setA(L._cone, 'opacity', f3(0.09 + 0.02 * Math.sin(3.1 * t + k) + 0.03 * warnS * Math.sin(23 * t + 2 * k)));
    });
    const cmD = st('crowd', 'mode', t, 'off'), dBoost = ['burst', 'chaos', 'clock', 'tobelt'].includes(cmD) ? 1.8 : 1;
    for (const m of H.motes) {   // Staub sinkt langsam im Kegel, blendet oben und unten weich (kein Springen beim Umlauf)
      const L = H.lamps[m._k], [h, h1, h2] = m._h, v = 10 + 18 * h, y = 230 + ((460 * h1 + t * v) % 460), q = (y - 210) / 490;
      const x = L._x + (2 * h2 - 1) * 0.8 * (70 + 230 * q) + 12 * Math.sin(0.6 * t + 2.1 * m._j) + (y - 44) * Math.tan(-L._ang * Math.PI / 180);
      setA(m, 'cx', f1(x)); setA(m, 'cy', f1(y)); setA(m, 'opacity', f3(Math.min(1, 0.5 * dBoost * Math.sin(Math.PI * (y - 230) / 460))));
    }
    const warn = warnS > 0.5;   // Warnleuchte: Lichtkegel und Raumflackern blenden in 0.4 s ein und aus
    const wp = 0.5 + 0.5 * Math.sin(t * 2 * Math.PI * 2.2);   // Warnleuchte 2.2 Hz (unter 3 Hz, fotosensibel unkritisch)
    setA(H.warnDome, 'fill', warn ? (wp > 0.5 ? '#FF7A9A' : C.him) : '#7A3046');
    show(H.warnRays, warnS > 0.01);
    if (warnS > 0.01) { setT(H.warnRays, `rotate(${(t * 400 % 360).toFixed(1)},1500,66)`); setA(H.warnRays, 'opacity', f3(warnS)); }
    setA(H.flash, 'opacity', f3(warnS * (0.03 + 0.07 * wp)));
    const bo = integ('belt', t);
    setA(H.beltTop, 'stroke-dashoffset', (-bo).toFixed(1));
    for (const r of H.rollers) { const a = bo / 13; setA(r, 'd', `M${(r._x - Math.cos(a) * 10).toFixed(1)} ${(630 - Math.sin(a) * 10).toFixed(1)}L${(r._x + Math.cos(a) * 10).toFixed(1)} ${(630 + Math.sin(a) * 10).toFixed(1)}`); }
    // Klappen schwingen mit dem Bandtempo und werden von Durchfahrenden aufgestoßen
    const bw = clamp(integ('beltRate', t) / 240, 0, 1), cm = st('crowd', 'mode', t, 'off'), cu = t - stT('crowd', 'mode', t);
    show(flapsFront, cm === 'tobelt' || cm === 'belt');
    H.flaps.forEach((fl, i) => {
      let a = Math.sin(t * 6 + i) * 6 * bw;
      const P = FLAPPASS[i];
      for (let k = lastLE(P, t); k >= 0 && t - P[k] < 2; k--) { const d = t - P[k]; a -= 22 * Math.exp(-3 * d) * Math.sin(9 * d); }
      const tr = Math.abs(a) > 0.02 ? `rotate(${f1(a)},${1781 + i * 31},470)` : '';
      setT(fl, tr); setT(H.flapsF[i], tr);
    });
    // Stempelkarten: ab dem Anflug auf die Uhr fällt eine nach der anderen aus dem Fach, taumelt, landet mit kleinem
    // Nachfedern und bleibt bis zum Ende der Halle liegen (eigene Endlage und eigener Winkel je Karte)
    H.cards.forEach((c, i) => {
      const uu = CLOCK_T === null ? -1 : t - (CLOCK_T + 1.2 + i * 0.5);
      if (uu > 0) {
        const Y = 640 + [0, 22, 8, 30][i], uL = (-300 + Math.sqrt(90000 + 800 * Y)) / 400, u = Math.min(uu, uL), q = u / uL;
        const rest = [172, -9, 188, 6][i], x = -u * 80 - i * 20 + [0, -26, 18, -8][i] * q, w = uu - uL;
        let y = u * 300 + u * u * 200, rot = rest * q + 40 * Math.sin(Math.PI * q) * (i % 2 ? 1 : -1);
        if (w > 0) { y -= 10 * Math.exp(-8 * w) * Math.abs(Math.sin(14 * w)); rot += 6 * Math.exp(-6 * w) * Math.sin(12 * w); }
        setT(c, `translate(${f1(x)},${f1(y)}) rotate(${f1(rot)},1746,${254 + i * 42})`);
      } else setT(c, '');
    });
    // Federn: beim Knall aus dem Trichter geschleudert (Luftwiderstand), dann taumeln sie wie Laub;
    // der Umlauf von unten nach oben liegt außerhalb des Bildes; auf dem Band blenden sie aus
    const fe = ['burst', 'chaos', 'clock', 'tobelt', 'belt'].includes(cm) && BURST.length;
    show(featherG, !!fe);
    if (fe) {
      const tau = t - BURST[Math.max(0, lastLE(BURST, t))], fade = cm === 'belt' ? 1 - smooth(cu / 1.5) : 1;
      feathers.forEach((e, i) => {
        const ang = -Math.PI / 2 + (2 * hash(i, 1) - 1) * 1.2, v0 = 450 + 400 * hash(i, 2), vT = 60 + 50 * hash(i, 3), k = 2.2, ex = 1 - Math.exp(-k * tau);
        const x = 852 + Math.cos(ang) * v0 * ex / k + 25 * (2 * hash(i, 4) - 1) * tau + 55 * Math.sin(1.6 * t + i) * ex;
        const y = ((500 + vT * tau + (Math.sin(ang) * v0 - vT) * ex / k + 60) % 1240 + 1240) % 1240 - 60;
        setA(e, 'cx', f1(x)); setA(e, 'cy', f1(y)); setA(e, 'transform', `rotate(${f1(40 * Math.cos(1.6 * t + i) + 300 * (1 - ex))},${f1(x)},${f1(y)})`);
        setA(e, 'opacity', f2(fade));
      });
    }
  } else show(featherG, false);
  if (scene === 'logo') {
    const p = num('logo', 'p', t), lu = t - s0;
    // Logo-Fussel: Atmen um die Fußlinie, Zucken beim Erscheinen des Knäuels (p ≈ 0.8), ein Lidschlag nach ~2 s,
    // Blick folgt der Schrift nach rechts und springt zum Knäuel
    const pp = (p - 0.8) * 3.2, jolt = pp > 0 ? 0.06 * Math.exp(-7 * pp) * Math.sin(20 * pp) : 0;
    const br = 0.016 * Math.sin(2 * Math.PI * lu / 2.4) + jolt;
    setT(H.logoFus, `translate(100,198) scale(${f3(1 - 0.5 * br)},${f3(1 + br)}) translate(-100,-198)`);
    const look = lerp(smooth((p - 0.1) / 0.5) * 2.5, 3.5, smooth(pp / 0.15)), lookY = lerp(0, -2.5, smooth(pp / 0.15));
    H.logoEyes.forEach(c => { setA(c, 'cx', f2(c._x + look)); setA(c, 'cy', f2(c._y + lookY)); });
    const bl = Math.max(blinkShape(lu - 1.55), blinkShape(lu - 3.9));
    H.logoLids.forEach(l => {
      const [cx, cy, r] = l._e, yE = cy - r + 2 * r * bl;
      show(l, bl > 0.01);
      if (bl > 0.01) setA(l, 'd', `M${cx - r - 2} ${cy - r - 2}H${cx + r + 2}V${f1(yE)}Q${cx} ${f1(yE + 3 + 4 * bl)} ${cx - r - 2} ${f1(yE)}Z`);
    });
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
    // Stempel fällt beschleunigt (aufs Stempel-Geräusch bei 0.25 s), staucht unter 1 und federt zurück;
    // den Aufprall-Stoß macht die Kamera (SHAKE_W.stamp)
    const sc = u < 0.25 ? lerp(1.8, 0.92, ease('in', u / 0.25)) : lerp(0.92, 1, ease('back', (u - 0.25) / 0.2));
    setT(H.stamp, `translate(960,320) rotate(-4) scale(${f3(sc)})`);
    setA(H.stamp, 'opacity', u < 0.05 ? 0 : 1);
    // Zeilen fliegen herein und bremsen mit kleinem Überschwinger; schnell: gestreckt + zwei Nachzieher
    const lx = (k, uu) => (k ? 1 : -1) * (1 - ease('brake', (uu - (k ? 0.6 : 0.4)) / 0.55)) * 1700;   // ganz außerhalb des Bildes
    [H.t1, H.t2].forEach((el, k) => {
      const x = lx(k, u), v = (lx(k, u + 1 / 240) - lx(k, u - 1 / 240)) * 120, sx = 1 + Math.abs(v) / 9000;
      setT(el, `translate(${f1(x)},0) translate(960,0) scale(${f3(sx)},1) translate(-960,0)`);
      [1 / 120, 1 / 60].forEach((d, j) => {
        const gh = H.tGhost[2 * k + j], on = Math.abs(v) > 1500;
        setA(gh, 'opacity', on ? (j ? 0.18 : 0.35) : 0);
        if (on) setT(gh, `translate(${f1(lx(k, u - d) - x)},0)`);
      });
    });
  }
  if (scene === 'filmtitel') {
    const u = t - s0;
    H.ft1.textContent = 'FILM ' + st('filmtitel', 'nr', t, 1);
    H.ft2.textContent = st('filmtitel', 'name', t, '');
    // Anschluss: im ersten Bild exakt KURTs Schirm (Zoom 14.4), dann öffnet sich der Rand in 0.7 s
    const R0 = 43 * 1.6 * 9, R = lerp(R0, 1150, ease('out', u / 0.7)), rimOn = u < 0.75;
    for (const e of H.ftRim) show(e, rimOn);
    show(H.ftRimFelt, rimOn); show(H.ftHi, rimOn);
    if (rimOn) {
      const circ = r => `M${f1(960 - r)} 540a${f1(r)} ${f1(r)} 0 1 0 ${f1(2 * r)} 0a${f1(r)} ${f1(r)} 0 1 0 ${f1(-2 * r)} 0Z`;
      const Rs = R * 44 / 43, Rb = R * 54 / 43, big = 'M-10 -10H1930V1090H-10Z';
      setA(H.ftRim[0], 'd', circ(Rs) + circ(R)); setA(H.ftRim[1], 'd', circ(Rb) + circ(Rs));
      setA(H.ftRim[2], 'd', big + circ(Rb));
      // Filz des Gehäuses in KURTs eigenen Koordinaten, damit das Muster genauso groß ist wie in der Halle
      setT(H.ftRimFelt, `translate(960,540) scale(${f3(14.4 * R / R0)}) translate(-115,-128)`);
      const k = R / R0;
      setA(H.ftHi, 'cx', f1(960 + 17 * 14.4 * k)); setA(H.ftHi, 'cy', f1(540 - 24 * 14.4 * k)); setA(H.ftHi, 'r', f1(57.6 * k));
      setA(H.ftHi, 'opacity', f3(0.18 * (1 - smooth(u / 0.5))));
    }
    // Die Fahrt läuft weiter: Karte von 1.25 auf 1; großer Titel schaltet sich wie eine Röhre ein
    const sc = lerp(1.25, 1, ease('out', u / 0.6));
    setT(H.ftG, `translate(960,540) scale(${f3(sc)}) translate(-960,-540)`);
    const fl = lerp(1, 0.92 + 0.05 * Math.sin(t * 11.3) + 0.03 * Math.sin(t * 27.1), smooth(u / 0.5));   // Röhrenflimmern, stetig
    setA(H.ft1, 'opacity', f3(fl));
    const on = clamp((u - 0.15) / 0.18, 0, 1);
    show(H.ft2, on > 0);
    setA(H.ft2, 'opacity', f3(fl));
    setT(H.ft2, `translate(960,590) scale(${f3(lerp(1.06, 1, ease('out', on)))},${f3(lerp(0.05, 1, ease('out', on)))}) translate(-960,-590)`);
    setA(H.ftGlow, 'opacity', f3(lerp(1, 0.6 + 0.15 * Math.sin(t * 3.1), smooth(u / 0.8))));
    setA(H.ftScan, 'opacity', f3(0.6 * smooth(u / 0.4)));
  }
  if (ascene === 'bahnhof') {
    // Anzeigetafel als Fallblatt: jedes geänderte Zeichen blättert, bis es (von links, Zeile für Zeile) steht
    const BL = (TL.states.board && TL.states.board.text) || [], kb = lastLE(BL, t + 1e-6, e => e[0]);
    const bt = kb >= 0 ? BL[kb][1] : 'leer', bt0 = kb >= 0 ? BL[kb][0] : -1e9;
    // beim Szenenanfang gesetzt: die Tafel steht schon so da, nichts blättert
    const bOld = kb > 0 && Math.abs(bt0 - s0) > 1e-3 ? BL[kb - 1][1] : bt;
    const rows = BOARD[bt] || BOARD.leer, old = BOARD[bOld] || ['', '', ''];
    [H.b1, H.b2, H.b3].forEach((el, ri) => {
      const nw = rows[ri], od = old[ri], n = Math.max(nw.length, od.length);
      let out = '';
      for (let c = 0; c < n; c++) {
        const ch = nw[c] || ' ', oc = od[c] || ' ';
        out += t < bt0 + 0.1 + 0.022 * c + 0.12 * ri && ch !== oc ? FLAPS[Math.floor(hash(c + 40 * ri, Math.floor(t * 30)) * FLAPS.length)] : ch;
      }
      if (el.textContent !== out) el.textContent = out;
    });
    setA(H.b3, 'opacity', bt === 'kruemel2' || bt === 'einfahrt' ? (((t * 1.25) % 1) < 0.65 ? 1 : 0.3) : 1);
    const sec = t % 60, sa = sec < 58.5 ? sec / 58.5 * 360 : 0, mu = sec / 0.12;
    setT(H.secHand, `rotate(${f1(sa)},1020,150)`);
    setT(H.clockMin, `rotate(${f1(6 * (12 + Math.floor(t / 60) - 1 + ease('back', mu)))},1020,150)`);
    const a = ampS('A', t);
    setT(H.horn, `translate(1812,200) scale(${(1 + a * 0.06).toFixed(3)}) translate(-1812,-200)`);
    H.hornW.forEach((w, k) => {
      const u = (t * 1.8 + k / 2) % 1, op = (1 - u) * smooth(u / 0.15) * Math.min(1, 2.5 * a);
      show(w, op > 0.01);
      if (op > 0.01) { setT(w, `translate(${f1(-36 * u)},0) translate(1730,205) scale(${f3(1 + 0.4 * u)}) translate(-1730,-205)`); setA(w, 'opacity', f2(op)); }
    });
  }
  if (ascene === 'zug') {
    const view = st('outside', 'view', t, 'land'), air = view === 'clouds' || view === 'circle';
    show(H.outLand, !air); show(H.outClouds, air);
    setT(H.outside, `translate(0,${f2(-0.9 * rkY)})`);
    const off = integ('land', t);
    setT(H.landFar, `translate(${(-(off * 0.3) % 1200).toFixed(1)},0)`);
    setT(H.landNear, `translate(${(-(off * 0.8) % 1200).toFixed(1)},0)`);
    setT(H.poles, `translate(${(-(off * 2.2) % 600).toFixed(1)},0)`);
    // Masten verwischen mit dem Tempo (Breite ~ Weg pro Bild, Deckkraft flächengleich)
    const pv = 2.2 * 520 * Math.abs(num('outside', 'v', t)), pw = 14 + 0.8 * pv / TL.fps;
    for (const pr of H.poleRects) { setA(pr, 'x', f1(pr._x - pw / 2)); setA(pr, 'width', f1(pw)); setA(pr, 'opacity', f2(Math.max(0.45, 14 / pw))); }
    // Bäckerei: liegt an der Strecke und kommt genau dort zum Stehen, wo der Zug hält
    let bdx = 1e9;
    for (const tS of STOPS) { const d = -(off - integ('land', tS)); if (Math.abs(d) < Math.abs(bdx)) bdx = d; }
    // −150: beim Halt stehen Brezel und Schild mitten im mittleren Fenster (x 720–1200), nicht auf dem Fensterrahmen
    show(H.outBakery, !air && Math.abs(bdx) < 2600);
    if (Math.abs(bdx) < 2600) setT(H.outBakery, `translate(${f1(bdx - 150)},0)`);
    setT(H.speaker, `translate(1780,100) scale(${f3(1 + 0.08 * ampS('A', t))}) translate(-1780,-100)`);
    if (view === 'clouds' || view === 'circle') {
      setT(H.cloudRow, `translate(${(-(t * 420) % 900).toFixed(1)},${view === 'circle' ? (Math.sin(t * 1.2) * 60).toFixed(1) : 0})`);
      const bx = view === 'circle' ? 2200 - ((t * 500) % 2600) : 4000;
      setT(H.cloudBrezel, `translate(${bx.toFixed(1)},300)`);
    }
  }
  if (scene === 'himmel') {
    setT(H.sunRays, `rotate(${(t * 10 % 360).toFixed(1)},1620,190)`);
    // Wolken ziehen nach rechts (der Zug fliegt nach links); beim Rückwärtsfliegen dreht der Wind um
    const co = integ('cloud', t);
    H.clouds.forEach(c => { const x = ((c._k * 330 + co * c._sp) % 2400 + 2400) % 2400 - 300; setT(c, `translate(${f1(x)},${140 + (c._k * 97) % 560}) scale(${c._sc})`); });
    H.fgClouds.forEach(c => { const x = ((c._k * 3000 + co * 420) % 6000 + 6000) % 6000 - 700; setT(c, `translate(${f1(x)},${c._k ? 180 : 900}) scale(1.8)`); });
    const sw = st('swarm', 'on', t, 0);
    show(H.swarm, sw);
    if (sw) {
      const bz = `translate(860,${f1(560 + 10 * Math.sin(0.8 * t))}) rotate(${f2(2 * Math.sin(0.5 * t))})`;
      setT(H.brezel, bz); setT(H.brezelLabel, bz);
      const A = integ('swarmA', t);
      H.minis.forEach((m, i) => {   // kreisen um die Brezel; Blick bleibt "vorwärts", auch wenn der Schwarm rückwärts fliegt
        const a = A + i * Math.PI * 2 / H.minis.length, rk = 1 + 0.1 * Math.sin(i * 2.3), dep = 0.8 + 0.25 * Math.sin(a);
        const x = 960 + Math.cos(a) * 640 * rk, y = 520 + Math.sin(a) * 300 * rk + 14 * Math.sin(1.7 * t + i);
        const face = -Math.sin(a), fx = (face < 0 ? -1 : 1) * Math.max(0.25, Math.abs(face));
        const dA = (integ('swarmA', t + 1 / 120) - integ('swarmA', t - 1 / 120)) * 60;   // Kreistempo [rad/s]
        const vx = -Math.sin(a) * 640 * rk * dA, vy = Math.cos(a) * 300 * rk * dA + 23.8 * Math.cos(1.7 * t + i);
        setT(m.g, `${smearT(vx, vy, 1 / 6000, 0.12, x, y)}translate(${f1(x)},${f1(y)}) rotate(${f2(10 * Math.cos(a))}) scale(${f3(fx * dep)},${f3(dep)})`);
        setT(m.w, `rotate(${f1(Math.sin(t * (8 + 2 * i) + i) * 20)},0,-30)`);
        m._want = Math.sin(a) > 0;   // vordere Hälfte vor der Brezel (aber hinter dem Schild)
      });
      // nur beim Wechsel umhängen, dann alle in fester Reihenfolge: die Ebenen hängen nur vom Bild ab, nicht vom Verlauf
      if (H.minis.some(m => m._front !== m._want)) H.minis.forEach(m => { m._front = m._want; H.swarm.insertBefore(m.g, m._want ? H.brezelLabel : H.brezel); });
    }
  }
  if (scene === 'endcard') {
    const u = t - s0;
    H.endFussel.update(poseEndFussel(t, u));
    setT(H.endTitle, `translate(0,${f1((1 - ease('back', u / 0.6)) * 300)})`);
    setA(H.endFrame, 'stroke-dashoffset', f1(-t * 30));   // Lauflicht-Rahmen
    setT(H.endDots, `translate(${f2((t * 12) % 32)},${f2((t * 6) % 32)})`);
  }

  // Iris und Abblende
  const ir = num('iris', 'r', t), ix = num('iris', 'x', t), iy = num('iris', 'y', t);
  const cover = Math.hypot(Math.max(ix, 1920 - ix), Math.max(iy, 1080 - iy));   // Kreis deckt alle Ecken: aus
  if (ir < cover) { setA(irisPath, 'd', `M0 0H1920V1080H0Z M${f1(ix - ir)} ${f1(iy)}a${f1(ir)} ${f1(ir)} 0 1 0 ${f1(2 * ir)} 0a${f1(ir)} ${f1(ir)} 0 1 0 ${f1(-2 * ir)} 0Z`); show(irisPath, true); }
  else show(irisPath, false);
  setA(fadeRect, 'opacity', num('fade', 'a', t).toFixed(3));
}

window.init = function (tl) { TL = tl; precompute(); return Math.round(tl.total * tl.fps); };
window.render = render;
// Für Prüfskripte: Zugriff auf Figuren, Kulissen und Kanäle (wird beim Rendern nicht benutzt)
window.STAGE = { fussel, kurt, broesel, gurrmann, sitter, crowd, train, H, world, INT, integ, num, numV, numA, mouth, pulse, BLINK, ACC, JUMP, poseFussel, posePigeon, poseKurt };
