"""
SemiContact Pro — Scientific Plot Canvas
Items implemented:
  1. Centralised marker system via graphs.marker_manager
  2. "Hide Markers" toggle — scatter points disappear; fit lines stay
  3. Export isolation — live figure never altered by export (see export_renderer)
  4. Deviation as smooth cubic-spline connected curve
  5. Axis-label overlap fix — x-label goes on residual subplot only
  6. Scale / tick-interval control (unchanged)
  7. Unified dataset colour — one colour per dataset drives all artists;
     custom Figure Options dialog exposes only that single colour property.
"""

import numpy as np
import matplotlib
import matplotlib.colors as mcolors
matplotlib.use("QtAgg")

from matplotlib.backends.backend_qtagg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar,
)
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QScrollArea,
    QPushButton, QLabel, QComboBox, QLineEdit,
    QDialog, QDialogButtonBox, QColorDialog, QSizePolicy,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from analysis.models import AnalysisSession
from graphs.marker_manager import get_marker, scatter_kwargs

# ── Default palette — single source of truth for both canvas & export ─────────
DATASET_COLORS = [
    "#00e5ff", "#00ffa0", "#ff6b6b", "#ffd93d",
    "#c77dff", "#ff9f43", "#48dbfb", "#ff9ff3",
]


# ── Theme helpers ─────────────────────────────────────────────────────────────

def _apply_dark_style(fig: Figure, axes) -> None:
    if not isinstance(axes, (list, tuple)):
        axes = [axes]
    fig.patch.set_facecolor("#090e14")
    for ax in axes:
        ax.set_facecolor("#0b131d")
        for sp in ax.spines.values():
            sp.set_color("#1e3a4a")
        ax.tick_params(colors="#3a8a9a", labelsize=9)
        ax.xaxis.label.set_color("#b0e8f0")
        ax.yaxis.label.set_color("#b0e8f0")
        ax.title.set_color("#00e5ff")
        ax.grid(True, color="#1e3a4a", linestyle="--", linewidth=0.6, alpha=0.7)
        ax.set_axisbelow(True)


def _toolbar_btn(text: str, checkable: bool = False) -> QPushButton:
    btn = QPushButton(text)
    btn.setCheckable(checkable)
    btn.setFixedHeight(26)
    btn.setFont(QFont("Segoe UI", 10))
    btn.setStyleSheet("""
        QPushButton{
            background:#0d2030;border:1px solid #3a5a6a;
            border-radius:5px;color:#3a8a9a;font-size:11px;padding:0 10px;
        }
        QPushButton:hover{border-color:#00bcd4;color:#00e5ff;}
        QPushButton:checked{
            background:#0d3a4a;border:1px solid #00e5ff;
            color:#00e5ff;font-weight:600;
        }
    """)
    return btn


# ── Dataset Appearance Dialog ─────────────────────────────────────────────────

# Human-readable label → matplotlib linestyle string
_LINE_STYLES: list[tuple[str, str]] = [
    ("Solid",     "-"),
    ("Dashed",    "--"),
    ("Dotted",    ":"),
    ("Dash-dot",  "-."),
]
_LINE_STYLE_LABELS = [ls[0] for ls in _LINE_STYLES]
_LABEL_TO_LS       = {ls[0]: ls[1] for ls in _LINE_STYLES}
_LS_TO_LABEL       = {ls[1]: ls[0] for ls in _LINE_STYLES}

_LINE_WIDTHS = ["0.8", "1.0", "1.2", "1.6", "2.0", "2.5", "3.0", "4.0"]


