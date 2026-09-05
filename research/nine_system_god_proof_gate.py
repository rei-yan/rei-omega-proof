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

REQUIRED_INTERNAL_ANCHORS = [
    ROOT / ".github" / "workflows" / "g2-proof.yml",
    ROOT / "research" / "COMPARATIVE_FRONTIER_ARENA.md",
    ROOT / "research" / "REALITY_ASCENSION_LIMIT.md",
    ROOT / "research" / "CLAIM_SCOPE_EVIDENCE_GRAPH.md",
    ROOT / "runtime" / "Safe-AutoUpdate-V193.ps1",
    ROOT / "runtime" / "continuous-reality-contract-v1.json",
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
    gate = contract["ascension_requirements"]

    # Internal structural readiness.
    assert contract["status"] == "CANDIDATE_ASCENSION_PENDING"
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

    source_text = " | ".join(source["promotion_blockers"])
    proof_text = " | ".join(proof["promotion_blockers"])
    assert "Unified GPT/Claude/local source registry is not yet implemented" in source_text
    assert "GPT/Claude disagreement arbitration is not yet a synchronized runtime capability" in source_text
    assert "Independent external validation remains open" in proof_text
    assert "G3/G4/G5/G6 and later external gates are not closed by internal CI" in proof_text

    blockers = list(EXPECTED_EXTERNAL_BLOCKERS)
    result = {
        "status": "NINE_SYSTEM_INTERNAL_PROOF_READY_WITH_EXTERNAL_BLOCKERS",
        "internal_mapping": "9/9",
        "internal_non_regression_contract": "READY_FOR_CI_CONFIRMATION",
        "god_proof_independent_check": "PENDING",
        "reality_validated": False,
        "ascension_granted": False,
        "blockers": blockers,
        "authority_expansion": False,
        "canonical_mainline_touched": False,
    }

    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    print("NINE_SYSTEM_GOD_PROOF_PRECHECK_SUCCESS")
    print("ASCENSION_MUST_REMAIN_NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
