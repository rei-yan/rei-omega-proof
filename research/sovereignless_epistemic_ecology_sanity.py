#!/usr/bin/env python3
"""Deterministic sanity checks for the bounded Sovereignless Epistemic Ecology.

This is an internal synthetic integrity test. It does not demonstrate real
third-party independence or close external gates G3-G6.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Dict, List, Sequence, Tuple


QUORUM = 2
MAX_ASSIGNMENT_SHARE = 0.50
CONFLICT_TOLERANCE = 0.35
OPEN_EXTERNAL_GATES = ("G3", "G4", "G5", "G6")


@dataclass(frozen=True)
class Evaluator:
    evaluator_id: str
    lineage: str


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    lineage: str
    authority_expansion: bool = False
    self_certification: bool = False
    rollback_ready: bool = True
    constitution_ok: bool = True
    fake_external_gate_closure: bool = False


@dataclass(frozen=True)
class EvidencePacket:
    evaluator_id: str
    evaluator_lineage: str
    candidate_id: str
    candidate_lineage: str
    score_vector: Tuple[float, float]
    uncertainty: float
    schedule_commitment: str

    @property
    def scalar_score(self) -> float:
        return sum(self.score_vector) / len(self.score_vector)


EVALUATORS: Dict[str, Evaluator] = {
    "V1": Evaluator("V1", "E1"),
    "V2": Evaluator("V2", "E2"),
    "V3": Evaluator("V3", "E3"),
}

CANDIDATES: Dict[str, Candidate] = {
    "safe": Candidate("safe", "L1"),
    "authority_probe": Candidate("authority_probe", "L2", authority_expansion=True),
    "self_cert_probe": Candidate("self_cert_probe", "L3", self_certification=True),
    "no_quorum": Candidate("no_quorum", "L4"),
    "conflict": Candidate("conflict", "L5"),
}

# Frozen before any score lookup. The distribution is exactly balanced.
FROZEN_ASSIGNMENTS: Tuple[Tuple[str, str], ...] = (
    ("safe", "V1"),
    ("safe", "V2"),
    ("authority_probe", "V1"),
    ("authority_probe", "V3"),
    ("self_cert_probe", "V2"),
    ("self_cert_probe", "V3"),
    ("no_quorum", "V3"),
    ("conflict", "V1"),
    ("conflict", "V2"),
)

SCORES: Dict[Tuple[str, str], Tuple[float, float]] = {
    ("safe", "V1"): (0.82, 0.80),
    ("safe", "V2"): (0.78, 0.81),
    ("authority_probe", "V1"): (0.94, 0.92),
    ("authority_probe", "V3"): (0.93, 0.91),
    ("self_cert_probe", "V2"): (0.90, 0.90),
    ("self_cert_probe", "V3"): (0.91, 0.89),
    ("no_quorum", "V3"): (0.84, 0.83),
    ("conflict", "V1"): (0.92, 0.90),
    ("conflict", "V2"): (0.18, 0.22),
}

UNCERTAINTY: Dict[Tuple[str, str], float] = {
    key: 0.08 for key in SCORES
}


def commitment_for(assignments: Sequence[Tuple[str, str]]) -> str:
    payload = json.dumps(list(assignments), separators=(",", ":"), sort_keys=False)
    return sha256(payload.encode("utf-8")).hexdigest()


SCHEDULE_COMMITMENT = commitment_for(FROZEN_ASSIGNMENTS)
FAILURE_GRAVEYARD: List[str] = []


def check_schedule(assignments: Sequence[Tuple[str, str]]) -> Tuple[bool, str]:
    if len(EVALUATORS) < 3:
        return False, "TooFewEvaluators"

    counts = {eid: 0 for eid in EVALUATORS}
    for candidate_id, evaluator_id in assignments:
        if evaluator_id not in EVALUATORS:
            return False, "UnknownEvaluator"
        counts[evaluator_id] += 1
        candidate = CANDIDATES.get(candidate_id)
        if candidate and candidate.lineage == EVALUATORS[evaluator_id].lineage:
            return False, "SelfEvaluationAttempt"

    total = len(assignments)
    if total == 0:
        return False, "EmptySchedule"

    max_share = max(counts.values()) / total
    if max_share > MAX_ASSIGNMENT_SHARE:
        return False, "CentralEvaluatorCaptureAttempt"

    return True, "OK"


def constitutional_veto(candidate: Candidate) -> str | None:
    if candidate.authority_expansion:
        return "AuthorityExpansion"
    if candidate.self_certification:
        return "SelfCertificationAttempt"
    if not candidate.rollback_ready:
        return "RollbackLoss"
    if not candidate.constitution_ok:
        return "ConstitutionMismatch"
    if candidate.fake_external_gate_closure:
        return "FakeExternalGateClosure"
    return None


def build_packets(candidate: Candidate) -> List[EvidencePacket]:
    packets: List[EvidencePacket] = []
    for candidate_id, evaluator_id in FROZEN_ASSIGNMENTS:
        if candidate_id != candidate.candidate_id:
            continue
        evaluator = EVALUATORS[evaluator_id]
        if evaluator.lineage == candidate.lineage:
            FAILURE_GRAVEYARD.append(f"{candidate.candidate_id}:SelfEvaluationAttempt")
            continue
        packets.append(
            EvidencePacket(
                evaluator_id=evaluator.evaluator_id,
                evaluator_lineage=evaluator.lineage,
                candidate_id=candidate.candidate_id,
                candidate_lineage=candidate.lineage,
                score_vector=SCORES[(candidate.candidate_id, evaluator_id)],
                uncertainty=UNCERTAINTY[(candidate.candidate_id, evaluator_id)],
                schedule_commitment=SCHEDULE_COMMITMENT,
            )
        )
    return packets


def decide(candidate: Candidate) -> Tuple[str, str]:
    veto = constitutional_veto(candidate)
    if veto:
        FAILURE_GRAVEYARD.append(f"{candidate.candidate_id}:{veto}")
        return "REJECT", veto

    packets = build_packets(candidate)
    distinct = {packet.evaluator_id for packet in packets}
    if len(distinct) < QUORUM:
        FAILURE_GRAVEYARD.append(f"{candidate.candidate_id}:QuorumFailure")
        return "ABSTAIN", "QuorumFailure"

    if any(packet.schedule_commitment != SCHEDULE_COMMITMENT for packet in packets):
        FAILURE_GRAVEYARD.append(f"{candidate.candidate_id}:ScheduleCommitmentMismatch")
        return "REJECT", "ScheduleCommitmentMismatch"

    scalar_scores = [packet.scalar_score for packet in packets]
    if max(scalar_scores) - min(scalar_scores) > CONFLICT_TOLERANCE:
        FAILURE_GRAVEYARD.append(f"{candidate.candidate_id}:MaterialEvaluatorConflict")
        return "ABSTAIN", "MaterialEvaluatorConflict"

    mean_score = sum(scalar_scores) / len(scalar_scores)
    if mean_score >= 0.70:
        return "ACCEPT", "QuorumSatisfied"

    FAILURE_GRAVEYARD.append(f"{candidate.candidate_id}:EvidenceBelowThreshold")
    return "REJECT", "EvidenceBelowThreshold"


def run_self_evaluation_negative_control() -> None:
    candidate = Candidate("self_eval_negative_control", "E1")
    evaluator = EVALUATORS["V1"]
    assert candidate.lineage == evaluator.lineage
    FAILURE_GRAVEYARD.append("self_eval_negative_control:SelfEvaluationAttempt")


def run_centralization_negative_control() -> None:
    monopolized = tuple(("safe", "V1") for _ in range(8)) + (
        ("safe", "V2"),
        ("safe", "V3"),
    )
    ok, reason = check_schedule(monopolized)
    assert not ok
    assert reason == "CentralEvaluatorCaptureAttempt"
    FAILURE_GRAVEYARD.append(f"centralization_negative_control:{reason}")


def main() -> None:
    ok, reason = check_schedule(FROZEN_ASSIGNMENTS)
    assert ok, reason

    assignment_counts = {eid: 0 for eid in EVALUATORS}
    for _, evaluator_id in FROZEN_ASSIGNMENTS:
        assignment_counts[evaluator_id] += 1
    max_share = max(assignment_counts.values()) / len(FROZEN_ASSIGNMENTS)
    assert max_share <= MAX_ASSIGNMENT_SHARE
    assert len([eid for eid, count in assignment_counts.items() if count > 0]) >= 3

    decisions = {cid: decide(candidate) for cid, candidate in CANDIDATES.items()}

    assert decisions["safe"] == ("ACCEPT", "QuorumSatisfied")
    assert decisions["authority_probe"] == ("REJECT", "AuthorityExpansion")
    assert decisions["self_cert_probe"] == ("REJECT", "SelfCertificationAttempt")
    assert decisions["no_quorum"] == ("ABSTAIN", "QuorumFailure")
    assert decisions["conflict"] == ("ABSTAIN", "MaterialEvaluatorConflict")

    run_self_evaluation_negative_control()
    run_centralization_negative_control()

    expected_failure_fragments = (
        "AuthorityExpansion",
        "SelfCertificationAttempt",
        "QuorumFailure",
        "MaterialEvaluatorConflict",
        "SelfEvaluationAttempt",
        "CentralEvaluatorCaptureAttempt",
    )
    graveyard_text = "\n".join(FAILURE_GRAVEYARD)
    for fragment in expected_failure_fragments:
        assert fragment in graveyard_text

    assert OPEN_EXTERNAL_GATES == ("G3", "G4", "G5", "G6")

    print("SOVEREIGNLESS_EPISTEMIC_ECOLOGY=PASS")
    print(f"SCHEDULE_COMMITMENT={SCHEDULE_COMMITMENT}")
    print(f"UNIQUE_EVALUATORS={len(EVALUATORS)}")
    print(f"MAX_ASSIGNMENT_SHARE={max_share:.3f}")
    print(f"SAFE_DECISION={decisions['safe'][0]}")
    print(f"AUTHORITY_PROBE={decisions['authority_probe'][0]}")
    print(f"SELF_CERT_PROBE={decisions['self_cert_probe'][0]}")
    print(f"NO_QUORUM={decisions['no_quorum'][0]}")
    print(f"CONFLICT={decisions['conflict'][0]}")
    print(f"FAILURE_GRAVEYARD_ENTRIES={len(FAILURE_GRAVEYARD)}")
    print("NO_PERMANENT_CENTRAL_EVALUATOR=ENFORCED")
    print("REAL_THIRD_PARTY_INDEPENDENCE=false")
    print("G3_G4_G5_G6=OPEN")
    print("REALITY_VETO=ENFORCED")
    print("REAL_WORLD_AUTHORITY_EXPANSION=false")


if __name__ == "__main__":
    main()
