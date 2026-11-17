# CampusSign — Pitch Deck Content (12 slides)

Nov 16, 2026 · Group No. 15 · Blockchain Presentation

Built deck: `out/deck.pptx` (PDF: `out/Group15_CampusSign_Blockchain.pdf`, previews in `out/previews/`). Source: `out/source/deck.py` and `out/source/slides_common.py`, theme "Public Record". This file is the words; the built deck is the look.

## Deck at a glance

Twelve slides tell one story: **a signature on paper cannot prove itself. A signature on CampusSign can, because it is locked on a blockchain.** Every slide carries one idea, one picture and one proof point, in plain words a first-year student could repeat.

**Storyline**

1. **Hook** (slides 1 to 3): the paper chase everyone has lived through, its size, and the real problem underneath: nobody can prove a paper approval is genuine.
2. **Fix** (slides 4 to 8): submit once, route by role, sign with your own digital key, lock the result on a blockchain; the blockchain architecture and its USPs; what it is built with; the four locks on every approval.
3. **Proof** (slides 9 and 10): change one character and the proof breaks, live; then every attack and how it is stopped.
4. **Payoff** (slides 11 and 12): paper, carbon and time saved, then a nationwide network of trust.

**How we talk about the blockchain (use these everywhere)**

| Technical idea | Say it like this |
| --- | --- |
| Blockchain | A public notebook that thousands of computers keep copies of. Anyone can read it; nobody can rub anything out. |
| SHA-256 hash | A fingerprint for a file. Change one letter and the fingerprint is completely different. |
| Smart contract | A notary that never sleeps, never forgets and cannot be bribed. |
| Approver wallet / private key | A personal seal only you can press. Your PIN unlocks it. |
| Merkle root | Every signature on a document squeezed into one tiny stamp. |
| On-chain signer check | The blockchain itself tells you who signed. You do not have to trust us. |
| Hash-chained audit log | Every line of history is glued to the one before it. Pull one out and the alarm goes off. |
| Permissioned network | Each college writes only its own records. A council of colleges decides who joins. |

**Design rules (unchanged)**

- Theme "Public Record": white background, ink `#101418`, accent blue `#1D4F91`, green `#1E7A4C` for Verified and every saving, red `#B42318` only for problems and Tampered. Public Sans for words, IBM Plex Mono for hashes.
- Headline = a full-sentence claim, never a topic word.
- Diagrams over bullets; numbers big, labels small; a source line on every slide with a number; "est." on every estimate.
- The green tick returns on slides 4, 7 and 8 so "Verified" sticks.

## Slides

### Slide 1 · Title

- **On slide:** CampusSign · *Campus approvals, locked on a blockchain. Anyone can check them.* · Group No. 15 · VIT Pune · Siddhesh Chaudhari, Devansh Goyanka, Ayush Jadhav, Shishir Chandanshiv, Arya Deshmukh.
- **Say:** "Every one of us has stood outside a cabin waiting for one signature, and at the end we got a piece of paper anyone could fake. CampusSign kills both problems. Every approval is locked on a blockchain: a public record nobody can quietly change, not even us."

### Slide 2 · Problem Statement

- **Headline:** Four cabins, three days, and the result is a paper anyone could fake.
- **On slide:** Riya's three-day journey: faculty coordinator (wrong date, reprint), HoD (away, come tomorrow), Dean Student Affairs (another queue), Security (final stamp). Tally: **4** signatures chased · **3** days · **2** lectures missed · **0** ways to prove it. The paper form she carries, stamped REPRINT.
- **Say:** "Four signatures, three days, two lectures. And the worst part: at the end she holds a paper that anyone with a pen and a photocopier could fake."

### Slide 3 · Scale of the Problem

- **Headline:** Crores of approvals a year, and not one of them can prove it is genuine.
- **On slide:** **4.50 crore** students (AISHE 2023-24) · **~67 crore** paper approvals a year (est.) · **1 in 20** education checks flag a problem, mostly fake certificates (AuthBridge 2025). Who carries the load: students, faculty, an admin office whose files anyone with access can quietly change, students who cannot easily reach every cabin.
- **Close line:** *Slow is bad. Impossible to verify is worse. A signature should prove itself.*

### Slide 4 · Proposed Solution

- **Headline:** Submit once. The right people sign. The blockchain remembers forever.
- **On slide:** five steps: **Request** (fill the form once) → **Route** (by role, not by name) → **Sign** (PIN + your own digital key) → **Seal** (locked on blockchain) → **Verify** (anyone scans the QR). Works for: event permission, on-duty, bonafide, no-dues, any PDF to sign, custom request. Time bar: 2 to 4 days on paper vs same day (target).
- **Say:** "Every tap signs with the approver's own key, like a personal seal nobody else can copy. When the last person signs, the PDF's fingerprint is locked on the blockchain. From then on anyone gets the truth in seconds: Verified, Superseded, Revoked or Tampered."

