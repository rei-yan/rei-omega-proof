#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Tuple

from wuxiang_epistemic_primitives import (
    EvidenceDebt,
    ExternalReceipt,
    MeasurementContext,
    compile_external_challenge as core_compile_external_challenge,
    context_equivalent,
    open_critical_debt as core_open_critical_debt,
    scope_transfer_allowed,
    verify_external_receipt,
)

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
    "COMPARATIVE_DEFEAT",
)


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


def admit_process_claim(claim: ProcessClaim) -> bool:
    return all((
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
    ))


def causal_claim_eligible(claim: ProcessClaim) -> bool:
    return (not claim.causal) or claim.causal_basis in ALLOWED_CAUSAL_BASES


def open_critical_debt(debts: Tuple[EvidenceDebt, ...]) -> bool:
    return core_open_critical_debt(debts, CRITICAL_EXTERNAL_DEBTS)


def compile_external_challenge(
    claim: ProcessClaim,
    candidate_commit: str,
    frozen_input_hash: str,
    hidden_challenge_commitment: str,
) -> dict:
    if not admit_process_claim(claim):
        raise ValueError("PROCESS_CLAIM_NOT_ADMISSIBLE")
    return core_compile_external_challenge(
        claim_id=claim.claim_id,
        claim_scope=claim.claim_scope,
        context=claim.context,
        falsification_conditions=claim.falsification_conditions,
        candidate_commit=candidate_commit,
        frozen_input_hash=frozen_input_hash,
        hidden_challenge_commitment=hidden_challenge_commitment,
    )


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

    renamed = ProcessClaim(**{**claim.__dict__, "claim_id": "PROCESS-CLAIM-RENAMED"})
    assert admit_process_claim(renamed)
    assert renamed.evidence == claim.evidence

    shifted_context = MeasurementContext(
        observer_role=base_context.observer_role,
        instrument="DIFFERENT-INSTRUMENT",
        protocol=base_context.protocol,
        regime=base_context.regime,
    )
    assert not context_equivalent(base_context, shifted_context)
    assert not scope_transfer_allowed(claim.claim_scope, claim.claim_scope, base_context, shifted_context)

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

    expired_context = MeasurementContext(
        observer_role=base_context.observer_role,
        instrument=base_context.instrument,
        protocol=base_context.protocol,
        regime=base_context.regime,
        lease_valid=False,
    )
    assert not scope_transfer_allowed(claim.claim_scope, claim.claim_scope, base_context, expired_context)

    debts = tuple(
        EvidenceDebt(d, "CRITICAL", "OPEN", f"External evidence debt: {d}")
        for d in CRITICAL_EXTERNAL_DEBTS
        if d != "COMPARATIVE_DEFEAT"
    )
    assert open_critical_debt(debts)

    package = compile_external_challenge(
        claim=claim,
        candidate_commit="SYNTHETIC-CANDIDATE-COMMIT",
        frozen_input_hash=sha256(b"synthetic-frozen-input").hexdigest(),
        hidden_challenge_commitment=sha256(b"sealed-synthetic-challenge").hexdigest(),
    )
    assert package["execution_authority"] == 0
    assert package["real_world_actuation_authority"] == 0

    comparative_defeat = EvidenceDebt(
        "COMPARATIVE_DEFEAT",
        "CRITICAL",
        "OPEN",
        "Synthetic frozen competitor beat REI in scoped arena",
    )
    assert open_critical_debt((comparative_defeat,))
    assert reality_gap_decision(claim, (comparative_defeat,), package, None) == "AWAITING_REQUIRED_EXTERNAL_EVIDENCE"

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

    assert reality_gap_decision(claim, debts, package, None) == "AWAITING_REQUIRED_EXTERNAL_EVIDENCE"

    markers = (
        "RELATION_EVENT_PROCESS_ABSTRACTION_READY",
        "OBSERVER_MEASUREMENT_CONTEXT_BINDING_READY",
        "CAUSAL_IDENTIFIABILITY_GATE_READY",
        "DISTRIBUTION_SHIFT_SCOPE_LEAK_DETECTOR_READY",
        "EVIDENCE_DEBT_BLIND_SPOT_LEDGER_READY",
        "EXTERNAL_CHALLENGE_COMPILER_READY",
        "INDEPENDENT_EVIDENCE_RECEIPT_VERIFIER_READY",
        "REALITY_GAP_CLOSURE_ORCHESTRATOR_READY",
        "CORRELATION_ONLY_CANNOT_CLAIM_CAUSALITY",
        "CONTEXT_CHANGE_REQUIRES_REVALIDATION",
        "SCOPE_LEAK_FORCES_ABSTAIN",
        "SYNTHETIC_RECEIPT_IS_NOT_EXTERNAL_EVIDENCE",
        "OPEN_CRITICAL_EVIDENCE_DEBT_PREVENTS_CLAIM_EXPANSION",
        "COMPARATIVE_DEFEAT_BLOCKS_CLAIM_EXPANSION",
        "AWAITING_REAL_EXTERNAL_EVIDENCE",
        "EXTERNAL_GATES_REMAIN_OPEN",
    )
    for marker in markers:
        print(marker)


if __name__ == "__main__":
    main()
