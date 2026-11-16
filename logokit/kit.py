"""Brand kit: every logo file a business needs, favicons, social images and a brand-guide PDF."""
import copy
import datetime
import json
import os
import zipfile

from PySide6.QtCore import QMarginsF, QRectF, QSizeF, Qt
from PySide6.QtGui import QColor, QFont, QFontMetricsF, QImage, QPageSize, QPainter, QPdfWriter, QPen, QTransform

from . import compose, export, ideas, palettes, textkit
from .scene import paint

VARIANTS = [("primary", "Primary logo"), ("horizontal", "Horizontal"), ("stacked", "Stacked"), ("icon", "Symbol only"),
            ("wordmark", "Wordmark only"), ("black", "One color, black"), ("white", "One color, white (for dark backgrounds)"),
            ("reverse", "On dark background")]


def slug(name):
    s = "".join(c if c.isalnum() else "-" for c in name.strip().lower())
    while "--" in s:
        s = s.replace("--", "-")
    return s.strip("-") or "logo"


def variant(spec, kind):
    s = copy.deepcopy(compose.merged(spec))
    c = s["colors"]
    has_sym = s["symbol"]["kind"] != "none"
    if kind == "horizontal":
        s["layout"] = "horizontal"
    elif kind == "stacked":
        s["layout"] = "stacked"
    elif kind == "icon":
        s["layout"] = "symbol"
        if not has_sym:
            s["symbol"].update(kind="monogram", container="rounded", cmode="solid")
    elif kind == "wordmark":
        s["layout"] = "wordmark"
        s["symbol"]["kind"] = "none"
    elif kind in ("black", "white"):
        v = "#000000" if kind == "black" else "#FFFFFF"
        s["colors"] = {"primary": v, "secondary": v, "text": v, "bg": "#FFFFFF" if kind == "black" else "#000000"}
        s["symbol"]["grad"] = False
        s["symbol"]["keep"] = False
        s["name_role"] = "text"
        s["tag_role"] = "primary"
        if s["layout"] in ("emblem",):
            s["fill"] = False
    elif kind == "reverse":
        s["colors"] = ideas.dark_variant({"primary": c["primary"], "secondary": c["secondary"], "text": c["text"], "bg": c["bg"]})
    return s


def bg_of(spec, kind):
    s = variant(spec, kind)
    if kind == "reverse":
        return s["colors"]["bg"]
    if kind == "white":
        return "#000000"
    return None


def cmyk(h):
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
    k = 1 - max(r, g, b)
    if k >= 1:
        return 0, 0, 0, 100
    return tuple(round(v * 100) for v in ((1 - r - k) / (1 - k), (1 - g - k) / (1 - k), (1 - b - k) / (1 - k), k))


def color_rows(spec):
    c = compose.merged(spec)["colors"]
    return [("Primary", c["primary"]), ("Secondary", c["secondary"]), ("Text", c["text"]), ("Background", c["bg"])]


def colors_text(spec):
    out = ["BRAND COLORS", ""]
    for n, h in color_rows(spec):
        h = palettes.norm(h)
        rgb = tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
        out.append(f"{n:<11} {h}   RGB {rgb[0]}, {rgb[1]}, {rgb[2]}   CMYK {'%d %d %d %d' % cmyk(h)} (approximate, check with your printer)")
    return "\n".join(out) + "\n"


def fonts_text(spec):
    s = compose.merged(spec)
    lines = ["FONTS", ""]
    for role, f in (("Name", s["font"]), ("Tagline", s["tfont"])):
        meta = textkit.BY_ID.get(f["id"], {})
        lines.append(f"{role}: {meta.get('name', f['id'])} ({'Bold' if f.get('bold') and textkit.has_bold(f['id']) else 'Regular'})  -  licence {meta.get('license', 'OFL-1.1')}")
    lines += ["", "These are open-source fonts: free for any use, including commercial. Download: https://fonts.google.com (search the name).",
              "The logo files themselves contain outlines, so no font has to be installed to use them."]
    return "\n".join(lines) + "\n"


