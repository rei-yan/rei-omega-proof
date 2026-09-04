# REI-Ω v1.9.3 Local Runtime Synchronization

Current integrated candidate: PR #28 / `rei-v193-reconcile`.

## Runtime participants

One compatible epoch/cycle covers:

1. God Wheel
2. Local Model `rei-local-node-vnext`
3. Shadow V2.3
4. vNext Observer
5. vNext Bridge
6. Ledger
7. Watchdog
8. Recovery
9. God Line observer bundle

A runtime cycle may report `SUCCESS_RUNTIME_VERIFIED` only when every participant has real heartbeat/health evidence in the same compatible runtime contract. Old model presence, file existence alone, or hard-coded booleans are not sufficient.

```text
observer_only = true
canonical_mainline_touched = false
RealityValidated = FALSE
Promotion = NO
candidate_pull_request = 28
candidate_head_ref = rei-v193-reconcile
```

Current runtime evidence:

```text
C:\REI-Shadow\runtime-v191\state\last-cycle.json
```

Current local context evidence:

```text
C:\REI-Shadow\context\sync_state.json
```

The context state must identify PR #28 and `rei-v193-reconcile` before the vNext local model may be considered synchronized.

## Scheduler authority

When `REI Full Pipeline v1.9.1` exists, it is the authoritative mutating scheduler for the synchronized v1.9.3 cycle. `Install-REI-VNext.ps1` deploys vNext components but removes/disables the separate `REI Unattended Closed Loop` scheduled task to prevent duplicate Shadow/Observer/Bridge/GitHub cycles.

If the Full Pipeline is absent, the standalone vNext loop may be used only as a fallback scheduler.

## v1.9.3 Safe Auto-Update Gate

Files:

```text
runtime/Install-REI-SafeAutoUpdate-V193.ps1
runtime/Safe-AutoUpdate-V193.ps1
runtime/rei_cycle_v193.ps1
runtime/Migrate-REI-V193-ReconciledLineage.ps1
```

Candidate source:

```text
origin/rei-v193-reconcile
```

Guarded path:

```text
DISCOVER
-> FETCH reconciled candidate
-> REQUIRE every attached candidate check suite completed/success
-> REQUIRE explicit G2 Lean Proof Gate completed/success
-> REQUIRE healthy current synchronized runtime
-> CHECKPOINT
-> STAGE
-> POWERSHELL SYNTAX CHECK
-> NON-MUTATING CANARY
-> ATOMIC SWITCH
-> FIRST FULL SYNCHRONIZED CYCLE
-> VERIFY PR #28 + exact vNext model + all 9 components
-> DEPLOYED_VERIFIED
```

Any post-checkpoint verification failure rolls back to the prior runtime. Pending, missing, cancelled, or failed CI results in WAIT/ABSTAIN.

## Install / migrate

Use an elevated PowerShell after the candidate CI is green:

```powershell
git -C C:\REI-Shadow\repo fetch origin rei-v193-reconcile

git -C C:\REI-Shadow\repo show origin/rei-v193-reconcile:runtime/Install-REI-SafeAutoUpdate-V193.ps1 |
Set-Content -Encoding UTF8 C:\REI-Shadow\Install-REI-SafeAutoUpdate-V193.ps1

powershell -ExecutionPolicy Bypass -File C:\REI-Shadow\Install-REI-SafeAutoUpdate-V193.ps1
```

For an already-installed updater that still points at the former observer branch, use:

```powershell
git -C C:\REI-Shadow\repo show origin/rei-v193-reconcile:runtime/Migrate-REI-V193-ReconciledLineage.ps1 |
Set-Content -Encoding UTF8 C:\REI-Shadow\Migrate-REI-V193-ReconciledLineage.ps1

powershell -ExecutionPolicy Bypass -File C:\REI-Shadow\Migrate-REI-V193-ReconciledLineage.ps1
```

## Evidence inspection

```powershell
Get-Content C:\REI-Shadow\runtime-v191\autoupdate\last-update.json
Get-Content C:\REI-Shadow\runtime-v191\state\last-cycle.json
Get-Content C:\REI-Shadow\state\vnext_observer\latest.json
Get-Content C:\REI-Shadow\context\sync_state.json
ollama list
```

A successful local deployment remains engineering evidence only.

```text
GreenCI != IndependentReplication
CanaryPass != RealityValidation
DeploymentSuccess != RealityValidation
AutomaticUpdate != AuthorityExpansion
```

The updater may fetch, stage, validate, checkpoint, switch the local observer runtime, restart local observer tasks, rollback, and record evidence. It may not merge canonical `main`, enable Promotion, set `RealityValidated = TRUE`, or bypass failed gates.
