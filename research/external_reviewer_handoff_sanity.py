from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import external_reviewer_handoff as handoff

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent
REQUEST_PATH = ROOT / "external_scientific_eligibility_review_request.example.json"
TEMPLATE_PATH = ROOT / "external_reviewer_attestation.template.json"

with REQUEST_PATH.open("r", encoding="utf-8") as handle:
    request = json.load(handle)

with TEMPLATE_PATH.open("r", encoding="utf-8") as handle:
    template = json.load(handle)

assert template["template_only"] is True
assert template["decision"] is None
assert template["signature_reference"] is None
assert template["independence_attested"] is None

sources = (
    ("research/FRONTIER_ARENA_ELIGIBILITY_CONTRACT.md", "frontier_eligibility_contract"),
    ("research/SCIENTIFIC_HYPOTHESIS_ARENA_ADAPTER_FORGE.md", "scientific_adapter_spec"),
    ("research/EXTERNAL_SCIENTIFIC_ELIGIBILITY_REVIEW.md", "external_review_protocol"),
    ("research/external_scientific_eligibility_review_request.example.json", "review_request"),
    ("research/external_reviewer_attestation.template.json", "attestation_template"),
)

records = [
    handoff.file_record(REPO_ROOT / path, role, root=REPO_ROOT)
    for path, role in sources
]

manifest = handoff.build_manifest(request, records, synthetic_fixture=True)
assert manifest["status"] == "EXTERNAL_REVIEWER_HANDOFF_PACKAGE_READY"
assert manifest["authority"] == 0
assert manifest["external_eligibility_established"] is False
assert manifest["g6_established"] is False
assert handoff.verify_manifest(manifest, request, root=REPO_ROOT) == []

# A single changed digest breaks both file verification and the package seal.
tampered_file = deepcopy(manifest)
tampered_file["files"][0]["sha256"] = "0" * 64
tamper_errors = handoff.verify_manifest(tampered_file, request, root=REPO_ROOT)
assert any(error.startswith("file_hash_mismatch:") for error in tamper_errors)
assert "mismatch:handoff_hash" in tamper_errors

# Candidate/adapter binding cannot be silently rewritten.
tampered_candidate = deepcopy(manifest)
tampered_candidate["candidate_hash"] = "sha256:changed-candidate"
tampered_candidate["handoff_hash"] = handoff.handoff_hash(tampered_candidate)
assert "mismatch:candidate_hash" in handoff.verify_manifest(
    tampered_candidate, request, root=REPO_ROOT
)

# A candidate-controlled package cannot smuggle an external decision inside.
forged_certificate = deepcopy(manifest)
forged_certificate["external_eligibility"] = "ELIGIBLE_FOR_FROZEN_EXTERNAL_TRIAL"
forged_certificate["handoff_hash"] = handoff.handoff_hash(forged_certificate)
assert "forbidden_field:external_eligibility" in handoff.verify_manifest(
    forged_certificate, request, root=REPO_ROOT
)

# External attestation is forbidden cargo in the candidate-prepared handoff.
forbidden_role = deepcopy(manifest)
forbidden_role["files"][0]["role"] = "external_attestation"
forbidden_role["handoff_hash"] = handoff.handoff_hash(forbidden_role)
forbidden_errors = handoff.verify_manifest(forbidden_role, request, root=REPO_ROOT)
assert "forbidden_role:external_attestation" in forbidden_errors
assert any(error.startswith("missing_roles:") for error in forbidden_errors)

# The package can be complete while eligibility remains deliberately false.
assert handoff.internal_status() == "EXTERNAL_REVIEWER_HANDOFF_PACKAGE_READY"
assert "external_attestation" not in {record["role"] for record in manifest["files"]}
assert "eligibility_certificate" not in {record["role"] for record in manifest["files"]}

print("EXTERNAL_REVIEWER_HANDOFF_SANITY_PASS")
print("INTERNAL_CEILING=EXTERNAL_REVIEWER_HANDOFF_PACKAGE_READY")
print("EXTERNAL_REVIEWER=NOT_ESTABLISHED")
print("EXTERNAL_ELIGIBILITY=NOT_ESTABLISHED")
print("G6=OPEN")
