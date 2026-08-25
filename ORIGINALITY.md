# Originality audit

The final source was compared against 161 GenLayer
contract sources in the workspace. All twenty new target contracts were excluded
from the pre-existing comparison pool.

Nearest pre-existing source: `parkrightnow\contracts\curb_window_compiler.py`

Combined structural score: `0.195225`

Token score: `0.316905`

AST score: `0.105064`

Nearest contract in this new set: `sequencecompressor\contracts\sequence_compressor.py` with combined
score `0.3513`. That score reflects shared safe GenLayer
boilerplate. The mechanisms differ materially:

- This repository: Consensus assigns records to a closed stratum set; seeded hashing and round-robin selection create a reproducible cross-stratum sample.
- Other repository: Consensus labels every ordered entry from a closed alphabet; deterministic run-length encoding creates assignable contiguous work segments.

The two do not share the same semantic input, deterministic algorithm, storage
record, state lifecycle, or decision views. Exact source SHA-256 values are also
unique across all twenty repositories. The complete machine-readable reports are
`review-tools/twenty-originality-audit.json` and
`review-tools/twenty-pairwise-audit.json` at the workspace level.

Similarity scoring is a review aid, not a guarantee of a human review outcome.
