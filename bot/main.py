import os
from dotenv import load_dotenv
from telegram.ext import Application
from bot.handlers import get_conversation_handler

def main():
    load_dotenv()
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_TOKEN не найден в .env файле")

    application = Application.builder().token(token).build()
    application.add_handler(get_conversation_handler())
    application.run_polling(allowed_updates=["message", "callback_query"])

if __name__ == "__main__":
    main()