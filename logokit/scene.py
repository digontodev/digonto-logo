"""A logo is a scene: a list of vector items (path + fill/stroke). One scene -> SVG / PDF / EPS / PNG / ICO."""
import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen, QBrush, QTransform


class Grad:
    def __init__(self, c1, c2, angle=45):
        self.c1, self.c2, self.angle = c1, c2, angle

    def key(self):
        return (self.c1, self.c2, self.angle)


class Item:
    def __init__(self, path, fill=None, stroke=None, width=0.0, opacity=1.0, rule=None, cap="butt", join="miter"):
        self.path, self.fill, self.stroke, self.width, self.opacity, self.cap, self.join = path, fill, stroke, width, opacity, cap, join
        self.rule = rule if rule is not None else path.fillRule()

    def bounds(self):
        r = self.path.boundingRect()
        if self.stroke and self.width:
            h = self.width / 2
            r = r.adjusted(-h, -h, h, h)
        return r


class Scene:
    def __init__(self):
        self.items = []

    def add(self, *a, **k):
        it = Item(*a, **k)
        self.items.append(it)
        return it

    def bounds(self):
        rs = [i.bounds() for i in self.items if not i.path.isEmpty()]
        if not rs:
            return QRectF(0, 0, 1, 1)
        r = rs[0]
        for x in rs[1:]:
            r = r.united(x)
        return r

    def mapped(self, tr):
        s = Scene()
        for i in self.items:
            s.items.append(Item(tr.map(i.path), i.fill, i.stroke, i.width * math.sqrt(abs(tr.determinant())), i.opacity, i.rule, i.cap, i.join))
        return s

    def recolored(self, fn):
        """new scene where every paint goes through fn(color_or_grad) -> color_or_grad"""
        s = Scene()
        for i in self.items:
            s.items.append(Item(i.path, fn(i.fill) if i.fill else None, fn(i.stroke) if i.stroke else None, i.width, i.opacity, i.rule, i.cap, i.join))
        return s


def _qcolor(c, a=1.0):
    q = QColor(c)
    q.setAlphaF(a)
    return q


def _brush(fill, rect, opacity):
    if isinstance(fill, Grad):
        a = math.radians(fill.angle)
        cx, cy = rect.center().x(), rect.center().y()
        dx, dy = math.cos(a) * rect.width() / 2, math.sin(a) * rect.height() / 2
        g = QLinearGradient(QPointF(cx - dx, cy - dy), QPointF(cx + dx, cy + dy))
        g.setColorAt(0, _qcolor(fill.c1, opacity))
        g.setColorAt(1, _qcolor(fill.c2, opacity))
        return QBrush(g)
    return QBrush(_qcolor(fill, opacity))


def paint(scene, painter, target, source=None, bg=None):
    """draw the scene into target (QRectF), keeping its proportions and centering it"""
    source = source or scene.bounds()
    painter.save()
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setRenderHint(QPainter.SmoothPixmapTransform)
    if bg:
        painter.fillRect(target, QColor(bg))
    k = min(target.width() / source.width(), target.height() / source.height())
    tx = target.x() + (target.width() - source.width() * k) / 2 - source.x() * k
    ty = target.y() + (target.height() - source.height() * k) / 2 - source.y() * k
    painter.translate(tx, ty)
    painter.scale(k, k)
    for it in scene.items:
        p = QPainterPath(it.path)
        p.setFillRule(it.rule)
        if it.fill:
            painter.setPen(Qt.NoPen)
            painter.setBrush(_brush(it.fill, p.boundingRect(), it.opacity))
            painter.drawPath(p)
        if it.stroke and it.width:
            pen = QPen(_brush(it.stroke, p.boundingRect(), it.opacity), it.width)
            pen.setCapStyle({"round": Qt.RoundCap, "square": Qt.SquareCap}.get(it.cap, Qt.FlatCap))
            pen.setJoinStyle({"round": Qt.RoundJoin, "bevel": Qt.BevelJoin}.get(it.join, Qt.MiterJoin))
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(p)
    painter.restore()


def path_d(p, prec=2):
    f = lambda v: ("%.*f" % (prec, v)).rstrip("0").rstrip(".") or "0"
    out, i, n = [], 0, p.elementCount()
    while i < n:
        e = p.elementAt(i)
        if e.type == QPainterPath.MoveToElement:
            if out and not out[-1].endswith("Z"):
                pass
            out.append(f"M{f(e.x)} {f(e.y)}")
        elif e.type == QPainterPath.LineToElement:
            out.append(f"L{f(e.x)} {f(e.y)}")
        elif e.type == QPainterPath.CurveToElement:
            c2, en = p.elementAt(i + 1), p.elementAt(i + 2)
            out.append(f"C{f(e.x)} {f(e.y)} {f(c2.x)} {f(c2.y)} {f(en.x)} {f(en.y)}")
            i += 2
        i += 1
    return "".join(out)


def closed_d(p, prec=2):
    """path_d, closing every sub-path whose end meets its start (fills need no Z, strokes of closed shapes do)"""
    f = lambda v: ("%.*f" % (prec, v)).rstrip("0").rstrip(".") or "0"
    subs, cur, start = [], [], None
    i, n = 0, p.elementCount()
    last = None
    while i < n:
        e = p.elementAt(i)
        if e.type == QPainterPath.MoveToElement:
            if cur:
                subs.append((cur, start, last))
            cur, start = [f"M{f(e.x)} {f(e.y)}"], (e.x, e.y)
            last = start
        elif e.type == QPainterPath.LineToElement:
            cur.append(f"L{f(e.x)} {f(e.y)}")
            last = (e.x, e.y)
        elif e.type == QPainterPath.CurveToElement:
            c2, en = p.elementAt(i + 1), p.elementAt(i + 2)
            cur.append(f"C{f(e.x)} {f(e.y)} {f(c2.x)} {f(c2.y)} {f(en.x)} {f(en.y)}")
            last = (en.x, en.y)
            i += 2
        i += 1
    if cur:
        subs.append((cur, start, last))
    out = []
    for c, s, l in subs:
        out.append("".join(c) + ("Z" if abs(s[0] - l[0]) < 1e-3 and abs(s[1] - l[1]) < 1e-3 else ""))
    return "".join(out)
