import { Contract, JsonRpcProvider, Wallet, encodeBytes32String, decodeBytes32String, ZeroHash } from 'ethers';
import { DocumentRegistryArtifact, LOCAL_DEV_KEY, REGISTRY_VERSION, deployRegistry } from '@plc/contracts';
import { splitSig, type ApprovalStruct } from './wallets.js';

export interface ChainRecord {
  status: 'none' | 'active' | 'superseded' | 'revoked';
  issuer: string;
  requestId: string;
  docType: string;
  version: number;
  prevHash: string | null;
  approvalsRoot: string | null;
  sealedAt: number;
  validFrom: number;
  validUntil: number;
  supersededBy: string | null;
  revokeReason: number;
}

export interface SealArgs {
  docHash: string; // hex, no 0x
  issuer: string; // college id
  requestId: string;
  docType: string;
  version: number;
  prevHash: string | null;
  rolesHash: string;
  /** Merkle root of the approval leaves (0x hex); null or missing for none. */
  approvalsRoot?: string | null;
  validFrom: number;
  validUntil: number;
}

/** Where a write landed. */
export interface Receipt {
  txHash: string;
  blockNumber: number;
  gasUsed: number;
}

export interface ChainOptions {
  network: 'local' | 'amoy' | string;
  rpcUrl: string;
  privateKey: string;
  /** College this server writes for; registered as an issuer when the contract is deployed (default COLLEGE-001). */
  collegeId?: string;
  /** Where to remember the contract address (the app's database). Without it, every connect deploys a fresh contract. */
  store?: { get: () => string | undefined; set: (address: string) => void };
  /** Called after a fresh deploy (local node restarted, or an older contract replaced) so stored seals can be replayed. */
  onFreshDeploy?: () => void;
}

const STATUS = ['none', 'active', 'superseded', 'revoked'] as const;
const hx = (h: string) => (h.startsWith('0x') ? h : `0x${h}`).toLowerCase();
const plain = (h: string) => h.replace(/^0x/, '').toLowerCase();
const TIMEOUT = 20_000;

function withTimeout<T>(p: Promise<T>, what: string): Promise<T> {
  return Promise.race([p, new Promise<T>((_, rej) => setTimeout(() => rej(new Error(`${what} timed out`)), TIMEOUT))]);
}

/** Thin client for DocumentRegistry. Writes are serialised so nonces never collide. */
export class ChainClient {
  private contract: Contract | null = null;
  private connecting: Promise<Contract> | null = null;
  private lane: Promise<unknown> = Promise.resolve();

  constructor(private opts: ChainOptions) {}

  get network() {
    return this.opts.network;
  }

  get college() {
    return (this.opts.collegeId ?? 'COLLEGE-001').slice(0, 31);
  }

  /** The address this server signs chain transactions from. */
  get issuerAddress() {
    return new Wallet(this.opts.privateKey).address;
  }

  async address() {
    return (await this.connect()).getAddress();
  }

  /** Forget the connected contract (after the stored address was cleared); the next call connects again. */
  reset() {
    this.contract = null;
    this.connecting = null;
  }

  /** Point at a different RPC (used by tests to simulate an outage and recovery). */
  useRpc(rpcUrl: string) {
    this.opts = { ...this.opts, rpcUrl };
    this.contract = null;
    this.connecting = null;
  }

  txUrl(txHash: string | null) {
    if (!txHash) return null;
    return this.opts.network === 'amoy' ? `https://amoy.polygonscan.com/tx/${txHash}` : null;
  }

  /** True when the address holds this version of the registry (an older deployment is replaced). */
  private async isCurrent(provider: JsonRpcProvider, address: string) {
    if ((await withTimeout(provider.getCode(address), 'getCode')) === '0x') return false;
    try {
      const c = new Contract(address, DocumentRegistryArtifact.abi as never, provider);
      return Number(await withTimeout(c.REGISTRY_VERSION(), 'version')) === REGISTRY_VERSION;
    } catch {
      return false;
    }
  }

