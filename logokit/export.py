"""Scene -> SVG, PNG, PDF, EPS, AI (PDF compatible), ICO, ICNS. Everything is vector outlines, no fonts needed."""
import json
import os
import struct

from PySide6.QtCore import QBuffer, QByteArray, QIODevice, QMarginsF, QRectF, QSizeF, Qt
from PySide6.QtGui import QColor, QImage, QPageSize, QPainter, QPdfWriter

from .scene import Grad, closed_d, paint


def source_rect(scene, pad=0.08):
    r = scene.bounds()
    p = max(r.width(), r.height()) * pad
    return r.adjusted(-p, -p, p, p)


def _col(c):
    return QColor(c).name().upper()


def to_svg(scene, bg=None, pad=0.08, title="Logo"):
    r = source_rect(scene, pad) if pad is not None else scene.bounds()
    f = lambda v: ("%.2f" % v).rstrip("0").rstrip(".")
    defs, body, gid = [], [], 0
    if bg:
        body.append(f'<rect x="{f(r.x())}" y="{f(r.y())}" width="{f(r.width())}" height="{f(r.height())}" fill="{_col(bg)}"/>')
    import math
    for it in scene.items:
        if it.path.isEmpty():
            continue
        fill = "none"
        if isinstance(it.fill, Grad):
            gid += 1
            a = math.radians(it.fill.angle)
            dx, dy = math.cos(a) / 2, math.sin(a) / 2
            defs.append(f'<linearGradient id="g{gid}" x1="{f(.5 - dx)}" y1="{f(.5 - dy)}" x2="{f(.5 + dx)}" y2="{f(.5 + dy)}">'
                        f'<stop offset="0" stop-color="{_col(it.fill.c1)}"/><stop offset="1" stop-color="{_col(it.fill.c2)}"/></linearGradient>')
            fill = f"url(#g{gid})"
        elif it.fill:
            fill = _col(it.fill)
        rule = ' fill-rule="evenodd"' if it.rule == Qt.OddEvenFill else ""
        body.append(f'<path d="{closed_d(it.path)}" fill="{fill}"{rule}/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{f(r.x())} {f(r.y())} {f(r.width())} {f(r.height())}" '
            f'width="{f(r.width() * 4)}" height="{f(r.height() * 4)}"><title>{title}</title>'
            + (f'<defs>{"".join(defs)}</defs>' if defs else "") + "".join(body) + "</svg>")


def to_image(scene, width, bg=None, pad=0.08, height=None):
    r = source_rect(scene, pad)
    h = height or max(1, round(width * r.height() / r.width()))
    img = QImage(int(width), int(h), QImage.Format_ARGB32)
    img.fill(QColor(bg) if bg else QColor(0, 0, 0, 0))
    p = QPainter(img)
    paint(scene, p, QRectF(0, 0, width, h), r)
    p.end()
    return img


def to_pdf(scene, path, bg=None, pad=0.08, title="Logo"):
    r = source_rect(scene, pad)
    k = 0.25                                         # scene unit -> mm (a 100 unit name is 25 mm tall)
    w, h = r.width() * k, r.height() * k
    pw = QPdfWriter(path)
    pw.setResolution(1200)
    pw.setTitle(title)
    pw.setPageSize(QPageSize(QSizeF(w, h), QPageSize.Millimeter))
    pw.setPageMargins(QMarginsF(0, 0, 0, 0))
    p = QPainter(pw)
    paint(scene, p, QRectF(0, 0, pw.width(), pw.height()), r, bg)
    p.end()


