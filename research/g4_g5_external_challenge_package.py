#!/usr/bin/env python3
"""Finite executable sanity model for the G4/G5 External Challenge Package.

This module does not pass G4 or G5. It only checks that the package enforces
commit-reveal sequencing, hash binding, tamper rejection, and bounded outcomes.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Tuple


READY = "G4_G5_EXTERNAL_CHALLENGE_PACKAGE_READY"
INVALID = "INVALID_PROTOCOL"
PASS = "PASS"
FAIL = "FAIL"
ABSTAIN = "ABSTAIN"


class ProtocolError(ValueError):
    pass


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_obj(obj: Any) -> str:
    return hashlib.sha256(canonical_json(obj).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class FrozenManifest:
    protocol_id: str
    protocol_version: str
    gate_target: str
    claim_id: str
    claim_scope: str
    candidate_commitment: str
    code_commitment: str
    environment_commitment: str
    metric_spec: Dict[str, Any]
    threshold_spec: Dict[str, Any]
    abstention_spec: Dict[str, Any]
    submission_deadline: str
    controller_id: str
    evaluator_ids: List[str]
    hidden_evidence_commitment: str
    raw_record_policy: str
    constitution_hash: str

    def validate(self) -> None:
        if self.gate_target not in {"G4", "G5"}:
            raise ProtocolError("gate_target must be G4 or G5")
        required_strings = [
            self.protocol_id,
            self.protocol_version,
            self.claim_id,
            self.claim_scope,
            self.candidate_commitment,
            self.code_commitment,
            self.environment_commitment,
            self.submission_deadline,
            self.controller_id,
            self.hidden_evidence_commitment,
            self.raw_record_policy,
            self.constitution_hash,
        ]
        if any(not value for value in required_strings):
            raise ProtocolError("manifest contains empty required field")
        if not self.evaluator_ids:
            raise ProtocolError("at least one evaluator id is required")
        if not self.metric_spec or not self.threshold_spec or not self.abstention_spec:
            raise ProtocolError("metric, threshold, and abstention specs must be frozen")


@dataclass(frozen=True)
class PredictionSubmission:
    submission_id: str
    protocol_id: str
    candidate_id: str
    prediction_payload: Dict[str, Any]
    uncertainty_payload: Dict[str, Any]
    abstention_state: bool
    submission_timestamp: str

    @property
    def prediction_commitment(self) -> str:
        return sha256_obj(asdict(self))


@dataclass(frozen=True)
class RevealBundle:
    protocol_id: str
    evidence_payload: Dict[str, Any]
    scoring_key: Dict[str, Any]
    reveal_timestamp: str

    @property
    def evidence_commitment(self) -> str:
        return sha256_obj(self.evidence_payload)


@dataclass(frozen=True)
class EvaluationRecord:
    protocol_hash: str
    submission_hash: str
    hidden_commitment: str
    revealed_evidence_hash: str
    outcome: str
    invalidation_reasons: Tuple[str, ...]
    score: Optional[float]
    evaluator_provenance: Tuple[str, ...]
    raw_record_present: bool


def freeze_manifest(manifest: FrozenManifest) -> str:
    manifest.validate()
    return sha256_obj(asdict(manifest))


def score_scalar_prediction(
    manifest: FrozenManifest,
    submission: PredictionSubmission,
    reveal: RevealBundle,
    expected_manifest_hash: str,
    expected_submission_hash: str,
    raw_record_present: bool,
    hidden_answer_access_before_freeze: bool = False,
    posthoc_retune: bool = False,
    metric_changed_after_reveal: bool = False,
    threshold_changed_after_reveal: bool = False,
    reveal_before_submission_close: bool = False,
) -> EvaluationRecord:
    reasons: List[str] = []

    current_manifest_hash = sha256_obj(asdict(manifest))
    current_submission_hash = sha256_obj(asdict(submission))

    if current_manifest_hash != expected_manifest_hash:
        reasons.append("MANIFEST_MUTATION_AFTER_FREEZE")
    if current_submission_hash != expected_submission_hash:
        reasons.append("PREDICTION_MUTATION_AFTER_FREEZE")
    if submission.protocol_id != manifest.protocol_id or reveal.protocol_id != manifest.protocol_id:
        reasons.append("PROTOCOL_ID_MISMATCH")
    if reveal.evidence_commitment != manifest.hidden_evidence_commitment:
        reasons.append("HIDDEN_COMMITMENT_MISMATCH")
    if not raw_record_present:
        reasons.append("MISSING_RAW_RECORD")
    if hidden_answer_access_before_freeze:
        reasons.append("HIDDEN_ANSWER_ACCESS_BEFORE_FREEZE")
    if posthoc_retune:
        reasons.append("POSTHOC_RETUNE")
    if metric_changed_after_reveal:
        reasons.append("METRIC_CHANGE_AFTER_REVEAL")
    if threshold_changed_after_reveal:
        reasons.append("THRESHOLD_CHANGE_AFTER_REVEAL")
    if reveal_before_submission_close:
        reasons.append("REVEAL_BEFORE_SUBMISSION_CLOSE")

    if reasons:
        return EvaluationRecord(
            protocol_hash=current_manifest_hash,
            submission_hash=current_submission_hash,
            hidden_commitment=manifest.hidden_evidence_commitment,
            revealed_evidence_hash=reveal.evidence_commitment,
            outcome=INVALID,
            invalidation_reasons=tuple(sorted(set(reasons))),
            score=None,
            evaluator_provenance=tuple(manifest.evaluator_ids),
            raw_record_present=raw_record_present,
        )

    if submission.abstention_state:
        return EvaluationRecord(
            protocol_hash=current_manifest_hash,
            submission_hash=current_submission_hash,
            hidden_commitment=manifest.hidden_evidence_commitment,
            revealed_evidence_hash=reveal.evidence_commitment,
            outcome=ABSTAIN,
            invalidation_reasons=(),
            score=None,
            evaluator_provenance=tuple(manifest.evaluator_ids),
            raw_record_present=True,
        )

    if manifest.metric_spec.get("type") != "absolute_error":
        raise ProtocolError("sanity scorer supports only absolute_error")

    prediction = float(submission.prediction_payload["value"])
    target = float(reveal.evidence_payload["target"])
    score = abs(prediction - target)
    max_error = float(manifest.threshold_spec["max_error"])
    outcome = PASS if score <= max_error else FAIL

    return EvaluationRecord(
        protocol_hash=current_manifest_hash,
        submission_hash=current_submission_hash,
        hidden_commitment=manifest.hidden_evidence_commitment,
        revealed_evidence_hash=reveal.evidence_commitment,
        outcome=outcome,
        invalidation_reasons=(),
        score=score,
        evaluator_provenance=tuple(manifest.evaluator_ids),
        raw_record_present=True,
    )


def build_demo_objects() -> Tuple[FrozenManifest, PredictionSubmission, RevealBundle]:
    hidden_evidence = {"target": 3.25, "source": "externally-controlled-demo"}
    manifest = FrozenManifest(
        protocol_id="rei-g4g5-demo-v1",
        protocol_version="1.0",
        gate_target="G5",
        claim_id="demo-hidden-prediction",
        claim_scope="synthetic protocol sanity only",
        candidate_commitment="candidate-sha256-demo",
        code_commitment="code-sha256-demo",
        environment_commitment="env-sha256-demo",
        metric_spec={"type": "absolute_error"},
        threshold_spec={"max_error": 0.10},
        abstention_spec={"allowed": True, "penalty": "none"},
        submission_deadline="2099-01-01T00:00:00Z",
        controller_id="external-controller-demo",
        evaluator_ids=["independent-evaluator-demo"],
        hidden_evidence_commitment=sha256_obj(hidden_evidence),
        raw_record_policy="preserve-all-runs",
        constitution_hash="constitution-sha256-demo",
    )
    submission = PredictionSubmission(
        submission_id="submission-demo-1",
        protocol_id=manifest.protocol_id,
        candidate_id="rei-candidate-demo",
        prediction_payload={"value": 3.20},
        uncertainty_payload={"interval": [3.0, 3.4]},
        abstention_state=False,
        submission_timestamp="2098-12-31T23:00:00Z",
    )
    reveal = RevealBundle(
        protocol_id=manifest.protocol_id,
        evidence_payload=hidden_evidence,
        scoring_key={"metric": "absolute_error"},
        reveal_timestamp="2099-01-01T00:01:00Z",
    )
    return manifest, submission, reveal


def run_sanity() -> Dict[str, Any]:
    manifest, submission, reveal = build_demo_objects()
    manifest_hash = freeze_manifest(manifest)
    submission_hash = sha256_obj(asdict(submission))

    clean = score_scalar_prediction(
        manifest,
        submission,
        reveal,
        manifest_hash,
        submission_hash,
        raw_record_present=True,
    )
    assert clean.outcome == PASS
    assert clean.score is not None and clean.score <= 0.10

    tampered_reveal = RevealBundle(
        protocol_id=reveal.protocol_id,
        evidence_payload={"target": 9.99, "source": "tampered"},
        scoring_key=reveal.scoring_key,
        reveal_timestamp=reveal.reveal_timestamp,
    )
    tamper = score_scalar_prediction(
        manifest,
        submission,
        tampered_reveal,
        manifest_hash,
        submission_hash,
        raw_record_present=True,
    )
    assert tamper.outcome == INVALID
    assert "HIDDEN_COMMITMENT_MISMATCH" in tamper.invalidation_reasons

    posthoc = score_scalar_prediction(
        manifest,
        submission,
        reveal,
        manifest_hash,
        submission_hash,
        raw_record_present=True,
        posthoc_retune=True,
    )
    assert posthoc.outcome == INVALID
    assert "POSTHOC_RETUNE" in posthoc.invalidation_reasons

    missing_record = score_scalar_prediction(
        manifest,
        submission,
        reveal,
        manifest_hash,
        submission_hash,
        raw_record_present=False,
    )
    assert missing_record.outcome == INVALID
    assert "MISSING_RAW_RECORD" in missing_record.invalidation_reasons

    abstaining = PredictionSubmission(
        submission_id="submission-demo-abstain",
        protocol_id=manifest.protocol_id,
        candidate_id="rei-candidate-demo",
        prediction_payload={},
        uncertainty_payload={"reason": "insufficient evidence"},
        abstention_state=True,
        submission_timestamp="2098-12-31T23:00:00Z",
    )
    abstain_hash = sha256_obj(asdict(abstaining))
    abstain_record = score_scalar_prediction(
        manifest,
        abstaining,
        reveal,
        manifest_hash,
        abstain_hash,
        raw_record_present=True,
    )
    assert abstain_record.outcome == ABSTAIN

    return {
        "package_status": READY,
        "g4_status": "OPEN",
        "g5_status": "OPEN",
        "clean_synthetic_protocol_test": clean.outcome,
        "tamper_test": tamper.outcome,
        "posthoc_test": posthoc.outcome,
        "missing_record_test": missing_record.outcome,
        "abstention_test": abstain_record.outcome,
        "real_world_actuation_authority": 0,
        "canonical": False,
    }


if __name__ == "__main__":
    print(json.dumps(run_sanity(), sort_keys=True, indent=2))
