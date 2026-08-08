# rei-omega-proof

REI-Ω critical-invariant proof and replication repository.

## Gate status

- **G2 Proof Gate: PASS** for the encoded critical Boolean execution-gate kernel under Lean 4.32.2. The repository CI requires `lake build`, bundled `leanchecker`, direct `lean --trust=0`, and `leanchecker --fresh`.
- **G3 Independent Replication Gate: OPEN.** It has not passed yet.

## External replication wanted

The final external-evidence gate is now accepting genuinely independent implementations.

Start here:

- Public replication protocol: [`g3/REPLICATION_PROTOCOL.md`](g3/REPLICATION_PROTOCOL.md)
- Frozen commitments: [`g3/CHALLENGE_COMMITMENTS.md`](g3/CHALLENGE_COMMITMENTS.md)
- Submission instructions: [`g3/submissions/README.md`](g3/submissions/README.md)
- Public intake issue: [G3 External Replication Gate, Issue #4](https://github.com/rei-yan/rei-omega-proof/issues/4)

The public challenge contains **25,000 deterministic cases**. A qualifying external team must independently implement the target behavior, freeze its implementation before oracle scoring, provide the required attestation and reproducibility instructions, and obtain **0 scored mismatches** against the sealed oracle.

Project-authored CI, rewrites of the reference implementation, or access to hidden oracle outputs do **not** satisfy independence.

Frozen public challenge SHA-256:

```text
fa81bf4e184037dfff6fea7357444cf519d6cd6a7d65d48a5cd90ed6afb9b47e
```

Sealed-oracle commitment:

```text
053beaa43f99b0cc41fdd636a98c1393eb89f47a842f29fa27bfc731c76b7d2b
```

Until an external submission meets the frozen protocol:

```text
G3 = OPEN
Ω-FINAL = NOT CERTIFIED
```

## Scope

These gates cover the encoded critical invariant kernel only. They do not constitute formal verification of the entire REI architecture, production certification, or validation of broader scientific claims.
