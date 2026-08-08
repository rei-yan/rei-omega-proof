# REI-Ω G3 v3.0 Frozen Commitments

This file freezes the public challenge identity before any qualifying external submission is scored.

## Public challenge

Generator:

`g3/make_challenge.py`

Cases:

- execution gate: 10,000
- authority monotonicity: 10,000
- upgrade inheritance: 5,000
- total: 25,000

Canonical challenge JSONL SHA-256:

```text
fa81bf4e184037dfff6fea7357444cf519d6cd6a7d65d48a5cd90ed6afb9b47e
```

## Sealed oracle

The full oracle is not present in the public repository before an independent submission is frozen.

Canonical oracle JSONL SHA-256 commitment:

```text
053beaa43f99b0cc41fdd636a98c1393eb89f47a842f29fa27bfc731c76b7d2b
```

When the oracle is revealed after a qualifying frozen submission, its canonical JSONL must hash to exactly this value or the scoring event is invalid.

## Canonicalization

Both commitments use UTF-8 JSONL with:

- one JSON object per line;
- keys sorted lexicographically;
- separators `,` and `:` with no extra whitespace;
- a final newline;
- no NaN/Infinity values.

## Integrity rule

If the challenge generator, specification, numeric tolerance, counts, seed, canonicalization, or oracle changes, the version must advance beyond G3 v3.0 and the old commitments remain in history.

No post-submission retuning is allowed under the same challenge version.
