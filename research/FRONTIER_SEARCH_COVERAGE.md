# Frontier Search Coverage

Status: candidate research extension, non-canonical.

Purpose: prevent omission bias in the Comparative Frontier Arena. A fair roster is invalid if the search process can quietly ignore strong challengers.

## Core rule

```text
NoCherryPicking != CompleteSearch
```

It is possible to keep every discovered competitor and still bias the arena by searching only convenient places. Therefore current-frontier claims require an auditable discovery process.

## Search coverage dimensions

A frontier search plan declares before roster freeze:

```text
Domains
SourceClasses
QueryFamilies
RecencyWindow
LanguageScope
OpenSourceCoverage
ClosedSystemCoverage
CitationBacktracking
ForwardCitationSearch
RepositorySearch
BenchmarkLeaderboardSearch
ExpertNominationChannel
StoppingRule
```

## Coverage states

- `SEARCH_PLAN_FROZEN`
- `SEARCH_IN_PROGRESS`
- `COVERAGE_INCOMPLETE`
- `COVERAGE_REVIEWABLE`
- `EXTERNAL_COVERAGE_AUDIT_REQUIRED`

Internal code cannot declare `COMPLETE_WORLD_FRONTIER_SEARCH`.

## Omission tests

```text
KnownEligibleChallengerMissingWithoutReason => COVERAGE_INCOMPLETE
OnlyOneSourceClassUsed => COVERAGE_INCOMPLETE
SearchTermsChangedAfterOutcome => INVALID_PROTOCOL
RecencyWindowChangedAfterOutcome => INVALID_PROTOCOL
StoppingRuleChangedAfterOutcome => INVALID_PROTOCOL
NegativeResultUsedAsProofOfUniqueness => INVALID_CLAIM
```

## Search failure

Network, index, API, or source outages are evidence about the search process, not evidence that no challenger exists.

```text
SearchFailure
!=
NoCompetitorExists
```

When discovery infrastructure is unavailable:

```text
CurrentFrontierRoster = UNFROZEN
WorldBest = UNVERIFIED
WorldUnique = UNVERIFIED
```

## Stopping rule

A search may stop only under a predeclared finite budget or external protocol deadline. Stopping does not imply completeness.

```text
SearchStoppedByRule != SearchComplete
```

The final report must preserve uncovered domains and unavailable sources as explicit uncertainty.

## Internal ceiling

```text
FRONTIER_SEARCH_COVERAGE_PROTOCOL_READY
ExternalCoverageAudit = REQUIRED
G6 = OPEN
```
