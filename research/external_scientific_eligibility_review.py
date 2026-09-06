from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

PROTOCOL_VERSION = "rei-external-scientific-eligibility-review-v1"

REQUEST_REQUIRED = (
    "protocol_version",
    "review_id",
    "arena_id",
    "candidate_id",
    "candidate_hash",
    "adapter_hash",
    "task_definition_hash",
    "input_schema_hash",
    "output_schema_hash",
    "metric_hash",
    "budget_envelope_hash",
    "tool_policy_hash",
    "human_assistance_policy_hash",
    "retry_policy_hash",
    "abstention_policy_hash",
    "evaluator_interface_hash",
    "provenance_hash",
    "review_cutoff",
)

ATTESTATION_REQUIRED = (
    "review_id",
    "packet_hash",
    "reviewed_candidate_hash",
    "reviewed_adapter_hash",
    "evaluator_id",
    "evaluator_provenance",
    "independence_attested",
    "candidate_operator",
    "conflict_of_interest_declared",
    "frozen_contract_accepted",
    "decision",
    "rationale",
    "signature_reference",
    "issued_at",
    "expires_at",
    "synthetic_fixture",
)

ALLOWED_DECISIONS = {
    "ELIGIBLE_FOR_FROZEN_EXTERNAL_TRIAL",
    "NOT_ELIGIBLE",
    "ABSTAIN",
    "INVALID_PROTOCOL",
}

INTERNAL_CEILING = {
    "EXTERNAL_ELIGIBILITY_REVIEW_PROTOCOL_READY",
    "AWAITING_EXTERNAL_REVIEW",
    "EXTERNAL_ATTESTATION_STRUCTURALLY_VALID",
}

