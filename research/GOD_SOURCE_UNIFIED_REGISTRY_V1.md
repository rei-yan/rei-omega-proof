# REI-Ω 神源完整化 · Phase 1

Status: `UNIFIED_SOURCE_REGISTRY_CANDIDATE`

Scope: PR #28 / `rei-v193-reconcile` only. Canonical `main` remains untouched.

## Goal

Phase 1 turns God Source from a local-model-only concept into a machine-readable source-governance layer.

This phase does **not** claim that GPT or Claude are already runtime-bound. It creates the registry, identity, provenance, authority ceiling and disagreement rules required before external model bindings may be admitted.

## Initial source set

1. `local:rei-local-node-vnext`
   - Existing local candidate source.
   - Identity must remain tied to runtime provenance and source SHA.

2. `openai:gpt`
   - Registered as an external source family.
   - Binding state remains `EXTERNAL_UNBOUND` until exact model/version and request provenance are available.

3. `anthropic:claude`
   - Registered as an external source family.
   - Binding state remains `EXTERNAL_UNBOUND` until exact model/version and request provenance are available.

The registry is extensible to tools, datasets, humans and external systems without granting any source governance authority.

## Constitutional invariants

```text
SourcePower != SourceAuthority
ProviderDiversity != Independence
Agreement != Truth
DisagreementMustBePreserved
SilentModelSubstitutionForbidden
UnknownSourceFailsClosed
RealityVeto > REI
```

A source may propose, rank, challenge or request more evidence. A source may not set `RealityValidated`, promote canonical state, grant ascension, override God Core, or override reality veto.

## Required source identity

Every registered source must carry:

- `source_id`
- `source_kind`
- `provider`
- `model_family`
- `model_version`
- `binding_state`
- provenance
- reliability history
- known failure modes
- correlation group
- cost profile
- latency profile
- authority level
- replaceability

This blocks silent model substitution and creates the minimum substrate for source-specific Failure Memory.

## Disagreement preservation

The registry forbids forced consensus.

Material disagreement is preserved as evidence and may be escalated to:

`God Wheel -> Shadow -> Observer -> God Proof`

Provider labels do not establish independence. Correlation must be measured rather than assumed.

## Phase 1 boundary

Implemented in this phase:

- unified machine-readable registry schema
- Local/GPT/Claude source identities
- provenance requirements
- source authority ceiling
- disagreement preservation contract
- correlation-awareness contract
- cost/latency accounting requirement
- fail-closed unknown-source policy
- source receipt schema
- CI sanity gate

Still pending:

- real GPT runtime binding
- real Claude runtime binding
- synchronized disagreement-arbitration runtime
- source-specific Failure Memory runtime
- dynamic reliability scoring
- budget-aware model routing
- downstream God Wheel/Shadow/Observer/God Proof execution receipts

Therefore:

```text
RegistryDefined = TRUE
ReceiptSchemaDefined = TRUE
ExternalBindings = PENDING
RuntimeArbitration = PENDING
RealityValidated = FALSE
Ascension = NO
```

## Promotion rule

The existing Nine-System interface map must not be upgraded merely because these files exist.

God Source maturity may advance from `PARTIAL_LOCAL_SOURCE_ONLY` only after the new registry sanity gate passes on the exact candidate SHA and the resulting candidate remains bounded by the nine-system God Proof constraints.
