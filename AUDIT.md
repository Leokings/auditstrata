# Security audit

Reviewed: 2026-09-27

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
| Latest-final `CLOSED` readback | PASS |
| Deployed source byte equality | PASS |
| Deployed schema method verification | PASS |
| Secrets in repository | NONE |

StudioNet contract: `0x88Ec3EC24A1947CE5AE95aC9acd7134AC1343785`

Deployment transaction: `0x52a026e830d55d50ad99f0e3390afb8fd93e267549ed2658f5585b5f6505fd4d`

Intelligent transaction: `0xffe96c2de69312d083081d8955e86d9f73ca5f28eb1f64095a818df08576dee7`

Close transaction: `0x34f11fb85f0ee0b43942ced49cf67170e12b5089991084e192c2b867ed11d04a`

Observed state: `{"state":"CLOSED","labels":[0,1],"sample_indexes":[1,0],"commitment_verified":true}`

## Residual trust assumptions

- Owner and auditor collusion can defeat independence; the contract proves wallet separation and action order, not organizational independence.
- The auditor can withhold commitment, reveal, or acknowledgements. No funds are locked, but that population may remain unfinished.
- The seed must be generated with sufficient entropy and protected until reveal. It becomes public in transaction calldata when revealed.
- Validators classify public descriptions; consensus does not authenticate the underlying records.
- StudioNet is a test network.

No known review-blocking source, authorization, state-machine, validation, test, or provenance defect remains. This is a focused engineering audit, not a formal proof or a promise of program acceptance.
