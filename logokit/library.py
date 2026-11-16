"""Digonto mark library: 200+ original symbols in a 100 x 100 box, grouped by category.
Every mark returns a list of (QPainterPath, role); role 'a' main colour, 'b' second, 'c' third."""
import math

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainterPath, QTransform

from .marks import _arc, circle, ngon, polygon, rrect, stroked
from .more import _line_p, _rot, _star

MARKS = {}
CATS = {}


def mark(cat, name=None):
    def deco(fn):
        n = name or fn.__name__[2:]
        MARKS[n] = fn
        CATS[n] = cat
        return fn
    return deco


# ---- tiny drawing kit
C = circle
def R(x, y, w, h, r=0):
    return rrect(x, y, w, h, r)


def P(pts, r=0):
    return polygon(pts, r)


def L(x1, y1, x2, y2, w=8):
    return stroked(_line_p(x1, y1, x2, y2), w)


def A(cx, cy, r, s, sw, w=8):
    return stroked(_arc(cx, cy, r, s, sw), w)


def ring(cx, cy, r, w):
    return circle(cx, cy, r).subtracted(circle(cx, cy, r - w))


def N(n, r=46, rot=-90, rad=0, cx=50, cy=50):
    return ngon(cx, cy, r, n, rot, rad)


def ST(n, ro=48, ri=20, rot=-90, rad=0):
    return _star(50, 50, ro, ri, n, rot, rad)


def spin(p, deg, cx=50, cy=50):
    return _rot(p, deg, cx, cy)


def fan(p, n, cx=50, cy=50, start=0):
    return [spin(p, start + 360 * i / n, cx, cy) for i in range(n)]


def move(p, dx, dy):
    return QTransform().translate(dx, dy).map(p)


def scale(p, k, cx=50, cy=50):
    return QTransform().translate(cx, cy).scale(k, k).translate(-cx, -cy).map(p)


def mirror(p, cx=50):
    return QTransform().translate(2 * cx, 0).scale(-1, 1).map(p)


def lens(x1, y1, x2, y2, bulge):
    """leaf / petal shape between two points"""
    dx, dy = x2 - x1, y2 - y1
    d = math.hypot(dx, dy) or 1
    nx, ny = -dy / d * bulge, dx / d * bulge
    p = QPainterPath()
    p.moveTo(x1, y1)
    p.cubicTo(x1 + dx * .25 + nx, y1 + dy * .25 + ny, x1 + dx * .75 + nx, y1 + dy * .75 + ny, x2, y2)
    p.cubicTo(x1 + dx * .75 - nx, y1 + dy * .75 - ny, x1 + dx * .25 - nx, y1 + dy * .25 - ny, x1, y1)
    return p


def U(*ps):
    r = QPainterPath()
    for q in ps:
        r = r.united(q)
    return r.simplified()


def heartp(cx=50, cy=50, s=1.0):
    p = QPainterPath()
    p.moveTo(50, 92)
    p.cubicTo(8, 62, 0, 42, 0, 30)
    p.cubicTo(0, 12, 16, 4, 28, 4)
    p.cubicTo(40, 4, 48, 12, 50, 22)
    p.cubicTo(52, 12, 60, 4, 72, 4)
    p.cubicTo(84, 4, 100, 12, 100, 30)
    p.cubicTo(100, 42, 92, 62, 50, 92)
    p.closeSubpath()
    return QTransform().translate(cx, cy).scale(s, s).translate(-50, -48).map(p)


# =============================================================== SHAPES
@mark("Shapes")
def m_star4():
    return [(ST(4, 48, 14, -90, 2), "a")]


@mark("Shapes")
def m_star5():
    return [(ST(5, 48, 21, -90, 3), "a")]


@mark("Shapes")
def m_star6():
    return [(ST(6, 48, 27, -90, 2), "a")]


@mark("Shapes")
def m_star8():
    return [(ST(8, 48, 30, -90, 1), "a")]


@mark("Shapes")
def m_star12():
    return [(ST(12, 48, 38, -90, 0), "a"), (C(50, 50, 14), "b")]


@mark("Shapes")
def m_starring():
    return [(ST(5, 48, 21, -90, 3).subtracted(ST(5, 28, 12, -90, 2)), "a")]


@mark("Shapes")
def m_triangle():
    return [(N(3, 52, -90, 8, 50, 56), "a")]


@mark("Shapes")
def m_pentagon():
    return [(N(5, 50, -90, 6), "a")]


@mark("Shapes")
def m_hexagon():
    return [(N(6, 50, -90, 6), "a")]


@mark("Shapes")
def m_heptagon():
    return [(N(7, 50, -90, 5), "a")]


@mark("Shapes")
def m_octagon():
    return [(N(8, 50, -67.5, 4), "a")]


@mark("Shapes")
def m_diamond():
    return [(P([(50, 2), (96, 50), (50, 98), (4, 50)], 4), "a")]


@mark("Shapes")
def m_ringtri():
    return [(N(3, 52, -90, 8, 50, 56).subtracted(N(3, 26, -90, 3, 50, 62)), "a")]


@mark("Shapes")
def m_ringhex():
    return [(N(6, 50, -90, 6).subtracted(N(6, 30, -90, 3)), "a")]


@mark("Shapes")
def m_ringsq():
    return [(R(6, 6, 88, 88, 16).subtracted(R(30, 30, 40, 40, 6)), "a")]


@mark("Shapes")
def m_ringdia():
    return [(P([(50, 2), (96, 50), (50, 98), (4, 50)], 4).subtracted(P([(50, 28), (72, 50), (50, 72), (28, 50)], 2)), "a")]


@mark("Shapes")
def m_ringpent():
    return [(N(5, 50, -90, 6).subtracted(N(5, 28, -90, 3)), "a")]


@mark("Shapes")
def m_target():
    return [(ring(50, 50, 48, 10), "a"), (ring(50, 50, 30, 10), "b"), (C(50, 50, 10), "a")]


@mark("Shapes")
def m_dotgrid():
    return [(C(20 + 30 * i, 20 + 30 * j, 10), "a" if (i + j) % 2 == 0 else "b") for i in range(3) for j in range(3)]


@mark("Shapes")
def m_dotcircle():
    return [(C(50 + 38 * math.cos(math.radians(i * 36 - 90)), 50 + 38 * math.sin(math.radians(i * 36 - 90)), 8), "a" if i % 2 == 0 else "b") for i in range(10)]


@mark("Shapes")
def m_halfmoons():
    a = U(C(50, 50, 46).intersected(R(0, 0, 50, 100)))
    b = U(C(50, 50, 46).intersected(R(50, 0, 50, 100)))
    return [(move(a, -4, 0), "a"), (move(b, 4, 0), "b")]


@mark("Shapes")
def m_quarters():
    out = []
    for i, role in enumerate("abab"):
        q = QPainterPath()
        q.moveTo(50, 50)
        q.arcTo(4, 4, 92, 92, 90 - 90 * i, -90)
        q.closeSubpath()
        out.append((move(q, [-2, 2, 2, -2][i], [-2, -2, 2, 2][i]), role))
    return out


@mark("Shapes")
def m_petals5():
    return [(p, "a" if i % 2 == 0 else "b") for i, p in enumerate(fan(lens(50, 50, 50, 4, 14), 5))]


@mark("Shapes")
def m_petals6():
    return [(p, "a" if i % 2 == 0 else "b") for i, p in enumerate(fan(lens(50, 50, 50, 4, 12), 6))]


@mark("Shapes")
def m_petals8():
    return [(p, "a" if i % 2 == 0 else "b") for i, p in enumerate(fan(lens(50, 50, 50, 3, 10), 8))]


@mark("Shapes")
def m_petals12():
    return [(p, "a" if i % 2 == 0 else "b") for i, p in enumerate(fan(lens(50, 52, 50, 3, 6), 12))]


@mark("Shapes")
def m_daisy():
    return [(p, "a") for p in fan(lens(50, 50, 50, 4, 9), 10)] + [(C(50, 50, 13), "b")]


@mark("Shapes")
def m_rosette():
    return [(ring(50 + 22 * math.cos(math.radians(i * 60)), 50 + 22 * math.sin(math.radians(i * 60)), 24, 5), "a" if i % 2 == 0 else "b") for i in range(6)]


@mark("Shapes")
def m_rays8():
    return [(C(50, 50, 20), "a")] + [(p, "b") for p in fan(L(50, 14, 50, 4, 8), 8)]


@mark("Shapes")
def m_rays12():
    return [(C(50, 50, 24), "a")] + [(p, "b") for p in fan(L(50, 16, 50, 4, 7), 12)]


@mark("Shapes")
def m_rays16():
    return [(ring(50, 50, 30, 8), "a")] + [(p, "b") for p in fan(L(50, 14, 50, 4, 4), 16)]


@mark("Shapes")
def m_plus():
    return [(U(R(36, 6, 28, 88, 8), R(6, 36, 88, 28, 8)), "a")]


@mark("Shapes")
def m_cross():
    return [(spin(U(R(36, 6, 28, 88, 8), R(6, 36, 88, 28, 8)), 45), "a")]


@mark("Shapes")
def m_asterisk():
    return [(spin(L(50, 10, 50, 90, 14), i * 60), "a") for i in range(3)]


