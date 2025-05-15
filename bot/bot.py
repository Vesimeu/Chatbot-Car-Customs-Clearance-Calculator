from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from handlers import register_handlers
from convector import load_cached_rate
import os
from dotenv import load_dotenv

load_dotenv()

# Загружаем курс USD/RUB при старте
load_cached_rate()

# Инициализация бота
bot = Bot(token=os.getenv("BOT_TOKEN"))
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Регистрация хендлеров
register_handlers(dp)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)