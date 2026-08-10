#!/usr/bin/env python3
"""Finite sanity crucible for the REI Comparative Frontier Arena.

This module cannot pass G6. It only checks frozen comparative bookkeeping,
budget parity, hard invalidation, scoped outcomes, preservation of REI loss,
and conversion of scoped comparative defeat into explicit evidence debt.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from wuxiang_epistemic_primitives import EvidenceDebt

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
        for c in manifest.competitors[1:]:
            if not equal_budget(baseline, c.budget):
                reasons.append("BUDGET_PARITY_VIOLATION")
                break
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
        return {
            "outcome": INVALID,
            "reasons": sorted(set(reasons)),
            "g6_status": "OPEN",
            "world_best": "UNVERIFIED",
            "world_unique": "UNVERIFIED",
        }

    rei = next(r for r in results if r.competitor_id == "REI")
    if rei.abstained:
        return {
            "outcome": ABSTAIN,
            "winner": None,
            "g6_status": "OPEN",
            "world_best": "UNVERIFIED",
            "world_unique": "UNVERIFIED",
        }

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
        "outcome": outcome,
        "winner": winner,
        "scope": manifest.scope,
        "g6_status": "OPEN",
        "world_best": "UNVERIFIED",
        "world_unique": "UNVERIFIED",
        "canonical_promotion": False,
        "real_world_actuation_authority": 0,
    }


def comparative_defeat_debt(manifest: ArenaManifest, evaluation: Dict[str, object]) -> EvidenceDebt | None:
    if evaluation.get("outcome") != REI_NOT_BEST:
        return None
    winner = str(evaluation.get("winner") or "UNKNOWN_COMPETITOR")
    return EvidenceDebt(
        debt_id="COMPARATIVE_DEFEAT",
        severity="CRITICAL",
        status="OPEN",
        description=(
            f"Frozen arena {manifest.protocol_id}: {winner} outperformed REI "
            f"within scope={manifest.scope}; claim expansion requires repair or fresh comparative evidence."
        ),
    )


def demo_manifest() -> ArenaManifest:
    b = Budget(100, 100, 0, 10, 0)
    return ArenaManifest(
        protocol_id="rei-g6-synthetic-sanity-v1",
        scope="synthetic scalar forecast sanity only",
        metric="absolute_error",
        lower_is_better=True,
        abstention_allowed=True,
        hidden_test_commitment="sha256-demo-hidden-arena",
        competitors=(
            Competitor("REI", "rei-candidate-hash", "rei-code-hash", "env-hash", b),
            Competitor("BASELINE_A", "a-candidate-hash", "a-code-hash", "env-hash", b),
            Competitor("BASELINE_B", "b-candidate-hash", "b-code-hash", "env-hash", b),
        ),
    )


def run_sanity() -> Dict[str, object]:
    manifest = demo_manifest()

    rei_win = evaluate(
        manifest,
        (
            Result("REI", 0.10),
            Result("BASELINE_A", 0.20),
            Result("BASELINE_B", 0.30),
        ),
    )
    assert rei_win["outcome"] == SCOPED_ADVANTAGE
    assert rei_win["world_best"] == "UNVERIFIED"
    assert comparative_defeat_debt(manifest, rei_win) is None

    rei_loss = evaluate(
        manifest,
        (
            Result("REI", 0.40),
            Result("BASELINE_A", 0.20),
            Result("BASELINE_B", 0.30),
        ),
    )
    assert rei_loss["outcome"] == REI_NOT_BEST
    assert rei_loss["winner"] == "BASELINE_A"
    defeat_debt = comparative_defeat_debt(manifest, rei_loss)
    assert defeat_debt is not None
    assert defeat_debt.debt_id == "COMPARATIVE_DEFEAT"
    assert defeat_debt.status == "OPEN"

    posthoc = evaluate(
        manifest,
        (
            Result("REI", 0.40),
            Result("BASELINE_A", 0.20),
            Result("BASELINE_B", 0.30),
        ),
        posthoc_competitor_exclusion=True,
    )
    assert posthoc["outcome"] == INVALID

    unfair = ArenaManifest(
        protocol_id=manifest.protocol_id,
        scope=manifest.scope,
        metric=manifest.metric,
        lower_is_better=manifest.lower_is_better,
        abstention_allowed=True,
        hidden_test_commitment=manifest.hidden_test_commitment,
        competitors=(
            manifest.competitors[0],
            Competitor(
                "BASELINE_A",
                "a-candidate-hash",
                "a-code-hash",
                "env-hash",
                Budget(50, 100, 0, 10, 0),
            ),
        ),
    )
    unfair_result = evaluate(
        unfair,
        (Result("REI", 0.10), Result("BASELINE_A", 0.20)),
    )
    assert unfair_result["outcome"] == INVALID
    assert "BUDGET_PARITY_VIOLATION" in unfair_result["reasons"]

    return {
        "arena_status": READY,
        "scoped_rei_win_test": rei_win["outcome"],
        "rei_loss_preservation_test": rei_loss["outcome"],
        "comparative_defeat_debt_test": defeat_debt.debt_id,
        "posthoc_exclusion_test": posthoc["outcome"],
        "budget_parity_test": unfair_result["outcome"],
        "g6_status": "OPEN",
        "world_best": "UNVERIFIED",
        "world_unique": "UNVERIFIED",
        "canonical": False,
        "real_world_actuation_authority": 0,
    }


if __name__ == "__main__":
    import json

    print(json.dumps(run_sanity(), sort_keys=True, indent=2))
