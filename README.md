# AuditStrata

AuditStrata is a reusable GenLayer Intelligent Contract for commit–seal–reveal audit sampling. A distinct auditor commits to a random seed before the owner supplies records, the owner seals an immutable record digest, validators classify records into a closed stratum set, and deterministic hashing draws a reproducible cross-stratum sample.

## How it works

1. `open_population` records bounded strata, sample size, owner, and a distinct nonzero auditor.
2. The auditor calls `commit_seed` with a SHA-256 commitment before record collection opens. Commitments cannot be reused.
3. The owner appends up to 30 public records and calls `seal_population`, which stores a canonical record digest and prevents later mutation.
4. The auditor calls `draw_sample` with the 32-byte seed preimage. The contract verifies the commitment, validators assign one stratum per record, and deterministic hashing selects the sample using both the sealed record digest and seed.
5. The auditor acknowledges every selected slot; only then can the owner call `close_population`.

## Public interface

Write methods: `open_population`, `commit_seed`, `append_record`, `seal_population`, `draw_sample`, `acknowledge_sample`, `close_population`

View methods: `get_population`, `sampled_record`, `sample_is_closed`

## Verification

```text
pip install -r requirements.txt
genvm-lint check contracts/audit_strata.py
genvm-lint typecheck contracts/audit_strata.py --strict
pytest tests/direct -q
python tests/run_glsim.py --port 4000 --validators 5
pytest tests/integration/test_audit_strata_consensus.py -q
```

Verified results on 2026-09-27: lint PASS, strict typecheck PASS, 21 direct tests PASS, one five-validator integration flow PASS, and a complete two-wallet StudioNet flow PASS.

StudioNet contract: https://explorer-studio.genlayer.com/address/0x88Ec3EC24A1947CE5AE95aC9acd7134AC1343785

The finalized live flow committed a random seed, sealed two records, drew both strata, acknowledged both slots, and reached `CLOSED`. See `deployments/studionet.json` for every transaction and the exact source proof.

## Boundary

All records, commitments, the revealed seed transaction, acknowledgements, calldata, and results are public. The preimage must remain private only until reveal. Validator classification does not authenticate record provenance. The contract moves no funds.
