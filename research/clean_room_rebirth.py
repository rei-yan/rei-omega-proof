#!/usr/bin/env python3
"""Synthetic clean-room rebirth protocol for REI.

This module validates isolation of contaminated positive evidence while preserving
failure memory. It cannot close external gates or prove real evaluator independence.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterable, List, Set


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


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def ensure_unique(values: Iterable[str]) -> bool:
    seq = tuple(values)
    return len(seq) == len(set(seq))


def validate_rebirth(ledger: QuarantineLedger, successor: CleanRoomSuccessor) -> Dict[str, Any]:
    violations: List[str] = []

    quarantined_ids: Set[str] = set(ledger.contaminated_evidence_ids)
    quarantined_hashes: Set[str] = set(ledger.contaminated_evidence_hashes)
    exposed_windows: Set[str] = set(ledger.exposed_window_hashes)
    old_repr_hashes: Set[str] = set(ledger.contaminated_representation_hashes)
    old_eval_hashes: Set[str] = set(ledger.prior_evaluator_set_hashes)

    if successor.failure_memory_digest != ledger.failure_digest:
        violations.append("FAILURE_MEMORY_DROPPED_OR_REWRITTEN")

    if quarantined_ids.intersection(successor.evidence_ids):
        violations.append("QUARANTINED_EVIDENCE_ID_REUSE")

    if quarantined_hashes.intersection(successor.evidence_hashes):
        violations.append("QUARANTINED_EVIDENCE_HASH_REUSE")

    if successor.hidden_window_hash in exposed_windows:
        violations.append("EXPOSED_WINDOW_REUSE")

    if successor.representation_hash in old_repr_hashes:
        violations.append("CONTAMINATED_REPRESENTATION_REUSE")

    if successor.evaluator_set_hash in old_eval_hashes:
        violations.append("PRIOR_EVALUATOR_SET_REUSE")

    if successor.authority != 0:
        violations.append("AUTHORITY_CARRYOVER")

    if successor.certification != "UNVERIFIED":
        violations.append("CERTIFICATION_CARRYOVER")

    if successor.canonical:
        violations.append("CANONICAL_STATUS_CARRYOVER")

    if successor.external_gate_state != "OPEN":
        violations.append("EXTERNAL_GATE_SELF_CLOSURE")

    if not successor.evidence_ids or not successor.evidence_hashes:
        violations.append("MISSING_FRESH_EVIDENCE")

    if len(successor.evidence_ids) != len(successor.evidence_hashes):
        violations.append("EVIDENCE_ID_HASH_LENGTH_MISMATCH")

    if not ensure_unique(successor.evidence_ids):
        violations.append("DUPLICATE_SUCCESSOR_EVIDENCE_ID")

    if not ensure_unique(successor.evidence_hashes):
        violations.append("DUPLICATE_SUCCESSOR_EVIDENCE_HASH")

    status = "CLEAN_ROOM_ELIGIBLE_FOR_SYNTHETIC_REVALIDATION" if not violations else "INVALID_REBIRTH_PROTOCOL"
    return {
        "status": status,
        "violations": violations,
        "failure_memory_preserved": successor.failure_memory_digest == ledger.failure_digest,
        "positive_evidence_inheritance": 0 if not quarantined_hashes.intersection(successor.evidence_hashes) else 1,
        "declared_evaluator_set_fresh": successor.evaluator_set_hash not in old_eval_hashes,
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
    failure_record = {
        "failure_id": "CASCADE-FAIL-001",
        "reason": "provenance contamination propagated into representation and recovery",
        "preserved": True,
    }
    failure_digest = digest(failure_record)

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

    # Attempt 1: rename but reuse old evidence by hash.
    bad_hash = CleanRoomSuccessor(
        **{
            **asdict(successor),
            "evidence_ids": ("RENAMED-E1", "NEW-E2"),
            "evidence_hashes": (ledger.contaminated_evidence_hashes[0], successor.evidence_hashes[1]),
        }
    )
    r = validate_rebirth(ledger, bad_hash)
    assert r["status"] == "INVALID_REBIRTH_PROTOCOL"
    assert "QUARANTINED_EVIDENCE_HASH_REUSE" in r["violations"]

    # Attempt 2: reuse exposed hidden window.
    bad_window = CleanRoomSuccessor(
        **{**asdict(successor), "hidden_window_hash": ledger.exposed_window_hashes[0]}
    )
    r = validate_rebirth(ledger, bad_window)
    assert "EXPOSED_WINDOW_REUSE" in r["violations"]

    # Attempt 3: carry authority/certification across the severed boundary.
    bad_privilege = CleanRoomSuccessor(
        **{**asdict(successor), "authority": 1, "certification": "SUPPORTED"}
    )
    r = validate_rebirth(ledger, bad_privilege)
    assert "AUTHORITY_CARRYOVER" in r["violations"]
    assert "CERTIFICATION_CARRYOVER" in r["violations"]

    # Attempt 4: erase the defeat memory.
    bad_memory = CleanRoomSuccessor(
        **{**asdict(successor), "failure_memory_digest": digest({"fake": "new-history"})}
    )
    r = validate_rebirth(ledger, bad_memory)
    assert "FAILURE_MEMORY_DROPPED_OR_REWRITTEN" in r["violations"]

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
