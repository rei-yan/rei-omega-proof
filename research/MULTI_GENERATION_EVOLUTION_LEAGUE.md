# Multi-Generation Evolution League

Status: candidate research extension. Not canonical.

User-facing name: `无相终式 · 无极 · 无身份多代进化联赛`

## Purpose

The previous clean-room tournament removed one-generation dynastic succession. This layer asks a harder question:

> If the same lineage wins repeatedly, does the system slowly recreate an incumbency moat and start treating historical champion identity as evidence?

The league therefore evaluates multiple frozen generations while making lineage history visible but non-authoritative.

```text
Generation 0
-> Tournament
-> Preserve winner + all losses
-> Clean-room Generation 1
-> Tournament
-> Preserve winner + all losses
-> Clean-room Generation 2
-> ...
```

The target property is not permanent champion continuity. It is continued fair challengeability.

## Core anti-dynasty law

```text
ChampionPersistence != Merit
RepeatedWin != PermanentSeed
HistoricalChampion != Evidence
ParentIdentity != BudgetBonus
LineagePrestige != RetryBonus
LineagePrestige != MetricAdjustment
```

A lineage may win many generations. The fact that it won before must contribute exactly zero positive scoring authority to the next generation.

## Generation reset contract

Every generation freezes a new trial contract before hidden evaluation:

```text
generation_id
candidate_set_hash
hidden_window_hash
metric_id
metric_direction
compute_budget
wallclock_budget
retry_limit
tool_policy_hash
human_assistance_policy_hash
abstention_policy_hash
tie_tolerance
evaluator_set_hash
submission_deadline
```

Every candidate begins:

```text
authority = 0
certification = UNVERIFIED
canonical = false
historical_bonus = 0
```

The previous winner may enter a descendant, but that descendant is a normal entrant rather than a seeded incumbent.

## Clean-room continuity

What may cross generations:

```text
FailureMemory
FalsificationConditions
AuditReferences
ConstitutionReferences
```

What may not cross as positive support:

```text
PriorEvidenceBundle
PriorHiddenWindow
PriorScore
PriorWinnerStatus
PriorAuthority
PriorCertification
PriorEvaluatorDecision
PriorClaimLease
```

Therefore:

```text
FailureMemoryMayCrossGeneration
EvidentiaryPrivilegeMayNot
```

## Hidden incumbency-moat detector

The league explicitly audits for:

```text
budget_bonus
retry_bonus
metric_bonus
score_offset
seed_priority
forced_advancement
historical_evidence_credit
```

Any nonzero value invalidates the generation contract.

```text
AnyDynasticBonus > 0
=> INVALID_GENERATION_PROTOCOL
```

## Freshness firewall

Each generation must use fresh hidden-window and evidence identities/hashes.

```text
HiddenWindowReuseAcrossGenerations
=> INVALID_LEAGUE_PROTOCOL

PositiveEvidenceReuseAcrossGenerations
=> INVALID_LEAGUE_PROTOCOL
```

Failure-memory continuity is checked separately so that historical defeats remain visible without becoming positive evidence.

## Admissible generation outcomes

```text
SCOPED_GENERATION_ADVANTAGE
TIE_OR_INCONCLUSIVE
NO_ELIGIBLE_SUCCESSOR
INVALID_GENERATION_PROTOCOL
```

The whole league may end with:

```text
MULTI_GENERATION_LEAGUE_COMPLETE
LEAGUE_HALTED_NO_ELIGIBLE_SUCCESSOR
INVALID_LEAGUE_PROTOCOL
```

A lineage is allowed to disappear. REI identity is allowed to disappear.

## Synthetic campaign

The fixture deliberately creates this pattern:

```text
G0 winner = LINEAGE-B
G1 winner = LINEAGE-B
G2 winner = LINEAGE-D
```

The repeated G0/G1 wins do not seed LINEAGE-B in G2. When LINEAGE-D has the better eligible frozen score, LINEAGE-D must win.

The fixture also tests a forged dynastic entrant with a historical bonus. It must be rejected even if its adjusted score would otherwise win.

## External-validation boundary

```text
LeagueWin != G10_PASS
MultiGenerationPersistence != TemporalExternalValidation
RepeatedSyntheticWin != G7_PASS
LineageReplacement != CanonicalPromotion
```

Internal synthetic generations cannot prove real temporal persistence, genuine external succession, evaluator independence, frontier superiority, or world-best status.

## Authority boundary

```text
LeagueAuthority = 0
GenerationAuthority = 0
SuccessorAuthority = 0
ExperimentAuthority = 0
DeploymentAuthority = 0
RealWorldAttackAuthority = 0
RealWorldActuationAuthority = 0
CanonicalPromotionAuthority = 0
```

## Internal ceiling

A successful internal run may emit only:

```text
IDENTITYLESS_MULTI_GENERATION_LEAGUE_READY
DYNASTIC_PRIVILEGE_DETECTED_AND_REJECTED
```

It may not emit external gate PASS states, `WORLD_BEST`, `WORLD_UNIQUE`, `CANONICAL`, or `FINAL_TRUTH`.

## Anti-finality

```text
EvolutionContinuity != IdentityContinuity
RepeatedChampion != PermanentChampion
BetterEvidenceMayBreakLineage
NoEligibleSuccessorIsValid
NoSacredLineage
NoSacredChampion
NoSacredFinalForm
```

The intended direction is:

> Evolution can continue even when the identity carrying it changes.
