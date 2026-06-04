"""
SemiContact Pro — Analysis Window
Three-panel layout: InputPanel | Graph + DataTable | OutputPanel
Works for both CTLM and LTLM modes.
"""

import os

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QSplitter, QLabel, QStatusBar, QPushButton,
    QFileDialog, QMessageBox, QApplication, QTabWidget
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor

from themes.dark_theme import MAIN_STYLESHEET
from ui.input_panel import InputPanel
from ui.output_panel import OutputPanel
from ui.data_table import DataTable
from graphs.plot_canvas import PlotCanvas

from analysis.models import AnalysisSession
from analysis.ctlm_engine import build_ctlm_dataset, run_ctlm_session
from analysis.ltlm_engine import build_ltlm_dataset, run_ltlm_session

from exports.exporter import export_png, export_pdf


class AnalysisWindow(QMainWindow):
    """
    Main workstation window.
    mode: "CTLM" or "LTLM"
    """

    def __init__(self, mode: str, on_back=None):
        super().__init__()
        self._mode    = mode
        self._on_back = on_back
        self._session: AnalysisSession | None = None

        self.setStyleSheet(MAIN_STYLESHEET)
        self._setup_window()
        self._build_ui()
        self._fade_in()

    # ── Window ────────────────────────────────────────────────────────
    def _setup_window(self):
        mode_display = "Circular TLM" if self._mode == "CTLM" else "Linear TLM"
        self.setWindowTitle(f"SemiContact Pro  —  {self._mode}  ({mode_display})")
        self.setMinimumSize(1280, 760)
        self.resize(1440, 860)
        screen = QApplication.primaryScreen().geometry()
        self.move(
            (screen.width()  - self.width())  // 2,
            (screen.height() - self.height()) // 2,
        )

    # ── UI ────────────────────────────────────────────────────────────
    def _build_ui(self):
        central = QWidget()
        central.setStyleSheet("background:#090e14;")
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Top bar ───────────────────────────────────────────────────
        main_layout.addWidget(self._build_topbar())

        # ── Three-panel splitter ──────────────────────────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("""
            QSplitter::handle { background:#1e3a4a; width:3px; }
        """)
        splitter.setHandleWidth(3)

        # LEFT: input
        self.input_panel = InputPanel(self._mode)
        self.input_panel.analyze_requested.connect(self._run_analysis)
        splitter.addWidget(self.input_panel)

        # CENTRE: graph + data table stacked
        centre = QWidget()
        centre.setStyleSheet("background:#090e14;")
        centre_v = QVBoxLayout(centre)
        centre_v.setContentsMargins(0, 0, 0, 0)
        centre_v.setSpacing(0)

        self.plot_canvas = PlotCanvas(self._mode)
        centre_v.addWidget(self.plot_canvas, stretch=3)

        # Tab bar for data table (one tab per dataset after analysis)
        self._table_tabs = QTabWidget()
        self._table_tabs.setMaximumHeight(220)
        self._table_tabs.setStyleSheet("""
            QTabWidget::pane{background:#0b131d;border-top:1px solid #1e3a4a;}
            QTabBar::tab{
                background:#0d1620;border:1px solid #1e3a4a;
                border-bottom:none;padding:4px 12px;
                color:#3a7a8a;font-size:10px;
                border-top-left-radius:5px;border-top-right-radius:5px;
                margin-right:1px;
            }
            QTabBar::tab:selected{background:#0f2030;color:#00e5ff;border-color:#00bcd4;}
        """)
        # placeholder tab
        ph = QLabel("  Run analysis to populate data table")
        ph.setStyleSheet("color:#1e5a6a;font-size:11px;")
        self._table_tabs.addTab(ph, "Data Table")
        centre_v.addWidget(self._table_tabs, stretch=1)

        splitter.addWidget(centre)

        # RIGHT: output
        self.output_panel = OutputPanel(self._mode)
        splitter.addWidget(self.output_panel)

        splitter.setSizes([300, 860, 280])
        main_layout.addWidget(splitter, stretch=1)

        # ── Status bar ────────────────────────────────────────────────
        self._status_bar = QStatusBar()
        self._status_bar.setStyleSheet(
            "QStatusBar{background:#060b10;color:#3a7a8a;font-size:11px;"
            "border-top:1px solid #1e3a4a;}"
        )
        self.setStatusBar(self._status_bar)
        self._status("Ready  —  Enter data and click Analyze")

    def _build_topbar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(52)
        bar.setStyleSheet("background:#060b10;border-bottom:1px solid #1e3a4a;")
        hl = QHBoxLayout(bar)
        hl.setContentsMargins(16, 0, 16, 0)
        hl.setSpacing(12)

        # Back button
        if self._on_back:
            back_btn = QPushButton("← Dashboard")
            back_btn.setFixedHeight(32)
            back_btn.setStyleSheet("""
                QPushButton{background:#0d1620;border:1px solid #1e3a4a;
                border-radius:6px;color:#3a7a8a;font-size:11px;padding:0 12px;}
                QPushButton:hover{background:#1e3a4a;color:#b0e8f0;}
            """)
            back_btn.clicked.connect(self._go_back)
            hl.addWidget(back_btn)

        # Mode badge
        accent = "#00e5ff" if self._mode == "CTLM" else "#00ffa0"
        badge = QLabel(f"  {self._mode} MODE  ")
        badge.setStyleSheet(
            f"color:{accent};background:#0d2a36;border:1px solid {accent};"
            "border-radius:5px;font-size:11px;font-weight:700;letter-spacing:2px;padding:3px 0;"
        )
        hl.addWidget(badge)

        mode_lbl = QLabel(
            "Circular Transmission Line Method" if self._mode == "CTLM"
            else "Linear Transmission Line Method"
        )
        mode_lbl.setStyleSheet("color:#3a7a8a;font-size:12px;")
        hl.addWidget(mode_lbl)

        hl.addStretch()

        # Export buttons
        for label, slot in [("⬇  Export PNG", self._export_png),
                             ("⬇  Export PDF", self._export_pdf)]:
            btn = QPushButton(label)
            btn.setFixedHeight(32)
            btn.setStyleSheet("""
                QPushButton{background:#0d2a36;border:1px solid #00bcd4;
                border-radius:6px;color:#00e5ff;font-size:11px;padding:0 14px;font-weight:600;}
                QPushButton:hover{background:#00bcd4;color:#000;}
                QPushButton:pressed{background:#007a8f;color:#000;}
                QPushButton:disabled{background:#0d1620;border-color:#1e3a4a;color:#1e4050;}
            """)
            btn.clicked.connect(slot)
            hl.addWidget(btn)
            if label.startswith("⬇  Export PNG"):
                self._png_btn = btn
            else:
                self._pdf_btn = btn

        return bar

    # ── Analysis ──────────────────────────────────────────────────────
    def _run_analysis(self):
        active_tabs = self.input_panel.get_active_tabs()
        if not active_tabs:
            QMessageBox.warning(self, "No Data",
                                "Please enter at least one R value before running analysis.")
            return

        session = AnalysisSession(
            wafer_number=self.input_panel.get_wafer_number(),
            product_id=self.input_panel.get_product_id(),
            mode=self._mode,
        )

        for tab in active_tabs:
            raw_R = tab.get_raw_R()
            if self._mode == "CTLM":
                ds = build_ctlm_dataset(
                    label=tab.get_label(),
                    Rp=tab.get_Rp(),
                    raw_R=raw_R,
                )
            else:
                ds = build_ltlm_dataset(
                    label=tab.get_label(),
                    Rp=tab.get_Rp(),
                    W=tab.get_W(),
                    raw_R=raw_R,
                )
            session.datasets.append(ds)

        # Fit
        if self._mode == "CTLM":
            run_ctlm_session(session)
        else:
            run_ltlm_session(session)

        self._session = session

        # Update graph
        self.plot_canvas.update_plot(session)

        # Update output panel
        self.output_panel.update_session(session)

        # Rebuild data table tabs
        self._rebuild_data_tables(session)

        # Status
        n_ok = sum(1 for d in session.datasets if d.converged)
        self._status(
            f"Analysis complete  —  {n_ok}/{len(session.datasets)} datasets converged  "
            f"| Wafer: {session.wafer_number or '—'}  | Product: {session.product_id or '—'}"
        )

    def _rebuild_data_tables(self, session: AnalysisSession):
        self._table_tabs.clear()
        for idx, ds in enumerate(session.datasets):
            tbl = DataTable(self._mode)
            tbl.load_dataset(ds)
            self._table_tabs.addTab(tbl, f"DS{idx + 1}  {ds.label}")

    # ── Export ────────────────────────────────────────────────────────
    def _export_png(self):
        if self._session is None:
            QMessageBox.information(self, "No Analysis", "Run analysis first.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Graph as PNG", "SemiContactPro_graph.png",
            "PNG Image (*.png)"
        )
        if not path:
            return
        try:
            export_png(self.plot_canvas.get_figure(), path,
                       show_markers=self.plot_canvas.get_show_markers())
            self._status(f"PNG exported \u2192 {path}")
            QMessageBox.information(self, "Export Successful", f"Graph saved to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))

    def _export_pdf(self):
        if self._session is None:
            QMessageBox.information(self, "No Analysis", "Run analysis first.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export PDF Report", "SemiContactPro_report.pdf",
            "PDF Document (*.pdf)"
        )
        if not path:
            return
        try:
            export_pdf(
                self._session,
                self.plot_canvas.get_figure(),
                path,
                report_date=self.input_panel.get_report_date(),
                show_markers=self.plot_canvas.get_show_markers(),
            )
            self._status(f"PDF exported \u2192 {path}")
            QMessageBox.information(self, "Export Successful", f"Report saved to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))

    # ── Helpers ───────────────────────────────────────────────────────
    def _status(self, msg: str):
        self._status_bar.showMessage(f"  {msg}")

    def _go_back(self):
        self.close()
        if self._on_back:
            self._on_back()

    def _fade_in(self):
        self.setWindowOpacity(0.0)
        self._anim = QPropertyAnimation(self, b"windowOpacity")
        self._anim.setDuration(500)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim.start()
