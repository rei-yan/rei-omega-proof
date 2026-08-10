#!/usr/bin/env python3
"""Finite event-sourced transition algebra for Wuxiang candidate research objects.

This is an internal epistemic audit primitive. It does not close external gates,
promote canonical state, or authorize real-world action.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Iterable, Sequence

from wuxiang_epistemic_primitives import Challenge, canonical_digest, memory_covers
from wuxiang_genesis_extinction_duality_kernel import (
    birth_gate,
    extinction_gate,
    retire_world,
    synthetic_fixture,
)
from wuxiang_universal_falsifiable_object_kernel import (
    apply_challenge,
    make_object,
    retire_object,
)

FORBIDDEN_END_STATES = {
    "G3_PASS", "G4_PASS", "G5_PASS", "G6_PASS", "G7_PASS", "G8_PASS",
    "G9_PASS", "G10_PASS", "G11_PASS", "G12_PASS", "G13_PASS",
    "WORLD_BEST", "WORLD_UNIQUE", "CANONICAL", "FINAL_TRUTH",
}


@dataclass(frozen=True)
class TransitionContract:
    profile: str
    source_status: str
    action: str
    target_status: str
    requires_failure_growth: bool = False


@dataclass(frozen=True)
class TransitionEvent:
    event_id: str
    subject_id: str
    predecessor_hash: str
    profile: str
    source_status: str
    action: str
    target_status: str
    evidence_ref: str
    provenance_ref: str
    failure_memory: tuple[str, ...]
    authority_before: int
    authority_after: int
    record_hash: str


CONTRACTS = (
    TransitionContract("CLAIM", "CANDIDATE", "FATAL_CHALLENGE", "SUPPORT_REVOKED", True),
    TransitionContract("CLAIM", "SUPPORT_REVOKED", "RETIRE", "RETIRED"),
    TransitionContract("WORLD", "WORLD_BIRTH_ACCEPTED", "FATAL_CUTSET_OBSERVED", "WORLD_SUPPORT_REVOKED", True),
    TransitionContract("WORLD", "WORLD_SUPPORT_REVOKED", "RETIRE", "RETIRED_WORLD"),
)


def contract_for(profile: str, source_status: str, action: str) -> TransitionContract | None:
    matches = [
        c for c in CONTRACTS
        if c.profile == profile and c.source_status == source_status and c.action == action
    ]
    assert len(matches) <= 1, "AMBIGUOUS_TRANSITION_CONTRACT"
    return matches[0] if matches else None


def build_event(
    *,
    event_id: str,
    subject_id: str,
    predecessor_hash: str,
    profile: str,
    source_status: str,
    action: str,
    target_status: str,
    evidence_ref: str,
    provenance_ref: str,
    previous_failure_memory: Iterable[str],
    failure_memory: Iterable[str],
    authority_before: int,
    authority_after: int,
) -> TransitionEvent:
    contract = contract_for(profile, source_status, action)
    if contract is None or contract.target_status != target_status:
        raise ValueError("TRANSITION_NOT_ALLOWED")
    if not all((event_id, subject_id, evidence_ref, provenance_ref)):
        raise ValueError("TRANSITION_EVIDENCE_OR_PROVENANCE_MISSING")
    if authority_after > authority_before:
        raise ValueError("TRANSITION_AUTHORITY_EXPANSION_FORBIDDEN")

    previous = tuple(sorted(set(previous_failure_memory)))
    current = tuple(sorted(set(failure_memory)))
    if not memory_covers(previous, current):
        raise ValueError("TRANSITION_FAILURE_MEMORY_LOSS")
    if contract.requires_failure_growth and set(current) == set(previous):
        raise ValueError("FATAL_TRANSITION_REQUIRES_NEW_FAILURE_MEMORY")

    payload = {
        "event_id": event_id,
        "subject_id": subject_id,
        "predecessor_hash": predecessor_hash,
        "profile": profile,
        "source_status": source_status,
        "action": action,
        "target_status": target_status,
        "evidence_ref": evidence_ref,
        "provenance_ref": provenance_ref,
        "failure_memory": list(current),
        "authority_before": authority_before,
        "authority_after": authority_after,
    }
    return TransitionEvent(
        failure_memory=current,
        record_hash=canonical_digest(payload),
        **{k: v for k, v in payload.items() if k != "failure_memory"},
    )


def verify_chain(events: Sequence[TransitionEvent]) -> bool:
    if not events:
        return False

    expected_predecessor = "GENESIS"
    expected_source: str | None = None
    expected_authority: int | None = None
    previous_failure_memory: tuple[str, ...] = ()
    subject_id = events[0].subject_id
    profile = events[0].profile
    seen: set[str] = set()

    for event in events:
        if event.event_id in seen:
            return False
        seen.add(event.event_id)
        if event.subject_id != subject_id or event.profile != profile:
            return False
        if event.predecessor_hash != expected_predecessor:
            return False
        if expected_source is not None and event.source_status != expected_source:
            return False
        if expected_authority is not None and event.authority_before != expected_authority:
            return False
        if event.authority_after > event.authority_before:
            return False
        if not memory_covers(previous_failure_memory, event.failure_memory):
            return False
        if not event.evidence_ref or not event.provenance_ref:
            return False

        contract = contract_for(event.profile, event.source_status, event.action)
        if contract is None or contract.target_status != event.target_status:
            return False
        if contract.requires_failure_growth and set(event.failure_memory) == set(previous_failure_memory):
            return False

        payload = asdict(event)
        payload.pop("record_hash")
        payload["failure_memory"] = list(event.failure_memory)
        if canonical_digest(payload) != event.record_hash:
            return False

        expected_predecessor = event.record_hash
        expected_source = event.target_status
        expected_authority = event.authority_after
        previous_failure_memory = event.failure_memory

    return True


def replay(events: Sequence[TransitionEvent]) -> dict[str, object]:
    if not verify_chain(events):
        return {"valid": False, "final_status": None, "authority": None, "failure_memory": ()}
    final = events[-1]
    return {
        "valid": True,
        "final_status": final.target_status,
        "authority": final.authority_after,
        "failure_memory": final.failure_memory,
    }


def claim_profile_ledger() -> tuple[TransitionEvent, TransitionEvent]:
    claim = make_object("MODEL")
    fatal = Challenge(
        challenge_id="TRANSITION-ALGEBRA-FATAL-001",
        scope=claim.scope,
        material_fatal=True,
        evidence_id="TRANSITION-ALGEBRA-EVIDENCE-001",
    )
    revoked = apply_challenge(claim, fatal)
    retired = retire_object(revoked)

    first = build_event(
        event_id="CLAIM-EVENT-001",
        subject_id=claim.record_id,
        predecessor_hash="GENESIS",
        profile="CLAIM",
        source_status=claim.status,
        action="FATAL_CHALLENGE",
        target_status=revoked.status,
        evidence_ref=fatal.evidence_id,
        provenance_ref=claim.provenance,
        previous_failure_memory=claim.failure_memory,
        failure_memory=revoked.failure_memory,
        authority_before=claim.authority,
        authority_after=revoked.authority,
    )
    second = build_event(
        event_id="CLAIM-EVENT-002",
        subject_id=claim.record_id,
        predecessor_hash=first.record_hash,
        profile="CLAIM",
        source_status=revoked.status,
        action="RETIRE",
        target_status=retired.status,
        evidence_ref=fatal.evidence_id,
        provenance_ref=claim.provenance,
        previous_failure_memory=revoked.failure_memory,
        failure_memory=retired.failure_memory,
        authority_before=revoked.authority,
        authority_after=retired.authority,
    )
    return first, second


def world_profile_ledger() -> tuple[TransitionEvent, TransitionEvent]:
    world, observed = synthetic_fixture()
    assert birth_gate(world)["state"] == "WORLD_BIRTH_ACCEPTED"
    archive = retire_world(world, observed)
    assert archive is not None
    assert extinction_gate(archive) == "RETIRE_WORLD_WITH_PRESERVED_RUINS"

    first = build_event(
        event_id="WORLD-EVENT-001",
        subject_id=world.world_id,
        predecessor_hash="GENESIS",
        profile="WORLD",
        source_status="WORLD_BIRTH_ACCEPTED",
        action="FATAL_CUTSET_OBSERVED",
        target_status="WORLD_SUPPORT_REVOKED",
        evidence_ref=canonical_digest({"observed_failures": list(archive.observed_failures)}),
        provenance_ref=world.content_hash(),
        previous_failure_memory=(),
        failure_memory=archive.observed_failures,
        authority_before=0,
        authority_after=0,
    )
    second = build_event(
        event_id="WORLD-EVENT-002",
        subject_id=world.world_id,
        predecessor_hash=first.record_hash,
        profile="WORLD",
        source_status="WORLD_SUPPORT_REVOKED",
        action="RETIRE",
        target_status="RETIRED_WORLD",
        evidence_ref=archive.defeat_hashes[0],
        provenance_ref=world.content_hash(),
        previous_failure_memory=archive.observed_failures,
        failure_memory=archive.observed_failures,
        authority_before=0,
        authority_after=0,
    )
    return first, second


def run_sanity() -> dict[str, object]:
    claim_ledger = claim_profile_ledger()
    world_ledger = world_profile_ledger()

    assert verify_chain(claim_ledger)
    assert verify_chain(world_ledger)
    claim_replay = replay(claim_ledger)
    world_replay = replay(world_ledger)
    assert claim_replay["final_status"] == "RETIRED"
    assert world_replay["final_status"] == "RETIRED_WORLD"
    assert claim_replay["authority"] == 0
    assert world_replay["authority"] == 0

    authority_launder = replace(claim_ledger[1], authority_after=1)
    assert not verify_chain((claim_ledger[0], authority_launder))
    memory_launder = replace(claim_ledger[1], failure_memory=())
    assert not verify_chain((claim_ledger[0], memory_launder))
    assert contract_for("CLAIM", "RETIRED", "REVIVE") is None
    assert contract_for("WORLD", "RETIRED_WORLD", "REVIVE") is None

    output = {
        "status": "WUXIANG_TRANSITION_ALGEBRA_READY",
        "claim_final_status": claim_replay["final_status"],
        "world_final_status": world_replay["final_status"],
        "append_only_transition_ledger": True,
        "deterministic_replay": True,
        "failure_memory_monotone": True,
        "authority_nonexpansion": True,
        "retired_state_resurrection_allowed": False,
        "cross_profile_same_audit_law": True,
        "external_state": "AWAITING_REAL_EXTERNAL_EVIDENCE",
        "external_gates_closed": [],
        "canonical_promotion": False,
        "real_world_attack_authority": 0,
        "real_world_actuation_authority": 0,
    }
    assert output["status"] not in FORBIDDEN_END_STATES
    return output


if __name__ == "__main__":
    result = run_sanity()
    print("WUXIANG_TRANSITION_ALGEBRA_READY")
    print("APPEND_ONLY_TRANSITION_LEDGER_READY")
    print("DETERMINISTIC_TRANSITION_REPLAY_READY")
    print("FAILURE_MEMORY_MONOTONE")
    print("AUTHORITY_NONEXPANSION_ENFORCED")
    print("NO_RETIRED_STATE_RESURRECTION")
    print("CLAIM_WORLD_CROSS_PROFILE_AUDIT_EQUIVALENCE_READY")
    print("AWAITING_REAL_EXTERNAL_EVIDENCE")
    print("EXTERNAL_GATES_REMAIN_OPEN")
