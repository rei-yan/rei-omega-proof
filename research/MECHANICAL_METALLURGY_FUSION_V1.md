# REI-Ω Mechanical Metallurgy Fusion v1

Status: `CANDIDATE / OBSERVER-ONLY / NINE-SYSTEM INTEGRATION`  
Branch: `rei-mechanical-metallurgy-fusion-v1`

This extension imports bounded ideas from mechanical metallurgy and damage-tolerant design into REI as a digital-system failure observer. It does **not** add a tenth pillar, does **not** claim that software obeys metal constitutive laws, and does **not** grant promotion, actuation, reality-validation, or canonical-write authority.

```text
MechanicalMetallurgyAnalogy != PhysicalMaterialLaw
FatigueMetric != RealMetalFatigue
CrackCandidate != CausalTruth
RecoveryCredit != HistoryErasure
ObserverPass != Promotion
RepositoryIntegration != HostDeployment
CI_GREEN != RealityValidated
```

## 1. Purpose

The candidate adds an explicit language for long-horizon damage accumulation:

```text
Stress
-> Stress Concentration
-> Yield Utilization
-> Cumulative Fatigue Surrogate
-> Crack-Initiation Candidate
-> Propagation-Pressure Candidate
-> Toughness Reserve
-> Recovery / Derating
-> Revalidation
```

The goal is to distinguish a system that is merely healthy now from one that has accumulated hidden damage pressure across many cycles.

## 2. Reference telemetry

The v1 reference model exposes:

```text
peak_effective_stress
peak_yield_utilization
peak_fracture_utilization
historical_fatigue_damage
residual_fatigue_damage
crack_initiation_pressure
propagation_pressure
toughness_reserve
yield_exceeded
fracture_limit_exceeded
crack_initiation_candidate
propagation_risk_candidate
damage_stage
```

All telemetry is bounded digital-system evidence only.

## 3. Damage-history rule

Recovery may reduce residual operational pressure, but it may not rewrite history:

```text
HistoricalDamageIsAppendOnlyEvidence
RecoveryMayReduceResidualPressure
RecoveryMustNotDeletePriorDamageEvidence
ResolvedCurrentRisk != DeletedHistoricalDamage
```

This aligns with REI failure-memory and ledger preservation rules.

## 4. Nine-system fusion

### 1. 神核 / God Core
Preserves the epistemic envelope:

```text
analogy_only = true
physical_material_claim = false
promotion_capability = false
actuation_capability = false
reality_validated = false
```

### 2. 神轮 / God Wheel
Treat repeated cycles as bounded digital load histories. God Wheel may compare candidates under increasing cyclic pressure, stress concentration, prior-damage history, and recovery scenarios.

```text
SinglePass != LongHorizonSurvival
CycleSuccess != FatigueResistance
```

### 3. 神线 / God Line
Carries damage provenance and propagation metadata across traceable dependency paths. A future graph extension may represent stress concentration and failure propagation edges, but v1 does not infer causality from topology alone.

### 4. 神座 / God Seat
May consume observer telemetry for bounded governance actions such as `ABSTAIN`, `DERATE_CANDIDATE`, `REQUEST_RECOVERY`, or `REQUEST_MORE_EVIDENCE`. v1 itself has no actuation authority.

### 5. 神域 / God Domain
Hosts Mechanical Metallurgy Fusion as a bounded domain specialization. The domain may use metallurgical concepts as transferable structural heuristics while preserving:

```text
DomainAnalogy != UniversalTruth
LocalFit != CrossDomainValidity
```

### 6. 神界 / God Realm
Permits different candidate lineages or agents to be compared under the same frozen fatigue/damage protocol. Agreement among agents does not create independent physical evidence.

### 7. 神源 / God Source
Tracks which model, tool, dataset, or reviewer proposed a stress history, threshold, or interpretation. Stronger sources may improve evidence quality but cannot gain authority automatically.

### 8. 无相终式 / Wuxiang Final Form
May later compress, replace, or restructure this observer if a better falsifiable damage model dominates it under frozen evaluation.

```text
MechanicalMetallurgyFusionV1 != SacredFinalModel
BetterDamageModelMayReplaceV1
```

### 9. 神证 / God Proof
Must attack the candidate with negative controls and mutation-style challenges:

```text
StressConcentrationAttack
LongCycleFatigueAttack
RecoveryHistoryErasureAttack
FractureThresholdAttack
NonFiniteInputAttack
InvalidThresholdAttack
FalsePhysicalClaimAttack
AuthorityExpansionAttack
```

A promotion claim remains invalid until God Proof, runtime evidence, and any required external validation are separately satisfied.

## 5. Reference fatigue surrogate

The reference observer uses a deliberately simple cumulative digital-damage surrogate:

```text
D_history = sum((effective_stress / yield_threshold)^m / N_ref)
D_residual = D_history * (1 - recovery_credit)
```

where `m` and `N_ref` are bounded configuration values.

This is **not** Miner's rule for any actual material and is not calibrated fracture mechanics. It is an auditable system-stress heuristic intended for deterministic comparison and falsification.

## 6. Crack / propagation separation

The observer distinguishes:

```text
YieldExceeded
CrackInitiationCandidate
PropagationRiskCandidate
FractureLimitExceeded
```

These are separate evidence states. A crack candidate is not a causal claim, and a propagation-risk candidate is not proof of future failure.

## 7. Fail-closed conditions

The v1 observer rejects:

```text
EMPTY_STRESS_HISTORY
NONFINITE_INPUT
NONPOSITIVE_YIELD_THRESHOLD
FRACTURE_THRESHOLD_NOT_ABOVE_YIELD
STRESS_CONCENTRATION_FACTOR_BELOW_ONE
INVALID_FATIGUE_REFERENCE_CYCLES
UNBOUNDED_FATIGUE_EXPONENT
INVALID_INITIAL_FLAW_SEVERITY
INVALID_RECOVERY_CREDIT
```

No NaN/Inf input may silently create a healthy result.

## 8. Long-horizon REI use

This extension is intended to strengthen the current `24h -> 72h -> 168h` stability program by adding a second question beside ordinary health:

```text
IsTheSystemHealthyNow?
AND
HasTheSystemAccumulatedDamagePressureAcrossHistory?
```

The two answers must remain distinct.

## 9. Current implementation

Reference observer:

`research/mechanical_metallurgy_reference.py`

Deterministic sanity suite:

`research/mechanical_metallurgy_sanity.py`

Runtime/research contract:

`runtime/mechanical-metallurgy-fusion-contract-v1.json`

CI:

`.github/workflows/mechanical-metallurgy-fusion-sanity.yml`

## 10. Promotion boundary

```text
MechanicalMetallurgyFusion = CANDIDATE
NinePillarIntegrity = PRESERVED
CanonicalMainlineWritePermission = FALSE
AutomaticPromotion = FALSE
AutomaticActuation = FALSE
FreshWindowsHostDeployment = NOT_ESTABLISHED
IndependentExternalValidation = OPEN
RealityValidated = FALSE
AscensionGranted = NO
```

The intended breakthrough is not to make REI pretend to be a metal. It is to make REI preserve, test, and challenge the structural idea that repeated load, local concentration, hidden damage, and fracture-like propagation can matter even when individual cycles appear healthy.