  private connect(): Promise<Contract> {
    if (this.contract) return Promise.resolve(this.contract);
    this.connecting ??= (async () => {
      const provider = new JsonRpcProvider(this.opts.rpcUrl, undefined, { staticNetwork: true, cacheTimeout: -1 });
      const wallet = new Wallet(this.opts.privateKey, provider);
      let address = this.opts.store?.get();
      if (!address || !(await this.isCurrent(provider, address))) {
        const replace = !!address; // had a contract: the chain lost it, or it is an older version
        address = await withTimeout(deployRegistry(wallet), 'deploy');
        // Governance step: the deploying account authorises itself to write for its college.
        const c = new Contract(address, DocumentRegistryArtifact.abi as never, wallet);
        await withTimeout(c.addIssuer(wallet.address, encodeBytes32String(this.college)).then((tx: { wait: () => Promise<unknown> }) => tx.wait()), 'addIssuer');
        this.opts.store?.set(address);
        if (replace) this.opts.onFreshDeploy?.();
      }
      this.contract = new Contract(address!, DocumentRegistryArtifact.abi as never, wallet);
      return this.contract;
    })().catch((e) => {
      this.connecting = null;
      throw e;
    });
    return this.connecting;
  }

  /**
   * Connected contract that still has code. If the chain lost it (local node restarted), forget it and
   * connect again, which redeploys and triggers onFreshDeploy. Prevents "successful" writes to an empty address.
   */
  private async live(): Promise<Contract> {
    const c = await this.connect();
    if ((await withTimeout(c.runner!.provider!.getCode(await c.getAddress()), 'getCode')) !== '0x') return c;
    this.contract = null;
    this.connecting = null;
    return this.connect();
  }

  private write(fn: (c: Contract) => Promise<{ wait: () => Promise<{ hash: string; blockNumber: number; gasUsed: bigint } | null> }>): Promise<Receipt> {
    const run = this.lane.then(async () => {
      const c = await this.live();
      try {
        const tx = await withTimeout(fn(c), 'send');
        const receipt = (await withTimeout(tx.wait(), 'confirm'))!;
        return { txHash: receipt.hash, blockNumber: Number(receipt.blockNumber), gasUsed: Number(receipt.gasUsed) };
      } catch (e) {
        throw named(c, e);
      }
    });
    this.lane = run.catch(() => undefined);
    return run;
  }

  seal(a: SealArgs): Promise<Receipt> {
    return this.write((c) =>
      c.seal(hx(a.docHash), {
        issuer: encodeBytes32String(a.issuer.slice(0, 31)),
        requestId: encodeBytes32String(a.requestId),
        docType: encodeBytes32String(a.docType.slice(0, 31)),
        version: a.version,
        prevHash: a.prevHash ? hx(a.prevHash) : ZeroHash,
        rolesHash: hx(a.rolesHash),
        approvalsRoot: a.approvalsRoot ? hx(a.approvalsRoot) : ZeroHash,
        sealedAt: 0,
        validFrom: a.validFrom,
        validUntil: a.validUntil,
        status: 0,
      }),
    );
  }

  async revoke(docHash: string, reasonCode: number): Promise<string> {
    return (await this.write((c) => c.revoke(hx(docHash), reasonCode))).txHash;
  }

  /** Record the audit ledger's latest entry on chain. */
  async checkpoint(head: string, seq: number): Promise<string> {
    return (await this.write((c) => c.checkpoint(hx(head), seq))).txHash;
  }

  async getCheckpoint(): Promise<{ seq: number; head: string; at: number }> {
    const c = await this.live();
    const r = await withTimeout(c.checkpointOf(encodeBytes32String(this.college)), 'read');
    return { seq: Number(r.seq), head: plain(r.head), at: Number(r.at) };
  }

