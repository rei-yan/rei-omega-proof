#!/usr/bin/env python3
"""Mutation control for the canonical mainline observation guard.

This is deliberately small: the production PowerShell guard must accept an
unchanged pair of SHAs and must fail non-zero when the observed main SHA changes.
A checker that always prints 'untouched' cannot pass this test.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUARD = ROOT / "runtime" / "REI-Canonical-Mainline-Observation-V1.ps1"
UNCHANGED = "1" * 40
MUTATED = "2" * 40


def shell() -> str:
    for name in ("pwsh", "powershell", "powershell.exe"):
        found = shutil.which(name)
        if found:
            return found
    raise RuntimeError("PowerShell executable unavailable")


def run_compare(before: str, after: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            shell(),
            "-NoProfile",
            "-File",
            str(GUARD),
            "-Mode",
            "Compare",
            "-BeforeSha",
            before,
            "-AfterSha",
            after,
        ],
        text=True,
        capture_output=True,
        check=False,
    )


def main() -> int:
    control = run_compare(UNCHANGED, UNCHANGED)
    assert control.returncode == 0, control.stdout + control.stderr
    assert "CANONICAL_MAINLINE_UNTOUCHED_BY_RUNTIME" in control.stdout

    mutant = run_compare(UNCHANGED, MUTATED)
    assert mutant.returncode != 0, "mutation survived: changed main was accepted"
    combined = mutant.stdout + mutant.stderr
    assert "CANONICAL_MAINLINE_TOUCHED_BY_RUNTIME" in combined

    print("CANONICAL_MAINLINE_OBSERVATION_CONTROL=PASS")
    print("MUTATION_CHANGED_MAIN_KILLED=TRUE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
