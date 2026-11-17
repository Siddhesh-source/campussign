# Team

CampusSign is built by Group No. 15:

| Member | Product area | Blockchain part |
| --- | --- | --- |
| **Siddhesh Chaudhari** | Core workflow and routing engine | Approver wallets and approval signatures |
| **Devansh Goyanka** | Sealing, documents and verification | Merkle tree of approvals |
| **Ayush Jadhav** | Approver experience and operations | Smart contract and on-chain approval check |
| **Shishir Chandanshiv** | Accounts, student workspace and collaboration | Permissioned college network and governance |
| **Arya Deshmukh** | Sign in place, offline gate, design and deployment | Hash-chained audit ledger and on-chain checkpoints |

The work is split two ways, equally:

- **The blockchain layer** is shared by all five. It has five parts (`docs/BLOCKCHAIN.md`), and each member owns one from design to tests.
- **The rest of the product** is cut into five areas of about the same size. Each member owns one area end to end: backend, screens, tests and the docs for it.

The core workflow (submit → route by role → sign → seal → verify) runs through every area, so everyone tests the full flow, not just their own part.

---

## Blockchain layer: one part each

| # | Part | Owner | Code | What it does |
| --- | --- | --- | --- | --- |
| 1 | Approver wallets | Siddhesh Chaudhari | `apps/api/src/wallets.ts`, signing step in `apps/api/src/workflow.ts` | Gives every user an Ethereum wallet derived from `WALLET_SEED` plus their user id. When an approver enters their PIN, the server signs the approval leaf (request, version, role, signer, form hash, time) with that approver's own key (ECDSA, secp256k1). Ed25519 stays in place for the offline QR. |
| 2 | Merkle tree of approvals | Devansh Goyanka | `apps/api/src/merkle.ts`, root building in `apps/api/src/seal.ts` | At sealing, the approval leaves become a Merkle tree (sorted pairs, keccak-256) and only the 32-byte root goes on chain, so the cost is the same for 2 or 20 signers. Builds per-signer proofs and carries unchanged approvals into amended versions. |
| 3 | Smart contract and approval check | Ayush Jadhav | `contracts/contracts/DocumentRegistry.sol`, `contracts/test/registry.test.ts` | The `DocumentRegistry` contract: records, versions (Active / Superseded / Revoked), events and errors. Owns `checkApproval`, which uses `ecrecover` and a Merkle proof so the chain itself confirms who approved. The Verify page shows the result for each signer. |
| 4 | Permissioned college network | Shishir Chandanshiv | `issuerOf`, `addIssuer` / `removeIssuer`, `onlyIssuer` in the contract; `apps/api/src/chain.ts` | The consortium model. Only listed issuers can seal, revoke or checkpoint, and only for their own college. The owner can only govern the issuer list. Also owns contract version detection, the automatic redeploy and re-anchor of older contracts, and the issuing college ID on chain. |
| 5 | Audit ledger and checkpoints | Arya Deshmukh | `apps/api/src/ledger.ts`, `checkpoint` in the contract, `GET /api/admin/ledger`, `GET /api/chain` | Links every audit entry to the one before it (SHA-256) and writes a checkpoint on chain after each anchor. Detects edited, inserted or deleted entries and a restored older database. Also owns block number and gas per seal and the public chain status endpoint. |

Shared by all five: `apps/api/test/blockchain.test.ts` (each member writes the cases for their part), the threat table in `docs/BLOCKCHAIN.md`, and explaining their own part during the presentation.

---

## Product areas: one area each

### 1. Siddhesh Chaudhari: core workflow and routing engine

The engine every request goes through.

- Request catalogue and approval chains, including parallel steps: event permission, on-duty, bonafide, no-dues, custom request (`apps/api/src/catalog.ts`)
- Routing by role: connected teacher first, otherwise the most recently joined holder in the department; delegates are honoured (`apps/api/src/workflow.ts`)
- Approve, Return, Reject with PIN; Reopen; selective re-review after a resubmission (carried approvals)
- Amendment of a sealed request: `affectedBy` rules, only affected approvers sign again, version n+1
- API routes and error handling (`apps/api/src/routes.ts`, `apps/api/src/app.ts`, `apps/api/src/errors.ts`)
- Tests: `workflow.test.ts`, `amend.test.ts`, `feedback.test.ts`

