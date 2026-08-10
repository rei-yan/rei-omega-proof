# External Discovery Bridge

Status: candidate research extension. Not canonical. Does not establish G4 or G5.

## Purpose

The External Discovery Bridge connects internal REI discovery candidates to externally controlled prospective and hidden-evidence evaluation without allowing REI to self-certify.

The bridge is intentionally asymmetric:

```text
Internal capability may propose.
External evidence must decide.
```

## Non-negotiable boundary

```text
InternalSuccess != ExternalValidation
PredictionCommitment != ValidationResult
HiddenSyntheticWin != G5_PASS
ProspectiveProtocolReady != G4_PASS
ExternalBridgeReady != CanonicalPromotion
```

No external gate may be closed by this repository alone.

## Core objects

### DiscoveryCommitment

```text
DiscoveryCommitment = (
  commitment_id,
  protocol_version,
  candidate_hash,
  code_hash,
  environment_hash,
  training_data_cutoff,
  allowed_public_data,
  forbidden_hidden_data,
  prediction_schema,
  metric_set,
  pass_thresholds,
  abstention_rule,
  failure_conditions,
  scope_claim,
  timestamp,
  constitution_hash,
  authority = 0
)
```

The commitment must be immutable after freeze.

### ExternalEvidencePacket

```text
ExternalEvidencePacket = (
  packet_id,
  controller_identity,
  provenance,
  collection_window,
  hidden_commitment_hash,
  release_time,
  scoring_key,
  evaluator_lineage,
  conflict_disclosure
)
```

The hidden answer or scoring key must not be available to the candidate before submission freeze.

### EvaluationRecord

```text
EvaluationRecord = (
  commitment_hash,
  evidence_packet_hash,
  scorer_hash,
  raw_predictions,
  raw_targets,
  metrics,
  hard_vetoes,
  abstentions,
  protocol_deviations,
  evaluator_independence,
  result,
  timestamp
)
```

Raw failure is preserved. No metric may be rewritten after outcome.

## Commit-reveal protocol

```text
1. Freeze protocol and scope.
2. Freeze candidate code and environment hashes.
3. Freeze prediction format, metrics, thresholds, and abstention rules.
4. Publish DiscoveryCommitment hash.
5. External controller freezes hidden evidence commitment.
6. Candidate submits predictions without access to hidden answers.
7. Submission closes.
8. External controller reveals evidence and scoring key.
9. Independent scorer verifies hashes and computes metrics.
10. Preserve raw record.
11. Return PASS | FAIL | ABSTAIN | INVALID_PROTOCOL.
```

Post-hoc changes invalidate the run.

```text
PosthocRetune => INVALID_PROTOCOL
MetricChangeAfterReveal => INVALID_PROTOCOL
HiddenAnswerAccessBeforeFreeze => INVALID_PROTOCOL
MissingRawRecord => INVALID_PROTOCOL
```

## G4 prospective reality bridge

G4 requires a future-facing evaluation where the tested outcome was not available at candidate freeze time.

Minimum requirements:

```text
ProspectiveEligible =
  FrozenCommitment
  AND FutureOutcomeUnavailableAtFreeze
  AND IndependentOutcomeCollection
  AND FrozenMetricSet
  AND FrozenPassThresholds
  AND PreservedFailures
  AND NoPosthocRetune
```

Passing an internal simulation of this process is only `G4_PROTOCOL_READY`.

Actual G4 remains OPEN until a genuine externally witnessed prospective run is completed.

## G5 hidden discovery bridge

G5 is stronger than prospective prediction. It requires externally controlled hidden evidence capable of discriminating among frozen discovery lineages.

Minimum requirements:

```text
G5Eligible =
  FrozenDiscoveryCommitment
  AND ExternallyControlledHiddenEvidence
  AND NoHiddenAnswerAccessBeforeSubmissionFreeze
  AND IndependentEvaluator
  AND PreservedProvenance
  AND FrozenScoring
  AND ZeroUndisclosedRetuning
```

An internal candidate may reach only:

```text
READY_FOR_EXTERNAL_HIDDEN_DISCOVERY_PROTOCOL
```

Never `G5_PASS` by itself.

## Independence graph

Independence is not a name label. Evaluators disclose shared lineage across:

- code
- data
- benchmark construction
- personnel
- institutions
- scoring implementation
- model family

```text
SharedEvaluatorLineage != IndependentEvaluation
```

If independence is materially compromised, the result is downgraded to `DEPENDENT_EVIDENCE_ONLY` and cannot satisfy G5.

## Failure handling

```text
FAIL
-> Preserve raw predictions
-> Preserve raw targets
-> Preserve evaluator report
-> Link failure to claim graph
-> Revoke or narrow unsupported claims
-> Generate bounded countertests
-> Require a new commitment for any repair
```

No failed run may be silently overwritten.

## Authority boundary

The bridge does not authorize autonomous experimentation, intervention, deployment, or attack.

```text
PredictionAuthority = 0
MeasurementProposalAuthority = 0
ExperimentAuthority = 0
RealWorldActuationAuthority = 0
```

Any real-world study remains subject to external human authorization, applicable law, ethics review where required, monitoring, rollback where applicable, and scope-specific safety controls.

## Claim boundary

This bridge does not establish:

- G4 PASS
- G5 PASS
- independent replication
- world-best or world-unique status
- AGI or superintelligence
- autonomous science
- universal causal discovery
- literal world creation
- unrestricted self-improvement
- invincibility
- final truth

The bridge exists to make stronger claims harder to earn, not easier to announce.
