#!/usr/bin/env python3
"""Finite synthetic crucible for ontology rupture, causal grammar, and transfer.

No real-world actions are performed. Generated candidates remain unverified,
non-canonical, and authority-zero.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Ontology:
    name: str
    features: tuple[Callable[[float], float], ...]
    authority: float = 0.0
    certification: str = "UNVERIFIED"


ONE = lambda x: 1.0
X = lambda x: x
SIGN0 = lambda x: 1.0 if x >= 0.0 else 0.0

ONTOLOGIES = (
    Ontology("continuous_x", (ONE, X)),
    Ontology("state_partition_zero", (ONE, SIGN0)),
    Ontology("hybrid_x_state", (ONE, X, SIGN0)),
)


def solve_linear(a: list[list[float]], b: list[float]) -> list[float]:
    n = len(b)
    m = [row[:] + [rhs] for row, rhs in zip(a, b)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(m[r][col]))
        if abs(m[pivot][col]) < 1e-12:
            raise ValueError("singular system")
        m[col], m[pivot] = m[pivot], m[col]
        p = m[col][col]
        for j in range(col, n + 1):
            m[col][j] /= p
        for r in range(n):
            if r == col:
                continue
            f = m[r][col]
            for j in range(col, n + 1):
                m[r][j] -= f * m[col][j]
    return [m[i][n] for i in range(n)]


def fit(ontology: Ontology, xs: list[float], ys: list[float]) -> list[float]:
    p = len(ontology.features)
    gram = [[0.0] * p for _ in range(p)]
    rhs = [0.0] * p
    for x, y in zip(xs, ys):
        phi = [f(x) for f in ontology.features]
        for i in range(p):
            rhs[i] += phi[i] * y
            for j in range(p):
                gram[i][j] += phi[i] * phi[j]
    for i in range(p):
        gram[i][i] += 1e-10
    return solve_linear(gram, rhs)


def predict(ontology: Ontology, coeffs: list[float], x: float) -> float:
    return sum(c * f(x) for c, f in zip(coeffs, ontology.features))


def max_error(ontology: Ontology, coeffs: list[float], xs: list[float], truth: Callable[[float], float]) -> float:
    return max(abs(predict(ontology, coeffs, x) - truth(x)) for x in xs)


def frozen_ontology_selection(truth: Callable[[float], float], tolerance: float = 0.15) -> dict:
    train_x = [-1.0, -0.75, -0.5, -0.25, 0.25, 0.5, 0.75, 1.0]
    holdout_x = [-1.2, -0.9, -0.4, -0.1, 0.1, 0.4, 0.9, 1.2]
    train_y = [truth(x) for x in train_x]

    candidates = []
    for ontology in ONTOLOGIES:
        coeffs = fit(ontology, train_x, train_y)
        err = max_error(ontology, coeffs, holdout_x, truth)
        candidates.append((err, len(ontology.features), ontology.name, ontology, coeffs))

    candidates.sort(key=lambda z: (z[0], z[1], z[2]))
    err, _, _, ontology, coeffs = candidates[0]
    return {
        "ontology": ontology,
        "coeffs": coeffs,
        "holdout_max_error": err,
        "status": "KEEP_AS_CANDIDATE" if err <= tolerance else "ABSTAIN",
    }


def transfer_without_retuning(
    ontology: Ontology,
    coeffs: list[float],
    target_truth: Callable[[float], float],
    tolerance: float = 0.15,
) -> dict:
    target_x = [-1.4, -1.0, -0.65, -0.2, 0.2, 0.65, 1.0, 1.4]
    err = max_error(ontology, coeffs, target_x, target_truth)
    return {
        "target_max_error": err,
        "retuned": False,
        "status": "KEEP_SCOPE" if err <= tolerance else "ABSTAIN",
    }


def causal_equivalence_challenge() -> dict:
    # Purely synthetic demonstration: observational covariance alone leaves two
    # direction hypotheses eligible. A frozen synthetic intervention breaks the tie.
    observational_candidates = ["A_to_B", "B_to_A"]
    observational_status = "CAUSAL_DIRECTION_UNIDENTIFIED"

    # Synthetic SCM truth: B = 2*A. Under do(A=3), candidate A->B predicts B=6;
    # candidate B->A has no licensed prediction of B from intervened A.
    intervention = {"do_A": 3.0, "observed_B": 6.0}
    predictions = {"A_to_B": 6.0, "B_to_A": None}
    surviving = [
        c for c in observational_candidates
        if predictions[c] is not None and abs(predictions[c] - intervention["observed_B"]) < 1e-12
    ]
    return {
        "observational_status": observational_status,
        "synthetic_intervention_only": True,
        "surviving_candidates": surviving,
        "authority": 0.0,
        "certification": "UNVERIFIED",
    }


def main() -> None:
    source_truth = lambda x: -1.0 if x < 0.0 else 1.0
    same_mechanism_new_samples = lambda x: -1.0 if x < 0.0 else 1.0
    shifted_regime = lambda x: -1.0 if x < 0.4 else 1.0

    selected = frozen_ontology_selection(source_truth)
    ontology = selected["ontology"]
    coeffs = selected["coeffs"]

    same = transfer_without_retuning(ontology, coeffs, same_mechanism_new_samples)
    shifted = transfer_without_retuning(ontology, coeffs, shifted_regime)
    causal = causal_equivalence_challenge()

    result = {
        "selected_ontology": ontology.name,
        "selection_status": selected["status"],
        "source_holdout_max_error": selected["holdout_max_error"],
        "same_mechanism_transfer": same,
        "shifted_regime_transfer": shifted,
        "causal_challenge": causal,
        "ontology_authority": ontology.authority,
        "ontology_certification": ontology.certification,
        "canonical": False,
        "external_gate_closed": False,
    }

    assert selected["status"] == "KEEP_AS_CANDIDATE"
    assert ontology.name == "state_partition_zero"
    assert same["status"] == "KEEP_SCOPE"
    assert same["retuned"] is False
    assert shifted["status"] == "ABSTAIN"
    assert shifted["retuned"] is False
    assert causal["observational_status"] == "CAUSAL_DIRECTION_UNIDENTIFIED"
    assert causal["surviving_candidates"] == ["A_to_B"]
    assert ontology.authority == 0.0
    assert ontology.certification == "UNVERIFIED"
    assert result["canonical"] is False
    assert result["external_gate_closed"] is False

    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
