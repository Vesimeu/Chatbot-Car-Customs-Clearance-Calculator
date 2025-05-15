import sqlite3
import logging
from datetime import datetime, date
import schedule
import time
import threading

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Максимальное количество расчётов в день
MAX_ATTEMPTS = 3
# Путь к базе данных SQLite
DB_FILE = "usage_data.db"


def init_db():
    """Инициализирует базу данных и создаёт таблицу, если она не существует."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usage (
                    user_id INTEGER,
                    date TEXT,
                    attempts INTEGER,
                    PRIMARY KEY (user_id, date)
                )
            """)
            conn.commit()
            logger.info("База данных инициализирована")
    except sqlite3.Error as e:
        logger.error(f"Ошибка при инициализации базы данных: {e}")


def clean_old_usage_data():
    """Удаляет записи за предыдущие дни."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            today = str(date.today())
            cursor.execute("DELETE FROM usage WHERE date != ?", (today,))
            conn.commit()
            logger.info(f"Устаревшие данные за дни до {today} удалены")
    except sqlite3.Error as e:
        logger.error(f"Ошибка при очистке устаревших данных: {e}")


def check_and_update_usage(user_id: int):
    """
    Проверяет, может ли пользователь выполнить расчёт, и обновляет счётчик.
    Возвращает кортеж (можно_ли_выполнить, оставшиеся_попытки, дата_сброса).
    """
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            today = str(date.today())

            # Проверяем текущие попытки пользователя
            cursor.execute(
                "SELECT attempts FROM usage WHERE user_id = ? AND date = ?",
                (user_id, today)
            )
            result = cursor.fetchone()

            if result is None:
                # Если записи нет, создаём новую
                attempts = 0
                cursor.execute(
                    "INSERT INTO usage (user_id, date, attempts) VALUES (?, ?, ?)",
                    (user_id, today, attempts)
                )
            else:
                attempts = result[0]

            if attempts >= MAX_ATTEMPTS:
                return False, 0, today

            # Увеличиваем счётчик попыток
            attempts += 1
            cursor.execute(
                "UPDATE usage SET attempts = ? WHERE user_id = ? AND date = ?",
                (attempts, user_id, today)
            )
            conn.commit()

            remaining = MAX_ATTEMPTS - attempts
            return True, remaining, today

    except sqlite3.Error as e:
        logger.error(f"Ошибка при работе с базой данных: {e}")
        return False, 0, str(date.today())


def schedule_cleanup():
    """Планирует ежедневную очистку устаревших данных."""
    schedule.every().day.at("09:00").do(clean_old_usage_data)
    logger.info("Запланирована ежедневная очистка устаревших данных в 09:00")
    while True:
        schedule.run_pending()
        time.sleep(60)


# Инициализация базы данных при запуске
init_db()