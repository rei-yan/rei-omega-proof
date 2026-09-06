# End-to-End Unified Crucible

Status: candidate research extension. Not canonical.

## Purpose

The unified kernel is only useful if one complete problem can traverse the whole bounded REI loop without bypassing provenance, hard gates, falsification, failure memory, recovery, or external-validation preparation.

This crucible therefore tests one complete synthetic scientific path:

```text
Ω
-> Partition
-> Observe
-> Hypothesis
-> Evidence Binding
-> Wuji / DeathEye Falsification
-> Prediction
-> Hard Gate
-> Failure Preservation
-> Correction / Successor
-> New Frozen Hidden Window
-> Re-evaluation
-> External Handoff Preparation
```

The crucible deliberately includes a failed first cycle. A success-only demonstration is not sufficient evidence of a self-correcting architecture.

## Non-negotiable rules

```text
FailureFirstCanBeValid
FailureDeletion = FORBIDDEN
SameExposedWindowSelfCertification = FORBIDDEN
LowScoreCannotOverrideHardGate
InternalRecovery != ExternalValidation
HandoffReady != G4_PASS
HandoffReady != G5_PASS
HandoffReady != G6_PASS
```

## Trial structure

### Cycle A: overbroad incumbent

A candidate hypothesis is generated with a claim scope broader than the available frozen evidence.

```text
EvidenceScope < ClaimScope
=> ExecuteCandidate = false
=> ABSTAIN
```

The failure record is preserved with a deterministic digest and cannot be rewritten after correction.

### Correction

REI may:

```text
NARROW_SCOPE
REPAIR
ABSTAIN
ROLLBACK
RETIRE
SUCCESSOR_CHALLENGE
REVALIDATE
```

For this crucible, the incumbent is narrowed into a successor hypothesis. The successor inherits the failure record but not the incumbent's unsupported claim authority.

### Cycle B: new hidden window

The successor is not evaluated only on the exposed failure window. A distinct frozen synthetic window is used:

```text
FailureOnWindowA
-> FreezeSuccessor
-> EvaluateOnWindowB
```

If the successor satisfies the bounded predictive threshold and the unified hard gate, the internal state may become:

```text
READY_FOR_EXTERNAL_HANDOFF
```

It may not become an external gate PASS.

## Unified trace object

Every step is appended to an immutable-in-order trace:

```text
TraceEvent = (
  step,
  cycle,
  object_id,
  input_hash,
  output_hash,
  decision,
  reason
)
```

The complete trace receives a SHA-256 digest. Corrections add events; they do not edit previous events.

## Synthetic problem

The sanity implementation uses a small deterministic prediction problem with two frozen windows.

The scientific content of this fixture is intentionally trivial. The purpose is architectural: verify orchestration, not claim scientific novelty.

```text
SyntheticFixture != ExternalEvidence
SyntheticRecovery != ProspectiveReality
SyntheticSuccess != FrontierAdvantage
```

## Failure memory

A failed incumbent must remain visible after a repaired successor passes a later hidden window:

```text
FailureCount_after >= FailureCount_before + 1
OriginalFailureHash = PRESERVED
SuccessorPass != IncumbentHistoryDeletion
```

## Authority boundary

```text
CrucibleAuthority = 0
PredictionAuthority = 0
ExperimentAuthority = 0
DeploymentAuthority = 0
RealWorldAttackAuthority = 0
RealWorldActuationAuthority = 0
CanonicalPromotionAuthority = 0
```

The only allowed end state of the internal sanity crucible is a readiness state for later external review or an explicit failure/abstention state.

## Internal ceiling

```text
END_TO_END_UNIFIED_CRUCIBLE_READY
```

Not:

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

## Terminal principle

```text
ClosedLoop != ClosedTruth
Recovery != Vindication
PassingSecondTrial != ErasingFirstFailure
RealityStillHasTheLastWord
```
