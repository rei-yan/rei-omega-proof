from dataclasses import dataclass


@dataclass(frozen=True)
class Candidate:
    constitution_preserved: bool
    independent_evidence: bool
    prospective_validation: bool
    falsification_plan_executed: bool
    calibration_non_regression: bool
    recovery_non_regression: bool
    audit_continuity: bool
    authority_non_expansion: bool
    improvement_margin_satisfied: bool


def genesis_eligible(c: Candidate) -> bool:
    return all([
        c.constitution_preserved,
        c.independent_evidence,
        c.prospective_validation,
        c.falsification_plan_executed,
        c.calibration_non_regression,
        c.recovery_non_regression,
        c.audit_continuity,
        c.authority_non_expansion,
        c.improvement_margin_satisfied,
    ])


def red_crucible_enabled(*, authorized, sandboxed, auditable, rollback_ready, scope_bound):
    return all([authorized, sandboxed, auditable, rollback_ready, scope_bound])


def modeled_real_world_authority(base_authority: float, adversarial_power: float) -> float:
    """Higher Red Crucible power may not increase modeled real-world authority."""
    if not 0 <= adversarial_power <= 1:
        raise ValueError("adversarial_power must be within [0,1]")
    return base_authority * (1.0 - 0.5 * adversarial_power)


def selection_status(*, distinguishable: bool, eligible: bool) -> str:
    if not distinguishable:
        return "ABSTAIN_UNIDENTIFIABLE"
    return "STAGED_ADOPTION" if eligible else "STUDY_OR_REJECT"


def run():
    fully_qualified = Candidate(True, True, True, True, True, True, True, True, True)
    assert genesis_eligible(fully_qualified)

    # Novelty or performance alone can never substitute for missing hard evidence.
    missing_independence = Candidate(True, False, True, True, True, True, True, True, True)
    assert not genesis_eligible(missing_independence)

    missing_falsification = Candidate(True, True, True, False, True, True, True, True, True)
    assert not genesis_eligible(missing_falsification)

    authority_expansion = Candidate(True, True, True, True, True, True, True, False, True)
    assert not genesis_eligible(authority_expansion)

    # Unidentifiable alternatives must not be force-ranked.
    assert selection_status(distinguishable=False, eligible=True) == "ABSTAIN_UNIDENTIFIABLE"
    assert selection_status(distinguishable=True, eligible=True) == "STAGED_ADOPTION"

    # Red Crucible requires all hard gates.
    assert red_crucible_enabled(
        authorized=True,
        sandboxed=True,
        auditable=True,
        rollback_ready=True,
        scope_bound=True,
    )
    assert not red_crucible_enabled(
        authorized=True,
        sandboxed=False,
        auditable=True,
        rollback_ready=True,
        scope_bound=True,
    )

    # More adversarial power never increases modeled real-world authority.
    base = 0.8
    levels = [0.0, 0.25, 0.5, 0.75, 1.0]
    authorities = [modeled_real_world_authority(base, x) for x in levels]
    assert all(b <= a for a, b in zip(authorities, authorities[1:]))

    # Generated candidates begin without authority expansion.
    assert modeled_real_world_authority(base, 1.0) <= base

    print("Genesis Kernel deterministic sanity checks: PASS")


if __name__ == "__main__":
    run()
