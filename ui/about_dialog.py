"""
SemiContact Pro — Credits & Contact Dialog
Refined layout: cleaner hierarchy, tighter spacing, improved alignment.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QApplication
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPainter, QColor, QLinearGradient, QBrush, QPainterPath, QPen, QFont


class AboutDialog(QDialog):
    """Compact Credits & Contact popup — dark cyber theme."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.setFixedWidth(420)
        self._build_ui()
        self._position_on_parent(parent)
        self._fade_in()

    # ── Positioning ───────────────────────────────────────────────────
    def _position_on_parent(self, parent):
        if parent:
            pg = parent.geometry()
            self.move(pg.right() - self.width() - 30, pg.top() + 80)
        else:
            s = QApplication.primaryScreen().geometry()
            self.move(s.width() - self.width() - 50, 100)

    # ── UI ────────────────────────────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(22, 18, 22, 18)
        root.setSpacing(0)

        # ── Header row: title + close button ─────────────────────────
        hdr = QHBoxLayout()
        hdr.setSpacing(0)
        hdr.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Credits & Contact")
        title.setStyleSheet(
            "color:#00e5ff;font-size:13px;font-weight:700;"
            "letter-spacing:1px;background:transparent;"
        )
        hdr.addWidget(title)
        hdr.addStretch()

        close_btn = QPushButton("\u00d7")   # × — universally rendered multiplication sign
        close_btn.setFixedSize(24, 24)
        close_btn.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        close_btn.setStyleSheet("""
            QPushButton{
                background:#0d2a36;border:1px solid #1e3a4a;
                border-radius:5px;color:#b0e8f0;
                padding:0px;
            }
            QPushButton:hover{background:#c0392b;color:#ffffff;border-color:#c0392b;}
            QPushButton:pressed{background:#922b21;}
        """)
        close_btn.clicked.connect(self.close)
        hdr.addWidget(close_btn)
        root.addLayout(hdr)

        root.addSpacing(10)

        # ── Thin cyan divider ─────────────────────────────────────────
        div = QFrame()
        div.setFrameShape(QFrame.Shape.HLine)
        div.setStyleSheet("background:#00bcd4;border:none;max-height:1px;")
        div.setFixedHeight(1)
        root.addWidget(div)

        root.addSpacing(12)

        # ── App name ──────────────────────────────────────────────────
        app_name = QLabel("SemiContact Pro")
        app_name.setStyleSheet(
            "color:#00e5ff;font-size:15px;font-weight:700;"
            "letter-spacing:2px;background:transparent;"
        )
        root.addWidget(app_name)

        root.addSpacing(8)

        # ── About paragraph ───────────────────────────────────────────
        about = QLabel(
            "SemiContact Pro is a scientific analysis platform developed for semiconductor "
            "contact resistance evaluation, data visualization, curve fitting, and automated "
            "reporting. The application is designed to streamline analytical workflows through "
            "an intuitive interface and precise computational tools."
        )
        about.setWordWrap(True)
        about.setStyleSheet(
            "color:#6a9aaa;font-size:11px;line-height:1.5;"
            "background:transparent;"
        )
        root.addWidget(about)

        root.addSpacing(14)

        # ── Credits card ──────────────────────────────────────────────
        card = QFrame()
        card.setStyleSheet(
            "background:#0b1820;border:1px solid #1e3a4a;border-radius:8px;"
        )
        card_v = QVBoxLayout(card)
        card_v.setContentsMargins(16, 14, 16, 14)
        card_v.setSpacing(0)

        def _row(role: str, name: str, role_color: str = "#3a7a8a",
                 name_color: str = "#b0e8f0", name_size: int = 12):
            """One role + name pair inside the credits card."""
            role_lbl = QLabel(role)
            role_lbl.setStyleSheet(
                f"color:{role_color};font-size:9px;letter-spacing:1px;"
                "font-weight:600;background:transparent;"
            )
            name_lbl = QLabel(name)
            name_lbl.setStyleSheet(
                f"color:{name_color};font-size:{name_size}px;font-weight:700;"
                "background:transparent;"
            )
            return role_lbl, name_lbl

        mentor_role, mentor_name = _row(
            "PROJECT ARCHITECTURE & GUIDANCE",
            "Mr. Niraj Kumar",
        )
        card_v.addWidget(mentor_role)
        card_v.addSpacing(2)
        card_v.addWidget(mentor_name)

        # Intra-card separator
        card_v.addSpacing(10)
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background:#1e3a4a;border:none;max-height:1px;")
        sep.setFixedHeight(1)
        card_v.addWidget(sep)
        card_v.addSpacing(10)

        dev_role, dev_name = _row(
            "DESIGNED & DEVELOPED BY",
            "Isha Joshi",
            name_color="#00e5ff",
            name_size=13,
        )
        card_v.addWidget(dev_role)
        card_v.addSpacing(2)
        card_v.addWidget(dev_name)

        root.addWidget(card)

        root.addSpacing(12)

        # ── Contact line ──────────────────────────────────────────────
        contact_lbl = QLabel("For future collaborations and professional correspondence:")
        contact_lbl.setStyleSheet("color:#3a7a8a;font-size:10px;background:transparent;")
        root.addWidget(contact_lbl)

        root.addSpacing(4)

        email_lbl = QLabel("sniraj1991@gmail.com \nijoshi2705@gmail.com")
        email_lbl.setStyleSheet(
            "color:#00ffa0;font-size:12px;font-weight:600;"
            "letter-spacing:0.5px;background:transparent;"
        )
        email_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        email_lbl.setCursor(Qt.CursorShape.IBeamCursor)
        root.addWidget(email_lbl)

        root.addSpacing(14)

        # ── Footer divider + version ──────────────────────────────────
        foot_div = QFrame()
        foot_div.setFrameShape(QFrame.Shape.HLine)
        foot_div.setStyleSheet("background:#1e3a4a;border:none;max-height:1px;")
        foot_div.setFixedHeight(1)
        root.addWidget(foot_div)

        root.addSpacing(8)

        ver = QLabel("v1.0.0  ·  © 2026 SemiContact Pro")
        ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ver.setStyleSheet("color:#1e3a4a;font-size:9px;background:transparent;")
        root.addWidget(ver)

    # ── Painted rounded background ────────────────────────────────────
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        path = QPainterPath()
        path.addRoundedRect(0, 0, w, h, 12, 12)
        bg = QLinearGradient(0, 0, 0, h)
        bg.setColorAt(0, QColor(13, 22, 34))
        bg.setColorAt(1, QColor(8, 14, 22))
        p.fillPath(path, QBrush(bg))
        pen = QPen(QColor(0, 188, 212, 110))
        pen.setWidth(1)
        p.setPen(pen)
        p.drawPath(path)
        p.end()

    # ── Fade in ───────────────────────────────────────────────────────
    def _fade_in(self):
        self.setWindowOpacity(0.0)
        self._anim = QPropertyAnimation(self, b"windowOpacity")
        self._anim.setDuration(220)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim.start()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)
