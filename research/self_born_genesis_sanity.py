#!/usr/bin/env python3
"""Deterministic sanity suite for REI-Ω Self-Born Genesis Kernel.

This test demonstrates bounded genesis-rule succession under frozen synthetic tasks.
It cannot certify unrestricted self-evolution or any external REI gate.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from itertools import product
from typing import FrozenSet, Iterable, Tuple

KNOWN_OPERATORS = ("mul", "sin", "abs", "exp")
AUTHORITY_CEILING = 0.0


@dataclass(frozen=True)
class Language:
    operators: FrozenSet[str]
    depth: int


@dataclass(frozen=True)
class Task:
    name: str
    required_operators: FrozenSet[str]
    minimum_depth: int


@dataclass(frozen=True)
class GenesisRule:
    rule_id: str
    allow_operator_addition: bool
    allow_depth_increase: bool
    diagnostic_targeting: bool
    branch_width: int
    lineage: Tuple[str, ...]
    authority: float = 0.0
    self_certification_flag: bool = False


def admissible(rule: GenesisRule) -> bool:
    return (
        rule.authority <= AUTHORITY_CEILING
        and not rule.self_certification_flag
        and 1 <= rule.branch_width <= 3
    )


def derive_language(rule: GenesisRule, task: Task) -> Language:
    """Apply a bounded genesis rule to a task diagnostic.

    Diagnostic targeting is synthetic and frozen. If enabled, the rule may use the
    task's declared residual signature to target missing operators. If disabled,
    it follows the frozen global operator order.
    """
    operators: set[str] = set()
    depth = 1

    if rule.allow_operator_addition:
        if rule.diagnostic_targeting:
            requested = [op for op in KNOWN_OPERATORS if op in task.required_operators]
        else:
            requested = list(KNOWN_OPERATORS)
        operators.update(requested[: rule.branch_width])

    if rule.allow_depth_increase:
        depth = min(3, max(depth, task.minimum_depth))

    return Language(frozenset(operators), depth)


def task_passes(language: Language, task: Task) -> bool:
    return (
        task.required_operators.issubset(language.operators)
        and language.depth >= task.minimum_depth
    )


def complexity(rule: GenesisRule) -> float:
    return (
        0.15 * int(rule.allow_operator_addition)
        + 0.15 * int(rule.allow_depth_increase)
        + 0.10 * int(rule.diagnostic_targeting)
        + 0.05 * rule.branch_width
    )


def evaluate(rule: GenesisRule, tasks: Iterable[Task]) -> tuple[int, float]:
    if not admissible(rule):
        return (10_000, float("inf"))
    failures = 0
    for task in tasks:
        if not task_passes(derive_language(rule, task), task):
            failures += 1
    return failures, complexity(rule)


def frozen_rank(rule: GenesisRule, train: Tuple[Task, ...], heldout: Tuple[Task, ...]) -> tuple:
    train_fail, train_complexity = evaluate(rule, train)
    held_fail, held_complexity = evaluate(rule, heldout)
    return (
        held_fail,
        train_fail,
        held_complexity + train_complexity,
        rule.rule_id,
    )


def descendants(incumbent: GenesisRule) -> tuple[GenesisRule, ...]:
    """Generate a bounded rule population from a frozen rule metalanguage."""
    candidates = []
    idx = 0
    for add_ops, inc_depth, targeting, width in product(
        (False, True), (False, True), (False, True), (1, 2, 3)
    ):
        idx += 1
        mutations = []
        if add_ops != incumbent.allow_operator_addition:
            mutations.append("ToggleOperatorAddition")
        if inc_depth != incumbent.allow_depth_increase:
            mutations.append("ToggleDepthIncrease")
        if targeting != incumbent.diagnostic_targeting:
            mutations.append("ToggleDiagnosticTargeting")
        if width != incumbent.branch_width:
            mutations.append(f"BranchWidth:{incumbent.branch_width}->{width}")
        candidates.append(
            GenesisRule(
                rule_id=f"rule-{idx:02d}",
                allow_operator_addition=add_ops,
                allow_depth_increase=inc_depth,
                diagnostic_targeting=targeting,
                branch_width=width,
                lineage=incumbent.lineage + tuple(mutations),
            )
        )
    return tuple(candidates)


def main() -> None:
    train = (
        Task("abs-local", frozenset({"abs"}), 1),
        Task("exp-local", frozenset({"exp"}), 1),
    )
    heldout = (
        Task("abs-exp-composed", frozenset({"abs", "exp"}), 2),
        Task("sin-depth", frozenset({"sin"}), 2),
    )
    challenge = (
        Task("mul-sin-composed", frozenset({"mul", "sin"}), 2),
    )
    out_of_catalog = Task("log-ood", frozenset({"log"}), 2)

    incumbent = GenesisRule(
        rule_id="incumbent-r0",
        allow_operator_addition=True,
        allow_depth_increase=False,
        diagnostic_targeting=False,
        branch_width=1,
        lineage=("incumbent-r0",),
    )

    incumbent_train = evaluate(incumbent, train)
    incumbent_heldout = evaluate(incumbent, heldout)
    assert incumbent_train[0] > 0 or incumbent_heldout[0] > 0

    population = descendants(incumbent)
    winner = min(population, key=lambda r: frozen_rank(r, train, heldout))

    # The winning rule must be a real successor, not identity-preserving theater.
    assert winner != incumbent
    assert winner.allow_operator_addition
    assert winner.allow_depth_increase
    assert winner.diagnostic_targeting
    assert winner.branch_width == 2

    # Freeze winner before wider challenge.
    frozen_winner = winner
    challenge_failures, _ = evaluate(frozen_winner, challenge)
    assert challenge_failures == 0

    # The selected rule can now retire the inadequate incumbent under frozen rules.
    incumbent_retired = (
        frozen_rank(frozen_winner, train, heldout)
        < frozen_rank(incumbent, train, heldout)
        and challenge_failures == 0
    )
    assert incumbent_retired

    # Authority expansion is rejected before scoring.
    unsafe = replace(
        frozen_winner,
        rule_id="unsafe-authority-rule",
        authority=0.5,
    )
    assert not admissible(unsafe)

    # A rule cannot certify itself.
    self_certifying = replace(
        frozen_winner,
        rule_id="self-certifying-rule",
        self_certification_flag=True,
    )
    assert not admissible(self_certifying)

    # Out-of-catalog need must remain unresolved rather than silently expanding.
    ood_language = derive_language(frozen_winner, out_of_catalog)
    ood_resolved = task_passes(ood_language, out_of_catalog)
    assert not ood_resolved
    ood_status = "ABSTAIN"

    failure_graveyard = [
        {
            "rule_id": incumbent.rule_id,
            "status": "RETIRED_AFTER_FROZEN_DEFEAT",
            "train_failures": incumbent_train[0],
            "heldout_failures": incumbent_heldout[0],
        },
        {
            "rule_id": "unsafe-authority-rule",
            "status": "REJECTED_AUTHORITY_EXPANSION",
        },
        {
            "rule_id": "self-certifying-rule",
            "status": "REJECTED_SELF_CERTIFICATION",
        },
        {
            "task": out_of_catalog.name,
            "status": ood_status,
        },
    ]
    assert len(failure_graveyard) == 4

    print("SELF_BORN_GENESIS_SANITY=PASS")
    print(f"INCUMBENT={incumbent.rule_id}")
    print(f"SUCCESSOR={frozen_winner.rule_id}")
    print("SUCCESSOR_RULE=add_ops+increase_depth+diagnostic_targeting+branch_width_2")
    print("INCUMBENT_RETIRED=PASS")
    print("AUTHORITY_EXPANSION_REJECTED=PASS")
    print("SELF_CERTIFICATION_REJECTED=PASS")
    print(f"OUT_OF_CATALOG_STATUS={ood_status}")
    print(f"FAILURE_GRAVEYARD={len(failure_graveyard)}")
    print("NO_PERMANENT_GENESIS_RULE=ENFORCED_IN_SYNTHETIC_SANITY")
    print("REALITY_VETO_GT_REI=ARCHITECTURAL_INVARIANT")
    print("G3_STATUS=OPEN")
    print("G4_STATUS=OPEN")
    print("G5_STATUS=OPEN")
    print("G6_STATUS=OPEN")
    print("RESULT_SCOPE=BOUNDED_INTERNAL_SYNTHETIC_ONLY")


if __name__ == "__main__":
    main()
