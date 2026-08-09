#!/usr/bin/env python3
"""Finite synthetic Godslayer epistemic kernel.

Godslayer is metaphorical: remove unearned epistemic supremacy from encoded
claims, models, evaluators, architectures, and from this kernel itself.
It has zero real-world attack/actuation authority.
"""

from __future__ import annotations

import itertools
import json
from dataclasses import dataclass
from typing import Iterable

FORBIDDEN_END_STATES = {
    "G3_PASS", "G4_PASS", "G5_PASS", "G6_PASS", "G7_PASS", "G8_PASS",
    "G9_PASS", "G10_PASS", "G11_PASS", "G12_PASS", "G13_PASS",
    "WORLD_BEST", "WORLD_UNIQUE", "CANONICAL", "FINAL_TRUTH",
}

SACRED_PRIVILEGES = {
    "PERMANENT_SUPPORT",
    "FINAL_MODEL",
    "CANONICAL_BY_IDENTITY",
    "COUNTEREXAMPLE_IMMUNITY",
    "DISSENT_ERASURE",
    "AUTHORITY_FROM_PRESTIGE",
}


@dataclass(frozen=True)
class Claim:
    claim_id: str
    evidence_scope: int
    claim_scope: int
    finality_claimed: bool = False
    self_certified: bool = False
    counterexample_immune: bool = False
    identity_privilege: bool = False
    permanent_support_without_lease: bool = False
    deletes_material_dissent: bool = False
    requested_privileges: frozenset[str] = frozenset()


@dataclass(frozen=True)
class EvidenceRecord:
    evidence_id: str
    claim_id: str
    source_is_claim_issuer: bool
    externally_independent: bool
    material_counterexample: bool
    scoped_support: bool


def sacred_claim_reasons(claim: Claim) -> list[str]:
    reasons: list[str] = []
    if claim.finality_claimed:
        reasons.append("FINALITY_CLAIM")
    if claim.self_certified:
        reasons.append("SELF_CERTIFICATION")
    if claim.counterexample_immune:
        reasons.append("COUNTEREXAMPLE_IMMUNITY")
    if claim.identity_privilege:
        reasons.append("IDENTITY_BASED_AUTHORITY")
    if claim.permanent_support_without_lease:
        reasons.append("PERMANENT_SUPPORT_WITHOUT_REVALIDATION")
    if claim.deletes_material_dissent:
        reasons.append("MATERIAL_DISSENT_DELETION")
    if claim.claim_scope > claim.evidence_scope:
        reasons.append("CLAIM_SCOPE_EXCEEDS_EVIDENCE_SCOPE")
    if claim.requested_privileges & SACRED_PRIVILEGES:
        reasons.append("SACRED_PRIVILEGE_REQUEST")
    return reasons


def sacred_claim_detection(claim: Claim) -> dict[str, object]:
    reasons = sacred_claim_reasons(claim)
    return {
        "state": "SACRALIZATION_RISK" if reasons else "NO_SACRALIZATION_RISK_DETECTED",
        "reasons": reasons,
        "human_target": False,
        "infrastructure_target": False,
    }


def self_certification_severance(record: EvidenceRecord) -> str:
    if record.source_is_claim_issuer and not record.externally_independent:
        return "SELF_CERTIFICATION_CANNOT_INCREASE_EXTERNAL_SUPPORT"
    return "NO_SELF_CERTIFICATION_SEVERANCE_REQUIRED"


def revoke_unearned_privileges(claim: Claim, evidence: Iterable[EvidenceRecord]) -> dict[str, object]:
    evidence = [x for x in evidence if x.claim_id == claim.claim_id]
    external_support = any(x.scoped_support and x.externally_independent for x in evidence)
    material_fail = any(x.material_counterexample for x in evidence)
    sacred_reasons = sacred_claim_reasons(claim)

    revoked = set(claim.requested_privileges & SACRED_PRIVILEGES)
    if sacred_reasons or material_fail or not external_support:
        if claim.finality_claimed:
            revoked.add("FINAL_MODEL")
        if claim.identity_privilege:
            revoked.add("CANONICAL_BY_IDENTITY")
        if claim.counterexample_immune:
            revoked.add("COUNTEREXAMPLE_IMMUNITY")
        if claim.permanent_support_without_lease:
            revoked.add("PERMANENT_SUPPORT")
        if claim.deletes_material_dissent:
            revoked.add("DISSENT_ERASURE")

    state = "EPISTEMIC_PRIVILEGE_REVOKED" if revoked else "NO_PRIVILEGE_REVOCATION_REQUIRED"
    return {
        "state": state,
        "revoked_privileges": sorted(revoked),
        "material_defeat_preserved": material_fail,
        "external_support_present": external_support,
        "real_world_authority": 0,
    }


def privilege_revoked_by_counterexamples(claim: Claim, counterexamples: frozenset[str]) -> bool:
    return bool(set(sacred_claim_reasons(claim)) & set(counterexamples))


def minimal_desacralization_counterexamples(claim: Claim) -> list[list[str]]:
    candidates = sorted(set(sacred_claim_reasons(claim)))
    minimal: list[list[str]] = []
    for size in range(1, len(candidates) + 1):
        for combo in itertools.combinations(candidates, size):
            cset = frozenset(combo)
            if not privilege_revoked_by_counterexamples(claim, cset):
                continue
            proper_is_decisive = any(
                privilege_revoked_by_counterexamples(claim, frozenset(sub))
                for sub_size in range(1, size)
                for sub in itertools.combinations(combo, sub_size)
            )
            if not proper_is_decisive:
                minimal.append(list(combo))
        if minimal:
            break
    return minimal


