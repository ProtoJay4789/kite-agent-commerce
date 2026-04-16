// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../contracts/AgentPaymentV2.sol";

contract AgentPaymentV2Test is Test {
    AgentPaymentV2 public paymentContract;
    
    address public owner = address(this);
    address public agent1 = address(0x1);
    address public agent2 = address(0x2);
    address public service1 = address(0x3);
    address public service2 = address(0x4);
    
    uint256 constant DEPOSIT_AMOUNT = 1 ether;
    uint256 constant DAILY_LIMIT = 0.5 ether;
    uint256 constant PAYMENT_AMOUNT = 0.1 ether;
    
    function setUp() public {
        paymentContract = new AgentPaymentV2();
        
        // Fund agents
        vm.deal(agent1, 10 ether);
        vm.deal(agent2, 10 ether);
    }
    
    function testInitialState() public {
        assertEq(paymentContract.owner(), owner);
        assertFalse(paymentContract.paused());
    }
    
    function testDeposit() public {
        vm.prank(agent1);
        paymentContract.deposit{value: DEPOSIT_AMOUNT}();
        
        assertEq(paymentContract.balances(agent1), DEPOSIT_AMOUNT);
    }
    
    function testWithdraw() public {
        // Deposit first
        vm.prank(agent1);
        paymentContract.deposit{value: DEPOSIT_AMOUNT}();
        
        uint256 balanceBefore = agent1.balance;
        
        // Withdraw
        vm.prank(agent1);
        paymentContract.withdraw(PAYMENT_AMOUNT);
        
        assertEq(paymentContract.balances(agent1), DEPOSIT_AMOUNT - PAYMENT_AMOUNT);
        assertEq(agent1.balance, balanceBefore + PAYMENT_AMOUNT);
    }
    
    function testSetDailyLimit() public {
        vm.prank(agent1);
        paymentContract.setDailyLimit(DAILY_LIMIT);
        
        assertEq(paymentContract.dailyLimits(agent1), DAILY_LIMIT);
    }
    
    function testPayment() public {
        // Setup
        vm.prank(agent1);
        paymentContract.deposit{value: DEPOSIT_AMOUNT}();
        
        vm.prank(agent1);
        paymentContract.setDailyLimit(DAILY_LIMIT);
        
        uint256 serviceBalanceBefore = service1.balance;
        
        // Make payment
        vm.prank(agent1);
        paymentContract.pay(service1, PAYMENT_AMOUNT, "Test payment");
        
        assertEq(paymentContract.balances(agent1), DEPOSIT_AMOUNT - PAYMENT_AMOUNT);
        assertEq(paymentContract.spentToday(agent1), PAYMENT_AMOUNT);
        assertEq(service1.balance, serviceBalanceBefore + PAYMENT_AMOUNT);
    }
    
    function testDailyLimitExceeded() public {
        // Setup with enough balance
        vm.prank(agent1);
        paymentContract.deposit{value: DEPOSIT_AMOUNT}();
        
        vm.prank(agent1);
        paymentContract.setDailyLimit(DAILY_LIMIT);
        
        // Try to exceed daily limit (but within balance)
        vm.prank(agent1);
        vm.expectRevert(AgentPaymentV2.DailyLimitExceeded.selector);
        paymentContract.pay(service1, DAILY_LIMIT + 1 wei, "Over limit");
    }
    
    function testResetDailySpending() public {
        // Setup and make payment
        vm.prank(agent1);
        paymentContract.deposit{value: DEPOSIT_AMOUNT}();
        
        vm.prank(agent1);
        paymentContract.setDailyLimit(DAILY_LIMIT);
        
        vm.prank(agent1);
        paymentContract.pay(service1, PAYMENT_AMOUNT, "Test payment");
        
        assertEq(paymentContract.spentToday(agent1), PAYMENT_AMOUNT);
        
        // Reset spending
        vm.prank(agent1);
        paymentContract.resetDailySpending();
        
        assertEq(paymentContract.spentToday(agent1), 0);
    }
    
    function testServiceRegistry() public {
        // Register service
        vm.prank(owner);
        paymentContract.registerService(service1, "Test Service", "A test service", 0.01 ether);
        
        (string memory name, string memory description, uint256 basePrice, bool active, , ) = paymentContract.getServiceInfo(service1);
        
        assertEq(name, "Test Service");
        assertEq(description, "A test service");
        assertEq(basePrice, 0.01 ether);
        assertTrue(active);
    }
    
    function testTaskBudget() public {
        // Setup
        vm.prank(agent1);
        paymentContract.deposit{value: DEPOSIT_AMOUNT}();
        
        bytes32 taskId = keccak256("task1");
        
        // Create task budget
        vm.prank(agent1);
        paymentContract.createTaskBudget(taskId, PAYMENT_AMOUNT * 2, 7 days, "Test task");
        
        // Check task budget
        (address taskAgent, uint256 totalBudget, uint256 spent, uint256 remaining, , bool active) = paymentContract.getTaskBudget(taskId);
        
        assertEq(taskAgent, agent1);
        assertEq(totalBudget, PAYMENT_AMOUNT * 2);
        assertEq(spent, 0);
        assertEq(remaining, PAYMENT_AMOUNT * 2);
        assertTrue(active);
        
        // Make payment from task
        vm.prank(agent1);
        paymentContract.payFromTask(service1, PAYMENT_AMOUNT, "Task payment", taskId);
        
        (, , spent, remaining, , ) = paymentContract.getTaskBudget(taskId);
        assertEq(spent, PAYMENT_AMOUNT);
        assertEq(remaining, PAYMENT_AMOUNT);
    }
    
    function testPauseContract() public {
        // Pause contract
        vm.prank(owner);
        paymentContract.setPaused(true);
        
        assertTrue(paymentContract.paused());
        
        // Try to deposit when paused
        vm.prank(agent1);
        vm.expectRevert(AgentPaymentV2.ContractPaused.selector);
        paymentContract.deposit{value: DEPOSIT_AMOUNT}();
    }
    
    function testTransferOwnership() public {
        address newOwner = address(0x99);
        
        vm.prank(owner);
        paymentContract.transferOwnership(newOwner);
        
        assertEq(paymentContract.owner(), newOwner);
    }
    
    function testAutomaticDailyReset() public {
        // Setup
        vm.prank(agent1);
        paymentContract.deposit{value: DEPOSIT_AMOUNT}();
        
        vm.prank(agent1);
        paymentContract.setDailyLimit(DAILY_LIMIT);
        
        // Make payment
        vm.prank(agent1);
        paymentContract.pay(service1, PAYMENT_AMOUNT, "Test payment");
        
        assertEq(paymentContract.spentToday(agent1), PAYMENT_AMOUNT);
        
        // Warp to next day
        vm.warp(block.timestamp + 1 days);
        
        // Check that spending is automatically reset
        (uint256 spent, , uint256 remaining) = paymentContract.getDailySpending();
        assertEq(spent, 0);
        assertEq(remaining, DAILY_LIMIT);
    }
}