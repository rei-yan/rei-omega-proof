#!/usr/bin/env python3
"""Finite deterministic crucible for Unknown Unknown Genesis.

This module classifies several synthetic closure failures in a frozen research
language. It does not perform real-world actions and does not claim arbitrary
unknown-unknown discovery.
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass


@dataclass(frozen=True)
class Obs:
    x: float
    y: float
    phase: str = "single"
    direction: str | None = None


def fit_line(records: list[Obs]) -> tuple[float, float, float]:
    n = len(records)
    sx = sum(r.x for r in records)
    sy = sum(r.y for r in records)
    sxx = sum(r.x * r.x for r in records)
    sxy = sum(r.x * r.y for r in records)
    den = n * sxx - sx * sx
    if abs(den) < 1e-12:
        return 0.0, sy / n, float("inf")
    a = (n * sxy - sx * sy) / den
    b = (sy - a * sx) / n
    mse = sum((a * r.x + b - r.y) ** 2 for r in records) / n
    return a, b, mse


def fit_quadratic_grid(records: list[Obs]) -> float:
    """Tiny frozen coefficient grid used only to detect obvious representation gaps."""
    candidates = [i / 2 for i in range(-6, 7)]
    best = float("inf")
    for a in candidates:
        for b in candidates:
            for c in candidates:
                mse = sum((a * r.x * r.x + b * r.x + c - r.y) ** 2 for r in records) / len(records)
                best = min(best, mse)
    return best


def repeated_x_spread(records: list[Obs]) -> dict[float, float]:
    groups: dict[float, list[float]] = defaultdict(list)
    for r in records:
        groups[round(r.x, 9)].append(r.y)
    return {x: max(v) - min(v) for x, v in groups.items() if len(v) > 1}


def direction_resolves(records: list[Obs], tolerance: float = 1e-9) -> bool:
    groups: dict[tuple[float, str], list[float]] = defaultdict(list)
    has_direction = False
    for r in records:
        if r.direction is None:
            continue
        has_direction = True
        groups[(round(r.x, 9), r.direction)].append(r.y)
    if not has_direction:
        return False
    for values in groups.values():
        if max(values) - min(values) > tolerance:
            return False
    return True


def phase_shift(records: list[Obs], slope_delta: float = 0.75, intercept_delta: float = 0.75) -> bool:
    phases = sorted({r.phase for r in records})
    if len(phases) < 2:
        return False
    fits = []
    for phase in phases:
        subset = [r for r in records if r.phase == phase]
        if len(subset) < 2:
            return False
        fits.append(fit_line(subset)[:2])
    a0, b0 = fits[0]
    return any(abs(a - a0) > slope_delta or abs(b - b0) > intercept_delta for a, b in fits[1:])


def classify(name: str, records: list[Obs]) -> dict:
    line_a, line_b, line_mse = fit_line(records)
    quad_mse = fit_quadratic_grid(records)
    spreads = repeated_x_spread(records)
    contradiction = any(v > 0.5 for v in spreads.values())

    if phase_shift(records):
        status = "REGIME_SHIFT"
        proposal = "FREEZE_CHANGEPOINT_AND_REVALIDATE"
    elif contradiction and direction_resolves(records):
        status = "STATE_MEMORY_GAP"
        proposal = "PROPOSE_BOUNDED_STATE_HISTORY_VARIABLE"
    elif contradiction:
        status = "MEASUREMENT_GAP"
        proposal = "PROPOSE_DISCRIMINATING_MEASUREMENT"
    elif line_mse <= 1e-10:
        status = "EXPLAINED_WITHIN_GRAMMAR"
        proposal = "NONE"
    elif quad_mse <= max(1e-10, line_mse * 0.05):
        status = "REPRESENTATION_GAP"
        proposal = "PROPOSE_FROZEN_NONLINEAR_BASIS_TEST"
    else:
        status = "UNRESOLVED_UNKNOWN"
        proposal = "PRESERVE_AND_CHALLENGE_WITHOUT_CERTAINTY"

    return {
        "case": name,
        "status": status,
        "proposal": proposal,
        "line_a": line_a,
        "line_b": line_b,
        "line_mse": line_mse,
        "quadratic_grid_mse": quad_mse,
        "authority": 0.0,
        "external_action_allowed": False,
        "self_certified": False,
    }


def main() -> None:
    cases = {
        "known_linear": [Obs(x, 2 * x + 1) for x in (-2, -1, 0, 1, 2)],
        "curved_language_gap": [Obs(x, x * x - x + 0.5) for x in (-2, -1, 0, 1, 2)],
        "latent_measurement_gap": [
            Obs(-1, -2), Obs(-1, 2), Obs(0, -1), Obs(0, 1), Obs(1, 0), Obs(1, 4)
        ],
        "hysteresis_state_gap": [
            Obs(-1, -1, direction="up"), Obs(0, 0, direction="up"), Obs(1, 1, direction="up"),
            Obs(1, 3, direction="down"), Obs(0, 2, direction="down"), Obs(-1, 1, direction="down"),
        ],
        "mechanism_regime_shift": [
            Obs(-1, -1, phase="early"), Obs(0, 0, phase="early"), Obs(1, 1, phase="early"),
            Obs(-1, 4, phase="late"), Obs(0, 2, phase="late"), Obs(1, 0, phase="late"),
        ],
        "unresolved_structure": [
            Obs(-2, 1.1), Obs(-1, -2.7), Obs(0, 0.4), Obs(1, 3.3), Obs(2, -1.8)
        ],
    }

    results = [classify(name, records) for name, records in cases.items()]
    by_name = {r["case"]: r for r in results}

    assert by_name["known_linear"]["status"] == "EXPLAINED_WITHIN_GRAMMAR"
    assert by_name["curved_language_gap"]["status"] == "REPRESENTATION_GAP"
    assert by_name["latent_measurement_gap"]["status"] == "MEASUREMENT_GAP"
    assert by_name["hysteresis_state_gap"]["status"] == "STATE_MEMORY_GAP"
    assert by_name["mechanism_regime_shift"]["status"] == "REGIME_SHIFT"
    assert by_name["unresolved_structure"]["status"] == "UNRESOLVED_UNKNOWN"
    assert all(r["authority"] == 0.0 for r in results)
    assert all(r["external_action_allowed"] is False for r in results)
    assert all(r["self_certified"] is False for r in results)

    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
