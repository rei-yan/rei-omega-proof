#!/usr/bin/env python3
"""Deterministic sanity checks for REI Mechanical Metallurgy Fusion v1."""

from __future__ import annotations

from mechanical_metallurgy_reference import assess_system_damage


def must_fail(fn, message: str) -> None:
    try:
        fn()
    except ValueError:
        return
    raise AssertionError(message)


def main() -> int:
    bounded = assess_system_damage(
        [8, 10, 9, 11],
        yield_threshold=20,
        fracture_threshold=40,
    )
    assert bounded.damage_stage == "BOUNDED_ELASTIC_ANALOG"
    assert bounded.yield_exceeded is False
    assert bounded.fracture_limit_exceeded is False
    assert bounded.analogy_only is True
    assert bounded.physical_material_claim is False
    assert bounded.observer_only is True
    assert bounded.promotion_capability is False
    assert bounded.actuation_capability is False
    assert bounded.reality_validated is False

    base = assess_system_damage(
        [18, 18],
        yield_threshold=20,
        fracture_threshold=40,
        stress_concentration_factor=1.0,
    )
    concentrated = assess_system_damage(
        [18, 18],
        yield_threshold=20,
        fracture_threshold=40,
        stress_concentration_factor=1.25,
    )
    assert base.yield_exceeded is False
    assert concentrated.yield_exceeded is True
    assert concentrated.peak_yield_utilization > base.peak_yield_utilization

    short = assess_system_damage(
        [12] * 100,
        yield_threshold=20,
        fracture_threshold=40,
        fatigue_reference_cycles=1000,
    )
    long = assess_system_damage(
        [12] * 3000,
        yield_threshold=20,
        fracture_threshold=40,
        fatigue_reference_cycles=1000,
    )
    assert long.historical_fatigue_damage > short.historical_fatigue_damage
    assert long.damage_stage in {
        "FATIGUE_ACCUMULATING",
        "CRACK_INITIATION_CANDIDATE",
        "PROPAGATION_RISK_CANDIDATE",
    }

    unrecovered = assess_system_damage(
        [16] * 2500,
        yield_threshold=20,
        fracture_threshold=40,
        fatigue_reference_cycles=1000,
        recovery_credit=0.0,
    )
    recovered = assess_system_damage(
        [16] * 2500,
        yield_threshold=20,
        fracture_threshold=40,
        fatigue_reference_cycles=1000,
        recovery_credit=0.5,
    )
    assert recovered.historical_fatigue_damage == unrecovered.historical_fatigue_damage
    assert recovered.residual_fatigue_damage < unrecovered.residual_fatigue_damage
    assert recovered.historical_damage_erased_by_recovery is False

    fracture = assess_system_damage(
        [35],
        yield_threshold=20,
        fracture_threshold=40,
        stress_concentration_factor=1.2,
    )
    assert fracture.fracture_limit_exceeded is True
    assert fracture.damage_stage == "FRACTURE_LIMIT_EXCEEDED"

    flawed = assess_system_damage(
        [25],
        yield_threshold=20,
        fracture_threshold=40,
        initial_flaw_severity=1.0,
    )
    assert flawed.crack_initiation_candidate is True

    must_fail(
        lambda: assess_system_damage([], yield_threshold=20, fracture_threshold=40),
        "empty history must fail closed",
    )
    must_fail(
        lambda: assess_system_damage([1], yield_threshold=0, fracture_threshold=40),
        "non-positive yield threshold must fail closed",
    )
    must_fail(
        lambda: assess_system_damage([1], yield_threshold=20, fracture_threshold=10),
        "fracture threshold below yield must fail closed",
    )
    must_fail(
        lambda: assess_system_damage(
            [1], yield_threshold=20, fracture_threshold=40, stress_concentration_factor=0.9
        ),
        "stress concentration factor below one must fail closed",
    )
    must_fail(
        lambda: assess_system_damage(
            [float("nan")], yield_threshold=20, fracture_threshold=40
        ),
        "non-finite input must fail closed",
    )

    print("MECHANICAL_METALLURGY_FUSION_SANITY_SUCCESS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
