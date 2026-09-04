# REI-Ω v1.9.3 Local Runtime Synchronization

Current integrated candidate: PR #28 / `rei-v193-reconcile`.

## Runtime participants

One established v1.9.3 compatible epoch/cycle covers:

1. God Wheel
2. Local Model `rei-local-node-vnext`
3. Shadow V2.3
4. vNext Observer
5. vNext Bridge
6. Ledger
7. Watchdog
8. Recovery
9. God Line observer bundle

A runtime cycle may report `SUCCESS_RUNTIME_VERIFIED` only when every required participant has real heartbeat/health evidence in the same compatible runtime contract. Old model presence, file existence alone, or hard-coded booleans are not sufficient.

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

## Synchronized extension rule

New observer capabilities are not considered locally deployed just because their repository files exist. Their contract must be propagated across the relevant compatibility surfaces and then verified on the Windows host.

```text
God Wheel
Local Model
Shadow
Observer
Bridge
Ledger
Watchdog
Recovery
God Line
Formal proof
CI
Runtime deploy / rollback
Handoff
```

Repository integration and host deployment are separate evidence states.

## RDDO candidate extension

The current candidate adds a bounded Recursive Divided-Difference Observer (RDDO).

Repository/runtime assets:

```text
research/rddo_reference.py
research/rddo_sanity.py
Rei_omega_proof/RecursiveDifferenceObserver.lean
research/GOD_WHEEL_FUSION_V1_9_4_RDDO.md
runtime/rddo-extension-contract-v194.json
runtime/Install-REI-RDDO-V194.ps1
```

RDDO is observer-only and has no promotion or reality-validation authority.

```text
InterpolationFit != Truth
LocalDifference != GlobalCausality
HighOrderActivity != VerifiedRegimeChange
HigherOrder != BetterEvidence
RDDO != RealityValidation
RDDO != PromotionAuthority
```

The guarded RDDO installer:

```text
FETCH exact reconciled candidate SHA
-> CHECKPOINT previous RDDO asset
-> STAGE Python + contract
-> PY_COMPILE
-> deterministic self-test
-> verify observer_only=true
-> verify promotion_capability=false
-> verify reality_validated=false
-> ATOMIC COPY
-> write local RDDO attestation
-> RDDO_DEPLOYED_VERIFIED
```

Failure rolls the optional observer asset back to its previous state. The installer creates no extra scheduler, so it cannot race the Full Pipeline.

A repository commit alone does **not** establish `RDDO_DEPLOYED_VERIFIED` on the user's Windows machine. Fresh local state is required.

## Scheduler authority

When `REI Full Pipeline v1.9.1` exists, it is the authoritative mutating scheduler for the synchronized v1.9.3 cycle. `Install-REI-VNext.ps1` deploys vNext components but removes/disables the separate `REI Unattended Closed Loop` scheduled task to prevent duplicate Shadow/Observer/Bridge/GitHub cycles.

If the Full Pipeline is absent, the standalone vNext loop may be used only as a fallback scheduler.

RDDO does not create a scheduler. It is an observer asset only.

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
-> VERIFY PR #28 + exact vNext model + all established runtime participants
-> DEPLOYED_VERIFIED
```

Any post-checkpoint verification failure rolls back to the prior runtime. Pending, missing, cancelled, or failed CI results in WAIT/ABSTAIN.

The base safe updater still verifies the established v1.9.3 runtime contract. RDDO must not be counted as a verified host participant until its guarded installer/overlay has run and the runtime contract is explicitly advanced to include its fresh state evidence.

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

To deploy the optional synchronized RDDO observer after the candidate checks are green:

```powershell
git -C C:\REI-Shadow\repo show origin/rei-v193-reconcile:runtime/Install-REI-RDDO-V194.ps1 |
Set-Content -Encoding UTF8 C:\REI-Shadow\Install-REI-RDDO-V194.ps1

powershell -ExecutionPolicy Bypass -File C:\REI-Shadow\Install-REI-RDDO-V194.ps1
```

## Evidence inspection

```powershell
Get-Content C:\REI-Shadow\runtime-v191\autoupdate\last-update.json
Get-Content C:\REI-Shadow\runtime-v191\state\last-cycle.json
Get-Content C:\REI-Shadow\state\vnext_observer\latest.json
Get-Content C:\REI-Shadow\state\rddo\latest.json
Get-Content C:\REI-Shadow\context\sync_state.json
ollama list
```

A successful local deployment remains engineering evidence only.

```text
GreenCI != IndependentReplication
CanaryPass != RealityValidation
DeploymentSuccess != RealityValidation
AutomaticUpdate != AuthorityExpansion
RDDO_DEPLOYED_VERIFIED != RealityValidation
```

The updater may fetch, stage, validate, checkpoint, switch the local observer runtime, restart local observer tasks, rollback, and record evidence. It may not merge canonical `main`, enable Promotion, set `RealityValidated = TRUE`, or bypass failed gates.
