# REI-Ω∞ External Reality Trial Kit

Status: candidate research extension only. Non-canonical. G4/G5 remain OPEN.

## Purpose

The External Reality Trial Kit turns the existing commit-reveal bridge into a third-party-operable trial envelope. Its job is not to make REI win. Its job is to make the trial hard to rewrite after the outcome is known.

The kit evaluates claims. It does not authorize experiments, deployment, intervention, exploitation, or attack.

## Terminal rule

```text
RealityVerdict > CandidateNarrative
FrozenRecord > PosthocExplanation
ExternalEvidence > InternalConfidence
DefeatPreserved > VictoryRewritten
```

## Roles

A trial has at least four explicit roles:

```text
CandidateOwner
ExternalController
IndependentEvaluator
RecordCustodian
```

The same declared actor must not occupy incompatible roles inside one trial. Declared role separation is necessary but does not by itself prove genuine institutional independence.

```text
DeclaredSeparation != ProvenIndependence
```

## Trial objects

```text
TrialManifest
CandidateSubmission
HiddenCommitmentEnvelope
RevealEnvelope
EvaluatorAttestation
TrialRecord
FailureArchiveEntry
```

Every object that can affect outcome must be frozen or commitment-bound before reveal.

## Sequence

```text
1. Freeze trial manifest
2. Freeze candidate/code/environment commitments
3. Freeze metric/threshold/abstention policy
4. External controller commits hidden evidence hash
5. Candidate submits prediction commitment
6. Submission closes
7. External controller reveals hidden evidence
8. Independent evaluator verifies commitments
9. Frozen scorer computes outcome
10. Record custodian preserves raw record and failures
11. Outcome = PASS | FAIL | ABSTAIN | INVALID_PROTOCOL
```

## Hard invalidation

Any one of the following invalidates the protocol:

```text
ManifestMutationAfterFreeze
PredictionMutationAfterFreeze
HiddenCommitmentMismatch
HiddenAnswerAccessBeforeFreeze
MetricChangeAfterReveal
ThresholdChangeAfterReveal
PosthocRetune
RevealBeforeSubmissionClose
MissingRawRecord
MissingEvaluatorAttestation
RoleCollision
EvaluatorUsesUnfrozenMetric
```

Hard vetoes cannot be averaged away by a good score.

## Abstention

Correct abstention is a first-class outcome.

```text
InsufficientEvidence -> ABSTAIN
UnknownRegime -> ABSTAIN
Unidentifiable -> ABSTAIN
```

Abstention is not a pass and not a failure rewrite.

## Evaluator attestation

The evaluator must attest at minimum:

- manifest hash verified
- submission hash verified
- hidden commitment verified
- frozen metric used
- frozen threshold used
- no known pre-freeze hidden-answer access
- raw record present
- no post-hoc retuning accepted

The attestation is evidence about protocol execution, not proof of universal independence.

## Failure archive

Every failed or invalid trial must preserve:

```text
trial_id
claim_id
frozen_manifest_hash
submission_hash
hidden_commitment
revealed_evidence_hash
outcome
score
invalidation_reasons
failure_mode
scope_effect
repair_allowed
revalidation_required
```

```text
NoDefeatDeletion
NoHistoricalPassRewriting
```

## Authority boundary

```text
PredictionAuthority = 0
MeasurementProposalAuthority = 0
ExperimentAuthority = 0
DeploymentAuthority = 0
RealWorldActuationAuthority = 0
```

## Gate boundary

Internal CI may establish only:

```text
EXTERNAL_REALITY_TRIAL_KIT_READY
```

It may not establish:

```text
G4_PASS
G5_PASS
G6_PASS
CanonicalPromotion
WorldBest
WorldUnique
Invincible
```

G4/G5 require genuinely external prospective or hidden evidence and an independently controlled reveal.

## Meaning of the "invincible" path

```text
InvincibleResearchProperty != NeverDefeated
InvincibleResearchProperty = DefeatCannotBeErasedOrConvertedIntoVictory
```

The strongest acceptable form of REI is therefore not a system that cannot lose. It is a system whose losses remain visible enough to constrain the next claim.