"""
SemiContact Pro — Landing Dashboard
Two-card launcher for CTLM and LTLM modes.
Fix 6: About & Contact button added to top-right of dashboard.
UI Refresh: Larger cards, improved scaling, more prominent Credits & Contact button.
"""

import math

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QApplication
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, pyqtProperty
from PyQt6.QtGui import (
    QPainter, QColor, QLinearGradient, QFont,
    QBrush, QPen, QPainterPath, QRadialGradient
)

from ui.about_dialog import AboutDialog


class ModeCard(QWidget):
    COLORS = {
        "ctlm": {"accent": QColor(0, 230, 255), "btn_text": "#00e5ff", "icon": "⬡"},
        "ltlm": {"accent": QColor(0, 255, 160), "btn_text": "#00ffa0", "icon": "⟶"},
    }

    def __init__(self, mode, title, subtitle, features, on_launch, parent=None):
        super().__init__(parent)
        self._mode       = mode
        self._glow_alpha = 0
        self._colors     = self.COLORS[mode]
        # Cards: wider than original (360→420) but height pulled back to a balanced 500
        self.setFixedSize(420, 500)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._build_ui(title, subtitle, features, on_launch)
        self._glow_anim = QPropertyAnimation(self, b"glow_alpha")
        self._glow_anim.setDuration(220)
        self._glow_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def _get_glow(self):    return self._glow_alpha
    def _set_glow(self, v): self._glow_alpha = v; self.update()
    glow_alpha = pyqtProperty(int, _get_glow, _set_glow)

    def _build_ui(self, title, subtitle, features, on_launch):
        layout = QVBoxLayout(self)
        # Padding: wider side margins (premium feel) but tighter top/bottom to fit reduced height
        layout.setContentsMargins(36, 28, 36, 26)
        layout.setSpacing(0)
        ch = self._colors["accent"].name()

        # Icon: 46pt — larger than original (42) but not oversized
        icon = QLabel(self._colors["icon"])
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setFont(QFont("Segoe UI Symbol", 46))
        icon.setStyleSheet(f"color:{ch};background:transparent;")
        layout.addWidget(icon)
        layout.addSpacing(12)

        # Card title: 19pt — upgraded from original 17, not as tall as 21
        t = QLabel(title)
        t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t.setFont(QFont("Segoe UI", 19, QFont.Weight.Bold))
        t.setStyleSheet(f"color:{ch};letter-spacing:2px;background:transparent;")
        layout.addWidget(t)
        layout.addSpacing(5)

        # ── CHANGE 5: Subtitle font size increased from 11 → 13
        s = QLabel(subtitle)
        s.setAlignment(Qt.AlignmentFlag.AlignCenter)
        s.setWordWrap(True)
        s.setStyleSheet("color:#3a7a8a;font-size:13px;letter-spacing:1px;background:transparent;")
        layout.addWidget(s)
        layout.addSpacing(16)

        div = QFrame(); div.setFrameShape(QFrame.Shape.HLine)
        div.setStyleSheet(f"background:{ch};border:none;max-height:1px;")
        layout.addWidget(div)
        layout.addSpacing(14)

        # ── CHANGE 6: Feature text increased from 12 → 13px, bullet icon slightly larger
        for feat in features:
            row = QHBoxLayout(); row.setSpacing(12)
            b = QLabel("◆"); b.setFixedWidth(14)
            b.setStyleSheet(f"color:{ch};font-size:8px;background:transparent;")
            row.addWidget(b)
            fl = QLabel(feat)
            fl.setStyleSheet("color:#7ab0c0;font-size:13px;background:transparent;")
            row.addWidget(fl); row.addStretch()
            layout.addLayout(row); layout.addSpacing(5)

        layout.addStretch()

        # Launch button: 46px — improved over original 44, not as tall as 52
        bc = self._colors["btn_text"]
        btn = QPushButton(f"  Launch {title.split()[0]}  ")
        btn.setFixedHeight(46)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton{{background:transparent;border:2px solid {bc};border-radius:10px;
                color:{bc};font-size:14px;font-weight:700;letter-spacing:2px;}}
            QPushButton:hover{{background:{bc};color:#000;}}
            QPushButton:pressed{{background:#005060;color:#000;}}
        """)
        btn.clicked.connect(on_launch)
        layout.addWidget(btn)

    def enterEvent(self, e): self._anim_glow(130); super().enterEvent(e)
    def leaveEvent(self, e): self._anim_glow(0);   super().leaveEvent(e)

    def _anim_glow(self, target):
        self._glow_anim.stop()
        self._glow_anim.setStartValue(self._glow_alpha)
        self._glow_anim.setEndValue(target)
        self._glow_anim.start()

    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        path = QPainterPath(); path.addRoundedRect(0, 0, w, h, 16, 16)
        bg = QLinearGradient(0, 0, 0, h)
        bg.setColorAt(0, QColor(14, 28, 42)); bg.setColorAt(1, QColor(9, 15, 24))
        p.fillPath(path, QBrush(bg))
        if self._glow_alpha > 0:
            a = self._colors["accent"]
            g = QRadialGradient(w/2, 0, w*0.9)
            g.setColorAt(0, QColor(a.red(), a.green(), a.blue(), self._glow_alpha//3))
            g.setColorAt(1, QColor(0,0,0,0)); p.fillPath(path, QBrush(g))
        a = self._colors["accent"]
        pen = QPen(QColor(a.red(), a.green(), a.blue(), min(80+self._glow_alpha,255)))
        pen.setWidth(1); p.setPen(pen); p.drawPath(path); p.end()


class DashBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._tick = 0
        t = QTimer(self); t.timeout.connect(self._step); t.start(50)

    def _step(self): self._tick += 1; self.update()

    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        bg = QLinearGradient(0,0,w,h)
        bg.setColorAt(0, QColor(6,10,16)); bg.setColorAt(0.5, QColor(8,14,22))
        bg.setColorAt(1, QColor(5,9,14)); p.fillRect(0,0,w,h,QBrush(bg))
        p.setPen(QPen(QColor(0,188,212,18)))
        for xi in range(0,w,40):
            for yi in range(0,h,40): p.drawPoint(xi,yi)
        by = int(h*0.5 + h*0.35*math.sin(self._tick*0.04))
        bm = QLinearGradient(0,by-80,0,by+80)
        bm.setColorAt(0,QColor(0,0,0,0)); bm.setColorAt(0.5,QColor(0,200,220,10))
        bm.setColorAt(1,QColor(0,0,0,0)); p.fillRect(0,by-80,w,160,QBrush(bm)); p.end()


class Dashboard(QMainWindow):
    def __init__(self, on_ctlm, on_ltlm):
        super().__init__()
        self._on_ctlm = on_ctlm; self._on_ltlm = on_ltlm
        self._setup_window(); self._build_ui(); self._fade_in()

    def _setup_window(self):
        self.setWindowTitle("SemiContact Pro — Workstation")
        # Window sized to hold 420×500 cards + 60px gap + all chrome without clipping
        self.setMinimumSize(1020, 740)
        self.resize(1160, 800)
        s = QApplication.primaryScreen().geometry()
        self.move((s.width()-self.width())//2,(s.height()-self.height())//2)

    def _build_ui(self):
        self.bg = DashBackground(); self.setCentralWidget(self.bg)
        root = QVBoxLayout(self.bg)
        root.setContentsMargins(64, 36, 64, 32)
        root.setSpacing(0)

        # ── Top row: About button ─────────────────────────────────────
        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.addStretch()

        # ── CHANGE 10: Credits & Contact button — larger, more prominent, better padding
        about_btn = QPushButton("  ✦  Credits & Contact  ")
        about_btn.setFixedHeight(36)
        about_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        about_btn.setStyleSheet("""
            QPushButton{
                background:#0d1e2e;
                border:1px solid #1e4a5a;
                border-radius:8px;
                color:#4a9aaa;
                font-size:12px;
                padding:0 20px;
                letter-spacing:0.8px;
            }
            QPushButton:hover{
                border-color:#00e5ff;
                color:#00e5ff;
                background:#0d2535;
            }
            QPushButton:pressed{background:#004a5a;}
        """)
        about_btn.clicked.connect(self._show_about)
        top_row.addWidget(about_btn)
        root.addLayout(top_row)
        root.addSpacing(10)

        badge = QLabel("SEMICONDUCTOR ANALYSIS WORKSTATION")
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet("color:#1e5a6a;font-size:12px;letter-spacing:5px;")
        root.addWidget(badge)
        root.addSpacing(4)

        title = QLabel("SemiContact Pro")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 36, QFont.Weight.Bold))
        title.setStyleSheet("color:#00e5ff;letter-spacing:4px;")
        root.addWidget(title)
        root.addSpacing(4)

        sub = QLabel("Select analysis mode to begin")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet("color:#3a7a8a;font-size:14px;letter-spacing:1px;")
        root.addWidget(sub)
        # Breathing room between header and cards — tighter than before to preserve footer
        root.addSpacing(36)

        # Card gap: 60px — wider than original 50, generous without wasting horizontal space
        cards = QHBoxLayout()
        cards.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cards.setSpacing(60)
        cards.addWidget(ModeCard("ctlm","CTLM MODE","Circular Transmission Line Method",
            ["Correction factor (CF) support","Live parameter extraction",
             "Multi-dataset analysis (up to 8)","Sheet resistance & LT extraction",
             "FOM & contact resistance output","PDF / PNG report export"],
            self._launch_ctlm))
        cards.addWidget(ModeCard("ltlm","LTLM MODE","Linear Transmission Line Method",
            ["Least-squares linear regression","Probe resistance correction",
             "Width W normalisation","Live graph analysis",
             "Multi-dataset analysis (up to 8)","PDF / PNG report export"],
            self._launch_ltlm))
        root.addLayout(cards)
        root.addStretch()

        footer = QLabel("v1.0.0  ·  © 2026 SemiContact Pro  ·  All rights reserved")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("color:#1a3a4a;font-size:10px;letter-spacing:1px;")
        root.addWidget(footer)

    def _fade_in(self):
        self.setWindowOpacity(0.0)
        self._anim = QPropertyAnimation(self, b"windowOpacity")
        self._anim.setDuration(700); self._anim.setStartValue(0.0); self._anim.setEndValue(1.0)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic); self._anim.start()

    def _launch_ctlm(self): self._on_ctlm()
    def _launch_ltlm(self): self._on_ltlm()

    def _show_about(self):
        dlg = AboutDialog(self)
        dlg.show()