# REI-Ω Continuous Reality Loop v1

Current candidate: PR #28 / `rei-v193-reconcile`.

## What this layer adds

```text
Reality Inbox
-> Reality Sidecar
-> append-only reality-feedback ledger
-> REALITY_FEEDBACK_CONTEXT.md
-> rei-local-node-vnext reality SHA binding
-> next synchronized Shadow cycle

Host runtime
-> Continuous Reality Guard
-> freshness / task / component checks
-> bounded recovery requests
-> 24h / 72h / 168h rolling stability evidence
```

The two paths are deliberately bounded:

```text
RealityFeedback != IndependentExternalEvidence
RealityFeedback != RealityValidated
72hStableHostEvidence != L5Proven
Promotion = NO
Ascension = NO
CanonicalMainlineTouched = FALSE
```

## Install on the Windows REI host

Run from an elevated PowerShell:

```powershell
git -C C:\REI-Shadow\repo fetch origin rei-v193-reconcile

git -C C:\REI-Shadow\repo show origin/rei-v193-reconcile:runtime/Install-REI-Continuous-Reality-Loop-V1.ps1 |
Set-Content -Encoding UTF8 C:\REI-Shadow\Install-REI-Continuous-Reality-Loop-V1.ps1

powershell -NoProfile -ExecutionPolicy Bypass -File C:\REI-Shadow\Install-REI-Continuous-Reality-Loop-V1.ps1
```

The installer:

1. fetches the current reconciled candidate assets;
2. validates PowerShell syntax and authority locks;
3. installs the reality sidecar, host guard, orchestrator, and reality-aware local-model overlay;
4. creates / preserves `C:\REI-Shadow\reality-inbox`;
5. builds the sidecar once;
6. forces one `rei-local-node-vnext` refresh;
7. requires `SidecarSHA == ModelRealitySHA`;
8. installs `REI Continuous Reality Guard v1` as `SYSTEM`, at startup and every 10 minutes by default;
9. records install evidence without claiming RealityValidated or promotion.

## Evidence files

```powershell
Get-Content C:\REI-Shadow\state\continuous-reality-install.json
Get-Content C:\REI-Shadow\state\continuous-reality\latest.json
Get-Content C:\REI-Shadow\state\continuous-reality\history.jsonl -Tail 20
Get-Content C:\REI-Shadow\state\reality-feedback\latest.json
Get-Content C:\REI-Shadow\state\reality-feedback\ledger.jsonl -Tail 20
Get-Content C:\REI-Shadow\context\model_vnext_state.json
```

Expected installation invariant:

```text
continuous-reality-install.json.reality_sidecar_bound_to_model = true
continuous-reality-install.json.reality_context_sha256
==
continuous-reality-install.json.model_reality_context_sha256
```

## Add an operational reality observation

Use a unique `.json` file in:

```text
C:\REI-Shadow\reality-inbox
```

Minimal shape:

```json
{
  "schema_version": 1,
  "evidence_id": "unique-id",
  "observed_at_utc": "2026-09-05T04:00:00Z",
  "source_type": "human",
  "subject": "what was observed",
  "outcome": "what actually happened",
  "provenance": "where this observation came from",
  "reality_validated": false,
  "promotion_authority": false
}
```

Allowed `source_type` values:

```text
human
external_system
external_model
benchmark
prospective_trial
```

A source type is a routing label, not proof of independence.

The SYSTEM orchestrator rebuilds the sidecar on its next guard pass. The local model consumes a changed sidecar on the next synchronized hourly pipeline refresh because its fingerprint includes the reality-context SHA.

## 72-hour gate

`stability_72h_verified=true` requires accumulated host history. It cannot become true immediately after installation.

Initial rule:

```text
coverage >= 71.5 hours
healthy sample ratio >= 0.99
unique successful synchronized cycles >= 60
unknown HOLD samples = 0
canonical touch samples = 0
maximum guard gap <= 30 minutes
current guard status = HEALTHY
```

This proves bounded runtime continuity only.

## Reality-validation boundary

Operational observations use the Tier A sidecar. Independently admissible external evidence remains a separate Tier B process under the Reality-Closed Evolution Stack.

```text
TierAOperationalFeedback
!= TierBIndependentExternalEvidence
!= RealityValidated
!= CanonicalPromotion
```

See:

```text
research/REALITY_FEEDBACK_TIERS_V1.md
research/REALITY_CLOSED_EVOLUTION_STACK.md
```
