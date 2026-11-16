"""Your own symbol: an SVG file (its shapes are kept as vectors) or a PNG/JPG picture (traced into a one-color vector shape).
Everything ends as path data in a 256 x 256 box, so it goes into the logo like any other symbol."""
import math
import re
import xml.etree.ElementTree as ET

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QImage, QPainterPath, QPainterPathStroker, QTransform

BOX = 256.0
_NUM = re.compile(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")
_TOK = re.compile(r"([MmLlHhVvCcSsQqTtAaZz])|([-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?)")


# ------------------------------------------------------------------ path data
def _arc(path, x0, y0, rx, ry, rot, large, sweep, x, y):
    """SVG elliptical arc -> cubic curves"""
    if (x0, y0) == (x, y):
        return
    rx, ry = abs(rx), abs(ry)
    if rx == 0 or ry == 0:
        path.lineTo(x, y)
        return
    phi = math.radians(rot)
    c, s = math.cos(phi), math.sin(phi)
    dx, dy = (x0 - x) / 2, (y0 - y) / 2
    x1, y1 = c * dx + s * dy, -s * dx + c * dy
    lam = (x1 * x1) / (rx * rx) + (y1 * y1) / (ry * ry)
    if lam > 1:
        rx, ry = rx * math.sqrt(lam), ry * math.sqrt(lam)
    num = rx * rx * ry * ry - rx * rx * y1 * y1 - ry * ry * x1 * x1
    den = rx * rx * y1 * y1 + ry * ry * x1 * x1
    co = math.sqrt(max(0.0, num / den)) * (-1 if large == sweep else 1) if den else 0.0
    cx1, cy1 = co * rx * y1 / ry, -co * ry * x1 / rx
    cx, cy = c * cx1 - s * cy1 + (x0 + x) / 2, s * cx1 + c * cy1 + (y0 + y) / 2

    def ang(ux, uy, vx, vy):
        a = math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)
        return a
    t1 = ang(1, 0, (x1 - cx1) / rx, (y1 - cy1) / ry)
    dt = ang((x1 - cx1) / rx, (y1 - cy1) / ry, (-x1 - cx1) / rx, (-y1 - cy1) / ry)
    if not sweep and dt > 0:
        dt -= 2 * math.pi
    elif sweep and dt < 0:
        dt += 2 * math.pi
    n = max(1, int(math.ceil(abs(dt) / (math.pi / 2) - 1e-9)))
    d = dt / n
    k = 4 / 3 * math.tan(d / 4)
    for i in range(n):
        a1, a2 = t1 + i * d, t1 + (i + 1) * d
        p1 = (math.cos(a1) - k * math.sin(a1), math.sin(a1) + k * math.cos(a1))
        p2 = (math.cos(a2) + k * math.sin(a2), math.sin(a2) - k * math.cos(a2))
        p3 = (math.cos(a2), math.sin(a2))

        def tr(p):
            return (c * rx * p[0] - s * ry * p[1] + cx, s * rx * p[0] + c * ry * p[1] + cy)
        a, b, e = tr(p1), tr(p2), tr(p3)
        path.cubicTo(a[0], a[1], b[0], b[1], e[0], e[1])