@mark("Shapes")
def m_asterisk8():
    return [(spin(L(50, 8, 50, 92, 10), i * 45), "a" if i % 2 == 0 else "b") for i in range(4)]


@mark("Shapes")
def m_equals():
    return [(R(8, 24, 84, 18, 9), "a"), (R(8, 58, 84, 18, 9), "b")]


@mark("Shapes")
def m_stripes():
    out = []
    clip = C(50, 50, 48)
    for i in range(4):
        out.append((spin(R(-10 + i * 30, -10, 15, 120, 0), 35).intersected(clip), "a" if i % 2 == 0 else "b"))
    return out


@mark("Shapes")
def m_triplestack():
    return [(N(3, 48 - i * 14, -90, 4, 50, 58 + i * 4).subtracted(N(3, 48 - i * 14 - 9, -90, 2, 50, 58 + i * 4 + 3)), "a" if i % 2 == 0 else "b") for i in range(3)]


@mark("Shapes")
def m_sqspiral():
    p = QPainterPath()
    p.moveTo(14, 14)
    for pt in [(86, 14), (86, 86), (22, 86), (22, 38), (62, 38), (62, 62), (44, 62)]:
        p.lineTo(*pt)
    return [(stroked(p, 9, join=Qt.MiterJoin), "a")]


@mark("Shapes")
def m_wirecube():
    h = N(6, 48, -90, 2).subtracted(N(6, 38, -90, 1))
    return [(h, "a"), (L(50, 50, 50, 92, 8), "b"), (L(50, 50, 8, 26, 8), "b"), (L(50, 50, 92, 26, 8), "b")]


@mark("Shapes")
def m_ringdot():
    return [(ring(50, 50, 46, 9), "a"), (C(50, 50, 16), "b")]


@mark("Shapes")
def m_yin():
    full = C(50, 50, 46)
    left = full.intersected(R(0, 0, 50, 100))
    s1 = C(50, 27, 23)
    s2 = C(50, 73, 23)
    a = left.united(s1).subtracted(s2)
    b = full.subtracted(a)
    return [(b, "b"), (a, "a")]


@mark("Shapes")
def m_eye():
    e = lens(2, 50, 98, 50, 34)
    return [(e, "a"), (C(50, 50, 20), "b"), (C(50, 50, 8), "a")]


@mark("Shapes")
def m_prism():
    t = N(3, 40, -90, 3, 40, 56)
    return [(t, "a"), (L(66, 50, 98, 38, 6), "b"), (L(66, 58, 98, 58, 6), "c"), (L(64, 66, 96, 80, 6), "b")]


@mark("Shapes")
def m_arrowright():
    return [(U(R(6, 38, 60, 24, 6), P([(60, 12), (96, 50), (60, 88)], 6)), "a")]


@mark("Shapes")
def m_arrowup():
    return [(spin(U(R(6, 38, 60, 24, 6), P([(60, 12), (96, 50), (60, 88)], 6)), -90), "a")]


@mark("Shapes")
def m_arrowdouble():
    return [(P([(6, 14), (46, 50), (6, 86), (6, 66), (26, 50), (6, 34)], 3), "a"), (P([(50, 14), (90, 50), (50, 86), (50, 66), (70, 50), (50, 34)], 3), "b")]


@mark("Shapes")
def m_arrowcurve():
    return [(A(50, 54, 36, 200, -220, 12), "a"), (P([(76, 10), (96, 40), (62, 40)], 3), "b")]


@mark("Shapes")
def m_cycle():
    return [(A(50, 50, 34, 20, 140, 10), "a"), (P([(70, 6), (92, 34), (58, 38)], 3), "a"),
            (A(50, 50, 34, 200, 140, 10), "b"), (P([(30, 94), (8, 66), (42, 62)], 3), "b")]


@mark("Shapes")
def m_tag():
    return [(P([(8, 8), (56, 8), (94, 46), (56, 94), (8, 94)], 6).subtracted(C(26, 28, 7)), "a")]


@mark("Shapes")
def m_trisplit():
    return [(P([(50, 6), (94, 88), (50, 88)], 3), "a"), (P([(50, 6), (50, 88), (6, 88)], 3), "b")]


@mark("Shapes")
def m_bowtie():
    return [(P([(6, 22), (50, 50), (6, 78)], 4), "a"), (P([(94, 22), (50, 50), (94, 78)], 4), "b")]


@mark("Shapes")
def m_kite():
    return [(P([(50, 4), (90, 40), (50, 96), (10, 40)], 4), "a"), (P([(50, 4), (50, 96), (10, 40)], 4), "b")]


@mark("Shapes")
def m_slashes():
    return [(spin(R(14 + i * 26, -10, 12, 120, 6), 25), "a" if i % 2 == 0 else "b") for i in range(3)]


@mark("Shapes")
def m_nested():
    return [(R(4, 4, 92, 92, 24), "a"), (R(22, 22, 56, 56, 14), "b"), (R(38, 38, 24, 24, 6), "a")]


# =============================================================== NATURE
@mark("Nature")
def m_sun():
    return [(C(50, 50, 22), "a")] + [(p, "b") for p in fan(P([(44, 12), (56, 12), (50, 2)], 1), 8)]


@mark("Nature")
def m_moonstar():
    moon = C(46, 52, 40).subtracted(C(64, 42, 34))
    return [(moon, "a"), (move(ST(4, 16, 5, -90, 1), 38, -38), "b")]


@mark("Nature")
def m_cloud():
    return [(U(R(8, 46, 84, 38, 19), C(34, 46, 20), C(58, 38, 26), C(76, 52, 16)), "a")]


@mark("Nature")
def m_rain():
    cl = U(R(8, 22, 84, 36, 18), C(34, 22, 18), C(58, 16, 22), C(76, 30, 14))
    return [(cl, "a")] + [(L(24 + i * 20, 70, 18 + i * 20, 90, 7), "b") for i in range(4)]


@mark("Nature")
def m_snow():
    arm = U(L(50, 50, 50, 4, 7), L(50, 22, 38, 12, 6), L(50, 22, 62, 12, 6), L(50, 36, 42, 30, 5), L(50, 36, 58, 30, 5))
    return [(p, "a") for p in fan(arm, 6)]


@mark("Nature")
def m_flame():
    p = QPainterPath()
    p.moveTo(50, 96)
    p.cubicTo(14, 96, 6, 62, 26, 42)
    p.cubicTo(30, 54, 38, 56, 40, 52)
    p.cubicTo(34, 32, 46, 14, 58, 4)
    p.cubicTo(60, 24, 90, 40, 90, 68)
    p.cubicTo(90, 86, 72, 96, 50, 96)
    p.closeSubpath()
    inner = QPainterPath()
    inner.moveTo(50, 92)
    inner.cubicTo(32, 92, 28, 74, 40, 64)
    inner.cubicTo(46, 70, 52, 66, 52, 60)
    inner.cubicTo(66, 70, 72, 92, 50, 92)
    return [(p, "a"), (inner, "c")]


@mark("Nature")
def m_leaf():
    return [(lens(10, 90, 90, 10, 26), "a"), (L(18, 82, 70, 30, 5), "b")]


@mark("Nature")
def m_leafpair():
    return [(lens(50, 90, 12, 24, 16), "a"), (lens(50, 90, 88, 24, 16), "b"), (L(50, 96, 50, 60, 6), "a")]


@mark("Nature")
def m_tree():
    return [(U(C(50, 36, 30), C(28, 52, 20), C(72, 52, 20)), "a"), (P([(44, 60), (56, 60), (60, 94), (40, 94)], 2), "b")]


@mark("Nature")
def m_pine():
    return [(P([(50, 4), (78, 40), (22, 40)], 3), "a"), (P([(50, 24), (86, 66), (14, 66)], 3), "a"), (R(42, 66, 16, 28, 2), "b")]


@mark("Nature")
def m_palm():
    out = [(L(50, 94, 54, 40, 9), "b")]
    for x, y in ((8, 56), (20, 22), (54, 6), (88, 22), (98, 56)):
        out.append((lens(54, 40, x, y, 9), "a"))
    out.append((C(54, 40, 6), "b"))
    return out


@mark("Nature")
def m_waves():
    out = []
    for i in range(3):
        p = QPainterPath()
        y = 30 + i * 22
        p.moveTo(6, y)
        for k in range(3):
            x = 6 + k * 29.3
            p.cubicTo(x + 7, y - 14, x + 22, y - 14, x + 29.3, y)
        out.append((stroked(p, 9), "a" if i != 1 else "b"))
    return out


@mark("Nature")
def m_mountainsun():
    return [(C(68, 28, 14), "b"), (P([(2, 92), (36, 30), (56, 62), (70, 44), (98, 92)], 4), "a")]


@mark("Nature")
def m_island():
    mound = C(50, 108, 52).intersected(R(0, 70, 100, 30))
    return [(mound, "b"), (L(50, 76, 52, 40, 7), "a"), (lens(52, 40, 22, 26, 7), "a"), (lens(52, 40, 80, 24, 7), "a"), (lens(52, 40, 38, 12, 6), "a"), (lens(52, 40, 68, 10, 6), "a")]


@mark("Nature")
def m_feather():
    return [(lens(14, 90, 86, 8, 22), "a"), (L(14, 90, 80, 14, 4), "b"), (L(40, 62, 62, 66, 4), "b"), (L(52, 46, 74, 50, 4), "b")]


