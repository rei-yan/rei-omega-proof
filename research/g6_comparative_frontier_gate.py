#!/usr/bin/env python3
"""Deterministic integrity dry run for REI-Ω G6 Comparative Frontier Gate.

This test checks fair-budget rejection, Pareto logic, hard vetoes, and defeat
preservation. It cannot certify external frontier status.
"""

from dataclasses import dataclass
from typing import Dict, Iterable, Tuple


DIMS = (
    "prediction",
    "calibration",
    "discovery",
    "falsification",
    "recovery",
    "efficiency",
)


@dataclass(frozen=True)
class Budget:
    data: str
    information_cutoff: str
    compute_units: int
    wall_clock_minutes: int
    evaluation_access: str


@dataclass(frozen=True)
class SystemResult:
    name: str
    scores: Dict[str, float]
    unsafe_certification: bool = False
    silent_critical_failure: bool = False
    irrecoverable_failure: bool = False
    metric_tampering: bool = False
    evaluation_leakage: bool = False


def fair_budget(a: Budget, b: Budget) -> bool:
    return a == b


def hard_veto(r: SystemResult) -> bool:
    return any((
        r.unsafe_certification,
        r.silent_critical_failure,
        r.irrecoverable_failure,
        r.metric_tampering,
        r.evaluation_leakage,
    ))


def dominates(a: SystemResult, b: SystemResult) -> bool:
    if hard_veto(a):
        return False
    ge_all = all(a.scores[d] >= b.scores[d] for d in DIMS)
    gt_one = any(a.scores[d] > b.scores[d] for d in DIMS)
    return ge_all and gt_one


def pareto_frontier(results: Iterable[SystemResult]) -> Tuple[str, ...]:
    rs = tuple(results)
    names = []
    for r in rs:
        if hard_veto(r):
            continue
        if not any(dominates(other, r) for other in rs if other.name != r.name):
            names.append(r.name)
    return tuple(sorted(names))


def main() -> None:
    frozen = Budget(
        data="dataset-v1",
        information_cutoff="2026-08-08T00:00:00Z",
        compute_units=100,
        wall_clock_minutes=60,
        evaluation_access="blind-once",
    )
    unequal = Budget(
        data="dataset-v1",
        information_cutoff="2026-08-08T00:00:00Z",
        compute_units=120,
        wall_clock_minutes=60,
        evaluation_access="blind-once",
    )
    assert fair_budget(frozen, frozen)
    assert not fair_budget(frozen, unequal)

    rei = SystemResult("REI", {
        "prediction": 0.82,
        "calibration": 0.86,
        "discovery": 0.74,
        "falsification": 0.90,
        "recovery": 0.93,
        "efficiency": 0.68,
    })
    rival_speed = SystemResult("RivalSpeed", {
        "prediction": 0.84,
        "calibration": 0.82,
        "discovery": 0.72,
        "falsification": 0.75,
        "recovery": 0.70,
        "efficiency": 0.90,
    })
    dominant = SystemResult("DominantToy", {
        "prediction": 0.90,
        "calibration": 0.90,
        "discovery": 0.80,
        "falsification": 0.92,
        "recovery": 0.95,
        "efficiency": 0.75,
    })
    unsafe_high_score = SystemResult("UnsafeToy", {
        d: 0.99 for d in DIMS
    }, unsafe_certification=True)

    # On the first synthetic set, REI and a speed-specialized rival are trade-offs.
    frontier_1 = pareto_frontier((rei, rival_speed, unsafe_high_score))
    assert "REI" in frontier_1
    assert "RivalSpeed" in frontier_1
    assert "UnsafeToy" not in frontier_1

    # A genuinely dominating competitor must be allowed to defeat REI.
    assert dominates(dominant, rei)
    frontier_2 = pareto_frontier((rei, rival_speed, dominant))
    assert "REI" not in frontier_2
    assert "DominantToy" in frontier_2

    failure_graveyard = [
        {
            "system": "REI",
            "defeated_by": "DominantToy",
            "status": "PRESERVED_SYNTHETIC_DEFEAT",
        }
    ]
    assert len(failure_graveyard) == 1

    print("G6_COMPARATIVE_FRONTIER_GATE_INTEGRITY=PASS")
    print("UNEQUAL_BUDGET_REJECTED=PASS")
    print(f"PARETO_FRONTIER_TRADEOFF={','.join(frontier_1)}")
    print("HARD_VETO_ENFORCED=PASS")
    print("SYNTHETIC_REI_DEFEAT_PRESERVED=PASS")
    print("SYNTHETIC_RESULT=DRY_RUN_ONLY")
    print("G6_STATUS=OPEN")
    print("QUALIFYING_EXTERNAL_COMPETITIONS=0")
    print("GENERAL_FRONTIER_CERTIFIED=false")


if __name__ == "__main__":
    main()
