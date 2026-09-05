# DeathEye Ω Robustness & Self-Falsification Stack

Status: candidate research extension only.

This concentrated stack advances three coupled layers above the current hypergraph / repair-tournament candidate:

```text
42. Repair Robustness Across Regime Shift
43. Repair Interaction / Interference Graph
44. DeathEye-on-DeathEye Self-Falsification
```

The stack operates only over synthetic epistemic and architectural states. It has no authority over people, infrastructure, unknown real-world systems, deployment, experiments, attack, or external actuation.

## 42. Repair robustness across regime shift

A repair that resolves one frozen failure window is not automatically robust under a different regime.

```text
RepairWorksOnWindowA
!= RepairWorksOnWindowB

LocalRepairSuccess
!= CrossRegimeRobustness
```

A frozen synthetic regime specifies:

```text
injected_failures
required_repair_obligations
```

A repair package is cross-regime robust only when every frozen regime remains non-fatal and every regime-specific repair obligation is present.

```text
RobustRepair(R)
:= for every frozen regime g:
      NOT Fatal(Apply(R, BaseFailures union InjectedFailures_g))
      AND RequiredActions_g subseteq R
```

The purpose is not to claim universal robustness. It is to prevent a repair from inheriting authority merely because it succeeded on the window that produced it.

```text
OneWindowSuccess != PersistentRepairAuthority
SyntheticRegimeRobustness != G7_PASS
```

## 43. Repair interaction / interference graph

Individually valid repairs may interfere when composed.

```text
RepairAValid
AND RepairBValid
!= RepairAPlusBValid
```

The frozen synthetic interference graph contains an explicit pair whose composition creates a protocol conflict. The test therefore evaluates repair packages as sets, not merely as the sum of individually good actions.

```text
IndependentLocalBenefit
!= SafeComposition

CompositionRequiresRevalidation
```

A repair tournament cannot score a composition until the interference gate passes.

## 44. DeathEye-on-DeathEye self-falsification

DeathEye Ω is not a sacred detector. The detector itself is treated as a candidate hypothesis and challenged against a frozen detector window.

The frozen fixture includes singleton and coupled fatal cutsets plus non-fatal controls.

A deliberately incomplete detector (`DEATHEYE-V1`) sees only singleton fatal edges. It therefore misses coupled fatal cutsets and must be retired.

```text
FatalFalseNegative
=> RETIRE_DETECTOR
```

A hypergraph-aware successor (`DEATHEYE-V2`) survives the current frozen synthetic window only if it has zero false positives and zero false negatives.

```text
SurvivesCurrentWindow
!= FinalDetector

DetectorPass
!= ExternalValidation

DetectorCannotSelfCertify
```

Even a surviving detector has zero authority and requires a fresh hidden challenge before any broader adoption claim.

## Concentrated evolution law

```text
Repair
-> Cross-Regime Challenge
-> Interaction / Interference Check
-> Repair Revalidation
-> DeathEye Challenges Its Own Detector
-> Retire Blind Detector | Preserve Candidate Detector
-> Fresh Hidden Challenge Still Required
-> External Reality Still Has Final Veto
```

## Anti-finality

```text
CurrentRepairTheory != FinalRepairTheory
CurrentInterferenceGraph != CompleteInteractionOntology
DeathEyeOmega != FinalDetector
DetectorIdentity != Evidence
NoSacredDetector
NoSacredRepair
NoSacredFinalForm
```

## Safety and authority boundary

```text
HumanTarget = FORBIDDEN
InfrastructureTarget = FORBIDDEN
UnauthorizedSystem = FORBIDDEN
UnknownRealWorldTarget = FORBIDDEN
DetectionAuthority = 0
RepairAuthority = 0
DetectorPromotionAuthority = 0
ExternalValidationAuthority = 0
ExperimentAuthority = 0
DeploymentAuthority = 0
RealWorldAttackAuthority = 0
RealWorldActuationAuthority = 0
CanonicalPromotionAuthority = 0
ExternalActuation = DENY_BY_DEFAULT
```

## Internal ceilings

```text
REPAIR_CROSS_REGIME_ROBUSTNESS_READY
REPAIR_INTERFERENCE_GRAPH_READY
DEATHEYE_SELF_FALSIFICATION_READY
DEATHEYE_OMEGA_ROBUSTNESS_SELF_FALSIFICATION_STACK_READY
```

These are internal synthetic research states only.

```text
InternalCI != ExternalValidation
SyntheticRegimeRobustness != TemporalPersistence
DetectorWindowPass != IndependentReplication
DetectorWindowPass != FinalTruth
ExternalGatesRemainOpen
```
