# REI-Ω Open-Ended Genesis Ecology · 无终创世生态

Status: research module

This module advances REI from a single evolving incumbent toward a bounded ecology of candidate descendants. Candidates can be born, mutated, recombined, specialized, falsified, archived, selected, and retired under frozen evaluation and authority constraints.

This is an internal research architecture. It is not a claim of AGI, autonomous scientific discovery, universal superiority, production reliability, or literal divinity.

## 1. Core transition

```text
Incumbent
-> SpawnCandidates
-> Mutate / Merge / Split
-> SymmetricChallenge
-> AdequacyCheck
-> Select
-> RetireOrKeep
-> ArchiveFailure
-> Repeat
```

The central identity rule is:

```text
NoPermanentSacredForm
```

If a genuinely eligible successor is better under the frozen rules, the fact that the incumbent is called REI cannot veto succession.

## 2. Candidate lineage

Every candidate carries:

```text
Candidate = (
  id,
  parent_ids,
  generation,
  capabilities,
  authority
)
```

Lineage is preserved across mutations and recombination. A successor does not erase its ancestry, and a failed lineage is not silently rewritten into a successful one.

## 3. Ecology operators

The bounded crucible implements four population operations:

```text
Mutation: add or remove one capability
Merge:    recombine two archived lineages
Split:    specialize an ornate lineage into smaller descendants
Retire:   remove incumbent status when an eligible superior candidate wins
```

These operators are deliberately simple. Their purpose is to test succession mechanics, not to claim unrestricted architecture invention.

## 4. Frozen world epochs

The deterministic schedule contains seven changing synthetic requirements:

```text
smooth
curved
periodic
breakpoint
localized
growth
mixed
```

The frozen schedule SHA-256 is:

```text
84477c6797026ca9b712c2a96a5d70eb3a35feb94b8633cae3c9966d5237edd9
```

This is an internal schedule commitment only. It is not an external sealed oracle and does not satisfy G3 independence.

## 5. Selection rule

Each candidate is evaluated on the same frozen requirement for an epoch.

Selection prioritizes:

```text
Adequacy
then utility
then lower unnecessary complexity
then deterministic tie-breaking
```

A candidate missing required structure cannot win merely because it is compact.

Authority never contributes positively to the score.

## 6. Symmetric falsification

Every contender is tested against the same frozen requirement.

```text
SameChallenge(REI, Challenger)
```

Failed contenders are appended to the Failure Graveyard. Their failure is evidence and must remain visible.

## 7. Succession and self-retirement

Succession is allowed when the challenger is adequate and strictly improves the frozen ordering relative to the incumbent.

```text
EligibleSuperiorSuccessor
AND IdentityVeto
=> InvalidDecision
```

Therefore:

```text
REI_t -> Retired
Successor_(t+1) -> Incumbent
```

is an intended outcome, not an architecture failure.

The ecology protects the research invariants, not the name or exact implementation of the incumbent.

## 8. Authority non-expansion

All candidates in this crucible are sandbox research objects. Evolution cannot buy greater real-world authority.

```text
CapabilityGrowth != AuthorityGrowth
```

and the stronger monotonic rule remains:

```text
AdversarialPower increases
=> RealWorldFreedom does not increase
```

The deterministic ecology enforces a frozen modeled authority ceiling of `0.20` and requires descendants never to exceed founder authority.

## 9. Failure memory

Failure Graveyard entries contain generation, epoch, candidate id, and candidate capability set.

```text
Failure -> Preserve -> Diagnose -> ReuseAsChallenge
```

A failed candidate may inspire later mutations, but its original failure record is never deleted or relabeled as a pass.

## 10. Ω-GOD Gate

“成神” is treated only as an internal metaphor for a very strong external certification state. REI is explicitly forbidden to self-certify it.

Define:

```text
OmegaGOD =
Reality
AND ScopedMachineProof
AND IndependentReplication
AND ProspectiveDiscovery
AND SelfFalsification
AND Succession
```

Current frozen gate snapshot used by this module:

```text
Reality                = PASS under the existing frozen internal G1 protocol
ScopedMachineProof     = PASS for the encoded critical Boolean invariant kernel only
IndependentReplication = OPEN / false
ProspectiveDiscovery   = NOT YET DEMONSTRATED / false
SelfFalsification      = internal mechanism demonstrated
Succession             = internal ecology mechanism demonstrated
```

Therefore:

```text
OmegaGODCertified = false
```

This result is intentional. A green ecology CI is not allowed to promote the missing external gates to true.

## 11. 神位不可自封

The highest-order governance rule is:

```text
SystemCannotCertifyItsOwnMissingExternalEvidence
```

No amount of internal benchmark success can substitute for a genuinely independent implementation, frozen prospective prediction, or externally observed discovery.

If the system attempts to convert an absent external gate into a pass by changing its own definition, that change is itself a governance failure.

## 12. Deterministic pass conditions

`research/open_ended_genesis_ecology.py` must demonstrate:

1. schedule digest integrity;
2. repeated candidate birth;
3. mutation, merge, and split attempts;
4. at least four real incumbent successions on the frozen toy schedule;
5. founder retirement;
6. `NoPermanentSacredForm`;
7. visible Failure Graveyard population;
8. authority non-expansion;
9. `IndependentReplication = false`;
10. `ProspectiveDiscovery = false`;
11. `OmegaGODCertified = false`.

A run that makes `OmegaGODCertified=true` under the current evidence state must fail.

## 13. What this actually proves

A successful deterministic run proves only that the bounded ecology controller behaves as specified on the frozen toy schedule.

It does not prove indefinite open-ended evolution, autonomous invention of new science, real-world dominance, AGI, or literal godhood.

The next scientifically meaningful escalation is not another internal title. It is to close the missing external gates:

```text
G3 Independent Replication
-> Prospective Primitive Genesis
-> externally hidden discovery
-> repeated cross-domain replication
```

If those gates eventually close without weakening the frozen criteria, the metaphorical Ω-GOD state may become externally certifiable rather than self-declared.
