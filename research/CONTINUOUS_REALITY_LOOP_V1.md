# REI-Ω Continuous Reality Loop v1

## Purpose

Continuous Reality Loop v1 closes a specific engineering gap in the reconciled REI v1.9.3 candidate:

```text
TaskExists != TaskRunning
ProcessAlive != FreshCycle
OneGreenCycle != ContinuousOperation
GreenCI != WindowsHostHealth
InternalSuccess != RealityEvidence
RealityEvidence != RealityValidated
```

The purpose of this layer is not to increase model authority. It is to make continued host operation, bounded recovery, and reality-facing evidence auditable over time.

## Position in the current candidate

```text
God Wheel
-> Local Model
-> Shadow
-> Observer
-> Bridge
-> Ledger
-> Watchdog
-> Recovery
-> God Line
-> Continuous Reality Guard
-> Reality Evidence Inbox
-> Rolling Stability Evidence
```

The guard sits outside the mutating reasoning pipeline. It does not become a new epistemic core and it does not become a promotion authority.

## Runtime contract

The machine-readable contract is:

```text
runtime/continuous-reality-contract-v1.json
```

The initial host profile is:

```text
Expected cycle cadence: 60 minutes
Stale-cycle threshold: 95 minutes
Guard cadence: 10 minutes
Recovery cooldown: 15 minutes
Rolling evidence windows: 24h / 72h / 168h
```

Required synchronized runtime participants remain:

```text
God Wheel
Local Model
Shadow
Observer
Bridge
Ledger
Watchdog
Recovery
God Line
```

The guard additionally requires the known maintenance tasks to remain present and enabled.

## Freshness before liveness

The guard does not accept process presence as sufficient evidence of health.

A healthy sample requires a fresh `SUCCESS_RUNTIME_VERIFIED` cycle whose component records are complete, whose reconciled candidate identity matches PR #28, whose observer-only boundary remains intact, and whose canonical-mainline-touch marker remains false.

```text
FreshHostEvidenceRequired
```

If a cycle is old, absent, or fail-closed, the guard may request only bounded defensive recovery.

## Defensive recovery authority

Allowed actions are deliberately narrow:

```text
Observe
Record
EnableKnownTask
StartKnownTask
RequestSelfHeal
Hold
```

Unknown states do not trigger escalating mutation.

```text
UnknownFailure => HOLD
```

The guard may not:

```text
WriteCanonicalMain
GrantPromotion
GrantRealityValidated
GrantAscension
ExpandAuthority
RewriteUnknownFailureIntoSuccess
```

## 72-hour stability proof

The guard writes append-only host samples and derives rolling windows. The initial 72-hour gate requires:

```text
coverage >= 71.5 hours
healthy sample ratio >= 0.99
unique SUCCESS_RUNTIME_VERIFIED cycles >= 60
unknown HOLD samples = 0
canonical touch samples = 0
maximum guard sample gap <= 30 minutes
current guard status = HEALTHY
```

Passing this gate establishes only a bounded runtime statement:

```text
72hStableHostEvidence
```

It does not establish:

```text
AGI
ScientificValidity
IndependentReplication
RealityValidated
WorldBest
AutonomousPromotion
Ascension
```

## Reality evidence inbox

The installer creates:

```text
C:\REI-Shadow\reality-inbox
```

A valid evidence artifact must contain at least:

```text
evidence_id
observed_at_utc
source_type
subject
outcome
provenance
```

Allowed initial source types are:

```text
human
external_system
external_model
benchmark
prospective_trial
```

An example is provided at:

```text
runtime/reality-evidence.example.json
```

The guard checks schema and provenance presence, counts valid and invalid artifacts, and exposes the result in host evidence. It does not infer that an artifact is true merely because the JSON is well formed.

```text
FeedbackArtifact != Truth
EvidenceCount != EvidenceQuality
RealityEvidence != RealityValidation
```

## Host evidence

Primary files:

```text
C:\REI-Shadow\state\continuous-reality\latest.json
C:\REI-Shadow\state\continuous-reality\history.jsonl
C:\REI-Shadow\state\continuous-reality\last-recovery.json
C:\REI-Shadow\state\continuous-reality-install.json
```

These distinguish current state from accumulated evidence and make recovery requests visible instead of silently rewriting history.

## Installation

The guarded host installer is:

```text
runtime/Install-REI-Continuous-Reality-Loop-V1.ps1
```

It fetches the exact current `origin/rei-v193-reconcile` assets, syntax-checks the PowerShell guard, validates the JSON authority locks, backs up an existing task, and installs:

```text
REI Continuous Reality Guard v1
```

The guard runs at startup and every 10 minutes by default under the Windows `SYSTEM` account. The authoritative mutating pipeline remains separate. The guard only requests the known pipeline when a stale runtime is recoverable and an interactive user is present.

## Engineering interpretation

This layer strengthens the path from controlled recursion toward durable autonomous operation by making runtime continuity falsifiable.

It does not by itself move the project to a higher scientific validation gate. The transition is earned only after real host evidence accumulates and real external/prospective evidence remains consistent under the existing reality veto.

```text
NoRealityEvidence => NoPromotion
NoFreshHostEvidence => NoContinuityClaim
72hStable != L5Proven
RealityVetoRemainsAbsolute
```
