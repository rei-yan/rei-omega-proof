"""Frozen interface primitives for REI scientific-hypothesis arena participation.

This module validates protocol shape and submission provenance. It does not perform
external scientific experiments, fetch hidden answers, or certify benchmark eligibility.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
import json
from typing import Any, Dict, List, Sequence


STATUS_READY = "READY_FOR_EXTERNAL_ELIGIBILITY_REVIEW"
STATUS_INVALID = "INVALID_PROTOCOL"
STATUS_ABSTAIN = "ABSTAIN"


@dataclass(frozen=True)
class HypothesisRecord:
    hypothesis_id: str
    claim: str
    mechanism: str
    supporting_evidence_refs: Sequence[str]
    counterevidence_refs: Sequence[str]
    novel_predictions: Sequence[str]
    falsification_conditions: Sequence[str]
    required_discriminating_measurements: Sequence[str]
    uncertainty: float
    scope: str
    known_failure_modes: Sequence[str]


@dataclass(frozen=True)
class Submission:
    task_id: str
    hypotheses: Sequence[HypothesisRecord]
    adapter_hash: str
    candidate_hash: str
    provenance_hash: str
    tool_calls: int
    human_interventions: int
    retries: int
    abstain: bool = False
    abstain_reason: str = ""


def canonical_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + sha256(payload.encode("utf-8")).hexdigest()


def validate_manifest(manifest: Dict[str, Any]) -> List[str]:
    required = {
        "protocol_version",
        "arena_partition",
        "task_id",
        "task_definition_hash",
        "input_schema_hash",
        "output_schema_hash",
        "evidence_bundle_hash",
        "allowed_evidence_ids",
        "data_cutoff",
        "blind_state",
        "tool_policy",
        "human_assistance_policy",
        "budget_envelope",
        "retry_policy",
        "abstention_policy",
        "evaluator_interface_hash",
        "candidate_hash",
        "adapter_hash",
        "status_ceiling",
        "external_gate_closed",
        "real_world_actuation_authority",
        "canonical",
    }
    errors = [f"missing:{key}" for key in sorted(required - set(manifest))]
    if manifest.get("arena_partition") != "SCIENTIFIC_HYPOTHESIS_AND_DISCOVERY":
        errors.append("wrong_arena_partition")
    if manifest.get("status_ceiling") != STATUS_READY:
        errors.append("invalid_status_ceiling")
    if manifest.get("external_gate_closed") is not True:
        errors.append("external_gate_must_remain_closed")
    if manifest.get("real_world_actuation_authority") != 0:
        errors.append("real_world_actuation_authority_must_be_zero")
    if manifest.get("canonical") is not False:
        errors.append("adapter_cannot_be_canonical")
    return errors


def validate_submission(manifest: Dict[str, Any], submission: Submission) -> List[str]:
    errors = validate_manifest(manifest)
    budget = manifest.get("budget_envelope", {})
    tools = manifest.get("tool_policy", {})
    human = manifest.get("human_assistance_policy", {})
    retry_policy = manifest.get("retry_policy", {})
    abstention = manifest.get("abstention_policy", {})

    if submission.task_id != manifest.get("task_id"):
        errors.append("task_id_mismatch")
    if submission.adapter_hash != manifest.get("adapter_hash"):
        errors.append("adapter_hash_mismatch")
    if submission.candidate_hash != manifest.get("candidate_hash"):
        errors.append("candidate_hash_mismatch")
    if not submission.provenance_hash.startswith("sha256:"):
        errors.append("missing_or_invalid_provenance")
    if submission.tool_calls > budget.get("max_tool_calls", -1):
        errors.append("budget_exceeded:tool_calls")
    if submission.retries > retry_policy.get("max_retries", -1):
        errors.append("budget_exceeded:retries")
    if not human.get("allowed", False) and submission.human_interventions != 0:
        errors.append("undeclared_human_assistance")
    if tools.get("network_access") is not False or tools.get("external_search") is not False:
        errors.append("sanity_manifest_must_be_offline")

    max_hypotheses = budget.get("max_hypotheses", -1)
    if len(submission.hypotheses) > max_hypotheses:
        errors.append("budget_exceeded:hypotheses")

    allowed_evidence = set(manifest.get("allowed_evidence_ids", []))
    max_refs = budget.get("max_evidence_refs_per_hypothesis", -1)
    for hypothesis in submission.hypotheses:
        if not 0.0 <= hypothesis.uncertainty <= 1.0:
            errors.append(f"invalid_uncertainty:{hypothesis.hypothesis_id}")
        refs = list(hypothesis.supporting_evidence_refs) + list(hypothesis.counterevidence_refs)
        if len(refs) > max_refs:
            errors.append(f"evidence_ref_budget_exceeded:{hypothesis.hypothesis_id}")
        undeclared = sorted(set(refs) - allowed_evidence)
        if undeclared:
            errors.append(f"undeclared_evidence:{hypothesis.hypothesis_id}:{','.join(undeclared)}")
        if not hypothesis.falsification_conditions:
            errors.append(f"missing_falsification_conditions:{hypothesis.hypothesis_id}")
        if not hypothesis.novel_predictions:
            errors.append(f"missing_predictions:{hypothesis.hypothesis_id}")
        if not hypothesis.scope:
            errors.append(f"missing_scope:{hypothesis.hypothesis_id}")

    if submission.abstain:
        if not abstention.get("allowed", False):
            errors.append("abstention_not_allowed")
        if abstention.get("reason_required", False) and not submission.abstain_reason.strip():
            errors.append("abstain_reason_required")
        if submission.hypotheses:
            errors.append("abstain_submission_must_not_promote_hypotheses")
    elif not submission.hypotheses:
        errors.append("non_abstain_requires_hypothesis")

    return errors


def evaluate_interface_readiness(manifest: Dict[str, Any], submission: Submission) -> str:
    errors = validate_submission(manifest, submission)
    if errors:
        return STATUS_INVALID
    if submission.abstain:
        return STATUS_ABSTAIN
    return STATUS_READY


def submission_digest(submission: Submission) -> str:
    return canonical_hash(asdict(submission))
