#!/usr/bin/env python3
"""REI-Ω Kernel / Null-Space observer reference.

This is a bounded linear-algebra diagnostic for observability gaps.  It computes
rank, nullity and a numerical null-space basis for a finite real matrix.  When a
state/damage vector is supplied, it also measures the component lying inside the
current observation kernel.

It has no promotion, actuation, causal-truth or reality-validation authority.
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from typing import Iterable, Sequence


def _finite(values: Iterable[float]) -> bool:
    return all(math.isfinite(float(v)) for v in values)


def _norm(v: Sequence[float]) -> float:
    return math.sqrt(sum(float(x) * float(x) for x in v))


def _matvec(a: Sequence[Sequence[float]], x: Sequence[float]) -> list[float]:
    return [sum(float(row[j]) * float(x[j]) for j in range(len(x))) for row in a]


def _orthonormalize(vectors: Sequence[Sequence[float]], tol: float) -> list[list[float]]:
    out: list[list[float]] = []
    for raw in vectors:
        v = [float(x) for x in raw]
        for q in out:
            coeff = sum(v[i] * q[i] for i in range(len(v)))
            v = [v[i] - coeff * q[i] for i in range(len(v))]
        n = _norm(v)
        if n > tol:
            out.append([x / n for x in v])
    return out


@dataclass(frozen=True)
class KernelNullSpaceResult:
    rows: int
    cols: int
    rank: int
    nullity: int
    pivot_columns: list[int]
    free_columns: list[int]
    nullspace_basis: list[list[float]]
    max_basis_residual: float
    unobservable_subspace_present: bool
    supplied_state_vector: bool
    state_norm: float
    hidden_component_norm: float
    hidden_fraction: float
    analogy_only: bool = True
    observer_only: bool = True
    promotion_capability: bool = False
    actuation_capability: bool = False
    causal_truth_capability: bool = False
    reality_validated: bool = False


def analyze_kernel(
    matrix: Sequence[Sequence[float]],
    *,
    state_vector: Sequence[float] | None = None,
    tolerance: float = 1e-10,
    max_dimension: int = 64,
) -> KernelNullSpaceResult:
    if not matrix:
        raise ValueError("matrix must contain at least one row")
    rows = len(matrix)
    cols = len(matrix[0])
    if cols < 1:
        raise ValueError("matrix must contain at least one column")
    if rows > max_dimension or cols > max_dimension:
        raise ValueError("matrix dimension exceeds bounded observer limit")
    if tolerance <= 0 or not math.isfinite(tolerance):
        raise ValueError("tolerance must be finite and positive")
    if any(len(row) != cols for row in matrix):
        raise ValueError("matrix must be rectangular")
    if not _finite(v for row in matrix for v in row):
        raise ValueError("matrix entries must be finite")

    a = [[float(v) for v in row] for row in matrix]
    rref = [row[:] for row in a]
    pivot_columns: list[int] = []
    pivot_row = 0

    for col in range(cols):
        candidate = max(range(pivot_row, rows), key=lambda r: abs(rref[r][col]), default=pivot_row)
        if pivot_row >= rows or abs(rref[candidate][col]) <= tolerance:
            continue
        rref[pivot_row], rref[candidate] = rref[candidate], rref[pivot_row]
        pivot = rref[pivot_row][col]
        rref[pivot_row] = [v / pivot for v in rref[pivot_row]]
        for r in range(rows):
            if r == pivot_row:
                continue
            factor = rref[r][col]
            if abs(factor) <= tolerance:
                continue
            rref[r] = [rref[r][c] - factor * rref[pivot_row][c] for c in range(cols)]
        pivot_columns.append(col)
        pivot_row += 1
        if pivot_row == rows:
            break

    free_columns = [c for c in range(cols) if c not in pivot_columns]
    raw_basis: list[list[float]] = []
    for free_col in free_columns:
        vector = [0.0] * cols
        vector[free_col] = 1.0
        for r, pivot_col in enumerate(pivot_columns):
            vector[pivot_col] = -rref[r][free_col]
        raw_basis.append(vector)

    basis = _orthonormalize(raw_basis, tolerance)
    residuals = [_norm(_matvec(a, v)) for v in basis]
    max_residual = max(residuals, default=0.0)

    supplied = state_vector is not None
    state_norm = 0.0
    hidden_norm = 0.0
    hidden_fraction = 0.0
    if state_vector is not None:
        if len(state_vector) != cols:
            raise ValueError("state_vector length must equal matrix column count")
        if not _finite(state_vector):
            raise ValueError("state_vector entries must be finite")
        x = [float(v) for v in state_vector]
        state_norm = _norm(x)
        projection = [0.0] * cols
        for q in basis:
            coeff = sum(x[i] * q[i] for i in range(cols))
            projection = [projection[i] + coeff * q[i] for i in range(cols)]
        hidden_norm = _norm(projection)
        hidden_fraction = hidden_norm / state_norm if state_norm > tolerance else 0.0

    return KernelNullSpaceResult(
        rows=rows,
        cols=cols,
        rank=len(pivot_columns),
        nullity=len(free_columns),
        pivot_columns=pivot_columns,
        free_columns=free_columns,
        nullspace_basis=basis,
        max_basis_residual=max_residual,
        unobservable_subspace_present=bool(free_columns),
        supplied_state_vector=supplied,
        state_norm=state_norm,
        hidden_component_norm=hidden_norm,
        hidden_fraction=hidden_fraction,
    )


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Observer-only Kernel / Null-Space diagnostic")
    parser.add_argument("--matrix", required=True, help="JSON 2D array")
    parser.add_argument("--state-vector", default=None, help="optional JSON vector")
    parser.add_argument("--tolerance", type=float, default=1e-10)
    args = parser.parse_args()

    result = analyze_kernel(
        json.loads(args.matrix),
        state_vector=None if args.state_vector is None else json.loads(args.state_vector),
        tolerance=args.tolerance,
    )
    print(json.dumps(asdict(result), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
