Project name: AuditStrata

Category: Intelligent Contracts

One-line description: Commit–seal–reveal stratified audit sampling.

What it does: A distinct auditor commits random seed material before the owner supplies records. The owner seals an immutable population digest, validators classify records into declared strata, and deterministic hashing draws a reproducible cross-stratum sample.

Why GenLayer: Record classification is semantic; commitment verification, immutability, role authorization, sampling, and closure are deterministic on-chain.

Repository: https://github.com/Leokings/auditstrata

Contract source: `contracts/audit_strata.py`

Source SHA-256: `8e32a15feb7b4c905afe356ff75809731e009e63442db33948555268c38cc4ee`

StudioNet contract: https://explorer-studio.genlayer.com/address/0x88Ec3EC24A1947CE5AE95aC9acd7134AC1343785

Deployment transaction: https://explorer-studio.genlayer.com/tx/0x52a026e830d55d50ad99f0e3390afb8fd93e267549ed2658f5585b5f6505fd4d

Intelligent transaction: https://explorer-studio.genlayer.com/tx/0xffe96c2de69312d083081d8955e86d9f73ca5f28eb1f64095a818df08576dee7

Verification: lint PASS; strict typecheck PASS; 21 direct tests PASS; five-validator integration PASS; complete finalized two-wallet StudioNet flow PASS; latest-final closed readback PASS; deployed-source and schema equality PASS.

Data boundary: Public caller-supplied records only. Wallet separation does not prove real-world auditor independence or record provenance.
