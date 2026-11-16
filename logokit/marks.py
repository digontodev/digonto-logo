"""Containers (badge shapes) and original abstract marks, all drawn in a 100 x 100 box.
A mark is a list of (QPainterPath, role): role 'a' = main color, 'b' = second color, 'c' = overlap / third tone."""
import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QPainterPath, QPainterPathStroker, QTransform


def stroked(p, w, cap=Qt.RoundCap, join=Qt.RoundJoin):
    s = QPainterPathStroker()
    s.setWidth(w)
    s.setCapStyle(cap)
    s.setJoinStyle(join)
    return s.createStroke(p).simplified()


def rrect(x, y, w, h, tl, tr=None, br=None, bl=None):
    tr = tl if tr is None else tr
    br = tl if br is None else br
    bl = tl if bl is None else bl
    p = QPainterPath()
    p.moveTo(x + tl, y)
    p.lineTo(x + w - tr, y)
    if tr:
        p.arcTo(x + w - 2 * tr, y, 2 * tr, 2 * tr, 90, -90)
    p.lineTo(x + w, y + h - br)
    if br:
        p.arcTo(x + w - 2 * br, y + h - 2 * br, 2 * br, 2 * br, 0, -90)
    p.lineTo(x + bl, y + h)
    if bl:
        p.arcTo(x, y + h - 2 * bl, 2 * bl, 2 * bl, 270, -90)
    p.lineTo(x, y + tl)
    if tl:
        p.arcTo(x, y, 2 * tl, 2 * tl, 180, -90)
    p.closeSubpath()
    return p


def circle(cx, cy, r):
    p = QPainterPath()
    p.addEllipse(QPointF(cx, cy), r, r)
    return p


def polygon(pts, rad=0.0):
    """closed polygon; rad > 0 rounds the corners"""
    p = QPainterPath()
    n = len(pts)
    if rad <= 0:
        p.moveTo(*pts[0])
        for q in pts[1:]:
            p.lineTo(*q)
        p.closeSubpath()
        return p
    for i in range(n):
        a, b, c = pts[i - 1], pts[i], pts[(i + 1) % n]
        v1 = (a[0] - b[0], a[1] - b[1])
        v2 = (c[0] - b[0], c[1] - b[1])
        l1, l2 = math.hypot(*v1), math.hypot(*v2)
        r = min(rad, l1 / 2, l2 / 2)
        s = (b[0] + v1[0] / l1 * r, b[1] + v1[1] / l1 * r)
        e = (b[0] + v2[0] / l2 * r, b[1] + v2[1] / l2 * r)
        if i == 0:
            p.moveTo(*s)
        else:
            p.lineTo(*s)
        p.quadTo(b[0], b[1], *e)
    p.closeSubpath()
    return p


def ngon(cx, cy, r, n, rot=-90, rad=0.0):
    return polygon([(cx + r * math.cos(math.radians(rot + 360 * i / n)), cy + r * math.sin(math.radians(rot + 360 * i / n))) for i in range(n)], rad)


# ------------------------------------------------------------------ containers
CONTAINERS = ["circle", "rounded", "squircle", "hexagon", "shield", "diamond", "arch", "leaf", "ring", "badge8"]


def container(kind):
    if kind == "circle":
        return circle(50, 50, 50)
    if kind == "rounded":
        return rrect(0, 0, 100, 100, 24)
    if kind == "squircle":
        p = QPainterPath()
        n = 4.0
        pts = []
        for i in range(120):
            t = 2 * math.pi * i / 120
            c, s = math.cos(t), math.sin(t)
            pts.append((50 + 50 * math.copysign(abs(c) ** (2 / n), c), 50 + 50 * math.copysign(abs(s) ** (2 / n), s)))
        p.moveTo(*pts[0])
        for q in pts[1:]:
            p.lineTo(*q)
        p.closeSubpath()
        return p
    if kind == "hexagon":
        return ngon(50, 50, 52, 6, -90, 9)
    if kind == "shield":
        p = QPainterPath()
        p.moveTo(50, 0)
        p.cubicTo(66, 12, 82, 14, 96, 14)
        p.lineTo(96, 50)
        p.cubicTo(96, 76, 74, 92, 50, 100)
        p.cubicTo(26, 92, 4, 76, 4, 50)
        p.lineTo(4, 14)
        p.cubicTo(18, 14, 34, 12, 50, 0)
        p.closeSubpath()
        return p
    if kind == "diamond":
        return polygon([(50, 0), (100, 50), (50, 100), (0, 50)], 12)
    if kind == "arch":
        return rrect(8, 0, 84, 100, 42, 42, 12, 12)
    if kind == "leaf":
        return rrect(0, 0, 100, 100, 50, 8, 50, 8)
    if kind == "ring":
        return circle(50, 50, 50).subtracted(circle(50, 50, 40))
    if kind == "badge8":
        pts = []
        for i in range(32):
            r = 50 if i % 2 == 0 else 44
            a = math.radians(-90 + 360 * i / 32)
            pts.append((50 + r * math.cos(a), 50 + r * math.sin(a)))
        return polygon(pts)
    from . import more
    if kind in more.CONTAINERS:
        return more.container(kind)
    return rrect(0, 0, 100, 100, 0)


