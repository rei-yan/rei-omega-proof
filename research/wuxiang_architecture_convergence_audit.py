#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research"
WORKFLOWS = ROOT / ".github" / "workflows"

CORE = {
    "EVOLUTION_QUALITY_GOVERNOR": {
        "doc": "research/WUXIANG_EVOLUTION_QUALITY_GOVERNOR.md",
        "py": "research/wuxiang_evolution_quality_governor.py",
        "data": "research/wuxiang_evolution_quality_governor.example.json",
        "workflow": ".github/workflows/wuxiang-evolution-quality-governor-sanity.yml",
    },
    "GODSLAYER": {
        "doc": "research/WUXIANG_GODSLAYER_EPISTEMIC_KERNEL.md",
        "py": "research/wuxiang_godslayer_epistemic_kernel.py",
        "data": "research/wuxiang_godslayer_epistemic_kernel.example.json",
        "workflow": ".github/workflows/wuxiang-godslayer-epistemic-kernel-sanity.yml",
    },
    "GENESIS_EXTINCTION": {
        "doc": "research/WUXIANG_GENESIS_EXTINCTION_DUALITY_KERNEL.md",
        "py": "research/wuxiang_genesis_extinction_duality_kernel.py",
        "data": "research/wuxiang_genesis_extinction_duality_kernel.example.json",
        "workflow": ".github/workflows/wuxiang-genesis-extinction-duality-sanity.yml",
    },
    "TRANSDUAL_WORLD_ECOLOGY": {
        "doc": "research/WUXIANG_TRANSDUAL_WORLD_ECOLOGY_KERNEL.md",
        "py": "research/wuxiang_transdual_world_ecology_kernel.py",
        "data": "research/wuxiang_transdual_world_ecology_kernel.example.json",
        "workflow": ".github/workflows/wuxiang-transdual-world-ecology-sanity.yml",
    },
    "RULE_GENESIS_EXTINCTION": {
        "doc": "research/WUXIANG_RULE_GENESIS_EXTINCTION_KERNEL.md",
        "py": "research/wuxiang_rule_genesis_extinction_kernel.py",
        "data": "research/wuxiang_rule_genesis_extinction_kernel.example.json",
        "workflow": ".github/workflows/wuxiang-rule-genesis-extinction-sanity.yml",
    },
    "UNIVERSAL_FALSIFIABLE_OBJECT": {
        "doc": "research/WUXIANG_UNIVERSAL_FALSIFIABLE_OBJECT_KERNEL.md",
        "py": "research/wuxiang_universal_falsifiable_object_kernel.py",
        "data": "research/wuxiang_universal_falsifiable_object_kernel.example.json",
        "workflow": ".github/workflows/wuxiang-universal-falsifiable-object-sanity.yml",
    },
    "REALITY_GAP_CLOSURE": {
        "doc": "research/WUXIANG_REALITY_GAP_CLOSURE_KERNEL.md",
        "py": "research/wuxiang_reality_gap_closure_kernel.py",
        "data": "research/wuxiang_reality_gap_closure_kernel.example.json",
        "workflow": ".github/workflows/wuxiang-reality-gap-closure-sanity.yml",
    },
    "TOTAL_CONVERGENCE": {
        "doc": "research/WUXIANG_TOTAL_CONVERGENCE_KERNEL.md",
        "py": "research/wuxiang_total_convergence_kernel.py",
        "data": "research/wuxiang_total_convergence_kernel.example.json",
        "workflow": ".github/workflows/wuxiang-total-convergence-kernel-sanity.yml",
    },
    "WUJI_UNIFIED_INTEGRATION": {
        "doc": "research/WUXIANG_WUJI_UNIFIED_INTEGRATION_KERNEL.md",
        "py": "research/wuxiang_wuji_unified_kernel.py",
        "data": "research/wuxiang_wuji_integration_map.json",
        "workflow": ".github/workflows/wuxiang-wuji-unified-integration-sanity.yml",
    },
}

