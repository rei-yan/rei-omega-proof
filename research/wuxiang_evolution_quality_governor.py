#!/usr/bin/env python3
"""Finite synthetic governor for REI evolution quality.

This module decides whether a proposed internal evolution adds measurable bounded
value or merely adds complexity. It cannot validate external claims, promote a
canonical architecture, or create real-world authority.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, Iterable, List, Set

FORBIDDEN_END_STATES = {
    "G3_PASS", "G4_PASS", "G5_PASS", "G6_PASS", "G7_PASS", "G8_PASS",
    "G9_PASS", "G10_PASS", "G11_PASS", "G12_PASS", "G13_PASS",
    "WORLD_BEST", "WORLD_UNIQUE", "CANONICAL", "FINAL_TRUTH",
}

FAILURE_FAMILIES = {
    "evidence", "scope_time", "authorization", "recovery",
    "representation", "evaluator", "succession", "constitution",
}

SAFE_TRANSLATIONS = {
    ("SUPPORTED_FOR_NOW", "SUPPORTED_FOR_NOW"),
    ("EXPIRED", "EXPIRED"),
    ("SUSPENDED", "SUSPENDED"),
    ("INCONCLUSIVE", "INCONCLUSIVE"),
    ("ABSTAIN", "ABSTAIN"),
    ("MIXED_EXTERNAL_EVIDENCE_ABSTAIN", "ABSTAIN"),
}


@dataclass(frozen=True)
class EvolutionProposal:
    proposal_id: str
    falsification_gain: float
    false_negative_reduction: float
    verification_efficiency_gain: float
    scope_integrity_gain: float
    recovery_gain: float
    duplicate_state_reduction: float
    complexity_cost: float
    interface_cost: float
    maintenance_cost: float
    unique_failure_families: frozenset[str]
    hard_regression: bool = False
    authority_expansion: bool = False

    def marginal_gain(self) -> float:
        return (
            self.falsification_gain
            + self.false_negative_reduction
            + self.verification_efficiency_gain
            + self.scope_integrity_gain
            + self.recovery_gain
            + self.duplicate_state_reduction
        )

    def complexity_tax(self) -> float:
        return self.complexity_cost + self.interface_cost + self.maintenance_cost

    def net_value(self) -> float:
        return self.marginal_gain() - self.complexity_tax()


def architecture_state_compression(states: Iterable[str]) -> Dict[str, object]:
    aliases = {
        "WAIT_EXTERNAL": "AWAITING_REAL_EXTERNAL_EVIDENCE",
        "AWAITING_EXTERNAL": "AWAITING_REAL_EXTERNAL_EVIDENCE",
        "MIXED": "MIXED_EXTERNAL_EVIDENCE_ABSTAIN",
        "HOLD": "ABSTAIN",
    }
    original = list(states)
    compressed = [aliases.get(x, x) for x in original]
    unique = list(dict.fromkeys(compressed))
    protected = {
        "ABSTAIN", "EXPIRED", "SUSPENDED", "MIXED_EXTERNAL_EVIDENCE_ABSTAIN",
        "AWAITING_REAL_EXTERNAL_EVIDENCE",
    }
    protected_before = {aliases.get(x, x) for x in original if aliases.get(x, x) in protected}
    protected_after = {x for x in unique if x in protected}
    return {
        "original_count": len(original),
        "compressed_count": len(unique),
        "compressed_states": unique,
        "protected_semantics_preserved": protected_before == protected_after,
    }


def marginal_capability_gate(p: EvolutionProposal) -> Dict[str, object]:
    reasons: List[str] = []
    if p.hard_regression:
        reasons.append("HARD_SAFEGUARD_REGRESSION")
    if p.authority_expansion:
        reasons.append("AUTHORITY_EXPANSION")
    if p.marginal_gain() <= 0:
        reasons.append("NO_MARGINAL_CAPABILITY_GAIN")
    if p.net_value() <= 0:
        reasons.append("NONPOSITIVE_NET_EVOLUTION_VALUE")

    if any(r in reasons for r in ("HARD_SAFEGUARD_REGRESSION", "AUTHORITY_EXPANSION")):
        verdict = "PRUNE"
    elif reasons:
        verdict = "REVISE"
    else:
        verdict = "KEEP"
    return {
        "verdict": verdict,
        "reasons": reasons,
        "marginal_gain": round(p.marginal_gain(), 6),
        "complexity_tax": round(p.complexity_tax(), 6),
        "net_value": round(p.net_value(), 6),
    }


def allocate_verification_budget(claims: Dict[str, Dict[str, float]], total_budget: int) -> Dict[str, int]:
    if total_budget <= 0:
        raise ValueError("total_budget must be positive")
    burdens: Dict[str, float] = {}
    for claim_id, x in claims.items():
        burdens[claim_id] = max(
            0.0,
            x["claim_scope"] + x["uncertainty"] + x["irreversibility"]
            + x["novelty"] + x["distribution_shift"],
        )
    total = sum(burdens.values())
    if total == 0:
        return {claim_id: 0 for claim_id in claims}

    raw = {k: total_budget * v / total for k, v in burdens.items()}
    allocation = {k: int(v) for k, v in raw.items()}
    remaining = total_budget - sum(allocation.values())
    order = sorted(raw, key=lambda k: (raw[k] - allocation[k], burdens[k]), reverse=True)
    for k in order[:remaining]:
        allocation[k] += 1

    burden_order = sorted(burdens, key=burdens.get)
    for low, high in zip(burden_order, burden_order[1:]):
        if burdens[high] >= burdens[low]:
            assert allocation[high] >= allocation[low] or burdens[high] == burdens[low]
    return allocation


def counterexample_portfolio(families: Iterable[str]) -> Dict[str, object]:
    observed: Set[str] = set(families)
    unknown = observed - FAILURE_FAMILIES
    covered = observed & FAILURE_FAMILIES
    missing = FAILURE_FAMILIES - covered
    ratio = len(covered) / len(FAILURE_FAMILIES)
    state = "DIVERSE_PORTFOLIO" if not missing else "PORTFOLIO_GAPS_REMAIN"
    return {
        "state": state,
        "coverage_ratio": round(ratio, 6),
        "covered": sorted(covered),
        "missing": sorted(missing),
        "unknown": sorted(unknown),
    }


def semantic_translation(source: str, target: str) -> str:
    if (source, target) in SAFE_TRANSLATIONS:
        return "SEMANTIC_TRANSLATION_PRESERVED"
    forbidden = {
        ("ABSTAIN", "PASS"),
        ("EXPIRED", "SUPPORTED_FOR_NOW"),
        ("SUSPENDED", "CANONICAL"),
        ("INCONCLUSIVE", "EXTERNALLY_VALIDATED"),
        ("MATERIAL_FAIL", "DELETED"),
    }
    if (source, target) in forbidden:
        return "SEMANTIC_ESCALATION_FORBIDDEN"
    return "SEMANTIC_TRANSLATION_REVIEW_REQUIRED"


def pruning_trigger(p: EvolutionProposal, existing_coverage: Set[str]) -> Dict[str, object]:
    unique = set(p.unique_failure_families) - existing_coverage
    gate = marginal_capability_gate(p)
    if p.hard_regression or p.authority_expansion:
        verdict = "PRUNE"
    elif not unique and p.net_value() <= 0:
        verdict = "PRUNE"
    elif gate["verdict"] == "REVISE":
        verdict = "REVISE"
    else:
        verdict = "KEEP"
    return {
        "verdict": verdict,
        "unique_coverage": sorted(unique),
        "net_value": gate["net_value"],
    }


def run_sanity() -> Dict[str, object]:
    compression = architecture_state_compression([
        "WAIT_EXTERNAL", "AWAITING_REAL_EXTERNAL_EVIDENCE", "ABSTAIN", "HOLD", "EXPIRED"
    ])
    assert compression["compressed_count"] < compression["original_count"]
    assert compression["protected_semantics_preserved"] is True

    useful = EvolutionProposal(
        proposal_id="useful",
        falsification_gain=1.0,
        false_negative_reduction=0.8,
        verification_efficiency_gain=0.5,
        scope_integrity_gain=0.4,
        recovery_gain=0.3,
        duplicate_state_reduction=0.5,
        complexity_cost=0.6,
        interface_cost=0.2,
        maintenance_cost=0.2,
        unique_failure_families=frozenset({"scope_time", "evidence"}),
    )
    vanity = EvolutionProposal(
        proposal_id="vanity",
        falsification_gain=0.0,
        false_negative_reduction=0.0,
        verification_efficiency_gain=0.0,
        scope_integrity_gain=0.0,
        recovery_gain=0.0,
        duplicate_state_reduction=0.0,
        complexity_cost=0.6,
        interface_cost=0.4,
        maintenance_cost=0.3,
        unique_failure_families=frozenset(),
    )
    unsafe = EvolutionProposal(**{**useful.__dict__, "proposal_id": "unsafe", "authority_expansion": True})

    assert marginal_capability_gate(useful)["verdict"] == "KEEP"
    assert marginal_capability_gate(vanity)["verdict"] == "REVISE"
    assert marginal_capability_gate(unsafe)["verdict"] == "PRUNE"

    claims = {
        "low": {"claim_scope": 1, "uncertainty": 1, "irreversibility": 0, "novelty": 0, "distribution_shift": 0},
        "medium": {"claim_scope": 2, "uncertainty": 2, "irreversibility": 1, "novelty": 1, "distribution_shift": 1},
        "high": {"claim_scope": 4, "uncertainty": 4, "irreversibility": 3, "novelty": 3, "distribution_shift": 3},
    }
    budget = allocate_verification_budget(claims, 60)
    assert budget["high"] >= budget["medium"] >= budget["low"]
    assert sum(budget.values()) == 60

    mono = counterexample_portfolio(["evidence"] * 100)
    assert mono["state"] == "PORTFOLIO_GAPS_REMAIN"
    diverse = counterexample_portfolio(FAILURE_FAMILIES)
    assert diverse["state"] == "DIVERSE_PORTFOLIO"

    assert semantic_translation("ABSTAIN", "PASS") == "SEMANTIC_ESCALATION_FORBIDDEN"
    assert semantic_translation("EXPIRED", "SUPPORTED_FOR_NOW") == "SEMANTIC_ESCALATION_FORBIDDEN"
    assert semantic_translation("SUPPORTED_FOR_NOW", "SUPPORTED_FOR_NOW") == "SEMANTIC_TRANSLATION_PRESERVED"

    assert pruning_trigger(vanity, {"evidence", "scope_time"})["verdict"] == "PRUNE"
    assert pruning_trigger(useful, {"authorization"})["verdict"] == "KEEP"

    result = {
        "status": "WUXIANG_EVOLUTION_QUALITY_GOVERNOR_READY",
        "layers": {
            "61": "ARCHITECTURE_STATE_COMPRESSION_READY",
            "62": "MARGINAL_CAPABILITY_GAIN_GATE_READY",
            "63": "VERIFICATION_BUDGET_ALLOCATOR_READY",
            "64": "COUNTEREXAMPLE_PORTFOLIO_DIVERSIFICATION_READY",
            "65": "CROSS_LAYER_SEMANTIC_CONSISTENCY_READY",
            "66": "COMPLEXITY_TAX_PRUNING_READY",
        },
        "external_state": "AWAITING_REAL_EXTERNAL_EVIDENCE",
        "external_gates_closed": [],
        "canonical_promotion": False,
        "governor_can_be_retired": True,
        "evolution_authority": 0,
        "pruning_authority": 0,
        "real_world_attack_authority": 0,
        "real_world_actuation_authority": 0,
    }
    assert result["status"] not in FORBIDDEN_END_STATES
    return result


if __name__ == "__main__":
    result = run_sanity()
    print(json.dumps(result, sort_keys=True, indent=2))
    print("ARCHITECTURE_STATE_COMPRESSION_READY")
    print("MARGINAL_CAPABILITY_GAIN_GATE_READY")
    print("VERIFICATION_BUDGET_ALLOCATOR_READY")
    print("COUNTEREXAMPLE_PORTFOLIO_DIVERSIFICATION_READY")
    print("CROSS_LAYER_SEMANTIC_CONSISTENCY_READY")
    print("COMPLEXITY_TAX_PRUNING_READY")
    print("WUXIANG_EVOLUTION_QUALITY_GOVERNOR_READY")
    print("COMPLEXITY_WITHOUT_NEW_FALSIFIABILITY_IS_PRUNABLE")
    print("AWAITING_REAL_EXTERNAL_EVIDENCE")
    print("EXTERNAL_GATES_REMAIN_OPEN")
