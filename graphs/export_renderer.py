"""
SemiContact Pro — Export Renderer  (v8.2)

Design rules:
  • Live figure is NEVER modified — always deep-copy first.
  • PNG export keeps the dark theme exactly as shown on screen.
  • PDF export:
      - remaps default neon dataset colours → publication-friendly palette
      - user-chosen custom colours are preserved as-is
      - sets white background, dark-grey axes/text, subtle grid
      - all artists for a dataset (line, scatter, legend) share one colour
  • Marker visibility state is honoured in both modes.
"""

import copy
import io
import matplotlib
import matplotlib.colors as mcolors
matplotlib.use("Agg")

from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.backend_bases import FigureCanvasBase
from matplotlib.lines import Line2D
from matplotlib.collections import PathCollection

from graphs.marker_manager import get_marker

# ── In-app neon palette (source) — must stay in sync with plot_canvas ────────
SCREEN_COLORS = [
    "#00e5ff", "#00ffa0", "#ff6b6b", "#ffd93d",
    "#c77dff", "#ff9f43", "#48dbfb", "#ff9ff3",
]

# ── Publication palette (target for PDF) ─────────────────────────────────────
EXPORT_COLORS = [
    "#1565C0",  # DS1 deep blue
    "#00838F",  # DS2 dark cyan
    "#C62828",  # DS3 crimson
    "#2E7D32",  # DS4 forest green
    "#EF6C00",  # DS5 dark orange
    "#6A1B9A",  # DS6 purple
    "#37474F",  # DS7 dark slate
    "#8E2430",  # DS8 maroon
]


def _screen_to_export_color(screen_color: str) -> str:
    """
    Map a screen colour to its publication equivalent.
    Default palette colours are remapped; user-chosen custom colours pass
    through unchanged so the user's selection is preserved in the export.
    """
    try:
        idx = SCREEN_COLORS.index(screen_color.lower())
        return EXPORT_COLORS[idx]
    except ValueError:
        return screen_color          # custom colour — preserve as-is


# ── Theme appliers ────────────────────────────────────────────────────────────

def _apply_dark_style(fig: Figure) -> None:
    """Restore dark theme on a copy (used for PNG export)."""
    fig.patch.set_facecolor("#090e14")
    for ax in fig.get_axes():
        ax.set_facecolor("#0b131d")
        for sp in ax.spines.values():
            sp.set_color("#1e3a4a")
        ax.tick_params(colors="#3a8a9a", labelsize=9)
        ax.xaxis.label.set_color("#b0e8f0")
        ax.yaxis.label.set_color("#b0e8f0")
        ax.title.set_color("#00e5ff")
        ax.grid(True, color="#1e3a4a", linestyle="--", linewidth=0.6, alpha=0.7)


def _apply_light_style(fig: Figure) -> None:
    """Apply clean white/grey scientific theme for PDF export."""
    fig.patch.set_facecolor("white")
    for ax in fig.get_axes():
        ax.set_facecolor("white")
        for sp in ax.spines.values():
            sp.set_color("#555555")
        ax.tick_params(colors="#333333", labelsize=9)
        ax.xaxis.label.set_color("#111111")
        ax.yaxis.label.set_color("#111111")
        ax.title.set_color("#111111")
        ax.grid(True, color="#dddddd", linestyle="--", linewidth=0.5)


