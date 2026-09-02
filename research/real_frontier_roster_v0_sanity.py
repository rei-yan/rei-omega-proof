#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REGISTRY = ROOT / "real_frontier_roster_v0.json"

ALLOWED_STATES = {
    "ROSTER_CANDIDATE",
    "SOURCE_VERIFIED",
    "COMPARABILITY_REVIEW",
    "FROZEN_FRONTIER_COMPETITOR",
    "EXCLUDED_WITH_REASON",
    "STALE_REVALIDATION_REQUIRED",
}


def fail(msg: str) -> None:
    raise AssertionError(msg)


def main() -> None:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))

    assert data["status"] == "PARTIALLY_POPULATED_NOT_FROZEN"
    assert data["g6"] == "OPEN"
    assert data["world_best"] == "UNVERIFIED"
    assert data["world_unique"] == "UNVERIFIED"
    assert data["real_world_actuation_authority"] == 0

    candidates = data["candidates"]
    assert len(candidates) >= 4

    seen = set()
    domains = set()
    for c in candidates:
        required = ["id", "name", "source_date", "source_url", "source_class", "identity", "scope", "roster_state", "comparability"]
        for key in required:
            if key not in c:
                fail(f"missing candidate field {key}: {c.get('id')}")
        if c["id"] in seen:
            fail(f"duplicate candidate id: {c['id']}")
        seen.add(c["id"])
        if c["roster_state"] not in ALLOWED_STATES:
            fail(f"invalid roster state: {c['roster_state']}")
        if c["roster_state"] == "FROZEN_FRONTIER_COMPETITOR":
            fail("v0 must not self-freeze real-world competitors")
        if c["comparability"] != "REVIEW_REQUIRED":
            fail("source verification must not bypass comparability review")
        if not c["source_url"].startswith("https://"):
            fail("source URL must be HTTPS")
        for scope in c["scope"]:
            domains.add(scope)

    assert len(domains) >= 8, "roster should remain explicitly heterogeneous"

    rules = data["hard_rules"]
    assert rules["source_verified_is_not_comparable"] is True
    assert rules["cross_domain_win_is_not_universal_superiority"] is True
    assert rules["no_overall_cross_domain_average"] is True
    assert rules["no_candidate_is_frozen_frontier_competitor_yet"] is True
    assert rules["external_coverage_audit_required"] is True

    anchors = data["evaluation_anchors"]
    assert len(anchors) >= 5
    for a in anchors:
        assert a["role"].endswith("anchor") or "anchor" in a["role"]

    print("REAL_FRONTIER_ROSTER_V0_POPULATED")
    print("CANDIDATES_SOURCE_VERIFIED_BUT_NOT_FROZEN")
    print("CROSS_DOMAIN_COMPARABILITY_GUARD_ACTIVE")
    print("G6=OPEN")
    print("WORLD_BEST=UNVERIFIED")
    print("WORLD_UNIQUE=UNVERIFIED")


if __name__ == "__main__":
    main()
