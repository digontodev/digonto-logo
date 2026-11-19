"""Design of the name text: slant, width, bend (text on a curve), outline styles, cut letters, shadows and gradient.

apply(s, items, size) takes the name as [(path, paint)] (baseline at y = 0) and returns ([(path, paint)], ink rect).
All settings live in s["font"]: slant (degrees), stretch (1.0 = normal), bend (-1 .. 1), nstyle, cut, shadow, ngrad.
"""
import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QPainterPath, QPainterPathStroker, QPolygonF, QTransform

from . import palettes, textkit
from .scene import Grad

STYLES = [("solid", "Solid"), ("outline", "Outline"), ("double", "Double outline"), ("inline", "Inline")]
CUTS = [("none", "None"), ("stripe", "Stripe through"), ("slash", "Diagonal cut"), ("lines", "Retro lines"), ("half", "Two-color halves"),
        ("top", "Cut top")]
SHADOWS = [("none", "None"), ("drop", "Drop shadow"), ("long", "Long shadow"), ("3d", "3D block"), ("glow", "Soft outline")]


def _stroke(p, w, cap=Qt.RoundCap, join=Qt.RoundJoin):
    s = QPainterPathStroker()
    s.setWidth(w)
    s.setCapStyle(cap)
    s.setJoinStyle(join)
    return s.createStroke(p)


def _solid(p):
    q = QPainterPath(p)
    q.setFillRule(Qt.WindingFill)
    return q.simplified()


def bend(paths, amount):
    """put the text on an arc. amount > 0 = arch up, < 0 = smile. Works on whole paths (keeps letters connected)."""
    if abs(amount) < 0.01:
        return paths
    u = QRectF()
    for p in paths:
        r = p.boundingRect()
        u = r if u.isEmpty() else u.united(r)
    if u.isEmpty():
        return paths
    W = u.width()
    span = amount * math.radians(150)                  # whole name spans up to 150 degrees
    R = W / span
    cx = u.center().x()
    step = max(W / 400.0, 0.2)
    out = []
    for p in paths:
        q = QPainterPath()
        q.setFillRule(Qt.WindingFill)
        for poly in p.toSubpathPolygons():
            pts = []
            for i in range(poly.count()):
                a, b = poly.at(i), poly.at((i + 1) % poly.count())
                n = max(1, int(math.hypot(b.x() - a.x(), b.y() - a.y()) / step)) if i < poly.count() - 1 else 1
                for k in range(n):
                    t = k / n
                    x, y = a.x() + (b.x() - a.x()) * t, a.y() + (b.y() - a.y()) * t
                    ang = (x - cx) / R
                    r = R - y
                    pts.append(QPointF(cx + r * math.sin(ang), R - r * math.cos(ang)))
            if len(pts) > 2:
                q.addPolygon(QPolygonF(pts))
                q.closeSubpath()
        out.append(q)
    return out


def apply(s, items, size):
    f = s["font"]
    if not items:
        return items, QRectF()
    slant, stretch, amt = float(f.get("slant", 0)), float(f.get("stretch", 1.0)), float(f.get("bend", 0))
    style, cut, shadow = f.get("nstyle", "solid"), f.get("cut", "none"), f.get("shadow", "none")
    paths = [p for p, _ in items]
    paints = [c for _, c in items]
    # 1. geometry: width and slant around the baseline, then the curve
    if abs(stretch - 1) > 0.005 or abs(slant) > 0.05:
        tr = QTransform(stretch, 0, -math.tan(math.radians(slant)), 1, 0, 0)
        paths = [tr.map(p) for p in paths]
    paths = bend(paths, amt)
    cap = textkit.metrics(f["id"], f["bold"])["cap"] * size
    # 2. letter style
    w = size * 0.045
    if style != "solid":
        new = []
        for p in paths:
            q = _solid(p)
            if style == "outline":
                q = _stroke(q, w, Qt.FlatCap, Qt.MiterJoin)
            elif style == "double":
                ring = _stroke(q, w * 4.2, Qt.FlatCap, Qt.RoundJoin).subtracted(_stroke(q, w * 2.4, Qt.FlatCap, Qt.RoundJoin)).subtracted(q)
                q = q.united(ring)
            elif style == "inline":
                core = q.subtracted(_stroke(q, w * 3.2, Qt.FlatCap, Qt.MiterJoin))
                q = q.subtracted(_stroke(core, w * 0.55).intersected(q))
            new.append(q)
        paths = new
    # 3. cut letters
    u = QRectF()
    for p in paths:
        r = p.boundingRect()
        u = r if u.isEmpty() else u.united(r)
    extra = []
    if cut != "none" and not u.isEmpty():
        band = QPainterPath()
        L, Wd = u.left() - 10, u.width() + 20
        if cut == "stripe":
            band.addRect(QRectF(L, -cap * 0.5 - size * 0.03, Wd, size * 0.06))
        elif cut == "lines":
            for k in range(3):
                band.addRect(QRectF(L, -cap * (0.18 + k * 0.16) - size * 0.012, Wd, size * 0.024))
        elif cut == "slash":
            b = QPainterPath()
            b.addRect(QRectF(L - Wd, -size * 0.03, Wd * 3, size * 0.06))
            band = QTransform().translate(u.center().x(), -cap * 0.5).rotate(-14).translate(-u.center().x(), 0).map(b)
        elif cut == "top":
            band.addRect(QRectF(L, -cap * 0.72 - size * 0.035, Wd, size * 0.07))
        if cut == "half":
            band.addRect(QRectF(L, -cap * 0.5, Wd, cap * 2))
            sec = s["colors"]["secondary"]
            for p in paths:
                extra.append((p.intersected(band), sec))
            paths = [p.subtracted(band) for p in paths]
        else:
            paths = [p.subtracted(band) for p in paths]
    # 4. color: gradient over the whole name
    if f.get("ngrad"):
        g = Grad(s["colors"]["primary"], s["colors"]["secondary"], 0)
        allp = QPainterPath()
        allp.setFillRule(Qt.WindingFill)
        for p in paths:
            allp.addPath(p)
        out = [(allp, g)]
    else:
        out = list(zip(paths, paints))
    out += extra
    # 5. shadow behind
    back = []
    if shadow != "none":
        body = QPainterPath()
        body.setFillRule(Qt.WindingFill)
        for p, _ in out:
            body.addPath(p)
        body = _solid(body)
        base = s["colors"]["text"] if isinstance(paints[0], Grad) else (paints[0] if isinstance(paints[0], str) else s["colors"]["text"])
        soft = palettes.mix(base, s["colors"]["bg"], 0.72)
        if shadow == "drop":
            back.append((QTransform().translate(size * 0.035, size * 0.045).map(body), soft))
        elif shadow in ("long", "3d"):
            n = 26 if shadow == "long" else 9
            d = (size * 0.32 if shadow == "long" else size * 0.07) / n
            sh = QPainterPath()
            sh.setFillRule(Qt.WindingFill)
            for k in range(1, n + 1):
                sh.addPath(QTransform().translate(k * d, k * d).map(body))
            col = soft if shadow == "long" else palettes.shade(s["colors"]["secondary"], -0.15)
            back.append((_solid(sh).subtracted(body), col))
        elif shadow == "glow":
            back.append((_stroke(body, size * 0.09).subtracted(body), palettes.mix(s["colors"]["secondary"], s["colors"]["bg"], 0.35)))
    res = back + out
    ink = QRectF()
    for p, _ in res:
        r = p.boundingRect()
        if not r.isEmpty():
            ink = r if ink.isEmpty() else ink.united(r)
    return res, ink
