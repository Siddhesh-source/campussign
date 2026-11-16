# CampusSign — Project Overview

Nov 16, 2026 · Group No. 15 · Blockchain Presentation (VIT Pune): Siddhesh Chaudhari, Devansh Goyanka, Ayush Jadhav, Shishir Chandanshiv, Arya Deshmukh

**One line:** CampusSign turns every signature-chasing paper form in an Indian university into a digital approval that is signed with the approver's own key and locked on a blockchain, so anyone, anywhere, can check it in seconds.

**Tagline:** *No queues. No paper. No forged signatures.*

**Elevator pitch (30 seconds):** A student needs a faculty or HoD signature on about 15 paper forms a year. Each one means queues, reprints and lost days, and at the end the student holds a paper that anyone with a pen could fake. CampusSign fixes both. The student submits once; the system sends it to the right people by their role; each approver signs with a PIN that unlocks their own digital key. The final document's fingerprint is locked on a blockchain: a public notebook nobody can rub out, not even us. A recruiter, a scholarship office or another college scans the QR and knows in two seconds whether the document is genuine, who signed it, and whether it was later changed or cancelled.

**The big idea in one sentence:** a paper signature asks you to trust it; a CampusSign signature proves itself.

## 1. Problem statement

Indian universities still run approvals on wet-ink signatures. AISHE 2023-24, released in July 2026, counts [4.50 crore enrolled students and 17.32 lakh teachers](https://www.civilsdaily.com/news/aishe-2023-24-indias-higher-education-enrolment-reaches-4-5-crore/) across [1,289 universities and 48,246 colleges](https://www.freepressjournal.in/analysis/the-aishe-report-institutional-network-of-higher-education).

**Two problems, not one:**

1. **It is slow.** A form is printed, carried from cabin to cabin, rejected for a typo, reprinted and carried again.
2. **It cannot prove itself.** Once signed, a paper approval is just ink. Nobody outside the campus can tell a genuine NOC from a fake one without phoning the college, and nobody inside can prove an old record was not quietly changed.

| Common paper form | Typical signers | What goes wrong today |
| --- | --- | --- |
| Event / club permission | Faculty coordinator, HoD, Dean Student Affairs, Security | 3 to 4 cabins in a row; one absent signer stalls the event |
| On-duty (OD) / leave application | Mentor, class teacher, HoD | Attendance lost while the slip waits |
| Bonafide / character certificate | Class teacher, HoD, Registrar office | Repeat visits; scholarship and visa deadlines missed |
| Internship / industrial-visit NOC | Guide, T&P officer, HoD | Offer letters expire while waiting |
| No-dues clearance | Library, labs, hostel, accounts, HoD | 6 to 10 signatures on one sheet |
| Letter of recommendation | Faculty, HoD | No tracking; easy to fake |
| Hostel gate pass / late entry | Warden | Manual registers, easy to forge |

**The trust gap, in numbers:** AuthBridge's 2025 background-verification report found [5% of education checks flagged discrepancies](https://cxotoday.com/press-release/authbridge-exposes-indias-hiring-red-flags/), mostly fake certificates and degrees from blacklisted institutions. One in twenty.

**Size of the waste (estimate to validate):** 4.5 crore students × \~15 forms a year ≈ **67 crore paper approvals a year**, about 200 crore sheets at 3 sheets each. Both multipliers are our assumptions; a student survey turns them into evidence.

**Why now:** India already trusts blockchains for records: the National Blockchain Framework has [verified 34 crore documents as of October 2025](https://www.shankariasparliament.com/current-affairs/mains-analysis/national-blockchain-framework-strengthening-governance-through-blockchain-technology), including CBSE certificates. What is missing is the everyday approval inside the campus, between a student and a professor.

## 2. Solution overview

CampusSign is an approval app with a blockchain at its heart. The student submits once, the system knows who must sign and in what order, and every finished approval is locked on a blockchain so it can never be forged or quietly changed.

**How it works:** fill the form → routed by role → each approver signs with PIN + their own digital key → PDF built with a QR code → its fingerprint locked on the blockchain → anyone scans and checks.

### The blockchain, in plain words

| What we do | What it means for you | The technical name |
| --- | --- | --- |
| Take a fingerprint of the final PDF | Change one letter and the fingerprint is completely different | SHA-256 hash |
| Write that fingerprint to a public notebook copied on many computers | Nobody can rub it out, not even us | Blockchain, transaction, block |
| Let a program on the blockchain hold the rules | A notary that never sleeps, never forgets and cannot be bribed | Smart contract (Solidity) |
| Give every approver their own key, unlocked by their PIN | A personal seal only they can press | Wallet, private and public key, digital signature |
| Squeeze all signatures on a document into one tiny stamp | 2 signers or 20, it costs the same | Merkle tree and Merkle root |
| Let the blockchain check one signer by itself | You do not have to trust our server about who signed | On-chain signature recovery + Merkle proof |
| Glue every line of history to the line before it, and copy the newest line to the blockchain | Pull out or edit one line and the alarm goes off | Hash-chained audit log with on-chain checkpoints |
| Let each college write only its own records; a council decides who joins | One shared network, no college can touch another's records | Permissioned network, Proof of Authority, governance |
| Link a changed approval to the one it replaces | The old copy says "Superseded", never "Verified" | Version chain on the blockchain |
| Mark a cancelled approval on the blockchain | Every copy, everywhere, now says "Revoked" | On-chain revocation |

### Core features (all built)

1. **Request catalogue.** Event permission, on-duty, bonafide, no-dues, a custom request the student writes, and **any PDF to sign** with signature boxes placed on the pages.
2. **Role-based routing.** Each request type has a chain of roles, not names, so when a HoD changes, nothing breaks. Steps can run one after another or side by side (no-dues goes to library, labs, hostel and accounts at once).
3. **Signing.** Approve, Return or Reject, confirmed with a 4-digit PIN. Approve signs twice: once with the college key and once with the approver's own wallet key.
4. **Blockchain seal.** The final PDF gets a QR code; its fingerprint, a Merkle root of the signatures, the version and the validity window go on the blockchain. **No names, roll numbers or form contents ever go on chain.**
5. **Verify for anyone.** Scan the QR or upload the file: **Verified**, **Superseded** (a newer version exists), **Revoked** (cancelled), or **Tampered** (one byte changed). Each signer shows a short wallet address and "checked on chain".
6. **The plan changed.** Amend a sealed approval: only the people affected by the change sign again; the new version is linked to the old one on the blockchain, which marks the old one Superseded. HoD or Dean can revoke entirely.
7. **Offline gate check.** The security guard's phone checks the QR with no internet at all, using the college's signature on the QR and a signed list of cancelled passes.
8. **Tracking, deadlines, delegation.** Students see where a request is and since when; a 48-hour deadline sends a reminder, then escalates; a faculty member on leave hands work to a delegate.
9. **Admin.** All requests, impact (sheets, CO2e, trees saved), the audit log with an "intact / altered" alarm, and the email log.

**The network effect:** every college that joins writes to the same registry under its own name. A NOC from Pune can be checked by a company in Bengaluru, a scholarship office in Delhi or another college, in two seconds, with no phone call. Each new college makes every other college's documents more useful.

## 3. Users and the before-vs-after journey

| User | Their pain today | What CampusSign gives them |
| --- | --- | --- |
| Student (Riya, 2nd-year CSE) | 3 days chasing 4 signatures; a paper nobody can check | Submits in 2 minutes, tracks live, gets a PDF that proves itself |
| Faculty / HoD (Prof. Kulkarni) | Interrupted 10+ times a day to sign slips | Approves from the phone, several at once, with one PIN |
| Admin / Registrar office | Files anyone with access can change; no proof for audits | A tamper-alarmed audit log; every approval anchored on chain |
| External verifier (company, scholarship body, other college) | Calls or emails the college to confirm a letter | Scans the QR and sees the blockchain answer in seconds |
| Security guard | Cannot tell a real pass from a photocopy | Scans the QR on a phone, even with no network |

**Riya's event permission, before and after**

| Step | Before (paper) | After (CampusSign) |
| --- | --- | --- |
| Prepare | Type, print, reprint after a typo | Fill one form on the phone |
| Faculty coordinator | Wait outside the cabin | Notified, approves with PIN |
| HoD and Security | Absent today, come back tomorrow | In parallel; a delegate covers leave |
| Dean Student Affairs | Another queue, another day | Approves on the phone |
| Proof | A photocopy in a file | A PDF whose fingerprint is locked on the blockchain |
| Event moved two days later | Start again from scratch | Amend: only the affected signers re-approve; old copy reads Superseded |
| Elapsed time | 2 to 4 days (typical, to validate) | Same day (target) |

## 4. System architecture

One app does the paperwork; the blockchain is the judge.

```
Students · Approvers · Admin · Verifiers · Gate phone
                    │
        Web app (React, installs on a phone, works offline at the gate)
                    │
        Server (Node.js): routing, deadlines, delegation, email
           │                         │
   Data (SQLite):            Sign and seal: PIN + approver key,
   forms, PDFs,              PDF with QR, SHA-256 fingerprint,
   chained audit log         Merkle root of the signatures
                                     │
                     Smart contract (Solidity) on the blockchain:
                     fingerprints · signer proof · versions · revocations · audit checkpoints
```

**Request lifecycle:** Submitted → In review (step 1…n) → Approved, Returned for changes, or Rejected → Signing → **Sealed on chain** → (Amended → Superseded) or (Revoked).

**What goes on chain and what stays off chain**

| On the blockchain (public, permanent) | Off the blockchain (private) |
| --- | --- |
| SHA-256 fingerprint of the final PDF | The PDF itself and attachments |
| Request ID, type and version | Student name, roll number, department |
| Fingerprint of the version it replaces | Form contents and comments |
| Merkle root of the signatures (each made by the approver's own key) | Which person holds which key |
| Validity dates and status (Active, Superseded, Revoked) | Emails and contact details |
| Issuing college ID | The audit log itself (only its latest fingerprint is on chain) |

Nothing personal touches the chain, which keeps us aligned with India's data protection law and keeps the cost to one small transaction per document.

**The college network:** the smart contract already works as a network of colleges. Each college writes from its own approved address and only for its own records; a governance account admits or removes colleges and can do nothing else. The chain runs either as a private college chain (Proof of Authority: known validators) or on Polygon's public test network (Proof of Stake). This mirrors the model India's National Blockchain Framework uses for government certificates.

## 5. Tech stack

Everything is open source. One language (TypeScript) from the phone screen to the server.

| Layer | Built with | Why |
| --- | --- | --- |
| Web app | React + Vite + Tailwind, installable (PWA) | Works on any phone or laptop browser; the gate screen works offline |
| Server and workflow | Node.js + Express | Routing by role, deadlines, escalation, delegation, batch approve |
| Data and files | SQLite (Postgres-ready schema) | Zero setup; forms, PDFs and the hash-chained audit log |
| **Smart contract** | **Solidity (`DocumentRegistry`)** | Seals, version links, revocations, college permissions, signer check, audit checkpoints |
| **Chain connection** | **ethers.js v6** | Sends transactions, waits for blocks, reads proofs |
| **Blockchain network** | **Hardhat local chain, or Polygon Amoy** | A private chain for a college, or a public test network anyone can inspect |
| **Signatures** | **Ed25519 (college key) + Ethereum wallets (ECDSA, one per approver)** | The college key signs the QR for offline checks; approver keys are checked by the contract |
| PDF and QR | pdf-lib + qrcode | Sealed PDF with a QR; signatures stamped into the student's own PDF |
| Email | AWS SES (or a log) | Approval requests, reminders, results |
| Hosting | AWS EC2 (free tier) with HTTPS | One small server runs the app and the local chain |
| Tests | Vitest + Supertest | 123 server tests and 11 smart-contract tests, all automated |

**Next integrations:** Aadhaar eSign for legally heavy documents, DigiLocker to push final certificates into the student's locker, and a bridge to Samarth or any college ERP.

## 6. Method: how we built it

We built the whole loop first, thin, then made each part deeper, with automated tests after every step.

1. **Core loop:** submit → route by role → sign → seal → verify, working end to end.
2. **Blockchain seal:** the PDF's fingerprint written to our own smart contract, with a queue that retries if the chain is down, and a full replay if a chain is reset.
3. **The plan changed:** amend with selective re-approval, versions linked on chain, revocation, and the offline gate check.
4. **Operations:** attachments, no-dues in parallel, deadlines and escalation, delegation, batch approve, impact dashboard, audit log, email.
5. **Sign in place:** any PDF, signature boxes on the pages, the real signature stamped in.
6. **Blockchain layer v2:** a key per approver, a Merkle root of the signatures, the contract checking each signer, a permissioned college network, and the tamper-alarmed audit log.

**Next:** one department for one semester with a paper fallback, measuring turnaround, reprints avoided and sheets saved against a baseline.

## 7. Impact and benefits

For one 10,000-student university we estimate 1.5 lakh approvals a year moved off paper, about 4.5 lakh sheets saved and over 1 lakh student-hours given back. Every multiplier is an assumption the pilot will measure.

| Metric (per 10,000-student university, per year) | Assumption | Estimate |
| --- | --- | --- |
| Paper approvals digitised | 15 forms per student | 1,50,000 approvals |
| Paper saved | 3 sheets per approval | \~4,50,000 sheets (\~900 reams) |
| Student time returned | \~45 min chasing per form | \~1,12,000 student-hours |
| Faculty time returned | \~2 min per paper sign vs \~20 sec digital, \~2 signers per form | \~8,000 faculty-hours |
| Turnaround per request | 2 to 4 days today | Same day (target) |
| Forged or altered approvals | Undetectable today | Caught in seconds: the fingerprint does not match |

**Benefits by stakeholder**

- **Students:** no queues, live status, and approvals that prove themselves for life.
- **Faculty:** approve from anywhere, several at once.
- **Administration:** an audit trail that sounds the alarm if anyone edits it, and accreditation-ready evidence for NAAC.
- **Employers and other colleges:** instant, zero-call verification.
- **Environment:** fewer trees, less toner and less waste.

**Policy alignment:** Digital India, NEP 2020, the National Blockchain Framework (launched in [September 2024 with a ₹64.76 crore budget](https://www.civilsdaily.com/?p=783300)), and APAAR / ABC for a single digital academic identity.

## 8. Environmental impact and SDGs

| Footprint avoided per year | Factor per A4 sheet | One 10,000-student university (4.5 lakh sheets) | All Indian higher education (\~200 crore sheets) |
| --- | --- | --- | --- |
| CO2e, paper production only (conservative) | [12.7 g](https://www.papercut.com/help/manuals/ng-mf/common/sys-environmental-impact/) | \~5.7 tonnes | \~25,400 tonnes |
| CO2e, full life cycle incl. landfill | [\~40 g](https://helpcenter-nddorbix.ndd.tech/en/faq/Current/how-is-the-environmental-impact-indicator-calculat) | \~18 tonnes | \~81,000 tonnes |
| Trees | 8,333 sheets per tree | \~54 trees | \~2.4 lakh trees |
| Water | \~0.4 litres | \~1.8 lakh litres | \~80 crore litres |

**A green blockchain:** we never use mining (Proof of Work). The chain runs on Proof of Authority or Proof of Stake, and each sealed document is one small transaction, so the blockchain's own energy use stays tiny next to the paper it replaces.

| SDG | What CampusSign changes |
| --- | --- |
| 4 Quality Education | Class time, not queue time; equal access for remote and differently-abled students |
| 9 Industry, Innovation and Infrastructure | Shared digital trust infrastructure any college can join |
| 12 Responsible Consumption | Single-use paper forms removed at the source |
| 13 Climate Action | A live "CO2 saved" counter on the admin dashboard |
| 15 Life on Land | Lakhs of trees not cut at national scale |
| 16 Strong Institutions | Every decision locked on chain, attributable and tamper-evident |

## 9. Feasibility and viability

**It already works.** The full product is built and tested: 123 automated server tests and 11 smart-contract tests pass, and it runs on a live server with HTTPS.

**Technical feasibility**

- One small server runs the app and a private chain; Polygon Amoy is a configuration switch away.
- Blockchain cost stays flat: each document stores all its signatures as one Merkle root, so 20 signers cost the same as 2.
- If the chain is down, seals wait in a queue and land later; nothing is lost and verification says "pending", never a false "Verified".

**Legal feasibility**

- Under the IT Act, 2000, [Section 5 gives recognised electronic signatures the same validity as wet ink](https://www.leegality.com/legalprimer/aadhaar-esign-enforceability); Aadhaar eSign is a notified technique.
- [The Bharatiya Sakshya Adhiniyam, 2023 gives electronic records the same legal status as paper (Section 61)](https://www.gktoday.in/legal-validity-of-electronic-documents-and-digital-signatures/).
- Internal approvals (OD, event permission) need only institutional policy; Aadhaar eSign is the next step for documents used outside the college.

**Economic viability (assumptions to validate)**

| Item | Per 10,000-student university, per year |
| --- | --- |
| Printing cost avoided (4.5 lakh sheets at ₹1 to ₹2 a page) | ₹4.5 to ₹9 lakh |
| Our price at ₹50 per student per year | ₹5 lakh |
| Running cost (one small server, email, chain fees) | Low, falling with scale |

**Business model:** free pilot for one department → per-student campus subscription (always free for students) → colleges pay a small membership to join the verification network → employers and verification firms pay per bulk check, which makes the network self-funding.

## 10. Competitive landscape

No existing tool combines campus role routing, a signature per approver and public blockchain verification for everyday approvals.

| Alternative | What it does well | What it misses |
| --- | --- | --- |
| Paper + wet ink | Familiar | Slow, untrackable, forgeable |
| Google Forms + email | Free and quick | No real signature, no audit trail, nothing to verify |
| College ERPs / Samarth eGov | Admissions, fees, exams at scale | Everyday ad-hoc approvals and outside verification are not their focus |
| Generic e-sign tools | Legally valid signing | No campus roles; no public proof anyone can check; per-document pricing |
| DigiLocker / NAD / APAAR | Final degrees and identity | Do not cover the in-semester approvals before a degree |
| NBF Certificate Chain | Government-grade certificate checks | Built for issued certificates, not multi-step campus workflows |

**Our edge**

- **Proves itself:** the blockchain, not our server, says who signed.
- **Role-based:** routes by role, not by name.
- **Change-aware:** amendments and cancellations show up on every copy, everywhere.
- **Works offline at the gate.**
- **Network-ready:** every college becomes a node.

**Positioning:** complementary, not competing. CampusSign is the everyday approvals layer that can feed DigiLocker and any ERP.

## 11. Security, privacy and risks

| Threat | How CampusSign stops it |
| --- | --- |
| A forged or edited PDF | Its fingerprint no longer matches the blockchain: **Tampered** |
| An old version passed off as current | The blockchain says **Superseded** and points to the latest |
| A cancelled pass still in someone's pocket | **Revoked** on chain, and on the guard's offline list |
| The same approval sealed twice | The contract refuses it |
| Someone edits an approval in our database | The contract's signer check fails for that signer |
| Someone edits or deletes audit history | The hash chain breaks and the on-chain checkpoint disagrees |
| A stranger or another college writes records | The contract accepts only approved college addresses, each for its own records |
| Guessing a PIN | Attempts are rate limited |
| Personal data leaking onto a public ledger | Impossible by design: only fingerprints, IDs and dates go on chain |

**Honest limits:** approver keys are held by the server and unlocked by the PIN (like an exchange account), so the server's secret must be protected like the database. The local chain has one validator; a real college network would run several.

**Risk register**

| Risk | Likelihood | Mitigation |
| --- | --- | --- |
| Faculty resist a new tool | Medium | Phone inbox, one PIN for several approvals; a champion faculty in the pilot |
| Some forms must stay on wet ink | Medium | Start with internal forms; Aadhaar eSign where legal weight is needed; paper fallback in the pilot |
| "Blockchain is hype" | Medium | Show the live tamper test: change one byte, watch it fail |
| Public test network downtime | Low | Seals queue and retry; a private college chain works without it |
| Lock-in | Low | Open source; standard Ethereum contract; data export anytime |

## 12. Roadmap and future scope

| Phase | What | Gate to the next phase |
| --- | --- | --- |
| **MVP (built)** | Sign, seal, amend, revoke, verify, offline gate, blockchain layer v2 | Admin approves a pilot |
| Department pilot | One department, one semester, paper fallback | Turnaround halved |
| University rollout | Aadhaar eSign and DigiLocker | 3 partner colleges |
| College network | Each college a node on one shared chain | — |

**Beyond education:** any place where a request climbs a ladder of signatures has the same problem: government offices, hospitals, banks, corporates, municipal and land records, schools and boards. In October 2025 alone, Special Campaign 5.0 [weeded out about 19.21 lakh physical government files](https://www.policyedge.in/p/government-concludes-special-campaign). The engine stays the same; only the forms and role chains change.

**Frequently asked questions**

- *Why blockchain and not just a database?* A database owner can quietly edit a record. A fingerprint on a shared blockchain lets anyone check a document without trusting the college's server, and our contract even checks each approver's own signature. If someone edits our database, the alarm goes off.
- *Is anything personal on the blockchain?* No. Only fingerprints, IDs, dates and anonymous key addresses.
- *What does it cost to run the blockchain?* One small transaction per sealed document; nothing on a private college chain.
- *Is an e-signature legally valid?* Yes for recognised e-signatures under the IT Act; internal approvals use PIN sign-off under college policy, and Aadhaar eSign is next for external documents.
- *How is this different from an ERP?* ERPs run admissions and fees; we make the everyday approval fast and provable outside the campus, and plug into any ERP.

**Next steps**

- [ ] Survey 50 students and 5 faculty to replace the assumed multipliers with measured ones.
- [ ] Secure a pilot department and a faculty champion.
- [ ] Map the 10 most-used forms and their exact signer chains.

## Sources

- [AISHE 2023-24 highlights: enrolment and teachers (CivilsDaily)](https://www.civilsdaily.com/news/aishe-2023-24-indias-higher-education-enrolment-reaches-4-5-crore/)
- [AISHE 2023-24 institutional network (Free Press Journal)](https://www.freepressjournal.in/analysis/the-aishe-report-institutional-network-of-higher-education)
- [AuthBridge Workforce Fraud Files 2025 (CXOToday)](https://cxotoday.com/press-release/authbridge-exposes-indias-hiring-red-flags/)
- [Aadhaar eSign legal validity under the IT Act (Leegality)](https://www.leegality.com/legalprimer/aadhaar-esign-enforceability)
- [Electronic records under the Bharatiya Sakshya Adhiniyam, 2023 (GKToday)](https://www.gktoday.in/legal-validity-of-electronic-documents-and-digital-signatures/)
- [National Blockchain Framework components and budget (CivilsDaily)](https://www.civilsdaily.com/?p=783300)
- [National Blockchain Framework: 34 crore documents verified (Shankar IAS)](https://www.shankariasparliament.com/current-affairs/mains-analysis/national-blockchain-framework-strengthening-governance-through-blockchain-technology)
- [DPDP Rules 2025 implementation timeline (TCSA)](https://www.tcsa.in/resources/dpdp-rules-2025-implementation-roadmap)
- [Paper footprint factors: CO2e, trees, energy (PaperCut, from the Environmental Paper Network calculator)](https://www.papercut.com/help/manuals/ng-mf/common/sys-environmental-impact/)
- [Full life-cycle CO2e and water per page (NDD, from the Environmental Paper Network calculator)](https://helpcenter-nddorbix.ndd.tech/en/faq/Current/how-is-the-environmental-impact-indicator-calculat)
- [NAAC metric 6.2.3 on e-governance (SRM University AQAR)](https://srmuniversity.ac.in/aqar/criteria6_2_3.php)
- [Special Campaign 5.0 results (The Policy Edge)](https://www.policyedge.in/p/government-concludes-special-campaign)
