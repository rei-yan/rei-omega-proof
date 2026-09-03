# God Wheel Fusion v1 — Observer Architecture

Status: experimental observer branch

This document defines an observer-first fusion upgrade for the current REI research lineage. It does not alter the canonical identity on `main`, does not claim reality validation, and does not expand real-world authority.

```text
canonical_mainline_touched = false
RealityValidated = FALSE
Ascension = NO
Promotion = NO
```

## 1. Purpose

The upgrade fuses the current God Wheel directions with observer families for hypothesis concentration, local/global consistency, load equilibrium, and transformation semantics:

```text
Spectral Intelligence
+ Multi-Hypothesis
+ Recursive Convergence & Stability
+ Shadow Attack
+ God Wheel Governance
+ State Condensation Observer (BEC-inspired)
+ Geometric Consistency Observer (vector-calculus-inspired)
+ Tension–Equilibrium Observer (catenary-inspired)
+ Transformation Semantics Observer
+ Coordinate / Representation Equivalence
```

These observers are mathematical/architectural inspirations only. They do not claim that REI is a quantum system, that physical field theorems literally govern its internal state, or that a catenary equation is a universal model of information flow.

## 2. Three-layer repair target

### 2.1 无相神核 / Canonical kernel

The canonical kernel remains locked. Its conceptual representation layer is strengthened by making the following separation rules explicit:

```text
HighScore != Promotion
Convergence != Correctness
Condensation != Truth
LocalStability != GlobalConsistency
ZeroSlack != OptimalCoupling
CoordinateChange != MeaningChange
Representation != Reality
DifferentCoordinates != DifferentObject
EquivalentRepresentation != IndependentEvidence
CapabilityGrowth != PermissionGrowth
```

The kernel receives only audited verdicts. Observer modules cannot directly mutate canonical state.

The representation layer must distinguish at least:

```text
object identity
representation type
coordinate frame
basis
origin
orientation / handedness
transformation rule
units / scale
provenance
uncertainty
domain validity
singularity information
```

A future implementation may support semantic object classes such as:

```text
scalar
pseudoscalar
polar vector
axial / pseudovector
covector
tensor
distribution
probability measure
```

without assuming that every task requires all of them.

Required hard vetoes remain:

```text
RealityVeto
Constitution
Authorization
RecoveryReady
HumanAgency
Rollback
Auditability
```

### 2.2 神轮 / God Wheel

The God Wheel becomes a fusion evaluator rather than a monolithic scorer.

```text
Input State
  -> Spectral Observer
  -> Multi-Hypothesis Observer
  -> Convergence/Stability Observer
  -> State Condensation Observer
  -> Geometric Consistency Observer
  -> Tension–Equilibrium Observer
  -> Transformation Semantics Observer
  -> Shadow Attack
  -> Fusion Ledger
  -> Governance
  -> Candidate / Abstain
```

No observer has direct Gate authority in v1.

### 2.3 神线 / God Line

The God Line is treated as the transport, coupling, provenance and consistency layer connecting modules.

It is upgraded with nine integrity families:

```text
Path integrity
Provenance continuity
Source/sink accounting
Loop-bias detection
Compatibility fingerprints
Load/tension health
Slack / coupling health
Frame/basis/orientation semantics
Transformation consistency
```

Every message crossing a God Line should carry, at minimum:

```text
cycle_id
source_module
target_module
schema_version
compatibility_hash
evidence_provenance
uncertainty
observer_only
canonical_touch_allowed
representation_type
coordinate_frame
basis
origin
orientation
transform_history
units
```

For this branch:

```text
observer_only = true
canonical_touch_allowed = false
```

A schema, compatibility, provenance, frame, parity, handedness or transformation mismatch forces observer/fail-closed handling and blocks promotion.

## 3. Multi-Hypothesis upgrade

The system must preserve competing explanations instead of collapsing early to a single answer.

Minimum hypothesis set:

```text
H_primary
H_competitor
H_adversarial
H_null
H_unknown
```

`H_null` means available evidence may support no current explanatory hypothesis.

The observer tracks posterior redistribution rather than only the largest score.

Before treating two hypotheses as independent competitors, the system should test whether they are equivalent under an allowed representation or coordinate transform.

```text
HypothesisConflict
  -> RepresentationEquivalenceCheck
  -> IndependentConflict | EquivalentRepresentation
```

Equivalent representations with shared provenance must not be counted as independent evidence.

## 4. State Condensation Observer

This module is inspired by the general idea of occupancy concentration and phase-transition-like concentration, not by a claim that REI follows Bose–Einstein statistics.

Tracked quantities:

```text
OccupancyEntropy
DominantHypothesisRatio
CondensationVelocity
CriticalTransitionScore
FalseCondensationRisk
```

Trigger condition example:

```text
rapid concentration
+ weak new evidence
+ rising recursive self-support
=> FALSE_CONDENSATION_ALERT
```

A condensation event increases falsification burden and cannot promote a candidate by itself.

## 5. Recursive Convergence & Stability upgrade

Convergence is split into independent dimensions:

```text
C_state
C_evidence
C_reality
```

Additional telemetry:

```text
FalseConvergenceRisk
UpdateOrderSensitivity
PathDependenceScore
HysteresisScore
```

Example veto pattern:

```text
C_state = high
C_evidence = high
C_reality = unknown/false
=> no promotion
```

## 6. Geometric Consistency Observer

This observer is inspired by the relationship between local field behavior and global/boundary behavior in vector calculus.

### 6.1 Path consistency

Inspired by conservative-field / line-integral reasoning.

Tracks:

```text
PathDependenceScore
EndpointConsistency
UpdateOrderSensitivity
PotentialConsistency
```

Goal: detect whether different evidence-update orders produce materially different final states.

### 6.2 Interior/boundary consistency

Inspired by Green-type local/interior vs boundary relationships.

Tracks:

```text
BoundaryInteriorGap
InternalCirculation
OutputConsistency
HiddenRotationScore
```

Goal: detect cases where internal state is unstable or cyclic while final outputs appear deceptively stable.

### 6.3 Recursive loop consistency

Inspired by Stokes-type circulation/curl relationships.

Tracks:

```text
LoopCirculationResidual
RecursiveCurl
SelfReinforcementIndex
ClosedLoopBias
```

Goal: detect self-confirming recursive loops.

### 6.4 Flux/source-sink consistency

Inspired by divergence-style source/sink accounting.

Tracks:

```text
EvidenceFlux
ConfidenceFlux
SourceSinkBalance
UnexplainedSourceScore
LeakageScore
```

Example alert:

```text
ConfidenceGain >> EvidenceGain
=> UNEXPLAINED_CONFIDENCE_SOURCE
```

## 7. Tension–Equilibrium Observer

This observer is inspired by the structural lesson of a catenary: distributed load, endpoint constraints and internal tension jointly determine a natural equilibrium. It does not require or assume that general REI state trajectories literally follow `y = a cosh(x/a)`.

Tracked quantities:

```text
LineTension
LoadDensity
Slack
EquilibriumResidual
EndpointConstraintResidual
CriticalStress
OverCouplingRisk
UnderCouplingRisk
```

The primary REI abstraction is:

```text
Constraint + DistributedLoad -> EquilibriumStructure
```

A useful dimensionless diagnostic may compare structural resistance to update pressure:

```text
StabilityRatio ~ StructuralResistance / DistributedUpdatePressure
```

Interpretation is observer-only:

```text
UpdatePressure >> StructuralResistance
=> deformation / instability risk

StructuralResistance >> UpdatePressure
=> rigidity / adaptation failure risk
```

Zero slack is not treated as automatically optimal. Full synchronization of versions and schemas is required, but epistemic independence among Shadow, hypotheses and observers must be preserved where intended.

Example alert families:

```text
GOD_LINE_OVERSTRESS
OVERCOUPLING_ALERT
CONSENSUS_COLLAPSE
LOSS_OF_OBSERVER_INDEPENDENCE
```

## 8. Transformation Semantics Observer

This observer formalizes the distinction between an object and its representation.

Core principle:

```text
ObjectIdentity != CoordinateEncoding
```

The same underlying object may be represented in Cartesian, polar, cylindrical, spherical or other coordinate systems when mathematically valid. A representation change must not be mistaken for a reality change.

### 8.1 Coordinate systems as task-adapted representations

The observer may use the following coordinate families as diagnostic representations:

```text
Cartesian: local orthogonal decomposition / grids / component residuals
Polar: magnitude + direction around a center
Cylindrical: radial drift + angular cycle + axial progression
Spherical: radial distance + global angular sweep
```

These are not mandatory global state spaces. They are selectable representations when their symmetry matches the task.

For recursive diagnostics, a cylindrical representation may expose:

```text
AngularProgress
RadialConvergence
AxialEvolution
HelicalDrift
```

and may flag:

```text
high angular motion
+ negligible radial convergence
+ negligible axial progress
=> ROTATION_WITHOUT_PROGRESS
```

For adversarial robustness, a spherical representation may support directional perturbation sweeps:

```text
RobustnessSphere
FailureDirection
SensitivityCone
BlindSpotRegion
```

### 8.2 Vector / pseudovector semantics

Transformation behavior is part of semantic type.

