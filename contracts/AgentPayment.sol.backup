// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title AgentPayment
 * @notice Simple payment contract for AI agents on Kite chain
 * @dev Agents can deposit, spend within limits, and settle transactions
 */
contract AgentPayment {
    mapping(address => uint256) public balances;
    mapping(address => uint256) public dailyLimits;
    mapping(address => uint256) public spentToday;

    event Deposited(address indexed agent, uint256 amount);
    event PaymentMade(address indexed agent, address indexed recipient, uint256 amount, string purpose);
    event LimitUpdated(address indexed agent, uint256 newLimit);

    function deposit() external payable {
        balances[msg.sender] += msg.value;
        emit Deposited(msg.sender, msg.value);
    }

    function setDailyLimit(uint256 limit) external {
        dailyLimits[msg.sender] = limit;
        emit LimitUpdated(msg.sender, limit);
    }

    function pay(address recipient, uint256 amount, string calldata purpose) external {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        require(spentToday[msg.sender] + amount <= dailyLimits[msg.sender], "Daily limit exceeded");

        balances[msg.sender] -= amount;
        spentToday[msg.sender] += amount;

        (bool success, ) = recipient.call{value: amount}("");
        require(success, "Transfer failed");

        emit PaymentMade(msg.sender, recipient, amount, purpose);
    }

    function resetDailySpending() external {
        spentToday[msg.sender] = 0;
    }

    function getBalance() external view returns (uint256) {
        return balances[msg.sender];
    }
}
