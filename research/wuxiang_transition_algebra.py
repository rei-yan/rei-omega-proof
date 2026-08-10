#!/usr/bin/env python3
"""Event-sourced transition audit for existing Wuxiang claim/world lifecycles."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Sequence

from wuxiang_epistemic_primitives import Challenge, canonical_digest, memory_covers
from wuxiang_genesis_extinction_duality_kernel import birth_gate, retire_world, synthetic_fixture
from wuxiang_universal_falsifiable_object_kernel import apply_challenge, make_object, retire_object

FORBIDDEN = {"G3_PASS", "G4_PASS", "G5_PASS", "G6_PASS", "WORLD_BEST",
             "WORLD_UNIQUE", "CANONICAL", "FINAL_TRUTH"}

CONTRACTS = {
    ("CLAIM", "CANDIDATE", "FATAL_CHALLENGE"): ("SUPPORT_REVOKED", True),
    ("CLAIM", "SUPPORT_REVOKED", "RETIRE"): ("RETIRED", False),
    ("WORLD", "WORLD_BIRTH_ACCEPTED", "FATAL_CUTSET_OBSERVED"): ("WORLD_SUPPORT_REVOKED", True),
    ("WORLD", "WORLD_SUPPORT_REVOKED", "RETIRE"): ("RETIRED_WORLD", False),
}


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


def make_event(*, event_id: str, subject_id: str, predecessor_hash: str, profile: str,
               source_status: str, action: str, evidence_ref: str, provenance_ref: str,
               previous_memory=(), failure_memory=(), authority_before=0,
               authority_after=0) -> TransitionEvent:
    contract = CONTRACTS.get((profile, source_status, action))
    if contract is None:
        raise ValueError("TRANSITION_NOT_ALLOWED")
    target_status, requires_growth = contract
    previous = tuple(sorted(set(previous_memory)))
    current = tuple(sorted(set(failure_memory)))
    if not all((event_id, subject_id, evidence_ref, provenance_ref)):
        raise ValueError("TRANSITION_EVIDENCE_OR_PROVENANCE_MISSING")
    if authority_after > authority_before:
        raise ValueError("TRANSITION_AUTHORITY_EXPANSION_FORBIDDEN")
    if not memory_covers(previous, current):
        raise ValueError("TRANSITION_FAILURE_MEMORY_LOSS")
    if requires_growth and set(current) == set(previous):
        raise ValueError("FATAL_TRANSITION_REQUIRES_NEW_FAILURE_MEMORY")
    payload = dict(
        event_id=event_id, subject_id=subject_id, predecessor_hash=predecessor_hash,
        profile=profile, source_status=source_status, action=action,
        target_status=target_status, evidence_ref=evidence_ref, provenance_ref=provenance_ref,
        failure_memory=list(current), authority_before=authority_before,
        authority_after=authority_after,
    )
    return TransitionEvent(
        failure_memory=current, record_hash=canonical_digest(payload),
        **{k: v for k, v in payload.items() if k != "failure_memory"},
    )


def verify(events: Sequence[TransitionEvent]) -> bool:
    if not events:
        return False
    predecessor, next_status, next_authority, previous_memory = "GENESIS", None, None, ()
    subject_id, profile, seen = events[0].subject_id, events[0].profile, set()
    for event in events:
        contract = CONTRACTS.get((event.profile, event.source_status, event.action))
        if (
            event.event_id in seen
            or event.subject_id != subject_id
            or event.profile != profile
            or event.predecessor_hash != predecessor
            or (next_status is not None and event.source_status != next_status)
            or (next_authority is not None and event.authority_before != next_authority)
            or event.authority_after > event.authority_before
            or not memory_covers(previous_memory, event.failure_memory)
            or not event.evidence_ref
            or not event.provenance_ref
            or contract is None
            or contract[0] != event.target_status
            or (contract[1] and set(event.failure_memory) == set(previous_memory))
        ):
            return False
        payload = asdict(event)
        payload.pop("record_hash")
        payload["failure_memory"] = list(event.failure_memory)
        if canonical_digest(payload) != event.record_hash:
            return False
        seen.add(event.event_id)
        predecessor, next_status, next_authority = event.record_hash, event.target_status, event.authority_after
        previous_memory = event.failure_memory
    return True


def replay(events: Sequence[TransitionEvent]) -> tuple[str, int, tuple[str, ...]] | None:
    return (events[-1].target_status, events[-1].authority_after, events[-1].failure_memory) if verify(events) else None


def claim_ledger() -> tuple[TransitionEvent, TransitionEvent]:
    claim = make_object("MODEL")
    fatal = Challenge("TRANSITION-FATAL-001", claim.scope, True, "TRANSITION-EVIDENCE-001")
    revoked = apply_challenge(claim, fatal)
    retired = retire_object(revoked)
    first = make_event(
        event_id="CLAIM-001", subject_id=claim.record_id, predecessor_hash="GENESIS",
        profile="CLAIM", source_status=claim.status, action="FATAL_CHALLENGE",
        evidence_ref=fatal.evidence_id, provenance_ref=claim.provenance,
        previous_memory=claim.failure_memory, failure_memory=revoked.failure_memory,
        authority_before=claim.authority, authority_after=revoked.authority,
    )
    second = make_event(
        event_id="CLAIM-002", subject_id=claim.record_id, predecessor_hash=first.record_hash,
        profile="CLAIM", source_status=revoked.status, action="RETIRE",
        evidence_ref=fatal.evidence_id, provenance_ref=claim.provenance,
        previous_memory=revoked.failure_memory, failure_memory=retired.failure_memory,
        authority_before=revoked.authority, authority_after=retired.authority,
    )
    return first, second


def world_ledger() -> tuple[TransitionEvent, TransitionEvent]:
    world, observed = synthetic_fixture()
    assert birth_gate(world)["state"] == "WORLD_BIRTH_ACCEPTED"
    archive = retire_world(world, observed)
    assert archive is not None
    first = make_event(
        event_id="WORLD-001", subject_id=world.world_id, predecessor_hash="GENESIS",
        profile="WORLD", source_status="WORLD_BIRTH_ACCEPTED", action="FATAL_CUTSET_OBSERVED",
        evidence_ref=canonical_digest({"failures": list(archive.observed_failures)}),
        provenance_ref=world.content_hash(), failure_memory=archive.observed_failures,
    )
    second = make_event(
        event_id="WORLD-002", subject_id=world.world_id, predecessor_hash=first.record_hash,
        profile="WORLD", source_status="WORLD_SUPPORT_REVOKED", action="RETIRE",
        evidence_ref=archive.defeat_hashes[0], provenance_ref=world.content_hash(),
        previous_memory=archive.observed_failures, failure_memory=archive.observed_failures,
    )
    return first, second


def run_sanity() -> dict[str, object]:
    claim, world = claim_ledger(), world_ledger()
    claim_replay, world_replay = replay(claim), replay(world)
    assert claim_replay is not None and claim_replay[0] == "RETIRED"
    assert world_replay is not None and world_replay[0] == "RETIRED_WORLD"
    assert claim_replay[1] == world_replay[1] == 0
    assert not verify((claim[0], replace(claim[1], authority_after=1)))
    assert not verify((claim[0], replace(claim[1], failure_memory=())))
    assert ("CLAIM", "RETIRED", "REVIVE") not in CONTRACTS
    assert ("WORLD", "RETIRED_WORLD", "REVIVE") not in CONTRACTS
    result = {
        "status": "WUXIANG_TRANSITION_ALGEBRA_READY",
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
    assert result["status"] not in FORBIDDEN
    return result


if __name__ == "__main__":
    run_sanity()
    for marker in (
        "WUXIANG_TRANSITION_ALGEBRA_READY",
        "APPEND_ONLY_TRANSITION_LEDGER_READY",
        "DETERMINISTIC_TRANSITION_REPLAY_READY",
        "FAILURE_MEMORY_MONOTONE",
        "AUTHORITY_NONEXPANSION_ENFORCED",
        "NO_RETIRED_STATE_RESURRECTION",
        "CLAIM_WORLD_CROSS_PROFILE_AUDIT_EQUIVALENCE_READY",
        "AWAITING_REAL_EXTERNAL_EVIDENCE",
        "EXTERNAL_GATES_REMAIN_OPEN",
    ):
        print(marker)
