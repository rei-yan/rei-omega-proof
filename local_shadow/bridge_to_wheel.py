#!/usr/bin/env python3
"""Bridge accepted REI Shadow V2.2 proposals into the Divine Wheel inbox.

This adapter is intentionally fail-closed. It never writes canonical state and
only exports cycles that already passed the local deterministic Shadow gate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Iterable


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
    if not path.exists():
        return
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except (OSError, UnicodeError):
        return
    for line in lines:
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            yield value


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def record_sha(record: dict[str, Any]) -> str:
    payload = {key: value for key, value in record.items() if key != "sha256"}
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def cycle_is_exportable(cycle: dict[str, Any], queued: dict[str, Any]) -> bool:
    gate = cycle.get("deterministic_gate")
    review = cycle.get("review")
    return bool(
        cycle.get("schema_version") == 2
        and cycle.get("branch") == "shadow-node"
        and isinstance(gate, dict)
        and gate.get("shadow_accepted") is True
        and cycle.get("canonical_mainline_touched") is False
        and cycle.get("core_committed") is False
        and cycle.get("human_review_required") is True
        and isinstance(review, dict)
        and review.get("verdict") == "ACCEPT_SHADOW"
        and review.get("target_state") == "shadow"
        and review.get("core_write") is False
        and review.get("human_review_required") is True
        and queued.get("status") == "PENDING_HUMAN_REVIEW"
        and queued.get("core_write") is False
    )


def list_text(value: Any) -> str:
    if not isinstance(value, list):
        return ""
    return "\n".join(f"- {str(item).strip()}" for item in value if str(item).strip())


def build_verdict(cycle: dict[str, Any], queued: dict[str, Any]) -> str:
    synthesis = cycle.get("synthesis") if isinstance(cycle.get("synthesis"), dict) else {}
    review = cycle.get("review") if isinstance(cycle.get("review"), dict) else {}
    gate = cycle.get("deterministic_gate") if isinstance(cycle.get("deterministic_gate"), dict) else {}

    sections = [
        f"SHADOW_CYCLE: {cycle.get('cycle_id', '')}",
        f"LOCAL_REVIEW: {review.get('verdict', '')}",
        "PROPOSED_SHADOW_UPDATE:\n" + str(
            queued.get("proposed_shadow_update")
            or synthesis.get("proposed_shadow_update")
            or ""
        ).strip(),
        "OPEN_RISKS:\n" + list_text(synthesis.get("open_risks")),
        "REVIEW_REASONS:\n" + list_text(review.get("reasons")),
        "REQUIRED_REVISIONS:\n" + list_text(review.get("required_revisions")),
        "REGRESSION_CHECKS:\n" + list_text(review.get("regression_checks")),
        "LOCAL_GATE_REASONS:\n" + list_text(gate.get("reasons")),
        "BOUNDARY: internal Shadow proposal only; not reality validation, "
        "independent replication, ascension, or canonical promotion.",
    ]
    return "\n\n".join(section for section in sections if not section.endswith(":\n"))


def find_cycle(home: Path, cycle_id: str) -> dict[str, Any] | None:
    cycle_path = home / "outputs" / "closed_loop_v2" / f"cycle_{cycle_id}.json"
    cycle = read_json(cycle_path)
    if cycle is not None:
        return cycle
    last_cycle = read_json(home / "state" / "last_cycle.json")
    if last_cycle and str(last_cycle.get("cycle_id", "")) == cycle_id:
        return last_cycle
    return None


def atomic_write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(canonical_json(record) + "\n" for record in records)
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


def bridge(home: Path) -> int:
    queue_path = home / "state" / "promotion_queue.jsonl"
    inbox_path = home / "divine_wheel_inbox.jsonl"

    queued_records = list(read_jsonl(queue_path))
    if not queued_records:
        print("NO_ACCEPTED_SHADOW_INPUT")
        print("Nothing bridged; rejected or revise-only cycles remain local.")
        print("Canonical mainline touched: FALSE")
        return 0

    existing_records = list(read_jsonl(inbox_path))
    known_sha = {
        str(record.get("sha256"))
        for record in existing_records
        if isinstance(record.get("sha256"), str)
    }
    known_cycle_ids = {
        str(record.get("source_cycle_id"))
        for record in existing_records
        if record.get("source_cycle_id")
    }

    appended = 0
    skipped_unsafe = 0
    for queued in queued_records:
        cycle_id = str(queued.get("cycle_id", "")).strip()
        if not cycle_id or cycle_id in known_cycle_ids:
            continue
        cycle = find_cycle(home, cycle_id)
        if cycle is None or not cycle_is_exportable(cycle, queued):
            skipped_unsafe += 1
            continue

        synthesis = cycle.get("synthesis") if isinstance(cycle.get("synthesis"), dict) else {}
        input_claim = str(
            synthesis.get("claim")
            or queued.get("proposed_shadow_update")
            or f"Accepted Shadow proposal from cycle {cycle_id}"
        ).strip()
        record: dict[str, Any] = {
            "timestamp": cycle.get("completed_at") or queued.get("created_at"),
            "source": SOURCE,
            "source_model": os.getenv("REI_MODEL", "rei-local-node:latest"),
            "evidence_grade": EVIDENCE_GRADE,
            "input_claim": input_claim,
            "shadow_verdict": build_verdict(cycle, queued),
            "reality_validated": False,
            "independent_replication": False,
            "ascension_permission": False,
            "canonical_write_permission": False,
            "wheel_status": WHEEL_STATUS,
            "source_cycle_id": cycle_id,
            "source_audit_hash": cycle.get("audit_hash") or queued.get("audit_hash"),
        }
        record["sha256"] = record_sha(record)
        if record["sha256"] in known_sha:
            continue
        existing_records.append(record)
        known_sha.add(record["sha256"])
        known_cycle_ids.add(cycle_id)
        appended += 1

    if appended:
        atomic_write_jsonl(inbox_path, existing_records)
        print("SHADOW_BRIDGE_SUCCESS")
        print(f"New accepted records: {appended}")
        print(f"Inbox: {inbox_path}")
    else:
        print("NO_NEW_SHADOW_INPUT")
        print("Nothing bridged; all records were duplicate, missing, or fail-closed.")
    if skipped_unsafe:
        print(f"Fail-closed records skipped: {skipped_unsafe}")
    print("Canonical mainline touched: FALSE")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="REI Shadow V2.2 -> Divine Wheel bridge")
    parser.add_argument("--home", default=os.getenv("REI_HOME", r"C:\REI-Shadow"))
    args = parser.parse_args()
    return bridge(Path(args.home))


if __name__ == "__main__":
    raise SystemExit(main())
