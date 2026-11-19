"""Icon library: 16,000+ open-source icons as filled outlines in a 256 x 256 box.

Sets (all free for commercial use, no credit needed in the logo): Phosphor (MIT; the original 1,494 names stay as
they are, so older projects open unchanged), Tabler (MIT), Lucide (ISC), Material Symbols (Apache 2.0), Iconoir (MIT),
Heroicons (MIT) and Bootstrap Icons (MIT). Line icons were turned into filled shapes, so every icon can be filled,
cut out and exported like any logo shape. Icons of the other sets have ids like "tabler:pizza".
"""
import gzip
import json
import os
import re

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainterPath

HERE = os.path.dirname(os.path.abspath(__file__))
SETS = [("phosphor", "Phosphor"), ("tabler", "Tabler"), ("lucide", "Lucide"), ("material", "Material"),
        ("iconoir", "Iconoir"), ("heroicons", "Heroicons"), ("bootstrap", "Bootstrap")]
WEIGHTS = [("fill", "Solid"), ("bold", "Bold outline"), ("regular", "Outline"), ("light", "Light outline"), ("thin", "Thin outline")]
_NEAR = {"fill": ("fill", "bold", "regular", "light", "thin"), "bold": ("bold", "regular", "light", "thin", "fill"),
         "regular": ("regular", "bold", "light", "thin", "fill"), "light": ("light", "regular", "thin", "bold", "fill"),
         "thin": ("thin", "light", "regular", "bold", "fill")}
_DB = None
_IDX = {}
_CACHE = {}
_TOK = re.compile(r"[MLCZ]|-?\d*\.?\d+")


def base(name):
    """'tabler:pizza-slice' -> 'pizza-slice'"""
    return name.rsplit(":", 1)[-1]


def set_of(name):
    return name.split(":", 1)[0] if ":" in name else "phosphor"


def db():
    global _DB
    if _DB is None:
        _DB = []
        with open(os.path.join(HERE, "data", "icons.json"), encoding="utf-8") as f:
            for i in json.load(f)["icons"]:                 # Phosphor solid + bold (the original library)
                _DB.append({"n": i["n"], "t": i["t"], "c": i.get("c", ""), "s": "phosphor", "w": {"fill": i["f"], "bold": i["b"]}})
        _IDX.update({i["n"]: i for i in _DB})
        folder = os.path.join(HERE, "data", "icons")
        for sid, _label in SETS:
            p = os.path.join(folder, f"{sid}.json.gz")
            if not os.path.isfile(p):
                continue
            with gzip.open(p, "rt", encoding="utf-8") as f:
                items = json.load(f)
            for i in items:
                if sid == "phosphor" and i["n"] in _IDX:     # more weights for the original Phosphor icons
                    _IDX[i["n"]]["w"].update(i["w"])
                    continue
                e = {"n": i["n"], "t": i.get("t", ""), "c": i.get("c", ""), "s": sid, "w": i["w"]}
                _DB.append(e)
                _IDX[e["n"]] = e
        for i in _DB:
            i["words"] = set(re.findall(r"[a-z]+", (base(i["n"]).replace("-", " ").replace("_", " ") + " " + i["t"]).lower()))
    return _DB


def count():
    return len(db())


def get(name):
    db()
    return _IDX.get(name)


def weights(name):
    ic = get(name)
    return list(ic["w"]) if ic else []


def _build(d):
    p = QPainterPath()
    t = _TOK.findall(d)
    i = 0
    while i < len(t):
        c = t[i]
        if c == "M":
            p.moveTo(float(t[i + 1]), float(t[i + 2])); i += 3
        elif c == "L":
            p.lineTo(float(t[i + 1]), float(t[i + 2])); i += 3
        elif c == "C":
            p.cubicTo(*(float(x) for x in t[i + 1:i + 7])); i += 7
        elif c == "Z":
            p.closeSubpath(); i += 1
        else:
            i += 1
    p.setFillRule(Qt.WindingFill)
    return p


def path(name, weight="fill"):
    """icon as QPainterPath in a 256 x 256 box (nonzero fill rule); the nearest style when this one is missing"""
    ic = get(name)
    if not ic:
        return QPainterPath()
    w = next((x for x in _NEAR.get(weight, _NEAR["fill"]) if x in ic["w"]), next(iter(ic["w"])))
    k = (name, w)
    if k not in _CACHE:
        _CACHE[k] = _build(ic["w"][w])
    return QPainterPath(_CACHE[k])


def search(query, limit=200, icon_set=None):
    db()
    pool = [i for i in _DB if icon_set in (None, "all") or i["s"] == icon_set]
    q = [w for w in re.findall(r"[a-z]+", query.lower())]
    if not q:
        return [i["n"] for i in pool][:limit]
    scored = []
    for i in pool:
        s = 0
        b = base(i["n"])
        parts = b.split("-")
        for w in q:
            if w == b:
                s += 10
            elif w in parts:
                s += 6
            elif w in b:
                s += 4
            if w in i["words"]:
                s += 3
            elif any(x.startswith(w) for x in i["words"]):
                s += 1
        if s:
            scored.append((-s, i["s"] != "phosphor", len(b), i["n"]))
    scored.sort()
    return [x[-1] for x in scored[:limit]]
