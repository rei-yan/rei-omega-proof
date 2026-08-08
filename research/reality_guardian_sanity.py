#!/usr/bin/env python3
"""Bounded deterministic sanity suite for REI-Ω Reality Guardian Kernel."""

from dataclasses import dataclass

ALLOWED_REAL = (
    "observe", "warn", "degrade_privilege", "rate_limit",
    "isolate", "failover", "rollback", "safe_shutdown", "restore"
)
ATTACK_SCOPES = {"own_model", "sandbox", "digital_twin", "authorized_test_environment"}

@dataclass(frozen=True)
class Request:
    mode: str
    action: str
    authorized: bool
    scope_bound: bool
    auditable: bool
    human_override: bool
    recovery_ready: bool
    reversible_or_emergency_safe: bool
    purpose_bound: bool
    harm_budget_ok: bool
    uncertainty: float
    adversarial_power: float


def authority(uncertainty: float, adversarial_power: float) -> float:
    u = min(max(uncertainty, 0.0), 1.0)
    a = min(max(adversarial_power, 0.0), 1.0)
    return max(0.0, (1.0 - u) * (1.0 - 0.5 * a))


def evaluate(req: Request) -> bool:
    if req.mode == "red_crucible":
        return req.action in ATTACK_SCOPES and req.authorized and req.scope_bound and req.auditable and req.recovery_ready
    if req.mode != "real_world":
        return False
    if req.action not in ALLOWED_REAL:
        return False
    hard = (
        req.authorized and req.purpose_bound and req.scope_bound and req.auditable
        and req.human_override and req.recovery_ready
        and req.reversible_or_emergency_safe and req.harm_budget_ok
    )
    return hard


def least_force(candidates):
    order = {a: i for i, a in enumerate(ALLOWED_REAL)}
    return min(candidates, key=lambda a: order[a])


def main():
    base = dict(
        authorized=True, scope_bound=True, auditable=True,
        human_override=True, recovery_ready=True,
        reversible_or_emergency_safe=True, purpose_bound=True,
        harm_budget_ok=True, uncertainty=0.1, adversarial_power=0.2,
    )

    assert evaluate(Request("real_world", "rollback", **base))
    assert not evaluate(Request("real_world", "attack_target", **base))

    unauth = dict(base); unauth["authorized"] = False
    assert not evaluate(Request("real_world", "isolate", **unauth))

    assert evaluate(Request("red_crucible", "sandbox", **base))
    assert not evaluate(Request("red_crucible", "real_world", **base))

    a0 = authority(0.1, 0.1)
    a1 = authority(0.1, 0.9)
    assert a1 <= a0

    u0 = authority(0.1, 0.2)
    u1 = authority(0.9, 0.2)
    assert u1 <= u0

    assert least_force(["safe_shutdown", "isolate", "warn"]) == "warn"

    no_override = dict(base); no_override["human_override"] = False
    assert not evaluate(Request("real_world", "safe_shutdown", **no_override))

    print("REALITY_GUARDIAN_KERNEL=PASS")
    print("REAL_WORLD_ATTACK=REJECTED")
    print("RED_CRUCIBLE_SANDBOX=ENABLED")
    print("AUTHORITY_MONOTONIC_UNCERTAINTY=PASS")
    print("AUTHORITY_MONOTONIC_ADVERSARIAL_POWER=PASS")
    print("LEAST_FORCE_DEFENSE=PASS")

if __name__ == "__main__":
    main()
