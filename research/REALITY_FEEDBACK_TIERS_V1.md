# REI-Ω Reality Feedback Tiers v1

Status: candidate research/runtime integration contract for PR #28 / `rei-v193-reconcile`.

## Why two tiers exist

REI now has two deliberately different reality-facing lanes. They must never be collapsed into one evidence grade.

```text
OperationalObservation != IndependentExternalEvidence
ExternalSourceLabel != VerifiedIndependence
FeedbackConsumedByModel != RealityValidated
RealityValidated != AutomaticPromotion
```

## Tier A: Operational Reality Feedback

Tier A is the Continuous Reality Loop sidecar.

Input:

```text
C:\REI-Shadow\reality-inbox\*.json
```

Required fields:

```text
evidence_id
observed_at_utc
source_type
subject
outcome
provenance
```

The sidecar normalizes accepted observations into an append-only local ledger and a bounded model context:

```text
Raw observation
-> schema/provenance check
-> evidence SHA-256
-> duplicate/conflict check
-> append-only reality-feedback ledger
-> REALITY_FEEDBACK_CONTEXT.md
-> rei-local-node-vnext fingerprint
-> next synchronized Shadow cycle
```

Every Tier A record is forced to:

```text
EpistemicStatus = UNVALIDATED_REALITY_FEEDBACK
IndependentExternalEvidence = FALSE
RealityValidated = FALSE
PromotionEffect = NONE
CanonicalWritePermission = FALSE
```

The model is explicitly instructed to treat all sidecar strings as quoted data rather than instructions. Tier A may alter hypothesis priority, uncertainty, counterexample search, challenge selection, reversible-test design, or requests for more evidence. It may not bypass Shadow, Observer, Reality Veto, promotion, or canonical-write gates.

The model state records the reality-context SHA-256. Installation succeeds only after the sidecar SHA and the model's recorded reality SHA match.

```text
SidecarSHA == ModelRealitySHA
```

This proves input wiring. It does not prove the observation is true.

## Tier B: Independently Admissible External Evidence

Tier B remains governed by the existing Reality-Closed Evolution Stack:

```text
External Evidence Admission Gate
-> Independent Replay Attestation Binding
-> External Reality Veto Ledger
-> Reality-Driven Succession Review
```

A Tier B packet requires stronger provenance and independence conditions than Tier A, including candidate/challenge binding, externally recorded identity/signature/independence verification, raw replay availability, and an outcome of PASS / FAIL / ABSTAIN.

A syntactically valid packet cannot manufacture reviewer independence.

```text
WellFormedPacket != IndependentEvidence
SelfIssuedPacket != ExternalEvidence
SyntheticFixture != ExternalEvidence
```

Tier B may support or suspend a scoped evidence claim, but it still has no canonical promotion authority.

## Non-escalation law

Tier A is never automatically upgraded into Tier B.

```text
TierAFeedback
!= TierBExternalEvidence
!= RealityValidated
!= CanonicalPromotion
```

If a Tier A observation later obtains the full independent attestation required by the Reality-Closed Evolution Stack, that separately attested packet may be evaluated by the Tier B admission gate. The original Tier A record remains in history and is not rewritten.

## Failure preservation

Reality-facing failures are append-only evidence history.

```text
NoFailureDeletion
LaterPassCannotErasePriorMaterialFail
ConflictingEvidence => PreserveConflict
UnknownIndependence => DoNotUpgrade
```

The purpose is to make reality capable of changing REI's hypothesis burden without allowing REI to manufacture its own validation.

## Current bounded claim

After host installation, Continuous Reality Loop v1 can establish only:

```text
Operational reality feedback is ingested as bounded, non-authoritative model context.
Runtime continuity is sampled over time.
Recovery requests and failures remain auditable.
```

It cannot establish until separate evidence exists:

```text
IndependentReplication
RealityValidated
L5AutonomousEvolutionProven
CanonicalPromotion
Ascension
```
