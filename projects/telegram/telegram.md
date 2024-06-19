# Hello, World!

Welcome to the first tutorial of Infernet! In this tutorial we will guide you through the process of setting up and
running an Infernet Node, and then demonstrate how to create and monitor off-chain compute jobs and on-chain subscriptions.

To interact with infernet, one could either create a job by accessing an infernet node directly through it's API (we'll
refer to this as an off-chain job), or by creating a subscription on-chain (we'll refer to this as an on-chain job).

## Requesting an off-chain job: Hello World!

This project is a simple [flask-app](container/src/app.py) that is compatible with `infernet`, and simply
[echoes what you send to it](container/src/app.py#L16).

### Install Docker & Verify Installation

To run this, you'll need to have docker installed. You can find instructions for installing docker [here](https://docs.docker.com/install/).

After installing & running docker, you can verify that the docker daemon is running by running the following command:

```bash copy
docker --version
# Docker version 25.0.2, build 29cf629
```

### Clone the starter repository

```bash copy
# Clone locally
git clone --recurse-submodules https://github.com/ritual-net/infernet-container-starter
# Navigate to the repository
cd infernet-container-starter
```

### Build the `telegram` container

Once inside the repository directory, you can run a simple command to build the `telegram` container:

```bash copy
make build-container project=telegram
```

### Running Locally

Then, from the top-level project directory, Run the following make command:

```
make deploy-container project=telegram
```

This will deploy an infernet node along with the `telegram` image.

### Creating an off-chain job through the API

You can create an off-chain job by posting to the `node` directly.

```bash
curl -X POST "http://127.0.0.1:4000/api/jobs" \
     -H "Content-Type: application/json" \
     -d '{"containers":["telegram"], "data": {"message": "Off-chain message"}}'
# returns
{"id":"d5281dd5-c4f4-4523-a9c2-266398e06007"}
```

This will return the id of that job.

### Getting the status/result/errors of a job

You can check the status of a job like so:

```bash
curl -X GET "http://127.0.0.1:4000/api/jobs?id=d5281dd5-c4f4-4523-a9c2-266398e06007"
# returns
[{"id":"d5281dd5-c4f4-4523-a9c2-266398e06007", "result":{"container":"telegram","output": {"output":"Hello, your Telegram message was: {'source': 1, 'data': {'message': 'Off-chain message'}}"}} ,"status":"success"}]
```

### Configuration

This project already comes with a pre-filled config file. The config file for the telegram project is located
[here](container/config.json):

```bash
projects/telegram/container/config.json
```

## Requesting an on-chain job

In this section we'll go over how to request an on-chain job in a local anvil node.

### Infernet's Anvil Testnet

To request an on-chain job, you'll need to deploy contracts using the infernet sdk.
We already have a public [anvil node](https://hub.docker.com/r/ritualnetwork/infernet-anvil) docker image which has the
corresponding infernet sdk contracts deployed, along with a node that has
registered itself to listen to on-chain subscription events.

- Registry Address: `0x663F3ad617193148711d28f5334eE4Ed07016602`
- Node Address: `0x70997970C51812dc3A010C7d01b50e0d17dc79C8` (This is the second account in the anvil's accounts.)

### Deploying Infernet Node & Infernet's Anvil Testnet

This step is similar to the section above:

```bash
docker logs -f infernet-anvil
```

In another terminal, run `docker container ls`, you should see something like this

```bash
CONTAINER ID   IMAGE                                            COMMAND                  CREATED          STATUS          PORTS                                       NAMES
0a24afba2426   ritualnetwork/telegram-polling:latest            "/start.sh --bind=0.…"   11 minutes ago   Up 11 minutes   3001/tcp, 0.0.0.0:3001->3000/tcp            telegram-polling
fecb3d05287a   ritualnetwork/example-telegram-infernet:latest   "/start.sh --bind=0.…"   11 minutes ago   Up 11 minutes   0.0.0.0:3000->3000/tcp                      telegram
8891cd193e72   ritualnetwork/infernet-node:1.0.0                "/app/entrypoint.sh"     11 minutes ago   Up 11 minutes   0.0.0.0:4000->4000/tcp                      infernet-node
71ab3112cb7c   redis:latest                                     "docker-entrypoint.s…"   11 minutes ago   Up 11 minutes   0.0.0.0:6379->6379/tcp, :::6379->6379/tcp   deploy-redis-1
f0301578d8d4   ritualnetwork/infernet-anvil:1.0.0               "anvil --host 0.0.0.…"   11 minutes ago   Up 11 minutes   0.0.0.0:8545->3000/tcp, :::8545->3000/tcp   infernet-anvil
8593c6c80c34   fluent/fluent-bit:latest                         "/fluent-bit/bin/flu…"   11 minutes ago   Up 11 minutes   2020/tcp, 24224/tcp                         deploy-fluentbit-1
```

You can see that the anvil node is running on port `8545`, and the infernet
node is running on port `4000`. Same as before.

### Deploying Consumer Contracts

We have a [sample forge project](./contracts) which contains
a simple consumer contract, [`Telegram`](contracts/src/Telegram.sol).
All this contract does is to request a job from the infernet node, and upon receiving
the result, it will use the `forge` console to print the result.

**Anvil Logs**: First, it's useful to look at the logs of the anvil node to see what's going on. In
a new terminal, run `docker logs -f infernet-anvil`.

**Deploying the contracts**: In another terminal, run the following command:

```bash
project=telegram make deploy-contracts
```

You should be able to see the following logs in the anvil logs:

```bash
eth_sendRawTransaction
eth_getTransactionReceipt

    Transaction: 0x23ca6b1d1823ad5af175c207c2505112f60038fc000e1e22509816fa29a3afd6
    Contract created: 0x13D69Cf7d6CE4218F646B759Dcf334D82c023d8e
    Gas used: 476669

    Block Number: 1
    Block Hash: 0x6b026b70fbe97b4a733d4812ccd6e8e25899a1f6c622430c3fb07a2e5c5c96b7
    Block Time: "Wed, 17 Jan 2024 22:17:31 +0000"

eth_getTransactionByHash
eth_getTransactionReceipt
eth_blockNumber
```

We can see that a new contract has been created at `0x13D69Cf7d6CE4218F646B759Dcf334D82c023d8e`.
That's the address of the `Telegram` contract.

### Calling the contract

Now, let's call the contract. In the same terminal, run the following command:

```bash
project=telegram make call-contract message="Off-chain message"
```

You should first see that a transaction was sent to the `Telegram` contract:

```bash
eth_getTransactionReceipt

    Transaction: 0xe56b5b6ac713a978a1631a44d6a0c9eb6941dce929e1b66b4a2f7a61b0349d65
    Gas used: 123323

    Block Number: 2
    Block Hash: 0x3d6678424adcdecfa0a8edd51e014290e5f54ee4707d4779e710a2a4d9867c08
    Block Time: "Wed, 17 Jan 2024 22:18:39 +0000"
eth_getTransactionByHash

```

Then, right after that you should see another transaction submitted by the `node`,
which is the result of the job request:

```bash
eth_chainId
eth_sendRawTransaction


_____  _____ _______ _    _         _
|  __ \|_   _|__   __| |  | |  /\   | |
| |__) | | |    | |  | |  | | /  \  | |
|  _  /  | |    | |  | |  | |/ /\ \ | |
| | \ \ _| |_   | |  | |__| / ____ \| |____
|_|  \_\_____|  |_|   \____/_/    \_\______|


subscription Id 1
interval 1
redundancy 1
node 0x70997970C51812dc3A010C7d01b50e0d17dc79C8
input:
0x
output:
0x000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000001737b276f7574707574273a2027596f75722054656c656772616d206d657373616765207761733a205c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c783030205c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7831314f66662d636861696e206d6573736167655c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c7830305c783030277d00000000000000000000000000
decoded output:  {'output': 'Your Telegram message was: \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x11Off-chain message\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'}
proof:
0x

    Transaction: 0x949351d02e2c7f50ced2be06d14ca4311bd470ec80b135a2ce78a43f43e60d3d
    Gas used: 94275

    Block Number: 3
    Block Hash: 0x57ed0cf39e3fb3a91a0d8baa5f9cb5d2bdc1875f2ad5d6baf4a9466f522df354
    Block Time: "Wed, 17 Jan 2024 22:18:40 +0000"


eth_blockNumber
eth_newFilter

```

We can see that the address of the `node` matches the address of the node in
our ritual anvil node.

### Next Steps

To learn more about on-chain requests, check out the following resources:

1. [Tutorial](contracts/Tutorial.md) on this project's consumer smart contracts.
2. [Infernet Callback Consumer Tutorial](https://docs.ritual.net/infernet/sdk/consumers/Callback)
3. [Infernet Nodes Docoumentation](https://docs.ritual.net/infernet/node/introduction)
4. [Infernet-Compatible Containers](https://docs.ritual.net/infernet/node/containers)
