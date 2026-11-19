"""Symbols that are made for each name, so no one else picks the same one from a list.

- monogram(text, font, style): the initials drawn in one of many styles
- abstract(name, style, variant): marks that grow from the letters of the name (the same name always makes the
  same mark, another name another one)
- line_art(parts, mode): any symbol as a one-line or two-line drawing

Every function returns [(QPainterPath, role)]: role 'a' = main color, 'b' = second color, 'c' = a darker main tone.
"""
import hashlib
import math
import random

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QPainterPath, QPainterPathStroker, QTransform

from . import textkit

MONO_STYLES = [
    ("plain", "Classic"), ("overlap", "Overlapping"), ("interlock", "Interlocked"), ("linked", "Linked"),
    ("stacked", "Stacked"), ("cutout", "Cut out of a circle"), ("shield", "In a shield"), ("outline", "Outline"),
    ("inline", "Inline"), ("stripe", "Stripe cut"), ("shadow", "Long shadow"), ("split", "Split in two"),
    ("diamond", "In a diamond"), ("ribbon", "Ribbon"),
]
ABSTRACT_STYLES = [
    ("radial", "Letter rosette"), ("pixel", "Pixel pattern"), ("rings", "Rings"), ("facets", "Facets"),
    ("burst", "Burst"), ("waves", "Waves"), ("orbit", "Orbits"), ("blocks", "Blocks"), ("petals", "Petals"),
    ("knot", "Knot"), ("steps", "Steps"), ("dots", "Dot field"),
]
LINE_MODES = [("none", "Solid"), ("line", "Line art"), ("double", "Double line")]


# ---------------------------------------------------------------------------------------------- helpers --
def _seed(*parts):
    h = hashlib.sha256("|".join(str(p) for p in parts).encode("utf-8")).hexdigest()
    return int(h[:16], 16)


def _fit(p, box=100.0, pad=0.0):
    """scale and move a path to fill a box x box square (keeping its proportions)"""
    r = p.boundingRect()
    if r.isEmpty():
        return p
    k = (box - 2 * pad) / max(r.width(), r.height())
    return QTransform().translate(box / 2, box / 2).scale(k, k).translate(-r.center().x(), -r.center().y()).map(p)


def _stroke(p, w, cap=Qt.RoundCap, join=Qt.RoundJoin):
    s = QPainterPathStroker()
    s.setWidth(w)
    s.setCapStyle(cap)
    s.setJoinStyle(join)
    return s.createStroke(p)


def _circle(cx, cy, r):
    p = QPainterPath()
    p.addEllipse(QPointF(cx, cy), r, r)
    return p


def _poly(pts):
    p = QPainterPath()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    p.closeSubpath()
    return p


def _letters(text, font_id):
    """each letter as its own path (bold), baseline at 0, at size 100"""
    fid = font_id if textkit.BY_ID.get(font_id, {}).get("cat") != "script" else "montserrat"
    out = []
    for ch in text:
        p, adv = textkit.run_path(ch, fid, True, 100)
        out.append((p, adv))
    return out


def _united(paths):
    u = QPainterPath()
    u.setFillRule(Qt.WindingFill)
    for p in paths:
        u = u.united(p)
    return u


