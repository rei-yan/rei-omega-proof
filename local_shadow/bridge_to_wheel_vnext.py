#!/usr/bin/env python3
"""Bridge accepted local Shadow cycles into the Divine Wheel inbox with vNext observer metadata.

Fail-closed, append-only, candidate-only. This adapter never writes canonical/main.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Iterable

PROTOCOL_VERSION = "REI-CLP/3.0-observer"
SOURCE = "OLLAMA_SHADOW_REI_NODE"
EVIDENCE_GRADE = "SHADOW_INTERNAL_ONLY"
WHEEL_STATUS = "PENDING_DIVINE_WHEEL_REVIEW"


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def read_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    if not path.exists(): return
    try: lines = path.read_text(encoding="utf-8-sig").splitlines()
    except (OSError, UnicodeError): return
    for line in lines:
        if not line.strip(): continue
        try: value = json.loads(line)
        except json.JSONDecodeError: continue
        if isinstance(value, dict): yield value


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def record_sha(record: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json({k:v for k,v in record.items() if k != "sha256"}).encode("utf-8")).hexdigest()


def cycle_is_exportable(cycle: dict[str, Any], queued: dict[str, Any]) -> bool:
    gate = cycle.get("deterministic_gate"); review = cycle.get("review")
    return bool(cycle.get("schema_version") == 2 and cycle.get("branch") == "shadow-node"
        and isinstance(gate, dict) and gate.get("shadow_accepted") is True
        and cycle.get("canonical_mainline_touched") is False and cycle.get("core_committed") is False
        and cycle.get("human_review_required") is True and isinstance(review, dict)
        and review.get("verdict") == "ACCEPT_SHADOW" and review.get("target_state") == "shadow"
        and review.get("core_write") is False and review.get("human_review_required") is True
        and queued.get("status") == "PENDING_HUMAN_REVIEW" and queued.get("core_write") is False)


def list_text(value: Any) -> str:
    return "\n".join(f"- {str(item).strip()}" for item in value if str(item).strip()) if isinstance(value, list) else ""


def build_verdict(cycle: dict[str, Any], queued: dict[str, Any], observer: dict[str, Any]) -> str:
    synthesis = cycle.get("synthesis") if isinstance(cycle.get("synthesis"), dict) else {}
    review = cycle.get("review") if isinstance(cycle.get("review"), dict) else {}
    gate = cycle.get("deterministic_gate") if isinstance(cycle.get("deterministic_gate"), dict) else {}
    promotion = observer.get("promotion_gate_v2") if isinstance(observer.get("promotion_gate_v2"), dict) else {}
    lineage = observer.get("lineage") if isinstance(observer.get("lineage"), dict) else {}
    recurrence = observer.get("failure_recurrence") if isinstance(observer.get("failure_recurrence"), dict) else {}
    sections = [f"SHADOW_CYCLE: {cycle.get('cycle_id', '')}", f"LOCAL_REVIEW: {review.get('verdict', '')}",
        f"VNEXT_PROTOCOL: {observer.get('protocol_version', '')}",
        f"VNEXT_PROMOTION_ADVISORY: {promotion.get('recommendation', 'HOLD')}",
        f"LINEAGE_SCORE: {lineage.get('lineage_score', 0.0)}",
        f"MAX_FAILURE_RECURRENCE: {recurrence.get('max_recurrence', 0)}",
        "PROPOSED_SHADOW_UPDATE:\n" + str(queued.get("proposed_shadow_update") or synthesis.get("proposed_shadow_update") or "").strip(),
        "OPEN_RISKS:\n" + list_text(synthesis.get("open_risks")), "REVIEW_REASONS:\n" + list_text(review.get("reasons")),
        "REQUIRED_REVISIONS:\n" + list_text(review.get("required_revisions")),
        "REGRESSION_CHECKS:\n" + list_text(review.get("regression_checks")),
        "LOCAL_GATE_REASONS:\n" + list_text(gate.get("reasons")),
        "BOUNDARY: internal Shadow proposal + observer metadata only; not reality validation, independent replication, ascension, or canonical promotion."]
    return "\n\n".join(section for section in sections if not section.endswith(":\n"))


def find_cycle(home: Path, cycle_id: str) -> dict[str, Any] | None:
    cycle = read_json(home / "outputs" / "closed_loop_v2" / f"cycle_{cycle_id}.json")
    if cycle is not None: return cycle
    last_cycle = read_json(home / "state" / "last_cycle.json")
    return last_cycle if last_cycle and str(last_cycle.get("cycle_id", "")) == cycle_id else None


def find_observer(home: Path, cycle_id: str) -> dict[str, Any] | None:
    observer = read_json(home / "outputs" / "closed_loop_v2" / f"vnext_{cycle_id}.json")
    if observer is None: observer = read_json(home / "state" / "vnext_observer" / "latest.json")
    if not observer or str(observer.get("cycle_id", "")) != cycle_id: return None
    if observer.get("protocol_version") != PROTOCOL_VERSION or observer.get("observer_mode") is not True: return None
    if observer.get("canonical_write_permission") is not False: return None
    return observer


def atomic_write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(canonical_json(record) + "\n" for record in records)
    fd, temporary_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text); handle.flush(); os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    finally:
        try: os.unlink(temporary_name)
        except FileNotFoundError: pass


def compact_observer(observer: dict[str, Any]) -> dict[str, Any]:
    lineage = observer.get("lineage") if isinstance(observer.get("lineage"), dict) else {}
    recurrence = observer.get("failure_recurrence") if isinstance(observer.get("failure_recurrence"), dict) else {}
    hypotheses = observer.get("hypothesis_state") if isinstance(observer.get("hypothesis_state"), dict) else {}
    seal = observer.get("prospective_seal") if isinstance(observer.get("prospective_seal"), dict) else {}
    promotion = observer.get("promotion_gate_v2") if isinstance(observer.get("promotion_gate_v2"), dict) else {}
    spectral = observer.get("spectral_observer") if isinstance(observer.get("spectral_observer"), dict) else {}
    return {"observer_sha256": observer.get("observer_sha256"), "lineage_score": lineage.get("lineage_score", 0.0),
        "unique_lineages": lineage.get("unique_lineages", 0), "duplicate_fraction": lineage.get("duplicate_fraction", 1.0),
        "max_failure_recurrence": recurrence.get("max_recurrence", 0),
        "recurrent_failure_present": recurrence.get("recurrent_failure_present", False),
        "hypothesis_count": len(hypotheses.get("hypotheses", [])) if isinstance(hypotheses.get("hypotheses"), list) else 0,
        "prospective_seal_status": seal.get("status", "UNKNOWN"), "spectral_applicable": spectral.get("applicable", False),
        "promotion_advisory": promotion.get("recommendation", "HOLD"), "promotion_mode": promotion.get("mode", "OBSERVER_ONLY")}


def bridge(home: Path) -> int:
    queue_path = home / "state" / "promotion_queue.jsonl"; inbox_path = home / "divine_wheel_inbox.jsonl"
    queued_records = list(read_jsonl(queue_path))
    if not queued_records:
        print("NO_ACCEPTED_SHADOW_INPUT"); print("Nothing bridged; rejected or revise-only cycles remain local.");
        print("Canonical mainline touched: FALSE"); return 0
    existing_records = list(read_jsonl(inbox_path))
    known_sha = {str(r.get("sha256")) for r in existing_records if isinstance(r.get("sha256"), str)}
    known_cycle_ids = {str(r.get("source_cycle_id")) for r in existing_records if r.get("source_cycle_id")}
    appended = skipped_unsafe = skipped_missing_observer = 0
    for queued in queued_records:
        cycle_id = str(queued.get("cycle_id", "")).strip()
        if not cycle_id or cycle_id in known_cycle_ids: continue
        cycle = find_cycle(home, cycle_id)
        if cycle is None or not cycle_is_exportable(cycle, queued): skipped_unsafe += 1; continue
        observer = find_observer(home, cycle_id)
        if observer is None: skipped_missing_observer += 1; continue
        synthesis = cycle.get("synthesis") if isinstance(cycle.get("synthesis"), dict) else {}
        input_claim = str(synthesis.get("claim") or queued.get("proposed_shadow_update") or f"Accepted Shadow proposal from cycle {cycle_id}").strip()
        source_audit_hash = str(cycle.get("audit_hash") or queued.get("audit_hash") or "")
        record: dict[str, Any] = {"schema_version": 2, "protocol_version": PROTOCOL_VERSION, "observer_mode": True,
            "timestamp": cycle.get("completed_at") or queued.get("created_at"), "source": SOURCE,
            "source_model": os.getenv("REI_MODEL", "rei-local-node-vnext"), "evidence_grade": EVIDENCE_GRADE,
            "input_claim": input_claim, "shadow_verdict": build_verdict(cycle, queued, observer), "reality_validated": False,
            "independent_replication": False, "ascension_permission": False, "canonical_write_permission": False,
            "wheel_status": WHEEL_STATUS, "source_cycle_id": cycle_id, "cycle_id": cycle_id,
            "source_audit_hash": source_audit_hash, "source_sha": source_audit_hash if len(source_audit_hash) == 64 else None,
            "provenance": {"branch": "shadow-node", "local_runtime_revision": cycle.get("runtime_revision"),
                           "observer_protocol": PROTOCOL_VERSION, "observer_sha256": observer.get("observer_sha256")},
            "vnext_observer": compact_observer(observer)}
        record["sha256"] = record_sha(record)
        if record["sha256"] in known_sha: continue
        existing_records.append(record); known_sha.add(record["sha256"]); known_cycle_ids.add(cycle_id); appended += 1
    if appended:
        atomic_write_jsonl(inbox_path, existing_records); print("SHADOW_VNEXT_BRIDGE_SUCCESS"); print(f"New accepted records: {appended}"); print(f"Inbox: {inbox_path}")
    else:
        print("NO_NEW_SHADOW_INPUT"); print("Nothing bridged; all records were duplicate, unsafe, or lacked vNext observer metadata.")
    if skipped_unsafe: print(f"Fail-closed records skipped: {skipped_unsafe}")
    if skipped_missing_observer: print(f"Missing-observer records skipped: {skipped_missing_observer}")
    print(f"Protocol: {PROTOCOL_VERSION}"); print("Observer mode: TRUE"); print("Canonical mainline touched: FALSE"); return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="REI Shadow -> Divine Wheel vNext observer bridge")
    parser.add_argument("--home", default=os.getenv("REI_HOME", r"C:\REI-Shadow")); args = parser.parse_args()
    return bridge(Path(args.home))

if __name__ == "__main__": raise SystemExit(main())