def parse_path(d):
    """SVG path data (all commands, relative and absolute, arcs) -> QPainterPath"""
    toks = [(m.group(1), m.group(2)) for m in _TOK.finditer(d or "")]
    path = QPainterPath()
    i, cmd = 0, None
    x = y = sx = sy = 0.0
    lc = None                                       # last control point for S / T
    last = ""

    def num():
        nonlocal i
        v = float(toks[i][1])
        i += 1
        return v
    while i < len(toks):
        if toks[i][0]:
            cmd = toks[i][0]
            i += 1
            if cmd in "Zz":
                path.closeSubpath()
                x, y = sx, sy
                last = "z"
                continue
        if cmd is None or i >= len(toks) or toks[i][1] is None:
            continue
        rel = cmd.islower()
        c = cmd.upper()
        try:
            if c == "M":
                nx, ny = num(), num()
                x, y = (x + nx, y + ny) if rel else (nx, ny)
                path.moveTo(x, y)
                sx, sy = x, y
                cmd = "l" if rel else "L"
            elif c == "L":
                nx, ny = num(), num()
                x, y = (x + nx, y + ny) if rel else (nx, ny)
                path.lineTo(x, y)
            elif c == "H":
                nx = num()
                x = x + nx if rel else nx
                path.lineTo(x, y)
            elif c == "V":
                ny = num()
                y = y + ny if rel else ny
                path.lineTo(x, y)
            elif c == "C":
                a = [num() for _ in range(6)]
                if rel:
                    a = [a[0] + x, a[1] + y, a[2] + x, a[3] + y, a[4] + x, a[5] + y]
                path.cubicTo(*a)
                lc = (a[2], a[3])
                x, y = a[4], a[5]
            elif c == "S":
                a = [num() for _ in range(4)]
                if rel:
                    a = [a[0] + x, a[1] + y, a[2] + x, a[3] + y]
                c1 = (2 * x - lc[0], 2 * y - lc[1]) if (lc and last in "CS") else (x, y)
                path.cubicTo(c1[0], c1[1], a[0], a[1], a[2], a[3])
                lc = (a[0], a[1])
                x, y = a[2], a[3]
            elif c == "Q":
                a = [num() for _ in range(4)]
                if rel:
                    a = [a[0] + x, a[1] + y, a[2] + x, a[3] + y]
                path.quadTo(*a)
                lc = (a[0], a[1])
                x, y = a[2], a[3]
            elif c == "T":
                a = [num() for _ in range(2)]
                if rel:
                    a = [a[0] + x, a[1] + y]
                q = (2 * x - lc[0], 2 * y - lc[1]) if (lc and last in "QT") else (x, y)
                path.quadTo(q[0], q[1], a[0], a[1])
                lc = q
                x, y = a[0], a[1]
            elif c == "A":
                rx, ry, rot = num(), num(), num()
                fa, fs = int(num()), int(num())
                nx, ny = num(), num()
                if rel:
                    nx, ny = nx + x, ny + y
                _arc(path, x, y, rx, ry, rot, fa, fs, nx, ny)
                x, y = nx, ny
            last = c
        except (IndexError, ValueError, TypeError):
            break
    return path


def dumps(path):
    """QPainterPath -> compact path data (M L C Z, absolute)"""
    out = []
    n = path.elementCount()
    i = 0
    f = lambda v: ("%.2f" % v).rstrip("0").rstrip(".")
    while i < n:
        e = path.elementAt(i)
        if e.type == QPainterPath.MoveToElement:
            out.append(f"M{f(e.x)} {f(e.y)}")
        elif e.type == QPainterPath.LineToElement:
            out.append(f"L{f(e.x)} {f(e.y)}")
        elif e.type == QPainterPath.CurveToElement:
            a, b = path.elementAt(i + 1), path.elementAt(i + 2)
            out.append(f"C{f(e.x)} {f(e.y)} {f(a.x)} {f(a.y)} {f(b.x)} {f(b.y)}")
            i += 2
        i += 1
    return "".join(out) + ("Z" if out else "")


def _closed(d):
    return d if d.endswith("Z") else d + "Z"


# ------------------------------------------------------------------ SVG
def _tr(attr):
    t = QTransform()
    for name, args in re.findall(r"(\w+)\s*\(([^)]*)\)", attr or ""):
        v = [float(a) for a in _NUM.findall(args)]
        if name == "translate" and v:
            t = QTransform().translate(v[0], v[1] if len(v) > 1 else 0) * t
        elif name == "scale" and v:
            t = QTransform().scale(v[0], v[1] if len(v) > 1 else v[0]) * t
        elif name == "rotate" and v:
            if len(v) == 3:
                t = QTransform().translate(v[1], v[2]).rotate(v[0]).translate(-v[1], -v[2]) * t
            else:
                t = QTransform().rotate(v[0]) * t
        elif name == "matrix" and len(v) == 6:
            t = QTransform(*v) * t
    return t


def _style(el, inherited):
    st = dict(inherited)
    for k in ("fill", "stroke", "stroke-width", "opacity", "display", "fill-opacity"):
        if el.get(k) is not None:
            st[k] = el.get(k)
    for part in (el.get("style") or "").split(";"):
        if ":" in part:
            k, v = part.split(":", 1)
            st[k.strip()] = v.strip()
    return st


def _color(v):
    if not v or v in ("none", "transparent") or v.startswith("url"):
        return None
    c = QColor(v if v != "currentColor" else "#000000")
    return c.name().upper() if c.isValid() else None


