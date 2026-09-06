# Frontier Rechallenge Protocol

Status: candidate research extension, non-canonical.

Purpose: prevent a frozen frontier roster from becoming a permanent moat. New challengers discovered after a valid historical arena cannot rewrite that historical arena, but can force a new prospective comparison.

## Core rule

```text
HistoricalFreeze != PermanentExclusion
NewEligibleChallenger != HistoricalResultInvalidation
NewEligibleChallenger => NewArenaRequired
```

## Challenger arrival states

- `NEW_CHALLENGER_CANDIDATE`
- `SOURCE_VERIFICATION_REQUIRED`
- `COMPARABILITY_REVIEW_REQUIRED`
- `ELIGIBLE_FOR_NEXT_ARENA`
- `NOT_COMPARABLE_WITH_REASON`
- `STALE_OR_WITHDRAWN`

## Historical integrity

If Arena N was valid under its frozen roster:

```text
ArenaNRecord = PRESERVED
```

A challenger discovered later does not retroactively enter Arena N. Instead:

```text
NewEligibleChallenger
-> Freeze Arena N+1 protocol
-> refresh roster and versions
-> refresh evidence leases
-> new hidden test
-> new independent evaluation
```

## Anti-moat vetoes

```text
RejectNewChallengerBecauseIncumbentWonBefore => INVALID_DECISION
DelayEligibleChallengerUntilAfterClaimExpiryToAvoidTest => INVALID_DECISION
SilentlyReuseOldChampionStatusAgainstNewField => INVALID_CLAIM
UseHistoricalWinAsPermanentFrontierAuthority => INVALID_CLAIM
```

## Rechallenge triggers

A new arena is required when one or more occur:

```text
EligibleNewChallenger
MaterialCompetitorVersionChange
MaterialBenchmarkShift
MaterialCapabilityShift
HistoricalRosterLeaseExpiry
IndependentEvaluatorRequestsRechallenge
```

The trigger grants no deployment or actuation authority. It only opens a new evidence challenge.

## Claim leases

```text
ScopedFrontierClaim = time-bounded lease
```

Possible statuses:

- `SUPPORTED_FOR_FROZEN_ARENA`
- `RECHALLENGE_REQUIRED`
- `EXPIRED`
- `REJECTED`
- `ABSTAIN`

Never `PERMANENT_FRONTIER_CHAMPION`.

## Internal ceiling

```text
FRONTIER_RECHALLENGE_PROTOCOL_READY
G6 = OPEN
CurrentWorldBest = UNVERIFIED
```

This module cannot manufacture a challenger, prove it is frontier-level, or close G6. It only guarantees that a legitimate new challenger cannot be permanently excluded by an old victory.
