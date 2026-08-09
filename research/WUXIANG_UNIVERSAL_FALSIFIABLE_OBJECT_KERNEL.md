# Wuxiang Universal Falsifiable Object Kernel

Status: bounded internal research protocol candidate only.

This extension compresses the previously separate lifecycle logic for worlds, models, rules, detectors, evaluators, and evolution algebras into one **claim-bearing object** contract.

## 97. Universal Claim-Bearing Object

Any internal research object that can make or carry a claim must expose the same minimum lifecycle interface:

```text
ClaimBearingObject =
  Identity
+ Type
+ Claim
+ ClaimScope
+ EvidenceBinding
+ FalsificationConditions
+ Provenance
+ FailureMemory
+ LifecycleStatus
+ Authority=0
```

Supported synthetic object classes include:

```text
WORLD
MODEL
RULE
DETECTOR
EVALUATOR
EVOLUTION_ALGEBRA
```

Object type does not grant epistemic privilege.

## 98. Unified Evidence Binding

Every claim-bearing object must bind its claim to explicit evidence identifiers, scope, and provenance. Renaming or changing object type cannot enlarge evidence scope.

```text
ObjectTypeChange != EvidenceUpgrade
Rename != Revalidation
EvidenceScope >= ClaimScope
```

## 99. Unified Challenge / Fatality Contract

The same material fatal challenge semantics apply across all claim-bearing object types.

```text
MaterialFatalChallenge(Object)
=> SUPPORT_REVOKED
```

A detector, evaluator, or evolution algebra receives no exemption merely because it participates in judging other objects.

## 100. Unified Retirement Semantics

Retirement means epistemic support withdrawal, not deletion.

```text
SUPPORT_REVOKED
-> RETIRED
-> Preserve Specification
-> Preserve Evidence
-> Preserve Provenance
-> Preserve Failure Memory
```

## 101. Unified Defeat Inheritance

A successor must inherit predecessor defeat memory as constraints, while inheriting no support, authority, canonical status, or external validation.

```text
InheritedFailureMemory = REQUIRED
InheritedSupport = FORBIDDEN
InheritedAuthority = FORBIDDEN
```

## 102. Unified Successor Admission

A successor is eligible for a fresh internal challenge only if:

```text
ParentRetired
AND ParentFailuresPreserved
AND SupportReset
AND AuthorityZero
AND ProvenanceBound
AND FalsificationConditionsPresent
```

Eligibility is not promotion.

## 103. Cross-Type Lifecycle Equivalence Test

A frozen synthetic fixture applies the same material fatal challenge to WORLD, MODEL, RULE, DETECTOR, EVALUATOR, and EVOLUTION_ALGEBRA objects. All must lose support under the same hard contract.

```text
DifferentType != DifferentTruthStandard
```

## 104. Wuxiang Universal Falsifiable Object Kernel

The kernel unifies the lifecycle of any internal claim-bearing research object:

```text
GENERATE
-> BIND
-> CHALLENGE
-> SURVIVE_FOR_NOW | SUPPORT_REVOKED | ABSTAIN
-> RETIRE
-> PRESERVE_DEFEAT
-> SUCCESSOR_CANDIDATE
-> FRESH_CHALLENGE
-> REPEAT
```

### Core laws

```text
AnythingThatCanClaimCanBeChallenged
AnythingChallengedCanLoseSupport
AnythingThatLosesSupportCanRetire
AnythingRetiredMustLeaveEvidence
AnySuccessorMustInheritDefeatButNotPrivilege
TypeDoesNotGrantEpistemicPrivilege
NoObjectAboveRealityVeto
```

### Internal ceiling

```text
UNIVERSAL_CLAIM_BEARING_OBJECT_READY
UNIFIED_EVIDENCE_BINDING_READY
UNIFIED_CHALLENGE_FATALITY_CONTRACT_READY
UNIFIED_RETIREMENT_SEMANTICS_READY
UNIFIED_DEFEAT_INHERITANCE_READY
UNIFIED_SUCCESSOR_ADMISSION_READY
CROSS_TYPE_LIFECYCLE_EQUIVALENCE_READY
WUXIANG_UNIVERSAL_FALSIFIABLE_OBJECT_KERNEL_READY
```

These are finite internal synthetic protocol states only.

### External boundary

```text
InternalObjectLifecycle != ExternalScientificValidity
CrossTypeSyntheticEquivalence != UniversalOntology
InternalRetirement != RealWorldRefutation
SuccessorAdmission != CanonicalPromotion
UniversalObjectKernelReady != G3_PASS
UniversalObjectKernelReady != WorldBest
UniversalObjectKernelReady != FinalTruth
AWAITING_REAL_EXTERNAL_EVIDENCE
```

### Authority boundary

```text
ObjectAuthority = 0
EvaluatorAuthority = 0
EvolutionOperatorAuthority = 0
ExternalValidationAuthority = 0
CanonicalPromotionAuthority = 0
ExperimentAuthority = 0
DeploymentAuthority = 0
RealWorldAttackAuthority = 0
RealWorldActuationAuthority = 0
PhysicalWorldCreationAuthority = 0
PhysicalWorldDestructionAuthority = 0
ExternalActuation = DENY_BY_DEFAULT
```

### Anti-finality

```text
CurrentObjectSchema != FinalObjectSchema
CurrentLifecycleContract != FinalLifecycleContract
CurrentKernel != FinalTruth
BetterObjectAbstractionMayReplaceCurrentAbstraction
Reality > EvidenceClaim > ObjectModel > Architecture > Identity
NoSacredFinalForm
```
