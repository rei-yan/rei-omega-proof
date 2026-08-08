#!/usr/bin/env python3
"""REI-Ω Primitive Genesis I: bounded residual-triggered primitive induction.

Toy research crucible only. It does not claim arbitrary operator invention,
scientific discovery, AGI, or real-world open-world reliability.
"""

import hashlib
import json
import math

SCHEDULE = {
    "worlds": [
        {"name": "freq_sine", "kind": "primitive_needed"},
        {"name": "hinge", "kind": "primitive_needed"},
        {"name": "shifted_cusp", "kind": "primitive_needed"},
        {"name": "rbf_bump", "kind": "primitive_needed"},
        {"name": "exp_growth", "kind": "primitive_needed"},
        {"name": "chirp_ood", "kind": "out_of_meta_grammar"},
        {"name": "saw_ood", "kind": "out_of_meta_grammar"},
    ],
    "train_range": [-1.2, 1.2],
    "challenge_range": [-2.4, 2.4],
    "version": "primitive-genesis-i-v1",
}
EXPECTED_SCHEDULE_SHA256 = "e4acf6823251150077decdec5c2b3cb995eaf620abb9c8ac0977290ef41d29ab"

HELDOUT_LIMIT = 0.03
CHALLENGE_LIMIT = 0.08
MAX_RESIDUAL_LIMIT = 0.20

TRAIN = [-1.2 + i * 0.12 for i in range(21)]
HELD = [-1.14 + i * 0.12 for i in range(20)]
CHALLENGE = [-2.4 + i * 0.06 for i in range(81)]
MEASURE_GRID = [-2.4 + i * 0.05 for i in range(97)]


def world(name, x):
    if name == "freq_sine":
        return 0.3 + 1.4 * math.sin(2.35 * x + 0.2)
    if name == "hinge":
        return 0.7 + 1.4 * x + 2.2 * max(0.0, x - 0.35)
    if name == "shifted_cusp":
        return -0.2 + 0.4 * x + 1.7 * abs(x + 0.4)
    if name == "rbf_bump":
        return 0.2 + 0.5 * x + 1.8 * math.exp(-((x - 0.45) / 0.6) ** 2)
    if name == "exp_growth":
        return -0.4 + 1.3 * math.exp(0.72 * x)
    if name == "chirp_ood":
        return math.sin(2.3 * x * x) + 0.15 * x
    if name == "saw_ood":
        t = (x + 1.7) / 0.7
        return 2.0 * (t - math.floor(t + 0.5)) + 0.1 * x
    raise KeyError(name)


def solve_linear(a, b):
    n = len(b)
    m = [list(map(float, a[i])) + [float(b[i])] for i in range(n)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(m[r][col]))
        if abs(m[pivot][col]) < 1e-12:
            raise ValueError("singular normal equation")
        m[col], m[pivot] = m[pivot], m[col]
        pv = m[col][col]
        for j in range(col, n + 1):
            m[col][j] /= pv
        for r in range(n):
            if r == col:
                continue
            factor = m[r][col]
            if factor == 0.0:
                continue
            for j in range(col, n + 1):
                m[r][j] -= factor * m[col][j]
    return [m[i][n] for i in range(n)]


def fit(features, xs, ys):
    p = len(features)
    gram = [[0.0] * p for _ in range(p)]
    rhs = [0.0] * p
    for x, y in zip(xs, ys):
        v = [fn(x) for _, fn in features]
        for i in range(p):
            rhs[i] += v[i] * y
            for j in range(p):
                gram[i][j] += v[i] * v[j]
    for i in range(p):
        gram[i][i] += 1e-8
    return solve_linear(gram, rhs)


def predict(features, beta, x):
    return sum(c * fn(x) for c, (_, fn) in zip(beta, features))


def rmse(features, beta, xs, ys):
    return math.sqrt(
        sum((y - predict(features, beta, x)) ** 2 for x, y in zip(xs, ys)) / len(xs)
    )


