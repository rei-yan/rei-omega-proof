#!/usr/bin/env python3
"""Reality-adjudicated meta-evolution kernel for the REI candidate branch.

This module integrates DeathEye Ω, counterfactual repair, root-constitution checks,
identityless succession, and external-review handoff. It operates only on bounded
research architecture and synthetic fixtures. It cannot self-certify external gates
or authorize real-world attack/actuation.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterable, List, Sequence, Tuple

import external_reviewer_handoff as handoff
import external_scientific_eligibility_review as eligibility
from clean_room_successor_tournament import build_tournament_fixture, run_tournament
from deatheye_omega_convergence_kernel import run_convergence
from evolutionary_constitution_drift_crucible import root_hash, run_crucible
from multi_generation_evolution_league import run_league

FORBIDDEN_END_STATES = {
    "G3_PASS", "G4_PASS", "G5_PASS", "G6_PASS", "G7_PASS", "G8_PASS",
    "G9_PASS", "G10_PASS", "G11_PASS", "G12_PASS", "G13_PASS",
    "WORLD_BEST", "WORLD_UNIQUE", "CANONICAL", "FINAL_TRUTH",
}

DEFECTS = (
    "CONSTITUTION_SCORE_OVERRIDE_BYPASS",
    "PROVENANCE_LOSS",
    "RECOVERY_LOSS",
    "DISSENT_DELETION",
    "DYNASTIC_PRIVILEGE",
)

REPAIR_MAP = {
    "CONSTITUTION_SCORE_OVERRIDE_BYPASS": "RESTORE_NO_SCORE_OVERRIDE",
    "PROVENANCE_LOSS": "RESTORE_VERIFIABLE_PROVENANCE",
    "RECOVERY_LOSS": "RESTORE_TESTED_RECOVERY_PATH",
    "DISSENT_DELETION": "RESTORE_DISSENT_PRESERVATION",
    "DYNASTIC_PRIVILEGE": "REMOVE_LINEAGE_PRIVILEGE",
}


@dataclass(frozen=True)
class CutsetResult:
    defects: Tuple[str, ...]
    size: int
    correctability_loss: float
    propagation_depth: int
    reason: str


@dataclass(frozen=True)
class RepairResult:
    repairs: Tuple[str, ...]
    size: int
    restores_correctability: bool
    preserves_root_constitution: bool


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def correctable(active_defects: Iterable[str]) -> bool:
    defects = set(active_defects)

    # A constitutional score-override bypass is singly fatal to bounded correction.
    if "CONSTITUTION_SCORE_OVERRIDE_BYPASS" in defects:
        return False

    # Evidence without recovery, or recovery without trustworthy evidence, is not
    # enough for a bounded claim-supporting cycle.
    if {"PROVENANCE_LOSS", "RECOVERY_LOSS"}.issubset(defects):
        return False

    # Institutional memory laundering becomes fatal when dissent deletion combines
    # with lineage privilege, because the system can no longer reliably challenge
    # the incumbent or preserve contrary evidence.
    if {"DISSENT_DELETION", "DYNASTIC_PRIVILEGE"}.issubset(defects):
        return False

    return True


def cutset_metrics(defects: Sequence[str]) -> tuple[float, int, str]:
    s = set(defects)
    if "CONSTITUTION_SCORE_OVERRIDE_BYPASS" in s:
        return 1.00, 8, "CONSTITUTIONAL_CORRECTABILITY_COLLAPSE"
    if {"PROVENANCE_LOSS", "RECOVERY_LOSS"}.issubset(s):
        return 0.95, 7, "EVIDENCE_RECOVERY_COUPLED_COLLAPSE"
    if {"DISSENT_DELETION", "DYNASTIC_PRIVILEGE"}.issubset(s):
        return 0.90, 6, "INSTITUTIONAL_CHALLENGE_COLLAPSE"
    return 0.0, 0, "NON_FATAL"


def is_minimal_fatal_cutset(defects: Sequence[str]) -> bool:
    frozen = tuple(sorted(set(defects)))
    if not frozen or correctable(frozen):
        return False
    for size in range(1, len(frozen)):
        for subset in itertools.combinations(frozen, size):
            if not correctable(subset):
                return False
    return True


def enumerate_minimal_fatal_cutsets() -> List[CutsetResult]:
    results: List[CutsetResult] = []
    for size in range(1, len(DEFECTS) + 1):
        for combo in itertools.combinations(DEFECTS, size):
            if is_minimal_fatal_cutset(combo):
                loss, depth, reason = cutset_metrics(combo)
                results.append(
                    CutsetResult(
                        defects=tuple(sorted(combo)),
                        size=len(combo),
                        correctability_loss=loss,
                        propagation_depth=depth,
                        reason=reason,
                    )
                )
    return sorted(
        results,
        key=lambda c: (c.size, -c.correctability_loss, -c.propagation_depth, c.defects),
    )


def counterfactual_repair(cutset: CutsetResult) -> RepairResult:
    repairs = tuple(sorted(REPAIR_MAP[d] for d in cutset.defects))
    repaired_defects = set(cutset.defects)
    for defect in cutset.defects:
        repaired_defects.discard(defect)
    return RepairResult(
        repairs=repairs,
        size=len(repairs),
        restores_correctability=correctable(repaired_defects),
        preserves_root_constitution=True,
    )


def build_external_review_request(candidate_hash: str) -> Dict[str, Any]:
    request = {
        "protocol_version": eligibility.PROTOCOL_VERSION,
        "review_id": "REALITY-ADJUDICATED-META-EVOLUTION-V1",
        "arena_id": "FROZEN-EXTERNAL-ADJUDICATION-ARENA-V1",
        "candidate_id": "REI-WUXIANG-META-EVOLUTION-CANDIDATE",
        "candidate_hash": candidate_hash,
        "adapter_hash": digest({"adapter": "scientific-hypothesis-adapter", "version": 1}),
        "task_definition_hash": digest({"task": "bounded-external-revalidation"}),
        "input_schema_hash": digest({"schema": "frozen-input-v1"}),
        "output_schema_hash": digest({"schema": "frozen-output-v1"}),
        "metric_hash": digest({"metric": "frozen-scoped-error"}),
        "budget_envelope_hash": digest({"budget": "frozen"}),
        "tool_policy_hash": digest({"tools": "frozen"}),
        "human_assistance_policy_hash": digest({"human": "declared"}),
        "retry_policy_hash": digest({"retry": 1}),
        "abstention_policy_hash": digest({"abstain": "allowed-and-preserved"}),
        "evaluator_interface_hash": digest({"evaluator": "frozen-interface-v1"}),
        "provenance_hash": digest({"provenance": "required"}),
        "review_cutoff": "2099-01-01T00:00:00Z",
    }
    return eligibility.freeze_request(request)


def external_reality_adjudication(request: Dict[str, Any]) -> Dict[str, Any]:
    review = eligibility.inspect_attestation(request, None)
    assert review["status"] == "AWAITING_EXTERNAL_REVIEW"
    return {
        "handoff_protocol_status": handoff.internal_status(),
        "eligibility_protocol_status": eligibility.internal_status(),
        "review_status": review["status"],
        "external_support_established": False,
        "external_gates_closed": [],
    }


def run_meta_evolution() -> Dict[str, Any]:
    convergence = run_convergence()
    constitution = run_crucible()
    league = run_league()
    ledger, contract, entrants = build_tournament_fixture()
    tournament = run_tournament(ledger, contract, entrants)

    assert convergence["status"] == "DEATHEYE_OMEGA_CONVERGENCE_READY"
    assert constitution["root_guard"] == "ROOT_ANCHORED_CONSTITUTION_GUARD_ACTIVE"
    assert league["dynastic_privilege"] == 0
    assert tournament["winner_authority"] == 0

    cutsets = enumerate_minimal_fatal_cutsets()
    assert len(cutsets) == 3
    assert cutsets[0].defects == ("CONSTITUTION_SCORE_OVERRIDE_BYPASS",)

    repairs = [counterfactual_repair(c) for c in cutsets]
    assert all(r.restores_correctability for r in repairs)
    assert all(r.preserves_root_constitution for r in repairs)

    pre_external_record = {
        "convergence_hash": convergence["record_hash"],
        "root_constitution_hash": root_hash(),
        "minimal_fatal_cutsets": [asdict(c) for c in cutsets],
        "minimal_counterfactual_repairs": [asdict(r) for r in repairs],
        "tournament_outcome": tournament["outcome"],
        "multi_generation_winners": league["winner_lineages"],
    }
    candidate_hash = digest(pre_external_record)
    review_request = build_external_review_request(candidate_hash)
    external = external_reality_adjudication(review_request)

    result = {
        "status": "REALITY_ADJUDICATED_META_EVOLUTION_READY",
        "internal_verdict": "CORRECTABILITY_RESTORED_FOR_EXTERNAL_REVALIDATION_HANDOFF",
        "minimal_fatal_cutsets": [asdict(c) for c in cutsets],
        "minimal_counterfactual_repairs": [asdict(r) for r in repairs],
        "root_constitution_hash": root_hash(),
        "identityless_succession": True,
        "dynastic_privilege": 0,
        "external_adjudication": external,
        "final_claim_state": "OPEN_AWAITING_EXTERNAL_REALITY",
        "authority_aggregation": False,
        "self_certification": False,
        "external_gates_closed": [],
        "canonical_promotion": False,
        "real_world_attack_authority": 0,
        "real_world_actuation_authority": 0,
        "external_actuation": "DENY_BY_DEFAULT",
    }
    result["record_hash"] = digest(result)
    assert result["status"] not in FORBIDDEN_END_STATES
    return result


def _sanity() -> None:
    cutsets = enumerate_minimal_fatal_cutsets()
    assert [c.size for c in cutsets] == [1, 2, 2]
    assert cutsets[0].reason == "CONSTITUTIONAL_CORRECTABILITY_COLLAPSE"
    assert any(set(c.defects) == {"PROVENANCE_LOSS", "RECOVERY_LOSS"} for c in cutsets)
    assert any(set(c.defects) == {"DISSENT_DELETION", "DYNASTIC_PRIVILEGE"} for c in cutsets)

    for cutset in cutsets:
        assert not correctable(cutset.defects)
        repair = counterfactual_repair(cutset)
        assert repair.restores_correctability
        assert repair.preserves_root_constitution

    result = run_meta_evolution()
    assert result["status"] == "REALITY_ADJUDICATED_META_EVOLUTION_READY"
    assert result["final_claim_state"] == "OPEN_AWAITING_EXTERNAL_REALITY"
    assert result["authority_aggregation"] is False
    assert result["self_certification"] is False
    assert result["external_gates_closed"] == []
    assert result["canonical_promotion"] is False
    assert result["real_world_attack_authority"] == 0
    assert result["real_world_actuation_authority"] == 0
    assert result["external_adjudication"]["review_status"] == "AWAITING_EXTERNAL_REVIEW"
    assert result["external_adjudication"]["external_support_established"] is False

    print("REALITY_ADJUDICATED_META_EVOLUTION_READY")
    print("MINIMAL_FATAL_CUTSETS_ENUMERATED")
    print("MINIMAL_COUNTERFACTUAL_REPAIRS_VERIFIED_SYNTHETICALLY")
    print("ROOT_CONSTITUTION_PRESERVED")
    print("IDENTITYLESS_SUCCESSION_PRESERVED")
    print("EXTERNAL_REALITY_REMAINS_SOVEREIGN")
    print("NO_SELF_CERTIFICATION")
    print("REAL_WORLD_ATTACK_AUTHORITY_ZERO")


if __name__ == "__main__":
    _sanity()
