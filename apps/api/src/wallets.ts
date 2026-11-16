import { AbiCoder, Signature, Wallet, encodeBytes32String, getBytes, hexlify, keccak256, randomBytes, toUtf8Bytes } from 'ethers';
import type { DB } from './db.js';

/** One secret that every user's wallet key is derived from: WALLET_SEED, or generated once and kept in the kv table. */
function seed(db: DB): string {
  let s = process.env.WALLET_SEED || (db.prepare("SELECT value FROM kv WHERE key = 'wallet_seed'").pluck().get() as string | undefined);
  if (!s) {
    s = hexlify(randomBytes(32));
    db.prepare("INSERT INTO kv (key, value) VALUES ('wallet_seed', ?)").run(s);
  }
  return s;
}

/** A user's Ethereum wallet (private key, public key, address). The same user always gets the same one. */
export const walletFor = (db: DB, userId: string) => new Wallet(keccak256(toUtf8Bytes(`${seed(db)}:${userId}`)));

/** An approval in the shape of the contract's `Approval` struct. */
export interface ApprovalStruct {
  requestId: string;
  version: number;
  role: string;
  signer: string;
  formHash: string;
  signedAt: number;
}

export function approvalStruct(a: { requestId: string; version: number; role: string; signer: string; formHash: string; signedAt: string }): ApprovalStruct {
  return {
    requestId: encodeBytes32String(a.requestId),
    version: a.version,
    role: encodeBytes32String(a.role.slice(0, 31)),
    signer: a.signer,
    formHash: `0x${a.formHash}`,
    signedAt: Math.floor(new Date(a.signedAt).getTime() / 1000),
  };
}

/** Merkle leaf of an approval: matches `leafOf` in the contract. */
export const approvalLeaf = (s: ApprovalStruct) =>
  keccak256(AbiCoder.defaultAbiCoder().encode(['bytes32', 'uint32', 'bytes32', 'address', 'bytes32', 'uint64'], [s.requestId, s.version, s.role, s.signer, s.formHash, s.signedAt]));

/** Sign an approval with the approver's own wallet. Returns what is stored on the approval row. */
export function signApproval(db: DB, userId: string, a: { requestId: string; version: number; role: string; formHash: string; signedAt: string }) {
  const wallet = walletFor(db, userId);
  const leaf = approvalLeaf(approvalStruct({ ...a, signer: wallet.address }));
  return { address: wallet.address, leaf, sig: wallet.signMessageSync(getBytes(leaf)) };
}

/** Split a stored signature into the v, r, s that the contract's ecrecover takes. */
export const splitSig = (sig: string) => {
  const s = Signature.from(sig);
  return { v: s.v, r: s.r, s: s.s };
};
