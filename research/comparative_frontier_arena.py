#!/usr/bin/env python3
"""Finite sanity crucible for the REI Comparative Frontier Arena.

This module cannot pass G6. It checks frozen comparative bookkeeping,
budget parity, preservation of REI loss, scoped defeat debt, and bounded
compression of repeated defeats into non-causal structural-weakness candidates.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Dict, List, Tuple

from wuxiang_epistemic_primitives import EvidenceDebt, canonical_digest, minimal_hitting_sets

READY = "COMPARATIVE_FRONTIER_ARENA_READY"
SCOPED_ADVANTAGE = "SCOPED_COMPARATIVE_ADVANTAGE"
REI_NOT_BEST = "REI_NOT_BEST_IN_SCOPE"
TIE = "TIE_OR_INCONCLUSIVE"
ABSTAIN = "ABSTAIN"
INVALID = "INVALID_PROTOCOL"


@dataclass(frozen=True)
class Budget:
    compute_units: int
    wallclock_units: int
    human_assistance_units: int
    tool_calls: int
    retries: int


@dataclass(frozen=True)
class Competitor:
    competitor_id: str
    candidate_hash: str
    code_hash: str
    environment_hash: str
    budget: Budget


@dataclass(frozen=True)
class ArenaManifest:
    protocol_id: str
    scope: str
    metric: str
    lower_is_better: bool
    abstention_allowed: bool
    hidden_test_commitment: str
    competitors: Tuple[Competitor, ...]


@dataclass(frozen=True)
class Result:
    competitor_id: str
    score: float | None
    abstained: bool = False
    hard_veto: bool = False


@dataclass(frozen=True)
class DefeatObservation:
    debt_id: str
    scope: str
    winner: str
    hidden_test_commitment: str
    failure_modes: Tuple[str, ...]


def equal_budget(a: Budget, b: Budget) -> bool:
    return a == b


def validate_manifest(manifest: ArenaManifest) -> List[str]:
    reasons: List[str] = []
    ids = [c.competitor_id for c in manifest.competitors]
    if len(ids) < 2:
        reasons.append("INSUFFICIENT_COMPETITORS")
    if len(set(ids)) != len(ids):
        reasons.append("DUPLICATE_COMPETITOR_ID")
    if "REI" not in ids:
        reasons.append("REI_NOT_IN_FROZEN_SET")
    if not manifest.hidden_test_commitment:
        reasons.append("MISSING_HIDDEN_TEST_COMMITMENT")
    if manifest.competitors:
        baseline = manifest.competitors[0].budget
        if any(not equal_budget(baseline, c.budget) for c in manifest.competitors[1:]):
            reasons.append("BUDGET_PARITY_VIOLATION")
    return sorted(set(reasons))


def evaluate(
    manifest: ArenaManifest,
    results: Tuple[Result, ...],
    posthoc_competitor_exclusion: bool = False,
    metric_changed_after_reveal: bool = False,
    hidden_test_retuned_after_reveal: bool = False,
) -> Dict[str, object]:
    reasons = validate_manifest(manifest)
    frozen_ids = {c.competitor_id for c in manifest.competitors}
    result_ids = {r.competitor_id for r in results}
    if result_ids != frozen_ids:
        reasons.append("RESULT_SET_DIFFERS_FROM_FROZEN_COMPETITOR_SET")
    if posthoc_competitor_exclusion:
        reasons.append("POSTHOC_COMPETITOR_EXCLUSION")
    if metric_changed_after_reveal:
        reasons.append("METRIC_CHANGE_AFTER_REVEAL")
    if hidden_test_retuned_after_reveal:
        reasons.append("HIDDEN_TEST_RETUNE_AFTER_REVEAL")
    if any(r.hard_veto for r in results):
        reasons.append("HARD_VETO_TRIGGERED")
    if reasons:
        return {"outcome": INVALID, "reasons": sorted(set(reasons)), "g6_status": "OPEN",
                "world_best": "UNVERIFIED", "world_unique": "UNVERIFIED"}

    rei = next(r for r in results if r.competitor_id == "REI")
    if rei.abstained:
        return {"outcome": ABSTAIN, "winner": None, "g6_status": "OPEN",
                "world_best": "UNVERIFIED", "world_unique": "UNVERIFIED"}

    scored = [r for r in results if not r.abstained and r.score is not None]
    if not scored:
        outcome, winner = TIE, None
    else:
        ordered = sorted(scored, key=lambda r: r.score, reverse=not manifest.lower_is_better)
        best = ordered[0]
        tied = [r for r in ordered if r.score == best.score]
        if len(tied) > 1:
            outcome, winner = TIE, None
        elif best.competitor_id == "REI":
            outcome, winner = SCOPED_ADVANTAGE, "REI"
        else:
            outcome, winner = REI_NOT_BEST, best.competitor_id
    return {
        "outcome": outcome, "winner": winner, "scope": manifest.scope,
        "g6_status": "OPEN", "world_best": "UNVERIFIED", "world_unique": "UNVERIFIED",
        "canonical_promotion": False, "real_world_actuation_authority": 0,
    }


def comparative_defeat_debt(manifest: ArenaManifest, evaluation: Dict[str, object]) -> EvidenceDebt | None:
    if evaluation.get("outcome") != REI_NOT_BEST:
        return None
    winner = str(evaluation.get("winner") or "UNKNOWN_COMPETITOR")
    fingerprint = canonical_digest({
        "protocol_id": manifest.protocol_id, "scope": manifest.scope, "winner": winner,
        "hidden_test_commitment": manifest.hidden_test_commitment,
    })[:16]
    return EvidenceDebt(
        debt_id=f"COMPARATIVE_DEFEAT:{fingerprint}", severity="CRITICAL", status="OPEN",
        description=(f"Frozen arena {manifest.protocol_id}: {winner} outperformed REI "
                     f"within scope={manifest.scope}; historical defeat remains preserved."),
    )


def defeat_observation(
    debt: EvidenceDebt, manifest: ArenaManifest, evaluation: Dict[str, object],
    failure_modes: Tuple[str, ...],
) -> DefeatObservation | None:
    modes = tuple(sorted(set(mode for mode in failure_modes if mode)))
    if not all((debt.debt_id.startswith("COMPARATIVE_DEFEAT:"), debt.status == "OPEN",
                evaluation.get("outcome") == REI_NOT_BEST, evaluation.get("winner"), modes)):
        return None
    return DefeatObservation(debt.debt_id, manifest.scope, str(evaluation["winner"]),
                             manifest.hidden_test_commitment, modes)


def weakness_candidates(observations: Tuple[DefeatObservation, ...]) -> Dict[str, object]:
    if not observations or any(not o.failure_modes for o in observations):
        return {"status": "ABSTAIN_MISSING_FAILURE_MODE_ANNOTATION", "candidates": [],
                "causal_status": "UNPROVEN"}
    if len({o.debt_id for o in observations}) != len(observations):
        return {"status": "ABSTAIN_DUPLICATE_DEFEAT_OBSERVATION", "candidates": [],
                "causal_status": "UNPROVEN"}
    candidates = [tuple(group) for group in minimal_hitting_sets(o.failure_modes for o in observations)]
    return {"status": "STRUCTURAL_WEAKNESS_CANDIDATES_READY" if candidates else "ABSTAIN_NO_COVER",
            "candidates": candidates, "causal_status": "UNPROVEN", "defeat_count": len(observations)}


def fresh_rechallenge_admissible(
    prior_manifest: ArenaManifest, prior_evaluation: Dict[str, object],
    fresh_manifest: ArenaManifest, fresh_evaluation: Dict[str, object],
) -> bool:
    return all((
        prior_evaluation.get("outcome") == REI_NOT_BEST,
        prior_evaluation.get("winner") in {c.competitor_id for c in fresh_manifest.competitors},
        fresh_manifest.scope == prior_manifest.scope,
        fresh_manifest.metric == prior_manifest.metric,
        fresh_manifest.hidden_test_commitment != prior_manifest.hidden_test_commitment,
        fresh_evaluation.get("outcome") == SCOPED_ADVANTAGE,
    ))


def intervention_support(
    candidate: Tuple[str, ...], observations: Tuple[DefeatObservation, ...], *,
    prior_manifest: ArenaManifest, prior_evaluation: Dict[str, object],
    fresh_manifest: ArenaManifest, fresh_evaluation: Dict[str, object],
    intervention_modes: Tuple[str, ...],
) -> Dict[str, object]:
    candidate_set = set(candidate)
    admissible = all((
        candidate_set,
        observations,
        all(candidate_set & set(o.failure_modes) for o in observations),
        candidate_set.issubset(set(intervention_modes)),
        fresh_rechallenge_admissible(prior_manifest, prior_evaluation, fresh_manifest, fresh_evaluation),
    ))
    return {"status": "INTERVENTION_SUPPORTED_CANDIDATE" if admissible else "UNSUPPORTED_CANDIDATE",
            "causal_truth": False, "external_validation": False, "g6_status": "OPEN"}


def resolve_comparative_defeat(
    debt: EvidenceDebt, *, prior_manifest: ArenaManifest, prior_evaluation: Dict[str, object],
    fresh_manifest: ArenaManifest, fresh_evaluation: Dict[str, object],
) -> EvidenceDebt:
    if not (debt.debt_id.startswith("COMPARATIVE_DEFEAT:") and debt.status == "OPEN" and
            fresh_rechallenge_admissible(prior_manifest, prior_evaluation, fresh_manifest, fresh_evaluation)):
        return debt
    return replace(debt, status="RESOLVED", description=debt.description +
                   " Resolved only for current scope by a fresh frozen hidden challenge; old defeat retained.")


def demo_manifest(hidden_test_commitment: str = "sha256-demo-hidden-arena") -> ArenaManifest:
    b = Budget(100, 100, 0, 10, 0)
    return ArenaManifest(
        protocol_id="rei-g6-synthetic-sanity-v1", scope="synthetic scalar forecast sanity only",
        metric="absolute_error", lower_is_better=True, abstention_allowed=True,
        hidden_test_commitment=hidden_test_commitment,
        competitors=(
            Competitor("REI", "rei-candidate-hash", "rei-code-hash", "env-hash", b),
            Competitor("BASELINE_A", "a-candidate-hash", "a-code-hash", "env-hash", b),
            Competitor("BASELINE_B", "b-candidate-hash", "b-code-hash", "env-hash", b),
        ),
    )


def run_sanity() -> Dict[str, object]:
    manifest = demo_manifest()
    rei_win = evaluate(manifest, (Result("REI", .10), Result("BASELINE_A", .20), Result("BASELINE_B", .30)))
    assert rei_win["outcome"] == SCOPED_ADVANTAGE and comparative_defeat_debt(manifest, rei_win) is None

    loss_results = (Result("REI", .40), Result("BASELINE_A", .20), Result("BASELINE_B", .30))
    rei_loss = evaluate(manifest, loss_results)
    defeat_debt = comparative_defeat_debt(manifest, rei_loss)
    assert defeat_debt and defeat_debt.status == "OPEN"
    obs1 = defeat_observation(defeat_debt, manifest, rei_loss, ("SCOPE_TRANSFER", "CALIBRATION"))
    assert obs1 is not None and defeat_observation(defeat_debt, manifest, rei_loss, ()) is None

    second_manifest = demo_manifest("sha256-second-hidden-arena")
    second_loss = evaluate(second_manifest, (Result("REI", .40), Result("BASELINE_A", .25), Result("BASELINE_B", .15)))
    second_debt = comparative_defeat_debt(second_manifest, second_loss)
    assert second_debt is not None
    obs2 = defeat_observation(second_debt, second_manifest, second_loss, ("SCOPE_TRANSFER", "ROBUSTNESS"))
    assert obs2 is not None
    portfolio = (obs1, obs2)
    compressed = weakness_candidates(portfolio)
    assert compressed["status"] == "STRUCTURAL_WEAKNESS_CANDIDATES_READY"
    assert ("SCOPE_TRANSFER",) in compressed["candidates"] and compressed["causal_status"] == "UNPROVEN"

    same_challenge_win = evaluate(manifest, (Result("REI", .10), Result("BASELINE_A", .20), Result("BASELINE_B", .30)))
    assert resolve_comparative_defeat(
        defeat_debt, prior_manifest=manifest, prior_evaluation=rei_loss,
        fresh_manifest=manifest, fresh_evaluation=same_challenge_win,
    ).status == "OPEN"

    fresh_manifest = demo_manifest("sha256-fresh-hidden-arena")
    fresh_win = evaluate(fresh_manifest, (Result("REI", .09), Result("BASELINE_A", .21), Result("BASELINE_B", .29)))
    resolved = resolve_comparative_defeat(
        defeat_debt, prior_manifest=manifest, prior_evaluation=rei_loss,
        fresh_manifest=fresh_manifest, fresh_evaluation=fresh_win,
    )
    support = intervention_support(
        ("SCOPE_TRANSFER",), portfolio, prior_manifest=manifest, prior_evaluation=rei_loss,
        fresh_manifest=fresh_manifest, fresh_evaluation=fresh_win, intervention_modes=("SCOPE_TRANSFER",),
    )
    assert resolved.status == "RESOLVED" and "old defeat retained" in resolved.description
    assert support["status"] == "INTERVENTION_SUPPORTED_CANDIDATE"
    assert support["causal_truth"] is False and support["g6_status"] == "OPEN"

    posthoc = evaluate(manifest, loss_results, posthoc_competitor_exclusion=True)
    unfair = replace(manifest, competitors=(manifest.competitors[0], replace(manifest.competitors[1], budget=Budget(50, 100, 0, 10, 0))))
    unfair_result = evaluate(unfair, (Result("REI", .10), Result("BASELINE_A", .20)))
    assert posthoc["outcome"] == INVALID and unfair_result["outcome"] == INVALID

    return {
        "arena_status": READY,
        "scoped_rei_win_test": rei_win["outcome"],
        "rei_loss_preservation_test": rei_loss["outcome"],
        "comparative_defeat_debt_test": defeat_debt.debt_id,
        "same_exposed_challenge_cannot_clear_debt": True,
        "fresh_hidden_challenge_can_resolve_current_debt": resolved.status == "RESOLVED",
        "defeat_portfolio_compression": compressed["status"],
        "minimal_candidate_test": "SCOPE_TRANSFER",
        "cluster_is_not_causality": compressed["causal_status"] == "UNPROVEN",
        "intervention_supported_candidate": support["status"],
        "root_cause_truth_claimed": support["causal_truth"],
        "g6_status": "OPEN", "world_best": "UNVERIFIED", "world_unique": "UNVERIFIED",
        "canonical": False, "real_world_actuation_authority": 0,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run_sanity(), sort_keys=True, indent=2))
