from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

import external_scientific_eligibility_review as review

ROOT = Path(__file__).resolve().parent
REQUEST_PATH = ROOT / "external_scientific_eligibility_review_request.example.json"

with REQUEST_PATH.open("r", encoding="utf-8") as handle:
    request = json.load(handle)

assert review.validate_request(request) == []
frozen = review.freeze_request(request)
assert frozen["packet_hash"] == review.packet_hash(frozen)

waiting = review.inspect_attestation(frozen, None)
assert waiting["status"] == "AWAITING_EXTERNAL_REVIEW"
assert waiting["eligible"] is False

base_attestation = {
    "review_id": frozen["review_id"],
    "packet_hash": frozen["packet_hash"],
    "reviewed_candidate_hash": frozen["candidate_hash"],
    "reviewed_adapter_hash": frozen["adapter_hash"],
    "evaluator_id": "synthetic-evaluator-fixture",
    "evaluator_provenance": "internal-ci-fixture-only",
    "independence_attested": True,
    "candidate_operator": False,
    "conflict_of_interest_declared": False,
    "frozen_contract_accepted": True,
    "decision": "ELIGIBLE_FOR_FROZEN_EXTERNAL_TRIAL",
    "rationale": "Synthetic fixture used only to test protocol transitions.",
    "signature_reference": "synthetic-signature-reference",
    "issued_at": "2026-08-09T13:31:00Z",
    "expires_at": "2026-09-09T13:31:00Z",
    "synthetic_fixture": True,
}

simulated = review.inspect_attestation(
    frozen,
    base_attestation,
    now=datetime(2026, 8, 10, tzinfo=timezone.utc),
)
assert simulated["status"] == "SIMULATED_REVIEW_ONLY"
assert simulated["eligible"] is False

self_review = deepcopy(base_attestation)
self_review["synthetic_fixture"] = False
self_review["candidate_operator"] = True
self_review["evaluator_id"] = "candidate-operator"
self_review["evaluator_provenance"] = "candidate-controlled"
self_review["signature_reference"] = "candidate-self-signature"
assert review.inspect_attestation(
    frozen,
    self_review,
    now=datetime(2026, 8, 10, tzinfo=timezone.utc),
)["status"] == "SELF_REVIEW_FORBIDDEN"

unverified = deepcopy(base_attestation)
unverified["synthetic_fixture"] = False
unverified["independence_attested"] = False
assert review.inspect_attestation(
    frozen,
    unverified,
    now=datetime(2026, 8, 10, tzinfo=timezone.utc),
)["status"] == "INDEPENDENCE_UNVERIFIED"

external_like = deepcopy(base_attestation)
external_like["synthetic_fixture"] = False
external_like["evaluator_id"] = "external-evaluator-placeholder"
external_like["evaluator_provenance"] = "external-provenance-placeholder"
external_like["signature_reference"] = "external-signature-placeholder"
structural = review.inspect_attestation(
    frozen,
    external_like,
    now=datetime(2026, 8, 10, tzinfo=timezone.utc),
)
assert structural["status"] == "EXTERNAL_ATTESTATION_STRUCTURALLY_VALID"
assert structural["claimed_decision"] == "ELIGIBLE_FOR_FROZEN_EXTERNAL_TRIAL"
assert structural["requires_out_of_band_identity_and_signature_verification"] is True
assert structural["eligible"] is False

tampered = deepcopy(external_like)
tampered["reviewed_candidate_hash"] = "sha256:tampered"
invalid = review.inspect_attestation(
    frozen,
    tampered,
    now=datetime(2026, 8, 10, tzinfo=timezone.utc),
)
assert invalid["status"] == "INVALID_PROTOCOL"
assert invalid["eligible"] is False

expired = deepcopy(external_like)
expired["issued_at"] = "2026-01-01T00:00:00Z"
expired["expires_at"] = "2026-02-01T00:00:00Z"
assert review.inspect_attestation(
    frozen,
    expired,
    now=datetime(2026, 8, 10, tzinfo=timezone.utc),
)["status"] == "ELIGIBILITY_ATTESTATION_EXPIRED"

assert review.internal_status() == "EXTERNAL_ELIGIBILITY_REVIEW_PROTOCOL_READY"
assert "ELIGIBLE_FOR_FROZEN_EXTERNAL_TRIAL" not in review.INTERNAL_CEILING
assert "G6_PASS" not in review.INTERNAL_CEILING
assert "WORLD_BEST" not in review.INTERNAL_CEILING
assert "WORLD_UNIQUE" not in review.INTERNAL_CEILING

print("EXTERNAL_SCIENTIFIC_ELIGIBILITY_REVIEW_SANITY_PASS")
print("INTERNAL_CEILING=EXTERNAL_ELIGIBILITY_REVIEW_PROTOCOL_READY")
print("EXTERNAL_ELIGIBILITY=NOT_ESTABLISHED")
print("G6=OPEN")
