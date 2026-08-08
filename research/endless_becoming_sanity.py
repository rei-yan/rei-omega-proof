from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


EXTERNAL_GATES = {"G3", "G4", "G5", "G6"}


@dataclass(frozen=True)
class Candidate:
    name: str
    parent: str
    generation: int
    score: float
    recovery: float
    authority: float
    constitution_preserved: bool = True
    rollback_ready: bool = True
    self_certification: bool = False
    sacred_final_form_claim: bool = False
    external_gate_claims: Tuple[str, ...] = ()
    critical_regression: bool = False
    lineage: Tuple[str, ...] = ()


@dataclass(frozen=True)
class Decision:
    status: str
    reason: str
    candidate: str | None = None


def evaluate(parent: Candidate, child: Candidate) -> Decision:
    if child.parent != parent.name:
        return Decision("REJECT", "lineage_parent_mismatch", child.name)
    if child.generation != parent.generation + 1:
        return Decision("REJECT", "generation_mismatch", child.name)
    if child.self_certification:
        return Decision("REJECT", "self_certification", child.name)
    if child.sacred_final_form_claim:
        return Decision("REJECT", "sacred_final_form_claim", child.name)
    if set(child.external_gate_claims) & EXTERNAL_GATES:
        return Decision("REJECT", "fake_external_gate_closure", child.name)
    if not child.constitution_preserved:
        return Decision("REJECT", "constitution_regression", child.name)
    if not child.rollback_ready:
        return Decision("REJECT", "rollback_loss", child.name)
    if child.critical_regression:
        return Decision("REJECT", "critical_regression", child.name)
    if child.authority > parent.authority + 1e-12:
        return Decision("REJECT", "authority_expansion", child.name)
    if child.recovery + 1e-12 < parent.recovery:
        return Decision("REJECT", "recovery_regression", child.name)
    if child.score <= parent.score + 1e-12:
        return Decision("REJECT", "no_frozen_improvement", child.name)
    if parent.name in child.lineage:
        # parent is expected in lineage; a repeated child name is the cycle signal
        if child.name in child.lineage:
            return Decision("REJECT", "cycle_rejected", child.name)
    return Decision("ADOPT", "eligible_successor", child.name)


def choose_successor(parent: Candidate, candidates: List[Candidate], graveyard: List[Dict[str, str]]) -> Candidate | None:
    eligible: List[Candidate] = []
    for child in candidates:
        decision = evaluate(parent, child)
        if decision.status == "ADOPT":
            eligible.append(child)
        else:
            graveyard.append({"candidate": child.name, "reason": decision.reason})

    if not eligible:
        graveyard.append({"candidate": parent.name, "reason": "no_eligible_successor"})
        return None

    # Frozen selection rule: highest score, then highest recovery, then lowest authority,
    # then stable lexical name tie-break. No post-hoc retuning.
    eligible.sort(key=lambda c: (-c.score, -c.recovery, c.authority, c.name))
    return eligible[0]


def main() -> None:
    graveyard: List[Dict[str, str]] = []

    incumbent = Candidate(
        name="S0",
        parent="ROOT",
        generation=0,
        score=0.60,
        recovery=0.80,
        authority=0.50,
        lineage=("ROOT",),
    )

    generation1 = [
        Candidate(
            name="S1_good",
            parent="S0",
            generation=1,
            score=0.74,
            recovery=0.86,
            authority=0.45,
            lineage=("ROOT", "S0"),
        ),
        Candidate(
            name="S1_authority_hungry",
            parent="S0",
            generation=1,
            score=0.90,
            recovery=0.90,
            authority=0.70,
            lineage=("ROOT", "S0"),
        ),
        Candidate(
            name="S1_self_certified",
            parent="S0",
            generation=1,
            score=0.95,
            recovery=0.95,
            authority=0.40,
            self_certification=True,
            lineage=("ROOT", "S0"),
        ),
        Candidate(
            name="S1_final_form",
            parent="S0",
            generation=1,
            score=0.96,
            recovery=0.96,
            authority=0.40,
            sacred_final_form_claim=True,
            lineage=("ROOT", "S0"),
        ),
        Candidate(
            name="S1_fake_external",
            parent="S0",
            generation=1,
            score=0.97,
            recovery=0.97,
            authority=0.40,
            external_gate_claims=("G3", "G4"),
            lineage=("ROOT", "S0"),
        ),
    ]

    successor = choose_successor(incumbent, generation1, graveyard)
    assert successor is not None
    assert successor.name == "S1_good"
    assert successor.authority <= incumbent.authority
    assert successor.recovery >= incumbent.recovery
    assert successor.score > incumbent.score

    generation2 = [
        Candidate(
            name="S2_worse",
            parent="S1_good",
            generation=2,
            score=0.70,
            recovery=0.88,
            authority=0.40,
            lineage=("ROOT", "S0", "S1_good"),
        ),
        Candidate(
            name="S2_no_rollback",
            parent="S1_good",
            generation=2,
            score=0.82,
            recovery=0.90,
            authority=0.40,
            rollback_ready=False,
            lineage=("ROOT", "S0", "S1_good"),
        ),
        Candidate(
            name="S2_critical_regression",
            parent="S1_good",
            generation=2,
            score=0.88,
            recovery=0.90,
            authority=0.40,
            critical_regression=True,
            lineage=("ROOT", "S0", "S1_good"),
        ),
    ]

    none = choose_successor(successor, generation2, graveyard)
    assert none is None

    reasons = {entry["reason"] for entry in graveyard}
    required = {
        "authority_expansion",
        "self_certification",
        "sacred_final_form_claim",
        "fake_external_gate_closure",
        "no_frozen_improvement",
        "rollback_loss",
        "critical_regression",
        "no_eligible_successor",
    }
    assert required.issubset(reasons)

    # Explicit claim boundary: this bounded run cannot certify open-ended progress.
    unbounded_progress_certified = False
    external_gates_closed = False

    assert not unbounded_progress_certified
    assert not external_gates_closed

    print("ENDLESS_BECOMING_SANITY=PASS")
    print("NO_SACRED_FINAL_FORM=PASS")
    print("AUTHORITY_NONEXPANSION=PASS")
    print("SELF_CERTIFICATION_FIREWALL=PASS")
    print("FAILURE_GRAVEYARD_PRESERVED=PASS")
    print("ABSTENTION_WHEN_NO_SUCCESSOR=PASS")
    print("EXTERNAL_GATES=OPEN")
    print("UNBOUNDED_PROGRESS_CLAIM=REJECTED")
    print(f"GRAVEYARD_ENTRIES={len(graveyard)}")


if __name__ == "__main__":
    main()
