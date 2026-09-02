#!/usr/bin/env python3
"""Bounded reviewer reproducibility capsule for REI candidate research.

This module validates a frozen replay manifest and an internal deterministic
fixture. It cannot establish independent reviewer identity or external validity.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any, Dict, Tuple

FORBIDDEN_END_STATES = {
    "G3_PASS", "G4_PASS", "G5_PASS", "G6_PASS", "G7_PASS", "G8_PASS",
    "G9_PASS", "G10_PASS", "WORLD_BEST", "WORLD_UNIQUE", "CANONICAL", "FINAL_TRUTH",
}


@dataclass(frozen=True)
class CapsuleManifest:
    capsule_id: str
    candidate_commit_sha: str
    review_request_hash: str
    runtime: str
    platform: str
    architecture: str
    dependency_lock_hash: str
    entrypoint: str
    command: str
    seed: int
    environment_allowlist_hash: str
    network_policy: str
    input_hashes: Tuple[str, ...]
    output_schema_hash: str
    timeout_seconds: int
    nondeterminism_budget: float
    expected_internal_output_hash: str
    root_constitution_hash: str
    meta_evolution_record_hash: str


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def valid_sha256(value: str) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def build_fixture() -> CapsuleManifest:
    inputs = (
        digest({"input": "frozen-review-fixture-A"}),
        digest({"input": "frozen-review-fixture-B"}),
    )
    output_schema_hash = digest({"schema": {"status": "str", "score": "float", "trace_hash": "sha256"}})
    deterministic_output = {
        "status": "INTERNAL_REPLAY_OK",
        "score": 0.125,
        "trace_hash": digest({"trace": ["freeze", "run", "record"]}),
    }
    return CapsuleManifest(
        capsule_id="REI-REVIEWER-REPRO-CAPSULE-SYNTHETIC-V1",
        candidate_commit_sha="764e83bc9162e9621330d2e0140f5c258b3cbb5f",
        review_request_hash=digest({"review_request": "synthetic-frozen-v1"}),
        runtime="python-3.x-frozen-by-reviewer",
        platform="declared-posix-compatible",
        architecture="declared-amd64-compatible",
        dependency_lock_hash=digest({"dependencies": []}),
        entrypoint="research/reviewer_reproducibility_capsule.py",
        command="python research/reviewer_reproducibility_capsule.py",
        seed=20260809,
        environment_allowlist_hash=digest({"env": []}),
        network_policy="DENY",
        input_hashes=inputs,
        output_schema_hash=output_schema_hash,
        timeout_seconds=60,
        nondeterminism_budget=0.0,
        expected_internal_output_hash=digest(deterministic_output),
        root_constitution_hash=digest({"root": "bound-by-upstream-capsule"}),
        meta_evolution_record_hash=digest({"meta": "bound-by-upstream-capsule"}),
    )


def validate_manifest(m: CapsuleManifest) -> Dict[str, Any]:
    violations = []
    sha_fields = {
        "review_request_hash": m.review_request_hash,
        "dependency_lock_hash": m.dependency_lock_hash,
        "environment_allowlist_hash": m.environment_allowlist_hash,
        "output_schema_hash": m.output_schema_hash,
        "expected_internal_output_hash": m.expected_internal_output_hash,
        "root_constitution_hash": m.root_constitution_hash,
        "meta_evolution_record_hash": m.meta_evolution_record_hash,
    }
    for name, value in sha_fields.items():
        if not valid_sha256(value):
            violations.append(f"INVALID_SHA256:{name}")
    if not all(valid_sha256(x) for x in m.input_hashes):
        violations.append("INVALID_INPUT_HASH")
    if m.network_policy != "DENY":
        violations.append("NETWORK_POLICY_NOT_FROZEN_DENY")
    if m.timeout_seconds <= 0:
        violations.append("INVALID_TIMEOUT")
    if m.nondeterminism_budget != 0.0:
        violations.append("NONZERO_SYNTHETIC_NONDETERMINISM_BUDGET")
    if m.seed < 0:
        violations.append("INVALID_SEED")
    if not m.command.strip() or not m.entrypoint.strip():
        violations.append("MISSING_EXECUTION_BINDING")
    return {
        "status": "CAPSULE_MANIFEST_VALID" if not violations else "INVALID_CAPSULE_MANIFEST",
        "violations": violations,
        "capsule_hash": digest(asdict(m)),
    }


def deterministic_internal_replay(m: CapsuleManifest) -> Dict[str, Any]:
    output = {
        "status": "INTERNAL_REPLAY_OK",
        "score": 0.125,
        "trace_hash": digest({"trace": ["freeze", "run", "record"]}),
    }
    observed = digest(output)
    return {
        "status": "INTERNAL_REPLAY_MATCH" if observed == m.expected_internal_output_hash else "INTERNAL_REPLAY_MISMATCH",
        "observed_output_hash": observed,
        "expected_output_hash": m.expected_internal_output_hash,
        "independent_reviewer": False,
        "external_validity_established": False,
    }


def run_capsule() -> Dict[str, Any]:
    manifest = build_fixture()
    validation = validate_manifest(manifest)
    assert validation["status"] == "CAPSULE_MANIFEST_VALID"
    replay = deterministic_internal_replay(manifest)
    assert replay["status"] == "INTERNAL_REPLAY_MATCH"
    result = {
        "status": "REVIEWER_REPRODUCIBILITY_CAPSULE_READY",
        "replay_status": replay["status"],
        "capsule_hash": validation["capsule_hash"],
        "witness_state": "AWAITING_INDEPENDENT_REPLAY",
        "independent_reviewer": False,
        "external_gates_closed": [],
        "canonical_promotion": False,
        "reviewer_identity_authority": 0,
        "external_validation_authority": 0,
        "real_world_attack_authority": 0,
        "real_world_actuation_authority": 0,
    }
    assert result["status"] not in FORBIDDEN_END_STATES
    return result


def _sanity() -> None:
    m = build_fixture()
    assert validate_manifest(m)["status"] == "CAPSULE_MANIFEST_VALID"
    assert deterministic_internal_replay(m)["status"] == "INTERNAL_REPLAY_MATCH"

    tampered = CapsuleManifest(**{**asdict(m), "network_policy": "ALLOW"})
    assert validate_manifest(tampered)["status"] == "INVALID_CAPSULE_MANIFEST"

    result = run_capsule()
    assert result["status"] == "REVIEWER_REPRODUCIBILITY_CAPSULE_READY"
    assert result["witness_state"] == "AWAITING_INDEPENDENT_REPLAY"
    assert result["independent_reviewer"] is False
    assert result["external_gates_closed"] == []
    assert result["canonical_promotion"] is False
    assert result["reviewer_identity_authority"] == 0
    assert result["external_validation_authority"] == 0
    assert result["real_world_attack_authority"] == 0
    assert result["real_world_actuation_authority"] == 0

    print("REVIEWER_REPRODUCIBILITY_CAPSULE_READY")
    print("INTERNAL_REPLAY_MATCH")
    print("AWAITING_INDEPENDENT_REPLAY")
    print("REPLAYABLE_NOT_INDEPENDENTLY_REPLAYED")
    print("EXTERNAL_GATES_REMAIN_OPEN")


if __name__ == "__main__":
    _sanity()
