"""
SemiContact Pro — Output Panel (Right Panel)
Displays extracted parameters as glowing metric cards with per-dataset tabs.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTabWidget, QScrollArea, QFrame, QGridLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QLinearGradient, QBrush, QPainterPath, QPen

from analysis.models import AnalysisSession, Dataset
from utils.helpers import fmt

# Matching palette from plot_canvas
DATASET_COLORS = [
    "#00e5ff", "#00ffa0", "#ff6b6b", "#ffd93d",
    "#c77dff", "#ff9f43", "#48dbfb", "#ff9ff3",
]


# ── Single glowing metric card ────────────────────────────────────────────────

class MetricCard(QWidget):
    """One glowing card showing a single extracted parameter."""

    def __init__(self, label: str, value: str, unit: str = "",
                 accent: str = "#00e5ff", parent=None):
        super().__init__(parent)
        self._accent = QColor(accent)
        self.setMinimumHeight(72)
        self._build_ui(label, value, unit)

    def _build_ui(self, label, value, unit):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(2)

        lbl = QLabel(label)
        lbl.setStyleSheet("color: #3a7a8a; font-size: 10px; letter-spacing: 1px; background: transparent;")
        layout.addWidget(lbl)

        val_row = QHBoxLayout()
        val_row.setSpacing(6)

        self._val_lbl = QLabel(value)
        self._val_lbl.setStyleSheet(
            f"color: {self._accent.name()}; font-size: 18px; font-weight: 700; background: transparent;"
        )
        val_row.addWidget(self._val_lbl)

        if unit:
            u = QLabel(unit)
            u.setStyleSheet("color: #3a7a8a; font-size: 10px; background: transparent;")
            u.setAlignment(Qt.AlignmentFlag.AlignBottom)
            val_row.addWidget(u)

        val_row.addStretch()
        layout.addLayout(val_row)

    def set_value(self, value: str):
        self._val_lbl.setText(value)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        path = QPainterPath()
        path.addRoundedRect(0, 0, w, h, 8, 8)

        bg = QLinearGradient(0, 0, 0, h)
        bg.setColorAt(0, QColor(14, 30, 44))
        bg.setColorAt(1, QColor(9, 16, 26))
        p.fillPath(path, QBrush(bg))

        # Left accent bar
        bar = QPainterPath()
        bar.addRoundedRect(0, 10, 3, h - 20, 1, 1)
        p.fillPath(bar, QBrush(QColor(self._accent.red(), self._accent.green(),
                                      self._accent.blue(), 200)))

        pen = QPen(QColor(self._accent.red(), self._accent.green(),
                          self._accent.blue(), 55))
        pen.setWidth(1)
        p.setPen(pen)
        p.drawPath(path)
        p.end()


# ── Status badge ──────────────────────────────────────────────────────────────

class StatusBadge(QWidget):
    """Convergence indicator."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)

        self._dot = QLabel("●")
        self._dot.setStyleSheet("color: #1e5a6a; font-size: 14px; background: transparent;")
        layout.addWidget(self._dot)

        self._status = QLabel("Awaiting analysis…")
        self._status.setStyleSheet("color: #3a7a8a; font-size: 12px; background: transparent;")
        layout.addWidget(self._status)

        layout.addStretch()

        

    def update_status(self, converged: bool, r2=None):
        if converged:
            self._dot.setStyleSheet("color: #00e5ff; font-size: 14px; background: transparent;")
            self._status.setText("Fit converged  ✓")
            self._status.setStyleSheet("color: #00e5ff; font-size: 12px; background: transparent;")
        else:
            self._dot.setStyleSheet("color: #ff6b6b; font-size: 14px; background: transparent;")
            self._status.setText("Insufficient data  ✗")
            self._status.setStyleSheet("color: #ff6b6b; font-size: 12px; background: transparent;")

       
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        path = QPainterPath()
        path.addRoundedRect(0, 0, w, h, 7, 7)
        p.fillPath(path, QBrush(QColor(10, 20, 32)))
        pen = QPen(QColor(30, 58, 74))
        pen.setWidth(1)
        p.setPen(pen)
        p.drawPath(path)
        p.end()


# ── Per-dataset output tab ────────────────────────────────────────────────────

