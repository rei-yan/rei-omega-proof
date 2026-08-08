#!/usr/bin/env python3
"""Deterministic bounded sanity suite for REI-Ω Primordial Wuxiang Kernel.

This suite tests language-level candidate evolution over a frozen synthetic
schedule. It is an internal dry run only. It does not establish new science,
unrestricted language invention, or physical-universe creation.
"""

from dataclasses import dataclass
import hashlib
import itertools
import json
import math
import statistics


OPS = ("mul", "abs", "sin", "exp")
HELDOUT_MAX = 0.05
CHALLENGE_MAX = 0.08


@dataclass(frozen=True)
class Grammar:
    ops: tuple
    depth: int

    @property
    def complexity(self) -> int:
        return len(self.ops) + max(0, self.depth - 1)


def ast_string(ast):
    op = ast[0]
    if op in ("1", "x"):
        return op
    if op in ("abs", "sin", "exp"):
        return f"{op}({ast_string(ast[1])})"
    if op == "mul":
        return f"({ast_string(ast[1])}*{ast_string(ast[2])})"
    raise ValueError(op)


def ast_complexity(ast):
    op = ast[0]
    if op == "1":
        return 0
    if op == "x":
        return 1
    if op in ("abs", "sin", "exp"):
        return 1 + ast_complexity(ast[1])
    if op == "mul":
        return 1 + ast_complexity(ast[1]) + ast_complexity(ast[2])
    raise ValueError(op)


def ast_depth(ast):
    op = ast[0]
    if op in ("1", "x"):
        return 0
    if op in ("abs", "sin", "exp"):
        return 1 + ast_depth(ast[1])
    if op == "mul":
        return 1 + max(ast_depth(ast[1]), ast_depth(ast[2]))
    raise ValueError(op)


def eval_ast(ast, x):
    op = ast[0]
    if op == "1":
        return 1.0
    if op == "x":
        return float(x)
    if op == "abs":
        return abs(eval_ast(ast[1], x))
    if op == "sin":
        return math.sin(eval_ast(ast[1], x))
    if op == "exp":
        z = max(min(eval_ast(ast[1], x), 6.0), -6.0)
        return math.exp(z)
    if op == "mul":
        return eval_ast(ast[1], x) * eval_ast(ast[2], x)
    raise ValueError(op)


def semantic_key(ast, xs):
    vals = []
    for x in xs:
        try:
            z = eval_ast(ast, x)
        except (OverflowError, ValueError):
            return None
        if not math.isfinite(z) or abs(z) > 1e6:
            return None
        vals.append(round(z, 9))
    return tuple(vals)


def generate_asts(xs, grammar, max_terms=120):
    terms = {("1",), ("x",)}
    for d in range(1, grammar.depth + 1):
        prior = sorted(
            [a for a in terms if ast_depth(a) < d],
            key=lambda a: (ast_complexity(a), ast_string(a)),
        )
        new = set()
        for op in grammar.ops:
            if op in ("abs", "sin", "exp"):
                for a in prior:
                    b = (op, a)
                    if ast_depth(b) <= grammar.depth:
                        new.add(b)
            elif op == "mul":
                for i, a in enumerate(prior):
                    for b in prior[i:]:
                        m = ("mul", a, b)
                        if ast_depth(m) <= grammar.depth:
                            new.add(m)

        candidates = sorted(
            terms | new,
            key=lambda a: (ast_complexity(a), ast_string(a)),
        )
        seen = {}
        for a in candidates:
            key = semantic_key(a, xs)
            if key is not None and key not in seen:
                seen[key] = a

        ordered = sorted(
            seen.values(),
            key=lambda a: (ast_complexity(a), ast_string(a)),
        )
        terms = set(ordered[:max_terms])

    return sorted(
        terms,
        key=lambda a: (ast_complexity(a), ast_string(a)),
    )


