#!/usr/bin/env python3
"""Fail-closed sanity checks for the REI-Ω nine-system candidate contract."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "runtime" / "nine-system-contract-v1.json"
INTERFACE_MAP = ROOT / "research" / "NINE_SYSTEM_INTERFACE_MAP_V1.json"
GOD_SOURCE_OVERLAY = ROOT / "research" / "NINE_SYSTEM_GOD_SOURCE_OVERLAY_V1.json"
EXPECTED_FIELDS = ["input", "state", "decision", "output", "failure", "evidence"]


def main() -> int:
    data = json.loads(CONTRACT.read_text(encoding="utf-8"))
    mapping = json.loads(INTERFACE_MAP.read_text(encoding="utf-8"))
    source_overlay = json.loads(GOD_SOURCE_OVERLAY.read_text(encoding="utf-8"))

    assert data["contract_id"] == "REI-NINE/1.0"
    assert data["status"] == "CANDIDATE_ASCENSION_PENDING"
    assert data["candidate_pull_request"] == 28
    assert data["candidate_head_ref"] == "rei-v193-reconcile"
    assert data["interface_map"] == "research/NINE_SYSTEM_INTERFACE_MAP_V1.json"
    assert data["interface_overlays"] == ["research/NINE_SYSTEM_GOD_SOURCE_OVERLAY_V1.json"]
    assert data["candidate_extensions"]["god_source_phase1"] == "CI_VERIFIED_EXTERNAL_BINDINGS_PENDING"

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

    # God Source Phase 1 is synchronized as an additive overlay so the 9/9 base
    # interface map remains a stable historical contract while candidate maturity
    # can advance only after its own fail-closed CI gate passes.
    source = next(s for s in mapped if s["id"] == 7)
    source_blockers = " | ".join(source["promotion_blockers"])
    assert source["maturity"] == source_overlay["precondition_maturity"]
    assert source_overlay["overlay_id"] == "REI-NINE-GOD-SOURCE-OVERLAY/1.0"
    assert source_overlay["status"] == "PHASE1_CI_VERIFIED_RUNTIME_BINDINGS_PENDING"
    assert source_overlay["applies_to_system_id"] == 7
    assert source_overlay["name_zh"] == "神源"
    assert source_overlay["name_en"] == "God Source"
    assert source_overlay["candidate_maturity"] == "PARTIAL_UNIFIED_REGISTRY_EXTERNAL_BINDINGS_OPEN"
    assert "ASCENDED" not in source_overlay["candidate_maturity"]
    assert "REALITY_VALIDATED" not in source_overlay["candidate_maturity"]
    assert "Unified GPT/Claude/local source registry is not yet implemented" in source_blockers
    assert "Unified GPT/Claude/local source registry is not yet implemented" in source_overlay["resolved_blockers"]
    remaining = " | ".join(source_overlay["remaining_blockers"])
    assert "Real GPT runtime binding remains pending" in remaining
    assert "Real Claude runtime binding remains pending" in remaining
    assert "GPT/Claude disagreement arbitration is not yet a synchronized runtime capability" in remaining
    assert "Source-specific Failure Memory runtime remains pending" in remaining
    assert source_overlay["runtime_external_bindings"] == "PENDING"
    assert source_overlay["reality_validated"] is False
    assert source_overlay["ascension_granted"] is False
    for rel in source_overlay["anchors_add"]:
        assert (ROOT / rel).exists(), f"missing God Source overlay anchor: {rel}"

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
    print("GOD_SOURCE_PHASE1_OVERLAY_SYNCED")
    print("GOD_SOURCE_EXTERNAL_BINDINGS_REMAIN_PENDING")
    print("NINE_SYSTEM_SANITY_SUCCESS")
    print("ASCENSION_REMAINS_PENDING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
