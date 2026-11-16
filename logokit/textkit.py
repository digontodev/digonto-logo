"""Fonts and text as vector outlines. The bundled open-source fonts are loaded into Qt; text comes out as paths,
so exported logos never depend on fonts being installed."""
import json
import math
import os

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QFont, QFontDatabase, QFontMetricsF, QPainterPath, QTransform

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data", "fonts")
with open(os.path.join(HERE, "data", "fonts.json"), encoding="utf-8") as _f:
    FONTS = json.load(_f)
BY_ID = {f["id"]: f for f in FONTS}
CATS = [("sans", "Sans-serif"), ("serif", "Serif"), ("display", "Display"), ("script", "Script"), ("slab", "Slab"), ("mono", "Mono")]
_FAM = {}
REF = 100.0                                      # outlines are made at 100 px, then scaled


def family(font_id):
    f = BY_ID.get(font_id) or BY_ID["montserrat"]
    if f["id"] not in _FAM:
        fam = None
        for k in ("regular", "bold"):
            if k in f:
                i = QFontDatabase.addApplicationFont(os.path.join(DATA, f[k]))
                if i >= 0 and fam is None:
                    fam = (QFontDatabase.applicationFontFamilies(i) or [None])[0]
        _FAM[f["id"]] = fam or "Sans Serif"
    return _FAM[f["id"]]


def has_bold(font_id):
    return "bold" in (BY_ID.get(font_id) or {})


def qfont(font_id, bold=False, track=0.0):
    f = QFont(family(font_id))
    f.setPixelSize(int(REF))
    f.setWeight(QFont.Bold if (bold and has_bold(font_id)) else QFont.Normal)
    f.setStyleStrategy(QFont.PreferOutline)
    f.setHintingPreference(QFont.PreferNoHinting)
    if track:
        f.setLetterSpacing(QFont.AbsoluteSpacing, track * REF)
    return f


def apply_case(t, case):
    if case == "upper":
        return t.upper()
    if case == "lower":
        return t.lower()
    if case == "title":
        return " ".join(w[:1].upper() + w[1:].lower() for w in t.split(" "))
    return t


def metrics(font_id, bold=False):
    m = QFontMetricsF(qfont(font_id, bold))
    return {"cap": m.capHeight() / REF or 0.7, "xh": m.xHeight() / REF or 0.5, "asc": m.ascent() / REF, "desc": m.descent() / REF}


def run_path(text, font_id, bold, size, track=0.0):
    """(path with baseline at y = 0 and the left edge at x = 0, advance width). size = em height in scene units"""
    f = qfont(font_id, bold, track)
    p = QPainterPath()
    p.addText(0, 0, f, text)
    k = size / REF
    adv = (QFontMetricsF(f).horizontalAdvance(text)) * k
    out = QTransform().scale(k, k).map(p)
    out.setFillRule(Qt.WindingFill)
    return out, adv


def text_runs(runs, size, track=0.0):
    """runs = [(text, font_id, bold, role)] laid out left to right. Returns ([(path, role)], ink rect)"""
    x, out = 0.0, []
    ink = None
    for text, fid, bold, role in runs:
        if not text:
            continue
        p, adv = run_path(text, fid, bold, size, track)
        p = QTransform().translate(x, 0).map(p)
        r = p.boundingRect()
        if not r.isEmpty():
            ink = r if ink is None else ink.united(r)
        out.append((p, role))
        x += adv
    return out, ink or QRectF(0, 0, 0, 0)


def text_width(text, font_id, bold, size, track=0.0):
    p, _ = run_path(text, font_id, bold, size, track)
    return p.boundingRect().width()


def arc_text(text, font_id, bold, size, radius, center_deg, track=0.0, bottom=False):
    """text along a circle around (0,0). Top text reads clockwise, centered on center_deg (-90 = top).
    bottom=True: text on the lower arc, upright (reads left to right), baseline on the circle"""
    f = qfont(font_id, bold)
    m = QFontMetricsF(f)
    k = size / REF
    adv = [m.horizontalAdvance(c) * k + track * size for c in text]
    total = sum(adv) - track * size
    out = QPainterPath()
    pos = -total / 2
    for c, a in zip(text, adv):
        if c != " ":
            g = QPainterPath()
            g.addText(0, 0, qfont(font_id, bold), c)
            gw = m.horizontalAdvance(c)
            mid = pos + a / 2 - (track * size) / 2
            ang = mid / radius                       # radians along the arc
            tr = QTransform()
            if not bottom:
                theta = math.radians(center_deg) + ang
                tr.translate(radius * math.cos(theta), radius * math.sin(theta))
                tr.rotate(math.degrees(theta) + 90)
            else:
                theta = math.radians(center_deg) - ang
                tr.translate(radius * math.cos(theta), radius * math.sin(theta))
                tr.rotate(math.degrees(theta) - 90)
            tr.scale(k, k)
            tr.translate(-gw / 2, 0)
            out.addPath(tr.map(g))
        pos += a
    out.setFillRule(Qt.WindingFill)
    return out
