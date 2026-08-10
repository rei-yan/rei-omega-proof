#!/usr/bin/env python3
"""Open-horizon reality revalidation kernel.

Finite synthetic sanity for evidence leases, scope containment, contradiction
preservation, reviewer-lineage diversity, prospectively frozen challenges,
retirement triggers, and rolling revalidation. It cannot create genuine external
reviewers or close external gates.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any, Iterable

FORBIDDEN_END_STATES = {
    "G3_PASS", "G4_PASS", "G5_PASS", "G6_PASS", "G7_PASS", "G8_PASS",
    "G9_PASS", "G10_PASS", "G11_PASS", "G12_PASS", "G13_PASS",
    "WORLD_BEST", "WORLD_UNIQUE", "CANONICAL", "FINAL_TRUTH",
}
VALID_OUTCOMES = {"PASS", "FAIL", "ABSTAIN"}
VALID_SUPPORT_STATES = {
    "SUPPORTED_FOR_NOW", "SUSPENDED", "MIXED_EXTERNAL_EVIDENCE_ABSTAIN",
    "EXPIRED", "INCONCLUSIVE", "AWAITING_REAL_EXTERNAL_EVIDENCE",
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class Scope:
    domain: str
    task: str
    population: str
    regime: str

    def contains(self, other: "Scope") -> bool:
        return self == other


@dataclass(frozen=True)
class EvidenceLease:
    evidence_id: str
    reviewer_id: str
    reviewer_lineage: str
    candidate_commit_sha: str
    capsule_hash: str
    challenge_hash: str
    scope: Scope
    outcome: str
    material: bool
    observed_at: int
    expires_at: int
    raw_record_hash: str
    signature_hash: str
    external_identity_verified: bool
    external_signature_verified: bool
    external_independence_verified: bool
    synthetic_fixture: bool = True

    def validate(self) -> list[str]:
        reasons: list[str] = []
        if self.outcome not in VALID_OUTCOMES:
            reasons.append("INVALID_OUTCOME")
        if self.observed_at >= self.expires_at:
            reasons.append("INVALID_LEASE_INTERVAL")
        if not self.external_identity_verified:
            reasons.append("IDENTITY_NOT_EXTERNALLY_VERIFIED")
        if not self.external_signature_verified:
            reasons.append("SIGNATURE_NOT_EXTERNALLY_VERIFIED")
        if not self.external_independence_verified:
            reasons.append("INDEPENDENCE_NOT_EXTERNALLY_VERIFIED")
        if self.synthetic_fixture:
            reasons.append("SYNTHETIC_FIXTURE_NOT_EXTERNAL_EVIDENCE")
        return reasons

    def fresh_at(self, now: int) -> bool:
        return self.observed_at <= now < self.expires_at


@dataclass(frozen=True)
class FrozenChallenge:
    challenge_id: str
    commitment_hash: str
    frozen_at: int
    reveal_after: int
    scope: Scope

    def valid(self) -> bool:
        return bool(self.challenge_id) and self.frozen_at < self.reveal_after


def scope_gate(evidence_scope: Scope, requested_scope: Scope) -> str:
    return "SCOPE_MATCH" if evidence_scope.contains(requested_scope) else "SCOPE_NON_TRANSFER"


def reviewer_independence_graph(leases: Iterable[EvidenceLease]) -> dict[str, Any]:
    leases = list(leases)
    ids = [x.reviewer_id for x in leases]
    lineages = [x.reviewer_lineage for x in leases]
    duplicate_ids = len(ids) != len(set(ids))
    unique_lineages = len(set(lineages))
    return {
        "reviewer_count": len(ids),
        "unique_lineage_count": unique_lineages,
        "duplicate_reviewer_id": duplicate_ids,
        "declared_lineage_diversity": unique_lineages == len(ids) and not duplicate_ids,
        "proven_external_independence": False,
    }


def adjudicate(leases: Iterable[EvidenceLease], now: int, requested_scope: Scope) -> dict[str, Any]:
    relevant: list[EvidenceLease] = []
    expired = 0
    for lease in leases:
        if scope_gate(lease.scope, requested_scope) != "SCOPE_MATCH":
            continue
        if not lease.fresh_at(now):
            expired += 1
            continue
        relevant.append(lease)

    if not relevant:
        state = "EXPIRED" if expired else "AWAITING_REAL_EXTERNAL_EVIDENCE"
    else:
        has_material_fail = any(x.outcome == "FAIL" and x.material for x in relevant)
        has_pass = any(x.outcome == "PASS" for x in relevant)
        if has_material_fail and has_pass:
            state = "MIXED_EXTERNAL_EVIDENCE_ABSTAIN"
        elif has_material_fail:
            state = "SUSPENDED"
        elif has_pass:
            state = "SUPPORTED_FOR_NOW"
        else:
            state = "INCONCLUSIVE"

    assert state in VALID_SUPPORT_STATES
    return {
        "state": state,
        "fresh_matching_evidence_count": len(relevant),
        "expired_matching_evidence_count": expired,
        "history_preserved": True,
        "canonical_promotion": False,
    }


def supersession_ledger(previous: list[dict[str, Any]], lease: EvidenceLease) -> list[dict[str, Any]]:
    entry = {
        "evidence_id": lease.evidence_id,
        "outcome": lease.outcome,
        "material": lease.material,
        "scope_hash": digest(asdict(lease.scope)),
        "lease_hash": digest(asdict(lease)),
    }
    return [*previous, entry]


def contradiction_escalation(leases: Iterable[EvidenceLease], requested_scope: Scope) -> str:
    relevant = [x for x in leases if x.scope == requested_scope]
    pass_seen = any(x.outcome == "PASS" for x in relevant)
    material_fail_seen = any(x.outcome == "FAIL" and x.material for x in relevant)
    if pass_seen and material_fail_seen:
        return "MATERIAL_CONTRADICTION_REQUIRES_ABSTENTION"
    return "NO_MATERIAL_CONTRADICTION"


def retirement_state(support_state: str, eligible_successor_exists: bool) -> str:
    if support_state == "SUSPENDED":
        return "RETIREMENT_REVIEW_REQUIRED" if eligible_successor_exists else "HOLD_WITHOUT_SUCCESSOR"
    if support_state in {"MIXED_EXTERNAL_EVIDENCE_ABSTAIN", "EXPIRED", "INCONCLUSIVE"}:
        return "ABSTAIN_AND_REVALIDATE"
    if support_state == "SUPPORTED_FOR_NOW":
        return "INCUMBENT_RETAINS_SCOPED_SUPPORT"
    return "AWAIT_EXTERNAL_EVIDENCE"


def rolling_revalidation(*, challenge: FrozenChallenge, leases: Iterable[EvidenceLease], now: int,
                         requested_scope: Scope, eligible_successor_exists: bool) -> dict[str, Any]:
    if not challenge.valid():
        return {"state": "INVALID_FROZEN_CHALLENGE", "external_gates_closed": []}
    support = adjudicate(leases, now, requested_scope)
    retirement = retirement_state(support["state"], eligible_successor_exists)
    return {
        "state": "OPEN_HORIZON_REVALIDATION_ACTIVE",
        "support_state": support["state"],
        "retirement_state": retirement,
        "next_challenge_required": True,
        "support_is_permanent": False,
        "history_preserved": True,
        "external_gates_closed": [],
        "canonical_promotion": False,
        "real_world_attack_authority": 0,
        "real_world_actuation_authority": 0,
    }


def synthetic_fixture() -> tuple[Scope, FrozenChallenge, list[EvidenceLease]]:
    scope = Scope("synthetic-science", "hypothesis-ranking", "fixture-population", "regime-A")
    challenge = FrozenChallenge(
        challenge_id="synthetic-prospective-v1",
        commitment_hash=digest({"challenge": "prospective-v1"}),
        frozen_at=100,
        reveal_after=200,
        scope=scope,
    )
    common = dict(
        candidate_commit_sha="b8110d374e1aee5be786955feef3c64455c58397",
        capsule_hash=digest({"capsule": "synthetic"}),
        challenge_hash=challenge.commitment_hash,
        scope=scope,
        observed_at=220,
        expires_at=300,
        raw_record_hash=digest({"raw": "fixture"}),
        signature_hash=digest({"signature": "fixture"}),
        external_identity_verified=True,
        external_signature_verified=True,
        external_independence_verified=True,
        synthetic_fixture=True,
    )
    a = EvidenceLease(
        evidence_id="fixture-pass-a", reviewer_id="reviewer-A", reviewer_lineage="lineage-A",
        outcome="PASS", material=False, **common
    )
    b = EvidenceLease(
        evidence_id="fixture-fail-b", reviewer_id="reviewer-B", reviewer_lineage="lineage-B",
        outcome="FAIL", material=True, **common
    )
    return scope, challenge, [a, b]


def run_sanity() -> dict[str, Any]:
    scope, challenge, leases = synthetic_fixture()

    assert all(x.fresh_at(250) for x in leases)
    assert all(not x.fresh_at(301) for x in leases)

    other_scope = Scope("synthetic-science", "other-task", "fixture-population", "regime-A")
    assert scope_gate(scope, other_scope) == "SCOPE_NON_TRANSFER"

    assert contradiction_escalation(leases, scope) == "MATERIAL_CONTRADICTION_REQUIRES_ABSTENTION"

    ledger: list[dict[str, Any]] = []
    for lease in leases:
        ledger = supersession_ledger(ledger, lease)
    assert len(ledger) == 2
    assert {x["outcome"] for x in ledger} == {"PASS", "FAIL"}

    graph = reviewer_independence_graph(leases)
    assert graph["declared_lineage_diversity"] is True
    assert graph["proven_external_independence"] is False

    assert challenge.valid()

    support = adjudicate(leases, 250, scope)
    assert support["state"] == "MIXED_EXTERNAL_EVIDENCE_ABSTAIN"
    assert retirement_state(support["state"], eligible_successor_exists=True) == "ABSTAIN_AND_REVALIDATE"

    loop = rolling_revalidation(
        challenge=challenge,
        leases=leases,
        now=250,
        requested_scope=scope,
        eligible_successor_exists=True,
    )
    assert loop["state"] == "OPEN_HORIZON_REVALIDATION_ACTIVE"
    assert loop["support_is_permanent"] is False
    assert loop["external_gates_closed"] == []

    expired = adjudicate(leases, 301, scope)
    assert expired["state"] == "EXPIRED"

    assert all("SYNTHETIC_FIXTURE_NOT_EXTERNAL_EVIDENCE" in x.validate() for x in leases)

    result = {
        "status": "OPEN_HORIZON_REALITY_REVALIDATION_KERNEL_READY",
        "layers": {
            "53": "EVIDENCE_LEASE_EXPIRY_READY",
            "54": "SCOPE_NON_TRANSFER_GATE_READY",
            "55": "CONTRADICTION_ESCALATION_READY",
            "56": "EVIDENCE_SUPERSESSION_LEDGER_READY",
            "57": "REVIEWER_INDEPENDENCE_GRAPH_READY",
            "58": "PROSPECTIVELY_FROZEN_REALITY_CHALLENGE_READY",
            "59": "REALITY_DRIVEN_RETIREMENT_STATE_MACHINE_READY",
            "60": "OPEN_HORIZON_REVALIDATION_READY"
        },
        "synthetic_support_state": support["state"],
        "expired_support_state": expired["state"],
        "real_external_state": "AWAITING_REAL_EXTERNAL_EVIDENCE",
        "external_gates_closed": [],
        "canonical_promotion": False,
        "final_truth": False,
        "real_world_attack_authority": 0,
        "real_world_actuation_authority": 0,
    }
    assert result["status"] not in FORBIDDEN_END_STATES
    return result


if __name__ == "__main__":
    result = run_sanity()
    print(json.dumps(result, sort_keys=True, indent=2))
    print("EVIDENCE_LEASE_EXPIRY_READY")
    print("SCOPE_NON_TRANSFER_GATE_READY")
    print("MATERIAL_CONTRADICTION_PRESERVED")
    print("EXTERNAL_DEFEAT_HISTORY_APPEND_ONLY")
    print("REVIEWER_INDEPENDENCE_GRAPH_READY")
    print("PROSPECTIVELY_FROZEN_REALITY_CHALLENGE_READY")
    print("REALITY_DRIVEN_RETIREMENT_STATE_MACHINE_READY")
    print("OPEN_HORIZON_REALITY_REVALIDATION_KERNEL_READY")
    print("AWAITING_REAL_EXTERNAL_EVIDENCE")
    print("NO_PERMANENT_SUPPORT")
    print("EXTERNAL_GATES_REMAIN_OPEN")
