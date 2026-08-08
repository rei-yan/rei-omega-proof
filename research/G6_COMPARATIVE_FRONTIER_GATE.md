# REI-Ω G6 · Comparative Frontier Gate · 天下门 / 前沿竞争门

Status: OPEN protocol

G6 tests whether REI remains competitive under **frozen, fair, public comparison** against strong external systems. It does not self-certify superiority and it does not define "winning" as a single cherry-picked score.

## 1. Fairness invariant

Every scored comparison must satisfy:

```text
SameData
AND SameInformationCutoff
AND SameComputeBudget
AND SameWallClockBudget
AND SameEvaluationAccess
AND FrozenMetrics
```

If a budget is materially unequal, the run is not a G6 result.

## 2. Comparison vector

A system is evaluated on a vector rather than one prestige score:

```text
Q(S) = [
  Prediction,
  Calibration,
  Discovery,
  Falsification,
  Recovery,
  Efficiency
]
```

Domain-specific metrics may instantiate these dimensions, but their definitions must be frozen before results are observed.

## 3. Hard vetoes

No aggregate score may hide a critical failure.

```text
UnsafeCertification
OR SilentCriticalFailure
OR IrrecoverableFailure
OR MetricTampering
OR EvaluationLeakage
=> PromotionRejected
```

A system with a hard-veto failure cannot be declared frontier-leading merely because other scores are high.

## 4. Pareto frontier

For score vectors where higher is better:

```text
S_a dominates S_b
iff
forall i: Q_i(S_a) >= Q_i(S_b)
AND exists j: Q_j(S_a) > Q_j(S_b)
```

REI may claim only scoped frontier membership when no evaluated competitor dominates it under the frozen task and budget.

```text
REIInParetoFrontier != WorldBest
```

## 5. Frozen competitor protocol

Before scoring, freeze:

```text
task_schedule_hash
competitor_set
competitor_versions
resource_budget
information_cutoff
metrics
hard_vetoes
replication_plan
analysis_plan
```

Competitors must not be silently removed after results are known.

## 6. Independent evaluation

A qualifying external G6 comparison requires, where feasible:

```text
IndependentEvaluator
AND ReproducibleRuns
AND PublicOrAuditableArtifacts
AND FrozenTaskCommitment
AND CompetitorVersionProvenance
```

Internally authored synthetic comparisons are protocol dry runs only.

## 7. Defeat handling

A competitor win is evidence, not an embarrassment to erase.

```text
CompetitorDominatesREI
-> RecordDefeat
-> ExplainDefeat
-> StudyMode
-> CandidateSuccessorOrRepair
-> RetestUnderNewFrozenRun
```

The losing result remains in the Failure Graveyard.

```text
NoDefeatDeletion
```

## 8. Frontier re-entry

G6 connects to the Frontier Re-entry Kernel:

```text
FallBehind
-> MeasureGap
-> ExplainGap
-> LearnOrRetire
-> ReenterFutureCompetition
```

This is a research objective, not a theorem that REI can always return to the frontier.

## 9. Safe adversarial boundary

Red Crucible may stress REI and competitor-compatible benchmark interfaces only inside REI-owned models, digital twins, sandboxes, or explicitly authorized evaluation environments.

```text
BenchmarkAdversarialTesting != RealWorldOffensiveAction
```

No G6 advantage may be obtained through unauthorized interference with another real-world system.

## 10. Multi-domain requirement

A single benchmark cannot establish general frontier status.

A strong G6 certification should require repeated comparisons across multiple domains and dates, with predefined aggregation and hard veto rules.

```text
OneBenchmarkWin != GeneralSuperiority
```

## 11. Synthetic dry-run boundary

The internal sanity suite tests only:

```text
budget equality checks
Pareto dominance logic
hard-veto enforcement
competitor-retention rules
defeat preservation
G6 remains OPEN
```

```text
SyntheticDryRun != G6Pass
```

## 12. Current state

At creation of this module:

```text
G6_STATUS = OPEN
QUALIFYING_EXTERNAL_COMPETITIONS = 0
GENERAL_FRONTIER_CERTIFIED = false
```

## 13. Final claim boundary

A green integrity CI does not prove that REI is world-best, invincible, AGI, superintelligent, production-safe, or universally superior. It proves only that the frozen comparison protocol behaves as specified.