# ------------------------------------------------------------------ guide pdf
class Page:
    U = 4.0                                         # units per mm

    def __init__(self, path, title):
        self.pw = QPdfWriter(path)
        self.pw.setResolution(300)
        self.pw.setTitle(title)
        self.pw.setPageSize(QPageSize(QPageSize.A4))
        self.pw.setPageMargins(QMarginsF(0, 0, 0, 0))
        self.p = QPainter(self.pw)
        k = self.pw.resolution() / 25.4 / self.U
        self.p.scale(k, k)
        self.p.setRenderHint(QPainter.Antialiasing)
        self.W, self.H = 210 * self.U, 297 * self.U
        self.first = True

    def new(self, bg="#FFFFFF"):
        if not self.first:
            self.pw.newPage()
        self.first = False
        self.p.fillRect(QRectF(0, 0, self.W, self.H), QColor(bg))

    def text(self, x, y, s, size, color="#111111", font="montserrat", bold=False, track=0.0, align="left", w=None):
        f = textkit.qfont(font, bold, 0.0)
        f.setPixelSize(int(size))
        if track:
            f.setLetterSpacing(QFont.AbsoluteSpacing, track * size)
        self.p.setFont(f)
        self.p.setPen(QColor(color))
        if align == "left" and w is None:
            self.p.drawText(int(x), int(y), s)
        else:
            self.p.drawText(QRectF(x, y - size, w or self.W, size * 2.2), {"left": Qt.AlignLeft, "center": Qt.AlignHCenter, "right": Qt.AlignRight}[align] | Qt.TextWordWrap, s)

    def logo(self, scene, rect, bg=None, pad=0.0):
        paint(scene, self.p, rect, export.source_rect(scene, pad), bg)

    def end(self):
        self.p.end()


def _tile(pg, rect, scene, bg, border="#E3E8E5", label=None, pad=0.1):
    pg.p.fillRect(rect, QColor(bg))
    pg.p.setPen(QPen(QColor(border), 1.2))
    pg.p.drawRect(rect)
    inner = rect.adjusted(rect.width() * 0.1, rect.height() * 0.12, -rect.width() * 0.1, -rect.height() * 0.12)
    pg.logo(scene, inner, None, 0)
    if label:
        pg.text(rect.x(), rect.bottom() + 22, label, 11, "#55645C", "montserrat")


