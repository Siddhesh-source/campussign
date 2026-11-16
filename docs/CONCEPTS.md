# CampusSign: project overview and the concepts behind it

CampusSign replaces signature-chasing paper forms in a university with role-routed digital approvals. A student submits one form; it reaches the right people in the right order; each approver signs with a PIN; the final document is sealed as a PDF with a QR code and its fingerprint is written to a blockchain. Anyone can later check a printed or downloaded copy: **Verified**, **Superseded**, **Revoked** or **Tampered**.

This page explains the ideas the product is built on, in plain words, and points to where each one lives in the code. Deeper detail: `docs/BLOCKCHAIN.md` (chain layer), `docs/TRUST.md` (signing and sealing), `docs/ARCHITECTURE.md` (system layout), `docs/OFFLINE_GATE.md` (gate check without network).

## The flow

```
submit ──► route by role ──► sign (PIN + two signatures) ──► seal (PDF + QR + Merkle root) ──► anchor on chain ──► verify
                                                                                                    │
                                              amend ► v2 supersedes v1 · revoke ► every copy reads Revoked
```

| Step | What happens | Concepts |
| --- | --- | --- |
| Submit | Student fills one form, attaches files | SHA-256 of the form and of each file |
| Route | Each request type has a chain of roles (some in parallel); a role resolves to a person in the student's department | Role-based workflow |
| Sign | Approver confirms with a PIN; the server signs the decision with the college key **and** with the approver's own wallet | Digital signatures, public/private keys, wallets and addresses |
| Seal | PDF with a signed QR is generated; its SHA-256 is the document's identity; the approvals form a Merkle tree | Hash functions, Merkle trees |
| Anchor | The hash, the Merkle root and the metadata go into a smart contract | Smart contracts, transactions, gas, blocks |
| Verify | Re-hash the file and look it up; the contract checks each signer | Immutability, tamper evidence, trustless verification |

## Blockchain and distributed ledgers

**Centralised vs decentralised vs distributed.** The approval data (forms, comments, PDFs) stays in the college's own database: central, private and fast. Only a fingerprint of each final document goes to a shared ledger that no single admin can quietly rewrite. This hybrid is the usual design for real records: personal data off chain, proof on chain.

**Blocks and transactions.** Every seal, revocation and audit checkpoint is a transaction. Each lands in a block; CampusSign stores the transaction hash, the **block number** and the **gas used**, and shows them on the verify page and at `GET /api/chain`.

**Public, private and consortium chains.** Two modes:
- `CHAIN_MODE=local`: a private chain run by the college (Hardhat node).
- `CHAIN_MODE=amoy`: the Polygon Amoy public test network, where anyone can read the records on a block explorer.

The contract itself is built for a **consortium**: several colleges share one registry, each authorised to write only its own records (see Proof of Authority below).

**Generations.** Blockchain 1.0 was money (Bitcoin). 2.0 added smart contracts (Ethereum). 3.0 applied them beyond finance: identity, supply chains, education, government. CampusSign is a 3.0 application: a smart contract as a public notary for university documents.

## Cryptography

**SHA-256 (hash function).** Turns any file into a 64-character fingerprint. Change one byte and the fingerprint changes completely; the same file always gives the same one. Used for the sealed PDF (`docHash`), the form contents (`formHash`), each attachment, and the audit ledger. Code: `packages/shared/src/crypto.ts`.

**Keccak-256.** Ethereum's hash function, used for the Merkle tree and the approval leaves, because the contract computes the same thing on chain.

**Public and private keys.** Each approver has a key pair. The private key signs; the public key (and the address derived from it) lets anyone check the signature. Two kinds are used:

| Key | Algorithm | Signs | Checked by |
| --- | --- | --- | --- |
| College issuer key | Ed25519 | Every decision, the QR pass, the revocation list | Browser and gate phone, fully offline |
| Approver wallet | ECDSA secp256k1 (Ethereum) | That approver's own approvals | The smart contract (`ecrecover`) |

**Wallets and addresses.** Every user gets an Ethereum wallet derived from a secret seed and their user id (`apps/api/src/wallets.ts`). The address (`0x…`, 40 hex characters) is pseudonymous: it identifies a signer on chain without revealing who they are. The PIN unlocks signing; the server holds the keys (a custodial wallet, like an exchange account), so approvers need no browser extension.

**Digital signatures.** What an approver signs names the exact request, version, role, their address, the form's hash and the time. A signature cannot be moved to another request or to an edited form.

**Merkle trees.** At sealing, the approvals of a version are hashed in pairs, level by level, down to a single **root** (`apps/api/src/merkle.ts`). Only the root goes on chain: 32 bytes whether 2 people signed or 20. A **Merkle proof** (the few sibling hashes on the path to the root) shows one approval belongs to the document without exposing the others.

## Ethereum and the smart contract

`contracts/contracts/DocumentRegistry.sol`, compiled with `solc` and run on the **Ethereum Virtual Machine**. The server talks to it through **ethers.js** (`apps/api/src/chain.ts`).

