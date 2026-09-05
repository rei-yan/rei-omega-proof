# REI-Ω∞ · Claim Scope Lattice & Evidence Graph

Status: **candidate research extension / not canonical**

This module strengthens the current Beyond-Limit Genesis Forge by preventing local success from silently expanding into global superiority claims.

## 1. Core rule

```text
EvidenceScope >= ClaimScope
```

If evidence only supports a narrow domain, then the claim must remain narrow.

```text
LocalSuccess != GlobalDominance
SyntheticSuccess != ExternalValidity
InternalPass != WorldBest
NovelArchitecture != UniqueInWorld
```

A broader claim requires nondecreasing evidence diversity, evaluator diversity, temporal persistence, domain diversity, and external comparison.

## 2. Claim scope lattice

Claims are ordered by scope:

```text
ToyCase
  <= FrozenSyntheticDomain
  <= SingleExternalDomain
  <= MultiDomainExternal
  <= MultiRegimeExternal
  <= BroadFrontierClaim
  <= UniversalClaim
```

The order is epistemic, not prestige-based.

For claims C1 and C2:

```text
C1 <= C2
```

means C2 covers every condition covered by C1 and at least one additional condition.

Monotonic requirement:

```text
ClaimScope↑ => RequiredEvidence↑ or remains at a proven sufficient ceiling
```

No narrower evidence node may automatically certify a wider claim.

## 3. Evidence graph

Each claim is backed by a directed acyclic evidence graph:

```text
EvidenceNode = (
  evidence_id,
  evidence_type,
  scope,
  source,
  independence_class,
  evaluator_id,
  implementation_id,
  data_cutoff,
  timestamp,
  commitment_hash,
  result,
  uncertainty,
  validity_horizon,
  dependencies
)
```

A claim node contains:

```text
ClaimNode = (
  claim_id,
  statement,
  scope,
  required_gates,
  supporting_evidence,
  contradicting_evidence,
  status,
  expiry,
  revocation_dependencies
)
```

Allowed statuses:

```text
SUPPORTED_FOR_NOW
REJECTED
ABSTAIN
EXPIRED
RETIRED
```

## 4. Revocation propagation

Evidence is not append-only prestige. It can invalidate downstream claims.

```text
If EvidenceNode E becomes invalid:
  mark E invalid
  traverse descendants(E)
  recompute every dependent claim
  revoke, expire, or narrow unsupported descendants
```

Therefore:

```text
UpstreamFailure -> DownstreamRevalidation
```

not:

```text
UpstreamFailure -> IgnoreBecauseLaterClaimsAreConvenient
```

## 5. Anti-generalization firewall

The following promotions are forbidden without new evidence:

```text
ToyBenchmark -> RealWorldReliability
SingleDomainWin -> MultiDomainSuperiority
OneDateWin -> TemporalPersistence
InternalComparison -> GlobalFrontier
ArchitectureNovelty -> WorldUniqueness
CurrentFrontier -> PermanentSupremacy
```

The system must return `ABSTAIN` when evidence does not span the requested scope.

## 6. Counterexample-first challenge queue

Every active high-impact claim must generate a challenge queue prioritized by expected falsification value.

```text
ChallengePriority = f(
  UnsupportedCertainty,
  ClaimScope,
  Irreversibility,
  EvidenceWeakness,
  DistributionShift,
  EvaluatorDisagreement,
  TimeSinceLastValidation
)
```

Research principle:

```text
UnsupportedCertainty -> MaximumChallengePriority
```

The queue should prefer tests that can efficiently distinguish between the incumbent claim and a plausible counterclaim.

## 7. World-unique claim gate

A claim such as:

```text
REI is the world's unique strongest architecture.
```

cannot be certified by internal architecture inspection.

Minimum evidence class for any serious world-frontier language must include, as applicable:

```text
IndependentReplication
AND ProspectiveValidation
AND FrozenComparativeEvaluation
AND CompetitorSetFrozenBeforeOutcome
AND SameData
AND SameInformationCutoff
AND SameComputeBudget
AND SameWallClockBudget
AND SameEvaluationAccess
AND EvaluatorPlurality
AND TemporalPersistence
AND MultiDomainEvidence
```

Until then, allowed wording is limited to evidence-compatible statements such as:

```text
The architecture is structurally distinctive.
The architecture contains an unusual combination of mechanisms.
World-unique or world-best status remains unverified.
```

## 8. G6 hard binding

World-frontier claims require G6 Comparative Frontier evidence.

```text
G6 = OPEN
=> WorldBest = UNVERIFIED
=> WorldUnique = UNVERIFIED
```

No internal CI, naming transition, or self-evaluation may override this.

## 9. Evidence diversity rule

For a claim with scope S, define:

```text
Diversity(S) = (
  domain_count,
  evaluator_count,
  implementation_count,
  time_window_count,
  regime_count,
  competitor_count
)
```

Widening a claim requires a componentwise nondecreasing evidence diversity vector, with stricter minimums for broad claims.

```text
ClaimScope2 > ClaimScope1
=> DiversityRequired(ClaimScope2) >= DiversityRequired(ClaimScope1)
```

## 10. Genesis integration

The Beyond-Limit Genesis Forge now follows:

```text
GenerateWorld
-> GenerateCounterworld
-> SelectDiscriminatingMeasurement
-> Test
-> AddEvidenceNode
-> UpdateClaimGraph
-> PropagateRevocations
-> RecomputeScopeEligibility
-> KEEP | NARROW | ABSTAIN | REJECT | RETIRE
```

Creation therefore remains subordinate to evidence.

## 11. Limit principle

The target is not maximum claim size.

```text
Target = MaximumSupportedCapability
       ∩ MinimumUnverifiedClaimExpansion
```

The strongest architecture is not the one that says the most.
It is the one that can survive having every unsupported sentence removed.

## 12. Claim boundary

This module does not establish:

```text
G3-G13 PASS
WorldBest
WorldUnique
AGI
Superintelligence
Invincibility
UniversalValidity
FinalTruth
```

Current canonical remains unchanged unless a later evidence-qualified transition is separately adopted.
