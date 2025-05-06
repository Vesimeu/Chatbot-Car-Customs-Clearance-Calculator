import logging
from telegram import Update
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from bot.states import (
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
    get_age_keyboard,
    get_engine_type_keyboard,
    get_confirm_keyboard,
)
from calculate import CustomsCalculator, WrongParamException
from tabulate import tabulate

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        "Выберите возраст автомобиля:",
        reply_markup=get_age_keyboard()
    )
    return AGE

async def age_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    age = query.data

    if age == "back_to_age":
        await query.message.edit_text(
            "Выберите возраст автомобиля:",
            reply_markup=get_age_keyboard()
        )
        return AGE

    context.user_data["age"] = age
    await query.message.edit_text(
        "Выберите тип двигателя:",
        reply_markup=get_engine_type_keyboard()
    )
    return ENGINE_TYPE

async def engine_type_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    engine_type = query.data

    if engine_type == "back_to_age":
        await query.message.edit_text(
            "Выберите возраст автомобиля:",
            reply_markup=get_age_keyboard()
        )
        return AGE

    context.user_data["engine_type"] = engine_type
    await query.message.edit_text("Введите объём двигателя (см³):")
    return ENGINE_CAPACITY

async def engine_capacity_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    try:
        engine_capacity = float(text)
        if engine_capacity <= 0:
            raise ValueError("Объём двигателя должен быть больше 0")
        context.user_data["engine_capacity"] = engine_capacity
        await update.message.reply_text("Введите мощность двигателя (л.с.):")
        return ENGINE_POWER
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите корректное число для объёма двигателя (см³):")
        return ENGINE_CAPACITY

async def engine_power_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    try:
        engine_power = float(text)
        if engine_power <= 0:
            raise ValueError("Мощность двигателя должна быть больше 0")
        context.user_data["engine_power"] = engine_power
        await update.message.reply_text("Введите цену автомобиля (руб.):")
        return PRICE
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите корректное число для мощности двигателя (л.с.):")
        return ENGINE_POWER

async def price_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    try:
        price = float(text)
        if price < 10000:
            raise ValueError("Цена автомобиля должна быть не менее 10,000 руб.")
        context.user_data["price_rub"] = price
        await update.message.reply_text("Введите стоимость корейской работы (руб., 0 если нет):")
        return KOREAN_WORK
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите корректное число для цены автомобиля (руб.):")
        return PRICE

async def korean_work_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    try:
        korean_work = float(text)
        if korean_work < 0:
            raise ValueError("Стоимость не может быть отрицательной")
        context.user_data["korean_work_rub"] = korean_work
        await update.message.reply_text("Введите комиссию агента (руб., 0 если нет):")
        return AGENT_FEE
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите корректное число для корейской работы (руб.):")
        return KOREAN_WORK

async def agent_fee_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    try:
        agent_fee = float(text)
        if agent_fee < 0:
            raise ValueError("Комиссия не может быть отрицательной")
        context.user_data["agent_fee_rub"] = agent_fee
        await update.message.reply_text("Введите стоимость работ во Владивостоке (руб., 0 если нет):")
        return VLADIVOSTOK_WORK
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите корректное число для комиссии агента (руб.):")
        return AGENT_FEE

async def vladivostok_work_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    try:
        vladivostok_work = float(text)
        if vladivostok_work < 0:
            raise ValueError("Стоимость не может быть отрицательной")
        context.user_data["vladivostok_work_rub"] = vladivostok_work
        await update.message.reply_text("Введите стоимость доставки по России (руб., 0 если нет):")
        return DELIVERY
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите корректное число для работ во Владивостоке (руб.):")
        return VLADIVOSTOK_WORK

async def delivery_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    try:
        delivery = float(text)
        if delivery < 0:
            raise ValueError("Стоимость не может быть отрицательной")
        context.user_data["delivery_rub"] = delivery

        params = context.user_data
        summary = (
            f"Подтвердите параметры:\n"
            f"Возраст: {params['age']}\n"
            f"Тип двигателя: {params['engine_type']}\n"
            f"Объём двигателя: {params['engine_capacity']} см³\n"
            f"Мощность: {params['engine_power']} л.с.\n"
            f"Цена: {params['price_rub']} руб.\n"
            f"Корейская работа: {params['korean_work_rub']} руб.\n"
            f"Комиссия агента: {params['agent_fee_rub']} руб.\n"
            f"Работы во Владивостоке: {params['vladivostok_work_rub']} руб.\n"
            f"Доставка: {params['delivery_rub']} руб."
        )
        await update.message.reply_text(summary, reply_markup=get_confirm_keyboard())
        return CONFIRM
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите корректное число для доставки (руб.):")
        return DELIVERY

async def confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    action = query.data

    if action == "back_to_delivery":
        await query.message.edit_text("Введите стоимость доставки по России (руб., 0 если нет):")
        return DELIVERY

    if action == "confirm":
        calculator = CustomsCalculator()
        params = context.user_data
        try:
            calculator.set_vehicle_details(
                age=params["age"],
                engine_capacity=params["engine_capacity"],
                engine_power=params["engine_power"],
                engine_type=params["engine_type"],
                price_rub=params["price_rub"],
                korean_work_rub=params["korean_work_rub"],
                agent_fee_rub=params["agent_fee_rub"],
                vladivostok_work_rub=params["vladivostok_work_rub"],
                delivery_rub=params["delivery_rub"]
            )
            results = calculator.calculate()
            table = [[k, f"{v:,.2f} руб."] for k, v in results.items()]
            output = tabulate(table, headers=["Описание", "Сумма"], tablefmt="psql")
            await query.message.edit_text(f"Результаты расчёта:\n```\n{output}\n```", parse_mode="Markdown")
        except WrongParamException as e:
            await query.message.edit_text(f"Ошибка: {e}")
        context.user_data.clear()
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Расчёт отменён.")
    context.user_data.clear()
    return ConversationHandler.END

def get_conversation_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            AGE: [CallbackQueryHandler(age_handler)],
            ENGINE_TYPE: [CallbackQueryHandler(engine_type_handler)],
            ENGINE_CAPACITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, engine_capacity_handler)],
            ENGINE_POWER: [MessageHandler(filters.TEXT & ~filters.COMMAND, engine_power_handler)],
            PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, price_handler)],
            KOREAN_WORK: [MessageHandler(filters.TEXT & ~filters.COMMAND, korean_work_handler)],
            AGENT_FEE: [MessageHandler(filters.TEXT & ~filters.COMMAND, agent_fee_handler)],
            VLADIVOSTOK_WORK: [MessageHandler(filters.TEXT & ~filters.COMMAND, vladivostok_work_handler)],
            DELIVERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, delivery_handler)],
            CONFIRM: [CallbackQueryHandler(confirm_handler)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )