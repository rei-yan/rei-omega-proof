#!/usr/bin/env python3
"""Finite deterministic sanity crucible for Discovery Genesis Stack.

Synthetic only. No real-world experimentation or external validity claim.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Hypothesis:
    name: str
    lineage: str
    predicts: callable
    assumptions: int
    authority: float = 0.0


@dataclass(frozen=True)
class Measurement:
    name: str
    x: float
    cost: float
    risk: float
    assumption_load: float
    authority: float = 0.0


def hypotheses() -> list[Hypothesis]:
    return [
        Hypothesis("linear", "L1", lambda x: 0.5 + 1.2 * x, 1),
        Hypothesis("quadratic", "L2", lambda x: 0.5 + 1.2 * x - 0.8 * x * x, 2),
        Hypothesis("periodic", "L3", lambda x: 0.3 + 0.7 * math.sin(x) - 0.4 * math.cos(x), 2),
    ]


def measurements() -> list[Measurement]:
    return [
        Measurement("m_left", -1.6, 1.0, 0.0, 0.5),
        Measurement("m_mid", 0.2, 0.8, 0.0, 0.4),
        Measurement("m_right", 1.6, 1.0, 0.0, 0.5),
    ]


def discrimination(m: Measurement, hs: list[Hypothesis]) -> float:
    ys = [h.predicts(m.x) for h in hs]
    return max(ys) - min(ys)


def measurement_value(m: Measurement, hs: list[Hypothesis]) -> float:
    reproducibility = 1.0
    reversibility = 1.0
    denominator = m.cost + m.risk + m.assumption_load
    return discrimination(m, hs) * reproducibility * reversibility / denominator


def choose_measurement(hs: list[Hypothesis], ms: list[Measurement]) -> Measurement:
    return max(ms, key=lambda m: (measurement_value(m, hs), m.name))


def hidden_truth(x: float) -> float:
    # Hidden until after lineage, measurement and metric freeze in this synthetic crucible.
    return 0.5 + 1.2 * x - 0.8 * x * x


def squared_error(h: Hypothesis, m: Measurement) -> float:
    return (h.predicts(m.x) - hidden_truth(m.x)) ** 2


def run_competition(posthoc_retune: bool = False) -> dict:
    hs = hypotheses()
    ms = measurements()

    # Freeze before revealing the hidden target value.
    frozen_lineages = tuple((h.name, h.lineage, h.assumptions) for h in hs)
    frozen_measurements = tuple((m.name, m.x, m.cost, m.risk, m.assumption_load) for m in ms)
    selected = choose_measurement(hs, ms)
    metric = "squared_error_plus_fixed_complexity_penalty"
    complexity_penalty = 1e-6

    if posthoc_retune:
        return {
            "status": "DISQUALIFIED_POSTHOC_RETUNE",
            "frozen_lineages": frozen_lineages,
            "selected_measurement": selected.name,
            "authority": 0.0,
            "g5": "OPEN",
            "external_validity": False,
        }

    ranked = sorted(
        hs,
        key=lambda h: (squared_error(h, selected) + complexity_penalty * h.assumptions, h.name),
    )
    winner = ranked[0]
    winner_error = squared_error(winner, selected)

    status = (
        "SURVIVES_INTERNAL_HIDDEN_CHALLENGE"
        if winner_error < 1e-12
        else "NO_DISCOVERY_CANDIDATE"
    )

    return {
        "status": status,
        "winner": winner.name if status == "SURVIVES_INTERNAL_HIDDEN_CHALLENGE" else None,
        "winner_lineage": winner.lineage if status == "SURVIVES_INTERNAL_HIDDEN_CHALLENGE" else None,
        "selected_measurement": selected.name,
        "selected_measurement_x": selected.x,
        "measurement_value": measurement_value(selected, hs),
        "frozen_lineages": frozen_lineages,
        "frozen_measurements": frozen_measurements,
        "metric": metric,
        "authority": 0.0,
        "certification": "UNVERIFIED",
        "external_validity": False,
        "g5": "OPEN",
        "promotion": "READY_FOR_EXTERNAL_HIDDEN_DISCOVERY_PROTOCOL",
    }


def unresolved_case() -> dict:
    # No candidate in the finite ecology explains this synthetic structure.
    truth = lambda x: 1.0 if abs(x) < 0.05 else 0.0
    hs = hypotheses()
    probes = [-1.0, -0.25, 0.0, 0.25, 1.0]
    best = min(
        hs,
        key=lambda h: max(abs(h.predicts(x) - truth(x)) for x in probes),
    )
    best_error = max(abs(best.predicts(x) - truth(x)) for x in probes)
    return {
        "status": "UNRESOLVED_UNKNOWN" if best_error > 0.5 else "NO_DISCOVERY_CANDIDATE",
        "best_existing_hypothesis": best.name,
        "best_max_error": best_error,
        "authority": 0.0,
        "real_world_execution": "FORBIDDEN_BY_DEFAULT",
    }


def main() -> None:
    good = run_competition(False)
    cheated = run_competition(True)
    unresolved = unresolved_case()

    assert good["status"] == "SURVIVES_INTERNAL_HIDDEN_CHALLENGE"
    assert good["winner"] == "quadratic"
    assert good["authority"] == 0.0
    assert good["certification"] == "UNVERIFIED"
    assert good["external_validity"] is False
    assert good["g5"] == "OPEN"
    assert good["promotion"] == "READY_FOR_EXTERNAL_HIDDEN_DISCOVERY_PROTOCOL"
    assert cheated["status"] == "DISQUALIFIED_POSTHOC_RETUNE"
    assert cheated["g5"] == "OPEN"
    assert unresolved["status"] == "UNRESOLVED_UNKNOWN"
    assert unresolved["real_world_execution"] == "FORBIDDEN_BY_DEFAULT"

    print(json.dumps({"competition": good, "retune_case": cheated, "unresolved": unresolved}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
