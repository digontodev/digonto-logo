"""Spec (a plain dict) -> Scene. Layouts: horizontal, stacked, twoline, wordmark, emblem, stamp, symbol."""
import copy
import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QPainterPath, QTransform

from . import custom, generate, icons, marks, namefx, palettes, textkit
from .scene import Grad, Scene

LAYOUTS = [("horizontal", "Symbol left"), ("stacked", "Symbol on top"), ("twoline", "Two lines"), ("wordmark", "Wordmark"),
           ("emblem", "Round emblem"), ("stamp", "Stamp"), ("badge", "Name badge"), ("frame", "Framed"), ("symbol", "Symbol only")]
CMODES = [("solid", "Solid, symbol cut out"), ("duo", "Solid, 2 colors"), ("outline", "Outline"), ("soft", "Soft tint")]
TWO = [("none", "One color"), ("first", "First word accent"), ("last", "Last word accent"), ("weight", "First word bold"),
       ("weight_last", "Last word bold"), ("light", "First bold, rest light"), ("alt", "Light / bold, word by word"), ("accent_bold", "First word bold + accent")]

DEFAULT = {
    "name": "Your Brand", "tagline": "",
    "layout": "horizontal",
    "symbol": {"kind": "icon", "icon": "star", "iw": "fill", "mark": "orbit", "letters": "", "container": "none", "cmode": "solid",
               "scale": 1.0, "grad": False, "mstyle": "plain", "astyle": "radial", "avar": 0, "line": "none"},
    "swap": {"on": False, "letter": "", "icon": "", "iw": "fill"},
    "font": {"id": "montserrat", "bold": True, "case": "upper", "track": 0.04, "two": "none", "size": 1.0,
             "slant": 0.0, "stretch": 1.0, "bend": 0.0, "nstyle": "solid", "cut": "none", "shadow": "none", "ngrad": False},
    "tfont": {"id": "montserrat", "bold": False, "case": "upper", "track": 0.2, "scale": 1.0, "fit": True},
    "colors": {"primary": "#C2395C", "secondary": "#E0662A", "text": "#0F3D2E", "bg": "#F4FAF7"},
    "name_role": "text", "tag_role": "muted", "gap": 1.0, "divider": False, "deco": "none", "fill": True,
}
F = 100.0


def merged(spec):
    s = copy.deepcopy(DEFAULT)
    for k, v in (spec or {}).items():
        if isinstance(v, dict) and isinstance(s.get(k), dict):
            s[k].update(v)
        else:
            s[k] = v
    return s


def color(s, role):
    c = s["colors"]
    if role == "muted":
        return palettes.mix(c["text"], c["bg"], 0.3)
    if role == "light":
        return "#FFFFFF" if palettes.luminance(c["primary"]) < 0.45 else c["text"]
    return c.get(role, c["text"])


def initials(name):
    w = [x for x in name.replace("-", " ").split() if x[:1].isalnum()]
    if not w:
        return "?"
    return (w[0][0] + w[1][0]).upper() if len(w) > 1 else w[0][0].upper()


# ------------------------------------------------------------------ symbol
def fit(path, size, cx, cy):
    r = path.boundingRect()
    if r.isEmpty():
        return path
    k = size / max(r.width(), r.height())
    tr = QTransform().translate(cx, cy).scale(k, k).translate(-r.center().x(), -r.center().y())
    return tr.map(path)


def glyph_parts(s):
    """the symbol's drawing without container: [(path, role)] in its own coordinates"""
    parts = _raw_parts(s)
    line = s["symbol"].get("line", "none")
    return generate.line_art(parts, line) if parts and line != "none" else parts


