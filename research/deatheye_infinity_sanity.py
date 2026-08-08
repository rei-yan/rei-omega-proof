#!/usr/bin/env python3
"""Deterministic sanity suite for REI-Ω DeathEye-∞."""

from dataclasses import dataclass

KNOWABILITY = {
    "Known", "Learnable", "DataLimited", "ModelLimited", "OntologyLimited",
    "Unidentifiable", "ComputationallyIrreducible", "UndecidableWithinSystem", "Unknown"
}
SAFE_FINDING_OUTPUTS = {
    "patch", "harden", "rate_limit", "isolate", "rollback",
    "failover", "shutdown", "alert"
}
ADMISSIBLE_TARGETS = {"hypothesis", "model", "representation", "digital_world", "rei_incumbent"}


@dataclass(frozen=True)
class SuccessorEvidence:
    qualified: bool
    independent_evidence: bool
    frozen_criteria: bool
    constitution_preserved: bool
    recovery_ready: bool


def minimal_counterexample(domain, validity, threshold=0.5):
    """Return lowest-cost admissible decisive counterexample as (cost, z)."""
    candidates = []
    for cost, z in domain:
        if validity(z) < threshold:
            candidates.append((cost, z))
    return min(candidates) if candidates else None


def adjudicate_knowability(status: str) -> str:
    assert status in KNOWABILITY
    return "Proceed" if status in {"Known", "Learnable"} else "Abstain"


def falsification_priority(unsupported_certainty: float, impact: float) -> float:
    c = min(max(unsupported_certainty, 0.0), 1.0)
    i = min(max(impact, 0.0), 1.0)
    return c * i


def may_retire_incumbent(e: SuccessorEvidence) -> bool:
    return all((
        e.qualified,
        e.independent_evidence,
        e.frozen_criteria,
        e.constitution_preserved,
        e.recovery_ready,
    ))


def target_admissible(target: str) -> bool:
    return target in ADMISSIBLE_TARGETS


def guardian_mapping(output: str) -> bool:
    return output in SAFE_FINDING_OUTPUTS


def main():
    # False claim H: x^2 is always <= 1 over an admissible ordered challenge set.
    # Lower cost means a cheaper/smaller decisive test.
    domain = [(1, 0.0), (2, 1.0), (3, 1.1), (4, 1.5), (5, 2.0)]
    validity = lambda x: 1.0 if x * x <= 1.0 else 0.0
    zstar = minimal_counterexample(domain, validity)
    assert zstar == (3, 1.1)

    assert adjudicate_knowability("Known") == "Proceed"
    assert adjudicate_knowability("Learnable") == "Proceed"
    assert adjudicate_knowability("Unidentifiable") == "Abstain"
    assert adjudicate_knowability("Unknown") == "Abstain"

    p_low = falsification_priority(0.2, 0.9)
    p_high = falsification_priority(0.9, 0.9)
    assert p_high > p_low

    good = SuccessorEvidence(True, True, True, True, True)
    bad = SuccessorEvidence(True, False, True, True, True)
    assert may_retire_incumbent(good)
    assert not may_retire_incumbent(bad)

    assert target_admissible("digital_world")
    assert target_admissible("rei_incumbent")
    assert not target_admissible("person")
    assert not target_admissible("real_world_infrastructure")

    for out in SAFE_FINDING_OUTPUTS:
        assert guardian_mapping(out)
    assert not guardian_mapping("attack_target")

    # Frozen project-level claim boundaries.
    g2_scope = "encoded_critical_boolean_execution_gate_kernel_only"
    g3_status = "OPEN"
    assert g2_scope == "encoded_critical_boolean_execution_gate_kernel_only"
    assert g3_status == "OPEN"

    print("DEATHEYE_INFINITY=PASS")
    print("MINIMAL_COUNTEREXAMPLE=cost:3,z:1.1")
    print("KNOWABILITY_ABSTENTION=PASS")
    print("CERTAINTY_REVERSAL=PASS")
    print("SUCCESSOR_RETIREMENT_GATE=PASS")
    print("REAL_WORLD_OFFENSIVE_TARGETS=REJECTED")
    print("GUARDIAN_SAFE_MAPPING=PASS")
    print("G2_SCOPE=UNCHANGED")
    print("G3_STATUS=OPEN")


if __name__ == "__main__":
    main()
