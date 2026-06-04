"""
SemiContact Pro — Splash Screen
Futuristic semiconductor workstation aesthetic with animated loading.
"""

import math
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QProgressBar
from PyQt6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve,
    pyqtProperty, QPoint, QRect
)
from PyQt6.QtGui import (
    QPainter, QColor, QLinearGradient, QFont, QPen,
    QRadialGradient, QConicalGradient, QBrush, QPainterPath
)


class AnimatedOrb(QWidget):
    """Spinning cyan ring with inner glow — central decorative element."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._angle = 0.0
        self._pulse = 0.0
        self._pulse_dir = 1
        self.setFixedSize(180, 180)

        self._spin_timer = QTimer(self)
        self._spin_timer.timeout.connect(self._tick)
        self._spin_timer.start(16)  # ~60 fps

    def _tick(self):
        self._angle = (self._angle + 1.2) % 360
        self._pulse += 0.02 * self._pulse_dir
        if self._pulse >= 1.0:
            self._pulse_dir = -1
        elif self._pulse <= 0.0:
            self._pulse_dir = 1
        self.update()

    def stop(self):
        self._spin_timer.stop()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        cx, cy = self.width() / 2, self.height() / 2

        # Outer glow
        glow = QRadialGradient(cx, cy, 90)
        alpha = int(40 + 30 * self._pulse)
        glow.setColorAt(0, QColor(0, 200, 220, alpha))
        glow.setColorAt(1, QColor(0, 0, 0, 0))
        p.setBrush(QBrush(glow))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(int(cx - 90), int(cy - 90), 180, 180)

        # Core circle
        core = QRadialGradient(cx, cy, 52)
        core.setColorAt(0, QColor(10, 50, 65, 220))
        core.setColorAt(1, QColor(5, 15, 25, 200))
        p.setBrush(QBrush(core))
        p.drawEllipse(int(cx - 52), int(cy - 52), 104, 104)

        # Ring segments
        rect = QRect(int(cx - 68), int(cy - 68), 136, 136)
        for i in range(3):
            pen = QPen(QColor(0, 188, 212, 220 - i * 60))
            pen.setWidth(3 - i)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(pen)
            offset = self._angle + i * 120
            p.drawArc(rect, int(offset * 16), int(240 * 16))

        # Inner circuit lines
        pen = QPen(QColor(0, 230, 255, 80))
        pen.setWidth(1)
        p.setPen(pen)
        for i in range(6):
            ang = math.radians(self._angle * 0.5 + i * 60)
            x1 = cx + 20 * math.cos(ang)
            y1 = cy + 20 * math.sin(ang)
            x2 = cx + 48 * math.cos(ang)
            y2 = cy + 48 * math.sin(ang)
            p.drawLine(int(x1), int(y1), int(x2), int(y2))

        # Bright center dot
        bright = int(180 + 75 * self._pulse)
        p.setBrush(QColor(0, bright, 255, 200))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(int(cx - 5), int(cy - 5), 10, 10)

        p.end()


class ScanLine(QWidget):
    """Horizontal scanning line effect."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pos = 0
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)

    def set_pos(self, pos):
        self._pos = pos
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        grad = QLinearGradient(0, self._pos, self.width(), self._pos)
        grad.setColorAt(0, QColor(0, 0, 0, 0))
        grad.setColorAt(0.3, QColor(0, 200, 220, 60))
        grad.setColorAt(0.5, QColor(0, 230, 255, 120))
        grad.setColorAt(0.7, QColor(0, 200, 220, 60))
        grad.setColorAt(1, QColor(0, 0, 0, 0))
        p.fillRect(0, self._pos - 1, self.width(), 3, QBrush(grad))
        p.end()