class DatasetAppearanceDialog(QDialog):
    """
    Replacement for matplotlib's built-in Figure Options.
    Shows Line Style, Line Width, and Dataset Color for each active dataset.
    Emits no signals — caller reads chosen_* attributes after exec().
    """

    _SWATCH_STYLE = (
        "border:1px solid #3a5a6a;border-radius:4px;"
        "min-width:56px;min-height:22px;font-size:10px;"
    )

    _COMBO_STYLE = """
        QComboBox{background:#0d2030;border:1px solid #3a5a6a;border-radius:4px;
            color:#b0e8f0;font-size:10px;padding:1px 6px;min-width:88px;}
        QComboBox:hover{border-color:#00bcd4;}
        QComboBox QAbstractItemView{background:#0d2030;color:#b0e8f0;
            selection-background-color:#007a8f;border:1px solid #1e3a4a;}
    """

    def __init__(self,
                 dataset_labels:      list[str],
                 current_colors:      list[str],
                 current_line_styles: list[str],   # matplotlib linestyle strings
                 current_line_widths: list[float],
                 parent=None):
        super().__init__(parent)
        self.setWindowTitle("Dataset Appearance")
        self.setModal(True)
        self.setMinimumWidth(380)
        self.setStyleSheet("""
            QDialog{background:#0d1a26;color:#b0e8f0;}
            QLabel{color:#b0e8f0;font-size:11px;}
            QDialogButtonBox QPushButton{
                background:#0d2a36;border:1px solid #00bcd4;border-radius:5px;
                color:#00e5ff;font-size:11px;padding:4px 18px;min-width:64px;
            }
            QDialogButtonBox QPushButton:hover{background:#00bcd4;color:#000;}
        """)

        # Working copies — modified in place
        self.chosen_colors:      list[str]   = list(current_colors)
        self.chosen_line_styles: list[str]   = list(current_line_styles)
        self.chosen_line_widths: list[float] = list(current_line_widths)

        root = QVBoxLayout(self)
        root.setSpacing(10)
        root.setContentsMargins(16, 14, 16, 10)

        title = QLabel("Dataset Appearance — Line Style · Line Width · Color")
        title.setStyleSheet(
            "color:#3a8a9a;font-size:10px;letter-spacing:1px;"
            "border-bottom:1px solid #1e3a4a;padding-bottom:6px;"
        )
        root.addWidget(title)

        # Column header row
        hdr = QWidget()
        hdr_h = QHBoxLayout(hdr)
        hdr_h.setContentsMargins(0, 0, 0, 0)
        hdr_h.setSpacing(6)
        for txt, w in [("Dataset", 90), ("Line Style", 96), ("Width", 60), ("Color", 90)]:
            lbl = QLabel(txt)
            lbl.setFixedWidth(w)
            lbl.setStyleSheet("color:#3a8a9a;font-size:9px;letter-spacing:1px;")
            hdr_h.addWidget(lbl)
        root.addWidget(hdr)

        # Per-dataset rows
        self._style_combos: list[QComboBox]   = []
        self._width_combos: list[QComboBox]   = []
        self._swatches:     list[QPushButton] = []

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(
            "QScrollArea{border:none;background:transparent;}"
            "QScrollBar:vertical{background:#0d1a26;width:8px;}"
            "QScrollBar::handle:vertical{background:#1e3a4a;border-radius:4px;}"
        )
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(6)
        scroll_layout.setContentsMargins(0, 0, 6, 0)

        for i, label in enumerate(dataset_labels):
            row = QWidget()
            rh  = QHBoxLayout(row)
            rh.setContentsMargins(0, 0, 0, 0)
            rh.setSpacing(6)

            # Dataset label
            ds_lbl = QLabel(label)
            ds_lbl.setFixedWidth(90)
            ds_lbl.setStyleSheet("color:#b0e8f0;font-size:10px;")
            rh.addWidget(ds_lbl)

            # Line Style combo
            style_combo = QComboBox()
            style_combo.setFixedWidth(96)
            style_combo.setFixedHeight(26)
            style_combo.addItems(_LINE_STYLE_LABELS)
            current_label = _LS_TO_LABEL.get(current_line_styles[i], "Solid")
            style_combo.setCurrentText(current_label)
            style_combo.setStyleSheet(self._COMBO_STYLE)
            style_combo.currentTextChanged.connect(
                lambda txt, idx=i: self._on_style_changed(idx, txt)
            )
            rh.addWidget(style_combo)
            self._style_combos.append(style_combo)

            # Line Width combo
            width_combo = QComboBox()
            width_combo.setFixedWidth(60)
            width_combo.setFixedHeight(26)
            width_combo.setEditable(True)
            width_combo.addItems(_LINE_WIDTHS)
            width_combo.setCurrentText(str(current_line_widths[i]))
            width_combo.setStyleSheet(self._COMBO_STYLE)
            width_combo.currentTextChanged.connect(
                lambda txt, idx=i: self._on_width_changed(idx, txt)
            )
            rh.addWidget(width_combo)
            self._width_combos.append(width_combo)

            # Color swatch
            swatch = QPushButton()
            swatch.setFixedHeight(26)
            swatch.setFixedWidth(90)
            self._update_swatch(swatch, current_colors[i])
            swatch.clicked.connect(lambda _, idx=i: self._pick_color(idx))
            rh.addWidget(swatch)
            self._swatches.append(swatch)

            scroll_layout.addWidget(row)

        scroll_area.setWidget(scroll_widget)
        scroll_area.setMaximumHeight(min(len(dataset_labels) * 42 + 16, 320))
        root.addWidget(scroll_area)

        bb = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        root.addWidget(bb)

    # ── slot helpers ──────────────────────────────────────────────────
    def _on_style_changed(self, idx: int, label: str) -> None:
        self.chosen_line_styles[idx] = _LABEL_TO_LS.get(label, "-")

    def _on_width_changed(self, idx: int, text: str) -> None:
        try:
            val = float(text)
            if val > 0:
                self.chosen_line_widths[idx] = val
        except ValueError:
            pass

    def _update_swatch(self, btn: QPushButton, hex_color: str) -> None:
        try:
            r, g, b = mcolors.to_rgb(hex_color)
            luma = 0.299 * r + 0.587 * g + 0.114 * b
            text_color = "#000000" if luma > 0.55 else "#ffffff"
        except Exception:
            text_color = "#ffffff"
        btn.setStyleSheet(
            f"background:{hex_color};color:{text_color};"
            + self._SWATCH_STYLE
        )
        btn.setText(hex_color.upper())

    def _pick_color(self, idx: int) -> None:
        initial = QColor(self.chosen_colors[idx])
        picked  = QColorDialog.getColor(
            initial, self,
            f"Choose colour for {self._swatches[idx].text()}",
            QColorDialog.ColorDialogOption.ShowAlphaChannel,
        )
        if picked.isValid():
            hex_c = picked.name()
            self.chosen_colors[idx] = hex_c
            self._update_swatch(self._swatches[idx], hex_c)