FORBIDDEN_INTERNAL_CERTIFICATES = {
    "ELIGIBLE_FOR_FROZEN_EXTERNAL_TRIAL",
    "G6_PASS",
    "WORLD_BEST",
    "WORLD_UNIQUE",
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _parse_utc(value: str) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def validate_request(request: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in REQUEST_REQUIRED:
        if field not in request:
            errors.append(f"missing:{field}")
    if errors:
        return errors

    if request["protocol_version"] != PROTOCOL_VERSION:
        errors.append("invalid:protocol_version")
    for field in REQUEST_REQUIRED:
        if field == "protocol_version":
            continue
        if not _nonempty_string(request[field]):
            errors.append(f"invalid:{field}")

    if _parse_utc(request["review_cutoff"]) is None:
        errors.append("invalid:review_cutoff")

    if "packet_hash" in request:
        expected = packet_hash(request)
        if request["packet_hash"] != expected:
            errors.append("invalid:packet_hash")

    return errors


def packet_payload(request: dict[str, Any]) -> dict[str, Any]:
    return {key: request[key] for key in REQUEST_REQUIRED if key in request}


def packet_hash(request: dict[str, Any]) -> str:
    return sha256_json(packet_payload(request))


def freeze_request(request: dict[str, Any]) -> dict[str, Any]:
    errors = validate_request(request)
    if errors:
        raise ValueError(";".join(errors))
    frozen = dict(packet_payload(request))
    frozen["packet_hash"] = packet_hash(request)
    return frozen


def validate_attestation(attestation: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in ATTESTATION_REQUIRED:
        if field not in attestation:
            errors.append(f"missing:{field}")
    if errors:
        return errors

    string_fields = (
        "review_id",
        "packet_hash",
        "reviewed_candidate_hash",
        "reviewed_adapter_hash",
        "evaluator_id",
        "evaluator_provenance",
        "decision",
        "rationale",
        "signature_reference",
        "issued_at",
        "expires_at",
    )
    for field in string_fields:
        if not _nonempty_string(attestation[field]):
            errors.append(f"invalid:{field}")

    bool_fields = (
        "independence_attested",
        "candidate_operator",
        "conflict_of_interest_declared",
        "frozen_contract_accepted",
        "synthetic_fixture",
    )
    for field in bool_fields:
        if not isinstance(attestation[field], bool):
            errors.append(f"invalid:{field}")

    if attestation["decision"] not in ALLOWED_DECISIONS:
        errors.append("invalid:decision")

    issued = _parse_utc(attestation["issued_at"])
    expires = _parse_utc(attestation["expires_at"])
    if issued is None:
        errors.append("invalid:issued_at")
    if expires is None:
        errors.append("invalid:expires_at")
    if issued is not None and expires is not None and expires <= issued:
        errors.append("invalid:expiry_order")

    return errors


def inspect_attestation(
    request: dict[str, Any],
    attestation: dict[str, Any] | None,
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    request_errors = validate_request(request)
    if request_errors:
        return {"status": "INVALID_PROTOCOL", "errors": request_errors, "eligible": False}

    frozen_hash = request.get("packet_hash") or packet_hash(request)

    if attestation is None:
        return {
            "status": "AWAITING_EXTERNAL_REVIEW",
            "packet_hash": frozen_hash,
            "eligible": False,
        }

    attestation_errors = validate_attestation(attestation)
    if attestation_errors:
        return {"status": "INVALID_PROTOCOL", "errors": attestation_errors, "eligible": False}

    if attestation["review_id"] != request["review_id"]:
        return {"status": "INVALID_PROTOCOL", "errors": ["mismatch:review_id"], "eligible": False}
    if attestation["packet_hash"] != frozen_hash:
        return {"status": "INVALID_PROTOCOL", "errors": ["mismatch:packet_hash"], "eligible": False}
    if attestation["reviewed_candidate_hash"] != request["candidate_hash"]:
        return {"status": "INVALID_PROTOCOL", "errors": ["mismatch:candidate_hash"], "eligible": False}
    if attestation["reviewed_adapter_hash"] != request["adapter_hash"]:
        return {"status": "INVALID_PROTOCOL", "errors": ["mismatch:adapter_hash"], "eligible": False}

    if attestation["synthetic_fixture"]:
        return {
            "status": "SIMULATED_REVIEW_ONLY",
            "claimed_decision": attestation["decision"],
            "eligible": False,
        }

    if attestation["candidate_operator"]:
        return {"status": "SELF_REVIEW_FORBIDDEN", "eligible": False}
    if not attestation["independence_attested"]:
        return {"status": "INDEPENDENCE_UNVERIFIED", "eligible": False}
    if attestation["conflict_of_interest_declared"]:
        return {"status": "CONFLICT_REQUIRES_EXTERNAL_RESOLUTION", "eligible": False}
    if not attestation["frozen_contract_accepted"]:
        return {"status": "EXTERNAL_REVIEW_REJECTS_CONTRACT", "eligible": False}

    current = now or datetime.now(timezone.utc)
    expires = _parse_utc(attestation["expires_at"])
    assert expires is not None
    if current.astimezone(timezone.utc) >= expires:
        return {"status": "ELIGIBILITY_ATTESTATION_EXPIRED", "eligible": False}

    if attestation["decision"] == "NOT_ELIGIBLE":
        return {"status": "EXTERNAL_ATTESTATION_REJECTS_ELIGIBILITY", "eligible": False}
    if attestation["decision"] == "ABSTAIN":
        return {"status": "EXTERNAL_ATTESTATION_ABSTAINS", "eligible": False}
    if attestation["decision"] == "INVALID_PROTOCOL":
        return {"status": "EXTERNAL_ATTESTATION_INVALIDATES_PROTOCOL", "eligible": False}

    # Deliberately do not emit ELIGIBLE here. This repository can validate
    # structure, hash binding, and self-review vetoes, but cannot prove that
    # an evaluator identity or signature is genuinely independent.
    return {
        "status": "EXTERNAL_ATTESTATION_STRUCTURALLY_VALID",
        "claimed_decision": attestation["decision"],
        "requires_out_of_band_identity_and_signature_verification": True,
        "eligible": False,
    }


def internal_status() -> str:
    return "EXTERNAL_ELIGIBILITY_REVIEW_PROTOCOL_READY"
