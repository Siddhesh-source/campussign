import { sha256Hex, type LedgerStatus } from '@plc/shared';
import type { DB } from './db.js';
import type { ChainClient } from './chain.js';

interface Row {
  id: number;
  request_id: string | null;
  actor_id: string | null;
  action: string;
  version: number | null;
  details_json: string;
  at: string;
  prev_hash: string | null;
  hash: string | null;
}

/** Hash of one audit entry, chained to the entry before it. */
const entryHash = (prev: string, r: Omit<Row, 'id' | 'prev_hash' | 'hash'>) =>
  sha256Hex(`${prev}|${JSON.stringify([r.request_id, r.actor_id, r.action, r.version, r.details_json, r.at])}`);

/** Link entries written before the ledger existed (once, in order). */
function backfill(db: DB) {
  let prev = '';
  const set = db.prepare('UPDATE audit_log SET prev_hash = ?, hash = ? WHERE id = ?');
  for (const r of db.prepare('SELECT * FROM audit_log ORDER BY id').all() as Row[]) {
    const hash = r.hash ?? entryHash(prev, r);
    if (!r.hash) set.run(prev, hash, r.id);
    prev = hash;
  }
}

/** Append an audit entry, linked to the previous one by its hash. */
export function appendLedger(db: DB, e: { requestId: string | null; actorId: string | null; action: string; version: number | null; details: object; at: string }) {
  let last = db.prepare('SELECT hash FROM audit_log ORDER BY id DESC LIMIT 1').get() as { hash: string | null } | undefined;
  if (last && !last.hash) {
    backfill(db);
    last = db.prepare('SELECT hash FROM audit_log ORDER BY id DESC LIMIT 1').get() as { hash: string };
  }
  const prev = last?.hash ?? '';
  const row = { request_id: e.requestId, actor_id: e.actorId, action: e.action, version: e.version, details_json: JSON.stringify(e.details), at: e.at };
  db.prepare('INSERT INTO audit_log (request_id, actor_id, action, version, details_json, at, prev_hash, hash) VALUES (?, ?, ?, ?, ?, ?, ?, ?)').run(
    row.request_id, row.actor_id, row.action, row.version, row.details_json, row.at, prev, entryHash(prev, row),
  );
}

/** Recompute the whole chain. `brokenAt` is the first entry that does not match. */
export function checkLedger(db: DB) {
  if (db.prepare('SELECT 1 FROM audit_log WHERE hash IS NULL LIMIT 1').get()) backfill(db);
  const rows = db.prepare('SELECT * FROM audit_log ORDER BY id').all() as Row[];
  let prev = '';
  let brokenAt: number | null = null;
  for (const r of rows) {
    if (r.prev_hash !== prev || r.hash !== entryHash(prev, r)) {
      brokenAt = r.id;
      break;
    }
    prev = r.hash!;
  }
  const last = rows[rows.length - 1];
  return { entries: rows.length, ok: brokenAt === null, brokenAt, seq: last?.id ?? 0, head: last?.hash ?? null };
}

/** Write the ledger's latest entry number and hash on chain, if it moved. Never throws. */
export async function checkpointLedger(db: DB, chain: ChainClient | null) {
  if (!chain) return;
  try {
    const last = db.prepare('SELECT id, hash FROM audit_log ORDER BY id DESC LIMIT 1').get() as { id: number; hash: string | null } | undefined;
    if (!last?.hash || last.id <= (await chain.getCheckpoint()).seq) return;
    await chain.checkpoint(last.hash, last.id);
  } catch {
    /* the next anchor tries again */
  }
}

/** Ledger health for the admin: the local hash chain, compared with the on-chain checkpoint. */
export async function ledgerStatus(db: DB, chain: ChainClient | null): Promise<LedgerStatus> {
  const local = checkLedger(db);
  let checkpoint: LedgerStatus['checkpoint'] = null;
  try {
    const c = chain ? await chain.getCheckpoint() : null;
    if (c && c.seq > 0) {
      const mine = db.prepare('SELECT hash FROM audit_log WHERE id = ?').pluck().get(c.seq) as string | undefined;
      // Matches = the entries up to the checkpoint still recompute, and end in the hash the chain recorded.
      const intact = local.brokenAt === null || local.brokenAt > c.seq;
      checkpoint = { seq: c.seq, head: c.head, at: c.at, matches: intact && mine === c.head, behind: c.seq > local.seq };
    }
  } catch {
    /* chain unreachable: report the local chain only */
  }
  return { ...local, checkpoint };
}
