// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title AgentPaymentV2
 * @notice Advanced payment contract for AI agents on Kite chain
 * @dev Supports service registry, task budgets, daily limits, and emergency controls
 * @author Dmob - Kite Agent Commerce
 */
contract AgentPaymentV2 {
    // ==================== STATE VARIABLES ====================
    
    // Owner management
    address public owner;
    bool public paused;
    
    // Agent balances and limits
    mapping(address => uint256) public balances;
    mapping(address => uint256) public dailyLimits;
    mapping(address => uint256) public spentToday;
    mapping(address => uint256) public lastSpendingDay; // For automatic daily reset
    
    // Service registry
    mapping(address => ServiceInfo) public services;
    address[] public registeredServices;
    
    // Task budgets
    mapping(bytes32 => TaskBudget) public taskBudgets;
    
    // ==================== STRUCTS ====================
    
    struct ServiceInfo {
        string name;
        string description;
        uint256 basePrice;
        bool active;
        uint256 totalEarned;
        uint256 transactionCount;
    }
    
    struct TaskBudget {
        address agent;
        uint256 totalBudget;
        uint256 spent;
        uint256 startTime;
        uint256 endTime;
        string description;
        bool active;
    }
    
    // ==================== EVENTS ====================
    
    // Ownership events
    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);
    event Paused(bool isPaused);
    
    // Agent events
    event Deposited(address indexed agent, uint256 amount);
    event Withdrawn(address indexed agent, uint256 amount);
    event DailyLimitUpdated(address indexed agent, uint256 newLimit);
    event DailySpendingReset(address indexed agent);
    
    // Payment events
    event PaymentMade(
        address indexed agent, 
        address indexed service, 
        uint256 amount, 
        string purpose,
        bytes32 indexed taskId
    );
    
    // Service events
    event ServiceRegistered(address indexed service, string name, uint256 basePrice);
    event ServiceUpdated(address indexed service, bool active);
    
    // Task events
    event TaskBudgetCreated(
        bytes32 indexed taskId,
        address indexed agent,
        uint256 budget,
        string description
    );
    event TaskBudgetClosed(bytes32 indexed taskId, uint256 remaining);
    
    // ==================== ERRORS ====================
    
    error OnlyOwner();
    error ContractPaused();
    error InsufficientBalance();
    error DailyLimitExceeded();
    error TransferFailed();
    error ServiceNotRegistered();
    error ServiceNotActive();
    error InvalidTaskBudget();
    error TaskBudgetExceeded();
    error ZeroAmount();
    error ZeroAddress();
    
    // ==================== MODIFIERS ====================
    
    modifier onlyOwner() {
        if (msg.sender != owner) revert OnlyOwner();
        _;
    }
    
    modifier whenNotPaused() {
        if (paused) revert ContractPaused();
        _;
    }
    
    modifier validAddress(address addr) {
        if (addr == address(0)) revert ZeroAddress();
        _;
    }
    
    // ==================== CONSTRUCTOR ====================
    
    constructor() {
        owner = msg.sender;
        emit OwnershipTransferred(address(0), msg.sender);
    }
    
    // ==================== ADMIN FUNCTIONS ====================
    
    function transferOwnership(address newOwner) external onlyOwner validAddress(newOwner) {
        address oldOwner = owner;
        owner = newOwner;
        emit OwnershipTransferred(oldOwner, newOwner);
    }
    
    function setPaused(bool _paused) external onlyOwner {
        paused = _paused;
        emit Paused(_paused);
    }
    
    // ==================== AGENT FUNCTIONS ====================
    
    function deposit() external payable whenNotPaused {
        if (msg.value == 0) revert ZeroAmount();
        
        balances[msg.sender] += msg.value;
        emit Deposited(msg.sender, msg.value);
    }
    
    function withdraw(uint256 amount) external whenNotPaused {
        if (amount == 0) revert ZeroAmount();
        if (balances[msg.sender] < amount) revert InsufficientBalance();
        
        balances[msg.sender] -= amount;
        
        (bool success, ) = msg.sender.call{value: amount}("");
        if (!success) revert TransferFailed();
        
        emit Withdrawn(msg.sender, amount);
    }
    
    function setDailyLimit(uint256 limit) external whenNotPaused {
        dailyLimits[msg.sender] = limit;
        emit DailyLimitUpdated(msg.sender, limit);
    }
    
    function resetDailySpending() external whenNotPaused {
        spentToday[msg.sender] = 0;
        lastSpendingDay[msg.sender] = block.timestamp / 1 days;
        emit DailySpendingReset(msg.sender);
    }
    
    // ==================== SERVICE REGISTRY ====================
    
    function registerService(
        address serviceAddress,
        string calldata name,
        string calldata description,
        uint256 basePrice
    ) external onlyOwner validAddress(serviceAddress) {
        services[serviceAddress] = ServiceInfo({
            name: name,
            description: description,
            basePrice: basePrice,
            active: true,
            totalEarned: 0,
            transactionCount: 0
        });
        
        registeredServices.push(serviceAddress);
        emit ServiceRegistered(serviceAddress, name, basePrice);
    }
    
    function updateServiceStatus(address serviceAddress, bool active) external onlyOwner {
        if (bytes(services[serviceAddress].name).length == 0) revert ServiceNotRegistered();
        services[serviceAddress].active = active;
        emit ServiceUpdated(serviceAddress, active);
    }
    
    // ==================== TASK BUDGETS ====================
    
    function createTaskBudget(
        bytes32 taskId,
        uint256 budget,
        uint256 durationDays,
        string calldata description
    ) external whenNotPaused {
        if (budget == 0) revert ZeroAmount();
        if (balances[msg.sender] < budget) revert InsufficientBalance();
        
        // Reserve the budget
        balances[msg.sender] -= budget;
        
        taskBudgets[taskId] = TaskBudget({
            agent: msg.sender,
            totalBudget: budget,
            spent: 0,
            startTime: block.timestamp,
            endTime: block.timestamp + (durationDays * 1 days),
            description: description,
            active: true
        });
        
        emit TaskBudgetCreated(taskId, msg.sender, budget, description);
    }
    
    function closeTaskBudget(bytes32 taskId) external whenNotPaused {
        TaskBudget storage task = taskBudgets[taskId];
        
        if (task.agent != msg.sender) revert InvalidTaskBudget();
        if (!task.active) revert InvalidTaskBudget();
        
        uint256 remaining = task.totalBudget - task.spent;
        task.active = false;
        
        // Return remaining budget to agent
        balances[msg.sender] += remaining;
        
        emit TaskBudgetClosed(taskId, remaining);
    }
    
    // ==================== PAYMENT FUNCTIONS ====================
    
    function pay(address service, uint256 amount, string calldata purpose) external whenNotPaused {
        _processPayment(service, amount, purpose, bytes32(0));
    }
    
    function payFromTask(
        address service,
        uint256 amount,
        string calldata purpose,
        bytes32 taskId
    ) public whenNotPaused validAddress(service) {
        _processPayment(service, amount, purpose, taskId);
    }
    
    function _processPayment(
        address service,
        uint256 amount,
        string calldata purpose,
        bytes32 taskId
    ) internal {
        if (amount == 0) revert ZeroAmount();
        
        // Check if paying from task budget or general balance
        bool isTaskPayment = taskId != bytes32(0);
        
        if (isTaskPayment) {
            TaskBudget storage task = taskBudgets[taskId];
            
            if (!task.active) revert InvalidTaskBudget();
            if (task.agent != msg.sender) revert InvalidTaskBudget();
            if (block.timestamp > task.endTime) revert InvalidTaskBudget();
            if (task.spent + amount > task.totalBudget) revert TaskBudgetExceeded();
            
            task.spent += amount;
        } else {
            // Check daily limit with automatic reset
            uint256 currentDay = block.timestamp / 1 days;
            if (lastSpendingDay[msg.sender] < currentDay) {
                spentToday[msg.sender] = 0;
                lastSpendingDay[msg.sender] = currentDay;
            }
            
            if (balances[msg.sender] < amount) revert InsufficientBalance();
            if (spentToday[msg.sender] + amount > dailyLimits[msg.sender]) revert DailyLimitExceeded();
            
            balances[msg.sender] -= amount;
            spentToday[msg.sender] += amount;
        }
        
        // Update service stats if registered
        if (bytes(services[service].name).length > 0) {
            services[service].totalEarned += amount;
            services[service].transactionCount += 1;
        }
        
        // Transfer funds
        (bool success, ) = service.call{value: amount}("");
        if (!success) revert TransferFailed();
        
        emit PaymentMade(msg.sender, service, amount, purpose, taskId);
    }
    
    // ==================== VIEW FUNCTIONS ====================
    
    function getBalance() external view returns (uint256) {
        return balances[msg.sender];
    }
    
    function getDailySpending() external view returns (uint256 spent, uint256 limit, uint256 remaining) {
        uint256 currentDay = block.timestamp / 1 days;
        uint256 currentSpent = spentToday[msg.sender];
        
        // If it's a new day, spending is reset
        if (lastSpendingDay[msg.sender] < currentDay) {
            currentSpent = 0;
        }
        
        return (
            currentSpent,
            dailyLimits[msg.sender],
            dailyLimits[msg.sender] - currentSpent
        );
    }
    
    function getTaskBudget(bytes32 taskId) external view returns (
        address agent,
        uint256 totalBudget,
        uint256 spent,
        uint256 remaining,
        uint256 endTime,
        bool active
    ) {
        TaskBudget storage task = taskBudgets[taskId];
        return (
            task.agent,
            task.totalBudget,
            task.spent,
            task.totalBudget - task.spent,
            task.endTime,
            task.active
        );
    }
    
    function getServiceInfo(address serviceAddress) external view returns (
        string memory name,
        string memory description,
        uint256 basePrice,
        bool active,
        uint256 totalEarned,
        uint256 transactionCount
    ) {
        ServiceInfo storage info = services[serviceAddress];
        return (
            info.name,
            info.description,
            info.basePrice,
            info.active,
            info.totalEarned,
            info.transactionCount
        );
    }
    
    function getRegisteredServicesCount() external view returns (uint256) {
        return registeredServices.length;
    }
    
    // ==================== RECEIVE FUNCTION ====================
    
    receive() external payable {
        // Allow direct transfers to the contract
        balances[msg.sender] += msg.value;
        emit Deposited(msg.sender, msg.value);
    }
}