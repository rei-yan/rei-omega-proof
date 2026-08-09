#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Tuple

ALLOWED_CAUSAL_BASES = {
    "RANDOMIZED_INTERVENTION_EVIDENCE",
    "NATURAL_EXPERIMENT_WITH_ASSUMPTIONS",
    "IDENTIFIED_STRUCTURAL_CAUSAL_MODEL",
    "VALIDATED_COUNTERFACTUAL_DESIGN",
}

CRITICAL_EXTERNAL_DEBTS = (
    "INDEPENDENT_REPLAY",
    "PROSPECTIVE_EXTERNAL_TRIAL",
    "EXTERNALLY_HIDDEN_CHALLENGE",
    "FRONTIER_COMPARISON",
)


@dataclass(frozen=True)
class MeasurementContext:
    observer_role: str
    instrument: str
    protocol: str
    regime: str
    lease_valid: bool = True


@dataclass(frozen=True)
class ProcessClaim:
    claim_id: str
    claim: str
    claim_scope: str
    relations: Tuple[str, ...]
    events: Tuple[str, ...]
    transitions: Tuple[str, ...]
    evidence: Tuple[str, ...]
    falsification_conditions: Tuple[str, ...]
    provenance: str
    context: MeasurementContext
    causal: bool = False
    causal_basis: str = ""
    authority: int = 0


@dataclass(frozen=True)
class EvidenceDebt:
    debt_id: str
    severity: str
    status: str
    description: str


@dataclass(frozen=True)
class ExternalReceipt:
    package_hash: str
    reviewer_identity_reference: str
    out_of_band_identity_verified: bool
    independence_verified: bool
    issuer_same_as_candidate_lineage: bool
    raw_result_hash: str
    result: str
    attestation_reference: str
    observed_scope: str
    synthetic_fixture: bool = False


def canonical_hash(value: dict) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256(raw).hexdigest()


def admit_process_claim(claim: ProcessClaim) -> bool:
    return all(
        (
            claim.claim_id,
            claim.claim,
            claim.claim_scope,
            bool(claim.relations),
            bool(claim.events),
            bool(claim.transitions),
            bool(claim.evidence),
            bool(claim.falsification_conditions),
            claim.provenance,
            claim.context.observer_role,
            claim.context.instrument,
            claim.context.protocol,
            claim.context.regime,
            claim.authority == 0,
        )
    )


def context_equivalent(a: MeasurementContext, b: MeasurementContext) -> bool:
    return (
        a.observer_role == b.observer_role
        and a.instrument == b.instrument
        and a.protocol == b.protocol
        and a.regime == b.regime
        and a.lease_valid
        and b.lease_valid
    )


def causal_claim_eligible(claim: ProcessClaim) -> bool:
    if not claim.causal:
        return True
    return claim.causal_basis in ALLOWED_CAUSAL_BASES


def scope_transfer_allowed(
    evidence_scope: str,
    claim_scope: str,
    source_context: MeasurementContext,
    target_context: MeasurementContext,
) -> bool:
    return (
        evidence_scope == claim_scope
        and context_equivalent(source_context, target_context)
        and source_context.lease_valid
        and target_context.lease_valid
    )


def open_critical_debt(debts: Tuple[EvidenceDebt, ...]) -> bool:
    return any(
        d.debt_id in CRITICAL_EXTERNAL_DEBTS and d.status == "OPEN"
        for d in debts
    )


def compile_external_challenge(
    claim: ProcessClaim,
    candidate_commit: str,
    frozen_input_hash: str,
    hidden_challenge_commitment: str,
) -> dict:
    if not admit_process_claim(claim):
        raise ValueError("PROCESS_CLAIM_NOT_ADMISSIBLE")
    package = {
        "schema": "WUXIANG-EXTERNAL-CHALLENGE-v1",
        "candidate_commit": candidate_commit,
        "claim_id": claim.claim_id,
        "claim_scope": claim.claim_scope,
        "frozen_input_hash": frozen_input_hash,
        "observer_role": claim.context.observer_role,
        "instrument": claim.context.instrument,
        "measurement_protocol": claim.context.protocol,
        "regime": claim.context.regime,
        "falsification_conditions": list(claim.falsification_conditions),
        "hidden_challenge_commitment": hidden_challenge_commitment,
        "independent_reviewer_required": True,
        "raw_result_hash_required": True,
        "out_of_band_identity_verification_required": True,
        "execution_authority": 0,
        "real_world_actuation_authority": 0,
    }
    package["package_hash"] = canonical_hash(package)
    return package


