#!/usr/bin/env python3
"""Deterministic sanity checks for the observer-only RDDO reference."""

from __future__ import annotations

from rddo_reference import divided_differences


def main() -> int:
    linear = divided_differences([0, 1, 2, 3], [1, 3, 5, 7], max_order=3)
    assert abs(linear.coefficients[0] - 1.0) < 1e-12
    assert abs(linear.coefficients[1] - 2.0) < 1e-12
    assert all(abs(v) < 1e-12 for v in linear.orders[2])
    assert linear.observer_only is True
    assert linear.promotion_capability is False
    assert linear.reality_validated is False

    quadratic = divided_differences([0, 1, 2, 3], [0, 1, 4, 9], max_order=3)
    assert abs(quadratic.coefficients[1] - 1.0) < 1e-12
    assert abs(quadratic.coefficients[2] - 1.0) < 1e-12
    assert all(abs(v) < 1e-12 for v in quadratic.orders[3])

    try:
        divided_differences([0, 1, 1], [0, 1, 2])
    except ValueError:
        pass
    else:
        raise AssertionError("duplicate sample coordinate must fail closed")

    try:
        divided_differences([0, 1], [0, float("nan")])
    except ValueError:
        pass
    else:
        raise AssertionError("non-finite input must fail closed")

    bounded = divided_differences(list(range(20)), [float(i * i) for i in range(20)], max_order=19)
    assert bounded.max_order == 8, "observer order must remain bounded"

    print("RDDO_SANITY_SUCCESS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