def guide(spec, path, brief=None):
    s = compose.merged(spec)
    c = s["colors"]
    name = s["name"].strip() or "Brand"
    pg = Page(path, f"{name} brand guidelines")
    M = 18 * pg.U
    prim = c["primary"]
    dark_theme = palettes.luminance(c["bg"]) < 0.35
    text = "#14201A"
    bgc = "#FFFFFF"                                   # the guide itself is always on white paper
    logo_bg = c["bg"]                                 # the primary logo sits on its own background
    head = lambda t, n: (pg.text(M, 30 * pg.U, t, 34, text, "montserrat", True), pg.text(M, 38 * pg.U, n, 12, "#66756D", "montserrat"))

    # cover
    rev = variant(spec, "reverse")
    pg.new(rev["colors"]["bg"])
    pg.logo(compose.build(rev), QRectF(M, 90 * pg.U, pg.W - 2 * M, 100 * pg.U))
    pg.text(0, 262 * pg.U, "BRAND GUIDELINES", 14, palettes.mix(rev["colors"]["text"], rev["colors"]["bg"], 0.25), "montserrat", True, 0.3, "center", pg.W)
    pg.text(0, 272 * pg.U, datetime.date.today().strftime("%B %Y"), 11, palettes.mix(rev["colors"]["text"], rev["colors"]["bg"], 0.5), "montserrat", False, 0.1, "center", pg.W)

    # logo
    pg.new(bgc)
    head("The logo", "Use the primary logo whenever there is room. The other versions are for tight spaces.")
    _tile(pg, QRectF(M, 52 * pg.U, pg.W - 2 * M, 80 * pg.U), compose.build(spec), logo_bg)
    tw = (pg.W - 2 * M - 12 * pg.U) / 4
    y = 150 * pg.U
    for i, (k, label) in enumerate((("horizontal", "Horizontal"), ("stacked", "Stacked"), ("icon", "Symbol"), ("wordmark", "Wordmark"))):
        _tile(pg, QRectF(M + i * (tw + 4 * pg.U), y, tw, 40 * pg.U), compose.build(variant(spec, k)), logo_bg, label=label)
    pg.text(M, 230 * pg.U, "Keep the logo's proportions. Do not redraw, stretch or recolor it - use the files supplied.", 12, "#55645C", "montserrat", False, 0, "left", pg.W - 2 * M)

    # clear space + min size
    pg.new(bgc)
    head("Clear space and size", "Keep free space around the logo so it can breathe.")
    sc = compose.build(spec)
    b = sc.bounds()
    x = pg.U * 0
    box = QRectF(M, 60 * pg.U, pg.W - 2 * M, 100 * pg.U)
    pad = 14 * pg.U
    pg.p.fillRect(box, QColor(logo_bg))
    inner = box.adjusted(pad * 2, pad * 1.5, -pad * 2, -pad * 1.5)
    pg.logo(sc, inner, None, 0)
    k = min(inner.width() / b.width(), inner.height() / b.height())
    lw, lh = b.width() * k, b.height() * k
    lr = QRectF(inner.center().x() - lw / 2, inner.center().y() - lh / 2, lw, lh)
    cap = textkit.metrics(s["font"]["id"], s["font"]["bold"])["cap"] * 100 * k
    pen = QPen(QColor("#E6533C"), 1.4, Qt.DashLine)
    pg.p.setPen(pen)
    pg.p.drawRect(lr)
    pg.p.drawRect(lr.adjusted(-cap, -cap, cap, cap))
    pg.text(lr.x() - cap, lr.y() - cap - 8, "Clear space = height of a capital letter of the name", 11, "#E6533C", "montserrat")
    pg.text(M, 190 * pg.U, "Minimum size", 18, text, "montserrat", True)
    ratio = b.width() / b.height()
    pg.text(M, 200 * pg.U, f"Print: at least {25 if ratio < 3 else 35} mm wide      Screen: at least {110 if ratio < 3 else 140} px wide", 13, "#55645C", "montserrat", False, 0, "left", pg.W - 2 * M)
    for i, wmm in enumerate((50, 35, 25)):
        r = QRectF(M + i * 60 * pg.U, 212 * pg.U, wmm * pg.U * 0.9, wmm * pg.U * 0.9 / ratio)
        pg.logo(sc, r)
        pg.text(r.x(), r.bottom() + 20, f"{wmm} mm", 10, "#66756D", "montserrat")

    # colors
    pg.new(bgc)
    head("Colors", "The palette. Use primary most, secondary as an accent.")
    rows = color_rows(spec)
    y = 55 * pg.U
    for n, h in rows:
        h = palettes.norm(h)
        pg.p.fillRect(QRectF(M, y, 70 * pg.U, 40 * pg.U), QColor(h))
        pg.p.setPen(QPen(QColor("#D5DDD8"), 1))
        pg.p.drawRect(QRectF(M, y, 70 * pg.U, 40 * pg.U))
        pg.text(M + 76 * pg.U, y + 12 * pg.U, n, 18, text, "montserrat", True)
        rgb = tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
        pg.text(M + 76 * pg.U, y + 22 * pg.U, f"HEX  {h}", 12, "#55645C", "montserrat")
        pg.text(M + 76 * pg.U, y + 30 * pg.U, f"RGB  {rgb[0]}  {rgb[1]}  {rgb[2]}      CMYK  {'%d  %d  %d  %d' % cmyk(h)}", 12, "#55645C", "montserrat")
        for j, t in enumerate((0.2, 0.4, 0.6, 0.8)):
            pg.p.fillRect(QRectF(M + 76 * pg.U + j * 22 * pg.U, y + 34 * pg.U, 20 * pg.U, 5 * pg.U), QColor(palettes.mix(h, "#FFFFFF", 1 - t)))
        y += 52 * pg.U
    pg.text(M, 272 * pg.U, "CMYK values are a starting point. Ask your printer for a proof before a large print run.", 10, "#66756D", "montserrat")

    # typography
    pg.new(bgc)
    head("Typography", "Two fonts. Both are free, open-source fonts.")
    y = 62 * pg.U
    for role, f in (("Name", s["font"]), ("Tagline and text", s["tfont"])):
        meta = textkit.BY_ID.get(f["id"], {})
        pg.text(M, y, role.upper(), 11, "#66756D", "montserrat", True, 0.2)
        pg.text(M, y + 22 * pg.U, meta.get("name", f["id"]), 42, text, f["id"], bool(f.get("bold")))
        pg.text(M, y + 36 * pg.U, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", 16, text, f["id"], bool(f.get("bold")), 0.05)
        pg.text(M, y + 44 * pg.U, "abcdefghijklmnopqrstuvwxyz 0123456789", 16, text, f["id"], bool(f.get("bold")))
        y += 74 * pg.U
    pg.text(M, 250 * pg.U, "Download the fonts free at fonts.google.com. The logo files contain outlines, so they never need the fonts.", 11, "#55645C", "montserrat", False, 0, "left", pg.W - 2 * M)

    # backgrounds
    pg.new(bgc)
    head("On backgrounds", "Pick the version with enough contrast to the background.")
    brand_ok = palettes.contrast(prim, "#FFFFFF") >= 2.5
    cells = [("primary", logo_bg, "Main background"), ("black", "#FFFFFF", "One color, black"),
             ("reverse", rev["colors"]["bg"], "Dark background"), ("white", prim if brand_ok else "#2B2F2D", "Brand color" if brand_ok else "Dark gray"),
             ("black", palettes.mix("#FFFFFF", prim, 0.12) if brand_ok else "#EDEDED", "Light tint"), ("white", "#1A1A1A", "One color, white")]
    cw = (pg.W - 2 * M - 8 * pg.U) / 2
    for i, (v, bg, label) in enumerate(cells):
        r = QRectF(M + (i % 2) * (cw + 8 * pg.U), 54 * pg.U + (i // 2) * 62 * pg.U, cw, 50 * pg.U)
        _tile(pg, r, compose.build(variant(spec, v)), bg, label=label)

    # dont's
    pg.new(bgc)
    head("Please do not", "Small changes make a brand look careless.")
    sc = compose.build(spec)
    bad = [("Stretch or squash", lambda p, r: _draw_tr(pg, sc, r, QTransform().scale(1.5, 0.75))),
           ("Rotate", lambda p, r: _draw_tr(pg, sc, r, QTransform().rotate(-14))),
           ("Change the colors", lambda p, r: pg.logo(compose.build(_recolor(spec)), r)),
           ("Use low contrast", lambda p, r: pg.logo(compose.build(_lowcontrast(spec)), r)),
           ("Add effects", lambda p, r: _shadow(pg, sc, r)),
           ("Put it on a busy background", lambda p, r: _busy(pg, sc, r))]
    cw = (pg.W - 2 * M - 8 * pg.U) / 2
    for i, (label, fn) in enumerate(bad):
        r = QRectF(M + (i % 2) * (cw + 8 * pg.U), 54 * pg.U + (i // 2) * 62 * pg.U, cw, 50 * pg.U)
        pg.p.fillRect(r, QColor(logo_bg))
        pg.p.setPen(QPen(QColor("#E3E8E5"), 1.2))
        pg.p.drawRect(r)
        pg.p.save()
        pg.p.setClipRect(r)
        fn(pg, r.adjusted(r.width() * 0.12, r.height() * 0.2, -r.width() * 0.12, -r.height() * 0.2))
        pg.p.restore()
        pg.p.setPen(QPen(QColor("#C93C3C"), 2.4))
        pg.p.drawLine(int(r.right() - 22), int(r.y() + 8), int(r.right() - 8), int(r.y() + 22))
        pg.p.drawLine(int(r.right() - 22), int(r.y() + 22), int(r.right() - 8), int(r.y() + 8))
        pg.text(r.x(), r.bottom() + 22, label, 11, "#55645C", "montserrat")
    pg.end()


def _draw_tr(pg, sc, r, tr):
    pg.p.save()
    pg.p.translate(r.center())
    pg.p.transform()
    pg.p.setTransform(tr * pg.p.transform())
    paint(sc, pg.p, QRectF(-r.width() / 2, -r.height() / 2, r.width(), r.height()))
    pg.p.restore()


def _recolor(spec):
    s = copy.deepcopy(compose.merged(spec))
    s["colors"].update(primary="#E83E8C", secondary="#18C5D8", text="#7B2FF7")
    return s


def _lowcontrast(spec):
    s = copy.deepcopy(compose.merged(spec))
    s["colors"].update(primary="#E6E6E6", secondary="#EEEEEE", text="#DADADA")
    return s


def _shadow(pg, sc, r):
    pg.p.save()
    pg.p.translate(7, 7)
    paint(sc.recolored(lambda c: "#9AA3A0"), pg.p, r)
    pg.p.restore()
    paint(sc, pg.p, r)


def _busy(pg, sc, r):
    for i in range(14):
        pg.p.fillRect(QRectF(r.x() - 40 + i * (r.width() / 8), r.y() - 30, r.width() / 14, r.height() + 60), QColor(["#F2994A", "#EB5757", "#2D9CDB", "#27AE60"][i % 4]))
    paint(sc, pg.p, r)


# ------------------------------------------------------------------ the kit
def build_kit(spec, folder, parts, zip_it=False, progress=None, brief=None):
    """parts: set of 'logos', 'icons', 'social', 'guide'. Returns the folder (or zip) path."""
    s = compose.merged(spec)
    name = s["name"].strip() or "Brand"
    base = os.path.join(folder, f"{slug(name)}-brand-kit")
    n = 1
    root = base
    while os.path.exists(root):
        n += 1
        root = f"{base}-{n}"
    os.makedirs(root)
    steps = ["logos", "icons", "social", "guide", "docs"]
    todo = [x for x in steps if x in parts or x == "docs"]
    done = 0

    def tick(label):
        nonlocal done
        done += 1
        if progress:
            progress(done, len(todo), label)
    sl = slug(name)
    if "logos" in parts:
        for fmt in ("svg", "png", "pdf", "eps", "ai"):
            os.makedirs(os.path.join(root, "logo", fmt))
        for k, label in VARIANTS:
            v = variant(spec, k)
            sc = compose.build(v)
            bg = bg_of(spec, k)
            fn = f"{sl}-{k}"
            with open(os.path.join(root, "logo", "svg", fn + ".svg"), "w", encoding="utf-8") as f:
                f.write(export.to_svg(sc, bg, 0.08, name))
            export.to_image(sc, 2400, bg).save(os.path.join(root, "logo", "png", fn + ".png"))
            export.to_pdf(sc, os.path.join(root, "logo", "pdf", fn + ".pdf"), bg, 0.08, name)
            export.to_pdf(sc, os.path.join(root, "logo", "ai", fn + ".ai"), bg, 0.08, name)
            export.to_eps(sc, os.path.join(root, "logo", "eps", fn + ".eps"), bg, 0.08, name)
        tick("Logo files")
    if "icons" in parts:
        d = os.path.join(root, "icons")
        os.makedirs(d)
        ic = compose.build(variant(spec, "icon"))
        bg = s["colors"]["bg"]
        sizes = {sz: export.square_image(ic, sz, None, 0.86) for sz in (16, 32, 48, 64, 128, 256, 512, 1024)}
        export.to_ico(os.path.join(d, "favicon.ico"), [sizes[z] for z in (16, 32, 48, 64, 128, 256)])
        export.to_icns(os.path.join(d, "app-icon.icns"), sizes)
        sizes[256].save(os.path.join(d, "icon-256.png"))
        for z in (32, 192, 512):
            export.square_image(ic, z, None, 0.86).save(os.path.join(d, f"icon-{z}.png"))
        export.square_image(ic, 180, bg, 0.62).save(os.path.join(d, "apple-touch-icon-180.png"))
        with open(os.path.join(d, "icon.svg"), "w", encoding="utf-8") as f:
            f.write(export.to_svg(ic, None, 0.04, name))
        with open(os.path.join(d, "html-head.txt"), "w", encoding="utf-8") as f:
            f.write('<link rel="icon" href="/favicon.ico" sizes="any">\n<link rel="icon" href="/icon.svg" type="image/svg+xml">\n'
                    '<link rel="apple-touch-icon" href="/apple-touch-icon-180.png">\n')
        tick("Icons and favicon")
    if "social" in parts:
        d = os.path.join(root, "social")
        os.makedirs(d)
        ic = compose.build(variant(spec, "icon"))
        full = compose.build(variant(spec, "primary"))
        bgc = s["colors"]["bg"]
        export.square_image(ic, 1024, bgc, 0.62).save(os.path.join(d, "avatar-1024.png"))

        def banner(w, h, fname, fill):
            img = QImage(w, h, QImage.Format_ARGB32)
            img.fill(QColor(bgc))
            p = QPainter(img)
            m = h * (1 - fill) / 2
            paint(full, p, QRectF(w * 0.12, m, w * 0.76, h - 2 * m))
            p.end()
            img.save(os.path.join(d, fname))
        banner(1200, 630, "og-image-1200x630.png", 0.5)
        banner(1500, 500, "cover-1500x500.png", 0.5)
        banner(1080, 1080, "square-post-1080.png", 0.35)
        tick("Social images")
    if "guide" in parts:
        guide(spec, os.path.join(root, f"{sl}-brand-guide.pdf"), brief)
        tick("Brand guide")
    with open(os.path.join(root, "colors.txt"), "w", encoding="utf-8") as f:
        f.write(colors_text(spec))
    with open(os.path.join(root, "fonts.txt"), "w", encoding="utf-8") as f:
        f.write(fonts_text(spec))
    with open(os.path.join(root, f"{sl}.dlgo"), "w", encoding="utf-8") as f:
        json.dump({"app": "digonto-logo", "version": 2, "spec": compose.merged(spec), "brief": brief or {}}, f)
    with open(os.path.join(root, "README.txt"), "w", encoding="utf-8") as f:
        f.write(f"{name} - brand kit\nMade with Digonto Logo on {datetime.date.today().isoformat()}\n\n"
                "logo/      Your logo as SVG, PNG, PDF, EPS and AI (opens in Illustrator). Pick 'primary' first.\n"
                "icons/     Favicon, app icon (.ico, .icns), PNG sizes and the HTML lines for your website.\n"
                "social/    Avatar, Open Graph image, cover image, square post.\n"
                f"{sl}-brand-guide.pdf  How to use the logo, colors and fonts.\n"
                f"{sl}.dlgo  Open this in Digonto Logo to change the design later.\n\n"
                "Fonts and the icon set are open source (SIL Open Font License / MIT). Free for commercial use.\n"
                "Note: the .ai files are PDF-compatible files that Illustrator opens; EPS files keep gradients as the first color.\n")
    tick("Notes")
    if zip_it:
        zp = root + ".zip"
        with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
            for dp, _, fs in os.walk(root):
                for fn in fs:
                    full = os.path.join(dp, fn)
                    z.write(full, os.path.relpath(full, os.path.dirname(root)))
        return zp
    return root
