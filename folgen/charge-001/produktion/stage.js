/* Flausenfabrik – Renderer für Charge 001.
   Zeichnet jedes Bild deterministisch aus timeline.json: render(frame).
   Stop-Motion-Look: 12 Bilder pro Sekunde, leichtes Wackeln der Figuren. */
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
function hash(a, b) { let x = Math.sin(a * 127.1 + b * 311.7) * 43758.5453; return x - Math.floor(x); }
function rnd(a, b) { return hash(a, b) * 2 - 1; }

// ---------------------------------------------------------------------------
// Zeitplan lesen
// ---------------------------------------------------------------------------
const DEF = {
  cam: { x: 960, y: 540, z: 1, r: 0 }, fussel: { x: -500, y: 900, s: 0.8, r: 0, flip: 1, lx: 0, ly: 0, thread: 1 },
  kurt: { x: 860, y: 900, s: 1.6, shake: 0 }, broesel: { x: 2200, y: 900, s: 1.25, r: 0, flip: -1, lid: 0.55, wing: 0 },
  gurrmann: { x: 2200, y: 900, s: 1.3, r: 0, flip: -1, lid: 0.2, wing: 0 }, train: { x: 3000, y: 740, s: 1, r: 0, doors: 0 },
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
function sceneAt(t) {
  let s = TL.scenes[0][1], s0 = 0;
  for (const [t0, n] of TL.scenes) { if (t0 > t + 1e-6) break; s = n; s0 = t0; }
  return [s, s0];
}
function amp(who, t, fx) {
  for (const l of TL.lines) {
    if (l.who !== who) continue;
    if (fx !== undefined && l.fx !== fx) continue;
    if (t >= l.t0 && t < l.t1) { const i = Math.floor((t - l.t0) * TL.fps); return l.env[i] || 0; }
  }
  return 0;
}
// Integrale über Zeit, vorab berechnet (Kurbel, Band, Fensterlandschaft)
const INT = {};
function buildIntegrals() {
  const dt = 1 / 48, n = Math.ceil(TL.total / dt) + 2;
  const crank = new Float32Array(n), belt = new Float32Array(n), land = new Float32Array(n);
  for (let i = 1; i < n; i++) {
    const t = i * dt;
    const c = st('kurt', 'crank', t, 0) ? (st('broesel', 'crankfast', t, 0) ? 900 : 380) : 0;
    crank[i] = crank[i - 1] + c * dt;
    belt[i] = belt[i - 1] + (st('belt', 'run', t, 0) ? 190 : 0) * dt;
    land[i] = land[i - 1] + num('outside', 'v', t) * 520 * dt;
  }
  Object.assign(INT, { dt, crank, belt, land });
}
function integ(name, t) { const a = INT[name]; return a[clamp(Math.round(t / INT.dt), 0, a.length - 1)]; }

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

function makeFussel(parent) {
  const g = E('g', null, parent), inner = E('g', null, g);
  const thread = E('path', { fill: 'none', stroke: C.himD, 'stroke-width': 5, 'stroke-linecap': 'round' }, inner);
  const legs = E('path', { fill: 'none', stroke: C.ink, 'stroke-width': 6, 'stroke-linecap': 'round' }, inner);
  const f1 = E('ellipse', { rx: 11, ry: 6, fill: C.ink }, inner), f2 = E('ellipse', { rx: 11, ry: 6, fill: C.ink }, inner);
  const body = E('g', null, inner);
  E('path', { d: FUR, fill: C.him }, body);
  E('path', { d: FUR, fill: 'url(#felt)' }, body);
  E('path', { d: 'M62 132q6 8 4 16M140 134q-5 8-3 15M70 80q5-6 13-7M128 76q8 2 12 9M96 158q6 3 12 0', fill: 'none', stroke: C.himD, 'stroke-width': 3, 'stroke-linecap': 'round' }, body);
  const eyes = E('g', null, body);
  const open = E('g', null, eyes);
  E('circle', { cx: 79, cy: 106, r: 19, fill: '#fff' }, open);
  E('circle', { cx: 122, cy: 104, r: 15, fill: '#fff' }, open);
  const p1 = E('circle', { r: 9, fill: C.ink }, open), p2 = E('circle', { r: 7.5, fill: C.ink }, open);
  const h1 = E('circle', { r: 3, fill: '#fff' }, open), h2 = E('circle', { r: 2.5, fill: '#fff' }, open);
  const happy = E('path', { d: 'M64 110q15-18 30 0M110 108q12-15 24 0', fill: 'none', stroke: C.ink, 'stroke-width': 6, 'stroke-linecap': 'round' }, eyes);
  const mouth = E('ellipse', { cx: 103, cy: 138, rx: 7, ry: 5, fill: C.ink }, body);
  const tongue = E('ellipse', { cx: 103, cy: 143, rx: 4, ry: 3, fill: C.himD }, body);
  let tlen = 0;
  return {
    g, update(o) {
      setT(g, `translate(${o.x.toFixed(1)},${o.y.toFixed(1)}) rotate(${o.r.toFixed(2)}) scale(${(o.s * o.flip * o.sx).toFixed(4)},${(o.s * o.sy).toFixed(4)}) translate(-100,-202)`);
      const w = o.t * 3.2;
      const d = `M101 52C${97 + Math.sin(w) * 3} 36 ${106 + Math.sin(w + 1) * 4} 22 ${121 + Math.sin(w + 2) * 3} 24C135 26 136 42 124 44C114 46 112 32 124 22C134 14 ${152 + Math.sin(w + 1.5) * 5} ${14 + Math.cos(w) * 4} ${162 + Math.sin(w + .7) * 6} ${24 + Math.sin(w + 2.1) * 6}`;
      setA(thread, 'd', d);
      if (!tlen) tlen = thread.getTotalLength();
      setA(thread, 'stroke-dasharray', `${(tlen * o.thread).toFixed(1)} 400`);
      let L;
      if (o.sit) L = 'M86 160L74 182M114 160L126 182';
      else if (o.air) L = 'M86 162L88 182M114 162L112 182';
      else if (o.walk) { const a = Math.sin(o.t * 14) * 7; L = `M86 166L${82 + a} ${194 - Math.max(0, a)}M114 166L${118 - a} ${194 - Math.max(0, -a)}`; }
      else L = 'M86 166L82 194M114 166L118 194';
      setA(legs, 'd', L);
      const m = L.match(/-?[\d.]+/g).map(Number);
      setA(f1, 'cx', m[2] - 4); setA(f1, 'cy', m[3] + 2); setA(f2, 'cx', m[6] + 4); setA(f2, 'cy', m[7] + 2);
      const happyOn = o.eyes === 'happy';
      show(happy, happyOn); show(open, !happyOn);
      const sc = o.eyes === 'wide' ? 1.17 : 1, blink = o.blink ? 0.12 : 1;
      setT(eyes, `translate(100,105) scale(${sc},${sc * blink}) translate(-100,-105)`);
      const lx = o.lx * 6, ly = o.ly * 5;
      setA(p1, 'cx', 84 + lx); setA(p1, 'cy', 110 + ly); setA(p2, 'cx', 125 + lx * .8); setA(p2, 'cy', 108 + ly * .8);
      setA(h1, 'cx', 87 + lx); setA(h1, 'cy', 106.5 + ly); setA(h2, 'cx', 127.5 + lx * .8); setA(h2, 'cy', 105 + ly * .8);
      const ry = 4.5 + o.amp * 9 + (o.eyes === 'wide' ? 2 : 0);
      setA(mouth, 'ry', ry.toFixed(1)); setA(mouth, 'rx', (7 + o.amp * 2).toFixed(1));
      setA(tongue, 'cy', (138 + ry * 0.55).toFixed(1));
      show(tongue, ry > 7);
    }
  };
}

function makeKurt(parent) {
  const g = E('g', null, parent), inner = E('g', null, g);
  const steam = E('g', null, inner);
  const puffs = [];
  for (let i = 0; i < 7; i++) puffs.push(E('circle', { fill: C.garn, opacity: 0.8 }, steam));
  E('rect', { x: 101, y: 40, width: 18, height: 24, fill: C.petDD }, inner);
  E('path', { d: 'M70 10H150L124 46H96Z', fill: C.garn }, inner);
  E('path', { d: 'M118 10H150L124 46H112Z', fill: C.garnD }, inner);
  E('ellipse', { cx: 110, cy: 10, rx: 40, ry: 7, fill: C.ink }, inner);
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
  const cid = 'kclip' + Math.floor(Math.random() * 1e6);
  const cp = E('clipPath', { id: cid }, defs); E('circle', { cx: 115, cy: 128, r: 43 }, cp);
  const content = E('g', { 'clip-path': `url(#${cid})` }, inner);
  const face = E('g', null, content);
  const e1 = E('rect', { x: 91, y: 110, width: 15, height: 20, rx: 2, fill: C.senf }, face);
  const e2 = E('rect', { x: 124, y: 110, width: 15, height: 20, rx: 2, fill: C.senf }, face);
  const mouth = E('rect', { x: 99, y: 146, width: 32, height: 5, rx: 2, fill: C.senf }, face);
  const load = E('g', null, content); const dots = [];
  for (let i = 0; i < 8; i++) dots.push(E('rect', { width: 7, height: 7, rx: 1, fill: C.senf }, load));
  const err = E('g', null, content);
  E('path', { d: 'M90 108l16 18M106 108l-16 18M124 108l16 18M140 108l-16 18', stroke: C.senf, 'stroke-width': 5, 'stroke-linecap': 'round' }, err);
  const errMouth = E('path', { d: 'M96 150l6-6 6 6 6-6 6 6 6-6', fill: 'none', stroke: C.senf, 'stroke-width': 4, 'stroke-linejoin': 'round' }, err);
  const boot = E('rect', { x: 71, y: 126, width: 88, height: 4, fill: C.garn }, content);
  const film = E('g', null, content);
  E('rect', { x: 70, y: 84, width: 90, height: 90, fill: '#163A3E' }, film);
  E('rect', { x: 70, y: 150, width: 90, height: 30, fill: '#0B2427' }, film);
  const ftrain = E('g', null, film);
  E('rect', { x: 0, y: 0, width: 44, height: 14, rx: 5, fill: C.senf }, ftrain);
  E('rect', { x: 5, y: 3, width: 6, height: 5, fill: C.screen }, ftrain); E('rect', { x: 16, y: 3, width: 6, height: 5, fill: C.screen }, ftrain); E('rect', { x: 27, y: 3, width: 6, height: 5, fill: C.screen }, ftrain);
  const fcloud = E('g', null, film);
  E('rect', { x: 0, y: 0, width: 18, height: 6, rx: 3, fill: C.garn, opacity: 0.6 }, fcloud);
  const ans = E('g', null, content); const bars = [];
  for (let i = 0; i < 7; i++) bars.push(E('rect', { x: 84 + i * 9, width: 6, rx: 2, fill: C.senf }, ans));
  E('rect', { x: 70, y: 84, width: 90, height: 90, fill: 'url(#scan)', opacity: 0.5 }, inner);
  E('circle', { cx: 132, cy: 104, r: 4, fill: '#fff', opacity: 0.18 }, inner);
  E('rect', { x: 80, y: 205, width: 70, height: 20, rx: 3, fill: C.senf }, inner);
  T(E('text', { x: 115, y: 219.5, 'text-anchor': 'middle', 'font-family': FONT.mono, 'font-size': 11, 'font-weight': 500, fill: C.ink, 'letter-spacing': 1 }, inner), 'K.U.R.T.');
  E('circle', { cx: 56, cy: 215, r: 9, fill: C.garn }, inner);
  const n1 = E('path', { stroke: C.ink, 'stroke-width': 2.5, 'stroke-linecap': 'round' }, inner);
  E('circle', { cx: 174, cy: 215, r: 9, fill: C.garn }, inner);
  const n2 = E('path', { stroke: C.ink, 'stroke-width': 2.5, 'stroke-linecap': 'round' }, inner);
  return {
    g, update(o) {
      const sh = o.shake;
      const jx = sh * 7 * rnd(o.f, 3), jy = sh * 4 * rnd(o.f, 4), jr = sh * 1.5 * rnd(o.f, 5);
      setT(g, `translate(${(o.x + jx).toFixed(1)},${(o.y + jy).toFixed(1)}) rotate(${(o.r + jr).toFixed(2)}) scale(${o.s},${o.s}) translate(-115,-262)`);
      setT(crank, `rotate(${(o.crank % 360).toFixed(1)},200,128)`);
      const na = o.cranking ? Math.sin(o.t * 9) * 0.9 : -0.6, nb = o.cranking ? Math.cos(o.t * 7) * 0.9 : 2.3;
      setA(n1, 'd', `M56 215L${(56 + Math.sin(na) * 7).toFixed(1)} ${(215 - Math.cos(na) * 7).toFixed(1)}`);
      setA(n2, 'd', `M174 215L${(174 + Math.sin(nb) * 7).toFixed(1)} ${(215 - Math.cos(nb) * 7).toFixed(1)}`);
      let mode = o.screen;
      if (mode === 'film' && o.amp > 0) mode = 'on';
      setA(scr, 'fill', mode === 'red' ? '#4A1027' : (mode === 'off' ? '#0A1719' : C.screen));
      show(face, mode === 'on' || mode === 'glitch');
      show(load, mode === 'load'); show(err, mode === 'red'); show(boot, mode === 'boot');
      show(film, mode === 'film'); show(ans, mode === 'ansage');
      if (mode === 'on' || mode === 'glitch') {
        const bl = o.blink ? 3 : 20;
        let gx = 0;
        if (mode === 'glitch') gx = rnd(o.f, 9) * 8;
        setA(e1, 'height', bl); setA(e2, 'height', bl);
        setA(e1, 'y', 120 - bl / 2); setA(e2, 'y', 120 - bl / 2);
        setA(e1, 'x', 91 + gx); setA(e2, 'x', 124 - gx);
        const mh = 5 + o.amp * 16;
        setA(mouth, 'height', mh.toFixed(1)); setA(mouth, 'y', (148.5 - mh / 2).toFixed(1));
        setA(e1, 'fill', mode === 'glitch' && o.f % 2 ? C.him : C.senf);
      }
      if (mode === 'load') {
        for (let i = 0; i < 8; i++) {
          const a = i / 8 * Math.PI * 2;
          setA(dots[i], 'x', (115 + Math.cos(a) * 20 - 3.5).toFixed(1)); setA(dots[i], 'y', (128 + Math.sin(a) * 20 - 3.5).toFixed(1));
          setA(dots[i], 'opacity', (((i - o.f) % 8 + 8) % 8 / 8 * 0.85 + 0.15).toFixed(2));
        }
      }
      if (mode === 'red') setT(errMouth, `translate(0,${(o.f % 2) * 2})`);
      if (mode === 'boot') { const u = clamp(o.sinceScreen / 1.2, 0, 1); setA(boot, 'width', (88 * u).toFixed(1)); setA(boot, 'x', (115 - 44 * u).toFixed(1)); setA(boot, 'height', (2 + 30 * u * u).toFixed(1)); setA(boot, 'y', (128 - (1 + 15 * u * u)).toFixed(1)); }
      if (mode === 'film') {
        const u = (o.t * 0.35) % 1;
        setT(ftrain, `translate(${(170 - u * 140).toFixed(1)},${(140 + Math.sin(o.t * 3) * 2).toFixed(1)})`);
        setT(fcloud, `translate(${(60 + ((o.t * 12) % 110)).toFixed(1)},100)`);
      }
      if (mode === 'ansage') for (let i = 0; i < 7; i++) { const h = 6 + o.ansAmp * 40 * (0.5 + 0.5 * Math.abs(Math.sin(i * 1.7 + o.f))); setA(bars[i], 'height', h.toFixed(1)); setA(bars[i], 'y', (128 - h / 2).toFixed(1)); }
      show(steam, o.steam);
      if (o.steam) for (let i = 0; i < puffs.length; i++) {
        const u = ((o.t * 0.9 + i / puffs.length) % 1);
        setA(puffs[i], 'cx', (110 + Math.sin(i * 2.3 + o.t) * 18 * u).toFixed(1)); setA(puffs[i], 'cy', (0 - u * 120).toFixed(1));
        setA(puffs[i], 'r', (8 + u * 26).toFixed(1)); setA(puffs[i], 'opacity', (0.85 * (1 - u)).toFixed(2));
      }
    }
  };
}

let PID = 0;
function makePigeon(parent, opt) {
  opt = Object.assign({ body: C.taube, wingC: C.taubeD, hat: 'none', neck: true, board: false }, opt || {});
  const id = ++PID;
  const g = E('g', null, parent), inner = E('g', null, g);
  const farWing = E('path', { d: 'M120 130C140 80 190 60 214 70C200 100 170 130 126 146Z', fill: opt.wingC, opacity: 0.85 }, inner);
  E('path', { d: 'M168 134L226 112L214 170Z', fill: opt.wingC }, inner);
  const legs = E('path', { fill: 'none', stroke: C.him, 'stroke-width': 6, 'stroke-linecap': 'round' }, inner);
  E('ellipse', { cx: 118, cy: 150, rx: 74, ry: 58, fill: opt.body }, inner);
  E('ellipse', { cx: 118, cy: 150, rx: 74, ry: 58, fill: 'url(#felt)' }, inner);
  if (opt.neck) {
    E('path', { d: 'M60 124C72 100 104 98 116 112C104 132 74 140 60 124Z', fill: C.pet }, inner);
    E('path', { d: 'M70 136C84 128 102 128 112 134C100 144 82 146 70 136Z', fill: C.him, opacity: 0.6 }, inner);
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
  E('path', { d: 'M44 92L22 101L46 99Z', fill: C.ink }, head);
  const lower = E('path', { d: 'M46 99L24 102L46 104Z', fill: C.ink }, head);
  E('ellipse', { cx: 47, cy: 91, rx: 5, ry: 4, fill: C.garn }, head);
  const cid = 'eye' + id;
  const cp = E('clipPath', { id: cid }, defs); E('circle', { cx: 68, cy: 82, r: 11 }, cp);
  E('circle', { cx: 68, cy: 82, r: 11, fill: '#fff' }, head);
  const pupil = E('circle', { cx: 66, cy: 85, r: 5, fill: C.ink }, head);
  const lidG = E('g', { 'clip-path': `url(#${cid})` }, head);
  const lid = E('rect', { x: 55, y: 70, width: 28, height: 10, fill: opt.wingC }, lidG);
  const lidLine = E('path', { stroke: C.ink, 'stroke-width': 2.5, 'stroke-linecap': 'round' }, head);
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
  return {
    g, opt, update(o) {
      const face = o.flip < 0 ? 1 : -1;
      setT(g, `translate(${o.x.toFixed(1)},${o.y.toFixed(1)}) rotate(${(o.r || 0).toFixed(2)}) scale(${(o.s * face).toFixed(4)},${o.s.toFixed(4)}) translate(-110,-226)`);
      let L;
      if (o.fly) L = 'M100 196L112 206M124 198L134 206';
      else if (o.sit) L = 'M96 200L86 210M126 202L118 212';
      else if (o.walk) { const a = Math.sin(o.t * 12) * 8; L = `M96 200L${90 + a} 222M126 202L${130 - a} 224M${80 + a} 224H${100 + a}M${118 - a} 226H${140 - a}`; }
      else L = 'M96 200L90 222M126 202L130 224M78 224H100M118 226H140';
      setA(legs, 'd', L);
      let wr = -o.wing * 55;
      if (o.fly) wr = -20 - 45 * (0.5 + 0.5 * Math.sin(o.t * 26 + o.ph));
      if (o.crank) wr = -25 + Math.sin(o.crankA * Math.PI / 180) * 18;
      if (o.sweep) wr = Math.sin(o.t * 6) * 14;
      setT(wing, `rotate(${wr.toFixed(1)},125,138)`);
      show(farWing, !!o.fly);
      if (o.fly) setT(farWing, `rotate(${(-30 + 50 * Math.sin(o.t * 26 + o.ph + 0.6)).toFixed(1)},126,140)`);
      show(broom, !!o.broom);
      if (o.broom) setT(broom, 'rotate(25,150,150)');
      let hr = (o.head || 0) + Math.sin(o.t * 1.3 + o.ph) * 2;
      if (o.walk) hr += Math.sin(o.t * 12) * 6;
      if (o.crank) hr += Math.sin(o.crankA * Math.PI / 180) * 9;
      if (o.peck) hr += o.peck;
      setT(head, `rotate(${hr.toFixed(1)},92,118)`);
      setT(lower, `rotate(${(-o.amp * 22).toFixed(1)},46,100)`);
      const lidv = o.blink ? 1 : clamp(o.lid, 0, 1);
      setA(lid, 'height', (22 * lidv).toFixed(1));
      setA(lidLine, 'd', `M57 ${(71 + 22 * lidv).toFixed(1)}H79`);
      show(lidLine, lidv > 0.08);
      setA(pupil, 'cx', (66 + (o.px || 0)).toFixed(1)); setA(pupil, 'cy', (85 + (o.py || 0)).toFixed(1));
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

function updateCrowd(t, f, scene) {
  const mode = st('crowd', 'mode', t, 'off');
  const m0 = stT('crowd', 'mode', t), u = t - m0;
  const prevMode = (() => { const L = TL.states.crowd && TL.states.crowd.mode; if (!L) return 'off'; let p = 'off'; for (let i = 0; i < L.length; i++) { if (L[i][0] >= m0 - 1e-6) break; p = L[i][1]; } return p; })();
  for (let i = 0; i < CROWD_N; i++) {
    const p = crowd[i];
    let o = { x: 0, y: 0, s: 0.75, flip: -1, t, f, ph: i * 1.3, lid: 0.25, amp: 0, walk: 0, fly: 0, sit: 0, head: 0, peck: 0, blink: ((t + i * 0.7) % 4.6) < 0.1, wing: 0 };
    let vis = true;
    if (mode === 'off') vis = false;
    else if (mode === 'platform' || mode === 'look' || mode === 'board') {
      const [x, y, fl] = PLAT_POS[i];
      o.x = x; o.y = y; o.flip = fl; o.s = 0.62 + (y - 900) / 900;
      const pk = Math.max(0, Math.sin(t * 2.2 + i * 2.1));
      o.peck = pk > 0.92 ? 28 : 0;
      if (mode === 'look') { o.flip = x < 600 ? 1 : -1; o.head = -14; o.peck = 0; o.lid = 0; }
      if (mode === 'board') {
        const d0 = 0.08 * i, uu = clamp((u - d0) / 1.4, 0, 1);
        const tx = i % 2 ? 700 : 1260, ty = 820;
        o.x = lerp(x, tx, uu); o.y = lerp(y, ty, uu) - Math.sin(uu * Math.PI) * 120; o.flip = tx > x ? 1 : -1;
        o.fly = uu > 0 && uu < 1; o.s *= lerp(1, 0.7, uu);
        if (uu >= 1) vis = false;
      }
    } else if (mode === 'seats' || mode === 'window' || mode === 'loud') {
      if (i >= SEAT_POS.length || scene !== 'zug') vis = false;
      else {
        const [x, y] = SEAT_POS[i]; o.x = x; o.y = y; o.sit = 1; o.s = 0.72; o.flip = i % 2 ? -1 : 1;
        if (mode === 'window') { o.head = -22; o.lid = 0; o.flip = 1; o.r = -6; }
        if (mode === 'loud') { o.amp = 0.5 + 0.5 * Math.abs(Math.sin(t * 9 + i)); o.head = Math.sin(t * 10 + i) * 10; o.y -= Math.abs(Math.sin(t * 8 + i)) * 10; }
      }
    } else if (mode === 'burst' || mode === 'chaos' || mode === 'clock' || mode === 'tobelt' || mode === 'belt') {
      if (scene !== 'halle') vis = false;
      o.s = 0.6; o.fly = 1;
      if (mode === 'burst') {
        const uu = clamp(u / 1.4, 0, 1), [cx, cy] = chaosPos(i, t);
        o.x = lerp(853, cx, ease('out', uu)); o.y = lerp(678, cy, ease('out', uu)); o.s = lerp(0.15, 0.6, uu); o.flip = cx > 853 ? 1 : -1;
      } else if (mode === 'chaos' || (mode === 'clock' && i % 3)) {
        const [x, y] = chaosPos(i, t), [x2] = chaosPos(i, t + 0.05); o.x = x; o.y = y; o.flip = x2 > x ? 1 : -1;
      } else if (mode === 'clock') {
        const tx = 1660 + (i % 4) * 30, ty = 300 + (i % 3) * 50, [sx, sy] = chaosPos(i, m0), uu = clamp(u / 1.0, 0, 1);
        o.x = lerp(sx, tx, ease('io', uu)); o.y = lerp(sy, ty, ease('io', uu)); o.flip = 1;
        if (uu >= 1) { o.fly = 0; o.peck = Math.sin(t * 14 + i) > 0 ? 26 : 0; }
      } else {
        const tx = beltX(i), ty = 608;
        const [sx, sy] = prevMode === 'clock' || prevMode === 'chaos' || mode === 'tobelt' ? chaosPos(i, mode === 'tobelt' ? m0 : stT('crowd', 'mode', m0 - 0.01)) : [tx, ty];
        if (mode === 'tobelt') {
          const uu = clamp((u - i * 0.05) / 1.2, 0, 1);
          o.x = lerp(sx, tx, ease('io', uu)); o.y = lerp(sy, ty, ease('io', uu)); o.flip = 1;
          if (uu >= 1) o.fly = 0;
        } else {
          o.fly = 0; o.flip = 1; o.x = tx + (integ('belt', t) - integ('belt', m0)); o.y = ty; o.s = 0.6;
          if (o.x > 1790) vis = false;
          o.head = Math.sin(t * 3 + i) * 5;
        }
      }
    } else vis = false;
    if (scene === 'logo' || scene === 'titel' || scene === 'filmtitel' || scene === 'endcard' || scene === 'himmel') vis = false;
    show(p.g, vis);
    if (vis) { o.x += rnd(f, 50 + i) * 0.8; o.y += rnd(f, 70 + i) * 0.8; p.update(o); }
  }
}

function updateCrumbs(t, f, scene, fx, fy) {
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

// ---------------------------------------------------------------------------
// Bild berechnen
// ---------------------------------------------------------------------------
function blinkAt(t, period, ph) { return ((t + ph) % period) < 0.11; }
function boil(f, id) { return [rnd(f, id) * 1.1, rnd(f, id + 0.5) * 1.1, rnd(f, id + 0.7) * 0.5]; }

function render(frame) {
  const f = frame, t = frame / TL.fps;
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
  const fv = st('fussel', 'vis', t, 0) && stage && scene !== 'endcard';
  show(fussel.g, fv);
  const fx = num('fussel', 'x', t), fy = num('fussel', 'y', t);
  if (fv) {
    const vy = (num('fussel', 'y', t + 0.04) - num('fussel', 'y', t - 0.04)) / 0.08;
    const stretch = clamp(Math.abs(vy) / 3500, 0, 0.18);
    const shake = st('fussel', 'shake', t, 0);
    const b = boil(f, 1);
    fussel.update({
      x: fx + b[0] + (shake ? Math.sin(t * 60) * 8 : 0), y: fy + b[1], r: num('fussel', 'r', t) + b[2] + (shake ? Math.sin(t * 47) * 9 : 0),
      s: num('fussel', 's', t), flip: num('fussel', 'flip', t) >= 0 ? 1 : -1, sx: 1 - stretch * 0.5, sy: 1 + stretch,
      t, thread: num('fussel', 'thread', t), lx: num('fussel', 'lx', t), ly: num('fussel', 'ly', t),
      sit: st('fussel', 'sit', t, 0), walk: st('fussel', 'walk', t, 0), air: Math.abs(vy) > 300,
      eyes: st('fussel', 'eyes', t, 'normal'), blink: blinkAt(t, 3.7, 0.4), amp: amp('F', t)
    });
  }
  // KURT
  const kv = st('kurt', 'vis', t, 0) && scene === 'halle';
  show(kurt.g, kv);
  if (kv) {
    const sc = st('kurt', 'screen', t, 'off');
    kurt.update({
      x: num('kurt', 'x', t), y: num('kurt', 'y', t), s: num('kurt', 's', t), r: 0, shake: num('kurt', 'shake', t), f, t,
      crank: integ('crank', t), cranking: !!st('kurt', 'crank', t, 0), screen: sc, sinceScreen: t - stT('kurt', 'screen', t),
      amp: amp('K', t), ansAmp: amp('A', t, 'kurt'), blink: blinkAt(t, 4.3, 1.1), steam: !!st('kurt', 'steam', t, 0)
    });
  }
  // Brösel
  const bv = st('broesel', 'vis', t, 0) && (scene === 'halle' || scene === 'endcard');
  show(broesel.g, bv);
  if (bv) {
    const b = boil(f, 2);
    const cranking = st('broesel', 'crank', t, 0) && scene === 'halle';
    const cA = integ('crank', t);
    broesel.update({
      x: num('broesel', 'x', t) + b[0], y: num('broesel', 'y', t) + b[1] - (cranking ? Math.abs(Math.sin(cA * Math.PI / 180)) * 6 : 0),
      r: num('broesel', 'r', t) + b[2], s: num('broesel', 's', t), flip: num('broesel', 'flip', t), t, f, ph: 0.3,
      lid: num('broesel', 'lid', t), wing: num('broesel', 'wing', t), walk: st('broesel', 'walk', t, 0), crank: cranking, crankA: cA,
      broom: st('broesel', 'broom', t, 0), sweep: st('broesel', 'sweep', t, 0), amp: amp('B', t), blink: blinkAt(t, 5.1, 2.2), px: -1
    });
  }
  // Gurrmann
  const gv = st('gurrmann', 'vis', t, 0) && stage && scene !== 'endcard';
  show(gurrmann.g, gv);
  if (gv) {
    const b = boil(f, 3);
    const fly = st('gurrmann', 'fly', t, 0);
    gurrmann.update({
      x: num('gurrmann', 'x', t) + b[0], y: num('gurrmann', 'y', t) + b[1] - (fly ? 30 + Math.sin(t * 9) * 12 : 0), r: num('gurrmann', 'r', t) + b[2],
      s: num('gurrmann', 's', t), flip: num('gurrmann', 'flip', t), t, f, ph: 1.1, lid: num('gurrmann', 'lid', t), wing: num('gurrmann', 'wing', t),
      walk: st('gurrmann', 'walk', t, 0), fly, amp: amp('G', t), blink: blinkAt(t, 4.0, 0.9), px: -1
    });
  }
  // Taube auf Fussels Kopf
  const sOn = st('sitter', 'on', t, 0) && scene === 'zug' && fv;
  show(sitter.g, sOn);
  if (sOn) {
    const u = clamp((t - stT('sitter', 'on', t)) / 0.7, 0, 1);
    const fs = num('fussel', 's', t);
    sitter.update({ x: lerp(1300, fx + 6, ease('out', u)), y: lerp(300, fy - 150 * fs, ease('out', u)), s: 0.55, flip: -1, t, f, ph: 2, fly: u < 1, lid: 0.6, wing: 0, amp: 0, blink: false, sit: u >= 1 });
  }
  // Ball (Idee)
  const balv = st('ball', 'vis', t, 0) && scene === 'halle';
  show(ball, balv);
  if (balv) setT(ball, `translate(${num('ball', 'x', t).toFixed(1)},${num('ball', 'y', t).toFixed(1)}) rotate(${(t * 400 % 360).toFixed(0)})`);
  // Zug
  const tv = st('train', 'vis', t, 0) && (scene === 'bahnhof' || scene === 'himmel');
  show(train.g, tv);
  if (tv) train.update({ x: num('train', 'x', t), y: num('train', 'y', t) + (st('train', 'wings', t, 0) ? Math.sin(t * 7) * 10 : 0), s: num('train', 's', t), r: num('train', 'r', t), doors: num('train', 'doors', t), wings: st('train', 'wings', t, 0), flap: st('train', 'flap', t, 0), t });

  updateCrowd(t, f, scene);
  updateCrumbs(t, f, scene, fx, fy);

  // Kulissen-Details
  if (scene === 'halle') {
    H.signN.textContent = String(st('sign', 'n', t, 3));
    const hh = (8 + t / 600) * 30, mm = (12 + t / 10) * 6;
    setT(H.hourHand, `rotate(${hh.toFixed(1)},1615,310)`); setT(H.minHand, `rotate(${mm.toFixed(1)},1615,310)`);
    const warn = st('warn', 'on', t, 0);
    setA(H.warnDome, 'fill', warn ? (f % 2 ? C.him : '#FF7A9A') : '#7A3046');
    show(H.warnRays, warn);
    if (warn) setT(H.warnRays, `rotate(${(t * 400 % 360).toFixed(0)},1500,66)`);
    setA(H.flash, 'opacity', warn ? (0.05 + 0.05 * Math.sin(t * 10)).toFixed(3) : 0);
    const bo = integ('belt', t);
    setA(H.beltTop, 'stroke-dashoffset', (-bo).toFixed(1));
    for (const r of H.rollers) { const a = bo / 13; setA(r, 'd', `M${(r._x - Math.cos(a) * 10).toFixed(1)} ${(630 - Math.sin(a) * 10).toFixed(1)}L${(r._x + Math.cos(a) * 10).toFixed(1)} ${(630 + Math.sin(a) * 10).toFixed(1)}`); }
    const running = st('belt', 'run', t, 0);
    H.flaps.forEach((fl, i) => setT(fl, running ? `rotate(${(Math.sin(t * 6 + i) * 6).toFixed(1)},${1781 + i * 31},470)` : ''));
    const cm = st('crowd', 'mode', t, 'off'), cu = t - stT('crowd', 'mode', t);
    H.cards.forEach((c, i) => {
      if ((cm === 'clock' && cu > 1.2 + i * 0.5) || cm === 'tobelt' || cm === 'belt' || (cm === 'off' && t > TL.cues.endcard_hold - 60 && st('sign', 'n', t, 3) === 0)) {
        const uu = cm === 'clock' ? cu - 1.2 - i * 0.5 : 3;
        setT(c, `translate(${(-uu * 80 - i * 20).toFixed(0)},${Math.min(640, uu * 300 + uu * uu * 200).toFixed(0)}) rotate(${(uu * 120 * (i % 2 ? 1 : -1)).toFixed(0)},1746,${254 + i * 42})`);
      } else setT(c, '');
    });
    const fe = ['burst', 'chaos', 'clock', 'tobelt'].includes(cm);
    show(featherG, fe);
    if (fe) feathers.forEach((e, i) => { const tt = (t * 0.3 + i / 10) % 1; setA(e, 'cx', (300 + i * 150 + Math.sin(t * 2 + i) * 60).toFixed(0)); setA(e, 'cy', (100 + tt * 800).toFixed(0)); setA(e, 'transform', `rotate(${(Math.sin(t * 3 + i) * 40).toFixed(0)},${300 + i * 150},${100 + tt * 800})`); });
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
    const fl = 0.85 + 0.15 * hash(f, 99);
    setA(H.ft1, 'opacity', fl.toFixed(2)); setA(H.ft2, 'opacity', fl.toFixed(2));
    setA(H.ftGlow, 'opacity', (0.6 + 0.2 * hash(f, 98)).toFixed(2));
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
    setA(H.b3, 'opacity', bt === 'kruemel2' || bt === 'einfahrt' ? (f % 6 < 4 ? 1 : 0.3) : 1);
    setT(H.secHand, `rotate(${((t * 6) % 360).toFixed(0)},1020,150)`);
    const a = amp('A', t);
    setT(H.horn, `translate(1812,200) scale(${(1 + a * 0.06).toFixed(3)}) translate(-1812,-200)`);
    show(H.hornWaves, a > 0);
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
      setT(H.cloudBrezel, `translate(${bx.toFixed(0)},300)`);
    }
  }
  if (scene === 'himmel') {
    setT(H.sunRays, `rotate(${(t * 10 % 360).toFixed(1)},1620,190)`);
    H.clouds.forEach((c) => { const k = c._k, sp = 60 + (k % 3) * 50, x = ((k * 330 - t * sp) % 2400 + 2400) % 2400 - 300; setT(c, `translate(${x.toFixed(0)},${(140 + (k * 97) % 560)}) scale(${(0.7 + (k % 3) * 0.25).toFixed(2)})`); });
    const sw = st('swarm', 'on', t, 0);
    show(H.swarm, sw);
    if (sw) H.minis.forEach((m, i) => {
      const a = t * 0.9 + i * Math.PI * 2 / H.minis.length;
      const x = 960 + Math.cos(a) * 640, y = 520 + Math.sin(a) * 300, dir = -Math.sin(a) >= 0 ? 1 : -1;
      setT(m.g, `translate(${x.toFixed(0)},${y.toFixed(0)}) scale(${(dir * (0.8 + 0.25 * Math.sin(a))).toFixed(3)},${(0.8 + 0.25 * Math.sin(a)).toFixed(3)})`);
      setT(m.w, `rotate(${(Math.sin(t * 9 + i) * 20).toFixed(0)},0,-30)`);
      m.g.parentNode.appendChild && (Math.sin(a) > 0 ? H.swarm.appendChild(m.g) : H.swarm.insertBefore(m.g, H.brezel));
    });
  }
  if (scene === 'endcard') {
    const u = t - s0;
    H.endFussel.update({ x: 1180, y: 540, s: 1.15, r: Math.sin(t * 2) * 3, flip: 1, sx: 1, sy: 1, t, thread: 1, lx: 0, ly: 0, sit: 0, walk: 0, air: 0, eyes: 'happy', blink: false, amp: 0 });
    setT(H.endTitle, `translate(0,${((1 - smooth(u / 0.6)) * 300).toFixed(0)})`);
  }

  // Iris und Abblende
  const ir = num('iris', 'r', t);
  if (ir < 1150) { setA(irisPath, 'd', `M0 0H1920V1080H0Z M${960 - ir} 540a${ir} ${ir} 0 1 0 ${2 * ir} 0a${ir} ${ir} 0 1 0 ${-2 * ir} 0Z`); show(irisPath, true); }
  else show(irisPath, false);
  setA(fadeRect, 'opacity', num('fade', 'a', t).toFixed(3));
}

window.init = function (tl) { TL = tl; buildIntegrals(); return Math.round(tl.total * tl.fps); };
window.render = render;
