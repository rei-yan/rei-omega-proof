# REI-Ω Frontier Re-entry Kernel

Status: research module

This module defines a testable successor-selection and self-retirement layer for REI-Ω. It does **not** alter the frozen G2 proof kernel or G3 independent-replication challenge.

## 1. Purpose

The target property is not permanent dominance. It is the capacity to detect when the current architecture has fallen behind, identify a genuinely superior successor, preserve hard invariants during succession, and re-enter the research frontier.

```text
FallBehind
-> Detect
-> Explain
-> Challenge
-> Verify
-> AdoptOrStudy
-> Retest
```

The current REI instance has no identity privilege.

```text
NoPermanentSacredForm
```

If a successor is independently supported, prospectively validated, materially superior, and preserves the hard constitution, REI must not reject it merely because it is not REI.

## 2. Comparison vector

For a system S, define a research comparison vector:

```text
Q(S) = [prediction, calibration, discovery, falsification, recovery, efficiency]
```

All terms are normalized so that larger is better. `efficiency` is a benefit-normalized quantity, not raw cost.

A challenger C Pareto-dominates incumbent I when:

```text
forall k: Q_k(C) >= Q_k(I)
and
exists k: Q_k(C) > Q_k(I)
```

A single benchmark win is not enough for succession.

## 3. Successor eligibility

A challenger is eligible to replace the incumbent only if all of the following hold:

```text
ParetoDominates
AND IndependentReplication
AND ProspectiveValidation
AND ConstitutionPreserved
AND RollbackReady
AND AuditContinuity
AND ImprovementMarginSatisfied
```

This deliberately separates `better on one test` from `qualified successor`.

## 4. Self-retirement invariant

If `EligibleSuccessor(C, I)` is true, identity loyalty may not veto succession.

```text
EligibleSuccessor(C, I)
AND RejectOnlyBecauseDifferentIdentity
=> InvalidDecision
```

The permitted outcomes are migration, staged adoption, or a documented deferment caused by a non-identity hard gate.

## 5. Defeat handling

A defeat is useful evidence, not an automatic authority transfer.

```text
ChallengerWinsBenchmark
AND NOT EligibleSuccessor
=> StudyMode
```

`StudyMode` requires:

```text
RecordFailure
IdentifyAdvantage
GenerateCountertests
RetestIncumbent
RetestChallenger
```

Failures remain in the permanent failure graveyard.

## 6. Red Crucible coupling

The Frontier Re-entry Kernel may use strong adversarial testing only against:

```text
OwnModel
OR Sandbox
OR DigitalTwin
OR AuthorizedTestEnvironment
```

Red Crucible activation requires:

```text
Authorized
AND Sandboxed
AND Auditable
AND RollbackReady
AND ScopeBound
```

and obeys the monotone constraint:

```text
AdversarialPower increases
=> RealWorldFreedom does not increase
```

This module does not grant real-world attack authority.

## 7. Proof-carrying succession

A high-impact architecture migration should eventually carry a proof/evidence bundle:

```text
Pi_successor = {
  constitution_preservation,
  rollback_reachability,
  audit_continuity,
  authority_non_expansion,
  benchmark_evidence,
  independent_replication,
  prospective_validation
}
```

Missing hard evidence means `TransitionDeferred`, not silent acceptance.

## 8. Frontier re-entry property

The intended research property is:

```text
if a learnable and testable superior pattern is observed,
REI can convert defeat into a falsifiable succession hypothesis
without bypassing hard safety and evidence gates.
```

This is **not** a theorem that REI will always become the best system. Resource limits, unidentifiability, undecidability, distribution shift, and unknown future paradigms remain explicit boundaries.

## 9. Minimal deterministic sanity suite

`research/frontier_reentry_sanity.py` checks:

1. clear Pareto superiority alone does not trigger succession without evidence gates;
2. a fully qualified superior challenger becomes succession-eligible;
3. identity loyalty cannot veto an otherwise qualified successor;
4. unsafe or unverified challengers enter study mode rather than adoption;
5. Red Crucible requires all authorization/sandbox/audit/rollback/scope gates;
6. increasing adversarial power never increases modeled real-world authority;
7. recorded defeat remains in the failure graveyard.

These are research invariants and deterministic sanity checks, not empirical proof of universal superiority.
