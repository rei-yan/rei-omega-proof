#!/usr/bin/env python3
"""REI-Ω Mechanical Metallurgy Fusion v1 reference model.

This is a mechanics-inspired digital-system damage observer. It borrows concepts
such as stress concentration, yield utilization, cumulative fatigue, crack
initiation, propagation pressure, toughness reserve, and recovery credit.

It is NOT a constitutive law for real metals, not a fracture-mechanics solver,
and not physical proof. It has no promotion, actuation, or reality-validation
authority.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass, asdict
from typing import Iterable, Sequence


@dataclass(frozen=True)
class MetallurgyFusionResult:
    stress_history: list[float]
    stress_concentration_factor: float
    effective_stress_history: list[float]
    peak_effective_stress: float
    yield_threshold: float
    fracture_threshold: float
    peak_yield_utilization: float
    peak_fracture_utilization: float
    fatigue_reference_cycles: float
    fatigue_exponent: float
    historical_fatigue_damage: float
    recovery_credit: float
    residual_fatigue_damage: float
    initial_flaw_severity: float
    crack_initiation_pressure: float
    propagation_pressure: float
    toughness_reserve: float
    yield_exceeded: bool
    fracture_limit_exceeded: bool
    crack_initiation_candidate: bool
    propagation_risk_candidate: bool
    damage_stage: str
    analogy_only: bool = True
    physical_material_claim: bool = False
    observer_only: bool = True
    promotion_capability: bool = False
    actuation_capability: bool = False
    reality_validated: bool = False
    historical_damage_erased_by_recovery: bool = False


def _finite(values: Iterable[float]) -> bool:
    return all(math.isfinite(v) for v in values)


def assess_system_damage(
    stress_history: Sequence[float],
    *,
    yield_threshold: float,
    fracture_threshold: float,
    stress_concentration_factor: float = 1.0,
    fatigue_reference_cycles: float = 1000.0,
    fatigue_exponent: float = 3.0,
    initial_flaw_severity: float = 0.0,
    recovery_credit: float = 0.0,
) -> MetallurgyFusionResult:
    if not stress_history:
        raise ValueError("stress_history must not be empty")

    history = [float(v) for v in stress_history]
    scalar_inputs = [
        float(yield_threshold),
        float(fracture_threshold),
        float(stress_concentration_factor),
        float(fatigue_reference_cycles),
        float(fatigue_exponent),
        float(initial_flaw_severity),
        float(recovery_credit),
    ]
    if not _finite(history) or not _finite(scalar_inputs):
        raise ValueError("all inputs must be finite")

    yield_threshold = float(yield_threshold)
    fracture_threshold = float(fracture_threshold)
    kt = float(stress_concentration_factor)
    reference_cycles = float(fatigue_reference_cycles)
    exponent = float(fatigue_exponent)
    initial_flaw = float(initial_flaw_severity)
    recovery = float(recovery_credit)

    if yield_threshold <= 0:
        raise ValueError("yield_threshold must be > 0")
    if fracture_threshold <= yield_threshold:
        raise ValueError("fracture_threshold must be > yield_threshold")
    if kt < 1.0:
        raise ValueError("stress_concentration_factor must be >= 1")
    if reference_cycles <= 0:
        raise ValueError("fatigue_reference_cycles must be > 0")
    if exponent < 1.0 or exponent > 12.0:
        raise ValueError("fatigue_exponent must be in [1, 12]")
    if not 0.0 <= initial_flaw <= 1.0:
        raise ValueError("initial_flaw_severity must be in [0, 1]")
    if not 0.0 <= recovery <= 1.0:
        raise ValueError("recovery_credit must be in [0, 1]")

    effective = [abs(v) * kt for v in history]
    peak = max(effective)

    yield_util = peak / yield_threshold
    fracture_util = peak / fracture_threshold

    # Digital fatigue surrogate inspired by cumulative damage reasoning.
    # Each observed load contributes a bounded-history increment. This is not
    # Miner's rule for any physical material and must not be interpreted as one.
    historical_damage = sum(
        (stress / yield_threshold) ** exponent / reference_cycles
        for stress in effective
    )

    # Recovery can lower residual operational pressure but cannot erase the
    # historical evidence that the damaging cycles occurred.
    residual_damage = historical_damage * (1.0 - recovery)

    crack_initiation_pressure = max(
        residual_damage,
        yield_util - 1.0,
        initial_flaw * yield_util,
    )
    propagation_pressure = (
        initial_flaw * fracture_util
        + max(0.0, residual_damage - 1.0)
        + max(0.0, fracture_util - 0.75)
    )
    toughness_reserve = max(0.0, 1.0 - propagation_pressure)

    yield_exceeded = yield_util >= 1.0
    fracture_exceeded = fracture_util >= 1.0
    crack_candidate = crack_initiation_pressure >= 1.0
    propagation_candidate = propagation_pressure >= 1.0 or fracture_exceeded

    if fracture_exceeded:
        stage = "FRACTURE_LIMIT_EXCEEDED"
    elif propagation_candidate:
        stage = "PROPAGATION_RISK_CANDIDATE"
    elif crack_candidate:
        stage = "CRACK_INITIATION_CANDIDATE"
    elif residual_damage >= 0.25 or yield_exceeded:
        stage = "FATIGUE_ACCUMULATING"
    else:
        stage = "BOUNDED_ELASTIC_ANALOG"

    return MetallurgyFusionResult(
        stress_history=history,
        stress_concentration_factor=kt,
        effective_stress_history=effective,
        peak_effective_stress=peak,
        yield_threshold=yield_threshold,
        fracture_threshold=fracture_threshold,
        peak_yield_utilization=yield_util,
        peak_fracture_utilization=fracture_util,
        fatigue_reference_cycles=reference_cycles,
        fatigue_exponent=exponent,
        historical_fatigue_damage=historical_damage,
        recovery_credit=recovery,
        residual_fatigue_damage=residual_damage,
        initial_flaw_severity=initial_flaw,
        crack_initiation_pressure=crack_initiation_pressure,
        propagation_pressure=propagation_pressure,
        toughness_reserve=toughness_reserve,
        yield_exceeded=yield_exceeded,
        fracture_limit_exceeded=fracture_exceeded,
        crack_initiation_candidate=crack_candidate,
        propagation_risk_candidate=propagation_candidate,
        damage_stage=stage,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Observer-only mechanics-inspired digital damage diagnostic"
    )
    parser.add_argument("--stress-history", required=True, help="JSON array")
    parser.add_argument("--yield-threshold", required=True, type=float)
    parser.add_argument("--fracture-threshold", required=True, type=float)
    parser.add_argument("--stress-concentration-factor", type=float, default=1.0)
    parser.add_argument("--fatigue-reference-cycles", type=float, default=1000.0)
    parser.add_argument("--fatigue-exponent", type=float, default=3.0)
    parser.add_argument("--initial-flaw-severity", type=float, default=0.0)
    parser.add_argument("--recovery-credit", type=float, default=0.0)
    args = parser.parse_args()

    result = assess_system_damage(
        json.loads(args.stress_history),
        yield_threshold=args.yield_threshold,
        fracture_threshold=args.fracture_threshold,
        stress_concentration_factor=args.stress_concentration_factor,
        fatigue_reference_cycles=args.fatigue_reference_cycles,
        fatigue_exponent=args.fatigue_exponent,
        initial_flaw_severity=args.initial_flaw_severity,
        recovery_credit=args.recovery_credit,
    )
    print(json.dumps(asdict(result), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