# ------------------------------------------------------------------ abstract marks
def m_orbit():
    a, b = circle(36, 50, 30), circle(64, 50, 30)
    return [(a.subtracted(b), "a"), (b.subtracted(a), "b"), (a.intersected(b), "c")]


def m_quad():
    return [(rrect(4, 4, 44, 44, 22, 22, 0, 22), "a"), (rrect(52, 4, 44, 44, 0, 22, 22, 22), "b"),
            (rrect(4, 52, 44, 44, 22, 0, 22, 22), "b"), (rrect(52, 52, 44, 44, 22, 22, 22, 0), "a")]


def m_bars():
    out = []
    for i, h in enumerate((34, 54, 74, 94)):
        out.append((rrect(6 + i * 23, 100 - h - 3, 17, h, 8.5, 8.5, 4, 4), "a" if i % 2 == 0 else "b"))
    return out


def m_wave():
    out = []
    for k, role in enumerate(("a", "b", "a")):
        p = QPainterPath()
        y0 = 26 + k * 24
        p.moveTo(2, y0)
        for s in range(2):
            x = 2 + s * 48
            p.cubicTo(x + 12, y0 - 18, x + 36, y0 + 18, x + 48, y0)
        out.append((stroked(p, 11), role))
    return out


def m_peaks():
    big = polygon([(2, 90), (40, 22), (78, 90)], 4)
    small = polygon([(52, 90), (74, 50), (98, 90)], 4)
    return [(big, "a"), (small, "b"), (circle(78, 22, 10), "c")]


def m_spark():
    p = QPainterPath()
    p.moveTo(50, 0)
    p.quadTo(50, 50, 100, 50)
    p.quadTo(50, 50, 50, 100)
    p.quadTo(50, 50, 0, 50)
    p.quadTo(50, 50, 50, 0)
    p.closeSubpath()
    return [(p, "a"), (circle(84, 16, 7), "b")]


def m_spiral():
    p = QPainterPath()
    cx = cy = 50
    first = True
    for i in range(0, 340):
        t = i / 340 * 5.2 * math.pi
        r = 3 + 42 * (i / 340)
        x, y = cx + r * math.cos(t), cy + r * math.sin(t)
        if first:
            p.moveTo(x, y)
            first = False
        else:
            p.lineTo(x, y)
    return [(stroked(p, 10), "a")]


def m_dots():
    out = []
    for r in range(3):
        for c in range(3):
            d = abs(r - c)
            out.append((circle(17 + c * 33, 17 + r * 33, [13, 9, 6][d]), "a" if (r + c) % 2 == 0 else "b"))
    return out


def m_arch():
    out = []
    for i, r in enumerate((44, 30, 16)):
        p = QPainterPath()
        p.moveTo(50 - r, 92)
        p.lineTo(50 - r, 92 - r)
        p.arcTo(50 - r, 92 - 2 * r, 2 * r, 2 * r, 180, -180)
        p.lineTo(50 + r, 92)
        out.append((stroked(p, 10, Qt.FlatCap, Qt.MiterJoin), "a" if i != 1 else "b"))
    return out


def _lens(p0, p1, bulge):
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy)
    nx, ny = -dy / L * bulge, dx / L * bulge
    q = QPainterPath()
    q.moveTo(*p0)
    q.cubicTo(p0[0] + dx * 0.25 + nx, p0[1] + dy * 0.25 + ny, p0[0] + dx * 0.75 + nx, p0[1] + dy * 0.75 + ny, *p1)
    q.cubicTo(p0[0] + dx * 0.75 - nx, p0[1] + dy * 0.75 - ny, p0[0] + dx * 0.25 - nx, p0[1] + dy * 0.25 - ny, *p0)
    q.closeSubpath()
    return q


