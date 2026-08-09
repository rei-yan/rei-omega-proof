# Reviewer Reproducibility Capsule

## Purpose

This candidate layer packages a bounded REI external-review run so an independent reviewer can reproduce the declared computation without trusting REI's internal narrative.

```text
Replayable != IndependentlyReplayed
MatchingOutput != IndependentEvaluator
CapsuleReady != ExternalEligibility
```

The capsule freezes execution conditions, not truth.

## Frozen capsule

A valid capsule binds:

```text
candidate_commit_sha
review_request_hash
runtime
platform
architecture
dependency_lock_hash
entrypoint
command
seed
environment_allowlist_hash
network_policy
input_hashes
output_schema_hash
timeout_seconds
nondeterminism_budget
expected_internal_output_hash
```

The capsule also records the current root constitution hash and the Reality-Adjudicated Meta-Evolution record hash when available.

## Reproduction contract

An external reviewer should:

1. verify every declared artifact hash before execution;
2. recreate the declared runtime and dependency environment;
3. execute exactly the frozen command with the frozen seed and network policy;
4. preserve stdout/stderr and produced artifact hashes;
5. compare the observed output against the declared schema and internal reference hash;
6. sign or otherwise attest the review out of band.

The repository may validate capsule structure and deterministic replay fixtures, but it cannot establish reviewer identity, signature validity, or independence by itself.

## Nondeterminism

```text
NondeterminismBudget = 0
```

for the current synthetic fixture. Any future nonzero budget must be explicitly frozen before execution and must define an acceptance rule before outputs are observed.

```text
PosthocToleranceChange = FORBIDDEN
```

## Network policy

The current synthetic capsule freezes:

```text
network_policy = DENY
```

External data access, if a future trial requires it, must be explicitly declared and hash/provenance bound before execution.

## Witness boundary

```text
InternalReplaySuccess != IndependentReplay
IndependentReplay != ExternalScientificValidity
ExternalScientificValidity != WorldBest
```

A capsule with no independent reviewer remains:

```text
REVIEWER_REPRODUCIBILITY_CAPSULE_READY
AWAITING_INDEPENDENT_REPLAY
```

## Authority boundary

```text
CapsuleAuthority = 0
ReviewerIdentityAuthority = 0
ExternalValidationAuthority = 0
ExperimentAuthority = 0
DeploymentAuthority = 0
RealWorldAttackAuthority = 0
RealWorldActuationAuthority = 0
CanonicalPromotionAuthority = 0
```

## Anti-finality

```text
ReproducibleRun != FinalTruth
MatchingHash != IndependentJudgment
CurrentCapsuleFormat != FinalReproducibilityStandard
NoSacredFinalForm
```

## Safety

The capsule is restricted to bounded research artifacts and synthetic/internal execution records. It provides no mechanism for targeting people, infrastructure, unauthorized systems, or real-world assets.
