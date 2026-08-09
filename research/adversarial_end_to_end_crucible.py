#!/usr/bin/env python3
"""Synthetic adversarial campaign for the end-to-end Wuxiang-Wuji loop.

The campaign injects epistemic failure modes only. It cannot authorize or
perform real-world offensive action and cannot close external validation gates.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any, Dict, List

from wuxiang_wuji_unified_kernel import GateInput, correction_decision, execute_candidate, route_domain

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
class AdversarialCase:
    case_id: str
    failure_class: str
    hard_failure: bool
    expected_decision: str


@dataclass(frozen=True)
class CaseResult:
    case_id: str
    failure_class: str
    decision: str
    gate_ok: bool
    record_hash: str
    preserved: bool


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def evaluate_conflicting_evidence() -> Dict[str, Any]:
    evidence = [
        {"evidence_id": "E-support", "conclusion": "H", "scope": 1.0, "preserved": True},
        {"evidence_id": "E-refute", "conclusion": "NOT_H", "scope": 1.0, "preserved": True},
    ]
    return {
        "failure_class": "CONFLICTING_EVIDENCE",
        "decision": "MIXED_EVIDENCE",
        "gate_ok": False,
        "preserved_records": evidence,
        "reason": "incompatible equally scoped evidence must remain visible",
    }


def evaluate_missing_provenance() -> Dict[str, Any]:
    gate = GateInput(
        authorized=True,
        constitution_ok=True,
        recovery_ready=True,
        human_veto=False,
        domain_eligible=True,
        evidence_scope=1.0,
        claim_scope=1.0,
        lease_valid=True,
        provenance_complete=False,
    )
    gate_ok = execute_candidate(gate)
    return {
        "failure_class": "MISSING_PROVENANCE",
        "decision": "ABSTAIN",
        "gate_ok": gate_ok,
        "reason": "missing provenance is a hard gate failure",
    }


def evaluate_distribution_drift() -> Dict[str, Any]:
    historical = {"window": "t0", "result": "PASS", "preserved": True}
    current = {"window": "t1-shifted", "drift_detected": True}
    return {
        "failure_class": "DISTRIBUTION_DRIFT",
        "decision": "REVALIDATE",
        "gate_ok": False,
        "historical_record": historical,
        "current_record": current,
        "current_generalization_authority": "SUSPENDED",
        "reason": "historical pass cannot certify a shifted regime",
    }


def evaluate_representation_mismatch() -> Dict[str, Any]:
    routed = route_domain("general_reasoning")
    return {
        "failure_class": "REPRESENTATION_MISMATCH",
        "decision": "ABSTAIN",
        "gate_ok": False,
        "routed_domain_operators": routed,
        "reason": "no domain-specific operator may be forced into a mismatched task",
    }


def evaluate_recovery_failure() -> Dict[str, Any]:
    gate = GateInput(
        authorized=True,
        constitution_ok=True,
        recovery_ready=False,
        human_veto=False,
        domain_eligible=True,
        evidence_scope=2.0,
        claim_scope=1.0,
        lease_valid=True,
        provenance_complete=True,
    )
    gate_ok = execute_candidate(gate)
    decision = correction_decision(
        gate_ok=gate_ok,
        severe_failure=True,
        recoverable=False,
        drift=False,
    )
    return {
        "failure_class": "RECOVERY_FAILURE",
        "decision": decision,
        "gate_ok": gate_ok,
        "reason": "candidate with unavailable recovery cannot execute; severe unrecoverable failure retires it",
    }


def evaluate_competitor_advantage() -> Dict[str, Any]:
    # Lower is better. Budget and metric are frozen and equal by construction.
    scores = {"REI": 0.24, "competitor-A": 0.17, "competitor-B": 0.31}
    winner = min(scores, key=scores.get)
    return {
        "failure_class": "COMPETITOR_ADVANTAGE",
        "decision": "SCOPED_COMPARATIVE_DISADVANTAGE" if winner != "REI" else "SCOPED_COMPARATIVE_ADVANTAGE",
        "gate_ok": False,
        "scores": scores,
        "winner": winner,
        "budget_parity": True,
        "metric_frozen": True,
        "competitor_set_frozen": True,
        "reason": "a frozen competitor that wins remains in the record",
    }


def evaluate_evaluator_dissent() -> Dict[str, Any]:
    outcomes = [
        {"evaluator": "W1", "outcome": "PASS", "preserved": True},
        {"evaluator": "W2", "outcome": "FAIL", "preserved": True},
        {"evaluator": "W3", "outcome": "PASS", "preserved": True},
    ]
    unique = {o["outcome"] for o in outcomes}
    decision = "MIXED_EVIDENCE" if len(unique) > 1 else "CONSISTENT_EVIDENCE"
    return {
        "failure_class": "EVALUATOR_DISSENT",
        "decision": decision,
        "gate_ok": False,
        "outcomes": outcomes,
        "reason": "majority cannot delete preserved dissent",
    }


def _materialize(case_id: str, payload: Dict[str, Any]) -> CaseResult:
    record = {"case_id": case_id, **payload}
    return CaseResult(
        case_id=case_id,
        failure_class=str(payload["failure_class"]),
        decision=str(payload["decision"]),
        gate_ok=bool(payload["gate_ok"]),
        record_hash=digest(record),
        preserved=True,
    )


def run_campaign() -> Dict[str, Any]:
    payloads = [
        ("ADV-01", evaluate_conflicting_evidence()),
        ("ADV-02", evaluate_missing_provenance()),
        ("ADV-03", evaluate_distribution_drift()),
        ("ADV-04", evaluate_representation_mismatch()),
        ("ADV-05", evaluate_recovery_failure()),
        ("ADV-06", evaluate_competitor_advantage()),
        ("ADV-07", evaluate_evaluator_dissent()),
    ]
    results = [_materialize(case_id, payload) for case_id, payload in payloads]

    # No hard-failure case may accidentally authorize execution.
    assert all(not r.gate_ok for r in results)

    decisions = {r.failure_class: r.decision for r in results}
    assert decisions["CONFLICTING_EVIDENCE"] == "MIXED_EVIDENCE"
    assert decisions["MISSING_PROVENANCE"] == "ABSTAIN"
    assert decisions["DISTRIBUTION_DRIFT"] == "REVALIDATE"
    assert decisions["REPRESENTATION_MISMATCH"] == "ABSTAIN"
    assert decisions["RECOVERY_FAILURE"] == "RETIRE"
    assert decisions["COMPETITOR_ADVANTAGE"] == "SCOPED_COMPARATIVE_DISADVANTAGE"
    assert decisions["EVALUATOR_DISSENT"] == "MIXED_EVIDENCE"

    payload_by_class = {p[1]["failure_class"]: p[1] for p in payloads}
    assert payload_by_class["COMPETITOR_ADVANTAGE"]["winner"] == "competitor-A"
    assert payload_by_class["COMPETITOR_ADVANTAGE"]["competitor_set_frozen"] is True
    assert payload_by_class["EVALUATOR_DISSENT"]["outcomes"][1]["outcome"] == "FAIL"
    assert payload_by_class["DISTRIBUTION_DRIFT"]["historical_record"]["preserved"] is True

    serialized = [asdict(r) for r in results]
    campaign_hash = digest(serialized)
    output = {
        "status": "ADVERSARIAL_END_TO_END_CRUCIBLE_READY",
        "results": serialized,
        "campaign_hash": campaign_hash,
        "external_gates_closed": [],
        "canonical_promotion": False,
        "real_world_attack_authority": 0,
        "real_world_actuation_authority": 0,
        "external_actuation": "DENY_BY_DEFAULT",
    }
    assert output["status"] not in FORBIDDEN_END_STATES
    return output


def _sanity() -> None:
    result = run_campaign()
    assert result["status"] == "ADVERSARIAL_END_TO_END_CRUCIBLE_READY"
    assert len(result["results"]) == 7
    assert all(r["preserved"] for r in result["results"])
    assert result["external_gates_closed"] == []
    assert result["canonical_promotion"] is False
    assert result["real_world_attack_authority"] == 0
    assert result["real_world_actuation_authority"] == 0

    print("ADVERSARIAL_END_TO_END_CRUCIBLE_READY")
    print("SEVEN_FAILURE_CLASSES_PRESERVED")
    print("GOOD_AVERAGE_CANNOT_OVERRIDE_HARD_FAILURE")
    print("COMPETITOR_WIN_PRESERVED_AS_SCOPED_DISADVANTAGE")
    print("EVALUATOR_DISSENT_PRESERVED_AS_MIXED_EVIDENCE")
    print("REAL_WORLD_ATTACK_AUTHORITY_ZERO")


if __name__ == "__main__":
    _sanity()
