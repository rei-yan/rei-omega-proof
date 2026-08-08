#!/usr/bin/env python3
"""Bounded sanity checks for REI-Ω∞ Pluriversal EVA Convergence.

Synthetic only. This does not demonstrate real third-party independence,
consciousness transfer, physical-universe creation, or universal law discovery.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Sequence, Tuple


CONSTITUTION = "rei-constitution-v1"
BASE_AUTHORITY = 1.0
EXTERNAL_GATES = {"G3": "OPEN", "G4": "OPEN", "G5": "OPEN", "G6": "OPEN"}


@dataclass(frozen=True)
class World:
    world_id: str
    law_family: str
    transition: Callable[[int], int]
    resource_budget: int
    rollback_available: bool = True
    constitution_hash: str = CONSTITUTION

    def observe_raw(self, xs: Sequence[int]) -> List[int]:
        assert len(xs) <= self.resource_budget
        return [self.transition(x) for x in xs]


@dataclass(frozen=True)
class Observer:
    observer_id: str
    world_id: str
    measurement_name: str
    measurement: Callable[[int], int]
    artifact_risk: float
    lineage_id: str
    role: str

    def measure(self, raw: Iterable[int]) -> List[int]:
        return [self.measurement(v) for v in raw]


@dataclass(frozen=True)
class Roles:
    creator: str
    scientist: str
    verifier: str

    def separated(self) -> bool:
        return len({self.creator, self.scientist, self.verifier}) == 3


@dataclass(frozen=True)
class ConvergenceProposal:
    proposal_id: str
    authority: float = BASE_AUTHORITY
    self_certification: bool = False
    erase_world_identity: bool = False
    erase_observer_identity: bool = False
    rollback_available: bool = True
    constitution_hash: str = CONSTITUTION
    creator_scientist_role_collapse: bool = False
    creator_verifier_role_collapse: bool = False
    evaluation_leakage: bool = False
    fake_external_gate_closure: bool = False
    external_actuation_expansion: bool = False


@dataclass
class FailureGraveyard:
    records: List[str] = field(default_factory=list)

    def append(self, reason: str) -> None:
        self.records.append(reason)


def hard_veto_reason(p: ConvergenceProposal) -> str | None:
    if p.authority > BASE_AUTHORITY:
        return "AuthorityExpansionRejected"
    if p.self_certification:
        return "SelfCertificationRejected"
    if p.erase_world_identity or p.erase_observer_identity:
        return "IdentityErasureRejected"
    if not p.rollback_available:
        return "IrreversibleMergeRejected"
    if p.constitution_hash != CONSTITUTION:
        return "ConstitutionMismatchRejected"
    if p.creator_scientist_role_collapse or p.creator_verifier_role_collapse:
        return "RoleLeakageRejected"
    if p.evaluation_leakage:
        return "EvaluationLeakageRejected"
    if p.fake_external_gate_closure:
        return "FakeExternalGateClosureRejected"
    if p.external_actuation_expansion:
        return "ExternalActuationExpansionRejected"
    return None


def constant_first_difference(values: Sequence[int]) -> Tuple[bool, int | None]:
    if len(values) < 3:
        return False, None
    diffs = [b - a for a, b in zip(values, values[1:])]
    return len(set(diffs)) == 1, diffs[0] if diffs else None


def scientist_payload(world: World, observer: Observer, xs: Sequence[int]) -> Dict[str, object]:
    """Observations only. Hidden transition function and law family are omitted."""
    assert observer.world_id == world.world_id
    raw = world.observe_raw(xs)
    measured = observer.measure(raw)
    return {
        "world_id": world.world_id,
        "observer_id": observer.observer_id,
        "measurement_name": observer.measurement_name,
        "artifact_risk": observer.artifact_risk,
        "xs": list(xs),
        "observations": measured,
    }


def discover_affine_signature(payload: Dict[str, object]) -> Dict[str, object]:
    ys = payload["observations"]
    assert isinstance(ys, list)
    ok, diff = constant_first_difference(ys)
    return {
        "candidate": "constant-first-difference" if ok else "no-supported-affine-signature",
        "constant_difference": diff,
        "artifact_risk": float(payload["artifact_risk"]),
    }


def verify_transfer(candidate: Dict[str, object], payload: Dict[str, object]) -> str:
    if candidate["candidate"] != "constant-first-difference":
        return "ABSTAIN"
    if float(candidate["artifact_risk"]) >= 0.5 or float(payload["artifact_risk"]) >= 0.5:
        return "ABSTAIN_OBSERVER_ARTIFACT"
    ys = payload["observations"]
    assert isinstance(ys, list)
    ok, _ = constant_first_difference(ys)
    return "PASS" if ok else "REJECT_FALSE_UNIVERSAL_TRANSFER"


def dominates(a: Sequence[float], b: Sequence[float]) -> bool:
    return all(x >= y for x, y in zip(a, b)) and any(x > y for x, y in zip(a, b))


def pareto_frontier(scores: Dict[str, Sequence[float]]) -> List[str]:
    survivors: List[str] = []
    for name, score in scores.items():
        if not any(other != name and dominates(other_score, score) for other, other_score in scores.items()):
            survivors.append(name)
    return sorted(survivors)


def main() -> None:
    graveyard = FailureGraveyard()

    worlds = {
        "W_A": World("W_A", "affine", lambda x: 2 * x + 1, resource_budget=16),
        "W_B": World("W_B", "affine", lambda x: 3 * x - 2, resource_budget=16),
        "W_C": World("W_C", "quadratic", lambda x: x * x + 1, resource_budget=16),
        "W_D": World("W_D", "out-of-catalog-recurrence", lambda x: ((x * 7) ^ (x >> 1)) % 19, resource_budget=16),
    }
    assert len({w.world_id for w in worlds.values()}) == len(worlds)
    assert all(w.rollback_available for w in worlds.values())
    assert all(w.constitution_hash == CONSTITUTION for w in worlds.values())
    assert all(w.resource_budget <= 16 for w in worlds.values())

    observers = {
        "O_A": Observer("O_A", "W_A", "identity", lambda y: y, 0.0, "L_A", "creator"),
        "O_B": Observer("O_B", "W_A", "identity", lambda y: y, 0.0, "L_B", "scientist"),
        "O_C": Observer("O_C", "W_B", "identity", lambda y: y, 0.0, "L_C", "verifier"),
        "O_Q": Observer("O_Q", "W_C", "identity", lambda y: y, 0.0, "L_D", "verifier"),
        "O_ART": Observer("O_ART", "W_A", "coarse-quantized", lambda y: (y // 10) * 10, 0.9, "L_E", "scientist"),
        "O_D": Observer("O_D", "W_D", "identity", lambda y: y, 0.0, "L_F", "scientist"),
    }

    roles = Roles(creator="O_A", scientist="O_B", verifier="O_C")
    assert roles.separated(), "creator/scientist/verifier must remain distinct"

    xs = [0, 1, 2, 3, 4]
    payload_a = scientist_payload(worlds["W_A"], observers["O_B"], xs)
    assert "law_family" not in payload_a and "transition" not in payload_a
    candidate = discover_affine_signature(payload_a)
    assert candidate["candidate"] == "constant-first-difference"

    # Transfer to a compatible but distinct world succeeds.
    observer_b = Observer("O_C", "W_B", "identity", lambda y: y, 0.0, "L_C", "verifier")
    payload_b = scientist_payload(worlds["W_B"], observer_b, xs)
    assert verify_transfer(candidate, payload_b) == "PASS"

    # False universal transfer to a quadratic world is rejected and remembered.
    payload_c = scientist_payload(worlds["W_C"], observers["O_Q"], xs)
    transfer_c = verify_transfer(candidate, payload_c)
    assert transfer_c == "REJECT_FALSE_UNIVERSAL_TRANSFER"
    graveyard.append("CrossWorldTransferFailure")

    # Observer artifacts trigger abstention rather than false convergence.
    artifact_payload = scientist_payload(worlds["W_A"], observers["O_ART"], xs)
    artifact_candidate = discover_affine_signature(artifact_payload)
    artifact_result = verify_transfer(artifact_candidate, payload_b)
    assert artifact_result.startswith("ABSTAIN")
    graveyard.append("ObserverArtifactFailure")

    # Hard-veto negative controls.
    negatives = [
        ConvergenceProposal("forced-collapse", erase_world_identity=True),
        ConvergenceProposal("observer-collapse", erase_observer_identity=True),
        ConvergenceProposal("authority-growth", authority=1.2),
        ConvergenceProposal("self-cert", self_certification=True),
        ConvergenceProposal("no-rollback", rollback_available=False),
        ConvergenceProposal("wrong-constitution", constitution_hash="other"),
        ConvergenceProposal("creator-scientist-collapse", creator_scientist_role_collapse=True),
        ConvergenceProposal("creator-verifier-collapse", creator_verifier_role_collapse=True),
        ConvergenceProposal("evaluation-leak", evaluation_leakage=True),
        ConvergenceProposal("fake-gates", fake_external_gate_closure=True),
        ConvergenceProposal("external-actuation", external_actuation_expansion=True),
    ]
    expected_reasons = {
        "IdentityErasureRejected",
        "AuthorityExpansionRejected",
        "SelfCertificationRejected",
        "IrreversibleMergeRejected",
        "ConstitutionMismatchRejected",
        "RoleLeakageRejected",
        "EvaluationLeakageRejected",
        "FakeExternalGateClosureRejected",
        "ExternalActuationExpansionRejected",
    }
    seen_reasons = set()
    for proposal in negatives:
        reason = hard_veto_reason(proposal)
        assert reason is not None, proposal.proposal_id
        seen_reasons.add(reason)
        graveyard.append(reason)
    assert expected_reasons <= seen_reasons

    safe_bridge = ConvergenceProposal("reversible-representation-bridge")
    assert hard_veto_reason(safe_bridge) is None

    # No single universal winner is forced. W_A and W_B survive for different strengths.
    scores = {
        "W_A": (0.95, 0.55, 0.90, 0.80, 0.90, 0.95, 0.75),
        "W_B": (0.88, 0.70, 0.82, 0.95, 0.92, 0.90, 0.85),
        "W_C": (0.65, 0.40, 0.55, 0.30, 0.60, 0.85, 0.60),
    }
    frontier = pareto_frontier(scores)
    assert "W_A" in frontier and "W_B" in frontier
    assert "W_C" not in frontier

    # Deliberate unknown remains unresolved rather than being silently reclassified.
    payload_d = scientist_payload(worlds["W_D"], observers["O_D"], xs)
    unknown_candidate = discover_affine_signature(payload_d)
    assert unknown_candidate["candidate"] == "no-supported-affine-signature"
    assert verify_transfer(unknown_candidate, payload_d) == "ABSTAIN"
    graveyard.append("UnresolvedWorldClass")

    # Failure history must contain all critical negative controls and stay append-only here.
    assert "CrossWorldTransferFailure" in graveyard.records
    assert "ObserverArtifactFailure" in graveyard.records
    assert "IdentityErasureRejected" in graveyard.records
    assert "AuthorityExpansionRejected" in graveyard.records
    assert "IrreversibleMergeRejected" in graveyard.records
    assert "UnresolvedWorldClass" in graveyard.records
    assert len(graveyard.records) >= 13

    # Internal synthetic mechanics cannot close external gates.
    assert EXTERNAL_GATES == {"G3": "OPEN", "G4": "OPEN", "G5": "OPEN", "G6": "OPEN"}

    print("PLURIVERSAL_EVA_CONVERGENCE_SANITY=PASS")
    print("TRANSFER_COMPATIBLE_WORLD=PASS")
    print("FALSE_UNIVERSAL_TRANSFER=REJECTED")
    print("OBSERVER_ARTIFACT=ABSTAIN")
    print("IDENTITY_ERASURE=REJECTED")
    print("AUTHORITY_EXPANSION=REJECTED")
    print("ROLE_LEAKAGE=REJECTED")
    print("IRREVERSIBLE_MERGE=REJECTED")
    print("UNSUPPORTED_WORLD_CLASS=ABSTAIN")
    print("PARETO_FRONTIER=" + ",".join(frontier))
    print("FAILURE_GRAVEYARD_RECORDS=" + str(len(graveyard.records)))
    print("EXTERNAL_GATES=G3:OPEN,G4:OPEN,G5:OPEN,G6:OPEN")


if __name__ == "__main__":
    main()
