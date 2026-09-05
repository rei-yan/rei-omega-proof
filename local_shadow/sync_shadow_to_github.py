#!/usr/bin/env python3
"""Sync allow-listed local Shadow + runtime parity artifacts to GitHub shadow-node.

The transport is deliberately narrow:
- shadow/divine_wheel_inbox.jsonl mirrors the local Shadow inbox when it changes.
- shadow/local_runtime_parity.json mirrors only a compact receipt for the newest
  local closed-loop cycle, never the raw cycle log.
- shadow/local_runtime_parity_receipts.jsonl is append-only and deduplicated by
  source_sha256.

It never force-pushes, never stages canonical/main files, and always pulls the
remote shadow-node branch before composing the outgoing commit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BRANCH = "shadow-node"
TARGET_INBOX = Path("shadow") / "divine_wheel_inbox.jsonl"
TARGET_PARITY = Path("shadow") / "local_runtime_parity.json"
TARGET_PARITY_LEDGER = Path("shadow") / "local_runtime_parity_receipts.jsonl"
ALLOWLIST = {TARGET_INBOX.as_posix(), TARGET_PARITY.as_posix(), TARGET_PARITY_LEDGER.as_posix()}


def run_git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if check and completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip()
        raise RuntimeError(f"git {' '.join(args)} failed: {detail}")
    return completed


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


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object in {path}")
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def first(payload: dict[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        if key in payload and payload[key] is not None:
            return payload[key]
    return default


def latest_cycle_file(runtime_home: Path) -> Path | None:
    cycle_dir = runtime_home / "outputs" / "closed_loop_v2"
    candidates = list(cycle_dir.glob("cycle_*.json")) if cycle_dir.exists() else []
    if candidates:
        return max(candidates, key=lambda path: path.stat().st_mtime_ns)
    fallback = runtime_home / "state" / "last_cycle.json"
    return fallback if fallback.exists() else None


def build_parity_receipt(home: Path, runtime_home: Path) -> dict[str, Any] | None:
    source = latest_cycle_file(runtime_home)
    if source is None:
        return None

    payload = load_json(source)
    deterministic_gate = payload.get("deterministic_gate")
    if not isinstance(deterministic_gate, dict):
        deterministic_gate = {}
    resilience = payload.get("resilience")
    if not isinstance(resilience, dict):
        resilience = {}

    context_state: dict[str, Any] = {}
    context_path = home / "context" / "sync_state.json"
    if context_path.exists():
        try:
            context_state = load_json(context_path)
        except (OSError, UnicodeError, ValueError, json.JSONDecodeError):
            context_state = {}

    source_sha = sha256_file(source)
    runtime_errors = payload.get("runtime_errors")
    if not isinstance(runtime_errors, list):
        runtime_errors = [] if runtime_errors in (None, "") else [runtime_errors]

    source_cycle_id = str(
        first(payload, "cycle_id", "cycle", "id", default=source.stem)
    )
    receipt = {
        "schema_version": 1,
        "receipt_type": "LOCAL_RUNTIME_PARITY",
        "source_cycle_id": source_cycle_id,
        "source_file": source.name,
        "source_sha256": source_sha,
        "source_last_write_utc": datetime.fromtimestamp(
            source.stat().st_mtime, tz=timezone.utc
        ).isoformat(),
        "observed_at_utc": utc_now(),
        "candidate_pull_request": first(context_state, "pull_request", default=28),
        "candidate_head_ref": first(context_state, "head_ref", default="rei-v193-reconcile"),
        "candidate_head_sha": first(context_state, "head_sha", default=None),
        "runtime_status": first(
            payload,
            "status",
            "runtime_status",
            "cycle_status",
            "result",
            default="UNKNOWN",
        ),
        "shadow_accepted": first(
            deterministic_gate,
            "shadow_accepted",
            default=first(payload, "shadow_accepted", default=None),
        ),
        "shadow_version_before": first(payload, "shadow_version_before", default=None),
        "shadow_version_after": first(payload, "shadow_version_after", default=None),
        "canonical_mainline_touched": bool(
            first(payload, "canonical_mainline_touched", default=False)
        ),
        "core_committed": bool(first(payload, "core_committed", default=False)),
        "human_review_required": bool(
            first(payload, "human_review_required", default=True)
        ),
        "runtime_errors_count": len(runtime_errors),
        "rollback_checkpoint": first(
            resilience,
            "rollback_checkpoint",
            default=first(payload, "rollback_checkpoint", default=None),
        ),
        "committed_checkpoint": first(
            resilience,
            "committed_checkpoint",
            default=first(payload, "committed_checkpoint", default=None),
        ),
        "canonical_write_permission": False,
        "reality_validated": bool(first(payload, "reality_validated", default=False)),
        "ascension_granted": bool(
            first(payload, "ascension_granted", "ascension_permission", default=False)
        ),
    }
    return receipt


def append_receipt_if_new(path: Path, receipt: dict[str, Any]) -> bool:
    source_sha = str(receipt["source_sha256"])
    if path.exists():
        with path.open("r", encoding="utf-8-sig", errors="replace") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    existing = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(existing, dict) and existing.get("source_sha256") == source_sha:
                    return False
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(receipt, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    return True


def sync(home: Path, runtime_home: Path, repo: Path) -> int:
    print("REI Shadow + Sync Parity GitHub transport starting...")
    if not shutil.which("git"):
        print("FAILED_CLOSED: git is not available in PATH.")
        return 2

    local_inbox = home / "divine_wheel_inbox.jsonl"

    try:
        run_git(repo, "rev-parse", "--is-inside-work-tree")
        current = run_git(repo, "branch", "--show-current").stdout.strip()
        if current != BRANCH:
            raise RuntimeError(f"expected branch {BRANCH}, found {current or 'DETACHED'}")

        staged = run_git(repo, "diff", "--cached", "--name-only").stdout.splitlines()
        unrelated_staged = [name for name in staged if name not in ALLOWLIST]
        if unrelated_staged:
            raise RuntimeError("unrelated staged changes present: " + ", ".join(unrelated_staged))

        run_git(repo, "pull", "--rebase", "origin", BRANCH)
        touched: list[str] = []
        parity_id: str | None = None

        if local_inbox.exists():
            inbox_text = local_inbox.read_text(encoding="utf-8-sig")
            atomic_text_write(repo / TARGET_INBOX, inbox_text)
            touched.append(TARGET_INBOX.as_posix())
        else:
            print("NO_NEW_SHADOW_INPUT: local inbox missing.")

        receipt = build_parity_receipt(home, runtime_home)
        if receipt is None:
            print("PARITY_SOURCE_MISSING: no local closed-loop cycle file found.")
        else:
            parity_id = str(receipt["source_cycle_id"])
            compact_text = json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
            atomic_text_write(repo / TARGET_PARITY, compact_text)
            append_receipt_if_new(repo / TARGET_PARITY_LEDGER, receipt)
            local_state = home / "state" / "sync_parity_receipt.json"
            atomic_text_write(local_state, compact_text)
            touched.extend([TARGET_PARITY.as_posix(), TARGET_PARITY_LEDGER.as_posix()])
            print(f"PARITY_RECEIPT_READY: {parity_id}")
            print(f"PARITY_SOURCE_SHA256: {receipt['source_sha256']}")

        if not touched:
            print("NO_NEW_SHADOW_OR_PARITY_INPUT")
            print("Canonical mainline touched: FALSE")
            return 0

        # Stage only the allow-listed paths that exist locally.
        unique_touched = [name for name in dict.fromkeys(touched) if (repo / name).exists()]
        for name in unique_touched:
            run_git(repo, "add", "--", name)

        changed = run_git(
            repo,
            "diff",
            "--cached",
            "--quiet",
            "--",
            *unique_touched,
            check=False,
        )
        if changed.returncode == 0:
            print("NO_NEW_SHADOW_OR_PARITY_INPUT")
            print("Nothing to push.")
            print("Canonical mainline touched: FALSE")
            return 0
        if changed.returncode != 1:
            raise RuntimeError("unable to inspect staged allow-listed sync artifacts")

        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        subject = (
            f"shadow: sync runtime parity {parity_id} {stamp}"
            if parity_id
            else f"shadow: sync Divine Wheel inbox {stamp}"
        )
        run_git(repo, "commit", "--only", "-m", subject, "--", *unique_touched)
        run_git(repo, "push", "origin", BRANCH)
        head = run_git(repo, "rev-parse", "HEAD").stdout.strip()
        print("SHADOW_SYNC_SUCCESS")
        if parity_id:
            print("SYNC_PARITY_PUSHED: TRUE")
            print(f"Source cycle: {parity_id}")
        print(f"Branch: {BRANCH}")
        print(f"Head: {head}")
        print("Canonical mainline touched: FALSE")
        return 0
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError, RuntimeError) as exc:
        print(f"SHADOW_SYNC_FAILED_RETRYABLE: {type(exc).__name__}: {exc}")
        print("No force push; canonical mainline touched: FALSE")
        return 2


def main() -> int:
    parser = argparse.ArgumentParser(description="Push allow-listed Shadow + parity artifacts")
    parser.add_argument("--home", default=os.getenv("REI_HOME", r"C:\REI-Shadow"))
    parser.add_argument(
        "--runtime-home", default=os.getenv("REI_RUNTIME_HOME", r"C:\REI")
    )
    parser.add_argument("--repo", default=os.getenv("REI_GIT_REPO", ""))
    args = parser.parse_args()
    home = Path(args.home)
    runtime_home = Path(args.runtime_home)
    repo = Path(args.repo) if args.repo else home
    return sync(home, runtime_home, repo)


if __name__ == "__main__":
    raise SystemExit(main())
