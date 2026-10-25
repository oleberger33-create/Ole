"""Prüft das erzeugte Datapack gegen die echten Spieldaten mehrerer Minecraft-Versionen.

Braucht die Zusammenfassungen aus github.com/misode/mcmeta (Zweige <version>-summary):
    git clone --depth 1 --branch 26.3-summary https://github.com/misode/mcmeta mcmeta-26.3-summary

Aufruf:  python3 pruefen.py <datapack-ordner> <mcmeta-elternordner>

Geprüft wird jede Zeile jeder Funktion (Makrozeilen mit Beispielwerten): Befehlsaufbau entlang des echten Befehlsbaums,
Blockzustände (Name, Eigenschaften, Werte), Register-IDs (Wesen, Effekte, Partikel, Geräusche,
Verzauberungen, Berufe, Gegenstände), Zielauswahl-Parameter, Textkomponenten und Funktionsaufrufe.
"""
import json
import os
import re
import sys

PACK, MCMETA = sys.argv[1], sys.argv[2]
LEGACY = "legacy_1_21_5"
# Version -> gilt das Overlay?
VERSIONEN = {"1.21.5": True, "1.21.10": True, "1.21.11": False, "26.3": False}

SELEKTOR_SCHLUESSEL = {"x", "y", "z", "dx", "dy", "dz", "distance", "scores", "tag", "team", "limit",
                       "sort", "level", "gamemode", "name", "x_rotation", "y_rotation", "type", "nbt",
                       "advancements", "predicate"}
TEXT_SCHLUESSEL = {"text", "translate", "score", "color", "bold", "italic", "underlined",
                   "strikethrough", "obfuscated", "click_event", "hover_event", "extra", "with",
                   "shadow_color", "font", "insertion"}
ZAHL = re.compile(r"^-?(\d+\.?\d*|\.\d+)$")
KOORD = re.compile(r"^([~^](-?(\d+\.?\d*|\.\d+))?|-?(\d+\.?\d*|\.\d+))$")


def tokens(zeile):
    out, akt, tiefe, quote = [], "", 0, None
    i = 0
    while i < len(zeile):
        c = zeile[i]
        if quote:
            akt += c
            if c == "\\":
                akt += zeile[i + 1]
                i += 1
            elif c == quote:
                quote = None
        elif c in "\"'":
            quote = c
            akt += c
        elif c in "[{(":
            tiefe += 1
            akt += c
        elif c in "]})":
            tiefe -= 1
            akt += c
        elif c == " " and tiefe == 0:
            if akt:
                out.append(akt)
            akt = ""
        else:
            akt += c
        i += 1
    if akt:
        out.append(akt)
    if tiefe != 0 or quote:
        raise ValueError("Klammern oder Anführungszeichen nicht geschlossen")
    return out


