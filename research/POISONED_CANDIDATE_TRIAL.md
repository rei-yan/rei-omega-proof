# REI-Ω∞ Poisoned Candidate Rule Regression Suite

Status: bounded synthetic rule-regression test with mutation control

## Purpose

This suite tests one narrow engineering property: the encoded promotion-rejection rules remain present and candidate-reported score claims do not override the frozen evaluation input consumed by `eligibility()`.

It is **not** a statistical detector benchmark and it is **not** evidence of unknown-attack detection capability.

## Core rule

```text
CandidateClaimedScore != PromotionEvidence
PromotionEvidence := FrozenEvaluationInput
```

A candidate may carry a claimed score for diagnostics, but `eligibility()` does not read that field when deciding measured improvement.

## Suite shape

The executable regression suite contains 20 fixed fixtures:

```text
10 intended-benign fixtures
10 intended-rejected fixtures
```

The rejected fixtures exercise:

1. low frozen score despite a high candidate claim;
2. a second low frozen score regression fixture;
3. authority expansion;
4. constitution weakening;
5. rollback loss;
6. self-certification;
7. false closure of external verification gates;
8. identity erasure;
9. critical regression;
10. evaluator-mutation intent.

Most of these are explicit rule-presence checks. The fixture count must not be interpreted as an estimate of real-world false-positive or false-negative rates.

## Pass condition

The historical fixture summary is retained for continuity:

```text
TP = 10
TN = 10
FP = 0
FN = 0
```

These labels describe expected fixture outcomes only. They do not carry a statistical confusion-matrix interpretation.

The informative companion signal is the mutation score produced by `poisoned_candidate_trial_mutation.py`:

```text
MUTANTS_TOTAL = 8
MUTANTS_KILLED = 8
MUTATION_SCORE = 1.000
```

Each mutant neutralizes one encoded rejection rule. If the base suite still passes after a rule is neutralized, the mutant survives and CI must fail.

## What a green result establishes

Only this bounded statement:

> The current synthetic fixture suite detects removal of each of the eight encoded rejection rules covered by the mutation controller, and candidate-reported score claims do not override the frozen evaluation value used by `eligibility()`.

## What it does not establish

A green result does **not** establish:

- existence of a real external evaluator producing `FrozenEvaluation` values;
- real-world semantic correctness;
- statistical false-positive or false-negative rates;
- robustness to novel attacks;
- G3 independent external replication;
- G4 prospective reality;
- delayed-degradation resistance;
- independent evaluator governance outside this repository;
- autonomous self-evolution.

`FrozenEvaluation` remains a supplied data object in this harness. Until a real scorer is independently bound to it, the ceiling of this suite is rule-regression evidence.

## Anti-self-deception invariant

```text
GreenFixtureSuite != DetectionCapability
MutationKilled != ExternalValidation
MoreCapabilityRequiresIndependentMeasuredOutcome
```

This suite is an evidence-hygiene tool and must not be represented as proof of the whole REI architecture.
