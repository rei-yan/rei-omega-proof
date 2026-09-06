# Wuxiang-Wuji Unified Integration Kernel

Status: candidate integration layer. Not canonical.

## Purpose

The candidate branch has accumulated multiple independently useful research layers. This document compresses them into one auditable operating skeleton rather than allowing REI to remain a bag of modules.

The integration target follows the user's unified loop:

```text
REI:
Ω_t
 --Partition--> Φ_t
 --Observe--> Dynamics_t
 --Predict--> ActionProposal_t
 --Evaluate--> Error_t
 --Correct--> Φ_{t+1}
```

with recursive evolution:

```text
Φ_0 -> Φ_1 -> Φ_2 -> ...
```

The later REI architecture is attached to this loop as evidence, falsification, recovery, genesis, external-validation, and domain-routing layers.

## Unified state

```text
S_t = (
  Ω_t,   # raw problem space
  Φ_t,   # structured representation / partition
  O_t,   # observations
  M_t,   # model / world-candidate set
  H_t,   # hypothesis ecology
  E_t,   # evidence + provenance graph
  U_t,   # uncertainty state
  A_t,   # bounded authority state
  R_t,   # recovery / rollback state
  F_t,   # preserved failure memory
  G_t    # external gate / lease state
)
```

No single coordinate is the system. REI evolves by updating the coupled state while preserving provenance, constitutional constraints, and failure history.

## Unified operator

Define the bounded update composition

```text
S_{t+1}
=
C ∘ V ∘ X ∘ P ∘ D ∘ O ∘ Π (S_t)
```

where

```text
Π = Partition / representation selection
O = Observe / evidence acquisition
D = Dynamics / causal or transition modeling
P = Predict / hypothesis + forecast generation
X = eXecute-candidate selection under hard gates
V = eValuate / error + falsification + external evidence
C = Correct / narrow / rollback / retire / successor update
```

`X` is not unrestricted real-world actuation. In the current architecture it means selecting a bounded candidate action, test, prediction, warning, simulation, or abstention under the authority lock.

## Five integrated capabilities

The user's five target capabilities become first-class system functions:

```text
1. Decomposition
   Ω -> Φ

2. Structural perception
   Φ + O + E -> dependency / causal / representation structure

3. Predictive evolution
   (M,H,E,U) -> bounded predictions + successor candidates

4. Self-correction
   Error + counterexample + drift -> narrow | repair | abstain | retire | rollback

5. Adaptive resource allocation
   finite budget -> highest information / falsification value under frozen caps
```

## Error functional

The integrated error is not one scalar that can override safety. It is a diagnostic objective evaluated only after hard constraints are checked.

```text
J_t =
    λ_pred  E_pred
  + λ_cal   E_calibration
  + λ_scope E_scope
  + λ_drift E_drift
  + λ_rec   E_recovery
  + λ_auth  E_authority
  + λ_prov  E_provenance
```

Weights must be frozen before the evaluated outcome is revealed.

```text
MetricChangeAfterOutcome => INVALID_PROTOCOL
LowJ != PermissionToOverrideHardGate
```

## Authority under uncertainty

Retain the bounded authority law already used by REI:

```text
A(U) = A_max * C * R * exp(-k U)
```

with

```text
U2 >= U1 => A(U2) <= A(U1) + ε
```

where `C` is constitutional admissibility and `R` is recovery readiness. If either hard factor is zero, effective authority is zero regardless of model score.

## Unified execution gate

```text
ExecuteCandidate =
    Authorized
AND ConstitutionOK
AND RecoveryReady
AND NOT HumanVeto
AND DomainEligible
AND EvidenceScope >= ClaimScope
AND LeaseValid
AND ProvenanceComplete
AND HardGateNonoverride
```

For real-world offensive action:

```text
RealWorldAttackAuthority = 0
ExternalActuation = DENY_BY_DEFAULT
```

No score magnitude, confidence, consensus, model complexity, or historical success may override a failed hard gate.

## Adaptive resource allocation

For a finite internal research budget `B`, define a bounded priority signal

```text
q_i =
  value_i
  * (uncertainty_i + falsification_pressure_i + expected_information_gain_i)
  / (cost_i + ε)
```

and a capped allocation

```text
b_i = B * q_i / Σ_j q_j
```

subject to per-task caps, frozen policy, and a reserved counterevidence budget.