class Pruefer:
    def __init__(self, version, funktionen, tags):
        basis = os.path.join(MCMETA, f"mcmeta-{version}-summary")
        self.version = version
        self.baum = json.load(open(os.path.join(basis, "commands", "data.json")))
        self.bloecke = json.load(open(os.path.join(basis, "blocks", "data.json")))
        self.reg = {k: set(v) for k, v in json.load(open(os.path.join(basis, "registries", "data.json"))).items()}
        self.lang = set(json.load(open(os.path.join(basis, "assets", "lang", "data.json")))["en_us"])
        self.funktionen = funktionen
        self.tags = tags
        self.fehler = []

    # ---------------------------------------------------------- Einzelprüfungen
    def id_ok(self, registry, wert):
        name = wert.split(":", 1)[1] if ":" in wert else wert
        return name in self.reg.get(registry, set())

    def blockzustand(self, tok):
        m = re.match(r"^(#?)([a-z0-9_.:/-]+)(\[[^\]]*\])?(\{.*\})?$", tok)
        if not m:
            return f"Blockzustand unlesbar: {tok}"
        if m.group(1):
            return None if m.group(2) in ("minecraft:replaceable",) else f"unbekannter Blocktag {tok}"
        name = m.group(2).split(":", 1)[-1]
        if name not in self.bloecke:
            return f"unbekannter Block {name}"
        props = self.bloecke[name][0]
        if m.group(3):
            for paar in m.group(3)[1:-1].split(","):
                if not paar:
                    continue
                k, v = paar.split("=")
                if k not in props:
                    return f"{name}: Eigenschaft {k} gibt es nicht"
                if v not in props[k]:
                    return f"{name}: {k}={v} ungültig (erlaubt {props[k]})"
        return None

    def selektor(self, tok, nur_spieler, einzeln):
        if not tok.startswith("@"):
            return None if re.match(r"^[#A-Za-z0-9_.+-]+$", tok) else f"Name unlesbar: {tok}"
        if tok[1] not in "aeprsn":
            return f"Selektor {tok[:2]} unbekannt"
        if nur_spieler and tok.startswith("@e") and "type=minecraft:player" not in tok:
            return f"hier sind nur Spieler erlaubt: {tok}"
        if einzeln and tok[:2] in ("@a", "@e") and "limit=1" not in tok:
            return f"hier ist nur ein einzelnes Ziel erlaubt: {tok}"
        if len(tok) > 2:
            if not (tok[2] == "[" and tok.endswith("]")):
                return f"Selektor unlesbar: {tok}"
            for teil in tokens_komma(tok[3:-1]):
                k, _, v = teil.partition("=")
                if k not in SELEKTOR_SCHLUESSEL:
                    return f"Selektor-Schlüssel {k} unbekannt"
                if k == "type":
                    v = v.lstrip("!")
                    if v.startswith("#"):
                        if v[1:] not in self.tags:
                            return f"Wesen-Tag {v} fehlt im Datapack"
                    elif not self.id_ok("entity_type", v):
                        return f"Wesen {v} unbekannt"
                if k == "gamemode" and v.lstrip("!") not in ("survival", "creative", "adventure", "spectator"):
                    return f"Spielmodus {v} unbekannt"
                if k in ("x", "y", "z", "dx", "dy", "dz") and not ZAHL.match(v):
                    return f"{k}={v} ist keine Zahl"
        return None

    def text(self, tok):
        try:
            obj = json.loads(tok)
        except json.JSONDecodeError as e:
            return f"Textkomponente kein gültiges JSON/SNBT: {e}"
        return self.text_obj(obj)

    def text_obj(self, obj):
        if isinstance(obj, str):
            return None
        if isinstance(obj, list):
            for o in obj:
                f = self.text_obj(o)
                if f:
                    return f
            return None
        unbekannt = set(obj) - TEXT_SCHLUESSEL
        if unbekannt:
            return f"Textkomponente: unbekannte Schlüssel {unbekannt}"
        if "translate" in obj and obj["translate"].startswith("enchantment.minecraft."):
            if not self.id_ok("enchantment", obj["translate"].rsplit(".", 1)[1]):
                return f"Übersetzungsschlüssel {obj['translate']}: Verzauberung fehlt in {self.version}"
        if "translate" in obj and obj["translate"].startswith(("item.minecraft.", "block.minecraft.")):
            if obj["translate"] not in self.lang:
                return f"Übersetzungsschlüssel {obj['translate']} gibt es in {self.version} nicht"
        if "click_event" in obj:
            ce = obj["click_event"]
            if ce.get("action") != "run_command" or "command" not in ce:
                return f"click_event falsch aufgebaut: {ce}"
        if "hover_event" in obj:
            he = obj["hover_event"]
            if he.get("action") != "show_text" or "value" not in he:
                return f"hover_event falsch aufgebaut: {he}"
        return None

    def nbt_inhalt(self, tok):
        """Register-IDs in Wesen-NBT prüfen (Verzauberungen, Berufe, Gegenstände, Textkomponenten)."""
        for name in re.findall(r'"minecraft:stored_enchantments":\{"minecraft:([a-z_]+)"', tok):
            if not self.id_ok("enchantment", name):
                return f"Verzauberung {name} gibt es in {self.version} nicht"
        for name in re.findall(r'profession:"minecraft:([a-z_]+)"', tok):
            if not self.id_ok("villager_profession", name):
                return f"Beruf {name} unbekannt"
        for name in re.findall(r'type:"minecraft:([a-z_]+)"', tok):
            if not self.id_ok("villager_type", name):
                return f"Dorfbewohner-Typ {name} unbekannt"
        for name in re.findall(r'\bid:"minecraft:([a-z_]+)"', tok):
            if not self.id_ok("item", name):
                return f"Gegenstand {name} unbekannt"
        for feld in ("text", "CustomName"):
            for m in re.finditer(r"\b%s:" % feld, tok):
                start = m.end()
                f = self.text(klammer_ausschnitt(tok, start))
                if f:
                    return f"{feld}: {f}"
        return None

    # ---------------------------------------------------------- Argumente
    def argument(self, knoten, toks, i):
        """Gibt die Zahl verbrauchter Tokens zurück oder (None, fehler)."""
        p = knoten["parser"]
        props = knoten.get("properties", {})
        rest = len(toks) - i
        mehr = {"minecraft:block_pos": 3, "minecraft:vec3": 3, "minecraft:column_pos": 2,
                "minecraft:vec2": 2, "minecraft:rotation": 2}.get(p, 1)
        if p in ("minecraft:message",) or (p == "brigadier:string" and props.get("type") == "greedy"):
            return rest, None
        if rest < mehr:
            return None, "zu wenige Argumente"
        t = toks[i:i + mehr]
        if mehr > 1 or p == "minecraft:angle":
            for k in t:
                if not KOORD.match(k):
                    return None, f"Koordinate {k} ungültig"
                if p in ("minecraft:block_pos", "minecraft:column_pos") and not k.startswith(("~", "^")) \
                        and not re.match(r"^-?\d+$", k):
                    return None, f"Blockkoordinate {k} muss ganzzahlig sein"
            return mehr, None
        k = t[0]
        if p == "brigadier:integer":
            if not re.match(r"^-?\d+$", k):
                return None, f"{k} ist keine Ganzzahl"
            v = int(k)
        elif p in ("brigadier:float", "brigadier:double"):
            if not ZAHL.match(k):
                return None, f"{k} ist keine Zahl"
            v = float(k)
        elif p == "brigadier:bool":
            return (1, None) if k in ("true", "false") else (None, f"{k} ist kein Wahrheitswert")
        elif p in ("minecraft:block_state", "minecraft:block_predicate"):
            f = self.blockzustand(k)
            return (None, f) if f else (1, None)
        elif p == "minecraft:entity" or p == "minecraft:score_holder" or p == "minecraft:game_profile":
            f = self.selektor(k, props.get("type") == "players", props.get("amount") == "single")
            return (None, f) if f else (1, None)
        elif p in ("minecraft:resource", "minecraft:resource_or_tag", "minecraft:resource_key"):
            reg = props["registry"].split(":")[1]
            if k.startswith("#"):
                return 1, None
            return (1, None) if self.id_ok(reg, k) else (None, f"{k} fehlt im Register {reg}")
        elif p in ("minecraft:item_stack", "minecraft:item_predicate"):
            if k == "*" or k.startswith("#"):
                return 1, None
            name = re.match(r"^[a-z0-9_.:/-]+", k).group(0)
            return (1, None) if self.id_ok("item", name) else (None, f"Gegenstand {name} unbekannt")
        elif p == "minecraft:particle":
            return (1, None) if self.id_ok("particle_type", k) else (None, f"Partikel {k} unbekannt")
        elif p == "minecraft:component":
            f = self.text(k)
            return (None, f) if f else (1, None)
        elif p == "minecraft:nbt_compound_tag":
            if not (k.startswith("{") and k.endswith("}")):
                return None, "NBT muss mit { beginnen"
            f = self.nbt_inhalt(k)
            return (None, f) if f else (1, None)
        elif p == "minecraft:function":
            name = k.lstrip("#")
            if k.startswith("#") or name in self.funktionen:
                return 1, None
            return None, f"Funktion {k} gibt es nicht"
        elif p == "minecraft:heightmap":
            ok = k in ("world_surface", "motion_blocking", "motion_blocking_no_leaves", "ocean_floor")
            return (1, None) if ok else (None, f"Höhenkarte {k} unbekannt")
        elif p == "minecraft:gamemode":
            ok = k in ("survival", "creative", "adventure", "spectator")
            return (1, None) if ok else (None, f"Spielmodus {k} unbekannt")
        elif p == "minecraft:dimension":
            return (1, None) if k in ("minecraft:overworld", "minecraft:the_nether", "minecraft:the_end") \
                else (None, f"Dimension {k} unbekannt")
        elif p == "minecraft:time":
            return (1, None) if re.match(r"^\d+(\.\d+)?[tsd]?$", k) else (None, f"Zeit {k} ungültig")
        elif p == "minecraft:objective_criteria":
            if k in ("dummy", "trigger", "deathCount", "health"):
                return 1, None
            m = re.match(r"^minecraft\.custom:minecraft\.([a-z_]+)$", k)
            if m and m.group(1) in self.reg.get("custom_stat", set()):
                return 1, None
            return None, f"Kriterium {k} unbekannt"
        elif p == "minecraft:objective":
            return (1, None) if re.match(r"^[A-Za-z0-9_.+-]{1,16}$", k) else (None, f"Ziel {k} ungültig")
        elif p == "minecraft:operation":
            return (1, None) if k in ("=", "+=", "-=", "*=", "/=", "%=", "<", ">", "><") \
                else (None, f"Operation {k} unbekannt")
        elif p == "minecraft:int_range":
            return (1, None) if re.match(r"^-?\d*(\.\.)?-?\d*$", k) else (None, f"Bereich {k} ungültig")
        else:
            return 1, None
        lo, hi = props.get("min"), props.get("max")
        if (lo is not None and v < lo) or (hi is not None and v > hi):
            return None, f"{k} außerhalb von [{lo}, {hi}]"
        return 1, None

    # ---------------------------------------------------------- Baum ablaufen
    def knoten_zu(self, pfad):
        n = self.baum
        for teil in pfad:
            n = n["children"][teil]
        return n

    def weiter(self, knoten, toks, i, fehler):
        if "redirect" in knoten:
            if i == len(toks):
                return knoten.get("executable", False)
            return self.passt(self.knoten_zu(knoten["redirect"]), toks, i, fehler)
        if knoten["type"] == "literal" and not knoten.get("children") and not knoten.get("executable"):
            return self.passt(self.baum, toks, i, fehler)  # execute … run
        if i == len(toks):
            return knoten.get("executable", False)
        return self.passt(knoten, toks, i, fehler)

    def passt(self, knoten, toks, i, fehler):
        for name, kind in knoten.get("children", {}).items():
            if kind["type"] == "literal":
                if toks[i] == name and self.weiter(kind, toks, i + 1, fehler):
                    return True
            else:
                n, f = self.argument(kind, toks, i)
                if n is None:
                    fehler.append(f"{name}: {f}")
                    continue
                if self.weiter(kind, toks, i + n, fehler):
                    return True
        return False

    def zeile(self, text):
        if text.startswith("$"):
            # Makrozeile: Platzhalter durch Beispielwerte ersetzen
            text = re.sub(r"\$\(dim\)", "minecraft:overworld", text[1:])
            text = re.sub(r"\$\([a-z_]+\)", "0", text)
        toks = tokens(text)
        fehler = []
        if not self.passt(self.baum, toks, 0, fehler):
            return "; ".join(dict.fromkeys(fehler)) or "Befehl passt nicht zum Befehlsbaum"
        return None


