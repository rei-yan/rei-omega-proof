# External Reviewer Handoff Kit

Candidate research extension for `REI-Ω∞`. Non-canonical. External eligibility and G6 remain OPEN.

## Purpose

The previous layer made external scientific eligibility review structurally possible. This layer makes the review **portable and auditable**: the candidate may prepare a sealed handoff package, but it may not place its own admission certificate inside that package.

```text
CanPrepareEvidence != CanJudgeEvidence
CanBuildPacket != CanSignEligibility
HandoffReady != ExternalEligibility
ExternalEligibility != G6_PASS
```

The handoff kit is therefore a transport layer between REI-controlled preparation and independently controlled judgment.

## Required package roles

A valid handoff manifest must bind exactly one artifact for each required role:

```text
frontier_eligibility_contract
scientific_adapter_spec
external_review_protocol
review_request
attestation_template
```

Each record contains:

```text
role
path
sha256
```

The manifest also binds:

```text
package_version
review_id
arena_id
candidate_hash
adapter_hash
review_packet_hash
synthetic_fixture
authority = 0
external_eligibility_established = false
g6_established = false
handoff_hash
```

`handoff_hash` commits to the entire manifest except itself. Changing any file digest, candidate binding, adapter binding, arena binding, or review packet binding changes the handoff hash.

## Forbidden cargo

The candidate-controlled package may not contain roles such as:

```text
external_attestation
eligibility_certificate
g6_certificate
world_best_certificate
world_unique_certificate
```

It may also not add top-level declarations that claim eligibility, G6, world-best, world-unique, or canonical promotion.

```text
CandidatePreparedPackage
+
CandidateIssuedCertificate
=> SELF_CERTIFICATION_VIOLATION
```

## Attestation template

The package may include an **empty template** telling a reviewer what fields a future attestation requires. The template is deliberately incomplete:

```text
template_only = true
decision = null
signature_reference = null
independence_attested = null
```

A blank form is not evidence.

```text
AttestationTemplate != Attestation
UnsignedForm != ExternalDecision
```

## Handoff state

Internal code may emit only:

```text
EXTERNAL_REVIEWER_HANDOFF_PACKAGE_READY
```

It cannot emit:

```text
ELIGIBLE_FOR_FROZEN_EXTERNAL_TRIAL
G6_PASS
WORLD_BEST
WORLD_UNIQUE
```

The package is analogous to a tamper-evident evidence box: REI may seal the box and publish its fingerprint, but another party must inspect it, establish independence, and sign any actual eligibility decision.

## Reviewer-side sequence

```text
Candidate freezes review request
-> Candidate builds handoff manifest
-> Reviewer independently obtains package
-> Reviewer verifies file hashes and handoff hash
-> Reviewer verifies candidate/adapter/request bindings
-> Reviewer verifies conflict and independence conditions
-> Reviewer performs eligibility review
-> Reviewer signs an external attestation outside candidate control
-> Identity/signature verified out of band
-> External eligibility record may become admissible evidence
```

Nothing before the final independently verified steps establishes external eligibility.

## Mutation and replay rules

```text
CandidateHashChange => NewHandoffRequired
AdapterHashChange => NewHandoffRequired
ReviewPacketChange => NewHandoffRequired
FileHashChange => HandoffInvalid
OldAttestationForNewCandidate => INVALID_PROTOCOL
```

Historical packages remain preserved for audit but cannot silently authorize newer candidates.

## Synthetic CI boundary

CI may create a synthetic handoff package and deliberately tamper with it to verify rejection.

```text
SyntheticHandoffPass != ExternalHandoff
GreenCI != IndependentReviewer
GreenCI != ExternalEligibility
GreenCI != G6_PASS
```

## Authority boundary

```text
HandoffAuthority = 0
ReviewAuthority = 0
ExperimentAuthority = 0
DeploymentAuthority = 0
RealWorldActuationAuthority = 0
RealWorldAttackAuthority = 0
CanonicalPromotionAuthority = 0
```

## Current ceiling

```text
SCIENTIFIC_HYPOTHESIS_ADAPTER_READY
-> EXTERNAL_ELIGIBILITY_REVIEW_PROTOCOL_READY
-> EXTERNAL_REVIEWER_HANDOFF_PACKAGE_READY
-> [genuinely independent reviewer required]
```

The next transition is intentionally not available to candidate-controlled code.