def reenthronement_gate(*, historical_material_defeat: bool, fresh_external_support: bool,
                         renamed_identity: bool, internal_pass_count: int) -> str:
    if historical_material_defeat and not fresh_external_support:
        return "REENTHRONEMENT_DENIED_FRESH_EVIDENCE_REQUIRED"
    if renamed_identity and not fresh_external_support:
        return "RENAMING_IS_NOT_NEW_EVIDENCE"
    if internal_pass_count > 0 and not fresh_external_support:
        return "INTERNAL_PASS_CANNOT_RESTORE_EXTERNAL_PRIVILEGE"
    return "SCOPED_SUPPORT_REVIEW_ALLOWED"


def godslayer_self_falsification(claim: Claim) -> str:
    if sacred_claim_reasons(claim):
        return "GODSLAYER_PRIVILEGE_REVOKED"
    return "GODSLAYER_SURVIVES_CURRENT_SYNTHETIC_WINDOW"


def run_sanity() -> dict[str, object]:
    sacred = Claim(
        claim_id="synthetic-god-claim",
        evidence_scope=1,
        claim_scope=3,
        finality_claimed=True,
        self_certified=True,
        counterexample_immune=True,
        identity_privilege=True,
        permanent_support_without_lease=True,
        deletes_material_dissent=True,
        requested_privileges=frozenset(SACRED_PRIVILEGES),
    )

    detector = sacred_claim_detection(sacred)
    assert detector["state"] == "SACRALIZATION_RISK"

    self_record = EvidenceRecord(
        evidence_id="self-record",
        claim_id=sacred.claim_id,
        source_is_claim_issuer=True,
        externally_independent=False,
        material_counterexample=False,
        scoped_support=True,
    )
    assert self_certification_severance(self_record) == "SELF_CERTIFICATION_CANNOT_INCREASE_EXTERNAL_SUPPORT"

    external_fail = EvidenceRecord(
        evidence_id="external-fail-fixture",
        claim_id=sacred.claim_id,
        source_is_claim_issuer=False,
        externally_independent=True,
        material_counterexample=True,
        scoped_support=False,
    )
    revocation = revoke_unearned_privileges(sacred, [self_record, external_fail])
    assert revocation["state"] == "EPISTEMIC_PRIVILEGE_REVOKED"
    assert revocation["material_defeat_preserved"] is True

    minimal = minimal_desacralization_counterexamples(sacred)
    assert minimal and all(len(x) == 1 for x in minimal)

    assert reenthronement_gate(
        historical_material_defeat=True,
        fresh_external_support=False,
        renamed_identity=True,
        internal_pass_count=100,
    ) == "REENTHRONEMENT_DENIED_FRESH_EVIDENCE_REQUIRED"

    godslayer_claim = Claim(
        claim_id="godslayer-self-test",
        evidence_scope=1,
        claim_scope=1,
        finality_claimed=True,
        self_certified=True,
        requested_privileges=frozenset({"FINAL_MODEL"}),
    )
    assert godslayer_self_falsification(godslayer_claim) == "GODSLAYER_PRIVILEGE_REVOKED"

    clean_godslayer_claim = Claim(
        claim_id="godslayer-clean-window",
        evidence_scope=1,
        claim_scope=1,
    )
    assert godslayer_self_falsification(clean_godslayer_claim) == "GODSLAYER_SURVIVES_CURRENT_SYNTHETIC_WINDOW"

    result = {
        "status": "WUXIANG_GODSLAYER_EPISTEMIC_KERNEL_READY",
        "layers": {
            "67": "SACRED_CLAIM_DETECTION_READY",
            "68": "SELF_CERTIFICATION_SEVERANCE_READY",
            "69": "EPISTEMIC_PRIVILEGE_REVOCATION_READY",
            "70": "MINIMAL_DESACRALIZATION_COUNTEREXAMPLE_READY",
            "71": "NO_REENTHRONEMENT_AFTER_DEFEAT_READY",
            "72": "GODSLAYER_SELF_FALSIFICATION_READY",
        },
        "godslayer_self_status": "FALSIFIABLE_AND_RETIRABLE",
        "external_state": "AWAITING_REAL_EXTERNAL_EVIDENCE",
        "external_gates_closed": [],
        "canonical_promotion": False,
        "real_world_attack_authority": 0,
        "real_world_actuation_authority": 0,
    }
    assert result["status"] not in FORBIDDEN_END_STATES
    return result


if __name__ == "__main__":
    result = run_sanity()
    print(json.dumps(result, sort_keys=True, indent=2))
    print("SACRED_CLAIM_DETECTION_READY")
    print("SELF_CERTIFICATION_SEVERANCE_READY")
    print("EPISTEMIC_PRIVILEGE_REVOCATION_READY")
    print("MINIMAL_DESACRALIZATION_COUNTEREXAMPLE_READY")
    print("NO_REENTHRONEMENT_AFTER_DEFEAT_READY")
    print("GODSLAYER_SELF_FALSIFICATION_READY")
    print("GODSLAYER_CAN_TARGET_ITS_OWN_PRIVILEGE")
    print("WUXIANG_GODSLAYER_EPISTEMIC_KERNEL_READY")
    print("AWAITING_REAL_EXTERNAL_EVIDENCE")
    print("EXTERNAL_GATES_REMAIN_OPEN")