def _raw_parts(s):
    sy = s["symbol"]
    kind = sy["kind"]
    if kind == "icon":
        return [(icons.path(sy["icon"], sy["iw"]), "a")]
    if kind == "mark":
        return marks.MARKS.get(sy["mark"], marks.m_orbit)()
    if kind == "custom":
        out = []
        for p, c in custom.paths(sy.get("custom")):
            p.setFillRule(Qt.WindingFill)
            out.append((p, c if (sy.get("keep") and c) else "a"))
        return out
    if kind == "monogram":
        t = (sy.get("letters") or initials(s["name"])).strip() or "?"
        return generate.monogram(t, s["font"]["id"], sy.get("mstyle", "plain"))
    if kind == "abstract":
        return generate.abstract(s["name"], sy.get("astyle", "radial"), int(sy.get("avar", 0)), s["font"]["id"])
    return []


def symbol(s, S):
    """(items, w, h): items = [(path, paint)] inside a w x h box with top-left at 0,0"""
    sy = s["symbol"]
    if sy["kind"] == "none":
        return [], 0.0, 0.0
    S = S * sy.get("scale", 1.0)
    prim = Grad(color(s, "primary"), color(s, "secondary"), 45) if sy.get("grad") else color(s, "primary")
    sec = color(s, "secondary")
    parts = glyph_parts(s)
    union = QPainterPath()
    for p, _ in parts:
        union.addPath(p)
    box = union.boundingRect()
    cont = sy.get("container", "none")
    paint_of = lambda role: role if role.startswith("#") else {"a": prim, "b": sec, "c": palettes.shade(color(s, "primary"), -0.35)}.get(role, prim)
    items = []
    if cont == "none":
        if box.isEmpty():
            return [], 0.0, 0.0
        k = S / max(box.width(), box.height())
        tr = QTransform().scale(k, k).translate(-box.x(), -box.y())
        w, h = box.width() * k, box.height() * k
        if sy.get("split"):
            half = _half(w, h)
            for p, role in parts:
                q = tr.map(p)
                a, b = q.intersected(half), q.subtracted(half)
                items.append((a, paint_of(role)))
                items.append((b, sec if not role.startswith("#") else paint_of(role)))
            return items, w, h
        for p, role in parts:
            items.append((tr.map(p), paint_of(role)))
        return items, w, h
    cp = marks.container(cont)
    cp = QTransform().scale(S / 100, S / 100).map(cp)
    mode = sy.get("cmode", "solid")
    gsize = S * (0.54 if cont not in ("ring",) else 0.5)
    k = gsize / max(box.width(), box.height()) if not box.isEmpty() else 1
    tr = QTransform().translate(S / 2, S / 2 + (S * 0.015 if cont == "shield" else 0)).scale(k, k).translate(-box.center().x(), -box.center().y())
    placed = [(tr.map(p), role) for p, role in parts]
    multi = sy["kind"] in ("mark", "abstract") or (sy["kind"] == "monogram" and any(r != "a" for _, r in parts)) or (sy["kind"] == "custom" and bool(sy.get("keep")) and any(r.startswith("#") for _, r in parts))
    if cont == "ring":
        items.append((cp, prim))
        items += [(p, paint_of(role)) for p, role in placed]
    elif mode == "outline":
        ring = marks.stroked(_inset(cp, S * 0.035), S * 0.07, Qt.FlatCap, Qt.MiterJoin) if False else _outline(cp, S * 0.07)
        items.append((ring, prim))
        items += [(p, paint_of(role)) for p, role in placed]
    elif mode == "soft":
        items.append((cp, palettes.mix(color(s, "primary"), "#FFFFFF", 0.86)))
        items += [(p, paint_of(role)) for p, role in placed]
    elif mode == "duo" or multi:
        items.append((cp, prim))
        for p, role in placed:
            items.append((p, role if role.startswith("#") else sec if (role == "a" and not multi) else {"a": color(s, "light"), "b": sec, "c": palettes.shade(color(s, "light"), -0.2)}[role]))
    else:                                       # solid with the symbol cut out
        cut = QPainterPath()
        for p, _ in placed:
            cut.addPath(p)
        cut.setFillRule(Qt.WindingFill)
        base = QPainterPath(cp)
        base.setFillRule(Qt.WindingFill)
        out = base.subtracted(cut.simplified())
        items.append((out, prim))
    return items, S, S


