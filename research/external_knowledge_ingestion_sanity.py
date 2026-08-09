#!/usr/bin/env python3
import copy
import json
from pathlib import Path

from external_knowledge_ingestion_gate import (
    manifest_digest,
    validate_manifest,
    verify_manifest_digest,
)

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "external_knowledge_sources" / "chatgpt-share-6a788050-b2c0-83e8-bb30-2b3c1ba6fe08.json"

manifest = json.loads(SOURCE.read_text(encoding="utf-8"))

# The exact user-provided locator is registered, but unresolved content carries no claims.
assert manifest["locator"] == "https://chatgpt.com/share/6a788050-b2c0-83e8-bb30-2b3c1ba6fe08"
assert manifest["state"] == "REGISTERED_UNRESOLVED"
assert manifest["parsed_claims"] == []
assert validate_manifest(manifest).valid
assert verify_manifest_digest(manifest)

# A locator alone cannot smuggle in a claim.
smuggled = copy.deepcopy(manifest)
smuggled["parsed_claims"] = [{"normalized_proposition": "unseen content invented"}]
assert not validate_manifest(smuggled).valid

# An unresolved source cannot pretend it has a content hash or frozen snapshot.
fake_capture = copy.deepcopy(manifest)
fake_capture["content_sha256"] = "a" * 64
fake_capture["snapshot_path"] = "research/external_knowledge_snapshots/fake.txt"
assert not validate_manifest(fake_capture).valid

# Ingestion cannot grant itself authority.
privileged = copy.deepcopy(manifest)
privileged["authority"] = 1
assert not validate_manifest(privileged).valid

# Ingestion cannot close external gates or declare frontier status.
self_promoted = copy.deepcopy(manifest)
self_promoted["g6_pass"] = True
assert not validate_manifest(self_promoted).valid

# A genuine frozen capture is structurally admissible, but still unverified and authority-zero.
captured = copy.deepcopy(manifest)
captured.pop("manifest_sha256")
captured["state"] = "CAPTURED_FROZEN"
captured["retrieval"]["status"] = "CAPTURED"
captured["retrieval"]["failure_reason"] = None
captured["content_sha256"] = "b" * 64
captured["snapshot_path"] = "research/external_knowledge_snapshots/example.txt"
captured["manifest_sha256"] = manifest_digest(captured)
assert validate_manifest(captured).valid
assert verify_manifest_digest(captured)

# Parsed claims remain candidate-only and provenance-bound to the frozen capture.
parsed = copy.deepcopy(captured)
parsed.pop("manifest_sha256")
parsed["state"] = "PARSED_CANDIDATE"
parsed["parsed_claims"] = [
    {
        "claim_id": "claim-001",
        "source_id": parsed["source_id"],
        "capture_hash": parsed["content_sha256"],
        "exact_support_span_or_locator": "snapshot:example.txt#L1-L2",
        "normalized_proposition": "example candidate proposition",
        "scope": "synthetic sanity fixture",
        "uncertainty": "HIGH",
        "parser_version": "sanity-1",
        "counterevidence_refs": [],
        "conflict_state": "UNASSESSED",
        "authority": 0,
        "certification": "UNVERIFIED",
        "canonical": False,
        "promotion": None,
    }
]
parsed["manifest_sha256"] = manifest_digest(parsed)
assert validate_manifest(parsed).valid
assert verify_manifest_digest(parsed)

# A parsed claim cannot self-promote into G6/world-best/canonical truth.
promoted_claim = copy.deepcopy(parsed)
promoted_claim["parsed_claims"][0]["promotion"] = "WORLD_BEST"
assert not validate_manifest(promoted_claim).valid

print("EXTERNAL_KNOWLEDGE_INGESTION_GATE_READY")
print("REGISTERED_SOURCE_REMAINS_UNRESOLVED")
print("NO_UNSEEN_CLAIMS_IMPORTED")
