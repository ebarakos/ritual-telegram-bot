from typing import Any

import telegram
from eth_abi import decode, encode  # type: ignore
from infernet_ml.utils.service_models import InfernetInput, JobLocation
from infernet_client.node import NodeClient
from infernet_client.chain.subscription import Subscription
from infernet_client.chain.rpc import RPC
from quart import Quart, request
import logging
import os
from dotenv import load_dotenv
from typing import Any, cast
from time import time
load_dotenv()
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import requests


log = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

async def send(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = 'http://172.17.0.1:3000/new_message'
    log.info(update.message.text)
    data = {
        'message': update.message.text,
    }

    response = requests.post(url, json=data)
    print('Status Code:', response.status_code)
    print('Response Text:', response.text)
    # await update.message.reply_text(update.message.text)

def create_app() -> Quart:
    app = Quart(__name__)

    bot_app = Application.builder().token(TELEGRAM_TOKEN).build()
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send))
    bot_app.run_polling(allowed_updates=Update.ALL_TYPES)

    return app  

if __name__ == "__main__":
    """
    Utility to run the app locally. For development purposes only.
    """
    create_app().run(port=3001)

    
