# Reality-Closed Evolution Stack

Status: candidate research extension only.

This stack advances four coupled layers beyond the current Wuxiang Total Convergence Kernel:

```text
49. External Evidence Admission Gate
50. Independent Replay Attestation Binding
51. External Reality Veto Ledger
52. Reality-Driven Succession Trigger
```

The purpose is not to simulate external validation. It is to make the architecture unable to cross an external gate without genuinely external evidence.

## Core transition

```text
Internal Candidate
-> Frozen Reproducibility Capsule
-> External Evidence Admission
-> Commit / Capsule / Challenge Binding
-> Append-Only Reality Veto Ledger
-> Support | Suspend | Abstain
-> Reality-Driven Succession Review
```

## 49. External Evidence Admission Gate

A packet is not external merely because it contains a reviewer name, signature-shaped string, or PASS verdict.

```text
WellFormedPacket != IndependentEvidence
DeclaredReviewer != VerifiedReviewer
SelfIssuedPacket != ExternalEvidence
SyntheticFixture != ExternalEvidence
```

Admission requires, within the protocol scope:

- source mode is real external, not a synthetic fixture;
- packet is not issued by the repository owner / candidate lineage;
- reviewer identity verification is externally recorded;
- signature verification is externally recorded;
- independence provenance is externally recorded;
- raw replay record is available;
- challenge was frozen before the replay;
- outcome is PASS, FAIL, or ABSTAIN;
- cryptographic binding fields are well formed.

The protocol can validate records supplied to it. It cannot manufacture reviewer independence.

## 50. Independent Replay Attestation Binding

An admitted packet is bound to exactly one candidate state and one frozen challenge context:

```text
Binding = H(
  candidate_commit_sha,
  capsule_hash,
  challenge_commitment_hash,
  replay_environment_hash,
  raw_record_hash,
  result_hash,
  claim_scope
)
```

Any mismatch rejects the packet for that evaluation.

```text
RightReviewer + WrongCommit = REJECT
RightCommit + WrongChallenge = REJECT
RightChallenge + MissingRawRecord = REJECT
```

## 51. External Reality Veto Ledger

Externally admissible evidence is append-only.

```text
NoExternalDefeatDeletion
ExternalPassCannotErasePriorMaterialFail
```

For a matching claim scope:

```text
Admissible material FAIL
=> INCUMBENT_EXTERNAL_SUPPORT_SUSPENDED

Admissible PASS with no unresolved material FAIL
=> EXTERNALLY_SUPPORTED_FOR_SCOPE

PASS + unresolved material FAIL
=> MIXED_EXTERNAL_EVIDENCE_ABSTAIN

ABSTAIN only
=> EXTERNAL_EVIDENCE_INCONCLUSIVE
```

Internal CI cannot overwrite this ledger.

## 52. Reality-Driven Succession Trigger

If real external evidence suspends the incumbent, the architecture may prepare a successor review. It may not auto-promote a successor.

A successor may become `READY_FOR_EXTERNAL_SUCCESSION_REVIEW` only when it has fresh externally admissible support, preserves the frozen constitutional hard predicates within scope, does not expand the authority ceiling, and preserves recovery / rollback requirements.

```text
IncumbentExternallyFails
!= AutomaticSuccessorPromotion

SuccessorExternallyPasses
!= CanonicalPromotion

NoEligibleSuccessor
=> ABSTAIN / HOLD
```

A non-REI successor must not be rejected merely because it is non-REI.

## Reality-closed law

```text
InternalClosure != ExternalTruth
Replayable != IndependentlyReplayed
AdmittedPacket != ProvenUniversalValidity
ExternalSupportIsScopedAndRevocable
ExternalFailureMaySuspendIncumbent
RealityMayForceIdentityRetirement
```

## Internal ceiling

```text
EXTERNAL_EVIDENCE_ADMISSION_GATE_READY
INDEPENDENT_REPLAY_ATTESTATION_BINDING_READY
EXTERNAL_REALITY_VETO_LEDGER_READY
REALITY_DRIVEN_SUCCESSION_TRIGGER_READY
REALITY_CLOSED_EVOLUTION_STACK_READY
AWAITING_REAL_EXTERNAL_EVIDENCE
```

None of these close G3-G13.

## Authority boundary

```text
EvidenceAdmissionAuthority = 0
ReviewerIdentityAuthority = 0
ExternalValidationAuthority = 0
SuccessionAuthority = 0
CanonicalPromotionAuthority = 0
ExperimentAuthority = 0
DeploymentAuthority = 0
RealWorldAttackAuthority = 0
RealWorldActuationAuthority = 0
ExternalActuation = DENY_BY_DEFAULT
```

## Anti-finality

```text
CurrentSupremeForm != PermanentSupremeForm
ExternalPass != FinalTruth
ExternalFail != NarrativeErasurePermission
Reality > EvidenceClaim > Architecture > Identity
NoSacredIncumbent
NoSacredSuccessor
NoSacredFinalForm
```
