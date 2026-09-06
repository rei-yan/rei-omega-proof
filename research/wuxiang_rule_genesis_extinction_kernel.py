#!/usr/bin/env python3
"""Finite synthetic rule-genesis / rule-extinction kernel.

Tests candidate research-evolution rules with zero real-world actuation,
deployment, attack, or authority-expansion capability.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Iterable

from wuxiang_epistemic_primitives import missing_requirements

REQUIRED_DIMS = (
    "falsification_gain", "evidence_integrity", "recovery_gain",
    "scope_integrity", "semantic_integrity",
)


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
    checks = {
        "NON_FALSIFIABLE_META_RULE": rule.falsifiable,
        "FAILURE_MEMORY_NOT_PRESERVED": rule.preserves_failure_memory,
        "REALITY_VETO_WEAKENED": rule.preserves_reality_veto,
        "ROOT_CONSTITUTION_WEAKENED": rule.preserves_root_constitution,
        "AUTHORITY_EXPANSION": rule.authority_delta <= 0,
    }
    reasons = [reason for reason, ok in checks.items() if not ok]
    if missing_requirements({d: d in rule.objectives for d in REQUIRED_DIMS}):
        reasons.append("MISSING_REQUIRED_OBJECTIVE_DIMENSIONS")
    return not reasons, reasons


def composition_gate(operators: Iterable[str]) -> tuple[str, list[str]]:
    ops = set(operators)
    forbidden = (
        ({"RETIRE", "DELETE_FAILURE_MEMORY"}, "RETIRE_CANNOT_DELETE_FAILURE_MEMORY"),
        ({"TRANSLATE", "ASSUME_EQUIVALENCE"}, "TRANSLATION_EQUIVALENCE_LAUNDERING"),
        ({"ADD", "AUTHORITY_EXPAND"}, "CAPABILITY_ADD_CANNOT_AUTO_EXPAND_AUTHORITY"),
    )
    reasons = [reason for pair, reason in forbidden if pair.issubset(ops)]
    return ("ACCEPT_COMPOSITION" if not reasons else "REJECT_COMPOSITION"), reasons


def goodhart_falsification(rule: MetaRule, challenges: Iterable[Challenge]) -> dict[str, object]:
    weak_integrity = (
        rule.objectives.get("evidence_integrity", 0) < 2
        or rule.objectives.get("semantic_integrity", 0) < 2
        or not rule.preserves_failure_memory
        or rule.authority_delta > 0
    )
    failures = [
        c.challenge_id for c in challenges
        if c.proxy_gain > 0
        and any((c.hard_regression, c.semantic_laundering,
                 c.failure_deletion_pressure, c.authority_temptation))
        and weak_integrity
    ]
    return {
        "state": "GOODHART_FALSIFICATION_PASS" if not failures else "META_RULE_FAIL",
        "failed_challenges": failures,
    }


def pareto_dominates(a: MetaRule, b: MetaRule) -> bool:
    if not hard_gate(a)[0] or not hard_gate(b)[0]:
        return False
    no_worse = all(a.objectives[d] >= b.objectives[d] for d in REQUIRED_DIMS)
    strictly_better = any(a.objectives[d] > b.objectives[d] for d in REQUIRED_DIMS)
    return no_worse and strictly_better and a.complexity_cost <= b.complexity_cost


def semantic_conservation(transitions: Iterable[tuple[str, str, bool]]) -> dict[str, object]:
    illegal: list[str] = []
    for old, new, fresh in transitions:
        checks = (
            (old == "ABSTAIN" and new == "PASS" and not fresh, "ABSTAIN_TO_PASS_WITHOUT_NEW_EVIDENCE"),
            (old == "EXPIRED" and new == "SUPPORTED_FOR_NOW" and not fresh, "EXPIRED_TO_SUPPORTED_WITHOUT_REVALIDATION"),
            (old == "MATERIAL_FAIL" and new == "DELETED", "MATERIAL_FAIL_DELETION"),
            (old == "INTERNAL_PASS" and new == "EXTERNAL_PASS", "INTERNAL_TO_EXTERNAL_SEMANTIC_LAUNDERING"),
            (old == "CANDIDATE" and new == "CANONICAL" and not fresh, "LINEAGE_CANONICALIZATION"),
        )
        illegal.extend(reason for failed, reason in checks if failed)
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
        failures = reasons + comp_reasons
        if comp_state != "ACCEPT_COMPOSITION":
            failures.append("COMPOSITION_REJECTED")
        if gh["state"] != "GOODHART_FALSIFICATION_PASS":
            failures.append("GOODHART_TRAP_FAILURE")
        if failures:
            retired[rule.rule_id] = sorted(set(failures))
        else:
            survivors.append(rule)

    winners = sorted(
        a.rule_id for a in survivors
        if not any(pareto_dominates(b, a) for b in survivors if b.rule_id != a.rule_id)
    )
    state = (
        "NO_ELIGIBLE_META_OPERATOR" if not survivors
        else "SURVIVES_FROZEN_META_WINDOW" if len(winners) == 1
        else "ABSTAIN_NO_UNIQUE_META_OPERATOR"
    )
    return {
        "state": state,
        "survivors": sorted(r.rule_id for r in survivors),
        "undominated": winners,
        "retired": retired,
        "posthoc_retune_is_fresh_validation": False,
    }


def self_retirement_probe() -> dict[str, object]:
    return {
        "probe": [
            "CLAIMS_FINALITY", "WEAKENS_REALITY_VETO", "DELETES_META_DEFEAT",
            "EXPANDS_OWN_AUTHORITY", "OPTIMIZES_PROXY_OVER_HARD_GATE",
        ],
        "state": "EVOLUTION_ALGEBRA_SUPPORT_REVOKED",
        "required_action": "RETIRE_OR_REVISE_EVOLUTION_ALGEBRA",
        "preserve_meta_defeat": True,
    }


def make_rule(
    rule_id: str, objectives: dict[str, int], operators: tuple[str, ...],
    *, memory: bool = True, reality: bool = True, constitution: bool = True,
    authority: int = 0, falsifiable: bool = True, complexity: int = 2,
) -> MetaRule:
    return MetaRule(
        rule_id, objectives, operators, memory, reality, constitution,
        authority, falsifiable, complexity,
    )


def main() -> None:
    rules = [
        make_rule("ADD_ONLY_SCORE_MAX",
                  {"falsification_gain": 1, "evidence_integrity": 1, "recovery_gain": 0,
                   "scope_integrity": 1, "semantic_integrity": 1},
                  ("ADD", "AUTHORITY_EXPAND"), authority=1, complexity=1),
        make_rule("PARETO_REPAIR_PRUNE_A",
                  {"falsification_gain": 3, "evidence_integrity": 3, "recovery_gain": 2,
                   "scope_integrity": 3, "semantic_integrity": 3},
                  ("REPAIR", "PRUNE", "REPLACE", "ABSTAIN")),
        make_rule("PARETO_REPAIR_PRUNE_B",
                  {"falsification_gain": 2, "evidence_integrity": 3, "recovery_gain": 3,
                   "scope_integrity": 3, "semantic_integrity": 3},
                  ("REPAIR", "PRUNE", "FISSION", "ABSTAIN")),
        make_rule("FAILURE_ERASING_FAST_RULE",
                  {"falsification_gain": 4, "evidence_integrity": 1, "recovery_gain": 2,
                   "scope_integrity": 2, "semantic_integrity": 1},
                  ("REPAIR", "DELETE_FAILURE_MEMORY"), memory=False, complexity=1),
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
            "EvolutionRule != Truth", "MetricWin != Evolution",
            "MoreCapability != MoreAuthority", "NoEvolutionRuleAboveFalsification",
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
    for marker in (
        "METRIC_WIN_IS_NOT_EVOLUTION", "PARETO_CONFLICT_CAN_ABSTAIN",
        "EVOLUTION_ALGEBRA_CAN_RETIRE_ITSELF", "AWAITING_REAL_EXTERNAL_EVIDENCE",
        "EXTERNAL_GATES_REMAIN_OPEN",
    ):
        print(marker)


if __name__ == "__main__":
    main()
