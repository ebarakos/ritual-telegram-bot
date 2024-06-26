// SPDX-License-Identifier: BSD-3-Clause-Clear
pragma solidity ^0.8.13;

import {Script, console2} from "forge-std/Script.sol";
import {Telegram} from "../src/Telegram.sol";

contract Deploy is Script {
    function run() public {
        // Setup wallet
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        vm.startBroadcast(deployerPrivateKey);

        // Log address
        address deployerAddress = vm.addr(deployerPrivateKey);
        console2.log("Loaded deployer: ", deployerAddress);

        address registry = 0x663F3ad617193148711d28f5334eE4Ed07016602;
        // Create consumer
        Telegram telegram = new Telegram(registry, deployerAddress);
        console2.log("Deployed SaysHello: ", address(telegram));

        // Execute
        vm.stopBroadcast();
        vm.broadcast();
    }
}