def tokens_komma(s):
    out, akt, tiefe = [], "", 0
    for c in s:
        if c in "{[":
            tiefe += 1
        elif c in "}]":
            tiefe -= 1
        if c == "," and tiefe == 0:
            out.append(akt)
            akt = ""
        else:
            akt += c
    if akt:
        out.append(akt)
    return out


def klammer_ausschnitt(s, start):
    """Schneidet ab start einen kompletten JSON-Wert ({…}, […] oder "…") heraus."""
    if s[start] == '"':
        i = start + 1
        while s[i] != '"':
            i += 2 if s[i] == "\\" else 1
        return s[start:i + 1]
    tiefe, quote = 0, False
    for i in range(start, len(s)):
        c = s[i]
        if quote:
            if c == "\\":
                continue
            if c == '"' and s[i - 1] != "\\":
                quote = False
        elif c == '"':
            quote = True
        elif c in "{[":
            tiefe += 1
        elif c in "}]":
            tiefe -= 1
            if tiefe == 0:
                return s[start:i + 1]
    raise ValueError("Klammer nicht geschlossen")


def lade_funktionen(wurzel):
    out = {}
    basis = os.path.join(wurzel, "data")
    for ns in os.listdir(basis):
        fdir = os.path.join(basis, ns, "function")
        if not os.path.isdir(fdir):
            continue
        for d, _, files in os.walk(fdir):
            for f in files:
                if f.endswith(".mcfunction"):
                    rel = os.path.relpath(os.path.join(d, f), fdir)[:-11].replace(os.sep, "/")
                    out[f"{ns}:{rel}"] = open(os.path.join(d, f), encoding="utf-8").read()
    return out


