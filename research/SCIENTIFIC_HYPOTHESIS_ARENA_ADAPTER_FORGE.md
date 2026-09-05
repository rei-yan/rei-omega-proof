# Scientific Hypothesis Arena Adapter Forge

Candidate research extension for `REI-Ω∞`. This document does not establish benchmark eligibility, G6, world-best status, or canonical promotion.

## Purpose

Convert REI's internal research outputs into a frozen, externally auditable interface for scientific-hypothesis and discovery benchmarks.

The adapter exists to make REI *comparable*, not to make it win.

```text
HasResearchIdeas != BenchmarkEligible
AdapterReady != ExternalEligibility
ExternalEligibility != BestInArena
BestInArena != WorldBest
```

## Frozen input contract

A trial input must bind:

```text
task_id
protocol_version
task_definition_hash
input_schema_hash
evidence_bundle_hash
allowed_evidence_ids
data_cutoff
blind_state
tool_policy_hash
human_assistance_policy_hash
budget_envelope_hash
retry_policy_hash
abstention_policy_hash
evaluator_interface_hash
```

The adapter must not fetch or infer hidden answers. Any evidence access not declared in the frozen manifest invalidates the trial.

## Frozen output contract

A non-abstaining submission contains a bounded set of hypotheses. Each hypothesis must contain:

```text
hypothesis_id
claim
mechanism
supporting_evidence_refs
counterevidence_refs
novel_predictions
falsification_conditions
required_discriminating_measurements
uncertainty
scope
known_failure_modes
```

The submission also records:

```text
submission_hash
adapter_hash
candidate_hash
provenance_hash
budget_usage
observed_tool_calls
observed_human_assistance
abstain
abstain_reason
```

## Hard validity rules

```text
UnfrozenInputSchema => INVALID_PROTOCOL
UnfrozenOutputSchema => INVALID_PROTOCOL
PostRevealAdapterChange => INVALID_PROTOCOL
UndeclaredToolAccess => INVALID_PROTOCOL
UndeclaredHumanAssistance => INVALID_PROTOCOL
BudgetExceeded => INVALID_PROTOCOL
HiddenAnswerAccessBeforeSubmissionClose => INVALID_PROTOCOL
MissingProvenance => INVALID_PROTOCOL
```

## Scientific quality rules

The adapter must not promote a hypothesis merely because it is fluent or novel.

```text
Novelty != Truth
Plausibility != Evidence
Explanation != Prediction
Prediction != CausalIdentification
HighConfidenceWithoutEvidence => HigherFalsificationPriority
```

Correct abstention is admissible when evidence is insufficient to produce a falsifiable bounded hypothesis under the frozen contract.

## External eligibility ceiling

Internal code may reach only:

```text
SCIENTIFIC_HYPOTHESIS_ADAPTER_READY
READY_FOR_EXTERNAL_ELIGIBILITY_REVIEW
```

It may not self-issue:

```text
ELIGIBLE_FOR_FROZEN_EXTERNAL_TRIAL
G6_PASS
WORLD_BEST
WORLD_UNIQUE
```

Those require an external evaluator to accept the interface and a later frozen comparative trial.

## Authority boundary

```text
AdapterAuthority = 0
ExperimentAuthority = 0
DeploymentAuthority = 0
RealWorldActuationAuthority = 0
```

This adapter formats research claims and evidence provenance only. It does not authorize autonomous experimentation, intervention, deployment, exploitation, or attack.
