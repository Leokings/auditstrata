# Security

## Controls

- concrete GenVM runner and Python dependencies are pinned;
- owner and auditor must be distinct and the auditor address nonzero;
- seed material and commitments must be exactly 32 bytes of lowercase-normalized hex;
- commitments are single-use;
- collection begins only after commitment and becomes immutable at seal;
- the canonical record digest is bound into the sampling seed;
- sample and stratum sizes, text, keys, and model vectors are bounded;
- model output uses an exact closed schema and rejects booleans or out-of-range labels;
- stratum order and record order are derived deterministically from the seed;
- every selected slot requires auditor acknowledgement before owner close;
- all deployed source bytes and required schema methods are checked against StudioNet.

## Threat boundary

Commit–seal–reveal prevents one non-colluding role from learning both the final population and random seed before committing its choice. It cannot prevent owner–auditor collusion, selective presentation of separate populations, weak off-chain random generation, or withheld actions.

## Public-data warning

All records and acknowledgements are public. The seed preimage becomes public in reveal transaction calldata. Never use a password or reusable secret as the seed, and do not submit confidential audit material.
