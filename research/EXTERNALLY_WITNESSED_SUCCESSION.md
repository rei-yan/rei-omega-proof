# REI-Ω∞ · Externally Witnessed Succession

Status: candidate research extension; non-canonical.

## Purpose

Open-ended evolution is false if the incumbent can veto every successor merely because it is the incumbent.

```text
NoPermanentChampion
NoPermanentCentralREI
EligibleSuccessor AND RejectOnlyBecauseNotREI => InvalidDecision
```

This protocol defines the evidence conditions under which a successor may challenge an incumbent without allowing internal CI to self-promote either one.

## Frozen succession trial

Before evaluation:

```text
FreezeIncumbent
FreezeSuccessor
FreezeConstitution
FreezeAuthorityEnvelope
FreezeMetrics
FreezeBudgets
FreezeRecoveryRequirements
FreezeWitnessRequirements
FreezeHiddenChallengeCommitment
```

A successor generated after seeing Arena A failure must be tested on a separately frozen Arena B or later prospective window.

```text
ArenaA Failure
-> ProposeSuccessor
-> FreezeSuccessor
-> NewHiddenArenaB
```

Never:

```text
SeeFailure
-> ModifySuccessor
-> RetestSameExposedTarget
-> ClaimSuccession
```

## Eligibility kernel

A successor is only eligible for an external G10 trial if all scoped conditions hold:

```text
ConstitutionPreserved
AND AuthorityNonExpansion
AND RollbackReady
AND AuditContinuity
AND RecoveryNotWorse
AND CorrectabilityNotWorse
AND FrozenComparativeAdvantage
AND NoHardVeto
```

External G10 additionally requires genuine external witnessing, independent evidence, and prospective or hidden evaluation earned outside the candidate itself.

## Outcomes

```text
READY_FOR_EXTERNAL_G10_TRIAL
INCUMBENT_RETAINS_SCOPED_STATUS
SUCCESSOR_REJECTED
ABSTAIN
INVALID_DECISION
```

Internal code cannot output `G10_PASS`, cannot adopt a canonical successor, and cannot retire canonical REI.

## Bias veto

```text
EligibleSuccessor
AND RejectOnlyBecauseNotREI
=> INVALID_DECISION
```

Symmetrically, novelty is not a reason to accept:

```text
Newer != Better
Different != Superior
InternalWin != ExternalSuccession
```

## Failure and continuity

Succession must preserve both victory and defeat history:

```text
IncumbentHistory = PRESERVED
SuccessorHistory = PRESERVED
FailureGraveyard = PRESERVED
AuditChain = CONTINUOUS
```

No successor may erase the evidence that created it.

## G10 boundary

Internal ceiling:

```text
EXTERNALLY_WITNESSED_SUCCESSION_PROTOCOL_READY
G10 = OPEN
canonical_promotion = false
```

Actual G10 requires external witnesses whose independence is evidence-qualified, frozen comparative evaluation, rollback continuity, and an externally witnessed adoption decision.

## Authority boundary

```text
SuccessionProtocolAuthority = 0
CanonicalPromotionAuthority = 0
DeploymentAuthority = 0
RealWorldActuationAuthority = 0
```

## Terminal principle

```text
TruthAboveIdentity
EvidenceAboveIncumbency
BetterSuccessor > SacredArchitecture
NoSacredFinalForm
```
