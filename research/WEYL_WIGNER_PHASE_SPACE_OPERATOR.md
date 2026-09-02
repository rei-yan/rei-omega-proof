# Weyl-Wigner Phase-Space Operator

Status: candidate domain-scoped scientific representation operator. Not canonical.

## Formula set

The user-supplied phase-space formulas are integrated using the standard one-degree-of-freedom Weyl-Wigner convention:

```text
A_W(q,p)
= ∫ dξ exp(-i p ξ / ħ)
    <q + ξ/2 | Â | q - ξ/2>
```

Inverse map:

```text
Â
= (1 / 2πħ) ∫ dq dp A_W(q,p) Δ̂(q,p)
```

Trace-pair identity:

```text
Tr(Â B̂)
= (1 / 2πħ) ∫ dq dp A_W(q,p) B_W(q,p)
```

Phase-point kernel:

```text
Δ̂(q,p)
= ∫ dξ exp(+i p ξ / ħ)
    |q + ξ/2><q - ξ/2|
```

Different references distribute normalization factors differently. REI therefore freezes the convention with every calculation rather than mixing formulas across conventions.

## REI integration

This operator plugs into Representation Genesis as a reversible, domain-bounded representation bridge:

```text
QuantumOperatorRepresentation
        |
        v
WeylTransform
        |
        v
PhaseSpaceRepresentation
        |
        +--> phase-space comparison
        +--> semiclassical inspection
        +--> trace-overlap evaluation
        +--> representation stress testing
        |
        v
InverseWeylTransform
```

The gain is not "quantum magic". It is a disciplined way to expose the same quantum object in two representations and test whether a conclusion survives the representation change.

```text
RepresentationChange != NewPhysicalLaw
EquivalentRepresentation != EquivalentInterpretation
WignerNegativity != ClassicalProbability
```

## Domain guard

Activate only for tasks that explicitly satisfy a quantum phase-space/operator setting with a declared `ħ` and normalization convention.

```text
QuantumPhaseSpaceTask = true
hbar > 0
NormalizationConvention = FROZEN
OperatorDomain = DECLARED
```

Otherwise:

```text
DOMAIN_MISMATCH => ABSTAIN
```

REI must not reinterpret `A_W(q,p)` as a generic probability distribution. For density operators, the Wigner function is a quasiprobability representation and may take negative values.

## Why it helps REI

The operator strengthens four existing REI ideas:

1. **Representation Genesis**: the same object can be examined in operator and phase-space coordinates.
2. **DeathEye / Wuji**: conclusions that vanish under a legitimate representation transform receive counterexample pressure.
3. **Multi-World / Multi-Representation Transfer**: invariants can be separated from coordinate artifacts.
4. **Scientific Adapter**: quantum-mechanical hypotheses can declare their representation and normalization explicitly.

A useful REI invariant is the trace-pair relation:

```text
OperatorOverlap
<->
PhaseSpaceOverlap
```

When the frozen convention and mathematical assumptions hold, the two descriptions must agree. A mismatch becomes a diagnostic signal rather than something to narratively smooth over.

## Normalization firewall

The implementation records:

```text
hbar
n_degrees_of_freedom
symbol_convention
inverse_prefactor
trace_prefactor
kernel_phase_sign
```

For `n` canonical degrees of freedom under this convention:

```text
inverse_prefactor = (2πħ)^(-n)
trace_prefactor   = (2πħ)^(-n)
```

Changing any of these fields creates a new representation contract.

## Authority boundary

```text
RepresentationAuthority = 0
PhysicalLawCreationAuthority = 0
ExperimentAuthority = 0
CanonicalPromotionAuthority = 0
```

This is a precise representation operator, not a proof of universal quantum capability and not evidence for G3-G13.
