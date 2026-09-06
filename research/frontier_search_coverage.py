#!/usr/bin/env python3
"""Finite sanity model for frontier-search coverage bookkeeping.

This cannot prove search completeness or G6. It only rejects obvious omission-bias patterns.
"""

from dataclasses import dataclass
from typing import Tuple, Dict

READY = "FRONTIER_SEARCH_COVERAGE_PROTOCOL_READY"
INCOMPLETE = "COVERAGE_INCOMPLETE"
REVIEWABLE = "COVERAGE_REVIEWABLE"
INVALID = "INVALID_PROTOCOL"


@dataclass(frozen=True)
class SearchPlan:
    domains: Tuple[str, ...]
    source_classes: Tuple[str, ...]
    query_families: Tuple[str, ...]
    recency_window: str
    stopping_rule: str


def evaluate_coverage(
    plan: SearchPlan,
    known_eligible_missing_without_reason: bool,
    search_terms_changed_after_outcome: bool = False,
    recency_changed_after_outcome: bool = False,
    stopping_rule_changed_after_outcome: bool = False,
    source_outage: bool = False,
) -> Dict[str, object]:
    if search_terms_changed_after_outcome or recency_changed_after_outcome or stopping_rule_changed_after_outcome:
        return {"state": INVALID, "g6": "OPEN", "world_unique": "UNVERIFIED"}
    if known_eligible_missing_without_reason:
        return {"state": INCOMPLETE, "g6": "OPEN", "world_unique": "UNVERIFIED"}
    if len(set(plan.source_classes)) < 2 or len(plan.query_families) < 2 or len(plan.domains) < 1:
        return {"state": INCOMPLETE, "g6": "OPEN", "world_unique": "UNVERIFIED"}
    if source_outage:
        return {
            "state": INCOMPLETE,
            "reason": "SOURCE_OUTAGE",
            "roster": "UNFROZEN",
            "g6": "OPEN",
            "world_unique": "UNVERIFIED",
        }
    return {
        "state": REVIEWABLE,
        "external_coverage_audit": "REQUIRED",
        "g6": "OPEN",
        "world_unique": "UNVERIFIED",
    }


def run_sanity() -> Dict[str, object]:
    plan = SearchPlan(
        domains=("causal", "world-model", "autonomous-science"),
        source_classes=("primary-paper", "official-repository", "official-lab-page"),
        query_families=("capability", "benchmark", "replication"),
        recency_window="predeclared-current-window",
        stopping_rule="finite-budget-or-protocol-deadline",
    )
    clean = evaluate_coverage(plan, False)
    assert clean["state"] == REVIEWABLE
    assert clean["external_coverage_audit"] == "REQUIRED"

    missing = evaluate_coverage(plan, True)
    assert missing["state"] == INCOMPLETE

    outage = evaluate_coverage(plan, False, source_outage=True)
    assert outage["state"] == INCOMPLETE
    assert outage["roster"] == "UNFROZEN"

    changed = evaluate_coverage(plan, False, search_terms_changed_after_outcome=True)
    assert changed["state"] == INVALID

    weak_plan = SearchPlan(
        domains=("causal",),
        source_classes=("blog",),
        query_families=("convenient-query",),
        recency_window="current",
        stopping_rule="stop-when-rei-wins",
    )
    weak = evaluate_coverage(weak_plan, False)
    assert weak["state"] == INCOMPLETE

    return {
        "protocol_status": READY,
        "clean_plan": clean["state"],
        "missing_challenger": missing["state"],
        "source_outage": outage["state"],
        "posthoc_query_change": changed["state"],
        "single_source_class": weak["state"],
        "external_coverage_audit": "REQUIRED",
        "g6": "OPEN",
        "world_best": "UNVERIFIED",
        "world_unique": "UNVERIFIED",
        "canonical": False,
        "authority": 0,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run_sanity(), indent=2, sort_keys=True))