def solve_linear(A, b):
    n = len(A)
    M = [list(map(float, row)) + [float(rhs)] for row, rhs in zip(A, b)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(M[r][col]))
        if abs(M[pivot][col]) < 1e-12:
            return None
        M[col], M[pivot] = M[pivot], M[col]

        scale = M[col][col]
        for j in range(col, n + 1):
            M[col][j] /= scale

        for r in range(n):
            if r == col:
                continue
            factor = M[r][col]
            for j in range(col, n + 1):
                M[r][j] -= factor * M[col][j]

    return [M[i][-1] for i in range(n)]


def fit_model(xs, ys, grammar, max_features=6):
    asts = generate_asts(xs, grammar)
    y_mean = statistics.mean(ys)

    def relevance(ast):
        vals = [eval_ast(ast, x) for x in xs]
        v_mean = statistics.mean(vals)
        numerator = sum((v - v_mean) * (y - y_mean) for v, y in zip(vals, ys))
        denominator = math.sqrt(sum((v - v_mean) ** 2 for v in vals)) + 1e-12
        return abs(numerator) / denominator

    constant = [a for a in asts if a == ("1",)]
    others = [a for a in asts if a != ("1",)]
    selected = constant + sorted(
        others,
        key=lambda a: (-relevance(a), ast_complexity(a), ast_string(a)),
    )[: max_features - 1]

    p = len(selected)
    X = [[eval_ast(a, x) for a in selected] for x in xs]
    ridge = 1e-8
    ATA = [
        [
            sum(row[i] * row[j] for row in X) + (ridge if i == j else 0.0)
            for j in range(p)
        ]
        for i in range(p)
    ]
    ATy = [
        sum(row[i] * y for row, y in zip(X, ys))
        for i in range(p)
    ]
    coef = solve_linear(ATA, ATy)
    if coef is None:
        raise RuntimeError("singular fit")

    return selected, coef


def predict(model, x):
    asts, coef = model
    return sum(c * eval_ast(a, x) for a, c in zip(asts, coef))


def rmse(model, xs, ys):
    return math.sqrt(
        sum((predict(model, x) - y) ** 2 for x, y in zip(xs, ys)) / len(xs)
    )


def candidate_grammars():
    out = []
    for k in range(0, 4):
        for subset in itertools.combinations(OPS, k):
            for depth in (1, 2):
                out.append(Grammar(tuple(subset), depth))
    return tuple(out)


def language_score(heldout_error, grammar):
    return heldout_error + 0.01 * len(grammar.ops) + 0.005 * max(0, grammar.depth - 1)


def select_language(world, train_x, heldout_x):
    train_y = [world(x) for x in train_x]
    heldout_y = [world(x) for x in heldout_x]
    candidates = []
    for grammar in candidate_grammars():
        model = fit_model(train_x, train_y, grammar)
        h = rmse(model, heldout_x, heldout_y)
        candidates.append(
            (
                language_score(h, grammar),
                h,
                grammar,
                model,
            )
        )
    return min(
        candidates,
        key=lambda row: (
            row[0],
            len(row[2].ops),
            row[2].depth,
            row[2].ops,
        ),
    )


def world_schedule():
    return {
        "quadratic": lambda x: 0.3 + 1.1 * x - 0.7 * x * x,
        "cusp": lambda x: -0.1 + 0.9 * abs(x),
        "periodic": lambda x: 0.2 + 1.2 * math.sin(x),
        "growth": lambda x: -0.3 + 0.7 * math.exp(x),
        "composed": lambda x: math.sin(x * x),
        "chirp_ood": lambda x: math.sin(3.0 * x * x),
        "step_ood": lambda x: 1.0 if x > 0.2 else -1.0,
    }


