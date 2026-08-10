# REI-Ω∞ Frontier Arena Eligibility Contract

Status: candidate research extension; non-canonical; G6 remains OPEN.

## Purpose

Prevent conceptual adjacency from being misreported as benchmark eligibility.

```text
HasRelatedModule != EligibleCompetitor
InternalPrototype != ExternalBenchmarkParticipant
ProofConsumer != GeneralTheoremProver
WorldCandidateGenerator != InteractiveWorldModel
CausalGrammar != CausalDiscoveryMethod
```

Before any candidate, including REI, enters a comparative arena, it must satisfy the same frozen eligibility contract.

## Eligibility contract

```text
ArenaEligibility =
  FrozenTaskDefinition
  AND FrozenInputSchema
  AND FrozenOutputSchema
  AND FrozenMetric
  AND FrozenBudgetEnvelope
  AND FrozenToolPolicy
  AND FrozenHumanAssistancePolicy
  AND FrozenRetryPolicy
  AND FrozenAbstentionPolicy
  AND ReproducibleExecutionIdentity
  AND ExternalEvaluatorCompatibility
```

If any required field is missing:

```text
NOT_ELIGIBLE
```

No architecture may receive a score for a task it was not eligible to enter.

## Current REI eligibility verdicts

These are intentionally conservative.

### SCIENTIFIC_HYPOTHESIS_AND_DISCOVERY

Current REI state: `NOT_YET_ELIGIBLE`.

Reason: the Discovery Genesis stack can generate candidate questions, measurements and hypotheses in bounded internal crucibles, but an external hypothesis/discovery arena requires a frozen external task interface, source-access policy, submission format, budget envelope, hidden evidence procedure and independent scoring contract.

### ALGORITHM_DISCOVERY_AND_EVOLUTION

Current REI state: `NOT_ELIGIBLE`.

Reason: REI does not currently expose a frozen general-purpose program-evolution interface comparable to an executable-evaluator algorithm discovery system.

### WORLD_MODEL_AND_INTERACTIVE_SIMULATION

Current REI state: `NOT_ELIGIBLE`.

Reason: REI's WorldCandidate and synthetic digital-world machinery are research representations, not a real-time interactive generative world model with comparable visual, temporal and control outputs.

### FORMAL_THEOREM_PROVING

Current REI state: `NOT_ELIGIBLE_AS_GENERAL_PROVER`.

Reason: G2 proves a scoped encoded invariant kernel. This is evidence about REI's own critical execution-gate invariants, not evidence that REI is a general automated theorem prover on external Lean formalization tasks.

### CAUSAL_DISCOVERY

Current REI state: `NOT_YET_ELIGIBLE`.

Reason: causal-grammar generation and synthetic intervention discrimination do not automatically implement a benchmark-compatible causal graph discovery method over frozen external datasets.

## Challenger symmetry

The same rule applies to external challengers.

```text
FamousSystem != EligibleForEveryArena
StrongInDomainA != CompetitorInDomainB
```

For example, a world model is not automatically admitted to a theorem-proving arena, and an algorithm-evolution system is not automatically admitted to a biomedical hypothesis arena.

## Adapter rule

An adapter may translate a system into an arena interface only if frozen before hidden evaluation.

```text
Adapter = (
  adapter_id,
  source_system_version,
  arena_id,
  input_mapping,
  output_mapping,
  tool_mapping,
  budget_mapping,
  abstention_mapping,
  evaluator_mapping,
  adapter_hash
)
```

Forbidden:

```text
AdapterRetunedAfterHiddenReveal => INVALID_PROTOCOL
DifferentAdaptersForWinnerSelection => INVALID_PROTOCOL
HiddenTaskSpecificPromptingAfterFreeze => INVALID_PROTOCOL
UncountedHumanAssistance => INVALID_PROTOCOL
UncountedToolAccess => INVALID_PROTOCOL
```

## Eligibility outcomes

```text
ELIGIBLE
NOT_YET_ELIGIBLE
NOT_ELIGIBLE
ELIGIBILITY_EXPIRED
INVALID_ELIGIBILITY_PROTOCOL
```

Eligibility is scoped and time-bounded. It is not a capability certificate outside the named arena.

## Anti-overclaim

```text
Eligible != Best
BestInArena != BestInWorld
NotEligible != Weak
NotComparable != Inferior
```

A system may be extremely capable and still be legitimately non-comparable under a particular protocol.

## Internal ceiling

```text
FRONTIER_ARENA_ELIGIBILITY_CONTRACT_READY
REI_AllFiveInitialArenaPartitions = NOT_FROZEN_ELIGIBLE
G6 = OPEN
WorldBest = UNVERIFIED
WorldUnique = UNVERIFIED
canonical_promotion = false
RealWorldActuationAuthority = 0
```

The purpose is to make unfair victory harder, including victory obtained by smuggling an architecture into a benchmark through an unfrozen adapter or by treating a neighboring capability as if it were the benchmarked capability itself.