# ── Custom NavigationToolbar ──────────────────────────────────────────────────

class _SemiContactToolbar(NavigationToolbar):
    """
    Subclass of NavigationToolbar2QT that replaces matplotlib's built-in
    'Edit curves lines and axes parameters' dialog with our own
    DatasetColorDialog.  Every other toolbar action is untouched.
    """

    def __init__(self, canvas, parent, plot_canvas_ref):
        super().__init__(canvas, parent)
        # Back-reference to the owning PlotCanvas so we can read/write colors
        self._plot_canvas = plot_canvas_ref

    def edit_parameters(self):
        """Called when the user clicks the ✎ (Edit) toolbar button."""
        pc = self._plot_canvas
        if pc._session is None:
            return  # nothing to edit yet

        # Build label + current-property lists for active datasets only
        labels:      list[str]   = []
        colors:      list[str]   = []
        line_styles: list[str]   = []
        line_widths: list[float] = []
        ds_indices:  list[int]   = []
        for idx, ds in enumerate(pc._session.datasets):
            if any(pt.Rnew is not None for pt in ds.points):
                labels.append(ds.label or f"DS{idx + 1}")
                colors.append(pc._get_dataset_color(idx))
                line_styles.append(pc._get_dataset_line_style(idx))
                line_widths.append(pc._get_dataset_line_width(idx))
                ds_indices.append(idx)

        if not labels:
            return

        dlg = DatasetAppearanceDialog(
            labels, colors, line_styles, line_widths, parent=self.parent()
        )
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        # Write chosen values back and redraw immediately — no Analyze needed
        changed = False
        for list_pos, ds_idx in enumerate(ds_indices):
            new_color = dlg.chosen_colors[list_pos]
            new_style = dlg.chosen_line_styles[list_pos]
            new_width = dlg.chosen_line_widths[list_pos]

            if new_color != pc._get_dataset_color(ds_idx):
                pc._dataset_colors[ds_idx] = new_color
                changed = True
            if new_style != pc._get_dataset_line_style(ds_idx):
                pc._dataset_line_styles[ds_idx] = new_style
                changed = True
            if new_width != pc._get_dataset_line_width(ds_idx):
                pc._dataset_line_widths[ds_idx] = new_width
                changed = True

        if changed:
            pc.update_plot(pc._session)


