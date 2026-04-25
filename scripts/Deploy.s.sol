// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Script} from "forge-std/Script.sol";
import {console2} from "forge-std/console2.sol";
import {AgentEscrow} from "../contracts/AgentEscrow.sol";
import {TECHPaymentRouter} from "../contracts/TECHPaymentRouter.sol";
import {MockTECH} from "../contracts/MockTECH.sol";

/**
 * @title DeployScript
 * @notice Kite AI Testnet (Chain ID 2368) deployment script
 * @dev Uses foundry's broadcast to deploy.
 */
contract DeployScript is Script {
    // Kite Testnet: USDC contract address (verified on explorer)
    address constant USDC = 0x2d16C0dc617dCF743f55A3bB42fDE4A0E640A5b5;

    // Deployer address (used as AI validator & treasury for testnet)
    address constant DEPLOYER = 0xE00a46132Fd03456cEcd05de8C69F43C5138Db95;

    // Burn ratio: 5000 = 50%, 7000 = 70% (range: 1000-9000)
    uint256 constant INITIAL_BURN_RATIO = 5000;

    // Discount: 2500 = 25% cheaper than USDC (range: 0-5000)
    uint256 constant INITIAL_DISCOUNT = 2500;

    function run() public {
        uint256 chainId = block.chainid;
        require(chainId == 2368, "Wrong chain! Expected Kite Testnet (2368)");

        uint256 deployerPK = vm.envUint("DEPLOYER_PRIVATE_KEY");
        vm.startBroadcast(deployerPK);

        // Deploy MockTECH token (faucetable for demo)
        MockTECH techToken = new MockTECH();
        console2.log("MockTECH deployed at:", address(techToken));

        // Deploy AgentEscrow
        AgentEscrow agentEscrow = new AgentEscrow(USDC, DEPLOYER);
        console2.log("AgentEscrow deployed at:", address(agentEscrow));

        // Deploy TECHPaymentRouter
        TECHPaymentRouter techRouter = new TECHPaymentRouter(
            address(techToken),
            DEPLOYER,
            INITIAL_BURN_RATIO,
            INITIAL_DISCOUNT
        );
        console2.log("TECHPaymentRouter deployed at:", address(techRouter));

        vm.stopBroadcast();

        console2.log("==============================================");
        console2.log("KITE AI TESTNET DEPLOYMENT COMPLETE");
        console2.log("==============================================");
        console2.log("Chain ID:            ", chainId);
        console2.log("MockTECH:            ", address(techToken));
        console2.log("AgentEscrow:         ", address(agentEscrow));
        console2.log("TECHPaymentRouter:   ", address(techRouter));
        console2.log("Deployer:            ", DEPLOYER);
        console2.log("==============================================");
    }
}
