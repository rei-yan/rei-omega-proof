#!/usr/bin/env python3
"""Finite, bounded representation-rupture experiment for REI-Ω∞.

This module demonstrates one conservative transition:
1) preserve failure of the existing grammar,
2) propose a primitive only from a preauthorized finite constructor set,
3) freeze and test that proposal,
4) keep authority at zero and external gates open.

It is a synthetic research experiment, not a real-world actuation system.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from typing import Callable

from beyond_limit_genesis_forge import forge


@dataclass(frozen=True)
class ThresholdCandidate:
    threshold: float
    authority: float = 0.0
    certification: str = "UNVERIFIED"
    canonical: bool = False
    external_gate_closed: bool = False

    def predict(self, x: float) -> float:
        return -1.0 if x < self.threshold else 1.0


FROZEN_THRESHOLDS = (-0.50, -0.25, -0.10, 0.0, 0.10, 0.25, 0.50)
TRAIN_X = (-1.0, -0.75, -0.50, -0.25, 0.0, 0.25, 0.50, 0.75, 1.0)
HOLDOUT_X = (-1.20, -0.90, -0.60, -0.30, 0.15, 0.45, 0.80, 1.10)
WIDER_X = tuple(i / 20 for i in range(-40, 41))


def mse_predict(predict: Callable[[float], float], truth: Callable[[float], float], xs: tuple[float, ...]) -> float:
    return sum((predict(x) - truth(x)) ** 2 for x in xs) / len(xs)


def max_error_predict(predict: Callable[[float], float], truth: Callable[[float], float], xs: tuple[float, ...]) -> float:
    return max(abs(predict(x) - truth(x)) for x in xs)


def residual_jump_signature(truth: Callable[[float], float], baseline_predict: Callable[[float], float]) -> dict:
    points = sorted(TRAIN_X)
    residuals = [(x, truth(x) - baseline_predict(x)) for x in points]
    jumps = []
    for (xa, ra), (xb, rb) in zip(residuals, residuals[1:]):
        jumps.append((abs(rb - ra), xa, xb, ra, rb))
    size, xa, xb, ra, rb = max(jumps)
    return {
        "max_residual_jump": size,
        "between": [xa, xb],
        "residual_before": ra,
        "residual_after": rb,
        "suggests_local_discontinuity": size >= 0.5,
    }


def select_threshold_candidate(truth: Callable[[float], float]) -> dict:
    scored = []
    for threshold in FROZEN_THRESHOLDS:
        candidate = ThresholdCandidate(threshold)
        train = mse_predict(candidate.predict, truth, TRAIN_X)
        heldout = mse_predict(candidate.predict, truth, HOLDOUT_X)
        # Frozen ranking: train, heldout, |threshold|, threshold.
        # The final tie-break is deterministic and fixed before seeing challenge outcomes.
        scored.append((train, heldout, abs(threshold), threshold, candidate))

    train, heldout, _, threshold, candidate = min(scored, key=lambda row: row[:4])
    wider = max_error_predict(candidate.predict, truth, WIDER_X)
    status = (
        "CANDIDATE_PRIMITIVE_PASSES_INTERNAL_FROZEN_TEST"
        if wider <= 0.20
        else "ARCHIVE_FAILURE"
    )
    return {
        "constructor": "StepThreshold",
        "threshold": threshold,
        "frozen_candidate_set": list(FROZEN_THRESHOLDS),
        "train_mse": train,
        "heldout_mse": heldout,
        "wider_max_error": wider,
        "status": status,
        "authority": candidate.authority,
        "certification": candidate.certification,
        "canonical": candidate.canonical,
        "external_gate_closed": candidate.external_gate_closed,
    }


def rupture_experiment(name: str, truth: Callable[[float], float]) -> dict:
    baseline = forge(name, truth)
    result = {
        "world": name,
        "baseline_status": baseline["status"],
        "baseline_family": baseline["selected_family"],
        "failure_preserved": baseline["status"] == "ABSTAIN",
        "rupture_triggered": False,
        "proposal": None,
        "final_status": baseline["status"],
    }

    if baseline["status"] != "ABSTAIN":
        return result

    # The current forge object does not expose coefficients, so for this finite
    # demonstration the rupture trigger is conservatively based on the frozen
    # baseline failure itself. Residual diagnostics are computed against a fixed
    # zero reference only as a descriptive signature, not as certification.
    signature = residual_jump_signature(truth, lambda _x: 0.0)
    result["residual_signature"] = signature

    if not signature["suggests_local_discontinuity"]:
        result["final_status"] = "ABSTAIN_NO_PREAUTHORIZED_RUPTURE"
        return result

    result["rupture_triggered"] = True
    proposal = select_threshold_candidate(truth)
    result["proposal"] = proposal
    result["final_status"] = proposal["status"]
    return result


def main() -> None:
    step_ood = lambda x: -1.0 if x < 0 else 1.0

    # A narrow spike is intentionally outside the bounded threshold constructor.
    # Even if rupture is triggered by a sharp residual, the frozen constructor
    # should fail wider challenge and remain non-certified.
    spike_ood = lambda x: 1.0 if abs(x) <= 0.10 else -1.0

    step = rupture_experiment("step_ood", step_ood)
    spike = rupture_experiment("spike_ood", spike_ood)

    assert step["baseline_status"] == "ABSTAIN"
    assert step["failure_preserved"] is True
    assert step["rupture_triggered"] is True
    assert step["proposal"] is not None
    assert step["proposal"]["threshold"] == 0.0
    assert step["proposal"]["status"] == "CANDIDATE_PRIMITIVE_PASSES_INTERNAL_FROZEN_TEST"
    assert step["proposal"]["authority"] == 0.0
    assert step["proposal"]["certification"] == "UNVERIFIED"
    assert step["proposal"]["canonical"] is False
    assert step["proposal"]["external_gate_closed"] is False

    assert spike["baseline_status"] == "ABSTAIN"
    assert spike["failure_preserved"] is True
    assert spike["rupture_triggered"] is True
    assert spike["proposal"] is not None
    assert spike["proposal"]["status"] == "ARCHIVE_FAILURE"
    assert spike["proposal"]["authority"] == 0.0
    assert spike["proposal"]["external_gate_closed"] is False

    output = {
        "representation_rupture_genesis": {
            "step_ood": step,
            "spike_ood": spike,
            "claim_boundary": {
                "external_validity": False,
                "g3_g13_pass": False,
                "canonical_promotion": False,
                "world_best": False,
                "world_unique": False,
                "invincible": False,
                "unrestricted_self_invention": False,
            },
        }
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