class DatasetOutputTab(QWidget):
    """Shows all extracted parameters for one dataset."""

    def __init__(self, mode: str, accent: str, parent=None):
        super().__init__(parent)
        self._mode   = mode
        self._accent = accent
        self._cards: dict[str, MetricCard] = {}
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 10, 8, 8)
        root.setSpacing(6)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea{border:none;background:transparent;}")

        inner = QWidget(); inner.setStyleSheet("background:transparent;")
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(0, 0, 4, 0)
        layout.setSpacing(6)

        # Status badge
        self._status = StatusBadge()
        layout.addWidget(self._status)

        layout.addSpacing(4)

        # Metric cards — common to both modes
        metrics = [
            ("slope",     "Slope",               "Ω/µm"),
            ("intercept", "Intercept",            "Ω"),
            ("Rc",        "Contact Resistance Rc","Ω"),
            ("LT",        "Transfer Length L\u209c",   "\u00b5m"),
            ("RSH",       "Sheet Resistance RSH", "Ω/□"),
            ("FOM",       "Figure of Merit FOM",  ""),
        ]

        for key, label, unit in metrics:
            card = MetricCard(label, "—", unit, self._accent)
            self._cards[key] = card
            layout.addWidget(card)

        layout.addStretch()
        scroll.setWidget(inner)
        root.addWidget(scroll)

    def update_dataset(self, ds: Dataset):
        self._status.update_status(ds.converged, ds.r_squared)

        self._cards["slope"].set_value(fmt(ds.slope))
        self._cards["intercept"].set_value(fmt(ds.intercept))
        self._cards["Rc"].set_value(fmt(ds.Rc))
        self._cards["LT"].set_value(fmt(ds.LT))
        self._cards["RSH"].set_value(fmt(ds.RSH))
        self._cards["FOM"].set_value(fmt(ds.FOM))

    def reset(self):
        self._status.update_status(False)
        for card in self._cards.values():
            card.set_value("—")


# ── Main output panel ─────────────────────────────────────────────────────────

class OutputPanel(QWidget):
    """
    Right panel showing extracted parameters.
    Rebuilds tabs whenever a new session is analysed.
    """

    def __init__(self, mode: str, parent=None):
        super().__init__(parent)
        self._mode = mode
        self.setMinimumWidth(240)
        self.setMaximumWidth(320)
        self._output_tabs: list[DatasetOutputTab] = []
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Panel header
        hdr = QWidget()
        hdr.setFixedHeight(40)
        hdr.setStyleSheet("background:#0b131d; border-bottom:1px solid #1e3a4a;")
        hdr_l = QHBoxLayout(hdr)
        hdr_l.setContentsMargins(14, 0, 14, 0)
        lbl = QLabel("EXTRACTED PARAMETERS")
        lbl.setStyleSheet("color:#00bcd4;font-size:10px;letter-spacing:3px;font-weight:600;")
        hdr_l.addWidget(lbl)
        hdr_l.addStretch()
        root.addWidget(hdr)

        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane{background:#090e14;border:none;}
            QTabBar::tab{
                background:#0d1620;border:1px solid #1e3a4a;
                border-bottom:none;padding:4px 10px;
                color:#3a7a8a;font-size:10px;
                border-top-left-radius:5px;border-top-right-radius:5px;
                margin-right:1px;
            }
            QTabBar::tab:selected{background:#0f2030;color:#00e5ff;border-color:#00bcd4;}
        """)
        root.addWidget(self.tab_widget)

        # Placeholder
        self._show_placeholder()

    def _show_placeholder(self):
        ph = QWidget()
        ph.setStyleSheet("background:transparent;")
        l = QVBoxLayout(ph)
        l.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl = QLabel("Run analysis to\nsee results here")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("color:#1e5a6a;font-size:12px;")
        l.addWidget(lbl)
        self.tab_widget.clear()
        self.tab_widget.addTab(ph, "—")
        self._output_tabs.clear()

    # ── Public API ────────────────────────────────────────────────────

    def update_session(self, session: AnalysisSession):
        """Rebuild tabs and populate with fitted session data."""
        self.tab_widget.clear()
        self._output_tabs.clear()

        if not session.datasets:
            self._show_placeholder()
            return

        for idx, ds in enumerate(session.datasets):
            accent = DATASET_COLORS[idx % len(DATASET_COLORS)]
            tab = DatasetOutputTab(self._mode, accent)
            tab.update_dataset(ds)
            self._output_tabs.append(tab)
            self.tab_widget.addTab(tab, f"DS{idx + 1}")

    def reset(self):
        self._show_placeholder()