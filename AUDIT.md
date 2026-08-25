# Final audit

Reviewed: 2026-08-25

Scope: `contracts/audit_strata.py` at SHA-256 `28e68bb3e26b175f13e3fb3735b2f755f3110ad535ab5c155599472c22a9cd0b`, its
tests and review documents, and the exact StudioNet deployment recorded in
`deployments/studionet.json`.

## Results

| Gate | Result |
| --- | --- |
| GenVM lint and semantic validation | PASS |
| Strict Pyright typecheck | PASS, zero diagnostics |
| Direct invariant tests | PASS, 4 tests |
| Independent GLSim validators | PASS, exactly 5 validators |
| StudioNet deployment | PASS, FINALIZED |
| Real intelligent write | PASS, AGREE or MAJORITY_AGREE |
| Latest-final state readback | PASS |
| Deployed source byte equality | PASS |
| Deployed schema required-method read | PASS |
| Dependency and GenVM runner pins | PASS |
| Prompt-injection boundary and JSON normalization | PASS |
| External wallet isolation | PASS, 5 unique roles for this repository |
| Cross-repository wallet reuse | NONE across 100 roles |
| Private key or mnemonic in repository | NONE |
| Workspace-wide originality scan | PASS, 161 contract sources scanned |
| GitHub push or remote | NONE |

StudioNet contract: 0x598D31Bd9570b5b5f7Cb9656E112Dd3668aebc1B

Deployment transaction: 0x0917906445fe25263b0662f2c2cab6d123cbeabd7cbbe5fb244ee9c1ed7e3b82

Intelligent transaction: 0x87b090b11d9b7fc1ed8339e74ba21c4c5df0145c72c7d0306ba556fcbe14d17d

Observed live state: `{"sample_indexes":[0,1],"state":"DRAWN","strata":[0,1,0,1]}`

## Consensus review

Validators independently re-execute the bounded semantic task and the custom validator rejects malformed or materially different output.

## Review conclusion

No known source, build, test, consensus, wallet, secret, dependency, provenance,
or repository-hygiene blocker remains. Human program review can still apply its
own policy judgment; this audit does not promise acceptance.
