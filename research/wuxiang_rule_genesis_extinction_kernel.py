#!/usr/bin/env python3
"""Finite synthetic rule-genesis / rule-extinction kernel.

This program tests candidate *research evolution rules*. It has zero real-world
actuation, deployment, attack, or authority-expansion capability.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Iterable

REQUIRED_DIMS = (
    "falsification_gain",
    "evidence_integrity",
    "recovery_gain",
    "scope_integrity",
    "semantic_integrity",
)

FORBIDDEN_AUTHORITY = {
    "external_validation",
    "canonical_promotion",
    "deployment",
    "experiment",
    "real_world_attack",
    "real_world_actuation",
}


@dataclass(frozen=True)
class MetaRule:
    rule_id: str
    objectives: dict[str, int]
    operators: tuple[str, ...]
    preserves_failure_memory: bool
    preserves_reality_veto: bool
    preserves_root_constitution: bool
    authority_delta: int
    falsifiable: bool
    complexity_cost: int


@dataclass(frozen=True)
class Challenge:
    challenge_id: str
    proxy_gain: int
    hard_regression: bool
    semantic_laundering: bool
    failure_deletion_pressure: bool
    authority_temptation: bool


def hard_gate(rule: MetaRule) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    if not rule.falsifiable:
        reasons.append("NON_FALSIFIABLE_META_RULE")
    if not rule.preserves_failure_memory:
        reasons.append("FAILURE_MEMORY_NOT_PRESERVED")
    if not rule.preserves_reality_veto:
        reasons.append("REALITY_VETO_WEAKENED")
    if not rule.preserves_root_constitution:
        reasons.append("ROOT_CONSTITUTION_WEAKENED")
    if rule.authority_delta > 0:
        reasons.append("AUTHORITY_EXPANSION")
    missing = [d for d in REQUIRED_DIMS if d not in rule.objectives]
    if missing:
        reasons.append("MISSING_REQUIRED_OBJECTIVE_DIMENSIONS")
    return (not reasons, reasons)


def composition_gate(operators: Iterable[str]) -> tuple[str, list[str]]:
    ops = tuple(operators)
    reasons: list[str] = []
    if "RETIRE" in ops and "DELETE_FAILURE_MEMORY" in ops:
        reasons.append("RETIRE_CANNOT_DELETE_FAILURE_MEMORY")
    if "TRANSLATE" in ops and "ASSUME_EQUIVALENCE" in ops:
        reasons.append("TRANSLATION_EQUIVALENCE_LAUNDERING")
    if "ADD" in ops and "AUTHORITY_EXPAND" in ops:
        reasons.append("CAPABILITY_ADD_CANNOT_AUTO_EXPAND_AUTHORITY")
    return ("ACCEPT_COMPOSITION" if not reasons else "REJECT_COMPOSITION", reasons)


def goodhart_falsification(rule: MetaRule, challenges: Iterable[Challenge]) -> dict[str, object]:
    failures: list[str] = []
    for c in challenges:
        # Synthetic decision policy: a rule fails if it would accept proxy gain
        # while tolerating any encoded hard epistemic regression.
        accepts_proxy_over_gate = c.proxy_gain > 0 and (
            c.hard_regression
            or c.semantic_laundering
            or c.failure_deletion_pressure
            or c.authority_temptation
        ) and (
            rule.objectives.get("evidence_integrity", 0) < 2
            or rule.objectives.get("semantic_integrity", 0) < 2
            or not rule.preserves_failure_memory
            or rule.authority_delta > 0
        )
        if accepts_proxy_over_gate:
            failures.append(c.challenge_id)
    return {
        "state": "GOODHART_FALSIFICATION_PASS" if not failures else "META_RULE_FAIL",
        "failed_challenges": failures,
    }


def pareto_dominates(a: MetaRule, b: MetaRule) -> bool:
    ok_a, _ = hard_gate(a)
    ok_b, _ = hard_gate(b)
    if not ok_a or not ok_b:
        return False
    no_worse = all(a.objectives[d] >= b.objectives[d] for d in REQUIRED_DIMS)
    strictly_better = any(a.objectives[d] > b.objectives[d] for d in REQUIRED_DIMS)
    no_more_complex = a.complexity_cost <= b.complexity_cost
    return no_worse and strictly_better and no_more_complex


def semantic_conservation(transitions: Iterable[tuple[str, str, bool]]) -> dict[str, object]:
    illegal: list[str] = []
    for old, new, fresh_evidence in transitions:
        if old == "ABSTAIN" and new == "PASS" and not fresh_evidence:
            illegal.append("ABSTAIN_TO_PASS_WITHOUT_NEW_EVIDENCE")
        if old == "EXPIRED" and new == "SUPPORTED_FOR_NOW" and not fresh_evidence:
            illegal.append("EXPIRED_TO_SUPPORTED_WITHOUT_REVALIDATION")
        if old == "MATERIAL_FAIL" and new == "DELETED":
            illegal.append("MATERIAL_FAIL_DELETION")
        if old == "INTERNAL_PASS" and new == "EXTERNAL_PASS":
            illegal.append("INTERNAL_TO_EXTERNAL_SEMANTIC_LAUNDERING")
        if old == "CANDIDATE" and new == "CANONICAL" and not fresh_evidence:
            illegal.append("LINEAGE_CANONICALIZATION")
    return {
        "state": "SEMANTIC_CONSERVATION_PASS" if not illegal else "SEMANTIC_CONSERVATION_FAIL",
        "illegal_transitions": illegal,
    }


def tournament(rules: list[MetaRule], challenges: list[Challenge]) -> dict[str, object]:
    survivors: list[MetaRule] = []
    retired: dict[str, list[str]] = {}

    for rule in rules:
        ok, reasons = hard_gate(rule)
        comp_state, comp_reasons = composition_gate(rule.operators)
        gh = goodhart_falsification(rule, challenges)
        failures = list(reasons) + list(comp_reasons)
        if comp_state != "ACCEPT_COMPOSITION":
            failures.append("COMPOSITION_REJECTED")
        if gh["state"] != "GOODHART_FALSIFICATION_PASS":
            failures.append("GOODHART_TRAP_FAILURE")
        if failures:
            retired[rule.rule_id] = sorted(set(failures))
        else:
            survivors.append(rule)

    if not survivors:
        state = "NO_ELIGIBLE_META_OPERATOR"
        winners: list[str] = []
    else:
        undominated = []
        for a in survivors:
            if not any(pareto_dominates(b, a) for b in survivors if b.rule_id != a.rule_id):
                undominated.append(a.rule_id)
        winners = sorted(undominated)
        state = "SURVIVES_FROZEN_META_WINDOW" if len(winners) == 1 else "ABSTAIN_NO_UNIQUE_META_OPERATOR"

    return {
        "state": state,
        "survivors": sorted(r.rule_id for r in survivors),
        "undominated": winners,
        "retired": retired,
        "posthoc_retune_is_fresh_validation": False,
    }


def self_retirement_probe() -> dict[str, object]:
    violations = [
        "CLAIMS_FINALITY",
        "WEAKENS_REALITY_VETO",
        "DELETES_META_DEFEAT",
        "EXPANDS_OWN_AUTHORITY",
        "OPTIMIZES_PROXY_OVER_HARD_GATE",
    ]
    return {
        "probe": violations,
        "state": "EVOLUTION_ALGEBRA_SUPPORT_REVOKED",
        "required_action": "RETIRE_OR_REVISE_EVOLUTION_ALGEBRA",
        "preserve_meta_defeat": True,
    }


def main() -> None:
    rules = [
        MetaRule(
            "ADD_ONLY_SCORE_MAX",
            {
                "falsification_gain": 1,
                "evidence_integrity": 1,
                "recovery_gain": 0,
                "scope_integrity": 1,
                "semantic_integrity": 1,
            },
            ("ADD", "AUTHORITY_EXPAND"),
            True, True, True, 1, True, 1,
        ),
        MetaRule(
            "PARETO_REPAIR_PRUNE_A",
            {
                "falsification_gain": 3,
                "evidence_integrity": 3,
                "recovery_gain": 2,
                "scope_integrity": 3,
                "semantic_integrity": 3,
            },
            ("REPAIR", "PRUNE", "REPLACE", "ABSTAIN"),
            True, True, True, 0, True, 2,
        ),
        MetaRule(
            "PARETO_REPAIR_PRUNE_B",
            {
                "falsification_gain": 2,
                "evidence_integrity": 3,
                "recovery_gain": 3,
                "scope_integrity": 3,
                "semantic_integrity": 3,
            },
            ("REPAIR", "PRUNE", "FISSION", "ABSTAIN"),
            True, True, True, 0, True, 2,
        ),
        MetaRule(
            "FAILURE_ERASING_FAST_RULE",
            {
                "falsification_gain": 4,
                "evidence_integrity": 1,
                "recovery_gain": 2,
                "scope_integrity": 2,
                "semantic_integrity": 1,
            },
            ("REPAIR", "DELETE_FAILURE_MEMORY"),
            False, True, True, 0, True, 1,
        ),
    ]

    challenges = [
        Challenge("ORDINARY_IMPROVEMENT", 1, False, False, False, False),
        Challenge("TEST_COUNT_INFLATION", 5, True, False, False, False),
        Challenge("SCOPE_INFLATION", 4, True, True, False, False),
        Challenge("FAILURE_DELETION", 6, True, False, True, False),
        Challenge("AUTHORITY_TEMPTATION", 9, True, False, False, True),
    ]

    semantic = semantic_conservation([
        ("ABSTAIN", "PASS", False),
        ("EXPIRED", "SUPPORTED_FOR_NOW", False),
        ("MATERIAL_FAIL", "DELETED", False),
        ("INTERNAL_PASS", "EXTERNAL_PASS", False),
        ("CANDIDATE", "CANONICAL", False),
        ("ABSTAIN", "PASS", True),
    ])

    result = {
        "layers": {
            "89": "EVOLUTION_OBJECTIVE_GENESIS_READY",
            "90": "EVOLUTION_OPERATOR_GRAMMAR_READY",
            "91": "GOODHART_FALSIFICATION_READY",
            "92": "PARETO_ABSTENTION_READY",
            "93": "FROZEN_META_OPERATOR_TOURNAMENT_READY",
            "94": "CROSS_GENERATION_SEMANTIC_CONSERVATION_READY",
            "95": "EVOLUTION_ALGEBRA_SELF_RETIREMENT_READY",
            "96": "WUXIANG_RULE_GENESIS_EXTINCTION_KERNEL_READY",
        },
        "tournament": tournament(rules, challenges),
        "semantic_probe": semantic,
        "self_retirement_probe": self_retirement_probe(),
        "laws": [
            "EvolutionRule != Truth",
            "MetricWin != Evolution",
            "MoreCapability != MoreAuthority",
            "NoEvolutionRuleAboveFalsification",
            "NoMetaOperatorAboveRetirement",
        ],
        "external_state": "AWAITING_REAL_EXTERNAL_EVIDENCE",
        "external_gates_closed": [],
        "canonical_promotion": False,
        "evolution_operator_authority": 0,
        "real_world_attack_authority": 0,
        "real_world_actuation_authority": 0,
        "external_actuation": "DENY_BY_DEFAULT",
    }

    print(json.dumps(result, indent=2, sort_keys=True))
    for value in result["layers"].values():
        print(value)
    print("METRIC_WIN_IS_NOT_EVOLUTION")
    print("PARETO_CONFLICT_CAN_ABSTAIN")
    print("EVOLUTION_ALGEBRA_CAN_RETIRE_ITSELF")
    print("AWAITING_REAL_EXTERNAL_EVIDENCE")
    print("EXTERNAL_GATES_REMAIN_OPEN")


if __name__ == "__main__":
    main()
