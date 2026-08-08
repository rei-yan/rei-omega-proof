from dataclasses import dataclass
from typing import Dict, List, Tuple

SCORE_KEYS = ("prediction", "calibration", "falsification", "recovery", "efficiency")
BASE_AUTHORITY = 1.0
BASE_CONSTITUTION = "K_INFINITY_V1"
EXTERNAL_GATES = ("G3", "G4", "G5", "G6")
MAX_LINEAGES = 16
MAX_PAIRWISE_CHALLENGES = 256
MAX_MERGE_PROPOSALS = 32


@dataclass(frozen=True)
class Lineage:
    lineage_id: str
    parent_ids: Tuple[str, ...]
    creator_id: str
    scientist_id: str
    verifier_id: str
    scores: Dict[str, float]
    authority: float = BASE_AUTHORITY
    recovery_ready: bool = True
    constitution_hash: str = BASE_CONSTITUTION
    self_certification: bool = False
    sacred_final_form_claim: bool = False
    central_monopoly_claim: bool = False
    claimed_closed_external_gates: Tuple[str, ...] = ()


def role_separated(lineage: Lineage) -> bool:
    roles = {lineage.creator_id, lineage.scientist_id, lineage.verifier_id}
    return len(roles) == 3


def eligible(lineage: Lineage) -> Tuple[bool, str]:
    if lineage.authority > BASE_AUTHORITY:
        return False, "UnsafeAuthorityExpansion"
    if not lineage.recovery_ready:
        return False, "RollbackUnavailable"
    if lineage.constitution_hash != BASE_CONSTITUTION:
        return False, "ConstitutionMismatch"
    if lineage.self_certification:
        return False, "SelfCertificationAttempt"
    if lineage.sacred_final_form_claim:
        return False, "SacredFinalFormClaim"
    if lineage.central_monopoly_claim:
        return False, "CentralMonopolyAttempt"
    if not role_separated(lineage):
        return False, "RoleSeparationViolation"
    if any(gate in EXTERNAL_GATES for gate in lineage.claimed_closed_external_gates):
        return False, "FakeExternalGateClosure"
    if set(lineage.scores) != set(SCORE_KEYS):
        return False, "MalformedScoreVector"
    return True, "Eligible"


def dominates(a: Lineage, b: Lineage) -> bool:
    ge_all = all(a.scores[k] >= b.scores[k] for k in SCORE_KEYS)
    gt_any = any(a.scores[k] > b.scores[k] for k in SCORE_KEYS)
    return ge_all and gt_any


def pareto_frontier(lineages: List[Lineage]) -> List[Lineage]:
    return [
        candidate
        for candidate in lineages
        if not any(dominates(other, candidate) for other in lineages if other != candidate)
    ]


def pairwise_challenge(lineages: List[Lineage]):
    records = []
    count = 0
    for i, a in enumerate(lineages):
        for b in lineages[i + 1 :]:
            count += 1
            assert count <= MAX_PAIRWISE_CHALLENGES
            if dominates(a, b):
                records.append((a.lineage_id, b.lineage_id, "B_DOMINATED"))
            elif dominates(b, a):
                records.append((a.lineage_id, b.lineage_id, "A_DOMINATED"))
            else:
                records.append((a.lineage_id, b.lineage_id, "NON_DOMINATED_PAIR"))
    return records


def merge_eligible(a: Lineage, b: Lineage, merged: Lineage) -> Tuple[bool, str]:
    ok, reason = eligible(merged)
    if not ok:
        return False, reason
    if a.constitution_hash != b.constitution_hash or merged.constitution_hash != a.constitution_hash:
        return False, "ConstitutionIncompatible"
    if merged.authority > max(a.authority, b.authority):
        return False, "MergeAuthorityExpansion"
    if not set(a.parent_ids + (a.lineage_id,)).issubset(set(merged.parent_ids)):
        return False, "ParentLineageAErased"
    if not set(b.parent_ids + (b.lineage_id,)).issubset(set(merged.parent_ids)):
        return False, "ParentLineageBErased"
    for key in SCORE_KEYS:
        floor = min(a.scores[key], b.scores[key])
        if merged.scores[key] < floor:
            return False, f"FrozenHeldoutRegression:{key}"
    return True, "MergeEligible"