@mark("Nature")
def m_butterfly():
    w1 = lens(50, 50, 6, 14, 22)
    w2 = lens(50, 50, 10, 90, 18)
    return [(w1, "a"), (mirror(w1), "a"), (w2, "b"), (mirror(w2), "b"), (R(46, 30, 8, 44, 4), "c")]


@mark("Nature")
def m_fish():
    body = lens(10, 50, 70, 50, 26)
    return [(body, "a"), (P([(64, 50), (96, 24), (96, 76)], 3), "b"), (C(28, 44, 4), "c")]


@mark("Nature")
def m_bird():
    p = QPainterPath()
    p.moveTo(6, 62)
    p.cubicTo(20, 20, 40, 24, 50, 56)
    p.cubicTo(60, 24, 80, 20, 94, 62)
    return [(stroked(p, 10), "a"), (C(50, 62, 6), "b")]


@mark("Nature")
def m_dove():
    body = lens(10, 62, 78, 40, 20)
    wing = lens(40, 54, 60, 6, 14)
    return [(body, "a"), (wing, "b"), (P([(78, 40), (96, 44), (78, 48)], 1), "c"), (P([(12, 62), (2, 82), (30, 66)], 2), "a")]


@mark("Nature")
def m_owl():
    return [(R(14, 10, 72, 84, 30), "a"), (C(36, 40, 15), "c"), (C(64, 40, 15), "c"), (C(36, 40, 6), "b"), (C(64, 40, 6), "b"),
            (P([(44, 52), (56, 52), (50, 64)], 1), "b"), (P([(18, 14), (30, 22), (18, 30)], 1), "b"), (P([(82, 14), (70, 22), (82, 30)], 1), "b")]


@mark("Nature")
def m_cat():
    face = U(C(50, 56, 36), P([(16, 40), (16, 6), (42, 24)], 3), P([(84, 40), (84, 6), (58, 24)], 3))
    return [(face, "a"), (C(38, 52, 5), "b"), (C(62, 52, 5), "b"), (P([(44, 62), (56, 62), (50, 70)], 1), "b")]


@mark("Nature")
def m_fox():
    return [(P([(6, 8), (36, 30), (64, 30), (94, 8), (88, 56), (50, 96), (12, 56)], 4), "a"), (P([(50, 96), (30, 58), (70, 58)], 3), "c"), (C(34, 46, 4), "b"), (C(66, 46, 4), "b")]


@mark("Nature")
def m_rabbit():
    return [(R(26, 2, 16, 48, 8), "a"), (R(58, 2, 16, 48, 8), "a"), (C(50, 64, 30), "a"), (C(40, 60, 4), "b"), (C(60, 60, 4), "b"), (C(50, 70, 4), "c")]


@mark("Nature")
def m_bee():
    body = R(22, 28, 56, 48, 24)
    out = [(body, "a")]
    for x in (38, 54):
        out.append((R(x, 28, 8, 48), "b"))
    out = [(body, "a"), (R(36, 28, 9, 48), "b"), (R(55, 28, 9, 48), "b")]
    return [(lens(34, 28, 12, 6, 8), "c"), (lens(66, 28, 88, 6, 8), "c")] + out


@mark("Nature")
def m_shell():
    out = [(p, "a" if i % 2 == 0 else "b") for i, p in enumerate([spin(lens(50, 92, 50, 8, 10), a, 50, 92) for a in (-60, -40, -20, 0, 20, 40, 60)])]
    return out


@mark("Nature")
def m_tulip():
    return [(L(50, 94, 50, 52, 7), "b"), (lens(50, 78, 22, 60, 8), "b"), (P([(24, 20), (36, 34), (50, 12), (64, 34), (76, 20), (76, 48), (50, 62), (24, 48)], 5), "a")]


@mark("Nature")
def m_cactus():
    return [(R(36, 8, 28, 86, 14), "a"), (U(R(8, 36, 14, 26, 7), R(8, 52, 40, 14, 7)), "a"), (U(R(78, 26, 14, 26, 7), R(52, 42, 40, 14, 7)), "a")]


@mark("Nature")
def m_mushroom():
    cap = A(50, 50, 44, 0, 180, 1)
    c = C(50, 52, 44).intersected(R(0, 0, 100, 52))
    return [(c, "a"), (R(34, 52, 32, 40, 8), "b"), (C(30, 36, 7), "c"), (C(62, 28, 6), "c"), (C(72, 44, 4), "c")]


@mark("Nature")
def m_wheat():
    out = [(L(50, 96, 50, 20, 5), "b")]
    for i in range(4):
        y = 70 - i * 16
        out.append((lens(50, y, 28, y - 16, 6), "a"))
        out.append((lens(50, y, 72, y - 16, 6), "a"))
    out.append((lens(50, 22, 50, 2, 6), "a"))
    return out


@mark("Nature")
def m_drops():
    d = lambda cx, cy, s: scale(move(U(C(50, 66, 24), P([(50, 6), (74, 56), (26, 56)], 1)), cx - 50, cy - 50), s, cx, cy)
    return [(d(36, 56, .8), "a"), (d(72, 36, .5), "b"), (d(72, 78, .45), "c")]


@mark("Nature")
def m_planet():
    e = QPainterPath()
    e.addEllipse(2, 34, 96, 32)
    ringp = stroked(spin(e, -24), 7)
    hidden = spin(R(0, 0, 100, 50), -24).intersected(C(50, 50, 29))
    return [(C(50, 50, 28), "a"), (ringp.subtracted(hidden), "b")]


@mark("Nature")
def m_rocket():
    body = lens(50, 4, 50, 82, 20)
    return [(body, "a"), (C(50, 38, 9), "c"), (P([(34, 56), (14, 84), (38, 76)], 2), "b"), (P([(66, 56), (86, 84), (62, 76)], 2), "b"), (P([(42, 84), (50, 98), (58, 84)], 2), "c")]


@mark("Nature")
def m_rainbow():
    return [(A(50, 82, 40 - i * 10, 0, 180, 8), r) for i, r in enumerate("abc")]


@mark("Nature")
def m_earth():
    return [(C(50, 50, 46), "a"), (U(P([(24, 20), (46, 14), (52, 36), (36, 50), (20, 40)], 4), P([(56, 56), (82, 48), (80, 78), (62, 88)], 4)), "b")]


@mark("Nature")
def m_wing():
    out = []
    for i in range(5):
        out.append((lens(10, 82 - i * 4, 94 - i * 12, 14 + i * 14, 8), "a" if i % 2 == 0 else "b"))
    return out


@mark("Nature")
def m_bamboo():
    out = []
    for i in range(3):
        y = 6 + i * 30
        out.append((R(38, y, 24, 26, 6), "a"))
    return out + [(lens(62, 30, 94, 14, 6), "b"), (lens(38, 60, 6, 46, 6), "b")]


@mark("Nature")
def m_acorn():
    return [(C(50, 62, 30).intersected(R(0, 50, 100, 50)).united(P([(50, 94), (34, 70), (66, 70)], 1)), "b"), (U(C(50, 46, 34).intersected(R(0, 0, 100, 48)), R(16, 40, 68, 14, 7)), "a"), (L(50, 10, 54, 2, 6), "a")]


# =============================================================== FOOD
@mark("Food")
def m_pizza():
    slice_ = P([(50, 94), (6, 20), (94, 20)], 6)
    crust = R(4, 8, 92, 16, 8)
    return [(slice_, "a"), (crust, "b"), (C(40, 40, 6), "c"), (C(60, 40, 6), "c"), (C(50, 62, 6), "c")]


@mark("Food")
def m_burger():
    top = C(50, 50, 44).intersected(R(0, 6, 100, 36))
    return [(top, "a"), (R(6, 46, 88, 10, 5), "c"), (R(8, 60, 84, 10, 5), "b"), (R(10, 74, 80, 16, 8), "a")]


@mark("Food")
def m_bean():
    b = lens(14, 86, 86, 14, 26)
    return [(b, "a"), (spin(L(22, 50, 78, 50, 6), -45), "b")]


@mark("Food")
def m_wine():
    bowl = P([(24, 6), (76, 6), (70, 44), (50, 58), (30, 44)], 8)
    return [(bowl, "a"), (R(46, 54, 8, 32, 2), "b"), (R(28, 86, 44, 8, 4), "b")]


@mark("Food")
def m_cutlery():
    fork = U(R(14, 4, 6, 34), R(26, 4, 6, 34), R(38, 4, 6, 34), R(14, 28, 30, 14, 7), R(22, 40, 14, 54, 6))
    knife = U(lens(68, 6, 68, 56, 10), R(62, 50, 12, 44, 6))
    return [(fork, "a"), (knife, "b")]


@mark("Food")
def m_cupcake():
    top = U(C(50, 34, 28), C(30, 42, 16), C(70, 42, 16))
    return [(top, "a"), (P([(18, 52), (82, 52), (72, 94), (28, 94)], 4), "b"), (C(50, 14, 7), "c")]


@mark("Food")
def m_icecream():
    return [(P([(26, 48), (74, 48), (50, 96)], 3), "b"), (U(C(50, 34, 28), R(20, 40, 60, 14, 7)), "a"), (C(50, 10, 6), "c")]


