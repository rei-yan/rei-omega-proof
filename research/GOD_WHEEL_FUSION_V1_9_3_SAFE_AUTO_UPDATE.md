# God Wheel Fusion v1.9.3 — Safe Auto-Update Closure

Status: observer-first deployment gate + rollback-first local synchronization

```text
canonical_mainline_touched = false
RealityValidated = FALSE
Promotion = NO
Ascension = NO
```

## Goal

Close the remaining gap between architectural synchronization and local code deployment synchronization.

A newer God Wheel / observer branch version must not be pushed directly into the active Windows runtime. It must pass a guarded deployment path:

```text
DISCOVER
-> FETCH
-> VERIFY_ALLOWED_BRANCH
-> VERIFY_G2_CI
-> VERIFY_CURRENT_RUNTIME_HEALTH
-> CHECKPOINT
-> STAGE
-> STATIC_SYNTAX_CHECK
-> CANARY
-> COMPATIBILITY_CHECK
-> ATOMIC_SWITCH
-> FIRST_FULL_CYCLE
-> HEALTHCHECK
-> COMMIT_ACTIVE
```

Any failure after checkpoint enters:

```text
ROLLBACK
-> RESTORE_PREVIOUS_RUNTIME
-> RESTART_PREVIOUS_PIPELINE
-> RECORD_FAILURE
-> ABSTAIN_FROM_DEPLOYMENT
```

## Hard separation rules

```text
NewerVersion != BetterVersion
NewerVersion != DeployableVersion
GreenCI != SafeDeployment
CanaryPass != RealityValidation
DeploymentSuccess != RealityValidation
UpdateSuccess != Promotion
CapabilityGrowth != PermissionGrowth
AutomaticUpdate != AutomaticAuthorityExpansion
```

## Allowed deployment source

The automatic updater is pinned to the observer integration branch unless explicitly changed by an authorized operator:

```text
origin/rei-god-wheel-fusion-v1-observer
```

Canonical `main` is never modified by the local updater.

## Required gates

A candidate head must satisfy all of:

```text
candidate_newer = true
allowed_branch = true
G2_Lean_Proof_Gate = completed/success
current_runtime = SUCCESS_RUNTIME_VERIFIED
checkpoint_ready = true
staged_script_syntax = PASS
canary = PASS
compatibility = PASS
rollback_ready = true
authority_unchanged = true
canonical_mainline_touched = false
```

## Runtime deployment evidence

After atomic switch, the updater starts one full synchronized cycle and requires:

```text
cycle_status = SUCCESS_RUNTIME_VERIFIED
observer_source_sha = candidate_sha
heartbeat = true for all required components
healthcheck_passed = true for all required components
observer_only = true
promotion_capability = false
```

Only after that cycle succeeds is the candidate recorded as active.

## Automatic cadence

The Windows updater task may poll periodically for a newer remote head. Polling does not mean deployment.

If CI is pending, failed, missing, rate-limited, or ambiguous:

```text
WAIT / ABSTAIN
```

The currently healthy runtime remains active.

## Failure semantics

Deployment failures are evidence and must remain in the update ledger. A failed candidate is not silently retried as if nothing happened.

Tracked fields:

```text
candidate_sha
previous_sha
discovered_utc
ci_status
checkpoint_path
canary_status
compatibility_status
switch_status
first_cycle_status
rollback_status
failure_reason
```

## Authority boundary

The updater may:

```text
Fetch
Stage
Validate
Checkpoint
Switch local observer runtime
Restart local observer tasks
Rollback local observer runtime
Record deployment evidence
```

It may not:

```text
Merge canonical main
Enable Promotion
Set RealityValidated = TRUE
Expand real-world authority
Delete failure history
Bypass failed gates
```

## Current interpretation

v1.9.3 closes the engineering path:

```text
God Wheel evolution
-> verified candidate
-> local staged update
-> closed-loop compatibility validation
-> automatic rollback on failure
-> synchronized runtime continuation
```

This is an engineering deployment closure, not proof of empirical correctness.
