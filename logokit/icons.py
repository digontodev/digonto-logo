"""Icon library: Phosphor Icons (MIT licence, 1,494 icons, 'fill' and 'bold' weights), stored as compact paths."""
import json
import os
import re

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainterPath

HERE = os.path.dirname(os.path.abspath(__file__))
_DB = None
_IDX = {}
_CACHE = {}
_TOK = re.compile(r"[MLCZ]|-?\d*\.?\d+")


def db():
    global _DB
    if _DB is None:
        with open(os.path.join(HERE, "data", "icons.json"), encoding="utf-8") as f:
            _DB = json.load(f)["icons"]
        for i in _DB:
            i["words"] = set(re.findall(r"[a-z]+", (i["n"].replace("-", " ") + " " + i["t"]).lower()))
            _IDX[i["n"]] = i
    return _DB


def get(name):
    db()
    return _IDX.get(name)


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
    """icon as QPainterPath in a 256 x 256 box (nonzero fill rule)"""
    k = (name, weight)
    if k not in _CACHE:
        ic = get(name)
        if not ic:
            return QPainterPath()
        _CACHE[k] = _build(ic["b" if weight == "bold" else "f"])
    return QPainterPath(_CACHE[k])


def search(query, limit=200):
    db()
    q = [w for w in re.findall(r"[a-z]+", query.lower())]
    if not q:
        return [i["n"] for i in _DB][:limit]
    scored = []
    for i in _DB:
        s = 0
        for w in q:
            if w in i["n"].split("-"):
                s += 6
            elif w in i["n"]:
                s += 4
            if w in i["words"]:
                s += 3
            elif any(x.startswith(w) for x in i["words"]):
                s += 1
        if s:
            scored.append((-s, i["n"]))
    scored.sort()
    return [n for _, n in scored[:limit]]