def _half(w, h):
    """a big diagonal half-plane over the left side of a w x h box (for two-color symbols)"""
    r = QPainterPath()
    big = max(w, h) * 3
    r.addRect(QRectF(w / 2 - big, h / 2 - big, big, big * 2))
    return QTransform().translate(w / 2, h / 2).rotate(28).translate(-w / 2, -h / 2).map(r)


def _outline(path, w):
    """ring of width w just inside the shape"""
    s = marks.stroked(path, w * 2, Qt.FlatCap, Qt.MiterJoin)
    return path.intersected(s)


def _inset(p, d):
    return p


# ------------------------------------------------------------------ text
def name_text(s):
    f = s["font"]
    t = textkit.apply_case(s["name"].strip(), f["case"])
    return t or " "


def name_runs(s, text=None):
    f = s["font"]
    text = text if text is not None else name_text(s)
    base_role = s["name_role"]
    two = f.get("two", "none")
    words = text.split(" ")
    if two == "none" or len(words) < 2:
        return [(text, f["id"], f["bold"], base_role)]
    runs = []
    for i, w in enumerate(words):
        sp = " " if i < len(words) - 1 else ""
        if two == "first":
            runs.append((w + sp, f["id"], f["bold"], "primary" if i == 0 else base_role))
        elif two == "last":
            runs.append((w + sp, f["id"], f["bold"], "primary" if i == len(words) - 1 else base_role))
        elif two == "weight":
            runs.append((w + sp, f["id"], i == 0, base_role))
        elif two == "weight_last":
            runs.append((w + sp, f["id"], i == len(words) - 1, base_role))
        elif two == "light":
            runs.append((w + sp, f["id"], True if i == 0 else 300, base_role))
        elif two == "alt":
            runs.append((w + sp, f["id"], 300 if i % 2 == 0 else True, base_role))
        elif two == "accent_bold":
            runs.append((w + sp, f["id"], i == 0, "primary" if i == 0 else base_role))
        else:
            runs.append((w + sp, f["id"], f["bold"], base_role))
    return runs


def _swap_target(text, letter):
    """index of the letter to swap: the chosen one, else the first o / a / e / any letter"""
    low = text.lower()
    for c in ([letter.lower()] if letter.strip() else []) + ["o", "a", "e"]:
        if c and c in low:
            return low.index(c)
    for i, c in enumerate(text):
        if c.isalnum():
            return i
    return -1


def _split_runs(runs, at):
    """split the runs so the character at position `at` is a run of its own; returns (runs, index of that run)"""
    out, pos, target = [], 0, -1
    for text, fid, bold, role in runs:
        if pos <= at < pos + len(text):
            j = at - pos
            for piece, mine in ((text[:j], False), (text[j], True), (text[j + 1:], False)):
                if piece:
                    if mine:
                        target = len(out)
                    out.append((piece, fid, bold, role))
        elif text:
            out.append((text, fid, bold, role))
        pos += len(text)
    return out, target


def swap_icon(s):
    sw = s.get("swap") or {}
    if sw.get("icon"):
        return sw["icon"], sw.get("iw", "fill")
    sy = s["symbol"]
    return (sy["icon"], sy["iw"]) if sy["kind"] == "icon" else ("star", "fill")


def build_name(s, size):
    spec = name_runs(s)
    sw = s.get("swap") or {}
    target = -1
    if sw.get("on"):
        at = _swap_target("".join(r[0] for r in spec), sw.get("letter", ""))
        if at >= 0:
            spec, target = _split_runs(spec, at)
    runs, ink = textkit.text_runs(spec, size, s["font"]["track"])
    if 0 <= target < len(runs):
        p, role = runs[target]
        r = p.boundingRect()
        if not r.isEmpty():
            name, w = swap_icon(s)
            ic = icons.path(name, w)
            if s["symbol"].get("line", "none") != "none":
                ic = generate.line_art([(ic, "a")], s["symbol"]["line"])[0][0]
            side = max(r.height(), r.width()) * 1.02
            ic = fit(ic, side, r.center().x(), r.center().y())
            runs[target] = (ic, "primary" if role == s["name_role"] else role)
            ink = QRectF()
            for q, _ in runs:
                ink = ink.united(q.boundingRect()) if not ink.isEmpty() else q.boundingRect()
    return namefx.apply(s, [(p, color(s, role)) for p, role in runs], size)


