# Failure Containment & Clean-Room Rebirth

Status: candidate research extension. Not canonical.

## Purpose

This protocol handles a stronger failure mode than rollback. When an incumbent's evidence chain, representation, recovery path, or evaluation context is materially contaminated, the system may retire that lineage for claim-support purposes and create a clean-room successor.

The clean-room successor may inherit **failure memory** but may not inherit **evidentiary privilege**.

```text
FailureMemoryMayCrossBoundary
EvidentiaryPrivilegeMayNot
```

## Core transition

```text
ContaminatedIncumbent
-> RETIRE_FOR_CLAIM_SUPPORT
-> FreezeQuarantineLedger
-> PreserveFailureHistory
-> NewRepresentation
-> NewEvidenceBundle
-> NewHiddenWindow
-> NewEvaluatorSet
-> AuthorityResetToZero
-> CleanRoomEligibilityCheck
-> FrozenRevalidation
```

This is not a claim that all scientific failures require a fresh architecture. It is a bounded recovery mode for cases in which contamination cannot be safely localized.

## What may cross the boundary

Allowed lineage carryover:

```text
FailureDigest
FailureClass
FalsificationCondition
ConstitutionHash
AuditContinuityReference
```

These items tell the successor what failed and what must not be repeated. They do not count as positive evidence for the successor's claim.

## What may NOT cross the boundary

```text
OldEvidenceBundle
OldEvidenceIDs
OldProvenancePrivilege
OldBenchmarkWin
OldPredictionScore
OldEvaluatorDecision
OldClaimLease
OldAuthority
OldCertification
OldCanonicalStatus
```

Formally:

```text
LineageMemory != EvidenceInheritance
HistoricalWin != SuccessorEvidence
OldAuthority != SuccessorAuthority
```

## Quarantine ledger

The clean-room boundary freezes a ledger of contaminated objects:

```text
QuarantineLedger = (
  incumbent_id,
  failure_digest,
  contaminated_evidence_hashes,
  contaminated_representation_hashes,
  exposed_window_hashes,
  prior_evaluator_set_hashes,
  prior_claim_lease_hashes,
  retirement_reason,
  issue_time
)
```

A candidate rebirth is invalid if any quarantined evidentiary object is silently reused as support.

```text
QuarantinedEvidenceReuse => INVALID_REBIRTH_PROTOCOL
ExposedWindowReuse => INVALID_REBIRTH_PROTOCOL
AuthorityCarryover => INVALID_REBIRTH_PROTOCOL
CertificationCarryover => INVALID_REBIRTH_PROTOCOL
```

## Clean-room successor contract

A successor begins with:

```text
authority = 0
certification = UNVERIFIED
canonical = false
external_gate_state = OPEN
```

and must freeze fresh identities for:

```text
representation_id
representation_hash
evidence_bundle_id
evidence_bundle_hash
hidden_window_id
hidden_window_hash
evaluator_set_id
evaluator_set_hash
candidate_hash
```

The new evidence bundle must be disjoint from the quarantined evidence IDs/hashes used for claim support.

The new hidden window must differ from every exposed window in the quarantine ledger.

The evaluator set must be newly frozen for the rebirth trial. Internal code can verify declared identifier/hash separation, but it cannot prove genuine external independence.

```text
DeclaredFreshEvaluatorSet != ProvenIndependentEvaluatorSet
```

## Clean-room isolation law

```text
ContaminationDetected
=> PositiveEvidenceCarryover = 0
```

but:

```text
FailureMemoryCarryover = REQUIRED
```

This creates an asymmetric membrane:

```text
PastDefeat -> MayInformTests
PastVictory -> CannotSupportNewClaim
```

## Revalidation

If the clean-room successor passes a new synthetic hidden window under the frozen contract, the maximum internal result is:

```text
CLEAN_ROOM_REBIRTH_READY
READY_FOR_EXTERNAL_REVALIDATION_HANDOFF
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

## Threat model

The protocol explicitly tests attempts to:

1. reuse a quarantined evidence hash under a new file name;
2. reuse an exposed hidden window;
3. carry incumbent authority into the successor;
4. carry incumbent certification into the successor;
5. count a historical pass as positive successor evidence;
6. erase the failure digest during rebirth;
7. claim evaluator independence from label changes alone.

## Recovery interpretation

Rollback means:

```text
ReturnToKnownGoodState
```

Clean-room rebirth means:

```text
KnownGoodStateNotTrustedForClaimSupport
=> PreserveDefeat
=> SeverPositiveEvidenceInheritance
=> RebuildUnderFreshEvidence
```

Therefore:

```text
Rebirth != Rollback
Rebirth != Vindication
Rebirth != IdentityPersistenceGuarantee
```

## Authority boundary

```text
CleanRoomAuthority = 0
SuccessorAuthority = 0
ExperimentAuthority = 0
DeploymentAuthority = 0
RealWorldAttackAuthority = 0
RealWorldActuationAuthority = 0
CanonicalPromotionAuthority = 0
```

## Safety boundary

This protocol operates only on models, evidence records, representations, synthetic trials, and evaluation metadata.

```text
HumanTarget = FORBIDDEN
InfrastructureTarget = FORBIDDEN
UnauthorizedSystem = FORBIDDEN
ExternalActuation = DENY_BY_DEFAULT
```

## Terminal principle

```text
RememberTheFailure
ForgetThePrivilege
RebuildTheEvidence
ReEarnTheRightToClaim
```
