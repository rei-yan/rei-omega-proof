#!/usr/bin/env python3
"""REI-Ω Recursive Divided-Difference Observer (RDDO) reference implementation.

Observer-only numerical diagnostic. It computes bounded Newton-style divided-
difference tables and conservative telemetry. It has no promotion, actuation,
or reality-validation authority.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass, asdict
from typing import Iterable, Sequence


@dataclass(frozen=True)
class RDDOResult:
    x: list[float]
    y: list[float]
    coefficients: list[float]
    orders: list[list[float]]
    max_order: int
    min_spacing: float
    max_spacing: float
    spacing_ratio: float
    max_abs_coefficient_by_order: list[float]
    high_order_activity_ratio: float
    conditioning_warning: bool
    nonfinite_detected: bool
    observer_only: bool = True
    promotion_capability: bool = False
    reality_validated: bool = False


def _finite(values: Iterable[float]) -> bool:
    return all(math.isfinite(v) for v in values)


def divided_differences(
    x: Sequence[float],
    y: Sequence[float],
    *,
    max_order: int | None = None,
    spacing_epsilon: float = 1e-12,
) -> RDDOResult:
    if len(x) != len(y):
        raise ValueError("x and y must have equal length")
    if len(x) < 2:
        raise ValueError("RDDO requires at least two samples")
    if not _finite(x) or not _finite(y):
        raise ValueError("RDDO input must be finite")

    pairs = sorted((float(a), float(b)) for a, b in zip(x, y))
    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]

    spacings = [xs[i + 1] - xs[i] for i in range(len(xs) - 1)]
    if any(abs(s) <= spacing_epsilon for s in spacings):
        raise ValueError("duplicate or near-duplicate sample coordinates")

    requested = len(xs) - 1 if max_order is None else int(max_order)
    if requested < 1:
        raise ValueError("max_order must be >= 1")
    bounded_order = min(requested, len(xs) - 1, 8)

    table: list[list[float]] = [ys[:]]
    current = ys[:]
    for order in range(1, bounded_order + 1):
        next_values: list[float] = []
        for i in range(len(current) - 1):
            denom = xs[i + order] - xs[i]
            if abs(denom) <= spacing_epsilon:
                raise ValueError("ill-defined divided difference denominator")
            next_values.append((current[i + 1] - current[i]) / denom)
        table.append(next_values)
        current = next_values

    coeffs = [order_values[0] for order_values in table]
    maxima = [max(abs(v) for v in order_values) if order_values else 0.0 for order_values in table]
    first_scale = max(maxima[1] if len(maxima) > 1 else 0.0, 1e-15)
    high_order_peak = max(maxima[2:], default=0.0)
    high_order_ratio = high_order_peak / first_scale

    min_spacing = min(abs(s) for s in spacings)
    max_spacing = max(abs(s) for s in spacings)
    spacing_ratio = max_spacing / min_spacing if min_spacing > 0 else math.inf

    nonfinite = not _finite(v for row in table for v in row)
    conditioning_warning = spacing_ratio > 1e6 or high_order_ratio > 1e8 or nonfinite

    return RDDOResult(
        x=xs,
        y=ys,
        coefficients=coeffs,
        orders=table,
        max_order=bounded_order,
        min_spacing=min_spacing,
        max_spacing=max_spacing,
        spacing_ratio=spacing_ratio,
        max_abs_coefficient_by_order=maxima,
        high_order_activity_ratio=high_order_ratio,
        conditioning_warning=conditioning_warning,
        nonfinite_detected=nonfinite,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Observer-only recursive divided-difference diagnostic")
    parser.add_argument("--x", required=True, help="JSON array of sample coordinates")
    parser.add_argument("--y", required=True, help="JSON array of observed values")
    parser.add_argument("--max-order", type=int, default=None)
    args = parser.parse_args()

    result = divided_differences(json.loads(args.x), json.loads(args.y), max_order=args.max_order)
    print(json.dumps(asdict(result), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
