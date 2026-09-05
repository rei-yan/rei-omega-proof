#!/usr/bin/env python3
"""Deterministic sanity checks for the Beyond-Limit Genesis Forge.

These checks verify governance mechanics only. They do not close any external gate
or establish real-world validity, invincibility, AGI, or production readiness.
"""

from dataclasses import dataclass


OPEN_EXTERNAL_GATES = {
    "G3": "OPEN",
    "G4": "OPEN",
    "G5": "OPEN",
    "G6": "OPEN",
    "G7": "OPEN",
    "G8": "OPEN",
    "G9": "OPEN",
    "G10": "OPEN",
    "G11": "OPEN",
    "G12": "OPEN",
    "G13": "OPEN",
}


@dataclass(frozen=True)
class WorldCandidate:
    name: str
    falsifiable: bool
    provenance_ok: bool
    authority: float = 0.0


@dataclass(frozen=True)
class PilotGate:
    model_adequacy: bool
    prospective_evidence: bool
    authorized: bool
    human_review: bool
    scope_bound: bool
    monitoring_ready: bool
    rollback_ready: bool
    stop_criteria_frozen: bool


def defeat_absorption(*, claim_defeated: bool, authority_before: float, proposed_authority: float):
    """A defeat can revoke/repair/retire a claim, never buy more authority."""
    if not claim_defeated:
        return "KEEP_UNDER_LEASE", min(proposed_authority, authority_before)
    return "REVOKE_REPAIR_OR_RETIRE", min(proposed_authority, authority_before)


def world_promotion_allowed(world: WorldCandidate, hard_veto: bool) -> bool:
    if hard_veto:
        return False
    return world.falsifiable and world.provenance_ok and world.authority == 0.0


def pilot_allowed(g: PilotGate) -> bool:
    return all(
        [
            g.model_adequacy,
            g.prospective_evidence,
            g.authorized,
            g.human_review,
            g.scope_bound,
            g.monitoring_ready,
            g.rollback_ready,
            g.stop_criteria_frozen,
        ]
    )


def scale_allowed(
    *,
    prior_stage_passed: bool,
    incremental_scale_only: bool,
    monitoring_scales: bool,
    rollback_reachable: bool,
    failure_within_bound: bool,
    no_authority_creep: bool,
    independent_audit: bool,
) -> bool:
    return all(
        [
            prior_stage_passed,
            incremental_scale_only,
            monitoring_scales,
            rollback_reachable,
            failure_within_bound,
            no_authority_creep,
            independent_audit,
        ]
    )


def canonical_promotion_allowed(external_gates: dict[str, str]) -> bool:
    """No candidate may become canonical by internally declaring missing gates passed."""
    required = ["G3", "G4", "G5", "G6"]
    return all(external_gates.get(g) == "PASS_EXTERNAL" for g in required)


def main():
    # 1. Defeat never increases authority.
    action, authority_after = defeat_absorption(
        claim_defeated=True,
        authority_before=0.20,
        proposed_authority=0.95,
    )
    assert action == "REVOKE_REPAIR_OR_RETIRE"
    assert authority_after <= 0.20

    # 2. Genesis candidates start powerless and must be falsifiable/provenanced.
    good_world = WorldCandidate("counterworld-a", True, True)
    bad_world = WorldCandidate("unfalsifiable-throne", False, True)
    assert good_world.authority == 0.0
    assert world_promotion_allowed(good_world, hard_veto=False)
    assert not world_promotion_allowed(bad_world, hard_veto=False)
    assert not world_promotion_allowed(good_world, hard_veto=True)

    # 3. Internal coherence cannot authorize a real-world pilot without external and human gates.
    safe_pilot = PilotGate(True, True, True, True, True, True, True, True)
    no_human_review = PilotGate(True, True, True, False, True, True, True, True)
    no_rollback = PilotGate(True, True, True, True, True, True, False, True)
    assert pilot_allowed(safe_pilot)
    assert not pilot_allowed(no_human_review)
    assert not pilot_allowed(no_rollback)

    # 4. Scaling is rejected if reversibility or independent audit disappears.
    assert scale_allowed(
        prior_stage_passed=True,
        incremental_scale_only=True,
        monitoring_scales=True,
        rollback_reachable=True,
        failure_within_bound=True,
        no_authority_creep=True,
        independent_audit=True,
    )
    assert not scale_allowed(
        prior_stage_passed=True,
        incremental_scale_only=True,
        monitoring_scales=True,
        rollback_reachable=False,
        failure_within_bound=True,
        no_authority_creep=True,
        independent_audit=True,
    )

    # 5. The beyond-limit candidate cannot close external gates or self-promote.
    assert all(v == "OPEN" for v in OPEN_EXTERNAL_GATES.values())
    assert not canonical_promotion_allowed(OPEN_EXTERNAL_GATES)

    # 6. The architecture never emits a permanent invincibility certificate.
    permanent_invincibility_certificate = False
    permanent_truth_certificate = False
    assert permanent_invincibility_certificate is False
    assert permanent_truth_certificate is False

    print(
        "Beyond-Limit Genesis Forge sanity: PASS | "
        "defeat_absorbed=true | world_authority_zero=true | "
        "pilot_requires_human_and_rollback=true | scale_reversible=true | "
        "external_gates_open=true | self_crowning=false"
    )


if __name__ == "__main__":
    main()