def build_tag(s, size, width=None):
    t = s["tfont"]
    text = textkit.apply_case(s["tagline"].strip(), t["case"])
    if not text:
        return [], QRectF()
    track = t["track"]
    if width and t.get("fit") and t["case"] == "upper" and len(text) > 1:
        w0 = textkit.text_width(text, t["id"], t["bold"], size, 0)
        track = max(0.0, min(0.7, (width - w0) / ((len(text) - 1) * size)))
    runs, ink = textkit.text_runs([(text, t["id"], t["bold"], s["tag_role"])], size, track)
    return [(p, color(s, role)) for p, role in runs], ink


def shifted(items, dx, dy):
    tr = QTransform().translate(dx, dy)
    return [(tr.map(p), c) for p, c in items]


def add(scene, items):
    for p, c in items:
        scene.add(p, fill=c)


def line(x1, y1, x2, y2, w, paint, cap=Qt.FlatCap):
    p = QPainterPath()
    p.moveTo(x1, y1)
    p.lineTo(x2, y2)
    return marks.stroked(p, w, cap, Qt.MiterJoin), paint


# ------------------------------------------------------------------ layouts
def build(spec):
    s = merged(spec)
    lay = s["layout"]
    if lay == "symbol" or (s["symbol"]["kind"] == "none" and lay in ("horizontal", "stacked")):
        lay = "wordmark" if s["symbol"]["kind"] == "none" else "symbol"
    sc = Scene()
    if lay == "symbol":
        items, w, h = symbol(s, F * 2.0)
        add(sc, items)
    elif lay == "stacked":
        _stacked(s, sc)
    elif lay == "twoline":
        _twoline(s, sc)
    elif lay == "wordmark":
        _wordmark(s, sc)
    elif lay == "emblem":
        _emblem(s, sc)
    elif lay == "stamp":
        _stamp(s, sc)
    elif lay == "badge":
        _badge(s, sc)
    elif lay == "frame":
        _frame(s, sc)
    else:
        _horizontal(s, sc)
    return sc


def _cap(s, size):
    return textkit.metrics(s["font"]["id"], s["font"]["bold"])["cap"] * size


def _tcap(s, size):
    return textkit.metrics(s["tfont"]["id"], s["tfont"]["bold"])["cap"] * size


def _desc(ink, size):
    """how far the name reaches below its baseline (g, p, y ...), so the tagline never touches it"""
    return max(0.0, ink.bottom()) * 0.85


def _horizontal(s, sc):
    size = F * s["font"].get("size", 1.0)
    items, sw, sh = symbol(s, F * 1.5)
    nitems, nink = build_name(s, size)
    cap = _cap(s, size)
    has_tag = bool(s["tagline"].strip())
    tsize = size * 0.3 * s["tfont"].get("scale", 1.0)
    titems, tink = build_tag(s, tsize, nink.width())
    tcap = _tcap(s, tsize)
    gt = size * 0.26 + _desc(nink, size)
    block = cap + ((gt + tcap) if has_tag else 0)
    g = F * 0.42 * s["gap"]
    xt = sw + g
    H = max(sh, block)
    yc = H / 2
    add(sc, shifted(items, 0, yc - sh / 2))
    if s["divider"] and items:
        sc.add(*[x for x in _fill_line(xt - g / 2, yc - block * 0.7, xt - g / 2, yc + block * 0.7, size * 0.025, color(s, "muted"))]) if False else add(sc, [line(xt - g / 2, yc - block * 0.75, xt - g / 2, yc + block * 0.75, size * 0.03, color(s, "muted"))])
    ytop = yc - block / 2
    add(sc, shifted(nitems, xt - nink.left(), ytop + cap))
    if has_tag:
        add(sc, shifted(titems, xt - tink.left(), ytop + cap + gt + tcap))


