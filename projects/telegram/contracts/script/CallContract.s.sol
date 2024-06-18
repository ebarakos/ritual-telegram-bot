// SPDX-License-Identifier: BSD-3-Clause-Clear
pragma solidity ^0.8.0;

import {Script, console2} from "forge-std/Script.sol";
import {SaysGM} from "../src/SaysGM.sol";


contract CallContract is Script {
    string defaultMessage = "Nothing to say";

    function run() public {
        // Setup wallet
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        string memory message = vm.envOr("message", defaultMessage);

        vm.startBroadcast(deployerPrivateKey);

        SaysGM saysGm = SaysGM(0x13D69Cf7d6CE4218F646B759Dcf334D82c023d8e);

        saysGm.sayGM(message);

        vm.stopBroadcast();
    }
}