### 2. Devansh Goyanka: sealing, documents and verification

What turns an approval into a document anyone can check.

- Sealing pipeline: PDF generation, SHA-256, anchoring queue with retry, replay after a chain restart (`apps/api/src/seal.ts`, `apps/api/src/pdf.ts`)
- Signed QR (Ed25519) and server keys (`apps/api/src/keys.ts`)
- Versioned sealing (v2 linked to v1, v1 Superseded) and revocation, with the signed revocation list
- Verify page: scan, upload, photo and link; the Verified / Tampered / Superseded / Revoked verdicts; rate limiting (`apps/web/src/pages/Verify.tsx`, `apps/api/src/ratelimit.ts`)
- Screens: `SignedDocument.tsx`, `VersionStrip.tsx`, `QrScanner.tsx`
- Tests: `seal.test.ts`, `verify.test.ts`, `revoke.test.ts`

### 3. Ayush Jadhav: approver experience and operations

Everything that makes approving quick and keeps requests moving.

- Approver inbox and PIN sheet, batch approve (one PIN, each item signed on its own) (`apps/web/src/pages/Inbox.tsx`)
- Deadlines (SLA): reminders, Overdue, escalation to the next authority (`apps/api/src/ops.ts`)
- Delegation: "Away? Set a delegate", signing on behalf of the original holder, hand-back
- Email notifications through the outbox; AWS SES configuration (`apps/api/src/notify.ts`, `docs/EMAIL_SES.md`)
- Admin and registrar: requests, Impact dashboard, audit log viewer, emails, staff dashboard and History with CSV (`Admin.tsx`, `ImpactDashboard.tsx`, `History.tsx`)
- Tests: `operations.test.ts`, `dashboard.test.ts`, `history.test.ts`

### 4. Shishir Chandanshiv: accounts, student workspace and collaboration

How people join and how students work with their teachers.

- Open sign-up and log in for students and staff, designation as role, profile, auth guards (`apps/api/src/accounts.ts`, `apps/api/src/auth.ts`, `Login.tsx`, `Profile.tsx`)
- Student workspace: home, new request, My requests, attachments with SHA-256 in the form hash (`StudentHome.tsx`, `NewRequest.tsx`, `apps/api/src/attachments.ts`)
- My teachers and People: connection requests, classes with emailed invite codes (`apps/api/src/classrooms.ts`, `MyTeachers.tsx`, `People.tsx`)
- Document library with drag and drop; discussion thread on every request (`DocumentLibrary.tsx`, `Discussion.tsx`)
- Seed and demo data (`apps/api/src/seed.ts`, `apps/api/src/demo.ts`)
- Tests: `auth.test.ts`, `accounts.test.ts`, `classrooms.test.ts`

### 5. Arya Deshmukh: sign in place, offline gate, design and deployment

Signing on the student's own PDF, the guard's check at the gate, and getting the app live.

- Sign in place: stored signatures (draw, type, upload), signature boxes on any PDF, Find sign spots, stamping and the certificate page, college form templates (`apps/api/src/stamp.ts`, `apps/api/src/templates.ts`, `SignaturePad.tsx`, `PdfSigner.tsx`, `SendDocument.tsx`)
- Offline gate check: gate PWA, QR checked on the device, validity window, revocation list sync and freshness indicator (`Gate.tsx`, `docs/OFFLINE_GATE.md`)
- Design system: one central CTA per screen, light and dark themes, icon set, logo (`apps/web/src/components/ui.tsx`, `docs/DESIGN.md`)
- Deployment and CI: AWS free tier, Caddy, systemd services, backups, GitHub Actions (`deploy/`, `docs/DEPLOY_AWS.md`, `.github/`)
- Tests: `signing.test.ts`, `gate.test.ts`, `demo.e2e.test.ts`

---

## Shared work

| Work | How it is shared |
| --- | --- |
| Full-flow testing (submit → route → sign → seal → verify) | Everyone runs it before merging; `npm test` must be green before a push |
| Docs (`docs/`) | Each member keeps the docs for their own area and blockchain part up to date |
| Pitch deck and demo | Each member presents their own blockchain part and product area |
| Code review | Every change is reviewed by one other member |
