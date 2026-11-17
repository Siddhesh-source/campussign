import { describe, expect, it } from 'vitest';
import { HDNodeWallet, JsonRpcProvider, Wallet, ZeroHash, id as keccak } from 'ethers';
import { merkleProof, merkleRoot, verifyProof } from '../src/merkle.js';
import { walletFor } from '../src/wallets.js';
import { ChainClient, dbAddressStore } from '../src/chain.js';
import { replayAll } from '../src/seal.js';
import { RIYA_EVENT, rpcUrl, setup } from './helpers.js';

const NEW_PLAN = { date: '2027-11-12', venue: 'Main Auditorium' };

describe('Merkle tree', () => {
  it('every leaf proves into the root, for 1 to 6 leaves; a wrong leaf or proof does not', () => {
    for (let n = 1; n <= 6; n++) {
      const leaves = Array.from({ length: n }, (_, i) => keccak(`leaf${i}`));
      const root = merkleRoot(leaves);
      if (n === 1) expect(root).toBe(leaves[0]);
      leaves.forEach((l, i) => expect(verifyProof(root, l, merkleProof(leaves, i))).toBe(true));
      expect(verifyProof(root, keccak('other'), merkleProof(leaves, 0))).toBe(false);
    }
    expect(merkleRoot([])).toBe(ZeroHash);
  });
});

describe('approver wallets', () => {
  it('each person has their own stable address', async () => {
    const { db } = await setup();
    expect(walletFor(db, 'u_mehta').address).toBe(walletFor(db, 'u_mehta').address);
    expect(walletFor(db, 'u_mehta').address).not.toBe(walletFor(db, 'u_rao').address);
  });
});

describe('approvals on chain', () => {
  it('every signer is checked by the contract: own wallet signature + Merkle proof against the stored root', async () => {
    const { db, approvedEvent, pub, chain } = await setup();
    const id = await approvedEvent();
    const v = (await pub(`/api/verify/ref/${id}/1`)).body;
    expect(v.status).toBe('verified');
    expect(v.signers).toHaveLength(4);
    for (const s of v.signers) {
      expect(s.onChain).toBe(true);
      expect(s.address).toMatch(/^0x[0-9a-fA-F]{40}$/);
    }
    expect(v.signers.map((s: { address: string }) => s.address)).toContain(walletFor(db, 'u_kulkarni').address);
    expect(v.approvalsRoot).toMatch(/^0x[0-9a-f]{64}$/);
    expect((await chain.get(v.docHash)).approvalsRoot).toBe(v.approvalsRoot);
    expect(v.blockNumber).toBeGreaterThan(0);
    expect(v.gasUsed).toBeGreaterThan(0);
    // A rejected or returned decision is never a leaf.
    const leaves = db.prepare("SELECT COUNT(*) FROM approvals WHERE request_id = ? AND leaf IS NOT NULL AND decision <> 'approved'").pluck().get(id);
    expect(leaves).toBe(0);
  });

  it('an edited approval row no longer passes the on-chain check', async () => {
    const { db, approvedEvent, pub } = await setup();
    const id = await approvedEvent();
    db.prepare("UPDATE approvals SET wallet_address = ? WHERE request_id = ? AND role = 'hod'").run(Wallet.createRandom().address, id);
    const v = (await pub(`/api/verify/ref/${id}/1`)).body;
    const hod = v.signers.find((s: { role: string }) => s.role === 'hod');
    expect(hod.onChain).toBe(false);
    expect(v.signers.filter((s: { onChain: boolean }) => s.onChain)).toHaveLength(3);
  });

  it('after an amendment, carried approvals keep their original signature and still check out in v2', async () => {
    const { as, act, approvedEvent, pub } = await setup();
    const id = await approvedEvent();
    await as('u_riya').post(`/api/requests/${id}/amend`, { changes: NEW_PLAN, reason: 'Hall B under repair' });
    await act('u_mehta', id, 'approved');
    await act('u_kulkarni', id, 'approved');
    const v2 = (await pub(`/api/verify/ref/${id}/2`)).body;
    expect(v2.status).toBe('verified');
    const carried = v2.signers.filter((s: { carried: boolean }) => s.carried);
    expect(carried.map((s: { role: string }) => s.role).sort()).toEqual(['dean_sa', 'security']);
    for (const s of v2.signers) expect(s.onChain).toBe(true);
    const v1 = (await pub(`/api/verify/ref/${id}/1`)).body;
    expect(v1.status).toBe('superseded');
    expect(v1.approvalsRoot).not.toBe(v2.approvalsRoot);
  });
});

