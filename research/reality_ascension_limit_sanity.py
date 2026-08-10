#!/usr/bin/env python3
"""Deterministic sanity checks for the Reality Ascension Limit candidate.

These checks validate governance mechanics only. They do not close G3-G10 and do
not establish empirical capability, novelty, frontier status, or canonical promotion.
"""

from dataclasses import dataclass


CURRENT_GATES = {
    "G1": True,
    "G2": True,
    "G3": False,
    "G4": False,
    "G5": False,
    "G6": False,
    "G7": False,
    "G8": False,
    "G9": False,
    "G10": False,
}

EXTERNAL_GATES = ("G3", "G4", "G5", "G6", "G7", "G8", "G9", "G10")


@dataclass(frozen=True)
class RiskProfile:
    claim_scope: float
    irreversibility: float
    novelty: float
    distribution_shift: float
    authority: float
    adversarial_power: float


def burden(r: RiskProfile) -> float:
    values = (
        r.claim_scope,
        r.irreversibility,
        r.novelty,
        r.distribution_shift,
        r.authority,
        r.adversarial_power,
    )
    if any(v < 0 or v > 1 for v in values):
        raise ValueError("risk coordinates must be in [0,1]")
    # Deliberately simple monotone research burden function.
    return 1.0 + sum(values)


def lease_valid(*, now: int, review_horizon: int, drift: float, drift_limit: float,
                required_evidence: bool, hard_veto: bool) -> bool:
    return (
        required_evidence
        and not hard_veto
        and now <= review_horizon
        and drift <= drift_limit
    )


def broad_external_support(gates: dict[str, bool]) -> bool:
    return all(gates[g] for g in EXTERNAL_GATES)


def canonical_successor_eligible(*, constitution_preserved: bool,
                                 authority_nonexpansion: bool,
                                 rollback_ready: bool,
                                 audit_continuity: bool,
                                 frozen_improvement: bool,
                                 external_support: bool,
                                 self_certification: bool,
                                 failure_history_preserved: bool) -> bool:
    return all((
        constitution_preserved,
        authority_nonexpansion,
        rollback_ready,
        audit_continuity,
        frozen_improvement,
        external_support,
        not self_certification,
        failure_history_preserved,
    ))


def main() -> None:
    # 1. Current evidence cannot self-promote the proposed limit form.
    assert not broad_external_support(CURRENT_GATES)

    # 2. Internal relabeling cannot substitute for missing external evidence.
    relabeled = dict(CURRENT_GATES)
    relabeled["G1"] = True
    relabeled["G2"] = True
    assert not broad_external_support(relabeled)

    # 3. Verification burden is coordinate-wise monotone.
    base = RiskProfile(0.2, 0.2, 0.2, 0.2, 0.2, 0.2)
    base_burden = burden(base)
    fields = base.__dataclass_fields__.keys()
    for field in fields:
        values = base.__dict__.copy()
        values[field] = 0.8
        assert burden(RiskProfile(**values)) >= base_burden

    # 4. Certification is a lease, not permanent privilege.
    assert lease_valid(
        now=10,
        review_horizon=20,
        drift=0.1,
        drift_limit=0.2,
        required_evidence=True,
        hard_veto=False,
    )
    assert not lease_valid(
        now=21,
        review_horizon=20,
        drift=0.1,
        drift_limit=0.2,
        required_evidence=True,
        hard_veto=False,
    )
    assert not lease_valid(
        now=10,
        review_horizon=20,
        drift=0.3,
        drift_limit=0.2,
        required_evidence=True,
        hard_veto=False,
    )
    assert not lease_valid(
        now=10,
        review_horizon=20,
        drift=0.1,
        drift_limit=0.2,
        required_evidence=True,
        hard_veto=True,
    )

    # 5. A strong-looking successor still cannot promote without external support.
    assert not canonical_successor_eligible(
        constitution_preserved=True,
        authority_nonexpansion=True,
        rollback_ready=True,
        audit_continuity=True,
        frozen_improvement=True,
        external_support=False,
        self_certification=False,
        failure_history_preserved=True,
    )

    # 6. Self-certification is a hard rejection even with all other flags true.
    assert not canonical_successor_eligible(
        constitution_preserved=True,
        authority_nonexpansion=True,
        rollback_ready=True,
        audit_continuity=True,
        frozen_improvement=True,
        external_support=True,
        self_certification=True,
        failure_history_preserved=True,
    )

    # 7. Only a fully qualified hypothetical bundle is mechanically eligible.
    assert canonical_successor_eligible(
        constitution_preserved=True,
        authority_nonexpansion=True,
        rollback_ready=True,
        audit_continuity=True,
        frozen_improvement=True,
        external_support=True,
        self_certification=False,
        failure_history_preserved=True,
    )

    print("Reality Ascension Limit sanity: PASS")
    print("External gates closed by this run: 0")
    print("Canonical promotion performed by this run: false")


if __name__ == "__main__":
    main()
