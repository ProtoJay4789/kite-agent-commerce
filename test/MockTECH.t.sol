// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Test} from "forge-std/Test.sol";
import {MockTECH} from "../contracts/MockTECH.sol";

contract MockTECHTest is Test {
    MockTECH public tech;
    address public owner = address(this);
    address public user = address(0x1);

    function setUp() public {
        tech = new MockTECH();
    }

    function test_constructorMintsToDeployer() public view {
        assertEq(tech.balanceOf(owner), 1_000_000 * 10 ** tech.decimals());
    }

    function test_mint() public {
        tech.mint(user, 1000);
        assertEq(tech.balanceOf(user), 1000);
    }

    function test_nameAndSymbol() public view {
        assertEq(tech.name(), "GenTech Token");
        assertEq(tech.symbol(), "TECH");
    }
}
