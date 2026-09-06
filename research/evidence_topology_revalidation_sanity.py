#!/usr/bin/env python3
"""Deterministic governance sanity checks for Evidence Topology & Revalidation Spine.

This file validates only internal research mechanics. It does not establish external
replication, prospective validity, frontier dominance, world uniqueness, or invincibility.
"""

from dataclasses import dataclass
from typing import Dict, List, Set


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    scope: int
    cluster: str
    review_horizon: int
    revoked: bool = False
    drift_ok: bool = True


@dataclass(frozen=True)
class Claim:
    claim_id: str
    scope: int
    dependencies: tuple[str, ...]
    high_impact: bool = False


def current_support(e: Evidence, now: int) -> bool:
    return (not e.revoked) and e.drift_ok and now <= e.review_horizon


def independent_cluster_count(evidence_ids: List[str], evidence: Dict[str, Evidence], now: int) -> int:
    return len({evidence[eid].cluster for eid in evidence_ids if current_support(evidence[eid], now)})


def claim_status(
    claim: Claim,
    evidence: Dict[str, Evidence],
    now: int,
    required_clusters: int = 1,
) -> str:
    deps = [evidence[eid] for eid in claim.dependencies]
    if any(e.revoked for e in deps):
        return "REVALIDATION_REQUIRED"
    if any(not e.drift_ok for e in deps):
        return "EXPIRED"
    if any(now > e.review_horizon for e in deps):
        return "EXPIRED"
    if any(e.scope < claim.scope for e in deps):
        return "ABSTAIN"
    if independent_cluster_count(list(claim.dependencies), evidence, now) < required_clusters:
        return "ABSTAIN"
    return "SUPPORTED_FOR_NOW"


def revocation_descendants(revoked_id: str, claims: Dict[str, Claim]) -> Set[str]:
    impacted: Set[str] = set()
    frontier = {revoked_id}
    while frontier:
        item = frontier.pop()
        for cid, claim in claims.items():
            if cid in impacted:
                continue
            if item in claim.dependencies:
                impacted.add(cid)
                frontier.add(cid)
    return impacted


def challenge_priority(
    scope: int,
    impact: int,
    irreversibility: int,
    novelty: int,
    uncertainty: int,
    centrality: int,
    evidence_age: int,
    evaluator_correlation: int,
) -> int:
    coords = (
        scope,
        impact,
        irreversibility,
        novelty,
        uncertainty,
        centrality,
        evidence_age,
        evaluator_correlation,
    )
    assert all(x >= 0 for x in coords)
    return sum(coords)


def assert_monotone_priority() -> None:
    base = challenge_priority(1, 1, 1, 1, 1, 1, 1, 1)
    for i in range(8):
        coords = [1] * 8
        coords[i] += 1
        assert challenge_priority(*coords) >= base


def main() -> None:
    now = 10
    evidence = {
        "e_local": Evidence("e_local", scope=1, cluster="A", review_horizon=20),
        "e_broad_a": Evidence("e_broad_a", scope=3, cluster="A", review_horizon=20),
        "e_broad_b": Evidence("e_broad_b", scope=3, cluster="B", review_horizon=20),
        "e_expired": Evidence("e_expired", scope=3, cluster="C", review_horizon=5),
        "e_revoked": Evidence("e_revoked", scope=3, cluster="D", review_horizon=20, revoked=True),
        "e_drift": Evidence("e_drift", scope=3, cluster="E", review_horizon=20, drift_ok=False),
    }

    claims = {
        "local": Claim("local", scope=1, dependencies=("e_local",)),
        "worldish": Claim("worldish", scope=3, dependencies=("e_broad_a", "e_broad_b"), high_impact=True),
        "overclaim": Claim("overclaim", scope=3, dependencies=("e_local",), high_impact=True),
        "expired": Claim("expired", scope=3, dependencies=("e_expired",)),
        "revoked": Claim("revoked", scope=3, dependencies=("e_revoked",)),
        "drift": Claim("drift", scope=3, dependencies=("e_drift",)),
        "dependent": Claim("dependent", scope=3, dependencies=("revoked",)),
    }

    # Scope-safe generalization.
    assert claim_status(claims["local"], evidence, now) == "SUPPORTED_FOR_NOW"
    assert claim_status(claims["overclaim"], evidence, now) == "ABSTAIN"

    # Diversity-weighted quorum for broad claims.
    assert claim_status(claims["worldish"], evidence, now, required_clusters=2) == "SUPPORTED_FOR_NOW"
    assert claim_status(
        Claim("correlated", scope=3, dependencies=("e_broad_a",)),
        evidence,
        now,
        required_clusters=2,
    ) == "ABSTAIN"

    # Temporal and drift expiry.
    assert claim_status(claims["expired"], evidence, now) == "EXPIRED"
    assert claim_status(claims["drift"], evidence, now) == "EXPIRED"

    # Revocation forces revalidation rather than preserving old support.
    assert claim_status(claims["revoked"], evidence, now) == "REVALIDATION_REQUIRED"

    # Propagation can traverse claim dependencies as graph nodes.
    impacted = revocation_descendants("e_revoked", claims)
    assert "revoked" in impacted
    assert "dependent" in impacted

    # Stronger claims/risk coordinates cannot get lower challenge priority.
    assert_monotone_priority()

    # Current external gate snapshot remains open by construction.
    gates = {f"G{i}": False for i in range(3, 14)}
    assert all(value is False for value in gates.values())

    world_best = False
    world_unique = False
    invincible = False
    canonical_promotion = False
    assert not any((world_best, world_unique, invincible, canonical_promotion))

    print("Evidence topology & revalidation sanity: PASS")
    print("External gates G3-G13: OPEN")
    print("World-best/world-unique/invincible/canonical promotion: UNVERIFIED")


if __name__ == "__main__":
    main()
