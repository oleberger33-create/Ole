"""Liest Logo und Fussel aus den Markendateien und schreibt assets.js für den Renderer."""
import json, os, re
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "assets")
logo = open(os.path.join(ROOT, "logo", "logo-horizontal.svg")).read()
w = float(re.search(r'viewBox="0 0 ([\d.]+)', logo).group(1))
fus = re.search(r'<g transform="translate\(0 42\)">(.*?)</g>', logo, re.S).group(1)
thread = re.search(r'<path d="([^"]+)" fill="none" stroke="#E33D6E" stroke-width="7"', logo).group(1)
word = re.search(r'<path d="([^"]+)" fill="#1D1A2B"/>', logo).group(1)
ball = logo[logo.index('<circle', logo.index(word)):logo.rindex('</svg>')]
bx, by = map(float, re.search(r'<circle cx="([\d.]+)" cy="([\d.]+)"', ball).groups())
fussel = open(os.path.join(ROOT, "figuren", "fussel.svg")).read()
fur = re.search(r'<path d="([^"]+)" fill="#E33D6E"/>', fussel).group(1)
out = "window.LOGO=" + json.dumps(dict(w=w, fussel=fus, thread=thread, word=word, ball=ball, bx=bx, by=by)) + ";\nwindow.FUR=" + json.dumps(fur) + ";\n"
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets.js"), "w").write(out)
print("assets.js", len(out), "Zeichen, Logo-Breite", w)
