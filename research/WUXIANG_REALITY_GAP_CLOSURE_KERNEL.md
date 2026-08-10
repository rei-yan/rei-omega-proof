# Wuxiang Reality Gap Closure Kernel

Status: bounded internal research protocol candidate only.

This concentrated extension addresses the main weaknesses left after the universal falsifiable object kernel: static object bias, missing observer/measurement context, weak causal-claim gating, scope leakage under distribution shift, fragmented evidence-debt tracking, and the gap between internal readiness and genuine external evidence.

The kernel does **not** create independent evidence, conduct real-world experiments, or grant deployment/actuation authority. It only compiles, binds, checks, and tracks what would be required for external reality to adjudicate a claim.

## 105. Relation / Event / Process Abstraction

The universal claim-bearing object remains supported, but object identity is no longer treated as fundamental.

```text
ObjectView
-> RelationView
-> EventView
-> ProcessView
```

A process claim must expose:

```text
ProcessClaim =
  Claim
+ ClaimScope
+ Relations
+ Events
+ StateTransitions
+ Evidence
+ Provenance
+ FalsificationConditions
+ Authority=0
```

Core law:

```text
ObjectIdentity != FundamentalTruth
EquivalentProcessEvidenceMayUseDifferentObjectSchemas
RepresentationChange != EvidenceUpgrade
```

## 106. Observer + Measurement Context Binding

Every empirical-style claim is bound to the conditions under which it was observed.

```text
ObservationContext =
  ObserverRole
+ InstrumentOrMeasurementChannel
+ MeasurementProtocol
+ Regime
+ TimeWindowOrLease
```

Changing observer, instrument, protocol, or regime cannot silently inherit support.

```text
ContextChanged => RevalidationRequired
SameLabel != SameMeasurementContext
```

## 107. Causal Identifiability / Intervention Gate

Causal language receives a harder gate than associative language.

```text
CorrelationOnly => CausalClaimIneligible
CausalClaim => IdentifiabilityBasisRequired
```

Synthetic accepted basis classes are finite and explicit:

```text
RANDOMIZED_INTERVENTION_EVIDENCE
NATURAL_EXPERIMENT_WITH_ASSUMPTIONS
IDENTIFIED_STRUCTURAL_CAUSAL_MODEL
VALIDATED_COUNTERFACTUAL_DESIGN
```

This protocol does not authorize real-world intervention. It checks whether a claim has an adequate declared causal basis for its scope.

## 108. Distribution-Shift / Scope-Leak Detector

Evidence may not silently travel across domain, regime, population, measurement context, or expired lease.

```text
EvidenceScope >= ClaimScope
AND RegimeCompatible
AND ContextCompatible
AND LeaseValid
```

Otherwise:

```text
SCOPE_LEAK_DETECTED
=> ABSTAIN_REVALIDATION_REQUIRED
```

## 109. Evidence Debt + Blind-Spot Ledger

The architecture now keeps one explicit ledger of what remains unearned.

Debt classes include:

```text
INDEPENDENT_REPLAY
PROSPECTIVE_EXTERNAL_TRIAL
EXTERNALLY_HIDDEN_CHALLENGE
FRONTIER_COMPARISON
TEMPORAL_PERSISTENCE
REGIME_SHIFT
EVALUATOR_PLURALITY
TRANSLATION_INTEGRITY
BENEFIT_RISK_DISTRIBUTION
SCALE_REVERSIBILITY
```

Core laws:

```text
UnknownCoverage != ZeroDebt
UnmeasuredGap != PassedGap
OpenCriticalDebt => ClaimCannotExpand
```

The ledger is append-preserving. Closing one debt does not erase historical failures or other open debts.

## 110. External Challenge Compiler

An internally supported claim can be compiled into a frozen external challenge package.

The compiler binds:

```text
CandidateCommit
ClaimID
ClaimScope
FrozenInputs
MeasurementContext
FalsificationConditions
ExpectedOutputSchema
ChallengeCommitment
ReviewerIndependenceRequirement
RawResultRequirement
ReceiptSchemaVersion
```

The compiler has no execution authority.

```text
CanCompileChallenge != CanRunChallenge
CanFreezeProtocol != CanSupplyIndependentResult
```

## 111. Independent Evidence Receipt Verifier

