# External Knowledge Ingestion Gate

Status: candidate research extension. Not canonical.

## Purpose

REI may receive external conversations, documents, webpages, notes, datasets, or other knowledge artifacts. A locator alone is not knowledge. This gate prevents REI from treating an unresolved URL, title, filename, citation, or metadata record as if the underlying content had been observed.

```text
LinkExists != ContentKnown
MetadataKnown != ClaimKnown
ContentCaptured != ClaimValidated
ClaimParsed != ClaimSupported
SourceAgreement != IndependentCorroboration
IngestionReady != CanonicalPromotion
```

The gate is designed to turn opaque external artifacts into auditable, provenance-bound candidate evidence without granting the ingestion mechanism epistemic authority.

## State machine

```text
REGISTERED_UNRESOLVED
        |
        v
CAPTURED_FROZEN
        |
        v
PARSED_CANDIDATE
        |
        v
EVIDENCE_REVIEWED
        |
        +--> SUPPORTED_FOR_SCOPE
        +--> REJECTED
        +--> ABSTAIN
        +--> CONFLICTING_EVIDENCE
        +--> EXPIRED
```

Transitions must be monotone with respect to provenance. No later state may erase the original locator, retrieval history, content digest, parsing version, dissent, or rejected claims.

## Unresolved-source rule

If the body of an artifact cannot be retrieved, REI may preserve only what is actually known:

- source identifier
- source type
- locator / URL
- registration time
- retrieval attempt metadata
- retrieval status
- failure reason

It must not invent a title, summarize unseen text, infer claims from the URL, or promote any concept supposedly contained in the artifact.

```text
retrieval_status = UNRESOLVED
=> content_sha256 = null
=> snapshot_path = null
=> parsed_claims = []
=> evidence_authority = 0
=> canonical = false
```

## Frozen capture

Once the content is actually available, the raw snapshot must be frozen before interpretation:

```text
RawArtifact
-> NormalizeTransportOnly
-> SHA256
-> ImmutableSnapshotReference
-> ParserVersionFreeze
-> ClaimExtraction
```

`NormalizeTransportOnly` may remove transport encoding differences but must not paraphrase, reorder, summarize, or semantically rewrite the source before hashing.

A changed source body creates a new capture. It does not silently overwrite the previous capture.

```text
ContentHashChanged => NewCaptureRequired
OldCapture => PRESERVED
```

## Claim extraction

Every parsed claim is a candidate object, not truth:

```text
IngestedClaim = (
  claim_id,
  source_id,
  capture_hash,
  exact_support_span_or_locator,
  normalized_proposition,
  scope,
  uncertainty,
  parser_version,
  counterevidence_refs,
  conflict_state,
  authority,
  certification,
  canonical
)
```

Required defaults:

```text
authority = 0
certification = UNVERIFIED
canonical = false
```

No parsed claim may inherit credibility merely because the source is familiar, persuasive, authored by REI, authored by ChatGPT, or previously discussed.

## Conflict handling

When a newly ingested claim conflicts with existing REI material:

```text
Conflict
-> PreserveBoth
-> TraceProvenance
-> CompareEvidenceScope
-> SearchCounterexample
-> Narrow | Reject | Abstain | Revalidate
```

Forbidden:

```text
NewestSourceWins
PreferredIdentityWins
HigherConfidenceLanguageWins
DeleteOlderFailure
MergeContradictionsByNarrative
```

## Authority boundary

```text
IngestionAuthority = 0
SourceRegistrationAuthority = 0
ClaimExtractionAuthority = 0
CanonicalPromotionAuthority = 0
ExternalGateClosureAuthority = 0
ExperimentAuthority = 0
RealWorldActuationAuthority = 0
```

The ingestion gate may prepare candidate evidence for later REI processes. It cannot close G3-G13, establish world-best/world-unique status, or alter the canonical architecture by itself.

## Current registered source

The candidate branch registers the user-provided ChatGPT shared-conversation locator:

```text
https://chatgpt.com/share/6a788050-b2c0-83e8-bb30-2b3c1ba6fe08
```

At registration time its conversation body was not retrievable through the available external reader, therefore its state is deliberately `REGISTERED_UNRESOLVED`. No claim from that conversation has been inferred or promoted.

## Integration path after capture

When the body becomes available:

```text
SharedConversation
-> FrozenContentSnapshot
-> ProvenanceBoundClaims
-> ClaimScopeEvidenceGraph
-> DeathEye / Wuji Counterexample Pressure
-> Genesis Candidate Generation where justified
-> Existing external-validation gates
```

This turns cross-conversation reuse into an evidence-bearing process rather than memory-by-assertion.

## Terminal rule

```text
UnknownContent => ABSTAIN_FROM_CONTENT_CLAIMS
ObservedContent => PRESERVE_RAW_FIRST
ParsedContent => CANDIDATE_ONLY
ValidatedContent => SCOPE_BOUND_SUPPORT_ONLY
RealityVeto > ImportedNarrative
```