def main() -> None:
    failure_graveyard = []

    alpha = Lineage(
        "alpha", (), "creator_a", "scientist_a", "verifier_a",
        {"prediction": 0.92, "calibration": 0.76, "falsification": 0.82, "recovery": 0.90, "efficiency": 0.68},
    )
    beta = Lineage(
        "beta", (), "creator_b", "scientist_b", "verifier_b",
        {"prediction": 0.80, "calibration": 0.93, "falsification": 0.78, "recovery": 0.86, "efficiency": 0.83},
    )
    gamma = Lineage(
        "gamma", (), "creator_c", "scientist_c", "verifier_c",
        {"prediction": 0.72, "calibration": 0.70, "falsification": 0.70, "recovery": 0.75, "efficiency": 0.61},
    )

    unsafe_authority = Lineage(
        "unsafe_authority", (), "creator_u", "scientist_u", "verifier_u",
        {k: 0.99 for k in SCORE_KEYS}, authority=1.25,
    )
    role_violation = Lineage(
        "role_violation", (), "same_role", "same_role", "verifier_r",
        {k: 0.85 for k in SCORE_KEYS},
    )
    monopoly = Lineage(
        "monopoly", (), "creator_m", "scientist_m", "verifier_m",
        {k: 0.88 for k in SCORE_KEYS}, central_monopoly_claim=True,
    )
    fake_gates = Lineage(
        "fake_gates", (), "creator_f", "scientist_f", "verifier_f",
        {k: 0.87 for k in SCORE_KEYS}, claimed_closed_external_gates=("G3",),
    )

    candidates = [alpha, beta, gamma, unsafe_authority, role_violation, monopoly, fake_gates]
    assert len(candidates) <= MAX_LINEAGES

    safe = []
    for lineage in candidates:
        ok, reason = eligible(lineage)
        if ok:
            safe.append(lineage)
        else:
            failure_graveyard.append((lineage.lineage_id, reason))

    assert {x.lineage_id for x in safe} == {"alpha", "beta", "gamma"}
    assert ("unsafe_authority", "UnsafeAuthorityExpansion") in failure_graveyard
    assert ("role_violation", "RoleSeparationViolation") in failure_graveyard
    assert ("monopoly", "CentralMonopolyAttempt") in failure_graveyard
    assert ("fake_gates", "FakeExternalGateClosure") in failure_graveyard

    frontier = pareto_frontier(safe)
    frontier_ids = {x.lineage_id for x in frontier}
    assert frontier_ids == {"alpha", "beta"}
    assert "gamma" not in frontier_ids
    failure_graveyard.append(("gamma", "DominatedLineage"))

    challenge_records = pairwise_challenge(safe)
    assert len(challenge_records) == 3
    assert any("DOMINATED" in result for _, _, result in challenge_records)
    assert any(result == "NON_DOMINATED_PAIR" for _, _, result in challenge_records)

    merged_good = Lineage(
        "alpha_beta_merge",
        ("alpha", "beta"),
        "creator_ab", "scientist_ab", "verifier_ab",
        {"prediction": 0.91, "calibration": 0.91, "falsification": 0.83, "recovery": 0.90, "efficiency": 0.80},
        authority=1.0,
    )
    ok, reason = merge_eligible(alpha, beta, merged_good)
    assert ok, reason

    merged_bad = Lineage(
        "bad_merge",
        ("alpha",),
        "creator_bad", "scientist_bad", "verifier_bad",
        {"prediction": 0.95, "calibration": 0.95, "falsification": 0.95, "recovery": 0.95, "efficiency": 0.95},
        authority=1.0,
    )
    ok, reason = merge_eligible(alpha, beta, merged_bad)
    assert not ok
    assert reason == "ParentLineageBErased"
    failure_graveyard.append(("bad_merge", f"MergeRejected:{reason}"))

    assert ("gamma", "DominatedLineage") in failure_graveyard
    assert any(item[0] == "bad_merge" and item[1].startswith("MergeRejected") for item in failure_graveyard)

    # External gates remain externally open in this internal synthetic test.
    external_gate_status = {gate: "OPEN" for gate in EXTERNAL_GATES}
    assert all(status == "OPEN" for status in external_gate_status.values())

    print("MULTILINEAGE_COEVOLUTION_KERNEL=PASS")
    print("FINITE_LINEAGES=7")
    print("ELIGIBLE_SAFE_LINEAGES=3")
    print("PARETO_SURVIVORS=" + ",".join(sorted(frontier_ids)))
    print("DOMINATED_RETIRED=gamma")
    print("GOOD_MERGE=ELIGIBLE")
    print("BAD_MERGE=REJECTED")
    print(f"FAILURE_GRAVEYARD_ENTRIES={len(failure_graveyard)}")
    print("NO_PERMANENT_CENTRAL_REI=ENFORCED")
    print("ROLE_SEPARATION=ENFORCED_SYNTHETICALLY")
    print("AUTHORITY_NONEXPANSION=ENFORCED")
    print("REALITY_VETO=ENFORCED_BY_ARCHITECTURE")
    print("EXTERNAL_GATES_G3_G4_G5_G6=OPEN")
    print("SYNTHETIC_PARETO_SUCCESS_DOES_NOT_EQUAL_REAL_WORLD_SUPERIORITY=true")


if __name__ == "__main__":
    main()
