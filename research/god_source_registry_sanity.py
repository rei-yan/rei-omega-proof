#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "runtime" / "god-source-registry-v1.json"
CONTRACT = ROOT / "runtime" / "god-source-contract-v1.json"
RECEIPT = ROOT / "runtime" / "god-source-receipt-schema-v1.json"
NINE = ROOT / "runtime" / "nine-system-contract-v1.json"
MANIFEST = ROOT / "research" / "GOD_SOURCE_UNIFIED_REGISTRY_V1.md"

required_sources = {
    "local:rei-local-node-vnext",
    "openai:gpt",
    "anthropic:claude",
}
required_fields = {
    "source_id",
    "source_kind",
    "provider",
    "model_family",
    "model_version",
    "binding_state",
    "provenance",
    "reliability_history",
    "known_failure_modes",
    "correlation_group",
    "cost_profile",
    "latency_profile",
    "authority_level",
    "replaceable",
}

registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
nine = json.loads(NINE.read_text(encoding="utf-8"))
manifest = MANIFEST.read_text(encoding="utf-8")

assert registry["registry_id"] == "REI-GOD-SOURCE/1.0"
assert registry["canonical_mainline_write_permission"] is False
assert registry["automatic_authority_expansion_permission"] is False
assert registry["reality_validation_permission"] is False
assert registry["ascension_permission"] is False

systems = {item["id"]: item for item in nine["systems"]}
assert systems[7]["name_zh"] == "神源"
assert systems[7]["name_en"] == "God Source"

sources = registry["sources"]
ids = [item["source_id"] for item in sources]
assert len(ids) == len(set(ids)), "source_id must be unique"
assert required_sources.issubset(ids)

for source in sources:
    missing = required_fields - set(source)
    assert not missing, f"{source.get('source_id')} missing fields: {sorted(missing)}"
    assert source["authority_level"] == "SOURCE_ONLY"
    assert source["replaceable"] is True
    assert source["correlation_group"]
    assert source["known_failure_modes"]
    assert source["provenance"]
    assert source["reliability_history"]

by_id = {item["source_id"]: item for item in sources}
assert by_id["local:rei-local-node-vnext"]["binding_state"] == "BOUND_LOCAL_CANDIDATE"
assert by_id["openai:gpt"]["binding_state"] == "EXTERNAL_UNBOUND"
assert by_id["anthropic:claude"]["binding_state"] == "EXTERNAL_UNBOUND"

policy = registry["policy"]
assert policy["source_power_does_not_equal_source_authority"] is True
assert policy["disagreement_preservation_required"] is True
assert policy["correlated_sources_are_not_independent"] is True
assert policy["silent_model_substitution_forbidden"] is True
assert policy["source_specific_failure_memory_required"] is True
assert policy["unknown_source_fails_closed"] is True
assert policy["provider_label_does_not_establish_independence"] is True

arb = registry["arbitration_boundary"]
assert arb["preserve_disagreement"] is True
assert arb["majority_vote_establishes_truth"] is False
assert arb["provider_diversity_establishes_independence"] is False
assert arb["automatic_promotion_permission"] is False
assert {"God Wheel", "Shadow", "Observer", "God Proof"}.issubset(arb["downstream_consumers"])

ceiling = contract["authority_ceiling"]
assert ceiling["source_may_set_reality_validated"] is False
assert ceiling["source_may_grant_canonical_promotion"] is False
assert ceiling["source_may_grant_ascension"] is False
assert ceiling["source_may_override_god_core"] is False
assert ceiling["source_may_override_reality_veto"] is False

assert contract["runtime_binding"]["gpt"] == "PENDING_EXTERNAL_BINDING"
assert contract["runtime_binding"]["claude"] == "PENDING_EXTERNAL_BINDING"
assert contract["runtime_binding"]["unified_arbitration_runtime"] == "PENDING"

assert receipt["schema_id"] == "REI-GOD-SOURCE-RECEIPT/1.0"
assert receipt["authority_constraints"]["authority_level_must_equal"] == "SOURCE_ONLY"
assert receipt["authority_constraints"]["may_set_reality_validated"] is False
assert receipt["authority_constraints"]["may_grant_promotion"] is False
assert receipt["authority_constraints"]["may_grant_ascension"] is False
assert "SILENT_SOURCE_SUBSTITUTION" in receipt["fail_closed_on"]
assert "AUTHORITY_ESCALATION" in receipt["fail_closed_on"]

assert "RegistryDefined = TRUE" in manifest
assert "ExternalBindings = PENDING" in manifest
assert "RealityValidated = FALSE" in manifest
assert "Ascension = NO" in manifest

print("GOD_SOURCE_REGISTRY_3_OF_3")
print("GOD_SOURCE_RECEIPT_SCHEMA_READY")
print("SOURCE_POWER_NE_SOURCE_AUTHORITY")
print("DISAGREEMENT_PRESERVATION_ENABLED")
print("CORRELATED_SOURCES_NE_INDEPENDENT_SOURCES")
print("GPT_CLAUDE_BINDINGS_REMAIN_PENDING")
print("GOD_SOURCE_PHASE1_SANITY_SUCCESS")
print("ASCENSION_REMAINS_NO")