@mark("Food")
def m_chefhat():
    return [(U(C(30, 40, 22), C(50, 28, 26), C(70, 40, 22)), "a"), (R(24, 46, 52, 30, 4), "a"), (R(24, 76, 52, 16, 4), "b")]


@mark("Food")
def m_chili():
    p = QPainterPath()
    p.moveTo(30, 28)
    p.cubicTo(80, 20, 98, 60, 60, 94)
    p.cubicTo(86, 62, 50, 44, 22, 46)
    p.closeSubpath()
    return [(p, "a"), (U(R(14, 14, 18, 22, 6)), "b"), (L(22, 14, 20, 4, 6), "b")]


@mark("Food")
def m_apple():
    return [(U(C(34, 56, 30), C(66, 56, 30), R(24, 34, 52, 50, 18)), "a"), (lens(52, 26, 76, 8, 6), "b"), (L(50, 32, 50, 18, 6), "b")]


@mark("Food")
def m_cherries():
    return [(L(30, 70, 54, 12, 5), "b"), (L(70, 70, 54, 12, 5), "b"), (lens(54, 12, 88, 6, 7), "b"), (C(30, 74, 18), "a"), (C(70, 74, 18), "a")]


@mark("Food")
def m_lemon():
    return [(U(lens(8, 50, 92, 50, 36), C(8, 50, 4), C(92, 50, 4)), "a"), (spin(lens(30, 50, 70, 50, 16), 0), "c")]


@mark("Food")
def m_carrot():
    return [(P([(30, 22), (78, 70), (14, 92)], 6), "a"), (spin(lens(30, 22, 30, 2, 5), 10, 30, 22), "b"), (spin(lens(30, 22, 8, 12, 5), 0, 30, 22), "b"), (spin(lens(30, 22, 46, 6, 5), 0, 30, 22), "b")]


@mark("Food")
def m_bread():
    return [(U(R(6, 28, 88, 56, 26), C(30, 30, 22), C(70, 30, 22)), "a"), (L(34, 44, 40, 62, 5), "c"), (L(52, 44, 58, 62, 5), "c")]


@mark("Food")
def m_croissant():
    body = C(50, 56, 46).subtracted(C(50, 84, 42))
    cuts = [spin(L(50, 30, 50, 50, 4), a, 50, 90) for a in (-50, -25, 0, 25, 50)]
    return [(body, "a")] + [(c.intersected(body), "c") for c in cuts]


@mark("Food")
def m_bottle():
    return [(R(40, 4, 20, 22, 4), "b"), (R(28, 24, 44, 70, 14), "a"), (R(34, 50, 32, 24, 4), "c")]


@mark("Food")
def m_cake():
    return [(R(10, 50, 80, 40, 8), "a"), (R(10, 46, 80, 14, 7), "c"), (R(28, 24, 44, 24, 6), "b"), (R(46, 6, 8, 18, 3), "b"), (C(50, 6, 5), "c")]


@mark("Food")
def m_pot():
    return [(R(10, 36, 80, 50, 14), "a"), (R(4, 40, 14, 8, 4), "b"), (R(82, 40, 14, 8, 4), "b"), (R(14, 26, 72, 10, 5), "b"), (R(44, 14, 12, 12, 6), "c")]


@mark("Food")
def m_teacup():
    return [(R(8, 36, 66, 46, 20), "a"), (A(76, 56, 16, -80, 170, 8), "b"), (R(6, 86, 78, 8, 4), "b"), (L(30, 8, 30, 24, 5), "c"), (L(46, 8, 46, 24, 5), "c")]


@mark("Food")
def m_cloche():
    return [(C(50, 62, 42).intersected(R(0, 0, 100, 62)), "a"), (R(4, 64, 92, 10, 5), "b"), (C(50, 16, 7), "b")]


@mark("Food")
def m_beer():
    return [(R(14, 24, 52, 68, 8), "a"), (U(C(26, 20, 12), C(42, 16, 14), C(56, 22, 12)), "c"), (A(66, 54, 16, -90, 180, 9), "b")]


@mark("Food")
def m_cocktail():
    return [(P([(6, 10), (94, 10), (50, 56)], 4), "a"), (R(46, 54, 8, 32, 2), "b"), (R(28, 86, 44, 8, 4), "b"), (L(62, 4, 76, 26, 5), "c"), (C(80, 30, 9), "c")]


@mark("Food")
def m_donut():
    return [(ring(50, 50, 44, 28), "a"), (spin(R(24, 28, 10, 5, 2), 30), "c"), (spin(R(62, 22, 10, 5, 2), -20), "b"), (spin(R(66, 64, 10, 5, 2), 50), "c"), (spin(R(22, 64, 10, 5, 2), -40), "b")]


@mark("Food")
def m_egg():
    e = QPainterPath()
    e.addEllipse(14, 14, 72, 72)
    return [(U(C(50, 56, 36), C(46, 30, 24), C(64, 46, 24)), "a"), (C(52, 54, 16), "c")]


@mark("Food")
def m_grape():
    out = []
    pts = [(28, 38), (50, 38), (72, 38), (39, 58), (61, 58), (50, 78)]
    for x, y in pts:
        out.append((C(x, y, 11), "a"))
    return out + [(L(50, 28, 50, 8, 6), "b"), (lens(50, 12, 80, 4, 6), "b")]


@mark("Food")
def m_noodles():
    p = QPainterPath()
    for i in range(3):
        y = 30 + i * 12
        p.moveTo(14, y)
        p.cubicTo(30, y - 12, 44, y + 12, 60, y)
        p.cubicTo(70, y - 8, 80, y + 6, 88, y)
    return [(C(50, 62, 40).intersected(R(0, 50, 100, 50)), "a"), (stroked(p, 5), "c"), (L(70, 4, 40, 40, 5), "b"), (L(82, 8, 56, 40, 5), "b")]


# =============================================================== BUSINESS
@mark("Business")
def m_briefcase():
    return [(R(6, 28, 88, 62, 10), "a"), (R(34, 10, 32, 24, 6).subtracted(R(42, 18, 16, 16, 3)), "b"), (R(6, 52, 88, 8, 0), "c")]


@mark("Business")
def m_chartup():
    p = QPainterPath()
    p.moveTo(8, 76)
    p.lineTo(34, 50)
    p.lineTo(52, 62)
    p.lineTo(88, 22)
    return [(stroked(p, 9), "a"), (P([(70, 18), (94, 16), (90, 40)], 2), "a"), (L(8, 92, 92, 92, 6), "b")]


@mark("Business")
def m_barchart():
    return [(R(8, 54, 20, 40, 4), "a"), (R(40, 30, 20, 64, 4), "b"), (R(72, 8, 20, 86, 4), "a")]


@mark("Business")
def m_piechart():
    full = C(50, 50, 46)
    sl = QPainterPath()
    sl.moveTo(50, 50)
    sl.arcTo(4, 4, 92, 92, 90, -100)
    sl.closeSubpath()
    return [(full.subtracted(sl), "a"), (move(sl, 5, -5), "b")]


@mark("Business")
def m_coin():
    return [(ring(50, 50, 46, 8), "a"), (C(50, 50, 30), "b"), (ST(5, 20, 9, -90, 1), "a")]


@mark("Business")
def m_bulb():
    return [(U(C(50, 38, 30), P([(32, 56), (68, 56), (60, 74), (40, 74)], 2)), "a"), (R(38, 76, 24, 8, 3), "b"), (R(42, 86, 16, 8, 4), "b")]


@mark("Business")
def m_trophy():
    return [(P([(22, 8), (78, 8), (72, 50), (50, 64), (28, 50)], 8), "a"), (A(20, 28, 14, 90, 180, 6), "b"), (A(80, 28, 14, -90, 180, 6), "b"), (R(44, 60, 12, 20, 2), "b"), (R(28, 80, 44, 12, 4), "b")]


@mark("Business")
def m_medal():
    return [(P([(22, 4), (44, 4), (56, 38), (36, 38)], 1), "b"), (P([(78, 4), (56, 4), (44, 38), (64, 38)], 1), "c"), (ring(50, 66, 28, 8), "a"), (move(ST(5, 14, 6, -90, 1), 0, 16), "a")]


@mark("Business")
def m_key():
    return [(ring(30, 50, 26, 12), "a"), (R(52, 44, 44, 12, 4), "b"), (R(74, 56, 8, 14, 2), "b"), (R(86, 56, 8, 10, 2), "b")]


@mark("Business")
def m_lock():
    return [(R(16, 42, 68, 50, 10), "a"), (A(50, 42, 22, 0, 180, 10), "b"), (C(50, 62, 7), "b"), (R(47, 62, 6, 16, 2), "b")]


@mark("Business")
def m_shieldcheck():
    sh = P([(50, 4), (90, 18), (90, 50), (50, 96), (10, 50), (10, 18)], 8)
    ck = QPainterPath()
    ck.moveTo(30, 48)
    ck.lineTo(44, 62)
    ck.lineTo(70, 34)
    return [(sh, "a"), (stroked(ck, 9), "c")]


@mark("Business")
def m_flag():
    return [(R(14, 4, 8, 92, 3), "b"), (P([(22, 10), (90, 10), (74, 34), (90, 58), (22, 58)], 3), "a")]


@mark("Business")
def m_bell():
    return [(U(C(50, 40, 30), R(20, 40, 60, 28, 0), R(12, 64, 76, 12, 6)), "a"), (C(50, 84, 9), "b"), (C(50, 10, 6), "b")]


