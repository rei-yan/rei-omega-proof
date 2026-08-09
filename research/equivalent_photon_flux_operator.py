#!/usr/bin/env python3
"""Domain-scoped Equivalent Photon Approximation flux evaluator.

This is a scientific helper, not a universal REI update rule and not an
external-validation gate.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class FluxResult:
    status: str
    density_per_x: Optional[float]
    bracket: Optional[float]
    reason: str


def equivalent_photon_density(*, Z: float, alpha: float, x: float, u: float) -> FluxResult:
    values = (Z, alpha, x, u)
    if not all(math.isfinite(v) for v in values):
        return FluxResult("INVALID_INPUT", None, None, "all parameters must be finite")
    if Z <= 0:
        return FluxResult("INVALID_INPUT", None, None, "Z must be positive")
    if alpha <= 0:
        return FluxResult("INVALID_INPUT", None, None, "alpha must be positive")
    if not (0 < x < 1):
        return FluxResult("INVALID_INPUT", None, None, "x must satisfy 0 < x < 1")
    if u <= 0:
        return FluxResult("INVALID_INPUT", None, None, "u must be positive and externally specified")

    bracket = math.log(u / x) - 0.5
    if bracket <= 0:
        return FluxResult(
            "ABSTAIN_OUTSIDE_APPROXIMATION",
            None,
            bracket,
            "logarithmic EPA bracket is non-positive; do not emit negative flux",
        )

    density = (2.0 * Z * Z * alpha / (math.pi * x)) * bracket
    return FluxResult(
        "SUPPORTED_DOMAIN_EVALUATION",
        density,
        bracket,
        "EPA formula evaluated within the explicit domain guard",
    )


def charge_scaling_ratio(Z1: float, Z2: float) -> float:
    """Return the local Z^2 scaling ratio for fixed x, u, alpha."""
    if not (math.isfinite(Z1) and math.isfinite(Z2)) or Z1 <= 0 or Z2 <= 0:
        raise ValueError("charges must be positive finite values")
    return (Z2 / Z1) ** 2


def _sanity() -> None:
    alpha = 1.0 / 137.035999084
    good = equivalent_photon_density(Z=82, alpha=alpha, x=1e-3, u=0.2)
    assert good.status == "SUPPORTED_DOMAIN_EVALUATION"
    assert good.density_per_x is not None and good.density_per_x > 0

    # The local charge scaling is exactly quadratic when all other model inputs are frozen.
    low = equivalent_photon_density(Z=10, alpha=alpha, x=1e-3, u=0.2)
    high = equivalent_photon_density(Z=20, alpha=alpha, x=1e-3, u=0.2)
    assert low.density_per_x is not None and high.density_per_x is not None
    assert math.isclose(high.density_per_x / low.density_per_x, 4.0, rel_tol=1e-12)
    assert math.isclose(charge_scaling_ratio(10, 20), 4.0, rel_tol=1e-12)

    outside = equivalent_photon_density(Z=82, alpha=alpha, x=0.2, u=0.2)
    assert outside.status == "ABSTAIN_OUTSIDE_APPROXIMATION"
    assert outside.density_per_x is None

    invalid = equivalent_photon_density(Z=0, alpha=alpha, x=1e-3, u=0.2)
    assert invalid.status == "INVALID_INPUT"

    print("EQUIVALENT_PHOTON_FLUX_OPERATOR_READY")
    print("DOMAIN_GUARD_ACTIVE")
    print("FORMULA_AUTHORITY_ZERO")


if __name__ == "__main__":
    _sanity()
