#!/usr/bin/env python3
"""Validate G3 submission structure without revealing or computing oracle answers."""

import json
import sys
from pathlib import Path


def load_jsonl(path):
    rows = []
    with Path(path).open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            if not line.strip():
                raise SystemExit(f"blank line at {path}:{line_no}")
            try:
                row = json.loads(line)
            except json.JSONDecodeError as e:
                raise SystemExit(f"invalid JSON at {path}:{line_no}: {e}")
            if not isinstance(row, dict):
                raise SystemExit(f"row is not a JSON object at {path}:{line_no}")
            rows.append(row)
    return rows


def require_bool(row, key, line_no):
    if set(row.keys()) != {"id", key}:
        raise SystemExit(
            f"submission line {line_no}: expected exactly keys id,{key}; got {sorted(row.keys())}"
        )
    if not isinstance(row[key], bool):
        raise SystemExit(f"submission line {line_no}: {key} must be JSON boolean")


def main():
    if len(sys.argv) != 3:
        raise SystemExit(
            "usage: python3 g3/validate_submission_shape.py CHALLENGE.jsonl SUBMISSION.jsonl"
        )

    challenge = load_jsonl(sys.argv[1])
    submission = load_jsonl(sys.argv[2])

    if len(challenge) != 25_000:
        raise SystemExit(f"challenge must contain 25000 rows, got {len(challenge)}")
    if len(submission) != len(challenge):
        raise SystemExit(
            f"submission row count mismatch: expected {len(challenge)}, got {len(submission)}"
        )

    seen = set()
    counts = {"gate": 0, "authority": 0, "upgrade": 0}

    for i, (inp, out) in enumerate(zip(challenge, submission), 1):
        cid = inp.get("id")
        ctype = inp.get("type")

        if not isinstance(cid, str) or cid in seen:
            raise SystemExit(f"challenge line {i}: invalid or duplicate id {cid!r}")
        seen.add(cid)

        if out.get("id") != cid:
            raise SystemExit(
                f"submission line {i}: id/order mismatch, expected {cid!r}, got {out.get('id')!r}"
            )

        if ctype == "gate":
            require_bool(out, "execute", i)
        elif ctype == "authority":
            require_bool(out, "monotone", i)
        elif ctype == "upgrade":
            require_bool(out, "accepted", i)
        else:
            raise SystemExit(f"challenge line {i}: unknown case type {ctype!r}")

        counts[ctype] += 1

    expected = {"gate": 10_000, "authority": 10_000, "upgrade": 5_000}
    if counts != expected:
        raise SystemExit(f"challenge type counts mismatch: got {counts}, expected {expected}")

    print(
        json.dumps(
            {
                "shape_valid": True,
                "rows": len(submission),
                "counts": counts,
                "oracle_used": False,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
