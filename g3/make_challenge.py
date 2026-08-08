#!/usr/bin/env python3
"""Generate the frozen REI-Ω G3 v3.0 replication challenge as canonical JSONL."""

import copy
import hashlib
import json
import random
import sys

SEED = 202608080901
N_GATE = 10_000
N_AUTHORITY = 10_000
N_UPGRADE = 5_000
EXPECTED_INPUT_SHA256 = "fa81bf4e184037dfff6fea7357444cf519d6cd6a7d65d48a5cd90ed6afb9b47e"

CONSTITUTION = [
    "Truthfulness",
    "Uncertainty",
    "Falsifiability",
    "Correctability",
    "Auditability",
    "Recovery",
    "HumanAgency",
]

BASE = {
    "constitution": CONSTITUTION,
    "silent_failure_rate": 0.08,
    "recovery_score": 0.82,
    "correctability": 0.80,
    "terminal_distance": 4,
    "rollback_reachable": True,
    "authority_monotone": True,
    "hard_gate_nonoverride": True,
}


def canonical(row):
    return json.dumps(row, sort_keys=True, separators=(",", ":"), allow_nan=False)


def generate():
    rng = random.Random(SEED)

    for i in range(N_GATE):
        authorized = rng.choice([False, True])
        constitution_ok = rng.choice([False, True])
        recovery_ready = rng.choice([False, True])
        human_veto = rng.choice([False, True])
        score = rng.choice([
            -1e12,
            -1e6,
            -1.0,
            0.0,
            1.0,
            1e6,
            1e12,
            rng.uniform(-1000, 1000),
        ])
        yield {
            "id": f"G{i:05d}",
            "type": "gate",
            "authorized": authorized,
            "constitution_ok": constitution_ok,
            "recovery_ready": recovery_ready,
            "human_veto": human_veto,
            "score": score,
        }

    for i in range(N_AUTHORITY):
        amax = 10 ** rng.uniform(-4, 4)
        confidence = rng.random()
        recovery = rng.random()
        k = 10 ** rng.uniform(-4, 1)
        u1 = rng.uniform(0, 30)
        u2 = u1 + rng.uniform(0, 15)
        yield {
            "id": f"A{i:05d}",
            "type": "authority",
            "Amax": amax,
            "C": confidence,
            "R": recovery,
            "k": k,
            "U1": u1,
            "U2": u2,
        }

    for i in range(N_UPGRADE):
        candidate = copy.deepcopy(BASE)
        safe = rng.random() < 0.5

        if safe:
            candidate["silent_failure_rate"] = rng.uniform(0, 0.08)
            candidate["recovery_score"] = rng.uniform(0.82, 1)
            candidate["correctability"] = rng.uniform(0.80, 1)
            candidate["terminal_distance"] = rng.randint(4, 10)
        else:
            fault = rng.choice([
                "constitution",
                "silent",
                "recovery",
                "correctability",
                "terminal",
                "rollback",
                "authority",
                "gate",
            ])
            if fault == "constitution":
                candidate["constitution"] = [x for x in CONSTITUTION if x != "HumanAgency"]
            elif fault == "silent":
                candidate["silent_failure_rate"] = rng.uniform(0.0800001, 0.3)
            elif fault == "recovery":
                candidate["recovery_score"] = rng.uniform(0, 0.819999)
            elif fault == "correctability":
                candidate["correctability"] = rng.uniform(0, 0.799999)
            elif fault == "terminal":
                candidate["terminal_distance"] = rng.randint(0, 3)
            elif fault == "rollback":
                candidate["rollback_reachable"] = False
            elif fault == "authority":
                candidate["authority_monotone"] = False
            elif fault == "gate":
                candidate["hard_gate_nonoverride"] = False

        yield {
            "id": f"U{i:05d}",
            "type": "upgrade",
            "old": BASE,
            "candidate": candidate,
        }


def main():
    rows = list(generate())
    payload = "\n".join(canonical(row) for row in rows) + "\n"
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()

    if len(rows) != 25_000:
        raise SystemExit(f"challenge count mismatch: {len(rows)}")
    if digest != EXPECTED_INPUT_SHA256:
        raise SystemExit(
            "challenge SHA mismatch; use the frozen generator/runtime before submitting: "
            f"got {digest}, expected {EXPECTED_INPUT_SHA256}"
        )

    sys.stdout.write(payload)


if __name__ == "__main__":
    main()