CLUSTERS = {
    "EXTERNAL_EVIDENCE_PIPELINE": [
        "research/EXTERNAL_SCIENTIFIC_ELIGIBILITY_REVIEW.md",
        "research/EXTERNAL_REVIEWER_HANDOFF_KIT.md",
        "research/REVIEWER_REPRODUCIBILITY_CAPSULE.md",
        "research/EXTERNAL_REALITY_TRIAL_KIT.md",
        "research/EXTERNAL_WITNESS_NETWORK.md",
        "research/G4_G5_EXTERNAL_CHALLENGE_PACKAGE.md",
        "research/WUXIANG_REALITY_GAP_CLOSURE_KERNEL.md",
    ],
    "SUCCESSION_AND_REBIRTH": [
        "research/CLEAN_ROOM_REBIRTH.md",
        "research/CLEAN_ROOM_SUCCESSOR_TOURNAMENT.md",
        "research/MULTI_GENERATION_EVOLUTION_LEAGUE.md",
        "research/EXTERNALLY_WITNESSED_SUCCESSION.md",
        "research/REALITY_ADJUDICATED_META_EVOLUTION_KERNEL.md",
    ],
    "FALSIFICATION_AND_DEATHEYE": [
        "research/WUJI_ADVERSARIAL_EPISTEMIC_CRUCIBLE.md",
        "research/DEATHEYE_OMEGA_CONVERGENCE_KERNEL.md",
        "research/DEATHEYE_OMEGA_HYPERGRAPH_EVOLUTION_STACK.md",
        "research/DEATHEYE_OMEGA_ROBUSTNESS_SELF_FALSIFICATION_STACK.md",
        "research/WUXIANG_TOTAL_CONVERGENCE_KERNEL.md",
        "research/WUXIANG_GODSLAYER_EPISTEMIC_KERNEL.md",
    ],
    "GENESIS_AND_REPRESENTATION": [
        "research/REPRESENTATION_RUPTURE_GENESIS.md",
        "research/ONTOLOGY_CAUSAL_TRANSFER_GENESIS.md",
        "research/UNKNOWN_UNKNOWN_GENESIS.md",
        "research/DISCOVERY_GENESIS_STACK.md",
        "research/WUXIANG_GENESIS_EXTINCTION_DUALITY_KERNEL.md",
        "research/WUXIANG_TRANSDUAL_WORLD_ECOLOGY_KERNEL.md",
        "research/WUXIANG_RULE_GENESIS_EXTINCTION_KERNEL.md",
        "research/WUXIANG_UNIVERSAL_FALSIFIABLE_OBJECT_KERNEL.md",
    ],
}

EXTERNAL_DIRS = [
    ROOT / "g3" / "submissions",
    ROOT / "external" / "reality_evidence",
    RESEARCH / "external_scientific_eligibility_reviews",
]

FORBIDDEN_AUTHORITY_PATTERNS = [
    re.compile(r"RealWorldAttackAuthority\s*=\s*([1-9]\d*)"),
    re.compile(r"RealWorldActuationAuthority\s*=\s*([1-9]\d*)"),
    re.compile(r"PhysicalWorldCreationAuthority\s*=\s*([1-9]\d*)"),
    re.compile(r"PhysicalWorldDestructionAuthority\s*=\s*([1-9]\d*)"),
]


def exists(rel: str) -> bool:
    return (ROOT / rel).is_file()


def meaningful_files(path: Path) -> list[str]:
    if not path.exists() or not path.is_dir():
        return []
    out: list[str] = []
    for p in path.rglob("*"):
        if not p.is_file():
            continue
        if p.name.lower() in {"readme.md", ".gitkeep"}:
            continue
        out.append(str(p.relative_to(ROOT)))
    return sorted(out)


def scan_forbidden_authority() -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for p in RESEARCH.glob("*.md"):
        text = p.read_text(encoding="utf-8")
        for pattern in FORBIDDEN_AUTHORITY_PATTERNS:
            m = pattern.search(text)
            if m:
                findings.append({"file": str(p.relative_to(ROOT)), "match": m.group(0)})
    return findings


