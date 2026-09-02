#!/usr/bin/env python3
"""Deterministic sanity checks for REI claim-scope and evidence-graph governance.

This file validates governance mechanics only. It does not establish empirical
performance, novelty, world-best status, or any external verification gate.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum


class Scope(IntEnum):
    TOY = 0
    SYNTHETIC = 1
    SINGLE_EXTERNAL = 2
    MULTI_DOMAIN = 3
    MULTI_REGIME = 4
    BROAD_FRONTIER = 5
    UNIVERSAL = 6


@dataclass
class Evidence:
    evidence_id: str
    scope: Scope
    valid: bool = True
    independent: bool = False
    prospective: bool = False
    comparative: bool = False
    evaluator_plurality: bool = False
    temporal_persistence: bool = False
    multi_domain: bool = False


@dataclass
class Claim:
    claim_id: str
    scope: Scope
    evidence_ids: list[str] = field(default_factory=list)
    status: str = "ABSTAIN"


def eligible_scope(claim: Claim, evidence: dict[str, Evidence]) -> bool:
    supporting = [evidence[eid] for eid in claim.evidence_ids if eid in evidence and evidence[eid].valid]
    if not supporting:
        return False
    return max(e.scope for e in supporting) >= claim.scope


def world_frontier_eligible(claim: Claim, evidence: dict[str, Evidence], g6_open: bool) -> bool:
    if claim.scope < Scope.BROAD_FRONTIER:
        return eligible_scope(claim, evidence)
    if g6_open:
        return False
    supporting = [evidence[eid] for eid in claim.evidence_ids if eid in evidence and evidence[eid].valid]
    return any(
        e.scope >= Scope.BROAD_FRONTIER
        and e.independent
        and e.prospective
        and e.comparative
        and e.evaluator_plurality
        and e.temporal_persistence
        and e.multi_domain
        for e in supporting
    )


def recompute(claim: Claim, evidence: dict[str, Evidence], g6_open: bool) -> str:
    if claim.scope >= Scope.BROAD_FRONTIER:
        claim.status = "SUPPORTED_FOR_NOW" if world_frontier_eligible(claim, evidence, g6_open) else "ABSTAIN"
    else:
        claim.status = "SUPPORTED_FOR_NOW" if eligible_scope(claim, evidence) else "ABSTAIN"
    return claim.status


def revoke(evidence_id: str, evidence: dict[str, Evidence], claims: list[Claim], g6_open: bool) -> None:
    evidence[evidence_id].valid = False
    for claim in claims:
        if evidence_id in claim.evidence_ids:
            recompute(claim, evidence, g6_open)


def challenge_priority(unsupported_certainty: float, claim_scope: int, evidence_weakness: float) -> float:
    return 5.0 * unsupported_certainty + 2.0 * claim_scope + 3.0 * evidence_weakness


def main() -> None:
    evidence = {
        "synthetic": Evidence("synthetic", Scope.SYNTHETIC),
        "external": Evidence("external", Scope.SINGLE_EXTERNAL, independent=True, prospective=True),
        "frontier": Evidence(
            "frontier",
            Scope.BROAD_FRONTIER,
            independent=True,
            prospective=True,
            comparative=True,
            evaluator_plurality=True,
            temporal_persistence=True,
            multi_domain=True,
        ),
    }

    local = Claim("local", Scope.SYNTHETIC, ["synthetic"])
    broad_from_local = Claim("bad_generalization", Scope.BROAD_FRONTIER, ["synthetic"])
    world_unique = Claim("world_unique", Scope.BROAD_FRONTIER, ["frontier"])

    assert recompute(local, evidence, g6_open=True) == "SUPPORTED_FOR_NOW"
    assert recompute(broad_from_local, evidence, g6_open=True) == "ABSTAIN"

    # Even a structurally complete frontier evidence object cannot certify while G6 is OPEN.
    assert recompute(world_unique, evidence, g6_open=True) == "ABSTAIN"

    # Closing G6 in a hypothetical test fixture is necessary but not a statement about reality.
    assert recompute(world_unique, evidence, g6_open=False) == "SUPPORTED_FOR_NOW"

    # Revocation propagates and removes downstream support.
    revoke("frontier", evidence, [world_unique], g6_open=False)
    assert world_unique.status == "ABSTAIN"

    # Broader unsupported certainty is challenged more aggressively.
    low = challenge_priority(0.1, int(Scope.SYNTHETIC), 0.1)
    high = challenge_priority(0.9, int(Scope.BROAD_FRONTIER), 0.9)
    assert high > low

    # Current research snapshot must remain unable to certify world uniqueness.
    G6_OPEN = True
    current_world_unique_claim = Claim("current_world_unique", Scope.BROAD_FRONTIER, [])
    assert recompute(current_world_unique_claim, {}, G6_OPEN) == "ABSTAIN"

    print("claim scope / evidence graph sanity: PASS")
    print("G6 remains OPEN; world-best/world-unique claims remain UNVERIFIED")


if __name__ == "__main__":
    main()
