# Wuxiang Evolution Quality Governor

Status: candidate research extension only.

This concentrated evolution does not add another domain capability. It governs whether future internal evolution is actually worth keeping.

```text
61. Architecture State Compression
62. Marginal Capability Gain Gate
63. Verification Budget Allocation
64. Counterexample Portfolio Diversification
65. Cross-Layer Semantic Consistency
66. Complexity Tax / Pruning Trigger
```

## Core law

```text
MoreCode != MoreCapability
MoreModules != MoreTruth
NewName != NewFunction
ComplexityWithoutNewFalsifiability => PRUNE
```

A proposal must earn its place by adding at least one measurable property within the frozen protocol scope:

- new falsification coverage;
- lower false-negative risk;
- lower verification cost for the same claim scope;
- stronger scope containment;
- stronger recovery / correctability;
- removal of duplicated state or interface semantics.

## 61. Architecture State Compression

Equivalent or alias states are mapped to one canonical internal semantic state before evaluation. State-count reduction is allowed only when it does not erase evidence, dissent, abstention, rollback, or scope information.

```text
Compression != EvidenceDeletion
Compression != FailureDeletion
Compression != SemanticCollapse
```

## 62. Marginal Capability Gain Gate

For proposal `p`:

```text
MarginalGain(p) =
  FalsificationGain
+ FalseNegativeReduction
+ VerificationEfficiencyGain
+ ScopeIntegrityGain
+ RecoveryGain
+ DuplicateStateReduction
```

A proposal with zero marginal gain cannot pass merely because it is more complex.

```text
MarginalGain <= 0 => PRUNE_OR_REVISE
```

Hard regressions in constitutional, recovery, authority, abstention, provenance, or reality-veto semantics veto the proposal regardless of score.

## 63. Verification Budget Allocation

Verification resources are assigned by frozen risk burden rather than module prestige.

```text
Burden = f(ClaimScope, Uncertainty, Irreversibility, Novelty, DistributionShift)
HigherBurden => AtLeastAsMuchVerificationBudget
```

The allocator is bounded and finite. It does not create compute, external reviewers, or external evidence.

## 64. Counterexample Portfolio Diversification

A large test suite concentrated on one failure family is not treated as broad robustness.

Required synthetic coverage families include:

```text
evidence
scope_time
authorization
recovery
representation
evaluator
succession
constitution
```

```text
TestCount != FailureModeCoverage
MonocultureSuite != RobustSuite
```

## 65. Cross-Layer Semantic Consistency

State translations across internal layers must preserve their epistemic meaning.

Forbidden examples:

```text
ABSTAIN -> PASS
EXPIRED -> SUPPORTED_FOR_NOW without revalidation
SUSPENDED -> CANONICAL
INCONCLUSIVE -> EXTERNALLY_VALIDATED
MATERIAL_FAIL -> DELETED
```

This is a finite encoded consistency checker, not a proof of universal semantic equivalence.

## 66. Complexity Tax / Pruning Trigger

Every proposal pays an explicit complexity tax.

```text
NetEvolutionValue = MarginalGain - ComplexityTax
```

A proposal is prunable when it adds no unique coverage and increases state, interface, or maintenance burden.

Valid outcomes:

```text
KEEP
REVISE
PRUNE
ABSTAIN
```

`PRUNE` is a valid evolutionary success when it removes redundant machinery without weakening safeguards.

## Concentrated evolution law

```text
Evolution = GrowWhenUseful + CompressWhenEquivalent + PruneWhenRedundant
```

The governor itself has no privilege. A future counterexample may retire or replace it.

```text
GovernorPass != FinalArchitecture
GovernorSurvival != ExternalValidation
GovernorCanBeRetired = true
```

## Internal ceiling

```text
ARCHITECTURE_STATE_COMPRESSION_READY
MARGINAL_CAPABILITY_GAIN_GATE_READY
VERIFICATION_BUDGET_ALLOCATOR_READY
COUNTEREXAMPLE_PORTFOLIO_DIVERSIFICATION_READY
CROSS_LAYER_SEMANTIC_CONSISTENCY_READY
COMPLEXITY_TAX_PRUNING_READY
WUXIANG_EVOLUTION_QUALITY_GOVERNOR_READY
```

These are internal synthetic protocol states only.

## External and authority boundary

```text
InternalCI != ExternalValidation
GovernorReady != G3_PASS
BudgetAllocatorReady != ExternalReviewerCapacity
SemanticConsistencyReady != G11_PASS
PruningReady != CanonicalPromotion

EvolutionAuthority = 0
PruningAuthority = 0
ExternalValidationAuthority = 0
CanonicalPromotionAuthority = 0
RealWorldAttackAuthority = 0
RealWorldActuationAuthority = 0
ExternalActuation = DENY_BY_DEFAULT
```

Current external state remains:

```text
AWAITING_REAL_EXTERNAL_EVIDENCE
```