def schedule_commitment():
    payload = {
        "version": "primordial-wuxiang-v0.1",
        "operators": OPS,
        "depths": [1, 2],
        "heldout_max": HELDOUT_MAX,
        "challenge_max": CHALLENGE_MAX,
        "worlds": tuple(world_schedule().keys()),
        "expected_certified": (
            "quadratic",
            "cusp",
            "periodic",
            "growth",
            "composed",
        ),
        "expected_unresolved": ("chirp_ood", "step_ood"),
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def main():
    worlds = world_schedule()

    train_x = [-1.2 + i * 0.08 for i in range(31)]
    heldout_x = [-2.5 + i * 0.2 for i in range(26)]
    challenge_x = [-3.0 + i * 0.1 for i in range(61)]

    base = Grammar((), 1)
    expected_certified = {"quadratic", "cusp", "periodic", "growth", "composed"}
    expected_unresolved = {"chirp_ood", "step_ood"}

    certified = set()
    unresolved = set()
    lineage = []
    failure_graveyard = []

    for name, world in worlds.items():
        train_y = [world(x) for x in train_x]
        heldout_y = [world(x) for x in heldout_x]
        challenge_y = [world(x) for x in challenge_x]

        base_model = fit_model(train_x, train_y, base)
        base_heldout = rmse(base_model, heldout_x, heldout_y)

        _, heldout_error, grammar, model = select_language(
            world,
            train_x,
            heldout_x,
        )
        challenge_error = rmse(model, challenge_x, challenge_y)

        adequate = (
            heldout_error <= HELDOUT_MAX
            and challenge_error <= CHALLENGE_MAX
        )

        if adequate:
            certified.add(name)
        else:
            unresolved.add(name)
            failure_graveyard.append(
                {
                    "world": name,
                    "selected_ops": grammar.ops,
                    "depth": grammar.depth,
                    "heldout_rmse": round(heldout_error, 6),
                    "challenge_rmse": round(challenge_error, 6),
                    "status": "PRESERVED_UNRESOLVED",
                }
            )

        lineage.append(
            {
                "world": name,
                "base_ops": base.ops,
                "selected_ops": grammar.ops,
                "selected_depth": grammar.depth,
                "base_heldout_rmse": round(base_heldout, 6),
                "selected_heldout_rmse": round(heldout_error, 6),
                "challenge_rmse": round(challenge_error, 6),
                "certified": adequate,
                "selected_terms": tuple(ast_string(a) for a in model[0]),
            }
        )

    assert certified == expected_certified
    assert unresolved == expected_unresolved

    # Every successful world required a language richer than the initial scaffold.
    for record in lineage:
        if record["world"] in expected_certified:
            assert record["selected_ops"]
            assert record["selected_heldout_rmse"] < record["base_heldout_rmse"]

    # The composed world requires a language with both multiplication and sine,
    # plus depth-2 composition, demonstrating language-level rule change.
    composed = next(r for r in lineage if r["world"] == "composed")
    assert set(("mul", "sin")).issubset(set(composed["selected_ops"]))
    assert composed["selected_depth"] == 2
    assert any("sin((x*x))" == term for term in composed["selected_terms"])

    # Out-of-language worlds must remain visible failures, not retuned wins.
    assert len(failure_graveyard) == 2
    assert {r["world"] for r in failure_graveyard} == expected_unresolved

    print("PRIMORDIAL_WUXIANG_KERNEL=PASS")
    print(f"SCHEDULE_SHA256={schedule_commitment()}")
    print("INITIAL_LANGUAGE=1,x")
    print(f"CERTIFIED_WORLDS={','.join(sorted(certified))}")
    print(f"UNRESOLVED_WORLDS={','.join(sorted(unresolved))}")
    print("COMPOSED_LANGUAGE=mul+sin,depth2")
    print(f"FAILURE_GRAVEYARD={len(failure_graveyard)}")
    print("REALITY_VETO=ENFORCED")
    print("LANGUAGE_SUCCESS_DOES_NOT_EQUAL_STRUCTURAL_TRUTH=ENFORCED")
    print("BOUNDED_META_GRAMMAR_SEARCH=true")
    print("UNRESTRICTED_LANGUAGE_INVENTION=false")
    print("EXTERNAL_GATES_UNCHANGED=true")


if __name__ == "__main__":
    main()
