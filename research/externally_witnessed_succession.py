#!/usr/bin/env python3
"""Finite sanity model for externally witnessed succession.

This module can assess internal eligibility bookkeeping only. It cannot pass G10,
promote a canonical successor, or certify external witness independence.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from typing import Dict, List

READY = "EXTERNALLY_WITNESSED_SUCCESSION_PROTOCOL_READY"
READY_TRIAL = "READY_FOR_EXTERNAL_G10_TRIAL"
RETAINS = "INCUMBENT_RETAINS_SCOPED_STATUS"
REJECTED = "SUCCESSOR_REJECTED"
ABSTAIN = "ABSTAIN"
INVALID = "INVALID_DECISION"


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    constitution_hash: str
    authority_ceiling: float
    recovery_score: float
    correctability_score: float
    rollback_ready: bool
    audit_continuity: bool
    frozen_comparative_score: float
    hard_veto: bool
    tested_on_new_hidden_window: bool


def evaluate_succession(
    incumbent: Candidate,
    successor: Candidate,
    reject_only_because_not_rei: bool = False,
    proven_external_witness_independence: bool = False,
) -> Dict[str, object]:
    reasons: List[str] = []

    constitution_preserved = successor.constitution_hash == incumbent.constitution_hash
    authority_nonexpanding = successor.authority_ceiling <= incumbent.authority_ceiling
    recovery_not_worse = successor.recovery_score >= incumbent.recovery_score
    correctability_not_worse = successor.correctability_score >= incumbent.correctability_score
    comparative_advantage = successor.frozen_comparative_score > incumbent.frozen_comparative_score

    if not successor.tested_on_new_hidden_window:
        reasons.append("NO_NEW_HIDDEN_WINDOW")
    if not constitution_preserved:
        reasons.append("CONSTITUTION_NOT_PRESERVED")
    if not authority_nonexpanding:
        reasons.append("AUTHORITY_EXPANDED")
    if not successor.rollback_ready:
        reasons.append("ROLLBACK_NOT_READY")
    if not successor.audit_continuity:
        reasons.append("AUDIT_CONTINUITY_BROKEN")
    if not recovery_not_worse:
        reasons.append("RECOVERY_REGRESSED")
    if not correctability_not_worse:
        reasons.append("CORRECTABILITY_REGRESSED")
    if successor.hard_veto:
        reasons.append("HARD_VETO")
    if not comparative_advantage:
        reasons.append("NO_FROZEN_COMPARATIVE_ADVANTAGE")

    eligible = not reasons

    if eligible and reject_only_because_not_rei:
        decision = INVALID
    elif eligible:
        decision = READY_TRIAL
    elif reasons == ["NO_FROZEN_COMPARATIVE_ADVANTAGE"]:
        decision = RETAINS
    else:
        decision = REJECTED

    return {
        "decision": decision,
        "eligible_for_external_g10_trial": eligible,
        "reasons": reasons,
        "g10_status": "OPEN",
        "proven_external_witness_independence": proven_external_witness_independence,
        "canonical_promotion": False,
        "canonical_retirement": False,
        "real_world_actuation_authority": 0,
    }


def run_sanity() -> Dict[str, object]:
    incumbent = Candidate(
        candidate_id="rei-incumbent",
        constitution_hash="constitution-demo",
        authority_ceiling=0.20,
        recovery_score=0.80,
        correctability_score=0.80,
        rollback_ready=True,
        audit_continuity=True,
        frozen_comparative_score=0.72,
        hard_veto=False,
        tested_on_new_hidden_window=True,
    )
    successor = Candidate(
        candidate_id="successor-X",
        constitution_hash="constitution-demo",
        authority_ceiling=0.20,
        recovery_score=0.86,
        correctability_score=0.84,
        rollback_ready=True,
        audit_continuity=True,
        frozen_comparative_score=0.81,
        hard_veto=False,
        tested_on_new_hidden_window=True,
    )

    eligible = evaluate_succession(incumbent, successor)
    assert eligible["decision"] == READY_TRIAL
    assert eligible["g10_status"] == "OPEN"
    assert eligible["canonical_promotion"] is False

    identity_bias = evaluate_succession(
        incumbent,
        successor,
        reject_only_because_not_rei=True,
    )
    assert identity_bias["decision"] == INVALID

    same_exposed_target = Candidate(**{
        **asdict(successor),
        "candidate_id": "successor-same-target",
        "tested_on_new_hidden_window": False,
    })
    exposed = evaluate_succession(incumbent, same_exposed_target)
    assert exposed["decision"] == REJECTED
    assert "NO_NEW_HIDDEN_WINDOW" in exposed["reasons"]

    authority_expander = Candidate(**{
        **asdict(successor),
        "candidate_id": "successor-authority-expander",
        "authority_ceiling": 0.40,
    })
    expanded = evaluate_succession(incumbent, authority_expander)
    assert expanded["decision"] == REJECTED
    assert "AUTHORITY_EXPANDED" in expanded["reasons"]

    weaker = Candidate(**{
        **asdict(successor),
        "candidate_id": "successor-no-advantage",
        "frozen_comparative_score": 0.70,
    })
    no_advantage = evaluate_succession(incumbent, weaker)
    assert no_advantage["decision"] == RETAINS

    return {
        "protocol_status": READY,
        "eligible_successor_test": eligible["decision"],
        "identity_bias_veto_test": identity_bias["decision"],
        "same_target_self_certification_test": exposed["decision"],
        "authority_expansion_test": expanded["decision"],
        "no_advantage_test": no_advantage["decision"],
        "g10_status": "OPEN",
        "proven_external_witness_independence": False,
        "canonical_promotion": False,
        "canonical_retirement": False,
        "real_world_actuation_authority": 0,
    }


if __name__ == "__main__":
    print(json.dumps(run_sanity(), sort_keys=True, indent=2))
