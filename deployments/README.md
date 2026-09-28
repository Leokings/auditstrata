# StudioNet deployment evidence

`studionet.json` binds `contracts/audit_strata.py` at SHA-256 `8e32a15feb7b4c905afe356ff75809731e009e63442db33948555268c38cc4ee` to a finalized StudioNet deployment and complete two-wallet commit/collect/seal/draw/acknowledge/close flow. It records latest-final state, required schema methods, quorum checks, byte-for-byte deployed-source equality, and one transparent pre-flow wrong-type probe that finalized as an expected rollback without state mutation. It contains public addresses and transaction hashes only—no wallet secret or unrevealed seed.

Contract explorer: https://explorer-studio.genlayer.com/address/0x64c2c19B9C00313DB2CE853D58aEA698543e811E
