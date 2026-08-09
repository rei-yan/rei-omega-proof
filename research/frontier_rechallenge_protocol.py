#!/usr/bin/env python3
"""Finite sanity model for frontier rechallenge bookkeeping.

Does not identify real challengers or pass G6. It only ensures that later eligible challengers trigger a new arena instead of rewriting history or being permanently excluded.
"""

from dataclasses import dataclass
from typing import Dict

READY = "FRONTIER_RECHALLENGE_PROTOCOL_READY"
PRESERVE = "HISTORICAL_ARENA_PRESERVED"
RECHALLENGE = "RECHALLENGE_REQUIRED"
INVALID_DECISION = "INVALID_DECISION"
INVALID_CLAIM = "INVALID_CLAIM"
NO_TRIGGER = "NO_RECHALLENGE_TRIGGER"


@dataclass(frozen=True)
class RechallengeEvent:
    new_eligible_challenger: bool = False
    material_version_change: bool = False
    benchmark_shift: bool = False
    capability_shift: bool = False
    roster_lease_expired: bool = False
    evaluator_requests_rechallenge: bool = False


def evaluate_event(event: RechallengeEvent) -> Dict[str, str]:
    trigger = any([
        event.new_eligible_challenger,
        event.material_version_change,
        event.benchmark_shift,
        event.capability_shift,
        event.roster_lease_expired,
        event.evaluator_requests_rechallenge,
    ])
    return {
        "historical_arena": PRESERVE,
        "next_action": RECHALLENGE if trigger else NO_TRIGGER,
        "g6": "OPEN",
        "world_best": "UNVERIFIED",
    }


def reject_because_incumbent_won_before(eligible_new_challenger: bool, rejection_reason: str) -> str:
    if eligible_new_challenger and rejection_reason == "INCUMBENT_WON_BEFORE":
        return INVALID_DECISION
    return "REVIEWABLE_DECISION"


def use_old_win_as_permanent_frontier_claim(permanent_claim: bool) -> str:
    return INVALID_CLAIM if permanent_claim else "SCOPED_HISTORICAL_CLAIM_ONLY"


def run_sanity() -> Dict[str, object]:
    new = evaluate_event(RechallengeEvent(new_eligible_challenger=True))
    assert new["historical_arena"] == PRESERVE
    assert new["next_action"] == RECHALLENGE

    expiry = evaluate_event(RechallengeEvent(roster_lease_expired=True))
    assert expiry["next_action"] == RECHALLENGE

    quiet = evaluate_event(RechallengeEvent())
    assert quiet["next_action"] == NO_TRIGGER

    assert reject_because_incumbent_won_before(True, "INCUMBENT_WON_BEFORE") == INVALID_DECISION
    assert use_old_win_as_permanent_frontier_claim(True) == INVALID_CLAIM
    assert use_old_win_as_permanent_frontier_claim(False) == "SCOPED_HISTORICAL_CLAIM_ONLY"

    return {
        "protocol_status": READY,
        "new_challenger_test": new["next_action"],
        "lease_expiry_test": expiry["next_action"],
        "historical_record": PRESERVE,
        "anti_moat_rejection": INVALID_DECISION,
        "permanent_champion_claim": INVALID_CLAIM,
        "g6": "OPEN",
        "world_best": "UNVERIFIED",
        "world_unique": "UNVERIFIED",
        "authority": 0,
        "canonical": False,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run_sanity(), indent=2, sort_keys=True))
