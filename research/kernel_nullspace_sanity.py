#!/usr/bin/env python3
"""Deterministic sanity checks for the Kernel / Null-Space observer."""

from __future__ import annotations

from kernel_nullspace_reference import analyze_kernel


def main() -> int:
    full_rank = analyze_kernel([[1, 0], [0, 1]], state_vector=[1, 2])
    assert full_rank.rank == 2
    assert full_rank.nullity == 0
    assert full_rank.unobservable_subspace_present is False
    assert full_rank.hidden_fraction == 0.0

    # x + z = 0, y + z = 0 has one-dimensional kernel span(-1,-1,1).
    hidden = analyze_kernel([[1, 0, 1], [0, 1, 1]], state_vector=[-1, -1, 1])
    assert hidden.rank == 2
    assert hidden.nullity == 1
    assert hidden.unobservable_subspace_present is True
    assert hidden.max_basis_residual < 1e-9
    assert hidden.hidden_fraction > 0.999999

    # A row-space direction is orthogonal to the null space, so it should not hide.
    visible = analyze_kernel([[1, 0, 1], [0, 1, 1]], state_vector=[1, 0, 1])
    assert visible.hidden_fraction < 1e-9

    assert hidden.analogy_only is True
    assert hidden.observer_only is True
    assert hidden.promotion_capability is False
    assert hidden.actuation_capability is False
    assert hidden.causal_truth_capability is False
    assert hidden.reality_validated is False

    try:
        analyze_kernel([[1, 2], [3]])
    except ValueError:
        pass
    else:
        raise AssertionError("ragged matrix must fail closed")

    try:
        analyze_kernel([[1, float("nan")]])
    except ValueError:
        pass
    else:
        raise AssertionError("non-finite matrix must fail closed")

    try:
        analyze_kernel([[1, 0], [0, 1]], state_vector=[1])
    except ValueError:
        pass
    else:
        raise AssertionError("dimension mismatch must fail closed")

    print("KERNEL_NULLSPACE_SANITY_SUCCESS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