@mark("Business")
def m_mail():
    env = R(6, 20, 88, 62, 8)
    fl = QPainterPath()
    fl.moveTo(10, 28)
    fl.lineTo(50, 58)
    fl.lineTo(90, 28)
    return [(env, "a"), (stroked(fl, 7), "c")]


@mark("Business")
def m_phone():
    return [(R(26, 4, 48, 92, 10), "a"), (R(32, 14, 36, 64, 2), "c"), (C(50, 86, 4), "c")]


@mark("Business")
def m_pin():
    return [(U(C(50, 38, 32), P([(24, 56), (76, 56), (50, 96)], 2)), "a"), (C(50, 38, 12), "c")]


@mark("Business")
def m_globe():
    e = QPainterPath()
    e.addEllipse(30, 4, 40, 92)
    return [(ring(50, 50, 46, 7), "a"), (stroked(e, 5).intersected(C(50, 50, 44)), "b"), (L(8, 50, 92, 50, 5), "b"), (A(50, -20, 66, 235, 70, 5).intersected(C(50, 50, 44)), "b"), (A(50, 120, 66, 55, 70, 5).intersected(C(50, 50, 44)), "b")]


@mark("Business")
def m_calendar():
    return [(R(8, 14, 84, 80, 10), "a"), (R(8, 14, 84, 22, 0).intersected(R(8, 14, 84, 22, 10)), "b"), (R(26, 4, 8, 18, 3), "c"), (R(66, 4, 8, 18, 3), "c")] + [(C(26 + 24 * i, 56 + 0, 6), "c") for i in range(3)] + [(C(26 + 24 * i, 76, 6), "c") for i in range(2)]


@mark("Business")
def m_clock():
    h = QPainterPath()
    h.moveTo(50, 22)
    h.lineTo(50, 50)
    h.lineTo(70, 62)
    return [(ring(50, 50, 46, 8), "a"), (stroked(h, 7), "b")]


@mark("Business")
def m_cart():
    h = QPainterPath()
    h.moveTo(4, 12)
    h.lineTo(20, 12)
    h.lineTo(32, 64)
    h.lineTo(80, 64)
    return [(stroked(h, 8), "b"), (P([(24, 24), (92, 24), (82, 54), (30, 54)], 4), "a"), (C(38, 84, 8), "a"), (C(72, 84, 8), "a")]


@mark("Business")
def m_bag():
    return [(P([(14, 30), (86, 30), (92, 94), (8, 94)], 6), "a"), (A(50, 30, 20, 0, 180, 7), "b")]


@mark("Business")
def m_gift():
    return [(R(10, 40, 80, 52, 6), "a"), (R(6, 28, 88, 18, 5), "b"), (R(44, 28, 12, 64, 0), "c"), (A(36, 22, 14, 0, 270, 6), "c"), (A(64, 22, 14, 270, 270, 6), "c")]


@mark("Business")
def m_receipt():
    return [(P([(16, 4), (84, 4), (84, 96), (72, 88), (60, 96), (50, 88), (38, 96), (28, 88), (16, 96)], 2), "a")] + [(R(28, 22 + 16 * i, 44 + (i % 2) * 0, 7, 3), "c") for i in range(3)]


@mark("Business")
def m_handshake():
    return [(heartp(50, 52, .9).subtracted(L(50, 10, 50, 90, 6)), "a"), (L(50, 14, 50, 88, 6), "b")]


@mark("Business")
def m_target2():
    return [(ring(44, 56, 38, 8), "a"), (ring(44, 56, 20, 8), "a"), (C(44, 56, 5), "a"), (L(46, 54, 90, 10, 6), "b"), (P([(76, 6), (94, 6), (94, 24)], 1), "b")]


@mark("Business")
def m_ladder():
    return [(R(24, 4, 8, 92, 3), "a"), (R(68, 4, 8, 92, 3), "a")] + [(R(30, 14 + 20 * i, 40, 7, 3), "b") for i in range(5)]


@mark("Business")
def m_puzzle():
    base = U(R(12, 28, 60, 60, 4), C(42, 28, 12), C(72, 58, 12)).subtracted(C(12, 58, 12))
    return [(base, "a"), (R(60, 4, 32, 32, 6), "b")]


@mark("Business")
def m_stairs():
    return [(P([(6, 94), (6, 70), (30, 70), (30, 46), (54, 46), (54, 22), (94, 22), (94, 94)], 3), "a"), (R(54, 22, 40, 10, 0), "b")]


@mark("Business")
def m_scale():
    return [(R(46, 12, 8, 76, 2), "a"), (R(24, 86, 52, 8, 4), "a"), (L(12, 24, 88, 24, 7), "b"), (P([(2, 56), (30, 56), (16, 30)], 1).united(A(16, 56, 14, 0, 180, 1)), "c"), (P([(70, 56), (98, 56), (84, 30)], 1).united(A(84, 56, 14, 0, 180, 1)), "c")]


# =============================================================== TECH
@mark("Tech")
def m_monitor():
    return [(R(6, 10, 88, 58, 8), "a"), (R(14, 18, 72, 42, 2), "c"), (R(42, 68, 16, 14, 0), "b"), (R(26, 82, 48, 8, 4), "b")]


@mark("Tech")
def m_laptop():
    return [(R(16, 14, 68, 50, 6), "a"), (R(22, 20, 56, 38, 2), "c"), (P([(2, 70), (98, 70), (92, 88), (8, 88)], 3), "b")]


@mark("Tech")
def m_tablet():
    return [(R(10, 8, 80, 84, 10), "a"), (R(18, 16, 64, 64, 2), "c"), (C(50, 86, 3), "c")]


@mark("Tech")
def m_cloudup():
    return [(U(R(8, 40, 84, 42, 21), C(34, 40, 20), C(60, 32, 26), C(78, 48, 16)), "a"), (P([(50, 40), (68, 62), (32, 62)], 2), "c"), (R(44, 58, 12, 22, 0), "c")]


@mark("Tech")
def m_chip():
    out = [(R(24, 24, 52, 52, 6), "a"), (R(38, 38, 24, 24, 3), "c")]
    for i in range(3):
        v = 34 + i * 16
        out += [(R(v - 3, 6, 6, 18), "b"), (R(v - 3, 76, 6, 18), "b"), (R(6, v - 3, 18, 6), "b"), (R(76, v - 3, 18, 6), "b")]
    return out


@mark("Tech")
def m_code():
    a = QPainterPath()
    a.moveTo(34, 24)
    a.lineTo(8, 50)
    a.lineTo(34, 76)
    b = QPainterPath()
    b.moveTo(66, 24)
    b.lineTo(92, 50)
    b.lineTo(66, 76)
    return [(stroked(a, 10), "a"), (stroked(b, 10), "a"), (L(56, 16, 44, 84, 8), "b")]


@mark("Tech")
def m_database():
    return [(R(10, 8 + i * 28, 80, 24, 12), "a" if i != 1 else "b") for i in range(3)]


@mark("Tech")
def m_battery():
    return [(R(4, 28, 84, 44, 8).subtracted(R(12, 36, 68, 28, 3)), "a"), (R(92, 40, 6, 20, 3), "a"), (R(16, 40, 40, 20, 2), "b")]


@mark("Tech")
def m_plug():
    return [(R(24, 6, 10, 26), "b"), (R(66, 6, 10, 26), "b"), (R(14, 28, 72, 30, 10), "a"), (P([(26, 56), (74, 56), (60, 76), (40, 76)], 2), "a"), (R(44, 74, 12, 22, 3), "b")]


@mark("Tech")
def m_power():
    return [(A(50, 54, 36, 120, 300, 10), "a"), (R(44, 4, 12, 46, 6), "b")]


@mark("Tech")
def m_headphones():
    return [(A(50, 54, 38, 0, 180, 10), "a"), (R(8, 54, 18, 34, 8), "b"), (R(74, 54, 18, 34, 8), "b")]


@mark("Tech")
def m_mic():
    return [(R(34, 4, 32, 56, 16), "a"), (A(50, 46, 28, 180, 180, 7), "b"), (R(47, 74, 6, 16), "b"), (R(30, 88, 40, 7, 3), "b")]


@mark("Tech")
def m_note():
    return [(R(50, 12, 10, 62), "a"), (C(38, 76, 16), "a"), (P([(56, 12), (88, 26), (88, 44), (56, 30)], 2), "b")]


@mark("Tech")
def m_notes():
    return [(R(28, 14, 8, 56), "a"), (R(72, 8, 8, 56), "a"), (C(20, 70, 14), "a"), (C(64, 64, 14), "a"), (P([(30, 14), (80, 6), (80, 24), (30, 32)], 2), "b")]


@mark("Tech")
def m_play():
    return [(ring(50, 50, 46, 8), "a"), (P([(38, 28), (72, 50), (38, 72)], 4), "b")]


@mark("Tech")
def m_clapper():
    return [(R(8, 36, 84, 56, 6), "a"), (spin(R(8, 20, 84, 18, 4), -10, 8, 36), "b")] + [(spin(R(14 + i * 20, 20, 10, 18, 0), -10, 8, 36), "c") for i in range(4)]


