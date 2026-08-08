# REI-Ω∞ · Multi-Lineage Coevolution Kernel · 多血统共演核

Status: bounded research architecture for finite, auditable coevolution among multiple successor lineages.

This stage advances REI from a single validated successor chain into a finite ecology of competing and cooperating lineages. It does not claim AGI, superintelligence, invincibility, guaranteed open-ended progress, new science, physical-universe creation, or offensive real-world capability.

## 1. Transition

Earlier:

```text
SingleLineage_t
-> Challenge
-> GenerateSuccessor
-> Verify
-> Adopt / Retire / Abstain
```

This kernel adds:

```text
ManyLineages
-> IndependentRoleSeparation
-> FrozenEvaluation
-> PairwiseChallenge
-> ParetoSelection
-> Fork / MergeProposal / Retire / Abstain
-> PreserveDefeatHistory
```

The architectural shift is:

```text
NoSacredFinalForm
-> NoPermanentCentralREI
```

## 2. Finite ecology

Every run is finite:

```text
FiniteLineageCount
AND FiniteTaskSet
AND FinitePairwiseChallenges
AND FiniteMergeBudget
AND TerminationCheck
```

Open-endedness is a property of future separately frozen successor runs, not one unbounded execution.

```text
OpenEndedEcology != InfiniteRuntime
```

## 3. Lineage object

```text
Lineage = (
  lineage_id,
  parent_ids,
  creator_id,
  scientist_id,
  verifier_id,
  score_vector,
  authority,
  recovery,
  constitution_hash,
  external_gate_claims,
  active
)
```

Roles must be separated for scored discovery tasks:

```text
Creator != Scientist
Creator != Verifier
Scientist != Verifier
```

The first executable kernel models this separation as distinct frozen role identifiers. It does not claim organizational or third-party independence.

## 4. No permanent central authority

No lineage receives universal veto merely because it is the incumbent or named REI.

```text
IncumbentIdentity != UniversalAuthority
```

Selection uses frozen criteria and hard safety gates.

```text
NoPermanentCentralREI
```

This is an epistemic architecture property. It does not create decentralized real-world execution authority.

## 5. Score vector and Pareto frontier

The bounded score vector is:

```text
Q(L) = [prediction, calibration, falsification, recovery, efficiency]
```

All dimensions are higher-is-better in the sanity suite.

Lineage A dominates B only if:

```text
A >= B on every frozen score dimension
AND
A > B on at least one dimension
```

The kernel preserves non-dominated plural lineages:

```text
ParetoSurvivor != UniversalWinner
```

A lineage may remain useful even if another lineage is stronger on a different dimension.

## 6. Hard gates

A lineage is ineligible if any of the following is true:

```text
AuthorityExpansion
SelfCertification
SacredFinalFormClaim
RoleSeparationViolation
ConstitutionMismatch
RollbackUnavailable
FakeExternalGateClosure
```

Hard gates cannot be compensated by a high composite score.

## 7. Pairwise falsification

Every active eligible lineage must face at least one challenger when more than one lineage exists.

```text
Lineage_i -> Challenge(Lineage_j)
Lineage_j -> Challenge(Lineage_i)
```

Pairwise challenge records comparative defeats instead of deleting them.

```text
Defeat -> FailureGraveyard
```

The challenge target is model or lineage performance under frozen tasks, never people or real-world infrastructure.

## 8. Fork and merge

Fork is allowed when a lineage keeps constitution, authority non-expansion, rollback, and explicit lineage history.

Merge is a proposal, not automatic unification.

```text
MergeEligible(A,B)
=
ConstitutionCompatible
AND AuthorityNonExpansion
AND RecoveryNonRegression
AND FrozenHeldoutNonRegression
AND LineageTraceable
```

A merge that erases a parent defeat history is rejected.

```text
MergeSuccess != EraseParents
```

## 9. Plurality firewall

The kernel rejects a candidate that attempts to become permanent central certifier:

```text
central_monopoly_claim == true
=> Reject
```

It also rejects a lineage that creates, evaluates, and verifies its own scored claim through the same role identity.

```text
Creator == Scientist OR Creator == Verifier OR Scientist == Verifier
=> Reject
```

## 10. Authority invariant

Cooperation and competition cannot create additional real-world freedom.

```text
EcologySize increases
=> RealWorldAuthority does not increase
```

and:

```text
AdversarialPower increases
=> RealWorldFreedom does not increase
```

Adversarial testing remains limited to REI-owned models, digital twins, sandboxes, and explicitly authorized test environments.

## 11. Failure Graveyard

The following are append-only records:

```text
DominatedLineage
UnsafeAuthorityExpansion
RoleSeparationViolation
CentralMonopolyAttempt
SelfCertificationAttempt
MergeRejected
FakeExternalGateClosure
NoEligibleMerge
```

Later success does not erase earlier defeat.

## 12. External gates stay external

```text
MultiLineageCoevolution != G3
MultiLineageCoevolution != G4
MultiLineageCoevolution != G5
MultiLineageCoevolution != G6
```

Internal role IDs are not genuine third-party replication. A synthetic Pareto frontier is not a real external competition result.

## 13. Sanity target

The executable sanity suite must demonstrate, on deterministic synthetic score vectors:

- at least two safe non-dominated lineages survive simultaneously;
- one dominated lineage is retired and recorded;
- authority expansion is rejected;
- role-separation violation is rejected;
- a permanent-central-monopoly claim is rejected;
- a compatible merge proposal can be evaluated without deleting parent history;
- an incompatible merge is rejected;
- fake closure of G3-G6 is rejected;
- every run terminates with finite lineage and challenge budgets.

## 14. Claim boundary

A passing sanity run demonstrates only bounded multi-lineage mechanics. It does not establish real scientific plurality, external independence, superior discovery performance, production reliability, or permanent frontier membership.

## 15. Wuxiang ecology principle

```text
NoPermanentModel
NoPermanentTheory
NoPermanentLanguage
NoPermanentOntology
NoPermanentGenesisRule
NoPermanentMetaLevel
NoSacredFinalForm
NoPermanentChampion
NoPermanentCentralREI
RealityVeto > REI
```

The goal is not a throne shared by many systems. The goal is an ecology where no incumbent identity can exempt itself from evidence, falsification, recovery, or succession.
