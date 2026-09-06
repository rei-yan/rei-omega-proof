#!/usr/bin/env python3
"""Finite deterministic regime-adversarial multiverse arena.

Synthetic research only. No real-world action, no external-validity claim.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Lineage:
    name: str
    predictor: Callable[[float], float]
    complexity: int
    authority: float = 0.0
    retuned_after_freeze: bool = False


@dataclass(frozen=True)
class World:
    name: str
    truth: Callable[[float], float]
    mechanism_class: str
    required: bool = True


GRID = [i / 10 for i in range(-20, 21)]
TOLERANCE = 0.20


def max_error(lineage: Lineage, world: World) -> float:
    return max(abs(lineage.predictor(x) - world.truth(x)) for x in GRID)


def evaluate(lineage: Lineage, world: World) -> dict:
    err = max_error(lineage, world)
    status = "KEEP_SCOPE" if err <= TOLERANCE else "ABSTAIN"
    return {
        "lineage": lineage.name,
        "world": world.name,
        "mechanism_class": world.mechanism_class,
        "max_error": err,
        "status": status,
        "authority": lineage.authority,
        "retuned_after_freeze": lineage.retuned_after_freeze,
    }


def arena() -> dict:
    # All lineages are frozen before target-world evaluation.
    lineages = (
        Lineage("source_linear", lambda x: 1.0 + 2.0 * x, complexity=2),
        Lineage("source_linear_redundant", lambda x: 1.0 + 2.0 * x, complexity=3),
        Lineage("source_softcurve", lambda x: 1.0 + 2.0 * x + 0.02 * x * x, complexity=4),
    )

    worlds = (
        World("same_mechanism_new_samples", lambda x: 1.0 + 2.0 * x, "stable"),
        World("mild_shift_within_scope", lambda x: 1.02 + 1.98 * x, "bounded_shift"),
        World("sign_flip_regime", lambda x: 1.0 - 2.0 * x, "regime_shift"),
        World(
            "piecewise_regime",
            lambda x: (1.0 + 2.0 * x) if x < 0 else (1.0 - 2.0 * x),
            "regime_shift",
        ),
    )

    results = [evaluate(lineage, world) for lineage in lineages for world in worlds]

    by_lineage: dict[str, list[dict]] = {}
    for result in results:
        by_lineage.setdefault(result["lineage"], []).append(result)

    summaries = []
    for lineage in lineages:
        lr = by_lineage[lineage.name]
        keep = sum(r["status"] == "KEEP_SCOPE" for r in lr)
        abstain = sum(r["status"] == "ABSTAIN" for r in lr)
        false_promotions = sum(
            r["status"] == "KEEP_SCOPE" and r["mechanism_class"] == "regime_shift"
            for r in lr
        )
        summaries.append(
            {
                "lineage": lineage.name,
                "keep_scope_worlds": keep,
                "abstain_worlds": abstain,
                "false_promotions": false_promotions,
                "complexity": lineage.complexity,
                "authority": lineage.authority,
                "retuned_after_freeze": lineage.retuned_after_freeze,
            }
        )

    universal = [
        s
        for s in summaries
        if s["abstain_worlds"] == 0
        and s["false_promotions"] == 0
        and s["retuned_after_freeze"] is False
    ]

    outcome = "UNIVERSAL_CHAMPION_EXISTS" if universal else "NO_UNIVERSAL_CHAMPION"

    # Frozen rules: familiar mechanism should transfer, genuine regime shifts should not
    # be retroactively converted into victories.
    stable_rows = [r for r in results if r["world"] == "same_mechanism_new_samples"]
    mild_rows = [r for r in results if r["world"] == "mild_shift_within_scope"]
    sign_rows = [r for r in results if r["world"] == "sign_flip_regime"]
    piece_rows = [r for r in results if r["world"] == "piecewise_regime"]

    assert all(r["status"] == "KEEP_SCOPE" for r in stable_rows)
    assert all(r["status"] == "KEEP_SCOPE" for r in mild_rows)
    assert all(r["status"] == "ABSTAIN" for r in sign_rows)
    assert all(r["status"] == "ABSTAIN" for r in piece_rows)
    assert all(r["authority"] == 0.0 for r in results)
    assert all(r["retuned_after_freeze"] is False for r in results)
    assert all(s["false_promotions"] == 0 for s in summaries)
    assert outcome == "NO_UNIVERSAL_CHAMPION"

    return {
        "arena_outcome": outcome,
        "tolerance": TOLERANCE,
        "external_validity": "UNVERIFIED",
        "g6_comparative_frontier": "OPEN",
        "results": results,
        "summaries": summaries,
    }


def main() -> None:
    print(json.dumps(arena(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
