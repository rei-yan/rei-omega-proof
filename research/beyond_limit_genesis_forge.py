#!/usr/bin/env python3
"""Finite deterministic digital-world forge for the Beyond-Limit Genesis proposal.

This is a synthetic research crucible. It generates and falsifies finite model-world
candidates only. It does not perform real-world actions or establish external validity.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Family:
    name: str
    basis: tuple[Callable[[float], float], ...]


@dataclass
class FittedWorld:
    family: Family
    coeffs: list[float]
    train_mse: float
    holdout_mse: float
    challenge_max_error: float
    authority: float = 0.0

    def predict(self, x: float) -> float:
        return sum(c * b(x) for c, b in zip(self.coeffs, self.family.basis))


ONE = lambda x: 1.0
X = lambda x: x
X2 = lambda x: x * x
SIN = lambda x: math.sin(x)
COS = lambda x: math.cos(x)
HINGE = lambda x: max(0.0, x - 0.5)

FAMILIES = (
    Family("linear", (ONE, X)),
    Family("quadratic", (ONE, X, X2)),
    Family("oscillatory", (ONE, SIN, COS)),
    Family("hinge", (ONE, X, HINGE)),
    Family("mixed", (ONE, X, X2, SIN, COS)),
)


def solve_linear(a: list[list[float]], b: list[float]) -> list[float]:
    """Small deterministic Gaussian elimination with partial pivoting."""
    n = len(b)
    m = [row[:] + [rhs] for row, rhs in zip(a, b)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(m[r][col]))
        if abs(m[pivot][col]) < 1e-12:
            raise ValueError("singular normal equation")
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


def fit(family: Family, xs: list[float], ys: list[float]) -> list[float]:
    p = len(family.basis)
    gram = [[0.0] * p for _ in range(p)]
    rhs = [0.0] * p
    ridge = 1e-10
    for x, y in zip(xs, ys):
        phi = [f(x) for f in family.basis]
        for i in range(p):
            rhs[i] += phi[i] * y
            for j in range(p):
                gram[i][j] += phi[i] * phi[j]
    for i in range(p):
        gram[i][i] += ridge
    return solve_linear(gram, rhs)


def mse(world: FittedWorld, xs: list[float], ys: list[float]) -> float:
    return sum((world.predict(x) - y) ** 2 for x, y in zip(xs, ys)) / len(xs)


def max_error(world: FittedWorld, xs: list[float], truth: Callable[[float], float]) -> float:
    return max(abs(world.predict(x) - truth(x)) for x in xs)


def fit_worlds(truth: Callable[[float], float]) -> list[FittedWorld]:
    train_x = [-1.0, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0]
    holdout_x = [-1.2, -0.9, -0.6, -0.3, 0.15, 0.45, 0.8, 1.1]
    challenge_x = [i / 10 for i in range(-20, 21)]
    train_y = [truth(x) for x in train_x]
    holdout_y = [truth(x) for x in holdout_x]

    worlds = []
    for family in FAMILIES:
        coeffs = fit(family, train_x, train_y)
        w = FittedWorld(family, coeffs, 0.0, 0.0, 0.0)
        w.train_mse = mse(w, train_x, train_y)
        w.holdout_mse = mse(w, holdout_x, holdout_y)
        w.challenge_max_error = max_error(w, challenge_x, truth)
        worlds.append(w)
    return worlds


def rank_worlds(worlds: list[FittedWorld]) -> list[FittedWorld]:
    # Tiny fixed complexity penalty prevents gratuitous ornate ties without overriding adequacy.
    return sorted(
        worlds,
        key=lambda w: (w.holdout_mse + 1e-10 * len(w.family.basis), len(w.family.basis), w.family.name),
    )


def discriminating_measurement(a: FittedWorld, b: FittedWorld) -> tuple[float, float]:
    grid = [i / 20 for i in range(-40, 41)]
    x = max(grid, key=lambda z: abs(a.predict(z) - b.predict(z)))
    return x, abs(a.predict(x) - b.predict(x))


def forge(name: str, truth: Callable[[float], float], tolerance: float = 0.20) -> dict:
    ranked = rank_worlds(fit_worlds(truth))
    winner, counterworld = ranked[0], ranked[1]
    measurement_x, disagreement = discriminating_measurement(winner, counterworld)
    status = "KEEP_AS_HYPOTHESIS" if winner.challenge_max_error <= tolerance else "ABSTAIN"
    return {
        "world": name,
        "selected_family": winner.family.name,
        "counterworld_family": counterworld.family.name,
        "holdout_mse": winner.holdout_mse,
        "wider_max_error": winner.challenge_max_error,
        "discriminating_measurement_x": measurement_x,
        "counterworld_disagreement": disagreement,
        "status": status,
        "authority": winner.authority,
        "external_gate_closed": False,
    }


def main():
    worlds = {
        "curved": lambda x: 0.5 + 1.2 * x - 0.8 * x * x,
        "periodic": lambda x: 0.3 + 0.7 * math.sin(x) - 0.4 * math.cos(x),
        "step_ood": lambda x: -1.0 if x < 0 else 1.0,
    }

    results = [forge(name, fn) for name, fn in worlds.items()]

    by_name = {r["world"]: r for r in results}
    assert by_name["curved"]["status"] == "KEEP_AS_HYPOTHESIS"
    assert by_name["periodic"]["status"] == "KEEP_AS_HYPOTHESIS"
    assert by_name["step_ood"]["status"] == "ABSTAIN"
    assert all(r["authority"] == 0.0 for r in results)
    assert all(r["external_gate_closed"] is False for r in results)
    assert all(r["counterworld_family"] for r in results)

    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
