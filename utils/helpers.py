"""
SemiContact Pro — Utility helpers.
"""

from typing import Optional


def fmt(value: Optional[float], decimals: int = 2, unit: str = "") -> str:
    """Format a float for display; returns '—' for None.
    Always shows 2 decimal places for displayed/exported values.
    Pass decimals > 2 only when higher precision is intentionally needed.
    """
    if value is None:
        return "—"
    text = f"{value:.{decimals}f}"
    if unit:
        text += f"  {unit}"
    return text


def safe_float(text: str) -> Optional[float]:
    """Convert a string to float; return None on failure."""
    try:
        return float(text.strip())
    except (ValueError, AttributeError):
        return None