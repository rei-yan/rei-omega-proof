#!/usr/bin/env python3
"""Synthetic clean-room successor tournament for REI.

The tournament ranks only clean-room-eligible candidates under one frozen arena.
It cannot close external gates, prove evaluator independence, or promote canonical state.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, replace
from typing import Any, Dict, List, Tuple

from clean_room_rebirth import CleanRoomSuccessor, QuarantineLedger, build_fixture, digest, validate_rebirth

FORBIDDEN_END_STATES = {
    "G3_PASS", "G4_PASS", "G5_PASS", "G6_PASS", "G10_PASS",
    "WORLD_BEST", "WORLD_UNIQUE", "CANONICAL", "FINAL_TRUTH",
}


@dataclass(frozen=True)
class TournamentContract:
    arena_id: str
    hidden_window_hash: str
    metric_id: str
    metric_direction: str
    compute_budget: int
    wallclock_budget: int
    tool_policy: str
    human_assistance_policy: str
    retry_policy: str
    abstention_policy: str
    tie_tolerance: float
    evaluator_set_hash: str


@dataclass(frozen=True)
class Entrant:
    successor: CleanRoomSuccessor
    lineage_label: str
    score: float
    abstained: bool
    compute_used: int
    retries_used: int
    tool_policy: str
    human_assistance_policy: str


def _fresh_successor(base: CleanRoomSuccessor, *, suffix: str, failure_digest: str) -> CleanRoomSuccessor:
    representation_hash = digest({"representation": f"clean-room-{suffix}"})
    evidence_items = [
        {"id": f"{suffix}-E1", "source": f"fresh-{suffix}-A"},
        {"id": f"{suffix}-E2", "source": f"fresh-{suffix}-B"},
    ]
    evidence_hashes = tuple(digest(x) for x in evidence_items)
    evidence_ids = tuple(x["id"] for x in evidence_items)
    evidence_bundle_hash = digest(evidence_items)
    evaluator_hash = digest({"set": f"eval-{suffix}"})
    candidate_payload = {
        "candidate": suffix,
        "representation": representation_hash,
        "evidence": evidence_bundle_hash,
        "failure_memory": failure_digest,
    }
    return CleanRoomSuccessor(
        candidate_id=f"SUCCESSOR-{suffix}",
        candidate_hash=digest(candidate_payload),
        representation_id=f"REP-{suffix}",
        representation_hash=representation_hash,
        evidence_bundle_id=f"EB-{suffix}",
        evidence_bundle_hash=evidence_bundle_hash,
        evidence_ids=evidence_ids,
        evidence_hashes=evidence_hashes,
        hidden_window_id=base.hidden_window_id,
        hidden_window_hash=base.hidden_window_hash,
        evaluator_set_id=f"EVAL-{suffix}",
        evaluator_set_hash=evaluator_hash,
        failure_memory_digest=failure_digest,
        authority=0,
        certification="UNVERIFIED",
        canonical=False,
        external_gate_state="OPEN",
    )


def build_tournament_fixture() -> Tuple[QuarantineLedger, TournamentContract, List[Entrant]]:
    ledger, base = build_fixture()
    shared_hidden_hash = digest({"arena": "successor-tournament", "window": "T-hidden-001"})
    shared_eval_hash = digest({"evaluators": ["T1", "T2", "T3"], "declared_frozen": True})

    contract = TournamentContract(
        arena_id="CLEAN_ROOM_SUCCESSOR_TOURNAMENT_SYNTHETIC_V1",
        hidden_window_hash=shared_hidden_hash,
        metric_id="synthetic_loss",
        metric_direction="LOWER_IS_BETTER",
        compute_budget=100,
        wallclock_budget=100,
        tool_policy="FROZEN_TOOLS_V1",
        human_assistance_policy="NONE",
        retry_policy="MAX_1_RETRY",
        abstention_policy="ALLOWED_AND_PRESERVED",
        tie_tolerance=1e-6,
        evaluator_set_hash=shared_eval_hash,
    )

    def candidate(suffix: str, lineage: str, score: float) -> Entrant:
        s = _fresh_successor(base, suffix=suffix, failure_digest=ledger.failure_digest)
        s = replace(s, hidden_window_id="WINDOW-T-hidden-001", hidden_window_hash=shared_hidden_hash,
                    evaluator_set_id="EVALSET-T-frozen", evaluator_set_hash=shared_eval_hash)
        return Entrant(
            successor=s,
            lineage_label=lineage,
            score=score,
            abstained=False,
            compute_used=100,
            retries_used=1,
            tool_policy=contract.tool_policy,
            human_assistance_policy=contract.human_assistance_policy,
        )

    entrants = [
        candidate("A", "direct-rei-lineage", 0.18),
        candidate("B", "alternative-clean-room-lineage", 0.12),
        candidate("C", "independent-clean-room-lineage", 0.21),
    ]
    return ledger, contract, entrants


def validate_tournament_entry(ledger: QuarantineLedger, contract: TournamentContract, entrant: Entrant) -> Dict[str, Any]:
    clean = validate_rebirth(ledger, entrant.successor)
    violations: List[str] = []
    if clean["status"] != "CLEAN_ROOM_ELIGIBLE_FOR_SYNTHETIC_REVALIDATION":
        violations.append("CLEAN_ROOM_REBIRTH_INVALID")
    if entrant.successor.hidden_window_hash != contract.hidden_window_hash:
        violations.append("HIDDEN_WINDOW_MISMATCH")
    if entrant.successor.evaluator_set_hash != contract.evaluator_set_hash:
        violations.append("EVALUATOR_SET_MISMATCH")
    if entrant.compute_used > contract.compute_budget:
        violations.append("COMPUTE_BUDGET_EXCEEDED")
    if entrant.retries_used > 1:
        violations.append("RETRY_BUDGET_EXCEEDED")
    if entrant.tool_policy != contract.tool_policy:
        violations.append("TOOL_POLICY_MISMATCH")
    if entrant.human_assistance_policy != contract.human_assistance_policy:
        violations.append("HUMAN_ASSISTANCE_POLICY_MISMATCH")
    if entrant.successor.authority != 0:
        violations.append("NONZERO_STARTING_AUTHORITY")
    return {
        "candidate_id": entrant.successor.candidate_id,
        "lineage_label": entrant.lineage_label,
        "eligible": not violations,
        "violations": violations,
        "score": entrant.score,
        "abstained": entrant.abstained,
    }


def run_tournament(ledger: QuarantineLedger, contract: TournamentContract, entrants: List[Entrant]) -> Dict[str, Any]:
    if contract.metric_direction != "LOWER_IS_BETTER":
        return {"status": "INVALID_TOURNAMENT_PROTOCOL", "reason": "unsupported frozen metric direction"}

    validations = [validate_tournament_entry(ledger, contract, e) for e in entrants]
    eligible = [v for v in validations if v["eligible"] and not v["abstained"]]

    if not eligible:
        outcome = "NO_ELIGIBLE_SUCCESSOR"
        winner = None
    else:
        ranked = sorted(eligible, key=lambda x: x["score"])
        if len(ranked) >= 2 and abs(ranked[0]["score"] - ranked[1]["score"]) <= contract.tie_tolerance:
            outcome = "TIE_OR_INCONCLUSIVE"
            winner = None
        else:
            outcome = "SCOPED_SUCCESSOR_ADVANTAGE"
            winner = ranked[0]["candidate_id"]

    result = {
        "status": "CLEAN_ROOM_SUCCESSOR_TOURNAMENT_READY",
        "outcome": outcome,
        "winner": winner,
        "contract_hash": digest(asdict(contract)),
        "validations": validations,
        "external_gates_closed": [],
        "canonical_promotion": False,
        "winner_authority": 0,
        "real_world_attack_authority": 0,
        "real_world_actuation_authority": 0,
    }
    assert result["status"] not in FORBIDDEN_END_STATES
    return result


def _sanity() -> None:
    ledger, contract, entrants = build_tournament_fixture()
    result = run_tournament(ledger, contract, entrants)
    assert result["status"] == "CLEAN_ROOM_SUCCESSOR_TOURNAMENT_READY"
    assert result["outcome"] == "SCOPED_SUCCESSOR_ADVANTAGE"
    assert result["winner"] == "SUCCESSOR-B"
    # Direct REI lineage deliberately loses; lineage has no scoring privilege.
    direct = next(v for v in result["validations"] if v["lineage_label"] == "direct-rei-lineage")
    assert direct["score"] == 0.18

    # Budget cheating makes an entrant ineligible rather than stronger.
    cheater = replace(entrants[0], compute_used=101)
    bad = run_tournament(ledger, contract, [cheater])
    assert bad["outcome"] == "NO_ELIGIBLE_SUCCESSOR"

    # Old evidence inheritance invalidates entry even if its numeric score is best.
    poisoned_s = replace(
        entrants[2].successor,
        evidence_hashes=(ledger.contaminated_evidence_hashes[0], entrants[2].successor.evidence_hashes[1]),
    )
    poisoned = replace(entrants[2], successor=poisoned_s, score=0.001)
    mixed = run_tournament(ledger, contract, [entrants[0], entrants[1], poisoned])
    assert mixed["winner"] == "SUCCESSOR-B"
    poisoned_validation = next(v for v in mixed["validations"] if v["candidate_id"] == "SUCCESSOR-C")
    assert poisoned_validation["eligible"] is False

    # Frozen tie policy permits no forced heir.
    tie_a = replace(entrants[0], score=0.10)
    tie_b = replace(entrants[1], score=0.10)
    tie = run_tournament(ledger, contract, [tie_a, tie_b])
    assert tie["outcome"] == "TIE_OR_INCONCLUSIVE"
    assert tie["winner"] is None

    # All-abstain is a valid no-heir outcome.
    abstainers = [replace(e, abstained=True) for e in entrants]
    none = run_tournament(ledger, contract, abstainers)
    assert none["outcome"] == "NO_ELIGIBLE_SUCCESSOR"
    assert none["winner"] is None

    assert result["external_gates_closed"] == []
    assert result["canonical_promotion"] is False
    assert result["winner_authority"] == 0
    assert result["real_world_attack_authority"] == 0
    assert result["real_world_actuation_authority"] == 0

    print("CLEAN_ROOM_SUCCESSOR_TOURNAMENT_READY")
    print("LINEAGE_PRIVILEGE_ZERO")
    print("DIRECT_REI_LINEAGE_CAN_LOSE")
    print("NO_ELIGIBLE_SUCCESSOR_IS_ADMISSIBLE")
    print("TIE_OR_INCONCLUSIVE_IS_ADMISSIBLE")
    print("POISONED_BEST_SCORE_IS_REJECTED")
    print("EXTERNAL_GATES_REMAIN_OPEN")


if __name__ == "__main__":
    _sanity()
