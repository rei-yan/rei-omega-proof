#!/usr/bin/env python3
"""Small deterministic sanity checks for the REI-Ω Ohmic Constraint Layer."""

import math


def assert_close(a, b, tol=1e-12):
    if not math.isclose(a, b, rel_tol=tol, abs_tol=tol):
        raise AssertionError(f"{a} != {b}")


def main():
    # Local Ohm law and dissipation.
    resistance = 5.0
    voltage = 10.0
    current = voltage / resistance
    power = voltage * current

    assert resistance > 0
    assert_close(voltage, current * resistance)
    assert_close(power, current * current * resistance)
    assert_close(power, voltage * voltage / resistance)
    assert power >= 0

    # Three-node passive line network:
    # node0 --(2 ohm)-- node1 --(4 ohm)-- node2
    # potentials: 12V, 8V, 0V
    v0, v1, v2 = 12.0, 8.0, 0.0
    r01, r12 = 2.0, 4.0
    g01, g12 = 1.0 / r01, 1.0 / r12

    i01 = g01 * (v0 - v1)
    i12 = g12 * (v1 - v2)

    assert_close(i01, 2.0)
    assert_close(i12, 2.0)

    # Interior-node KCL: incoming current equals outgoing current.
    assert_close(i01 - i12, 0.0)

    p01 = g01 * (v0 - v1) ** 2
    p12 = g12 * (v1 - v2) ** 2
    p_total = p01 + p12
    assert_close(p_total, 24.0)
    assert p_total >= 0

    print("OHMIC_LOCAL_LAW: PASS")
    print("OHMIC_KCL: PASS")
    print("OHMIC_PASSIVE_DISSIPATION: PASS")


if __name__ == "__main__":
    main()
