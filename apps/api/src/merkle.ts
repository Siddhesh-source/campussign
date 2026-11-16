import { ZeroHash, concat, keccak256 } from 'ethers';

/** Hash two nodes into their parent. The pair is sorted first, so a proof needs no left/right flags. */
const parent = (a: string, b: string) => keccak256(concat(a.toLowerCase() < b.toLowerCase() ? [a, b] : [b, a]));

/** Every level of the tree, leaves first. An odd node moves up unchanged. */
function levels(leaves: string[]): string[][] {
  const all = [leaves];
  while (all[all.length - 1].length > 1) {
    const level = all[all.length - 1];
    const next: string[] = [];
    for (let i = 0; i < level.length; i += 2) next.push(i + 1 < level.length ? parent(level[i], level[i + 1]) : level[i]);
    all.push(next);
  }
  return all;
}

/** Merkle root of 0x-prefixed 32-byte leaves. No leaves gives the zero hash. */
export function merkleRoot(leaves: string[]): string {
  if (!leaves.length) return ZeroHash;
  const all = levels(leaves);
  return all[all.length - 1][0];
}

/** The sibling hashes needed to rebuild the root from the leaf at `index`. */
export function merkleProof(leaves: string[], index: number): string[] {
  const proof: string[] = [];
  for (const level of levels(leaves).slice(0, -1)) {
    const sibling = index ^ 1;
    if (sibling < level.length) proof.push(level[sibling]);
    index >>= 1;
  }
  return proof;
}

/** The same walk the contract does in `inTree`. */
export const verifyProof = (root: string, leaf: string, proof: string[]) => proof.reduce(parent, leaf).toLowerCase() === root.toLowerCase();
