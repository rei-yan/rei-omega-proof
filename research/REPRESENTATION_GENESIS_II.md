# REI-Ω Representation Genesis II · Compositional Forge

Status: research module

This module extends the Open-World Genesis Crucible from **selecting among human-specified basis functions** to **constructing new bounded symbolic representations by composition**.

It is deliberately finite and fallible. It does not claim unrestricted concept invention, autonomous scientific discovery, AGI, universal superiority, or production reliability.

## 1. Core transition

The previous crucible searched a fixed basis set. Representation Genesis II begins from a much smaller primitive vocabulary and composes candidate expressions:

```text
Primitive
-> Compose
-> Deduplicate
-> Fit
-> Falsify
-> Measure
-> WiderChallenge
-> CertifyOrAbstain
-> Record
```

The target research property is:

```text
REI can construct a useful representation that was not present as an initial atomic feature.
```

This is bounded compositional synthesis, not unrestricted invention of arbitrary mathematics.

## 2. Primitive language

The initial atomic representation contains only:

```text
x
```

The allowed operators are:

```text
add(a,b)
sub(a,b)
mul(a,b)
sin(a)
abs(a)
```

Expressions are generated only up to a frozen complexity bound. The system is therefore capable of constructing expressions such as:

```text
x*x
(x*x*x)-x
sin(x+x)
x*sin(x)
abs((x*x)-x)
```

without those expressions being supplied as atomic features.

The operators themselves remain human-specified. That limitation is explicit.

## 3. Candidate synthesis and semantic deduplication

The generator recursively composes expressions and removes numerical duplicates using a frozen semantic signature grid.

Two syntactically different expressions that evaluate identically on the signature grid are treated as the same candidate, with the lower-complexity expression preferred.

This controls combinatorial growth and introduces a simple form of representation compression.

```text
EquivalentBehavior -> PreferLowerComplexity
```

## 4. Frozen world schedule

The deterministic internal schedule contains five worlds that can be represented by compositions of the primitive language and two worlds deliberately outside the grammar:

```text
quadratic
cubic_drift
double_sine
x_sin
abs_quad_shift
exp_ood
step_ood
```

The canonical schedule SHA-256 is:

```text
bbee6443f47552dd2a11cbe17e06adaa1c01d3d074650cafdd6fe7dd653c7700
```

This freezes an internal research sanity schedule only. It is not an external oracle and does not satisfy G3 independence.

## 5. Generated representation fitting

Each generated expression `phi(x)` receives an affine calibration:

```text
y_hat = beta_0 + beta_1 * phi(x)
```

Candidates are ranked on held-out error with complexity used as a deterministic tie-breaker.

A candidate is never certified from held-out fit alone.

## 6. Counterexample-first challenge

For the selected candidate `C`, the forge searches a wider challenge interval and exposes the maximum-residual point:

```text
z*(C) = argmax_z |y_true(z) - y_hat_C(z)|
```

Certification requires all frozen adequacy gates:

```text
HeldOutRMSE <= H
AND WiderChallengeRMSE <= W
AND MaxChallengeResidual <= R
```

This preserves:

```text
ApproximationSuccess != StructuralTruth
AdequacyBeforeRanking
```

## 7. Measurement Genesis

The strongest two candidates are compared over a frozen admissible measurement grid. The next proposed measurement is where their predictions disagree most:

```text
m* = argmax_x |C1(x) - C2(x)|
```

This remains a bounded discrimination heuristic, not a general experimental-design theorem.

## 8. Out-of-grammar honesty

The exponential and step worlds are intentionally not representable by the current grammar within the frozen complexity bound.

The exponential case is especially important: a generated polynomial-like composite can look acceptable on the held-out in-range set while failing badly on the wider challenge interval.

Required behavior:

```text
LooksGoodInside
AND FailsWiderChallenge
=> Abstain
```

The system must not expand its truth claim merely because its current grammar produced the least-bad approximation.

## 9. Generator / judge separation

The expression generator cannot rewrite:

```text
world schedule
adequacy thresholds
challenge interval
signature grid
pass conditions
```

after seeing results.

The research roles remain separated:

```text
Generator != Falsifier != Verifier != Approver != Executor
```

## 10. Red Crucible boundary

Adversarial search remains restricted to synthetic worlds, REI-owned models, sandboxes, digital twins, and authorized test environments.

```text
AdversarialPower increases
=> RealWorldFreedom does not increase
```

This module grants no real-world attack authority.

## 11. Deterministic pass conditions

`research/representation_genesis_ii.py` must demonstrate:

1. the frozen schedule digest matches the committed SHA-256;
2. the generator starts from atomic `x` and constructs composite representations;
3. all five representable worlds are certified;
4. both out-of-grammar worlds are refused certification;
5. the exponential OOD world can pass the in-range held-out tolerance while failing the wider challenge;
6. every selected candidate exposes a falsification point;
7. every world produces a maximum-disagreement measurement proposal;
8. semantic deduplication prefers lower-complexity equivalent expressions;
9. stronger modeled adversarial power never increases modeled real-world authority.

A failing run must remain a visible failure and must not be converted to green by silently changing the frozen meaning of the gates.

## 12. What this actually proves

A successful run proves only that the deterministic bounded compositional forge behaves as specified on this toy schedule.

It does **not** prove that REI can invent arbitrary mathematical primitives, discover unknown physical laws, outperform frontier AI systems, or generalize to unrestricted real-world science.

The next meaningful escalation is **Prospective Genesis**: freeze a generator and evaluation protocol before future or externally hidden observations are known, then test whether a newly synthesized representation predicts those observations better than fixed strong baselines.