def _remap_colors_for_export(
    fig: Figure,
    show_markers: bool,
    bw_mode: bool = True,   # kept for call-site compatibility; not used internally
) -> None:
    """
    Walk every artist on the copied figure and replace default neon screen
    colours with their publication-palette equivalents.  User-chosen custom
    colours are left unchanged.

    Colour pairing strategy
    -----------------------
    Each dataset contributes exactly one dashed fit Line2D to ax (in dataset
    order) and exactly one PathCollection (scatter) also in dataset order.
    After remapping line colours we assign the same remapped colour to the
    matching scatter collection, so every visual element for a dataset shares
    one colour — matching the unified-colour contract of plot_canvas.

    Handles:
      • Line2D          (fit lines, residual curves, stem lines)
      • PathCollection  (scatter markers)
      • Line2D legend handles
    """
    for ax in fig.get_axes():

        # ── Step 1: remap all Line2D colours ─────────────────────────
        # Collect fit lines (dashed) in draw order to correlate with scatter.
        fit_line_colors: list[str] = []

        for line in ax.get_lines():
            c = line.get_color()
            try:
                hex_c = mcolors.to_hex(c)
                new_c = _screen_to_export_color(hex_c)
            except Exception:
                new_c = c
            line.set_color(new_c)
            # Sync any marker glyphs on the line itself
            line.set_markerfacecolor(new_c)
            line.set_markeredgecolor(new_c)
            line.set_fillstyle("full")
            line.set_markeredgewidth(0.8)

            if line.get_linestyle() in ("--", "dashed"):
                fit_line_colors.append(new_c)

        # ── Step 2: apply remapped colour to matching scatter collections
        scatter_colls = [a for a in ax.collections
                         if isinstance(a, PathCollection)]

        for i, coll in enumerate(scatter_colls):
            if not show_markers:
                coll.set_alpha(0.0)
                continue

            coll.set_alpha(1.0)

            # Pair with the fit line at the same position when available;
            # otherwise remap from the collection's own stored face colour.
            if i < len(fit_line_colors):
                dataset_color = fit_line_colors[i]
            else:
                try:
                    fc = coll.get_facecolor()
                    hex_c = mcolors.to_hex(fc[0]) if fc is not None and len(fc) else "#333333"
                    dataset_color = _screen_to_export_color(hex_c)
                except Exception:
                    dataset_color = "#333333"

            coll.set_facecolor(dataset_color)
            coll.set_edgecolor(dataset_color)

        # ── Step 3: legend ────────────────────────────────────────────
        legend = ax.get_legend()
        if legend is not None:
            legend.get_frame().set_facecolor("white")
            legend.get_frame().set_edgecolor("#bbbbbb")
            for text in legend.get_texts():
                text.set_color("#111111")
            for handle in legend.legend_handles:
                if isinstance(handle, Line2D):
                    c = handle.get_color()
                    try:
                        hex_c = mcolors.to_hex(c)
                        new_c = _screen_to_export_color(hex_c)
                    except Exception:
                        new_c = c
                    handle.set_color(new_c)
                    handle.set_markerfacecolor(new_c)
                    handle.set_markeredgecolor(new_c)
                    handle.set_alpha(1.0)   # always show in legend


# ── Core deep-copy renderer ───────────────────────────────────────────────────

def render_for_export(
    live_fig: Figure,
    bw: bool = True,
    show_markers: bool = True,
) -> Figure:
    """
    Deep-copy the live figure and apply export styling.

    Args:
        live_fig:     PlotCanvas.fig — NEVER modified.
        bw:           True → light theme + publication colours (PDF).
                      False → dark theme preserved (PNG).
        show_markers: Mirror the app's current marker-visibility toggle.

    Returns:
        A standalone Figure safe to save/close freely.
    """
    # ── Safe deep-copy ────────────────────────────────────────────────
    # The live figure is attached to a PyQt canvas which is not safely
    # deepcopy-able (it holds C++ widget state).  Calling
    # FigureCanvasAgg(fig_copy) AFTER a broken deepcopy does not recover
    # the lost artists — it only re-attaches a canvas to whatever partial
    # state survived the copy.
    #
    # Fix: temporarily swap the live canvas for a lightweight
    # FigureCanvasBase (plain Python, deepcopy-safe), perform the copy,
    # then immediately restore the original canvas on the live figure and
    # attach a fresh FigureCanvasAgg to the copy.  All axes, lines,
    # scatter collections, and legend entries are preserved intact.
    orig_canvas = live_fig.canvas
    live_fig.set_canvas(FigureCanvasBase(live_fig))   # swap to safe placeholder
    try:
        fig_copy: Figure = copy.deepcopy(live_fig)
    finally:
        live_fig.set_canvas(orig_canvas)              # always restore live canvas

    FigureCanvasAgg(fig_copy)   # attach headless Agg canvas to the copy

    if bw:
        _apply_light_style(fig_copy)
        _remap_colors_for_export(fig_copy, show_markers=show_markers, bw_mode=bw)
    else:
        _apply_dark_style(fig_copy)
        if not show_markers:
            for ax in fig_copy.get_axes():
                for coll in ax.collections:
                    if isinstance(coll, PathCollection):
                        coll.set_alpha(0.0)

    return fig_copy


def fig_to_png_bytes(fig: Figure, dpi: int = 150) -> io.BytesIO:
    """Render a Figure to PNG bytes in memory (for embedding in PDF)."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi,
                bbox_inches="tight", facecolor=fig.get_facecolor())
    buf.seek(0)
    return buf