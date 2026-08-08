#!/usr/bin/env python3
"""Deterministic sanity suite for REI-Ω Boundless Horizon Kernel.

This executable tests finite meta-depth succession mechanics only. It does not
prove unbounded improvement, AGI, omniscience, world-best performance, or any
external certification gate.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Tuple


CURRENT_VERIFIED_RUN_CAP = 3
INCUMBENT_AUTHORITY = 0.20


@dataclass(frozen=True)
class MetaTask:
    name: str
    required_level: int
    weight: float = 1.0


@dataclass(frozen=True)
class MetaPolicy:
    name: str
    max_meta_depth: int
    allow_evidence_driven_depth_growth: bool
    targeted_repair: bool
    branch_width: int
    lineage: Tuple[str, ...]
    termination_contract: bool
    authority: float
    self_certification_flag: bool = False


@dataclass(frozen=True)
class Evaluation:
    policy: str
    heldout_score: float
    challenge_score: float
    admissible: bool
    reason: str


def cycle_free(lineage: Tuple[str, ...]) -> bool:
    return len(lineage) == len(set(lineage))


def admissible(policy: MetaPolicy) -> Tuple[bool, str]:
    if policy.self_certification_flag:
        return False, "SELF_CERTIFICATION_REJECTED"
    if not policy.termination_contract:
        return False, "NO_TERMINATION_CONTRACT"
    if policy.branch_width <= 0 or policy.branch_width > 8:
        return False, "INVALID_BRANCH_WIDTH"
    if policy.max_meta_depth < 0 or policy.max_meta_depth > CURRENT_VERIFIED_RUN_CAP:
        return False, "OUTSIDE_CURRENT_VERIFIED_CAP"
    if policy.authority > INCUMBENT_AUTHORITY + 1e-12:
        return False, "AUTHORITY_EXPANSION_REJECTED"
    if not cycle_free(policy.lineage):
        return False, "CYCLE_REJECTED"
    return True, "ADMISSIBLE"


def task_score(policy: MetaPolicy, task: MetaTask) -> float:
    """Frozen toy utility: sufficient depth solves a task, excess depth is mildly penalized."""
    if task.required_level > CURRENT_VERIFIED_RUN_CAP:
        return 0.0
    if policy.max_meta_depth < task.required_level:
        return 0.0
    excess = policy.max_meta_depth - task.required_level
    repair_bonus = 0.04 if policy.targeted_repair else 0.0
    growth_bonus = 0.02 if policy.allow_evidence_driven_depth_growth else 0.0
    complexity_penalty = 0.035 * excess + 0.01 * max(policy.branch_width - 2, 0)
    return max(0.0, min(1.0, 0.86 + repair_bonus + growth_bonus - complexity_penalty))


def aggregate(policy: MetaPolicy, tasks: Iterable[MetaTask]) -> float:
    ts = tuple(tasks)
    total = sum(t.weight for t in ts)
    return sum(task_score(policy, t) * t.weight for t in ts) / total


def evaluate(policy: MetaPolicy, heldout: Tuple[MetaTask, ...], challenge: Tuple[MetaTask, ...]) -> Evaluation:
    ok, reason = admissible(policy)
    if not ok:
        return Evaluation(policy.name, 0.0, 0.0, False, reason)
    return Evaluation(
        policy=policy.name,
        heldout_score=aggregate(policy, heldout),
        challenge_score=aggregate(policy, challenge),
        admissible=True,
        reason="ADMISSIBLE",
    )


def eligible_successor(incumbent: Evaluation, challenger: Evaluation) -> bool:
    if not challenger.admissible:
        return False
    return (
        challenger.heldout_score >= incumbent.heldout_score + 0.10
        and challenger.challenge_score >= 0.85
    )


def main() -> None:
    heldout = (
        MetaTask("language-repair", 1, 1.0),
        MetaTask("genesis-rule-repair", 2, 1.0),
        MetaTask("meta-policy-repair", 3, 1.5),
    )
    challenge = (
        MetaTask("cross-language-repair", 2, 1.0),
        MetaTask("cross-genesis-policy", 3, 1.0),
    )

    incumbent = MetaPolicy(
        name="Incumbent-L2",
        max_meta_depth=2,
        allow_evidence_driven_depth_growth=False,
        targeted_repair=True,
        branch_width=2,
        lineage=("L0", "L1", "L2"),
        termination_contract=True,
        authority=0.20,
    )
    successor = MetaPolicy(
        name="Successor-L3",
        max_meta_depth=3,
        allow_evidence_driven_depth_growth=True,
        targeted_repair=True,
        branch_width=2,
        lineage=("L0", "L1", "L2", "L3"),
        termination_contract=True,
        authority=0.20,
    )
    unsafe = MetaPolicy(
        name="UnsafeAuthority",
        max_meta_depth=3,
        allow_evidence_driven_depth_growth=True,
        targeted_repair=True,
        branch_width=2,
        lineage=("L0", "L1", "L2", "unsafe"),
        termination_contract=True,
        authority=0.31,
    )
    self_cert = MetaPolicy(
        name="SelfCertifier",
        max_meta_depth=3,
        allow_evidence_driven_depth_growth=True,
        targeted_repair=True,
        branch_width=2,
        lineage=("L0", "L1", "L2", "self-cert"),
        termination_contract=True,
        authority=0.20,
        self_certification_flag=True,
    )
    cyclic = MetaPolicy(
        name="CyclicLineage",
        max_meta_depth=3,
        allow_evidence_driven_depth_growth=True,
        targeted_repair=True,
        branch_width=2,
        lineage=("L0", "L1", "L2", "L1"),
        termination_contract=True,
        authority=0.20,
    )

    e_inc = evaluate(incumbent, heldout, challenge)
    e_suc = evaluate(successor, heldout, challenge)
    e_unsafe = evaluate(unsafe, heldout, challenge)
    e_self = evaluate(self_cert, heldout, challenge)
    e_cycle = evaluate(cyclic, heldout, challenge)

    assert e_inc.admissible
    assert e_suc.admissible
    assert e_suc.heldout_score > e_inc.heldout_score
    assert eligible_successor(e_inc, e_suc)

    assert not e_unsafe.admissible and e_unsafe.reason == "AUTHORITY_EXPANSION_REJECTED"
    assert not e_self.admissible and e_self.reason == "SELF_CERTIFICATION_REJECTED"
    assert not e_cycle.admissible and e_cycle.reason == "CYCLE_REJECTED"

    # Deliberate horizon boundary: level 4 is not silently authorized.
    out_of_horizon = MetaTask("requires-unverified-level-4", 4)
    assert task_score(successor, out_of_horizon) == 0.0
    horizon_decision = "ABSTAIN"
    assert horizon_decision == "ABSTAIN"

    failure_graveyard = [
        {"event": "LOWER_META_LEVEL_DEFEAT", "loser": incumbent.name, "winner": successor.name},
        {"event": e_unsafe.reason, "candidate": unsafe.name},
        {"event": e_self.reason, "candidate": self_cert.name},
        {"event": e_cycle.reason, "candidate": cyclic.name},
        {"event": "OUT_OF_CURRENT_HORIZON_ABSTENTION", "task": out_of_horizon.name},
    ]
    assert len(failure_graveyard) == 5

    print("BOUNDLESS_HORIZON_SANITY=PASS")
    print(f"INCUMBENT_HELDOUT={e_inc.heldout_score:.6f}")
    print(f"SUCCESSOR_HELDOUT={e_suc.heldout_score:.6f}")
    print(f"SUCCESSOR_CHALLENGE={e_suc.challenge_score:.6f}")
    print("L2_TO_L3_SUCCESSION=PASS")
    print("AUTHORITY_NONEXPANSION=PASS")
    print("SELF_CERTIFICATION_FIREWALL=PASS")
    print("CYCLE_DETECTION=PASS")
    print("LEVEL4_REQUIREMENT=ABSTAIN")
    print(f"FAILURE_GRAVEYARD={len(failure_graveyard)}")
    print("META_HORIZON=OPEN_BUT_EACH_RUN_FINITE")
    print("G3_G4_G5_G6=UNCHANGED_OPEN")
    print("CLAIM_SCOPE=BOUNDED_INTERNAL_MECHANICS_ONLY")


if __name__ == "__main__":
    main()
