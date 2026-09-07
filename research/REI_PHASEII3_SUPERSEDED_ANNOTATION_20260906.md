# REI-Ω Phase II.3 Seal — Superseded Annotation

**Historical seal:** Phase II.3, 2026-09-06  
**Historical Self-Heal pin:** `5415F0555FD93414CBDAB87F5A62084F1F32BCED6666539C60583E7AA571B19C`  
**Current Phase II.4 Self-Heal pin at supersession:** `11CECB2192E7555029804A8A75BB3FB6394302F11F09FF1E5CF2DA1D69CF4323`

## Status

`SUPERSEDED_FOR_CURRENT_PRODUCTION_BEHAVIOR`

The Phase II.3 evidence remains historically valid for the exact Phase II.3 source pin and tested host conditions. It must not be read as evidence of current Phase II.4 production behavior.

Phase II.3 sealed these heartbeat-marker behaviors as authority-bearing preservation mechanisms:

- `validated_live_degraded_owner`
- `recent_degraded_marker_uncertain:*`

Phase II.4 intentionally changed the trust boundary. OS 1-byte lock ownership became primary, while heartbeat-marker results became advisory when the OS byte lock is free. Therefore those Phase II.3 preservation semantics are inert as independent vetoes at the Phase II.4 production hash.

## Governance consequence

Any evidence register or current-state summary must represent the Phase II.3 seal as:

`HISTORICALLY_VALID / CURRENTLY_SUPERSEDED`

It must not report Phase II.3 heartbeat-veto behavior as a current production property unless the live source pin returns to a revision that actually implements that behavior and it is revalidated.

This annotation does not invalidate the historical 0043A/B/C results. It changes their current applicability.

## Evidence Epoch rule extracted from this incident

Future evidence should be `VALID` only while all material source/dependency pins and declared preconditions still match the live compatibility epoch. A material pin divergence should make the old claim `SUPERSEDED`, not silently current.

This file records the incident and the governance correction only. Automated Evidence Epoch Invalidation remains a later phase after Phase II.5 is closed.
