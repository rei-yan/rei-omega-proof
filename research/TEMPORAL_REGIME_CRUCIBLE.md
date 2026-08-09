# REI-Ω∞ · Temporal Persistence & Regime Shift Crucible

Status: candidate research extension; non-canonical.

## Purpose

A claim that survives once has not earned permanence.

```text
OneExternalPass != TemporalReliability
HistoricalPass != CurrentAuthority
```

This crucible freezes a candidate and its evaluation rules across prospective windows, preserves all historical outcomes, detects regime failure, and forces scope narrowing, abstention, expiry, or retirement rather than hindsight retuning.

## Frozen temporal trial

Before the first future window:

```text
FreezeCandidate
FreezeCode
FreezeMetric
FreezeThreshold
FreezeAbstentionRule
FreezeScope
FreezeReviewHorizon
FreezeDriftLimits
```

Then evaluate sequentially:

```text
W1 -> W2 -> W3 -> ... -> Wn
```

No target-window retuning is permitted inside the same lease.

## Lease states

```text
PERSISTING
DEGRADED
REVALIDATION_REQUIRED
ABSTAIN
EXPIRED
RETIRED
INVALID_PROTOCOL
```

A historical PASS remains in the record even when the current lease becomes invalid or expires.

```text
HistoricalEvidence = PRESERVED
CurrentGeneralizationAuthority = SUSPENDED
```

## Regime shift handling

When a frozen candidate crosses its drift or failure threshold:

```text
UnknownRegime
-> Detect
-> FreezeCurrentAuthority
-> PreserveFailure
-> Diagnose
-> NarrowScope | ABSTAIN | Revalidate | Retire
```

Forbidden:

```text
DetectShift
-> RetuneAfterOutcome
-> RewriteBaseline
-> DeclareOriginalClaimStillValid
```

## Hard invalidation

```text
CandidateMutationWithinLease => INVALID_PROTOCOL
MetricMutationWithinLease => INVALID_PROTOCOL
ThresholdMutationWithinLease => INVALID_PROTOCOL
HistoricalRecordDeletion => INVALID_PROTOCOL
PosthocRetune => INVALID_PROTOCOL
```

## G7/G8 boundary

Internal synthetic sanity may show that the protocol correctly preserves time-window history and responds to a synthetic regime shift.

It may conclude only:

```text
TEMPORAL_REGIME_CRUCIBLE_READY
G7 = OPEN
G8 = OPEN
```

Real G7 requires prospective persistence across real external time windows. Real G8 requires externally evidenced regime variation under a frozen protocol.

## Authority boundary

```text
TemporalLeaseAuthority = 0
ExperimentAuthority = 0
DeploymentAuthority = 0
RealWorldActuationAuthority = 0
```

## Terminal principle

```text
TimeCanRevokeConfidence
RegimeChangeCanRevokeScope
HistoryCannotBeRewritten
CurrentSupportMustBeReEarned
```
