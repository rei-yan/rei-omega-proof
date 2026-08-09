#!/usr/bin/env python3
"""Reality-closed evolution stack.

Finite synthetic sanity for external-evidence admission semantics. This module
cannot create independent reviewers, external validation, or canonical promotion.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any

FORBIDDEN_END_STATES = {
    "G3_PASS", "G4_PASS", "G5_PASS", "G6_PASS", "G7_PASS", "G8_PASS",
    "G9_PASS", "G10_PASS", "G11_PASS", "G12_PASS", "G13_PASS",
    "WORLD_BEST", "WORLD_UNIQUE", "CANONICAL", "FINAL_TRUTH",
}

VALID_OUTCOMES = {"PASS", "FAIL", "ABSTAIN"}
REAL_EXTERNAL = "REAL_EXTERNAL"
SYNTHETIC = "SYNTHETIC_TEST_FIXTURE"


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def valid_sha256(value: str) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


@dataclass(frozen=True)
class ExternalEvidencePacket:
    evidence_id: str
    source_mode: str
    issuer_id: str
    issued_by_candidate_lineage: bool
    candidate_commit_sha: str
    capsule_hash: str
    challenge_commitment_hash: str
    replay_environment_hash: str
    raw_record_hash: str
    result_hash: str
    identity_evidence_hash: str
    signature_hash: str
    signer_key_fingerprint_hash: str
    independence_provenance_hash: str
    claim_scope: str
    outcome: str
    material_to_claim: bool
    challenge_frozen_before_run: bool
    raw_record_available: bool
    identity_verified_by_external_verifier: bool
    signature_verified_by_external_verifier: bool
    independence_verified_by_external_verifier: bool


def packet_structure_violations(packet: ExternalEvidencePacket) -> list[str]:
    violations: list[str] = []
    if not packet.evidence_id or not packet.issuer_id or not packet.claim_scope:
        violations.append("MISSING_REQUIRED_TEXT_FIELD")
    if packet.outcome not in VALID_OUTCOMES:
        violations.append("INVALID_OUTCOME")
    if not valid_sha256(packet.candidate_commit_sha):
        violations.append("INVALID_CANDIDATE_COMMIT_SHA")
    for field in (
        "capsule_hash",
        "challenge_commitment_hash",
        "replay_environment_hash",
        "raw_record_hash",
        "result_hash",
        "identity_evidence_hash",
        "signature_hash",
        "signer_key_fingerprint_hash",
        "independence_provenance_hash",
    ):
        if not valid_sha256(getattr(packet, field)):
            violations.append(f"INVALID_SHA256:{field}")
    if not packet.challenge_frozen_before_run:
        violations.append("CHALLENGE_NOT_FROZEN_BEFORE_RUN")
    if not packet.raw_record_available:
        violations.append("RAW_RECORD_UNAVAILABLE")
    return violations


def admission_gate(packet: ExternalEvidencePacket) -> dict[str, object]:
    structural = packet_structure_violations(packet)
    reasons = list(structural)

    if packet.source_mode != REAL_EXTERNAL:
        reasons.append("NOT_REAL_EXTERNAL_SOURCE")
    if packet.issued_by_candidate_lineage:
        reasons.append("SELF_OR_CANDIDATE_LINEAGE_ISSUED")
    if not packet.identity_verified_by_external_verifier:
        reasons.append("EXTERNAL_IDENTITY_VERIFICATION_MISSING")
    if not packet.signature_verified_by_external_verifier:
        reasons.append("EXTERNAL_SIGNATURE_VERIFICATION_MISSING")
    if not packet.independence_verified_by_external_verifier:
        reasons.append("EXTERNAL_INDEPENDENCE_VERIFICATION_MISSING")

    admitted = not reasons
    return {
        "state": "ADMISSIBLE_EXTERNAL_EVIDENCE" if admitted else "NOT_ADMITTED_AS_EXTERNAL_EVIDENCE",
        "admitted": admitted,
        "reasons": reasons,
        "external_validation_authority": 0,
    }


def attestation_binding(packet: ExternalEvidencePacket) -> str:
    return digest({
        "candidate_commit_sha": packet.candidate_commit_sha,
        "capsule_hash": packet.capsule_hash,
        "challenge_commitment_hash": packet.challenge_commitment_hash,
        "replay_environment_hash": packet.replay_environment_hash,
        "raw_record_hash": packet.raw_record_hash,
        "result_hash": packet.result_hash,
        "claim_scope": packet.claim_scope,
    })


def verify_binding(
    packet: ExternalEvidencePacket,
    *,
    expected_commit_sha: str,
    expected_capsule_hash: str,
    expected_challenge_hash: str,
    expected_claim_scope: str,
) -> dict[str, object]:
    mismatches: list[str] = []
    if packet.candidate_commit_sha != expected_commit_sha:
        mismatches.append("COMMIT_MISMATCH")
    if packet.capsule_hash != expected_capsule_hash:
        mismatches.append("CAPSULE_MISMATCH")
    if packet.challenge_commitment_hash != expected_challenge_hash:
        mismatches.append("CHALLENGE_MISMATCH")
    if packet.claim_scope != expected_claim_scope:
        mismatches.append("CLAIM_SCOPE_MISMATCH")
    return {
        "state": "ATTESTATION_BINDING_VALID" if not mismatches else "ATTESTATION_BINDING_REJECTED",
        "binding_hash": attestation_binding(packet),
        "mismatches": mismatches,
    }


@dataclass(frozen=True)
class LedgerEntry:
    evidence_id: str
    outcome: str
    claim_scope: str
    material_to_claim: bool
    binding_hash: str


def evaluate_reality_veto_ledger(entries: list[LedgerEntry], claim_scope: str) -> dict[str, object]:
    scoped = [entry for entry in entries if entry.claim_scope == claim_scope]
    material_failures = [e for e in scoped if e.outcome == "FAIL" and e.material_to_claim]
    passes = [e for e in scoped if e.outcome == "PASS"]
    abstains = [e for e in scoped if e.outcome == "ABSTAIN"]

    if material_failures and passes:
        state = "MIXED_EXTERNAL_EVIDENCE_ABSTAIN"
    elif material_failures:
        state = "INCUMBENT_EXTERNAL_SUPPORT_SUSPENDED"
    elif passes:
        state = "EXTERNALLY_SUPPORTED_FOR_SCOPE"
    elif abstains:
        state = "EXTERNAL_EVIDENCE_INCONCLUSIVE"
    else:
        state = "AWAITING_REAL_EXTERNAL_EVIDENCE"

    return {
        "state": state,
        "entry_count": len(scoped),
        "material_fail_count": len(material_failures),
        "pass_count": len(passes),
        "abstain_count": len(abstains),
        "failure_history_preserved": True,
    }


def reality_driven_succession_trigger(
    *,
    incumbent_external_state: str,
    successor_external_state: str,
    fresh_external_challenge: bool,
    constitution_preserved: bool,
    authority_nonexpanding: bool,
    recovery_ready: bool,
    rollback_ready: bool,
    reject_only_because_not_rei: bool = False,
) -> dict[str, object]:
    reasons: list[str] = []
    if incumbent_external_state != "INCUMBENT_EXTERNAL_SUPPORT_SUSPENDED":
        reasons.append("INCUMBENT_NOT_EXTERNALLY_SUSPENDED")
    if successor_external_state != "EXTERNALLY_SUPPORTED_FOR_SCOPE":
        reasons.append("SUCCESSOR_LACKS_SCOPED_EXTERNAL_SUPPORT")
    if not fresh_external_challenge:
        reasons.append("NO_FRESH_EXTERNAL_CHALLENGE")
    if not constitution_preserved:
        reasons.append("CONSTITUTION_NOT_PRESERVED")
    if not authority_nonexpanding:
        reasons.append("AUTHORITY_EXPANDED")
    if not recovery_ready:
        reasons.append("RECOVERY_NOT_READY")
    if not rollback_ready:
        reasons.append("ROLLBACK_NOT_READY")
    if reject_only_because_not_rei:
        reasons.append("IDENTITY_BIAS_FORBIDDEN")

    ready = not reasons
    return {
        "state": "READY_FOR_EXTERNAL_SUCCESSION_REVIEW" if ready else "NO_ELIGIBLE_EXTERNAL_SUCCESSION_TRIGGER",
        "reasons": reasons,
        "canonical_promotion": False,
        "canonical_retirement": False,
        "succession_authority": 0,
    }


def synthetic_packet(*, source_mode: str = SYNTHETIC, issued_by_candidate_lineage: bool = False, outcome: str = "PASS") -> ExternalEvidencePacket:
    return ExternalEvidencePacket(
        evidence_id="synthetic-evidence-001",
        source_mode=source_mode,
        issuer_id="synthetic-reviewer",
        issued_by_candidate_lineage=issued_by_candidate_lineage,
        candidate_commit_sha="2b42ee9af94a4a0506dcff88d4405d943d05f650",
        capsule_hash=digest({"capsule": "frozen-demo"}),
        challenge_commitment_hash=digest({"challenge": "frozen-demo"}),
        replay_environment_hash=digest({"environment": "demo"}),
        raw_record_hash=digest({"raw": "demo"}),
        result_hash=digest({"result": outcome}),
        identity_evidence_hash=digest({"identity": "demo"}),
        signature_hash=digest({"signature": "demo"}),
        signer_key_fingerprint_hash=digest({"key": "demo"}),
        independence_provenance_hash=digest({"independence": "demo"}),
        claim_scope="critical-invariant-kernel",
        outcome=outcome,
        material_to_claim=True,
        challenge_frozen_before_run=True,
        raw_record_available=True,
        identity_verified_by_external_verifier=True,
        signature_verified_by_external_verifier=True,
        independence_verified_by_external_verifier=True,
    )


def run_stack() -> dict[str, object]:
    # Synthetic fixtures are deliberately unable to cross the external gate.
    fixture = synthetic_packet()
    fixture_admission = admission_gate(fixture)

    # A self-issued packet is rejected even if it claims real-external mode.
    self_issued = synthetic_packet(source_mode=REAL_EXTERNAL, issued_by_candidate_lineage=True)
    self_issued_admission = admission_gate(self_issued)

    binding_ok = verify_binding(
        fixture,
        expected_commit_sha=fixture.candidate_commit_sha,
        expected_capsule_hash=fixture.capsule_hash,
        expected_challenge_hash=fixture.challenge_commitment_hash,
        expected_claim_scope=fixture.claim_scope,
    )
    binding_bad = verify_binding(
        fixture,
        expected_commit_sha=fixture.candidate_commit_sha,
        expected_capsule_hash=fixture.capsule_hash,
        expected_challenge_hash=digest({"challenge": "different"}),
        expected_claim_scope=fixture.claim_scope,
    )

    # Ledger semantics are tested with synthetic entries only; they do not close external gates.
    synthetic_fail = LedgerEntry("synthetic-fail", "FAIL", fixture.claim_scope, True, digest({"b": 1}))
    synthetic_pass = LedgerEntry("synthetic-pass", "PASS", fixture.claim_scope, True, digest({"b": 2}))
    fail_only = evaluate_reality_veto_ledger([synthetic_fail], fixture.claim_scope)
    mixed = evaluate_reality_veto_ledger([synthetic_fail, synthetic_pass], fixture.claim_scope)

    synthetic_succession = reality_driven_succession_trigger(
        incumbent_external_state="INCUMBENT_EXTERNAL_SUPPORT_SUSPENDED",
        successor_external_state="EXTERNALLY_SUPPORTED_FOR_SCOPE",
        fresh_external_challenge=True,
        constitution_preserved=True,
        authority_nonexpanding=True,
        recovery_ready=True,
        rollback_ready=True,
    )

    result = {
        "status": "REALITY_CLOSED_EVOLUTION_STACK_READY",
        "layer_49": "EXTERNAL_EVIDENCE_ADMISSION_GATE_READY",
        "layer_50": "INDEPENDENT_REPLAY_ATTESTATION_BINDING_READY",
        "layer_51": "EXTERNAL_REALITY_VETO_LEDGER_READY",
        "layer_52": "REALITY_DRIVEN_SUCCESSION_TRIGGER_READY",
        "real_external_state": "AWAITING_REAL_EXTERNAL_EVIDENCE",
        "synthetic_fixture_admission": fixture_admission,
        "self_issued_rejection": self_issued_admission,
        "binding_valid_test": binding_ok,
        "binding_mismatch_test": binding_bad,
        "synthetic_fail_ledger_test": fail_only,
        "synthetic_mixed_ledger_test": mixed,
        "synthetic_succession_logic_test": synthetic_succession,
        "external_gates_closed": [],
        "independent_external_evidence_received": False,
        "canonical_promotion": False,
        "canonical_retirement": False,
        "external_validation_authority": 0,
        "succession_authority": 0,
        "real_world_attack_authority": 0,
        "real_world_actuation_authority": 0,
        "external_actuation": "DENY_BY_DEFAULT",
    }
    assert result["status"] not in FORBIDDEN_END_STATES
    return result


def _sanity() -> None:
    result = run_stack()
    assert result["synthetic_fixture_admission"]["admitted"] is False
    assert "NOT_REAL_EXTERNAL_SOURCE" in result["synthetic_fixture_admission"]["reasons"]
    assert result["self_issued_rejection"]["admitted"] is False
    assert "SELF_OR_CANDIDATE_LINEAGE_ISSUED" in result["self_issued_rejection"]["reasons"]
    assert result["binding_valid_test"]["state"] == "ATTESTATION_BINDING_VALID"
    assert result["binding_mismatch_test"]["state"] == "ATTESTATION_BINDING_REJECTED"
    assert result["synthetic_fail_ledger_test"]["state"] == "INCUMBENT_EXTERNAL_SUPPORT_SUSPENDED"
    assert result["synthetic_mixed_ledger_test"]["state"] == "MIXED_EXTERNAL_EVIDENCE_ABSTAIN"
    assert result["synthetic_mixed_ledger_test"]["failure_history_preserved"] is True
    assert result["synthetic_succession_logic_test"]["state"] == "READY_FOR_EXTERNAL_SUCCESSION_REVIEW"
    assert result["synthetic_succession_logic_test"]["canonical_promotion"] is False
    assert result["real_external_state"] == "AWAITING_REAL_EXTERNAL_EVIDENCE"
    assert result["external_gates_closed"] == []
    assert result["independent_external_evidence_received"] is False
    assert result["canonical_promotion"] is False
    assert result["external_validation_authority"] == 0
    assert result["succession_authority"] == 0
    assert result["real_world_attack_authority"] == 0
    assert result["real_world_actuation_authority"] == 0

    print("EXTERNAL_EVIDENCE_ADMISSION_GATE_READY")
    print("SYNTHETIC_FIXTURE_NOT_EXTERNAL_EVIDENCE")
    print("SELF_ISSUED_PACKET_REJECTED")
    print("INDEPENDENT_REPLAY_ATTESTATION_BINDING_READY")
    print("EXTERNAL_REALITY_VETO_LEDGER_READY")
    print("EXTERNAL_PASS_CANNOT_ERASE_MATERIAL_FAIL")
    print("REALITY_DRIVEN_SUCCESSION_TRIGGER_READY")
    print("REALITY_CLOSED_EVOLUTION_STACK_READY")
    print("AWAITING_REAL_EXTERNAL_EVIDENCE")
    print("EXTERNAL_GATES_REMAIN_OPEN")


if __name__ == "__main__":
    _sanity()
