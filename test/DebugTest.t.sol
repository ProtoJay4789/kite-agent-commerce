// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../contracts/AgentPaymentV2.sol";

contract DebugTest is Test {
    AgentPaymentV2 public paymentContract;
    
    address public agent1 = address(0x1);
    address public service1 = address(0x3);
    
    function setUp() public {
        paymentContract = new AgentPaymentV2();
        vm.deal(agent1, 10 ether);
    }
    
    function testDebug() public {
        // Deposit
        vm.prank(agent1);
        paymentContract.deposit{value: 1 ether}();
        
        // Check balance
        console.log("Balance after deposit:", paymentContract.balances(agent1));
        
        // Set daily limit
        vm.prank(agent1);
        paymentContract.setDailyLimit(0.5 ether);
        
        console.log("Daily limit:", paymentContract.dailyLimits(agent1));
        
        // Try to make payment
        vm.prank(agent1);
        try paymentContract.pay(service1, 0.5 ether, "Test") {
            console.log("Payment succeeded");
        } catch (bytes memory reason) {
            console.log("Payment failed");
        }
    }
}