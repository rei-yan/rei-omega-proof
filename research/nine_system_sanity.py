#!/usr/bin/env python3
"""Fail-closed sanity checks for the REI-Ω nine-system candidate contract."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "runtime" / "nine-system-contract-v1.json"
INTERFACE_MAP = ROOT / "research" / "NINE_SYSTEM_INTERFACE_MAP_V1.json"
EXPECTED_FIELDS = ["input", "state", "decision", "output", "failure", "evidence"]


def main() -> int:
    data = json.loads(CONTRACT.read_text(encoding="utf-8"))
    mapping = json.loads(INTERFACE_MAP.read_text(encoding="utf-8"))

    assert data["contract_id"] == "REI-NINE/1.0"
    assert data["status"] == "CANDIDATE_ASCENSION_PENDING"
    assert data["candidate_pull_request"] == 28
    assert data["candidate_head_ref"] == "rei-v193-reconcile"
    assert data["interface_map"] == "research/NINE_SYSTEM_INTERFACE_MAP_V1.json"

    systems = data["systems"]
    assert len(systems) == 9, "exactly nine candidate systems are required"
    assert [s["id"] for s in systems] == list(range(1, 10))
    assert len({s["name_zh"] for s in systems}) == 9
    assert len({s["name_en"] for s in systems}) == 9
    assert all(s["role"].strip() for s in systems)
    assert data["required_interface_fields"] == EXPECTED_FIELDS

    assert mapping["contract_id"] == "REI-NINE-INTERFACE/1.0"
    assert mapping["status"] == "MAPPED_CANDIDATE_NOT_ASCENDED"
    assert mapping["candidate_pull_request"] == 28
    assert mapping["candidate_head_ref"] == "rei-v193-reconcile"
    assert mapping["required_interface_fields"] == EXPECTED_FIELDS
    assert mapping["mapping_rule"] == "Mapped != Implemented != RealityValidated != Ascended"

    mapped = mapping["systems"]
    assert len(mapped) == 9
    assert [s["id"] for s in mapped] == list(range(1, 10))
    assert [s["name_zh"] for s in mapped] == [s["name_zh"] for s in systems]
    assert [s["name_en"] for s in mapped] == [s["name_en"] for s in systems]

    for system in mapped:
        assert system["maturity"].strip()
        assert "ASCENDED" not in system["maturity"]
        assert "REALITY_VALIDATED" not in system["maturity"]
        interface = system["interface"]
        assert list(interface.keys()) == EXPECTED_FIELDS
        assert all(isinstance(interface[field], str) and interface[field].strip() for field in EXPECTED_FIELDS)
        anchors = system["anchors"]
        assert anchors, f"system {system['id']} must have real repository anchors"
        for rel in anchors:
            assert (ROOT / rel).exists(), f"missing anchor for system {system['id']}: {rel}"
        assert isinstance(system["promotion_blockers"], list)

    source = next(s for s in mapped if s["id"] == 7)
    source_blockers = " | ".join(source["promotion_blockers"])
    assert "GPT/Claude/local source registry is not yet implemented" in source_blockers
    assert "GPT/Claude disagreement arbitration is not yet a synchronized runtime capability" in source_blockers

    proof = next(s for s in mapped if s["id"] == 9)
    proof_blockers = " | ".join(proof["promotion_blockers"])
    assert "Independent external validation remains open" in proof_blockers
    assert "may not self-grant canonical promotion or ascension" in proof_blockers

    assert data["canonical_mainline_write_permission"] is False
    assert data["automatic_ascension_permission"] is False
    assert data["automatic_authority_expansion_permission"] is False
    assert data["existing_runtime_must_remain_unchanged"] is True

    gate = data["ascension_requirements"]
    assert gate["nine_of_nine_responsibilities_defined"] is True
    assert gate["nine_of_nine_interfaces_mapped"] is True
    assert gate["no_authority_expansion"] is True
    assert gate["rollback_available"] is True
    assert gate["ledger_traceability"] is True
    assert gate["canonical_mainline_touched"] is False
    assert gate["existing_runtime_regression"] is False
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
        "MappedDoesNotEqualImplemented",
    }
    assert required_rules.issubset(rules)

    print("NINE_SYSTEM_INTERFACE_MAP_9_OF_9")
    print("NINE_SYSTEM_SANITY_SUCCESS")
    print("ASCENSION_REMAINS_PENDING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
