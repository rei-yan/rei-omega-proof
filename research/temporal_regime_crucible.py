#!/usr/bin/env python3
"""Finite sanity model for temporal persistence and regime-shift handling.

This synthetic crucible cannot pass G7 or G8. It only checks that a frozen
candidate preserves historical windows, cannot retune inside a lease, and
suspends current authority when a regime shift defeats the frozen claim.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from typing import Dict, List

READY = "TEMPORAL_REGIME_CRUCIBLE_READY"
INVALID = "INVALID_PROTOCOL"
PERSISTING = "PERSISTING"
DEGRADED = "DEGRADED"
REVALIDATE = "REVALIDATION_REQUIRED"
ABSTAIN = "ABSTAIN"
EXPIRED = "EXPIRED"
RETIRED = "RETIRED"


def canonical_hash(obj: object) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


@dataclass(frozen=True)
class LeaseManifest:
    lease_id: str
    candidate_hash: str
    code_hash: str
    metric: str
    max_error: float
    scope: str
    review_horizon_windows: int
    drift_limit: float
    abstention_allowed: bool

    @property
    def frozen_hash(self) -> str:
        return canonical_hash(asdict(self))


@dataclass(frozen=True)
class Window:
    window_id: str
    regime_id: str
    prediction: float
    target: float
    timestamp_index: int


@dataclass(frozen=True)
class WindowRecord:
    window_id: str
    regime_id: str
    error: float
    outcome: str
    preserved: bool


def evaluate_lease(
    manifest: LeaseManifest,
    windows: List[Window],
    expected_manifest_hash: str,
    posthoc_retune: bool = False,
    historical_record_deleted: bool = False,
) -> Dict[str, object]:
    reasons: List[str] = []
    if manifest.frozen_hash != expected_manifest_hash:
        reasons.append("MANIFEST_MUTATION_WITHIN_LEASE")
    if posthoc_retune:
        reasons.append("POSTHOC_RETUNE")
    if historical_record_deleted:
        reasons.append("HISTORICAL_RECORD_DELETION")
    if reasons:
        return {
            "state": INVALID,
            "invalidation_reasons": sorted(reasons),
            "records": [],
            "g7_status": "OPEN",
            "g8_status": "OPEN",
        }

    if not windows:
        return {"state": ABSTAIN, "records": [], "g7_status": "OPEN", "g8_status": "OPEN"}

    records: List[WindowRecord] = []
    first_regime = windows[0].regime_id
    state = PERSISTING
    regime_shift_detected = False

    for window in windows:
        error = abs(window.prediction - window.target)
        passed = error <= manifest.max_error
        if window.regime_id != first_regime:
            regime_shift_detected = True

        if passed:
            outcome = "PASS"
        else:
            outcome = "FAIL"
            if regime_shift_detected:
                state = REVALIDATE
            elif error <= manifest.max_error + manifest.drift_limit:
                state = DEGRADED
            else:
                state = REVALIDATE

        records.append(WindowRecord(window.window_id, window.regime_id, round(error, 6), outcome, True))

    if len(windows) >= manifest.review_horizon_windows and state == PERSISTING:
        state = EXPIRED

    return {
        "state": state,
        "regime_shift_detected": regime_shift_detected,
        "records": [asdict(r) for r in records],
        "historical_passes_preserved": all(r.preserved for r in records),
        "current_generalization_authority": "SUSPENDED" if state in {REVALIDATE, EXPIRED, RETIRED} else "SCOPED_ONLY",
        "g7_status": "OPEN",
        "g8_status": "OPEN",
        "real_world_actuation_authority": 0,
        "canonical": False,
    }


def run_sanity() -> Dict[str, object]:
    manifest = LeaseManifest(
        lease_id="temporal-demo-v1",
        candidate_hash="candidate-frozen-demo",
        code_hash="code-frozen-demo",
        metric="absolute_error",
        max_error=0.10,
        scope="synthetic prospective windows only",
        review_horizon_windows=5,
        drift_limit=0.15,
        abstention_allowed=True,
    )
    frozen = manifest.frozen_hash

    stable = [
        Window("W1", "regime-A", 1.00, 1.04, 1),
        Window("W2", "regime-A", 1.10, 1.15, 2),
    ]
    stable_result = evaluate_lease(manifest, stable, frozen)
    assert stable_result["state"] == PERSISTING

    shifted = stable + [Window("W3", "regime-B", 1.20, 1.75, 3)]
    shifted_result = evaluate_lease(manifest, shifted, frozen)
    assert shifted_result["regime_shift_detected"] is True
    assert shifted_result["state"] == REVALIDATE
    assert shifted_result["records"][0]["outcome"] == "PASS"
    assert shifted_result["records"][1]["outcome"] == "PASS"
    assert shifted_result["records"][2]["outcome"] == "FAIL"
    assert shifted_result["current_generalization_authority"] == "SUSPENDED"

    posthoc = evaluate_lease(manifest, shifted, frozen, posthoc_retune=True)
    assert posthoc["state"] == INVALID

    deleted = evaluate_lease(manifest, shifted, frozen, historical_record_deleted=True)
    assert deleted["state"] == INVALID

    return {
        "crucible_status": READY,
        "stable_window_test": stable_result["state"],
        "regime_shift_test": shifted_result["state"],
        "regime_shift_detected": shifted_result["regime_shift_detected"],
        "history_preserved": shifted_result["historical_passes_preserved"],
        "posthoc_retune_test": posthoc["state"],
        "history_deletion_test": deleted["state"],
        "g7_status": "OPEN",
        "g8_status": "OPEN",
        "real_world_actuation_authority": 0,
        "canonical": False,
    }


if __name__ == "__main__":
    print(json.dumps(run_sanity(), sort_keys=True, indent=2))
