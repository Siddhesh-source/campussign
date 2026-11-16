// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @title DocumentRegistry
/// @notice Anchors SHA-256 hashes of sealed approval PDFs for a network of colleges.
///         Stores no personal data: only hashes, a Merkle root of the approvals, issuing college,
///         request id, type, version, validity window and status.
contract DocumentRegistry {
    /// Lets a client tell this contract from an older deployment.
    uint256 public constant REGISTRY_VERSION = 2;

    enum Status { None, Active, Superseded, Revoked }

    struct Record {
        bytes32 issuer;        // issuing college ID, e.g. "COLLEGE-001"
        bytes32 requestId;     // e.g. "PLC-2026-0001" as bytes32
        bytes32 docType;       // e.g. "event_permission" as bytes32
        uint32 version;        // 1, 2, ...
        bytes32 prevHash;      // hash of the version this one amends (0 for v1)
        bytes32 rolesHash;     // SHA-256 of the canonical list of signer roles and times
        bytes32 approvalsRoot; // Merkle root of the approval leaves (0 when there are none)
        uint64 sealedAt;       // unix seconds
        uint64 validFrom;      // unix seconds
        uint64 validUntil;     // unix seconds
        Status status;
    }

    /// One approver's approval. Its hash is a leaf of the document's Merkle tree and is what the approver signs.
    struct Approval {
        bytes32 requestId;
        uint32 version;    // the version that was actually signed
        bytes32 role;      // e.g. "hod" as bytes32
        address signer;    // the approver's wallet address
        bytes32 formHash;  // SHA-256 of the form contents that were approved
        uint64 signedAt;   // unix seconds
    }

    /// Latest point of a college's audit ledger: entry number and that entry's hash.
    struct Checkpoint {
        bytes32 head;
        uint64 seq;
        uint64 at;
    }

    address public immutable owner;                      // governance: manages the issuer list only
    mapping(address => bytes32) public issuerOf;         // authorised address => college ID (0 = not authorised)
    mapping(bytes32 => Record) private records;          // docHash => record
    mapping(bytes32 => bytes32) public supersededBy;     // old docHash => new docHash
    mapping(bytes32 => bytes32) public latestFor;        // requestId => latest docHash
    mapping(bytes32 => uint8) public revokeReason;       // docHash => reason code
    mapping(bytes32 => Checkpoint) public checkpointOf;  // college ID => latest audit checkpoint

    event IssuerAdded(address indexed who, bytes32 indexed college);
    event IssuerRemoved(address indexed who, bytes32 indexed college);
    event Sealed(bytes32 indexed docHash, bytes32 indexed requestId, uint32 version, bytes32 prevHash);
    event Superseded(bytes32 indexed oldHash, bytes32 indexed newHash);
    event Revoked(bytes32 indexed docHash, uint8 reasonCode);
    event Checkpointed(bytes32 indexed college, uint64 seq, bytes32 head);

    error NotOwner();
    error NotIssuer();
    error WrongCollege();
    error EmptyHash();
    error AlreadySealed();
    error RequestAlreadySealed();
    error PrevNotActive();
    error PrevOtherRequest();
    error BadVersion();
    error NotActive();
    error StaleCheckpoint();

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        if (msg.sender != owner) revert NotOwner();
        _;
    }

    modifier onlyIssuer() {
        if (issuerOf[msg.sender] == bytes32(0)) revert NotIssuer();
        _;
    }

    // ---------- governance ----------

    /// @notice Authorise an address to write records for one college.
    function addIssuer(address who, bytes32 college) external onlyOwner {
        if (college == bytes32(0)) revert EmptyHash();
        issuerOf[who] = college;
        emit IssuerAdded(who, college);
    }

    /// @notice Withdraw an address's authority. Its past records stay.
    function removeIssuer(address who) external onlyOwner {
        emit IssuerRemoved(who, issuerOf[who]);
        delete issuerOf[who];
    }

    // ---------- records ----------

    /// @notice Seal a document. With prevHash set, the previous version must be Active and is marked Superseded.
    function seal(bytes32 docHash, Record calldata r) external onlyIssuer {
        if (r.issuer != issuerOf[msg.sender]) revert WrongCollege();
        if (docHash == bytes32(0)) revert EmptyHash();
        if (records[docHash].status != Status.None) revert AlreadySealed();

        if (r.prevHash == bytes32(0)) {
            if (latestFor[r.requestId] != bytes32(0)) revert RequestAlreadySealed();
            if (r.version != 1) revert BadVersion();
        } else {
            Record storage p = records[r.prevHash];
            if (p.status != Status.Active) revert PrevNotActive();
            if (p.requestId != r.requestId) revert PrevOtherRequest();
            if (p.issuer != r.issuer) revert WrongCollege();
            if (r.version != p.version + 1) revert BadVersion();
            p.status = Status.Superseded;
            supersededBy[r.prevHash] = docHash;
            emit Superseded(r.prevHash, docHash);
        }

        records[docHash] = Record({
            issuer: r.issuer,
            requestId: r.requestId,
            docType: r.docType,
            version: r.version,
            prevHash: r.prevHash,
            rolesHash: r.rolesHash,
            approvalsRoot: r.approvalsRoot,
            sealedAt: uint64(block.timestamp),
            validFrom: r.validFrom,
            validUntil: r.validUntil,
            status: Status.Active
        });
        latestFor[r.requestId] = docHash;
        emit Sealed(docHash, r.requestId, r.version, r.prevHash);
    }

    /// @notice Revoke an active document of the caller's college.
    function revoke(bytes32 docHash, uint8 reasonCode) external onlyIssuer {
        Record storage rec = records[docHash];
        if (rec.status != Status.Active) revert NotActive();
        if (rec.issuer != issuerOf[msg.sender]) revert WrongCollege();
        rec.status = Status.Revoked;
        revokeReason[docHash] = reasonCode;
        emit Revoked(docHash, reasonCode);
    }

    function get(bytes32 docHash) external view returns (Record memory) {
        return records[docHash];
    }

    // ---------- audit ledger checkpoints ----------

    /// @notice Record the latest entry of the caller's audit ledger. It can only move forward.
    function checkpoint(bytes32 head, uint64 seq) external onlyIssuer {
        bytes32 college = issuerOf[msg.sender];
        if (seq <= checkpointOf[college].seq) revert StaleCheckpoint();
        checkpointOf[college] = Checkpoint({ head: head, seq: seq, at: uint64(block.timestamp) });
        emit Checkpointed(college, seq, head);
    }

    // ---------- checking one approval ----------

    /// @notice The Merkle leaf for an approval: the hash the approver signs.
    function leafOf(Approval calldata a) public pure returns (bytes32) {
        return keccak256(abi.encode(a.requestId, a.version, a.role, a.signer, a.formHash, a.signedAt));
    }

    /// @notice Walk a Merkle proof from a leaf up to a root. Each pair is sorted before hashing.
    function inTree(bytes32 root, bytes32 leaf, bytes32[] calldata proof) public pure returns (bool) {
        bytes32 node = leaf;
        for (uint256 i = 0; i < proof.length; i++) {
            bytes32 other = proof[i];
            node = node < other ? keccak256(abi.encodePacked(node, other)) : keccak256(abi.encodePacked(other, node));
        }
        return node == root;
    }

    /// @notice True when the approval was signed by the wallet it names and is part of the sealed document.
    function checkApproval(bytes32 docHash, Approval calldata a, uint8 v, bytes32 r, bytes32 s, bytes32[] calldata proof)
        external
        view
        returns (bool)
    {
        Record storage rec = records[docHash];
        if (rec.status == Status.None || rec.approvalsRoot == bytes32(0)) return false;
        if (a.requestId != rec.requestId || a.signer == address(0)) return false;
        bytes32 leaf = leafOf(a);
        bytes32 signed = keccak256(abi.encodePacked("\x19Ethereum Signed Message:\n32", leaf));
        if (ecrecover(signed, v, r, s) != a.signer) return false;
        return inTree(rec.approvalsRoot, leaf, proof);
    }
}
