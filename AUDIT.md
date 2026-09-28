# Security audit

Reviewed: 2026-09-28

Scope: `contracts/audit_strata.py` at SHA-256 `8e32a15feb7b4c905afe356ff75809731e009e63442db33948555268c38cc4ee`, direct and integration tests, review documents, and the exact StudioNet deployment in `deployments/studionet.json`.

## Findings resolved

| Severity | Finding | Resolution |
| --- | --- | --- |
| High | The population owner previously knew and controlled the sampling seed while choosing record keys and contents. | A distinct auditor must commit a seed hash before record collection; the owner then seals a canonical record digest before reveal. |
| Medium | Small samples favored low-numbered strata because round-robin traversal always began at index zero. | Stratum traversal order is now derived from the committed seed and sealed population. |
| Medium | Record mutation needed a cryptographic boundary before reveal. | `seal_population` stores a canonical SHA-256 digest and closes collection. |
| Medium | Seed reuse could make related draws easier to correlate or precompute. | Commitments are globally single-use within the deployment. |
| Low | Stratum labels needed the same prompt-injection boundary as records. | Both blocks are explicitly delimited and treated as untrusted data. |
| Coverage | Original tests did not exercise commitment authorization, preimage mismatch, post-seal immutability, biased order, or full close. | Direct coverage increased from 4 to 21 tests and the five-validator flow was rerun. |

## Verification results

| Gate | Result |
| --- | --- |
| GenVM lint and semantic validation | PASS |
| Strict typecheck | PASS, zero diagnostics |
| Direct invariant and negative-path tests | PASS, 21 tests |
| Independent local validators | PASS, exactly 5 validators |
| StudioNet owner and distinct auditor flow | PASS |
| Every StudioNet transaction finalized with successful agreeing-validator execution | PASS |
| Minimum agreeing StudioNet votes | PASS, 3 of 5; some receipts were 5 of 5 |
| Latest-final `CLOSED` readback | PASS |
| Deployed source byte equality | PASS |
| Deployed schema method verification | PASS |
| Secrets in repository | NONE |

StudioNet contract: `0x64c2c19B9C00313DB2CE853D58aEA698543e811E`

Deployment transaction: `0x6802df3cb0f44a516d835a5d6e8a6fd5d67c864547b6f91b7815e142bc4b0144`

Intelligent transaction: `0xa3ce39b43e653336b84f9b50e772e71377ac8fdc03b39f8c837fb0ca4e8f2f8b`

Close transaction: `0x2dbeaab53d20e083ea59db13e9d6951bfc5fdf9f0625c2298424453e68084204`

Observed state: `{"schema":"auditstrata/population/v2","state":"CLOSED","record_count":4,"labels":[0,0,1,1],"sample_indexes":[3,1],"acknowledgements_complete":true}`

## Residual trust assumptions

- Owner and auditor collusion can defeat independence; the contract proves wallet separation and action order, not organizational independence.
- The auditor can withhold commitment, reveal, or acknowledgements. No funds are locked, but that population may remain unfinished.
- The seed must be generated with sufficient entropy and protected until reveal. It becomes public in transaction calldata when revealed.
- Validators classify public descriptions; consensus does not authenticate the underlying records.
- StudioNet is a test network.

No known review-blocking source, authorization, state-machine, validation, test, or provenance defect remains. This is a focused engineering audit, not a formal proof or a promise of program acceptance.