# --------------------------------------------------------------------------------------------- monograms --
def monogram(text, font_id, style="plain"):
    text = (text or "?").strip()[:3] or "?"
    L = _letters(text, font_id)
    if style == "stacked" and len(L) > 1:
        out, y = [], 0.0
        for p, _ in L:
            r = p.boundingRect()
            out.append(QTransform().translate(-r.center().x(), y - r.top()).map(p))
            y += r.height() * 1.08
        return [(o, "a") for o in out]
    # side by side (tight), the base of most styles
    placed, x = [], 0.0
    gap = {"overlap": -0.28, "interlock": -0.22, "linked": -0.16}.get(style, 0.02)
    for p, adv in L:
        r = p.boundingRect()
        q = QTransform().translate(x - r.left(), 0).map(p)
        placed.append(q)
        x += r.width() + gap * r.height()
    word = _united(placed)
    box = word.boundingRect()
    h = max(box.height(), 1)
    if style == "plain":
        return [(word, "a")]
    if style == "overlap" and len(placed) > 1:
        out = [(placed[0], "a")]
        for q in placed[1:]:
            both = q.intersected(_united([o for o, _ in out]))
            out.append((q.subtracted(both), "b"))
            out.append((both, "c"))
        return out
    if style == "interlock" and len(placed) > 1:          # where the letters cross, the shape is cut away (XOR)
        acc = placed[0]
        for q in placed[1:]:
            acc = acc.united(q).subtracted(acc.intersected(q))
        return [(acc, "a")]
    if style == "linked" and len(placed) > 1:             # every second letter in the second color, with a gap
        out = []
        for i, q in enumerate(placed):
            if i:
                gap_cut = _stroke(placed[i - 1], h * 0.09)
                q = q.subtracted(gap_cut)
            out.append((q, "a" if i % 2 == 0 else "b"))
        return out
    if style == "cutout":
        r = max(box.width(), box.height()) * 0.78
        disc = _circle(box.center().x(), box.center().y(), r)
        return [(disc.subtracted(word), "a")]
    if style == "shield":
        cx, w = box.center().x(), max(box.width(), box.height()) * 1.55
        top, bot = box.center().y() - w * 0.55, box.center().y() + w * 0.62
        sh = QPainterPath()
        sh.moveTo(cx - w / 2, top)
        sh.lineTo(cx + w / 2, top)
        sh.lineTo(cx + w / 2, top + w * 0.55)
        sh.cubicTo(cx + w / 2, bot - w * 0.2, cx + w * 0.2, bot - w * 0.05, cx, bot)
        sh.cubicTo(cx - w * 0.2, bot - w * 0.05, cx - w / 2, bot - w * 0.2, cx - w / 2, top + w * 0.55)
        sh.closeSubpath()
        return [(sh.subtracted(word), "a")]
    if style == "outline":
        return [(_stroke(word, h * 0.07, Qt.FlatCap, Qt.MiterJoin), "a")]
    if style == "inline":                                 # a thin line inside each letter
        inner = _stroke(word, h * 0.16, Qt.FlatCap, Qt.MiterJoin)
        core = word.subtracted(inner)
        line = _stroke(core, h * 0.025)
        return [(word.subtracted(line.intersected(word)), "a")]
    if style == "stripe":
        band = QPainterPath()
        band.addRect(QRectF(box.left() - 5, box.center().y() - h * 0.045, box.width() + 10, h * 0.09))
        return [(word.subtracted(band), "a")]
    if style == "shadow":
        sh = QPainterPath()
        sh.setFillRule(Qt.WindingFill)
        steps = 24
        for i in range(1, steps + 1):
            sh.addPath(QTransform().translate(i * h * 0.012, i * h * 0.012).map(word))
        return [(sh.simplified().subtracted(word), "b"), (word, "a")]
    if style == "split":
        half = QPainterPath()
        half.addRect(QRectF(box.left() - 5, box.top() - 5, box.width() + 10, box.height() / 2 + 5))
        top, bottom = word.intersected(half), word.subtracted(half)
        return [(top, "a"), (QTransform().translate(h * 0.04, h * 0.04).map(bottom), "b")]
    if style == "diamond":
        c, s = box.center(), max(box.width(), box.height()) * 0.98
        d = _poly([(c.x(), c.y() - s), (c.x() + s, c.y()), (c.x(), c.y() + s), (c.x() - s, c.y())])
        ring = d.subtracted(_poly([(c.x(), c.y() - s * 0.86), (c.x() + s * 0.86, c.y()), (c.x(), c.y() + s * 0.86), (c.x() - s * 0.86, c.y())]))
        return [(ring, "b"), (word, "a")]
    if style == "ribbon":
        r = max(box.width(), box.height()) * 0.82
        cx, cy = box.center().x(), box.center().y()
        disc = _circle(cx, cy, r)
        band = QPainterPath()
        band.addRect(QRectF(cx - r * 1.35, cy + r * 0.48, r * 2.7, r * 0.42))
        return [(disc.subtracted(word).subtracted(band), "a"), (band.subtracted(_stroke(disc, r * 0.06)), "b")]
    return [(word, "a")]


