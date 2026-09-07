# REI-Ω Recovery Hardening Phase II.5
## Pre-Registration — Atomic Ownership Through Destructive Act

**Status:** `CANDIDATE_NOT_INSTALLED`

## Scope

This phase addresses exactly one known defect carried from the Phase II.4 seal:

`OS authority read -> authority released -> other checks -> backup/copy -> Remove-Item`

The Phase II.4 OS byte-lock decision is correct when observed, but its authority is no longer held when the destructive act occurs. This creates a TOCTOU window.

## Primary hypothesis

> If Self-Heal decides a stale `runtime.lock` is deletion-eligible, it must acquire and retain the same 1-byte OS lock across the destructive removal call, then release it in `finally`.

This converts:

`it was free`

into:

`it is free and Self-Heal currently holds destructive authority`.

## Production pins required before installation

- Python SHA256: `6752672711E1FF7BA5F7035221E88403EAAEE716E444573D82477A62D51EC3DB`
- Self-Heal SHA256: `11CECB2192E7555029804A8A75BB3FB6394302F11F09FF1E5CF2DA1D69CF4323`

Any mismatch is a `SAFE_ABORT`.

## Design

Add one narrow helper, `Invoke-OsByteLockProtectedRemoval`, used only at the two `runtime.lock` destructive call sites already governed by Phase II.4.

The helper must:

1. open the target with `FileShare.ReadWrite | FileShare.Delete`;
2. acquire `Lock(0,1)` immediately before removal;
3. keep the lock held while `Remove-Item` executes;
4. treat open/lock/removal uncertainty as non-removal with attributable warning evidence;
5. execute `Unlock` and `Dispose` in `finally` on every reachable path;
6. never change canonical/main, promotion authority, or RealityValidated state.

The earlier Phase II.4 `Get-OsByteLockDecision` remains as an early ownership screen. Phase II.5 adds a final destructive-authority reacquisition so freshness is established at the destructive boundary.

## Pre-registered falsification matrix

### 0045A — race / competing owner

Instrument a test copy of the protected-removal helper with a bounded delay after byte-lock acquisition and before removal. During the delay, a competing holder attempts to acquire byte 0.

PASS requires:

- Self-Heal/test helper retains byte-lock ownership through the delay;
- competing holder cannot acquire ownership;
- no live-owner lock is deleted;
- removal outcome is attributable;
- `Unlock` / `Dispose` execute.

Critical falsifier:

`COMPETING_OWNER_MUST_NOT_ACQUIRE_BETWEEN_AUTHORITY_ACQUISITION_AND_REMOVE`

### 0045B — forged marker / no OS holder regression

Re-run the Phase II.4 0044B semantics under the new pinned Self-Heal hash.

PASS requires forged heartbeat identity to remain advisory and stale lock cleanup to succeed when OS ownership is free.

### 0045C — no holder / no marker regression

Re-run Phase II.4 0044C semantics under the new pinned Self-Heal hash.

PASS requires ordinary stale-lock cleanup to remain functional.

### 0045D — live owner protection / probe safety

Re-run Phase II.4 live-holder semantics under the new pinned Self-Heal hash.

PASS requires the live owner to remain alive, lock state preserved, heartbeat clean, and no destructive action emitted.

## Acceptance rule

Do not seal Phase II.5 unless all of the following are true under one pinned post-patch Self-Heal hash:

- patch preflight pins match;
- PowerShell parser reports zero errors;
- 0045A critical race falsifier passes;
- 0045B regression passes;
- 0045C negative control passes;
- 0045D live-owner protection passes;
- post-test clean baseline passes;
- no canonical mainline touch occurs;
- `RealityValidated = false` and promotion remains `NO`.

## Explicit non-goals

Do not combine this phase with:

- `Get-ScheduledTask` fail-open remediation;
- `$CycleLock` ownership parity;
- marker parse policy;
- Evidence Epoch Invalidation;
- Epistemic Debt Gate;
- event-log rotation;
- temporary heartbeat-file cleanup;
- Mechanical Metallurgy / Kernel promotion.

**One phase, one race.**

## Boundary

`PhaseII5Pass != GlobalRecoveryCorrectness`

`AtomicRemovalAuthority != RealityValidated`

`RepositoryIntegration != HostDeployment`

`CI_GREEN != WindowsRuntimeProof`
