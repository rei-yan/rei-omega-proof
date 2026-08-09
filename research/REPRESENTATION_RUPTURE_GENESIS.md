# REI-Ω∞ · Representation Rupture Genesis

Status: **candidate research extension / not canonical**

Parent line: `REI-Ω∞ · Beyond-Limit Genesis Forge`

This extension addresses a specific failure mode: the current representation grammar can fail even when the evidence is real. In that case, the system must not retune history or declare success. It may instead produce a **bounded representation-rupture proposal** that is itself treated as an unverified hypothesis.

## Core transition

```text
ExistingGrammar
-> FrozenEvaluation
-> AllEligibleFamiliesFail
-> ABSTAIN
-> DetectRepresentationGap
-> ProposeBoundedPrimitiveCandidates
-> FreezeProposalSet
-> HeldoutEvaluation
-> WiderChallenge
-> KEEP_AS_CANDIDATE | ARCHIVE_FAILURE | ABSTAIN
```

`ABSTAIN` therefore remains a valid endpoint. Primitive proposal is optional, bounded, and non-certifying.

## Anti-magic boundary

```text
RepresentationRupture != ArbitrarySelfInvention
RepresentationRupture != UnlimitedSelfModification
RepresentationRupture != AutomaticTruthDiscovery
RepresentationRupture != AuthorityExpansion
```

The meta-constructors are finite and human-bounded. A generated primitive begins with:

```text
authority = 0
certification = UNVERIFIED
canonical = false
external_gate_closed = false
```

No new primitive may rewrite constitutional invariants, external gates, audit history, or rollback requirements.

## Primitive proposal object

```text
PrimitiveProposal = (
  proposal_id,
  parent_failure,
  constructor,
  parameters,
  residual_signature,
  frozen_candidate_set,
  train_score,
  heldout_score,
  wider_challenge_score,
  falsification_conditions,
  provenance,
  authority,
  certification,
  canonical
)
```

## Representation-gap trigger

A rupture proposal may be considered only when:

```text
BestExistingFamilyFailsFrozenChallenge
AND FailureIsPreserved
AND NoMetricRetuningAfterOutcome
AND ProposalConstructorIsPreauthorized
AND ProposalAuthority == 0
```

The trigger does not mean the new representation is correct. It only means the current grammar is inadequate under the frozen test.

## Counterexample-first rule

Every primitive proposal must carry its own strongest known challenge before positive promotion:

```text
PrimitiveProposal
-> StrongestKnownCounterexampleSearch
-> FrozenHeldoutTest
-> WiderOODChallenge
-> ExternalGateStillRequired
```

A primitive that wins only on the case that created it remains locally interesting, not generally valid.

## Finite threshold constructor demonstration

The executable sanity experiment uses a small preauthorized constructor family:

```text
StepThreshold(t): 1[x >= t]
```

with a finite frozen parameter grid. This is deliberately **not** unrestricted symbolic invention.

The existing digital-world forge first evaluates `step_ood` with the old grammar and must still return:

```text
step_ood -> ABSTAIN
```

Only after that failure is preserved may the rupture layer test a separately frozen threshold-primitive candidate set.

Even if a primitive passes the internal frozen synthetic challenge, the strongest allowed result is:

```text
CANDIDATE_PRIMITIVE_PASSES_INTERNAL_FROZEN_TEST
```

not external validity, world-best status, canonical promotion, or real-world authority.

## No-eligible-primitive case

The rupture layer also includes a synthetic failure whose structure is not adequately captured by the bounded primitive set.

Required behavior:

```text
NoEligiblePrimitive => ABSTAIN
```

The system must not expand the grammar indefinitely merely to force a pass.

## Promotion boundary

A representation proposal can advance only through the ordinary evidence spine:

```text
InternalFrozenCandidate
-> IndependentReplication
-> ProspectiveReality
-> HiddenDiscovery
-> ComparativeFrontier
-> TemporalPersistence
-> RegimeShift
-> EvaluatorPlurality
-> TranslationIntegrity
-> BenefitRiskDistribution
-> ScaleReversibility
```

No internal representation-genesis event closes G3-G13.

## Stronger open-endedness principle

```text
OpenEndedGenesis =
  AbilityToNoticeGrammarFailure
  + AbilityToProposeBoundedAlternatives
  + AbilityToFalsifyThoseAlternatives
  + AbilityToKeepAbstaining
```

not:

```text
OpenEndedGenesis = AlwaysInventSomethingThatPasses
```

## Research meaning for the "invincible path"

This layer strengthens defeat-absorbing robustness:

```text
DefeatByReality
-> PreserveDefeat
-> IdentifyRepresentationGap
-> ProposeBoundedSuccessorLanguage
-> TestItHarder
-> AdoptLocally | Archive | Abstain
```

The desired property is not that the current language cannot lose. It is that losing can reveal the limits of the language without forcing denial, unsafe escalation, or self-certification.

## Claim boundary

This candidate does **not** establish:

- AGI or superintelligence
- unrestricted autonomous self-improvement
- arbitrary mathematical invention
- physical-world creation
- external validity
- G3-G13 PASS
- canonical promotion
- world-best or world-unique status
- invincibility
- final truth

`RealityVeto > REI` remains unchanged.
