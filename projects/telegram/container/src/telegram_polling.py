import logging
import os
import requests
from quart import Quart
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv
load_dotenv()

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

    
