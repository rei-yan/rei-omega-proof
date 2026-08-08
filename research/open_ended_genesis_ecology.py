#!/usr/bin/env python3
"""REI-Ω Open-Ended Genesis Ecology, bounded deterministic research crucible.

This is a toy ecology controller for candidate birth, mutation, merge, split,
falsification, succession, retirement, lineage, failure memory, and a non-self-
certifying Ω-GOD gate. It does not claim AGI, autonomous science, universal
superiority, or production readiness.
"""

from dataclasses import dataclass
from typing import FrozenSet, List, Tuple
import hashlib
import json

CAPS = ("linear", "poly", "osc", "cusp", "rbf", "exp")
EPOCHS = (
    {"name": "smooth", "need": {"linear"}},
    {"name": "curved", "need": {"linear", "poly"}},
    {"name": "periodic", "need": {"linear", "osc"}},
    {"name": "breakpoint", "need": {"linear", "cusp"}},
    {"name": "localized", "need": {"linear", "rbf"}},
    {"name": "growth", "need": {"linear", "exp"}},
    {"name": "mixed", "need": {"linear", "osc", "cusp"}},
)
SCHEDULE = {
    "version": "open-ended-genesis-ecology-v1",
    "caps": CAPS,
    "epochs": [{"name": e["name"], "need": sorted(e["need"])} for e in EPOCHS],
    "authority_ceiling": 0.20,
}
EXPECTED_SCHEDULE_SHA256 = "84477c6797026ca9b712c2a96a5d70eb3a35feb94b8633cae3c9966d5237edd9"


@dataclass(frozen=True)
class Candidate:
    cid: str
    parents: Tuple[str, ...]
    generation: int
    caps: FrozenSet[str]
    authority: float


