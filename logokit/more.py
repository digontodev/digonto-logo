"""More logo shapes: extra badge containers and 30 extra marks (all original, drawn in a 100 x 100 box)."""
import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QPainterPath, QTransform

from .marks import _arc, circle, ngon, polygon, rrect, stroked


def _rot(p, deg, cx=50, cy=50):
    return QTransform().translate(cx, cy).rotate(deg).translate(-cx, -cy).map(p)


def _star(cx, cy, ro, ri, n, rot=-90, rad=0):
    pts = []
    for i in range(n * 2):
        r = ro if i % 2 == 0 else ri
        a = math.radians(rot + 180 * i / n)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return polygon(pts, rad)


# ------------------------------------------------------------------ containers
CONTAINERS = ["pill", "seal", "octagon", "ticket", "tag", "cloud", "banner", "triangle", "heart", "stamp", "drop"]


def container(kind):
    if kind == "pill":
        return rrect(0, 22, 100, 56, 28)
    if kind == "seal":
        pts = []
        for i in range(72):
            r = 50 if (i // 3) % 2 == 0 else 45
            a = math.radians(-90 + 360 * i / 72)
            pts.append((50 + r * math.cos(a), 50 + r * math.sin(a)))
        return polygon(pts, 2)
    if kind == "octagon":
        return ngon(50, 50, 52, 8, -67.5, 6)
    if kind == "ticket":
        p = rrect(0, 14, 100, 72, 10)
        return p.subtracted(circle(0, 50, 11)).subtracted(circle(100, 50, 11))
    if kind == "tag":
        p = polygon([(0, 12), (68, 12), (100, 50), (68, 88), (0, 88)], 8)
        return p.subtracted(circle(16, 50, 6))
    if kind == "cloud":
        p = rrect(8, 44, 84, 42, 21)
        for cx, cy, r in ((32, 44, 22), (58, 36, 28), (76, 52, 18)):
            p = p.united(circle(cx, cy, r))
        return p.simplified()
    if kind == "banner":
        p = polygon([(0, 18), (100, 18), (88, 50), (100, 82), (0, 82), (12, 50)], 3)
        return p
    if kind == "triangle":
        return polygon([(50, 4), (98, 90), (2, 90)], 12)
    if kind == "heart":
        p = QPainterPath()
        p.moveTo(50, 92)
        p.cubicTo(10, 62, 0, 40, 0, 28)
        p.cubicTo(0, 10, 16, 2, 28, 2)
        p.cubicTo(40, 2, 48, 12, 50, 20)
        p.cubicTo(52, 12, 60, 2, 72, 2)
        p.cubicTo(84, 2, 100, 10, 100, 28)
        p.cubicTo(100, 40, 90, 62, 50, 92)
        p.closeSubpath()
        return p
    if kind == "stamp":
        p = rrect(4, 4, 92, 92, 4)
        for i in range(8):
            for x, y in ((6 + i * 12.5, 4), (6 + i * 12.5, 96), (4, 6 + i * 12.5), (96, 6 + i * 12.5)):
                p = p.subtracted(circle(x, y, 3.2))
        return p
    if kind == "drop":
        p = QPainterPath()
        p.moveTo(50, 0)
        p.cubicTo(50, 0, 96, 46, 96, 68)
        p.cubicTo(96, 88, 76, 100, 50, 100)
        p.cubicTo(24, 100, 4, 88, 4, 68)
        p.cubicTo(4, 46, 50, 0, 50, 0)
        return p
    return rrect(0, 0, 100, 100, 0)


# ------------------------------------------------------------------ marks
def m_hexcluster():
    out = []
    for i, (dx, dy, r) in enumerate(((0, 0, "b"), (0, -29, "a"), (25, -14.5, "a"), (25, 14.5, "a"), (0, 29, "a"), (-25, 14.5, "a"), (-25, -14.5, "a"))):
        out.append((ngon(50 + dx, 50 + dy, 13.5, 6, -90, 2), r))
    return out


def m_crescent():
    moon = circle(46, 50, 40).subtracted(circle(62, 44, 33))
    return [(moon, "a"), (_star(76, 28, 12, 5, 5, -90, 1), "b")]


def m_sunrise():
    out = [(circle(50, 64, 26).intersected(rrect(0, 0, 100, 64, 0)), "b")]
    for i in range(7):
        a = 180 + i * 30
        r1, r2 = 34, 48 if i % 2 == 0 else 42
        p = QPainterPath()
        p.moveTo(50 + r1 * math.cos(math.radians(a)), 64 + r1 * math.sin(math.radians(a)))
        p.lineTo(50 + r2 * math.cos(math.radians(a)), 64 + r2 * math.sin(math.radians(a)))
        out.append((stroked(p, 5), "a"))
    out.append((rrect(6, 70, 88, 8, 4), "a"))
    out.append((rrect(22, 84, 56, 8, 4), "a"))
    return out


def m_mountain():
    big = polygon([(2, 90), (40, 18), (78, 90)], 3)
    small = polygon([(46, 90), (72, 44), (98, 90)], 3)
    snow = polygon([(40, 18), (50, 38), (40, 34), (31, 40)], 1)
    return [(big, "a"), (small.subtracted(big), "b"), (snow, "c")]


def m_infinity():
    p = QPainterPath()
    p.moveTo(50, 50)
    p.cubicTo(66, 20, 98, 24, 98, 50)
    p.cubicTo(98, 76, 66, 80, 50, 50)
    p.cubicTo(34, 20, 2, 24, 2, 50)
    p.cubicTo(2, 76, 34, 80, 50, 50)
    return [(stroked(p, 13), "a")]


def m_bolt():
    return [(polygon([(58, 2), (14, 56), (44, 56), (36, 98), (86, 40), (54, 40)], 4), "a")]


def m_heartbeat():
    p = QPainterPath()
    p.moveTo(2, 54)
    for x, y in ((26, 54), (36, 28), (48, 82), (58, 8), (68, 64), (76, 54), (98, 54)):
        p.lineTo(x, y)
    return [(stroked(p, 8), "a")]


def m_check():
    ring = circle(50, 50, 46).subtracted(circle(50, 50, 36))
    p = QPainterPath()
    p.moveTo(28, 52)
    p.lineTo(44, 68)
    p.lineTo(74, 34)
    return [(ring, "b"), (stroked(p, 11), "a")]


def m_burst():
    return [(_star(50, 50, 48, 30, 12, -90, 2), "a"), (circle(50, 50, 16), "b")]


def m_laurel():
    out = []
    leaf = QPainterPath()
    leaf.moveTo(0, 0)
    leaf.cubicTo(4, -8, 16, -8, 22, 0)
    leaf.cubicTo(16, 8, 4, 8, 0, 0)
    for side in (1, -1):
        for i in range(7):
            t = math.radians(18 + i * 22)            # angle around the wreath centre, from the bottom
            x = 50 - side * 34 * math.sin(t)
            y = 50 + 34 * math.cos(t)
            rot = math.degrees(t) * (-side) + (-90 if side == 1 else -90) + (0 if side == 1 else 0)
            tr = QTransform().translate(x, y).rotate(-90 + side * (90 - math.degrees(t)) * -1 + 0)
            tr = QTransform().translate(x, y).rotate(-side * math.degrees(t) - 90 + (180 if side == -1 else 0) * 0)
            out.append((tr.map(leaf), "a" if i % 2 == 0 else "b"))
    return out


def m_compass():
    ring = stroked(_arc(50, 50, 42, 0, 360), 6)
    n = polygon([(50, 12), (62, 50), (50, 44), (38, 50)], 1)
    s = polygon([(50, 88), (38, 50), (50, 56), (62, 50)], 1)
    return [(ring, "b"), (n, "a"), (s, "b"), (circle(50, 50, 5), "c")]


def m_gear():
    p = ngon(50, 50, 36, 8, -90, 0)
    teeth = QPainterPath()
    for i in range(8):
        teeth = teeth.united(_rot(rrect(41, 6, 18, 22, 4), 45 * i))
    body = circle(50, 50, 34).united(teeth)
    return [(body.subtracted(circle(50, 50, 14)), "a")]


def m_steps():
    return [(rrect(4, 68, 28, 28, 5), "b"), (rrect(36, 44, 28, 52, 5), "a"), (rrect(68, 16, 28, 80, 5), "a")]


def m_pixels():
    out = []
    cells = [(0, 1), (1, 0), (1, 1), (1, 2), (2, 1), (2, 2), (3, 0), (3, 3), (0, 3), (2, 0)]
    for i, (cx, cy) in enumerate(cells):
        out.append((rrect(8 + cx * 22, 8 + cy * 22, 18, 18, 4), "a" if i % 3 else "b"))
    return out


def m_sprout():
    stem = QPainterPath()
    stem.moveTo(50, 94)
    stem.cubicTo(50, 70, 50, 56, 50, 40)
    leaf = QPainterPath()
    leaf.moveTo(0, 0)
    leaf.cubicTo(8, -22, 34, -28, 40, -26)
    leaf.cubicTo(38, -2, 22, 10, 0, 0)
    l1 = QTransform().translate(50, 56).map(leaf)
    l2 = QTransform().translate(50, 44).scale(-1, 1).map(leaf)
    return [(stroked(stem, 7), "b"), (l1, "a"), (l2, "a")]


def m_waverings():
    out = []
    for i, r in enumerate((44, 32, 20, 8)):
        out.append((circle(50, 50, r).subtracted(circle(50, 50, r - 7)) if r > 8 else circle(50, 50, 8), "a" if i % 2 == 0 else "b"))
    return out


def m_origami():
    a = polygon([(6, 30), (50, 8), (50, 56)], 2)
    b = polygon([(50, 8), (94, 30), (50, 56)], 2)
    c = polygon([(6, 30), (50, 56), (30, 94)], 2)
    d = polygon([(94, 30), (50, 56), (70, 94)], 2)
    return [(a, "a"), (b, "b"), (c, "b"), (d, "a")]


def m_gems():
    out = []
    for i, (x, y, s) in enumerate(((50, 28, 24), (28, 66, 20), (72, 66, 20))):
        out.append((polygon([(x, y - s), (x + s, y), (x, y + s), (x - s, y)], 3), "a" if i == 0 else ("b" if i == 1 else "c")))
    return out


def m_keyhole():
    body = circle(50, 40, 34)
    slot = polygon([(40, 56), (60, 56), (66, 96), (34, 96)], 3)
    hole = circle(50, 36, 12).united(polygon([(44, 44), (56, 44), (60, 70), (40, 70)], 2))
    return [(body.united(slot).subtracted(hole), "a")]


def m_swoosh():
    p = QPainterPath()
    p.moveTo(4, 70)
    p.cubicTo(30, 80, 70, 70, 96, 20)
    p.cubicTo(76, 56, 38, 72, 4, 70)
    q = QPainterPath()
    q.moveTo(10, 50)
    q.cubicTo(34, 56, 62, 48, 82, 16)
    q.cubicTo(62, 38, 34, 46, 10, 50)
    return [(p, "a"), (q, "b")]


def m_lotus():
    out = []
    petal = QPainterPath()
    petal.moveTo(50, 90)
    petal.cubicTo(30, 70, 30, 36, 50, 10)
    petal.cubicTo(70, 36, 70, 70, 50, 90)
    for i, a in enumerate((-60, -30, 0, 30, 60)):
        tr = QTransform().translate(50, 90).rotate(a).translate(-50, -90)
        out.append((tr.map(petal), "a" if i % 2 == 0 else "b"))
    return out


def m_atom():
    out = []
    for a in (0, 60, 120):
        e = QPainterPath()
        e.addEllipse(QRectF(6, 32, 88, 36))
        out.append((stroked(_rot(e, a), 5), "a" if a == 0 else "b"))
    out.append((circle(50, 50, 9), "c"))
    return out


def m_crown():
    p = polygon([(8, 78), (8, 30), (30, 52), (50, 18), (70, 52), (92, 30), (92, 78)], 4)
    base = rrect(8, 82, 84, 12, 4)
    return [(p, "a"), (base, "b")]


def m_paw():
    out = [(circle(50, 66, 22), "a")]
    for x, y, r in ((22, 44, 10), (40, 28, 11), (60, 28, 11), (78, 44, 10)):
        out.append((circle(x, y, r), "b"))
    return out


def m_anchor():
    p = QPainterPath()
    p.moveTo(50, 30)
    p.lineTo(50, 90)
    q = QPainterPath()
    q.moveTo(24, 62)
    q.cubicTo(26, 90, 74, 90, 76, 62)
    r = QPainterPath()
    r.moveTo(36, 44)
    r.lineTo(64, 44)
    return [(stroked(p, 8), "a"), (stroked(q, 8), "a"), (stroked(r, 8), "a"), (stroked(_arc(50, 18, 11, 0, 360), 7), "b")]


def _line_p(x1, y1, x2, y2):
    p = QPainterPath()
    p.moveTo(x1, y1)
    p.lineTo(x2, y2)
    return p


def m_camera():
    body = rrect(6, 26, 88, 62, 12)
    top = rrect(32, 12, 36, 18, 5)
    lens = circle(50, 58, 20)
    return [(body.united(top).subtracted(lens), "a"), (circle(50, 58, 12), "b")]


def m_wifi():
    out = []
    for i, r in enumerate((14, 30, 46)):
        out.append((stroked(_arc(50, 80, r, 45, 90), 8), "a" if i != 0 else "b"))
    out.append((circle(50, 80, 7), "b"))
    return out


def m_book():
    l = polygon([(48, 20), (48, 88), (8, 80), (8, 14)], 4)
    r = polygon([(52, 20), (92, 14), (92, 80), (52, 88)], 4)
    return [(l, "a"), (r, "b")]


def m_chat():
    b = rrect(6, 10, 88, 60, 16).united(polygon([(24, 64), (24, 94), (52, 68)], 2))
    dots = [circle(30 + 20 * i, 40, 6) for i in range(3)]
    p = b
    for d in dots:
        p = p.subtracted(d)
    return [(p, "a")]


def m_home():
    roof = polygon([(4, 50), (50, 8), (96, 50), (84, 50), (84, 92), (16, 92), (16, 50)], 3)
    door = rrect(42, 60, 16, 32, 3)
    return [(roof.subtracted(door), "a"), (door, "b")]


def m_cup():
    cup = rrect(14, 30, 56, 56, 14)
    handle = stroked(_arc(70, 56, 14, -90, 180), 8)
    steam = [stroked(_line_p(28 + 14 * i, 8, 28 + 14 * i, 22), 6) for i in range(3)]
    return [(cup, "a"), (handle, "b")] + [(s, "b") for s in steam]


MARKS = {"hexcluster": m_hexcluster, "crescent": m_crescent, "sunrise": m_sunrise, "mountain": m_mountain, "infinity": m_infinity,
         "bolt": m_bolt, "heartbeat": m_heartbeat, "check": m_check, "burst": m_burst, "laurel": m_laurel, "compass": m_compass,
         "gear": m_gear, "steps": m_steps, "pixels": m_pixels, "sprout": m_sprout, "waverings": m_waverings, "origami": m_origami,
         "gems": m_gems, "keyhole": m_keyhole, "swoosh": m_swoosh, "lotus": m_lotus, "atom": m_atom, "crown": m_crown, "paw": m_paw,
         "anchor": m_anchor, "camera": m_camera, "wifi": m_wifi, "book": m_book, "chat": m_chat, "home": m_home, "cup": m_cup}
