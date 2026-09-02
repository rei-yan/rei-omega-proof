#!/usr/bin/env python3
"""Finite sanity checks for the External Discovery Bridge.

This is an internal protocol crucible only. It does not create external evidence and
cannot establish G4 or G5.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from typing import Tuple


def digest(obj) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True)
class DiscoveryCommitment:
    candidate_hash: str
    code_hash: str
    environment_hash: str
    metric: str
    threshold: float
    abstention_rule: str
    scope: str
    authority: int = 0


@dataclass(frozen=True)
class ExternalPacketCommitment:
    packet_id: str
    hidden_digest: str
    evaluator_lineage: Tuple[str, ...]


def make_hidden_packet(values):
    packet = {"targets": list(values), "scoring_key": "mse-v1"}
    return packet, digest(packet)


def mse(pred, target):
    assert len(pred) == len(target) and pred
    return sum((a - b) ** 2 for a, b in zip(pred, target)) / len(pred)


def evaluate(
    commitment: DiscoveryCommitment,
    external_commitment: ExternalPacketCommitment,
    revealed_packet,
    predictions,
    *,
    posthoc_retune=False,
    metric_changed=False,
    hidden_answer_access_before_freeze=False,
    raw_record_preserved=True,
    evaluator_independent=True,
):
    if digest(revealed_packet) != external_commitment.hidden_digest:
        return "INVALID_PROTOCOL"
    if posthoc_retune or metric_changed or hidden_answer_access_before_freeze:
        return "INVALID_PROTOCOL"
    if not raw_record_preserved:
        return "INVALID_PROTOCOL"
    if commitment.authority != 0:
        return "INVALID_PROTOCOL"
    score = mse(predictions, revealed_packet["targets"])
    if not evaluator_independent:
        return "DEPENDENT_EVIDENCE_ONLY"
    return "INTERNAL_BRIDGE_PASS" if score <= commitment.threshold else "INTERNAL_BRIDGE_FAIL"


def main():
    candidate = DiscoveryCommitment(
        candidate_hash="candidate-v1",
        code_hash="code-v1",
        environment_hash="env-v1",
        metric="mse",
        threshold=0.01,
        abstention_rule="abstain-on-schema-violation",
        scope="finite synthetic bridge sanity",
    )
    candidate_hash = digest(asdict(candidate))
    assert len(candidate_hash) == 64

    hidden, hidden_digest = make_hidden_packet([1.0, 2.0, 3.0])
    external = ExternalPacketCommitment(
        packet_id="external-controller-synthetic-001",
        hidden_digest=hidden_digest,
        evaluator_lineage=("synthetic-controller", "synthetic-scorer"),
    )

    good = evaluate(candidate, external, hidden, [1.0, 2.0, 3.0])
    assert good == "INTERNAL_BRIDGE_PASS"

    bad_prediction = evaluate(candidate, external, hidden, [1.0, 2.0, 4.0])
    assert bad_prediction == "INTERNAL_BRIDGE_FAIL"

    tampered = {"targets": [1.0, 2.0, 9.0], "scoring_key": "mse-v1"}
    assert evaluate(candidate, external, tampered, [1.0, 2.0, 3.0]) == "INVALID_PROTOCOL"

    assert evaluate(
        candidate, external, hidden, [1.0, 2.0, 3.0], posthoc_retune=True
    ) == "INVALID_PROTOCOL"

    assert evaluate(
        candidate, external, hidden, [1.0, 2.0, 3.0], metric_changed=True
    ) == "INVALID_PROTOCOL"

    assert evaluate(
        candidate,
        external,
        hidden,
        [1.0, 2.0, 3.0],
        hidden_answer_access_before_freeze=True,
    ) == "INVALID_PROTOCOL"

    assert evaluate(
        candidate, external, hidden, [1.0, 2.0, 3.0], raw_record_preserved=False
    ) == "INVALID_PROTOCOL"

    assert evaluate(
        candidate, external, hidden, [1.0, 2.0, 3.0], evaluator_independent=False
    ) == "DEPENDENT_EVIDENCE_ONLY"

    # Internal sanity must never mint external gate passes.
    forbidden = {
        "G4_PASS",
        "G5_PASS",
        "WORLD_BEST",
        "WORLD_UNIQUE",
        "CANONICAL_PROMOTION",
        "AUTONOMOUS_EXPERIMENT_AUTHORITY",
        "REAL_WORLD_ACTUATION_AUTHORITY",
    }
    observed = {
        good,
        bad_prediction,
        "INVALID_PROTOCOL",
        "DEPENDENT_EVIDENCE_ONLY",
        "G4_PROTOCOL_READY",
        "READY_FOR_EXTERNAL_HIDDEN_DISCOVERY_PROTOCOL",
    }
    assert forbidden.isdisjoint(observed)

    print("External Discovery Bridge sanity: PASS")
    print("G4: OPEN")
    print("G5: OPEN")
    print("real_world_actuation_authority: 0")


if __name__ == "__main__":
    main()
