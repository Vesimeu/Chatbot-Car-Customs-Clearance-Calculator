from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_region_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(KeyboardButton("Китай (до Перми)"))
    keyboard.add(KeyboardButton("Корея (до Владивостока)"))
    return keyboard

def get_age_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(KeyboardButton("до 3"))
    keyboard.add(KeyboardButton("3-5"))
    return keyboard

def get_engine_type_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(KeyboardButton("gasoline"))
    keyboard.add(KeyboardButton("diesel"))
    keyboard.add(KeyboardButton("electric"))
    keyboard.add(KeyboardButton("hybrid"))
    return keyboard

def get_back_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Назад", callback_data="back"))
    return keyboard