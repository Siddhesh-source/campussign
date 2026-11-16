-- Blockchain layer v2 (docs/BLOCKCHAIN.md).
-- Each approval is also signed with the approver's own wallet; the signed hash is a Merkle leaf.
ALTER TABLE approvals ADD COLUMN wallet_address TEXT;
ALTER TABLE approvals ADD COLUMN wallet_sig TEXT;
ALTER TABLE approvals ADD COLUMN leaf TEXT;
ALTER TABLE approvals ADD COLUMN signed_form_hash TEXT;

-- Merkle root of a version's approval leaves (on chain), plus where the seal landed.
ALTER TABLE seals ADD COLUMN approvals_root TEXT;
ALTER TABLE seals ADD COLUMN block_number INTEGER;
ALTER TABLE seals ADD COLUMN gas_used INTEGER;

-- Audit ledger: every entry carries the hash of the one before it.
ALTER TABLE audit_log ADD COLUMN prev_hash TEXT;
ALTER TABLE audit_log ADD COLUMN hash TEXT;
