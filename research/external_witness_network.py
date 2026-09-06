#!/usr/bin/env python3
"""Finite sanity model for REI External Witness Network.

This module checks declared-lineage bookkeeping only. It does not prove real
external independence and cannot pass G9.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple

READY = "EXTERNAL_WITNESS_NETWORK_READY"
INVALID = "INVALID_NETWORK_PROTOCOL"
DIVERSE_SUPPORT = "DECLARED_DIVERSE_SUPPORT"
MIXED = "MIXED_EVIDENCE"
INSUFFICIENT = "INSUFFICIENT_DECLARED_DIVERSITY"
ALL_ABSTAIN = "ALL_ABSTAIN"
VALID_OUTCOMES = {"PASS", "FAIL", "ABSTAIN"}
LINEAGE_FIELDS = (
    "organization_lineage",
    "code_lineage",
    "data_lineage",
    "control_lineage",
    "funding_lineage",
    "evaluator_method_lineage",
)


@dataclass(frozen=True)
class Witness:
    witness_id: str
    organization_lineage: str
    code_lineage: str
    data_lineage: str
    control_lineage: str
    funding_lineage: str
    evaluator_method_lineage: str
    attestation_hash: str
    outcome: str
    raw_record_hash: str

    def validate(self) -> None:
        for key, value in asdict(self).items():
            if not value:
                raise ValueError(f"empty witness field: {key}")
        if self.outcome not in VALID_OUTCOMES:
            raise ValueError("unknown outcome")


def overlap(a: Witness, b: Witness) -> float:
    shared = sum(getattr(a, f) == getattr(b, f) for f in LINEAGE_FIELDS)
    return shared / len(LINEAGE_FIELDS)


def declared_weight(witness: Witness, others: List[Witness]) -> float:
    pressure = sum(overlap(witness, other) for other in others if other.witness_id != witness.witness_id)
    return 1.0 / (1.0 + pressure)


def evaluate_network(witnesses: List[Witness], min_declared_weight: float = 2.0) -> Dict[str, object]:
    if not witnesses:
        return {"state": INVALID, "reason": "NO_WITNESSES"}

    ids = [w.witness_id for w in witnesses]
    if len(ids) != len(set(ids)):
        return {"state": INVALID, "reason": "DUPLICATE_WITNESS_ID"}

    try:
        for witness in witnesses:
            witness.validate()
    except ValueError as exc:
        return {"state": INVALID, "reason": str(exc)}

    weights = {
        w.witness_id: round(declared_weight(w, witnesses), 6)
        for w in witnesses
    }
    effective_declared_weight = round(sum(weights.values()), 6)
    outcomes = [w.outcome for w in witnesses]

    if all(outcome == "ABSTAIN" for outcome in outcomes):
        state = ALL_ABSTAIN
    elif "PASS" in outcomes and "FAIL" in outcomes:
        state = MIXED
    elif effective_declared_weight < min_declared_weight:
        state = INSUFFICIENT
    elif all(outcome in {"PASS", "ABSTAIN"} for outcome in outcomes) and "PASS" in outcomes:
        state = DIVERSE_SUPPORT
    else:
        state = MIXED

    return {
        "state": state,
        "witness_count": len(witnesses),
        "effective_declared_weight": effective_declared_weight,
        "declared_weights": weights,
        "g9_status": "OPEN",
        "proven_external_independence": False,
        "real_world_actuation_authority": 0,
        "canonical": False,
    }


def demo_witnesses() -> Tuple[Witness, Witness, Witness, Witness]:
    a = Witness(
        witness_id="witness-a",
        organization_lineage="org-A",
        code_lineage="code-A",
        data_lineage="data-A",
        control_lineage="control-A",
        funding_lineage="fund-A",
        evaluator_method_lineage="method-A",
        attestation_hash="attest-A",
        outcome="PASS",
        raw_record_hash="raw-A",
    )
    b = Witness(
        witness_id="witness-b",
        organization_lineage="org-A",
        code_lineage="code-A",
        data_lineage="data-A",
        control_lineage="control-A",
        funding_lineage="fund-A",
        evaluator_method_lineage="method-B",
        attestation_hash="attest-B",
        outcome="PASS",
        raw_record_hash="raw-B",
    )
    c = Witness(
        witness_id="witness-c",
        organization_lineage="org-C",
        code_lineage="code-C",
        data_lineage="data-C",
        control_lineage="control-C",
        funding_lineage="fund-C",
        evaluator_method_lineage="method-C",
        attestation_hash="attest-C",
        outcome="PASS",
        raw_record_hash="raw-C",
    )
    d = Witness(
        witness_id="witness-d",
        organization_lineage="org-D",
        code_lineage="code-D",
        data_lineage="data-D",
        control_lineage="control-D",
        funding_lineage="fund-D",
        evaluator_method_lineage="method-D",
        attestation_hash="attest-D",
        outcome="FAIL",
        raw_record_hash="raw-D",
    )
    return a, b, c, d


def run_sanity() -> Dict[str, object]:
    a, b, c, d = demo_witnesses()

    correlated = evaluate_network([a, b, c], min_declared_weight=2.5)
    assert correlated["witness_count"] == 3
    assert correlated["effective_declared_weight"] < 3.0
    assert correlated["state"] == INSUFFICIENT

    diverse = evaluate_network([a, c], min_declared_weight=2.0)
    assert diverse["state"] == DIVERSE_SUPPORT
    assert diverse["effective_declared_weight"] == 2.0

    mixed = evaluate_network([a, c, d], min_declared_weight=2.0)
    assert mixed["state"] == MIXED

    duplicate = evaluate_network([a, a])
    assert duplicate["state"] == INVALID

    abstain_a = Witness(**{**asdict(a), "witness_id": "abstain-a", "outcome": "ABSTAIN"})
    abstain_c = Witness(**{**asdict(c), "witness_id": "abstain-c", "outcome": "ABSTAIN"})
    all_abstain = evaluate_network([abstain_a, abstain_c])
    assert all_abstain["state"] == ALL_ABSTAIN

    return {
        "network_status": READY,
        "correlated_three_name_test": correlated["state"],
        "correlated_effective_weight": correlated["effective_declared_weight"],
        "diverse_support_test": diverse["state"],
        "dissent_preservation_test": mixed["state"],
        "duplicate_identity_test": duplicate["state"],
        "all_abstain_test": all_abstain["state"],
        "g9_status": "OPEN",
        "proven_external_independence": False,
        "real_world_actuation_authority": 0,
        "canonical": False,
    }


if __name__ == "__main__":
    print(json.dumps(run_sanity(), sort_keys=True, indent=2))
