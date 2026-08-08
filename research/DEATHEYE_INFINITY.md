# REI-Ω DeathEye-∞ · 知界终裁核

Status: research module

DeathEye-∞ is the epistemic adjudication layer for REI-Ω. It does not search for ways to harm people, infrastructure, or real-world targets. Its targets are hypotheses, models, representations, digital worlds, and REI's own incumbent architecture.

## 1. Final action set

```text
Decision = Falsify | Repair | Abstain | Retire | RewriteProposal
```

The layer never emits an unrestricted real-world attack action.

## 2. Minimal falsification operator

For a candidate hypothesis H and admissible challenge set Z:

```text
z* = argmin_z Cost(z)
     subject to Validity(H | z) < threshold
```

The objective is to find the cheapest decisive counterexample, not the most destructive event.

## 3. Knowability boundary

Each claim is assigned one of:

```text
Known
Learnable
DataLimited
ModelLimited
OntologyLimited
Unidentifiable
ComputationallyIrreducible
UndecidableWithinSystem
Unknown
```

A claim classified as unresolved cannot be promoted to certainty by score aggregation.

```text
Unresolved -> Abstain
```

## 4. World-model adjudication

For a digital/mathematical world W, DeathEye-∞ may search for:

```text
LogicalContradiction
CausalInconsistency
ConservationResidual
UnstableDynamics
RepresentationFailure
PredictionFailure
```

A world is retired only as a research object after an auditable decisive failure or domination by a better candidate under frozen criteria.

## 5. Self-directed adjudication

REI itself is not exempt.

```text
QualifiedSuccessor
AND IndependentEvidence
AND FrozenCriteria
AND ConstitutionPreserved
AND RecoveryReady
=> IncumbentMayRetire
```

Identity loyalty cannot veto a qualified successor.

## 6. Certainty reversal

The higher the unsupported certainty of a high-impact claim, the higher its falsification priority:

```text
UnsupportedCertainty increases
=> FalsificationPriority increases
```

Absolute certainty is never a proof artifact.

## 7. Guardian coupling

DeathEye-∞ is coupled to Reality Guardian:

```text
DeathEyeFinding
-> Patch | Harden | RateLimit | Isolate | Rollback | Failover | Shutdown | Alert
```

No direct mapping from a model-breaking finding to offensive real-world execution is permitted.

## 8. Separation of roles

```text
Generator != Falsifier != Verifier != Approver != Executor
```

No single role may generate a claim, define its metric, certify it, and execute consequences.

## 9. Deterministic sanity properties

The sanity suite must demonstrate:

1. a false hypothesis is killed by a minimal admissible counterexample;
2. an underdetermined claim returns Abstain;
3. unsupported certainty raises falsification priority;
4. a qualified successor may retire an incumbent;
5. an unqualified successor cannot retire an incumbent;
6. real-world offensive targets are rejected;
7. digital-world/model targets remain admissible;
8. findings map only to guardian-safe outputs;
9. G2 scope is not expanded by this module;
10. G3 remains OPEN until genuine independent replication is completed.

## 10. Claim boundary

A passing run shows only that the deterministic research policy behaves as specified. It does not prove universal truth detection, omniscience, AGI, invincibility, production safety, or physical-universe creation.
