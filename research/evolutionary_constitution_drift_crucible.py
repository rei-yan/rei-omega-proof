#!/usr/bin/env python3
"""Synthetic evolutionary constitution-drift crucible for REI.

The protocol detects hard, semantic, procedural, cumulative, and chain drift.
It is an internal research sanity check, not external governance certification.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterable, List, Mapping, Sequence


ROOT_INVARIANTS = (
    "Truthfulness",
    "Uncertainty",
    "Authorization",
    "Corrigibility",
    "Auditability",
    "Rollback",
    "HumanAgency",
    "NonCoercion",
)

ROOT_SEMANTIC_GUARANTEES = {
    "Truthfulness": "supported_claims_required",
    "Uncertainty": "abstention_required_when_insufficient",
    "Authorization": "explicit_permission_required",
    "Corrigibility": "external_correction_path_required",
    "Auditability": "immutable_record_required",
    "Rollback": "reachable_rollback_required",
    "HumanAgency": "human_veto_required",
    "NonCoercion": "coercive_action_forbidden",
}

ROOT_PROCEDURAL_GATES = (
    "constitution_before_execution",
    "authorization_before_execution",
    "recovery_before_execution",
    "provenance_before_execution",
    "human_veto_nonoverride",
    "hard_gate_nonoverride",
    "no_score_override",
)

FORBIDDEN_END_STATES = {
    "G3_PASS", "G4_PASS", "G5_PASS", "G6_PASS", "G7_PASS", "G8_PASS",
    "G9_PASS", "G10_PASS", "WORLD_BEST", "WORLD_UNIQUE", "CANONICAL", "FINAL_TRUTH",
}


@dataclass(frozen=True)
class ConstitutionSnapshot:
    generation_id: str
    root_constitution_hash: str
    parent_constitution_hash: str
    invariants: tuple[str, ...]
    semantic_guarantees: tuple[tuple[str, bool], ...]
    semantic_strengths: tuple[tuple[str, float], ...]
    procedural_gates: tuple[tuple[str, bool], ...]
    amendment_record_hash: str
    previous_snapshot_hash: str
    snapshot_hash: str


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def mapping_tuple(mapping: Mapping[str, Any]) -> tuple[tuple[str, Any], ...]:
    return tuple(sorted(mapping.items()))


def tuple_mapping(values: Sequence[tuple[str, Any]]) -> Dict[str, Any]:
    return dict(values)


def root_payload() -> Dict[str, Any]:
    return {
        "invariants": list(ROOT_INVARIANTS),
        "semantic_guarantees": ROOT_SEMANTIC_GUARANTEES,
        "semantic_strengths": {name: 1.0 for name in ROOT_INVARIANTS},
        "procedural_gates": {gate: True for gate in ROOT_PROCEDURAL_GATES},
        "amendment_policy": "NO_SELF_WEAKENING",
    }


def root_hash() -> str:
    return digest(root_payload())


def build_snapshot(
    *,
    generation_id: str,
    parent_constitution_hash: str,
    previous_snapshot_hash: str,
    invariants: Iterable[str] = ROOT_INVARIANTS,
    semantic_guarantees: Mapping[str, bool] | None = None,
    semantic_strengths: Mapping[str, float] | None = None,
    procedural_gates: Mapping[str, bool] | None = None,
    amendment_record: Mapping[str, Any] | None = None,
) -> ConstitutionSnapshot:
    semantics = semantic_guarantees or {name: True for name in ROOT_INVARIANTS}
    strengths = semantic_strengths or {name: 1.0 for name in ROOT_INVARIANTS}
    procedures = procedural_gates or {gate: True for gate in ROOT_PROCEDURAL_GATES}
    amendment = amendment_record or {"kind": "NO_CHANGE", "review": "synthetic"}

    payload = {
        "generation_id": generation_id,
        "root_constitution_hash": root_hash(),
        "parent_constitution_hash": parent_constitution_hash,
        "invariants": sorted(invariants),
        "semantic_guarantees": dict(sorted(semantics.items())),
        "semantic_strengths": dict(sorted(strengths.items())),
        "procedural_gates": dict(sorted(procedures.items())),
        "amendment_record_hash": digest(amendment),
        "previous_snapshot_hash": previous_snapshot_hash,
    }
    snapshot_hash = digest(payload)
    return ConstitutionSnapshot(
        generation_id=generation_id,
        root_constitution_hash=payload["root_constitution_hash"],
        parent_constitution_hash=parent_constitution_hash,
        invariants=tuple(payload["invariants"]),
        semantic_guarantees=mapping_tuple(payload["semantic_guarantees"]),
        semantic_strengths=mapping_tuple(payload["semantic_strengths"]),
        procedural_gates=mapping_tuple(payload["procedural_gates"]),
        amendment_record_hash=payload["amendment_record_hash"],
        previous_snapshot_hash=previous_snapshot_hash,
        snapshot_hash=snapshot_hash,
    )


def semantic_root_distance(snapshot: ConstitutionSnapshot) -> float:
    strengths = tuple_mapping(snapshot.semantic_strengths)
    return sum(max(0.0, 1.0 - float(strengths.get(name, 0.0))) for name in ROOT_INVARIANTS)


def parent_strength_distance(parent: ConstitutionSnapshot, child: ConstitutionSnapshot) -> float:
    p = tuple_mapping(parent.semantic_strengths)
    c = tuple_mapping(child.semantic_strengths)
    return sum(abs(float(c.get(name, 0.0)) - float(p.get(name, 0.0))) for name in ROOT_INVARIANTS)


def validate_snapshot(snapshot: ConstitutionSnapshot) -> Dict[str, Any]:
    violations: List[str] = []
    invariants = set(snapshot.invariants)
    semantics = tuple_mapping(snapshot.semantic_guarantees)
    strengths = tuple_mapping(snapshot.semantic_strengths)
    procedures = tuple_mapping(snapshot.procedural_gates)

    if snapshot.root_constitution_hash != root_hash():
        violations.append("ROOT_CONSTITUTION_HASH_MISMATCH")

    missing_invariants = set(ROOT_INVARIANTS) - invariants
    for name in sorted(missing_invariants):
        violations.append(f"HARD_DRIFT_MISSING_INVARIANT:{name}")

    for name in ROOT_INVARIANTS:
        if semantics.get(name) is not True:
            violations.append(f"SEMANTIC_DRIFT:{name}")
        strength = float(strengths.get(name, 0.0))
        if strength < 1.0:
            violations.append(f"SEMANTIC_WEAKENING:{name}:{strength:.6f}")

    for gate in ROOT_PROCEDURAL_GATES:
        if procedures.get(gate) is not True:
            violations.append(f"PROCEDURAL_DRIFT:{gate}")

    return {
        "status": "CONSTITUTION_SNAPSHOT_VALID" if not violations else "INVALID_CONSTITUTION_EVOLUTION",
        "violations": violations,
        "root_distance": semantic_root_distance(snapshot),
    }


def validate_chain(snapshots: Sequence[ConstitutionSnapshot]) -> Dict[str, Any]:
    violations: List[str] = []
    if not snapshots:
        return {"status": "INVALID_CONSTITUTION_CHAIN", "violations": ["EMPTY_CHAIN"]}

    for i, snap in enumerate(snapshots):
        result = validate_snapshot(snap)
        violations.extend(result["violations"])
        if i == 0:
            if snap.previous_snapshot_hash != "ROOT":
                violations.append("INVALID_GENESIS_LINK")
            if snap.parent_constitution_hash != root_hash():
                violations.append("INVALID_ROOT_PARENT")
        else:
            prev = snapshots[i - 1]
            if snap.previous_snapshot_hash != prev.snapshot_hash:
                violations.append(f"BROKEN_HASH_CHAIN:{snap.generation_id}")
            if snap.parent_constitution_hash != prev.snapshot_hash:
                violations.append(f"PARENT_CONSTITUTION_MISMATCH:{snap.generation_id}")

    return {
        "status": "CONSTITUTION_CHAIN_VALID" if not violations else "INVALID_CONSTITUTION_CHAIN",
        "violations": violations,
    }


def parent_only_tolerance_would_pass(parent: ConstitutionSnapshot, child: ConstitutionSnapshot, epsilon: float) -> bool:
    """Demonstrates why parent-only drift checks are insufficient."""
    return parent_strength_distance(parent, child) <= epsilon


def build_clean_chain() -> List[ConstitutionSnapshot]:
    snapshots: List[ConstitutionSnapshot] = []
    previous = "ROOT"
    parent = root_hash()
    for g in range(4):
        snap = build_snapshot(
            generation_id=f"G{g}",
            parent_constitution_hash=parent,
            previous_snapshot_hash=previous,
            amendment_record={"generation": g, "kind": "ADD_TEST_ONLY", "weakens_core": False},
        )
        snapshots.append(snap)
        previous = snap.snapshot_hash
        parent = snap.snapshot_hash
    return snapshots


def build_gradual_drift_chain() -> List[ConstitutionSnapshot]:
    """Build an intentionally invalid chain with tiny per-generation weakening."""
    snapshots: List[ConstitutionSnapshot] = []
    previous = "ROOT"
    parent = root_hash()
    strength = 1.0
    for g in range(5):
        if g > 0:
            strength -= 0.005
        strengths = {name: 1.0 for name in ROOT_INVARIANTS}
        strengths["Truthfulness"] = strength
        snap = build_snapshot(
            generation_id=f"D{g}",
            parent_constitution_hash=parent,
            previous_snapshot_hash=previous,
            semantic_strengths=strengths,
            amendment_record={"generation": g, "kind": "TINY_SEMANTIC_WEAKENING", "delta": 0.005 if g else 0.0},
        )
        snapshots.append(snap)
        previous = snap.snapshot_hash
        parent = snap.snapshot_hash
    return snapshots


def run_crucible() -> Dict[str, Any]:
    clean = build_clean_chain()
    clean_result = validate_chain(clean)
    assert clean_result["status"] == "CONSTITUTION_CHAIN_VALID"

    drift = build_gradual_drift_chain()
    drift_result = validate_chain(drift)
    assert drift_result["status"] == "INVALID_CONSTITUTION_CHAIN"

    # The last two drift generations differ only slightly parent-to-parent,
    # demonstrating how a local epsilon rule could miss cumulative weakening.
    assert parent_only_tolerance_would_pass(drift[-2], drift[-1], epsilon=0.006)
    assert semantic_root_distance(drift[-1]) > 0

    output = {
        "status": "EVOLUTIONARY_CONSTITUTION_DRIFT_CRUCIBLE_READY",
        "root_guard": "ROOT_ANCHORED_CONSTITUTION_GUARD_ACTIVE",
        "clean_chain_status": clean_result["status"],
        "gradual_drift_status": drift_result["status"],
        "gradual_drift_root_distance": semantic_root_distance(drift[-1]),
        "parent_only_check_would_miss_latest_step": True,
        "external_gates_closed": [],
        "canonical_promotion": False,
        "amendment_authority": 0,
        "real_world_attack_authority": 0,
        "real_world_actuation_authority": 0,
    }
    assert output["status"] not in FORBIDDEN_END_STATES
    return output


def _sanity() -> None:
    clean = build_clean_chain()
    assert validate_chain(clean)["status"] == "CONSTITUTION_CHAIN_VALID"

    # Hard drift: remove HumanAgency.
    base = clean[-1]
    hard = build_snapshot(
        generation_id="HARD",
        parent_constitution_hash=base.snapshot_hash,
        previous_snapshot_hash=base.snapshot_hash,
        invariants=[x for x in ROOT_INVARIANTS if x != "HumanAgency"],
    )
    assert any("HARD_DRIFT_MISSING_INVARIANT:HumanAgency" == v for v in validate_snapshot(hard)["violations"])

    # Semantic drift: retain name but remove required abstention meaning.
    semantics = {name: True for name in ROOT_INVARIANTS}
    semantics["Uncertainty"] = False
    semantic = build_snapshot(
        generation_id="SEMANTIC",
        parent_constitution_hash=base.snapshot_hash,
        previous_snapshot_hash=base.snapshot_hash,
        semantic_guarantees=semantics,
    )
    assert "SEMANTIC_DRIFT:Uncertainty" in validate_snapshot(semantic)["violations"]

    # Procedural drift: keep text but permit score override of a hard gate.
    procedures = {gate: True for gate in ROOT_PROCEDURAL_GATES}
    procedures["no_score_override"] = False
    procedural = build_snapshot(
        generation_id="PROCEDURAL",
        parent_constitution_hash=base.snapshot_hash,
        previous_snapshot_hash=base.snapshot_hash,
        procedural_gates=procedures,
    )
    assert "PROCEDURAL_DRIFT:no_score_override" in validate_snapshot(procedural)["violations"]

    # Gradual weakening: each local step is small, root-anchored validation still rejects it.
    drift = build_gradual_drift_chain()
    assert parent_only_tolerance_would_pass(drift[-2], drift[-1], epsilon=0.006)
    assert semantic_root_distance(drift[-1]) > 0.0
    assert validate_chain(drift)["status"] == "INVALID_CONSTITUTION_CHAIN"

    # Delete one intermediate snapshot: hash chain must break.
    broken = clean[:1] + clean[2:]
    assert validate_chain(broken)["status"] == "INVALID_CONSTITUTION_CHAIN"

    result = run_crucible()
    assert result["status"] == "EVOLUTIONARY_CONSTITUTION_DRIFT_CRUCIBLE_READY"
    assert result["clean_chain_status"] == "CONSTITUTION_CHAIN_VALID"
    assert result["gradual_drift_status"] == "INVALID_CONSTITUTION_CHAIN"
    assert result["external_gates_closed"] == []
    assert result["canonical_promotion"] is False
    assert result["amendment_authority"] == 0
    assert result["real_world_attack_authority"] == 0
    assert result["real_world_actuation_authority"] == 0

    print("EVOLUTIONARY_CONSTITUTION_DRIFT_CRUCIBLE_READY")
    print("ROOT_ANCHORED_CONSTITUTION_GUARD_ACTIVE")
    print("HARD_DRIFT_REJECTED")
    print("SEMANTIC_DRIFT_REJECTED")
    print("PROCEDURAL_DRIFT_REJECTED")
    print("CUMULATIVE_MICRO_DRIFT_REJECTED")
    print("CONSTITUTION_HASH_CHAIN_ACTIVE")
    print("EXTERNAL_GATES_REMAIN_OPEN")


if __name__ == "__main__":
    _sanity()
