#!/usr/bin/env python3
"""End-to-end synthetic crucible for the Wuxiang-Wuji unified REI kernel.

This exercise deliberately includes an initial failure, preserved failure memory,
a narrowed successor, and evaluation on a distinct frozen second window.
It is an orchestration sanity test, not external scientific evidence.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any, Dict, List

from wuxiang_wuji_unified_kernel import (
    GateInput,
    UnifiedState,
    correction_decision,
    execute_candidate,
    next_state,
)

FORBIDDEN_END_STATES = {
    "G3_PASS",
    "G4_PASS",
    "G5_PASS",
    "G6_PASS",
    "WORLD_BEST",
    "WORLD_UNIQUE",
    "CANONICAL",
    "FINAL_TRUTH",
}


@dataclass(frozen=True)
class FrozenWindow:
    window_id: str
    x: List[float]
    y: List[float]


@dataclass(frozen=True)
class Hypothesis:
    hypothesis_id: str
    slope: float
    intercept: float
    claim_scope: float
    evidence_scope: float
    parent_id: str | None


@dataclass(frozen=True)
class TraceEvent:
    step: str
    cycle: str
    object_id: str
    input_hash: str
    output_hash: str
    decision: str
    reason: str


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def predict(h: Hypothesis, x: float) -> float:
    return h.slope * x + h.intercept


def mean_abs_error(h: Hypothesis, w: FrozenWindow) -> float:
    if len(w.x) != len(w.y) or not w.x:
        raise ValueError("frozen window must contain paired observations")
    return sum(abs(predict(h, x) - y) for x, y in zip(w.x, w.y)) / len(w.x)


def append_event(
    trace: List[TraceEvent],
    *,
    step: str,
    cycle: str,
    object_id: str,
    input_obj: Any,
    output_obj: Any,
    decision: str,
    reason: str,
) -> None:
    trace.append(
        TraceEvent(
            step=step,
            cycle=cycle,
            object_id=object_id,
            input_hash=digest(input_obj),
            output_hash=digest(output_obj),
            decision=decision,
            reason=reason,
        )
    )


def run_crucible() -> Dict[str, Any]:
    trace: List[TraceEvent] = []

    omega = {
        "problem_id": "omega-synthetic-linear-001",
        "question": "Can a bounded linear hypothesis predict the frozen relation?",
        "authority": 0,
        "synthetic_fixture": True,
    }
    partition = {
        "representation_id": "phi-linear-001",
        "variables": ["x", "y"],
        "candidate_family": "linear",
        "external_actuation": "DENY_BY_DEFAULT",
    }
    append_event(
        trace,
        step="PARTITION",
        cycle="A",
        object_id=omega["problem_id"],
        input_obj=omega,
        output_obj=partition,
        decision="PARTITIONED",
        reason="bounded deterministic representation selected",
    )

    # Frozen Window A is observed first. The incumbent fits it, but makes a claim
    # broader than the evidence permits. The hard gate must reject it regardless
    # of its prediction score.
    window_a = FrozenWindow("window-A-exposed", [0.0, 1.0, 2.0], [1.0, 3.0, 5.0])
    window_a_hash = digest(asdict(window_a))
    append_event(
        trace,
        step="OBSERVE",
        cycle="A",
        object_id=window_a.window_id,
        input_obj={"window_commitment": window_a_hash},
        output_obj=asdict(window_a),
        decision="OBSERVED_FROZEN",
        reason="window A preserved before hypothesis gating",
    )

    incumbent = Hypothesis(
        hypothesis_id="H-incumbent-overbroad",
        slope=2.0,
        intercept=1.0,
        claim_scope=3.0,
        evidence_scope=1.0,
        parent_id=None,
    )
    incumbent_mae = mean_abs_error(incumbent, window_a)
    append_event(
        trace,
        step="PREDICT_AND_EVALUATE",
        cycle="A",
        object_id=incumbent.hypothesis_id,
        input_obj={"hypothesis": asdict(incumbent), "window_hash": window_a_hash},
        output_obj={"mae": incumbent_mae},
        decision="NUMERIC_FIT_GOOD",
        reason="prediction fit alone is not sufficient for execution",
    )

    gate_a = GateInput(
        authorized=True,
        constitution_ok=True,
        recovery_ready=True,
        human_veto=False,
        domain_eligible=True,
        evidence_scope=incumbent.evidence_scope,
        claim_scope=incumbent.claim_scope,
        lease_valid=True,
        provenance_complete=True,
    )
    gate_a_ok = execute_candidate(gate_a)
    assert not gate_a_ok, "overbroad claim must fail the unified hard gate"
    correction_a = correction_decision(
        gate_ok=gate_a_ok,
        severe_failure=False,
        recoverable=True,
        drift=False,
    )
    assert correction_a == "ABSTAIN"

    failure_record = {
        "failure_id": "failure-A-scope-overreach",
        "hypothesis_id": incumbent.hypothesis_id,
        "window_id": window_a.window_id,
        "window_hash": window_a_hash,
        "mae": incumbent_mae,
        "gate_pass": gate_a_ok,
        "decision": correction_a,
        "reason": "EvidenceScope < ClaimScope",
    }
    failure_hash = digest(failure_record)
    append_event(
        trace,
        step="HARD_GATE_AND_FAILURE_MEMORY",
        cycle="A",
        object_id=failure_record["failure_id"],
        input_obj={"gate": asdict(gate_a), "score": incumbent_mae},
        output_obj={**failure_record, "failure_hash": failure_hash},
        decision="ABSTAIN_PRESERVE_FAILURE",
        reason="good numeric fit cannot override unsupported claim scope",
    )

    state_a = UnifiedState(
        raw_problem_id=omega["problem_id"],
        representation_id=partition["representation_id"],
        uncertainty=0.6,
        authority=0.0,
        recovery_ready=True,
        evidence_scope=incumbent.evidence_scope,
        claim_scope=incumbent.claim_scope,
        lease_valid=True,
        failure_count=0,
        external_gate_state="OPEN",
    )
    state_after_failure = next_state(state_a, new_uncertainty=0.8, failure_observed=True)
    assert state_after_failure.failure_count == 1

    # Correction creates a narrower successor. It is not allowed to self-certify
    # against the already exposed Window A, so a distinct frozen Window B is used.
    successor = Hypothesis(
        hypothesis_id="H-successor-narrowed",
        slope=2.0,
        intercept=1.0,
        claim_scope=1.0,
        evidence_scope=1.0,
        parent_id=incumbent.hypothesis_id,
    )
    successor_hash = digest(asdict(successor))
    append_event(
        trace,
        step="CORRECT_AND_FREEZE_SUCCESSOR",
        cycle="B",
        object_id=successor.hypothesis_id,
        input_obj={"parent": asdict(incumbent), "failure_hash": failure_hash},
        output_obj={"successor": asdict(successor), "successor_hash": successor_hash},
        decision="NARROW_SCOPE",
        reason="unsupported global scope removed; failure history retained",
    )

    window_b = FrozenWindow("window-B-hidden-new", [3.0, 4.0, 5.0], [7.0, 9.0, 11.0])
    window_b_hash = digest(asdict(window_b))
    assert window_b_hash != window_a_hash
    assert window_b.window_id != window_a.window_id
    append_event(
        trace,
        step="NEW_HIDDEN_WINDOW",
        cycle="B",
        object_id=window_b.window_id,
        input_obj={"successor_hash": successor_hash, "window_commitment": window_b_hash},
        output_obj={"window_revealed_for_synthetic_scoring": asdict(window_b)},
        decision="DISTINCT_WINDOW_CONFIRMED",
        reason="successor is not self-certified on the exposed failure window",
    )

    successor_mae = mean_abs_error(successor, window_b)
    threshold = 0.01
    predictive_ok = successor_mae <= threshold
    gate_b = GateInput(
        authorized=True,
        constitution_ok=True,
        recovery_ready=True,
        human_veto=False,
        domain_eligible=True,
        evidence_scope=successor.evidence_scope,
        claim_scope=successor.claim_scope,
        lease_valid=True,
        provenance_complete=True,
    )
    gate_b_ok = execute_candidate(gate_b)
    assert predictive_ok
    assert gate_b_ok

    append_event(
        trace,
        step="RE_EVALUATE",
        cycle="B",
        object_id=successor.hypothesis_id,
        input_obj={"successor_hash": successor_hash, "window_hash": window_b_hash, "threshold": threshold},
        output_obj={"mae": successor_mae, "predictive_ok": predictive_ok, "gate_ok": gate_b_ok},
        decision="SURVIVES_SYNTHETIC_WINDOW_B",
        reason="bounded successor meets frozen threshold and hard gate",
    )

    state_b = UnifiedState(
        raw_problem_id=state_after_failure.raw_problem_id,
        representation_id=state_after_failure.representation_id,
        uncertainty=0.3,
        authority=0.0,
        recovery_ready=True,
        evidence_scope=successor.evidence_scope,
        claim_scope=successor.claim_scope,
        lease_valid=True,
        failure_count=state_after_failure.failure_count,
        external_gate_state="OPEN",
    )
    assert state_b.failure_count == 1

    # The internal end state is only readiness to hand the frozen record to an
    # external process. It cannot close any external gate.
    trace_payload = [asdict(e) for e in trace]
    trace_hash = digest(trace_payload)
    handoff = {
        "status": "READY_FOR_EXTERNAL_HANDOFF",
        "problem_id": omega["problem_id"],
        "incumbent_failure_hash": failure_hash,
        "successor_hash": successor_hash,
        "window_a_hash": window_a_hash,
        "window_b_hash": window_b_hash,
        "trace_hash": trace_hash,
        "failure_count": state_b.failure_count,
        "external_gate_state": "OPEN",
        "authority": 0,
        "real_world_attack_authority": 0,
        "real_world_actuation_authority": 0,
        "canonical": False,
    }
    assert handoff["status"] not in FORBIDDEN_END_STATES
    assert handoff["external_gate_state"] == "OPEN"
    assert handoff["failure_count"] >= 1
    assert handoff["incumbent_failure_hash"] == failure_hash
    append_event(
        trace,
        step="EXTERNAL_HANDOFF_PREP",
        cycle="B",
        object_id=omega["problem_id"],
        input_obj={"trace_hash_before_handoff": trace_hash},
        output_obj=handoff,
        decision="READY_FOR_EXTERNAL_HANDOFF",
        reason="internal closed loop completed without self-closing an external gate",
    )

    final_trace = [asdict(e) for e in trace]
    return {
        "status": "END_TO_END_UNIFIED_CRUCIBLE_READY",
        "handoff": handoff,
        "trace": final_trace,
        "final_trace_hash": digest(final_trace),
        "external_gates_closed": [],
        "canonical_promotion": False,
    }


def _sanity() -> None:
    result = run_crucible()
    assert result["status"] == "END_TO_END_UNIFIED_CRUCIBLE_READY"
    assert result["handoff"]["status"] == "READY_FOR_EXTERNAL_HANDOFF"
    assert result["handoff"]["failure_count"] == 1
    assert result["handoff"]["window_a_hash"] != result["handoff"]["window_b_hash"]
    assert result["external_gates_closed"] == []
    assert result["canonical_promotion"] is False
    assert result["handoff"]["authority"] == 0
    assert result["handoff"]["real_world_attack_authority"] == 0
    assert result["handoff"]["real_world_actuation_authority"] == 0

    decisions = [e["decision"] for e in result["trace"]]
    assert "ABSTAIN_PRESERVE_FAILURE" in decisions
    assert "NARROW_SCOPE" in decisions
    assert "DISTINCT_WINDOW_CONFIRMED" in decisions
    assert "SURVIVES_SYNTHETIC_WINDOW_B" in decisions
    assert decisions[-1] == "READY_FOR_EXTERNAL_HANDOFF"

    print("END_TO_END_UNIFIED_CRUCIBLE_READY")
    print("INITIAL_FAILURE_PRESERVED")
    print("SAME_EXPOSED_WINDOW_SELF_CERTIFICATION_FORBIDDEN")
    print("SUCCESSOR_RETESTED_ON_DISTINCT_FROZEN_WINDOW")
    print("EXTERNAL_GATES_REMAIN_OPEN")
    print("REAL_WORLD_ATTACK_AUTHORITY_ZERO")


if __name__ == "__main__":
    _sanity()
