from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_region_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Китай"))
    keyboard.add(KeyboardButton("Корея"))
    return keyboard

def get_age_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("до 3"))
    keyboard.add(KeyboardButton("3-5"))
    return keyboard

def get_engine_type_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Бензиновый"))
    keyboard.add(KeyboardButton("Дизельный"))
    keyboard.add(KeyboardButton("Гибридный"))
    keyboard.add(KeyboardButton("Электрический"))
    return keyboard