  /** Ask the contract: did this wallet sign this approval, and is the approval part of this document? */
  async checkApproval(docHash: string, a: ApprovalStruct, signature: string, proof: string[]): Promise<boolean> {
    const c = await this.live();
    const { v, r, s } = splitSig(signature);
    return withTimeout(c.checkApproval(hx(docHash), a, v, r, s, proof), 'read');
  }

  async get(docHash: string): Promise<ChainRecord> {
    const c = await this.live();
    const [r, next, reason] = await withTimeout(
      Promise.all([c.get(hx(docHash)), c.supersededBy(hx(docHash)), c.revokeReason(hx(docHash))]),
      'read',
    );
    const status = STATUS[Number(r.status)];
    return {
      status,
      issuer: status === 'none' ? '' : decodeBytes32String(r.issuer),
      requestId: status === 'none' ? '' : decodeBytes32String(r.requestId),
      docType: status === 'none' ? '' : decodeBytes32String(r.docType),
      version: Number(r.version),
      prevHash: r.prevHash === ZeroHash ? null : plain(r.prevHash),
      approvalsRoot: r.approvalsRoot === ZeroHash ? null : (r.approvalsRoot as string).toLowerCase(),
      sealedAt: Number(r.sealedAt),
      validFrom: Number(r.validFrom),
      validUntil: Number(r.validUntil),
      supersededBy: next === ZeroHash ? null : plain(next),
      revokeReason: Number(reason),
    };
  }

  /** Public facts about the network and the registry. */
  async info() {
    const c = await this.live();
    const provider = c.runner!.provider!;
    const [net, blockNumber, owner, contract, college] = await withTimeout(
      Promise.all([provider.getNetwork(), provider.getBlockNumber(), c.owner(), c.getAddress(), c.issuerOf(this.issuerAddress)]),
      'read',
    );
    return {
      chainId: Number(net.chainId),
      blockNumber,
      owner: owner as string,
      contract,
      college: college === ZeroHash ? '' : decodeBytes32String(college),
    };
  }
}

/** Turn a revert into an Error named after the contract's custom error (e.g. "RequestAlreadySealed"). */
function named(c: Contract, e: unknown): Error {
  const err = e as { data?: string; info?: { error?: { data?: string | { data?: string } } }; message?: string };
  const raw = err?.data ?? (typeof err?.info?.error?.data === 'string' ? err.info.error.data : err?.info?.error?.data?.data);
  try {
    const parsed = raw ? c.interface.parseError(raw) : null;
    if (parsed) return new Error(`Contract refused: ${parsed.name}`);
  } catch {
    /* not a contract error */
  }
  return e instanceof Error ? e : new Error(String(e));
}

/** Contract address per network, remembered in the app database so a fresh database gets a fresh contract. */
export function dbAddressStore(db: { prepare: (sql: string) => any }, network: string) {
  const key = `registry_address:${network}`;
  return {
    get: () => db.prepare('SELECT value FROM kv WHERE key = ?').pluck().get(key) as string | undefined,
    set: (address: string) => db.prepare('INSERT INTO kv (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value').run(key, address),
  };
}

export function chainFromConfig(
  cfg: { chainMode: string; localRpcUrl: string; amoyRpcUrl: string; amoyPrivateKey: string; collegeId?: string },
  store: (network: string) => ChainOptions['store'],
  onFreshDeploy?: () => void,
) {
  if (cfg.chainMode === 'off') return null;
  const collegeId = cfg.collegeId;
  if (cfg.chainMode === 'amoy') {
    if (!cfg.amoyPrivateKey) throw new Error('CHAIN_MODE=amoy needs AMOY_PRIVATE_KEY (a funded Amoy test wallet)');
    return new ChainClient({ network: 'amoy', rpcUrl: cfg.amoyRpcUrl, privateKey: cfg.amoyPrivateKey, collegeId, store: store('amoy'), onFreshDeploy });
  }
  return new ChainClient({ network: 'local', rpcUrl: cfg.localRpcUrl, privateKey: LOCAL_DEV_KEY, collegeId, store: store('local'), onFreshDeploy });
}
