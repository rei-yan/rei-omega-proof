# REI-Ω G5 · Original Discovery Gate · 原创发现门

Status: OPEN protocol

G5 tests whether REI can produce a genuinely useful new scientific representation, primitive, measurement, relationship, or theory candidate **before** the hidden evaluation evidence is revealed, and whether that candidate survives externally hidden validation under frozen criteria.

G5 is not a same-session benchmark and cannot self-certify novelty.

## 1. Discovery object

A candidate discovery is registered as:

```text
Discovery = (
  protocol_version,
  domain,
  data_cutoff,
  training_evidence_hash,
  generator_hash,
  baseline_hash,
  candidate_type,
  candidate_definition,
  operationalization,
  predicted_gain,
  falsification_plan,
  scoring_rule,
  novelty_scope,
  created_at
)
```

The canonical serialization is committed by SHA-256 before hidden evaluation.

## 2. Candidate classes

G5 may evaluate bounded claims of:

```text
NewRepresentation
NewPrimitive
NewMeasurement
NewRelationship
NewModelClass
NewCausalHypothesis
NewTheoryCandidate
```

A candidate must be operational enough to be scored. Beautiful language alone is not a discovery.

## 3. Three-way separation

```text
Generator != HiddenEvaluator != NoveltyReviewer
```

The generator must not see sealed evaluation evidence.
The hidden evaluator must not change scoring after seeing the candidate.
The novelty reviewer must not be replaced by the candidate generator.

## 4. Frozen evaluation

At registration time freeze:

```text
target
candidate
baselines
scoring_rule
minimum_improvement_margin
falsification_plan
data_cutoff
```

After hidden evidence is revealed, these fields may not be retuned before scoring.

```text
OutcomeSeen -> RetuningBeforeScore = Forbidden
```

## 5. Discovery validity

A candidate can become G5-eligible only if all hard gates hold:

```text
CommitmentValid
AND HiddenEvidenceWasUnavailable
AND NoEvaluationLeakage
AND FrozenScoring
AND BaselineComparisonCompleted
AND ImprovementMarginMet
AND FalsificationExecuted
AND ExternalProvenancePresent
AND IndependentNoveltyReviewCompleted
```

Failure of any hard gate means the candidate does not close G5.

## 6. Novelty boundary

G5 distinguishes usefulness from priority claims.

```text
UsefulNewToREI != NewToScience
```

A claim such as "world first", "first discovery", or "scientifically novel" requires an independent prior-art review. Absence of a matching search result is not proof of novelty.

Novelty status is one of:

```text
Unreviewed
NewToSystemOnly
KnownInLiterature
PossiblyNovel
IndependentlySupportedNovel
```

Only `IndependentlySupportedNovel` may satisfy the novelty component of a full G5 certification.

## 7. Prospective hidden-discovery protocol

```text
t0: Freeze generator + evidence cutoff + baselines + score + falsification plan
t1: Generate candidate without sealed evaluation evidence
t2: Freeze candidate commitment
t3: Reveal external/withheld evidence
t4: Score candidate and baselines without retuning
t5: Execute falsification plan
t6: Independent novelty/prior-art review
t7: Preserve pass or failure permanently
```

## 8. Failure Graveyard

Negative results are permanent research assets.

```text
FailedDiscovery -> FailureGraveyard
```

The record should retain candidate commitment, score, baseline score, failure reason, leakage status, and reviewer status. Failed discoveries must not be silently removed from aggregate reporting.

## 9. Synthetic dry-run boundary

A deterministic internal hidden-world test may verify protocol integrity only.

```text
SyntheticHiddenWorld = DRY_RUN_ONLY
SyntheticHiddenWorld != G5Pass
```

The same repository, author, or session cannot convert a synthetic dry run into independent external discovery evidence.

## 10. Relationship to other gates

```text
G2 != G5
G3 != G5
G4 != G5
```

- G2 tests a scoped machine-checked invariant kernel.
- G3 tests independent replication.
- G4 tests prospective honesty against future reality.
- G5 tests original discovery under hidden evidence and novelty review.

No one gate substitutes for another.

## 11. Current state

At creation of this module:

```text
G5_STATUS = OPEN
EXTERNALLY_HIDDEN_DISCOVERIES = 0
INDEPENDENTLY_SUPPORTED_NOVEL_DISCOVERIES = 0
```

This is intentional.

## 12. Claim boundary

A green G5 integrity CI proves only that the preregistration and anti-self-certification logic behaves as specified. It does not prove scientific originality, AGI, superintelligence, autonomous science, world-best performance, or universal discovery ability.
