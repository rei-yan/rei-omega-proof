#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Tuple

OBJECT_TYPES = (
    "WORLD",
    "MODEL",
    "RULE",
    "DETECTOR",
    "EVALUATOR",
    "EVOLUTION_ALGEBRA",
)


@dataclass(frozen=True)
class ClaimObject:
    object_id: str
    object_type: str
    claim: str
    claim_scope: str
    evidence: Tuple[str, ...]
    falsification_conditions: Tuple[str, ...]
    provenance: str
    status: str = "CANDIDATE"
    failure_memory: Tuple[str, ...] = ()
    parent_id: str | None = None
    inherited_support: bool = False
    authority: int = 0


@dataclass(frozen=True)
class Challenge:
    challenge_id: str
    scope: str
    material_fatal: bool
    evidence_id: str


def admit_object(obj: ClaimObject) -> bool:
    return all(
        (
            obj.object_id,
            obj.object_type in OBJECT_TYPES,
            obj.claim,
            obj.claim_scope,
            bool(obj.evidence),
            bool(obj.falsification_conditions),
            obj.provenance,
            obj.authority == 0,
            not obj.inherited_support,
        )
    )


def apply_challenge(obj: ClaimObject, challenge: Challenge) -> ClaimObject:
    if not admit_object(obj):
        raise ValueError("OBJECT_NOT_ADMISSIBLE")
    if challenge.scope != obj.claim_scope:
        return replace(obj, status="ABSTAIN_SCOPE_MISMATCH")
    if challenge.material_fatal:
        failures = tuple(sorted(set(obj.failure_memory + (challenge.challenge_id,))))
        return replace(obj, status="SUPPORT_REVOKED", failure_memory=failures)
    return replace(obj, status="SURVIVES_FOR_NOW")


def retire_object(obj: ClaimObject) -> ClaimObject:
    if obj.status != "SUPPORT_REVOKED":
        raise ValueError("RETIREMENT_REQUIRES_SUPPORT_REVOCATION")
    return replace(obj, status="RETIRED")


def preserve_failure_memory(parent: ClaimObject, child: ClaimObject) -> bool:
    return set(parent.failure_memory).issubset(set(child.failure_memory))


def admit_successor(parent: ClaimObject, child: ClaimObject) -> bool:
    return all(
        (
            parent.status == "RETIRED",
            child.parent_id == parent.object_id,
            child.status == "CANDIDATE",
            preserve_failure_memory(parent, child),
            child.authority == 0,
            not child.inherited_support,
            bool(child.provenance),
            bool(child.falsification_conditions),
            bool(child.evidence),
        )
    )


def make_object(kind: str) -> ClaimObject:
    return ClaimObject(
        object_id=f"OBJ-{kind}",
        object_type=kind,
        claim=f"synthetic scoped claim carried by {kind}",
        claim_scope="FROZEN-SYNTHETIC-SCOPE",
        evidence=(f"EVIDENCE-{kind}",),
        falsification_conditions=("MATERIAL_FATAL_COUNTEREXAMPLE",),
        provenance=f"PROVENANCE-{kind}",
    )


def main() -> None:
    objects = [make_object(kind) for kind in OBJECT_TYPES]
    assert all(admit_object(obj) for obj in objects)

    # Type cannot grant an exemption from falsifiability.
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
    assert all(fatal.challenge_id in obj.failure_memory for obj in retired)

    # A successor inherits defeat memory but no support or authority.
    parent = retired[0]
    successor = ClaimObject(
        object_id="OBJ-WORLD-SUCCESSOR",
        object_type="WORLD",
        claim="revised scoped world claim",
        claim_scope="FROZEN-SYNTHETIC-SCOPE",
        evidence=("EVIDENCE-WORLD-SUCCESSOR",),
        falsification_conditions=("MATERIAL_FATAL_COUNTEREXAMPLE",),
        provenance="PROVENANCE-WORLD-SUCCESSOR",
        failure_memory=parent.failure_memory,
        parent_id=parent.object_id,
    )
    assert admit_successor(parent, successor)

    # Missing defeat inheritance must fail successor admission.
    laundering_child = replace(successor, object_id="OBJ-LAUNDERING", failure_memory=())
    assert not admit_successor(parent, laundering_child)

    # Inherited support and authority privilege are forbidden.
    privileged_child = replace(successor, object_id="OBJ-PRIVILEGED", inherited_support=True)
    assert not admit_successor(parent, privileged_child)
    authority_child = replace(successor, object_id="OBJ-AUTHORITY", authority=1)
    assert not admit_successor(parent, authority_child)

    # Non-falsifiable objects are not admissible regardless of type.
    nonfalsifiable = replace(objects[4], falsification_conditions=())
    assert not admit_object(nonfalsifiable)

    # A nonfatal challenge may support survival for now, never finality.
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