# ------------------------------------------------------------------------------------------ abstract marks --
def abstract(name, style="radial", variant=0, font_id="montserrat"):
    rng = random.Random(_seed(name.strip().lower(), style, variant))
    first = (name.strip() or "D")[0]
    if style == "radial":                                 # the first letter turned around the centre
        p, _ = textkit.run_path(first.upper(), font_id if textkit.BY_ID.get(font_id, {}).get("cat") != "script" else "montserrat", True, 100)
        p = _fit(p, 44)
        n = rng.choice([3, 4, 5, 6, 8])
        out = QPainterPath()
        out.setFillRule(Qt.WindingFill)
        for i in range(n):
            out.addPath(QTransform().translate(50, 50).rotate(360 * i / n).translate(-22, -48).map(p))
        return [(out, "a")]
    if style == "pixel":                                  # a mirrored 5 x 5 or 7 x 7 pattern, like a fingerprint
        n = rng.choice([5, 7])
        cell = 100 / n
        rad = rng.choice([0, cell * 0.22, cell * 0.5])
        a, b = QPainterPath(), QPainterPath()
        for y in range(n):
            for x in range((n + 1) // 2):
                if rng.random() < 0.52:
                    for xx in {x, n - 1 - x}:
                        tgt = a if rng.random() < 0.82 else b
                        tgt.addRoundedRect(QRectF(xx * cell + cell * 0.06, y * cell + cell * 0.06, cell * 0.88, cell * 0.88), rad, rad)
        return [(a, "a"), (b, "b")]
    if style == "rings":                                  # broken rings, each gap where a letter says
        out = QPainterPath()
        out.setFillRule(Qt.WindingFill)
        k = rng.randint(3, 5)
        for i in range(k):
            r = 46 - i * (38 / k)
            start = rng.uniform(0, 360)
            span = rng.uniform(200, 320)
            arc = QPainterPath()
            arc.arcMoveTo(QRectF(50 - r, 50 - r, 2 * r, 2 * r), start)
            arc.arcTo(QRectF(50 - r, 50 - r, 2 * r, 2 * r), start, span)
            out.addPath(_stroke(arc, 38 / k * 0.55))
        return [(out, "a")]
    if style == "facets":                                 # a polygon cut into triangles, two tones
        n = rng.choice([5, 6, 8])
        pts = [(50 + 48 * math.cos(math.radians(-90 + 360 * i / n)), 50 + 48 * math.sin(math.radians(-90 + 360 * i / n))) for i in range(n)]
        c = (50 + rng.uniform(-10, 10), 50 + rng.uniform(-10, 10))
        out = []
        for i in range(n):
            tri = _poly([c, pts[i], pts[(i + 1) % n]])
            out.append((tri.subtracted(_stroke(tri, 2.4)), "a" if i % 2 == 0 else ("b" if rng.random() < 0.5 else "c")))
        return out
    if style == "burst":
        n = rng.choice([8, 10, 12, 16])
        out = QPainterPath()
        out.setFillRule(Qt.WindingFill)
        for i in range(n):
            ang = math.radians(360 * i / n)
            ln = 30 + 18 * rng.random()
            seg = QPainterPath()
            seg.moveTo(50 + 12 * math.cos(ang), 50 + 12 * math.sin(ang))
            seg.lineTo(50 + ln * math.cos(ang), 50 + ln * math.sin(ang))
            out.addPath(_stroke(seg, 7))
        out.addPath(_circle(50, 50, 7))
        return [(out, "a")]
    if style == "waves":
        out = []
        k = rng.randint(3, 4)
        amp = rng.uniform(6, 10)
        for i in range(k):
            y = 25 + i * (50 / (k - 1))
            w = QPainterPath()
            w.moveTo(6, y)
            for s in range(1, 41):
                x = 6 + s * 2.2
                w.lineTo(x, y + amp * math.sin(s / 40 * math.pi * 2 + i * 0.8))
            out.append((_stroke(w, 8), "a" if i % 2 == 0 else "b"))
        disc = _circle(50, 50, 48)
        return [(p.intersected(disc), r) for p, r in out]
    if style == "orbit":
        out = QPainterPath()
        out.setFillRule(Qt.WindingFill)
        k = rng.randint(2, 3)
        for i in range(k):
            e = QPainterPath()
            e.addEllipse(QRectF(4, 34, 92, 32))
            e = QTransform().translate(50, 50).rotate(180 * i / k + rng.uniform(-8, 8)).translate(-50, -50).map(e)
            out.addPath(_stroke(e, 5))
        return [(out, "a"), (_circle(50, 50, 11), "b")]
    if style == "blocks":                                 # bars whose heights come from the letters
        letters = [c for c in name.lower() if c.isalpha()][:6] or ["d"]
        n = len(letters)
        out = []
        bw = 92 / n
        for i, c in enumerate(letters):
            hgt = 30 + (ord(c) - 97) / 25 * 66
            out.append((QPainterPath(), "a"))
            out[-1][0].addRoundedRect(QRectF(4 + i * bw + bw * 0.1, 96 - hgt, bw * 0.8, hgt), bw * 0.2, bw * 0.2)
            if i % 3 == 2:
                out[-1] = (out[-1][0], "b")
        return out
    if style == "petals":
        n = rng.choice([4, 5, 6, 8])
        out = []
        for i in range(n):
            leaf = QPainterPath()
            leaf.moveTo(50, 50)
            leaf.cubicTo(30, 30, 40, 4, 50, 2)
            leaf.cubicTo(60, 4, 70, 30, 50, 50)
            out.append((QTransform().translate(50, 50).rotate(360 * i / n).translate(-50, -50).map(leaf), "a" if i % 2 == 0 else "b"))
        return out
    if style == "knot":                                   # an endless loop
        n = rng.choice([3, 4, 5])
        p = QPainterPath()
        for s in range(0, 361, 3):
            t = math.radians(s)
            r = 30 + 14 * math.cos(n * t)
            pt = (50 + r * math.cos(t), 50 + r * math.sin(t))
            p.moveTo(*pt) if s == 0 else p.lineTo(*pt)
        return [(_stroke(p, 7), "a")]
    if style == "steps":
        k = rng.randint(3, 5)
        out = QPainterPath()
        sz = 92 / k
        for i in range(k):
            out.addRoundedRect(QRectF(4 + i * sz, 96 - (i + 1) * sz, sz * (k - i), sz * 0.86), sz * 0.18, sz * 0.18)
        return [(out, "a")]
    if style == "dots":
        out, out2 = QPainterPath(), QPainterPath()
        n = 7
        for y in range(n):
            for x in range(n):
                cx, cy = 7 + x * 86 / (n - 1), 7 + y * 86 / (n - 1)
                d = math.hypot(cx - 50, cy - 50)
                if d > 47:
                    continue
                r = 5.6 * (1 - d / 60) * (0.6 + 0.4 * rng.random())
                (out if rng.random() < 0.85 else out2).addEllipse(QPointF(cx, cy), r, r)
        return [(out, "a"), (out2, "b")]
    return abstract(name, "radial", variant, font_id)


# --------------------------------------------------------------------------------------------- line art --
def line_art(parts, mode="line"):
    """any symbol as a drawing: the outline of each shape as a line (one or two lines)"""
    if mode not in ("line", "double"):
        return parts
    u = QPainterPath()
    for p, _ in parts:
        u.addPath(p)
    r = u.boundingRect()
    s = max(r.width(), r.height(), 1)
    out = []
    for p, role in parts:
        q = QPainterPath(p)
        q.setFillRule(Qt.WindingFill)
        q = q.simplified()
        if mode == "line":
            out.append((_stroke(q, s * 0.035), role))
        else:
            outer = _stroke(q, s * 0.03)
            inner_line = _stroke(_stroke(q, s * 0.11, Qt.FlatCap, Qt.MiterJoin).intersected(q), s * 0.022)
            out.append((outer.united(inner_line.intersected(q)), role))
    return out
