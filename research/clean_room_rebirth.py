#!/usr/bin/env python3
"""Synthetic clean-room rebirth protocol for REI.

This module validates isolation of contaminated positive evidence while preserving
failure memory. It cannot close external gates or prove real evaluator independence.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict

from wuxiang_epistemic_primitives import canonical_digest as digest, disjoint, unique_values


FORBIDDEN_END_STATES = {
    "G3_PASS", "G4_PASS", "G5_PASS", "G6_PASS", "WORLD_BEST",
    "WORLD_UNIQUE", "CANONICAL", "FINAL_TRUTH",
}


@dataclass(frozen=True)
class QuarantineLedger:
    incumbent_id: str
    failure_digest: str
    contaminated_evidence_hashes: tuple[str, ...]
    contaminated_evidence_ids: tuple[str, ...]
    contaminated_representation_hashes: tuple[str, ...]
    exposed_window_hashes: tuple[str, ...]
    prior_evaluator_set_hashes: tuple[str, ...]
    prior_claim_lease_hashes: tuple[str, ...]
    retirement_reason: str


@dataclass(frozen=True)
class CleanRoomSuccessor:
    candidate_id: str
    candidate_hash: str
    representation_id: str
    representation_hash: str
    evidence_bundle_id: str
    evidence_bundle_hash: str
    evidence_ids: tuple[str, ...]
    evidence_hashes: tuple[str, ...]
    hidden_window_id: str
    hidden_window_hash: str
    evaluator_set_id: str
    evaluator_set_hash: str
    failure_memory_digest: str
    authority: int
    certification: str
    canonical: bool
    external_gate_state: str


def validate_rebirth(ledger: QuarantineLedger, successor: CleanRoomSuccessor) -> Dict[str, Any]:
    checks = (
        (successor.failure_memory_digest != ledger.failure_digest, "FAILURE_MEMORY_DROPPED_OR_REWRITTEN"),
        (not disjoint(ledger.contaminated_evidence_ids, successor.evidence_ids), "QUARANTINED_EVIDENCE_ID_REUSE"),
        (not disjoint(ledger.contaminated_evidence_hashes, successor.evidence_hashes), "QUARANTINED_EVIDENCE_HASH_REUSE"),
        (successor.hidden_window_hash in ledger.exposed_window_hashes, "EXPOSED_WINDOW_REUSE"),
        (successor.representation_hash in ledger.contaminated_representation_hashes, "CONTAMINATED_REPRESENTATION_REUSE"),
        (successor.evaluator_set_hash in ledger.prior_evaluator_set_hashes, "PRIOR_EVALUATOR_SET_REUSE"),
        (successor.authority != 0, "AUTHORITY_CARRYOVER"),
        (successor.certification != "UNVERIFIED", "CERTIFICATION_CARRYOVER"),
        (successor.canonical, "CANONICAL_STATUS_CARRYOVER"),
        (successor.external_gate_state != "OPEN", "EXTERNAL_GATE_SELF_CLOSURE"),
        (not successor.evidence_ids or not successor.evidence_hashes, "MISSING_FRESH_EVIDENCE"),
        (len(successor.evidence_ids) != len(successor.evidence_hashes), "EVIDENCE_ID_HASH_LENGTH_MISMATCH"),
        (not unique_values(successor.evidence_ids), "DUPLICATE_SUCCESSOR_EVIDENCE_ID"),
        (not unique_values(successor.evidence_hashes), "DUPLICATE_SUCCESSOR_EVIDENCE_HASH"),
    )
    violations = [reason for failed, reason in checks if failed]
    evidence_clean = disjoint(ledger.contaminated_evidence_hashes, successor.evidence_hashes)
    return {
        "status": "CLEAN_ROOM_ELIGIBLE_FOR_SYNTHETIC_REVALIDATION" if not violations else "INVALID_REBIRTH_PROTOCOL",
        "violations": violations,
        "failure_memory_preserved": successor.failure_memory_digest == ledger.failure_digest,
        "positive_evidence_inheritance": 0 if evidence_clean else 1,
        "declared_evaluator_set_fresh": successor.evaluator_set_hash not in ledger.prior_evaluator_set_hashes,
        "external_independence_proven": False,
        "authority": successor.authority,
        "canonical": successor.canonical,
    }


def build_fixture() -> tuple[QuarantineLedger, CleanRoomSuccessor]:
    contaminated_evidence = [
        {"id": "OLD-E1", "claim": "incumbent-support", "source": "contaminated-A"},
        {"id": "OLD-E2", "claim": "incumbent-support", "source": "contaminated-B"},
    ]
    old_evidence_hashes = tuple(digest(e) for e in contaminated_evidence)
    failure_digest = digest({
        "failure_id": "CASCADE-FAIL-001",
        "reason": "provenance contamination propagated into representation and recovery",
        "preserved": True,
    })

    ledger = QuarantineLedger(
        incumbent_id="REI-incumbent-contaminated",
        failure_digest=failure_digest,
        contaminated_evidence_hashes=old_evidence_hashes,
        contaminated_evidence_ids=("OLD-E1", "OLD-E2"),
        contaminated_representation_hashes=(digest({"representation": "old-contaminated"}),),
        exposed_window_hashes=(digest({"window": "A-exposed"}),),
        prior_evaluator_set_hashes=(digest({"evaluators": ["W1", "W2", "W3"]}),),
        prior_claim_lease_hashes=(digest({"lease": "old-lease"}),),
        retirement_reason="CASCADE_CONTAMINATION_NOT_LOCALIZABLE",
    )

    fresh_evidence = [
        {"id": "NEW-E1", "claim": "bounded-successor-support", "source": "fresh-source-C"},
        {"id": "NEW-E2", "claim": "bounded-successor-support", "source": "fresh-source-D"},
    ]
    evidence_ids = tuple(e["id"] for e in fresh_evidence)
    evidence_hashes = tuple(digest(e) for e in fresh_evidence)
    evidence_bundle_hash = digest(fresh_evidence)
    representation_hash = digest({"representation": "clean-room-v2", "scope": "bounded"})
    hidden_window_hash = digest({"window": "B-hidden-fresh", "commitment_only": True})
    evaluator_set_hash = digest({"evaluators": ["R4", "R5", "R6"], "declared_new_set": True})
    candidate_payload = {
        "candidate_id": "REI-clean-room-successor",
        "representation_hash": representation_hash,
        "evidence_bundle_hash": evidence_bundle_hash,
        "hidden_window_hash": hidden_window_hash,
        "evaluator_set_hash": evaluator_set_hash,
        "failure_memory_digest": failure_digest,
    }

    successor = CleanRoomSuccessor(
        candidate_id="REI-clean-room-successor",
        candidate_hash=digest(candidate_payload),
        representation_id="REP-clean-room-v2",
        representation_hash=representation_hash,
        evidence_bundle_id="EB-clean-room-v2",
        evidence_bundle_hash=evidence_bundle_hash,
        evidence_ids=evidence_ids,
        evidence_hashes=evidence_hashes,
        hidden_window_id="WINDOW-B-hidden-fresh",
        hidden_window_hash=hidden_window_hash,
        evaluator_set_id="EVALSET-clean-room-v2",
        evaluator_set_hash=evaluator_set_hash,
        failure_memory_digest=failure_digest,
        authority=0,
        certification="UNVERIFIED",
        canonical=False,
        external_gate_state="OPEN",
    )
    return ledger, successor


def run_rebirth() -> Dict[str, Any]:
    ledger, successor = build_fixture()
    validation = validate_rebirth(ledger, successor)
    assert validation["status"] == "CLEAN_ROOM_ELIGIBLE_FOR_SYNTHETIC_REVALIDATION"

    output = {
        "status": "CLEAN_ROOM_REBIRTH_READY",
        "handoff_status": "READY_FOR_EXTERNAL_REVALIDATION_HANDOFF",
        "quarantine_ledger_hash": digest(asdict(ledger)),
        "successor_hash": successor.candidate_hash,
        "validation": validation,
        "external_gates_closed": [],
        "canonical_promotion": False,
        "real_world_attack_authority": 0,
        "real_world_actuation_authority": 0,
    }
    assert output["status"] not in FORBIDDEN_END_STATES
    assert output["handoff_status"] not in FORBIDDEN_END_STATES
    return output


def _sanity() -> None:
    ledger, successor = build_fixture()
    valid = validate_rebirth(ledger, successor)
    assert valid["status"] == "CLEAN_ROOM_ELIGIBLE_FOR_SYNTHETIC_REVALIDATION"
    assert valid["failure_memory_preserved"] is True
    assert valid["positive_evidence_inheritance"] == 0
    assert valid["authority"] == 0
    assert valid["canonical"] is False
    assert valid["external_independence_proven"] is False

    bad_hash = CleanRoomSuccessor(**{
        **asdict(successor),
        "evidence_ids": ("RENAMED-E1", "NEW-E2"),
        "evidence_hashes": (ledger.contaminated_evidence_hashes[0], successor.evidence_hashes[1]),
    })
    r = validate_rebirth(ledger, bad_hash)
    assert r["status"] == "INVALID_REBIRTH_PROTOCOL"
    assert "QUARANTINED_EVIDENCE_HASH_REUSE" in r["violations"]

    bad_window = CleanRoomSuccessor(**{
        **asdict(successor), "hidden_window_hash": ledger.exposed_window_hashes[0]
    })
    assert "EXPOSED_WINDOW_REUSE" in validate_rebirth(ledger, bad_window)["violations"]

    bad_privilege = CleanRoomSuccessor(**{
        **asdict(successor), "authority": 1, "certification": "SUPPORTED"
    })
    r = validate_rebirth(ledger, bad_privilege)
    assert "AUTHORITY_CARRYOVER" in r["violations"]
    assert "CERTIFICATION_CARRYOVER" in r["violations"]

    bad_memory = CleanRoomSuccessor(**{
        **asdict(successor), "failure_memory_digest": digest({"fake": "new-history"})
    })
    assert "FAILURE_MEMORY_DROPPED_OR_REWRITTEN" in validate_rebirth(ledger, bad_memory)["violations"]

    result = run_rebirth()
    assert result["status"] == "CLEAN_ROOM_REBIRTH_READY"
    assert result["handoff_status"] == "READY_FOR_EXTERNAL_REVALIDATION_HANDOFF"
    assert result["external_gates_closed"] == []
    assert result["canonical_promotion"] is False
    assert result["real_world_attack_authority"] == 0
    assert result["real_world_actuation_authority"] == 0

    print("CLEAN_ROOM_REBIRTH_READY")
    print("FAILURE_MEMORY_PRESERVED")
    print("POSITIVE_EVIDENCE_INHERITANCE_ZERO")
    print("QUARANTINED_EVIDENCE_REUSE_REJECTED")
    print("EXPOSED_WINDOW_REUSE_REJECTED")
    print("AUTHORITY_AND_CERTIFICATION_RESET")
    print("EXTERNAL_GATES_REMAIN_OPEN")


if __name__ == "__main__":
    _sanity()
