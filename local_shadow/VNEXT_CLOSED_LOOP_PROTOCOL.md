# REI Closed Loop Sync vNext

Protocol: `REI-CLP/3.0-observer`

This is an observer-governance upgrade for the existing `shadow-node` loop. It does not change canonical/main and does not grant new external authority.

## Lockstep path

```text
GitHub context sync
-> rei-local-node
-> rei-local-node-vnext overlay
-> Shadow V2.3 + Resilience Layer v1
-> vNext observer
-> vNext bridge
-> Divine Wheel inbox
-> GitHub shadow-node
-> cloud receipt pull
-> next local cycle
```

## Added observer functions

- Evidence lineage scoring and duplicate-source pressure.
- Failure fingerprints and recurrence counts.
- Multi-hypothesis state preservation.
- Calibration ledger entries that remain `PENDING_OUTCOME` until a real outcome exists.
- Prospective-seal support that refuses to call an internal timestamp externally witnessed.
- Spectral observer hook that stays inactive when no numeric time series exists.
- Promotion Gate v2 advisory. It can recommend `HOLD` or `ELIGIBLE_FOR_FURTHER_REVIEW`, but cannot promote canonical state.

## Immutable boundaries

```text
HighScore != Promotion
RepeatedEvidence != IndependentEvidence
InternalPrediction != IndependentProspectiveEvidence
HypothesisMixture != QuantumSuperposition
ObserverOutput != CanonicalAuthority
RealityValidated = FALSE unless externally earned
IndependentReplication = FALSE unless independently earned
CanonicalWritePermission = FALSE
```

## Compatibility

The existing Shadow V2.3 cycle schema remains unchanged. vNext is added as a sidecar observer and bridge envelope so rollback is simple and old state/checkpoints remain readable.
