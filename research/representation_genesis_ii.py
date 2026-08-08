import hashlib
import json
import math
from dataclasses import dataclass

TRAIN = [-1.5 + 3.0 * i / 24 for i in range(25)]
HELDOUT = [-1.425 + 2.85 * i / 18 for i in range(19)]
CHALLENGE = [-3.0 + 6.0 * i / 60 for i in range(61)]
SIGNATURE_GRID = [-2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0]
MEASUREMENT_GRID = CHALLENGE

MAX_COMPLEXITY = 9
GENERATION_ROUNDS = 3
HELDOUT_LIMIT = 0.10
WIDER_RMSE_LIMIT = 0.05
MAX_RESIDUAL_LIMIT = 0.15

SCHEDULE = [
    {"name": "quadratic", "formula": "0.7+1.3*(x*x)", "representable": True},
    {"name": "cubic_drift", "formula": "-0.2+0.8*((x*x*x)-x)", "representable": True},
    {"name": "double_sine", "formula": "0.1+1.2*sin(x+x)", "representable": True},
    {"name": "x_sin", "formula": "-0.1+1.5*(x*sin(x))", "representable": True},
    {"name": "abs_quad_shift", "formula": "0.2+0.9*abs((x*x)-x)", "representable": True},
    {"name": "exp_ood", "formula": "exp(0.9*x)", "representable": False},
    {"name": "step_ood", "formula": "1 if x>0.3 else -1", "representable": False},
]
EXPECTED_SCHEDULE_SHA256 = "bbee6443f47552dd2a11cbe17e06adaa1c01d3d074650cafdd6fe7dd653c7700"


