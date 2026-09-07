from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "runtime" / "REI-PhaseII5-AtomicOwnership-Patch-v1.ps1"
PREREG = ROOT / "research" / "REI_PHASEII5_ATOMIC_OWNERSHIP_THROUGH_DELETE.md"
ANNOTATION = ROOT / "research" / "REI_PHASEII3_SUPERSEDED_ANNOTATION_20260906.md"

EXPECTED_PY = "6752672711E1FF7BA5F7035221E88403EAAEE716E444573D82477A62D51EC3DB"
EXPECTED_HEAL = "11CECB2192E7555029804A8A75BB3FB6394302F11F09FF1E5CF2DA1D69CF4323"
BASELINE = "cc85cb647188eefe182cfc5ab6364d9f146ef96a"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    patch = PATCH.read_text(encoding="utf-8")
    prereg = PREREG.read_text(encoding="utf-8")
    annotation = ANNOTATION.read_text(encoding="utf-8")

    require(EXPECTED_PY in patch, "Python production pin missing")
    require(EXPECTED_HEAL in patch, "Phase II.4 Self-Heal production pin missing")
    require(EXPECTED_HEAL in prereg, "prereg does not pin Phase II.4 Self-Heal")

    helper_start = patch.index("function Invoke-OsByteLockProtectedRemoval")
    helper_end = patch.index("'@", helper_start)
    helper = patch[helper_start:helper_end]

    open_idx = helper.index("[System.IO.FileShare]::ReadWrite -bor [System.IO.FileShare]::Delete")
    lock_idx = helper.index("$stream.Lock(0,1)")
    remove_idx = helper.index("Remove-Item -LiteralPath $LockPath -Force -ErrorAction Stop")
    unlock_idx = helper.index("$stream.Unlock(0,1)")
    dispose_idx = helper.index("$stream.Dispose()")

    require(open_idx < lock_idx < remove_idx < unlock_idx < dispose_idx,
            "protected-removal ordering is not open -> lock -> remove -> unlock -> dispose")
    require("finally {" in helper, "protected removal lacks finally cleanup")
    require("atomic_remove_authority_unavailable" in helper, "authority contention is not attributable")
    require("atomic_remove_failed" in helper, "destructive failure is not attributable")

    require("Invoke-OsByteLockProtectedRemoval -LockPath $lock" in patch,
            "Clear-OrphanLocks protected removal call missing")
    require("Invoke-OsByteLockProtectedRemoval -LockPath $lockPath" in patch,
            "Repair-OrphanRuntimeLock protected removal call missing")
    require("Replace-ExactlyOnce" in patch, "installer must use exact unique anchors")
    require("SAFE_ABORT" in patch, "installer lacks fail-closed source/window aborts")
    require("ROLLBACK_MATCHES_PHASEII4_PIN" in patch, "rollback evidence check missing")

    require("0045A" in prereg and "COMPETING_OWNER_MUST_NOT_ACQUIRE" in prereg,
            "critical race falsifier not preregistered")
    require("0045B" in prereg and "0045C" in prereg and "0045D" in prereg,
            "full regression matrix not preregistered")
    require("One phase, one race" in prereg, "scope compression rule missing")

    require("SUPERSEDED_FOR_CURRENT_PRODUCTION_BEHAVIOR" in annotation,
            "Phase II.3 current applicability is not marked superseded")
    require("5415F055" in annotation and "11CECB21" in annotation,
            "supersession annotation lacks old/new source pins")
    require("HISTORICALLY_VALID / CURRENTLY_SUPERSEDED" in annotation,
            "historical validity/current supersession distinction missing")

    # This sanity is deliberately static. It must never manufacture runtime claims.
    forbidden_claims = [
        "RealityValidated = TRUE",
        "ASCENSION_GRANTED = YES",
        "CanonicalPromotion = YES",
    ]
    for claim in forbidden_claims:
        require(claim not in prereg, f"forbidden promotion claim present: {claim}")

    print("PHASEII5_STATIC_SANITY=PASS")
    print(f"BASELINE_EXPECTED={BASELINE}")
    print("HOST_DEPLOYMENT_VERIFIED=False")
    print("REALITY_VALIDATED=False")


if __name__ == "__main__":
    main()
