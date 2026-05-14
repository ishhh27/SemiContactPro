"""
SemiContact Pro — main.py
Application entry point.

Launch order:
  1. SplashScreen  (~3 s animated)
  2. Dashboard     (CTLM / LTLM selector)
  3. AnalysisWindow (CTLM or LTLM)

Fully offline, no server, no browser.
"""

import sys
import os

# ── Make sure project root is on sys.path (important for PyInstaller) ─────────
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# ── Qt / matplotlib backend must be set before any import of pyplot ───────────
os.environ.setdefault("MPLBACKEND", "Qt5Agg")

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from themes.dark_theme import MAIN_STYLESHEET
from ui.splash import SplashScreen
from ui.dashboard import Dashboard
from ui.analysis_window import AnalysisWindow


# ── Application controller ────────────────────────────────────────────────────

class AppController:
    """
    Owns all top-level windows and manages the show/hide lifecycle.
    Keeps Qt objects alive (prevents premature GC).
    """

    def __init__(self, app: QApplication):
        self._app      = app
        self._splash:   SplashScreen   | None = None
        self._dashboard: Dashboard     | None = None
        self._analysis: AnalysisWindow | None = None

    def start(self):
        self._splash = SplashScreen(on_finished=self._show_dashboard)

    # ── Dashboard ─────────────────────────────────────────────────────
    def _show_dashboard(self):
        self._dashboard = Dashboard(
            on_ctlm=self._launch_ctlm,
            on_ltlm=self._launch_ltlm,
        )
        self._dashboard.show()

    # ── Analysis windows ──────────────────────────────────────────────
    def _launch_ctlm(self):
        self._dashboard.hide()
        self._analysis = AnalysisWindow(
            mode="CTLM",
            on_back=self._back_to_dashboard,
        )
        self._analysis.show()

    def _launch_ltlm(self):
        self._dashboard.hide()
        self._analysis = AnalysisWindow(
            mode="LTLM",
            on_back=self._back_to_dashboard,
        )
        self._analysis.show()

    def _back_to_dashboard(self):
        self._analysis = None
        if self._dashboard:
            self._dashboard.show()


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    # High-DPI support
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("SemiContact Pro")
    app.setOrganizationName("SemiContact")
    app.setApplicationVersion("1.0.0")

    # Apply global dark theme
    app.setStyleSheet(MAIN_STYLESHEET)

    # Set default font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    controller = AppController(app)
    controller.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
