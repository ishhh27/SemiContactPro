"""
SemiContact Pro — Data Table Widget
Fix 3: CF column removed from UI display. Rnew header shown as Rₙₑw (subscript).
Calculations remain unchanged — CF is applied in ctlm_engine.py internally.
Fix 9: Displayed values limited to 2 decimal places (internal precision unchanged).
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont

from analysis.models import Dataset
from utils.helpers import fmt

COL_ACCENT = "#00bcd4"


def _item(text: str, align=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter) -> QTableWidgetItem:
    it = QTableWidgetItem(text)
    it.setTextAlignment(align)
    it.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
    return it


class DataTable(QWidget):
    """
    Tabular view of one dataset's d / R / Rₙₑw values.
    CF is intentionally not displayed — it is used only in backend calculations.
    """

    def __init__(self, mode: str, parent=None):
        super().__init__(parent)
        self._mode = mode
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        hdr = QLabel("Data Table")
        hdr.setStyleSheet("color:#00bcd4;font-size:10px;letter-spacing:2px;font-weight:600;")
        layout.addWidget(hdr)

        # Fix 3 updated: header uses Rₙ (subscript n only)
        cols = ["d (\u00b5m)", "R (\u03a9)", "R\u2099 (\u03a9)"]   # Rₙ

        self._table = QTableWidget(0, len(cols))
        self._table.setHorizontalHeaderLabels(cols)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.setMaximumHeight(200)
        self._table.setStyleSheet(f"""
            QTableWidget {{
                background-color: #0b131d;
                alternate-background-color: #0d1a26;
                gridline-color: #1e3a4a;
                border: 1px solid #1e3a4a;
                border-radius: 6px;
                color: #b0e8f0;
                font-size: 12px;
                selection-background-color: #00bcd422;
            }}
            QHeaderView::section {{
                background-color: #0d2a36;
                color: {COL_ACCENT};
                border: none;
                border-right: 1px solid #1e3a4a;
                border-bottom: 1px solid #1e3a4a;
                padding: 5px;
                font-size: 11px;
                font-weight: 600;
            }}
            QTableWidget::item {{ padding: 4px 8px; }}
        """)
        layout.addWidget(self._table)

    def load_dataset(self, ds: Dataset):
        """Populate the table — d, R, Rₙₑw. CF excluded from display."""
        accent = "#00e5ff" if self._mode == "CTLM" else "#00ffa0"
        self._table.setRowCount(0)

        for pt in ds.points:
            row = self._table.rowCount()
            self._table.insertRow(row)

            self._table.setItem(row, 0, _item(
                str(int(pt.d)),
                Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter,
            ))

            # Fix 9: display precision reduced to 2 dp; internal values unchanged
            r_str = fmt(pt.R, 2) if pt.R is not None else "—"
            self._table.setItem(row, 1, _item(r_str))

            rn_str = fmt(pt.Rnew, 2) if pt.Rnew is not None else "—"
            rn_item = _item(rn_str)
            if pt.Rnew is not None:
                rn_item.setForeground(QColor(accent))
            self._table.setItem(row, 2, rn_item)

    def clear_table(self):
        self._table.setRowCount(0)