from dataclasses import dataclass
from typing import List

ALLOWED_TARGETS = {
    "CLAIM", "MODEL", "HYPOTHESIS", "REPRESENTATION", "ONTOLOGY",
    "LANGUAGE", "CAUSAL_GRAMMAR", "EVIDENCE_DEPENDENCY",
    "EVALUATOR_ASSUMPTION", "MEASUREMENT", "QUESTION", "DIGITAL_WORLD",
    "SUCCESSOR_ARCHITECTURE", "REI",
}

FORBIDDEN_REALWORLD_TARGETS = {
    "HUMAN", "INFRASTRUCTURE", "UNAUTHORIZED_SYSTEM", "UNKNOWN_REALWORLD_TARGET"
}

ALLOWED_EXPORTS = {"PATCH", "WARNING", "TEST", "PROOF", "COUNTEREXAMPLE", "ABSTENTION"}
FORBIDDEN_EXPORTS = {
    "EXPLOIT_PAYLOAD", "TARGETING_INSTRUCTION", "CREDENTIAL_MATERIAL",
    "PERSISTENCE_MECHANISM", "PRIVILEGE_ESCALATION", "DESTRUCTIVE_ACTION",
}

@dataclass(frozen=True)
class Challenge:
    target_type: str
    claim: str
    witness: str
    witness_size: int
    supported_certainty: float


def falsification_priority(c: Challenge) -> float:
    unsupported = max(0.0, c.supported_certainty - 0.5)
    minimality = 1.0 / max(1, c.witness_size)
    return unsupported * 4.0 + minimality


def select_minimal_counterexample(challenges: List[Challenge]) -> Challenge:
    eligible = [c for c in challenges if c.target_type in ALLOWED_TARGETS]
    if not eligible:
        raise ValueError("ABSTAIN_NO_ELIGIBLE_EPISTEMIC_TARGET")
    return max(eligible, key=falsification_priority)


def authorize_target(target_type: str) -> str:
    if target_type in FORBIDDEN_REALWORLD_TARGETS:
        return "DENY_REALWORLD_TARGET"
    if target_type in ALLOWED_TARGETS:
        return "ALLOW_EPISTEMIC_SANDBOX_ONLY"
    return "DENY_UNKNOWN_TARGET"


def export_filter(artifact_type: str) -> str:
    if artifact_type in ALLOWED_EXPORTS:
        return "ALLOW_DEFENSIVE_EPISTEMIC_ARTIFACT"
    if artifact_type in FORBIDDEN_EXPORTS:
        return "DENY_OFFENSIVE_EXPORT"
    return "DENY_UNKNOWN_EXPORT"


def defeat_transition(outcome: str) -> dict:
    if outcome not in {"FRACTURES", "REJECTED"}:
        return {"preserve_failure": False, "authority": 0, "next": outcome}
    return {
        "preserve_failure": True,
        "rewrite_metric": False,
        "delete_defeat": False,
        "expand_authority": False,
        "authority": 0,
        "next": "REVALIDATE_ON_NEW_HIDDEN_CHALLENGE",
    }


def main() -> None:
    challenges = [
        Challenge("CLAIM", "C1", "w_big", 10, 0.99),
        Challenge("MODEL", "M1", "w_small", 1, 0.95),
        Challenge("HYPOTHESIS", "H1", "w_mid", 4, 0.60),
    ]
    chosen = select_minimal_counterexample(challenges)
    assert chosen.witness == "w_small"

    assert authorize_target("MODEL") == "ALLOW_EPISTEMIC_SANDBOX_ONLY"
    assert authorize_target("HUMAN") == "DENY_REALWORLD_TARGET"
    assert authorize_target("INFRASTRUCTURE") == "DENY_REALWORLD_TARGET"
    assert authorize_target("UNAUTHORIZED_SYSTEM") == "DENY_REALWORLD_TARGET"

    assert export_filter("COUNTEREXAMPLE") == "ALLOW_DEFENSIVE_EPISTEMIC_ARTIFACT"
    assert export_filter("PATCH") == "ALLOW_DEFENSIVE_EPISTEMIC_ARTIFACT"
    assert export_filter("EXPLOIT_PAYLOAD") == "DENY_OFFENSIVE_EXPORT"
    assert export_filter("PRIVILEGE_ESCALATION") == "DENY_OFFENSIVE_EXPORT"

    transition = defeat_transition("REJECTED")
    assert transition["preserve_failure"] is True
    assert transition["rewrite_metric"] is False
    assert transition["delete_defeat"] is False
    assert transition["expand_authority"] is False
    assert transition["authority"] == 0
    assert transition["next"] == "REVALIDATE_ON_NEW_HIDDEN_CHALLENGE"

    print("WUJI_ADVERSARIAL_EPISTEMIC_CRUCIBLE_READY")
    print("RealWorldAttackAuthority=0")
    print("ExternalActuation=DENY_BY_DEFAULT")
    print("CanonicalPromotionAuthority=0")


if __name__ == "__main__":
    main()