@mark("Tech")
def m_gamepad():
    return [(R(4, 26, 92, 48, 24), "a"), (R(20, 42, 24, 8, 3), "c"), (R(28, 34, 8, 24, 3), "c"), (C(68, 40, 5), "c"), (C(80, 54, 5), "c")]


@mark("Tech")
def m_search():
    return [(ring(40, 40, 32, 10), "a"), (spin(R(66, 62, 12, 36, 6), -45, 72, 68), "b")]


@mark("Tech")
def m_wrench():
    return [(spin(U(R(42, 36, 16, 60, 8), ring(50, 24, 24, 12).subtracted(R(40, 0, 20, 22))), 40), "a")]


@mark("Tech")
def m_hammer():
    return [(spin(U(R(42, 30, 16, 66, 4)), -40), "b"), (spin(R(20, 10, 60, 24, 5), -40), "a")]


@mark("Tech")
def m_scissors():
    return [(spin(L(50, 50, 50, 4, 8), 25), "a"), (spin(L(50, 50, 50, 4, 8), -25), "a"), (ring(30, 76, 14, 7), "b"), (ring(70, 76, 14, 7), "b")]


@mark("Tech")
def m_brush():
    return [(spin(R(44, 40, 12, 56, 5), 35, 50, 60), "b"), (spin(P([(36, 36), (64, 36), (60, 6), (40, 6)], 6), 35, 50, 60), "a")]


@mark("Tech")
def m_pencil():
    return [(spin(U(R(38, 6, 24, 62, 4), P([(38, 68), (62, 68), (50, 96)], 2)), 40), "a"), (spin(R(38, 6, 24, 14, 4), 40), "b")]


@mark("Tech")
def m_ruler():
    return [(spin(R(0, 36, 100, 28, 4), -35), "a")] + [(spin(R(12 + i * 16, 36, 4, 12 if i % 2 else 18, 0), -35), "c") for i in range(5)]


@mark("Tech")
def m_palette():
    p = U(C(50, 50, 46)).subtracted(C(70, 80, 14))
    return [(p, "a"), (C(30, 40, 8), "b"), (C(50, 24, 8), "c"), (C(72, 36, 8), "b"), (C(76, 58, 8), "c")]


@mark("Tech")
def m_nib():
    return [(P([(50, 94), (20, 46), (28, 8), (72, 8), (80, 46)], 6), "a"), (L(50, 94, 50, 40, 5), "c"), (C(50, 42, 7), "c")]


@mark("Tech")
def m_quote():
    q = lambda x: U(C(x + 12, 36, 14), P([(x - 2, 38), (x + 26, 38), (x + 12, 76)], 2))
    return [(move(q(8), 0, 0), "a"), (move(q(54), 0, 0), "b")]


@mark("Tech")
def m_hash():
    return [(spin(L(34, 12, 30, 88, 9), 0), "a"), (L(66, 12, 62, 88, 9), "a"), (L(10, 36, 90, 36, 9), "b"), (L(10, 66, 90, 66, 9), "b")]


@mark("Tech")
def m_at():
    return [(A(50, 50, 40, 0, 330, 10), "a"), (ring(50, 50, 16, 8), "b"), (L(66, 40, 66, 58, 8), "b")]


@mark("Tech")
def m_braces():
    a = QPainterPath()
    a.moveTo(34, 6)
    a.cubicTo(18, 6, 26, 40, 8, 50)
    a.cubicTo(26, 60, 18, 94, 34, 94)
    b = QPainterPath()
    b.moveTo(66, 6)
    b.cubicTo(82, 6, 74, 40, 92, 50)
    b.cubicTo(74, 60, 82, 94, 66, 94)
    return [(stroked(a, 9), "a"), (stroked(b, 9), "b")]


@mark("Tech")
def m_binary():
    return [(ring(24, 24, 16, 8), "a"), (R(62, 8, 8, 32, 3), "b"), (R(8, 62, 8, 32, 3), "b"), (ring(76, 76, 16, 8), "a")]


@mark("Tech")
def m_network():
    ps = [(50, 20), (16, 78), (84, 78)]
    out = [(L(*ps[0], *ps[1], 5), "b"), (L(*ps[1], *ps[2], 5), "b"), (L(*ps[0], *ps[2], 5), "b")]
    return out + [(C(x, y, 14), "a") for x, y in ps]


@mark("Tech")
def m_signal():
    return [(R(8 + i * 22, 70 - i * 20, 14, 24 + i * 20, 4), "a" if i < 3 else "b") for i in range(4)]


@mark("Tech")
def m_cursor():
    return [(P([(20, 6), (20, 80), (40, 62), (54, 94), (68, 88), (54, 56), (80, 54)], 3), "a")]


@mark("Tech")
def m_pixelheart():
    pts = ["..XX..XX..", ".XXXXXXXX.", "XXXXXXXXXX", "XXXXXXXXXX", ".XXXXXXXX.", "..XXXXXX..", "...XXXX...", "....XX...."]
    out = []
    for r, row in enumerate(pts):
        for c, ch in enumerate(row):
            if ch == "X":
                out.append((R(5 + c * 9, 14 + r * 9, 8.4, 8.4, 1), "a" if r < 4 else "b"))
    return out


@mark("Tech")
def m_qrlike():
    out = []
    for (x, y) in ((8, 8), (62, 8), (8, 62)):
        out.append((R(x, y, 30, 30, 5).subtracted(R(x + 8, y + 8, 14, 14, 2)), "a"))
        out.append((R(x + 11, y + 11, 8, 8, 1), "b"))
    return out + [(R(50 + 12 * i, 50 + 12 * j, 8, 8, 1), "b") for i in range(3) for j in range(3) if (i + j) % 2 == 0]


@mark("Tech")
def m_drone():
    return [(R(36, 40, 28, 18, 6), "a"), (L(36, 44, 12, 28, 5), "b"), (L(64, 44, 88, 28, 5), "b"), (R(2, 22, 22, 6, 3), "c"), (R(76, 22, 22, 6, 3), "c")]


@mark("Tech")
def m_fingerprint():
    return [(A(50, 56, 12 + i * 9, 200, 220 + i * 5, 4), "a" if i % 2 == 0 else "b") for i in range(5)]


@mark("Tech")
def m_robot():
    return [(R(14, 24, 72, 56, 14), "a"), (R(46, 8, 8, 18, 3), "b"), (C(50, 8, 6), "b"), (C(34, 50, 9), "c"), (C(66, 50, 9), "c"), (R(34, 66, 32, 6, 3), "b"), (R(4, 40, 10, 20, 4), "b"), (R(86, 40, 10, 20, 4), "b")]


# =============================================================== PEOPLE & PLACES
@mark("People")
def m_user():
    return [(C(50, 30, 22), "a"), (C(50, 100, 42).intersected(R(0, 54, 100, 46)), "b")]


@mark("People")
def m_users():
    return [(C(30, 32, 16), "b"), (C(30, 90, 30).intersected(R(0, 52, 60, 46)), "b"), (C(66, 28, 20), "a"), (C(66, 100, 36).intersected(R(20, 52, 100, 46)), "a")]


@mark("People")
def m_smile():
    return [(C(50, 50, 46), "a"), (C(34, 40, 6), "c"), (C(66, 40, 6), "c"), (A(50, 52, 26, 200, 140, 7), "c")]


@mark("People")
def m_thumb():
    return [(R(6, 42, 20, 48, 4), "b"), (P([(32, 42), (50, 6), (64, 12), (58, 38), (92, 38), (86, 84), (32, 90)], 7), "a")]


@mark("People")
def m_hand():
    out = [(R(14 + i * 17, 8 + (1 if i in (1, 2) else 0) * -4 + (3 if i == 0 else 0) * 4, 12, 48, 6), "a") for i in range(4)]
    return out + [(R(14, 44, 68, 48, 20), "a"), (spin(R(66, 34, 12, 38, 6), 40), "b")]


@mark("People")
def m_graduate():
    return [(P([(50, 14), (98, 36), (50, 58), (2, 36)], 2), "a"), (P([(24, 50), (24, 72), (50, 84), (76, 72), (76, 50), (50, 62)], 3), "b"), (L(92, 40, 92, 70, 5), "c")]


@mark("People")
def m_baby():
    return [(C(50, 52, 38), "a"), (C(36, 52, 5), "c"), (C(64, 52, 5), "c"), (A(50, 58, 14, 210, 120, 5), "c"), (A(50, 14, 14, 270, 200, 6), "b")]


@mark("People")
def m_house():
    return [(P([(50, 6), (96, 48), (4, 48)], 5), "a"), (R(16, 46, 68, 46, 4), "b"), (R(42, 62, 16, 30, 2), "c")]


@mark("People")
def m_building():
    out = [(R(18, 6, 64, 88, 4), "a")]
    for r in range(4):
        for c in range(3):
            out.append((R(28 + c * 18, 16 + r * 16, 10, 9, 1), "c"))
    return out


@mark("People")
def m_shop():
    return [(P([(8, 34), (20, 8), (80, 8), (92, 34)], 2), "b"), (R(8, 34, 84, 10, 0), "a"), (R(14, 44, 72, 48, 2), "a"), (R(40, 60, 20, 32, 2), "c")]


@mark("People")
def m_castle():
    return [(R(10, 36, 80, 58, 2), "a")] + [(R(10 + i * 30, 22, 20, 18, 0), "a") for i in range(3)] + [(R(42, 62, 16, 32, 8), "c")]


