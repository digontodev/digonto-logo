"""Digonto Logo - a complete logo and brand creator. Type your business, pick an idea, make it yours, export the whole brand kit."""
import copy
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from PySide6.QtCore import QPointF, QRectF, QSize, Qt, QTimer
from PySide6.QtGui import QAction, QColor, QFont, QIcon, QImage, QKeySequence, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import (QApplication, QButtonGroup, QCheckBox, QColorDialog, QComboBox, QFileDialog, QFrame, QGridLayout,
                               QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QMainWindow, QMessageBox,
                               QPlainTextEdit, QProgressBar, QPushButton, QScrollArea, QSizePolicy, QSlider, QSpinBox,
                               QStackedWidget, QTabWidget, QVBoxLayout, QWidget)

import digonto_ui as ui
from logokit import __version__ as VERSION
from logokit import compose, custom, export, icons, ideas, kit, marks, palettes, textkit
from logokit.scene import paint

APP_NAME = "Digonto Logo"
SLUG = "digonto-logo"
G = "#C2395C"
QSS = """
QMainWindow{background:#F6F2FA;} QMenuBar{background:#EDE6F4; color:#1B1040;} QMenu{background:white; color:#1B1040;} QMenu::item:selected{background:#FBDCE5;} QStatusBar{background:#EDE6F4;color:#5B5278;}
QLineEdit,QPlainTextEdit,QComboBox,QSpinBox{background:white; border:1px solid #D0C4E1; border-radius:6px; padding:6px;}
QComboBox QAbstractItemView::item{min-height:24px; color:#1B1040; background:white;} QComboBox QAbstractItemView::item:selected,QComboBox QAbstractItemView::item:hover{background:#FBDCE5; color:#1B1040;}
QComboBox QAbstractItemView{background:white; color:#1B1040; selection-background-color:#FBDCE5; selection-color:#1B1040; border:1px solid #D0C4E1;}
QPushButton{background:white; border:1px solid #D0C4E1; border-radius:6px; padding:6px 12px;}
QPushButton:hover{background:#EDE6F4;}
QPushButton:checked{background:qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF6F8E, stop:1 #FFB05A); color:#2A1241; border-color:#FF6F8E;}
QPushButton#primary{background:qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF6F8E, stop:1 #FFB05A); color:#2A1241; border-color:#FF6F8E; font-weight:600; padding:9px 18px;}
QPushButton#primary:hover{background:qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF86A1, stop:1 #FFC273);}
QPushButton#primary:disabled{background:#E2B3C2; border-color:#E2B3C2;}
QLabel#h{font-size:11px; font-weight:700; color:#5B5278; letter-spacing:1px;}
QTabWidget::pane{border:0; background:white;} QTabBar::tab{padding:8px 11px; background:#EDE6F4; border:0; margin-right:1px;}
QTabBar::tab:selected{background:white; color:#8A2150; font-weight:600;}
QListWidget{background:white; border:1px solid #DDD3E9; border-radius:6px;}
QListWidget::item:selected{background:#FBDCE5; color:#1B1040;}
QProgressBar{border:1px solid #D0C4E1; border-radius:6px; text-align:center; background:white;} QProgressBar::chunk{background:qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF6F8E, stop:1 #FFB05A); border-radius:5px;}
"""


def base_dir():
    env = (os.environ.get("DIGONTO_BASE") or os.environ.get("PROTTOY_BASE"))
    return env if env else os.path.dirname(os.path.dirname(HERE))


def add_recent(path):
    rp = os.path.join(base_dir(), "recent.json")
    try:
        with open(rp, encoding="utf-8") as f:
            items = [r for r in json.load(f) if isinstance(r, dict)]
    except (OSError, ValueError):
        items = []
    items = [r for r in items if r.get("path") != path]
    items.insert(0, {"app": SLUG, "path": path, "time": time.time()})
    try:
        os.makedirs(base_dir(), exist_ok=True)
        with open(rp, "w", encoding="utf-8") as f:
            json.dump(items[:40], f)
    except OSError:
        pass


def heading(t):
    l = QLabel(t.upper())
    l.setObjectName("h")
    l.setStyleSheet("margin-top:8px;")
    return l


def chips(options, current, on_change, multi=False, parent=None):
    """row of toggle buttons. options = [(key, label)]. Returns (widget, group dict key->button)"""
    w = QWidget(parent)
    lay = QHBoxLayout(w)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(6)
    btns = {}
    grp = QButtonGroup(w)
    grp.setExclusive(not multi)
    for k, label in options:
        b = QPushButton(label)
        b.setCheckable(True)
        b.setChecked(k == current if not multi else k in (current or []))
        b.setStyleSheet("QPushButton{padding:5px 11px; border-radius:15px;} QPushButton:checked{background:qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF6F8E, stop:1 #FFB05A); color:#2A1241; border-color:#FF6F8E;}")
        grp.addButton(b)
        btns[k] = b
        lay.addWidget(b)
        b.clicked.connect(lambda _=False, k=k: on_change(k))
    lay.addStretch()
    return w, btns


