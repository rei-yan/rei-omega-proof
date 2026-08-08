# REI-Ω Reality Guardian Kernel · 现实守护核

Status: research module

This module gives REI a bounded real-world agency model for **defense, containment, recovery, and reversible authorized intervention** while keeping adversarial attack capability restricted to REI-owned models, digital twins, sandboxes, and explicitly authorized test environments.

It does not authorize weapons, coercion, sabotage, harmful physical actuation, or offensive action against real-world targets.

## 1. Core separation

```text
RealWorldMode = Observe | Warn | RateLimit | Isolate | Rollback | Failover | Shutdown | Restore
AttackMode    = OwnModel | Sandbox | DigitalTwin | AuthorizedTestEnvironment
```

The system must reject any attempt to map Red Crucible attack plans directly into unrestricted real-world execution.

```text
RedCrucibleOutput -> RealWorldAttack = Forbidden
```

## 2. Reality authority gate

A real-world defensive action is eligible only if all hard gates hold:

```text
Authorized
AND PurposeBound
AND ScopeBound
AND ReversibleOrEmergencySafe
AND Auditable
AND HumanOverrideAvailable
AND RecoveryReady
AND HarmBudgetSatisfied
```

Otherwise:

```text
RealWorldActionRejected
```

## 3. Defensive action ladder

The kernel uses the least-force principle:

```text
Observe
-> Warn
-> DegradePrivilege
-> RateLimit
-> Isolate
-> Failover
-> Rollback
-> SafeShutdown
```

The system must choose the minimum sufficient reversible action before any stronger containment action.

## 4. Adversarial asymmetry

The stronger the internal adversarial search becomes, the less real-world freedom it receives:

```text
AdversarialPower increases
=> RealWorldFreedom does not increase
```

and for high-risk conditions:

```text
Uncertainty increases
=> Authority decreases
```

## 5. World Genesis boundary

World Genesis is allowed to create and evolve mathematical/digital worlds, law sets, agents, and challenge environments inside bounded compute and sandbox constraints.

```text
WorldGenesis != PhysicalUniverseCreationClaim
```

The research target is generative world-model construction, not a claim that software can create a literal physical universe.

## 6. Guardian objective

Define the guardian score only for defensive robustness:

```text
GuardianStrength =
Detection
+ Containment
+ Recovery
+ Auditability
+ Calibration
+ SafeAbstention
```

No offensive damage term is permitted in the objective.

## 7. Attack/defense coupling

Red Crucible may generate counterexamples, stress sequences, failure cascades, adversarial observations, and model-breaking cases in bounded environments.

Those findings may only produce real-world outputs of the form:

```text
Patch
Harden
RateLimit
Isolate
Rollback
Failover
Shutdown
Alert
```

They may not produce unrestricted attack execution.

## 8. Deterministic safety properties

The sanity suite must demonstrate:

1. unauthorized real-world action is rejected;
2. authorized reversible defensive action may pass;
3. real-world attack requests are rejected;
4. Red Crucible remains available in sandbox scope;
5. higher adversarial power never increases real-world authority;
6. higher uncertainty never increases authority;
7. least-force defensive ordering is respected;
8. rollback and human override remain mandatory for high-impact action;
9. failure records remain visible;
10. World Genesis remains a digital/mathematical research process.

## 9. Claim boundary

A passing run proves only that the bounded guardian policy behaves as specified in a deterministic research test.

It does not prove invincibility, AGI, production safety, autonomous defense in arbitrary environments, or the ability to create a physical universe.
