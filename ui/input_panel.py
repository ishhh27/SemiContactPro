"""
SemiContact Pro — Input Panel (Left Panel)
+ / − buttons use Unicode glyphs rendered via QPushButton with explicit font.
Manual date field replaces auto-timestamp.
Date input enforces strict DD-MM-YYYY validation.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTabWidget, QScrollArea, QGroupBox,
    QFormLayout, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QRegularExpression
from PyQt6.QtGui import QFont, QRegularExpressionValidator, QColor

from analysis.models import D_VALUES
from utils.helpers import safe_float

MAX_DATASETS = 8

# ── Date auto-formatter / validator ──────────────────────────────────────────

class _DateInputFilter:
    """
    Auto-inserts dashes in a QLineEdit as the user types a DD-MM-YYYY date.
    Strips non-digit characters, limits to 8 digits (DDMMYYYY), and
    re-formats as DD-MM-YYYY on the fly.
    """

    def __init__(self, edit: QLineEdit):
        self._edit = edit
        self._updating = False

    def auto_format(self, text: str):
        if self._updating:
            return
        # Strip everything that is not a digit
        digits = "".join(c for c in text if c.isdigit())[:8]
        # Reformat: DD-MM-YYYY
        if len(digits) <= 2:
            formatted = digits
        elif len(digits) <= 4:
            formatted = f"{digits[:2]}-{digits[2:]}"
        else:
            formatted = f"{digits[:2]}-{digits[2:4]}-{digits[4:]}"

        self._updating = True
        pos = len(formatted)
        self._edit.setText(formatted)
        self._edit.setCursorPosition(pos)
        self._updating = False

# ── Shared styles ─────────────────────────────────────────────────────────────
_EDIT_STYLE = """
    QLineEdit {
        background-color: #0d1a26;
        border: 1px solid #1e3a4a;
        border-radius: 5px;
        padding: 5px 8px;
        color: #b0e8f0;
        font-size: 12px;
    }
    QLineEdit:focus { border: 1px solid #00bcd4; }
    QLineEdit:hover { border: 1px solid #2a6a7a; }
"""
_LBL_STYLE = "color: #7ab0c0; font-size: 12px;"


def _make_edit(placeholder: str = "") -> QLineEdit:
    e = QLineEdit()
    e.setPlaceholderText(placeholder)
    e.setStyleSheet(_EDIT_STYLE)
    return e


def _make_lbl(txt: str) -> QLabel:
    l = QLabel(txt)
    l.setStyleSheet(_LBL_STYLE)
    return l


# ── Dataset tab ───────────────────────────────────────────────────────────────

class DatasetInputTab(QWidget):
    """One tab: label, Rp, optional W, one R-field per d-value."""

    def __init__(self, index: int, mode: str, parent=None):
        super().__init__(parent)
        self._index = index
        self._mode  = mode
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 12, 10, 10)
        layout.setSpacing(8)

        form = QFormLayout()
        form.setSpacing(8)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.label_edit = _make_edit(f"Dataset {self._index + 1}")
        form.addRow(_make_lbl("Label"), self.label_edit)

        self.rp_edit = _make_edit("0.0")
        form.addRow(_make_lbl("Rp  (Ω)"), self.rp_edit)

        if self._mode == "LTLM":
            self.w_edit = _make_edit("1.0")
            form.addRow(_make_lbl("W  (µm)"), self.w_edit)
        else:
            self.w_edit = None

        layout.addLayout(form)

        div = QFrame()
        div.setFrameShape(QFrame.Shape.HLine)
        div.setStyleSheet("background:#1e3a4a;border:none;max-height:1px;")
        layout.addWidget(div)

        r_hdr = QLabel("Resistance Values")
        r_hdr.setStyleSheet("color:#00bcd4;font-size:11px;font-weight:600;letter-spacing:1px;")
        layout.addWidget(r_hdr)

        # Column headers — d and R only (CF used internally, not displayed)
        hdr_row = QHBoxLayout(); hdr_row.setSpacing(0)
        cols = [("d (µm)", 60), ("R (Ω)", 100)]
        for txt, w in cols:
            lbl = QLabel(txt)
            lbl.setStyleSheet("color:#3a7a8a;font-size:10px;")
            lbl.setFixedWidth(w)
            hdr_row.addWidget(lbl)
        hdr_row.addStretch()
        layout.addLayout(hdr_row)

        self.r_edits: dict[int, QLineEdit] = {}
        for d in D_VALUES:
            row = QHBoxLayout(); row.setSpacing(6)

            d_lbl = QLabel(str(d))
            d_lbl.setFixedWidth(50)
            d_lbl.setStyleSheet("color:#00bcd4;font-size:12px;font-weight:600;")
            row.addWidget(d_lbl)

            r_edit = _make_edit("")
            r_edit.setFixedWidth(100)
            self.r_edits[d] = r_edit
            row.addWidget(r_edit)
            # CF applied internally in ctlm_engine.py — not displayed here

            row.addStretch()
            layout.addLayout(row)

        layout.addStretch()

    # ── Data extraction ────────────────────────────────────────────────
    def get_label(self) -> str:
        txt = self.label_edit.text().strip()
        return txt if txt else f"Dataset {self._index + 1}"

    def get_Rp(self) -> float:
        v = safe_float(self.rp_edit.text())
        return v if v is not None else 0.0

    def get_W(self) -> float:
        if self.w_edit is None:
            return 1.0
        v = safe_float(self.w_edit.text())
        return v if v is not None else 1.0

    def get_raw_R(self) -> dict:
        return {d: safe_float(e.text()) for d, e in self.r_edits.items()}

    def has_any_data(self) -> bool:
        return any(safe_float(e.text()) is not None for e in self.r_edits.values())

    def clear(self):
        self.label_edit.clear()
        self.rp_edit.clear()
        if self.w_edit:
            self.w_edit.clear()
        for e in self.r_edits.values():
            e.clear()


# ── Main input panel ──────────────────────────────────────────────────────────

class InputPanel(QWidget):
    """
    Left panel.
    FIX 1: + / − icons replaced with styled text buttons that work in EXE.
    CHANGE 4: live timestamp shown in session info box.
    """

    analyze_requested = pyqtSignal()

    def __init__(self, mode: str, parent=None):
        super().__init__(parent)
        self._mode = mode
        self.setMinimumWidth(280)
        self.setMaximumWidth(360)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea{border:none;background:transparent;}")

        inner = QWidget()
        inner.setStyleSheet("background:transparent;")
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # ── Session info ──────────────────────────────────────────────
        info_box = QGroupBox("Session Information")
        info_form = QFormLayout(info_box)
        info_form.setSpacing(8)
        info_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.wafer_edit   = _make_edit("e.g. W2025-001")
        self.product_edit = _make_edit("e.g. GaN-HEMT")
        info_form.addRow(_make_lbl("Wafer No."),  self.wafer_edit)
        info_form.addRow(_make_lbl("Product ID"), self.product_edit)

        # Manual date input — strictly validated DD-MM-YYYY
        self.date_edit = _make_edit("DD-MM-YYYY")
        self.date_edit.setMaxLength(10)
        # Regex validator: two digits, dash, two digits, dash, four digits
        _date_rx = QRegularExpression(
            r"^(0[1-9]|[12]\d|3[01])-(0[1-9]|1[0-2])-\d{4}$"
        )
        self._date_validator = _DateInputFilter(self.date_edit)
        self.date_edit.textChanged.connect(self._date_validator.auto_format)
        self.date_edit.editingFinished.connect(self._validate_date_field)
        info_form.addRow(_make_lbl("Date"), self.date_edit)

        layout.addWidget(info_box)

        # ── Dataset header + add/remove ───────────────────────────────
        ds_hdr = QHBoxLayout()
        ds_title = QLabel("Datasets")
        ds_title.setStyleSheet("color:#00bcd4;font-size:13px;font-weight:600;")
        ds_hdr.addWidget(ds_title)
        ds_hdr.addStretch()

        # FIX 1 — plain text buttons with explicit font; no icon files needed
        add_btn = self._icon_btn("＋", "#00bcd4", "#00e5ff", tip="Add dataset")
        add_btn.clicked.connect(self._add_dataset)
        ds_hdr.addWidget(add_btn)

        rem_btn = self._icon_btn("－", "#3a5a6a", "#b0e8f0", tip="Remove last dataset")
        rem_btn.clicked.connect(self._remove_dataset)
        ds_hdr.addWidget(rem_btn)

        layout.addLayout(ds_hdr)

        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane{background:#0b131d;border:1px solid #1e3a4a;border-radius:6px;}
            QTabBar::tab{
                background:#0d1620;border:1px solid #1e3a4a;border-bottom:none;
                padding:5px 10px;color:#3a7a8a;font-size:11px;
                border-top-left-radius:5px;border-top-right-radius:5px;margin-right:1px;
            }
            QTabBar::tab:selected{background:#0f2030;color:#00e5ff;border-color:#00bcd4;}
            QTabBar::tab:hover{color:#b0e8f0;}
        """)
        layout.addWidget(self.tab_widget)

        self._dataset_tabs: list[DatasetInputTab] = []
        self._add_dataset()

        # ── Analyze / Clear ───────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        self.analyze_btn = QPushButton("⚡  Analyze")
        self.analyze_btn.setFixedHeight(42)
        self.analyze_btn.setStyleSheet("""
            QPushButton{
                background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #005f6b,stop:1 #007a8f);
                border:1px solid #00bcd4;border-radius:8px;
                color:#00e5ff;font-size:13px;font-weight:700;letter-spacing:1px;
            }
            QPushButton:hover{
                background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #00bcd4,stop:1 #00e5ff);
                color:#000;
            }
            QPushButton:pressed{background:#004a5a;}
        """)
        self.analyze_btn.clicked.connect(self.analyze_requested.emit)
        btn_row.addWidget(self.analyze_btn)

        clear_btn = QPushButton("Clear All")
        clear_btn.setFixedHeight(42)
        clear_btn.setStyleSheet("""
            QPushButton{background:#0d1620;border:1px solid #3a5a6a;
                border-radius:8px;color:#3a8a9a;font-size:12px;}
            QPushButton:hover{background:#1e3a4a;color:#b0e8f0;}
        """)
        clear_btn.clicked.connect(self._clear_all)
        btn_row.addWidget(clear_btn)

        layout.addLayout(btn_row)
        layout.addStretch()

        scroll.setWidget(inner)
        root.addWidget(scroll)

    # ── FIX 1 helper: icon button with text glyph ─────────────────────
    @staticmethod
    def _icon_btn(glyph: str, border_col: str, text_col: str, tip: str) -> QPushButton:
        """
        Creates a square button using a Unicode glyph as the 'icon'.
        Uses setFont to force correct rendering — works in EXE without external resources.
        """
        btn = QPushButton(glyph)
        btn.setFixedSize(28, 28)
        btn.setToolTip(tip)
        btn.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        btn.setStyleSheet(f"""
            QPushButton{{
                background:#0d2a36;
                border:1px solid {border_col};
                border-radius:6px;
                color:{text_col};
                padding:0px;
            }}
            QPushButton:hover{{
                background:{border_col};
                color:#000000;
            }}
            QPushButton:pressed{{
                background:#004a5a;
            }}
        """)
        return btn

    # ── Date validation ───────────────────────────────────────────────
    def _validate_date_field(self):
        """Highlight field red if date is not a valid DD-MM-YYYY date."""
        import re
        text = self.date_edit.text().strip()
        if not text or text == "DD-MM-YYYY":
            # empty — neutral
            self.date_edit.setStyleSheet(_EDIT_STYLE)
            return
        match = re.fullmatch(
            r"(0[1-9]|[12]\d|3[01])-(0[1-9]|1[0-2])-(\d{4})", text
        )
        if match:
            # Extra check: day valid for month/year
            import datetime
            try:
                datetime.datetime(
                    int(match.group(3)),
                    int(match.group(2)),
                    int(match.group(1)),
                )
                self.date_edit.setStyleSheet(_EDIT_STYLE)
            except ValueError:
                self._mark_date_invalid()
        else:
            self._mark_date_invalid()

    def _mark_date_invalid(self):
        self.date_edit.setStyleSheet(
            _EDIT_STYLE + "\nQLineEdit { border: 1px solid #ff6b6b; color: #ff6b6b; }"
        )

    # ── Timestamp helper ──────────────────────────────────────────────
    def get_report_date(self) -> str:
        """Return the manually entered date, or empty string if blank."""
        return self.date_edit.text().strip()

    # ── Dataset management ────────────────────────────────────────────
    def _add_dataset(self):
        if len(self._dataset_tabs) >= MAX_DATASETS:
            return
        idx = len(self._dataset_tabs)
        tab = DatasetInputTab(idx, self._mode)
        self._dataset_tabs.append(tab)
        self.tab_widget.addTab(tab, f"DS{idx + 1}")
        self.tab_widget.setCurrentIndex(idx)

    def _remove_dataset(self):
        if len(self._dataset_tabs) <= 1:
            return
        last = len(self._dataset_tabs) - 1
        self.tab_widget.removeTab(last)
        self._dataset_tabs.pop()

    def _clear_all(self):
        for tab in self._dataset_tabs:
            tab.clear()
        self.wafer_edit.clear()
        self.product_edit.clear()

    # ── Data extraction ───────────────────────────────────────────────
    def get_wafer_number(self) -> str:
        return self.wafer_edit.text().strip()

    def get_product_id(self) -> str:
        return self.product_edit.text().strip()

    def get_active_tabs(self) -> list[DatasetInputTab]:
        return [t for t in self._dataset_tabs if t.has_any_data()]