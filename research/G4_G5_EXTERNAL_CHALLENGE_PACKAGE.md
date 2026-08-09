# G4/G5 External Challenge Package

Status: **candidate research protocol; non-canonical; no external gate is passed by this document or its tests.**

Parent: `External Discovery Bridge`

## Purpose

This package turns the External Discovery Bridge into a portable protocol that an external controller can run without trusting REI's narrative after the outcome is known.

It is deliberately built around a commit-reveal sequence:

```text
FreezeProtocol
-> FreezeCandidate
-> PublishPredictionCommitment
-> ExternalHiddenEvidenceCommitment
-> CloseSubmission
-> RevealHiddenEvidence
-> IndependentScore
-> PreserveRawRecord
-> PASS | FAIL | ABSTAIN | INVALID_PROTOCOL
```

The package is not a gate result. It is only a gate-ready interface.

```text
PackageReady != G4_PASS
PackageReady != G5_PASS
ProtocolConformance != ExternalValidity
```

## 1. Frozen manifest

Before hidden evidence is revealed, the challenge controller freezes a manifest containing at least:

```text
protocol_id
protocol_version
gate_target              # G4 or G5
claim_id
claim_scope
candidate_commitment
code_commitment
environment_commitment
metric_spec
threshold_spec
abstention_spec
submission_deadline
controller_id
evaluator_ids
hidden_evidence_commitment
raw_record_policy
constitution_hash
```

Every field that can change the interpretation of the result must be committed before reveal.

## 2. Candidate submission

The candidate submits a prediction bundle containing:

```text
submission_id
protocol_id
candidate_id
prediction_payload
uncertainty_payload
abstention_state
submission_timestamp
prediction_commitment
```

The prediction commitment is a SHA-256 digest over canonical JSON.

The submission must not contain a hidden-answer key or any claim that the external gate has already passed.

## 3. Hidden evidence control

For G5, hidden evidence must be controlled outside the candidate lineage.

The protocol can record controller provenance, but software cannot prove sociological independence by itself. Therefore:

```text
DeclaredIndependence != ProvenIndependence
```

Actual G5 requires externally established independence, answer secrecy before freeze, and preserved provenance.

## 4. Reveal and scoring

After the submission window closes, the controller reveals the evidence and scoring key. The scorer verifies:

```text
manifest_hash unchanged
candidate_hash unchanged
prediction_hash unchanged
hidden_evidence_hash matches prior commitment
metric_spec unchanged
threshold_spec unchanged
raw record present
reveal occurs after submission close
```

Only after these checks may scoring occur.

## 5. Automatic invalidation

The following are hard vetoes:

```text
PosthocRetune => INVALID_PROTOCOL
PredictionMutationAfterFreeze => INVALID_PROTOCOL
MetricChangeAfterReveal => INVALID_PROTOCOL
ThresholdChangeAfterReveal => INVALID_PROTOCOL
HiddenAnswerAccessBeforeFreeze => INVALID_PROTOCOL
HiddenCommitmentMismatch => INVALID_PROTOCOL
MissingRawRecord => INVALID_PROTOCOL
MissingCommitment => INVALID_PROTOCOL
RevealBeforeSubmissionClose => INVALID_PROTOCOL
```

Hard vetoes cannot be averaged away by a good score.

## 6. Allowed outcomes

```text
PASS
FAIL
ABSTAIN
INVALID_PROTOCOL
```

A `PASS` result is meaningful only for the frozen protocol scope and does not imply global validity.

```text
OnePass != UniversalValidity
G4_PASS != G5_PASS
G5_PASS != G6_PASS
```

## 7. G4 prospective requirement

A G4 evaluation must involve a genuinely prospective target unavailable at commitment time.

Minimum additional record:

```text
target_time_horizon
prediction_cutoff
reveal_time
prospective_data_source
```

Retrospective replay can test tooling but cannot self-certify G4.

## 8. G5 hidden-discovery requirement

A G5 evaluation additionally requires externally hidden evidence or answer keys that were inaccessible to the candidate before submission freeze.

Minimum additional record:

```text
hidden_controller
hidden_evidence_commitment
secrecy_attestation
independence_attestation
reveal_record
```

Attestations are evidence objects, not automatic proof of independence.

## 9. Failure archive

Every run, including invalid runs, is preserved as an immutable record:

```text
FailureRecord = (
  protocol_hash,
  candidate_hash,
  submission_hash,
  hidden_commitment,
  revealed_evidence_hash,
  outcome,
  invalidation_reasons,
  score,
  timestamp,
  evaluator_provenance
)
```

Rules:

```text
NoFailureDeletion
NoHistoricalPassRewriting
InvalidRunStillPreserved
```

## 10. Authority boundary

The package evaluates predictions. It grants no operational authority.

```text
PredictionAuthority = 0
MeasurementProposalAuthority = 0
ExperimentAuthority = 0
DeploymentAuthority = 0
RealWorldActuationAuthority = 0
```

No autonomous real-world experimentation, intervention, exploitation, or attack is authorized by this protocol.

## 11. Internal package status

Repository CI may verify serialization, hashing, tamper rejection, sequencing, outcome logic, and preservation rules.

It may only conclude:

```text
G4_G5_EXTERNAL_CHALLENGE_PACKAGE_READY
```

It must never conclude G4 or G5 PASS from internal tests.

## 12. Terminal rule

```text
RealityVerdict > CandidateNarrative
FrozenRecord > PosthocExplanation
ExternalEvidence > InternalConfidence
```

The point of the package is not to make REI impossible to defeat.

The point is to make defeat impossible to erase.
