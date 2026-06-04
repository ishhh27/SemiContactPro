"""
SemiContact Pro — Data models shared across CTLM and LTLM modules.
"""

from dataclasses import dataclass, field
from typing import Optional


# Fixed gap spacings used across both methods
D_VALUES = [4, 8, 12, 24, 32, 40]

# CTLM correction factors keyed by d
CTLM_CF = {
    4:  0.96,
    8:  0.93,
    12: 0.90,
    24: 0.82,
    32: 0.77,
    40: 0.73,
}


@dataclass
class DataPoint:
    """One (d, R) measurement pair with derived Rnew."""
    d: float
    R: Optional[float]      # raw resistance (None = invalid/empty)
    Rp: float               # probe resistance for this dataset
    CF: Optional[float]     # correction factor (CTLM only, else None)
    Rnew: Optional[float]   # corrected resistance (None if R is None)


@dataclass
class Dataset:
    """One dataset (one colour on the graph, one set of outputs)."""
    label: str
    Rp: float
    W: Optional[float]      # width (LTLM only)
    points: list[DataPoint] = field(default_factory=list)

    # Regression results — populated after fit()
    slope:      Optional[float] = None
    intercept:  Optional[float] = None
    r_squared:  Optional[float] = None
    converged:  bool = False

    # Derived parameters
    Rc:   Optional[float] = None
    RSH:  Optional[float] = None
    LT:   Optional[float] = None
    FOM:  Optional[float] = None


@dataclass
class AnalysisSession:
    """Top-level session container (wafer + product + list of datasets)."""
    wafer_number: str = ""
    product_id:   str = ""
    mode:         str = ""          # "CTLM" or "LTLM"
    datasets:     list[Dataset] = field(default_factory=list)
