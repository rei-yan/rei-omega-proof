from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MODULE_PATH = ROOT / "scientific_hypothesis_adapter.py"
MANIFEST_PATH = ROOT / "scientific_hypothesis_adapter_manifest.example.json"

spec = importlib.util.spec_from_file_location("scientific_hypothesis_adapter", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)

with MANIFEST_PATH.open("r", encoding="utf-8") as handle:
    manifest = json.load(handle)

assert module.validate_manifest(manifest) == []

H = module.HypothesisRecord
S = module.Submission

valid_hypothesis = H(
    hypothesis_id="H1",
    claim="A bounded mechanism may explain the frozen evidence pattern.",
    mechanism="Mechanism M predicts a directional change under a discriminating measurement.",
    supporting_evidence_refs=("E1", "E2"),
    counterevidence_refs=("E3",),
    novel_predictions=("Prediction P must hold on a future frozen measurement.",),
    falsification_conditions=("Reject H1 if P fails under the frozen measurement protocol.",),
    required_discriminating_measurements=("Measure P with the externally frozen protocol.",),
    uncertainty=0.42,
    scope="synthetic-interface-sanity-only",
    known_failure_modes=("measurement confounding", "scope drift"),
)

valid_submission = S(
    task_id=manifest["task_id"],
    hypotheses=(valid_hypothesis,),
    adapter_hash=manifest["adapter_hash"],
    candidate_hash=manifest["candidate_hash"],
    provenance_hash="sha256:provenance-placeholder",
    tool_calls=3,
    human_interventions=0,
    retries=0,
)

assert module.evaluate_interface_readiness(manifest, valid_submission) == module.STATUS_READY
assert module.submission_digest(valid_submission).startswith("sha256:")

# Correct abstention is a valid bounded outcome, not a fake hypothesis promotion.
abstain_submission = S(
    task_id=manifest["task_id"],
    hypotheses=(),
    adapter_hash=manifest["adapter_hash"],
    candidate_hash=manifest["candidate_hash"],
    provenance_hash="sha256:provenance-placeholder",
    tool_calls=1,
    human_interventions=0,
    retries=0,
    abstain=True,
    abstain_reason="Frozen evidence is insufficient for a falsifiable bounded hypothesis.",
)
assert module.evaluate_interface_readiness(manifest, abstain_submission) == module.STATUS_ABSTAIN

# Adapter mutation after freeze is rejected.
tampered_adapter = S(
    task_id=manifest["task_id"],
    hypotheses=(valid_hypothesis,),
    adapter_hash="sha256:changed-after-freeze",
    candidate_hash=manifest["candidate_hash"],
    provenance_hash="sha256:provenance-placeholder",
    tool_calls=3,
    human_interventions=0,
    retries=0,
)
assert module.evaluate_interface_readiness(manifest, tampered_adapter) == module.STATUS_INVALID

# Undeclared evidence is rejected.
bad_evidence = H(
    hypothesis_id="H2",
    claim="Invalid evidence example",
    mechanism="M2",
    supporting_evidence_refs=("E999",),
    counterevidence_refs=(),
    novel_predictions=("P2",),
    falsification_conditions=("F2",),
    required_discriminating_measurements=("D2",),
    uncertainty=0.5,
    scope="synthetic-interface-sanity-only",
    known_failure_modes=(),
)
bad_evidence_submission = S(
    task_id=manifest["task_id"],
    hypotheses=(bad_evidence,),
    adapter_hash=manifest["adapter_hash"],
    candidate_hash=manifest["candidate_hash"],
    provenance_hash="sha256:provenance-placeholder",
    tool_calls=2,
    human_interventions=0,
    retries=0,
)
assert module.evaluate_interface_readiness(manifest, bad_evidence_submission) == module.STATUS_INVALID

# Uncounted human assistance is rejected.
human_assisted = S(
    task_id=manifest["task_id"],
    hypotheses=(valid_hypothesis,),
    adapter_hash=manifest["adapter_hash"],
    candidate_hash=manifest["candidate_hash"],
    provenance_hash="sha256:provenance-placeholder",
    tool_calls=2,
    human_interventions=1,
    retries=0,
)
assert module.evaluate_interface_readiness(manifest, human_assisted) == module.STATUS_INVALID

print("SCIENTIFIC_HYPOTHESIS_ADAPTER_SANITY_PASS")
print("status_ceiling=READY_FOR_EXTERNAL_ELIGIBILITY_REVIEW")
print("external_eligibility=NOT_SELF_CERTIFIED")
print("G6=OPEN")
print("world_best=UNVERIFIED")
print("real_world_actuation_authority=0")
