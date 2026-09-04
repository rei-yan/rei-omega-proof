# REI-Ω v1.9.x Local Runtime Synchronization

This directory turns the synchronization contract into a local Windows runtime harness.

## Runtime participants

One shared `epoch_id` and `cycle_id` covers:

- God Wheel
- Local Model
- Shadow
- Observer
- Bridge
- Ledger
- Watchdog
- Recovery
- God Line

The runtime fails closed on incompatible metadata or missing health evidence and preserves:

```text
observer_only = true
canonical_mainline_touched = false
RealityValidated = FALSE
Promotion = NO
```

## Verified local cycle

The installed Windows pipeline writes:

```text
C:\REI-Shadow\runtime-v191\state\last-cycle.json
```

A fully verified cycle must show:

```text
cycle_status = SUCCESS_RUNTIME_VERIFIED
heartbeat = true
healthcheck_passed = true
observer_only = true
promotion_capability = false
```

A successful cycle still does not imply reality validation.

## v1.9.3 Safe Auto-Update Gate

The remaining code-deployment synchronization gap is handled by:

```text
runtime/Install-REI-SafeAutoUpdate-V193.ps1
runtime/Safe-AutoUpdate-V193.ps1
runtime/rei_cycle_v193.ps1
```

The updater is pinned to:

```text
origin/rei-god-wheel-fusion-v1-observer
```

and follows this guarded path:

```text
DISCOVER
-> FETCH
-> REQUIRE G2 Lean Proof Gate completed/success
-> REQUIRE current SUCCESS_RUNTIME_VERIFIED
-> CHECKPOINT
-> STAGE candidate runtime
-> POWERSHELL SYNTAX CHECK
-> NON-MUTATING CANARY
-> ATOMIC SWITCH
-> FIRST FULL SYNCHRONIZED CYCLE
-> VERIFY candidate SHA + all component health
-> COMMIT ACTIVE
```

Any failure after checkpoint performs rollback to the previous runtime script and restarts the previous pipeline.

Polling for a newer candidate is not permission to deploy. Pending/missing/failed CI results in WAIT/ABSTAIN and leaves the healthy runtime untouched.

## Install Safe Auto-Update

Only after the v1.9.3 branch head has a successful G2 CI run and the current local runtime already reports `SUCCESS_RUNTIME_VERIFIED`, run from an elevated PowerShell:

```powershell
git fetch origin

git show origin/rei-god-wheel-fusion-v1-observer:runtime/Install-REI-SafeAutoUpdate-V193.ps1 |
Set-Content -Encoding UTF8 C:\REI-Shadow\Install-REI-SafeAutoUpdate-V193.ps1

powershell -ExecutionPolicy Bypass -File C:\REI-Shadow\Install-REI-SafeAutoUpdate-V193.ps1
```

Default poll interval is 15 minutes.

Update evidence:

```powershell
Get-Content C:\REI-Shadow\runtime-v191\autoupdate\last-update.json
```

Runtime evidence:

```powershell
Get-Content C:\REI-Shadow\runtime-v191\state\last-cycle.json
```

Expected successful deployment state:

```text
status = DEPLOYED_VERIFIED
cycle_status = SUCCESS_RUNTIME_VERIFIED
observer_source_sha = candidate_sha
```

## Safety rules

```text
NewerVersion != DeployableVersion
GreenCI != SafeDeployment
CanaryPass != RealityValidation
DeploymentSuccess != RealityValidation
AutomaticUpdate != AutomaticAuthorityExpansion
```

The updater may fetch, stage, validate, checkpoint, switch the local observer runtime, restart local observer tasks, rollback, and record evidence. It may not merge canonical `main`, enable Promotion, set `RealityValidated = TRUE`, or bypass failed gates.
