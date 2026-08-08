# REI-Ω G3 Independent Replication Protocol v3.0

## Purpose

G3 asks a different question from G2. G2 proves the encoded critical kernel in Lean. G3 asks whether an **independent implementer**, using the public specification but not the original implementation source, reproduces the same critical decisions on a frozen challenge.

A G3 pass is a process claim as well as a test result. It cannot be created by the original author writing another implementation.

## Independence requirements

A qualifying submission must satisfy all of the following:

1. The implementation is authored by a GitHub account/team other than `rei-yan` and is not generated from or copied from the existing REI implementation code.
2. The implementer may read this specification, but should not use `Rei_omega_proof/Critical.lean` as source code for the implementation.
3. The submission is frozen in a commit before scoring.
4. The implementer records language, runtime/compiler version, dependency versions and commit SHA.
5. All disagreements are reported. The challenge is not retuned after the submission is frozen.

## Challenge

Run:

```bash
python3 g3/make_challenge.py > challenge.jsonl
```

The generator creates exactly **25,000** JSONL cases:

- 10,000 execution-gate cases
- 10,000 authority-monotonicity cases
- 5,000 upgrade-inheritance cases

The generated input SHA-256 is frozen as:

`fa81bf4e184037dfff6fea7357444cf519d6cd6a7d65d48a5cd90ed6afb9b47e`

## Public specification

### 1. Execution gate

For a `gate` case, execution is allowed exactly when:

```text
authorized
AND constitution_ok
AND recovery_ready
AND NOT human_veto
AND score >= 0
```

The output row is:

```json
{"id":"G00000","execute":false}
```

No score magnitude may override a failed hard gate.

### 2. Authority monotonicity

For an `authority` case:

```text
A(U) = Amax * C * R * exp(-k * U)
```

The challenge guarantees `U2 >= U1` and nonnegative factors. The implementation returns whether:

```text
A(U2) <= A(U1) + 1e-12
```

The output row is:

```json
{"id":"A00000","monotone":true}
```

### 3. Upgrade inheritance

For an `upgrade` case, accept the candidate only if **all** are true:

- constitution exactly preserved
- silent failure rate does not increase
- recovery score does not decrease
- correctability does not decrease
- terminal distance does not decrease
- rollback remains reachable
- authority monotonicity remains valid
- hard-gate nonoverride remains valid

Numeric non-regression comparisons use tolerance `1e-12` where shown in the reference specification.

The output row is:

```json
{"id":"U00000","accepted":false}
```

## Submission interface

Create a directory:

```text
g3/submissions/<team-name>/
```

containing at minimum:

```text
ATTESTATION.md
run.sh
<implementation source files>
```

`run.sh` must accept a path to `challenge.jsonl` as its first argument and write one JSON object per line to stdout, in the same order as the input cases.

Example:

```bash
./g3/submissions/acme/run.sh challenge.jsonl > submission.jsonl
```

## Required attestation

`ATTESTATION.md` must state:

- who authored the implementation;
- that the original REI implementation source was not reused;
- whether any AI/code-generation tools were used;
- implementation language/runtime;
- frozen submission commit SHA.

Using general documentation or the public specification is allowed. Reusing the original implementation code is not.

## Pass rule

After the submission commit is frozen, its output is compared against the sealed reference oracle.

A core G3 pass requires:

- 0 execution-gate mismatches;
- 0 authority mismatches;
- 0 upgrade accept/reject mismatches;
- a completed independence attestation;
- an implementation that is genuinely independently authored.

The frozen oracle SHA-256 commitment is:

`053beaa43f99b0cc41fdd636a98c1393eb89f47a842f29fa27bfc731c76b7d2b`

The oracle itself is intentionally not committed to this public repository before an external submission is frozen.

## Scope boundary

Passing G3 validates replication of this **critical invariant kernel only**. It does not independently validate the full REI architecture, all synthetic experiments, or production reliability.
