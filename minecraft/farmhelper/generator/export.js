const fs = require("fs");
const dir = process.argv[2];
let src = fs.readFileSync(dir + "/engine.js", "utf8");
src = src.slice(0, src.indexOf("/* ---------- Kleine Mathe"));
src += fs.readFileSync(dir + "/builds.js", "utf8") + "\n" + fs.readFileSync("farms_src.js", "utf8") + "\n" + fs.readFileSync(dir + "/meta.js", "utf8");
src += "\nmodule.exports = {BL, BUILDS, FARMS, META, Bau};";
fs.writeFileSync("bundle.js", src);
const {BL, BUILDS, FARMS, META, Bau} = require("./bundle.js");
const out = [];
for (const f of FARMS) {
  const b = new Bau(); BUILDS[f.id](b);
  const endZustand = b.state(b.steps.length - 1);
  // Stellen, die ein Schritt ausdrücklich leer macht und die im fertigen Bau leer bleiben (Löcher, Schächte, Räume)
  const luft = k => { const m = new Map(); for (const [st,x,y,z,blk] of b.ops) if (st === k && !blk && (!endZustand.has(x+","+y+","+z) || endZustand.get(x+","+y+","+z).id === "flowing_water")) m.set(x+","+y+","+z, {x,y,z}); return [...m.values()]; };
  const steps = b.steps.map((s, k) => ({text: s.text, luft: luft(k), added: [...b.added(k).values()].map(x => ({x:x.x, y:x.y, z:x.z, id:x.id, p:x.p, ent:!!x.ent}))}));
  const fertig = [...b.state(b.steps.length - 1).values()].map(x => ({x:x.x, y:x.y, z:x.z, id:x.id, p:x.p, ent:!!x.ent}));
  out.push({id:f.id, name:f.name, cat:f.cat, diff:f.diff, out:f.out, where:f.where, afk:f.afk, why:f.why, help:f.help, verified:!!f.verified, meta:META[f.id]||null, steps, fertig});
}
fs.writeFileSync("plaene.json", JSON.stringify(out));
const ids = new Set(); out.forEach(f => f.fertig.forEach(b => ids.add(b.id)));
console.log(out.length, "Farmen;", [...ids].join(" "));
