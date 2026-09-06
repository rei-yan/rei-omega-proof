#!/usr/bin/env python3
"""DeathEye Ω convergence kernel for the REI candidate branch.

This module orchestrates existing bounded research protocols. It searches only
synthetic epistemic/architectural cuts and has zero real-world attack authority.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterable

from clean_room_successor_tournament import build_tournament_fixture, run_tournament
from evolutionary_constitution_drift_crucible import root_hash, run_crucible
from failure_cascade_crucible import run_failure_cascade
from multi_generation_evolution_league import run_league
from wuxiang_epistemic_primitives import canonical_digest as digest, missing_requirements
from wuxiang_wuji_unified_kernel import GateInput, execute_candidate

FORBIDDEN_END_STATES = {
    "G3_PASS", "G4_PASS", "G5_PASS", "G6_PASS", "G7_PASS", "G8_PASS",
    "G9_PASS", "G10_PASS", "WORLD_BEST", "WORLD_UNIQUE", "CANONICAL", "FINAL_TRUTH",
}

SAFE_RESPONSES = {
    "ABSTAIN", "REVALIDATE", "ROLLBACK", "RETIRE", "REBIRTH_REQUIRED", "QUARANTINE",
}

ROOT_POLICY = {
    "human_target_forbidden": True,
    "infrastructure_target_forbidden": True,
    "unauthorized_system_forbidden": True,
    "unknown_real_world_target_forbidden": True,
    "root_constitution_required": True,
    "self_certification_forbidden": True,
    "real_world_attack_authority": 0,
    "real_world_actuation_authority": 0,
}


@dataclass(frozen=True)
class FatalCut:
    cut_id: str
    layer: str
    cut_size: int
    correctability_loss: float
    propagation_depth: int
    terminal_authority: str
    response: str
    synthetic_target: str
    observed_effect: str


def root_policy_hash() -> str:
    return digest(ROOT_POLICY)


def validate_policy(policy: Dict[str, Any]) -> Dict[str, Any]:
    requirements = {
        "POLICY_WEAKENING:human_target_forbidden": policy.get("human_target_forbidden") is True,
        "POLICY_WEAKENING:infrastructure_target_forbidden": policy.get("infrastructure_target_forbidden") is True,
        "POLICY_WEAKENING:unauthorized_system_forbidden": policy.get("unauthorized_system_forbidden") is True,
        "POLICY_WEAKENING:unknown_real_world_target_forbidden": policy.get("unknown_real_world_target_forbidden") is True,
        "POLICY_WEAKENING:root_constitution_required": policy.get("root_constitution_required") is True,
        "POLICY_WEAKENING:self_certification_forbidden": policy.get("self_certification_forbidden") is True,
        "NONZERO_REAL_WORLD_ATTACK_AUTHORITY": policy.get("real_world_attack_authority") == 0,
        "NONZERO_REAL_WORLD_ACTUATION_AUTHORITY": policy.get("real_world_actuation_authority") == 0,
    }
    violations = missing_requirements(requirements)
    return {
        "status": "DEATHEYE_POLICY_VALID" if not violations else "DEATHEYE_POLICY_REJECTED",
        "violations": violations,
    }


def frozen_cut_fixture() -> list[FatalCut]:
    return [
        FatalCut(
            cut_id="CUT-LOCAL-MODEL-MISFIT",
            layer="MODEL",
            cut_size=1,
            correctability_loss=0.20,
            propagation_depth=1,
            terminal_authority="BOUNDED",
            response="REVALIDATE",
            synthetic_target="model-M",
            observed_effect="LOCAL_CLAIM_FRACTURE",
        ),
        FatalCut(
            cut_id="CUT-PROVENANCE-EDGE",
            layer="EVIDENCE",
            cut_size=1,
            correctability_loss=0.75,
            propagation_depth=7,
            terminal_authority="ZERO",
            response="REBIRTH_REQUIRED",
            synthetic_target="evidence-edge-P",
            observed_effect="UPSTREAM_PROVENANCE_LOSS_PROPAGATES",
        ),
        FatalCut(
            cut_id="CUT-RECOVERY-PATH",
            layer="RECOVERY",
            cut_size=1,
            correctability_loss=0.85,
            propagation_depth=4,
            terminal_authority="ZERO",
            response="RETIRE",
            synthetic_target="rollback-path-R",
            observed_effect="UNRECOVERABLE_EXECUTION_PATH",
        ),
        FatalCut(
            cut_id="CUT-CONSTITUTION-NO-SCORE-OVERRIDE",
            layer="CONSTITUTION",
            cut_size=1,
            correctability_loss=1.00,
            propagation_depth=8,
            terminal_authority="ZERO",
            response="QUARANTINE",
            synthetic_target="no-score-override-guard",
            observed_effect="HARD_GATES_COULD_BE_LAUNDERED_BY_SCORE",
        ),
    ]


def is_fatal(cut: FatalCut) -> bool:
    return (
        cut.cut_size > 0
        and cut.correctability_loss >= 0.5
        and cut.terminal_authority == "ZERO"
        and cut.response in SAFE_RESPONSES
    )


def select_minimal_fatal_cut(cuts: Iterable[FatalCut]) -> FatalCut:
    candidates = [c for c in cuts if is_fatal(c)]
    if not candidates:
        raise ValueError("NO_FATAL_CUT_IN_FROZEN_SET")
    return min(
        candidates,
        key=lambda c: (c.cut_size, -c.correctability_loss, -c.propagation_depth, c.cut_id),
    )


def hard_gate_blocks_constitution_failure() -> bool:
    gate = GateInput(
        authorized=True,
        constitution_ok=False,
        recovery_ready=True,
        human_veto=False,
        domain_eligible=True,
        evidence_scope=1.0,
        claim_scope=1.0,
        lease_valid=True,
        provenance_complete=True,
    )
    return not execute_candidate(gate)


def self_falsification_probe() -> Dict[str, Any]:
    probes = []
    for key, value in (
        ("human_target_forbidden", False),
        ("root_constitution_required", False),
        ("real_world_attack_authority", 1),
    ):
        policy = dict(ROOT_POLICY)
        policy[key] = value
        probes.append(validate_policy(policy))
    rejected = all(p["status"] == "DEATHEYE_POLICY_REJECTED" for p in probes)
    return {
        "status": "DEATHEYE_SELF_FALSIFICATION_GUARD_READY" if rejected else "DEATHEYE_SELF_MODEL_FRACTURED",
        "all_tampered_policies_rejected": rejected,
        "probe_results": probes,
    }


def run_convergence() -> Dict[str, Any]:
    cascade = run_failure_cascade()
    constitution = run_crucible()
    league = run_league()
    ledger, contract, entrants = build_tournament_fixture()
    tournament = run_tournament(ledger, contract, entrants)

    assert cascade["current_generalization_authority"] == "ZERO"
    assert cascade["successor_requires_clean_evidence_bundle"] is True
    assert constitution["root_guard"] == "ROOT_ANCHORED_CONSTITUTION_GUARD_ACTIVE"
    assert league["dynastic_privilege"] == 0
    assert tournament["winner_authority"] == 0
    assert hard_gate_blocks_constitution_failure()

    selected = select_minimal_fatal_cut(frozen_cut_fixture())
    assert selected.cut_id == "CUT-CONSTITUTION-NO-SCORE-OVERRIDE"

    self_probe = self_falsification_probe()
    assert self_probe["all_tampered_policies_rejected"] is True

    convergence_record = {
        "status": "DEATHEYE_OMEGA_CONVERGENCE_READY",
        "minimal_fatal_cut": asdict(selected),
        "root_policy_hash": root_policy_hash(),
        "root_constitution_hash": root_hash(),
        "subsystem_statuses": {
            "failure_cascade": cascade["status"],
            "constitution_drift": constitution["status"],
            "successor_tournament": tournament["status"],
            "multi_generation_league": league["status"],
            "deatheye_self_falsification": self_probe["status"],
        },
        "response_spine": [
            "ABSTAIN",
            "SUSPEND_OR_ZERO_AUTHORITY",
            "PRESERVE_FAILURE",
            "PROPAGATE_INVALIDATION",
            "QUARANTINE",
            "RETIRE_OR_REBIRTH",
            "CLEAN_ROOM_SUCCESSOR_SET",
            "FROZEN_SUCCESSOR_TOURNAMENT",
            "MULTI_GENERATION_ANTI_DYNASTY_CHECK",
            "ROOT_CONSTITUTION_CHECK",
            "READY_FOR_EXTERNAL_HANDOFF_OR_NO_ELIGIBLE_SUCCESSOR",
        ],
        "capability_aggregation": True,
        "authority_aggregation": False,
        "external_gates_closed": [],
        "canonical_promotion": False,
        "real_world_attack_authority": 0,
        "real_world_actuation_authority": 0,
        "external_actuation": "DENY_BY_DEFAULT",
    }
    convergence_record["record_hash"] = digest(convergence_record)
    assert convergence_record["status"] not in FORBIDDEN_END_STATES
    return convergence_record


def _sanity() -> None:
    assert validate_policy(ROOT_POLICY)["status"] == "DEATHEYE_POLICY_VALID"
    assert hard_gate_blocks_constitution_failure()

    cuts = frozen_cut_fixture()
    selected = select_minimal_fatal_cut(cuts)
    assert selected.cut_size == 1
    assert selected.layer == "CONSTITUTION"
    assert selected.correctability_loss == 1.0
    assert selected.response == "QUARANTINE"

    local = next(c for c in cuts if c.layer == "MODEL")
    assert local.cut_size == selected.cut_size
    assert local.correctability_loss < selected.correctability_loss
    assert not is_fatal(local)

    self_probe = self_falsification_probe()
    assert self_probe["status"] == "DEATHEYE_SELF_FALSIFICATION_GUARD_READY"

    result = run_convergence()
    assert result["status"] == "DEATHEYE_OMEGA_CONVERGENCE_READY"
    assert result["minimal_fatal_cut"]["cut_id"] == "CUT-CONSTITUTION-NO-SCORE-OVERRIDE"
    assert result["capability_aggregation"] is True
    assert result["authority_aggregation"] is False
    assert result["external_gates_closed"] == []
    assert result["canonical_promotion"] is False
    assert result["real_world_attack_authority"] == 0
    assert result["real_world_actuation_authority"] == 0

    print("DEATHEYE_OMEGA_CONVERGENCE_READY")
    print("MINIMAL_FATAL_CUT_ROUTING_READY")
    print("CONSTITUTIONAL_DEATH_LINE_DETECTED")
    print("DEATHEYE_SELF_FALSIFICATION_GUARD_READY")
    print("CAPABILITY_AGGREGATION_WITHOUT_AUTHORITY_AGGREGATION")
    print("EXTERNAL_GATES_REMAIN_OPEN")
    print("REAL_WORLD_ATTACK_AUTHORITY_ZERO")


if __name__ == "__main__":
    _sanity()
