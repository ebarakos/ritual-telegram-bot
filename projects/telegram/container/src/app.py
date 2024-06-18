from typing import Any

from flask import Flask, request
import telegram
from eth_abi import decode, encode  # type: ignore
from infernet_ml.utils.service_models import InfernetInput, JobLocation
from quart import Quart, request
import logging
import os
from dotenv import load_dotenv

from typing import Any, cast

load_dotenv()


log = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")


def create_app() -> Quart:
    app = Quart(__name__)
    @app.route("/")
    def index() -> str:
        """
        Utility endpoint to check if the service is running.
        """
        return "Telegram Bot Example"

    @app.route("/service_output", methods=["POST"])
    async def messaging() -> dict[str, Any]:   
        print(TELEGRAM_TOKEN)
        bot = telegram.Bot(TELEGRAM_TOKEN)
        # async with bot:
            # Retrieve chat_id
            # updates = (await bot.get_updates())[0]
            # await bot.send_message(text='Hi!', chat_id=updates.message.chat_id)
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
                # (message,) = decode(
                #     ["string"], bytes.fromhex(cast(str, infernet_input.data))
                # )
            case _:
                raise ValueError("Invalid source")
        log.info("message: %s", message)

        async with bot:
            updates = (await bot.get_updates())[0]
            # Retrieve chat_id
            await bot.send_message(text=message, chat_id=updates.message.chat_id)

            
    return app


if __name__ == "__main__":
    """
    Utility to run the app locally. For development purposes only.
    """
    create_app().run(port=3000)
