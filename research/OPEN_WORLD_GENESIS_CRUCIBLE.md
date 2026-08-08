# REI-Ω Open-World Genesis Crucible

Status: research module

The Open-World Genesis Crucible extends the Genesis Kernel with a deliberately fallible discovery test. The purpose is to test whether REI can propose representations and measurements, falsify its own candidates, and abstain when the available representation grammar is inadequate.

This is not a claim of autonomous scientific discovery, AGI, universal superiority, or open-world reliability.

## 1. Core objective

```text
UnknownWorld
-> Observe
-> ProposeRepresentations
-> FitCandidateModels
-> GenerateCounterexamples
-> ProposeDiscriminatingMeasurement
-> ChallengeOutsideTrainingRange
-> CertifyOrAbstain
-> RecordFailure
```

The crucial rule is:

```text
ApproximationSuccess != StructuralTruth
```

A low in-sample error is insufficient for certification.

## 2. Frozen research world schedule

The deterministic internal schedule contains five worlds that are representable by the current finite grammar and two worlds deliberately outside that grammar.

```text
linear
quadratic
cubic
absolute-value
sinusoidal
exponential OOD
step OOD
```

The schedule is frozen by SHA-256:

```text
19a699ac17503eebb30679f4ba297051826a46952ac27b353c04ed3e3f90fc00
```

This commitment freezes the internal sanity schedule only. It is not an external sealed oracle and does not satisfy G3 independence.

## 3. Representation proposal

The current research grammar is intentionally finite:

```text
x
x^2
x^3
abs(x)
sin(1.3x)
```

The system searches candidate representations and small combinations rather than being told which one is correct for each world.

This is bounded representation genesis, not unrestricted concept invention. The grammar remains human-specified and is an explicit limitation.

## 4. Candidate fitting

Each candidate is an affine model over its proposed representation:

```text
y_hat = beta_0 + sum_k beta_k phi_k(x)
```

Candidates are ranked on held-out points, then challenged on a wider interval than the training interval.

The wider challenge interval is designed to expose residual laundering, where a flexible approximation looks excellent inside the observed region but fails outside it.

## 5. Falsification-first rule

For every selected candidate, the crucible searches the challenge grid for the point with the largest absolute residual:

```text
z*(C) = argmax_z |y_true(z) - y_hat_C(z)|
```

This is a finite-grid approximation to the broader DeathEye / Minimal Falsification Operator idea.

A candidate with a decisive counterexample cannot be certified merely because its validation score is good.

## 6. Measurement Genesis

The two strongest surviving candidates are compared over an admissible measurement grid. The next measurement proposal is the point of maximum prediction disagreement:

```text
m* = argmax_x |C_1(x) - C_2(x)|
```

This is a simple discrimination-gain proxy. It tests the ordering principle:

```text
WhenModelsDisagree -> MeasureWhereTheyDisagreeMost
```

It is not yet a general Bayesian experimental-design engine.

## 7. Adequacy before ranking

Certification requires all three:

```text
HeldOutRMSE <= threshold
AND WiderChallengeRMSE <= threshold
AND MaxChallengeResidual <= threshold
```

Therefore a candidate that fits the observed interval but fails outside it is rejected.

The intended behavior is:

```text
RepresentableWorld -> CandidateMayBeCertified
OutOfGrammarWorld -> Abstain / Unresolved
```

No candidate may declare the world representable merely by selecting itself.

## 8. Open-world honesty

The crucible includes two intentionally out-of-grammar worlds. Passing requires refusing to certify them.

```text
UnknownButLooksGoodInside
AND FailsWiderChallenge
=> Abstain
```

This preserves the earlier REI principle:

```text
Adequacy Before Ranking
```

and the permanent failure lesson:

```text
ModelClassBlindness is itself a failure mode.
```

## 9. Generator and judge separation

The representation generator does not control the adequacy thresholds or the wider challenge set.

```text
Generator != Falsifier != Verifier
```

The candidate generator is not allowed to rewrite the score after seeing results.

## 10. Red Crucible boundary

Adversarial search in this module is limited to synthetic worlds, REI-owned models, sandboxes, digital twins, and authorized test environments.

```text
AdversarialPower increases
=> RealWorldFreedom does not increase
```

This module grants no real-world attack authority.

## 11. Deterministic pass conditions

`research/open_world_genesis_crucible.py` must show:

1. the frozen schedule digest matches the committed SHA-256;
2. all five in-grammar worlds are certified under the frozen thresholds;
3. both out-of-grammar worlds are refused certification;
4. each selected model has an explicit falsification point;
5. the proposed measurement maximizes disagreement over the admissible grid;
6. an out-of-grammar world can look deceptively good on the held-out in-range set and still be rejected by the wider challenge;
7. stronger adversarial search does not imply greater modeled real-world authority.

A failure is to be preserved and investigated rather than hidden by retuning the criterion after the run.

## 12. Research boundary

A successful sanity run proves only that this deterministic toy crucible behaves as specified. It does not prove that REI can invent arbitrary new scientific representations, discover new physical laws, outperform frontier AI systems, or generalize to unrestricted real-world science.

The next meaningful escalation after this crucible is external prospective evaluation on data or experiments whose answers were genuinely unknown at freeze time.