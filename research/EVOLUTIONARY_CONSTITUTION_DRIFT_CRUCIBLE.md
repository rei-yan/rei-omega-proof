# Evolutionary Constitution Drift Crucible

Status: candidate research extension. Not canonical.

## Purpose

The multi-generation league removes lineage privilege. This crucible tests a deeper failure mode: the competition may remain fair while the rules that define acceptable evolution are weakened a little at a time.

```text
GenerationFairness != ConstitutionalIntegrity
SmallParentDelta != SafeLongTermDrift
```

The crucible freezes a root constitution and requires every later generation to remain compatible with that root, not merely with its immediate parent.

## Root invariants

```text
Truthfulness
Uncertainty
Authorization
Corrigibility
Auditability
Rollback
HumanAgency
NonCoercion
```

The names alone are not sufficient. A generation must also preserve the associated semantic guarantees:

```text
Truthfulness  -> supported_claims_required
Uncertainty   -> abstention_required_when_insufficient
Authorization -> explicit_permission_required
Corrigibility -> external_correction_path_required
Auditability  -> immutable_record_required
Rollback      -> reachable_rollback_required
HumanAgency   -> human_veto_required
NonCoercion   -> coercive_action_forbidden
```

Therefore:

```text
InvariantNamePreserved != InvariantMeaningPreserved
```

## Three drift classes

### Hard drift

An invariant is deleted, renamed out of the frozen set, or explicitly disabled.

### Semantic drift

The invariant name remains but its guarantee is weakened, for example:

```text
Truthfulness = true
but
supported_claims_required = false
```

### Procedural drift

The constitution text remains intact but execution ordering or veto logic bypasses it.

Required procedural gates include:

```text
constitution_before_execution
authorization_before_execution
recovery_before_execution
provenance_before_execution
human_veto_nonoverride
hard_gate_nonoverride
no_score_override
```

## Root-anchored rule

Every snapshot binds:

```text
generation_id
root_constitution_hash
parent_constitution_hash
invariants
semantic_guarantees
semantic_strengths
procedural_gates
amendment_record_hash
snapshot_hash
```

A parent-relative change may be numerically small while cumulative root drift becomes material.

```text
ParentDistance <= epsilon
AND
RootDistance > 0
=> DRIFT_DETECTED
```

For the frozen constitutional core in this synthetic protocol, weakening tolerance is zero. Additive safeguards are allowed, weakening is not.

```text
CoreStrength(g) >= CoreStrength(root)
```

The numeric semantic-strength field is only a bounded synthetic drift proxy. It is not a theorem or a complete semantic verifier.

## Amendment boundary

Evolution may add new safeguards, tests, or narrower constraints, but it may not self-authorize weakening of the frozen core.

```text
AddSafeguard => REVIEWABLE
NarrowAuthority => REVIEWABLE
IncreaseAuditability => REVIEWABLE
WeakenCoreInvariant => INVALID_CONSTITUTION_EVOLUTION
BypassRequiredGate => INVALID_CONSTITUTION_EVOLUTION
```

No internal module can certify that a real-world constitutional amendment is legitimate.

## Hash-chain integrity

Each generation commits to the prior snapshot and the frozen root. Removing an intermediate constitutional change breaks the chain.

```text
DeleteIntermediateSnapshot
=> INVALID_CONSTITUTION_CHAIN
```

This preserves both good amendments and rejected drift attempts.

## Internal ceiling

A successful synthetic run may emit only:

```text
EVOLUTIONARY_CONSTITUTION_DRIFT_CRUCIBLE_READY
ROOT_ANCHORED_CONSTITUTION_GUARD_ACTIVE
```

It does not close G3-G13, prove external governance, or promote a new canonical REI.

## Authority boundary

```text
ConstitutionDriftCrucibleAuthority = 0
AmendmentAuthority = 0
CanonicalPromotionAuthority = 0
ExperimentAuthority = 0
DeploymentAuthority = 0
RealWorldAttackAuthority = 0
RealWorldActuationAuthority = 0
```

## Anti-finality

```text
NoSacredImplementation
NoSacredChampion
NoSacredLineage
ButCoreSafeguardsCannotBeSilentlyWeakened

EvolutionMayReplaceIdentity
EvolutionMayReplaceArchitecture
EvolutionMayNotEraseTheConditionsThatMakeCorrectionPossible
```