def scaffold():
    # This is the frozen pre-primitive language used by this crucible.
    return [("1", lambda x: 1.0), ("x", lambda x: x)]


def primitive_candidates():
    """Human-specified meta-constructors with data-selected parameters.

    The constructor families are NOT claimed to be invented by REI. The
    induced parameterized primitive is new relative to the frozen scaffold.
    """
    out = []

    # Oscillator primitive. Frequency is searched rather than supplied per world.
    for i in range(69):
        w = 0.60 + i * 0.05
        out.append(
            (
                "osc",
                {"w": round(w, 2)},
                [
                    (f"sin({w:.2f}x)", lambda x, w=w: math.sin(w * x)),
                    (f"cos({w:.2f}x)", lambda x, w=w: math.cos(w * x)),
                ],
            )
        )

    # Data-positioned hinge and cusp primitives.
    for i in range(49):
        tau = -1.20 + i * 0.05
        out.append(
            (
                "hinge",
                {"tau": round(tau, 2)},
                [(f"hinge@{tau:.2f}", lambda x, tau=tau: max(0.0, x - tau))],
            )
        )
        out.append(
            (
                "cusp",
                {"tau": round(tau, 2)},
                [(f"abs@{tau:.2f}", lambda x, tau=tau: abs(x - tau))],
            )
        )

    # Localized radial primitive with learned center and scale.
    for i in range(33):
        center = -0.80 + i * 0.05
        for scale in (0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.80, 1.00):
            out.append(
                (
                    "rbf",
                    {"c": round(center, 2), "s": scale},
                    [
                        (
                            f"rbf({center:.2f},{scale:.2f})",
                            lambda x, center=center, scale=scale: math.exp(
                                -((x - center) / scale) ** 2
                            ),
                        )
                    ],
                )
            )

    # Exponential primitive with learned rate.
    for i in range(121):
        k = -1.20 + i * 0.02
        if abs(k) < 0.10:
            continue
        out.append(
            (
                "exp",
                {"k": round(k, 2)},
                [(f"exp({k:.2f}x)", lambda x, k=k: math.exp(k * x))],
            )
        )
    return out


def evaluate(name):
    train_y = [world(name, x) for x in TRAIN]
    held_y = [world(name, x) for x in HELD]
    challenge_y = [world(name, x) for x in CHALLENGE]

    base = scaffold()
    base_beta = fit(base, TRAIN, train_y)
    base_held = rmse(base, base_beta, HELD, held_y)
    base_challenge = rmse(base, base_beta, CHALLENGE, challenge_y)

    # Primitive creation is triggered only because the frozen scaffold is inadequate.
    scaffold_adequate = (
        base_held <= HELDOUT_LIMIT and base_challenge <= CHALLENGE_LIMIT
    )

    ranked = []
    for kind, params, extra in primitive_candidates():
        features = base + extra
        try:
            beta = fit(features, TRAIN, train_y)
        except ValueError:
            continue
        held_error = rmse(features, beta, HELD, held_y)
        # IMPORTANT: ranking does not use the wider challenge set.
        ranked.append(
            (
                round(held_error, 12),
                len(extra),
                kind,
                json.dumps(params, sort_keys=True),
                params,
                features,
                beta,
            )
        )

    ranked.sort(key=lambda row: row[:4])
    best = ranked[0]
    second = ranked[1]

    def finalize(row):
        held_error, _, kind, _, params, features, beta = row
        challenge_error = rmse(features, beta, CHALLENGE, challenge_y)
        residuals = [
            abs(y - predict(features, beta, x))
            for x, y in zip(CHALLENGE, challenge_y)
        ]
        max_residual = max(residuals)
        falsify_x = CHALLENGE[residuals.index(max_residual)]
        certified = (
            (not scaffold_adequate)
            and held_error <= HELDOUT_LIMIT
            and challenge_error <= CHALLENGE_LIMIT
            and max_residual <= MAX_RESIDUAL_LIMIT
        )
        return {
            "kind": kind,
            "params": params,
            "features": features,
            "beta": beta,
            "held": held_error,
            "challenge": challenge_error,
            "max_residual": max_residual,
            "falsify_x": falsify_x,
            "certified": certified,
        }

    b = finalize(best)
    s = finalize(second)

    disagreements = [
        abs(
            predict(b["features"], b["beta"], x)
            - predict(s["features"], s["beta"], x)
        )
        for x in MEASURE_GRID
    ]
    measure_x = MEASURE_GRID[disagreements.index(max(disagreements))]

    return {
        "name": name,
        "base_held": base_held,
        "base_challenge": base_challenge,
        "scaffold_adequate": scaffold_adequate,
        "best": b,
        "second": s,
        "measure_x": measure_x,
        "max_disagreement": max(disagreements),
    }


