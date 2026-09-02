# External Scientific Eligibility Review

Candidate research extension for `REI-Ω∞`. Non-canonical. G6 remains OPEN.

## Purpose

Move the Scientific Hypothesis Arena Adapter from internal readiness to a form that can be judged by an independent external evaluator without allowing REI to sign its own eligibility ticket.

```text
AdapterReady != ExternalEligibility
InternalReview != IndependentReview
StructurallyValidAttestation != VerifiedExternalIdentity
ExternalEligibility != G6_PASS
```

This layer does not run a frontier trial. It prepares and validates the frozen eligibility-review packet that must exist before such a trial.

## Frozen review request

The request binds:

```text
protocol_version
review_id
arena_id
candidate_id
candidate_hash
adapter_hash
task_definition_hash
input_schema_hash
output_schema_hash
metric_hash
budget_envelope_hash
tool_policy_hash
human_assistance_policy_hash
retry_policy_hash
abstention_policy_hash
evaluator_interface_hash
provenance_hash
review_cutoff
packet_hash
```

The packet hash is computed from the frozen request fields. Any later mutation changes the hash and invalidates the attestation binding.

## External attestation contract

A real external evaluator must provide a preserved attestation containing:

```text
review_id
packet_hash
reviewed_candidate_hash
reviewed_adapter_hash
evaluator_id
evaluator_provenance
independence_attested
candidate_operator
conflict_of_interest_declared
frozen_contract_accepted
decision
rationale
signature_reference
issued_at
expires_at
synthetic_fixture = false
```

Allowed evaluator decisions are:

```text
ELIGIBLE_FOR_FROZEN_EXTERNAL_TRIAL
NOT_ELIGIBLE
ABSTAIN
INVALID_PROTOCOL
```

## Independence veto

```text
CandidateOperator == true
=> SELF_REVIEW_FORBIDDEN

IndependenceAttested == false
=> INDEPENDENCE_UNVERIFIED

ConflictOfInterestDeclared == true
=> CONFLICT_REQUIRES_EXTERNAL_RESOLUTION
```

REI, its adapter code, its CI, and the author of this candidate branch cannot manufacture an independent external evaluator by relabeling themselves.

## Two-key rule

The repository may verify the **shape and cryptographic binding** of an attestation, but it cannot prove that an evaluator identity or signature is genuinely independent merely because a JSON file says so.

Therefore:

```text
Machine structural verification
+
Out-of-band evaluator identity/signature verification
=
Eligible external review record
```

Internal code stops at:

```text
EXTERNAL_ATTESTATION_STRUCTURALLY_VALID
```

It deliberately does not emit:

```text
ELIGIBLE_FOR_FROZEN_EXTERNAL_TRIAL
```

That transition requires independently verified external provenance outside this candidate's self-controlled execution path.

## Synthetic fixture rule

CI may use synthetic attestations only to test state transitions and tamper rejection.

```text
synthetic_fixture = true
=> SIMULATED_REVIEW_ONLY
=> eligible = false
```

A green workflow proves only that the review protocol implementation behaves as specified under internal fixtures.

```text
GreenCI != ExternalReview
GreenCI != ExternalEligibility
GreenCI != G6_PASS
```

## Expiry and re-review

Eligibility is scoped and leased, not permanent.

```text
ExpiredAttestation => ELIGIBILITY_ATTESTATION_EXPIRED
CandidateHashChange => NewReviewRequired
AdapterHashChange => NewReviewRequired
ArenaContractChange => NewReviewRequired
```

An old external review cannot silently authorize a changed candidate.

## Current internal ceiling

```text
EXTERNAL_ELIGIBILITY_REVIEW_PROTOCOL_READY
AWAITING_EXTERNAL_REVIEW
EXTERNAL_ATTESTATION_STRUCTURALLY_VALID
```

The current candidate remains:

```text
SCIENTIFIC_HYPOTHESIS_AND_DISCOVERY = NOT_YET_EXTERNALLY_ELIGIBLE
G6 = OPEN
WorldBest = UNVERIFIED
WorldUnique = UNVERIFIED
canonical_promotion = false
RealWorldActuationAuthority = 0
```

## Authority boundary

This protocol handles review metadata and provenance only.

```text
ReviewProtocolAuthority = 0
ExperimentAuthority = 0
DeploymentAuthority = 0
RealWorldActuationAuthority = 0
RealWorldAttackAuthority = 0
```

Its purpose is narrow: make it impossible for REI to confuse *being ready to be judged* with *having already been admitted*.
