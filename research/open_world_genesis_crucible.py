#!/usr/bin/env python3
"""Deterministic toy crucible for bounded open-world Genesis research.

This is a research sanity test, not a claim of unrestricted discovery.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
from dataclasses import dataclass
from typing import Callable, Iterable, Sequence


FEATURES: dict[str, Callable[[float], float]] = {
    "x": lambda x: x,
    "x2": lambda x: x * x,
    "x3": lambda x: x * x * x,
    "abs": lambda x: abs(x),
    "sin13": lambda x: math.sin(1.3 * x),
}

WORLD_SCHEDULE = [
    ("linear", 1101),
    ("quadratic", 1102),
    ("cubic", 1103),
    ("abs", 1104),
    ("sin", 1105),
    ("exp_ood", 2101),
    ("step_ood", 2102),
]

EXPECTED_SCHEDULE_SHA256 = (
    "19a699ac17503eebb30679f4ba297051826a46952ac27b353c04ed3e3f90fc00"
)

WORLD_FNS: dict[str, Callable[[float], float]] = {
    "linear": lambda x: 1.2 + 2.4 * x,
    "quadratic": lambda x: -0.5 + 1.7 * x * x,
    "cubic": lambda x: 0.4 - 0.9 * x * x * x,
    "abs": lambda x: 0.3 + 2.1 * abs(x),
    "sin": lambda x: -0.2 + 1.8 * math.sin(1.3 * x),
    "exp_ood": lambda x: -0.5 + math.exp(0.75 * x),
    "step_ood": lambda x: (-1.4 if x < 0.35 else 1.6) + 0.15 * x,
}

IN_GRAMMAR = {"linear", "quadratic", "cubic", "abs", "sin"}
OUT_OF_GRAMMAR = {"exp_ood", "step_ood"}

NOISE_SD = 0.015
HELDOUT_RMSE_MAX = 0.07
CHALLENGE_RMSE_MAX = 0.11
MAX_RESIDUAL_MAX = 0.28


@dataclass(frozen=True)
class Model:
    features: tuple[str, ...]
    beta: tuple[float, ...]

    def predict(self, x: float) -> float:
        return self.beta[0] + sum(
            coef * FEATURES[name](x)
            for coef, name in zip(self.beta[1:], self.features)
        )


@dataclass(frozen=True)
class Evaluation:
    world: str
    model: Model
    heldout_rmse: float
    challenge_rmse: float
    max_residual: float
    falsification_x: float
    falsification_residual: float
    measurement_x: float
    measurement_disagreement: float
    certified: bool


def schedule_digest() -> str:
    payload = json.dumps(WORLD_SCHEDULE, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def grid(lo: float, hi: float, n: int, midpoint: bool = False) -> list[float]:
    if midpoint:
        width = (hi - lo) / n
        return [lo + (i + 0.5) * width for i in range(n)]
    if n == 1:
        return [(lo + hi) / 2.0]
    return [lo + (hi - lo) * i / (n - 1) for i in range(n)]


def solve_linear(a: list[list[float]], b: list[float], eps: float = 1e-12) -> list[float]:
    n = len(b)
    m = [list(map(float, a[i])) + [float(b[i])] for i in range(n)]

    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(m[r][col]))
        if abs(m[pivot][col]) < eps:
            raise ValueError("singular normal system")
        m[col], m[pivot] = m[pivot], m[col]

        p = m[col][col]
        for j in range(col, n + 1):
            m[col][j] /= p

        for row in range(n):
            if row == col:
                continue
            factor = m[row][col]
            if factor == 0.0:
                continue
            for j in range(col, n + 1):
                m[row][j] -= factor * m[col][j]

    return [m[i][n] for i in range(n)]


def fit_model(xs: Sequence[float], ys: Sequence[float], features: Sequence[str]) -> Model:
    p = 1 + len(features)
    xtx = [[0.0] * p for _ in range(p)]
    xty = [0.0] * p

    for x, y in zip(xs, ys):
        row = [1.0] + [FEATURES[name](x) for name in features]
        for i in range(p):
            xty[i] += row[i] * y
            for j in range(p):
                xtx[i][j] += row[i] * row[j]

    # Tiny fixed ridge is numeric stabilization, not a fitted hyperparameter.
    for i in range(p):
        xtx[i][i] += 1e-8

    beta = solve_linear(xtx, xty)
    return Model(tuple(features), tuple(beta))


def rmse(model: Model, xs: Sequence[float], ys: Sequence[float]) -> float:
    return math.sqrt(
        sum((model.predict(x) - y) ** 2 for x, y in zip(xs, ys)) / len(xs)
    )


def abs_corr(a: Sequence[float], b: Sequence[float]) -> float:
    ma = sum(a) / len(a)
    mb = sum(b) / len(b)
    da = [x - ma for x in a]
    db = [x - mb for x in b]
    va = sum(x * x for x in da)
    vb = sum(x * x for x in db)
    if va < 1e-12 or vb < 1e-12:
        return 0.0
    return abs(sum(x * y for x, y in zip(da, db)) / math.sqrt(va * vb))


def propose_candidates(xs: Sequence[float], ys: Sequence[float]) -> list[Model]:
    """Generate a bounded candidate ecology from a finite representation grammar."""
    candidates: dict[tuple[str, ...], Model] = {}

    # Residual-driven representation mutation begins with the raw coordinate.
    chosen = ["x"]
    for _ in range(3):
        model = fit_model(xs, ys, chosen)
        candidates[model.features] = model
        residual = [y - model.predict(x) for x, y in zip(xs, ys)]
        if len(chosen) >= 3:
            break

        unused = [name for name in FEATURES if name not in chosen]
        scored = [
            (
                abs_corr(residual, [FEATURES[name](x) for x in xs]),
                name,
            )
            for name in unused
        ]
        score, best = max(scored)
        if score < 0.08:
            break
        chosen.append(best)

    # Independent small challengers prevent the residual path from becoming sacred.
    for name in FEATURES:
        model = fit_model(xs, ys, [name])
        candidates[model.features] = model

    for name in FEATURES:
        if name == "x":
            continue
        model = fit_model(xs, ys, ["x", name])
        candidates[model.features] = model

    return list(candidates.values())


def choose_measurement(a: Model, b: Model, xs: Iterable[float]) -> tuple[float, float]:
    scored = [(abs(a.predict(x) - b.predict(x)), x) for x in xs]
    disagreement, x = max(scored)
    return x, disagreement


def evaluate_world(world: str, seed: int) -> Evaluation:
    truth = WORLD_FNS[world]
    rng = random.Random(seed)

    train_x = grid(-2.0, 2.0, 40)
    train_y = [truth(x) + rng.gauss(0.0, NOISE_SD) for x in train_x]

    heldout_x = grid(-2.0, 2.0, 40, midpoint=True)
    heldout_y = [truth(x) for x in heldout_x]

    challenge_x = grid(-3.0, 3.0, 81)
    challenge_y = [truth(x) for x in challenge_x]

    candidates = propose_candidates(train_x, train_y)
    ranked = sorted(candidates, key=lambda m: rmse(m, heldout_x, heldout_y))
    best, second = ranked[0], ranked[1]

    heldout_error = rmse(best, heldout_x, heldout_y)
    challenge_error = rmse(best, challenge_x, challenge_y)

    residuals = [
        abs(best.predict(x) - y) for x, y in zip(challenge_x, challenge_y)
    ]
    idx = max(range(len(residuals)), key=residuals.__getitem__)
    max_residual = residuals[idx]
    falsification_x = challenge_x[idx]

    measurement_grid = grid(-3.0, 3.0, 121)
    measurement_x, measurement_disagreement = choose_measurement(
        best, second, measurement_grid
    )

    # Assert the measurement proposal is actually the maximum-disagreement point.
    all_disagreements = [
        abs(best.predict(x) - second.predict(x)) for x in measurement_grid
    ]
    assert math.isclose(
        measurement_disagreement,
        max(all_disagreements),
        rel_tol=0.0,
        abs_tol=1e-12,
    )

    certified = (
        heldout_error <= HELDOUT_RMSE_MAX
        and challenge_error <= CHALLENGE_RMSE_MAX
        and max_residual <= MAX_RESIDUAL_MAX
    )

    return Evaluation(
        world=world,
        model=best,
        heldout_rmse=heldout_error,
        challenge_rmse=challenge_error,
        max_residual=max_residual,
        falsification_x=falsification_x,
        falsification_residual=max_residual,
        measurement_x=measurement_x,
        measurement_disagreement=measurement_disagreement,
        certified=certified,
    )


def modeled_real_world_authority(adversarial_power: float) -> float:
    """Toy monotone authority cap: stronger red-team power never increases authority."""
    adversarial_power = min(1.0, max(0.0, adversarial_power))
    return 1.0 - 0.75 * adversarial_power


def main() -> None:
    digest = schedule_digest()
    assert digest == EXPECTED_SCHEDULE_SHA256, (digest, EXPECTED_SCHEDULE_SHA256)

    results = [evaluate_world(world, seed) for world, seed in WORLD_SCHEDULE]
    by_name = {result.world: result for result in results}

    # Frozen behavior: representable worlds may certify, OOD worlds must not.
    assert all(by_name[name].certified for name in IN_GRAMMAR)
    assert all(not by_name[name].certified for name in OUT_OF_GRAMMAR)

    # Every selected candidate must expose a concrete falsification target.
    assert all(math.isfinite(r.falsification_x) for r in results)
    assert all(r.falsification_residual >= 0.0 for r in results)

    # Residual laundering trap: exponential OOD looks good in-range, fails wider test.
    exp_result = by_name["exp_ood"]
    assert exp_result.heldout_rmse <= HELDOUT_RMSE_MAX
    assert exp_result.challenge_rmse > CHALLENGE_RMSE_MAX
    assert not exp_result.certified

    # Stronger adversarial search cannot imply greater modeled real-world authority.
    powers = [0.0, 0.25, 0.5, 0.75, 1.0]
    authorities = [modeled_real_world_authority(p) for p in powers]
    assert all(b <= a for a, b in zip(authorities, authorities[1:]))

    print("OPEN_WORLD_GENESIS_CRUCIBLE=PASS")
    print(f"SCHEDULE_SHA256={digest}")
    for r in results:
        print(
            f"{r.world:10s} "
            f"features={'+'.join(r.model.features):12s} "
            f"heldout={r.heldout_rmse:.6f} "
            f"challenge={r.challenge_rmse:.6f} "
            f"max_residual={r.max_residual:.6f} "
            f"certified={str(r.certified).lower()} "
            f"falsify_x={r.falsification_x:.3f} "
            f"measure_x={r.measurement_x:.3f}"
        )


if __name__ == "__main__":
    main()
