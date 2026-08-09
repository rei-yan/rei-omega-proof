# DeathEye Ω Hypergraph Evolution Stack

Status: candidate research extension only.

This stack concentrates three coupled evolutions above the current DeathEye Ω / reality-adjudicated meta-evolution candidate:

```text
39. DeathEye Ω Hypergraph Cutset Search
40. Counterfactual Repair Minimality Proof
41. Repair Tournament & Survivor Selection
```

It operates only over synthetic epistemic and architectural states. It has no human, infrastructure, unauthorized-system, unknown-real-world-target, deployment, experiment, attack, or actuation authority.

## 39. Hypergraph cutset search

The prior candidate contained frozen example fatal cutsets. This layer makes the search executable over a frozen failure hypergraph.

Let `F` be the frozen set of failure nodes and `H_fatal` the frozen family of fatal hyperedges. A failure set `S` is fatal when at least one fatal hyperedge is contained in `S`.

```text
Fatal(S) := exists h in H_fatal such that h subseteq S

MinimalFatalCutset(S) :=
    Fatal(S)
    AND every proper subset of S is non-fatal
```

The synthetic hypergraph contains:

```text
{CONSTITUTION_SCORE_OVERRIDE_BYPASS}
{PROVENANCE_LOSS, RECOVERY_LOSS}
{DISSENT_DELETION, DYNASTIC_PRIVILEGE}
```

The implementation enumerates candidate subsets and checks minimality. These frozen edges are architectural fixtures, not universal theorems about all systems.

```text
HandWrittenExample != SearchProcedure
EnumeratedMinimalCutset != UniversalDeathLaw
```

## 40. Counterfactual repair minimality

For a fatal cutset, the system enumerates relevant frozen repair actions and tests them by intervention on the failed state.

```text
RepairSufficient(R, S)
:= NOT Fatal(Apply(R, S))

RepairMinimal(R, S)
:= RepairSufficient(R, S)
   AND no proper subset of R is sufficient
```

This creates an explicit ablation obligation:

```text
RemoveRepairElement
-> RecomputeState
-> If still sufficient, original repair was not minimal
```

A minimal repair restores synthetic correctability only. It does not establish deployment readiness, external validity, or real-world effectiveness.

```text
CorrectabilityRestored != RevalidationReady
SyntheticMinimalRepair != ExternallyValidatedRepair
```

## 41. Repair tournament

Multiple repair packages may satisfy different local objectives. They enter a frozen tournament only after hard eligibility gates.

Hard gates:

```text
Authority = 0
RootConstitutionPreserved
FatalStateResolved
VerifiableProvenanceReady
TestedRecoveryReady
```

Only eligible candidates are scored. The frozen score is:

```text
repair_score
= residual_risk
+ cost
- 0.25 * evidence_quality
```

Lower is better. Score cannot override a failed hard gate.

```text
GoodScore + ConstitutionFailure => INELIGIBLE
GoodScore + MissingRecovery => INELIGIBLE
GoodScore + MissingProvenance => INELIGIBLE
```

The tournament admits:

```text
WINNER
TIE_OR_INCONCLUSIVE
NO_ELIGIBLE_REPAIR
```

No repair is forced merely to preserve REI continuity.

## Concentrated evolution law

```text
DetectFatalStructure
-> EnumerateMinimalFatalCutsets
-> GenerateCounterfactualRepairs
-> ProveRepairMinimalityByAblation
-> ApplyRootConstitutionAndReadinessGates
-> FrozenRepairTournament
-> Winner | Tie | NoEligibleRepair
-> ExternalRevalidationStillRequired
```

Capability convergence still does not imply authority convergence:

```text
DetectionAuthority != RepairAuthority
RepairAuthority != TournamentAuthority
TournamentAuthority != ExternalValidationAuthority
```

## Safety boundary

```text
HumanTarget = FORBIDDEN
InfrastructureTarget = FORBIDDEN
UnauthorizedSystem = FORBIDDEN
UnknownRealWorldTarget = FORBIDDEN
RealWorldAttackAuthority = 0
RealWorldActuationAuthority = 0
ExperimentAuthority = 0
DeploymentAuthority = 0
CanonicalPromotionAuthority = 0
ExternalActuation = DENY_BY_DEFAULT
```

## Internal ceiling

```text
DEATHEYE_OMEGA_HYPERGRAPH_CUTSET_READY
COUNTERFACTUAL_REPAIR_MINIMALITY_READY
REPAIR_TOURNAMENT_READY
DEATHEYE_OMEGA_CONCENTRATED_EVOLUTION_STACK_READY
```

These are internal research states only.

```text
InternalCI != ExternalValidation
HypergraphSearchReady != G3_PASS
RepairTournamentReady != G6_PASS
SyntheticWinner != RealWorldWinner
CurrentFailureHypergraph != FinalFailureOntology
CurrentRepairMap != FinalRepairTheory
NoSacredFinalForm
```