describe('hash-chained audit ledger', () => {
  it('checkpoints on chain, detects an edited entry and a rolled-back database', async () => {
    const { db, approvedEvent, as } = await setup();
    await approvedEvent();
    let l = (await as('u_admin').get('/api/admin/ledger')).body;
    expect(l.ok).toBe(true);
    expect(l.entries).toBeGreaterThan(5);
    expect(l.checkpoint.matches).toBe(true);
    expect(l.checkpoint.behind).toBe(false);
    expect(l.checkpoint.seq).toBeLessThanOrEqual(l.seq);

    // Someone with database access changes who did what.
    const target = db.prepare("SELECT id FROM audit_log WHERE action = 'approved' ORDER BY id LIMIT 1").pluck().get() as number;
    db.prepare('UPDATE audit_log SET actor_id = ? WHERE id = ?').run('u_admin', target);
    l = (await as('u_admin').get('/api/admin/ledger')).body;
    expect(l.ok).toBe(false);
    expect(l.brokenAt).toBe(target);
    expect(l.checkpoint.matches).toBe(false);
    expect((await as('u_riya').get('/api/admin/ledger')).status).toBe(403);
  });

  it('deleting the latest entries shows the database is behind the chain', async () => {
    const { db, approvedEvent, as } = await setup();
    await approvedEvent();
    const before = (await as('u_admin').get('/api/admin/ledger')).body;
    db.prepare('DELETE FROM audit_log WHERE id >= ?').run(before.checkpoint.seq);
    const after = (await as('u_admin').get('/api/admin/ledger')).body;
    expect(after.ok).toBe(true); // what is left is consistent...
    expect(after.checkpoint.behind).toBe(true); // ...but the chain remembers more
  });
});

describe('chain facts and upgrade', () => {
  it('GET /api/chain shows the network, consensus, issuer and totals', async () => {
    const { approvedEvent, pub, chain } = await setup();
    await approvedEvent();
    const c = (await pub('/api/chain')).body;
    expect(c).toMatchObject({ network: 'local', chainId: 31337, registryVersion: 2, college: 'COLLEGE-001', anchored: 1 });
    expect(c.consensus).toMatch(/Proof of Authority/);
    expect(c.contract).toBe(await chain.address());
    expect(c.issuer).toBe(chain.issuerAddress);
    expect(c.gasUsed).toBeGreaterThan(0);
    expect(c.blockNumber).toBeGreaterThan(0);
    expect(c.checkpoint.seq).toBeGreaterThan(0);
  });

  it('an older contract at the stored address is replaced and everything is anchored again', async () => {
    // A contract that answers 42 to every call stands in for an older registry.
    const key = HDNodeWallet.fromPhrase('test test test test test test test test test test test junk', undefined, "m/44'/60'/0'/0/18").privateKey;
    const deployer = new Wallet(key, new JsonRpcProvider(rpcUrl(), undefined, { staticNetwork: true, cacheTimeout: -1 }));
    const receipt = await (await deployer.sendTransaction({ data: '0x600a600c600039600a6000f3602a60005260206000f3' })).wait();
    const old = receipt!.contractAddress!;

    const ctx = await setup({
      chain: (db) => {
        dbAddressStore(db, 'local').set(old);
        return new ChainClient({ network: 'local', rpcUrl: rpcUrl(), privateKey: key, store: dbAddressStore(db, 'local'), onFreshDeploy: () => replayAll(db) });
      },
    });
    const id = await ctx.approvedEvent(RIYA_EVENT);
    expect(await ctx.chain.address()).not.toBe(old);
    expect((await ctx.pub(`/api/verify/ref/${id}/1`)).body.status).toBe('verified');
  });
});
