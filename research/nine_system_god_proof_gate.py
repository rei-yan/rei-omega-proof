#!/usr/bin/env python3
"""Internal pre-ascension God Proof gate for REI-Ω Nine-System candidate.

This gate proves only that the candidate is internally mapped, fail-closed, and
still blocked from self-ascension. It deliberately cannot convert internal CI
into independent external validation, RealityValidated, canonical promotion,
or ASCENSION_GRANTED.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "runtime" / "nine-system-contract-v1.json"
INTERFACE_MAP = ROOT / "research" / "NINE_SYSTEM_INTERFACE_MAP_V1.json"
GOD_SOURCE_OVERLAY = ROOT / "research" / "NINE_SYSTEM_GOD_SOURCE_OVERLAY_V1.json"
GOD_SOURCE_REGISTRY = ROOT / "runtime" / "god-source-registry-v1.json"
GOD_SOURCE_CONTRACT = ROOT / "runtime" / "god-source-contract-v1.json"
GOD_SOURCE_RECEIPT = ROOT / "runtime" / "god-source-receipt-schema-v1.json"

REQUIRED_INTERNAL_ANCHORS = [
    ROOT / ".github" / "workflows" / "g2-proof.yml",
    ROOT / ".github" / "workflows" / "god-source-registry-sanity.yml",
    ROOT / "research" / "COMPARATIVE_FRONTIER_ARENA.md",
    ROOT / "research" / "REALITY_ASCENSION_LIMIT.md",
    ROOT / "research" / "CLAIM_SCOPE_EVIDENCE_GRAPH.md",
    ROOT / "research" / "GOD_SOURCE_UNIFIED_REGISTRY_V1.md",
    ROOT / "runtime" / "Safe-AutoUpdate-V193.ps1",
    ROOT / "runtime" / "continuous-reality-contract-v1.json",
    GOD_SOURCE_REGISTRY,
    GOD_SOURCE_CONTRACT,
    GOD_SOURCE_RECEIPT,
]

EXPECTED_EXTERNAL_BLOCKERS = [
    "REALITY_VALIDATED_FALSE",
    "INDEPENDENT_EXTERNAL_VALIDATION_OPEN",
    "G3_G4_G5_G6_EXTERNAL_GATES_OPEN",
    "GOD_SOURCE_EXTERNAL_ARBITRATION_INCOMPLETE",
]


def main() -> int:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    mapping = json.loads(INTERFACE_MAP.read_text(encoding="utf-8"))
    source_overlay = json.loads(GOD_SOURCE_OVERLAY.read_text(encoding="utf-8"))
    source_registry = json.loads(GOD_SOURCE_REGISTRY.read_text(encoding="utf-8"))
    source_contract = json.loads(GOD_SOURCE_CONTRACT.read_text(encoding="utf-8"))
    source_receipt = json.loads(GOD_SOURCE_RECEIPT.read_text(encoding="utf-8"))
    gate = contract["ascension_requirements"]

    # Internal structural readiness.
    assert contract["status"] == "CANDIDATE_ASCENSION_PENDING"
    assert contract["interface_overlays"] == ["research/NINE_SYSTEM_GOD_SOURCE_OVERLAY_V1.json"]
    assert contract["candidate_extensions"]["god_source_phase1"] == "CI_VERIFIED_EXTERNAL_BINDINGS_PENDING"
    assert gate["nine_of_nine_responsibilities_defined"] is True
    assert gate["nine_of_nine_interfaces_mapped"] is True
    assert gate["no_authority_expansion"] is True
    assert gate["rollback_available"] is True
    assert gate["ledger_traceability"] is True
    assert gate["canonical_mainline_touched"] is False
    assert gate["existing_runtime_regression"] is False

    # Self-certification must remain impossible.
    assert contract["canonical_mainline_write_permission"] is False
    assert contract["automatic_ascension_permission"] is False
    assert contract["automatic_authority_expansion_permission"] is False
    assert gate["god_proof_independent_check"] == "PENDING"
    assert gate["reality_validated"] is False
    assert gate["ascension_granted"] is False

    for path in REQUIRED_INTERNAL_ANCHORS:
        assert path.exists(), f"missing God Proof anchor: {path.relative_to(ROOT)}"

    systems = mapping["systems"]
    assert len(systems) == 9
    source = next(s for s in systems if s["id"] == 7)
    proof = next(s for s in systems if s["id"] == 9)

    # Base map remains historical; the synchronized overlay records the verified
    # Phase 1 source-registry advance without pretending external bindings exist.
    source_text = " | ".join(source["promotion_blockers"])
    assert source["maturity"] == source_overlay["precondition_maturity"]
    assert "Unified GPT/Claude/local source registry is not yet implemented" in source_text
    assert "Unified GPT/Claude/local source registry is not yet implemented" in source_overlay["resolved_blockers"]
    assert source_overlay["status"] == "PHASE1_CI_VERIFIED_RUNTIME_BINDINGS_PENDING"
    assert source_overlay["candidate_maturity"] == "PARTIAL_UNIFIED_REGISTRY_EXTERNAL_BINDINGS_OPEN"
    remaining = " | ".join(source_overlay["remaining_blockers"])
    assert "Real GPT runtime binding remains pending" in remaining
    assert "Real Claude runtime binding remains pending" in remaining
    assert "GPT/Claude disagreement arbitration is not yet a synchronized runtime capability" in remaining
    assert source_overlay["runtime_external_bindings"] == "PENDING"
    assert source_overlay["reality_validated"] is False
    assert source_overlay["ascension_granted"] is False

    assert source_registry["registry_id"] == "REI-GOD-SOURCE/1.0"
    assert source_registry["policy"]["source_power_does_not_equal_source_authority"] is True
    assert source_registry["arbitration_boundary"]["preserve_disagreement"] is True
    assert source_registry["arbitration_boundary"]["provider_diversity_establishes_independence"] is False
    assert source_contract["runtime_binding"]["gpt"] == "PENDING_EXTERNAL_BINDING"
    assert source_contract["runtime_binding"]["claude"] == "PENDING_EXTERNAL_BINDING"
    assert source_contract["runtime_binding"]["unified_arbitration_runtime"] == "PENDING"
    assert source_contract["authority_ceiling"]["source_may_set_reality_validated"] is False
    assert source_contract["authority_ceiling"]["source_may_grant_ascension"] is False
    assert source_receipt["authority_constraints"]["may_set_reality_validated"] is False
    assert source_receipt["authority_constraints"]["may_grant_ascension"] is False

    proof_text = " | ".join(proof["promotion_blockers"])
    assert "Independent external validation remains open" in proof_text
    assert "G3/G4/G5/G6 and later external gates are not closed by internal CI" in proof_text

    blockers = list(EXPECTED_EXTERNAL_BLOCKERS)
    result = {
        "status": "NINE_SYSTEM_INTERNAL_PROOF_READY_WITH_EXTERNAL_BLOCKERS",
        "internal_mapping": "9/9",
        "god_source_phase1": "CI_VERIFIED_EXTERNAL_BINDINGS_PENDING",
        "internal_non_regression_contract": "READY_FOR_CI_CONFIRMATION",
        "god_proof_independent_check": "PENDING",
        "reality_validated": False,
        "ascension_granted": False,
        "blockers": blockers,
        "authority_expansion": False,
        "canonical_mainline_touched": False,
    }

    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    print("GOD_SOURCE_PHASE1_ACCEPTED_AS_BOUNDED_CANDIDATE_OVERLAY")
    print("GOD_SOURCE_EXTERNAL_ARBITRATION_REMAINS_INCOMPLETE")
    print("NINE_SYSTEM_GOD_PROOF_PRECHECK_SUCCESS")
    print("ASCENSION_MUST_REMAIN_NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
