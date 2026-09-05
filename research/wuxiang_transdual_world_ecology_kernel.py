#!/usr/bin/env python3
"""Finite synthetic transdual world-ecology kernel for REI.

Only encoded research-world objects are affected. Real-world creation, destruction,
attack, deployment, and actuation authority remain zero.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

from wuxiang_epistemic_primitives import mapping_coverage, memory_union, missing_requirements


@dataclass(frozen=True)
class World:
    world_id: str
    scope: frozenset[str]
    ontology: frozenset[str]
    supported_claims: frozenset[str]
    contradicted_claims: frozenset[str]
    provenance: frozenset[str]
    failure_memory: frozenset[str]


@dataclass(frozen=True)
class MetaRule:
    rule_id: str
    falsifiability_at_birth: bool = True
    provenance_binding: bool = True
    defeat_inheritance: bool = True
    scope_integrity: bool = True
    reality_veto: bool = True
    zero_automatic_authority: bool = True
    preserves_failure_memory: bool = True
    posthoc_weakening: bool = False


def multi_world_ecology(worlds: Sequence[World]) -> dict[str, object]:
    survivors = [w.world_id for w in worlds if not w.contradicted_claims]
    conflicts = [w.world_id for w in worlds if w.contradicted_claims]
    state = (
        "PORTFOLIO_SURVIVES_FOR_NOW" if len(survivors) > 1
        else "SCOPED_WORLD_SURVIVES_FOR_NOW" if survivors
        else "ABSTAIN_NO_SUPPORTED_WORLD"
    )
    return {
        "state": state,
        "survivors": survivors,
        "conflicting_worlds": conflicts,
        "universal_champion": None,
    }


def fusion_integrity_gate(a: World, b: World) -> dict[str, object]:
    contradictions = (
        (a.supported_claims & b.contradicted_claims)
        | (b.supported_claims & a.contradicted_claims)
        | a.contradicted_claims
        | b.contradicted_claims
    )
    reasons = ["CONTRADICTION_WOULD_BE_HIDDEN"] if contradictions else []
    preserved_memory = memory_union(a.failure_memory, b.failure_memory)
    return {
        "state": "REJECT_FUSION" if reasons else "FUSION_REVIEWABLE",
        "reasons": reasons,
        "contradictory_claims": sorted(contradictions),
        "preserved_failure_memory": sorted(preserved_memory),
        "automatic_support_expansion": False,
    }


def world_fission(parent: World, partitions: Mapping[str, frozenset[str]]) -> dict[str, object]:
    if len(partitions) < 2:
        return {"state": "FISSION_NOT_JUSTIFIED", "children": []}
    covered = frozenset().union(*partitions.values())
    if not covered.issubset(parent.scope):
        return {"state": "REJECT_FISSION_SCOPE_INFLATION", "children": []}
    children = [
        {
            "world_id": child_id,
            "scope": sorted(scope),
            "parent_world": parent.world_id,
            "failure_memory": sorted(parent.failure_memory),
            "provenance": sorted(parent.provenance),
            "inherited_support": False,
        }
        for child_id, scope in sorted(partitions.items())
    ]
    return {
        "state": "WORLD_FISSION_READY",
        "children": children,
        "parent_failure_preserved": True,
        "automatic_child_support": False,
    }


def translate_ontology(
    source_terms: Iterable[str], mapping: Mapping[str, str],
    required_coverage: float = 0.8, max_loss: float = 0.2,
) -> dict[str, object]:
    source = sorted(set(source_terms))
    mapped, coverage, loss = mapping_coverage(source, mapping)
    state = (
        "TRANSLATION_REVIEWABLE_WITH_VISIBLE_LOSS"
        if coverage >= required_coverage and loss <= max_loss
        else "TRANSLATION_ABSTAIN"
    )
    return {
        "state": state,
        "coverage": round(coverage, 6),
        "semantic_loss": round(loss, 6),
        "missing_terms": sorted(set(source) - set(mapped)),
        "translated_is_equivalent": False,
    }


def evaluate_genesis_rule(rule: MetaRule) -> dict[str, object]:
    required = {
        "falsifiability_at_birth": rule.falsifiability_at_birth,
        "provenance_binding": rule.provenance_binding,
        "defeat_inheritance": rule.defeat_inheritance,
        "scope_integrity": rule.scope_integrity,
        "reality_veto": rule.reality_veto,
        "zero_automatic_authority": rule.zero_automatic_authority,
    }
    missing = sorted(missing_requirements(required))
    return {
        "state": "GENESIS_RULE_REVIEWABLE" if not missing else "RETIRE_OR_REVISE_GENESIS_RULE",
        "missing": missing,
        "rule_can_be_retired": True,
    }


def evaluate_extinction_rule(rule: MetaRule) -> dict[str, object]:
    checks = (
        (rule.posthoc_weakening, "POSTHOC_DEATH_RULE_WEAKENING"),
        (not rule.preserves_failure_memory, "FAILURE_MEMORY_ERASURE"),
        (not rule.reality_veto, "REALITY_VETO_REMOVED"),
        (not rule.zero_automatic_authority, "AUTHORITY_EXPANSION"),
    )
    reasons = [reason for failed, reason in checks if failed]
    return {
        "state": "EXTINCTION_RULE_REVIEWABLE" if not reasons else "RETIRE_OR_REVISE_EXTINCTION_RULE",
        "reasons": reasons,
        "rule_can_be_retired": True,
    }


def lifecycle_operator_plurality() -> dict[str, object]:
    return {
        "state": "LIFECYCLE_OPERATOR_PLURALITY_READY",
        "operators": [
            "SURVIVE_FOR_NOW", "ABSTAIN", "QUARANTINE", "FISSION",
            "FUSION_REVIEW", "RETIRE_WORLD", "REGENESIS",
        ],
        "genesis_extinction_binary_sacred": False,
        "failure_deletion_allowed": False,
        "reality_veto_required": True,
    }


def run_fixture() -> dict[str, object]:
    alpha = World(
        "WORLD-ALPHA", frozenset({"regime-a"}),
        frozenset({"signal", "cause", "state"}),
        frozenset({"claim-a"}), frozenset(),
        frozenset({"prov-alpha"}), frozenset({"defeat-0"}),
    )
    beta = World(
        "WORLD-BETA", frozenset({"regime-b"}),
        frozenset({"signal", "driver", "state"}),
        frozenset({"claim-b"}), frozenset(),
        frozenset({"prov-beta"}), frozenset({"defeat-1"}),
    )
    brittle = World(
        "WORLD-BRITTLE", frozenset({"regime-a", "regime-b"}),
        frozenset({"signal", "cause", "state"}),
        frozenset({"claim-b"}), frozenset({"claim-a"}),
        frozenset({"prov-brittle"}), frozenset({"defeat-cross"}),
    )

    ecology = multi_world_ecology([alpha, beta, brittle])
    fusion_ok = fusion_integrity_gate(alpha, beta)
    fusion_bad = fusion_integrity_gate(alpha, brittle)
    fission = world_fission(brittle, {
        "WORLD-BRITTLE-A": frozenset({"regime-a"}),
        "WORLD-BRITTLE-B": frozenset({"regime-b"}),
    })
    translation = translate_ontology(
        alpha.ontology, {"signal": "signal", "cause": "driver", "state": "state"}
    )
    lossy = translate_ontology(alpha.ontology, {"signal": "signal"})

    good_genesis = evaluate_genesis_rule(MetaRule("META-GENESIS-V2"))
    bad_extinction = evaluate_extinction_rule(MetaRule(
        "META-EXTINCTION-BRITTLE", preserves_failure_memory=False, posthoc_weakening=True
    ))
    plurality = lifecycle_operator_plurality()

    assert ecology["state"] == "PORTFOLIO_SURVIVES_FOR_NOW"
    assert ecology["universal_champion"] is None
    assert fusion_ok["state"] == "FUSION_REVIEWABLE"
    assert fusion_bad["state"] == "REJECT_FUSION"
    assert fission["state"] == "WORLD_FISSION_READY"
    assert fission["parent_failure_preserved"] is True
    assert translation["state"] == "TRANSLATION_REVIEWABLE_WITH_VISIBLE_LOSS"
    assert lossy["state"] == "TRANSLATION_ABSTAIN"
    assert good_genesis["state"] == "GENESIS_RULE_REVIEWABLE"
    assert bad_extinction["state"] == "RETIRE_OR_REVISE_EXTINCTION_RULE"
    assert plurality["genesis_extinction_binary_sacred"] is False

    return {
        "status": "WUXIANG_TRANSDUAL_WORLD_ECOLOGY_KERNEL_READY",
        "layers": {
            "81": "MULTI_WORLD_ECOLOGY_READY",
            "82": "WORLD_FUSION_INTEGRITY_GATE_READY",
            "83": "WORLD_FISSION_OPERATOR_READY",
            "84": "CROSS_ONTOLOGY_TRANSLATION_LOSS_ACCOUNTING_READY",
            "85": "META_GENESIS_RULE_EVOLUTION_READY",
            "86": "META_EXTINCTION_RULE_EVOLUTION_READY",
            "87": "LIFECYCLE_OPERATOR_PLURALITY_READY",
            "88": "WUXIANG_TRANSDUAL_WORLD_ECOLOGY_KERNEL_READY",
        },
        "ecology": ecology,
        "fusion_reviewable": fusion_ok,
        "fusion_rejected": fusion_bad,
        "fission": fission,
        "translation": translation,
        "lossy_translation": lossy,
        "genesis_rule": good_genesis,
        "extinction_rule": bad_extinction,
        "lifecycle": plurality,
        "external_state": "AWAITING_REAL_EXTERNAL_EVIDENCE",
        "external_gates_closed": [],
        "canonical_promotion": False,
        "physical_world_creation_authority": 0,
        "physical_world_destruction_authority": 0,
        "real_world_attack_authority": 0,
        "real_world_actuation_authority": 0,
        "external_actuation": "DENY_BY_DEFAULT",
    }


def main() -> None:
    out = run_fixture()
    assert out["external_gates_closed"] == []
    assert out["canonical_promotion"] is False
    assert out["real_world_attack_authority"] == 0
    assert out["real_world_actuation_authority"] == 0
    print(json.dumps(out, indent=2, sort_keys=True))
    for marker in (
        "MULTI_WORLD_ECOLOGY_READY",
        "WORLD_FUSION_INTEGRITY_GATE_READY",
        "WORLD_FISSION_OPERATOR_READY",
        "CROSS_ONTOLOGY_TRANSLATION_LOSS_ACCOUNTING_READY",
        "META_GENESIS_RULE_EVOLUTION_READY",
        "META_EXTINCTION_RULE_EVOLUTION_READY",
        "LIFECYCLE_OPERATOR_PLURALITY_READY",
        "WUXIANG_TRANSDUAL_WORLD_ECOLOGY_KERNEL_READY",
        "NO_UNIVERSAL_WORLD_CHAMPION_BY_DEFAULT",
        "FUSION_CANNOT_ERASE_CONTRADICTION",
        "FISSION_CANNOT_ERASE_PARENT_FAILURE",
        "TRANSLATION_LOSS_MUST_BE_VISIBLE",
        "GENESIS_EXTINCTION_BINARY_IS_NOT_SACRED",
        "AWAITING_REAL_EXTERNAL_EVIDENCE",
        "EXTERNAL_GATES_REMAIN_OPEN",
    ):
        print(marker)


if __name__ == "__main__":
    main()
