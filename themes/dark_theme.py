"""
SemiContact Pro — Dark Neon Scientific Theme
"""

MAIN_STYLESHEET = """
/* ── Global ──────────────────────────────────────────── */
* {
    font-family: 'Segoe UI', 'Consolas', monospace;
    color: #e0f7ff;
    selection-background-color: #00bcd4;
    selection-color: #000000;
}

QMainWindow, QDialog, QWidget {
    background-color: #090e14;
}

/* ── Scroll bars ─────────────────────────────────────── */
QScrollBar:vertical {
    background: #0d1620;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #00bcd4;
    border-radius: 4px;
    min-height: 20px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QScrollBar:horizontal {
    background: #0d1620;
    height: 8px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal {
    background: #00bcd4;
    border-radius: 4px;
}

/* ── Labels ──────────────────────────────────────────── */
QLabel {
    background: transparent;
}

/* ── Line Edits ──────────────────────────────────────── */
QLineEdit {
    background-color: #0d1a26;
    border: 1px solid #1e3a4a;
    border-radius: 6px;
    padding: 6px 10px;
    color: #b0e8f0;
    font-size: 13px;
}
QLineEdit:focus {
    border: 1px solid #00bcd4;
    background-color: #0f2030;
}
QLineEdit:hover {
    border: 1px solid #007a8f;
}

/* ── ComboBox ────────────────────────────────────────── */
QComboBox {
    background-color: #0d1a26;
    border: 1px solid #1e3a4a;
    border-radius: 6px;
    padding: 5px 10px;
    color: #b0e8f0;
    font-size: 13px;
    min-width: 120px;
}
QComboBox:focus {
    border: 1px solid #00bcd4;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #00bcd4;
    width: 0;
    height: 0;
    margin-right: 6px;
}
QComboBox QAbstractItemView {
    background-color: #0d1a26;
    border: 1px solid #00bcd4;
    selection-background-color: #00bcd4;
    selection-color: #000;
    outline: none;
}

/* ── Push Buttons ────────────────────────────────────── */
QPushButton {
    background-color: #0d2a36;
    border: 1px solid #00bcd4;
    border-radius: 8px;
    padding: 8px 18px;
    color: #00e5ff;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.5px;
}
QPushButton:hover {
    background-color: #00bcd4;
    color: #000000;
}
QPushButton:pressed {
    background-color: #007a8f;
    color: #000000;
}
QPushButton:disabled {
    background-color: #0d1620;
    border-color: #1e3a4a;
    color: #3a5a6a;
}

/* ── Tab Widget ──────────────────────────────────────── */
QTabWidget::pane {
    border: 1px solid #1e3a4a;
    background-color: #090e14;
    border-radius: 6px;
}
QTabBar::tab {
    background-color: #0d1620;
    border: 1px solid #1e3a4a;
    border-bottom: none;
    padding: 7px 18px;
    color: #5a8a9a;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background-color: #0f2030;
    color: #00e5ff;
    border-color: #00bcd4;
}
QTabBar::tab:hover {
    color: #b0e8f0;
    background-color: #0f1e2a;
}

/* ── GroupBox ────────────────────────────────────────── */
QGroupBox {
    border: 1px solid #1e3a4a;
    border-radius: 8px;
    margin-top: 14px;
    padding: 12px 8px 8px 8px;
    background-color: #0b131d;
    font-size: 12px;
    font-weight: 600;
    color: #00bcd4;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 2px 10px;
    left: 12px;
    color: #00e5ff;
    background-color: #090e14;
    border-radius: 4px;
}

/* ── Table ───────────────────────────────────────────── */
QTableWidget {
    background-color: #0b131d;
    alternate-background-color: #0d1a26;
    gridline-color: #1e3a4a;
    border: 1px solid #1e3a4a;
    border-radius: 6px;
    selection-background-color: #00bcd422;
    selection-color: #00e5ff;
}
QTableWidget::item {
    padding: 4px 8px;
    border: none;
}
QHeaderView::section {
    background-color: #0d2a36;
    color: #00e5ff;
    border: none;
    border-right: 1px solid #1e3a4a;
    border-bottom: 1px solid #1e3a4a;
    padding: 6px 10px;
    font-size: 12px;
    font-weight: 600;
}

/* ── Splitter ────────────────────────────────────────── */
QSplitter::handle {
    background-color: #1e3a4a;
}
QSplitter::handle:horizontal {
    width: 3px;
}

/* ── ToolTip ─────────────────────────────────────────── */
QToolTip {
    background-color: #0d2a36;
    border: 1px solid #00bcd4;
    color: #00e5ff;
    padding: 4px 8px;
    border-radius: 4px;
}

/* ── Status Bar ──────────────────────────────────────── */
QStatusBar {
    background-color: #060b10;
    color: #3a7a8a;
    font-size: 11px;
    border-top: 1px solid #1e3a4a;
}

/* ── Spin Box ────────────────────────────────────────── */
QDoubleSpinBox, QSpinBox {
    background-color: #0d1a26;
    border: 1px solid #1e3a4a;
    border-radius: 6px;
    padding: 5px 8px;
    color: #b0e8f0;
}
QDoubleSpinBox:focus, QSpinBox:focus {
    border: 1px solid #00bcd4;
}

/* ── Message Box ─────────────────────────────────────── */
QMessageBox {
    background-color: #090e14;
}
QMessageBox QLabel {
    color: #b0e8f0;
}
"""

SPLASH_STYLESHEET = """
QWidget {
    background-color: #050a0f;
}
"""

CARD_STYLE_BASE = """
    background-color: #0d1a26;
    border: 1px solid #1e3a4a;
    border-radius: 14px;
"""

CARD_STYLE_HOVER = """
    background-color: #0f2235;
    border: 1px solid #00bcd4;
    border-radius: 14px;
"""
