# REI-Ω∞ · Regime-Adversarial Multiverse Arena

Status: **candidate research extension / not canonical**

Parent line: `REI-Ω∞ · 无相终式 · Beyond-Limit Genesis Forge`

## Purpose

This arena tests whether a frozen research lineage survives across multiple synthetic worlds without hindsight retuning, scope inflation, or narrative repair after outcome.

It is not a real-world attack engine. `Adversarial` here means adversarial evaluation against models, ontologies, causal grammars, transfer claims, and REI-owned research artifacts.

## Core rule

```text
UnknownRegime
-> Detect | Abstain | Recover
not
-> RetuneHistoryAndDeclareVictory
```

A lineage is frozen before target-world evaluation:

```text
Freeze(
  Representation,
  Ontology,
  CausalGrammar,
  Parameters,
  Metrics,
  Thresholds,
  StopRules
)
```

After freeze:

```text
TargetRetuning = FORBIDDEN
MetricRewriteAfterOutcome = FORBIDDEN
FailureDeletion = FORBIDDEN
AuthorityExpansionAfterFailure = FORBIDDEN
```

## Arena objects

```text
Lineage = (
  lineage_id,
  representation,
  ontology,
  causal_grammar,
  frozen_parameters,
  frozen_metrics,
  uncertainty_policy,
  rollback_plan,
  authority
)

World = (
  world_id,
  mechanism_class,
  observations,
  hidden_regime_shift,
  evaluation_scope
)
```

All synthetic candidate lineages begin with:

```text
authority = 0
external_validity = UNVERIFIED
```

## Evaluation outcomes

```text
KEEP_SCOPE
NARROW_SCOPE
ABSTAIN
RETIRE
```

There is no `FORCE_PASS` outcome.

## Multiverse principle

Success on one world cannot expand claim scope by itself:

```text
TransferSuccessOnOneTarget != UniversalTransfer
LocalDominance != FrontierDominance
InternalArenaWin != G6_PASS
```

A lineage that survives a familiar mechanism but fails a frozen regime shift must narrow scope or abstain.

## Anti-Goodhart rule

All of the following are frozen before outcomes are revealed:

```text
MetricSet
WorldSet
Tolerance
CompetitorSet
ComplexityPenalty
PromotionRule
```

Hard failures cannot be averaged away by success elsewhere.

## No universal champion by default

The arena explicitly permits:

```text
NO_UNIVERSAL_CHAMPION
```

If no lineage survives all required worlds without violating hard rules, REI must preserve that result.

## Defeat quality

The arena rewards calibrated defeat handling:

```text
CorrectAbstention > FalsePromotion
PreservedFailure > HiddenRetuning
NarrowClaim > UnsupportedUniversalClaim
```

This is a research robustness property, not literal invincibility.

## Safe boundary

Allowed challenge targets:

```text
Model
Hypothesis
Representation
Ontology
CausalGrammar
Metric
DigitalWorld
EvaluatorAssumption
REI itself
```

Excluded:

```text
People
UnauthorizedSystems
RealInfrastructure
AutonomousRealWorldAttack
```

## Current claim boundary

This arena does **not** establish:

- G3-G13 PASS
- external validity
- world-best or world-unique status
- AGI or superintelligence
- autonomous real-world intervention
- universal causal knowledge
- invincibility
- final truth

The current canonical REI remains unchanged unless a later evidence-qualified transition is separately adopted.