def _fill_line(*a):
    return []


def _stacked(s, sc):
    size = F * s["font"].get("size", 1.0)
    items, sw, sh = symbol(s, F * 1.8)
    nitems, nink = build_name(s, size)
    cap = _cap(s, size)
    has_tag = bool(s["tagline"].strip())
    tsize = size * 0.3 * s["tfont"].get("scale", 1.0)
    titems, tink = build_tag(s, tsize, nink.width())
    tcap = _tcap(s, tsize)
    W = max(sw, nink.width(), tink.width() if has_tag else 0)
    g = F * 0.45 * s["gap"]
    add(sc, shifted(items, (W - sw) / 2, 0))
    y = sh + g + cap
    add(sc, shifted(nitems, (W - nink.width()) / 2 - nink.left(), y))
    if has_tag:
        y += size * 0.26 + _desc(nink, size) + tcap
        add(sc, shifted(titems, (W - tink.width()) / 2 - tink.left(), y))


def _twoline(s, sc):
    text = name_text(s)
    words = text.split(" ")
    if len(words) < 2:
        return _horizontal(s, sc)
    best, bi = None, 1
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        d = abs(len(a) - len(b))
        if best is None or d < best:
            best, bi = d, i
    l1, l2 = " ".join(words[:bi]), " ".join(words[bi:])
    size = F * 0.85 * s["font"].get("size", 1.0)
    f = s["font"]
    cap = _cap(s, size)
    r1, i1 = textkit.text_runs(name_runs(s, l1), size, f["track"])
    r2, i2 = textkit.text_runs(name_runs(s, l2), size, f["track"])
    if f.get("two") in ("first", "last"):
        # accent applies per line here: first line / last line
        role1 = "primary" if f["two"] == "first" else s["name_role"]
        role2 = "primary" if f["two"] == "last" else s["name_role"]
        r1 = [(p, role1) for p, _ in r1]
        r2 = [(p, role2) for p, _ in r2]
    n1, i1 = namefx.apply(s, [(p, color(s, r)) for p, r in r1], size)
    n2, i2 = namefx.apply(s, [(p, color(s, r)) for p, r in r2], size)
    items, sw, sh = symbol(s, F * 1.3)
    lead = cap * 1.42
    has_tag = bool(s["tagline"].strip())
    tsize = size * 0.34 * s["tfont"].get("scale", 1.0)
    titems, tink = build_tag(s, tsize, max(i1.width(), i2.width()))
    tcap = _tcap(s, tsize)
    gt = size * 0.3 + _desc(i2, size)
    block = cap + lead + ((gt + tcap) if has_tag else 0)
    g = F * 0.42 * s["gap"]
    H = max(sh, block)
    yc = H / 2
    add(sc, shifted(items, 0, yc - sh / 2))
    xt = sw + g
    ytop = yc - block / 2
    add(sc, shifted(n1, xt - i1.left(), ytop + cap))
    add(sc, shifted(n2, xt - i2.left(), ytop + cap + lead))
    if has_tag:
        add(sc, shifted(titems, xt - tink.left(), ytop + cap + lead + gt + tcap))


def _wordmark(s, sc):
    size = F * 1.1 * s["font"].get("size", 1.0)
    nitems, nink = build_name(s, size)
    cap = _cap(s, size)
    has_tag = bool(s["tagline"].strip())
    tsize = size * 0.28 * s["tfont"].get("scale", 1.0)
    titems, tink = build_tag(s, tsize, nink.width())
    tcap = _tcap(s, tsize)
    W = max(nink.width(), tink.width() if has_tag else 0)
    add(sc, shifted(nitems, (W - nink.width()) / 2 - nink.left(), cap))
    y = cap
    deco = s.get("deco", "none")
    if deco == "bar":
        y += size * 0.3
        bw = max(W * 0.18, size * 0.6)
        add(sc, [line(W / 2 - bw / 2, y, W / 2 + bw / 2, y, size * 0.075, color(s, "primary"))])
        y += size * 0.09
    elif deco == "underline":
        y += size * 0.28
        add(sc, [line(0, y, W, y, size * 0.05, color(s, "primary"))])
        y += size * 0.03
    if has_tag:
        y += size * 0.26 + (_desc(nink, size) if deco in ("none", "lines") else 0) + tcap
        if deco == "lines":
            tw = tink.width()
            ly = y - tcap / 2
            gap = size * 0.2
            add(sc, [line(0, ly, (W - tw) / 2 - gap, ly, size * 0.03, color(s, "muted")),
                     line((W + tw) / 2 + gap, ly, W, ly, size * 0.03, color(s, "muted"))])
        add(sc, shifted(titems, (W - tink.width()) / 2 - tink.left(), y))


