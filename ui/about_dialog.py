"""
SemiContact Pro — Credits & Contact Dialog
UI Refresh: Larger dialog, improved spacing, more prominent credits cards,
better typography hierarchy, and more visible contact information.
All functionality, animations, and positioning behavior preserved.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QApplication
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPainter, QColor, QLinearGradient, QBrush, QPainterPath, QPen, QFont


class AboutDialog(QDialog):
    """Credits & Contact popup — dark cyber theme, polished layout."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        # ── CHANGE 1: Dialog width increased from 420 → 520 for a more substantial presence
        self.setFixedWidth(520)
        self._build_ui()
        self._position_on_parent(parent)
        self._fade_in()

    # ── Positioning ────────────────────────────────────────────────────
    def _position_on_parent(self, parent):
        if parent:
            pg = parent.geometry()
            self.move(pg.right() - self.width() - 40, pg.top() + 90)
        else:
            s = QApplication.primaryScreen().geometry()
            self.move(s.width() - self.width() - 50, 100)

    # ── UI ─────────────────────────────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        # ── CHANGE 2: Outer margins increased from 22/18 → 28/24 for more breathing room
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(0)

        # ── Header row: title + close button ──────────────────────────
        hdr = QHBoxLayout()
        hdr.setSpacing(0)
        hdr.setContentsMargins(0, 0, 0, 0)

        # ── CHANGE 3: Header label font size increased from 13 → 14px
        title = QLabel("Credits & Contact")
        title.setStyleSheet(
            "color:#00e5ff;font-size:14px;font-weight:700;"
            "letter-spacing:1.5px;background:transparent;"
        )
        hdr.addWidget(title)
        hdr.addStretch()

        # ── CHANGE 4: Close button slightly larger (24→28) for easier click target
        close_btn = QPushButton("\u00d7")
        close_btn.setFixedSize(28, 28)
        close_btn.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        close_btn.setStyleSheet("""
            QPushButton{
                background:#0d2a36;border:1px solid #1e3a4a;
                border-radius:6px;color:#b0e8f0;
                padding:0px;
            }
            QPushButton:hover{background:#c0392b;color:#ffffff;border-color:#c0392b;}
            QPushButton:pressed{background:#922b21;}
        """)
        close_btn.clicked.connect(self.close)
        hdr.addWidget(close_btn)
        root.addLayout(hdr)

        root.addSpacing(14)

        # ── Cyan divider ───────────────────────────────────────────────
        div = QFrame()
        div.setFrameShape(QFrame.Shape.HLine)
        div.setStyleSheet("background:#00bcd4;border:none;max-height:1px;")
        div.setFixedHeight(1)
        root.addWidget(div)

        root.addSpacing(20)

        # ── CHANGE 5: App name significantly more prominent — larger font, wider tracking
        app_name = QLabel("SemiContact Pro")
        app_name.setStyleSheet(
            "color:#00e5ff;font-size:22px;font-weight:700;"
            "letter-spacing:3px;background:transparent;"
        )
        root.addWidget(app_name)

        root.addSpacing(4)

        # ── CHANGE 6: New tagline below app name for hierarchy depth
        tagline = QLabel("Semiconductor Contact Analysis Platform")
        tagline.setStyleSheet(
            "color:#2a7a8a;font-size:11px;letter-spacing:1.5px;"
            "background:transparent;"
        )
        root.addWidget(tagline)

        root.addSpacing(16)

        # ── About paragraph ────────────────────────────────────────────
        # ── CHANGE 7: Font size increased from 11 → 12px for better legibility
        about = QLabel(
            "SemiContact Pro is a scientific analysis platform developed for semiconductor "
            "contact resistance evaluation, data visualization, curve fitting, and automated "
            "reporting. The application is designed to streamline analytical workflows through "
            "an intuitive interface and precise computational tools."
        )
        about.setWordWrap(True)
        about.setStyleSheet(
            "color:#5a8a9a;font-size:12px;line-height:1.6;"
            "background:transparent;"
        )
        root.addWidget(about)

        root.addSpacing(20)

        # ── CHANGE 8: Section label above credits cards ────────────────
        credits_label = QLabel("PROJECT CREDITS")
        credits_label.setStyleSheet(
            "color:#1e5a6a;font-size:9px;letter-spacing:2.5px;"
            "font-weight:700;background:transparent;"
        )
        root.addWidget(credits_label)

        root.addSpacing(8)

        # ── CHANGE 9: Mentor card — now a standalone bordered panel ────
        mentor_card = QFrame()
        mentor_card.setStyleSheet("""
            QFrame{
                background:#091420;
                border:1px solid #1e3a4a;
                border-left: 3px solid #3a7a8a;
                border-radius:8px;
            }
        """)
        mentor_v = QVBoxLayout(mentor_card)
        mentor_v.setContentsMargins(18, 14, 18, 14)
        mentor_v.setSpacing(3)

        mentor_role = QLabel("PROJECT ARCHITECTURE & GUIDANCE")
        mentor_role.setStyleSheet(
            "color:#3a7a8a;font-size:9px;letter-spacing:1.5px;"
            "font-weight:700;background:transparent;border:none;"
        )
        mentor_v.addWidget(mentor_role)

        # ── CHANGE 10: Mentor name font increased from 12 → 15px
        mentor_name = QLabel("Mr. Niraj Kumar")
        mentor_name.setStyleSheet(
            "color:#b0e8f0;font-size:15px;font-weight:700;"
            "background:transparent;border:none;"
        )
        mentor_v.addWidget(mentor_name)

        root.addWidget(mentor_card)

        root.addSpacing(10)

        # ── CHANGE 11: Developer card — accent cyan left border, higher visual prominence
        dev_card = QFrame()
        dev_card.setStyleSheet("""
            QFrame{
                background:#091420;
                border:1px solid #1e4a5a;
                border-left: 3px solid #00bcd4;
                border-radius:8px;
            }
        """)
        dev_v = QVBoxLayout(dev_card)
        dev_v.setContentsMargins(18, 14, 18, 14)
        dev_v.setSpacing(3)

        dev_role = QLabel("DESIGNED & DEVELOPED BY")
        dev_role.setStyleSheet(
            "color:#3a9aaa;font-size:9px;letter-spacing:1.5px;"
            "font-weight:700;background:transparent;border:none;"
        )
        dev_v.addWidget(dev_role)

        # ── CHANGE 12: Developer name increased from 13 → 17px, full cyan accent
        dev_name = QLabel("Isha Joshi")
        dev_name.setStyleSheet(
            "color:#00e5ff;font-size:17px;font-weight:700;"
            "letter-spacing:0.5px;background:transparent;border:none;"
        )
        dev_v.addWidget(dev_name)

        root.addWidget(dev_card)

        root.addSpacing(20)

        # ── CHANGE 13: Contact section label ──────────────────────────
        contact_section = QLabel("CONTACT")
        contact_section.setStyleSheet(
            "color:#1e5a6a;font-size:9px;letter-spacing:2.5px;"
            "font-weight:700;background:transparent;"
        )
        root.addWidget(contact_section)

        root.addSpacing(8)

        # ── CHANGE 14: Contact info in its own card panel ─────────────
        contact_card = QFrame()
        contact_card.setStyleSheet("""
            QFrame{
                background:#091420;
                border:1px solid #1e3a4a;
                border-left:3px solid #00ffa0;
                border-radius:8px;
            }
        """)
        contact_v = QVBoxLayout(contact_card)
        contact_v.setContentsMargins(18, 14, 18, 14)
        contact_v.setSpacing(6)

        contact_desc = QLabel("For future collaborations and professional correspondence:")
        contact_desc.setStyleSheet(
            "color:#3a7a8a;font-size:11px;background:transparent;border:none;"
        )
        contact_v.addWidget(contact_desc)

        # ── CHANGE 15: Email addresses larger (12→14px) and clearly separated
        email_lbl = QLabel("sniraj1991@gmail.com")
        email_lbl.setStyleSheet(
            "color:#00ffa0;font-size:14px;font-weight:600;"
            "letter-spacing:0.5px;background:transparent;border:none;"
        )
        email_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        email_lbl.setCursor(Qt.CursorShape.IBeamCursor)
        contact_v.addWidget(email_lbl)

        email_lbl2 = QLabel("ijoshi2705@gmail.com")
        email_lbl2.setStyleSheet(
            "color:#00ffa0;font-size:14px;font-weight:600;"
            "letter-spacing:0.5px;background:transparent;border:none;"
        )
        email_lbl2.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        email_lbl2.setCursor(Qt.CursorShape.IBeamCursor)
        contact_v.addWidget(email_lbl2)

        root.addWidget(contact_card)

        root.addSpacing(20)

        # ── Footer divider + version ───────────────────────────────────
        foot_div = QFrame()
        foot_div.setFrameShape(QFrame.Shape.HLine)
        foot_div.setStyleSheet("background:#1e3a4a;border:none;max-height:1px;")
        foot_div.setFixedHeight(1)
        root.addWidget(foot_div)

        root.addSpacing(10)

        ver = QLabel("v1.0.0  ·  © 2026 SemiContact Pro")
        ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ver.setStyleSheet("color:#1e3a4a;font-size:9px;background:transparent;")
        root.addWidget(ver)

    # ── Painted rounded background ─────────────────────────────────────
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        path = QPainterPath()
        path.addRoundedRect(0, 0, w, h, 14, 14)
        bg = QLinearGradient(0, 0, 0, h)
        bg.setColorAt(0, QColor(13, 22, 34))
        bg.setColorAt(1, QColor(8, 14, 22))
        p.fillPath(path, QBrush(bg))
        pen = QPen(QColor(0, 188, 212, 110))
        pen.setWidth(1)
        p.setPen(pen)
        p.drawPath(path)
        p.end()

    # ── Fade in ────────────────────────────────────────────────────────
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