### Slide 5 · System Architecture

- **Headline:** One app does the paperwork; the blockchain is the judge nobody can bribe.
- **On slide:** students, approvers, admin office and verifiers → one web app (React, installs on a phone) → workflow (Node.js server: who signs, deadlines, escalation, delegation, email) → sign and seal (PIN + approver's own key, PDF with QR, SHA-256 fingerprint) → **Blockchain** (smart contract on Polygon Amoy or a college chain). Data in SQLite with a chained audit log. A gate phone checks the QR with no internet. Connects to a public block explorer and email (AWS SES); next: Aadhaar eSign, DigiLocker, college ERP.
- **Trust line:** *Holds fingerprints, a proof of signers and status. No personal data.*

### Slide 6 · Blockchain Architecture

- **Headline:** One Ethereum smart contract, shared by every college, guarding every approval.
- **On slide (diagram):** College A's CampusSign server (approver wallets, Merkle tree, SHA-256 fingerprint, hash-linked audit log) sends a **seal transaction** to its node. The network is a ring of nodes, colleges A, B and C plus validators, all holding the same **DocumentRegistry** Solidity contract, run by the Ethereum Virtual Machine on every node. Polygon Amoy (Proof of Stake) or a college chain (Proof of Authority). Below: a row of blocks, each pointing to the one before; block #1043 holds the seal transaction. A verifier scans the QR and reads the contract for free, no gas: Verified or Tampered.
- **On slide (USPs, each tagged with its concept):**
  1. **A wallet for every approver** (keys · ECDSA): each approval signed with the person's own key.
  2. **One stamp for all signatures** (Merkle tree): one Merkle root; 2 signers cost the same as 20.
  3. **The contract checks the signer** (EVM): ecrecover + Merkle proof in Solidity, no trust in us.
  4. **A network of colleges** (consortium · PoA): each college writes only its own records.
  5. **History nobody can rewrite** (hash chain): hash-linked audit log, latest line copied on chain.
  6. **Versions and revocation on chain** (contract state): old copy Superseded, cancelled Revoked.
- **Say:** "The contract does not live on one computer: every node keeps a full copy, and the nodes are the colleges themselves. Every transaction lands in a block, and every block points to the one before, so changing anything old breaks everything after it. All six of these are built and tested."

### Slide 7 · Tech Stack

- **Headline:** Open-source from top to bottom; the blockchain layer is the heart of it.
- **On slide (shaded rows = blockchain layer):**

| Layer | Built with | Also works with | What it does |
| --- | --- | --- | --- |
| Web app | React + Vite | Any browser | Student, approver, admin, verify and gate screens |
| Server and workflow | Node.js + Express | | Role routing, deadlines, escalation, delegation |
| Data and files | SQLite | Postgres | Forms, PDFs, hash-chained audit log |
| **Smart contract** | **Solidity** | | Seals, versions, revocations, signer check |
| **Chain connection** | **ethers.js** | | Sends seals, reads proofs, waits for blocks |
| **Blockchain network** | **Polygon Amoy** | College chain | Public test network, or a private one per college |
| **Digital signatures** | **Ed25519 + wallets** | Aadhaar eSign (next) | College key for the QR; one key per approver |
| PDF and email | pdf-lib + QR | AWS SES | Sealed PDF with QR code; email alerts |

- **Close line:** *Every tool is open source and free, so a college is never locked in.*

### Slide 8 · Workflow and Blockchain Proof

- **Headline:** The system knows who must sign; the blockchain remembers that they did.
- **On slide (left):** event permission routed by role: student → faculty coordinator (48 h deadline, then a reminder) → HoD (on leave? goes to the delegate) with Security in parallel → Dean Student Affairs (too slow? auto-escalates) → sealed on the blockchain.
- **On slide (middle), four locks on every approval:** *Your own digital key* (only you can unlock it) · *One stamp for all* (all signatures in one Merkle root) · *The chain checks it* (the contract confirms each signer) · *Tamper alarm* (edit a record and the hash chain breaks). Close: **People sign. The chain remembers.**
- **On slide (right):** the HoD inbox: Robotics fest, 5 Nov; "Your signing key 0x7a3f…c91e. Approve with your PIN; sealed on chain."; Approve / Return.

### Slide 9 · Trust and Verification

- **Headline:** Change one character and the proof breaks.
- **On slide:** Signed PDF → SHA-256 fingerprint → locked on the blockchain (fingerprint, signers' proof, status) → QR code on the PDF. Then the fork: original document, same fingerprint → **Verified**; request no. 0412 edited to 0413, different fingerprint → **Tampered**. Strip: *Smart contract checks every signer itself* · *IT Act 2000 s.5* · *BSA 2023 s.61* · *DPDP Rules 2025: no personal data on chain* · *Same model as India's National Blockchain Framework*.
- **Say:** "Think of a fingerprint for a file. Change one letter and it is completely different. We lock that fingerprint on the blockchain. Here we changed one character, and the proof breaks. And the contract checks each approver's own signature itself, so a recruiter in Bengaluru can trust a NOC from Pune without a single phone call, and without trusting our server."

### Slide 10 · Security

- **Headline:** In a trust product, security is the product: every attack has an answer.
- **On slide (threat → what the attacker tries → how CampusSign stops it → where):**

| Threat | What the attacker tries | How CampusSign stops it | Where |
| --- | --- | --- | --- |
| Forged PDF | Change a date or a name on a real approval | Fingerprint no longer matches the chain: Tampered | Chain |
| Double sealing | Seal two versions as current (double spend) | Contract keeps one Active version; duplicates refused | Chain |
| Fake signer | Sign as the HoD, or reuse an old signature | Own key per approver, bound to request, version, form | Chain |
| Insider edit | Rewrite who approved inside the database | Contract re-checks signers; audit hash chain breaks | Chain |
| Sybil / rogue college | A fake issuer floods the registry | Only approved college addresses can write | Chain |
| Reentrancy | Call back into the contract mid-write | No outside calls and no funds held: nothing to grab | Chain |
| 51% / eclipse | Rewrite history or cut a node off | Many validators: college nodes (PoA) or Polygon (PoS) | Network |
| PIN guessing | Try all 10,000 PINs | Attempts rate limited; every attempt logged | App |
| Privacy leak | Personal data public forever | Only fingerprints, IDs and dates on chain (DPDP) | Chain |

- **Honest limit (on slide):** approver keys sit on our server behind each PIN, so that secret is guarded like the database.
- **Say:** "In a trust product, security is not a feature, it is the product. Every serious attack, from a forged PDF to a 51% attack, has an answer, and most answers live in the smart contract itself, where nobody, including us, can switch them off."

### Slide 11 · Impact and Benefits

- **Headline:** One campus saves lakhs of sheets; India saves tens of thousands of tonnes of CO2e.
- **On slide (per 10,000-student university per year, est.):** 1.5 lakh approvals off paper · ~4.5 lakh sheets · ≥5.7 t CO2e · ~54 trees · ~1.1 lakh student-hours · ~8,000 faculty-hours. All of India: ~67 crore approvals, ~200 crore sheets, ≥25,400 t CO2e, ~2.4 lakh trees. SDGs 4, 9, 12, 13, 15, 16 (16: every decision locked on chain).
- **Say:** "Every tap is a sheet not printed, and every approval is a record that can never be quietly changed."

### Slide 12 · Roadmap and Future Scope

- **Headline:** From one campus chain to a nationwide network of trust.
- **On slide:** **MVP built** (sign, seal, amend, revoke, verify) → gate: admin approves → **Department pilot** → gate: turnaround halved → **University rollout** (Aadhaar eSign and DigiLocker) → gate: 3 partner colleges → **College network** (each college a chain node). Same engine beyond education: government offices, hospitals, banks and NBFCs, corporates, municipal and land, schools and boards. Facts: ₹50 per student a year (est.) · NAAC 6.2.3 counts e-governance · 19.21 lakh government files weeded out in one month (Special Campaign 5.0).
- **Close:** "Picture one trust network where a NOC or internship letter from any college can be checked in two seconds. CampusSign: campus approvals, locked on a blockchain, and anyone can check them."

## Proof points to keep handy

- **The live verify page:** each signer with a short wallet address and "checked on chain", plus the block number.
- **The tamper demo:** upload a PDF with one byte changed and it reads Tampered.
- **The audit alarm:** the admin audit tab says "Audit trail intact"; edit one record in the database and it names the broken entry.
- **Privacy line wherever the blockchain appears:** "fingerprints only, no personal data on chain".
- **Honesty line on estimates:** every number with "est." is our assumption, to be measured in the pilot.

## Rebuild the deck

```
cd out
python source/deck.py <full path>\deck.pptx
powershell -File source/render.ps1 -Pptx <full path>\deck.pptx -OutDir <full path>\previews -Pdf <full path>\Group15_CampusSign_Blockchain.pdf
```

Needs python-pptx, PowerPoint (for the render) and the Public Sans and IBM Plex fonts (`source/getfonts.py`).