| Solidity feature | Where |
| --- | --- |
| `struct` | `Record` (one sealed document), `Approval` (one signer's approval), `Checkpoint` (audit ledger head) |
| `mapping` | `records`, `supersededBy`, `latestFor`, `revokeReason`, `issuerOf`, `checkpointOf` |
| `enum` | `Status { None, Active, Superseded, Revoked }` |
| `modifier` | `onlyOwner` (governance), `onlyIssuer` (authorised college) |
| `event` | `Sealed`, `Superseded`, `Revoked`, `IssuerAdded`, `IssuerRemoved`, `Checkpointed` |
| custom `error` | `NotIssuer`, `WrongCollege`, `AlreadySealed`, `PrevNotActive`, `StaleCheckpoint`, … |
| `view` / `pure` | `get`, `leafOf`, `inTree`, `checkApproval` (free to call, no gas) |
| `ecrecover` | recovers the signer of an approval inside the contract |
| `immutable`, `constant` | `owner`, `REGISTRY_VERSION` |

**Gas.** Writes cost gas; reads (`view`) do not. Storing a Merkle root instead of every signer keeps the cost flat. Gas per seal is recorded and totalled.

**Versioning on chain.** An amended document (v2) is sealed with the hash of v1 as `prevHash`; the contract marks v1 **Superseded** and links both ways. Only the one Active version may be amended, so two competing v2s are impossible.

**Deployment and upgrades.** A fresh database deploys a fresh contract and registers the server as its college's issuer. If the stored contract is an older version, or the local chain restarted and lost it, the server deploys a new one and re-anchors every stored seal and revocation in order.

**DApp.** The web app is the front end; the contract is the shared back end that anyone can query. The verify page needs no account.

## Consensus

| Mechanism | How it decides the next block | In CampusSign |
| --- | --- | --- |
| Proof of Work | Miners race to solve a hash puzzle | Not used: slow and energy-hungry, not needed for a known set of colleges |
| Proof of Stake | Validators lock up coins and are chosen by stake | Polygon (Amoy mode) |
| Proof of Authority | A known list of approved validators | The local chain; and the same idea at contract level: only authorised college addresses may write |
| PBFT / Byzantine fault tolerance | Agreement holds if fewer than a third of nodes misbehave | The basis of permissioned networks such as Hyperledger Fabric; a natural next step for a multi-college network |

**Byzantine Generals Problem.** Getting many parties to agree when some may lie. CampusSign avoids needing agreement on the documents themselves: each college writes only its own records, and anyone can recompute a hash.

## Permissioned network and governance

The contract keeps a list of authorised issuers (`issuerOf[address] = college`). The **owner** account is governance: it can add or remove colleges and nothing else. An issuer can seal, revoke and checkpoint only for its own college (`WrongCollege` otherwise). Removing an issuer stops new writes but leaves its past records intact. This is the enterprise / consortium model (as in Hyperledger Fabric) expressed in one Ethereum contract.

## Security

| Attack or risk | How it is handled |
| --- | --- |
| Forged or edited PDF | Its SHA-256 no longer matches anything on chain: **Tampered** |
| Old version passed off as current | Contract status **Superseded**, verify points to the latest version |
| Cancelled approval still in someone's hands | **Revoked** on chain and in the signed revocation list the gate phone syncs |
| Double use (two v1s, the same hash twice, two v2s) | `RequestAlreadySealed`, `AlreadySealed`, `PrevNotActive`: the registry's version of preventing double spending |
| Someone edits an approval row in the database | The contract's `checkApproval` fails for that signer: "signature does not match" |
| Someone edits or deletes audit history | Hash-chained audit log breaks; the on-chain checkpoint disagrees (`GET /api/admin/ledger`) |
| A stranger or another college writes records | `NotIssuer`, `WrongCollege` |
| Sybil attack (many fake identities) | Only governance-approved addresses can write; open sign-up accounts cannot |
| 51% attack, eclipse attack | Network-level; left to the validator set (Polygon PoS, or the college's own nodes) |
| Reentrancy | The contract makes no external calls and holds no funds |
| PIN guessing | Rate limited per IP |

**Privacy.** Nothing personal goes on chain: no names, roll numbers, departments, venues or form contents. Only hashes, a Merkle root, ids, dates and pseudonymous addresses. A Merkle proof reveals one approval without the rest; it is not a full zero-knowledge proof, which would also hide that approval's details.

**Offline verification.** The QR carries a compact pass signed with Ed25519. The guard's phone checks the signature and the event date without network, and refuses passes on the latest signed revocation list it synced.

## Applications this demonstrates

- **Education:** tamper-evident permissions, certificates, no-dues and bonafide letters.
- **Digital identity:** each approver has a wallet address that signs on their behalf.
- **E-governance:** an audit trail no single administrator can rewrite unnoticed; a public verify page.
- **Sustainability:** the impact dashboard estimates sheets, CO2e and trees saved. On-chain cost stays small: one transaction per sealed document, no mining (PoA / PoS rather than PoW).

## Stack

TypeScript everywhere · React + Vite + Tailwind (web, installable PWA) · Node + Express + SQLite (API) · Solidity + ethers v6 + Hardhat node (chain) · pdf-lib + qrcode (sealed PDF) · `@noble/ed25519` (offline signatures) · Vitest + Supertest (tests).