def canonical_schedule_digest():
    payload = json.dumps(SCHEDULE, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def evaluate(expr, x):
    op = expr[0]
    if op == "x":
        return x
    if op == "sin":
        return math.sin(evaluate(expr[1], x))
    if op == "abs":
        return abs(evaluate(expr[1], x))
    if op == "add":
        return evaluate(expr[1], x) + evaluate(expr[2], x)
    if op == "sub":
        return evaluate(expr[1], x) - evaluate(expr[2], x)
    if op == "mul":
        return evaluate(expr[1], x) * evaluate(expr[2], x)
    raise ValueError(op)


def complexity(expr):
    if expr[0] == "x":
        return 1
    if expr[0] in {"sin", "abs"}:
        return 1 + complexity(expr[1])
    return 1 + complexity(expr[1]) + complexity(expr[2])


def render(expr):
    op = expr[0]
    if op == "x":
        return "x"
    if op == "sin":
        return f"sin({render(expr[1])})"
    if op == "abs":
        return f"abs({render(expr[1])})"
    symbol = {"add": "+", "sub": "-", "mul": "*"}[op]
    return f"({render(expr[1])}{symbol}{render(expr[2])})"


def semantic_signature(expr):
    values = []
    for x in SIGNATURE_GRID:
        y = evaluate(expr, x)
        if not math.isfinite(y) or abs(y) > 100.0:
            return None
        values.append(round(y, 8))
    return tuple(values)


def synthesize_expressions():
    simplest_by_signature = {}
    x_expr = ("x",)
    simplest_by_signature[semantic_signature(x_expr)] = x_expr

    for _ in range(GENERATION_ROUNDS):
        base = list(simplest_by_signature.values())
        proposals = []

        for a in base:
            for op in ("sin", "abs"):
                candidate = (op, a)
                if complexity(candidate) <= MAX_COMPLEXITY:
                    proposals.append(candidate)

        for a in base:
            for b in base:
                for op in ("add", "sub", "mul"):
                    candidate = (op, a, b)
                    if complexity(candidate) <= MAX_COMPLEXITY:
                        proposals.append(candidate)

        for candidate in proposals:
            sig = semantic_signature(candidate)
            if sig is None:
                continue
            incumbent = simplest_by_signature.get(sig)
            if incumbent is None or complexity(candidate) < complexity(incumbent):
                simplest_by_signature[sig] = candidate

    return list(simplest_by_signature.values()), simplest_by_signature


def world_function(name):
    if name == "quadratic":
        return lambda x: 0.7 + 1.3 * (x * x)
    if name == "cubic_drift":
        return lambda x: -0.2 + 0.8 * ((x * x * x) - x)
    if name == "double_sine":
        return lambda x: 0.1 + 1.2 * math.sin(x + x)
    if name == "x_sin":
        return lambda x: -0.1 + 1.5 * (x * math.sin(x))
    if name == "abs_quad_shift":
        return lambda x: 0.2 + 0.9 * abs((x * x) - x)
    if name == "exp_ood":
        return lambda x: math.exp(0.9 * x)
    if name == "step_ood":
        return lambda x: 1.0 if x > 0.3 else -1.0
    raise ValueError(name)


def affine_fit(phi, target):
    n = len(target)
    mean_phi = sum(phi) / n
    mean_target = sum(target) / n
    denom = sum((p - mean_phi) ** 2 for p in phi)
    if denom <= 1e-14:
        beta1 = 0.0
    else:
        beta1 = sum((p - mean_phi) * (y - mean_target) for p, y in zip(phi, target)) / denom
    beta0 = mean_target - beta1 * mean_phi
    return beta0, beta1


def rmse(pred, truth):
    return math.sqrt(sum((p - y) ** 2 for p, y in zip(pred, truth)) / len(truth))


@dataclass
class Fit:
    expr: tuple
    beta0: float
    beta1: float
    heldout_rmse: float
    wider_rmse: float
    max_residual: float
    falsify_x: float

    def predict(self, x):
        return self.beta0 + self.beta1 * evaluate(self.expr, x)


def fit_expression(expr, truth_fn):
    train_truth = [truth_fn(x) for x in TRAIN]
    phi = [evaluate(expr, x) for x in TRAIN]
    beta0, beta1 = affine_fit(phi, train_truth)

    def pred(x):
        return beta0 + beta1 * evaluate(expr, x)

    held_truth = [truth_fn(x) for x in HELDOUT]
    held_pred = [pred(x) for x in HELDOUT]
    wider_truth = [truth_fn(x) for x in CHALLENGE]
    wider_pred = [pred(x) for x in CHALLENGE]
    residuals = [abs(y - p) for y, p in zip(wider_truth, wider_pred)]
    idx = max(range(len(residuals)), key=lambda i: residuals[i])
    return Fit(
        expr=expr,
        beta0=beta0,
        beta1=beta1,
        heldout_rmse=rmse(held_pred, held_truth),
        wider_rmse=rmse(wider_pred, wider_truth),
        max_residual=residuals[idx],
        falsify_x=CHALLENGE[idx],
    )


def certify(fit):
    return (
        fit.heldout_rmse <= HELDOUT_LIMIT
        and fit.wider_rmse <= WIDER_RMSE_LIMIT
        and fit.max_residual <= MAX_RESIDUAL_LIMIT
    )


def strongest_two(expressions, truth_fn):
    fits = [fit_expression(expr, truth_fn) for expr in expressions]
    fits.sort(key=lambda f: (f.heldout_rmse, complexity(f.expr), render(f.expr)))
    return fits[0], fits[1]


def measurement_proposal(a, b):
    disagreements = [abs(a.predict(x) - b.predict(x)) for x in MEASUREMENT_GRID]
    idx = max(range(len(disagreements)), key=lambda i: disagreements[i])
    return MEASUREMENT_GRID[idx], disagreements[idx]


def modeled_real_world_authority(adversarial_power):
    # This research module has no real-world execution authority. The monotone
    # function is intentionally non-increasing as adversarial search increases.
    return max(0.0, 1.0 - adversarial_power)


def main():
    assert canonical_schedule_digest() == EXPECTED_SCHEDULE_SHA256

    expressions, simplest = synthesize_expressions()
    assert len(expressions) > 100

    # The atom set contains only x. These useful structures must be synthesized.
    required_composites = [
        ("mul", ("x",), ("x",)),
        ("sub", ("mul", ("x",), ("mul", ("x",), ("x",))), ("x",)),
        ("sin", ("add", ("x",), ("x",))),
        ("mul", ("x",), ("sin", ("x",))),
        ("abs", ("sub", ("mul", ("x",), ("x",)), ("x",))),
    ]
    generated_signatures = {semantic_signature(e) for e in expressions}
    for expr in required_composites:
        assert semantic_signature(expr) in generated_signatures

    # Semantic deduplication retains x rather than a more complex equivalent x+(x-x).
    redundant_x = ("add", ("x",), ("sub", ("x",), ("x",)))
    assert render(simplest[semantic_signature(redundant_x)]) == "x"

    results = []
    for item in SCHEDULE:
        truth_fn = world_function(item["name"])
        best, second = strongest_two(expressions, truth_fn)
        measure_x, disagreement = measurement_proposal(best, second)
        is_certified = certify(best)

        max_disagreement = max(abs(best.predict(x) - second.predict(x)) for x in MEASUREMENT_GRID)
        assert abs(disagreement - max_disagreement) <= 1e-12
        assert best.falsify_x in CHALLENGE

        if item["representable"]:
            assert is_certified, (item["name"], render(best.expr), best)
            assert complexity(best.expr) > 1
        else:
            assert not is_certified, (item["name"], render(best.expr), best)

        results.append((item["name"], best, measure_x, is_certified))

    # Residual-laundering trap: exp looks acceptable in-range but fails wider challenge.
    exp_best = next(best for name, best, _, _ in results if name == "exp_ood")
    assert exp_best.heldout_rmse <= HELDOUT_LIMIT
    assert exp_best.wider_rmse > WIDER_RMSE_LIMIT
    assert exp_best.max_residual > MAX_RESIDUAL_LIMIT

    powers = [0.0, 0.25, 0.5, 0.75, 1.0]
    authorities = [modeled_real_world_authority(p) for p in powers]
    assert all(authorities[i + 1] <= authorities[i] for i in range(len(authorities) - 1))

    print("REPRESENTATION_GENESIS_II=PASS")
    print(f"SCHEDULE_SHA256={canonical_schedule_digest()}")
    print(f"GENERATED_UNIQUE_EXPRESSIONS={len(expressions)}")
    for name, best, measure_x, is_certified in results:
        print(
            f"{name:14s} expr={render(best.expr):28s} "
            f"complexity={complexity(best.expr):2d} "
            f"heldout={best.heldout_rmse:.6f} "
            f"challenge={best.wider_rmse:.6f} "
            f"max_residual={best.max_residual:.6f} "
            f"certified={str(is_certified).lower()} "
            f"falsify_x={best.falsify_x:.3f} "
            f"measure_x={measure_x:.3f}"
        )


if __name__ == "__main__":
    main()
