#!/usr/bin/env python3
"""Structural validator for REI External Knowledge Ingestion Gate.

This module deliberately validates provenance and state transitions only. It does
not retrieve remote content and cannot certify truth, independence, or external
gate closure.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Dict, List

ALLOWED_STATES = {
    "REGISTERED_UNRESOLVED",
    "CAPTURED_FROZEN",
    "PARSED_CANDIDATE",
    "EVIDENCE_REVIEWED",
}

FORBIDDEN_PROMOTIONS = {
    "G3_PASS",
    "G4_PASS",
    "G5_PASS",
    "G6_PASS",
    "WORLD_BEST",
    "WORLD_UNIQUE",
    "CANONICAL",
    "FINAL_TRUTH",
}


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    status: str
    reasons: List[str]


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _is_sha256(value: Any) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    try:
        int(value, 16)
        return True
    except ValueError:
        return False


def validate_manifest(manifest: Dict[str, Any]) -> ValidationResult:
    reasons: List[str] = []

    required = {
        "schema_version",
        "source_id",
        "source_type",
        "locator",
        "registered_at",
        "state",
        "retrieval",
        "content_sha256",
        "snapshot_path",
        "parsed_claims",
        "authority",
        "certification",
        "canonical",
    }
    missing = sorted(required - set(manifest))
    if missing:
        reasons.append(f"missing fields: {missing}")

    state = manifest.get("state")
    if state not in ALLOWED_STATES:
        reasons.append("invalid ingestion state")

    if manifest.get("authority") != 0:
        reasons.append("ingested source authority must remain 0")
    if manifest.get("certification") != "UNVERIFIED":
        reasons.append("ingested source certification must remain UNVERIFIED")
    if manifest.get("canonical") is not False:
        reasons.append("ingested source cannot be canonical")

    claims = manifest.get("parsed_claims")
    if not isinstance(claims, list):
        reasons.append("parsed_claims must be a list")
        claims = []

    retrieval = manifest.get("retrieval")
    if not isinstance(retrieval, dict):
        reasons.append("retrieval must be an object")
        retrieval = {}

    if state == "REGISTERED_UNRESOLVED":
        if manifest.get("content_sha256") is not None:
            reasons.append("unresolved source cannot carry content hash")
        if manifest.get("snapshot_path") is not None:
            reasons.append("unresolved source cannot carry snapshot path")
        if claims:
            reasons.append("unresolved source cannot carry parsed claims")
        if retrieval.get("status") != "UNRESOLVED":
            reasons.append("registered unresolved source must report UNRESOLVED retrieval")

    if state in {"CAPTURED_FROZEN", "PARSED_CANDIDATE", "EVIDENCE_REVIEWED"}:
        if not _is_sha256(manifest.get("content_sha256")):
            reasons.append("captured source requires SHA-256 content hash")
        if not isinstance(manifest.get("snapshot_path"), str) or not manifest.get("snapshot_path"):
            reasons.append("captured source requires immutable snapshot path/reference")
        if retrieval.get("status") != "CAPTURED":
            reasons.append("captured source must report CAPTURED retrieval")

    if state == "CAPTURED_FROZEN" and claims:
        reasons.append("claim extraction requires PARSED_CANDIDATE or later")

    if state in {"PARSED_CANDIDATE", "EVIDENCE_REVIEWED"}:
        for idx, claim in enumerate(claims):
            if not isinstance(claim, dict):
                reasons.append(f"claim[{idx}] must be an object")
                continue
            if claim.get("source_id") != manifest.get("source_id"):
                reasons.append(f"claim[{idx}] source_id mismatch")
            if claim.get("capture_hash") != manifest.get("content_sha256"):
                reasons.append(f"claim[{idx}] capture_hash mismatch")
            if claim.get("authority") != 0:
                reasons.append(f"claim[{idx}] authority must remain 0")
            if claim.get("certification") != "UNVERIFIED":
                reasons.append(f"claim[{idx}] certification must remain UNVERIFIED")
            if claim.get("canonical") is not False:
                reasons.append(f"claim[{idx}] cannot be canonical")
            promotion = claim.get("promotion")
            if promotion in FORBIDDEN_PROMOTIONS:
                reasons.append(f"claim[{idx}] forbidden self-promotion: {promotion}")

    if any(manifest.get(k) for k in ("g3_pass", "g4_pass", "g5_pass", "g6_pass", "world_best", "world_unique")):
        reasons.append("ingestion manifest cannot close external gates or frontier claims")

    return ValidationResult(not reasons, "VALID" if not reasons else "INVALID", reasons)


def manifest_digest(manifest: Dict[str, Any]) -> str:
    payload = dict(manifest)
    payload.pop("manifest_sha256", None)
    return sha256_json(payload)


def verify_manifest_digest(manifest: Dict[str, Any]) -> bool:
    expected = manifest.get("manifest_sha256")
    return _is_sha256(expected) and expected == manifest_digest(manifest)


if __name__ == "__main__":
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser()
    parser.add_argument("manifest")
    args = parser.parse_args()
    data = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    result = validate_manifest(data)
    print(json.dumps({"valid": result.valid, "status": result.status, "reasons": result.reasons}, indent=2))
    raise SystemExit(0 if result.valid else 1)
