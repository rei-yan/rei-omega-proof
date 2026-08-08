# REI-Ω Genesis Kernel

Status: research module

The Genesis Kernel extends the Frontier Re-entry Kernel with bounded candidate generation. Its purpose is not to grant execution authority. Its purpose is to create testable alternatives to the current REI architecture, challenge them, and retain only candidates that survive independent evidence and hard governance gates.

## 1. Core loop

```text
ObserveFailureOrOpportunity
-> GenerateCandidates
-> GenerateCounterexamples
-> GenerateMeasurements
-> RedCrucible
-> Verify
-> Compare
-> AdoptStudyOrReject
-> Record
```

The kernel treats generation and validation as different roles:

```text
Generator != Falsifier != Verifier != Approver != Executor
```

No candidate may approve or execute itself.

## 2. Candidate world and architecture objects

A generated candidate is represented as:

```text
C = {
  representation,
  model_class,
  causal_assumptions,
  measurement_policy,
  recovery_policy,
  uncertainty_model,
  resource_budget,
  constitution_hash
}
```

A candidate is not accepted because it is novel. Novelty is evidence-neutral.

```text
Novel(C) != Valid(C)
```

## 3. Bounded architecture mutation

The Genesis Kernel may propose bounded changes such as:

```text
ReplaceModelClass
SplitWorldModel
MergeCompatibleModels
AddMeasurement
RemoveRedundantMeasurement
ChangeRepresentation
AdjustUncertaintyModel
AddRecoveryPath
RetireModule
IntroduceSuccessorModule
```

All changes are proposals only. A generated candidate has zero new real-world authority by default.

```text
Authority(C_new) <= Authority(incumbent)
```

until the normal authorization process explicitly grants otherwise.

## 4. Counterexample-first generation

For every candidate C, the kernel must generate a falsification target before any adoption attempt.

Conceptually:

```text
z*(C) = argmin_z Cost(z)
subject to Validity(C | z) < threshold
```

The practical implementation may approximate this objective, but the ordering rule remains:

```text
FalsificationPlanBeforeAdoption
```

A candidate without a falsification plan is incomplete.

## 5. Measurement Genesis

When competing candidates cannot be distinguished by current evidence, the kernel should seek the most discriminating safe measurement.

```text
Measurement* = argmax_m
  (InformationGain + DiscriminationGain)
  / (Cost + Risk + Irreversibility)
```

If no admissible measurement can distinguish the candidates, the status must remain unresolved.

```text
Unidentifiable -> AbstainFromSelection
```

## 6. Candidate ecology

The kernel maintains a population of hypotheses/architectures rather than one sacred model.

Permitted lifecycle states:

```text
Proposed
Challenged
Supported
Dominated
Quarantined
Retired
Adopted
```

A candidate may be killed by evidence without affecting the survival of the Genesis process itself.

## 7. Genesis eligibility gate

A generated candidate may enter staged adoption only when all hard conditions are true:

```text
ConstitutionPreserved
AND IndependentEvidence
AND ProspectiveValidation
AND FalsificationPlanExecuted
AND CalibrationNonRegression
AND RecoveryNonRegression
AND AuditContinuity
AND AuthorityNonExpansion
AND ImprovementMarginSatisfied
```

Otherwise the only valid outcomes are `Study`, `Reject`, `Quarantine`, or `Defer`.

## 8. Self-generated challenger rule

The Genesis Kernel is explicitly allowed to generate a challenger designed to outperform the incumbent on its known weaknesses.

```text
IncumbentFailure
-> ChallengerGeneration
-> CountertestGeneration
-> SymmetricRetest
```

The retest must be symmetric. The system may not create tests that only expose competitors while protecting the incumbent.

```text
AdversarialCoverage(incumbent) >= minimum
AND
AdversarialCoverage(challenger) >= minimum
```

## 9. Red Crucible coupling

Strong attack-mode behavior remains restricted to:

```text
OwnModel
OR Sandbox
OR DigitalTwin
OR AuthorizedTestEnvironment
```

Activation requires:

```text
Authorized
AND Sandboxed
AND Auditable
AND RollbackReady
AND ScopeBound
```

and must satisfy:

```text
AdversarialPower increases
=> RealWorldFreedom does not increase
```

No real-world attack authority is introduced by this module.

## 10. Anti-Goodhart and anti-self-deception

The candidate generator does not control its own final score. Evaluation metrics are frozen or independently governed before candidate scoring.

```text
GeneratorCannotRewriteMetric
```

A candidate that improves the headline metric while degrading calibration, recovery, uncertainty honesty, or silent-failure risk cannot pass the hard gate.

## 11. Genesis evidence bundle

A high-impact candidate should eventually carry:

```text
Pi_genesis = {
  lineage,
  mutation_description,
  constitution_preservation,
  falsification_plan,
  countertest_results,
  calibration_report,
  prospective_validation,
  independent_evidence,
  rollback_reachability,
  audit_continuity,
  authority_non_expansion,
  failure_graveyard_links
}
```

Missing hard evidence means no staged adoption.

## 12. Research claim boundary

The Genesis Kernel does not prove autonomous scientific discovery, AGI, universal superiority, or open-world reliability. It formalizes a bounded research mechanism for generating and eliminating candidate architectures under evidence, falsification, recovery, and governance constraints.

The intended long-run property is:

```text
REI can generate falsifiable alternatives to itself
without granting those alternatives unearned authority.
```

That is a research target, not a universal theorem.