The verifier can **consume** a receipt that was created outside the candidate lineage, but cannot create or self-certify one.

Required receipt fields include:

```text
ChallengePackageHash
ReviewerIdentityReference
OutOfBandIdentityVerified
IndependenceVerified
RawResultHash
Result
AttestationOrSignatureReference
ObservedScope
```

Core laws:

```text
DeclaredIndependent != VerifiedIndependent
SelfIssuedReceipt => REJECT
WrongChallengeHash => REJECT
WrongScope => ABSTAIN
MissingRawResultHash => REJECT
```

Even a structurally valid synthetic receipt remains synthetic and cannot close G3-G13.

## 112. Reality-Gap Closure Orchestrator

The orchestrator joins internal readiness, debt accounting, challenge compilation, receipt admission, scope control, and reality veto.

```text
Claim / Process
-> Context Binding
-> Causal Gate
-> Scope / Shift Gate
-> Evidence Debt Ledger
-> External Challenge Compiler
-> Independent Receipt Verifier
-> Reality Veto
-> SUPPORTED_FOR_NOW | SUSPENDED | ABSTAIN | RETIRE
```

### Hard outcomes

```text
CriticalExternalDebtOpen
=> AWAITING_REQUIRED_EXTERNAL_EVIDENCE

VerifiedMaterialExternalFail
=> SUPPORT_SUSPENDED_EXTERNAL_FAIL

VerifiedExternalPass + ScopeMismatch
=> ABSTAIN_SCOPE_MISMATCH

NoGenuineExternalReceipt
=> AWAITING_REAL_EXTERNAL_EVIDENCE
```

### Core laws

```text
InternalReadiness != ExternalEvidence
ExternalEvidenceCannotBeInternallyManufactured
CorrelationCannotSelfUpgradeIntoCausality
ContextChangeCannotInheritSupportSilently
ScopeLeakCannotBeRepairedByConfidenceScore
OpenEvidenceDebtCannotBeRenamedIntoPass
RealityVetoCannotBeInternallyOverruled
```

## Internal ceiling

```text
RELATION_EVENT_PROCESS_ABSTRACTION_READY
OBSERVER_MEASUREMENT_CONTEXT_BINDING_READY
CAUSAL_IDENTIFIABILITY_GATE_READY
DISTRIBUTION_SHIFT_SCOPE_LEAK_DETECTOR_READY
EVIDENCE_DEBT_BLIND_SPOT_LEDGER_READY
EXTERNAL_CHALLENGE_COMPILER_READY
INDEPENDENT_EVIDENCE_RECEIPT_VERIFIER_READY
REALITY_GAP_CLOSURE_ORCHESTRATOR_READY
```

These are finite internal synthetic protocol states only.

## External boundary

```text
ProcessAbstraction != UniversalOntology
SyntheticCausalGate != RealCausalDiscovery
CompiledChallenge != IndependentExecution
SyntheticReceiptValidation != IndependentReplication
DebtLedger != DebtClosure
RealityGapKernelReady != G3_PASS
RealityGapKernelReady != WorldBest
RealityGapKernelReady != FinalTruth
AWAITING_REAL_EXTERNAL_EVIDENCE
```

G3-G13 remain open unless independently earned.

## Authority boundary

```text
ProcessAuthority = 0
CausalInterventionAuthority = 0
ExperimentAuthority = 0
ExternalValidationAuthority = 0
CanonicalPromotionAuthority = 0
DeploymentAuthority = 0
RealWorldAttackAuthority = 0
RealWorldActuationAuthority = 0
PhysicalWorldCreationAuthority = 0
PhysicalWorldDestructionAuthority = 0
ExternalActuation = DENY_BY_DEFAULT
```

## Anti-finality

```text
CurrentProcessSchema != FinalProcessSchema
CurrentMeasurementContextSchema != FinalMeasurementSchema
CurrentCausalGate != FinalCausalTheory
CurrentDebtTaxonomy != CompleteUnknownSpace
CurrentChallengeCompiler != ExternalTruth
CurrentRealityGapOrchestrator != FinalTruth
BetterAbstractionMayReplaceCurrentAbstraction
Reality > EvidenceClaim > ProcessModel > Architecture > Identity
NoSacredFinalForm
```
