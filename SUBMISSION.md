Project name: AuditStrata

Category: Intelligent Contracts

One-line description: Commit–seal–reveal stratified audit sampling.

What it does: A distinct auditor commits random seed material before the owner supplies records. The owner seals an immutable population digest, validators classify records into declared strata, and deterministic hashing draws a reproducible cross-stratum sample.

Why GenLayer: Record classification is semantic; commitment verification, immutability, role authorization, sampling, and closure are deterministic on-chain.

Repository: https://github.com/Leokings/auditstrata (currently private; grant reviewer access or make it public before submission).

Contract source: `contracts/audit_strata.py`

Source SHA-256: `8e32a15feb7b4c905afe356ff75809731e009e63442db33948555268c38cc4ee`

StudioNet contract: https://explorer-studio.genlayer.com/address/0x64c2c19B9C00313DB2CE853D58aEA698543e811E

Deployment transaction: https://explorer-studio.genlayer.com/tx/0x6802df3cb0f44a516d835a5d6e8a6fd5d67c864547b6f91b7815e142bc4b0144

Intelligent transaction: https://explorer-studio.genlayer.com/tx/0xa3ce39b43e653336b84f9b50e772e71377ac8fdc03b39f8c837fb0ca4e8f2f8b

Final close transaction: https://explorer-studio.genlayer.com/tx/0x2dbeaab53d20e083ea59db13e9d6951bfc5fdf9f0625c2298424453e68084204

Verification: lint PASS; strict typecheck PASS; 21 direct tests PASS; five-validator integration PASS; complete finalized two-wallet StudioNet flow PASS; latest-final closed readback PASS; deployed-source and schema equality PASS.

Data boundary: Public caller-supplied records only. Wallet separation does not prove real-world auditor independence or record provenance.
