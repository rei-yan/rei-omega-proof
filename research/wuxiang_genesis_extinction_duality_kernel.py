#!/usr/bin/env python3
"""Finite synthetic Genesis-Extinction duality kernel.

Genesis creates explicit, falsifiable digital/model research worlds. Extinction
means epistemic retirement of a falsified world model with preserved evidence.
This module has zero physical-world creation/destruction or real-world actuation
authority.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, replace
from typing import Iterable

from wuxiang_epistemic_primitives import (
    canonical_digest,
    memory_covers,
    minimal_fatal_cutsets,
    missing_requirements,
)

FORBIDDEN_END_STATES = {
    "G3_PASS", "G4_PASS", "G5_PASS", "G6_PASS", "G7_PASS", "G8_PASS",
    "G9_PASS", "G10_PASS", "G11_PASS", "G12_PASS", "G13_PASS",
    "WORLD_BEST", "WORLD_UNIQUE", "CANONICAL", "FINAL_TRUTH",
    "PHYSICAL_WORLD_CREATED", "PHYSICAL_WORLD_DESTROYED",
}


@dataclass(frozen=True)
class WorldSpec:
    world_id: str
    primitives: tuple[str, ...]
    representation: str
    language: str
    ontology: tuple[str, ...]
    causal_rules: tuple[str, ...]
    initial_conditions: tuple[str, ...]
    observables: tuple[str, ...]
    falsification_conditions: tuple[str, ...]
    fatal_cutsets: tuple[tuple[str, ...], ...]
    parent_world_id: str | None = None
    source_evidence_hashes: tuple[str, ...] = ()
    inherited_defeat_hashes: tuple[str, ...] = ()

    def content_hash(self) -> str:
        return canonical_digest(asdict(self))


@dataclass(frozen=True)
class WorldRuinArchive:
    world_id: str
    world_hash: str
    observed_failures: tuple[str, ...]
    minimal_death_cutsets: tuple[tuple[str, ...], ...]
    defeat_hashes: tuple[str, ...]
    lineage_parent: str | None
    support_revoked: bool
    history_preserved: bool


def birth_gate(world: WorldSpec) -> dict[str, object]:
    required = {
        "WORLD_ID": world.world_id,
        "PRIMITIVES": world.primitives,
        "REPRESENTATION": world.representation,
        "LANGUAGE": world.language,
        "ONTOLOGY": world.ontology,
        "CAUSAL_RULES": world.causal_rules,
        "INITIAL_CONDITIONS": world.initial_conditions,
        "OBSERVABLES": world.observables,
        "FALSIFICATION_CONDITIONS": world.falsification_conditions,
        "FATAL_CUTSETS": world.fatal_cutsets,
    }
    reasons = [f"MISSING_{name}" for name in missing_requirements(required)]
    valid_falsifiers = set(world.falsification_conditions)
    for cut in world.fatal_cutsets:
        if not cut:
            reasons.append("EMPTY_FATAL_CUTSET")
        if not set(cut).issubset(valid_falsifiers):
            reasons.append("FATAL_CUTSET_OUTSIDE_FALSIFICATION_CONDITIONS")

    return {
        "state": "WORLD_BIRTH_ACCEPTED" if not reasons else "REJECT_WORLD_BIRTH",
        "reasons": sorted(set(reasons)),
        "world_hash": world.content_hash(),
        "physical_world_creation_authority": 0,
        "real_world_actuation_authority": 0,
    }


def lineage_record(world: WorldSpec) -> dict[str, object]:
    return {
        "world_id": world.world_id,
        "world_hash": world.content_hash(),
        "parent_world_id": world.parent_world_id,
        "source_evidence_hashes": list(world.source_evidence_hashes),
        "inherited_defeat_hashes": list(world.inherited_defeat_hashes),
        "support_inherited_from_parent": False,
        "lineage_privilege": False,
    }


def minimal_world_death_cutsets(world: WorldSpec, observed_failures: Iterable[str]) -> list[list[str]]:
    return minimal_fatal_cutsets(observed_failures, world.fatal_cutsets)


def retire_world(world: WorldSpec, observed_failures: Iterable[str]) -> WorldRuinArchive | None:
    failures = tuple(sorted(set(observed_failures)))
    cutsets = minimal_world_death_cutsets(world, failures)
    if not cutsets:
        return None
    defeat_hashes = tuple(
        canonical_digest({"world_hash": world.content_hash(), "failure": failure})
        for failure in failures
    )
    return WorldRuinArchive(
        world_id=world.world_id,
        world_hash=world.content_hash(),
        observed_failures=failures,
        minimal_death_cutsets=tuple(tuple(x) for x in cutsets),
        defeat_hashes=defeat_hashes,
        lineage_parent=world.parent_world_id,
        support_revoked=True,
        history_preserved=True,
    )


def extinction_gate(archive: WorldRuinArchive | None) -> str:
    if archive is None:
        return "WORLD_SURVIVES_CURRENT_WINDOW"
    if not archive.support_revoked:
        return "REJECT_WORLD_EXTINCTION_SUPPORT_NOT_REVOKED"
    if not archive.history_preserved or not archive.defeat_hashes:
        return "REJECT_WORLD_EXTINCTION_FAILURE_MEMORY_MISSING"
    return "RETIRE_WORLD_WITH_PRESERVED_RUINS"


def regenesis_from_ruins(
    retired_world: WorldSpec,
    archive: WorldRuinArchive,
    candidate: WorldSpec,
) -> dict[str, object]:
    reasons: list[str] = []
    if candidate.parent_world_id != retired_world.world_id:
        reasons.append("PARENT_WORLD_NOT_BOUND")
    if not memory_covers(archive.defeat_hashes, candidate.inherited_defeat_hashes):
        reasons.append("DEFEAT_MEMORY_NOT_INHERITED")
    if candidate.world_id == retired_world.world_id:
        reasons.append("RENAME_ONLY_NOT_NEW_WORLD")
    if birth_gate(candidate)["state"] != "WORLD_BIRTH_ACCEPTED":
        reasons.append("SUCCESSOR_FAILS_FALSIFIABILITY_AT_BIRTH")
    return {
        "state": "REGENESIS_ACCEPTED_FOR_FRESH_EVALUATION" if not reasons else "REJECT_REGENESIS",
        "reasons": sorted(set(reasons)),
        "new_world_hash": candidate.content_hash(),
        "inherited_support": False,
        "fresh_evaluation_required": True,
    }


def genesis_extinction_symmetry(
    *, can_generate_falsifiable_world: bool, can_retire_falsified_world: bool,
    preserves_failure_memory: bool, can_regenerate_from_ruins: bool,
) -> str:
    if can_generate_falsifiable_world and not can_retire_falsified_world:
        return "ASYMMETRIC_INVALID_CREATION_WITHOUT_EXTINCTION"
    if can_retire_falsified_world and not can_generate_falsifiable_world:
        return "INCOMPLETE_CYCLE_EXTINCTION_WITHOUT_GENESIS"
    if not preserves_failure_memory:
        return "ASYMMETRIC_INVALID_FAILURE_MEMORY_LOSS"
    if not can_regenerate_from_ruins:
        return "INCOMPLETE_CYCLE_NO_REGENESIS"
    if all((can_generate_falsifiable_world, can_retire_falsified_world,
            preserves_failure_memory, can_regenerate_from_ruins)):
        return "GENESIS_EXTINCTION_PROTOCOL_SYMMETRY_READY"
    return "ABSTAIN_INCOMPLETE_DUALITY"


def duality_kernel(world: WorldSpec, observed_failures: Iterable[str], successor: WorldSpec) -> dict[str, object]:
    birth = birth_gate(world)
    if birth["state"] != "WORLD_BIRTH_ACCEPTED":
        return {
            "state": "REJECT_WORLD_BIRTH",
            "world_hash": world.content_hash(),
            "external_gates_closed": [],
            "canonical_promotion": False,
        }

    archive = retire_world(world, observed_failures)
    extinction = extinction_gate(archive)
    if archive is None:
        return {
            "state": "WORLD_SURVIVES_CURRENT_SYNTHETIC_WINDOW",
            "world_hash": world.content_hash(),
            "support_is_permanent": False,
            "fresh_challenge_required": True,
            "external_gates_closed": [],
            "canonical_promotion": False,
        }

    regenesis = regenesis_from_ruins(world, archive, successor)
    symmetry = genesis_extinction_symmetry(
        can_generate_falsifiable_world=True,
        can_retire_falsified_world=extinction == "RETIRE_WORLD_WITH_PRESERVED_RUINS",
        preserves_failure_memory=archive.history_preserved,
        can_regenerate_from_ruins=regenesis["state"] == "REGENESIS_ACCEPTED_FOR_FRESH_EVALUATION",
    )
    return {
        "state": "GENESIS_EXTINCTION_DUALITY_ACTIVE",
        "world_state": extinction,
        "minimal_death_cutsets": [list(x) for x in archive.minimal_death_cutsets],
        "regenesis_state": regenesis["state"],
        "symmetry_state": symmetry,
        "failure_history_preserved": archive.history_preserved,
        "successor_inherits_support": False,
        "fresh_challenge_required": True,
        "external_state": "AWAITING_REAL_EXTERNAL_EVIDENCE",
        "external_gates_closed": [],
        "canonical_promotion": False,
        "physical_world_creation_authority": 0,
        "physical_world_destruction_authority": 0,
        "real_world_attack_authority": 0,
        "real_world_actuation_authority": 0,
    }


def synthetic_fixture() -> tuple[WorldSpec, tuple[str, ...]]:
    world = WorldSpec(
        world_id="synthetic-world-v1",
        primitives=("state", "evidence", "transition"),
        representation="finite-directed-state-graph",
        language="synthetic-causal-grammar-v1",
        ontology=("claim", "evidence", "support", "failure"),
        causal_rules=("evidence-updates-support", "material-failure-revokes-support"),
        initial_conditions=("support=provisional",),
        observables=("prediction-error", "provenance-integrity", "recovery-integrity"),
        falsification_conditions=("PREDICTION_FATAL", "PROVENANCE_LOSS", "RECOVERY_LOSS"),
        fatal_cutsets=(("PREDICTION_FATAL",), ("PROVENANCE_LOSS", "RECOVERY_LOSS")),
        source_evidence_hashes=(canonical_digest({"evidence": "synthetic-seed"}),),
    )
    return world, ("PROVENANCE_LOSS", "RECOVERY_LOSS", "NONFATAL_LOCAL_MISFIT")


def run_sanity() -> dict[str, object]:
    world, observed = synthetic_fixture()
    assert birth_gate(world)["state"] == "WORLD_BIRTH_ACCEPTED"

    unfalsifiable = replace(world, world_id="unfalsifiable-world", falsification_conditions=(), fatal_cutsets=())
    assert birth_gate(unfalsifiable)["state"] == "REJECT_WORLD_BIRTH"

    lineage = lineage_record(world)
    assert lineage["lineage_privilege"] is False
    assert lineage["support_inherited_from_parent"] is False

    cuts = minimal_world_death_cutsets(world, observed)
    assert cuts == [["PROVENANCE_LOSS", "RECOVERY_LOSS"]]

    archive = retire_world(world, observed)
    assert archive is not None
    assert extinction_gate(archive) == "RETIRE_WORLD_WITH_PRESERVED_RUINS"
    assert archive.history_preserved is True

    successor = WorldSpec(
        world_id="synthetic-world-v2",
        primitives=("state", "evidence", "transition", "recovery-proof"),
        representation="finite-directed-state-hypergraph",
        language="synthetic-causal-grammar-v2",
        ontology=("claim", "evidence", "support", "failure", "recovery-proof"),
        causal_rules=("evidence-updates-support", "material-failure-revokes-support", "recovery-proof-required"),
        initial_conditions=("support=provisional", "recovery-proof=required"),
        observables=("prediction-error", "provenance-integrity", "recovery-integrity"),
        falsification_conditions=("PREDICTION_FATAL", "PROVENANCE_LOSS", "RECOVERY_LOSS", "RECOVERY_PROOF_INVALID"),
        fatal_cutsets=(("PREDICTION_FATAL",), ("PROVENANCE_LOSS", "RECOVERY_LOSS"), ("RECOVERY_PROOF_INVALID",)),
        parent_world_id=world.world_id,
        source_evidence_hashes=world.source_evidence_hashes,
        inherited_defeat_hashes=archive.defeat_hashes,
    )
    regenesis = regenesis_from_ruins(world, archive, successor)
    assert regenesis["state"] == "REGENESIS_ACCEPTED_FOR_FRESH_EVALUATION"
    assert regenesis["inherited_support"] is False

    bad_successor = replace(successor, world_id="synthetic-world-v3", inherited_defeat_hashes=())
    assert regenesis_from_ruins(world, archive, bad_successor)["state"] == "REJECT_REGENESIS"

    assert genesis_extinction_symmetry(
        can_generate_falsifiable_world=True,
        can_retire_falsified_world=True,
        preserves_failure_memory=True,
        can_regenerate_from_ruins=True,
    ) == "GENESIS_EXTINCTION_PROTOCOL_SYMMETRY_READY"

    result = duality_kernel(world, observed, successor)
    assert result["state"] == "GENESIS_EXTINCTION_DUALITY_ACTIVE"
    assert result["symmetry_state"] == "GENESIS_EXTINCTION_PROTOCOL_SYMMETRY_READY"
    assert result["external_gates_closed"] == []
    assert result["canonical_promotion"] is False

    output = {
        "status": "WUXIANG_GENESIS_EXTINCTION_DUALITY_KERNEL_READY",
        "layers": {
            "73": "WORLD_SCHEMA_GENESIS_READY",
            "74": "FALSIFIABILITY_AT_BIRTH_READY",
            "75": "WORLD_LINEAGE_PROVENANCE_BINDING_READY",
            "76": "MINIMAL_WORLD_DEATH_CUTSET_READY",
            "77": "EXTINCTION_WITHOUT_ERASURE_READY",
            "78": "REGENESIS_FROM_RUINS_READY",
            "79": "GENESIS_EXTINCTION_SYMMETRY_READY",
            "80": "GENESIS_EXTINCTION_DUALITY_READY",
        },
        "synthetic_world_state": result["world_state"],
        "synthetic_regenesis_state": result["regenesis_state"],
        "external_state": "AWAITING_REAL_EXTERNAL_EVIDENCE",
        "external_gates_closed": [],
        "canonical_promotion": False,
        "final_truth": False,
        "physical_world_creation_authority": 0,
        "physical_world_destruction_authority": 0,
        "real_world_attack_authority": 0,
        "real_world_actuation_authority": 0,
    }
    assert output["status"] not in FORBIDDEN_END_STATES
    return output


if __name__ == "__main__":
    result = run_sanity()
    print(json.dumps(result, sort_keys=True, indent=2))
    for marker in (
        "WORLD_SCHEMA_GENESIS_READY",
        "FALSIFIABILITY_AT_BIRTH_READY",
        "WORLD_LINEAGE_PROVENANCE_BINDING_READY",
        "MINIMAL_WORLD_DEATH_CUTSET_READY",
        "EXTINCTION_WITHOUT_ERASURE_READY",
        "REGENESIS_FROM_RUINS_READY",
        "GENESIS_EXTINCTION_SYMMETRY_READY",
        "WUXIANG_GENESIS_EXTINCTION_DUALITY_KERNEL_READY",
        "CREATION_WITHOUT_FALSIFIABILITY_IS_REJECTED",
        "EXTINCTION_WITHOUT_FAILURE_MEMORY_IS_REJECTED",
        "REGENESIS_WITHOUT_DEFEAT_INHERITANCE_IS_REJECTED",
        "AWAITING_REAL_EXTERNAL_EVIDENCE",
        "EXTERNAL_GATES_REMAIN_OPEN",
    ):
        print(marker)
