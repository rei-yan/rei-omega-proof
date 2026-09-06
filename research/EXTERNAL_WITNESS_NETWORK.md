# REI-Ω∞ · External Witness Network

Status: candidate research extension; non-canonical.

## Purpose

The External Witness Network extends the External Reality Trial Kit from one declared evaluator into a multi-witness evidence topology. Its job is not to manufacture consensus. Its job is to prevent correlated evaluators from being counted as independent merely because there are many names on a page.

Core rule:

```text
EvaluatorCount != IndependentEvaluatorCount
DeclaredDiversity != ProvenExternalIndependence
Agreement != IndependentAgreement
```

## Witness lineage

Each witness declaration carries auditable lineage fields:

```text
Witness = (
  witness_id,
  organization_lineage,
  code_lineage,
  data_lineage,
  control_lineage,
  funding_lineage,
  evaluator_method_lineage,
  attestation_hash,
  outcome,
  raw_record_hash
)
```

These fields are declarations and evidence hooks. They do not prove real institutional independence by themselves.

## Correlation pressure

For two witnesses `i,j`, the internal bookkeeping layer computes a declared overlap fraction across lineage dimensions.

```text
Overlap(i,j) = shared_declared_lineages / compared_lineages
```

A witness receives less effective declared weight when it shares more lineage with the rest of the network.

```text
DeclaredWeight(i) = 1 / (1 + Σ_j Overlap(i,j))
```

This is a bounded bookkeeping heuristic, not a theorem of statistical independence and not a G9 proof.

Required interpretation:

```text
HighDeclaredWeight != ProvenIndependent
LowDeclaredWeight => CorrelationConcern
```

## Network outcomes

The network may return only scoped evidence states:

```text
DECLARED_DIVERSE_SUPPORT
MIXED_EVIDENCE
INSUFFICIENT_DECLARED_DIVERSITY
ALL_ABSTAIN
INVALID_NETWORK_PROTOCOL
```

No internal state equals `G9_PASS`.

Hard vetoes:

```text
MissingRawRecord => INVALID_NETWORK_PROTOCOL
MissingAttestation => INVALID_NETWORK_PROTOCOL
DuplicateWitnessIdentity => INVALID_NETWORK_PROTOCOL
UnknownOutcome => INVALID_NETWORK_PROTOCOL
```

A high average score cannot erase a hard veto.

## Disagreement preservation

Disagreement is evidence, not noise to delete.

```text
WitnessA = PASS
WitnessB = FAIL
=> MIXED_EVIDENCE
```

The losing side is not removed merely to create consensus.

```text
NoDissentDeletion
NoCorrelationLaundering
NoEvaluatorCloning
NoOutcomeMajorityWashing
```

## G9 boundary

The executable sanity layer can test bookkeeping properties such as:

- duplicate identities are rejected;
- correlated witness declarations receive lower effective weight;
- three names can count as materially less than three effective declared witnesses;
- dissent is preserved as `MIXED_EVIDENCE`;
- insufficient declared diversity cannot be promoted to support;
- the network cannot self-certify G9.

It cannot prove:

- organizational independence;
- funding independence;
- hidden coordination absence;
- code/data provenance truthfulness;
- evaluator competence;
- real-world plurality.

Those require external evidence.

Internal ceiling:

```text
EXTERNAL_WITNESS_NETWORK_READY
G9 = OPEN
```

## Authority boundary

```text
WitnessNetworkAuthority = 0
ExperimentAuthority = 0
DeploymentAuthority = 0
RealWorldActuationAuthority = 0
```

The network evaluates claims and provenance. It does not authorize real-world action, exploitation, attack, or autonomous experimentation.

## Terminal principle

```text
ManyVoices != ManyIndependentVoices
IndependentEvidence > ApparentConsensus
PreservedDissent > ManufacturedAgreement
RealityVerdict > NetworkNarrative
```