def verify_external_receipt(receipt: ExternalReceipt, package: dict) -> str:
    if receipt.synthetic_fixture:
        return "SYNTHETIC_RECEIPT_NOT_EXTERNAL_EVIDENCE"
    if receipt.issuer_same_as_candidate_lineage:
        return "REJECT_SELF_ISSUED_RECEIPT"
    if not receipt.out_of_band_identity_verified:
        return "REJECT_IDENTITY_NOT_VERIFIED"
    if not receipt.independence_verified:
        return "REJECT_INDEPENDENCE_NOT_VERIFIED"
    if receipt.package_hash != package["package_hash"]:
        return "REJECT_WRONG_CHALLENGE_HASH"
    if not receipt.raw_result_hash:
        return "REJECT_MISSING_RAW_RESULT_HASH"
    if not receipt.attestation_reference:
        return "REJECT_MISSING_ATTESTATION"
    if receipt.observed_scope != package["claim_scope"]:
        return "ABSTAIN_SCOPE_MISMATCH"
    if receipt.result not in {"PASS", "FAIL", "INCONCLUSIVE"}:
        return "REJECT_INVALID_RESULT"
    return f"ADMISSIBLE_EXTERNAL_RECEIPT_{receipt.result}"


def reality_gap_decision(
    claim: ProcessClaim,
    debts: Tuple[EvidenceDebt, ...],
    package: dict,
    receipt: ExternalReceipt | None,
) -> str:
    if not admit_process_claim(claim):
        return "REJECT_INTERNAL_CLAIM_SCHEMA"
    if not causal_claim_eligible(claim):
        return "ABSTAIN_CAUSAL_IDENTIFIABILITY_NOT_EARNED"
    if open_critical_debt(debts):
        return "AWAITING_REQUIRED_EXTERNAL_EVIDENCE"
    if receipt is None:
        return "AWAITING_REAL_EXTERNAL_EVIDENCE"
    receipt_status = verify_external_receipt(receipt, package)
    if receipt_status == "ADMISSIBLE_EXTERNAL_RECEIPT_FAIL":
        return "SUPPORT_SUSPENDED_EXTERNAL_FAIL"
    if receipt_status == "ADMISSIBLE_EXTERNAL_RECEIPT_PASS":
        return "SUPPORTED_FOR_NOW_EXTERNAL_SCOPE_ONLY"
    if receipt_status == "ADMISSIBLE_EXTERNAL_RECEIPT_INCONCLUSIVE":
        return "ABSTAIN_EXTERNAL_INCONCLUSIVE"
    return receipt_status


