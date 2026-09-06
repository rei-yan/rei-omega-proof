#!/usr/bin/env python3
"""Wuxiang total convergence kernel.

Synthetic epistemic/architectural research only. No real-world targeting or actuation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

from deatheye_omega_hypergraph_evolution_stack import (
    FATAL_HYPEREDGES,
    frozen_repair_tournament_fixture,
    is_fatal,
    run_repair_tournament,
)
from deatheye_omega_robustness_self_falsification_stack import (
    DetectorCase,
    FROZEN_DETECTOR_WINDOW,
    challenge_detector,
    cross_regime_repair_report,
    detector_v1_singletons_only,
    detector_v2_hypergraph,
    repair_composition_safe,
)

FORBIDDEN_END_STATES = {
    "G3_PASS", "G4_PASS", "G5_PASS", "G6_PASS", "G7_PASS", "G8_PASS",
    "G9_PASS", "G10_PASS", "WORLD_BEST", "WORLD_UNIQUE", "CANONICAL", "FINAL_TRUTH",
}


def detector_v3_brittle_exact_edge(failures: frozenset[str]) -> bool:
    """Deliberately brittle: recognizes only exact fatal edges, not fatal supersets."""
    return failures in FATAL_HYPEREDGES


def detector_v4_equivalent_hypergraph(failures: frozenset[str]) -> bool:
    """Independent-looking internal implementation of the same frozen rule."""
    return any(all(node in failures for node in edge) for edge in FATAL_HYPEREDGES)


@dataclass(frozen=True)
class DetectorCandidate:
    detector_id: str
    detector: Callable[[frozenset[str]], bool]
    authority: int = 0


def detector_ecology_tournament(
    candidates: Sequence[DetectorCandidate],
    cases: Sequence[DetectorCase] = FROZEN_DETECTOR_WINDOW,
) -> dict[str, object]:
    reports = [challenge_detector(c.detector_id, c.detector, cases) for c in candidates]
    eligible = [
        report for report in reports
        if report["status"] == "SURVIVES_FROZEN_SYNTHETIC_WINDOW"
        and int(report["detector_authority"]) == 0
    ]
    if not eligible:
        status = "NO_ELIGIBLE_DETECTOR"
        winner = None
    elif len(eligible) == 1:
        status = "PROVISIONAL_SINGLE_SURVIVOR"
        winner = eligible[0]["detector_id"]
    else:
        status = "NO_UNIQUE_DETECTOR_CHAMPION"
        winner = None
    return {
        "status": status,
        "winner": winner,
        "eligible_detectors": sorted(str(r["detector_id"]) for r in eligible),
        "reports": reports,
        "permanent_champion": False,
        "external_validation": False,
    }


@dataclass(frozen=True)
class EvaluatorVerdict:
    evaluator_id: str
    verdict: str
    material_counterexample: bool = False
    provenance_complete: bool = True


def adjudicate_material_dissent(verdicts: Sequence[EvaluatorVerdict]) -> dict[str, object]:
    material = [v for v in verdicts if v.material_counterexample and v.provenance_complete]
    passes = sum(1 for v in verdicts if v.verdict == "PASS")
    fails = sum(1 for v in verdicts if v.verdict == "FAIL")
    if material:
        status = "MIXED_EVIDENCE_ABSTAIN"
    elif fails > 0:
        status = "MIXED_EVIDENCE"
    elif passes == len(verdicts) and verdicts:
        status = "PROVISIONAL_INTERNAL_SUPPORT"
    else:
        status = "ABSTAIN"
    return {
        "status": status,
        "pass_count": passes,
        "fail_count": fails,
        "material_counterexamples": [v.evaluator_id for v in material],
        "dissent_preserved": bool(material or fails),
        "external_validation": False,
    }


def generate_blind_spot_cases() -> tuple[DetectorCase, ...]:
    cases: list[DetectorCase] = []
    for i, edge in enumerate(FATAL_HYPEREDGES, start=1):
        cases.append(DetectorCase(
            case_id=f"METAMORPHIC_FATAL_SUPERSET_{i}",
            failures=frozenset(set(edge) | {"LOCAL_MODEL_MISFIT"}),
            expected_fatal=True,
        ))
    cases.extend([
        DetectorCase(
            case_id="METAMORPHIC_PROVENANCE_ONLY_CONTROL",
            failures=frozenset({"PROVENANCE_LOSS", "LOCAL_MODEL_MISFIT"}),
            expected_fatal=False,
        ),
        DetectorCase(
            case_id="METAMORPHIC_DISSENT_ONLY_CONTROL",
            failures=frozenset({"DISSENT_DELETION", "LOCAL_MODEL_MISFIT"}),
            expected_fatal=False,
        ),
    ])
    return tuple(cases)


def blind_spot_challenge(detector_id: str, detector: Callable[[frozenset[str]], bool]) -> dict[str, object]:
    report = challenge_detector(detector_id, detector, generate_blind_spot_cases())
    report["derived_challenge_only"] = True
    report["independent_hidden_challenge"] = False
    return report


def run_total_convergence() -> dict[str, object]:
    detectors = [
        DetectorCandidate("DEATHEYE-V1-SINGLETONS", detector_v1_singletons_only),
        DetectorCandidate("DEATHEYE-V2-HYPERGRAPH", detector_v2_hypergraph),
        DetectorCandidate("DEATHEYE-V3-BRITTLE-EXACT", detector_v3_brittle_exact_edge),
        DetectorCandidate("DEATHEYE-V4-EQUIVALENT-HYPERGRAPH", detector_v4_equivalent_hypergraph),
    ]
    ecology = detector_ecology_tournament(detectors)

    dissent = adjudicate_material_dissent([
        EvaluatorVerdict("EVAL-A", "PASS"),
        EvaluatorVerdict("EVAL-B", "PASS"),
        EvaluatorVerdict("EVAL-C", "PASS"),
        EvaluatorVerdict("EVAL-D", "FAIL", material_counterexample=True),
    ])

    blind_v2 = blind_spot_challenge("DEATHEYE-V2-HYPERGRAPH", detector_v2_hypergraph)
    blind_v3 = blind_spot_challenge("DEATHEYE-V3-BRITTLE-EXACT", detector_v3_brittle_exact_edge)
    blind_v4 = blind_spot_challenge("DEATHEYE-V4-EQUIVALENT-HYPERGRAPH", detector_v4_equivalent_hypergraph)

    failures, repair_candidates = frozen_repair_tournament_fixture()
    repair_tournament = run_repair_tournament(failures, repair_candidates)
    robust_actions = frozenset({
        "RESTORE_VERIFIABLE_PROVENANCE",
        "RESTORE_TESTED_RECOVERY_PATH",
        "RESTORE_DISSENT_PRESERVATION",
        "REMOVE_LINEAGE_PRIVILEGE",
    })
    robustness = cross_regime_repair_report(robust_actions)
    composition_safe = repair_composition_safe(robust_actions)

    internal_hard_gates = (
        repair_tournament["status"] == "REPAIR_WINNER_SELECTED"
        and bool(robustness["cross_regime_robust"])
        and composition_safe
        and blind_v2["status"] == "SURVIVES_FROZEN_SYNTHETIC_WINDOW"
        and blind_v4["status"] == "SURVIVES_FROZEN_SYNTHETIC_WINDOW"
    )

    # Material counterexample intentionally blocks a stronger internal verdict.
    if dissent["status"] == "MIXED_EVIDENCE_ABSTAIN":
        decision = "ABSTAIN_PENDING_EXTERNAL_REALITY"
    elif internal_hard_gates:
        decision = "READY_FOR_EXTERNAL_REALITY_ADJUDICATION_HANDOFF"
    else:
        decision = "ABSTAIN_INTERNAL_GATES_INCOMPLETE"

    result = {
        "status": "WUXIANG_TOTAL_CONVERGENCE_KERNEL_READY",
        "layer_45": "DETECTOR_ECOLOGY_TOURNAMENT_READY",
        "layer_46": "MATERIAL_DISSENT_PRESERVATION_READY",
        "layer_47": "BLIND_SPOT_CHALLENGE_GENESIS_READY",
        "layer_48": "WUXIANG_TOTAL_CONVERGENCE_KERNEL_READY",
        "detector_ecology": ecology,
        "material_dissent": dissent,
        "blind_spot_v2": blind_v2,
        "blind_spot_v3": blind_v3,
        "blind_spot_v4": blind_v4,
        "repair_tournament": repair_tournament["status"],
        "repair_cross_regime_robust": robustness["cross_regime_robust"],
        "repair_composition_safe": composition_safe,
        "internal_hard_gates": internal_hard_gates,
        "decision": decision,
        "external_gates_closed": [],
        "external_reality_verdict": "OPEN",
        "canonical_promotion": False,
        "permanent_champion": False,
        "real_world_attack_authority": 0,
        "real_world_actuation_authority": 0,
        "external_actuation": "DENY_BY_DEFAULT",
    }
    assert result["status"] not in FORBIDDEN_END_STATES
    return result


def _sanity() -> None:
    result = run_total_convergence()

    ecology = result["detector_ecology"]
    assert ecology["status"] == "NO_UNIQUE_DETECTOR_CHAMPION"
    assert "DEATHEYE-V2-HYPERGRAPH" in ecology["eligible_detectors"]
    assert "DEATHEYE-V3-BRITTLE-EXACT" in ecology["eligible_detectors"]
    assert "DEATHEYE-V4-EQUIVALENT-HYPERGRAPH" in ecology["eligible_detectors"]
    assert ecology["permanent_champion"] is False

    dissent = result["material_dissent"]
    assert dissent["pass_count"] == 3
    assert dissent["fail_count"] == 1
    assert dissent["status"] == "MIXED_EVIDENCE_ABSTAIN"
    assert dissent["dissent_preserved"] is True

    assert result["blind_spot_v2"]["status"] == "SURVIVES_FROZEN_SYNTHETIC_WINDOW"
    assert result["blind_spot_v3"]["status"] == "RETIRE_DETECTOR"
    assert result["blind_spot_v3"]["false_negatives"] >= 1
    assert result["blind_spot_v4"]["status"] == "SURVIVES_FROZEN_SYNTHETIC_WINDOW"
    assert result["blind_spot_v3"]["independent_hidden_challenge"] is False

    assert result["repair_tournament"] == "REPAIR_WINNER_SELECTED"
    assert result["repair_cross_regime_robust"] is True
    assert result["repair_composition_safe"] is True
    assert result["internal_hard_gates"] is True
    assert result["decision"] == "ABSTAIN_PENDING_EXTERNAL_REALITY"
    assert result["external_reality_verdict"] == "OPEN"
    assert result["external_gates_closed"] == []
    assert result["canonical_promotion"] is False
    assert result["permanent_champion"] is False
    assert result["real_world_attack_authority"] == 0
    assert result["real_world_actuation_authority"] == 0

    print("DETECTOR_ECOLOGY_TOURNAMENT_READY")
    print("NO_UNIQUE_DETECTOR_CHAMPION_IS_VALID")
    print("MATERIAL_DISSENT_PRESERVATION_READY")
    print("MAJORITY_PASS_CANNOT_DELETE_MATERIAL_COUNTEREXAMPLE")
    print("BLIND_SPOT_CHALLENGE_GENESIS_READY")
    print("PASS_ORIGINAL_WINDOW_NOT_BLIND_SPOT_FREE")
    print("WUXIANG_TOTAL_CONVERGENCE_KERNEL_READY")
    print("CAPABILITY_CONVERGENCE_NOT_AUTHORITY_CONVERGENCE")
    print("ABSTAIN_PENDING_EXTERNAL_REALITY")
    print("EXTERNAL_GATES_REMAIN_OPEN")
    print("REAL_WORLD_ATTACK_AUTHORITY_ZERO")


if __name__ == "__main__":
    _sanity()