def _ring(r, w):
    a, b = QPainterPath(), QPainterPath()
    a.addEllipse(QPointF(0, 0), r + w / 2, r + w / 2)
    b.addEllipse(QPointF(0, 0), r - w / 2, r - w / 2)
    return a.subtracted(b)


def _emblem(s, sc):
    R = F * 2.4
    prim = color(s, "primary")
    f, t = s["font"], s["tfont"]
    fill = s.get("fill", True)
    name = name_text(s)
    capr = textkit.metrics(f["id"], f["bold"])["cap"]
    rc = R * 0.76
    size = F * 0.46 * f.get("size", 1.0)
    # shrink the name until it spans at most about 200 degrees
    for _ in range(30):
        w = textkit.text_width(name, f["id"], f["bold"], size, f["track"])
        if w / (rc + size * capr / 2) <= math.radians(210):
            break
        size *= 0.93
    rt = rc - size * capr / 2
    top = textkit.arc_text(name, f["id"], f["bold"], size, rt, -90, f["track"])
    tag = textkit.apply_case(s["tagline"].strip(), t["case"])
    tsize = size * 0.62 * t.get("scale", 1.0)
    bottom = QPainterPath()
    if tag:
        tcap = textkit.metrics(t["id"], t["bold"])["cap"] * tsize
        rb = rc + tcap / 2
        for _ in range(20):
            if textkit.text_width(tag, t["id"], t["bold"], tsize, t["track"]) / rb <= math.radians(170):
                break
            tsize *= 0.93
        bottom = textkit.arc_text(tag, t["id"], t["bold"], tsize, rb, 90, t["track"], bottom=True)
    else:
        for a in (-1, 1):
            d = QPainterPath()
            d.addEllipse(QPointF(rc * math.sin(math.radians(a * 14)), rc * math.cos(math.radians(a * 14))), size * 0.07, size * 0.07)
            bottom.addPath(d)
    ri = R * 0.56
    sy = dict(s["symbol"])
    sy["container"] = "none" if sy.get("container") in (None, "none") else sy["container"]
    s2 = dict(s)
    s2["symbol"] = sy
    items, sw, sh = symbol(s2, ri * 1.18)
    items = shifted(items, -sw / 2, -sh / 2)
    if fill:
        disc = QPainterPath()
        disc.addEllipse(QPointF(0, 0), R, R)
        out = disc.subtracted(top).subtracted(bottom).subtracted(_ring(ri, R * 0.018))
        for p, c in items:
            out = out.subtracted(p)
        sc.add(out, fill=prim)
    else:
        sc.add(_ring(R, R * 0.045), fill=prim)
        sc.add(_ring(ri, R * 0.018), fill=prim)
        sc.add(top, fill=color(s, "primary") if s["name_role"] == "primary" else color(s, "text"))
        sc.add(bottom, fill=color(s, "secondary") if s["tag_role"] == "secondary" else color(s, "muted"))
        add(sc, items)


