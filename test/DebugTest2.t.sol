// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../contracts/AgentPaymentV2.sol";

contract DebugTest2 is Test {
    AgentPaymentV2 public paymentContract;
    
    address public agent1 = address(0x1);
    address public service1 = address(0x3);
    
    function setUp() public {
        paymentContract = new AgentPaymentV2();
        vm.deal(agent1, 10 ether);
    }
    
    function testDebugDailyReset() public {
        // Deposit
        vm.prank(agent1);
        paymentContract.deposit{value: 1 ether}();
        
        // Set daily limit
        vm.prank(agent1);
        paymentContract.setDailyLimit(0.5 ether);
        
        // Make payment
        vm.prank(agent1);
        paymentContract.pay(service1, 0.1 ether, "Test");
        
        console.log("After payment:");
        console.log("  spentToday:", paymentContract.spentToday(agent1));
        console.log("  lastSpendingDay:", paymentContract.lastSpendingDay(agent1));
        console.log("  block.timestamp:", block.timestamp);
        console.log("  currentDay:", block.timestamp / 1 days);
        
        // Warp to next day
        vm.warp(block.timestamp + 1 days);
        
        console.log("After warp:");
        console.log("  block.timestamp:", block.timestamp);
        console.log("  currentDay:", block.timestamp / 1 days);
        console.log("  lastSpendingDay:", paymentContract.lastSpendingDay(agent1));
        
        // Check getDailySpending
        (uint256 spent, uint256 limit, uint256 remaining) = paymentContract.getDailySpending();
        
        console.log("getDailySpending:");
        console.log("  spent:", spent);
        console.log("  limit:", limit);
        console.log("  remaining:", remaining);
    }
}