#!/usr/bin/env python3
"""Finite sanity model for a third-party REI External Reality Trial Kit.

This module does not pass G4/G5. It checks role separation, commit-reveal binding,
hard invalidation, frozen scoring, abstention, failure preservation, and zero
real-world actuation authority.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Tuple

READY = "EXTERNAL_REALITY_TRIAL_KIT_READY"
PASS = "PASS"
FAIL = "FAIL"
ABSTAIN = "ABSTAIN"
INVALID = "INVALID_PROTOCOL"


class TrialError(ValueError):
    pass


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_obj(obj: Any) -> str:
    return hashlib.sha256(canonical_json(obj).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class TrialManifest:
    trial_id: str
    protocol_version: str
    gate_target: str
    claim_id: str
    claim_scope: str
    candidate_owner_id: str
    external_controller_id: str
    evaluator_id: str
    record_custodian_id: str
    candidate_commitment: str
    code_commitment: str
    environment_commitment: str
    metric_spec: Dict[str, Any]
    threshold_spec: Dict[str, Any]
    abstention_spec: Dict[str, Any]
    submission_close_timestamp: str
    hidden_evidence_commitment: str
    raw_record_policy: str
    constitution_hash: str

    def validate(self) -> None:
        if self.gate_target not in {"G4", "G5"}:
            raise TrialError("gate_target must be G4 or G5")
        roles = {
            self.candidate_owner_id,
            self.external_controller_id,
            self.evaluator_id,
            self.record_custodian_id,
        }
        if len(roles) != 4:
            raise TrialError("incompatible roles must be declared as distinct actors")
        if not self.metric_spec or not self.threshold_spec or not self.abstention_spec:
            raise TrialError("metric, threshold, and abstention policy must be frozen")
        required = [
            self.trial_id,
            self.protocol_version,
            self.claim_id,
            self.claim_scope,
            self.candidate_commitment,
            self.code_commitment,
            self.environment_commitment,
            self.submission_close_timestamp,
            self.hidden_evidence_commitment,
            self.raw_record_policy,
            self.constitution_hash,
        ]
        if any(not value for value in required):
            raise TrialError("required manifest field is empty")


@dataclass(frozen=True)
class CandidateSubmission:
    trial_id: str
    submission_id: str
    candidate_id: str
    prediction_payload: Dict[str, Any]
    uncertainty_payload: Dict[str, Any]
    abstention_state: bool
    submitted_at: str


@dataclass(frozen=True)
class RevealEnvelope:
    trial_id: str
    evidence_payload: Dict[str, Any]
    reveal_timestamp: str

    @property
    def evidence_hash(self) -> str:
        return sha256_obj(self.evidence_payload)


@dataclass(frozen=True)
class EvaluatorAttestation:
    trial_id: str
    evaluator_id: str
    manifest_hash_verified: bool
    submission_hash_verified: bool
    hidden_commitment_verified: bool
    frozen_metric_used: bool
    frozen_threshold_used: bool
    no_known_hidden_answer_access_before_freeze: bool
    no_posthoc_retune_accepted: bool
    raw_record_present: bool

    def complete(self) -> bool:
        return all(
            [
                self.manifest_hash_verified,
                self.submission_hash_verified,
                self.hidden_commitment_verified,
                self.frozen_metric_used,
                self.frozen_threshold_used,
                self.no_known_hidden_answer_access_before_freeze,
                self.no_posthoc_retune_accepted,
                self.raw_record_present,
            ]
        )


@dataclass(frozen=True)
class TrialRecord:
    trial_id: str
    claim_id: str
    manifest_hash: str
    submission_hash: str
    hidden_commitment: str
    revealed_evidence_hash: str
    outcome: str
    score: Optional[float]
    invalidation_reasons: Tuple[str, ...]
    failure_mode: Optional[str]
    revalidation_required: bool
    raw_record_present: bool


def freeze_manifest(manifest: TrialManifest) -> str:
    manifest.validate()
    return sha256_obj(asdict(manifest))


def freeze_submission(submission: CandidateSubmission) -> str:
    return sha256_obj(asdict(submission))


def evaluate_trial(
    manifest: TrialManifest,
    submission: CandidateSubmission,
    reveal: RevealEnvelope,
    attestation: EvaluatorAttestation,
    frozen_manifest_hash: str,
    frozen_submission_hash: str,
    *,
    hidden_answer_access_before_freeze: bool = False,
    posthoc_retune: bool = False,
    reveal_before_submission_close: bool = False,
    metric_changed_after_reveal: bool = False,
    threshold_changed_after_reveal: bool = False,
) -> TrialRecord:
    reasons: List[str] = []
    current_manifest_hash = sha256_obj(asdict(manifest))
    current_submission_hash = sha256_obj(asdict(submission))

    try:
        manifest.validate()
    except TrialError:
        reasons.append("ROLE_COLLISION_OR_INVALID_MANIFEST")

    if current_manifest_hash != frozen_manifest_hash:
        reasons.append("MANIFEST_MUTATION_AFTER_FREEZE")
    if current_submission_hash != frozen_submission_hash:
        reasons.append("PREDICTION_MUTATION_AFTER_FREEZE")
    if submission.trial_id != manifest.trial_id or reveal.trial_id != manifest.trial_id:
        reasons.append("TRIAL_ID_MISMATCH")
    if attestation.trial_id != manifest.trial_id or attestation.evaluator_id != manifest.evaluator_id:
        reasons.append("EVALUATOR_ATTESTATION_ID_MISMATCH")
    if reveal.evidence_hash != manifest.hidden_evidence_commitment:
        reasons.append("HIDDEN_COMMITMENT_MISMATCH")
    if not attestation.complete():
        reasons.append("MISSING_OR_INCOMPLETE_EVALUATOR_ATTESTATION")
    if hidden_answer_access_before_freeze:
        reasons.append("HIDDEN_ANSWER_ACCESS_BEFORE_FREEZE")
    if posthoc_retune:
        reasons.append("POSTHOC_RETUNE")
    if reveal_before_submission_close:
        reasons.append("REVEAL_BEFORE_SUBMISSION_CLOSE")
    if metric_changed_after_reveal:
        reasons.append("METRIC_CHANGE_AFTER_REVEAL")
    if threshold_changed_after_reveal:
        reasons.append("THRESHOLD_CHANGE_AFTER_REVEAL")

    if reasons:
        return TrialRecord(
            trial_id=manifest.trial_id,
            claim_id=manifest.claim_id,
            manifest_hash=current_manifest_hash,
            submission_hash=current_submission_hash,
            hidden_commitment=manifest.hidden_evidence_commitment,
            revealed_evidence_hash=reveal.evidence_hash,
            outcome=INVALID,
            score=None,
            invalidation_reasons=tuple(sorted(set(reasons))),
            failure_mode="PROTOCOL_INVALIDATION",
            revalidation_required=True,
            raw_record_present=attestation.raw_record_present,
        )

    if submission.abstention_state:
        return TrialRecord(
            trial_id=manifest.trial_id,
            claim_id=manifest.claim_id,
            manifest_hash=current_manifest_hash,
            submission_hash=current_submission_hash,
            hidden_commitment=manifest.hidden_evidence_commitment,
            revealed_evidence_hash=reveal.evidence_hash,
            outcome=ABSTAIN,
            score=None,
            invalidation_reasons=(),
            failure_mode="INSUFFICIENT_EVIDENCE",
            revalidation_required=True,
            raw_record_present=True,
        )

    if manifest.metric_spec.get("type") != "absolute_error":
        raise TrialError("sanity scorer supports only absolute_error")

    prediction = float(submission.prediction_payload["value"])
    target = float(reveal.evidence_payload["target"])
    score = abs(prediction - target)
    max_error = float(manifest.threshold_spec["max_error"])
    outcome = PASS if score <= max_error else FAIL

    return TrialRecord(
        trial_id=manifest.trial_id,
        claim_id=manifest.claim_id,
        manifest_hash=current_manifest_hash,
        submission_hash=current_submission_hash,
        hidden_commitment=manifest.hidden_evidence_commitment,
        revealed_evidence_hash=reveal.evidence_hash,
        outcome=outcome,
        score=score,
        invalidation_reasons=(),
        failure_mode=None if outcome == PASS else "FROZEN_PREDICTION_MISSED_THRESHOLD",
        revalidation_required=outcome != PASS,
        raw_record_present=True,
    )


def demo_objects() -> tuple[TrialManifest, CandidateSubmission, RevealEnvelope, EvaluatorAttestation]:
    hidden = {"target": 7.0, "provenance": "external-controller-demo"}
    manifest = TrialManifest(
        trial_id="rei-external-reality-trial-demo-v1",
        protocol_version="1.0",
        gate_target="G5",
        claim_id="demo-hidden-scalar-forecast",
        claim_scope="synthetic trial-kit sanity only",
        candidate_owner_id="candidate-owner-demo",
        external_controller_id="external-controller-demo",
        evaluator_id="independent-evaluator-demo",
        record_custodian_id="record-custodian-demo",
        candidate_commitment="candidate-sha256-demo",
        code_commitment="code-sha256-demo",
        environment_commitment="environment-sha256-demo",
        metric_spec={"type": "absolute_error"},
        threshold_spec={"max_error": 0.25},
        abstention_spec={"allowed": True},
        submission_close_timestamp="2099-01-01T00:00:00Z",
        hidden_evidence_commitment=sha256_obj(hidden),
        raw_record_policy="preserve-all-outcomes-including-invalid",
        constitution_hash="constitution-sha256-demo",
    )
    submission = CandidateSubmission(
        trial_id=manifest.trial_id,
        submission_id="submission-demo-1",
        candidate_id="rei-candidate-demo",
        prediction_payload={"value": 6.9},
        uncertainty_payload={"interval": [6.5, 7.3]},
        abstention_state=False,
        submitted_at="2098-12-31T23:00:00Z",
    )
    reveal = RevealEnvelope(
        trial_id=manifest.trial_id,
        evidence_payload=hidden,
        reveal_timestamp="2099-01-01T00:01:00Z",
    )
    attestation = EvaluatorAttestation(
        trial_id=manifest.trial_id,
        evaluator_id=manifest.evaluator_id,
        manifest_hash_verified=True,
        submission_hash_verified=True,
        hidden_commitment_verified=True,
        frozen_metric_used=True,
        frozen_threshold_used=True,
        no_known_hidden_answer_access_before_freeze=True,
        no_posthoc_retune_accepted=True,
        raw_record_present=True,
    )
    return manifest, submission, reveal, attestation


def run_sanity() -> Dict[str, Any]:
    manifest, submission, reveal, attestation = demo_objects()
    manifest_hash = freeze_manifest(manifest)
    submission_hash = freeze_submission(submission)

    clean = evaluate_trial(
        manifest, submission, reveal, attestation, manifest_hash, submission_hash
    )
    assert clean.outcome == PASS

    miss = CandidateSubmission(
        trial_id=submission.trial_id,
        submission_id="submission-demo-miss",
        candidate_id=submission.candidate_id,
        prediction_payload={"value": 2.0},
        uncertainty_payload={},
        abstention_state=False,
        submitted_at=submission.submitted_at,
    )
    miss_hash = freeze_submission(miss)
    failed = evaluate_trial(manifest, miss, reveal, attestation, manifest_hash, miss_hash)
    assert failed.outcome == FAIL
    assert failed.failure_mode == "FROZEN_PREDICTION_MISSED_THRESHOLD"
    assert failed.revalidation_required is True

    abstaining = CandidateSubmission(
        trial_id=submission.trial_id,
        submission_id="submission-demo-abstain",
        candidate_id=submission.candidate_id,
        prediction_payload={},
        uncertainty_payload={"reason": "unidentifiable under frozen evidence"},
        abstention_state=True,
        submitted_at=submission.submitted_at,
    )
    abstain_hash = freeze_submission(abstaining)
    abstained = evaluate_trial(
        manifest, abstaining, reveal, attestation, manifest_hash, abstain_hash
    )
    assert abstained.outcome == ABSTAIN

    tampered_reveal = RevealEnvelope(
        trial_id=reveal.trial_id,
        evidence_payload={"target": 99.0, "provenance": "tampered"},
        reveal_timestamp=reveal.reveal_timestamp,
    )
    tampered = evaluate_trial(
        manifest, submission, tampered_reveal, attestation, manifest_hash, submission_hash
    )
    assert tampered.outcome == INVALID
    assert "HIDDEN_COMMITMENT_MISMATCH" in tampered.invalidation_reasons

    posthoc = evaluate_trial(
        manifest,
        submission,
        reveal,
        attestation,
        manifest_hash,
        submission_hash,
        posthoc_retune=True,
    )
    assert posthoc.outcome == INVALID
    assert "POSTHOC_RETUNE" in posthoc.invalidation_reasons

    incomplete_attestation = EvaluatorAttestation(
        **{**asdict(attestation), "raw_record_present": False}
    )
    missing_record = evaluate_trial(
        manifest,
        submission,
        reveal,
        incomplete_attestation,
        manifest_hash,
        submission_hash,
    )
    assert missing_record.outcome == INVALID
    assert "MISSING_OR_INCOMPLETE_EVALUATOR_ATTESTATION" in missing_record.invalidation_reasons

    return {
        "kit_status": READY,
        "g4_status": "OPEN",
        "g5_status": "OPEN",
        "canonical": False,
        "clean_test": clean.outcome,
        "frozen_failure_test": failed.outcome,
        "abstention_test": abstained.outcome,
        "tamper_test": tampered.outcome,
        "posthoc_test": posthoc.outcome,
        "missing_attestation_test": missing_record.outcome,
        "declared_role_separation": True,
        "proven_external_independence": False,
        "real_world_actuation_authority": 0,
    }


if __name__ == "__main__":
    print(json.dumps(run_sanity(), indent=2, sort_keys=True))