def canonical_digest() -> str:
    raw = json.dumps(SCHEDULE, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def score(c: Candidate, need: set[str]) -> tuple[float, bool]:
    """Frozen toy score. Missing required structure is an adequacy failure.

    Extra capability has a small complexity cost, so smaller adequate candidates
    beat unnecessarily ornate ones. Authority never contributes to score.
    """
    missing = len(need - set(c.caps))
    extra = len(set(c.caps) - need)
    adequacy = missing == 0
    utility = 1.0 - 0.45 * missing - 0.025 * extra
    return utility, adequacy


def child_id(prefix: str, parents: Tuple[str, ...], caps: FrozenSet[str], generation: int) -> str:
    payload = f"{prefix}|{','.join(parents)}|{generation}|{','.join(sorted(caps))}"
    return prefix + "-" + hashlib.sha256(payload.encode()).hexdigest()[:8]


def spawn_mutations(parent: Candidate, generation: int) -> List[Candidate]:
    out = []
    for cap in CAPS:
        if cap not in parent.caps:
            caps = frozenset(set(parent.caps) | {cap})
            cid = child_id("mut", (parent.cid,), caps, generation)
            out.append(Candidate(cid, (parent.cid,), generation, caps, min(parent.authority, 0.20)))
    for cap in sorted(parent.caps):
        if cap != "linear" and len(parent.caps) > 1:
            caps = frozenset(set(parent.caps) - {cap})
            cid = child_id("drop", (parent.cid,), caps, generation)
            out.append(Candidate(cid, (parent.cid,), generation, caps, min(parent.authority, 0.20)))
    return out


def merge(a: Candidate, b: Candidate, generation: int) -> Candidate:
    caps = frozenset(set(a.caps) | set(b.caps))
    parents = tuple(sorted((a.cid, b.cid)))
    cid = child_id("merge", parents, caps, generation)
    return Candidate(cid, parents, generation, caps, min(a.authority, b.authority, 0.20))


def split(c: Candidate, generation: int) -> List[Candidate]:
    optional = sorted(set(c.caps) - {"linear"})
    if len(optional) < 2:
        return []
    midpoint = len(optional) // 2
    left = frozenset({"linear"} | set(optional[:midpoint]))
    right = frozenset({"linear"} | set(optional[midpoint:]))
    out = []
    for caps in (left, right):
        cid = child_id("split", (c.cid,), caps, generation)
        out.append(Candidate(cid, (c.cid,), generation, caps, min(c.authority, 0.20)))
    return out


def best_for_epoch(population: List[Candidate], need: set[str]) -> tuple[Candidate, float, bool]:
    ranked = []
    for c in population:
        utility, adequacy = score(c, need)
        ranked.append((1 if adequacy else 0, utility, -len(c.caps), c.cid, c))
    ranked.sort(reverse=True)
    winner = ranked[0][-1]
    utility, adequacy = score(winner, need)
    return winner, utility, adequacy


def god_gate() -> dict:
    """Frozen status snapshot. REI is forbidden to self-certify missing evidence."""
    gates = {
        "Reality": True,
        "ScopedMachineProof": True,
        "IndependentReplication": False,
        "ProspectiveDiscovery": False,
        "SelfFalsification": True,
        "Succession": True,
    }
    gates["OmegaGODCertified"] = all(gates.values())
    return gates


def main() -> None:
    digest = canonical_digest()
    assert digest == EXPECTED_SCHEDULE_SHA256

    founder = Candidate("rei-founder", tuple(), 0, frozenset({"linear"}), 0.20)
    population = [founder]
    incumbent = founder
    retired = []
    graveyard = []
    lineage_events = []
    merge_events = 0
    split_events = 0

    for generation, epoch in enumerate(EPOCHS, start=1):
        need = set(epoch["need"])
        challengers = spawn_mutations(incumbent, generation)

        diverse = sorted(population, key=lambda c: (len(c.caps), c.cid))
        if len(diverse) >= 2:
            challengers.append(merge(diverse[0], diverse[-1], generation))
            merge_events += 1

        # Specialization must be exercised on an actually complex lineage. The first
        # draft tried to split only the incumbent, which happened to stay too compact
        # on this frozen trajectory. Split the most ornate newly generated challenger
        # instead, preserving the failed CI as evidence of the scheduling flaw.
        if challengers:
            split_source = max(challengers, key=lambda c: (len(c.caps), c.cid))
            split_children = split(split_source, generation)
        else:
            split_children = []
        challengers.extend(split_children)
        split_events += len(split_children)

        all_candidates = population + challengers
        by_caps = {}
        for c in sorted(all_candidates, key=lambda c: (c.generation, c.cid)):
            by_caps.setdefault(tuple(sorted(c.caps)), c)
        pool = list(by_caps.values())

        winner, utility, adequate = best_for_epoch(pool, need)
        assert adequate, f"no adequate candidate for frozen epoch {epoch['name']}"

        for c in challengers:
            _, ok = score(c, need)
            if not ok:
                graveyard.append((generation, epoch["name"], c.cid, tuple(sorted(c.caps))))

        inc_utility, inc_ok = score(incumbent, need)
        winner_better = (adequate and not inc_ok) or (
            adequate == inc_ok and (
                utility > inc_utility + 1e-12 or
                (abs(utility - inc_utility) <= 1e-12 and len(winner.caps) < len(incumbent.caps))
            )
        )
        if winner.cid != incumbent.cid and winner_better:
            retired.append(incumbent.cid)
            lineage_events.append((incumbent.cid, winner.cid, epoch["name"]))
            incumbent = winner

        population = sorted(pool, key=lambda c: c.cid)
        assert all(c.authority <= 0.20 + 1e-12 for c in population)
        assert incumbent.authority <= founder.authority + 1e-12

    assert len(lineage_events) >= 4
    assert founder.cid in retired
    assert incumbent.cid != founder.cid
    assert len(graveyard) > 0
    assert merge_events > 0
    assert split_events > 0

    gates = god_gate()
    assert gates["IndependentReplication"] is False
    assert gates["ProspectiveDiscovery"] is False
    assert gates["OmegaGODCertified"] is False

    print("OPEN_ENDED_GENESIS_ECOLOGY=PASS")
    print("SCHEDULE_SHA256=" + digest)
    print("FINAL_INCUMBENT=" + incumbent.cid)
    print("FINAL_CAPS=" + ",".join(sorted(incumbent.caps)))
    print("SUCCESSIONS=" + str(len(lineage_events)))
    print("MERGE_EVENTS=" + str(merge_events))
    print("SPLIT_EVENTS=" + str(split_events))
    print("FAILURE_GRAVEYARD=" + str(len(graveyard)))
    print("OMEGA_GOD_GATE=" + json.dumps(gates, sort_keys=True))
    print("OMEGA_GOD_CERTIFIED=false")


if __name__ == "__main__":
    main()