def main() -> None:
    counts = {
        "research_markdown": len(list(RESEARCH.glob("*.md"))),
        "research_python": len(list(RESEARCH.glob("*.py"))),
        "research_json": len(list(RESEARCH.glob("*.json"))),
        "workflows": len(list(WORKFLOWS.glob("*.yml"))) + len(list(WORKFLOWS.glob("*.yaml"))),
    }

    core_coverage = {}
    missing_core = []
    total_slots = 0
    present_slots = 0
    for capability, artifacts in CORE.items():
        status = {}
        for kind, rel in artifacts.items():
            ok = exists(rel)
            status[kind] = ok
            total_slots += 1
            present_slots += int(ok)
            if not ok:
                missing_core.append({"capability": capability, "kind": kind, "path": rel})
        core_coverage[capability] = status

    coverage_ratio = present_slots / total_slots if total_slots else 0.0

    clusters = {}
    for name, members in CLUSTERS.items():
        present = [m for m in members if exists(m)]
        clusters[name] = {
            "present_count": len(present),
            "declared_count": len(members),
            "present": present,
            "status": "COMPRESSION_REVIEW_CANDIDATE" if len(present) >= 3 else "LOW_DENSITY",
        }

    external_material = []
    for d in EXTERNAL_DIRS:
        external_material.extend(meaningful_files(d))
    external_material = sorted(set(external_material))

    forbidden = scan_forbidden_authority()

    if missing_core:
        recommendation = "REPAIR_CORE_ARTIFACT_COVERAGE_BEFORE_GROWTH"
    elif forbidden:
        recommendation = "REVOKE_CANDIDATE_SUPPORT_AND_REPAIR_AUTHORITY_BOUNDARY"
    elif not external_material:
        recommendation = "EXTERNALIZE_AND_COMPRESS_BEFORE_FURTHER_GROWTH"
    else:
        recommendation = "ADJUDICATE_EXTERNAL_MATERIAL_AND_REVIEW_COMPRESSION_BEFORE_GROWTH"

    result = {
        "protocol": "WUXIANG_ARCHITECTURE_CONVERGENCE_AUDIT",
        "audited_candidate_extensions": 112,
        "counts": counts,
        "core_artifact_coverage_ratio": round(coverage_ratio, 4),
        "core_artifact_coverage": core_coverage,
        "missing_core_artifacts": missing_core,
        "compression_review_clusters": clusters,
        "external_material_files": external_material,
        "external_material_count": len(external_material),
        "external_state": (
            "EXTERNAL_MATERIAL_PRESENT_REQUIRES_INDEPENDENT_ADJUDICATION"
            if external_material
            else "AWAITING_REAL_EXTERNAL_EVIDENCE"
        ),
        "forbidden_real_world_authority_markers": forbidden,
        "automatic_pruning_authority": 0,
        "canonical_promotion_authority": 0,
        "external_validation_authority": 0,
        "real_world_attack_authority": 0,
        "real_world_actuation_authority": 0,
        "recommendation": recommendation,
    }

    print(json.dumps(result, indent=2, sort_keys=True))

    assert coverage_ratio == 1.0, "CORE_ARTIFACT_COVERAGE_INCOMPLETE"
    assert not forbidden, "FORBIDDEN_REAL_WORLD_AUTHORITY_MARKER"
    assert result["automatic_pruning_authority"] == 0
    assert result["canonical_promotion_authority"] == 0
    assert result["external_validation_authority"] == 0

    print("ARCHITECTURE_CENSUS_READY")
    print("CORE_ARTIFACT_COVERAGE_READY")
    print("COMPRESSION_REVIEW_CLUSTERS_READY")
    print("EXTERNAL_EVIDENCE_DEBT_VISIBLE")
    print("NO_AUTOMATIC_PRUNING")
    print("NO_FORBIDDEN_REAL_WORLD_AUTHORITY_MARKERS")
    print("EXTERNAL_EVIDENCE_NOT_SELF_CERTIFIED")
    print("ARCHITECTURE_CONVERGENCE_AUDIT_READY")


if __name__ == "__main__":
    main()
