#!/usr/bin/env python3
"""Observer-only governance layer for the REI local Shadow closed loop.

This module never writes canonical state and never grants promotion authority.
It post-processes one completed Shadow cycle into bounded, auditable observer data:
lineage quality, failure recurrence, multi-hypothesis state, calibration placeholders,
prospective sealing status, and an advisory promotion gate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROTOCOL_VERSION = "REI-CLP/3.0-observer"
OBSERVER_MODE = True
CANONICAL_WRITE_PERMISSION = False


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    out: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except (OSError, UnicodeError):
        return []
    for line in lines:
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            out.append(value)
    return out


def atomic_text_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    finally:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass


def atomic_json_write(path: Path, payload: Any) -> None:
    atomic_text_write(path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    existing = read_jsonl(path)
    existing.append(payload)
    atomic_text_write(path, "".join(canonical_json(item) + "\n" for item in existing))


def normalize_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip().lower())[:500]


def normalize_provenance(value: Any) -> str:
    text = normalize_text(value)
    text = re.sub(r"https?://(www\.)?", "", text)
    text = re.sub(r"[?#].*$", "", text)
    return text or "unknown"


def collect_evidence(cycle: dict[str, Any]) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    for wrapper in cycle.get("proposals", []) if isinstance(cycle.get("proposals"), list) else []:
        if not isinstance(wrapper, dict):
            continue
        role = str(wrapper.get("role", "unknown"))
        proposal = wrapper.get("proposal") if isinstance(wrapper.get("proposal"), dict) else {}
        for item in proposal.get("evidence", []) if isinstance(proposal.get("evidence"), list) else []:
            if not isinstance(item, dict):
                continue
            try:
                independence = float(item.get("independence", 0.0))
            except (TypeError, ValueError):
                independence = 0.0
            evidence.append({
                "role": role,
                "claim": str(item.get("claim", ""))[:500],
                "support": str(item.get("support", ""))[:500],
                "provenance": str(item.get("provenance", "unknown"))[:500],
                "normalized_provenance": normalize_provenance(item.get("provenance")),
                "declared_independence": max(0.0, min(independence, 1.0)),
            })
    return evidence


def lineage_summary(evidence: list[dict[str, Any]]) -> dict[str, Any]:
    if not evidence:
        return {"total_evidence": 0, "unique_lineages": 0, "duplicate_fraction": 1.0,
                "mean_declared_independence": 0.0, "lineage_score": 0.0, "lineage_groups": []}
    groups: dict[str, list[dict[str, Any]]] = {}
    for item in evidence:
        groups.setdefault(item["normalized_provenance"], []).append(item)
    total = len(evidence)
    unique = len(groups)
    mean_ind = sum(item["declared_independence"] for item in evidence) / total
    uniqueness = unique / total
    score = max(0.0, min(1.0, mean_ind * uniqueness))
    return {"total_evidence": total, "unique_lineages": unique,
            "duplicate_fraction": round(1.0 - uniqueness, 6),
            "mean_declared_independence": round(mean_ind, 6), "lineage_score": round(score, 6),
            "lineage_groups": [{"provenance": key, "count": len(items),
                                "roles": sorted({item["role"] for item in items})}
                               for key, items in sorted(groups.items())]}


def collect_hypotheses(cycle: dict[str, Any]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    hypotheses: list[dict[str, Any]] = []
    synthesis = cycle.get("synthesis") if isinstance(cycle.get("synthesis"), dict) else {}
    primary = str(synthesis.get("claim", "")).strip()
    if primary:
        seen.add(normalize_text(primary))
        hypotheses.append({"kind": "primary", "text": primary[:800], "source": "synthesis"})
    for wrapper in cycle.get("proposals", []) if isinstance(cycle.get("proposals"), list) else []:
        if not isinstance(wrapper, dict):
            continue
        proposal = wrapper.get("proposal") if isinstance(wrapper.get("proposal"), dict) else {}
        role = str(wrapper.get("role", "unknown"))
        for text in proposal.get("counterarguments", []) if isinstance(proposal.get("counterarguments"), list) else []:
            clean = str(text).strip()
            key = normalize_text(clean)
            if clean and key not in seen:
                seen.add(key)
                hypotheses.append({"kind": "alternative", "text": clean[:800], "source": role})
    return hypotheses[:24]


def failure_signals(cycle: dict[str, Any]) -> list[str]:
    signals: list[str] = []
    gate = cycle.get("deterministic_gate") if isinstance(cycle.get("deterministic_gate"), dict) else {}
    review = cycle.get("review") if isinstance(cycle.get("review"), dict) else {}
    for value in gate.get("reasons", []) if isinstance(gate.get("reasons"), list) else []:
        if str(value).strip(): signals.append("gate:" + str(value).strip())
    for value in review.get("required_revisions", []) if isinstance(review.get("required_revisions"), list) else []:
        if str(value).strip(): signals.append("revision:" + str(value).strip())
    for value in cycle.get("runtime_errors", []) if isinstance(cycle.get("runtime_errors"), list) else []:
        if str(value).strip(): signals.append("runtime:" + str(value).strip())
    return signals


def recurrence_summary(signals: list[str], prior: list[dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    prior_counts: Counter[str] = Counter()
    for row in prior:
        for item in row.get("failures", []) if isinstance(row.get("failures"), list) else []:
            if isinstance(item, dict) and item.get("fingerprint"): prior_counts[str(item["fingerprint"])] += 1
    failures: list[dict[str, Any]] = []
    max_recurrence = 0
    for signal in sorted(set(signals)):
        fp = hashlib.sha256(normalize_text(signal).encode("utf-8")).hexdigest()[:20]
        recurrence = prior_counts[fp] + 1
        max_recurrence = max(max_recurrence, recurrence)
        failures.append({"fingerprint": fp, "signal": signal[:800], "recurrence_count": recurrence})
    return {"failure_count": len(failures), "max_recurrence": max_recurrence,
            "recurrent_failure_present": max_recurrence >= 2}, failures


def calibration_assertions(cycle: dict[str, Any]) -> list[dict[str, Any]]:
    assertions: list[dict[str, Any]] = []
    for wrapper in cycle.get("proposals", []) if isinstance(cycle.get("proposals"), list) else []:
        if not isinstance(wrapper, dict): continue
        proposal = wrapper.get("proposal") if isinstance(wrapper.get("proposal"), dict) else {}
        try: uncertainty = float(proposal.get("uncertainty", 1.0))
        except (TypeError, ValueError): uncertainty = 1.0
        assertions.append({"source": str(wrapper.get("role", "unknown")),
                           "stated_confidence": round(max(0.0, min(1.0, 1.0 - uncertainty)), 6),
                           "outcome_status": "PENDING_OUTCOME", "calibration_eligible": False,
                           "reason": "No independently observed prospective outcome is attached to this cycle."})
    review = cycle.get("review") if isinstance(cycle.get("review"), dict) else {}
    if "score" in review:
        assertions.append({"source": "internal_review_score", "stated_confidence": review.get("score"),
                           "outcome_status": "NOT_A_PROBABILITY_FORECAST", "calibration_eligible": False,
                           "reason": "Internal review score must not be reinterpreted as calibrated probability."})
    return assertions


def prospective_seal(cycle: dict[str, Any]) -> dict[str, Any]:
    synthesis = cycle.get("synthesis") if isinstance(cycle.get("synthesis"), dict) else {}
    explicit = synthesis.get("prospective_prediction")
    if not isinstance(explicit, str) or not explicit.strip():
        return {"status": "NO_EXPLICIT_PROSPECTIVE_PREDICTION", "externally_witnessed": False,
                "timestamp_independence_verified": False, "promotion_effect": "NONE"}
    payload = {"prediction": explicit.strip()[:1500], "cycle_id": cycle.get("cycle_id"),
               "sealed_at": utc_now(), "source_audit_hash": cycle.get("audit_hash")}
    return {"status": "SEALED_INTERNAL_ONLY", "seal_sha256": digest(payload), "payload": payload,
            "externally_witnessed": False, "timestamp_independence_verified": False,
            "promotion_effect": "NONE_UNTIL_FUTURE_OUTCOME"}


def build_observer(cycle: dict[str, Any], recurrence_ledger: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
    evidence = collect_evidence(cycle)
    lineage = lineage_summary(evidence)
    hypotheses = collect_hypotheses(cycle)
    recurrence, failures = recurrence_summary(failure_signals(cycle), recurrence_ledger)
    seal = prospective_seal(cycle)
    base_gate = bool((cycle.get("deterministic_gate") or {}).get("shadow_accepted"))
    runtime_clean = not bool(cycle.get("runtime_errors"))
    advisory_conditions = {"base_shadow_gate_passed": base_gate, "runtime_clean": runtime_clean,
                           "lineage_score_at_least_0_35": lineage["lineage_score"] >= 0.35,
                           "no_high_recurrence_failure": recurrence["max_recurrence"] < 3}
    eligible = all(advisory_conditions.values())
    observer = {"schema_version": 1, "protocol_version": PROTOCOL_VERSION, "observer_mode": OBSERVER_MODE,
                "canonical_write_permission": CANONICAL_WRITE_PERMISSION, "cycle_id": cycle.get("cycle_id"),
                "source_cycle_audit_hash": cycle.get("audit_hash"), "generated_at": utc_now(),
                "lineage": lineage,
                "hypothesis_state": {"policy": "maintain_multiple_hypotheses_until_evidence_justifies_collapse",
                                     "quantum_claim": False, "hypotheses": hypotheses},
                "failure_recurrence": recurrence,
                "calibration": {"status": "OBSERVER_ONLY", "assertions": calibration_assertions(cycle)},
                "prospective_seal": seal,
                "spectral_observer": {"applicable": False,
                                      "reason": "No explicit numeric time-series payload is present in this Shadow cycle.",
                                      "promotion_effect": "NONE"},
                "promotion_gate_v2": {"mode": "OBSERVER_ONLY", "conditions": advisory_conditions,
                                      "recommendation": "ELIGIBLE_FOR_FURTHER_REVIEW" if eligible else "HOLD",
                                      "may_promote_canonical": False, "may_grant_reality_validation": False,
                                      "may_grant_ascension": False},
                "boundaries": ["HighScore != Promotion", "RepeatedEvidence != IndependentEvidence",
                               "InternalPrediction != IndependentProspectiveEvidence",
                               "HypothesisMixture != QuantumSuperposition", "ObserverOutput != CanonicalAuthority"]}
    recurrence_record = {"schema_version": 1, "protocol_version": PROTOCOL_VERSION,
                         "cycle_id": cycle.get("cycle_id"), "timestamp": observer["generated_at"],
                         "failures": failures, "canonical_write_permission": False}
    observer["observer_sha256"] = digest(observer)
    return observer, recurrence_record


def process(home: Path) -> int:
    state_dir = home / "state"
    output_dir = home / "outputs" / "closed_loop_v2"
    cycle = read_json(state_dir / "last_cycle.json")
    if not cycle:
        print("VNEXT_OBSERVER_NO_CYCLE"); return 0
    cycle_id = str(cycle.get("cycle_id", "")).strip()
    if not cycle_id:
        print("VNEXT_OBSERVER_FAILED_CLOSED: cycle_id missing"); return 2
    observer_dir = state_dir / "vnext_observer"
    recurrence_path = observer_dir / "failure_recurrence.jsonl"
    prior = read_jsonl(recurrence_path)
    if any(str(row.get("cycle_id")) == cycle_id for row in prior):
        print("VNEXT_OBSERVER_ALREADY_PROCESSED"); return 0
    observer, recurrence_record = build_observer(cycle, prior)
    atomic_json_write(output_dir / f"vnext_{cycle_id}.json", observer)
    atomic_json_write(observer_dir / "latest.json", observer)
    append_jsonl(recurrence_path, recurrence_record)
    append_jsonl(observer_dir / "calibration_ledger.jsonl", {"schema_version": 1,
        "protocol_version": PROTOCOL_VERSION, "cycle_id": cycle_id, "timestamp": observer["generated_at"],
        "assertions": observer["calibration"]["assertions"], "canonical_write_permission": False})
    append_jsonl(observer_dir / "lineage_ledger.jsonl", {"schema_version": 1,
        "protocol_version": PROTOCOL_VERSION, "cycle_id": cycle_id, "timestamp": observer["generated_at"],
        "lineage": observer["lineage"], "canonical_write_permission": False})
    atomic_json_write(observer_dir / "protocol_state.json", {"protocol_version": PROTOCOL_VERSION,
        "observer_mode": True, "last_cycle_id": cycle_id, "last_observer_sha256": observer["observer_sha256"],
        "updated_at": observer["generated_at"], "canonical_write_permission": False})
    print("VNEXT_OBSERVER_SUCCESS")
    print(f"Cycle: {cycle_id}")
    print(f"Lineage score: {observer['lineage']['lineage_score']}")
    print(f"Max failure recurrence: {observer['failure_recurrence']['max_recurrence']}")
    print(f"Promotion advisory: {observer['promotion_gate_v2']['recommendation']}")
    print("Observer mode: TRUE")
    print("Canonical write permission: FALSE")
    return 0


def self_test() -> int:
    sample = {"cycle_id": "test-cycle", "audit_hash": "a" * 64,
              "deterministic_gate": {"shadow_accepted": True, "reasons": []}, "runtime_errors": [],
              "proposals": [{"role": "evidence", "proposal": {"uncertainty": 0.2,
                "counterarguments": ["alt"], "evidence": [
                    {"claim": "c1", "support": "s", "provenance": "https://example.com/a", "independence": 0.8},
                    {"claim": "c2", "support": "s", "provenance": "https://example.com/a?x=1", "independence": 0.8}]}},
                {"role": "ood", "proposal": {"uncertainty": 0.4, "counterarguments": ["shift"],
                 "evidence": [{"claim": "c3", "support": "s", "provenance": "model_inference", "independence": 0.2}]}}],
              "synthesis": {"claim": "primary"}, "review": {"score": 0.8, "required_revisions": []}}
    observer, record = build_observer(sample, [])
    assert observer["observer_mode"] is True and observer["canonical_write_permission"] is False
    assert observer["lineage"]["total_evidence"] == 3
    assert observer["hypothesis_state"]["quantum_claim"] is False
    assert observer["promotion_gate_v2"]["may_promote_canonical"] is False
    assert record["cycle_id"] == "test-cycle"
    print("VNEXT_OBSERVER_SELF_TEST_SUCCESS"); return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="REI vNext observer-only governance layer")
    parser.add_argument("--home", default=os.getenv("REI_HOME", r"C:\REI-Shadow"))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    return self_test() if args.self_test else process(Path(args.home))


if __name__ == "__main__":
    raise SystemExit(main())
