#!/usr/bin/env python3
"""Push only the local Divine Wheel inbox to GitHub shadow-node.

The transport intentionally stages one allow-listed file. It never force-pushes,
never stages canonical/main files, and first pulls remote receipt changes.
"""

from __future__ import annotations

import argparse
import os
import secrets
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path


BRANCH = "shadow-node"
TARGET = Path("shadow") / "divine_wheel_inbox.jsonl"


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


def sync(home: Path, repo: Path) -> int:
    print("REI Shadow GitHub Sync starting...")
    if not shutil.which("git"):
        print("FAILED_CLOSED: git is not available in PATH.")
        return 2

    source = home / "divine_wheel_inbox.jsonl"
    if not source.exists():
        print("NO_NEW_SHADOW_INPUT")
        print("Nothing to push.")
        return 0

    try:
        source_text = source.read_text(encoding="utf-8-sig")
        run_git(repo, "rev-parse", "--is-inside-work-tree")
        current = run_git(repo, "branch", "--show-current").stdout.strip()
        if current != BRANCH:
            raise RuntimeError(f"expected branch {BRANCH}, found {current or 'DETACHED'}")

        # Refuse to hide or rewrite unrelated user changes.
        staged = run_git(repo, "diff", "--cached", "--name-only").stdout.splitlines()
        unrelated_staged = [name for name in staged if name != TARGET.as_posix()]
        if unrelated_staged:
            raise RuntimeError("unrelated staged changes present: " + ", ".join(unrelated_staged))

        run_git(repo, "pull", "--rebase", "origin", BRANCH)
        target = repo / TARGET
        atomic_text_write(target, source_text)
        run_git(repo, "add", "--", TARGET.as_posix())

        changed = run_git(repo, "diff", "--cached", "--quiet", "--", TARGET.as_posix(), check=False)
        if changed.returncode == 0:
            print("NO_NEW_SHADOW_INPUT")
            print("Nothing to push.")
            print("Canonical mainline touched: FALSE")
            return 0
        if changed.returncode != 1:
            raise RuntimeError("unable to inspect staged Shadow inbox")

        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        run_git(repo, "commit", "--only", "-m", f"shadow: sync Divine Wheel inbox {stamp}", "--", TARGET.as_posix())
        run_git(repo, "push", "origin", BRANCH)
        head = run_git(repo, "rev-parse", "HEAD").stdout.strip()
        print("SHADOW_SYNC_SUCCESS")
        print(f"Branch: {BRANCH}")
        print(f"Head: {head}")
        print("Canonical mainline touched: FALSE")
        return 0
    except (OSError, UnicodeError, RuntimeError) as exc:
        print(f"SHADOW_SYNC_FAILED_RETRYABLE: {type(exc).__name__}: {exc}")
        print("No force push; canonical mainline touched: FALSE")
        return 2


def main() -> int:
    parser = argparse.ArgumentParser(description="Push allow-listed Shadow inbox to GitHub")
    parser.add_argument("--home", default=os.getenv("REI_HOME", r"C:\REI-Shadow"))
    parser.add_argument("--repo", default=os.getenv("REI_GIT_REPO", ""))
    args = parser.parse_args()
    home = Path(args.home)
    repo = Path(args.repo) if args.repo else home
    return sync(home, repo)


if __name__ == "__main__":
    raise SystemExit(main())