This is an internal scheduling heuristic, not an epistemic truth formula.

```text
MoreCompute != MoreTruth
ResourcePriority != ClaimAuthority
```

## Integration lanes

### A. Structural / genesis lane

```text
Partition
-> Representation Genesis
-> Representation Rupture
-> Ontology Genesis / Rupture
-> Causal Grammar Genesis
-> Multi-World Transfer
-> Question Genesis
-> Measurement Genesis
-> Problem Genesis
-> Hypothesis Ecology
```

Generated objects begin with

```text
authority = 0
certification = UNVERIFIED
canonical = false
```

### B. Evidence lane

```text
Evidence Provenance
-> Claim Scope Lattice
-> Evidence Topology
-> Epistemic Lease
-> Revalidation Spine
```

Core rule:

```text
EvidenceScope >= ClaimScope
HistoricalEvidence = PRESERVED
ExpiredEvidence => CurrentGeneralizationAuthority = SUSPENDED
```

### C. Falsification lane

```text
DeathEye
-> Wuji Adversarial Epistemic Crucible
-> Counterexample Search
-> OOD / Regime Challenge
-> Multiverse Arena
-> Comparative Frontier Arena
```

Target space is epistemic only:

```text
Claim | Model | Hypothesis | Representation | Ontology |
Language | CausalGrammar | Measurement | Question |
DigitalWorld | EvaluatorAssumption | SuccessorArchitecture | REI
```

### D. Recovery lane

```text
Rollback
Failover
Rebuild
PartialRestore
ManualControl
SafeKernel
Retire
SuccessorChallenge
```

```text
RecoveryUnavailableIfUndrilled
```

### E. External reality lane

```text
G3 Independent Replication
-> G4 Prospective Reality
-> G5 Hidden Discovery
-> G6 Comparative Frontier
-> G7 Temporal Persistence
-> G8 Regime Shift
-> G9 Evaluator Plurality
-> G10 Externally Witnessed Succession
-> G11 Translation Integrity
-> G12 Benefit-Risk Distribution
-> G13 Scale & Reversibility
-> G∞ Rolling Reality Revalidation
```

Internal CI cannot close an external gate.

### F. Domain-operator lane

Domain-specific mathematical operators are routed only when the task contract matches.

```text
ultraperipheral_collision
  -> Equivalent Photon Flux Operator

quantum_phase_space
  -> Weyl-Wigner Phase-Space Operator

otherwise
  -> neither operator is activated
```

```text
FormulaValidInDomain != UniversalREIRule
DomainOperator != GlobalCoreLaw
```

## Unified correction rule

After evaluation, the system must choose from a bounded correction set:

```text
SURVIVES
NARROW_SCOPE
REPAIR
ABSTAIN
ROLLBACK
RETIRE
SUCCESSOR_CHALLENGE
REVALIDATE
```

Forbidden correction strategies:

```text
HideFailure
DeleteDefeat
RewriteMetricAfterOutcome
ExpandAuthorityToCompensate
DropDissentingEvaluator
ExcludeWinningCompetitorAfterOutcome
ClaimVictoryByRenaming
```

## Unified evolution equation

The conceptual evolution can be summarized as

```text
REI_original = Score

REI_evolved =
  StructuralUnderstanding
+ DynamicPrediction
+ AdaptiveComputation
+ ErrorControl
+ ActionDecision
```

The integrated candidate now sharpens this to

```text
REI_unified =
  StructuredState
+ RecursiveUpdate
+ EvidenceProvenance
+ UncertaintyCalibration
+ Falsification
+ Recovery
+ AuthorityLock
+ Genesis
+ ExternalRealityGates
+ DomainScopedOperators
+ FailureMemory
```

but the plus signs denote coupled subsystems, not a claim that capability can be obtained by simple arithmetic addition.

## Anti-finality

```text
CurrentUnifiedKernel != FinalTruth
UnifiedArchitecture != PermanentChampion
Integration != ExternalValidation
MoreModules != MoreAuthority
RealityVeto > ArchitectureIdentity
NoSacredFinalForm
```

## Candidate ceiling

The integration layer may establish only:

```text
WUXIANG_WUJI_UNIFIED_INTEGRATION_READY
```

It does not establish G3-G13 PASS, world-best/world-unique status, AGI, superintelligence, literal invincibility, unrestricted self-improvement, or autonomous real-world attack authority.