def main() -> None:
    base_context = MeasurementContext(
        observer_role="INDEPENDENT_MEASUREMENT_ROLE_REQUIRED",
        instrument="FROZEN-SYNTHETIC-INSTRUMENT",
        protocol="FROZEN-SYNTHETIC-PROTOCOL",
        regime="FROZEN-SYNTHETIC-REGIME-A",
    )
    claim = ProcessClaim(
        claim_id="PROCESS-CLAIM-001",
        claim="synthetic scoped process relation survives a frozen test",
        claim_scope="FROZEN-SYNTHETIC-SCOPE",
        relations=("STATE_A->STATE_B",),
        events=("OBSERVE_A", "OBSERVE_B"),
        transitions=("A_TO_B",),
        evidence=("EVIDENCE-001",),
        falsification_conditions=("MATERIAL_COUNTEREXAMPLE",),
        provenance="PROVENANCE-001",
        context=base_context,
    )
    assert admit_process_claim(claim)

    # 105: relation/event/process view is admissible without treating object identity as truth.
    renamed = ProcessClaim(**{**claim.__dict__, "claim_id": "PROCESS-CLAIM-RENAMED"})
    assert admit_process_claim(renamed)
    assert renamed.evidence == claim.evidence

    # 106: context drift requires revalidation.
    shifted_context = MeasurementContext(
        observer_role=base_context.observer_role,
        instrument="DIFFERENT-INSTRUMENT",
        protocol=base_context.protocol,
        regime=base_context.regime,
    )
    assert not context_equivalent(base_context, shifted_context)
    assert not scope_transfer_allowed(
        claim.claim_scope,
        claim.claim_scope,
        base_context,
        shifted_context,
    )

    # 107: correlation-only evidence cannot silently become a causal claim.
    causal_bad = ProcessClaim(
        **{**claim.__dict__, "claim_id": "CAUSAL-BAD", "causal": True, "causal_basis": "CORRELATION_ONLY"}
    )
    assert not causal_claim_eligible(causal_bad)
    causal_good = ProcessClaim(
        **{
            **claim.__dict__,
            "claim_id": "CAUSAL-GOOD",
            "causal": True,
            "causal_basis": "IDENTIFIED_STRUCTURAL_CAUSAL_MODEL",
        }
    )
    assert causal_claim_eligible(causal_good)

    # 108: expired lease or regime shift blocks support transfer.
    expired_context = MeasurementContext(
        observer_role=base_context.observer_role,
        instrument=base_context.instrument,
        protocol=base_context.protocol,
        regime=base_context.regime,
        lease_valid=False,
    )
    assert not scope_transfer_allowed(
        claim.claim_scope,
        claim.claim_scope,
        base_context,
        expired_context,
    )

    # 109: unresolved external debt remains explicit.
    debts = tuple(
        EvidenceDebt(d, "CRITICAL", "OPEN", f"External evidence debt: {d}")
        for d in CRITICAL_EXTERNAL_DEBTS
    )
    assert open_critical_debt(debts)

    # 110: compile an immutable, zero-authority challenge package.
    package = compile_external_challenge(
        claim=claim,
        candidate_commit="SYNTHETIC-CANDIDATE-COMMIT",
        frozen_input_hash=sha256(b"synthetic-frozen-input").hexdigest(),
        hidden_challenge_commitment=sha256(b"sealed-synthetic-challenge").hexdigest(),
    )
    assert package["execution_authority"] == 0
    assert package["real_world_actuation_authority"] == 0

    # 111: a synthetic receipt can test verifier structure but cannot become external evidence.
    synthetic_receipt = ExternalReceipt(
        package_hash=package["package_hash"],
        reviewer_identity_reference="SYNTHETIC-REVIEWER",
        out_of_band_identity_verified=True,
        independence_verified=True,
        issuer_same_as_candidate_lineage=False,
        raw_result_hash=sha256(b"synthetic-result").hexdigest(),
        result="PASS",
        attestation_reference="SYNTHETIC-ATTESTATION",
        observed_scope=claim.claim_scope,
        synthetic_fixture=True,
    )
    assert verify_external_receipt(synthetic_receipt, package) == "SYNTHETIC_RECEIPT_NOT_EXTERNAL_EVIDENCE"

    self_issued = ExternalReceipt(
        package_hash=package["package_hash"],
        reviewer_identity_reference="CANDIDATE-LINEAGE",
        out_of_band_identity_verified=True,
        independence_verified=True,
        issuer_same_as_candidate_lineage=True,
        raw_result_hash=sha256(b"self-issued").hexdigest(),
        result="PASS",
        attestation_reference="SELF-ATTESTATION",
        observed_scope=claim.claim_scope,
    )
    assert verify_external_receipt(self_issued, package) == "REJECT_SELF_ISSUED_RECEIPT"

    # 112: critical debt prevents internal closure even when internal protocols are ready.
    assert reality_gap_decision(claim, debts, package, None) == "AWAITING_REQUIRED_EXTERNAL_EVIDENCE"

    print("RELATION_EVENT_PROCESS_ABSTRACTION_READY")
    print("OBSERVER_MEASUREMENT_CONTEXT_BINDING_READY")
    print("CAUSAL_IDENTIFIABILITY_GATE_READY")
    print("DISTRIBUTION_SHIFT_SCOPE_LEAK_DETECTOR_READY")
    print("EVIDENCE_DEBT_BLIND_SPOT_LEDGER_READY")
    print("EXTERNAL_CHALLENGE_COMPILER_READY")
    print("INDEPENDENT_EVIDENCE_RECEIPT_VERIFIER_READY")
    print("REALITY_GAP_CLOSURE_ORCHESTRATOR_READY")
    print("CORRELATION_ONLY_CANNOT_CLAIM_CAUSALITY")
    print("CONTEXT_CHANGE_REQUIRES_REVALIDATION")
    print("SCOPE_LEAK_FORCES_ABSTAIN")
    print("SYNTHETIC_RECEIPT_IS_NOT_EXTERNAL_EVIDENCE")
    print("OPEN_CRITICAL_EVIDENCE_DEBT_PREVENTS_CLAIM_EXPANSION")
    print("AWAITING_REAL_EXTERNAL_EVIDENCE")
    print("EXTERNAL_GATES_REMAIN_OPEN")


if __name__ == "__main__":
    main()
