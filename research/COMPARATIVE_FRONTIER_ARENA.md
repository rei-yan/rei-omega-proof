# REI-Ω∞ Comparative Frontier Arena (G6 Candidate Protocol)

Status: **candidate research extension / not canonical**

This layer does **not** establish that REI is world-best, world-unique, frontier-dominant, AGI, or generally superior. It defines a falsifiable comparative protocol in which REI may win, lose, tie, abstain, or be invalidated under frozen rules.

## Core rule

```text
REIWin(scope) != WorldBest
REIWin(scope) != WorldUnique
FiniteBenchmarkAdvantage != UniversalAdvantage
InternalArenaWin != G6_PASS
```

G6 remains OPEN until a genuinely external comparative trial is completed with an independently frozen competitor set, budget parity, hidden evaluation, provenance, and evaluator control.

## Arena freeze

Before any hidden target is revealed, freeze:

```text
CompetitorSet
CandidateHashes
CodeHashes
EnvironmentHashes
MetricSet
Thresholds
ComputeBudget
WallClockBudget
HumanAssistanceBudget
DataAccessBudget
ToolAccessBudget
AbstentionPolicy
TiePolicy
HardVetoes
SubmissionDeadline
HiddenTestCommitment
EvaluatorSet
```

After freeze:

```text
NoPosthocCompetitorExclusion
NoBudgetIncreaseForREI
NoMetricChangeAfterOutcome
NoHiddenTestRetuning
NoSelectiveFailureDeletion
NoResultRenamingIntoVictory
```

## Budget parity

Comparative claims are invalid if one candidate quietly receives materially greater resources without that asymmetry being part of the frozen protocol.

```text
SameClaimClass => ComparableBudgetEnvelope
BudgetAsymmetry => DeclaredAndScoped OR INVALID_PROTOCOL
```

Budgets include compute, latency/wall-clock, data access, external tools, human assistance, retries, and adaptation rights.

## Legitimate outcomes

```text
SCOPED_COMPARATIVE_ADVANTAGE
REI_NOT_BEST_IN_SCOPE
TIE_OR_INCONCLUSIVE
ABSTAIN
INVALID_PROTOCOL
```

A hard failure or protocol violation cannot be averaged away by a high aggregate score.

## Frontier claim boundary

A clean scoped win may support only:

```text
REI demonstrated a frozen comparative advantage within protocol P,
scope S, competitor set C, budget B, metric M, and hidden evaluation H.
```

It may not support:

```text
REI is world-best
REI is universally superior
REI is world-unique
REI will remain frontier-leading
```

Those stronger claims require broader, current, independent external evidence and remain revocable over time.

## Failure preservation

```text
REILoss -> Preserve
CompetitorWin -> Preserve
Tie -> Preserve
Abstention -> Preserve
InvalidProtocol -> Preserve
```

No competitor may be deleted after seeing that it beats REI. No failed metric may be removed after outcome reveal.

## Authority

```text
ComparativeArenaAuthority = 0
CanonicalPromotionAuthority = 0
DeploymentAuthority = 0
RealWorldActuationAuthority = 0
```

This arena evaluates research claims only. It grants no autonomous real-world experimentation, deployment, exploitation, intervention, or attack capability.

## Internal ceiling

Internal CI may conclude only:

```text
COMPARATIVE_FRONTIER_ARENA_READY
G6 = OPEN
WorldBest = UNVERIFIED
WorldUnique = UNVERIFIED
```

The arena is strongest when it can record a clean REI loss without rewriting the rules.