def m_leaves():
    return [(_lens((48, 62), (10, 12), 26), "a"), (_lens((52, 62), (90, 12), 26), "b"), (stroked(_line(50, 96, 50, 52), 8), "a")]


def _line(x1, y1, x2, y2):
    p = QPainterPath()
    p.moveTo(x1, y1)
    p.lineTo(x2, y2)
    return p


def m_chevrons():
    out = []
    for i in range(3):
        p = QPainterPath()
        y = 18 + i * 26
        p.moveTo(10, y + 26)
        p.lineTo(50, y)
        p.lineTo(90, y + 26)
        out.append((stroked(p, 12, Qt.RoundCap, Qt.RoundJoin), ("a", "b", "a")[i]))
    return out


def m_ringcut():
    ring = stroked(_arc(50, 50, 38, 40, 320), 14, Qt.RoundCap)
    return [(ring, "a"), (circle(50, 50, 13), "b")]


def _arc(cx, cy, r, start, sweep):
    p = QPainterPath()
    p.arcMoveTo(cx - r, cy - r, 2 * r, 2 * r, start)
    p.arcTo(cx - r, cy - r, 2 * r, 2 * r, start, sweep)
    return p


def m_cube():
    top = polygon([(50, 4), (92, 27), (50, 50), (8, 27)], 2)
    left = polygon([(8, 33), (46, 56), (46, 98), (8, 75)], 2)
    right = polygon([(54, 56), (92, 33), (92, 75), (54, 98)], 2)
    return [(top, "c"), (left, "a"), (right, "b")]


def m_drop():
    p = QPainterPath()
    p.moveTo(50, 2)
    p.cubicTo(50, 2, 90, 44, 90, 66)
    p.cubicTo(90, 86, 72, 98, 50, 98)
    p.cubicTo(28, 98, 10, 86, 10, 66)
    p.cubicTo(10, 44, 50, 2, 50, 2)
    hi = stroked(_arc(50, 66, 24, 200, -90), 8)
    return [(p.subtracted(hi), "a")]


def m_flower():
    out = [(circle(50, 50, 16), "b")]
    for i in range(6):
        a = math.radians(60 * i)
        out.append((circle(50 + 28 * math.cos(a), 50 + 28 * math.sin(a), 16).subtracted(circle(50, 50, 18)), "a"))
    return out


def m_split():
    c = circle(50, 50, 46)
    cut = polygon([(0, 70), (0, 100), (100, 100), (100, 30)])
    top, bot = c.subtracted(cut), c.intersected(cut)
    return [(top, "a"), (QTransform().translate(5, 6).map(bot), "b")]


def m_triangles():
    t = lambda x, y: polygon([(x, y + 38), (x + 22, y), (x + 44, y + 38)], 4)
    return [(t(28, 4), "a"), (t(4, 50), "b"), (t(52, 50), "a")]


def m_pinwheel():
    out = []
    for i, role in enumerate(("a", "b", "a", "b")):
        q = QPainterPath()
        q.moveTo(50, 50)
        q.lineTo(50, 4)
        q.arcTo(4, 4, 92, 92, 90, -90)
        q.closeSubpath()
        out.append((QTransform().translate(50, 50).rotate(90 * i).translate(-50, -50).map(q.translated(0, 0)), role))
    return [(o.subtracted(circle(50, 50, 7)), r) for o, r in out]


def m_layers():
    return [(rrect(14, 64, 72, 26, 10), "a"), (rrect(8, 36, 84, 26, 10), "b"), (rrect(20, 8, 60, 26, 10), "a")]


MARKS = {"orbit": m_orbit, "quad": m_quad, "bars": m_bars, "wave": m_wave, "peaks": m_peaks, "spark": m_spark, "spiral": m_spiral,
         "dots": m_dots, "arch": m_arch, "leaves": m_leaves, "chevrons": m_chevrons, "ringcut": m_ringcut, "cube": m_cube,
         "drop": m_drop, "flower": m_flower, "split": m_split, "triangles": m_triangles, "pinwheel": m_pinwheel, "layers": m_layers}


from . import more as _more  # noqa: E402

MARKS.update(_more.MARKS)
CONTAINERS.extend(c for c in _more.CONTAINERS if c not in CONTAINERS)

from . import library as _library  # noqa: E402

for _n in MARKS:
    if _n not in _library.CATS:
        _library.CATS[_n] = "Abstract"
MARKS.update(_library.MARKS)
CATS = _library.CATS
CATEGORIES = ["All", "Abstract", "Shapes", "Nature", "Food", "Business", "Tech", "People", "Travel", "Sport", "Symbols"]
