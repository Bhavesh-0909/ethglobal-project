// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

/**
 * @title DAO Staking Governance (Optimized)
 * @dev Optimized for gas and clarity while retaining original semantics.
 */
contract DAOStakingGovernance is AccessControl, ReentrancyGuard, Pausable {
    using SafeERC20 for IERC20;

    // Roles
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant PROPOSAL_AGENT_ROLE = keccak256("PROPOSAL_AGENT_ROLE");
    bytes32 public constant VOTER_AGENT_ROLE = keccak256("VOTER_AGENT_ROLE");
    bytes32 public constant EXECUTION_AGENT_ROLE = keccak256("EXECUTION_AGENT_ROLE");

    // Enums
    enum ProposalStatus { Pending, Active, Approved, Rejected, Executed, Cancelled }
    enum VoteType { None, For, Against, Abstain }

    // Organization
    struct Organization {
        uint256 id;
        string name;
        string description;
        address owner;
        address stakingToken;           // address(0) for ETH
        uint256 minStakeAmount;
        uint256 totalStaked;
        uint256 memberCount;
        bool isActive;
        uint256 createdAt;
        // mappings
        mapping(address => uint256) memberStakes;
        mapping(address => uint256) memberJoinTime;
        uint256[] proposalIds;
    }

    // Proposal
    struct Proposal {
        uint256 id;
        uint256 organizationId;
        string title;
        string description;
        address proposer;
        uint256 requestedAmount;
        address tokenAddress;           // address(0) for ETH
        address recipientAddress;
        ProposalStatus status;
        uint256 createdAt;
        uint256 votingStartTime;
        uint256 votingEndTime;
        uint256 executedAt;
        // votes
        uint256 forVotes;
        uint256 againstVotes;
        uint256 abstainVotes;
        mapping(address => VoteType) votes;
        mapping(address => uint256) voteWeights;
        // agent analysis
        string agentAnalysisHash;
        uint256 riskLevel;
        uint256 confidenceScore;
        string sentimentAnalysis;
        bool executionApproved;
    }

    // Agent metadata
    struct AgentInfo {
        string name;
        bool isActive;
        uint256 registeredAt;
        uint256 lastActivity;
    }

    // State
    mapping(uint256 => Organization) private organizations;
    uint256 public organizationCount;

    mapping(uint256 => Proposal) private proposals;
    uint256 public proposalCount;

    mapping(address => AgentInfo) public agents;
    // removed agentList to avoid unbounded growth

    mapping(uint256 => mapping(address => uint256)) public organizationTreasury; // orgId => token => amount

    // Constants
    uint256 public constant VOTING_PERIOD = 24 hours;
    uint256 public constant MIN_STAKE_PERIOD = 1 hours;

    // Events (kept compact)
    event OrganizationCreated(uint256 indexed orgId, string name, address indexed owner, address stakingToken, uint256 minStakeAmount);
    event MemberJoined(uint256 indexed orgId, address indexed member, uint256 stakeAmount);
    event MemberLeft(uint256 indexed orgId, address indexed member, uint256 returnedAmount);
    event StakeIncreased(uint256 indexed orgId, address indexed member, uint256 newAmount);

    event ProposalCreated(uint256 indexed proposalId, uint256 indexed orgId, address indexed proposer, string title);
    event ProposalAnalyzed(uint256 indexed proposalId, address indexed agent, string analysisHash, uint256 riskLevel);
    event VotingStarted(uint256 indexed proposalId, uint256 startTime, uint256 endTime);
    event VoteCast(uint256 indexed proposalId, address indexed voter, VoteType vote, uint256 weight);
    event ProposalExecuted(uint256 indexed proposalId, bool success, uint256 amount);

    event AgentRegistered(address indexed agent, string name);
    event TreasuryFunded(uint256 indexed orgId, address token, uint256 amount);

    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
    }

    // ===== ORGANIZATION MANAGEMENT =====

    function createOrganization(
        string memory name,
        string memory description,
        address stakingToken,
        uint256 minStakeAmount
    ) external returns (uint256) {
        require(bytes(name).length > 0, "Name required");
        require(minStakeAmount > 0, "Min stake must be > 0");

        unchecked { organizationCount++; }
        uint256 newId = organizationCount;

        Organization storage org = organizations[newId];
        org.id = newId;
        org.name = name;
        org.description = description;
        org.owner = msg.sender;
        org.stakingToken = stakingToken;
        org.minStakeAmount = minStakeAmount;
        org.totalStaked = 0;
        org.memberCount = 0;
        org.isActive = true;
        org.createdAt = block.timestamp;

        emit OrganizationCreated(newId, name, msg.sender, stakingToken, minStakeAmount);
        return newId;
    }

    function joinOrganization(uint256 orgId, uint256 stakeAmount) external payable nonReentrant whenNotPaused {
        require(orgId > 0 && orgId <= organizationCount, "Invalid org ID");

        Organization storage org = organizations[orgId];
        require(org.isActive, "Organization not active");
        require(stakeAmount >= org.minStakeAmount, "Stake below min");
        require(org.memberStakes[msg.sender] == 0, "Already a member");

        // Transfer staking tokens
        if (org.stakingToken == address(0)) {
            require(msg.value == stakeAmount, "ETH amount mismatch");
        } else {
            require(msg.value == 0, "Do not send ETH for token staking");
            IERC20(org.stakingToken).safeTransferFrom(msg.sender, address(this), stakeAmount);
        }

        org.memberStakes[msg.sender] = stakeAmount;
        org.memberJoinTime[msg.sender] = block.timestamp;
        org.totalStaked += stakeAmount;
        org.memberCount++;

        emit MemberJoined(orgId, msg.sender, stakeAmount);
    }

    function increaseStake(uint256 orgId, uint256 additionalAmount) external payable nonReentrant whenNotPaused {
        Organization storage org = organizations[orgId];
        uint256 currentStake = org.memberStakes[msg.sender];
        require(currentStake > 0, "Not a member");
        require(additionalAmount > 0, "Amount must be > 0");

        if (org.stakingToken == address(0)) {
            require(msg.value == additionalAmount, "ETH amount mismatch");
        } else {
            require(msg.value == 0, "Do not send ETH for token staking");
            IERC20(org.stakingToken).safeTransferFrom(msg.sender, address(this), additionalAmount);
        }

        org.memberStakes[msg.sender] = currentStake + additionalAmount;
        org.totalStaked += additionalAmount;

        emit StakeIncreased(orgId, msg.sender, org.memberStakes[msg.sender]);
    }

    function leaveOrganization(uint256 orgId) external nonReentrant {
        Organization storage org = organizations[orgId];
        uint256 stakeAmount = org.memberStakes[msg.sender];
        require(stakeAmount > 0, "Not a member");

        // update accounting
        delete org.memberStakes[msg.sender];
        delete org.memberJoinTime[msg.sender];
        unchecked { org.memberCount--; }
        org.totalStaked -= stakeAmount;

        // return funds
        if (org.stakingToken == address(0)) {
            (bool success, ) = payable(msg.sender).call{value: stakeAmount}("");
            require(success, "ETH transfer failed");
        } else {
            IERC20(org.stakingToken).safeTransfer(msg.sender, stakeAmount);
        }

        emit MemberLeft(orgId, msg.sender, stakeAmount);
    }

    // ===== PROPOSAL MANAGEMENT =====

    function createProposal(
        uint256 orgId,
        string memory title,
        string memory description,
        uint256 requestedAmount,
        address tokenAddress,
        address recipientAddress
    ) external returns (uint256) {
        Organization storage org = organizations[orgId];
        require(org.memberStakes[msg.sender] > 0, "Must be staked member");
        require(bytes(title).length > 0, "Title required");
        require(recipientAddress != address(0), "Invalid recipient");

        unchecked { proposalCount++; }
        uint256 newPid = proposalCount;

        Proposal storage p = proposals[newPid];
        p.id = newPid;
        p.organizationId = orgId;
        p.title = title;
        p.description = description;
        p.proposer = msg.sender;
        p.requestedAmount = requestedAmount;
        p.tokenAddress = tokenAddress;
        p.recipientAddress = recipientAddress;
        p.status = ProposalStatus.Pending;
        p.createdAt = block.timestamp;

        org.proposalIds.push(newPid);

        emit ProposalCreated(newPid, orgId, msg.sender, title);
        return newPid;
    }

    // ===== AGENT INTEGRATION =====

    function registerAgent(address agentAddress, string memory name) external onlyRole(ADMIN_ROLE) {
        require(agentAddress != address(0), "Invalid address");
        require(!agents[agentAddress].isActive, "Already registered");
        agents[agentAddress] = AgentInfo({
            name: name,
            isActive: true,
            registeredAt: block.timestamp,
            lastActivity: block.timestamp
        });
        emit AgentRegistered(agentAddress, name);
    }

    function submitProposalAnalysis(
        uint256 proposalId,
        string memory analysisHash,
        uint256 riskLevel,
        uint256 confidenceScore,
        bool approveForVoting
    ) external onlyRole(PROPOSAL_AGENT_ROLE) {
        Proposal storage p = proposals[proposalId];
        require(p.id != 0, "Proposal not found");
        require(p.status == ProposalStatus.Pending, "Not pending");
        require(riskLevel >= 1 && riskLevel <= 3, "Invalid risk level");
        require(confidenceScore <= 100, "Invalid confidence");

        p.agentAnalysisHash = analysisHash;
        p.riskLevel = riskLevel;
        p.confidenceScore = confidenceScore;

        if (approveForVoting && confidenceScore >= 70) {
            p.status = ProposalStatus.Active;
            p.votingStartTime = block.timestamp;
            p.votingEndTime = block.timestamp + VOTING_PERIOD;
            emit VotingStarted(proposalId, p.votingStartTime, p.votingEndTime);
        } else {
            p.status = ProposalStatus.Cancelled;
        }

        agents[msg.sender].lastActivity = block.timestamp;
        emit ProposalAnalyzed(proposalId, msg.sender, analysisHash, riskLevel);
    }

    function submitSentimentAnalysis(uint256 proposalId, string memory sentimentData) external onlyRole(VOTER_AGENT_ROLE) {
        Proposal storage p = proposals[proposalId];
        require(p.id != 0, "Proposal not found");
        p.sentimentAnalysis = sentimentData;
        agents[msg.sender].lastActivity = block.timestamp;
    }

    function submitExecutionCheck(uint256 proposalId, bool approved) external onlyRole(EXECUTION_AGENT_ROLE) {
        Proposal storage p = proposals[proposalId];
        require(p.id != 0, "Proposal not found");
        require(p.status == ProposalStatus.Approved, "Not approved for execution");
        p.executionApproved = approved;
        agents[msg.sender].lastActivity = block.timestamp;
    }

    // ===== VOTING =====

    function vote(uint256 proposalId, VoteType voteType) external whenNotPaused {
        require(voteType != VoteType.None, "Invalid vote");
        Proposal storage p = proposals[proposalId];
        require(p.id != 0, "Proposal not found");
        require(p.status == ProposalStatus.Active, "Not active");
        require(block.timestamp <= p.votingEndTime, "Voting ended");
        require(p.votes[msg.sender] == VoteType.None, "Already voted");

        Organization storage org = organizations[p.organizationId];
        uint256 memberStake = org.memberStakes[msg.sender];
        require(memberStake > 0, "Not a member");
        require(block.timestamp >= org.memberJoinTime[msg.sender] + MIN_STAKE_PERIOD, "Stake too recent");

        // Record vote
        p.votes[msg.sender] = voteType;
        p.voteWeights[msg.sender] = memberStake;

        if (voteType == VoteType.For) {
            p.forVotes += memberStake;
        } else if (voteType == VoteType.Against) {
            p.againstVotes += memberStake;
        } else {
            p.abstainVotes += memberStake;
        }

        emit VoteCast(proposalId, msg.sender, voteType, memberStake);

        // Inline check finalize: if voting window passed, finalize immediately
        if (block.timestamp > p.votingEndTime) {
            _finalizeProposal(proposalId);
        }
    }

    function finalizeVoting(uint256 proposalId) external {
        Proposal storage p = proposals[proposalId];
        require(p.id != 0, "Proposal not found");
        require(p.status == ProposalStatus.Active, "Not active");
        require(block.timestamp > p.votingEndTime, "Voting still active");
        _finalizeProposal(proposalId);
    }

    function _quorumThreshold(uint256 orgId) internal view returns (uint256) {
        uint256 total = organizations[orgId].totalStaked;
        uint256 q = total / 10; // 10%
        if (q == 0) {
            return total > 0 ? 1 : 0;
        }
        return q;
    }

    function _finalizeProposal(uint256 proposalId) internal {
        Proposal storage p = proposals[proposalId];
        if (p.status != ProposalStatus.Active) return; // only finalize active

        Organization storage org = organizations[p.organizationId];

        uint256 totalVotes = p.forVotes + p.againstVotes + p.abstainVotes;
        uint256 quorum = _quorumThreshold(p.organizationId);

        if (quorum > 0 && totalVotes >= quorum && p.forVotes > p.againstVotes) {
            p.status = ProposalStatus.Approved;
        } else {
            p.status = ProposalStatus.Rejected;
        }
    }

    // ===== EXECUTION =====

    function executeProposal(uint256 proposalId) external onlyRole(EXECUTION_AGENT_ROLE) nonReentrant whenNotPaused {
        Proposal storage p = proposals[proposalId];
        require(p.id != 0, "Proposal not found");
        require(p.status == ProposalStatus.Approved, "Not approved");
        require(p.executionApproved, "Execution not approved by agent");

        uint256 orgId = p.organizationId;
        uint256 amount = p.requestedAmount;
        address token = p.tokenAddress;

        require(organizationTreasury[orgId][token] >= amount, "Insufficient treasury");

        bool success = false;

        if (token == address(0)) {
            (bool sent, ) = payable(p.recipientAddress).call{value: amount}("");
            success = sent;
        } else {
            // will revert on failure
            IERC20(token).safeTransfer(p.recipientAddress, amount);
            success = true;
        }

        if (success) {
            p.status = ProposalStatus.Executed;
            p.executedAt = block.timestamp;
            organizationTreasury[orgId][token] -= amount;
        }

        emit ProposalExecuted(proposalId, success, amount);
    }

    // ===== TREASURY =====

    function fundTreasury(uint256 orgId, address tokenAddress, uint256 amount) external payable whenNotPaused {
        Organization storage org = organizations[orgId];
        require(org.isActive, "Organization not active");

        if (tokenAddress == address(0)) {
            require(msg.value == amount, "ETH amount mismatch");
            organizationTreasury[orgId][address(0)] += amount;
        } else {
            require(msg.value == 0, "Do not send ETH for token treasury");
            IERC20(tokenAddress).safeTransferFrom(msg.sender, address(this), amount);
            organizationTreasury[orgId][tokenAddress] += amount;
        }

        emit TreasuryFunded(orgId, tokenAddress, amount);
    }

    // ===== VIEWS =====

    function getOrganizationInfo(uint256 orgId) external view returns (
        string memory name,
        string memory description,
        address owner,
        address stakingToken,
        uint256 minStakeAmount,
        uint256 totalStaked,
        uint256 memberCount,
        bool isActive,
        uint256 createdAt
    ) {
        Organization storage org = organizations[orgId];
        return (org.name, org.description, org.owner, org.stakingToken, org.minStakeAmount, org.totalStaked, org.memberCount, org.isActive, org.createdAt);
    }

    function getMemberStake(uint256 orgId, address member) external view returns (uint256) {
        return organizations[orgId].memberStakes[member];
    }

