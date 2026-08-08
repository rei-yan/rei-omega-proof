# REI-Ω Primitive Genesis I · 原语创生炉

Status: research module

Primitive Genesis I advances the Representation Genesis II forge from composing existing symbolic operators to **residual-triggered induction of new parameterized primitives relative to a frozen scaffold**.

It is intentionally bounded and fallible. It does not claim arbitrary invention of mathematics, autonomous scientific discovery, AGI, universal superiority, or production reliability.

## 1. Core transition

The frozen scaffold for this crucible contains only:

```text
1
x
```

If that scaffold cannot satisfy the frozen adequacy gates, the primitive forge is allowed to propose a new parameterized primitive from a human-specified meta-grammar:

```text
ScaffoldFailure
-> TriggerPrimitiveForge
-> SearchPrimitiveParameters
-> Fit
-> HeldoutRank
-> WiderChallenge
-> Falsify
-> Measure
-> CertifyOrAbstain
-> Record
```

The research target is:

```text
REI can add a useful parameterized primitive that was not an atomic feature of the frozen scaffold.
```

This is a stricter claim than fixed-feature selection, but weaker than inventing arbitrary new operators from nothing.

## 2. Meta-grammar and limitation

The current primitive constructors are human-specified families:

```text
oscillator(w)
hinge(tau)
cusp(tau)
rbf(center, scale)
exponential(rate)
```

The system is not told which constructor or parameter belongs to a world. It searches the frozen parameter ranges and selects by held-out performance only.

The constructor families themselves remain human-designed. This limitation is explicit and permanent in the claim boundary.

Therefore:

```text
ParameterizedPrimitiveInduction != UnrestrictedPrimitiveInvention
```

## 3. Residual-trigger rule

A primitive is considered only when the frozen scaffold is inadequate.

```text
ScaffoldAdequate -> NoPrimitiveClaim
ScaffoldInadequate -> PrimitiveForgeMayRun
```

This prevents the system from manufacturing unnecessary conceptual machinery merely because a more ornate representation exists.

## 4. Frozen world schedule

The deterministic sanity schedule contains five worlds that require a new primitive relative to the scaffold and two worlds deliberately outside the current meta-grammar:

```text
freq_sine
hinge
shifted_cusp
rbf_bump
exp_growth
chirp_ood
saw_ood
```

The schedule SHA-256 is:

```text
e4acf6823251150077decdec5c2b3cb995eaf620abb9c8ac0977290ef41d29ab
```

This freezes only an internal research sanity schedule. It is not a sealed external oracle and does not satisfy G3 independence.

## 5. Candidate ranking and Reality veto

Primitive candidates are ranked using the frozen held-out set.

The wider challenge set is **not used to choose the candidate**. It is a later veto.

```text
Generate -> HeldoutRank -> FreezeWinner -> WiderChallenge
```

Certification requires:

```text
ScaffoldInadequate
AND HeldOutRMSE <= H
AND WiderChallengeRMSE <= W
AND MaxChallengeResidual <= R
```

Therefore an attractive in-range primitive can still be rejected by Reality outside the selection interval.

## 6. Primitive examples

The forge can induce parameterized forms such as:

```text
oscillator(w = learned frequency)
hinge(tau = learned breakpoint)
cusp(tau = learned cusp location)
rbf(center = learned, scale = learned)
exponential(rate = learned)
```

The target parameter is not supplied per world. It emerges from a frozen search over the constructor family.

## 7. Counterexample-first falsification

For the selected primitive model `C`, the forge exposes its worst point on the wider challenge interval:

```text
z*(C) = argmax_z |y_true(z) - y_hat_C(z)|
```

A candidate that violates the frozen residual gate cannot be certified merely because it won the held-out ranking.

## 8. Measurement Genesis coupling

The strongest two held-out candidates are compared over a frozen admissible measurement grid.

```text
m* = argmax_x |C1(x) - C2(x)|
```

This proposes the next observation where the competing induced primitives disagree most.

It remains a bounded discrimination heuristic, not a general theorem of optimal experimental design.

## 9. Out-of-meta-grammar honesty

The chirp and sawtooth worlds are deliberately not representable well enough by one current induced primitive plus the frozen scaffold.

Required behavior:

```text
BestAvailablePrimitiveStillFails
=> Unresolved / Abstain
```

The system must not promote the least-bad primitive into truth merely because it is the current winner.

## 10. Generator / judge separation

The primitive generator cannot rewrite after seeing results:

```text
world schedule
held-out set
challenge interval
adequacy thresholds
constructor parameter ranges
pass conditions
```

The wider challenge remains a judge, not a training signal for winner selection.

Research roles remain separated:

```text
Generator != Falsifier != Verifier != Approver != Executor
```

## 11. Red Crucible boundary

Adversarial search remains restricted to synthetic worlds, REI-owned models, sandboxes, digital twins, and authorized test environments.

```text
AdversarialPower increases
=> RealWorldFreedom does not increase
```

No real-world attack authority is introduced.

## 12. Deterministic pass conditions

`research/primitive_genesis_i.py` must demonstrate:

1. the frozen schedule digest matches the committed SHA-256;
2. all five target worlds fail the frozen scaffold before primitive induction;
3. all five target worlds become certifiable with an induced primitive;
4. the two out-of-meta-grammar worlds remain uncertified;
5. primitive winner ranking does not use the wider challenge set;
6. every selected candidate exposes a falsification point;
7. every world receives a maximum-disagreement measurement proposal;
8. stronger modeled adversarial power never increases modeled real-world authority.

A failing run is evidence. It must remain visible rather than being converted to green by silently redefining the gate.

## 13. What this actually proves

A successful run proves only that the deterministic bounded primitive-induction crucible behaves as specified on this toy schedule.

It does **not** prove that REI can invent arbitrary mathematical operators, discover unknown physical laws, outperform frontier AI systems, or generalize to unrestricted real-world science.

The next meaningful escalation is **Prospective Primitive Genesis**: freeze the scaffold, meta-grammar, generator, baselines, and evaluation protocol before future or externally hidden observations are revealed, then ask whether an induced primitive predicts those observations better than strong fixed baselines.