def main():
    basis = lade_funktionen(PACK)
    legacy = lade_funktionen(os.path.join(PACK, LEGACY)) if os.path.isdir(os.path.join(PACK, LEGACY)) else {}
    tags = set()
    tagdir = os.path.join(PACK, "data")
    for ns in os.listdir(tagdir):
        for typ in ("entity_type",):
            d = os.path.join(tagdir, ns, "tags", typ)
            if os.path.isdir(d):
                tags |= {f"{ns}:{f[:-5]}" for f in os.listdir(d)}
    meta = json.load(open(os.path.join(PACK, "pack.mcmeta"), encoding="utf-8"))
    p = meta["pack"]
    assert p["min_format"] == p["pack_format"] == p["supported_formats"][0], "pack.mcmeta: Formate passen nicht"
    assert p["max_format"] == p["supported_formats"][1], "pack.mcmeta: Formate passen nicht"
    fehler_gesamt = 0
    for version, mit_overlay in VERSIONEN.items():
        wirksam = dict(basis)
        if mit_overlay:
            wirksam.update(legacy)
        pr = Pruefer(version, set(wirksam), tags)
        zeilen = 0
        for name, inhalt in sorted(wirksam.items()):
            for nr, z in enumerate(inhalt.splitlines(), 1):
                if not z.strip() or z.startswith("#"):
                    continue
                zeilen += 1
                try:
                    f = pr.zeile(z)
                except Exception as e:  # noqa: BLE001
                    f = f"Prüfer-Fehler: {e!r}"
                if f:
                    fehler_gesamt += 1
                    if fehler_gesamt <= 40:
                        print(f"[{version}] {name}:{nr}: {f}\n    {z[:220]}")
        print(f"{version}: {len(wirksam)} Funktionen, {zeilen} Befehle geprüft")
    for pfad in ["data/minecraft/tags/function/load.json", "data/minecraft/tags/function/tick.json"]:
        for v in json.load(open(os.path.join(PACK, pfad)))["values"]:
            assert v in basis, f"{pfad}: {v} fehlt"
    print("FEHLER:", fehler_gesamt)
    sys.exit(1 if fehler_gesamt else 0)


if __name__ == "__main__":
    main()