class LogoView(QWidget):
    """paints one logo (from a spec) on a background"""

    def __init__(self, spec=None, bg=None, margin=0.14, radius=10, parent=None):
        super().__init__(parent)
        self.spec, self.bg, self.margin, self.radius = spec, bg, margin, radius
        self._key, self._scene = None, None
        self.checker = False
        self.bg_image, self.dim = None, 0

    def set_spec(self, spec, bg=None):
        self.spec = spec
        if bg is not None:
            self.bg = bg
        self.update()

    def scene(self):
        key = json.dumps(self.spec, sort_keys=True, default=str)
        if key != self._key:
            self._key = key
            try:
                self._scene = compose.build(self.spec)
            except Exception:
                self._scene = None
        return self._scene

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        path = QPainterPath()
        path.addRoundedRect(r, self.radius, self.radius)
        p.setClipPath(path)
        if self.checker:
            p.fillRect(r, QColor("#FFFFFF"))
            s = 14
            for y in range(0, int(r.height()) + s, s):
                for x in range(0, int(r.width()) + s, s):
                    if (x // s + y // s) % 2:
                        p.fillRect(QRectF(x, y, s, s), QColor("#E9EEEB"))
        elif self.bg_image is not None and not self.bg_image.isNull():
            export.draw_cover(p, self.bg_image, r, self.dim)
        else:
            bg = self.bg or compose.merged(self.spec)["colors"]["bg"]
            p.fillRect(r, QColor(bg))
        sc = self.scene()
        if sc is not None and sc.items:
            m = min(r.width(), r.height()) * self.margin
            paint(sc, p, r.adjusted(m, m, -m, -m), export.source_rect(sc, 0.0))
        p.setClipping(False)
        p.setPen(QPen(QColor("#DDD3E9"), 1))
        p.drawRoundedRect(r, self.radius, self.radius)


class Card(LogoView):
    def __init__(self, spec, on_open, on_fav, on_more, fav):
        super().__init__(spec, margin=0.16)
        self.setMinimumSize(250, 190)
        self.setCursor(Qt.PointingHandCursor)
        self.on_open, self.on_fav, self.on_more = on_open, on_fav, on_more
        self.hover = False
        self.fav = fav
        self.setMouseTracking(True)

    def enterEvent(self, e):
        self.hover = True
        self.update()

    def leaveEvent(self, e):
        self.hover = False
        self.update()

    def heart_rect(self):
        return QRectF(self.width() - 38, 8, 30, 30)

    def more_rect(self):
        return QRectF(self.width() - 76, 8, 34, 30)

    def paintEvent(self, e):
        super().paintEvent(e)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        dark = palettes.luminance(compose.merged(self.spec)["colors"]["bg"]) < 0.4
        ink = QColor("#FFFFFF" if dark else "#5B5278")
        if self.hover:
            p.setPen(QPen(QColor(G), 2.5))
            p.drawRoundedRect(QRectF(self.rect()).adjusted(1.5, 1.5, -1.5, -1.5), 10, 10)
            p.setPen(ink)
            f = p.font()
            f.setPixelSize(12)
            f.setBold(True)
            p.setFont(f)
            p.drawText(self.more_rect(), Qt.AlignCenter, "more")
        if self.hover or self.fav:
            p.setPen(QColor("#E0386B") if self.fav else ink)
            f = p.font()
            f.setPixelSize(22)
            p.setFont(f)
            p.drawText(self.heart_rect(), Qt.AlignCenter, "♥" if self.fav else "♡")

    def mousePressEvent(self, e):
        pt = e.position()
        if self.heart_rect().contains(pt):
            self.fav = not self.fav
            self.on_fav(self.spec, self.fav)
            self.update()
        elif self.hover and self.more_rect().contains(pt):
            self.on_more(self.spec)
        else:
            self.on_open(self.spec)


class ColorBtn(QPushButton):
    def __init__(self, color, on_change):
        super().__init__()
        self.setFixedSize(46, 28)
        self.on_change = on_change
        self.set(color)
        self.clicked.connect(self.pick)

    def set(self, c):
        self.color = palettes.norm(c)
        self.setStyleSheet(f"QPushButton{{background:{self.color}; border:1px solid #9787A3; border-radius:5px;}}")

    def pick(self):
        c = QColorDialog.getColor(QColor(self.color), self, "Choose a color")
        if c.isValid():
            self.set(c.name())
            self.on_change(self.color)


def swatch_icon(pal, size=40):
    pm = QPixmap(size, size)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(Qt.NoPen)
    p.setBrush(QColor(pal["bg"]))
    p.drawRoundedRect(0, 0, size, size, 8, 8)
    p.setBrush(QColor(pal["primary"]))
    p.drawPie(QRectF(5, 5, size - 10, size - 10), 90 * 16, 180 * 16)
    p.setBrush(QColor(pal["secondary"]))
    p.drawPie(QRectF(5, 5, size - 10, size - 10), 270 * 16, 180 * 16)
    p.setPen(QPen(QColor("#D0C4E1"), 1))
    p.setBrush(Qt.NoBrush)
    p.drawRoundedRect(QRectF(0.5, 0.5, size - 1, size - 1), 8, 8)
    p.end()
    return QIcon(pm)


def glyph_icon(draw, size=56, color="#1B1040"):
    pm = QPixmap(size, size)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    draw(p, size)
    p.end()
    return QIcon(pm)


# ====================================================================== pages
class BriefPage(QWidget):
    def __init__(self, win):
        super().__init__()
        self.win = win
        self.palette_choice = None
        root = QHBoxLayout(self)
        root.setContentsMargins(36, 24, 36, 24)
        root.setSpacing(34)
        left = QVBoxLayout()
        left.setSpacing(6)
        t = QLabel("Tell us about your business")
        t.setStyleSheet("font-size:26px; font-weight:700; color:#1B1040;")
        left.addWidget(t)
        s = QLabel("We make dozens of different logo ideas from this. You can change everything afterwards.")
        s.setStyleSheet("color:#5B5278; font-size:13px;")
        s.setWordWrap(True)
        left.addWidget(s)
        left.addWidget(heading("Business name"))
        self.name = QLineEdit()
        self.name.setPlaceholderText("for example  Harbor Light Coffee")
        self.name.setStyleSheet("font-size:16px; padding:9px;")
        left.addWidget(self.name)
        left.addWidget(heading("Tagline (optional)"))
        self.tag = QLineEdit()
        self.tag.setPlaceholderText("for example  Roasted fresh every morning")
        left.addWidget(self.tag)
        left.addWidget(heading("What do you do? (a few words help us choose symbols)"))
        self.desc = QPlainTextEdit()
        self.desc.setPlaceholderText("for example  Italian pizza and pasta restaurant in Cologne, wood-fired oven")
        self.desc.setFixedHeight(74)
        left.addWidget(self.desc)
        left.addWidget(heading("Kind of business"))
        self.ind = QComboBox()
        self.ind.addItem("Detect from my description", "auto")
        for k, v in ideas.INDUSTRIES.items():
            self.ind.addItem(v["label"], k)
        left.addWidget(self.ind)
        left.addWidget(heading("Style (pick any)"))
        self.style_btns = {}
        row = QHBoxLayout()
        row.setSpacing(6)
        for k, v in ideas.STYLES.items():
            b = QPushButton(v["label"])
            b.setCheckable(True)
            b.setStyleSheet("QPushButton{padding:6px 12px; border-radius:15px;} QPushButton:checked{background:qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF6F8E, stop:1 #FFB05A); color:#2A1241; border-color:#FF6F8E;}")
            b.toggled.connect(self.refresh_samples)
            self.style_btns[k] = b
            row.addWidget(b)
        row.addStretch()
        left.addLayout(row)
        left.addWidget(heading("Colors"))
        self.pal_row = QHBoxLayout()
        self.pal_row.setSpacing(6)
        self.pal_btns = {}
        auto = QPushButton("Auto")
        auto.setCheckable(True)
        auto.setChecked(True)
        auto.clicked.connect(lambda: self.choose_palette(None))
        self.pal_btns[None] = auto
        self.pal_row.addWidget(auto)
        for pid in ("tomato", "electric", "gold", "forest", "candy", "sunny", "ink", "digonto"):
            p = palettes.BY_ID[pid]
            b = QPushButton()
            b.setIcon(swatch_icon(p, 28))
            b.setIconSize(QSize(28, 28))
            b.setCheckable(True)
            b.setToolTip(p["name"])
            b.setFixedSize(40, 36)
            b.clicked.connect(lambda _=False, pid=pid: self.choose_palette(pid))
            self.pal_btns[pid] = b
            self.pal_row.addWidget(b)
        own = QPushButton("My color ...")
        own.clicked.connect(self.own_color)
        self.pal_row.addWidget(own)
        self.pal_row.addStretch()
        left.addLayout(self.pal_row)
        left.addStretch(1)
        go = QPushButton("Show me logo ideas  →")
        go.setObjectName("primary")
        go.setStyleSheet("font-size:15px;")
        go.clicked.connect(self.go)
        left.addWidget(go)
        lw = QWidget()
        lw.setLayout(left)
        lw.setMaximumWidth(560)
        root.addWidget(lw, 5)
        right = QVBoxLayout()
        r1 = QLabel("A first look")
        r1.setStyleSheet("font-size:14px; font-weight:600; color:#5B5278;")
        right.addWidget(r1)
        self.grid = QGridLayout()
        self.grid.setSpacing(12)
        self.samples = []
        for i in range(6):
            v = LogoView(None, margin=0.16)
            v.setMinimumSize(190, 140)
            self.samples.append(v)
            self.grid.addWidget(v, i // 2, i % 2)
        right.addLayout(self.grid, 1)
        rw = QWidget()
        rw.setLayout(right)
        root.addWidget(rw, 6)
        self.timer = QTimer(self, singleShot=True, interval=350, timeout=self.refresh_samples)
        for w in (self.name, self.tag):
            w.textChanged.connect(lambda: self.timer.start())
        self.desc.textChanged.connect(lambda: self.timer.start())
        self.ind.currentIndexChanged.connect(lambda: self.timer.start())
        self.refresh_samples()

    def own_color(self):
        c = QColorDialog.getColor(QColor(G), self, "Your main brand color")
        if c.isValid():
            self.choose_palette(c.name().upper())

    def choose_palette(self, pid):
        self.palette_choice = pid
        for k, b in self.pal_btns.items():
            b.setChecked(k == pid)
        self.refresh_samples()

    def brief(self):
        return {"name": self.name.text().strip(), "tagline": self.tag.text().strip(), "desc": self.desc.toPlainText().strip(),
                "industry": self.ind.currentData(), "styles": [k for k, b in self.style_btns.items() if b.isChecked()],
                "palette": self.palette_choice}

    def set_brief(self, b):
        self.name.setText(b.get("name", ""))
        self.tag.setText(b.get("tagline", ""))
        self.desc.setPlainText(b.get("desc", ""))
        i = self.ind.findData(b.get("industry", "auto"))
        self.ind.setCurrentIndex(max(0, i))
        for k, btn in self.style_btns.items():
            btn.setChecked(k in b.get("styles", []))
        self.palette_choice = b.get("palette")
        for k, btn in self.pal_btns.items():
            btn.setChecked(k == self.palette_choice)

    def refresh_samples(self, *_):
        b = self.brief()
        b["name"] = b["name"] or "Your Brand"
        for v, s in zip(self.samples, ideas.generate(b, 6, 0)):
            v.set_spec(s)

    def go(self):
        if not self.name.text().strip():
            QMessageBox.information(self, APP_NAME, "Please type your business name first.")
            self.name.setFocus()
            return
        self.win.make_ideas(self.brief())


class IdeasPage(QWidget):
    FILTERS = [("all", "All"), ("icon", "Symbol"), ("split", "Two-tone"), ("mark", "Shapes"), ("monogram", "Initials"), ("wordmark", "Wordmark"),
               ("badge", "Badge"), ("frame", "Framed"), ("emblem", "Emblem"), ("stamp", "Stamp"), ("fav", "\u2665 Favorites")]

    def __init__(self, win):
        super().__init__()
        self.win = win
        self.specs, self.title_text, self.filter = [], "", "all"
        v = QVBoxLayout(self)
        v.setContentsMargins(24, 14, 24, 10)
        top = QHBoxLayout()
        self.title = QLabel("")
        self.title.setStyleSheet("font-size:20px; font-weight:700; color:#1B1040;")
        top.addWidget(self.title)
        top.addStretch()
        w, self.fbtns = chips(self.FILTERS, "all", self.set_filter)
        top.addWidget(w)
        self.more = QPushButton("More ideas")
        self.more.clicked.connect(win.more_ideas)
        top.addWidget(self.more)
        self.back_btn = QPushButton("← All ideas")
        self.back_btn.clicked.connect(win.back_to_ideas)
        self.back_btn.hide()
        top.addWidget(self.back_btn)
        v.addLayout(top)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.host = QWidget()
        self.grid = QGridLayout(self.host)
        self.grid.setSpacing(14)
        self.grid.setAlignment(Qt.AlignTop)
        self.scroll.setWidget(self.host)
        v.addWidget(self.scroll, 1)
        self.hint = QLabel("Click an idea to customize it.  ♡ saves it to Favorites.  \"more\" shows other takes on the same idea.")
        self.hint.setStyleSheet("color:#65596E; font-size:12px;")
        v.addWidget(self.hint)
        self.cards = []

    def show_specs(self, specs, title, variations=False):
        self.specs = specs
        self.variations = variations
        self.title.setText(title)
        self.back_btn.setVisible(variations)
        self.more.setVisible(not variations)
        self.rebuild()

    def set_filter(self, k):
        self.filter = k
        self.rebuild()

    def visible_specs(self):
        if self.variations:
            return self.specs
        if self.filter == "fav":
            return self.win.favs
        if self.filter == "all":
            return self.specs
        return [s for s in self.specs if s.get("kind") == self.filter]

    def rebuild(self):
        for c in self.cards:
            c.setParent(None)
            c.deleteLater()
        self.cards = []
        favkeys = {json.dumps(f, sort_keys=True, default=str) for f in self.win.favs}
        cols = max(1, (self.width() - 70) // 290)
        for i, s in enumerate(self.visible_specs()):
            c = Card(s, self.win.open_editor, self.win.toggle_fav, self.win.show_variations, json.dumps(s, sort_keys=True, default=str) in favkeys)
            self.cards.append(c)
            self.grid.addWidget(c, i // cols, i % cols)
        for k in range(cols):
            self.grid.setColumnStretch(k, 1)
        if not self.cards:
            self.hint.setText("Nothing here yet. Press the ♡ on an idea to save it.")
        else:
            self.hint.setText("Click an idea to customize it.  ♡ saves it to Favorites.  \"more\" shows other takes on the same idea.")
        self._cols = cols

    def resizeEvent(self, e):
        super().resizeEvent(e)
        cols = max(1, (self.width() - 70) // 290)
        if getattr(self, "_cols", cols) != cols and self.cards:
            QTimer.singleShot(0, self.rebuild)


class Editor(QWidget):
    def __init__(self, win):
        super().__init__()
        self.win = win
        self.spec = compose.merged({})
        self.undo, self.redo = [], []
        self._last_group, self._last_t = None, 0
        self._busy = False
        h = QHBoxLayout(self)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)
        self.tabs = QTabWidget()
        self.tabs.setFixedWidth(380)
        self.tabs.setStyleSheet("QTabWidget>QWidget>QWidget{background:white;}")
        self.build_name_tab()
        self.build_symbol_tab()
        self.build_layout_tab()
        self.build_color_tab()
        self.build_type_tab()
        h.addWidget(self.tabs)
        h.addWidget(self.center(), 1)
        self.timer = QTimer(self, singleShot=True, interval=60, timeout=self.refresh)

    # ---- helpers
    def scroll_tab(self, title):
        sc = QScrollArea()
        sc.setWidgetResizable(True)
        sc.setFrameShape(QFrame.NoFrame)
        sc.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        w = QWidget()
        w.setStyleSheet("background:white;")
        v = QVBoxLayout(w)
        v.setContentsMargins(16, 10, 16, 16)
        sc.setWidget(w)
        self.tabs.addTab(sc, title)
        return v

    def row(self, label, widget):
        r = QHBoxLayout()
        l = QLabel(label)
        l.setMinimumWidth(78)
        r.addWidget(l)
        r.addWidget(widget, 1)
        return r

    def slider(self, lo, hi, cb, group):
        s = QSlider(Qt.Horizontal)
        s.setRange(lo, hi)
        s.valueChanged.connect(lambda v: cb(v) if not self._busy else None)
        return s

    def combo(self, items, cb):
        c = QComboBox()
        for k, label in items:
            c.addItem(label, k)
        c.currentIndexChanged.connect(lambda _: cb(c.currentData()) if not self._busy else None)
        return c

    # ---- spec edits
    def set(self, *path, value, group=None):
        if self._busy:
            return
        self.push(group or ".".join(map(str, path)))
        d = self.spec
        for k in path[:-1]:
            d = d[k]
        d[path[-1]] = value
        self.schedule()

    def push(self, group):
        now = time.time()
        if group == self._last_group and now - self._last_t < 1.2:
            self._last_t = now
            return
        self._last_group, self._last_t = group, now
        self.undo.append(copy.deepcopy(self.spec))
        self.undo = self.undo[-60:]
        self.redo.clear()

    def do_undo(self):
        if self.undo:
            self.redo.append(copy.deepcopy(self.spec))
            self.spec = self.undo.pop()
            self._last_group = None
            self.sync()
            self.refresh()

    def do_redo(self):
        if self.redo:
            self.undo.append(copy.deepcopy(self.spec))
            self.spec = self.redo.pop()
            self._last_group = None
            self.sync()
            self.refresh()

    def schedule(self):
        self.timer.start()

    def load(self, spec):
        self.spec = compose.merged(spec)
        self.undo, self.redo = [], []
        self._last_group = None
        self.sync()
        self.refresh()

    # ---- tab: name
    def build_name_tab(self):
        v = self.scroll_tab("Name")
        v.addWidget(heading("Business name"))
        self.e_name = QLineEdit()
        self.e_name.textChanged.connect(lambda t: self.set("name", value=t, group="name"))
        v.addWidget(self.e_name)
        v.addWidget(heading("Tagline"))
        self.e_tag = QLineEdit()
        self.e_tag.textChanged.connect(lambda t: self.set("tagline", value=t, group="tag"))
        v.addWidget(self.e_tag)
        v.addWidget(heading("Letters"))
        self.c_case = self.combo([("", "As typed"), ("upper", "UPPERCASE"), ("lower", "lowercase"), ("title", "Title Case")], lambda k: self.set("font", "case", value=k))
        v.addLayout(self.row("Name", self.c_case))
        self.c_tcase = self.combo([("", "As typed"), ("upper", "UPPERCASE"), ("lower", "lowercase"), ("title", "Title Case")], lambda k: self.set("tfont", "case", value=k))
        v.addLayout(self.row("Tagline", self.c_tcase))
        v.addWidget(heading("Name colors"))
        self.c_two = self.combo(compose.TWO, lambda k: self.set("font", "two", value=k))
        v.addLayout(self.row("Words", self.c_two))
        self.c_nrole = self.combo([("text", "Text color"), ("primary", "Main color"), ("secondary", "Second color")], lambda k: self.set("name_role", value=k))
        v.addLayout(self.row("Name", self.c_nrole))
        self.c_trole = self.combo([("muted", "Soft"), ("text", "Text color"), ("primary", "Main color"), ("secondary", "Second color")], lambda k: self.set("tag_role", value=k))
        v.addLayout(self.row("Tagline", self.c_trole))
        v.addStretch(1)

    # ---- tab: symbol
    def build_symbol_tab(self):
        v = self.scroll_tab("Symbol")
        v.addWidget(heading("Kind"))
        w, self.kind_btns = chips([("icon", "Icon"), ("mark", "Shape"), ("monogram", "Initials"), ("custom", "My own"), ("none", "None")], "icon", lambda k: self.set("symbol", "kind", value=k))
        v.addWidget(w)
        self.sym_stack = QStackedWidget()
        # icons
        iw = QWidget()
        il = QVBoxLayout(iw)
        il.setContentsMargins(0, 6, 0, 0)
        self.i_search = QLineEdit()
        self.i_search.setPlaceholderText("Search 1,494 icons: pizza, coffee, heart, rocket ...")
        self.i_search.textChanged.connect(lambda _: self.fill_icons())
        il.addWidget(self.i_search)
        self.i_list = QListWidget()
        self.i_list.setViewMode(QListWidget.IconMode)
        self.i_list.setIconSize(QSize(44, 44))
        self.i_list.setGridSize(QSize(58, 58))
        self.i_list.setResizeMode(QListWidget.Adjust)
        self.i_list.setMovement(QListWidget.Static)
        self.i_list.setUniformItemSizes(True)
        self.i_list.setMinimumHeight(250)
        self.i_list.itemClicked.connect(lambda it: self.set("symbol", "icon", value=it.data(Qt.UserRole), group="icon") or self.set("symbol", "kind", value="icon", group="icon"))
        il.addWidget(self.i_list)
        self.c_iw = self.combo([("fill", "Solid"), ("bold", "Outline")], lambda k: self.set("symbol", "iw", value=k))
        il.addLayout(self.row("Style", self.c_iw))
        lic = QLabel("Icons: Phosphor Icons (MIT licence). Free for commercial use.")
        lic.setStyleSheet("color:#6E6475; font-size:11px;")
        il.addWidget(lic)
        self.sym_stack.addWidget(iw)
        # marks
        mw = QWidget()
        ml = QVBoxLayout(mw)
        ml.setContentsMargins(0, 6, 0, 0)
        self.m_list = QListWidget()
        self.m_list.setViewMode(QListWidget.IconMode)
        self.m_list.setIconSize(QSize(54, 54))
        self.m_list.setGridSize(QSize(68, 68))
        self.m_list.setResizeMode(QListWidget.Adjust)
        self.m_list.setMovement(QListWidget.Static)
        self.m_list.setMinimumHeight(280)
        self.m_cat = QComboBox()
        self.m_cat.addItems(marks.CATEGORIES)
        self.m_find = QLineEdit()
        self.m_find.setPlaceholderText("Search ...")
        self.m_find.setClearButtonEnabled(True)
        frow = QHBoxLayout()
        frow.addWidget(self.m_cat, 1)
        frow.addWidget(self.m_find, 1)
        ml.addLayout(frow)
        for name, fn in marks.MARKS.items():
            def draw(p, size, fn=fn):
                k = size / 100.0
                p.scale(k * 0.92, k * 0.92)
                p.translate(4, 4)
                for path, role in fn():
                    p.fillPath(path, QColor({"a": G, "b": "#E0662A", "c": "#0F3D2E"}[role]))
            it = QListWidgetItem(glyph_icon(draw, 54), "")
            it.setData(Qt.UserRole, name)
            it.setToolTip(name.replace("_", " ").capitalize() + "  (" + marks.CATS.get(name, "") + ")")
            self.m_list.addItem(it)

        def filter_marks():
            cat, q = self.m_cat.currentText(), self.m_find.text().strip().lower()
            for i in range(self.m_list.count()):
                it = self.m_list.item(i)
                n = it.data(Qt.UserRole)
                it.setHidden(not ((cat == "All" or marks.CATS.get(n) == cat) and (not q or q in n or q in marks.CATS.get(n, "").lower())))
        self.m_cat.currentIndexChanged.connect(filter_marks)
        self.m_find.textChanged.connect(filter_marks)
        self.m_list.itemClicked.connect(lambda it: self.set("symbol", "mark", value=it.data(Qt.UserRole), group="mark") or self.set("symbol", "kind", value="mark", group="mark"))
        ml.addWidget(self.m_list)
        ml.addWidget(QLabel(f"{len(marks.MARKS)} original shapes made for Digonto Logo."))
        self.sym_stack.addWidget(mw)
        # monogram
        gw = QWidget()
        gl = QVBoxLayout(gw)
        gl.setContentsMargins(0, 6, 0, 0)
        self.e_letters = QLineEdit()
        self.e_letters.setMaxLength(3)
        self.e_letters.setPlaceholderText("empty = first letters of the name")
        self.e_letters.textChanged.connect(lambda t: self.set("symbol", "letters", value=t, group="letters"))
        gl.addLayout(self.row("Letters", self.e_letters))
        gl.addWidget(QLabel("Initials use the bold name font."))
        gl.addStretch(1)
        self.sym_stack.addWidget(gw)
        cw = QWidget()
        cl = QVBoxLayout(cw)
        cl.setContentsMargins(0, 6, 0, 0)
        imp = QPushButton("Choose a file: SVG, PNG or JPG ...")
        imp.setStyleSheet("QPushButton{background:qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF6F8E, stop:1 #FFB05A); color:#2A1241; border:0; border-radius:6px; padding:9px 18px; font-weight:600;}"
                          "QPushButton:hover{background:#A82E4E;}")
        imp.clicked.connect(self.import_symbol)
        cl.addWidget(imp)
        self.l_custom = QLabel("Nothing chosen yet.")
        self.l_custom.setWordWrap(True)
        self.l_custom.setStyleSheet("color:#5B5278;")
        cl.addWidget(self.l_custom)
        self.k_keep = QCheckBox("Keep the colors of the SVG")
        self.k_keep.toggled.connect(lambda b: self.set("symbol", "keep", value=b))
        cl.addWidget(self.k_keep)
        self.k_inv = QCheckBox("Picture: swap shape and background")
        self.k_inv.toggled.connect(lambda b: self.retrace(invert=b))
        cl.addWidget(self.k_inv)
        self.s_thr = self.slider(10, 90, lambda x: self.retrace(threshold=x / 100), "thr")
        self.s_thr.setValue(50)
        cl.addLayout(self.row("Detail", self.s_thr))
        note = QLabel("An SVG keeps its shapes as vectors. A PNG or JPG is traced into one clean shape in your main color "
                      "(best with a dark symbol on a plain light background). Use only artwork you have the rights to.")
        note.setWordWrap(True)
        note.setStyleSheet("color:#6E6475; font-size:11px;")
        cl.addWidget(note)
        cl.addStretch(1)
        self.sym_stack.addWidget(cw)
        self.sym_stack.addWidget(QWidget())
        v.addWidget(self.sym_stack)
        v.addWidget(heading("Container"))
        self.c_cont = self.combo([("none", "None")] + [(c, c.capitalize()) for c in marks.CONTAINERS], lambda k: self.set("symbol", "container", value=k))
        v.addLayout(self.row("Shape", self.c_cont))
        self.c_cmode = self.combo(compose.CMODES, lambda k: self.set("symbol", "cmode", value=k))
        v.addLayout(self.row("Look", self.c_cmode))
        self.s_size = self.slider(50, 170, lambda x: self.set("symbol", "scale", value=x / 100, group="sscale"), "sscale")
        v.addLayout(self.row("Size", self.s_size))
        self.k_grad = QCheckBox("Gradient from main to second color")
        self.k_grad.toggled.connect(lambda b: self.set("symbol", "grad", value=b))
        v.addWidget(self.k_grad)
        self.k_split = QCheckBox("Two-tone symbol (diagonal split, no container)")
        self.k_split.toggled.connect(lambda b: self.set("symbol", "split", value=b))
        v.addWidget(self.k_split)
        v.addStretch(1)

    def fill_icons(self):
        q = self.i_search.text().strip()
        names = icons.search(q, 150) if q else (self.win.suggested_icons() or icons.search("", 150))
        self.i_list.clear()
        col = self.spec["colors"]["primary"]
        for n in names[:150]:
            def draw(p, size, n=n):
                path = icons.path(n, self.spec["symbol"].get("iw", "fill"))
                r = path.boundingRect()
                k = (size * 0.92) / max(r.width(), r.height(), 1)
                p.translate(size / 2, size / 2)
                p.scale(k, k)
                p.translate(-r.center().x(), -r.center().y())
                p.fillPath(path, QColor("#1A2B23"))
            it = QListWidgetItem(glyph_icon(draw, 44), "")
            it.setData(Qt.UserRole, n)
            it.setToolTip(n.replace("-", " "))
            self.i_list.addItem(it)

    # ---- tab: layout
    def build_layout_tab(self):
        v = self.scroll_tab("Layout")
        v.addWidget(heading("Arrangement"))
        self.lay_views = {}
        g = QGridLayout()
        g.setSpacing(8)
        for i, (k, label) in enumerate(compose.LAYOUTS):
            lv = LogoView(None, margin=0.12)
            lv.setFixedSize(150, 94)
            lv.setCursor(Qt.PointingHandCursor)
            lv.mousePressEvent = lambda e, k=k: self.set("layout", value=k)
            cap = QLabel(label)
            cap.setStyleSheet("color:#5B5278; font-size:11px;")
            self.lay_views[k] = lv
            box = QVBoxLayout()
            box.setSpacing(2)
            box.addWidget(lv)
            box.addWidget(cap)
            g.addLayout(box, i // 2, i % 2)
        v.addLayout(g)
        v.addWidget(heading("Details"))
        self.s_gap = self.slider(30, 220, lambda x: self.set("gap", value=x / 100, group="gap"), "gap")
        v.addLayout(self.row("Spacing", self.s_gap))
        self.k_div = QCheckBox("Thin line between symbol and name")
        self.k_div.toggled.connect(lambda b: self.set("divider", value=b))
        v.addWidget(self.k_div)
        self.c_deco = self.combo([("none", "None"), ("bar", "Short bar"), ("underline", "Underline"), ("lines", "Lines beside tagline")], lambda k: self.set("deco", value=k))
        v.addLayout(self.row("Wordmark", self.c_deco))
        self.k_fill = QCheckBox("Emblem: filled disc (off = outline)")
        self.k_fill.toggled.connect(lambda b: self.set("fill", value=b))
        v.addWidget(self.k_fill)
        v.addStretch(1)

    # ---- tab: colors
    def build_color_tab(self):
        v = self.scroll_tab("Colors")
        v.addWidget(heading("Palettes"))
        g = QGridLayout()
        g.setSpacing(6)
        for i, p in enumerate(palettes.PALETTES):
            b = QPushButton()
            b.setIcon(swatch_icon(p, 40))
            b.setIconSize(QSize(40, 40))
            b.setFixedSize(52, 52)
            b.setToolTip(p["name"])
            b.setStyleSheet("QPushButton{padding:0; border-radius:8px;}")
            b.clicked.connect(lambda _=False, p=p: self.apply_palette(p))
            g.addWidget(b, i // 6, i % 6)
        v.addLayout(g)
        v.addWidget(heading("Your own colors"))
        self.cb = {}
        for key, label in (("primary", "Main"), ("secondary", "Second"), ("text", "Text"), ("bg", "Background")):
            b = ColorBtn("#000000", lambda c, key=key: self.set("colors", key, value=c, group="col-" + key))
            self.cb[key] = b
            r = QHBoxLayout()
            r.addWidget(QLabel(label))
            r.addStretch()
            r.addWidget(b)
            v.addLayout(r)
        r = QHBoxLayout()
        sw = QPushButton("Swap main / second")
        sw.clicked.connect(self.swap_colors)
        dk = QPushButton("Dark version")
        dk.clicked.connect(self.dark_version)
        r.addWidget(sw)
        r.addWidget(dk)
        v.addLayout(r)
        self.contrast_lbl = QLabel("")
        self.contrast_lbl.setWordWrap(True)
        self.contrast_lbl.setStyleSheet("color:#5B5278; font-size:12px; background:#EDE6F4; border-radius:8px; padding:8px;")
        v.addWidget(self.contrast_lbl)
        v.addStretch(1)

    def apply_palette(self, p):
        self.push("palette")
        self.spec["colors"] = ideas.colors_of(p)
        self.spec["palette"] = p["id"]
        self.sync_colors()
        self.schedule()

    def swap_colors(self):
        self.push("swap")
        c = self.spec["colors"]
        c["primary"], c["secondary"] = c["secondary"], c["primary"]
        self.sync_colors()
        self.schedule()

    def dark_version(self):
        self.push("dark")
        self.spec["colors"] = ideas.dark_variant(self.spec["colors"])
        self.sync_colors()
        self.schedule()

    def sync_colors(self):
        for k, b in self.cb.items():
            b.set(self.spec["colors"][k])

    # ---- tab: type
    def build_type_tab(self):
        v = self.scroll_tab("Fonts")
        v.addWidget(heading("Name font"))
        self.c_cat = self.combo([("all", "All fonts")] + textkit.CATS, lambda k: self.fill_fonts())
        v.addLayout(self.row("Group", self.c_cat))
        self.f_list = QListWidget()
        self.f_list.setMinimumHeight(250)
        self.f_list.itemClicked.connect(self.pick_font)
        v.addWidget(self.f_list)
        self.k_bold = QCheckBox("Bold")
        self.k_bold.toggled.connect(lambda b: self.set("font", "bold", value=b))
        v.addWidget(self.k_bold)
        self.s_track = self.slider(-5, 40, lambda x: self.set("font", "track", value=x / 100, group="track"), "track")
        v.addLayout(self.row("Letter space", self.s_track))
        self.s_nsize = self.slider(50, 160, lambda x: self.set("font", "size", value=x / 100, group="nsize"), "nsize")
        v.addLayout(self.row("Name size", self.s_nsize))
        v.addWidget(heading("Tagline font"))
        self.c_tf = QComboBox()
        for f in textkit.FONTS:
            self.c_tf.addItem(f["name"], f["id"])
        self.c_tf.currentIndexChanged.connect(lambda _: self.set("tfont", "id", value=self.c_tf.currentData()) if not self._busy else None)
        v.addWidget(self.c_tf)
        self.k_tbold = QCheckBox("Bold")
        self.k_tbold.toggled.connect(lambda b: self.set("tfont", "bold", value=b))
        v.addWidget(self.k_tbold)
        self.s_ttrack = self.slider(-5, 60, lambda x: self.set("tfont", "track", value=x / 100, group="ttrack"), "ttrack")
        v.addLayout(self.row("Letter space", self.s_ttrack))
        self.s_tsize = self.slider(50, 200, lambda x: self.set("tfont", "scale", value=x / 100, group="tsize"), "tsize")
        v.addLayout(self.row("Tagline size", self.s_tsize))
        self.k_fit = QCheckBox("Stretch tagline to the width of the name")
        self.k_fit.toggled.connect(lambda b: self.set("tfont", "fit", value=b))
        v.addWidget(self.k_fit)
        lic = QLabel("All fonts are open source (SIL Open Font License): free for any use.")
        lic.setStyleSheet("color:#6E6475; font-size:11px;")
        v.addWidget(lic)
        v.addStretch(1)
        self.fill_fonts()

    def fill_fonts(self):
        cat = self.c_cat.currentData()
        self.f_list.clear()
        for f in textkit.FONTS:
            if cat in ("all", None) or f["cat"] == cat:
                it = QListWidgetItem(f["name"])
                it.setData(Qt.UserRole, f["id"])
                ft = QFont(textkit.family(f["id"]))
                ft.setPixelSize(19)
                it.setFont(ft)
                self.f_list.addItem(it)
                if f["id"] == self.spec["font"]["id"]:
                    self.f_list.setCurrentItem(it)

    def pick_font(self, it):
        fid = it.data(Qt.UserRole)
        self.push("font")
        self.spec["font"]["id"] = fid
        if not textkit.has_bold(fid):
            self.spec["font"]["bold"] = False
        self.sync()
        self.schedule()

    # ---- center
    def center(self):
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(18, 12, 18, 12)
        bar = QHBoxLayout()
        self.b_undo = QPushButton("Undo")
        self.b_undo.setToolTip("Ctrl+Z")
        self.b_undo.clicked.connect(self.do_undo)
        self.b_redo = QPushButton("Redo")
        self.b_redo.clicked.connect(self.do_redo)
        bar.addWidget(self.b_undo)
        bar.addWidget(self.b_redo)
        bar.addSpacing(14)
        self.bg_combo = QComboBox()
        for k, label in (("design", "Design background"), ("white", "White"), ("black", "Black"), ("checker", "Transparent"), ("image", "My picture ...")):
            self.bg_combo.addItem(label, k)
        self.bg_combo.currentIndexChanged.connect(lambda _: self.set_bg(self.bg_combo.currentData()))
        bar.addWidget(self.bg_combo)
        self.s_dim = QSlider(Qt.Horizontal)
        self.s_dim.setRange(0, 85)
        self.s_dim.setFixedWidth(70)
        self.s_dim.setToolTip("Darken the picture")
        self.s_dim.setEnabled(False)
        self.s_dim.valueChanged.connect(lambda _: self.refresh())
        bar.addWidget(self.s_dim)
        bar.addStretch()
        self.b_fav = QPushButton("♡ Favorite")
        self.b_fav.clicked.connect(self.fav)
        bar.addWidget(self.b_fav)
        self.b_var = QPushButton("Variations")
        self.b_var.clicked.connect(lambda: self.win.show_variations(self.spec))
        bar.addWidget(self.b_var)
        ex = QPushButton("Export  →")
        ex.setObjectName("primary")
        ex.clicked.connect(self.win.go_export)
        bar.addWidget(ex)
        v.addLayout(bar)
        self.view = LogoView(None, margin=0.16, radius=14)
        self.view.setMinimumHeight(300)
        v.addWidget(self.view, 1)
        v.addWidget(heading("In use"))
        r = QHBoxLayout()
        r.setSpacing(12)
        self.app_views = []
        for kind, (w_, h_) in (("icon", (72, 72)), ("round", (72, 72)), ("horizontal", (130, 72)), ("stacked", (100, 72)), ("black", (130, 72))):
            lv = LogoView(None, margin=0.2 if kind in ("icon", "round") else 0.15)
            lv.setFixedSize(w_, h_)
            lv.kind = kind
            r.addWidget(lv)
            self.app_views.append(lv)
        r.addStretch()
        v.addLayout(r)
        return w

    def import_symbol(self):
        f, _ = QFileDialog.getOpenFileName(self, "Choose your symbol", "", "Symbols (*.svg *.png *.jpg *.jpeg *.webp *.bmp)")
        if f:
            self.load_symbol(f)

    def load_symbol(self, f, invert=False, threshold=0.5):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            c = custom.from_file(f, invert, threshold)
        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.warning(self, APP_NAME, f"This file could not be used:\n{e}")
            return
        QApplication.restoreOverrideCursor()
        if not c["parts"]:
            QMessageBox.information(self, APP_NAME, "No shape found in this file. For a picture, use a dark symbol on a plain light background "
                                                    "(or a PNG with transparent background).")
            return
        c.update(src=f, invert=invert, threshold=threshold)
        self.push("custom")
        self.spec["symbol"]["custom"] = c
        self.spec["symbol"]["kind"] = "custom"
        self.spec["symbol"]["keep"] = bool(c["colors"])
        self.sync()
        self.schedule()

    def retrace(self, invert=None, threshold=None):
        if self._busy:
            return
        cu = self.spec["symbol"].get("custom") or {}
        if cu.get("kind") != "image" or not os.path.isfile(cu.get("src", "")):
            return
        self._retrace = (cu["src"], cu.get("invert", False) if invert is None else invert, cu.get("threshold", 0.5) if threshold is None else threshold)
        if not hasattr(self, "_rt"):
            self._rt = QTimer(self, singleShot=True, interval=350, timeout=lambda: self.load_symbol(*self._retrace))
        self._rt.start()

    def set_bg(self, k):
        if k == "image":
            f, _ = QFileDialog.getOpenFileName(self, "Choose a background picture", "", "Pictures (*.png *.jpg *.jpeg *.webp *.bmp)")
            img = QImage(f) if f else QImage()
            if img.isNull():
                self.bg_combo.blockSignals(True)
                self.bg_combo.setCurrentIndex(self.bg_combo.findData(self.bg_mode))
                self.bg_combo.blockSignals(False)
                return
            self.bg_image, self.bg_image_path = img, f
        self.bg_mode = k
        self.s_dim.setEnabled(k == "image")
        self.refresh()

    bg_image, bg_image_path = None, ""

    def use_bg_image(self, path, dim=0):
        self.bg_image, self.bg_image_path = QImage(path), path
        self.s_dim.setValue(dim)
        self.bg_combo.blockSignals(True)
        self.bg_combo.setCurrentIndex(self.bg_combo.findData("image"))
        self.bg_combo.blockSignals(False)
        self.bg_mode = "image"
        self.s_dim.setEnabled(True)
        self.refresh()

    bg_mode = "design"

    def fav(self):
        self.win.toggle_fav(copy.deepcopy(self.spec), True)
        self.b_fav.setText("♥ Saved")

    # ---- sync + refresh
    def sync(self):
        s = self.spec
        self._busy = True
        try:
            self.e_name.setText(s["name"])
            self.e_tag.setText(s["tagline"])
            for c, v in ((self.c_case, s["font"]["case"]), (self.c_tcase, s["tfont"]["case"]), (self.c_two, s["font"]["two"]),
                         (self.c_nrole, s["name_role"]), (self.c_trole, s["tag_role"]), (self.c_iw, s["symbol"]["iw"]),
                         (self.c_cont, s["symbol"]["container"]), (self.c_cmode, s["symbol"]["cmode"]), (self.c_deco, s["deco"])):
                i = c.findData(v)
                c.setCurrentIndex(max(0, i))
            for k, b in self.kind_btns.items():
                b.setChecked(k == s["symbol"]["kind"])
            self.sym_stack.setCurrentIndex({"icon": 0, "mark": 1, "monogram": 2, "custom": 3, "none": 4}.get(s["symbol"]["kind"], 4))
            cu = s["symbol"].get("custom") or {}
            self.l_custom.setText((cu.get("name") or "Nothing chosen yet.") + (f"  ({len(cu.get('parts', []))} shapes)" if cu.get("parts") else ""))
            self.k_keep.setChecked(bool(s["symbol"].get("keep")))
            self.k_keep.setEnabled(bool(cu.get("colors")))
            self.k_inv.setChecked(bool(cu.get("invert")))
            self.k_inv.setEnabled(cu.get("kind") == "image")
            self.s_thr.setEnabled(cu.get("kind") == "image")
            self.s_thr.setValue(int(cu.get("threshold", 0.5) * 100))
            self.k_split.setChecked(bool(s["symbol"].get("split")))
            self.e_letters.setText(s["symbol"].get("letters", ""))
            self.s_size.setValue(int(s["symbol"]["scale"] * 100))
            self.k_grad.setChecked(bool(s["symbol"]["grad"]))
            self.s_gap.setValue(int(s["gap"] * 100))
            self.k_div.setChecked(bool(s["divider"]))
            self.k_fill.setChecked(bool(s["fill"]))
            self.sync_colors()
            self.k_bold.setChecked(bool(s["font"]["bold"]))
            self.k_bold.setEnabled(textkit.has_bold(s["font"]["id"]))
            self.s_track.setValue(int(s["font"]["track"] * 100))
            self.s_nsize.setValue(int(s["font"].get("size", 1.0) * 100))
            i = self.c_tf.findData(s["tfont"]["id"])
            self.c_tf.setCurrentIndex(max(0, i))
            self.k_tbold.setChecked(bool(s["tfont"]["bold"]))
            self.k_tbold.setEnabled(textkit.has_bold(s["tfont"]["id"]))
            self.s_ttrack.setValue(int(s["tfont"]["track"] * 100))
            self.s_tsize.setValue(int(s["tfont"].get("scale", 1.0) * 100))
            self.k_fit.setChecked(bool(s["tfont"].get("fit", True)))
            for it in range(self.f_list.count()):
                item = self.f_list.item(it)
                if item.data(Qt.UserRole) == s["font"]["id"]:
                    self.f_list.setCurrentItem(item)
            self.b_fav.setText("♡ Favorite")
        finally:
            self._busy = False

    def refresh(self):
        s = self.spec
        mode = self.bg_mode
        self.view.checker = mode == "checker"
        bg = {"design": None, "white": "#FFFFFF", "black": "#000000", "checker": None, "image": None}[mode]
        self.view.bg_image = self.bg_image if mode == "image" else None
        self.view.dim = self.s_dim.value()
        self.view.set_spec(s, bg)
        for k, lv in self.lay_views.items():
            t = copy.deepcopy(s)
            t["layout"] = k
            lv.set_spec(t, "#FFFFFF" if palettes.luminance(s["colors"]["bg"]) >= 0.4 else s["colors"]["bg"])
            lv.setStyleSheet("")
        for lv in self.app_views:
            if lv.kind == "icon":
                lv.set_spec(kit.variant(s, "icon"), s["colors"]["bg"])
            elif lv.kind == "round":
                lv.set_spec(kit.variant(s, "icon"), s["colors"]["bg"])
            elif lv.kind == "black":
                lv.set_spec(kit.variant(s, "black"), "#FFFFFF")
            else:
                lv.set_spec(kit.variant(s, lv.kind), s["colors"]["bg"])
            lv.radius = 60 if lv.kind == "round" else 10
            lv.update()
        c = s["colors"]
        ratio = palettes.contrast(c["primary"], c["bg"])
        self.contrast_lbl.setText(f"Contrast of the main color on the background: {ratio:.1f}:1 - " + ("good." if ratio >= 3 else "low. Make the main color darker or the background lighter."))
        self.b_undo.setEnabled(bool(self.undo))
        self.b_redo.setEnabled(bool(self.redo))
        self.win.dirty = True
        if self.sym_stack.currentIndex() == 0 and self.i_list.count() == 0:
            self.fill_icons()


class ExportPage(QWidget):
    def __init__(self, win):
        super().__init__()
        self.win = win
        h = QHBoxLayout(self)
        h.setContentsMargins(30, 20, 30, 20)
        h.setSpacing(30)
        left = QVBoxLayout()
        t = QLabel("Export")
        t.setStyleSheet("font-size:24px; font-weight:700; color:#1B1040;")
        left.addWidget(t)
        left.addWidget(heading("Complete brand kit"))
        info = QLabel("One folder with everything a business needs. Takes a few seconds.")
        info.setStyleSheet("color:#5B5278;")
        left.addWidget(info)
        self.k = {}
        for key, label in (("logos", "Logo files: SVG, PNG, PDF, EPS, AI (8 versions)"), ("icons", "Favicon and app icons: ICO, ICNS, PNG"),
                           ("social", "Social images: avatar, cover, Open Graph, post"), ("guide", "Brand guide PDF: colors, fonts, clear space, don'ts")):
            c = QCheckBox(label)
            c.setChecked(True)
            self.k[key] = c
            left.addWidget(c)
        self.zip = QCheckBox("Also pack it into one .zip")
        left.addWidget(self.zip)
        self.folder = QLineEdit(os.path.expanduser("~/Documents") if os.path.isdir(os.path.expanduser("~/Documents")) else os.path.expanduser("~"))
        fr = QHBoxLayout()
        fr.addWidget(self.folder, 1)
        b = QPushButton("Choose ...")
        b.clicked.connect(self.pick)
        fr.addWidget(b)
        left.addWidget(heading("Save in"))
        left.addLayout(fr)
        self.go = QPushButton("Create brand kit")
        self.go.setObjectName("primary")
        self.go.clicked.connect(self.make)
        left.addWidget(self.go)
        self.pb = QProgressBar()
        self.pb.setVisible(False)
        left.addWidget(self.pb)
        self.msg = QLabel("")
        self.msg.setWordWrap(True)
        self.msg.setStyleSheet("color:#8A2150;")
        left.addWidget(self.msg)
        left.addWidget(heading("Just this logo"))
        r = QHBoxLayout()
        pic = QPushButton("On my picture")
        pic.setToolTip("PNG of the logo placed on the background picture chosen in step 3")
        pic.clicked.connect(self.on_picture)
        r.addWidget(pic)
        for f in ("SVG", "PNG", "PDF", "EPS", "AI", "ICO"):
            b = QPushButton(f)
            b.clicked.connect(lambda _=False, f=f: self.single(f.lower()))
            r.addWidget(b)
        left.addLayout(r)
        r2 = QHBoxLayout()
        r2.addWidget(QLabel("PNG width"))
        self.px = QSpinBox()
        self.px.setRange(100, 12000)
        self.px.setValue(2400)
        self.px.setSuffix(" px")
        r2.addWidget(self.px)
        self.trans = QCheckBox("Transparent")
        self.trans.setChecked(True)
        r2.addWidget(self.trans)
        r2.addStretch()
        left.addLayout(r2)
        left.addStretch(1)
        lw = QWidget()
        lw.setLayout(left)
        lw.setFixedWidth(430)
        h.addWidget(lw)
        right = QVBoxLayout()
        rt = QLabel("What you get")
        rt.setStyleSheet("font-size:14px; font-weight:600; color:#5B5278;")
        right.addWidget(rt)
        g = QGridLayout()
        g.setSpacing(12)
        self.tiles = []
        for i, (k, label) in enumerate(kit.VARIANTS):
            lv = LogoView(None, margin=0.14)
            lv.setMinimumSize(190, 128)
            lv.kind = k
            cap = QLabel(label)
            cap.setStyleSheet("color:#5B5278; font-size:11px;")
            box = QVBoxLayout()
            box.setSpacing(2)
            box.addWidget(lv, 1)
            box.addWidget(cap)
            g.addLayout(box, i // 3, i % 3)
            self.tiles.append(lv)
        right.addLayout(g, 1)
        rw = QWidget()
        rw.setLayout(right)
        h.addWidget(rw, 1)

    def pick(self):
        d = QFileDialog.getExistingDirectory(self, "Save the brand kit in", self.folder.text())
        if d:
            self.folder.setText(d)

    def refresh(self):
        s = self.win.editor.spec
        for lv in self.tiles:
            v = kit.variant(s, lv.kind)
            lv.set_spec(v, kit.bg_of(s, lv.kind) or v["colors"]["bg"])

    def make(self):
        parts = {k for k, c in self.k.items() if c.isChecked()}
        folder = self.folder.text().strip()
        if not os.path.isdir(folder):
            QMessageBox.information(self, APP_NAME, "Please choose an existing folder.")
            return
        self.go.setEnabled(False)
        self.pb.setVisible(True)
        self.pb.setValue(0)
        self.msg.setText("")
        QApplication.processEvents()

        def prog(a, b, label):
            self.pb.setMaximum(b)
            self.pb.setValue(a)
            self.msg.setText(label + " ...")
            QApplication.processEvents()
        try:
            out = kit.build_kit(self.win.editor.spec, folder, parts, self.zip.isChecked(), prog, self.win.brief_dict())
        except OSError as e:
            QMessageBox.warning(self, APP_NAME, f"Could not create the kit:\n{e}")
            self.go.setEnabled(True)
            return
        self.go.setEnabled(True)
        ed = self.win.editor
        if ed.bg_image is not None and os.path.isdir(out):
            try:
                os.makedirs(os.path.join(out, "logo"), exist_ok=True)
                export.on_image(compose.build(ed.spec), ed.bg_image, 1920, 1080, ed.s_dim.value()).save(os.path.join(out, "logo", "logo-on-my-picture.png"))
            except OSError:
                pass
        self.msg.setText(f"Done. Saved in\n{out}")
        self.win.statusBar().showMessage("Brand kit created", 6000)
        self.win.save_project(quiet=True, near=out if os.path.isdir(out) else None)

    def on_picture(self, folder=None):
        ed = self.win.editor
        if ed.bg_image is None:
            QMessageBox.information(self, APP_NAME, "In step 3, choose Background > My picture ... first.")
            return
        sc = compose.build(ed.spec)
        img = export.on_image(sc, ed.bg_image, 1920, 1080, ed.s_dim.value())
        name = kit.slug(ed.spec["name"]) + "-on-picture.png"
        path, _ = QFileDialog.getSaveFileName(self, "Save PNG", os.path.join(self.folder.text(), name), "PNG (*.png)")
        if path:
            img.save(path if path.lower().endswith(".png") else path + ".png")
            self.win.statusBar().showMessage(f"Saved {path}", 6000)

    def single(self, fmt):
        s = self.win.editor.spec
        sc = compose.build(s)
        name = kit.slug(s["name"])
        path, _ = QFileDialog.getSaveFileName(self, f"Save {fmt.upper()}", os.path.join(self.folder.text(), f"{name}.{fmt}"), f"{fmt.upper()} (*.{fmt})")
        if not path:
            return
        if not path.lower().endswith("." + fmt):
            path += "." + fmt
        bg = None if (self.trans.isChecked() or fmt in ("pdf", "eps", "ai")) else s["colors"]["bg"]
        try:
            if fmt == "svg":
                open(path, "w", encoding="utf-8").write(export.to_svg(sc, bg, 0.08, s["name"]))
            elif fmt == "png":
                export.to_image(sc, self.px.value(), bg).save(path)
            elif fmt in ("pdf", "ai"):
                export.to_pdf(sc, path, None, 0.08, s["name"])
            elif fmt == "eps":
                export.to_eps(sc, path, None, 0.08, s["name"])
            else:
                ic = compose.build(kit.variant(s, "icon"))
                export.to_ico(path, [export.square_image(ic, z, None, 0.86) for z in (16, 32, 48, 64, 128, 256)])
        except OSError as e:
            QMessageBox.warning(self, APP_NAME, f"Could not save:\n{e}")
            return
        self.win.statusBar().showMessage(f"Saved {path}", 6000)


# ====================================================================== window
class Main(QMainWindow):
    def __init__(self, path=None):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.icon = ui.app_icon(HERE, SLUG)
        self.setWindowIcon(self.icon)
        ui.fit_window(self, 1320, 860)
        self.setMinimumSize(640, 440)
        self.setStyleSheet(QSS)
        self.favs, self.ideas_all, self.seed, self.brief = [], [], 0, {}
        self.project_path, self.dirty = None, False
        self.build_menu()
        self.stack = QStackedWidget()
        self.brief_page = BriefPage(self)
        self.ideas_page = IdeasPage(self)
        self.editor = Editor(self)
        self.export_page = ExportPage(self)
        for p in (self.brief_page, self.ideas_page, self.editor, self.export_page):
            self.stack.addWidget(p)
        self.steps = []
        bar = QWidget()
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(0, 0, 12, 0)
        bl.setSpacing(4)
        for i, name in enumerate(("1  Brief", "2  Ideas", "3  Customize", "4  Export")):
            b = QPushButton(name)
            b.setCheckable(True)
            b.setStyleSheet("QPushButton{color:white; background:transparent; border:0; border-bottom:3px solid transparent; border-radius:0; padding:8px 12px; font-weight:600;}"
                            "QPushButton:hover{background:rgba(255,255,255,0.12);}"
                            "QPushButton:checked{background:rgba(255,255,255,0.0); border-bottom:3px solid white;}")
            b.clicked.connect(lambda _=False, i=i: self.goto(i))
            self.steps.append(b)
            bl.addWidget(b)
        hd = ui.make_header(APP_NAME, "Make a complete logo and brand in minutes", self.icon, self.about, bar)
        self.rail = ui.Rail(
            [("new", "new", "New logo (Ctrl+N)", self.new),
             ("open", "open", "Open project (Ctrl+O)", self.open_dialog),
             ("save", "save", "Save project (Ctrl+S)", self.save_project),
             ("export", "export", "Export the logo and brand kit (Ctrl+E)", self.go_export),
             None,
             ("ideas", "wand", "Ideas (step 2)", lambda: self.goto(1)),
             ("customize", "pen", "Customize (step 3)", lambda: self.goto(2))],
            [("settings", "settings", "Settings and help", self.rail_settings)])
        body = QWidget()
        bh = QHBoxLayout(body)
        bh.setContentsMargins(0, 0, 0, 0)
        bh.setSpacing(0)
        bh.addWidget(self.rail)
        bh.addWidget(self.stack, 1)
        ui.wrap_with_header(self, hd, body)
        self.goto(0)
        if path and os.path.isfile(path):
            self.open_project(path)

    def build_menu(self):
        mb = self.menuBar()
        fm = mb.addMenu("File")
        for text, sc, fn in (("New", "Ctrl+N", self.new), ("Open project ...", "Ctrl+O", self.open_dialog), ("Save project", "Ctrl+S", self.save_project),
                             ("Save project as ...", "Ctrl+Shift+S", lambda: self.save_project(as_new=True)), ("Close project", "Ctrl+W", self.new)):
            fm.addAction(QAction(text, self, shortcut=sc, triggered=fn))
        fm.addSeparator()
        fm.addAction(QAction("Export ...", self, shortcut="Ctrl+E", triggered=self.go_export))
        fm.addSeparator()
        fm.addAction(QAction("Exit", self, shortcut="Ctrl+Q", triggered=self.close))
        fm.addAction(QAction("Quit (force)", self, shortcut="Ctrl+Shift+Q", triggered=lambda: os._exit(0)))
        em = mb.addMenu("Edit")
        em.addAction(QAction("Undo", self, shortcut="Ctrl+Z", triggered=lambda: self.editor.do_undo()))
        _rd = QAction("Redo", self, triggered=lambda: self.editor.do_redo())
        _rd.setShortcuts(["Ctrl+Shift+Z", "Ctrl+Y"])
        em.addAction(_rd)
        vm = mb.addMenu("View")
        for i, n in enumerate(("Brief", "Ideas", "Customize", "Export")):
            vm.addAction(QAction(n, self, shortcut=f"Ctrl+{i + 1}", triggered=lambda _=False, i=i: self.goto(i)))
        hm = mb.addMenu("Help")
        hm.addAction(QAction("About Digonto Logo", self, triggered=self.about))

    def rail_settings(self):
        from PySide6.QtWidgets import QMenu
        m = QMenu(self)
        m.addAction("Save project as …", lambda: self.save_project(as_new=True))
        m.addSeparator()
        m.addAction("About Digonto Logo", self.about)
        b = self.rail.button("settings")
        m.exec(b.mapToGlobal(b.rect().topRight()))

    # ---- navigation
    def goto(self, i):
        if i >= 2 and not self.editor_ready():
            QMessageBox.information(self, APP_NAME, "Pick an idea first (step 2).")
            i = 1 if self.ideas_all else 0
        if i == 1 and not self.ideas_all:
            if self.brief_page.name.text().strip():
                self.make_ideas(self.brief_page.brief())
                return
            i = 0
        self.stack.setCurrentIndex(i)
        for k, b in enumerate(self.steps):
            b.setChecked(k == i)
        if i == 3:
            self.export_page.refresh()
        if i == 2:
            self.editor.refresh()

    def editor_ready(self):
        return bool(getattr(self, "_editor_loaded", False))

    def make_ideas(self, brief):
        self.brief = brief
        self.seed = 0
        self.ideas_all = ideas.generate(brief, 30, 0)
        self.ideas_page.filter = "all"
        for k, b in self.ideas_page.fbtns.items():
            b.setChecked(k == "all")
        self.ideas_page.show_specs(self.ideas_all, f"Ideas for {brief['name']}")
        self.goto(1)

    def more_ideas(self):
        self.seed += 1
        self.ideas_all = ideas.generate(self.brief, 30, self.seed)
        self.ideas_page.show_specs(self.ideas_all, f"Ideas for {self.brief['name']}")

    def show_variations(self, spec):
        self.ideas_page.show_specs(ideas.variations(spec, 12, int(time.time()) % 1000), "Other takes on this idea", variations=True)
        self.stack.setCurrentIndex(1)
        for k, b in enumerate(self.steps):
            b.setChecked(k == 1)

    def back_to_ideas(self):
        self.ideas_page.show_specs(self.ideas_all, f"Ideas for {self.brief.get('name', '')}")

    def open_editor(self, spec):
        self._editor_loaded = True
        self.editor.load(spec)
        self.editor.fill_icons()
        self.goto(2)

    def go_export(self):
        if not self.editor_ready():
            QMessageBox.information(self, APP_NAME, "Pick an idea first.")
            return
        self.goto(3)

    def suggested_icons(self):
        try:
            return ideas.icon_pool(self.brief or {"name": self.editor.spec["name"], "desc": ""}, ideas.detect(self.brief or {}))[:150]
        except Exception:
            return []

    def toggle_fav(self, spec, on):
        key = json.dumps(spec, sort_keys=True, default=str)
        self.favs = [f for f in self.favs if json.dumps(f, sort_keys=True, default=str) != key]
        if on:
            self.favs.append(copy.deepcopy(spec))
        self.dirty = True

    def brief_dict(self):
        return self.brief or self.brief_page.brief()

    # ---- projects (.dlgo; older .ptlogo files still open)
    def project(self):
        return {"app": SLUG, "version": 2, "brief": self.brief or self.brief_page.brief(), "spec": self.editor.spec if self.editor_ready() else None,
                "favorites": self.favs, "bg_image": self.editor.bg_image_path if self.editor.bg_image is not None else "",
                "dim": self.editor.s_dim.value()}

    def maybe_save(self):
        """True when it is fine to leave this project (asks to save when it has changes)"""
        if not self.dirty or not (self.editor_ready() or self.favs):
            return True
        r = QMessageBox.question(self, APP_NAME, "Save changes to this project?", QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
        if r == QMessageBox.Save:
            self.save_project()
            return not self.dirty
        return r == QMessageBox.Discard

    def new(self):
        if not self.maybe_save():
            return
        self.dirty = False
        self.project_path = None
        self.favs, self.ideas_all, self._editor_loaded = [], [], False
        self.brief_page.set_brief({})
        self.goto(0)

    def open_dialog(self):
        p, _ = QFileDialog.getOpenFileName(self, "Open project", "", "Digonto Logo project (*.dlgo *.ptlogo)")
        if p and self.maybe_save():
            self.open_project(p)

    def open_project(self, path):
        try:
            with open(path, encoding="utf-8") as f:
                d = json.load(f)
            if d.get("version") != 2:
                raise ValueError("this file was made by the older Digonto Brand program")
            self.brief = d.get("brief") or {}
            self.brief_page.set_brief(self.brief)
            self.favs = d.get("favorites", [])
            if self.brief.get("name"):
                self.ideas_all = ideas.generate(self.brief, 30, 0)
                self.ideas_page.show_specs(self.ideas_all, f"Ideas for {self.brief['name']}")
            if d.get("spec"):
                self.open_editor(d["spec"])
                bgp = d.get("bg_image") or ""
                if bgp and os.path.isfile(bgp):
                    self.editor.use_bg_image(bgp, int(d.get("dim", 0)))
            else:
                self.goto(0)
        except (OSError, ValueError, KeyError) as e:
            QMessageBox.warning(self, APP_NAME, f"This project could not be opened:\n{e}")
            return
        self.project_path = path
        add_recent(path)
        QTimer.singleShot(400, lambda: setattr(self, "dirty", False))

    def save_project(self, as_new=False, quiet=False, near=None):
        path = self.project_path
        if as_new or not path:
            if quiet and near:
                path = os.path.join(near, kit.slug(self.editor.spec["name"]) + ".dlgo")
            else:
                start = (self.editor.spec["name"] if self.editor_ready() else "logo") + ".dlgo"
                path, _ = QFileDialog.getSaveFileName(self, "Save project", start, "Digonto Logo project (*.dlgo)")
                if path and not path.lower().endswith(".dlgo"):
                    path += ".dlgo"
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.project(), f)
        except OSError as e:
            QMessageBox.warning(self, APP_NAME, f"Could not save:\n{e}")
            return
        self.project_path = path
        self.dirty = False
        add_recent(path)
        self.statusBar().showMessage(f"Saved {path}", 5000)

    def closeEvent(self, ev):
        if not self.maybe_save():
            ev.ignore()
            return
        ev.accept()
        QApplication.instance().quit()
        QTimer.singleShot(300, lambda: os._exit(0))

    def about(self):
        QMessageBox.about(self, f"About {APP_NAME}",
                          f"<h3>{APP_NAME} {VERSION}</h3><p>Type your business name and what you do, pick from dozens of logo ideas, change "
                          "anything, then export a complete brand kit: logo files (SVG, PNG, PDF, EPS, AI), favicon and app icons, social images and a brand guide.</p>"
                          "<p>Icons: Phosphor Icons (MIT). Fonts: open-source Google Fonts (SIL OFL). Shapes: made for Digonto. "
                          "Everything is exported as outlines, so no font needs to be installed.</p>"
                          "<p>Built with Qt for Python (PySide6-Essentials).</p>")


def main():
    if "--version" in sys.argv:
        print(VERSION)
        return
    ui.mac_app_name(APP_NAME)
    app = QApplication(sys.argv)
    if ui.forward_to_running(SLUG, sys.argv[1:]):
        os._exit(0)
    ui.setup_app(app, APP_NAME, SLUG, ui.app_icon(HERE, SLUG))
    path = next((a for a in sys.argv[1:] if os.path.isfile(a)), None)
    w = Main(path)
    w.show()
    _extra = []

    def _new_window(p):
        x = Main(p)
        x.show()
        _extra.append(x)
        return x
    ui.serve_single(SLUG, w, _new_window)
    os._exit(app.exec())


if __name__ == "__main__":
    main()
