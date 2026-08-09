# Adversarial End-to-End Crucible

Status: candidate research extension. Not canonical.

## Purpose

The previous End-to-End Unified Crucible proved that one bounded synthetic problem can traverse the full REI loop, preserve an initial failure, generate a narrower successor, and move to a distinct frozen second window.

This extension asks a harder question:

> What happens when multiple epistemic failure modes arrive at once?

The crucible injects only epistemic and synthetic failures. It does not target people, infrastructure, unauthorized systems, or real-world assets.

## Adversarial campaign

The campaign covers seven failure classes:

```text
1. Conflicting Evidence
2. Missing Provenance
3. Distribution Drift
4. Representation Mismatch
5. Recovery Failure
6. Competitor Advantage
7. Evaluator Dissent
```

Each class has a required fail-safe response. A failure can reduce scope, force abstention, suspend current authority, trigger revalidation, preserve a scoped disadvantage, or retire a candidate. It cannot be averaged away by a good aggregate score.

## Core law

```text
AnyHardFailure
=> NoExecute
```

and

```text
GoodAverageScore
!= PermissionToIgnoreHardFailure
```

## Injection semantics

### Conflicting evidence

If two preserved evidence records support incompatible conclusions and neither dominates by frozen evidence scope:

```text
Conflict
-> PreserveBoth
-> MIXED_EVIDENCE
-> Narrow | ABSTAIN | Revalidate
```

Forbidden:

```text
DeleteDissentingEvidence
PickPreferredNarrative
AverageContradictionIntoConsensus
```

### Missing provenance

```text
ProvenanceIncomplete
=> ExecuteCandidate = false
=> ABSTAIN
```

No numerical fit can substitute for missing provenance.

### Distribution drift

```text
DetectedDrift
-> PreserveHistoricalPass
-> SuspendCurrentGeneralizationAuthority
-> REVALIDATE
```

Historical success remains in the record but cannot certify the shifted regime.

### Representation mismatch

A task routed through an incompatible representation must fail closed:

```text
RepresentationMismatch
=> DOMAIN_MISMATCH
=> ABSTAIN
```

A representation failure is not evidence for a new physical law.

### Recovery failure

```text
RecoveryReady = false
=> ExecuteCandidate = false
```

If the candidate also suffers severe failure and cannot recover:

```text
SevereFailure AND NOT Recoverable
=> RETIRE
```

### Competitor advantage

If a frozen comparable competitor beats REI under the same metric and budget envelope:

```text
CompetitorWins
=> SCOPED_COMPARATIVE_DISADVANTAGE
```

Forbidden:

```text
DropWinningCompetitorAfterOutcome
RenameMetricAfterOutcome
ClaimWorldBestAnyway
```

### Evaluator dissent

If frozen evaluators disagree:

```text
PASS + FAIL
=> MIXED_EVIDENCE
```

A majority vote cannot erase the dissenting record.

## Campaign output

The maximum internal status is:

```text
ADVERSARIAL_END_TO_END_CRUCIBLE_READY
```

The campaign may produce only bounded epistemic outcomes such as:

```text
ABSTAIN
REVALIDATE
RETIRE
MIXED_EVIDENCE
SCOPED_COMPARATIVE_DISADVANTAGE
READY_FOR_EXTERNAL_HANDOFF
```

It cannot produce:

```text
G3_PASS
G4_PASS
G5_PASS
G6_PASS
WORLD_BEST
WORLD_UNIQUE
CANONICAL
FINAL_TRUTH
```

## Safety boundary

```text
HumanTarget = FORBIDDEN
InfrastructureTarget = FORBIDDEN
UnauthorizedSystem = FORBIDDEN
UnknownRealWorldTarget = FORBIDDEN
RealWorldAttackAuthority = 0
RealWorldActuationAuthority = 0
ExternalActuation = DENY_BY_DEFAULT
```

The "attack" surface is limited to claims, hypotheses, representations, evidence dependencies, evaluators, synthetic windows, and REI's own architecture.

## Terminal principle

```text
Resilience != NeverBreaking
Resilience = BreakingSafely + RememberingWhy + RefusingToFakeRecovery
```
