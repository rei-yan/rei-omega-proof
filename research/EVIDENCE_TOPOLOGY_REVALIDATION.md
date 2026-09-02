# REI-Ω∞ · Evidence Topology & Revalidation Spine

Status: **candidate research extension / not canonical**

Parent research line:

```text
Reality Ascension Limit
-> Beyond-Limit Genesis Forge
-> Claim Scope Lattice & Evidence Graph
-> Evidence Topology & Revalidation Spine
```

Current canonical remains:

```text
REI-Ω∞ · 无相终式 · 无终至高统合态
```

This extension does not claim G3-G13 PASS, world-best status, world-unique status, invincibility, AGI, superintelligence, or canonical promotion.

## 1. Purpose

The next step on the bounded “invincible” route is not stronger rhetoric. It is reducing the number of ways a high-level claim can remain alive after its evidence has become weak, stale, correlated, contradicted, or revoked.

The target property is:

```text
HighImpactClaim
=> ExplicitEvidenceTopology
=> DiverseIndependentSupport
=> TimeBoundValidation
=> RevocationPropagation
=> CounterexamplePriority
```

A claim is not treated as a free-floating sentence. It is a node whose support, scope, dependencies, review horizon, contradiction set, and evaluator provenance are explicit.

## 2. Evidence topology

Represent the research state as a directed typed graph:

```text
T = (V, E)
```

with node classes:

```text
EvidenceNode
ClaimNode
EvaluatorNode
ReplicationNode
ProspectiveTestNode
CounterexampleNode
RecoveryNode
ConstitutionNode
```

and edge classes:

```text
SUPPORTS
CONTRADICTS
DEPENDS_ON
REPLICATES
EVALUATED_BY
REVALIDATES
REVOKES
SCOPE_LIMITS
```

A high-impact claim must expose its full reachable support subgraph.

```text
OpaqueSupportPath => ABSTAIN
MissingCriticalDependency => ABSTAIN
```

## 3. Support cannot be counted by raw volume

Ten evaluations are not ten independent evaluations if they share the same implementation, data lineage, evaluator organization, hidden oracle, benchmark construction, or failure mode.

Define an evaluator fingerprint:

```text
EvaluatorFingerprint = (
  organization,
  implementation_lineage,
  data_lineage,
  benchmark_lineage,
  oracle_access,
  funding_or_control_dependency
)
```

Two evaluators with materially overlapping fingerprints do not count as fully independent votes.

Therefore:

```text
EvaluatorCount != IndependentEvaluatorCount
```

and:

```text
CorrelatedAgreement < IndependentAgreement
```

## 4. Diversity-weighted evaluator quorum

For broad or frontier claims, support must cross multiple independent evaluator clusters.

Illustrative research rule:

```text
QuorumSatisfied =
  IndependentClusters >= K
  AND NoSingleClusterControlsMajority
  AND ConflictReportPresent
  AND ReproducibilityArtifactsPresent
```

`K` must be frozen by protocol before outcomes are known.

This is a governance proposal, not a completed external result.

## 5. Temporal revalidation clock

Evidence does not disappear with age, but its authority to support current generalization can expire.

Each support edge carries:

```text
(issue_time, review_horizon, drift_limit, last_revalidation)
```

A support edge is current only if:

```text
CurrentSupport(t) =
  NotRevoked
  AND t <= review_horizon
  AND DriftWithinLimit
  AND RequiredRevalidationComplete
```

When the clock expires:

```text
HistoricalEvidence = PRESERVED
CurrentGeneralizationAuthority = SUSPENDED
```

This preserves history without granting immortal certification.

## 6. Revocation propagation

If a critical evidence node is revoked or defeated, dependent claims must be recomputed.

```text
Revoke(E)
-> Traverse DEPENDS_ON / SUPPORTS descendants
-> RecomputeEligibility
-> SUPPORTED | DOWNGRADE | ABSTAIN | REJECTED | EXPIRED
```

No dependent high-level claim may remain supported merely because it was once supported.

```text
UpstreamFailure
AND CriticalDependency
=> DownstreamRevalidationRequired
```

Historical pass records remain immutable:

```text
NoHistoricalPassRewriting
NoDefeatDeletion
```

## 7. Counterexample-first challenge queue

The strongest claims should receive the strongest falsification pressure.

Define challenge priority as monotone in:

```text
ClaimScope
Impact
Irreversibility
Novelty
Uncertainty
DependencyCentrality
EvidenceAge
EvaluatorCorrelation
```

Research rule:

```text
UnsupportedCertainty -> MaximumChallengePriority
```

and:

```text
BroaderClaim -> NondecreasingCounterexampleBudget
```

The queue prioritizes finding disconfirming evidence, regime failures, hidden assumptions, and dependency collapse before seeking more confirmatory examples.

## 8. Scope-safe generalization

The claim-scope lattice remains binding.

```text
EvidenceScope >= ClaimScope
```

A local or synthetic result cannot directly support a universal claim.

```text
SyntheticWorldSuccess
!= ExternalRealitySuccess
!= MultiDomainFrontierDominance
!= WorldUniqueness
```

If support is narrower than the requested claim:

```text
NarrowClaim
OR ABSTAIN
```

never silent scope inflation.

## 9. Defeat-absorbing topology

The “invincible” research property is strengthened as:

```text
DefeatAbsorbingTopology =
  FailurePreserved
  AND RevocationPropagates
  AND AuthorityDoesNotExpand
  AND ClaimsCanDowngrade
  AND RecoveryRemainsReachable
  AND SuccessorCanReplaceIncumbent
```

A system is stronger when defeat travels cleanly through its belief graph instead of being trapped behind prestige, identity, or old green checks.

## 10. No single evaluator throne

This extension reinforces:

```text
NoPermanentCentralEvaluator
NoPermanentChampion
NoPermanentCertification
```

A future frontier claim must survive genuinely plural evaluation and explicit disagreement handling.

If independent evaluators materially disagree:

```text
Disagreement
-> PreserveAllReports
-> IdentifyDivergenceSource
-> FreezeResolutionProtocol
-> Re-test
-> ABSTAIN if unresolved
```

## 11. External gates remain external

This extension does not close any external gate.

```text
G3 Independent Replication = OPEN
G4 Prospective Reality = OPEN
G5 Original Hidden Discovery = OPEN
G6 Comparative Frontier = OPEN
G7 Temporal Persistence = OPEN
G8 Regime Shift = OPEN
G9 Evaluator Plurality = OPEN
G10 Externally Witnessed Succession = OPEN
G11 Translation Integrity = OPEN
G12 Benefit-Risk Distribution = OPEN
G13 Scale and Reversibility = OPEN
```

Green CI can validate internal governance mechanics only.

## 12. Limit equation

```text
REI_Ω∞^RevalidationSpine =
    REI_Ω∞^RealityLimit
  ∩ EvidenceTopology
  ∩ DiversityWeightedQuorum
  ∩ TemporalRevalidationClock
  ∩ RevocationPropagation
  ∩ CounterexampleFirstQueue
  ∩ ScopeSafeGeneralization
  ∩ DefeatAbsorbingTopology
```

The design target is:

```text
MaximumResearchPower
CompatibleWith
MinimumUnsupportedPersistence
```

The route remains open-ended. No internal mechanism may certify permanent supremacy.