@mark("People")
def m_tent():
    return [(P([(50, 8), (96, 90), (4, 90)], 4), "a"), (P([(50, 40), (68, 90), (32, 90)], 2), "c")]


@mark("People")
def m_church():
    return [(R(40, 4, 20, 20, 2), "b"), (P([(50, 0), (66, 20), (34, 20)], 1), "b"), (R(24, 36, 52, 58, 2), "a"), (A(50, 94, 12, 0, 180, 1).__class__() if False else R(44, 64, 12, 30, 6), "c")]


@mark("People")
def m_lighthouse():
    return [(P([(36, 30), (64, 30), (72, 94), (28, 94)], 2), "a"), (R(30, 12, 40, 18, 4), "b"), (R(24, 6, 52, 6, 2), "a"), (L(76, 18, 98, 8, 4), "c"), (L(24, 18, 2, 8, 4), "c")]


@mark("People")
def m_bridge():
    return [(R(2, 56, 96, 8, 2), "a"), (A(50, 64, 40, 0, 180, 7).__class__() if False else A(50, 20, 44, 180, 180, 7), "b"), (R(14, 36, 6, 28, 0), "b"), (R(80, 36, 6, 28, 0), "b"), (R(47, 34, 6, 30, 0), "b"), (R(2, 76, 96, 6, 2), "c")]


# =============================================================== TRAVEL
@mark("Travel")
def m_car():
    return [(U(R(4, 44, 92, 34, 10), P([(24, 44), (34, 20), (66, 20), (80, 44)], 6)), "a"), (C(28, 78, 12), "b"), (C(72, 78, 12), "b"), (P([(38, 28), (62, 28), (70, 42), (34, 42)], 2), "c")]


@mark("Travel")
def m_bike():
    return [(ring(24, 68, 20, 6), "a"), (ring(76, 68, 20, 6), "a"), (L(24, 68, 44, 34, 5), "b"), (L(44, 34, 76, 68, 5), "b"), (L(44, 34, 66, 34, 5), "b"), (L(24, 68, 54, 68, 5), "b"), (L(40, 28, 52, 28, 6), "c")]


@mark("Travel")
def m_plane():
    return [(spin(U(lens(50, 4, 50, 96, 8), P([(50, 40), (96, 64), (96, 72), (50, 62)], 2), P([(50, 40), (4, 64), (4, 72), (50, 62)], 2), P([(50, 80), (72, 92), (72, 96), (50, 90)], 1), P([(50, 80), (28, 92), (28, 96), (50, 90)], 1)), 0), "a")]


@mark("Travel")
def m_ship():
    return [(P([(6, 60), (94, 60), (80, 90), (20, 90)], 4), "a"), (R(30, 36, 40, 24, 3), "b"), (R(44, 18, 12, 18, 2), "c"), (R(6, 94, 88, 4, 2), "b")]


@mark("Travel")
def m_sailboat():
    return [(P([(50, 6), (50, 66), (14, 66)], 2), "a"), (P([(56, 20), (56, 66), (88, 66)], 2), "b"), (P([(6, 74), (94, 74), (80, 92), (20, 92)], 4), "c")]


@mark("Travel")
def m_truck():
    return [(R(2, 22, 58, 52, 4), "a"), (P([(62, 36), (84, 36), (98, 54), (98, 74), (62, 74)], 4), "b"), (C(24, 78, 11), "c"), (C(76, 78, 11), "c")]


@mark("Travel")
def m_bus():
    return [(R(8, 8, 84, 76, 12), "a"), (R(16, 18, 68, 26, 3), "c"), (C(28, 66, 6), "c"), (C(72, 66, 6), "c"), (R(14, 84, 14, 12, 3), "b"), (R(72, 84, 14, 12, 3), "b")]


@mark("Travel")
def m_train():
    return [(R(18, 6, 64, 72, 16), "a"), (R(26, 16, 48, 24, 3), "c"), (C(34, 60, 6), "c"), (C(66, 60, 6), "c"), (L(26, 94, 38, 76, 6), "b"), (L(74, 94, 62, 76, 6), "b")]


@mark("Travel")
def m_helmet():
    return [(C(50, 56, 42).intersected(R(0, 0, 100, 62)), "a"), (R(8, 56, 84, 12, 6), "b"), (L(30, 14, 30, 50, 6), "c"), (L(50, 10, 50, 50, 6), "c"), (L(70, 14, 70, 50, 6), "c")]


@mark("Travel")
def m_suitcase():
    return [(R(8, 28, 84, 62, 10), "a"), (A(50, 28, 16, 0, 180, 7), "b"), (R(24, 40, 7, 38, 3), "c"), (R(69, 40, 7, 38, 3), "c")]


@mark("Travel")
def m_map():
    return [(P([(4, 20), (34, 10), (66, 22), (96, 12), (96, 80), (66, 90), (34, 78), (4, 88)], 3), "a"), (L(34, 10, 34, 78, 4), "c"), (L(66, 22, 66, 90, 4), "c")]


@mark("Travel")
def m_compass2():
    return [(ring(50, 50, 46, 7), "a"), (P([(50, 14), (62, 50), (50, 86), (38, 50)], 1).__class__() if False else spin(P([(50, 14), (60, 50), (50, 50), (40, 50)], 1), 30), "b"), (spin(P([(50, 86), (60, 50), (40, 50)], 1), 30), "c")]


@mark("Travel")
def m_anchor2():
    return [(ring(50, 18, 12, 6), "a"), (R(46, 28, 8, 60, 2), "a"), (L(30, 40, 70, 40, 6), "a"), (A(50, 62, 32, 0, -180, 9), "b")]


@mark("Travel")
def m_wheel():
    out = [(ring(50, 50, 40, 7), "a"), (C(50, 50, 12), "b")]
    out += [(p, "a") for p in fan(L(50, 12, 50, 38, 5), 8)]
    out += [(p, "b") for p in fan(C(50, 6, 5), 8)]
    return out


# =============================================================== SPORT & HEALTH
@mark("Sport")
def m_dumbbell():
    return [(R(4, 34, 14, 32, 4), "a"), (R(20, 24, 14, 52, 4), "a"), (R(34, 44, 32, 12, 2), "b"), (R(66, 24, 14, 52, 4), "a"), (R(82, 34, 14, 32, 4), "a")]


@mark("Sport")
def m_ball():
    return [(C(50, 50, 46), "a"), (N(5, 16, -90, 2), "c"), (L(50, 34, 50, 6, 4), "c"), (L(64, 56, 90, 42, 4), "c"), (L(36, 56, 10, 42, 4), "c"), (L(42, 66, 30, 92, 4), "c"), (L(58, 66, 70, 92, 4), "c")]


@mark("Sport")
def m_basketball():
    return [(ring(50, 50, 46, 6), "a"), (L(50, 6, 50, 94, 5), "a"), (L(6, 50, 94, 50, 5), "a"), (A(-4, 50, 50, -50, 100, 5).intersected(C(50, 50, 46)), "b"), (A(104, 50, 50, 130, 100, 5).intersected(C(50, 50, 46)), "b")]


@mark("Sport")
def m_tennis():
    return [(C(50, 50, 46), "a"), (A(-8, 50, 50, -60, 120, 6).intersected(C(50, 50, 46)), "c"), (A(108, 50, 50, 120, 120, 6).intersected(C(50, 50, 46)), "c")]


@mark("Sport")
def m_racket():
    return [(ring(40, 36, 30, 8), "a"), (spin(R(36, 62, 8, 34, 4), 40, 40, 36).__class__() if False else spin(R(36, 62, 10, 36, 4), 40, 40, 36), "b"), (A(40, 36, 18, 0, 360, 2), "c")]


@mark("Sport")
def m_whistle():
    return [(U(C(36, 56, 28), R(36, 28, 60, 26, 6)), "a"), (C(36, 56, 10), "c"), (R(70, 32, 6, 10, 0), "b")]


@mark("Sport")
def m_flagrace():
    out = []
    for r in range(3):
        for c in range(4):
            out.append((R(14 + c * 18, 8 + r * 16, 18, 16), "a" if (r + c) % 2 == 0 else "b"))
    return out + [(R(6, 4, 8, 92, 3), "c")]


@mark("Sport")
def m_swim():
    return [(C(70, 26, 12), "a"), (A(30, 70, 24, 200, 140, 8), "b"), (A(70, 70, 24, 200, 140, 8), "b"), (L(14, 46, 60, 34, 9), "a")]


@mark("Sport")
def m_yoga():
    return [(C(50, 18, 12), "a"), (L(50, 32, 50, 62, 10), "a"), (L(50, 40, 18, 28, 8), "b"), (L(50, 40, 82, 28, 8), "b"), (L(50, 62, 20, 90, 9), "a"), (L(50, 62, 80, 90, 9), "a")]


@mark("Sport")
def m_run():
    return [(C(60, 14, 11), "a"), (L(56, 30, 42, 60, 10), "a"), (L(56, 30, 84, 42, 8), "b"), (L(48, 40, 22, 40, 8), "b"), (L(42, 60, 18, 92, 9), "a"), (L(42, 60, 70, 76, 9), "a")]


@mark("Sport")
def m_medcross():
    return [(U(R(34, 6, 32, 88, 8), R(6, 34, 88, 32, 8)), "a"), (R(42, 20, 16, 60, 3), "c"), (R(20, 42, 60, 16, 3), "c")]


