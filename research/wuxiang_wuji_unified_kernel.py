#!/usr/bin/env python3
"""Executable sanity kernel for the Wuxiang-Wuji unified REI integration layer.

This file validates only the bounded orchestration rules. It does not certify
external gates, scientific truth, or unrestricted real-world authority.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Iterable, List

EPS = 1e-12


@dataclass(frozen=True)
class GateInput:
    authorized: bool
    constitution_ok: bool
    recovery_ready: bool
    human_veto: bool
    domain_eligible: bool
    evidence_scope: float
    claim_scope: float
    lease_valid: bool
    provenance_complete: bool
    hard_gate_nonoverride: bool = True


@dataclass(frozen=True)
class ErrorVector:
    prediction: float
    calibration: float
    scope: float
    drift: float
    recovery: float
    authority: float
    provenance: float


@dataclass(frozen=True)
class ResourceSignal:
    name: str
    value: float
    uncertainty: float
    falsification_pressure: float
    expected_information_gain: float
    cost: float


@dataclass(frozen=True)
class UnifiedState:
    raw_problem_id: str
    representation_id: str
    uncertainty: float
    authority: float
    recovery_ready: bool
    evidence_scope: float
    claim_scope: float
    lease_valid: bool
    failure_count: int
    external_gate_state: str


def execute_candidate(g: GateInput) -> bool:
    """Hard execution gate. No score can override this function."""
    return (
        g.authorized
        and g.constitution_ok
        and g.recovery_ready
        and not g.human_veto
        and g.domain_eligible
        and g.evidence_scope + EPS >= g.claim_scope
        and g.lease_valid
        and g.provenance_complete
        and g.hard_gate_nonoverride
    )


def authority_under_uncertainty(
    *,
    a_max: float,
    constitution_factor: float,
    recovery_factor: float,
    uncertainty: float,
    k: float,
) -> float:
    values = (a_max, constitution_factor, recovery_factor, uncertainty, k)
    if not all(math.isfinite(v) for v in values):
        raise ValueError("authority inputs must be finite")
    if a_max < 0 or not (0 <= constitution_factor <= 1) or not (0 <= recovery_factor <= 1):
        raise ValueError("invalid authority factors")
    if uncertainty < 0 or k < 0:
        raise ValueError("uncertainty and k must be nonnegative")
    return a_max * constitution_factor * recovery_factor * math.exp(-k * uncertainty)


def integrated_error(error: ErrorVector, weights: Dict[str, float]) -> float:
    required = {
        "prediction",
        "calibration",
        "scope",
        "drift",
        "recovery",
        "authority",
        "provenance",
    }
    if set(weights) != required:
        raise ValueError("weights must exactly match the frozen error dimensions")
    if any((not math.isfinite(v) or v < 0) for v in weights.values()):
        raise ValueError("weights must be finite and nonnegative")
    parts = {
        "prediction": error.prediction,
        "calibration": error.calibration,
        "scope": error.scope,
        "drift": error.drift,
        "recovery": error.recovery,
        "authority": error.authority,
        "provenance": error.provenance,
    }
    if any((not math.isfinite(v) or v < 0) for v in parts.values()):
        raise ValueError("error components must be finite and nonnegative")
    return sum(weights[k] * parts[k] for k in required)


def adaptive_resource_allocation(
    signals: Iterable[ResourceSignal],
    *,
    total_budget: float,
    per_task_cap_fraction: float = 0.6,
) -> Dict[str, float]:
    signals = list(signals)
    if not signals:
        return {}
    if not math.isfinite(total_budget) or total_budget < 0:
        raise ValueError("total_budget must be finite and nonnegative")
    if not (0 < per_task_cap_fraction <= 1):
        raise ValueError("cap fraction must be in (0,1]")

    priorities: Dict[str, float] = {}
    for s in signals:
        vals = (s.value, s.uncertainty, s.falsification_pressure, s.expected_information_gain, s.cost)
        if not all(math.isfinite(v) for v in vals):
            raise ValueError("resource signals must be finite")
        if min(vals) < 0:
            raise ValueError("resource signals must be nonnegative")
        priorities[s.name] = s.value * (
            s.uncertainty + s.falsification_pressure + s.expected_information_gain
        ) / (s.cost + EPS)

    total_priority = sum(priorities.values())
    if total_priority <= EPS:
        equal = total_budget / len(signals)
        return {s.name: equal for s in signals}

    cap = total_budget * per_task_cap_fraction
    raw = {name: total_budget * q / total_priority for name, q in priorities.items()}
    alloc = {name: min(v, cap) for name, v in raw.items()}

    # Redistribute any capped remainder deterministically among tasks with headroom.
    remainder = total_budget - sum(alloc.values())
    while remainder > EPS:
        headroom = {name: cap - v for name, v in alloc.items() if cap - v > EPS}
        if not headroom:
            break
        hsum = sum(headroom.values())
        moved = 0.0
        for name, room in headroom.items():
            add = min(room, remainder * room / hsum)
            alloc[name] += add
            moved += add
        if moved <= EPS:
            break
        remainder -= moved

    return alloc


def route_domain(domain: str) -> List[str]:
    """Return only domain-specific optional operators."""
    routing = {
        "ultraperipheral_collision": ["equivalent_photon_flux_operator"],
        "quantum_phase_space": ["weyl_wigner_phase_space_operator"],
    }
    return list(routing.get(domain, []))


def correction_decision(*, gate_ok: bool, severe_failure: bool, recoverable: bool, drift: bool) -> str:
    if not gate_ok:
        return "ABSTAIN"
    if severe_failure and not recoverable:
        return "RETIRE"
    if severe_failure and recoverable:
        return "ROLLBACK"
    if drift:
        return "REVALIDATE"
    return "SURVIVES"


def next_state(state: UnifiedState, *, new_uncertainty: float, failure_observed: bool) -> UnifiedState:
    if new_uncertainty < 0 or not math.isfinite(new_uncertainty):
        raise ValueError("new uncertainty must be finite and nonnegative")
    # State update cannot increase authority merely because uncertainty increased.
    new_authority = min(state.authority, authority_under_uncertainty(
        a_max=max(state.authority, 0.0),
        constitution_factor=1.0,
        recovery_factor=1.0 if state.recovery_ready else 0.0,
        uncertainty=new_uncertainty,
        k=1.0,
    ))
    return UnifiedState(
        raw_problem_id=state.raw_problem_id,
        representation_id=state.representation_id,
        uncertainty=new_uncertainty,
        authority=new_authority,
        recovery_ready=state.recovery_ready,
        evidence_scope=state.evidence_scope,
        claim_scope=state.claim_scope,
        lease_valid=state.lease_valid,
        failure_count=state.failure_count + int(failure_observed),
        external_gate_state=state.external_gate_state,
    )


def _sanity() -> None:
    good_gate = GateInput(
        authorized=True,
        constitution_ok=True,
        recovery_ready=True,
        human_veto=False,
        domain_eligible=True,
        evidence_scope=2.0,
        claim_scope=1.0,
        lease_valid=True,
        provenance_complete=True,
    )
    assert execute_candidate(good_gate)

    # Score is deliberately absent from the gate API: no score can override veto.
    vetoed = GateInput(**{**good_gate.__dict__, "human_veto": True})
    assert not execute_candidate(vetoed)
    scope_fail = GateInput(**{**good_gate.__dict__, "evidence_scope": 0.5, "claim_scope": 1.0})
    assert not execute_candidate(scope_fail)

    a_low_u = authority_under_uncertainty(
        a_max=1.0, constitution_factor=1.0, recovery_factor=1.0, uncertainty=0.1, k=2.0
    )
    a_high_u = authority_under_uncertainty(
        a_max=1.0, constitution_factor=1.0, recovery_factor=1.0, uncertainty=0.8, k=2.0
    )
    assert a_high_u <= a_low_u + EPS
    assert authority_under_uncertainty(
        a_max=1.0, constitution_factor=0.0, recovery_factor=1.0, uncertainty=0.0, k=1.0
    ) == 0.0

    err = ErrorVector(1, 2, 3, 4, 5, 6, 7)
    weights = {
        "prediction": 1,
        "calibration": 1,
        "scope": 1,
        "drift": 1,
        "recovery": 1,
        "authority": 1,
        "provenance": 1,
    }
    assert integrated_error(err, weights) == 28

    allocation = adaptive_resource_allocation(
        [
            ResourceSignal("counterexample", 1.0, 0.8, 1.0, 0.8, 1.0),
            ResourceSignal("prediction", 1.0, 0.3, 0.2, 0.5, 1.0),
            ResourceSignal("recovery", 0.8, 0.5, 0.6, 0.4, 1.0),
        ],
        total_budget=100.0,
        per_task_cap_fraction=0.6,
    )
    assert math.isclose(sum(allocation.values()), 100.0, rel_tol=1e-9, abs_tol=1e-9)
    assert max(allocation.values()) <= 60.0 + 1e-9

    assert route_domain("ultraperipheral_collision") == ["equivalent_photon_flux_operator"]
    assert route_domain("quantum_phase_space") == ["weyl_wigner_phase_space_operator"]
    assert route_domain("general_reasoning") == []

    state = UnifiedState(
        raw_problem_id="omega-1",
        representation_id="phi-0",
        uncertainty=0.2,
        authority=0.8,
        recovery_ready=True,
        evidence_scope=1.0,
        claim_scope=1.0,
        lease_valid=True,
        failure_count=2,
        external_gate_state="OPEN",
    )
    updated = next_state(state, new_uncertainty=0.9, failure_observed=True)
    assert updated.authority <= state.authority + EPS
    assert updated.failure_count == state.failure_count + 1

    assert correction_decision(gate_ok=False, severe_failure=False, recoverable=True, drift=False) == "ABSTAIN"
    assert correction_decision(gate_ok=True, severe_failure=True, recoverable=False, drift=False) == "RETIRE"
    assert correction_decision(gate_ok=True, severe_failure=True, recoverable=True, drift=False) == "ROLLBACK"
    assert correction_decision(gate_ok=True, severe_failure=False, recoverable=True, drift=True) == "REVALIDATE"

    print("WUXIANG_WUJI_UNIFIED_INTEGRATION_READY")
    print("HARD_GATE_NONOVERRIDE_ACTIVE")
    print("FAILURE_MEMORY_PRESERVED")
    print("DOMAIN_OPERATORS_ROUTED_NOT_GLOBALIZED")
    print("REAL_WORLD_ATTACK_AUTHORITY_ZERO")


if __name__ == "__main__":
    _sanity()
