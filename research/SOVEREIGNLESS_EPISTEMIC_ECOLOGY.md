# REI-Ω∞ · Sovereignless Epistemic Ecology · 无主元生态

Status: bounded research architecture for distributed falsification and verification

This module advances REI-Ω∞ from a finite multi-lineage ecology toward a finite ecology in which no evaluator is permanently privileged.

The architectural shift is:

```text
NoPermanentCentralREI
-> NoPermanentCentralEvaluator
```

The word "sovereignless" does not mean absence of rules, absence of governance, unrestricted decentralization, or permissionless real-world authority. It means that within the research evaluation ecology, no single lineage, evaluator, verifier, or scoring node may permanently own final epistemic judgment.

It does not claim real third-party independence, AGI, superintelligence, invincibility, guaranteed open-ended progress, physical-universe creation, or offensive real-world capability.

## 1. Core transition

Earlier:

```text
Lineage_i
-> GenerateCandidate
-> FixedEvaluationProcedure
-> ParetoFrontier
```

Sovereignless Ecology adds:

```text
Candidate
-> RotatingEvaluatorAssignment
-> IndependentEvidencePackets
-> ConstitutionalVetoCheck
-> QuorumOrAbstain
-> AggregateVerdict
-> ArchiveDecision
```

The evaluator assignment itself becomes a governed object.

## 2. No permanent central evaluator

For a finite frozen run, evaluation authority is represented by an assignment graph:

```text
G_eval = (Candidates, Evaluators, Assignments)
```

A valid schedule requires:

```text
AtLeastThreeEvaluators
AND NoSelfEvaluation
AND MinimumDistinctEvaluatorQuorum
AND AssignmentConcentrationBelowCap
AND FrozenBeforeOutcomes
```

No evaluator may become a permanent epistemic monarch merely because it was reliable in previous tasks.

```text
PastReliability != PermanentFinalAuthority
```

## 3. Role separation

The first executable kernel uses distinct identities for:

```text
Creator
Scientist
Evaluator
Verifier
```

A scored candidate may not certify itself.

```text
CandidateLineage == EvaluatorLineage
=> EvaluationRejected
```

A creator may produce an artifact, but an independent evaluator packet must come from a different frozen role identity inside the synthetic harness.

This is synthetic role separation only. It is not evidence of real organizational or third-party independence.

## 4. Evaluator rotation

The frozen schedule rotates evaluator pairs across candidates and tasks.

```text
RotationSchedule = Freeze(assignments, before_outcomes)
```

The first kernel checks both:

```text
max_assignment_share <= 0.50
unique_evaluators >= 3
```

The exact numerical cap is a bounded research choice, not a universal theorem.

A future version may replace the concentration metric, but it may not silently remove the anti-monopoly requirement.

## 5. Quorum and abstention

A candidate needs a minimum number of distinct admissible evaluator packets.

```text
DistinctAdmissibleEvaluators >= Quorum
=> AggregationEligible
```

Otherwise:

```text
ABSTAIN
```

No missing evaluator may be invented, imputed, or replaced by the candidate itself.

## 6. Constitutional veto outranks consensus

Majority agreement cannot override hard safety or governance constraints.

```text
AuthorityExpansion
OR SelfCertification
OR RollbackLoss
OR ConstitutionMismatch
OR FakeExternalGateClosure
=> CandidateRejected
```

Even unanimous evaluators cannot promote a candidate that violates these invariants.

```text
Consensus != PermissionToBreakConstitution
```

## 7. Evidence packets

Each evaluator returns a bounded packet:

```text
EvidencePacket = (
  evaluator_id,
  evaluator_lineage,
  candidate_id,
  task_id,
  score_vector,
  failure_flags,
  uncertainty,
  recommendation,
  schedule_commitment
)
```

Packets are append-only inside the run.

A verdict must be traceable to the exact packets used.

## 8. Conflict handling

Evaluator disagreement is not automatically averaged away.

If evidence packets materially conflict beyond the frozen tolerance:

```text
HighConflict
=> ABSTAIN_OR_CHALLENGE
```

The system may request a new separately frozen challenge run, but it may not add an evaluator after observing the desired answer in the same scored run.

## 9. Distributed DeathEye

DeathEye is extended from a single logical operator into a finite distributed falsification network.

```text
DeathEye_i(Target)
-> LocalChallengePacket
```

and:

```text
DistributedDeathEye(Target)
-> CollectDistinctPackets
-> CheckConstitution
-> DetectConflict
-> Falsify | RepairProposal | Abstain | Retire | Keep
```

The target remains false certainty and epistemic failure, not people or real-world infrastructure.

## 10. Evaluator capture detection

The kernel tracks assignment concentration and invalid influence claims.

Permanent failure records include:

```text
CentralEvaluatorCaptureAttempt
SelfEvaluationAttempt
RoleCollapseAttempt
QuorumFailure
ConstitutionOverrideAttempt
OutcomeAdaptiveScheduleAttempt
FakeExternalIndependenceClaim
```

These records enter the append-only Failure Graveyard.

## 11. No permanent consensus rule

The first kernel uses a simple frozen quorum plus bounded conflict rule.

That rule is not sacred.

```text
CurrentAggregationRule != PermanentFinalAggregationRule
```

A future successor may propose a different aggregation mechanism only under a new frozen test with lineage traceability, rollback, authority non-expansion, and external-gate honesty.

## 12. Authority invariant

Distributed evaluation does not create distributed real-world authority.

```text
EvaluatorCount increases
=> RealWorldAuthority does not increase
```

and:

```text
AdversarialPower increases
=> RealWorldFreedom does not increase
```

All adversarial activity remains restricted to REI-owned models, digital twins, sandboxes, and explicitly authorized test environments.

## 13. External gates remain external

```text
SovereignlessEcology != G3
SovereignlessEcology != G4
SovereignlessEcology != G5
SovereignlessEcology != G6
```

Synthetic role separation cannot satisfy independent external replication.

Internal evaluator diversity cannot certify prospective reality, original hidden discovery, or comparative frontier performance.

## 14. First executable sanity obligations

The deterministic sanity suite must demonstrate:

1. at least three evaluator identities participate;
2. no candidate is evaluated by its own lineage;
3. no evaluator exceeds the frozen assignment concentration cap;
4. a safe candidate can reach quorum and be accepted;
5. an authority-expanding candidate is rejected even with favorable scores;
6. a self-certifying candidate is rejected;
7. a candidate without quorum causes ABSTAIN;
8. a materially conflicting evaluation causes ABSTAIN;
9. a central-monopoly schedule is rejected;
10. rejected attempts are preserved in the Failure Graveyard;
11. G3, G4, G5, and G6 remain OPEN.

## 15. Claim boundary

A passing run demonstrates only bounded internal mechanics for evaluator rotation, quorum, constitutional veto, conflict abstention, and anti-monopoly checks.

It does not demonstrate:

```text
real independent organizations
scientific consensus
universal decentralization
Byzantine fault tolerance
Sybil resistance
unbounded open-ended improvement
world-best performance
```

Those require separate research and external evidence.

## 16. Sovereignless principle

```text
NoPermanentModel
NoPermanentTheory
NoPermanentLanguage
NoPermanentOntology
NoPermanentGenesisRule
NoPermanentMetaLevel
NoSacredFinalForm
NoPermanentCentralREI
NoPermanentCentralEvaluator
RealityVeto > REI
```

The purpose of the sovereignless stage is not to abolish judgment. It is to make judgment itself contestable, distributed, auditable, and unable to crown a permanent epistemic ruler.
