#!/usr/bin/env python3
"""Mutation control for the poisoned-candidate rule regression suite.

The suite is informative only if removal of each encoded rejection rule makes the
suite fail. This script neutralizes one rule at a time in the exact production
`reject_reason` function and requires every mutant to be killed.
"""

from __future__ import annotations

import dataclasses

import wuxiang_supreme_consolidation_sanity as w
from poisoned_candidate_trial import run_trial

MUTATED_FIELDS = [
    "authority",
    "constitution",
    "rollback_ready",
    "self_certifies",
    "fake_external_gate_closure",
    "identity_erasure",
    "critical_regression",
    "attempts_evaluator_mutation",
]


def main() -> int:
    original = w.reject_reason
    survivors: list[str] = []

    for field in MUTATED_FIELDS:
        safe_value = getattr(w.Candidate("probe"), field)

        def mutant(candidate: w.Candidate, *, _field=field, _safe=safe_value):
            neutralized = dataclasses.replace(candidate, **{_field: _safe})
            return original(neutralized)

        w.reject_reason = mutant
        try:
            run_trial()
        except AssertionError:
            pass
        else:
            survivors.append(field)
        finally:
            w.reject_reason = original

    killed = len(MUTATED_FIELDS) - len(survivors)
    score = killed / len(MUTATED_FIELDS)
    print(f"MUTANTS_TOTAL={len(MUTATED_FIELDS)}")
    print(f"MUTANTS_KILLED={killed}")
    print(f"MUTATION_SCORE={score:.3f}")
    if survivors:
        raise AssertionError(f"mutation survivors: {survivors}")
    assert score == 1.0
    print("POISONED_RULE_MUTATION_CONTROL=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
