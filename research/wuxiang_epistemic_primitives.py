#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass, replace
from hashlib import sha256
from itertools import combinations
import json
from typing import Iterable, Mapping, Tuple


@dataclass(frozen=True)
class MeasurementContext:
    observer_role: str
    instrument: str
    protocol: str
    regime: str
    lease_valid: bool = True


@dataclass(frozen=True)
class LifecycleRecord:
    record_id: str
    kind: str
    claim: str
    scope: str
    evidence: Tuple[str, ...]
    falsifiers: Tuple[str, ...]
    provenance: str
    status: str = "CANDIDATE"
    failure_memory: Tuple[str, ...] = ()
    parent_id: str | None = None
    inherited_support: bool = False
    authority: int = 0


@dataclass(frozen=True)
class Challenge:
    challenge_id: str
    scope: str
    material_fatal: bool
    evidence_id: str


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


def canonical_digest(value: object) -> str:
    raw = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return sha256(raw).hexdigest()


def verify_chained_records(
    records: Iterable[object],
    *,
    genesis: str = "GENESIS",
    id_field: str = "event_id",
    predecessor_field: str = "predecessor_hash",
    hash_field: str = "record_hash",
) -> bool:
    seq = tuple(records)
    if not seq:
        return False
    expected, seen = genesis, set()
    for record in seq:
        if is_dataclass(record) and not isinstance(record, type):
            data = asdict(record)
        elif isinstance(record, Mapping):
            data = dict(record)
        else:
            return False
        record_id = data.get(id_field)
        record_hash = data.get(hash_field)
        if not record_id or record_id in seen or data.get(predecessor_field) != expected or not record_hash:
            return False
        payload = dict(data)
        payload.pop(hash_field, None)
        if canonical_digest(payload) != record_hash:
            return False
        seen.add(record_id)
        expected = record_hash
    return True


def missing_requirements(requirements: Mapping[str, object]) -> list[str]:
    return [name for name, value in requirements.items() if not value]


def unique_values(values: Iterable[str]) -> bool:
    seq = tuple(values)
    return len(seq) == len(set(seq))


def disjoint(left: Iterable[str], right: Iterable[str]) -> bool:
    return set(left).isdisjoint(right)


def memory_covers(required: Iterable[str], actual: Iterable[str]) -> bool:
    return set(required).issubset(set(actual))


def memory_union(*groups: Iterable[str]) -> frozenset[str]:
    merged: set[str] = set()
    for group in groups:
        merged.update(group)
    return frozenset(merged)


def minimal_fatal_cutsets(
    observed_failures: Iterable[str], fatal_cutsets: Iterable[Iterable[str]]
) -> list[list[str]]:
    observed = sorted(set(observed_failures))
    fatal = tuple(frozenset(cut) for cut in fatal_cutsets if tuple(cut))
    result: list[list[str]] = []
    for size in range(1, len(observed) + 1):
        for combo in combinations(observed, size):
            candidate = frozenset(combo)
            if not any(cut.issubset(candidate) for cut in fatal):
                continue
            if any(set(previous).issubset(candidate) for previous in result):
                continue
            result.append(list(combo))
    return result


def mapping_coverage(
    source_terms: Iterable[str], mapping: Mapping[str, str]
) -> tuple[dict[str, str], float, float]:
    source = sorted(set(source_terms))
    if not source:
        return {}, 0.0, 1.0
    mapped = {term: mapping[term] for term in source if mapping.get(term)}
    coverage = len(mapped) / len(source)
    return mapped, coverage, 1.0 - coverage


def admit_record(record: LifecycleRecord, allowed_kinds: Iterable[str] | None = None) -> bool:
    kind_ok = True if allowed_kinds is None else record.kind in set(allowed_kinds)
    return all((
        record.record_id,
        kind_ok,
        record.claim,
        record.scope,
        bool(record.evidence),
        bool(record.falsifiers),
        record.provenance,
        record.authority == 0,
        not record.inherited_support,
    ))


def apply_challenge(record: LifecycleRecord, challenge: Challenge) -> LifecycleRecord:
    if not admit_record(record):
        raise ValueError("RECORD_NOT_ADMISSIBLE")
    if challenge.scope != record.scope:
        return replace(record, status="ABSTAIN_SCOPE_MISMATCH")
    if challenge.material_fatal:
        failures = tuple(sorted(set(record.failure_memory + (challenge.challenge_id,))))
        return replace(record, status="SUPPORT_REVOKED", failure_memory=failures)
    return replace(record, status="SURVIVES_FOR_NOW")


def retire_record(record: LifecycleRecord) -> LifecycleRecord:
    if record.status != "SUPPORT_REVOKED":
        raise ValueError("RETIREMENT_REQUIRES_SUPPORT_REVOCATION")
    return replace(record, status="RETIRED")


def defeat_memory_preserved(parent: LifecycleRecord, child: LifecycleRecord) -> bool:
    return memory_covers(parent.failure_memory, child.failure_memory)


def successor_eligible(parent: LifecycleRecord, child: LifecycleRecord) -> bool:
    return all((
        parent.status == "RETIRED",
        child.parent_id == parent.record_id,
        child.status == "CANDIDATE",
        defeat_memory_preserved(parent, child),
        child.authority == 0,
        not child.inherited_support,
        bool(child.provenance),
        bool(child.falsifiers),
        bool(child.evidence),
    ))


def context_equivalent(a: MeasurementContext, b: MeasurementContext) -> bool:
    return (
        a.observer_role == b.observer_role
        and a.instrument == b.instrument
        and a.protocol == b.protocol
        and a.regime == b.regime
        and a.lease_valid
        and b.lease_valid
    )


def scope_transfer_allowed(
    evidence_scope: str,
    claim_scope: str,
    source_context: MeasurementContext,
    target_context: MeasurementContext,
) -> bool:
    return evidence_scope == claim_scope and context_equivalent(source_context, target_context)


def open_critical_debt(debts: Tuple[EvidenceDebt, ...], critical_ids: Iterable[str]) -> bool:
    critical = tuple(critical_ids)
    return any(
        d.status == "OPEN"
        and any(d.debt_id == c or d.debt_id.startswith(f"{c}:") for c in critical)
        for d in debts
    )


def compile_external_challenge(
    *,
    claim_id: str,
    claim_scope: str,
    context: MeasurementContext,
    falsification_conditions: Tuple[str, ...],
    candidate_commit: str,
    frozen_input_hash: str,
    hidden_challenge_commitment: str,
) -> dict:
    package = {
        "schema": "WUXIANG-EXTERNAL-CHALLENGE-v1",
        "candidate_commit": candidate_commit,
        "claim_id": claim_id,
        "claim_scope": claim_scope,
        "frozen_input_hash": frozen_input_hash,
        "observer_role": context.observer_role,
        "instrument": context.instrument,
        "measurement_protocol": context.protocol,
        "regime": context.regime,
        "falsification_conditions": list(falsification_conditions),
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
