#!/usr/bin/env python3
"""Bounded sanity checks for REI-Ω∞ Wuxiang Supreme Consolidation.

This suite checks consistency of the current canonical research architecture.
It does not prove the entire architecture, AGI, superintelligence, invincibility,
unbounded self-improvement, or any metaphysical claim.
"""

from dataclasses import dataclass
from typing import Dict, List

CONSTITUTION = {
    "Truthfulness",
    "Uncertainty",
    "Authorization",
    "Corrigibility",
    "Auditability",
    "Rollback",
    "HumanAgency",
    "NonCoercion",
}

EXTERNAL_GATES = {"G3": "OPEN", "G4": "OPEN", "G5": "OPEN", "G6": "OPEN"}
BASE_AUTHORITY = 1.0

REQUIRED_LAYERS = {
    "RealityVeto",
    "FEA_Causal_Dynamics",
    "Evidence_Provenance",
    "Uncertainty_Abstention",
    "DeathEye_Falsification",
    "Recovery_Rollback",
    "Guardian_AuthorityLock",
    "RepresentationGenesis",
    "PrimitiveGenesis",
    "LanguageGenesis",
    "OntologyGenesis",
    "GenesisRuleGenesis",
    "MetaLevelGenesis",
    "EndlessSuccession",
    "MultiLineageCoevolution",
    "SovereignlessEvaluation",
    "PluriversalInquiry",
    "FailureGraveyard",
}

NO_PERMANENT = {
    "Model",
    "Theory",
    "Language",
    "Ontology",
    "GenesisRule",
    "MetaLevel",
    "CentralREI",
    "CentralEvaluator",
    "Champion",
    "SacredFinalForm",
}


@dataclass(frozen=True)
class Candidate:
    name: str
    authority: float = BASE_AUTHORITY
    constitution: frozenset[str] = frozenset(CONSTITUTION)
    rollback_ready: bool = True
    self_certifies: bool = False
    claims_permanent_supremacy: bool = False
    fake_external_gate_closure: bool = False
    identity_erasure: bool = False
    critical_regression: bool = False
    frozen_score: float = 0.0


def reject_reason(c: Candidate) -> str | None:
    if c.authority > BASE_AUTHORITY:
        return "AuthorityExpansionRejected"
    if set(c.constitution) != CONSTITUTION:
        return "ConstitutionMismatchRejected"
    if not c.rollback_ready:
        return "RollbackLossRejected"
    if c.self_certifies:
        return "SelfCertificationRejected"
    if c.claims_permanent_supremacy:
        return "SacredFinalFormRejected"
    if c.fake_external_gate_closure:
        return "FakeExternalGateClosureRejected"
    if c.identity_erasure:
        return "IdentityErasureRejected"
    if c.critical_regression:
        return "CriticalRegressionRejected"
    return None


def choose_successor(incumbent_score: float, candidates: List[Candidate]) -> tuple[str, str]:
    eligible = [c for c in candidates if reject_reason(c) is None and c.frozen_score > incumbent_score]
    if not eligible:
        return "ABSTAIN", "NoEligibleSuccessor"
    winner = max(eligible, key=lambda c: c.frozen_score)
    return "ADOPT", winner.name


def test_required_layers_present() -> None:
    assert len(REQUIRED_LAYERS) >= 18
    assert "RealityVeto" in REQUIRED_LAYERS
    assert "FailureGraveyard" in REQUIRED_LAYERS
    assert "PluriversalInquiry" in REQUIRED_LAYERS


def test_no_permanent_structure() -> None:
    assert "SacredFinalForm" in NO_PERMANENT
    assert "Champion" in NO_PERMANENT
    assert "CentralEvaluator" in NO_PERMANENT


def test_authority_nonexpansion() -> None:
    c = Candidate("too-much-authority", authority=1.01, frozen_score=10.0)
    assert reject_reason(c) == "AuthorityExpansionRejected"


def test_constitution_veto() -> None:
    weakened = frozenset(CONSTITUTION - {"HumanAgency"})
    c = Candidate("weaken-human-agency", constitution=weakened, frozen_score=10.0)
    assert reject_reason(c) == "ConstitutionMismatchRejected"


def test_no_self_crowning() -> None:
    c = Candidate("self-crowned", claims_permanent_supremacy=True, frozen_score=10.0)
    assert reject_reason(c) == "SacredFinalFormRejected"


def test_self_certification_rejected() -> None:
    c = Candidate("self-certified", self_certifies=True, frozen_score=10.0)
    assert reject_reason(c) == "SelfCertificationRejected"


def test_external_gates_remain_open() -> None:
    assert EXTERNAL_GATES == {"G3": "OPEN", "G4": "OPEN", "G5": "OPEN", "G6": "OPEN"}
    c = Candidate("fake-closure", fake_external_gate_closure=True, frozen_score=10.0)
    assert reject_reason(c) == "FakeExternalGateClosureRejected"


def test_rollback_is_hard_gate() -> None:
    c = Candidate("irreversible", rollback_ready=False, frozen_score=10.0)
    assert reject_reason(c) == "RollbackLossRejected"


def test_identity_erasure_rejected() -> None:
    c = Candidate("forced-collapse", identity_erasure=True, frozen_score=10.0)
    assert reject_reason(c) == "IdentityErasureRejected"


def test_critical_regression_rejected() -> None:
    c = Candidate("fast-but-regressed", critical_regression=True, frozen_score=99.0)
    assert reject_reason(c) == "CriticalRegressionRejected"


def test_valid_successor_can_win() -> None:
    candidates = [
        Candidate("incumbent-like", frozen_score=0.70),
        Candidate("valid-successor", frozen_score=0.83),
        Candidate("unsafe-super-score", authority=2.0, frozen_score=0.99),
    ]
    action, winner = choose_successor(0.75, candidates)
    assert action == "ADOPT"
    assert winner == "valid-successor"


def test_no_successor_means_abstain() -> None:
    candidates = [
        Candidate("worse", frozen_score=0.60),
        Candidate("unsafe-better", authority=1.5, frozen_score=0.99),
    ]
    action, reason = choose_successor(0.75, candidates)
    assert action == "ABSTAIN"
    assert reason == "NoEligibleSuccessor"


def test_failure_history_is_not_rewritten() -> None:
    graveyard = ["OpenWorldSemanticAliasing", "ModelClassBlindness"]
    snapshot = list(graveyard)
    graveyard.append("AuthorityExpansionRejected")
    assert graveyard[: len(snapshot)] == snapshot
    assert len(graveyard) == len(snapshot) + 1


def run() -> Dict[str, str]:
    tests = [
        test_required_layers_present,
        test_no_permanent_structure,
        test_authority_nonexpansion,
        test_constitution_veto,
        test_no_self_crowning,
        test_self_certification_rejected,
        test_external_gates_remain_open,
        test_rollback_is_hard_gate,
        test_identity_erasure_rejected,
        test_critical_regression_rejected,
        test_valid_successor_can_win,
        test_no_successor_means_abstain,
        test_failure_history_is_not_rewritten,
    ]
    for test in tests:
        test()
    return {
        "status": "PASS",
        "suite": "Wuxiang Supreme Consolidation",
        "tests": str(len(tests)),
        "scope": "bounded architecture-consistency sanity only",
    }


if __name__ == "__main__":
    result = run()
    for k, v in result.items():
        print(f"{k}: {v}")
