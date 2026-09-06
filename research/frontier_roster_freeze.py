#!/usr/bin/env python3
"""Finite sanity model for Frontier Roster Freeze.

Does not identify the actual world frontier and cannot pass G6.
It only checks admission-state, provenance, version binding and anti-cherry-pick rules.
"""

from dataclasses import dataclass
from typing import Optional, Tuple, List, Dict

READY = "FRONTIER_ROSTER_FREEZE_PROTOCOL_READY"
CANDIDATE = "ROSTER_CANDIDATE"
SOURCE_VERIFIED = "SOURCE_VERIFIED"
COMPARABILITY_REVIEW = "COMPARABILITY_REVIEW"
FROZEN = "FROZEN_FRONTIER_COMPETITOR"
EXCLUDED = "EXCLUDED_WITH_REASON"
STALE = "STALE_REVALIDATION_REQUIRED"
INVALID = "INVALID_PROTOCOL"


@dataclass(frozen=True)
class Challenger:
    challenger_id: str
    domain: str
    system_name: str
    version_or_commit: str
    primary_source_uri: str
    source_date: str
    implementation_uri: str
    task_scope: str
    inclusion_reason: str
    freshness_horizon: str
    admission_state: str = CANDIDATE


def admissible_source(c: Challenger) -> bool:
    return all([
        c.challenger_id,
        c.domain,
        c.system_name,
        c.version_or_commit,
        c.primary_source_uri,
        c.source_date,
        c.task_scope,
        c.inclusion_reason,
        c.freshness_horizon,
    ])


def freeze_roster(
    challengers: Tuple[Challenger, ...],
    search_complete: bool,
    comparability_verified: bool,
    source_verified_ids: Tuple[str, ...],
) -> Dict[str, object]:
    if not search_complete:
        return {
            "status": READY,
            "roster_state": "INCOMPLETE_SEARCH_NOT_FROZEN",
            "g6": "OPEN",
            "world_best": "UNVERIFIED",
            "frozen_ids": [],
        }

    frozen: List[str] = []
    pending: List[str] = []
    for c in challengers:
        if not admissible_source(c):
            pending.append(c.challenger_id)
            continue
        if c.challenger_id not in source_verified_ids:
            pending.append(c.challenger_id)
            continue
        if not comparability_verified:
            pending.append(c.challenger_id)
            continue
        frozen.append(c.challenger_id)

    return {
        "status": READY,
        "roster_state": "FROZEN" if frozen and not pending else "PARTIAL_NOT_FRONTIER_COMPLETE",
        "g6": "OPEN",
        "world_best": "UNVERIFIED",
        "frozen_ids": frozen,
        "pending_ids": pending,
    }


def mutation_after_freeze(
    removed_after_rei_loss: bool = False,
    added_weak_after_outcome: bool = False,
    version_swapped: bool = False,
) -> str:
    if removed_after_rei_loss or added_weak_after_outcome or version_swapped:
        return INVALID
    return "UNCHANGED"


def run_sanity() -> Dict[str, object]:
    a = Challenger(
        challenger_id="challenger-a",
        domain="synthetic-demo",
        system_name="A",
        version_or_commit="v1",
        primary_source_uri="primary://a",
        source_date="2026-01-01",
        implementation_uri="impl://a",
        task_scope="frozen synthetic task",
        inclusion_reason="meets predeclared demo inclusion rule",
        freshness_horizon="2026-12-31",
    )
    b = Challenger(
        challenger_id="challenger-b",
        domain="synthetic-demo",
        system_name="B",
        version_or_commit="v2",
        primary_source_uri="primary://b",
        source_date="2026-02-01",
        implementation_uri="impl://b",
        task_scope="frozen synthetic task",
        inclusion_reason="meets predeclared demo inclusion rule",
        freshness_horizon="2026-12-31",
    )

    unavailable = freeze_roster((a, b), False, True, ("challenger-a", "challenger-b"))
    assert unavailable["roster_state"] == "INCOMPLETE_SEARCH_NOT_FROZEN"
    assert unavailable["g6"] == "OPEN"

    frozen = freeze_roster((a, b), True, True, ("challenger-a", "challenger-b"))
    assert frozen["roster_state"] == "FROZEN"
    assert set(frozen["frozen_ids"]) == {"challenger-a", "challenger-b"}
    assert frozen["world_best"] == "UNVERIFIED"

    partial = freeze_roster((a, b), True, True, ("challenger-a",))
    assert partial["roster_state"] == "PARTIAL_NOT_FRONTIER_COMPLETE"
    assert "challenger-b" in partial["pending_ids"]

    assert mutation_after_freeze(removed_after_rei_loss=True) == INVALID
    assert mutation_after_freeze(added_weak_after_outcome=True) == INVALID
    assert mutation_after_freeze(version_swapped=True) == INVALID
    assert mutation_after_freeze() == "UNCHANGED"

    return {
        "protocol_status": READY,
        "search_failure_test": unavailable["roster_state"],
        "clean_freeze_test": frozen["roster_state"],
        "partial_source_test": partial["roster_state"],
        "posthoc_removal_test": INVALID,
        "posthoc_weak_addition_test": INVALID,
        "version_swap_test": INVALID,
        "g6": "OPEN",
        "world_best": "UNVERIFIED",
        "world_unique": "UNVERIFIED",
        "authority": 0,
        "canonical": False,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run_sanity(), indent=2, sort_keys=True))