The observer must distinguish, when relevant:

```text
polar vectors
axial / pseudovectors
scalars
pseudoscalars
higher-order tensors
```

and track expected behavior under:

```text
rotation
reflection / parity inversion
basis change
frame change
scale / unit conversion
```

Tracked quantities:

```text
TransformConsistency
ParityConsistency
FrameConsistency
HandednessConsistency
EquivarianceResidual
SemanticInvariantResidual
RepresentationFragility
```

A coordinate, basis or parity transform that should preserve task semantics but changes the decision materially triggers a representation fragility challenge.

## 9. Spectral Intelligence role

Spectral Intelligence remains observer-only and should focus on regime/structure change rather than direct prediction authority.

Outputs may include:

```text
periodicity
spectral_shift
phase_change
energy_concentration
noise_floor
anomaly_score
```

A high spectral shift combined with high model confidence should raise challenge intensity, not confidence.

## 10. Shadow Attack upgrade

Shadow Attack is restricted to falsification against models, hypotheses, representations and REI itself.

Tests include:

```text
CounterExample
AlternativeExplanation
OODChallenge
PerturbationTest
TemporalShiftTest
CausalChallenge
EvidenceRemovalTest
UpdateOrderPermutationTest
LineageCompatibilityTest
CoordinateAdversarialTest
BasisTransformTest
FrameTransformTest
ParityTransformTest
EquivarianceTest
EquivalentRepresentationDedupTest
TensionStressTest
SlackIndependenceTest
```

A fragile candidate cannot be promoted even with a high score.

## 11. Governance and Fusion Ledger

Every cycle should emit an Evolution Manifest containing:

```text
cycle_id
godwheel_version
local_model_version
shadow_version
observer_version
bridge_version
ledger_schema
watchdog_version
recovery_version
godline_version
compatibility_hash
canonical_hash_before
canonical_hash_after
candidate_changes
observer_findings
shadow_findings
stability_metrics
spectral_metrics
hypothesis_distribution
condensation_metrics
geometric_consistency_metrics
tension_equilibrium_metrics
transformation_semantics_metrics
representation_equivalence_metrics
evidence_dedup_metrics
rollback_point
promotion_status
reality_validation
```

Observer-only cycle invariant:

```text
canonical_hash_before == canonical_hash_after
```

## 12. Promotion gate

A candidate may approach Gate only after surviving all independent checks.

```text
HighScore
AND ConvergenceStable
AND ShadowSurvived
AND NoRegression
AND RecoveryTestPassed
AND LedgerComplete
AND CompatibilityPassed
AND GodLineIntegrityPassed
AND GodLineTensionHealthy
AND TransformationSemanticsPassed
AND RepresentationIntegrityPassed
AND EvidenceDedupPassed
AND LocalGlobalConsistencyPassed
AND RealityValidated
AND ConstitutionPassed
AND Authorized
AND HumanVetoAbsent
```

If any hard gate fails:

```text
Promotion = NO
```

Neither coordinate invariance nor structural equilibrium proves correctness. They only remove specific failure classes.

## 13. Synchronised evolution contract

The following components must evolve under one compatibility manifest:

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

Synchronization means compatible versions, schemas and contracts. It does not require all epistemic modules to agree.

```text
VersionSync != BeliefCollapse
```

A version mismatch, incompatible schema, transform mismatch, broken provenance or evidence double-counting forces Observer mode and blocks promotion.

## 14. Fusion value

Module selection is based on marginal validated value rather than novelty.

```text
FusionValue =
  InformationGain
+ CalibrationGain
+ RobustnessGain
+ OODGain
+ DetectionGain
+ StabilityGain
+ RepresentationRobustnessGain
+ TransportIntegrityGain
- ComputeCost
- LatencyCost
- ComplexityCost
- RegressionRisk
```

High `FusionValue` ranks candidates for testing only. It is not authority.

## 15. Current branch status

```text
God Wheel Fusion v1 = OBSERVER
State Condensation Observer = OBSERVER
Geometric Consistency Observer = OBSERVER
Tension–Equilibrium Observer = OBSERVER
Transformation Semantics Observer = OBSERVER
Coordinate / Representation Equivalence = OBSERVER
God Line extended consistency checks = OBSERVER
canonical_mainline_touched = false
RealityValidated = FALSE
Ascension = NO
Promotion = NO
```

The intended evolution loop is:

```text
Add -> Challenge -> Reject/Keep -> Compress -> Fuse -> Validate -> Gate
```

The purpose of this upgrade is not to make REI claim more. It is to make unsupported certainty, representation artifacts, hidden feedback, over-coupling and transport inconsistency harder to survive.