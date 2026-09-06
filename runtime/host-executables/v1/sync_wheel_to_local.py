#!/usr/bin/env python3
"""Pull bounded Divine Wheel receipts into the local REI Shadow state.

This is a one-way receipt transport. It never writes canonical state, never
promotes Shadow output, and treats every cloud receipt as correlated internal
review rather than independent or reality evidence.
"""

from __future__ import annotations

import argparse
import json
import os
import secrets
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_URL = (
    "https://raw.githubusercontent.com/rei-yan/rei-omega-proof/"
    "shadow-node/shadow/divine_wheel_receipts.jsonl"
)
ALLOWED_DECISIONS = {
    "ACKNOWLEDGED_INTERNAL",
    "REVISE_SHADOW",
    "REJECT_SHADOW",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def atomic_text_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(
        f".{path.name}.{os.getpid()}.{time.time_ns()}.{secrets.token_hex(3)}.tmp"
    )
    try:
        with temporary.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def atomic_json_write(path: Path, value: Any) -> None:
    atomic_text_write(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def parse_jsonl(text: str, *, strict: bool) -> tuple[list[dict[str, Any]], list[str]]:
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"line_{line_number}:invalid_json:{exc.msg}")
            continue
        if not isinstance(value, dict):
            errors.append(f"line_{line_number}:not_object")
            continue
        records.append(value)
    if strict and errors:
        raise RuntimeError("local feedback ledger is malformed: " + "; ".join(errors[:5]))
    return records, errors


def valid_receipt(record: dict[str, Any]) -> tuple[bool, str]:
    source_sha = str(record.get("source_sha256", ""))
    receipt_id = str(record.get("receipt_id", ""))
    checks = [
        (record.get("schema_version") == 1, "schema_version"),
        (
            len(source_sha) == 64
            and all(character in "0123456789abcdef" for character in source_sha.lower()),
            "source_sha256",
        ),
        (receipt_id == f"wheel-{source_sha}", "receipt_id"),
        (record.get("decision") in ALLOWED_DECISIONS, "decision"),
        (record.get("evidence_grade") == "CORRELATED_INTERNAL_REVIEW", "evidence_grade"),
        (record.get("wheel_status") == "DIVINE_WHEEL_REVIEWED", "wheel_status"),
        (record.get("reality_validated") is False, "reality_validated"),
        (record.get("independent_replication") is False, "independent_replication"),
        (record.get("ascension_granted") is False, "ascension_granted"),
        (record.get("canonical_write_permission") is False, "canonical_write_permission"),
        (record.get("canonical_state") == "UNCHANGED", "canonical_state"),
    ]
    failed = [name for passed, name in checks if not passed]
    return not failed, ",".join(failed)


def fetch_receipts(url: str, timeout: int) -> str | None:
    headers = {
        "Accept": "application/vnd.github.raw+json",
        "User-Agent": "REI-Wheel-To-Local/1.0",
    }
    token = os.getenv("GITHUB_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read().decode("utf-8-sig")
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise


def sync(home: Path, url: str, timeout: int = 30) -> int:
    state_dir = home / "state"
    ledger_path = state_dir / "cloud_feedback.jsonl"
    state_path = state_dir / "cloud_feedback_sync_state.json"
    rejection_path = state_dir / "cloud_feedback_rejections.jsonl"
    state_dir.mkdir(parents=True, exist_ok=True)

    try:
        local_text = ledger_path.read_text(encoding="utf-8-sig") if ledger_path.exists() else ""
        local_records, _ = parse_jsonl(local_text, strict=True)
        remote_text = fetch_receipts(url, timeout)
        if remote_text is None:
            atomic_json_write(state_path, {
                "schema_version": 1,
                "checked_at": utc_now(),
                "status": "NO_REMOTE_RECEIPT_LEDGER",
                "new_receipts": 0,
                "total_receipts": len(local_records),
                "canonical_mainline_touched": False,
            })
            print("NO_CLOUD_WHEEL_RECEIPTS")
            print("Canonical mainline touched: FALSE")
            return 0

        remote_records, parse_errors = parse_jsonl(remote_text, strict=False)
        known_ids = {str(item.get("receipt_id")) for item in local_records}
        known_source = {str(item.get("source_sha256")) for item in local_records}
        appended: list[dict[str, Any]] = []
        rejected: list[dict[str, Any]] = []

        for item in remote_records:
            valid, reason = valid_receipt(item)
            if not valid:
                rejected.append({
                    "rejected_at": utc_now(),
                    "reason": reason,
                    "receipt_id": item.get("receipt_id"),
                    "source_sha256": item.get("source_sha256"),
                })
                continue
            receipt_id = str(item["receipt_id"])
            source_sha = str(item["source_sha256"])
            if receipt_id in known_ids or source_sha in known_source:
                continue
            appended.append(item)
            known_ids.add(receipt_id)
            known_source.add(source_sha)

        if parse_errors:
            rejected.extend({"rejected_at": utc_now(), "reason": error} for error in parse_errors)
        if rejected:
            existing = rejection_path.read_text(encoding="utf-8") if rejection_path.exists() else ""
            additions = "".join(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n" for item in rejected)
            atomic_text_write(rejection_path, existing + additions)

        if appended:
            merged = local_records + appended
            text = "".join(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n" for item in merged)
            atomic_text_write(ledger_path, text)
        else:
            merged = local_records

        atomic_json_write(state_path, {
            "schema_version": 1,
            "checked_at": utc_now(),
            "status": "SYNCED",
            "new_receipts": len(appended),
            "total_receipts": len(merged),
            "rejected_rows": len(rejected),
            "canonical_mainline_touched": False,
        })
        print("WHEEL_TO_LOCAL_SYNC_SUCCESS")
        print(f"New receipts: {len(appended)}")
        print(f"Total local receipts: {len(merged)}")
        print("Canonical mainline touched: FALSE")
        return 0
    except (OSError, UnicodeError, urllib.error.URLError, TimeoutError, RuntimeError) as exc:
        atomic_json_write(state_path, {
            "schema_version": 1,
            "checked_at": utc_now(),
            "status": "FAILED_RETRYABLE",
            "error": f"{type(exc).__name__}: {exc}",
            "canonical_mainline_touched": False,
        })
        print(f"WHEEL_TO_LOCAL_SYNC_RETRYABLE: {type(exc).__name__}: {exc}")
        print("Cached feedback retained; canonical mainline touched: FALSE")
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Pull bounded Divine Wheel receipts to local Shadow")
    parser.add_argument("--home", default=os.getenv("REI_HOME", r"C:\REI-Shadow"))
    parser.add_argument("--url", default=os.getenv("REI_WHEEL_RECEIPTS_URL", DEFAULT_URL))
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args()
    return sync(Path(args.home), args.url, max(5, args.timeout))


if __name__ == "__main__":
    raise SystemExit(main())
