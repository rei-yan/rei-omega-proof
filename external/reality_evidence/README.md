# External Reality Evidence Intake

This directory is reserved for future genuinely external evidence packets.

The repository does **not** currently contain a genuine independent external evidence packet for the Reality-Closed Evolution Stack.

A future submission should bind, at minimum, to:

```text
candidate_commit_sha
capsule_hash
challenge_commitment_hash
replay_environment_hash
raw_record_hash
result_hash
identity_evidence_hash
signature_hash
signer_key_fingerprint_hash
independence_provenance_hash
claim_scope
outcome = PASS | FAIL | ABSTAIN
```

Additional requirements:

- the challenge must be frozen before the replay;
- the raw replay record must be available for audit;
- the packet must not be issued by the candidate / repository-owner lineage;
- reviewer identity, signature, and independence provenance must be verified externally rather than merely declared in the packet;
- a PASS is scoped and revocable;
- a material FAIL is preserved and cannot be deleted by later internal CI;
- mixed material PASS/FAIL evidence yields abstention rather than vote-count victory.

Submitting a file here does not itself establish independence, G3-G13 PASS, canonical promotion, world-best status, or final truth.

Current state:

```text
AWAITING_REAL_EXTERNAL_EVIDENCE
```
