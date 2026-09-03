#!/usr/bin/env python3
"""Deterministic sanity checks for REI-CLP/3.0-observer."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import bridge_to_wheel_vnext as bridge_mod
import vnext_observer as observer_mod


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False) + "\n", encoding="utf-8")


def build_cycle(cycle_id: str = "sanity-cycle") -> dict[str, object]:
    return {
        "schema_version": 2,
        "runtime_revision": "2.3",
        "cycle_id": cycle_id,
        "completed_at": "2026-09-03T00:00:00Z",
        "branch": "shadow-node",
        "audit_hash": "a" * 64,
        "canonical_mainline_touched": False,
        "core_committed": False,
        "human_review_required": True,
        "runtime_errors": [],
        "proposals": [
            {
                "role": "evidence",
                "proposal": {
                    "uncertainty": 0.2,
                    "counterarguments": ["alternative explanation"],
                    "evidence": [
                        {"claim": "c1", "support": "s1", "provenance": "https://example.com/a", "independence": 0.8},
                        {"claim": "c2", "support": "s2", "provenance": "https://example.com/a?copy=1", "independence": 0.8},
                    ],
                },
                "local_gate": {"passed": True, "reasons": []},
            },
            {
                "role": "ood",
                "proposal": {
                    "uncertainty": 0.4,
                    "counterarguments": ["distribution shift"],
                    "evidence": [
                        {"claim": "c3", "support": "s3", "provenance": "model_inference", "independence": 0.2}
                    ],
                },
                "local_gate": {"passed": True, "reasons": []},
            },
        ],
        "synthesis": {"claim": "primary claim", "proposed_shadow_update": "bounded update", "open_risks": []},
        "review": {
            "verdict": "ACCEPT_SHADOW",
            "target_state": "shadow",
            "core_write": False,
            "human_review_required": True,
            "score": 0.8,
            "reasons": [],
            "required_revisions": [],
            "regression_checks": ["canonical unchanged"],
        },
        "deterministic_gate": {"shadow_accepted": True, "reasons": []},
    }


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="rei-vnext-sanity-") as td:
        home = Path(td)
        cycle = build_cycle()
        write_json(home / "state" / "last_cycle.json", cycle)
        write_json(home / "outputs" / "closed_loop_v2" / "cycle_sanity-cycle.json", cycle)
        (home / "state" / "promotion_queue.jsonl").write_text(
            json.dumps({
                "cycle_id": "sanity-cycle",
                "status": "PENDING_HUMAN_REVIEW",
                "core_write": False,
                "proposed_shadow_update": "bounded update",
                "audit_hash": "a" * 64,
            }) + "\n",
            encoding="utf-8",
        )

        assert observer_mod.self_test() == 0
        assert observer_mod.process(home) == 0
        assert observer_mod.process(home) == 0

        observer = json.loads((home / "state" / "vnext_observer" / "latest.json").read_text(encoding="utf-8"))
        assert observer["protocol_version"] == observer_mod.PROTOCOL_VERSION
        assert observer["observer_mode"] is True
        assert observer["canonical_write_permission"] is False
        assert observer["hypothesis_state"]["quantum_claim"] is False
        assert observer["promotion_gate_v2"]["may_promote_canonical"] is False

        for name in ("failure_recurrence.jsonl", "calibration_ledger.jsonl", "lineage_ledger.jsonl"):
            rows = [line for line in (home / "state" / "vnext_observer" / name).read_text(encoding="utf-8").splitlines() if line.strip()]
            assert len(rows) == 1, (name, len(rows))

        assert bridge_mod.bridge(home) == 0
        records = [json.loads(line) for line in (home / "divine_wheel_inbox.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
        assert len(records) == 1
        record = records[0]
        assert record["protocol_version"] == observer_mod.PROTOCOL_VERSION
        assert record["observer_mode"] is True
        assert record["canonical_write_permission"] is False
        assert record["reality_validated"] is False
        assert record["independent_replication"] is False
        assert record["ascension_permission"] is False

        corrupt = home / "corrupt.jsonl"
        corrupt.write_text('{"ok":1}\n{broken\n', encoding="utf-8")
        try:
            list(bridge_mod.read_jsonl(corrupt))
        except RuntimeError:
            pass
        else:
            raise AssertionError("bridge must fail closed on malformed JSONL")

    print("VNEXT_SANITY_SUCCESS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
