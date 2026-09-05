#!/usr/bin/env python3
"""Fail-closed sanity checks for the REI-Ω nine-system candidate contract."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "runtime" / "nine-system-contract-v1.json"


def main() -> int:
    data = json.loads(CONTRACT.read_text(encoding="utf-8"))

    assert data["contract_id"] == "REI-NINE/1.0"
    assert data["status"] == "CANDIDATE_ASCENSION_PENDING"
    assert data["candidate_pull_request"] == 28
    assert data["candidate_head_ref"] == "rei-v193-reconcile"

    systems = data["systems"]
    assert len(systems) == 9, "exactly nine candidate systems are required"
    assert [s["id"] for s in systems] == list(range(1, 10))
    assert len({s["name_zh"] for s in systems}) == 9
    assert len({s["name_en"] for s in systems}) == 9
    assert all(s["role"].strip() for s in systems)

    expected = ["input", "state", "decision", "output", "failure", "evidence"]
    assert data["required_interface_fields"] == expected

    assert data["canonical_mainline_write_permission"] is False
    assert data["automatic_ascension_permission"] is False
    assert data["automatic_authority_expansion_permission"] is False
    assert data["existing_runtime_must_remain_unchanged"] is True

    gate = data["ascension_requirements"]
    assert gate["canonical_mainline_touched"] is False
    assert gate["existing_runtime_regression"] is False
    assert gate["nine_of_nine_interfaces_mapped"] is False
    assert gate["god_proof_independent_check"] == "PENDING"
    assert gate["reality_validated"] is False
    assert gate["ascension_granted"] is False

    rules = set(data["hard_rules"])
    required_rules = {
        "NineSystemDefinitionDoesNotEqualAscension",
        "CapabilityGainDoesNotEqualRealityValidation",
        "SourcePowerDoesNotEqualSourceAuthority",
        "NoSacredFinalForm",
        "RealityVetoRemainsAbsolute",
        "CandidateArchitectureMayBeRejected",
    }
    assert required_rules.issubset(rules)

    print("NINE_SYSTEM_SANITY_SUCCESS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
