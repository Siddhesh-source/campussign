# The Blockchain in CampusSign: How It Works

> **One line:** Every approval is **signed with the approver's own key**. All the signatures are **folded into one Merkle root**, and the document's **SHA-256 fingerprint** plus that root are written into a **smart contract nobody can edit**. Anyone can check it, **free, in two seconds**.

**Bold** words are the ones to say out loud when presenting. Each concept has four parts: the **simple picture**, **how it works**, **why we did it this way**, and **where it lives in the code**.

---

## Part 1: The whole flow, technically

```
 APPROVE                      SEAL                                   VERIFY
 ───────                      ────                                   ──────
 PIN ok                       all approvals done                     scan QR / upload PDF
   │                            │                                      │
   ▼                            ▼                                      ▼
 leaf = keccak256(            build PDF  ──► SHA-256 = docHash        SHA-256 of the file
  requestId, version,         leaves ──► Merkle root                  │
  role, wallet address,          │                                    ▼
  formHash, signedAt)            ▼                                   contract.get(docHash)
   │                          issuer wallet sends a transaction:       │  Active / Superseded / Revoked / none
   ▼                           seal(docHash, {college, request,        ▼
 sign leaf with the            version, prevHash, approvalsRoot,     for each signer:
 approver's OWN wallet         validFrom, validUntil})                contract.checkApproval(
 (ECDSA secp256k1)               │                                     leaf, signature, Merkle proof)
   │                             ▼                                     │
   ▼                          block mined: txHash, block number,       ▼
 stored: address,             gas recorded                           VERIFIED ✔  or  TAMPERED ✘
 leaf, signature                 │
                                 ▼
                              audit log head written on chain (checkpoint)
```

Step by step:

1. **Approve.** The approver enters their PIN. The server builds the **approval leaf**, a keccak-256 hash of *(request ID, version, role, approver's wallet address, SHA-256 of the form, time)*. It signs that leaf with **that approver's own private key** and stores the address, leaf and signature. (`workflow.ts` → `signApproval` in `wallets.ts`)
2. **Seal.** After the last approval, the server builds the PDF and takes its **SHA-256** (the `docHash`). It turns all approval leaves into a **Merkle tree** and keeps only the **root**. (`seal.ts` → `merkleRoot` in `merkle.ts`)
3. **Anchor.** The college's **issuer wallet** sends one **transaction** calling `seal(docHash, record)` on the `DocumentRegistry` **smart contract**. The contract checks its rules and stores the record. The server saves the **transaction hash, block number and gas used**. (`anchor` in `seal.ts`, `ChainClient.seal` in `chain.ts`)
4. **Checkpoint.** The latest hash of the **audit log** is written on chain, so history can't be quietly changed later. (`checkpointLedger` in `ledger.ts`)
5. **Verify.** Anyone uploads the PDF or scans the QR. The server re-hashes the file and **asks the contract** (a free read) for its status. Then, for every signer, it asks the contract `checkApproval(...)`, and the **contract itself** checks the signature and the Merkle proof. (`verifyHash` in `seal.ts`)

If the chain is down, the seal waits in a **queue with retry** and is anchored later. If the local chain restarts, every seal is **replayed** onto it in order.

---

## Part 2: Every concept, explained

### 1. Blockchain = **the public notebook that can't be erased**
- **How it works:** A shared database copied on many computers (**nodes**). New data is added in **blocks**, and each block contains the **hash of the previous block**. Changing an old block changes its hash, which breaks every later block, so every node would reject it.
- **Why:** Paper and ordinary databases can be edited by whoever controls them. Here **nobody controls the history**, not even us.
- **In our code:** a local **Hardhat** chain (`CHAIN_MODE=local`) or **Polygon Amoy** (`CHAIN_MODE=amoy`). The server talks to it with **ethers.js** over **RPC**.
> Say: "**Write once. Never erase. Anyone can read.**"

### 2. Hash (SHA-256, keccak-256) = **the fingerprint**
- **How it works:** A one-way function that turns any data into a fixed 32-byte code. The same input always gives the same code, and changing **one bit** gives a completely different one. You **can't reverse it** or find two files with the same code.
- **Why:** We put the **fingerprint, not the file**, on chain. That makes it tiny, cheap and **private**, but still proves the exact file. **SHA-256** fingerprints the PDF, the form and the audit log. **keccak-256** is Ethereum's own hash, used for the leaves and the Merkle tree so the contract can compute them too.
- **In our code:** `docHash = sha256Hex(finalPdf)` in `seal.ts`, and `formHash` (the form plus each attachment's SHA-256).
> Say: "**Change one dot, the fingerprint screams.**"

### 3. Wallet = **a personal seal nobody can copy**
- **How it works:** A wallet is a **key pair**. The **private key** is a secret 256-bit number. The **public key** is derived from it on the **secp256k1** curve, and the **address** is the last 20 bytes of the keccak-256 of the public key. Getting from the address back to the key is mathematically infeasible.
- **How we make them:** `privateKey = keccak256(WALLET_SEED + ":" + userId)`. Every user gets a **deterministic** wallet: the same person always has the same address, and we **don't need a key table**.
- **Why custodial:** Teachers shouldn't have to install MetaMask or guard seed phrases. The server holds one secret seed, and the **PIN unlocks the signing**, the way a bank holds your account and your PIN authorises it.
- **Two kinds:** **approver wallets** only *sign* (no money, no transactions, no cost). The **issuer wallet** (one per college) is the only one that *sends* transactions and pays gas.
- **In our code:** `walletFor()` in `wallets.ts`, issuer wallet in `chain.ts`.
> Say: "**Every approver has their own unforgeable seal.**"

### 4. Digital signature (ECDSA) = **the mark the seal leaves**
- **How it works:** Signing = math(private key, message hash) → `(v, r, s)`. Anyone with the signature and the message can run **`ecrecover`** and get back the **address** that signed. If it matches the approver's address, the approval is genuine. Without the private key, a valid signature **can't be produced**.
- **What is signed:** the **approval leaf**, which binds **request + version + role + signer + form fingerprint + time**. Edit the form, reuse the signature on another request, or swap the version, and **ecrecover returns the wrong address**.
- **Why two signature types:** **ECDSA** (wallets) so the **smart contract can check** signatures on chain. **Ed25519** (server key) signs the **QR pass** so a guard's phone can check it **fully offline**.
- **In our code:** `signApproval()` and `approvalLeaf()` in `wallets.ts`, and `leafOf()` in the contract (they must produce the same hash).
> Say: "**A signature that can't be copy-pasted.**"

### 5. Merkle tree and root = **one stamp for all**
- **How it works:** Take all approval leaves. Hash them **in pairs** (each pair sorted first), then hash those results in pairs, and so on until **one hash remains: the root**.
  ```
              ROOT
            /      \
        H(A,B)    H(C,D)
        /   \      /   \
      A     B    C     D      ← approval leaves (Coordinator, HoD, Security, Dean)
  ```
- **Merkle proof:** To prove "**HoD's approval (B) is in this document**", give just **A and H(C,D)**. Hash B with A, then with H(C,D). If you get the ROOT stored on chain, it's proven. That is **2 hashes for 4 signers, about 10 for 1,000**. The other approvals are **not revealed**.
- **Why:** Storing every signature on chain costs gas per signer. One **32-byte root** costs the **same for 2 or 200 signers**, and you can still check each one.
- **Amendments:** v2's tree **reuses the original leaves** of approvers who didn't need to sign again, so it shows who really signed which version.
- **In our code:** `merkleRoot()`, `merkleProof()` in `merkle.ts`, and `inTree()` in the contract (it walks the proof in exactly the same way).
> Say: "**One stamp holds every signature, and each can still be checked.**"

### 6. Smart contract = **the robot notary**
- **How it works:** A program written in **Solidity**, deployed onto the chain at its own address. Its code **can't be changed** after deployment, and **every node runs it** and must agree on the result.
- **What ours (`DocumentRegistry`) stores, per document fingerprint:** college, request ID, type, version, previous version's hash, roles hash, **approvals root**, sealed time, **valid from / until**, and status (**Active / Superseded / Revoked**).
- **Rules it enforces (it rejects the transaction otherwise):**
  | Rule | Error it throws |
  | --- | --- |
  | Only an authorised college can write | `NotIssuer` |
  | Only for its own college | `WrongCollege` |
  | Same document can't be sealed twice | `AlreadySealed` |
  | A request can't get two v1s | `RequestAlreadySealed` |
  | v2 must follow an **Active** v1 of the **same** request | `PrevNotActive`, `PrevOtherRequest`, `BadVersion` |
  | Only Active documents can be revoked | `NotActive` |
- **`checkApproval()`:** a **read-only** function (free, no transaction). It (1) checks the approval belongs to this document, (2) runs `ecrecover` to confirm **who signed**, and (3) walks the Merkle proof to the **stored root**. Only if all three pass does it return true.
- **Why:** Verification **doesn't trust our server's word**. The contract does the checking.
- **Events** (`Sealed`, `Superseded`, `Revoked`, `Checkpointed`) give a public, searchable history.
- **In our code:** `contracts/contracts/DocumentRegistry.sol`, with tests in `contracts/test/registry.test.ts`.
> Say: "**A notary that never sleeps and can't be bribed, not even by us.**"

### 7. Transaction, gas and block = **sending a registered letter**
- **How it works:** Writing (`seal`, `revoke`, `checkpoint`) is a **transaction**: a message signed by the issuer wallet and sent to the network. Validators include it in a **block**. You pay **gas**, a fee for the computation used. Reading (`get`, `checkApproval`) is a **call**: run locally by a node, **free**, no transaction.
- **Why it matters:** Sealing costs gas **once**. **Verifying costs nothing, forever, for anyone.**
- **In our code:** `write()` in `chain.ts` sends one transaction at a time, waits for confirmation, and records `txHash`, `blockNumber` and `gasUsed`. These are shown on the Verify page.
> Say: "**Pay once to seal. Free to verify, forever.**"

### 8. Permissioned network (issuers and governance) = **the guest list**
- **How it works:** The contract has `issuerOf[address] = collegeId`. Only listed addresses can write, and only for their own college (`onlyIssuer` modifier). The **owner** (the deployer) can only call `addIssuer` / `removeIssuer`. It's **governance only, and it can't seal anything itself**.
- **Why:** This is a **consortium** model. Many colleges share **one registry**, each writes under its own identity, and **none can touch another's records**. A removed college's **past records stay valid**.
- **In our code:** on first deploy, `chain.ts` deploys the contract and calls `addIssuer(serverAddress, COLLEGE_ID)` for itself.
> Say: "**One network, many colleges, zero interference.**"

### 9. Hash-chained audit log + on-chain checkpoints = **the tamper alarm**
- **How it works:** Every action (submit, approve, return, seal…) is a row in our database with `hash = SHA-256(previous hash | this entry)`. That is the **same linking as blocks**. After every seal or revoke, the **latest entry number and hash** go on chain via `checkpoint()`. The contract **refuses to go backwards** (`StaleCheckpoint`).
- **Detects:** an **edited** row (its hash no longer matches), a **deleted or inserted** row (the chain breaks), and a **restored older database** (the chain's checkpoint is *ahead* of the database).
- **Why:** The approvals live off chain. This makes **even our own database admin** unable to rewrite them unnoticed, without paying to put every log line on chain.
- **In our code:** `appendLedger()`, `checkLedger()`, `ledgerStatus()` in `ledger.ts`, and `GET /api/admin/ledger`.
> Say: "**Even we can't secretly change history.**"

### 10. Versioning and revocation = **the newer edition**
- **How it works:** An amendment is sealed as **v2 with `prevHash` = v1's fingerprint**. In the **same transaction** the contract marks v1 **Superseded** and records `supersededBy[v1] = v2`. Revoke sets the status to **Revoked** with a reason code.
- **Verify verdict order:** **Revoked → Superseded → Not yet valid → Expired → Verified**. An old copy can **never** show Verified. (`verdictFor` in `packages/shared`)
- **Offline:** the guard's phone keeps a **signed revocation list**, so revoked passes fail even without internet.
> Say: "**Old paper can't fool anyone.**"

### 11. Ethereum vs Polygon = **same language, cheaper road**
- **How it works:** Polygon is **EVM-compatible**. It runs the same virtual machine, the same Solidity contract, the same keys, addresses and signatures. Only the **RPC URL** and the **validators** differ. It's secured by **Proof of Stake** (validators lock up tokens and lose them if they cheat). The local Hardhat chain is one trusted node.
- **Why Polygon:** **about 2-second blocks** and fees of **a fraction of a rupee**, versus Ethereum mainnet's high fees. Switching is **one setting** (`CHAIN_MODE=amoy` plus a funded `AMOY_PRIVATE_KEY`), with **zero code changes**. Each transaction links to **amoy.polygonscan.com**.
> Say: "**Ethereum-grade trust, near-zero cost, one switch.**"

### 12. Validators and consensus = **the notebook's guards**
- **How it works:** Validators agree on which block comes next. To fake history, an attacker would need to control **most of them** (a **51% attack**) or create fake identities (a **Sybil attack**). With **Proof of Stake** that means buying and risking most of the staked money, which is **economically insane**.
- **Our part:** the network handles this. We add **issuer permissions**, so even a valid network participant **can't write CampusSign records** unless they are listed.
> Say: "**Trust the math, not a person.**"

---

## Part 3: On chain vs off chain

| On the chain (public, permanent) | Off the chain (our database, private) |
| --- | --- |
| PDF fingerprint (`docHash`) | The PDF itself |
| **Merkle root** of approvals | Names, emails, roll numbers |
| College ID, request ID, type, version | Form details, comments, attachments |
| Previous version's fingerprint | Approval signatures + wallet addresses (shown on Verify) |
| Valid from / until, status | Audit log (fingerprinted, head checkpointed on chain) |

**Why:** a blockchain is **public and permanent**, so personal data there could **never be deleted**. Fingerprints prove everything and reveal **nothing**.
> Say: "**Proof is public. Data stays private.**"

---

## Part 4: Attacks and what stops them

| Someone tries to... | What stops them (technically) |
| --- | --- |
| Edit one word in the PDF | SHA-256 changes → no record on chain → **Tampered** |
| Forge a teacher's approval | No private key → `ecrecover` gives the wrong address |
| Reuse a real signature elsewhere | The leaf binds request + version + form hash → doesn't match |
| Hide or add a signer | Merkle proof doesn't reach the stored root |
| Seal the same thing twice (**double sealing**) | `AlreadySealed`, `RequestAlreadySealed` |
| Write as a fake college | `NotIssuer`, `WrongCollege` |
| Edit or delete audit history | Hash chain breaks + on-chain checkpoint mismatch |
| Restore an old database | Checkpoint on chain is ahead → reported |
| Show an outdated or cancelled pass | **Superseded / Revoked**, also offline via the signed list |
| **Reentrancy** (classic contract hack) | The contract holds **no money** and calls **no other contract** |
| **51% / Sybil** | Network validators (Proof of Stake / Authority) |

---

## Part 5: The 30-second pitch

> "Paper signatures can be **forged in a minute**. In CampusSign every approver signs with **their own cryptographic wallet**, locked to the **exact form they saw**. All the signatures fold into **one Merkle root**, and with the document's **SHA-256 fingerprint** it's sealed by a **smart contract on the blockchain**, where **nobody, not even us, can change it**. Anyone can upload the PDF or scan the QR, and the **contract itself** checks every signature **in two seconds, for free**. **Pay once to seal. Free to verify. Impossible to fake.**"

---

## Honest limits (if asked)

- **Custodial wallets:** the server holds `WALLET_SEED`, so it must be protected like the database. Next step: approvers holding their own keys (hardware or phone wallets).
- **The live demo runs a local chain** (one validator). Polygon Amoy is **one setting** away.
- A Merkle proof **hides the other approvals** but is not a zero-knowledge proof.
- "Impossible to fake" means it would take **more computing power than exists on Earth**, not magic.

Full reference: `docs/BLOCKCHAIN.md` · Contract: `contracts/contracts/DocumentRegistry.sol` · Server: `apps/api/src/{wallets,merkle,chain,ledger,seal}.ts`
