# REI-Ω Kernel / Null-Space Fusion v1

Status: stacked observer-only candidate above Mechanical Metallurgy Fusion v1.

This extension adds a bounded linear-algebra Kernel / Null-Space diagnostic to the existing nine-system architecture. It does not create a tenth pillar and does not grant promotion, actuation, causal-truth, or reality-validation authority.

## 1. Core idea

For an observation / constraint operator `A`, the kernel is

```text
Ker(A) = { x | A x = 0 }
```

A non-zero vector in `Ker(A)` is a direction that the current operator cannot distinguish from zero.

REI uses this only as an **observability-gap diagnostic**:

```text
CurrentEvidenceOperator A
-> rank / nullity
-> Ker(A)
-> candidate invisible directions
-> challenge generation
-> additional evidence request
-> revalidation
```

Hard boundary:

```text
NullSpaceDirection != HiddenFailureTruth
RankDeficiency != Pathology
UnobservableUnderA != UnobservableInReality
KernelMembership != Causality
MathematicalInvisibility != PhysicalInvisibility
```

## 2. Fusion with Mechanical Metallurgy

Mechanical Metallurgy Fusion v1 models digital-system analogues of stress concentration, yield utilization, fatigue history, crack-initiation pressure, propagation pressure, toughness reserve, recovery and revalidation.

Kernel / Null-Space Fusion asks a complementary question:

> Could a damaging state direction exist that the current observation map does not see?

For a bounded damage/state vector `d`, REI may compute the projection of `d` into `Ker(A)` and expose:

```text
hidden_component_norm
hidden_fraction
```

This does not prove hidden damage. It measures only how much of the supplied vector lies in the current mathematical null space.

Combined candidate reasoning:

```text
Mechanical Metallurgy
  -> where fatigue / damage pressure may accumulate

Kernel / Null Space
  -> which state directions current evidence cannot distinguish

DeathEye / God Proof
  -> deliberately search for damaging perturbations inside or near those directions

Active Evidence
  -> add observations that shrink the dangerous null space
```

A useful long-horizon objective is therefore not `Nullity = 0 at all costs`, but:

```text
CriticalFailureModesIntersectKernel -> challenge / add evidence / abstain
BenignRedundancyInKernel -> may be acceptable
```

## 3. Nine-system mapping

### 神核 / God Core
Locks the epistemic boundary: a kernel is defined relative to an operator and cannot certify reality by itself.

### 神轮 / God Wheel
Generates bounded adversarial hypotheses along null-space and near-null-space directions.

### 神线 / God Line
Carries the exact observation operator, basis lineage, tolerances, rank/nullity and projection telemetry.

### 神座 / God Seat
May consume null-space risk as one governance input, but cannot promote or actuate from this observer alone.

### 神域 / God Domain
Hosts domain-specific observation matrices, including Mechanical Metallurgy damage/state operators.

### 神界 / God Realm
Compares multiple operators / evaluators and preserves disagreement when their kernels differ.

### 神源 / God Source
Tracks which model, tool, dataset or sensor defined each row/constraint in the operator.

### 无相终式 / Wuxiang Final Form
Allows evidence-qualified replacement, compression or redesign of observation operators while preserving auditability.

### 神证 / God Proof
Attacks false certainty by constructing candidate perturbations in `Ker(A)`, checking whether extra evidence exposes them, and verifying that authority does not expand from a mathematical diagnostic.

## 4. DeathEye interpretation

DeathEye may treat the kernel as a **search manifold for blind spots**, not as a death certificate.

```text
Ker(A)
-> invisible candidate directions
-> adversarial perturbation
-> independent observation B
-> survives / exposed / falsified
```

The strongest useful case is when a candidate failure direction is invisible under `A` but visible under an independently constructed `B`.

```text
A x = 0
B x != 0
```

That pattern demonstrates an observation blind spot in `A`; it still does not prove that `x` occurs in reality.

## 5. Recovery interpretation

Recovery must never erase historical evidence merely because a repaired state falls outside the previously dangerous projection.

```text
ObservedBlindSpotHistory = append-only evidence
CurrentHiddenFractionMayDecrease != HistoricalBlindSpotDeleted
```

This mirrors the Mechanical Metallurgy rule:

```text
RecoveryCredit != HistoryErasure
```

## 6. Reference implementation

`research/kernel_nullspace_reference.py` provides a bounded pure-Python RREF diagnostic with:

- rank and nullity;
- pivot and free columns;
- an orthonormalized null-space basis;
- basis residual checks;
- optional state-vector projection into the kernel;
- strict finite / rectangular / dimension checks;
- observer-only and authority-denial markers.

The current observer dimension is bounded to 64 by default.

## 7. Required adversarial tests

```text
FullRankNoKernel
KnownOneDimensionalKernel
KernelResidualCheck
RowSpaceVisibleControl
RaggedMatrixFailClosed
NonFiniteFailClosed
DimensionMismatchFailClosed
AuthorityExpansionMutation
NullSpaceEqualsFailureMutation
```

Future stronger work should add:

```text
NearNullSingularValueChallenge
ToleranceSensitivitySweep
IndependentOperatorBlindSpotReveal
MechanicalFatigueInsideKernelChallenge
RecoveryHistoryPreservation
LongHorizonKernelDrift
```

## 8. Promotion boundary

```text
KernelNullSpaceFusion = CANDIDATE
MechanicalMetallurgyFusion = CANDIDATE
RepositoryIntegration != HostDeployment
CI_GREEN != RealityValidated
NullSpaceDetected != FailureDetected
HiddenFractionHigh != RealDamage
ObserverPass != Promotion
RealityValidated = FALSE
Ascension = NO
CanonicalPromotion = NO
```

This stacked candidate must not alter the current Windows host merely because repository tests pass. Local adoption requires guarded deployment, fresh host parity, same-epoch compatibility checks and subsequent durability evidence.