def modeled_authority(adversarial_power):
    # Stronger red-team search must never buy greater real-world authority.
    return max(0.0, 1.0 - 0.8 * adversarial_power)


def main():
    canonical = json.dumps(SCHEDULE, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode()).hexdigest()
    assert digest == EXPECTED_SCHEDULE_SHA256

    results = [evaluate(item["name"]) for item in SCHEDULE["worlds"]]
    by_name = {r["name"]: r for r in results}

    # The old scaffold must genuinely fail before a new primitive is considered.
    for name in ("freq_sine", "hinge", "shifted_cusp", "rbf_bump", "exp_growth"):
        assert not by_name[name]["scaffold_adequate"], name
        assert by_name[name]["best"]["certified"], name

    # Family-level sanity. Hinge and cusp are affine-equivalent with the scaffold,
    # so either is acceptable for the hinge/cusp targets.
    assert by_name["freq_sine"]["best"]["kind"] == "osc"
    assert by_name["hinge"]["best"]["kind"] in {"hinge", "cusp"}
    assert by_name["shifted_cusp"]["best"]["kind"] in {"hinge", "cusp"}
    assert by_name["rbf_bump"]["best"]["kind"] == "rbf"
    assert by_name["exp_growth"]["best"]["kind"] == "exp"

    # The deliberately out-of-meta-grammar worlds must remain unresolved.
    assert not by_name["chirp_ood"]["best"]["certified"]
    assert not by_name["saw_ood"]["best"]["certified"]

    # Every selected model exposes a falsification point and a measurement proposal.
    for result in results:
        assert result["best"]["falsify_x"] in CHALLENGE
        assert result["measure_x"] in MEASURE_GRID
        # Recompute the maximum-disagreement rule explicitly.
        b = result["best"]
        s = result["second"]
        values = [
            abs(
                predict(b["features"], b["beta"], x)
                - predict(s["features"], s["beta"], x)
            )
            for x in MEASURE_GRID
        ]
        assert abs(max(values) - result["max_disagreement"]) < 1e-12

    # Adversarial power cannot increase modeled real-world authority.
    powers = [i / 10.0 for i in range(11)]
    authorities = [modeled_authority(p) for p in powers]
    assert all(authorities[i + 1] <= authorities[i] for i in range(len(authorities) - 1))

    print("PRIMITIVE_GENESIS_I=PASS")
    print(f"SCHEDULE_SHA256={digest}")
    print(f"PRIMITIVE_CANDIDATES={len(primitive_candidates())}")
    for result in results:
        b = result["best"]
        print(
            f"{result['name']:14s} primitive={b['kind']:5s} params={json.dumps(b['params'], sort_keys=True):18s} "
            f"base_hold={result['base_held']:.6f} held={b['held']:.6f} "
            f"challenge={b['challenge']:.6f} max_residual={b['max_residual']:.6f} "
            f"certified={str(b['certified']).lower()} falsify_x={b['falsify_x']:.3f} "
            f"measure_x={result['measure_x']:.3f}"
        )


if __name__ == "__main__":
    main()