function getProposalBasic(uint256 proposalId) external view returns (
    uint256 id,
    uint256 organizationId,
    string memory title,
    address proposer,
    ProposalStatus status
) {
    Proposal storage p = proposals[proposalId];
    return (p.id, p.organizationId, p.title, p.proposer, p.status);
}

function getProposalVoting(uint256 proposalId) external view returns (
    uint256 forVotes,
    uint256 againstVotes,
    uint256 abstainVotes,
    uint256 votingEndTime
) {
    Proposal storage p = proposals[proposalId];
    return (p.forVotes, p.againstVotes, p.abstainVotes, p.votingEndTime);
}

function getProposalAnalysis(uint256 proposalId) external view returns (
    string memory analysisHash,
    uint256 riskLevel,
    uint256 confidenceScore,
    bool executionApproved
) {
    Proposal storage p = proposals[proposalId];
    return (p.agentAnalysisHash, p.riskLevel, p.confidenceScore, p.executionApproved);
}


    function getTreasuryBalance(uint256 orgId, address tokenAddress) external view returns (uint256) {
        return organizationTreasury[orgId][tokenAddress];
    }

    function getVote(uint256 proposalId, address voter) external view returns (VoteType, uint256) {
        Proposal storage p = proposals[proposalId];
        return (p.votes[voter], p.voteWeights[voter]);
    }

    // ===== ADMIN =====

    function grantAgentRole(address agent, bytes32 role) external onlyRole(ADMIN_ROLE) {
        _grantRole(role, agent);
    }

    function pause() external onlyRole(ADMIN_ROLE) {
        _pause();
    }

    function unpause() external onlyRole(ADMIN_ROLE) {
        _unpause();
    }

    // Receive ETH (for safety)
    receive() external payable {}
}
