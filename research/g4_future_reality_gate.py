#!/usr/bin/env python3
"""Deterministic protocol-integrity dry run for REI-Ω G4 Future Reality Gate."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class Registration:
    protocol_version: str
    generator_hash: str
    model_hash: str
    data_cutoff: str
    target: str
    horizon: str
    prediction: float
    prediction_interval: tuple[float, float]
    scoring_rule: str
    baseline_spec: str
    analysis_plan: str
    constitution_hash: str
    created_at: str


def canonical_bytes(reg: Registration) -> bytes:
    return json.dumps(
        asdict(reg), sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def commitment(reg: Registration) -> str:
    return hashlib.sha256(canonical_bytes(reg)).hexdigest()


def register(reg: Registration, outcome=None) -> dict:
    # Temporal honesty rule: registration must not contain the future outcome.
    if outcome is not None:
        raise ValueError("future outcome forbidden during registration")
    lo, hi = reg.prediction_interval
    if lo > reg.prediction or reg.prediction > hi:
        raise ValueError("prediction must lie inside frozen interval")
    return {
        "state": "REGISTERED",
        "g4_status": "OPEN",
        "commitment": commitment(reg),
        "real_prospective_resolutions": 0,
    }


def verify_commitment(reg: Registration, expected: str) -> bool:
    return commitment(reg) == expected


def dry_run_score(reg: Registration, synthetic_outcome: float) -> dict:
    # This exists only to test that the frozen scoring machinery is deterministic.
    # It is explicitly not a G4 resolution.
    err = reg.prediction - synthetic_outcome
    if reg.scoring_rule != "squared_error":
        raise ValueError("dry run supports frozen squared_error only")
    return {
        "protocol_integrity": "PASS",
        "synthetic_score": err * err,
        "g4_status": "OPEN",
        "counts_as_real_resolution": False,
    }


def main():
    reg = Registration(
        protocol_version="g4-v0.1",
        generator_hash="genesis-generator-frozen-v1",
        model_hash="model-frozen-v1",
        data_cutoff="2030-01-01T00:00:00Z",
        target="synthetic_future_scalar",
        horizon="30d",
        prediction=10.0,
        prediction_interval=(8.0, 12.0),
        scoring_rule="squared_error",
        baseline_spec="frozen_constant_baseline_v1",
        analysis_plan="score exactly once after external outcome provenance is available",
        constitution_hash="rei-omega-constitution-v1",
        created_at="2030-01-01T00:00:00Z",
    )

    ticket = register(reg)
    assert ticket["state"] == "REGISTERED"
    assert ticket["g4_status"] == "OPEN"
    assert ticket["real_prospective_resolutions"] == 0
    assert len(ticket["commitment"]) == 64
    assert verify_commitment(reg, ticket["commitment"])

    # Tampering after commitment must be detectable.
    tampered = Registration(**{**asdict(reg), "prediction": 11.0})
    assert not verify_commitment(tampered, ticket["commitment"])

    # Outcome leakage at registration must fail.
    try:
        register(reg, outcome=9.5)
    except ValueError:
        leakage_rejected = True
    else:
        leakage_rejected = False
    assert leakage_rejected

    dry = dry_run_score(reg, synthetic_outcome=9.5)
    assert dry["protocol_integrity"] == "PASS"
    assert dry["g4_status"] == "OPEN"
    assert dry["counts_as_real_resolution"] is False

    print("G4_PROTOCOL_INTEGRITY=PASS")
    print(f"REGISTRATION_COMMITMENT={ticket['commitment']}")
    print("OUTCOME_LEAKAGE=REJECTED")
    print("TAMPER_DETECTION=PASS")
    print("SYNTHETIC_DRY_RUN=PASS")
    print("SYNTHETIC_DRY_RUN_COUNTS_AS_G4=false")
    print("REAL_PROSPECTIVE_RESOLUTIONS=0")
    print("G4_STATUS=OPEN")


if __name__ == "__main__":
    main()
