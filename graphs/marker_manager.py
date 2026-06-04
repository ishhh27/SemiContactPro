"""
SemiContact Pro — Marker Manager
Centralised, single-source-of-truth for dataset marker shapes and sizes.

Each of the 8 datasets has a fixed marker style that is used identically on:
  - main graph scatter points
  - residual subplot scatter points
  - legends
  - exported PNG
  - exported PDF copies

Marker sizes are normalised so visually 'large' glyphs (star, X) don't
overwhelm smaller ones (circle, square).
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class MarkerSpec:
    """One dataset's complete marker specification."""
    code:     str    # matplotlib marker code
    scatter_s: int   # size for ax.scatter(s=...)
    line_ms:  float  # size for ax.plot(markersize=...)  — used in legends
    label:    str    # human-readable name for debugging


# ── Canonical mapping DS1–DS8 ─────────────────────────────────────────────────
# Sizes are tuned so all markers appear visually balanced at roughly the same
# perceived footprint.  Star (*) and X are inherently 'open' so get a size
# boost; pentagon (P) and diamond (D) get a slight reduction.

_MARKER_SPECS: list[MarkerSpec] = [
    MarkerSpec("o", scatter_s=55, line_ms=7,   label="circle"),        # DS1
    MarkerSpec("s", scatter_s=50, line_ms=6,   label="square"),        # DS2
    MarkerSpec("^", scatter_s=55, line_ms=7,   label="triangle_up"),   # DS3
    MarkerSpec("D", scatter_s=45, line_ms=6,   label="diamond"),       # DS4
    MarkerSpec("P", scatter_s=50, line_ms=6,   label="pentagon"),      # DS5
    MarkerSpec("X", scatter_s=55, line_ms=7,   label="x_filled"),      # DS6
    MarkerSpec("*", scatter_s=70, line_ms=9,   label="star"),          # DS7
    MarkerSpec("v", scatter_s=55, line_ms=7,   label="triangle_down"), # DS8
]


def get_marker(dataset_index: int) -> MarkerSpec:
    """
    Return the MarkerSpec for a dataset by zero-based index.
    Cycles safely if index >= 8 (future-proof).
    """
    return _MARKER_SPECS[dataset_index % len(_MARKER_SPECS)]


def scatter_kwargs(dataset_index: int, color: str,
                   visible: bool = True) -> dict:
    """
    Return a ready-to-unpack kwargs dict for ax.scatter().
    Pass visible=False to produce invisible (alpha=0) markers that still
    reserve legend space (used by the Hide Markers toggle).

    Both face colour and edge colour are set to the single dataset colour so
    the unified-colour system is honoured throughout.
    """
    spec = get_marker(dataset_index)
    return {
        "marker":      spec.code,
        "s":           spec.scatter_s,
        "color":       color,
        "edgecolors":  color if visible else "#00000000",
        "linewidths":  0.5,
        "zorder":      5,
        "alpha":       1.0 if visible else 0.0,
    }


def legend_handle_kwargs(dataset_index: int, color: str) -> dict:
    """
    Return kwargs that produce a correctly-shaped legend entry when used
    with ax.scatter(..., label=...).  The legend picks up marker + color
    automatically, so this is just a convenience reference.
    """
    spec = get_marker(dataset_index)
    return {"marker": spec.code, "color": color, "s": spec.scatter_s}