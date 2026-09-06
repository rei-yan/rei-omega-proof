# Frontier Roster Freeze

Status: candidate research extension, non-canonical.

Purpose: convert the G6 Comparative Frontier Arena from a generic comparison harness into an auditable challenger-admission process without allowing REI to cherry-pick weak or convenient opponents.

## Core rule

```text
CurrentFrontierClaim
requires
FrozenRoster + PrimarySourceProvenance + VersionBinding + InclusionCriteria + ExclusionRecord
```

A named system is not admitted merely because it is famous, recent, or convenient.

```text
MentionedSystem != FrontierCompetitor
RepositoryFound != CurrentFrontier
PaperFound != ComparableImplementation
Popularity != Relevance
```

## Admission states

- `ROSTER_CANDIDATE`: plausible challenger, not yet evidence-complete.
- `SOURCE_VERIFIED`: primary source and version identity verified.
- `COMPARABILITY_REVIEW`: scope, task and budget comparability under review.
- `FROZEN_FRONTIER_COMPETITOR`: admitted before hidden evaluation.
- `EXCLUDED_WITH_REASON`: excluded with immutable pre-outcome rationale.
- `STALE_REVALIDATION_REQUIRED`: source/version exceeded the roster freshness horizon.

## Required challenger record

```text
ChallengerRecord = (
  challenger_id,
  domain,
  system_name,
  version_or_commit,
  primary_source_uri,
  source_date,
  source_hash_or_commit,
  implementation_uri,
  implementation_status,
  task_scope,
  claimed_capabilities,
  known_constraints,
  compute_profile,
  human_assistance_profile,
  data_access_profile,
  tool_access_profile,
  license_or_access_constraints,
  inclusion_reason,
  exclusion_risks,
  freshness_horizon,
  admission_state
)
```

## Freeze procedure

```text
Discover candidates
-> Verify primary sources
-> Bind exact versions
-> Record inclusion/exclusion criteria
-> Check task comparability
-> Check budget comparability
-> Publish roster commitment
-> Freeze roster
-> Only then reveal hidden arena
```

## Anti-cherry-pick vetoes

```text
RemoveCompetitorAfterLoss => INVALID_PROTOCOL
AddWeakCompetitorAfterOutcome => INVALID_PROTOCOL
ExcludeStrongCompetitorWithoutPreOutcomeReason => INVALID_PROTOCOL
VersionSwapAfterFreeze => INVALID_PROTOCOL
SourceDateFabrication => INVALID_PROTOCOL
PrimarySourceMissing => NOT_ADMISSIBLE
ComparabilityUnknown => ROSTER_CANDIDATE
```

## Freshness

Frontier status expires. A frozen roster remains historical evidence, but cannot silently become a current-frontier claim after its freshness horizon.

```text
HistoricalRoster = PRESERVED
ExpiredRoster -> CurrentFrontierAuthority = SUSPENDED
```

## Search failure rule

If current primary-source discovery is unavailable or incomplete:

```text
SearchUnavailable
-> preserve candidate slots
-> mark roster incomplete
-> do not freeze current-frontier roster
-> do not infer world-best absence
```

The system must not fill missing challengers from memory and call the roster current.

## Internal ceiling

```text
FRONTIER_ROSTER_FREEZE_PROTOCOL_READY
G6 = OPEN
CurrentFrontierRoster = NOT_YET_EXTERNALLY_FROZEN
WorldBest = UNVERIFIED
WorldUnique = UNVERIFIED
```

This protocol does not itself identify the world's strongest systems. It only defines what evidence is required before such systems can enter a fair frozen comparison.
