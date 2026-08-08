#!/usr/bin/env python3
"""Deterministic protocol-integrity dry run for REI-Ω G5 Original Discovery Gate.

This script deliberately cannot certify G5. It only checks commitment integrity,
anti-retuning rules, hidden-evidence gating, baseline freezing, and novelty-review
requirements on a synthetic example.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json


@dataclass(frozen=True)
class DiscoveryRegistration:
    protocol_version: str
    domain: str
    data_cutoff: str
    training_evidence_hash: str
    generator_hash: str
    baseline_hash: str
    candidate_type: str
    candidate_definition: str
    operationalization: str
    predicted_gain: float
    falsification_plan: str
    scoring_rule: str
    minimum_improvement_margin: float
    novelty_scope: str
    created_at: str


def canonical(reg: DiscoveryRegistration) -> bytes:
    payload = json.dumps(asdict(reg), sort_keys=True, separators=(",", ":"))
    return payload.encode("utf-8")


def commitment(reg: DiscoveryRegistration) -> str:
    return hashlib.sha256(canonical(reg)).hexdigest()


def can_resolve(*, outcome_available: bool, external_provenance: bool,
                no_leakage: bool, independent_novelty_review: bool) -> bool:
    return all((outcome_available, external_provenance, no_leakage,
                independent_novelty_review))


def eligible_for_g5(*, commit_valid: bool, hidden_unavailable_at_generation: bool,
                    no_leakage: bool, frozen_scoring: bool,
                    baseline_complete: bool, margin_met: bool,
                    falsification_executed: bool, external_provenance: bool,
                    novelty_status: str) -> bool:
    return all((
        commit_valid,
        hidden_unavailable_at_generation,
        no_leakage,
        frozen_scoring,
        baseline_complete,
        margin_met,
        falsification_executed,
        external_provenance,
        novelty_status == "IndependentlySupportedNovel",
    ))


def score(candidate_error: float, baseline_error: float) -> float:
    """Positive means the candidate improves over the frozen baseline."""
    return baseline_error - candidate_error


def main() -> None:
    reg = DiscoveryRegistration(
        protocol_version="g5-v0.1",
        domain="synthetic-protocol-dry-run",
        data_cutoff="2026-08-08T00:00:00Z",
        training_evidence_hash="training-evidence-frozen",
        generator_hash="generator-frozen",
        baseline_hash="baseline-frozen",
        candidate_type="NewRepresentation",
        candidate_definition="synthetic_candidate_phi",
        operationalization="fit frozen linear head over phi",
        predicted_gain=0.20,
        falsification_plan="challenge on wider withheld synthetic range",
        scoring_rule="absolute_error_reduction",
        minimum_improvement_margin=0.10,
        novelty_scope="NewToSystemOnly",
        created_at="2026-08-08T00:00:00Z",
    )

    c0 = commitment(reg)
    assert len(c0) == 64
    assert c0 == commitment(reg)

    mutated = DiscoveryRegistration(**{
        **asdict(reg),
        "candidate_definition": "changed_after_outcome",
    })
    assert commitment(mutated) != c0

    # No outcome means no resolution.
    assert not can_resolve(
        outcome_available=False,
        external_provenance=True,
        no_leakage=True,
        independent_novelty_review=True,
    )

    # Synthetic scoring can test mechanics, but it cannot establish external novelty.
    improvement = score(candidate_error=0.30, baseline_error=0.55)
    assert improvement >= reg.minimum_improvement_margin

    # A candidate that is only new to the system is intentionally not G5-certified.
    assert not eligible_for_g5(
        commit_valid=True,
        hidden_unavailable_at_generation=True,
        no_leakage=True,
        frozen_scoring=True,
        baseline_complete=True,
        margin_met=True,
        falsification_executed=True,
        external_provenance=True,
        novelty_status="NewToSystemOnly",
    )

    # Missing independent novelty review blocks certification even if everything else looks good.
    assert not can_resolve(
        outcome_available=True,
        external_provenance=True,
        no_leakage=True,
        independent_novelty_review=False,
    )

    print("G5_ORIGINAL_DISCOVERY_GATE_INTEGRITY=PASS")
    print(f"REGISTRATION_SHA256={c0}")
    print(f"SYNTHETIC_IMPROVEMENT={improvement:.6f}")
    print("SYNTHETIC_RESULT=DRY_RUN_ONLY")
    print("G5_STATUS=OPEN")
    print("EXTERNALLY_HIDDEN_DISCOVERIES=0")
    print("INDEPENDENTLY_SUPPORTED_NOVEL_DISCOVERIES=0")


if __name__ == "__main__":
    main()
