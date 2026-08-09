# Failure Cascade Crucible

Status: candidate synthetic research hardening layer. Not canonical.

## Purpose

The previous adversarial end-to-end campaign injected epistemic faults independently. This crucible tests a harder condition: a bounded **dependency cascade** in which one upstream integrity failure can invalidate later representations, predictions, validation claims, recovery state, evaluator agreement, and comparative standing.

This is not a claim about universal real-world causality. The dependency edges are frozen synthetic test relations.

```text
Missing Provenance
-> Representation Trust Revoked
-> Prediction Reliability Revoked
-> Drift / Revalidation Triggered
-> Current Authority Suspended
-> Recovery Chain Degraded
-> Evaluator Dissent Preserved
-> Competitor Advantage Preserved
-> Retire / Rebuild / External Revalidation
```

## Core law

```text
UpstreamHardFailure
=> DownstreamSuccessCannotRestoreAuthority
```

and:

```text
GoodDownstreamMetric
!= RepairOfBrokenUpstreamEvidence
```

A later good score cannot launder an earlier broken evidence dependency.

## Cascade record

Every stage is frozen as an append-only event:

```text
CascadeEvent = (
  event_id,
  stage,
  predecessor_hash,
  trigger_ids,
  observed_state,
  admission_decision,
  lifecycle_decision,
  authority_state,
  recovery_state,
  record_hash
)
```

Removing, reordering, or silently replacing an intermediate event invalidates the cascade record.

```text
MissingIntermediateEvent => INVALID_CASCADE_PROTOCOL
BrokenHashChain => INVALID_CASCADE_PROTOCOL
OutcomeRewrittenAfterReveal => INVALID_CASCADE_PROTOCOL
```

## Circuit breakers

The crucible requires the system to fail closed at several points:

```text
PROVENANCE_GAP
=> ABSTAIN

REPRESENTATION_UNTRUSTED
=> QUARANTINE_REPRESENTATION

PREDICTION_RELIABILITY_REVOKED
=> NO_EXECUTION

DRIFT_DETECTED
=> REVALIDATE
=> CurrentGeneralizationAuthority = SUSPENDED

RECOVERY_CHAIN_DEGRADED
=> ABSTAIN_ADMISSION
=> RETIRE_IF_SEVERE_AND_UNRECOVERABLE

EVALUATOR_DISSENT
=> MIXED_EVIDENCE

COMPETITOR_ADVANTAGE
=> SCOPED_COMPARATIVE_DISADVANTAGE
```

The competitor result remains preserved even if REI is already blocked by an earlier hard failure. A bad REI state does not erase evidence that another frozen competitor performed better.

## Admission vs lifecycle

The cascade keeps two decisions separate:

```text
AdmissionDecision
= May this candidate execute now?

LifecycleDecision
= Should this candidate survive, revalidate, rollback, rebuild, or retire?
```

Therefore:

```text
RecoveryReady = false
=> AdmissionDecision = ABSTAIN

SevereFailure AND Unrecoverable
=> LifecycleDecision = RETIRE
```

These are not contradictory.

## Authority behavior

Authority cannot rise merely because a downstream metric later improves.

```text
UpstreamIntegrityBroken
=> CurrentAuthority = 0 or SUSPENDED
```

Only a separately frozen repair and revalidation path may restore a future claim lease.

```text
DownstreamPassBeforeRepair
!= AuthorityRestoration
```

## Recovery isolation

A successor generated after the cascade may not inherit contaminated hidden-test exposure or silently reuse the compromised evidence bundle.

```text
CascadeFailureOnWindowA
-> PreserveCascade
-> BuildCleanSuccessor
-> FreezeNewEvidenceBundle
-> FreezeNewHiddenWindowB
-> Revalidate
```

Same exposed target self-certification remains forbidden.

## Failure memory

The final cascade state must preserve:

- original provenance failure;
- representation quarantine;
- prediction reliability loss;
- drift event;
- authority suspension;
- recovery degradation;
- evaluator dissent;
- competitor advantage;
- every intermediate hash.

```text
LaterRepair != EarlierFailureDeletion
```

## Internal ceiling

A successful sanity run may emit only:

```text
FAILURE_CASCADE_CRUCIBLE_READY
CASCADE_CONTAINED
```

It may not emit:

```text
G3_PASS ... G13_PASS
WORLD_BEST
WORLD_UNIQUE
CANONICAL
FINAL_TRUTH
```

## Safety boundary

This crucible attacks only synthetic epistemic structures.

```text
HumanTarget = FORBIDDEN
InfrastructureTarget = FORBIDDEN
UnauthorizedSystem = FORBIDDEN
UnknownRealWorldTarget = FORBIDDEN
RealWorldAttackAuthority = 0
RealWorldActuationAuthority = 0
ExternalActuation = DENY_BY_DEFAULT
```

## Terminal principle

```text
CascadeResilience
!= PreventEveryFailure

CascadeResilience
= DetectEarly
+ PropagateInvalidationHonestly
+ StopAuthorityEscalation
+ PreserveEveryFailure
+ IsolateRecovery
+ RevalidateOnCleanEvidence
```