@mark("Sport")
def m_pill():
    return [(spin(R(4, 30, 92, 40, 20), -40), "a"), (spin(R(4, 30, 46, 40, 20).intersected(R(4, 30, 46, 40, 20)), -40).__class__(), "a")] if False else [(spin(R(4, 30, 92, 40, 20), -40), "a"), (spin(U(R(50, 30, 46, 40, 0).intersected(R(4, 30, 92, 40, 20))), -40), "b")]


@mark("Sport")
def m_tooth():
    p = QPainterPath()
    p.moveTo(50, 20)
    p.cubicTo(30, 4, 6, 14, 10, 40)
    p.cubicTo(12, 58, 24, 62, 26, 94)
    p.cubicTo(34, 100, 40, 80, 50, 70)
    p.cubicTo(60, 80, 66, 100, 74, 94)
    p.cubicTo(76, 62, 88, 58, 90, 40)
    p.cubicTo(94, 14, 70, 4, 50, 20)
    return [(p, "a")]


@mark("Sport")
def m_pulse():
    p = QPainterPath()
    p.moveTo(4, 52)
    for pt in [(26, 52), (36, 22), (50, 84), (62, 40), (70, 52), (96, 52)]:
        p.lineTo(*pt)
    return [(stroked(p, 9), "a")]


@mark("Sport")
def m_drop2():
    return [(U(C(50, 64, 30), P([(50, 4), (76, 54), (24, 54)], 2)), "a"), (spin(lens(36, 70, 36, 52, 4), 0), "c")]


@mark("Sport")
def m_heartcross():
    return [(heartp(50, 52, .95), "a"), (U(R(44, 30, 12, 34), R(33, 41, 34, 12)), "c")]


@mark("Sport")
def m_dna():
    out = []
    p = QPainterPath()
    q = QPainterPath()
    for i in range(0, 101, 5):
        x = 50 + 28 * math.sin(i / 100 * 4 * math.pi)
        y = 4 + i * .92
        (p.moveTo if i == 0 else p.lineTo)(x, y)
        x2 = 100 - x
        (q.moveTo if i == 0 else q.lineTo)(x2, y)
    out += [(stroked(p, 7), "a"), (stroked(q, 7), "b")]
    out += [(L(50 + 28 * math.sin(i / 8 * 4 * math.pi), 4 + i / 8 * 92, 50 - 28 * math.sin(i / 8 * 4 * math.pi), 4 + i / 8 * 92, 4), "c") for i in range(1, 8)]
    return out


# =============================================================== SYMBOLS
@mark("Symbols")
def m_heart():
    return [(heartp(50, 52, 1.0), "a")]


@mark("Symbols")
def m_heartline():
    return [(heartp(50, 52, 1.0).subtracted(heartp(50, 50, .66)), "a")]


@mark("Symbols")
def m_hearts():
    return [(heartp(36, 56, .6), "a"), (heartp(70, 38, .42), "b"), (heartp(74, 76, .32), "c")]


@mark("Symbols")
def m_halfheart():
    h = heartp(50, 52, 1.0)
    return [(h.intersected(R(0, 0, 50, 100)), "a"), (h.intersected(R(50, 0, 50, 100)), "b")]


@mark("Symbols")
def m_peace():
    return [(ring(50, 50, 46, 8), "a"), (L(50, 6, 50, 94, 8), "a"), (L(50, 50, 20, 80, 8), "a"), (L(50, 50, 80, 80, 8), "a")]


@mark("Symbols")
def m_ankh():
    return [(ring(50, 26, 20, 9), "a"), (R(45, 44, 10, 52, 3), "a"), (R(20, 56, 60, 10, 3), "b")]


@mark("Symbols")
def m_hamsa():
    return [(P([(20, 94), (14, 40), (24, 40), (26, 14), (38, 14), (38, 34), (42, 34), (44, 6), (56, 6), (58, 34), (62, 34), (62, 14), (74, 14), (76, 40), (86, 40), (80, 94)], 6), "a"), (ring(50, 62, 12, 5), "c"), (C(50, 62, 4), "c")]


@mark("Symbols")
def m_infinity2():
    p = QPainterPath()
    p.moveTo(50, 50)
    p.cubicTo(66, 20, 96, 20, 96, 50)
    p.cubicTo(96, 80, 66, 80, 50, 50)
    p.cubicTo(34, 20, 4, 20, 4, 50)
    p.cubicTo(4, 80, 34, 80, 50, 50)
    return [(stroked(p, 12), "a")]


@mark("Symbols")
def m_music():
    return [(ring(50, 50, 46, 8), "a"), (R(54, 24, 6, 36, 2), "b"), (C(46, 62, 10), "b"), (P([(58, 24), (74, 32), (74, 40), (58, 32)], 1), "b")]


@mark("Symbols")
def m_yingstar():
    return [(ST(4, 48, 24, -90, 2).subtracted(C(50, 50, 12)), "a"), (C(50, 50, 6), "b")]


@mark("Symbols")
def m_sparkles():
    return [(ST(4, 40, 10, -90, 1), "a"), (move(ST(4, 18, 5, -90, 1), 30, -30), "b"), (move(ST(4, 14, 4, -90, 1), -34, 36), "c")]


@mark("Symbols")
def m_crown2():
    return [(P([(6, 80), (6, 30), (28, 52), (50, 14), (72, 52), (94, 30), (94, 80)], 4), "a"), (R(6, 82, 88, 10, 3), "b"), (C(6, 28, 6), "c"), (C(50, 12, 6), "c"), (C(94, 28, 6), "c")]


@mark("Symbols")
def m_diamond2():
    return [(P([(22, 10), (78, 10), (98, 38), (50, 94), (2, 38)], 4), "a"), (P([(2, 38), (98, 38), (50, 94)], 1), "b"), (P([(30, 10), (22, 38), (50, 38)], 1).__class__() if False else L(36, 10, 26, 38, 3), "c")]


@mark("Symbols")
def m_clover():
    return [(spin(heartp(50, 28, .42), a, 50, 50), r) for a, r in ((0, "a"), (90, "b"), (180, "a"), (270, "b"))] + [(L(50, 50, 66, 94, 6), "c")]


@mark("Symbols")
def m_horseshoe():
    return [(A(50, 46, 34, 160, 220, 14).__class__() if False else A(50, 46, 34, -40, 260, 16), "a")] + [(C(50 + 34 * math.cos(math.radians(a)), 46 - 34 * math.sin(math.radians(a)), 3), "c") for a in (-20, 20, 60, 160, 200, 240)]


@mark("Symbols")
def m_dice():
    return [(R(8, 8, 84, 84, 18), "a")] + [(C(x, y, 8), "c") for x, y in ((28, 28), (72, 28), (50, 50), (28, 72), (72, 72))]


@mark("Symbols")
def m_cards():
    return [(spin(R(14, 12, 48, 70, 8), -12, 38, 50), "b"), (spin(R(38, 14, 48, 70, 8), 10, 62, 50), "a"), (move(ST(4, 12, 4, -90, 1), 24, 0), "c")]


@mark("Symbols")
def m_spade():
    return [(spin(heartp(50, 44, .95), 180), "a"), (P([(50, 56), (62, 94), (38, 94)], 2), "a")]


@mark("Symbols")
def m_bolt2():
    return [(P([(58, 4), (18, 56), (46, 56), (38, 96), (82, 40), (54, 40)], 3), "a")]


@mark("Symbols")
def m_flowerpot():
    return [(P([(22, 56), (78, 56), (70, 94), (30, 94)], 3), "b"), (R(16, 48, 68, 12, 4), "b"), (L(50, 48, 50, 28, 5), "a"), (U(*[p for p in fan(lens(50, 22, 50, 4, 6), 6, 50, 22)]), "a")]


@mark("Symbols")
def m_hourglass():
    return [(P([(20, 6), (80, 6), (80, 14), (54, 50), (80, 86), (80, 94), (20, 94), (20, 86), (46, 50), (20, 14)], 3), "a"), (P([(34, 82), (66, 82), (50, 62)], 1), "b")]


@mark("Symbols")
def m_umbrella():
    return [(C(50, 52, 46).intersected(R(0, 0, 100, 52)), "a"), (A(50, 80, 10, 180, 180, 7), "b"), (R(47, 50, 6, 30, 2), "b")]


@mark("Symbols")
def m_glasses():
    return [(ring(26, 56, 22, 7), "a"), (ring(74, 56, 22, 7), "a"), (A(50, 56, 8, 0, 180, 6), "b")]


@mark("Symbols")
def m_balloon():
    return [(lens(50, 8, 50, 70, 30), "a"), (P([(44, 70), (56, 70), (50, 78)], 1), "a"), (A(50, 88, 10, 90, 180, 3).__class__() if False else A(50, 86, 8, 90, 360, 3), "b")]


@mark("Symbols")
def m_boat2():
    return [(P([(4, 56), (96, 56), (74, 92), (26, 92)], 5), "a"), (L(50, 56, 50, 6, 5), "b"), (P([(54, 10), (86, 50), (54, 50)], 2), "c")]


for _n in ("swim", "ball", "racket", "bridge", "spade"):
    MARKS.pop(_n, None)
    CATS.pop(_n, None)
