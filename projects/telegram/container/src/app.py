import logging
import os
import telegram
import random
from typing import Any
from infernet_ml.utils.service_models import InfernetInput, JobLocation
from infernet_client.node import NodeClient
from infernet_client.chain.subscription import Subscription
from infernet_client.chain.rpc import RPC
from quart import Quart, request
from typing import Any, cast
from time import time
from dotenv import load_dotenv
load_dotenv()


async def get_chat_id() -> str:
    global chat_id
    bot = telegram.Bot(TELEGRAM_TOKEN)
    updates = await bot.get_updates()
    if updates:
        chat_id = updates[-1].message.chat.id
        return chat_id
    else:
        print('No updates found')
        return None

log = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
CHAT_ID = os.getenv("CHAT_ID")
    
def create_app() -> Quart:
    app = Quart(__name__)
    bot = telegram.Bot(TELEGRAM_TOKEN)

    @app.route("/")
    async def index() -> str:
        """
        Utility endpoint to check if the service is running.
        """
        # print("CHAT_ID:")
        # print(await get_chat_id())
        result = await get_chat_id()
        # async with bot:
        #     await bot.send_message(text=result, chat_id=result)

        return {"CHAT_ID": result}
    
    @app.route("/new_message", methods=["POST"])
    async def new_message() -> dict[str, Any]: 
        req_data = await request.get_json()
        message = req_data.get("message")

        sub = Subscription(
            owner="0x13D69Cf7d6CE4218F646B759Dcf334D82c023d8e",
            active_at=0,
            period=0,
            frequency=1,
            redundancy=1,
            containers=["telegram"],
            lazy=False,
            verifier=ZERO_ADDRESS,
            payment_amount=0,
            payment_token=ZERO_ADDRESS,
            wallet=ZERO_ADDRESS,
        )

        client = NodeClient("http://172.17.0.1:4000")
        nonce = random.randint(0, 2**32 - 1)
        await client.request_delegated_subscription(
            subscription=sub,
            rpc=RPC("http://172.17.0.1:8545"),
            coordinator_address="0x2E983A1Ba5e8b38AAAeC4B440B9dDcFBf72E15d1",
            expiry=int(time() + 10),
            nonce=nonce,
            private_key="0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a",
            data={ "message" : "Delegated subscription message: " + message },
        )
       
        return {"status": "ok"}
    
    @app.route("/service_output", methods=["POST"])
    async def service_output() -> dict[str, Any]:   
        req_data = await request.get_json()
        """
        InfernetInput has the format:
            source: (0 on-chain, 1 off-chain)
            data: dict[str, Any]
        """
        infernet_input: InfernetInput = InfernetInput(**req_data)

        match infernet_input:
            case InfernetInput(source=JobLocation.OFFCHAIN):
                message = cast(dict[str, Any], infernet_input.data).get("message")
            case InfernetInput(source=JobLocation.ONCHAIN):
                # On-chain requests are sent as a generalized hex-string which we will
                # decode to the appropriate format.
                bytes_data = bytes.fromhex(infernet_input.data)
                message = bytes_data.decode('utf-8')
            case _:
                raise ValueError("Invalid source")
        log.info("message: %s", message)

        async with bot:
            await bot.send_message(text=message, chat_id=CHAT_ID)
        return {"output": f"Your Telegram message was: {message}"}
    return app  

if __name__ == "__main__":
    """
    Utility to run the app locally. For development purposes only.
    """
    create_app().run(port=3000)
