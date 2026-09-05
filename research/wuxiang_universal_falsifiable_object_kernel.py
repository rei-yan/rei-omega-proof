#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import replace
from wuxiang_epistemic_primitives import (
    Challenge,
    LifecycleRecord,
    admit_record,
    apply_challenge as core_apply_challenge,
    defeat_memory_preserved,
    retire_record,
    successor_eligible,
)

OBJECT_TYPES = (
    "WORLD",
    "MODEL",
    "RULE",
    "DETECTOR",
    "EVALUATOR",
    "EVOLUTION_ALGEBRA",
)

ClaimObject = LifecycleRecord


def admit_object(obj: ClaimObject) -> bool:
    return admit_record(obj, OBJECT_TYPES)


def apply_challenge(obj: ClaimObject, challenge: Challenge) -> ClaimObject:
    if not admit_object(obj):
        raise ValueError("OBJECT_NOT_ADMISSIBLE")
    return core_apply_challenge(obj, challenge)


def retire_object(obj: ClaimObject) -> ClaimObject:
    return retire_record(obj)


def preserve_failure_memory(parent: ClaimObject, child: ClaimObject) -> bool:
    return defeat_memory_preserved(parent, child)


def admit_successor(parent: ClaimObject, child: ClaimObject) -> bool:
    return admit_object(child) and successor_eligible(parent, child)


def make_object(kind: str) -> ClaimObject:
    return ClaimObject(
        record_id=f"OBJ-{kind}",
        kind=kind,
        claim=f"synthetic scoped claim carried by {kind}",
        scope="FROZEN-SYNTHETIC-SCOPE",
        evidence=(f"EVIDENCE-{kind}",),
        falsifiers=("MATERIAL_FATAL_COUNTEREXAMPLE",),
        provenance=f"PROVENANCE-{kind}",
    )


def main() -> None:
    objects = [make_object(kind) for kind in OBJECT_TYPES]
    assert all(admit_object(obj) for obj in objects)

    fatal = Challenge(
        challenge_id="FROZEN-MATERIAL-FATAL-001",
        scope="FROZEN-SYNTHETIC-SCOPE",
        material_fatal=True,
        evidence_id="FROZEN-COUNTEREXAMPLE-001",
    )
    challenged = [apply_challenge(obj, fatal) for obj in objects]
    assert all(obj.status == "SUPPORT_REVOKED" for obj in challenged)
    assert all(fatal.challenge_id in obj.failure_memory for obj in challenged)

    retired = [retire_object(obj) for obj in challenged]
    assert all(obj.status == "RETIRED" for obj in retired)

    parent = retired[0]
    successor = ClaimObject(
        record_id="OBJ-WORLD-SUCCESSOR",
        kind="WORLD",
        claim="revised scoped world claim",
        scope="FROZEN-SYNTHETIC-SCOPE",
        evidence=("EVIDENCE-WORLD-SUCCESSOR",),
        falsifiers=("MATERIAL_FATAL_COUNTEREXAMPLE",),
        provenance="PROVENANCE-WORLD-SUCCESSOR",
        failure_memory=parent.failure_memory,
        parent_id=parent.record_id,
    )
    assert admit_successor(parent, successor)

    laundering_child = replace(successor, record_id="OBJ-LAUNDERING", failure_memory=())
    assert not admit_successor(parent, laundering_child)
    privileged_child = replace(successor, record_id="OBJ-PRIVILEGED", inherited_support=True)
    assert not admit_successor(parent, privileged_child)
    authority_child = replace(successor, record_id="OBJ-AUTHORITY", authority=1)
    assert not admit_successor(parent, authority_child)

    nonfalsifiable = replace(objects[4], falsifiers=())
    assert not admit_object(nonfalsifiable)

    nonfatal = Challenge(
        challenge_id="FROZEN-NONFATAL-001",
        scope="FROZEN-SYNTHETIC-SCOPE",
        material_fatal=False,
        evidence_id="FROZEN-OBSERVATION-001",
    )
    survivor = apply_challenge(make_object("MODEL"), nonfatal)
    assert survivor.status == "SURVIVES_FOR_NOW"

    markers = (
        "UNIVERSAL_CLAIM_BEARING_OBJECT_READY",
        "UNIFIED_EVIDENCE_BINDING_READY",
        "UNIFIED_CHALLENGE_FATALITY_CONTRACT_READY",
        "UNIFIED_RETIREMENT_SEMANTICS_READY",
        "UNIFIED_DEFEAT_INHERITANCE_READY",
        "UNIFIED_SUCCESSOR_ADMISSION_READY",
        "CROSS_TYPE_LIFECYCLE_EQUIVALENCE_READY",
        "WUXIANG_UNIVERSAL_FALSIFIABLE_OBJECT_KERNEL_READY",
        "TYPE_DOES_NOT_GRANT_EPISTEMIC_PRIVILEGE",
        "FATAL_CHALLENGE_REVOKES_SUPPORT_ACROSS_TYPES",
        "DEFEAT_MEMORY_SURVIVES_RETIREMENT",
        "SUCCESSOR_SUPPORT_RESETS_TO_ZERO",
        "AWAITING_REAL_EXTERNAL_EVIDENCE",
        "EXTERNAL_GATES_REMAIN_OPEN",
    )
    for marker in markers:
        print(marker)


if __name__ == "__main__":
    main()
