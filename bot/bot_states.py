from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler

# Определение состояний
(
    AGE,
    ENGINE_TYPE,
    ENGINE_CAPACITY,
    ENGINE_POWER,
    PRICE,
    KOREAN_WORK,
    AGENT_FEE,
    VLADIVOSTOK_WORK,
    DELIVERY,
    CONFIRM,
) = range(10)

def get_age_keyboard():
    keyboard = [
        [InlineKeyboardButton("До 3 лет", callback_data="до 3")],
        [InlineKeyboardButton("3–5 лет", callback_data="3-5")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_engine_type_keyboard():
    keyboard = [
        [InlineKeyboardButton("Бензин", callback_data="gasoline")],
        [InlineKeyboardButton("Дизель", callback_data="diesel")],
        [InlineKeyboardButton("Электрический", callback_data="electric")],
        [InlineKeyboardButton("Гибрид", callback_data="hybrid")],
        [InlineKeyboardButton("Назад", callback_data="back_to_age")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_confirm_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("Подтвердить", callback_data="confirm"),
            InlineKeyboardButton("Назад", callback_data="back_to_delivery")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)