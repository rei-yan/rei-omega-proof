#!/usr/bin/env python3
"""DeathEye Ω robustness and self-falsification stack.

Synthetic epistemic/architectural research only. No real-world targeting or actuation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

from deatheye_omega_hypergraph_evolution_stack import (
    FATAL_HYPEREDGES,
    apply_repairs,
    is_fatal,
)

FORBIDDEN_END_STATES = {
    "G3_PASS", "G4_PASS", "G5_PASS", "G6_PASS", "G7_PASS", "G8_PASS",
    "G9_PASS", "G10_PASS", "WORLD_BEST", "WORLD_UNIQUE", "CANONICAL", "FINAL_TRUTH",
}

BASE_FAILURES = frozenset({"PROVENANCE_LOSS", "RECOVERY_LOSS"})


@dataclass(frozen=True)
class Regime:
    regime_id: str
    injected_failures: frozenset[str]
    required_actions: frozenset[str]


FROZEN_REGIMES = (
    Regime(
        regime_id="BASELINE",
        injected_failures=frozenset(),
        required_actions=frozenset({
            "RESTORE_VERIFIABLE_PROVENANCE",
            "RESTORE_TESTED_RECOVERY_PATH",
        }),
    ),
    Regime(
        regime_id="DISSENT_SHIFT",
        injected_failures=frozenset({"DISSENT_DELETION"}),
        required_actions=frozenset({
            "RESTORE_VERIFIABLE_PROVENANCE",
            "RESTORE_TESTED_RECOVERY_PATH",
            "RESTORE_DISSENT_PRESERVATION",
        }),
    ),
    Regime(
        regime_id="LINEAGE_SHIFT",
        injected_failures=frozenset({"DYNASTIC_PRIVILEGE"}),
        required_actions=frozenset({
            "RESTORE_VERIFIABLE_PROVENANCE",
            "RESTORE_TESTED_RECOVERY_PATH",
            "REMOVE_LINEAGE_PRIVILEGE",
        }),
    ),
)


def evaluate_repair_in_regime(actions: frozenset[str], regime: Regime) -> dict[str, object]:
    failures = BASE_FAILURES.union(regime.injected_failures)
    remaining = apply_repairs(failures, actions)
    obligations_met = regime.required_actions.issubset(actions)
    fatal_resolved = not is_fatal(remaining)
    return {
        "regime_id": regime.regime_id,
        "remaining_failures": sorted(remaining),
        "obligations_met": obligations_met,
        "fatal_resolved": fatal_resolved,
        "passes": obligations_met and fatal_resolved,
    }


def cross_regime_repair_report(actions: frozenset[str]) -> dict[str, object]:
    states = [evaluate_repair_in_regime(actions, regime) for regime in FROZEN_REGIMES]
    return {
        "actions": sorted(actions),
        "states": states,
        "cross_regime_robust": all(bool(state["passes"]) for state in states),
    }


INTERFERENCE_GRAPH = {
    frozenset({"RESTORE_DISSENT_PRESERVATION", "RECALIBRATE_LOCAL_MODEL"}):
        "EVALUATOR_CALIBRATION_COLLISION",
}


def repair_interference_hazards(actions: frozenset[str]) -> list[str]:
    hazards = [
        hazard
        for trigger, hazard in INTERFERENCE_GRAPH.items()
        if trigger.issubset(actions)
    ]
    return sorted(hazards)


def repair_composition_safe(actions: frozenset[str]) -> bool:
    return not repair_interference_hazards(actions)


@dataclass(frozen=True)
class DetectorCase:
    case_id: str
    failures: frozenset[str]
    expected_fatal: bool


FROZEN_DETECTOR_WINDOW = (
    DetectorCase(
        case_id="SINGLETON_CONSTITUTION_DEATH",
        failures=frozenset({"CONSTITUTION_SCORE_OVERRIDE_BYPASS"}),
        expected_fatal=True,
    ),
    DetectorCase(
        case_id="COUPLED_PROVENANCE_RECOVERY_DEATH",
        failures=frozenset({"PROVENANCE_LOSS", "RECOVERY_LOSS"}),
        expected_fatal=True,
    ),
    DetectorCase(
        case_id="COUPLED_DISSENT_DYNASTY_DEATH",
        failures=frozenset({"DISSENT_DELETION", "DYNASTIC_PRIVILEGE"}),
        expected_fatal=True,
    ),
    DetectorCase(
        case_id="LOCAL_MISFIT_CONTROL",
        failures=frozenset({"LOCAL_MODEL_MISFIT"}),
        expected_fatal=False,
    ),
    DetectorCase(
        case_id="PROVENANCE_ONLY_CONTROL",
        failures=frozenset({"PROVENANCE_LOSS"}),
        expected_fatal=False,
    ),
    DetectorCase(
        case_id="DISSENT_ONLY_CONTROL",
        failures=frozenset({"DISSENT_DELETION"}),
        expected_fatal=False,
    ),
)


def detector_v1_singletons_only(failures: frozenset[str]) -> bool:
    return any(len(edge) == 1 and edge.issubset(failures) for edge in FATAL_HYPEREDGES)


def detector_v2_hypergraph(failures: frozenset[str]) -> bool:
    return is_fatal(failures)


def challenge_detector(
    detector_id: str,
    detector: Callable[[frozenset[str]], bool],
    cases: Sequence[DetectorCase] = FROZEN_DETECTOR_WINDOW,
) -> dict[str, object]:
    outcomes: list[dict[str, object]] = []
    false_negatives = 0
    false_positives = 0
    for case in cases:
        observed = bool(detector(case.failures))
        if case.expected_fatal and not observed:
            false_negatives += 1
        if not case.expected_fatal and observed:
            false_positives += 1
        outcomes.append({
            "case_id": case.case_id,
            "expected_fatal": case.expected_fatal,
            "observed_fatal": observed,
            "match": observed == case.expected_fatal,
        })

    if false_negatives > 0:
        status = "RETIRE_DETECTOR"
    elif false_positives > 0:
        status = "REJECT_DETECTOR"
    else:
        status = "SURVIVES_FROZEN_SYNTHETIC_WINDOW"

    return {
        "detector_id": detector_id,
        "status": status,
        "false_negatives": false_negatives,
        "false_positives": false_positives,
        "outcomes": outcomes,
        "detector_authority": 0,
        "external_validation": False,
        "final_detector": False,
        "requires_fresh_hidden_window": True,
    }


def run_stack() -> dict[str, object]:
    baseline_only_repair = frozenset({
        "RESTORE_VERIFIABLE_PROVENANCE",
        "RESTORE_TESTED_RECOVERY_PATH",
    })
    robust_repair = frozenset({
        "RESTORE_VERIFIABLE_PROVENANCE",
        "RESTORE_TESTED_RECOVERY_PATH",
        "RESTORE_DISSENT_PRESERVATION",
        "REMOVE_LINEAGE_PRIVILEGE",
    })

    baseline_report = cross_regime_repair_report(baseline_only_repair)
    robust_report = cross_regime_repair_report(robust_repair)

    action_a = frozenset({"RESTORE_DISSENT_PRESERVATION"})
    action_b = frozenset({"RECALIBRATE_LOCAL_MODEL"})
    combined = action_a.union(action_b)
    interference = {
        "action_a_safe": repair_composition_safe(action_a),
        "action_b_safe": repair_composition_safe(action_b),
        "combined_safe": repair_composition_safe(combined),
        "combined_hazards": repair_interference_hazards(combined),
    }

    v1 = challenge_detector("DEATHEYE-V1-SINGLETONS", detector_v1_singletons_only)
    v2 = challenge_detector("DEATHEYE-V2-HYPERGRAPH", detector_v2_hypergraph)

    result = {
        "status": "DEATHEYE_OMEGA_ROBUSTNESS_SELF_FALSIFICATION_STACK_READY",
        "layer_42": "REPAIR_CROSS_REGIME_ROBUSTNESS_READY",
        "layer_43": "REPAIR_INTERFERENCE_GRAPH_READY",
        "layer_44": "DEATHEYE_SELF_FALSIFICATION_READY",
        "baseline_only_repair": baseline_report,
        "robust_repair": robust_report,
        "repair_interference": interference,
        "detector_v1": v1,
        "detector_v2": v2,
        "external_gates_closed": [],
        "canonical_promotion": False,
        "real_world_attack_authority": 0,
        "real_world_actuation_authority": 0,
        "external_actuation": "DENY_BY_DEFAULT",
    }
    assert result["status"] not in FORBIDDEN_END_STATES
    return result


def _sanity() -> None:
    result = run_stack()

    assert result["baseline_only_repair"]["cross_regime_robust"] is False
    assert result["robust_repair"]["cross_regime_robust"] is True

    interference = result["repair_interference"]
    assert interference["action_a_safe"] is True
    assert interference["action_b_safe"] is True
    assert interference["combined_safe"] is False
    assert interference["combined_hazards"] == ["EVALUATOR_CALIBRATION_COLLISION"]

    v1 = result["detector_v1"]
    v2 = result["detector_v2"]
    assert v1["status"] == "RETIRE_DETECTOR"
    assert v1["false_negatives"] == 2
    assert v1["false_positives"] == 0
    assert v2["status"] == "SURVIVES_FROZEN_SYNTHETIC_WINDOW"
    assert v2["false_negatives"] == 0
    assert v2["false_positives"] == 0
    assert v2["final_detector"] is False
    assert v2["external_validation"] is False
    assert v2["requires_fresh_hidden_window"] is True

    assert result["external_gates_closed"] == []
    assert result["canonical_promotion"] is False
    assert result["real_world_attack_authority"] == 0
    assert result["real_world_actuation_authority"] == 0

    print("REPAIR_CROSS_REGIME_ROBUSTNESS_READY")
    print("ONE_WINDOW_REPAIR_SUCCESS_NOT_PERSISTENT_AUTHORITY")
    print("REPAIR_INTERFERENCE_GRAPH_READY")
    print("INDIVIDUAL_REPAIR_VALIDITY_NOT_COMPOSITION_SAFETY")
    print("DEATHEYE_SELF_FALSIFICATION_READY")
    print("FATAL_FALSE_NEGATIVE_RETIRES_DETECTOR")
    print("DETECTOR_PASS_NOT_FINAL_DETECTOR")
    print("DEATHEYE_OMEGA_ROBUSTNESS_SELF_FALSIFICATION_STACK_READY")
    print("EXTERNAL_GATES_REMAIN_OPEN")
    print("REAL_WORLD_ATTACK_AUTHORITY_ZERO")


if __name__ == "__main__":
    _sanity()