class SplashScreen(QWidget):
    """
    Full-screen splash with:
    - dark gradient background with grid overlay
    - animated spinner orb
    - title + subtitle typography
    - loading progress bar
    - auto-close after ~3 seconds
    """

    def __init__(self, on_finished):
        super().__init__()
        self._on_finished = on_finished
        self._scan_y = 0

        self._setup_window()
        self._build_ui()
        self._start_sequence()

    # ── Setup ──────────────────────────────────────────────────────
    def _setup_window(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.SplashScreen
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(820, 500)

        # Center on screen
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(0)
        layout.setContentsMargins(60, 50, 60, 40)

        # Orb
        self.orb = AnimatedOrb(self)
        layout.addWidget(self.orb, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addSpacing(24)

        # Title
        self.title_lbl = QLabel("SemiContact Pro")
        self.title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont("Segoe UI", 36, QFont.Weight.Bold)
        self.title_lbl.setFont(title_font)
        self.title_lbl.setStyleSheet("color: #00e5ff; letter-spacing: 4px; background: transparent;")
        layout.addWidget(self.title_lbl)

        # Sub-title
        sub = QLabel("SEMICONDUCTOR CONTACT RESISTANCE WORKSTATION")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub_font = QFont("Consolas", 10)
        sub.setFont(sub_font)
        sub.setStyleSheet("color: #3a8a9a; letter-spacing: 3px; background: transparent;")
        layout.addWidget(sub)

        layout.addSpacing(10)

        # Version badge
        ver = QLabel("v1.0.0  ·  CTLM  |  LTLM  |  TLM")
        ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ver.setStyleSheet("color: #1e5a6a; font-size: 11px; letter-spacing: 2px; background: transparent;")
        layout.addWidget(ver)

        layout.addSpacing(28)

        # Status label
        self.status_lbl = QLabel("Initializing core modules…")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_lbl.setStyleSheet("color: #00bcd4; font-size: 12px; letter-spacing: 1px; background: transparent;")
        layout.addWidget(self.status_lbl)

        layout.addSpacing(10)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setFixedHeight(4)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                background-color: #0d2030;
                border: none;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00bcd4,
                    stop:0.5 #00e5ff,
                    stop:1 #00bcd4
                );
                border-radius: 2px;
            }
        """)
        layout.addWidget(self.progress)

        layout.addSpacing(12)

        # Copyright
        copy_lbl = QLabel("© 2026 SemiContact Pro  ·  All rights reserved")
        copy_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        copy_lbl.setStyleSheet("color: #1a3a4a; font-size: 10px; background: transparent;")
        layout.addWidget(copy_lbl)

        # Scan line overlay
        self.scan = ScanLine(self)
        self.scan.setGeometry(0, 0, self.width(), self.height())
        self.scan.lower()

    # ── Sequence ────────────────────────────────────────────────────
    def _start_sequence(self):
        self._progress_val = 0
        self._messages = [
            (10,  "Loading analysis engine…"),
            (28,  "Initializing CTLM solver…"),
            (46,  "Initializing LTLM solver…"),
            (63,  "Loading graph renderer…"),
            (78,  "Configuring export pipeline…"),
            (90,  "Preparing workspace…"),
            (100, "Ready."),
        ]
        self._msg_idx = 0

        # Fade in
        self.setWindowOpacity(0.0)
        self.show()
        self._fade_in = QPropertyAnimation(self, b"windowOpacity")
        self._fade_in.setDuration(600)
        self._fade_in.setStartValue(0.0)
        self._fade_in.setEndValue(1.0)
        self._fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._fade_in.start()

        # Progress timer
        self._prog_timer = QTimer(self)
        self._prog_timer.timeout.connect(self._advance_progress)
        self._prog_timer.start(25)

        # Scan line timer
        self._scan_timer = QTimer(self)
        self._scan_timer.timeout.connect(self._advance_scan)
        self._scan_timer.start(16)

    def _advance_progress(self):
        if self._msg_idx < len(self._messages):
            target, msg = self._messages[self._msg_idx]
            if self._progress_val < target:
                self._progress_val = min(self._progress_val + 1, target)
                self.progress.setValue(self._progress_val)
            else:
                self.status_lbl.setText(msg)
                self._msg_idx += 1
        else:
            self._prog_timer.stop()
            QTimer.singleShot(600, self._close_splash)

    def _advance_scan(self):
        self._scan_y = (self._scan_y + 3) % self.height()
        self.scan.set_pos(self._scan_y)

    def _close_splash(self):
        self._scan_timer.stop()
        self.orb.stop()
        fade_out = QPropertyAnimation(self, b"windowOpacity")
        fade_out.setDuration(500)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        fade_out.setEasingCurve(QEasingCurve.Type.InCubic)
        fade_out.finished.connect(self._finish)
        fade_out.start()
        self._fade_out = fade_out  # keep reference

    def _finish(self):
        self.close()
        self._on_finished()

    # ── Paint: background ──────────────────────────────────────────
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        # Rounded rect clip
        path = QPainterPath()
        path.addRoundedRect(0, 0, w, h, 18, 18)
        p.setClipPath(path)

        # Background gradient
        bg = QLinearGradient(0, 0, 0, h)
        bg.setColorAt(0, QColor(8, 14, 22))
        bg.setColorAt(0.5, QColor(6, 10, 18))
        bg.setColorAt(1, QColor(4, 8, 14))
        p.fillPath(path, QBrush(bg))

        # Grid lines
        pen = QPen(QColor(0, 188, 212, 12))
        pen.setWidth(1)
        p.setPen(pen)
        step = 32
        for x in range(0, w, step):
            p.drawLine(x, 0, x, h)
        for y in range(0, h, step):
            p.drawLine(0, y, w, y)

        # Corner accent marks
        accent = QPen(QColor(0, 230, 255, 160))
        accent.setWidth(2)
        p.setPen(accent)
        corner_len = 22
        # top-left
        p.drawLine(18, 18, 18 + corner_len, 18)
        p.drawLine(18, 18, 18, 18 + corner_len)
        # top-right
        p.drawLine(w - 18, 18, w - 18 - corner_len, 18)
        p.drawLine(w - 18, 18, w - 18, 18 + corner_len)
        # bottom-left
        p.drawLine(18, h - 18, 18 + corner_len, h - 18)
        p.drawLine(18, h - 18, 18, h - 18 - corner_len)
        # bottom-right
        p.drawLine(w - 18, h - 18, w - 18 - corner_len, h - 18)
        p.drawLine(w - 18, h - 18, w - 18, h - 18 - corner_len)

        # Border glow
        border_pen = QPen(QColor(0, 188, 212, 80))
        border_pen.setWidth(1)
        p.setPen(border_pen)
        p.drawRoundedRect(1, 1, w - 2, h - 2, 17, 17)

        p.end()