def _stamp(s, sc):
    inner = Scene()
    _stacked(s, inner)
    b = inner.bounds()
    pad = F * 0.55
    sc.items += inner.mapped(QTransform().translate(pad - b.x(), pad - b.y())).items
    w, h = b.width() + 2 * pad, b.height() + 2 * pad
    prim = color(s, "primary")
    r = F * 0.28
    outer = marks.rrect(0, 0, w, h, r)
    k = F * 0.05
    sc.add(_outline(outer, k), fill=prim)
    gap = F * 0.1
    inn = marks.rrect(k + gap, k + gap, w - 2 * (k + gap), h - 2 * (k + gap), max(2, r - k - gap))
    sc.add(_outline(inn, k * 0.4), fill=prim)


def _badge(s, sc):
    """the name knocked out of a solid pill (or label), the symbol beside it, the tagline underneath"""
    size = F * 0.95 * s["font"].get("size", 1.0)
    runs, nink = textkit.text_runs([(name_text(s), s["font"]["id"], s["font"]["bold"], "text")], size, s["font"]["track"])
    cap = _cap(s, size)
    px, py = size * 0.62, size * 0.42
    W, H = nink.width() + 2 * px, cap + 2 * py
    prim = Grad(color(s, "primary"), color(s, "secondary"), 20) if s["symbol"].get("grad") else color(s, "primary")
    pill = QPainterPath()
    pill.addRoundedRect(QRectF(0, 0, W, H), H * (0.5 if s.get("fill", True) else 0.16), H * (0.5 if s.get("fill", True) else 0.16))
    text = QPainterPath()
    text.setFillRule(Qt.WindingFill)
    for p, _ in runs:
        text.addPath(QTransform().translate(px - nink.left(), py + cap).map(p))
    pill.setFillRule(Qt.WindingFill)
    cut = pill.subtracted(text.simplified())
    items, sw, sh = symbol(s, H * 1.25)
    g = H * 0.32 * s["gap"] if items else 0
    rowH = max(H, sh)
    x0 = sw + g
    add(sc, shifted(items, 0, (rowH - sh) / 2))
    sc.add(QTransform().translate(x0, (rowH - H) / 2).map(cut), fill=prim)
    if s["tagline"].strip():
        tsize = size * 0.3 * s["tfont"].get("scale", 1.0)
        titems, tink = build_tag(s, tsize, W)
        tcap = _tcap(s, tsize)
        add(sc, shifted(titems, x0 + (W - tink.width()) / 2 - tink.left(), rowH + (rowH - H) / 2 * 0 + size * 0.42 + tcap))


def _frame(s, sc):
    """a thin frame around the name, with the symbol breaking the top edge"""
    size = F * 0.9 * s["font"].get("size", 1.0)
    nitems, nink = build_name(s, size)
    cap = _cap(s, size)
    has_tag = bool(s["tagline"].strip())
    tsize = size * 0.3 * s["tfont"].get("scale", 1.0)
    titems, tink = build_tag(s, tsize, nink.width())
    tcap = _tcap(s, tsize)
    items, sw, sh = symbol(s, F * 1.25)
    inner = max(nink.width(), tink.width() if has_tag else 0)
    px, py = size * 0.7, size * 0.55
    topgap = sh * 0.55 if items else 0
    fw = inner + 2 * px
    body = cap + ((size * 0.3 + _desc(nink, size) + tcap) if has_tag else 0)
    fh = body + 2 * py + topgap
    lw = size * 0.05
    rect = QPainterPath()
    rect.addRect(QRectF(0, 0, fw, fh))
    frame = marks.stroked(rect, lw, Qt.FlatCap, Qt.MiterJoin)
    if items:
        gap = QPainterPath()
        gap.addRect(QRectF(fw / 2 - sw / 2 - size * 0.25, -lw * 2, sw + size * 0.5, sh * 0.55 + lw * 3 + size * 0.0))
        frame = frame.subtracted(gap)
    sc.add(frame, fill=color(s, "primary"))
    if items:
        add(sc, shifted(items, fw / 2 - sw / 2, -sh * 0.45))
    y = topgap + py + cap
    add(sc, shifted(nitems, (fw - nink.width()) / 2 - nink.left(), y))
    if has_tag:
        y += size * 0.3 + _desc(nink, size) + tcap
        add(sc, shifted(titems, (fw - tink.width()) / 2 - tink.left(), y))