def _shape(el, tag):
    p = QPainterPath()
    g = lambda k, dflt=0.0: float(_NUM.findall(el.get(k, str(dflt)))[0]) if _NUM.findall(el.get(k, str(dflt))) else dflt
    if tag == "path":
        return parse_path(el.get("d", ""))
    if tag == "rect":
        x, y, w, h = g("x"), g("y"), g("width"), g("height")
        rx = g("rx", g("ry"))
        ry = g("ry", rx)
        if rx or ry:
            p.addRoundedRect(QRectF(x, y, w, h), rx, ry)
        else:
            p.addRect(QRectF(x, y, w, h))
    elif tag == "circle":
        p.addEllipse(QPointF(g("cx"), g("cy")), g("r"), g("r"))
    elif tag == "ellipse":
        p.addEllipse(QPointF(g("cx"), g("cy")), g("rx"), g("ry"))
    elif tag in ("polygon", "polyline"):
        v = [float(a) for a in _NUM.findall(el.get("points", ""))]
        pts = [QPointF(v[i], v[i + 1]) for i in range(0, len(v) - 1, 2)]
        if pts:
            p.moveTo(pts[0])
            for q in pts[1:]:
                p.lineTo(q)
            if tag == "polygon":
                p.closeSubpath()
    elif tag == "line":
        p.moveTo(g("x1"), g("y1"))
        p.lineTo(g("x2"), g("y2"))
    return p


def load_svg(file):
    """-> [(QPainterPath, '#RRGGBB' or None)] in the file's own coordinates (strokes are turned into shapes)"""
    root = ET.parse(file).getroot()
    out = []

    def walk(el, tr, st):
        tag = el.tag.split("}")[-1]
        if tag in ("defs", "clipPath", "mask", "symbol", "style", "title", "desc", "metadata", "linearGradient", "radialGradient", "pattern", "filter"):
            return
        st = _style(el, st)
        t = _tr(el.get("transform")) * tr
        if st.get("display") == "none":
            return
        if tag in ("path", "rect", "circle", "ellipse", "polygon", "polyline", "line"):
            p = _shape(el, tag)
            if not p.isEmpty():
                fill = st.get("fill", "#000000")
                fc = _color(fill)
                if fc and tag != "line" and tag != "polyline":
                    out.append((t.map(p), fc))
                elif fill.startswith("url"):
                    out.append((t.map(p), "#000000"))
                sc = _color(st.get("stroke"))
                if sc:
                    w = float(_NUM.findall(st.get("stroke-width", "1"))[0]) if _NUM.findall(st.get("stroke-width", "1")) else 1.0
                    stk = QPainterPathStroker()
                    stk.setWidth(w)
                    stk.setCapStyle(Qt.RoundCap)
                    stk.setJoinStyle(Qt.RoundJoin)
                    out.append((t.map(stk.createStroke(p)), sc))
        for ch in el:
            walk(ch, t, st)
    vb = [float(a) for a in _NUM.findall(root.get("viewBox", ""))]
    base = QTransform()
    if len(vb) == 4:
        base = QTransform().translate(-vb[0], -vb[1])
    walk(root, base, {})
    return out


# ------------------------------------------------------------------ raster tracing
def _rdp(pts, eps):
    if len(pts) < 3:
        return pts
    (x1, y1), (x2, y2) = pts[0], pts[-1]
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    best, idx = -1.0, 0
    for i in range(1, len(pts) - 1):
        x, y = pts[i]
        d = abs(dy * x - dx * y + x2 * y1 - y2 * x1) / L if L else math.hypot(x - x1, y - y1)
        if d > best:
            best, idx = d, i
    if best > eps:
        return _rdp(pts[:idx + 1], eps)[:-1] + _rdp(pts[idx:], eps)
    return [pts[0], pts[-1]]


