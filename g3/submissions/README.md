# G3 External Submission Template

Create one directory per independent team:

```text
g3/submissions/<team-name>/
```

Minimum files:

```text
ATTESTATION.md
run.sh
<source files>
```

## ATTESTATION.md template

```markdown
# REI-Ω G3 Independence Attestation

Team / author:
GitHub handle(s):
Date:
Frozen submission commit SHA:

Implementation language:
Runtime / compiler version:
Dependencies and versions:

Original REI executable implementation source reused: NO
Inspected sealed oracle before freezing submission: NO
Inspected `Rei_omega_proof/Critical.lean` before implementation: YES / NO
AI or code-generation tools used: YES / NO
If YES, list tools and what they were used for:

I confirm that the submitted implementation was independently authored from the public G3 specification and that its output was frozen before oracle reveal.

Signed:
```

## run.sh contract

Your script must accept one argument, the frozen challenge JSONL path, and write exactly one JSON object per input line to stdout.

```bash
./g3/submissions/<team-name>/run.sh challenge.jsonl > submission.jsonl
```

Do not write logging text to stdout. Send diagnostics to stderr.

Before freezing your commit, validate only the shape/order of your output:

```bash
python3 g3/validate_submission_shape.py challenge.jsonl submission.jsonl
```

This public validator does **not** know the answers and cannot tell you whether your implementation is correct.
