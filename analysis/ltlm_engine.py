"""
SemiContact Pro — LTLM / TLM Analysis Engine
Linear Transmission Line Method (no correction factors).
"""

import numpy as np
from scipy import stats
from typing import Optional

from .models import (
    Dataset, DataPoint, AnalysisSession,
    D_VALUES
)


def build_ltlm_dataset(
    label: str,
    Rp: float,
    W: float,
    raw_R: dict[int, Optional[float]],   # {d: R or None}
) -> Dataset:
    """
    Build a Dataset from raw user inputs for LTLM.

    For each valid point: Rnew = R - Rp
    No correction factor is applied.
    """
    ds = Dataset(label=label, Rp=Rp, W=W)

    for d in D_VALUES:
        R = raw_R.get(d)
        if R is None:
            ds.points.append(DataPoint(d=d, R=None, Rp=Rp, CF=None, Rnew=None))
        else:
            Rnew = R - Rp
            ds.points.append(DataPoint(d=d, R=R, Rp=Rp, CF=None, Rnew=Rnew))

    return ds


def fit_ltlm_dataset(ds: Dataset) -> Dataset:
    """
    Run linear regression on valid (d, Rnew) pairs.

    LTLM outputs (per reference — Linear TLM column):
        slope  m   — from regression          [ m = Rsh / W ]
        intercept b — from regression         [ b = 2·Rc ]
        Rc         = b / 2                    [ contact resistance, Ω ]
        RSH        = m × W                    [ sheet resistance, Ω/sq ]
        LT         = b / 2m   [ transfer length, µm ]
        FOM        = (LT x m × W) / 1000                 [ normalised transfer length ]
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

    # Derived parameters — Linear TLM (reference image, LTLM column)
    # m  = Rsh / W          =>  Rsh = m × W
    # b  = 2·Rc             =>  Rc  = b / 2
    # # LT = (Rc × W) / Rsh         
    # FOM = (LT x m × W) / 1000                 [ normalised transfer length ]
    W = ds.W if ds.W and ds.W != 0 else 1.0
    ds.Rc  = ds.intercept / 2.0
    ds.RSH = ds.slope * W
    if ds.RSH != 0:
        ds.LT = (ds.Rc * W) / ds.RSH
    else:
        ds.LT = None
    if ds.LT is not None:
        ds.FOM = (ds.LT * ds.slope * W) / 1000
    else:
        ds.FOM = None

    return ds


def run_ltlm_session(session: AnalysisSession) -> AnalysisSession:
    """Fit every dataset in the session in-place."""
    for i, ds in enumerate(session.datasets):
        session.datasets[i] = fit_ltlm_dataset(ds)
    return session