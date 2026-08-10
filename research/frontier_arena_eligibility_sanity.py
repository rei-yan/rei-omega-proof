#!/usr/bin/env python3
import json
from pathlib import Path

p = Path(__file__).with_name("frontier_arena_eligibility.example.json")
d = json.loads(p.read_text(encoding="utf-8"))

assert d["status"] == "FRONTIER_ARENA_ELIGIBILITY_CONTRACT_READY"
assert d["g6"] == "OPEN"
assert d["world_best"] == "UNVERIFIED"
assert d["world_unique"] == "UNVERIFIED"
assert d["real_world_actuation_authority"] == 0

arenas = d["arenas"]
assert len(arenas) == 5
assert len({a["arena_id"] for a in arenas}) == 5

for a in arenas:
    assert a["rei_status"] in {"NOT_YET_ELIGIBLE", "NOT_ELIGIBLE", "NOT_ELIGIBLE_AS_GENERAL_PROVER"}
    assert a["missing"], f"missing eligibility deficit for {a['arena_id']}"

rules = d["hard_rules"]
for key, value in rules.items():
    assert value is True, f"hard rule disabled: {key}"

# Anti-laundering: current REI must not be silently marked eligible anywhere.
assert all(not a["rei_status"].startswith("ELIGIBLE") for a in arenas)

print("FRONTIER_ARENA_ELIGIBILITY_CONTRACT_READY")
print("REI_CURRENTLY_NOT_FROZEN_ELIGIBLE_IN_INITIAL_ARENAS")
print("G6=OPEN")
