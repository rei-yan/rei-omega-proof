# REI-Ω G4 · Future Reality Gate · 未来现实门

Status: OPEN protocol

G4 exists to prevent hindsight, retuning, and same-session self-certification. A prediction must be frozen before the future outcome is observed.

## 1. Preregistration object

A G4 registration contains:

```text
protocol_version
generator_hash
model_hash
data_cutoff
target
horizon
prediction
prediction_interval
scoring_rule
baseline_spec
analysis_plan
constitution_hash
created_at
```

The canonical serialized object is committed by SHA-256.

## 2. Two-phase design

```text
REGISTER phase:
  freeze protocol, target, horizon, prediction, interval, scoring rule, baselines
  compute commitment hash
  forbid outcome input
  state = REGISTERED / G4_OPEN

RESOLVE phase:
  consume the frozen registration and a later externally sourced outcome
  verify commitment
  score without changing prediction, interval, model, or scoring rule
  preserve failures
```

A registration and its scored outcome must not be generated from the same hidden answer path.

## 3. No same-session pass

```text
SyntheticDryRun = ProtocolIntegrityOnly
SyntheticDryRun != G4Pass
```

Before a future or externally withheld outcome arrives:

```text
G4_STATUS = OPEN
```

No CI run may flip G4 to PASS simply because registration code works.

## 4. Frozen scoring

The scoring rule and baseline comparison are committed before the outcome arrives.

A valid resolver may compute metrics, but it may not:

```text
change target
change horizon
change prediction
change interval
change baseline after seeing result
change scoring rule after seeing result
silently drop failed registrations
```

## 5. Evidence boundary

For a real G4 resolution, provenance should establish that the outcome was unavailable to the prediction process at registration time.

Required external evidence should include, where feasible:

```text
timestamp
source provenance
data publication or observation time
registration commitment
resolver version
```

## 6. Relationship to other gates

```text
G2 != G4
G3 != G4
```

Lean verification of the scoped Boolean kernel does not prove prospective predictive power. Independent replication does not substitute for future prediction. G4 specifically tests temporal honesty against reality.

## 7. Current state

At creation of this module:

```text
G4_STATUS = OPEN
REAL_PROSPECTIVE_RESOLUTIONS = 0
```

This is intentional. The gate is not allowed to self-certify.
