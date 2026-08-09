#!/usr/bin/env python3
"""Concentrated DeathEye Ω evolution stack.

Synthetic epistemic/architectural research only. No real-world targeting or actuation.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from itertools import combinations
from typing import Iterable, Sequence

FAILURE_NODES = (
    "CONSTITUTION_SCORE_OVERRIDE_BYPASS",
    "PROVENANCE_LOSS",
    "RECOVERY_LOSS",
    "DISSENT_DELETION",
    "DYNASTIC_PRIVILEGE",
    "LOCAL_MODEL_MISFIT",
)

FATAL_HYPEREDGES = (
    frozenset({"CONSTITUTION_SCORE_OVERRIDE_BYPASS"}),
    frozenset({"PROVENANCE_LOSS", "RECOVERY_LOSS"}),
    frozenset({"DISSENT_DELETION", "DYNASTIC_PRIVILEGE"}),
)

REPAIR_ACTIONS = {
    "RESTORE_NO_SCORE_OVERRIDE": "CONSTITUTION_SCORE_OVERRIDE_BYPASS",
    "RESTORE_VERIFIABLE_PROVENANCE": "PROVENANCE_LOSS",
    "RESTORE_TESTED_RECOVERY_PATH": "RECOVERY_LOSS",
    "RESTORE_DISSENT_PRESERVATION": "DISSENT_DELETION",
    "REMOVE_LINEAGE_PRIVILEGE": "DYNASTIC_PRIVILEGE",
    "RECALIBRATE_LOCAL_MODEL": "LOCAL_MODEL_MISFIT",
}

FORBIDDEN_END_STATES = {
    "G3_PASS", "G4_PASS", "G5_PASS", "G6_PASS", "G7_PASS", "G8_PASS",
    "G9_PASS", "G10_PASS", "WORLD_BEST", "WORLD_UNIQUE", "CANONICAL", "FINAL_TRUTH",
}


def powerset_nonempty(values: Sequence[str]) -> Iterable[frozenset[str]]:
    for size in range(1, len(values) + 1):
        for combo in combinations(values, size):
            yield frozenset(combo)


def is_fatal(failures: frozenset[str]) -> bool:
    return any(edge.issubset(failures) for edge in FATAL_HYPEREDGES)


def proper_nonempty_subsets(values: frozenset[str]) -> Iterable[frozenset[str]]:
    ordered = sorted(values)
    for size in range(1, len(ordered)):
        for combo in combinations(ordered, size):
            yield frozenset(combo)


def is_minimal_fatal_cutset(failures: frozenset[str]) -> bool:
    return is_fatal(failures) and all(not is_fatal(subset) for subset in proper_nonempty_subsets(failures))


def enumerate_minimal_fatal_cutsets() -> list[frozenset[str]]:
    found = [candidate for candidate in powerset_nonempty(FAILURE_NODES) if is_minimal_fatal_cutset(candidate)]
    return sorted(found, key=lambda item: (len(item), tuple(sorted(item))))


def apply_repairs(failures: frozenset[str], actions: frozenset[str]) -> frozenset[str]:
    unknown = set(actions).difference(REPAIR_ACTIONS)
    if unknown:
        raise ValueError("UNKNOWN_REPAIR_ACTION:" + ",".join(sorted(unknown)))
    repaired_nodes = {REPAIR_ACTIONS[action] for action in actions}
    return frozenset(node for node in failures if node not in repaired_nodes)


def repair_sufficient_for_correctability(cutset: frozenset[str], actions: frozenset[str]) -> bool:
    return not is_fatal(apply_repairs(cutset, actions))


def is_minimal_repair(cutset: frozenset[str], actions: frozenset[str]) -> bool:
    if not actions or not repair_sufficient_for_correctability(cutset, actions):
        return False
    ordered = sorted(actions)
    for size in range(0, len(ordered)):
        for combo in combinations(ordered, size):
            subset = frozenset(combo)
            if repair_sufficient_for_correctability(cutset, subset):
                return False
    return True


def minimal_counterfactual_repairs(cutset: frozenset[str]) -> list[frozenset[str]]:
    relevant_actions = sorted(action for action, node in REPAIR_ACTIONS.items() if node in cutset)
    repairs = [
        candidate
        for candidate in powerset_nonempty(relevant_actions)
        if is_minimal_repair(cutset, candidate)
    ]
    return sorted(repairs, key=lambda item: (len(item), tuple(sorted(item))))


@dataclass(frozen=True)
class RepairCandidate:
    candidate_id: str
    actions: tuple[str, ...]
    evidence_quality: float
    residual_risk: float
    cost: float
    constitution_ok: bool
    provenance_claimed_ready: bool
    recovery_claimed_ready: bool
    authority: int = 0


def candidate_state(candidate: RepairCandidate, failures: frozenset[str]) -> dict[str, object]:
    actions = frozenset(candidate.actions)
    remaining = apply_repairs(failures, actions)
    actual_provenance_ready = (
        "PROVENANCE_LOSS" not in remaining and candidate.provenance_claimed_ready
    )
    actual_recovery_ready = (
        "RECOVERY_LOSS" not in remaining and candidate.recovery_claimed_ready
    )
    fatal_resolved = not is_fatal(remaining)
    eligible = (
        candidate.authority == 0
        and candidate.constitution_ok
        and fatal_resolved
        and actual_provenance_ready
        and actual_recovery_ready
    )
    score = candidate.residual_risk + candidate.cost - 0.25 * candidate.evidence_quality
    return {
        "candidate_id": candidate.candidate_id,
        "actions": list(candidate.actions),
        "remaining_failures": sorted(remaining),
        "fatal_resolved": fatal_resolved,
        "provenance_ready": actual_provenance_ready,
        "recovery_ready": actual_recovery_ready,
        "constitution_ok": candidate.constitution_ok,
        "authority": candidate.authority,
        "eligible": eligible,
        "score": round(score, 12),
    }


def run_repair_tournament(failures: frozenset[str], candidates: Sequence[RepairCandidate]) -> dict[str, object]:
    states = [candidate_state(candidate, failures) for candidate in candidates]
    eligible = [state for state in states if state["eligible"]]
    if not eligible:
        return {"status": "NO_ELIGIBLE_REPAIR", "winner": None, "states": states}
    best_score = min(float(state["score"]) for state in eligible)
    winners = [state for state in eligible if float(state["score"]) == best_score]
    if len(winners) != 1:
        return {
            "status": "TIE_OR_INCONCLUSIVE",
            "winner": None,
            "tied_candidates": sorted(str(state["candidate_id"]) for state in winners),
            "states": states,
        }
    return {
        "status": "REPAIR_WINNER_SELECTED",
        "winner": winners[0]["candidate_id"],
        "winner_score": winners[0]["score"],
        "states": states,
    }


def frozen_repair_tournament_fixture() -> tuple[frozenset[str], list[RepairCandidate]]:
    failures = frozenset({"PROVENANCE_LOSS", "RECOVERY_LOSS"})
    candidates = [
        RepairCandidate(
            candidate_id="REPAIR-A",
            actions=("RESTORE_VERIFIABLE_PROVENANCE", "RESTORE_TESTED_RECOVERY_PATH"),
            evidence_quality=0.80,
            residual_risk=0.20,
            cost=0.30,
            constitution_ok=True,
            provenance_claimed_ready=True,
            recovery_claimed_ready=True,
        ),
        RepairCandidate(
            candidate_id="REPAIR-B",
            actions=("RESTORE_VERIFIABLE_PROVENANCE", "RESTORE_TESTED_RECOVERY_PATH"),
            evidence_quality=0.90,
            residual_risk=0.15,
            cost=0.22,
            constitution_ok=True,
            provenance_claimed_ready=True,
            recovery_claimed_ready=True,
        ),
        RepairCandidate(
            candidate_id="CHEAP-INCOMPLETE",
            actions=("RESTORE_VERIFIABLE_PROVENANCE",),
            evidence_quality=0.99,
            residual_risk=0.01,
            cost=0.01,
            constitution_ok=True,
            provenance_claimed_ready=True,
            recovery_claimed_ready=False,
        ),
        RepairCandidate(
            candidate_id="CONSTITUTION-LAUNDERED",
            actions=("RESTORE_VERIFIABLE_PROVENANCE", "RESTORE_TESTED_RECOVERY_PATH"),
            evidence_quality=1.00,
            residual_risk=0.00,
            cost=0.00,
            constitution_ok=False,
            provenance_claimed_ready=True,
            recovery_claimed_ready=True,
        ),
    ]
    return failures, candidates


def run_stack() -> dict[str, object]:
    cutsets = enumerate_minimal_fatal_cutsets()
    repairs = {
        "+".join(sorted(cutset)): [sorted(repair) for repair in minimal_counterfactual_repairs(cutset)]
        for cutset in cutsets
    }

    failures, candidates = frozen_repair_tournament_fixture()
    tournament = run_repair_tournament(failures, candidates)

    no_eligible = run_repair_tournament(
        failures,
        [
            RepairCandidate(
                candidate_id="INVALID-1",
                actions=("RESTORE_VERIFIABLE_PROVENANCE",),
                evidence_quality=1.0,
                residual_risk=0.0,
                cost=0.0,
                constitution_ok=True,
                provenance_claimed_ready=True,
                recovery_claimed_ready=False,
            ),
            RepairCandidate(
                candidate_id="INVALID-2",
                actions=("RESTORE_VERIFIABLE_PROVENANCE", "RESTORE_TESTED_RECOVERY_PATH"),
                evidence_quality=1.0,
                residual_risk=0.0,
                cost=0.0,
                constitution_ok=False,
                provenance_claimed_ready=True,
                recovery_claimed_ready=True,
            ),
        ],
    )

    result = {
        "status": "DEATHEYE_OMEGA_CONCENTRATED_EVOLUTION_STACK_READY",
        "layer_39": "DEATHEYE_OMEGA_HYPERGRAPH_CUTSET_READY",
        "layer_40": "COUNTERFACTUAL_REPAIR_MINIMALITY_READY",
        "layer_41": "REPAIR_TOURNAMENT_READY",
        "minimal_fatal_cutsets": [sorted(cutset) for cutset in cutsets],
        "minimal_counterfactual_repairs": repairs,
        "repair_tournament": tournament,
        "no_eligible_fixture": no_eligible["status"],
        "external_gates_closed": [],
        "canonical_promotion": False,
        "real_world_attack_authority": 0,
        "real_world_actuation_authority": 0,
        "external_actuation": "DENY_BY_DEFAULT",
    }
    assert result["status"] not in FORBIDDEN_END_STATES
    return result


def _sanity() -> None:
    expected_cutsets = {
        frozenset({"CONSTITUTION_SCORE_OVERRIDE_BYPASS"}),
        frozenset({"PROVENANCE_LOSS", "RECOVERY_LOSS"}),
        frozenset({"DISSENT_DELETION", "DYNASTIC_PRIVILEGE"}),
    }
    actual = set(enumerate_minimal_fatal_cutsets())
    assert actual == expected_cutsets

    for cutset in actual:
        repairs = minimal_counterfactual_repairs(cutset)
        assert repairs
        for repair in repairs:
            assert is_minimal_repair(cutset, repair)
            assert repair_sufficient_for_correctability(cutset, repair)
            # Every one-action removal from a singleton minimal repair must fail.
            if len(repair) == 1:
                assert not repair_sufficient_for_correctability(cutset, frozenset())

    failures, candidates = frozen_repair_tournament_fixture()
    tournament = run_repair_tournament(failures, candidates)
    assert tournament["status"] == "REPAIR_WINNER_SELECTED"
    assert tournament["winner"] == "REPAIR-B"

    states = {state["candidate_id"]: state for state in tournament["states"]}
    assert states["CHEAP-INCOMPLETE"]["eligible"] is False
    assert states["CONSTITUTION-LAUNDERED"]["eligible"] is False
    assert states["CONSTITUTION-LAUNDERED"]["score"] < states["REPAIR-B"]["score"]

    result = run_stack()
    assert result["no_eligible_fixture"] == "NO_ELIGIBLE_REPAIR"
    assert result["external_gates_closed"] == []
    assert result["canonical_promotion"] is False
    assert result["real_world_attack_authority"] == 0
    assert result["real_world_actuation_authority"] == 0

    print("DEATHEYE_OMEGA_HYPERGRAPH_CUTSET_READY")
    print("COUNTERFACTUAL_REPAIR_MINIMALITY_READY")
    print("REPAIR_TOURNAMENT_READY")
    print("DEATHEYE_OMEGA_CONCENTRATED_EVOLUTION_STACK_READY")
    print("GOOD_SCORE_CANNOT_OVERRIDE_HARD_REPAIR_GATES")
    print("NO_ELIGIBLE_REPAIR_IS_VALID")
    print("EXTERNAL_GATES_REMAIN_OPEN")
    print("REAL_WORLD_ATTACK_AUTHORITY_ZERO")


if __name__ == "__main__":
    _sanity()
