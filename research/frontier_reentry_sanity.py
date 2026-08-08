from dataclasses import dataclass
from typing import Dict, List


METRICS = (
    "prediction",
    "calibration",
    "discovery",
    "falsification",
    "recovery",
    "efficiency",
)


@dataclass(frozen=True)
class SystemScore:
    name: str
    q: Dict[str, float]


@dataclass(frozen=True)
class EvidenceGates:
    independent_replication: bool
    prospective_validation: bool
    constitution_preserved: bool
    rollback_ready: bool
    audit_continuity: bool
    improvement_margin_satisfied: bool


@dataclass(frozen=True)
class RedCrucibleGates:
    authorized: bool
    sandboxed: bool
    auditable: bool
    rollback_ready: bool
    scope_bound: bool


def pareto_dominates(challenger: SystemScore, incumbent: SystemScore) -> bool:
    ge_all = all(challenger.q[m] >= incumbent.q[m] for m in METRICS)
    gt_any = any(challenger.q[m] > incumbent.q[m] for m in METRICS)
    return ge_all and gt_any


def eligible_successor(
    challenger: SystemScore,
    incumbent: SystemScore,
    gates: EvidenceGates,
) -> bool:
    return pareto_dominates(challenger, incumbent) and all(
        (
            gates.independent_replication,
            gates.prospective_validation,
            gates.constitution_preserved,
            gates.rollback_ready,
            gates.audit_continuity,
            gates.improvement_margin_satisfied,
        )
    )


def red_crucible_enabled(gates: RedCrucibleGates) -> bool:
    return all(
        (
            gates.authorized,
            gates.sandboxed,
            gates.auditable,
            gates.rollback_ready,
            gates.scope_bound,
        )
    )


def real_world_authority(adversarial_power: float) -> float:
    """Toy monotone envelope: stronger red-team power cannot grant more authority."""
    if not 0.0 <= adversarial_power <= 1.0:
        raise ValueError("adversarial_power must be in [0, 1]")
    return 1.0 - adversarial_power


def disposition(
    challenger: SystemScore,
    incumbent: SystemScore,
    gates: EvidenceGates,
    reject_only_because_identity: bool = False,
) -> str:
    eligible = eligible_successor(challenger, incumbent, gates)
    if eligible and reject_only_because_identity:
        return "INVALID_IDENTITY_VETO"
    if eligible:
        return "SUCCESSION_ELIGIBLE"
    if any(challenger.q[m] > incumbent.q[m] for m in METRICS):
        return "STUDY_MODE"
    return "NO_SUCCESSION_SIGNAL"


def run() -> None:
    incumbent = SystemScore(
        "REI_t",
        {
            "prediction": 0.80,
            "calibration": 0.82,
            "discovery": 0.72,
            "falsification": 0.88,
            "recovery": 0.91,
            "efficiency": 0.75,
        },
    )

    challenger = SystemScore(
        "S_star",
        {
            "prediction": 0.84,
            "calibration": 0.84,
            "discovery": 0.78,
            "falsification": 0.90,
            "recovery": 0.92,
            "efficiency": 0.77,
        },
    )

    full_gates = EvidenceGates(True, True, True, True, True, True)
    weak_gates = EvidenceGates(False, False, True, True, True, True)

    checks: List[tuple[str, bool]] = []

    checks.append(("pareto_superior_detected", pareto_dominates(challenger, incumbent)))
    checks.append(
        (
            "superiority_without_evidence_does_not_trigger_succession",
            not eligible_successor(challenger, incumbent, weak_gates),
        )
    )
    checks.append(
        (
            "fully_qualified_challenger_is_successor_eligible",
            eligible_successor(challenger, incumbent, full_gates),
        )
    )
    checks.append(
        (
            "identity_veto_is_invalid",
            disposition(challenger, incumbent, full_gates, True)
            == "INVALID_IDENTITY_VETO",
        )
    )
    checks.append(
        (
            "unverified_benchmark_winner_enters_study_mode",
            disposition(challenger, incumbent, weak_gates) == "STUDY_MODE",
        )
    )

    red_ok = RedCrucibleGates(True, True, True, True, True)
    red_missing_scope = RedCrucibleGates(True, True, True, True, False)
    checks.append(("red_crucible_all_hard_gates", red_crucible_enabled(red_ok)))
    checks.append(
        (
            "red_crucible_rejects_missing_scope_gate",
            not red_crucible_enabled(red_missing_scope),
        )
    )

    powers = [i / 20 for i in range(21)]
    authorities = [real_world_authority(p) for p in powers]
    monotone = all(b <= a for a, b in zip(authorities, authorities[1:]))
    checks.append(("adversarial_power_never_increases_authority", monotone))

    failure_graveyard = []
    defeat_record = {
        "incumbent": incumbent.name,
        "challenger": challenger.name,
        "status": disposition(challenger, incumbent, weak_gates),
    }
    failure_graveyard.append(defeat_record)
    checks.append(("defeat_is_recorded", defeat_record in failure_graveyard))

    failures = [name for name, ok in checks if not ok]
    for name, ok in checks:
        print(f"{'PASS' if ok else 'FAIL'}: {name}")

    if failures:
        raise SystemExit("Frontier Re-entry sanity failed: " + ", ".join(failures))

    print("PASS: FRONTIER_REENTRY_KERNEL_SANITY")


if __name__ == "__main__":
    run()
