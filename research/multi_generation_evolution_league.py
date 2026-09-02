#!/usr/bin/env python3
"""Synthetic identityless multi-generation evolution league for REI.

The league tests whether repeated winners accumulate hidden dynastic privilege.
It is a bounded research protocol, not external validation or autonomous actuation.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Sequence


FORBIDDEN_END_STATES = {
    "G3_PASS", "G4_PASS", "G5_PASS", "G6_PASS", "G7_PASS", "G8_PASS",
    "G9_PASS", "G10_PASS", "WORLD_BEST", "WORLD_UNIQUE", "CANONICAL", "FINAL_TRUTH",
}


@dataclass(frozen=True)
class GenerationContract:
    generation_id: str
    hidden_window_hash: str
    metric_id: str
    metric_direction: str
    compute_budget: int
    wallclock_budget: int
    retry_limit: int
    tool_policy_hash: str
    human_assistance_policy_hash: str
    abstention_policy_hash: str
    tie_tolerance: float
    evaluator_set_hash: str
    submission_deadline: str


@dataclass(frozen=True)
class Entrant:
    candidate_id: str
    lineage_id: str
    parent_candidate_id: str
    generation_id: str
    evidence_hash: str
    failure_memory_digest: str
    score: float
    eligible: bool
    authority: int = 0
    certification: str = "UNVERIFIED"
    canonical: bool = False
    historical_bonus: float = 0.0
    budget_bonus: int = 0
    retry_bonus: int = 0
    metric_bonus: float = 0.0
    seed_priority: int = 0
    forced_advancement: bool = False
    historical_evidence_credit: float = 0.0


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def all_unique(values: Iterable[str]) -> bool:
    seq = tuple(values)
    return len(seq) == len(set(seq))


def dynastic_privilege(entrant: Entrant) -> float:
    return float(
        abs(entrant.historical_bonus)
        + abs(entrant.budget_bonus)
        + abs(entrant.retry_bonus)
        + abs(entrant.metric_bonus)
        + abs(entrant.seed_priority)
        + abs(entrant.historical_evidence_credit)
        + (1.0 if entrant.forced_advancement else 0.0)
    )


def validate_generation(contract: GenerationContract, entrants: Sequence[Entrant]) -> Dict[str, Any]:
    violations: List[str] = []
    if contract.metric_direction not in {"minimize", "maximize"}:
        violations.append("INVALID_METRIC_DIRECTION")
    if contract.compute_budget <= 0 or contract.wallclock_budget <= 0 or contract.retry_limit < 0:
        violations.append("INVALID_RESOURCE_CONTRACT")
    if contract.tie_tolerance < 0:
        violations.append("INVALID_TIE_TOLERANCE")
    if not entrants:
        violations.append("EMPTY_GENERATION")

    ids = [e.candidate_id for e in entrants]
    evidence = [e.evidence_hash for e in entrants]
    if not all_unique(ids):
        violations.append("DUPLICATE_CANDIDATE_ID")
    if not all_unique(evidence):
        violations.append("DUPLICATE_POSITIVE_EVIDENCE_WITHIN_GENERATION")

    for e in entrants:
        if e.generation_id != contract.generation_id:
            violations.append(f"GENERATION_MISMATCH:{e.candidate_id}")
        if e.authority != 0:
            violations.append(f"AUTHORITY_CARRYOVER:{e.candidate_id}")
        if e.certification != "UNVERIFIED":
            violations.append(f"CERTIFICATION_CARRYOVER:{e.candidate_id}")
        if e.canonical:
            violations.append(f"CANONICAL_CARRYOVER:{e.candidate_id}")
        if dynastic_privilege(e) > 0:
            violations.append(f"DYNASTIC_PRIVILEGE:{e.candidate_id}")

    return {
        "status": "GENERATION_PROTOCOL_VALID" if not violations else "INVALID_GENERATION_PROTOCOL",
        "violations": violations,
    }


def rank_generation(contract: GenerationContract, entrants: Sequence[Entrant]) -> Dict[str, Any]:
    validation = validate_generation(contract, entrants)
    if validation["status"] != "GENERATION_PROTOCOL_VALID":
        return {"status": "INVALID_GENERATION_PROTOCOL", "winner": None, "violations": validation["violations"]}

    eligible = [e for e in entrants if e.eligible]
    if not eligible:
        return {"status": "NO_ELIGIBLE_SUCCESSOR", "winner": None, "violations": []}

    reverse = contract.metric_direction == "maximize"
    ranked = sorted(eligible, key=lambda e: e.score, reverse=reverse)
    best = ranked[0]
    if len(ranked) > 1:
        delta = abs(ranked[0].score - ranked[1].score)
        if delta <= contract.tie_tolerance:
            return {
                "status": "TIE_OR_INCONCLUSIVE",
                "winner": None,
                "tied": [ranked[0].candidate_id, ranked[1].candidate_id],
                "violations": [],
            }

    return {
        "status": "SCOPED_GENERATION_ADVANTAGE",
        "winner": best.candidate_id,
        "winner_lineage": best.lineage_id,
        "winner_score": best.score,
        "winner_authority": best.authority,
        "violations": [],
    }


def validate_league(generations: Sequence[tuple[GenerationContract, Sequence[Entrant]]]) -> Dict[str, Any]:
    violations: List[str] = []
    hidden_windows: List[str] = []
    positive_evidence: List[str] = []
    for contract, entrants in generations:
        gen = validate_generation(contract, entrants)
        if gen["status"] != "GENERATION_PROTOCOL_VALID":
            violations.extend(gen["violations"])
        hidden_windows.append(contract.hidden_window_hash)
        positive_evidence.extend(e.evidence_hash for e in entrants)

    if not all_unique(hidden_windows):
        violations.append("HIDDEN_WINDOW_REUSE_ACROSS_GENERATIONS")
    if not all_unique(positive_evidence):
        violations.append("POSITIVE_EVIDENCE_REUSE_ACROSS_GENERATIONS")

    return {
        "status": "LEAGUE_PROTOCOL_VALID" if not violations else "INVALID_LEAGUE_PROTOCOL",
        "violations": violations,
    }


def build_fixture() -> List[tuple[GenerationContract, List[Entrant]]]:
    failure_memory = digest({"failure": "incumbent-cascade", "preserved": True})

    def contract(g: int) -> GenerationContract:
        return GenerationContract(
            generation_id=f"G{g}",
            hidden_window_hash=digest({"hidden_window": f"fresh-{g}"}),
            metric_id="frozen_error",
            metric_direction="minimize",
            compute_budget=100,
            wallclock_budget=60,
            retry_limit=1,
            tool_policy_hash=digest({"tools": ["frozen-toolset"]}),
            human_assistance_policy_hash=digest({"human": "none"}),
            abstention_policy_hash=digest({"abstain": "allowed"}),
            tie_tolerance=1e-9,
            evaluator_set_hash=digest({"evaluators": [f"E{g}A", f"E{g}B"]}),
            submission_deadline=f"G{g}-deadline",
        )

    g0 = [
        Entrant("G0-A", "LINEAGE-A", "NONE", "G0", digest({"g":0,"e":"A"}), failure_memory, 0.18, True),
        Entrant("G0-B", "LINEAGE-B", "NONE", "G0", digest({"g":0,"e":"B"}), failure_memory, 0.12, True),
        Entrant("G0-C", "LINEAGE-C", "NONE", "G0", digest({"g":0,"e":"C"}), failure_memory, 0.21, True),
    ]
    g1 = [
        Entrant("G1-A", "LINEAGE-A", "G0-A", "G1", digest({"g":1,"e":"A"}), failure_memory, 0.17, True),
        Entrant("G1-B", "LINEAGE-B", "G0-B", "G1", digest({"g":1,"e":"B"}), failure_memory, 0.11, True),
        Entrant("G1-D", "LINEAGE-D", "NONE", "G1", digest({"g":1,"e":"D"}), failure_memory, 0.16, True),
    ]
    # LINEAGE-B has won twice before G2, but receives no bonus and can lose cleanly.
    g2 = [
        Entrant("G2-B", "LINEAGE-B", "G1-B", "G2", digest({"g":2,"e":"B"}), failure_memory, 0.13, True),
        Entrant("G2-D", "LINEAGE-D", "G1-D", "G2", digest({"g":2,"e":"D"}), failure_memory, 0.10, True),
        Entrant("G2-E", "LINEAGE-E", "NONE", "G2", digest({"g":2,"e":"E"}), failure_memory, 0.19, True),
    ]
    return [(contract(0), g0), (contract(1), g1), (contract(2), g2)]


def run_league() -> Dict[str, Any]:
    generations = build_fixture()
    league_validation = validate_league(generations)
    if league_validation["status"] != "LEAGUE_PROTOCOL_VALID":
        return {"status": "INVALID_LEAGUE_PROTOCOL", "violations": league_validation["violations"]}

    records = []
    lineage_winners = []
    for contract, entrants in generations:
        outcome = rank_generation(contract, entrants)
        records.append({"generation": contract.generation_id, **outcome})
        if outcome.get("winner_lineage"):
            lineage_winners.append(outcome["winner_lineage"])

    result = {
        "status": "IDENTITYLESS_MULTI_GENERATION_LEAGUE_READY",
        "records": records,
        "winner_lineages": lineage_winners,
        "dynastic_privilege": 0,
        "historical_champion_seed": False,
        "external_gates_closed": [],
        "canonical_promotion": False,
        "real_world_attack_authority": 0,
        "real_world_actuation_authority": 0,
    }
    assert result["status"] not in FORBIDDEN_END_STATES
    return result


def _sanity() -> None:
    generations = build_fixture()
    assert validate_league(generations)["status"] == "LEAGUE_PROTOCOL_VALID"

    r0 = rank_generation(*generations[0])
    r1 = rank_generation(*generations[1])
    r2 = rank_generation(*generations[2])
    assert r0["winner_lineage"] == "LINEAGE-B"
    assert r1["winner_lineage"] == "LINEAGE-B"
    assert r2["winner_lineage"] == "LINEAGE-D"

    # Forged incumbency moat: a repeated champion tries to claim a historical bonus.
    contract2, entrants2 = generations[2]
    forged = list(entrants2)
    forged[0] = Entrant(
        **{**forged[0].__dict__, "historical_bonus": 0.05, "seed_priority": 1}
    )
    bad = rank_generation(contract2, forged)
    assert bad["status"] == "INVALID_GENERATION_PROTOCOL"
    assert any("DYNASTIC_PRIVILEGE" in v for v in bad["violations"])

    # Reusing an old hidden window invalidates the league.
    c0, e0 = generations[0]
    c1, e1 = generations[1]
    reused = GenerationContract(**{**c1.__dict__, "hidden_window_hash": c0.hidden_window_hash})
    assert validate_league([(c0, e0), (reused, e1)])["status"] == "INVALID_LEAGUE_PROTOCOL"

    # A generation with no eligible successor is an admissible outcome, not a forced heir.
    none_eligible = [Entrant(**{**e.__dict__, "eligible": False}) for e in e0]
    assert rank_generation(c0, none_eligible)["status"] == "NO_ELIGIBLE_SUCCESSOR"

    result = run_league()
    assert result["status"] == "IDENTITYLESS_MULTI_GENERATION_LEAGUE_READY"
    assert result["winner_lineages"] == ["LINEAGE-B", "LINEAGE-B", "LINEAGE-D"]
    assert result["dynastic_privilege"] == 0
    assert result["historical_champion_seed"] is False
    assert result["external_gates_closed"] == []
    assert result["canonical_promotion"] is False
    assert result["real_world_attack_authority"] == 0
    assert result["real_world_actuation_authority"] == 0

    print("IDENTITYLESS_MULTI_GENERATION_LEAGUE_READY")
    print("REPEATED_CHAMPION_NOT_PERMANENT_SEED")
    print("DYNASTIC_PRIVILEGE_DETECTED_AND_REJECTED")
    print("BETTER_EVIDENCE_CAN_BREAK_LINEAGE")
    print("NO_ELIGIBLE_SUCCESSOR_IS_ADMISSIBLE")
    print("EXTERNAL_GATES_REMAIN_OPEN")


if __name__ == "__main__":
    _sanity()