# ── PlotCanvas ────────────────────────────────────────────────────────────────

class PlotCanvas(QWidget):
    """Self-contained scientific plot canvas with unified dataset colours."""

    def __init__(self, mode: str, parent=None):
        super().__init__(parent)
        self._mode           = mode
        self._session        = None
        self._show_deviation = False
        self._show_markers   = True
        self._tick_interval  = None
        # ── Unified colour store: dataset-index → hex string ──────────
        # Seeded lazily from DATASET_COLORS; persists across re-plots so
        # that any colour chosen via DatasetColorDialog is remembered.
        self._dataset_colors: dict[int, str] = {}
        # ── Per-dataset line style / width — seeded lazily on first access
        self._dataset_line_styles: dict[int, str] = {}   # matplotlib linestyle string
        self._dataset_line_widths: dict[int, float] = {} # float pt width
        self._build_ui()

    # ── Unified colour access ─────────────────────────────────────────
    def _get_dataset_color(self, idx: int) -> str:
        """Return the authoritative colour for dataset *idx*, seeding the
        default palette on first access."""
        if idx not in self._dataset_colors:
            self._dataset_colors[idx] = DATASET_COLORS[idx % len(DATASET_COLORS)]
        return self._dataset_colors[idx]

    def set_dataset_colors(self, color_map: dict[int, str]) -> None:
        """Bulk-update colours and redraw.  Keys are zero-based dataset indices."""
        self._dataset_colors.update(color_map)
        if self._session is not None:
            self.update_plot(self._session)

    def _get_dataset_line_style(self, idx: int) -> str:
        """Return the authoritative linestyle for dataset *idx* (default solid)."""
        if idx not in self._dataset_line_styles:
            self._dataset_line_styles[idx] = "-"
        return self._dataset_line_styles[idx]

    def _get_dataset_line_width(self, idx: int) -> float:
        """Return the authoritative line width for dataset *idx* (default 1.6)."""
        if idx not in self._dataset_line_widths:
            self._dataset_line_widths[idx] = 1.6
        return self._dataset_line_widths[idx]

    # ── UI ────────────────────────────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        toolbar_row = QWidget()
        toolbar_row.setStyleSheet("background:#0b131d;border-bottom:1px solid #1e3a4a;")
        tr = QHBoxLayout(toolbar_row)
        tr.setContentsMargins(6, 3, 6, 3)
        tr.setSpacing(8)

        self.fig    = Figure(figsize=(8, 5), dpi=100)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setStyleSheet("background-color:#090e14;")

        # Use our custom toolbar so the ✎ button opens DatasetColorDialog
        self.mpl_toolbar = _SemiContactToolbar(self.canvas, self,
                                               plot_canvas_ref=self)
        self.mpl_toolbar.setStyleSheet("""
            QToolBar{background:#0b131d;border:none;spacing:3px;padding:1px 4px;}
            QToolButton{background:#0d2030;border:1px solid #1e3a4a;border-radius:4px;
                color:#00bcd4;padding:2px 5px;}
            QToolButton:hover{background:#00bcd4;color:#000;}
            QToolButton:checked{background:#007a8f;color:#fff;}
        """)
        tr.addWidget(self.mpl_toolbar)
        tr.addStretch()

        # Deviation
        dev_lbl = QLabel("Residual View  ")
        dev_lbl.setStyleSheet("color:#1e5a6a;font-size:10px;letter-spacing:1px;")
        tr.addWidget(dev_lbl)
        self._dev_btn = _toolbar_btn("  Show Deviation  ", checkable=True)
        self._dev_btn.toggled.connect(self._on_deviation_toggled)
        tr.addWidget(self._dev_btn)

        # Item 2 — Hide Markers
        self._marker_btn = _toolbar_btn("  Hide Markers  ", checkable=True)
        self._marker_btn.toggled.connect(self._on_markers_toggled)
        tr.addWidget(self._marker_btn)

        # Scale
        scale_lbl = QLabel("  Scale:")
        scale_lbl.setStyleSheet("color:#3a7a8a;font-size:10px;")
        tr.addWidget(scale_lbl)

        self._scale_combo = QComboBox()
        self._scale_combo.setFixedHeight(26)
        self._scale_combo.setFixedWidth(80)
        self._scale_combo.addItems(["Auto", "5", "10", "20", "Custom"])
        self._scale_combo.setStyleSheet("""
            QComboBox{background:#0d2030;border:1px solid #3a5a6a;border-radius:4px;
                color:#b0e8f0;font-size:10px;padding:1px 6px;}
            QComboBox:hover{border-color:#00bcd4;}
            QComboBox QAbstractItemView{background:#0d2030;color:#b0e8f0;
                selection-background-color:#007a8f;border:1px solid #1e3a4a;}
        """)
        self._scale_combo.currentTextChanged.connect(self._on_scale_changed)
        tr.addWidget(self._scale_combo)

        self._custom_scale = QLineEdit()
        self._custom_scale.setFixedSize(52, 26)
        self._custom_scale.setPlaceholderText("e.g. 4")
        self._custom_scale.setVisible(False)
        self._custom_scale.setStyleSheet("""
            QLineEdit{background:#0d2030;border:1px solid #3a5a6a;border-radius:4px;
                color:#b0e8f0;font-size:10px;padding:1px 5px;}
            QLineEdit:focus{border-color:#00bcd4;}
        """)
        self._custom_scale.returnPressed.connect(self._apply_custom_scale)
        tr.addWidget(self._custom_scale)

        root.addWidget(toolbar_row)
        root.addWidget(self.canvas)

        self._reset_axes(deviation=False)
        self._draw_placeholder()

    # ── Axes reset ────────────────────────────────────────────────────
    def _reset_axes(self, deviation: bool):
        self.fig.clf()
        if deviation:
            gs = GridSpec(
                2, 1, height_ratios=[3, 1], hspace=0.42,
                figure=self.fig,
                top=0.92, bottom=0.12, left=0.09, right=0.97,
            )
            self.ax     = self.fig.add_subplot(gs[0])
            self.ax_res = self.fig.add_subplot(gs[1], sharex=self.ax)
            _apply_dark_style(self.fig, [self.ax, self.ax_res])
        else:
            self.ax = self.fig.add_subplot(111)
            self.fig.subplots_adjust(top=0.92, bottom=0.11, left=0.09, right=0.97)
            self.ax_res = None
            _apply_dark_style(self.fig, [self.ax])

    # ── Toggles ───────────────────────────────────────────────────────
    def _on_deviation_toggled(self, checked: bool):
        self._show_deviation = checked
        self._dev_btn.setText("  Hide Deviation  " if checked else "  Show Deviation  ")
        if self._session is not None:
            self.update_plot(self._session)
        else:
            self._reset_axes(checked)
            self._draw_placeholder()

    def _on_markers_toggled(self, checked: bool):
        """Item 2 — hide/show scatter markers live."""
        self._show_markers = not checked
        self._marker_btn.setText("  Show Markers  " if checked else "  Hide Markers  ")
        if self._session is not None:
            self.update_plot(self._session)

    # ── Scale ─────────────────────────────────────────────────────────
    def _on_scale_changed(self, text: str):
        if text == "Custom":
            self._custom_scale.setVisible(True)
            self._custom_scale.setFocus()
            return
        self._custom_scale.setVisible(False)
        try:
            self._tick_interval = None if text == "Auto" else float(text)
        except ValueError:
            self._tick_interval = None
        if self._session is not None:
            self.update_plot(self._session)

    def _apply_custom_scale(self):
        try:
            val = float(self._custom_scale.text().strip())
            if val > 0:
                self._tick_interval = val
                if self._session is not None:
                    self.update_plot(self._session)
        except ValueError:
            pass

    def _apply_tick_interval(self):
        if self._tick_interval is None:
            return
        import matplotlib.ticker as ticker
        self.ax.xaxis.set_major_locator(ticker.MultipleLocator(self._tick_interval))
        self.ax.yaxis.set_major_locator(ticker.MultipleLocator(self._tick_interval))
        if self.ax_res is not None:
            self.ax_res.xaxis.set_major_locator(ticker.MultipleLocator(self._tick_interval))

    # ── Main plot renderer ────────────────────────────────────────────
    def update_plot(self, session: AnalysisSession) -> None:
        self._session = session
        self._reset_axes(self._show_deviation)
        _apply_dark_style(
            self.fig, [self.ax] + ([self.ax_res] if self.ax_res else [])
        )

        has_data = False

        for idx, ds in enumerate(session.datasets):
            # ── Single authoritative colour for this dataset ───────────
            color = self._get_dataset_color(idx)
            spec  = get_marker(idx)
            valid = [(pt.d, pt.Rnew) for pt in ds.points if pt.Rnew is not None]
            if not valid:
                continue

            has_data = True
            xs = np.array([v[0] for v in valid])
            ys = np.array([v[1] for v in valid])

            # Scatter — face, edge, and visibility all derived from color
            scatter_cfg = scatter_kwargs(idx, color, visible=self._show_markers)
            self.ax.scatter(xs, ys, **scatter_cfg, label=ds.label)

            if ds.converged and ds.slope is not None:
                x_min = xs.min() * 0.85
                x_max = xs.max() * 1.08
                xf    = np.linspace(x_min, x_max, 200)
                yf    = ds.slope * xf + ds.intercept

                self.ax.plot(
                    xf, yf, color=color,
                    linewidth=self._get_dataset_line_width(idx),
                    linestyle=self._get_dataset_line_style(idx),
                    alpha=0.85, zorder=4,
                )

                # ── Deviation / residual ───────────────────────────────
                if self._show_deviation:
                    y_fit_at_x = ds.slope * xs + ds.intercept
                    residuals  = ys - y_fit_at_x

                    if self._show_markers:
                        for xi, yi, fi in zip(xs, ys, y_fit_at_x):
                            self.ax.plot(
                                [xi, xi], [fi, yi],
                                color=color, alpha=0.4,
                                linewidth=1.0, linestyle=":", zorder=3,
                            )

                    if self.ax_res is not None:
                        sort_idx = np.argsort(xs)
                        xs_s     = xs[sort_idx]
                        res_s    = residuals[sort_idx]

                        if len(xs_s) >= 4:
                            from scipy.interpolate import make_interp_spline
                            x_dense = np.linspace(xs_s[0], xs_s[-1], 300)
                            spl     = make_interp_spline(xs_s, res_s, k=3)
                            self.ax_res.plot(
                                x_dense, spl(x_dense),
                                color=color, linewidth=1.5, alpha=0.9, zorder=4,
                            )
                        else:
                            self.ax_res.plot(
                                xs_s, res_s,
                                color=color, linewidth=1.5, alpha=0.9, zorder=4,
                            )

                        if self._show_markers:
                            self.ax_res.scatter(
                                xs_s, res_s,
                                marker=spec.code,
                                s=max(spec.scatter_s * 0.5, 20),
                                color=color, zorder=5,
                                edgecolors=color, linewidths=0.4,
                            )

                        self.ax_res.axhline(
                            0, color="#3a5a6a", linewidth=0.8, linestyle="-",
                        )

        if not has_data:
            self._draw_placeholder()
            self.canvas.draw()
            return

        # ── Labels ────────────────────────────────────────────────────
        if self._show_deviation:
            self.ax.tick_params(labelbottom=False)
            self.ax.set_xlabel("")
        else:
            self.ax.set_xlabel("Spacing  d  (\u03bcm)", fontsize=10, labelpad=8)

        self.ax.set_ylabel("Resistance  R\u2099  (\u03a9)", fontsize=10, labelpad=8)
        self.ax.set_title(
            f"SemiContact Pro \u2014 {self._mode} Analysis",
            fontsize=12, fontweight="bold", pad=10,
        )

        # ── Legend — one Line2D per dataset, colour from _dataset_colors
        legend_handles = []
        for idx, ds in enumerate(session.datasets):
            if not any(pt.Rnew is not None for pt in ds.points):
                continue
            color = self._get_dataset_color(idx)
            spec  = get_marker(idx)
            handle = Line2D(
                [0], [0],
                color=color,
                marker=spec.code,
                linestyle=self._get_dataset_line_style(idx),
                linewidth=self._get_dataset_line_width(idx),
                markersize=spec.line_ms,
                markerfacecolor=color,
                markeredgecolor=color,
                markeredgewidth=0.5,
                label=ds.label,
            )
            legend_handles.append(handle)

        if legend_handles:
            self.ax.legend(
                handles=legend_handles,
                loc="upper left", fontsize=8, framealpha=0.3,
                facecolor="#0b131d", edgecolor="#1e3a4a", labelcolor="#b0e8f0",
            )

        if self.ax_res is not None:
            self.ax_res.set_xlabel("Spacing  d  (\u03bcm)", fontsize=9, labelpad=6)
            self.ax_res.set_ylabel("Residual (\u03a9)", fontsize=8, labelpad=4)
            self.ax_res.tick_params(labelsize=8)

        self._apply_tick_interval()
        self.canvas.draw()

    # ── Public getters ────────────────────────────────────────────────
    def get_figure(self) -> Figure:
        """Return the live figure — export code MUST deep-copy before styling."""
        return self.fig

    def get_show_markers(self) -> bool:
        return self._show_markers

    def get_show_deviation(self) -> bool:
        return self._show_deviation

    # ── Placeholder ───────────────────────────────────────────────────
    def _draw_placeholder(self):
        self.ax.cla()
        _apply_dark_style(self.fig, [self.ax])
        self.ax.text(
            0.5, 0.5,
            "Enter data and click  \u26a1 Analyze  to render graph",
            ha="center", va="center", transform=self.ax.transAxes,
            fontsize=12, color="#1e5a6a",
        )
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        if self.ax_res:
            self.ax_res.cla()
            _apply_dark_style(self.fig, [self.ax_res])
            self.ax_res.set_xticks([])
            self.ax_res.set_yticks([])
        self.canvas.draw()