def to_eps(scene, path, bg=None, pad=0.08, title="Logo"):
    r = source_rect(scene, pad)
    k = 0.72                                          # points per scene unit
    W, H = r.width() * k, r.height() * k
    out = ["%!PS-Adobe-3.0 EPSF-3.0", f"%%Title: {title}", "%%Creator: Digonto Logo",
           f"%%BoundingBox: 0 0 {int(W + 0.999)} {int(H + 0.999)}", f"%%HiResBoundingBox: 0 0 {W:.3f} {H:.3f}", "%%EndComments",
           f"gsave {k:.5f} {-k:.5f} scale {-r.x():.3f} {-r.y() - r.height():.3f} translate" if False else
           f"gsave 0 {H:.3f} translate {k:.5f} {-k:.5f} scale {-r.x():.3f} {-r.y():.3f} translate"]

    def rgb(c):
        q = QColor(c.c1 if isinstance(c, Grad) else c)
        return f"{q.redF():.4f} {q.greenF():.4f} {q.blueF():.4f} setrgbcolor"
    if bg:
        out.append(f"{rgb(bg)} {r.x():.3f} {r.y():.3f} moveto {r.right():.3f} {r.y():.3f} lineto {r.right():.3f} {r.bottom():.3f} lineto {r.x():.3f} {r.bottom():.3f} lineto closepath fill")
    from PySide6.QtGui import QPainterPath
    for it in scene.items:
        p = it.path
        if p.isEmpty() or not it.fill:
            continue
        out.append(rgb(it.fill))
        out.append("newpath")
        i, n = 0, p.elementCount()
        start = None
        while i < n:
            e = p.elementAt(i)
            if e.type == QPainterPath.MoveToElement:
                out.append(f"{e.x:.3f} {e.y:.3f} moveto")
            elif e.type == QPainterPath.LineToElement:
                out.append(f"{e.x:.3f} {e.y:.3f} lineto")
            else:
                c2, en = p.elementAt(i + 1), p.elementAt(i + 2)
                out.append(f"{e.x:.3f} {e.y:.3f} {c2.x:.3f} {c2.y:.3f} {en.x:.3f} {en.y:.3f} curveto")
                i += 2
            i += 1
        out.append("closepath " + ("eofill" if it.rule == Qt.OddEvenFill else "fill"))
    out += ["grestore", "%%EOF", ""]
    with open(path, "w", encoding="ascii") as f:
        f.write("\n".join(out))


def png_bytes(img):
    ba = QByteArray()
    b = QBuffer(ba)
    b.open(QIODevice.WriteOnly)
    img.save(b, "PNG")
    return bytes(ba)


def square_image(scene, size, bg=None, fill=0.78):
    """the scene centered in a square canvas (icons, avatars)"""
    img = QImage(size, size, QImage.Format_ARGB32)
    img.fill(QColor(bg) if bg else QColor(0, 0, 0, 0))
    p = QPainter(img)
    m = size * (1 - fill) / 2
    paint(scene, p, QRectF(m, m, size - 2 * m, size - 2 * m))
    p.end()
    return img


def to_ico(path, imgs):
    """imgs: list of QImage (square, <= 256) stored as PNG inside the .ico"""
    datas = [png_bytes(i) for i in imgs]
    head = struct.pack("<HHH", 0, 1, len(datas))
    off = 6 + 16 * len(datas)
    ent, body = b"", b""
    for i, d in zip(imgs, datas):
        w = 0 if i.width() >= 256 else i.width()
        ent += struct.pack("<BBBBHHII", w, w, 0, 0, 1, 32, len(d), off + len(body))
        body += d
    with open(path, "wb") as f:
        f.write(head + ent + body)


def to_icns(path, images):
    """images: {size: QImage}; uses the PNG icon types"""
    types = {16: b"icp4", 32: b"icp5", 64: b"icp6", 128: b"ic07", 256: b"ic08", 512: b"ic09", 1024: b"ic10"}
    chunks = b""
    for s, img in sorted(images.items()):
        if s in types:
            d = png_bytes(img)
            chunks += types[s] + struct.pack(">I", len(d) + 8) + d
    with open(path, "wb") as f:
        f.write(b"icns" + struct.pack(">I", len(chunks) + 8) + chunks)


def draw_cover(p, img, rect, dim=0):
    """a picture scaled to fill the rectangle (cropped in the middle), optionally darkened (dim 0..100)"""
    from PySide6.QtCore import Qt
    k = max(rect.width() / img.width(), rect.height() / img.height())
    w, h = img.width() * k, img.height() * k
    p.save()
    p.setRenderHint(QPainter.SmoothPixmapTransform)
    p.drawImage(QRectF(rect.center().x() - w / 2, rect.center().y() - h / 2, w, h), img)
    if dim:
        p.fillRect(rect, QColor(0, 0, 0, int(255 * dim / 100)))
    p.restore()


def on_image(scene, img, width=1920, height=1080, dim=0, frac=0.5):
    """the logo centered on top of a picture"""
    out = QImage(width, height, QImage.Format_ARGB32)
    p = QPainter(out)
    p.setRenderHint(QPainter.Antialiasing)
    draw_cover(p, img, QRectF(0, 0, width, height), dim)
    src = source_rect(scene, 0.0)
    k = min(width * frac / src.width(), height * 0.6 / src.height())
    w, h = src.width() * k, src.height() * k
    paint(scene, p, QRectF((width - w) / 2, (height - h) / 2, w, h), src)
    p.end()
    return out
