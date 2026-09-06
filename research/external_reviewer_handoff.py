from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

import external_scientific_eligibility_review as eligibility

PACKAGE_VERSION = "rei-external-reviewer-handoff-v1"
PACKAGE_READY = "EXTERNAL_REVIEWER_HANDOFF_PACKAGE_READY"

REQUIRED_ROLES = {
    "frontier_eligibility_contract",
    "scientific_adapter_spec",
    "external_review_protocol",
    "review_request",
    "attestation_template",
}

FORBIDDEN_ROLES = {
    "external_attestation",
    "eligibility_certificate",
    "g6_certificate",
    "world_best_certificate",
    "world_unique_certificate",
}

FORBIDDEN_TOP_LEVEL_FIELDS = {
    "eligible",
    "external_eligibility",
    "g6_pass",
    "world_best",
    "world_unique",
    "canonical_promotion",
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_json(value: Any) -> str:
    return sha256_bytes(canonical_json(value).encode("utf-8"))


def file_record(path: Path, role: str, *, root: Path) -> dict[str, str]:
    resolved_root = root.resolve()
    resolved_path = path.resolve()
    try:
        relative = resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError("file_outside_root") from exc

    if role in FORBIDDEN_ROLES:
        raise ValueError(f"forbidden_role:{role}")
    if not resolved_path.is_file():
        raise ValueError(f"missing_file:{relative.as_posix()}")

    return {
        "role": role,
        "path": relative.as_posix(),
        "sha256": sha256_bytes(resolved_path.read_bytes()),
    }


def _manifest_payload(manifest: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in manifest.items() if key != "handoff_hash"}


def handoff_hash(manifest: dict[str, Any]) -> str:
    return sha256_json(_manifest_payload(manifest))


def build_manifest(
    request: dict[str, Any],
    records: Iterable[dict[str, str]],
    *,
    synthetic_fixture: bool,
) -> dict[str, Any]:
    request_errors = eligibility.validate_request(request)
    if request_errors:
        raise ValueError("invalid_review_request:" + ";".join(request_errors))

    frozen_request = eligibility.freeze_request(request)
    normalized_records = sorted((dict(record) for record in records), key=lambda item: (item["role"], item["path"]))

    roles = [record["role"] for record in normalized_records]
    paths = [record["path"] for record in normalized_records]

    missing_roles = sorted(REQUIRED_ROLES.difference(roles))
    if missing_roles:
        raise ValueError("missing_roles:" + ",".join(missing_roles))
    forbidden_roles = sorted(FORBIDDEN_ROLES.intersection(roles))
    if forbidden_roles:
        raise ValueError("forbidden_roles:" + ",".join(forbidden_roles))
    if len(paths) != len(set(paths)):
        raise ValueError("duplicate_paths")
    if len(roles) != len(set(roles)):
        raise ValueError("duplicate_roles")

    manifest: dict[str, Any] = {
        "package_version": PACKAGE_VERSION,
        "status": PACKAGE_READY,
        "review_id": frozen_request["review_id"],
        "arena_id": frozen_request["arena_id"],
        "candidate_hash": frozen_request["candidate_hash"],
        "adapter_hash": frozen_request["adapter_hash"],
        "review_packet_hash": frozen_request["packet_hash"],
        "synthetic_fixture": bool(synthetic_fixture),
        "files": normalized_records,
        "authority": 0,
        "external_eligibility_established": False,
        "g6_established": False,
    }
    manifest["handoff_hash"] = handoff_hash(manifest)
    return manifest


def verify_manifest(
    manifest: dict[str, Any],
    request: dict[str, Any],
    *,
    root: Path | None = None,
) -> list[str]:
    errors: list[str] = []

    if manifest.get("package_version") != PACKAGE_VERSION:
        errors.append("invalid:package_version")
    if manifest.get("status") != PACKAGE_READY:
        errors.append("invalid:status")
    if manifest.get("authority") != 0:
        errors.append("invalid:authority")
    if manifest.get("external_eligibility_established") is not False:
        errors.append("self_certification:external_eligibility")
    if manifest.get("g6_established") is not False:
        errors.append("self_certification:g6")

    for field in FORBIDDEN_TOP_LEVEL_FIELDS:
        if field in manifest:
            errors.append(f"forbidden_field:{field}")

    request_errors = eligibility.validate_request(request)
    if request_errors:
        errors.extend(f"request:{error}" for error in request_errors)
        return errors

    frozen_request = eligibility.freeze_request(request)
    binding_fields = {
        "review_id": frozen_request["review_id"],
        "arena_id": frozen_request["arena_id"],
        "candidate_hash": frozen_request["candidate_hash"],
        "adapter_hash": frozen_request["adapter_hash"],
        "review_packet_hash": frozen_request["packet_hash"],
    }
    for field, expected in binding_fields.items():
        if manifest.get(field) != expected:
            errors.append(f"mismatch:{field}")

    files = manifest.get("files")
    if not isinstance(files, list):
        errors.append("invalid:files")
        return errors

    roles: list[str] = []
    paths: list[str] = []
    for index, record in enumerate(files):
        if not isinstance(record, dict):
            errors.append(f"invalid:file_record:{index}")
            continue
        role = record.get("role")
        path = record.get("path")
        digest = record.get("sha256")
        if not isinstance(role, str) or not role:
            errors.append(f"invalid:file_role:{index}")
            continue
        if not isinstance(path, str) or not path:
            errors.append(f"invalid:file_path:{index}")
            continue
        if not isinstance(digest, str) or len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
            errors.append(f"invalid:file_sha256:{index}")
            continue
        roles.append(role)
        paths.append(path)
        if role in FORBIDDEN_ROLES:
            errors.append(f"forbidden_role:{role}")

        if root is not None:
            resolved_root = root.resolve()
            resolved_path = (resolved_root / path).resolve()
            try:
                resolved_path.relative_to(resolved_root)
            except ValueError:
                errors.append(f"file_outside_root:{path}")
                continue
            if not resolved_path.is_file():
                errors.append(f"missing_file:{path}")
            elif sha256_bytes(resolved_path.read_bytes()) != digest:
                errors.append(f"file_hash_mismatch:{path}")

    missing = sorted(REQUIRED_ROLES.difference(roles))
    if missing:
        errors.append("missing_roles:" + ",".join(missing))
    if len(roles) != len(set(roles)):
        errors.append("duplicate_roles")
    if len(paths) != len(set(paths)):
        errors.append("duplicate_paths")

    expected_handoff_hash = handoff_hash(manifest)
    if manifest.get("handoff_hash") != expected_handoff_hash:
        errors.append("mismatch:handoff_hash")

    return errors


def internal_status() -> str:
    return PACKAGE_READY
