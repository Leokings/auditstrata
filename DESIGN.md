# Design

## Commit–seal–reveal mechanism

AuditStrata separates control of the population from control of randomness. The auditor commits `sha256("auditstrata/v2|seed|" + secret)` before collection. The owner then supplies records and seals a canonical digest. Reveal is accepted only from the auditor and only when the preimage matches.

The final sampling seed domain-separates the population id, sealed record digest, and secret. Each record receives a deterministic hash inside its validator-assigned stratum. A seed-derived stratum permutation removes fixed low-index priority, and round-robin selection continues until the requested sample size is reached.

## State machine

`AWAITING_SEED_COMMITMENT` → `COLLECTING` → `SEALED` → `DRAWN` → `CLOSED`.

Only the auditor commits, reveals, and acknowledges. Only the owner appends, seals, and closes. Records cannot change after `SEALED`, and a sample cannot close until every selected slot has a nonempty auditor acknowledgement.

## Off-chain responsibilities

Real-world auditor identity, organizational independence, secure preimage storage before reveal, record provenance, private source documents, and actions based on the sample remain off-chain.
