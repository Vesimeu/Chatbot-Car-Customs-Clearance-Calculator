import requests
import json
import os
from datetime import datetime
import schedule
import time
import logging

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Путь к файлу для кэширования курса
CACHE_FILE = "usd_to_rub.json"
# URL для ExchangeRate-API (без ключа, обновление раз в 24 часа)
API_URL = "https://open.exchangerate-api.com/v6/latest"

# Инициализация курса по умолчанию
USD_TO_RUB = 85.0  # Запасное значение, если API недоступен

def load_cached_rate():
    """Загружает кэшированный курс из файла."""
    global USD_TO_RUB
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r') as f:
                data = json.load(f)
                # Проверяем, что данные свежие (сегодняшние)
                cache_date = datetime.strptime(data['date'], '%Y-%m-%d')
                if cache_date.date() == datetime.now().date():
                    USD_TO_RUB = data['rate']
                    logger.info(f"Загружен кэшированный курс USD/RUB: {USD_TO_RUB}")
                else:
                    logger.info("Кэш устарел, запрашиваем новый курс")
                    update_exchange_rate()
        else:
            logger.info("Кэш не найден, запрашиваем новый курс")
            update_exchange_rate()
    except Exception as e:
        logger.error(f"Ошибка при загрузке кэша: {e}")
        USD_TO_RUB = 90.0  # Запасное значение

def save_cached_rate(rate):
    """Сохраняет курс в кэш."""
    try:
        data = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'rate': rate
        }
        with open(CACHE_FILE, 'w') as f:
            json.dump(data, f)
        logger.info(f"Кэширован курс USD/RUB: {rate}")
    except Exception as e:
        logger.error(f"Ошибка при сохранении кэша: {e}")

def update_exchange_rate():
    """Обновляет курс USD/RUB через API."""
    global USD_TO_RUB
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            data = response.json()
            if data['result'] == 'success':
                USD_TO_RUB = data['rates']['RUB']
                save_cached_rate(USD_TO_RUB)
                logger.info(f"Успешно обновлён курс USD/RUB: {USD_TO_RUB}")
            else:
                logger.error("Ошибка в данных API")
        else:
            logger.error(f"Ошибка API: статус {response.status_code}")
    except Exception as e:
        logger.error(f"Ошибка при запросе к API: {e}")
        USD_TO_RUB = 90.0  # Запасное значение

def schedule_update():
    """Планирует ежедневное обновление курса."""
    schedule.every().day.at("09:00").do(update_exchange_rate)
    logger.info("Запланировано ежедневное обновление курса в 09:00")
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    # Загружаем курс при запуске
    load_cached_rate()
    # Запускаем планировщик в фоновом режиме
    import threading
    scheduler_thread = threading.Thread(target=schedule_update, daemon=True)
    scheduler_thread.start()