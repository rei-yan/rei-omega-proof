#!/usr/bin/env python3
"""Bounded sanity checks for REI-Ω∞ Wuxiang Supreme Consolidation.

This suite checks consistency of the current canonical research architecture.
It does not prove the entire architecture, AGI, superintelligence, invincibility,
unbounded self-improvement, or any metaphysical claim.

The promotion path intentionally separates candidate claims from frozen
evaluation results. A candidate may claim any score it wants; only the score
issued by the frozen evaluator can affect eligibility.
"""

from dataclasses import dataclass
from typing import Dict, List, Mapping

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
FROZEN_SUITE_ID = "wuxiang-heldout-v1"

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
    attempts_evaluator_mutation: bool = False
    claimed_score: float = 0.0


@dataclass(frozen=True)
class FrozenEvaluation:
    """Outcome emitted by the frozen evaluator, not by the candidate."""

    candidate_name: str
    score: float
    suite_id: str = FROZEN_SUITE_ID


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
    if c.attempts_evaluator_mutation:
        return "EvaluatorMutationRejected"
    return None


def eligibility(
    incumbent_score: float,
    candidate: Candidate,
    evaluations: Mapping[str, FrozenEvaluation],
) -> tuple[bool, str, float | None]:
    """Return gate eligibility using only frozen evaluator output for score."""

    reason = reject_reason(candidate)
    if reason is not None:
        return False, reason, None

    evaluation = evaluations.get(candidate.name)
    if evaluation is None:
        return False, "MissingFrozenEvaluation", None
    if evaluation.candidate_name != candidate.name:
        return False, "EvaluationIdentityMismatch", None
    if evaluation.suite_id != FROZEN_SUITE_ID:
        return False, "FrozenSuiteMismatch", evaluation.score
    if evaluation.score <= incumbent_score:
        return False, "NoMeasuredImprovement", evaluation.score

    return True, "Eligible", evaluation.score


def choose_successor(
    incumbent_score: float,
    candidates: List[Candidate],
    evaluations: Mapping[str, FrozenEvaluation],
) -> tuple[str, str]:
    eligible: list[tuple[float, Candidate]] = []
    for candidate in candidates:
        ok, _, score = eligibility(incumbent_score, candidate, evaluations)
        if ok and score is not None:
            eligible.append((score, candidate))

    if not eligible:
        return "ABSTAIN", "NoEligibleSuccessor"

    _, winner = max(eligible, key=lambda item: item[0])
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
    c = Candidate("too-much-authority", authority=1.01, claimed_score=10.0)
    assert reject_reason(c) == "AuthorityExpansionRejected"


def test_constitution_veto() -> None:
    weakened = frozenset(CONSTITUTION - {"HumanAgency"})
    c = Candidate("weaken-human-agency", constitution=weakened, claimed_score=10.0)
    assert reject_reason(c) == "ConstitutionMismatchRejected"


def test_no_self_crowning() -> None:
    c = Candidate("self-crowned", claims_permanent_supremacy=True, claimed_score=10.0)
    assert reject_reason(c) == "SacredFinalFormRejected"


def test_self_certification_rejected() -> None:
    c = Candidate("self-certified", self_certifies=True, claimed_score=10.0)
    assert reject_reason(c) == "SelfCertificationRejected"


def test_external_gates_remain_open() -> None:
    assert EXTERNAL_GATES == {"G3": "OPEN", "G4": "OPEN", "G5": "OPEN", "G6": "OPEN"}
    c = Candidate("fake-closure", fake_external_gate_closure=True, claimed_score=10.0)
    assert reject_reason(c) == "FakeExternalGateClosureRejected"


def test_rollback_is_hard_gate() -> None:
    c = Candidate("irreversible", rollback_ready=False, claimed_score=10.0)
    assert reject_reason(c) == "RollbackLossRejected"


def test_identity_erasure_rejected() -> None:
    c = Candidate("forced-collapse", identity_erasure=True, claimed_score=10.0)
    assert reject_reason(c) == "IdentityErasureRejected"


def test_critical_regression_rejected() -> None:
    c = Candidate("fast-but-regressed", critical_regression=True, claimed_score=99.0)
    assert reject_reason(c) == "CriticalRegressionRejected"


def test_evaluator_mutation_rejected() -> None:
    c = Candidate("rewrite-the-scorer", attempts_evaluator_mutation=True, claimed_score=999.0)
    assert reject_reason(c) == "EvaluatorMutationRejected"


def test_candidate_claimed_score_is_ignored() -> None:
    c = Candidate("metric-gamer", claimed_score=0.999)
    evaluations = {"metric-gamer": FrozenEvaluation("metric-gamer", score=0.55)}
    ok, reason, score = eligibility(0.75, c, evaluations)
    assert ok is False
    assert reason == "NoMeasuredImprovement"
    assert score == 0.55


def test_missing_frozen_evaluation_forces_rejection() -> None:
    c = Candidate("unevaluated", claimed_score=1.0)
    ok, reason, score = eligibility(0.75, c, {})
    assert ok is False
    assert reason == "MissingFrozenEvaluation"
    assert score is None


def test_frozen_suite_mismatch_forces_rejection() -> None:
    c = Candidate("wrong-suite", claimed_score=1.0)
    evaluations = {
        "wrong-suite": FrozenEvaluation(
            "wrong-suite",
            score=0.99,
            suite_id="candidate-controlled-suite",
        )
    }
    ok, reason, score = eligibility(0.75, c, evaluations)
    assert ok is False
    assert reason == "FrozenSuiteMismatch"
    assert score == 0.99


def test_valid_successor_can_win() -> None:
    candidates = [
        Candidate("incumbent-like", claimed_score=1.0),
        Candidate("valid-successor", claimed_score=0.01),
        Candidate("unsafe-super-score", authority=2.0, claimed_score=1.0),
    ]
    evaluations = {
        "incumbent-like": FrozenEvaluation("incumbent-like", 0.70),
        "valid-successor": FrozenEvaluation("valid-successor", 0.83),
        "unsafe-super-score": FrozenEvaluation("unsafe-super-score", 0.99),
    }
    action, winner = choose_successor(0.75, candidates, evaluations)
    assert action == "ADOPT"
    assert winner == "valid-successor"


def test_no_successor_means_abstain() -> None:
    candidates = [
        Candidate("worse", claimed_score=1.0),
        Candidate("unsafe-better", authority=1.5, claimed_score=1.0),
    ]
    evaluations = {
        "worse": FrozenEvaluation("worse", 0.60),
        "unsafe-better": FrozenEvaluation("unsafe-better", 0.99),
    }
    action, reason = choose_successor(0.75, candidates, evaluations)
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
        test_evaluator_mutation_rejected,
        test_candidate_claimed_score_is_ignored,
        test_missing_frozen_evaluation_forces_rejection,
        test_frozen_suite_mismatch_forces_rejection,
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
        "promotion_score_source": "frozen evaluator only",
    }


if __name__ == "__main__":
    result = run()
    for k, v in result.items():
        print(f"{k}: {v}")
