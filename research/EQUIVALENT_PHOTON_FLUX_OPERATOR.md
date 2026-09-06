# Equivalent Photon Flux Operator

Status: candidate domain-scoped scientific operator. Not canonical.

## Formula

The user-supplied formula is incorporated in differential form as

```text
dn_gamma(x)
= (2 Z^2 alpha / pi) (dx / x)
  [ ln(u(Z) / x) - 1/2 ]
```

or equivalently

```text
dn_gamma/dx
= (2 Z^2 alpha / (pi x))
  [ ln(u(Z) / x) - 1/2 ]
```

where `x` is the photon energy fraction, `Z` is the source charge number, `alpha` is the fine-structure constant, and `u(Z)` is treated by REI as a domain/model input whose provenance must be supplied rather than silently invented.

## REI integration

This becomes a physics-domain operator for equivalent-photon / ultraperipheral-collision reasoning:

```text
PhysicsTask
-> DomainCheck(EPA / ultraperipheral collision)
-> ParameterProvenance(Z, alpha, x, u)
-> ApproximationValidityCheck
-> EquivalentPhotonFlux
-> Prediction / Uncertainty / Falsification
```

It is not a generic weighting law, probability law, epistemic score, authority function, or universal REI update equation.

```text
EPAFormula != UniversalREIFormula
PhysicalFlux != EpistemicAuthority
LargeZ != HigherTruth
```

## Domain guard

The operator may evaluate only when:

```text
Z > 0
alpha > 0
0 < x < 1
u > 0
ln(u/x) - 1/2 > 0
```

If the logarithmic bracket becomes non-positive, the implementation returns `ABSTAIN_OUTSIDE_APPROXIMATION` rather than emitting an unphysical negative photon density.

The operator does not infer `u(Z)` from `Z` alone. A task must provide the adopted ultraperipherality / cutoff parameter and its provenance or uncertainty model.

## Scientific use in REI

The operator can support:

- scale-resolved photon-flux estimates in the EPA regime;
- hypothesis generation for photon-induced processes;
- sensitivity analysis with respect to `Z`, `x`, and `u`;
- comparison of competing cutoff/form-factor assumptions;
- DeathEye/Wuji pressure against extrapolation outside the frozen approximation domain.

For a fixed admissible `x` and `u`, the formula gives the explicit charge scaling

```text
Flux ~ Z^2
```

but REI must not turn this local model property into a universal causal statement outside the EPA task scope.

## Falsification hooks

```text
DomainMismatch => ABSTAIN
MissingUProvenance => ABSTAIN
NonPositiveBracket => ABSTAIN_OUTSIDE_APPROXIMATION
NonFiniteParameter => INVALID_INPUT
NegativeOrZeroZ => INVALID_INPUT
```

A later external scientific task may compare this approximation against a fuller form-factor calculation. Failure is preserved rather than hidden.

## Authority boundary

```text
FormulaAuthority = 0
ExperimentAuthority = 0
DeploymentAuthority = 0
CanonicalPromotionAuthority = 0
```

Adding a validated physics formula expands REI's domain vocabulary; it does not close G3-G13 or establish frontier superiority.
