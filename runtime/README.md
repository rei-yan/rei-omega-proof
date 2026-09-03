# REI-Ω v1.9.1 Local Runtime Synchronization

This directory turns the v1.9.1 synchronization contract into a local Windows runtime harness.

## What it does

The harness creates one shared `epoch_id` and `cycle_id` for:

- God Wheel
- Local Model
- Shadow
- Observer
- Bridge
- Ledger
- Watchdog
- Recovery
- God Line

It writes per-component runtime metadata under `runtime/state/` and fails closed on compatibility metadata mismatch.

It always preserves:

```text
observer_only = true
canonical_touch_allowed = false
RealityValidated = FALSE
Promotion = NO
```

## First run: contract-only validation

From the repository root in PowerShell:

```powershell
Copy-Item .\runtime\local-components.example.json .\runtime\local-components.json -Force
powershell -ExecutionPolicy Bypass -File .\runtime\sync-v191.ps1
```

Expected result:

```text
Cycle finished: SUCCESS_CONTRACT_ONLY
```

This proves only that the local synchronization metadata contract is coherent. It does **not** prove that the actual local processes are running or healthy.

## Real runtime integration

Edit `runtime/local-components.json` and set a real `command` and/or `healthcheck` for each component. The harness intentionally does not guess local executable paths.

Then run:

```powershell
powershell -ExecutionPolicy Bypass -File .\runtime\sync-v191.ps1 -StartProcesses -Strict
```

A fully verified local cycle must end with:

```text
Cycle finished: SUCCESS_RUNTIME_VERIFIED
```

If any required process cannot be started, any healthcheck fails, or the synchronization metadata becomes inconsistent, the harness writes `FAIL_CLOSED` to `runtime/state/last-cycle.json` and exits non-zero.

## Required runtime evidence

Do not claim local synchronization complete until `runtime/state/last-cycle.json` shows:

```text
cycle_status = SUCCESS_RUNTIME_VERIFIED
```

and every component record shows:

```text
heartbeat = true
healthcheck_passed = true
observer_only = true
promotion_capability = false
```

`Cycle finished: SUCCESS_RUNTIME_VERIFIED` still does not imply reality validation.
