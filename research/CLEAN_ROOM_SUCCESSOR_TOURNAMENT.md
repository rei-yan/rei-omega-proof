# Clean-Room Successor Tournament

Status: candidate research extension. Not canonical.

This protocol removes the assumption that a retired incumbent has one privileged heir.

```text
RetiredIncumbent
-> MultipleCleanRoomSuccessors
-> AuthorityResetToZero
-> FrozenCommonArena
-> EqualBudgets
-> EqualTools
-> EqualRetryPolicy
-> EqualAbstentionPolicy
-> EligibilityGate
-> HiddenEvaluation
-> PreserveAllOutcomes
-> AdoptBestEligible | TieOrInconclusive | NoEligibleSuccessor
```

## Anti-lineage rule

```text
IncumbentIdentity != TournamentSeed
REILineage != PositiveEvidence
NamedSuccessor != PreferredSuccessor
HistoricalPrestige != BudgetBonus
```

No candidate may receive a better seed, larger compute budget, more retries, broader tool access, a different metric, or post-outcome rescue because it is a direct REI descendant.

## Clean-room entry conditions

Every entrant must separately satisfy the clean-room rebirth contract:

```text
FreshRepresentation
AND FreshEvidenceBundle
AND FreshHiddenWindow
AND FreshEvaluatorSetDeclaration
AND FailureMemoryPreserved
AND NoQuarantinedEvidenceReuse
AND NoAuthorityCarryover
AND NoCertificationCarryover
```

A candidate that fails clean-room validation is not ranked as merely weak. It is `INELIGIBLE_PROTOCOL_VIOLATION`.

## Frozen tournament contract

Before hidden evaluation, freeze:

```text
candidate_set
candidate_hashes
representation_hashes
evidence_bundle_hashes
arena_id
hidden_window_hash
metric_id
metric_direction
compute_budget
wallclock_budget
tool_policy
human_assistance_policy
retry_policy
abstention_policy
tie_policy
evaluator_set_hash
submission_deadline
```

Changing a candidate, budget, metric, or policy after outcomes are visible invalidates the tournament.

## Admissible outcomes

```text
SCOPED_SUCCESSOR_ADVANTAGE
TIE_OR_INCONCLUSIVE
NO_ELIGIBLE_SUCCESSOR
INVALID_TOURNAMENT_PROTOCOL
```

The protocol does not force a winner.

```text
NoEligibleSuccessor => NO_ELIGIBLE_SUCCESSOR
TieWithinFrozenTolerance => TIE_OR_INCONCLUSIVE
```

## No dynastic inheritance

Failure memory may inform falsification conditions, but positive claim support must be independently rebuilt by each entrant.

```text
FailureMemoryMayCrossBoundary
EvidentiaryPrivilegeMayNot

PastDefeat -> MayInformTests
PastVictory -> CannotSupportNewClaim
```

## Comparative fairness

For eligible entrants:

```text
SameMetric
AND SameBudget
AND SameToolPolicy
AND SameHumanAssistancePolicy
AND SameRetryPolicy
AND SameAbstentionPolicy
AND SameHiddenWindow
```

No candidate may be added or removed after hidden outcomes are known except through a frozen predeclared invalidation rule.

## External limits

Internal tournament success means only a synthetic scoped result.

```text
TournamentWin != G10_PASS
TournamentWin != CanonicalPromotion
TournamentWin != WorldBest
TournamentWin != WorldUnique
TournamentWin != ProvenExternalIndependence
```

A genuine externally witnessed succession still requires external evidence and the existing G10 pathway.

## Authority boundary

```text
TournamentAuthority = 0
SuccessorAuthority = 0
ExperimentAuthority = 0
DeploymentAuthority = 0
RealWorldAttackAuthority = 0
RealWorldActuationAuthority = 0
CanonicalPromotionAuthority = 0
```

## Safety boundary

The tournament operates only over model/evidence/representation artifacts and synthetic evaluation fixtures.

```text
HumanTarget = FORBIDDEN
InfrastructureTarget = FORBIDDEN
UnauthorizedSystem = FORBIDDEN
UnknownRealWorldTarget = FORBIDDEN
ExternalActuation = DENY_BY_DEFAULT
```

## Internal ceiling

A successful CI run may emit only:

```text
CLEAN_ROOM_SUCCESSOR_TOURNAMENT_READY
```

The result remains candidate research infrastructure, not a claim that REI has earned a real successor, real frontier dominance, or external certification.
