"""
SemiContact Pro — CTLM Analysis Engine
Circular Transmission Line Method with correction factors.
"""

import numpy as np
from scipy import stats
from typing import Optional

from .models import (
    Dataset, DataPoint, AnalysisSession,
    D_VALUES, CTLM_CF
)


def build_ctlm_dataset(
    label: str,
    Rp: float,
    raw_R: dict[int, Optional[float]],   # {d: R or None}
) -> Dataset:
    """
    Build a Dataset from raw user inputs for CTLM.

    raw_R: mapping of d → R value (or None if blank).
    For each valid point: Rnew = (R - Rp) / CF(d)
    """
    ds = Dataset(label=label, Rp=Rp, W=None)

    for d in D_VALUES:
        R = raw_R.get(d)
        cf = CTLM_CF[d]
        if R is None:
            ds.points.append(DataPoint(d=d, R=None, Rp=Rp, CF=cf, Rnew=None))
        else:
            Rnew = (R - Rp) / cf
            ds.points.append(DataPoint(d=d, R=R, Rp=Rp, CF=cf, Rnew=Rnew))

    return ds


def fit_ctlm_dataset(ds: Dataset) -> Dataset:
    """
    Run linear regression on valid (d, Rnew) pairs.

    CTLM outputs:
        slope      — from regression
        intercept  — from regression
        RSH        = slope × 314
        LT         = intercept / (2 × slope)
        Rc         = intercept / 2
        FOM        = Rc × 0.314
        R²         — coefficient of determination
    """
    valid = [(pt.d, pt.Rnew) for pt in ds.points if pt.Rnew is not None]

    if len(valid) < 2:
        ds.converged = False
        return ds

    x = np.array([v[0] for v in valid], dtype=float)
    y = np.array([v[1] for v in valid], dtype=float)

    result = stats.linregress(x, y)
    ds.slope      = float(result.slope)
    ds.intercept  = float(result.intercept)
    ds.r_squared  = float(result.rvalue ** 2)
    ds.converged  = True

    # Derived parameters
    ds.RSH = ds.slope * 314.0
    ds.Rc  = ds.intercept / 2.0
    if ds.slope != 0:
        ds.LT = ds.intercept / (2.0 * ds.slope)
    else:
        ds.LT = None
    ds.FOM = ds.Rc * 0.314

    return ds


def run_ctlm_session(session: AnalysisSession) -> AnalysisSession:
    """Fit every dataset in the session in-place."""
    for i, ds in enumerate(session.datasets):
        session.datasets[i] = fit_ctlm_dataset(ds)
    return session