def _mask(img, invert=False, threshold=0.5):
    """image -> (w, h, set of (x, y) that belong to the shape)"""
    img = img.convertToFormat(QImage.Format_ARGB32)
    w, h = img.width(), img.height()
    alphas = [(img.pixelColor(x, y).alpha()) for y in range(0, h, max(1, h // 40)) for x in range(0, w, max(1, w // 40))]
    has_alpha = min(alphas) < 200 if alphas else False
    on = set()
    if has_alpha:
        for y in range(h):
            for x in range(w):
                if (img.pixelColor(x, y).alpha() > 127) != invert:
                    on.add((x, y))
        return w, h, on
    corners = [img.pixelColor(x, y) for x, y in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1))]
    bg = sum(c.lightnessF() for c in corners) / 4
    for y in range(h):
        for x in range(w):
            l = img.pixelColor(x, y).lightnessF()
            far = abs(l - bg) > (0.5 - (threshold - 0.5) * 0.9) * 0.9 + 0.02 if False else abs(l - bg) > (1.0 - threshold) * 0.8 + 0.05
            if far != invert:
                on.add((x, y))
    return w, h, on


def trace(img, invert=False, threshold=0.5, size=360):
    """picture -> one QPainterPath in a 256 box (the shape is whatever differs from the background)"""
    if img.isNull():
        return QPainterPath()
    k = size / max(img.width(), img.height())
    if k < 1 or max(img.width(), img.height()) < 200:
        img = img.scaled(int(img.width() * k), int(img.height() * k), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
    w, h, on = _mask(img, invert, threshold)
    if not on or len(on) > 0.97 * w * h:
        return QPainterPath()
    # directed boundary edges with the shape on the left-hand side
    nxt = {}
    for (x, y) in on:
        if (x, y - 1) not in on:
            nxt.setdefault((x, y), []).append((x + 1, y))
        if (x + 1, y) not in on:
            nxt.setdefault((x + 1, y), []).append((x + 1, y + 1))
        if (x, y + 1) not in on:
            nxt.setdefault((x + 1, y + 1), []).append((x, y + 1))
        if (x - 1, y) not in on:
            nxt.setdefault((x, y + 1), []).append((x, y))
    loops = []
    while nxt:
        start = next(iter(nxt))
        loop, cur, prev_dir = [start], start, None
        while True:
            outs = nxt.get(cur)
            if not outs:
                break
            if len(outs) > 1 and prev_dir is not None:      # keep turning the same way so touching pixels stay apart
                def turn(o):
                    d = (o[0] - cur[0], o[1] - cur[1])
                    return prev_dir[0] * d[1] - prev_dir[1] * d[0]
                outs.sort(key=turn)
            n = outs.pop(0)
            if not outs:
                del nxt[cur]
            prev_dir = (n[0] - cur[0], n[1] - cur[1])
            cur = n
            if cur == start:
                break
            loop.append(cur)
        if len(loop) > 3:
            loops.append(loop)
    path = QPainterPath()
    path.setFillRule(Qt.OddEvenFill)
    for loop in loops:
        # drop collinear points first, then simplify
        pts = [p for i, p in enumerate(loop) if not (loop[i - 1][0] == p[0] == loop[(i + 1) % len(loop)][0] or loop[i - 1][1] == p[1] == loop[(i + 1) % len(loop)][1])]
        if len(pts) < 3:
            continue
        half = len(pts) // 2
        simp = _rdp(pts[:half + 1], 0.75)[:-1] + _rdp(pts[half:] + [pts[0]], 0.75)[:-1]
        if len(simp) < 3:
            continue
        path.moveTo(*simp[0])
        for q in simp[1:]:
            path.lineTo(*q)
        path.closeSubpath()
    return path


# ------------------------------------------------------------------ into the 256 box
def normalize(parts):
    """[(path, color|None)] -> (list of [d, color], ...) fitted into the 256 box, aspect kept"""
    union = QPainterPath()
    for p, _ in parts:
        union.addPath(p)
    r = union.boundingRect()
    if r.isEmpty():
        return []
    k = BOX / max(r.width(), r.height())
    tr = QTransform().translate((BOX - r.width() * k) / 2, (BOX - r.height() * k) / 2).scale(k, k).translate(-r.x(), -r.y())
    return [[_closed(dumps(tr.map(p))), c] for p, c in parts if not p.isEmpty()]


def from_file(file, invert=False, threshold=0.5):
    """any .svg / .png / .jpg -> {'parts': [[d, color|None]...], 'name': str, 'colors': bool, 'kind': 'svg'|'image'}"""
    import os
    name = os.path.basename(file)
    if file.lower().endswith(".svg"):
        parts = load_svg(file)
        norm = normalize(parts)
        return {"parts": norm, "name": name, "colors": len({c for _, c in norm if c}) > 0, "kind": "svg"}
    img = QImage(file)
    p = trace(img, invert, threshold)
    return {"parts": normalize([(p, None)]), "name": name, "colors": False, "kind": "image"}


def paths(custom):
    """stored custom symbol -> [(QPainterPath, color|None)]"""
    return [(parse_path(d), c) for d, c in (custom or {}).get("parts", [])]
