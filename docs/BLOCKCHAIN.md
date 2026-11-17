# Blockchain layer

What the chain does in CampusSign, what was added to it and why. The approval workflow itself (submit → route by role → sign → seal → verify) is unchanged: everything here happens underneath the same steps.

Code: `contracts/contracts/DocumentRegistry.sol`, `apps/api/src/chain.ts`, `apps/api/src/merkle.ts`, `apps/api/src/wallets.ts`, `apps/api/src/ledger.ts`, `apps/api/src/seal.ts`.

## Where it stood

| Had | Gap |
| --- | --- |
| SHA-256 of the sealed PDF anchored in a Solidity contract | The chain knew *that* a document was sealed, not *who* approved it; `rolesHash` is one opaque hash nobody can check a single approval against |
| Approvals signed with one server key (Ed25519) | Approvers had no key pair, wallet or address of their own |
| One owner address could write | No notion of several authorised colleges (a permissioned network) or of governance |
| Audit log in a plain table | A database admin could edit history and nobody would know |
| Transaction hash stored | Block number and gas never recorded or shown |

## What was added (five steps)

### 1. A wallet for every approver (key pairs, addresses, digital signatures)

- Every user gets an Ethereum wallet: a private key, a public key and an address. The key is derived from one secret seed plus the user id (`WALLET_SEED`, or generated once and kept in the database), so no key table is needed and the same person always gets the same address.
- When an approver confirms with their PIN, the server signs the approval with **that approver's** private key (ECDSA, secp256k1, the scheme Ethereum uses). The PIN is what unlocks the key: these are custodial wallets, the same model as an exchange account.
- What is signed is the **approval leaf**: `keccak256(requestId, version, role, signer address, formHash, signedAt)`. It names the exact form contents, so a signature cannot be replayed on another request, another version or an edited form.
- The existing Ed25519 signature is kept (the offline QR depends on it).

### 2. A Merkle tree of approvals, root on chain

- At sealing, the approval leaves of that version become the leaves of a Merkle tree (pairs are sorted then hashed with keccak-256; an odd leaf moves up unchanged).
- Only the 32-byte **root** goes on chain, in the document's record (`approvalsRoot`). Cost on chain is the same for 2 signers or 20.
- A **Merkle proof** (a few sibling hashes) shows that one approval is in the tree without revealing the others.
- An amended version carries the unchanged approvers' original leaves forward, so v2's tree shows who really signed v1 and who signed v2.

### 3. The contract checks an approval itself

`checkApproval(docHash, approval, v, r, s, proof)` is a read-only function that answers yes only when all of these hold:

1. the document is sealed and the approval belongs to its request,
2. `ecrecover` on the signature returns the signer address written in the approval (the signer really held that key),
3. the approval's leaf, walked up the proof, gives the root stored on chain.

The verify page calls it for every signer and shows the wallet address with "checked on chain". Nobody has to trust the server's word for who approved.

### 4. A permissioned network of colleges (Proof of Authority, governance)

- The contract keeps a list of **authorised issuers**: `issuerOf[address] = college id`. Only a listed address may seal, revoke or checkpoint, and only for its own college (`NotIssuer`, `WrongCollege`).
- The **owner** is the governance account: it can only add or remove issuers (`addIssuer`, `removeIssuer`). It cannot seal by itself.
- This is the consortium model: several colleges share one registry, each writes under its own identity, none can touch another's records. It matches how the chain itself is run: the local chain and Polygon are validated by known validators, not by mining.
- On first deploy the server registers its own address as the issuer for `COLLEGE_ID`.

### 5. A hash-chained audit ledger with on-chain checkpoints

- Every audit entry stores the hash of the entry before it: `hash = SHA-256(prevHash + entry)`. Changing or deleting any old entry breaks every hash after it. This is the same linking that joins blocks in a blockchain.
- After each seal or revocation is anchored, the server writes a **checkpoint** on chain: the latest entry number and its hash. The contract refuses a checkpoint that goes backwards (`StaleCheckpoint`).
- `GET /api/admin/ledger` recomputes the whole chain and compares it with the checkpoint. It reports the first broken entry, or that the database is behind the chain (a rollback).
- Old entries are linked once, on the first write after the upgrade.

### Also recorded

- **Block number and gas used** for every seal (`seals.block_number`, `seals.gas_used`), shown on the verify page and in `GET /api/chain`.
- `GET /api/chain` (public): network, chain id, block height, contract address and version, issuer address and college, consensus type, number of anchored documents, total gas, latest ledger checkpoint.

## Contract summary (`DocumentRegistry`, version 2)

| Kind | Items |
| --- | --- |
| Structs | `Record` (now with `approvalsRoot`), `Approval`, `Checkpoint` |
| Mappings | `records`, `supersededBy`, `latestFor`, `revokeReason`, `issuerOf`, `checkpointOf` |
| Modifiers | `onlyOwner` (governance), `onlyIssuer` (authorised college) |
| Writes | `addIssuer`, `removeIssuer`, `seal`, `revoke`, `checkpoint` |
| Reads | `get`, `leafOf`, `inTree`, `checkApproval`, `REGISTRY_VERSION` |
| Events | `IssuerAdded`, `IssuerRemoved`, `Sealed`, `Superseded`, `Revoked`, `Checkpointed` |
| Errors | `NotOwner`, `NotIssuer`, `WrongCollege`, `EmptyHash`, `AlreadySealed`, `RequestAlreadySealed`, `PrevNotActive`, `PrevOtherRequest`, `BadVersion`, `NotActive`, `StaleCheckpoint` |

## Upgrading an existing installation

The server checks `REGISTRY_VERSION` on the stored contract address. An older contract is replaced: a new one is deployed, the server registers itself as issuer, and every stored seal and revocation is anchored again in order (the existing replay path). Approvals signed before the upgrade have no wallet signature, so their documents get an empty approvals root and verify exactly as before, without the per-signer check.

## Security notes

| Threat | Answer |
| --- | --- |
| Same document sealed twice / two v1s for one request (the registry's "double spend") | `AlreadySealed`, `RequestAlreadySealed`; an amendment must link to the one Active version |
| Replaying an approval signature elsewhere | The leaf binds request, version, role, signer and form hash |
| A stranger or another college writing records | `onlyIssuer` + college match |
| Editing the audit log in the database | Hash chain breaks; on-chain checkpoint disagrees |
| Restoring an old database to hide history | Chain checkpoint is ahead of the ledger; reported |
| Reentrancy | The contract makes no external calls and holds no funds |
| Personal data on a public ledger | Still none: hashes, roots, ids and pseudonymous addresses only |
| 51% / Sybil attacks | Out of the app's hands: handled by the network's validator set (Proof of Authority locally, Proof of Stake on Polygon) |

Limits, stated plainly: wallets are custodial (the server holds the seed, so `WALLET_SEED` must be protected like the database); a Merkle proof hides the other approvals but is not a zero-knowledge proof; the local chain has one validator.

## Tests

- `contracts/test/registry.test.ts`: issuers and governance, college isolation, approvals root, `checkApproval` (good proof, wrong signer, wrong proof, other request), checkpoints.
- `apps/api/test/blockchain.test.ts`: Merkle root/proof helpers, wallet addresses, full flow with per-signer on-chain check, carried approvals after an amendment, ledger tamper detection, checkpoint match, old-contract upgrade, `GET /api/chain`.
