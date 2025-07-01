import requests
import json
import os
from datetime import datetime
import schedule
import time
import logging
import threading
from usage_tracker import clean_old_usage_data  # Импортируем для очистки

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Путь к файлу для кэширования курса
CACHE_FILE = "usd_to_rub.json"
CNY_CACHE_FILE = "cny_to_rub.json"
# URL для ExchangeRate-API
API_URL = "https://open.exchangerate-api.com/v6/latest"

# Инициализация курса по умолчанию
USD_TO_RUB = 85.0
CNY_TO_RUB = 11.0

def load_cached_rate():
    """Загружает кэшированные курсы из файлов."""
    global USD_TO_RUB, CNY_TO_RUB
    try:
        # USD
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r') as f:
                data = json.load(f)
                cache_date = datetime.strptime(data['date'], '%Y-%m-%d')
                if cache_date.date() == datetime.now().date():
                    USD_TO_RUB = data['rate']
                    logger.info(f"Загружен кэшированный курс USD/RUB: {USD_TO_RUB}")
                else:
                    logger.info("Кэш USD устарел, запрашиваем новый курс")
                    update_exchange_rate()
        else:
            logger.info("Кэш USD не найден, запрашиваем новый курс")
            update_exchange_rate()
        # CNY
        if os.path.exists(CNY_CACHE_FILE):
            with open(CNY_CACHE_FILE, 'r') as f:
                data = json.load(f)
                cache_date = datetime.strptime(data['date'], '%Y-%m-%d')
                if cache_date.date() == datetime.now().date():
                    CNY_TO_RUB = data['rate']
                    logger.info(f"Загружен кэшированный курс CNY/RUB: {CNY_TO_RUB}")
                else:
                    logger.info("Кэш CNY устарел, запрашиваем новый курс")
                    update_exchange_rate()
        else:
            logger.info("Кэш CNY не найден, запрашиваем новый курс")
            update_exchange_rate()
    except Exception as e:
        logger.error(f"Ошибка при загрузке кэша: {e}")
        USD_TO_RUB = 85.0
        CNY_TO_RUB = 12.0

def save_cached_rate(rate, currency="USD"):
    """Сохраняет курс в кэш."""
    try:
        data = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'rate': rate
        }
        if currency == "USD":
            with open(CACHE_FILE, 'w') as f:
                json.dump(data, f)
            logger.info(f"Кэширован курс USD/RUB: {rate}")
        elif currency == "CNY":
            with open(CNY_CACHE_FILE, 'w') as f:
                json.dump(data, f)
            logger.info(f"Кэширован курс CNY/RUB: {rate}")
    except Exception as e:
        logger.error(f"Ошибка при сохранении кэша: {e}")

def update_exchange_rate():
    """Обновляет курсы USD/RUB и CNY/RUB через API."""
    global USD_TO_RUB, CNY_TO_RUB
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            data = response.json()
            if data['result'] == 'success':
                USD_TO_RUB = data['rates']['RUB']
                save_cached_rate(USD_TO_RUB, currency="USD")
                logger.info(f"Успешно обновлён курс USD/RUB: {USD_TO_RUB}")
                if 'CNY' in data['rates']:
                    CNY_TO_RUB = data['rates']['RUB'] / data['rates']['CNY']
                    save_cached_rate(CNY_TO_RUB, currency="CNY")
                    logger.info(f"Успешно обновлён курс CNY/RUB: {CNY_TO_RUB}")
                else:
                    logger.error("Нет курса CNY в данных API")
            else:
                logger.error("Ошибка в данных API")
        else:
            logger.error(f"Ошибка API: статус {response.status_code}")
    except Exception as e:
        logger.error(f"Ошибка при запросе к API: {e}")
        USD_TO_RUB = 85.0
        CNY_TO_RUB = 12.0

def schedule_tasks():
    """Планирует ежедневное обновление курса и очистку данных."""
    schedule.every().day.at("09:00").do(update_exchange_rate)
    schedule.every().day.at("09:00").do(clean_old_usage_data)
    logger.info("Запланированы ежедневные задачи в 09:00: обновление курса и очистка данных")
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    load_cached_rate()
    scheduler_thread = threading.Thread(target=schedule_tasks, daemon=True)
    scheduler_thread.start()