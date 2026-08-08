# REI-Ω Ohmic Constraint Layer

Status: research module

This module extends REI-Ω with an electrically grounded constitutive layer without modifying the frozen G2 proof kernel or G3 replication challenge.

## 1. Local constitutive law

For a passive resistive element:

```text
V = I R
G = 1 / R
I = G V
```

with `R > 0` and `G > 0`.

The role of this layer is not to treat Ohm's law as a universal law for every domain. It is a typed physical constraint that is active only when the modeled element is explicitly declared to be Ohmic within its validated operating regime.

## 2. Network form

Let `B` be the oriented incidence matrix of a graph and `g_e` the conductance of edge `e`.

Define the conductance Laplacian:

```text
L_G = B^T diag(g_e) B
```

For node potentials `v`, edge currents are:

```text
i = diag(g_e) B v
```

and Kirchhoff current balance becomes:

```text
B^T i = s
```

or equivalently:

```text
L_G v = s
```

for source/sink vector `s`.

This makes the Ohmic layer directly compatible with the existing REI graph-Laplacian and FEA views.

## 3. Dissipation invariant

For a passive resistor:

```text
P = V I = I^2 R = V^2 / R >= 0
```

Network dissipation is:

```text
P_total = sum_e g_e (Delta v_e)^2 >= 0
```

This becomes a physical admissibility gate for passive Ohmic components:

```text
PassiveOhmic
AND R > 0
AND P_total < 0
=> ModelInvalid
```

The system must not repair a negative-dissipation violation by silently changing units, signs or element semantics.

## 4. Integration with REI-FEA

An Ohmic element may carry the state:

```text
q_e = [V_e, I_e, R_e, G_e, P_e, T_e, u_e]
```

where `u_e` is local uncertainty and `T_e` is optional temperature when resistance is temperature dependent.

Element residuals can include:

```text
r_ohm = V_e - I_e R_e
r_power = P_e - V_e I_e
r_kcl = B^T i - s
```

The Ohmic residual contribution to an element error indicator can be written conceptually as:

```text
eta_e^2 = w1 |r_ohm|^2 + w2 |r_power|^2 + w3 |r_kcl|^2 + ...
```

Large residuals increase local uncertainty and can trigger adaptive refinement, model-class revision or abstention.

## 5. Typed validity boundary

Ohm's law is not assumed outside its regime.

Examples that require a different constitutive model include nonlinear semiconductor junctions, strongly temperature-dependent materials, superconducting regimes, electrochemical systems, hysteretic devices and explicitly non-Ohmic media.

Therefore:

```text
OhmicFitSuccess != UniversalOhmicTruth
```

and:

```text
ConstitutiveLaw = Ohmic
```

must always carry a domain-of-validity certificate.

## 6. REI coupling

The new layer plugs into REI as:

```text
Evidence
 -> Typed Physical Semantics
 -> Ohmic Constitutive Check
 -> Conductance Laplacian
 -> FEA / Network Solve
 -> Residual Estimation
 -> Uncertainty Update
 -> Falsification / Decision / Recovery
```

The Constitution, authorization, human veto, recovery and audit gates remain above this layer and are unchanged.

## 7. Safe research scope

Permitted uses include circuit modeling, sensor networks, thermal/electrical analog models, passive-network digital twins, calibration, anomaly detection and scientific simulation.

This module does not grant any new execution authority and does not alter the G2/G3 certification criteria.
