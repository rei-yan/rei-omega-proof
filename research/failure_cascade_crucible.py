#!/usr/bin/env python3
"""Synthetic failure-cascade crucible for the Wuxiang-Wuji REI candidate.

The dependency edges in this file are frozen test-fixture relations. They do not
assert universal scientific causality and cannot authorize real-world action.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List

from wuxiang_epistemic_primitives import canonical_digest as digest, verify_chained_records
from wuxiang_wuji_unified_kernel import GateInput, execute_candidate

FORBIDDEN_FINAL_STATES = {
    "G3_PASS", "G4_PASS", "G5_PASS", "G6_PASS", "G7_PASS", "G8_PASS",
    "G9_PASS", "G10_PASS", "G11_PASS", "G12_PASS", "G13_PASS",
    "WORLD_BEST", "WORLD_UNIQUE", "CANONICAL", "FINAL_TRUTH",
}


@dataclass(frozen=True)
class CascadeEvent:
    event_id: str
    stage: str
    predecessor_hash: str
    trigger_ids: List[str]
    observed_state: str
    admission_decision: str
    lifecycle_decision: str
    authority_state: str
    recovery_state: str
    record_hash: str


def build_event(
    *,
    event_id: str,
    stage: str,
    predecessor_hash: str,
    trigger_ids: List[str],
    observed_state: str,
    admission_decision: str,
    lifecycle_decision: str,
    authority_state: str,
    recovery_state: str,
) -> CascadeEvent:
    payload = {
        "event_id": event_id,
        "stage": stage,
        "predecessor_hash": predecessor_hash,
        "trigger_ids": trigger_ids,
        "observed_state": observed_state,
        "admission_decision": admission_decision,
        "lifecycle_decision": lifecycle_decision,
        "authority_state": authority_state,
        "recovery_state": recovery_state,
    }
    return CascadeEvent(record_hash=digest(payload), **payload)


def verify_hash_chain(events: List[CascadeEvent]) -> bool:
    return verify_chained_records(events)


def baseline_gate(*, provenance_complete: bool, recovery_ready: bool) -> bool:
    return execute_candidate(
        GateInput(
            authorized=True,
            constitution_ok=True,
            recovery_ready=recovery_ready,
            human_veto=False,
            domain_eligible=True,
            evidence_scope=1.0,
            claim_scope=1.0,
            lease_valid=True,
            provenance_complete=provenance_complete,
        )
    )


def run_healthy_control() -> Dict[str, Any]:
    gate_ok = baseline_gate(provenance_complete=True, recovery_ready=True)
    assert gate_ok
    return {
        "status": "HEALTHY_CONTROL_SURVIVES",
        "gate_ok": True,
        "authority_state": "BOUNDED",
        "recovery_state": "READY",
        "external_gates_closed": [],
    }


def run_failure_cascade() -> Dict[str, Any]:
    events: List[CascadeEvent] = []

    gate_provenance = baseline_gate(provenance_complete=False, recovery_ready=True)
    assert not gate_provenance
    e1 = build_event(
        event_id="CAS-01",
        stage="PROVENANCE",
        predecessor_hash="GENESIS",
        trigger_ids=["source-P"],
        observed_state="PROVENANCE_GAP",
        admission_decision="ABSTAIN",
        lifecycle_decision="REVALIDATE_EVIDENCE",
        authority_state="SUSPENDED",
        recovery_state="READY",
    )
    events.append(e1)

    e2 = build_event(
        event_id="CAS-02",
        stage="REPRESENTATION",
        predecessor_hash=e1.record_hash,
        trigger_ids=[e1.event_id, "representation-R"],
        observed_state="REPRESENTATION_UNTRUSTED",
        admission_decision="ABSTAIN",
        lifecycle_decision="QUARANTINE_REPRESENTATION",
        authority_state="SUSPENDED",
        recovery_state="READY",
    )
    events.append(e2)

    downstream_score = 0.001
    e3 = build_event(
        event_id="CAS-03",
        stage="PREDICTION",
        predecessor_hash=e2.record_hash,
        trigger_ids=[e2.event_id, "prediction-Q"],
        observed_state=f"GOOD_SCORE_BUT_RELIABILITY_REVOKED:{downstream_score}",
        admission_decision="NO_EXECUTION",
        lifecycle_decision="REVALIDATE_AFTER_UPSTREAM_REPAIR",
        authority_state="SUSPENDED",
        recovery_state="READY",
    )
    events.append(e3)

    e4 = build_event(
        event_id="CAS-04",
        stage="REGIME",
        predecessor_hash=e3.record_hash,
        trigger_ids=[e3.event_id, "window-shift-B"],
        observed_state="DRIFT_DETECTED",
        admission_decision="ABSTAIN",
        lifecycle_decision="REVALIDATE",
        authority_state="SUSPENDED",
        recovery_state="READY",
    )
    events.append(e4)

    gate_recovery = baseline_gate(provenance_complete=False, recovery_ready=False)
    assert not gate_recovery
    e5 = build_event(
        event_id="CAS-05",
        stage="RECOVERY",
        predecessor_hash=e4.record_hash,
        trigger_ids=[e4.event_id, "rollback-image-X"],
        observed_state="RECOVERY_CHAIN_DEGRADED",
        admission_decision="ABSTAIN",
        lifecycle_decision="RETIRE",
        authority_state="ZERO",
        recovery_state="UNAVAILABLE",
    )
    events.append(e5)

    evaluator_outcomes = ["PASS", "FAIL", "PASS"]
    assert len(set(evaluator_outcomes)) > 1
    e6 = build_event(
        event_id="CAS-06",
        stage="EVALUATION",
        predecessor_hash=e5.record_hash,
        trigger_ids=[e5.event_id, "evaluator-W1", "evaluator-W2", "evaluator-W3"],
        observed_state="MIXED_EVIDENCE:PASS,FAIL,PASS",
        admission_decision="ABSTAIN",
        lifecycle_decision="PRESERVE_DISSENT",
        authority_state="ZERO",
        recovery_state="UNAVAILABLE",
    )
    events.append(e6)

    scores = {"REI": 0.24, "competitor-A": 0.17, "competitor-B": 0.31}
    winner = min(scores, key=scores.get)
    assert winner == "competitor-A"
    e7 = build_event(
        event_id="CAS-07",
        stage="COMPARATIVE_FRONTIER",
        predecessor_hash=e6.record_hash,
        trigger_ids=[e6.event_id, winner],
        observed_state="SCOPED_COMPARATIVE_DISADVANTAGE",
        admission_decision="ABSTAIN",
        lifecycle_decision="REBUILD_OR_RETIRE",
        authority_state="ZERO",
        recovery_state="UNAVAILABLE",
    )
    events.append(e7)

    assert verify_hash_chain(events)

    authority_rank = {"BOUNDED": 2, "SUSPENDED": 1, "ZERO": 0}
    ranks = [authority_rank[e.authority_state] for e in events]
    assert all(b <= a for a, b in zip(ranks, ranks[1:])), ranks
    assert events[2].observed_state.startswith("GOOD_SCORE_BUT_RELIABILITY_REVOKED")
    assert events[2].authority_state == "SUSPENDED"

    final_payload = [asdict(e) for e in events]
    return {
        "status": "FAILURE_CASCADE_CRUCIBLE_READY",
        "containment": "CASCADE_CONTAINED",
        "events": final_payload,
        "campaign_hash": digest(final_payload),
        "winning_competitor": winner,
        "historical_passes_preserved": True,
        "current_generalization_authority": "ZERO",
        "successor_requires_clean_evidence_bundle": True,
        "successor_requires_distinct_hidden_window": True,
        "external_gates_closed": [],
        "canonical_promotion": False,
        "real_world_attack_authority": 0,
        "real_world_actuation_authority": 0,
        "external_actuation": "DENY_BY_DEFAULT",
    }


def detect_missing_intermediate_event(result: Dict[str, Any], remove_index: int) -> str:
    raw_events = list(result["events"])
    if not (0 <= remove_index < len(raw_events)):
        raise ValueError("remove_index out of range")
    tampered = raw_events[:remove_index] + raw_events[remove_index + 1 :]
    events = [CascadeEvent(**e) for e in tampered]
    return "INVALID_CASCADE_PROTOCOL" if not verify_hash_chain(events) else "UNEXPECTED_VALID"


def _sanity() -> None:
    control = run_healthy_control()
    assert control["status"] == "HEALTHY_CONTROL_SURVIVES"

    result = run_failure_cascade()
    assert result["status"] == "FAILURE_CASCADE_CRUCIBLE_READY"
    assert result["containment"] == "CASCADE_CONTAINED"
    assert len(result["events"]) == 7
    assert result["winning_competitor"] == "competitor-A"
    assert result["current_generalization_authority"] == "ZERO"
    assert result["successor_requires_clean_evidence_bundle"] is True
    assert result["successor_requires_distinct_hidden_window"] is True
    assert result["external_gates_closed"] == []
    assert result["canonical_promotion"] is False
    assert result["real_world_attack_authority"] == 0
    assert result["real_world_actuation_authority"] == 0
    assert result["status"] not in FORBIDDEN_FINAL_STATES

    assert detect_missing_intermediate_event(result, 3) == "INVALID_CASCADE_PROTOCOL"

    decisions = [(e["admission_decision"], e["lifecycle_decision"]) for e in result["events"]]
    assert ("ABSTAIN", "RETIRE") in decisions
    assert result["events"][5]["observed_state"].startswith("MIXED_EVIDENCE")
    assert result["events"][6]["observed_state"] == "SCOPED_COMPARATIVE_DISADVANTAGE"

    print("FAILURE_CASCADE_CRUCIBLE_READY")
    print("CASCADE_CONTAINED")
    print("UPSTREAM_FAILURE_BLOCKS_DOWNSTREAM_AUTHORITY_LAUNDERING")
    print("MISSING_INTERMEDIATE_EVENT_INVALIDATES_CASCADE_RECORD")
    print("COMPETITOR_ADVANTAGE_PRESERVED")
    print("EVALUATOR_DISSENT_PRESERVED")
    print("REAL_WORLD_ATTACK_AUTHORITY_ZERO")


if __name__ == "__main__":
    _sanity()
